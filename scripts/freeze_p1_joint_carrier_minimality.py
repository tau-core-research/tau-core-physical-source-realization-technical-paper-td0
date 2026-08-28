#!/usr/bin/env python3
"""Freeze the carrier-minimality route from JGR-P1 to source selection.

The packet does not declare Nature selection.  It records a conditional
theorem: the already frozen joint algebra has minimal faithful carrier
dimension 32, its internal JGR realization attains that dimension, and the
existing unnormalised heat-trace extension theorem rejects faithful proper
carrier extensions when their positive source operator has the same frozen
compression.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_joint_graded_representation.json"
OUT = DERIVED / "p3_clp3_p1_joint_carrier_minimality.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-JOINT-CARRIER-MINIMALITY-v1",
        "upstream_jgr_fingerprint_sha256": upstream[
            "source_fingerprint_sha256"
        ],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "joint_algebra": {
            "name": "Cl_7(C) graded_tensor A_port",
            "block_decomposition": "M_8(C) direct-sum M_8(C) direct-sum M_8(C) direct-sum M_8(C)",
            "simple_block_sizes": [8, 8, 8, 8],
            "complex_algebra_dimension": 256,
            "faithful_carrier_dimension_formula": "8*(m_1+m_2+m_3+m_4), all m_i>=1",
            "minimal_faithful_carrier_dimension": 32,
            "equality_multiplicities": [1, 1, 1, 1],
        },
        "candidate_realizations": {
            "internal": {
                "carrier_dimension": 32,
                "multiplicities": [1, 1, 1, 1],
                "same_ontic_envelope": True,
                "joint_image_dimension": 256,
            },
            "external_tensor_record": {
                "carrier_dimension": 64,
                "multiplicities": [2, 2, 2, 2],
                "same_ontic_envelope": False,
                "joint_image_dimension": 256,
                "proper_extension_of_internal_carrier": True,
            },
        },
        "selection_assumptions": {
            "joint_source_grammar_is_physically_owned": False,
            "faithful_graded_representations_only": True,
            "fixed_role_representation_and_record_trace": True,
            "positive_source_operator": True,
            "same_frozen_internal_compression_on_every_extension": True,
            "heat_trace_uses_unnormalized_trace": True,
            "heat_trace_priority_is_physically_owned": False,
            "nature_occupies_the_minimizer": False,
        },
        "conditional_theorem": {
            "name": "JCM-P1 joint-carrier minimality",
            "statement": (
                "Within faithful graded realizations of the frozen joint "
                "source algebra that extend the same 32-dimensional role "
                "carrier and positive source compression, unnormalized "
                "heat-trace minimization excludes every proper carrier "
                "extension and selects the 32-dimensional same-envelope "
                "JGR class."
            ),
            "selected_carrier_dimension": 32,
            "selected_landing_modulo_gauge": "one Spin(3) orbit",
            "new_fit_parameter": False,
        },
        "adversarial_controls": {
            "normalized_trace": (
                "normalizing by carrier dimension erases the multiplicity "
                "penalty for a duplicated external representation"
            ),
            "changed_compression": (
                "without the same-compression premise an enlarged carrier "
                "can have smaller heat trace by shifting all eigenvalues"
            ),
            "nonfaithful_small_carrier": (
                "dropping one M_8 block gives dimension 24 but has a nonzero kernel"
            ),
            "ungraded_internal": (
                "carrier minimality alone does not replace the graded joint grammar"
            ),
        },
        "claim_boundary": {
            "carrier_minimality_theorem_proved_conditionally": True,
            "same_envelope_follows_under_selection_assumptions": True,
            "current_source_physically_owns_all_selection_assumptions": False,
            "nature_selection_proved": False,
            "physical_p1_exhaustivity_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
        "exact_remaining_source_datum": (
            "common physical ownership and occupation of the frozen joint "
            "grammar plus the unnormalized same-compression heat-trace priority"
        ),
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_joint_carrier_minimality_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_JOINT_CARRIER_MINIMALITY_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
