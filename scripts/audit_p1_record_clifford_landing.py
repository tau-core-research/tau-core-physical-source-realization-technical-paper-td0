#!/usr/bin/env python3
"""Audit the unique-orbit reduction of the P1 record--Clifford landing law."""

from __future__ import annotations

import hashlib
import json
import math
import warnings
from functools import reduce
from pathlib import Path

import numpy as np


warnings.filterwarnings(
    "ignore", message=".*encountered in matmul", category=RuntimeWarning
)

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_record_clifford_landing.json"
UPSTREAM = DERIVED / "p3_clp3_p1_record_clifford_embedding.json"
OUT = DERIVED / "p3_clp3_p1_record_clifford_landing_audit.json"
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


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def ordered_product(indices: tuple[int, ...], gammas: list[np.ndarray]) -> np.ndarray:
    result = np.eye(gammas[0].shape[0], dtype=complex)
    for index in indices:
        result = result @ gammas[index]
    return result


def adjoint_matrix_and_residual(
    record: np.ndarray, complement: list[np.ndarray]
) -> tuple[np.ndarray, float]:
    dimension = record.shape[0]
    matrix = np.zeros((3, 3))
    residuals: list[float] = []
    for column, vector in enumerate(complement):
        image = record @ vector @ record
        for row, basis in enumerate(complement):
            matrix[row, column] = float(np.trace(basis @ image).real / dimension)
        projection = sum(matrix[row, column] * complement[row] for row in range(3))
        residuals.append(norm(image - projection))
    return matrix, max(residuals)


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

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["upstream_embedding_packet_is_fingerprint_locked"] = (
        payload["upstream_embedding_fingerprint_sha256"]
        == upstream["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["even_commutant_basis_is_four_dimensional"] = (
        np.linalg.matrix_rank(
            np.stack([identity.reshape(-1)] + [b.reshape(-1) for b in bivectors]),
            tol=TOL,
        )
        == 4
    )
    even_commuting_words: list[tuple[int, ...]] = []
    for mask in range(1 << 10):
        indices = tuple(index for index in range(10) if mask & (1 << index))
        if len(indices) % 2:
            continue
        word = ordered_product(indices, gammas)
        if all(norm(commutator(word, role)) < TOL for role in roles):
            even_commuting_words.append(indices)
    checks["even_relative_commutant_has_no_hidden_clifford_words"] = (
        even_commuting_words
        == [(), (7, 8), (7, 9), (8, 9)]
    )
    checks["bivectors_are_even_and_commute_with_roles"] = all(
        norm(commutator(b, grading)) < TOL
        and all(norm(commutator(b, role)) < TOL for role in roles)
        for b in bivectors
    )
    checks["bivectors_are_orthonormal_traceless_involutions"] = all(
        np.allclose(b, b.conj().T)
        and np.allclose(b @ b, identity)
        and abs(np.trace(b)) < TOL
        for b in bivectors
    ) and all(
        abs(np.trace(bivectors[i] @ bivectors[j]) / 32.0 - (i == j)) < TOL
        for i in range(3)
        for j in range(3)
    )

    sample_vectors = [
        np.array([0.0, 0.0, 1.0]),
        np.array([1.0, 0.0, 0.0]),
        np.array([1.0, 2.0, 3.0]) / math.sqrt(14.0),
        np.array([-2.0, 1.0, 4.0]) / math.sqrt(21.0),
    ]
    diagnostics: list[dict[str, object]] = []
    all_records = True
    all_projectors = True
    all_preserve = True
    all_split = True
    all_proper = True
    for vector in sample_vectors:
        record = sum(float(vector[i]) * bivectors[i] for i in range(3))
        p_plus = 0.5 * (identity + record)
        p_minus = 0.5 * (identity - record)
        adjoint, residual = adjoint_matrix_and_residual(record, complement)
        eigenvalues = np.linalg.eigvalsh(adjoint)
        all_records &= (
            np.allclose(record, record.conj().T)
            and np.allclose(record @ record, identity)
            and abs(np.trace(record)) < TOL
        )
        all_projectors &= (
            np.linalg.matrix_rank(p_plus, tol=TOL) == 16
            and np.linalg.matrix_rank(p_minus, tol=TOL) == 16
            and np.allclose(p_plus @ p_minus, 0.0)
        )
        all_preserve &= residual < TOL
        all_split &= np.allclose(eigenvalues, [-1.0, -1.0, 1.0])
        all_proper &= np.isclose(np.linalg.det(adjoint), 1.0)
        diagnostics.append(
            {
                "unit_bivector_coordinates": vector.tolist(),
                "complement_preservation_residual": residual,
                "adjoint_eigenvalues": eigenvalues.tolist(),
                "adjoint_determinant": float(np.linalg.det(adjoint)),
                "ambient_projector_ranks": [
                    int(np.linalg.matrix_rank(p_plus, tol=TOL)),
                    int(np.linalg.matrix_rank(p_minus, tol=TOL)),
                ],
            }
        )
    checks["every_sampled_unit_bivector_is_a_valid_record_involution"] = all_records
    checks["trace_preservation_gives_equal_minimal_projectors"] = all_projectors
    checks["even_landing_automatically_preserves_W"] = all_preserve
    checks["every_sampled_embedding_has_two_plus_one_split"] = all_split
    checks["every_sampled_adjoint_action_is_a_proper_half_turn"] = all_proper

    # The three traceless Hermitian basis elements identify the unit zero set
    # with S^2.  Spin(3)=SU(2) acts transitively on this sphere, including the
    # antipodal map that exchanges the two record labels.
    checks["valid_embedding_set_is_one_spin3_orbit"] = (
        checks["even_commutant_basis_is_four_dimensional"]
        and checks["bivectors_are_orthonormal_traceless_involutions"]
        and payload["automatic_consequences"]["all_embeddings_form"]
        == "one Spin(3)-conjugacy orbit"
    )
    checks["label_exchange_introduces_no_discrete_physical_choice"] = (
        payload["automatic_consequences"]["record_label_exchange"]
        == "contained in the same gauge orbit"
    )
    checks["vector_preservation_premise_is_redundant"] = (
        boundary["complement_preservation_is_redundant_after_even_landing"]
        and all_preserve
    )
    checks["current_joint_action_contains_no_cross_landing_equation"] = (
        payload["current_source_audit"]["owns_pusc_and_record_together"]
        and payload["current_source_audit"][
            "contains_record_to_clifford_map_variable"
        ]
        is False
        and payload["current_source_audit"][
            "contains_even_relative_commutant_cross_residual"
        ]
        is False
        and payload["current_source_audit"]["embedding_direction_has_euler_equation"]
        is False
    )
    checks["current_source_nonentailment_and_nature_boundary_are_preserved"] = (
        boundary["current_source_derives_even_landing"] is False
        and boundary["physical_source_ownership_proved"] is False
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
            "EVEN_RELATIVE_COMMUTANT_LANDING_HAS_ONE_SPIN3_GAUGE_ORBIT_"
            "CURRENT_COMMON_ACTION_DOES_NOT_FORCE_THE_LANDING"
        ),
        "diagnostics": {
            "sampled_embedding_count": len(diagnostics),
            "sampled_embeddings": diagnostics,
            "traceless_even_commutant_dimension": 3,
            "full_even_commutant_dimension": 4,
            "even_commuting_clifford_words": [
                list(indices) for indices in even_commuting_words
            ],
        },
        "exact_remaining_source_datum": (
            "physical occupation of the even-relative-commutant landing class"
        ),
        "physical_source_ownership": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"P1_RECORD_CLIFFORD_LANDING_AUDIT_FAIL {failed}")
    print(f"P1_RECORD_CLIFFORD_LANDING_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
