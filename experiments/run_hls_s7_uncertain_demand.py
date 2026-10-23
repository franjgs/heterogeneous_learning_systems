"""First reproducible S7 validation: exact planning under Markov demand."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from random import Random
from statistics import mean, stdev
from time import perf_counter

from experiments.run_hls_s4_transfer_exact import make_case as make_physical_case
from experiments.run_hls_s4_transfer_opportunities import scenario
from hls.hls_lab_nk_environment import generate_environment_trajectory_nk
from hls.synthetic.hls_s7_uncertain_demand import (
    S7MarkovDemandCase,
    independent_tree_enumeration,
    replay_markov_policy,
    solve_markov_bellman,
    solve_reactive_greedy,
)

RESULT = Path("results/experiments/hls_s7_uncertain_demand/results.json")
HORIZON = 3
MC_SEEDS = tuple(range(73000, 74000))


def make_case(horizon: int = HORIZON) -> S7MarkovDemandCase:
    setup = scenario(0.05)
    physical = make_physical_case()
    environment = setup["environment"]
    process = environment.process
    states = tuple(environment.emissions[key].problems[0]
                   for key in process.initial_distribution)
    state_ids = tuple(process.initial_distribution)
    return S7MarkovDemandCase(
        physical_case=physical,
        demand_states=states,
        initial_probabilities=tuple(process.initial_distribution[key]
                                    for key in state_ids),
        transition_probabilities=tuple(
            tuple(process.transitions[key][next_key] for next_key in state_ids)
            for key in state_ids
        ),
        horizon=horizon,
    )


def run() -> dict:
    case = make_case()
    started = perf_counter()
    policies = {}
    for transfer in (False, True):
        policies[f"bellman_transfer_{transfer}"] = solve_markov_bellman(
            case, transfer_available=transfer,
        )
        policies[f"reactive_transfer_{transfer}"] = solve_reactive_greedy(
            case, transfer_available=transfer,
        )
    exact_seconds = perf_counter() - started

    # Independent exhaustive contingent-tree check on the first two periods.
    check_case = make_case(2)
    exhaustive_checks = {}
    for transfer in (False, True):
        bellman = solve_markov_bellman(check_case, transfer_available=transfer)
        exhaustive = independent_tree_enumeration(
            check_case, transfer_available=transfer,
        )
        exhaustive_checks[str(transfer)] = {
            "bellman": bellman.value,
            "independent_exhaustive_tree": exhaustive,
            "absolute_difference": abs(bellman.value - exhaustive),
        }
        if abs(bellman.value - exhaustive) > 1e-10:
            raise AssertionError("stochastic Bellman differs from exhaustive tree")

    environment = replace(scenario(0.05)["environment"], horizon=HORIZON)
    state_index = {problem.problem_id: index
                   for index, problem in enumerate(case.demand_states)}
    trajectory_rewards = {name: [] for name in policies}
    example_trace = {}
    example_path = None
    for seed in MC_SEEDS:
        trajectory = generate_trajectory(environment, seed)
        path = tuple(state_index[problem.problem_id] for problem in trajectory)
        if seed == MC_SEEDS[0]:
            example_path = path
        for name, policy in policies.items():
            rows = replay_markov_policy(case, policy, path)
            trajectory_rewards[name].append(sum(row["reward"] for row in rows))
            if seed == MC_SEEDS[0]:
                example_trace[name] = [
                    {**row, "action": {
                        "production": row["action"].production,
                        "teaching": (None if row["action"].teaching is None
                                     else row["action"].teaching.__dict__),
                    }} for row in rows
                ]

    monte_carlo = {
        name: {
            "mean_realized_ces": mean(values),
            "sd_across_demand_paths": stdev(values),
            "n_paths": len(values),
            "difference_from_exact_expected_value": mean(values) - policies[name].value,
            "mc_standard_error": stdev(values) / len(values) ** 0.5,
        }
        for name, values in trajectory_rewards.items()
    }
    result = {
        "experiment": "HLS-S7 first validation: stochastic Markov-demand Bellman reference",
        "reference": {
            "article": "Su, Zhong & Zhang (2025), Integrated training course planning and hierarchical multi-skilled employee scheduling in the workforce skill transformation context, IJPE 286, 109642, DOI 10.1016/j.ijpe.2025.109642",
            "consultation": "Full 19-page PDF read from ~/Downloads/1-s2.0-S0925527325001276-main.pdf",
            "relevant_scope": "The article's ITCESP assumes service/task information known in advance and proposes a single-stage integrated course timetable and employee scheduling model; stochastic demand is named as future work in its conclusion. S7 retains HLS MIS-v2/transfer laws and adds a finite Markov demand law; it does not reproduce ITCESP.",
        },
        "configuration_ABC": {
            "A_system": "Existing S4 2-agent × 2-skill physical case; deterministic hidden competence state evolves by unchanged MIS-v2 and optional unchanged transfer; demand is the existing C5 two-state Markov process.",
            "B_organization": "Existing feasible joint production/teaching action set under the same individual and collective resource limits.",
            "C_architecture": "Exact expected-value Bellman with known Markov transition law; reactive exact immediate-reward comparator. Both use the existing CES objective and physical transitions.",
        },
        "design": {
            "horizon": HORIZON,
            "demand_state_ids": [problem.problem_id for problem in case.demand_states],
            "initial_probabilities": case.initial_probabilities,
            "transition_probabilities": case.transition_probabilities,
            "c5_semantics": "The current demand state is observed before acting; future states are not revealed. The exact reference knows the transition matrix.",
            "transfer_parameter": case.physical_case.teaching_parameters.transfer_rate,
            "learning_eta": case.physical_case.profile.eta,
            "reward": "sum_t existing CES collective reward before competence transition",
            "randomness": "No random competence/reward noise; demand paths sampled from the existing C5 trajectory generator for the Monte Carlo check.",
        },
        "exact_values": {
            name: {
                "expected_cumulative_ces": policy.value,
                "visited_states": policy.visited_states,
                "transfer_available": policy.transfer_available,
            }
            for name, policy in policies.items()
        },
        "independent_exhaustive_validation_horizon_2": exhaustive_checks,
        "monte_carlo_policy_replay": monte_carlo,
        "example_demand_path": [case.demand_states[index].problem_id
                                for index in example_path],
        "example_policy_trajectories": example_trace,
        "runtime_seconds": {"exact_policies": exact_seconds},
        "interpretation": "Exact planning is a finite-case reference with known demand law, not an implementable recommendation for a setting where the transition law is unknown. The Monte Carlo means validate the expected values; this is an implementation/reference check, not a broad performance campaign.",
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def generate_trajectory(environment, seed: int):
    return generate_environment_trajectory_nk(environment, seed=seed).problems


if __name__ == "__main__":
    output = run()
    print(json.dumps({
        "exact_values": {
            name: row["expected_cumulative_ces"]
            for name, row in output["exact_values"].items()
        },
        "independent_tree_checks": output["independent_exhaustive_validation_horizon_2"],
        "monte_carlo_means": {
            name: row["mean_realized_ces"]
            for name, row in output["monte_carlo_policy_replay"].items()
        },
    }, indent=2))
