#!/usr/bin/env python3
"""Matched train/test pilot for contextual LinUCB with joint N×K assignment."""

from __future__ import annotations

import itertools
import json
import random
import statistics
import time
from pathlib import Path

import scipy

from hls.hls_lab_nk_assignment import HungarianAssignmentOptimizerNK
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_linucb_assignment import PairwiseLinUCBAdapterNK
from hls.linucb import alpha_from_delta


OUTPUT = Path("results/experiments/hls_linucb_bipartite_hybrid/results.json")
AGENTS = ("agent_0", "agent_1", "agent_2")
TASKS = ("task_0", "task_1", "task_2")
COMPETENCE = ((0.95, 0.55, 0.35), (0.40, 0.90, 0.60), (0.65, 0.30, 0.92))
TRAIN_SEEDS = tuple(range(7100, 7108))
EVAL_SEEDS = tuple(range(8200, 8210))
TRAIN_HORIZON = 36
EVAL_HORIZON = 36
N_MODES = 3
ALPHA = alpha_from_delta(0.05)
FEATURES = 1 + N_MODES
RESOURCE_BUDGET = 3.0
ORG = OrganizationConfigNK(AGENTS, TASKS, COMPETENCE, (1.0,) * 3, RESOURCE_BUDGET)
PROBLEM = ProblemSpecNK("three simultaneous tasks", (1.0,) * 3, RESOURCE_BUDGET)
ASSIGNER = HungarianAssignmentOptimizerNK()
POLICIES = (
    "LINUCB_HUNGARIAN",
    "GREEDY_SAME_LINUCB_SCORES",
    "LINUCB_GREEDY_ONLINE",
    "ORACLE_HUNGARIAN",
    "BEST_FIXED_TRAIN",
)


def reward_coefficients():
    """Synthetic, fixed pair coefficients; hidden from every non-oracle policy."""
    result = []
    for i in range(len(AGENTS)):
        row = []
        for k in range(len(TASKS)):
            base = 0.20 + 0.55 * COMPETENCE[i][k]
            mode_effects = tuple(0.12 * (((i + 2 * k + mode) % 3) - 1)
                                 for mode in range(N_MODES))
            row.append((base, *mode_effects))
        result.append(tuple(row))
    return tuple(result)


THETA_TRUE = reward_coefficients()


def mode_trajectory(seed: int, horizon: int):
    """Reproducible three-state contextual demand regime with persistence."""
    rng = random.Random(seed)
    mode = rng.randrange(N_MODES)
    path = [mode]
    for _ in range(horizon - 1):
        if rng.random() >= 0.70:
            mode = rng.choice(tuple(candidate for candidate in range(N_MODES)
                                    if candidate != mode))
        path.append(mode)
    return tuple(path)


def contexts_for_mode(mode: int):
    context = (1.0, *(1.0 if j == mode else 0.0 for j in range(N_MODES)))
    return tuple(tuple(context for _ in TASKS) for _ in AGENTS)


def true_reward_matrix(mode: int):
    context = (1.0, *(1.0 if j == mode else 0.0 for j in range(N_MODES)))
    rewards = tuple(
        tuple(sum(weight * feature for weight, feature in zip(THETA_TRUE[i][k], context))
              for k in range(len(TASKS)))
        for i in range(len(AGENTS))
    )
    if any(not 0.0 <= value <= 1.0 for row in rewards for value in row):
        raise AssertionError("latent reward fell outside LinUCB's [0,1] domain")
    return rewards


def training_data():
    episodes = []
    for seed in TRAIN_SEEDS:
        modes = mode_trajectory(seed, TRAIN_HORIZON)
        matrices = tuple(true_reward_matrix(mode) for mode in modes)
        episodes.append({"seed": seed, "mode_sequence": modes, "reward_matrices": matrices})
    return tuple(episodes)


def best_fixed_mapping(train_episodes):
    started = time.perf_counter()
    candidates = []
    for permutation in itertools.permutations(range(len(AGENTS))):
        value = sum(
            matrix[permutation[task]][task]
            for episode in train_episodes for matrix in episode["reward_matrices"]
            for task in range(len(TASKS))
        )
        candidates.append((value, permutation))
    best = max(value for value, _ in candidates)
    mapping = min(permutation for value, permutation in candidates if abs(value - best) <= 1e-12)
    return mapping, best, time.perf_counter() - started


def greedy_from_scores(scores):
    edges = sorted(
        ((float(scores[i][j]), i, j) for i in range(len(AGENTS)) for j in range(len(TASKS))),
        key=lambda edge: (-edge[0], edge[1], edge[2]),
    )
    selected, used_agents, used_tasks = [], set(), set()
    for _, agent, task in edges:
        if len(selected) >= int(RESOURCE_BUDGET):
            break
        if agent not in used_agents and task not in used_tasks:
            selected.append((agent, task))
            used_agents.add(agent)
            used_tasks.add(task)
    return tuple(sorted(selected))


def _sum_rewards(reward_matrix, matches):
    return sum(reward_matrix[i][j] for i, j in matches)


def _as_matches(matches):
    return [{"agent": AGENTS[i], "task": TASKS[j]} for i, j in matches]


def evaluate_episode(seed: int, fixed_mapping):
    modes = mode_trajectory(seed, EVAL_HORIZON)
    hybrid_model = PairwiseLinUCBAdapterNK(len(AGENTS), len(TASKS), FEATURES, ALPHA)
    greedy_model = PairwiseLinUCBAdapterNK(len(AGENTS), len(TASKS), FEATURES, ALPHA)
    cumulative = {policy: 0.0 for policy in POLICIES}
    cumulative_regret = {policy: 0.0 for policy in POLICIES}
    resource_use = {policy: 0 for policy in POLICIES}
    compute_seconds = {policy: 0.0 for policy in POLICIES}
    trace = []

    for period, mode in enumerate(modes):
        contexts = contexts_for_mode(mode)
        rewards = true_reward_matrix(mode)

        # Main hybrid: only LinUCB scores are passed to the matching optimizer.
        started = time.perf_counter()
        hybrid_scores = hybrid_model.score_matrix(contexts)
        hybrid_assignment = ASSIGNER.optimize(hybrid_scores, ORG, PROBLEM)
        hybrid_matches = hybrid_assignment.matches
        hybrid_observed = {(i, j): rewards[i][j] for i, j in hybrid_matches}
        hybrid_model.update_selected(hybrid_matches, contexts, hybrid_observed)
        compute_seconds["LINUCB_HUNGARIAN"] += time.perf_counter() - started

        # Exact-score greedy ablation: same score matrix as the hybrid this
        # period; counterfactual and deliberately does not receive feedback.
        started = time.perf_counter()
        greedy_same_matches = greedy_from_scores(hybrid_scores)
        compute_seconds["GREEDY_SAME_LINUCB_SCORES"] += time.perf_counter() - started

        # A second, independently updated online LinUCB+greedy organization.
        started = time.perf_counter()
        greedy_scores = greedy_model.score_matrix(contexts)
        greedy_online_matches = greedy_from_scores(greedy_scores)
        greedy_observed = {(i, j): rewards[i][j] for i, j in greedy_online_matches}
        greedy_model.update_selected(greedy_online_matches, contexts, greedy_observed)
        compute_seconds["LINUCB_GREEDY_ONLINE"] += time.perf_counter() - started

        # Full-information reference is isolated to the explicitly named oracle.
        started = time.perf_counter()
        oracle_matches = ASSIGNER.optimize(rewards, ORG, PROBLEM).matches
        compute_seconds["ORACLE_HUNGARIAN"] += time.perf_counter() - started
        started = time.perf_counter()
        fixed_matches = tuple(sorted((fixed_mapping[task], task)
                                     for task in range(len(TASKS))))
        compute_seconds["BEST_FIXED_TRAIN"] += time.perf_counter() - started

        decisions = {
            "LINUCB_HUNGARIAN": hybrid_matches,
            "GREEDY_SAME_LINUCB_SCORES": greedy_same_matches,
            "LINUCB_GREEDY_ONLINE": greedy_online_matches,
            "ORACLE_HUNGARIAN": oracle_matches,
            "BEST_FIXED_TRAIN": fixed_matches,
        }
        oracle_reward = _sum_rewards(rewards, oracle_matches)
        period_rewards = {policy: _sum_rewards(rewards, pairs) for policy, pairs in decisions.items()}
        for policy, pairs in decisions.items():
            cumulative[policy] += period_rewards[policy]
            cumulative_regret[policy] += oracle_reward - period_rewards[policy]
            resource_use[policy] += len(pairs)

        trace.append({
            "period": period,
            "context_mode": mode,
            "context_features_by_pair": [[list(contexts[i][j]) for j in range(len(TASKS))]
                                          for i in range(len(AGENTS))],
            "assignments": {policy: _as_matches(pairs) for policy, pairs in decisions.items()},
            "linucb_hybrid_scores_before": [list(row) for row in hybrid_scores],
            "linucb_greedy_scores_before": [list(row) for row in greedy_scores],
            "true_rewards_evaluator_only": [list(row) for row in rewards],
            "observed_rewards_hybrid_selected_only": [
                {"agent": AGENTS[i], "task": TASKS[j], "reward": reward}
                for (i, j), reward in sorted(hybrid_observed.items())
            ],
            "observed_rewards_greedy_online_selected_only": [
                {"agent": AGENTS[i], "task": TASKS[j], "reward": reward}
                for (i, j), reward in sorted(greedy_observed.items())
            ],
            "period_rewards": period_rewards,
            "period_oracle_regret": {policy: oracle_reward - value
                                     for policy, value in period_rewards.items()},
            "resource_use": {policy: len(pairs) for policy, pairs in decisions.items()},
            "hybrid_theta_after": [[list(hybrid_model.coefficient_estimates[i][j])
                                    for j in range(len(TASKS))] for i in range(len(AGENTS))],
            "hybrid_observation_counts_after": [list(row) for row in hybrid_model.observation_counts],
            "greedy_theta_after": [[list(greedy_model.coefficient_estimates[i][j])
                                    for j in range(len(TASKS))] for i in range(len(AGENTS))],
            "greedy_observation_counts_after": [list(row) for row in greedy_model.observation_counts],
        })

    return {
        "seed": seed,
        "mode_sequence": list(modes),
        "cumulative_reward": cumulative,
        "cumulative_oracle_regret": cumulative_regret,
        "resource_use": resource_use,
        "computation_seconds": compute_seconds,
        "final_hybrid_coefficients": hybrid_model.coefficient_estimates,
        "final_hybrid_observation_counts": hybrid_model.observation_counts,
        "final_greedy_coefficients": greedy_model.coefficient_estimates,
        "final_greedy_observation_counts": greedy_model.observation_counts,
        "trace": trace,
    }


def run_experiment():
    train = training_data()
    fixed_mapping, fixed_train_reward, fixed_fit_seconds = best_fixed_mapping(train)
    replications = [evaluate_episode(seed, fixed_mapping) for seed in EVAL_SEEDS]
    summaries = {}
    for policy in POLICIES:
        rewards = [rep["cumulative_reward"][policy] for rep in replications]
        regrets = [rep["cumulative_oracle_regret"][policy] for rep in replications]
        resource = [rep["resource_use"][policy] for rep in replications]
        timings = [rep["computation_seconds"][policy] for rep in replications]
        summaries[policy] = {
            "mean_cumulative_reward": statistics.fmean(rewards),
            "sd_cumulative_reward": statistics.stdev(rewards),
            "mean_cumulative_regret_vs_oracle": statistics.fmean(regrets),
            "sd_cumulative_regret_vs_oracle": statistics.stdev(regrets),
            "mean_resource_use": statistics.fmean(resource),
            "mean_computation_seconds_per_episode": statistics.fmean(timings),
        }
    return {
        "experiment": "HLS LinUCB × bipartite assignment hybrid: independent train/test trajectories",
        "ontology": {
            "A_scenario": "3 heterogeneous agents and 3 simultaneous tasks; each task has unit demand each period; three observable contextual demand modes; identical seeded evaluation paths and unit resource constraints.",
            "B_mechanism": "Pairwise disjoint LinUCB updates contextual reward coefficients from selected agent-task outcomes only. Agent competence is fixed and only shapes latent reward coefficients; no competence learning or transfer.",
            "C_organization": "LinUCB UCB-score matrix fed to joint bipartite optimizer. Greedy same-score counterfactual isolates matching, a separate online LinUCB+greedy run is also reported, oracle uses true current rewards, and fixed assignment is optimized on separate training trajectories.",
            "policy_learning_vs_agent_learning": "LinUCB estimator state changes; physical competence remains constant.",
        },
        "configuration": {
            "agents": list(AGENTS), "tasks": list(TASKS), "competence_agent_by_task": [list(row) for row in COMPETENCE],
            "training_seeds": list(TRAIN_SEEDS), "training_horizon": TRAIN_HORIZON,
            "evaluation_seeds": list(EVAL_SEEDS), "evaluation_horizon": EVAL_HORIZON,
            "feature_vector": "[intercept, context_mode_0, context_mode_1, context_mode_2] per agent-task pair",
            "context_process": "three-state Markov-like process: seeded initial mode; each next period stays with probability .70, otherwise moves uniformly to one of the other modes",
            "reward_model_evaluator_only": "r_ik(x)=theta_ik·x, theta intercept=.20+.55*competence[i,k], mode coefficient=.12*(((i+2*k+mode)%3)-1); deterministic, in [0,1], unknown to policies",
            "latent_reward_coefficients_evaluator_only": [[list(THETA_TRUE[i][k]) for k in range(len(TASKS))]
                                                          for i in range(len(AGENTS))],
            "linucb": "existing LinUCBDisjoint, one single-arm disjoint model per agent-task pair; alpha=alpha_from_delta(.05); all pair contexts are observed; only selected-pair rewards update each model after the simultaneous matching",
            "batch_feedback_boundary": "one simultaneous matching then one observed reward per selected pair; updates are applied after the period. This is a multiple-play/batched composition of the single-play LinUCB update, not the original one-action-per-round protocol or its guarantee.",
            "resource_contract": "unit assignment per matched pair; agent and task each at most once; individual limits=1, collective and problem budget=3; all policies share this contract",
            "fixed_baseline": "single one-to-one map selected by enumerating all 3! mappings and maximizing summed reward over training trajectories; evaluated only on disjoint evaluation seeds",
            "greedy_same_scores": "counterfactual greedy matching on the exact score matrix produced by the main LinUCB-Hungarian learner at that period; does not feed counterfactual rewards into that learner",
            "oracle": "Hungarian optimizer on the evaluator-only true reward matrix; not deployable and never used for LinUCB updates",
            "solver": "SciPy linear_sum_assignment (modified Jonker–Volgenant backend), SciPy " + scipy.__version__,
        },
        "fixed_training_data": [
            {"seed": episode["seed"], "mode_sequence": list(episode["mode_sequence"]),
             "reward_matrices_evaluator_only": [[list(row) for row in matrix]
                                                  for matrix in episode["reward_matrices"]]}
            for episode in train
        ],
        "fixed_mapping": {TASKS[task]: AGENTS[fixed_mapping[task]] for task in range(len(TASKS))},
        "fixed_mapping_training_reward": fixed_train_reward,
        "fixed_mapping_training_fit_seconds": fixed_fit_seconds,
        "summary": summaries,
        "replications": replications,
        "limitations": [
            "This is a synthetic contextual reward model, not empirical task/agent data.",
            "The hybrid uses a simultaneous multiple-play/batched update of per-pair disjoint LinUCB models; published single-play guarantees do not transfer automatically.",
            "The exact-score greedy row is a counterfactual matching ablation sharing the hybrid's scores; it is not an independently updated online policy. A separate LinUCB+greedy online policy is included as well.",
            "The true-reward oracle is evaluator-only and not a deployable policy.",
            "The fixed map has full reward labels on training trajectories but is evaluated on disjoint trajectories; its training information differs from selected-only LinUCB feedback.",
            "Competence is constant, there is no learning-by-doing or transfer, and all assignments consume identical unit resources.",
            "Computation times are local diagnostics, not portable performance claims.",
        ],
    }


def main():
    result = run_experiment()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
    for policy, values in result["summary"].items():
        print(f"{policy}: reward={values['mean_cumulative_reward']:.4f} "
              f"(SD {values['sd_cumulative_reward']:.4f}), "
              f"regret={values['mean_cumulative_regret_vs_oracle']:.4f}, "
              f"resources={values['mean_resource_use']:.1f}, "
              f"sec/episode={values['mean_computation_seconds_per_episode']:.6f}")
    print(f"Fixed map on training trajectories: {result['fixed_mapping']}")
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
