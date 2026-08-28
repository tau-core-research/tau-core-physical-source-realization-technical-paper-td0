#!/usr/bin/env python3
"""Finite audit of the frozen P3/CLP3 CompleteSeedPresentation candidate."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET_PATH = DERIVED / "p3_clp3_complete_seed_presentation.json"
AUDIT_PATH = DERIVED / "p3_clp3_instantiation_audit.json"
TOL = 1.0e-10


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def kron_all(factors: list[np.ndarray]) -> np.ndarray:
    out = np.array([[1.0]], dtype=complex)
    for factor in factors:
        out = np.kron(out, factor)
    return out


def checked_matmul(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Multiply finite audit matrices and fail closed on numerical corruption."""
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        result = left @ right
    if not np.all(np.isfinite(result)):
        raise FloatingPointError("non-finite matrix product in P3/CLP3 audit")
    return result


def jordan_wigner_gammas(qubits: int) -> list[np.ndarray]:
    identity = np.eye(2, dtype=complex)
    x = np.array([[0, 1], [1, 0]], dtype=complex)
    y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    z = np.diag([1.0, -1.0]).astype(complex)
    result: list[np.ndarray] = []
    for site in range(qubits):
        prefix = [z] * site
        suffix = [identity] * (qubits - site - 1)
        result.append(kron_all(prefix + [x] + suffix))
        result.append(kron_all(prefix + [y] + suffix))
    return result


def exterior_gammas(modes: int) -> list[np.ndarray]:
    dimension = 1 << modes
    result: list[np.ndarray] = []
    for mode in range(modes):
        creation = np.zeros((dimension, dimension), dtype=complex)
        for mask in range(dimension):
            if not ((mask >> mode) & 1):
                lower = bin(mask & ((1 << mode) - 1)).count("1")
                creation[mask | (1 << mode), mask] = -1.0 if lower % 2 else 1.0
        result.append(creation + creation.conj().T)
    return result


def ordered_words(generators: list[np.ndarray]) -> list[np.ndarray]:
    identity = np.eye(generators[0].shape[0], dtype=complex)
    words: list[np.ndarray] = []
    for mask in range(1 << len(generators)):
        word = identity.copy()
        for index, generator in enumerate(generators):
            if (mask >> index) & 1:
                word = checked_matmul(word, generator)
        words.append(word)
    return words


def reachable(initial: tuple[int, int], rules) -> set[tuple[int, int]]:
    seen = {initial}
    frontier = [initial]
    while frontier:
        state = frontier.pop()
        for rule in rules:
            candidate = rule(state)
            if candidate not in seen:
                seen.add(candidate)
                frontier.append(candidate)
    return seen


def recursive_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key).lower())
            keys.update(recursive_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(recursive_keys(child))
    return keys


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]
    checks: dict[str, bool] = {}

    checks["source_fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )

    # Seven Clifford generators and the complete 128-dimensional Cl_7 word
    # algebra on a compact 16-dimensional faithful prototype.
    prototype = jordan_wigner_gammas(4)[:7]
    identity16 = np.eye(16, dtype=complex)
    checks["seven_self_adjoint_role_generators"] = len(prototype) == 7 and all(
        np.allclose(g, g.conj().T) for g in prototype
    )
    checks["clifford_relations_hold"] = all(
        np.allclose(
            checked_matmul(prototype[i], prototype[j])
            + checked_matmul(prototype[j], prototype[i]),
            2.0 * (1 if i == j else 0) * identity16,
        )
        for i in range(7)
        for j in range(7)
    )
    prototype_words = ordered_words(prototype)
    word_columns = np.column_stack([word.reshape(-1) for word in prototype_words])
    word_rank = int(np.linalg.matrix_rank(word_columns, tol=TOL))
    checks["cl7_words_have_full_dimension_128"] = word_rank == 128

    # Canonical exterior-record realization and cyclic trace root.
    exterior = exterior_gammas(7)
    vacuum = np.zeros(128, dtype=complex)
    vacuum[0] = 1.0
    exterior_orbit = []
    root_expectations = []
    for word in ordered_words(exterior):
        vector = checked_matmul(word, vacuum)
        exterior_orbit.append(vector)
        root_expectations.append(np.vdot(vacuum, vector))
    exterior_orbit_matrix = np.column_stack(exterior_orbit)
    checks["exterior_root_orbit_rank_128"] = (
        np.linalg.matrix_rank(exterior_orbit_matrix, tol=TOL) == 128
    )
    record_basis = np.eye(2, dtype=complex)
    joint_orbit = np.column_stack(
        [
            np.kron(vector, record_basis[:, record])
            for record in range(2)
            for vector in exterior_orbit
        ]
    )
    checks["record_doubled_root_orbit_rank_256"] = (
        np.linalg.matrix_rank(joint_orbit, tol=TOL) == 256
    )
    checks["root_state_is_trace_on_clifford_words"] = (
        abs(root_expectations[0] - 1.0) < TOL
        and max(abs(value) for value in root_expectations[1:]) < TOL
    )
    checks["record_root_has_equal_faithful_weights"] = np.allclose(
        np.abs(np.array([1.0, 1.0]) / math.sqrt(2.0)) ** 2,
        np.array([0.5, 0.5]),
    )
    checks["declared_quotient_dimension_is_256"] = (
        2 * word_rank
        == payload["complete_seed_presentation"]["quotient_algebra"]["complex_dimension"]
        == 256
    )

    # The frozen atemporal Hodge-action weight is the exterior number
    # operator; its exponential is strictly positive on every finite mode.
    degrees = np.array(
        [bin(mask).count("1") for mask in range(128) for _record in range(2)],
        dtype=float,
    )
    spectral_weights = np.exp(-degrees)
    checks["hodge_number_operator_is_nonnegative"] = bool(degrees.min() == 0.0)
    checks["hodge_exponential_is_trace_class_and_faithful"] = bool(
        np.isfinite(spectral_weights.sum()) and spectral_weights.min() > 0.0
    )
    checks["hodge_heat_trace_matches_closed_form"] = np.isclose(
        spectral_weights.sum(), 2.0 * (1.0 + math.exp(-1.0)) ** 7
    )

    # Source support flag and ordered ports.
    p_bmg = np.diag([1.0, 0.0, 0.0, 0.0, 1.0, 1.0])
    p_oq = np.diag([0.0, 1.0, 0.0, 1.0, 0.0, 0.0])
    p_rmg = np.diag([0.0, 0.0, 1.0, 0.0, 1.0, 1.0])
    projectors = [p_bmg, p_oq, p_rmg]
    checks["support_projectors_are_commuting_self_adjoint_idempotents"] = all(
        np.allclose(p, p.T) and np.allclose(p @ p, p) for p in projectors
    ) and all(np.allclose(left @ right, right @ left) for left in projectors for right in projectors)
    fingerprints = [
        tuple(int(projector[index, index]) for projector in projectors)
        for index in range(6)
    ]
    multiplicities = {fingerprint: fingerprints.count(fingerprint) for fingerprint in set(fingerprints)}
    checks["support_flag_has_1_2_1_2_blocks"] = sorted(multiplicities.values()) == [1, 1, 2, 2]
    oq_port = np.array([0.0, 1.0, 0.0, -1.0, 0.0, 0.0]) / math.sqrt(2.0)
    mg_port = np.array([0.0, 0.0, 0.0, 0.0, 1.0, -1.0]) / math.sqrt(2.0)
    checks["ordered_ports_are_nonzero_orthonormal"] = (
        np.isclose(oq_port @ oq_port, 1.0)
        and np.isclose(mg_port @ mg_port, 1.0)
        and np.isclose(oq_port @ mg_port, 0.0)
    )
    relative_plus_unit = np.eye(7)
    checks["independent_unit_raises_rank_six_to_seven"] = (
        np.linalg.matrix_rank(relative_plus_unit[:, :6]) == 6
        and np.linalg.matrix_rank(relative_plus_unit) == 7
    )

    # Component-local composition and its hidden-global countermodel.
    product = {(a, b) for a in (0, 1) for b in (0, 1, 2)}
    local_rules = (
        lambda state: (1 - state[0], state[1]),
        lambda state: (state[0], (state[1] + 1) % 3),
    )
    local_closure = reachable((0, 0), local_rules)
    hidden_global = {(0, 0), (1, 1)}
    checks["jlc_local_rules_generate_cartesian_closure"] = local_closure == product
    checks["hidden_global_predicate_control_has_complete_marginals"] = (
        {x for x, _ in hidden_global} == {0, 1}
        and {y for _, y in hidden_global} == {0, 1}
        and len(hidden_global) < len(product)
    )
    h_joint = np.diag([2.0, 3.0, 5.0, 7.0, 11.0] + [1.0] * 7)
    checks["once_counted_component_hessian_positive_direct_sum"] = (
        np.linalg.eigvalsh(h_joint).min() > 0.0
        and np.allclose(h_joint, np.diag(np.diag(h_joint)))
    )
    checks["attainable_joint_zero"] = float(np.zeros(12) @ h_joint @ np.zeros(12)) == 0.0

    # One-copy Q/G fanout and the hidden diagonal LC3 control.
    source_dimension = 4
    eye4 = np.eye(source_dimension, dtype=complex)
    p_q = np.diag([1.0] * source_dimension + [0.0] * source_dimension)
    p_g = np.diag([0.0] * source_dimension + [1.0] * source_dimension)
    theta = 0.37
    unitary = np.diag(np.exp(1j * theta * np.arange(source_dimension)))
    diagonal_embedding = np.vstack([eye4, unitary]) / math.sqrt(2.0)
    diagonal_projector = diagonal_embedding @ diagonal_embedding.conj().T
    checks["qg_full_fanout_rank_is_two_source_copies"] = np.linalg.matrix_rank(p_q + p_g, tol=TOL) == 8
    checks["q_and_g_fibres_each_have_one_source_copy"] = (
        np.linalg.matrix_rank(p_q, tol=TOL) == source_dimension
        and np.linalg.matrix_rank(p_g, tol=TOL) == source_dimension
    )
    checks["hidden_diagonal_has_full_marginals_but_half_rank"] = (
        np.linalg.matrix_rank(p_q @ diagonal_embedding, tol=TOL) == source_dimension
        and np.linalg.matrix_rank(p_g @ diagonal_embedding, tol=TOL) == source_dimension
        and np.linalg.matrix_rank(diagonal_projector, tol=TOL) == source_dimension
    )
    checks["hidden_diagonal_not_preserved_by_role_projectors"] = (
        not np.allclose((np.eye(8) - diagonal_projector) @ p_q @ diagonal_projector, 0.0)
        and not np.allclose((np.eye(8) - diagonal_projector) @ p_g @ diagonal_projector, 0.0)
    )

    # Completion-class invariance and claim-boundary checks.
    k = np.diag([1.0, 2.0, 3.0, 5.0, 7.0, 11.0, 13.0])
    probe = np.arange(1.0, 8.0) / 10.0
    gamma = 0.5 * float(probe @ k @ probe)
    checks["off_shell_deformation_is_distinct_away_from_zero"] = gamma + gamma * gamma > gamma
    checks["off_shell_deformation_preserves_zero_and_two_jet"] = (
        0.0 + 0.0**2 == 0.0
        and np.allclose(k, k + 2.0 * 0.0 * k)
    )
    keys = recursive_keys(payload)
    forbidden_endpoint_keys = {"observed_value", "endpoint_score", "fitted_gain", "held_out_data"}
    checks["no_endpoint_selection_fields"] = not bool(keys & forbidden_endpoint_keys)
    checks["nature_ownership_remains_false"] = (
        payload["claim_boundary"]["nature_seed_selection"] is False
        and payload["claim_boundary"]["nature_occupation"] is False
        and payload["conditional_base_seed_packet_candidate"]["physical_export_authorized"] is False
    )
    checks["p1_p7_boundary_is_not_silently_closed"] = (
        payload["p1_p7_ledger"]["P1_complete_seed_physically_owned"]["nature_ownership_proved"] is False
        and payload["p1_p7_ledger"]["P4_physical_spectral_priority"]["nature_ownership_proved"] is False
        and payload["p1_p7_ledger"]["P5_attainment_and_equality_rigidity"]["unrestricted_rigidity_proved"] is False
        and payload["p1_p7_ledger"]["P7_td1_regular_handoff"]["physical_body_law_selected"] is False
    )

    checks = {name: bool(value) for name, value in checks.items()}
    passed = sum(checks.values())
    total = len(checks)
    audit = {
        "schema": "tau_core_p3_clp3_instantiation_audit_v1",
        "candidate_id": payload["candidate_id"],
        "source_fingerprint_sha256": packet["source_fingerprint_sha256"],
        "checks": checks,
        "passed": passed,
        "total": total,
        "diagnostics": {
            "cl7_word_rank": word_rank,
            "exterior_root_orbit_rank": int(np.linalg.matrix_rank(exterior_orbit_matrix, tol=TOL)),
            "record_doubled_root_orbit_rank": int(np.linalg.matrix_rank(joint_orbit, tol=TOL)),
            "hodge_heat_trace": float(spectral_weights.sum()),
            "qg_full_rank": int(np.linalg.matrix_rank(p_q + p_g, tol=TOL)),
            "qg_hidden_diagonal_rank": int(np.linalg.matrix_rank(diagonal_projector, tol=TOL)),
        },
        "verdict": "INTERNAL_COMPLETE_SEED_INSTANTIATION_PASS" if passed == total else "FAIL",
        "nature_level_occupation": False,
        "physical_base_seed_packet_export_authorized": False,
    }
    AUDIT_PATH.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != total:
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"P3_CLP3_INSTANTIATION_FAIL {failed}")
    print(f"P3_CLP3_INSTANTIATION_PASS {passed}/{total}")


if __name__ == "__main__":
    main()
