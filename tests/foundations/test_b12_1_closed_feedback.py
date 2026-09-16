import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]

MODULE_PATH = (
    ROOT / "experiments" / "foundations"
    / "b12_1_closed_feedback" / "run.py"
)

spec = importlib.util.spec_from_file_location(
    "b12_1",
    MODULE_PATH,
)
b12 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b12)


CONFIG = {
    "periods": 6,
    "problem_probabilities": [0.6, 0.4],
    "z_initial": [-0.5, -0.2],
    "beta": [0.02, 0.02],
    "eta": [0.30, 0.30],
    "tolerance": 1e-12,
}


def test_learning_step_matches_beam2_equation():
    z = np.array([-0.5, -0.2])
    x = np.array([1.0, 0.0])

    result = b12.learning_step(
        z,
        x,
        beta=np.array([0.02, 0.02]),
        eta=np.array([0.30, 0.30]),
    )

    expected = np.array([-0.22, -0.22])

    assert np.allclose(result, expected)


def test_routing_produces_extremal_allocation():
    choice, allocation, _ = b12.routing(
        [0.6, 0.4],
        [-0.5, -0.2],
    )

    assert choice in (0, 1)
    assert np.isclose(allocation.sum(), 1.0)
    assert set(allocation).issubset({0.0, 1.0})


def test_state_is_passed_to_next_period():
    history = b12.simulate(CONFIG)

    for t in range(len(history) - 1):
        assert np.allclose(
            history[t]["z_after"],
            history[t + 1]["z_before"],
        )


def test_closed_feedback_identity():
    history = b12.simulate(CONFIG)

    assert b12.verify_closed_feedback(
        history,
        CONFIG,
    )


def test_routing_uses_evolved_state():
    history = b12.simulate(CONFIG)

    for row in history:
        z = np.asarray(row["z_before"])

        choice, _, _ = b12.routing(
            CONFIG["problem_probabilities"],
            z,
        )

        assert choice == row["choice"]
