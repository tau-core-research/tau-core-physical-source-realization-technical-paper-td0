#!/usr/bin/env python3
"""Freeze the record--Clifford embedding reduction of the P1 connector packet.

This packet is source first and endpoint blind.  It proves only a conditional
algebraic reduction: after a graded record embedding is supplied, the two
previous connector generators are a gauge frame of one three-dimensional
Clifford complement.  It does not assert that the current Tau source selects
or occupies that embedding.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_envelope_connector_selector.json"
OUT = DERIVED / "p3_clp3_p1_record_clifford_embedding.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-RECORD-CLIFFORD-EMBEDDING-v1",
        "upstream_connector_fingerprint_sha256": upstream[
            "source_fingerprint_sha256"
        ],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "inherited_conditional_structure": {
            "ontic_envelope": "Cl_10(C) isomorphic to M_32(C)",
            "p3_role_space": "E=span(gamma_1,...,gamma_7)",
            "orthogonal_complement": "W=E^perp, dim_R W=3",
            "record_algebra": "A_port=C p_+ direct-sum C p_-",
            "record_difference": "r=p_+-p_-",
            "normalized_trace_weights": [0.5, 0.5],
        },
        "single_embedding_contract": {
            "map": "iota_rec:A_port -> Comm(Cl(E)) intersect Cl(W)^even",
            "requirements": [
                "unital star embedding",
                "iota_rec(r) is self-adjoint",
                "iota_rec(r)^2=1",
                "normalized trace of iota_rec(r) is zero",
                "iota_rec(r) is even in the global Cl_10 grading",
                "Ad_iota_rec(r) preserves the vector complement W",
            ],
            "source_selected": False,
            "nature_occupied": False,
        },
        "derived_split": {
            "W_minus": "ker(Ad_r+I) intersect W",
            "W_plus": "ker(Ad_r-I) intersect W",
            "dimensions": {"W_minus": 2, "W_plus": 1},
            "connector_frame": (
                "choose unit u in W_minus and unit v in W_plus; "
                "set w=-i u r"
            ),
            "gauge_freedom": "SO(2) frame rotation in W_minus and sign of W_plus",
            "gauge_invariant_content": (
                "the graded record embedding and its 2+1 adjoint splitting"
            ),
        },
        "conditional_consequence": {
            "connector_variables_are_independent_primitives": False,
            "two_connector_packet_is": (
                "a gauge-fixed orthonormal frame of one graded record--Clifford embedding"
            ),
            "generated_algebra": "Cl(E direct-sum W)=Cl_10(C)=M_32(C)",
            "faithful_gns_rank": "1024/1024 in the ontic-envelope branch",
            "physical_source_problem_reduced_to": (
                "selection and occupation of iota_rec, not separate ownership of u and v"
            ),
        },
        "non_entailment_controls": {
            "odd_twist": (
                "r_odd=chi_E r_even preserves the local record/P3 reduct but is odd"
            ),
            "chirality_misalignment": (
                "r_mis=P_chi+ r_1 + P_chi- r_2 preserves the local reduct "
                "but is not globally even and does not preserve W"
            ),
            "current_common_source_selects_embedding": False,
            "reason": (
                "the inherited PUSC and port actions contain no cross relation "
                "tying the binary record involution to the even Clifford complement"
            ),
        },
        "claim_boundary": {
            "record_clifford_reduction_proved_conditionally": True,
            "individual_u_v_source_primitives_required": False,
            "graded_embedding_is_derived_from_current_source": False,
            "graded_embedding_is_physically_owned": False,
            "nature_occupation_proved": False,
            "physical_p1_exhaustivity_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_record_clifford_embedding_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_RECORD_CLIFFORD_EMBEDDING_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
