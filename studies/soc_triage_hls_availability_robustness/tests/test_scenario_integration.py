from pathlib import Path

from studies.soc_triage_hls_availability_robustness.execution_api import CalendarBackend
from studies.soc_triage_hls_availability_robustness.run_scenario import run_one
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario
from studies.soc_triage_hls_availability_robustness.triage_execution import run_triage_flow


ROOT = Path(__file__).parents[1]
V2 = ROOT / "config" / "SOC_REFERENCE_ORGANIZATION_V2.json"


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

