"""C5 dynamic task-demand processes for G0.

C5 extends Theta_Q with stationary stochastic, non-stationary, and Markov
demand. Randomness remains external and injectable: task processes never own
an RNG.

FiniteTaskSequence remains the deterministic control.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Hashable, Mapping, Sequence

from .interfaces import RandomSource
from .state import WorldState


Task = Hashable
Distribution = Mapping[Task, float]


def _validated_distribution(distribution: Distribution) -> Mapping[Task, float]:
    values = dict(distribution)
    if not values:
        raise ValueError("task distribution must not be empty")
    if any(
        not math.isfinite(float(p)) or p < 0.0
        for p in values.values()
    ):
        raise ValueError("task probabilities must be finite and non-negative")
    total = sum(values.values())
    if abs(total - 1.0) > 1e-12:
        raise ValueError("task probabilities must sum to one")
    if total <= 0.0:
        raise ValueError("task distribution must have positive mass")
    return MappingProxyType(values)


def _sample(distribution: Mapping[Task, float], randomness: RandomSource) -> Task:
    u = randomness.random()
    cumulative = 0.0
    last = None
    for task, probability in distribution.items():
        last = task
        cumulative += probability
        if u < cumulative:
            return task
    # Protect against floating-point accumulation at the upper boundary.
    assert last is not None
    return last


@dataclass(frozen=True)
class StationaryTaskDemand:
    """IID task demand with a fixed distribution."""

    distribution: Distribution

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "distribution", _validated_distribution(self.distribution)
        )

    def sample_task(
        self,
        time: int,
        state: WorldState,
        history: Sequence[object],
        randomness: RandomSource,
    ) -> Task:
        del time, state, history
        return _sample(self.distribution, randomness)


@dataclass(frozen=True)
class NonStationaryTaskDemand:
    """Time-indexed task distributions."""

    distributions: Mapping[int, Distribution]

    def __post_init__(self) -> None:
        values = dict(self.distributions)
        if not values or any(time < 0 for time in values):
            raise ValueError("non-stationary demand requires non-negative times")
        validated = {
            time: _validated_distribution(distribution)
            for time, distribution in values.items()
        }
        object.__setattr__(
            self, "distributions", MappingProxyType(validated)
        )

    def sample_task(
        self,
        time: int,
        state: WorldState,
        history: Sequence[object],
        randomness: RandomSource,
    ) -> Task:
        del state, history
        try:
            distribution = self.distributions[time]
        except KeyError as error:
            raise IndexError("task distribution is unidentified for this time") from error
        return _sample(distribution, randomness)


@dataclass(frozen=True)
class MarkovTaskDemand:
    """First-order Markov task demand.

    initial_distribution generates Q_0. For t>0, the previous realized task is
    read from history and selects a transition row.
    """

    initial_distribution: Distribution
    transitions: Mapping[Task, Distribution]

    def __post_init__(self) -> None:
        initial = _validated_distribution(self.initial_distribution)
        transitions = {
            task: _validated_distribution(distribution)
            for task, distribution in dict(self.transitions).items()
        }

        task_set = set(initial)
        if set(transitions) != task_set:
            raise ValueError(
                "Markov transitions must contain exactly one row per task"
            )
        if any(set(row) != task_set for row in transitions.values()):
            raise ValueError(
                "every Markov transition row must use the same task set"
            )

        object.__setattr__(self, "initial_distribution", initial)
        object.__setattr__(
            self, "transitions", MappingProxyType(transitions)
        )

    def sample_task(
        self,
        time: int,
        state: WorldState,
        history: Sequence[object],
        randomness: RandomSource,
    ) -> Task:
        del state
        if time == 0:
            return _sample(self.initial_distribution, randomness)

        if not history:
            raise ValueError("Markov demand requires previous task history")

        previous = getattr(history[-1], "task", None)
        if previous not in self.transitions:
            raise ValueError("previous task is unavailable to Markov demand")

        return _sample(self.transitions[previous], randomness)
