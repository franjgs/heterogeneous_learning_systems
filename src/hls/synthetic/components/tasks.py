"""Task-process implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Sequence

from ..state import WorldState


@dataclass(frozen=True)
class FiniteTaskSequence:
    """One minimal deterministic TaskProcess implementation."""

    tasks: tuple[Hashable, ...]

    def __post_init__(self) -> None:
        if not self.tasks:
            raise ValueError("task sequence must not be empty")

    def task_at(
        self,
        time: int,
        state: WorldState,
        history: Sequence[object],
    ) -> Hashable:
        del state, history
        if not 0 <= time < len(self.tasks):
            raise IndexError("task sequence exhausted")
        return self.tasks[time]
