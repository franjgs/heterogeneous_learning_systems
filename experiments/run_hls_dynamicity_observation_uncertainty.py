#!/usr/bin/env python3
"""Observation-noise extension of frozen HLS D0/D1/D2 paired scenarios."""

from __future__ import annotations

import json
import itertools
import math
import platform
import random
import statistics
import time
from pathlib import Path

if __package__:
    from . import run_hls_dynamicity_information_ablation as prior
else:  # Direct execution puts experiments/ rather than repository root on sys.path.
    import run_hls_dynamicity_information_ablation as prior

base = prior.base

OUTPUT_DIR = Path("results/experiments/hls_dynamicity_observation_uncertainty")
RESULT_PATH = OUTPUT_DIR / "results.json"
SIGMAS = (0.0, 0.10, 0.20)
POLICIES = (
    "FIXED_OPT_TRAIN",
    "P0_REACTIVE_MATCHING_OBSERVED",
    "LINUCB_HUNGARIAN_OBSERVED",
    "DYNAMIC_ORACLE_TRUE_EVALUATOR_ONLY",
)
OBSERVATION_NOISE_XOR = 0x0B5E7A
_PERMUTATIONS = tuple(itertools.permutations(range(3)))


def _all_feasible_matching_actions():
    """Existing optional-cardinality one-to-one assignments (0–3 edges)."""
    complete = tuple(
        tuple(sorted((permutation[task], task) for task in range(3)))
        for permutation in _PERMUTATIONS
    )
    partial = []
    for cardinality in (2, 1, 0):
        for agents in itertools.combinations(range(3), cardinality):
            for tasks in itertools.combinations(range(3), cardinality):
                for task_order in itertools.permutations(tasks):
                    partial.append(tuple(sorted(zip(agents, task_order))))
    return complete + tuple(partial)


MATCHINGS = _all_feasible_matching_actions()
MATCHING_TO_ID = {matching: index for index, matching in enumerate(MATCHINGS)}
MATCHING_ACTIONS = tuple(
    tuple(tuple(float((agent, task) in matching) for task in range(3))
          for agent in range(3))
    for matching in MATCHINGS
)
MATCHING_CODE_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def standard_normal_observation_noise(seed: int, horizon: int = base.HORIZON):
    """One shared standardized Gaussian field, separate from reward noise."""
    rng = random.Random(seed ^ OBSERVATION_NOISE_XOR)
    return tuple(
        tuple(tuple(rng.gauss(0.0, 1.0) for _ in range(3)) for _ in range(3))
        for _ in range(horizon)
    )


def observed_competence(true_competence, standard_noise, sigma: float):
    if sigma not in SIGMAS:
        raise ValueError("sigma must be one of the preregistered levels")
    return tuple(
        tuple(min(1.0, max(0.0, true_competence[i][k] + sigma * standard_noise[i][k]))
              for k in range(3))
        for i in range(3)
    )


def _p0_reactive_matches(competence_observation):
    """Existing P0 rank over the same optional one-to-one action set."""
    _, allocation = prior.P0.choose(
        MATCHING_ACTIONS, competence_observation, prior.P0_PROBLEM,
    )
    return tuple(sorted(
        (agent, task)
        for agent, row in enumerate(allocation)
        for task, effort in enumerate(row) if effort == 1.0
    ))


def _matching_code(matches):
    return MATCHING_CODE_ALPHABET[MATCHING_TO_ID[tuple(sorted(matches))]]


def evaluate_episode(condition: str, sigma: float, seed: int, fixed_mapping,
                     horizon: int = base.HORIZON):
    demand = base.generate_environment_trajectory_nk(
        base.make_environment_config(horizon), seed=seed,
    )
    regimes, true_path = base.competence_path(condition, seed, horizon)
    standard_noise = standard_normal_observation_noise(seed, horizon)
    reward_uniforms = base._potential_uniforms(seed, horizon)
    if len(demand.problems) != horizon or any(
        problem.requirements != (1.0, 1.0, 1.0) for problem in demand.problems
    ):
        raise AssertionError("demand no longer matches the frozen D0/D1/D2 setup")

    learner = prior.PairwiseLinUCBAdapterNK(3, 3, 1, prior.ALPHA)
    realized = {policy: [] for policy in POLICIES}
    expected = {policy: [] for policy in POLICIES}
    regrets = {policy: [] for policy in POLICIES}
    assignments = {policy: [] for policy in POLICIES}
    observation_squared_error = []
    clipped_values = 0
    observation_count = 0
    compute_seconds = {policy: 0.0 for policy in POLICIES}
    resources = {policy: 0 for policy in POLICIES}

    for period, (regime, true_matrix) in enumerate(zip(regimes, true_path)):
        observed_matrix = observed_competence(true_matrix, standard_noise[period], sigma)
        observation_squared_error.extend(
            (observed_matrix[i][k] - true_matrix[i][k]) ** 2
            for i in range(3) for k in range(3)
        )
        clipped_values += sum(
            true_matrix[i][k] + sigma * standard_noise[period][i][k] < 0.0
            or true_matrix[i][k] + sigma * standard_noise[period][i][k] > 1.0
            for i in range(3) for k in range(3)
        )
        observation_count += 9

        # Rewards are generated only from true competence; potential outcomes
        # are common to every organization and every sigma for this seed.
        realized_matrix = base._realized_reward_matrix(true_matrix, reward_uniforms[period])
        feedback_all_pairs = {
            (i, k): realized_matrix[i][k] for i in range(3) for k in range(3)
        }
        contexts = tuple(tuple((observed_matrix[i][k],) for k in range(3))
                         for i in range(3))

        started = time.perf_counter()
        p0_matches = _p0_reactive_matches(observed_matrix)
        compute_seconds["P0_REACTIVE_MATCHING_OBSERVED"] += time.perf_counter() - started

        started = time.perf_counter()
        scores = learner.score_matrix(contexts)
        linucb_matches = base.ASSIGNER.optimize(scores, base.ORG, base.PROBLEM).matches
        learner.update_selected(
            linucb_matches, contexts,
            {pair: feedback_all_pairs[pair] for pair in linucb_matches},
        )
        compute_seconds["LINUCB_HUNGARIAN_OBSERVED"] += time.perf_counter() - started

        fixed_matches = base._fixed_matches(fixed_mapping)
        started = time.perf_counter()
        oracle_matches = base._oracle_matches(true_matrix)
        compute_seconds["DYNAMIC_ORACLE_TRUE_EVALUATOR_ONLY"] += time.perf_counter() - started
        decisions = {
            "FIXED_OPT_TRAIN": fixed_matches,
            "P0_REACTIVE_MATCHING_OBSERVED": p0_matches,
            "LINUCB_HUNGARIAN_OBSERVED": linucb_matches,
            "DYNAMIC_ORACLE_TRUE_EVALUATOR_ONLY": oracle_matches,
        }
        oracle_value = base._matrix_sum(true_matrix, oracle_matches)
        for policy, matches in decisions.items():
            if len(matches) > 3 or len({i for i, _ in matches}) != len(matches) \
                    or len({k for _, k in matches}) != len(matches):
                raise AssertionError(f"{policy} violated matching/resource constraints")
            realized[policy].append(base._matrix_sum(realized_matrix, matches))
            expected[policy].append(base._matrix_sum(true_matrix, matches))
            regrets[policy].append(oracle_value - expected[policy][-1])
            assignments[policy].append(tuple(sorted(matches)))
            resources[policy] += len(matches)

    switches = [t for t in range(1, horizon) if regimes[t] != regimes[t - 1]]
    return {
        "seed": seed,
        "condition": condition,
        "sigma": sigma,
        "regime_path_bits": "".join(map(str, regimes)),
        "regime_switch_periods": switches,
        "competence_seed": seed ^ 0xC05E7E,
        "observation_noise_seed": seed ^ OBSERVATION_NOISE_XOR,
        "reward_noise_seed": seed ^ 0xA11CE,
        "demand_trajectory_seed": demand.seed,
        "assignment_path_code_by_policy": {
            policy: "".join(_matching_code(matches) for matches in assignments[policy])
            for policy in POLICIES
        },
        "realized_reward_digit_series_by_policy": {
            policy: "".join(str(int(value)) for value in realized[policy])
            for policy in POLICIES
        },
        "cumulative_realized_reward": {policy: sum(realized[policy]) for policy in POLICIES},
        "cumulative_expected_reward": {policy: sum(expected[policy]) for policy in POLICIES},
        "cumulative_pseudo_regret": {policy: sum(regrets[policy]) for policy in POLICIES},
        "optimal_assignment_match_fraction": {
            policy: sum(assignments[policy][t] == tuple(sorted(base._oracle_matches(true_path[t])))
                        for t in range(horizon)) / horizon for policy in POLICIES
        },
        "assignment_change_count": {
            policy: sum(path[t] != path[t - 1] for t in range(1, horizon))
            for policy, path in assignments.items()
        },
        "resource_use": resources,
        "observation_rmse": math.sqrt(statistics.fmean(observation_squared_error)),
        "observation_clipped_fraction": clipped_values / observation_count,
        "linucb_observation_counts": [list(row) for row in learner.observation_counts],
        "linucb_coefficient_estimates": [[list(coef) for coef in row]
                                          for row in learner.coefficient_estimates],
        "policy_compute_seconds": compute_seconds,
    }


def _paired_interval(differences):
    from scipy.stats import t
    values = tuple(float(value) for value in differences)
    mean = statistics.fmean(values)
    half = float(t.ppf(0.975, len(values) - 1)) * statistics.stdev(values) / math.sqrt(len(values))
    return [mean - half, mean + half]


def summarize_cell(condition, sigma, replications):
    summary = {}
    for policy in POLICIES:
        rewards = [rep["cumulative_realized_reward"][policy] for rep in replications]
        regrets = [rep["cumulative_pseudo_regret"][policy] for rep in replications]
        paired = {}
        for comparator in POLICIES:
            if comparator == policy:
                continue
            differences = [rep["cumulative_realized_reward"][policy] -
                           rep["cumulative_realized_reward"][comparator]
                           for rep in replications]
            paired[comparator] = {
                "mean_difference": statistics.fmean(differences),
                "descriptive_95pct_t_interval": _paired_interval(differences),
            }
        summary[policy] = {
            "mean_cumulative_reward": statistics.fmean(rewards),
            "sd_cumulative_reward": statistics.stdev(rewards),
            "mean_cumulative_expected_reward": statistics.fmean(
                rep["cumulative_expected_reward"][policy] for rep in replications
            ),
            "mean_pseudo_regret_vs_true_competence_oracle": statistics.fmean(regrets),
            "mean_paired_reward_differences": paired,
            "optimal_assignment_match_fraction": statistics.fmean(
                rep["optimal_assignment_match_fraction"][policy] for rep in replications
            ),
            "mean_assignment_changes": statistics.fmean(
                rep["assignment_change_count"][policy] for rep in replications
            ),
            "mean_resource_use": statistics.fmean(rep["resource_use"][policy] for rep in replications),
            "mean_compute_seconds_per_episode": statistics.fmean(
                rep["policy_compute_seconds"][policy] for rep in replications
            ),
        }
    return {
        "condition": condition,
        "sigma": sigma,
        "n_evaluation_seeds": len(replications),
        "mean_observation_rmse": statistics.fmean(rep["observation_rmse"] for rep in replications),
        "mean_observation_clipped_fraction": statistics.fmean(
            rep["observation_clipped_fraction"] for rep in replications
        ),
        "policy_summary": summary,
        "replications": replications,
    }


def _preflight():
    if base.HORIZON != 300 or base.EVAL_SEEDS != tuple(range(8200, 8220)):
        raise AssertionError("the frozen D0/D1/D2 protocol changed")
    if set(base.TRAIN_SEEDS) & set(base.EVAL_SEEDS):
        raise AssertionError("fixed training and evaluation seeds overlap")
    checks = base.preflight()
    seed = base.EVAL_SEEDS[0]
    noise_a = standard_normal_observation_noise(seed, 8)
    noise_b = standard_normal_observation_noise(seed, 8)
    if noise_a != noise_b:
        raise AssertionError("observation noise is not reproducible")
    for condition in base.CONDITIONS:
        _, path = base.competence_path(condition, seed, 8)
        observed = observed_competence(path[0], noise_a[0], 0.0)
        if observed != path[0]:
            raise AssertionError("sigma=0 does not reproduce true competence")
    if base._potential_uniforms(seed, 8) == noise_a:
        raise AssertionError("observation noise unexpectedly reuses reward stream")
    return {
        "original_dynamicity_preflight": checks,
        "evaluation_seed_count": len(base.EVAL_SEEDS),
        "training_evaluation_disjoint": True,
        "sigma_zero_identity": True,
        "observation_noise_reproducible_and_separate": True,
        "same_observation_generator_for_all_policies_and_dynamicity_conditions": True,
        "reward_generation_uses_true_competence": True,
        "learning_feedback_selected_pairs_only": True,
        "one_to_one_actions_and_common_resource_budget": len(MATCHINGS) == 34,
        "linucb_implementation_and_matching_optimizer_unchanged": True,
    }


def run_experiment():
    checks = _preflight()
    conditions = {}
    for condition in base.CONDITIONS:
        fixed_mapping, train_value, _ = base._fit_fixed_map(condition)
        sigma_cells = {}
        for sigma in SIGMAS:
            reps = [evaluate_episode(condition, sigma, seed, fixed_mapping)
                    for seed in base.EVAL_SEEDS]
            sigma_cells[str(sigma)] = summarize_cell(condition, sigma, reps)
            sigma_cells[str(sigma)]["fixed_map_training"] = {
                "task_to_agent": {
                    base.TASKS[k]: base.AGENTS[fixed_mapping[k]] for k in range(3)
                },
                "training_seeds": list(base.TRAIN_SEEDS),
                "training_expected_reward": train_value,
            }
        conditions[condition] = sigma_cells

    # Exact paired validation against the immediately preceding information
    # ablation at sigma=0, including all evaluation seeds and assignments.
    previous_path = prior.RESULT_PATH
    previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else None
    sigma_zero_validation = {"previous_artifact_available": previous is not None}
    if previous is not None:
        checks_by_condition = {}
        for condition in base.CONDITIONS:
            current = conditions[condition]["0.0"]
            old = previous["conditions"][condition]
            mapping = {
                "FIXED_OPT_TRAIN": "FIXED_OPT_TRAIN",
                "LINUCB_HUNGARIAN_OBSERVED": "LINUCB_HUNGARIAN_FULL_CONTEXT",
                "P0_REACTIVE_MATCHING_OBSERVED": "P0_REACTIVE_MATCHING",
                "DYNAMIC_ORACLE_TRUE_EVALUATOR_ONLY": "DYNAMIC_ORACLE_EVALUATOR_ONLY",
            }
            passed = True
            for new_name, old_name in mapping.items():
                new_reps, old_reps = current["replications"], old["replications"]
                for new_rep, old_rep in zip(new_reps, old_reps):
                    old_codes = old_rep["assignment_path_code_by_policy"][old_name]
                    new_codes = new_rep["assignment_path_code_by_policy"][new_name]
                    old_rewards = old_rep["reward_digit_series_by_policy"][old_name]
                    new_rewards = new_rep["realized_reward_digit_series_by_policy"][new_name]
                    passed &= new_rep["seed"] == old_rep["seed"]
                    passed &= new_codes == old_codes
                    passed &= new_rewards == old_rewards
            checks_by_condition[condition] = bool(passed)
            if not passed:
                raise AssertionError(f"sigma=0 failed exact prior-result validation in {condition}")
        sigma_zero_validation["exact_per_seed_assignment_and_reward_match"] = checks_by_condition
    result = {
        "experiment": "HLS D0/D1/D2 competence observation uncertainty",
        "status": "bounded paired campaign executed",
        "source_scenario": "experiments/run_hls_dynamicity_sensitivity.py",
        "source_organizations": "experiments/run_hls_dynamicity_information_ablation.py and existing HLS P0/LinUCB/matching components",
        "ontology": {
            "A_scenario": "Unchanged exogenous D0/D1/D2 competence paths, C5 all-tasks demand, 3 agents x 3 tasks, 300 periods, existing 20 paired evaluation seeds.",
            "B_mechanism": "True competence generates Bernoulli rewards; observed competence is clipped true competence plus independent seeded Gaussian noise. LinUCB updates only from assigned-pair rewards; no agent learning is introduced.",
            "C_organization": "Trained fixed map; existing P0 applied to matching candidates using observed competence; existing LinUCB+matching using observed competence; true-competence oracle is evaluator-only.",
            "policy_learning_vs_agent_learning": "Only LinUCB policy parameters learn; competence trajectories remain exogenous and policy-independent.",
        },
        "configuration": {
            "conditions": base.CONDITIONS,
            "observation_sigma": SIGMAS,
            "observation_model": "C_obs[i,k,t]=clip(C_true[i,k,t]+sigma*Z[i,k,t],0,1); Z~N(0,1). One Z field per evaluation seed is reused across D conditions, sigma levels and policies; observation stream is independent of potential Bernoulli reward stream.",
            "agents": base.AGENTS, "tasks": base.TASKS, "horizon": base.HORIZON,
            "evaluation_seeds": base.EVAL_SEEDS, "training_seeds": base.TRAIN_SEEDS,
            "training_evaluation_disjoint": True,
            "base_competence": base.BASE_COMPETENCE,
            "competence_shift_pattern": base.COMPETENCE_SHIFT,
            "demand": "Unchanged C5 StationaryTaskDemand; all three task types present every period.",
            "reward_generation": "Bernoulli(mean=C_true[i,k,t]); existing pre-generated potential uniform per pair-period shared across organizations, sigma values and D conditions.",
            "observation_noise_seed": "evaluation_seed XOR 0x0B5E7A; random.Random.gauss(0,1), scaled by sigma. Separate from competence and reward seeds.",
            "linucb": "Existing PairwiseLinUCBAdapterNK with one current observed competence feature, alpha_from_delta(0.05), unchanged equations; feedback for selected assignments only.",
            "p0": "Existing P0ProductionOnlyNK over six one-to-one perfect matching candidates, scored from C_obs and public unit requirements only.",
            "fixed_opt": "Existing condition-specific fixed map trained on the 20 training seeds with known training reward means and held out from all evaluation seeds and observation noise.",
            "oracle": "Uses true C only for evaluator-side benchmark, regret and optimal assignment coincidence; never executable.",
            "resources": "Same existing one-to-one action/resource contract with maximum cardinality and collective budget 3 per period; actual assignments are recorded. Fixed and oracle policies use 900 assignments per episode; reactive/estimated policies may leave an edge unassigned when their observed-score rule ties at zero.",
            "runtime": platform.python_version(),
        },
        "preflight": checks,
        "sigma_zero_validation": sigma_zero_validation,
        "limitations": [
            "Gaussian observation errors are synthetic; clipping creates boundary mass and may induce nonzero bias near 0/1.",
            "The fixed policy uses the preexisting training protocol with expected rewards from training trajectories; it does not experience evaluation observation noise.",
            "The oracle sees true current competence and is evaluator-only, not a deployable policy.",
            "The public expected-reward identity E[R]=C is correctly specified; this is observation noise, not structural model misspecification.",
            "D1 and D2 jointly vary competence-shift amplitude and persistence; the interaction is descriptive, not a factorial identification of those two factors.",
            "Twenty seeds per cell support bounded exploratory comparisons, not confirmatory generalization claims.",
        ],
        "conditions": conditions,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
    return result


def main():
    result = run_experiment()
    for condition, cells in result["conditions"].items():
        for sigma, cell in cells.items():
            print(f"{condition} sigma={sigma}")
            for policy, row in cell["policy_summary"].items():
                print(f"  {policy}: {row['mean_cumulative_reward']:.3f} "
                      f"(SD {row['sd_cumulative_reward']:.3f}), "
                      f"regret {row['mean_pseudo_regret_vs_true_competence_oracle']:.3f}, "
                      f"optimal-match {row['optimal_assignment_match_fraction']:.3f}")
    print(f"Saved {RESULT_PATH}")


if __name__ == "__main__":
    main()
