#!/usr/bin/env python3
"""Paired contextual-agent selection comparison: LinUCB, EXP3 and controls."""

from __future__ import annotations

import argparse
import itertools
import json
import random
import statistics
import time
from pathlib import Path
from types import SimpleNamespace

from hls.exp3 import Exp3, gamma_for_horizon
from hls.linucb import LinUCBDisjoint, alpha_from_delta
from hls.synthetic.c5 import NonStationaryTaskDemand
from hls.synthetic.state import WorldState


AGENT_IDS = ("agent_0", "agent_1", "agent_2")
TASK_IDS = ("task_0", "task_1", "task_2")
# Rows are agents; columns are fixed task competencies / success probabilities.
COMPETENCE = (
    (0.85, 0.20, 0.20),
    (0.20, 0.85, 0.20),
    (0.20, 0.20, 0.85),
)


def _mean(values):
    return statistics.fmean(values)


def _sd(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def demand_process(horizon: int) -> NonStationaryTaskDemand:
    distributions = {}
    phase_distributions = (
        {0: 0.70, 1: 0.20, 2: 0.10},
        {0: 0.10, 1: 0.20, 2: 0.70},
        {0: 0.20, 1: 0.70, 2: 0.10},
    )
    for period in range(horizon):
        phase = min(2, (3 * period) // horizon)
        distributions[period] = {
            TASK_IDS[task]: probability
            for task, probability in phase_distributions[phase].items()
        }
    return NonStationaryTaskDemand(distributions)


def generate_trajectory(seed: int, horizon: int) -> dict:
    """Generate the observable task path and evaluator-only potential outcomes."""
    process = demand_process(horizon)
    task_rng = random.Random(seed)
    reward_rng = random.Random(1_000_000 + seed)
    state = WorldState(COMPETENCE, time=0)
    history = []
    contexts = []
    for period in range(horizon):
        task = process.sample_task(period, state, history, task_rng)
        history.append(SimpleNamespace(task=task))
        contexts.append(TASK_IDS.index(task))
    potential_rewards = [
        tuple(float(reward_rng.random() < COMPETENCE[agent][task])
              for agent in range(len(AGENT_IDS)))
        for task in contexts
    ]
    return {"seed": seed, "contexts": contexts, "potential_rewards": potential_rewards}


def _best_fixed_map(contexts: list[int], potential_rewards: list[tuple[float, ...]]) -> tuple[tuple[int, ...], float]:
    """Hindsight optimum over fixed maps task->agent; evaluator-only reference."""
    best_mapping: tuple[int, ...] | None = None
    best_return = float("-inf")
    for mapping in itertools.product(range(len(AGENT_IDS)), repeat=len(TASK_IDS)):
        total = sum(potential_rewards[t][mapping[context]] for t, context in enumerate(contexts))
        if total > best_return:
            best_mapping, best_return = tuple(mapping), total
    assert best_mapping is not None
    return best_mapping, best_return


def _policy_expected_regret(choices, contexts, oracle_means):
    return sum(max(means[context]) - means[context][arm]
               for arm, context, means in zip(choices, contexts, oracle_means))


def _run_replication(seed: int, horizon: int, alpha: float, delta: float) -> dict:
    trajectory = generate_trajectory(seed, horizon)
    contexts = trajectory["contexts"]
    potential_rewards = trajectory["potential_rewards"]
    exp3 = Exp3(len(AGENT_IDS), gamma_for_horizon(len(AGENT_IDS), horizon))
    linucb = LinUCBDisjoint(len(AGENT_IDS), len(TASK_IDS), alpha)
    exp3_rng = random.Random(2_000_000 + seed)
    uniform_rng = random.Random(3_000_000 + seed)

    returns = {name: 0.0 for name in (
        "LINUCB", "EXP3", "UNIFORM", "CONTEXTUAL_ORACLE"
    )}
    choices = {name: [] for name in returns}
    pseudo_regrets = {name: 0.0 for name in returns}
    times = {name: 0.0 for name in ("LINUCB", "EXP3", "UNIFORM")}
    mapping, best_fixed_map_return = _best_fixed_map(contexts, potential_rewards)
    best_fixed_agent_return = max(
        sum(outcomes[agent] for outcomes in potential_rewards)
        for agent in range(len(AGENT_IDS))
    )
    trace = []

    for period, (task, rewards) in enumerate(zip(contexts, potential_rewards)):
        context = tuple(1.0 if feature == task else 0.0
                        for feature in range(len(TASK_IDS)))
        arm_contexts = (context,) * len(AGENT_IDS)
        mean_rewards = tuple(COMPETENCE[agent][task] for agent in range(len(AGENT_IDS)))

        linucb_scores = linucb.scores(arm_contexts)
        started = time.perf_counter()
        linucb_arm = linucb.select(arm_contexts)
        linucb_reward = rewards[linucb_arm]
        linucb.observe_reward(linucb_reward)
        times["LINUCB"] += time.perf_counter() - started

        exp3_probabilities = exp3.probabilities
        started = time.perf_counter()
        exp3_arm = exp3.select(exp3_rng)
        exp3_reward = rewards[exp3_arm]
        exp3.observe_reward(exp3_reward)
        times["EXP3"] += time.perf_counter() - started

        started = time.perf_counter()
        uniform_arm = uniform_rng.randrange(len(AGENT_IDS))
        uniform_reward = rewards[uniform_arm]
        times["UNIFORM"] += time.perf_counter() - started

        oracle_arm = max(range(len(AGENT_IDS)), key=lambda agent: mean_rewards[agent])
        oracle_reward = rewards[oracle_arm]
        selected = {
            "LINUCB": (linucb_arm, linucb_reward),
            "EXP3": (exp3_arm, exp3_reward),
            "UNIFORM": (uniform_arm, uniform_reward),
            "CONTEXTUAL_ORACLE": (oracle_arm, oracle_reward),
        }
        for name, (arm, reward) in selected.items():
            returns[name] += reward
            choices[name].append(arm)
            pseudo_regrets[name] += max(mean_rewards) - mean_rewards[arm]

        trace.append({
            "period": period,
            "task": TASK_IDS[task],
            "observed_context": list(context),
            "linucb_scores": list(linucb_scores),
            "linucb_agent": linucb_arm,
            "linucb_reward_observed": linucb_reward,
            "linucb_coefficients_after": [list(row) for row in linucb.coefficient_estimates],
            "exp3_probabilities_before": list(exp3_probabilities),
            "exp3_agent": exp3_arm,
            "exp3_reward_observed": exp3_reward,
            "exp3_probabilities_after": list(exp3.probabilities),
            "uniform_agent": uniform_arm,
            "uniform_reward": uniform_reward,
            "contextual_oracle_agent": oracle_arm,
            "contextual_oracle_reward": oracle_reward,
        })

    return {
        "replication": seed,
        "task_seed": seed,
        "potential_reward_seed": 1_000_000 + seed,
        "exp3_policy_seed": 2_000_000 + seed,
        "uniform_policy_seed": 3_000_000 + seed,
        "task_sequence": [TASK_IDS[task] for task in contexts],
        "potential_rewards_evaluator_only": [list(row) for row in potential_rewards],
        "contextual_oracle_expected_reward": sum(
            max(COMPETENCE[agent][task] for agent in range(len(AGENT_IDS)))
            for task in contexts
        ),
        "cumulative_reward": returns,
        "pseudo_regret_vs_contextual_oracle": pseudo_regrets,
        "best_fixed_task_agent_mapping_retrospective": [AGENT_IDS[agent] for agent in mapping],
        "best_fixed_mapping_realized_reward": best_fixed_map_return,
        "best_fixed_agent_retrospective_reward": best_fixed_agent_return,
        "realized_regret_vs_best_fixed_agent": {
            name: best_fixed_agent_return - reward for name, reward in returns.items()
        },
        "realized_regret_vs_best_fixed_mapping": {
            name: best_fixed_map_return - reward for name, reward in returns.items()
        },
        "mean_policy_seconds": times,
        "agent_choices": choices,
        "trace": trace,
    }


def run_experiment(repetitions: int = 20, horizon: int = 300,
                   delta: float = 0.05) -> dict:
    if repetitions < 2 or horizon < 1:
        raise ValueError("repetitions must be >=2 and horizon must be positive")
    alpha = alpha_from_delta(delta)
    runs = [_run_replication(seed, horizon, alpha, delta) for seed in range(repetitions)]
    policy_names = ("LINUCB", "EXP3", "UNIFORM", "CONTEXTUAL_ORACLE")
    summary = {}
    for name in policy_names:
        rewards = [run["cumulative_reward"][name] for run in runs]
        summary[name] = {
            "mean_cumulative_reward": _mean(rewards),
            "sd_cumulative_reward": _sd(rewards),
            "mean_pseudo_regret_vs_contextual_oracle": _mean(
                [run["pseudo_regret_vs_contextual_oracle"][name] for run in runs]
            ),
            "mean_realized_regret_vs_best_fixed_mapping": _mean(
                [run["realized_regret_vs_best_fixed_mapping"][name] for run in runs]
            ),
            "mean_realized_regret_vs_best_fixed_agent": _mean(
                [run["realized_regret_vs_best_fixed_agent"][name] for run in runs]
            ),
            "mean_policy_seconds_per_run": _mean([run["mean_policy_seconds"].get(name, 0.0) for run in runs]),
            "mean_agent_choices": [
                _mean([run["agent_choices"][name].count(agent) for run in runs])
                for agent in range(len(AGENT_IDS))
            ],
        }
    fixed_map_returns = [run["best_fixed_mapping_realized_reward"] for run in runs]
    fixed_agent_returns = [run["best_fixed_agent_retrospective_reward"] for run in runs]
    summary["BEST_FIXED_TASK_TO_AGENT_MAP_RETROSPECTIVE"] = {
        "mean_cumulative_reward": _mean(fixed_map_returns),
        "sd_cumulative_reward": _sd(fixed_map_returns),
        "role": "hindsight maximum over all 3^3 fixed task-to-agent mappings; evaluator-only, not deployable",
    }
    summary["BEST_FIXED_AGENT_RETROSPECTIVE"] = {
        "mean_cumulative_reward": _mean(fixed_agent_returns),
        "sd_cumulative_reward": _sd(fixed_agent_returns),
        "role": "hindsight best constant agent; aligns with EXP3 weak-regret reference",
    }
    paired_comparisons = {}
    compared = ("EXP3", "UNIFORM", "CONTEXTUAL_ORACLE")
    for other in compared:
        differences = [run["cumulative_reward"]["LINUCB"] - run["cumulative_reward"][other]
                       for run in runs]
        paired_comparisons[f"LINUCB_minus_{other}"] = {
            "mean": _mean(differences),
            "sd": _sd(differences),
        }
    linucb_oracle_accuracy = _mean(
        sum(arm == max(range(len(AGENT_IDS)), key=lambda a: COMPETENCE[a][task])
            for arm, task in zip(run["agent_choices"]["LINUCB"],
                                 [TASK_IDS.index(task) for task in run["task_sequence"]])) / horizon
        for run in runs
    )
    return {
        "scenario": "HLS contextual agent selection; 3 tasks, 3 heterogeneous agents; fixed competencies",
        "horizon": horizon,
        "repetitions": repetitions,
        "agent_ids": list(AGENT_IDS),
        "task_ids": list(TASK_IDS),
        "fixed_competence_success_probabilities_agent_by_task": [list(row) for row in COMPETENCE],
        "demand": "existing C5 NonStationaryTaskDemand; three equal-length phases with distributions (0.70,0.20,0.10), (0.10,0.20,0.70), (0.20,0.70,0.10)",
        "context_features": "3-dimensional one-hot task identity; same task context supplied for every agent to LinUCB",
        "reward": "Bernoulli task success in [0,1], sampled from fixed agent-task competence; per-agent-period potential outcomes pre-generated and shared across policies",
        "learning_scope": "LinUCB learns per-agent reward-model coefficients only; physical agent competencies remain fixed",
        "linucb_variant": "disjoint linear models, Li et al. (2010) §3.1, Algorithm 1; tie break is lowest agent index",
        "linucb_alpha": alpha,
        "linucb_delta_for_paper_eq_4": delta,
        "exp3": "existing unmodified EXP3 implementation; context-free by algorithm definition",
        "uniform": "uniform random agent selection, with independent policy RNG",
        "best_fixed_mapping": "best realized fixed task-to-agent map among all 27 mappings; retrospective evaluator-only reference",
        "contextual_oracle": "selects the agent with highest true expected reward for each observed task; evaluator-only model-knowledge reference, does not inspect realized potential outcome",
        "information_boundary": "LinUCB receives current task features and only selected reward; EXP3/uniform receive no context features; all receive only their selected reward as action feedback",
        "paired_trajectories": True,
        "linucb_contextual_choice_accuracy": linucb_oracle_accuracy,
        "paired_reward_differences": paired_comparisons,
        "summary": summary,
        "replications": runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/experiments/hls_linucb_validation/results.json"))
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--horizon", type=int, default=300)
    parser.add_argument("--delta", type=float, default=0.05)
    args = parser.parse_args()
    result = {
        "algorithm_validation": {
            "variant": "disjoint LinUCB, Li et al. (2010) §3.1, Algorithm 1",
            "validation_test": "tests/test_linucb.py",
            "expected_contextual_preferences": "agents 0,1,2 are respectively optimal for one-hot contexts 0,1,2",
        },
        "hls_evaluation": run_experiment(args.repetitions, args.horizon, args.delta),
        "reference": {
            "authors": "Lihong Li, Wei Chu, John Langford, Robert E. Schapire",
            "title": "A Contextual-Bandit Approach to Personalized News Article Recommendation",
            "venue": "WWW 2010",
            "arxiv": "https://arxiv.org/abs/1003.0146",
            "doi": "10.1145/1772690.1772758",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "summary": result["hls_evaluation"]["summary"],
        "linucb_contextual_choice_accuracy": result["hls_evaluation"]["linucb_contextual_choice_accuracy"],
    }, indent=2))


if __name__ == "__main__":
    main()

