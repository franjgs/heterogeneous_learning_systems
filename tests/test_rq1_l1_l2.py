import csv
from datetime import datetime

import pytest

from hls.rq1_allocation import Alert, Analyst
from hls.rq1_l1_l2 import RoutedAlert, simulate_l1_l2
from studies.rq1_soctra_l1_l2_integration import (
    _pool, format_report, load_oos_predictions, run_replay,
)
from studies.soctra_demand_experiment import SourceAlertDemand


def _analyst(name, allowed):
    return Analyst(name, frozenset(allowed), {task: 0.8 for task in allowed})


def _rows():
    return (
        RoutedAlert(Alert("opaque-a", 0.0, "p", 2.0), True, False),
        RoutedAlert(Alert("opaque-b", 0.0, "p", 2.0), False, True),
    )


def _run(rows, l2_eligibility=("p",), policy="B0", mode="historical_label_reference"):
    return simulate_l1_l2(
        rows, [_analyst("l1", {"p"})], [_analyst("l2", l2_eligibility)],
        {"p": 0.1}, {"p": 0.2}, policy=policy,
        admission_horizon=1.0, drain_period=0.5, coordination_latency=0.0,
        decision_mode=mode,
    )


def test_fixed_historical_label_routes_only_selected_l1_completions_to_l2():
    result = _run(_rows())
    records = {row.alert_id: row for row in result.escalation_records}
    assert records["opaque-a"].historical_label is True
    assert records["opaque-a"].recommendation is False
    assert records["opaque-a"].observed_effective_analyst_decision is None
    assert records["opaque-a"].scenario_routing_decision is True
    assert records["opaque-a"].entered_l2
    assert not records["opaque-b"].entered_l2
    assert len(result.l1_simulation.assignments) == 2
    assert len(result.l2_simulation.assignments) == 1
    assert result.after_drain.admitted == 2
    assert result.after_drain.pending == 0
    assert result.at_horizon.l1_backlog + result.at_horizon.l2_backlog == result.at_horizon.pending
    assert result.after_drain.l1_backlog + result.after_drain.l2_backlog == result.after_drain.pending


def test_hypothetical_recommendation_acceptance_is_separate_from_history():
    result = _run(_rows(), mode="hypothetical_recommendation_acceptance")
    records = {row.alert_id: row for row in result.escalation_records}
    assert records["opaque-a"].historical_label is True
    assert records["opaque-a"].recommendation is False
    assert records["opaque-a"].observed_effective_analyst_decision is None
    assert records["opaque-a"].scenario_routing_decision is False
    assert not records["opaque-a"].entered_l2
    assert records["opaque-b"].observed_effective_analyst_decision is None
    assert records["opaque-b"].scenario_routing_decision is True
    assert records["opaque-b"].entered_l2


def test_escalation_conserves_tasks_and_prevents_double_processing():
    result = _run(_rows(), policy="B2")
    l1_ids = [job.alert_id for job in result.l1_simulation.assignments]
    l2_ids = [job.alert_id for job in result.l2_simulation.assignments]
    assert len(l1_ids) == len(set(l1_ids)) == 2
    assert len(l2_ids) == len(set(l2_ids)) == 1
    assert set(l2_ids).issubset(l1_ids)
    assert result.after_drain.completed_within_sla + result.after_drain.completed_late + result.after_drain.pending == 2


def test_project_eligibility_can_leave_l2_work_pending():
    result = _run(_rows(), l2_eligibility=("other-project",))
    assert result.after_drain.l1_backlog == 0
    assert result.after_drain.l2_backlog == 1
    assert result.after_drain.pending == 1
    assert not result.l2_simulation.assignments


def test_hypothetical_project_eligibility_is_encoded_in_both_role_pools():
    l1 = _pool("L1", 4, 8, "specialist_backup")
    l2 = _pool("L2", 2, 8, "specialist_backup")
    for task_class in range(8):
        assert sum(task_class in analyst.eligible_classes for analyst in l1) == 2
        assert sum(task_class in analyst.eligible_classes for analyst in l2) == 1


def test_l1_completion_at_drain_cutoff_is_counted_as_l2_backlog():
    row = RoutedAlert(Alert("boundary", 0.0, "p", 3.0), True)
    result = simulate_l1_l2(
        [row], [_analyst("l1", {"p"})], [_analyst("l2", {"p"})],
        {"p": 1.5}, {"p": 0.1}, policy="B0", admission_horizon=1.0,
        drain_period=0.5, coordination_latency=0.0,
    )
    assert result.after_drain.l1_backlog == 0
    assert result.after_drain.l2_backlog == result.after_drain.pending == 1
    assert result.after_drain.l1_backlog + result.after_drain.l2_backlog == result.after_drain.pending
    assert result.escalation_records[0].entered_l2


def test_two_level_simulation_is_reproducible():
    assert _run(_rows(), policy="B3") == _run(_rows(), policy="B3")


def test_oos_prediction_loader_requires_available_at_alert_time_and_training_cutoff(tmp_path):
    path = tmp_path / "predictions.csv"
    fields = ("id_alerta", "recommendation", "out_of_sample", "available_at", "training_cutoff", "model_id", "evaluation_split")

    def write(available, cutoff):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerow({
                "id_alerta": "source-id", "recommendation": "true", "out_of_sample": "true",
                "available_at": available, "training_cutoff": cutoff,
                "model_id": "model-v1", "evaluation_split": "test",
            })

    # The test fixture's source key must be produced through the same namespace.
    import hashlib
    source = (SourceAlertDemand(
        hashlib.sha256(b"hls-rq1-alert-key-v1\0source-id").hexdigest(),
        datetime(2024, 2, 1), 0.5, 2, True,
    ),)
    write("2024-02-01T00:00:00", "2024-01-31T00:00:00")
    assert load_oos_predictions(path, source) == {source[0].alert_key: True}
    write("2024-02-02T00:00:00", "2024-01-31T00:00:00")
    with pytest.raises(ValueError, match="not demonstrably available"):
        load_oos_predictions(path, source)
    write("2024-01-31T00:00:00", "2024-02-01T00:00:00")
    with pytest.raises(ValueError, match="not demonstrably available"):
        load_oos_predictions(path, source)


def test_bounded_synthetic_replay_writes_aggregate_only_report(tmp_path):
    from datetime import timedelta

    from studies.soctra_demand_experiment import load_soctra_demand

    source_path = tmp_path / "source-fixture.csv"
    with source_path.open("w", newline="", encoding="utf-8") as handle:
        fields = ("id_alerta", "@timestamp0", "proyecto", "escalada_L2")
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        first = datetime(2024, 1, 1)
        for day in range(90):
            for event in range(3):
                writer.writerow({
                    "id_alerta": f"private-{day}-{event}",
                    "@timestamp0": (first + timedelta(days=day, hours=event * 4)).isoformat(sep=" "),
                    "proyecto": f"private-project-{event}",
                    "escalada_L2": "true" if event == 0 else "false",
                })
    source = load_soctra_demand(source_path)
    results = run_replay(source)
    report = format_report(source, results)
    assert len(results) == 2 * 2 * 4  # two windows × two eligibility profiles × four policies
    assert "B0" in report and "B1" in report and "B2" in report and "B3" in report
    assert "private-project" not in report and "private-" not in report
