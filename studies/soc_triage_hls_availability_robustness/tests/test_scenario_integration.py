import json
from pathlib import Path

from studies.soc_triage_hls_availability_robustness.execution_api import CalendarBackend
from studies.soc_triage_hls_availability_robustness.run_scenario import run_one
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario
from studies.soc_triage_hls_availability_robustness.triage_execution import run_triage_flow


ROOT = Path(__file__).parents[1]
V2 = ROOT / "config" / "SOC_REFERENCE_ORGANIZATION_V2.json"
V2_24X7 = ROOT / "config" / "SOC_REFERENCE_ORGANIZATION_V2_24X7.json"


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

