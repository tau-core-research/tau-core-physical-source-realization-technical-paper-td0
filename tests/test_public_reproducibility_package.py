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
    assert len(ledger["results"]) == 14


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
