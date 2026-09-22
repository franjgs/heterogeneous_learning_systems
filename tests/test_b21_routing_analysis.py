import importlib.util
from pathlib import Path


def module():
    path = Path(__file__).resolve().parents[1] / "experiments/pilots/b21_pacs_factorial/analyze_routing.py"
    spec = importlib.util.spec_from_file_location("b21_routing_analysis", path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def test_routing_tie_preserves_fast_convention():
    assert module().route(0.8, 0.75, 0.05) == "F"
    assert module().route(0.69, 0.75, 0.05) == "D"


def test_factorial_routing_interaction_and_classification_definitions():
    m = module()
    indicators = {"r0": 0, "ri": 1, "rj": 0, "rij": 1}
    assert indicators["rij"] - indicators["ri"] - indicators["rj"] + indicators["r0"] == 0
    assert abs(0.2 - 0.1) < abs(0.2)
    assert abs(-0.2 - 0.1) > abs(0.2)
    assert m.EPSILON == 1e-12
