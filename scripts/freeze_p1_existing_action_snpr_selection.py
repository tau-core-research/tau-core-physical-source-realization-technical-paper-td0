#!/usr/bin/env python3
"""Freeze the registered-action coverage of the five SNPR source premises."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_source_natural_pointed_realization.json"
OUT = DERIVED / "p3_clp3_p1_existing_action_snpr_selection.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    premises = [f"SNPR{i}" for i in range(1, 6)]
    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-EXISTING-ACTION-SNPR-SELECTION-v1",
        "upstream_snpr_fingerprint_sha256": upstream["source_fingerprint_sha256"],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "selection_status_vocabulary": {
            "varied_and_forced": (
                "the source datum is a variable in one common candidate domain "
                "and every global minimum has the target property"
            ),
            "fixed_input": (
                "the datum is supplied by the law packet or admissible domain; "
                "the action proves only conditional occupation"
            ),
            "not_forced": "an exact same-zero control violates the target property",
            "outside_domain": "the action contains no variable of this source type",
        },
        "premises": premises,
        "action_coverage": {
            "P3_RL6_unchanged": [
                "fixed_input", "fixed_input", "fixed_input", "not_forced", "not_forced"
            ],
            "P3_RL6F": [
                "fixed_input", "fixed_input", "fixed_input", "fixed_input", "fixed_input"
            ],
            "L_P3_min": [
                "fixed_input", "fixed_input", "fixed_input", "fixed_input", "fixed_input"
            ],
            "Gamma_CLP3": [
                "fixed_input", "fixed_input", "fixed_input", "fixed_input", "fixed_input"
            ],
            "source_fidelity_Hodge": [
                "fixed_input", "fixed_input", "outside_domain", "fixed_input", "outside_domain"
            ],
            "constrained_heat_trace_priority": [
                "fixed_input", "fixed_input", "fixed_input", "fixed_input", "fixed_input"
            ],
            "L_1src_single_source_realization_action": [
                "fixed_input", "fixed_input", "fixed_input", "fixed_input", "outside_domain"
            ],
        },
        "exact_action_domain_reading": {
            "P3_RL6_unchanged": (
                "the relation and two-leg record defects do not vary the root-state Gram"
            ),
            "P3_RL6F": (
                "the explicit Gram defect closes the metric lock only in the supplied pointed class"
            ),
            "L_P3_min": (
                "D_SF, the faithful separating state and Omega_empty are in the law packet"
            ),
            "Gamma_CLP3": (
                "JLC5 imports L_P3_min including support, ports, decoder, operator square and root"
            ),
            "source_fidelity_Hodge": (
                "the reference state and Hodge source class are supplied; record and root are absent"
            ),
            "constrained_heat_trace_priority": (
                "the priority orders an already declared common-compression candidate class; grammar, record domain and root eligibility are supplied"
            ),
            "L_1src_single_source_realization_action": (
                "the action realizes a supplied complete residual language and cannot self-certify that language or select pointing"
            ),
        },
        "general_no_go": {
            "name": "EAS-SNPR-N1 external-source variational nonselection",
            "premise": (
                "two source fibres share the narrow reduct and attainable action floor "
                "but disagree on the target source property"
            ),
            "conclusion": (
                "fibrewise Euler-Lagrange equations cannot select the property when "
                "the source datum is not varied and no cross-fibre law is supplied"
            ),
            "status": "proved_no_go",
        },
        "claim_boundary": {
            "Gamma_CLP3_conditional_occupation_valid": True,
            "SNPR_joint_sufficiency_valid": True,
            "one_audited_unchanged_action_selects_all_five_from_narrow_reduct": False,
            "nature_occupation_proved": False,
            "ambient_parent_exhaustivity_proved": False,
        },
        "exact_next_mathematical_target": (
            "one endpoint-blind upstream source variational domain containing grammar, "
            "positive realization, binary record, invariant state and pointing alternatives"
        ),
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_existing_action_snpr_selection_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_EXISTING_ACTION_SNPR_SELECTION_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
