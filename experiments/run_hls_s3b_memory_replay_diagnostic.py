#!/usr/bin/env python3
"""Final S3b diagnostic: isolate memory under shared and closed-loop feedback.

FULL and WINDOW are empirical-mean diagnostics, not UCB1/SW-UCB replicas.
The only estimator difference is global versus W-period observation retention.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import statistics
import struct
import subprocess
import time
from array import array
from dataclasses import asdict
from pathlib import Path
from typing import Any

from scipy.stats import t as student_t

from experiments.run_hls_s3b_change_observation_factorial import (
    BASE, CALIBRATION, CALIBRATION_PERMUTATIONS, HORIZON, K, MATCHINGS, N,
    OBSERVATION_PROBABILITIES, PAIRS, TRANSIENT, WINDOW, generate_randomness,
    matrix_at, calibration_matching, change_times, opportunity_mask,
)
from hls.nonstationary_assignment import PairwiseBanditEstimator
from hls.experiment_contract import (
    ExperimentEvent, ExperimentRun, MetricValue, SeedRecord, UnitDeclaration,
)
from hls.performance_evaluation import (
    EvaluationProfile, EvaluationRecord, PerformanceEvaluator, Status,
)


OUT_DIR = Path("results/experiments/hls_s3b_memory_replay_diagnostic")
RESULT_PATH = OUT_DIR / "results.json"
SEEDS = tuple(range(9000, 9030))
# A 3-cell L design gives a one-factor contrast at each fixed reference:
# infrequent/high vs frequent/high varies tau; frequent/high vs frequent/low
# varies opportunity probability. It deliberately does not estimate A×B.
CONDITIONS = (
    {"id": "infrequent_high", "label": "infrequent/high", "interval": 2_500, "p": .75},
    {"id": "frequent_high", "label": "frequent/high", "interval": 500, "p": .75},
    {"id": "frequent_low", "label": "frequent/low", "interval": 500, "p": .25},
)
CONTROLS = ("shared_observations", "closed_loop")
ESTIMATORS = {"FULL": "global_mean", "WINDOW": "recent_mean"}
POLICY_IDS = {"FULL": "FULL_DIAGNOSTIC", "WINDOW": "WINDOW_DIAGNOSTIC"}
MATCHING_CATALOG = tuple(sorted(MATCHINGS))
PERIOD_METRICS = (
    "expected_reward", "expected_regret", "mse_global", "mse_optimal_edges",
    "mse_selected_edges", "optimal_matching", "real_optimal_margin",
    "estimated_order_gap",
)


def choose_matching(values, catalog= MATCHING_CATALOG):
    """Maximize estimated mean reward; ties use a catalog-order-free key."""
    candidates = tuple(sorted(tuple(tuple(edge) for edge in matching) for matching in catalog))
    scored = [(sum(float(values[i][k]) for i, k in matching), matching)
              for matching in candidates]
    best = max(value for value, _ in scored)
    return min(matching for value, matching in scored
               if math.isclose(value, best, rel_tol=0.0, abs_tol=1e-12))


def oracle_matching(values):
    return choose_matching(values, MATCHING_CATALOG)


def _matching_value(values, matching):
    return sum(float(values[i][k]) for i, k in matching)


def _digest_observations(rows):
    digest = hashlib.sha256()
    for period, i, k, reward in rows:
        digest.update(struct.pack("<iiiB", int(period), int(i), int(k), int(reward)))
    return digest.hexdigest()


def _digest_matrix_path(interval):
    digest = hashlib.sha256()
    for period in range(HORIZON):
        for row in matrix_at(period, interval):
            for value in row:
                digest.update(struct.pack("<d", float(value)))
    return digest.hexdigest()


def _seed_streams(seed):
    return {
        "potential_outcomes": int(seed) ^ 0xA17E5B,
        "observation_opportunities": int(seed) ^ 0x0B5E7A,
        "competence_path": None,
        "policy_randomness": None,
    }


def _calendar_matching(period):
    if period < CALIBRATION:
        return calibration_matching(period)
    return MATCHING_CATALOG[(period - CALIBRATION) % len(MATCHING_CATALOG)]


def run_episode(seed: int, condition: dict, control: str, estimator_name: str,
                reward_uniforms, opportunity_uniforms) -> dict[str, Any]:
    if control not in CONTROLS or estimator_name not in ESTIMATORS:
        raise ValueError("unknown diagnostic arm")
    interval, p = condition["interval"], condition["p"]
    estimator = PairwiseBanditEstimator(
        N, K, method=ESTIMATORS[estimator_name], window=WINDOW, xi=1.0,
    )
    obs_counts = {pair: 0 for pair in PAIRS}
    opportunity_mask_open = {pair: 0 for pair in PAIRS}
    scheduled_counts = {pair: 0 for pair in PAIRS}
    used_count_sum = {pair: 0 for pair in PAIRS}
    age_sum = {pair: 0.0 for pair in PAIRS}
    age_count = {pair: 0 for pair in PAIRS}
    last_observed = {pair: None for pair in PAIRS}
    pair_mse_sum = {pair: 0.0 for pair in PAIRS}
    pair_decision_error_sum = {pair: 0.0 for pair in PAIRS}
    pair_decision_error_n = {pair: 0 for pair in PAIRS}
    observed_events: list[tuple[int, int, int, int]] = []
    time_metrics: dict[str, list[float]] = {name: [] for name in PERIOD_METRICS}
    selected_ids = []
    examples = []
    change_set = set(change_times(interval))
    action_mismatches = 0
    total_regret = total_reward = 0.0
    optimal_count = assignment_error_edges = 0
    mse_global_total = mse_optimal_total = mse_selected_total = 0.0
    mse_decisive_total = 0.0
    mse_decisive_period_count = 0
    margin_by_regime: dict[str, dict[str, float]] = {
        "base": {"regret": 0.0, "mse": 0.0, "n": 0},
        "transient": {"regret": 0.0, "mse": 0.0, "n": 0},
    }
    margin_strata = {"0.05": {"regret": 0.0, "mse": 0.0, "n": 0, "optimal": 0},
                     "0.45": {"regret": 0.0, "mse": 0.0, "n": 0, "optimal": 0}}
    mse_optimal_sum = mse_suboptimal_sum = 0.0
    n_optimal = n_suboptimal = 0
    for period in range(HORIZON):
        matrix = matrix_at(period, interval)
        regime = "base" if matrix == BASE else "transient"
        estimate = estimator.empirical_mean_matrix(period)
        if period < CALIBRATION:
            selected = calibration_matching(period)
        else:
            selected = choose_matching(estimate)
        selected_ids.append(selected)
        estimator_diagnostics = estimator.diagnostic_matrix(period)
        oracle = oracle_matching(matrix)
        expected_reward = _matching_value(matrix, selected)
        oracle_reward = _matching_value(matrix, oracle)
        regret = oracle_reward - expected_reward
        if regret < -1e-10:
            raise AssertionError("selected matching exceeded the feasible oracle")
        regret = max(0.0, regret)
        is_optimal = selected == oracle
        if not is_optimal:
            action_mismatches += 1
            assignment_error_edges += len(set(selected) - set(oracle))

        error_sq = {(i, k): (float(estimate[i][k]) - float(matrix[i][k])) ** 2
                    for i, k in PAIRS}
        mse_global = statistics.fmean(error_sq.values())
        mse_opt = statistics.fmean(error_sq[pair] for pair in oracle)
        mse_sel = statistics.fmean(error_sq[pair] for pair in selected)
        best_values = sorted((_matching_value(matrix, matching) for matching in MATCHING_CATALOG),
                             reverse=True)
        margin = best_values[0] - best_values[1]
        est_choice_value = _matching_value(estimate, selected)
        est_oracle_value = _matching_value(estimate, oracle)
        estimated_order_gap = est_choice_value - est_oracle_value
        if period >= CALIBRATION and estimated_order_gap < -1e-10:
            raise AssertionError("decision rule selected below its estimated optimum")
        signed_pair_bias = sum(estimate[i][k] - matrix[i][k] for i,k in set(selected)-set(oracle))
        signed_pair_bias -= sum(estimate[i][k] - matrix[i][k] for i,k in set(oracle)-set(selected))
        if not math.isclose(estimated_order_gap, signed_pair_bias - regret,
                            rel_tol=0.0, abs_tol=1e-10):
            raise AssertionError("pairwise decision-error decomposition did not reconcile")
        if not is_optimal:
            decisive = (set(selected) ^ set(oracle))
            mse_decisive_total += statistics.fmean(error_sq[pair] for pair in decisive)
            mse_decisive_period_count += 1
            # Signed error contribution to selected-vs-oracle estimated order.
            for pair in set(selected) - set(oracle):
                pair_decision_error_sum[pair] += estimate[pair[0]][pair[1]] - matrix[pair[0]][pair[1]]
                pair_decision_error_n[pair] += 1
            for pair in set(oracle) - set(selected):
                pair_decision_error_sum[pair] -= estimate[pair[0]][pair[1]] - matrix[pair[0]][pair[1]]
                pair_decision_error_n[pair] += 1
            if (len(examples) < 12 and period >= CALIBRATION
                    and (period in change_set or period == CALIBRATION)):
                examples.append({
                    "period": period, "regime": regime, "estimated_matching": selected,
                    "oracle_matching": oracle, "selected_expected_reward": expected_reward,
                    "oracle_expected_reward": oracle_reward, "regret": regret,
                    "mse_global": mse_global, "mse_oracle_edges": mse_opt,
                    "mse_symmetric_difference": statistics.fmean(error_sq[pair] for pair in decisive),
                    "real_optimal_margin": margin, "estimated_order_gap": estimated_order_gap,
                    "signed_pair_bias": signed_pair_bias,
                    "decisive_pair_errors": {
                        f"{i},{k}": float(estimate[i][k] - matrix[i][k])
                        for i, k in sorted(decisive)
                    },
                })

        total_regret += regret
        total_reward += expected_reward
        optimal_count += int(is_optimal)
        mse_global_total += mse_global
        mse_optimal_total += mse_opt
        mse_selected_total += mse_sel
        margin_by_regime[regime]["regret"] += regret
        margin_by_regime[regime]["mse"] += mse_global
        margin_by_regime[regime]["n"] += 1
        margin_key = min(margin_strata, key=lambda value: abs(float(value) - margin))
        margin_strata[margin_key]["regret"] += regret
        margin_strata[margin_key]["mse"] += mse_global
        margin_strata[margin_key]["n"] += 1
        margin_strata[margin_key]["optimal"] += int(is_optimal)
        if is_optimal:
            mse_optimal_sum += mse_global
            n_optimal += 1
        else:
            mse_suboptimal_sum += mse_global
            n_suboptimal += 1
        for pair in PAIRS:
            pair_mse_sum[pair] += error_sq[pair]
            used_count_sum[pair] += estimator_diagnostics[pair[0]][pair[1]]["observations_used"]
            if last_observed[pair] is not None:
                age_sum[pair] += period - last_observed[pair]
                age_count[pair] += 1
        time_metrics["expected_reward"].append(expected_reward)
        time_metrics["expected_regret"].append(regret)
        time_metrics["mse_global"].append(mse_global)
        time_metrics["mse_optimal_edges"].append(mse_opt)
        time_metrics["mse_selected_edges"].append(mse_sel)
        time_metrics["optimal_matching"].append(float(is_optimal))
        time_metrics["real_optimal_margin"].append(margin)
        time_metrics["estimated_order_gap"].append(estimated_order_gap)
        availability = opportunity_mask(opportunity_uniforms[period], p)
        for pair in PAIRS:
            if availability & (1 << (pair[0] * K + pair[1])):
                opportunity_mask_open[pair] += 1
        observed_matching = selected if control == "closed_loop" else _calendar_matching(period)
        feedback_edges = []
        feedback = {}
        for i, k in observed_matching:
            pair = (i, k)
            scheduled_counts[pair] += 1
            bit = 1 << (i * K + k)
            if availability & bit:
                reward = float(reward_uniforms[period][i][k] < matrix[i][k])
                obs_counts[pair] += 1
                last_observed[pair] = period
                observed_events.append((period, i, k, int(reward)))
                feedback_edges.append(pair)
                feedback[pair] = reward
        estimator.update(period, feedback_edges, feedback)

    # Paired regime summaries and deterministic recovery lag.
    recovery_lags = []
    oracle_ids = [oracle_matching(matrix_at(t, interval)) for t in range(HORIZON)]
    # Decisions are retained compactly by reconstructing the same deterministic
    # estimator replay in time_metrics' companion assignment series.
    # Store assignment choices during the loop via a second lightweight replay.
    # (The event examples above retain exact counterfactual decision evidence.)
    # Recovery is computed directly below from the recorded choices.
    boundaries = change_times(interval)
    for index, boundary in enumerate(boundaries):
        next_boundary = boundaries[index + 1] if index + 1 < len(boundaries) else HORIZON
        stop = min(next_boundary, boundary + 1_000)
        lag = None
        for start in range(boundary, stop - 19):
            if all(selected_ids[t] == oracle_ids[t] for t in range(start, start + 20)):
                lag = start - boundary
                break
        recovery_lags.append(lag)

    return {
        "seed": seed, "condition": condition["label"], "interval": interval,
        "opportunity_probability": p, "control": control, "estimator": estimator_name,
        "expected_reward": total_reward, "expected_regret": total_regret,
        "optimal_matching_rate": optimal_count / HORIZON,
        "assignment_error_edges_per_period": assignment_error_edges / HORIZON,
        "mse_global": mse_global_total / HORIZON,
        "mse_optimal_edges": mse_optimal_total / HORIZON,
        "mse_selected_edges": mse_selected_total / HORIZON,
        "mse_decisive_edges": mse_decisive_total / mse_decisive_period_count if mse_decisive_period_count else None,
        "decision_mismatch_periods": action_mismatches,
        "mse_when_matching_optimal": mse_optimal_sum / n_optimal if n_optimal else None,
        "mse_when_matching_suboptimal": mse_suboptimal_sum / n_suboptimal if n_suboptimal else None,
        "mse_optimal_period_count": n_optimal,
        "mse_suboptimal_period_count": n_suboptimal,
        "observations_per_pair": {f"{i},{k}": obs_counts[(i,k)] for i,k in PAIRS},
        "mask_open_count_per_pair": {f"{i},{k}": opportunity_mask_open[(i,k)] for i,k in PAIRS},
        "scheduled_or_executed_count_per_pair": {f"{i},{k}": scheduled_counts[(i,k)] for i,k in PAIRS},
        "mean_observations_used_at_decision_per_pair": {
            f"{i},{k}": used_count_sum[(i,k)] / HORIZON for i,k in PAIRS},
        "last_observation_age_per_pair": {
            f"{i},{k}": (HORIZON - 1 - last_observed[(i,k)]) if last_observed[(i,k)] is not None else None
            for i,k in PAIRS},
        "mean_age_when_observed_before_decision_per_pair": {
            f"{i},{k}": age_sum[(i,k)] / age_count[(i,k)] if age_count[(i,k)] else None
            for i,k in PAIRS},
        "pair_mse": {f"{i},{k}": pair_mse_sum[(i,k)] / HORIZON for i,k in PAIRS},
        "pair_signed_decision_error_contribution": {
            f"{i},{k}": pair_decision_error_sum[(i,k)] / pair_decision_error_n[(i,k)]
            if pair_decision_error_n[(i,k)] else None for i,k in PAIRS},
        "regime_summary": {
            regime: {"mean_regret_per_period": vals["regret"] / vals["n"] if vals["n"] else None,
                     "mean_global_mse": vals["mse"] / vals["n"] if vals["n"] else None,
                     "periods": int(vals["n"])}
            for regime, vals in margin_by_regime.items()},
        "margin_strata": {
            margin_key: {"mean_regret_per_period": vals["regret"] / vals["n"] if vals["n"] else None,
                         "mean_global_mse": vals["mse"] / vals["n"] if vals["n"] else None,
                         "optimal_matching_rate": vals["optimal"] / vals["n"] if vals["n"] else None,
                         "periods": int(vals["n"])}
            for margin_key, vals in margin_strata.items()},
        "recovery_lags": recovery_lags,
        "first_decision_error_examples": examples,
        "wall_time_seconds": None,
        "observation_sequence_sha256": _digest_observations(observed_events),
        "competence_path_sha256": _digest_matrix_path(interval),
        "time_metrics": time_metrics,
    }


def _profile(condition, control):
    cid = f"s3b_memory_{condition['id']}_{control}_v1"
    return EvaluationProfile(
        profile_id=cid, scenario_id="S3b", configuration_id=cid,
        application_domain="synthetic_assignment_bandit",
        organizational_problem="B2_complete_one_to_one_matching_3x3",
        decision_objective={pid: "expected_reward_maximization" for pid in POLICY_IDS.values()},
        constraints="complete one-to-one 3x3 matching; six feasible matchings",
        primary_metrics=("original_reward_cumulative",),
        diagnostic_fields=("matching", "oracle", "expected_regret", "pair_estimates",
                           "pair_observation_counts", "observation_sequence_hash"),
        information_regime=(
            "same fixed exogenous matching calendar; counterfactual choices do not affect observations"
            if control == "shared_observations" else
            "feedback only on the estimator's own executed matching, when exogenous opportunity is present"
        ),
        temporal_horizon=HORIZON,
        aggregation_rules="sum expected matching reward over periods",
        demand_distribution_id=f"S3b_recurrent_tau{condition['interval']}_p{condition['p']}_v1",
    )


def _records(episode, profile):
    return tuple(EvaluationRecord(
        scenario_id=profile.scenario_id,
        configuration_id=profile.configuration_id,
        policy_id=POLICY_IDS[episode["estimator"]],
        period=t,
        demand="complete_three_task_matching",
        original_reward=float(value),
        provenance=f"diagnostic:{episode['seed']}:{episode['condition']}:{episode['control']}:{t}",
        information_regime=profile.information_regime,
        decision_objective="expected_reward_maximization",
        field_status={"output": Status.NOT_APPLICABLE, "requirements": Status.NOT_APPLICABLE,
                      "success": Status.NOT_APPLICABLE, "deficit": Status.NOT_APPLICABLE,
                      "resource_usage": Status.NOT_APPLICABLE},
    ) for t, value in enumerate(episode["time_metrics"]["expected_reward"]))


def _ci(values):
    values = tuple(float(v) for v in values)
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    half = student_t.ppf(.975, len(values)-1) * sd / math.sqrt(len(values)) if len(values) > 1 else 0.0
    return {"n_seeds": len(values), "mean": mean, "sd_between_seeds": sd,
            "ci95": [mean-half, mean+half]}


def _ci_available(values):
    values=tuple(value for value in values if value is not None)
    if not values:
        return {"n_seeds":0,"mean":None,"sd_between_seeds":None,"ci95":None,
                "status":"NOT_OBSERVABLE"}
    return {**_ci(values),"status":"VALID"}


def _paired_summary(rows, metric):
    by_key = {(r["condition"], r["control"], r["seed"], r["estimator"]): r for r in rows}
    result = {}
    for condition in (c["label"] for c in CONDITIONS):
        for control in CONTROLS:
            diffs = []
            for seed in SEEDS:
                full = by_key[(condition, control, seed, "FULL")]
                window = by_key[(condition, control, seed, "WINDOW")]
                a, b = full[metric], window[metric]
                if a is not None and b is not None:
                    diffs.append(float(b)-float(a))
            result[f"{condition}/{control}/WINDOW_minus_FULL/{metric}"] = _ci(diffs)
    return result


def run() -> dict[str, Any]:
    revision = subprocess.run(["git", "rev-parse", "HEAD"], check=True,
                              capture_output=True, text=True).stdout.strip()
    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    profiles = {(c["label"], control): _profile(c, control)
                for c in CONDITIONS for control in CONTROLS}
    evaluators = {}
    for key, profile in profiles.items():
        evaluator = PerformanceEvaluator()
        evaluator.register_profile(profile)
        evaluators[key] = evaluator
    episodes = []
    runs = {}
    pef_values = {}
    curve_sums = {
        (c["label"], control, estimator, metric): array("d", [0.0]) * HORIZON
        for c in CONDITIONS for control in CONTROLS
        for estimator in ESTIMATORS for metric in PERIOD_METRICS
    }
    paired_period_diagnostics = {f"{c['label']}/{control}": {
        "window_lower_mse_and_higher_regret_per_seed": [],
        "window_higher_mse_and_lower_regret_per_seed": [],
    } for c in CONDITIONS for control in CONTROLS}
    pair_error_sums = {f"{c['label']}/{control}/{estimator}": {f"{i},{k}": [] for i,k in PAIRS}
                       for c in CONDITIONS for control in CONTROLS for estimator in ESTIMATORS}
    for seed in SEEDS:
        reward_uniforms, opportunity_uniforms = generate_randomness(seed)
        for condition in CONDITIONS:
            condition_rows = {}
            for control in CONTROLS:
                for estimator_name in ESTIMATORS:
                    started = time.perf_counter()
                    row = run_episode(seed, condition, control, estimator_name,
                                      reward_uniforms, opportunity_uniforms)
                    row["wall_time_seconds"] = time.perf_counter() - started
                    condition_rows[(control, estimator_name)] = row
                    for metric in PERIOD_METRICS:
                        curve = curve_sums[(condition["label"], control, estimator_name, metric)]
                        for t, value in enumerate(row["time_metrics"][metric]):
                            curve[t] += float(value)
                    profile = profiles[(condition["label"], control)]
                    policy_id = POLICY_IDS[estimator_name]
                    records = _records(row, profile)
                    pef = evaluators[(condition["label"], control)].evaluate(
                        profile.profile_id, policy_id, records)["original_reward_cumulative"]
                    if not math.isclose(pef.value, row["expected_reward"], rel_tol=0.0, abs_tol=1e-8):
                        raise AssertionError("PEF reward did not reconcile with diagnostic rollout")
                    pef_values[(condition["label"], control, seed, estimator_name)] = pef.value
                    run_id = f"s3b-e1-memory-{condition['id']}-{control}-{estimator_name}-seed{seed}"
                    run_record = ExperimentRun(
                        schema_version="hls-experiment-run/1.0", run_id=run_id,
                        mechanism_id="empirical_pair_means_plus_exact_matching_diagnostic",
                        policy_id=policy_id,
                        configuration={"scenario":"S3b", "condition":condition,
                                       "control":control, "estimator":estimator_name,
                                       "window":WINDOW if estimator_name == "WINDOW" else None,
                                       "decision_rule":"maximize estimated mean over six matchings; lexicographic tie-break",
                                       "exploration_bonus":0.0, "calibration_periods":CALIBRATION},
                        initial_conditions={"competence_matrix":BASE},
                        random_seeds=(
                            SeedRecord("potential_outcomes", seed ^ 0xA17E5B,
                                       "common Bernoulli potential outcomes by period and pair"),
                            SeedRecord("observation_opportunities", seed ^ 0x0B5E7A,
                                       "common exogenous pair-period masks"),
                        ),
                        information_available={
                            "competences":"hidden from decision rule; evaluation only",
                            "shared_observations":"fixed calendar, common observations",
                            "closed_loop":"only selected pairs with available feedback",
                            "future_regime":"not visible to estimator"},
                        observation_model={"reward":"Bernoulli(c_ik(t))",
                                           "missing":"mask unavailable to policy until after matching",
                                           "control":control},
                        software_revision=None,
                        units=(UnitDeclaration("expected_reward","declared_reward","Expected matching value summed over periods."),
                               UnitDeclaration("expected_regret","declared_reward_gap","Feasible true-mean matching oracle minus selected matching."),
                               UnitDeclaration("mse","squared_probability_error","Squared competence probability error.")),
                        events=(ExperimentEvent(0,"diagnostic_episode_summary",run_id,
                                                {"observation_sequence_sha256":row["observation_sequence_sha256"],
                                                 "competence_path_sha256":row["competence_path_sha256"],
                                                 "horizon":HORIZON}),),
                        metrics=(MetricValue("original_reward_cumulative",row["expected_reward"],"declared_reward","Expected matching reward."),
                                 MetricValue("expected_regret_cumulative",row["expected_regret"],"declared_reward_gap","Regret against exact feasible matching oracle.","lower"),
                                 MetricValue("optimal_matching_rate",row["optimal_matching_rate"],"fraction","Fraction of optimal matchings."),
                                 MetricValue("mean_estimation_mse",row["mse_global"],"squared_probability_error","Mean squared error across pairs and periods.","lower"),
                                 MetricValue("episode_wall_time",row["wall_time_seconds"],"seconds","Wall time for one diagnostic simulation rollout.","lower")),
                        mechanism_results={k:v for k,v in row.items() if k != "time_metrics"},
                        metadata={"evaluation_profile_id":profile.profile_id,
                                  "diagnostic_only":True,"seed":seed,
                                  "base_git_revision":revision},
                    )
                    if ExperimentRun.from_json(run_record.to_json()).to_json() != run_record.to_json():
                        raise AssertionError("ExperimentRun JSON round-trip changed a record")
                    runs[run_id] = run_record.to_dict()
                    row.update({"run_id":run_id,"profile_id":profile.profile_id,
                                "pef_expected_reward":pef.value})
                    episodes.append({k:v for k,v in row.items() if k != "time_metrics"})
                full = condition_rows[(control,"FULL")]
                window = condition_rows[(control,"WINDOW")]
                if control == "shared_observations" and full["observation_sequence_sha256"] != window["observation_sequence_sha256"]:
                    raise AssertionError("shared-observation control histories differ")
                lower_mse_higher_regret = sum(
                    w_m < f_m and w_r > f_r
                    for f_m,w_m,f_r,w_r in zip(full["time_metrics"]["mse_global"],window["time_metrics"]["mse_global"],
                                               full["time_metrics"]["expected_regret"],window["time_metrics"]["expected_regret"])
                ) / HORIZON
                higher_mse_lower_regret = sum(
                    w_m > f_m and w_r < f_r
                    for f_m,w_m,f_r,w_r in zip(full["time_metrics"]["mse_global"],window["time_metrics"]["mse_global"],
                                               full["time_metrics"]["expected_regret"],window["time_metrics"]["expected_regret"])
                ) / HORIZON
                key=f"{condition['label']}/{control}"
                paired_period_diagnostics[key]["window_lower_mse_and_higher_regret_per_seed"].append(lower_mse_higher_regret)
                paired_period_diagnostics[key]["window_higher_mse_and_lower_regret_per_seed"].append(higher_mse_lower_regret)
                for estimator_name, estimator_row in (("FULL", full), ("WINDOW", window)):
                    pair_key_base=f"{condition['label']}/{control}/{estimator_name}"
                    for pair_key in pair_error_sums[pair_key_base]:
                        value=estimator_row["pair_signed_decision_error_contribution"][pair_key]
                        pair_error_sums[pair_key_base][pair_key].append(value if value is not None else 0.0)

    # Paired contrasts by seed; never treat time periods as independent units.
    paired = {}
    by_key = {(e["condition"],e["control"],e["seed"],e["estimator"]):e for e in episodes}
    arms = {}
    for condition in (c["label"] for c in CONDITIONS):
        for control in CONTROLS:
            for estimator_name in ESTIMATORS:
                samples=[by_key[(condition,control,seed,estimator_name)] for seed in SEEDS]
                arm_key=f"{condition}/{control}/{estimator_name}"
                arms[arm_key]={metric:_ci_available(row[metric] for row in samples)
                               for metric in ("expected_reward","expected_regret","optimal_matching_rate",
                                              "assignment_error_edges_per_period","mse_global",
                                              "mse_optimal_edges","mse_selected_edges","mse_decisive_edges",
                                              "decision_mismatch_periods","wall_time_seconds")}
                arms[arm_key]["observations_total"]=_ci(
                    sum(row["observations_per_pair"].values()) for row in samples)
                arms[arm_key]["mse_when_matching_optimal"]=_ci_available(
                    row["mse_when_matching_optimal"] for row in samples)
                arms[arm_key]["mse_when_matching_suboptimal"]=_ci_available(
                    row["mse_when_matching_suboptimal"] for row in samples)
                arms[arm_key]["regimes"]={regime:{
                    metric:_ci_available(row["regime_summary"][regime][metric] for row in samples)
                    for metric in ("mean_regret_per_period","mean_global_mse")
                } for regime in ("base","transient")}
                seed_recovery_means=[
                    statistics.fmean(lag for lag in row["recovery_lags"] if lag is not None)
                    for row in samples if any(lag is not None for lag in row["recovery_lags"])
                ]
                arms[arm_key]["recovery"]={
                    "mean_lag_by_seed":_ci_available(seed_recovery_means),
                    "unrecovered_change_events":sum(lag is None for row in samples for lag in row["recovery_lags"]),
                    "change_events":sum(len(row["recovery_lags"]) for row in samples),
                }
                arms[arm_key]["pairs"]={pair:{
                    "observations":_ci(row["observations_per_pair"][pair] for row in samples),
                    "scheduled_or_executed":_ci(row["scheduled_or_executed_count_per_pair"][pair] for row in samples),
                    "mask_open":_ci(row["mask_open_count_per_pair"][pair] for row in samples),
                    "mean_observations_used":_ci(row["mean_observations_used_at_decision_per_pair"][pair] for row in samples),
                    "last_observation_age":_ci_available(row["last_observation_age_per_pair"][pair]
                                                         for row in samples),
                    "mse":_ci(row["pair_mse"][pair] for row in samples),
                } for pair in (f"{i},{k}" for i,k in PAIRS)}
    scalar_metrics=("expected_reward","expected_regret","optimal_matching_rate",
                    "assignment_error_edges_per_period","mse_global","mse_optimal_edges",
                    "mse_selected_edges","mse_decisive_edges","decision_mismatch_periods",
                    "wall_time_seconds")
    for condition in (c["label"] for c in CONDITIONS):
        for control in CONTROLS:
            for metric in scalar_metrics:
                diffs=[]
                for seed in SEEDS:
                    a=by_key[(condition,control,seed,"FULL")][metric]
                    b=by_key[(condition,control,seed,"WINDOW")][metric]
                    if a is not None and b is not None:
                        diffs.append(float(b)-float(a))
                paired[f"{condition}/{control}/WINDOW_minus_FULL/{metric}"]=_ci_available(diffs)
            for i,k in PAIRS:
                pair_key=f"{i},{k}"
                paired[f"{condition}/{control}/WINDOW_minus_FULL/pair_mse/{pair_key}"]=_ci(
                    by_key[(condition,control,seed,"WINDOW")]["pair_mse"][pair_key]
                    - by_key[(condition,control,seed,"FULL")]["pair_mse"][pair_key]
                    for seed in SEEDS
                )
    pef_paired={}
    for condition in (c["label"] for c in CONDITIONS):
        for control in CONTROLS:
            diffs=[]
            for seed in SEEDS:
                direct=(by_key[(condition,control,seed,"WINDOW")]["expected_reward"]
                        -by_key[(condition,control,seed,"FULL")]["expected_reward"])
                pef=(pef_values[(condition,control,seed,"WINDOW")]
                     -pef_values[(condition,control,seed,"FULL")])
                if not math.isclose(direct,pef,rel_tol=0.0,abs_tol=1e-8):
                    raise AssertionError("PEF paired reward difference diverged from direct evaluation")
                diffs.append(pef)
            pef_paired[f"{condition}/{control}/WINDOW_minus_FULL/original_reward"]=_ci(diffs)
    memory_effect_across_conditions={}
    for control in CONTROLS:
        for metric in ("expected_regret","mse_global","optimal_matching_rate"):
            for first, second, label in (
                ("infrequent/high","frequent/high","frequent_high_minus_infrequent_high"),
                ("frequent/high","frequent/low","frequent_low_minus_frequent_high"),
            ):
                values=[]
                for seed in SEEDS:
                    effect_first=(by_key[(first,control,seed,"WINDOW")][metric]
                                  -by_key[(first,control,seed,"FULL")][metric])
                    effect_second=(by_key[(second,control,seed,"WINDOW")][metric]
                                   -by_key[(second,control,seed,"FULL")][metric])
                    values.append(float(effect_second)-float(effect_first))
                memory_effect_across_conditions[f"{control}/{label}/memory_effect_{metric}"]=_ci(values)
    cross_control={}
    for condition in (c["label"] for c in CONDITIONS):
        for estimator_name in ESTIMATORS:
            for metric in ("expected_regret","mse_global","observations_total","optimal_matching_rate"):
                diffs=[]
                for seed in SEEDS:
                    a=by_key[(condition,"shared_observations",seed,estimator_name)]
                    b=by_key[(condition,"closed_loop",seed,estimator_name)]
                    if metric == "observations_total":
                        av=sum(a["observations_per_pair"].values())
                        bv=sum(b["observations_per_pair"].values())
                    else:
                        av,bv=a[metric],b[metric]
                    diffs.append(float(bv)-float(av))
                cross_control[f"{condition}/{estimator_name}/closed_loop_minus_shared/{metric}"]=_ci(diffs)
    for key,vals in paired_period_diagnostics.items():
        for name, samples in vals.items():
            paired[f"{key}/{name}"]=_ci(samples)
    for key, pairs in pair_error_sums.items():
        for pair, samples in pairs.items():
            paired[f"{key}/mean_signed_decision_error_contribution/{pair}"]=_ci(samples)

    period_curves={}
    for condition in CONDITIONS:
        for control in CONTROLS:
            for estimator_name in ESTIMATORS:
                name=f"{condition['label']}/{control}/{estimator_name}"
                period_curves[name]={metric:[value/len(SEEDS) for value in curve_sums[(condition['label'],control,estimator_name,metric)]]
                                     for metric in PERIOD_METRICS}
    return {
        "experiment":"HLS-S3b-E1 final memory and closed-loop diagnostic",
        "date":"2026-10-23",
        "design":{"conditions":list(CONDITIONS),"controls":list(CONTROLS),
                  "estimators":ESTIMATORS,"decision_rule":"empirical-mean exact matching, no exploration bonus; canonical lexicographic tie-break",
                  "window":WINDOW,"horizon":HORIZON,"calibration_periods":CALIBRATION,
                  "seeds":list(SEEDS),"replicate_count":len(episodes),
                  "reduced_design_justification":"infrequent/high vs frequent/high varies stability interval at high opportunity; frequent/high vs frequent/low varies opportunity at fast changes; no interaction estimate",
                  "shared_calendar":"first nine periods reuse fixed calibration matchings; afterward cycle all six feasible matchings, independent of diagnostic choices; mask gates observed outcomes",
                  "closed_loop":"after common nine-period calibration, each estimator's own matching determines which masked outcomes it receives",
                  "memory_only_difference":"global_mean retains all; recent_mean retains observations with period >= t-W; same empirical mean and neutral 0.5 when no usable sample",
                  "regret_oracle":"exact maximum true-mean value over the same six feasible complete matchings; evaluation only",
                  "no_resource_cost":True},
        "validation":{"shared_observation_hashes_equal":True,
                      "same_exogenous_seed_streams_paired":True,
                      "matching_decision_rule_shared":True,
                      "future_information_hidden":True,
                      "oracle_feasible":True,
                      "regret_equals_oracle_minus_selected_expected_value":True,
                      "pef_read_only_expected_reward":True,
                      "experiment_run_roundtrip":True},
        "profiles":{f"{c['label']}/{control}":asdict(profiles[(c['label'],control)])
                    for c in CONDITIONS for control in CONTROLS},
        "episodes":episodes,"experiment_runs":runs,"arm_summary":arms,
        "paired_contrasts":paired,"pef_paired_reward_contrasts":pef_paired,
        "memory_effect_across_conditions":memory_effect_across_conditions,
        "closed_loop_minus_shared_descriptive":cross_control,
        "period_curves_mean_across_seeds":period_curves,
        "decision_error_examples":{
            f"{e['condition']}/{e['control']}/{e['estimator']}/seed{e['seed']}":e["first_decision_error_examples"]
            for e in episodes if e["first_decision_error_examples"]},
        "artifacts":{"period_curves_are_seed_aggregates":True,
                     "raw_period_trace_stored":False},
        "provenance":{"base_git_revision":revision,"seed_ranges_reused_from_factorial":True,
                      "source":"experiments/run_hls_s3b_memory_replay_diagnostic.py",
                      "source_sha256_at_run_start":source_sha256,
                      "historical_factorial_artifacts_overwritten":False},
    }


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True,exist_ok=True)
    result=run()
    RESULT_PATH.write_text(json.dumps(result,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"result":RESULT_PATH.as_posix(),"episodes":len(result["episodes"]),
                      "conditions":len(CONDITIONS),"replicates":len(SEEDS)},indent=2))
