"""Focused controls for the deterministic configuration × environment prototype."""

from __future__ import annotations

import pytest

from hls.configuration_environment_policy_v0 import (
    CONFIGURATIONS,
    ENVIRONMENTS,
    brute_force_joint_value,
    evaluate_fixed,
    evaluate_fixed_best,
    evaluate_matrix,
    evaluate_policy,
    reward,
    total_budget,
    transition,
)
from hls.g3_organizational_value import learning_increment


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


def test_fixed_keeps_the_preselected_agent_for_every_problem(monkeypatch) -> None:
    import hls.configuration_environment_policy_v0 as policy_v0

    original_transition = policy_v0.transition
    assigned_agents = []

    def recording_transition(state, agent, task, learning_scale):
        assigned_agents.append(agent)
        return original_transition(state, agent, task, learning_scale)

    monkeypatch.setattr(policy_v0, "transition", recording_transition)
    sequence = (0, 1, 0, 1, 1, 0)
    evaluation = evaluate_fixed(CONFIGURATIONS["DIVERSE"], sequence, 0.5, 2)
    assert evaluation.policy == "FIXED"
    assert evaluation.fixed_agent == 2
    assert evaluation.first_actions == (2,)
    assert assigned_agents == [2] * len(sequence)


def test_fixed_best_is_the_oracle_maximum_over_three_constant_agents() -> None:
    state = CONFIGURATIONS["SPECIALIST"]
    sequence = (0, 1, 0, 0, 1, 1)
    candidates = tuple(evaluate_fixed(state, sequence, 0.5, agent) for agent in range(3))
    best = evaluate_fixed_best(state, sequence, 0.5)
    assert best.policy == "FIXED_BEST"
    assert best.value == max(candidate.value for candidate in candidates)
    assert best.first_actions == tuple(
        agent for agent, candidate in enumerate(candidates) if candidate.value == best.value
    )


def test_identical_state_assignment_uses_the_same_mis_transition() -> None:
    state = CONFIGURATIONS["DIVERSE"]
    next_state = transition(state, 1, 0, 0.5)
    expected = [list(row) for row in state]
    expected[1][0] += learning_increment(state[1][0], 0.5)
    assert next_state == tuple(tuple(row) for row in expected)
    assert transition(state, 1, 0, 0.0) == state


def test_fixed_greedy_and_dp_share_the_same_transition_for_identical_assignment(monkeypatch) -> None:
    import hls.configuration_environment_policy_v0 as policy_v0

    original_transition = policy_v0.transition
    calls = []

    def recording_transition(state, agent, task, learning_scale):
        result = original_transition(state, agent, task, learning_scale)
        calls.append((state, agent, task, learning_scale, result))
        return result

    monkeypatch.setattr(policy_v0, "transition", recording_transition)
    state = CONFIGURATIONS["GENERALIST"]
    sequence = (0,)
    evaluate_fixed(state, sequence, 0.5, agent=0)
    evaluate_policy(state, sequence, 0.5, "GREEDY_USE")
    evaluate_policy(state, sequence, 0.5, "JOINT_DP")

    same_assignment_results = {
        result
        for call_state, agent, task, scale, result in calls
        if call_state == state and agent == 0 and task == 0 and scale == 0.5
    }
    assert len(same_assignment_results) == 1


def test_fixed_best_is_bounded_by_full_sequence_joint_dp() -> None:
    for state in CONFIGURATIONS.values():
        for sequence in ENVIRONMENTS.values():
            for scale in (0.0, 0.5):
                fixed = evaluate_fixed_best(state, sequence, scale)
                joint = evaluate_policy(state, sequence, scale, "JOINT_DP")
                assert fixed.value <= joint.value + 1e-12
