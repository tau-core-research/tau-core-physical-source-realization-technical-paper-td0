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
    assert len(ledger["results"]) == 48


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
    assert audit["physical_source_ownership"] == "OPEN"


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
