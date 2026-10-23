"""Focused HLS-PEF checks; no simulator or policy is imported."""

from dataclasses import replace
from math import isclose

import pytest

from hls.performance_evaluation import (
    EvaluationProfile, EvaluationRecord, PerformanceEvaluator, Status,
)
from experiments.run_hls_pef_retrospective import run


METRICS = (
    "original_reward_cumulative", "ces_cumulative", "functional_success_rate",
    "functional_deficit_cumulative", "production_cumulative",
    "resource_usage:effort",
)


def profile(*, info: str = "same", demand: str = "d", horizon: int = 2,
            availability=None) -> EvaluationProfile:
    return EvaluationProfile(
        "test", "S4", "case", "synthetic", "test problem", {"p": "CES"},
        "capacity", METRICS, information_regime=info, temporal_horizon=horizon,
        demand_distribution_id=demand, resource_units={"effort": "effort"},
        metric_availability={} if availability is None else availability,
    )


def records(policy: str = "p") -> tuple[EvaluationRecord, ...]:
    return (
        EvaluationRecord("S4", "case", policy, 0, "x", (0.4, 0.2), (0.3, 0.5),
                         False, (0.0, 0.3), {"effort": 2.0}, 0.6, 0.6,
                         provenance="fixture#/0"),
        EvaluationRecord("S4", "case", policy, 1, "y", (0.0, 1.0), (0.0, 0.9),
                         True, (0.0, 0.0), {"effort": 1.0}, 1.0, 1.0,
                         provenance="fixture#/1"),
    )


def test_metrics_temporal_aggregation_units_and_provenance():
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile())
    result = evaluator.evaluate("test", "p", records())
    assert result["original_reward_cumulative"].value == pytest.approx(1.6)
    assert result["ces_cumulative"].value == pytest.approx(1.6)
    assert result["functional_success_rate"].value == pytest.approx(0.5)
    assert result["functional_deficit_cumulative"].value == pytest.approx(0.3)
    assert result["production_cumulative"].value == pytest.approx(1.6)
    assert result["resource_usage:effort"].value == pytest.approx(3.0)
    assert result["resource_usage:effort"].unit == "effort"
    assert result["functional_success_rate"].aggregation == "successes/demanded_periods"
    assert result["ces_cumulative"].provenance == ("fixture#/0", "fixture#/1")


def test_missing_and_undefined_are_not_zero():
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile())
    missing = list(records())
    missing[1] = replace(missing[1], ces=None)
    result = evaluator.evaluate("test", "p", missing)
    assert result["ces_cumulative"].status is Status.NOT_RECORDED
    assert result["ces_cumulative"].value is None
    assert result["original_reward_cumulative"].status is Status.VALID
    no_demand = [replace(row, demand=None) for row in records()]
    result = evaluator.evaluate("test", "p", no_demand)
    assert result["functional_success_rate"].status is Status.UNDEFINED
    assert result["functional_success_rate"].value is None
    unobserved = list(records())
    unobserved[1] = replace(unobserved[1], ces=None,
                            field_status={"ces": Status.NOT_OBSERVABLE})
    result = evaluator.evaluate("test", "p", unobserved)
    assert result["ces_cumulative"].status is Status.NOT_OBSERVABLE


def test_availability_states_and_zero():
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile(availability={
        "ces_cumulative": Status.NOT_APPLICABLE,
        "production_cumulative": Status.NOT_OBSERVABLE,
    }))
    result = evaluator.evaluate("test", "p", records())
    assert result["ces_cumulative"].status is Status.NOT_APPLICABLE
    assert result["production_cumulative"].status is Status.NOT_OBSERVABLE
    zero = evaluator.import_historical("test", "p", "functional_deficit_cumulative", 0.0,
                                       "fixture#/zero")
    assert zero.status is Status.VALID and zero.value == 0.0
    with pytest.raises(ValueError):
        evaluator.import_historical("test", "p", "ces_cumulative", float("nan"), "fixture#/nan")


def test_comparability_and_information_label():
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile())
    left = evaluator.evaluate("test", "p", records())["ces_cumulative"]
    right = evaluator.import_historical("test", "q", "ces_cumulative", 1.0, "fixture#/q")
    difference = evaluator.compare(left, right)
    assert difference.value == pytest.approx(0.6)
    assert difference.note == "same_information_regime"
    other_info = PerformanceEvaluator()
    other_info.register_profile(replace(profile(), information_regime="more_information"))
    unequal = other_info.import_historical("test", "q", "ces_cumulative", 1.0, "fixture#/q")
    with pytest.raises(ValueError, match="information"):
        evaluator.compare(left, unequal)
    assert evaluator.compare(left, unequal, allow_information_inequality=True).note == "informationally_unequal"
    other_demand = PerformanceEvaluator()
    other_demand.register_profile(replace(profile(), demand_distribution_id="other"))
    incompatible = other_demand.import_historical("test", "q", "ces_cumulative", 1.0, "fixture#/q")
    with pytest.raises(ValueError, match="incompatible"):
        evaluator.compare(left, incompatible)
    other_aggregation = PerformanceEvaluator()
    other_aggregation.register_profile(replace(profile(), aggregation_rules="one unit per task"))
    different_unit = other_aggregation.import_historical("test", "q", "ces_cumulative", 1.0,
                                                         "fixture#/q")
    with pytest.raises(ValueError, match="incompatible"):
        evaluator.compare(left, different_unit)
    with pytest.raises(ValueError, match="incompatible"):
        evaluator.compare(left, evaluator.evaluate("test", "p", records())["original_reward_cumulative"])
    other_objective = PerformanceEvaluator()
    other_objective.register_profile(replace(profile(), decision_objective={"q": "service"}))
    reward_q = other_objective.import_historical("test", "q", "original_reward_cumulative",
                                                  1.0, "fixture#/reward_q")
    reward_p = evaluator.evaluate("test", "p", records())["original_reward_cumulative"]
    with pytest.raises(ValueError, match="incompatible"):
        evaluator.compare(reward_p, reward_q)


def test_invalid_periods_and_duplicate_registration():
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile())
    with pytest.raises(ValueError, match="duplicate"):
        evaluator.register_profile(profile())
    with pytest.raises(ValueError, match="period"):
        evaluator.evaluate("test", "p", records()[:1])
    with pytest.raises(ValueError, match="context"):
        evaluator.evaluate("test", "q", records())


def test_weighted_episode_aggregation_and_probability_validation():
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile())
    low = tuple(replace(row, episode_id="low", branch_probability=0.25) for row in records())
    high = tuple(replace(row, episode_id="high", branch_probability=0.75,
                         ces=(row.ces or 0.0) + 1.0) for row in records())
    result = evaluator.evaluate_weighted_episodes("test", "p", (low, high))
    assert result["ces_cumulative"].value == pytest.approx(3.1)
    assert result["ces_cumulative"].aggregation == "exact_branch_probability_expectation"
    invalid = tuple(replace(row, branch_probability=0.1) for row in high)
    with pytest.raises(ValueError, match="sum to one"):
        evaluator.evaluate_weighted_episodes("test", "p", (low, invalid))
    duplicate_id = tuple(replace(row, episode_id="low", branch_probability=0.75)
                         for row in records())
    with pytest.raises(ValueError, match="IDs must be unique"):
        evaluator.evaluate_weighted_episodes("test", "p", (low, duplicate_id))


def test_retrospective_s4_s7_regression_and_provenance():
    first = run()
    second = run()
    assert first == second
    a = first["s7"]["policies"]["A"]["ces_cumulative"]
    b = first["s7"]["policies"]["B"]["ces_cumulative"]
    ma = first["s7"]["policies"]["MA"]["ces_cumulative"]
    mb = first["s7"]["policies"]["MB"]["ces_cumulative"]
    assert a["value"] == pytest.approx(3.1628653621)
    assert b["value"] == pytest.approx(3.1743777327)
    assert ma["value"] == pytest.approx(3.0346209871)
    assert mb["value"] == pytest.approx(3.0346209871)
    contrasts = first["s7"]["contrasts_CES"]
    assert contrasts["planning_without_transfer"]["value"] == pytest.approx(0.1282443750)
    assert contrasts["planning_with_transfer"]["value"] == pytest.approx(0.1397567456)
    assert contrasts["transfer_with_planning"]["value"] == pytest.approx(0.0115123706)
    assert contrasts["transfer_without_planning"]["value"] == pytest.approx(0.0)
    assert first["s7"]["interaction_CES"] == pytest.approx(0.0115123706)
    assert "stored_historical_aggregate" in b["note"]
    assert "mechanistic_robustness" in b["provenance"][0]
    assert first["s7"]["policies"]["B"]["production_cumulative"]["status"] == "NOT_RECORDED"
    assert first["s7"]["policies"]["A"]["functional_success_rate"]["value"] == pytest.approx(3.001 / 4)
    assert first["s7"]["policies"]["B"]["functional_deficit_cumulative"]["value"] == pytest.approx(0.175)
    s4 = first["s4"]
    for policy in ("A", "B"):
        assert isclose(s4["policies"][policy]["ces_cumulative"]["value"],
                       s4["policies"][policy]["original_reward_cumulative"]["value"])
        assert s4["policies"][policy]["ces_cumulative"]["note"] == "recomputed_from_period_records"


def test_s7_pilot_exact_branches_metrics_and_policy_independence():
    from experiments.run_hls_pef_s7_pilot import run as run_pilot

    first = run_pilot()
    second = run_pilot()
    assert first == second
    assert first["branch_count"] == 16
    assert first["branch_probability_sum"] == pytest.approx(1.0)
    assert first["validation"]["weighted_CES_matches_policy_value"]
    assert len(first["pairwise_differences"]["ces_cumulative"]["all_pairs"]) == 6
    expected = {"A": 3.1628653621, "B": 3.1743777327,
                "MA": 3.0346209871, "MB": 3.0346209871}
    for policy, value in expected.items():
        metrics = first["policies"][policy]
        assert metrics["ces_cumulative"]["value"] == pytest.approx(value)
        assert len(first["expected_period_summaries"][policy]) == 4
    a = first["policies"]["A"]
    b = first["policies"]["B"]
    assert a["functional_success_rate"]["value"] == pytest.approx(0.75025)
    assert b["functional_success_rate"]["value"] == pytest.approx(0.75)
    assert a["functional_deficit_cumulative"]["value"] == pytest.approx(0.04995)
    assert b["functional_deficit_cumulative"]["value"] == pytest.approx(0.175)
    assert b["resource_usage:teaching_effort"]["value"] == pytest.approx(0.25)
    assert b["resource_usage:teaching_resource"]["value"] == pytest.approx(0.5)
    assert b["teaching_actions_cumulative"]["value"] == pytest.approx(1.0)
    assert a["resource_usage:total_effort"]["value"] == pytest.approx(
        a["resource_usage:productive_effort"]["value"]
        + a["resource_usage:teaching_resource"]["value"])
    assert b["resource_usage:total_effort"]["value"] == pytest.approx(
        b["resource_usage:productive_effort"]["value"]
        + b["resource_usage:teaching_resource"]["value"])
    # Adapting existing replays is observational: replay actions are retained
    # verbatim in the records and do not feed back into later branches.
    records = first["branch_records"]["B"]
    assert all(len(branch["period_records"]) == 4 for branch in records)
    assert sum(branch["probability"] for branch in records) == pytest.approx(1.0)
