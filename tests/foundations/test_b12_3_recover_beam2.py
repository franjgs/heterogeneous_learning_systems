import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]

MODULE_PATH = (
    ROOT / "experiments" / "foundations"
    / "b12_3_recover_beam2" / "run.py"
)

spec = importlib.util.spec_from_file_location("b12_3", MODULE_PATH)
b12 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b12)


CONFIG = {
    "z_initial": [-0.5, -0.2],
    "beta": [0.05, 0.02],
    "eta": [0.30, 0.20],
    "allocation_path": [
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [0.0, 1.0],
    ],
    "tolerance": 1e-12,
}


def test_initial_closed_form_state():
    z = b12.closed_form_state(
        CONFIG["z_initial"],
        CONFIG["beta"],
        CONFIG["eta"],
        CONFIG["allocation_path"],
        0,
    )

    assert np.allclose(z, CONFIG["z_initial"])


def test_first_update_matches_equation():
    history = b12.simulate_fixed_allocations(CONFIG)

    expected = np.array([-0.25, -0.22])

    assert np.allclose(history[0]["z_after"], expected)


def test_recursive_matches_closed_form_each_period():
    history = b12.simulate_fixed_allocations(CONFIG)

    for row in history:
        assert np.allclose(
            row["z_before"],
            row["closed_form_before"],
        )
        assert np.allclose(
            row["z_after"],
            row["closed_form_after"],
        )


def test_final_state_matches_direct_formula():
    history = b12.simulate_fixed_allocations(CONFIG)

    expected = b12.closed_form_state(
        CONFIG["z_initial"],
        CONFIG["beta"],
        CONFIG["eta"],
        CONFIG["allocation_path"],
        len(CONFIG["allocation_path"]),
    )

    assert np.allclose(history[-1]["z_after"], expected)


def test_beam2_limiting_case_is_recovered():
    history = b12.simulate_fixed_allocations(CONFIG)

    assert b12.verify_beam2_recovery(history, CONFIG)
