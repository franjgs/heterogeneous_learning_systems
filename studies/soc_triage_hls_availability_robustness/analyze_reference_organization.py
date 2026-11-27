"""Reproducible non-campaign diagnostics for the versioned synthetic roster.

Run from the repository root. The time grid enumerates one Monday-starting
week; it does not draw arrivals, invoke an engine, or compare policies.
"""
from __future__ import annotations

import json
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
CONFIG = ROOT / "config" / "SOC_REFERENCE_ORGANIZATION_V1.json"


def weighted_quantile(rows, field: str, probability: float) -> float:
    ordered = sorted((float(row[field]), float(row["weight"])) for row in rows)
    target = probability * sum(weight for _, weight in ordered)
    cumulative = 0.0
    for value, weight in ordered:
        cumulative += weight
        if cumulative >= target:
            return value
    return ordered[-1][0]


def main() -> None:
    scenario = load_scenario(CONFIG)
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
        routes = ((False, 1.0 - pi * pd - (1.0 - pi) * pfa, 1.0),
                  (True, pi * pd, 1.0),
                  (True, (1.0 - pi) * pfa, demand["alpha"]))
        for severity in ("high", "medium", "low"):
            alerts = tuple(Alert(f"{task_class}-{severity}-{h:04d}", h * .25 + .125,
                                 task_class, h * .25 + .125 + scenario.settings.deadlines.offsets_by_severity_h[severity])
                           for h in range(672))
            for needs_l2, route_weight, alpha in routes:
                if route_weight == 0:
                    continue
                env = EnvironmentRealization(
                    service_scale_by_alert={a.alert_id: alpha for a in alerts},
                    difficulty_by_alert={a.alert_id: .5 for a in alerts},
                    difficulty_service_beta=demand["beta"],
                )
                request = scenario.request_for("L1", alerts,
                    severity_by_alert={a.alert_id: severity for a in alerts}, environment=env)
                report = assess_deadline_feasibility(
                    request, l2_required_by_alert={a.alert_id: needs_l2 for a in alerts},
                    route_basis="scenario_route", environment=env, include_calendars=True,
                )
                rows.append({"class": task_class, "severity": severity,
                             "route": "L1+L2" if needs_l2 else "L1",
                             "route_probability": route_weight,
                             "alpha": alpha,
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
                for route in ("L1", "L1+L2")
            },
        },
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
