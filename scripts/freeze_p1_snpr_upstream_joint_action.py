#!/usr/bin/env python3
"""Freeze the endpoint-blind USA--SNPR joint source-action packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_source_natural_pointed_realization.json"
OUT = DERIVED / "p3_clp3_p1_snpr_upstream_joint_action.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def main() -> None:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload = {
        "theorem_packet": "USA-SNPR-N1/C1/I1",
        "upstream_snpr_fingerprint_sha256": upstream["source_fingerprint_sha256"],
        "common_source_domain": {
            "variables": [
                "primitive_role_space_V",
                "word_carrier_W",
                "composition_m_and_unit",
                "base_pairing_K",
                "creation_contraction_representation_C",
                "record_object_R",
                "occupied_state_rho",
                "pointed_root_Omega",
                "generated_support_map_pi",
            ],
            "premise_patterns": 32,
        },
        "exact_nonnegative_defects": [
            "oriented_multiplicity_free_exterior_generation",
            "positive_no_bypass_Hodge_realization",
            "binary_dagger_Frobenius_record",
            "full_source_state_naturality",
            "same_state_pointed_cyclic_occupation",
        ],
        "fixed_positive_source_weights": [1, 2, 3, 5, 7],
        "action": "A_SNPR=sum_i lambda_i D_i",
        "reduct_factorisation_control": "A_red=a_after_R",
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "claim_boundary": {
            "common_source_variational_domain_constructed": True,
            "conditional_zero_set_selection": True,
            "direct_sum_defects_irredundant": True,
            "defects_derived_from_one_parent_operator": False,
            "old_bare_entailment": False,
            "nature_occupation": False,
            "ambient_parent_exhaustivity": False,
        },
    }
    packet = {
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": hashlib.sha256(
            canonical_bytes(payload)
        ).hexdigest(),
    }
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
