#!/usr/bin/env python3
"""Paired D0/D1/D2 sensitivity experiment for LinUCB organization policies.

The only experiment-specific dynamics here are exogenous competence-regime
paths. N×K geometry, C5 task emission, LinUCB and bipartite assignment are
reused unchanged. Competence and potential outcomes are generated before any
policy runs, so actions cannot affect either path.
"""

from __future__ import annotations

import itertools
import json
import math
import random
import statistics
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.stats import t as student_t

if __package__:
    from .run_hls_linucb_bipartite_hybrid import greedy_from_scores as greedy_matching
else:  # Direct script execution places only the experiments/ directory on sys.path.
    from run_hls_linucb_bipartite_hybrid import greedy_from_scores as greedy_matching
from hls.hls_lab_nk_assignment import HungarianAssignmentOptimizerNK
from hls.hls_lab_nk_environment import (
    DemandRegimeNK,
    ExogenousEnvironmentConfigNK,
    generate_environment_trajectory_nk,
)
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_linucb_assignment import PairwiseLinUCBAdapterNK
from hls.linucb import alpha_from_delta
from hls.synthetic.c5 import StationaryTaskDemand


OUTPUT_DIR = Path("results/experiments/hls_dynamicity_sensitivity")
RESULT_PATH = OUTPUT_DIR / "results.json"
PLOT_PATH = OUTPUT_DIR / "dynamicity_sensitivity.png"

AGENTS = ("agent_0", "agent_1", "agent_2")
TASKS = ("task_0", "task_1", "task_2")
BASE_COMPETENCE = (
    (0.70, 0.50, 0.35),
    (0.35, 0.70, 0.50),
    (0.50, 0.35, 0.70),
)
# Positive entries favor the forward cycle; negative entries reduce diagonal
# specialization. This pattern is declared from the problem structure, not
# selected using any policy's evaluation reward.
COMPETENCE_SHIFT = (
    (-1.0, 1.0, 0.0),
    (0.0, -1.0, 1.0),
    (1.0, 0.0, -1.0),
)
HORIZON = 300
TRAIN_SEEDS = tuple(range(6100, 6120))
EVAL_SEEDS = tuple(range(8200, 8220))
ALPHA = alpha_from_delta(0.05)
POST_CHANGE_WINDOW = 10

CONDITIONS = {
    "D0": {"amplitude": 0.0, "mean_dwell_periods": None, "switch_probability": 0.0},
    "D1": {"amplitude": 0.15, "mean_dwell_periods": 100, "switch_probability": 0.01},
    "D2": {"amplitude": 0.30, "mean_dwell_periods": 25, "switch_probability": 0.04},
}
POLICIES = (
    "LINUCB_HUNGARIAN",
    "LINUCB_GREEDY_ONLINE",
    "FIXED_OPT_TRAIN",
    "DYNAMIC_ORACLE",
)
PERMUTATIONS = tuple(itertools.permutations(range(3)))
PERMUTATION_TO_ID = {permutation: index for index, permutation in enumerate(PERMUTATIONS)}

ORG = OrganizationConfigNK(
    AGENTS, TASKS, BASE_COMPETENCE, (1.0, 1.0, 1.0), 3.0,
)
PROBLEM = ProblemSpecNK("three_simultaneous_tasks", (1.0, 1.0, 1.0), 3.0)
ASSIGNER = HungarianAssignmentOptimizerNK()


def make_environment_config(horizon: int = HORIZON) -> ExogenousEnvironmentConfigNK:
    """Existing C5 stationary demand: all three task types every period."""
    problem = ProblemSpecNK("all_three_tasks", (1.0, 1.0, 1.0), 3.0)
    regime = DemandRegimeNK("all_tasks_present", (problem,), (1.0,))
    return ExogenousEnvironmentConfigNK(
        StationaryTaskDemand({"all_tasks": 1.0}),
        {"all_tasks": regime}, horizon, resource_budget=3.0,
    )


def competence_path(condition: str, seed: int, horizon: int = HORIZON):
    """Seeded, policy-independent two-regime competence trajectory.

    A two-state geometric dwell process starts in the baseline profile. D1
    changes with expected inter-switch interval 100 periods and amplitude
    0.15; D2 uses 25 periods and amplitude 0.30. The same initial matrix is
    used in all conditions and all values remain in [0,1].
    """
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition {condition!r}")
    spec = CONDITIONS[condition]
    rng = random.Random(seed ^ 0xC05E7E)
    shifted = False
    regimes = []
    matrices = []
    for period in range(horizon):
        if period and rng.random() < spec["switch_probability"]:
            shifted = not shifted
        regimes.append(int(shifted))
        amplitude = spec["amplitude"] if shifted else 0.0
        matrix = tuple(
            tuple(BASE_COMPETENCE[i][k] + amplitude * COMPETENCE_SHIFT[i][k]
                  for k in range(3))
            for i in range(3)
        )
        if any(not 0.0 <= value <= 1.0 for row in matrix for value in row):
            raise AssertionError("generated competence left [0,1]")
        matrices.append(matrix)
    return tuple(regimes), tuple(matrices)


def _potential_uniforms(seed: int, horizon: int):
    # A separate stream pre-generates a potential outcome for every edge and
    # period, shared by every policy and all three conditions for this seed.
    rng = random.Random(seed ^ 0xA11CE)
    return tuple(tuple(tuple(rng.random() for _ in range(3)) for _ in range(3))
                 for _ in range(horizon))


def _realized_reward_matrix(means, uniforms):
    return tuple(tuple(float(uniforms[i][k] < means[i][k]) for k in range(3))
                 for i in range(3))


def _matrix_sum(matrix, matches):
    return sum(matrix[i][k] for i, k in matches)


def _as_permutation(matches):
    by_task = [None] * 3
    for agent, task in matches:
        by_task[task] = agent
    if any(agent is None for agent in by_task):
        raise AssertionError("all three task assignments are required")
    return tuple(by_task)


def _fixed_matches(mapping):
    return tuple(sorted((mapping[task], task) for task in range(3)))


def _oracle_matches(means):
    return ASSIGNER.optimize(means, ORG, PROBLEM).matches


def _fit_fixed_map(condition: str):
    totals = {permutation: 0.0 for permutation in PERMUTATIONS}
    for seed in TRAIN_SEEDS:
        _, matrices = competence_path(condition, seed)
        for matrix in matrices:
            for permutation in PERMUTATIONS:
                totals[permutation] += sum(matrix[permutation[k]][k] for k in range(3))
    best_value = max(totals.values())
    best = min(permutation for permutation, value in totals.items()
               if math.isclose(value, best_value, rel_tol=0.0, abs_tol=1e-12))
    return best, totals[best], totals


def _t_interval(values):
    values = tuple(float(value) for value in values)
    mean = statistics.fmean(values)
    if len(values) < 2:
        return [mean, mean]
    half_width = float(student_t.ppf(0.975, len(values) - 1)) * statistics.stdev(values) / math.sqrt(len(values))
    return [mean - half_width, mean + half_width]


def evaluate_episode(condition: str, seed: int, fixed_mapping, horizon: int = HORIZON):
    demand = generate_environment_trajectory_nk(make_environment_config(horizon), seed=seed)
    regimes, competences = competence_path(condition, seed, horizon)
    uniforms = _potential_uniforms(seed, horizon)
    if len(demand.problems) != horizon or any(
        problem.requirements != (1.0, 1.0, 1.0) for problem in demand.problems
    ):
        raise AssertionError("N×K demand trajectory failed the simultaneous-task contract")

    learners = {
        "LINUCB_HUNGARIAN": PairwiseLinUCBAdapterNK(3, 3, 1, ALPHA),
        "LINUCB_GREEDY_ONLINE": PairwiseLinUCBAdapterNK(3, 3, 1, ALPHA),
    }
    cumulative_reward = {policy: 0.0 for policy in POLICIES}
    cumulative_expected = {policy: 0.0 for policy in POLICIES}
    cumulative_regret = {policy: 0.0 for policy in POLICIES}
    reward_by_regime = {policy: {"stable": 0.0, "shifted": 0.0} for policy in POLICIES}
    expected_by_regime = {policy: {"stable": 0.0, "shifted": 0.0} for policy in POLICIES}
    periods_by_regime = {"stable": 0, "shifted": 0}
    resource_use = {policy: 0 for policy in POLICIES}
    assignment_ids = {policy: [] for policy in POLICIES}
    realized_series = {policy: [] for policy in POLICIES}
    expected_series = {policy: [] for policy in POLICIES}
    regret_series = {policy: [] for policy in POLICIES}
    oracle_series = []
    switch_events = []
    total_solver_seconds = {policy: 0.0 for policy in POLICIES}

    oracle_assignments = []
    for period, (regime, means) in enumerate(zip(regimes, competences)):
        oracle_assignments.append(_oracle_matches(means))
    switches = [period for period in range(1, horizon) if regimes[period] != regimes[period - 1]]
    switch_set = set(switches)

    for period, (regime, means) in enumerate(zip(regimes, competences)):
        observed_matrix = _realized_reward_matrix(means, uniforms[period])
        contexts = tuple(tuple((means[i][k],) for k in range(3)) for i in range(3))

        started = time.perf_counter()
        joint_model = learners["LINUCB_HUNGARIAN"]
        joint_scores = joint_model.score_matrix(contexts)
        joint_matches = ASSIGNER.optimize(joint_scores, ORG, PROBLEM).matches
        total_solver_seconds["LINUCB_HUNGARIAN"] += time.perf_counter() - started
        joint_feedback = {(i, k): observed_matrix[i][k] for i, k in joint_matches}
        joint_model.update_selected(joint_matches, contexts, joint_feedback)

        started = time.perf_counter()
        greedy_model = learners["LINUCB_GREEDY_ONLINE"]
        greedy_scores = greedy_model.score_matrix(contexts)
        greedy_matches = greedy_matching(greedy_scores)
        total_solver_seconds["LINUCB_GREEDY_ONLINE"] += time.perf_counter() - started
        greedy_feedback = {(i, k): observed_matrix[i][k] for i, k in greedy_matches}
        greedy_model.update_selected(greedy_matches, contexts, greedy_feedback)

        fixed = _fixed_matches(fixed_mapping)
        oracle = oracle_assignments[period]
        decisions = {
            "LINUCB_HUNGARIAN": joint_matches,
            "LINUCB_GREEDY_ONLINE": greedy_matches,
            "FIXED_OPT_TRAIN": fixed,
            "DYNAMIC_ORACLE": oracle,
        }
        oracle_expected = _matrix_sum(means, oracle)
        oracle_series.append(oracle_expected)
        regime_name = "shifted" if regime else "stable"
        periods_by_regime[regime_name] += 1
        period_row = {"period": period, "regime": regime_name, "competence": means}
        del period_row  # Detailed trajectories are reconstructed from seed/config.

        for policy, matches in decisions.items():
            realized = _matrix_sum(observed_matrix, matches)
            expected = _matrix_sum(means, matches)
            regret = oracle_expected - expected
            if regret < -1e-10:
                raise AssertionError("policy pseudo-regret against true-mean oracle is negative")
            cumulative_reward[policy] += realized
            cumulative_expected[policy] += expected
            cumulative_regret[policy] += max(0.0, regret)
            reward_by_regime[policy][regime_name] += realized
            expected_by_regime[policy][regime_name] += expected
            resource_use[policy] += len(matches)
            assignment_ids[policy].append(PERMUTATION_TO_ID[_as_permutation(matches)])
            realized_series[policy].append(realized)
            expected_series[policy].append(expected)
            regret_series[policy].append(max(0.0, regret))

    # Per-switch diagnostics: cumulative pseudo-regret and time to the first
    # oracle-matching action in a predeclared 10-period, non-overlapping window.
    for position, switch_period in enumerate(switches):
        next_switch = switches[position + 1] if position + 1 < len(switches) else horizon
        stop = min(switch_period + POST_CHANGE_WINDOW, next_switch, horizon)
        event = {"period": switch_period, "window_periods": stop - switch_period,
                 "by_policy": {}}
        for policy in POLICIES:
            window_regret = sum(regret_series[policy][switch_period:stop])
            recovery = next((t - switch_period for t in range(switch_period, stop)
                             if assignment_ids[policy][t] ==
                             PERMUTATION_TO_ID[_as_permutation(oracle_assignments[t])]), None)
            event["by_policy"][policy] = {
                "pseudo_regret": window_regret,
                "periods_to_first_oracle_assignment": recovery,
                "recovered_within_window": recovery is not None,
            }
        switch_events.append(event)

    # Evaluator-only best fixed map on the full test path, used only to measure
    # the maximum hindsight flexibility opportunity (never passed to policies).
    retrospective = max(
        sum(sum(competences[i][k] for i, k in enumerate(permutation))
            for competences in competences)
        for permutation in PERMUTATIONS
    )
    dynamic_oracle_expected = sum(oracle_series)
    cumulative_expected["RETROSPECTIVE_BEST_FIXED_DIAGNOSTIC"] = retrospective

    return {
        "seed": seed,
        "condition": condition,
        "regime_path_bits": "".join(str(value) for value in regimes),
        "competence_seed": seed ^ 0xC05E7E,
        "reward_noise_seed": seed ^ 0xA11CE,
        "demand_trajectory_seed": demand.seed,
        "regime_switch_periods": switches,
        "oracle_assignment_switches": sum(
            oracle_assignments[t] != oracle_assignments[t - 1] for t in range(1, horizon)
        ),
        "assignment_ids_by_policy": assignment_ids,
        "realized_reward_series_by_policy": realized_series,
        "expected_reward_series_by_policy": expected_series,
        "pseudo_regret_series_by_policy": regret_series,
        "oracle_expected_reward_series": oracle_series,
        "cumulative_realized_reward": cumulative_reward,
        "cumulative_expected_reward": cumulative_expected,
        "cumulative_pseudo_regret": cumulative_regret,
        "reward_by_regime": reward_by_regime,
        "expected_reward_by_regime": expected_by_regime,
        "periods_by_regime": periods_by_regime,
        "resource_use": resource_use,
        "retrospective_best_fixed_expected_reward": retrospective,
        "retrospective_fixed_loss_vs_dynamic_oracle": dynamic_oracle_expected - retrospective,
        "total_reward_matrix_variation_frobenius": sum(
            math.sqrt(sum((competences[t][i][k] - competences[t - 1][i][k]) ** 2
                          for i in range(3) for k in range(3)))
            for t in range(1, horizon)
        ),
        "change_diagnostics": switch_events,
        "linucb_observation_counts": {
            policy: [list(row) for row in learner.observation_counts]
            for policy, learner in learners.items()
        },
        "policy_compute_seconds": total_solver_seconds,
    }


def preflight():
    """Configuration-only checks; deliberately independent of policy results."""
    initial = {}
    regime_optima = {}
    bounds = {}
    for condition, spec in CONDITIONS.items():
        regimes, matrices = competence_path(condition, 20261020)
        initial[condition] = matrices[0]
        bounds[condition] = {
            "minimum": min(v for matrix in matrices for row in matrix for v in row),
            "maximum": max(v for matrix in matrices for row in matrix for v in row),
        }
        regime_optima[condition] = {}
        for regime in (0, 1):
            matrix = tuple(tuple(BASE_COMPETENCE[i][k] +
                                 (spec["amplitude"] * COMPETENCE_SHIFT[i][k] if regime else 0.0)
                                 for k in range(3)) for i in range(3))
            regime_optima[condition]["shifted" if regime else "stable"] = {
                "matching": _as_permutation(_oracle_matches(matrix)),
                "expected_reward": _matrix_sum(matrix, _oracle_matches(matrix)),
            }
    if not (initial["D0"] == initial["D1"] == initial["D2"] == BASE_COMPETENCE):
        raise AssertionError("conditions must share the same initial competencies")
    for condition in ("D1", "D2"):
        amplitude = CONDITIONS[condition]["amplitude"]
        shifted = tuple(tuple(BASE_COMPETENCE[i][k] + amplitude * COMPETENCE_SHIFT[i][k]
                              for k in range(3)) for i in range(3))
        if _oracle_matches(BASE_COMPETENCE) == _oracle_matches(shifted):
            raise AssertionError(f"{condition} must produce a decision-relevant regime change by design")
    return {
        "same_initial_competencies_all_conditions": True,
        "competence_bounds_by_condition": bounds,
        "oracle_assignment_by_static_regime": regime_optima,
        "D1_and_D2_change_oracle_assignment": True,
        "demand_all_three_tasks_each_period": True,
        "policy_results_used_for_configuration_selection": False,
    }


def _summarize_condition(condition, replications):
    def pooled_reward_per_period(field, policy, regime):
        total = sum(rep[field][policy][regime] for rep in replications)
        count = sum(rep["periods_by_regime"][regime] for rep in replications)
        return total / count if count else None

    summary = {}
    for policy in POLICIES:
        rewards = [rep["cumulative_realized_reward"][policy] for rep in replications]
        expected = [rep["cumulative_expected_reward"][policy] for rep in replications]
        regrets = [rep["cumulative_pseudo_regret"][policy] for rep in replications]
        resources = [rep["resource_use"][policy] for rep in replications]
        summary[policy] = {
            "mean_cumulative_reward": statistics.fmean(rewards),
            "sd_cumulative_reward": statistics.stdev(rewards),
            "mean_cumulative_reward_95pct_t_interval": _t_interval(rewards),
            "mean_cumulative_expected_reward": statistics.fmean(expected),
            "mean_pseudo_regret_vs_dynamic_oracle": statistics.fmean(regrets),
            "sd_pseudo_regret_vs_dynamic_oracle": statistics.stdev(regrets),
            "mean_paired_reward_difference_vs_fixed": statistics.fmean(
                rep["cumulative_realized_reward"][policy] -
                rep["cumulative_realized_reward"]["FIXED_OPT_TRAIN"]
                for rep in replications
            ),
            "paired_difference_vs_fixed_95pct_t_interval": _t_interval([
                rep["cumulative_realized_reward"][policy] -
                rep["cumulative_realized_reward"]["FIXED_OPT_TRAIN"]
                for rep in replications
            ]),
            "mean_resource_use": statistics.fmean(resources),
            "mean_compute_seconds_per_episode": statistics.fmean(
                rep["policy_compute_seconds"][policy] for rep in replications
            ),
            "reward_by_regime_mean_per_period": {
                regime: pooled_reward_per_period("reward_by_regime", policy, regime)
                for regime in ("stable", "shifted")
            },
            "expected_reward_by_regime_mean_per_period": {
                regime: pooled_reward_per_period("expected_reward_by_regime", policy, regime)
                for regime in ("stable", "shifted")
            },
            "fraction_periods_matching_dynamic_oracle": statistics.fmean(
                sum(rep["assignment_ids_by_policy"][policy][t] ==
                    rep["assignment_ids_by_policy"]["DYNAMIC_ORACLE"][t]
                    for t in range(len(rep["assignment_ids_by_policy"][policy]))) / HORIZON
                for rep in replications
            ),
        }
    return {
        "condition": condition,
        "n_evaluation_seeds": len(replications),
        "policy_summary": summary,
        "environment_summary": {
            "mean_competence_regime_switches": statistics.fmean(
                len(rep["regime_switch_periods"]) for rep in replications
            ),
            "mean_oracle_assignment_switches": statistics.fmean(
                rep["oracle_assignment_switches"] for rep in replications
            ),
            "share_paths_with_oracle_assignment_switch": statistics.fmean(
                rep["oracle_assignment_switches"] > 0 for rep in replications
            ),
            "mean_reward_matrix_variation_frobenius": statistics.fmean(
                rep["total_reward_matrix_variation_frobenius"] for rep in replications
            ),
            "mean_retrospective_best_fixed_loss_vs_oracle": statistics.fmean(
                rep["retrospective_fixed_loss_vs_dynamic_oracle"] for rep in replications
            ),
            "mean_post_change_pseudo_regret_by_policy": {
                policy: statistics.fmean(
                    event["by_policy"][policy]["pseudo_regret"]
                    for rep in replications for event in rep["change_diagnostics"]
                ) if any(rep["change_diagnostics"] for rep in replications) else None
                for policy in POLICIES
            },
            "mean_post_change_recovery_periods_by_policy": {
                policy: statistics.fmean(
                    event["by_policy"][policy]["periods_to_first_oracle_assignment"]
                    for rep in replications for event in rep["change_diagnostics"]
                    if event["by_policy"][policy]["periods_to_first_oracle_assignment"] is not None
                ) if any(event["by_policy"][policy]["periods_to_first_oracle_assignment"] is not None
                         for rep in replications for event in rep["change_diagnostics"]) else None
                for policy in POLICIES
            },
            "post_change_recovery_fraction_by_policy": {
                policy: statistics.fmean(
                    event["by_policy"][policy]["recovered_within_window"]
                    for rep in replications for event in rep["change_diagnostics"]
                ) if any(rep["change_diagnostics"] for rep in replications) else None
                for policy in POLICIES
            },
            "post_change_event_count": sum(len(rep["change_diagnostics"]) for rep in replications),
        },
        "time_series_mean_cumulative_realized_reward": {
            policy: [statistics.fmean(
                sum(rep["realized_reward_series_by_policy"][policy][:t + 1])
                for rep in replications
            ) for t in range(HORIZON)]
            for policy in POLICIES
        },
        "replications": replications,
    }


def _plot(result):
    colors = {
        "LINUCB_HUNGARIAN": "#2878B5",
        "LINUCB_GREEDY_ONLINE": "#F39B7F",
        "FIXED_OPT_TRAIN": "#3A923A",
        "DYNAMIC_ORACLE": "#7B4AB5",
    }
    labels = {
        "LINUCB_HUNGARIAN": "LinUCB + matching",
        "LINUCB_GREEDY_ONLINE": "LinUCB + greedy",
        "FIXED_OPT_TRAIN": "Fixed map (train)",
        "DYNAMIC_ORACLE": "Dynamic oracle (expected)",
    }
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
    periods = np.arange(1, HORIZON + 1)
    for axis, condition in zip(axes, ("D0", "D1", "D2")):
        data = result["conditions"][condition]
        for policy in POLICIES:
            series = np.asarray(data["time_series_mean_cumulative_realized_reward"][policy])
            axis.plot(periods, series, label=labels[policy], color=colors[policy], linewidth=1.8)
        axis.set_title(f"{condition}: amplitude={CONDITIONS[condition]['amplitude']}, "
                       f"mean dwell={CONDITIONS[condition]['mean_dwell_periods'] or '∞'}")
        axis.set_xlabel("Period")
        axis.grid(alpha=0.25)
    axes[0].set_ylabel("Mean cumulative reward (20 paired seeds)")
    handles, labels_ = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels_, loc="lower center", ncol=4, frameon=False)
    fig.suptitle("HLS dynamicity sensitivity: paired cumulative performance")
    fig.tight_layout(rect=(0, 0.12, 1, 0.93))
    fig.savefig(PLOT_PATH, dpi=160)
    plt.close(fig)


def run_experiment():
    if len(EVAL_SEEDS) != 20 or len(set(TRAIN_SEEDS) & set(EVAL_SEEDS)):
        raise AssertionError("the protocol requires 20 disjoint evaluation seeds")
    checks = preflight()
    conditions = {}
    for condition in CONDITIONS:
        fixed_mapping, train_value, train_totals = _fit_fixed_map(condition)
        reps = [evaluate_episode(condition, seed, fixed_mapping) for seed in EVAL_SEEDS]
        condition_result = _summarize_condition(condition, reps)
        condition_result["fixed_map_training"] = {
            "task_to_agent": {TASKS[k]: AGENTS[fixed_mapping[k]] for k in range(3)},
            "permutation_id": PERMUTATION_TO_ID[fixed_mapping],
            "training_expected_reward": train_value,
            "training_seed_count": len(TRAIN_SEEDS),
            "training_horizon_per_seed": HORIZON,
            "training_totals_by_permutation_id": {
                str(PERMUTATION_TO_ID[permutation]): value
                for permutation, value in train_totals.items()
            },
        }
        conditions[condition] = condition_result
    result = {
        "experiment": "HLS dynamicity sensitivity D0/D1/D2",
        "protocol_status": "executed bounded paired evaluation",
        "ontology": {
            "A_scenario": "3 agents × 3 simultaneous unit-demand tasks; N×K resources; C5 stationary all-tasks-present demand; competence profile is exogenous and paired across policies.",
            "B_mechanism": "Competencies are exogenous [0,1]-bounded two-regime processes. MIS-v2 and Nembhard are disabled. LinUCB learns reward-prediction parameters only; it does not change agent competence.",
            "C_organization": "Existing pairwise disjoint LinUCB scores are combined with either the existing bipartite optimizer or a deterministic online greedy matcher; fixed map is trained offline; dynamic true-mean oracle is evaluator-only.",
            "policy_learning_vs_agent_learning": "LinUCB model state updates from selected feedback; agent competence follows the seeded scenario process independently of decisions.",
        },
        "configuration": {
            "agents": list(AGENTS), "tasks": list(TASKS), "periods_per_execution": HORIZON,
            "evaluation_seeds": list(EVAL_SEEDS), "training_seeds": list(TRAIN_SEEDS),
            "train_evaluation_disjoint": True,
            "conditions": CONDITIONS,
            "base_competence": BASE_COMPETENCE,
            "shift_pattern": COMPETENCE_SHIFT,
            "initial_competence_same_all_conditions": True,
            "competence_transition": "At each period after t=0, toggle stable/shifted regime with condition-specific probability p; geometric mean dwell is 1/p. C_t=C_base in stable regime; C_t=C_base+amplitude*S in shifted regime. Seeded and policy-independent.",
            "demand": "Existing N×K/C5 StationaryTaskDemand and generate_environment_trajectory_nk; all three task types are present each period, same seed/demand path for each policy and condition.",
            "reward_mean": "mu[i,k,t] = current exogenous competence C[i,k,t].",
            "reward_observation": "Bernoulli(mu) potential outcome for every pair-period, pre-generated from a separate coordinate-seeded stream and shared across policies and D conditions; selected policies receive only assigned-pair feedback.",
            "contexts": "One observed scalar context x[i,k,t]=C[i,k,t] per agent-task pair. For each pair, expected reward is linear theta*x with theta=1; LinUCB equations and alpha_from_delta(0.05) are unchanged.",
            "resource_contract": "Exactly three unit assignments per period; each agent and each task at most once; collective and individual unit capacity 1; equal resource use for all methods.",
            "fixed_policy": "Enumerate all 3! fixed task-to-agent maps and maximize total expected reward on 20 distinct 300-period training trajectories for each condition; test only on evaluation seeds.",
            "compact_result_encoding": "Each evaluation replication stores its exogenous regime path as 0/1 bits, each assignment as one digit 0–5 indexing the permutation list in this configuration, and each realized per-period reward as one digit 0–3. Aggregate time series and per-seed metrics are also stored; other period series are reproducible from the runner.",
            "oracle": "At each period maximize the evaluator-only true expected reward matrix using the existing bipartite optimizer. No policy sees the oracle or future regime path.",
            "adaptation_cost": f"At each exogenous regime switch, report pseudo-regret and periods to first oracle matching in a predeclared window of at most {POST_CHANGE_WINDOW} periods, truncated at the next switch or horizon.",
            "solver": "SciPy linear_sum_assignment; SciPy " + scipy.__version__,
        },
        "preflight": checks,
        "conditions": conditions,
        "limitations": [
            "Synthetic exogenous competence regimes are not industrial/empirical data and are not MIS-v2 or Nembhard learning.",
            "The competence path is observed perfectly by both online LinUCB policies; no state-estimation error is tested.",
            "The fixed baseline is trained with full expected-reward trajectories, while LinUCB observes selected pair outcomes only; this is intentionally a strong offline fixed comparator with a different training information budget.",
            "The simultaneous LinUCB adapter applies multiple selected-pair updates per period; single-play LinUCB guarantees do not automatically apply.",
            "The dynamic oracle is an evaluator-only true-mean reference, not an executable information-feasible policy.",
            "Twenty evaluation seeds support a bounded sensitivity comparison, not a confirmatory generalization claim.",
            "The change process is two-state Markov with specified mean dwell, not a deterministic periodic schedule; exact paths are seed-reproducible.",
            "Computation times are local diagnostics, not portable runtime claims.",
        ],
    }
    for condition_result in result["conditions"].values():
        for replication in condition_result["replications"]:
            replication["assignment_path_code_by_policy"] = {
                policy: "".join(str(value) for value in path)
                for policy, path in replication.pop("assignment_ids_by_policy").items()
            }
            replication["realized_reward_digit_series_by_policy"] = {
                policy: "".join(str(int(value)) for value in path)
                for policy, path in replication.pop("realized_reward_series_by_policy").items()
            }
            replication.pop("expected_reward_series_by_policy")
            replication.pop("pseudo_regret_series_by_policy")
            replication.pop("oracle_expected_reward_series")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
    _plot(result)
    return result


def main():
    result = run_experiment()
    for condition, details in result["conditions"].items():
        env = details["environment_summary"]
        print(f"{condition}: switches={env['mean_competence_regime_switches']:.2f}, "
              f"oracle assignment switches={env['mean_oracle_assignment_switches']:.2f}, "
              f"retrospective fixed loss={env['mean_retrospective_best_fixed_loss_vs_oracle']:.3f}")
        for policy, values in details["policy_summary"].items():
            print(f"  {policy}: reward={values['mean_cumulative_reward']:.3f} "
                  f"(SD {values['sd_cumulative_reward']:.3f}), "
                  f"pseudo-regret={values['mean_pseudo_regret_vs_dynamic_oracle']:.3f}, "
                  f"resources={values['mean_resource_use']:.0f}")
    print(f"Saved {RESULT_PATH} and {PLOT_PATH}")


if __name__ == "__main__":
    main()
