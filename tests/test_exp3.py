import math
import random

import pytest

from hls.exp3 import Exp3, gamma_for_horizon, uniform_probabilities


class FixedRandom:
    def __init__(self, value):
        self.value = value

    def random(self):
        return self.value


def test_probabilities_are_normalized_and_include_uniform_exploration():
    policy = Exp3(n_arms=3, gamma=0.3)
    assert math.isclose(sum(policy.probabilities), 1.0)
    assert all(p >= 0.1 for p in policy.probabilities)
    assert policy.probabilities == pytest.approx((1 / 3, 1 / 3, 1 / 3))


def test_importance_weighted_exponential_update_matches_exp3_formula():
    policy = Exp3(n_arms=3, gamma=0.3)
    arm = policy.select(FixedRandom(0.1))
    assert arm == 0
    probability = 1 / 3
    policy.observe_reward(0.6)

    # Figure 1: w_i <- w_i exp(gamma * (x_i / p_i) / K).
    expected_ratio = math.exp(0.3 * (0.6 / probability) / 3)
    weights = policy.weights  # common rescaling is policy-invariant
    assert weights[0] / weights[1] == pytest.approx(expected_ratio)
    assert all(weight > 0.0 for weight in weights)


def test_selection_and_reward_feedback_are_reproducible():
    def run(seed):
        policy = Exp3(n_arms=3, gamma=0.2)
        rng = random.Random(seed)
        trace = []
        rewards = (0.8, 0.4, 0.1)
        for _ in range(50):
            probabilities = policy.probabilities
            arm = policy.select(rng)
            trace.append((arm, probabilities))
            policy.observe_reward(rewards[arm])
        return trace, policy.weights

    assert run(712) == run(712)
    assert run(712) != run(713)


@pytest.mark.parametrize("reward", [-0.01, 1.01, float("nan"), float("inf"), [0.2, 0.8]])
def test_rejects_non_scalar_or_unbounded_reward(reward):
    policy = Exp3(n_arms=2, gamma=0.2)
    policy.select(FixedRandom(0.1))
    with pytest.raises(ValueError):
        policy.observe_reward(reward)


def test_feedback_api_cannot_update_from_unobserved_reward_vector():
    policy = Exp3(n_arms=3, gamma=0.2)
    with pytest.raises(RuntimeError, match="select an arm"):
        policy.observe_reward(0.5)
    policy.select(FixedRandom(0.1))
    with pytest.raises(ValueError, match="scalar"):
        policy.observe_reward((1.0, 0.0, 0.0))
    with pytest.raises(RuntimeError, match="before selecting again"):
        policy.select(FixedRandom(0.1))


def test_requires_one_feedback_per_selection_and_valid_tuning():
    policy = Exp3(n_arms=2, gamma=0.2)
    policy.select(FixedRandom(0.1))
    with pytest.raises(RuntimeError):
        policy.select(FixedRandom(0.1))
    policy.observe_reward(0.5)
    assert sum(uniform_probabilities(4)) == pytest.approx(1.0)
    assert 0.0 < gamma_for_horizon(3, 300) <= 1.0
    with pytest.raises(ValueError):
        Exp3(0, 0.2)
    with pytest.raises(ValueError):
        Exp3(2, 0.0)


def test_exp3_learns_simple_known_deterministic_bandit():
    """A simple algorithm check, not an HLS experiment or superiority claim."""
    rewards = (1.0, 0.0, 0.0)
    horizon = 300
    gamma = gamma_for_horizon(len(rewards), horizon)
    exp3_total = 0.0
    uniform_total = 0.0
    repetitions = 40
    for seed in range(repetitions):
        policy = Exp3(len(rewards), gamma)
        exp3_rng = random.Random(seed)
        uniform_rng = random.Random(10_000 + seed)
        for _ in range(horizon):
            arm = policy.select(exp3_rng)
            exp3_total += rewards[arm]
            policy.observe_reward(rewards[arm])
            uniform_total += rewards[uniform_rng.randrange(len(rewards))]
    assert exp3_total / repetitions > uniform_total / repetitions

