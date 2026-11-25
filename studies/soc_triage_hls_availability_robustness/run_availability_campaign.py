"""Paired synthetic L1→L2 calendar campaign; never writes historical artifacts."""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from hls.rq1_allocation import Alert, HLSBConfig, simulate as simulate_continuous
from hls import rq1_allocation as allocation_module
from studies.soc_triage_hls_q1_integration_evidence import run_primary_campaign as old
from studies.soc_triage_hls_availability_robustness.availability_engine import (
    CONTINUOUS, WEEKDAY_9_TO_17, simulate as simulate_calendar,
)
from studies.soc_triage_hls_availability_robustness import availability_engine as availability_module
from studies.soc_triage_hls_availability_robustness.fast_dispatch import dispatch_d1_fast
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity
from studies.soc_human_ai_organization.soc_parametric_baseline import (
    BASE_ELIGIBILITY, BASE_L1_ANALYSTS, BASE_SERVICE_L1_H, BASE_SERVICE_L2_H,
    PROJECTS, PROJECT_MIX, build_roster,
)

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config" / "availability_campaign.json").read_text())
OUT = ROOT / "results" / "soc_triage_hls_availability_robustness" / "campaign"
H = float(CONFIG["admission_horizon_h"])
CUTOFF = float(CONFIG["evaluation_cutoff_h"])
PI = float(old.PI)


def _write(path: Path, rows, fields=None):
    rows = list(rows)
    if not rows:
        raise ValueError(f"refusing to write empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def _hash(value):
    return hashlib.sha256(repr(value).encode()).hexdigest()


def _make_trace(seed: int, point: dict, rho: float):
    # Reuse the exact Q1 exogenous generator and keyed recommendation draw.
    prev = {"pi": PI, "need_by_class": tuple(PI for _ in PROJECTS)}
    old_horizon = old.frozen.CONFIG["horizon_h"]
    try:
        old.frozen.CONFIG["horizon_h"] = H
        trace, rate = old.frozen._make_trace(rho_l1=rho, seed=seed, prevalence=prev, point=point)
    finally:
        old.frozen.CONFIG["horizon_h"] = old_horizon
    deadlines = CONFIG["deadlines_h_by_severity"]
    mapped = []
    for row in trace:
        severity = str(row.severity).lower()
        if severity not in deadlines:
            raise ValueError(f"unexpected synthetic severity value {severity!r}")
        a = row.routed.alert
        alert = replace(a, deadline=a.arrival + float(deadlines[severity]))
        mapped.append(replace(row, routed=replace(row.routed, alert=alert)))
    return tuple(mapped), rate, prev


def _run_l1(trace, roster, service, policy, seed, mu_l1):
    rows = [row.routed.alert for row in trace]
    waps = None
    engine_policy = policy
    if policy == "WAPS":
        engine_policy = "HLS-B"
        waps = HLSBConfig(**CONFIG["waps"], capacity_per_h=mu_l1)
    return simulate_continuous(
        rows, roster, BASE_SERVICE_L1_H, policy=engine_policy,
        admission_horizon=H, drain_period=CUTOFF-H,
        random_seed=seed, service_by_analyst_class=service,
        hlsb_config=waps,
    )


def _availability_hours(calendar, cutoff):
    # All configured shift boundaries are whole hours; midpoint integration is exact.
    return sum(calendar.available(hour + .5) for hour in range(int(math.ceil(cutoff))))


def _run_condition(trace, point, rho, alpha, n_l2, policy, seed, l1, l1_services,
                   l2, l2_services, mu_l1, calendar_name, l1_result):
    route = {r.routed.alert.alert_id: bool(r.routed.soctra_recommendation) for r in trace}
    need = {r.routed.alert.alert_id: bool(r.true_escalation_need) for r in trace}
    trace_by_id = {r.routed.alert.alert_id: r for r in trace}
    l1_jobs = {j.alert_id: j for j in l1_result.assignments}
    l2_arrivals = []
    for row in trace:
        a = row.routed.alert
        job = l1_jobs.get(a.alert_id)
        if a.arrival < H and route[a.alert_id] and job is not None and job.completion < CUTOFF:
            l2_arrivals.append(Alert(a.alert_id, job.completion, a.task_class, a.deadline))
    l2_need = {a.alert_id: need[a.alert_id] for a in l2_arrivals}
    scales = {a.alert_id: 1.0 if l2_need[a.alert_id] else alpha for a in l2_arrivals}
    factors = old._expected_class_factors(point, alpha)
    forecast = {analyst.analyst_id: {k: l2_services[analyst.analyst_id][k] * factors[k]
                                    for k in analyst.eligible_classes} for analyst in l2}
    _, route_mix = old.frozen._expected_route_mix(tuple(PI for _ in PROJECTS), point["pD"], point["pFA"])
    mu_l2 = effective_capacity(l2, forecast, route_mix)["max_common_arrivals_per_h"]
    waps = HLSBConfig(**CONFIG["waps"], capacity_per_h=mu_l2) if policy == "WAPS" else None
    cal = CONTINUOUS if calendar_name == "L2_24x7" else WEEKDAY_9_TO_17
    if calendar_name == "L2_24x7":
        # Exact compatibility fast path for the historical continuous event loop.
        l2_result = old.simulate_l2_hidden_work(
            l2_arrivals, l2_need, l2, l2_services, forecast, scales,
            policy="HLS-B" if policy == "WAPS" else policy, horizon=CUTOFF,
            seed=seed, hlsb_config=waps,
        )
        status_by_id = {j.alert_id: (("completed_late" if j.completion > trace_by_id[j.alert_id].routed.alert.deadline else "completed")
                                     if j.completion <= CUTOFF else "running")
                        for j in l2_result.assignments}
        assignment_map = {j.alert_id: j for j in l2_result.assignments}
        for aid in l2_result.pending_at_cutoff:
            status_by_id.setdefault(aid,"queued")
        # Exact continuous work segments are clipped assignment intervals.
        executed_by_id = {j.alert_id: max(0.0, min(j.completion, CUTOFF)-j.start) for j in l2_result.assignments}
        suspension_by_id = {a.alert_id: 0.0 for a in l2_arrivals}
        switches = l2_result.switches
        dispatch_epochs = l2_result.dispatch_epochs
        p1_epochs = l2_result.p1_dispatch_epochs
    else:
        l2_result = simulate_calendar(
            l2_arrivals, l2, forecast, {a.analyst_id: cal for a in l2},
            horizon=CUTOFF, policy=policy, seed=seed, waps_config=waps,
            actual_service=l2_services, realized_scale_by_alert=scales,
        )
        status_by_id = {e.alert_id: e.status for e in l2_result.episodes}
        assignment_map = {j.alert_id: j for j in l2_result.assignments}
        executed_by_id = dict(l2_result.work_done_by_alert)
        suspension_by_id = {e.alert_id: e.suspension_h for e in l2_result.episodes}
        switches = l2_result.switches
        dispatch_epochs = l2_result.dispatch_epochs
        p1_epochs = l2_result.p1_dispatch_epochs

    admitted = [r for r in trace if r.routed.alert.arrival < H]
    need_total = sum(need[r.routed.alert.alert_id] for r in admitted)
    tp = sum(need[r.routed.alert.alert_id] and route[r.routed.alert.alert_id] for r in admitted)
    fp = sum(not need[r.routed.alert.alert_id] and route[r.routed.alert.alert_id] for r in admitted)
    fn, tn = need_total-tp, len(admitted)-tp-fp-(need_total-tp)
    splus_ids = []
    task_rows = []
    l2_waits = []
    l2_episode_by_id = {e.alert_id: e for e in getattr(l2_result, "episodes", ())}
    for alert in l2_arrivals:
        aid = alert.alert_id
        job = assignment_map.get(aid)
        status = status_by_id.get(aid, "queued")
        start = job.start if job else None
        complete = job.completion if job else None
        episode = l2_episode_by_id.get(aid)
        if episode is not None:
            start = episode.start
            complete = episode.completion
        l2_waits.append(max(0.0, (start if start is not None else CUTOFF)-alert.arrival))
        if need[aid] and status == "completed" and complete is not None and complete <= trace_by_id[aid].routed.alert.deadline:
            splus_ids.append(aid)
        task_rows.append({"alert_id": aid, "status": status, "analyst_id": (job.analyst_id if job else (episode.analyst_id if episode else "")),
                          "l1_completion": alert.arrival, "start": start if start is not None else "",
                          "completion": complete if complete is not None else "", "deadline": alert.deadline,
                          "service_effective_h": executed_by_id.get(aid, 0.0),
                          "remaining_service_h": (episode.remaining_service_h if episode else
                              (max(0.0, complete-CUTOFF) if job and complete is not None and complete>CUTOFF else "")),
                          "suspension_h": suspension_by_id.get(aid, 0.0), "need_hidden": int(need[aid]),
                          "recommendation": int(route[aid]), "alpha": alpha})

    l1_h = l1_result.at_horizon
    l1_cut = l1_result.after_drain
    l1_waits = []
    for row in admitted:
        a = row.routed.alert
        j = l1_jobs.get(a.alert_id)
        l1_waits.append(max(0.0, (j.start if j else CUTOFF)-a.arrival))
    l1_work_H = sum(max(0.0, min(H, j.completion)-j.start) for j in l1_result.assignments)
    l1_work_cut = sum(max(0.0, min(CUTOFF, j.completion)-j.start) for j in l1_result.assignments)
    admitted_deadline={r.routed.alert.alert_id:r.routed.alert.deadline for r in admitted}
    l1_assignments=[j for j in l1_result.assignments if j.alert_id in admitted_deadline]
    l1_completed_late=sum(j.completion <= CUTOFF and j.completion > admitted_deadline[j.alert_id]
                          for j in l1_assignments)
    l1_completed_cut=sum(j.completion <= CUTOFF for j in l1_assignments)
    if calendar_name == "L2_24x7":
        l2_work_by_analyst_H = {a.analyst_id: 0.0 for a in l2}
        l2_work_by_analyst_cut = {a.analyst_id: 0.0 for a in l2}
        for j in l2_result.assignments:
            l2_work_by_analyst_H[j.analyst_id] += max(0.0, min(H, j.completion)-j.start)
            l2_work_by_analyst_cut[j.analyst_id] += max(0.0, min(CUTOFF, j.completion)-j.start)
        l2_episodes = []
        completed_late = sum(s == "completed_late" for s in status_by_id.values())
    else:
        l2_work_by_analyst_H = {a.analyst_id: 0.0 for a in l2}
        l2_work_by_analyst_cut = {a.analyst_id: 0.0 for a in l2}
        for aid, analyst_id, start, end in l2_result.work_segments:
            l2_work_by_analyst_cut[analyst_id] += max(0.0, min(CUTOFF, end)-start)
            l2_work_by_analyst_H[analyst_id] += max(0.0, min(H, end)-start)
        l2_episodes = list(l2_result.episodes)
        completed_late = sum(e.status == "completed_late" for e in l2_episodes)
    avail_H = _availability_hours(cal, H)
    avail_cut = _availability_hours(cal, CUTOFF)
    util_l2_H = statistics.mean(l2_work_by_analyst_H[a.analyst_id] / max(1, _availability_hours(cal, H)) for a in l2)
    util_l2_cut = statistics.mean(l2_work_by_analyst_cut[a.analyst_id] / max(1, avail_cut) for a in l2)
    l2_backlog_H = sum(
        alert.arrival <= H and (status_by_id.get(alert.alert_id) not in {"completed", "completed_late"}
           or (assignment_map.get(alert.alert_id) is not None and assignment_map[alert.alert_id].completion > H))
        for alert in l2_arrivals)
    l2_backlog_cut = sum(status_by_id.get(a.alert_id) not in {"completed", "completed_late"} for a in l2_arrivals)
    fp_work_offered = sum(statistics.mean(l2_services[a.analyst_id][x.task_class]
                           for a in l2 if x.task_class in a.eligible_classes) * alpha
                          for x in l2_arrivals if not need[x.alert_id])
    fp_work_done = sum(executed_by_id.get(a.alert_id, 0.0) for a in l2_arrivals if not need[a.alert_id])
    l2_work_done = sum(executed_by_id.values())
    return {
        "condition": {"classifier_id": point["id"], "rho_L1": rho, "alpha": alpha,
                      "n_L2": n_l2, "policy": policy, "calendar": calendar_name, "seed": seed},
        "admitted": len(admitted), "true_need_count": need_total, "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "S_plus_numerator": len(splus_ids), "S_plus_denominator": need_total,
        "S_plus_per_seed": len(splus_ids)/need_total if need_total else "",
        "L1_wait_mean_h": statistics.mean(l1_waits) if l1_waits else 0.0,
        "L2_wait_mean_h": statistics.mean(l2_waits) if l2_waits else 0.0,
        "L1_backlog_H": l1_h.pending, "L1_backlog_cutoff": l1_cut.pending,
        "L2_backlog_H": l2_backlog_H, "L2_backlog_cutoff": l2_backlog_cut,
        "L1_work_H": l1_work_H, "L1_work_cutoff": l1_work_cut,
        "L2_work_effective_cutoff": l2_work_done, "L2_FP_work_offered": fp_work_offered,
        "L2_FP_work_executed": fp_work_done,
        "L2_suspension_total_h": sum(suspension_by_id.values()),
        "L2_completed_tasks": sum(s in {"completed", "completed_late"} for s in status_by_id.values()),
        "L2_completed_late": completed_late,
        "L2_late_fraction": completed_late / max(1, sum(s in {"completed", "completed_late"} for s in status_by_id.values())),
        "L2_queued_at_cutoff":sum(s=="queued" for s in status_by_id.values()),
        "L2_suspended_at_cutoff":sum(s=="suspended" for s in status_by_id.values()),
        "L2_running_at_cutoff":sum(s=="running" for s in status_by_id.values()),
        "L2_completed_on_time":sum(s=="completed" for s in status_by_id.values()),
        "L2_overdue_unfinished":sum(status_by_id.get(a.alert_id) in {"queued","suspended","running"}
                                     and a.deadline<CUTOFF for a in l2_arrivals),
        "L1_completed_at_cutoff":l1_completed_cut,"L1_completed_late":l1_completed_late,
        "L1_late_fraction":l1_completed_late/max(1,l1_completed_cut),
        "L1_utilization_H": statistics.mean(v for _, v in l1_h.utilization_by_analyst),
        "L1_utilization_cutoff": statistics.mean(v for _, v in l1_cut.utilization_by_analyst),
        "L2_utilization_available_H": util_l2_H, "L2_utilization_available_cutoff": util_l2_cut,
        "WAPS_switch_count": len(switches), "WAPS_P1_dispatch_fraction": p1_epochs/dispatch_epochs if dispatch_epochs else 0.0,
        "trace_hash": old.frozen._trace_hash(trace, include_recommendation=True),
        "exogenous_hash": old.frozen._trace_hash(trace, include_recommendation=False),
        "recommendation_hash": _hash(tuple((r.routed.alert.alert_id, r.routed.soctra_recommendation) for r in trace)),
        "need_hash": _hash(tuple((r.routed.alert.alert_id, r.true_escalation_need) for r in trace)),
        "l1_assignment_hash": _hash(tuple((j.alert_id,j.analyst_id,j.start,j.completion) for j in l1_result.assignments)),
        "l2_tasks": task_rows,
        "max_deadline_admitted_h": max((r.routed.alert.deadline for r in admitted), default=0.0),
        "evaluation_cutoff_h": CUTOFF,
        "available_hours_per_l2": avail_cut,
    }


def _bootstrap(seed_ids, reps, seed):
    rng = np.random.default_rng(seed)
    return rng.integers(0, len(seed_ids), size=(reps, len(seed_ids)))


def _q(values):
    return [float(np.quantile(values, .025)), float(np.quantile(values, .975))]


def _summarize(rows, reps=10000, boot_seed=711202611):
    seeds = sorted({r["condition"]["seed"] for r in rows})
    idx = _bootstrap(seeds, reps, boot_seed)
    ordered_seed_index = {seed: i for i, seed in enumerate(seeds)}
    groups = defaultdict(list)
    for row in rows:
        c = row["condition"]
        groups[(c["classifier_id"], c["rho_L1"], c["alpha"], c["n_L2"], c["policy"], c["calendar"])].append(row)
    summaries = []
    by_group = {}
    point_s = {}
    for key, group in sorted(groups.items()):
        nums = np.zeros(len(seeds), dtype=float); dens = np.zeros(len(seeds), dtype=float)
        for r in group:
            i = ordered_seed_index[r["condition"]["seed"]]
            nums[i] += r["S_plus_numerator"]; dens[i] += r["S_plus_denominator"]
        boot_den = dens[idx].sum(axis=1); boot_num = nums[idx].sum(axis=1)
        boot_s = boot_num[boot_den > 0] / boot_den[boot_den > 0]
        n, d = int(nums.sum()), int(dens.sum())
        summary = dict(zip(("classifier_id","rho_L1","alpha","n_L2","policy","calendar"),key))
        summary.update({"seed_blocks":len(group),"S_plus_numerator":n,"S_plus_denominator":d,
                        "S_plus_pooled":n/d if d else math.nan,
                        "S_plus_CI95_low":_q(boot_s)[0],"S_plus_CI95_high":_q(boot_s)[1]})
        summary["zero_need_seed_blocks"] = int(np.count_nonzero(dens == 0))
        metrics = ["L1_wait_mean_h","L2_wait_mean_h","L1_backlog_H","L1_backlog_cutoff",
                   "L2_backlog_H","L2_backlog_cutoff","L2_work_effective_cutoff","L2_FP_work_offered",
                   "L2_FP_work_executed","L2_suspension_total_h","L2_late_fraction",
                   "L2_queued_at_cutoff","L2_suspended_at_cutoff","L2_running_at_cutoff",
                   "L2_completed_on_time","L2_completed_late","L2_overdue_unfinished","L1_late_fraction",
                   "L1_utilization_H","L1_utilization_cutoff","L2_utilization_available_H",
                   "L2_utilization_available_cutoff","WAPS_switch_count","WAPS_P1_dispatch_fraction"]
        byseed = {r["condition"]["seed"]: r for r in group}
        for metric in metrics:
            vals = np.array([float(byseed[s][metric]) for s in seeds])
            bs = vals[idx].mean(axis=1)
            summary[metric+"_mean"] = float(vals.mean())
            summary[metric+"_CI95_low"],summary[metric+"_CI95_high"] = _q(bs)
        summaries.append(summary); by_group[key] = (nums,dens,boot_num,boot_den)
        point_s[key] = summary["S_plus_pooled"]
        # Keep one draw vector for all paired factorial contrasts.
        by_group[key] = (*by_group[key], np.divide(boot_num,boot_den,
            out=np.full_like(boot_num,np.nan),where=boot_den>0))

    contrasts=[]
    # Shared bootstrap indices preserve seed pairing for every calendar contrast.
    for classifier,rho,alpha,n_l2,policy in sorted({k[:5] for k in groups}):
        k24=(classifier,rho,alpha,n_l2,policy,"L2_24x7")
        k85=(classifier,rho,alpha,n_l2,policy,"L2_8x5_Mon_Fri_09_17")
        n0,d0,bn0,bd0,v0=by_group[k24]; n1,d1,bn1,bd1,v1=by_group[k85]
        delta=v1-v0; delta=delta[np.isfinite(delta)]
        contrasts.append({"classifier_id":classifier,"rho_L1":rho,"alpha":alpha,"n_L2":n_l2,"policy":policy,
                          "contrast":"8x5_minus_24x7_S_plus","S_plus_difference":n1.sum()/d1.sum()-n0.sum()/d0.sum(),
                          "CI95_low":_q(delta)[0],"CI95_high":_q(delta)[1],"paired_seed_blocks":len(seeds)})
    factor_contrasts=[]
    def emit(kind, classifier, rho, alpha, n_l2, calendar, contrast, left_key, right_key,
             difference_arrays, point_delta, policy=None):
        arr=np.asarray(difference_arrays,dtype=float); arr=arr[np.isfinite(arr)]
        factor_contrasts.append({"contrast_type":kind,"classifier_id":classifier,"rho_L1":rho,
            "alpha":alpha,"n_L2":n_l2,"calendar":calendar,"contrast":contrast,
            "policy":policy or "all","estimate":float(point_delta),"CI95_low":_q(arr)[0],"CI95_high":_q(arr)[1],
            "paired_seed_blocks":len(seeds)})
    classifiers=sorted({k[0] for k in groups})
    for classifier,rho,alpha,n_l2 in sorted({k[:4] for k in groups}):
      for calendar in CONFIG["calendar_conditions"]:
        for label,left,right in (("P1-D1","P1","D1"),("WAPS-D1","WAPS","D1"),("WAPS-P1","WAPS","P1")):
            kl=(classifier,rho,alpha,n_l2,left,calendar); kr=(classifier,rho,alpha,n_l2,right,calendar)
            vl=by_group[kl][4]; vr=by_group[kr][4]
            emit("policy",classifier,rho,alpha,n_l2,calendar,label,kl,kr,vl-vr,
                 point_s[kl]-point_s[kr])
        for label,left,right in (("P1-D1","P1","D1"),("WAPS-D1","WAPS","D1")):
            k_l24=(classifier,rho,alpha,n_l2,left,"L2_24x7"); k_r24=(classifier,rho,alpha,n_l2,right,"L2_24x7")
            k_l85=(classifier,rho,alpha,n_l2,left,"L2_8x5_Mon_Fri_09_17"); k_r85=(classifier,rho,alpha,n_l2,right,"L2_8x5_Mon_Fri_09_17")
            triple=(by_group[k_l85][4]-by_group[k_r85][4])-(by_group[k_l24][4]-by_group[k_r24][4])
            point=(point_s[k_l85]-point_s[k_r85])-(point_s[k_l24]-point_s[k_r24])
            emit("policy_by_calendar_interaction",classifier,rho,alpha,n_l2,"8x5-minus-24x7",label,
                 k_l85,k_r85,triple,point)
      # Classifier × calendar contrasts, at fixed policy and other factors.
      for ca,cb in itertools.combinations(classifiers,2):
        for policy in CONFIG["policies"]:
          ka24=(ca,rho,alpha,n_l2,policy,"L2_24x7"); ka85=(ca,rho,alpha,n_l2,policy,"L2_8x5_Mon_Fri_09_17")
          kb24=(cb,rho,alpha,n_l2,policy,"L2_24x7"); kb85=(cb,rho,alpha,n_l2,policy,"L2_8x5_Mon_Fri_09_17")
          inter=(by_group[kb85][4]-by_group[kb24][4])-(by_group[ka85][4]-by_group[ka24][4])
          point=(point_s[kb85]-point_s[kb24])-(point_s[ka85]-point_s[ka24])
          emit("classifier_by_calendar_interaction",f"{ca} vs {cb}",rho,alpha,n_l2,policy,
               "difference_in_calendar_effect",ka85,kb85,inter,point)
      for ca,cb in itertools.combinations(classifiers,2):
        for policy_pair,left,right in (("P1-D1","P1","D1"),("WAPS-D1","WAPS","D1")):
          # Three-way classifier × policy × calendar interaction.
          def policy_calendar(classifier, pol):
            a24=(classifier,rho,alpha,n_l2,pol,"L2_24x7"); b24=(classifier,rho,alpha,n_l2,"D1","L2_24x7")
            a85=(classifier,rho,alpha,n_l2,pol,"L2_8x5_Mon_Fri_09_17"); b85=(classifier,rho,alpha,n_l2,"D1","L2_8x5_Mon_Fri_09_17")
            return ((by_group[a85][4]-by_group[b85][4])-(by_group[a24][4]-by_group[b24][4]),
                    (point_s[a85]-point_s[b85])-(point_s[a24]-point_s[b24]))
          va,pa=policy_calendar(ca,left); vb,pb=policy_calendar(cb,left)
          emit("classifier_policy_calendar_interaction",f"{ca} vs {cb}",rho,alpha,n_l2,
               "8x5-minus-24x7",f"({left}-D1) interaction",None,None,vb-va,pb-pa)
    for classifier,rho,n_l2,policy,calendar in sorted({(k[0],k[1],k[3],k[4],k[5]) for k in groups}):
      ka=(classifier,rho,.25,n_l2,policy,calendar); kb=(classifier,rho,1.0,n_l2,policy,calendar)
      emit("alpha_sensitivity",classifier,rho,.25,n_l2,calendar,"alpha_0.25-minus-alpha_1.0",
           ka,kb,by_group[ka][4]-by_group[kb][4],point_s[ka]-point_s[kb],policy=policy)
    for classifier,alpha,n_l2,policy in sorted({(k[0],k[2],k[3],k[4]) for k in groups}):
      ka0=(classifier,.85,alpha,n_l2,policy,"L2_24x7"); kb0=(classifier,.85,alpha,n_l2,policy,"L2_8x5_Mon_Fri_09_17")
      ka1=(classifier,1.25,alpha,n_l2,policy,"L2_24x7"); kb1=(classifier,1.25,alpha,n_l2,policy,"L2_8x5_Mon_Fri_09_17")
      inter=(by_group[kb1][4]-by_group[ka1][4])-(by_group[kb0][4]-by_group[ka0][4])
      point=(point_s[kb1]-point_s[ka1])-(point_s[kb0]-point_s[ka0])
      emit("calendar_by_rho_interaction",classifier,1.25,alpha,n_l2,"both",
           "calendar_effect_rho1.25-minus-rho0.85",ka1,kb1,inter,point)
    return summaries, contrasts, factor_contrasts


def run(seed_count=None, output=OUT, seed_offset=0, save_task_details=False):
    start=time.time(); output.mkdir(parents=True,exist_ok=True)
    nseed=int(CONFIG["seed_blocks"] if seed_count is None else seed_count)
    if not 1 <= nseed <= int(CONFIG["seed_blocks"]): raise ValueError("invalid seed count")
    if seed_offset < 0 or seed_offset+nseed > int(CONFIG["seed_blocks"]):
        raise ValueError("seed range falls outside the prespecified seed blocks")
    seed_ids=list(range(int(CONFIG["seed_base"])+seed_offset,
                        int(CONFIG["seed_base"])+seed_offset+nseed))
    points=CONFIG["classifiers"]
    l1,l2ref,l1services,l2refservices=build_roster(n_l1=int(CONFIG["n_L1"]),n_l2=int(CONFIG["n_L2"][0]),mean_eligible_projects=BASE_ELIGIBILITY)
    mu_l1=effective_capacity(l1,l1services,PROJECT_MIX)["max_common_arrivals_per_h"]
    original_horizon=old.frozen.CONFIG["horizon_h"]
    original_d1=allocation_module._dispatch_d1
    original_calendar_d1=availability_module._dispatch_d1
    old.frozen.CONFIG["horizon_h"]=H
    # Candidate lookup optimization only; the focused regression test proves
    # exact dispatch pairs, trace objects, and RNG state against frozen D1.
    allocation_module._dispatch_d1=dispatch_d1_fast
    availability_module._dispatch_d1=dispatch_d1_fast
    rows=[]; trace_rows=[]; task_count=0
    l2_rosters={}
    for n_l2 in CONFIG["n_L2"]:
        _, roster, _, services = build_roster(n_l1=int(CONFIG["n_L1"]), n_l2=int(n_l2),
                                               mean_eligible_projects=BASE_ELIGIBILITY)
        l2_rosters[int(n_l2)] = (roster, services)
    task_path=output/"l2_tasks.csv"
    if save_task_details:
        task_path.parent.mkdir(parents=True,exist_ok=True)
    task_fields=["classifier_id","rho_L1","alpha","n_L2","policy","calendar","seed","alert_id",
                 "status","analyst_id","l1_completion","start","completion","deadline",
                 "service_effective_h","remaining_service_h","suspension_h","need_hidden","recommendation",
                 "trace_sha256","recommendation_hash","need_hash","l1_assignment_hash"]
    try:
        task_context = task_path.open("w",newline="",encoding="utf-8") if save_task_details else None
        try:
          if task_context:
           task_stream=task_context
           task_writer=csv.DictWriter(task_stream,fieldnames=task_fields,lineterminator="\n")
           task_writer.writeheader()
          else:
           task_stream=None; task_writer=None
          # Keep only one seed's traces/assignments resident; episode summaries
          # are retained for paired block bootstrap, task details stream to CSV.
          for rho in CONFIG["rho_L1"]:
            for seed in seed_ids:
              base_trace,_,_=_make_trace(seed,points[0],float(rho))
              l1_for_seed={policy:_run_l1(base_trace,l1,l1services,policy,seed,mu_l1)
                           for policy in CONFIG["policies"]}
              for point in points:
                trace,_,_=_make_trace(seed,point,float(rho))
                trace_rows.append({"rho_L1":rho,"classifier_id":point["id"],"seed":seed,
                    "alerts":len(trace),"trace_sha256":old.frozen._trace_hash(trace,include_recommendation=True),
                    "exogenous_sha256":old.frozen._trace_hash(trace,include_recommendation=False),
                    "recommendation_sha256":_hash(tuple((r.routed.alert.alert_id,r.routed.soctra_recommendation) for r in trace)),
                    "need_sha256":_hash(tuple((r.routed.alert.alert_id,r.true_escalation_need) for r in trace))})
                for n_l2 in CONFIG["n_L2"]:
                  l2,l2services=l2_rosters[int(n_l2)]
                  for policy in CONFIG["policies"]:
                    for alpha in CONFIG["alpha"]:
                      for calendar in CONFIG["calendar_conditions"]:
                        row=_run_condition(trace,point,float(rho),float(alpha),int(n_l2),policy,seed,
                            l1,l1services,l2,l2services,mu_l1,calendar,l1_for_seed[policy])
                        rows.append({k:v for k,v in row.items() if k!="l2_tasks"})
                        if save_task_details:
                          for trow in row["l2_tasks"]:
                            task_writer.writerow({**row["condition"],**trow,
                                "trace_sha256":row["trace_hash"],"recommendation_hash":row["recommendation_hash"],
                                "need_hash":row["need_hash"],"l1_assignment_hash":row["l1_assignment_hash"]})
                            task_count+=1
                        if len(rows)%500==0:
                          if task_stream: task_stream.flush()
                          print(f"campaign episodes={len(rows)} tasks={task_count}",flush=True)
        finally:
          if task_context: task_context.close()
        expected=len(seed_ids)*len(points)*len(CONFIG["rho_L1"])*len(CONFIG["n_L2"])*len(CONFIG["policies"])*len(CONFIG["alpha"])*len(CONFIG["calendar_conditions"])
        if len(rows)!=expected: raise AssertionError(f"episode rows {len(rows)} != {expected}")
        # Pairing gates: each calendar pair shares every exogenous hash and L1 trajectory.
        pairs=defaultdict(list)
        for r in rows:
            c=r["condition"]; pairs[(c["classifier_id"],c["rho_L1"],c["alpha"],c["n_L2"],c["policy"],c["seed"])].append(r)
        failures=[]
        for key,pair in pairs.items():
            if len(pair)!=2 or len({x["trace_hash"] for x in pair})!=1 or len({x["l1_assignment_hash"] for x in pair})!=1:
                failures.append((key,"paired input mismatch"))
            if len({(x["admitted"],x["TP"],x["FP"],x["FN"],x["TN"],x["S_plus_denominator"]) for x in pair})!=1:
                failures.append((key,"confusion/Splus denominator mismatch"))
            if any(x["max_deadline_admitted_h"]>CUTOFF for x in pair): failures.append((key,"deadline not mature"))
        if failures: raise AssertionError(f"paired validation failures: {failures[:10]}")
        summaries,contrasts,factor_contrasts=_summarize(rows,int(CONFIG["bootstrap"]["replicates"]),int(CONFIG["bootstrap"]["seed"]))
        episode_export=[]
        for r in rows:
            episode_export.append({**r["condition"], **{k:v for k,v in r.items() if k!="condition"}})
        _write(output/"episodes.csv",episode_export)
        _write(output/"trace_audit.csv",trace_rows)
        _write(output/"summary_by_condition.csv",summaries)
        _write(output/"paired_calendar_contrasts.csv",contrasts)
        _write(output/"paired_factor_contrasts.csv",factor_contrasts)
        elapsed=time.time()-start
        code_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
        checks={"status":"PASS","episode_rows":len(rows),"task_rows":task_count,
            "paired_seed_blocks":nseed,"expected_episode_rows":expected,"trace_records":len(trace_rows),
            "calendar_pair_checks":"PASS","recommendation_need_deadline_and_L1_assignment_pairing":"PASS",
            "all_admitted_deadlines_mature_before_cutoff":True,"admission_h":H,"evaluation_cutoff_h":CUTOFF,
            "terminal_drain_h":0,"seed_ids":[seed_ids[0],seed_ids[-1]],"elapsed_seconds":elapsed,
            "regression_source_commit":"9772abae1bfcd2c810760e68ecd8fba107d320f0",
            "code_commit":code_commit,"all_final_state_categories_reported":True}
        (output/"validation_checks.json").write_text(json.dumps(checks,indent=2)+"\n")
        (output/"execution_manifest.json").write_text(json.dumps({"config":CONFIG,"checks":checks,
             "code_commit":code_commit,"synthetic_only":True},indent=2)+"\n")
        print(f"wrote {len(rows)} episodes and {task_count} L2 tasks in {elapsed:.1f}s",flush=True)
    finally:
        old.frozen.CONFIG["horizon_h"]=original_horizon
        allocation_module._dispatch_d1=original_d1
        availability_module._dispatch_d1=original_calendar_d1


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--seed-count",type=int,default=None,help="seed blocks in this run; default full 400")
    parser.add_argument("--seed-offset",type=int,default=0,help="zero-based offset into paired campaign seeds")
    parser.add_argument("--output-dir",type=Path,default=OUT)
    parser.add_argument("--save-task-details",action="store_true")
    args=parser.parse_args()
    out=args.output_dir if args.output_dir.is_absolute() else ROOT/args.output_dir
    run(args.seed_count,out,args.seed_offset,args.save_task_details)
