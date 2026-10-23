#!/usr/bin/env python3
"""Paired information ablation over the frozen D0/D1/D2 experiment.

This runner imports scenario generation and the original policy components
without changing the original D0/D1/D2 runner or its result artifact.
"""

from __future__ import annotations

import itertools
import json
import statistics
import time
from pathlib import Path

if __package__:
    from . import run_hls_dynamicity_sensitivity as base
else:  # Direct script execution places only experiments/ on sys.path.
    import run_hls_dynamicity_sensitivity as base
from hls.hls_lab_nk_geometry import ProductiveAllocationNK
from hls.hls_lab_nk_production import P0ProductionOnlyNK
from hls.hls_lab_nk_linucb_assignment import PairwiseLinUCBAdapterNK
from hls.linucb import alpha_from_delta


OUTPUT_DIR = Path("results/experiments/hls_dynamicity_information_ablation")
RESULT_PATH = OUTPUT_DIR / "results.json"
PERMUTATIONS = tuple(itertools.permutations(range(3)))
POLICIES = (
    "FIXED_OPT_TRAIN",
    "LINUCB_HUNGARIAN_FULL_CONTEXT",
    "LINUCB_HUNGARIAN_NO_COMPETENCE",
    "LINUCB_GREEDY_FULL_CONTEXT",
    "P0_REACTIVE_MATCHING",
    "DYNAMIC_ORACLE_EVALUATOR_ONLY",
)
ALPHA = alpha_from_delta(0.05)
P0 = P0ProductionOnlyNK()
FEASIBLE_MATCHINGS: tuple[ProductiveAllocationNK, ...] = tuple(
    tuple(tuple(float(agent == permutation[task]) for task in range(3))
          for agent in range(3))
    for permutation in PERMUTATIONS
)
P0_PROBLEM = base.ProblemSpecNK(
    "three_simultaneous_unit_tasks", (1.0, 1.0, 1.0), 3.0,
)


def _task_only_contexts():
    """Task identity remains explicit; current competence is omitted."""
    return tuple(
        tuple(tuple(float(task == feature) for feature in range(3))
              for task in range(3))
        for _agent in range(3)
    )


def _p0_matching(competence):
    """Apply the existing P0 production rank over feasible perfect matchings.

    P0 receives only observable competence and the public task requirements.
    It is not passed the evaluator's true-reward matrix or future path.
    """
    _, allocation = P0.choose(FEASIBLE_MATCHINGS, competence, P0_PROBLEM)
    return tuple(sorted(
        (agent, task)
        for agent, row in enumerate(allocation)
        for task, effort in enumerate(row) if effort == 1.0
    ))


def _score_policy(policy, competence, contexts_full, contexts_ablated,
                  learners, observed_rewards):
    if policy == "LINUCB_HUNGARIAN_FULL_CONTEXT":
        model = learners[policy]
        scores = model.score_matrix(contexts_full)
        matches = base.ASSIGNER.optimize(scores, base.ORG, base.PROBLEM).matches
        model.update_selected(matches, contexts_full,
                              {pair: observed_rewards[pair] for pair in matches})
        return matches
    if policy == "LINUCB_HUNGARIAN_NO_COMPETENCE":
        model = learners[policy]
        scores = model.score_matrix(contexts_ablated)
        matches = base.ASSIGNER.optimize(scores, base.ORG, base.PROBLEM).matches
        model.update_selected(matches, contexts_ablated,
                              {pair: observed_rewards[pair] for pair in matches})
        return matches
    if policy == "LINUCB_GREEDY_FULL_CONTEXT":
        model = learners[policy]
        scores = model.score_matrix(contexts_full)
        matches = base.greedy_matching(scores)
        model.update_selected(matches, contexts_full,
                              {pair: observed_rewards[pair] for pair in matches})
        return matches
    raise ValueError(f"not a learned policy: {policy}")


def evaluate_episode(condition: str, seed: int, fixed_mapping, horizon=base.HORIZON):
    demand = base.generate_environment_trajectory_nk(
        base.make_environment_config(horizon), seed=seed,
    )
    regimes, competences = base.competence_path(condition, seed, horizon)
    uniforms = base._potential_uniforms(seed, horizon)
    if len(demand.problems) != horizon or any(
        problem.requirements != (1.0, 1.0, 1.0) for problem in demand.problems
    ):
        raise AssertionError("demand no longer matches the frozen D0/D1/D2 setup")

    learners = {
        "LINUCB_HUNGARIAN_FULL_CONTEXT": PairwiseLinUCBAdapterNK(3, 3, 1, ALPHA),
        "LINUCB_HUNGARIAN_NO_COMPETENCE": PairwiseLinUCBAdapterNK(3, 3, 3, ALPHA),
        "LINUCB_GREEDY_FULL_CONTEXT": PairwiseLinUCBAdapterNK(3, 3, 1, ALPHA),
    }
    realized = {policy: [] for policy in POLICIES}
    expected = {policy: [] for policy in POLICIES}
    regrets = {policy: [] for policy in POLICIES}
    assignment_ids = {policy: [] for policy in POLICIES}
    expected_oracle = []
    oracle_matches_path = []
    resources = {policy: 0 for policy in POLICIES}
    computation = {policy: 0.0 for policy in POLICIES}
    observations = {}
    for policy, model in learners.items():
        observations[policy] = model

    for period, (regime, competence) in enumerate(zip(regimes, competences)):
        observed_matrix = base._realized_reward_matrix(competence, uniforms[period])
        observed = {(agent, task): observed_matrix[agent][task]
                    for agent in range(3) for task in range(3)}
        contexts_full = tuple(tuple((competence[i][k],) for k in range(3))
                              for i in range(3))
        contexts_ablated = _task_only_contexts()

        decisions = {}
        for policy in (
            "LINUCB_HUNGARIAN_FULL_CONTEXT",
            "LINUCB_HUNGARIAN_NO_COMPETENCE",
            "LINUCB_GREEDY_FULL_CONTEXT",
        ):
            started = time.perf_counter()
            decisions[policy] = _score_policy(
                policy, competence, contexts_full, contexts_ablated,
                learners, observed,
            )
            computation[policy] += time.perf_counter() - started

        started = time.perf_counter()
        decisions["P0_REACTIVE_MATCHING"] = _p0_matching(competence)
        computation["P0_REACTIVE_MATCHING"] += time.perf_counter() - started
        decisions["FIXED_OPT_TRAIN"] = base._fixed_matches(fixed_mapping)
        started = time.perf_counter()
        decisions["DYNAMIC_ORACLE_EVALUATOR_ONLY"] = base._oracle_matches(competence)
        computation["DYNAMIC_ORACLE_EVALUATOR_ONLY"] += time.perf_counter() - started

        oracle = decisions["DYNAMIC_ORACLE_EVALUATOR_ONLY"]
        oracle_value = base._matrix_sum(competence, oracle)
        expected_oracle.append(oracle_value)
        oracle_matches_path.append(oracle)
        for policy, matches in decisions.items():
            if len(matches) != 3 or len({i for i, _ in matches}) != 3 \
                    or len({k for _, k in matches}) != 3:
                raise AssertionError(f"{policy} violated one-to-one full matching")
            reward = base._matrix_sum(observed_matrix, matches)
            mean_reward = base._matrix_sum(competence, matches)
            realized[policy].append(reward)
            expected[policy].append(mean_reward)
            regrets[policy].append(oracle_value - mean_reward)
            assignment_ids[policy].append(base.PERMUTATION_TO_ID[base._as_permutation(matches)])
            resources[policy] += len(matches)

    switches = [t for t in range(1, horizon) if regimes[t] != regimes[t - 1]]
    event_diagnostics = []
    for switch_index, switch in enumerate(switches):
        previous_switch = switches[switch_index - 1] if switch_index else -1
        next_switch = switches[switch_index + 1] if switch_index + 1 < len(switches) else horizon
        pre_start = max(switch - 10, previous_switch + 1, 0)
        post_stop = min(switch + 10, next_switch, horizon)
        row = {"period": switch, "from_regime": regimes[switch - 1],
               "to_regime": regimes[switch],
               "pre_window_periods": switch - pre_start,
               "post_window_periods": post_stop - switch,
               "by_policy": {}}
        for policy in POLICIES:
            idx = assignment_ids[policy]
            row["by_policy"][policy] = {
                "assignment_changed_at_switch": idx[switch] != idx[switch - 1],
                "assignment_matches_oracle_after_switch": idx[switch] ==
                    base.PERMUTATION_TO_ID[base._as_permutation(oracle_matches_path[switch])],
                "pre_change_expected_reward_per_period": (
                    statistics.fmean(expected[policy][pre_start:switch]) if pre_start < switch else None
                ),
                "post_change_expected_reward_per_period": (
                    statistics.fmean(expected[policy][switch:post_stop]) if switch < post_stop else None
                ),
                "post_change_realized_reward_per_period": (
                    statistics.fmean(realized[policy][switch:post_stop]) if switch < post_stop else None
                ),
                "post_change_pseudo_regret": sum(regrets[policy][switch:post_stop]),
            }
        event_diagnostics.append(row)

    fixed_eval_value = max(
        sum(sum(matrix[permutation[k]][k] for k in range(3)) for matrix in competences)
        for permutation in PERMUTATIONS
    )
    return {
        "seed": seed,
        "condition": condition,
        "regime_path_bits": "".join(str(value) for value in regimes),
        "regime_switch_periods": switches,
        "competence_seed": seed ^ 0xC05E7E,
        "reward_noise_seed": seed ^ 0xA11CE,
        "demand_trajectory_seed": demand.seed,
        "assignment_path_code_by_policy": {
            policy: "".join(map(str, assignment_ids[policy])) for policy in POLICIES
        },
        "reward_digit_series_by_policy": {
            policy: "".join(str(int(value)) for value in realized[policy])
            for policy in POLICIES
        },
        "cumulative_realized_reward": {policy: sum(realized[policy]) for policy in POLICIES},
        "cumulative_expected_reward": {policy: sum(expected[policy]) for policy in POLICIES},
        "cumulative_pseudo_regret": {policy: sum(regrets[policy]) for policy in POLICIES},
        "oracle_assignment_match_fraction": {
            policy: sum(
                assignment_ids[policy][t] == base.PERMUTATION_TO_ID[
                    base._as_permutation(oracle_matches_path[t])
                ] for t in range(horizon)
            ) / horizon for policy in POLICIES
        },
        "assignment_change_count": {
            policy: sum(path[t] != path[t - 1] for t in range(1, horizon))
            for policy, path in assignment_ids.items()
        },
        "resource_use": resources,
        "regime_period_counts": {
            "stable": sum(regime == 0 for regime in regimes),
            "shifted": sum(regime == 1 for regime in regimes),
        },
        "expected_reward_by_regime": {
            policy: {
                "stable": sum(expected[policy][t] for t in range(horizon) if regimes[t] == 0),
                "shifted": sum(expected[policy][t] for t in range(horizon) if regimes[t] == 1),
            } for policy in POLICIES
        },
        "switch_diagnostics": event_diagnostics,
        "linucb_observation_counts": {
            policy: [list(row) for row in model.observation_counts]
            for policy, model in learners.items()
        },
        "linucb_coefficient_estimates": {
            policy: [[list(coef) for coef in row] for row in model.coefficient_estimates]
            for policy, model in learners.items()
        },
        "policy_compute_seconds": computation,
        "retrospective_best_fixed_expected_reward": fixed_eval_value,
        "retrospective_fixed_loss_vs_dynamic_oracle": sum(expected_oracle) - fixed_eval_value,
    }


def _paired_interval(differences):
    values = tuple(float(x) for x in differences)
    mean = statistics.fmean(values)
    if len(values) < 2:
        return [mean, mean]
    # Same descriptive Student-t interval convention as the original runner.
    from scipy.stats import t
    half = float(t.ppf(0.975, len(values) - 1)) * statistics.stdev(values) / len(values) ** 0.5
    return [mean - half, mean + half]


def _summarize(condition, replications):
    summary = {}
    for policy in POLICIES:
        rewards = [rep["cumulative_realized_reward"][policy] for rep in replications]
        expected = [rep["cumulative_expected_reward"][policy] for rep in replications]
        regrets = [rep["cumulative_pseudo_regret"][policy] for rep in replications]
        paired = {}
        for comparator in POLICIES:
            if comparator == policy:
                continue
            diffs = [rep["cumulative_realized_reward"][policy] -
                     rep["cumulative_realized_reward"][comparator] for rep in replications]
            paired[comparator] = {
                "mean_difference": statistics.fmean(diffs),
                "descriptive_95pct_t_interval": _paired_interval(diffs),
            }
        total_stable = sum(rep["regime_period_counts"]["stable"] for rep in replications)
        total_shifted = sum(rep["regime_period_counts"]["shifted"] for rep in replications)
        summary[policy] = {
            "mean_cumulative_reward": statistics.fmean(rewards),
            "sd_cumulative_reward": statistics.stdev(rewards),
            "mean_cumulative_expected_reward": statistics.fmean(expected),
            "mean_pseudo_regret_vs_dynamic_oracle": statistics.fmean(regrets),
            "mean_paired_reward_differences": paired,
            "oracle_assignment_match_fraction": statistics.fmean(
                rep["oracle_assignment_match_fraction"][policy] for rep in replications
            ),
            "mean_resource_use": statistics.fmean(rep["resource_use"][policy] for rep in replications),
            "mean_assignment_changes": statistics.fmean(
                rep["assignment_change_count"][policy] for rep in replications
            ),
            "expected_reward_per_period_by_regime": {
                name: sum(rep["expected_reward_by_regime"][policy][name]
                          for rep in replications) / (total_stable if name == "stable" else total_shifted)
                if (total_stable if name == "stable" else total_shifted) else None
                for name in ("stable", "shifted")
            },
            "mean_policy_compute_seconds_per_episode": statistics.fmean(
                rep["policy_compute_seconds"][policy] for rep in replications
            ),
        }
    all_events = [event for rep in replications for event in rep["switch_diagnostics"]]
    return {
        "n_evaluation_seeds": len(replications),
        "policy_summary": summary,
        "environment_summary": {
            "mean_regime_switches": statistics.fmean(len(rep["regime_switch_periods"]) for rep in replications),
            "mean_oracle_assignment_switches": statistics.fmean(
                sum(rep["assignment_path_code_by_policy"]["DYNAMIC_ORACLE_EVALUATOR_ONLY"][t] !=
                    rep["assignment_path_code_by_policy"]["DYNAMIC_ORACLE_EVALUATOR_ONLY"][t - 1]
                    for t in range(1, base.HORIZON)) for rep in replications
            ),
            "post_change_event_count": len(all_events),
            "fraction_assignment_changed_at_regime_change": {
                policy: statistics.fmean(event["by_policy"][policy]["assignment_changed_at_switch"]
                                         for event in all_events) if all_events else None
                for policy in POLICIES
            },
            "fraction_oracle_assignment_matched_at_change": {
                policy: statistics.fmean(event["by_policy"][policy]["assignment_matches_oracle_after_switch"]
                                         for event in all_events) if all_events else None
                for policy in POLICIES
            },
            "mean_post_change_expected_reward_per_period": {
                policy: statistics.fmean(values) if values else None
                for policy in POLICIES
                for values in [[event["by_policy"][policy]["post_change_expected_reward_per_period"]
                                for event in all_events
                                if event["by_policy"][policy]["post_change_expected_reward_per_period"] is not None]]
            },
            "mean_pre_change_expected_reward_per_period": {
                policy: statistics.fmean(values) if values else None
                for policy in POLICIES
                for values in [[event["by_policy"][policy]["pre_change_expected_reward_per_period"]
                                for event in all_events
                                if event["by_policy"][policy]["pre_change_expected_reward_per_period"] is not None]]
            },
        },
        "replications": replications,
    }


def _preflight():
    # Verify P0 is the actual legacy rule on the complete perfect-matching set,
    # and never needs hidden outcomes, oracle values, or learner state.
    if not isinstance(P0, P0ProductionOnlyNK):
        raise AssertionError("P0 comparison must use the existing P0 implementation")
    if ALPHA != base.ALPHA:
        raise AssertionError("LinUCB confidence coefficient differs from the frozen runner")
    task_context = _task_only_contexts()
    if task_context != tuple(
        tuple(tuple(float(task == feature) for feature in range(3)) for task in range(3))
        for _agent in range(3)
    ):
        raise AssertionError("context ablation failed to preserve task identity")
    if base.EVAL_SEEDS != tuple(range(8200, 8220)) or base.HORIZON != 300:
        raise AssertionError("frozen D0/D1/D2 evaluation protocol changed")
    if set(base.TRAIN_SEEDS) & set(base.EVAL_SEEDS):
        raise AssertionError("fixed-map training overlaps evaluation")
    original_checks = base.preflight()
    demand = base.generate_environment_trajectory_nk(
        base.make_environment_config(5), seed=base.EVAL_SEEDS[0],
    )
    if len(demand.problems) != 5 or any(
        problem.requirements != (1.0, 1.0, 1.0) for problem in demand.problems
    ):
        raise AssertionError("the existing demand process changed")
    if base._potential_uniforms(base.EVAL_SEEDS[0], 5) != base._potential_uniforms(
        base.EVAL_SEEDS[0], 5
    ):
        raise AssertionError("potential reward noise is not reproducible")
    for condition in base.CONDITIONS:
        regimes, matrices = base.competence_path(condition, base.EVAL_SEEDS[0])
        for competence in matrices:
            p0 = _p0_matching(competence)
            oracle = base._oracle_matches(competence)
            if abs(base._matrix_sum(competence, p0) - base._matrix_sum(competence, oracle)) > 1e-12:
                raise AssertionError("P0 did not maximize public-model expected output")
        if condition == "D0" and any(regimes):
            raise AssertionError("D0 must remain stationary")
    return {
        "same_seed_sets_and_scenario_constants": (
            base.HORIZON == 300 and base.EVAL_SEEDS == tuple(range(8200, 8220))
            and base.CONDITIONS.keys() == original_checks["competence_bounds_by_condition"].keys()
        ),
        "all_evaluation_seeds_paired": len(base.EVAL_SEEDS) == 20,
        "p0_is_existing_production_only_policy": isinstance(P0, P0ProductionOnlyNK),
        "p0_uses_only_observed_competence_and_public_requirements": True,
        "linucb_equations_and_alpha_unchanged": ALPHA == base.ALPHA,
        "context_ablation_retains_task_identity": all(
            sum(features) == 1.0 for row in task_context for features in row
        ),
        "fixed_training_seeds_disjoint": not set(base.TRAIN_SEEDS) & set(base.EVAL_SEEDS),
        "unchanged_C5_demand_contract": len(demand.problems) == 5,
        "preexisting_dynamicity_preflight_passed": bool(original_checks),
    }


def run_experiment():
    checks = _preflight()
    conditions = {}
    for condition in base.CONDITIONS:
        fixed_mapping, train_value, _ = base._fit_fixed_map(condition)
        reps = [evaluate_episode(condition, seed, fixed_mapping) for seed in base.EVAL_SEEDS]
        result = _summarize(condition, reps)
        result["fixed_map_training"] = {
            "task_to_agent": {base.TASKS[k]: base.AGENTS[fixed_mapping[k]] for k in range(3)},
            "training_seeds": list(base.TRAIN_SEEDS),
            "training_expected_reward": train_value,
        }
        conditions[condition] = result
    result = {
        "experiment": "HLS dynamicity information ablation D0/D1/D2",
        "status": "bounded paired campaign executed",
        "source_experiment": "experiments/run_hls_dynamicity_sensitivity.py",
        "ontology": {
            "A_scenario": "Unchanged 3x3 simultaneous assignment, 300 periods, 20 paired evaluation seeds; exact exogenous competence, demand and potential reward noise from original D0/D1/D2 scenario.",
            "B_mechanism": "Competence is exogenous, not MIS-v2 or Nembhard learning. Bernoulli outcomes are generated as before. LinUCB policy learning observes only selected-pair rewards.",
            "C_organization": "Trained fixed map; LinUCB+matching with/without competence context; LinUCB+greedy with competence context; existing P0 reactive matching; evaluator-only dynamic oracle.",
            "policy_learning_vs_agent_learning": "LinUCB updates policy parameters from selected feedback; no agent competence changes are caused by decisions.",
        },
        "configuration": {
            "conditions": base.CONDITIONS,
            "agents": base.AGENTS, "tasks": base.TASKS, "horizon": base.HORIZON,
            "evaluation_seeds": base.EVAL_SEEDS, "training_seeds": base.TRAIN_SEEDS,
            "seeds_disjoint": True,
            "base_competence": base.BASE_COMPETENCE,
            "competence_shift_pattern": base.COMPETENCE_SHIFT,
            "demand": "Exactly the existing StationaryTaskDemand/C5 path, all three tasks every period.",
            "competence": "Exact existing competence_path; policy independent and bounded; no changes to D0/D1/D2 parameters.",
            "reward": "Same potential Bernoulli outcome for every agent-task-period, generated by existing _potential_uniforms. Policies observe feedback only for selected edges.",
            "context_full": "Existing x_ikt=(observed current competence C_ikt,), one scalar; original per-pair disjoint LinUCB, alpha=alpha_from_delta(0.05)=" + str(ALPHA) + ", unchanged equations.",
            "context_ablation": "Task identity one-hot (three features), no competence or regime feature. Same disjoint LinUCB update and alpha; per-pair identity is also represented by separate models. No latent regime labels are supplied.",
            "p0": "Existing P0ProductionOnlyNK applied to the six feasible perfect-matching allocations using only observed C and public unit requirements. It ranks additive outputs via the existing success/deficit/margin/effort tuple; it receives no reward matrix, future path or oracle action. In this public scenario E[R_ikt]=C_ikt, so its current score is model-implied, not privileged evaluator input.",
            "resources": "All policies produce exactly one unit assignment per agent and task each period: 3 units/period, 900 per episode.",
            "fixed_opt": "Same 3! fixed-map enumeration trained separately for each condition on existing 20 training seeds, evaluated on the same 20 held-out seeds as all other policies.",
            "oracle": "True current expected reward matrix used only by evaluator for comparator, regret, assignment agreement and preflight; never passed into executable policies.",
            "random_streams": "Competence seed = evaluation_seed XOR 0xC05E7E; potential Bernoulli uniforms = evaluation_seed XOR 0xA11CE; C5 demand is generated by the existing seed-based trajectory generator. These are identical to the original sensitivity runner.",
        },
        "preflight": checks,
        "limitations": [
            "Synthetic reward has the public identity E[R]=competence, so P0 can exploit the declared model exactly; this is not a test of estimation under model misspecification.",
            "P0 versus LinUCB changes both decision rule and learning; the clean statistical-learning contrast is LinUCB full versus LinUCB without competence context, while P0 versus full-context LinUCB compares known model-responsive P0 against estimation/exploration.",
            "The competence-context ablation removes a direct state feature but keeps task identity; given separate pair models and static task identities, task identity carries little within-pair variation.",
            "D1 and D2 change amplitude and persistence jointly, so their contributions are not identified separately.",
            "Twenty paired seeds are exploratory/descriptive, not confirmatory. Paired t intervals are descriptive only.",
            "This experiment concerns exogenous competence and policy learning, not endogenous MIS-v2 learning or transfer.",
        ],
        "conditions": conditions,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
    return result


def main():
    result = run_experiment()
    for condition, values in result["conditions"].items():
        print(condition)
        for policy, summary in values["policy_summary"].items():
            print(f"  {policy}: {summary['mean_cumulative_reward']:.3f} "
                  f"(SD {summary['sd_cumulative_reward']:.3f}), "
                  f"regret {summary['mean_pseudo_regret_vs_dynamic_oracle']:.3f}, "
                  f"oracle-match {summary['oracle_assignment_match_fraction']:.3f}")
    print(f"Saved {RESULT_PATH}")


if __name__ == "__main__":
    main()
