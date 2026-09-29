"""Gate for the minimal preregistered RQ0-A/B runner."""

import importlib.util
import sys
from pathlib import Path

import pytest


RUNNER = (
    Path(__file__).parents[2]
    / "experiments"
    / "synthetic"
    / "rq0"
    / "run_initial_campaign.py"
)

spec = importlib.util.spec_from_file_location("rq0_runner", RUNNER)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)


EXPECTED_NAMES = (
    "B*",
    "REDUNDANT",
    "FREE_RESOURCE",
    "NO_COUPLING",
    "INTERFERENCE",
    "TRANSFER",
    "SPECIALIZED",
    "MAX_COUPLING",
    "NO_DEVELOPMENT",
)


def test_runner_returns_exactly_nine_preregistered_results():
    results = module.run_campaign()

    assert len(results) == 9
    assert tuple(result.name for result in results) == EXPECTED_NAMES


def test_runner_records_only_frozen_comparison_quantities():
    result = module.run_campaign()[0]

    assert set(result.__dataclass_fields__) == {
        "name",
        "j_hls",
        "j_sep_min",
        "j_sep_max",
        "j_sep_omega",
        "delta_j_cons",
        "delta_omega",
    }


def test_derived_quantities_are_defined_exactly_as_preregistered():
    for result in module.run_campaign():
        assert result.delta_j_cons == pytest.approx(
            result.j_hls - result.j_sep_max
        )
        assert result.delta_omega == pytest.approx(
            result.j_hls - result.j_sep_omega
        )


def test_sep_omega_constructive_boundary_matches_hls():
    for result in module.run_campaign():
        assert result.delta_omega == pytest.approx(0.0, abs=1e-12)


def test_strong_sep_interval_is_well_formed():
    for result in module.run_campaign():
        assert result.j_sep_min <= result.j_sep_max + 1e-12
