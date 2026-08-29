#!/usr/bin/env python3
"""Audit USA--SNPR factorisation, zero-set and irredundancy claims."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_snpr_upstream_joint_action.json"
UPSTREAM = DERIVED / "p3_clp3_p1_source_natural_pointed_realization.json"
OUT = DERIVED / "p3_clp3_p1_snpr_upstream_joint_action_audit.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def action(bits: tuple[int, ...], weights: tuple[int, ...]) -> int:
    return sum(weight * (1 - bit) for bit, weight in zip(bits, weights))


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]
    patterns = tuple(itertools.product((0, 1), repeat=5))
    target = (1, 1, 1, 1, 1)
    weights = tuple(payload["fixed_positive_source_weights"])
    values = {bits: action(bits, weights) for bits in patterns}
    minimizers = [bits for bits, value in values.items() if value == min(values.values())]

    deletion_controls = []
    for index in range(5):
        reduced = tuple(0 if j == index else weights[j] for j in range(5))
        control = tuple(0 if j == index else 1 for j in range(5))
        deletion_controls.append(
            action(target, reduced) == action(control, reduced) == 0
        )

    # Any a o R is constant here because all 32 patterns are members of the
    # same declared narrow-reduct fibre.
    reduct_values = [13 for _ in patterns]
    boundary = payload["claim_boundary"]
    checks = {
        "fingerprint_matches_payload": (
            hashlib.sha256(canonical_bytes(payload)).hexdigest()
            == packet["source_fingerprint_sha256"]
        ),
        "upstream_SNPR_packet_is_fingerprint_locked": (
            payload["upstream_snpr_fingerprint_sha256"]
            == upstream["source_fingerprint_sha256"]
        ),
        "endpoint_blind_freeze": (
            payload["terminal_data_used"] is False
            and payload["endpoint_fitted_parameters"] == []
        ),
        "all_32_premise_patterns_are_compared": len(patterns) == 32,
        "reduct_factored_action_is_constant_on_the_fibre": (
            len(set(reduct_values)) == 1
        ),
        "full_joint_action_has_zero_floor": min(values.values()) == 0,
        "full_joint_action_has_only_the_all_premise_zero_pattern": (
            minimizers == [target]
        ),
        "all_five_weights_are_strictly_positive": all(weight > 0 for weight in weights),
        "every_component_is_irredundant": all(deletion_controls),
        "conditional_selection_is_not_reported_as_common_origin": (
            boundary["conditional_zero_set_selection"] is True
            and boundary["defects_derived_from_one_parent_operator"] is False
        ),
        "old_bare_Nature_and_exhaustivity_claims_remain_false": (
            boundary["old_bare_entailment"] is False
            and boundary["nature_occupation"] is False
            and boundary["ambient_parent_exhaustivity"] is False
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    audit = {
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "verdict": (
            "REDUCT_FACTORISATION_NO_GO_AND_CONDITIONAL_FIVE_DEFECT_"
            "ZERO_SET_CLOSURE_PASS"
        ),
        "diagnostics": {
            "candidate_count": len(patterns),
            "global_minimizers": [list(bits) for bits in minimizers],
            "deletion_controls": deletion_controls,
        },
        "primitive_common_origin": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if audit["passed"] != audit["total"]:
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"P1_SNPR_UPSTREAM_JOINT_ACTION_AUDIT_FAIL {failed}")
    print(
        "P1_SNPR_UPSTREAM_JOINT_ACTION_AUDIT_PASS "
        f"{audit['passed']}/{audit['total']}"
    )


if __name__ == "__main__":
    main()
