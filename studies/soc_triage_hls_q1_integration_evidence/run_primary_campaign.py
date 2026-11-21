"""Run the prespecified, paired FP-workload sensitivity campaign.

SOCTRA is not rerun. Published rates are synthetic Bernoulli inputs. The
experiment-only L2 driver imports the frozen D1/P1 dispatchers and preserves
all historical result files.
"""
from __future__ import annotations
import csv, hashlib, json, math, random, statistics, sys, time
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from hls.rq1_allocation import HLSBConfig, simulate  # noqa: E402
from hls.rq1_l1_l2 import simulate_l1_l2  # noqa: E402
from studies.soc_triage_organization_coupling import run_pilot as frozen  # noqa: E402
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity  # noqa: E402
from studies.soc_human_ai_organization.soc_parametric_baseline import (  # noqa: E402
    BASE_DEADLINES_H, BASE_ELIGIBILITY, BASE_L1_ANALYSTS, BASE_L2_ANALYSTS,
    BASE_SERVICE_L1_H, BASE_SERVICE_L2_H, PROJECTS, PROJECT_MIX, REFERENCE,
    build_roster,
)
from studies.soc_triage_hls_q1_integration_evidence.fp_workload_engine import simulate_l2_hidden_work  # noqa: E402

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config" / "primary_campaign.json").read_text())
OUT = ROOT / "results" / "soc_triage_hls_q1_integration_evidence"
POLICIES = tuple(CONFIG["simulation"]["policies"])
ALPHAS = tuple(CONFIG["simulation"]["fp_service_fraction_alpha"])
H = float(CONFIG["simulation"]["horizon_h"])
DRAIN = float(CONFIG["simulation"]["drain_h"])
CUTOFF = H + DRAIN
PI = float(CONFIG["prevalence"]["pi"])
BOOT_REPS = int(CONFIG["statistics"]["bootstrap"]["replicates"])
BOOT_SEED = int(CONFIG["statistics"]["bootstrap"]["seed"])


def _write(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty output {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for row in rows for k in row)), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def _sha(rows) -> str:
    return hashlib.sha256(repr(tuple(rows)).encode()).hexdigest()


def _expected_class_factors(point: dict, alpha: float) -> dict:
    factors = {}
    for task_class in PROJECTS:
        pos = PI * point["pD"] + (1.0 - PI) * point["pFA"]
        tp_fraction = PI * point["pD"] / pos if pos else 0.0
        fp_fraction = (1.0 - PI) * point["pFA"] / pos if pos else 0.0
        factors[task_class] = tp_fraction + alpha * fp_fraction if pos else 1.0
    return factors


def _primary_trace(seed: int, point: dict):
    prev = {"pi": PI, "need_by_class": tuple(PI for _ in PROJECTS)}
    trace, rate = frozen._make_trace(rho_l1=float(CONFIG["simulation"]["rho_L1"]),
                                     seed=int(seed), prevalence=prev, point=point)
    return trace, prev, rate


def _run_l1(trace, policy: str, seed: int, l1, l1_services, mu_l1: float):
    kwargs = {}
    if policy == "HLS-B":
        raw = CONFIG["simulation"]["waps"]
        kwargs["hlsb_config"] = HLSBConfig(**raw, capacity_per_h=mu_l1)
    return simulate(tuple(row.routed.alert for row in trace), l1, BASE_SERVICE_L1_H,
                    policy=policy, admission_horizon=H, drain_period=DRAIN,
                    random_seed=seed, service_by_analyst_class=l1_services,
                    **kwargs)


def _summary_trace_hash(trace):
    exogenous = frozen._trace_hash(trace, include_recommendation=False)
    complete = frozen._trace_hash(trace, include_recommendation=True)
    return exogenous, complete


def _episode(trace, point, alpha, n_l2, policy, seed, l1_sim, l1, l2, l2_services, mu_l1):
    base_class_mean = {}
    for k in PROJECTS:
        base_class_mean[k] = statistics.mean(l2_services[a.analyst_id][k] for a in l2 if k in a.eligible_classes)
    factors = _expected_class_factors(point, alpha)
    forecast = {a.analyst_id: {k: l2_services[a.analyst_id][k] * factors[k] for k in a.eligible_classes}
                for a in l2}
    _, routed_mix = frozen._expected_route_mix(tuple(PI for _ in PROJECTS), point["pD"], point["pFA"])
    mu_l2 = effective_capacity(l2, forecast, routed_mix)["max_common_arrivals_per_h"]
    route = {row.routed.alert.alert_id: bool(row.routed.soctra_recommendation) for row in trace}
    need = {row.routed.alert.alert_id: bool(row.true_escalation_need) for row in trace}
    by_id = {row.routed.alert.alert_id: row for row in trace}
    l1_jobs = {job.alert_id: job for job in l1_sim.assignments}
    l2_arrivals = []
    for row in trace:
        alert = row.routed.alert
        job = l1_jobs.get(alert.alert_id)
        if alert.arrival < H and route[alert.alert_id] and job is not None and job.completion < CUTOFF:
            l2_arrivals.append(type(alert)(alert.alert_id, job.completion, alert.task_class, alert.deadline))
    l2_need = {a.alert_id: need[a.alert_id] for a in l2_arrivals}
    l2_scale = {a.alert_id: (1.0 if need[a.alert_id] else alpha) for a in l2_arrivals}
    cfg = CONFIG["simulation"]["waps"]
    hcfg = HLSBConfig(**cfg, capacity_per_h=mu_l2) if policy == "HLS-B" else None
    l2_sim = simulate_l2_hidden_work(
        l2_arrivals, l2_need, l2, l2_services, forecast, l2_scale,
        policy=policy, horizon=CUTOFF, seed=seed, hlsb_config=hcfg,
    )
    l2_jobs = {job.alert_id: job for job in l2_sim.assignments}
    admitted = [row for row in trace if row.routed.alert.arrival < H]
    total_need = sum(need[row.routed.alert.alert_id] for row in admitted)
    tp = sum(need[row.routed.alert.alert_id] and route[row.routed.alert.alert_id] for row in admitted)
    fp = sum(not need[row.routed.alert.alert_id] and route[row.routed.alert.alert_id] for row in admitted)
    fn = total_need - tp
    tn = len(admitted) - tp - fp - fn
    timely_need_ids = set()
    timely_necessary_quality = 0.0
    timely_routed = 0
    completed_routed = 0
    l2_completed_at_H = 0
    for row in admitted:
        a = row.routed.alert; aid = a.alert_id
        first = l1_jobs.get(aid)
        if not first or first.completion > CUTOFF:
            continue
        final = first
        if route[aid]:
            final = l2_jobs.get(aid)
            if final is None or final.completion > CUTOFF:
                continue
        completed_routed += 1
        if final.completion <= a.deadline:
            timely_routed += 1
            if need[aid] and route[aid]:
                timely_need_ids.add(aid)
                timely_necessary_quality += final.competence * (1.0 - 0.35 * row.difficulty)
        if route[aid] and final.completion <= H:
            l2_completed_at_H += 1
    terminal_jobs = {a.alert_id: a for a in l2_arrivals}
    l2_backlog_H = sum(a.arrival <= H and (a.alert_id not in l2_jobs or l2_jobs[a.alert_id].completion > H)
                       for a in l2_arrivals)
    l1_backlog_H = sum(a.alert_id not in l1_jobs or l1_jobs[a.alert_id].completion > H
                       for a in (row.routed.alert for row in admitted))
    l1_backlog_terminal = sum(a.alert_id not in l1_jobs or l1_jobs[a.alert_id].completion > CUTOFF
                              for a in (row.routed.alert for row in admitted))
    l2_backlog_terminal = sum(a.alert_id not in l2_jobs or l2_jobs[a.alert_id].completion > CUTOFF
                              for a in l2_arrivals)
    true_ids = {row.routed.alert.alert_id for row in admitted if need[row.routed.alert.alert_id]}
    tp_ids = true_ids & {row.routed.alert.alert_id for row in admitted if route[row.routed.alert.alert_id]}
    fp_ids = {row.routed.alert.alert_id for row in admitted if (not need[row.routed.alert.alert_id] and route[row.routed.alert.alert_id])}
    fn_ids = true_ids - tp_ids
    generated_ids = set(terminal_jobs)
    generated_fp_ids = fp_ids & generated_ids
    generated_tp_ids = tp_ids & generated_ids
    l2_work_offered = sum(base_class_mean[terminal_jobs[aid].task_class] * l2_scale[aid] for aid in terminal_jobs)
    fp_work = sum(base_class_mean[by_id[aid].routed.alert.task_class] * alpha for aid in generated_fp_ids)
    tp_work = sum(base_class_mean[by_id[aid].routed.alert.task_class] for aid in generated_tp_ids)
    fn_work_omitted = sum(base_class_mean[by_id[aid].routed.alert.task_class] for aid in fn_ids)
    service_exec = sum(max(0.0, min(j.completion, CUTOFF) - j.start) for j in l2_sim.assignments)
    util_l2_H = statistics.mean(
        sum(max(0.0, min(j.completion, H) - j.start) for j in l2_sim.assignments if j.analyst_id == a.analyst_id) / H
        for a in l2
    )
    util_l2_terminal = statistics.mean(
        sum(max(0.0, min(j.completion, CUTOFF) - j.start) for j in l2_sim.assignments if j.analyst_id == a.analyst_id) / CUTOFF
        for a in l2
    )
    _, trace_hash = _summary_trace_hash(trace)
    exog_hash, _ = _summary_trace_hash(trace)
    positive_by_class = frozen._expected_route_mix(tuple(PI for _ in PROJECTS), point["pD"], point["pFA"])[1]
    return {
        "label_definition": "standardized", "prevalence_scenario": "19_of_14449_standardized_test", "pi": PI,
        "classifier_id": point["id"], "algorithm": point["algorithm"], "features": point["features"],
        "cost_regime": "symmetric", "pD_target": point["pD"], "pFA_target": point["pFA"], "BA_published": point["BA"],
        "alpha_fp_service_fraction": alpha, "rho_L1": CONFIG["simulation"]["rho_L1"], "n_L1": BASE_L1_ANALYSTS,
        "n_L2": n_l2, "policy": policy, "seed": seed, "admitted": len(admitted), "true_need_count": total_need,
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "pD_realized": tp / total_need if total_need else "", "pFA_realized": fp / (len(admitted)-total_need) if len(admitted)>total_need else "",
        "recommendations": tp + fp, "l2_tasks_generated_by_terminal": len(l2_arrivals),
        "l2_tasks_assigned": len(l2_sim.assignments), "l2_tasks_completed_by_terminal": sum(j.completion <= CUTOFF for j in l2_sim.assignments),
        "l2_tasks_completed_by_H": l2_completed_at_H, "l1_tasks_assigned": len(l1_jobs),
        "timely_needs_numerator": len(timely_need_ids), "S_plus_per_seed": len(timely_need_ids)/total_need if total_need else "",
        "S_plus_denominator": total_need, "necessary_correct_timely_per_admitted": len(timely_need_ids)/len(admitted) if admitted else 0.0,
        "necessary_quality_timely_per_admitted": timely_necessary_quality/len(admitted) if admitted else 0.0,
        "routed_task_SLA_terminal": timely_routed/len(admitted) if admitted else 0.0,
        "routed_task_completion_terminal": completed_routed/len(admitted) if admitted else 0.0,
        "L1_backlog_H": l1_backlog_H, "L2_backlog_H": l2_backlog_H,
        "L1_backlog_terminal": l1_backlog_terminal, "L2_backlog_terminal": l2_backlog_terminal,
        "L2_work_offered_class_mean_h": l2_work_offered, "L2_unnecessary_FP_work_h": fp_work,
        "L2_necessary_TP_work_h": tp_work, "L2_omitted_FN_work_h": fn_work_omitted,
        "L1_service_hours_executed_by_H": sum(max(0.0,min(j.completion,H)-j.start) for j in l1_sim.assignments),
        "L1_service_hours_executed_by_terminal": sum(max(0.0,min(j.completion,CUTOFF)-j.start) for j in l1_sim.assignments),
        "L2_service_hours_executed_by_terminal": service_exec,
        "utilization_L1_mean_H": statistics.mean(v for _aid,v in l1_sim.at_horizon.utilization_by_analyst),
        "utilization_L1_mean_terminal": statistics.mean(v for _aid,v in l1_sim.after_drain.utilization_by_analyst),
        "utilization_L2_mean_H": util_l2_H, "utilization_L2_mean_terminal": util_l2_terminal,
        "mu_L1_effective_per_h": mu_l1, "mu_L2_effective_per_h_alpha_adjusted": mu_l2,
        "lambda_L1_per_h": mu_l1 * float(CONFIG["simulation"]["rho_L1"]),
        "lambda_L2_offered_per_h": mu_l1 * float(CONFIG["simulation"]["rho_L1"]) * (PI*point["pD"]+(1-PI)*point["pFA"]),
        "rho_L2_offered_alpha_adjusted": (mu_l1 * float(CONFIG["simulation"]["rho_L1"]) * (PI*point["pD"]+(1-PI)*point["pFA"]) / mu_l2) if mu_l2 else 0.0,
        "P1_fraction_of_policy_dispatch_epochs": l2_sim.p1_dispatch_epochs/l2_sim.dispatch_epochs if l2_sim.dispatch_epochs else 0.0,
        "WAPS_mode_switch_count": len(l2_sim.switches), "WAPS_switch_times_h": ";".join(f"{x.time:.6f}" for x in l2_sim.switches),
        "exogenous_sha256": exog_hash, "trace_sha256": trace_hash,
        "terminal_cutoff_h": CUTOFF, "max_deadline_h": max((row.routed.alert.deadline for row in trace), default=0.0),
    }


def bootstrap_indices(seed_ids):
    rng = np.random.default_rng(BOOT_SEED)
    return rng.integers(0, len(seed_ids), size=(BOOT_REPS, len(seed_ids)))


def _quantiles(values):
    return float(np.quantile(values, .025)), float(np.quantile(values, .975))


def _aggregate(rows, idx):
    ordered = sorted(rows, key=lambda r: int(r["seed"]))
    vals = np.zeros(BOOT_REPS)
    nums = np.array([int(r["timely_needs_numerator"]) for r in ordered])
    dens = np.array([int(r["S_plus_denominator"]) for r in ordered])
    boot_num = nums[idx].sum(axis=1)
    boot_den = dens[idx].sum(axis=1)
    valid = boot_den > 0
    vals[valid] = boot_num[valid] / boot_den[valid]
    vals[~valid] = np.nan
    point_den = int(dens.sum()); point_num = int(nums.sum())
    return point_num, point_den, point_num/point_den if point_den else math.nan, vals


def summarize(episodes):
    seed_ids = sorted({int(r["seed"]) for r in episodes})
    idx = bootstrap_indices(seed_ids)
    groups = defaultdict(list)
    for r in episodes:
        groups[(r["classifier_id"], float(r["alpha_fp_service_fraction"]), int(r["n_L2"]), r["policy"])].append(r)
    summaries=[]
    boot_splus={}
    for key, rows in sorted(groups.items()):
        classifier, alpha, n_l2, policy = key
        num, den, point, boot = _aggregate(rows, idx)
        boot_splus[key] = boot
        tp_total=sum(int(r["TP"]) for r in rows); fp_total=sum(int(r["FP"]) for r in rows)
        fn_total=sum(int(r["FN"]) for r in rows); tn_total=sum(int(r["TN"]) for r in rows)
        n_total=sum(int(r["admitted"]) for r in rows)
        row={"classifier_id":classifier,"alpha":alpha,"n_L2":n_l2,"policy":policy,
             "seeds":len(rows),"zero_need_seeds":sum(int(r["S_plus_denominator"])==0 for r in rows),
             "admitted_total":n_total,"TP_total":tp_total,"FP_total":fp_total,"FN_total":fn_total,"TN_total":tn_total,
             "pD_realized_pooled":tp_total/den if den else math.nan,
             "pFA_realized_pooled":fp_total/(n_total-den) if n_total>den else math.nan,
             "recommendations_total":tp_total+fp_total,"timely_needs":num,"total_needs":den,"S_plus_pooled":point,
             "S_plus_CI95_low":_quantiles(boot[np.isfinite(boot)])[0],"S_plus_CI95_high":_quantiles(boot[np.isfinite(boot)])[1],
         "zero_denominator_bootstrap_replicates":int(np.isnan(boot).sum())}
        for metric in ["necessary_correct_timely_per_admitted","necessary_quality_timely_per_admitted","routed_task_SLA_terminal",
                       "L2_work_offered_class_mean_h","L2_unnecessary_FP_work_h","L2_omitted_FN_work_h",
                       "L1_backlog_H","L2_backlog_H","L1_backlog_terminal","L2_backlog_terminal",
                       "utilization_L1_mean_H","utilization_L1_mean_terminal","utilization_L2_mean_H","utilization_L2_mean_terminal","rho_L2_offered_alpha_adjusted",
                       "P1_fraction_of_policy_dispatch_epochs","WAPS_mode_switch_count"]:
            vals=np.array([float(r[metric]) for r in sorted(rows,key=lambda r:int(r["seed"]))])
            bs=vals[idx].mean(axis=1)
            row[metric+"_mean"]=float(vals.mean())
            row[metric+"_CI95_low"],row[metric+"_CI95_high"]=_quantiles(bs)
        summaries.append(row)
    contrasts=[]; interactions=[]
    classifiers=sorted({r["classifier_id"] for r in episodes})
    for classifier in classifiers:
      for alpha in ALPHAS:
       for n_l2 in CONFIG["simulation"]["n_L2"]:
        for contrast_name,left,right in (("WAPS-D1","HLS-B","D1"),("P1-D1","P1","D1"),("WAPS-P1","HLS-B","P1")):
         b1=boot_splus[(classifier,alpha,n_l2,left)]; b0=boot_splus[(classifier,alpha,n_l2,right)]
         keep=np.isfinite(b1)&np.isfinite(b0); d=b1[keep]-b0[keep]
         point_left=next(x["S_plus_pooled"] for x in summaries if x["classifier_id"]==classifier and x["alpha"]==alpha and x["n_L2"]==n_l2 and x["policy"]==left)
         point_right=next(x["S_plus_pooled"] for x in summaries if x["classifier_id"]==classifier and x["alpha"]==alpha and x["n_L2"]==n_l2 and x["policy"]==right)
         contrast={"classifier_id":classifier,"alpha":alpha,"n_L2":n_l2,"contrast":contrast_name,
                   "S_plus_difference":float(point_left-point_right),
                   "bootstrap_CI95_low":_quantiles(d)[0],"bootstrap_CI95_high":_quantiles(d)[1],"bootstrap_replicates":len(d)}
         contrasts.append(contrast)
        for a,b in ((classifiers[0],classifiers[1]),(classifiers[0],classifiers[2]),(classifiers[1],classifiers[2])):
         w_a=boot_splus[(a,alpha,n_l2,"HLS-B")]-boot_splus[(a,alpha,n_l2,"D1")]
         w_b=boot_splus[(b,alpha,n_l2,"HLS-B")]-boot_splus[(b,alpha,n_l2,"D1")]
         dd=w_b-w_a; dd=dd[np.isfinite(dd)]
         interactions.append({"classifier_A":a,"classifier_B":b,"alpha":alpha,"n_L2":n_l2,
                              "difference_in_WAPS_minus_D1_S_plus":float(dd.mean()),
                              "bootstrap_CI95_low":_quantiles(dd)[0],"bootstrap_CI95_high":_quantiles(dd)[1],
                              "bootstrap_replicates":len(dd)})
    return summaries,contrasts,interactions


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    start=time.time(); points=CONFIG["classifiers"]
    seed_ids=list(range(int(CONFIG["simulation"]["seed_base"]),int(CONFIG["simulation"]["seed_base"])+int(CONFIG["simulation"]["n_new_paired_seeds"])))
    l1,l2_reference,l1s_reference,l2s_reference=build_roster(n_l1=BASE_L1_ANALYSTS,n_l2=int(CONFIG["simulation"]["n_L2"][0]),mean_eligible_projects=BASE_ELIGIBILITY)
    mu_l1=effective_capacity(l1,l1s_reference,PROJECT_MIX)["max_common_arrivals_per_h"]
    rows=[]; trace_audit={}; l1_cache={}
    # The fixed L1 roster is independent of L2 capacity; compute each paired
    # seed/policy trajectory once and reuse it across points, alpha and rosters.
    for seed in seed_ids:
      seed_trace,_prev,_rate=_primary_trace(seed,points[0])
      for policy in POLICIES:
        l1_cache[(seed,policy)]=_run_l1(seed_trace,policy,seed,l1,l1s_reference,mu_l1)
    for n_l2 in CONFIG["simulation"]["n_L2"]:
      _l1,l2,l1s_current,l2s=build_roster(n_l1=BASE_L1_ANALYSTS,n_l2=int(n_l2),mean_eligible_projects=BASE_ELIGIBILITY)
      for point in points:
       for seed in seed_ids:
        trace,prev,_rate=_primary_trace(seed,point)
        exog,full=_summary_trace_hash(trace)
        trace_audit[(point["id"],seed)]=(exog,full,len(trace),sum(bool(r.true_escalation_need) for r in trace))
        for policy in POLICIES:
         l1_sim=l1_cache[(seed,policy)]
         for alpha in ALPHAS:
          rows.append(_episode(trace,point,alpha,int(n_l2),policy,seed,l1_sim,l1,l2,l2s,mu_l1))
    expected=len(points)*len(seed_ids)*len(CONFIG["simulation"]["n_L2"])*len(POLICIES)*len(ALPHAS)
    if len(rows)!=expected: raise AssertionError(f"episode count {len(rows)} != {expected}")
    grouped=defaultdict(list)
    for r in rows:
      grouped[(r["classifier_id"],r["alpha_fp_service_fraction"],r["n_L2"],r["seed"])].append(r)
    failures=[]
    for k,rs in grouped.items():
      if len(rs)!=len(POLICIES): failures.append((k,"policy rows"))
      if len({r["exogenous_sha256"] for r in rs})!=1: failures.append((k,"exogenous trace"))
      if len({(r["admitted"],r["true_need_count"],r["TP"],r["FP"],r["FN"],r["TN"]) for r in rs})!=1: failures.append((k,"denominator/confusion"))
      for r in rs:
       if r["TP"]+r["FN"]!=r["true_need_count"] or r["TP"]+r["FP"]+r["FN"]+r["TN"]!=r["admitted"]: failures.append((k,"confusion identity"))
       if r["timely_needs_numerator"]>r["TP"]: failures.append((k,"Splus numerator"))
       if r["max_deadline_h"]>r["terminal_cutoff_h"]: failures.append((k,"deadline truncation"))
    # Exogenous arrivals/classes/severity/need/difficulty must match across classifier points.
    for seed in seed_ids:
      exogs={trace_audit[(p["id"],seed)][0] for p in points}
      if len(exogs)!=1: failures.append((seed,"common exogenous trace across classifier points"))
    if failures: raise AssertionError(f"validation failures: {failures[:10]}")
    # Persist fully validated episode data before post-processing so that a
    # summary/figure issue never requires rerunning the simulation campaign.
    _write(OUT/"episodes.csv",rows)
    summaries,contrasts,interactions=summarize(rows)
    _write(OUT/"summary_by_condition.csv",summaries)
    _write(OUT/"paired_policy_contrasts.csv",contrasts)
    _write(OUT/"classifier_organization_interactions.csv",interactions)
    trace_rows=[{"classifier_id":k[0],"seed":k[1],"exogenous_sha256":v[0],"trace_sha256":v[1],"alerts":v[2],"synthetic_needs":v[3]} for k,v in sorted(trace_audit.items())]
    _write(OUT/"trace_audit.csv",trace_rows)
    elapsed=time.time()-start
    checks={"status":"PASS","episode_rows":len(rows),"classifier_points":len(points),"alpha_levels":len(ALPHAS),
            "rosters":CONFIG["simulation"]["n_L2"],"policies":list(POLICIES),"paired_seed_count":len(seed_ids),
            "new_seed_ids":[seed_ids[0],seed_ids[-1]],"zero_need_seed_cells_per_trace":sum(v[3]==0 for v in trace_audit.values()),
            "denominator_confusion_trace_checks":"PASS","all_deadlines_mature_before_cutoff":True,
            "same_trace_and_confusion_across_policies":"PASS","common_random_numbers_across_classifiers":"stable per-alert triage uniform; trace audit stored",
            "alpha1_original_engine_equivalence":"see tests and validation run","HLS_policies_frozen":True,"SOCTRA_models_frozen":True,
            "elapsed_seconds":elapsed,"bootstrap_replicates":BOOT_REPS,"bootstrap_seed":BOOT_SEED}
    (OUT/"validation_checks.json").write_text(json.dumps(checks,indent=2)+"\n")
    (OUT/"execution_manifest.json").write_text(json.dumps({"config":CONFIG,"checks":checks,"input_source":"published aggregate rates only","no_historical_result_files_modified":True},indent=2)+"\n")
    print(f"wrote {len(rows)} episode rows in {elapsed:.1f}s; needs={sum(int(r['true_need_count']) for r in rows)} rows sum (repeated by policy/alpha/roster)")

if __name__ == "__main__":
    run()
