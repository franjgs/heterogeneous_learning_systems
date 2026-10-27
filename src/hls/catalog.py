"""Standard-library validation helpers for the single scientific catalog."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ENTITY_TYPES = {"scenario", "organization", "model", "policy", "evaluation", "study", "experiment", "result", "theoretical_result"}
REQUIRED = {"id", "type", "name", "definition", "scope", "assumptions", "relationships", "status"}
EXECUTION_STATUSES = {"PROPOSED", "IMPLEMENTED", "EXECUTED", "EVALUATED", "VALIDATED", "CLOSED", "SUSPENDED", "INVALIDATED", "PENDING"}
SCIENTIFIC_OUTCOMES = {"POSITIVE", "NEGATIVE", "NULL", "AMBIGUOUS", "INCONCLUSIVE", "INVALID", "NOT_EVALUATED"}
EVIDENCE_TYPES = {"formal_proof", "exact_computation", "confirmatory", "exploratory", "negative", "inconclusive", "technical_validation", "not_verified"}


def load_catalog(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError("catalog root must be an object")
    return data


def validate_catalog(data: dict[str, Any], repository_root: str | Path) -> list[str]:
    issues: list[str] = []
    root = Path(repository_root)
    entities = data.get("entities")
    if not isinstance(entities, list):
        return ["entities must be a list"]
    ids: set[str] = set()
    for index, item in enumerate(entities):
        if not isinstance(item, dict):
            issues.append(f"entities[{index}] must be an object")
            continue
        missing = REQUIRED - item.keys()
        if missing:
            issues.append(f"entities[{index}] missing {sorted(missing)}")
            continue
        if item["type"] not in ENTITY_TYPES:
            issues.append(f"{item['id']}: unknown type {item['type']}")
        if not isinstance(item["id"], str) or not item["id"].startswith(item["type"] + "."):
            issues.append(f"{item['id']}: primary id must be descriptive and type-prefixed")
        if item["id"] in ids:
            issues.append(f"duplicate id {item['id']}")
        ids.add(item["id"])
        if not isinstance(item["assumptions"], list) or not isinstance(item["relationships"], list):
            issues.append(f"{item['id']}: assumptions and relationships must be lists")
        if item["type"] == "study":
            for field in ("research_question", "hypothesis", "start_date", "completion_date"):
                if field not in item:
                    issues.append(f"{item['id']}: missing study field {field}")
            if item.get("execution_status") not in EXECUTION_STATUSES:
                issues.append(f"{item['id']}: invalid or missing execution_status")
            if item.get("scientific_outcome") not in SCIENTIFIC_OUTCOMES:
                issues.append(f"{item['id']}: invalid or missing scientific_outcome")
            for field in ("start_date", "completion_date"):
                value = item.get(field)
                if value is not None and (not isinstance(value, str) or len(value) != 10 or value[4] != "-" or value[7] != "-"):
                    issues.append(f"{item['id']}: {field} must be an ISO date or null")
        if item["type"] == "result":
            if item.get("evidence_type") not in EVIDENCE_TYPES:
                issues.append(f"{item['id']}: invalid or missing evidence_type")
            if item.get("scientific_outcome") not in SCIENTIFIC_OUTCOMES:
                issues.append(f"{item['id']}: invalid or missing scientific_outcome")
            if not item.get("evidence_availability"):
                issues.append(f"{item['id']}: missing evidence_availability")
        if item["type"] == "scenario":
            contract = item.get("scenario_contract", {})
            required_scenario_fields = {"agents", "tasks", "capabilities", "dynamics", "constraints", "uncertainty"}
            if not required_scenario_fields <= contract.keys():
                issues.append(f"{item['id']}: incomplete scenario_contract")
        if item["type"] == "model":
            if not all(item.get(field) for field in ("mathematical_object", "inputs", "outputs")):
                issues.append(f"{item['id']}: model must state its mathematical object, inputs, and outputs")
        if item["type"] == "policy":
            if not all(item.get(field) for field in ("inputs", "outputs")):
                issues.append(f"{item['id']}: policy must state its inputs and outputs")
        for relation in item["relationships"]:
            if not isinstance(relation, dict) or not {"kind", "target"} <= relation.keys():
                issues.append(f"{item['id']}: malformed relationship")
            elif relation["target"] == item["id"]:
                issues.append(f"{item['id']}: self-reference is not allowed")
        for field in ("implementation", "evidence"):
            for ref in item.get(field, []):
                if ref.get("kind") == "local":
                    target = root / ref.get("path", "")
                    if not target.is_file():
                        issues.append(f"{item['id']}: missing local {field} {ref.get('path')}")
                elif ref.get("kind") != "historical":
                    issues.append(f"{item['id']}: unsupported {field} reference kind")
        for ref in item.get("historical_sources", []):
            if not all(ref.get(key) for key in ("branch", "commit", "path", "availability", "role")):
                issues.append(f"{item['id']}: incomplete historical source provenance")
        if item["type"] == "result" and not item.get("historical_sources") and not item.get("evidence"):
            issues.append(f"{item['id']}: result has no evidence provenance")
        if item["type"] == "result" and item.get("documented_in", {}).get("path") != "docs/RESEARCH.md":
            issues.append(f"{item['id']}: result missing its research-record location")
    for item in entities:
        if isinstance(item, dict):
            for relation in item.get("relationships", []):
                if isinstance(relation, dict) and relation.get("target") not in ids:
                    issues.append(f"{item.get('id')}: unresolved relation {relation.get('target')}")
    aliases = data.get("aliases", {})
    if not isinstance(aliases, dict):
        issues.append("aliases must be an object")
        aliases = {}
    for alias, record in aliases.items():
        if alias in ids:
            issues.append(f"alias {alias} duplicates primary identifier")
        if not isinstance(record, dict) or "targets" not in record:
            issues.append(f"alias {alias}: mapping must declare targets")
            continue
        for target in record["targets"]:
            if target not in ids:
                issues.append(f"alias {alias}: unresolved target {target}")
        if not record["targets"] and not record.get("resolution"):
            issues.append(f"alias {alias}: unresolved mapping must explain why")
    if data.get("version") != 1:
        issues.append("unsupported catalog version")
    if not isinstance(data.get("program"), dict) or not isinstance(data["program"].get("conceptual_levels"), list):
        issues.append("program conceptual levels are missing")
    return issues
