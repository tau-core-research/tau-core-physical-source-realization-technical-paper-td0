#!/usr/bin/env python3
"""Audit the global/component P1 source-envelope separator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_source_envelope_separator.json"
OUT = DERIVED / "p3_clp3_p1_source_envelope_separator_audit.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]
    source = payload["independent_source_candidate"]
    embedding = payload["typed_embedding_candidate"]
    rank = payload["faithful_gns_rank_test"]
    staged = payload["downstream_control_only"]
    separator = payload["ontology_separator"]
    boundary = payload["claim_boundary"]

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["prebody_source_candidate_is_independent_of_p3"] = (
        source["source_first"] is True
        and source["derived_from_p3_seed_candidate"] is False
    )
    checks["cl10_matrix_size_is_32"] = source["matrix_size"] == 32
    checks["cl10_algebra_dimension_is_1024"] = (
        source["complex_algebra_dimension"] == 32**2 == 1024
    )
    checks["p3_seed_algebra_is_four_m8_blocks"] = (
        embedding["seed_complex_algebra_dimension"] == 4 * 8**2 == 256
    )
    checks["unital_block_embedding_fills_carrier"] = 4 * 8 == 32
    checks["equal_block_multiplicity_gives_quarter_trace_weights"] = (
        embedding["ambient_trace_restriction"] == "equal central weights 1/4"
    )
    checks["mathematical_embedding_exists_but_physical_ownership_open"] = (
        embedding["mathematical_embedding_exists"] is True
        and embedding["source_owned_typed_embedding_proved"] is False
    )
    checks["faithful_gns_seed_rank_is_256"] = rank["seed_generated_rank"] == 256
    checks["faithful_gns_prebody_rank_is_1024"] = rank["prebody_ambient_rank"] == 1024
    checks["global_rank_gap_is_768"] = rank["missing_ambient_directions"] == 768
    checks["prebody_rank_ratio_is_one_quarter"] = rank["rank_ratio"] == 0.25
    checks["component_p1_survives_global_p1_fails_conditionally"] = (
        rank["component_relative_p1"] is True
        and rank["global_p1_if_prebody_envelope_is_ontic"] is False
    )
    checks["cl16_matrix_size_is_256"] = staged["matrix_size"] == 256
    checks["cl16_algebra_dimension_is_65536"] = (
        staged["complex_algebra_dimension"] == 256**2 == 65536
    )
    checks["staged_envelope_is_not_upstream_p1_input"] = (
        staged["eligible_as_upstream_p1_ambient"] is False
    )
    checks["staged_seed_ratio_is_one_over_256"] = (
        staged["seed_rank_ratio"] == 1 / 256
    )
    checks["local_packet_cannot_choose_envelope_ontology"] = (
        separator["same_p3_local_packet_in_both_branches"] is True
        and separator["local_p3_data_selects_branch"] is False
    )
    checks["nature_ownership_and_export_remain_closed"] = (
        source["nature_ownership_proved"] is False
        and boundary["nature_ambient_source_algebra_owned"] is False
        and boundary["nature_occupation_proved"] is False
        and boundary["physical_base_seed_packet_export_authorized"] is False
    )
    checks["claim_boundary_retains_only_component_completeness"] = (
        boundary["independent_prebody_ambient_candidate_found"] is True
        and boundary["conditional_global_p1_pass"] is False
        and boundary["conditional_global_p1_rejected_under_envelope_ontic_branch"]
        is True
        and boundary["p3_component_completeness_retained"] is True
    )

    checks = {name: bool(value) for name, value in checks.items()}
    passed = sum(checks.values())
    total = len(checks)
    audit = {
        "schema": "tau_core_p1_source_envelope_separator_audit_v1",
        "candidate_id": payload["candidate_id"],
        "source_fingerprint_sha256": packet["source_fingerprint_sha256"],
        "checks": checks,
        "passed": passed,
        "total": total,
        "diagnostics": {
            "p3_component_algebra_dimension": rank["seed_generated_rank"],
            "prebody_pusc_algebra_dimension": rank["prebody_ambient_rank"],
            "prebody_missing_directions": rank["missing_ambient_directions"],
            "prebody_rank_ratio": rank["rank_ratio"],
            "staged_cl16_algebra_dimension": staged[
                "complex_algebra_dimension"
            ],
            "staged_rank_ratio": staged["seed_rank_ratio"],
        },
        "verdict": (
            "P3_COMPONENT_COMPLETE_GLOBAL_P1_FAILS_IF_PREBODY_ENVELOPE_IS_ONTIC"
            if passed == total
            else "FAIL"
        ),
        "nature_level_ambient_choice": "OPEN",
        "physical_P1_exhaustivity_proved": False,
        "physical_base_seed_packet_export_authorized": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != total:
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"P1_SOURCE_ENVELOPE_SEPARATOR_FAIL {failed}")
    print(f"P1_SOURCE_ENVELOPE_SEPARATOR_PASS {passed}/{total} GLOBAL_P1_OPEN")


if __name__ == "__main__":
    main()
