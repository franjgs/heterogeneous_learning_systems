"""N×K adaptation of Nembhard direct experience, separate from competence.

This is an HLS operational convention around the standalone scalar curve;
it is not a reproduction of the complete Nembhard & Bentefouet model.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .hls_lab_nk_geometry import ProductiveAllocationNK
from .mechanisms.nembhard_direct import (
    DirectExperienceParameters,
    advance_direct_experience,
    direct_productivity,
)

ExperienceMatrixNK = tuple[tuple[float, ...], ...]


def _matrix(values, name: str) -> ExperienceMatrixNK:
    try:
        result = tuple(tuple(float(value) for value in row) for row in values)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a numeric N×K matrix") from exc
    if not result or not result[0] or any(len(row) != len(result[0]) for row in result):
        raise ValueError(f"{name} must be a non-empty rectangular N×K matrix")
    if any(not isfinite(value) or value < 0 for row in result for value in row):
        raise ValueError(f"{name} values must be finite and non-negative")
    return result


@dataclass(frozen=True)
class NembhardDirectProfileNK:
    """Cell-specific ``k``, ``p`` and ``r`` matrices for agents × skills."""

    asymptotic_productivity: ExperienceMatrixNK
    prior_experience: ExperienceMatrixNK
    experience_scale: ExperienceMatrixNK

    def __post_init__(self) -> None:
        k = _matrix(self.asymptotic_productivity, "asymptotic_productivity")
        p = _matrix(self.prior_experience, "prior_experience")
        r = _matrix(self.experience_scale, "experience_scale")
        if len(k) != len(p) or len(k) != len(r) or any(
            len(k[i]) != len(p[i]) or len(k[i]) != len(r[i]) for i in range(len(k))
        ):
            raise ValueError("Nembhard k, p and r matrices must have identical N×K dimensions")
        for i in range(len(k)):
            for skill in range(len(k[0])):
                DirectExperienceParameters(k[i][skill], p[i][skill], r[i][skill])
        object.__setattr__(self, "asymptotic_productivity", k)
        object.__setattr__(self, "prior_experience", p)
        object.__setattr__(self, "experience_scale", r)

    @property
    def n_agents(self) -> int:
        return len(self.asymptotic_productivity)

    @property
    def n_skills(self) -> int:
        return len(self.asymptotic_productivity[0])

    def validate_dimensions(self, n_agents: int, n_skills: int) -> None:
        if (self.n_agents, self.n_skills) != (n_agents, n_skills):
            raise ValueError(
                f"Nembhard profile is {self.n_agents}×{self.n_skills}; "
                f"organization geometry is {n_agents}×{n_skills}"
            )


@dataclass(frozen=True)
class NembhardDirectStateNK:
    """Independent cumulative direct-experience state ``D[N,K]``."""

    experience: ExperienceMatrixNK

    def __post_init__(self) -> None:
        object.__setattr__(self, "experience", _matrix(self.experience, "experience"))

    @property
    def n_agents(self) -> int:
        return len(self.experience)

    @property
    def n_skills(self) -> int:
        return len(self.experience[0])

    @classmethod
    def zeros(cls, n_agents: int, n_skills: int) -> "NembhardDirectStateNK":
        if (not isinstance(n_agents, int) or isinstance(n_agents, bool) or n_agents < 1
                or not isinstance(n_skills, int) or isinstance(n_skills, bool) or n_skills < 1):
            raise ValueError("n_agents and n_skills must be positive integers")
        return cls(tuple((0.0,) * n_skills for _ in range(n_agents)))

    def validate_dimensions(self, n_agents: int, n_skills: int) -> None:
        if (self.n_agents, self.n_skills) != (n_agents, n_skills):
            raise ValueError(
                f"Nembhard experience is {self.n_agents}×{self.n_skills}; "
                f"organization geometry is {n_agents}×{n_skills}"
            )


@dataclass(frozen=True)
class NembhardOutputUnitContract:
    """Caller attestation for the HLS output bridge; no conversion is applied.

    The caller declares that effort intensity times duration has the declared
    ``exposure_unit``, that ``k`` is measured in ``output_unit / exposure_unit``,
    and that output and task requirements share one unit. This is an explicit
    calibration contract, not a dimensional unit engine.
    """

    effort_intensity_unit: str
    duration_unit: str
    exposure_unit: str
    output_unit: str
    requirement_unit: str

    def __post_init__(self) -> None:
        for name in ("effort_intensity_unit", "duration_unit", "exposure_unit",
                     "output_unit", "requirement_unit"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty declared unit label")
        if self.output_unit != self.requirement_unit:
            raise ValueError("Nembhard output unit must match the task requirement unit")


@dataclass(frozen=True)
class NembhardDirectExecutionNK:
    """Explicit-allocation episode specification for Nembhard Direct v0.1."""

    profile: NembhardDirectProfileNK
    allocations: tuple[ProductiveAllocationNK, ...]
    unit_contract: NembhardOutputUnitContract
    initial_state: NembhardDirectStateNK | None = None
    period_duration: float = 1.0

    def __post_init__(self) -> None:
        if isinstance(self.period_duration, bool):
            raise ValueError("period_duration must be finite and strictly positive")
        try:
            duration = float(self.period_duration)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("period_duration must be finite and strictly positive") from exc
        if not isfinite(duration) or duration <= 0:
            raise ValueError("period_duration must be finite and strictly positive")
        allocations = tuple(tuple(tuple(float(x) for x in row) for row in allocation)
                            for allocation in self.allocations)
        if not allocations:
            raise ValueError("Nembhard execution requires a non-empty explicit allocation sequence")
        if not isinstance(self.profile, NembhardDirectProfileNK):
            raise TypeError("profile must be NembhardDirectProfileNK")
        if self.initial_state is not None and not isinstance(self.initial_state, NembhardDirectStateNK):
            raise TypeError("initial_state must be NembhardDirectStateNK or None")
        if not isinstance(self.unit_contract, NembhardOutputUnitContract):
            raise TypeError("unit_contract must be NembhardOutputUnitContract")
        object.__setattr__(self, "allocations", allocations)
        object.__setattr__(self, "period_duration", duration)


def nembhard_productive_outputs_nk(
    allocation: ProductiveAllocationNK,
    state: NembhardDirectStateNK,
    profile: NembhardDirectProfileNK,
    *,
    period_duration: float = 1.0,
) -> tuple[tuple[float, ...], tuple[tuple[float, ...], ...]]:
    """Return total K-output and per-agent/skill contributions from ``D_t``."""
    if isinstance(period_duration, bool):
        raise ValueError("period_duration must be finite and strictly positive")
    try:
        duration = float(period_duration)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("period_duration must be finite and strictly positive") from exc
    if not isfinite(duration) or duration <= 0:
        raise ValueError("period_duration must be finite and strictly positive")
    n, k = state.n_agents, state.n_skills
    profile.validate_dimensions(n, k)
    try:
        action = tuple(tuple(float(value) for value in row) for row in allocation)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("allocation must be a numeric N×K matrix") from exc
    if len(action) != n or any(len(row) != k for row in action):
        raise ValueError(f"allocation must have shape {n}×{k}")
    if any(not isfinite(value) or value < 0 for row in action for value in row):
        raise ValueError("allocation values must be finite and non-negative")

    productivities = tuple(tuple(direct_productivity(
        state.experience[i][skill],
        DirectExperienceParameters(
            profile.asymptotic_productivity[i][skill],
            profile.prior_experience[i][skill],
            profile.experience_scale[i][skill],
        ),
    ) for skill in range(k)) for i in range(n))
    contributions = tuple(tuple(
        action[i][skill] * productivities[i][skill] * duration for skill in range(k)
    ) for i in range(n))
    outputs = tuple(sum(contributions[i][skill] for i in range(n)) for skill in range(k))
    if any(not isfinite(value) for row in contributions for value in row) or any(
        not isfinite(value) for value in outputs
    ):
        raise ValueError("Nembhard output overflowed; check parameter calibration and scale")
    return outputs, productivities


def advance_nembhard_experience_nk(
    state: NembhardDirectStateNK,
    allocation: ProductiveAllocationNK,
    *,
    period_duration: float = 1.0,
) -> NembhardDirectStateNK:
    """Apply the HLS convention ``D_next = D_current + e * delta_t`` cellwise."""
    if isinstance(period_duration, bool):
        raise ValueError("period_duration must be finite and strictly positive")
    try:
        duration = float(period_duration)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("period_duration must be finite and strictly positive") from exc
    if not isfinite(duration) or duration <= 0:
        raise ValueError("period_duration must be finite and strictly positive")
    try:
        action = tuple(tuple(float(value) for value in row) for row in allocation)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("allocation must be a numeric N×K matrix") from exc
    if len(action) != state.n_agents or any(len(row) != state.n_skills for row in action):
        raise ValueError("allocation dimensions do not match experience state")
    next_state = tuple(tuple(advance_direct_experience(
        state.experience[i][skill], action[i][skill] * duration,
    ) for skill in range(state.n_skills)) for i in range(state.n_agents))
    return NembhardDirectStateNK(next_state)
