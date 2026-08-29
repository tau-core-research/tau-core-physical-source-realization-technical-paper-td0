#!/usr/bin/env python3
"""Finite audit of the conditional seed-Boolean-to-CAR7 refinement."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_seed_boolean_car_bridge.json"
UPSTREAM = DERIVED / "p3_clp3_p1_role_record_hodge_ownership.json"
P3 = DERIVED / "p3_clp3_complete_seed_presentation.json"
OUT = DERIVED / "p3_clp3_p1_seed_boolean_car_bridge_audit.json"
TOL = 1.0e-10


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def fermion_operators(n_modes: int) -> tuple[list[np.ndarray], list[np.ndarray]]:
    dim = 1 << n_modes
    creators: list[np.ndarray] = []
    annihilators: list[np.ndarray] = []
    for mode in range(n_modes):
        creation = np.zeros((dim, dim), dtype=complex)
        lower_mask = (1 << mode) - 1
        for state in range(dim):
            if state & (1 << mode):
                continue
            parity = bin(state & lower_mask).count("1") % 2
            creation[state | (1 << mode), state] = -1.0 if parity else 1.0
        creators.append(creation)
        annihilators.append(creation.conj().T)
    return creators, annihilators


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    p3 = json.loads(P3.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]

    n_modes = 7
    dim = 1 << n_modes
    creators, annihilators = fermion_operators(n_modes)
    identity = np.eye(dim, dtype=complex)
    zero = np.zeros_like(identity)

    creation_defect = max(
        np.linalg.norm(creators[a] @ creators[b] + creators[b] @ creators[a])
        for a in range(n_modes)
        for b in range(n_modes)
    )
    annihilation_defect = max(
        np.linalg.norm(
            annihilators[a] @ annihilators[b]
            + annihilators[b] @ annihilators[a]
        )
        for a in range(n_modes)
        for b in range(n_modes)
    )
    mixed_defect = max(
        np.linalg.norm(
            annihilators[a] @ creators[b]
            + creators[b] @ annihilators[a]
            - (identity if a == b else zero)
        )
        for a in range(n_modes)
        for b in range(n_modes)
    )

    boundary = sum(annihilators, start=np.zeros_like(identity))
    coboundary = boundary.conj().T
    boundary_square_defect = np.linalg.norm(boundary @ boundary)
    boundary_laplacian = boundary @ coboundary + coboundary @ boundary
    boundary_laplacian_defect = np.linalg.norm(
        boundary_laplacian - n_modes * identity
    )
    number = sum(
        (creator @ annihilator for creator, annihilator in zip(creators, annihilators)),
        start=np.zeros_like(identity),
    )
    number_spectrum = np.linalg.eigvalsh(number)
    expected_degree_spectrum = np.array(
        [bin(state).count("1") for state in range(dim)], dtype=float
    )

    ones = np.ones(n_modes, dtype=float)
    u = ones / np.linalg.norm(ones)
    v1 = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0]) / np.sqrt(2.0)
    v2 = np.array([1.0, 1.0, -2.0, 0.0, 0.0, 0.0, 0.0]) / np.sqrt(6.0)
    theta = 0.731
    rotation = (
        np.eye(n_modes)
        + (np.cos(theta) - 1.0) * (np.outer(v1, v1) + np.outer(v2, v2))
        + np.sin(theta) * (np.outer(v2, v1) - np.outer(v1, v2))
    )
    rotated_annihilators = [
        sum(
            (rotation[a, b] * annihilators[b] for b in range(n_modes)),
            start=np.zeros_like(identity),
        )
        for a in range(n_modes)
    ]
    rotated_creators = [op.conj().T for op in rotated_annihilators]
    rotated_boundary = sum(rotated_annihilators, start=np.zeros_like(identity))
    rotated_number = sum(
        (
            creator @ annihilator
            for creator, annihilator in zip(
                rotated_creators, rotated_annihilators
            )
        ),
        start=np.zeros_like(identity),
    )
    rotated_mixed_defect = max(
        np.linalg.norm(
            rotated_annihilators[a] @ rotated_creators[b]
            + rotated_creators[b] @ rotated_annihilators[a]
            - (identity if a == b else zero)
        )
        for a in range(n_modes)
        for b in range(n_modes)
    )
    mode_change_norm = max(
        np.linalg.norm(rotated_annihilators[a] - annihilators[a])
        for a in range(n_modes)
    )

    missing_face = (1 << 0) | (1 << 1)
    face_projector = identity.copy()
    face_projector[missing_face, missing_face] = 0.0
    compressed_creators = [
        face_projector @ op @ face_projector for op in creators
    ]
    compressed_annihilators = [op.conj().T for op in compressed_creators]
    compressed_mixed_defect = max(
        np.linalg.norm(
            compressed_annihilators[a] @ compressed_creators[b]
            + compressed_creators[b] @ compressed_annihilators[a]
            - (face_projector if a == b else zero)
        )
        for a in range(n_modes)
        for b in range(n_modes)
    )

    vacuum = np.zeros(dim, dtype=complex)
    vacuum[0] = 1.0
    orbit = []
    for subset in range(dim):
        state = vacuum.copy()
        for mode in range(n_modes):
            if subset & (1 << mode):
                state = creators[mode] @ state
        orbit.append(state)
    orbit_matrix = np.column_stack(orbit)
    orbit_rank = int(np.linalg.matrix_rank(orbit_matrix, tol=TOL))
    orbit_gram_defect = np.linalg.norm(
        orbit_matrix.conj().T @ orbit_matrix - identity
    )

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["upstream_role_record_hodge_packet_is_locked"] = (
        payload["upstream_role_record_hodge_fingerprint_sha256"]
        == upstream["source_fingerprint_sha256"]
    )
    checks["upstream_p3_packet_is_locked"] = (
        payload["upstream_p3_fingerprint_sha256"]
        == p3["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["complete_boolean_car_creation_relations_hold"] = creation_defect < TOL
    checks["complete_boolean_car_annihilation_relations_hold"] = (
        annihilation_defect < TOL
    )
    checks["complete_boolean_car_mixed_relations_hold"] = mixed_defect < TOL
    checks["global_boundary_is_nilpotent"] = boundary_square_defect < TOL
    checks["global_boundary_laplacian_is_seven_identity"] = (
        boundary_laplacian_defect < TOL
    )
    checks["number_operator_has_exact_exterior_degree_spectrum"] = np.allclose(
        np.sort(number_spectrum), np.sort(expected_degree_spectrum)
    )
    checks["empty_root_generates_all_boolean_words"] = orbit_rank == dim
    checks["empty_root_orbit_is_orthonormal"] = orbit_gram_defect < TOL
    checks["binary_record_doubles_carrier_to_256"] = 2 * orbit_rank == 256
    checks["rotation_is_nontrivial_orthogonal_and_fixes_boundary_direction"] = (
        np.linalg.norm(rotation.T @ rotation - np.eye(n_modes)) < TOL
        and np.linalg.norm(rotation @ u - u) < TOL
        and np.linalg.norm(rotation - np.eye(n_modes)) > 0.1
    )
    checks["rotated_modes_still_obey_car"] = rotated_mixed_defect < TOL
    checks["rotated_modes_are_distinct"] = mode_change_norm > 0.1
    checks["global_boundary_does_not_select_colored_modes"] = (
        np.linalg.norm(rotated_boundary - boundary) < TOL
    )
    checks["number_operator_does_not_select_colored_modes"] = (
        np.linalg.norm(rotated_number - number) < TOL
    )
    checks["one_missing_boolean_face_breaks_car"] = compressed_mixed_defect > 0.5
    checks["current_physical_source_ownership_remains_open"] = (
        payload["claim_boundary"][
            "current_physical_seed_owns_complete_typed_boolean_closure"
        ]
        is False
        and payload["claim_boundary"]["nature_occupation_proved"] is False
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
            "COMPLETE_TYPED_BOOLEAN_SEED_CONDITIONALLY_DERIVES_CAR7_"
            "GLOBAL_BOUNDARY_ALONE_DOES_NOT_SELECT_TYPED_MODES"
        ),
        "diagnostics": {
            "boolean_word_count": dim,
            "exterior_record_dimension": 2 * dim,
            "creation_car_defect": float(creation_defect),
            "annihilation_car_defect": float(annihilation_defect),
            "mixed_car_defect": float(mixed_defect),
            "boundary_square_defect": float(boundary_square_defect),
            "boundary_laplacian_seven_identity_defect": float(
                boundary_laplacian_defect
            ),
            "rotated_boundary_defect": float(
                np.linalg.norm(rotated_boundary - boundary)
            ),
            "rotated_number_defect": float(np.linalg.norm(rotated_number - number)),
            "rotated_mode_change_norm": float(mode_change_norm),
            "missing_face_car_defect": float(compressed_mixed_defect),
            "empty_root_orbit_rank": orbit_rank,
            "empty_root_orbit_gram_defect": float(orbit_gram_defect),
            "unresolved_colored_frame_gauge": "O(6) fixing the global boundary line",
        },
        "exact_remaining_source_datum": payload["exact_remaining_source_datum"],
        "physical_source_ownership": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"P1_SEED_BOOLEAN_CAR_BRIDGE_AUDIT_FAIL {failed}")
    print(f"P1_SEED_BOOLEAN_CAR_BRIDGE_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
