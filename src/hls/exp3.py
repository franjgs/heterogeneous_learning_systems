"""Minimal implementation of EXP3 for bounded-reward arm selection.

The public interaction deliberately separates selection from feedback: after
``select`` the caller can report one scalar reward only, for the selected arm.
This matches the bandit information structure and prevents the policy API from
receiving the unobserved reward vector.
"""

from __future__ import annotations

import math
import random


class Exp3:
    """EXP3 (weak-regret variant) from Auer et al. (2002), Figure 1.

    Rewards must be in [0, 1]. A call to :meth:`select` must be followed by
    exactly one call to :meth:`observe_reward` before another selection.
    ``rng`` is supplied by the caller so policy randomness remains separate
    from environment randomness.
    """

    def __init__(self, n_arms: int, gamma: float) -> None:
        if isinstance(n_arms, bool) or not isinstance(n_arms, int) or n_arms < 1:
            raise ValueError("n_arms must be a positive integer")
        if not math.isfinite(gamma) or not 0.0 < gamma <= 1.0:
            raise ValueError("gamma must be finite and in (0, 1]")
        self.n_arms = n_arms
        self.gamma = float(gamma)
        self._weights = [1.0] * n_arms
        self._pending: tuple[int, float] | None = None

    @property
    def weights(self) -> tuple[float, ...]:
        """Current positive weights (a common scale has no policy meaning)."""
        return tuple(self._weights)

    @property
    def probabilities(self) -> tuple[float, ...]:
        total = math.fsum(self._weights)
        return tuple(
            (1.0 - self.gamma) * weight / total + self.gamma / self.n_arms
            for weight in self._weights
        )

    def select(self, rng: random.Random) -> int:
        """Sample an arm from the current EXP3 distribution."""
        if self._pending is not None:
            raise RuntimeError("observe the selected arm's reward before selecting again")
        probabilities = self.probabilities
        draw = rng.random()
        cumulative = 0.0
        for arm, probability in enumerate(probabilities):
            cumulative += probability
            if draw < cumulative or arm == self.n_arms - 1:
                self._pending = (arm, probability)
                return arm
        raise AssertionError("unreachable categorical-sampling state")

    def observe_reward(self, reward: float) -> None:
        """Update from the one observed scalar reward for the pending arm."""
        if self._pending is None:
            raise RuntimeError("select an arm before observing a reward")
        if isinstance(reward, bool) or not isinstance(reward, (int, float)):
            raise ValueError("reward must be a scalar in [0, 1]")
        reward = float(reward)
        if not math.isfinite(reward) or not 0.0 <= reward <= 1.0:
            raise ValueError("reward must be finite and in [0, 1]")

        arm, selected_probability = self._pending
        estimate = reward / selected_probability
        exponent = self.gamma * estimate / self.n_arms
        updated = list(self._weights)
        updated[arm] *= math.exp(exponent)

        # A common rescaling leaves all probabilities unchanged and prevents
        # avoidable overflow in finite, long-running evaluations.
        scale = max(updated)
        self._weights = [weight / scale for weight in updated]
        if any(not math.isfinite(weight) or weight <= 0.0 for weight in self._weights):
            raise FloatingPointError("EXP3 weight lost finite positive representation")
        self._pending = None


def gamma_for_horizon(n_arms: int, horizon: int) -> float:
    """Corollary 3.2 tuning with the paper's valid upper bound g=T."""
    if n_arms < 1 or horizon < 1:
        raise ValueError("n_arms and horizon must be positive")
    if n_arms == 1:
        return 1.0
    return min(1.0, math.sqrt(n_arms * math.log(n_arms) / ((math.e - 1.0) * horizon)))


def uniform_probabilities(n_arms: int) -> tuple[float, ...]:
    if n_arms < 1:
        raise ValueError("n_arms must be positive")
    return (1.0 / n_arms,) * n_arms

