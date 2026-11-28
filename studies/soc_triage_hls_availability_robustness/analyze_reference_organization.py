"""Reproducible non-campaign diagnostics for the versioned synthetic roster.

Run from the repository root. The time grid enumerates one Monday-starting
week; it does not draw arrivals, invoke an engine, or compare policies.
"""
from __future__ import annotations

import json
import argparse
from pathlib import Path
import sys

ROOT_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_REPO))
sys.path.insert(0, str(ROOT_REPO / "src"))

from hls.rq1_allocation import Alert
from studies.soc_triage_hls_availability_robustness.execution_api import EnvironmentRealization
from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import (
    CapacityDemandProfile, DemandRegime, assess_capacity, assess_deadline_feasibility,
)
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario


ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config" / "SOC_REFERENCE_ORGANIZATION_V2_24X7.json"


def weighted_quantile(rows, field: str, probability: float) -> float:
    ordered = sorted((float(row[field]), float(row["weight"])) for row in rows)
    target = probability * sum(weight for _, weight in ordered)
    cumulative = 0.0
    for value, weight in ordered:
        cumulative += weight
        if cumulative >= target:
            return value
    return ordered[-1][0]


def expected_l2_outside_schedule(scenario, demand, width_h: float = 0.25) -> dict:
    """Expected offered L2 alerts/work during intervals with no L2 coverage."""
    l2 = scenario.organization.resources_for("L2")
    horizon = scenario.settings.admission_horizon
    classes = tuple(demand["class_mix"])
    bins = int(round(horizon / width_h))
    count = work = 0.0
    by_regime = {}
    for index in range(bins):
        start = index * width_h
        midpoint = start + width_h / 2
        regime = next(r for r in demand["regimes"] if r["start_h"] <= midpoint < r["end_h"])
        available = any(r.calendar and r.calendar.available(midpoint) for r in l2)
        if available:
            continue
        c_count = c_work = 0.0
        for k in classes:
            rate = float(regime["arrival_rate_by_class"][k])
            pi = float(demand["prevalence_by_class"][k])
            pd = float(demand["sensitivity_by_class"][k])
            pfa = float(demand["false_positive_rate_by_class"][k])
            route = pi * pd + (1 - pi) * pfa
            tp = pi * pd
            fp = (1 - pi) * pfa
            conditional_service_factor = (tp + fp * float(demand["alpha"])) / route if route else 1.0
            eligible = [r for r in l2 if k in r.analyst.eligible_classes]
            mean_service = sum(r.service_by_class[k] for r in eligible) / len(eligible) if eligible else 0.0
            c_count += rate * route * width_h
            c_work += rate * route * conditional_service_factor * mean_service * width_h
        count += c_count
        work += c_work
        entry = by_regime.setdefault(regime["name"], {"alerts": 0.0, "work_h": 0.0})
        entry["alerts"] += c_count
        entry["work_h"] += c_work
    return {"method": f"{width_h:g}-hour midpoint integration; configured classifier and alpha; mean eligible L2 service per class",
            "l2_covered_hours_per_week": sum(
                any(r.calendar and r.calendar.available(i + .5) for r in l2)
                for i in range(int(horizon))),
            "off_schedule_expected_routed_alerts": count,
            "off_schedule_expected_service_work_h": work,
            "by_regime": by_regime,
            "interpretation": "unserved at arrival; queues until L2 coverage resumes. Not a queueing simulation."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG,
                        help="scenario JSON (defaults to the V2_24X7 experimental base)")
    scenario = load_scenario(parser.parse_args().config)
    demand = scenario.demand_profile
    classes = tuple(demand["prevalence_by_class"])
    profile = CapacityDemandProfile(
        regimes=tuple(DemandRegime(r["name"], r["start_h"], r["end_h"],
                                   r["arrival_rate_by_class"])
                      for r in demand["regimes"]),
        prevalence_by_class=demand["prevalence_by_class"],
        sensitivity_by_class=demand["sensitivity_by_class"],
        false_positive_rate_by_class=demand["false_positive_rate_by_class"],
        alpha=demand["alpha"], beta=demand["beta"],
        difficulty_mean_by_class_and_need=demand.get("difficulty_mean_by_class_and_need"),
        gamma=demand.get("gamma", 1.0), flow_mode=scenario.flow_mode,
    )
    capacity = assess_capacity(scenario.organization, profile)

    # Deterministic enumeration over 15-minute arrival bins at each bin midpoint,
    # weighted by configured class/severity prevalence and TP/FP probability.
    class_mix = demand["class_mix"]
    severity_mix = demand["severity_mix"]
    rows = []
    slack_rows = []
    for task_class in classes:
        pi = demand["prevalence_by_class"][task_class]
        pd = demand["sensitivity_by_class"][task_class]
        pfa = demand["false_positive_rate_by_class"][task_class]
        routes = ((False, (1.0 - pi) * (1.0 - pfa), "TN", 1.0),
                  (False, pi * (1.0 - pd), "FN", demand.get("gamma", 1.0)),
                  (True, pi * pd, "TP", 1.0),
                  (True, (1.0 - pi) * pfa, "FP", demand["alpha"]))
        for severity in ("high", "medium", "low"):
            alerts = tuple(Alert(f"{task_class}-{severity}-{h:04d}", h * .25 + .125,
                                 task_class, h * .25 + .125 + scenario.settings.deadlines.offsets_by_severity_h[severity])
                           for h in range(672))
            for route_l2, route_weight, confusion, multiplier in routes:
                if route_weight == 0:
                    continue
                env = EnvironmentRealization(
                    service_scale_by_alert={a.alert_id: multiplier for a in alerts},
                    difficulty_by_alert={a.alert_id: .5 for a in alerts},
                    difficulty_service_beta=demand["beta"],
                )
                request = scenario.request_for("L1", alerts,
                    severity_by_alert={a.alert_id: severity for a in alerts}, environment=env)
                report = assess_deadline_feasibility(
                    request, l2_required_by_alert={a.alert_id: route_l2 for a in alerts},
                    route_basis="scenario_route", environment=env, include_calendars=True,
                    flow_mode=scenario.flow_mode,
                )
                rows.append({"class": task_class, "severity": severity, "confusion": confusion,
                             "route": "L2" if route_l2 else "L1",
                             "route_probability": route_weight,
                             "service_multiplier": multiplier,
                             "intrinsic_infeasible_fraction": report.infeasible_fraction,
                             "calendar_infeasible_fraction": report.calendar_infeasible_fraction,
                             "weight": class_mix[task_class] * severity_mix[severity] * route_weight})
                task_weight = class_mix[task_class] * severity_mix[severity] * route_weight / len(report.tasks)
                slack_rows.extend({"severity": severity, "weight": task_weight,
                                   "optimistic_slack_h": task.optimistic_slack_h,
                                   "calendar_slack_h": task.calendar_slack_h}
                                  for task in report.tasks)

    total_weight = sum(x["weight"] for x in rows)
    overall_intrinsic = sum(x["weight"] * x["intrinsic_infeasible_fraction"] for x in rows) / total_weight
    overall_calendar = sum(x["weight"] * x["calendar_infeasible_fraction"] for x in rows) / total_weight
    by_severity = {}
    for severity in severity_mix:
        group = [x for x in rows if x["severity"] == severity]
        weight = sum(x["weight"] for x in group)
        by_severity[severity] = {
            "intrinsic_infeasible_fraction": sum(x["weight"] * x["intrinsic_infeasible_fraction"] for x in group) / weight,
            "calendar_infeasible_fraction": sum(x["weight"] * x["calendar_infeasible_fraction"] for x in group) / weight,
            "optimistic_slack_quantiles_h": {f"p{p:02d}": weighted_quantile([x for x in slack_rows if x["severity"] == severity], "optimistic_slack_h", p / 100) for p in (10, 50, 90)},
            "calendar_slack_quantiles_h": {f"p{p:02d}": weighted_quantile([x for x in slack_rows if x["severity"] == severity], "calendar_slack_h", p / 100) for p in (10, 50, 90)},
        }

    cost = scenario.cost_model
    print(json.dumps({
        "scenario_id": scenario.scenario_id,
        "diagnostic_only": True,
        "capacity": [vars(x) for x in capacity.regimes],
        "capacity_assumptions": capacity.assumptions,
        "temporal_feasibility": {
            "method": "one-week, Monday 00:00 anchored 15-minute midpoint grid, weighted by configured class, severity and classifier TP/FP probabilities; not a stochastic trace",
            "alerts_intrinsically_infeasible_fraction": overall_intrinsic,
            "alerts_calendar_infeasible_fraction": overall_calendar,
            "optimistic_slack_min_h": min(x["optimistic_slack_h"] for x in slack_rows),
            "calendar_slack_min_h": min(x["calendar_slack_h"] for x in slack_rows),
            "optimistic_slack_quantiles_h": {f"p{p:02d}": weighted_quantile(slack_rows, "optimistic_slack_h", p / 100) for p in (10, 50, 90)},
            "calendar_slack_quantiles_h": {f"p{p:02d}": weighted_quantile(slack_rows, "calendar_slack_h", p / 100) for p in (10, 50, 90)},
            "by_severity": by_severity,
            "route_conditioned_calendar_infeasible_fraction": {
                route: sum(x["weight"] * x["calendar_infeasible_fraction"] for x in rows if x["route"] == route) /
                       sum(x["weight"] for x in rows if x["route"] == route)
                for route in ("L1", "L2")
            },
        },
        "l2_off_schedule_accumulation": expected_l2_outside_schedule(scenario, demand),
        "cost": {
            "contracted_hours_per_week": dict(cost["contracted_hours_per_week"]),
            "scheduled_cost_units_per_week": {
                level: cost["contracted_hours_per_week"][level] * cost["normalization"][level]
                for level in cost["contracted_hours_per_week"]
            },
            "hourly_relative_rates": dict(cost["normalization"]),
        },
        "l2_saturday_sunday_offered_routed_alerts_expected": sum(
            sum(r["arrival_rate_by_class"].values()) *
            sum(class_mix[k] * (demand["prevalence_by_class"][k] * demand["sensitivity_by_class"][k] +
                                (1-demand["prevalence_by_class"][k]) * demand["false_positive_rate_by_class"][k])
                for k in classes) * (r["end_h"] - r["start_h"])
            for r in demand["regimes"] if r["start_h"] >= 120
        ),
    }, indent=2, default=list))


if __name__ == "__main__":
    main()
