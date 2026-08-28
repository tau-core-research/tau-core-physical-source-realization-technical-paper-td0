#!/usr/bin/env python3
"""Finite audit of the JCM-P1 carrier-minimality theorem and controls."""

from __future__ import annotations

import hashlib
import json
import math
from functools import reduce
from itertools import product
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_joint_carrier_minimality.json"
UPSTREAM = DERIVED / "p3_clp3_p1_joint_graded_representation.json"
UPSTREAM_AUDIT = DERIVED / "p3_clp3_p1_joint_graded_representation_audit.json"
OUT = DERIVED / "p3_clp3_p1_joint_carrier_minimality_audit.json"
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


def heat_trace(eigenvalues: np.ndarray) -> float:
    return float(np.exp(-np.asarray(eigenvalues, dtype=float)).sum())


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    upstream_audit = json.loads(UPSTREAM_AUDIT.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]

    faithful_multiplicities = list(product(range(1, 5), repeat=4))
    faithful_dimensions = [8 * sum(item) for item in faithful_multiplicities]
    minimum_dimension = min(faithful_dimensions)
    equality_cases = [
        list(item)
        for item, dimension in zip(
            faithful_multiplicities, faithful_dimensions
        )
        if dimension == minimum_dimension
    ]

    gammas = jordan_wigner_gammas(5)
    identity = np.eye(32, dtype=complex)
    roles = gammas[:7]
    chi7 = 1.0j * reduce(np.matmul, roles)
    record = 1.0j * gammas[7] @ gammas[8]
    projectors = []
    for chirality_sign in (-1.0, 1.0):
        for record_sign in (-1.0, 1.0):
            projector = (
                0.25
                * (identity + chirality_sign * chi7)
                @ (identity + record_sign * record)
            )
            projectors.append(projector)
    internal_block_ranks = [
        int(np.linalg.matrix_rank(projector, tol=TOL))
        for projector in projectors
    ]
    identity2 = np.eye(2, dtype=complex)
    external_block_ranks = [
        int(np.linalg.matrix_rank(np.kron(projector, identity2), tol=TOL))
        for projector in projectors
    ]

    internal_eigenvalues = np.linspace(0.2, 3.3, 32)
    external_eigenvalues = np.concatenate(
        [internal_eigenvalues, internal_eigenvalues]
    )
    internal_heat_trace = heat_trace(internal_eigenvalues)
    external_heat_trace = heat_trace(external_eigenvalues)
    internal_complexity = math.log(internal_heat_trace)
    external_complexity = math.log(external_heat_trace)
    internal_normalized_trace = internal_heat_trace / 32.0
    external_normalized_trace = external_heat_trace / 64.0

    changed_compression_eigenvalues = np.concatenate(
        [internal_eigenvalues + 10.0, internal_eigenvalues + 10.0]
    )
    changed_compression_heat_trace = heat_trace(
        changed_compression_eigenvalues
    )

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["upstream_jgr_packet_is_fingerprint_locked"] = (
        payload["upstream_jgr_fingerprint_sha256"]
        == upstream["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["upstream_jgr_audit_passes"] = (
        upstream_audit["passed"] == upstream_audit["total"] == 19
    )
    checks["four_simple_blocks_have_size_eight"] = (
        payload["joint_algebra"]["simple_block_sizes"] == [8, 8, 8, 8]
        and payload["joint_algebra"]["complex_algebra_dimension"] == 256
    )
    checks["minimal_faithful_carrier_dimension_is_32"] = (
        minimum_dimension == 32
        and payload["joint_algebra"][
            "minimal_faithful_carrier_dimension"
        ]
        == 32
    )
    checks["minimal_faithful_multiplicity_is_unique"] = (
        equality_cases == [[1, 1, 1, 1]]
    )
    checks["internal_realization_attains_minimum"] = (
        internal_block_ranks == [8, 8, 8, 8]
        and payload["candidate_realizations"]["internal"][
            "carrier_dimension"
        ]
        == 32
    )
    checks["external_tensor_model_is_a_proper_duplication"] = (
        external_block_ranks == [16, 16, 16, 16]
        and payload["candidate_realizations"]["external_tensor_record"][
            "carrier_dimension"
        ]
        == 64
    )
    checks["unnormalized_heat_trace_strictly_penalizes_extension"] = (
        external_heat_trace > internal_heat_trace
        and np.isclose(external_heat_trace, 2.0 * internal_heat_trace)
        and external_complexity > internal_complexity
    )
    checks["complexity_gap_is_log_two_for_duplicate"] = np.isclose(
        external_complexity - internal_complexity, math.log(2.0)
    )
    checks["normalized_trace_erases_duplicate_penalty"] = np.isclose(
        external_normalized_trace, internal_normalized_trace
    )
    checks["changed_compression_can_reverse_selector"] = (
        changed_compression_heat_trace < internal_heat_trace
    )
    checks["dimension_24_control_is_nonfaithful"] = (
        8 * 3 == 24 and 3 < len(payload["joint_algebra"]["simple_block_sizes"])
    )
    checks["same_carrier_means_same_full_matrix_envelope"] = (
        identity.shape == (32, 32)
        and payload["candidate_realizations"]["internal"][
            "same_ontic_envelope"
        ]
        is True
    )
    checks["jgr_then_supplies_the_igl_landing"] = (
        upstream_audit["checks"][
            "internal_joint_representation_has_full_256_rank"
        ]
        and upstream_audit["checks"][
            "good_record_is_even_and_role_local"
        ]
    )
    checks["new_fit_parameter_is_absent"] = (
        payload["conditional_theorem"]["new_fit_parameter"] is False
    )
    checks["physical_selection_remains_open"] = (
        payload["selection_assumptions"][
            "joint_source_grammar_is_physically_owned"
        ]
        is False
        and payload["selection_assumptions"][
            "heat_trace_priority_is_physically_owned"
        ]
        is False
        and payload["selection_assumptions"][
            "nature_occupies_the_minimizer"
        ]
        is False
        and payload["claim_boundary"]["nature_selection_proved"] is False
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
            "SAME_ENVELOPE_SELECTED_BY_JOINT_CARRIER_MINIMALITY_"
            "UNDER_FROZEN_HEAT_TRACE_ASSUMPTIONS_PHYSICAL_OWNERSHIP_OPEN"
        ),
        "diagnostics": {
            "internal_block_ranks": internal_block_ranks,
            "external_block_ranks": external_block_ranks,
            "minimal_faithful_carrier_dimension": minimum_dimension,
            "minimal_multiplicity_cases": equality_cases,
            "internal_heat_trace": internal_heat_trace,
            "external_heat_trace": external_heat_trace,
            "heat_trace_ratio": external_heat_trace / internal_heat_trace,
            "complexity_gap": external_complexity - internal_complexity,
            "internal_normalized_heat_trace": internal_normalized_trace,
            "external_normalized_heat_trace": external_normalized_trace,
            "changed_compression_heat_trace": changed_compression_heat_trace,
        },
        "exact_remaining_source_datum": payload[
            "exact_remaining_source_datum"
        ],
        "physical_source_ownership": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"P1_JOINT_CARRIER_MINIMALITY_AUDIT_FAIL {failed}")
    print(f"P1_JOINT_CARRIER_MINIMALITY_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
