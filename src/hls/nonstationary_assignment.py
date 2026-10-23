"""Per-edge UCB estimators for experimental nonstationary assignment.

The estimators expose only reward feedback supplied for selected pairs. Their
combination with simultaneous bipartite matching is an HLS adaptation; the
single-play bandit guarantees of the cited papers are not inherited here.
"""

from __future__ import annotations

from dataclasses import dataclass
from bisect import bisect_left
from math import log, sqrt
from typing import Iterable


Pair = tuple[int, int]


@dataclass(frozen=True)
class PairObservation:
    period: int
    reward: float


class PairwiseBanditEstimator:
    """Per-pair UCB indices or empirical means on N×K pair rewards."""

    def __init__(self, n_agents: int, n_tasks: int, *, method: str,
                 window: int, xi: float = 1.0):
        if n_agents < 1 or n_tasks < 1 or window < 1 or xi <= 0:
            raise ValueError("dimensions, window and xi must be positive")
        if method not in {"ucb1", "sw_ucb", "recent_mean", "global_mean"}:
            raise ValueError("unknown estimator method")
        self.n_agents = n_agents
        self.n_tasks = n_tasks
        self.method = method
        self.window = window
        self.xi = float(xi)
        self._history: dict[Pair, list[PairObservation]] = {
            (i, k): [] for i in range(n_agents) for k in range(n_tasks)
        }
        # Prefix sums preserve the estimator equations while avoiding a full
        # scan of each pair's history at every decision (important for the
        # 10,000-period paired S3b-E1 protocol).
        self._periods: dict[Pair, list[int]] = {pair: [] for pair in self._history}
        self._prefix_rewards: dict[Pair, list[float]] = {pair: [0.0] for pair in self._history}
        self._period = -1
        self._additional_observation_periods: set[int] = set()

    def _statistics(self, pair: Pair, period: int) -> tuple[int, float]:
        periods = self._periods[pair]
        prefix = self._prefix_rewards[pair]
        if self.method in {"ucb1", "global_mean"}:
            start = 0
        else:
            start = bisect_left(periods, period - self.window)
        end = bisect_left(periods, period)
        return end - start, prefix[end] - prefix[start]

    @property
    def observations(self) -> dict[Pair, tuple[PairObservation, ...]]:
        return {pair: tuple(rows) for pair, rows in self._history.items()}

    def update(self, period: int, selected: Iterable[Pair], feedback: dict[Pair, float]) -> None:
        selected = tuple(selected)
        if period <= self._period:
            raise ValueError("periods must be strictly increasing")
        if set(feedback) != set(selected):
            raise ValueError("feedback must contain exactly the selected pairs")
        if len(set(selected)) != len(selected):
            raise ValueError("selected pairs must be unique")
        for i, k in selected:
            if (i, k) not in self._history:
                raise ValueError("selected pair is out of range")
            reward = float(feedback[(i, k)])
            if not 0.0 <= reward <= 1.0:
                raise ValueError("rewards must lie in [0, 1]")
            self._history[(i, k)].append(PairObservation(period, reward))
            self._periods[(i, k)].append(period)
            self._prefix_rewards[(i, k)].append(self._prefix_rewards[(i, k)][-1] + reward)
        self._period = period

    def update_additional_observation(self, period: int, pair: Pair, reward: float) -> None:
        """Add one extra feedback sample stamped at the current global period.

        This is for observation interventions where an extra outcome is
        sampled after the ordinary update for the same period. It does not
        advance time; the sample enters the temporal window alongside other
        observations with that timestamp.
        """
        if period != self._period or period < 0:
            raise ValueError("an additional observation must use the current period")
        if period in self._additional_observation_periods:
            raise ValueError("only one additional observation is allowed per period")
        if pair not in self._history:
            raise ValueError("additional observation pair is out of range")
        reward = float(reward)
        if not 0.0 <= reward <= 1.0:
            raise ValueError("rewards must lie in [0, 1]")
        self._history[pair].append(PairObservation(period, reward))
        self._periods[pair].append(period)
        self._prefix_rewards[pair].append(self._prefix_rewards[pair][-1] + reward)
        self._additional_observation_periods.add(period)

    def score_matrix(self, period: int) -> tuple[tuple[float, ...], ...]:
        """Return finite assignment indices using no environment parameters."""
        if period < 0:
            raise ValueError("period must be nonnegative")
        # A finite sentinel dominates every finite UCB1/SW-UCB index at this
        # horizon, allowing the existing finite-valued matching solver to
        # choose recently unobserved pairs without exposing hidden rewards.
        sentinel = 2.0 + sqrt(2.0 * log(max(2, period + 1)))
        rows = []
        for i in range(self.n_agents):
            row = []
            for k in range(self.n_tasks):
                history = self._history[(i, k)]
                count, reward_sum = self._statistics((i, k), period)
                if not count:
                    # No valid observation in the global-period window:
                    # optimistic unseen-pair index for UCB variants, neutral
                    # 1/2 prior for the no-exploration recent-mean comparator.
                    row.append(0.5 if self.method in {"recent_mean", "global_mean"} else sentinel)
                    continue
                mean = reward_sum / count
                if self.method in {"recent_mean", "global_mean"}:
                    row.append(mean)
                elif self.method == "ucb1":
                    row.append(mean + sqrt(2.0 * log(max(2, period + 1)) / count))
                else:
                    row.append(mean + sqrt(self.xi * log(max(2, min(period + 1, self.window))) / count))
            rows.append(tuple(row))
        return tuple(rows)


    def empirical_mean_matrix(self, period: int) -> tuple[tuple[float, ...], ...]:
        """Return current per-pair means (neutral 0.5 if the window is empty)."""
        if period < 0:
            raise ValueError("period must be nonnegative")
        matrix = []
        for i in range(self.n_agents):
            row = []
            for k in range(self.n_tasks):
                history = self._history[(i, k)]
                count, reward_sum = self._statistics((i, k), period)
                row.append(reward_sum / count if count else 0.5)
            matrix.append(tuple(row))
        return tuple(matrix)

    def diagnostic_matrix(self, period: int) -> tuple[tuple[dict, ...], ...]:
        """Return observable estimator diagnostics for every pair at a period.

        The `bonus` field is zero for empirical-mean methods and the additive
        confidence term for observed UCB pairs. For an empty UCB history/window,
        `bonus` is None and `index` is the finite unseen-pair sentinel.
        """
        scores = self.score_matrix(period)
        rows = []
        for i in range(self.n_agents):
            row = []
            for k in range(self.n_tasks):
                history = self._history[(i, k)]
                windowed = self.method in {"sw_ucb", "recent_mean"}
                count, reward_sum = self._statistics((i, k), period)
                mean = reward_sum / count if count else 0.5
                if count and self.method == "ucb1":
                    bonus = sqrt(2.0 * log(max(2, period + 1)) / count)
                elif count and self.method == "sw_ucb":
                    bonus = sqrt(self.xi * log(max(2, min(period + 1, self.window))) / count)
                else:
                    bonus = 0.0 if self.method in {"recent_mean", "global_mean"} else None
                row.append({
                    "observations_used": count,
                    "observations_in_window": count if windowed else None,
                    "observations_discarded": len(history) - count if windowed else 0,
                    "estimated_mean": mean,
                    "exploration_bonus": bonus,
                    "index": scores[i][k],
                    "last_observation_age": period - history[-1].period if history else None,
                })
            rows.append(tuple(row))
        return tuple(rows)


class GarivierMoulinesPairwiseEstimator:
    """UCB-1, SW-UCB or discounted-UCB indices on pair rewards.

    UCB-1/SW-UCB retain the paper's bounded-reward confidence expressions;
    discounted-UCB uses the discounted sufficient statistics in Garivier and
    Moulines (2008). Combining these pair indices with matching is an HLS
    adaptation, not the single-play algorithm analyzed in that paper.
    """

    METHODS = {"ucb1", "sw_ucb", "d_ucb"}

    def __init__(self, n_agents: int, n_tasks: int, *, method: str,
                 window: int | None = None, gamma: float | None = None,
                 xi: float = 0.5, reward_bound: float = 1.0):
        if n_agents < 1 or n_tasks < 1 or method not in self.METHODS:
            raise ValueError("invalid dimensions or method")
        if xi <= 0 or reward_bound <= 0:
            raise ValueError("xi and reward_bound must be positive")
        if method == "sw_ucb" and (window is None or window < 1):
            raise ValueError("SW-UCB requires a positive window")
        if method == "d_ucb" and (gamma is None or not 0 < gamma < 1):
            raise ValueError("D-UCB requires gamma in (0, 1)")
        self.n_agents, self.n_tasks = n_agents, n_tasks
        self.method, self.window, self.gamma = method, window, gamma
        self.xi, self.reward_bound = float(xi), float(reward_bound)
        pairs = tuple((i, k) for i in range(n_agents) for k in range(n_tasks))
        self._history: dict[Pair, list[PairObservation]] = {pair: [] for pair in pairs}
        self._raw_sum = {pair: 0.0 for pair in pairs}
        self._raw_count = {pair: 0 for pair in pairs}
        self._window_start_index = {pair: 0 for pair in pairs}
        self._window_sum = {pair: 0.0 for pair in pairs}
        self._window_count = {pair: 0 for pair in pairs}
        self._discounted_sum = {pair: 0.0 for pair in pairs}
        self._discounted_count = {pair: 0.0 for pair in pairs}
        self._period = -1

    @property
    def observations(self) -> dict[Pair, tuple[PairObservation, ...]]:
        return {pair: tuple(rows) for pair, rows in self._history.items()}

    @property
    def discounted_statistics(self) -> dict[Pair, tuple[float, float]]:
        return {pair: (self._discounted_sum[pair], self._discounted_count[pair])
                for pair in self._history}

    def update(self, period: int, selected: Iterable[Pair], feedback: dict[Pair, float]) -> None:
        selected = tuple(selected)
        if period <= self._period:
            raise ValueError("periods must be strictly increasing")
        if len(set(selected)) != len(selected) or set(feedback) != set(selected):
            raise ValueError("feedback must contain exactly the unique selected pairs")
        for pair in selected:
            if pair not in self._history:
                raise ValueError("selected pair is out of range")
            reward = float(feedback[pair])
            if not 0.0 <= reward <= self.reward_bound:
                raise ValueError("reward is outside the declared bound")
        if self.method == "d_ucb":
            gap = 1 if self._period < 0 else period - self._period
            decay = self.gamma ** gap
            for pair in self._history:
                self._discounted_sum[pair] *= decay
                self._discounted_count[pair] *= decay
            for pair in selected:
                self._discounted_sum[pair] += float(feedback[pair])
                self._discounted_count[pair] += 1.0
        for pair in selected:
            reward = float(feedback[pair])
            self._history[pair].append(PairObservation(period, reward))
            self._raw_sum[pair] += reward
            self._raw_count[pair] += 1
            if self.method == "sw_ucb":
                self._window_sum[pair] += reward
                self._window_count[pair] += 1
        self._period = period

    def score_matrix(self, period: int) -> tuple[tuple[float, ...], ...]:
        if period < 0 or period <= self._period:
            raise ValueError("score period must be a future nonnegative period")
        effective_total = sum(self._discounted_count.values())
        t = max(2, period + 1)
        matrix = []
        for i in range(self.n_agents):
            row = []
            for k in range(self.n_tasks):
                pair = (i, k)
                if self.method == "d_ucb":
                    count = self._discounted_count[pair]
                    if count <= 0:
                        row.append(float("inf"))
                        continue
                    mean = self._discounted_sum[pair] / count
                    bonus = (2.0 * self.reward_bound
                             * sqrt(self.xi * log(max(1.0, effective_total)) / count))
                else:
                    if self.method == "sw_ucb":
                        start = period - self.window
                        history = self._history[pair]
                        index = self._window_start_index[pair]
                        while index < len(history) and history[index].period < start:
                            self._window_sum[pair] -= history[index].reward
                            self._window_count[pair] -= 1
                            index += 1
                        self._window_start_index[pair] = index
                        count = self._window_count[pair]
                        total = self._window_sum[pair]
                        log_term = log(max(2, min(t, self.window)))
                    else:
                        count = self._raw_count[pair]
                        total = self._raw_sum[pair]
                        log_term = log(t)
                    if count == 0:
                        row.append(float("inf"))
                        continue
                    mean = total / count
                    bonus = self.reward_bound * sqrt(self.xi * log_term / count)
                row.append(mean + bonus)
            matrix.append(tuple(row))
        return tuple(matrix)


def fixed_score_matrix_from_observations(
    n_agents: int, n_tasks: int, observations: dict[Pair, tuple[PairObservation, ...]],
) -> tuple[tuple[float, ...], ...]:
    """Return the empirical-mean score matrix from common calibration data."""
    matrix = []
    for i in range(n_agents):
        row = []
        for k in range(n_tasks):
            values = [obs.reward for obs in observations[(i, k)]]
            if not values:
                raise ValueError("every pair needs calibration feedback")
            row.append(sum(values) / len(values))
        matrix.append(tuple(row))
    return tuple(tuple(row) for row in matrix)
