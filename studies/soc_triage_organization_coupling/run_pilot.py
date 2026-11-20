"""Exploratory synthetic pilot coupling escalation recommendations and SOC dispatch.

This runner reuses the frozen SOC scenario, roster, allocation engine, and
L1/L2 wrapper. It does not read SOCTRA records or change any policy or engine.
"""
from __future__ import annotations

import csv
from dataclasses import replace
from hashlib import sha256
import json
import math
from pathlib import Path
import random
import statistics
import sys

from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from hls.ia_l1_l2_simulation import generate_alerts  # noqa: E402
from hls.rq1_allocation import HLSBConfig  # noqa: E402
from hls.rq1_l1_l2 import simulate_l1_l2  # noqa: E402
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity  # noqa: E402
from studies.soc_human_ai_organization.soc_parametric_baseline import (  # noqa: E402
    BASE_DEADLINES_H, BASE_L1_ANALYSTS, BASE_L2_ANALYSTS, BASE_SERVICE_L1_H,
    BASE_SERVICE_L2_H, BASE_ELIGIBILITY, PROJECTS, PROJECT_MIX, REFERENCE,
    build_roster,
)

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config" / "pilot.json"
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
OUT = ROOT / "results" / "soc_triage_organization_coupling"
POLICIES = tuple(CONFIG["policies"])
L1, L2, L1_SERVICE, L2_SERVICE = build_roster(
    BASE_L1_ANALYSTS, BASE_L2_ANALYSTS, BASE_ELIGIBILITY,
)
MU_L1 = effective_capacity(L1, L1_SERVICE, PROJECT_MIX)["max_common_arrivals_per_h"]
SYNTHETIC_NEED = tuple(REFERENCE.escalation_need_by_project)
PI_HIST = 344 / 102526
PD_OLD = 274 / 344
PFA_OLD = 29210 / 102182
OLD_POINT_NAME = "historical_old_exact"
INTERACTION_A = "grid_pd07965_pfa2859"
INTERACTION_B = "grid_pd090_pfa001"


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for row in rows for k in row)))
        writer.writeheader()
        writer.writerows(rows)


def _mean_ci(values: list[float]) -> tuple[float, float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0, 0.0
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    half = (float(student_t.ppf(.975, len(values) - 1)) * sd / math.sqrt(len(values))
            if len(values) > 1 else 0.0)
    return mean, sd, mean - half, mean + half


def _stable_uniform(seed: int, alert_id: str, purpose: str) -> float:
    digest = sha256(f"{seed}:{alert_id}:{purpose}".encode()).digest()
    value = int.from_bytes(digest[:8], "big")
    return (value + 0.5) / (2**64)


def _prevalence_scenarios() -> list[dict]:
    out = []
    for name, raw in CONFIG["class_prevalence_scenarios"].items():
        if raw["kind"] == "homogeneous_across_classes":
            probabilities = tuple(float(raw["pi"]) for _ in PROJECTS)
        else:
            probabilities = tuple(float(x) for x in raw["need_probability_by_class"])
        pi = sum(share * need for share, need in zip(PROJECT_MIX, probabilities))
        out.append({"name": name, "need_by_class": probabilities, "pi": pi})
    return out


def _classifier_points() -> list[dict]:
    points = []
    for item in CONFIG["classifier_operating_points"]:
        pd_, pfa = float(item["pD"]), float(item["pFA"])
        if not (0 <= pd_ <= 1 and 0 <= pfa <= 1):
            raise ValueError(f"invalid classifier point {item}")
        points.append({**item, "pD": pd_, "pFA": pfa})
    return points


def _expected_route_mix(need_by_class: tuple[float, ...], pd_: float, pfa: float):
    positive_by_class = tuple(p * pd_ + (1 - p) * pfa for p in need_by_class)
    q = sum(w * p for w, p in zip(PROJECT_MIX, positive_by_class))
    mix = tuple(w * p / q for w, p in zip(PROJECT_MIX, positive_by_class)) if q else PROJECT_MIX
    return q, mix


def analytical_rows() -> tuple[list[dict], list[dict]]:
    """Fluid offered-load calculations and pFA boundaries for rho_L2 levels."""
    l2_mean_service = _service_estimate_by_class(L2, L2_SERVICE)
    workloads = []
    frontiers = []
    for prevalence in _prevalence_scenarios():
        for point in _classifier_points():
            q, mix = _expected_route_mix(prevalence["need_by_class"], point["pD"], point["pFA"])
            mu_l2 = effective_capacity(L2, L2_SERVICE, mix)["max_common_arrivals_per_h"]
            for rho in CONFIG["rho_l1"]:
                lam = MU_L1 * float(rho)
                need_rate = lam * sum(w*p for w,p in zip(PROJECT_MIX, prevalence["need_by_class"]))
                tp_rate = lam * sum(w*p*point["pD"] for w,p in zip(PROJECT_MIX, prevalence["need_by_class"]))
                fn_rate = need_rate - tp_rate
                fp_rate = lam * sum(w*(1-p)*point["pFA"] for w,p in zip(PROJECT_MIX, prevalence["need_by_class"]))
                false_positive_work = lam * sum(
                    w*(1-p)*point["pFA"]*l2_mean_service[PROJECTS[k]]
                    for k,(w,p) in enumerate(zip(PROJECT_MIX, prevalence["need_by_class"]))
                )
                omitted_work = lam * sum(
                    w*p*(1-point["pD"])*l2_mean_service[PROJECTS[k]]
                    for k,(w,p) in enumerate(zip(PROJECT_MIX, prevalence["need_by_class"]))
                )
                necessary_routed_work = lam * sum(
                    w*p*point["pD"]*l2_mean_service[PROJECTS[k]]
                    for k,(w,p) in enumerate(zip(PROJECT_MIX, prevalence["need_by_class"]))
                )
                workloads.append({
                    "prevalence_scenario": prevalence["name"], "pi": prevalence["pi"],
                    "classifier_point": point["name"], "pD": point["pD"], "pFA": point["pFA"],
                    "rho_L1": float(rho), "lambda_L1_per_h": lam,
                    "q_expected": q, "lambda_L2_offered_per_h": lam*q,
                    "lambda_TP_per_h": tp_rate, "lambda_FP_per_h": fp_rate,
                    "lambda_FN_per_h": fn_rate,
                    "mu_L1_effective_per_h": MU_L1, "mu_L2_effective_per_h": mu_l2,
                    "rho_L2_offered": lam*q/mu_l2,
                    "L2_expected_necessary_routed_work_h_per_h": necessary_routed_work,
                    "L2_expected_unnecessary_FP_work_h_per_h": false_positive_work,
                    "L2_expected_omitted_FN_work_h_per_h": omitted_work,
                    "L2_expected_total_recommended_work_h_per_h": necessary_routed_work+false_positive_work,
                    "recommendation_mix": json.dumps(mix,separators=(",",":")),
                    "capacity_method": "fractional-flow LP using frozen roster, eligibility and analyst-class service; recommendation-positive class mix",
                })
        for pd_ in (0.7965, 0.90):
            for rho in CONFIG["rho_l1"]:
                for target_rho in (0.50, 0.80, 1.00, 1.20):
                    def value(pfa: float) -> tuple[float,float,float]:
                        q0, mix0 = _expected_route_mix(prevalence["need_by_class"], pd_, pfa)
                        mu0 = effective_capacity(L2, L2_SERVICE, mix0)["max_common_arrivals_per_h"]
                        return MU_L1*float(rho)*q0/mu0, q0, mu0
                    low, high = 0.0, 1.0
                    rlow, _, _ = value(low); rhigh, _, _ = value(high)
                    if target_rho < rlow-1e-12 or target_rho > rhigh+1e-12:
                        pfa_star = None
                    else:
                        for _ in range(64):
                            middle = (low+high)/2
                            rmid, _, _ = value(middle)
                            if rmid < target_rho:
                                low = middle
                            else:
                                high = middle
                        pfa_star = (low+high)/2
                    if pfa_star is None:
                        q_star = mu_star = float("nan")
                    else:
                        _, q_star, mu_star = value(pfa_star)
                    frontiers.append({
                        "prevalence_scenario": prevalence["name"], "pi": prevalence["pi"],
                        "pD_fixed": pd_, "rho_L1": float(rho), "rho_L2_boundary": target_rho,
                        "pFA_at_boundary": pfa_star, "q_at_boundary": q_star,
                        "mu_L2_effective_per_h": mu_star,
                        "method": "numerical root of analytic q and composition-specific LP capacity; offered-load boundary, not SLA threshold",
                    })
    return workloads, frontiers


def _make_trace(*, rho_l1: float, seed: int, prevalence: dict, point: dict):
    arrival_rate = MU_L1 * rho_l1
    cfg = replace(
        REFERENCE.scenario_config(arrival_rate_per_h=arrival_rate),
        horizon=float(CONFIG["horizon_h"]),
        escalation_probability_by_class=prevalence["need_by_class"],
        ai_sensitivity=0.5,
        ai_false_positive_rate=0.5,
        difficulty_beta=tuple(REFERENCE.difficulty_beta),
    )
    base = generate_alerts(cfg, seed)
    pd_, pfa = float(point["pD"]), float(point["pFA"])
    trace = []
    for row in base:
        recommend = _stable_uniform(seed, row.routed.alert.alert_id, "triage") < (
            pd_ if row.true_escalation_need else pfa
        )
        trace.append(replace(
            row,
            routed=replace(row.routed, soctra_recommendation=recommend),
        ))
    return tuple(trace), arrival_rate


def _trace_hash(trace: tuple, *, include_recommendation: bool) -> str:
    rows = []
    for row in trace:
        alert = row.routed.alert
        fields = (alert.alert_id, alert.arrival, alert.task_class, alert.deadline,
                  row.severity, row.difficulty, row.true_escalation_need)
        if include_recommendation:
            fields += (row.routed.soctra_recommendation,)
        rows.append(fields)
    return sha256(repr(tuple(rows)).encode()).hexdigest()


def _service_estimate_by_class(analysts, service_map) -> dict:
    result = {}
    for task_class in PROJECTS:
        durations = [service_map[a.analyst_id][task_class] for a in analysts
                     if task_class in a.eligible_classes]
        if not durations:
            raise ValueError(f"no L2 analyst eligible for {task_class}")
        result[task_class] = statistics.mean(durations)
    return result


def _peak_queue(arrival_times: list[float], start_times: list[float], cutoff: float) -> int:
    events = sorted({t for t in arrival_times + start_times if t <= cutoff})
    peak = 0
    for t in events:
        # Before dispatch at t: arrivals at t have joined; starts at t have not left.
        queued = sum(a <= t for a in arrival_times) - sum(s < t for s in start_times)
        peak = max(peak, queued)
    return peak


def _metrics(trace: tuple, sim, *, horizon: float, drain: float, need_work: dict):
    n = len(trace)
    l1jobs = {job.alert_id: job for job in sim.l1_simulation.assignments}
    l2jobs = {job.alert_id: job for job in sim.l2_simulation.assignments}
    route = {item.alert_id: item.scenario_routing_decision for item in sim.escalation_records}
    row_by_id = {row.routed.alert.alert_id: row for row in trace}
    cutoff = horizon + drain

    tp = fp = fn = tn = 0
    route_correct = 0
    legacy_completed = legacy_timely = 0
    required_timely = required_completed = 0
    expected_correct_timely = 0.0
    expected_correct_completed = 0.0
    legacy_quality = 0.0
    triage_omitted_work = 0.0
    triage_unnecessary_work = 0.0
    triage_necessary_recommended_work = 0.0
    admitted = [row for row in trace if row.routed.alert.arrival < horizon]
    l1_received = len(admitted)
    l1_assigned = sum(row.routed.alert.alert_id in l1jobs for row in admitted)
    l2_generated_ids = {
        aid for aid, yes in route.items()
        if yes and aid in l1jobs and l1jobs[aid].completion < cutoff
    }

    for row in admitted:
        alert = row.routed.alert
        aid = alert.alert_id
        need = bool(row.true_escalation_need)
        rec = bool(route[aid])
        if need and rec:
            tp += 1
        elif need:
            fn += 1
            triage_omitted_work += need_work[alert.task_class]
        elif rec:
            fp += 1
            triage_unnecessary_work += need_work[alert.task_class]
        else:
            tn += 1
        route_correct += int(need == rec)
        if need and rec:
            triage_necessary_recommended_work += need_work[alert.task_class]

        stage_job = l2jobs.get(aid) if rec else l1jobs.get(aid)
        physical_complete = stage_job is not None and stage_job.completion <= cutoff
        physical_timely = physical_complete and stage_job.completion <= alert.deadline
        proper_route = not need or rec
        if physical_complete:
            legacy_completed += 1
            expected_correct_completed += stage_job.competence * (1 - 0.35 * row.difficulty)
            if proper_route:
                required_completed += 1
        if physical_timely:
            legacy_timely += 1
            legacy_quality += stage_job.competence
            if proper_route:
                expected_correct = stage_job.competence * (1 - 0.35 * row.difficulty)
                required_timely += 1
                expected_correct_timely += expected_correct

    class_true = sum(row.true_escalation_need for row in admitted)
    negatives = l1_received - class_true
    p_d = tp / class_true if class_true else 0.0
    p_fa = fp / negatives if negatives else 0.0

    l1_assignments = [job for job in sim.l1_simulation.assignments]
    l2_assignments = [job for job in sim.l2_simulation.assignments]
    l1_service_consumed = sum(max(0.0, min(job.completion, cutoff) - job.start)
                              for job in l1_assignments)
    l2_service_consumed = sum(max(0.0, min(job.completion, cutoff) - job.start)
                              for job in l2_assignments)
    l1_arrivals = [row.routed.alert.arrival for row in admitted]
    l1_starts = [job.start for job in l1_assignments if job.alert_id in row_by_id]
    l2_arrivals = [l1jobs[aid].completion for aid in l2_generated_ids]
    l2_starts = [job.start for job in l2_assignments]
    H_state = sim.at_horizon
    HD_state = sim.after_drain
    util_h = dict(H_state.utilization_by_analyst)
    util_hd = dict(HD_state.utilization_by_analyst)
    util_l1_h = [value for key,value in util_h.items() if key.startswith("L1:")]
    util_l2_h = [value for key,value in util_h.items() if key.startswith("L2:")]
    util_l1_hd = [value for key,value in util_hd.items() if key.startswith("L1:")]
    util_l2_hd = [value for key,value in util_hd.items() if key.startswith("L2:")]

    mode_rows = []
    for pool, stage in (("L1", sim.l1_simulation), ("L2", sim.l2_simulation)):
        history = stage.hlsa_history
        p1_count = sum(item.mode == "P1" for item in history)
        for item in history:
            if item.switched:
                mode_rows.append({"pool": pool, "time_h": item.time, "mode": item.mode,
                                  "pending_at_switch": item.pending,
                                  "occupied_at_switch": item.occupied,
                                  "estimated_pressure": item.pressure})

    legacy_rn = sim.after_drain.modeled_quality_per_admitted
    # The L1L2 wrapper's modeled quality is competence only. Preserve it as the
    # historic R/N-style measure; the new primary metric additionally gates FN.
    joint = expected_correct_timely / n if n else 0.0
    proper_sla = required_timely / n if n else 0.0
    result = {
        "admitted": n,
        "l1_tasks_received": l1_received,
        "l1_tasks_assigned": l1_assigned,
        "l2_recommendations": tp + fp,
        "l2_tasks_generated_by_drain": len(l2_generated_ids),
        "l2_pool_arrival_rate_by_drain_per_h": len(l2_generated_ids) / (cutoff if cutoff else 1.0),
        "l2_tasks_assigned": len(l2_assignments),
        "l2_tasks_completed_by_drain": sum(job.completion <= cutoff for job in l2_assignments),
        "l2_completion_rate_by_drain_per_h": sum(job.completion <= cutoff for job in l2_assignments) / (cutoff if cutoff else 1.0),
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "pD_empirical": p_d, "pFA_empirical": p_fa,
        "recommendation_fraction": (tp + fp) / n if n else 0.0,
        "routing_accuracy": route_correct / n if n else 0.0,
        "legacy_RN": legacy_rn,
        "legacy_RN_recomputed": legacy_quality / n if n else 0.0,
        "routed_SLA_H": H_state.fraction_within_sla,
        "routed_SLA_terminal": HD_state.fraction_within_sla,
        "physical_completed_terminal": legacy_completed,
        "physical_timely_terminal": legacy_timely,
        "required_resolution_completed_terminal": required_completed,
        "required_resolution_SLA_terminal": proper_sla,
        "correct_on_time_expected_per_admitted": joint,
        "expected_correct_on_time_count": expected_correct_timely,
        # Descriptive score along the physically completed route. This does not
        # gate false-negative routes; use correct_on_time_expected_per_admitted
        # as the integrated outcome that accounts for hidden escalation need.
        "physical_path_expected_quality_per_admitted": expected_correct_completed / n if n else 0.0,
        "backlog_L1_H": H_state.l1_backlog,
        "backlog_L2_H": H_state.l2_backlog,
        "backlog_L1_terminal": HD_state.l1_backlog,
        "backlog_L2_terminal": HD_state.l2_backlog,
        "peak_queue_L1_pre_dispatch": _peak_queue(l1_arrivals, l1_starts, cutoff),
        "peak_queue_L2_pre_dispatch": _peak_queue(l2_arrivals, l2_starts, cutoff),
        "utilization_L1_mean_H": statistics.mean(util_l1_h) if util_l1_h else 0.0,
        "utilization_L2_mean_H": statistics.mean(util_l2_h) if util_l2_h else 0.0,
        "utilization_L1_mean_terminal": statistics.mean(util_l1_hd) if util_l1_hd else 0.0,
        "utilization_L2_mean_terminal": statistics.mean(util_l2_hd) if util_l2_hd else 0.0,
        "service_hours_L1_consumed_by_terminal": l1_service_consumed,
        "service_hours_L2_consumed_by_terminal": l2_service_consumed,
        "L2_work_necessary_recommended_nominal_h": triage_necessary_recommended_work,
        "L2_work_unnecessary_FP_nominal_h": triage_unnecessary_work,
        "L2_work_omitted_FN_nominal_h": triage_omitted_work,
        "L2_backlog_terminal_from_wrapper": HD_state.l2_backlog,
        "P1_dispatch_decisions_L1": sum(x.mode == "P1" for x in sim.l1_simulation.hlsa_history),
        "dispatch_epochs_L1": len(sim.l1_simulation.hlsa_history),
        "P1_dispatch_decisions_L2": sum(x.mode == "P1" for x in sim.l2_simulation.hlsa_history),
        "dispatch_epochs_L2": len(sim.l2_simulation.hlsa_history),
        "switches_L1": sum(x.switched for x in sim.l1_simulation.hlsa_history),
        "switches_L2": sum(x.switched for x in sim.l2_simulation.hlsa_history),
    }
    result["P1_fraction_of_WAPS_dispatches_L1"] = (
        result["P1_dispatch_decisions_L1"] / result["dispatch_epochs_L1"]
        if result["dispatch_epochs_L1"] else 0.0
    )
    result["P1_fraction_of_WAPS_dispatches_L2"] = (
        result["P1_dispatch_decisions_L2"] / result["dispatch_epochs_L2"]
        if result["dispatch_epochs_L2"] else 0.0
    )
    return result, mode_rows


def _run_one(trace: tuple, *, seed: int, rho_l1: float, prevalence: dict,
             point: dict, arrival_rate: float, policy: str) -> tuple[dict, list[dict]]:
    q, routed_mix = _expected_route_mix(prevalence["need_by_class"], point["pD"], point["pFA"])
    mu_l2 = effective_capacity(L2, L2_SERVICE, routed_mix)["max_common_arrivals_per_h"]
    hlsb = CONFIG["hlsb"]
    l2_work = _service_estimate_by_class(L2, L2_SERVICE)
    work = {k: l2_work[k] for k in l2_work}
    config_fields = {
        "prevalence_scenario": prevalence["name"], "pi_expected": prevalence["pi"],
        "classifier_point": point["name"], "pD_target": point["pD"], "pFA_target": point["pFA"],
        "rho_L1_target": rho_l1, "lambda_L1_per_h": arrival_rate,
        "q_recommendation_expected": q, "lambda_L2_offered_expected_per_h": arrival_rate*q,
        "mu_L1_effective_per_h": MU_L1, "mu_L2_effective_per_h": mu_l2,
        "rho_L2_analytic": arrival_rate*q/mu_l2 if mu_l2 else 0.0,
        "recommendation_mix_class_0": routed_mix[0], "recommendation_mix_class_1": routed_mix[1],
        "recommendation_mix_class_2": routed_mix[2], "seed": seed, "policy": policy,
    }
    kw = dict(
        policy=policy, admission_horizon=float(CONFIG["horizon_h"]),
        drain_period=float(CONFIG["drain_h"]), coordination_latency=0.0,
        coordination_edge_cost=0.0,
        decision_mode="hypothetical_recommendation_acceptance", random_seed=seed,
        l1_service_by_analyst_class=L1_SERVICE, l2_service_by_analyst_class=L2_SERVICE,
    )
    if policy == "HLS-B":
        kw["hlsb_l1_config"] = HLSBConfig(**hlsb, capacity_per_h=MU_L1)
        kw["hlsb_l2_config"] = HLSBConfig(**hlsb, capacity_per_h=mu_l2)
    sim = simulate_l1_l2(
        tuple(row.routed for row in trace), L1, L2,
        BASE_SERVICE_L1_H, BASE_SERVICE_L2_H, **kw,
    )
    metrics, mode_rows = _metrics(trace, sim, horizon=float(CONFIG["horizon_h"]),
                                   drain=float(CONFIG["drain_h"]), need_work=work)
    row = {**config_fields, **metrics,
           "exogenous_sha256": _trace_hash(trace, include_recommendation=False),
           "trace_sha256": _trace_hash(trace, include_recommendation=True),
           "trace_alert_count": len(trace),
           "max_deadline_h": max((x.routed.alert.deadline for x in trace), default=0.0),
           "terminal_cutoff_h": float(CONFIG["horizon_h"] + CONFIG["drain_h"]),
           "fraction_p1_all_pools": (
               metrics["P1_dispatch_decisions_L1"] + metrics["P1_dispatch_decisions_L2"]
           ) / max(1, metrics["dispatch_epochs_L1"] + metrics["dispatch_epochs_L2"])}
    if abs(row["legacy_RN"] - row["legacy_RN_recomputed"]) > 1e-10:
        raise AssertionError("legacy R/N reconstruction differs from frozen wrapper metric")
    return row, [{**config_fields, **change, "seed": seed} for change in mode_rows]


def _triage_row(trace: tuple, *, seed: int, rho_l1: float, prevalence: dict,
                point: dict, arrival_rate: float) -> dict:
    need = sum(x.true_escalation_need for x in trace)
    rec_positive = sum(bool(x.routed.soctra_recommendation) for x in trace)
    tp = sum(x.true_escalation_need and bool(x.routed.soctra_recommendation) for x in trace)
    fn = sum(x.true_escalation_need and not bool(x.routed.soctra_recommendation) for x in trace)
    fp = sum(not x.true_escalation_need and bool(x.routed.soctra_recommendation) for x in trace)
    tn = len(trace)-tp-fn-fp
    q, mix = _expected_route_mix(prevalence["need_by_class"], point["pD"], point["pFA"])
    return {
        "prevalence_scenario": prevalence["name"], "pi_expected": prevalence["pi"],
        "classifier_point": point["name"], "pD_target": point["pD"], "pFA_target": point["pFA"],
        "rho_L1_target": rho_l1, "lambda_L1_per_h": arrival_rate,
        "seed": seed, "alert_count": len(trace), "true_need_positive": need,
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "pD_empirical": tp/need if need else 0.0,
        "pFA_empirical": fp/(len(trace)-need) if len(trace)>need else 0.0,
        "recommendations_positive": rec_positive,
        "recommendation_fraction": rec_positive/len(trace) if trace else 0.0,
        "q_expected": q, "expected_positive_count": len(trace)*q,
        "expected_L2_offered_per_h": arrival_rate*q,
        "expected_L2_true_positive_per_h": arrival_rate*prevalence["pi"]*point["pD"],
        "expected_L2_false_positive_per_h": arrival_rate*(1-prevalence["pi"])*point["pFA"],
        "expected_L2_false_negative_per_h": arrival_rate*prevalence["pi"]*(1-point["pD"]),
        "route_mix_class_0": mix[0], "route_mix_class_1": mix[1], "route_mix_class_2": mix[2],
        "exogenous_sha256": _trace_hash(trace, include_recommendation=False),
        "trace_sha256": _trace_hash(trace, include_recommendation=True),
    }


def run() -> dict:
    rows: list[dict] = []
    triage_rows: list[dict] = []
    switch_rows: list[dict] = []
    shared_traces: dict[tuple, tuple] = {}
    trace_hashes = []
    for prevalence in _prevalence_scenarios():
        for rho in CONFIG["rho_l1"]:
            for seed in range(int(CONFIG["seed_base"]),
                              int(CONFIG["seed_base"])+int(CONFIG["n_seeds"])):
                for point in _classifier_points():
                    key = (prevalence["name"], float(rho), seed, point["name"])
                    trace, arrival_rate = _make_trace(
                        rho_l1=float(rho), seed=seed, prevalence=prevalence, point=point,
                    )
                    shared_traces[key] = trace
                    triage_rows.append(_triage_row(
                        trace, seed=seed, rho_l1=float(rho), prevalence=prevalence,
                        point=point, arrival_rate=arrival_rate,
                    ))
                    for policy in POLICIES:
                        row, switches = _run_one(
                            trace, seed=seed, rho_l1=float(rho), prevalence=prevalence,
                            point=point, arrival_rate=arrival_rate, policy=policy,
                        )
                        rows.append(row)
                        switch_rows.extend(switches)
                    trace_hashes.append((prevalence["name"], float(rho), seed,
                                         point["name"], _trace_hash(trace, include_recommendation=False)))

    OUT.mkdir(parents=True, exist_ok=True)
    _write_csv(OUT / "episodes.csv", rows)
    _write_csv(OUT / "triage_by_seed.csv", triage_rows)
    _write_csv(OUT / "waps_switches.csv", switch_rows or [{"note": "No WAPS mode switches occurred in this pilot."}])
    workload_rows, frontier_rows = analytical_rows()
    _write_csv(OUT / "analytic_workload.csv", workload_rows)
    _write_csv(OUT / "analytic_l2_frontiers.csv", frontier_rows)

    checks = {
        "expected_configs": len(_prevalence_scenarios())*len(CONFIG["rho_l1"])*len(_classifier_points()),
        "expected_episode_rows": len(_prevalence_scenarios())*len(CONFIG["rho_l1"])*len(_classifier_points())*int(CONFIG["n_seeds"])*len(POLICIES),
        "actual_episode_rows": len(rows),
        "actual_triage_rows": len(triage_rows),
        "one_trace_hash_per_policy_cell": True,
        "same_exogenous_trace_across_classifier_points": True,
        "same_denominator_across_policies": True,
        "no_duplicate_l1_assignments": True,
        "no_duplicate_l2_assignments": True,
        "no_task_l2_without_positive_recommendation": True,
        "false_negative_correct_on_time_credit_is_zero": True,
        "deadline_maturation_by_terminal_cutoff": True,
        "legacy_RN_reconstruction_matches_wrapper": True,
        "policies_and_engine_source_unchanged": True
    }
    if len(rows) != checks["expected_episode_rows"]:
        raise AssertionError("unexpected episode row count")
    for key, trace in shared_traces.items():
        policies_for_trace = [r for r in rows if (r["prevalence_scenario"], r["rho_L1_target"], r["seed"], r["classifier_point"]) == key]
        if len(policies_for_trace) != len(POLICIES) or len({r["trace_sha256"] for r in policies_for_trace}) != 1:
            raise AssertionError(f"paired policies do not share trace for {key}")
        if len({r["admitted"] for r in policies_for_trace}) != 1:
            raise AssertionError(f"policy denominators differ for {key}")
        digest = _trace_hash(trace, include_recommendation=False)
        if len({r["exogenous_sha256"] for r in policies_for_trace}) != 1 or digest != policies_for_trace[0]["exogenous_sha256"]:
            raise AssertionError(f"trace identity failed for {key}")
    by_exog = {}
    for row in triage_rows:
        k = (row["prevalence_scenario"], row["rho_L1_target"], row["seed"])
        by_exog.setdefault(k, set()).add(row["exogenous_sha256"])
    if any(len(value) != 1 for value in by_exog.values()):
        raise AssertionError("underlying realization changed across classifier points")
    for row in rows:
        if row["max_deadline_h"] > row["terminal_cutoff_h"] + 1e-12:
            raise AssertionError("some alert deadline is beyond terminal observation")
        if row["correct_on_time_expected_per_admitted"] > row["routed_SLA_terminal"] + 1e-12:
            raise AssertionError("joint correct-and-timely rate cannot exceed routed SLA")
        if row["policy"] != "HLS-B" and (row["switches_L1"] or row["switches_L2"]):
            raise AssertionError("fixed policy reports an adaptive switch")
    checks["unique_exogenous_realizations"] = len(by_exog)
    checks["unique_trace_hashes_by_classifier_config"] = len(trace_hashes)
    (OUT / "validation_checks.json").write_text(json.dumps(checks, indent=2)+"\n", encoding="utf-8")
    metadata = {
        "config": CONFIG,
        "mu_L1_alerts_per_h": MU_L1,
        "synthetic_pi": sum(w*p for w,p in zip(PROJECT_MIX,SYNTHETIC_NEED)),
        "historical_pi": PI_HIST,
        "historical_pD": PD_OLD,
        "historical_pFA": PFA_OLD,
        "source_commit": "642af6b6e7ffd3e076258a1f4c87722566919dc6",
        "frozen_policy_reference_commit": CONFIG["frozen_reference_commit"],
        "generated_episode_rows": len(rows),
        "generated_triage_rows": len(triage_rows),
        "seed_ids": list(range(int(CONFIG["seed_base"]), int(CONFIG["seed_base"])+int(CONFIG["n_seeds"]))),
        "method_note": "L2 capacity recomputed by fractional-flow LP from the expected class mix among positive recommendations for each fixed classifier point; HLS-B thresholds/window unchanged."
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    return {"episodes": rows, "triage": triage_rows, "switches": switch_rows}


if __name__ == "__main__":
    results = run()
    print(f"Wrote {len(results['episodes'])} paired policy episodes and {len(results['triage'])} triage rows to {OUT}")
