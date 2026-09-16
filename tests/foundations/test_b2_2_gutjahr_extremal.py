import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT
    / "experiments"
    / "foundations"
    / "b2_2_gutjahr_extremal"
    / "run.py"
)

spec = importlib.util.spec_from_file_location("b2_2", MODULE_PATH)
b2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b2)


def test_logistic_is_convex_for_negative_z():
    z = np.linspace(-5.0, -0.01, 1000)

    assert np.all(
        b2.phi_second_derivative(z) > 0.0
    )


def test_all_reachable_states_remain_in_convex_region():
    z_initial = np.array([-3.0, -2.8])
    eta = np.array([0.30, 0.25])
    periods = 4

    max_z = z_initial + eta * (periods - 1)

    assert np.all(max_z < 0.0)
    assert np.all(
        b2.phi_second_derivative(max_z) > 0.0
    )


def test_extremal_search_has_expected_size():
    policies = b2.extremal_policies(4)

    assert len(policies) == 16

    for p in policies:
        assert np.allclose(p.sum(axis=1), 1.0)
        assert np.all(
            np.logical_or(p == 0.0, p == 1.0)
        )


def test_extremal_optimum_matches_full_grid():
    params = {
        "z_initial": [-3.0, -2.8],
        "beta": [0.0, 0.0],
        "eta": [0.30, 0.25],
        "weights": [1.0, 1.0],
    }

    extreme_value, _, _, _ = b2.optimize(
        b2.extremal_policies(4),
        params,
    )

    grid_value, _, _, _ = b2.optimize(
        b2.grid_policies(4, 0.05),
        params,
    )

    assert abs(
        grid_value - extreme_value
    ) < 1e-12


def test_objective_uses_pre_decision_state():
    policy = np.array([[1.0, 0.0], [0.0, 1.0]])
    value, z, _ = b2.evaluate_policy(
        policy,
        z_initial=[-1.0, -0.5],
        beta=[0.1, 0.2],
        eta=[0.4, 0.3],
        weights=[2.0, 3.0],
    )

    expected_z = np.array([[-1.0, -0.5], [-0.7, -0.7]])
    expected_value = 2.0 * b2.phi(-1.0) + 3.0 * b2.phi(-0.7)

    assert np.allclose(z, expected_z)
    assert abs(value - expected_value) < 1e-12
