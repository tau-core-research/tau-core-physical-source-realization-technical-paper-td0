#!/usr/bin/env python3
"""Freeze the endpoint-blind operational record-origin packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_snpr_ownership_refinement.json"
OUT = DERIVED / "p3_clp3_p1_operational_record_origin.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def main() -> None:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload = {
        "theorem_packet": "USA-SNPR-C4/C5/N4",
        "upstream_ownership_refinement_fingerprint_sha256": upstream[
            "source_fingerprint_sha256"
        ],
        "operational_record_axioms": [
            "exact_common_logical_decoder_on_every_port",
            "exact_recovery_after_loss_of_all_but_one_port",
            "independently_composable_port_local_changes",
            "source_faithful_product_complete_joint_decoder",
            "primitive_deterministic_occupation",
            "common_positive_trace_Hodge_metric_and_dagger_closure",
        ],
        "declared_consequences": {
            "joint_carrier": "Y_mk_isomorphic_to_A_m_tensor_power_k",
            "copy_map": "Delta_mk_e_i_equals_e_i_tensor_power_k",
            "two_port_law": "special_commutative_dagger_Frobenius",
        },
        "selector": {
            "logical_alternatives": list(range(2, 7)),
            "physical_ports": list(range(2, 6)),
            "compression": "K_mk=K_0_tensor_I_(m_power_k)",
            "trace": "ordinary_unnormalized",
            "priority": "positive_log_heat_trace",
            "selected_pair": [2, 2],
        },
        "incidence_control": {
            "PUSC_alternatives": 2,
            "record_alternatives": 2,
            "models": ["perfectly_correlated", "independent"],
            "same_marginals_required": True,
        },
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "claim_boundary": {
            "copy_law_derived_inside_operational_class": True,
            "two_alternatives_two_ports_selected_conditionally": True,
            "operational_class_physically_owned": False,
            "full_carrier_priority_physically_owned": False,
            "common_PUSC_record_incidence_derived": False,
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
