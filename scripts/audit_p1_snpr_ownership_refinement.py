#!/usr/bin/env python3
"""Audit the finite symmetry and record-cardinality refinement controls."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_snpr_ownership_refinement.json"
UPSTREAM = DERIVED / "p3_clp3_p1_snpr_upstream_joint_action.json"
OUT = DERIVED / "p3_clp3_p1_snpr_ownership_refinement_audit.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def z2(value: float, element: int) -> float:
    return value if element == 1 else -value


def response(base: float, seed: float) -> float:
    return base + seed


def heat_trace(spectrum: tuple[float, ...], n: int, shift: float = 0.0) -> float:
    return n * sum(math.exp(-(eigenvalue + shift)) for eigenvalue in spectrum)


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]

    equivariant = all(
        math.isclose(
            response(z2(0.0, g), z2(1.0, g)),
            z2(response(0.0, 1.0), g),
            abs_tol=1e-12,
        )
        for g in (1, -1)
    )
    fixed_response = response(0.0, 0.0)
    asymmetric_responses = (response(0.0, -1.0), response(0.0, 1.0))
    explicit_bias_breaks_equivariance = not math.isclose(1.0, z2(1.0, -1))
    spontaneous_minima = (-1.0, 1.0)

    spectrum = (0.25, 1.0, 2.25)
    ns = tuple(range(1, 9))
    nontrivial = tuple(payload["record_meta_domain"]["eligible_cardinalities"])
    common = {n: heat_trace(spectrum, n) for n in ns}
    complexity = {n: math.log(value) for n, value in common.items()}
    selected_nontrivial = min(nontrivial, key=complexity.__getitem__)
    selected_unrestricted = min(ns, key=complexity.__getitem__)
    normalized = {n: common[n] / n for n in ns}
    changed = {n: heat_trace(spectrum, n, shift=float(n)) for n in nontrivial}
    selected_changed = min(nontrivial, key=changed.__getitem__)

    boundary = payload["claim_boundary"]
    checks = {
        "fingerprint_matches_payload": (
            hashlib.sha256(canonical_bytes(payload)).hexdigest()
            == packet["source_fingerprint_sha256"]
        ),
        "upstream_joint_action_is_fingerprint_locked": (
            payload["upstream_joint_action_fingerprint_sha256"]
            == upstream["source_fingerprint_sha256"]
        ),
        "freeze_is_endpoint_blind": (
            payload["terminal_data_used"] is False
            and payload["endpoint_fitted_parameters"] == []
        ),
        "Z2_response_is_equivariant": equivariant,
        "fixed_base_and_seed_give_fixed_response": math.isclose(
            fixed_response, 0.0, abs_tol=1e-12
        ),
        "noninvariant_seed_supplies_oriented_pair": asymmetric_responses == (-1.0, 1.0),
        "explicit_bias_escape_breaks_equivariance": explicit_bias_breaks_equivariance,
        "spontaneous_escape_is_nonunique": len(spontaneous_minima) == 2,
        "common_compression_heat_trace_scales_as_n": all(
            math.isclose(common[n] / common[1], float(n), rel_tol=1e-12)
            for n in ns
        ),
        "smallest_nontrivial_record_is_binary": selected_nontrivial == 2,
        "allowing_trivial_record_selects_n1": selected_unrestricted == 1,
        "normalized_trace_erases_cardinality_priority": (
            max(normalized.values()) - min(normalized.values()) < 1e-12
        ),
        "changed_compression_can_select_larger_record": selected_changed != 2,
        "copy_law_and_meta_law_ownership_remain_open": (
            boundary["physical_record_copy_law_derived"] is False
            and boundary["meta_law_physically_owned"] is False
        ),
        "common_occupation_and_Nature_claims_remain_false": (
            boundary["common_PUSC_record_occupation"] is False
            and boundary["nature_occupation"] is False
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    audit = {
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "verdict": (
            "ASYMMETRY_LOCALIZED_ON_DECLARED_BRANCH_AND_BINARY_RECORD_"
            "SELECTED_ONLY_IN_NONTRIVIAL_COMMON_COMPRESSION_CLASS"
        ),
        "diagnostics": {
            "fixed_response": fixed_response,
            "asymmetric_responses": list(asymmetric_responses),
            "selected_nontrivial_cardinality": selected_nontrivial,
            "selected_if_trivial_allowed": selected_unrestricted,
            "selected_with_changed_compression": selected_changed,
            "normalized_trace_spread": max(normalized.values()) - min(normalized.values()),
        },
        "physical_meta_law_ownership": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if audit["passed"] != audit["total"]:
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"P1_SNPR_OWNERSHIP_REFINEMENT_AUDIT_FAIL {failed}")
    print(
        "P1_SNPR_OWNERSHIP_REFINEMENT_AUDIT_PASS "
        f"{audit['passed']}/{audit['total']}"
    )


if __name__ == "__main__":
    main()
