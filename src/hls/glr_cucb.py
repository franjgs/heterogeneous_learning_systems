"""GLR-CUCB for Bernoulli combinatorial semi-bandits.

This is the global-restart GLR-CUCB of Zhou et al. (AAAI 2020), adapted to
HLS's additive bipartite-matching oracle. Rewards are supplied only for the
selected matching edges.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Iterable

Pair = tuple[int, int]


def bernoulli_kl(p: float, q: float) -> float:
    """Binary relative entropy, with the standard endpoint conventions."""
    p, q = min(1.0, max(0.0, p)), min(1.0, max(0.0, q))
    value = 0.0
    if p > 0:
        if q == 0:
            return math.inf
        value += p * math.log(p / q)
    if p < 1:
        if q == 1:
            return math.inf
        value += (1 - p) * math.log((1 - p) / (1 - q))
    return value


def glr_statistic(samples: Iterable[float]) -> float:
    """Equation (1): maximum two-segment Bernoulli log-likelihood ratio."""
    values = tuple(float(x) for x in samples)
    n = len(values)
    if n < 2:
        return 0.0
    total = sum(values)
    best = 0.0
    left_sum = 0.0
    for split in range(1, n):
        left_sum += values[split - 1]
        left_mean = left_sum / split
        right_mean = (total - left_sum) / (n - split)
        pooled = total / n
        statistic = split * bernoulli_kl(left_mean, pooled)
        statistic += (n - split) * bernoulli_kl(right_mean, pooled)
        best = max(best, statistic)
    return best


def glr_threshold(n: int, delta: float) -> float:
    """Paper threshold using its published upper bound for Q (Eq. 13 ref.).

    Zhou et al. define beta(n,delta)=2 Q(log(3 n^(3/2)/delta)/2)
    + 6 log(1+log(n)). Their cited bound Q(x) <= x+4log(1+x+sqrt(2x))
    is used here, giving a conservative threshold without numerical inversion.
    """
    if n < 2 or not 0 < delta < 1:
        raise ValueError("n must be >= 2 and delta must lie in (0, 1)")
    x = max(5.0, math.log(3 * n ** 1.5 / delta) / 2)
    q_upper = x + 4 * math.log(1 + x + math.sqrt(2 * x))
    return 2 * q_upper + 6 * math.log1p(math.log(n))


class GLRCUCB:
    """Global-restart GLR-CUCB state for a finite bipartite semi-bandit."""

    def __init__(self, n_agents: int, n_tasks: int, *, horizon: int,
                 epsilon: float, delta: float, seed: int,
                 initial_history: dict[Pair, Iterable[tuple[int, float]]] | None = None):
        if min(n_agents, n_tasks, horizon) < 1 or not 0 < epsilon < 1:
            raise ValueError("invalid dimensions, horizon or epsilon")
        if not 0 < delta < 1:
            raise ValueError("delta must lie in (0, 1)")
        self.n_agents, self.n_tasks, self.horizon = n_agents, n_tasks, horizon
        self.n_arms = n_agents * n_tasks
        self.epsilon, self.delta = epsilon, delta
        self.rng = random.Random(seed)
        self.tau = 0
        self._samples: dict[Pair, list[float]] = defaultdict(list)
        self._times: dict[Pair, list[int]] = defaultdict(list)
        self.detections: list[dict] = []
        self.last_statistics: dict[Pair, tuple[float, float, int]] = {}
        if initial_history:
            for pair, rows in initial_history.items():
                for time, reward in rows:
                    self._samples[pair].append(float(reward))
                    self._times[pair].append(int(time))
            if self._times:
                self.tau = max((t for ts in self._times.values() for t in ts), default=-1)
                # Calibration is common external initialization; GLR starts
                # from its end, carrying the common observations as its data.
                self.tau = max(0, self.tau)

    def score_matrix(self, period: int) -> tuple[tuple[float, ...], ...]:
        elapsed = max(1, period - self.tau)
        log_time = math.log(max(1, elapsed))
        rows = []
        for i in range(self.n_agents):
            row = []
            for k in range(self.n_tasks):
                n = len(self._samples[(i, k)])
                mean = sum(self._samples[(i, k)]) / n if n else 0.5
                row.append(mean + math.sqrt(3 * log_time / (2 * n)) if n else 1e6)
            rows.append(tuple(row))
        return tuple(rows)

    def forced_arm(self, period: int) -> Pair | None:
        """Algorithm 2 cyclic forced exploration; None means use CUCB oracle."""
        cycle = max(self.n_arms, math.floor(self.n_arms / self.epsilon))
        # Convert the paper's 1-indexed round/arm labels to Python's 0-index.
        slot = (period - self.tau - 1) % cycle
        if slot < self.n_arms:
            return divmod(slot, self.n_tasks)
        return None

    def forced_matching(self, arm: Pair, matchings: Iterable[tuple[Pair, ...]]) -> tuple[Pair, ...]:
        candidates = [m for m in matchings if arm in m]
        if not candidates:
            raise ValueError(f"no feasible superarm contains {arm}")
        return self.rng.choice(candidates)

    def update(self, period: int, selected: Iterable[Pair], feedback: dict[Pair, float]) -> None:
        selected = tuple(selected)
        if set(feedback) != set(selected) or len(set(selected)) != len(selected):
            raise ValueError("feedback must exactly match unique selected edges")
        changed = []
        for pair in selected:
            reward = float(feedback[pair])
            if pair[0] not in range(self.n_agents) or pair[1] not in range(self.n_tasks):
                raise ValueError("selected pair is out of range")
            if reward not in (0.0, 1.0):
                raise ValueError("GLR-CUCB requires Bernoulli feedback")
            self._samples[pair].append(reward)
            self._times[pair].append(period)
            n = len(self._samples[pair])
            statistic = glr_statistic(self._samples[pair])
            threshold = glr_threshold(n, self.delta) if n >= 2 else math.inf
            self.last_statistics[pair] = (statistic, threshold, n)
            if statistic >= threshold:
                changed.append((pair, statistic, threshold, n))
        if changed:
            self.detections.append({"period": period, "arms": [list(x[0]) for x in changed],
                                    "statistics": [x[1] for x in changed],
                                    "thresholds": [x[2] for x in changed],
                                    "samples": [x[3] for x in changed]})
            # Paper Algorithm 2 globally resets all base-arm statistics.
            self._samples = defaultdict(list)
            self._times = defaultdict(list)
            self.tau = period

