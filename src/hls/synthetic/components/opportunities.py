"""Opportunity-generation kernels."""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Hashable, Mapping, Sequence

from ..state import WorldState


@dataclass(frozen=True)
class A1MixtureOpportunityKernel:
    """A1's executor-mixture formula as one OpportunityKernel."""

    baseline: Mapping[Hashable, float]
    executor_values: Mapping[tuple[Hashable, Hashable], float]
    rho: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.rho) or not 0.0 <= self.rho <= 1.0:
            raise ValueError("rho must lie in [0, 1]")
        baseline = dict(self.baseline)
        executor_values = dict(self.executor_values)
        for value in (*baseline.values(), *executor_values.values()):
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError("opportunity primitives must lie in [0, 1]")
        object.__setattr__(self, "baseline", MappingProxyType(baseline))
        object.__setattr__(self, "executor_values", MappingProxyType(executor_values))

    def probability(
        self,
        state: WorldState,
        task: Hashable,
        operational_action: Hashable,
        history: Sequence[object],
    ) -> float:
        del state, history
        try:
            baseline = self.baseline[task]
            executor = self.executor_values[(operational_action, task)]
        except KeyError as error:
            raise ValueError("opportunity primitive is unidentified") from error
        return (1.0 - self.rho) * baseline + self.rho * executor
