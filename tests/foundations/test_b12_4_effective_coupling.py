import importlib.util
import itertools
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]

MODULE_PATH = (
    ROOT / "experiments" / "foundations"
    / "b12_4_effective_coupling" / "run.py"
)

CONFIG_PATH = (
    ROOT / "experiments" / "foundations"
    / "b12_4_effective_coupling" / "config.json"
)

spec = importlib.util.spec_from_file_location("b12_4", MODULE_PATH)
b12 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b12)

CONFIG = json.loads(CONFIG_PATH.read_text())


def test_intervention_changes_next_state_when_learning_exists():
    case = b12.evaluate_case(
        [0.5, 0.5],
        [-0.2, -0.2],
        0.0,
        0.3,
        5,
        1e-12,
    )

    assert case["state_changed"]


def test_intervention_does_not_change_state_when_learning_is_zero():
    beta = np.array([0.05, 0.05])
    eta = np.zeros(2)

    h0 = b12.simulate_with_initial_intervention(
        [0.5, 0.5], [-0.2, -0.2],
        beta, eta, 5, 0
    )
    h1 = b12.simulate_with_initial_intervention(
        [0.5, 0.5], [-0.2, -0.2],
        beta, eta, 5, 1
    )

    assert np.allclose(h0[0]["z_after"], h1[0]["z_after"])


def test_decoupled_control_has_same_future_decisions():
    case = b12.evaluate_case(
        [0.55, 0.45],
        [-0.4, -0.2],
        0.05,
        0.3,
        5,
        1e-12,
    )

    assert not case["control_future_decisions_changed"]


def test_parameter_sweep_contains_multiple_coupled_cases():
    cases = b12.sweep(CONFIG)
    coupled = [c for c in cases if c["effective_coupling"]]

    assert len(coupled) > 1


def test_effect_is_not_present_in_decoupled_controls():
    cases = b12.sweep(CONFIG)

    assert all(
        not c["control_state_changed"]
        and not c["control_future_decisions_changed"]
        for c in cases
    )


def test_coupled_cases_do_not_depend_on_routing_ties():
    cases = b12.sweep(CONFIG)
    coupled = [c for c in cases if c["effective_coupling"]]

    assert coupled
    assert all(not c["future_routing_tie"] for c in coupled)
    assert min(c["minimum_future_score_margin"] for c in coupled) > 0.01


def test_initial_intervention_is_only_initial_difference():
    h0 = b12.simulate_with_initial_intervention(
        [0.45, 0.55], [-0.4, -0.4],
        np.array([0.05, 0.05]), np.array([0.5, 0.5]), 5, 0
    )
    h1 = b12.simulate_with_initial_intervention(
        [0.45, 0.55], [-0.4, -0.4],
        np.array([0.05, 0.05]), np.array([0.5, 0.5]), 5, 1
    )

    assert np.allclose(h0[0]["z_before"], h1[0]["z_before"])
    assert np.allclose(h0[0]["scores"], h1[0]["scores"])
    assert h0[0]["natural_choice"] == h1[0]["natural_choice"]
    assert h0[0]["allocation"] != h1[0]["allocation"]
    assert all(
        row["choice"] == row["natural_choice"]
        for history in (h0, h1)
        for row in history[1:]
    )


def test_independent_oracle_recovers_36_of_96():
    def route(p, z):
        scores = [p[i] / (1.0 + math.exp(-z[i])) for i in range(2)]
        return 0 if scores[0] >= scores[1] else 1

    def choices(p, z_initial, beta, eta, first_choice):
        z = list(z_initial)
        sequence = []
        for period in range(CONFIG["periods"]):
            choice = first_choice if period == 0 else route(p, z)
            sequence.append(choice)
            z = [
                z[i] - beta + eta * float(choice == i)
                for i in range(2)
            ]
        return tuple(sequence)

    coupled = 0
    controls = 0
    total = 0
    for p, z0, beta, eta in itertools.product(
        CONFIG["problem_probability_grid"],
        CONFIG["z_initial_grid"],
        CONFIG["beta_grid"],
        CONFIG["eta_grid"],
    ):
        total += 1
        path0 = choices(p, z0, beta, eta, 0)
        path1 = choices(p, z0, beta, eta, 1)
        next0 = tuple(
            z0[i] - beta + eta * float(i == 0) for i in range(2)
        )
        next1 = tuple(
            z0[i] - beta + eta * float(i == 1) for i in range(2)
        )
        coupled += next0 != next1 and path0[1:] != path1[1:]

        control0 = choices(p, z0, beta, 0.0, 0)
        control1 = choices(p, z0, beta, 0.0, 1)
        controls += control0[1:] != control1[1:]

    assert total == 96
    assert coupled == 36
    assert controls == 0
