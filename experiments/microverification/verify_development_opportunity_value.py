"""Grid verification for development-opportunity value identities.

This is a numerical audit of exact, documented DERIVED-IN-MODEL identities.
It writes no result artifacts and is not empirical HLS evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hls.development_opportunity_value import (
    cross_difference,
    fast_deep_h1,
    fast_deep_h12,
    fast_deep_h2,
    gamma_comp_closed,
    gamma_policy_selection,
    gamma_sub_closed,
    individual_selection,
    individual_opportunity_values,
    joint_opportunity_value,
    mixed_gamma,
    portfolio_selection,
    smooth_pairwise_lower_bound,
    symmetric_fast_deep_joint_benefit,
    value_comp,
    value_sub,
    xi_cost,
    xi_value,
)


GRID = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
TOLERANCE = 1e-12
POLICY_GRID = tuple(value / 2 for value in range(-12, 13))
DECISION_GRID = tuple(value / 2 for value in range(-12, 13))
FAST_DEEP_STATE_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
FAST_DEEP_KAPPA_GRID = (0.0, 0.0625, 0.125, 0.1875, 0.25)


def _strict_decision_region(g1: float, g2: float, c: float) -> str | None:
    """Classify the four strict decision-change regions."""
    if c > 0:
        if g1 > 0 and -c < g2 < 0:
            return "A"
        if g2 > 0 and -c < g1 < 0:
            return "B"
        if g1 < 0 and g2 < 0 and g1 + g2 + c > 0:
            return "C"
    if c < 0 and g1 > 0 and g2 > 0 and c < -min(g1, g2):
        return "D"
    return None


def _portfolio_value(option: frozenset[int], g1: float, g2: float, c: float) -> float:
    """Evaluate one development set with the true portfolio interaction."""
    return (
        (g1 if 1 in option else 0.0)
        + (g2 if 2 in option else 0.0)
        + (c if option == frozenset({1, 2}) else 0.0)
    )


def _region_loss(region: str, g1: float, g2: float, c: float) -> float:
    """Return the documented exact loss formula for a strict region."""
    if region == "A":
        return g2 + c
    if region == "B":
        return g1 + c
    if region == "C":
        return g1 + g2 + c
    if region == "D":
        return -min(g1, g2) - c
    raise ValueError(f"unknown region: {region}")


def _audit_integrated_fast_deep() -> dict[str, int]:
    """Verify the symmetric Omega + Gamma identity within the Fast/Deep model."""
    cases = 0
    strictly_joint_beneficial = 0
    for h in FAST_DEEP_STATE_GRID:
        for s in FAST_DEEP_STATE_GRID:
            if s <= h:
                continue
            for delta in FAST_DEEP_STATE_GRID:
                if s + delta > 1.0:
                    continue
                for beta in FAST_DEEP_STATE_GRID:
                    for kappa1 in FAST_DEEP_KAPPA_GRID:
                        for kappa2 in FAST_DEEP_KAPPA_GRID:
                            h1 = fast_deep_h1(s, s, delta, h, beta, kappa1)
                            h2 = fast_deep_h2(s, s, delta, h, beta, kappa2)
                            h12 = fast_deep_h12(
                                s, s, delta, delta, h, beta, kappa1, kappa2
                            )
                            gamma = cross_difference(
                                value_comp, s, s, delta, delta, h
                            )
                            assert abs(h1 - (-(s - h) - kappa1)) <= TOLERANCE
                            assert abs(h2 - (-(s - h) - kappa2)) <= TOLERANCE
                            assert abs(gamma - delta) <= TOLERANCE
                            assert abs(h12 - (h1 + h2 + beta * gamma)) <= TOLERANCE
                            condition = symmetric_fast_deep_joint_benefit(
                                s, h, delta, beta, kappa1, kappa2
                            )
                            assert (h12 > TOLERANCE) == condition
                            if (
                                h1 < -TOLERANCE
                                and h2 < -TOLERANCE
                                and h12 > TOLERANCE
                            ):
                                strictly_joint_beneficial += 1
                            cases += 1

    # Explicit non-strict boundaries and the supplied numerical instance.
    assert abs(fast_deep_h1(0.8, 0.8, 0.2, 0.8, 1.0, 0.0)) <= TOLERANCE
    assert (
        abs(fast_deep_h12(0.8, 0.8, 0.2, 0.2, 0.8, 1.0, 0.0, 0.0) - 0.2)
        <= TOLERANCE
    )
    assert cross_difference(value_comp, 0.75, 0.75, 0.0, 0.0, 0.5) == 0.0
    assert fast_deep_h12(0.75, 0.75, 0.25, 0.25, 0.5, 0.0, 0.0, 0.0) < 0.0
    assert not symmetric_fast_deep_joint_benefit(0.75, 0.5, 0.5, 1.0, 0.0, 0.0)

    example_h1 = fast_deep_h1(0.85, 0.85, 0.15, 0.8, 1.0, 0.0)
    example_h2 = fast_deep_h2(0.85, 0.85, 0.15, 0.8, 1.0, 0.0)
    example_h12 = fast_deep_h12(0.85, 0.85, 0.15, 0.15, 0.8, 1.0, 0.0, 0.0)
    example_gamma = cross_difference(value_comp, 0.85, 0.85, 0.15, 0.15, 0.8)
    assert abs(example_h1 + 0.05) <= TOLERANCE
    assert abs(example_h2 + 0.05) <= TOLERANCE
    assert abs(example_h12 - 0.05) <= TOLERANCE
    assert abs(example_gamma - 0.15) <= TOLERANCE

    return {
        "integrated_fast_deep_cases": cases,
        "integrated_fast_deep_strictly_joint_beneficial_cases": strictly_joint_beneficial,
    }


def _quadratic_value(mu: float):
    """Return a smooth value with every off-diagonal cross partial equal to mu."""
    def value(state: tuple[float, ...]) -> float:
        return sum(state) + mu * sum(
            state[i] * state[j]
            for i in range(len(state))
            for j in range(i + 1, len(state))
        )

    return value


def _third_difference(
    value, state: tuple[float, float, float], increments: tuple[float, float, float]
) -> float:
    """Return the third finite difference for three independent increments."""
    def at(indices: tuple[int, ...]) -> float:
        return value(
            tuple(
                component + (increments[i] if i in indices else 0.0)
                for i, component in enumerate(state)
            )
        )

    return (
        at((0, 1, 2))
        - at((0, 1))
        - at((0, 2))
        - at((1, 2))
        + at((0,))
        + at((1,))
        + at((2,))
        - at(())
    )


def _audit_general_joint_opportunity_structure() -> dict[str, int]:
    """Verify general Xi identities, smooth bounds, and higher-order caution."""
    smooth_cases = 0
    modular_cases = 0
    smooth_by_n = {n: 0 for n in (3, 4, 5)}
    for n in (3, 4, 5):
        state = tuple(0.125 for _ in range(n))
        individual_costs = tuple(0.125 + 0.0625 * i for i in range(n))
        for mu in (0.0, 0.5, 1.0):
            value = _quadratic_value(mu)
            lower_cross_partials = tuple(
                tuple(0.0 if i == j else mu for j in range(n)) for i in range(n)
            )
            for delta in (0.0, 0.25, 0.5):
                increments = tuple(delta for _ in range(n))
                for beta in (0.0, 0.5, 1.0):
                    total_cost = sum(individual_costs) + 0.0625
                    h_total = joint_opportunity_value(
                        value, state, increments, total_cost, beta
                    )
                    h_individual = individual_opportunity_values(
                        value, state, increments, individual_costs, beta
                    )
                    interaction_value = xi_value(value, state, increments)
                    interaction_cost = xi_cost(total_cost, individual_costs)
                    assert abs(
                        h_total
                        - (sum(h_individual) + beta * interaction_value - interaction_cost)
                    ) <= TOLERANCE
                    lower_bound = smooth_pairwise_lower_bound(
                        lower_cross_partials, increments
                    )
                    assert interaction_value + TOLERANCE >= lower_bound
                    smooth_cases += 1
                    smooth_by_n[n] += 1

                    modular_value = lambda point: sum(point)
                    additive_total_cost = sum(individual_costs)
                    modular_total = joint_opportunity_value(
                        modular_value, state, increments, additive_total_cost, beta
                    )
                    modular_individual = individual_opportunity_values(
                        modular_value, state, increments, individual_costs, beta
                    )
                    assert abs(xi_value(modular_value, state, increments)) <= TOLERANCE
                    assert abs(modular_total - sum(modular_individual)) <= TOLERANCE
                    modular_cases += 1

    # A cubic term makes base-state pair interactions insufficient for n=3.
    def cubic_value(state: tuple[float, ...]) -> float:
        return _quadratic_value(1.0)(state) + 2.0 * state[0] * state[1] * state[2]

    base = (0.0, 0.0, 0.0)
    cubic_increments = (0.5, 0.5, 0.5)
    xi_cubic = xi_value(cubic_value, base, cubic_increments)
    pair_sum = sum(
        xi_value(
            cubic_value,
            base,
            tuple(cubic_increments[k] if k in pair else 0.0 for k in range(3)),
        )
        for pair in ((0, 1), (0, 2), (1, 2))
    )
    third = _third_difference(cubic_value, base, cubic_increments)
    cubic_bound = smooth_pairwise_lower_bound(
        ((0.0, 1.0, 1.0), (1.0, 0.0, 1.0), (1.0, 1.0, 0.0)),
        cubic_increments,
    )
    assert abs(xi_cubic - (pair_sum + third)) <= TOLERANCE
    assert abs(third - 0.25) <= TOLERANCE
    assert abs(pair_sum - 0.75) <= TOLERANCE
    assert abs(xi_cubic - 1.0) <= TOLERANCE
    assert xi_cubic + TOLERANCE >= cubic_bound

    # Equality in the sufficient condition remains non-strict.
    equality_value = _quadratic_value(1.0)
    equality_state = (0.0, 0.0, 0.0)
    equality_increments = (0.5, 0.5, 0.5)
    equality_costs = (0.75, 0.75, 0.75)
    equality_h = joint_opportunity_value(
        equality_value, equality_state, equality_increments, sum(equality_costs), 1.0
    )
    equality_h_individual = individual_opportunity_values(
        equality_value, equality_state, equality_increments, equality_costs, 1.0
    )
    equality_bound = smooth_pairwise_lower_bound(
        ((0.0, 1.0, 1.0), (1.0, 0.0, 1.0), (1.0, 1.0, 0.0)),
        equality_increments,
    )
    assert abs(equality_h) <= TOLERANCE
    assert abs(equality_bound + sum(equality_h_individual)) <= TOLERANCE

    # A strict uniform bound can exceed the accumulated individual deficits.
    rescue_costs = (0.7, 0.7, 0.7)
    rescue_h = joint_opportunity_value(
        equality_value, equality_state, equality_increments, sum(rescue_costs), 1.0
    )
    rescue_h_individual = individual_opportunity_values(
        equality_value, equality_state, equality_increments, rescue_costs, 1.0
    )
    assert all(value < 0.0 for value in rescue_h_individual)
    assert equality_bound > -sum(rescue_h_individual)
    assert (3 - 1) * 1.0 * 1.0 * 0.5**2 > 2.0 * 0.2
    assert rescue_h > 0.0

    # The n=2 general identity reduces exactly to Proposition 7.
    fast_deep_state = (0.85, 0.85)
    fast_deep_increments = (0.15, 0.15)
    fast_deep_costs = (0.05, 0.05)
    fast_deep_value = lambda point: value_comp(point[0], point[1], 0.8)
    assert abs(
        joint_opportunity_value(
            fast_deep_value, fast_deep_state, fast_deep_increments, sum(fast_deep_costs), 1.0
        )
        - fast_deep_h12(0.85, 0.85, 0.15, 0.15, 0.8, 1.0, 0.0, 0.0)
    ) <= TOLERANCE
    assert abs(xi_value(fast_deep_value, fast_deep_state, fast_deep_increments) - 0.15) <= TOLERANCE

    return {
        "general_smooth_bound_cases": smooth_cases,
        **{f"general_smooth_n{n}_cases": count for n, count in smooth_by_n.items()},
        "general_modular_cases": modular_cases,
        "general_third_order_cases": 1,
        "general_uniform_rescue_cases": 1,
        "general_fast_deep_reductions": 1,
    }


def audit() -> dict[str, float | int]:
    """Exhaustively check signs and closed forms over the declared small grid."""
    checked = 0
    strict_both = 0
    for h in GRID:
        for s1 in GRID:
            for s2 in GRID:
                for delta1 in GRID:
                    for delta2 in GRID:
                        gamma_sub = cross_difference(value_sub, s1, s2, delta1, delta2, h)
                        gamma_comp = cross_difference(value_comp, s1, s2, delta1, delta2, h)
                        assert gamma_sub <= TOLERANCE
                        assert gamma_comp >= -TOLERANCE
                        assert abs(gamma_sub - gamma_sub_closed(s1, s2, delta1, delta2, h)) <= TOLERANCE
                        assert abs(gamma_comp - gamma_comp_closed(s1, s2, delta1, delta2, h)) <= TOLERANCE
                        checked += 1
                        if gamma_sub < -TOLERANCE and gamma_comp > TOLERANCE:
                            p_star = gamma_comp / (gamma_comp + abs(gamma_sub))
                            assert mixed_gamma(gamma_sub, gamma_comp, p_star - 0.01) > TOLERANCE
                            assert abs(mixed_gamma(gamma_sub, gamma_comp, p_star)) <= TOLERANCE
                            assert mixed_gamma(gamma_sub, gamma_comp, p_star + 0.01) < -TOLERANCE
                            strict_both += 1

    policy_cases = 0
    same_policy_cases = 0
    nonzero_policy_interactions = 0
    for z in POLICY_GRID:
        for x in POLICY_GRID:
            for y in POLICY_GRID:
                gamma = gamma_policy_selection(z, x, y)
                if x * y > 0:
                    assert gamma >= 0
                elif x * y < 0:
                    assert gamma <= 0
                else:
                    assert gamma == 0
                deltas = (z, z + x, z + y, z + x + y)
                if all(delta > 0 for delta in deltas) or all(delta < 0 for delta in deltas):
                    assert gamma == 0
                    same_policy_cases += 1
                if gamma != 0:
                    assert min(deltas) < 0 < max(deltas)
                    nonzero_policy_interactions += 1
                policy_cases += 1

    decision_cases = 0
    strict_decision_cases = 0
    tie_cases = 0
    region_counts = {region: 0 for region in "ABCD"}
    for g1 in DECISION_GRID:
        for g2 in DECISION_GRID:
            for c in DECISION_GRID:
                individual = individual_selection(g1, g2)
                portfolio = portfolio_selection(g1, g2, c)
                decision_cases += 1
                if len(individual) != 1 or len(portfolio) != 1:
                    tie_cases += 1
                    continue
                individual_option = next(iter(individual))
                portfolio_option = next(iter(portfolio))
                region = _strict_decision_region(g1, g2, c)
                differs = individual_option != portfolio_option
                assert differs == (region is not None)
                if region is not None:
                    actual_loss = _portfolio_value(portfolio_option, g1, g2, c) - _portfolio_value(
                        individual_option, g1, g2, c
                    )
                    assert actual_loss == _region_loss(region, g1, g2, c)
                    assert actual_loss > 0
                    strict_decision_cases += 1
                    region_counts[region] += 1

    # Explicit boundary and tied-optimum checks requested by the analytical audit.
    assert gamma_policy_selection(1, 0, -2) == 0
    assert gamma_policy_selection(-1, 2, 0) == 0
    assert gamma_policy_selection(0, 2, 3) == 0
    assert gamma_policy_selection(-1, 1, 2) == 1  # z+x=0
    assert gamma_policy_selection(-1, 2, 1) == 1  # z+y=0
    assert gamma_policy_selection(-3, 1, 2) == 0  # z+x+y=0
    assert len(individual_selection(0, 2)) == 2
    assert len(individual_selection(2, 0)) == 2
    assert individual_selection(2, 2) == frozenset({frozenset({1, 2})})
    assert portfolio_selection(2, 2, -3) == frozenset(
        {frozenset({1}), frozenset({2})}
    )
    assert portfolio_selection(1, 2, -1) == frozenset(
        {frozenset({2}), frozenset({1, 2})}
    )
    assert individual_selection(1, -1) == portfolio_selection(1, -1, 0)

    integrated_fast_deep = _audit_integrated_fast_deep()
    general_joint_structure = _audit_general_joint_opportunity_structure()

    return {
        "grid_cases": checked,
        "mixed_sign_reversal_cases": strict_both,
        "policy_selection_cases": policy_cases,
        "strict_same_policy_cases": same_policy_cases,
        "nonzero_policy_interactions": nonzero_policy_interactions,
        "development_decision_cases": decision_cases,
        "strict_decision_changes": strict_decision_cases,
        "decision_tie_cases": tie_cases,
        **{f"region_{region}_cases": count for region, count in region_counts.items()},
        **integrated_fast_deep,
        **general_joint_structure,
        "tolerance": TOLERANCE,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
