"""Analytical and paired synthetic phase-two SOCTRA–HLS evaluation.

Classifier rates come from published aggregate operating points only. No
individual alert records, model predictions, or classifier training are used.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from hls.ia_l1_l2_simulation import generate_alerts  # noqa: E402
from hls.rq1_allocation import HLSBConfig  # noqa: E402
from hls.rq1_l1_l2 import simulate_l1_l2  # noqa: E402
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity  # noqa: E402
from studies.soc_human_ai_organization.soc_parametric_baseline import (  # noqa: E402
    BASE_DEADLINES_H, BASE_ELIGIBILITY, BASE_L1_ANALYSTS, BASE_L2_ANALYSTS,
    BASE_SERVICE_L1_H, BASE_SERVICE_L2_H, PROJECTS, PROJECT_MIX, REFERENCE,
    build_roster,
)
from studies.soc_triage_organization_coupling import run_pilot as frozen_pilot  # noqa: E402

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config" / "phase2.json").read_text(encoding="utf-8"))
POINTS_SPEC = json.loads((HERE / "config" / "classifier_points.json").read_text(encoding="utf-8"))
OUT = ROOT / "results" / "soc_triage_classifier_operating_impact"
POLICIES = tuple(CONFIG["simulation"]["policies"])
SELECTED = {k: set(v) for k, v in CONFIG["simulation_selection"].items()}


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _prevalences() -> list[dict]:
    out = []
    for name, spec in CONFIG["prevalence_scenarios"].items():
        pi = float(spec["pi"])
        out.append({
            "name": name,
            "label_definition": spec["label_definition"],
            "pi": pi,
            "need_by_class": tuple(pi for _ in PROJECTS),
            "definition": spec["definition"],
        })
    return out


def _points() -> list[dict]:
    rows = []
    for raw in POINTS_SPEC["points"]:
        pd_, pfa = float(raw["pD"]), float(raw["pFA"])
        ba_calc = ((1.0 - pfa) + pd_) / 2.0
        # Costs normalized to sum to one: symmetric (.5,.5); asymmetric (.25,.75).
        benefit_sym = 1.0 - (0.5 * pfa + 0.5 * (1.0 - pd_))
        benefit_asym = 1.0 - (0.25 * pfa + 0.75 * (1.0 - pd_))
        if abs(ba_calc - float(raw["BA_published"])) > 0.00011:
            raise AssertionError(f"published BA check failed for {raw['id']}: {ba_calc}")
        rows.append({
            **raw,
            "pD": pd_, "pFA": pfa,
            "BA_recomputed": ba_calc,
            "normalized_bayes_benefit_symmetric_derived": benefit_sym,
            "normalized_bayes_benefit_cM3cFA_derived": benefit_asym,
            "published_cost_stratum": "not separated by the cited operating-point tables",
            "provenance": f"AIAI 2026 Table {raw['table']}; aggregate published pD/pFA, synthetic Bernoulli recommendation generation",
        })
    return rows


def _is_dominated(point: dict, pool: list[dict]) -> bool:
    return any(
        other["pD"] >= point["pD"] and other["pFA"] <= point["pFA"]
        and (other["pD"] > point["pD"] or other["pFA"] < point["pFA"])
        for other in pool if other["id"] != point["id"]
    )


def _statistical_pareto(points: list[dict]) -> list[dict]:
    result = []
    for label in ("original", "standardized"):
        pool = [p for p in points if p["label_definition"] == label]
        for p in pool:
            result.append({
                "id": p["id"], "label_definition": label, "table": p["table"],
                "algorithm": p["algorithm"], "features": p["features"],
                "pD": p["pD"], "pFA": p["pFA"], "BA_published": p["BA_published"],
                "dominated": _is_dominated(p, pool),
                "frontier_rule": "maximize pD and minimize pFA within label definition only",
            })
    return result


def _service_means(l2, service) -> dict[str, float]:
    means = {}
    for task_class in PROJECTS:
        eligible = [a for a in l2 if task_class in a.eligible_classes]
        means[task_class] = statistics.mean(service[a.analyst_id][task_class] for a in eligible)
    return means


def analytical_workload(points: list[dict], prevalences: list[dict]) -> tuple[list[dict], list[dict]]:
    rows = []
    frontiers = []
    for prev in prevalences:
        for n_l2 in CONFIG["simulation"]["l2_analyst_counts"]:
            l1, l2, l1_s, l2_s = build_roster(
                n_l1=BASE_L1_ANALYSTS, n_l2=int(n_l2),
                mean_eligible_projects=BASE_ELIGIBILITY,
            )
            mu_l1 = effective_capacity(l1, l1_s, PROJECT_MIX)["max_common_arrivals_per_h"]
            service_mean = _service_means(l2, l2_s)
            for point in points:
                if point["label_definition"] != prev["label_definition"]:
                    continue
                q, mix = frozen_pilot._expected_route_mix(prev["need_by_class"], point["pD"], point["pFA"])
                mu_l2 = effective_capacity(l2, l2_s, mix)["max_common_arrivals_per_h"]
                mean_l2_task_h = sum(w * service_mean[k] for w, k in zip(mix, PROJECTS))
                for rho in CONFIG["simulation"]["rho_l1"]:
                    lam = mu_l1 * float(rho)
                    tp_rate = lam * prev["pi"] * point["pD"]
                    fn_rate = lam * prev["pi"] * (1.0 - point["pD"])
                    fp_rate = lam * (1.0 - prev["pi"]) * point["pFA"]
                    tn_rate = lam * (1.0 - prev["pi"]) * (1.0 - point["pFA"])
                    q_by_1000 = q * 1000.0
                    rows.append({
                        "label_definition": prev["label_definition"], "prevalence_scenario": prev["name"],
                        "pi": prev["pi"], "prevalence_definition": prev["definition"],
                        "classifier_id": point["id"], "table": point["table"], "algorithm": point["algorithm"],
                        "features": point["features"], "pD": point["pD"], "pFA": point["pFA"],
                        "BA_published": point["BA_published"], "rho_L1": rho, "lambda_L1_per_h": lam,
                        "n_L2": n_l2, "mu_L1_effective_per_h": mu_l1, "mu_L2_effective_per_h": mu_l2,
                        "recommendation_fraction_q": q, "recommendations_per_1000": q_by_1000,
                        "TP_per_1000": 1000.0 * prev["pi"] * point["pD"],
                        "FP_per_1000": 1000.0 * (1.0-prev["pi"]) * point["pFA"],
                        "FN_per_1000": 1000.0 * prev["pi"] * (1.0-point["pD"]),
                        "TN_per_1000": 1000.0 * (1.0-prev["pi"]) * (1.0-point["pFA"]),
                        "necessary_recommendation_rate_TP_per_h": tp_rate,
                        "false_positive_rate_FP_per_h": fp_rate,
                        "omitted_need_rate_FN_per_h": fn_rate,
                        "l2_offered_rate_recommendations_per_h": lam*q,
                        "rho_L2_offered": lam*q/mu_l2,
                        "mean_L2_task_service_h": mean_l2_task_h,
                        "L2_necessary_TP_work_offered_h_per_h": tp_rate * mean_l2_task_h,
                        "L2_unnecessary_FP_work_offered_h_per_h": fp_rate * mean_l2_task_h,
                        "L2_necessary_FN_work_omitted_h_per_h": fn_rate * mean_l2_task_h,
                        "L2_total_recommended_work_offered_h_per_h": (tp_rate+fp_rate) * mean_l2_task_h,
                        "positive_recommendation_class_mix": json.dumps(mix, separators=(",", ":")),
                        "operating_point_provenance": point["provenance"],
                    })
            # pFA frontiers with composition-specific capacity; use all fixed pD values in the class.
            for pd_value in sorted({p["pD"] for p in points if p["label_definition"] == prev["label_definition"]}):
                for rho in CONFIG["simulation"]["rho_l1"]:
                    for target in (0.50, 0.80, 1.00, 1.20):
                        def val(pfa):
                            q0, mix0 = frozen_pilot._expected_route_mix(prev["need_by_class"], pd_value, pfa)
                            mu0 = effective_capacity(l2, l2_s, mix0)["max_common_arrivals_per_h"]
                            return mu_l1 * float(rho) * q0 / mu0, q0, mu0
                        low, high = 0.0, 1.0
                        if val(low)[0] > target or val(high)[0] < target:
                            pfa_star = None
                        else:
                            for _ in range(64):
                                mid = (low+high)/2
                                if val(mid)[0] < target: low = mid
                                else: high = mid
                            pfa_star = (low+high)/2
                        if pfa_star is None:
                            q_star = mu_star = float("nan")
                        else:
                            _, q_star, mu_star = val(pfa_star)
                        frontiers.append({
                            "label_definition": prev["label_definition"], "prevalence_scenario": prev["name"],
                            "pi": prev["pi"], "pD_fixed": pd_value, "rho_L1": rho, "n_L2": n_l2,
                            "rho_L2_boundary": target, "pFA_at_boundary": pfa_star,
                            "q_at_boundary": q_star, "mu_L2_effective_per_h": mu_star,
                            "interpretation": "fluid offered-load marker; not an empirically validated SLA threshold",
                        })
    return rows, frontiers


def _trace_hash(rows, recommendation=True):
    return frozen_pilot._trace_hash(rows, include_recommendation=recommendation)


def _run_one(trace, point, prev, rho, n_l2, policy, seed):
    l1, l2, l1_s, l2_s = build_roster(
        n_l1=BASE_L1_ANALYSTS, n_l2=int(n_l2), mean_eligible_projects=BASE_ELIGIBILITY,
    )
    q, mix = frozen_pilot._expected_route_mix(prev["need_by_class"], point["pD"], point["pFA"])
    mu_l1 = effective_capacity(l1, l1_s, PROJECT_MIX)["max_common_arrivals_per_h"]
    mu_l2 = effective_capacity(l2, l2_s, mix)["max_common_arrivals_per_h"]
    l2_work = _service_means(l2, l2_s)
    h = float(CONFIG["simulation"]["horizon_h"])
    drain = float(CONFIG["simulation"]["drain_h"])
    kwargs = dict(
        policy=policy, admission_horizon=h, drain_period=drain,
        coordination_latency=0.0, coordination_edge_cost=0.0,
        decision_mode="hypothetical_recommendation_acceptance", random_seed=seed,
        l1_service_by_analyst_class=l1_s, l2_service_by_analyst_class=l2_s,
    )
    if policy == "HLS-B":
        hcfg = CONFIG["simulation"]["hlsb"]
        kwargs["hlsb_l1_config"] = HLSBConfig(**hcfg, capacity_per_h=mu_l1)
        kwargs["hlsb_l2_config"] = HLSBConfig(**hcfg, capacity_per_h=mu_l2)
    sim = simulate_l1_l2(tuple(r.routed for r in trace), l1, l2,
        BASE_SERVICE_L1_H, BASE_SERVICE_L2_H, **kwargs)
    metrics, switches = frozen_pilot._metrics(trace, sim, horizon=h, drain=drain, need_work=l2_work)

    admitted = [r for r in trace if r.routed.alert.arrival < h]
    l1_jobs = {job.alert_id: job for job in sim.l1_simulation.assignments}
    l2_jobs = {job.alert_id: job for job in sim.l2_simulation.assignments}
    routes = {r.alert_id: bool(r.scenario_routing_decision) for r in sim.escalation_records}
    records = {r.routed.alert.alert_id: r for r in admitted}
    cutoff = h + drain
    needed = [r for r in admitted if bool(r.true_escalation_need)]
    need_n = len(needed)
    tp_n = sum(bool(r.true_escalation_need) and routes[r.routed.alert.alert_id] for r in admitted)
    fn_n = need_n - tp_n
    tp_timely = 0
    tp_completed = 0
    for r in needed:
        aid = r.routed.alert.alert_id
        if not routes[aid]:
            continue
        job = l2_jobs.get(aid)
        if job and job.completion <= cutoff: tp_completed += 1
        if job and job.completion <= cutoff and job.completion <= r.routed.alert.deadline:
            tp_timely += 1
    false_positive_ids = {r.routed.alert.alert_id for r in admitted
                          if not r.true_escalation_need and routes[r.routed.alert.alert_id]}
    true_positive_ids = {r.routed.alert.alert_id for r in admitted
                         if r.true_escalation_need and routes[r.routed.alert.alert_id]}
    l2_generated = {aid for aid, yes in routes.items()
                    if yes and aid in l1_jobs and l1_jobs[aid].completion < cutoff}
    fp_generated = false_positive_ids & l2_generated
    tp_generated = true_positive_ids & l2_generated
    fp_nominal = sum(l2_work[records[aid].routed.alert.task_class] for aid in false_positive_ids)
    tp_nominal = sum(l2_work[records[aid].routed.alert.task_class] for aid in true_positive_ids)
    fn_nominal = sum(l2_work[r.routed.alert.task_class] for r in admitted
                     if r.true_escalation_need and not routes[r.routed.alert.alert_id])
    fp_generated_nominal = sum(l2_work[records[aid].routed.alert.task_class] for aid in fp_generated)
    tp_generated_nominal = sum(l2_work[records[aid].routed.alert.task_class] for aid in tp_generated)
    fp_executed = tp_executed = 0.0
    for aid, job in l2_jobs.items():
        used = max(0.0, min(job.completion, cutoff) - job.start)
        if aid in false_positive_ids: fp_executed += used
        elif aid in true_positive_ids: tp_executed += used

    n = len(admitted)
    extra = {
        "true_need_count": need_n,
        "TP_count": tp_n,
        "FN_count": fn_n,
        "necessary_L2_detection_fraction": tp_n / need_n if need_n else 0.0,
        "necessary_L2_completed_per_need": tp_completed / need_n if need_n else 0.0,
        "necessary_L2_timely_per_need": tp_timely / need_n if need_n else 0.0,
        "necessary_L2_timely_given_TP": tp_timely / tp_n if tp_n else 0.0,
        "FP_recommended_count": len(false_positive_ids),
        "FP_L2_tasks_generated_by_terminal": len(fp_generated),
        "TP_L2_tasks_generated_by_terminal": len(tp_generated),
        "FP_L2_work_nominal_offered_h": fp_nominal,
        "TP_L2_work_nominal_offered_h": tp_nominal,
        "FN_L2_work_nominal_omitted_h": fn_nominal,
        "FP_L2_work_nominal_generated_by_terminal_h": fp_generated_nominal,
        "TP_L2_work_nominal_generated_by_terminal_h": tp_generated_nominal,
        "FP_L2_service_hours_executed_by_terminal": fp_executed,
        "TP_L2_service_hours_executed_by_terminal": tp_executed,
        "positive_recommendation_class_mix": json.dumps(mix, separators=(",", ":")),
        "n_L2": int(n_l2),
        "mu_L2_effective_per_h": mu_l2,
        "rho_L2_offered_analytic": (mu_l1 * rho * q / mu_l2) if mu_l2 else 0.0,
    }
    row = {
        "label_definition": prev["label_definition"], "prevalence_scenario": prev["name"],
        "pi": prev["pi"], "classifier_id": point["id"], "table": point["table"],
        "algorithm": point["algorithm"], "features": point["features"],
        "pD_target": point["pD"], "pFA_target": point["pFA"], "BA_published": point["BA_published"],
        "rho_L1": float(rho), "lambda_L1_per_h": mu_l1 * float(rho),
        "seed": int(seed), "policy": policy,
        **metrics, **extra,
        "exogenous_sha256": _trace_hash(trace, recommendation=False),
        "trace_sha256": _trace_hash(trace, recommendation=True),
        "trace_alert_count": len(trace), "terminal_cutoff_h": cutoff,
        "max_deadline_h": max((r.routed.alert.deadline for r in trace), default=0.0),
    }
    return row, switches


def run() -> dict:
    points = _points()
    prevalences = _prevalences()
    analysis, frontiers = analytical_workload(points, prevalences)
    _write_csv(OUT / "all_published_operating_points.csv", points)
    _write_csv(OUT / "statistical_pareto.csv", _statistical_pareto(points))
    _write_csv(OUT / "analytic_load_by_point.csv", analysis)
    _write_csv(OUT / "analytic_l2_frontiers.csv", frontiers)

    rows, triage, switches = [], [], []
    exogenous_counts = set()
    for prev in prevalences:
        for rho in CONFIG["simulation"]["rho_l1"]:
            for seed in range(int(CONFIG["simulation"]["seed_base"]),
                              int(CONFIG["simulation"]["seed_base"])+int(CONFIG["simulation"]["n_seeds"])):
                points_for_label = [p for p in points if p["label_definition"] == prev["label_definition"]
                                    and p["id"] in SELECTED[prev["label_definition"]]]
                base_trace = None
                for point in points_for_label:
                    trace, _ = frozen_pilot._make_trace(
                        rho_l1=float(rho), seed=seed, prevalence=prev, point=point,
                    )
                    if base_trace is None: base_trace = trace
                    if _trace_hash(trace, recommendation=False) != _trace_hash(base_trace, recommendation=False):
                        raise AssertionError("classifier points do not share the same exogenous trace")
                    exogenous_counts.add((prev["name"], float(rho), seed, _trace_hash(trace, recommendation=False)))
                    needed = sum(x.true_escalation_need for x in trace)
                    tp = sum(x.true_escalation_need and bool(x.routed.soctra_recommendation) for x in trace)
                    fn = needed - tp
                    fp = sum((not x.true_escalation_need) and bool(x.routed.soctra_recommendation) for x in trace)
                    tn = len(trace)-needed-fp
                    triage.append({
                        "label_definition": prev["label_definition"], "prevalence_scenario": prev["name"],
                        "pi": prev["pi"], "classifier_id": point["id"], "table": point["table"],
                        "algorithm": point["algorithm"], "features": point["features"],
                        "pD_target": point["pD"], "pFA_target": point["pFA"], "BA_published": point["BA_published"],
                        "rho_L1": float(rho), "seed": seed, "alert_count": len(trace),
                        "need_positive_count": needed, "TP": tp, "FP": fp, "FN": fn, "TN": tn,
                        "pD_realized": tp/needed if needed else 0.0,
                        "pFA_realized": fp/(len(trace)-needed) if len(trace)>needed else 0.0,
                        "recommendations_positive": tp+fp,
                        "recommendation_fraction_realized": (tp+fp)/len(trace) if trace else 0.0,
                        "exogenous_sha256": _trace_hash(trace, recommendation=False),
                        "trace_sha256": _trace_hash(trace, recommendation=True),
                    })
                    for n_l2 in CONFIG["simulation"]["l2_analyst_counts"]:
                        for policy in POLICIES:
                            result, mode_rows = _run_one(trace, point, prev, float(rho), int(n_l2), policy, seed)
                            rows.append(result)
                            switches.extend({**m, "seed": seed, "classifier_id": point["id"],
                                "label_definition": prev["label_definition"],
                                "prevalence_scenario": prev["name"], "rho_L1": float(rho),
                                "n_L2": int(n_l2), "policy": policy} for m in mode_rows)

    expected_configs = sum(len(SELECTED[p["label_definition"]]) for p in prevalences) * len(CONFIG["simulation"]["rho_l1"]) * len(CONFIG["simulation"]["l2_analyst_counts"])
    expected_episodes = expected_configs * int(CONFIG["simulation"]["n_seeds"]) * len(POLICIES)
    if len(rows) != expected_episodes:
        raise AssertionError(f"episode count {len(rows)} != planned {expected_episodes}")
    # All policies in a matched cell must see identical trace hashes/denominators and classifier outcomes.
    by_policy_key = {}
    for row in rows:
        key = (row["label_definition"], row["prevalence_scenario"], row["classifier_id"], row["rho_L1"],
               row["n_L2"], row["seed"])
        by_policy_key.setdefault(key, []).append(row)
    if any(len({x["exogenous_sha256"] for x in g}) != 1 or len({x["trace_sha256"] for x in g}) != 1
           or len({x["admitted"] for x in g}) != 1 or len({(x["TP"],x["FP"],x["FN"],x["TN"]) for x in g}) != 1
           for g in by_policy_key.values()):
        raise AssertionError("policy/denominator/confusion mismatch on paired traces")
    if any(r["correct_on_time_expected_per_admitted"] > r["required_resolution_SLA_terminal"] + 1e-12 for r in rows):
        raise AssertionError("integrated correct-on-time score exceeds route-qualified SLA fraction")
    _write_csv(OUT / "episodes.csv", rows)
    _write_csv(OUT / "triage_by_seed.csv", triage)
    _write_csv(OUT / "waps_switches.csv", switches or [{"note":"no mode switches in selected cells"}])
    checks = {
        "published_operating_points": len(points), "original_points": sum(p["label_definition"]=="original" for p in points),
        "standardized_points": sum(p["label_definition"]=="standardized" for p in points),
        "selected_original_points": len(SELECTED["original"]), "selected_standardized_points": len(SELECTED["standardized"]),
        "expected_conditions": expected_configs, "expected_episode_rows": expected_episodes,
        "actual_episode_rows": len(rows), "actual_triage_rows": len(triage),
        "paired_policy_cells": len(by_policy_key),
        "same_exogenous_trace_across_classifier_points": True,
        "same_trace_and_denominator_across_policies": True,
        "same_confusion_counts_across_policies": True,
        "no_policy_receives_hidden_need": True,
        "false_negative_credit_gated_by_integrated_metric": True,
        "all_deadlines_mature_before_terminal_cutoff": all(r["max_deadline_h"] <= r["terminal_cutoff_h"] for r in rows),
        "published_BA_recomputed_within_rounding": True,
        "unique_exogenous_trace_seeds": len(exogenous_counts),
        "n_seeds": int(CONFIG["simulation"]["n_seeds"]),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "validation_checks.json").write_text(json.dumps(checks, indent=2)+"\n", encoding="utf-8")
    metadata = {
        "configuration": CONFIG,
        "source": POINTS_SPEC["source"],
        "selected_classifier_ids": {k: sorted(v) for k,v in SELECTED.items()},
        "source_commit": CONFIG["reference_pilot_commit"],
        "generated_episode_rows": len(rows), "generated_triage_rows": len(triage),
        "seed_ids": list(range(int(CONFIG["simulation"]["seed_base"]),
                               int(CONFIG["simulation"]["seed_base"])+int(CONFIG["simulation"]["n_seeds"]))),
        "checks": checks,
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print(f"Wrote {len(points)} published points, {len(rows)} policy episodes and {len(triage)} trace/triage rows")
    return {"points": points, "analysis": analysis, "episodes": rows, "triage": triage}


if __name__ == "__main__":
    run()
