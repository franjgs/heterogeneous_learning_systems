"""Run the final exploratory SOC operating map using the existing simulator.

No policy or simulation-engine implementation is changed by this runner. The
script generates synthetic Poisson arrivals by regime and pairs D1/P1/HLS-B on
identical alert objects within every scenario and seed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from hls.ia_l1_l2_simulation import generate_alerts  # noqa: E402
from hls.rq1_allocation import HLSBConfig  # noqa: E402
from hls.rq1_l1_l2 import simulate_l1_l2  # noqa: E402
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster  # noqa: E402
from studies.soc_human_ai_organization.soc_parametric_baseline import (  # noqa: E402
    BASE_SERVICE_L1_H, BASE_SERVICE_L2_H, PROJECT_MIX, REFERENCE, build_roster,
)
from studies.soc_human_ai_organization.calibrate_a1_scenarios import (  # noqa: E402
    effective_capacity, routed_l2_shares,
)

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config/soc_hls_final_operating_map.json"
C = json.loads(CONFIG_PATH.read_text())
OUT = ROOT / "results/soc_hls_final_operating_map"
POLICIES = tuple(C["policies"])
BASE_L1, BASE_L2, BASE_S1, BASE_S2 = _roster([0, 1, 2, 3, 4, 5])
BASE_MU_L1 = effective_capacity(BASE_L1, BASE_S1, PROJECT_MIX)["max_common_arrivals_per_h"]
ROUTED_SHARE, ROUTED_MIX = routed_l2_shares()
BASE_MU_L2_TASK = effective_capacity(BASE_L2, BASE_S2, ROUTED_MIX)["max_common_arrivals_per_h"]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no records to save: {path}")
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def scenarios() -> list[dict]:
    result = []
    recovery = float(C["post_pulse_recovery_h"])
    start = float(C["pulse_start_h"])
    normal = float(C["rho_normal"])
    for rho in C["rho_high_grid"]:
        for duration in C["pulse_duration_grid_h"]:
            rho, duration = float(rho), int(duration)
            h = start + duration + recovery
            b = max(rho - 1.0, 0.0) * duration
            gamma = b / ((1.0 - normal) * recovery)
            if rho <= 1.0:
                region = "normal_or_capacity_edge"
            elif gamma >= 1.0:
                region = "congestion_severe"
            else:
                region = "congestion_operational"
            result.append({
                "profile": f"rho{int(round(rho*100)):03d}_d{duration:02d}",
                "rho_normal": normal, "rho_high": rho, "rho_recovery": normal,
                "pulse_start_h": start, "duration_h": duration,
                "recovery_h": recovery, "admission_h": h,
                "drain_h": float(C["drain_h"]), "B": b, "Gamma": gamma,
                "design_region": region,
            })
    return result


def deadline_map(sla: dict | None = None) -> dict[str, float]:
    if sla is None:
        return {k: float(v) for k, v in C["deadline_h_reference"].items()}
    return {"high": float(sla["T0"]), "medium": float(sla["T0"] * sla["f_high"]),
            "low": float(sla["T0"] * sla["f_low"])}


def make_trace(profile: dict, seed: int, arrival_mu: float,
               deadlines: dict[str, float]) -> tuple:
    start = profile["pulse_start_h"]
    pulse_end = start + profile["duration_h"]
    horizon = profile["admission_h"]
    segments = ((0.0, start, profile["rho_normal"]),
                (start, pulse_end, profile["rho_high"]),
                (pulse_end, horizon, profile["rho_recovery"]))
    alerts = []
    for ix, (lo, hi, rho) in enumerate(segments):
        if hi <= lo:
            continue
        cfg = replace(
            REFERENCE.scenario_config(arrival_rate_per_h=arrival_mu * rho),
            horizon=hi - lo,
            deadline_by_severity=tuple((k, deadlines[k]) for k in ("low", "medium", "high")),
        )
        for j, generated in enumerate(generate_alerts(cfg, seed * 100 + ix)):
            alert = generated.routed.alert
            alert = replace(alert, alert_id=f"{ix:02d}-{j:08d}",
                            arrival=alert.arrival + lo, deadline=alert.deadline + lo)
            alerts.append(replace(generated, routed=replace(generated.routed, alert=alert)))
    return tuple(sorted(alerts, key=lambda x: (x.routed.alert.arrival, x.routed.alert.alert_id)))


def trace_digest(alerts: tuple, include_deadline: bool = False) -> str:
    fingerprint = tuple((x.routed.alert.alert_id, x.routed.alert.arrival,
                         x.routed.alert.task_class,
                         *((x.routed.alert.deadline,) if include_deadline else ()),
                         x.routed.soctra_recommendation, x.severity, x.difficulty)
                        for x in alerts)
    return hashlib.sha256(repr(fingerprint).encode()).hexdigest()


def run_one(profile: dict, seed: int, policy: str, alerts: tuple,
            l1: tuple, l2: tuple, s1: dict, s2: dict,
            mu_l1: float, mu_l2_task: float, trace_hash: str,
            condition: dict) -> tuple[dict, list[dict], list[dict], list[dict], list[dict]]:
    h = profile["admission_h"]
    drain = profile["drain_h"]
    kw = dict(policy=policy, admission_horizon=h, drain_period=drain,
              coordination_latency=0.0, coordination_edge_cost=0.0,
              decision_mode="hypothetical_recommendation_acceptance",
              random_seed=seed, l1_service_by_analyst_class=s1,
              l2_service_by_analyst_class=s2)
    if policy == "HLS-B":
        kw.update(hlsb_l1_config=HLSBConfig(**C["hlsb"], capacity_per_h=mu_l1),
                  hlsb_l2_config=HLSBConfig(**C["hlsb"], capacity_per_h=mu_l2_task))
    sim = simulate_l1_l2(tuple(x.routed for x in alerts), l1, l2,
                         BASE_SERVICE_L1_H, BASE_SERVICE_L2_H, **kw)
    l1jobs = {x.alert_id: x for x in sim.l1_simulation.assignments}
    l2jobs = {x.alert_id: x for x in sim.l2_simulation.assignments}
    routes = {x.alert_id: x.scenario_routing_decision for x in sim.escalation_records}
    admitted = [x for x in alerts if x.routed.alert.arrival < h]
    finals = {x.routed.alert.alert_id:
              (l2jobs.get(x.routed.alert.alert_id) if routes[x.routed.alert.alert_id]
               else l1jobs.get(x.routed.alert.alert_id)) for x in admitted}

    def metric(group: list, cutoff: float) -> dict:
        timely = completed = quality = quality_completed = 0.0
        for x in group:
            aid = x.routed.alert.alert_id
            job = finals[aid]
            if job is None or job.completion > cutoff:
                continue
            value = job.competence * (1.0 - 0.35 * x.difficulty)
            completed += 1
            quality_completed += value
            if job.completion <= x.routed.alert.deadline:
                timely += 1
                quality += value
        n = len(group)
        return {"admitted": n, "completed": int(completed), "pending": int(n-completed),
                "SLA": timely/n if n else 0.0, "RN": quality/n if n else 0.0,
                "quality_completed": quality_completed/completed if completed else 0.0}

    def assigned_metrics(cutoff: float) -> tuple[int, int, float, float, int, int, float, float]:
        l1q = l2q = l1busy = l2busy = 0
        w1 = w2 = 0.0
        for x in admitted:
            aid = x.routed.alert.alert_id
            # Queue/work at t only includes alerts that have arrived by t.
            # Future arrivals remain part of terminal denominators, never of
            # instantaneous physical backlog.
            if x.routed.alert.arrival >= cutoff:
                continue
            first = l1jobs.get(aid)
            if first is None or first.completion > cutoff:
                l1q += int(first is None or first.start >= cutoff)
                w1 += BASE_SERVICE_L1_H[x.routed.alert.task_class]
                l1busy += int(first is not None and first.start <= cutoff < first.completion)
            if routes[aid] and first is not None and first.completion <= cutoff:
                second = l2jobs.get(aid)
                if second is None or second.completion > cutoff:
                    l2q += int(second is None or second.start >= cutoff)
                    w2 += BASE_SERVICE_L2_H[x.routed.alert.task_class]
                    l2busy += int(second is not None and second.start <= cutoff < second.completion)
        return l1q, l2q, w1, w2, l1busy, l2busy, l1q+l2q, w1+w2

    cutoff_rows = []
    cohorts = []
    priority = []
    for cutoff_name, cutoff in (("H", h), ("HD", h+drain)):
        m = metric(admitted, cutoff)
        state = sim.at_horizon if cutoff_name == "H" else sim.after_drain
        row = {"profile": profile["profile"], **condition, **profile, "seed": seed,
               "policy": policy, "cutoff": cutoff_name, "cutoff_h": cutoff,
               "trace_sha256": trace_hash, **m,
               "queue_l1": state.l1_backlog, "queue_l2": state.l2_backlog,
               "work_l1_h_est": assigned_metrics(cutoff)[2],
               "work_l2_h_est": assigned_metrics(cutoff)[3],
               "quality_RN_numerator": m["RN"]*m["admitted"]}
        cutoff_rows.append(row)
    start = profile["pulse_start_h"]
    pulse_end = start + profile["duration_h"]
    for cohort, lo, hi in (("pre", 0.0, start), ("pulse", start, pulse_end),
                           ("recovery", pulse_end, h)):
        group = [x for x in admitted if lo <= x.routed.alert.arrival < hi]
        cohorts.append({"profile": profile["profile"], **condition, "seed": seed,
                        "policy": policy, "cohort": cohort, "start_h": lo, "end_h": hi,
                        **metric(group, h+drain)})
    for severity in ("high", "medium", "low"):
        group = [x for x in admitted if x.severity == severity]
        priority.append({"profile": profile["profile"], **condition, "seed": seed,
                         "policy": policy, "priority": severity,
                         **metric(group, h+drain)})

    horizon = h + drain
    series = []
    for step in range(int(math.ceil(horizon))+1):
        t = min(float(step), horizon)
        q1, q2, w1, w2, busy1, busy2, _, _ = assigned_metrics(t)
        rho = profile["rho_normal"] if t < start or t >= pulse_end else profile["rho_high"]
        state = {"profile": profile["profile"], **condition, "seed": seed,
                 "policy": policy, "time_h": t, "rho": rho,
                 "queue_l1": q1, "queue_l2": q2, "work_l1_h_est": w1,
                 "work_l2_h_est": w2, "occupied_l1": busy1, "occupied_l2": busy2,
                 "pending_l1_past_deadline": 0, "pending_l2_past_deadline": 0}
        # Pending work whose alert deadline has passed cannot meet terminal SLA.
        for x in admitted:
            aid=x.routed.alert.alert_id
            if x.routed.alert.deadline > t:
                continue
            first=l1jobs.get(aid)
            if first is None or first.completion > t:
                state["pending_l1_past_deadline"] += 1
            elif routes[aid]:
                second=l2jobs.get(aid)
                if second is None or second.completion > t:
                    state["pending_l2_past_deadline"] += 1
        series.append(state)
    modes=[]
    for pool, stage in (("L1",sim.l1_simulation),("L2",sim.l2_simulation)):
        for item in stage.hlsa_history:
            modes.append({"profile":profile["profile"],**condition,"seed":seed,
                          "policy":policy,"pool":pool,"time_h":item.time,
                          "mode":item.mode,"switched":item.switched,
                          "pressure":item.pressure,"pending":item.pending,
                          "occupied":item.occupied})
    return cutoff_rows, series, cohorts, priority, modes


def run_batch(phase: str, seed_start: int, seed_count: int,
              selected_profiles: set[str] | None = None) -> None:
    out = OUT / phase
    out.mkdir(parents=True, exist_ok=True)
    episode_rows=[];series_rows=[];cohort_rows=[];priority_rows=[];mode_rows=[];manifest=[]
    base_profiles=scenarios()
    if phase.startswith("main"):
        cases=[(p, "reference", None, None) for p in base_profiles
               if selected_profiles is None or p["profile"] in selected_profiles]
        rosters={"reference":(BASE_L1,BASE_L2,BASE_S1,BASE_S2,
                                BASE_MU_L1,BASE_MU_L2_TASK)}
    elif phase=="sla_staff":
        cases=[]
        profiles={p["profile"]:p for p in base_profiles}
        for profile_name in C["sla_map_profiles"]:
            for sla in C["sla_profiles"]:
                cases.append((profiles[profile_name], sla["name"], sla, None))
        for profile_name in C["staffing_profiles"]:
            for team in C["staffing_teams"]:
                cases.append((profiles[profile_name], team["name"], None, team))
        rosters={}
        for team in C["staffing_teams"]:
            l1,l2,s1,s2=build_roster(team["n_l1"],team["n_l2"],2.5)
            m1=effective_capacity(l1,s1,PROJECT_MIX)["max_common_arrivals_per_h"]
            m2=effective_capacity(l2,s2,ROUTED_MIX)["max_common_arrivals_per_h"]
            rosters[team["name"]]=(l1,l2,s1,s2,m1,m2)
        rosters["reference"]=(BASE_L1,BASE_L2,BASE_S1,BASE_S2,BASE_MU_L1,BASE_MU_L2_TASK)
    else:
        raise ValueError(f"unsupported phase: {phase}")

    for profile, condition_name, sla, team in cases:
        condition={"condition_kind":"sla" if sla else ("staff" if team else "reference"),
                   "condition":condition_name}
        deadlines=deadline_map(sla)
        team_name=team["name"] if team else "reference"
        l1,l2,s1,s2,mu1,mu2=rosters[team_name]
        if sla:
            condition.update({"T0_h":sla["T0"],"f_high":sla["f_high"],"f_low":sla["f_low"],
                              "Tpulse_over_Tcrit":profile["duration_h"]/sla["T0"]})
        if team:
            rate_scale=BASE_MU_L1
            condition.update({"n_l1":len(l1),"n_l2":len(l2),"mu_l1_common_alerts_per_h":mu1,
                              "mu_l2_tasks_per_h":mu2,
                              "rho_normal_l1":rate_scale*profile["rho_normal"]/mu1,
                              "rho_high_l1":rate_scale*profile["rho_high"]/mu1,
                              "rho_normal_l2":rate_scale*profile["rho_normal"]*ROUTED_SHARE/mu2,
                              "rho_high_l2":rate_scale*profile["rho_high"]*ROUTED_SHARE/mu2,
                              "demand_absolute_base_team":"fixed"})
        for seed in range(seed_start,seed_start+seed_count):
            trace=make_trace(profile,seed,BASE_MU_L1,deadlines)
            adm=[x for x in trace if x.routed.alert.arrival < profile["admission_h"]]
            digest=trace_digest(adm)
            scenario_digest=trace_digest(adm,include_deadline=True)
            manifest.append({"profile":profile["profile"],**condition,"seed":seed,
                             "trace_sha256":digest,"scenario_sha256":scenario_digest,"admitted":len(adm),
                             "deadline_map":deadlines,"arrival_mu_base":BASE_MU_L1,
                             "admission_h":profile["admission_h"]})
            for policy in POLICIES:
                outputs=run_one(profile,seed,policy,trace,l1,l2,s1,s2,mu1,mu2,digest,condition)
                episode_rows.extend(outputs[0]);series_rows.extend(outputs[1]);
                cohort_rows.extend(outputs[2]);priority_rows.extend(outputs[3]);mode_rows.extend(outputs[4])
            print(phase,profile["profile"],condition_name,seed,"complete",flush=True)
    for filename, rows in (("episodes.csv",episode_rows),("timeseries.csv",series_rows),
                           ("cohorts.csv",cohort_rows),("priority.csv",priority_rows),
                           ("modes.csv",mode_rows)):
        if rows: write_csv(out/filename,rows)
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    metadata={"config":C,"phase":phase,"seed_start":seed_start,"seed_count":seed_count,
              "base_mu_l1":BASE_MU_L1,"base_mu_l2_tasks_per_h":BASE_MU_L2_TASK,
              "expected_l2_routing_fraction":ROUTED_SHARE,
              "base_mu_l2_equivalent_common_alerts_per_h":BASE_MU_L2_TASK/ROUTED_SHARE,
              "episodes_rows":len(episode_rows),"timeseries_rows":len(series_rows),
              "trace_matching":"all policies share identical synthetic alert object and trace hash per profile/seed/condition",
              "engine_or_policy_changes":False}
    (out/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print("saved",phase,len(episode_rows),"episode-cutoff rows",flush=True)


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--phase",choices=("main_initial","main_initial_v2","main_extension","sla_staff"),required=True)
    parser.add_argument("--seed-start",type=int)
    parser.add_argument("--seed-count",type=int)
    parser.add_argument("--profiles",help="comma-separated main profile ids; defaults to all")
    args=parser.parse_args()
    if args.phase in ("main_initial","main_initial_v2"):
        start=args.seed_start if args.seed_start is not None else C["seed_base_initial"]
        count=args.seed_count if args.seed_count is not None else C["seed_count_initial"]
    elif args.phase=="main_extension":
        start=args.seed_start if args.seed_start is not None else C["seed_base_extension"]
        count=args.seed_count if args.seed_count is not None else C["seed_count_extension"]
    else:
        start=args.seed_start if args.seed_start is not None else C["seed_base_initial"]
        count=args.seed_count if args.seed_count is not None else C["seed_count_initial"]
    selected=set(args.profiles.split(",")) if args.profiles else None
    run_batch(args.phase,start,count,selected)


if __name__=="__main__":
    main()
