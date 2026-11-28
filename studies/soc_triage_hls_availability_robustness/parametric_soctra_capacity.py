"""Algebraic/LP parameter study for SOCTRA-HLS demand and staffing.

No trace generation, dispatch, queue simulation, campaign or policy comparison
is performed. Outputs are analytical expectations under explicitly synthetic
assumptions and the existing eligibility-constrained fluid capacity LP.

Run from the repository root:
  python studies/soc_triage_hls_availability_robustness/parametric_soctra_capacity.py
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Mapping

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from hls.rq1_allocation import Analyst  # noqa: E402
from studies.soc_triage_hls_availability_robustness.execution_api import (  # noqa: E402
    AnalystResource, OrganizationConfig, TeamConfig,
)
from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import (  # noqa: E402
    CapacityDemandProfile, DemandRegime, assess_capacity,
)
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario  # noqa: E402

CONFIG = ROOT / "studies/soc_triage_hls_availability_robustness/config/SOC_NEW_MODEL_CONOPS_REFERENCE_SOCTRA_SEVERITY_V1.json"
P_VALUES = (570 / 156981, .01, .02, .05, .10)
FPR_VALUES = (.01, .045, .10)
BETA_VALUES = (0.0, 1.0, 2.0, 3.0)
ROSTERS = ((5, 3), (10, 3), (12, 4), (20, 5), (20, 2), (28, 1))
INTENSITY_MULTIPLIERS = (.5, 1.0, 1.5, 2.0, 2.5)
RAW_RECORDS_PER_H = 9.019
PROCESSED_RECORDS_PER_H = 6.593
HOURLY_CV = .82
SEVERITY_MIX = {"critical": 21937 / 156981, "high": 87545 / 156981,
                "medium": 47499 / 156981}
DEADLINES_H = {"critical": 1.0, "high": 4.0, "medium": 12.0}


def beta22_cdf(q: float) -> float:
    q = min(1.0, max(0.0, float(q)))
    return 3 * q * q - 2 * q * q * q


def beta22_survival(q: float) -> float:
    return (1 - q) ** 2 * (1 + 2 * q)


def q0_for_prevalence(prevalence: float) -> float:
    if not 0 < prevalence < 1:
        raise ValueError("prevalence must be in (0,1)")
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if beta22_survival(mid) > prevalence:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


@dataclass(frozen=True)
class NeedDistribution:
    prevalence: float
    q0: float
    mean_q_need: float
    mean_q_ordinary: float


def need_distribution(prevalence: float) -> NeedDistribution:
    q0 = q0_for_prevalence(prevalence)
    # Integral_0^1 q*6q(1-q)dq = 1/2.
    upper_first_moment = .5 - 2 * q0**3 + 1.5 * q0**4
    mean_need = upper_first_moment / prevalence
    mean_ordinary = (.5 - prevalence * mean_need) / (1 - prevalence)
    return NeedDistribution(prevalence, q0, mean_need, mean_ordinary)


def confusion(prevalence: float, sensitivity: float, fpr: float) -> dict[str, float]:
    if not 0 <= sensitivity <= 1 or not 0 <= fpr <= 1:
        raise ValueError("sensitivity and FPR must be in [0,1]")
    return {
        "TP": prevalence * sensitivity,
        "FN": prevalence * (1 - sensitivity),
        "FP": (1 - prevalence) * fpr,
        "TN": (1 - prevalence) * (1 - fpr),
    }


def route_summary(prevalence: float, sensitivity: float, fpr: float,
                  beta: float = 1.0) -> dict[str, float]:
    dist = need_distribution(prevalence)
    counts = confusion(prevalence, sensitivity, fpr)
    l1 = counts["TN"] + counts["FN"]
    l2 = counts["TP"] + counts["FP"]
    ew_need = 1 + beta * (dist.mean_q_need - .5)
    ew_ordinary = 1 + beta * (dist.mean_q_ordinary - .5)
    return {
        **counts, "q0": dist.q0,
        "l1_fraction": l1, "l2_fraction": l2,
        "l1_complex_fraction": counts["FN"] / l1 if l1 else 0.0,
        "l2_complex_fraction": counts["TP"] / l2 if l2 else 0.0,
        "mean_q_l1": (counts["TN"] * dist.mean_q_ordinary +
                      counts["FN"] * dist.mean_q_need) / l1 if l1 else 0.0,
        "mean_q_l2": (counts["FP"] * dist.mean_q_ordinary +
                      counts["TP"] * dist.mean_q_need) / l2 if l2 else 0.0,
        "work_ordinary": ew_ordinary, "work_complex": ew_need,
        "complex_ordinary_ratio": ew_need / ew_ordinary if ew_ordinary else np.inf,
    }


def expand_organization(base: OrganizationConfig, n_l1: int, n_l2: int) -> OrganizationConfig:
    """Cycle existing role profiles; do not invent competence or speed values."""
    if n_l1 < 1 or n_l2 < 1:
        raise ValueError("both levels require at least one analyst")
    out = []
    team_ids = {}
    for level, n in (("L1", n_l1), ("L2", n_l2)):
        templates = base.resources_for(level)
        ids = []
        for index in range(n):
            template = templates[index % len(templates)]
            cycle = index // len(templates) + 1
            aid = template.analyst.analyst_id if cycle == 1 else f"{template.analyst.analyst_id}-rep{cycle:02d}"
            analyst = Analyst(aid, template.analyst.eligible_classes,
                              dict(template.analyst.competence))
            resource = AnalystResource(
                analyst, dict(template.service_by_class), template.calendar,
                dict(template.forecast_service_by_class),
            )
            out.append(resource)
            ids.append(aid)
        team_ids[level] = tuple(ids)
    return OrganizationConfig(tuple(out), tuple(
        TeamConfig(level, team_ids[level]) for level in ("L1", "L2")
    ))


def scale_services(organization: OrganizationConfig, factor: float) -> OrganizationConfig:
    if factor <= 0:
        raise ValueError("service scale must be positive")
    resources = tuple(AnalystResource(
        r.analyst,
        {k: factor * v for k, v in r.service_by_class.items()},
        r.calendar,
        {k: factor * v for k, v in r.forecast_service_by_class.items()},
    ) for r in organization.analysts)
    return OrganizationConfig(resources, organization.teams)


def equalize_speeds_within_eligibility(organization: OrganizationConfig) -> OrganizationConfig:
    """Capacity control: keep eligibility and class means, remove within-class speed spread."""
    out = []
    for level in ("L1", "L2"):
        resources = organization.resources_for(level)
        classes = set().union(*(set(r.analyst.eligible_classes) for r in resources))
        averages = {k: float(np.mean([r.service_by_class[k] for r in resources
                                      if k in r.analyst.eligible_classes])) for k in classes}
        for r in resources:
            times = {k: averages[k] for k in r.analyst.eligible_classes}
            out.append(AnalystResource(r.analyst, times, r.calendar, times))
    return OrganizationConfig(tuple(out), organization.teams)


def _capacity_profile(class_mix: Mapping[str, float], prevalence: float,
                      sensitivity: float, fpr: float, beta: float,
                      mean_q_need: float, mean_q_ordinary: float) -> CapacityDemandProfile:
    classes = tuple(class_mix)
    pmap = {k: prevalence for k in classes}
    return CapacityDemandProfile(
        regimes=(DemandRegime("unit_arrival_rate", 0, 1,
                              {k: float(class_mix[k]) for k in classes}),),
        prevalence_by_class=pmap,
        sensitivity_by_class={k: sensitivity for k in classes},
        false_positive_rate_by_class={k: fpr for k in classes},
        alpha=1.0, beta=beta,
        difficulty_mean_by_class_and_need={k: (mean_q_need, mean_q_ordinary) for k in classes},
        gamma=1.0, flow_mode="triage_single_investigation",
    )


def capacity_result(organization: OrganizationConfig, class_mix: Mapping[str, float],
                    prevalence: float, sensitivity: float, fpr: float, beta: float,
                    service_scale: float = 1.0) -> dict:
    dist = need_distribution(prevalence)
    org = scale_services(organization, service_scale) if service_scale != 1 else organization
    profile = _capacity_profile(class_mix, prevalence, sensitivity, fpr, beta,
                                dist.mean_q_need, dist.mean_q_ordinary)
    report = assess_capacity(org, profile).regimes
    summary = route_summary(prevalence, sensitivity, fpr, beta)
    by_level = {}
    for row in report:
        n = len(org.resources_for(row.level))
        team_hours = n  # continuous individual availability, one analyst-hour per hour
        utilization = row.offered_l1_work_h_per_h / n if row.level == "L1" else row.offered_l2_work_h_per_h / n
        lp_util = [u * row.relative_load for _, u in row.analyst_utilization_at_capacity]
        route_fraction = summary["l1_fraction"] if row.level == "L1" else summary["l2_fraction"]
        total_rate_capacity = row.capacity_per_h / route_fraction if route_fraction else np.inf
        by_level[row.level] = {
            "route_capacity_per_h": row.capacity_per_h,
            "total_arrival_capacity_per_h": total_rate_capacity,
            "relative_load_at_lambda_1": row.relative_load,
            "offered_work_per_h_at_lambda_1": row.offered_l1_work_h_per_h if row.level == "L1" else row.offered_l2_work_h_per_h,
            "team_size": n, "mean_utilization_per_fte_at_lambda_1": utilization,
            "lp_util_min_at_lambda_1": min(lp_util) if lp_util else 0.0,
            "lp_util_max_at_lambda_1": max(lp_util) if lp_util else 0.0,
            "capacity_work_h_per_h": sum(u for _, u in row.analyst_utilization_at_capacity),
            "unstaffed_classes": row.unstaffed_classes,
        }
    return {**summary, "levels": by_level,
            "total_stable_arrival_capacity_per_h": min(
                by_level["L1"]["total_arrival_capacity_per_h"],
                by_level["L2"]["total_arrival_capacity_per_h"]),
            "service_scale": service_scale, "beta": beta, "fpr": fpr}


def utilization_window(result: Mapping, n_l1: int, n_l2: int,
                       *, l1_band=(.25, .80), l2_band=(.10, .60)) -> tuple[float, float] | None:
    """Lambda interval meeting declared exploratory utilization bands and LP stability."""
    l1w = result["levels"]["L1"]["offered_work_per_h_at_lambda_1"]
    l2w = result["levels"]["L2"]["offered_work_per_h_at_lambda_1"]
    lower = max(l1_band[0] * n_l1 / l1w, l2_band[0] * n_l2 / l2w)
    upper = min(l1_band[1] * n_l1 / l1w, l2_band[1] * n_l2 / l2w,
                result["total_stable_arrival_capacity_per_h"])
    return (lower, upper) if lower <= upper else None


def _service_infeasible_probability(base_h: float, beta: float, deadline_h: float,
                                    q0: float, complex_need: bool) -> float:
    if beta == 0:
        return float(base_h > deadline_h)
    cutoff = .5 + (deadline_h / base_h - 1) / beta
    if complex_need:
        lower, upper = q0, 1.0
    else:
        lower, upper = 0.0, q0
    mass = beta22_cdf(upper) - beta22_cdf(lower)
    if mass <= 0:
        return 0.0
    remaining = beta22_cdf(upper) - beta22_cdf(max(lower, min(upper, cutoff)))
    return float(max(0.0, min(1.0, remaining / mass)))


def sla_feasibility(organization: OrganizationConfig, class_mix: Mapping[str, float],
                    prevalence: float, sensitivity: float, fpr: float, beta: float,
                    service_scale: float = 1.0) -> list[dict]:
    """Zero-queue infeasibility: uniform eligible-profile and fastest-profile bounds."""
    dist = need_distribution(prevalence)
    probs = confusion(prevalence, sensitivity, fpr)
    rows = []
    for level, groups, routeprob in (
        ("L1", (("TN", False), ("FN", True)), probs["TN"] + probs["FN"]),
        ("L2", (("FP", False), ("TP", True)), probs["FP"] + probs["TP"]),
    ):
        resources = organization.resources_for(level)
        for severity, deadline in DEADLINES_H.items():
            den = routeprob
            uniform_bad = best_bad = weighted_mean_service = 0.0
            if den <= 0:
                rows.append({"level":level,"severity":severity,"deadline_h":deadline,
                             "mean_service_h":None,"mean_margin_h":None,
                             "uniform_eligible_infeasible":None,"fastest_eligible_infeasible":None})
                continue
            for task_class, mix in class_mix.items():
                eligible = [r for r in resources if task_class in r.analyst.eligible_classes]
                if not eligible and mix > 0:
                    raise ValueError(f"{level} has no eligible analyst for {task_class}")
                times = [r.service_by_class[task_class] * service_scale for r in eligible]
                for label, is_complex in groups:
                    mass = probs[label] * float(mix) / den
                    if mass == 0:
                        continue
                    means_q = dist.mean_q_need if is_complex else dist.mean_q_ordinary
                    mean_factor = 1 + beta * (means_q - .5)
                    mean_base = float(np.mean(times))
                    weighted_mean_service += mass * mean_base * mean_factor
                    uniform_bad += mass * np.mean([
                        _service_infeasible_probability(t, beta, deadline, dist.q0, is_complex)
                        for t in times
                    ])
                    best_bad += mass * _service_infeasible_probability(
                        min(times), beta, deadline, dist.q0, is_complex)
            rows.append({"level":level,"severity":severity,"deadline_h":deadline,
                         "mean_service_h":weighted_mean_service,
                         "mean_margin_h":deadline-weighted_mean_service,
                         "uniform_eligible_infeasible":uniform_bad,
                         "fastest_eligible_infeasible":best_bad})
    return rows


def _fmt(x: float | None, digits: int = 3) -> str:
    return "—" if x is None or not np.isfinite(float(x)) else f"{100*x:.{digits}f}%"


def run_study() -> str:
    scenario = load_scenario(CONFIG)
    demand = scenario.demand_profile
    class_mix = demand["class_mix"]
    sensitivity = float(next(iter(demand["sensitivity_by_class"].values())))
    base_fpr = float(next(iter(demand["false_positive_rate_by_class"].values())))
    base_org = scenario.organization
    records = ["# Parametric SOCTRA-HLS staffing and capacity study", "",
               "Algebra + eligibility-constrained fluid LP only. No trace generation, queue simulation, campaign, policy comparison or optimization.", "",
               f"Empirical anchors: September processed N=156,981; standardized escalation label=570/156,981={570/156981:.6%} (proxy only; it does not establish true need for L2); source record intensity={RAW_RECORDS_PER_H:.3f}/h; processed rate={PROCESSED_RECORDS_PER_H:.3f}/h; observed hourly CV={HOURLY_CV:.2f}. Project/severity/label variation is established in SOC_ORGANIZATIONAL_MODEL.md §19 and is not modeled as a joint process in this first sensitivity grid.", "",
               "Synthetic fixed inputs: Beta(2,2) q, class mix 50/30/20 (not an empirical project mapping), sensitivity 0.8421, baseline FPR 0.045, severity independent of q and classifier errors, continuous availability, one direct investigation, alpha=gamma=1. The scenario classifier rates and service profiles are reused, not recalibrated. κ=1 record→task is only a scale assumption; every arrival and offered-work value scales linearly with κ.", "",
               "## 1. Prevalence and classifier routing", "",
               "TP/FN/FP/TN are fractions of incoming alert records. L2 route fraction is TP+FP, not p. q0 solves P(q≥q0)=p for Beta(2,2).", "",
               "| Need prevalence p | q0 | TP | FN | FP | TN | L1 route | L2 route | Complex share L1 | Complex share L2 | E[q|L1] | E[q|L2] | β=1 E[W] complex/ordinary |", "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for p in P_VALUES:
        r=route_summary(p,sensitivity,base_fpr,1)
        records.append("| " + " | ".join([
            f"{p:.4%}",f"{r['q0']:.6f}",*[f"{r[k]:.4%}" for k in ("TP","FN","FP","TN","l1_fraction","l2_fraction","l1_complex_fraction","l2_complex_fraction")],
            f"{r['mean_q_l1']:.4f}",f"{r['mean_q_l2']:.4f}",f"{r['work_complex']:.3f}/{r['work_ordinary']:.3f}",
        ]) + " |")
    records += ["", "Expected work contribution per incoming record at β=1 (W normalized to mean 1 at q=0.5); separates ordinary and complex work by assigned level:", "",
                "| Need p | L1 ordinary TN | L1 complex FN | L2 ordinary FP | L2 complex TP | Total expected work |", "|---:|---:|---:|---:|---:|---:|"]
    for p in P_VALUES:
        r=route_summary(p,sensitivity,base_fpr,1)
        parts=(r["TN"]*r["work_ordinary"],r["FN"]*r["work_complex"],
               r["FP"]*r["work_ordinary"],r["TP"]*r["work_complex"])
        records.append("| " + " | ".join([f"{p:.4%}",*[f"{x:.5f}" for x in parts],f"{sum(parts):.5f}"]) + " |")
    records += ["", "FPR sensitivity changes total L2 routing substantially; higher FPR is not evidence-supported here:", "",
                "| p | FPR | TP | FP | L2 routes | FP share of L2 |", "|---:|---:|---:|---:|---:|---:|"]
    for p in (P_VALUES[0], .01, .05, .10):
        for fpr in FPR_VALUES:
            c=confusion(p,sensitivity,fpr); route=c["TP"]+c["FP"]
            records.append(f"| {p:.4%} | {fpr:.1%} | {c['TP']:.3%} | {c['FP']:.3%} | {route:.3%} | {c['FP']/route:.1%} |")

    records += ["", "## 2. Work ratio and zero-queue SLA viability", "",
                "q controls effort once through W(q)=1+β(q−0.5); γ=α=1 add no redundant scale. β=1 is the current model; β=0 removes complexity effect; β=2/3 are explicit sensitivity hypotheses. Mean service is averaged over eligible analyst-class cells; zero-queue infeasibility is also estimated under uniform eligible-analyst assignment and bounded by assigning the fastest eligible profile. Neither is a D1/P1 dispatch prediction.", "",
                "| p | β | E[W complex] / E[W ordinary] |", "|---:|---:|---:|"]
    for p in (P_VALUES[0], .01, .05, .10):
        for beta in BETA_VALUES:
            r=route_summary(p,sensitivity,base_fpr,beta)
            records.append(f"| {p:.4%} | {beta:.1f} | {r['complex_ordinary_ratio']:.3f}× |")
    records += ["", "At the empirical p and β=1, per-investigation expected mean work-times by confusion route (with the current synthetic profiles) and deadline feasibility:", "",
            "| Level / confusion | Mean active service h |",
                "|---|---:|"]
    # The route-specific mean service is generated below from the same class mix.
    dist=need_distribution(P_VALUES[0]); base_times={}
    for level in ("L1","L2"):
        res=base_org.resources_for(level)
        for task_class in class_mix:
            base_times[level,task_class]=float(np.mean([r.service_by_class[task_class] for r in res if task_class in r.analyst.eligible_classes]))
    r=route_summary(P_VALUES[0],sensitivity,base_fpr,1)
    for name,level,prob,is_complex in (("TN","L1",r["TN"],False),("FN","L1",r["FN"],True),("FP","L2",r["FP"],False),("TP","L2",r["TP"],True)):
        meanbase=sum(float(class_mix[k])*base_times[level,k] for k in class_mix)
        qmean=dist.mean_q_need if is_complex else dist.mean_q_ordinary
        records.append(f"| {level} {name} | {meanbase*(1+qmean-.5):.3f} |")
    records += ["", "| Severity/deadline | Level | Mean service h | Mean margin h | Infeasible, uniform eligible | Infeasible, fastest eligible bound |", "|---|---|---:|---:|---:|---:|"]
    for row in sla_feasibility(base_org,class_mix,P_VALUES[0],sensitivity,base_fpr,1):
        records.append(f"| {row['severity'].upper()} / {row['deadline_h']:g} h | {row['level']} | {row['mean_service_h']:.3f} | {row['mean_margin_h']:.3f} | {_fmt(row['uniform_eligible_infeasible'])} | {_fmt(row['fastest_eligible_infeasible'])} |")
    records += ["", "SLA infeasibility depends on service time against the deadline before waiting. Waiting, queueing and total resolution are not conflated. Severe deadlines are synthetic resolution deadlines. Because severity is modeled independent of q/project, the same service distribution is paired with each empirical severity deadline and prevalence weight.", ""]

    records += ["## 3. Profiles, heterogeneity and assignable capacity", "",
                "Roster expansion cycles existing profiles in their original order (e.g. L1-01…L1-05, then a second explicitly labeled copy cycle); each copy preserves eligibility, competence and every project-specific service/forecast value exactly. This creates no new empirical workers. L2 likewise cycles the existing all-project L2 profiles. All analyst IDs remain unique. The LP respects individual eligibility and service differences. A separate speed-equalized control preserves project eligibility and per-class mean L1/L2 service while removing within-class speed spread; competence is unchanged and does not enter service/capacity.", "",
                "| Template | L1/L2 | β | p | Offered work L1 h-person/h | Offered work L2 h-person/h | Util L1 | Util L2 | LP relative load L1 | LP relative load L2 | Stable total arrivals/h max |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    results={}
    selected_p=(P_VALUES[0],.01,.02,.05,.10)
    for n1,n2 in ROSTERS:
        org=expand_organization(base_org,n1,n2)
        for p in selected_p:
            result=capacity_result(org,class_mix,p,sensitivity,base_fpr,1)
            results[n1,n2,p,1]=result
            l1,l2=result["levels"]["L1"],result["levels"]["L2"]
            records.append(f"| {n1}/{n2} | {n1}/{n2} | 1 | {p:.4%} | {l1['offered_work_per_h_at_lambda_1']*RAW_RECORDS_PER_H:.3f} | {l2['offered_work_per_h_at_lambda_1']*RAW_RECORDS_PER_H:.3f} | {RAW_RECORDS_PER_H*l1['mean_utilization_per_fte_at_lambda_1']:.1%} | {RAW_RECORDS_PER_H*l2['mean_utilization_per_fte_at_lambda_1']:.1%} | {RAW_RECORDS_PER_H*l1['relative_load_at_lambda_1']:.3f} | {RAW_RECORDS_PER_H*l2['relative_load_at_lambda_1']:.3f} | {result['total_stable_arrival_capacity_per_h']:.2f} |")
    records += ["", "Selected stable intensity windows under a declared screening band: L1 mean utilization 25–80%, L2 10–60%, and both LP loads <1. This is a candidate-generation criterion, not an empirically validated definition of reasonable utilization.", "",
                "| Template | p | β | Feasible arrival intensity λ (record-equivalent/h) | Multiple of source mean 9.019/h |", "|---|---:|---:|---:|---:|"]
    for n1,n2 in ROSTERS:
        for p in (.01,.02,.05,.10):
            result=results[n1,n2,p,1]
            interval=utilization_window(result,n1,n2)
            if interval:
                records.append(f"| {n1}/{n2} | {p:.1%} | 1 | {interval[0]:.2f}–{interval[1]:.2f} | {interval[0]/RAW_RECORDS_PER_H:.2f}–{interval[1]/RAW_RECORDS_PER_H:.2f}× |")
            else:
                records.append(f"| {n1}/{n2} | {p:.1%} | 1 | No overlap | — |")

    records += ["", "### Fixed-organization load regimes and speed sensitivity", "",
                "The same organization is held fixed across each multiplier. Per-level load and mean utilization scale linearly with arrivals; LP relative load above 1 indicates that level cannot sustain the rate. The transient pulse is shown as offered-work pressure only; fluid recovery is backlog work divided by spare capacity after returning to baseline.", "",
                "| Template | p | Regime | λ records-equivalent/h | L1 mean util | L2 mean util | LP load L1/L2 |", "|---|---:|---|---:|---:|---:|---:|"]
    for n1,n2,p in ((5,3,.10),(10,3,.10),(12,4,.05),(20,2,.05)):
        base_result=results[n1,n2,p,1]
        for label,mult in (("reduced",.5),("normal",1.0),("elevated",1.5),("temporary pulse",2.5)):
            l1,l2=base_result["levels"]["L1"],base_result["levels"]["L2"]
            records.append(f"| {n1}/{n2} | {p:.0%} | {label} | {RAW_RECORDS_PER_H*mult:.2f} | {l1['mean_utilization_per_fte_at_lambda_1']*RAW_RECORDS_PER_H*mult:.1%} | {l2['mean_utilization_per_fte_at_lambda_1']*RAW_RECORDS_PER_H*mult:.1%} | {l1['relative_load_at_lambda_1']*RAW_RECORDS_PER_H*mult:.2f}/{l2['relative_load_at_lambda_1']*RAW_RECORDS_PER_H*mult:.2f} |")
    records += ["", "For a 2.5× pulse lasting 6 h followed by 1× baseline, the next table reports fluid stage-arrival backlog and ideal recovery. Backlog is zero if the pulse does not exceed that level's LP capacity; recovery is backlog divided by baseline spare stage capacity. This assumes unchanged class mix and continuous capacity, and is not a queue simulation.", "",
                "| Template | p | Level | Pulse ρ | Backlog, stage-task equivalents | Recovery h |", "|---|---:|---|---:|---:|---:|"]
    for n1,n2,p in ((5,3,.10),(10,3,.10),(12,4,.05),(20,2,.05)):
        r=results[n1,n2,p,1]
        for level,sharekey in (("L1","l1_fraction"),("L2","l2_fraction")):
            row=r["levels"][level]
            baseline=RAW_RECORDS_PER_H*r[sharekey]
            pulse=2.5*baseline
            cap=row["route_capacity_per_h"]
            backlog=max(0.0,(pulse-cap)*6)
            recovery=backlog/(cap-baseline) if backlog and cap>baseline else (0.0 if not backlog else np.inf)
            recovery_text = f"{recovery:.2f}" if np.isfinite(recovery) else "unbounded"
            records.append(f"| {n1}/{n2} | {p:.0%} | {level} | {pulse/cap:.2f} | {backlog:.2f} | {recovery_text} |")
    records += ["", "| Template | p | Heterogeneous LP capacity arrivals/h | Equal-speed control arrivals/h | Change |", "|---|---:|---:|---:|---:|"]
    for n1,n2,p in ((10,3,.10),(12,4,.05),(20,2,.05)):
        org=expand_organization(base_org,n1,n2)
        actual=results[n1,n2,p,1]["total_stable_arrival_capacity_per_h"]
        equalized=capacity_result(equalize_speeds_within_eligibility(org),class_mix,p,sensitivity,base_fpr,1)["total_stable_arrival_capacity_per_h"]
        records.append(f"| {n1}/{n2} | {p:.0%} | {actual:.2f} | {equalized:.2f} | {(equalized/actual-1):+.1%} |")

    records += ["", "### One-factor sensitivities", "",
                "| Factor | Levels examined | Main direction under this model |", "|---|---|---|"]
    records += [
        "| Need prevalence p | 0.363%, 1%, 2%, 5%, 10% | Raises TP and complex-q arrivals; lowers q0; changes the L2 share beyond p only through classifier operating point. |",
        "| FPR | 1%, 4.5%, 10% | Raises ordinary FP work in L2 and reduces L1 routing; can make L2 more active without changing p. |",
        "| Complexity slope β | 0, 1, 2, 3 | Changes ordinary and complex work factors once through W(q); larger β raises complex work and tail SLA risk. |",
        "| L1/L2 ratio | 5/3, 10/3, 12/4, 20/5, 20/2, 28/1 | Changes per-person pressure; repeated profile cycles preserve heterogeneity but are replicas, not new observations. |",
        "| Arrival intensity | 0.5×–2.5× 9.019 records/h; κ sensitivity | Offered work and LP rho scale linearly with λ and κ; observed hourly CV=0.82 and peak 161 records/h motivate transient stress tests, not an hourly task-rate calibration. |",
        "| Speed heterogeneity | observed synthetic profile vs within-class equal-speed control | Alters assignable LP capacity via eligibility and service edges; competence differences affect modeled quality only, not the capacity LP. |",
        "",
        "The spread between LP offered load and theoretical capacity identifies where L1, L2 or both are overloaded. A transient pulse accumulates work only when its offered work rate exceeds level capacity; on return to a stable baseline, ideal fluid recovery time is backlog work divided by baseline spare capacity. No queue or event simulation is run here.", "",
        "## 4. Identification and candidate interpretation", "",
        "Empirical: September record count/rate, processed severity mix, standardized escalation prevalence, and observed temporal/project/severity-label variation (see §19.1–19.2). Hypothesis: each record becomes one task (κ), p is interpreted as need, classifier errors remain constant across project/severity, q~Beta(2,2), service ratios, synthetic roster/profile replication, continuous availability and SLA resolution deadlines. The February test prevalence 19/14,449 is an alternative reference point, not interchangeable with September global p.", "",
        "Candidate regions to carry forward only to a later, separately authorized simulation: (i) p=2–5%, FPR=4.5%, β=1–2 with 12/4 or 20/5; (ii) p=5–10%, FPR=1–4.5%, β=1 with 10/3 or 12/4; (iii) p=1–2%, FPR near 10% only as explicit classifier-error sensitivity, not an assumed operating point. Candidate arrival intervals are listed in the table above; use κ and the source/project/time mix as sensitivity dimensions. These are feasible regions under the fluid screening band, not optimal organizations or empirically plausible deployments. Reject candidates with no overlapping interval or with excessive LP load.", "",
        "This analysis does not establish operationally plausible staffing or service durations, since SOCTRA has no per-investigation start/end events, analyst assignment-stage logs, verified task conversion, or individual skill/velocity measurements. It also does not assess queue waiting distributions, D1/P1/HLS-B performance, operational shift coverage, or model the observed joint project-severity-escalation distribution. Those limits must be resolved or explicitly bounded before campaigns.", "",
        "Reproduce the deterministic analysis with:", "",
        "```sh",
        "python studies/soc_triage_hls_availability_robustness/parametric_soctra_capacity.py",
        "```", "",
    ]
    return "\n".join(records)


def main() -> None:
    print(run_study())


if __name__ == "__main__":
    main()
