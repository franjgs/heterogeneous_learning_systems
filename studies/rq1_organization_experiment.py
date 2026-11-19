"""Paired synthetic first experiment for SOCTRA-HLS RQ1.

Example: PYTHONPATH=src python studies/rq1_organization_experiment.py
The script uses no SOCTRA input and reports aggregate results only.
"""
from __future__ import annotations

import argparse
import random
from collections import defaultdict

from hls.rq1_allocation import Alert, Analyst, simulate


N_ANALYSTS = 4
HORIZON = 12.0
DRAIN = 12.0
LOADS = (("low", 0.55), ("medium", 0.90), ("high", 1.25))
ELIGIBILITY = ("homogeneous", "restricted")
COMPETENCE = ("homogeneous", "heterogeneous")
SERVICE = {0: 0.8, 1: 1.0, 2: 1.2, 3: 1.0}
SLA = {0: 1.5, 1: 2.0, 2: 2.5, 3: 3.0}
POLICIES = ("B0", "B1", "B2")


def generate_alerts(seed: int, offered_load: float) -> tuple[Alert, ...]:
    """Poisson arrivals, four equiprobable classes and fixed class SLA."""
    rng = random.Random(seed)
    rate = offered_load * N_ANALYSTS / (sum(SERVICE.values()) / len(SERVICE))
    now = 0.0
    alerts = []
    while True:
        now += rng.expovariate(rate)
        if now >= HORIZON:
            break
        task_class = rng.randrange(4)
        alerts.append(Alert(f"s{seed:03d}-a{len(alerts):04d}", now, task_class, now + SLA[task_class]))
    return tuple(alerts)


def make_team(eligibility: str, competence_profile: str) -> tuple[Analyst, ...]:
    team = []
    for i in range(N_ANALYSTS):
        enabled = frozenset(range(4)) if eligibility == "homogeneous" else frozenset({i, (i + 1) % 4})
        if competence_profile == "homogeneous":
            values = {k: 0.65 for k in enabled}
        else:
            values = {k: (0.95 if i == k else 0.55) for k in enabled}
        team.append(Analyst(f"analyst-{i:02d}", enabled, values))
    return tuple(team)


def run_experiment(seed_count: int = 8) -> tuple[dict, ...]:
    if seed_count < 1:
        raise ValueError("seed_count must be positive")
    rows = []
    for load_name, load in LOADS:
        for seed in range(seed_count):
            trace = generate_alerts(seed, load)
            for eligibility in ELIGIBILITY:
                for competence in COMPETENCE:
                    team = make_team(eligibility, competence)
                    for policy in POLICIES:
                        result = simulate(
                            trace, team, SERVICE, policy=policy,
                            admission_horizon=HORIZON, drain_period=DRAIN,
                        )
                        rows.append({
                            "load": load_name,
                            "eligibility": eligibility,
                            "competence": competence,
                            "seed": seed,
                            "policy": policy,
                            "admitted": result.at_horizon.admitted,
                            "horizon": result.at_horizon,
                            "drained": result.after_drain,
                        })
    return tuple(rows)


def _mean(values):
    return sum(values) / len(values) if values else 0.0


def _condition_rows(rows, cutoff):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["load"], row["eligibility"], row["competence"], row["seed"], row["policy"])].append(row[cutoff])
    seed_metrics = {}
    for key, values in grouped.items():
        seed_metrics[key] = values[0]
    conditions = sorted({key[:3] for key in seed_metrics})
    summary = []
    for condition in conditions:
        seed_ids = sorted({key[3] for key in seed_metrics if key[:3] == condition})
        metric_names = (
            "admitted",
            "fraction_within_sla", "completed_within_sla", "completed_late", "pending",
            "mean_wait_accrued", "mean_response_completed", "mean_utilization",
            "modeled_quality_per_admitted",
        )
        metrics = {}
        for name in metric_names:
            by_policy = {
                policy: [_metric_value(seed_metrics[(*condition, seed, policy)], name) for seed in seed_ids]
                for policy in POLICIES
            }
            metrics[name] = {
                policy: _mean(vals) for policy, vals in by_policy.items()
            }
            metrics[name]["delta_B1_B0"] = _mean([
                by_policy["B1"][ix] - by_policy["B0"][ix] for ix in range(len(seed_ids))
            ])
            metrics[name]["delta_B2_B0"] = _mean([
                by_policy["B2"][ix] - by_policy["B0"][ix] for ix in range(len(seed_ids))
            ])
        summary.append((condition, metrics))
    return summary


def _value(value):
    return value if value is not None else 0.0


def _metric_value(metric, name):
    if name == "mean_utilization":
        values = [value for _, value in metric.utilization_by_analyst]
        return _mean(values) if values else 0.0
    return _value(getattr(metric, name))


def _fmt(value):
    return f"{value:.3f}"


def format_report(rows, seed_count):
    output = [
        "# RQ1 synthetic initial experiment",
        "",
        f"Paired seeds: {seed_count}. Alerts are synthetic; each seed's identical arrival trace is replayed under B0/B1/B2 and all organization profiles. No SOCTRA extract is read.",
        "",
        f"Parameters: H={HORIZON:g}, drain={DRAIN:g}, {N_ANALYSTS} analysts, service by class={SERVICE}, SLA duration by class={SLA}, loads={dict(LOADS)}. Arrival processes are Poisson; classes are equiprobable; random seed is the integer 0 through {seed_count - 1}. Restricted eligibility gives analyst i classes {{i, i+1 mod 4}}. Heterogeneous competence assigns 0.95 to the class-index specialist and 0.55 to other eligible classes; homogeneous competence is 0.65. These are scenario parameters, not empirical estimates.",
        "",
        "Each table reports means across paired seeds. ΔB1−B0 and ΔB2−B0 are computed within seed before averaging. Positive SLA and quality differences are larger modeled values; negative pending/wait/response differences are lower modeled values. The wait metric at H is waiting time accrued to the cutoff, including right-censored waits for alerts not yet started. Response is averaged over alerts completed by that cutoff. Mean utilization is the average of the four analyst utilizations. Quality is modeled competence contribution for alerts completed by the cutoff and within SLA, divided by all admitted alerts.",
    ]
    metric_labels = (
        ("fraction_within_sla", "SLA fraction"),
        ("admitted", "Admitted alerts"),
        ("completed_within_sla", "Completed within SLA"),
        ("completed_late", "Completed late"),
        ("pending", "Pending"),
        ("mean_wait_accrued", "Mean wait accrued"),
        ("mean_response_completed", "Mean response"),
        ("mean_utilization", "Mean analyst utilization"),
        ("modeled_quality_per_admitted", "Modeled quality/admitted"),
    )
    for cutoff, heading in (("horizon", "At admission cutoff H"), ("drained", "After explicit drain")):
        output.extend(["", f"## {heading}", ""])
        summary = _condition_rows(rows, cutoff)
        for metric_name, label in metric_labels:
            output.extend([
                f"### {label}",
                "",
                "| Load / eligibility / competence | B0 | B1 | B2 | Δ B1−B0 | Δ B2−B0 |",
                "|---|---:|---:|---:|---:|---:|",
            ])
            for condition, metrics in summary:
                name = " / ".join(condition)
                values = metrics[metric_name]
                output.append(
                    f"| {name} | {_fmt(values['B0'])} | {_fmt(values['B1'])} | {_fmt(values['B2'])} | {_fmt(values['delta_B1_B0'])} | {_fmt(values['delta_B2_B0'])} |"
                )
            output.append("")
    output.extend([
        "## Interpretation boundary",
        "",
        "These are deterministic outputs of the declared synthetic traces and rules. They establish neither operational superiority nor estimates for SOCTRA/GMV. B1 optimizes only its current dispatch matching; no policy anticipates future arrivals. B2's modeled quality is not classification accuracy or adjudicated treatment quality.",
        "",
    ])
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=8)
    args = parser.parse_args()
    print(format_report(run_experiment(args.seeds), args.seeds))


if __name__ == "__main__":
    main()
