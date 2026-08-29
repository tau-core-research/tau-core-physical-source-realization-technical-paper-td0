#!/usr/bin/env python3
"""Audit the existing-action SNPR source-selection no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_existing_action_snpr_selection.json"
UPSTREAM = DERIVED / "p3_clp3_p1_source_natural_pointed_realization.json"
TRACE_AUDIT = DERIVED / "p3_clp3_p1_trace_gns_booleanization_audit.json"
OUT = DERIVED / "p3_clp3_p1_existing_action_snpr_selection_audit.json"
TOL = 1.0e-12


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    trace_audit = json.loads(TRACE_AUDIT.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]

    # Exact finite fibre witness: each fixed source has a unique response
    # minimum, but the common zero does not select which source fibre exists.
    source_labels = ("target", "control")
    response_centres = {"target": -1.0, "control": 2.0}
    grid = np.linspace(-3.0, 4.0, 7001)
    minima: dict[str, float] = {}
    argmins: dict[str, float] = {}
    for label in source_labels:
        values = (grid - response_centres[label]) ** 2
        index = int(np.argmin(values))
        minima[label] = float(values[index])
        argmins[label] = float(grid[index])

    coverage = payload["action_coverage"]
    fully_selected = {
        name: all(status == "varied_and_forced" for status in statuses)
        for name, statuses in coverage.items()
    }

    diagnostics = trace_audit["diagnostics"]
    checks = {
        "fingerprint_matches_payload": (
            hashlib.sha256(canonical_bytes(payload)).hexdigest()
            == packet["source_fingerprint_sha256"]
        ),
        "upstream_SNPR_packet_is_fingerprint_locked": (
            payload["upstream_snpr_fingerprint_sha256"]
            == upstream["source_fingerprint_sha256"]
        ),
        "endpoint_blind_freeze": (
            payload["terminal_data_used"] is False
            and payload["endpoint_fitted_parameters"] == []
        ),
        "both_source_fibres_have_attainable_zero": (
            max(abs(value) for value in minima.values()) < TOL
        ),
        "each_source_fibre_has_unique_distinct_response_minimum": (
            abs(argmins["target"] - response_centres["target"]) < TOL
            and abs(argmins["control"] - response_centres["control"]) < TOL
            and argmins["target"] != argmins["control"]
        ),
        "equal_floor_does_not_select_external_source_label": (
            minima["target"] == minima["control"]
        ),
        "exact_P3_carrier_control_contains_32D_and_256D_readings": (
            diagnostics["abstract_minimal_faithful_module_dimension"] == 32
            and diagnostics["root_preserving_dimension_lower_bound"] == 256
        ),
        "32D_vector_state_fails_faithful_trace_root_clause": (
            diagnostics["minimal_module_vector_density_rank_per_block"] == 1
            and diagnostics["trace_density_rank_per_block"] == 8
        ),
        "Gamma_CLP3_imports_all_five_source_data_in_this_audit": (
            coverage["Gamma_CLP3"] == ["fixed_input"] * 5
        ),
        "heat_trace_priority_requires_a_predeclared_candidate_and_root_class": (
            coverage["constrained_heat_trace_priority"] == ["fixed_input"] * 5
        ),
        "single_source_realization_action_does_not_self_certify_pointed_language": (
            coverage["L_1src_single_source_realization_action"][-1]
            == "outside_domain"
        ),
        "no_audited_action_varies_and_forces_all_five": (
            not any(fully_selected.values())
        ),
        "conditional_occupation_is_retained": (
            payload["claim_boundary"]["Gamma_CLP3_conditional_occupation_valid"]
            is True
            and payload["claim_boundary"]["SNPR_joint_sufficiency_valid"] is True
        ),
        "Nature_occupation_and_exhaustivity_remain_open": (
            payload["claim_boundary"]["nature_occupation_proved"] is False
            and payload["claim_boundary"]["ambient_parent_exhaustivity_proved"]
            is False
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = sum(checks.values())
    audit = {
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "verdict": (
            "NO_AUDITED_UNCHANGED_ACTION_SELECTS_SNPR1_TO_SNPR5_FROM_THE_"
            "NARROW_REDUCT_GAMMA_CLP3_REMAINS_CONDITIONAL_OCCUPATION_LAW"
        ),
        "diagnostics": {
            "fibre_minima": minima,
            "fibre_argmins": argmins,
            "fully_selected": fully_selected,
            "abstract_module_dimension": diagnostics[
                "abstract_minimal_faithful_module_dimension"
            ],
            "trace_GNS_dimension": diagnostics[
                "root_preserving_dimension_lower_bound"
            ],
        },
        "exact_next_mathematical_target": payload["exact_next_mathematical_target"],
        "physical_source_ownership": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"P1_EXISTING_ACTION_SNPR_SELECTION_AUDIT_FAIL {failed}")
    print(f"P1_EXISTING_ACTION_SNPR_SELECTION_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
