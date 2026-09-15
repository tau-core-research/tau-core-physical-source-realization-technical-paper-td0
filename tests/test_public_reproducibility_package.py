from pathlib import Path
import json
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def test_publication_files_exist():
    for rel in [
        "physical_source_submission_source/main.tex",
        "physical_source_submission_source/refs.bib",
        "physical_source_submission_source/main.pdf",
        "figures/fig_physical_source_contract.pdf",
        "data/derived/interface_contract.json",
        "data/derived/theorem_ledger.json",
        "data/derived/derivation_audit.json",
        "data/derived/p3_clp3_complete_seed_presentation.json",
        "data/derived/p3_clp3_instantiation_audit.json",
        "data/derived/p3_clp3_p1_ambient_certificate.json",
        "data/derived/p3_clp3_p1_ambient_certificate_audit.json",
        "data/derived/p3_clp3_p1_source_envelope_separator.json",
        "data/derived/p3_clp3_p1_source_envelope_separator_audit.json",
        "data/derived/p3_clp3_p1_envelope_connector_selector.json",
        "data/derived/p3_clp3_p1_envelope_connector_selector_audit.json",
        "data/derived/p3_clp3_p1_record_clifford_embedding.json",
        "data/derived/p3_clp3_p1_record_clifford_embedding_audit.json",
        "data/derived/p3_clp3_p1_record_clifford_landing.json",
        "data/derived/p3_clp3_p1_record_clifford_landing_audit.json",
        "data/derived/p3_clp3_p1_record_clifford_source_completion.json",
        "data/derived/p3_clp3_p1_record_clifford_source_completion_audit.json",
        "data/derived/p3_clp3_p1_joint_graded_representation.json",
        "data/derived/p3_clp3_p1_joint_graded_representation_audit.json",
        "data/derived/p3_clp3_p1_joint_carrier_minimality.json",
        "data/derived/p3_clp3_p1_joint_carrier_minimality_audit.json",
        "data/derived/p3_clp3_p1_spectral_priority_origin.json",
        "data/derived/p3_clp3_p1_spectral_priority_origin_audit.json",
        "data/derived/p3_clp3_p1_hodge_functorial_origin.json",
        "data/derived/p3_clp3_p1_hodge_functorial_origin_audit.json",
        "data/derived/p3_clp3_p1_role_record_hodge_ownership.json",
        "data/derived/p3_clp3_p1_role_record_hodge_ownership_audit.json",
        "data/derived/p3_clp3_p1_seed_boolean_car_bridge.json",
        "data/derived/p3_clp3_p1_seed_boolean_car_bridge_audit.json",
        "data/derived/p3_clp3_p1_trace_gns_booleanization.json",
        "data/derived/p3_clp3_p1_trace_gns_booleanization_audit.json",
        "data/derived/p3_clp3_p1_source_natural_pointed_realization.json",
        "data/derived/p3_clp3_p1_source_natural_pointed_realization_audit.json",
        "data/derived/p3_clp3_p1_existing_action_snpr_selection.json",
        "data/derived/p3_clp3_p1_existing_action_snpr_selection_audit.json",
        "data/derived/p3_clp3_p1_snpr_upstream_joint_action.json",
        "data/derived/p3_clp3_p1_snpr_upstream_joint_action_audit.json",
        "data/derived/p3_clp3_p1_snpr_ownership_refinement.json",
        "data/derived/p3_clp3_p1_snpr_ownership_refinement_audit.json",
        "data/derived/p3_clp3_p1_operational_record_origin.json",
        "data/derived/p3_clp3_p1_operational_record_origin_audit.json",
        "data/derived/p3_clp3_single_source_law.json",
        "data/derived/p3_clp3_single_source_law_audit.json",
        "arxiv_submission_source.zip",
        "THEOREM_AUDIT.md",
        "DEPENDENCY_LEDGER.md",
        "DATA_NOTICE.md",
    ]:
        assert (ROOT / rel).exists(), rel


def test_claim_ledger_is_bounded():
    ledger = json.loads((ROOT / "data/derived/theorem_ledger.json").read_text())
    assert ledger["nature_level_validation"] is False
    assert ledger["unrestricted_parent_selection_derived"] is False
    assert ledger["empirical_data_used"] is False
    assert len(ledger["results"]) == 82


def test_p3_clp3_source_freeze_is_endpoint_blind_and_bounded():
    packet = json.loads(
        (ROOT / "data/derived/p3_clp3_complete_seed_presentation.json").read_text()
    )
    payload = packet["source_freeze_payload"]
    assert payload["terminal_data_used"] is False
    assert payload["endpoint_fitted_parameters"] == []
    assert payload["complete_seed_presentation"]["quotient_algebra"]["complex_dimension"] == 256
    assert payload["conditional_base_seed_packet_candidate"]["physical_export_authorized"] is False
    assert payload["claim_boundary"]["nature_seed_selection"] is False
    assert payload["claim_boundary"]["nature_occupation"] is False


def test_p3_clp3_instantiation_audit_passes():
    audit = json.loads(
        (ROOT / "data/derived/p3_clp3_instantiation_audit.json").read_text()
    )
    assert audit["passed"] == audit["total"]
    assert audit["total"] >= 28
    assert audit["nature_level_occupation"] is False
    assert audit["physical_base_seed_packet_export_authorized"] is False


def test_single_source_law_compresses_p4_p7_but_not_p1():
    law = json.loads(
        (ROOT / "data/derived/p3_clp3_single_source_law.json").read_text()
    )
    audit = json.loads(
        (ROOT / "data/derived/p3_clp3_single_source_law_audit.json").read_text()
    )
    boundary = law["source_freeze_payload"]["claim_boundary"]
    assert audit["passed"] == audit["total"]
    assert audit["total"] >= 20
    assert audit["verdict"] == "P4_P7_SINGLE_ACTION_COMPRESSION_PASS"
    assert boundary["single_action_compresses_P4_through_P7_conditionally"] is True
    assert boundary["P1_self_certified_by_the_action"] is False
    assert audit["nature_level_occupation"] is False


def test_p1_independent_ambient_certificate_is_conditional_and_bounded():
    certificate = json.loads(
        (ROOT / "data/derived/p3_clp3_p1_ambient_certificate.json").read_text()
    )
    audit = json.loads(
        (ROOT / "data/derived/p3_clp3_p1_ambient_certificate_audit.json").read_text()
    )
    payload = certificate["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 18
    assert audit["verdict"] == "CONDITIONAL_P1_AMBIENT_RANK_THEOREM_PASS"
    assert audit["checks"]["same_component_missing_relation_is_detected"]
    assert audit["checks"]["hidden_component_fails_global_ambient_rank"]
    assert payload["finite_control_realization"][
        "ambient_derived_independently_of_seed_candidate"
    ] is False
    assert audit["physical_P1_certificate_eligible"] is False
    assert audit["P1_physical_exhaustivity_proved"] is False


def test_p1_source_envelope_separator_retypes_global_exhaustivity():
    packet = json.loads(
        (ROOT / "data/derived/p3_clp3_p1_source_envelope_separator.json").read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_source_envelope_separator_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 21
    assert audit["verdict"] == (
        "P3_COMPONENT_COMPLETE_GLOBAL_P1_FAILS_IF_PREBODY_ENVELOPE_IS_ONTIC"
    )
    assert audit["diagnostics"]["p3_component_algebra_dimension"] == 256
    assert audit["diagnostics"]["prebody_pusc_algebra_dimension"] == 1024
    assert audit["diagnostics"]["prebody_rank_ratio"] == 0.25
    assert payload["downstream_control_only"][
        "eligible_as_upstream_p1_ambient"
    ] is False
    assert audit["nature_level_ambient_choice"] == "OPEN"
    assert audit["physical_P1_exhaustivity_proved"] is False


def test_p1_envelope_connector_selector_is_exact_and_claim_bounded():
    packet = json.loads(
        (ROOT / "data/derived/p3_clp3_p1_envelope_connector_selector.json").read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_envelope_connector_selector_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 24
    assert audit["verdict"] == (
        "TWO_CONNECTOR_ONTIC_PUSC_COMPLETION_PASS_NATURE_SELECTION_OPEN"
    )
    assert audit["diagnostics"]["algebra_dimensions"] == {
        "p3_only": 256,
        "p3_plus_u": 512,
        "p3_plus_v": 512,
        "p3_plus_u_and_v": 1024,
    }
    assert audit["diagnostics"]["good_connector_defect"] == 0.0
    assert audit["diagnostics"]["zero_u_defect"] > 0.0
    assert payload["ontology_decision"][
        "simple_m32_has_no_nontrivial_star_ideal_for_a_p3_null_quotient"
    ] is True
    assert audit["physical_connector_ownership"] == "OPEN"
    assert audit["physical_P1_exhaustivity_proved"] is False


def test_p1_record_clifford_embedding_reduces_primitives_but_not_ownership():
    packet = json.loads(
        (ROOT / "data/derived/p3_clp3_p1_record_clifford_embedding.json").read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_record_clifford_embedding_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 31
    assert audit["verdict"] == (
        "CONNECTOR_PAIR_REDUCED_TO_ONE_GRADED_RECORD_CLIFFORD_EMBEDDING_"
        "CURRENT_SOURCE_SELECTION_OPEN"
    )
    assert audit["diagnostics"]["good_adjoint_eigenvalues"] == [
        -1.0,
        -1.0,
        1.0,
    ]
    assert audit["checks"]["local_reduct_does_not_entail_graded_embedding"]
    assert payload["conditional_consequence"][
        "connector_variables_are_independent_primitives"
    ] is False
    assert audit["physical_record_clifford_embedding_ownership"] == "OPEN"
    assert audit["nature_level_occupation"] is False


def test_p1_record_clifford_landing_is_one_gauge_orbit_but_not_source_owned():
    packet = json.loads(
        (ROOT / "data/derived/p3_clp3_p1_record_clifford_landing.json").read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_record_clifford_landing_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 17
    assert audit["checks"][
        "even_relative_commutant_has_no_hidden_clifford_words"
    ]
    assert audit["checks"]["valid_embedding_set_is_one_spin3_orbit"]
    assert audit["checks"]["even_landing_automatically_preserves_W"]
    assert audit["checks"][
        "current_joint_action_contains_no_cross_landing_equation"
    ]
    assert payload["automatic_consequences"][
        "separate_vector_preservation_premise_required"
    ] is False
    assert audit["physical_source_ownership"] == "OPEN"
    assert audit["nature_level_occupation"] is False


def test_p1_record_clifford_source_completion_is_minimal_and_bounded():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_record_clifford_source_completion.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_record_clifford_source_completion_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 18
    assert audit["verdict"] == (
        "CURRENT_SOURCE_NONENTAILMENT_PROVED_"
        "MINIMAL_INTERNAL_GRADED_LOCALITY_COMPLETION_CONSTRUCTED"
    )
    assert audit["checks"][
        "internal_and_external_models_share_the_current_reduct"
    ]
    assert audit["checks"]["both_cross_components_are_logically_necessary"]
    assert audit["checks"]["sampled_spin3_orbit_has_zero_joint_defect"]
    assert payload["conditional_positive_completion"][
        "new_dimensionless_fit_parameter"
    ] is False
    assert payload["claim_boundary"]["current_source_derives_IGL_P1"] is False
    assert audit["physical_source_ownership"] == "OPEN"
    assert audit["nature_level_occupation"] is False


def test_p1_joint_graded_representation_retypes_igl_but_not_ownership():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_joint_graded_representation.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_joint_graded_representation_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 19
    assert audit["verdict"] == (
        "IGL_EQUIVALENT_TO_SAME_ENVELOPE_JOINT_GRADED_REPRESENTATION_"
        "PHYSICAL_OWNERSHIP_OPEN"
    )
    assert audit["diagnostics"]["internal_joint_image_rank"] == 256
    assert audit["diagnostics"]["external_joint_image_rank"] == 256
    assert audit["checks"]["same_envelope_condition_is_logically_essential"]
    assert audit["checks"][
        "odd_control_is_faithful_and_role_local_but_not_graded"
    ]
    assert payload["equivalence_theorem"][
        "new_independent_dynamical_coefficient"
    ] is False
    assert audit["physical_source_ownership"] == "OPEN"
    assert audit["nature_level_occupation"] is False


def test_p1_joint_carrier_minimality_selects_internality_conditionally():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_joint_carrier_minimality.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_joint_carrier_minimality_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 18
    assert audit["verdict"] == (
        "SAME_ENVELOPE_SELECTED_BY_JOINT_CARRIER_MINIMALITY_"
        "UNDER_FROZEN_HEAT_TRACE_ASSUMPTIONS_PHYSICAL_OWNERSHIP_OPEN"
    )
    assert audit["diagnostics"]["minimal_faithful_carrier_dimension"] == 32
    assert audit["diagnostics"]["minimal_multiplicity_cases"] == [
        [1, 1, 1, 1]
    ]
    assert audit["diagnostics"]["heat_trace_ratio"] == 2.0
    assert audit["checks"][
        "normalized_trace_erases_duplicate_penalty"
    ]
    assert audit["checks"]["changed_compression_can_reverse_selector"]
    assert payload["claim_boundary"][
        "same_envelope_follows_under_selection_assumptions"
    ] is True
    assert audit["physical_source_ownership"] == "OPEN"
    assert audit["nature_level_occupation"] is False


def test_p1_spectral_priority_has_structural_origin_but_open_ownership():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_spectral_priority_origin.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_spectral_priority_origin_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 19
    assert audit["checks"][
        "normalized_trace_fails_direct_sum_additivity"
    ]
    assert audit["checks"][
        "nonlinear_unitary_functional_lies_outside_trace_theorem"
    ]
    assert audit["checks"][
        "positive_sign_uniquely_prefers_one_copy"
    ]
    assert audit["checks"][
        "hodge_intertwining_implies_same_compression"
    ]
    assert audit["checks"][
        "changed_compression_can_reverse_heat_trace_selection"
    ]
    assert payload["conditional_consequence"][
        "separate_choice_of_unnormalized_trace_needed"
    ] is False
    assert payload["claim_boundary"]["nature_selection_proved"] is False
    assert audit["physical_source_ownership"] == "OPEN"


def test_p1_hodge_transport_is_dagger_functorial_but_not_yet_owned():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_hodge_functorial_origin.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_hodge_functorial_origin_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 20
    assert audit["checks"]["differential_intertwines"]
    assert audit["checks"]["codifferential_intertwines"]
    assert audit["checks"]["harmonic_projector_intertwines"]
    assert audit["checks"]["same_compression_is_derived"]
    assert audit["checks"][
        "unstarred_cochain_control_changes_hodge_operator"
    ]
    assert audit["checks"][
        "nonisometric_control_breaks_compression_normalization"
    ]
    assert payload["conditional_consequence"][
        "separate_hodge_intertwining_axiom_needed"
    ] is False
    assert payload["claim_boundary"][
        "physical_source_owns_complete_star_differential_grammar"
    ] is False
    assert payload["claim_boundary"][
        "current_joint_role_record_grammar_contains_nonzero_odd_nilpotents"
    ] is True
    assert payload["claim_boundary"][
        "dhf_hodge_identified_with_frozen_p3_hodge"
    ] is False
    assert audit["physical_source_ownership"] == "OPEN"


def test_role_record_nilpotents_do_not_generate_the_frozen_p3_hodge():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_role_record_hodge_ownership.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_role_record_hodge_ownership_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 25
    assert audit["checks"]["q01_is_nonzero_nilpotent"]
    assert audit["checks"]["distinct_nilpotents_are_not_selected_by_relations"]
    assert audit["checks"]["explicit_dhf_hodge_differs_from_frozen_p3_hodge"]
    assert audit["checks"]["exterior_creation_is_not_in_left_role_image"]
    assert audit["checks"]["number_operator_is_not_in_left_role_image"]
    assert audit["checks"]["car_completion_recovers_number_operator"]
    assert audit["checks"]["faithful_car7_cannot_fit_32_dimensional_carrier"]
    assert payload["claim_boundary"]["dhf_generates_the_frozen_p3_hodge"] is False
    assert payload["claim_boundary"]["physical_source_owns_car7_completion"] is False
    assert audit["physical_source_ownership"] == "OPEN"


def test_seed_boolean_closure_conditionally_refines_mvp_boundary_to_car7():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_seed_boolean_car_bridge.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_seed_boolean_car_bridge_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 20
    assert audit["checks"]["complete_boolean_car_mixed_relations_hold"]
    assert audit["checks"]["global_boundary_is_nilpotent"]
    assert audit["checks"]["empty_root_generates_all_boolean_words"]
    assert audit["checks"]["binary_record_doubles_carrier_to_256"]
    assert audit["checks"]["global_boundary_does_not_select_colored_modes"]
    assert audit["checks"]["number_operator_does_not_select_colored_modes"]
    assert audit["checks"]["one_missing_boolean_face_breaks_car"]
    assert payload["claim_boundary"][
        "current_physical_seed_owns_complete_typed_boolean_closure"
    ] is False
    assert audit["physical_source_ownership"] == "OPEN"


def test_trace_gns_root_forces_256_and_derives_boolean_car7():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_trace_gns_booleanization.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_trace_gns_booleanization_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 22
    assert audit["diagnostics"]["abstract_minimal_faithful_module_dimension"] == 32
    assert audit["diagnostics"]["root_preserving_dimension_lower_bound"] == 256
    assert audit["checks"]["one_copy_vector_state_is_rank_one_and_nonfaithful"]
    assert audit["checks"]["four_block_trace_gns_orbit_has_rank_256"]
    assert audit["checks"]["degree_split_recovers_each_clifford_generator"]
    assert audit["checks"]["degree_split_obeys_mixed_car"]
    assert audit["checks"]["degree_split_recovers_exterior_number"]
    assert payload["claim_boundary"]["narrow_old_bare_tau_owns_trace_gns_root"] is False
    assert audit["physical_source_ownership"] == "OPEN"


def test_source_natural_pointed_packet_composes_all_internal_p3_steps():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_source_natural_pointed_realization.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_source_natural_pointed_realization_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 24
    assert audit["checks"]["finite_inner_frame_twirl_is_normalized_trace"]
    assert audit["checks"]["transitive_block_exchange_equalizes_weights"]
    assert audit["checks"]["nontracial_control_fails_inner_frame_naturality"]
    assert audit["checks"]["unequal_central_weights_fail_block_exchange"]
    assert audit["checks"]["spectator_extension_breaks_no_bypass_occupation"]
    assert audit["checks"]["typed_clifford_degree_recovers_boolean_car"]
    assert payload["composition_theorem"]["status"] == "proved_conditional_composition"
    assert payload["claim_boundary"]["physical_parent_owns_SNPR1_to_SNPR5"] is False
    assert audit["physical_source_ownership"] == "OPEN"


def test_existing_action_audit_separates_occupation_from_source_selection():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_existing_action_snpr_selection.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_existing_action_snpr_selection_audit.json"
        ).read_text()
    )
    payload = packet["source_freeze_payload"]
    assert audit["passed"] == audit["total"] == 14
    assert audit["checks"]["equal_floor_does_not_select_external_source_label"]
    assert audit["checks"]["no_audited_action_varies_and_forces_all_five"]
    assert audit["checks"]["conditional_occupation_is_retained"]
    assert payload["action_coverage"]["Gamma_CLP3"] == ["fixed_input"] * 5
    assert payload["claim_boundary"][
        "one_audited_unchanged_action_selects_all_five_from_narrow_reduct"
    ] is False
    assert audit["physical_source_ownership"] == "OPEN"


def test_upstream_joint_action_closes_zero_set_but_not_common_origin():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_snpr_upstream_joint_action.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_snpr_upstream_joint_action_audit.json"
        ).read_text()
    )
    boundary = packet["source_freeze_payload"]["claim_boundary"]
    assert audit["passed"] == audit["total"] == 11
    assert audit["checks"]["reduct_factored_action_is_constant_on_the_fibre"]
    assert audit["checks"][
        "full_joint_action_has_only_the_all_premise_zero_pattern"
    ]
    assert audit["checks"]["every_component_is_irredundant"]
    assert boundary["common_source_variational_domain_constructed"] is True
    assert boundary["defects_derived_from_one_parent_operator"] is False
    assert audit["primitive_common_origin"] == "OPEN"
    assert audit["nature_level_occupation"] is False


def test_snpr_ownership_refinement_is_conditional_and_controlled():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_snpr_ownership_refinement.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_snpr_ownership_refinement_audit.json"
        ).read_text()
    )
    boundary = packet["source_freeze_payload"]["claim_boundary"]
    assert audit["passed"] == audit["total"] == 15
    assert audit["checks"]["Z2_response_is_equivariant"]
    assert audit["checks"]["fixed_base_and_seed_give_fixed_response"]
    assert audit["checks"]["smallest_nontrivial_record_is_binary"]
    assert audit["checks"]["allowing_trivial_record_selects_n1"]
    assert audit["checks"]["normalized_trace_erases_cardinality_priority"]
    assert audit["checks"]["changed_compression_can_select_larger_record"]
    assert boundary["full_exterior_word_list_is_primitive_seed_data"] is False
    assert boundary["physical_record_copy_law_derived"] is False
    assert audit["physical_meta_law_ownership"] == "OPEN"
    assert audit["nature_level_occupation"] is False


def test_operational_record_origin_is_typed_conditional_and_bounded():
    packet = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_operational_record_origin.json"
        ).read_text()
    )
    audit = json.loads(
        (
            ROOT
            / "data/derived/p3_clp3_p1_operational_record_origin_audit.json"
        ).read_text()
    )
    boundary = packet["source_freeze_payload"]["claim_boundary"]
    assert audit["passed"] == audit["total"] == 21
    assert audit["checks"]["primitive_exact_recovery_forces_diagonal_copy"]
    assert audit["checks"]["copy_is_coassociative"]
    assert audit["checks"]["frobenius_left_identity"]
    assert audit["checks"]["full_carrier_priority_selects_m2_k2"]
    assert audit["checks"]["diagonal_only_score_is_port_blind"]
    assert audit["checks"]["same_marginals_do_not_fix_common_incidence"]
    assert boundary["copy_law_derived_inside_operational_class"] is True
    assert boundary["operational_class_physically_owned"] is False
    assert boundary["common_PUSC_record_incidence_derived"] is False
    assert audit["nature_level_occupation"] is False


def test_derivation_audit_passes():
    audit = json.loads((ROOT / "data/derived/derivation_audit.json").read_text())
    assert audit["passed"] == audit["total"]
    assert audit["total"] >= 18
    assert audit["nature_level_closure"] is False


def test_interface_contract():
    contract = json.loads((ROOT / "data/derived/interface_contract.json").read_text())
    assert contract["module"] == "TD-0"
    assert contract["consumes"] == "CompleteSeedPresentation"
    assert contract["produces"] == "BaseSeedPacket"
    assert contract["terminal_fit_allowed"] is False


def test_manuscript_scope_markers():
    tex = (ROOT / "physical_source_submission_source/main.tex").read_text()
    assert "Tau Core Physical Source Realization" in tex
    assert "Nature-level" in tex and "occupation remains open" in tex
    assert "Mixed-Hessian response reduction and the vertical-jet boundary" in tex
    assert "\\Gamma:=D_YZ_*=-H^{-1}B" in tex
    assert "p_s\\Gamma\\vert_{\\ker DF}=0" in tex
    assert "positivity, common mediation, no-anchor structure and Schur neutrality" in tex
    assert "Generalized internal-measurement source boundary" in tex
    assert "eq:td0-generalized-backaction-source" in tex
    assert "same-context and clamped-target" in tex
    assert "reselect the already frozen morphological body" in tex
    forbidden = ["Tau Core is proven", "empirically validates Tau Core", "Nature necessarily selects"]
    assert all(item not in tex for item in forbidden)


def test_standalone_repository_metadata_and_dependency_boundary():
    readme = (ROOT / "README.md").read_text()
    citation = (ROOT / "CITATION.cff").read_text()
    ledger = (ROOT / "DEPENDENCY_LEDGER.md").read_text()
    assert "tau-core-physical-source-realization-technical-paper-td0" in readme
    assert "No checkout of the central theory repository is required" in readme
    assert "repository-code:" in citation
    assert "P1 source-language exhaustivity" in ledger
    assert "Foundation Paper IV" in ledger
    assert "Nature occupation" in ledger


def test_arxiv_zip_is_source_only():
    with zipfile.ZipFile(ROOT / "arxiv_submission_source.zip") as zf:
        names = zf.namelist()
    assert "main.tex" in names
    assert "refs.bib" in names
    assert "figures/fig_physical_source_contract.pdf" in names
    assert not any(name.endswith("main.pdf") for name in names)
    assert not any(name.endswith((".aux", ".log", ".out")) for name in names)


def test_ectr_legendre_riesz_source_boundary():
    tex = (ROOT / "physical_source_submission_source/main.tex").read_text()
    assert "ECTR Legendre--Riesz source completion and non-selection" in tex
    assert "eq:td0-ectr-dual-lock" in tex
    assert "eq:td0-ectr-control" in tex
    ledger = json.loads((ROOT / "data/derived/theorem_ledger.json").read_text())
    ids = {item["id"] for item in ledger["results"]}
    assert {"PSR81", "PSR82"} <= ids
