#!/usr/bin/env python3
"""Freeze the conditional two-connector completion of the P3/PUSC envelope.

The packet is source-first and endpoint blind.  It constructs a minimal
Clifford connector grammar inside the already declared pre-body PUSC carrier;
it does not claim that Nature owns or occupies that grammar.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
SEPARATOR = DERIVED / "p3_clp3_p1_source_envelope_separator.json"
OUT = DERIVED / "p3_clp3_p1_envelope_connector_selector.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    separator = json.loads(SEPARATOR.read_text(encoding="utf-8"))
    separator_payload = separator["source_freeze_payload"]

    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-CONNECTOR-v1",
        "upstream_separator_id": separator_payload["candidate_id"],
        "upstream_separator_fingerprint_sha256": separator[
            "source_fingerprint_sha256"
        ],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "declared_prebody_carrier": {
            "representation": "irreducible 32-dimensional Cl_10(C) module",
            "p3_role_generators": [f"gamma_{index}" for index in range(1, 8)],
            "p3_record_involution": "r = i gamma_8 gamma_9",
            "p3_chirality_involution": "chi = i gamma_1 ... gamma_7",
            "p3_central_blocks": "p_(s,t)=(1+s chi)(1+t r)/4",
            "central_block_count": 4,
            "central_block_rank": 8,
            "p3_algebra": "M_8(C) direct-sum M_8(C) direct-sum M_8(C) direct-sum M_8(C)",
            "p3_complex_algebra_dimension": 256,
            "pusc_algebra": "Cl_10(C) isomorphic to M_32(C)",
            "pusc_complex_algebra_dimension": 1024,
        },
        "connector_grammar": {
            "u": "gamma_8",
            "v": "gamma_10",
            "recovered_generator": "gamma_9 = -i u r",
            "u_relations": [
                "u=u^dagger",
                "u^2=1",
                "{u,gamma_a}=0 for a=1,...,7",
                "{u,r}=0",
            ],
            "v_relations": [
                "v=v^dagger",
                "v^2=1",
                "{v,gamma_a}=0 for a=1,...,7",
                "[v,r]=0",
                "{u,v}=0",
            ],
            "connector_count": 2,
            "connector_count_is_minimal_in_declared_grading_class": True,
        },
        "algebra_rank_ladder": {
            "p3_only": 256,
            "p3_plus_u": 512,
            "p3_plus_v": 512,
            "p3_plus_u_and_v": 1024,
            "single_connector_is_globally_exhaustive": False,
            "two_connectors_are_globally_exhaustive": True,
        },
        "single_connector_defect_action": {
            "name": "L_conn",
            "form": (
                "sum of normalized Hilbert-Schmidt squares of the u/v "
                "self-adjoint-unitary, grading, record and mutual-Clifford defects"
            ),
            "nonnegative": True,
            "zero_locus_generates_cl10": True,
            "zero_connector_control_has_positive_defect": True,
            "wrong_scaled_connector_control_has_positive_defect": True,
            "source_domain_and_relation_grammar_are_inputs_to_the_action": True,
        },
        "conditional_consequence": {
            "if_parent_owns_u_v_domain_and_defect_action": (
                "every zero-defect 32-dimensional unital realization generates "
                "Cl_10(C)=M_32(C), so the expanded seed algebra has faithful-GNS "
                "rank 1024/1024 relative to the ontic PUSC envelope"
            ),
            "p3_only_action_can_create_new_typed_connector_variables": False,
            "physical_choice_reduced_to": (
                "source ownership and occupation of the two connector incidences "
                "u and v, or an equivalent connected block-incidence packet"
            ),
        },
        "ontology_decision": {
            "ontic_pusc_requires_connectors_or_equivalent_nonnull_incidence": True,
            "p3_without_connectors_is_not_global_p1_in_ontic_pusc": True,
            "simple_m32_has_no_nontrivial_star_ideal_for_a_p3_null_quotient": True,
            "preserving_p3_as_complete_requires_nonontic_auxiliary_or_different_ambient": True,
            "current_p3_packet_selects_u_v": False,
            "nature_selects_u_v": False,
        },
        "claim_boundary": {
            "conditional_ontic_completion_constructed": True,
            "minimal_connector_theorem_proved_in_declared_clifford_class": True,
            "unrestricted_minimality_over_all_parent_algebras_proved": False,
            "current_tau_source_owns_connector_grammar": False,
            "nature_occupation_proved": False,
            "physical_p1_exhaustivity_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_envelope_connector_selector_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_ENVELOPE_CONNECTOR_SELECTOR_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
