from __future__ import annotations

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


def test_substitution_and_complementarity_closed_forms_on_grid() -> None:
    grid = (0.0, 0.4, 0.8, 1.0)
    for h in grid:
        for s1 in grid:
            for s2 in grid:
                for delta1 in grid:
                    for delta2 in grid:
                        sub = cross_difference(value_sub, s1, s2, delta1, delta2, h)
                        comp = cross_difference(value_comp, s1, s2, delta1, delta2, h)
                        assert sub <= 1e-12
                        assert comp >= -1e-12
                        assert abs(sub - gamma_sub_closed(s1, s2, delta1, delta2, h)) <= 1e-12
                        assert abs(comp - gamma_comp_closed(s1, s2, delta1, delta2, h)) <= 1e-12


def test_mixed_workload_sign_reversal_and_fast_deep_example() -> None:
    sub = cross_difference(value_sub, 0.6, 0.6, 0.3, 0.3, 0.8)
    comp = cross_difference(value_comp, 0.6, 0.6, 0.3, 0.3, 0.8)
    assert sub < 0
    assert abs(comp - 0.1) <= 1e-12
    p_star = comp / (comp + abs(sub))
    assert mixed_gamma(sub, comp, p_star - 0.05) > 0
    assert abs(mixed_gamma(sub, comp, p_star)) <= 1e-12
    assert mixed_gamma(sub, comp, p_star + 0.05) < 0


def test_policy_selection_interaction_sign_and_same_policy() -> None:
    grid = tuple(range(-4, 5))
    for z in grid:
        for x in grid:
            for y in grid:
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


def test_individual_and_portfolio_decision_regions_and_ties() -> None:
    both = frozenset({frozenset({1, 2})})
    only_1 = frozenset({frozenset({1})})
    only_2 = frozenset({frozenset({2})})
    empty = frozenset({frozenset()})

    assert individual_selection(3, -1) == only_1
    assert portfolio_selection(3, -1, 2) == both  # Region A.
    assert individual_selection(-1, 3) == only_2
    assert portfolio_selection(-1, 3, 2) == both  # Region B.
    assert individual_selection(-1, -1) == empty
    assert portfolio_selection(-1, -1, 3) == both  # Region C.
    assert individual_selection(2, 3) == both
    assert portfolio_selection(2, 3, -3) == only_2  # Region D.

    assert len(individual_selection(0, 2)) == 2
    assert len(individual_selection(2, 0)) == 2
    assert portfolio_selection(2, 2, -3) == frozenset(
        {frozenset({1}), frozenset({2})}
    )
    assert portfolio_selection(1, 2, -1) == frozenset(
        {frozenset({2}), frozenset({1, 2})}
    )
