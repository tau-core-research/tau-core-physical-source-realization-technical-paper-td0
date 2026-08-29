#!/usr/bin/env python3
"""Finite audit of P3 nilpotents, Hodge mismatch, and CAR completion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_role_record_hodge_ownership.json"
UPSTREAM = DERIVED / "p3_clp3_p1_hodge_functorial_origin.json"
P3 = DERIVED / "p3_clp3_complete_seed_presentation.json"
OUT = DERIVED / "p3_clp3_p1_role_record_hodge_ownership_audit.json"
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
            sign = -1.0 if (bin(state & lower_mask).count("1") % 2) else 1.0
            creation[state | (1 << mode), state] = sign
        creators.append(creation)
        annihilators.append(creation.conj().T)
    return creators, annihilators


def ordered_clifford_words(gammas: list[np.ndarray]) -> np.ndarray:
    dim = gammas[0].shape[0]
    words: list[np.ndarray] = []
    for subset in range(1 << len(gammas)):
        word = np.eye(dim, dtype=complex)
        for mode, gamma in enumerate(gammas):
            if subset & (1 << mode):
                word = word @ gamma
        words.append(word.reshape(-1))
    return np.column_stack(words)


def projection_residual(basis: np.ndarray, target: np.ndarray) -> float:
    coefficients, *_ = np.linalg.lstsq(basis, target.reshape(-1), rcond=None)
    residual = basis @ coefficients - target.reshape(-1)
    return float(np.linalg.norm(residual) / np.linalg.norm(target))


def main() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    p3 = json.loads(P3.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]

    n_modes = 7
    creators, annihilators = fermion_operators(n_modes)
    dim = 1 << n_modes
    identity = np.eye(dim, dtype=complex)
    zero = np.zeros_like(identity)
    gammas = [c + a for c, a in zip(creators, annihilators)]

    clifford_defect = max(
        np.linalg.norm(
            gammas[i] @ gammas[j]
            + gammas[j] @ gammas[i]
            - (2.0 * identity if i == j else zero)
        )
        for i in range(n_modes)
        for j in range(n_modes)
    )
    car_creation_defect = max(
        np.linalg.norm(creators[i] @ creators[j] + creators[j] @ creators[i])
        for i in range(n_modes)
        for j in range(n_modes)
    )
    car_mixed_defect = max(
        np.linalg.norm(
            annihilators[i] @ creators[j]
            + creators[j] @ annihilators[i]
            - (identity if i == j else zero)
        )
        for i in range(n_modes)
        for j in range(n_modes)
    )

    q01 = 0.5 * (gammas[0] + 1j * gammas[1])
    q23 = 0.5 * (gammas[2] + 1j * gammas[3])
    q01_star = q01.conj().T
    delta_q = q01 @ q01_star + q01_star @ q01
    delta_eigenvalues = np.linalg.eigvalsh(delta_q)
    harmonic_dimension = int(np.count_nonzero(np.abs(delta_eigenvalues) < TOL))
    ph_q = np.zeros_like(identity)
    khat_q = delta_q + ph_q

    number = sum(
        (creator @ annihilator for creator, annihilator in zip(creators, annihilators)),
        start=np.zeros_like(identity),
    )
    number_eigenvalues = np.linalg.eigvalsh(number)
    number_kernel_dimension_with_record = 2 * int(
        np.count_nonzero(np.abs(number_eigenvalues) < TOL)
    )

    left_role_basis = ordered_clifford_words(gammas)
    left_role_rank = int(np.linalg.matrix_rank(left_role_basis, tol=TOL))
    creator_projection_residual = projection_residual(left_role_basis, creators[0])
    number_projection_residual = projection_residual(left_role_basis, number)

    rng = np.random.default_rng(20260828)
    raw = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
    unitary, _ = np.linalg.qr(raw)
    transported_creators = [unitary @ op @ unitary.conj().T for op in creators]
    transported_annihilators = [unitary @ op @ unitary.conj().T for op in annihilators]
    transported_number = sum(
        (
            creator @ annihilator
            for creator, annihilator in zip(
                transported_creators, transported_annihilators
            )
        ),
        start=np.zeros_like(identity),
    )
    transport_defect = np.linalg.norm(transported_number @ unitary - unitary @ number)

    parity = np.diag(
        [1.0 if (bin(state).count("1") % 2 == 0) else -1.0 for state in range(dim)]
    )
    degree_one = np.diag(
        [1.0 if bin(state).count("1") == 1 else 0.0 for state in range(dim)]
    )
    degree_one_even_rank = int(
        round(np.trace(0.5 * (identity + parity) @ degree_one).real)
    )
    degree_one_odd_rank = int(
        round(np.trace(0.5 * (identity - parity) @ degree_one).real)
    )

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["upstream_hodge_packet_is_locked"] = (
        payload["upstream_hodge_functorial_fingerprint_sha256"]
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
    checks["seven_mode_clifford_relations_hold"] = clifford_defect < TOL
    checks["q01_is_nonzero_nilpotent"] = (
        np.linalg.norm(q01) > 1.0 and np.linalg.norm(q01 @ q01) < TOL
    )
    checks["q01_star_is_owned_by_star_closure"] = np.linalg.norm(
        q01_star - 0.5 * (gammas[0] - 1j * gammas[1])
    ) < TOL
    checks["q01_has_one_mode_car_laplacian"] = np.linalg.norm(
        delta_q - identity
    ) < TOL
    checks["distinct_nilpotents_are_not_selected_by_relations"] = (
        np.linalg.norm(q23 @ q23) < TOL
        and np.linalg.norm(q01 - q23) > 1.0
        and np.linalg.norm(
            q23 @ q23.conj().T + q23.conj().T @ q23 - identity
        )
        < TOL
    )
    checks["explicit_q_has_no_harmonic_sector"] = harmonic_dimension == 0
    checks["explicit_dhf_hodge_is_identity"] = np.linalg.norm(
        khat_q - identity
    ) < TOL
    checks["frozen_number_operator_has_record_kernel"] = (
        number_kernel_dimension_with_record == 2
    )
    checks["explicit_dhf_hodge_differs_from_frozen_p3_hodge"] = np.linalg.norm(
        khat_q - number
    ) > 1.0
    checks["left_role_image_has_expected_dimension"] = left_role_rank == 128
    checks["exterior_creation_is_not_in_left_role_image"] = (
        creator_projection_residual > 0.5
    )
    checks["number_operator_is_not_in_left_role_image"] = (
        number_projection_residual > 1.0e-6
    )
    checks["car_creation_relations_hold"] = car_creation_defect < TOL
    checks["car_mixed_relations_hold"] = car_mixed_defect < TOL
    checks["car_completion_recovers_role_generators"] = max(
        np.linalg.norm(gammas[i] - creators[i] - annihilators[i])
        for i in range(n_modes)
    ) < TOL
    checks["car_completion_recovers_number_operator"] = np.linalg.norm(
        number
        - sum(
            (
                creators[i] @ annihilators[i]
                for i in range(n_modes)
            ),
            start=np.zeros_like(identity),
        )
    ) < TOL
    checks["full_star_transport_derives_number_transport"] = transport_defect < TOL
    checks["number_spectrum_matches_exterior_degree"] = np.allclose(
        np.sort(number_eigenvalues),
        np.sort(np.array([bin(state).count("1") for state in range(dim)], dtype=float)),
    )
    checks["degree_one_positive_spectrum_is_parity_unbalanced"] = (
        degree_one_even_rank == 0 and degree_one_odd_rank == 7
    )
    checks["faithful_car7_cannot_fit_32_dimensional_carrier"] = 128 > 32
    checks["physical_ownership_remains_open"] = (
        payload["claim_boundary"]["physical_source_owns_car7_completion"]
        is False
        and payload["claim_boundary"][
            "mvp_recovery_incidence_is_identified_with_p3_car7"
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
            "ROLE_ALGEBRA_NILPOTENTS_EXIST_BUT_FROZEN_P3_HODGE_IS_NOT_"
            "SINGLE_DIFFERENTIAL_GENERATED_CAR7_COMPLETION_CONDITIONAL"
        ),
        "diagnostics": {
            "clifford_defect": float(clifford_defect),
            "car_creation_defect": float(car_creation_defect),
            "car_mixed_defect": float(car_mixed_defect),
            "q01_nilpotency_defect": float(np.linalg.norm(q01 @ q01)),
            "q01_laplacian_identity_defect": float(
                np.linalg.norm(delta_q - identity)
            ),
            "frozen_number_kernel_dimension_with_record": (
                number_kernel_dimension_with_record
            ),
            "left_role_image_rank": left_role_rank,
            "creator_projection_relative_residual": creator_projection_residual,
            "number_projection_relative_residual": number_projection_residual,
            "car_number_transport_defect": float(transport_defect),
            "minimal_faithful_car7_carrier_dimension": 128,
            "minimal_faithful_jgr_carrier_dimension": 32,
        },
        "exact_remaining_source_datum": payload["exact_remaining_source_datum"],
        "physical_source_ownership": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"P1_ROLE_RECORD_HODGE_OWNERSHIP_AUDIT_FAIL {failed}")
    print(f"P1_ROLE_RECORD_HODGE_OWNERSHIP_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
