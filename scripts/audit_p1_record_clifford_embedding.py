#!/usr/bin/env python3
"""Audit the conditional P1 record--Clifford embedding reduction."""

from __future__ import annotations

import hashlib
import json
import math
import warnings
from functools import reduce
from pathlib import Path

import numpy as np


# NumPy/Accelerate on some macOS runners emits spurious floating-point
# warnings for finite complex ``matmul`` calls.  Every result below is checked
# explicitly for the required exact relations, so silence only that warning.
warnings.filterwarnings(
    "ignore", message=".*encountered in matmul", category=RuntimeWarning
)


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_record_clifford_embedding.json"
UPSTREAM = DERIVED / "p3_clp3_p1_envelope_connector_selector.json"
OUT = DERIVED / "p3_clp3_p1_record_clifford_embedding_audit.json"
TOL = 1.0e-10


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def kron_all(factors: list[np.ndarray]) -> np.ndarray:
    return reduce(np.kron, factors)


def jordan_wigner_gammas(qubits: int) -> list[np.ndarray]:
    identity = np.eye(2, dtype=complex)
    sigma_x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    sigma_y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
    sigma_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    generators: list[np.ndarray] = []
    for slot in range(qubits):
        prefix = [sigma_z] * slot
        suffix = [identity] * (qubits - slot - 1)
        generators.append(kron_all(prefix + [sigma_x] + suffix))
        generators.append(kron_all(prefix + [sigma_y] + suffix))
    return generators


def ordered_product(matrices: list[np.ndarray], dimension: int) -> np.ndarray:
    result = np.eye(dimension, dtype=complex)
    for matrix in matrices:
        result = result @ matrix
    return result


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def anticommutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right + right @ left


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def clifford_words(generators: list[np.ndarray]) -> list[np.ndarray]:
    words = [np.eye(generators[0].shape[0], dtype=complex)]
    for generator in generators:
        words += [word @ generator for word in words]
    return words


def central_projector_ranks(
    identity: np.ndarray, chirality: np.ndarray, record: np.ndarray
) -> list[int]:
    ranks: list[int] = []
    for sign_chi in (1, -1):
        for sign_record in (1, -1):
            projector = (
                0.25
                * (identity + sign_chi * chirality)
                @ (identity + sign_record * record)
            )
            ranks.append(int(np.linalg.matrix_rank(projector, tol=TOL)))
    return ranks


def adjoint_matrix_and_residual(
    record: np.ndarray, complement: list[np.ndarray]
) -> tuple[np.ndarray, float]:
    dimension = record.shape[0]
    matrix = np.zeros((len(complement), len(complement)))
    residuals: list[float] = []
    for column, vector in enumerate(complement):
        image = record @ vector @ record
        for row, basis in enumerate(complement):
            matrix[row, column] = float(
                np.trace(basis @ image).real / dimension
            )
        projection = sum(
            matrix[row, column] * complement[row]
            for row in range(len(complement))
        )
        residuals.append(norm(image - projection))
    return matrix, max(residuals)


def full_clifford_trace_test(generators: list[np.ndarray]) -> tuple[int, float, float]:
    words = clifford_words(generators)
    identity = np.eye(generators[0].shape[0], dtype=complex)
    trace_defect = max(abs(np.trace(word)) for word in words[1:])
    unitary_defect = max(norm(word.conj().T @ word - identity) for word in words)
    return len(words), float(trace_defect), float(unitary_defect)


def generated_algebra_dimension(generators: list[np.ndarray]) -> int:
    words = clifford_words(generators)
    columns = np.stack([word.reshape(-1) for word in words], axis=1)
    return int(np.linalg.matrix_rank(columns, tol=TOL))


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]
    boundary = payload["claim_boundary"]

    gammas = jordan_wigner_gammas(5)
    identity = np.eye(32, dtype=complex)
    roles = gammas[:7]
    complement = gammas[7:]
    chi = 1.0j * ordered_product(roles, 32)
    grading = 1.0j * ordered_product(gammas, 32)
    record_even = 1.0j * gammas[7] @ gammas[8]

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["upstream_connector_packet_is_fingerprint_locked"] = (
        payload["upstream_connector_fingerprint_sha256"]
        == upstream["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["ten_generator_clifford_relations_hold"] = all(
        np.allclose(gamma, gamma.conj().T)
        and np.allclose(gamma @ gamma, identity)
        for gamma in gammas
    ) and all(
        np.allclose(anticommutator(gammas[left], gammas[right]), 0.0)
        for left in range(10)
        for right in range(left + 1, 10)
    )
    checks["p3_space_has_dimension_seven_and_complement_three"] = (
        len(roles) == 7 and len(complement) == 3
    )
    checks["global_grading_is_self_adjoint_involution"] = (
        np.allclose(grading, grading.conj().T)
        and np.allclose(grading @ grading, identity)
    )
    checks["good_record_is_self_adjoint_traceless_involution"] = (
        np.allclose(record_even, record_even.conj().T)
        and np.allclose(record_even @ record_even, identity)
        and abs(np.trace(record_even)) < TOL
    )
    checks["good_record_commutes_with_p3_roles"] = all(
        np.allclose(commutator(record_even, role), 0.0) for role in roles
    )
    checks["good_record_is_globally_even"] = np.allclose(
        commutator(record_even, grading), 0.0
    )
    checks["good_record_and_p3_chirality_give_four_rank_eight_blocks"] = (
        central_projector_ranks(identity, chi, record_even) == [8, 8, 8, 8]
    )
    checks["good_local_p3_record_algebra_has_dimension_256"] = (
        generated_algebra_dimension(roles + [record_even]) == 256
    )

    adjoint_good, preservation_good = adjoint_matrix_and_residual(
        record_even, complement
    )
    eig_good = np.linalg.eigvalsh(adjoint_good)
    checks["good_record_preserves_vector_complement"] = preservation_good < TOL
    checks["adjoint_action_is_orthogonal_involution"] = (
        np.allclose(adjoint_good.T @ adjoint_good, np.eye(3))
        and np.allclose(adjoint_good @ adjoint_good, np.eye(3))
    )
    checks["adjoint_split_is_exactly_two_minus_one_plus"] = np.allclose(
        eig_good, [-1.0, -1.0, 1.0]
    )
    checks["adjoint_split_projectors_have_ranks_two_and_one"] = (
        np.linalg.matrix_rank(np.eye(3) - adjoint_good, tol=TOL) == 2
        and np.linalg.matrix_rank(np.eye(3) + adjoint_good, tol=TOL) == 1
    )
    checks["adjoint_orientation_is_proper"] = np.isclose(
        np.linalg.det(adjoint_good), 1.0
    )

    gauge_diagnostics: list[dict[str, object]] = []
    all_gauge_frames_valid = True
    all_gauge_frames_close_cl10 = True
    for theta in (0.0, 0.37, 1.10):
        u = math.cos(theta) * gammas[7] + math.sin(theta) * gammas[8]
        companion = -1.0j * u @ record_even
        v = gammas[9]
        frame = [u, companion, v]
        frame_valid = all(
            np.allclose(vector, vector.conj().T)
            and np.allclose(vector @ vector, identity)
            for vector in frame
        ) and all(
            np.allclose(anticommutator(frame[left], frame[right]), 0.0)
            for left in range(3)
            for right in range(left + 1, 3)
        )
        word_count, trace_defect, unitary_defect = full_clifford_trace_test(
            roles + frame
        )
        closes = (
            word_count == 1024
            and trace_defect < TOL
            and unitary_defect < TOL
        )
        all_gauge_frames_valid &= frame_valid
        all_gauge_frames_close_cl10 &= closes
        gauge_diagnostics.append(
            {
                "theta": theta,
                "frame_valid": bool(frame_valid),
                "word_count": word_count,
                "max_nonidentity_trace": trace_defect,
                "max_word_unitarity_defect": unitary_defect,
            }
        )
    checks["record_recovers_companion_for_multiple_gauge_frames"] = (
        all_gauge_frames_valid
    )
    checks["every_tested_gauge_frame_closes_full_cl10"] = (
        all_gauge_frames_close_cl10
    )
    checks["connector_content_is_gauge_invariant"] = (
        all(item["word_count"] == 1024 for item in gauge_diagnostics)
        and payload["derived_split"]["gauge_invariant_content"]
        == "the graded record embedding and its 2+1 adjoint splitting"
    )

    # Wrong-grading control: same P3/record reduct and equal blocks, but odd.
    record_odd = chi @ record_even
    adjoint_odd, preservation_odd = adjoint_matrix_and_residual(
        record_odd, complement
    )
    checks["odd_twist_preserves_local_p3_record_reduct"] = (
        np.allclose(record_odd, record_odd.conj().T)
        and np.allclose(record_odd @ record_odd, identity)
        and abs(np.trace(record_odd)) < TOL
        and all(np.allclose(commutator(record_odd, role), 0.0) for role in roles)
        and central_projector_ranks(identity, chi, record_odd) == [8, 8, 8, 8]
    )
    checks["odd_twist_local_algebra_dimension_remains_256"] = (
        generated_algebra_dimension(roles + [record_odd]) == 256
    )
    checks["odd_twist_fails_global_evenness"] = (
        norm(commutator(record_odd, grading)) > 1.0
        and np.allclose(anticommutator(record_odd, grading), 0.0)
    )
    checks["odd_twist_reverses_the_two_plus_one_split"] = (
        preservation_odd < TOL
        and np.allclose(np.linalg.eigvalsh(adjoint_odd), [-1.0, 1.0, 1.0])
    )

    # Misaligned-commutant control: different complement bivectors in the two
    # P3 chirality sectors.  It has the same local four-block reduct, but it is
    # neither globally even nor a vector-space-preserving Clifford record.
    p_chi_plus = 0.5 * (identity + chi)
    p_chi_minus = 0.5 * (identity - chi)
    record_alt = 1.0j * gammas[8] @ gammas[9]
    record_misaligned = p_chi_plus @ record_even + p_chi_minus @ record_alt
    adjoint_misaligned, preservation_misaligned = adjoint_matrix_and_residual(
        record_misaligned, complement
    )
    checks["misaligned_control_preserves_local_p3_record_reduct"] = (
        np.allclose(record_misaligned, record_misaligned.conj().T)
        and np.allclose(record_misaligned @ record_misaligned, identity)
        and abs(np.trace(record_misaligned)) < TOL
        and all(
            np.allclose(commutator(record_misaligned, role), 0.0)
            for role in roles
        )
        and central_projector_ranks(identity, chi, record_misaligned)
        == [8, 8, 8, 8]
    )
    checks["misaligned_local_algebra_dimension_remains_256"] = (
        generated_algebra_dimension(roles + [record_misaligned]) == 256
    )
    checks["misaligned_control_fails_global_evenness"] = (
        norm(commutator(record_misaligned, grading)) > 1.0
        and norm(anticommutator(record_misaligned, grading)) > 1.0
    )
    checks["misaligned_control_does_not_preserve_vector_complement"] = (
        preservation_misaligned > 1.0
    )
    checks["local_reduct_does_not_entail_graded_embedding"] = (
        checks["odd_twist_preserves_local_p3_record_reduct"]
        and checks["misaligned_control_preserves_local_p3_record_reduct"]
        and checks["odd_twist_fails_global_evenness"]
        and checks["misaligned_control_does_not_preserve_vector_complement"]
    )
    checks["current_source_selection_remains_open"] = (
        payload["single_embedding_contract"]["source_selected"] is False
        and payload["non_entailment_controls"][
            "current_common_source_selects_embedding"
        ]
        is False
    )
    checks["nature_and_physical_export_remain_closed"] = (
        boundary["nature_occupation_proved"] is False
        and boundary["physical_p1_exhaustivity_proved"] is False
        and boundary["physical_base_seed_packet_export_authorized"] is False
    )
    checks["primitive_count_is_reduced_not_nature_closed"] = (
        boundary["individual_u_v_source_primitives_required"] is False
        and boundary["graded_embedding_is_derived_from_current_source"] is False
    )

    passed = sum(bool(value) for value in checks.values())
    audit = {
        "checks": {key: bool(value) for key, value in checks.items()},
        "passed": passed,
        "total": len(checks),
        "verdict": (
            "CONNECTOR_PAIR_REDUCED_TO_ONE_GRADED_RECORD_CLIFFORD_EMBEDDING_"
            "CURRENT_SOURCE_SELECTION_OPEN"
        ),
        "diagnostics": {
            "good_adjoint_matrix": adjoint_good.tolist(),
            "good_adjoint_eigenvalues": eig_good.tolist(),
            "good_complement_preservation_residual": preservation_good,
            "gauge_frames": gauge_diagnostics,
            "odd_adjoint_matrix": adjoint_odd.tolist(),
            "odd_complement_preservation_residual": preservation_odd,
            "misaligned_adjoint_matrix": adjoint_misaligned.tolist(),
            "misaligned_complement_preservation_residual": preservation_misaligned,
        },
        "physical_record_clifford_embedding_ownership": "OPEN",
        "nature_level_occupation": False,
        "physical_P1_exhaustivity_proved": False,
        "physical_base_seed_packet_export_authorized": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"P1_RECORD_CLIFFORD_EMBEDDING_AUDIT_FAIL {failed}")
    print(f"P1_RECORD_CLIFFORD_EMBEDDING_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
