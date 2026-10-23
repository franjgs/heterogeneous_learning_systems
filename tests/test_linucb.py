import math
import random
from types import SimpleNamespace

import pytest

from hls.linucb import LinUCBDisjoint, alpha_from_delta
from hls.synthetic.c5 import NonStationaryTaskDemand
from hls.synthetic.state import WorldState


def context(index, dimensions=3):
    return tuple(1.0 if j == index else 0.0 for j in range(dimensions))


def same_context_for_all(task_index, n_arms=3, n_features=3):
    vector = context(task_index, n_features)
    return (vector,) * n_arms


def test_disjoint_linucb_initial_score_is_the_confidence_term():
    policy = LinUCBDisjoint(3, 3, alpha=0.7)
    scores = policy.scores(same_context_for_all(1))
    assert scores == pytest.approx((0.7, 0.7, 0.7))
    assert policy.design_matrices == tuple(
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)) for _ in range(3)
    )


def test_ridge_estimate_ucb_and_selected_arm_update_match_paper_equations():
    policy = LinUCBDisjoint(2, 2, alpha=0.5)
    contexts = ((1.0, 0.0), (1.0, 0.0))
    assert policy.select(contexts) == 0  # deterministic first-arm tie break
    policy.observe_reward(1.0)

    # A_0 = I + xx', b_0 = r*x; A_1,b_1 are unchanged.
    assert policy.design_matrices[0] == ((2.0, 0.0), (0.0, 1.0))
    assert policy.response_vectors[0] == (1.0, 0.0)
    assert policy.design_matrices[1] == ((1.0, 0.0), (0.0, 1.0))
    assert policy.response_vectors[1] == (0.0, 0.0)
    assert policy.coefficient_estimates[0] == pytest.approx((0.5, 0.0))
    # Score 0: x' theta + alpha sqrt(x' A^-1 x) = .5 + .5/sqrt(2).
    assert policy.scores(contexts) == pytest.approx((0.5 + 0.5 / math.sqrt(2), 0.5))


def test_contextual_preferences_are_learned_from_chosen_arm_feedback():
    policy = LinUCBDisjoint(3, 3, alpha=0.5)
    for _ in range(80):
        for task in range(3):
            selected = policy.select(same_context_for_all(task))
            policy.observe_reward(float(selected == task))

    # In this deterministic task-agent system, each task has its own best agent.
    for task in range(3):
        assert policy.select(same_context_for_all(task)) == task
        policy.observe_reward(1.0)


def test_policy_is_reproducible_and_ties_are_deterministic():
    def run():
        policy = LinUCBDisjoint(3, 3, alpha=0.8)
        trace = []
        for task in (2, 0, 2, 1, 0, 1) * 8:
            arm = policy.select(same_context_for_all(task))
            trace.append((task, arm, policy.scores(same_context_for_all(task))))
            policy.observe_reward(float(arm == task))
        return trace, policy.design_matrices, policy.response_vectors

    assert run() == run()
    assert LinUCBDisjoint(3, 3, 1.0).select(same_context_for_all(0)) == 0


def test_only_chosen_arm_feedback_is_accepted():
    policy = LinUCBDisjoint(3, 3, alpha=1.0)
    with pytest.raises(RuntimeError, match="select an arm"):
        policy.observe_reward(0.5)
    policy.select(same_context_for_all(0))
    with pytest.raises(ValueError, match="scalar"):
        policy.observe_reward((1.0, 0.0, 0.0))
    with pytest.raises(RuntimeError, match="before selecting again"):
        policy.select(same_context_for_all(1))


@pytest.mark.parametrize("reward", [-0.1, 1.1, float("nan"), float("inf")])
def test_rewards_must_be_finite_and_bounded(reward):
    policy = LinUCBDisjoint(2, 2, alpha=0.5)
    policy.select(((1.0, 0.0), (1.0, 0.0)))
    with pytest.raises(ValueError):
        policy.observe_reward(reward)


def test_context_dimensions_and_delta_are_validated():
    with pytest.raises(ValueError):
        LinUCBDisjoint(0, 2, 1.0)
    with pytest.raises(ValueError):
        LinUCBDisjoint(2, 0, 1.0)
    with pytest.raises(ValueError):
        LinUCBDisjoint(2, 2, -0.1)
    with pytest.raises(ValueError):
        LinUCBDisjoint(2, 2, 1.0).scores(((1.0,), (1.0,)))
    assert alpha_from_delta(0.05) == pytest.approx(1.0 + math.sqrt(math.log(40) / 2))
    with pytest.raises(ValueError):
        alpha_from_delta(1.0)


def test_hls_context_and_potential_reward_replay_is_reproducible():
    horizon = 90
    competence = ((0.85, 0.20, 0.20), (0.20, 0.85, 0.20), (0.20, 0.20, 0.85))
    distributions = {
        t: ({"task_0": 0.7, "task_1": 0.2, "task_2": 0.1}
            if t < 30 else
            {"task_0": 0.1, "task_1": 0.2, "task_2": 0.7}
            if t < 60 else
            {"task_0": 0.2, "task_1": 0.7, "task_2": 0.1})
        for t in range(horizon)
    }
    process = NonStationaryTaskDemand(distributions)

    def replay(seed):
        task_rng, reward_rng = random.Random(seed), random.Random(1000 + seed)
        state = WorldState(competence)
        history, tasks = [], []
        for period in range(horizon):
            task = process.sample_task(period, state, history, task_rng)
            tasks.append(task)
            history.append(SimpleNamespace(task=task))
        outcomes = [
            tuple(float(reward_rng.random() < competence[agent][int(task[-1])])
                  for agent in range(3))
            for task in tasks
        ]
        return tasks, outcomes

    first = replay(932)
    assert first == replay(932)
    assert first != replay(933)
    assert len(first[0]) == len(first[1]) == horizon
    assert all(len(row) == 3 and set(row).issubset({0.0, 1.0}) for row in first[1])


def test_hls_contexts_have_distinct_preferred_agents():
    competence = ((0.85, 0.20, 0.20), (0.20, 0.85, 0.20), (0.20, 0.20, 0.85))
    best = [max(range(3), key=lambda agent: competence[agent][task])
            for task in range(3)]
    assert best == [0, 1, 2]

