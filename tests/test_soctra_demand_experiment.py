import csv
from datetime import datetime

import pytest

from studies.soctra_demand_experiment import (
    N_AGENTS,
    _evaluate,
    _organization,
    _ordered,
    _synthetic_demand_controls,
    _service_times,
    load_soctra_demand,
)


def _write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("id_alerta", "@timestamp0", "proyecto"))
        writer.writeheader()
        writer.writerows(rows)


def test_local_adapter_uses_timestamp_and_project_without_emitting_labels(tmp_path):
    path = tmp_path / "restricted.csv"
    _write_csv(path, [
        {"id_alerta": "private-a", "@timestamp0": "2023-02-01 00:00:00", "proyecto": "private-project-b"},
        {"id_alerta": "private-b", "@timestamp0": "2023-02-01 00:00:00", "proyecto": "private-project-a"},
        {"id_alerta": "private-c", "@timestamp0": "2023-02-01 12:00:00", "proyecto": "private-project-a"},
    ])
    result = load_soctra_demand(path)
    trace = result.traces["full_observed_coverage"]

    assert result.row_count == result.unique_alert_ids == 3
    assert result.project_class_count == 2
    assert result.tied_timestamp_rows == 2
    assert result.tied_timestamp_groups == 1
    assert result.max_tie_size == 2
    assert trace.horizon == 1.0
    assert [task.arrival_time for task in trace.arrivals] == [0.0, 0.0, 0.5]
    assert all(isinstance(task.task_type, int) for task in trace.arrivals)
    assert "private-project" not in repr(result)


def test_restricted_csv_rejects_duplicate_alert_ids_and_timezone_ambiguity(tmp_path):
    path = tmp_path / "duplicate.csv"
    base = {"@timestamp0": "2023-02-01 00:00:00", "proyecto": "p"}
    _write_csv(path, [{**base, "id_alerta": "x"}, {**base, "id_alerta": "x"}])
    with pytest.raises(ValueError, match="duplicate alert identifier"):
        load_soctra_demand(path)

    _write_csv(path, [{"id_alerta": "x", "@timestamp0": "2023-02-01T00:00:00+01:00", "proyecto": "p"}])
    with pytest.raises(ValueError, match="timezone-aware"):
        load_soctra_demand(path)


def test_organization_profiles_keep_equal_per_class_mean_and_maximum():
    for profile in ("homogeneous", "specialized", "partially_polyvalent", "dominant_worker"):
        matrix = _organization(profile, 27)
        assert len(matrix) == N_AGENTS
        assert all(len(row) == 27 for row in matrix)
        assert all(sum(matrix[i][k] for i in range(N_AGENTS)) / N_AGENTS == pytest.approx(0.6) for k in range(27))
        expected_max = {
            "homogeneous": 0.6,
            "specialized": 0.9,
            "partially_polyvalent": 0.75,
            "dominant_worker": 0.9,
        }[profile]
        assert all(max(matrix[i][k] for i in range(N_AGENTS)) == expected_max for k in range(27))


def test_offered_load_is_exact_under_uniform_and_class_heterogeneous_service():
    from studies.soctra_demand_experiment import DemandTrace
    from hls.temporal_allocation import ArrivalTask

    arrivals = tuple(ArrivalTask(i / 10, i % 3) for i in range(9))
    for profile in ("uniform", "class_heterogeneous"):
        service = _service_times(arrivals, 0.9, profile)
        assert len(service) == 3
        assert sum(service[task.task_type] for task in arrivals) / N_AGENTS == pytest.approx(0.9)

    trace = DemandTrace("fixture", arrivals, 1.0, datetime(2024, 1, 1), datetime(2025, 1, 1))
    for policy_result in _evaluate(trace, "partially_polyvalent", 0.9, "uniform", "class_ascending").values():
        assert len(policy_result.decisions) == len(arrivals)


def test_same_timestamp_order_is_explicit_and_reproducible():
    from collections import Counter
    from hls.temporal_allocation import ArrivalTask

    arrivals = (ArrivalTask(0.0, 1), ArrivalTask(0.0, 0), ArrivalTask(0.0, 2))
    ascending = _ordered(arrivals, "class_ascending")
    descending = _ordered(arrivals, "class_descending")
    assert tuple(task.task_type for task in ascending) == (0, 1, 2)
    assert tuple(task.task_type for task in descending) == (2, 1, 0)
    assert ascending == _ordered(arrivals, "class_ascending")
    assert Counter(task.arrival_time for task in ascending) == Counter(task.arrival_time for task in descending)
    assert Counter(task.task_type for task in ascending) == Counter(task.task_type for task in descending)


def test_timestamp_normalization_preserves_order_and_relative_separations(tmp_path):
    path = tmp_path / "times.csv"
    _write_csv(path, [
        {"id_alerta": "a", "@timestamp0": "2023-02-01 00:00:00", "proyecto": "p"},
        {"id_alerta": "b", "@timestamp0": "2023-02-01 06:00:00", "proyecto": "p"},
        {"id_alerta": "c", "@timestamp0": "2023-02-01 18:00:00", "proyecto": "p"},
    ])
    trace = load_soctra_demand(path).traces["full_observed_coverage"]
    times = tuple(task.arrival_time for task in trace.arrivals)
    assert trace.horizon == 1.0
    assert times == (0.0, 0.25, 0.75)
    assert times[1] - times[0] == pytest.approx((6 * 3600) / (24 * 3600))
    assert times[2] - times[1] == pytest.approx((12 * 3600) / (24 * 3600))
    assert times == tuple(sorted(times))


def test_policy_replays_conserve_tasks_and_capacity_and_report_horizon_backlog(tmp_path):
    from datetime import datetime
    from studies.soctra_demand_experiment import DemandTrace
    from hls.temporal_allocation import ArrivalTask

    arrivals = tuple(ArrivalTask(t, k) for t, k in (
        (0.0, 0), (0.0, 1), (0.2, 0), (0.4, 1), (0.9, 0),
    ))
    trace = DemandTrace("fixture", arrivals, 1.0, datetime(2024, 1, 1), datetime(2024, 1, 2))
    for result in _evaluate(trace, "partially_polyvalent", 0.9, "uniform", "class_ascending").values():
        assert len(result.decisions) == len(arrivals)
        assert tuple(d.task_index for d in result.decisions) == tuple(range(len(arrivals)))
        assert len({d.task_index for d in result.decisions}) == len(arrivals)
        assert all(d.service_start >= d.arrival_time for d in result.decisions)
        assert all(d.completion_time >= d.service_start for d in result.decisions)
        for agent in range(N_AGENTS):
            assigned = [d for d in result.decisions if d.agent_index == agent]
            assert all(
                right.service_start >= left.completion_time
                for left, right in zip(assigned, assigned[1:])
            )
            expected_pending = [d for d in assigned if d.completion_time > trace.horizon]
            assert result.pending_task_count_by_agent[agent] == len(expected_pending)
            assert result.pending_work_at_horizon_by_agent[agent] >= 0.0
            assert 0.0 <= result.utilization_by_agent[agent] <= 1.0
        completed_at_horizon = sum(d.completion_time <= trace.horizon for d in result.decisions)
        assert completed_at_horizon + result.pending_task_count == len(arrivals)
        assert sum(result.assigned_count_by_agent) == len(arrivals)
        assert sum(result.effectiveness_by_agent) == pytest.approx(result.total_effectiveness)
        total_work = sum(0.9 * N_AGENTS / len(arrivals) for _ in arrivals)
        busy_work_until_horizon = sum(result.utilization_by_agent) * trace.horizon
        assert busy_work_until_horizon + result.pending_work_at_horizon == pytest.approx(total_work)


def test_p1_concentration_occurs_with_exact_ties_and_strict_dominance():
    from hls.temporal_allocation import run_max_effectiveness_temporal_policy

    arrivals = tuple((index / 10, 0) for index in range(10))
    tied = run_max_effectiveness_temporal_policy(arrivals, ((0.6,),) * 4, (0.01,), 1.0)
    strict = run_max_effectiveness_temporal_policy(arrivals, ((0.9,), (0.5,), (0.5,), (0.5,)), (0.01,), 1.0)
    assert tied.assigned_count_by_agent == strict.assigned_count_by_agent == (10, 0, 0, 0)
    assert tied.mean_response_time == strict.mean_response_time
    assert tied.assigned_count_by_agent[0] / len(arrivals) == 1.0


def test_p1_maximum_tie_structure_matches_declared_organization_profiles():
    expected_ties = {
        "homogeneous": 4,
        "specialized": 1,
        "partially_polyvalent": 2,
        "dominant_worker": 1,
    }
    for profile, tied_agents in expected_ties.items():
        matrix = _organization(profile, 27)
        for task_type in range(27):
            maximum = max(row[task_type] for row in matrix)
            assert sum(row[task_type] == maximum for row in matrix) == tied_agents


def test_synthetic_demand_controls_preserve_count_horizon_and_declared_margins(tmp_path):
    path = tmp_path / "fixture.csv"
    _write_csv(path, [
        {"id_alerta": f"id-{i}", "@timestamp0": f"2023-02-01 00:00:{i:02d}", "proyecto": f"p-{i % 2}"}
        for i in range(6)
    ])
    source = load_soctra_demand(path)
    controls = _synthetic_demand_controls(source)
    observed = source.traces["full_observed_coverage"]
    assert all(len(trace.arrivals) == len(observed.arrivals) for trace in controls.values())
    assert all(trace.horizon == observed.horizon == 1.0 for trace in controls.values())
    assert tuple(task.arrival_time for task in controls["observed_times_balanced_classes"].arrivals) == tuple(
        task.arrival_time for task in observed.arrivals
    )
    classes = source.project_class_count
    counts = [sum(task.task_type == k for task in controls["uniform_times_balanced_classes"].arrivals) for k in range(classes)]
    assert max(counts) - min(counts) <= 1
    uniform_times = [task.arrival_time for task in controls["uniform_times_balanced_classes"].arrivals]
    assert all(uniform_times[i] < uniform_times[i + 1] for i in range(len(uniform_times) - 1))
