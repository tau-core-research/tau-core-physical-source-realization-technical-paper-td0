#!/usr/bin/env python3
"""Audit the conditional two-connector P3-to-PUSC completion theorem."""

from __future__ import annotations

import hashlib
import json
from functools import reduce
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_envelope_connector_selector.json"
OUT = DERIVED / "p3_clp3_p1_envelope_connector_selector_audit.json"
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


def ordered_product(matrices: list[np.ndarray], identity: np.ndarray) -> np.ndarray:
    result = identity.copy()
    for matrix in matrices:
        result = result @ matrix
    return result


def clifford_words(generators: list[np.ndarray]) -> list[np.ndarray]:
    identity = np.eye(generators[0].shape[0], dtype=complex)
    words = [identity]
    for generator in generators:
        words += [word @ generator for word in words]
    return words


def hs_square(matrix: np.ndarray) -> float:
    dimension = matrix.shape[0]
    value = float(np.trace(matrix.conj().T @ matrix).real / dimension)
    return 0.0 if value < TOL**2 else value


def anticommutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right + right @ left


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def connector_defect(
    roles: list[np.ndarray], record: np.ndarray, u: np.ndarray, v: np.ndarray
) -> float:
    identity = np.eye(record.shape[0], dtype=complex)
    terms = [
        u - u.conj().T,
        u @ u - identity,
        anticommutator(u, record),
        v - v.conj().T,
        v @ v - identity,
        commutator(v, record),
        anticommutator(u, v),
    ]
    terms += [anticommutator(u, role) for role in roles]
    terms += [anticommutator(v, role) for role in roles]
    return sum(hs_square(term) for term in terms)


def block_graph(
    projectors: list[np.ndarray], connector: np.ndarray
) -> set[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for left in range(len(projectors)):
        for right in range(left + 1, len(projectors)):
            block = projectors[left] @ connector @ projectors[right]
            reverse = projectors[right] @ connector @ projectors[left]
            if hs_square(block) > TOL**2 or hs_square(reverse) > TOL**2:
                edges.add((left, right))
    return edges


def component_sizes(vertex_count: int, edges: set[tuple[int, int]]) -> list[int]:
    neighbors = {vertex: set() for vertex in range(vertex_count)}
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    remaining = set(range(vertex_count))
    sizes: list[int] = []
    while remaining:
        root = min(remaining)
        stack = [root]
        seen: set[int] = set()
        while stack:
            vertex = stack.pop()
            if vertex in seen:
                continue
            seen.add(vertex)
            stack.extend(neighbors[vertex] - seen)
        remaining -= seen
        sizes.append(len(seen))
    return sorted(sizes, reverse=True)


def algebra_dimension_from_components(sizes: list[int], block_rank: int) -> int:
    return block_rank**2 * sum(size**2 for size in sizes)


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]
    carrier = payload["declared_prebody_carrier"]
    ladder = payload["algebra_rank_ladder"]
    ontology = payload["ontology_decision"]
    boundary = payload["claim_boundary"]

    gammas = jordan_wigner_gammas(5)
    identity = np.eye(32, dtype=complex)
    roles = gammas[:7]
    u = gammas[7]
    gamma_9 = gammas[8]
    v = gammas[9]
    record = 1.0j * u @ gamma_9
    chirality = 1.0j * ordered_product(roles, identity)

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["ten_self_adjoint_clifford_generators"] = (
        len(gammas) == 10
        and all(np.allclose(gamma, gamma.conj().T) for gamma in gammas)
        and all(np.allclose(gamma @ gamma, identity) for gamma in gammas)
        and all(
            np.allclose(anticommutator(gammas[left], gammas[right]), 0.0)
            for left in range(10)
            for right in range(left + 1, 10)
        )
    )
    checks["record_and_chirality_are_commuting_involutions"] = (
        np.allclose(record, record.conj().T)
        and np.allclose(record @ record, identity)
        and np.allclose(chirality, chirality.conj().T)
        and np.allclose(chirality @ chirality, identity)
        and np.allclose(commutator(record, chirality), 0.0)
    )
    checks["p3_roles_commute_with_record"] = all(
        np.allclose(commutator(role, record), 0.0) for role in roles
    )
    checks["p3_chirality_is_central_on_role_algebra"] = all(
        np.allclose(commutator(role, chirality), 0.0) for role in roles
    )

    labels = [(sign_chi, sign_record) for sign_chi in (1, -1) for sign_record in (1, -1)]
    projectors = [
        0.25
        * (identity + sign_chi * chirality)
        @ (identity + sign_record * record)
        for sign_chi, sign_record in labels
    ]
    checks["four_central_projectors_are_rank_eight"] = (
        len(projectors) == 4
        and all(np.linalg.matrix_rank(projector, tol=TOL) == 8 for projector in projectors)
    )
    checks["central_projectors_are_orthogonal_and_complete"] = (
        np.allclose(sum(projectors), identity)
        and all(np.allclose(projector @ projector, projector) for projector in projectors)
        and all(
            np.allclose(projectors[left] @ projectors[right], 0.0)
            for left in range(4)
            for right in range(left + 1, 4)
        )
    )
    trace_weights = [float(np.trace(projector).real / 32.0) for projector in projectors]
    checks["normalized_trace_has_equal_quarter_block_weights"] = np.allclose(
        trace_weights, np.full(4, 0.25)
    )

    recovered_gamma_9 = -1.0j * u @ record
    checks["gamma_nine_is_recovered_from_u_and_record"] = np.allclose(
        recovered_gamma_9, gamma_9
    )
    checks["u_has_declared_record_and_role_grading"] = (
        np.allclose(anticommutator(u, record), 0.0)
        and all(np.allclose(anticommutator(u, role), 0.0) for role in roles)
    )
    checks["v_has_declared_record_and_role_grading"] = (
        np.allclose(commutator(v, record), 0.0)
        and all(np.allclose(anticommutator(v, role), 0.0) for role in roles)
        and np.allclose(anticommutator(u, v), 0.0)
    )

    u_edges = block_graph(projectors, u)
    v_edges = block_graph(projectors, v)
    no_sizes = component_sizes(4, set())
    u_sizes = component_sizes(4, u_edges)
    v_sizes = component_sizes(4, v_edges)
    uv_sizes = component_sizes(4, u_edges | v_edges)
    dimensions = {
        "p3_only": algebra_dimension_from_components(no_sizes, 8),
        "p3_plus_u": algebra_dimension_from_components(u_sizes, 8),
        "p3_plus_v": algebra_dimension_from_components(v_sizes, 8),
        "p3_plus_u_and_v": algebra_dimension_from_components(uv_sizes, 8),
    }
    checks["each_single_connector_leaves_two_components"] = (
        u_sizes == [2, 2] and v_sizes == [2, 2]
    )
    checks["two_connector_union_is_connected"] = uv_sizes == [4]
    checks["component_formula_matches_declared_rank_ladder"] = all(
        dimensions[key] == ladder[key] for key in dimensions
    )

    full_words = clifford_words(gammas)
    nonidentity_trace_max = max(abs(np.trace(word)) for word in full_words[1:])
    word_norm_defect_max = max(
        np.linalg.norm(word.conj().T @ word - identity) for word in full_words
    )
    checks["cl10_words_fill_m32_by_trace_orthogonality"] = (
        len(full_words) == 1024
        and nonidentity_trace_max < TOL
        and word_norm_defect_max < TOL
        and carrier["pusc_complex_algebra_dimension"] == 1024
    )

    good_defect = connector_defect(roles, record, u, v)
    zero_u_defect = connector_defect(roles, record, np.zeros_like(u), v)
    zero_v_defect = connector_defect(roles, record, u, np.zeros_like(v))
    scaled_u_defect = connector_defect(roles, record, 0.8 * u, v)
    wrong_v_defect = connector_defect(roles, record, u, u)
    checks["declared_connector_witness_has_zero_defect"] = good_defect == 0.0
    checks["zero_connector_controls_have_positive_defect"] = (
        zero_u_defect > 0.0 and zero_v_defect > 0.0
    )
    checks["scaled_and_wrong_grading_controls_have_positive_defect"] = (
        scaled_u_defect > 0.0 and wrong_v_defect > 0.0
    )
    checks["nonnegative_zero_witness_attains_global_defect_minimum"] = (
        min(good_defect, zero_u_defect, zero_v_defect, scaled_u_defect, wrong_v_defect)
        == 0.0
    )
    checks["connector_completion_restores_conditional_full_gns_rank"] = (
        dimensions["p3_plus_u_and_v"] / carrier["pusc_complex_algebra_dimension"]
        == 1.0
    )
    checks["p3_only_rank_ratio_remains_one_quarter"] = (
        dimensions["p3_only"] / carrier["pusc_complex_algebra_dimension"]
        == 0.25
    )
    checks["simple_m32_cannot_have_p3_as_a_nontrivial_star_quotient"] = (
        ontology["simple_m32_has_no_nontrivial_star_ideal_for_a_p3_null_quotient"]
        is True
        and carrier["p3_complex_algebra_dimension"]
        < carrier["pusc_complex_algebra_dimension"]
    )
    checks["nature_claim_and_packet_export_remain_closed"] = (
        boundary["conditional_ontic_completion_constructed"] is True
        and boundary["current_tau_source_owns_connector_grammar"] is False
        and boundary["nature_occupation_proved"] is False
        and boundary["physical_p1_exhaustivity_proved"] is False
        and boundary["physical_base_seed_packet_export_authorized"] is False
    )

    checks = {name: bool(value) for name, value in checks.items()}
    passed = sum(checks.values())
    total = len(checks)
    audit = {
        "schema": "tau_core_p1_envelope_connector_selector_audit_v1",
        "candidate_id": payload["candidate_id"],
        "source_fingerprint_sha256": packet["source_fingerprint_sha256"],
        "checks": checks,
        "passed": passed,
        "total": total,
        "diagnostics": {
            "central_block_ranks": [
                int(np.linalg.matrix_rank(projector, tol=TOL))
                for projector in projectors
            ],
            "central_trace_weights": trace_weights,
            "u_block_edges": sorted([list(edge) for edge in u_edges]),
            "v_block_edges": sorted([list(edge) for edge in v_edges]),
            "component_sizes": {
                "p3_only": no_sizes,
                "p3_plus_u": u_sizes,
                "p3_plus_v": v_sizes,
                "p3_plus_u_and_v": uv_sizes,
            },
            "algebra_dimensions": dimensions,
            "good_connector_defect": good_defect,
            "zero_u_defect": zero_u_defect,
            "zero_v_defect": zero_v_defect,
            "scaled_u_defect": scaled_u_defect,
            "wrong_v_defect": wrong_v_defect,
            "nonidentity_clifford_trace_max": float(nonidentity_trace_max),
            "clifford_word_norm_defect_max": float(word_norm_defect_max),
        },
        "verdict": (
            "TWO_CONNECTOR_ONTIC_PUSC_COMPLETION_PASS_NATURE_SELECTION_OPEN"
            if passed == total
            else "FAIL"
        ),
        "physical_connector_ownership": "OPEN",
        "nature_level_occupation": False,
        "physical_P1_exhaustivity_proved": False,
        "physical_base_seed_packet_export_authorized": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != total:
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"P1_ENVELOPE_CONNECTOR_SELECTOR_FAIL {failed}")
    print(
        f"P1_ENVELOPE_CONNECTOR_SELECTOR_PASS {passed}/{total} "
        "ONTIC_COMPLETION_CONDITIONAL"
    )


if __name__ == "__main__":
    main()
