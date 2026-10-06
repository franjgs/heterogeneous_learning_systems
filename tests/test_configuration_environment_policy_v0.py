"""Focused controls for the deterministic configuration × environment prototype."""

from __future__ import annotations

import pytest

from hls.configuration_environment_policy_v0 import (
    CONFIGURATIONS,
    ENVIRONMENTS,
    brute_force_joint_value,
    evaluate_matrix,
    evaluate_policy,
    reward,
    total_budget,
    transition,
)


def test_configurations_have_exactly_equal_initial_budget() -> None:
    budgets = {name: total_budget(state) for name, state in CONFIGURATIONS.items()}
    assert set(budgets.values()) == {3.0}
    by_capability = {
        name: tuple(sum(row[task] for row in state) for task in range(2))
        for name, state in CONFIGURATIONS.items()
    }
    assert set(by_capability.values()) == {(1.5, 1.5)}


def test_disabled_learning_is_the_identity_transition() -> None:
    state = CONFIGURATIONS["DIVERSE"]
    for agent in range(3):
        for task in range(2):
            assert transition(state, agent, task, 0.0) == state


def test_greedy_policy_only_uses_immediate_reward_maximizers() -> None:
    state = CONFIGURATIONS["DIVERSE"]
    sequence = ENVIRONMENTS["E0_STABLE_BALANCED"]
    evaluation = evaluate_policy(state, sequence, 0.5, "GREEDY_USE")
    task = sequence[0]
    best_reward = max(reward(state, agent, task) for agent in range(3))
    assert evaluation.first_actions
    assert all(reward(state, agent, task) == pytest.approx(best_reward) for agent in evaluation.first_actions)


def test_joint_dp_weakly_dominates_fair_greedy_over_the_full_matrix() -> None:
    for enabled in (True, False):
        for point in evaluate_matrix(learning_scale=0.5, development_enabled=enabled):
            assert point.joint_dp.value >= point.greedy.value - 1e-12


def test_evaluation_is_deterministic() -> None:
    assert evaluate_matrix(learning_scale=0.5, development_enabled=True) == evaluate_matrix(
        learning_scale=0.5, development_enabled=True
    )


def test_dp_matches_independent_brute_force_on_a_tiny_horizon() -> None:
    state = CONFIGURATIONS["SPECIALIST"]
    sequence = (0, 1, 0)
    dynamic = evaluate_policy(state, sequence, 0.5, "JOINT_DP")
    assert dynamic.value == pytest.approx(brute_force_joint_value(state, sequence, 0.5))
