import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs/registry/query_hls_catalog.py"
SPEC = importlib.util.spec_from_file_location("hls_catalog_query", SCRIPT)
assert SPEC and SPEC.loader
catalog_query = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog_query)


def args(**overrides):
    values = dict(domain=None, scenario=None, model=None, organization=None, experiment=None, result=None)
    values.update(overrides)
    return type("Args", (), values)()


def test_scenario_catalog_links_all_research_and_results():
    catalog, research, results = catalog_query.load()
    assert catalog_query.validate_catalog(catalog, research, results) == []
    summary = catalog_query.report()["summary"]
    assert summary["research_covered"] == 30
    assert summary["research_total"] == 33
    assert summary["results_covered_by_scenarios"] == 108
    assert summary["results_total"] == 112
    assert summary["documented_scenarios_or_suites"] == 30
    assert summary["research_without_scenario"] == [
        "CE05_COURSE_CORRECTION", "EXPERIMENTRUN_HLSPEF", "MINIMAL_HLS_OPV"
    ]


def test_variants_are_not_counted_as_independent_scenarios():
    catalog, _, _ = catalog_query.load()
    by_label = {s["label"]: s for s in catalog["scenarios"]}
    assert by_label["CE-04 synthetic H2 scenario at N=12 and N=48"]["classification"] == "parametric_variant"
    assert by_label["CE-04 synthetic N=24 workload; nine additional technical-pilot replications"]["classification"] == "parametric_variant"
    assert by_label["finite S4 and S7 fixtures with distinct compliance semantics"]["classification"] == "scenario_suite"


def test_queries_cover_domain_scenario_model_experiment_and_result():
    assert catalog_query.query(args(domain="structure_of_capabilities"))["research"]
    assert catalog_query.query(args(scenario="synthetic dynamic task queues"))["scenarios"]
    assert catalog_query.query(args(model="CE-04 discrete-event model"))["research"]
    assert catalog_query.query(args(experiment="CE07"))["research"][0]["id"] == "CE07"
    assert catalog_query.query(args(result="CE07_CONFIRMATORY_EFFECT"))["results"]
    assert catalog_query.query(args(experiment="CE05_COURSE_CORRECTION"))["research"]
    assert catalog_query.query(args(organization="H0/H1/H2"))["research"]


def test_component_graph_covers_all_research_and_result_records():
    import json
    graph=json.loads(catalog_query.COMPONENTS.read_text())
    catalog,research,results=catalog_query.load()
    assert catalog_query.validate_component_catalog(graph,research,results,catalog["scenarios"]) == []
    kinds=graph["counts"]
    assert kinds["research"]==33 and kinds["result"]==112
    assert kinds["scenario"]==30 and kinds["evaluation"]==53
    assert kinds["model"]==33 and kinds["organization"]==8 and kinds["policy"]==22
    assert kinds["experiment"]==32 and kinds["theory"]==21 and kinds["protocol"]==14
    assert kinds["application"]==1
    assert len([r for r in results if r.get("estimand") is None])==59


def test_component_query_returns_relations(capsys):
    result=catalog_query.component_query("CE-07")
    assert result["components"] and result["relations"]
    assert any(n["kind"]=="experiment" for n in result["components"])
    assert catalog_query.main(["--component","CE-07"])==0
    assert '"relations"' in capsys.readouterr().out
