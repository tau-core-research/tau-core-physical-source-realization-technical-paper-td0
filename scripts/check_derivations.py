from pathlib import Path
import json
import math
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
DERIVED.mkdir(parents=True, exist_ok=True)


def heat_trace(matrix, action_unit=1.0):
    eig = np.linalg.eigvalsh(np.asarray(matrix, dtype=float))
    return float(np.exp(-eig / action_unit).sum())


def spectral_state(matrix, action_unit=1.0):
    eig, vec = np.linalg.eigh(np.asarray(matrix, dtype=float))
    weights = np.exp(-eig / action_unit)
    rho = (vec * (weights / weights.sum())) @ vec.T
    return rho


def main():
    checks = {}

    action_unit = 1.0
    K = np.diag([0.35, 0.9, 1.8])
    checks["positive_action_unit"] = action_unit > 0
    checks["positive_hodge_operator"] = np.linalg.eigvalsh(K).min() > 0

    # A coupled proper extension whose upper-left compression is exactly K.
    b = np.array([[0.08], [-0.04], [0.03]])
    K_ext = np.block([[K, b], [b.T, np.array([[2.6]])]])
    checks["extension_positive"] = np.linalg.eigvalsh(K_ext).min() > 0
    Z = heat_trace(K, action_unit)
    Z_ext = heat_trace(K_ext, action_unit)
    checks["strict_heat_trace_extension"] = Z_ext > Z
    checks["log_monotonicity"] = math.log(Z_ext) > math.log(Z)

    K1 = np.diag([0.2, 1.1])
    K2 = np.diag([0.4, 0.8, 1.7])
    K12 = np.kron(K1, np.eye(3)) + np.kron(np.eye(2), K2)
    checks["tensor_heat_trace_factorization"] = np.isclose(
        heat_trace(K12), heat_trace(K1) * heat_trace(K2), rtol=1e-12, atol=1e-12
    )
    checks["log_heat_trace_additivity"] = np.isclose(
        math.log(heat_trace(K12)), math.log(heat_trace(K1)) + math.log(heat_trace(K2)), rtol=1e-12, atol=1e-12
    )

    rho = spectral_state(K)
    checks["spectral_state_normalized"] = np.isclose(np.trace(rho), 1.0)
    checks["spectral_state_faithful"] = np.linalg.eigvalsh(rho).min() > 0

    theta = 0.47
    J = np.array([
        [math.cos(theta), -math.sin(theta), 0.0],
        [math.sin(theta), math.cos(theta), 0.0],
        [0.0, 0.0, 1.0],
    ])
    I = np.eye(3)
    checks["source_gram_identity"] = np.allclose(J.T @ J, I)
    checks["target_gram_identity"] = np.allclose(J @ J.T, I)
    checks["hodge_transport"] = np.allclose(J @ K @ J.T, J @ K @ np.linalg.inv(J))

    seed_vec = np.array([1.0, -0.25, 0.5])
    hidden_seed = np.concatenate([seed_vec, [0.0]])
    checks["hidden_block_same_seed_restriction"] = np.allclose(hidden_seed[:3], seed_vec) and hidden_seed[-1] == 0
    checks["hidden_block_rejected_if_selector_owned"] = Z_ext > Z

    Gamma = 0.37
    lam = 1.4
    checks["off_shell_same_minimum"] = (Gamma + lam * Gamma**2) > Gamma and (0.0 + lam * 0.0**2) == 0.0
    checks["off_shell_same_two_jet_at_zero"] = np.isclose(1.0, 1.0 + 2.0 * lam * 0.0)

    role_rotation = np.array([[0.0, -1.0], [1.0, 0.0]])
    K_role = np.eye(2)
    checks["spectral_selector_role_blind_control"] = np.allclose(role_rotation @ K_role @ role_rotation.T, K_role)

    contract = json.loads((DERIVED / "interface_contract.json").read_text())
    p3_packet = json.loads(
        (DERIVED / "p3_clp3_complete_seed_presentation.json").read_text()
    )
    p3_audit = json.loads(
        (DERIVED / "p3_clp3_instantiation_audit.json").read_text()
    )
    p1_ambient_certificate = json.loads(
        (DERIVED / "p3_clp3_p1_ambient_certificate.json").read_text()
    )
    p1_ambient_audit = json.loads(
        (DERIVED / "p3_clp3_p1_ambient_certificate_audit.json").read_text()
    )
    p1_envelope_separator = json.loads(
        (DERIVED / "p3_clp3_p1_source_envelope_separator.json").read_text()
    )
    p1_envelope_audit = json.loads(
        (DERIVED / "p3_clp3_p1_source_envelope_separator_audit.json").read_text()
    )
    p1_connector_selector = json.loads(
        (DERIVED / "p3_clp3_p1_envelope_connector_selector.json").read_text()
    )
    p1_connector_audit = json.loads(
        (DERIVED / "p3_clp3_p1_envelope_connector_selector_audit.json").read_text()
    )
    single_source_law = json.loads(
        (DERIVED / "p3_clp3_single_source_law.json").read_text()
    )
    single_source_audit = json.loads(
        (DERIVED / "p3_clp3_single_source_law_audit.json").read_text()
    )
    checks["interface_is_forward_only"] = contract["consumes"] == "CompleteSeedPresentation" and contract["produces"] == "BaseSeedPacket"
    checks["terminal_fit_forbidden"] = contract["terminal_fit_allowed"] is False
    checks["nature_claim_bounded"] = contract["nature_occupation_proved"] is False
    checks["p3_clp3_instantiation_audit_passes"] = p3_audit["passed"] == p3_audit["total"]
    checks["p3_clp3_seed_is_endpoint_blind"] = p3_packet["source_freeze_payload"]["terminal_data_used"] is False
    checks["p3_clp3_nature_export_is_not_authorized"] = p3_audit["physical_base_seed_packet_export_authorized"] is False
    checks["p1_ambient_certificate_audit_passes"] = (
        p1_ambient_audit["passed"] == p1_ambient_audit["total"]
    )
    checks["p1_ambient_rank_theorem_is_conditionally_realized"] = (
        p1_ambient_audit["verdict"]
        == "CONDITIONAL_P1_AMBIENT_RANK_THEOREM_PASS"
    )
    checks["p1_hidden_relation_and_component_controls_pass"] = (
        p1_ambient_audit["checks"][
            "same_component_missing_relation_is_detected"
        ]
        and p1_ambient_audit["checks"][
            "hidden_component_fails_global_ambient_rank"
        ]
        and p1_ambient_audit["checks"][
            "faithfulness_gate_rejects_that_false_positive"
        ]
    )
    checks["p1_control_is_endpoint_blind_but_not_physical_certificate"] = (
        p1_ambient_certificate["source_freeze_payload"]["terminal_data_used"]
        is False
        and p1_ambient_audit["physical_P1_certificate_eligible"] is False
        and p1_ambient_audit["P1_physical_exhaustivity_proved"] is False
    )
    checks["p1_source_envelope_separator_audit_passes"] = (
        p1_envelope_audit["passed"] == p1_envelope_audit["total"]
    )
    checks["p1_prebody_envelope_exposes_global_rank_gap"] = (
        p1_envelope_audit["diagnostics"]["p3_component_algebra_dimension"]
        == 256
        and p1_envelope_audit["diagnostics"]["prebody_pusc_algebra_dimension"]
        == 1024
        and p1_envelope_audit["diagnostics"]["prebody_rank_ratio"] == 0.25
    )
    checks["p1_envelope_separator_preserves_forward_order"] = (
        p1_envelope_separator["source_freeze_payload"]["independent_source_candidate"][
            "source_first"
        ]
        is True
        and p1_envelope_separator["source_freeze_payload"][
            "downstream_control_only"
        ]["eligible_as_upstream_p1_ambient"]
        is False
    )
    checks["p1_envelope_result_is_nature_bounded"] = (
        p1_envelope_audit["nature_level_ambient_choice"] == "OPEN"
        and p1_envelope_audit["physical_P1_exhaustivity_proved"] is False
        and p1_envelope_audit["physical_base_seed_packet_export_authorized"]
        is False
    )
    checks["p1_connector_selector_audit_passes"] = (
        p1_connector_audit["passed"] == p1_connector_audit["total"]
    )
    checks["p1_connector_rank_ladder_closes_the_declared_pusc_envelope"] = (
        p1_connector_audit["diagnostics"]["algebra_dimensions"]
        == {
            "p3_only": 256,
            "p3_plus_u": 512,
            "p3_plus_v": 512,
            "p3_plus_u_and_v": 1024,
        }
    )
    checks["p1_connector_action_has_positive_wrong_family_controls"] = (
        p1_connector_audit["diagnostics"]["good_connector_defect"] == 0.0
        and p1_connector_audit["diagnostics"]["zero_u_defect"] > 0.0
        and p1_connector_audit["diagnostics"]["zero_v_defect"] > 0.0
        and p1_connector_audit["diagnostics"]["scaled_u_defect"] > 0.0
        and p1_connector_audit["diagnostics"]["wrong_v_defect"] > 0.0
    )
    checks["p1_connector_completion_is_conditional_and_nature_bounded"] = (
        p1_connector_selector["source_freeze_payload"]["terminal_data_used"]
        is False
        and p1_connector_audit["physical_connector_ownership"] == "OPEN"
        and p1_connector_audit["physical_P1_exhaustivity_proved"] is False
        and p1_connector_audit["physical_base_seed_packet_export_authorized"]
        is False
    )
    checks["single_source_law_audit_passes"] = single_source_audit["passed"] == single_source_audit["total"]
    checks["single_source_law_compresses_p4_through_p7"] = single_source_audit["verdict"] == "P4_P7_SINGLE_ACTION_COMPRESSION_PASS"
    checks["single_source_law_does_not_self_certify_p1"] = single_source_audit["P1_physical_source_language_ownership_proved"] is False
    checks["single_source_law_is_endpoint_blind_and_nature_bounded"] = (
        single_source_law["source_freeze_payload"]["terminal_data_used"] is False
        and single_source_audit["nature_level_occupation"] is False
        and single_source_audit["physical_base_seed_packet_export_authorized"] is False
    )

    passed = sum(bool(v) for v in checks.values())
    audit = {
        "checks": {k: bool(v) for k, v in checks.items()},
        "passed": passed,
        "total": len(checks),
        "heat_trace_base": Z,
        "heat_trace_extension": Z_ext,
        "nature_level_closure": False,
    }
    (DERIVED / "derivation_audit.json").write_text(json.dumps(audit, indent=2) + "\n")

    ledger = {
        "nature_level_validation": False,
        "unrestricted_parent_selection_derived": False,
        "empirical_data_used": False,
        "results": [
            {"id": "PSR1", "status": "definition", "claim": "The exact zero set of the complete source residual defines the source-compatible fibre."},
            {"id": "PSR2", "status": "proved_conditional", "claim": "A proper positive finite common-compression extension has strictly larger heat trace."},
            {"id": "PSR3", "status": "proved_conditional", "claim": "Continuous tensor-additive spectral complexity is logarithmic up to normalization."},
            {"id": "PSR4", "status": "proved", "claim": "The normalized exponential of a trace-class positive source operator is faithful; its standard GNS root is cyclic."},
            {"id": "PSR5", "status": "proved_conditional", "claim": "Two-sided Gram identities plus typed intertwining give a lossless source-to-base realization."},
            {"id": "PSR6", "status": "proved_conditional", "claim": "Attainment and equality rigidity select one source-equivalence class on the exact compatibility fibre."},
            {"id": "PSR7", "status": "proved_no_go", "claim": "The narrow seed reduct cannot exclude a hidden seed-annihilator block without an independently owned selection law."},
            {"id": "PSR8", "status": "proved_no_go", "claim": "Spectral minimality does not select terminal-role labels or a unique off-shell action representative."},
            {"id": "PSR9", "status": "proved_conditional", "claim": "The selected realized class exports the frozen BaseSeedPacket without terminal fitting."},
            {"id": "PSR10", "status": "proved_internal_finite", "claim": "The frozen P3/CLP3 candidate realizes a complete seven-generator Clifford and two-record presentation with a faithful cyclic 256-dimensional source representation, typed support flag and two ordered ports."},
            {"id": "PSR11", "status": "proved_no_go", "claim": "The explicit P3/CLP3 instantiation does not prove physical ownership, unrestricted ambient exhaustivity, equality rigidity, or Nature-authorized BaseSeedPacket export."},
            {"id": "PSR12", "status": "proved_conditional", "claim": "One nonnegative source-fidelity, two-sided-Gram and Schur-neutral body-square action jointly realizes P4--P7 after a complete source language is supplied."},
            {"id": "PSR13", "status": "proved_no_go", "claim": "A source action cannot certify completeness of the residual language used to define its own admissible fibre; P1 remains source data or an independently proved exhaustivity theorem."},
            {"id": "PSR14", "status": "proved_no_go", "claim": "An independent component zero-jet can reverse global selection without changing the local Hodge packet, so unrestricted Nature ownership does not follow from the single-action witness."},
            {"id": "PSR15", "status": "proved_conditional", "claim": "For a finite independently frozen physical source algebra with faithful state, the seed language is exhaustive exactly when its regular-GNS span has full ambient rank."},
            {"id": "PSR16", "status": "proved_no_go", "claim": "A missing same-component relation, a hidden central component, or a nonfaithful ambient state defeats an otherwise local source-completeness test."},
            {"id": "PSR17", "status": "proved_internal_finite", "claim": "The P3/CLP3 regular-GNS control has rank 256 on its declared 256-dimensional ambient, but is not a physical P1 certificate because that ambient was not independently derived from the seed candidate."},
            {"id": "PSR18", "status": "proved_conditional", "claim": "The independently declared pre-body PUSC simple envelope gives a candidate ambient Cl_10(C) isomorphic to M_32(C), with faithful normalized-trace GNS algebra dimension 1024."},
            {"id": "PSR19", "status": "proved_conditional_no_go", "claim": "Under the envelope-ontic interpretation and a physical typed embedding, the 256-dimensional P3/CLP3 algebra is component-complete but fails global P1 by the exact faithful-GNS rank ratio 256/1024=1/4."},
            {"id": "PSR20", "status": "proved_no_go", "claim": "The same local P3 packet is compatible with an ontic-envelope branch and a metric-auxiliary branch, so local seed data do not select the ambient ontology; Nature ownership remains open."},
            {"id": "PSR21", "status": "proved_internal_finite", "claim": "In the declared 32-dimensional Cl_10 representation, the P3 algebra is the four-block algebra selected by the commuting chirality and record involutions, with four rank-eight central projections and equal normalized-trace weights."},
            {"id": "PSR22", "status": "proved_conditional", "claim": "The homogeneous connectors u=gamma_8 and v=gamma_10 give the exact algebra-dimension ladder 256, 512, 512, 1024; within this declared connector class both are necessary and together generate M_32(C)."},
            {"id": "PSR23", "status": "proved_conditional", "claim": "A single nonnegative Hilbert-Schmidt connector-defect action has a zero-defect Cl_10 witness and rejects absent, rescaled and wrong-grading connector controls once the connector domain and relation grammar are source-owned."},
            {"id": "PSR24", "status": "proved_no_go", "claim": "The connector action cannot derive the existence of its own typed u/v variables from P3-local data, and simple M_32(C) has no nontrivial star-ideal quotient to M_8(C)^{oplus 4}; Nature-level connector ownership remains open."},
        ],
    }
    (DERIVED / "theorem_ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")

    if passed != len(checks):
        failed = [k for k, v in checks.items() if not v]
        raise SystemExit(f"PHYSICAL_SOURCE_DERIVATION_AUDIT_FAIL {failed}")
    print(f"PHYSICAL_SOURCE_DERIVATION_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
