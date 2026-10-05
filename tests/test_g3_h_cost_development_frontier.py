"""Focused controls for the descriptive frozen-G3-H cost--development ledger."""

from __future__ import annotations

import pytest

from hls.g3_h_cost_development_frontier import evaluate_cost_development_frontier
from hls.g3_h_regime_map import evaluate_point
from hls.g3_organizational_value import G3A_ASSIGNMENTS
from hls.minimal_reference_scenario import EXACT_TOL


STATE = ((0.5, 0.7), (0.3, 0.2), (0.5, 0.8))
PROFILE = (0.4, 0.6, 0.4)


def test_cost_is_existing_operational_gap_and_development_bounds_hold() -> None:
    frontier = evaluate_cost_development_frontier(STATE, PROFILE)
    point = evaluate_point(STATE, PROFILE)
    gaps = {item.action: item.operational_gap for item in point.actions}
    for item in frontier.actions:
        assert item.cost >= -EXACT_TOL
        assert item.cost == pytest.approx(gaps[item.action], abs=EXACT_TOL)
        assert item.local_value == pytest.approx(item.reward + item.development, abs=EXACT_TOL)
    assert frontier.free_development <= frontier.maximum_development + EXACT_TOL
    assert frontier.minimum_cost_of_maximum_development >= -EXACT_TOL


def test_frontier_contains_no_dominated_action() -> None:
    frontier = evaluate_cost_development_frontier(STATE, PROFILE)
    by_action = {item.action: item for item in frontier.actions}
    for action in frontier.frontier_actions:
        candidate = by_action[action]
        for other in frontier.actions:
            weakly_better = other.cost <= candidate.cost + EXACT_TOL and other.development >= candidate.development - EXACT_TOL
            strictly_better = other.cost < candidate.cost - EXACT_TOL or other.development > candidate.development + EXACT_TOL
            assert not (weakly_better and strictly_better)


def test_frontier_is_enumeration_order_invariant() -> None:
    forward = evaluate_cost_development_frontier(STATE, PROFILE)
    reverse = evaluate_cost_development_frontier(STATE, PROFILE, actions=tuple(reversed(G3A_ASSIGNMENTS)))
    assert forward.frontier_actions == reverse.frontier_actions
    assert forward.free_development == pytest.approx(reverse.free_development, abs=EXACT_TOL)
    assert forward.maximum_development == pytest.approx(reverse.maximum_development, abs=EXACT_TOL)
    assert forward.minimum_cost_of_maximum_development == pytest.approx(reverse.minimum_cost_of_maximum_development, abs=EXACT_TOL)
