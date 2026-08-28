#!/usr/bin/env python3
"""Freeze the finite independent-ambient certificate candidate for P1."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
SEED_PACKET = DERIVED / "p3_clp3_complete_seed_presentation.json"
OUT = DERIVED / "p3_clp3_p1_ambient_certificate.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def main() -> None:
    seed_packet = json.loads(SEED_PACKET.read_text(encoding="utf-8"))
    seed_payload = seed_packet["source_freeze_payload"]
    source_dimension = seed_payload["complete_seed_presentation"][
        "quotient_algebra"
    ]["complex_dimension"]

    payload = {
        "candidate_id": "P3-CLP3-P1-IAEC-v1",
        "upstream_seed_candidate_id": seed_payload["candidate_id"],
        "upstream_seed_fingerprint_sha256": seed_packet[
            "source_fingerprint_sha256"
        ],
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "theorem": {
            "name": "finite faithful-GNS ambient exhaustivity",
            "ambient_object": (
                "a finite-dimensional unital star algebra A_phys after an "
                "independently frozen physical-null quotient"
            ),
            "state": "a faithful state omega_phys on A_phys",
            "seed_subalgebra": "A_s=C*(R_s) included in A_phys",
            "criterion": (
                "closure(pi_omega(A_s) Omega_omega)=H_omega "
                "iff A_s=A_phys"
            ),
            "finite_rank_form": "rank(Vec_omega(A_s))=dim(A_phys)",
        },
        "required_independence": {
            "ambient_fixed_before_seed_candidate_comparison": True,
            "ambient_fixed_before_terminal_endpoint_inspection": True,
            "physical_null_quotient_fixed_source_first": True,
            "faithful_state_required": True,
            "all_occupied_central_components_included": True,
        },
        "finite_control_realization": {
            "source_dimension": source_dimension,
            "declared_ambient_dimension": source_dimension,
            "basis": "canonical regular-GNS coordinate basis",
            "ambient_derived_independently_of_seed_candidate": False,
            "reason_not_physical_certificate": (
                "the control ambient reuses the declared P3/CLP3 quotient "
                "dimension and therefore illustrates the theorem without "
                "independently establishing the physical ambient algebra"
            ),
        },
        "claim_boundary": {
            "conditional_P1_certificate_theorem": True,
            "current_P3_control_physically_eligible": False,
            "P1_physical_exhaustivity_proved": False,
            "nature_ambient_source_algebra_owned": False,
            "nature_occupation_proved": False,
            "physical_base_seed_packet_export_authorized": False,
        },
    }
    artifact = {
        "schema": "tau_core_p1_independent_ambient_certificate_v1",
        "source_freeze_payload": payload,
        "source_fingerprint_sha256": hashlib.sha256(
            canonical_bytes(payload)
        ).hexdigest(),
    }
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(
        "P3_CLP3_P1_AMBIENT_CERTIFICATE_FREEZE",
        artifact["source_fingerprint_sha256"],
    )


if __name__ == "__main__":
    main()
