"""Controls for derived DISCOVER-v0 production--information geometry."""

from __future__ import annotations

from itertools import permutations

import pytest

from hls.discover_v0 import THETA_1, THETA_2, capability_dual, enumerate_canonical_states, evaluate_state
from hls.discover_v0_geometry import action_information_by_action, action_information_geometry, pareto_frontier


STATE = ((0.0, 0.0), (0.5, 0.5), (1.0, 1.0))


def _points(items):
    return sorted((item.reward_prior, item.discriminability, item.kl, item.production_gap, item.pareto_optimal) for item in items)


def test_complete_ledger_obeys_discriminability_kl_identities() -> None:
    items = action_information_geometry(STATE)
    assert len(items) == 64
    assert all(item.kl == pytest.approx(item.discriminability**2 / 2.0) for item in items)
    assert all(item.kl == pytest.approx(0.0) for item in items if item.discriminability == pytest.approx(0.0))
    assert all(item.production_gap >= -1e-10 for item in items)


def test_equal_mean_actions_are_uninformative() -> None:
    items = action_information_geometry(STATE)
    assert all(item.discriminability == pytest.approx(0.0) and item.kl == pytest.approx(0.0) for item in items if item.mu_theta1 == pytest.approx(item.mu_theta2))


def test_pareto_frontier_is_complete_and_undominated() -> None:
    items = action_information_geometry(STATE)
    frontier = pareto_frontier(items)
    assert frontier
    for item in frontier:
        assert not any(
            other.reward_prior >= item.reward_prior
            and other.discriminability >= item.discriminability
            and (other.reward_prior > item.reward_prior or other.discriminability > item.discriminability)
            for other in items
        )


def test_geometry_is_worker_permutation_invariant_as_a_multiset() -> None:
    baseline = action_information_geometry(STATE)
    for permutation in permutations(range(3)):
        candidate = tuple(STATE[index] for index in permutation)
        assert _points(action_information_geometry(candidate)) == pytest.approx(_points(baseline))


def test_capability_theta_duality_preserves_geometry() -> None:
    original = action_information_geometry(STATE)
    dual = action_information_geometry(capability_dual(STATE), theta_1=THETA_2, theta_2=THETA_1)
    assert _points(dual) == pytest.approx(_points(original))


def test_unknown_initial_actions_are_reported_from_the_prior_dp_only() -> None:
    evaluation = evaluate_state(STATE)
    by_action = action_information_by_action(action_information_geometry(STATE))
    assert set(evaluation.unknown.first_actions) <= set(by_action)
    assert evaluation == evaluate_state(STATE)
    assert len(enumerate_canonical_states()) == 31


def test_s001_s002_reference_values_and_geometry_difference_reproduce() -> None:
    s001 = ((0.0, 0.0), (0.5, 0.5), (1.0, 1.0))
    s002 = ((0.0, 0.0), (0.5, 1.0), (0.5, 1.0))
    first, second = evaluate_state(s001), evaluate_state(s002)
    assert first.known_value == pytest.approx(2.96665631459995)
    assert first.discovery_cost == pytest.approx(0.29147845842775144)
    assert second.known_value == pytest.approx(2.9639387691339825)
    assert second.discovery_cost == pytest.approx(0.1970847442944117)
    first_geometry = action_information_geometry(s001)
    second_geometry = action_information_geometry(s002)
    assert max(item.discriminability for item in first_geometry) == pytest.approx(9.0)
    assert max(item.discriminability for item in second_geometry) == pytest.approx(12.0)
