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
    from hls.temporal_allocation import ArrivalTask

    arrivals = (ArrivalTask(0.0, 1), ArrivalTask(0.0, 0), ArrivalTask(0.0, 2))
    ascending = _ordered(arrivals, "class_ascending")
    descending = _ordered(arrivals, "class_descending")
    assert tuple(task.task_type for task in ascending) == (0, 1, 2)
    assert tuple(task.task_type for task in descending) == (2, 1, 0)
    assert ascending == _ordered(arrivals, "class_ascending")


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
