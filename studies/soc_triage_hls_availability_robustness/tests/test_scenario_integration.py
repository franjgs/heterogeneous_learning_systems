import json
from pathlib import Path

import pytest

from studies.soc_triage_hls_availability_robustness.execution_api import CalendarBackend
from studies.soc_triage_hls_availability_robustness.run_scenario import run_one
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario
from studies.soc_triage_hls_availability_robustness.triage_execution import run_triage_flow


ROOT = Path(__file__).parents[1]
V2 = ROOT / "config" / "SOC_REFERENCE_ORGANIZATION_V2.json"
V2_24X7 = ROOT / "config" / "SOC_REFERENCE_ORGANIZATION_V2_24X7.json"
V2_LOAD = ROOT / "config" / "SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json"


def test_v2_json_to_calendar_engine_is_reproducible_and_dispatches_one_route():
    scenario = load_scenario(V2)
    triage, trace = scenario.triage_scenario_for(998001)
    result = run_triage_flow(triage, flow_mode=scenario.flow_mode,
                             backend=CalendarBackend())
    recommendation = triage.recommendation_l2_by_alert
    assert set(result.stage_results["L1"].tasks_by_alert) == {
        aid for aid, positive in recommendation.items() if not positive
    }
    assert set(result.stage_results["L2"].tasks_by_alert) == {
        aid for aid, positive in recommendation.items() if positive
    }
    assert all(outcome.investigation_count == 1 for outcome in result.outcomes)
    assert {outcome.status for outcome in result.outcomes} >= {
        "completed_within_sla", "completed_late"
    }
    by_id = {row.routed.alert.alert_id: row for row in trace}
    for level in ("L1", "L2"):
        resources = {r.analyst.analyst_id: r for r in scenario.organization.resources_for(level)}
        for assignment in result.stage_results[level].assignments:
            assert by_id[assignment.alert_id].routed.alert.task_class in resources[assignment.analyst_id].analyst.eligible_classes

    first = run_one(V2, seed=998001)
    again = run_one(V2, seed=998001)
    assert first == again
    assert first["generated_alerts"] == 476
    assert first["confusion_counts"] == {"TP": 35, "FP": 28, "TN": 405, "FN": 8}
    assert first["investigation_counts"] == {1: 476}
    assert first["sla_status_counts"]["completed_late"] > 0
    legacy = run_one(V2, seed=998001, flow_mode="historical_l1_then_l2")
    assert legacy["flow_mode"] == "historical_l1_then_l2"
    assert legacy["investigation_counts"] == {1: 413, 2: 63}


def test_24x7_variant_changes_only_calendars_and_keeps_seeded_trace():
    original = json.loads(V2.read_text())
    variant = json.loads(V2_24X7.read_text())
    original_analysts = original["organization"]["analysts"]
    variant_analysts = variant["organization"]["analysts"]
    assert len(original_analysts) == len(variant_analysts)
    for before, after in zip(original_analysts, variant_analysts):
        assert {k: v for k, v in before.items() if k != "calendar"} == {
            k: v for k, v in after.items() if k != "calendar"
        }
        assert after["calendar"] == {"kind": "continuous"}

    base, all_day = load_scenario(V2), load_scenario(V2_24X7)
    base_trace = base.generate_trace(998001)
    all_day_trace = all_day.generate_trace(998001)
    assert base_trace == all_day_trace
    for resource in all_day.organization.analysts:
        assert all(resource.calendar.available(t / 4) for t in range(7 * 24 * 4))

    triage, _ = all_day.triage_scenario_for(998001)
    result = run_triage_flow(triage, flow_mode=all_day.flow_mode,
                             backend=CalendarBackend())
    assert len(result.outcomes) == len(base_trace)
    assert all(outcome.investigation_count == 1 for outcome in result.outcomes)
    original_alerts = {alert.alert_id: alert for alert in triage.alerts}
    assert all(outcome.deadline == original_alerts[outcome.alert_id].deadline
               for outcome in result.outcomes)
    assert all(task.suspension == 0
               for stage in result.stage_results.values()
               for task in stage.tasks_by_alert.values())

    output = run_one(V2_24X7, seed=998001)
    assert output["generated_alerts"] == 476
    assert output["confusion_counts"] == {"TP": 35, "FP": 28, "TN": 405, "FN": 8}
    assert output["investigation_counts"] == {1: 476}
    assert output["sla_status_counts"] == {
        "completed_within_sla": 476, "completed_late": 0, "pending": 0
    }
    assert output["effective_service_work_h_by_stage"]["L1"] > 0
    assert output["effective_service_work_h_by_stage"]["L2"] > 0


def test_load_regime_profile_targets_lp_load_and_recovers_with_fixed_organization():
    from studies.soc_triage_hls_availability_robustness.analyze_load_regimes import diagnose
    from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import (
        CapacityDemandProfile, DemandRegime, assess_capacity,
    )

    base = json.loads(V2_24X7.read_text())
    configured = json.loads(V2_LOAD.read_text())
    assert configured["organization"] == base["organization"]
    assert configured["generation"] == base["generation"]
    assert configured["policies"] == base["policies"]
    assert configured["deadlines"] == base["deadlines"]
    assert configured["time"] == base["time"]
    assert configured["cost_model"] == base["cost_model"]
    assert configured["flow_mode"] == base["flow_mode"]
    assert configured["experiment"]["seed_start"] == base["experiment"]["seed_start"]
    metadata = {"regimes", "schedule_reference", "generator_mapping"}
    assert {k: v for k, v in configured["demand_profile"].items() if k not in metadata} == {
        k: v for k, v in base["demand_profile"].items() if k not in metadata
    }
    assert [(x["start_h"], x["end_h"]) for x in configured["demand_profile"]["regimes"]] == [
        (0, 96), (96, 120), (120, 168)
    ]

    scenario = load_scenario(V2_LOAD)
    first = scenario.generate_trace(998001)
    assert first == scenario.generate_trace(998001)
    assert len(first) == 2812
    assert all(0 <= row.routed.alert.arrival < 168 for row in first)
    assert [sum(regime["start_h"] <= row.routed.alert.arrival < regime["end_h"]
                for row in first)
            for regime in scenario.demand_profile["regimes"]] == [1606, 601, 605]

    demand = scenario.demand_profile
    profile = CapacityDemandProfile(
        regimes=tuple(DemandRegime(x["name"], x["start_h"], x["end_h"],
                                   x["arrival_rate_by_class"])
                      for x in demand["regimes"]),
        prevalence_by_class=demand["prevalence_by_class"],
        sensitivity_by_class=demand["sensitivity_by_class"],
        false_positive_rate_by_class=demand["false_positive_rate_by_class"],
        alpha=demand["alpha"], beta=demand["beta"], gamma=demand["gamma"],
        flow_mode=scenario.flow_mode,
    )
    capacity = assess_capacity(scenario.organization, profile)
    target = {"ordinary": .85, "overload_pulse": 1.25, "recovery": .65}
    l1_rows = [x for x in capacity.regimes if x.level == "L1"]
    assert [x.relative_load for x in l1_rows] == pytest.approx(
        [target[x.regime] for x in l1_rows], abs=1e-10
    )

    result = diagnose(V2_LOAD, 998001)
    assert {str(k): v for k, v in result["investigation_count_distribution"].items()} == {"1": 2812}
    assert sum(result["sla_status_counts"].values()) == 2812
    assert result["sla_status_counts"] == {
        "completed_within_sla": 2743, "completed_late": 69, "pending": 0
    }
    assert result["suspension_total_h_by_level"] == {"L1": 0.0, "L2": 0.0}
    pulse = result["realized_regimes"][1]
    recovery = result["realized_regimes"][2]
    assert pulse["hourly_queue"]["L1"]["max_sampled_hourly_queue"] > 0
    assert recovery["boundary_state_end"]["L1"]["queued_alerts"] == 0
    assert recovery["boundary_state_end"]["L1"]["remaining_work_of_owned_h"] < pulse["boundary_state_start"]["L1"]["remaining_work_of_owned_h"]

