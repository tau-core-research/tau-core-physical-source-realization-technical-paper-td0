#!/usr/bin/env python3
"""Finite audit of UTR-P1, SPS-P1 and HCI-P1 with negative controls."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_spectral_priority_origin.json"
UPSTREAM = DERIVED / "p3_clp3_p1_joint_carrier_minimality.json"
UPSTREAM_AUDIT = DERIVED / "p3_clp3_p1_joint_carrier_minimality_audit.json"
OUT = DERIVED / "p3_clp3_p1_spectral_priority_origin_audit.json"
TOL = 1.0e-11


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def heat_trace(matrix: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvalsh(np.asarray(matrix, dtype=complex))
    return float(np.exp(-eigenvalues.real).sum())


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    upstream_audit = json.loads(UPSTREAM_AUDIT.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]

    a = np.array([[1.4, 0.2j], [-0.2j, 0.7]], dtype=complex)
    b = np.array(
        [[0.9, 0.1, 0.0], [0.1, 1.8, -0.15j], [0.0, 0.15j, 1.2]],
        dtype=complex,
    )
    direct_sum = np.block(
        [
            [a, np.zeros((2, 3), dtype=complex)],
            [np.zeros((3, 2), dtype=complex), b],
        ]
    )
    ordinary_direct_sum = np.trace(direct_sum).real
    ordinary_separate_sum = np.trace(a).real + np.trace(b).real
    normalized_direct_sum = np.trace(direct_sum).real / 5.0
    normalized_separate_sum = np.trace(a).real / 2.0 + np.trace(b).real / 3.0
    nonlinear_direct_sum = ordinary_direct_sum**2
    nonlinear_separate_sum = (
        np.trace(a).real**2 + np.trace(b).real**2
    )

    theta = 0.37
    unitary2 = np.array(
        [
            [math.cos(theta), -math.sin(theta)],
            [math.sin(theta), math.cos(theta)],
        ],
        dtype=complex,
    )
    unitary_trace = np.trace(unitary2 @ a @ unitary2.conj().T).real

    k1 = np.diag([0.2, 0.8])
    k2 = np.diag([0.4, 1.1, 1.7])
    k_tensor = np.kron(k1, np.eye(3)) + np.kron(np.eye(2), k2)
    z1 = heat_trace(k1)
    z2 = heat_trace(k2)
    z_tensor = heat_trace(k_tensor)

    z0 = 4.75
    multiplicities = np.arange(1, 129, dtype=float)
    positive_objective = np.log(multiplicities * z0)
    zero_objective = np.zeros_like(multiplicities)
    negative_objective = -np.log(multiplicities * z0)

    k0 = np.diag([0.3, 0.9, 1.6])
    kh = np.diag([1.1, 2.2])
    k_ext = np.block(
        [
            [k0, np.zeros((3, 2))],
            [np.zeros((2, 3)), kh],
        ]
    )
    embedding = np.vstack([np.eye(3), np.zeros((2, 3))])
    intertwining_defect = np.linalg.norm(k_ext @ embedding - embedding @ k0)
    compression_defect = np.linalg.norm(
        embedding.T @ k_ext @ embedding - k0
    )

    shifted_k_ext = k_ext.copy()
    shifted_k_ext[:3, :3] = k0 + 10.0 * np.eye(3)
    shifted_intertwining_defect = np.linalg.norm(
        shifted_k_ext @ embedding - embedding @ k0
    )
    shifted_compression_defect = np.linalg.norm(
        embedding.T @ shifted_k_ext @ embedding - k0
    )
    shifted_extension_wins = heat_trace(shifted_k_ext) < heat_trace(k0)

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["upstream_jcm_packet_is_fingerprint_locked"] = (
        payload["upstream_jcm_fingerprint_sha256"]
        == upstream["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["upstream_jcm_audit_passes"] = (
        upstream_audit["passed"] == upstream_audit["total"] == 18
    )
    checks["ordinary_trace_is_direct_sum_additive"] = np.isclose(
        ordinary_direct_sum, ordinary_separate_sum, atol=TOL
    )
    checks["ordinary_trace_is_unitarily_invariant"] = np.isclose(
        unitary_trace, np.trace(a).real, atol=TOL
    )
    checks["primitive_trace_calibration_is_one"] = np.isclose(
        np.trace(np.ones((1, 1))), 1.0, atol=TOL
    )
    checks["normalized_trace_fails_direct_sum_additivity"] = not np.isclose(
        normalized_direct_sum, normalized_separate_sum, atol=TOL
    )
    checks["nonlinear_unitary_functional_lies_outside_trace_theorem"] = (
        not np.isclose(
            nonlinear_direct_sum, nonlinear_separate_sum, atol=TOL
        )
    )
    checks["heat_trace_factorizes_under_tensor_sum"] = np.isclose(
        z_tensor, z1 * z2, rtol=TOL, atol=TOL
    )
    checks["log_heat_trace_is_tensor_additive"] = np.isclose(
        math.log(z_tensor), math.log(z1) + math.log(z2), atol=TOL
    )
    checks["positive_sign_uniquely_prefers_one_copy"] = (
        int(np.argmin(positive_objective)) == 0
        and np.all(np.diff(positive_objective) > 0.0)
    )
    checks["zero_sign_destroys_equality_rigidity"] = np.allclose(
        zero_objective, zero_objective[0], atol=TOL
    )
    checks["negative_sign_rewards_unbounded_duplication"] = (
        int(np.argmin(negative_objective)) == len(negative_objective) - 1
        and np.all(np.diff(negative_objective) < 0.0)
        and negative_objective[-1] < negative_objective[0]
    )
    checks["hodge_intertwining_implies_same_compression"] = (
        intertwining_defect < TOL and compression_defect < TOL
    )
    checks["algebraic_extension_without_intertwining_changes_compression"] = (
        shifted_intertwining_defect > 1.0
        and shifted_compression_defect > 1.0
    )
    checks["changed_compression_can_reverse_heat_trace_selection"] = bool(
        shifted_extension_wins
    )
    checks["formula_choices_are_removed_conditionally"] = (
        payload["conditional_consequence"][
            "separate_choice_of_unnormalized_trace_needed"
        ]
        is False
        and payload["conditional_consequence"][
            "separate_choice_of_positive_log_sign_needed"
        ]
        is False
        and payload["conditional_consequence"][
            "separate_same_compression_axiom_needed_after_hodge_intertwining"
        ]
        is False
    )
    checks["physical_common_ownership_remains_open"] = (
        payload["claim_boundary"][
            "current_source_co_owns_joint_grammar_and_structural_packet"
        ]
        is False
        and payload["claim_boundary"][
            "hodge_intertwining_physically_owned_for_all_candidates"
        ]
        is False
        and payload["claim_boundary"][
            "spectral_sufficiency_and_well_posedness_physically_owned"
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
            "SPECTRAL_PRIORITY_FORM_AND_SIGN_STRUCTURALLY_UNIQUE_"
            "COMMON_PHYSICAL_OWNERSHIP_OPEN"
        ),
        "diagnostics": {
            "ordinary_direct_sum_trace": ordinary_direct_sum,
            "ordinary_separate_trace_sum": ordinary_separate_sum,
            "normalized_direct_sum_trace": normalized_direct_sum,
            "normalized_separate_trace_sum": normalized_separate_sum,
            "nonlinear_direct_sum_value": nonlinear_direct_sum,
            "nonlinear_separate_sum_value": nonlinear_separate_sum,
            "tensor_heat_trace_ratio": z_tensor / (z1 * z2),
            "positive_duplicate_gap_at_128": float(
                positive_objective[-1] - positive_objective[0]
            ),
            "negative_duplicate_drop_at_128": float(
                negative_objective[-1] - negative_objective[0]
            ),
            "hodge_intertwining_defect": intertwining_defect,
            "hodge_compression_defect": compression_defect,
            "shifted_intertwining_defect": shifted_intertwining_defect,
            "shifted_compression_defect": shifted_compression_defect,
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
        raise SystemExit(f"P1_SPECTRAL_PRIORITY_ORIGIN_AUDIT_FAIL {failed}")
    print(f"P1_SPECTRAL_PRIORITY_ORIGIN_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
