"""Paired robustness experiment for RQ1, including decentralized controls.

Example: PYTHONPATH=src python studies/rq1_robustness_experiment.py
No SOCTRA source data are opened. The initial RQ1 results file is untouched.
"""
from __future__ import annotations

import argparse
import random
from collections import defaultdict
from statistics import mean

from hls.rq1_allocation import simulate
from rq1_organization_experiment import DRAIN, HORIZON, LOADS, SERVICE, generate_alerts, make_team


POLICIES = ("B0", "B0-R", "B0-F", "B1", "B2")
DECENTRALIZED = ("B0", "B0-R", "B0-F")
METRICS = {
    "SLA fraction": "fraction_within_sla",
    "Modeled quality/admitted": "modeled_quality_per_admitted",
    "Backlog": "pending",
}
SEED_BASE = 0


def run_robustness(seed_count: int = 30):
    if seed_count < 30:
        raise ValueError("robustness comparison requires at least 30 paired seeds")
    records = []
    for load_name, load in LOADS:
        for seed in range(SEED_BASE, SEED_BASE + seed_count):
            # Demand generation is performed once per (load, seed), then the
            # exact immutable trace is replayed for all policies and profiles.
            alerts = generate_alerts(seed, load)
            for eligibility in ("homogeneous", "restricted"):
                for competence in ("homogeneous", "heterogeneous"):
                    team = make_team(eligibility, competence)
                    for policy in POLICIES:
                        result = simulate(
                            alerts, team, SERVICE, policy=policy,
                            admission_horizon=HORIZON, drain_period=DRAIN,
                            random_seed=seed,
                        )
                        records.append({
                            "condition": (load_name, eligibility, competence),
                            "seed": seed,
                            "policy": policy,
                            "admitted": result.at_horizon.admitted,
                            "H": result.at_horizon,
                            "H+D": result.after_drain,
                        })
    return tuple(records)


def _index_records(records):
    return {
        (row["condition"], row["seed"], row["policy"]): row
        for row in records
    }


def _best_control(index, condition, seeds):
    # Prespecified scenario-level benchmark: largest mean H SLA fraction;
    # exact ties retain the declared order B0, B0-R, B0-F.
    means = {
        policy: mean(index[(condition, seed, policy)]["H"].fraction_within_sla for seed in seeds)
        for policy in DECENTRALIZED
    }
    best = max(DECENTRALIZED, key=lambda policy: means[policy])
    return best, means


def _bootstrap_indices(seed_count, repetitions, rng):
    return [tuple(rng.randrange(seed_count) for _ in range(seed_count)) for _ in range(repetitions)]


def _percentile_interval(values):
    ordered = sorted(values)
    low = ordered[int(0.025 * (len(ordered) - 1))]
    high = ordered[int(0.975 * (len(ordered) - 1))]
    return low, high


def _paired_ci(differences, samples):
    boot_means = [mean(differences[ix] for ix in indices) for indices in samples]
    return _percentile_interval(boot_means)


def _scenario_summary(index, condition, seeds, cutoff, attr, bootstrap_reps):
    values = {
        policy: [getattr(index[(condition, seed, policy)][cutoff], attr) for seed in seeds]
        for policy in POLICIES
    }
    means = {policy: mean(values[policy]) for policy in POLICIES}
    best, _ = _best_control(index, condition, seeds)
    rng = random.Random(f"rq1-ci-v1:{condition}:{cutoff}:{attr}")
    samples = _bootstrap_indices(len(seeds), bootstrap_reps, rng)
    contrasts = {}
    best_boot = {policy: [] for policy in ("B0-R", "B0-F", "B1", "B2")}
    primary_h_sla = {
        policy: [index[(condition, seed, policy)]["H"].fraction_within_sla for seed in seeds]
        for policy in DECENTRALIZED
    }
    metric_values = {
        policy: [getattr(index[(condition, seed, policy)][cutoff], attr) for seed in seeds]
        for policy in POLICIES
    }
    for indices in samples:
        selected_control = max(
            DECENTRALIZED,
            key=lambda candidate: mean(primary_h_sla[candidate][ix] for ix in indices),
        )
        for policy in best_boot:
            best_boot[policy].append(mean(
                metric_values[policy][ix] - metric_values[selected_control][ix]
                for ix in indices
            ))
    for policy in ("B0-R", "B0-F", "B1", "B2"):
        vs_b0 = [left - right for left, right in zip(values[policy], values["B0"])]
        contrasts[(policy, "B0")] = (mean(vs_b0), *_paired_ci(vs_b0, samples))
        vs_best = [left - right for left, right in zip(values[policy], values[best])]
        low, high = _percentile_interval(best_boot[policy])
        contrasts[(policy, "best")] = (mean(vs_best), low, high)
    return means, best, contrasts


def _fmt(value):
    return f"{value:.3f}"


def _format_interval(value):
    estimate, low, high = value
    return f"{_fmt(estimate)} [{_fmt(low)}, {_fmt(high)}]"


def _scenario_name(condition):
    return " / ".join(condition)


def format_report(records, seed_count, bootstrap_reps):
    index = _index_records(records)
    conditions = sorted({row["condition"] for row in records})
    seeds = tuple(range(SEED_BASE, SEED_BASE + seed_count))
    best_by_condition = {condition: _best_control(index, condition, seeds)[0] for condition in conditions}
    summaries = {
        (cutoff, label, condition): _scenario_summary(
            index, condition, seeds, cutoff, attr, bootstrap_reps
        )
        for cutoff in ("H", "H+D")
        for label, attr in METRICS.items()
        for condition in conditions
    }
    lines = [
        "# RQ1 robustness audit: decentralized controls",
        "",
        "**Status:** synthetic robustness experiment; no SOCTRA data were read. Original B0/B1/B2 definitions and the initial eight-seed result file were preserved.",
        "",
        f"Run: {seed_count} paired seeds ({seeds[0]}–{seeds[-1]}), {bootstrap_reps} bootstrap replicates, 3 loads × 2 eligibility structures × 2 competence structures = 12 scenarios and {len(records)} policy runs.",
        "",
        f"Demand/scenario parameters are unchanged from the initial study: H={HORIZON}, D={DRAIN}, 4 analysts, service={SERVICE}, offered loads={dict(LOADS)}, class SLA durations 1.5/2/2.5/3.0, identical generated trace across all five policies and team profiles for each load/seed. B0-R receives the paired seed as its per-run random-order seed. B0-F sorts analysts by number of enabled classes, then ID.",
        "",
        "**Controls:** B0-R and B0-F are robustness controls for B0's analyst order, not proposed primary policies. All three decentralized rules still select each analyst's earliest-deadline eligible alert, with arrival and alert ID ties.",
        "",
        "**Intervals:** 95% paired nonparametric percentile bootstrap intervals of the mean seed-paired difference (resample whole seed indices with replacement; 5,000 replicates by default; fixed report RNG). For best-control contrasts, the decentralized benchmark is selected at scenario level by the highest mean SLA fraction at H, tie order B0→B0-R→B0-F; it is never selected per seed. Each bootstrap replicate repeats that scenario-level selection to include selection uncertainty. These intervals are exploratory for the finite synthetic seed population, not operational confidence intervals.",
        "",
        "## Policy means",
        "",
    ]
    for cutoff in ("H", "H+D"):
        for label, attr in METRICS.items():
            lines.extend([
                f"### {label} — {cutoff}",
                "",
                "| Scenario | Best decentralized control | B0 | B0-R | B0-F | B1 | B2 |",
                "|---|---|---:|---:|---:|---:|---:|",
            ])
            for condition in conditions:
                means, best, _ = summaries[(cutoff, label, condition)]
                lines.append(
                    f"| {_scenario_name(condition)} | {best} | "
                    + " | ".join(_fmt(means[p]) for p in POLICIES) + " |"
                )
            lines.append("")
    lines.extend(["## Paired differences", ""])
    for cutoff in ("H", "H+D"):
        for label, attr in METRICS.items():
            lines.extend([
                f"### {label} — {cutoff}",
                "",
                "Each cell is mean paired difference [95% bootstrap CI]. Lower backlog is favorable; SLA and modeled quality are oriented so higher is favorable.",
                "",
                "| Scenario | Policy | Δ vs B0 | Δ vs best decentralized |",
                "|---|---|---:|---:|",
            ])
            for condition in conditions:
                _, best, contrasts = summaries[(cutoff, label, condition)]
                for policy in ("B0-R", "B0-F", "B1", "B2"):
                    lines.append(
                        f"| {_scenario_name(condition)} | {policy} | "
                        f"{_format_interval(contrasts[(policy, 'B0')])} | "
                        f"{_format_interval(contrasts[(policy, 'best')])} ({best}) |"
                    )
            lines.append("")
    lines.extend(["## Diagnostics", ""])
    lines.extend(_diagnostics(index, conditions, seeds, bootstrap_reps))
    lines.extend([
        "",
        "## Audit findings and limitations",
        "",
        "- The coordinated assignment is exact for the declared lexicographic matching objective at a single dispatch instant; it is not a global-horizon optimizer. The implementation uses a residual min-cost-flow network with lexicographic tuple costs. With A currently free analysts and Q pending alerts, it creates O(AQ) edges and O(A+Q) vertices; the initial shortest-path potentials cost O(AQ) for this forward acyclic network, followed by at most A Dijkstra augmentations, approximately O(A²Q log(A+Q)) per dispatch. It stores O(AQ) edge state. Repeated matching at arrivals/completions can therefore dominate runtime as the pending queue grows.",
        "- Feasibility for on-time assignment uses only `now + s[class] <= deadline`; overdue alerts are retained and assigned when eligible. Event handling incorporates all same-time arrivals, then frees all completing analysts, then dispatches once. Admission is `[0,H)`; completion at H or H+D is included in the corresponding metric snapshot.",
        "- Metrics conserve admitted alerts: on-time completions + late completions + pending = admitted. Pending includes both queued and in-service alerts. H and H+D are separate snapshots; mean wait at H is accrued/right-censored for not-yet-started alerts, response is over completed alerts, and utilization uses service overlap divided by the snapshot cutoff.",
        "- No future arrivals enter B1/B2 decisions. Their only inputs at dispatch are present pending alerts, free analysts, eligibility, current time, class service durations, deadlines, and (for B2) fixed modeled competence.",
        "- The B1–B0 SLA contrast persists against B0-R and the observed B0-F control under this fixed scenario grid; B0-F collapses to B0 here because the rosters have equal flexibility. Thus the evidence weighs against fixed ID ordering as the main explanation, while leaving coordination gains under unequal analyst flexibility untested. The contrast remains conditional on synthetic service/SLA assumptions and cost-free instantaneous coordination.",
        "- B0-R and B0-F are diagnostic controls, not scientifically proposed replacement baselines. All competencies, service times, SLA durations, arrivals, and eligibility maps are hypothetical. Results are not accuracy or SOC operational performance; there is no escalation, staffing schedule, waiting interruption, future-arrival anticipation, coordination cost, or external validation.",
        "",
        "## Reproducibility",
        "",
        "Run with `PYTHONPATH=src python studies/rq1_robustness_experiment.py --seeds 30 --bootstrap-reps 5000`. The experiment uses standard-library RNG and an explicit seed for every demand trace, B0-R order stream, and bootstrap stream. The earlier initial-results artifact is retained unchanged.",
        "",
    ])
    return "\n".join(lines)


def _diagnostics(index, conditions, seeds, bootstrap_reps):
    lines = []
    b1_best_h = []
    b1_best_d = []
    b1_by_eligibility = defaultdict(list)
    order_effects = []
    b2_quality = []
    b2_sla = []
    worse_b1_b0 = worse_b2_b0 = worse_b1_best = worse_b2_best = 0
    worse_outcomes = defaultdict(list)
    for condition in conditions:
        best, _ = _best_control(index, condition, seeds)
        h1 = mean(index[(condition, seed, "B1")]["H"].fraction_within_sla - index[(condition, seed, best)]["H"].fraction_within_sla for seed in seeds)
        d1 = mean(index[(condition, seed, "B1")]["H+D"].fraction_within_sla - index[(condition, seed, best)]["H+D"].fraction_within_sla for seed in seeds)
        b1_best_h.append(h1)
        b1_best_d.append(d1)
        b1_by_eligibility[condition[1]].append(h1)
        order_effects.append(mean(index[(condition, seed, "B0-R")]["H"].fraction_within_sla - index[(condition, seed, "B0")]["H"].fraction_within_sla for seed in seeds))
        b2_quality.append(mean(index[(condition, seed, "B2")]["H"].modeled_quality_per_admitted - index[(condition, seed, "B1")]["H"].modeled_quality_per_admitted for seed in seeds))
        b2_sla.append(mean(index[(condition, seed, "B2")]["H"].fraction_within_sla - index[(condition, seed, "B1")]["H"].fraction_within_sla for seed in seeds))
        b0sla = mean(index[(condition, seed, "B0")]["H"].fraction_within_sla for seed in seeds)
        b1sla = mean(index[(condition, seed, "B1")]["H"].fraction_within_sla for seed in seeds)
        b2sla = mean(index[(condition, seed, "B2")]["H"].fraction_within_sla for seed in seeds)
        bestsla = mean(index[(condition, seed, best)]["H"].fraction_within_sla for seed in seeds)
        worse_b1_b0 += b1sla < b0sla
        worse_b2_b0 += b2sla < b0sla
        worse_b1_best += b1sla < bestsla
        worse_b2_best += b2sla < bestsla
        for cutoff in ("H", "H+D"):
            for metric_name, attr in METRICS.items():
                baseline = mean(getattr(index[(condition, seed, "B0")][cutoff], attr) for seed in seeds)
                for policy in ("B1", "B2"):
                    candidate = mean(getattr(index[(condition, seed, policy)][cutoff], attr) for seed in seeds)
                    is_worse = candidate > baseline if metric_name == "Backlog" else candidate < baseline
                    if is_worse:
                        worse_outcomes[(cutoff, metric_name, policy)].append(_scenario_name(condition))

    lines.extend([
        f"- **A — B1 versus robust decentralized control:** B1 mean paired SLA-fraction difference vs the scenario-level best decentralized control averaged {_fmt(mean(b1_best_h))} at H (range {_fmt(min(b1_best_h))} to {_fmt(max(b1_best_h))} across 12 scenarios) and {_fmt(mean(b1_best_d))} after drain. These point summaries describe this synthetic design only.",
        f"- **B — dependence on eligibility:** mean H SLA difference B1−best control was {_fmt(mean(b1_by_eligibility['homogeneous']))} under homogeneous eligibility and {_fmt(mean(b1_by_eligibility['restricted']))} under restricted eligibility. This is a descriptive scenario contrast; eligibility and load are not a sampled SOC population.",
        f"- **C — fixed-order sensitivity:** mean H SLA difference B0-R−B0 across scenarios was {_fmt(mean(order_effects))}; per-scenario range {_fmt(min(order_effects))} to {_fmt(max(order_effects))}. B0-F was identical to B0 in these 12 scenarios because every analyst had the same flexibility count (4 classes under homogeneous eligibility; 2 under restricted eligibility); it does not test differing-flexibility order here. The difference diagnoses analyst-order sensitivity, not a causal estimate of real decentralized behavior.",
        f"- **D — B2 quality/SLA trade-off:** mean paired H modeled-quality difference B2−B1 was {_fmt(mean(b2_quality))}; mean H SLA-fraction difference was {_fmt(mean(b2_sla))}. B2 had higher mean quality than B1 in {sum(value > 0 for value in b2_quality)}/12 scenario cells (all heterogeneous-competence cells) and higher SLA fraction in {sum(value > 0 for value in b2_sla)}/12. Modeled quality gain is conditional on competence heterogeneity and can coincide with lower SLA completion.",
        f"- **E — adverse scenarios:** B1's mean H SLA was below B0 in {worse_b1_b0}/12 scenarios and below the selected decentralized control in {worse_b1_best}/12. B2 was below B0 in {worse_b2_b0}/12 and below the selected control in {worse_b2_best}/12. Use the scenario tables for exact values and intervals.",
        "- **Other metric trade-offs:**",
        *[
            f"  - {policy} had worse {metric_name.lower()} than B0 at {cutoff} in {len(cells)}/12 cells: {', '.join(cells)}."
            for (cutoff, metric_name, policy), cells in sorted(worse_outcomes.items())
        ],
        "",
        "**Decision:** REVISE before any operational claim. The SLA advantage persists against B0-R in the medium/high-load synthetic cells and is too large to attribute mainly to the fixed analyst-ID order. However, B0-F is degenerate under the current equal-flexibility rosters, and the scenario-level best-control contrast is approximately zero in low-load restricted cases. Add a predeclared unequal-flexibility roster and validate service/deadline meanings and coordination costs before interpreting B1/B2 gains as SOC improvement.",
    ])
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--bootstrap-reps", type=int, default=5000)
    args = parser.parse_args()
    if args.bootstrap_reps < 1000:
        parser.error("--bootstrap-reps must be at least 1000")
    print(format_report(run_robustness(args.seeds), args.seeds, args.bootstrap_reps))


if __name__ == "__main__":
    main()
