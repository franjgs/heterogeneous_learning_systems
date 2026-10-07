"""Execution-infrastructure checks that do not run the Campaign 1 factorial."""

import inspect
import json
from pathlib import Path

import pandas as pd
import pytest

from experiments.synthetic.campaign1.run import _task, build_tasks, run_condition, run_no_develop
from hls.campaign1_protocol import CONDITIONS, TOTAL_RUNS
from hls.discover_v0 import DEFAULT_SIGMA
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE


STATE = ((0.1, 0.6), (0.5, 0.5), (0.9, 0.2))
PROBLEMS = ((0.8, 0.2), (0.7, 0.3))
ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "campaigns" / "campaign1_test_range"


def test_exact_run_key_matrix_is_unique_and_complete():
    tasks = build_tasks()
    assert len(tasks) == len(set(tasks)) == TOTAL_RUNS == 960


def test_no_develop_uses_dynamic_mpc_primitive_and_never_changes_state():
    source = inspect.getsource(run_no_develop)
    assert "finite_choose_dynamic_action_v2" in source
    assert "develop=False" in source
    assert "finite_unknown_policy_value" not in source
    rows = run_no_develop(STATE, PROBLEMS, eta=.35, horizon=3, seed=4)
    assert len(rows) == 6
    assert all(row.state_before == row.state_after == STATE for row in rows)
    assert rows[0].belief_before == rows[3].belief_before == (1 / 3,) * 3


def test_full_no_develop_and_known_z_share_crn_draws():
    # This small infrastructure check is not a frozen Campaign 1 configuration/run.
    results = {condition: run_condition("G00", "TR-PR", condition, 3) for condition in CONDITIONS}
    innovations = {
        condition: tuple(round((row.observed_reward - row.true_mean) / DEFAULT_SIGMA, 14) for row in rows)
        for condition, rows in results.items()
    }
    assert innovations["FULL"] == pytest.approx(innovations["NO-DEVELOP"], abs=2e-14)
    assert innovations["FULL"] == pytest.approx(innovations["KNOWN-Z"], abs=2e-14)
    assert all(row.belief_before is None for row in results["KNOWN-Z"])
    assert all(row.belief_before is not None for row in results["FULL"] + results["NO-DEVELOP"])


def test_condition_dispatch_is_exact():
    with pytest.raises(ValueError):
        run_condition("G00", "TR-PR", "DISCOVER_ONLY", 0)


def test_worker_task_serializes_summary_and_complete_trajectory():
    summary, rows = _task(("TR-PR", "G00", "NO-DEVELOP", 0))
    assert summary["eta"] == .35 and summary["horizon"] == 3
    assert len(rows) == 18
    assert all(row["state_before"] == row["state_after"] for row in rows)


def test_materialized_campaign_is_complete_unique_and_crn_aligned():
    runs = pd.read_csv(RESULTS / "runs.csv")
    trajectories = pd.read_csv(RESULTS / "trajectories.csv")
    run_key = ["scenario_id", "configuration_id", "condition", "seed"]
    step_key = run_key + ["problem_index", "within_problem_step"]
    assert len(runs) == 960
    assert len(trajectories) == 17_280
    assert not runs.duplicated(run_key).any()
    assert not trajectories.duplicated(step_key).any()
    assert runs.groupby("condition").size().to_dict() == {
        "FULL": 320, "KNOWN-Z": 320, "NO-DEVELOP": 320,
    }
    assert (runs.groupby(["scenario_id", "condition"]).size() == 40).all()
    assert (runs.groupby("configuration_id").size() == 240).all()
    assert (runs.groupby(run_key[:-1]).seed.nunique() == 10).all()
    assert (trajectories.groupby(run_key).size() == 18).all()
    for _, values in trajectories.groupby(
        ["seed", "problem_index", "within_problem_step"]
    ).noise_innovation:
        assert values.max() - values.min() <= 2e-14


def test_materialized_performance_is_mu_true_not_observed_reward():
    runs = pd.read_csv(RESULTS / "runs.csv")
    trajectories = pd.read_csv(RESULTS / "trajectories.csv")
    totals = trajectories.groupby(
        ["scenario_id", "configuration_id", "condition", "seed"]
    ).mu_true.sum()
    stored = runs.set_index(
        ["scenario_id", "configuration_id", "condition", "seed"]
    ).cumulative_performance
    assert stored.sort_index().to_numpy() == pytest.approx(totals.sort_index().to_numpy(), abs=1e-12)
    assert (trajectories.observed_reward != trajectories.mu_true).any()


def test_materialized_manifest_and_analysis_close_the_frozen_campaign():
    manifest = json.loads((RESULTS / "execution_manifest.json").read_text())
    analysis = json.loads((RESULTS / "analysis_summary.json").read_text())
    assert manifest["pre_results_head"] == "bcc3ad8"
    assert manifest["test_range_commit"] == "05b86cb"
    assert manifest["run_count"] == 960 and manifest["trajectory_rows"] == 17_280
    assert manifest["performance_field"] == "mu_true"
    assert manifest["analysis_classification"] == analysis["classification"] == "PASS"
    assert all(manifest["materialized_validation"].values())
