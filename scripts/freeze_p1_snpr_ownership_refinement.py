#!/usr/bin/env python3
"""Freeze the endpoint-blind SNPR ownership-refinement packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_snpr_upstream_joint_action.json"
OUT = DERIVED / "p3_clp3_p1_snpr_ownership_refinement.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def main() -> None:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload = {
        "theorem_packet": "USA-SNPR-C2/C3/N3",
        "upstream_joint_action_fingerprint_sha256": upstream[
            "source_fingerprint_sha256"
        ],
        "symmetry_branch": {
            "base_state_is_group_fixed": True,
            "response_law_is_equivariant": True,
            "selected_response_is_unique": True,
            "target_contains_noninvariant_orientation_or_pointing": True,
            "conclusion": "noninvariant_source_datum_required",
            "unrestricted_escape_routes": [
                "inhomogeneous_base",
                "explicit_law_breaking",
                "nonunique_spontaneous_branch_with_independent_selector",
            ],
        },
        "exterior_refinement": {
            "primitive_data": [
                "finite_primitive_space_V",
                "unital_associative_composition",
                "odd_interchange",
                "multiplicity_exclusion_v_squared_zero",
                "no_additional_source_relations",
            ],
            "derived_completion": "Lambda_bullet_V_with_empty_root",
        },
        "record_meta_domain": {
            "candidate_class": "exchangeable_finite_special_commutative_dagger_Frobenius_records",
            "eligible_cardinalities": list(range(2, 9)),
            "nontrivial_record_required": True,
            "common_compression": "K_n=K_0_tensor_I_n",
            "trace": "ordinary_unnormalized",
            "priority": "positive_log_heat_trace",
            "selected_cardinality": 2,
        },
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "claim_boundary": {
            "asymmetry_localized_to_seed_on_declared_branch": True,
            "full_exterior_word_list_is_primitive_seed_data": False,
            "binary_record_selected_conditionally": True,
            "physical_record_copy_law_derived": False,
            "meta_law_physically_owned": False,
            "common_PUSC_record_occupation": False,
            "nature_occupation": False,
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
