"""Aggregate-only feasibility-frontier analysis; never invokes a simulator."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "results" / "soc_triage_feasibility_frontier"
CAMPAIGN = ROOT / "results" / "soc_triage_classifier_frontier_campaign"
SOURCE = ROOT / "results" / "soc_triage_classifier_operating_impact_source_audit"
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from studies.soc_human_ai_organization.soc_parametric_baseline import (  # noqa: E402
    BASE_ELIGIBILITY, BASE_L1_ANALYSTS, BASE_L2_ANALYSTS, BASE_SERVICE_L1_H,
    BASE_SERVICE_L2_H, PROJECT_MIX, PROJECTS, build_roster,
)
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity  # noqa: E402
from studies.soc_triage_organization_coupling.run_pilot import MU_L1  # noqa: E402

POLICIES = ("D1", "P1", "HLS-B")
POLICY_LABEL = {"HLS-B": "WAPS"}
ANALYSIS_CONFIG_PATH = HERE / "config" / "analysis.json"
ANALYSIS_CONFIG = json.loads(ANALYSIS_CONFIG_PATH.read_text(encoding="utf-8"))
BOOTSTRAP_REPS = int(ANALYSIS_CONFIG["bootstrap"]["replicates"])
BOOTSTRAP_SEED = int(ANALYSIS_CONFIG["bootstrap"]["seed"])
D_MIN_GRID = tuple(ANALYSIS_CONFIG["threshold_grid"]["d_min"])
RHO_MAX_GRID = tuple(ANALYSIS_CONFIG["threshold_grid"]["rho_max"])
S_MIN_GRID = tuple(ANALYSIS_CONFIG["threshold_grid"]["s_min"])


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def reconstruct_timely_numerator(row: dict[str, str], tolerance: float = 1e-9) -> int:
    """Recover exact count from saved per-episode rate and integer denominator.

    The campaign stores timely_needs / total_needs (not its numerator as a
    separate field). Recovering the integer is exact up to CSV float encoding;
    reject rows whose product is not numerically an integer.
    """
    denominator = int(row["true_need_count"])
    rate = float(row["necessary_L2_timely_per_need"])
    tp = int(row["TP_count"])
    fn = int(row["FN_count"])
    if denominator < 0 or tp < 0 or fn < 0 or tp + fn != denominator:
        raise ValueError("need denominator or TP/FN counts are inconsistent")
    if not 0.0 <= rate <= 1.0:
        raise ValueError("timely-needs rate is outside [0, 1]")
    if denominator == 0:
        if rate != 0.0 or tp != 0 or fn != 0:
            raise ValueError("zero-need episode has a nonzero rate or confusion count")
        return 0
    product = rate * denominator
    numerator = int(round(product))
    if abs(product - numerator) > tolerance:
        raise ValueError(f"saved per-episode rate does not imply an integer numerator: {product}")
    if numerator > tp:
        raise ValueError("timely necessary resolutions exceed true positive recommendations")
    return numerator


def aggregate_splus(rows: list[dict[str, str]]) -> dict:
    denominator = sum(int(row["true_need_count"]) for row in rows)
    numerator = sum(reconstruct_timely_numerator(row) for row in rows)
    tp = sum(int(row["TP_count"]) for row in rows)
    fn = sum(int(row["FN_count"]) for row in rows)
    if denominator != tp + fn:
        raise ValueError("aggregated total needs differs from TP+FN")
    s_plus = numerator / denominator if denominator else math.nan
    p_d_empirical = tp / denominator if denominator else math.nan
    g = numerator / tp if tp else math.nan
    if denominator and s_plus > p_d_empirical + 1e-12:
        raise ValueError("empirical S_plus exceeds empirical pD")
    return {"timely_need_numerator": numerator, "total_need_denominator": denominator,
            "TP_denominator": tp, "FN_count": fn, "S_plus": s_plus,
            "pD_empirical_pooled": p_d_empirical, "G_timely_given_TP": g}


def paired_bootstrap_splus(numerators: dict[str, np.ndarray],
                           denominators: dict[str, np.ndarray],
                           draw_indices: np.ndarray) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], int]:
    """Bootstrap ratios and paired contrasts with common seed-cluster draws."""
    if set(numerators) != set(denominators):
        raise ValueError("policy keys differ between numerators and denominators")
    policies = sorted(numerators)
    reference = denominators[policies[0]]
    for policy in policies:
        if not np.array_equal(denominators[policy], reference):
            raise ValueError("paired policies must share the same per-seed denominator")
        if len(numerators[policy]) != len(reference):
            raise ValueError("numerator/denominator lengths differ")
    sampled_den = reference[draw_indices].sum(axis=1)
    valid = sampled_den > 0
    zero_replicates = int((~valid).sum())
    estimates = {policy: numerators[policy][draw_indices].sum(axis=1)[valid] / sampled_den[valid]
                 for policy in policies}
    contrasts = {}
    for first, second, label in (("HLS-B", "D1", "WAPS-D1"),
                                  ("P1", "D1", "P1-D1"),
                                  ("HLS-B", "P1", "WAPS-P1")):
        if first in estimates and second in estimates:
            contrasts[label] = estimates[first] - estimates[second]
    return estimates, contrasts, zero_replicates


def status_for(detection_ok: bool, capacity_ok: bool, estimate: float,
               lower: float, upper: float, s_min: float) -> str:
    if not detection_ok:
        return "inadmissible_detection"
    if not capacity_ok:
        return "inadmissible_capacity"
    if lower >= s_min:
        return "admissible_supported_95"
    if upper < s_min:
        return "inadmissible_service_upper95_below"
    if estimate >= s_min:
        return "point_admissible_uncertain"
    return "indeterminate_service"


def point_admissible(p_d: float, rho: float, s_plus: float,
                     d_min: float, rho_max: float, s_min: float) -> bool:
    return p_d >= d_min and rho <= rho_max + 1e-12 and s_plus >= s_min


def supported_admissible(p_d: float, rho: float, lower_s_plus: float,
                         d_min: float, rho_max: float, s_min: float) -> bool:
    return p_d >= d_min and rho <= rho_max + 1e-12 and lower_s_plus >= s_min


def l2_offered_load_lp(point: dict, pi: float, rho_l1: float, n_l2: int) -> dict:
    """Minimum max analyst utilization needed to sustain class-specific flow."""
    p_d, p_fa = float(point["pD"]), float(point["pFA"])
    l1, analysts, _, services = build_roster(
        n_l1=BASE_L1_ANALYSTS, n_l2=n_l2, mean_eligible_projects=BASE_ELIGIBILITY)
    del l1
    lambda_all = MU_L1 * rho_l1
    pi_by_class = (pi,) * len(PROJECTS)
    q_by_class = tuple(p * p_d + (1.0 - p) * p_fa for p in pi_by_class)
    demands = tuple(lambda_all * PROJECT_MIX[k] * q_by_class[k]
                    for k in range(len(PROJECTS)))
    edges = [(a_ix, k) for a_ix, analyst in enumerate(analysts)
             for k, task_class in enumerate(PROJECTS) if task_class in analyst.eligible_classes]
    n_edges = len(edges)
    objective = [0.0] * n_edges + [1.0]
    a_eq, b_eq = [], []
    for k, demand in enumerate(demands):
        a_eq.append([float(edge_k == k) for _, edge_k in edges] + [0.0])
        b_eq.append(demand)
    a_ub, b_ub = [], []
    for a_ix, analyst in enumerate(analysts):
        row = [services[analyst.analyst_id][PROJECTS[k]] if edge_a == a_ix else 0.0
               for edge_a, k in edges] + [-1.0]
        a_ub.append(row)
        b_ub.append(0.0)
    solution = linprog(objective, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=b_eq,
                       bounds=[(0.0, None)] * (n_edges + 1), method="highs")
    if not solution.success:
        raise RuntimeError(f"heterogeneous capacity LP failed: {solution.message}")
    min_util = float(solution.x[-1])
    p_mix = sum(PROJECT_MIX[k] * q_by_class[k] for k in range(len(PROJECTS)))
    offered_l2 = lambda_all * p_mix
    mu_eff = offered_l2 / min_util if min_util > 0 else math.inf
    class_mean_service = {}
    for k, task_class in enumerate(PROJECTS):
        eligible_services = [services[a.analyst_id][task_class] for a in analysts
                             if task_class in a.eligible_classes]
        class_mean_service[task_class] = sum(eligible_services) / len(eligible_services)
    need_rates = tuple(lambda_all * PROJECT_MIX[k] * pi_by_class[k] for k in range(len(PROJECTS)))
    tp_rates = tuple(need_rates[k] * p_d for k in range(len(PROJECTS)))
    fn_rates = tuple(need_rates[k] * (1.0 - p_d) for k in range(len(PROJECTS)))
    fp_rates = tuple(lambda_all * PROJECT_MIX[k] * (1.0 - pi_by_class[k]) * p_fa
                     for k in range(len(PROJECTS)))
    work = lambda rates: sum(rates[k] * class_mean_service[PROJECTS[k]]
                             for k in range(len(PROJECTS)))
    # Existing effective_capacity uses the same fluid assignment model with
    # a fixed routed mix; compare its common-rate estimate as a check.
    routed_mix = tuple(demands[k] / offered_l2 if offered_l2 else PROJECT_MIX[k]
                       for k in range(len(PROJECTS)))
    mu_existing = effective_capacity(analysts, services, routed_mix)["max_common_arrivals_per_h"]
    if offered_l2 and abs(offered_l2 / mu_existing - min_util) > 1e-8:
        raise AssertionError("explicit per-analyst LP differs from existing effective-capacity LP")
    return {"lambda_L1_per_h": lambda_all, "q_expected": p_mix,
            "lambda_L2_offered_per_h": offered_l2,
            "lambda_TP_per_h": sum(tp_rates), "lambda_FP_per_h": sum(fp_rates),
            "lambda_FN_per_h": sum(fn_rates), "lambda_TN_per_h": lambda_all * (1.0-pi) * (1.0-p_fa),
            "L2_necessary_recommended_work_h_per_h": work(tp_rates),
            "L2_unnecessary_FP_work_h_per_h": work(fp_rates),
            "L2_necessary_omitted_FN_work_h_per_h": work(fn_rates),
            "effective_capacity_L2_per_h": mu_eff,
            "rho_L2_min_max_analyst_utilization": min_util,
            "rho_L2_offered_over_existing_LP_capacity": offered_l2 / mu_existing if mu_existing else math.inf,
            "class_specific_l2_rates": json.dumps(dict(zip(PROJECTS, demands)), separators=(",", ":"))}


def pfa_capacity_boundary(pi: float, p_d: float, lambda_l1: float,
                          n_l2: int, rho_max: float) -> dict:
    """Solve the heterogeneous LP boundary in pFA for the class mix at this pi."""
    # With this study's homogeneous pi across classes, pFA changes total load
    # without changing the class mix; the LP-derived mu is therefore fixed.
    template = {"pD": p_d, "pFA": 0.0}
    zero = l2_offered_load_lp(template, pi, lambda_l1 / MU_L1, n_l2)
    template["pFA"] = 1.0
    one = l2_offered_load_lp(template, pi, lambda_l1 / MU_L1, n_l2)
    mu = float(zero["effective_capacity_L2_per_h"])
    homogeneous_formula_raw = (rho_max * mu / lambda_l1 - pi * p_d) / (1.0 - pi)
    rho_zero = float(zero["rho_L2_min_max_analyst_utilization"])
    rho_one = float(one["rho_L2_min_max_analyst_utilization"])
    if rho_zero > rho_max + 1e-12:
        exact, state = None, "capacity_infeasible_even_at_pFA0"
    elif rho_one <= rho_max + 1e-12:
        exact, state = 1.0, "all_pFA_feasible"
    else:
        exact = min(1.0, max(0.0, homogeneous_formula_raw))
        # Validate the closed-form boundary with the heterogeneous assignment
        # LP. Here pi is homogeneous across classes, so changing pFA scales each
        # class flow equally and leaves its class mix/capacity unchanged.
        trial = l2_offered_load_lp({"pD": p_d, "pFA": exact}, pi,
                                   lambda_l1 / MU_L1, n_l2)
        if abs(float(trial["rho_L2_min_max_analyst_utilization"]) - rho_max) > 1e-7:
            raise AssertionError("fixed-mix pFA formula failed heterogeneous-LP boundary check")
        state = "closed_form_checked_against_heterogeneous_LP"
    return {"rho_max": rho_max, "mu_L2_effective_per_h_at_mix": mu,
            "pFA_max_fixed_mix_formula_raw": homogeneous_formula_raw,
            "pFA_max_fixed_mix_formula_clipped": min(1.0, max(0.0, homogeneous_formula_raw)),
            "pFA_max_heterogeneous_LP": exact, "boundary_state": state,
            "formula_LP_abs_difference": (abs(exact-homogeneous_formula_raw)
                if exact is not None else None)}


def percentile(values: np.ndarray) -> tuple[float, float]:
    return float(np.quantile(values, .025)), float(np.quantile(values, .975))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    episodes = read_csv(ROOT / ANALYSIS_CONFIG["episode_input"])
    inventory = read_csv(ROOT / ANALYSIS_CONFIG["classifier_inventory_input"])
    campaign_config = json.loads((ROOT / "studies/soc_triage_classifier_frontier_campaign/config/campaign.json").read_text())
    points = {row["id"]: row for row in inventory}
    if len(episodes) != 18720 or len(points) != 72:
        raise AssertionError("unexpected source row count or classifier inventory size")

    keyed: dict[tuple, dict[str, dict[int, dict]]] = defaultdict(lambda: defaultdict(dict))
    all_trace_needs = defaultdict(dict)
    for row in episodes:
        key = (row["label_definition"], row["prevalence_scenario"], row["classifier_id"],
               float(row["rho_L1"]), int(row["n_L2"]))
        policy, seed = row["policy"], int(row["seed"])
        if policy not in POLICIES or seed in keyed[key][policy]:
            raise AssertionError(f"duplicate/unexpected episode key: {key}, {policy}, {seed}")
        num = reconstruct_timely_numerator(row)
        row["_timely_need_numerator"] = num
        keyed[key][policy][seed] = row
        need_key = (row["label_definition"], row["prevalence_scenario"], float(row["rho_L1"]), seed)
        all_trace_needs[need_key][(row["classifier_id"], int(row["n_L2"]), policy)] = (
            int(row["true_need_count"]), int(row["admitted"]))

    # Denominators and number of admitted alerts must be shared across all
    # classifiers, rosters, and policies on the same prevalence/load/seed.
    for need_key, records in all_trace_needs.items():
        if len(set(records.values())) != 1:
            raise AssertionError(f"need/admission denominators differ on paired trace {need_key}")
    trace_keys=defaultdict(set)
    exog_keys=defaultdict(set)
    for row in episodes:
        run_key=(row["label_definition"],row["prevalence_scenario"],row["classifier_id"],
                 float(row["rho_L1"]),int(row["n_L2"]),int(row["seed"]))
        trace_keys[run_key].add((row["exogenous_sha256"],row["trace_sha256"]))
        exog_key=(row["label_definition"],row["prevalence_scenario"],float(row["rho_L1"]),int(row["seed"]))
        exog_keys[exog_key].add(row["exogenous_sha256"])
        if int(row["TP"])+int(row["FP"])+int(row["FN"])+int(row["TN"])!=int(row["admitted"]):
            raise AssertionError("triage confusion counts do not sum to admissions")
        if float(row["max_deadline_h"]) > float(row["terminal_cutoff_h"]):
            raise AssertionError("terminal cut truncates a deadline")
    if any(len(v)!=1 for v in trace_keys.values()) or any(len(v)!=1 for v in exog_keys.values()):
        raise AssertionError("paired policies/classifiers do not share exogenous or recommendation traces")
    seeds = sorted({int(row["seed"]) for row in episodes})
    if len(seeds) != 40:
        raise AssertionError(f"expected 40 paired seed clusters, found {len(seeds)}")
    seed_ix = {seed: i for i, seed in enumerate(seeds)}
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draw_indices = rng.integers(0, len(seeds), size=(BOOTSTRAP_REPS, len(seeds)), dtype=np.int16)
    contrast_rows = []
    bootstrap_cache = {}
    point_rows = []
    zero_seed_total = 0
    for key, policy_data in sorted(keyed.items()):
        if any(set(policy_data[p]) != set(seeds) for p in POLICIES):
            raise AssertionError(f"incomplete seed/policy pairing for {key}")
        num_by_policy, den_by_policy = {}, {}
        for policy in POLICIES:
            rs = [policy_data[policy][seed] for seed in seeds]
            num_by_policy[policy] = np.array([int(r["_timely_need_numerator"]) for r in rs], dtype=np.int64)
            den_by_policy[policy] = np.array([int(r["true_need_count"]) for r in rs], dtype=np.int64)
        if any(not np.array_equal(den_by_policy[POLICIES[0]], den_by_policy[p]) for p in POLICIES[1:]):
            raise AssertionError(f"policy denominators are not identical for {key}")
        estimates, contrasts, zero_reps = paired_bootstrap_splus(num_by_policy, den_by_policy, draw_indices)
        bootstrap_cache[key] = (estimates, contrasts, zero_reps)
        zero_seeds = int((den_by_policy[POLICIES[0]] == 0).sum())
        zero_seed_total += zero_seeds
        first = policy_data["D1"][seeds[0]]
        point = points[first["classifier_id"]]
        pi = float(first["pi"])
        rho_l1 = float(first["rho_L1"])
        n_l2 = int(first["n_L2"])
        cap = l2_offered_load_lp(point, pi, rho_l1, n_l2)
        for policy in POLICIES:
            rows = [policy_data[policy][seed] for seed in seeds]
            agg = aggregate_splus(rows)
            lo, hi = percentile(estimates[policy])
            point_rows.append({
                "label_definition": key[0], "prevalence_scenario": key[1], "pi": pi,
                "classifier_id": key[2], "algorithm": point["algorithm"], "features": point["features"],
                "cost_regime": point["cost_regime"], "pD_published": float(point["pD"]),
                "pFA_published": float(point["pFA"]), "BA_published": float(point["BA_published"]),
                "rho_L1": rho_l1, "n_L2": n_l2, "policy": policy,
                "seeds": len(seeds), "seeds_with_zero_needs": zero_seeds,
                **agg, "S_plus_bootstrap_ci95_low": lo, "S_plus_bootstrap_ci95_high": hi,
                "bootstrap_replicates": BOOTSTRAP_REPS,
                "bootstrap_zero_denominator_replicates": zero_reps,
                "bootstrap_valid_replicates": len(estimates[policy]),
                "G_definition": "timely_need_numerator / TP_count; undefined when TP_count=0",
                "rho_L2_offered_source_campaign": float(first["rho_L2_offered_analytic"]),
                **cap,
            })
        for label, values in contrasts.items():
            lo, hi = percentile(values)
            contrast_rows.append({"label_definition": key[0], "prevalence_scenario": key[1],
                "classifier_id": key[2], "rho_L1": rho_l1, "n_L2": n_l2,
                "contrast": label, "estimate": float(estimates["HLS-B"].mean()-estimates["D1"].mean())
                    if label == "WAPS-D1" else float(values.mean()),
                "paired_bootstrap_ci95_low": lo, "paired_bootstrap_ci95_high": hi,
                "n_seed_clusters": len(seeds), "bootstrap_replicates": BOOTSTRAP_REPS,
                "bootstrap_zero_denominator_replicates": zero_reps,
                "method": "paired seed-cluster percentile bootstrap; common resample indices for all policies/configurations"})

    # Recompute each policy contrast point estimate from the ratio of pooled counts.
    point_by_key_policy = {(r["label_definition"], r["prevalence_scenario"], r["classifier_id"],
                            r["rho_L1"], r["n_L2"], r["policy"]): r for r in point_rows}
    for row in contrast_rows:
        args = (row["label_definition"], row["prevalence_scenario"], row["classifier_id"],
                row["rho_L1"], row["n_L2"])
        a_name, b_name = {"WAPS-D1": ("HLS-B", "D1"), "P1-D1": ("P1", "D1"),
                          "WAPS-P1": ("HLS-B", "P1")}[row["contrast"]]
        a = point_by_key_policy[(*args, a_name)]["S_plus"]
        b = point_by_key_policy[(*args, b_name)]["S_plus"]
        row["estimate"] = a - b

    # Analytic demand/capacity table and heterogeneous LP-derived pFA boundaries.
    analytic_rows, boundary_rows = [], []
    seen_conditions = set()
    for row in point_rows:
        k = (row["label_definition"], row["prevalence_scenario"], row["classifier_id"],
             row["rho_L1"], row["n_L2"])
        if k in seen_conditions:
            continue
        seen_conditions.add(k)
        inv = points[row["classifier_id"]]
        pi = float(row["pi"])
        for rho_max in RHO_MAX_GRID:
            analytic_rows.append({**{x: row[x] for x in ("label_definition", "prevalence_scenario", "pi",
                "classifier_id", "algorithm", "features", "cost_regime", "pD_published", "pFA_published",
                "rho_L1", "n_L2")}, **{x: row[x] for x in (
                "lambda_L1_per_h", "q_expected", "lambda_L2_offered_per_h", "lambda_TP_per_h",
                "lambda_FP_per_h", "lambda_FN_per_h", "lambda_TN_per_h",
                "L2_necessary_recommended_work_h_per_h", "L2_unnecessary_FP_work_h_per_h",
                "L2_necessary_omitted_FN_work_h_per_h", "effective_capacity_L2_per_h",
                "rho_L2_min_max_analyst_utilization", "rho_L2_offered_over_existing_LP_capacity",
                "class_specific_l2_rates")}, "rho_max": rho_max,
                "capacity_feasible": row["rho_L2_min_max_analyst_utilization"] <= rho_max + 1e-12,
                "demand_absolute_kept_fixed_across_L2_rosters": True})
            boundary = pfa_capacity_boundary(pi, float(inv["pD"]),
                float(row["lambda_L1_per_h"]), int(row["n_L2"]), rho_max)
            boundary_rows.append({**{x: row[x] for x in ("label_definition", "prevalence_scenario", "pi",
                "classifier_id", "rho_L1", "n_L2", "pD_published")}, **boundary})

    # Full threshold grid: point status and 95%-supported status are separate.
    pidx = {(r["label_definition"], r["prevalence_scenario"], r["classifier_id"],
             r["rho_L1"], r["n_L2"], r["policy"]): r for r in point_rows}
    cap_by_condition = {}
    for r in point_rows:
        cap_by_condition[(r["label_definition"], r["prevalence_scenario"], r["classifier_id"],
                          r["rho_L1"], r["n_L2"])] = r
    feasibility = []
    for k, r in pidx.items():
        label, prevalence, classifier_id, rho_l1, n_l2, policy = k
        d_ok_value = float(r["pD_published"])
        rho_value = float(r["rho_L2_min_max_analyst_utilization"])
        for d_min in D_MIN_GRID:
            for rho_max in RHO_MAX_GRID:
                for s_min in S_MIN_GRID:
                    estimate = float(r["S_plus"])
                    lo, hi = float(r["S_plus_bootstrap_ci95_low"]), float(r["S_plus_bootstrap_ci95_high"])
                    feasibility.append({"label_definition": label, "prevalence_scenario": prevalence,
                        "classifier_id": classifier_id, "rho_L1": rho_l1, "n_L2": n_l2,
                        "policy": policy, "d_min": d_min, "rho_max": rho_max, "s_min": s_min,
                        "pD_published": d_ok_value, "rho_L2_offered_LP": rho_value,
                        "S_plus_pooled": estimate, "S_plus_ci95_low": lo, "S_plus_ci95_high": hi,
                        "timely_need_numerator": int(r["timely_need_numerator"]),
                        "total_need_denominator": int(r["total_need_denominator"]),
                        "TP_denominator": int(r["TP_denominator"]), "FN_count": int(r["FN_count"]),
                        "pD_empirical_pooled": float(r["pD_empirical_pooled"]),
                        "G_timely_given_TP": float(r["G_timely_given_TP"]),
                        "seeds_with_zero_needs": int(r["seeds_with_zero_needs"]),
                        "bootstrap_zero_denominator_replicates": int(r["bootstrap_zero_denominator_replicates"]),
                        "bootstrap_valid_replicates": int(r["bootstrap_valid_replicates"]),
                        "detection_ok": d_ok_value >= d_min,
                        "capacity_ok": rho_value <= rho_max + 1e-12,
                        "point_admissible": point_admissible(d_ok_value, rho_value, estimate, d_min, rho_max, s_min),
                        "supported_admissible_95": supported_admissible(d_ok_value, rho_value, lo, d_min, rho_max, s_min),
                        "status": status_for(d_ok_value >= d_min, rho_value <= rho_max+1e-12,
                                             estimate, lo, hi, s_min)})

    # Case-specific thresholds required by the request.
    priority = ANALYSIS_CONFIG["priority_case"]
    case_rows = [r for r in feasibility if r["label_definition"] == "standardized"
        and r["classifier_id"] == priority["classifier_id"]
        and r["prevalence_scenario"] == priority["prevalence_scenario"]
        and r["rho_L1"] == priority["rho_L1"] and r["n_L2"] == priority["n_L2"]
        and r["d_min"] == priority["d_min"] and r["rho_max"] == priority["rho_max"]
        and r["s_min"] == priority["s_min"]]

    prevalence_sensitivity_rows = build_prevalence_sensitivity(keyed, draw_indices)
    write_csv(OUT / "splus_estimates.csv", point_rows)
    write_csv(OUT / "splus_paired_contrasts.csv", contrast_rows)
    write_csv(OUT / "prevalence_sensitivity_splus.csv", prevalence_sensitivity_rows)
    write_csv(OUT / "analytic_capacity_load.csv", analytic_rows)
    write_csv(OUT / "heterogeneous_pfa_capacity_boundaries.csv", boundary_rows)
    write_csv(OUT / "feasibility_grid.csv", feasibility)
    write_csv(OUT / "priority_case_status.csv", case_rows)

    checks = make_checks(episodes, keyed, point_rows, contrast_rows, feasibility, campaign_config)
    (OUT / "validation_checks.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    create_figures(point_rows, feasibility)
    write_manifest()
    print(json.dumps({"status": checks["status"], "episodes_read": len(episodes),
        "condition_policy_estimates": len(point_rows), "paired_policy_contrasts": len(contrast_rows),
        "analytic_capacity_rows": len(analytic_rows), "feasibility_rows": len(feasibility),
        "zero_need_seed_cells": checks["zero_need_seed_cells"],
        "priority_case": case_rows}, indent=2))


def make_checks(episodes, keyed, point_rows, contrast_rows, feasibility, campaign_config):
    violations = []
    row_bounds = 0
    empirical_over_published = []
    empirical_over_published_ci_contains = 0
    empirical_over_published_ci_lower = 0
    for row in episodes:
        denominator = int(row["true_need_count"])
        timely = int(row["_timely_need_numerator"])
        tp = int(row["TP_count"])
        row_bounds += int(timely <= tp)
    for row in point_rows:
        if row["S_plus"] > row["pD_empirical_pooled"] + 1e-12:
            violations.append("S_plus exceeds pooled empirical pD")
        if row["S_plus"] > row["pD_published"]:
            empirical_over_published.append((row["label_definition"], row["classifier_id"], row["policy"],
                                             row["rho_L1"], row["n_L2"]))
            empirical_over_published_ci_contains += int(
                float(row["S_plus_bootstrap_ci95_low"]) <= float(row["pD_published"]) <=
                float(row["S_plus_bootstrap_ci95_high"]))
            empirical_over_published_ci_lower += int(
                float(row["S_plus_bootstrap_ci95_low"]) > float(row["pD_published"]))
    grid_lookup = {(r["label_definition"],r["prevalence_scenario"],r["classifier_id"],r["rho_L1"],r["n_L2"],r["policy"],r["d_min"],r["rho_max"],r["s_min"]):r["point_admissible"] for r in feasibility}
    monotonicity_violations = []
    ds, cs, ss = sorted(D_MIN_GRID), sorted(RHO_MAX_GRID), sorted(S_MIN_GRID)
    for key, value in grid_lookup.items():
        label, prev, classifier, rho, n2, policy, d, c, s = key
        tighter_keys=[]
        if d in ds and ds.index(d)+1 < len(ds): tighter_keys.append((ds[ds.index(d)+1],c,s))
        if c in cs and cs.index(c)>0: tighter_keys.append((d,cs[cs.index(c)-1],s))
        if s in ss and ss.index(s)+1 < len(ss): tighter_keys.append((d,c,ss[ss.index(s)+1]))
        for nd,nc,ns in tighter_keys:
            tighter_value=grid_lookup[(label,prev,classifier,rho,n2,policy,nd,nc,ns)]
            if tighter_value and not value:
                monotonicity_violations.append((key,(nd,nc,ns)))
    if row_bounds != len(episodes): violations.append("finite-sample S_plus <= realized pD check failed")
    if monotonicity_violations: violations.append("tightening requirements enlarged admissible set")
    unique_need_by_seed={}
    for row in episodes:
        unique_need_by_seed[(row["label_definition"],row["prevalence_scenario"],float(row["rho_L1"]),int(row["seed"]))] = int(row["true_need_count"])
    denom_zero_seed_cells = sum(value==0 for value in unique_need_by_seed.values())
    capacity_differences=[]
    capacity_by_prevalence=defaultdict(list)
    capacity_crossings=defaultdict(int)
    for key, policy_data in keyed.items():
        source_row=policy_data["D1"][min(policy_data["D1"])]
        point=next(r for r in point_rows if r["label_definition"]==key[0]
          and r["prevalence_scenario"]==key[1] and r["classifier_id"]==key[2]
          and r["rho_L1"]==key[3] and r["n_L2"]==key[4] and r["policy"]=="D1")
        source_rho=float(source_row["rho_L2_offered_analytic"])
        derived_rho=float(point["rho_L2_min_max_analyst_utilization"])
        capacity_differences.append(abs(source_rho-derived_rho))
        capacity_by_prevalence[key[1]].append(source_rho-derived_rho)
        for threshold in RHO_MAX_GRID:
            capacity_crossings[(key[1],threshold)] += int((source_rho<=threshold)!=(derived_rho<=threshold))
    checks = {"status":"PASS" if not violations else "FAIL", "failures":violations,
        "episodes_read":len(episodes), "seed_count":40, "bootstrap_replicates":BOOTSTRAP_REPS,
        "bootstrap_seed":BOOTSTRAP_SEED, "seed_cluster_ids":sorted({int(r["seed"]) for r in episodes}),
        "numerator_reconstruction":"necessary_L2_timely_per_need × true_need_count, checked integer to 1e-9; numerator <= TP_count",
        "need_denominator":"true_need_count; TP_count+FN_count checked for every episode",
        "policy_denominator_pairing":"exact per seed across D1/P1/HLS-B and all classifier/roster alternatives",
        "finite_sample_Splus_le_empirical_pD_rows_checked":row_bounds,
        "Splus_point_estimates_above_published_pD_count":len(empirical_over_published),
        "Splus_above_published_pD_cells":empirical_over_published,
        "Splus_above_published_pD_ci_contains_target_count":empirical_over_published_ci_contains,
        "Splus_above_published_pD_ci_lower_above_target_count":empirical_over_published_ci_lower,
        "unique_need_prevalence_load_seed_cells":len(unique_need_by_seed),
        "capacity_LP_source_metric_max_abs_difference":max(capacity_differences),
        "capacity_LP_condition_comparisons":len(capacity_differences),
        "capacity_LP_source_metric_differences_by_prevalence":{
          prev:{"n":len(vals),"max_abs":max(abs(x) for x in vals),"mean_signed":sum(vals)/len(vals)}
          for prev,vals in capacity_by_prevalence.items()},
        "capacity_feasibility_threshold_classification_crossings":{
          f"{prev}|rho_max={threshold}":count for (prev,threshold),count in capacity_crossings.items()},
        "zero_need_seed_cells":denom_zero_seed_cells,
        "zero_denominator_bootstrap_replicates":"excluded from ratio quantiles and counted per condition; all point denominators positive",
        "monotonicity_violations":len(monotonicity_violations),
        "demand_scenarios_preserved":sorted({float(r["rho_L1"]) for r in episodes}),
        "l2_rosters":sorted({int(r["n_L2"]) for r in episodes}),
        "policy_set":list(POLICIES), "simulation_executed":False,
        "source_campaign_commit":campaign_config["phase2_source_commit"],
        "campaign_trace_hash_checks":"inherited from source campaign validation_checks.json"}
    return checks


def build_prevalence_sensitivity(keyed, draw_indices):
    """Paired 39-vs-40 prevalence sensitivity, with scenario-specific denominators."""
    out=[]
    for key in sorted(k for k in keyed if k[0]=="original" and k[1]=="original_audited_39_of_14449"):
        label, _, classifier, rho, n_l2 = key
        key40=(label,"original_pdf_ir_implied_40_of_14449",classifier,rho,n_l2)
        if key40 not in keyed:
            continue
        for policy in POLICIES:
            rows39=keyed[key][policy]
            rows40=keyed[key40][policy]
            seeds=sorted(rows39)
            if seeds!=sorted(rows40):
                raise AssertionError("prevalence scenarios lost seed pairing")
            n39=np.array([int(rows39[s]["_timely_need_numerator"]) for s in seeds],dtype=np.int64)
            d39=np.array([int(rows39[s]["true_need_count"]) for s in seeds],dtype=np.int64)
            n40=np.array([int(rows40[s]["_timely_need_numerator"]) for s in seeds],dtype=np.int64)
            d40=np.array([int(rows40[s]["true_need_count"]) for s in seeds],dtype=np.int64)
            bd39=d39[draw_indices].sum(axis=1)
            bd40=d40[draw_indices].sum(axis=1)
            valid=(bd39>0)&(bd40>0)
            differences=(n40[draw_indices].sum(axis=1)[valid]/bd40[valid]-
                         n39[draw_indices].sum(axis=1)[valid]/bd39[valid])
            estimate39=n39.sum()/d39.sum() if d39.sum() else math.nan
            estimate40=n40.sum()/d40.sum() if d40.sum() else math.nan
            lo,hi=percentile(differences)
            out.append({"classifier_id":classifier,"rho_L1":rho,"n_L2":n_l2,"policy":policy,
                "contrast":"pi 40/14449 minus pi 39/14449","S_plus_pi39":estimate39,
                "S_plus_pi40":estimate40,"difference_pi40_minus_pi39":estimate40-estimate39,
                "paired_bootstrap_ci95_low":lo,"paired_bootstrap_ci95_high":hi,
                "n_seed_clusters":len(seeds),"bootstrap_replicates":len(draw_indices),
                "zero_denominator_replicates_excluded":int((~valid).sum()),
                "method":"same seed-cluster draws across prevalence scenarios; ratio-of-counts difference"})
    return out


def create_figures(point_rows, feasibility):
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/soc_triage_feasibility_mplcache")
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # Required threshold case: show all policies and L2 roster sizes by classifier point.
    selected = [r for r in feasibility if r["label_definition"] == "standardized"
        and r["prevalence_scenario"] == "standardized_pdf_ir_implied_19_of_14449"
        and r["rho_L1"] == 1.25 and r["d_min"] == .8 and r["rho_max"] == .8 and r["s_min"] == .7]
    ids = sorted({r["classifier_id"] for r in selected})
    fig, ax = plt.subplots(figsize=(12, 6))
    palette = {"D1":"#5577aa", "P1":"#dd8844", "HLS-B":"#448866"}
    markers = {2:"o",3:"s",4:"^"}
    for r in selected:
        y = ids.index(r["classifier_id"])
        color=palette[r["policy"]]
        if r["status"] == "admissible_supported_95": face=color
        elif r["status"] == "point_admissible_uncertain": face="white"
        else: face="#cccccc"
        ax.scatter([int(r["n_L2"])],[y],marker=markers[int(r["n_L2"])],s=65,
                   facecolors=face,edgecolors=color,linewidths=1.5)
    ax.set_yticks(range(len(ids)),[x.replace("standardized_","") for x in ids])
    ax.set_xticks([2,3,4]);ax.set_xlabel("Número de analistas L2 (rho_max = 0.80)")
    ax.set_title("Admisibilidad del caso d_min=0.80, s_min=0.70 · etiquetas estandarizadas · rhoL1=1.25")
    ax.grid(axis="x",alpha=.25)
    handles=[plt.Line2D([0],[0],marker="o",color="w",markerfacecolor=palette[p],label=p,markeredgecolor=palette[p]) for p in POLICIES]
    handles += [plt.Line2D([0],[0],marker="o",color="#555",markerfacecolor="white",label="Puntual admisible, IC cruza umbral"),
                plt.Line2D([0],[0],marker="o",color="#555",markerfacecolor="#ccc",label="No admisible / no apoyado")]
    ax.legend(handles=handles,loc="lower right",fontsize=8)
    fig.tight_layout();fig.savefig(OUT/"priority_case_feasibility.png",dpi=180);plt.close(fig)

    # S_plus curves for the priority classifier; values are pooled ratios with seed bootstrap intervals.
    priority = [r for r in point_rows if r["label_definition"]=="standardized"
        and r["classifier_id"]=="standardized_lightgbm_apc_symmetric"
        and r["prevalence_scenario"]=="standardized_pdf_ir_implied_19_of_14449"
        and r["rho_L1"]==1.25]
    fig, axs=plt.subplots(1,3,figsize=(12,4),sharey=True)
    for ax,n_l2 in zip(axs,(2,3,4)):
        for policy in POLICIES:
            r=next(x for x in priority if x["n_L2"]==n_l2 and x["policy"]==policy)
            ax.errorbar([policy],[r["S_plus"]],yerr=[[r["S_plus"]-r["S_plus_bootstrap_ci95_low"]],
                [r["S_plus_bootstrap_ci95_high"]-r["S_plus"]]],fmt="o",capsize=3,label=policy)
        ax.axhline(.7,color="#a44",linestyle="--",linewidth=1,label="s_min=0.70" if n_l2==2 else None)
        ax.set_title(f"{n_l2} analistas L2");ax.set_ylim(0,1);ax.grid(axis="y",alpha=.2)
        ax.set_xlabel("Política")
    axs[0].set_ylabel("S+ agrupado (IC95% bootstrap por semilla)")
    axs[-1].legend(fontsize=8,loc="lower right")
    fig.tight_layout();fig.savefig(OUT/"priority_case_splus_by_policy.png",dpi=180);plt.close(fig)

    # Mean S+ map under the .80/.80 capacity cut; cells encode policy-specific service feasibility.
    rows=[r for r in feasibility if r["d_min"]==.8 and r["rho_max"]==.8 and r["s_min"]==.7]
    groups=defaultdict(list)
    for r in rows:
        groups[(r["label_definition"],r["prevalence_scenario"],r["rho_L1"],r["n_L2"],r["policy"])].append(r)
    maps=[]
    for (label,prev,rho,n2,policy),rs in groups.items():
        counts=defaultdict(int)
        for r in rs:counts[r["status"]]+=1
        maps.append({"label_definition":label,"prevalence_scenario":prev,"rho_L1":rho,"n_L2":n2,"policy":policy,
          "classifier_count":len(rs),"admissible_supported_95":counts["admissible_supported_95"],
          "point_admissible_uncertain":counts["point_admissible_uncertain"],
          "indeterminate_service":counts["indeterminate_service"],
          "service_upper95_below":counts["inadmissible_service_upper95_below"],
          "detection_or_capacity_inadmissible":counts["inadmissible_detection"]+counts["inadmissible_capacity"]})
    write_csv(OUT/"threshold_080_summary.csv",maps)


def write_manifest():
    def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
    inputs=[ANALYSIS_CONFIG_PATH, ROOT / ANALYSIS_CONFIG["episode_input"], CAMPAIGN/"reproducibility_manifest.json",
            ROOT / ANALYSIS_CONFIG["classifier_inventory_input"],
            ROOT/"studies/soc_triage_classifier_frontier_campaign/config/campaign.json", ANALYSIS_CONFIG_PATH]
    outputs=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!="reproducibility_manifest.json")
    manifest={"created_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "analysis_only_no_simulations":True,"bootstrap_replicates":BOOTSTRAP_REPS,
      "bootstrap_seed":BOOTSTRAP_SEED,"input_sha256":{str(p.relative_to(ROOT)):digest(p) for p in inputs},
      "output_sha256":{p.name:digest(p) for p in outputs}}
    (OUT/"reproducibility_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
