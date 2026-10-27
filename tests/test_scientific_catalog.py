from pathlib import Path
import re

from hls.catalog import bibliography_keys, load_catalog, validate_catalog

ROOT = Path(__file__).resolve().parents[1]


def test_catalog_schema_references_aliases_and_files_are_valid():
    assert validate_catalog(load_catalog(ROOT / "registry/catalog.json"), ROOT) == []


def test_catalog_covers_each_scientific_entity_class():
    kinds = {entity["type"] for entity in load_catalog(ROOT / "registry/catalog.json")["entities"]}
    assert kinds == {"scenario", "organization", "model", "policy", "evaluation", "study", "experiment", "result", "theoretical_result"}


def test_primary_ids_are_descriptive_not_historical_campaign_labels():
    catalog = load_catalog(ROOT / "registry/catalog.json")
    ids = [entity["id"] for entity in catalog["entities"]]
    assert all(not re.search(r"(^|[._-])(CE-?0[0-9]|G[1-3]|S3b|RQ0|META-VOC|Campaign|B2\.3)([._-]|$)", value, re.I) for value in ids)
    for alias in ("CE-04", "CE-07", "G1", "G2", "G3/G3-H", "S3b", "META-VOC", "RQ0"):
        assert alias in catalog["aliases"]


def test_research_record_and_catalog_have_one_to_one_study_coverage():
    catalog = load_catalog(ROOT / "registry/catalog.json")
    registered = {item["id"] for item in catalog["entities"] if item["type"] == "study"}
    documented = set(re.findall(r"\*\*Stable ID:\*\* `([^`]+)`", (ROOT / "docs/RESEARCH.md").read_text()))
    assert registered == documented


def test_active_implementation_paths_use_scientific_names():
    historical = re.compile(r"(^|[._/-])(ce-?0[0-9]|g[1-3]|s3b|rq0|meta[-_]voc|campaign[-_ ]?[0-9]|b2[._-]3)([._/-]|$)", re.I)
    for base in (ROOT / "src", ROOT / "studies", ROOT / "tests"):
        for path in base.rglob("*"):
            assert not historical.search(path.relative_to(ROOT).as_posix()), path


def test_every_literature_citation_resolves_to_bibtex_key():
    keys, issues = bibliography_keys(ROOT / "references/hls.bib")
    assert issues == []
    text = "\n".join(path.read_text() for path in (ROOT / "docs").glob("*.md"))
    citations = set(re.findall(r"@([A-Za-z0-9:_-]+)", text))
    assert citations
    assert citations <= keys


def test_catalog_rejects_invalid_relation_domain_and_bibliography_key():
    catalog = load_catalog(ROOT / "registry/catalog.json")
    model = next(item for item in catalog["entities"] if item["type"] == "model")
    policy = next(item for item in catalog["entities"] if item["type"] == "policy")
    model["relationships"].append({"kind": "compares", "target": policy["id"]})
    model["bibliography_refs"].append("missing_reference")
    issues = validate_catalog(catalog, ROOT)
    assert any("invalid domain/range" in issue for issue in issues)
    assert any("unknown bibliography key" in issue for issue in issues)


def test_informed_by_links_context_without_claiming_direct_reuse():
    catalog = load_catalog(ROOT / "registry/catalog.json")
    scenario = next(item for item in catalog["entities"] if item["id"] == "scenario.soc_alert_operations")
    assert any(
        relation == {"kind": "informed_by", "target": "result.mean_preserving_composition_effect"}
        for relation in scenario["relationships"]
    )
    assert validate_catalog(catalog, ROOT) == []


def test_soc_testbed_is_a_proposal_with_separate_l1_and_l2_processes():
    catalog = load_catalog(ROOT / "registry/catalog.json")
    entities = {item["id"]: item for item in catalog["entities"]}
    scenario = entities["scenario.soc_alert_operations"]
    study = entities["study.soc_competence_heterogeneity_testbed"]
    assert [process["id"] for process in scenario["processes"]] == ["L1", "L2"]
    assert study["execution_status"] == "PROPOSED"
    assert study["scientific_outcome"] == "NOT_EVALUATED"
    assert study["hypothesis"] is None


def test_catalog_exposes_all_canonical_knowledge_documents():
    catalog = load_catalog(ROOT / "registry/catalog.json")
    assert set(catalog["program"]["documents"]) == {
        "philosophy", "doctrine", "ontology", "theory",
        "literature", "research", "history",
    }
    assert all((ROOT / path).is_file() for path in catalog["program"]["documents"].values())


def test_canonical_markdown_local_links_resolve():
    documents = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
    for source in documents:
        for target in re.findall(r"\]\(([^)]+)\)", source.read_text()):
            target = target.split("#", 1)[0].split("?", 1)[0]
            if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            assert (source.parent / target).exists(), f"{source.relative_to(ROOT)} -> {target}"
