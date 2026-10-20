from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign4_counterfactual_deliberation import engine  # noqa: E402
from hls import campaign2_theory as theory  # noqa: E402
from hls.discover_v0 import JOINT_ACTIONS  # noqa: E402
from hls.small_problem_world import UNIFORM_PRIOR  # noqa: E402


def _record(state_id: str) -> dict:
    return {
        "state_id": state_id, "history_id": "synthetic-history", "domain": "synthetic",
        "policy": "Q11", "state_before": json.dumps([[0.5, 0.5]] * 3),
        "belief_before": json.dumps(UNIFORM_PRIOR), "clock": 1, "remaining": 3, "tau": 36,
    }


def test_identical_forced_first_action_gives_identical_paired_trajectories(monkeypatch):
    action = JOINT_ACTIONS[0]
    monkeypatch.setattr(engine, "choose_fast_action", lambda *_: (action, 0.0))
    monkeypatch.setattr(engine, "choose_deep_action", lambda *_: (action, 0.0))
    original = theory._real_decision
    state_log = []

    def recording_real_decision(state, belief, action, problem, epsilon, model):
        result = original(state, belief, action, problem, epsilon, model)
        state_log.append((state, belief, result.state_after, result.belief_after))
        return result

    monkeypatch.setattr(engine.theory, "_real_decision", recording_real_decision)
    problems = tuple(0.2 + 0.6 * i / 11 for i in range(12))
    eps = {clock: (clock - 18.5) / 10.0 for clock in range(1, 37)}
    common = dict(horizon="H2", continuation="Q11", problems=problems, eps=eps,
                  model={}, costs={}, thresholds={})
    fast = engine.rollout(_record("same-action-state"), branch="FAST", **common)
    deep = engine.rollout(_record("same-action-state"), branch="DEEP", **common)
    physical_fields = ("clock", "action_id", "mu_true")
    assert [{key: row[key] for key in physical_fields} for row in fast["trace"]] == [
        {key: row[key] for key in physical_fields} for row in deep["trace"]
    ]
    assert fast["trace"][0]["invoked_deep"] is False
    assert deep["trace"][0]["invoked_deep"] is True
    assert fast["state_final"] == deep["state_final"]
    assert fast["belief_final"] == deep["belief_final"]
    assert [row["clock"] for row in fast["trace"]] == list(range(1, 37))
    assert len(fast["trace"]) == 36
    assert fast["reward"] == fast["reward_current"] + fast["reward_later"]
    assert len(state_log) == 72
    for branch_start in (0, 36):
        branch_log = state_log[branch_start:branch_start + 36]
        for index, (state_before, belief_before, state_after, belief_after) in enumerate(branch_log):
            if index:
                assert state_before == branch_log[index - 1][2]  # S persists across problem boundaries.
                if index % 3 == 0:
                    assert belief_before == tuple(UNIFORM_PRIOR)  # b resets at clocks 4, 7, ...
                else:
                    assert belief_before == branch_log[index - 1][3]


def test_different_forced_actions_recompute_branch_specific_real_transitions(monkeypatch):
    fast_action = JOINT_ACTIONS[0]
    deep_action = JOINT_ACTIONS[-1]
    monkeypatch.setattr(engine, "choose_fast_action", lambda *_: (fast_action, 0.0))
    monkeypatch.setattr(engine, "choose_deep_action", lambda *_: (deep_action, 0.0))
    original = theory._real_decision
    realized = []

    def recording_real_decision(state, belief, action, problem, epsilon, model):
        result = original(state, belief, action, problem, epsilon, model)
        realized.append((action, float(epsilon), result.mu_true, result.observation,
                         result.state_after, result.belief_after))
        return result

    monkeypatch.setattr(engine.theory, "_real_decision", recording_real_decision)
    problems = (0.2,) * 12
    eps = {clock: 0.25 for clock in range(1, 37)}
    common = dict(horizon="H0", continuation="Q11", problems=problems, eps=eps,
                  model={}, costs={}, thresholds={})
    fast = engine.rollout(_record("different-actions"), branch="FAST", **common)
    deep = engine.rollout(_record("different-actions"), branch="DEEP", **common)
    fast_first, deep_first = realized[0], realized[2]
    assert fast_first[0] != deep_first[0]
    assert fast_first[1] == deep_first[1] == eps[1]
    assert fast_first[2] != deep_first[2]
    assert fast_first[3] - fast_first[2] == pytest.approx(deep_first[3] - deep_first[2])
    assert fast["state_final"] != deep["state_final"]

