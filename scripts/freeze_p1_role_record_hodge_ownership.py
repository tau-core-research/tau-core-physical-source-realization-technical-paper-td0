#!/usr/bin/env python3
"""Freeze the P3 role--record differential/Hodge ownership audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_hodge_functorial_origin.json"
P3 = DERIVED / "p3_clp3_complete_seed_presentation.json"
OUT = DERIVED / "p3_clp3_p1_role_record_hodge_ownership.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    p3 = json.loads(P3.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-ROLE-RECORD-HODGE-OWNERSHIP-v1",
        "upstream_hodge_functorial_fingerprint_sha256": upstream[
            "source_fingerprint_sha256"
        ],
        "upstream_p3_fingerprint_sha256": p3["source_fingerprint_sha256"],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "typed_carriers": {
            "role_record_algebra": "Cl_7(C) graded_tensor A_port ~= M_8(C)^direct_sum_4",
            "minimal_faithful_jgr_carrier_dimension": 32,
            "regular_exterior_record_carrier": "Lambda^bullet(C^7) tensor C^2_record",
            "regular_exterior_record_carrier_dimension": 256,
            "frozen_p3_hodge": "K_s=N_ext tensor I_2",
        },
        "theorems": {
            "RNE_P1": {
                "name": "role-algebra nilpotent existence",
                "formula": "q_ab=(g_a+i g_b)/2 for a!=b",
                "consequences": [
                    "q_ab is odd and nonzero",
                    "q_ab^2=0",
                    "q_ab^*=(g_a-i g_b)/2",
                    "q_ab q_ab^*+q_ab^* q_ab=1",
                ],
                "status": "proved",
            },
            "RNS_N1": {
                "name": "nilpotent nonselection",
                "statement": (
                    "the frozen role-record relations admit multiple distinct q_ab; "
                    "no current source clause selects one complete differential grammar"
                ),
                "status": "proved_no_go",
            },
            "PHM_N1": {
                "name": "frozen P3 Hodge mismatch",
                "statement": (
                    "no odd nilpotent q on the frozen graded P3 carrier can satisfy "
                    "Delta_q+P_H,q=N_ext tensor I_2"
                ),
                "proof_keys": [
                    "Delta_q+P_H,q is strictly positive in finite dimension",
                    "N_ext tensor I_2 has a two-dimensional kernel",
                    "for the explicit q_ab, Delta_q=I and P_H,q=0",
                ],
                "status": "proved_no_go",
            },
            "RRA_N1": {
                "name": "role algebra does not contain exterior polarization",
                "statement": (
                    "in the regular exterior representation, neither epsilon_a nor "
                    "N_ext belongs to the left Cl_7 role image"
                ),
                "status": "proved_no_go",
            },
            "CAR_P1": {
                "name": "same-exterior-carrier CAR completion",
                "grammar": [
                    "{epsilon_a,epsilon_b}=0",
                    "{iota_a,iota_b}=0",
                    "{iota_a,epsilon_b}=delta_ab 1",
                    "epsilon_a^*=iota_a",
                ],
                "derived_objects": [
                    "g_a=epsilon_a+iota_a",
                    "N_ext=sum_a epsilon_a iota_a",
                    "full-star intertwining implies N_ext transport and common compression",
                ],
                "status": "proved_conditional",
            },
            "M32_N1": {
                "name": "minimal-envelope dimension obstruction",
                "statement": (
                    "the faithful CAR_7 algebra M_128(C) cannot be represented "
                    "faithfully inside the 32-dimensional ontic JGR envelope M_32(C)"
                ),
                "status": "proved_no_go",
            },
        },
        "mvp_relation": {
            "existing_result": (
                "MVP-SHRCHAINCLOSE1 conditionally supplies one nonzero odd nilpotent "
                "recovery incidence N_s from an oriented seed order complex"
            ),
            "not_yet_proved": (
                "a typed star representation identifying that recovery complex with "
                "the seven-mode P3 CAR polarization on the same physical carrier"
            ),
            "single_boundary_operator_is_not_enough": True,
        },
        "branch_decision": {
            "minimal_ontic_jgr": (
                "retain the 32-dimensional carrier and derive a new intrinsic Hodge "
                "operator; the frozen N_ext formula is then not its same-carrier origin"
            ),
            "exterior_car_completion": (
                "retain K_s=N_ext on the 256-dimensional regular carrier and physically "
                "own the CAR_7 polarization; the 32-dimensional carrier-minimality "
                "argument cannot simultaneously select that carrier as ontic"
            ),
        },
        "claim_boundary": {
            "role_algebra_contains_nonzero_odd_nilpotents": True,
            "role_record_packet_selects_one_complete_differential": False,
            "dhf_generates_the_frozen_p3_hodge": False,
            "car7_completion_is_mathematically_explicit": True,
            "physical_source_owns_car7_completion": False,
            "mvp_recovery_incidence_is_identified_with_p3_car7": False,
            "nature_occupation_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
        "exact_remaining_source_datum": (
            "choose and physically own either a 32-dimensional intrinsic JGR Hodge "
            "grammar or the 256-dimensional exterior CAR_7 polarization, and prove its "
            "typed common-source identification with the occupied MVP seed complex"
        ),
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_role_record_hodge_ownership_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_ROLE_RECORD_HODGE_OWNERSHIP_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
