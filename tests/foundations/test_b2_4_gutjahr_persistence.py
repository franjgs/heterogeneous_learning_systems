import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT / "experiments" / "foundations"
    / "b2_4_gutjahr_persistence" / "run.py"
)

spec = importlib.util.spec_from_file_location(
    "b2_4",
    MODULE_PATH,
)
b2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b2)


PARAMS = {
    "z_initial": [-1.0, -0.8, -1.2],
    "eta": [0.35, 0.25, 0.45],
    "weights": [1.0, 1.0, 1.0],
}


def test_phi_is_strictly_increasing():
    z = np.linspace(-5.0, 5.0, 1001)
    y = b2.phi(z)

    assert np.all(np.diff(y) > 0.0)


def test_policy_space_size():
    results = b2.enumerate_extremal_policies(
        periods=6,
        classes=3,
        params=PARAMS,
    )

    assert len(results) == 3 ** 6


def test_persistence_detection():
    assert b2.is_persistent((0, 0, 0, 0))
    assert b2.is_persistent((2, 2, 2))
    assert not b2.is_persistent((0, 0, 1, 0))


def test_best_extremal_policy_has_persistent_optimum():
    results = b2.enumerate_extremal_policies(
        periods=6,
        classes=3,
        params=PARAMS,
    )

    best = max(r["value"] for r in results)

    optimal = [
        r for r in results
        if abs(r["value"] - best) <= 1e-12
    ]

    assert any(
        b2.is_persistent(r["choices"])
        for r in optimal
    )


def test_best_persistent_equals_global_extremal_optimum():
    results = b2.enumerate_extremal_policies(
        periods=6,
        classes=3,
        params=PARAMS,
    )

    global_best = max(
        r["value"] for r in results
    )

    persistent_values = []

    for i in range(3):
        value, _ = b2.evaluate_extremal_policy(
            (i,) * 6,
            PARAMS["z_initial"],
            PARAMS["eta"],
            PARAMS["weights"],
        )
        persistent_values.append(value)

    assert abs(
        global_best - max(persistent_values)
    ) <= 1e-12


def test_experience_affects_only_later_periods():
    value, z = b2.evaluate_extremal_policy(
        (0, 0),
        z_initial=[-1.0, -0.8],
        eta=[0.35, 0.25],
        weights=[1.0, 1.0],
    )

    assert np.allclose(z, [[-1.0, -0.8], [-0.65, -0.8]])
    assert abs(value - (b2.phi(-1.0) + b2.phi(-0.65))) < 1e-12
