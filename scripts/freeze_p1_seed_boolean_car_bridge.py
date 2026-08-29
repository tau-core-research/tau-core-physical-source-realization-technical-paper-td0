#!/usr/bin/env python3
"""Freeze the conditional MVP seed-Boolean-to-P3 CAR bridge."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_role_record_hodge_ownership.json"
P3 = DERIVED / "p3_clp3_complete_seed_presentation.json"
OUT = DERIVED / "p3_clp3_p1_seed_boolean_car_bridge.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    p3 = json.loads(P3.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-SEED-BOOLEAN-CAR-BRIDGE-v1",
        "upstream_role_record_hodge_fingerprint_sha256": upstream[
            "source_fingerprint_sha256"
        ],
        "upstream_p3_fingerprint_sha256": p3["source_fingerprint_sha256"],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "source_owned_premises": {
            "typed_degree_one_frame": (
                "E_P3=direct_sum_{a=1}^7 L_a with ordered one-dimensional "
                "source-owned role lines"
            ),
            "complete_pointed_boolean_closure": (
                "every subset S of {1,...,7}, including the empty root, is an "
                "occupied admissible exterior word; no face is bypassed"
            ),
            "oriented_insertion_deletion": (
                "epsilon_a inserts role a with the source order sign and "
                "iota_a=epsilon_a^dagger deletes it"
            ),
            "faithful_hodge_realization": (
                "the complete body map preserves the pointed exterior carrier, "
                "its positive Hodge metric, and all seven colored incidences"
            ),
            "record_completion": (
                "the independently typed binary record factor is tensored once "
                "and does not duplicate seed alternatives"
            ),
        },
        "conditional_theorem": {
            "name": "seed Boolean CAR refinement",
            "carrier": "Lambda^bullet(C^7) tensor C^2_record",
            "carrier_dimension": 256,
            "relations": [
                "{epsilon_a,epsilon_b}=0",
                "{iota_a,iota_b}=0",
                "{iota_a,epsilon_b}=delta_ab I",
                "partial=sum_a iota_a and partial^2=0",
                "{partial,partial^dagger}=7 I",
                "N_ext=sum_a epsilon_a iota_a",
            ],
            "conclusion": (
                "the seven colored incidences give the full CAR_7 star algebra, "
                "recover the frozen P3 Clifford generators and exterior number "
                "operator, and reproduce the 256-dimensional exterior-record carrier"
            ),
            "status": "proved_conditional",
        },
        "nonentailment_theorem": {
            "name": "global boundary decomposition no-go",
            "statement": (
                "one global MVP boundary partial, even together with its adjoint, "
                "Hodge Laplacian and exterior number operator, does not select the "
                "seven typed colored incidences"
            ),
            "countermodel": (
                "a nontrivial orthogonal rotation on the six-plane perpendicular "
                "to the all-ones boundary direction fixes partial, its Laplacian, "
                "N_ext and the CAR relations while changing every rotated typed mode"
            ),
            "status": "proved_no_go",
        },
        "face_completeness_theorem": {
            "statement": (
                "removing an allowed Boolean face while retaining compressed "
                "insertions/deletions violates a diagonal CAR identity; a general "
                "non-total order complex therefore does not imply the full P3 CAR_7 grammar"
            ),
            "status": "proved_no_go",
        },
        "mvp_relation": {
            "what_MVP_SHRCHAINCLOSE1_supplies": (
                "one transported nonzero nilpotent alternating boundary partial=N_s"
            ),
            "what_it_does_not_supply": (
                "the source-owned seven-color decomposition, full Boolean face "
                "completion, and typed faithful Hodge realization"
            ),
            "exact_bridge_condition": (
                "MVP-to-P3 CAR refinement holds exactly on the declared class when "
                "the occupied seed complex is the complete pointed oriented Boolean "
                "closure of the seven typed role lines and the base realizes each "
                "colored incidence faithfully"
            ),
        },
        "claim_boundary": {
            "conditional_MVP_to_CAR7_bridge_is_explicit": True,
            "single_global_boundary_selects_typed_CAR7": False,
            "generic_seed_order_complex_implies_boolean_closure": False,
            "current_physical_seed_owns_complete_typed_boolean_closure": False,
            "nature_occupation_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
        "exact_remaining_source_datum": (
            "prove from the physical base-seed action that the occupied seven-role "
            "seed owns the complete pointed oriented Boolean closure and its seven "
            "colored incidences, not merely their uncolored sum N_s"
        ),
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_seed_boolean_car_bridge_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_SEED_BOOLEAN_CAR_BRIDGE_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
