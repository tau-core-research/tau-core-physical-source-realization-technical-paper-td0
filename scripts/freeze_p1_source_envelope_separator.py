#!/usr/bin/env python3
"""Freeze the source-envelope separator for global versus component P1.

The pre-body PUSC envelope is imported as an independently declared source
candidate.  It is not derived from the P3/CLP3 presentation and it is not
claimed to be selected by Nature.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
SEED_PACKET = DERIVED / "p3_clp3_complete_seed_presentation.json"
OUT = DERIVED / "p3_clp3_p1_source_envelope_separator.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    seed_packet = json.loads(SEED_PACKET.read_text(encoding="utf-8"))
    seed_payload = seed_packet["source_freeze_payload"]
    seed_algebra = seed_payload["complete_seed_presentation"]["quotient_algebra"]

    prebody_rows = 10
    prebody_matrix_size = 2 ** (prebody_rows // 2)
    prebody_algebra_dimension = prebody_matrix_size**2
    seed_algebra_dimension = int(seed_algebra["complex_dimension"])

    full_rows = 16
    full_matrix_size = 2 ** (full_rows // 2)
    full_algebra_dimension = full_matrix_size**2

    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-SEPARATOR-v1",
        "upstream_seed_candidate_id": seed_payload["candidate_id"],
        "upstream_seed_fingerprint_sha256": seed_packet[
            "source_fingerprint_sha256"
        ],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "independent_source_candidate": {
            "name": "PUSC-P1 pre-body simple defect envelope",
            "canonical_owner": (
                "docs/tau_core_hypergraph_pre_response_carrier_derivation_001.md"
                "#definition-pusc-p1-protected-unital-source-calculus"
            ),
            "relation_row_count": prebody_rows,
            "algebra": "Cl_10(C) isomorphic to M_32(C)",
            "matrix_size": prebody_matrix_size,
            "complex_algebra_dimension": prebody_algebra_dimension,
            "faithful_state": "normalized matrix trace",
            "source_first": True,
            "derived_from_p3_seed_candidate": False,
            "nature_ownership_proved": False,
        },
        "typed_embedding_candidate": {
            "seed_algebra": "Cl_7(C) tensor (C direct-sum C)",
            "seed_isomorphism_class": seed_algebra["isomorphism_class"],
            "seed_complex_algebra_dimension": seed_algebra_dimension,
            "embedding": (
                "unital block-diagonal star embedding of four M_8(C) blocks "
                "into M_32(C), each with multiplicity one"
            ),
            "ambient_trace_restriction": "equal central weights 1/4",
            "mathematical_embedding_exists": True,
            "source_owned_typed_embedding_proved": False,
        },
        "faithful_gns_rank_test": {
            "seed_generated_rank": seed_algebra_dimension,
            "prebody_ambient_rank": prebody_algebra_dimension,
            "rank_ratio": seed_algebra_dimension / prebody_algebra_dimension,
            "missing_ambient_directions": (
                prebody_algebra_dimension - seed_algebra_dimension
            ),
            "component_relative_p1": True,
            "global_p1_if_prebody_envelope_is_ontic": False,
        },
        "downstream_control_only": {
            "name": "PUSC-PBSE common staged envelope",
            "relation_row_count": full_rows,
            "algebra": "Cl_16(C) isomorphic to M_256(C)",
            "matrix_size": full_matrix_size,
            "complex_algebra_dimension": full_algebra_dimension,
            "seed_rank_ratio": seed_algebra_dimension / full_algebra_dimension,
            "eligible_as_upstream_p1_ambient": False,
            "reason": (
                "PBSE is post-body, so using the staged Cl_16 envelope to "
                "construct an upstream seed-completeness premise would reverse "
                "the Tau generative order"
            ),
        },
        "ontology_separator": {
            "envelope_ontic_branch": (
                "if the pre-body Cl_10 envelope is the physical source algebra "
                "and the typed embedding is physical, P3 global P1 fails by rank"
            ),
            "metric_auxiliary_branch": (
                "if the Clifford envelope is only a norm/trace completion, the "
                "P3 local packet cannot identify the smaller physical algebra"
            ),
            "same_p3_local_packet_in_both_branches": True,
            "local_p3_data_selects_branch": False,
            "nature_level_decision": "OPEN",
        },
        "claim_boundary": {
            "independent_prebody_ambient_candidate_found": True,
            "conditional_global_p1_pass": False,
            "conditional_global_p1_rejected_under_envelope_ontic_branch": True,
            "p3_component_completeness_retained": True,
            "nature_ambient_source_algebra_owned": False,
            "nature_occupation_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_source_envelope_separator_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(f"P1_SOURCE_ENVELOPE_SEPARATOR_FREEZE {packet['source_fingerprint_sha256']}")


if __name__ == "__main__":
    main()
