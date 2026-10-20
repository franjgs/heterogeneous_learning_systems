"""Run the explicitly authorized, bounded HLS-G0-C6 exploratory campaign."""

from __future__ import annotations

from dataclasses import asdict
from itertools import combinations
import hashlib
import json
import platform
from pathlib import Path
import statistics
import sys
from time import perf_counter

from hls.synthetic.e1_minimum import (
    build_e1_instance,
    four_policy_solutions,
    make_replay,
    run_policy,
)


POLICY_ORDER = ("BEST_STATIC", "MYOPIC", "STRONG_SEP", "HLS")
SEEDS = tuple(2026101900 + index for index in range(20))
ETA_LEVELS = (0.0, 0.1, 0.75)
DEMAND_LEVELS = ("stationary", "changing")
OUTPUT = Path("results/experiments/hls_g0_c6/exploratory_results.json")


def _policy_identities(policies):
    return {
        name: {
            "static_routing": (
                dict(solution.policy.static_routing)
                if solution.policy.static_routing is not None
                else None
            ),
            "tie_coordination": solution.policy.tie_coordination,
        }
        for name, solution in policies.items()
    }


def _one_trace(instance, result):
    environment = instance.problem.environment
    rows = []
    saturation_observations = 0
    competence_observations = 0
    ties = 0
    null_development = 0
    budget_used = 0.0
    for transition in result.trace.transitions:
        rewards = {
            action: environment.reward.operational_reward(
                transition.state, transition.task, action
            )
            for action in instance.problem.operational_actions
        }
        best = max(rewards.values())
        tied = sum(abs(value - best) <= 1e-12 for value in rewards.values()) > 1
        ties += int(tied)
        null_development += int(transition.development_action.is_null)
        before_budget = transition.state.resource_dict().get(
            "development_budget", 0.0
        )
        after_budget = transition.next_state.resource_dict().get(
            "development_budget", 0.0
        )
        budget_used += before_budget - after_budget
        for matrix in (transition.state.competence, transition.next_state.competence):
            for row in matrix:
                for value in row:
                    competence_observations += 1
                    saturation_observations += int(value >= 1.0 - 1e-12)
        rows.append(
            {
                "time": transition.state.time,
                "task": transition.task,
                "routing": transition.operational_action,
                "opportunity": transition.opportunity.available,
                "development": asdict(transition.development_action),
                "operational_reward": transition.operational_reward,
                "development_objective_cost": transition.development_cost,
                "development_budget_before": before_budget,
                "development_budget_after": after_budget,
                "competence_before": transition.state.competence,
                "competence_after": transition.next_state.competence,
                "immediate_routing_tie": tied,
            }
        )
    return {
        "transitions": rows,
        "operational_reward": result.cumulative_reward - result.terminal_reward,
        "terminal_reward": result.terminal_reward,
        "cumulative_reward": result.cumulative_reward,
        "development_objective_cost": result.development_cost,
        "development_budget_used": budget_used,
        "objective": result.objective,
        "null_development_count": null_development,
        "null_development_frequency": null_development / len(rows),
        "immediate_routing_tie_count": ties,
        "competence_saturation_fraction": (
            saturation_observations / competence_observations
        ),
        "final_competence": result.trace.transitions[-1].next_state.competence,
    }


def _summarize(paired_records):
    comparisons = {}
    for left, right in combinations(POLICY_ORDER, 2):
        differences = [
            record["policies"][left]["objective"]
            - record["policies"][right]["objective"]
            for record in paired_records
        ]
        comparisons[f"{left}_minus_{right}"] = {
            "paired_differences": differences,
            "mean": statistics.fmean(differences),
            "median": statistics.median(differences),
            "sample_sd": statistics.stdev(differences),
            "min": min(differences),
            "max": max(differences),
        }

    pairwise_coincidence = {}
    for left, right in combinations(POLICY_ORDER, 2):
        matching = 0
        total = 0
        for record in paired_records:
            left_actions = record["policies"][left]["transitions"]
            right_actions = record["policies"][right]["transitions"]
            for a, b in zip(left_actions, right_actions):
                total += 1
                matching += int(a["routing"] == b["routing"])
        pairwise_coincidence[f"{left}_vs_{right}"] = {
            "matching_decisions": matching,
            "total_decisions": total,
            "fraction": matching / total,
        }
    return {
        "paired_objective_differences": comparisons,
        "routing_decision_coincidence": pairwise_coincidence,
        "exploratory_only_no_significance_claim": True,
    }


def run_campaign(output: Path = OUTPUT) -> dict:
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing result: {output}")

    report = {
        "experiment_id": "HLS-G0-C6",
        "title": "Anticipatory Capability Development under Stochastic Demand",
        "status": "EXPLORATORY_CAMPAIGN_EXECUTED",
        "campaign_design": {
            "agents": 2,
            "tasks": 2,
            "horizon": 4,
            "eta_levels": ETA_LEVELS,
            "demand_levels": DEMAND_LEVELS,
            "seed_ids": SEEDS,
            "paired_trajectories_per_cell": len(SEEDS),
            "exogenous_trajectories": len(ETA_LEVELS)
            * len(DEMAND_LEVELS)
            * len(SEEDS),
            "policies_per_trajectory": POLICY_ORDER,
            "policy_randomness": "none; all policies deterministic",
            "opportunity_randomness": "common uniforms, action-conditioned Bernoulli outcomes",
        },
        "instances": [],
    }

    for demand in DEMAND_LEVELS:
        for eta in ETA_LEVELS:
            instance = build_e1_instance(eta=eta, demand=demand, horizon=4)
            started = perf_counter()
            policy_solutions = four_policy_solutions(instance)
            solver_seconds = perf_counter() - started
            policies = {
                name: solution.policy
                for name, solution in policy_solutions.items()
            }
            paired_records = []
            execution_seconds = {name: [] for name in POLICY_ORDER}
            for seed in SEEDS:
                replay = make_replay(instance, seed)
                paired_results = {}
                for name in POLICY_ORDER:
                    started = perf_counter()
                    paired_results[name] = run_policy(
                        instance, name, policies[name], replay
                    )
                    execution_seconds[name].append(perf_counter() - started)
                policy_results = {
                    name: _one_trace(instance, paired_results[name])
                    for name in POLICY_ORDER
                }
                paired_records.append(
                    {
                        "seed": seed,
                        "demand_seed": replay.demand_seed,
                        "opportunity_seed": replay.opportunity_seed,
                        "task_path": replay.task_path,
                        "opportunity_uniforms": replay.opportunity_uniforms,
                        "policies": policy_results,
                    }
                )

            expected = {
                name: solution.value
                for name, solution in policy_solutions.items()
            }
            empirical_means = {
                name: statistics.fmean(
                    record["policies"][name]["objective"]
                    for record in paired_records
                )
                for name in POLICY_ORDER
            }
            report["instances"].append(
                {
                    "configuration": {
                        "eta": eta,
                        "demand": demand,
                        "initial_competence": instance.initial_state.competence,
                        "initial_development_budget": 1.0,
                        "budget_per_development": 1.0,
                        "objective_cost_per_development": 0.0,
                        "beta": 1.0,
                        "terminal_task": instance.problem.terminal_task,
                        "task_distributions": (
                            {"each_period": {1: 0.5, 2: 0.5}}
                            if demand == "stationary"
                            else {
                                "periods_0_1": {1: 0.8, 2: 0.2},
                                "periods_2_3": {1: 0.2, 2: 0.8},
                            }
                        ),
                    },
                    "policy_identities": _policy_identities(policy_solutions),
                    "exact_expected_policy_objectives": expected,
                    "empirical_mean_policy_objectives": empirical_means,
                    "empirical_minus_exact_mean": {
                        name: empirical_means[name] - expected[name]
                        for name in POLICY_ORDER
                    },
                    "solver_construction_seconds_all_four": solver_seconds,
                    "policy_execution_seconds_mean": {
                        name: statistics.fmean(values)
                        for name, values in execution_seconds.items()
                    },
                    "summary": _summarize(paired_records),
                    "trajectory_records": paired_records,
                }
            )

    report["reproducibility"] = {
        "python": sys.version,
        "platform": platform.platform(),
        "head_commit": "8531b08",
        "worktree_was_dirty_before_campaign": True,
        "source_sha256": {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (
                Path("src/hls/synthetic/exact.py"),
                Path("src/hls/synthetic/e1_minimum.py"),
                Path("experiments/run_hls_g0_c6.py"),
            )
        },
        "same_python_runtime_required_for_random_tape_replay": True,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    return report


if __name__ == "__main__":
    result = run_campaign()
    print(
        f"Wrote {result['campaign_design']['exogenous_trajectories']} paired "
        f"trajectories to {OUTPUT}"
    )
