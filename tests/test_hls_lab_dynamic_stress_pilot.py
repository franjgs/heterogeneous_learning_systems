"""Design-only checks for the bounded stress-pilot scenario construction."""
import pytest
import csv
import hashlib
import json
from pathlib import Path

from experiments.synthetic.hls_lab_dynamic.stress_pilot import (
    BALANCED_NEAR_FRONTIER, COMPLEMENTARY, RESTRICTED_REQ, SIMILAR,
    HETEROGENEOUS, dynamic_sequence, frontier, validate_scenarios,
)
from hls.hls_lab_dynamic import DiscoverBeliefPolicy
from hls.hls_lab_dynamic import LearningProfile, run_dynamic_sequence
from hls.hls_lab_v1 import GreedyAdaptive, ProblemSpec, feasible_actions, make_team
from experiments.synthetic.hls_lab_dynamic.stress_pilot import summarize, trace_rows

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/experiments/hls_dynamic_stress_pilot"


def test_frontier_criteria_are_nontrivial_and_policy_independent():
    similar, heterogeneous, tight = validate_scenarios()
    assert similar["max_balanced"] == pytest.approx(0.675)
    assert heterogeneous["max_balanced"] == pytest.approx(1.07)
    assert similar["success_count"](BALANCED_NEAR_FRONTIER) > 0
    assert heterogeneous["success_count"](BALANCED_NEAR_FRONTIER) > 0
    assert similar["success_count"](COMPLEMENTARY) == 0
    assert heterogeneous["success_count"](COMPLEMENTARY) > 0
    assert tight["action_count"] == 10
    assert 0 < tight["success_count"](RESTRICTED_REQ) < 10


def test_scenario_sequences_are_reproducible_and_switch_at_problem_boundary():
    a = dynamic_sequence(3, "switching_orientation")
    b = dynamic_sequence(3, "switching_orientation")
    assert a == b
    assert len(a) == 8
    assert tuple(x.problem.requirements for x in a[:4]) == ((1.2, 0.25),) * 4
    assert tuple(x.problem.requirements for x in a[4:]) == ((0.25, 1.2),) * 4


def test_restricted_budget_is_not_claimed_as_discover_compatible():
    problem = ProblemSpec("tight", RESTRICTED_REQ, 1.5)
    assert len(feasible_actions(problem)) == 10
    assert len(feasible_actions(problem)) != 64
    # Frozen DISCOVER adapter rejects a selected action outside the legal
    # subset; the stress-pilot contract therefore excludes it in this block.
    assert DiscoverBeliefPolicy().name == "discover_unknown_policy"


def test_frontier_calibration_uses_only_existing_team_and_action_sets():
    assert frontier(SIMILAR)["action_count"] == 64
    assert frontier(HETEROGENEOUS)["action_count"] == 64


def test_restricted_budget_records_use_existing_episode_record_shape():
    result = run_dynamic_sequence(
        make_team(SIMILAR), (ProblemSpec("tight", RESTRICTED_REQ, 1.5),),
        GreedyAdaptive(), learning=LearningProfile(((.03, .03),) * 3),
        individual_learning=False,
    )
    summary = summarize(result, "test", "tight_frontier", "similar", 1, 0, "eval")
    rows = list(trace_rows(result, "test", "tight_frontier", "similar", 1, 0, "eval"))
    assert summary["decisions"] == 1
    assert len(rows) == 1
    assert rows[0]["environment"] == "fixed_theta1_no_belief_model"


def test_pilot_artifacts_are_complete_unique_and_hash_verified():
    manifest = json.loads((OUT / "manifest.json").read_text())
    assert manifest["protocol"] == "hls-dynamic-stress-pilot-v1"
    assert manifest["runs"] == 448
    assert manifest["decisions"] == 7104
    for name, digest in manifest["source_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
    for name, digest in manifest["artifact_sha256"].items():
        assert hashlib.sha256((OUT / name).read_bytes()).hexdigest() == digest
    with (OUT / "run_summary.csv").open() as f:
        runs = list(csv.DictReader(f))
    with (OUT / "decision_traces.csv").open() as f:
        traces = list(csv.DictReader(f))
    run_ids = [(r["block"], r["scenario"], r["team"], r["horizon"], r["seed"], r["phase"])
               for r in runs]
    assert len(run_ids) == len(set(run_ids)) == 448
    assert len(traces) == 7104
    assert all(float(r["resource_cost"]) == float(r["effort"])
               for r in traces if r["block"] == "full_catalog")
