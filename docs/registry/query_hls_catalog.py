#!/usr/bin/env python3
"""Validate and query the HLS scenario/domain catalogue and scientific registry."""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs/registry/hls_scientific_registry.jsonl"
CATALOG = ROOT / "docs/registry/hls_scenario_catalog.json"
COMPONENTS = ROOT / "docs/registry/hls_component_catalog.json"
VALIDATOR = ROOT / "docs/registry/validate_hls_scientific_registry.py"
_SPEC = importlib.util.spec_from_file_location("hls_registry_validator", VALIDATOR)
assert _SPEC and _SPEC.loader
_validator = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_validator)


def load() -> tuple[dict, list[dict], list[dict]]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    records = [json.loads(line) for line in REGISTRY.read_text(encoding="utf-8").splitlines() if line.strip()]
    research = [x for x in records if x.get("record_type") == "research"]
    results = [x for x in records if x.get("record_type") == "result"]
    return catalog, research, results


def validate_catalog(catalog: dict, research: list[dict], results: list[dict]) -> list[str]:
    errors: list[str] = []
    if catalog.get("schema_version") != "1.0" or catalog.get("catalog_type") != "hls_scientific_scenario_catalog":
        errors.append("unsupported scenario-catalog schema or catalog_type")
    research_by_id = {x["id"]: x for x in research}
    result_by_id = {x["id"]: x for x in results}
    scenarios = catalog.get("scenarios")
    domains = catalog.get("domains")
    if not isinstance(scenarios, list) or not isinstance(domains, list):
        return errors + ["catalog scenarios and domains must be arrays"]
    expected_domains = {
        "structure_of_capabilities", "organization_and_assignment",
        "learning_and_evolution", "complementarity_and_cooperation",
        "adaptation_and_uncertainty", "evaluation_and_methodology",
    }
    classification_values = {
        "independent_scenario", "scenario_family", "scenario_suite",
        "parametric_variant", "benchmark", "composite_reference",
        "scenario_reference",
    }
    documentation_values = {"documented", "partial"}
    scenario_by_id: dict[str, dict] = {}
    for scenario in scenarios:
        sid = scenario.get("scenario_id")
        if not isinstance(sid, str) or not sid:
            errors.append("scenario has missing scenario_id")
            continue
        if sid in scenario_by_id:
            errors.append(f"duplicate scenario_id: {sid}")
        scenario_by_id[sid] = scenario
        if scenario.get("classification") not in classification_values:
            errors.append(f"{sid}: unknown scenario classification {scenario.get('classification')!r}")
        if scenario.get("documentation_status") not in documentation_values:
            errors.append(f"{sid}: invalid documentation_status")
        if not isinstance(scenario.get("missing_dimensions"), list):
            errors.append(f"{sid}: missing_dimensions must be an array")
        if scenario.get("variant_of") is not None and not isinstance(scenario.get("variant_of"), str):
            errors.append(f"{sid}: variant_of must be a scenario ID or null")
        for field in ("research_refs", "experiment_families", "result_refs", "source_refs", "models", "organizations", "policies", "limitations", "reusability_evidence", "missing_dimensions"):
            if not isinstance(scenario.get(field), list):
                errors.append(f"{sid}: {field} must be an array")
        for field in ("uncertainty", "parameters", "evaluation"):
            if field not in scenario:
                errors.append(f"{sid}: {field} must be explicit or null")
            if scenario.get(field) is None and field not in scenario.get("missing_dimensions", []):
                errors.append(f"{sid}: unknown {field} must be listed as missing")
        for rid in scenario.get("research_refs", []):
            if rid not in research_by_id:
                errors.append(f"{sid}: unknown experiment/research reference {rid}")
        if scenario.get("reusability") == "verified_reused":
            evidence = scenario.get("reusability_evidence", [])
            if not evidence or any(item not in research_by_id for item in evidence):
                errors.append(f"{sid}: verified reuse requires valid research evidence")
        expected_families = {
            family for rid in scenario.get("research_refs", []) if rid in research_by_id
            for family in (research_by_id[rid].get("audit_experiment_families") or [])
        }
        if set(scenario.get("experiment_families", [])) != expected_families:
            errors.append(f"{sid}: experiment_families differ from the linked canonical research records")
        for result_id in scenario.get("result_refs", []):
            if result_id not in result_by_id:
                errors.append(f"{sid}: unknown result reference {result_id}")
            elif result_by_id[result_id]["research_id"] not in scenario.get("research_refs", []):
                errors.append(f"{sid}: result {result_id} belongs to an unlinked research")
        for source in scenario.get("source_refs", []):
            path = source.get("path") if isinstance(source, dict) else None
            if not path or not (ROOT / path).is_file():
                errors.append(f"{sid}: missing source path {path!r}")
        for path in scenario.get("code_and_protocol_refs", []):
            if not isinstance(path, str) or not (ROOT / path).exists():
                errors.append(f"{sid}: missing code/protocol path {path!r}")
    for sid, scenario in scenario_by_id.items():
        parent = scenario.get("variant_of")
        if parent is not None and parent not in scenario_by_id:
            errors.append(f"{sid}: unknown variant parent {parent}")
    domain_ids: set[str] = set()
    domain_cover: Counter[str] = Counter()
    for domain in domains:
        did = domain.get("domain_id")
        if not isinstance(did, str) or not did:
            errors.append("domain has missing domain_id")
            continue
        if did in domain_ids:
            errors.append(f"duplicate domain_id: {did}")
        domain_ids.add(did)
        for rid in domain.get("research_refs", []):
            if rid not in research_by_id:
                errors.append(f"{did}: unknown research reference {rid}")
            domain_cover[rid] += 1
        for sid in domain.get("scenario_refs", []):
            if sid not in scenario_by_id:
                errors.append(f"{did}: unknown scenario reference {sid}")
    if domain_ids != expected_domains:
        errors.append(f"domain set mismatch: missing={sorted(expected_domains-domain_ids)}, unknown={sorted(domain_ids-expected_domains)}")
    for rid in research_by_id:
        if not domain_cover[rid]:
            errors.append(f"research missing domain classification: {rid}")
    for rid in research_by_id:
        source_refs = research_by_id[rid].get("scenario_refs") or []
        catalog_refs = {
            s.get("registry_scenario_ref") for s in scenarios
            if rid in s.get("research_refs", []) and s.get("registry_scenario_ref")
        }
        if set(source_refs) != catalog_refs:
            errors.append(f"{rid}: catalog scenario references differ from the canonical registry")
    refs_seen: dict[str, str] = {}
    for sid, scenario in scenario_by_id.items():
        ref = scenario.get("registry_scenario_ref")
        if ref is not None:
            if ref in refs_seen:
                errors.append(f"duplicate registry scenario reference {ref!r}: {refs_seen[ref]} and {sid}")
            refs_seen[ref] = sid
    catalog_results = [result_id for s in scenarios for result_id in s.get("result_refs", [])]
    expected = {rid for s in scenarios for rid in s.get("result_refs", [])}
    observed = set(catalog_results)
    if observed != expected:
        errors.append(f"scenario result coverage mismatch: missing={sorted(expected-observed)}, unknown={sorted(observed-expected)}")
    duplicates = sorted(result_id for result_id, count in Counter(catalog_results).items() if count > 1)
    if duplicates:
        errors.append(f"results linked more than once; review scenario decomposition: {duplicates}")
    return errors


def report() -> dict:
    catalog, research, results = load()
    base = _validator.validate_registry(REGISTRY, ROOT)
    errors = validate_catalog(catalog, research, results)
    if not base["valid"]:
        errors.extend(base["summary"]["errors"])
    scenarios = catalog["scenarios"]
    documented = scenarios
    completeness = Counter(s.get("documentation_status", "missing") for s in scenarios)
    classifications = Counter(s.get("classification", "missing") for s in scenarios)
    models = {m for r in research for m in (r.get("model_refs") or [])}
    organizations = {o for r in research for o in (r.get("organization_refs") or [])}
    return {
        "valid": not errors,
        "summary": {
            "scenario_records": len(scenarios),
            "documented_scenarios_or_suites": len(documented),
            "research_without_scenario": sorted({r["id"] for r in research} - {rid for s in scenarios for rid in s["research_refs"]}),
            "scenario_documentation_status": dict(sorted(completeness.items())),
            "scenario_classification": dict(sorted(classifications.items())),
            "incompletely_documented_scenarios": [
                {"id": s["scenario_id"], "label": s["label"], "missing": s.get("missing_dimensions", [])}
                for s in scenarios if s.get("documentation_status") != "documented"
            ],
            "models_referenced": len(models),
            "organizations_referenced": len(organizations),
            "domains": {d["domain_id"]: len(d["research_refs"]) for d in catalog["domains"]},
            "research_covered": len({r for s in scenarios for r in s["research_refs"]}),
            "research_total": len(research),
            "results_covered_by_scenarios": len(set(x for s in scenarios for x in s["result_refs"])),
            "results_total": len(results),
            "base_registry": base["summary"],
            "errors": errors,
        },
    }


def validate_component_catalog(data: dict, research: list[dict], results: list[dict], scenarios: list[dict]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "1.0" or data.get("catalog_type") != "hls_component_graph":
        errors.append("unsupported component-catalog schema or catalog_type")
    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return errors + ["component catalog nodes and edges must be arrays"]
    node_ids = [n.get("id") for n in nodes]
    if len(node_ids) != len(set(node_ids)):
        errors.append("duplicate component node id")
    by_id = {n.get("id"): n for n in nodes}
    allowed_kinds = {"research", "result", "scenario", "organization", "model", "policy", "evaluation", "protocol", "experiment", "theory", "application"}
    for node in nodes:
        if node.get("kind") not in allowed_kinds:
            errors.append(f"{node.get('id')}: unknown component kind")
        for path in node.get("source_refs", []):
            if not (ROOT / path).is_file():
                errors.append(f"{node.get('id')}: missing source {path}")
        if node.get("kind") == "result" and node.get("research_id") not in {r["id"] for r in research}:
            errors.append(f"{node.get('id')}: missing research parent")
    for edge in edges:
        if edge.get("source") not in by_id or edge.get("target") not in by_id:
            errors.append(f"edge has unknown endpoint: {edge}")
    expected_research = {f"research:{r['id']}" for r in research}
    expected_results = {f"result:{r['id']}" for r in results}
    expected_scenarios = {f"scenario:{s['scenario_id']}" for s in scenarios}
    for kind, expected in (("research", expected_research), ("result", expected_results), ("scenario", expected_scenarios)):
        observed = {n["id"] for n in nodes if n.get("kind") == kind}
        if observed != expected:
            errors.append(f"{kind} node coverage mismatch: missing={sorted(expected-observed)}, extra={sorted(observed-expected)}")
    edge_pairs = {(e.get("source"), e.get("relation"), e.get("target")) for e in edges}
    scenario_by_ref = {s.get("registry_scenario_ref"): s["scenario_id"] for s in scenarios if s.get("registry_scenario_ref")}
    for record in research:
        rid = record["id"]
        research_node = by_id.get(f"research:{rid}", {})
        for field in ("research_status", "evidence_status", "question", "hypotheses", "limitations"):
            if research_node.get(field) != record.get(field):
                errors.append(f"research:{rid}: graph field {field} differs from registry")
        for sid in record.get("scenario_refs") or []:
            scenario_id = scenario_by_ref.get(sid)
            if scenario_id is None or (f"research:{rid}", "uses_scenario", f"scenario:{scenario_id}") not in edge_pairs:
                errors.append(f"research:{rid}: missing scenario edge {sid}")
        for field, rel, kind in (("model_refs", "uses_model", "model"), ("organization_refs", "uses_organization", "organization"), ("policy_refs", "uses_policy", "policy"), ("protocol_refs", "uses_protocol", "protocol"), ("audit_experiment_families", "contains_experiment_family", "experiment"), ("theory_ledger_refs", "references_theory_result", "theory"), ("application_refs", "potential_application", "application")):
            for label in record.get(field) or []:
                target = next((n["id"] for n in nodes if n.get("kind") == kind and n.get("label") == label), None)
                if target is None or (f"research:{rid}", rel, target) not in edge_pairs:
                    errors.append(f"research:{rid}: missing {kind} edge for {label}")
        for result_id in record.get("result_refs") or []:
            if (f"research:{rid}", "has_result", f"result:{result_id}") not in edge_pairs:
                errors.append(f"research:{rid}: missing result edge {result_id}")
    for result in results:
        if (f"result:{result['id']}", "evidence_for", f"research:{result['research_id']}") not in edge_pairs:
            errors.append(f"result:{result['id']}: missing research evidence edge")
        result_node = by_id.get(f"result:{result['id']}", {})
        for field in ("result_kind", "outcome_class", "estimand", "value", "uncertainty", "conditions", "artifact_availability", "raw_artifact_status", "artifact_refs"):
            if result_node.get(field) != result.get(field):
                errors.append(f"result:{result['id']}: graph field {field} differs from registry")
        if result_node.get("limitations") != result.get("scope_and_nonclaims"):
            errors.append(f"result:{result['id']}: graph limitations differ from registry")
        for label in result.get("theory_ledger_refs") or []:
            target = next((n["id"] for n in nodes if n.get("kind") == "theory" and n.get("label") == label), None)
            if target is None or (f"result:{result['id']}", "supported_by_theory_reference", target) not in edge_pairs:
                errors.append(f"result:{result['id']}: missing theory-reference edge for {label}")
    expected_experiments = {x for r in research for x in (r.get("audit_experiment_families") or [])}
    expected_theory = {x for r in research + results for x in (r.get("theory_ledger_refs") or [])}
    expected_applications = {x for r in research for x in (r.get("application_refs") or [])}
    for kind, expected in (("experiment", expected_experiments), ("theory", expected_theory), ("application", expected_applications)):
        observed = {n.get("label") for n in nodes if n.get("kind") == kind}
        if observed != expected:
            errors.append(f"{kind} reference coverage mismatch: missing={sorted(expected-observed)}, extra={sorted(observed-expected)}")
    for kind, field in (("model", "model_refs"), ("organization", "organization_refs"), ("policy", "policy_refs"), ("protocol", "protocol_refs")):
        expected = {label for r in research for label in (r.get(field) or [])}
        observed = {n.get("label") for n in nodes if n.get("kind") == kind}
        if observed != expected:
            errors.append(f"{kind} reference coverage mismatch: missing={sorted(expected-observed)}, extra={sorted(observed-expected)}")
    expected_evaluations = {r.get("estimand") for r in results if r.get("estimand") is not None}
    observed_evaluations = {n.get("label") for n in nodes if n.get("kind") == "evaluation"}
    if observed_evaluations != expected_evaluations:
        errors.append(f"evaluation reference coverage mismatch: missing={sorted(expected_evaluations-observed_evaluations)}, extra={sorted(observed_evaluations-expected_evaluations)}")
    actual_counts = Counter(n.get("kind") for n in nodes)
    if data.get("counts") != dict(sorted(actual_counts.items())):
        errors.append("component counts do not match nodes")
    for scenario in scenarios:
        node = by_id.get(f"scenario:{scenario['scenario_id']}", {})
        for field in ("classification", "definition", "agents", "tasks", "capabilities", "dynamics", "constraints", "uncertainty", "parameters", "evaluation", "organizations", "models", "policies", "experiment_families", "result_refs", "evidence_kinds", "evidence_availability", "limitations", "reusability", "reusability_evidence", "documentation_status", "missing_dimensions"):
            if node.get(field) != scenario.get(field):
                errors.append(f"scenario:{scenario['scenario_id']}: graph field {field} differs from scenario catalog")
    return errors


def query(args: argparse.Namespace) -> dict:
    catalog, research, results = load()
    domains = {d["domain_id"]: d for d in catalog["domains"]}
    scenarios = {s["scenario_id"]: s for s in catalog["scenarios"]}
    research_by_id = {r["id"]: r for r in research}
    matched_scenarios = list(scenarios.values())
    if args.scenario:
        matched_scenarios = [
            s for s in matched_scenarios
            if args.scenario.lower() in (
                s["scenario_id"] + " " + s["label"] + " " + " ".join(s["research_refs"])
            ).lower()
        ]
    if args.domain:
        if args.domain not in domains:
            raise SystemExit(f"unknown domain {args.domain!r}; choices: {', '.join(sorted(domains))}")
        ids = set(domains[args.domain]["scenario_refs"])
        matched_scenarios = [s for s in matched_scenarios if s["scenario_id"] in ids]
    research_ids = ({rid for s in matched_scenarios for rid in s["research_refs"]}
                    if args.scenario or args.domain else set(research_by_id))
    if args.experiment:
        research_ids &= {rid for rid in research_by_id if args.experiment.lower() in (rid+" "+research_by_id[rid]["name"]+" "+" ".join(research_by_id[rid].get("audit_experiment_families", []))).lower()}
    if args.model:
        research_ids = {rid for rid in research_ids if any(args.model.lower() in m.lower() for m in (research_by_id[rid].get("model_refs") or []))}
    if getattr(args, "organization", None):
        research_ids = {rid for rid in research_ids if any(args.organization.lower() in o.lower() for o in (research_by_id[rid].get("organization_refs") or []))}
    result_ids = {x["id"] for x in results if x["research_id"] in research_ids}
    if args.result:
        result_ids = {rid for rid in result_ids if args.result.lower() in (rid+" "+next(x["claim"] for x in results if x["id"]==rid)).lower()}
        research_ids &= {x["research_id"] for x in results if x["id"] in result_ids}
    return {
        "scenarios": [{"id":s["scenario_id"],"label":s["label"],"classification":s["classification"],"variant_of":s["variant_of"],"research_refs":[r for r in s["research_refs"] if r in research_ids],"experiment_families":s["experiment_families"],"result_refs":[r for r in s["result_refs"] if r in result_ids],"source_refs":s["source_refs"]} for s in matched_scenarios if any(r in research_ids for r in s["research_refs"])],
        "research": [research_by_id[r] for r in sorted(research_ids)],
        "results": [x for x in results if x["id"] in result_ids],
    }


def component_query(text: str) -> dict:
    graph = json.loads(COMPONENTS.read_text(encoding="utf-8"))
    hits = [n for n in graph["nodes"] if text.lower() in (n["id"] + " " + n["label"]).lower()]
    ids = {n["id"] for n in hits}
    return {"components": hits, "relations": [e for e in graph["edges"] if e["source"] in ids or e["target"] in ids]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="validate scenario/component catalogs and canonical research/result registry")
    parser.add_argument("--domain", help="filter by one of the six scientific domains")
    parser.add_argument("--scenario", help="case-insensitive scenario ID or label substring")
    parser.add_argument("--model", help="case-insensitive model-reference substring")
    parser.add_argument("--organization", help="case-insensitive organization-reference substring")
    parser.add_argument("--experiment", help="research ID or name substring")
    parser.add_argument("--result", help="result ID or claim substring")
    parser.add_argument("--component", help="case-insensitive component ID or label in the cross-reference graph")
    args = parser.parse_args(argv)
    if args.validate:
        result = report()
    elif any((args.domain,args.scenario,args.model,args.organization,args.experiment,args.result,args.component)):
        result = query(args)
    else:
        parser.error("use --validate or at least one query filter")
    if args.validate:
        component_data = json.loads(COMPONENTS.read_text(encoding="utf-8"))
        _, research, results = load()
        result["summary"]["component_catalog_errors"] = validate_component_catalog(component_data, research, results, json.loads(CATALOG.read_text(encoding="utf-8"))["scenarios"])
        result["summary"]["component_catalog_counts"] = component_data["counts"]
        result["summary"]["results_without_named_estimand"] = sorted(r["id"] for r in results if r.get("estimand") is None)
        result["valid"] = result["valid"] and not result["summary"]["component_catalog_errors"]
    elif getattr(args, "component", None):
        result = component_query(args.component)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not args.validate or result["valid"] else 1

if __name__ == "__main__":
    sys.exit(main())
