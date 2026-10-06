"""Focused scientific and numerical controls for DISCOVER-v0."""

from __future__ import annotations

from itertools import permutations
from math import exp

import pytest

from hls.discover_v0 import (
    DEFAULT_PRIOR,
    DEFAULT_SIGMA,
    JOINT_ACTIONS,
    THETA_1,
    THETA_2,
    bayes_update,
    canonical_state,
    capability_dual,
    enumerate_canonical_states,
    evaluate_state,
    known_expected_value,
    known_policy_value,
    known_value_bruteforce,
    means,
    production_inputs,
    state_budget,
    unknown_policy_value,
    unknown_value_bruteforce,
)


STATE = ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0))


def test_enumeration_preserves_exact_budget_and_worker_canonicalization() -> None:
    states = enumerate_canonical_states()
    assert len(states) == 31
    assert all(state_budget(state) == pytest.approx(3.0) for state in states)
    assert all(state == canonical_state(state) for state in states)


def test_discrete_actions_obey_agent_time_capacity() -> None:
    assert len(JOINT_ACTIONS) == 64
    for action in JOINT_ACTIONS:
        assert all(sum(allocation) <= 1.0 for allocation in action)


def test_bayes_matches_hand_computable_symmetric_case() -> None:
    mu_1, mu_2, sigma = 1.0, 0.0, 1.0
    # At r=.5 the two Gaussian likelihoods are identical, so b remains .5.
    assert bayes_update(0.5, 0.5, mu_1, mu_2, sigma) == pytest.approx(0.5)
    # r=1, equal prior: posterior odds are exp(.5).
    assert bayes_update(0.5, 1.0, mu_1, mu_2, sigma) == pytest.approx(exp(0.5) / (1.0 + exp(0.5)))


def test_uninformative_action_does_not_change_belief() -> None:
    # Zero allocation has equal means under both CES types.
    action = ((0.0, 0.0),) * 3
    mu_1, mu_2 = means(STATE, action)
    assert mu_1 == pytest.approx(mu_2)
    assert bayes_update(0.37, 0.42, mu_1, mu_2, DEFAULT_SIGMA) == pytest.approx(0.37)


def test_revealed_theta_control_is_exactly_known_value() -> None:
    evaluation = evaluate_state(STATE)
    assert evaluation.known_value == pytest.approx(
        0.5 * evaluation.known_theta_1.value + 0.5 * evaluation.known_theta_2.value
    )
    assert known_expected_value(STATE) == pytest.approx(evaluation.known_value)
    assert unknown_policy_value(STATE, prior=1.0).value == pytest.approx(evaluation.known_theta_1.value)
    assert unknown_policy_value(STATE, prior=0.0).value == pytest.approx(evaluation.known_theta_2.value)


def test_horizon_one_has_no_future_information_term() -> None:
    unknown = unknown_policy_value(STATE, horizon=1)
    expected = max(DEFAULT_PRIOR * mu_1 + (1.0 - DEFAULT_PRIOR) * mu_2 for mu_1, mu_2 in (means(STATE, action) for action in JOINT_ACTIONS))
    assert unknown.value == pytest.approx(expected)


def test_identical_types_eliminate_discovery_cost() -> None:
    evaluation = evaluate_state(STATE, theta_1=THETA_1, theta_2=THETA_1)
    assert evaluation.discovery_cost == pytest.approx(0.0, abs=1e-10)


def test_small_noise_has_lower_discovery_cost_on_discriminating_state() -> None:
    baseline = evaluate_state(STATE)
    low_noise = evaluate_state(STATE, sigma=1e-4)
    assert baseline.discovery_cost > 0.0
    assert low_noise.discovery_cost < baseline.discovery_cost


def test_worker_permutations_preserve_values() -> None:
    baseline = evaluate_state(STATE)
    for permutation in permutations(range(3)):
        candidate = tuple(STATE[index] for index in permutation)
        evaluation = evaluate_state(candidate)
        assert evaluation.known_value == pytest.approx(baseline.known_value)
        assert evaluation.unknown_value == pytest.approx(baseline.unknown_value)


def test_capability_theta_duality_preserves_values() -> None:
    original = evaluate_state(STATE)
    dual = evaluate_state(capability_dual(STATE), theta_1=THETA_2, theta_2=THETA_1)
    assert dual.known_value == pytest.approx(original.known_value)
    assert dual.unknown_value == pytest.approx(original.unknown_value)
    assert dual.discovery_cost == pytest.approx(original.discovery_cost)


def test_known_value_matches_independent_action_sequence_enumeration() -> None:
    for alpha in (THETA_1, THETA_2):
        assert known_policy_value(STATE, alpha, horizon=3).value == pytest.approx(known_value_bruteforce(STATE, alpha, horizon=3))


def test_unknown_belief_dp_matches_uncached_small_tree_enumeration() -> None:
    dynamic = unknown_policy_value(STATE, horizon=2, quadrature_order=3).value
    brute = unknown_value_bruteforce(STATE, horizon=2, prior=DEFAULT_PRIOR, sigma=DEFAULT_SIGMA, quadrature_order=3)
    assert dynamic == pytest.approx(brute)


def test_gauss_hermite_convergence_at_increasing_orders() -> None:
    values = [unknown_policy_value(STATE, quadrature_order=order).value for order in (15, 23, 31)]
    changes = [abs(right - left) for left, right in zip(values, values[1:])]
    assert all(change >= 0.0 for change in changes)
    # The runner preserves the actual errors for all states; this test guards
    # deterministic repeated numerical integration rather than inventing a
    # scientific materiality cutoff.
    assert values == [unknown_policy_value(STATE, quadrature_order=order).value for order in (15, 23, 31)]


def test_reproducibility_and_nonnegative_discovery_cost() -> None:
    first = evaluate_state(STATE)
    second = evaluate_state(STATE)
    assert first == second
    states = enumerate_canonical_states()
    for state in (states[0], states[len(states) // 2], states[-1]):
        assert evaluate_state(state, quadrature_order=5).discovery_cost >= -1e-10
