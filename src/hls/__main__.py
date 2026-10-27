"""Minimal catalog validation and query command."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from hls.catalog import load_catalog, validate_catalog


def main() -> int:
    parser = argparse.ArgumentParser(prog="hls")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="validate registry/catalog.json")
    query = sub.add_parser("query", help="filter catalog entities")
    query.add_argument("--type", choices=("scenario", "organization", "model", "policy", "evaluation", "study", "experiment", "result", "theoretical_result"))
    query.add_argument("--text", help="case-insensitive search in id, name, definition and aliases")
    query.add_argument("--status")
    query.add_argument("--related-to", help="entity id; match direct links in either direction")
    args = parser.parse_args()
    path = Path(__file__).resolve().parents[2] / "registry" / "catalog.json"
    data = load_catalog(path)
    issues = validate_catalog(data, path.parent.parent)
    if issues:
        parser.error("catalog invalid: " + "; ".join(issues))
    if args.command == "validate":
        counts = {}
        for item in data["entities"]:
            counts[item["type"]] = counts.get(item["type"], 0) + 1
        print(json.dumps({"valid": True, "entities": len(data["entities"]), "by_type": counts}, sort_keys=True))
        return 0
    text = (args.text or "").casefold()
    hits = []
    for item in data["entities"]:
        if args.type and item["type"] != args.type:
            continue
        if args.status and item.get("status") != args.status:
            continue
        if args.related_to and not any(
            relation.get("target") == args.related_to
            for relation in item.get("relationships", [])
        ) and not any(
            relation.get("target") == item["id"]
            for other in data["entities"]
            for relation in other.get("relationships", [])
            if other["id"] == args.related_to
        ):
            continue
        aliases = [alias for alias, record in data.get("aliases", {}).items() if item["id"] in record.get("targets", [])]
        searchable = " ".join([item["id"], item["name"], item["definition"], *aliases]).casefold()
        if text and text not in searchable:
            continue
        hits.append({"id": item["id"], "type": item["type"], "name": item["name"], "status": item["status"]})
    print(json.dumps(hits, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
