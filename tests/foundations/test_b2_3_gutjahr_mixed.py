import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT / "experiments" / "foundations"
    / "b2_3_gutjahr_mixed" / "run.py"
)

spec = importlib.util.spec_from_file_location("b2_3", MODULE_PATH)
b2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b2)


def test_piecewise_phi():
    assert b2.phi(-2.0) == 0.0
    assert b2.phi(-1.0) == 0.0
    assert b2.phi(0.0) == 0.5
    assert b2.phi(1.0) == 1.0
    assert b2.phi(2.0) == 1.0


def test_exact_example2_policy_value():
    value = b2.objective(0.5, 1.0)

    assert abs(value - 13.0 / 8.0) < 1e-12


def test_mixed_policy_beats_every_extremal_policy():
    mixed = b2.objective(0.5, 1.0)

    (_, best_extreme), candidates = b2.best_extremal_policy()

    assert len(candidates) == 4
    assert mixed > best_extreme


def test_grid_recovers_gutjahr_optimum():
    policy, value = b2.exhaustive_grid(0.001)

    assert np.allclose(policy, [0.5, 1.0], atol=0.0005)
    assert abs(value - 13.0 / 8.0) < 1e-12
