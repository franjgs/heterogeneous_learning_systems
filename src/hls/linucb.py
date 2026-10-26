"""LinUCB with disjoint linear models (Li et al., 2010, Algorithm 1)."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np


class LinUCBDisjoint:
    """Contextual agent selector with one ridge model per agent/arm.

    Every decision receives one feature vector per arm. After selecting one
    arm, the caller may provide only its scalar reward. This implements the
    disjoint variant in Li et al. §3.1: ``A_a=I``, ``b_a=0``,
    ``theta_a=A_a^-1 b_a``, UCB score ``x' theta + alpha sqrt(x' A^-1 x)``,
    followed by ``A_a += xx'`` and ``b_a += reward*x`` for the chosen arm.
    """

    def __init__(self, n_arms: int, n_features: int, alpha: float) -> None:
        if isinstance(n_arms, bool) or not isinstance(n_arms, int) or n_arms < 1:
            raise ValueError("n_arms must be a positive integer")
        if isinstance(n_features, bool) or not isinstance(n_features, int) or n_features < 1:
            raise ValueError("n_features must be a positive integer")
        if not math.isfinite(alpha) or alpha < 0.0:
            raise ValueError("alpha must be finite and non-negative")
        self.n_arms = n_arms
        self.n_features = n_features
        self.alpha = float(alpha)
        self._A = [np.eye(n_features, dtype=float) for _ in range(n_arms)]
        self._b = [np.zeros(n_features, dtype=float) for _ in range(n_arms)]
        self._pending: tuple[int, np.ndarray] | None = None

    @property
    def design_matrices(self) -> tuple[tuple[tuple[float, ...], ...], ...]:
        return tuple(tuple(tuple(float(v) for v in row) for row in matrix) for matrix in self._A)

    @property
    def response_vectors(self) -> tuple[tuple[float, ...], ...]:
        return tuple(tuple(float(v) for v in vector) for vector in self._b)

    @property
    def coefficient_estimates(self) -> tuple[tuple[float, ...], ...]:
        return tuple(tuple(float(v) for v in np.linalg.solve(matrix, vector))
                     for matrix, vector in zip(self._A, self._b))

    def _validate_contexts(self, contexts: Sequence[Sequence[float]]) -> tuple[np.ndarray, ...]:
        if len(contexts) != self.n_arms:
            raise ValueError("provide exactly one context vector per arm")
        vectors = []
        for context in contexts:
            vector = np.asarray(context, dtype=float)
            if vector.shape != (self.n_features,) or not np.all(np.isfinite(vector)):
                raise ValueError("each context must be a finite vector of n_features")
            vectors.append(vector)
        return tuple(vectors)

    def scores(self, contexts: Sequence[Sequence[float]]) -> tuple[float, ...]:
        """Return current upper-confidence scores without changing policy state."""
        vectors = self._validate_contexts(contexts)
        scores = []
        for matrix, response, context in zip(self._A, self._b, vectors):
            theta = np.linalg.solve(matrix, response)
            inverse_context = np.linalg.solve(matrix, context)
            variance = float(context @ inverse_context)
            if variance < -1e-10:
                raise FloatingPointError("LinUCB confidence quadratic form became negative")
            confidence = math.sqrt(max(0.0, variance))
            scores.append(float(context @ theta + self.alpha * confidence))
        return tuple(scores)

    def select(self, contexts: Sequence[Sequence[float]]) -> int:
        """Choose the maximal-UCB arm; ties go to the first arm in input order."""
        if self._pending is not None:
            raise RuntimeError("observe selected arm reward before selecting again")
        vectors = self._validate_contexts(contexts)
        scores = self.scores(vectors)
        arm = max(range(self.n_arms), key=lambda index: scores[index])
        self._pending = (arm, vectors[arm].copy())
        return arm

    def observe_reward(self, reward: float) -> None:
        """Update only the selected arm's linear model from scalar feedback."""
        if self._pending is None:
            raise RuntimeError("select an arm before observing a reward")
        if isinstance(reward, bool) or not isinstance(reward, (int, float)):
            raise ValueError("reward must be a scalar in [0, 1]")
        reward = float(reward)
        if not math.isfinite(reward) or not 0.0 <= reward <= 1.0:
            raise ValueError("reward must be finite and in [0, 1]")
        arm, context = self._pending
        self._A[arm] += np.outer(context, context)
        self._b[arm] += reward * context
        self._pending = None

    def observe_delayed(self, arm: int, context: Sequence[float], reward: float) -> None:
        """Apply the same selected-arm update when feedback arrives later.

        The caller must retain the originally selected arm/context and call
        this only when that action's reward is observable. This additive
        method supports asynchronous environments without changing the
        existing select/observe_reward contract.
        """
        if isinstance(arm, bool) or not isinstance(arm, int) or not 0 <= arm < self.n_arms:
            raise ValueError("arm must be a valid arm index")
        vector = np.asarray(context, dtype=float)
        if vector.shape != (self.n_features,) or not np.all(np.isfinite(vector)):
            raise ValueError("context must be a finite vector of n_features")
        if isinstance(reward, bool) or not isinstance(reward, (int, float)):
            raise ValueError("reward must be a scalar in [0, 1]")
        reward = float(reward)
        if not math.isfinite(reward) or not 0.0 <= reward <= 1.0:
            raise ValueError("reward must be finite and in [0, 1]")
        self._A[arm] += np.outer(vector, vector)
        self._b[arm] += reward * vector


def alpha_from_delta(delta: float) -> float:
    """Confidence coefficient from Li et al. (2010), Eq. (4)."""
    if not math.isfinite(delta) or not 0.0 < delta < 1.0:
        raise ValueError("delta must lie strictly between 0 and 1")
    return 1.0 + math.sqrt(math.log(2.0 / delta) / 2.0)

