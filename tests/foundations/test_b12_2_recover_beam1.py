import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]

MODULE_PATH = (
    ROOT / "experiments" / "foundations"
    / "b12_2_recover_beam1" / "run.py"
)

spec = importlib.util.spec_from_file_location("b12_2", MODULE_PATH)
b12 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b12)


CONFIG = {
    "periods": 6,
    "problem_probabilities": [0.6, 0.4],
    "z_initial": [-0.5, -0.2],
    "beta": [0.0, 0.0],
    "eta": [0.0, 0.0],
    "tolerance": 1e-12,
}


def test_zero_evolution_preserves_state():
    history = b12.b12_1.simulate(CONFIG)
    z0 = np.asarray(CONFIG["z_initial"])

    for row in history:
        assert np.allclose(row["z_before"], z0)
        assert np.allclose(row["z_after"], z0)


def test_routing_scores_are_static():
    history = b12.b12_1.simulate(CONFIG)
    scores0 = history[0]["routing_scores"]

    for row in history:
        assert np.allclose(row["routing_scores"], scores0)


def test_choice_is_static():
    history = b12.b12_1.simulate(CONFIG)
    choice0 = history[0]["choice"]

    assert all(row["choice"] == choice0 for row in history)


def test_allocation_is_static():
    history = b12.b12_1.simulate(CONFIG)
    allocation0 = history[0]["allocation"]

    for row in history:
        assert np.allclose(row["allocation"], allocation0)


def test_beam1_limiting_case_is_recovered():
    history = b12.b12_1.simulate(CONFIG)

    assert b12.verify_beam1_recovery(history, CONFIG)
