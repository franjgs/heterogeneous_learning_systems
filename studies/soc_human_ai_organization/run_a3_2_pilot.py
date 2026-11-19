"""Reproducible, paired exploratory D1/T/Q/C pilot (synthetic demand only)."""
from __future__ import annotations

import csv
from dataclasses import replace
from hashlib import sha256
import json
import random
from pathlib import Path
import statistics
import sys
from time import perf_counter

from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hls.ia_l1_l2_simulation import ScenarioConfig, generate_alerts  # noqa: E402
from hls.rq1_allocation import (  # noqa: E402
    AllocationSession, _dispatch_central_sequential, _dispatch_d1,
    _dispatch_local_competence, _dispatch_local_priority,
)
from hls.rq1_l1_l2 import simulate_l1_l2, stage_metrics_at  # noqa: E402
from calibrate_a1_scenarios import build_scenario, effective_capacity  # noqa: E402
from soc_parametric_baseline import (  # noqa: E402
    BASE_L1_ANALYSTS, BASE_L2_ANALYSTS, BASE_SERVICE_L1_H, BASE_SERVICE_L2_H,
    build_roster,
)

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config" / "a3_2_pilot.json"
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
COMPARISONS = tuple(CONFIG["comparisons"])
POLICIES = tuple(row["label"] for row in COMPARISONS)
HORIZON = float(CONFIG["admission_horizon_h"])
DRAIN = float(CONFIG["drain_h"])
LATENCY = float(CONFIG["coordination_latency_c_h"])
EDGE_COST = float(CONFIG["coordination_edge_cost_c_units"])


def _team(scenario):
    return build_roster(
        BASE_L1_ANALYSTS, BASE_L2_ANALYSTS, float(scenario["eligibility_level"]),
    )


def _roster_for(scenario):
    l1, l2, l1svc, l2svc = _team(scenario)
    if scenario["homogeneous_competence"]:
        from hls.rq1_allocation import Analyst
        l1 = tuple(Analyst(a.analyst_id, a.eligible_classes,
                           {k: 0.8 for k in a.eligible_classes}) for a in l1)
        l2 = tuple(Analyst(a.analyst_id, a.eligible_classes,
                           {k: 0.8 for k in a.eligible_classes}) for a in l2)
    if scenario["homogeneous_speed"]:
        l1svc = {a.analyst_id: {k: BASE_SERVICE_L1_H[k] for k in a.eligible_classes} for a in l1}
        l2svc = {a.analyst_id: {k: BASE_SERVICE_L2_H[k] for k in a.eligible_classes} for a in l2}
    return l1, l2, l1svc, l2svc


def _common_uniform(seed: int, alert_id: str) -> float:
    digest = sha256(f"a3.2:{seed}:{alert_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def _completion_map(result, admitted, cutoff):
    l1_jobs = {job.alert_id: job for job in result.l1_simulation.assignments
               if job.completion <= cutoff}
    l2_jobs = {job.alert_id: job for job in result.l2_simulation.assignments
               if job.completion <= cutoff}
    route = {row.routed.alert.alert_id: bool(row.routed.soctra_recommendation) for row in admitted}
    final = {}
    for row in admitted:
        alert_id = row.routed.alert.alert_id
        l1 = l1_jobs.get(alert_id)
        if l1 is None:
            continue
        final[alert_id] = l2_jobs.get(alert_id) if route[alert_id] else l1
        if final[alert_id] is None:
            del final[alert_id]
    return l1_jobs, l2_jobs, final


def _episode_metrics(scenario, seed, policy, generated, simulation):
    admitted_rows = [row for row in generated if row.routed.alert.arrival < HORIZON]
    alerts = [row.routed.alert for row in admitted_rows]
    h_l1, h_l2, h_final = _completion_map(simulation, admitted_rows, HORIZON)
    d_l1, d_l2, d_final = _completion_map(simulation, admitted_rows, HORIZON + DRAIN)
    terminal_sla = sum(d_final[x.alert_id].completion <= x.deadline for x in alerts if x.alert_id in d_final)
    on_time_final = [x for x in alerts if x.alert_id in d_final and d_final[x.alert_id].completion <= x.deadline]
    quality_values, correct_on_time = [], 0
    row_by_id = {row.routed.alert.alert_id: row for row in admitted_rows}
    for alert in alerts:
        job = d_final.get(alert.alert_id)
        if job is None:
            continue
        row = row_by_id[alert.alert_id]
        probability = max(0.0, min(1.0, job.competence * (1 - 0.35 * row.difficulty)))
        quality_values.append(probability)
        if job.completion <= alert.deadline and _common_uniform(seed, alert.alert_id) < probability:
            correct_on_time += 1
    class_rows = []
    pool_class_rows = []
    for task_class in sorted({x.task_class for x in alerts}):
        group = [x for x in alerts if x.task_class == task_class]
        complete = [x for x in group if x.alert_id in d_final]
        on_time = [x for x in complete if d_final[x.alert_id].completion <= x.deadline]
        probs = [max(0.0, min(1.0, d_final[x.alert_id].competence *
                              (1 - 0.35 * row_by_id[x.alert_id].difficulty))) for x in complete]
        class_rows.append({
            "scenario": scenario["name"], "seed": seed, "policy": policy,
            "task_class": task_class, "admitted": len(group), "completed_after_drain": len(complete),
            "terminal_sla_numerator": len(on_time),
            "terminal_sla_fraction_admitted": len(on_time) / len(group) if group else 0.0,
            "mean_expected_quality_completed": statistics.mean(probs) if probs else None,
        })
        for pool, done_h, done_d, pool_input in (
            ("L1", h_l1, d_l1, group),
            ("L2", h_l2, d_l2, [x for x in group if x.alert_id in d_l1 and
                                  row_by_id[x.alert_id].routed.soctra_recommendation]),
        ):
            pool_jobs = [done_d[x.alert_id] for x in pool_input if x.alert_id in done_d]
            pool_h_jobs = [done_h[x.alert_id] for x in pool_input if x.alert_id in done_h]
            pool_class_rows.append({
                "scenario": scenario["name"], "seed": seed, "policy": policy,
                "pool": pool, "task_class": task_class,
                "pool_input_n": len(pool_input), "completed_by_h": len(pool_h_jobs),
                "completed_after_drain": len(pool_jobs),
                "stage_deadline_fraction_completed": (
                    sum(job.completion <= next(x.deadline for x in pool_input if x.alert_id == job.alert_id)
                        for job in pool_jobs) / len(pool_jobs) if pool_jobs else None
                ),
                "mean_pool_wait_h_completed": (
                    statistics.mean(
                        job.start - (next(x.arrival for x in pool_input if x.alert_id == job.alert_id)
                                     if pool == "L1" else d_l1[job.alert_id].completion)
                        for job in pool_jobs
                    ) if pool_jobs else None
                ),
            })
    n = len(alerts)
    h_completed = len(h_final)
    d_completed = len(d_final)
    l1_util = [value for _, value in stage_metrics_at(simulation.l1_simulation, HORIZON)]
    l2_util = [value for _, value in stage_metrics_at(simulation.l2_simulation, HORIZON)]
    unique_starts_l1 = len({job.start for job in simulation.l1_simulation.assignments})
    unique_starts_l2 = len({job.start for job in simulation.l2_simulation.assignments})
    return {
        "scenario": scenario["name"], "seed": seed, "policy": policy, "admitted": n,
        "sla_h": simulation.at_horizon.fraction_within_sla,
        "sla_terminal": simulation.after_drain.fraction_within_sla,
        "completed_h": h_completed, "completed_after_drain": d_completed,
        "completed_during_drain": d_completed - h_completed,
        "pending_h": simulation.at_horizon.pending,
        "pending_after_drain": simulation.after_drain.pending,
        "late_terminal": simulation.after_drain.completed_late,
        "quality_expected_completed": statistics.mean(quality_values) if quality_values else None,
        "modeled_quality_per_admitted": simulation.after_drain.modeled_quality_per_admitted,
        "correct_and_on_time_per_admitted": correct_on_time / n if n else 0.0,
        "correct_and_on_time_n": correct_on_time,
        "mean_wait_h_terminal": simulation.after_drain.mean_wait_accrued,
        "mean_response_h_terminal_completed": simulation.after_drain.mean_response_completed,
        "l1_utilization_mean": statistics.mean(l1_util) if l1_util else 0.0,
        "l2_utilization_mean": statistics.mean(l2_util) if l2_util else 0.0,
        "l1_completed": len(d_l1), "l2_completed": len(d_l2),
        "l1_decision_epochs": simulation.l1_simulation.dispatch_decisions,
        "l2_decision_epochs": simulation.l2_simulation.dispatch_decisions,
        "coordination_latency_h": simulation.l1_simulation.coordination_latency_total + simulation.l2_simulation.coordination_latency_total,
        "coordination_person_time_h": simulation.coordination_person_time,
        "coordination_resource_units": simulation.l1_simulation.coordination_resource + simulation.l2_simulation.coordination_resource,
        "completed_within_sla_terminal": len(on_time_final),
        "quality_model_label": "expected correctness p=competence*(1-0.35*difficulty); difficulty and competence synthetic",
    }, class_rows, pool_class_rows


def _max_matching_size(free, pending):
    match_alert = {}
    def augment(analyst, seen):
        for alert in pending:
            if alert.task_class not in analyst.eligible_classes or alert.alert_id in seen:
                continue
            seen.add(alert.alert_id)
            if alert.alert_id not in match_alert or augment(match_alert[alert.alert_id], seen):
                match_alert[alert.alert_id] = analyst
                return True
        return False
    return sum(augment(analyst, set()) for analyst in free)


def _d1_trajectory_diagnostics(alerts, analysts, services, individual, *, seed, latency):
    """Same-state counterfactual proposals along a D1 trajectory (not outcomes)."""
    session = AllocationSession(
        alerts, analysts, services, admission_horizon=HORIZON, drain_period=DRAIN,
        random_seed=seed, coordination_latency=latency,
        service_by_analyst_class=individual,
    )
    counts = {name: 0 for name in (
        "dispatch_states", "nontrivial_states", "two_or_more_free",
        "matching_cardinality_ge2", "D1_vs_T", "D1_vs_Q", "D1_vs_C",
        "T_vs_C", "Q_vs_C", "feasible_edges",
    )}
    while not session._finalized:
        event = session.next_event_time()
        if event is None:
            break
        session.advance_to(event)
        if not session.can_dispatch():
            continue
        free, pending = session.available_analysts(), dict(session.pending)
        service = session._service_time
        # Clone the actual RNG state so D1 preview does not change the run.
        preview_rng = random.Random()
        preview_rng.setstate(session.order_rng.getstate())
        d1 = _dispatch_d1(free, pending, session.now, service, preview_rng)
        t = _dispatch_local_priority(free, pending, session.now, service)
        q = _dispatch_local_competence(free, pending, session.now, service)
        c = _dispatch_central_sequential(free, pending, session.now, service, latency)
        pairsets = {name: {(a.analyst_id, x.alert_id) for a, x in pairs}
                    for name, pairs in (("D1", d1), ("T", t), ("Q", q), ("C", c))}
        counts["dispatch_states"] += 1
        edges = sum(x.task_class in a.eligible_classes for a in free for x in pending.values())
        counts["feasible_edges"] += edges
        counts["two_or_more_free"] += len(free) >= 2
        counts["matching_cardinality_ge2"] += _max_matching_size(free, tuple(pending.values())) >= 2
        counts["nontrivial_states"] += len({tuple(sorted(s)) for s in pairsets.values()}) > 1
        for label, left, right in (("D1_vs_T", "D1", "T"), ("D1_vs_Q", "D1", "Q"),
                                   ("D1_vs_C", "D1", "C"), ("T_vs_C", "T", "C"),
                                   ("Q_vs_C", "Q", "C")):
            counts[label] += pairsets[left] != pairsets[right]
        session.dispatch("D1")
    return counts


def _write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _mean_ci(values):
    n = len(values)
    mean = statistics.mean(values) if n else 0.0
    if n < 2:
        return mean, 0.0, mean, mean
    sd = statistics.stdev(values)
    half = float(student_t.ppf(0.975, n - 1)) * sd / n**0.5
    return mean, sd, mean - half, mean + half


def run(output_dir: Path | None = None):
    started = perf_counter()
    out = output_dir or ROOT / CONFIG["output_dir"]
    out.mkdir(parents=True, exist_ok=True)
    config_a1 = json.loads((HERE / "config" / "a1_calibration.json").read_text(encoding="utf-8"))
    episode_rows, class_rows, pool_class_rows, diag_rows = [], [], [], []
    scenario_capacity_rows = []
    for scenario in CONFIG["scenarios"]:
        l1, l2, l1_services, l2_services = _roster_for(scenario)
        class_probs = tuple(scenario.get("class_probabilities", (0.592, 0.236, 0.172)))
        capacity = effective_capacity(l1, l1_services, class_probs)["max_common_arrivals_per_h"]
        rate = float(scenario["rho_l1"]) * float(capacity)
        cfg = build_scenario(config_a1, rate=rate,
                             deadline_multiplier=float(scenario["deadline_multiplier"]))
        # Require explicit common trace parameters across policies.
        cfg = replace(cfg, horizon=HORIZON, class_probabilities=class_probs)
        scenario_capacity_rows.append({"scenario": scenario["name"], "rho_l1": scenario["rho_l1"],
                                       "class_probabilities": class_probs,
                                       "fluid_capacity_l1_per_h": capacity,
                                       "arrival_rate_per_h": rate})
        for offset in range(int(CONFIG["seed_count"])):
            seed = int(CONFIG["seed_base"]) + offset
            generated = generate_alerts(cfg, seed)
            routed = tuple(row.routed for row in generated)
            diag_rows.append({"scenario": scenario["name"], "seed": seed,
                              **_d1_trajectory_diagnostics(
                                  [row.alert for row in routed], l1,
                                  BASE_SERVICE_L1_H,
                                  l1_services, seed=seed, latency=LATENCY,
                              )})
            for comparison in COMPARISONS:
                policy = comparison["policy"]
                label = comparison["label"]
                result = simulate_l1_l2(
                    routed, l1, l2,
                    BASE_SERVICE_L1_H,
                    BASE_SERVICE_L2_H,
                    policy=policy, admission_horizon=HORIZON, drain_period=DRAIN,
                    coordination_latency=float(comparison["coordination_latency_h"]),
                    coordination_edge_cost=float(comparison["coordination_edge_cost_units"]),
                    decision_mode="hypothetical_recommendation_acceptance",
                    random_seed=seed,
                    l1_service_by_analyst_class=l1_services,
                    l2_service_by_analyst_class=l2_services,
                )
                summary, by_class, by_pool_class = _episode_metrics(scenario, seed, label, generated, result)
                episode_rows.append(summary)
                class_rows.extend(by_class)
                pool_class_rows.extend(by_pool_class)
    _write_csv(out / "episode_metrics.csv", episode_rows)
    _write_csv(out / "class_metrics.csv", class_rows)
    _write_csv(out / "pool_class_metrics.csv", pool_class_rows)
    _write_csv(out / "d1_trajectory_decision_diagnostics.csv", diag_rows)
    metrics = ("sla_h", "sla_terminal", "quality_expected_completed",
               "correct_and_on_time_per_admitted", "mean_wait_h_terminal",
               "mean_response_h_terminal_completed", "modeled_quality_per_admitted",
               "l1_utilization_mean", "l2_utilization_mean", "pending_h",
               "pending_after_drain", "completed_during_drain", "l1_completed",
               "l2_completed", "l1_decision_epochs", "l2_decision_epochs",
               "coordination_latency_h", "coordination_person_time_h",
               "coordination_resource_units")
    summary_rows, paired_rows = [], []
    for scenario in CONFIG["scenarios"]:
        scenario_name = scenario["name"]
        for metric in metrics:
            groups = {policy: [r[metric] for r in episode_rows
                              if r["scenario"] == scenario_name and r["policy"] == policy
                              and r[metric] is not None] for policy in POLICIES}
            for policy, values in groups.items():
                mean, sd, low, high = _mean_ci(values)
                summary_rows.append({"scenario": scenario_name, "metric": metric,
                                     "policy": policy, "n": len(values), "mean": mean,
                                     "sd": sd, "ci95_low": low, "ci95_high": high})
                if policy == "D1":
                    continue
                d1_values = {r["seed"]: r[metric] for r in episode_rows
                             if r["scenario"] == scenario_name and r["policy"] == "D1"}
                policy_values = {r["seed"]: r[metric] for r in episode_rows
                                 if r["scenario"] == scenario_name and r["policy"] == policy}
                diffs = [policy_values[s] - d1_values[s] for s in sorted(d1_values)
                         if s in policy_values and policy_values[s] is not None and d1_values[s] is not None]
                mean, sd, low, high = _mean_ci(diffs)
                paired_rows.append({"scenario": scenario_name, "metric": metric,
                                    "comparison": f"{policy}-D1", "n_pairs": len(diffs),
                                    "mean_difference": mean, "sd_difference": sd,
                                    "ci95_low": low, "ci95_high": high,
                                    "episodes_improved": sum(x > 0 for x in diffs),
                                    "episodes_worse": sum(x < 0 for x in diffs),
                                    "episodes_tied": sum(x == 0 for x in diffs)})
            zero_values = {r["seed"]: r[metric] for r in episode_rows
                           if r["scenario"] == scenario_name and r["policy"] == "C_zero_latency"}
            charged_values = {r["seed"]: r[metric] for r in episode_rows
                              if r["scenario"] == scenario_name and r["policy"] == "C"}
            c_diffs = [charged_values[s] - zero_values[s] for s in sorted(zero_values)
                       if s in charged_values and charged_values[s] is not None and zero_values[s] is not None]
            mean, sd, low, high = _mean_ci(c_diffs)
            paired_rows.append({"scenario": scenario_name, "metric": metric,
                                "comparison": "C-C_zero_latency", "n_pairs": len(c_diffs),
                                "mean_difference": mean, "sd_difference": sd,
                                "ci95_low": low, "ci95_high": high,
                                "episodes_improved": sum(x > 0 for x in c_diffs),
                                "episodes_worse": sum(x < 0 for x in c_diffs),
                                "episodes_tied": sum(x == 0 for x in c_diffs)})
    _write_csv(out / "scenario_policy_summary.csv", summary_rows)
    _write_csv(out / "paired_differences.csv", paired_rows)
    (out / "run_metadata.json").write_text(json.dumps({
        "config": CONFIG, "source_config": str(CONFIG_PATH.relative_to(ROOT)),
        "generated_episodes": len(episode_rows), "paired_trace_count": len(diag_rows),
        "runtime_seconds": round(perf_counter() - started, 3),
        "scenario_capacity": scenario_capacity_rows,
        "classification": "exploratory pilot; not confirmatory; synthetic inputs only",
    }, indent=2) + "\n", encoding="utf-8")
    return out, episode_rows, summary_rows, paired_rows, diag_rows


if __name__ == "__main__":
    output, episodes, summary, paired, diagnostics = run()
    print(f"output={output}")
    print(f"episodes={len(episodes)} paired_diagnostics={len(diagnostics)}")
    shown_metrics = {"sla_h", "sla_terminal", "quality_expected_completed",
                     "correct_and_on_time_per_admitted", "mean_wait_h_terminal"}
    for row in summary:
        if row["metric"] in shown_metrics:
            print("MEAN", row["scenario"], row["metric"], row["policy"],
                  round(row["mean"], 5), round(row["ci95_low"], 5), round(row["ci95_high"], 5))
    for row in paired:
        if row["metric"] in {"sla_terminal", "correct_and_on_time_per_admitted"}:
            print("PAIRED", row["scenario"], row["metric"], row["comparison"],
                  round(row["mean_difference"], 5), round(row["ci95_low"], 5),
                  round(row["ci95_high"], 5), row["episodes_improved"], row["episodes_worse"])
