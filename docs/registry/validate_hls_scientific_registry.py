#!/usr/bin/env python3
"""Validate the HLS research/result JSONL registry and print its coverage."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


RESEARCH_STATES = {"active", "closed", "suspended", "pending", "discarded"}
EVIDENCE_KINDS = {
    "formal_proof",
    "exact_computation",
    "confirmatory",
    "exploratory",
    "negative",
    "inconclusive",
    "technical_validation",
    "not_verified",
}
RECORD_TYPES = {"research", "result"}
ARTIFACT_STATES = {
    "tracked",
    "local_only",
    "partially_tracked",
    "external",
    "regenerable",
    "not_applicable",
    "not_verified",
    "missing",
}
RAW_ARTIFACT_STATES = {"tracked", "external", "local_only", "regenerable", "missing", "not_applicable", "not_verified"}

RESEARCH_REQUIRED = {
    "schema_version",
    "record_type",
    "id",
    "name",
    "question",
    "hypotheses",
    "scenario_refs",
    "organization_refs",
    "model_refs",
    "policy_refs",
    "protocol_refs",
    "research_status",
    "evidence_status",
    "limitations",
    "sources",
    "dates",
    "relations",
    "result_refs",
    "application_refs",
    "audit_experiment_families",
    "theory_ledger_refs",
}
RESULT_REQUIRED = {
    "schema_version",
    "record_type",
    "id",
    "research_id",
    "claim",
    "result_kind",
    "outcome_class",
    "estimand",
    "value",
    "uncertainty",
    "unit_of_analysis",
    "conditions",
    "sources",
    "configuration",
    "code_commit",
    "config_hash",
    "artifact_manifest",
    "raw_artifact_status",
    "artifact_availability",
    "artifact_refs",
    "scope_and_nonclaims",
    "theory_ledger_refs",
    "provenance",
}
SOURCE_REQUIRED = {"path", "section", "role"}
DATE_FIELDS = {"event", "decision", "execution_start", "execution_end", "recorded"}
RELATION_TYPES = {
    "reuses", "extends", "contrasts_with", "corroborates", "contradicts",
    "supersedes", "derived_from", "shares_components",
}
RESEARCH_LIST_FIELDS = {
    "hypotheses", "scenario_refs", "organization_refs", "model_refs",
    "policy_refs", "protocol_refs", "limitations", "sources", "relations",
    "result_refs", "application_refs", "audit_experiment_families",
    "theory_ledger_refs",
}
NULLABLE_RESEARCH_LIST_FIELDS = {
    "hypotheses", "scenario_refs", "organization_refs", "model_refs", "policy_refs",
}
RESULT_LIST_FIELDS = {"sources", "artifact_refs", "scope_and_nonclaims", "theory_ledger_refs"}


def _read_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        errors.append(f"cannot read registry {path}: {exc}")
        return records
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            errors.append(f"blank JSONL line at {number}")
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON at line {number}: {exc.msg}")
            continue
        if not isinstance(record, dict):
            errors.append(f"line {number} is not a JSON object")
            continue
        record["_line"] = number
        records.append(record)
    return records


def _load_csv_column(path: Path, column: str, errors: list[str]) -> set[str]:
    if not path.is_file():
        errors.append(f"coverage source is missing: {path}")
        return set()
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if column not in (reader.fieldnames or []):
                errors.append(f"coverage source {path} has no {column!r} column")
                return set()
            return {row[column] for row in reader if row.get(column)}
    except (OSError, csv.Error) as exc:
        errors.append(f"cannot read coverage source {path}: {exc}")
        return set()


def _git_tracked(root: Path, relative_path: str, cache: dict[str, bool]) -> bool:
    if relative_path not in cache:
        try:
            completed = subprocess.run(
                ["git", "ls-files", "--error-unmatch", "--", relative_path],
                cwd=root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            cache[relative_path] = completed.returncode == 0
        except OSError:
            cache[relative_path] = False
    return cache[relative_path]


def _validate_repository_references(
    record: dict[str, Any], fields: tuple[str, ...], root: Path, errors: list[str], allow_directories: bool = False
) -> None:
    for field in fields:
        values = record.get(field)
        if values is None and field in NULLABLE_RESEARCH_LIST_FIELDS:
            continue
        if not isinstance(values, list):
            continue  # The field-type diagnostic is emitted by the caller.
        for value in values:
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{record.get('id')}: {field} entries must be non-empty repository paths")
                continue
            path = Path(value)
            if path.is_absolute() or ".." in path.parts:
                errors.append(f"{record.get('id')}: {field} path must be repository-relative: {value!r}")
                continue
            target = root / path
            try:
                target.resolve().relative_to(root)
            except ValueError:
                errors.append(f"{record.get('id')}: {field} reference resolves outside repository: {value!r}")
                continue
            if not target.is_file() and not (allow_directories and target.is_dir()):
                errors.append(f"{record.get('id')}: referenced {field} path does not exist: {value}")


def _validate_dates(record: dict[str, Any], errors: list[str]) -> None:
    dates = record.get("dates")
    if not isinstance(dates, dict):
        errors.append(f"{record.get('id')}: dates must be an object")
        return
    missing = DATE_FIELDS - dates.keys()
    if missing:
        errors.append(f"{record.get('id')}: dates missing keys {sorted(missing)}")
        return
    parsed: dict[str, date] = {}
    for key in DATE_FIELDS:
        value = dates[key]
        if value is None:
            continue
        if not isinstance(value, str):
            errors.append(f"{record.get('id')}: date {key} must be ISO date or null")
            continue
        try:
            parsed[key] = date.fromisoformat(value)
        except ValueError:
            errors.append(f"{record.get('id')}: invalid ISO date {key}={value!r}")
    if "event" in parsed and "decision" in parsed and parsed["decision"] < parsed["event"]:
        errors.append(f"{record.get('id')}: decision date precedes event date")
    if (
        "execution_start" in parsed
        and "execution_end" in parsed
        and parsed["execution_end"] < parsed["execution_start"]
    ):
        errors.append(f"{record.get('id')}: execution end precedes execution start")


def _has_directional_cycle(research_records: list[dict[str, Any]]) -> bool:
    graph: dict[str, list[str]] = {}
    for record in research_records:
        source = record.get("id")
        if not isinstance(source, str):
            continue
        for relation in record.get("relations", []):
            if isinstance(relation, dict) and relation.get("type") in {"supersedes", "derived_from"}:
                target = relation.get("id")
                if isinstance(target, str):
                    graph.setdefault(source, []).append(target)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for child in graph.get(node, []):
            if visit(child):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def validate_registry(
    registry_path: Path,
    root: Path,
    experiment_matrix: Path | None = None,
    theory_ledger: Path | None = None,
) -> dict[str, Any]:
    """Return validation errors, warnings, and a generated coverage summary."""
    registry_path = registry_path.resolve()
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    records = _read_jsonl(registry_path, errors)
    ids: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            errors.append(f"line {record['_line']}: id must be a non-empty string")
            continue
        if record_id in ids:
            errors.append(f"duplicate id {record_id!r} on lines {ids[record_id]['_line']} and {record['_line']}")
        else:
            ids[record_id] = record

    research_records: list[dict[str, Any]] = []
    result_records: list[dict[str, Any]] = []
    source_tracking: dict[str, bool] = {}
    incomplete_references = 0
    for record in records:
        kind = record.get("record_type")
        if kind not in RECORD_TYPES:
            errors.append(f"{record.get('id')}: unrecognized record_type {kind!r}")
            continue
        required = RESEARCH_REQUIRED if kind == "research" else RESULT_REQUIRED
        absent = required - record.keys()
        if absent:
            errors.append(f"{record.get('id')}: missing fields {sorted(absent)}")
        if record.get("schema_version") != "1.0":
            errors.append(f"{record.get('id')}: unsupported schema_version {record.get('schema_version')!r}")
        if kind == "research":
            research_records.append(record)
            for field in RESEARCH_LIST_FIELDS:
                if field in record and not isinstance(record[field], list):
                    if not (field in NULLABLE_RESEARCH_LIST_FIELDS and record[field] is None):
                        errors.append(f"{record.get('id')}: {field} must be an array" + (" or null" if field in NULLABLE_RESEARCH_LIST_FIELDS else ""))
            if record.get("research_status") not in RESEARCH_STATES:
                errors.append(f"{record.get('id')}: invalid research_status {record.get('research_status')!r}")
            evidence = record.get("evidence_status")
            if not isinstance(evidence, list) or any(item not in EVIDENCE_KINDS for item in evidence):
                errors.append(f"{record.get('id')}: invalid evidence_status values")
            if record.get("question") is not None and not isinstance(record.get("question"), str):
                errors.append(f"{record.get('id')}: question must be text or null")
            _validate_dates(record, errors)
            _validate_repository_references(record, ("protocol_refs",), root, errors)
        else:
            result_records.append(record)
            for field in RESULT_LIST_FIELDS:
                if field in record and not isinstance(record[field], list):
                    errors.append(f"{record.get('id')}: {field} must be an array")
            if not isinstance(record.get("claim"), str) or not record.get("claim", "").strip():
                errors.append(f"{record.get('id')}: claim must be non-empty text")
            if record.get("result_kind") not in EVIDENCE_KINDS:
                errors.append(f"{record.get('id')}: invalid result_kind {record.get('result_kind')!r}")
            if record.get("artifact_availability") not in ARTIFACT_STATES:
                errors.append(f"{record.get('id')}: invalid artifact_availability")
            if record.get("raw_artifact_status") not in RAW_ARTIFACT_STATES:
                errors.append(f"{record.get('id')}: invalid raw_artifact_status")
            for field in ("configuration", "artifact_manifest"):
                path_value = record.get(field)
                if path_value is not None:
                    if not isinstance(path_value, str):
                        errors.append(f"{record.get('id')}: {field} must be a repository path or null")
                    else:
                        _validate_repository_references({"id": record.get("id"), field: [path_value]}, (field,), root, errors, allow_directories=True)
            for field in ("code_commit", "config_hash"):
                if record.get(field) is not None and not isinstance(record.get(field), str):
                    errors.append(f"{record.get('id')}: {field} must be text or null")
            if not isinstance(record.get("conditions"), dict):
                errors.append(f"{record.get('id')}: conditions must be an object")
            if not isinstance(record.get("provenance"), dict):
                errors.append(f"{record.get('id')}: provenance must be an object")
            else:
                provenance = record["provenance"]
                paired_fields = {
                    "code_commit": "code_commit",
                    "config_hash": "config_hash",
                    "configuration": "configuration_path",
                    "artifact_manifest": "manifest_path",
                }
                for record_field, provenance_field in paired_fields.items():
                    if record.get(record_field) != provenance.get(provenance_field):
                        errors.append(f"{record.get('id')}: {record_field} disagrees with provenance.{provenance_field}")
            _validate_repository_references(record, ("artifact_refs",), root, errors, allow_directories=True)

        sources = record.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{record.get('id')}: at least one source reference is required")
            incomplete_references += 1
            continue
        has_primary_accessible_source = False
        for source in sources:
            if not isinstance(source, dict) or SOURCE_REQUIRED - source.keys():
                errors.append(f"{record.get('id')}: malformed source reference")
                incomplete_references += 1
                continue
            if not isinstance(source.get("section"), str) or not source.get("section", "").strip():
                errors.append(f"{record.get('id')}: source section must be non-empty text")
            if source.get("role") not in {"primary", "supporting", "audit"}:
                errors.append(f"{record.get('id')}: invalid source role {source.get('role')!r}")
            path_value = source.get("path")
            if not isinstance(path_value, str) or Path(path_value).is_absolute() or ".." in Path(path_value).parts:
                errors.append(f"{record.get('id')}: source path must be a repository-relative path")
                continue
            target = root / path_value
            try:
                target.resolve().relative_to(root)
            except ValueError:
                errors.append(f"{record.get('id')}: source resolves outside repository root: {path_value}")
                continue
            if not target.is_file():
                errors.append(f"{record.get('id')}: source file does not exist: {path_value}")
                continue
            tracked = _git_tracked(root, path_value, source_tracking)
            if source.get("role") == "primary" and tracked:
                has_primary_accessible_source = True
            elif not tracked:
                warnings.append(f"{record.get('id')}: source exists locally but is not Git-tracked: {path_value}")
            if source.get("section") is None:
                incomplete_references += 1
        if kind == "result" and not has_primary_accessible_source:
            errors.append(f"{record.get('id')}: no Git-tracked primary source is accessible")

    research_ids = {record.get("id") for record in research_records}
    result_ids = {record.get("id") for record in result_records}
    for result in result_records:
        parent = result.get("research_id")
        if parent not in research_ids:
            errors.append(f"{result.get('id')}: unknown research_id {parent!r}")
        elif result.get("id") not in ids[parent].get("result_refs", []):
            errors.append(f"{result.get('id')}: parent {parent} does not list this result in result_refs")
    for research in research_records:
        for result_id in research.get("result_refs", []):
            if result_id not in result_ids:
                errors.append(f"{research.get('id')}: unknown result_ref {result_id!r}")
            elif ids[result_id].get("research_id") != research.get("id"):
                errors.append(f"{research.get('id')}: result_ref {result_id!r} points to another research")
        for relation in research.get("relations", []):
            if (
                not isinstance(relation, dict)
                or relation.get("id") not in research_ids
                or relation.get("type") not in RELATION_TYPES
            ):
                errors.append(f"{research.get('id')}: malformed or unknown research relation {relation!r}")
    if _has_directional_cycle(research_records):
        errors.append("directional research relations contain a cycle (supersedes/derived_from)")

    experiment_matrix = experiment_matrix or root / "docs/research/audits/HLS_EXPERIMENT_EVIDENCE_MATRIX_2026-10-26.csv"
    theory_ledger = theory_ledger or root / "docs/research/audits/HLS_THEORETICAL_RESULTS_LEDGER_2026-10-26.csv"
    expected_families = _load_csv_column(experiment_matrix, "line", errors)
    represented_families = {
        family
        for record in research_records
        for family in record.get("audit_experiment_families", [])
    }
    missing_families = sorted(expected_families - represented_families)
    expected_theory = _load_csv_column(theory_ledger, "result", errors)
    represented_theory = {
        label
        for record in research_records + result_records
        for label in record.get("theory_ledger_refs", [])
    }
    missing_theory = sorted(expected_theory - represented_theory)

    results_per_research = Counter(record.get("research_id") for record in result_records)
    research_status_counts = Counter(record.get("research_status") for record in research_records)
    evidence_counts = Counter(record.get("result_kind") for record in result_records)
    results_without_primary = sum(
        1 for error in errors if ": no Git-tracked primary source is accessible" in error
    )
    summary = {
        "research_count": len(research_records),
        "result_count": len(result_records),
        "research_status_distribution": dict(sorted(research_status_counts.items())),
        "evidence_type_distribution": dict(sorted(evidence_counts.items())),
        "research_without_results": sorted(
            record.get("id") for record in research_records if not results_per_research.get(record.get("id"))
        ),
        "results_without_accessible_primary_evidence": results_without_primary,
        "incomplete_source_references": incomplete_references,
        "audit_families_expected": len(expected_families),
        "audit_families_represented": len(expected_families & represented_families),
        "audit_families_unrepresented": missing_families,
        "theory_ledger_expected": len(expected_theory),
        "theory_ledger_represented": len(expected_theory & represented_theory),
        "theory_ledger_unrepresented": missing_theory,
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }
    return {"valid": not errors, "summary": summary}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).resolve().with_name("hls_scientific_registry.jsonl"),
    )
    args = parser.parse_args(argv)
    result = validate_registry(args.registry, args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
