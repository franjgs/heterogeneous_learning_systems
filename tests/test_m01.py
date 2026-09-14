import math

import pytest

from hls.m01 import (
    dV_ddelta_constant_ell,
    dV_ddelta_variable_cost,
    dV_ddelta_variable_ell,
    intervention_value_m01,
    linear_gain,
    linear_learnability,
    operational_surplus,
    proportional_gain,
    validate_strictly_switchable,
)


EPSILON = 1e-6


def central_difference(function, delta: float) -> float:
    return (function(delta + EPSILON) - function(delta - EPSILON)) / (2 * EPSILON)


def test_linear_gain_and_surplus_identity() -> None:
    delta, a, b, c = 0.3, 0.25, 0.5, 0.15
    gain = linear_gain(delta, a, b)
    assert gain == pytest.approx(a + b * delta)
    assert operational_surplus(delta, c, gain) == pytest.approx(a + c + (b - 1) * delta)


@pytest.mark.parametrize(
    "b, expected_sign",
    [(0.5, -1), (1.0, 0), (1.5, 1)],
)
def test_linear_gain_derivative_sign_and_finite_difference(b: float, expected_sign: int) -> None:
    delta, a, c = 0.30, 0.25, 0.15
    p, ell, K, H, gamma = 0.4, 0.7, 0.02, 3, 0.8
    gain = linear_gain(delta, a, b)
    validate_strictly_switchable(delta, c, gain)
    analytic = dV_ddelta_constant_ell(p, ell, b, H, gamma)
    numeric = central_difference(
        lambda point: intervention_value_m01(
            point, p, ell, linear_gain(point, a, b), K, c, H, gamma
        ),
        delta,
    )
    assert analytic == pytest.approx(numeric, abs=1e-9)
    assert math.copysign(1, analytic) == expected_sign if expected_sign else analytic == 0.0


def test_linear_below_one_switching_boundary() -> None:
    a, b, c = 0.25, 0.5, 0.15
    delta_switch = (a + c) / (1 - b)
    assert operational_surplus(delta_switch - 0.1, c, linear_gain(delta_switch - 0.1, a, b)) > 0
    assert operational_surplus(delta_switch + 0.1, c, linear_gain(delta_switch + 0.1, a, b)) < 0


def test_linear_b_equal_one_has_delta_independent_switchability() -> None:
    a, b, c = 0.05, 1.0, 0.15
    assert operational_surplus(0.2, c, linear_gain(0.2, a, b)) == pytest.approx(a + c)
    assert operational_surplus(0.8, c, linear_gain(0.8, a, b)) == pytest.approx(a + c)


@pytest.mark.parametrize("rho", [0.25, 0.5, 0.9])
def test_proportional_response_derivative_and_switching_boundary(rho: float) -> None:
    c = 0.15
    p, ell, K, H, gamma = 0.5, 0.8, 0.01, 4, 0.9
    delta_switch = c / (1 - rho)
    delta = c + (delta_switch - c) / 2
    assert delta < delta_switch
    gain = proportional_gain(delta, rho)
    assert operational_surplus(delta, c, gain) == pytest.approx(c - (1 - rho) * delta)
    analytic = dV_ddelta_constant_ell(p, ell, rho, H, gamma)
    numeric = central_difference(
        lambda point: intervention_value_m01(
            point, p, ell, proportional_gain(point, rho), K, c, H, gamma
        ),
        delta,
    )
    assert analytic == pytest.approx(numeric, abs=1e-9)
    assert analytic < 0


def test_zero_proportional_recovery_has_no_strictly_switchable_canonical_interval() -> None:
    c, rho = 0.15, 0.0
    delta_switch = c / (1 - rho)
    assert delta_switch == c
    with pytest.raises(ValueError, match=r"h\(delta\) > 0"):
        validate_strictly_switchable(0.20, c, proportional_gain(0.20, rho))


def test_perfect_proportional_recovery_has_zero_derivative_and_constant_value() -> None:
    c, rho, p, ell, K, H, gamma = 0.15, 1.0, 0.5, 0.8, 0.01, 4, 0.9
    values = [
        intervention_value_m01(delta, p, ell, proportional_gain(delta, rho), K, c, H, gamma)
        for delta in (0.2, 0.4, 0.8)
    ]
    assert dV_ddelta_constant_ell(p, ell, rho, H, gamma) == 0.0
    assert values[0] == pytest.approx(values[1])
    assert values[1] == pytest.approx(values[2])
    assert central_difference(
        lambda delta: intervention_value_m01(
            delta, p, ell, proportional_gain(delta, rho), K, c, H, gamma
        ),
        0.4,
    ) == pytest.approx(0.0, abs=1e-9)


def test_variable_learnability_derivative_matches_finite_difference() -> None:
    delta, a, b, c = 0.3, 0.3, 0.5, 0.15
    ell0, s, p, K, H, gamma = 0.3, 0.1, 0.4, 0.02, 3, 0.8
    gain = linear_gain(delta, a, b)
    ell = linear_learnability(delta, ell0, s)
    analytic = dV_ddelta_variable_ell(delta, p, ell, s, gain, b, c, H, gamma)
    numeric = central_difference(
        lambda point: intervention_value_m01(
            point,
            p,
            linear_learnability(point, ell0, s),
            linear_gain(point, a, b),
            K,
            c,
            H,
            gamma,
        ),
        delta,
    )
    assert analytic == pytest.approx(numeric, abs=1e-9)


def test_linear_learnability_sign_boundary() -> None:
    delta, a, b, c, ell0 = 0.3, 0.3, 0.5, 0.15, 0.3
    denominator = a + c + 2 * (b - 1) * delta
    s_star = -ell0 * (b - 1) / denominator
    signs = []
    for s in (s_star - 0.2, s_star, s_star + 0.2):
        ell = linear_learnability(delta, ell0, s)
        derivative = dV_ddelta_variable_ell(
            delta, 0.4, ell, s, linear_gain(delta, a, b), b, c, 3, 0.8
        )
        signs.append(derivative)
    assert signs[0] < 0
    assert signs[1] == pytest.approx(0.0, abs=1e-12)
    assert signs[2] > 0


def test_variable_cost_derivative_shifts_one_for_one_and_matches_finite_difference() -> None:
    delta, a, b, c = 0.3, 0.3, 0.5, 0.15
    ell0, s, p, K0, r, H, gamma = 0.3, 0.1, 0.4, 0.02, 0.07, 3, 0.8
    gain = linear_gain(delta, a, b)
    ell = linear_learnability(delta, ell0, s)
    without_cost = dV_ddelta_variable_ell(delta, p, ell, s, gain, b, c, H, gamma)
    with_cost = dV_ddelta_variable_cost(delta, p, ell, s, gain, b, r, c, H, gamma)
    numeric = central_difference(
        lambda point: intervention_value_m01(
            point,
            p,
            linear_learnability(point, ell0, s),
            linear_gain(point, a, b),
            K0 + r * point,
            c,
            H,
            gamma,
        ),
        delta,
    )
    assert with_cost == pytest.approx(without_cost - r)
    assert with_cost == pytest.approx(numeric, abs=1e-9)


def test_invalid_canonical_and_kink_points_are_rejected_for_differentiation() -> None:
    with pytest.raises(ValueError, match="delta > c"):
        validate_strictly_switchable(0.15, 0.15, 0.3)
    with pytest.raises(ValueError, match=r"h\(delta\) > 0"):
        validate_strictly_switchable(0.3, 0.15, 0.15)
    with pytest.raises(ValueError, match="delta > c"):
        intervention_value_m01(0.15, 0.4, 0.7, 0.3, 0.02, 0.15, 3, 0.8)
