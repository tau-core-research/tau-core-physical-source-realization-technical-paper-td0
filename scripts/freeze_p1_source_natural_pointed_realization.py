#!/usr/bin/env python3
"""Freeze the source-natural pointed realization composition theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
TRACE_GNS = DERIVED / "p3_clp3_p1_trace_gns_booleanization.json"
ROLE_HODGE = DERIVED / "p3_clp3_p1_role_record_hodge_ownership.json"
OUT = DERIVED / "p3_clp3_p1_source_natural_pointed_realization.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    trace_gns = json.loads(TRACE_GNS.read_text(encoding="utf-8"))
    role_hodge = json.loads(ROLE_HODGE.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-SOURCE-NATURAL-POINTED-REALIZATION-v1",
        "upstream_trace_gns_fingerprint_sha256": trace_gns[
            "source_fingerprint_sha256"
        ],
        "upstream_role_hodge_fingerprint_sha256": role_hodge[
            "source_fingerprint_sha256"
        ],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "premises": {
            "SNPR1_oriented_multiplicity_free_seed": (
                "the complete unital seven-role possibility grammar is generated "
                "by oriented primitive occurrences with v^2=0 and no additional relations"
            ),
            "SNPR2_positive_hodge_realization": (
                "the base supplies one positive K_* and realizes each typed role as "
                "epsilon(v)+iota_{K_*(v,-)} with no bypass"
            ),
            "SNPR3_binary_frobenius_record": (
                "one source-owned exchangeable binary Frobenius unfolding supplies "
                "two typed record ports and their symmetric pointed root"
            ),
            "SNPR4_full_source_naturality": (
                "the occupied source state is invariant under every within-block inner "
                "frame automorphism and the transitive grade/record block exchanges"
            ),
            "SNPR5_pointed_cyclic_occupation": (
                "the empty exterior word and symmetric record root are physically "
                "occupied, their vector state is the occupied state constrained by "
                "SNPR4, and their generated orbit is the complete required support"
            ),
        },
        "composition_theorem": {
            "name": "SNPR-P1 source-natural pointed realization",
            "chain": [
                "SNPR1 implies Lambda^bullet(C^7) with its empty-word root",
                "SNPR2 implies typed CAR_7 and Cl_7(C)",
                "SNPR3 implies A_port=C^2 and A_J=M_8(C)^{oplus 4}",
                "SNPR4 uniquely fixes tau_sym=(1/4)sum tr_8",
                "SNPR5 plus the Hodge realization makes the root orbit the faithful trace-GNS packet",
                "GNS faithfulness forces dimension 256 and word degree recovers N_ext",
            ],
            "conclusion": (
                "the complete P3 relation, symmetry, cyclic occupation, 256-dimensional "
                "carrier and Boolean/CAR_7 Hodge grammar follow jointly, up to typed unitary"
            ),
            "status": "proved_conditional_composition",
        },
        "independence_controls": {
            "without_SNPR1": "tensor and symmetric seed grammars share the primitive inventory",
            "without_SNPR2": "an oriented word inventory need not carry the adjoint CAR realization",
            "without_SNPR3": "the Clifford packet has 128 rather than 256 algebra/GNS dimensions",
            "without_SNPR4_inner_naturality": "a faithful full-rank nontracial block density survives",
            "without_SNPR4_block_exchange": "unequal positive central block weights survive",
            "without_SNPR5": "a rootless or spectator-extended realization has the same algebraic relations but different occupation",
        },
        "claim_boundary": {
            "mathematical_composition_closed_under_SNPR1_to_SNPR5": True,
            "SNPR1_to_SNPR5_follow_from_old_bare_tau": False,
            "physical_parent_owns_SNPR1_to_SNPR5": False,
            "nature_occupation_proved": False,
            "terminal_data_used_for_selection": False,
        },
        "exact_remaining_physical_statement": (
            "the unrestricted physical base-seed parent realizes SNPR1--SNPR5; "
            "equivalently it owns the oriented multiplicity-free pointed seed, the "
            "positive no-bypass Hodge realization, the binary record unfolding and "
            "full source naturality on one occupied packet"
        ),
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_source_natural_pointed_realization_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_SOURCE_NATURAL_POINTED_REALIZATION_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
