"""Nembhard-inspired direct-experience productivity mechanism.

This module implements only the scalar direct-experience curve from
Nembhard & Bentefouet (2015), Eq. (1), printed p. 176. It is intentionally
separate from HLS normalized competence, MIS-v2, production, and the N×K
episode runner.

The implemented operational domain is ``k >= 0``, ``p >= 0``, ``r > 0`` and
``D >= 0``. This is the positive-scale monotone/saturating domain used for
this mechanism component; it is narrower than the source equation's printed
condition ``p + r > 0``. The symbols ``D``, ``p`` and ``r`` must share one
declared exposure unit. The productivity unit is the unit of ``k`` and is
application-defined; this module performs no unit conversion.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


def _finite_float(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite real number")
    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite real number") from exc
    if not isfinite(converted):
        raise ValueError(f"{name} must be a finite real number")
    return converted


@dataclass(frozen=True)
class DirectExperienceParameters:
    """Parameters for ``P(D) = k * (D + p) / (D + p + r)``.

    ``asymptotic_productivity`` is ``k`` in productivity units.
    ``prior_experience`` is ``p`` and ``experience_scale`` is ``r``; both
    use the same exposure unit as the input ``D``. ``r`` is strictly
    positive in this implementation.
    """

    asymptotic_productivity: float
    prior_experience: float
    experience_scale: float

    def __post_init__(self) -> None:
        k = _finite_float(self.asymptotic_productivity, "asymptotic_productivity")
        p = _finite_float(self.prior_experience, "prior_experience")
        r = _finite_float(self.experience_scale, "experience_scale")
        if k < 0.0:
            raise ValueError("asymptotic_productivity must be non-negative")
        if p < 0.0:
            raise ValueError("prior_experience must be non-negative")
        if r <= 0.0:
            raise ValueError("experience_scale must be strictly positive")
        object.__setattr__(self, "asymptotic_productivity", k)
        object.__setattr__(self, "prior_experience", p)
        object.__setattr__(self, "experience_scale", r)


@dataclass(frozen=True)
class DirectExperienceEvaluation:
    """Productivity immediately before and after one exposure increment."""

    experience_before: float
    experience_after: float
    productivity_before: float
    productivity_after: float


def _validate_experience(experience: float, name: str = "experience") -> float:
    value = _finite_float(experience, name)
    if value < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return value


def direct_productivity(
    experience: float,
    parameters: DirectExperienceParameters,
) -> float:
    """Evaluate the direct-experience productivity curve at cumulative ``D``.

    No competence update or state mutation occurs. The scaled fallback keeps
    the ratio finite for very large, but finite, exposure inputs.
    """
    if not isinstance(parameters, DirectExperienceParameters):
        raise TypeError("parameters must be DirectExperienceParameters")
    d = _validate_experience(experience)
    k = parameters.asymptotic_productivity
    p = parameters.prior_experience
    r = parameters.experience_scale

    effective_experience = d + p
    denominator = effective_experience + r
    if isfinite(effective_experience) and isfinite(denominator):
        ratio = effective_experience / denominator
    else:
        scale = max(d, p, r)
        numerator_scaled = d / scale + p / scale
        ratio = numerator_scaled / (numerator_scaled + r / scale)
    return k * ratio


def direct_productivity_many(
    experiences: Iterable[float],
    parameters: DirectExperienceParameters,
) -> tuple[float, ...]:
    """Evaluate a sequence of exposures without adding a numerical dependency."""
    return tuple(direct_productivity(value, parameters) for value in experiences)


def advance_direct_experience(current: float, delta_D: float) -> float:
    """Return ``D_next = D_current + delta_D`` in the caller's exposure unit.

    ``delta_D`` is direct experience, not HLS productive effort; converting
    between those quantities requires an explicit future integration contract.
    """
    current_value = _validate_experience(current, "current experience")
    increment = _validate_experience(delta_D, "delta_D")
    next_value = current_value + increment
    if not isfinite(next_value):
        raise ValueError("updated experience must remain finite")
    return next_value


def evaluate_direct_exposure(
    current: float,
    delta_D: float,
    parameters: DirectExperienceParameters,
) -> DirectExperienceEvaluation:
    """Report productivity before and after one specified exposure increment."""
    next_experience = advance_direct_experience(current, delta_D)
    return DirectExperienceEvaluation(
        experience_before=_validate_experience(current, "current experience"),
        experience_after=next_experience,
        productivity_before=direct_productivity(current, parameters),
        productivity_after=direct_productivity(next_experience, parameters),
    )
