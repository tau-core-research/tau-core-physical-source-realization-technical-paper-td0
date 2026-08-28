#!/usr/bin/env python3
"""Freeze the P3/CLP3 single-source action candidate.

The action compresses P4--P7 into one nonnegative, Schur-neutral parent law
after a complete seed grammar has been supplied.  It deliberately does not
claim that the action can certify the completeness of its own source language
or that Nature occupies the candidate.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
P3_PACKET = DERIVED / "p3_clp3_complete_seed_presentation.json"
OUT = DERIVED / "p3_clp3_single_source_law.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    p3 = json.loads(P3_PACKET.read_text(encoding="utf-8"))
    source_payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-SSAC-v1",
        "freeze_date": "2026-08-28",
        "status": "SOURCE_FROZEN_SINGLE_ACTION_CONDITIONAL_CANDIDATE",
        "upstream_seed_candidate_id": p3["source_freeze_payload"]["candidate_id"],
        "upstream_seed_fingerprint_sha256": p3["source_fingerprint_sha256"],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "source_law": {
            "name": "source-fidelity Gram body-square action",
            "formula": "L_1src=I_Sat(X)+A_*D(rhohat_s||rho_X)+(A_*/2)Gamma_GE(J)+Q_B(b;s)",
            "gram_defect": "Gamma_GE(J)=||J^dagger J-I_src||_HS^2+||J J^dagger-I_phys||_HS^2",
            "body_square": "Q_B=1/2<b-b0,K_B(b-b0)>-<j_B(s),b-b0>+1/2<j_B(s),K_B^-1 j_B(s)>",
            "body_square_equivalent": "Q_B=1/2||K_B^(1/2)(b-b0-K_B^-1 j_B(s))||^2",
            "generative_order": [
                "freeze the complete source grammar and exact compatibility fibre",
                "select the source-equivalence completion by source fidelity",
                "realize it through the two-sided Gram-zero map",
                "solve the Schur-neutral body square",
            ],
            "units": {
                "A_*": "action",
                "relative_entropy": "dimensionless",
                "Gamma_GE": "dimensionless in source-normalized Hodge frames",
                "Q_B": "action",
            },
        },
        "assumptions": {
            "S1": "a physically supplied complete seed grammar and complete residual family define Sat",
            "S2": "faithful Hodge states exist on a fixed common domain and equality is rigid modulo Hodge-unitary source equivalence",
            "S3": "the parent counts source-fidelity mismatch and the two-sided Gram defect once and positively",
            "S4": "K_B is source-independent, positive and invertible; j_B(s) is the typed seed first variation",
            "S5": "the admitted comparison lies in one seed-fixed connected Hodge-generated component, or relative component characters are supplied",
        },
        "derived_premise_status": {
            "P1_complete_seed_physically_owned": "NOT_DERIVED; S1 supplies the source language",
            "P2_exact_compatible_fibre": "INHERITED_AND_ENFORCED_BY_I_Sat",
            "P3_positive_trace_class_hodge_action": "INHERITED_FROM_P3_CLP3_FINITE_PACKET",
            "P4_physical_spectral_priority": "DERIVED_CONDITIONALLY_FROM_POSITIVE_SOURCE_FIDELITY_TERM",
            "P5_attainment_and_equality_rigidity": "DERIVED_CONDITIONALLY_UNDER_S2_AND_S5",
            "P6_two_sided_typed_realization": "DERIVED_CONDITIONALLY_FROM_Gamma_GE_MINIMUM_ZERO",
            "P7_td1_regular_handoff": "DERIVED_CONDITIONALLY_FROM_Q_B_WITH_K_B_POSITIVE",
        },
        "countermodels": {
            "incomplete_language": "an undeclared relation direction can leave every declared source residual zero",
            "wrong_fidelity_sign": "negative relative-entropy sign selects a proper source-compatible extension",
            "one_sided_gram": "isometric inclusion or coisometry hides target or source support",
            "component_zero_jet": "an independent component constant can reverse the global minimum without changing the Hodge packet",
            "nonpositive_body_hessian": "loss of positive invertibility destroys the unique regular body handoff",
        },
        "claim_boundary": {
            "single_action_compresses_P4_through_P7_conditionally": True,
            "P1_self_certified_by_the_action": False,
            "old_bare_tau_derives_the_action": False,
            "nature_owns_the_action": False,
            "nature_occupation": False,
            "physical_base_seed_packet_export_authorized": False,
            "empirical_validation": False,
        },
    }
    fingerprint = hashlib.sha256(canonical_bytes(source_payload)).hexdigest()
    return {
        "schema": "tau_core_p3_clp3_single_source_action_v1",
        "source_freeze_payload": source_payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(f"P3_CLP3_SINGLE_SOURCE_LAW_FREEZE {packet['source_fingerprint_sha256']}")


if __name__ == "__main__":
    main()
