"""Exact finite-difference identities for documented opportunity models.

These pure functions implement only DERIVED-IN-MODEL formulas in the
operational-development opportunity-value note.
"""

from __future__ import annotations

from collections.abc import Callable


def positive(value: float) -> float:
    """Return the positive part of a scalar."""
    return max(value, 0.0)


def value_sub(s1: float, s2: float, h: float) -> float:
    """Future value with one shared deep-model backup capacity."""
    return max(s1 + s2, h + s1, h + s2)


def value_comp(s1: float, s2: float, h: float) -> float:
    """Future value when fast-model work requires both competences."""
    return max(h, min(s1, s2))


def cross_difference(
    value: Callable[[float, float, float], float],
    s1: float,
    s2: float,
    delta1: float,
    delta2: float,
    h: float,
) -> float:
    """Return the finite interaction difference for two independent increments."""
    return (
        value(s1 + delta1, s2 + delta2, h)
        - value(s1 + delta1, s2, h)
        - value(s1, s2 + delta2, h)
        + value(s1, s2, h)
    )


def gamma_sub_closed(s1: float, s2: float, delta1: float, delta2: float, h: float) -> float:
    """Closed form for routing-induced substitution, using symmetry if needed."""
    if s2 < s1:
        return gamma_sub_closed(s2, s1, delta2, delta1, h)
    u = positive(h - s1)
    v = positive(h - s2)
    u_prime = positive(u - delta1)
    v_prime = positive(v - delta2)
    return -positive(v - max(u_prime, v_prime))


def gamma_comp_closed(s1: float, s2: float, delta1: float, delta2: float, h: float) -> float:
    """Closed form for routing-induced complementarity, using symmetry if needed."""
    if s2 < s1:
        return gamma_comp_closed(s2, s1, delta2, delta1, h)
    u = positive(s1 - h)
    v = positive(s2 - h)
    u_prime = positive(s1 + delta1 - h)
    v_prime = positive(s2 + delta2 - h)
    return positive(min(u_prime, v_prime) - v)


def mixed_gamma(gamma_sub: float, gamma_comp: float, p: float) -> float:
    """Return the workload-mixture interaction value."""
    return p * gamma_sub + (1.0 - p) * gamma_comp
