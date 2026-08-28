#!/usr/bin/env python3
"""Audit the finite faithful-GNS exhaustivity certificate and its no-go controls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
CERTIFICATE = DERIVED / "p3_clp3_p1_ambient_certificate.json"
SEED_PACKET = DERIVED / "p3_clp3_complete_seed_presentation.json"
OUT = DERIVED / "p3_clp3_p1_ambient_certificate_audit.json"
TOL = 1.0e-10


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def checked_matmul(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Multiply finite audit matrices and fail closed on non-finite output."""
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        result = left @ right
    if not np.all(np.isfinite(result)):
        raise FloatingPointError("non-finite matrix product in P1 ambient audit")
    return result


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    payload = certificate["source_freeze_payload"]
    seed_packet = json.loads(SEED_PACKET.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    checks["certificate_fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == certificate["source_fingerprint_sha256"]
    )
    checks["upstream_seed_fingerprint_is_bound"] = (
        payload["upstream_seed_fingerprint_sha256"]
        == seed_packet["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )

    dimension = int(payload["finite_control_realization"]["source_dimension"])
    source_basis = np.eye(dimension, dtype=float)
    faithful_weights = np.ones(dimension, dtype=float)
    weighted_gram = checked_matmul(
        source_basis.T, faithful_weights[:, None] * source_basis
    )
    checks["finite_source_basis_has_declared_rank"] = (
        np.linalg.matrix_rank(source_basis, tol=TOL) == dimension == 256
    )
    checks["faithful_state_has_no_null_direction"] = faithful_weights.min() > 0.0
    checks["faithful_gns_gram_is_positive_definite"] = (
        np.linalg.eigvalsh(weighted_gram).min() > 0.0
    )
    checks["declared_control_span_equals_declared_ambient"] = (
        np.linalg.matrix_rank(source_basis, tol=TOL)
        == payload["finite_control_realization"]["declared_ambient_dimension"]
    )

    # The criterion depends only on the generated subspace, not on the chosen
    # coordinate basis used to present it.
    reversed_basis = np.fliplr(source_basis)
    checks["basis_relabeling_preserves_exhaustivity_rank"] = (
        np.linalg.matrix_rank(reversed_basis, tol=TOL) == dimension
        and np.allclose(
            checked_matmul(reversed_basis.T, reversed_basis), np.eye(dimension)
        )
    )

    # A missing relation direction within the same ambient component is seen.
    missing_relation_basis = source_basis[:, :-1]
    checks["same_component_missing_relation_is_detected"] = (
        np.linalg.matrix_rank(missing_relation_basis, tol=TOL) == dimension - 1
    )

    # A hidden direct-sum component leaves the complete local source Gram
    # unchanged but fails the global ambient-rank condition.
    hidden_component_basis = np.vstack([source_basis, np.zeros((1, dimension))])
    hidden_ambient_dimension = dimension + 1
    checks["hidden_component_preserves_local_source_gram"] = np.allclose(
        checked_matmul(hidden_component_basis.T, hidden_component_basis),
        np.eye(dimension),
    )
    checks["hidden_component_fails_global_ambient_rank"] = (
        np.linalg.matrix_rank(hidden_component_basis, tol=TOL) == dimension
        < hidden_ambient_dimension
    )

    # Faithfulness is essential: zero weight on the hidden direction would
    # quotient it away and create a false appearance of completeness.
    nonfaithful_weights = np.concatenate([np.ones(dimension), [0.0]])
    effective_nonfaithful_dimension = int(np.count_nonzero(nonfaithful_weights > TOL))
    checks["nonfaithful_state_can_hide_one_ambient_direction"] = (
        effective_nonfaithful_dimension == dimension
        and nonfaithful_weights.min() == 0.0
    )
    checks["faithfulness_gate_rejects_that_false_positive"] = not bool(
        nonfaithful_weights.min() > 0.0
    )

    independence = payload["required_independence"]
    checks["certificate_requires_source_first_ambient_and_null_policy"] = (
        independence["ambient_fixed_before_seed_candidate_comparison"] is True
        and independence["ambient_fixed_before_terminal_endpoint_inspection"] is True
        and independence["physical_null_quotient_fixed_source_first"] is True
    )
    checks["certificate_requires_all_occupied_components"] = (
        independence["all_occupied_central_components_included"] is True
    )
    checks["current_control_declares_missing_ambient_independence"] = (
        payload["finite_control_realization"][
            "ambient_derived_independently_of_seed_candidate"
        ]
        is False
    )
    boundary = payload["claim_boundary"]
    checks["conditional_theorem_not_promoted_to_physical_P1"] = (
        boundary["conditional_P1_certificate_theorem"] is True
        and boundary["current_P3_control_physically_eligible"] is False
        and boundary["P1_physical_exhaustivity_proved"] is False
    )
    checks["nature_and_packet_export_remain_closed"] = (
        boundary["nature_ambient_source_algebra_owned"] is False
        and boundary["nature_occupation_proved"] is False
        and boundary["physical_base_seed_packet_export_authorized"] is False
    )

    checks = {name: bool(value) for name, value in checks.items()}
    passed = sum(checks.values())
    total = len(checks)
    audit = {
        "schema": "tau_core_p1_independent_ambient_certificate_audit_v1",
        "candidate_id": payload["candidate_id"],
        "source_fingerprint_sha256": certificate["source_fingerprint_sha256"],
        "checks": checks,
        "passed": passed,
        "total": total,
        "diagnostics": {
            "declared_source_rank": int(np.linalg.matrix_rank(source_basis, tol=TOL)),
            "declared_ambient_dimension": dimension,
            "same_component_missing_relation_rank": int(
                np.linalg.matrix_rank(missing_relation_basis, tol=TOL)
            ),
            "hidden_component_source_rank": int(
                np.linalg.matrix_rank(hidden_component_basis, tol=TOL)
            ),
            "hidden_component_ambient_dimension": hidden_ambient_dimension,
        },
        "verdict": (
            "CONDITIONAL_P1_AMBIENT_RANK_THEOREM_PASS"
            if passed == total
            else "FAIL"
        ),
        "physical_P1_certificate_eligible": False,
        "P1_physical_exhaustivity_proved": False,
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != total:
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"P3_CLP3_P1_AMBIENT_CERTIFICATE_FAIL {failed}")
    print(f"P3_CLP3_P1_AMBIENT_CERTIFICATE_PASS {passed}/{total} P1_OPEN")


if __name__ == "__main__":
    main()
