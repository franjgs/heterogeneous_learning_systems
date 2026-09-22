import importlib.util
from pathlib import Path

import pytest


def b21():
    path = Path(__file__).resolve().parents[1] / "experiments/pilots/b21_pacs_factorial/run.py"
    spec = importlib.util.spec_from_file_location("b21_factorial", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_factorial_constants_and_formulas():
    m = b21()
    assert m.DOMAINS == ("photo", "art_painting", "cartoon", "sketch")
    assert m.N_VALUES == (25, 50, 100)
    assert m.COSTS == (0.0, 0.02, 0.05, 0.1, 0.15)
    assert m.gamma_learn(0.8, 0.6, 0.5, 0.4) == pytest.approx(0.1)


def test_operational_value_routes_by_domain():
    m = b21()
    fast = dict(zip(m.DOMAINS, (0.4, 0.8, 0.2, 0.7)))
    deep = dict(zip(m.DOMAINS, (0.6, 0.5, 0.9, 0.1)))
    value, route = m.operational_value(fast, deep, 0.1)
    assert route == {"photo": "D", "art_painting": "F", "cartoon": "D", "sketch": "F"}
    assert value == pytest.approx((0.6 - 0.1 + 0.8 + 0.9 - 0.1 + 0.7) / 4)


def test_fit_count_and_test_closed():
    m = b21()
    assert 5 * (2 + 3 * (4 + 6)) == 160
    source = (Path(__file__).resolve().parents[1] / "experiments/pilots/b21_pacs_factorial/run.py").read_text()
    assert 'splits["test"]' not in source
    assert "test_metrics" not in source
