from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.run_hls_s2b_intertemporal_budget import run_s2b


def _without_timings(value):
    if isinstance(value, dict):
        return {key: _without_timings(item) for key, item in value.items()
                if "seconds" not in key}
    if isinstance(value, (tuple, list)):
        return type(value)(_without_timings(item) for item in value)
    return value


def test_s2b_sufficient_budget_has_no_planning_gap_and_leaves_resource_unused():
    result = run_s2b()["cases"]["A_sufficient_budget"]
    assert result["myopic"]["reward"] == pytest.approx(1.9)
    assert result["bellman"]["reward"] == pytest.approx(1.9)
    assert result["global_exhaustive"]["reward"] == pytest.approx(1.9)
    assert result["bellman_minus_myopic"] == pytest.approx(0.0)
    assert result["myopic"]["budget_consumed"] == 2
    assert result["myopic"]["budget_remaining"] == 1


def test_s2b_binding_budget_is_reserved_for_higher_future_reward():
    result = run_s2b()["cases"]["B_shared_budget_binding"]
    myopic = result["myopic"]
    bellman = result["bellman"]
    assert myopic["reward"] == pytest.approx(0.9)
    assert bellman["reward"] == pytest.approx(1.0)
    assert result["global_exhaustive"]["reward"] == pytest.approx(1.0)
    assert result["bellman_minus_myopic"] == pytest.approx(0.1)
    assert myopic["periods"][0]["assignments"][0]["task"] == "t1"
    assert myopic["periods"][1]["assignments"] == ()
    assert bellman["periods"][0]["assignments"] == ()
    assert bellman["periods"][1]["assignments"][0]["task"] == "t0"
    assert result["bellman_minus_enumeration"] == pytest.approx(0.0)


def test_s2b_zero_budget_and_budget_conservation():
    cases = run_s2b()["cases"]
    zero = cases["zero_budget_control"]
    assert zero["myopic"]["reward"] == zero["bellman"]["reward"] == 0.0
    assert zero["global_exhaustive"]["reward"] == 0.0
    for case in cases.values():
        for name in ("myopic", "bellman"):
            policy = case[name]
            assert policy["budget_consumed"] + policy["budget_remaining"] == case["budget"]
            remaining = case["budget"]
            for period in policy["periods"]:
                assert period["budget_before"] == remaining
                count = period["units_executed"]
                assert count == len(period["assignments"])
                assert count <= 3
                assert count <= remaining
                assert period["budget_after"] == remaining - count
                assert len({item["agent"] for item in period["assignments"]}) == count
                assert len({item["unit"] for item in period["assignments"]}) == count
                demand = period["demand_by_task"]
                served = period["demand_satisfied"]
                assert all(0 <= served[task] <= demand[task] for task in demand)
                assert period["demand_unserved"] == {
                    task: demand[task] - served[task] for task in demand
                }
                assert sum(served.values()) == count
                if name == "myopic":
                    assert period["reward"] == pytest.approx(
                        period["immediate_optimum_given_budget"]
                    )
                remaining = period["budget_after"]
            assert remaining == policy["budget_remaining"]


def test_s2b_bellman_matches_independent_enumeration_and_is_reproducible():
    first = run_s2b()
    second = run_s2b()
    assert _without_timings(first) == _without_timings(second)
    for case in first["cases"].values():
        assert case["bellman"]["reward"] == pytest.approx(case["global_exhaustive"]["reward"])
        assert case["bellman"]["reward"] + 1e-12 >= case["myopic"]["reward"]
        assert case["global_exhaustive"]["budget_feasible_sequences"] > 0
