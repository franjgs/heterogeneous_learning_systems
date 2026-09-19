"""Exact finite-difference identities for documented opportunity models.

These pure functions implement only DERIVED-IN-MODEL formulas in the
operational-development opportunity-value note.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence


DevelopmentSet = frozenset[int]
Selection = frozenset[DevelopmentSet]
CompetenceVector = tuple[float, ...]
ContinuationValue = Callable[[CompetenceVector], float]
DEVELOPMENT_SETS: tuple[DevelopmentSet, ...] = (
    frozenset(),
    frozenset({1}),
    frozenset({2}),
    frozenset({1, 2}),
)


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


def gamma_policy_selection(z: float, x: float, y: float) -> float:
    """Interaction created by selecting the better of two additive policies."""
    return positive(z + x + y) - positive(z + x) - positive(z + y) + positive(z)


def _maximizers(values: dict[DevelopmentSet, float]) -> Selection:
    """Return every maximizing development set, preserving exact ties."""
    best = max(values.values())
    return frozenset(option for option, value in values.items() if value == best)


def individual_selection(g1: float, g2: float) -> Selection:
    """Select interventions from their individual net values, including ties."""
    return _maximizers(
        {
            DEVELOPMENT_SETS[0]: 0.0,
            DEVELOPMENT_SETS[1]: g1,
            DEVELOPMENT_SETS[2]: g2,
            DEVELOPMENT_SETS[3]: g1 + g2,
        }
    )


def portfolio_selection(g1: float, g2: float, c: float) -> Selection:
    """Select interventions using their joint portfolio value, including ties."""
    return _maximizers(
        {
            DEVELOPMENT_SETS[0]: 0.0,
            DEVELOPMENT_SETS[1]: g1,
            DEVELOPMENT_SETS[2]: g2,
            DEVELOPMENT_SETS[3]: g1 + g2 + c,
        }
    )


def fast_deep_h1(
    s1: float,
    s2: float,
    delta1: float,
    h: float,
    beta: float,
    kappa1: float,
) -> float:
    """Full value of routing task 1 to Deep and using its opportunity."""
    return (
        -(s1 - h)
        + beta * (value_comp(s1 + delta1, s2, h) - value_comp(s1, s2, h))
        - kappa1
    )


def fast_deep_h2(
    s1: float,
    s2: float,
    delta2: float,
    h: float,
    beta: float,
    kappa2: float,
) -> float:
    """Full value of routing task 2 to Deep and using its opportunity."""
    return (
        -(s2 - h)
        + beta * (value_comp(s1, s2 + delta2, h) - value_comp(s1, s2, h))
        - kappa2
    )


def fast_deep_h12(
    s1: float,
    s2: float,
    delta1: float,
    delta2: float,
    h: float,
    beta: float,
    kappa1: float,
    kappa2: float,
) -> float:
    """Full value of routing both tasks to Deep and using both opportunities."""
    return (
        -(s1 - h)
        - (s2 - h)
        + beta * (value_comp(s1 + delta1, s2 + delta2, h) - value_comp(s1, s2, h))
        - kappa1
        - kappa2
    )


def symmetric_fast_deep_joint_benefit(
    s: float,
    h: float,
    delta: float,
    beta: float,
    kappa1: float,
    kappa2: float,
) -> bool:
    """Strict analytic condition for the documented symmetric Fast/Deep case."""
    return beta * delta > 2.0 * (s - h) + kappa1 + kappa2


def _developed_state(
    state: Sequence[float], increments: Sequence[float]
) -> CompetenceVector:
    """Return the state after the listed independent competence increments."""
    if len(state) != len(increments):
        raise ValueError("state and increments must have the same dimension")
    return tuple(
        component + increment for component, increment in zip(state, increments)
    )


def joint_opportunity_value(
    value: ContinuationValue,
    state: Sequence[float],
    increments: Sequence[float],
    total_cost: float,
    beta: float,
) -> float:
    """Return H(D) for a specified set of independent development increments."""
    initial_state = tuple(state)
    return -total_cost + beta * (
        value(_developed_state(initial_state, increments)) - value(initial_state)
    )


def individual_opportunity_values(
    value: ContinuationValue,
    state: Sequence[float],
    increments: Sequence[float],
    individual_costs: Sequence[float],
    beta: float,
) -> tuple[float, ...]:
    """Return H_i for each listed independent development opportunity."""
    if len(increments) != len(individual_costs):
        raise ValueError("increments and individual_costs must have the same dimension")
    return tuple(
        joint_opportunity_value(
            value,
            state,
            tuple(
                increment if i == j else 0.0
                for j, increment in enumerate(increments)
            ),
            cost,
            beta,
        )
        for i, cost in enumerate(individual_costs)
    )


def xi_value(
    value: ContinuationValue,
    state: Sequence[float],
    increments: Sequence[float],
) -> float:
    """Return Xi_V(D), the non-additivity of the continuation increment."""
    initial_state = tuple(state)
    total_increment = (
        value(_developed_state(initial_state, increments)) - value(initial_state)
    )
    individual_increments = sum(
        value(
            _developed_state(
                initial_state,
                tuple(
                    increment if i == j else 0.0
                    for j, increment in enumerate(increments)
                ),
            )
        )
        - value(initial_state)
        for i in range(len(increments))
    )
    return total_increment - individual_increments


def xi_cost(total_cost: float, individual_costs: Sequence[float]) -> float:
    """Return Xi_K(D), the non-additivity of present opportunity costs."""
    return total_cost - sum(individual_costs)


def smooth_pairwise_lower_bound(
    lower_cross_partials: Sequence[Sequence[float]], increments: Sequence[float]
) -> float:
    """Return sum_{i<j} mu_ij Delta_i Delta_j for supplied uniform bounds."""
    if len(lower_cross_partials) != len(increments):
        raise ValueError(
            "lower_cross_partials and increments must have the same dimension"
        )
    if any(len(row) != len(increments) for row in lower_cross_partials):
        raise ValueError("lower_cross_partials must be a square matrix")
    return sum(
        lower_cross_partials[i][j] * increments[i] * increments[j]
        for i in range(len(increments))
        for j in range(i + 1, len(increments))
    )
