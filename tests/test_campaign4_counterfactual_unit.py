from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_fast_deep_meta import run as fast_deep  # noqa: E402
from experiments.synthetic.campaign3_c32_data import targets as c32_targets  # noqa: E402
from experiments.synthetic.campaign4_counterfactual_deliberation import engine  # noqa: E402
from hls import finite_problem_belief as planner  # noqa: E402
from hls.discover_v0 import JOINT_ACTIONS  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402


def test_horizon_end_clock_semantics_are_problem_indexed():
    assert engine.horizon_end(1, 3, "H0") == 2
    assert engine.horizon_end(1, 3, "H1") == 3
    assert engine.horizon_end(1, 3, "H2") == 36
    assert engine.horizon_end(5, 2, "H0") == 6
    assert engine.horizon_end(5, 2, "H1") == 6
    assert engine.horizon_end(5, 2, "H2") == 36
    with pytest.raises(ValueError):
        engine.horizon_end(3, 3, "H0")


def test_h0_is_not_the_frozen_c32_training_target_horizon():
    # The C4 two-decision H0 is retained, but C3.2 labels use the distinct
    # current-remainder-plus-eleven-subsequent-problems endpoint.
    assert c32_targets.ELL == 11
    assert engine.horizon_end(1, 3, "H0") - 1 + 1 == 2


def test_counter_seeded_observation_innovations_are_clock_keyed_and_repeatable():
    first = engine.innovations("fixed-state", 2, range(4, 10))
    second = engine.innovations("fixed-state", 2, range(4, 10))
    assert first == second
    assert set(first) == set(range(4, 10))
    assert engine.innovations("fixed-state", 3, range(4, 10)) != first


def test_fast_is_exact_q00_and_deep_collapses_to_fast_at_terminal():
    symmetric = ((0.5, 0.5), (0.5, 0.5), (0.5, 0.5))
    cases = [(symmetric, UNIFORM_PRIOR)]
    tie_values = planner.prospective_action_values(
        symmetric, UNIFORM_PRIOR, HYPOTHESIS_REPERTOIRE, remaining=1,
        anticipate_information=False, anticipate_development=False, eta=0.35,
    )
    best = max(tie_values.values())
    assert sum(abs(value - best) <= planner.EXACT_TOL for value in tie_values.values()) > 1
    state = symmetric
    belief = UNIFORM_PRIOR
    for clock in (1, 2):
        assert fast_deep.choose_fast_action(state, belief, 3)[0] == planner.choose_prospective_action(
            state, belief, HYPOTHESIS_REPERTOIRE, remaining=3,
            policy_mode=planner.ProspectivePolicyMode.NONE, eta=0.35,
        )[0]
        cases.append((state, belief))
    for state, belief in cases:
        fast_action = fast_deep.choose_fast_action(state, belief, 1)[0]
        q00_action = planner.choose_prospective_action(
            state, belief, HYPOTHESIS_REPERTOIRE, remaining=1,
            policy_mode=planner.ProspectivePolicyMode.NONE, eta=0.35,
        )[0]
        deep_action = fast_deep.choose_deep_action(state, belief, 1)[0]
        assert fast_action == q00_action
        assert fast_action == deep_action


def test_terminal_meta_continuation_does_not_call_selector(monkeypatch):
    action = JOINT_ACTIONS[0]
    monkeypatch.setattr(engine, "choose_fast_action", lambda *_: (action, 0.0))

    def forbidden(*_args, **_kwargs):
        raise AssertionError("terminal decision must not invoke selector/DEEP")

    monkeypatch.setattr(engine, "frozen_selector", forbidden)
    monkeypatch.setattr(engine, "choose_deep_action", forbidden)
    selected, invoked = engine.choose_continuation(
        ((0.5, 0.5),) * 3, UNIFORM_PRIOR, 3, "META_VOC_50", {}, {}, {}
    )
    assert selected == action
    assert invoked is False


def test_q11_and_meta_continuations_follow_their_own_frozen_route(monkeypatch):
    fast, deep = JOINT_ACTIONS[0], JOINT_ACTIONS[-1]
    monkeypatch.setattr(engine, "choose_fast_action", lambda *_: (fast, 0.0))
    monkeypatch.setattr(engine, "choose_deep_action", lambda *_: (deep, 0.0))
    monkeypatch.setattr(engine, "frozen_selector", lambda *_: {"invoke": False})
    assert engine.choose_continuation(((0.5, 0.5),) * 3, UNIFORM_PRIOR, 1,
                                      "Q11", {}, {}, {}) == (deep, True)
    assert engine.choose_continuation(((0.5, 0.5),) * 3, UNIFORM_PRIOR, 1,
                                      "META_VOC_50", {}, {}, {}) == (fast, False)
    monkeypatch.setattr(engine, "frozen_selector", lambda *_: {"invoke": True})
    assert engine.choose_continuation(((0.5, 0.5),) * 3, UNIFORM_PRIOR, 1,
                                      "META_VOC_50", {}, {}, {}) == (deep, True)



