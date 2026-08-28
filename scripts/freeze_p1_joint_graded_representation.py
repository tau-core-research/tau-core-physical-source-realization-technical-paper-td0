#!/usr/bin/env python3
"""Freeze the joint-graded-representation interpretation of IGL-P1.

The packet asks whether IGL-P1 is an independent dynamical postulate.  It
records the sharper conditional equivalence: once the abstract P3--record
tensor product is required to have one faithful graded representation in the
same ontic Cl_10 envelope, its record factor lands in the even relative
commutant, and conversely every such landing defines that joint
representation.  Physical ownership of the same-envelope representation is
not derived.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
UPSTREAM = DERIVED / "p3_clp3_p1_record_clifford_source_completion.json"
OUT = DERIVED / "p3_clp3_p1_joint_graded_representation.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-P1-JOINT-GRADED-REPRESENTATION-v1",
        "upstream_igl_fingerprint_sha256": upstream["source_fingerprint_sha256"],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "inherited_source_objects": {
            "abstract_joint_algebra": "Cl(E) graded_tensor A_port",
            "role_dimension": 7,
            "port_algebra": "A_port=C p_+ direct-sum C p_- with trivial even grading",
            "ontic_candidate_envelope": "Cl_10(C)=M_32(C)",
            "fixed_role_embedding": "gamma:Cl(E)->Cl_10(C)",
            "role_restriction_faithful": True,
            "both_odd_clifford_central_sectors_occupied": True,
        },
        "joint_representation_principle": {
            "name": "JGR-P1 same-envelope joint graded realization",
            "map": "Pi_J:Cl(E) graded_tensor A_port -> Cl_10(C)",
            "properties": [
                "unital star monomorphism",
                "graded",
                "extends the fixed role embedding gamma",
                "trace preserving on the equal-weight record factor",
            ],
            "record_image": "iota(b)=Pi_J(1 tensor b)",
            "same_ontic_envelope_is_essential": True,
        },
        "equivalence_theorem": {
            "forward": (
                "JGR-P1 implies iota(A_port) is contained in "
                "Comm(Cl(E)) intersect Cl_10(C)^even"
            ),
            "reverse": (
                "every trace-preserving even-relative-commutant landing "
                "defines Pi_J(a tensor b)=gamma(a)iota(b)"
            ),
            "faithful_image_dimension": 256,
            "igl_residual_is": (
                "the finite relation defect of JGR-P1 after the record "
                "algebra constraints are inherited"
            ),
            "new_independent_dynamical_coefficient": False,
        },
        "adversarial_controls": {
            "external_tensor_model": (
                "a faithful graded representation in Cl_10(C) tensor A_port "
                "satisfies the abstract joint algebra but not same-envelope internality"
            ),
            "odd_internal_model": (
                "a faithful ungraded internal tensor representation can commute "
                "with Cl(E) while failing evenness"
            ),
            "even_role_mixer": (
                "an even record involution can fail tensor-factor commutation"
            ),
        },
        "source_status": {
            "abstract_Cl7_tensor_Aport_owned_conditionally": True,
            "ontic_Cl10_envelope_owned_conditionally": True,
            "same_envelope_joint_graded_representation_owned": False,
            "jgr_p1_selected_by_current_common_action": False,
            "nature_occupied": False,
        },
        "claim_boundary": {
            "igl_is_an_arbitrary_extra_coefficient_law": False,
            "igl_is_equivalent_to_jgr_p1_conditionally": True,
            "current_source_derives_jgr_p1": False,
            "same_source_name_implies_same_envelope_internality": False,
            "physical_p1_exhaustivity_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
    }
    fingerprint = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return {
        "schema": "tau_core_p1_joint_graded_representation_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(
        "P1_JOINT_GRADED_REPRESENTATION_FREEZE "
        f"{packet['source_fingerprint_sha256']}"
    )


if __name__ == "__main__":
    main()
