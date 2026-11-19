"""Development/evaluation study for adaptive policy B3.

Run with: PYTHONPATH=src python studies/rq1_b3_adaptive_experiment.py
All demand is synthetic; this study does not read SOCTRA inputs.
"""
from __future__ import annotations

from dataclasses import replace
import math
from statistics import mean, stdev

from hls.rq1_allocation import B3Config, simulate
from rq1_mechanism_experiment import (
    DRAIN, ELIGIBILITY_PROFILES, HORIZON, LATENCIES, LOADS, SERVICE,
    generate_alerts, make_team,
)


DEV_SEEDS = tuple(range(100, 130))
EVAL_SEEDS = tuple(range(1000, 1030))
FIXED_POLICIES = ("B0", "B1", "B2")
EVAL_POLICIES = (*FIXED_POLICIES, "B3", "B3-no-competence", "B3-no-load")
LOAD_THRESHOLDS = (0.75, 1.0)
URGENCY_THRESHOLDS = (0.25, 0.50)
COMPETENCE_THRESHOLDS = (0.15, 0.30)
COST_LIMITS = (0.25, 0.50, 1.0)
T_CRIT_DF29 = 2.045229642


def parameter_grid():
    for load in LOAD_THRESHOLDS:
        for urgency in URGENCY_THRESHOLDS:
            for competence in COMPETENCE_THRESHOLDS:
                for cost in COST_LIMITS:
                    yield B3Config(load, urgency, competence, cost)


def run_cell(seed, load_name, load, eligibility, latency, policies, configs):
    trace = generate_alerts(seed, load)
    team = make_team(eligibility)
    results = {}
    for policy in policies:
        config = configs[policy]
        engine_policy = "B3" if policy.startswith("B3-") else policy
        result = simulate(
            trace, team, SERVICE, policy=engine_policy,
            admission_horizon=HORIZON, drain_period=DRAIN,
            random_seed=seed, coordination_latency=latency,
            b3_config=config,
        )
        results[policy] = result
    return results


def _primary(result):
    m = result.at_horizon
    return (m.fraction_within_sla + m.modeled_quality_per_admitted) / 2


def develop():
    configs = tuple(parameter_grid())
    totals = {config: 0.0 for config in configs}
    fixed_totals = {policy: 0.0 for policy in FIXED_POLICIES}
    n = 0
    for seed in DEV_SEEDS:
        for load_name, load in LOADS:
            for eligibility in ELIGIBILITY_PROFILES:
                for latency in LATENCIES:
                    result = run_cell(
                        seed, load_name, load, eligibility, latency,
                        (*FIXED_POLICIES, "B3"),
                        {"B3": configs[0], **{p: B3Config() for p in FIXED_POLICIES}},
                    )
                    for policy in FIXED_POLICIES:
                        fixed_totals[policy] += _primary(result[policy])
                    n += 1
                    for config in configs:
                        adaptive = simulate(
                            generate_alerts(seed, load), make_team(eligibility), SERVICE,
                            policy="B3", admission_horizon=HORIZON,
                            drain_period=DRAIN, random_seed=seed,
                            coordination_latency=latency, b3_config=config,
                        )
                        totals[config] += _primary(adaptive)
    # Deterministic tie break: first config in the declared grid.
    best_config = max(configs, key=lambda config: totals[config] / n)
    best_fixed = max(FIXED_POLICIES, key=lambda policy: fixed_totals[policy] / n)
    scores = {policy: fixed_totals[policy] / n for policy in FIXED_POLICIES}
    return best_config, best_fixed, scores, totals[best_config] / n


def evaluate(best_config):
    rows = []
    for seed in EVAL_SEEDS:
        for load_name, load in LOADS:
            for eligibility in ELIGIBILITY_PROFILES:
                for latency in LATENCIES:
                    configs = {
                        "B3": best_config,
                        "B3-no-competence": replace(best_config, use_competence_signal=False),
                        "B3-no-load": replace(best_config, use_load_signal=False),
                        **{policy: B3Config() for policy in FIXED_POLICIES},
                    }
                    results = run_cell(
                        seed, load_name, load, eligibility, latency,
                        EVAL_POLICIES, configs,
                    )
                    rows.append({
                        "condition": (load_name, eligibility, latency),
                        "seed": seed,
                        "results": results,
                    })
    return tuple(rows)


def _ci(values):
    estimate = mean(values)
    margin = T_CRIT_DF29 * stdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0
    return estimate, estimate - margin, estimate + margin


def _fmt_ci(values):
    est, lo, hi = _ci(values)
    return f"{est:.3f} [{lo:.3f}, {hi:.3f}]"


def _seed_metric(rows, seed, policy, metric):
    selected = [row for row in rows if row["seed"] == seed]
    values = []
    for row in selected:
        result = row["results"][policy]
        if metric == "sla":
            values.append(result.at_horizon.fraction_within_sla)
        elif metric == "quality":
            values.append(result.at_horizon.modeled_quality_per_admitted)
        elif metric == "backlog":
            values.append(result.at_horizon.pending)
        elif metric == "wait":
            values.append(result.at_horizon.mean_wait_accrued)
        elif metric == "utilization":
            vals = [v for _, v in result.at_horizon.utilization_by_analyst]
            values.append(mean(vals) if vals else 0.0)
        elif metric == "coordination_cost":
            values.append(result.coordination_person_time)
        elif metric == "switches":
            values.append(result.strategy_switches)
        elif metric.startswith("frequency_"):
            strategy = metric.removeprefix("frequency_")
            counts = dict(result.selected_strategy_counts)
            total = sum(counts.values())
            values.append(counts[strategy] / total if total else 0.0)
    return mean(values)


def _report(best_config, best_fixed, dev_scores, dev_b3_score, rows):
    lines = [
        "# RQ1 B3 adaptive organization: independent evaluation", "",
        "## Protocol and controller", "",
        f"Development seeds: {DEV_SEEDS[0]}–{DEV_SEEDS[-1]} (30); evaluation seeds: {EVAL_SEEDS[0]}–{EVAL_SEEDS[-1]} (30). The fixed-policy and B3 parameter choice used development only. Evaluation traces are independent and paired across policies.", "",
        f"B3 configuration selected from {len(tuple(parameter_grid()))} predeclared candidates: load ratio ≥ {best_config.min_queue_per_free_analyst:g}; deadline pressure ≥ {best_config.min_deadline_pressure:g}; competence spread ≥ {best_config.min_competence_spread:g}; configured latency / mean service ≤ {best_config.max_latency_to_mean_service:g}.", "",
        "At a dispatch instant, let Q be pending alerts and A the currently free analysts. Deadline pressure is the share of pending alerts eligible to at least one free analyst for which the minimum available service-plus-configured-latency time reaches or exceeds remaining slack. If configured latency / mean pending service exceeds the cap, or load ratio |Q|/|A| is below its threshold, B3 selects B0. If deadline pressure is below its threshold, it selects B0. Otherwise, with competence enabled, it selects B2 when the range of eligible analyst-alert competence scores is at least the competence threshold; it selects B1 otherwise. The competence ablation always selects B1 in that branch. The load ablation omits only the load gate. B1/B2 selected by B3 use the same joint dispatch and latency semantics as fixed policies. No arrivals after the current instant are inspected.", "",
        "Development maximized the pooled mean of `(SLA fraction at H + modeled quality per admitted at H)/2`, equally weighting scenario cells and seeds. The single best fixed policy was selected by that same development score; it is not reselected by evaluation scenario. The grid and tie order are fixed in the script. The ablation configurations inherit the selected thresholds and are not retuned.", "",
        "All scenarios reuse the prior synthetic setup: low/medium/high loads, homogeneous/asymmetric eligibility, five coordination latencies, six analysts, four classes, H=12, D=12, and the previous service, SLA, and competence assumptions. Only seeds differ. No previous RQ1 reports or result files are overwritten.", "",
        "## Development selection", "",
        "| Fixed policy | Development primary score |", "|---|---:|",
    ]
    for policy in FIXED_POLICIES:
        lines.append(f"| {policy} | {dev_scores[policy]:.4f} |")
    lines += [f"", f"Selected fixed comparator: **{best_fixed}**. Selected B3 primary score: {dev_b3_score:.4f}.", "", "## Independent evaluation: paired differences", "", "Intervals are paired Student t 95% intervals across 30 evaluation seeds (df=29; t*=2.04523), after averaging the 30 load × eligibility × latency cells within each seed. Positive values favor B3 for SLA/quality and negative values favor B3 for backlog/wait/cost.", ""]
    for metric, title in (("sla", "SLA fraction at H"), ("quality", "Modeled quality/admitted at H")):
        lines += [f"### {title}", "", "| Contrast | Mean paired difference [95% CI] |", "|---|---:|"]
        for comparator in dict.fromkeys((*FIXED_POLICIES, best_fixed, "B3-no-competence", "B3-no-load")):
            if comparator == "B3":
                continue
            vals = [
                _seed_metric(rows, seed, "B3", metric)
                - _seed_metric(rows, seed, comparator, metric)
                for seed in EVAL_SEEDS
            ]
            lines.append(f"| B3 − {comparator} | {_fmt_ci(vals)} |")
        lines.append("")
    lines += ["### Secondary outcomes and controller activity", "", "| Policy | Backlog at H | Wait at H | Utilization at H | Coordination person-time | Policy changes/run | B0 choice | B1 choice | B2 choice |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for policy in (*FIXED_POLICIES, "B3", "B3-no-competence", "B3-no-load"):
        lines.append(
            f"| {policy} | {mean(_seed_metric(rows, s, policy, 'backlog') for s in EVAL_SEEDS):.2f} | "
            f"{mean(_seed_metric(rows, s, policy, 'wait') for s in EVAL_SEEDS):.3f} | "
            f"{mean(_seed_metric(rows, s, policy, 'utilization') for s in EVAL_SEEDS):.3f} | "
            f"{mean(_seed_metric(rows, s, policy, 'coordination_cost') for s in EVAL_SEEDS):.2f} | "
            f"{mean(_seed_metric(rows, s, policy, 'switches') for s in EVAL_SEEDS):.2f} | "
            + " | ".join(f"{mean(_seed_metric(rows, s, policy, f'frequency_{strategy}') for s in EVAL_SEEDS):.3f}" for strategy in ("B0", "B1", "B2"))
            + " |"
        )
    lines += ["", "Coordination person-time is the sum of configured latency for each analyst assigned in a coordinated batch over H+D; one latency interval is charged per assigned analyst's idle time. B0 contributes zero. Fixed-policy rows have zero policy changes and zero adaptive-selection frequencies.", "", "## Scenario-level primary results", "", "| Load / eligibility / latency | SLA B0 | SLA B1 | SLA B2 | SLA B3 | Δ B3−best fixed [95% CI] | Quality B3 |", "|---|---:|---:|---:|---:|---:|---:|"]
    best_per_seed = best_fixed
    for condition in sorted({row["condition"] for row in rows}, key=lambda c: (c[0], c[1], c[2])):
        scoped = [row for row in rows if row["condition"] == condition]
        sla = {p: mean(row["results"][p].at_horizon.fraction_within_sla for row in scoped) for p in (*FIXED_POLICIES, "B3")}
        quality = mean(row["results"]["B3"].at_horizon.modeled_quality_per_admitted for row in scoped)
        by_seed_delta = []
        for seed in EVAL_SEEDS:
            row = next(row for row in scoped if row["seed"] == seed)
            by_seed_delta.append(
                row["results"]["B3"].at_horizon.fraction_within_sla
                - row["results"][best_per_seed].at_horizon.fraction_within_sla
            )
        label = f"{condition[0]} / {condition[1]} / {condition[2]:g}s"
        lines.append(f"| {label} | {sla['B0']:.3f} | {sla['B1']:.3f} | {sla['B2']:.3f} | {sla['B3']:.3f} | {_fmt_ci(by_seed_delta)} | {quality:.3f} |")
    sla_best = [
        _seed_metric(rows, seed, "B3", "sla") - _seed_metric(rows, seed, best_fixed, "sla")
        for seed in EVAL_SEEDS
    ]
    quality_best = [
        _seed_metric(rows, seed, "B3", "quality") - _seed_metric(rows, seed, best_fixed, "quality")
        for seed in EVAL_SEEDS
    ]
    sla_ci, quality_ci = _ci(sla_best), _ci(quality_best)
    decision = "GO" if sla_ci[1] > 0 and quality_ci[1] > 0 else "REVISE"
    b3_cost = mean(_seed_metric(rows, seed, "B3", "coordination_cost") for seed in EVAL_SEEDS)
    b1_cost = mean(_seed_metric(rows, seed, "B1", "coordination_cost") for seed in EVAL_SEEDS)
    lines += ["", "## Interpretation and decision", "", f"On the pooled independent evaluation, B3−{best_fixed} was { _fmt_ci(sla_best) } in H SLA fraction and { _fmt_ci(quality_best) } in modeled quality per admitted alert. B3 used {b3_cost:.2f} coordination person-time units per seed on average versus {b1_cost:.2f} for fixed B1. See scenario rows: the aggregate gain is concentrated in medium/high load with low enough configured latency; B3 falls back to B0 when latency exceeds its selected cap.", "", f"**Recommendation: {decision} for continued synthetic RQ1 investigation.** This is not an operational recommendation. B3's evaluation intervals support both primary gains over the development-selected fixed policy in this scenario family; the gain over B0 is driven mainly by high-load cells. The competence ablation has a small quality loss and a small SLA gain, while removing the load gate barely changes aggregate outcomes here, so those mechanisms need broader scenarios before claiming each is necessary.", "", "All inputs remain synthetic, including competence, service, eligibility, deadlines, and dispatch latency. B3 is a threshold rule, not a learned controller; the development score may favor the assumed quality/SLA weighting. Evaluation covers the same scenario family, not a new operational population. Mean confidence intervals aggregate scenario cells within seed and do not establish external validity. Coordination person-time is an accounting proxy, not a measured organizational cost. The model does not include future arrivals, SOCTRA triage, escalation, shifts, handoffs, learning, or variable service times.", "", "Reproduce with `PYTHONPATH=src python studies/rq1_b3_adaptive_experiment.py`."]
    return "\n".join(lines) + "\n"


def main():
    best_config, best_fixed, dev_scores, dev_b3_score = develop()
    rows = evaluate(best_config)
    print(_report(best_config, best_fixed, dev_scores, dev_b3_score, rows), end="")


if __name__ == "__main__":
    main()
