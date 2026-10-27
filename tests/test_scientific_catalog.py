from pathlib import Path
import re

from hls.catalog import load_catalog, validate_catalog

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
