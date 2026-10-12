from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_fast_deep_meta import run  # noqa: E402
from experiments.synthetic.strategy_discrimination_gate.run import MODE_BY_ID  # noqa: E402
from hls import finite_problem_belief as planner  # noqa: E402
from hls.discover_v0 import EXACT_TOL, JOINT_ACTIONS  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE  # noqa: E402


def test_fast_matches_frozen_q00_on_existing_development_states():
    frame = pd.read_csv(
        ROOT / "results/diagnostics/campaign3_gate2/factual_states.csv.gz",
        usecols=["state_before", "belief_before", "action_Q00", "decision"],
        nrows=20,
    )
    for row in frame.itertuples(index=False):
        state = tuple(tuple(float(v) for v in x) for x in json.loads(row.state_before))
        belief = tuple(float(v) for v in json.loads(row.belief_before))
        remaining = 4 - int(row.decision)
        fast, _ = planner.choose_fast_action(state, belief, HYPOTHESIS_REPERTOIRE)
        q00, _ = planner.choose_prospective_action(
            state, belief, HYPOTHESIS_REPERTOIRE, remaining=remaining,
            policy_mode=MODE_BY_ID["Q00"], eta=0.35,
        )
        assert fast == q00 == JOINT_ACTIONS[int(row.action_Q00)]


def test_fast_and_deep_collapse_at_one_remaining_decision():
    frame = pd.read_csv(
        ROOT / "results/diagnostics/campaign3_gate2/factual_states.csv.gz",
        usecols=["state_before", "belief_before"], nrows=12,
    )
    for row in frame.itertuples(index=False):
        state = tuple(tuple(float(v) for v in x) for x in json.loads(row.state_before))
        belief = tuple(float(v) for v in json.loads(row.belief_before))
        fast, _ = run.choose_fast_action(state, belief, 1)
        deep, _ = run.choose_deep_action(state, belief, 1)
        assert fast == deep


def test_fast_ties_use_frozen_joint_action_order_and_tolerance():
    state = ((0.5, 0.5), (0.5, 0.5), (0.5, 0.5))
    belief = (1 / 3, 1 / 3, 1 / 3)
    model, canonical_belief = planner.canonical_model(HYPOTHESIS_REPERTOIRE, belief)
    values = {
        action: planner.expected_reward(canonical_belief, planner.hypothesis_means(state, action, model))
        for action in JOINT_ACTIONS
    }
    maximum = max(values.values())
    expected = next(action for action in JOINT_ACTIONS if abs(values[action] - maximum) <= EXACT_TOL)
    actual, _ = planner.choose_fast_action(state, belief, HYPOTHESIS_REPERTOIRE)
    assert actual == expected


def test_meta_fast_route_never_calls_deep(monkeypatch):
    counts = {"fast": 0, "deep": 0}
    def fast(*args):
        counts["fast"] += 1
        return JOINT_ACTIONS[0], 0.0
    def deep(*args):
        counts["deep"] += 1
        raise AssertionError("DEEP must not execute on FAST acceptance")
    monkeypatch.setattr(run, "choose_fast_action", fast)
    monkeypatch.setattr(run, "choose_deep_action", deep)
    monkeypatch.setattr(run.c33, "predict", lambda *args: np.array([-0.25]))
    action, detail = run.choose_meta_action(((0.5, 0.5),) * 3, (1 / 3,) * 3, 2, 20, {})
    assert action == JOINT_ACTIONS[0]
    assert detail["route"] == "FAST_ACCEPT" and detail["deep_ns"] == 0
    assert counts == {"fast": 1, "deep": 0}


def test_meta_terminal_route_skips_selector_and_deep(monkeypatch):
    called = {"predict": 0, "deep": 0}
    monkeypatch.setattr(run, "choose_fast_action", lambda *args: (JOINT_ACTIONS[0], 0.0))
    monkeypatch.setattr(run, "choose_deep_action", lambda *args: called.__setitem__("deep", 1))
    monkeypatch.setattr(run.c33, "predict", lambda *args: called.__setitem__("predict", 1))
    _, detail = run.choose_meta_action(((0.5, 0.5),) * 3, (1 / 3,) * 3, 1, 1, {})
    assert detail["route"] == "FAST_TERMINAL"
    assert detail["deep_ns"] == detail["selector_ns"] == 0
    assert called == {"predict": 0, "deep": 0}


def test_fresh_design_and_common_random_numbers_are_reproducible():
    first, second = run.new_tasks(), run.new_tasks()
    assert len(first) == 420
    assert [(x["history_id"], x["problem_seed"], x["noise_seed"]) for x in first] == [
        (x["history_id"], x["problem_seed"], x["noise_seed"]) for x in second
    ]
    p1, e1 = run.exogenous(first[0]); p2, e2 = run.exogenous(second[0])
    assert p1 == p2 and e1 == e2 and len(p1) == 12 and len(e1) == 36


def test_fast_deep_cost_benchmark_distinguishes_cold_and_cached():
    assert run.BOOTSTRAP_B == 2000
    assert run.N_CELLS == 420
    # Cost reporting is deliberately split: the experiment is uncached; the
    # separate diagnostic labels cold calls and warm memoized lookups.
    source = (ROOT / "experiments/synthetic/campaign3_fast_deep_meta/run.py").read_text()
    assert '"cold_median_ms"' in source and '"warm_cached_median_ms"' in source


def test_one_fresh_history_simulates_independent_reproducible_policy_paths():
    model = json.loads((run.c33.OUT / "selector_model.json").read_text())
    task = run.new_tasks()[0]
    first_runs, first_trace = run.simulate_history((task, model))
    second_runs, second_trace = run.simulate_history((task, model))
    assert [row["policy"] for row in first_runs] == ["FAST", "DEEP", "META"]
    assert len(first_trace) == len(second_trace) == 108
    for a, b in zip(first_runs, second_runs, strict=True):
        assert a["cumulative_mu_true"] == b["cumulative_mu_true"]
        assert a["problem_stream_sha256"] == b["problem_stream_sha256"]
        assert a["noise_stream_sha256"] == b["noise_stream_sha256"]
    timing_fields = {"decision_compute_ns", "selector_ns", "fast_ns", "deep_ns"}
    stable_a = [{k: v for k, v in row.items() if k not in timing_fields} for row in first_trace]
    stable_b = [{k: v for k, v in row.items() if k not in timing_fields} for row in second_trace]
    assert stable_a == stable_b
    for policy in ("FAST", "DEEP", "META"):
        own = [row for row in first_trace if row["policy"] == policy]
        assert len(own) == 36
        for current, following in zip(own, own[1:]):
            assert current["state_after"] == following["state_before"]
        assert own[0]["state_before"] == json.dumps(task["team"], separators=(",", ":"))
    meta = [row for row in first_trace if row["policy"] == "META"]
    assert all(row["deep_ns"] == 0 for row in meta if row["route"] in ("FAST_ACCEPT", "FAST_TERMINAL"))
