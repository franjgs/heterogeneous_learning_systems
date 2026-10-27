"""Standard-library validation helpers for the single scientific catalog."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ENTITY_TYPES = {"scenario", "organization", "model", "policy", "evaluation", "study", "experiment", "result", "theoretical_result"}
REQUIRED = {"id", "type", "name", "definition", "scope", "assumptions", "relationships", "status"}
EXECUTION_STATUSES = {"PROPOSED", "IMPLEMENTED", "EXECUTED", "EVALUATED", "VALIDATED", "CLOSED", "SUSPENDED", "INVALIDATED", "PENDING"}
SCIENTIFIC_OUTCOMES = {"POSITIVE", "NEGATIVE", "NULL", "AMBIGUOUS", "INCONCLUSIVE", "INVALID", "NOT_EVALUATED"}
EVIDENCE_TYPES = {"formal_proof", "exact_computation", "confirmatory", "exploratory", "negative", "inconclusive", "technical_validation", "not_verified"}
EVIDENCE_MATURITY = {"current_reproducible", "historical_documentary", "incomplete", "implementation_reference_present", "not_independently_verified"}
RELATION_RANGES = {
    "uses": {"study": {"scenario", "organization", "model"}, "model": {"scenario"}, "experiment": {"policy"}},
    "evaluated_by": {"study": {"evaluation"}},
    "evaluated_in": {"organization": {"scenario"}},
    "compares": {"study": {"policy"}},
    "study": {"experiment": {"study"}, "result": {"study"}, "theoretical_result": {"study"}},
    "from": {"result": {"experiment"}},
    "from_study": {"result": {"study"}},
    "belongs_to": {"theoretical_result": {"study"}},
    "supports": {"experiment": {"theoretical_result"}},
    # Contextual lineage: a precedent informs a proposal without asserting
    # that the precedent is reused, equivalent, or direct evidence for it.
    "informed_by": {
        "scenario": {"study", "result", "theoretical_result"},
        "study": {"study", "result", "theoretical_result", "model"},
    },
}


def bibliography_keys(path: str | Path) -> tuple[set[str], list[str]]:
    """Read citation keys from a deliberately small, brace-balanced BibTeX file."""
    source = Path(path).read_text(encoding="utf-8")
    keys: set[str] = set()
    issues: list[str] = []
    cursor = 0
    pattern = re.compile(r"@([A-Za-z]+)\s*\{")
    while match := pattern.search(source, cursor):
        depth, quoted, escaped, end = 1, False, False, match.end()
        while end < len(source) and depth:
            char = source[end]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted and char == "{":
                depth += 1
            elif not quoted and char == "}":
                depth -= 1
            end += 1
        if depth:
            issues.append(f"unclosed BibTeX entry at character {match.start()}")
            break
        body = source[match.end():end - 1]
        key = body.split(",", 1)[0].strip()
        if not key or not re.fullmatch(r"[A-Za-z0-9:_-]+", key):
            issues.append(f"invalid BibTeX key at character {match.start()}")
        elif key in keys:
            issues.append(f"duplicate BibTeX key {key}")
        else:
            keys.add(key)
        cursor = end
    if not keys:
        issues.append("bibliography contains no BibTeX entries")
    if re.search(r"(?m)^\s*@\w+\s*\(", source):
        issues.append("BibTeX parenthesized entries are unsupported; use braces")
    return keys, issues


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
    bibliography = data.get("bibliography", {})
    bib_path = root / bibliography.get("path", "") if isinstance(bibliography, dict) else root / "__missing_bibliography__"
    if not isinstance(bibliography, dict) or not bibliography.get("path") or not bib_path.is_file():
        issues.append("catalog bibliography path is missing")
        bib_keys: set[str] = set()
    else:
        bib_keys, bib_issues = bibliography_keys(bib_path)
        issues.extend(bib_issues)
        if bibliography.get("format") != "BibTeX":
            issues.append("catalog bibliography format must be BibTeX")
        document = bibliography.get("document")
        if not isinstance(document, str) or not (root / document).is_file():
            issues.append("catalog literature document is missing")
    types_by_id = {item.get("id"): item.get("type") for item in entities if isinstance(item, dict)}
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
        if item.get("ontology_class") != item["type"]:
            issues.append(f"{item['id']}: ontology_class must match its catalog entity type")
        if item.get("evidence_maturity") not in EVIDENCE_MATURITY:
            issues.append(f"{item['id']}: invalid or missing evidence_maturity")
        refs = item.get("bibliography_refs", [])
        if not isinstance(refs, list):
            issues.append(f"{item['id']}: bibliography_refs must be a list")
        else:
            for key in refs:
                if key not in bib_keys:
                    issues.append(f"{item['id']}: unknown bibliography key {key}")
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
            elif relation["kind"] not in RELATION_RANGES:
                issues.append(f"{item['id']}: unknown relationship type {relation['kind']}")
            elif item["type"] not in RELATION_RANGES[relation["kind"]] or types_by_id.get(relation["target"]) not in RELATION_RANGES[relation["kind"]].get(item["type"], set()):
                issues.append(f"{item['id']}: invalid domain/range for {relation['kind']} -> {relation['target']}")
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
    documents = data.get("program", {}).get("documents", {})
    for name, path in documents.items():
        if not isinstance(path, str) or not (root / path).is_file():
            issues.append(f"program document {name} is missing: {path}")
    return issues
