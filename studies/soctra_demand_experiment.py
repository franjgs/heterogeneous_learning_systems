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
from math import fsum, isclose
from pathlib import Path
from statistics import fmean, pstdev

from hls.temporal_allocation import (
    ArrivalTask,
    TemporalAllocationResult,
    run_effectiveness_load_temporal_policy,
    run_fixed_temporal_policy,
    run_max_effectiveness_temporal_policy,
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


def _row(
    trace: str,
    organization: str,
    load: float,
    service_profile: str,
    tie_order: str,
    policy: str,
    result: TemporalAllocationResult,
) -> dict[str, object]:
    return {
        "trace": trace,
        "organization": organization,
        "offered_load": load,
        "service_profile": service_profile,
        "tie_order": tie_order,
        "policy": policy,
        "tasks": len(result.decisions),
        "effectiveness_mean": result.mean_effectiveness,
        "effectiveness_total": result.total_effectiveness,
        "waiting_mean": result.mean_waiting_time,
        "waiting_p95": result.p95_waiting_time,
        "response_mean": result.mean_response_time,
        "response_p95": result.p95_response_time,
        "pending_tasks": result.pending_task_count,
        "pending_tasks_by_agent": result.pending_task_count_by_agent,
        "pending_work": result.pending_work_at_horizon,
        "pending_work_by_agent": result.pending_work_at_horizon_by_agent,
        "utilization": result.utilization_by_agent,
        "assigned": result.assigned_count_by_agent,
        "effectiveness_by_agent": result.effectiveness_by_agent,
        "makespan": result.makespan,
    }


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--soctra-csv", required=True, help="path to an authorized local SOCTRA snapshot")
    args = parser.parse_args()
    result = run_soctra_demand_experiment(args.soctra_csv)
    print(format_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
