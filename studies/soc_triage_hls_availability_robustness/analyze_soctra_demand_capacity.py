"""Aggregate SOCTRA demand characterization and analytic CONOPS capacity checks.

This is a read-only analysis: it reads the source CSV and the existing canonical
Parquets, anonymizes project labels before rendering, and never executes a
campaign or writes record-level data. Example:

python studies/soc_triage_hls_availability_robustness/analyze_soctra_demand_capacity.py \
  --raw-september /path/to/dataset_20250919.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import (  # noqa: E402
    CapacityDemandProfile, DemandRegime, assess_capacity,
)
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario  # noqa: E402

DEFAULT_PROCESSED = ROOT / "data/soctra/processed/soctra_preprocessed.parquet"
DEFAULT_FEBRUARY = ROOT / "data/soctra/processed/soctra_february_reference.parquet"
CONOPS = ROOT / "studies/soc_triage_hls_availability_robustness/config/SOC_NEW_MODEL_CONOPS_REFERENCE_SOCTRA_SEVERITY_V1.json"
SEVERITIES = ("critical", "high", "medium")
LABELS = (
    "escalada_L2_original", "escalada_procedimiento_original",
    "escalada_procedimiento_corregida", "escalada_combinada_antes_estandarizacion",
    "escalada_estandarizada",
)


def _fmt(x, digits=3):
    if x is None or not np.isfinite(float(x)):
        return "—"
    return f"{float(x):,.{digits}f}"


def _pval(p: float) -> str:
    return "<1e-300" if p == 0 else f"{p:.2g}"


def _cramers_v(frame: pd.DataFrame) -> tuple[float, float]:
    tab = pd.crosstab(frame.iloc[:, 0], frame.iloc[:, 1])
    if min(tab.shape) < 2:
        return 0.0, 1.0
    chi2, p, _, _ = chi2_contingency(tab, correction=False)
    n = tab.to_numpy().sum()
    return float(np.sqrt(chi2 / (n * (min(tab.shape) - 1)))), float(p)


def _prev_table(frame: pd.DataFrame, group: str, labels: tuple[str, ...]) -> list[str]:
    lines = [f"| {group} | N | " + " | ".join(f"{x} n (prev. %)" for x in labels) + " |",
             "|---|---:|" + "---:|" * len(labels)]
    for key, rows in frame.groupby(group, dropna=False, sort=False):
        cells = []
        for label in labels:
            present = rows[label].notna()
            n = int(present.sum())
            pos = int(rows.loc[present, label].astype(bool).sum())
            cells.append(f"{pos:,} ({100 * pos / n:.3f})" if n else "—")
        lines.append(f"| {key} | {len(rows):,} | " + " | ".join(cells) + " |")
    return lines


def _period_table(frame: pd.DataFrame, timestamp: str, labels: tuple[str, ...]) -> list[str]:
    dates = pd.to_datetime(frame[timestamp], errors="coerce")
    groups = frame.assign(_month=dates.dt.to_period("M").astype(str)).groupby("_month", sort=True)
    lines = ["| Month | Records | " + " | ".join(f"{x} %" for x in labels) + " |",
             "|---|---:|" + "---:|" * len(labels)]
    for month, rows in groups:
        vals = []
        for label in labels:
            n = int(rows[label].notna().sum())
            pos = int(rows[label].fillna(False).astype(bool).sum())
            vals.append(f"{100*pos/n:.3f}" if n else "—")
        lines.append(f"| {month} | {len(rows):,} | " + " | ".join(vals) + " |")
    return lines


def _rolling_peak(hours: pd.Series, width: str) -> tuple[float, str]:
    hourly = hours.resample("h").size()
    rolled = hourly.rolling(width, min_periods=1).sum()
    ix = rolled.idxmax()
    return float(rolled.loc[ix]), str(ix)


def characterize(raw_path: Path, processed_path: Path, february_path: Path) -> str:
    raw = pd.read_csv(raw_path, low_memory=False)
    raw["@timestamp0"] = pd.to_datetime(raw["@timestamp0"], errors="coerce")
    processed = pd.read_parquet(processed_path)
    feb = pd.read_parquet(february_path)
    if not raw["id_alerta"].is_unique or not processed["id_alerta_original"].is_unique:
        raise ValueError("alert IDs must be unique before population matching")
    retained = set(processed["id_alerta_original"].astype(str))
    raw["_id"] = raw["id_alerta"].astype(str)
    raw["population"] = np.where(raw["_id"].isin(retained), "processed", "excluded")
    if len(retained & set(raw["_id"])) != len(processed):
        raise ValueError("processed IDs do not map one-to-one to the source CSV")

    project_counts = raw["proyecto"].fillna("<missing>").value_counts()
    project_code = {name: f"P{i:02d}" for i, (name, _) in
                    enumerate(project_counts.items(), start=1)}
    raw["project_code"] = raw["proyecto"].fillna("<missing>").map(project_code)
    processed["project_code"] = processed["proyecto"].fillna("<missing>").map(project_code)
    if processed["project_code"].isna().any():
        raise ValueError("processed project values not present in the source population")
    raw["severity_code"] = raw["severidad"].str.strip().str.casefold().fillna("unknown")
    processed["severity_code"] = processed["preprocessed__severidad"].str.strip().str.casefold().fillna("unknown")

    dates = raw["@timestamp0"].dropna().sort_values()
    days = raw.assign(_day=raw["@timestamp0"].dt.floor("D")).groupby("_day").size()
    hours = raw.set_index("@timestamp0").sort_index().index.to_series()
    hourly = raw.set_index("@timestamp0").resample("h").size()
    dow = raw.assign(_dow=raw["@timestamp0"].dt.day_name()).groupby("_dow").size()
    dow_days = raw.assign(_day=raw["@timestamp0"].dt.floor("D"),
                          _dow=raw["@timestamp0"].dt.day_name()).drop_duplicates("_day")
    dow_count = dow_days["_dow"].value_counts()
    by_hour = raw.assign(_hour=raw["@timestamp0"].dt.hour).groupby("_hour").size()
    weekly = raw.assign(_week=raw["@timestamp0"].dt.to_period("W-SUN").astype(str)).groupby("_week").size()
    monthly = raw.assign(_month=raw["@timestamp0"].dt.to_period("M").astype(str)).groupby("_month").size()

    out = ["# SOCTRA demand and sizing diagnostic", "",
           f"Generated from `{raw_path.name}` and existing canonical Parquets; source rows: {len(raw):,}; processed September: {len(processed):,}; excluded by integrated preprocessing: {int((raw.population == 'excluded').sum()):,}.",
           f"Timestamp coverage: {dates.iloc[0]} to {dates.iloc[-1]}; timezone is not encoded. Project labels are anonymized as P01… by descending source volume. These are alert-record counts, not established investigation counts.", "",
           "## 1. Demand records and timing", "",
           f"Observed source record intensity over {(dates.iloc[-1]-dates.iloc[0]).total_seconds()/86400:.1f} elapsed days: {len(raw)/((dates.iloc[-1]-dates.iloc[0]).total_seconds()/3600):.3f} records/h (all records), {len(processed)/((dates.iloc[-1]-dates.iloc[0]).total_seconds()/3600):.3f} processed records/h. The model's one-investigation-per-alert is a scenario assumption, not inferred from these counts.", "",
           "| Interval | Mean records | SD | Median | P90 | P95 | Max | CV |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, series in (("Hourly", hourly), ("Daily", days), ("ISO week", weekly), ("Month", monthly)):
        out.append(f"| {name} | {_fmt(series.mean())} | {_fmt(series.std(ddof=0))} | {_fmt(series.median())} | {_fmt(series.quantile(.9))} | {_fmt(series.quantile(.95))} | {int(series.max()):,} | {_fmt(series.std(ddof=0)/series.mean())} |")
    out += ["", "Peak trailing-window totals (overlapping windows; not independent episodes):"]
    for width in ("1h", "6h", "24h", "7D"):
        value, when = _rolling_peak(hours, width)
        out.append(f"- {width}: {value:,.0f} records ending {when}.")
    out += ["", "| Hour of day | Records | Share % |", "|---:|---:|---:|"]
    for hour in range(24):
        n = int(by_hour.get(hour, 0))
        out.append(f"| {hour:02d} | {n:,} | {100*n/len(raw):.2f} |")
    out += ["", "| Weekday | Records | Avg. records/calendar day |", "|---|---:|---:|"]
    for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"):
        out.append(f"| {day} | {int(dow.get(day,0)):,} | {dow.get(day,0)/max(1,dow_count.get(day,0)):.2f} |")
    out += ["", "| Month | Records |", "|---|---:|"]
    out.extend(f"| {month} | {int(count):,} |" for month, count in monthly.items())

    out += ["", "## 2. Project distribution (anonymized)", "",
            "| Project code | Source records | Source share % | Processed | Retention % |", "|---|---:|---:|---:|---:|"]
    rawp = raw.groupby("project_code").size()
    procp = processed.groupby("project_code").size()
    processed_ranked=procp.sort_values(ascending=False)
    source_bins=(rawp.sort_values(ascending=False).iloc[:5].sum(),
                 rawp.sort_values(ascending=False).iloc[5:10].sum(),
                 rawp.sort_values(ascending=False).iloc[10:].sum())
    processed_bins=(processed_ranked.iloc[:5].sum(),processed_ranked.iloc[5:10].sum(),processed_ranked.iloc[10:].sum())
    out += [f"Empirical volume bins by within-population project rank (top five / next five / tail): source "
            f"{source_bins[0]:,}/{source_bins[1]:,}/{source_bins[2]:,} = "
            f"{100*source_bins[0]/len(raw):.1f}/{100*source_bins[1]/len(raw):.1f}/{100*source_bins[2]/len(raw):.1f}% of source; "
            f"processed {processed_bins[0]:,}/{processed_bins[1]:,}/{processed_bins[2]:,} = "
            f"{100*processed_bins[0]/len(processed):.1f}/{100*processed_bins[1]/len(processed):.1f}/{100*processed_bins[2]/len(processed):.1f}%.", "",
            "These do not match the current synthetic project-class mix of 50/30/20 exactly; a top-five bucket may also obscure heterogeneous severity/escalation. No project labels are mapped to capabilities.", ""]
    for code in rawp.index:
        n, m = int(rawp[code]), int(procp.get(code, 0))
        out.append(f"| {code} | {n:,} | {100*n/len(raw):.2f} | {m:,} | {100*m/n:.2f} |")
    for pop_name, frame in (("source",raw),("processed",processed)):
        tab=pd.crosstab(frame.project_code,frame.severity_code.str.upper())
        out += ["", f"Project×severity counts ({pop_name}; codes ranked by source volume):", "",
                "| Project | N | CRITICAL | HIGH | MEDIUM |", "|---|---:|---:|---:|---:|"]
        for code in rawp.index:
            if code not in tab.index: continue
            row=tab.loc[code]
            out.append(f"| {code} | {int(row.sum()):,} | {int(row.get('CRITICAL',0)):,} | {int(row.get('HIGH',0)):,} | {int(row.get('MEDIUM',0)):,} |")
    raw_v, raw_p = _cramers_v(raw[["project_code", "severity_code"]])
    proc_v, proc_p = _cramers_v(processed[["project_code", "severity_code"]])
    out += ["", f"Project×severity association (Cramér V): source {raw_v:.3f} (p={_pval(raw_p)}); processed {proc_v:.3f} (p={_pval(proc_p)}). These are descriptive associations, not causal effects.", "",
            "| Dataset / label | Project association V (p) | Severity association V (p) |", "|---|---:|---:|"]
    for pop_name, frame, labels, sev_col in (
        ("source", raw, ("escalada_L2", "escalada_procedimiento"), "severity_code"),
        ("processed", processed, LABELS, "severity_code"),
    ):
        for label in labels:
            v1, p1 = _cramers_v(frame[["project_code", label]].dropna())
            v2, p2 = _cramers_v(frame[[sev_col, label]].dropna())
            out.append(f"| {pop_name} `{label}` | {v1:.3f} ({_pval(p1)}) | {v2:.3f} ({_pval(p2)}) |")
    out += ["", "### Escalation prevalence by project", "",
            *_prev_table(raw.assign(escalada_L2=raw.escalada_L2.astype(bool),
                                    escalada_procedimiento=raw.escalada_procedimiento.astype(bool)),
                         "project_code", ("escalada_L2", "escalada_procedimiento")),
            "", "Processed standardized prevalence by project:", "",
            *_prev_table(processed, "project_code", ("escalada_estandarizada",)),
            "", "### Escalation prevalence by month (processed population)", "",
            *_period_table(processed, "timestamp_original", LABELS)]
    out += ["", "### Project association within severity strata (processed)", "",
            "Per-severity standardized prevalence spans projects with at least 100 records; project names are omitted.", "",
            "| Severity | Projects included | Prevalence range | Cramér V(project×standardized label) |",
            "|---|---:|---:|---:|"]
    for severity in SEVERITIES:
        subset=processed.loc[processed.severity_code.eq(severity)]
        values=[float(group.escalada_estandarizada.mean()) for _,group in subset.groupby("project_code") if len(group)>=100]
        v,_=_cramers_v(subset[["project_code","escalada_estandarizada"]])
        span=f"{100*min(values):.3f}–{100*max(values):.3f}%" if values else "—"
        out.append(f"| {severity.upper()} | {len(values)} | {span} | {v:.3f} |")

    feb_test = feb.loc[feb["partition_test"].astype(bool)]
    sep_l2 = int(processed["escalada_L2_original"].sum())
    sep_proc = int(processed["escalada_procedimiento_original"].sum())
    sep_std = int(processed["escalada_estandarizada"].sum())
    out += ["", "## 3. September global versus February temporal test", "",
            "| Population | N | L2 original + (%) | Procedure original + (%) | Procedure corrected + (%) | Combined pre-standardization + (%) | Standardized + (%) |",
            "|---|---:|---:|---:|---:|---:|---:|"]
    for name, frame in (("September processed global", processed), ("February processed test", feb_test)):
        vals=[]
        for label in LABELS:
            pos=int(frame[label].sum()); vals.append(f"{pos:,} ({100*pos/len(frame):.4f})")
        out.append(f"| {name} | {len(frame):,} | " + " | ".join(vals) + " |")
    out += ["", f"September global standardized: {sep_std:,}/{len(processed):,} = {100*sep_std/len(processed):.4f}%; February test: {int(feb_test.escalada_estandarizada.sum()):,}/{len(feb_test):,} = {100*feb_test.escalada_estandarizada.mean():.4f}%. These populations differ in snapshot and preprocessing/split context; this is not a matched-period estimator.",
            "", "## 4. Analytical load and capacity (no queue simulation)", ""]

    scenario = load_scenario(CONOPS)
    demand = scenario.demand_profile
    class_mix = demand["class_mix"]
    base_rate = demand["arrival_intensity_total_per_h"]
    pi = float(next(iter(demand["prevalence_by_class"].values())))
    detection = float(next(iter(demand["sensitivity_by_class"].values())))
    pfa = float(next(iter(demand["false_positive_rate_by_class"].values())))
    p_tp, p_fp = pi*detection, (1-pi)*pfa
    p_fn = pi*(1-detection)
    p_tn = (1-pi)*(1-pfa)
    p_l2 = p_tp + p_fp
    p_l1 = 1-p_l2
    qneed,qordinary=map(float,demand["difficulty_mean_by_class_and_need"][next(iter(class_mix))])
    wneed=1+float(demand["beta"])*(qneed-.5)
    wordinary=1+float(demand["beta"])*(qordinary-.5)
    l1_base_by_class={k:np.mean([r.service_by_class[k] for r in scenario.organization.resources_for("L1") if k in r.analyst.eligible_classes]) for k in class_mix}
    l2_base_by_class={k:np.mean([r.service_by_class[k] for r in scenario.organization.resources_for("L2") if k in r.analyst.eligible_classes]) for k in class_mix}
    components={"L1 TN":0.0,"L1 FN":0.0,"L2 FP":0.0,"L2 TP":0.0}
    for k,share in class_mix.items():
        rate=base_rate*float(share)
        components["L1 TN"] += rate*p_tn*wordinary*l1_base_by_class[k]
        components["L1 FN"] += rate*p_fn*float(demand["gamma"])*wneed*l1_base_by_class[k]
        components["L2 FP"] += rate*p_fp*float(demand["alpha"])*wordinary*l2_base_by_class[k]
        components["L2 TP"] += rate*p_tp*wneed*l2_base_by_class[k]
    out += [f"Classifier routing probabilities under the frozen CONOPS: L2 TP={100*p_tp:.4f}% of records, L2 FP={100*p_fp:.4f}%, total L2={100*p_l2:.3f}%; L1 TN={100*p_tn:.3f}%, FN={100*p_fn:.4f}%, total L1={100*p_l1:.3f}%. False positives account for {100*p_fp/p_l2:.2f}% of L2 investigation records. These are classifier-model expectations, not SOCTRA empirical escalation rates.", "",
            f"Expected complexity-work multipliers are {wordinary:.3f} for ordinary/no-need q and {wneed:.3f} for need q (Beta(2,2) truncated at q0); false positives remain ordinary work at L2, while false negatives carry high-q work at L1. At base intensity the component work rates are:", "",
            "| Component | Route records/h | Mean service h/record | Offered work h-person/h |", "|---|---:|---:|---:|"]
    for name,probability in (("L1 TN",p_tn),("L1 FN",p_fn),("L2 FP",p_fp),("L2 TP",p_tp)):
        route_rate=base_rate*probability
        out.append(f"| {name} | {route_rate:.4f} | {components[name]/route_rate:.4f} | {components[name]:.4f} |")
    out += ["", f"False-positive investigations account for {100*components['L2 FP']/(components['L2 FP']+components['L2 TP']):.2f}% of expected L2 work in this model; this is distinct from their 97.60% share of L2 route records.", "",
            "`assess_capacity` evaluates the existing eligibility-constrained fluid LP for the 5-L1/3-L2 reference roster; it is an analytic mean-load bound, not a queue or SLA guarantee. The record-to-investigation conversion factor κ is unknown; rates below assume κ=1 and scale linearly in κ.", "",
            "| Record intensity × | records/h | L1 records/h | L2 records/h | L1 work h-person/h | L2 work h-person/h | L1 assignable arrivals/h | L2 assignable arrivals/h | LP load L1 | LP load L2 |", "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    base_regime = demand["regimes"][0]
    for mult in (0.25, 0.5, 1.0, 1.5, 2.0):
        rates={k:float(v)*mult for k,v in base_regime["arrival_rate_by_class"].items()}
        profile=CapacityDemandProfile(
            regimes=(DemandRegime(f"x{mult:g}",0,1,rates),),
            prevalence_by_class=demand["prevalence_by_class"],
            sensitivity_by_class=demand["sensitivity_by_class"],
            false_positive_rate_by_class=demand["false_positive_rate_by_class"],
            alpha=demand["alpha"], beta=demand["beta"], gamma=demand["gamma"],
            difficulty_mean_by_class_and_need=demand["difficulty_mean_by_class_and_need"],
            flow_mode=scenario.flow_mode)
        cap=assess_capacity(scenario.organization,profile).regimes
        l1=next(x for x in cap if x.level=="L1"); l2=next(x for x in cap if x.level=="L2")
        total_rate=base_rate*mult
        out.append(f"| {mult:.2f} | {total_rate:.3f} | {total_rate*p_l1:.3f} | {total_rate*p_l2:.3f} | {l1.offered_l1_work_h_per_h:.3f} | {l2.offered_l2_work_h_per_h:.3f} | {l1.capacity_per_h:.3f} | {l2.capacity_per_h:.3f} | {l1.relative_load:.3f} | {l2.relative_load:.3f} |")
    work_l1 = assess_capacity(scenario.organization, CapacityDemandProfile(
        regimes=(DemandRegime("base",0,1,base_regime["arrival_rate_by_class"]),),
        prevalence_by_class=demand["prevalence_by_class"], sensitivity_by_class=demand["sensitivity_by_class"],
        false_positive_rate_by_class=demand["false_positive_rate_by_class"], alpha=demand["alpha"], beta=demand["beta"],
        gamma=demand["gamma"], difficulty_mean_by_class_and_need=demand["difficulty_mean_by_class_and_need"],
        flow_mode=scenario.flow_mode)).regimes
    baseline=work_l1
    first_l1=next(x for x in baseline if x.level=="L1")
    first_l2=next(x for x in baseline if x.level=="L2")
    util_l1=first_l1.offered_l1_work_h_per_h/5
    util_l2=first_l2.offered_l2_work_h_per_h/3
    u_ratio=util_l1/util_l2 if util_l2 else float("inf")
    time1=np.mean([v for r in scenario.organization.resources_for("L1") for v in r.service_by_class.values()])
    time2=np.mean([v for r in scenario.organization.resources_for("L2") for v in r.service_by_class.values()])
    eq_share=3*time1/(5*time2+3*time1)
    out += ["", "Synthetic team parameters from the scenario; statistics are over analyst×eligible-class cells:", "",
            "| Level | Analysts | Eligible cells | Competence min/median/max | Service h min/median/max | Speed min/median/max (1/h) |",
            "|---|---:|---:|---:|---:|---:|"]
    for level in ("L1","L2"):
        resources=scenario.organization.resources_for(level)
        comp=[float(r.analyst.competence[k]) for r in resources for k in r.analyst.eligible_classes]
        service=[float(r.service_by_class[k]) for r in resources for k in r.analyst.eligible_classes]
        speed=[1/x for x in service]
        triple=lambda xs: "/".join(_fmt(x,3) for x in (min(xs),float(np.median(xs)),max(xs)))
        out.append(f"| {level} | {len(resources)} | {len(service)} | {triple(comp)} | {triple(service)} | {triple(speed)} |")
    individual_u={"L1":[x*first_l1.relative_load for _,x in first_l1.analyst_utilization_at_capacity],
                  "L2":[x*first_l2.relative_load for _,x in first_l2.analyst_utilization_at_capacity]}
    out += ["", "Fluid LP individual-assignment utilization at base demand (capacity allocation scaled by relative load; not dispatch):", "",
            "| Level | Min / median / max |", "|---|---:|"]
    for level,values in individual_u.items():
        out.append(f"| {level} | " + " / ".join(f"{100*x:.1f}%" for x in (min(values),float(np.median(values)),max(values))) + " |")
    out += ["", "Roster-size sensitivity using the same mean work rates, full availability and fractional fluid assignment; this omits discrete eligibility bottlenecks, so the 5/3 capacity result above is authoritative:", "",
            "| L1 analysts | L2 analysts | L1 mean utilization | L2 mean utilization |", "|---:|---:|---:|---:|"]
    for n1,n2 in ((3,1),(5,1),(5,3),(10,1),(10,2),(10,3),(20,1),(20,2),(28,1)):
        out.append(f"| {n1} | {n2} | {100*first_l1.offered_l1_work_h_per_h/n1:.1f}% | {100*first_l2.offered_l2_work_h_per_h/n2:.1f}% |")
    capwork1=float(len(scenario.organization.resources_for("L1")))
    pulse_mult,pulse_h=2.5,6.0
    backlog=max(0.0,first_l1.offered_l1_work_h_per_h*pulse_mult-capwork1)*pulse_h
    recovery=backlog/(capwork1-first_l1.offered_l1_work_h_per_h)
    threshold=first_l1.capacity_per_h/first_l1.offered_rate_per_h
    out += ["", f"For L1, the fluid overload threshold is about {threshold:.2f}× the base record stream. A constructed x2.5 pulse for 6 h then returning to x1 accumulates about {backlog:.2f} analyst-work h and clears in about {recovery:.2f} h at constant spare baseline capacity. This is arithmetic on the fluid LP, not a simulated episode or empirical recovery event.", ""]
    out += ["", f"At the model's base intensity ({base_rate:.3f} record arrivals/h), mean offered active work implies utilization about {100*util_l1:.1f}% for L1 and {100*util_l2:.1f}% for L2 across the 5 and 3 continuously available analysts (work-equivalent, fluid mean). L1/L2 utilization ratio is {u_ratio:.1f}:1. The reference roster's eligible-analyst mean base service times are {_fmt(time1,4)} h (L1) and {_fmt(time2,4)} h (L2); individual/class service values range {_fmt(min(v for r in scenario.organization.resources_for('L1') for v in r.service_by_class.values()),4)}–{_fmt(max(v for r in scenario.organization.resources_for('L1') for v in r.service_by_class.values()),4)} h and {_fmt(min(v for r in scenario.organization.resources_for('L2') for v in r.service_by_class.values()),4)}–{_fmt(max(v for r in scenario.organization.resources_for('L2') for v in r.service_by_class.values()),4)} h, respectively. The implied L2 route share for equal aggregate utilization with this 5:3 roster and these average base times would be approximately {100*eq_share:.1f}%, versus model expectation {100*p_l2:.2f}%. This is a structural workload mismatch, not proof that an operational L2 team is idle; unmodeled L2 activities are outside scope.", "",
            "### Work duration versus synthetic deadlines", "",
            "For a requested slack fraction s reserved for queueing/congestion, the no-queue active-work ceiling is `(1−s)×deadline`. These are feasibility envelopes, not estimates of actual SOCTRA investigation times:", "",
            "| Severity / synthetic completion SLA | At least 50% slack | At least 75% slack |",
            "|---|---:|---:|"]
    for severity, deadline in (("CRITICAL",1),("HIGH",4),("MEDIUM",12)):
        out.append(f"| {severity} / {deadline} h | ≤ {deadline/2:.2f} h work | ≤ {deadline/4:.2f} h work |")
    out += ["", "The synthetic work model uses `W(q)=1+β(q−0.5)`, β=1, so per-investigation work varies from 0.5× to 1.5× base duration; it is independent of severity. L1 receives TN and FN; FN has high-q work, while γ=1 adds no extra multiplier. L2 receives TP and FP; FP consumes modeled L2 service at ordinary (`q<q0`) complexity, not zero work. No duration or route is observed in SOCTRA. A service time exceeding a deadline is infeasible even with an empty queue; service below it leaves `deadline−service` for waiting, but finite-arrival congestion may consume that margin.", "",
            "### Reduced, normal, elevated and transient regimes", "",
            "The x0.25/x0.5/x1/x1.5/x2 rows above hold organization, classifier, competence, speeds, work model and policies constant while multiplying arrivals. Read utilization and fluid LP load separately: utilization is expected offered work divided by team analyst-hours; LP load additionally accounts for class eligibility and assignment. Example operating labels (not calibrated cutoffs): reduced <0.5 utilization, normal 0.5–0.75, elevated 0.75–1, structural overload >1. A pulse is transiently saturating when its offered load exceeds capacity while baseline remains below capacity. After returning to baseline, idealized fluid recovery time is backlog work divided by spare baseline capacity; stochastic queues, schedules and SLA tails require a later explicitly authorized study.", "",
            "## 5. Identification boundary", "",
            "| Quantity | Status | What is identified |",
            "|---|---|---|",
            "| Alert counts/timestamps/project/severity/recorded escalation labels | A. Estimable from data | Historical records after stated population selection; timestamps lack an encoded timezone. Project is not assumed synonymous with client.",
            "| Initial-assignment SLA breach flag | A. Estimable from data | A recorded binary breach/reason field; no assignment timestamp or contractual duration to reconstruct elapsed time.",
            "| Generalist/specialist attention patterns | B. Qualitative only | Available organizational context suggests different attention, not measured activity rates or staffing shares.",
            "| One record = one investigation; κ; arrival process; q distribution and q0; classifier errors; service times; speeds, competencies, roster size; 1/4/12h completion SLAs | C. Synthetic | Explicit scenario assumptions; none should be described as SOCTRA-measured operations.",
            "| Number of L2 investigations/activities | Not identified | No per-alert assignment-stage or investigation event history is available to infer additional L2 work. Do not add activities solely to fill L2 capacity.", "",
            "For a common update, set `SOCTRA_RAW_SEPTEMBER` to the local CSV path, then run this aggregate-only command; it does not regenerate data or execute a simulation:", "",
            "```sh",
            "python studies/soc_triage_hls_availability_robustness/analyze_soctra_demand_capacity.py \\",
            "  --raw-september \"$SOCTRA_RAW_SEPTEMBER\" \\",
            "  --processed-september data/soctra/processed/soctra_preprocessed.parquet \\",
            "  --processed-february data/soctra/processed/soctra_february_reference.parquet",
            "```", ""]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-september", type=Path, required=True)
    parser.add_argument("--processed-september", type=Path, default=DEFAULT_PROCESSED)
    parser.add_argument("--processed-february", type=Path, default=DEFAULT_FEBRUARY)
    args = parser.parse_args()
    print(characterize(args.raw_september, args.processed_september, args.processed_february))


if __name__ == "__main__":
    main()
