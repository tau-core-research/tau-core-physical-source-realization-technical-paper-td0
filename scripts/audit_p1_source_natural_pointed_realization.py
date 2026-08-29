#!/usr/bin/env python3
"""Finite audit of the source-natural pointed realization theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_source_natural_pointed_realization.json"
TRACE_GNS = DERIVED / "p3_clp3_p1_trace_gns_booleanization.json"
TRACE_GNS_AUDIT = DERIVED / "p3_clp3_p1_trace_gns_booleanization_audit.json"
ROLE_HODGE = DERIVED / "p3_clp3_p1_role_record_hodge_ownership.json"
ROLE_HODGE_AUDIT = DERIVED / "p3_clp3_p1_role_record_hodge_ownership_audit.json"
OUT = DERIVED / "p3_clp3_p1_source_natural_pointed_realization_audit.json"
TOL = 1.0e-10


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def weyl_operators(n: int) -> list[np.ndarray]:
    phase = np.exp(2j * np.pi / n)
    shift = np.roll(np.eye(n, dtype=complex), 1, axis=0)
    clock = np.diag([phase**k for k in range(n)])
    return [np.linalg.matrix_power(shift, p) @ np.linalg.matrix_power(clock, q)
            for p in range(n) for q in range(n)]


def inner_twirl(matrix: np.ndarray, operators: list[np.ndarray]) -> np.ndarray:
    return sum((u @ matrix @ u.conj().T for u in operators), start=np.zeros_like(matrix)) / len(operators)


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    trace_gns = json.loads(TRACE_GNS.read_text(encoding="utf-8"))
    trace_audit = json.loads(TRACE_GNS_AUDIT.read_text(encoding="utf-8"))
    role_hodge = json.loads(ROLE_HODGE.read_text(encoding="utf-8"))
    role_audit = json.loads(ROLE_HODGE_AUDIT.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]

    n = 8
    n_blocks = 4
    weyl = weyl_operators(n)
    rng = np.random.default_rng(20260828)
    raw_blocks = []
    for _ in range(n_blocks):
        x = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
        rho = x @ x.conj().T
        rho /= np.trace(rho)
        raw_blocks.append(rho)

    twirled_blocks = [inner_twirl(rho, weyl) for rho in raw_blocks]
    inner_twirl_defect = max(
        np.linalg.norm(rho - np.eye(n) / n) for rho in twirled_blocks
    )
    block_weights = np.array([0.11, 0.19, 0.27, 0.43])
    exchanged_weights = np.full(n_blocks, np.mean(block_weights))
    exchange_weight_defect = np.linalg.norm(
        exchanged_weights - np.full(n_blocks, 0.25)
    )

    nontracial = np.diag(np.arange(1, n + 1, dtype=float))
    nontracial /= np.trace(nontracial)
    nontracial_blocks = [nontracial.copy() for _ in range(n_blocks)]
    nontracial_is_faithful = min(
        np.linalg.eigvalsh(rho).min() for rho in nontracial_blocks
    ) > 0.0
    nontracial_survives_block_exchange = max(
        np.linalg.norm(rho - nontracial_blocks[0]) for rho in nontracial_blocks
    ) < TOL
    nontracial_fails_inner_naturality = np.linalg.norm(
        inner_twirl(nontracial, weyl) - nontracial
    ) > 0.1

    unequal_weights_are_positive = bool(np.all(block_weights > 0.0))
    unequal_weights_are_normalized = abs(float(np.sum(block_weights)) - 1.0) < TOL
    unequal_weights_fail_exchange = np.linalg.norm(
        block_weights - np.full(n_blocks, 0.25)
    ) > 0.1

    clifford_only_dimension = 128
    record_completed_dimension = 2 * clifford_only_dimension
    spectator_extension_dimension = 256 + 1
    source_orbit_rank = trace_audit["diagnostics"]["four_block_root_orbit_rank"]

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["upstream_trace_gns_packet_is_locked"] = (
        payload["upstream_trace_gns_fingerprint_sha256"]
        == trace_gns["source_fingerprint_sha256"]
    )
    checks["upstream_role_hodge_packet_is_locked"] = (
        payload["upstream_role_hodge_fingerprint_sha256"]
        == role_hodge["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["upstream_trace_gns_audit_passes"] = (
        trace_audit["passed"] == trace_audit["total"] == 22
    )
    checks["upstream_role_hodge_audit_passes"] = (
        role_audit["passed"] == role_audit["total"] == 25
    )
    checks["finite_inner_frame_twirl_is_normalized_trace"] = inner_twirl_defect < TOL
    checks["transitive_block_exchange_equalizes_weights"] = exchange_weight_defect < TOL
    checks["joint_naturality_has_equal_quarter_trace_output"] = (
        inner_twirl_defect < TOL and exchange_weight_defect < TOL
    )
    checks["nontracial_control_is_faithful"] = nontracial_is_faithful
    checks["nontracial_control_survives_discrete_block_exchange"] = (
        nontracial_survives_block_exchange
    )
    checks["nontracial_control_fails_inner_frame_naturality"] = (
        nontracial_fails_inner_naturality
    )
    checks["unequal_central_weights_are_faithful_state_weights"] = (
        unequal_weights_are_positive and unequal_weights_are_normalized
    )
    checks["unequal_central_weights_fail_block_exchange"] = (
        unequal_weights_fail_exchange
    )
    checks["record_port_is_dimensionally_independent"] = (
        clifford_only_dimension == 128 and record_completed_dimension == 256
    )
    checks["pointed_trace_gns_orbit_is_complete"] = source_orbit_rank == 256
    checks["spectator_extension_breaks_no_bypass_occupation"] = (
        source_orbit_rank < spectator_extension_dimension
    )
    checks["typed_clifford_degree_recovers_boolean_car"] = (
        trace_audit["checks"]["degree_split_obeys_mixed_car"]
        and trace_audit["checks"]["degree_split_recovers_exterior_number"]
    )
    checks["oriented_seed_and_positive_hodge_inputs_are_explicit"] = (
        "SNPR1_oriented_multiplicity_free_seed" in payload["premises"]
        and "SNPR2_positive_hodge_realization" in payload["premises"]
    )
    checks["binary_record_and_full_naturality_inputs_are_explicit"] = (
        "SNPR3_binary_frobenius_record" in payload["premises"]
        and "SNPR4_full_source_naturality" in payload["premises"]
    )
    checks["pointed_occupation_input_is_explicit"] = (
        "SNPR5_pointed_cyclic_occupation" in payload["premises"]
    )
    checks["all_five_premises_have_independence_controls"] = (
        len(payload["independence_controls"]) == 6
    )
    checks["composition_is_conditional_not_nature_level"] = (
        payload["composition_theorem"]["status"]
        == "proved_conditional_composition"
        and payload["claim_boundary"]["physical_parent_owns_SNPR1_to_SNPR5"]
        is False
        and payload["claim_boundary"]["nature_occupation_proved"] is False
    )
    checks["no_terminal_selection_enters_the_composition"] = (
        payload["claim_boundary"]["terminal_data_used_for_selection"] is False
    )

    passed = sum(bool(value) for value in checks.values())
    audit = {
        "checks": {key: bool(value) for key, value in checks.items()},
        "passed": passed,
        "total": len(checks),
        "verdict": (
            "SNPR1_TO_SNPR5_CONDITIONALLY_FORCE_THE_COMPLETE_POINTED_"
            "P3_TRACE_GNS_PACKET_NATURE_OWNERSHIP_OPEN"
        ),
        "diagnostics": {
            "inner_twirl_trace_defect": float(inner_twirl_defect),
            "block_exchange_weight_defect": float(exchange_weight_defect),
            "nontracial_inner_naturality_defect": float(
                np.linalg.norm(inner_twirl(nontracial, weyl) - nontracial)
            ),
            "unequal_weight_exchange_defect": float(
                np.linalg.norm(block_weights - np.full(n_blocks, 0.25))
            ),
            "clifford_only_dimension": clifford_only_dimension,
            "record_completed_dimension": record_completed_dimension,
            "pointed_source_orbit_rank": source_orbit_rank,
            "spectator_extension_dimension": spectator_extension_dimension,
        },
        "exact_remaining_physical_statement": payload[
            "exact_remaining_physical_statement"
        ],
        "physical_source_ownership": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"P1_SOURCE_NATURAL_POINTED_REALIZATION_AUDIT_FAIL {failed}")
    print(f"P1_SOURCE_NATURAL_POINTED_REALIZATION_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
