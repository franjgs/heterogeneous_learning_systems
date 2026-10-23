#!/usr/bin/env python3
"""Run bounded implementation checks and a paired HLS EXP3 pilot."""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from pathlib import Path

from hls.exp3 import Exp3, gamma_for_horizon


def _mean(values):
    return statistics.fmean(values)


def _sd(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def known_bandit_check(repetitions: int = 40, horizon: int = 300) -> dict:
    """Deterministic rewards with one known-best arm; implementation check."""
    rewards = (1.0, 0.0, 0.0)
    gamma = gamma_for_horizon(len(rewards), horizon)
    exp3_returns, uniform_returns = [], []
    for seed in range(repetitions):
        policy = Exp3(len(rewards), gamma)
        policy_rng = random.Random(seed)
        uniform_rng = random.Random(10_000 + seed)
        exp3_return = uniform_return = 0.0
        for _ in range(horizon):
            arm = policy.select(policy_rng)
            reward = rewards[arm]
            exp3_return += reward
            policy.observe_reward(reward)
            uniform_return += rewards[uniform_rng.randrange(len(rewards))]
        exp3_returns.append(exp3_return)
        uniform_returns.append(uniform_return)
    return {
        "purpose": "known deterministic bandit implementation check; not HLS evidence",
        "arms_reward": list(rewards),
        "horizon": horizon,
        "repetitions": repetitions,
        "gamma": gamma,
        "exp3_mean_reward": _mean(exp3_returns),
        "uniform_mean_reward": _mean(uniform_returns),
        "best_arm_reward": float(horizon),
        "exp3_mean_regret_vs_best_arm": horizon - _mean(exp3_returns),
        "uniform_mean_regret_vs_best_arm": horizon - _mean(uniform_returns),
        "check_passed": _mean(exp3_returns) > _mean(uniform_returns),
    }


def _make_hls_rewards(seed: int, horizon: int, success_probabilities: tuple[float, ...]):
    """Pre-generate evaluator-only potential outcomes for paired replay."""
    rng = random.Random(seed)
    return [
        tuple(float(rng.random() < probability) for probability in success_probabilities)
        for _ in range(horizon)
    ]


def hls_pilot(repetitions: int = 20, horizon: int = 300) -> dict:
    """Single-task HLS bandit: fixed heterogeneous agent capabilities."""
    probabilities = (0.80, 0.55, 0.35)
    n_agents = len(probabilities)
    gamma = gamma_for_horizon(n_agents, horizon)
    exp3_runs, uniform_runs = [], []
    traces = []

    for replication in range(repetitions):
        environment_seed = 20_000 + replication
        exp3_seed = 30_000 + replication
        uniform_seed = 40_000 + replication
        outcomes = _make_hls_rewards(environment_seed, horizon, probabilities)
        best_fixed_reward = max(sum(row[agent] for row in outcomes) for agent in range(n_agents))

        exp3 = Exp3(n_agents, gamma)
        exp3_rng = random.Random(exp3_seed)
        uniform_rng = random.Random(uniform_seed)
        exp3_return = uniform_return = 0.0
        exp3_selections = [0] * n_agents
        uniform_selections = [0] * n_agents
        exp3_time = uniform_time = 0.0
        steps = []

        for period, potential_rewards in enumerate(outcomes):
            before = exp3.probabilities
            started = time.perf_counter()
            exp3_arm = exp3.select(exp3_rng)
            exp3_reward = potential_rewards[exp3_arm]
            exp3.observe_reward(exp3_reward)
            exp3_time += time.perf_counter() - started
            exp3_return += exp3_reward
            exp3_selections[exp3_arm] += 1

            started = time.perf_counter()
            uniform_arm = uniform_rng.randrange(n_agents)
            uniform_reward = potential_rewards[uniform_arm]
            uniform_time += time.perf_counter() - started
            uniform_return += uniform_reward
            uniform_selections[uniform_arm] += 1

            steps.append({
                "period": period,
                "exp3_probabilities_before": list(before),
                "exp3_agent": exp3_arm,
                "exp3_reward_observed": exp3_reward,
                "exp3_probabilities_after": list(exp3.probabilities),
                "uniform_agent": uniform_arm,
                "uniform_reward": uniform_reward,
            })

        exp3_runs.append({
            "seed": replication,
            "environment_seed": environment_seed,
            "exp3_policy_seed": exp3_seed,
            "uniform_policy_seed": uniform_seed,
            "exp3_reward": exp3_return,
            "uniform_reward": uniform_return,
            "best_fixed_retrospective_reward": best_fixed_reward,
            "exp3_regret_vs_best_fixed": best_fixed_reward - exp3_return,
            "uniform_regret_vs_best_fixed": best_fixed_reward - uniform_return,
            "exp3_agent_selections": exp3_selections,
            "uniform_agent_selections": uniform_selections,
            "exp3_policy_seconds": exp3_time,
            "uniform_selector_seconds": uniform_time,
            "trace": steps,
        })
        uniform_runs.append(uniform_return)

    exp3_rewards = [run["exp3_reward"] for run in exp3_runs]
    fixed_rewards = [run["best_fixed_retrospective_reward"] for run in exp3_runs]
    exp3_regrets = [run["exp3_regret_vs_best_fixed"] for run in exp3_runs]
    uniform_regrets = [run["uniform_regret_vs_best_fixed"] for run in exp3_runs]
    paired_differences = [run["exp3_reward"] - run["uniform_reward"] for run in exp3_runs]
    return {
        "scenario": "one repeated unit task; agent selection; fixed heterogeneous success probabilities",
        "agents": ["agent_0", "agent_1", "agent_2"],
        "fixed_success_probabilities": list(probabilities),
        "capabilities_change": False,
        "task_count": 1,
        "horizon": horizon,
        "repetitions": repetitions,
        "gamma": gamma,
        "reward_definition": "Bernoulli task success in [0,1]; independent potential outcomes pre-generated per agent and period",
        "information_boundary": "EXP3 receives only the selected agent's scalar reward; full potential outcomes are evaluator-only",
        "paired_exogenous_outcomes": True,
        "policies": {
            "EXP3": {
                "mean_cumulative_reward": _mean(exp3_rewards),
                "sd_cumulative_reward": _sd(exp3_rewards),
                "mean_regret_vs_retrospective_best_fixed": _mean(exp3_regrets),
                "mean_policy_seconds_per_run": _mean([run["exp3_policy_seconds"] for run in exp3_runs]),
                "mean_agent_selections": [
                    _mean([run["exp3_agent_selections"][agent] for run in exp3_runs])
                    for agent in range(n_agents)
                ],
            },
            "UNIFORM": {
                "mean_cumulative_reward": _mean(uniform_runs),
                "sd_cumulative_reward": _sd(uniform_runs),
                "mean_regret_vs_retrospective_best_fixed": _mean(uniform_regrets),
                "mean_policy_seconds_per_run": _mean([run["uniform_selector_seconds"] for run in exp3_runs]),
                "mean_agent_selections": [
                    _mean([run["uniform_agent_selections"][agent] for run in exp3_runs])
                    for agent in range(n_agents)
                ],
            },
            "BEST_FIXED_RETROSPECTIVE": {
                "mean_cumulative_reward": _mean(fixed_rewards),
                "sd_cumulative_reward": _sd(fixed_rewards),
                "role": "non-deployable hindsight reference; maximizes realized total over constant-agent choices",
            },
        },
        "paired_exp3_minus_uniform_reward": {
            "mean": _mean(paired_differences),
            "sd": _sd(paired_differences),
        },
        "replications": exp3_runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/experiments/hls_exp3_validation/results.json"))
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--horizon", type=int, default=300)
    args = parser.parse_args()
    if args.repetitions < 2 or args.horizon < 1:
        parser.error("repetitions must be >=2 and horizon >=1")

    result = {
        "algorithm": "EXP3",
        "primary_reference": "Auer, Cesa-Bianchi, Freund, and Schapire (2002), Figure 1, Theorem 3.1, Corollary 3.2",
        "doi": "10.1137/S0097539701398375",
        "gamma_rule": "Corollary 3.2 with g=T, gamma=min(1,sqrt(K ln(K)/((e-1)T)))",
        "implementation_verification": known_bandit_check(),
        "hls_evaluation": hls_pilot(args.repetitions, args.horizon),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "implementation_check_passed": result["implementation_verification"]["check_passed"],
        "exp3_mean_reward": result["hls_evaluation"]["policies"]["EXP3"]["mean_cumulative_reward"],
        "uniform_mean_reward": result["hls_evaluation"]["policies"]["UNIFORM"]["mean_cumulative_reward"],
        "best_fixed_mean_reward": result["hls_evaluation"]["policies"]["BEST_FIXED_RETROSPECTIVE"]["mean_cumulative_reward"],
    }, indent=2))


if __name__ == "__main__":
    main()

