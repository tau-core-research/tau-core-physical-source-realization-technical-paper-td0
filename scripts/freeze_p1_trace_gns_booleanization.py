#!/usr/bin/env python3
"""Freeze the trace-GNS carrier and Clifford-word Booleanization theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
P3 = DERIVED / "p3_clp3_complete_seed_presentation.json"
BOOLEAN = DERIVED / "p3_clp3_p1_seed_boolean_car_bridge.json"
OUT = DERIVED / "p3_clp3_p1_trace_gns_booleanization.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    p3 = json.loads(P3.read_text(encoding="utf-8"))
    boolean = json.loads(BOOLEAN.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-TRACE-GNS-BOOLEANIZATION-v1",
        "upstream_p3_fingerprint_sha256": p3["source_fingerprint_sha256"],
        "upstream_boolean_fingerprint_sha256": boolean[
            "source_fingerprint_sha256"
        ],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "typed_input": {
            "source_algebra": "A=M_8(C) direct_sum M_8(C) direct_sum M_8(C) direct_sum M_8(C)",
            "source_state": (
                "tau_sym=(1/4) sum_alpha tr_8 on the four source-natural blocks"
            ),
            "physical_root_clause": (
                "the occupied carrier is the cyclic GNS orbit closure of one root "
                "Omega whose vector state is tau_sym"
            ),
            "typed_clifford_frame": "seven source-owned generators g_a",
        },
        "theorems": {
            "faithful_gns_dimension": {
                "statement": (
                    "for a faithful state on a finite-dimensional star algebra, "
                    "the GNS null left ideal is zero, hence dim H_GNS=dim_C A=256"
                ),
                "status": "proved",
            },
            "minimal_module_control": {
                "statement": (
                    "a 32-dimensional one-copy-per-block faithful module exists, "
                    "but no vector on it induces a faithful state on any M_8 block; "
                    "therefore it is not the declared faithful cyclic GNS-root carrier"
                ),
                "status": "proved_no_go",
            },
            "clifford_word_booleanization": {
                "statement": (
                    "the 128 ordered Clifford words g_S Omega form an orthonormal "
                    "basis of the Clifford part; word degree splits every g_a uniquely "
                    "into degree-raising epsilon_a and degree-lowering iota_a, which "
                    "obey CAR_7 and recover the pointed exterior/Boolean grammar"
                ),
                "status": "proved_conditional",
            },
        },
        "carrier_typing_correction": {
            "abstract_minimal_faithful_module_dimension": 32,
            "faithful_trace_gns_carrier_dimension": 256,
            "conclusion": (
                "JCM-P1 selects 32 only in a root-free abstract representation class. "
                "It cannot select the carrier of the already declared faithful "
                "trace-GNS root. In the root-preserving class the 256-dimensional "
                "regular GNS carrier is forced up to unitary equivalence."
            ),
        },
        "claim_boundary": {
            "trace_gns_root_implies_256_carrier": True,
            "typed_clifford_plus_degree_implies_boolean_car": True,
            "global_boundary_alone_selects_typed_frame": False,
            "narrow_old_bare_tau_owns_trace_gns_root": False,
            "nature_occupation_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
        "exact_remaining_physical_datum": (
            "show that the unrestricted physical base-seed law owns and occupies the "
            "source-natural faithful trace-GNS root together with the typed seven-role "
            "Clifford frame; the representation-theoretic 32-versus-256 ambiguity is "
            "then closed, but Nature-level source selection is not"
        ),
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_trace_gns_booleanization_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_TRACE_GNS_BOOLEANIZATION_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
