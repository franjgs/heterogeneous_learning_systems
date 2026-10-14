"""Integrity checks for the bounded, archived HLS characterization pilot."""

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/experiments/hls_dynamic_characterization"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_characterization_manifest_and_artifact_hashes():
    manifest = json.loads((OUT / "manifest.json").read_text())
    assert manifest["protocol"] == "hls-dynamic-characterization-pilot-v1"
    assert manifest["seeds"] == [0, 1, 2, 3]
    assert manifest["horizons"] == [1, 3]
    assert manifest["no_new_policy_or_physics"] is True
    for relative, expected in manifest["source_hashes"].items():
        assert sha(ROOT / relative) == expected
    for name, expected in manifest["artifact_sha256"].items():
        assert sha(OUT / name) == expected


def test_characterization_counts_and_resource_observer():
    manifest = json.loads((OUT / "manifest.json").read_text())
    with (OUT / "run_summary.csv").open() as f:
        runs = list(csv.DictReader(f))
    with (OUT / "decision_traces.csv").open() as f:
        decisions = list(csv.DictReader(f))
    assert len(runs) == manifest["runs"] == 256
    assert len(decisions) == manifest["decisions"] == 5632
    run_keys = [(r["block"], r["scenario"], r["phase"], r["seed"]) for r in runs]
    assert len(set(run_keys)) == len(run_keys)
    # Unit effort cost is an observer only; its registered amount is effort×1.
    assert all(abs(float(r["resource_cost"]) - float(r["effort"])) < 1e-12 for r in decisions)
    assert {r["policy"] for r in runs} == {
        "adaptive_greedy", "discover_unknown_policy", "learned_tabular"
    }


def test_paired_contrasts_cover_information_learning_planning_and_cost():
    with (OUT / "paired_contrasts.csv").open() as f:
        rows = list(csv.DictReader(f))
    contrasts = {r["contrast"] for r in rows}
    assert {
        "planning_minus_greedy", "partial_static_minus_oracle",
        "partial_updated_minus_static", "individual_learning_on_minus_off",
        "individual_fast_learning_on_minus_off", "fast_on_minus_slow_on",
        "organizational_update_eval",
    } <= contrasts
    assert {r["outcome"] for r in rows} == {"reward", "success", "cost", "effort"}
    assert all(int(r["bootstrap_replicates"]) == 2000 for r in rows)
