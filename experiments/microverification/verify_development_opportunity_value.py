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
    gamma_comp_closed,
    gamma_policy_selection,
    gamma_sub_closed,
    individual_selection,
    mixed_gamma,
    portfolio_selection,
    value_comp,
    value_sub,
)


GRID = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
TOLERANCE = 1e-12
POLICY_GRID = tuple(value / 2 for value in range(-12, 13))
DECISION_GRID = tuple(value / 2 for value in range(-12, 13))


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
        "tolerance": TOLERANCE,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
