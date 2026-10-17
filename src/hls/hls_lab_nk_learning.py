"""N×K adapter for the existing MIS-v2 learning-by-doing law.

This module generalizes only the dimensions of the state and parameters. The
scalar transition and eta convention remain owned by DISCOVER-v2.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .discover_develop_v2 import capability_after_exposure, eta_to_lambda
from .hls_lab_nk_geometry import CompetenceMatrixNK, ProductiveAllocationNK


@dataclass(frozen=True)
class LearningProfileNK:
    """MIS-v2 one-unit gap-closure parameters, indexed agent × competence."""

    eta: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        try:
            values = tuple(tuple(float(value) for value in row) for row in self.eta)
        except (TypeError, ValueError) as exc:
            raise ValueError("eta must be a numeric N×K matrix") from exc
        if not values or not values[0] or any(len(row) != len(values[0]) for row in values):
            raise ValueError("eta must be a non-empty rectangular N×K matrix")
        for row in values:
            for value in row:
                # MIS-v2 defines eta strictly within (0, 1); eta=0 is not a
                # learning parameter. Disable the mechanism for a no-learning
                # control, as the authoritative implementation does.
                eta_to_lambda(value)
        object.__setattr__(self, "eta", values)

    @property
    def n_agents(self) -> int:
        return len(self.eta)

    @property
    def n_skills(self) -> int:
        return len(self.eta[0])

    def validate_dimensions(self, n_agents: int, n_skills: int) -> None:
        if (self.n_agents, self.n_skills) != (n_agents, n_skills):
            raise ValueError(
                f"MIS-v2 eta has shape {self.n_agents}×{self.n_skills}; "
                f"organization requires {n_agents}×{n_skills}"
            )


def mis_v2_transition_nk(
    competence: CompetenceMatrixNK,
    productive_effort: ProductiveAllocationNK,
    profile: LearningProfileNK,
    *,
    enabled: bool = True,
) -> CompetenceMatrixNK:
    """Apply MIS-v2 independently to each agent-skill cell after production.

    For cell ``(i,k)``, the unchanged authoritative law is
    ``c' = 1 - (1-c) exp(-lambda(eta[i,k]) * effort[i,k])``.
    Zero exposure is an exact identity. No cross-agent or cross-skill transfer
    is introduced. The caller controls timing; the episode runner applies this
    transition only after current-period output and reward are recorded.
    """
    try:
        state = tuple(tuple(float(value) for value in row) for row in competence)
        effort = tuple(tuple(float(value) for value in row) for row in productive_effort)
    except (TypeError, ValueError) as exc:
        raise ValueError("competence and productive effort must be numeric matrices") from exc
    if not state or not state[0] or any(len(row) != len(state[0]) for row in state):
        raise ValueError("competence must be a non-empty rectangular N×K matrix")
    n, k = len(state), len(state[0])
    profile.validate_dimensions(n, k)
    if len(effort) != n or any(len(row) != k for row in effort):
        raise ValueError(f"productive_effort must have shape {n}×{k}")
    for row in state:
        if any(not isfinite(value) or not 0.0 <= value <= 1.0 for value in row):
            raise ValueError("competence values must be finite and lie in [0, 1]")
    for row in effort:
        if any(not isfinite(value) or value < 0.0 for value in row):
            raise ValueError("productive effort must be finite and non-negative")
    if not enabled:
        return state
    return tuple(tuple(
        capability_after_exposure(
            state[i][skill], effort[i][skill],
            rate=eta_to_lambda(profile.eta[i][skill]),
        )
        for skill in range(k)
    ) for i in range(n))
