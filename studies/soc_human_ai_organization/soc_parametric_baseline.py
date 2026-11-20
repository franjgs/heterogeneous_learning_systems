"""Reproducible, configurable reference SOC scenario and frozen-D1 sensitivity.

All time values are hours. SOCTRA informs only the aggregate alert-volume
anchor; roster, project grouping, service, SLA and competence remain assumptions.
This module calls the existing IA-L1/L2 simulator and does not alter D1.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import csv
import math
from pathlib import Path
import statistics
import sys
from typing import Iterable

from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hls.ia_l1_l2_simulation import ScenarioConfig, SimulatedAlert, generate_alerts  # noqa: E402
from hls.rq1_allocation import Analyst  # noqa: E402
from hls.rq1_l1_l2 import L1L2Result, simulate_l1_l2  # noqa: E402


PROJECTS = ("portfolio_top5", "portfolio_next5", "portfolio_tail")
# SOCTRA's anonymized aggregate shares: top five projects, next five, remaining
# observed project labels. These are workload strata, not individual clients.
PROJECT_MIX = (0.592, 0.236, 0.172)
PRIORITIES = ("low", "medium", "high")
PRIORITY_PROBABILITIES = (0.50, 0.35, 0.15)  # assumed
BASE_DEADLINES_H = (("low", 12.0), ("medium", 4.0), ("high", 1.0))  # assumed
BASE_SERVICE_L1_H = {"portfolio_top5": 0.20, "portfolio_next5": 0.25, "portfolio_tail": 0.30}
BASE_SERVICE_L2_H = {"portfolio_top5": 0.75, "portfolio_next5": 0.90, "portfolio_tail": 1.00}
ESCALATION_NEED_BY_PROJECT = (0.03, 0.05, 0.08)  # assumed need, not historical label
AI_SENSITIVITY = 0.90  # assumed operating point
AI_FALSE_POSITIVE_RATE = 0.01  # assumed operating point
HORIZON_H = 24.0
DRAIN_H = 36.0
BASE_ARRIVAL_RATE_PER_H = 9.0  # 216 observed alert records/day ÷ 24; assumes 24x7 clock mapping
BASE_L1_ANALYSTS = 6
BASE_L2_ANALYSTS = 3
REPLICATES = 12
SEED_BASE = 261119000

# Common underlying skill/speed profiles. Eligibility sweeps mask skills but do
# not alter the profiles; service speed is independent of competence.
L1_COMPETENCE = (
    (0.84, 0.74, 0.66), (0.75, 0.87, 0.72), (0.68, 0.90, 0.76),
    (0.86, 0.70, 0.82), (0.78, 0.73, 0.86), (0.72, 0.80, 0.75),
)
L1_SPEED = (
    (0.90, 1.05, 1.10), (1.10, 0.95, 0.90), (1.00, 1.10, 0.95),
    (0.95, 0.90, 1.05), (1.05, 1.00, 0.90), (0.90, 0.95, 1.10),
)
L2_COMPETENCE = ((0.84, 0.78, 0.74), (0.76, 0.88, 0.82), (0.80, 0.76, 0.90))
L2_SPEED = ((0.90, 1.05, 1.00), (1.05, 0.90, 1.10), (1.00, 1.10, 0.90))
ELIGIBILITY_LEVELS = {
    3.0: (PROJECTS, PROJECTS, PROJECTS, PROJECTS, PROJECTS, PROJECTS),
    2.5: (PROJECTS, PROJECTS, PROJECTS, ("portfolio_top5", "portfolio_next5"),
          ("portfolio_next5", "portfolio_tail"), ("portfolio_top5", "portfolio_tail")),
    2.0: (("portfolio_top5", "portfolio_next5"), ("portfolio_next5", "portfolio_tail"),
          ("portfolio_top5", "portfolio_tail"), ("portfolio_top5", "portfolio_next5"),
          ("portfolio_next5", "portfolio_tail"), ("portfolio_top5", "portfolio_tail")),
    1.5: (("portfolio_top5",), ("portfolio_next5",), ("portfolio_tail",),
          ("portfolio_top5", "portfolio_next5"), ("portfolio_next5", "portfolio_tail"),
          ("portfolio_top5", "portfolio_tail")),
    1.0: (("portfolio_top5",), ("portfolio_top5",), ("portfolio_next5",),
          ("portfolio_next5",), ("portfolio_tail",), ("portfolio_tail",)),
}
BASE_ELIGIBILITY = 2.5


@dataclass(frozen=True)
class SocReference:
    """Central scenario contract; names and units are explicit."""

    time_unit: str = "hour"
    horizon_h: float = HORIZON_H
    drain_h: float = DRAIN_H
    arrival_rate_per_h: float = BASE_ARRIVAL_RATE_PER_H
    project_names: tuple[str, ...] = PROJECTS
    project_probabilities: tuple[float, ...] = PROJECT_MIX
    priority_names: tuple[str, ...] = PRIORITIES
    priority_probabilities: tuple[float, ...] = PRIORITY_PROBABILITIES
    sla_deadline_h: tuple[tuple[str, float], ...] = BASE_DEADLINES_H
    n_l1: int = BASE_L1_ANALYSTS
    n_l2: int = BASE_L2_ANALYSTS
    mean_eligible_projects_per_l1: float = BASE_ELIGIBILITY
    escalation_need_by_project: tuple[float, ...] = ESCALATION_NEED_BY_PROJECT
    ai_sensitivity: float = AI_SENSITIVITY
    ai_false_positive_rate: float = AI_FALSE_POSITIVE_RATE
    l1_service_h: tuple[tuple[str, float], ...] = tuple(BASE_SERVICE_L1_H.items())
    l2_service_h: tuple[tuple[str, float], ...] = tuple(BASE_SERVICE_L2_H.items())
    difficulty_beta: tuple[float, float] = (2.0, 2.0)

    def scenario_config(self, *, arrival_rate_per_h: float | None = None,
                        sla_multiplier: float = 1.0) -> ScenarioConfig:
        deadlines = tuple((p, h * sla_multiplier) for p, h in self.sla_deadline_h)
        return ScenarioConfig(
            horizon=self.horizon_h,
            arrival_rate=self.arrival_rate_per_h if arrival_rate_per_h is None else arrival_rate_per_h,
            classes=self.project_names,
            class_probabilities=self.project_probabilities,
            severity_probabilities=self.priority_probabilities,
            escalation_probability_by_class=self.escalation_need_by_project,
            deadline_by_severity=deadlines,
            ai_sensitivity=self.ai_sensitivity,
            ai_false_positive_rate=self.ai_false_positive_rate,
            difficulty_beta=self.difficulty_beta,
        )


REFERENCE = SocReference()


def build_roster(n_l1: int = BASE_L1_ANALYSTS, n_l2: int = BASE_L2_ANALYSTS,
                 mean_eligible_projects: float = BASE_ELIGIBILITY):
    """Return analyst pools plus analyst/project service maps in hours."""
    if n_l1 < 3 or n_l2 < 1:
        raise ValueError("need at least 3 L1 analysts to cover the 3 projects and 1 L2 analyst")
    if mean_eligible_projects not in ELIGIBILITY_LEVELS:
        raise ValueError(f"eligibility level must be one of {tuple(ELIGIBILITY_LEVELS)}")
    patterns = ELIGIBILITY_LEVELS[mean_eligible_projects]
    base_l1, l1_services = [], {}
    for ix in range(n_l1):
        profile_ix = ix % len(L1_COMPETENCE)
        eligible = frozenset(patterns[ix % len(patterns)])
        base_l1.append(Analyst(f"L1-{ix + 1:02d}", eligible,
                               dict(zip(PROJECTS, L1_COMPETENCE[profile_ix]))))
        l1_services[f"L1-{ix + 1:02d}"] = {
            project: dict(BASE_SERVICE_L1_H.items())[project] * L1_SPEED[profile_ix][p_ix]
            for p_ix, project in enumerate(PROJECTS) if project in eligible
        }
    base_l2, l2_services = [], {}
    for ix in range(n_l2):
        profile_ix = ix % len(L2_COMPETENCE)
        analyst_id = f"L2-{ix + 1:02d}"
        base_l2.append(Analyst(analyst_id, frozenset(PROJECTS),
                               dict(zip(PROJECTS, L2_COMPETENCE[profile_ix]))))
        l2_services[analyst_id] = {
            project: dict(BASE_SERVICE_L2_H.items())[project] * L2_SPEED[profile_ix][p_ix]
            for p_ix, project in enumerate(PROJECTS)
        }
    return tuple(base_l1), tuple(base_l2), l1_services, l2_services


def _max_queue(arrival_times: Iterable[float], start_times: Iterable[float]) -> int:
    arrivals = sorted(arrival_times)
    starts = sorted(start_times)
    times = sorted(set(arrivals) | set(starts))
    ai = si = peak = 0
    for now in times:
        while ai < len(arrivals) and arrivals[ai] <= now:
            ai += 1
        while si < len(starts) and starts[si] < now:
            si += 1
        peak = max(peak, ai - si)  # queue just before same-time dispatch
        while si < len(starts) and starts[si] == now:
            si += 1
        peak = max(peak, ai - si)
    return peak


def run_d1_episode(seed: int, *, config: SocReference = REFERENCE,
                   arrival_rate_per_h: float | None = None,
                   n_l1: int | None = None,
                   mean_eligible_projects_per_l1: float | None = None,
                   sla_multiplier: float = 1.0) -> dict[str, object]:
    """Run unchanged D1 and return outcome vector; no scalar reward used."""
    l1n = config.n_l1 if n_l1 is None else n_l1
    eligibility = (config.mean_eligible_projects_per_l1 if mean_eligible_projects_per_l1 is None
                   else mean_eligible_projects_per_l1)
    l1, l2, l1_service, l2_service = build_roster(l1n, config.n_l2, eligibility)
    sc = config.scenario_config(arrival_rate_per_h=arrival_rate_per_h, sla_multiplier=sla_multiplier)
    alerts = generate_alerts(sc, seed)
    sim = simulate_l1_l2(
        tuple(row.routed for row in alerts), l1, l2,
        dict(config.l1_service_h), dict(config.l2_service_h),
        policy="D1", admission_horizon=config.horizon_h,
        drain_period=config.drain_h, coordination_latency=0.0,
        decision_mode="hypothetical_recommendation_acceptance", random_seed=seed,
        l1_service_by_analyst_class=l1_service,
        l2_service_by_analyst_class=l2_service,
    )
    return episode_metrics(alerts, sim)


def episode_metrics(alerts: tuple[SimulatedAlert, ...], sim: L1L2Result) -> dict[str, object]:
    """Compute terminal SLA and congestion without a weighted reward."""
    l1_jobs = {job.alert_id: job for job in sim.l1_simulation.assignments}
    l2_jobs = {job.alert_id: job for job in sim.l2_simulation.assignments}
    admitted = tuple(row for row in alerts if row.routed.alert.arrival < sim.horizon)
    routes = {r.alert_id: r.scenario_routing_decision for r in sim.escalation_records}
    by_priority: dict[str, list[tuple[int, int, int]]] = {p: [] for p in PRIORITIES}
    by_project: dict[str, list[tuple[int, int, int]]] = {p: [] for p in PROJECTS}
    responses, waits = [], []
    expected_correct = 0.0
    for row in admitted:
        alert = row.routed.alert
        l1_job = l1_jobs.get(alert.alert_id)
        final = l2_jobs.get(alert.alert_id) if routes.get(alert.alert_id, False) else l1_job
        completed = int(final is not None and final.completion <= sim.after_drain.cutoff)
        on_time = int(bool(completed) and final.completion <= alert.deadline)
        if completed:
            expected_correct += final.competence * (1.0 - 0.35 * row.difficulty)
        for grouping, key in ((by_priority, row.severity), (by_project, alert.task_class)):
            if key in grouping:
                grouping[key].append((on_time, completed, 1))
        if final is not None and completed:
            responses.append(final.completion - alert.arrival)
        wait = max(0.0, (l1_job.start if l1_job else sim.after_drain.cutoff) - alert.arrival)
        if routes.get(alert.alert_id, False) and l1_job is not None:
            l2_job = l2_jobs.get(alert.alert_id)
            wait += max(0.0, (l2_job.start if l2_job else sim.after_drain.cutoff) - l1_job.completion)
        waits.append(wait)
    def group_sla(group):
        return {k: (sum(x[0] for x in v) / len(v) if v else None,
                    len(v), sum(x[1] for x in v)) for k, v in group.items()}
    def quantile(values, q):
        if not values:
            return None
        ordered = sorted(values)
        return ordered[math.ceil(q * len(ordered)) - 1]
    l1_arrivals = [row.routed.alert.arrival for row in admitted]
    l1_start = [job.start for job in l1_jobs.values()]
    l2_arrivals = [l1_jobs[row.routed.alert.alert_id].completion for row in admitted
                   if routes.get(row.routed.alert.alert_id, False)
                   and row.routed.alert.alert_id in l1_jobs
                   and l1_jobs[row.routed.alert.alert_id].completion < sim.horizon + sim.drain_period]
    l2_start = [job.start for job in l2_jobs.values()]
    util = dict(sim.at_horizon.utilization_by_analyst)
    l1_util = [v for key, v in util.items() if key.startswith("L1:")]
    l2_util = [v for key, v in util.items() if key.startswith("L2:")]
    n = len(admitted)
    end = sim.after_drain
    result = {
        "admitted": n,
        "completed": end.admitted - end.pending,
        "pending": end.pending,
        "sla_h": sim.at_horizon.fraction_within_sla,
        "sla_terminal": end.fraction_within_sla,
        "quality_model": expected_correct / n if n else 0.0,
        "on_time_competence_proxy": end.modeled_quality_per_admitted,
        "mean_response_h": end.mean_response_completed,
        "p95_response_h": quantile(responses, .95),
        "mean_wait_h": end.mean_wait_accrued,
        "mean_wait_recomputed_h": statistics.mean(waits) if waits else 0.0,
        "backlog_l1_end": end.l1_backlog,
        "backlog_l2_end": end.l2_backlog,
        "backlog_l1_peak": _max_queue(l1_arrivals, l1_start),
        "backlog_l2_peak": _max_queue(l2_arrivals, l2_start),
        "l1_util_mean_horizon": statistics.mean(l1_util) if l1_util else 0.0,
        "l1_util_max_horizon": max(l1_util, default=0.0),
        "l2_util_mean_horizon": statistics.mean(l2_util) if l2_util else 0.0,
        "l2_util_max_horizon": max(l2_util, default=0.0),
        "sla_by_priority": group_sla(by_priority),
        "sla_by_project": group_sla(by_project),
        "utilization_by_analyst": dict(sim.at_horizon.utilization_by_analyst),
        "waiting_censored": end.pending,
        "route_rate": sum(bool(row.routed.soctra_recommendation) for row in admitted) / n if n else 0.0,
        "n_l1": len(sim.l1_simulation.at_horizon.utilization_by_analyst),
        "n_l2": len(sim.l2_simulation.at_horizon.utilization_by_analyst),
        "wait_percentile95_h": quantile(waits, .95),
        "seed": None,
    }
    for prefix, groups in (("priority", by_priority), ("project", by_project)):
        for key, (fraction, denominator, completed) in group_sla(groups).items():
            result[f"sla_{prefix}_{key}"] = fraction or 0.0
            result[f"admitted_{prefix}_{key}"] = denominator
            result[f"completed_{prefix}_{key}"] = completed
    return result


SWEEPS = {
    "arrival_rate_per_h": (4.5, 9.0, 13.5, 18.0, 27.0),
    "n_l1": (3, 4, 6, 8, 10),
    "mean_eligible_projects_per_l1": (3.0, 2.5, 2.0, 1.5, 1.0),
    "sla_multiplier": (0.5, 0.75, 1.0, 1.5, 2.0),
}
BASE_POINTS = {
    "arrival_rate_per_h": 9.0,
    "n_l1": 6,
    "mean_eligible_projects_per_l1": BASE_ELIGIBILITY,
    "sla_multiplier": 1.0,
}
PRIMARY_METRIC = "sla_terminal"
METRICS = (
    "admitted", "completed", "pending", "sla_h", "sla_terminal", "quality_model",
    "on_time_competence_proxy", "mean_response_h", "p95_response_h", "mean_wait_h", "backlog_l1_end",
    "backlog_l2_end", "backlog_l1_peak", "backlog_l2_peak",
    "l1_util_mean_horizon", "l1_util_max_horizon", "l2_util_mean_horizon",
    "l2_util_max_horizon",
) + tuple(f"{name}_{group}" for name in ("sla_priority", "admitted_priority", "completed_priority")
           for group in PRIORITIES) + tuple(
               f"{name}_{group}" for name in ("sla_project", "admitted_project", "completed_project")
               for group in PROJECTS)


def _mean_ci(values: list[float]) -> tuple[float, float, float]:
    mean = statistics.mean(values)
    if len(values) < 2:
        return mean, mean, mean
    half = float(student_t.ppf(.975, len(values) - 1)) * statistics.stdev(values) / math.sqrt(len(values))
    return mean, mean - half, mean + half


def run_sensitivity(replicates: int = REPLICATES, seed_base: int = SEED_BASE) -> list[dict[str, object]]:
    """Run four one-factor D1 sweeps; use same seed within every grid point."""
    if replicates < 2:
        raise ValueError("at least two replicates are required for confidence intervals")
    rows: list[dict[str, object]] = []
    for factor, values in SWEEPS.items():
        for value in values:
            for replicate in range(replicates):
                seed = seed_base + replicate
                kwargs = {factor: value}
                result = run_d1_episode(seed, **kwargs)
                result["seed"] = seed
                result["sweep"] = factor
                result["value"] = value
                result["replicate"] = replicate
                rows.append(result)
    return rows


def summarize_sensitivity(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Means, t-CIs and paired deltas against the fixed reference value."""
    result = []
    for factor, values in SWEEPS.items():
        base = BASE_POINTS[factor]
        base_rows = {int(r["seed"]): r for r in rows if r["sweep"] == factor and r["value"] == base}
        for value in values:
            level_rows = [r for r in rows if r["sweep"] == factor and r["value"] == value]
            item: dict[str, object] = {"sweep": factor, "value": value, "base_value": base}
            for metric in METRICS:
                vals = [float(r[metric] or 0.0) for r in level_rows]
                mean, low, high = _mean_ci(vals)
                paired = [float(r[metric] or 0.0) - float(base_rows[int(r["seed"])][metric] or 0.0)
                          for r in level_rows]
                dmean, dlow, dhigh = _mean_ci(paired)
                item.update({f"{metric}_mean": mean, f"{metric}_ci_low": low,
                             f"{metric}_ci_high": high, f"{metric}_delta": dmean,
                             f"{metric}_delta_ci_low": dlow, f"{metric}_delta_ci_high": dhigh})
            result.append(item)
    return result


def write_csv(path: Path, summary: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)


def write_reference_utilization(path: Path, rows: list[dict[str, object]]) -> None:
    """Per-synthetic-analyst utilization at H for the 9 alerts/hour reference."""
    reference_rows = [r for r in rows if r["sweep"] == "arrival_rate_per_h" and r["value"] == 9.0]
    names = sorted({name for r in reference_rows for name in r["utilization_by_analyst"]})
    records = []
    for name in names:
        values = [float(r["utilization_by_analyst"][name]) for r in reference_rows]
        mean, low, high = _mean_ci(values)
        records.append({"synthetic_analyst_id": name, "replicates": len(values),
                        "mean_utilization_at_24h": mean, "ci95_low": low, "ci95_high": high})
    write_csv(path, records)


def write_figure(path: Path, summary: list[dict[str, object]]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = {
        "arrival_rate_per_h": ("Arrival rate (alerts/hour)", "Arrival rate; all other parameters fixed"),
        "n_l1": ("Number of L1 analysts", "L1 staffing; L2 staffing fixed"),
        "mean_eligible_projects_per_l1": ("Mean eligible project classes per L1", "Eligibility overlap; skills/speeds fixed"),
        "sla_multiplier": ("SLA duration multiplier", "Deadline stringency; all else fixed"),
    }
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 7.2), constrained_layout=True)
    for ax, factor in zip(axes.flat, SWEEPS):
        points = [r for r in summary if r["sweep"] == factor]
        x = [float(r["value"]) for r in points]
        y = [float(r["sla_terminal_mean"]) for r in points]
        low = [float(r["sla_terminal_mean"]) - float(r["sla_terminal_ci_low"]) for r in points]
        high = [float(r["sla_terminal_ci_high"]) - float(r["sla_terminal_mean"]) for r in points]
        ax.errorbar(x, y, yerr=[low, high], marker="o", capsize=3)
        ax.set_xlabel(labels[factor][0]); ax.set_ylabel("Terminal SLA completion fraction")
        ax.set_title(labels[factor][1]); ax.set_ylim(-.03, 1.03); ax.grid(alpha=.25)
    fig.suptitle("Frozen D1: one-factor sensitivity (mean and 95% t interval)")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format=path.suffix.lstrip("."), dpi=150)
    plt.close(fig)


def main() -> None:
    out = Path(__file__).resolve().parent
    rows = run_sensitivity()
    summary = summarize_sensitivity(rows)
    write_csv(out / "SOC_PARAMETRIC_D1_SENSITIVITY.csv", summary)
    write_reference_utilization(out / "SOC_PARAMETRIC_D1_ANALYST_UTILIZATION.csv", rows)
    write_figure(out / "SOC_PARAMETRIC_D1_SENSITIVITY.svg", summary)
    for row in summary:
        print(row["sweep"], row["value"],
              f"SLA={row['sla_terminal_mean']:.3f} [{row['sla_terminal_ci_low']:.3f}, {row['sla_terminal_ci_high']:.3f}]",
              f"dSLA={row['sla_terminal_delta']:+.3f} [{row['sla_terminal_delta_ci_low']:+.3f}, {row['sla_terminal_delta_ci_high']:+.3f}]",
              f"q95={row['p95_response_h_mean']:.3f}h backlog={row['pending_mean']:.2f}")


if __name__ == "__main__":
    main()
