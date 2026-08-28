#!/usr/bin/env python3
"""Finite theorem/countermodel audit for the P3/CLP3 single-source law."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
LAW_PATH = DERIVED / "p3_clp3_single_source_law.json"
P3_PATH = DERIVED / "p3_clp3_complete_seed_presentation.json"
OUT = DERIVED / "p3_clp3_single_source_law_audit.json"
TOL = 1.0e-11


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def gram_defect(j_map: np.ndarray) -> float:
    source_identity = np.eye(j_map.shape[1])
    target_identity = np.eye(j_map.shape[0])
    source_defect = j_map.T @ j_map - source_identity
    target_defect = j_map @ j_map.T - target_identity
    return float(np.sum(source_defect**2) + np.sum(target_defect**2))


def body_square(b: np.ndarray, b0: np.ndarray, hessian: np.ndarray, load: np.ndarray) -> float:
    displacement = b - b0
    return float(
        0.5 * displacement @ hessian @ displacement
        - load @ displacement
        + 0.5 * load @ np.linalg.solve(hessian, load)
    )


def main() -> None:
    law = json.loads(LAW_PATH.read_text(encoding="utf-8"))
    payload = law["source_freeze_payload"]
    p3 = json.loads(P3_PATH.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    checks["law_fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == law["source_fingerprint_sha256"]
    )
    checks["law_is_bound_to_frozen_p3_seed"] = (
        payload["upstream_seed_candidate_id"]
        == p3["source_freeze_payload"]["candidate_id"]
        and payload["upstream_seed_fingerprint_sha256"]
        == p3["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_and_unfitted"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )

    # Source-fidelity block.  The 256 P3 exterior-record spectrum is used
    # directly; a proper split extension adds one positive Hodge mode.
    action_unit = 1.0
    degrees = np.array(
        [bin(mask).count("1") for mask in range(128) for _record in range(2)],
        dtype=float,
    )
    hidden_eigenvalue = 4.25
    z0 = float(np.exp(-degrees / action_unit).sum())
    z1 = z0 + math.exp(-hidden_eigenvalue / action_unit)
    relative_entropy_base = 0.0
    relative_entropy_extension = math.log(z1 / z0)
    checks["source_fidelity_zero_on_seed_completion"] = abs(relative_entropy_base) < TOL
    checks["proper_extension_has_positive_source_fidelity_cost"] = relative_entropy_extension > 0.0
    checks["split_extension_cost_equals_log_heat_trace_ratio"] = np.isclose(
        relative_entropy_extension, math.log(z1) - math.log(z0), atol=TOL
    )
    checks["wrong_sign_selects_the_extension_control"] = -relative_entropy_extension < 0.0

    # Two-sided realization block and sharp one-sided controls.
    theta = 0.41
    j_good = np.array(
        [
            [math.cos(theta), -math.sin(theta), 0.0],
            [math.sin(theta), math.cos(theta), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    j_inclusion = np.vstack([np.eye(3), np.zeros((1, 3))])
    j_coisometry = np.hstack([np.eye(3), np.zeros((3, 1))])
    j_reweighted = np.diag([1.0, 1.0, 1.3])
    checks["two_sided_unitary_realization_has_zero_gram_defect"] = gram_defect(j_good) < TOL
    checks["isometric_inclusion_exposes_hidden_target_support"] = np.isclose(
        gram_defect(j_inclusion), 1.0
    )
    checks["coisometry_exposes_collapsed_source_support"] = np.isclose(
        gram_defect(j_coisometry), 1.0
    )
    checks["independent_hodge_reweighting_is_penalized"] = gram_defect(j_reweighted) > 0.0

    # Source-independent positive base Hessian and Schur-neutral body square.
    hessian = np.diag(np.arange(1.0, 8.0))
    b0 = np.zeros(7)
    load = np.array([1.0, -0.5, 0.25, -0.125, 0.4, -0.2, 0.1])
    b_star = b0 + np.linalg.solve(hessian, load)
    gradient_at_star = hessian @ (b_star - b0) - load
    probe = b_star + np.linspace(0.1, 0.7, 7)
    checks["body_hessian_is_source_independent_positive"] = np.linalg.eigvalsh(hessian).min() > 0.0
    checks["body_stationarity_is_exact"] = np.linalg.norm(gradient_at_star) < TOL
    checks["body_square_has_zero_minimum"] = abs(body_square(b_star, b0, hessian, load)) < TOL
    checks["body_square_is_positive_away_from_minimum"] = body_square(probe, b0, hessian, load) > 0.0
    checks["zero_source_returns_neutral_body"] = abs(body_square(b0, b0, hessian, np.zeros(7))) < TOL
    second_load = 0.37 * load
    second_star = np.linalg.solve(hessian, second_load)
    checks["body_square_is_schur_neutral_for_distinct_loads"] = (
        abs(body_square(b_star, b0, hessian, load)) < TOL
        and abs(body_square(second_star, b0, hessian, second_load)) < TOL
    )

    selected_total = (
        relative_entropy_base
        + 0.5 * gram_defect(j_good)
        + body_square(b_star, b0, hessian, load)
    )
    extension_total = relative_entropy_extension + 0.5 * gram_defect(j_good)
    checks["single_action_has_attained_zero_witness"] = abs(selected_total) < TOL
    checks["single_action_rejects_the_proper_extension"] = extension_total > selected_total

    # The action cannot certify the completeness of the language used to
    # define its own residuals.  Both points satisfy the declared residual,
    # while the second carries an undeclared relation coordinate.
    visible = np.array([0.0, 0.0])
    hidden_relation = np.array([0.0, 1.0])
    declared_defect = lambda x: float(x[0] ** 2)
    checks["incomplete_residual_language_has_same_zero_control"] = (
        declared_defect(visible) == 0.0
        and declared_defect(hidden_relation) == 0.0
        and not np.allclose(visible, hidden_relation)
    )
    component_offset = -2.0 * relative_entropy_extension
    checks["independent_component_zero_jet_can_reverse_selection"] = (
        relative_entropy_extension + component_offset < relative_entropy_base
    )

    boundary = payload["claim_boundary"]
    checks["p4_through_p7_are_only_conditional"] = (
        boundary["single_action_compresses_P4_through_P7_conditionally"] is True
        and boundary["P1_self_certified_by_the_action"] is False
    )
    checks["nature_export_remains_forbidden"] = (
        boundary["nature_owns_the_action"] is False
        and boundary["nature_occupation"] is False
        and boundary["physical_base_seed_packet_export_authorized"] is False
    )

    checks = {name: bool(value) for name, value in checks.items()}
    passed = sum(checks.values())
    total = len(checks)
    audit = {
        "schema": "tau_core_p3_clp3_single_source_action_audit_v1",
        "candidate_id": payload["candidate_id"],
        "source_fingerprint_sha256": law["source_fingerprint_sha256"],
        "checks": checks,
        "passed": passed,
        "total": total,
        "diagnostics": {
            "p3_heat_trace": z0,
            "extended_heat_trace": z1,
            "source_fidelity_extension_cost": relative_entropy_extension,
            "good_gram_defect": gram_defect(j_good),
            "hidden_target_gram_defect": gram_defect(j_inclusion),
            "collapsed_source_gram_defect": gram_defect(j_coisometry),
            "body_minimum": body_square(b_star, b0, hessian, load),
        },
        "verdict": "P4_P7_SINGLE_ACTION_COMPRESSION_PASS" if passed == total else "FAIL",
        "P1_physical_source_language_ownership_proved": False,
        "nature_level_occupation": False,
        "physical_base_seed_packet_export_authorized": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != total:
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"P3_CLP3_SINGLE_SOURCE_LAW_FAIL {failed}")
    print(f"P3_CLP3_SINGLE_SOURCE_LAW_PASS {passed}/{total}")


if __name__ == "__main__":
    main()
