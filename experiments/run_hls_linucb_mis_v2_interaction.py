#!/usr/bin/env python3
"""Bounded LinUCB × MIS-v2 interaction pilot using existing HLS components."""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from pathlib import Path
from types import SimpleNamespace

from hls.hls_lab_nk_geometry import (
    OrganizationConfigNK,
    ProblemSpecNK,
    ProductiveAllocationNK,
    validate_productive_allocation_nk,
)
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from hls.hls_lab_nk_production import P0ProductionOnlyNK
from hls.linucb import LinUCBDisjoint, alpha_from_delta
from hls.synthetic.c5 import NonStationaryTaskDemand
from hls.synthetic.state import WorldState


OUTPUT = Path("results/experiments/hls_linucb_mis_v2_interaction/results.json")
AGENTS = ("agent_0", "agent_1", "agent_2")
TASKS = ("task_0", "task_1", "task_2")
HORIZON = 300
REPETITIONS = 20
INITIAL_COMPETENCE = (
    (0.85, 0.20, 0.20),
    (0.20, 0.85, 0.20),
    (0.20, 0.20, 0.85),
)
ETA = ((0.15, 0.15, 0.15),) * len(AGENTS)
LEARNING = LearningProfileNK(ETA)
INITIAL_ORGANIZATION = OrganizationConfigNK(
    AGENTS, TASKS, INITIAL_COMPETENCE, (1.0, 1.0, 1.0), 1.0,
)
SPECIALIZED_MAP = (0, 1, 2)  # fixed task index -> agent index
REQUIREMENT = 0.90
DELTA = 0.05
POLICIES = ("LINUCB", "FIXED_SPECIALIZED", "REACTIVE_P0")
CONDITIONS = ("COMPETENCE_CONSTANT", "MIS_V2_EVOLVING")


def c5_demand(horizon: int = HORIZON) -> NonStationaryTaskDemand:
    """Three-phase, time-indexed task demand from the existing C5 process."""
    distributions = {}
    phases = (
        (0.70, 0.20, 0.10),
        (0.10, 0.20, 0.70),
        (0.20, 0.70, 0.10),
    )
    for period in range(horizon):
        phase = min(2, (3 * period) // horizon)
        distributions[period] = dict(zip(TASKS, phases[phase]))
    return NonStationaryTaskDemand(distributions)


def _common_trajectory(seed: int, horizon: int) -> dict:
    """Pre-generate common exogenous demand and per-agent outcome shocks."""
    process = c5_demand(horizon)
    demand_rng = random.Random(seed)
    outcome_rng = random.Random(1_000_000 + seed)
    world = WorldState(INITIAL_COMPETENCE, time=0)
    history = []
    tasks = []
    for period in range(horizon):
        task = process.sample_task(period, world, history, demand_rng)
        tasks.append(TASKS.index(task))
        history.append(SimpleNamespace(task=task))
    outcome_uniforms = tuple(
        tuple(outcome_rng.random() for _ in AGENTS) for _ in range(horizon)
    )
    return {
        "seed": seed,
        "tasks": tuple(tasks),
        "outcome_uniforms": outcome_uniforms,
        "demand_seed": seed,
        "outcome_seed": 1_000_000 + seed,
    }


def _actions_for_task(task: int) -> tuple[ProductiveAllocationNK, ...]:
    """Common catalog: exactly one unit of current-task effort for one agent."""
    actions = []
    for agent in range(len(AGENTS)):
        actions.append(tuple(
            tuple(1.0 if i == agent and k == task else 0.0
                  for k in range(len(TASKS)))
            for i in range(len(AGENTS))
        ))
    return tuple(actions)


def _problem_for_task(task: int) -> ProblemSpecNK:
    requirements = tuple(REQUIREMENT if k == task else 0.0
                          for k in range(len(TASKS)))
    return ProblemSpecNK(TASKS[task], requirements, 1.0)


def _linucb_contexts(task: int, competence) -> tuple[tuple[float, ...], ...]:
    """Expose identical task and current-competence information to all arms."""
    task_features = tuple(1.0 if k == task else 0.0 for k in range(len(TASKS)))
    current_task_competencies = tuple(competence[a][task] for a in range(len(AGENTS)))
    observed = task_features + current_task_competencies
    return (observed,) * len(AGENTS)


def _run_policy(trajectory: dict, policy: str, learning_enabled: bool,
                alpha: float, *, record_trace: bool = True) -> dict:
    competence = INITIAL_COMPETENCE
    linucb = LinUCBDisjoint(len(AGENTS), len(TASKS) * 2, alpha) if policy == "LINUCB" else None
    reactive = P0ProductionOnlyNK()
    total_reward = 0.0
    expected_reward = 0.0
    choices = []
    trace = []
    policy_seconds = 0.0

    for period, task in enumerate(trajectory["tasks"]):
        before = competence
        actions = _actions_for_task(task)
        problem = _problem_for_task(task)
        contexts = _linucb_contexts(task, before)
        scores = coefficients = None
        started = time.perf_counter()
        if policy == "LINUCB":
            assert linucb is not None
            scores = linucb.scores(contexts)
            agent = linucb.select(contexts)
        elif policy == "FIXED_SPECIALIZED":
            agent = SPECIALIZED_MAP[task]
        elif policy == "REACTIVE_P0":
            # Use P0's existing dimension-independent production ranking with
            # the same feasible action catalog (no alternate selector rule).
            action_id, chosen = reactive.choose(actions, before, problem)
            del action_id
            agent = next(i for i, row in enumerate(chosen) if row[task] == 1.0)
        else:
            raise ValueError(f"unknown policy {policy!r}")
        policy_seconds += time.perf_counter() - started

        if not validate_productive_allocation_nk(actions[agent], INITIAL_ORGANIZATION, problem):
            raise AssertionError("selected assignment violates the shared action/resource contract")
        expected = before[agent][task]
        reward = float(trajectory["outcome_uniforms"][period][agent] < expected)
        total_reward += reward
        expected_reward += expected
        choices.append(agent)

        if linucb is not None:
            linucb.observe_reward(reward)
            coefficients = linucb.coefficient_estimates

        after = mis_v2_transition_nk(
            before, actions[agent], LEARNING, enabled=learning_enabled,
        )
        if record_trace:
            changed_value = after[agent][task]
            row = {
                "period": period,
                "task": TASKS[task],
                "context": list(contexts[0]),
                "selected_agent": AGENTS[agent],
                "expected_success_probability": expected,
                "observed_reward": reward,
                "competence_before": [list(values) for values in before],
                "updated_cell_after": [AGENTS[agent], TASKS[task], changed_value],
                "resource_used": 1.0,
            }
            if linucb is not None:
                row["linucb_scores_before"] = list(scores)
                row["linucb_coefficients_after"] = [list(values) for values in coefficients]
            trace.append(row)
        competence = after

    result = {
        "cumulative_reward": total_reward,
        "mean_expected_reward": expected_reward / len(trajectory["tasks"]),
        "success_rate": total_reward / len(trajectory["tasks"]),
        "resource_used": float(len(trajectory["tasks"])),
        "selected_agent_counts": [choices.count(agent) for agent in range(len(AGENTS))],
        "final_competence": [list(row) for row in competence],
        "policy_seconds": policy_seconds,
        "trace": trace,
    }
    if linucb is not None:
        result["linucb_final_design_matrices"] = linucb.design_matrices
        result["linucb_final_response_vectors"] = linucb.response_vectors
        result["linucb_final_coefficients"] = linucb.coefficient_estimates
    return result


def _mean(values):
    return statistics.fmean(values)


def _sd(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def run_experiment(repetitions: int = REPETITIONS, horizon: int = HORIZON,
                   delta: float = DELTA) -> dict:
    if repetitions < 2 or horizon < 3:
        raise ValueError("repetitions must be >=2 and horizon must include all three C5 phases")
    alpha = alpha_from_delta(delta)
    trajectories = [_common_trajectory(seed, horizon) for seed in range(repetitions)]
    runs = []
    for trajectory in trajectories:
        policies = {}
        for condition in CONDITIONS:
            enabled = condition == "MIS_V2_EVOLVING"
            policies[condition] = {
                policy: _run_policy(trajectory, policy, enabled, alpha)
                for policy in POLICIES
            }
        runs.append({
            "replication": trajectory["seed"],
            "demand_seed": trajectory["demand_seed"],
            "outcome_seed": trajectory["outcome_seed"],
            "conditions": policies,
        })

    summary = {}
    for condition in CONDITIONS:
        summary[condition] = {}
        for policy in POLICIES:
            episodes = [run["conditions"][condition][policy] for run in runs]
            summary[condition][policy] = {
                "mean_cumulative_reward": _mean([e["cumulative_reward"] for e in episodes]),
                "sd_cumulative_reward": _sd([e["cumulative_reward"] for e in episodes]),
                "mean_expected_reward": _mean([e["mean_expected_reward"] for e in episodes]),
                "mean_success_rate": _mean([e["success_rate"] for e in episodes]),
                "mean_resource_used": _mean([e["resource_used"] for e in episodes]),
                "mean_selected_agent_counts": [
                    _mean([e["selected_agent_counts"][i] for e in episodes])
                    for i in range(len(AGENTS))
                ],
                "mean_final_competence": [
                    [
                        _mean([e["final_competence"][i][k] for e in episodes])
                        for k in range(len(TASKS))
                    ] for i in range(len(AGENTS))
                ],
                "mean_policy_seconds_per_episode": _mean([e["policy_seconds"] for e in episodes]),
            }

    paired = {}
    for condition in CONDITIONS:
        for left, right in (("LINUCB", "FIXED_SPECIALIZED"),
                            ("LINUCB", "REACTIVE_P0"),
                            ("REACTIVE_P0", "FIXED_SPECIALIZED")):
            differences = [
                run["conditions"][condition][left]["cumulative_reward"]
                - run["conditions"][condition][right]["cumulative_reward"]
                for run in runs
            ]
            paired[f"{condition}:{left}_minus_{right}"] = {
                "mean": _mean(differences), "sd": _sd(differences),
                "per_seed": differences,
            }
    for policy in POLICIES:
        differences = [
            run["conditions"]["MIS_V2_EVOLVING"][policy]["cumulative_reward"]
            - run["conditions"]["COMPETENCE_CONSTANT"][policy]["cumulative_reward"]
            for run in runs
        ]
        paired[f"MIS_V2_effect:{policy}"] = {
            "mean": _mean(differences), "sd": _sd(differences), "per_seed": differences,
        }
    paired["difference_in_differences:LinUCB_minus_fixed_by_MIS"] = {
        "mean": _mean([
            (run["conditions"]["MIS_V2_EVOLVING"]["LINUCB"]["cumulative_reward"]
             - run["conditions"]["MIS_V2_EVOLVING"]["FIXED_SPECIALIZED"]["cumulative_reward"])
            - (run["conditions"]["COMPETENCE_CONSTANT"]["LINUCB"]["cumulative_reward"]
               - run["conditions"]["COMPETENCE_CONSTANT"]["FIXED_SPECIALIZED"]["cumulative_reward"])
            for run in runs
        ]),
        "interpretation": "paired policy-by-MIS interaction contrast; descriptive, not a mediated causal effect",
    }
    divergence = [
        sum(a["selected_agent"] != b["selected_agent"] for a, b in zip(
            run["conditions"]["MIS_V2_EVOLVING"]["LINUCB"]["trace"],
            run["conditions"]["COMPETENCE_CONSTANT"]["LINUCB"]["trace"],
        )) / horizon
        for run in runs
    ]
    return {
        "experiment": "HLS-LinUCB-MIS-v2 mechanism interaction pilot",
        "ontology": {
            "A_scenario": "3 agents, 3 task types, 300 periods, nonstationary C5 three-phase demand; one unit assignment per period.",
            "B_mechanisms": "LinUCB learns the selection rule from selected-arm reward feedback; MIS-v2 changes the selected agent-task competence after execution. Transfer disabled.",
            "C_organization": "LinUCB-disjoint, fixed task-specialist map, and current-state myopic P0 production selector.",
            "selection_learning_is_not_competence_learning": True,
        },
        "configuration": {
            "horizon": horizon, "repetitions": repetitions, "agents": list(AGENTS), "tasks": list(TASKS),
            "initial_competence_agent_by_task": [list(row) for row in INITIAL_COMPETENCE],
            "MIS_v2_eta": [list(row) for row in ETA], "transfer": "disabled; MIS-v2 is agent-skill local",
            "conditions": list(CONDITIONS), "demand": "existing C5 NonStationaryTaskDemand; three equal phases using the distributions recorded by c5_demand()",
            "action_catalog": "three feasible actions for current task: assign one unit effort to exactly one of three agents; shared and individual budgets are 1.0",
            "reward": "Bernoulli task success in [0,1], probability equal to current competence of selected agent in current task; one common pre-generated uniform shock per seed-period-agent across all policies and learning conditions",
            "competence_observation": "current true competence matrix is perfectly observable and shared with organizations; LinUCB receives task one-hot plus all three current competences for that task in each arm context",
            "linucb_variant": "unmodified disjoint LinUCB; 6 features (3 task indicators + 3 current-task agent competences); alpha from Li et al. Eq. (4), delta=0.05",
            "reactive_selector": "existing P0ProductionOnlyNK ranking on the common one-unit action catalog; current competence only, no future value",
            "fixed_policy": "predeclared specialized map task_i -> agent_i; selected from the initial competence profile, not evaluation outcomes",
            "randomness": "C5 demand and per-agent Bernoulli outcome shocks are separately seeded and replayed identically across all policies and both competence conditions; no policy RNG is used",
        },
        "policy_information_and_updates": {
            "LINUCB": "current task and all current-task competencies; only selected-agent reward enters A_a += xx^T, b_a += r x",
            "FIXED_SPECIALIZED": "same task and competence information is available, but the predeclared map ignores current state; no update",
            "REACTIVE_P0": "same task and true current competence; maximizes current expected production via existing P0 lexicographic rule; no update or lookahead",
            "MIS_v2": "after reward, one unit exposure updates only selected (agent, task) cell with existing MIS-v2 transition; enabled=False control leaves competence unchanged",
        },
        "paired_comparisons": paired,
        "linucb_action_divergence_rate_evolving_vs_constant_mean": _mean(divergence),
        "summary": summary,
        "replications": runs,
        "interpretation_boundary": "small synthetic mechanism-interaction evaluation; descriptive paired evidence, not a general superiority claim or a reproduction of Li et al. (2010)",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=int, default=REPETITIONS)
    parser.add_argument("--horizon", type=int, default=HORIZON)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    results = run_experiment(args.repetitions, args.horizon)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, separators=(",", ":")) + "\n", encoding="utf-8")
    for condition, methods in results["summary"].items():
        print(condition)
        for method, metrics in methods.items():
            print(f"  {method}: reward={metrics['mean_cumulative_reward']:.3f} "
                  f"(SD {metrics['sd_cumulative_reward']:.3f}), "
                  f"success={metrics['mean_success_rate']:.3f}, "
                  f"final_C={metrics['mean_final_competence']}")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
