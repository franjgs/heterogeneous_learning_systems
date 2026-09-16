import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT / "experiments" / "foundations"
    / "b2_5_gutjahr_switching" / "run.py"
)

spec = importlib.util.spec_from_file_location("b2_5", MODULE_PATH)
b2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b2)


PARAMS = {
    "periods": 2,
    "z_initial": [1.0, 0.0],
    "beta": [3.0, 0.0],
    "eta": [4.0, 1.0],
    "weights": [1.0, 1.0],
}


def value(policy):
    v, _ = b2.evaluate_extremal_policy(
        policy,
        PARAMS["z_initial"],
        PARAMS["beta"],
        PARAMS["eta"],
        PARAMS["weights"],
    )
    return v


def test_published_phi_is_implemented_literally():
    assert b2.phi(-2.0) == 0.0
    assert b2.phi(-1.0) == 0.0
    assert b2.phi(0.0) == 0.5
    assert b2.phi(1.0) == 1.0
    assert b2.phi(2.0) == 1.0


def test_all_four_extremal_policies_are_evaluated():
    results = b2.enumerate_extremal_policies(PARAMS)
    assert len(results) == 4


def test_published_switching_policy_evaluates_to_1_5():
    assert abs(value((0, 1)) - 1.5) < 1e-12


def test_literal_equations_make_persistent_policy_best():
    results = b2.enumerate_extremal_policies(PARAMS)

    best = max(r["objective"] for r in results)
    optimal = [
        r["choices"]
        for r in results
        if abs(r["objective"] - best) < 1e-12
    ]

    assert optimal == [(0, 0)]
    assert abs(best - 2.0) < 1e-12


def test_published_example3_conclusion_is_not_reproduced():
    assert value((0, 0)) > value((0, 1))


def test_all_published_equation_values_are_recovered():
    expected = {
        (0, 0): 2.0,
        (0, 1): 1.5,
        (1, 0): 0.5,
        (1, 1): 1.5,
    }
    assert all(abs(value(policy) - target) < 1e-12 for policy, target in expected.items())
