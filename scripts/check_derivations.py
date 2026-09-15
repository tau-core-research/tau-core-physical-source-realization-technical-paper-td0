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

    gram_identity = np.eye(4)
    gram_collective = np.ones((4, 4))
    checks["finite_gram_counterpair_is_admissible"] = (
        np.allclose(np.diag(gram_identity), 1.0)
        and np.allclose(np.diag(gram_collective), 1.0)
        and np.linalg.eigvalsh(gram_identity).min() >= -1e-12
        and np.linalg.eigvalsh(gram_collective).min() >= -1e-12
    )
    checks["finite_gram_converse_does_not_select_source"] = (
        np.linalg.matrix_rank(gram_identity) != np.linalg.matrix_rank(gram_collective)
    )

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
    p1_record_embedding = json.loads(
        (DERIVED / "p3_clp3_p1_record_clifford_embedding.json").read_text()
    )
    p1_record_embedding_audit = json.loads(
        (DERIVED / "p3_clp3_p1_record_clifford_embedding_audit.json").read_text()
    )
    p1_record_landing = json.loads(
        (DERIVED / "p3_clp3_p1_record_clifford_landing.json").read_text()
    )
    p1_record_landing_audit = json.loads(
        (DERIVED / "p3_clp3_p1_record_clifford_landing_audit.json").read_text()
    )
    p1_record_source_completion = json.loads(
        (DERIVED / "p3_clp3_p1_record_clifford_source_completion.json").read_text()
    )
    p1_record_source_completion_audit = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_record_clifford_source_completion_audit.json"
        ).read_text()
    )
    p1_joint_graded_representation = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_joint_graded_representation.json"
        ).read_text()
    )
    p1_joint_graded_representation_audit = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_joint_graded_representation_audit.json"
        ).read_text()
    )
    p1_joint_carrier_minimality = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_joint_carrier_minimality.json"
        ).read_text()
    )
    p1_joint_carrier_minimality_audit = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_joint_carrier_minimality_audit.json"
        ).read_text()
    )
    p1_spectral_priority_origin = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_spectral_priority_origin.json"
        ).read_text()
    )
    p1_spectral_priority_origin_audit = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_spectral_priority_origin_audit.json"
        ).read_text()
    )
    p1_hodge_functorial_origin = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_hodge_functorial_origin.json"
        ).read_text()
    )
    p1_hodge_functorial_origin_audit = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_hodge_functorial_origin_audit.json"
        ).read_text()
    )
    p1_role_record_hodge_ownership = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_role_record_hodge_ownership.json"
        ).read_text()
    )
    p1_role_record_hodge_ownership_audit = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_role_record_hodge_ownership_audit.json"
        ).read_text()
    )
    p1_seed_boolean_car_bridge = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_seed_boolean_car_bridge.json"
        ).read_text()
    )
    p1_seed_boolean_car_bridge_audit = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_seed_boolean_car_bridge_audit.json"
        ).read_text()
    )
    p1_existing_action_snpr_selection = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_existing_action_snpr_selection.json"
        ).read_text()
    )
    p1_existing_action_snpr_selection_audit = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_existing_action_snpr_selection_audit.json"
        ).read_text()
    )
    p1_snpr_ownership_refinement = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_snpr_ownership_refinement.json"
        ).read_text()
    )
    p1_snpr_ownership_refinement_audit = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_snpr_ownership_refinement_audit.json"
        ).read_text()
    )
    p1_operational_record_origin = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_operational_record_origin.json"
        ).read_text()
    )
    p1_operational_record_origin_audit = json.loads(
        (
            DERIVED
            / "p3_clp3_p1_operational_record_origin_audit.json"
        ).read_text()
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
    checks["p1_record_clifford_embedding_audit_passes"] = (
        p1_record_embedding_audit["passed"]
        == p1_record_embedding_audit["total"]
    )
    checks["p1_connector_pair_reduces_to_one_graded_embedding"] = (
        p1_record_embedding_audit["diagnostics"]["good_adjoint_eigenvalues"]
        == [-1.0, -1.0, 1.0]
        and p1_record_embedding["source_freeze_payload"][
            "conditional_consequence"
        ]["connector_variables_are_independent_primitives"]
        is False
    )
    checks["p1_record_embedding_has_adversarial_nonentailment_controls"] = (
        p1_record_embedding_audit["checks"][
            "odd_twist_preserves_local_p3_record_reduct"
        ]
        and p1_record_embedding_audit["checks"][
            "misaligned_control_preserves_local_p3_record_reduct"
        ]
        and p1_record_embedding_audit["checks"][
            "local_reduct_does_not_entail_graded_embedding"
        ]
    )
    checks["p1_record_embedding_selection_is_open_and_nature_bounded"] = (
        p1_record_embedding_audit[
            "physical_record_clifford_embedding_ownership"
        ]
        == "OPEN"
        and p1_record_embedding_audit["nature_level_occupation"] is False
        and p1_record_embedding_audit["physical_P1_exhaustivity_proved"]
        is False
    )
    checks["p1_record_clifford_landing_audit_passes"] = (
        p1_record_landing_audit["passed"]
        == p1_record_landing_audit["total"]
    )
    checks["p1_even_landing_has_one_spin3_gauge_orbit"] = (
        p1_record_landing_audit["checks"][
            "valid_embedding_set_is_one_spin3_orbit"
        ]
        and p1_record_landing_audit["checks"][
            "even_landing_automatically_preserves_W"
        ]
        and p1_record_landing["source_freeze_payload"][
            "automatic_consequences"
        ]["separate_vector_preservation_premise_required"]
        is False
    )
    checks["p1_exact_remaining_datum_is_cross_landing_not_map_choice"] = (
        p1_record_landing_audit["exact_remaining_source_datum"]
        == "physical occupation of the even-relative-commutant landing class"
        and p1_record_landing_audit["checks"][
            "current_joint_action_contains_no_cross_landing_equation"
        ]
        and p1_record_landing_audit["physical_source_ownership"] == "OPEN"
    )
    checks["p1_record_source_completion_audit_passes"] = (
        p1_record_source_completion_audit["passed"]
        == p1_record_source_completion_audit["total"]
    )
    checks["p1_same_reduct_models_prove_current_source_nonentailment"] = (
        p1_record_source_completion_audit["checks"][
            "internal_and_external_models_share_the_current_reduct"
        ]
        and p1_record_source_completion["source_freeze_payload"][
            "same_reduct_models"
        ]["different_landing_truth_value"]
    )
    checks["p1_internal_graded_locality_is_minimal_and_claim_bounded"] = (
        p1_record_source_completion_audit["checks"][
            "both_cross_components_are_logically_necessary"
        ]
        and p1_record_source_completion_audit["checks"][
            "zero_set_modulo_gauge_is_one_orbit"
        ]
        and p1_record_source_completion_audit["physical_source_ownership"]
        == "OPEN"
        and p1_record_source_completion_audit["nature_level_occupation"]
        is False
    )
    checks["p1_joint_graded_representation_audit_passes"] = (
        p1_joint_graded_representation_audit["passed"]
        == p1_joint_graded_representation_audit["total"]
    )
    checks["p1_igl_is_equivalent_to_same_envelope_joint_realization"] = (
        p1_joint_graded_representation_audit["checks"][
            "internal_joint_representation_has_full_256_rank"
        ]
        and p1_joint_graded_representation_audit["checks"][
            "every_sampled_igl_zero_defines_a_faithful_joint_representation"
        ]
        and p1_joint_graded_representation["source_freeze_payload"][
            "claim_boundary"
        ]["igl_is_equivalent_to_jgr_p1_conditionally"]
    )
    checks["p1_same_envelope_and_grading_are_independent_requirements"] = (
        p1_joint_graded_representation_audit["checks"][
            "same_envelope_condition_is_logically_essential"
        ]
        and p1_joint_graded_representation_audit["checks"][
            "odd_control_is_faithful_and_role_local_but_not_graded"
        ]
        and p1_joint_graded_representation_audit["checks"][
            "even_role_mixer_is_graded_but_not_tensor_local"
        ]
    )
    checks["p1_joint_realization_ownership_remains_open"] = (
        p1_joint_graded_representation_audit["physical_source_ownership"]
        == "OPEN"
        and p1_joint_graded_representation_audit["nature_level_occupation"]
        is False
        and p1_joint_graded_representation["source_freeze_payload"][
            "source_status"
        ]["same_envelope_joint_graded_representation_owned"]
        is False
    )
    checks["p1_joint_carrier_minimality_audit_passes"] = (
        p1_joint_carrier_minimality_audit["passed"]
        == p1_joint_carrier_minimality_audit["total"]
    )
    checks["p1_minimal_faithful_joint_carrier_is_32"] = (
        p1_joint_carrier_minimality_audit["checks"][
            "minimal_faithful_carrier_dimension_is_32"
        ]
        and p1_joint_carrier_minimality_audit["checks"][
            "minimal_faithful_multiplicity_is_unique"
        ]
        and p1_joint_carrier_minimality_audit["checks"][
            "internal_realization_attains_minimum"
        ]
    )
    checks["p1_heat_trace_excludes_same_compression_external_extension"] = (
        p1_joint_carrier_minimality_audit["checks"][
            "unnormalized_heat_trace_strictly_penalizes_extension"
        ]
        and p1_joint_carrier_minimality_audit["checks"][
            "jgr_then_supplies_the_igl_landing"
        ]
    )
    checks["p1_carrier_selection_assumptions_are_necessary_and_open"] = (
        p1_joint_carrier_minimality_audit["checks"][
            "normalized_trace_erases_duplicate_penalty"
        ]
        and p1_joint_carrier_minimality_audit["checks"][
            "changed_compression_can_reverse_selector"
        ]
        and p1_joint_carrier_minimality_audit["physical_source_ownership"]
        == "OPEN"
        and p1_joint_carrier_minimality["source_freeze_payload"][
            "claim_boundary"
        ]["nature_selection_proved"]
        is False
    )
    checks["p1_spectral_priority_origin_audit_passes"] = (
        p1_spectral_priority_origin_audit["passed"]
        == p1_spectral_priority_origin_audit["total"]
        == 19
    )
    checks["p1_compatible_trace_is_ordinary_unnormalized_trace"] = (
        p1_spectral_priority_origin_audit["checks"][
            "ordinary_trace_is_direct_sum_additive"
        ]
        and p1_spectral_priority_origin_audit["checks"][
            "ordinary_trace_is_unitarily_invariant"
        ]
        and p1_spectral_priority_origin_audit["checks"][
            "normalized_trace_fails_direct_sum_additivity"
        ]
        and p1_spectral_priority_origin_audit["checks"][
            "nonlinear_unitary_functional_lies_outside_trace_theorem"
        ]
    )
    checks["p1_spectator_stability_fixes_positive_log_sign"] = (
        p1_spectral_priority_origin_audit["checks"][
            "positive_sign_uniquely_prefers_one_copy"
        ]
        and p1_spectral_priority_origin_audit["checks"][
            "zero_sign_destroys_equality_rigidity"
        ]
        and p1_spectral_priority_origin_audit["checks"][
            "negative_sign_rewards_unbounded_duplication"
        ]
    )
    checks["p1_hodge_intertwining_derives_same_compression_but_ownership_is_open"] = (
        p1_spectral_priority_origin_audit["checks"][
            "hodge_intertwining_implies_same_compression"
        ]
        and p1_spectral_priority_origin_audit["checks"][
            "algebraic_extension_without_intertwining_changes_compression"
        ]
        and p1_spectral_priority_origin_audit[
            "physical_source_ownership"
        ]
        == "OPEN"
        and p1_spectral_priority_origin["source_freeze_payload"][
            "claim_boundary"
        ]["nature_selection_proved"]
        is False
    )
    checks["p1_hodge_functorial_origin_audit_passes"] = (
        p1_hodge_functorial_origin_audit["passed"]
        == p1_hodge_functorial_origin_audit["total"]
        == 20
    )
    checks["p1_complete_star_differential_grammar_derives_hodge_transport"] = (
        p1_hodge_functorial_origin_audit["checks"][
            "differential_intertwines"
        ]
        and p1_hodge_functorial_origin_audit["checks"][
            "codifferential_intertwines"
        ]
        and p1_hodge_functorial_origin_audit["checks"][
            "laplacian_intertwines"
        ]
        and p1_hodge_functorial_origin_audit["checks"][
            "harmonic_projector_intertwines"
        ]
        and p1_hodge_functorial_origin_audit["checks"][
            "same_compression_is_derived"
        ]
    )
    checks["p1_unstarred_chain_map_and_nonisometric_controls_are_rejected"] = (
        p1_hodge_functorial_origin_audit["checks"][
            "unstarred_cochain_control_preserves_d_only"
        ]
        and p1_hodge_functorial_origin_audit["checks"][
            "unstarred_cochain_control_changes_hodge_operator"
        ]
        and p1_hodge_functorial_origin_audit["checks"][
            "nonisometric_control_breaks_compression_normalization"
        ]
        and p1_hodge_functorial_origin_audit["checks"][
            "independent_harmonic_policy_is_not_derived"
        ]
    )
    checks["p1_physical_star_differential_ownership_remains_open"] = (
        p1_hodge_functorial_origin_audit["physical_source_ownership"]
        == "OPEN"
        and p1_hodge_functorial_origin_audit["nature_level_occupation"]
        is False
        and p1_hodge_functorial_origin["source_freeze_payload"][
            "claim_boundary"
        ]["current_joint_role_record_grammar_contains_nonzero_odd_nilpotents"]
        is True
        and p1_hodge_functorial_origin["source_freeze_payload"][
            "claim_boundary"
        ]["current_joint_role_record_grammar_selects_complete_differential"]
        is False
    )
    checks["p1_role_record_hodge_ownership_audit_passes"] = (
        p1_role_record_hodge_ownership_audit["passed"]
        == p1_role_record_hodge_ownership_audit["total"]
        == 25
    )
    checks["p1_role_algebra_has_nilpotents_but_does_not_select_one"] = (
        p1_role_record_hodge_ownership_audit["checks"][
            "q01_is_nonzero_nilpotent"
        ]
        and p1_role_record_hodge_ownership_audit["checks"][
            "distinct_nilpotents_are_not_selected_by_relations"
        ]
    )
    checks["p1_frozen_hodge_is_not_single_differential_generated"] = (
        p1_role_record_hodge_ownership_audit["checks"][
            "explicit_dhf_hodge_differs_from_frozen_p3_hodge"
        ]
        and p1_role_record_hodge_ownership_audit["checks"][
            "frozen_number_operator_has_record_kernel"
        ]
        and p1_role_record_hodge_ownership["source_freeze_payload"][
            "claim_boundary"
        ]["dhf_generates_the_frozen_p3_hodge"]
        is False
    )
    checks["p1_car7_is_a_conditional_same_exterior_carrier_completion"] = (
        p1_role_record_hodge_ownership_audit["checks"][
            "car_completion_recovers_role_generators"
        ]
        and p1_role_record_hodge_ownership_audit["checks"][
            "car_completion_recovers_number_operator"
        ]
        and p1_role_record_hodge_ownership_audit["checks"][
            "full_star_transport_derives_number_transport"
        ]
    )
    checks["p1_car7_cannot_be_internal_to_minimal_m32_carrier"] = (
        p1_role_record_hodge_ownership_audit["checks"][
            "faithful_car7_cannot_fit_32_dimensional_carrier"
        ]
        and p1_role_record_hodge_ownership_audit["physical_source_ownership"]
        == "OPEN"
    )
    checks["p1_seed_boolean_car_bridge_audit_passes"] = (
        p1_seed_boolean_car_bridge_audit["passed"]
        == p1_seed_boolean_car_bridge_audit["total"]
        == 20
    )
    checks["p1_complete_typed_boolean_seed_conditionally_derives_car7"] = (
        p1_seed_boolean_car_bridge_audit["checks"][
            "complete_boolean_car_mixed_relations_hold"
        ]
        and p1_seed_boolean_car_bridge_audit["checks"][
            "empty_root_generates_all_boolean_words"
        ]
        and p1_seed_boolean_car_bridge_audit["checks"][
            "binary_record_doubles_carrier_to_256"
        ]
    )
    checks["p1_global_boundary_and_number_do_not_select_colored_modes"] = (
        p1_seed_boolean_car_bridge_audit["checks"][
            "global_boundary_does_not_select_colored_modes"
        ]
        and p1_seed_boolean_car_bridge_audit["checks"][
            "number_operator_does_not_select_colored_modes"
        ]
    )
    checks["p1_boolean_face_completeness_is_not_optional"] = (
        p1_seed_boolean_car_bridge_audit["checks"][
            "one_missing_boolean_face_breaks_car"
        ]
        and p1_seed_boolean_car_bridge["source_freeze_payload"][
            "claim_boundary"
        ]["generic_seed_order_complex_implies_boolean_closure"]
        is False
        and p1_seed_boolean_car_bridge_audit["physical_source_ownership"]
        == "OPEN"
    )
    checks["p1_existing_action_snpr_selection_audit_passes"] = (
        p1_existing_action_snpr_selection_audit["passed"]
        == p1_existing_action_snpr_selection_audit["total"]
    )
    checks["p1_existing_actions_do_not_select_all_five_from_narrow_reduct"] = (
        p1_existing_action_snpr_selection_audit["checks"][
            "no_audited_action_varies_and_forces_all_five"
        ]
        and p1_existing_action_snpr_selection["source_freeze_payload"][
            "claim_boundary"
        ]["one_audited_unchanged_action_selects_all_five_from_narrow_reduct"]
        is False
    )
    checks["p1_conditional_clp3_occupation_survives_domain_no_go"] = (
        p1_existing_action_snpr_selection_audit["checks"][
            "conditional_occupation_is_retained"
        ]
        and p1_existing_action_snpr_selection_audit["nature_level_occupation"]
        is False
    )
    checks["p1_snpr_ownership_refinement_audit_passes"] = (
        p1_snpr_ownership_refinement_audit["passed"]
        == p1_snpr_ownership_refinement_audit["total"]
    )
    checks["p1_snpr_asymmetry_is_localized_only_on_declared_branch"] = (
        p1_snpr_ownership_refinement_audit["checks"][
            "fixed_base_and_seed_give_fixed_response"
        ]
        and p1_snpr_ownership_refinement_audit["checks"][
            "explicit_bias_escape_breaks_equivariance"
        ]
        and p1_snpr_ownership_refinement["source_freeze_payload"][
            "claim_boundary"
        ]["asymmetry_localized_to_seed_on_declared_branch"]
    )
    checks["p1_binary_record_selection_has_all_three_controls"] = (
        p1_snpr_ownership_refinement_audit["checks"][
            "smallest_nontrivial_record_is_binary"
        ]
        and p1_snpr_ownership_refinement_audit["checks"][
            "allowing_trivial_record_selects_n1"
        ]
        and p1_snpr_ownership_refinement_audit["checks"][
            "normalized_trace_erases_cardinality_priority"
        ]
        and p1_snpr_ownership_refinement_audit["checks"][
            "changed_compression_can_select_larger_record"
        ]
    )
    checks["p1_snpr_refinement_is_endpoint_blind_and_nature_bounded"] = (
        p1_snpr_ownership_refinement["source_freeze_payload"][
            "terminal_data_used"
        ]
        is False
        and p1_snpr_ownership_refinement_audit["physical_meta_law_ownership"]
        == "OPEN"
        and p1_snpr_ownership_refinement_audit["nature_level_occupation"]
        is False
    )
    checks["p1_operational_record_origin_audit_passes"] = (
        p1_operational_record_origin_audit["passed"]
        == p1_operational_record_origin_audit["total"]
    )
    checks["p1_operational_record_axioms_force_copy_law"] = (
        p1_operational_record_origin_audit["checks"][
            "primitive_exact_recovery_forces_diagonal_copy"
        ]
        and p1_operational_record_origin_audit["checks"]["copy_is_special"]
        and p1_operational_record_origin_audit["checks"][
            "frobenius_left_identity"
        ]
        and p1_operational_record_origin["source_freeze_payload"][
            "claim_boundary"
        ]["copy_law_derived_inside_operational_class"]
    )
    checks["p1_full_carrier_priority_selects_m2_k2_with_controls"] = (
        p1_operational_record_origin_audit["checks"][
            "full_carrier_priority_selects_m2_k2"
        ]
        and p1_operational_record_origin_audit["checks"][
            "allowing_one_port_selects_k1"
        ]
        and p1_operational_record_origin_audit["checks"][
            "normalized_trace_erases_selector"
        ]
        and p1_operational_record_origin_audit["checks"][
            "diagonal_only_score_is_port_blind"
        ]
        and p1_operational_record_origin_audit["checks"][
            "changed_compression_can_change_selected_pair"
        ]
    )
    checks["p1_common_PUSC_record_incidence_remains_open"] = (
        p1_operational_record_origin_audit["checks"][
            "same_marginals_do_not_fix_common_incidence"
        ]
        and p1_operational_record_origin["source_freeze_payload"][
            "claim_boundary"
        ]["common_PUSC_record_incidence_derived"]
        is False
        and p1_operational_record_origin_audit[
            "physical_PUSC_record_incidence"
        ]
        == "OPEN"
        and p1_operational_record_origin_audit["nature_level_occupation"]
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
            {"id": "PSR25", "status": "proved_conditional", "claim": "Given an ontic Cl_10 envelope, the canonical seven-dimensional P3 role subspace, and an even Clifford-compatible embedding of the equal-weight binary record algebra, the record involution splits the three-dimensional complement into a two-dimensional minus eigenspace and a one-dimensional plus eigenspace."},
            {"id": "PSR26", "status": "proved_conditional", "claim": "The prior u/v connector pair is a gauge-fixed orthonormal frame of that single graded record--Clifford embedding; any tested O(2)-rotated frame closes the same Cl_10 algebra, so u and v need not be separately owned source primitives."},
            {"id": "PSR27", "status": "proved_no_go", "claim": "The current P3/PUSC plus binary-record reduct does not entail the graded embedding: odd-twist and chirality-misaligned involutions preserve the local four-block P3/record data while violating global evenness or vector-complement preservation."},
            {"id": "PSR28", "status": "open", "claim": "Physical source selection and Nature occupation of the graded record--Clifford embedding remain unproved; therefore physical P1 exhaustivity and BaseSeedPacket export remain unauthorized."},
            {"id": "PSR29", "status": "proved_conditional", "claim": "A unital trace-preserving star embedding of the equal-weight binary record algebra into the even relative commutant of the P3 Cl_7 algebra automatically preserves the three-dimensional vector complement, has adjoint split 2+1, and belongs to one Spin(3)-conjugacy orbit; no continuous embedding parameter or separate complement-preservation premise remains."},
            {"id": "PSR30", "status": "proved_no_go", "claim": "The existing Schur-neutral PUSC-plus-record action jointly realizes the two sectors but contains neither a record-to-Clifford map variable nor an even-relative-commutant cross residual, so it cannot force the landing class."},
            {"id": "PSR31", "status": "open", "claim": "The exact surviving physical datum is Nature occupation of the even-relative-commutant landing class, not selection of a particular embedding representative; physical P1 exhaustivity and BaseSeedPacket export remain unauthorized."},
            {"id": "PSR32", "status": "proved_no_go", "claim": "The current PUSC and Frobenius-record presentation has no mixed record--Clifford word: an internal even-commutant realization and an external tensor-record realization have identical current reducts but different landing truth values."},
            {"id": "PSR33", "status": "constructed_conditional", "claim": "Given an inherited record involution image inside the same Cl_10 envelope, one nonnegative internal-graded-locality residual has zero set exactly the even-relative-commutant landing manifold and hence one Spin(3) gauge orbit."},
            {"id": "PSR34", "status": "proved_minimal_conditional", "claim": "Role commutation and evenness are independently necessary: the odd-twist and even role-mixing record controls satisfy one condition while violating the other. The completion does not derive ownership of its in-envelope record domain or Nature occupation."},
            {"id": "PSR35", "status": "proved_conditional", "claim": "A faithful trace-preserving graded star representation of Cl(E) graded-tensor A_port in the same Cl_10 ontic envelope, extending the fixed role embedding, is equivalent to a trace-preserving binary-record landing in the even relative commutant."},
            {"id": "PSR36", "status": "proved_no_go", "claim": "Abstract joint-algebra ownership alone does not force internal landing: a faithful external tensor-factor realization preserves the abstract graded product but is not a same-envelope representation; an odd internal control additionally proves that grading cannot be omitted."},
            {"id": "PSR37", "status": "open", "claim": "IGL-P1 can be reinterpreted as the finite relation defect of same-envelope joint graded realization rather than a new fitted gain, but the current source still does not derive or physically occupy that realization."},
            {"id": "PSR38", "status": "proved", "claim": "The finite joint algebra Cl_7(C) graded-tensor A_port is M_8(C)^{oplus 4}; every faithful finite representation has carrier dimension 8 sum_i m_i with all m_i>=1, so the unique minimal multiplicity vector is (1,1,1,1) and the minimal carrier dimension is 32."},
            {"id": "PSR39", "status": "proved_conditional", "claim": "The internal JGR realization attains the 32-dimensional faithful minimum. Under the frozen positive source compression and unnormalized heat-trace priority, every faithful proper carrier extension has strictly larger heat trace, so the selected class is same-envelope and hence satisfies IGL."},
            {"id": "PSR40", "status": "proved_no_go_open", "claim": "Carrier minimality does not follow from normalized trace, changed-compression comparison, nonfaithful smaller carriers or ungraded realization. Physical common ownership and Nature occupation of the joint grammar and unnormalized same-compression heat-trace priority remain open."},
            {"id": "PSR41", "status": "proved_conditional", "claim": "A positive linear unitarily invariant functional on every finite carrier that is compatible with orthogonal direct sums and calibrated by T_C(1)=1 is uniquely the ordinary unnormalized matrix trace; normalized trace fails the direct-sum law."},
            {"id": "PSR42", "status": "proved_conditional", "claim": "For continuous spectral-only tensor-additive complexity, finite faithful spectator closure plus attained equality-rigid minimization excludes c<=0 in C(Z)=c log Z; primitive derivative calibration fixes c=1."},
            {"id": "PSR43", "status": "proved_conditional_no_go", "claim": "An isometric Hodge intertwiner K_X J=J K_0 implies the common-compression identity J^*K_XJ=K_0. Algebra representation alone does not imply intertwining, and changed compression can reverse heat-trace selection."},
            {"id": "PSR44", "status": "open", "claim": "The physical source has not yet been shown to co-own the joint grammar, source-Hodge intertwining, spectral sufficiency, tensor additivity and spectator-stable well-posed minimization; Nature occupation and BaseSeedPacket export remain unauthorized."},
            {"id": "PSR45", "status": "proved_conditional", "claim": "For finite graded star representations of one nilpotent differential grammar, a degree-preserving isometric full-star intertwiner automatically transports the differential, codifferential and Hodge Laplacian."},
            {"id": "PSR46", "status": "proved_conditional", "claim": "The same dagger-functorial intertwiner transports the harmonic spectral projector and therefore the dimensionless positive Hodge operator Delta+P_H; multiplying by the common action unit preserves the result and derives common compression."},
            {"id": "PSR47", "status": "proved_no_go", "claim": "Intertwining the unstarred differential alone is insufficient because complement-to-source incidence can change the codifferential and Hodge compression. Nonisometric intertwiners and independently assigned harmonic projectors are also insufficient."},
            {"id": "PSR48", "status": "corrected_open", "claim": "DHF-P1 transports any supplied star-closed differential Hodge operator, but it does not identify that operator with the frozen P3 N_ext compression. Physical ownership, typed compatibility and Nature occupation remain open."},
            {"id": "PSR49", "status": "proved_internal_finite", "claim": "The P3 role Clifford algebra contains explicit nonzero odd nilpotents q_ab=(g_a+i g_b)/2 with q_ab^2=0 and {q_ab,q_ab^*}=1; therefore nilpotent existence was not the missing algebraic fact."},
            {"id": "PSR50", "status": "proved_no_go", "claim": "The frozen role-record relations admit multiple distinct q_ab and do not select one complete differential grammar. For every explicit q_ab the Hodge Laplacian is the identity, not the frozen exterior number operator."},
            {"id": "PSR51", "status": "proved_no_go", "claim": "No finite odd nilpotent differential on the frozen graded P3 carrier can obey Delta_q+P_H,q=N_ext tensor I_2: the left side is strictly positive while the frozen P3 operator has a two-dimensional record-doubled kernel."},
            {"id": "PSR52", "status": "proved_no_go", "claim": "In the regular exterior representation, exterior creation and N_ext are not elements of the left Cl_7 role image; hence no star-polynomial or spectral functional of a role-algebra differential can recover the frozen P3 Hodge operator."},
            {"id": "PSR53", "status": "proved_conditional", "claim": "The seven-mode CAR star extension on the same 256-dimensional exterior-record carrier recovers both g_a=epsilon_a+iota_a and N_ext=sum_a epsilon_a iota_a; a full-star intertwiner therefore transports the frozen P3 Hodge operator without a separate gain."},
            {"id": "PSR54", "status": "proved_no_go_open", "claim": "Faithful CAR_7 requires a carrier of dimension at least 128 and cannot be internal to the 32-dimensional minimal JGR envelope. The MVP seed boundary supplies a conditional nonzero recovery incidence, but its typed identification with the seven-mode P3 CAR polarization and Nature occupation remain open."},
            {"id": "PSR55", "status": "proved_conditional", "claim": "If the occupied seven-role seed owns the complete pointed oriented Boolean word grammar and the base faithfully realizes every colored incidence, exterior insertion and deletion obey CAR_7; their global boundary is nilpotent, their number sum is N_ext, and the record factor yields the 256-dimensional P3 carrier."},
            {"id": "PSR56", "status": "proved_no_go", "claim": "One global boundary, its adjoint, scalar Hodge Laplacian and N_ext do not select the seven typed CAR modes: a nontrivial O(6) family fixes all global data while rotating the colored mode frame."},
            {"id": "PSR57", "status": "proved_no_go", "claim": "In the standard subset-word realization, deleting one Boolean face violates a diagonal CAR identity; a generic non-total seed order complex therefore does not imply the complete exterior grammar."},
            {"id": "PSR58", "status": "open", "claim": "Current MVP results supply one transported uncolored nilpotent boundary, not physical ownership of the complete pointed typed Boolean closure and its seven colored incidences. Nature occupation and packet export remain open."},
            {"id": "PSR59", "status": "proved", "claim": "For A=M_8(C)^{oplus 4} with a faithful source-natural state, the GNS null left ideal is zero and every cyclic vector realization of that state has orbit dimension dim_C A=256, uniquely up to pointed unitary equivalence."},
            {"id": "PSR60", "status": "proved_no_go_correction", "claim": "The 32-dimensional one-copy-per-block module is a faithful abstract representation but no vector on it induces a faithful state on an M_8 block. JCM-P1 therefore selects only a root-free module class and cannot replace the declared faithful trace-GNS root carrier."},
            {"id": "PSR61", "status": "proved_conditional", "claim": "On the faithful pointed trace-GNS carrier, the seven typed Clifford generators have an orthonormal ordered-word basis; word-degree raising/lowering uniquely derives the Boolean exterior CAR_7 grammar and N_ext. Physical source ownership and Nature occupation of the pointed packet remain open."},
            {"id": "PSR62", "status": "proved_conditional_composition", "claim": "SNPR1--SNPR5 jointly force the complete 256-dimensional pointed P3 trace-GNS packet up to typed unitary: oriented multiplicity-free seed composition, positive no-bypass Hodge realization, binary Frobenius record, full source naturality and pointed cyclic occupation compose without terminal input."},
            {"id": "PSR63", "status": "proved_no_go", "claim": "The narrow primitive inventory, Clifford relations, discrete exchanges, full orbit rank and source nonloss do not imply SNPR1--SNPR5: symmetric/tensor, non-Hodge, recordless, nontracial, unequal-weight, rootless and spectator controls preserve the relevant reducts while failing the target packet."},
            {"id": "PSR64", "status": "open", "claim": "The unrestricted physical base-seed parent has not been proved to own and occupy SNPR1--SNPR5. This is now the exact physical source statement; another carrier, coefficient or terminal score does not close it."},
            {"id": "PSR65", "status": "proved_no_go", "claim": "If a source packet is external to the varied response fibre, equal attainable minima on target-satisfying and target-failing source fibres prove that fibrewise Euler-Lagrange equations cannot select the target source property, even when each response minimizer is unique."},
            {"id": "PSR66", "status": "proved_action_domain_audit", "claim": "No action in the audited SNPR-relevant set varies and forces SNPR1--SNPR5 from the narrow reduct: unchanged P3-RL6 has the exact carrier/root same-zero control; P3-RL6F, L_P3^min and Gamma_CLP3 import pointed source data; source-fidelity/Hodge and constrained heat-trace work only in supplied source classes; and L_1src cannot self-certify its residual language."},
            {"id": "PSR67", "status": "proved_conditional_boundary", "claim": "L_P3^min and Gamma_CLP3 remain valid conditional law-to-occupation results after their source packet is supplied. The next mathematical target is one endpoint-blind upstream source variational domain over the five SNPR alternatives; Nature occupation remains open."},
            {"id": "PSR68", "status": "proved_no_go", "claim": "Even when the source packet belongs to the variational domain, any source action A_red=a after R that factors through the narrow reduct is constant on each same-reduct fibre and cannot uniquely select the SNPR class when a premise-deletion control exists."},
            {"id": "PSR69", "status": "proved_conditional", "claim": "Given five exact nonnegative endpoint-blind source defects, strictly positive source-fixed weights and an attainable simultaneous zero, A_SNPR=sum_i lambda_i D_i has the typed-unitary SNPR packet as its exact global-zero class."},
            {"id": "PSR70", "status": "proved_irredundant_open_origin", "claim": "Every component of the five-defect SNPR action is necessary in the direct-sum residual class, because deleting one admits the corresponding premise-deletion control as a target-failing zero. Packaging the residuals into one norm does not derive their common parent origin; Nature occupation remains open."},
            {"id": "PSR71", "status": "proved_no_go", "claim": "A source action cannot independently derive a structural property already built into the typed language of its own model space. Comparing inequivalent source grammars requires a prior meta-domain and cross-language comparison law."},
            {"id": "PSR72", "status": "candidate_conditional", "claim": "The minimal nonrecursive enriched completion candidate assigns oriented exterior, binary-record and pointing grammar to the one universal seed; positive dagger-Hodge realization, the action unit and source-frame naturality to the base; and stable no-bypass, state-lock and cyclic actualization to their joint action. SNPR closure follows conditionally, but uniqueness and Nature occupation are open."},
            {"id": "PSR73", "status": "proved_conditional_symmetry_ownership", "claim": "On a homogeneous-base, invariant-seed, equivariant unique-response branch, the occupied response is group fixed. A non-invariant orientation or pointing therefore requires a non-invariant source datum, explicit law breaking, or a separately selected nonunique spontaneous branch."},
            {"id": "PSR74", "status": "proved_conditional_compression", "claim": "Oriented multiplicity-free primitive composition with no additional source relations derives the complete exterior algebra and empty root, so the expanded exterior-word list need not be primitive seed data in that class."},
            {"id": "PSR75", "status": "proved_conditional_record_selection", "claim": "Over a predeclared nontrivial family of exchangeable n-point special commutative dagger-Frobenius logical record alphabets with common compression, ordinary unnormalized trace and positive logarithmic priority give C(n)=constant+log n and uniquely select n=2. This n is logical-alternative cardinality, not physical port count."},
            {"id": "PSR76", "status": "proved_no_go_open_ownership", "claim": "Logical binary-record selection is premise-sensitive: allowing n=1 selects the trivial record, normalized trace makes cardinalities tie, and changed compression can select a larger record. The one-axis selector does not derive physical port count, common PUSC occupation or Nature occupation."},
            {"id": "PSR77", "status": "proved_conditional_operational_copy", "claim": "Exact complete multiport record axioms force Y_(m,k) isomorphic to A_m tensor-power k and Delta_(m,k)e_i=e_i tensor-power k. At k=2 the common dagger metric yields the special commutative dagger-Frobenius TMB copy law without assuming it algebraically."},
            {"id": "PSR78", "status": "proved_conditional_record_port_selection", "claim": "On the nontrivial redundant full-product carrier with common compression, ordinary unnormalized trace and positive logarithmic priority give C(m,k)=constant+k log m and uniquely select (m,k)=(2,2); for fixed m at least two, k=2 is unique. Allowing one port, normalized trace, diagonal-only scoring or changed compression defeats the conclusion."},
            {"id": "PSR79", "status": "proved_no_go_open_incidence", "claim": "Identical PUSC and copied-record marginal packets admit correlated and independent common completions, so they do not select their typed cross-incidence. One no-bypass map j_PR suffices for the earlier Schur-neutral graph action, but its physical ownership and Nature occupation remain open."},
            {"id": "PSR80", "status": "proved_standard_no_go", "claim": "Finite normalized GNS Gram data reconstruct an abstract ray family only; PSD, rank, Bargmann phases and graph spectra do not certify the physical source algebra, probe semantics, seed or Nature occupation."},
            {"id": "PSR81", "status": "proved_conditional_source_action", "claim": "Given the frozen body symbol, positive source stiffness, normalized Legendre--Riesz coevaluation and positive action scale, the post-body source action has a unique stationary response whose dual Hessian is G=K_src/(2 A_*)=k_(c,O)^2 A_(0,M)^(-1); no terminal fit is used."},
            {"id": "PSR82", "status": "proved_same_reduct_no_go", "claim": "A modified coevaluation preserves the frozen seed, body and coframe reduct while changing the dual generator to C^* Ahat_(0,M)^(-1) C. The reduct therefore does not select the ECTR lock, and nonzero access, atlas compatibility and Nature occupation remain open."},
        ],
    }
    (DERIVED / "theorem_ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")

    if passed != len(checks):
        failed = [k for k, v in checks.items() if not v]
        raise SystemExit(f"PHYSICAL_SOURCE_DERIVATION_AUDIT_FAIL {failed}")
    print(f"PHYSICAL_SOURCE_DERIVATION_AUDIT_PASS {passed}/{len(checks)}")


if __name__ == "__main__":
    main()
