#!/usr/bin/env python3
"""Audit the operational copy law, selector, and incidence counterpair."""

from __future__ import annotations

import hashlib
import json
import math
from itertools import product
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_operational_record_origin.json"
UPSTREAM = DERIVED / "p3_clp3_p1_snpr_ownership_refinement.json"
OUT = DERIVED / "p3_clp3_p1_operational_record_origin_audit.json"
TOL = 1.0e-12


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def copy_matrix(m: int) -> np.ndarray:
    delta = np.zeros((m * m, m), dtype=float)
    for i in range(m):
        delta[i * m + i, i] = 1.0
    return delta


def swap_matrix(m: int) -> np.ndarray:
    swap = np.zeros((m * m, m * m), dtype=float)
    for i, j in product(range(m), repeat=2):
        swap[j * m + i, i * m + j] = 1.0
    return swap


def mutual_information(table: np.ndarray) -> float:
    row = table.sum(axis=1)
    col = table.sum(axis=0)
    return sum(
        table[i, j] * math.log(table[i, j] / (row[i] * col[j]))
        for i, j in product(range(table.shape[0]), range(table.shape[1]))
        if table[i, j] > 0.0
    )


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]
    boundary = payload["claim_boundary"]

    m = 2
    identity = np.eye(m)
    delta = copy_matrix(m)
    mu = delta.T
    swap = swap_matrix(m)
    epsilon = np.ones((1, m), dtype=float)

    coassoc_left = np.kron(delta, identity) @ delta
    coassoc_right = np.kron(identity, delta) @ delta
    frob_left = np.kron(mu, identity) @ np.kron(identity, delta)
    frob_middle = delta @ mu
    frob_right = np.kron(identity, mu) @ np.kron(delta, identity)

    primitive_unique = all(
        [
            word
            for word in product(range(m), repeat=ports)
            if all(symbol == logical for symbol in word)
        ]
        == [(logical,) * ports]
        for ports in range(2, 6)
        for logical in range(m)
    )

    spectrum = (0.25, 1.0, 2.25)
    z0 = sum(math.exp(-value) for value in spectrum)
    alternatives = tuple(payload["selector"]["logical_alternatives"])
    ports = tuple(payload["selector"]["physical_ports"])
    scores = {
        (logical, copies): math.log((logical**copies) * z0)
        for logical, copies in product(alternatives, ports)
    }
    selected = min(scores, key=scores.__getitem__)
    normalized = {
        (logical, copies): ((logical**copies) * z0) / (logical**copies)
        for logical, copies in product(alternatives, ports)
    }
    diagonal_only = {
        (logical, copies): logical * z0
        for logical, copies in product(alternatives, ports)
    }
    changed = {
        (logical, copies): (logical**copies) * math.exp(-logical * copies) * z0
        for logical, copies in product(alternatives, ports)
    }
    changed_selected = min(changed, key=changed.__getitem__)

    correlated = np.diag([0.5, 0.5])
    independent = np.full((2, 2), 0.25)
    same_marginals = np.allclose(
        correlated.sum(axis=0), independent.sum(axis=0), atol=TOL
    ) and np.allclose(
        correlated.sum(axis=1), independent.sum(axis=1), atol=TOL
    )
    mi_correlated = mutual_information(correlated)
    mi_independent = mutual_information(independent)

    checks = {
        "fingerprint_matches_payload": (
            hashlib.sha256(canonical_bytes(payload)).hexdigest()
            == packet["source_fingerprint_sha256"]
        ),
        "upstream_ownership_refinement_is_fingerprint_locked": (
            payload["upstream_ownership_refinement_fingerprint_sha256"]
            == upstream["source_fingerprint_sha256"]
        ),
        "freeze_is_endpoint_blind": (
            payload["terminal_data_used"] is False
            and payload["endpoint_fitted_parameters"] == []
        ),
        "primitive_exact_recovery_forces_diagonal_copy": primitive_unique,
        "copy_is_isometric": np.allclose(delta.T @ delta, identity, atol=TOL),
        "copy_is_cocommutative": np.allclose(swap @ delta, delta, atol=TOL),
        "copy_is_coassociative": np.allclose(
            coassoc_left, coassoc_right, atol=TOL
        ),
        "copy_is_special": np.allclose(mu @ delta, identity, atol=TOL),
        "frobenius_left_identity": np.allclose(
            frob_left, frob_middle, atol=TOL
        ),
        "frobenius_right_identity": np.allclose(
            frob_right, frob_middle, atol=TOL
        ),
        "left_counit_identity": np.allclose(
            np.kron(epsilon, identity) @ delta, identity, atol=TOL
        ),
        "right_counit_identity": np.allclose(
            np.kron(identity, epsilon) @ delta, identity, atol=TOL
        ),
        "full_carrier_priority_selects_m2_k2": selected == (2, 2),
        "fixed_nontrivial_alphabet_selects_two_ports": all(
            min(ports, key=lambda copies: copies * math.log(logical)) == 2
            for logical in alternatives
        ),
        "allowing_one_port_selects_k1": min(
            range(1, 6), key=lambda copies: copies * math.log(2)
        )
        == 1,
        "normalized_trace_erases_selector": (
            max(normalized.values()) - min(normalized.values()) < TOL
        ),
        "diagonal_only_score_is_port_blind": all(
            len({diagonal_only[(logical, copies)] for copies in ports}) == 1
            for logical in alternatives
        ),
        "changed_compression_can_change_selected_pair": changed_selected
        != (2, 2),
        "same_marginals_do_not_fix_common_incidence": (
            same_marginals and mi_correlated > TOL and abs(mi_independent) < TOL
        ),
        "copy_law_is_claimed_only_inside_operational_class": (
            boundary["copy_law_derived_inside_operational_class"] is True
            and boundary["operational_class_physically_owned"] is False
        ),
        "common_incidence_and_Nature_claims_remain_false": (
            boundary["common_PUSC_record_incidence_derived"] is False
            and boundary["nature_occupation"] is False
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    audit = {
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "verdict": (
            "OPERATIONAL_COPY_LAW_PROVED_AND_M2_K2_SELECTED_CONDITIONALLY;_"
            "COMMON_PUSC_RECORD_INCIDENCE_OPEN"
        ),
        "diagnostics": {
            "selected_pair": list(selected),
            "changed_compression_selected_pair": list(changed_selected),
            "correlated_mutual_information_nats": mi_correlated,
            "independent_mutual_information_nats": mi_independent,
        },
        "physical_operational_class_ownership": "OPEN",
        "physical_PUSC_record_incidence": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if audit["passed"] != audit["total"]:
        failed = [name for name, value in checks.items() if not value]
        raise SystemExit(f"P1_OPERATIONAL_RECORD_ORIGIN_AUDIT_FAIL {failed}")
    print(
        "P1_OPERATIONAL_RECORD_ORIGIN_AUDIT_PASS "
        f"{audit['passed']}/{audit['total']}"
    )


if __name__ == "__main__":
    main()
