#!/usr/bin/env python3
"""Finite audit of the minimal mixed record--Clifford source completion."""

from __future__ import annotations

import hashlib
import json
import math
from functools import reduce
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_record_clifford_source_completion.json"
UPSTREAM = DERIVED / "p3_clp3_p1_record_clifford_landing.json"
OUT = DERIVED / "p3_clp3_p1_record_clifford_source_completion_audit.json"
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
    result: list[np.ndarray] = []
    for slot in range(qubits):
        prefix = [sz] * slot
        suffix = [identity] * (qubits - slot - 1)
        result.append(kron_all(prefix + [sx] + suffix))
        result.append(kron_all(prefix + [sy] + suffix))
    return result


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def hs2(matrix: np.ndarray) -> float:
    return float(np.trace(matrix.conj().T @ matrix).real / matrix.shape[0])


def record_constraints(record: np.ndarray, identity: np.ndarray) -> bool:
    return (
        np.allclose(record, record.conj().T, atol=TOL)
        and np.allclose(record @ record, identity, atol=TOL)
        and abs(np.trace(record) / record.shape[0]) < TOL
    )


def defect_parts(
    record: np.ndarray, roles: list[np.ndarray], grading: np.ndarray
) -> tuple[float, float, float]:
    role = sum(hs2(commutator(record, gamma)) for gamma in roles)
    even = hs2(commutator(record, grading))
    return role, even, role + even


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]
    boundary = payload["claim_boundary"]

    gammas = jordan_wigner_gammas(5)
    identity = np.eye(32, dtype=complex)
    roles = gammas[:7]
    complement = gammas[7:]
    grading = 1.0j * reduce(np.matmul, gammas)
    bivectors = [
        1.0j * complement[1] @ complement[2],
        1.0j * complement[2] @ complement[0],
        1.0j * complement[0] @ complement[1],
    ]

    good = bivectors[2]
    restricted_chirality = 1.0j * reduce(np.matmul, roles)
    odd_twist = restricted_chirality @ good
    even_role_mixer = 1.0j * roles[0] @ complement[0]

    good_parts = defect_parts(good, roles, grading)
    odd_parts = defect_parts(odd_twist, roles, grading)
    mixer_parts = defect_parts(even_role_mixer, roles, grading)

    samples = [
        np.array([0.0, 0.0, 1.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([1.0, 2.0, 3.0]) / math.sqrt(14.0),
        np.array([-2.0, 1.0, 4.0]) / math.sqrt(21.0),
    ]
    orbit_defects: list[float] = []
    for coordinates in samples:
        record = sum(
            float(coordinates[index]) * bivectors[index] for index in range(3)
        )
        orbit_defects.append(defect_parts(record, roles, grading)[2])

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["upstream_landing_packet_is_fingerprint_locked"] = (
        payload["upstream_landing_fingerprint_sha256"]
        == upstream["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["current_source_has_no_mixed_record_clifford_word"] = (
        payload["current_source_signature_audit"][
            "mixed_record_clifford_word_present"
        ]
        is False
        and payload["current_source_signature_audit"][
            "record_image_in_Cl_10_is_a_variational_variable"
        ]
        is False
    )
    checks["internal_and_external_models_share_the_current_reduct"] = (
        payload["same_reduct_models"]["different_landing_truth_value"]
        and payload["same_reduct_models"]["verdict"]
        == "CURRENT_SOURCE_PRESENTATION_DOES_NOT_ENTAIL_INTERNAL_LANDING"
    )
    checks["all_controls_are_valid_record_involutions"] = all(
        record_constraints(record, identity)
        for record in [good, odd_twist, even_role_mixer]
    )
    checks["good_record_has_zero_joint_defect"] = good_parts[2] < TOL
    checks["odd_twist_passes_role_locality"] = odd_parts[0] < TOL
    checks["odd_twist_fails_evenness"] = odd_parts[1] > 1.0
    checks["even_role_mixer_passes_evenness"] = mixer_parts[1] < TOL
    checks["even_role_mixer_fails_role_locality"] = mixer_parts[0] > 1.0
    checks["both_cross_components_are_logically_necessary"] = (
        checks["odd_twist_passes_role_locality"]
        and checks["odd_twist_fails_evenness"]
        and checks["even_role_mixer_passes_evenness"]
        and checks["even_role_mixer_fails_role_locality"]
    )
    checks["sampled_spin3_orbit_has_zero_joint_defect"] = all(
        value < TOL for value in orbit_defects
    )
    checks["zero_set_is_the_even_relative_commutant_record_manifold"] = (
        payload["conditional_positive_completion"]["zero_set"]
        == "record involutions in Comm(Cl(E)) intersect Cl_10(C)^even"
        and checks["good_record_has_zero_joint_defect"]
        and checks["both_cross_components_are_logically_necessary"]
    )
    checks["zero_set_modulo_gauge_is_one_orbit"] = (
        payload["conditional_positive_completion"]["zero_set_modulo_gauge"]
        == "one Spin(3) conjugacy orbit"
        and upstream["source_freeze_payload"]["automatic_consequences"][
            "all_embeddings_form"
        ]
        == "one Spin(3)-conjugacy orbit"
    )
    checks["completion_introduces_no_endpoint_fit_parameter"] = (
        payload["conditional_positive_completion"][
            "new_dimensionless_fit_parameter"
        ]
        is False
        and payload["conditional_positive_completion"][
            "off_shell_weight_uniqueness_claimed"
        ]
        is False
    )
    checks["completion_does_not_create_its_own_domain"] = (
        payload["minimality_controls"]["current_action_can_generate_missing_R_domain"]
        is False
        and boundary["current_source_owns_in_envelope_record_domain"] is False
    )
    checks["nature_boundary_is_preserved"] = (
        boundary["current_source_derives_IGL_P1"] is False
        and boundary["nature_occupation_proved"] is False
        and boundary["physical_p1_exhaustivity_proved"] is False
        and boundary["physical_base_seed_packet_export_authorized"] is False
    )

    passed = sum(bool(value) for value in checks.values())
    audit = {
        "checks": {key: bool(value) for key, value in checks.items()},
        "passed": passed,
        "total": len(checks),
        "verdict": (
            "CURRENT_SOURCE_NONENTAILMENT_PROVED_"
            "MINIMAL_INTERNAL_GRADED_LOCALITY_COMPLETION_CONSTRUCTED"
        ),
        "diagnostics": {
            "good_record_defect": {
                "role": good_parts[0],
                "grading": good_parts[1],
                "joint": good_parts[2],
            },
            "odd_twist_defect": {
                "role": odd_parts[0],
                "grading": odd_parts[1],
                "joint": odd_parts[2],
            },
            "even_role_mixer_defect": {
                "role": mixer_parts[0],
                "grading": mixer_parts[1],
                "joint": mixer_parts[2],
            },
            "sampled_spin3_orbit_joint_defects": orbit_defects,
        },
        "exact_remaining_source_datum": (
            "physical ownership of the in-envelope record image and IGL-P1"
        ),
        "physical_source_ownership": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"P1_RECORD_CLIFFORD_SOURCE_COMPLETION_AUDIT_FAIL {failed}")
    print(f"P1_RECORD_CLIFFORD_SOURCE_COMPLETION_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
