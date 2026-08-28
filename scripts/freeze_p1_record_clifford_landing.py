#!/usr/bin/env python3
"""Freeze the minimal record--Clifford landing-law reduction.

The packet is endpoint blind.  It does not choose an embedding representative.
It records the sharper fact that, once the binary record algebra is required to
land in the even relative commutant of the P3 Clifford algebra, trace
preservation leaves a single Spin(3)-gauge orbit.  The present separate
PUSC-plus-record action does not contain that cross-landing relation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_record_clifford_embedding.json"
OUT = DERIVED / "p3_clp3_p1_record_clifford_landing.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-RECORD-CLIFFORD-LANDING-v1",
        "upstream_embedding_fingerprint_sha256": upstream[
            "source_fingerprint_sha256"
        ],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "inherited_objects": {
            "role_algebra": "Cl(E), dim_R(E)=7",
            "ontic_envelope": "Cl_10(C)=M_32(C)",
            "complement": "W=E^perp, dim_R(W)=3",
            "record_algebra": "A_port=C p_+ direct-sum C p_-",
            "record_trace": "tau_port(p_+)=tau_port(p_-)=1/2",
            "record_involution": "r=p_+-p_-",
        },
        "minimal_cross_law": {
            "name": "even-relative-commutant landing",
            "statement": (
                "the physical record representation is a unital "
                "trace-preserving star monomorphism from A_port into "
                "Comm(Cl(E)) intersect Cl_10(C)^even"
            ),
            "equivalent_codomain": "Cl(W)^even isomorphic to M_2(C)",
            "source_selected_by_current_pusc_record_action": False,
            "nature_occupied": False,
        },
        "automatic_consequences": {
            "minimal_record_projector_ranks": [1, 1],
            "record_difference_is": "a self-adjoint traceless involution",
            "vector_complement_preservation": "automatic",
            "adjoint_split": {"minus": 2, "plus": 1},
            "all_embeddings_form": "one Spin(3)-conjugacy orbit",
            "record_label_exchange": "contained in the same gauge orbit",
            "continuous_embedding_parameter": False,
            "separate_vector_preservation_premise_required": False,
            "separate_connector_direction_selection_required": False,
        },
        "current_source_audit": {
            "joint_action": (
                "Gamma_PUSC(z)+A_*/2 ||y-mu^dagger chi(z)||^2"
            ),
            "owns_pusc_and_record_together": True,
            "owns_tensor_leg_record_domain_conditionally": True,
            "contains_record_to_clifford_map_variable": False,
            "contains_even_relative_commutant_cross_residual": False,
            "embedding_direction_has_euler_equation": False,
            "verdict": "CURRENT_COMMON_ACTION_DOES_NOT_FORCE_THE_LANDING",
        },
        "adversarial_controls": {
            "independent_tensor_record": (
                "Cl_7(C) tensor A_port realizes the four local blocks but "
                "does not identify A_port with the even complement"
            ),
            "odd_twist": (
                "an odd record involution preserves the same local P3/record "
                "block data while violating the landing law"
            ),
            "interpretation": (
                "local common occupation is weaker than typed cross-incidence"
            ),
        },
        "claim_boundary": {
            "even_landing_implies_unique_gauge_orbit": True,
            "complement_preservation_is_redundant_after_even_landing": True,
            "current_source_derives_even_landing": False,
            "physical_source_ownership_proved": False,
            "nature_occupation_proved": False,
            "physical_p1_exhaustivity_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_record_clifford_landing_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_RECORD_CLIFFORD_LANDING_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
