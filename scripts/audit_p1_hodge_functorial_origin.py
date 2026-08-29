#!/usr/bin/env python3
"""Finite audit of DHF-P1 with cochain, metric and projector controls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_hodge_functorial_origin.json"
UPSTREAM = DERIVED / "p3_clp3_p1_spectral_priority_origin.json"
UPSTREAM_AUDIT = (
    DERIVED / "p3_clp3_p1_spectral_priority_origin_audit.json"
)
OUT = DERIVED / "p3_clp3_p1_hodge_functorial_origin_audit.json"
TOL = 1.0e-11


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def full_differential(rectangular_d: np.ndarray) -> np.ndarray:
    """Return q on H^0 direct-sum H^1 from d:H^0->H^1."""
    n1, n0 = rectangular_d.shape
    return np.block(
        [
            [np.zeros((n0, n0)), np.zeros((n0, n1))],
            [rectangular_d, np.zeros((n1, n1))],
        ]
    )


def hodge_packet(q: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    delta = q @ q.conj().T + q.conj().T @ q
    eigenvalues, eigenvectors = np.linalg.eigh(delta)
    harmonic = eigenvectors[:, np.abs(eigenvalues) < TOL]
    projector = harmonic @ harmonic.conj().T
    khat = delta + projector
    return delta, projector, khat


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    upstream_audit = json.loads(UPSTREAM_AUDIT.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]

    d0_rect = np.diag([2.0, 0.0])
    dx_rect = np.diag([2.0, 0.0, 3.0])
    q0 = full_differential(d0_rect)
    qx = full_differential(dx_rect)
    j_grade = np.vstack([np.eye(2), np.zeros((1, 2))])
    j = np.block(
        [
            [j_grade, np.zeros((3, 2))],
            [np.zeros((3, 2)), j_grade],
        ]
    )

    delta0, ph0, khat0 = hodge_packet(q0)
    deltax, phx, khatx = hodge_packet(qx)

    chain_defect = np.linalg.norm(qx @ j - j @ q0)
    cochain_defect = np.linalg.norm(qx.conj().T @ j - j @ q0.conj().T)
    laplacian_defect = np.linalg.norm(deltax @ j - j @ delta0)
    harmonic_defect = np.linalg.norm(phx @ j - j @ ph0)
    hodge_defect = np.linalg.norm(khatx @ j - j @ khat0)
    compression_defect = np.linalg.norm(j.conj().T @ khatx @ j - khat0)

    d_bad_rect = dx_rect.copy()
    d_bad_rect[0, 2] = 1.25
    q_bad = full_differential(d_bad_rect)
    delta_bad, ph_bad, khat_bad = hodge_packet(q_bad)
    bad_chain_defect = np.linalg.norm(q_bad @ j - j @ q0)
    bad_cochain_defect = np.linalg.norm(
        q_bad.conj().T @ j - j @ q0.conj().T
    )
    bad_hodge_defect = np.linalg.norm(khat_bad @ j - j @ khat0)
    bad_compression_defect = np.linalg.norm(
        j.conj().T @ khat_bad @ j - khat0
    )

    scaled_j = 1.7 * j
    scaled_intertwining_defect = np.linalg.norm(
        khatx @ scaled_j - scaled_j @ khat0
    )
    scaled_isometry_defect = np.linalg.norm(
        scaled_j.conj().T @ scaled_j - np.eye(4)
    )
    scaled_compression_defect = np.linalg.norm(
        scaled_j.conj().T @ khatx @ scaled_j - khat0
    )

    ph_independent = phx.copy()
    ph_independent[0, 0] = 1.0
    khat_independent = deltax + ph_independent
    independent_projector_defect = np.linalg.norm(
        ph_independent @ ph_independent - ph_independent
    )
    independent_harmonic_commutation_defect = np.linalg.norm(
        ph_independent @ j - j @ ph0
    )

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["upstream_packet_is_fingerprint_locked"] = (
        payload["upstream_spectral_priority_fingerprint_sha256"]
        == upstream["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["upstream_spectral_priority_audit_passes"] = (
        upstream_audit["passed"] == upstream_audit["total"] == 19
    )
    checks["source_differential_is_nilpotent"] = (
        np.linalg.norm(q0 @ q0) < TOL
    )
    checks["extension_differential_is_nilpotent"] = (
        np.linalg.norm(qx @ qx) < TOL
    )
    checks["embedding_is_isometric"] = (
        np.linalg.norm(j.conj().T @ j - np.eye(4)) < TOL
    )
    checks["differential_intertwines"] = chain_defect < TOL
    checks["codifferential_intertwines"] = cochain_defect < TOL
    checks["laplacian_intertwines"] = laplacian_defect < TOL
    checks["harmonic_projector_intertwines"] = harmonic_defect < TOL
    checks["hodge_operator_intertwines"] = hodge_defect < TOL
    checks["same_compression_is_derived"] = compression_defect < TOL
    checks["unstarred_cochain_control_preserves_d_only"] = (
        bad_chain_defect < TOL and bad_cochain_defect > 1.0
    )
    checks["unstarred_cochain_control_changes_hodge_operator"] = (
        bad_hodge_defect > 1.0 and bad_compression_defect > 1.0
    )
    checks["nonisometric_control_preserves_intertwining"] = (
        scaled_intertwining_defect < TOL
    )
    checks["nonisometric_control_breaks_compression_normalization"] = (
        scaled_isometry_defect > 1.0 and scaled_compression_defect > 1.0
    )
    checks["independent_harmonic_policy_is_not_derived"] = (
        independent_projector_defect < TOL
        and independent_harmonic_commutation_defect > 0.5
        and np.linalg.norm(khat_independent @ j - j @ khat0) > 0.5
    )
    checks["separate_hodge_axiom_is_removed_conditionally"] = (
        payload["conditional_consequence"][
            "separate_hodge_intertwining_axiom_needed"
        ]
        is False
        and payload["conditional_consequence"][
            "same_compression_then_follows"
        ]
        is True
    )
    checks["physical_star_differential_ownership_remains_open"] = (
        payload["claim_boundary"][
            "current_joint_role_record_grammar_contains_nonzero_odd_nilpotents"
        ]
        is True
        and payload["claim_boundary"][
            "current_joint_role_record_grammar_selects_complete_differential"
        ]
        is False
        and payload["claim_boundary"][
            "dhf_hodge_identified_with_frozen_p3_hodge"
        ]
        is False
        and payload["claim_boundary"][
            "physical_source_owns_complete_star_differential_grammar"
        ]
        is False
        and payload["claim_boundary"]["nature_occupation_proved"]
        is False
        and payload["claim_boundary"][
            "physical_base_seed_packet_export_authorized"
        ]
        is False
    )

    passed = sum(bool(value) for value in checks.values())
    audit = {
        "checks": {key: bool(value) for key, value in checks.items()},
        "passed": passed,
        "total": len(checks),
        "verdict": (
            "HODGE_INTERTWINING_DERIVED_FROM_DAGGER_FUNCTORIAL_GRAMMAR_"
            "PHYSICAL_GRAMMAR_OWNERSHIP_OPEN"
        ),
        "diagnostics": {
            "chain_defect": chain_defect,
            "codifferential_defect": cochain_defect,
            "laplacian_defect": laplacian_defect,
            "harmonic_projector_defect": harmonic_defect,
            "hodge_operator_defect": hodge_defect,
            "compression_defect": compression_defect,
            "bad_chain_defect": bad_chain_defect,
            "bad_codifferential_defect": bad_cochain_defect,
            "bad_hodge_operator_defect": bad_hodge_defect,
            "bad_compression_defect": bad_compression_defect,
            "scaled_isometry_defect": scaled_isometry_defect,
            "scaled_compression_defect": scaled_compression_defect,
        },
        "exact_remaining_source_datum": payload[
            "exact_remaining_source_datum"
        ],
        "physical_source_ownership": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"P1_HODGE_FUNCTORIAL_ORIGIN_AUDIT_FAIL {failed}")
    print(f"P1_HODGE_FUNCTORIAL_ORIGIN_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
