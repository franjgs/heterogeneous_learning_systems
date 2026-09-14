"""Pure analytical checks for the gap-dependent M0.1 extension.

This module implements only the equations documented in
``docs/models/model_M0_1_gap_dependent_learning.md``.  It is separate from
``hls.m0`` so that M0 remains an implementation of the fixed-gain model.
Derivative helpers apply only at strictly canonical, strictly switchable
points, where the positive-part operation in the M0 value is differentiable.
"""

from __future__ import annotations

from .m0 import discount_factor_sum


def _require_probability(name: str, value: float) -> None:
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must lie in [0, 1]; received {value}.")


def _require_nonnegative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative; received {value}.")


def linear_gain(delta: float, a: float, b: float) -> float:
    """Return the M0.1 linear response ``g(delta) = a + b delta``."""
    return a + b * delta


def proportional_gain(delta: float, rho: float) -> float:
    """Return proportional gap recovery ``g(delta) = rho delta``."""
    if not 0 <= rho <= 1:
        raise ValueError(f"rho must lie in [0, 1]; received {rho}.")
    return rho * delta


def linear_learnability(delta: float, ell0: float, s: float) -> float:
    """Return the unclipped verification family ``ell(delta) = ell0 + s delta``."""
    return ell0 + s * delta


def operational_surplus(delta: float, c: float, gain: float) -> float:
    """Return ``h(delta) = g(delta) + c - delta``."""
    _require_nonnegative("c", c)
    return gain + c - delta


def validate_strictly_switchable(delta: float, c: float, gain: float) -> None:
    """Require canonical M0 routing and a differentiable switchable point.

    ``delta > c`` ensures the expensive model routes before intervention.
    ``h(delta) > 0`` ensures the positive-part operation is inactive after a
    successful intervention. Equality is a boundary/kink and is excluded.
    """
    _require_nonnegative("c", c)
    if delta <= c:
        raise ValueError("Canonical M0.1 requires delta > c.")
    if operational_surplus(delta, c, gain) <= 0:
        raise ValueError("Derivative verification requires h(delta) > 0.")


def intervention_value_m01(
    delta: float,
    p: float,
    ell: float,
    gain: float,
    K: float,
    c: float,
    H: int,
    gamma: float,
) -> float:
    """Return canonical M0.1 value ``-K + A_H p ell [h(delta)]_+``."""
    _require_probability("p", p)
    _require_probability("ell", ell)
    _require_nonnegative("gain", gain)
    _require_nonnegative("K", K)
    _require_nonnegative("c", c)
    if delta <= c:
        raise ValueError("Canonical M0.1 requires delta > c.")
    return -K + discount_factor_sum(H, gamma) * p * ell * max(
        operational_surplus(delta, c, gain), 0.0
    )


def dV_ddelta_constant_ell(
    p: float,
    ell: float,
    gain_derivative: float,
    H: int,
    gamma: float,
) -> float:
    """Return ``A_H p ell [g'(delta)-1]`` at a validated switchable point.

    The caller supplies the point-specific gain derivative and is responsible
    for using this expression only where ``delta > c`` and ``h(delta) > 0``.
    """
    _require_probability("p", p)
    _require_probability("ell", ell)
    return discount_factor_sum(H, gamma) * p * ell * (gain_derivative - 1.0)


def dV_ddelta_variable_ell(
    delta: float,
    p: float,
    ell: float,
    ell_derivative: float,
    gain: float,
    gain_derivative: float,
    c: float,
    H: int,
    gamma: float,
) -> float:
    """Return ``A_H p [ell' h + ell (g'-1)]`` at a switchable point."""
    _require_probability("p", p)
    _require_probability("ell", ell)
    validate_strictly_switchable(delta, c, gain)
    h = operational_surplus(delta, c, gain)
    return discount_factor_sum(H, gamma) * p * (
        ell_derivative * h + ell * (gain_derivative - 1.0)
    )


def dV_ddelta_variable_cost(
    delta: float,
    p: float,
    ell: float,
    ell_derivative: float,
    gain: float,
    gain_derivative: float,
    K_derivative: float,
    c: float,
    H: int,
    gamma: float,
) -> float:
    """Return ``-K' + A_H p [ell' h + ell (g'-1)]`` at a switchable point."""
    return -K_derivative + dV_ddelta_variable_ell(
        delta=delta,
        p=p,
        ell=ell,
        ell_derivative=ell_derivative,
        gain=gain,
        gain_derivative=gain_derivative,
        c=c,
        H=H,
        gamma=gamma,
    )
