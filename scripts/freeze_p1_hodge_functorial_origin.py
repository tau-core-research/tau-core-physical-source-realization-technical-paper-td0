#!/usr/bin/env python3
"""Freeze the dagger-functorial origin theorem for source-Hodge transport."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_spectral_priority_origin.json"
OUT = DERIVED / "p3_clp3_p1_hodge_functorial_origin.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-HODGE-FUNCTORIAL-ORIGIN-v1",
        "upstream_spectral_priority_fingerprint_sha256": upstream[
            "source_fingerprint_sha256"
        ],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "theorem": {
            "name": "DHF-P1 dagger-functorial Hodge transport",
            "source_grammar": {
                "type": "finite graded star differential grammar",
                "odd_generator": "q",
                "relations": ["q^2=0", "star closure contains q^*"],
            },
            "premises": [
                "pi_0 and pi_X are graded star representations of the same grammar",
                "d_i=pi_i(q) and d_i^*=pi_i(q^*)",
                "J:H_0->H_X is a degree-preserving isometry",
                "J intertwines the complete star grammar",
            ],
            "derived_chain": [
                "d_X J=J d_0",
                "d_X^* J=J d_0^*",
                "Delta_X J=J Delta_0",
                "P_H,X J=J P_H,0",
                "Khat_X J=J Khat_0 for Khat=Delta+P_H",
                "J^* Khat_X J=Khat_0",
            ],
            "dimensional_convention": (
                "Khat is dimensionless and K=A_* Khat carries action units"
            ),
        },
        "minimality_and_controls": {
            "unstarred_cochain_intertwining_only": (
                "insufficient because complement-to-source incidence can alter d^*"
            ),
            "nonisometric_intertwiner": (
                "preserves operator intertwining but not normalized compression"
            ),
            "changed_harmonic_policy": (
                "an independently assigned projector need not be functorial"
            ),
            "algebra_only_without_differential_generator": (
                "does not determine a Hodge operator"
            ),
        },
        "conditional_consequence": {
            "separate_hodge_intertwining_axiom_needed": False,
            "if_complete_star_differential_grammar_is_physically_owned": True,
            "same_compression_then_follows": True,
        },
        "claim_boundary": {
            "finite_dagger_functorial_theorem_proved": True,
            "current_joint_role_record_grammar_contains_q_and_q_star": False,
            "physical_source_owns_complete_star_differential_grammar": False,
            "nature_occupation_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
        "exact_remaining_source_datum": (
            "physical co-ownership of the joint role-record grammar and the "
            "complete star-closed differential generator on the same carrier"
        ),
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_hodge_functorial_origin_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_HODGE_FUNCTORIAL_ORIGIN_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
