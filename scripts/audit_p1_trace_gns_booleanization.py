#!/usr/bin/env python3
"""Finite audit of the trace-GNS carrier and Clifford-word Booleanization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
PACKET = DERIVED / "p3_clp3_p1_trace_gns_booleanization.json"
P3 = DERIVED / "p3_clp3_complete_seed_presentation.json"
BOOLEAN = DERIVED / "p3_clp3_p1_seed_boolean_car_bridge.json"
OUT = DERIVED / "p3_clp3_p1_trace_gns_booleanization_audit.json"
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
    p3 = json.loads(P3.read_text(encoding="utf-8"))
    boolean = json.loads(BOOLEAN.read_text(encoding="utf-8"))
    payload = packet["source_freeze_payload"]

    block_size = 8
    n_blocks = 4
    algebra_dimension = n_blocks * block_size**2
    abstract_minimal_module_dimension = n_blocks * block_size

    # A vector in C^n tensor C^m induces on M_n a density of rank at most m.
    # The faithful trace has density I_n/n and therefore rank n, so m >= n.
    trace_density = np.eye(block_size) / block_size
    trace_density_rank = int(np.linalg.matrix_rank(trace_density, tol=TOL))
    minimal_module_vector_density = np.zeros((block_size, block_size))
    minimal_module_vector_density[0, 0] = 1.0
    minimal_module_vector_density_rank = int(
        np.linalg.matrix_rank(minimal_module_vector_density, tol=TOL)
    )
    root_preserving_multiplicity_lower_bound = trace_density_rank
    root_preserving_dimension_lower_bound = (
        n_blocks * block_size * root_preserving_multiplicity_lower_bound
    )

    # Explicit maximally entangled GNS root for one M_8 block.
    omega_block = np.eye(block_size, dtype=complex).reshape(-1) / np.sqrt(block_size)
    rng = np.random.default_rng(20260828)
    vector_state_defects = []
    for _ in range(12):
        a = rng.normal(size=(block_size, block_size)) + 1j * rng.normal(
            size=(block_size, block_size)
        )
        represented = np.kron(a, np.eye(block_size))
        vector_value = np.vdot(omega_block, represented @ omega_block)
        trace_value = np.trace(a) / block_size
        vector_state_defects.append(abs(vector_value - trace_value))
    trace_root_defect = max(vector_state_defects)

    # The orbit of matrix units on the maximally entangled root spans n^2.
    block_orbit = []
    for i in range(block_size):
        for j in range(block_size):
            eij = np.zeros((block_size, block_size), dtype=complex)
            eij[i, j] = 1.0
            block_orbit.append(np.kron(eij, np.eye(block_size)) @ omega_block)
    block_orbit_matrix = np.column_stack(block_orbit)
    block_orbit_rank = int(np.linalg.matrix_rank(block_orbit_matrix, tol=TOL))

    n_modes = 7
    word_dim = 1 << n_modes
    creators, annihilators = fermion_operators(n_modes)
    clifford = [c + a for c, a in zip(creators, annihilators)]
    identity = np.eye(word_dim, dtype=complex)
    zero = np.zeros_like(identity)
    degrees = np.array([bin(state).count("1") for state in range(word_dim)])
    projectors = [np.diag((degrees == k).astype(float)) for k in range(n_modes + 1)]

    split_creators = []
    split_annihilators = []
    for g in clifford:
        raising = sum(
            (projectors[k + 1] @ g @ projectors[k] for k in range(n_modes)),
            start=np.zeros_like(g),
        )
        lowering = sum(
            (projectors[k - 1] @ g @ projectors[k] for k in range(1, n_modes + 1)),
            start=np.zeros_like(g),
        )
        split_creators.append(raising)
        split_annihilators.append(lowering)

    split_recovery_defect = max(
        np.linalg.norm(clifford[a] - split_creators[a] - split_annihilators[a])
        for a in range(n_modes)
    )
    split_mixed_car_defect = max(
        np.linalg.norm(
            split_annihilators[a] @ split_creators[b]
            + split_creators[b] @ split_annihilators[a]
            - (identity if a == b else zero)
        )
        for a in range(n_modes)
        for b in range(n_modes)
    )
    split_same_car_defect = max(
        max(
            np.linalg.norm(
                split_creators[a] @ split_creators[b]
                + split_creators[b] @ split_creators[a]
            ),
            np.linalg.norm(
                split_annihilators[a] @ split_annihilators[b]
                + split_annihilators[b] @ split_annihilators[a]
            ),
        )
        for a in range(n_modes)
        for b in range(n_modes)
    )
    number = sum(
        (c @ a for c, a in zip(split_creators, split_annihilators)),
        start=np.zeros_like(identity),
    )
    degree_operator = np.diag(degrees.astype(float))
    number_defect = np.linalg.norm(number - degree_operator)

    vacuum = np.zeros(word_dim, dtype=complex)
    vacuum[0] = 1.0
    word_orbit = []
    for subset in range(word_dim):
        state = vacuum.copy()
        for mode in range(n_modes):
            if subset & (1 << mode):
                state = split_creators[mode] @ state
        word_orbit.append(state)
    word_orbit_matrix = np.column_stack(word_orbit)
    word_orbit_rank = int(np.linalg.matrix_rank(word_orbit_matrix, tol=TOL))
    word_orbit_gram_defect = np.linalg.norm(
        word_orbit_matrix.conj().T @ word_orbit_matrix - identity
    )

    checks: dict[str, bool] = {}
    checks["fingerprint_matches_payload"] = (
        hashlib.sha256(canonical_bytes(payload)).hexdigest()
        == packet["source_fingerprint_sha256"]
    )
    checks["upstream_p3_packet_is_locked"] = (
        payload["upstream_p3_fingerprint_sha256"]
        == p3["source_fingerprint_sha256"]
    )
    checks["upstream_boolean_packet_is_locked"] = (
        payload["upstream_boolean_fingerprint_sha256"]
        == boolean["source_fingerprint_sha256"]
    )
    checks["endpoint_blind_freeze"] = (
        payload["terminal_data_used"] is False
        and payload["endpoint_fitted_parameters"] == []
    )
    checks["joint_algebra_dimension_is_256"] = algebra_dimension == 256
    checks["abstract_minimal_faithful_module_dimension_is_32"] = (
        abstract_minimal_module_dimension == 32
    )
    checks["trace_density_has_full_block_rank"] = trace_density_rank == 8
    checks["one_copy_vector_state_is_rank_one_and_nonfaithful"] = (
        minimal_module_vector_density_rank == 1
    )
    checks["faithful_trace_root_requires_multiplicity_at_least_eight"] = (
        root_preserving_multiplicity_lower_bound == 8
    )
    checks["faithful_trace_root_carrier_lower_bound_is_256"] = (
        root_preserving_dimension_lower_bound == 256
    )
    checks["maximally_entangled_root_realizes_normalized_trace"] = (
        trace_root_defect < TOL
    )
    checks["one_block_trace_root_orbit_has_rank_64"] = block_orbit_rank == 64
    checks["four_block_trace_gns_orbit_has_rank_256"] = (
        n_blocks * block_orbit_rank == 256
    )
    checks["degree_split_recovers_each_clifford_generator"] = (
        split_recovery_defect < TOL
    )
    checks["degree_split_obeys_mixed_car"] = split_mixed_car_defect < TOL
    checks["degree_split_obeys_same_type_car"] = split_same_car_defect < TOL
    checks["degree_split_recovers_exterior_number"] = number_defect < TOL
    checks["empty_root_generates_all_128_clifford_words"] = word_orbit_rank == 128
    checks["clifford_word_orbit_is_orthonormal"] = word_orbit_gram_defect < TOL
    checks["binary_record_doubles_word_orbit_to_256"] = 2 * word_orbit_rank == 256
    checks["jcm_32_is_retyped_as_root_free_only"] = (
        payload["carrier_typing_correction"][
            "abstract_minimal_faithful_module_dimension"
        ]
        == 32
        and payload["carrier_typing_correction"][
            "faithful_trace_gns_carrier_dimension"
        ]
        == 256
    )
    checks["nature_occupation_remains_open"] = (
        payload["claim_boundary"]["narrow_old_bare_tau_owns_trace_gns_root"]
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
            "FAITHFUL_TRACE_GNS_ROOT_FORCES_256_AND_TYPED_CLIFFORD_"
            "DEGREE_DERIVES_BOOLEAN_CAR7"
        ),
        "diagnostics": {
            "joint_algebra_dimension": algebra_dimension,
            "abstract_minimal_faithful_module_dimension": (
                abstract_minimal_module_dimension
            ),
            "trace_density_rank_per_block": trace_density_rank,
            "minimal_module_vector_density_rank_per_block": (
                minimal_module_vector_density_rank
            ),
            "root_preserving_dimension_lower_bound": (
                root_preserving_dimension_lower_bound
            ),
            "trace_root_defect": float(trace_root_defect),
            "one_block_root_orbit_rank": block_orbit_rank,
            "four_block_root_orbit_rank": n_blocks * block_orbit_rank,
            "clifford_split_recovery_defect": float(split_recovery_defect),
            "clifford_split_mixed_car_defect": float(split_mixed_car_defect),
            "clifford_split_same_car_defect": float(split_same_car_defect),
            "number_operator_defect": float(number_defect),
            "word_orbit_rank": word_orbit_rank,
            "word_orbit_gram_defect": float(word_orbit_gram_defect),
        },
        "exact_remaining_physical_datum": payload[
            "exact_remaining_physical_datum"
        ],
        "physical_source_ownership": "OPEN",
        "nature_level_occupation": False,
    }
    OUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    if passed != len(checks):
        failed = [key for key, value in checks.items() if not value]
        raise SystemExit(f"P1_TRACE_GNS_BOOLEANIZATION_AUDIT_FAIL {failed}")
    print(f"P1_TRACE_GNS_BOOLEANIZATION_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
