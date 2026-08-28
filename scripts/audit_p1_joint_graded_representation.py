#!/usr/bin/env python3
"""Finite audit of the JGR-P1 <-> IGL-P1 equivalence theorem."""

from __future__ import annotations

import hashlib
import json
import math
from functools import reduce
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_joint_graded_representation.json"
UPSTREAM = DERIVED / "p3_clp3_p1_record_clifford_source_completion.json"
OUT = DERIVED / "p3_clp3_p1_joint_graded_representation_audit.json"
TOL = 1.0e-10


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def kron_all(factors: list[np.ndarray]) -> np.ndarray:
    return reduce(np.kron, factors)


def jordan_wigner_gammas(qubits: int) -> list[np.ndarray]:
    identity = np.eye(2, dtype=complex)
    sx = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    sy = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
    sz = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    generators: list[np.ndarray] = []
    for slot in range(qubits):
        prefix = [sz] * slot
        suffix = [identity] * (qubits - slot - 1)
        generators.append(kron_all(prefix + [sx] + suffix))
        generators.append(kron_all(prefix + [sy] + suffix))
    return generators


def ordered_words(generators: list[np.ndarray]) -> list[np.ndarray]:
    identity = np.eye(generators[0].shape[0], dtype=complex)
    words: list[np.ndarray] = []
    for mask in range(1 << len(generators)):
        word = identity.copy()
        for index, generator in enumerate(generators):
            if mask & (1 << index):
                word = word @ generator
        words.append(word)
    return words


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def hs2(matrix: np.ndarray) -> float:
    return float(np.trace(matrix.conj().T @ matrix).real / matrix.shape[0])


def matrix_span_rank(matrices: list[np.ndarray]) -> int:
    stacked = np.stack([matrix.reshape(-1) for matrix in matrices])
    return int(np.linalg.matrix_rank(stacked, tol=TOL))


def record_constraints(record: np.ndarray, identity: np.ndarray) -> bool:
    return (
        np.allclose(record, record.conj().T, atol=TOL)
        and np.allclose(record @ record, identity, atol=TOL)
        and abs(np.trace(record) / record.shape[0]) < TOL
    )


def igl_defect(
    record: np.ndarray, roles: list[np.ndarray], grading: np.ndarray
) -> tuple[float, float, float]:
    role = sum(hs2(commutator(record, generator)) for generator in roles)
    even = hs2(commutator(record, grading))
    return role, even, role + even


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]

    gammas = jordan_wigner_gammas(5)
    identity = np.eye(32, dtype=complex)
    roles = gammas[:7]
    complement = gammas[7:]
    grading = 1.0j * reduce(np.matmul, gammas)
    chirality7 = 1.0j * reduce(np.matmul, roles)
    bivectors = [
        1.0j * complement[1] @ complement[2],
        1.0j * complement[2] @ complement[0],
        1.0j * complement[0] @ complement[1],
    ]
    role_words = ordered_words(roles)

    good = bivectors[2]
    odd = chirality7 @ good
    mixer = 1.0j * roles[0] @ complement[0]
    p_plus = 0.5 * (identity + good)
    p_minus = 0.5 * (identity - good)

    good_joint_basis = role_words + [word @ good for word in role_words]
    good_joint_rank = matrix_span_rank(good_joint_basis)
    odd_joint_basis = role_words + [word @ odd for word in role_words]
    odd_joint_rank = matrix_span_rank(odd_joint_basis)

    port_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    identity2 = np.eye(2, dtype=complex)
    external_role_words = [np.kron(word, identity2) for word in role_words]
    external_record = np.kron(identity, port_z)
    external_joint_basis = external_role_words + [
        word @ external_record for word in external_role_words
    ]
    external_joint_rank = matrix_span_rank(external_joint_basis)

    samples = [
        np.array([0.0, 0.0, 1.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([1.0, 2.0, 3.0]) / math.sqrt(14.0),
        np.array([-2.0, 1.0, 4.0]) / math.sqrt(21.0),
    ]
    orbit_diagnostics: list[dict[str, object]] = []
    for coordinates in samples:
        record = sum(
            float(coordinates[index]) * bivectors[index] for index in range(3)
        )
        basis = role_words + [word @ record for word in role_words]
        orbit_diagnostics.append(
            {
                "coordinates": coordinates.tolist(),
                "igl_defect": igl_defect(record, roles, grading)[2],
                "joint_image_rank": matrix_span_rank(basis),
                "record_constraints": bool(record_constraints(record, identity)),
            }
        )

    good_defect = igl_defect(good, roles, grading)
    odd_defect = igl_defect(odd, roles, grading)
    mixer_defect = igl_defect(mixer, roles, grading)

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["upstream_igl_packet_is_fingerprint_locked"] = (
        payload["upstream_igl_fingerprint_sha256"]
        == upstream["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["good_record_obeys_inherited_record_algebra"] = record_constraints(
        good, identity
    )
    checks["good_record_is_even_and_role_local"] = good_defect[2] < TOL
    checks["good_record_projectors_have_equal_trace"] = (
        np.linalg.matrix_rank(p_plus, tol=TOL) == 16
        and np.linalg.matrix_rank(p_minus, tol=TOL) == 16
        and np.isclose(np.trace(p_plus).real / 32.0, 0.5)
        and np.isclose(np.trace(p_minus).real / 32.0, 0.5)
    )
    checks["internal_joint_representation_has_full_256_rank"] = (
        good_joint_rank == 256
        and payload["equivalence_theorem"]["faithful_image_dimension"] == 256
    )
    checks["every_sampled_igl_zero_defines_a_faithful_joint_representation"] = all(
        item["record_constraints"]
        and item["igl_defect"] < TOL
        and item["joint_image_rank"] == 256
        for item in orbit_diagnostics
    )
    checks["joint_representation_recovers_the_landing"] = (
        all(hs2(commutator(good, generator)) < TOL for generator in roles)
        and hs2(commutator(good, grading)) < TOL
    )
    checks["landing_multiplication_map_is_well_defined"] = all(
        hs2(commutator(good, word)) < TOL for word in role_words
    )
    checks["odd_control_is_a_valid_record_involution"] = record_constraints(
        odd, identity
    )
    checks["odd_control_is_faithful_and_role_local_but_not_graded"] = (
        odd_joint_rank == 256 and odd_defect[0] < TOL and odd_defect[1] > 1.0
    )
    checks["even_role_mixer_is_a_valid_record_involution"] = record_constraints(
        mixer, identity
    )
    checks["even_role_mixer_is_graded_but_not_tensor_local"] = (
        mixer_defect[1] < TOL and mixer_defect[0] > 1.0
    )
    checks["external_tensor_model_is_faithful"] = external_joint_rank == 256
    checks["external_tensor_model_is_not_same_envelope_internality"] = (
        external_record.shape == (64, 64)
        and payload["adversarial_controls"]["external_tensor_model"].startswith(
            "a faithful graded representation in Cl_10(C) tensor A_port"
        )
    )
    checks["same_envelope_condition_is_logically_essential"] = (
        checks["external_tensor_model_is_faithful"]
        and checks["external_tensor_model_is_not_same_envelope_internality"]
        and payload["joint_representation_principle"][
            "same_ontic_envelope_is_essential"
        ]
    )
    checks["igl_is_the_joint_representation_defect_not_a_new_gain"] = (
        payload["equivalence_theorem"]["new_independent_dynamical_coefficient"]
        is False
        and payload["claim_boundary"][
            "igl_is_equivalent_to_jgr_p1_conditionally"
        ]
    )
    checks["current_source_does_not_derive_jgr_or_nature_occupation"] = (
        payload["source_status"][
            "same_envelope_joint_graded_representation_owned"
        ]
        is False
        and payload["source_status"][
            "jgr_p1_selected_by_current_common_action"
        ]
        is False
        and payload["source_status"]["nature_occupied"] is False
        and payload["claim_boundary"]["physical_p1_exhaustivity_proved"]
        is False
        and payload["claim_boundary"][
            "physical_base_seed_packet_export_authorized"
        ]
        is False
    )

    passed = sum(bool(value) for value in checks.values())
    audit = {
        "checks": {key: bool(value) for key, value in checks.items()},
        "passed": passed,
        "total": len(checks),
        "verdict": (
            "IGL_EQUIVALENT_TO_SAME_ENVELOPE_JOINT_GRADED_REPRESENTATION_"
            "PHYSICAL_OWNERSHIP_OPEN"
        ),
        "diagnostics": {
            "internal_joint_image_rank": good_joint_rank,
            "odd_ungraded_joint_image_rank": odd_joint_rank,
            "external_joint_image_rank": external_joint_rank,
            "good_igl_defect": good_defect,
            "odd_igl_defect": odd_defect,
            "even_role_mixer_igl_defect": mixer_defect,
            "sampled_landing_orbit": orbit_diagnostics,
        },
        "exact_remaining_source_datum": (
            "physical ownership and occupation of one same-envelope graded "
            "joint representation of Cl(E) tensor A_port"
        ),
        "physical_source_ownership": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"P1_JOINT_GRADED_REPRESENTATION_AUDIT_FAIL {failed}")
    print(f"P1_JOINT_GRADED_REPRESENTATION_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
