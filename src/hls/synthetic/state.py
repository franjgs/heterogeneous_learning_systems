"""Immutable state objects for synthetic HLS worlds."""

from __future__ import annotations

from dataclasses import dataclass
import math


CompetenceMatrix = tuple[tuple[float, ...], ...]


@dataclass(frozen=True)
class WorldState:
    """Collective competence state at one world time.

    Shape is deliberately general: any positive number of learners and
    competence dimensions is admissible at this layer.
    """

    competence: CompetenceMatrix
    time: int = 0
    resources: tuple[tuple[str, float], ...] = ()

    def __post_init__(self) -> None:
        if self.time < 0:
            raise ValueError("state time must be non-negative")
        if not self.competence or not self.competence[0]:
            raise ValueError("competence state must have positive M and K")
        width = len(self.competence[0])
        if any(len(row) != width for row in self.competence):
            raise ValueError("competence state must be rectangular")
        if any(not math.isfinite(float(value)) for row in self.competence for value in row):
            raise ValueError("competence entries must be finite")

    @property
    def n_learners(self) -> int:
        return len(self.competence)

    @property
    def n_competences(self) -> int:
        return len(self.competence[0])

    def resource_dict(self) -> dict[str, float]:
        """Return the immutable resource payload as a plain mapping."""
        return dict(self.resources)

    def advanced(
        self,
        competence: CompetenceMatrix,
        *,
        resources: tuple[tuple[str, float], ...] | None = None,
    ) -> "WorldState":
        """Return a new state; the current state is never mutated."""
        return WorldState(
            competence=competence,
            time=self.time + 1,
            resources=self.resources if resources is None else resources,
        )
