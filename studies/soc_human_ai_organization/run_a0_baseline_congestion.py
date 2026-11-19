"""D1-only, paired-seed congestion characterization for the SOC model.

All workload, analyst, SLA, escalation, and quality parameters are synthetic
or hypothetical. Outputs are aggregate/local artifacts under results/.
"""
from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path
import statistics
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from hls.ia_l1_l2_simulation import generate_alerts  # noqa: E402
from hls.rq1_l1_l2 import simulate_l1_l2, stage_metrics_at  # noqa: E402
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity  # noqa: E402
from studies.soc_human_ai_organization.soc_parametric_baseline import (  # noqa: E402
    BASE_L1_ANALYSTS, BASE_L2_ANALYSTS, BASE_SERVICE_L1_H, BASE_SERVICE_L2_H,
    REFERENCE, build_roster,
)

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config" / "a0_baseline_congestion.json"
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
HORIZON = float(CONFIG["admission_horizon_h"])
DRAIN = float(CONFIG["drain_h"])
GRID = float(CONFIG["queue_time_grid_h"])
SEED_BASE = int(CONFIG["seed_base"])
SEED_COUNT = int(CONFIG["seed_count"])


def _csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)]


def _queue_profile(arrival_times: list[float], start_times: list[float], cutoff: float) -> dict:
    """Waiting-queue process; arrivals are added before same-time starts dispatch."""
    arrivals: dict[float, int] = {}
    starts: dict[float, int] = {}
    for time in arrival_times:
        if 0 <= time <= cutoff:
            arrivals[time] = arrivals.get(time, 0) + 1
    for time in start_times:
        if 0 <= time <= cutoff:
            starts[time] = starts.get(time, 0) + 1
    times = sorted({0.0, cutoff, *arrivals, *starts})
    queue = 0
    peak = 0
    area = 0.0
    last = 0.0
    at_cutoff = 0
    for time in times:
        area += queue * (time - last)
        queue += arrivals.get(time, 0)
        peak = max(peak, queue)  # transient queue before immediate dispatch
        queue -= starts.get(time, 0)
        if queue < 0:
            raise AssertionError("queue conservation failed: starts exceed arrivals")
        peak = max(peak, queue)
        if time == cutoff:
            at_cutoff = queue
        last = time
    return {"queue_peak": peak, "queue_mean_time_weighted": area / cutoff if cutoff else 0.0,
            "queue_waiting_at_cutoff": at_cutoff}


def _all_busy_duration(eligible_ids: list[str], busy: dict[str, list[tuple[float, float]]],
                       start: float, end: float) -> float:
    if not eligible_ids or end <= start:
        return 0.0
    points = {start, end}
    for analyst_id in eligible_ids:
        for left, right in busy.get(analyst_id, []):
            if right > start and left < end:
                points.add(max(start, left))
                points.add(min(end, right))
    ordered = sorted(points)
    duration = 0.0
    for left, right in zip(ordered, ordered[1:]):
        mid = (left + right) / 2
        if all(any(a <= mid < b for a, b in busy.get(analyst_id, []))
               for analyst_id in eligible_ids):
            duration += right - left
    return duration


def _roster(indices: list[int]):
    all_l1, l2, all_l1_service, l2_service = build_roster(
        BASE_L1_ANALYSTS, BASE_L2_ANALYSTS, 2.5,
    )
    l1 = tuple(all_l1[ix] for ix in indices)
    l1_service = {a.analyst_id: all_l1_service[a.analyst_id] for a in l1}
    return l1, l2, l1_service, l2_service


def _run_episode(series: str, setting: str, load_value: float, arrival_rate: float,
                 indices: list[int], seed: int) -> tuple[dict, list[dict], list[dict]]:
    l1, l2, l1_service, l2_service = _roster(indices)
    capacity = effective_capacity(l1, l1_service, REFERENCE.project_probabilities)["max_common_arrivals_per_h"]
    scenario = REFERENCE.scenario_config(arrival_rate_per_h=arrival_rate)
    scenario = type(scenario)(**{**scenario.__dict__, "horizon": HORIZON})
    generated = generate_alerts(scenario, seed)
    routed = tuple(row.routed for row in generated)
    result = simulate_l1_l2(
        routed, l1, l2, BASE_SERVICE_L1_H, BASE_SERVICE_L2_H,
        policy="D1", admission_horizon=HORIZON, drain_period=DRAIN,
        coordination_latency=0.0,
        decision_mode="hypothetical_recommendation_acceptance",
        random_seed=seed, l1_service_by_analyst_class=l1_service,
        l2_service_by_analyst_class=l2_service,
    )
    admitted = [row for row in generated if row.routed.alert.arrival < HORIZON]
    alert_by_id = {row.routed.alert.alert_id: row for row in admitted}
    l1_jobs = {job.alert_id: job for job in result.l1_simulation.assignments}
    l2_jobs = {job.alert_id: job for job in result.l2_simulation.assignments}
    routes = {row.alert_id: row.scenario_routing_decision for row in result.escalation_records}
    l1_arrivals = [row.routed.alert.arrival for row in admitted]
    l1_starts = [job.start for job in l1_jobs.values()]
    l2_arrivals = [l1_jobs[aid].completion for aid, route in routes.items()
                   if route and aid in l1_jobs and l1_jobs[aid].completion < HORIZON + DRAIN]
    l2_starts = [job.start for job in l2_jobs.values()]
    l1_busy: dict[str, list[tuple[float, float]]] = {a.analyst_id: [] for a in l1}
    for job in l1_jobs.values():
        l1_busy[job.analyst_id].append((job.start, job.completion))

    wait_l1, wait_l2, wait_total, response, quality_all = [], [], [], [], []
    expired_before_l1 = 0
    urgent_blocked = urgent_high = 0
    urgent_blocked_wait, urgent_total_wait = 0.0, 0.0
    for row in admitted:
        alert = row.routed.alert
        first = l1_jobs.get(alert.alert_id)
        first_start = min(first.start, HORIZON + DRAIN) if first else HORIZON + DRAIN
        this_l1_wait = max(0.0, first_start - alert.arrival)
        this_l2_wait = 0.0
        wait_l1.append(this_l1_wait)
        if first is None or first.start > alert.deadline:
            expired_before_l1 += 1
        second = l2_jobs.get(alert.alert_id) if routes.get(alert.alert_id, False) else None
        if routes.get(alert.alert_id, False) and first is not None and first.completion < HORIZON + DRAIN:
            second_start = min(second.start, HORIZON + DRAIN) if second else HORIZON + DRAIN
            this_l2_wait = max(0.0, second_start - first.completion)
            wait_l2.append(this_l2_wait)
        wait_total.append(this_l1_wait + this_l2_wait)
        final = second if routes.get(alert.alert_id, False) else first
        if final is not None and final.completion <= HORIZON + DRAIN:
            response.append(final.completion - alert.arrival)
            quality_all.append(final.competence * (1 - 0.35 * row.difficulty))

        if row.severity == "high":
            urgent_high += 1
            eligible = [a.analyst_id for a in l1 if alert.task_class in a.eligible_classes]
            busy_at_arrival = [aid for aid in eligible if any(
                start < alert.arrival < end for start, end in l1_busy.get(aid, [])
            )]
            if eligible and len(busy_at_arrival) == len(eligible):
                urgent_blocked += 1
            wait_end = first.start if first else HORIZON + DRAIN
            duration = max(0.0, min(wait_end, HORIZON + DRAIN) - alert.arrival)
            urgent_total_wait += duration
            urgent_blocked_wait += _all_busy_duration(
                eligible, l1_busy, alert.arrival, min(wait_end, HORIZON + DRAIN),
            )

    queue_l1_H = _queue_profile(l1_arrivals, l1_starts, HORIZON)
    queue_l1_D = _queue_profile(l1_arrivals, l1_starts, HORIZON + DRAIN)
    queue_l2_H = _queue_profile(l2_arrivals, l2_starts, HORIZON)
    queue_l2_D = _queue_profile(l2_arrivals, l2_starts, HORIZON + DRAIN)
    l1_util_H = [v for _, v in stage_metrics_at(result.l1_simulation, HORIZON)]
    l2_util_H = [v for _, v in stage_metrics_at(result.l2_simulation, HORIZON)]
    l1_util_D = [v for _, v in stage_metrics_at(result.l1_simulation, HORIZON + DRAIN)]
    l2_util_D = [v for _, v in stage_metrics_at(result.l2_simulation, HORIZON + DRAIN)]
    outcome = result.after_drain
    n_admitted = outcome.admitted
    completed = n_admitted - outcome.pending
    if completed + outcome.pending != n_admitted:
        raise AssertionError("end-to-end alert conservation failed")
    terminal_sla_by_severity = {}
    for severity in ("low", "medium", "high"):
        group = [r for r in admitted if r.severity == severity]
        on_time = 0
        for row in group:
            aid = row.routed.alert.alert_id
            final = l2_jobs.get(aid) if routes.get(aid, False) else l1_jobs.get(aid)
            on_time += int(final is not None and final.completion <= HORIZON + DRAIN
                            and final.completion <= row.routed.alert.deadline)
        terminal_sla_by_severity[severity] = on_time / len(group) if group else 0.0
    stratified = []
    for group_type, levels, predicate in (
        ("priority", ("low", "medium", "high"), lambda row, level: row.severity == level),
        ("class", tuple(sorted({row.routed.alert.task_class for row in admitted})),
         lambda row, level: row.routed.alert.task_class == level),
    ):
        for level in levels:
            group = [row for row in admitted if predicate(row, level)]
            group_done = group_on_time = group_late = group_pending = 0
            group_quality = []
            for row in group:
                aid = row.routed.alert.alert_id
                final = l2_jobs.get(aid) if routes.get(aid, False) else l1_jobs.get(aid)
                if final is None or final.completion > HORIZON + DRAIN:
                    group_pending += 1
                    continue
                group_done += 1
                if final.completion <= row.routed.alert.deadline:
                    group_on_time += 1
                else:
                    group_late += 1
                group_quality.append(final.competence * (1 - .35 * row.difficulty))
            stratified.append({
                "series": series, "setting": setting, "load_value": load_value,
                "arrival_rate_per_h": arrival_rate, "n_l1": len(l1), "seed": seed,
                "group_type": group_type, "group": level, "admitted": len(group),
                "completed_terminal": group_done, "completed_late": group_late,
                "pending_censored_terminal": group_pending,
                "sla_h_fraction_admitted": (
                    sum(1 for row in group
                        if (lambda job: job is not None and job.completion <= HORIZON
                            and job.completion <= row.routed.alert.deadline)(
                                l2_jobs.get(row.routed.alert.alert_id)
                                if routes.get(row.routed.alert.alert_id, False)
                                else l1_jobs.get(row.routed.alert.alert_id))) / len(group) if group else 0.0
                ),
                "sla_terminal_fraction_admitted": group_on_time / len(group) if group else 0.0,
                "quality_expected_completed": statistics.mean(group_quality) if group_quality else None,
            })
    metrics = {
        "series": series, "setting": setting, "load_value": load_value,
        "arrival_rate_per_h": arrival_rate, "l1_capacity_fluid_per_h": capacity,
        "rho_l1": arrival_rate / capacity, "n_l1": len(l1), "n_l2": len(l2),
        "seed": seed, "generated": len(generated), "admitted": n_admitted,
        "completed_terminal": completed, "completed_within_sla_h": result.at_horizon.completed_within_sla,
        "completed_h_total": n_admitted - result.at_horizon.pending,
        "completed_within_sla_terminal": outcome.completed_within_sla,
        "sla_h": result.at_horizon.fraction_within_sla,
        "sla_terminal": outcome.fraction_within_sla,
        "pending_h_total": result.at_horizon.pending,
        "pending_terminal_total": outcome.pending,
        "pending_l1_h": result.at_horizon.l1_backlog,
        "pending_l2_h": result.at_horizon.l2_backlog,
        "pending_l1_terminal": outcome.l1_backlog,
        "pending_l2_terminal": outcome.l2_backlog,
        "queue_l1_peak_h": queue_l1_H["queue_peak"],
        "queue_l1_mean_h": queue_l1_H["queue_mean_time_weighted"],
        "queue_l1_at_h": queue_l1_H["queue_waiting_at_cutoff"],
        "queue_l1_peak_terminal": queue_l1_D["queue_peak"],
        "queue_l1_mean_terminal": queue_l1_D["queue_mean_time_weighted"],
        "queue_l1_at_terminal": queue_l1_D["queue_waiting_at_cutoff"],
        "queue_l2_peak_h": queue_l2_H["queue_peak"],
        "queue_l2_mean_h": queue_l2_H["queue_mean_time_weighted"],
        "queue_l2_at_h": queue_l2_H["queue_waiting_at_cutoff"],
        "queue_l2_peak_terminal": queue_l2_D["queue_peak"],
        "queue_l2_mean_terminal": queue_l2_D["queue_mean_time_weighted"],
        "queue_l2_at_terminal": queue_l2_D["queue_waiting_at_cutoff"],
        "util_l1_mean_h": statistics.mean(l1_util_H) if l1_util_H else 0.0,
        "util_l1_max_h": max(l1_util_H, default=0.0),
        "util_l2_mean_h": statistics.mean(l2_util_H) if l2_util_H else 0.0,
        "util_l2_max_h": max(l2_util_H, default=0.0),
        "util_l1_mean_terminal": statistics.mean(l1_util_D) if l1_util_D else 0.0,
        "util_l2_mean_terminal": statistics.mean(l2_util_D) if l2_util_D else 0.0,
        "mean_wait_l1_h": statistics.mean(wait_l1) if wait_l1 else 0.0,
        "p95_wait_l1_h": _quantile(wait_l1, .95),
        "mean_wait_l2_h": statistics.mean(wait_l2) if wait_l2 else 0.0,
        "p95_wait_l2_h": _quantile(wait_l2, .95),
        "mean_wait_total_h": statistics.mean(wait_total) if wait_total else 0.0,
        "mean_response_completed_h": statistics.mean(response) if response else None,
        "p95_response_completed_h": _quantile(response, .95),
        "quality_expected_completed": statistics.mean(quality_all) if quality_all else None,
        "quality_expected_per_admitted": sum(quality_all) / n_admitted if n_admitted else 0.0,
        "expired_before_l1_service_n": expired_before_l1,
        "expired_before_l1_service_fraction": expired_before_l1 / n_admitted if n_admitted else 0.0,
        "high_alerts": urgent_high, "high_blocked_at_arrival_n": urgent_blocked,
        "high_blocked_at_arrival_fraction": urgent_blocked / urgent_high if urgent_high else 0.0,
        "high_wait_h": urgent_total_wait,
        "high_wait_all_eligible_busy_h": urgent_blocked_wait,
        "high_wait_share_all_eligible_busy": urgent_blocked_wait / urgent_total_wait if urgent_total_wait else 0.0,
        "discarded_n": 0, "discarded_policy": "not modeled; infinite pending queues",
        "sla_high_terminal": terminal_sla_by_severity["high"],
        "sla_medium_terminal": terminal_sla_by_severity["medium"],
        "sla_low_terminal": terminal_sla_by_severity["low"],
        "censored_after_drain_n": outcome.pending,
        "modeled_quality_label": "competence × (1 − 0.35 × synthetic difficulty); expected proxy only",
    }
    traj = []
    grid_n = int(round((HORIZON + DRAIN) / GRID))
    for ix in range(grid_n + 1):
        t = round(ix * GRID, 9)
        l1q = sum(a <= t for a in l1_arrivals) - sum(s <= t for s in l1_starts)
        l2q = sum(a <= t for a in l2_arrivals) - sum(s <= t for s in l2_starts)
        traj.append({"series": series, "setting": setting, "load_value": load_value,
                     "arrival_rate_per_h": arrival_rate, "n_l1": len(l1), "time_h": t,
                     "queue_l1_waiting": l1q, "queue_l2_waiting": l2q,
                     "pending_end_to_end_horizon_only": t == HORIZON})
    return metrics, traj, stratified


def _settings():
    base_capacity = float(CONFIG["base_l1_capacity_per_hour"])
    series = CONFIG["series"]
    output = []
    for rho in series["A_arrival_load"]["arrival_capacity_multipliers"]:
        output.append(("A_arrival_load", f"rho{rho:.2f}", float(rho),
                       base_capacity * float(rho), series["A_arrival_load"]["active_l1_indices"]))
    for row in series["B_staffing"]["staffing_levels"]:
        output.append(("B_staffing", f"nL1_{row['n_l1']}", float(row["n_l1"]),
                       float(series["B_staffing"]["arrival_rate_per_hour"]), row["active_l1_indices"]))
    for row in series["C_high_load_reduced_staffing"]["staffing_levels"]:
        output.append(("C_high_load_reduced_staffing", f"nL1_{row['n_l1']}", float(row["n_l1"]),
                       float(series["C_high_load_reduced_staffing"]["arrival_rate_per_hour"]),
                       row["active_l1_indices"]))
    return output


def _summaries(rows: list[dict]) -> list[dict]:
    numeric = [key for key, value in rows[0].items()
               if isinstance(value, (int, float)) and key not in {"seed", "load_value", "n_l1", "n_l2"}]
    result = []
    groups = {}
    for row in rows:
        groups.setdefault((row["series"], row["setting"]), []).append(row)
    from scipy.stats import t as student_t
    for (series, setting), group in groups.items():
        for metric in numeric:
            values = [float(row[metric]) for row in group if row[metric] is not None]
            if not values:
                continue
            mean = statistics.mean(values)
            sd = statistics.stdev(values) if len(values) > 1 else 0.0
            half = float(student_t.ppf(.975, len(values)-1)) * sd / math.sqrt(len(values)) if len(values) > 1 else 0.0
            lower, upper = mean - half, mean + half
            if any(token in metric for token in ("sla", "fraction", "quality", "util_")):
                lower, upper = max(0.0, lower), min(1.0, upper)
            elif any(token in metric for token in ("wait", "queue", "pending", "completed", "generated", "expired", "blocked")):
                lower = max(0.0, lower)
            result.append({"series": series, "setting": setting, "metric": metric,
                           "n_seeds": len(values), "mean": mean, "sd": sd,
                           "ci95_low": lower, "ci95_high": upper})
    return result


def _stratified_summaries(rows: list[dict]) -> list[dict]:
    from scipy.stats import t as student_t
    numeric = ["admitted", "completed_terminal", "completed_late",
               "pending_censored_terminal", "sla_h_fraction_admitted",
               "sla_terminal_fraction_admitted", "quality_expected_completed"]
    groups = {}
    for row in rows:
        key = (row["series"], row["setting"], row["group_type"], row["group"])
        groups.setdefault(key, []).append(row)
    result = []
    for (series, setting, group_type, group_name), group_rows in groups.items():
        for metric in numeric:
            values = [float(row[metric]) for row in group_rows if row[metric] is not None]
            if not values:
                continue
            mean = statistics.mean(values)
            sd = statistics.stdev(values) if len(values) > 1 else 0.0
            half = float(student_t.ppf(.975, len(values)-1)) * sd / math.sqrt(len(values)) if len(values) > 1 else 0.0
            lower, upper = mean - half, mean + half
            if metric.startswith("sla_") or metric.startswith("quality"):
                lower, upper = max(0.0, lower), min(1.0, upper)
            result.append({"series": series, "setting": setting, "group_type": group_type,
                           "group": group_name, "metric": metric, "n_seeds": len(values),
                           "mean": mean, "sd": sd, "ci95_low": lower, "ci95_high": upper})
    return result


def _plots(out: Path, summaries: list[dict], trajectories: list[dict]) -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(out / ".mplconfig"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def metric(series, key):
        return [r for r in summaries if r["series"] == series and r["metric"] == key]

    fig, axes = plt.subplots(2, 3, figsize=(14, 8), constrained_layout=True)
    for ax, key, title, ylabel in (
        (axes[0, 0], "util_l1_mean_h", "L1 utilization at H", "utilization"),
        (axes[0, 1], "queue_l1_peak_h", "Peak L1 waiting queue", "alerts"),
        (axes[1, 0], "p95_wait_l1_h", "95th percentile L1 wait", "hours"),
        (axes[1, 1], "sla_terminal", "Terminal SLA after drain", "fraction admitted"),
        (axes[0, 2], "pending_h_total", "Unfinished alerts at H", "alerts"),
        (axes[1, 2], "expired_before_l1_service_fraction", "Deadline passed before L1 start", "fraction admitted"),
    ):
        rows = metric("A_arrival_load", key)
        rows.sort(key=lambda r: float(r["setting"].replace("rho", "")))
        x = [float(r["setting"].replace("rho", "")) for r in rows]
        y = [r["mean"] for r in rows]
        low = [r["ci95_low"] for r in rows]
        high = [r["ci95_high"] for r in rows]
        ax.plot(x, y, marker="o")
        ax.fill_between(x, low, high, alpha=.18)
        ax.set_xlabel("offered arrival load / fluid L1 capacity (ρ)")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(alpha=.25)
    fig.suptitle("D1-only arrival-load sensitivity (mean, 95% t interval)")
    ax = axes[0, 0]
    rows = metric("A_arrival_load", "util_l2_mean_h")
    rows.sort(key=lambda r: float(r["setting"].replace("rho", "")))
    x = [float(r["setting"].replace("rho", "")) for r in rows]
    ax.plot(x, [r["mean"] for r in rows], marker="s", linestyle="--", label="L2")
    ax.plot([float(r["setting"].replace("rho", "")) for r in metric("A_arrival_load", "util_l1_mean_h")],
            [r["mean"] for r in metric("A_arrival_load", "util_l1_mean_h")],
            marker="o", label="L1")
    ax.legend(fontsize=8)
    ax.set_title("Mean pool utilization at H")
    ax = axes[1, 1]
    rows_h = metric("A_arrival_load", "sla_h")
    rows_terminal = metric("A_arrival_load", "sla_terminal")
    rows_h.sort(key=lambda r: float(r["setting"].replace("rho", "")))
    rows_terminal.sort(key=lambda r: float(r["setting"].replace("rho", "")))
    x_h = [float(r["setting"].replace("rho", "")) for r in rows_h]
    ax.plot(x_h, [r["mean"] for r in rows_h], marker="o", label="SLA at H")
    ax.plot(x_h, [r["mean"] for r in rows_terminal], marker="s", linestyle="--", label="terminal SLA")
    ax.legend(fontsize=8)
    ax.set_title("SLA at H and after drain")
    fig.savefig(out / "a0_arrival_load_curves.svg")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    for ax, key, title, ylabel in (
        (axes[0], "util_l1_mean_h", "L1 utilization", "fraction"),
        (axes[1], "queue_l1_peak_h", "Peak L1 waiting queue", "alerts"),
        (axes[2], "sla_terminal", "Terminal SLA", "fraction admitted"),
    ):
        for series_name, label in (("B_staffing", "18.47 arrivals/h"),
                                   ("C_high_load_reduced_staffing", "22 arrivals/h")):
            rows = metric(series_name, key)
            rows.sort(key=lambda r: int(r["setting"].split("_")[1]), reverse=True)
            x = [int(r["setting"].split("_")[1]) for r in rows]
            ax.errorbar(x, [r["mean"] for r in rows], yerr=[
                [r["mean"]-r["ci95_low"] for r in rows], [r["ci95_high"]-r["mean"] for r in rows]
            ], marker="o", capsize=3, label=label)
        ax.set_xlabel("available L1 analysts")
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.grid(alpha=.25)
        ax.legend(fontsize=8)
    fig.suptitle("D1-only staffing sensitivity at fixed demand levels")
    fig.savefig(out / "a0_staffing_curves.svg")
    plt.close(fig)

    selected = [("A_arrival_load", "rho0.65", "ρ=0.65 reference"),
                ("A_arrival_load", "rho1.25", "ρ=1.25 overload"),
                ("B_staffing", "nL1_4", "fixed demand, 4 L1")]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for series, setting, label in selected:
        group = [r for r in trajectories if r["series"] == series and r["setting"] == setting]
        bins = {}
        for row in group:
            bins.setdefault(row["time_h"], []).append((row["queue_l1_waiting"], row["queue_l2_waiting"]))
        ts = sorted(bins)
        axes[0].plot(ts, [statistics.mean(x[0] for x in bins[t]) for t in ts], label=label)
        axes[1].plot(ts, [statistics.mean(x[1] for x in bins[t]) for t in ts], label=label)
    for ax, title in zip(axes, ("L1 queue evolution", "L2 queue evolution")):
        ax.axvline(HORIZON, color="black", linestyle="--", linewidth=1, label="H" if title.startswith("L1") else None)
        ax.set_xlabel("simulation time (h)")
        ax.set_ylabel("waiting alerts")
        ax.set_title(title)
        ax.grid(alpha=.25)
        ax.legend(fontsize=8)
    fig.savefig(out / "a0_queue_evolution.svg")
    plt.close(fig)

    rows = metric("A_arrival_load", "high_blocked_at_arrival_fraction")
    rows.sort(key=lambda r: float(r["setting"].replace("rho", "")))
    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
    x = [float(r["setting"].replace("rho", "")) for r in rows]
    ax.errorbar(x, [r["mean"] for r in rows], yerr=[
        [r["mean"] - r["ci95_low"] for r in rows],
        [r["ci95_high"] - r["mean"] for r in rows],
    ], marker="o", capsize=3)
    ax.set_xlabel("offered arrival load / fluid L1 capacity (ρ)")
    ax.set_ylabel("fraction of high-priority arrivals")
    ax.set_title("High-priority arrivals finding all eligible L1 busy")
    ax.set_ylim(bottom=0)
    ax.grid(alpha=.25)
    fig.savefig(out / "a0_urgent_blocking.svg")
    plt.close(fig)


def run(output_dir: Path | None = None):
    started = perf_counter()
    out = output_dir or ROOT / CONFIG["output_dir"]
    out.mkdir(parents=True, exist_ok=True)
    episode_rows, trajectory_rows, stratified_rows = [], [], []
    settings = _settings()
    for series, setting, load_value, rate, indices in settings:
        for offset in range(SEED_COUNT):
            seed = SEED_BASE + offset
            metrics, traj, stratified = _run_episode(series, setting, load_value, rate, indices, seed)
            episode_rows.append(metrics)
            trajectory_rows.extend(traj)
            stratified_rows.extend(stratified)
    summaries = _summaries(episode_rows)
    stratified_summaries = _stratified_summaries(stratified_rows)
    _csv(out / "episode_metrics.csv", episode_rows)
    _csv(out / "summary_metrics.csv", summaries)
    _csv(out / "queue_trajectories.csv", trajectory_rows)
    _csv(out / "stratified_metrics.csv", stratified_rows)
    _csv(out / "stratified_summary.csv", stratified_summaries)
    _plots(out, summaries, trajectory_rows)
    metadata = {
        "config": CONFIG,
        "n_settings": len(settings), "n_episodes": len(episode_rows),
        "seed_range": [SEED_BASE, SEED_BASE + SEED_COUNT - 1],
        "runtime_seconds": round(perf_counter() - started, 3),
        "policy": "D1 only",
        "simulated_data_only": True,
        "queue_capacity": "unbounded",
        "loss_or_expiration": "not modeled",
    }
    (out / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return out, episode_rows, summaries


if __name__ == "__main__":
    output, episodes, summaries = run()
    print(f"output={output} episodes={len(episodes)}")
    for row in summaries:
        if row["metric"] in {"rho_l1", "util_l1_mean_h", "queue_l1_peak_h", "p95_wait_l1_h",
                             "sla_h", "sla_terminal", "pending_terminal_total",
                             "high_blocked_at_arrival_fraction"}:
            print(row["series"], row["setting"], row["metric"],
                  f"{row['mean']:.4f} [{row['ci95_low']:.4f}, {row['ci95_high']:.4f}]")
