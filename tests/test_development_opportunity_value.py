from __future__ import annotations

from hls.development_opportunity_value import (
    cross_difference,
    gamma_comp_closed,
    gamma_sub_closed,
    mixed_gamma,
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
