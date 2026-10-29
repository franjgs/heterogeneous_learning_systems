"""Run a privacy-conscious, deterministic HLS-02 demand replay.

The input CSV remains local and restricted.  A row is treated as a modeled
arrival proxy, and its project label only selects a hypothetical task class;
neither mapping is asserted to describe human work or analyst competence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from math import ceil, fsum, isclose
from pathlib import Path
from statistics import fmean, pstdev

from hls.temporal_allocation import (
    AdaptiveThresholds,
    ArrivalTask,
    TemporalAllocationResult,
    run_effectiveness_load_temporal_policy,
    run_adaptive_temporal_policy,
    run_fixed_temporal_policy,
    run_lowest_workload_temporal_policy,
    run_max_effectiveness_temporal_policy,
    run_specialist_backup_temporal_policy,
)


N_AGENTS = 4  # Hypothetical study size; not inferred from SOCTRA labels.
OFFERED_LOADS = (0.50, 0.90, 1.20)
ORGANIZATIONS = (
    "homogeneous",
    "specialized",
    "partially_polyvalent",
    "dominant_worker",
)
POLICY_RUNNERS = (
    ("P0", run_fixed_temporal_policy),
    ("P1", run_max_effectiveness_temporal_policy),
    ("P2", run_effectiveness_load_temporal_policy),
)
ORGANIZATIONAL_POLICY_NAMES = ("S0", "S1", "S2", "S3")
ADAPTIVE_POLICY_NAMES = ("S0", "S1", "S2", "S3", "S4")
ORGANIZATIONAL_WINDOW_DAYS = 28
S3_PRIMARY_THRESHOLD = 1.0
S3_THRESHOLD_SENSITIVITY = (0.5, 2.0)
S3_BACKUP_EFFECTIVENESS_FLOOR = 0.50
S4_PRIMARY_THRESHOLDS = AdaptiveThresholds()


@dataclass(frozen=True)
class DemandTrace:
    name: str
    arrivals: tuple[ArrivalTask, ...]
    horizon: float
    start: datetime
    end: datetime


@dataclass(frozen=True)
class SourceDemand:
    traces: dict[str, DemandTrace]
    project_class_count: int
    row_count: int
    unique_alert_ids: int
    tied_timestamp_rows: int
    tied_timestamp_groups: int
    max_tie_size: int
    demand_summaries: dict[str, dict[str, float | int]]
    early_late_project_mix_tv: float | None
    organizational_demand_summaries: dict[str, dict[str, float | int]]


def load_soctra_demand(path: str | Path) -> SourceDemand:
    """Load timestamp/project fields only; never retain or emit source labels."""
    source = Path(path)
    projects: set[str] = set()
    identifiers: set[str] = set()
    records: list[tuple[datetime, str]] = []
    ties: Counter[datetime] = Counter()
    required = {"@timestamp0", "proyecto", "id_alerta"}
    try:
        handle = source.open("r", newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise ValueError("could not open the local SOCTRA CSV") from exc
    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError("SOCTRA CSV lacks required timestamp/project/alert-id fields")
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"malformed SOCTRA CSV record at row {row_number}")
            timestamp_text = (row.get("@timestamp0") or "").strip()
            project = (row.get("proyecto") or "").strip()
            alert_id = (row.get("id_alerta") or "").strip()
            if not timestamp_text or not alert_id:
                raise ValueError(f"missing timestamp or alert identifier at row {row_number}")
            if alert_id in identifiers:
                raise ValueError(f"duplicate alert identifier at row {row_number}")
            identifiers.add(alert_id)
            try:
                timestamp = datetime.fromisoformat(timestamp_text)
            except ValueError as exc:
                raise ValueError(f"invalid timestamp at row {row_number}") from exc
            if timestamp.tzinfo is not None:
                raise ValueError("timezone-aware timestamps require an explicit reviewed conversion")
            # A missing project label is retained as one explicit unclassified class.
            class_label = project if project else "\x00unclassified-project"
            projects.add(class_label)
            records.append((timestamp, class_label))
            ties[timestamp] += 1
    if not records:
        raise ValueError("SOCTRA CSV contains no demand records")

    # Opaque, deterministic class ordering; labels are not returned or written.
    ordered_projects = sorted(
        projects,
        key=lambda value: hashlib.sha256(
            b"hls-soc-demand-class-v1\0" + value.encode("utf-8")
        ).digest(),
    )
    class_index = {label: index for index, label in enumerate(ordered_projects)}
    first_date = min(timestamp.date() for timestamp, _ in records)
    last_date = max(timestamp.date() for timestamp, _ in records)
    windows = {
        "full_observed_coverage": (
            datetime.combine(first_date, time.min),
            datetime.combine(last_date + timedelta(days=1), time.min),
        ),
        "early_calendar_year": (datetime(2023, 1, 1), datetime(2024, 1, 1)),
        "late_12_month_window": (datetime(2024, 9, 1), datetime(2025, 9, 1)),
    }
    traces: dict[str, DemandTrace] = {}
    demand_summaries: dict[str, dict[str, float | int]] = {}
    class_counts_by_trace: dict[str, Counter[int]] = {}
    for name, (start, end) in windows.items():
        duration = (end - start).total_seconds()
        selected = [
            (timestamp, class_index[label])
            for timestamp, label in records
            if start <= timestamp < end
        ]
        if not selected:
            if name == "full_observed_coverage":
                raise ValueError("full SOCTRA coverage unexpectedly has no records")
            continue
        selected.sort(key=lambda item: (item[0], item[1]))
        per_day: Counter[date] = Counter(timestamp.date() for timestamp, _ in selected)
        per_class: Counter[int] = Counter(task_type for _, task_type in selected)
        day_count = (end.date() - start.date()).days
        daily_counts = [per_day.get(start.date() + timedelta(days=offset), 0) for offset in range(day_count)]
        top_counts = sorted(per_class.values(), reverse=True)
        demand_summaries[name] = {
            "rows": len(selected),
            "active_project_classes": len(per_class),
            "top1_share": top_counts[0] / len(selected),
            "top5_share": sum(top_counts[:5]) / len(selected),
            "daily_mean": fmean(daily_counts),
            "daily_cv": pstdev(daily_counts) / fmean(daily_counts) if fmean(daily_counts) else 0.0,
            "daily_peak": max(daily_counts),
        }
        class_counts_by_trace[name] = per_class
        arrivals = tuple(
            ArrivalTask((timestamp - start).total_seconds() / duration, task_type)
            for timestamp, task_type in selected
        )
        traces[name] = DemandTrace(name, arrivals, 1.0, start, end)

    # Select four equal-length windows using demand-only criteria, before any
    # organization or policy is evaluated. These are qualitative pattern
    # exemplars, not estimates of a real SOC's task rate.
    selected_windows = _select_organizational_windows(records, class_index)
    traces.update(selected_windows)
    organizational_demand_summaries: dict[str, dict[str, float | int]] = {}
    for name, trace in selected_windows.items():
        selected = [
            (timestamp, class_index[label])
            for timestamp, label in records
            if trace.start <= timestamp < trace.end
        ]
        daily: Counter[date] = Counter(timestamp.date() for timestamp, _ in selected)
        per_class: Counter[int] = Counter(task_type for _, task_type in selected)
        half_class_counts = (Counter(), Counter())
        for timestamp, label in selected:
            half = 0 if timestamp < trace.start + timedelta(days=14) else 1
            half_class_counts[half][label] += 1
        half_sizes = (sum(half_class_counts[0].values()), sum(half_class_counts[1].values()))
        half_mix_tv = (
            0.5 * fsum(
                abs(
                    half_class_counts[0].get(k, 0) / half_sizes[0]
                    - half_class_counts[1].get(k, 0) / half_sizes[1]
                )
                for k in range(len(class_index))
            )
            if half_sizes[0] and half_sizes[1]
            else 0.0
        )
        counts = sorted(per_class.values(), reverse=True)
        day_count = ORGANIZATIONAL_WINDOW_DAYS
        daily_values = [daily.get(trace.start.date() + timedelta(days=i), 0) for i in range(day_count)]
        mean_daily = fmean(daily_values)
        organizational_demand_summaries[name] = {
            "rows": len(selected),
            "active_project_classes": len(per_class),
            "top1_share": counts[0] / len(selected),
            "top5_share": sum(counts[:5]) / len(selected),
            "daily_mean": mean_daily,
            "daily_cv": pstdev(daily_values) / mean_daily if mean_daily else 0.0,
            "daily_peak": max(daily_values),
            "first_second_mix_tv": half_mix_tv,
        }

    early, late = "early_calendar_year", "late_12_month_window"
    mix_tv = None
    if early in class_counts_by_trace and late in class_counts_by_trace:
        early_counts, late_counts = class_counts_by_trace[early], class_counts_by_trace[late]
        early_total = sum(early_counts.values())
        late_total = sum(late_counts.values())
        mix_tv = 0.5 * fsum(
            abs(early_counts.get(k, 0) / early_total - late_counts.get(k, 0) / late_total)
            for k in range(len(ordered_projects))
        )
    return SourceDemand(
        traces=traces,
        project_class_count=len(projects),
        row_count=len(records),
        unique_alert_ids=len(identifiers),
        tied_timestamp_rows=sum(count for count in ties.values() if count > 1),
        tied_timestamp_groups=sum(count > 1 for count in ties.values()),
        max_tie_size=max(ties.values()),
        demand_summaries=demand_summaries,
        early_late_project_mix_tv=mix_tv,
        organizational_demand_summaries=organizational_demand_summaries,
    )


def _organization(profile: str, n_types: int, alignment: int = 0) -> tuple[tuple[float, ...], ...]:
    matrix = []
    for agent in range(N_AGENTS):
        row = []
        for task_type in range(n_types):
            owner = (task_type + alignment) % N_AGENTS
            if profile == "homogeneous":
                value = 0.60
            elif profile == "specialized":
                value = 0.90 if agent == owner else 0.50
            elif profile == "partially_polyvalent":
                value = 0.75 if agent in {owner, (owner + 1) % N_AGENTS} else 0.45
            elif profile == "dominant_worker":
                value = 0.90 if agent == 0 else 0.50
            else:
                raise ValueError(f"unknown organization profile: {profile}")
            row.append(value)
        matrix.append(tuple(row))
    result = tuple(matrix)
    # All structures have the same per-class mean by construction.
    assert all(isclose(fsum(result[i][k] for i in range(N_AGENTS)) / N_AGENTS, 0.60) for k in range(n_types))
    return result


def _select_organizational_windows(
    records: list[tuple[datetime, str]], class_index: dict[str, int]
) -> dict[str, DemandTrace]:
    """Select fixed 28-day demand-pattern windows without policy outcomes.

    ``usual`` is nearest the median window volume, with lower daily CV as a
    tie-break. ``peak`` maximizes peak/mean daily volume among windows at or
    above the median volume. ``mix_shift`` maximizes total-variation distance
    between the first and second 14 days. ``post_mix_shift`` is the immediately
    following 28 days. Remaining ties use the earlier calendar start.
    """
    first = min(timestamp.date() for timestamp, _ in records)
    last = max(timestamp.date() for timestamp, _ in records)
    daily_total: Counter[date] = Counter(timestamp.date() for timestamp, _ in records)
    daily_class: dict[date, Counter[int]] = {}
    for timestamp, label in records:
        daily_class.setdefault(timestamp.date(), Counter())[class_index[label]] += 1
    width = ORGANIZATIONAL_WINDOW_DAYS
    # A transition window and its post-period must both be fully covered.
    candidate_count = (last - first).days - (2 * width) + 2
    if candidate_count <= 0:
        return {}
    candidates: list[dict[str, object]] = []
    for offset in range(candidate_count):
        start_date = first + timedelta(days=offset)
        days = [start_date + timedelta(days=i) for i in range(width)]
        counts = [daily_total.get(day, 0) for day in days]
        total = sum(counts)
        if total == 0:
            continue
        first_mix, second_mix = Counter(), Counter()
        for day in days[:14]:
            first_mix.update(daily_class.get(day, Counter()))
        for day in days[14:]:
            second_mix.update(daily_class.get(day, Counter()))
        first_n, second_n = sum(first_mix.values()), sum(second_mix.values())
        if not first_n or not second_n:
            continue
        tv = 0.5 * fsum(
            abs(first_mix.get(k, 0) / first_n - second_mix.get(k, 0) / second_n)
            for k in range(len(class_index))
        )
        average = total / width
        candidates.append({
            "start": start_date,
            "total": total,
            "cv": pstdev(counts) / average,
            "peak_ratio": max(counts) / average,
            "mix_tv": tv,
        })
    if not candidates:
        return {}
    median_total = sorted(int(row["total"]) for row in candidates)[(len(candidates) - 1) // 2]
    usual = min(
        candidates,
        key=lambda row: (abs(int(row["total"]) - median_total), float(row["cv"]), row["start"]),
    )
    eligible_peak = [row for row in candidates if int(row["total"]) >= median_total]
    peak = min(
        eligible_peak,
        key=lambda row: (-float(row["peak_ratio"]), -int(row["total"]), row["start"]),
    )
    change = min(
        candidates,
        key=lambda row: (-float(row["mix_tv"]), -int(row["total"]), row["start"]),
    )
    selected = {
        "usual_28d": usual,
        "peak_28d": peak,
        "mix_shift_28d": change,
    }
    result: dict[str, DemandTrace] = {}
    for name, row in selected.items():
        start = datetime.combine(row["start"], time.min)
        end = start + timedelta(days=width)
        events = [
            (timestamp, class_index[label])
            for timestamp, label in records
            if start <= timestamp < end
        ]
        events.sort(key=lambda item: (item[0], item[1]))
        duration = (end - start).total_seconds()
        result[name] = DemandTrace(
            name,
            tuple(ArrivalTask((timestamp - start).total_seconds() / duration, kind) for timestamp, kind in events),
            1.0,
            start,
            end,
        )
    post_start = datetime.combine(change["start"] + timedelta(days=width), time.min)
    post_end = post_start + timedelta(days=width)
    post_events = [
        (timestamp, class_index[label])
        for timestamp, label in records
        if post_start <= timestamp < post_end
    ]
    post_events.sort(key=lambda item: (item[0], item[1]))
    if post_events:
        duration = (post_end - post_start).total_seconds()
        result["post_mix_shift_28d"] = DemandTrace(
            "post_mix_shift_28d",
            tuple(ArrivalTask((timestamp - post_start).total_seconds() / duration, kind) for timestamp, kind in post_events),
            1.0,
            post_start,
            post_end,
        )
    return result


def _fixed_mapping(profile: str, n_types: int, alignment: int = 0) -> tuple[int, ...]:
    # A predeclared balanced responsibility map over opaque project classes.
    # Specialists own their designated class; the other organizations use
    # a fixed round-robin class roster, independent of test arrival order.
    return tuple((task_type + alignment) % N_AGENTS for task_type in range(n_types))


def _service_times(
    arrivals: tuple[ArrivalTask, ...], offered_load: float, service_profile: str
) -> tuple[float, ...]:
    n_types = max(task.task_type for task in arrivals) + 1
    if service_profile == "uniform":
        multipliers = (1.0,) * n_types
    elif service_profile == "class_heterogeneous":
        multipliers = tuple((0.5, 1.0, 1.5)[k % 3] for k in range(n_types))
    else:
        raise ValueError(f"unknown service profile: {service_profile}")
    weighted_work = fsum(multipliers[task.task_type] for task in arrivals)
    scale = offered_load * N_AGENTS / weighted_work
    service = tuple(scale * factor for factor in multipliers)
    offered = fsum(service[task.task_type] for task in arrivals) / N_AGENTS
    assert isclose(offered, offered_load, rel_tol=1e-12, abs_tol=1e-12)
    return service


def _ordered(arrivals: tuple[ArrivalTask, ...], mode: str) -> tuple[ArrivalTask, ...]:
    if mode == "class_ascending":
        return tuple(sorted(arrivals, key=lambda task: (task.arrival_time, task.task_type)))
    if mode == "class_descending":
        return tuple(sorted(arrivals, key=lambda task: (task.arrival_time, -task.task_type)))
    raise ValueError(f"unknown simultaneous-arrival order: {mode}")


def _synthetic_demand_controls(source: SourceDemand) -> dict[str, DemandTrace]:
    """Construct matched controls: preserve either time pattern or neither."""
    observed = source.traces["full_observed_coverage"]
    count = len(observed.arrivals)
    classes = source.project_class_count
    time_only = tuple(
        ArrivalTask(task.arrival_time, index % classes)
        for index, task in enumerate(observed.arrivals)
    )
    fully_balanced = tuple(
        ArrivalTask((index + 0.5) / count, index % classes)
        for index in range(count)
    )
    return {
        "observed_times_balanced_classes": DemandTrace(
            "observed_times_balanced_classes", time_only, 1.0, observed.start, observed.end
        ),
        "uniform_times_balanced_classes": DemandTrace(
            "uniform_times_balanced_classes", fully_balanced, 1.0, observed.start, observed.end
        ),
    }


def _evaluate(
    trace: DemandTrace,
    profile: str,
    offered_load: float,
    service_profile: str,
    tie_order: str,
    alignment: int = 0,
) -> dict[str, TemporalAllocationResult]:
    arrivals = _ordered(trace.arrivals, tie_order)
    n_types = max(task.task_type for task in arrivals) + 1
    matrix = _organization(profile, n_types, alignment)
    service = _service_times(arrivals, offered_load, service_profile)
    mapping = _fixed_mapping(profile, n_types, alignment)
    results = {
        "P0": run_fixed_temporal_policy(arrivals, matrix, service, trace.horizon, mapping),
        "P1": run_max_effectiveness_temporal_policy(arrivals, matrix, service, trace.horizon),
        "P2": run_effectiveness_load_temporal_policy(arrivals, matrix, service, trace.horizon),
    }
    for result in results.values():
        if len(result.decisions) != len(arrivals) or sum(result.assigned_count_by_agent) != len(arrivals):
            raise AssertionError("task conservation failed")
        if tuple(decision.task_index for decision in result.decisions) != tuple(range(len(arrivals))):
            raise AssertionError("task sequence integrity failed")
        if any(
            decision.service_start < decision.arrival_time
            or decision.completion_time < decision.service_start
            for decision in result.decisions
        ):
            raise AssertionError("service timing violates arrival/start/completion order")
        for agent in range(N_AGENTS):
            agent_tasks = [d for d in result.decisions if d.agent_index == agent]
            if any(
                right.service_start < left.completion_time
                for left, right in zip(agent_tasks, agent_tasks[1:])
            ):
                raise AssertionError("single-server FCFS capacity was violated")
            if result.pending_task_count_by_agent[agent] != sum(
                d.completion_time > trace.horizon for d in agent_tasks
            ):
                raise AssertionError("horizon task backlog does not match completion times")
        completed_by_horizon = sum(d.completion_time <= trace.horizon for d in result.decisions)
        if completed_by_horizon + result.pending_task_count != len(arrivals):
            raise AssertionError("completed plus pending tasks does not conserve arrivals")
        if any(work < 0.0 for work in result.pending_work_at_horizon_by_agent):
            raise AssertionError("negative pending work")
        if any(not 0.0 <= value <= 1.0 for value in result.utilization_by_agent):
            raise AssertionError("agent utilization is outside [0, 1]")
        offered_work = fsum(service[task.task_type] for task in arrivals)
        busy_work_by_horizon = trace.horizon * fsum(result.utilization_by_agent)
        if not isclose(
            busy_work_by_horizon + result.pending_work_at_horizon,
            offered_work,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            raise AssertionError("busy plus pending service work does not conserve offered work")
        if not isclose(fsum(result.effectiveness_by_agent), result.total_effectiveness):
            raise AssertionError("agent contributions do not sum to total effectiveness")
    if results["P1"].total_effectiveness + 1e-12 < max(
        results["P0"].total_effectiveness, results["P2"].total_effectiveness
    ):
        raise AssertionError("P1 taskwise effectiveness bound failed")
    return results


def _evaluate_organizational(
    trace: DemandTrace,
    profile: str,
    offered_load: float,
    threshold_multiplier: float = S3_PRIMARY_THRESHOLD,
) -> dict[str, TemporalAllocationResult]:
    """Matched S0-S3 evaluation on one qualitative-pattern demand window."""
    arrivals = _ordered(trace.arrivals, "class_ascending")
    n_types = max(task.task_type for task in arrivals) + 1
    matrix = _organization(profile, n_types)
    service = _service_times(arrivals, offered_load, "uniform")
    results = {
        "S0": run_lowest_workload_temporal_policy(arrivals, matrix, service, trace.horizon),
        "S1": run_max_effectiveness_temporal_policy(arrivals, matrix, service, trace.horizon),
        "S2": run_effectiveness_load_temporal_policy(arrivals, matrix, service, trace.horizon),
        "S3": run_specialist_backup_temporal_policy(
            arrivals, matrix, service, trace.horizon,
            threshold_multiplier, S3_BACKUP_EFFECTIVENESS_FLOOR,
        ),
    }
    # S0 is the new minimum-workload organization. It is not the predeclared
    # fixed-mapping P0 retained by the historical runner.
    for name, result in results.items():
        if len(result.decisions) != len(arrivals):
            raise AssertionError(f"{name}: task conservation failed")
        completed = sum(d.completion_time <= trace.horizon for d in result.decisions)
        if completed + result.pending_task_count != len(arrivals):
            raise AssertionError(f"{name}: completed plus pending does not conserve arrivals")
        if not isclose(fsum(result.effectiveness_by_agent), result.total_effectiveness):
            raise AssertionError(f"{name}: individual contributions do not sum to total")
    return results


def run_soctra_demand_experiment(path: str | Path) -> dict[str, object]:
    """Run a bounded matched replay and sensitivity around recorded event order."""
    source = load_soctra_demand(path)
    full = source.traces["full_observed_coverage"]
    primary: list[dict[str, object]] = []
    for profile in ORGANIZATIONS:
        for load in OFFERED_LOADS:
            for policy, result in _evaluate(full, profile, load, "uniform", "class_ascending").items():
                primary.append(_row("full", profile, load, "uniform", "class_ascending", policy, result))

    historical_windows: list[dict[str, object]] = []
    for trace_name in ("early_calendar_year", "late_12_month_window"):
        trace = source.traces.get(trace_name)
        if trace is None:
            continue
        for profile in ORGANIZATIONS:
            for policy, result in _evaluate(trace, profile, 0.90, "uniform", "class_ascending").items():
                historical_windows.append(_row(trace_name, profile, 0.90, "uniform", "class_ascending", policy, result))

    service_sensitivity: list[dict[str, object]] = []
    for profile in ORGANIZATIONS:
        for load in OFFERED_LOADS:
            for policy, result in _evaluate(full, profile, load, "class_heterogeneous", "class_ascending").items():
                service_sensitivity.append(_row("full", profile, load, "class_heterogeneous", "class_ascending", policy, result))

    tie_sensitivity: list[dict[str, object]] = []
    for profile in ORGANIZATIONS:
        for order in ("class_ascending", "class_descending"):
            for policy, result in _evaluate(full, profile, 0.90, "uniform", order).items():
                tie_sensitivity.append(_row("full", profile, 0.90, "uniform", order, policy, result))

    alignment_sensitivity: list[dict[str, object]] = []
    for profile in ORGANIZATIONS:
        for alignment in range(N_AGENTS):
            for policy, result in _evaluate(full, profile, 0.90, "uniform", "class_ascending", alignment).items():
                row = _row("full", profile, 0.90, "uniform", "class_ascending", policy, result)
                row["alignment"] = alignment
                alignment_sensitivity.append(row)

    synthetic_controls: list[dict[str, object]] = []
    for trace_name, trace in _synthetic_demand_controls(source).items():
        for profile in ORGANIZATIONS:
            for policy, result in _evaluate(trace, profile, 0.90, "uniform", "class_ascending").items():
                synthetic_controls.append(_row(trace_name, profile, 0.90, "uniform", "class_ascending", policy, result))

    return {
        "source": source,
        "primary": tuple(primary),
        "historical_windows": tuple(historical_windows),
        "service_sensitivity": tuple(service_sensitivity),
        "tie_sensitivity": tuple(tie_sensitivity),
        "alignment_sensitivity": tuple(alignment_sensitivity),
        "synthetic_controls": tuple(synthetic_controls),
    }


def run_organizational_strategy_comparison(path: str | Path) -> dict[str, object]:
    """Compare S0-S3 on matched, demand-pattern windows selected without outcomes.

    SOCTRA contributes relative timestamps and opaque class sequence patterns.
    All service loads, team structures and effectiveness matrices remain
    hypothetical; normalized-window replay is not a measured operational rate.
    """
    source = load_soctra_demand(path)
    names = ("usual_28d", "peak_28d", "mix_shift_28d", "post_mix_shift_28d")
    missing = [name for name in names if name not in source.traces]
    if missing:
        raise ValueError(
            "the local snapshot does not span enough nonempty calendar days "
            "for the predeclared 28-day demand windows: " + ", ".join(missing)
        )
    sensitivity: list[dict[str, object]] = []
    for window in names:
        trace = source.traces[window]
        for profile in ORGANIZATIONS:
            for load in OFFERED_LOADS:
                for policy, result in _evaluate_organizational(trace, profile, load).items():
                    sensitivity.append(_row(
                        window, profile, load, "uniform", "class_ascending", policy, result
                    ))
    threshold_rows: list[dict[str, object]] = []
    for window in names:
        trace = source.traces[window]
        for profile in ORGANIZATIONS:
            for threshold in S3_THRESHOLD_SENSITIVITY:
                result = run_specialist_backup_temporal_policy(
                    _ordered(trace.arrivals, "class_ascending"),
                    _organization(profile, max(task.task_type for task in trace.arrivals) + 1),
                    _service_times(trace.arrivals, 0.90, "uniform"),
                    trace.horizon,
                    threshold,
                    S3_BACKUP_EFFECTIVENESS_FLOOR,
                )
                row = _row(window, profile, 0.90, "uniform", "class_ascending", "S3", result)
                row["threshold_multiplier"] = threshold
                threshold_rows.append(row)
    return {
        "source": source,
        "load_sensitivity": tuple(sensitivity),
        "threshold_sensitivity": tuple(threshold_rows),
    }


def run_adaptive_organizational_comparison(path: str | Path) -> dict[str, object]:
    """Run the 240 matched S0-S4 cells and a bounded service-time sensitivity.

    The SOCTRA records supply qualitative relative arrival timing and opaque
    class patterns only. The controller's ``s_ref`` is the arithmetic mean
    of the scenario's fixed class service-time vector. The sensitivity keeps
    the same class service-time vector for every agent and normalizes total
    offered work to the same rho.
    """
    source = load_soctra_demand(path)
    names = ("usual_28d", "peak_28d", "mix_shift_28d", "post_mix_shift_28d")
    missing = [name for name in names if name not in source.traces]
    if missing:
        raise ValueError("missing predeclared demand windows: " + ", ".join(missing))
    primary_rows: list[dict[str, object]] = []
    service_sensitivity_rows: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    for window in names:
        trace = source.traces[window]
        arrivals = _ordered(trace.arrivals, "class_ascending")
        n_types = max(task.task_type for task in arrivals) + 1
        for profile in ORGANIZATIONS:
            matrix = _organization(profile, n_types)
            for load in OFFERED_LOADS:
                service = _service_times(arrivals, load, "uniform")
                baseline = {
                    "S0": run_lowest_workload_temporal_policy(arrivals, matrix, service, trace.horizon),
                    "S1": run_max_effectiveness_temporal_policy(arrivals, matrix, service, trace.horizon),
                    "S2": run_effectiveness_load_temporal_policy(arrivals, matrix, service, trace.horizon),
                    "S3": run_specialist_backup_temporal_policy(
                        arrivals, matrix, service, trace.horizon,
                        S3_PRIMARY_THRESHOLD, S3_BACKUP_EFFECTIVENESS_FLOOR,
                    ),
                }
                adaptive = run_adaptive_temporal_policy(
                    arrivals, matrix, service, trace.horizon, S4_PRIMARY_THRESHOLDS
                )
                all_results = {**baseline, "S4": adaptive.allocation}
                for policy, result in all_results.items():
                    row = _row(window, profile, load, "uniform", "class_ascending", policy, result)
                    if len(result.decisions) != len(arrivals) or row["completed_tasks"] + row["pending_tasks_count"] != len(arrivals):
                        raise AssertionError(f"{policy}: task conservation failed")
                    primary_rows.append(row)
                diagnostics.append({
                    "trace": window,
                    "organization": profile,
                    "offered_load": load,
                    "diagnostics": adaptive.diagnostics,
                })
                if load == 0.90:
                    service = _service_times(arrivals, load, "class_heterogeneous")
                    for policy, result in {
                        "S0": run_lowest_workload_temporal_policy(arrivals, matrix, service, trace.horizon),
                        "S1": run_max_effectiveness_temporal_policy(arrivals, matrix, service, trace.horizon),
                        "S2": run_effectiveness_load_temporal_policy(arrivals, matrix, service, trace.horizon),
                        "S3": run_specialist_backup_temporal_policy(
                            arrivals, matrix, service, trace.horizon,
                            S3_PRIMARY_THRESHOLD, S3_BACKUP_EFFECTIVENESS_FLOOR,
                        ),
                    }.items():
                        service_sensitivity_rows.append(_row(
                            window, profile, load, "class_heterogeneous", "class_ascending", policy, result
                        ))
                    adaptive_sensitivity = run_adaptive_temporal_policy(
                        arrivals, matrix, service, trace.horizon, S4_PRIMARY_THRESHOLDS
                    )
                    service_sensitivity_rows.append(_row(
                        window, profile, load, "class_heterogeneous", "class_ascending", "S4",
                        adaptive_sensitivity.allocation,
                    ))
    return {
        "source": source,
        "primary_rows": tuple(primary_rows),
        "service_sensitivity_rows": tuple(service_sensitivity_rows),
        "diagnostics": tuple(diagnostics),
    }


def _row(
    trace: str,
    organization: str,
    load: float,
    service_profile: str,
    tie_order: str,
    policy: str,
    result: TemporalAllocationResult,
) -> dict[str, object]:
    completed = [task for task in result.decisions if task.completion_time <= result.arrival_horizon]
    completed_effectiveness = fsum(task.effectiveness for task in completed)
    j_h = completed_effectiveness / len(result.decisions)
    completed_fraction = len(completed) / len(result.decisions)
    if not (
        -1e-12 <= j_h <= completed_fraction + 1e-12
        and j_h <= result.mean_effectiveness + 1e-12
    ):
        raise AssertionError("J_H must be bounded by completion fraction and assigned effectiveness")
    if not isclose(j_h, result.j_h, rel_tol=1e-12, abs_tol=1e-12):
        raise AssertionError("J_H from decisions disagrees with the model summary")
    completed_responses = [task.response_time for task in completed]
    completed_waits = [task.waiting_time for task in completed]
    return {
        "trace": trace,
        "organization": organization,
        "offered_load": load,
        "service_profile": service_profile,
        "tie_order": tie_order,
        "policy": policy,
        "tasks": len(result.decisions),
        "completed_tasks": len(completed),
        "pending_tasks_count": result.pending_task_count,
        "completed_fraction": completed_fraction,
        "effectiveness_mean": result.mean_effectiveness,
        "effectiveness_total": result.total_effectiveness,
        "completed_effectiveness_total": completed_effectiveness,
        "j_h": j_h,
        "completed_effectiveness_mean": (
            completed_effectiveness / len(completed) if completed else None
        ),
        "waiting_mean": result.mean_waiting_time,
        "waiting_p95": result.p95_waiting_time,
        "response_mean": result.mean_response_time,
        "response_p95": result.p95_response_time,
        "completed_response_mean": _mean_or_none(completed_responses),
        "completed_response_p95": _nearest_rank(completed_responses),
        "completed_waiting_mean": _mean_or_none(completed_waits),
        "completed_waiting_p95": _nearest_rank(completed_waits),
        "pending_tasks": result.pending_task_count,
        "pending_tasks_by_agent": result.pending_task_count_by_agent,
        "pending_work": result.pending_work_at_horizon,
        "pending_work_by_agent": result.pending_work_at_horizon_by_agent,
        "utilization": result.utilization_by_agent,
        "assigned": result.assigned_count_by_agent,
        "effectiveness_by_agent": result.effectiveness_by_agent,
        "makespan": result.makespan,
    }


def _mean_or_none(values: list[float]) -> float | None:
    return fsum(values) / len(values) if values else None


def _nearest_rank(values: list[float]) -> float | None:
    return sorted(values)[ceil(0.95 * len(values)) - 1] if values else None


def _fmt(value: float) -> str:
    return f"{value:.5f}"


def format_report(result: dict[str, object]) -> str:
    source: SourceDemand = result["source"]
    rows = result["primary"]
    lines = [
        "## Local SOCTRA demand replay (aggregate outputs only)",
        "",
        f"Source records: {source.row_count}; unique alert IDs: {source.unique_alert_ids}; ",
        f"project classes including any unclassified label: {source.project_class_count}.",
        f"Exact-timestamp ties: {source.tied_timestamp_groups} groups / {source.tied_timestamp_rows} rows; ",
        f"largest group {source.max_tie_size}. No source labels or row data are emitted.",
        "",
        "Observed demand summaries (alerts are arrival proxies; both comparison windows span 12 complete months, and only the first is a calendar year):",
        "| Window | Records | Active project classes | Top project share | Top five share | Daily mean / CV / peak |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, summary in source.demand_summaries.items():
        lines.append(
            f"| {name} | {summary['rows']} | {summary['active_project_classes']} "
            f"| {summary['top1_share']:.3f} | {summary['top5_share']:.3f} "
            f"| {summary['daily_mean']:.1f} / {summary['daily_cv']:.3f} / {summary['daily_peak']} |"
        )
    if source.early_late_project_mix_tv is not None:
        lines.append(f"\nEarly-to-late project-mix total-variation distance: {source.early_late_project_mix_tv:.3f} (0 means identical aggregate shares; 1 means disjoint class support).")
    lines += [
        "",
        "Primary results: full observed coverage, uniform hypothetical service, class-ascending tie sensitivity.",
        "Offered load is fixed at 0.50 / 0.90 / 1.20 by service-time scaling; not realized utilization.",
        "Metrics are reported as P0/P1/P2 triples; time units are fractions of the normalized scenario horizon.",
        "",
        "| Organization | ρ | Effect total / mean P0 · P1 · P2 | Wait mean / P95 P0 · P1 · P2 | Response mean / P95 P0 · P1 · P2 | Pending tasks / work P0 · P1 · P2 | Makespan P0 · P1 · P2 |",
        "|---|---:|---|---|---|---|---|",
    ]
    primary_lookup = {(row["organization"], row["offered_load"], row["policy"]): row for row in rows}
    for profile in ORGANIZATIONS:
        for load in OFFERED_LOADS:
            triplet = [primary_lookup[(profile, load, policy)] for policy, _ in POLICY_RUNNERS]
            effect = " · ".join(f"{_fmt(row['effectiveness_total'])} / {_fmt(row['effectiveness_mean'])}" for row in triplet)
            waiting = " · ".join(f"{_fmt(row['waiting_mean'])} / {_fmt(row['waiting_p95'])}" for row in triplet)
            response = " · ".join(f"{_fmt(row['response_mean'])} / {_fmt(row['response_p95'])}" for row in triplet)
            backlog = " · ".join(f"{row['pending_tasks']} / {_fmt(row['pending_work'])}" for row in triplet)
            makespan = " · ".join(_fmt(row["makespan"]) for row in triplet)
            lines.append(
                f"| {profile} | {load:.2f} | {effect} | {waiting} | {response} | {backlog} | {makespan} |"
            )
    lines += [
        "",
        "### Offered-load sensitivity by policy",
        "Each row is one deterministic cell. Utilization vectors use agent order; pending is task count / remaining service work at H.",
        "| Organization | Policy | ρ | Mean effectiveness | Response mean / P95 | Pending tasks / work | Utilization by agent |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for profile in ORGANIZATIONS:
        for load in OFFERED_LOADS:
            for policy, _ in POLICY_RUNNERS:
                row = primary_lookup[(profile, load, policy)]
                utilization = "(" + ", ".join(_fmt(value) for value in row["utilization"]) + ")"
                lines.append(
                    f"| {profile} | {policy} | {load:.2f} | {_fmt(row['effectiveness_mean'])} "
                    f"| {_fmt(row['response_mean'])} / {_fmt(row['response_p95'])} "
                    f"| {row['pending_tasks']} / {_fmt(row['pending_work'])} | {utilization} |"
                )
    lines += [
        "",
        "### Agent allocation and horizon backlog at ρ=0.90",
        "Agent vectors use model index order. Assignment fractions divide by all received alert proxies; utilization divides busy time inside [0,H] by H. Pending work is residual service plus queued service at H, in normalized time units.",
        "| Organization | Policy | Mean effect | Response mean / P95 | Assignments by agent | Assignment fractions | Utilization by agent | Pending tasks by agent | Pending work by agent | Contribution by agent |",
        "|---|---|---:|---:|---|---|---|---|---|---|",
    ]
    for profile in ORGANIZATIONS:
        for policy, _ in POLICY_RUNNERS:
            row = primary_lookup[(profile, 0.90, policy)]
            total_tasks = row["tasks"]
            assigned = "(" + ", ".join(str(value) for value in row["assigned"]) + ")"
            fractions = "(" + ", ".join(_fmt(value / total_tasks) for value in row["assigned"]) + ")"
            utilization = "(" + ", ".join(_fmt(value) for value in row["utilization"]) + ")"
            pending_tasks = "(" + ", ".join(str(value) for value in row["pending_tasks_by_agent"]) + ")"
            pending_work = "(" + ", ".join(_fmt(value) for value in row["pending_work_by_agent"]) + ")"
            contribution = "(" + ", ".join(_fmt(value) for value in row["effectiveness_by_agent"]) + ")"
            lines.append(
                f"| {profile} | {policy} | {_fmt(row['effectiveness_mean'])} "
                f"| {_fmt(row['response_mean'])} / {_fmt(row['response_p95'])} "
                f"| {assigned} | {fractions} | {utilization} | {pending_tasks} "
                f"| {pending_work} | {contribution} |"
            )
    lines += [
        "",
        "### Demand-window comparison at offered load 0.90, uniform service",
        "| Window | Organization | Policy | Tasks | Mean effectiveness | Response mean / P95 | Pending tasks |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in result["historical_windows"]:
        lines.append(
            f"| {row['trace']} | {row['organization']} | {row['policy']} | {row['tasks']} "
            f"| {_fmt(row['effectiveness_mean'])} | {_fmt(row['response_mean'])} / {_fmt(row['response_p95'])} "
            f"| {row['pending_tasks']} |"
        )
    service_rows = result["service_sensitivity"]
    uniform_lookup = {
        (row["organization"], row["offered_load"], row["policy"]): row
        for row in rows
    }
    lines += [
        "",
        "### Service-time sensitivity (class-dependent / uniform)",
        "| Organization | Load | Policy | Δ mean effectiveness | Δ response mean | Δ response P95 |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for row in service_rows:
        baseline = uniform_lookup[(row["organization"], row["offered_load"], row["policy"])]
        lines.append(
            f"| {row['organization']} | {row['offered_load']:.2f} | {row['policy']} "
            f"| {_fmt(row['effectiveness_mean'] - baseline['effectiveness_mean'])} "
            f"| {_fmt(row['response_mean'] - baseline['response_mean'])} "
            f"| {_fmt(row['response_p95'] - baseline['response_p95'])} |"
        )
    tie_rows = result["tie_sensitivity"]
    tie_lookup = {(row["organization"], row["policy"], row["tie_order"]): row for row in tie_rows}
    lines += [
        "",
        "### Same-timestamp tie-order sensitivity at offered load 0.90",
        "Deltas are descending class order minus ascending class order. Both conditions contain the same timestamp multiset and task-class multiset; only order inside equal-time groups differs.",
        "| Organization | Policy | Δ mean effectiveness | Δ response mean | Δ response P95 | Δ assignments by agent | Δ utilization by agent |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for profile in ORGANIZATIONS:
        for policy, _ in POLICY_RUNNERS:
            ascending = tie_lookup[(profile, policy, "class_ascending")]
            descending = tie_lookup[(profile, policy, "class_descending")]
            lines.append(
                f"| {profile} | {policy} "
                f"| {descending['effectiveness_mean'] - ascending['effectiveness_mean']:.3e} "
                f"| {descending['response_mean'] - ascending['response_mean']:.3e} "
                f"| {descending['response_p95'] - ascending['response_p95']:.3e} "
                f"| {tuple(y - x for x, y in zip(ascending['assigned'], descending['assigned']))} "
                f"| {tuple(round(y - x, 8) for x, y in zip(ascending['utilization'], descending['utilization']))} |"
            )
    align_rows = result["alignment_sensitivity"]
    lines += [
        "",
        "### Project-class / specialist alignment sensitivity at offered load 0.90",
        "For each policy and organization, report the range across four cyclic assignments of anonymous project classes to hypothetical worker profiles.",
        "| Organization | Policy | Effectiveness range | Response mean range | Response P95 range |",
        "|---|---|---:|---:|---:|",
    ]
    for profile in ORGANIZATIONS:
        for policy, _ in POLICY_RUNNERS:
            group = [row for row in align_rows if row["organization"] == profile and row["policy"] == policy]
            lines.append(
                f"| {profile} | {policy} "
                f"| {_fmt(min(row['effectiveness_mean'] for row in group))}–{_fmt(max(row['effectiveness_mean'] for row in group))} "
                f"| {_fmt(min(row['response_mean'] for row in group))}–{_fmt(max(row['response_mean'] for row in group))} "
                f"| {_fmt(min(row['response_p95'] for row in group))}–{_fmt(max(row['response_p95'] for row in group))} |"
            )
    synthetic_rows = result["synthetic_controls"]
    lines += [
        "",
        "### Synthetic balanced-demand controls at offered load 0.90",
        "Both controls keep the observed task count and horizon. One keeps recorded timestamps but replaces project mix with a cyclic balanced class sequence; the other also spaces arrivals uniformly.",
        "| Organization | Policy | Observed response mean | Same times, balanced classes | Uniform times and classes | Observed / synthetic effectiveness |",
        "|---|---|---:|---:|---:|---:|",
    ]
    primary_lookup = {(row["organization"], row["policy"]): row for row in rows if row["offered_load"] == 0.90}
    synthetic_lookup = {(row["organization"], row["policy"], row["trace"]): row for row in synthetic_rows}
    for profile in ORGANIZATIONS:
        for policy, _ in POLICY_RUNNERS:
            observed_row = primary_lookup[(profile, policy)]
            same_time = synthetic_lookup[(profile, policy, "observed_times_balanced_classes")]
            uniform = synthetic_lookup[(profile, policy, "uniform_times_balanced_classes")]
            lines.append(
                f"| {profile} | {policy} | {_fmt(observed_row['response_mean'])} "
                f"| {_fmt(same_time['response_mean'])} | {_fmt(uniform['response_mean'])} "
                f"| {_fmt(observed_row['effectiveness_mean'])} / {_fmt(uniform['effectiveness_mean'])} |"
            )
    lines += [
        "",
        "All organization matrices and service durations are hypothetical. An alert record is used only as a demand-arrival proxy; no result estimates analyst performance or actual service capacity.",
        "The study also reports matched early/late calendar years, class-dependent service sensitivity, ascending/descending same-timestamp ordering, and four cyclic class-to-profile alignments.",
    ]
    return "\n".join(lines)


def format_organizational_report(result: dict[str, object]) -> str:
    """Compact, deterministic report for the separately named S0-S3 study."""
    source: SourceDemand = result["source"]
    rows = result["load_sensitivity"]
    lookup = {
        (row["trace"], row["organization"], row["offered_load"], row["policy"]): row
        for row in rows
    }
    names = ("usual_28d", "peak_28d", "mix_shift_28d", "post_mix_shift_28d")
    lines = [
        "## HLS-02 organizational strategy comparison S0-S3",
        "",
        "SOCTRA is used as a qualitative source of relative arrival timing and opaque project-class sequence patterns. Every event is an alert-record proxy; selected-window counts are not interpreted as human task rates. Horizon is normalized to 1 and service times are hypothetical, scaled to offered load.",
        "",
        "Windows were selected before policy evaluation, from complete 28-day calendar windows: usual = volume nearest the median (then lower daily CV); peak = maximum daily peak/mean among windows at or above median volume; mix shift = maximum total-variation distance between first and second 14-day class shares; post mix shift = the immediately following 28 days. Ties resolve by larger volume where relevant, then earliest date.",
        "",
        f"S3 fixed parameters: specialist threshold θ={S3_PRIMARY_THRESHOLD:g} times the current task's class service duration; if specialist workload W_i(t)>θs_k, use the highest-effectiveness other currently idle agent with e_ik≥{S3_BACKUP_EFFECTIVENESS_FLOOR:.2f}; ties use lowest index. If none qualifies, use the specialist. Threshold sensitivity: {', '.join(map(str, S3_THRESHOLD_SENSITIVITY))} in addition to θ=1.",
        "",
        "All effectiveness values, team profiles and service durations are hypothetical. Classes are anonymous project labels, not competence categories. The table reports exact scenario outputs, not policy estimates for GMV-CERT.",
        "",
        "| 28-day pattern | Dates (start–end exclusive) | Alert proxies | Active classes | Daily mean / CV / peak | First-half / second-half class TV |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for name in names:
        trace = source.traces[name]
        summary = source.organizational_demand_summaries[name]
        lines.append(
            f"| {name} | {trace.start.date()}–{trace.end.date()} | {summary['rows']} | "
            f"{summary['active_project_classes']} | {summary['daily_mean']:.1f} / "
            f"{summary['daily_cv']:.3f} / {summary['daily_peak']} | {summary['first_second_mix_tv']:.3f} |"
        )
    lines += [
        "",
        "At each cell, policy values below are `mean effectiveness / mean response / P95 response / completed fraction by H`. Response uses all assigned tasks (including tasks completed after H); completed fraction is a separate horizon view. All time units are normalized hypothetical service units.",
        "",
        "| Pattern | Organization | ρ offered | S0 | S1 | S2 | S3 |",
        "|---|---|---:|---|---|---|---|",
    ]
    for window in names:
        for profile in ORGANIZATIONS:
            for load in OFFERED_LOADS:
                cells = []
                for policy in ORGANIZATIONAL_POLICY_NAMES:
                    row = lookup[(window, profile, load, policy)]
                    cells.append(
                        f"{row['effectiveness_mean']:.3f} / {row['response_mean']:.3f} / "
                        f"{row['response_p95']:.3f} / {row['completed_fraction']:.3f}"
                    )
                lines.append(
                    f"| {window} | {profile} | {load:.2f} | " + " | ".join(cells) + " |"
                )
    lines += [
        "",
        "### Horizon completion and resource detail at ρ=0.90",
        "Received = completed by H + pending at H. Completed-task quality and time below use completed tasks only; the preceding table's quality and response use all assigned tasks. Assignment counts and utilization vectors follow agent-index order.",
        "",
        "| Pattern | Organization | Policy | Received / completed / pending | Completed effectiveness total / mean | Completed response mean / P95 | Pending work | Assigned by agent | Utilization by agent |",
        "|---|---|---|---:|---:|---:|---:|---|---|",
    ]
    for window in names:
        for profile in ORGANIZATIONS:
            for policy in ORGANIZATIONAL_POLICY_NAMES:
                row = lookup[(window, profile, 0.90, policy)]
                completed_mean = row["completed_effectiveness_mean"]
                completed_response = row["completed_response_mean"]
                completed_p95 = row["completed_response_p95"]
                assigned = "(" + ", ".join(map(str, row["assigned"])) + ")"
                utilization = "(" + ", ".join(f"{value:.3f}" for value in row["utilization"]) + ")"
                lines.append(
                    f"| {window} | {profile} | {policy} | {row['tasks']} / {row['completed_tasks']} / {row['pending_tasks_count']} "
                    f"| {row['completed_effectiveness_total']:.2f} / "
                    f"{'NA' if completed_mean is None else f'{completed_mean:.3f}'} "
                    f"| {'NA' if completed_response is None else f'{completed_response:.3f}'} / "
                    f"{'NA' if completed_p95 is None else f'{completed_p95:.3f}'} "
                    f"| {row['pending_work']:.3f} | {assigned} | {utilization} |"
                )
    threshold_lookup: dict[tuple[object, ...], dict[str, object]] = {}
    for row in result["threshold_sensitivity"]:
        threshold_lookup[(row["trace"], row["organization"], row["threshold_multiplier"])] = row
    lines += [
        "",
        "### S3 threshold sensitivity at ρ=0.90",
        "Values are mean effectiveness / mean response / P95 response / completed fraction. This is a fixed sensitivity set, not post-result tuning.",
        "",
        "| Pattern | Organization | θ=0.5 | θ=1.0 | θ=2.0 |",
        "|---|---|---|---|---|",
    ]
    for window in names:
        for profile in ORGANIZATIONS:
            cells = []
            for threshold in (0.5, 1.0, 2.0):
                if threshold == S3_PRIMARY_THRESHOLD:
                    row = lookup[(window, profile, 0.90, "S3")]
                else:
                    row = threshold_lookup[(window, profile, threshold)]
                cells.append(
                    f"{row['effectiveness_mean']:.3f} / {row['response_mean']:.3f} / "
                    f"{row['response_p95']:.3f} / {row['completed_fraction']:.3f}"
                )
            lines.append(f"| {window} | {profile} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "Interpretation boundary: S0-S3 are constructed organizational rules. Demand-window choice is outcome-blind and descriptive. Since each window is normalized and service is scaled to ρ, the evaluation preserves within-window ordering and relative timing but does not estimate alert rates, analyst capacity, actual SOC response, or effects of AI. No statistical inference is applied.",
    ]
    return "\n".join(lines)


def format_adaptive_organizational_report(result: dict[str, object]) -> str:
    """Compact primary results, S4 diagnostics and bounded service sensitivity."""
    rows = result["primary_rows"]
    lookup = {(r["trace"], r["organization"], r["offered_load"], r["policy"]): r for r in rows}
    names = ("usual_28d", "peak_28d", "mix_shift_28d", "post_mix_shift_28d")
    lines = [
        "## HLS-02 organizational comparison S0-S4",
        "",
        "Demand windows are selected outcome-blind from SOCTRA alert records, used only as qualitative relative time and opaque class-pattern inputs. Team profiles, service times, and load scaling are hypothetical; this is not an estimate of GMV-CERT performance.",
        "",
        "S4 observes predecision work W_i=max(0, queue_tail_i-t), C=sum(W_i)/(N*s_ref), s_ref=arithmetic mean of fixed class service times, and I=(N*max(W_i)/sum(W_i)-1)/(N-1), with I=0 at zero work. It starts SPECIALIZATION (S1), moves to BALANCED (S2) at C≥0.25 or I≥0.35, to LOAD_DISTRIBUTION (S0) at C≥1; load exits below C=0.75 to BALANCED, and BALANCED exits to specialization only below C=0.15 and I=0.25. Parameters were fixed before replay.",
        "",
        "Primary cells average the four windows within each organization/load combination and report J_H / mean assigned effectiveness / completed fraction / all-task mean response / all-task P95 response. J_H is computed directly from per-task assigned effectiveness for tasks completed by H, divided by all tasks received. All-task wait/response and makespan include the post-H queue drain; completed-only response is retained separately by the runner.",
        "",
        "### Primary comparison: 240 matched evaluations",
        "Each policy uses the same ordered arrivals, effectiveness matrix, service vector and H within a cell. Values are deterministic cell averages across four demand windows, not independent statistical replicates.",
        "",
        "| Organization | ρ | S0 J_H / ē / f_H / R̄ / R95 | S1 | S2 | S3 | S4 |",
        "|---|---:|---|---|---|---|---|",
    ]
    for profile in ORGANIZATIONS:
        for load in OFFERED_LOADS:
            cells = []
            for policy in ADAPTIVE_POLICY_NAMES:
                selected = [lookup[(window, profile, load, policy)] for window in names]
                means = [fmean(row[key] for row in selected) for key in (
                    "j_h", "effectiveness_mean", "completed_fraction", "response_mean", "response_p95"
                )]
                cells.append(" / ".join(f"{value:.4f}" for value in means))
            lines.append(f"| {profile} | {load:.2f} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "At the primary load ρ=.90, this window/profile view preserves each of the 16 demand-pattern cells. Values are J_H for S0/S1/S2/S3/S4; ties are shown explicitly.",
        "",
        "| Window | Organization | S0 / S1 / S2 / S3 / S4 J_H | Maximum J_H policy |",
        "|---|---|---|---|",
    ]
    for window in names:
        for profile in ORGANIZATIONS:
            cell = [lookup[(window, profile, 0.90, policy)] for policy in ADAPTIVE_POLICY_NAMES]
            best = max(row["j_h"] for row in cell)
            winners = ", ".join(
                policy for policy, row in zip(ADAPTIVE_POLICY_NAMES, cell)
                if isclose(row["j_h"], best, rel_tol=1e-12, abs_tol=1e-12)
            )
            values = " / ".join(f"{row['j_h']:.4f}" for row in cell)
            lines.append(f"| {window} | {profile} | {values} | {winners} |")
    comparisons = []
    for left, right in (("S2", "S0"), ("S2", "S1"), ("S2", "S3"), ("S4", "S2")):
        differences = [
            lookup[(window, profile, load, left)]["j_h"]
            - lookup[(window, profile, load, right)]["j_h"]
            for window in names for profile in ORGANIZATIONS for load in OFFERED_LOADS
        ]
        comparisons.append(f"{left}−{right}: mean ΔJ_H={fmean(differences):+.5f}, range [{min(differences):+.5f},{max(differences):+.5f}]")
    lines += ["", "Paired J_H contrasts over the 48 within-window organization/load cells: " + "; ".join(comparisons) + "."]
    lines += [
        "",
        "At ρ=0.90, S4 controller diagnostics (state fractions are also the S1/S2/S0 decision fractions in corresponding order). No alert-level trace is retained.",
        "",
        "| Organization | Mean S1 fraction | Mean S2 fraction | Mean S0 fraction | Mean switches per window |",
        "|---|---:|---:|---:|---:|",
    ]
    diagnostics = [item for item in result["diagnostics"] if item["offered_load"] == 0.90]
    for profile in ORGANIZATIONS:
        items = [item["diagnostics"] for item in diagnostics if item["organization"] == profile]
        decisions = [dict(diag.strategy_decision_counts) for diag in items]
        totals = {name: sum(counts.get(name, 0) for counts in decisions) for name in ("S1", "S2", "S0")}
        total = sum(totals.values())
        switch_mean = fmean(diag.transition_count for diag in items)
        lines.append(
            f"| {profile} | {totals['S1']/total:.3f} | {totals['S2']/total:.3f} | "
            f"{totals['S0']/total:.3f} | {switch_mean:.1f} |"
        )
    service_rows = result["service_sensitivity_rows"]
    service_lookup = {(r["trace"], r["organization"], r["policy"]): r for r in service_rows}
    lines += [
        "",
        "### Minimal class-dependent service-time sensitivity (80 paired evaluations; ρ=.90)",
        "Class durations differ by class but are identical across agents. Their total offered service work is normalized to the same ρ. This tests dependence on equal class durations only; it does not model measured SOC processing times.",
        "",
        "| Organization | Policy | Uniform J_H / response / P95 | Class-dependent J_H / response / P95 | ΔJ_H | Δresponse |",
        "|---|---|---|---|---:|---:|",
    ]
    for profile in ORGANIZATIONS:
        for policy in ADAPTIVE_POLICY_NAMES:
            uniform = [lookup[(window, profile, 0.90, policy)] for window in names]
            varied = [service_lookup[(window, profile, policy)] for window in names]
            uniform_means = [fmean(r[key] for r in uniform) for key in ("j_h", "response_mean", "response_p95")]
            varied_means = [fmean(r[key] for r in varied) for key in ("j_h", "response_mean", "response_p95")]
            lines.append(
                f"| {profile} | {policy} | "
                f"{uniform_means[0]:.4f} / {uniform_means[1]:.5f} / {uniform_means[2]:.5f} | "
                f"{varied_means[0]:.4f} / {varied_means[1]:.5f} / {varied_means[2]:.5f} | "
                f"{varied_means[0]-uniform_means[0]:+.4f} | {varied_means[1]-uniform_means[1]:+.5f} |"
            )
    lines += [
        "",
        "Interpretation boundary: these are deterministic outputs under normalized hypothetical scenarios. J_H is modeled expected quality completed by H per received task, not observed success. The alert records provide relative temporal/class patterns only; no inference about GMV-CERT performance, analyst competence, service time or staffing follows. No significance tests are applied.",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--soctra-csv", required=True, help="path to an authorized local SOCTRA snapshot")
    parser.add_argument(
        "--organizational-strategies",
        action="store_true",
        help="run the separately identified S0-S3 organization comparison",
    )
    parser.add_argument(
        "--adaptive-organizational-strategies",
        action="store_true",
        help="run the separately identified S0-S4 adaptive organization comparison",
    )
    args = parser.parse_args()
    if args.organizational_strategies and args.adaptive_organizational_strategies:
        parser.error("choose one organizational comparison mode")
    if args.adaptive_organizational_strategies:
        result = run_adaptive_organizational_comparison(args.soctra_csv)
        print(format_adaptive_organizational_report(result))
    elif args.organizational_strategies:
        result = run_organizational_strategy_comparison(args.soctra_csv)
        print(format_organizational_report(result))
    else:
        result = run_soctra_demand_experiment(args.soctra_csv)
        print(format_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
