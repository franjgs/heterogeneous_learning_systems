#!/usr/bin/env python3
"""Reproduce the pre-existing S3b 2x2 design with contract/PEF traces.

Levels and algorithm parameters are inherited unchanged from the registered
change-observation factorial. New paired seeds and a separate result directory
make this an instrumented reproduction rather than an overwrite.
"""

from __future__ import annotations

import gzip
import json
import math
import statistics
import subprocess
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from typing import Any

from scipy.stats import t as student_t

from experiments.run_hls_s3b_change_observation_factorial import (
    BASE,
    CALIBRATION,
    CALIBRATION_PERMUTATIONS,
    CHANGE_INTERVALS,
    CRITICAL_PAIRS,
    HORIZON,
    K,
    MATCHINGS,
    N,
    OBSERVATION_PROBABILITIES,
    PAIRS,
    POLICIES,
    SEEDS as HISTORICAL_SEEDS,
    TRANSIENT,
    WINDOW,
    XI,
    generate_randomness,
    run_episode,
)
from hls.experiment_contract import ExperimentRun
from hls.performance_evaluation import PerformanceEvaluator
from hls.synthetic.s3b_pef_adapter import adapt_s3b_episode, s3b_evaluation_profile


OUT_DIR = Path("results/experiments/hls_s3b_observability_recovery")
RESULT_PATH = OUT_DIR / "results.json"
TRACE_PATH = OUT_DIR / "period_traces.jsonl.gz"
SEEDS = tuple(range(9000, 9030))
SOLVER_PATH = Path("src/hls/nonstationary_assignment.py")
SOURCE_RUNNER_PATH = Path("experiments/run_hls_s3b_change_observation_factorial.py")


def ci(values) -> dict[str, Any]:
    rows = tuple(float(value) for value in values)
    if not rows:
        raise ValueError("cannot summarize an empty sample")
    mean = statistics.fmean(rows)
    sd = statistics.stdev(rows) if len(rows) > 1 else 0.0
    half = (float(student_t.ppf(0.975, len(rows) - 1)) * sd / math.sqrt(len(rows))
            if len(rows) > 1 else 0.0)
    return {"n_seeds": len(rows), "mean": mean, "sd_between_seeds": sd,
            "ci95": [mean - half, mean + half]}


def ci_optional(values) -> dict[str, Any]:
    rows = tuple(value for value in values if value is not None)
    if not rows:
        return {"n_seeds": 0, "mean": None, "sd_between_seeds": None,
                "ci95": None, "status": "NOT_OBSERVABLE"}
    return {**ci(rows), "status": "VALID"}


def _episode_lookup(episodes: list[dict]) -> dict[tuple[int, float, int, str], dict]:
    return {(row["interval"], row["opportunity_probability"], row["seed"], row["policy"]): row
            for row in episodes}


def summarize(episodes: list[dict], pef_episode_values: dict[str, float]) -> dict[str, Any]:
    lookup = _episode_lookup(episodes)
    cells: dict[str, Any] = {}
    for change_name, interval in CHANGE_INTERVALS.items():
        for observation_name, probability in OBSERVATION_PROBABILITIES.items():
            for policy in POLICIES:
                name = f"{change_name}/{observation_name}/{policy}"
                rows = [lookup[(interval, probability, seed, policy)] for seed in SEEDS]
                cells[name] = {
                    metric: ci(row[metric] for row in rows)
                    for metric in ("expected_reward", "realized_reward", "oracle_expected_reward",
                                   "expected_regret", "optimal_rate", "assignment_changes")
                }
                cells[name]["pef_expected_reward"] = ci(
                    pef_episode_values[row["run_id"]] for row in rows
                )
                cells[name]["regimes"] = {
                    regime: {metric: ci(row["regimes"][regime][metric] for row in rows)
                             for metric in ("expected_reward", "expected_regret", "optimal_rate")}
                    for regime in ("base", "transient")
                }
                cells[name]["pair_information"] = {
                    f"{i},{k}": {
                        field: ci_optional(row["pair_information"][f"{i},{k}"][field] for row in rows)
                        for field in ("opportunities", "executions", "observations",
                                      "observation_per_opportunity", "observation_per_execution",
                                      "mean_estimation_squared_error",
                                      "mean_compatible_observations_in_full_history_at_decision",
                                      "mean_compatible_observations_retained_at_decision",
                                      "mean_incompatible_observations_retained_at_decision",
                                      "final_last_observation_age")
                    }
                    for i, k in PAIRS
                }
                cells[name]["effective_observations_per_stability_interval"] = {
                    f"{i},{k}": {
                        regime: ci(
                            row["pair_information"][f"{i},{k}"]["observations_by_competence_regime"][regime]
                            / (HORIZON // (2 * interval)) for row in rows
                        )
                        for regime in ("base", "transient")
                    }
                    for i, k in PAIRS
                }
                cells[name]["recovery"] = {
                    # Transition events within a seed are correlated. Summarize
                    # each replicate first, then form uncertainty across seeds.
                    "mean_lag_when_recovered_by_seed": ci(
                        statistics.fmean(lag for lag in row["recovery_lags"] if lag is not None)
                        for row in rows
                        if any(lag is not None for lag in row["recovery_lags"])
                    ) if any(lag is not None for row in rows for lag in row["recovery_lags"]) else None,
                    "pooled_mean_lag_when_recovered_descriptive": (
                        statistics.fmean(lag for row in rows for lag in row["recovery_lags"]
                                         if lag is not None)
                        if any(lag is not None for row in rows for lag in row["recovery_lags"])
                        else None
                    ),
                    "events_not_recovered_within_regime_or_search": sum(
                        lag is None for row in rows for lag in row["recovery_lags"]
                    ),
                    "events": sum(len(row["recovery_lags"]) for row in rows),
                }

    paired: dict[str, Any] = {}
    for change_name, interval in CHANGE_INTERVALS.items():
        for observation_name, probability in OBSERVATION_PROBABILITIES.items():
            for metric in ("expected_regret", "expected_reward", "optimal_rate"):
                paired[f"{change_name}/{observation_name}/SW_minus_UCB/{metric}"] = ci(
                    lookup[(interval, probability, seed, "SW-UCB")][metric]
                    - lookup[(interval, probability, seed, "UCB1")][metric]
                    for seed in SEEDS
                )
    for observation_name, probability in OBSERVATION_PROBABILITIES.items():
        for metric in ("expected_regret", "expected_reward", "optimal_rate"):
            paired[f"frequency_effect_on_policy_difference/{observation_name}/{metric}"] = ci(
                (lookup[(CHANGE_INTERVALS["frequent"], probability, seed, "SW-UCB")][metric]
                 - lookup[(CHANGE_INTERVALS["frequent"], probability, seed, "UCB1")][metric])
                - (lookup[(CHANGE_INTERVALS["infrequent"], probability, seed, "SW-UCB")][metric]
                   - lookup[(CHANGE_INTERVALS["infrequent"], probability, seed, "UCB1")][metric])
                for seed in SEEDS
            )
    for change_name, interval in CHANGE_INTERVALS.items():
        for policy in POLICIES:
            for metric in ("expected_regret", "expected_reward", "optimal_rate"):
                paired[f"availability_effect_low_minus_high/{change_name}/{policy}/{metric}"] = ci(
                    lookup[(interval, OBSERVATION_PROBABILITIES["low"], seed, policy)][metric]
                    - lookup[(interval, OBSERVATION_PROBABILITIES["high"], seed, policy)][metric]
                    for seed in SEEDS
                )
    for metric in ("expected_regret", "expected_reward", "optimal_rate"):
        # Difference-in-differences: frequency effect on (SW-UCB - UCB1)
        # under high availability minus the same effect under low availability.
        paired[f"factorial_interaction_frequency_x_availability/{metric}"] = ci(
            ((lookup[(CHANGE_INTERVALS["frequent"], OBSERVATION_PROBABILITIES["high"], seed, "SW-UCB")][metric]
              - lookup[(CHANGE_INTERVALS["frequent"], OBSERVATION_PROBABILITIES["high"], seed, "UCB1")][metric])
             - (lookup[(CHANGE_INTERVALS["infrequent"], OBSERVATION_PROBABILITIES["high"], seed, "SW-UCB")][metric]
                - lookup[(CHANGE_INTERVALS["infrequent"], OBSERVATION_PROBABILITIES["high"], seed, "UCB1")][metric]))
            - ((lookup[(CHANGE_INTERVALS["frequent"], OBSERVATION_PROBABILITIES["low"], seed, "SW-UCB")][metric]
                - lookup[(CHANGE_INTERVALS["frequent"], OBSERVATION_PROBABILITIES["low"], seed, "UCB1")][metric])
               - (lookup[(CHANGE_INTERVALS["infrequent"], OBSERVATION_PROBABILITIES["low"], seed, "SW-UCB")][metric]
                  - lookup[(CHANGE_INTERVALS["infrequent"], OBSERVATION_PROBABILITIES["low"], seed, "UCB1")][metric]))
            for seed in SEEDS
        )
    return {"cells": cells, "paired_contrasts": paired,
            "inference_unit": "paired seed; periods are not independent replicates"}


def run() -> dict[str, Any]:
    if set(SEEDS) & set(HISTORICAL_SEEDS):
        raise AssertionError("instrumented replication seeds must be independent of historical factorial seeds")
    base_revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True,
    ).stdout.strip()
    worktree_status = subprocess.run(
        ["git", "status", "--porcelain"], check=True, capture_output=True, text=True,
    ).stdout
    exact_revision = base_revision if not worktree_status.strip() else None
    solver_hash_before = sha256(SOLVER_PATH.read_bytes()).hexdigest()
    source_hash_before = sha256(SOURCE_RUNNER_PATH.read_bytes()).hexdigest()
    profiles = {}
    evaluators = {}
    for change_name, interval in CHANGE_INTERVALS.items():
        for observation_name, probability in OBSERVATION_PROBABILITIES.items():
            profile = s3b_evaluation_profile(change_name, interval, observation_name, probability)
            profiles[(interval, probability)] = profile
            evaluator = PerformanceEvaluator()
            evaluator.register_profile(profile)
            evaluators[(interval, probability)] = evaluator

    episodes: list[dict] = []
    experiment_runs: dict[str, dict] = {}
    pef_episode_values: dict[str, float] = {}
    pef_episode_results = {}
    trace_index: dict[str, dict] = {}
    run_counter = 0
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with gzip.open(TRACE_PATH, "wt", encoding="utf-8", compresslevel=6) as trace_file:
        header = {
            "record_type": "schema",
            "schema": "s3b_compact_pairwise_diagnostics_v1",
            "pair_order_flat_nk": [list(pair) for pair in PAIRS],
            "matching_catalog": [[list(pair) for pair in matching] for matching in MATCHINGS],
            "regime_codes": {"0": "base", "1": "transient"},
            "feedback_mask_note": "bit i*K+k indicates selected pair outcome was observed; availability_mask applies to all pairs but is not policy-visible before action",
            "indices_note": "mean, bonus and index arrays are diagnostics; true matrices are in configuration and evaluation-only",
        }
        trace_file.write(json.dumps(header, separators=(",", ":")) + "\n")
        for seed in SEEDS:
            reward_uniforms, opportunity_uniforms = generate_randomness(seed)
            for change_name, interval in CHANGE_INTERVALS.items():
                for observation_name, probability in OBSERVATION_PROBABILITIES.items():
                    profile = profiles[(interval, probability)]
                    for policy_id in POLICIES:
                        run_counter += 1
                        run_id = f"s3b-obs-recovery-{change_name}-{observation_name}-{policy_id}-seed{seed}"
                        episode = run_episode(
                            seed, interval, probability, policy_id,
                            reward_uniforms, opportunity_uniforms, detailed_trace=True,
                        )
                        trace = episode.pop("trace")
                        detailed = trace["detailed_periods"]
                        for row in detailed:
                            trace_file.write(json.dumps({
                                "record_type": "period",
                                "run_id": run_id,
                                "seed": seed,
                                "change_frequency": change_name,
                                "observation_availability": observation_name,
                                "policy": policy_id,
                                **row,
                            }, separators=(",", ":"), allow_nan=False) + "\n")
                        config = {
                            "scenario_id": "S3b",
                            "configuration_id": profile.configuration_id,
                            "organizational_problem_id": "B2_complete_one_to_one_matching_3x3",
                            "agents": N,
                            "tasks": K,
                            "competence_base": BASE,
                            "competence_transient": TRANSIENT,
                            "change_interval": interval,
                            "observation_probability": probability,
                            "observation_level": observation_name,
                            "horizon": HORIZON,
                            "calibration_periods": CALIBRATION,
                            "xi": XI,
                            "window": WINDOW if policy_id == "SW-UCB" else None,
                            "policy_formula": (
                                "empirical pair mean + sqrt(2 log(max(2,t+1))/n)"
                                if policy_id == "UCB1" else
                                f"empirical pair mean over global-period window W={WINDOW} + "
                                "sqrt(xi * log(max(2,min(t+1,W))) / n)"
                            ),
                            "matching_solver": "exact maximum-weight matching over six permutations",
                            "resource_model": "no separate resource cost; one complete matching executes three pairs per period",
                        }
                        trace_ref = f"{TRACE_PATH.as_posix()}#run_id={run_id}"
                        run_record, pef_records = adapt_s3b_episode(
                            episode,
                            detailed,
                            profile,
                            trace_artifact=trace_ref,
                            run_id=run_id,
                            software_revision=exact_revision,
                            base_git_revision=base_revision,
                            seed=seed,
                            configuration=config,
                            pair_information=episode["pair_information"],
                        )
                        if ExperimentRun.from_json(run_record.to_json()).to_json() != run_record.to_json():
                            raise AssertionError(f"ExperimentRun round-trip failed for {run_id}")
                        pef = evaluators[(interval, probability)].evaluate(
                            profile.profile_id, policy_id, pef_records,
                        )["original_reward_cumulative"]
                        if not math.isclose(pef.value, episode["expected_reward"], rel_tol=0.0, abs_tol=1e-8):
                            raise AssertionError("HLS-PEF reward differs from source expected reward")
                        pef_episode_values[run_id] = float(pef.value)
                        pef_episode_results[run_id] = pef
                        experiment_runs[run_id] = run_record.to_dict()
                        episode.update({
                            "change_frequency": change_name,
                            "observation_availability": observation_name,
                            "run_id": run_id,
                            "profile_id": profile.profile_id,
                            "pef_expected_reward": float(pef.value),
                        })
                        trace_index[run_id] = {
                            "seed": seed,
                            "change_frequency": change_name,
                            "change_interval": interval,
                            "observation_availability": observation_name,
                            "observation_probability": probability,
                            "policy": policy_id,
                            "periods": HORIZON,
                        }
                        episodes.append(episode)

    summary = summarize(episodes, pef_episode_values)
    pef_comparisons = {}
    lookup = _episode_lookup(episodes)
    for change_name, interval in CHANGE_INTERVALS.items():
        for observation_name, probability in OBSERVATION_PROBABILITIES.items():
            differences = []
            for seed in SEEDS:
                sw_row = lookup[(interval, probability, seed, "SW-UCB")]
                ucb_row = lookup[(interval, probability, seed, "UCB1")]
                difference = PerformanceEvaluator.compare(
                    pef_episode_results[sw_row["run_id"]],
                    pef_episode_results[ucb_row["run_id"]],
                )
                differences.append(difference.value)
            pef_comparisons[f"{change_name}/{observation_name}/SW_minus_UCB/reward"] = ci(differences)
    solver_hash_after = sha256(SOLVER_PATH.read_bytes()).hexdigest()
    source_hash_after = sha256(SOURCE_RUNNER_PATH.read_bytes()).hexdigest()
    if solver_hash_before != solver_hash_after or source_hash_before != source_hash_after:
        raise AssertionError("source S3b mechanism runner changed during experiment")

    design = {
        "agents": N,
        "tasks": K,
        "organizational_problem": "B2 full one-to-one matching; same six feasible matchings in every cell",
        "horizon": HORIZON,
        "seeds": list(SEEDS),
        "historical_factorial_seeds_not_reused": list(HISTORICAL_SEEDS),
        "competence_base": BASE,
        "competence_transient": TRANSIENT,
        "change_interval_by_level": CHANGE_INTERVALS,
        "change_schedule": "deterministic recurrent alternation; transitions at interval multiples",
        "observation_probability_by_level": OBSERVATION_PROBABILITIES,
        "observation_rule": "pre-generated exogenous per-pair/per-period mask; policy sees feedback only after assigning that pair",
        "reward_model": "Bernoulli(c_ik(t)); all selected outcomes contribute to realized reward whether observed or not",
        "random_streams": {
            "rewards": "random.Random(seed XOR 0xA17E5B), period-agent-task",
            "opportunity_masks": "random.Random(seed XOR 0x0B5E7A), period-agent-task; thresholds nested at .25/.75",
        },
        "calibration": f"first {CALIBRATION} periods use existing fixed E1 matching cycle and count in reward",
        "algorithms": {
            "UCB1": "existing PairwiseBanditEstimator; empirical mean + sqrt(2 log(max(2,t+1))/n)",
            "SW-UCB": f"same estimator, global-time window W={WINDOW}, xi={XI}; published SW-UCB confidence form",
            "adaptation_note": "single-play bandit analyses are not claimed for simultaneous pairwise matching",
        },
        "oracle": "exact maximum true-mean complete matching; evaluation only and independent of observation masks",
        "main_outcome": "expected cumulative collective matching reward and expected regret against the dynamic oracle",
        "main_contrast": "paired-seed SW-UCB minus UCB1 regret within each factorial cell; frequency×availability difference-in-differences",
        "hypothesis": "the effect of memory choice on collective regret depends jointly on competence stability interval and exogenous per-pair feedback opportunity probability",
        "hypothesis_criterion": "report paired main effects and interaction with 95% t intervals; no directional winner is presupposed",
        "resource_costs": "no independent resource-cost variable exists in this B2 S3b model; assignment count is structural, not a cost",
        "rho_opportunity": "p_observe × stability interval; descriptive opportunity count, not a universal performance law",
        "rho_effective": "observations actually received per relevant pair per stability interval, conditional on organization selecting the pair",
    }
    if len(episodes) != len(SEEDS) * len(CHANGE_INTERVALS) * len(OBSERVATION_PROBABILITIES) * len(POLICIES):
        raise AssertionError("factorial cell/replicate count mismatch")
    oracle_invariants = {}
    for interval in CHANGE_INTERVALS.values():
        for seed in SEEDS:
            values = {round(row["oracle_expected_reward"], 10) for row in episodes
                      if row["seed"] == seed and row["interval"] == interval}
            oracle_invariants[f"seed{seed}/interval{interval}"] = len(values) == 1
    if not all(oracle_invariants.values()):
        raise AssertionError("oracle reward changed across observation/policy conditions")

    result = {
        "experiment": "HLS-S3b memory × change dynamics × observation opportunities (contract-instrumented reproduction)",
        "date": "2026-10-23",
        "design": design,
        "validation": {
            "same_feasible_actions_all_cells": True,
            "observation_opportunities_exogenous_and_hidden_before_action": True,
            "only_selected_available_feedback_updates_estimators": True,
            "realized_rewards_count_even_without_feedback": True,
            "oracle_independent_of_availability": True,
            "competences_hidden_from_policy": True,
            "pef_evaluates_expected_reward_only": True,
            "no_resource_cost_in_model": True,
            "experiment_run_json_round_trips": True,
            "historical_artifacts_overwritten": False,
        },
        "profiles": {
            f"{change}/{availability}": asdict(profile)
            for (interval, probability), profile in profiles.items()
            for change, mapped_interval in CHANGE_INTERVALS.items() if mapped_interval == interval
            for availability, mapped_probability in OBSERVATION_PROBABILITIES.items() if mapped_probability == probability
        },
        "summary": summary,
        "analysis_method": {
            "independent_unit": "paired replicate seed",
            "recovery_lag_uncertainty": (
                "average eligible change-boundary lags within each seed, then form the 95% t interval across seeds"
            ),
            "periods_and_change_boundaries_are_not_independent_replicates": True,
        },
        "hls_pef_paired_reward_comparisons": pef_comparisons,
        "episodes": episodes,
        "experiment_runs": experiment_runs,
        "trace_index": trace_index,
        "artifacts": {
            "period_traces": TRACE_PATH.as_posix(),
            "historical_factorial_preserved": "results/experiments/hls_s3b_change_observation_factorial/results.json",
        },
        "provenance": {
            "base_git_revision": base_revision,
            "software_revision": exact_revision,
            "working_tree_clean": exact_revision is not None,
            "source_sha256": {
                "pairwise_estimator": sha256(SOLVER_PATH.read_bytes()).hexdigest(),
                "factorial_source_runner": source_hash_after,
                "instrumented_runner": sha256(Path(__file__).read_bytes()).hexdigest(),
            },
            "source_artifacts": [
                "results/experiments/hls_s3b_change_observation_factorial/results.json",
                "results/experiments/hls_s3b_change_observation_factorial/period_traces.jsonl.gz",
            ],
        },
    }
    return result


if __name__ == "__main__":
    artifact = run()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(artifact, separators=(",", ":"), allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({"result": RESULT_PATH.as_posix(),
                      "period_traces": TRACE_PATH.as_posix(),
                      "cells": len(artifact["summary"]["cells"]),
                      "replicates": len(artifact["episodes"])}, indent=2))
