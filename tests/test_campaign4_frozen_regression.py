from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_c33 import c33  # noqa: E402
from experiments.synthetic.campaign3_fast_deep_meta import run as fast_deep  # noqa: E402
from experiments.synthetic.campaign3_meta_voc import confirmatory, run as voc  # noqa: E402
from experiments.synthetic.campaign4_counterfactual_deliberation import engine, preflight  # noqa: E402
from hls import campaign2_theory as theory  # noqa: E402
from hls import finite_problem_belief as planner  # noqa: E402
from hls.discover_v0 import JOINT_ACTIONS  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402

RUNS = ROOT / "results/campaigns/campaign3_meta_voc_confirmatory/runs.csv.gz"
TRAJECTORIES = ROOT / "results/campaigns/campaign3_meta_voc_confirmatory/trajectories.csv.gz"
MODEL = ROOT / "results/campaigns/campaign3_c33/selector_model.json"
CALIBRATION = ROOT / "results/campaigns/campaign3_meta_voc/sequential_full/calibration.json"
EXPECTED_HISTORIES = (
    "campaign3_meta_voc_confirmatory_v1:G1:F01:K01:0",
    "campaign3_meta_voc_confirmatory_v1:G4:F24:K30:0",
)
TOL = 1e-12


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _close(actual, expected, *, label: str, discrepancies: list[dict]):
    a, e = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
    if not np.allclose(a, e, rtol=TOL, atol=TOL):
        discrepancies.append({"field": label, "max_abs_error": float(np.max(np.abs(a - e))),
                              "actual": a.tolist(), "expected": e.tolist()})


def test_frozen_confirmatory_artifact_hashes_and_counts():
    report = preflight.inspect(RUNS, TRAJECTORIES, MODEL, CALIBRATION)
    assert report["n_histories"] == 868
    assert report["n_decisions"] == 249_984
    run_frame = pd.read_csv(RUNS)
    trace_frame = pd.read_csv(TRAJECTORIES)
    assert len(run_frame) == 6_944
    assert set(run_frame.policy.unique()) == set(confirmatory.POLICIES)
    assert run_frame.groupby("domain").history_id.nunique().to_dict() == {
        "G1": 420, "G2": 200, "G3": 168, "G4": 80,
    }
    assert trace_frame.groupby("policy").size().eq(868 * 36).all()
    assert report["runs_sha256"] == "3c2d7310a510deed03264b9a6df30ffc09a0af5915cc76dba233d29eadfd9e28"
    assert report["trajectories_sha256"] == "b4022b7a76c2aece607138d6d740ae854517fa171e889d09c557350c8da2e498"
    assert report["ridge_sha256"] == "1874b1f06a7122361677f5bb617132bd2eff3976fd1aa890d7152436fb59ba1d"
    assert report["calibration_sha256"] == "bf329147e4e62a98bbfc9ae48c75cbe1066c1ff73b87c6fce6b63cf4f796e94a"


def test_reconstruct_two_frozen_histories_and_replay_recorded_real_transitions():
    tasks = {task["history_id"]: task for task in confirmatory.planned_tasks()
             if task["history_id"] in EXPECTED_HISTORIES}
    assert set(tasks) == set(EXPECTED_HISTORIES)
    runs = pd.read_csv(RUNS, dtype={"history_id": str})
    traces = pd.read_csv(TRAJECTORIES, dtype={"history_id": str})
    run_rows = runs[runs.history_id.isin(EXPECTED_HISTORIES)].copy()
    trace_rows = traces[traces.history_id.isin(EXPECTED_HISTORIES)].copy()
    assert len(run_rows) == 2 * 8
    assert len(trace_rows) == 2 * 8 * 36

    discrepancies: list[dict] = []
    max_errors = {"state_before": 0.0, "belief_before": 0.0,
                  "state_after": 0.0, "belief_after": 0.0, "mu_true": 0.0}
    checked_transitions = 0
    checked_problem_boundaries = 0
    model, prior = planner.canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    for history_id in EXPECTED_HISTORIES:
        task = tasks[history_id]
        observed_runs = run_rows[run_rows.history_id == history_id]
        assert set(observed_runs.policy) == set(confirmatory.POLICIES)
        assert set(observed_runs.problem_seed.astype(int)) == {task["problem_seed"]}
        assert set(observed_runs.noise_seed.astype(int)) == {task["noise_seed"]}
        problems, eps = voc.make_exogenous(task)
        problem_hash = hashlib.sha256(voc.packed(problems).encode()).hexdigest()
        noise_hash = hashlib.sha256(voc.packed(eps).encode()).hexdigest()
        assert set(observed_runs.problem_stream_sha256) == {problem_hash}
        assert set(observed_runs.noise_stream_sha256) == {noise_hash}

        for policy in confirmatory.POLICIES:
            policy_rows = trace_rows[(trace_rows.history_id == history_id) & (trace_rows.policy == policy)]
            policy_rows = policy_rows.sort_values("clock")
            assert len(policy_rows) == 36
            state = task["team"]
            belief = prior
            for row in policy_rows.to_dict("records"):
                clock = int(row["clock"])
                if clock > 1 and (clock - 1) % 3 == 0:
                    belief = prior
                    checked_problem_boundaries += 1
                recorded_before = json.loads(row["state_before"])
                recorded_belief_before = json.loads(row["belief_before"])
                for field, actual, expected in (
                    ("state_before", state, recorded_before),
                    ("belief_before", belief, recorded_belief_before),
                ):
                    err = float(np.max(np.abs(np.asarray(actual) - np.asarray(expected))))
                    max_errors[field] = max(max_errors[field], err)
                    _close(actual, expected, label=f"{history_id}/{policy}/{clock}/{field}", discrepancies=discrepancies)
                action = JOINT_ACTIONS[int(row["action_id"])]
                p = problems[(clock - 1) // 3]
                real = theory._real_decision(state, belief, action, (p, 1.0 - p), eps[clock - 1], model)
                for field, actual, expected in (
                    ("state_after", real.state_after, json.loads(row["state_after"])),
                    ("belief_after", real.belief_after, json.loads(row["belief_after"])),
                    ("mu_true", real.mu_true, float(row["mu_true"])),
                ):
                    err = float(np.max(np.abs(np.asarray(actual) - np.asarray(expected))))
                    max_errors[field] = max(max_errors[field], err)
                    _close(actual, expected, label=f"{history_id}/{policy}/{clock}/{field}", discrepancies=discrepancies)
                state, belief = real.state_after, real.belief_after
                checked_transitions += 1
    assert checked_transitions == 2 * 8 * 36
    assert checked_problem_boundaries == 2 * 8 * 11
    print(json.dumps({"selected_history_ids": EXPECTED_HISTORIES,
                      "replayed_transitions": checked_transitions,
                      "belief_reset_boundaries": checked_problem_boundaries,
                      "tolerance_atol_rtol": TOL,
                      "max_abs_errors": max_errors,
                      "discrepancy_count": len(discrepancies)}, sort_keys=True))
    assert not discrepancies, json.dumps({"tolerance_atol_rtol": TOL, "max_abs_errors": max_errors,
                                           "discrepancies": discrepancies[:25],
                                           "discrepancy_count": len(discrepancies)}, indent=2)


def test_fast_matches_recorded_q00_and_terminal_deep_action():
    traces = pd.read_csv(TRAJECTORIES, dtype={"history_id": str})
    states = traces[(traces.history_id.isin(EXPECTED_HISTORIES)) & traces.policy.isin(("FAST", "Q00"))]
    for row in states.to_dict("records"):
        state = tuple(tuple(float(v) for v in r) for r in json.loads(row["state_before"]))
        belief = tuple(float(v) for v in json.loads(row["belief_before"]))
        remaining = int(row["remaining"])
        fast_action = fast_deep.choose_fast_action(state, belief, remaining)[0]
        q00_action = planner.choose_prospective_action(
            state, belief, HYPOTHESIS_REPERTOIRE, remaining=remaining,
            policy_mode=planner.ProspectivePolicyMode.NONE, eta=0.35,
        )[0]
        assert fast_action == q00_action, f"FAST/Q00 action mismatch at {row['history_id']} clock={row['clock']}"
        if remaining == 1:
            assert fast_deep.choose_deep_action(state, belief, remaining)[0] == fast_action


def test_frozen_meta_voc_50_reproduces_recorded_routes_and_scores():
    model = json.loads(MODEL.read_text())
    calibration = json.loads(CALIBRATION.read_text())
    assert tuple(model["features"]) == ("s11", "s12", "s21", "s22", "s31", "s32", "b0", "b1", "b2", "tau")
    assert model["alpha"] == 10.0
    costs = {int(k): float(v) for k, v in calibration["predicted_extra_cost_seconds_by_remaining"].items()}
    cutoff = calibration["thresholds"]["50"]
    assert cutoff["score_cutoff"] == 0.16708983036248765
    assert cutoff["tie_rule"] == "score descending, SHA-256 of ex-ante feature vector ascending"

    traces = pd.read_csv(TRAJECTORIES, dtype={"history_id": str})
    rows = traces[(traces.history_id.isin(EXPECTED_HISTORIES)) & (traces.policy == "META_VOC_50")]
    assert len(rows) == 2 * 36
    for row in rows.to_dict("records"):
        if int(row["remaining"]) == 1:
            assert row["route"] == "FAST_TERMINAL"
            continue
        state = tuple(tuple(float(v) for v in r) for r in json.loads(row["state_before"]))
        belief = tuple(float(v) for v in json.loads(row["belief_before"]))
        clock = int(row["clock"])
        selected = engine.frozen_selector(state, belief, clock, model, costs, calibration["thresholds"])
        assert selected["invoke"] == (row["route"] == "DEEP_INVOKE")
        assert math.isclose(selected["prediction"], float(row["predicted_benefit"]), rel_tol=TOL, abs_tol=TOL)
        assert math.isclose(selected["score"], float(row["score"]), rel_tol=TOL, abs_tol=TOL)
        assert math.isclose(selected["predicted_cost"], float(row["predicted_extra_cost_seconds"]), rel_tol=TOL, abs_tol=TOL)

