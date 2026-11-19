"""Predeclared RQ1 mechanism experiment: eligibility flexibility × dispatch latency.

Run: PYTHONPATH=src python studies/rq1_mechanism_experiment.py
Only synthetic arrivals are generated; no SOCTRA source data are opened.
"""
from __future__ import annotations

import math
import random
from statistics import mean, stdev

from hls.rq1_allocation import Alert, Analyst, simulate


N_SPECIALISTS = 4
N_GENERALISTS = 2
N_ANALYSTS = N_SPECIALISTS + N_GENERALISTS
CLASSES = tuple(range(4))
HORIZON = 12.0
DRAIN = 12.0
SERVICE = {0: 0.8, 1: 1.0, 2: 1.2, 3: 1.0}
MEAN_SERVICE = sum(SERVICE.values()) / len(SERVICE)
LOADS = (("low", 0.55), ("medium", 0.90), ("high", 1.25))
LATENCIES = (0.0, 0.10, 0.25, 0.50, 1.00)
ELIGIBILITY_PROFILES = ("homogeneous", "asymmetric")
POLICIES = ("B0", "B0-R", "B0-F", "B1", "B2")
SEEDS = tuple(range(30))
T_CRIT_DF29 = 2.045229642


def generate_alerts(seed: int, offered_load: float) -> tuple[Alert, ...]:
    """Generate one deterministic Poisson trace, reused across every cell."""
    rng = random.Random(seed)
    arrival_rate = offered_load * N_ANALYSTS / MEAN_SERVICE
    now = 0.0
    alerts = []
    while True:
        now += rng.expovariate(arrival_rate)
        if now >= HORIZON:
            break
        task_class = rng.randrange(len(CLASSES))
        sla = (1.5, 2.0, 2.5, 3.0)[task_class]
        alerts.append(Alert(f"seed-{seed:02d}-alert-{len(alerts):04d}", now, task_class, now + sla))
    return tuple(alerts)


def make_team(eligibility: str) -> tuple[Analyst, ...]:
    """Six fixed analysts; asymmetric roster has four specialists/two generalists."""
    team = []
    generalist_sets = ({0, 1, 2}, {1, 2, 3})
    for ix in range(N_GENERALISTS):
        allowed = set(CLASSES) if eligibility == "homogeneous" else generalist_sets[ix]
        team.append(Analyst(
            f"0{ix}-generalist-{ix}", frozenset(allowed),
            {k: 0.70 for k in CLASSES},
        ))
    for task_class in CLASSES:
        allowed = set(CLASSES) if eligibility == "homogeneous" else {task_class}
        team.append(Analyst(
            f"1{task_class}-specialist-{task_class}", frozenset(allowed),
            {k: (0.95 if k == task_class else 0.45) for k in CLASSES},
        ))
    return tuple(team)


def run_experiment():
    rows = []
    for load_name, load in LOADS:
        for seed in SEEDS:
            trace = generate_alerts(seed, load)
            for eligibility in ELIGIBILITY_PROFILES:
                team = make_team(eligibility)
                for latency in LATENCIES:
                    for policy in POLICIES:
                        result = simulate(
                            trace, team, SERVICE, policy=policy,
                            admission_horizon=HORIZON, drain_period=DRAIN,
                            random_seed=seed,
                            coordination_latency=latency,
                        )
                        rows.append({
                            "condition": (load_name, eligibility, latency),
                            "seed": seed,
                            "policy": policy,
                            "H": result.at_horizon,
                            "H+D": result.after_drain,
                        })
    return tuple(rows)


def _index(rows):
    return {(row["condition"], row["seed"], row["policy"]): row for row in rows}


def _metric_value(metrics, name):
    if name == "mean_utilization":
        vals = [value for _, value in metrics.utilization_by_analyst]
        return mean(vals) if vals else 0.0
    return getattr(metrics, name)


def _paired_t_interval(differences):
    n = len(differences)
    estimate = mean(differences)
    margin = T_CRIT_DF29 * stdev(differences) / math.sqrt(n) if n > 1 else 0.0
    return estimate, estimate - margin, estimate + margin


def _fmt(value):
    return f"{value:.3f}"


def _fmt_ci(result):
    est, low, high = result
    return f"{_fmt(est)} [{_fmt(low)}, {_fmt(high)}]"


def _scenario_label(condition):
    load, eligibility, latency = condition
    return f"{load} / {eligibility} / {latency:g}s"


def _summarize(index, condition, cutoff, metric):
    per_seed = {
        policy: [
            _metric_value(index[(condition, seed, policy)][cutoff], metric)
            for seed in SEEDS
        ]
        for policy in POLICIES
    }
    means = {policy: mean(values) for policy, values in per_seed.items()}
    diffs = {}
    pairs = (
        ("B0-R", "B0"), ("B0-F", "B0"),
        ("B1", "B0"), ("B1", "B0-F"), ("B1", "B0-R"),
        ("B2", "B0-F"), ("B2", "B1"),
    )
    for left, right in pairs:
        diffs[(left, right)] = _paired_t_interval([
            x - y for x, y in zip(per_seed[left], per_seed[right])
        ])
    return means, diffs


def _mean_tables(index, conditions):
    sections = []
    metrics = (
        ("SLA fraction", "fraction_within_sla"),
        ("Modeled quality/admitted", "modeled_quality_per_admitted"),
        ("Backlog", "pending"),
        ("Mean analyst utilization", "mean_utilization"),
    )
    for cutoff, cutoff_name in (("H", "at H"), ("H+D", "after drain")):
        for label, metric in metrics:
            sections.extend([
                f"### {label} — {cutoff_name}",
                "",
                "| Load / eligibility / dispatch latency | B0 | B0-R | B0-F | B1 | B2 |",
                "|---|---:|---:|---:|---:|---:|",
            ])
            for condition in conditions:
                means, _ = _summarize(index, condition, cutoff, metric)
                sections.append(
                    f"| {_scenario_label(condition)} | "
                    + " | ".join(_fmt(means[p]) for p in POLICIES) + " |"
                )
            sections.append("")
    return sections


def _contrast_tables(index, conditions):
    sections = []
    for cutoff, cutoff_name in (("H", "H"), ("H+D", "H+D")):
        _, _ = cutoff_name, cutoff
        means, diffs = None, None
        for metric_name, metric, pairs in (
            ("SLA fraction", "fraction_within_sla", (("B0-R", "B0"), ("B0-F", "B0"), ("B1", "B0"), ("B1", "B0-F"), ("B1", "B0-R"), ("B2", "B0-F"))),
            ("Modeled quality/admitted", "modeled_quality_per_admitted", (("B2", "B0-F"), ("B2", "B1"))),
            ("Backlog", "pending", (("B1", "B0-F"), ("B2", "B0-F"))),
            ("Mean analyst utilization", "mean_utilization", (("B1", "B0-F"), ("B2", "B0-F"))),
        ):
            sections.extend([
                f"### Paired differences: {metric_name} — {cutoff_name}",
                "",
                "Cells show mean seed-paired difference [95% paired t interval, df=29].",
                "",
                "| Load / eligibility / latency | " + " | ".join(f"Δ {a}−{b}" for a, b in pairs) + " |",
                "|---|" + "---:|" * len(pairs),
            ])
            for condition in conditions:
                _, diffs = _summarize(index, condition, cutoff, metric)
                sections.append(
                    f"| {_scenario_label(condition)} | "
                    + " | ".join(_fmt_ci(diffs[pair]) for pair in pairs) + " |"
                )
            sections.append("")
    return sections


def _diagnostics(index, conditions):
    lines = []
    controls_by_eligibility = {}
    retained = []
    threshold_rows = []
    appreciable = []
    for eligibility in ELIGIBILITY_PROFILES:
        control_differences = []
        for load_name, _ in LOADS:
            for latency in LATENCIES:
                condition = (load_name, eligibility, latency)
                _, diff = _summarize(index, condition, "H", "fraction_within_sla")
                control_differences.append((condition, diff))
        controls_by_eligibility[eligibility] = control_differences

    for load_name, _ in LOADS:
        for eligibility in ELIGIBILITY_PROFILES:
            values_h, values_d = [], []
            means_h, means_d = [], []
            for latency in LATENCIES:
                condition = (load_name, eligibility, latency)
                m_h, d_h = _summarize(index, condition, "H", "fraction_within_sla")
                m_d, d_d = _summarize(index, condition, "H+D", "fraction_within_sla")
                delta_h = d_h[("B1", "B0-F")]
                delta_d = d_d[("B1", "B0-F")]
                means_h.append(delta_h[0])
                means_d.append(delta_d[0])
                values_h.append(delta_h)
                values_d.append(delta_d)
                appreciable.append((
                    condition,
                    delta_h[0] >= 0.05 and delta_h[1] > 0,
                    delta_d[0] >= 0.05 and delta_d[1] > 0,
                ))
            for values, horizon_name in ((means_h, "H"), (means_d, "H+D")):
                crossing = next((ix for ix, value in enumerate(values) if value <= 0), None)
                threshold_rows.append((load_name, eligibility, horizon_name, crossing, values))
            for latency, delta_h, delta_d in zip(LATENCIES, values_h, values_d):
                condition = (load_name, eligibility, latency)
                m_h, _ = _summarize(index, condition, "H", "fraction_within_sla")
                if m_h["B1"] - m_h["B0"] > 1e-12:
                    retained.append((condition, delta_h[0] / (m_h["B1"] - m_h["B0"])))

    lines.extend([
        "## Mechanism diagnostics",
        "",
        "- **A — B0-F versus B0:** in the asymmetric roster, B0-F dispatches four single-class specialists before the two generalists; in the homogeneous roster all flexibility counts tie and B0-F reduces to the ID order. The SLA paired contrasts (B0-F−B0 and B0-R−B0) are in the SLA difference tables. The roster is asymmetric by design, not fitted to outcomes.",
        "- **B — B1 advantage retained versus B0-F:** among conditions where B1−B0 is positive, the mean ratio `(B1−B0-F)/(B1−B0)` at H was " + _fmt(mean(ratio for _, ratio in retained)) + "; ratios by load, eligibility, and latency are in the SLA tables. This ratio is descriptive and can exceed 1 or be negative.",
        "- **C — appreciable gains:** predeclared as a point SLA gain of at least 0.05 with the paired 95% interval lower bound above zero. The scenario/latency cells meeting this criterion are listed below.",
        "- **D — latency response:** tables include 0, 0.10, 0.25, 0.50, and 1.00 service-time units. Dispatch latency is applied once per nonempty coordinated batch; affected analysts wait idle with their alerts reserved. Arrivals during latency remain eligible for decisions by other free analysts. Each decision's assignments start together when its latency expires. B0/B0-R/B0-F incur zero latency.",
        "- **E — threshold:** the report marks the first tested latency at which the mean paired B1−B0-F SLA difference is nonpositive, separately at H and H+D. This is a sampled sign crossing, not an interpolated or inferred threshold; if none is found, no crossing is reported through one mean service time.",
        "- **F — B2 quality:** modeled quality and B2−B1 quality intervals are reported at both cutoffs; SLA differences show whether that quality gain trades against timeliness.",
        "",
        "### Cells meeting the appreciable-SLA criterion",
        "",
    ])
    lines.append("| Load / eligibility / latency | At H | After drain |")
    lines.append("|---|---|---|")
    for condition, at_h, after_drain in appreciable:
        if at_h or after_drain:
            lines.append(f"| {_scenario_label(condition)} | {'yes' if at_h else 'no'} | {'yes' if after_drain else 'no'} |")
    if not any(a or b for _, a, b in appreciable):
        lines.append("| No cells | — | — |")
    lines.extend(["", "### Sampled latency threshold for B1 versus B0-F", "", "| Load / eligibility | Cutoff | First tested nonpositive mean | Mean differences across latency grid |", "|---|---|---:|---|"])
    for load_name, eligibility, horizon_name, crossing, values in threshold_rows:
        if crossing is None:
            crossing_text = "none through 1.00"
        else:
            crossing_text = f"{LATENCIES[crossing]:g}"
        sequence = "; ".join(f"{latency:g}: {_fmt(value)}" for latency, value in zip(LATENCIES, values))
        lines.append(f"| {load_name} / {eligibility} | {horizon_name} | {crossing_text} | {sequence} |")
    return lines


def format_report(rows):
    index = _index(rows)
    conditions = sorted({row["condition"] for row in rows})
    lines = [
        "# RQ1 final mechanism experiment: eligibility and coordination latency",
        "",
        "**Status:** predeclared synthetic mechanism experiment. No SOCTRA data were read. Earlier RQ1 and HLS-02 result files were not edited.",
        "",
        f"Thirty paired seeds (0–29); 3 offered loads × 2 eligibility profiles × 5 latencies = 30 conditions; {len(rows)} policy runs. The same seed/load demand trace is reused across eligibility, latency, and all five policies.",
        "",
        f"Parameters: six analysts (four specialists, two generalists); four classes; H={HORIZON:g}, drain D={DRAIN:g}; mean service={MEAN_SERVICE:g}; service={SERVICE}; loads={dict(LOADS)}; SLA durations by class=(1.5, 2, 2.5, 3) time units; latency grid={LATENCIES}, i.e. 0, 0.10, 0.25, 0.50, and 1.00 times mean service. Synthetic arrivals are Poisson and classes equiprobable.",
        "",
        "Eligibility profiles: homogeneous means all six analysts can process all four classes. Asymmetric means four single-class specialists (one per class) and two generalists: generalist 0 can process classes 0/1/2; generalist 1 can process 1/2/3. Thus every class has a specialist and at least one generalist; classes 1 and 2 have several generalist options. Competence matrix is held fixed across eligibility profiles: specialists score 0.95 on their named class and 0.45 elsewhere; generalists score 0.70 on each class. These values are hypothetical and B2 uses them only for modeled quality, never to change service time.",
        "",
        "Latency semantics: at a nonempty B1/B2 decision at time t, reserve the matched alerts and hold the selected analysts idle until t+ℓ; service begins at t+ℓ. A reserved alert cannot be assigned again. New arrivals during this interval enter the shared queue; analysts not reserved may receive a separate decision. Each batch incurs one latency interval, not one interval per analyst. B0 variants are unaffected. Feasibility predictions for B1/B2 include ℓ. Utilization counts service time only; response and wait include latency.",
        "",
        "Intervals use paired Student t intervals for the mean of 30 seed-level differences (df=29; t*=2.04523). Seeds are paired across policies and comparable conditions. This assumes the paired seed differences are sufficiently regular for a t interval; intervals describe this synthetic seed design, not uncertainty about a real SOC.",
        "",
        "## Policy means",
        "",
        *_mean_tables(index, conditions),
        "## Paired differences",
        "",
        *_contrast_tables(index, conditions),
        *_diagnostics(index, conditions),
        "",
        "## Limitations and interpretation",
        "",
        "Service durations, SLA windows, competence scores, eligibility, and dispatch latency are synthetic. The latency values are stress-test parameters, not estimated coordination costs. The model has no SOCTRA triage/escalation, shifts, handoffs, interruptions, service variation, learning, or cost accounting beyond the idle dispatch interval. The coordinated decision remains a local matching at each dispatch instant and does not anticipate future arrivals. Policy differences are conditional simulation results, not evidence of operational superiority.",
        "",
        "The first nonpositive point difference, where present, only brackets a crossing between adjacent tested latency values. No interpolation or extrapolation is made. Where confidence intervals include zero, the sign of the estimated mean alone does not establish a reliable advantage.",
        "",
        "Reproduce with `PYTHONPATH=src python studies/rq1_mechanism_experiment.py`.",
        "",
    ]
    return "\n".join(lines)


def main():
    print(format_report(run_experiment()))


if __name__ == "__main__":
    main()
