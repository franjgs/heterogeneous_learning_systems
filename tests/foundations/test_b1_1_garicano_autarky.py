import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT
    / "experiments"
    / "foundations"
    / "b1_1_garicano_autarky"
    / "run.py"
)

spec = importlib.util.spec_from_file_location("b1_1", MODULE_PATH)
b1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b1)


def test_density_integrates_to_one():
    z = np.linspace(0.0, 1.0, 100001)
    integral = np.trapz(b1.density(z), z)
    assert abs(integral - 1.0) < 1e-8


def test_analytical_optimum_satisfies_foc():
    c = 1.0
    z_star = b1.analytical_optimum(c)
    assert abs(float(b1.density(z_star)) - c) < 1e-12


def test_numerical_optimum_matches_analytical():
    c = 1.0
    z = np.linspace(0.0, 1.0, 10001)

    numerical = float(z[np.argmax(b1.autarky_output(z, c))])
    analytical = b1.analytical_optimum(c)

    assert abs(numerical - analytical) <= 2e-4
