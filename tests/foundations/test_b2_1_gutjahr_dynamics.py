import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT
    / "experiments"
    / "foundations"
    / "b2_1_gutjahr_dynamics"
    / "run.py"
)

spec = importlib.util.spec_from_file_location("b2_1", MODULE_PATH)
b2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b2)


def test_logistic_efficiency_bounds():
    z = np.array([-100.0, -1.0, 0.0, 1.0, 100.0])
    gamma = b2.logistic_phi(z)

    assert np.all(gamma >= 0.0)
    assert np.all(gamma <= 1.0)
    assert abs(b2.logistic_phi(0.0) - 0.5) < 1e-12


def test_closed_form_equals_recursive_dynamics():
    allocations = np.array([0.75, 0.50, 0.25, 1.00, 0.00])

    closed = b2.competence_trajectory(
        z_initial=-1.0,
        beta=0.10,
        eta=0.80,
        allocations=allocations,
    )

    recursive = b2.recursive_trajectory(
        z_initial=-1.0,
        beta=0.10,
        eta=0.80,
        allocations=allocations,
    )

    assert np.allclose(closed, recursive, atol=1e-12)


def test_first_period_is_initial_competence():
    allocations = np.array([0.75, 0.50, 0.25])

    z = b2.competence_trajectory(
        z_initial=-1.0,
        beta=0.10,
        eta=0.80,
        allocations=allocations,
    )

    assert abs(z[0] - (-1.0)) < 1e-12


def test_period_two_update():
    allocations = np.array([0.75, 0.50])

    z = b2.competence_trajectory(
        z_initial=-1.0,
        beta=0.10,
        eta=0.80,
        allocations=allocations,
    )

    expected = -1.0 - 0.10 + 0.80 * 0.75

    assert abs(z[1] - expected) < 1e-12
