#!/usr/bin/env python3
"""Freeze the finite P3/CLP3 CompleteSeedPresentation candidate.

The packet is source-side and endpoint blind.  It is a concrete mathematical
instantiation on the declared finite support, not a claim that Nature owns or
occupies this completion.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "p3_clp3_complete_seed_presentation.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def build_packet() -> dict[str, object]:
    roles = ["B", "O", "R", "U", "Q", "M", "G"]
    relative_roles = ["B", "O", "R", "Q", "M", "G"]
    source_payload: dict[str, object] = {
        "candidate_id": "P3-CLP3-CSP-v1",
        "freeze_date": "2026-08-28",
        "status": "SOURCE_FROZEN_CONDITIONAL_COMPLETION_CANDIDATE",
        "terminal_data_used": False,
        "endpoint_fitted_parameters": [],
        "canonical_owners": [
            "docs/tau_core_p3_occupied_algebra_reconstruction_001.md",
            "docs/tau_core_base_seed_full_response_three_front_001.md",
            "docs/tau_core_cross_scale_readout_composition_principle_001.md",
        ],
        "complete_seed_presentation": {
            "type": "CompleteSeedPresentation",
            "tuple": [
                "R_s",
                "A_s",
                "pi_s",
                "H_s",
                "Omega_s",
                "g_s",
                "delta_s",
                "A_*",
            ],
            "role_order": roles,
            "degree_one_carrier": {
                "symbol": "E_P3",
                "field": "C",
                "dimension": 7,
                "metric": "K_*=I_7 in the frozen source-orthonormal frame",
                "typed_rays": {role: index for index, role in enumerate(roles)},
            },
            "primitive_generators": {
                "role_generators": [f"g_{role}" for role in roles],
                "record_idempotents": ["p_0", "p_1"],
            },
            "relations": [
                "g_a^*=g_a",
                "g_a g_b+g_b g_a=2 delta_ab 1",
                "p_r^*=p_r",
                "p_r p_s=delta_rs p_r",
                "p_0+p_1=1",
                "[p_r,g_a]=0",
            ],
            "quotient_algebra": {
                "presentation": "Cl(E_P3,K_*) tensor (C direct-sum C)",
                "isomorphism_class": "M_8(C) direct-sum M_8(C) direct-sum M_8(C) direct-sum M_8(C)",
                "complex_dimension": 256,
                "source_exhaustivity_scope": "declared P3 component only",
            },
            "representation": {
                "H_s": "Lambda^bullet(C^7) tensor C^2_record",
                "dimension": 256,
                "pi_s(g_a)": "(exterior_creation_a+exterior_contraction_a) tensor I_2",
                "pi_s(p_r)": "I_128 tensor |r><r|",
                "Omega_s": "|empty> tensor (|0>+|1>)/sqrt(2)",
                "root_property": "faithful cyclic trace-GNS root on the declared quotient",
            },
            "grading_and_source_symmetry": {
                "clifford_grade": "gamma(g_a)=-g_a; gamma(p_r)=p_r",
                "record_exchange": "sigma(g_a)=g_a; sigma(p_0)=p_1",
                "trace": "tau_sym=(1/4) sum_(epsilon,r) tr_8",
                "central_weights": [0.25, 0.25, 0.25, 0.25],
            },
            "hodge_action_datum": {
                "delta_s": "canonical exterior creation/contraction calculus",
                "K_s": "N_ext tensor I_2",
                "eigenvalues": list(range(8)),
                "multiplicity_rule": "2 binomial(7,degree)",
                "action_unit": 1.0,
                "action_unit_status": "dimensionless source normalization; A_*=hbar only under the separate faithful phase theorem",
            },
            "typed_support_flag": {
                "relative_role_order": relative_roles,
                "projector_supports": {
                    "P_BMG": ["B", "M", "G"],
                    "P_OQ": ["O", "Q"],
                    "P_RMG": ["R", "M", "G"],
                },
                "joint_blocks": {"100": 1, "010": 2, "001": 1, "101": 2},
                "ordered_ports": {
                    "OQ": {"source_leg": "O", "conjugate_response_leg": "Q"},
                    "MG": {"source_leg": "M", "conjugate_response_leg": "G"},
                },
                "independent_unit_line": "L_U",
            },
        },
        "component_local_completion": {
            "representative": "Gamma_CLP3=sum_(C in pi_0(s_U)) Gamma_C",
            "p3_component_law": "L_P3^min",
            "clauses": {
                "JLC1": "primitive support exhaustivity",
                "JLC2": "component preservation",
                "JLC3": "once-counted nonnegative component action with no hidden global predicate",
                "JLC4": "source-rigid common-unit realization",
                "JLC5": "the connected P3 component carries L_P3^min with attainable zero",
            },
            "identifiable_class": "[Gamma_CLP3]_QG: same physical minimum, true-normal Hessian, typed support/port/root/phase packet",
            "off_shell_representative_unique": False,
        },
        "qg_fanout": {
            "source_module": "two-mode pointed CAR module H_src=C^4",
            "role_plane": "R_QG=span(v_Q,v_G)",
            "joint_support": "R_QG tensor H_src",
            "role_fibres": {"Q": "H_src", "G": "H_src"},
            "transport": "T_(G<-Q)=W_G W_Q^+",
            "relative_metric_law": "T^dagger h_G T=h_Q",
            "phase_identification": "A_*=hbar only if the faithful phase-character premise is physically owned",
        },
        "conditional_base_seed_packet_candidate": {
            "type": "BaseSeedPacketCandidate",
            "B_tau_phys": "finite P3/CLP3 candidate carrier; not Nature-certified",
            "s_U": "typed E_P3 relation seed plus two-leg record root",
            "A_B": "unit positive quadratic downstream witness only",
            "J_seed": "identity on the seven source-orthonormal role directions",
            "N_phys": "zero on the declared finite witness",
            "source_grading": "typed P3 rays plus Clifford grade and record exchange",
            "A_*": 1.0,
            "physical_export_authorized": False,
        },
        "p1_p7_ledger": {
            "P1_complete_seed_physically_owned": {
                "candidate_instantiated": True,
                "nature_ownership_proved": False,
            },
            "P2_exact_compatible_fibre": {
                "finite_declared_support_witness": True,
                "unrestricted_ambient_exhaustivity_proved": False,
            },
            "P3_positive_trace_class_hodge_action": {
                "finite_witness": True,
            },
            "P4_physical_spectral_priority": {
                "candidate_law_declared": True,
                "nature_ownership_proved": False,
            },
            "P5_attainment_and_equality_rigidity": {
                "completion_class_attained": True,
                "unrestricted_rigidity_proved": False,
            },
            "P6_two_sided_typed_realization": {
                "identity_witness_on_declared_support": True,
                "physical_base_ownership_proved": False,
            },
            "P7_td1_regular_handoff": {
                "unit_quadratic_interface_witness": True,
                "physical_body_law_selected": False,
            },
        },
        "claim_boundary": {
            "internal_finite_seed_presentation_complete": True,
            "conditional_clp3_law_to_p3_occupation": True,
            "conditional_qg_fanout": True,
            "nature_seed_selection": False,
            "nature_occupation": False,
            "ambient_parent_exhaustivity": False,
            "empirical_validation": False,
        },
    }
    fingerprint = hashlib.sha256(canonical_bytes(source_payload)).hexdigest()
    return {
        "schema": "tau_core_p3_clp3_complete_seed_presentation_v1",
        "source_freeze_payload": source_payload,
        "source_fingerprint_sha256": fingerprint,
    }


def main() -> None:
    packet = build_packet()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(f"P3_CLP3_SOURCE_FREEZE {packet['source_fingerprint_sha256']}")


if __name__ == "__main__":
    main()
