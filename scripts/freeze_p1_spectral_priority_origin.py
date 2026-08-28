#!/usr/bin/env python3
"""Freeze the structural origin theorem for the JCM spectral priority."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_joint_carrier_minimality.json"
OUT = DERIVED / "p3_clp3_p1_spectral_priority_origin.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-SPECTRAL-PRIORITY-ORIGIN-v1",
        "upstream_jcm_fingerprint_sha256": upstream[
            "source_fingerprint_sha256"
        ],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "trace_origin_theorem": {
            "name": "UTR-P1 compatible trace rigidity",
            "premises": [
                "positive linear functional T_H on every finite carrier",
                "unitary invariance",
                "orthogonal direct-sum compatibility",
                "primitive calibration T_C(1)=1",
            ],
            "conclusion": "T_H=ordinary unnormalized matrix trace",
            "normalized_trace_is_excluded": True,
        },
        "complexity_origin_theorem": {
            "name": "SPS-P1 spectator-stable spectral priority",
            "premises": [
                "complexity depends continuously only on Z=T(exp(-K/A_*))",
                "independent tensor composition is additive",
                "the candidate class is closed under finite faithful spectator duplication",
                "minimization is attained and equality-rigid against proper duplicates",
                "primitive derivative normalization fixes the unit coefficient",
            ],
            "intermediate_form": "C(Z)=c log Z",
            "sign_result": "c>0",
            "normalized_result": "c=1",
            "conclusion": "C_HT=log Tr exp(-K/A_*)",
        },
        "compression_origin_lemma": {
            "name": "HCI-P1 Hodge-compression intertwining",
            "premises": [
                "J:H_0->H_X is isometric",
                "K_X J=J K_0",
            ],
            "conclusion": "J^* K_X J=K_0",
            "algebra_representation_alone_is_insufficient": True,
        },
        "adversarial_controls": {
            "normalized_trace": "violates direct-sum compatibility",
            "zero_log_coefficient": "all faithful spectator duplicates tie",
            "negative_log_coefficient": "spectator duplication drives the objective to minus infinity",
            "no_hodge_intertwining": "the source compression can change and reverse JCM selection",
            "nonlinear_unitarily_invariant_functional": "does not satisfy positive linear trace premises",
        },
        "conditional_consequence": {
            "separate_choice_of_unnormalized_trace_needed": False,
            "separate_choice_of_positive_log_sign_needed": False,
            "separate_same_compression_axiom_needed_after_hodge_intertwining": False,
            "jcm_selection_follows_if_the_structural_packet_is_physically_owned": True,
        },
        "claim_boundary": {
            "structural_uniqueness_proved": True,
            "current_source_co_owns_joint_grammar_and_structural_packet": False,
            "hodge_intertwining_physically_owned_for_all_candidates": False,
            "spectral_sufficiency_and_well_posedness_physically_owned": False,
            "nature_selection_proved": False,
            "physical_p1_exhaustivity_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
        "exact_remaining_source_datum": (
            "physical common ownership and occupation of the joint grammar, "
            "source-Hodge intertwining, spectral sufficiency, tensor "
            "additivity and spectator-stable well-posed minimization"
        ),
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_spectral_priority_origin_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_SPECTRAL_PRIORITY_ORIGIN_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
