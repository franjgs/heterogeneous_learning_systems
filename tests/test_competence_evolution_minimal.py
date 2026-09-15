import numpy as np
import pytest

from hls.competence_evolution_minimal import (
    beta_critical,
    complementary_switch_gain,
    division_gap,
    numeric_rebalancing_argmin,
    rebalancing_effective_cost,
    rebalancing_solution,
    rk4_specialization,
    specialization_eigenvalues,
    specialization_jacobian_at_symmetric,
    specialization_rhs,
    symmetric_equilibrium,
)


def test_division_gap_and_complementary_switch_threshold() -> None:
    competence = np.array([[0.8, 0.2], [0.2, 0.8]])
    assert division_gap(competence) == pytest.approx(1.2)
    assert complementary_switch_gain(1.0, 0.6, 0.0) == 0.0
    assert complementary_switch_gain(1.0, 0.0, 0.6) == 0.0
    assert complementary_switch_gain(1.0, 0.6, 0.6) == pytest.approx(0.2)


def test_symmetric_equilibrium_and_critical_threshold() -> None:
    eta, depreciation = 0.4, 0.2
    assert symmetric_equilibrium(eta, depreciation) == pytest.approx(0.5)
    assert beta_critical(eta, depreciation) == pytest.approx(2.0)


def test_analytic_jacobian_matches_finite_difference() -> None:
    eta, depreciation, beta = 0.4, 0.2, 1.7
    c_star = symmetric_equilibrium(eta, depreciation)
    state = np.full(4, c_star)
    epsilon = 1e-6
    numeric = np.empty((4, 4))
    for column in range(4):
        displacement = np.zeros(4)
        displacement[column] = epsilon
        numeric[:, column] = (
            specialization_rhs(state + displacement, eta, depreciation, beta)
            - specialization_rhs(state - displacement, eta, depreciation, beta)
        ) / (2 * epsilon)
    assert numeric == pytest.approx(specialization_jacobian_at_symmetric(eta, depreciation, beta), abs=1e-9)


def test_critical_eigenvalue_changes_sign_at_beta_critical() -> None:
    eta, depreciation = 0.4, 0.2
    critical = beta_critical(eta, depreciation)
    assert specialization_eigenvalues(eta, depreciation, 0.9 * critical)[-1] < 0
    assert specialization_eigenvalues(eta, depreciation, critical)[-1] == pytest.approx(0.0, abs=1e-12)
    assert specialization_eigenvalues(eta, depreciation, 1.1 * critical)[-1] > 0


def test_symmetric_perturbations_decay_below_and_select_opposite_branches_above() -> None:
    eta, depreciation = 0.4, 0.2
    c_star = symmetric_equilibrium(eta, depreciation)
    direction = np.array([1.0, 1.0, -1.0, -1.0])
    below = rk4_specialization(np.full(4, c_star) + 0.05 * direction, eta, depreciation, 1.0, 0.01, 8000)[-1]
    positive = rk4_specialization(np.full(4, c_star) + 0.05 * direction, eta, depreciation, 3.0, 0.01, 12000)[-1]
    negative = rk4_specialization(np.full(4, c_star) - 0.05 * direction, eta, depreciation, 3.0, 0.01, 12000)[-1]
    assert np.linalg.norm(below - c_star) < 1e-4
    assert positive @ direction > 0.1
    assert negative @ direction < -0.1


def test_beta_critical_diverges_as_depreciation_approaches_zero() -> None:
    assert beta_critical(0.4, 1e-4) > beta_critical(0.4, 1e-3) > beta_critical(0.4, 1e-2)


def test_rebalancing_regimes_and_formula() -> None:
    assert rebalancing_solution(1.0, 0.5, 1.0, 1.0)[2] == "TRAIN"
    x, y, regime, q, horizon = rebalancing_solution(1.0, 1.5, 1.0, 1.0)
    assert regime == "MIXED"
    assert x == pytest.approx(0.5)
    assert y == pytest.approx(0.5)
    assert q == pytest.approx(1.375)
    assert horizon == pytest.approx(q)
    assert rebalancing_solution(1.0, 2.5, 1.0, 1.0)[2] == "ROUTE"


def test_rebalancing_numeric_argmin_and_boundaries() -> None:
    for a in (0.5, 1.0, 1.5, 2.0, 2.5):
        _, y_star, _, q_star, _ = rebalancing_solution(1.0, a, 1.0, 1.0)
        y_numeric, q_numeric = numeric_rebalancing_argmin(1.0, a, 1.0, 1.0)
        assert y_numeric == pytest.approx(y_star, abs=1e-4)
        assert q_numeric == pytest.approx(q_star, abs=1e-8)


def test_mixed_cost_is_strictly_lower_only_in_interior_regime() -> None:
    _, _, regime, q_mixed, _ = rebalancing_solution(1.0, 1.5, 1.0, 1.0)
    assert regime == "MIXED"
    assert q_mixed < 1.5  # Q_T
    assert q_mixed < 1.5  # Q_R
    assert rebalancing_solution(1.0, 1.0, 1.0, 1.0)[3] == pytest.approx(1.0)
    assert rebalancing_solution(1.0, 2.0, 1.0, 1.0)[3] == pytest.approx(1.5)


def test_rebalancing_effective_cost_rejects_invalid_domain() -> None:
    with pytest.raises(ValueError):
        rebalancing_effective_cost(-0.1, 1.0, 1.0, 1.0, 1.0)
    with pytest.raises(ValueError):
        rebalancing_solution(1.0, 1.0, 0.0, 1.0)
