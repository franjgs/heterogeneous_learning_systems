#!/usr/bin/env python3
"""HLS-E2.1: exact dynamic allocation versus best task-dependent static map.

This deliberately small model has two agents, two independent skills, and two
task types (one task type per skill). Each period presents one unit-effort task;
the selected agent performs that task's skill. Reward is the Nembhard Direct
productivity at the start of the period. The selected agent-skill cell gains
one unit of direct experience after production.

The implementation is an isolated experiment, not a change to HLS-E1 or the
N×K laboratory. It reuses the authoritative scalar Nembhard curve.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import subprocess
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from src.hls.mechanisms.nembhard_direct import (
    DirectExperienceParameters,
    direct_productivity,
)


N_AGENTS = 2
N_SKILLS = 2
TASK_TO_SKILL = {"taskA": 0, "taskB": 1}
DEFAULT_HORIZON = 12
DEFAULT_TOLERANCE = 1e-10
ACTION_ORDER = (0, 1)  # stable tie-break: lower agent index first


@dataclass(frozen=True)
class Model:
    """A 2×2 matrix of direct-productivity parameters and initial experience."""

    k: tuple[tuple[float, float], tuple[float, float]]
    p: tuple[tuple[float, float], tuple[float, float]]
    r: tuple[tuple[float, float], tuple[float, float]]
    d0: tuple[tuple[int, int], tuple[int, int]]

    def __post_init__(self) -> None:
        for name in ("k", "p", "r", "d0"):
            matrix = getattr(self, name)
            if len(matrix) != N_AGENTS or any(len(row) != N_SKILLS for row in matrix):
                raise ValueError(f"{name} must be a 2×2 matrix")
        for i in range(N_AGENTS):
            for s in range(N_SKILLS):
                DirectExperienceParameters(self.k[i][s], self.p[i][s], self.r[i][s])
                value = self.d0[i][s]
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    raise ValueError("initial experience d0 must be a non-negative integer")

    def productivity(self, agent: int, skill: int, experience: tuple[int, ...]) -> float:
        cell = agent * N_SKILLS + skill
        params = DirectExperienceParameters(self.k[agent][skill], self.p[agent][skill], self.r[agent][skill])
        return direct_productivity(self.d0[agent][skill] + experience[cell], params)

    def initial_state(self) -> tuple[int, int, int, int]:
        return (0, 0, 0, 0)  # integer increments; d0 is held in the immutable model

    def state_matrix(self, increments: tuple[int, ...]) -> list[list[int]]:
        return [[self.d0[i][s] + increments[i * N_SKILLS + s]
                 for s in range(N_SKILLS)] for i in range(N_AGENTS)]


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    profile_id: str
    demand_id: str
    demands: tuple[str, ...]
    model: Model


def demand_sequences(horizon: int = DEFAULT_HORIZON) -> dict[str, tuple[str, ...]]:
    if horizon != 12:
        # Keep declared sequence construction explicit rather than silently
        # changing counts for a different horizon.
        raise ValueError("the reference E2.1 study defines demand sequences for T=12")
    return {
        "alternating": tuple("taskA" if t % 2 == 0 else "taskB" for t in range(horizon)),
        "clustered": ("taskA",) * 6 + ("taskB",) * 6,
        "changing_frequency": ("taskA",) * 8 + ("taskB",) * 4,
    }


def parameter_profiles() -> dict[str, Model]:
    """Small deterministic design spanning the requested structural cases."""
    homogeneous = Model(
        k=((1.0, 1.0), (1.0, 1.0)), p=((1.0, 1.0), (1.0, 1.0)),
        r=((4.0, 4.0), (4.0, 4.0)), d0=((0, 0), (0, 0)),
    )
    stable_specialization = Model(
        k=((1.6, 0.8), (0.8, 1.6)), p=((1.0, 1.0), (1.0, 1.0)),
        r=((4.0, 4.0), (4.0, 4.0)), d0=((0, 0), (0, 0)),
    )
    asymmetric_learning = Model(
        k=((1.0, 1.0), (2.0, 2.0)), p=((9.0, 9.0), (1.0, 1.0)),
        r=((1.0, 1.0), (3.0, 3.0)), d0=((0, 0), (0, 0)),
    )
    different_initial_experience = Model(
        k=((1.4, 1.2), (1.4, 1.2)), p=((1.0, 1.0), (1.0, 1.0)),
        r=((3.0, 3.0), (3.0, 3.0)), d0=((6, 0), (0, 5)),
    )
    mixed_learning_and_initial_experience = Model(
        k=((1.2, 1.0), (1.8, 1.6)), p=((5.0, 2.0), (1.0, 1.0)),
        r=((1.5, 5.0), (3.0, 2.5)), d0=((2, 0), (0, 4)),
    )
    # Small ±2% one-factor perturbations around the crossing-curve profile.
    # They are sensitivity checks, not a stochastic sample or campaign.
    def scaled(model: Model, field: str, factor: float) -> Model:
        return Model(
            k=tuple(tuple(v * factor for v in row) for row in model.k)
               if field == "k" else model.k,
            p=tuple(tuple(v * factor for v in row) for row in model.p)
               if field == "p" else model.p,
            r=tuple(tuple(v * factor for v in row) for row in model.r)
               if field == "r" else model.r,
            d0=model.d0,
        )
    crossing = asymmetric_learning
    return {
        "homogeneous": homogeneous,
        "stable_specialization": stable_specialization,
        "asymmetric_learning": asymmetric_learning,
        "different_initial_experience": different_initial_experience,
        "mixed_learning_and_initial_experience": mixed_learning_and_initial_experience,
        "crossing_k_minus_2pct": scaled(crossing, "k", 0.98),
        "crossing_k_plus_2pct": scaled(crossing, "k", 1.02),
        "crossing_p_minus_2pct": scaled(crossing, "p", 0.98),
        "crossing_p_plus_2pct": scaled(crossing, "p", 1.02),
        "crossing_r_minus_2pct": scaled(crossing, "r", 0.98),
        "crossing_r_plus_2pct": scaled(crossing, "r", 1.02),
    }


def _validate_demands(demands: Iterable[str]) -> tuple[str, ...]:
    result = tuple(demands)
    if not result or any(task not in TASK_TO_SKILL for task in result):
        raise ValueError("demands must be a non-empty sequence of taskA/taskB")
    return result


def _transition(state: tuple[int, ...], agent: int, skill: int) -> tuple[int, ...]:
    cell = agent * N_SKILLS + skill
    return state[:cell] + (state[cell] + 1,) + state[cell + 1:]


def _period_record(model: Model, state: tuple[int, ...], task: str, agent: int,
                   reward: float) -> dict[str, Any]:
    skill = TASK_TO_SKILL[task]
    productivity = [[model.productivity(i, s, state) for s in range(N_SKILLS)]
                    for i in range(N_AGENTS)]
    return {
        "task": task,
        "allocation": {"agent": agent, "skill": skill, "effort": 1},
        "experience_before": model.state_matrix(state),
        "productivity_before": productivity,
        "reward": reward,
    }


def evaluate_sequence(model: Model, demands: Iterable[str], allocations: Iterable[int]) -> dict[str, Any]:
    """Evaluate a supplied agent choice per task; choices are 0 or 1."""
    demand_path = _validate_demands(demands)
    actions = tuple(allocations)
    if len(actions) != len(demand_path) or any(a not in ACTION_ORDER for a in actions):
        raise ValueError("allocations must contain one feasible agent index per demand")
    state = model.initial_state()
    rows = []
    total = 0.0
    for task, agent in zip(demand_path, actions):
        skill = TASK_TO_SKILL[task]
        reward = model.productivity(agent, skill, state)
        row = _period_record(model, state, task, agent, reward)
        total += reward
        state = _transition(state, agent, skill)
        row["experience_after"] = model.state_matrix(state)
        row["productivity_after"] = [
            [model.productivity(i, s, state) for s in range(N_SKILLS)]
            for i in range(N_AGENTS)
        ]
        rows.append(row)
    return {"reward": total, "allocations": list(actions), "trajectory": rows,
            "final_experience": model.state_matrix(state)}


def optimize_dynamic(model: Model, demands: Iterable[str]) -> dict[str, Any]:
    """Exact finite-horizon DP; full demand path is known to this offline oracle."""
    demand_path = _validate_demands(demands)
    started = time.perf_counter()

    @lru_cache(maxsize=None)
    def value(t: int, state: tuple[int, ...]) -> float:
        if t == len(demand_path):
            return 0.0
        skill = TASK_TO_SKILL[demand_path[t]]
        best = float("-inf")
        for agent in ACTION_ORDER:
            reward = model.productivity(agent, skill, state)
            candidate = reward + value(t + 1, _transition(state, agent, skill))
            if candidate > best:
                best = candidate
        return best

    initial = model.initial_state()
    optimum = value(0, initial)
    state = initial
    actions: list[int] = []
    for t, task in enumerate(demand_path):
        skill = TASK_TO_SKILL[task]
        # Iterate in catalogue order and retain the first action on exact ties.
        chosen = ACTION_ORDER[0]
        best = float("-inf")
        for agent in ACTION_ORDER:
            candidate = model.productivity(agent, skill, state) + value(
                t + 1, _transition(state, agent, skill)
            )
            if candidate > best:
                best, chosen = candidate, agent
        actions.append(chosen)
        state = _transition(state, chosen, skill)
    evaluated = evaluate_sequence(model, demand_path, actions)
    elapsed = time.perf_counter() - started
    return {**evaluated, "reward": optimum, "states_explored": value.cache_info().currsize,
            "elapsed_seconds": elapsed, "policy_knowledge": [
                "true model parameters", "current experience", "complete future demand sequence"
            ]}


def optimize_best_static(model: Model, demands: Iterable[str]) -> dict[str, Any]:
    """Globally evaluate every stationary task-type→agent mapping (2² maps)."""
    demand_path = _validate_demands(demands)
    mappings = list(itertools.product(ACTION_ORDER, repeat=len(TASK_TO_SKILL)))
    candidates = []
    for mapping in mappings:
        actions = tuple(mapping[TASK_TO_SKILL[task]] for task in demand_path)
        result = evaluate_sequence(model, demand_path, actions)
        candidates.append({"mapping": list(mapping), "reward": result["reward"],
                           "allocations": list(actions), "trajectory": result["trajectory"],
                           "final_experience": result["final_experience"]})
    # Product enumeration is lexicographic; strict > preserves first map on ties.
    best = candidates[0]
    for candidate in candidates[1:]:
        if candidate["reward"] > best["reward"]:
            best = candidate
    return {**best, "mappings_evaluated": len(candidates),
            "all_mapping_rewards": [
                {"mapping": row["mapping"], "reward": row["reward"]} for row in candidates
            ], "policy_knowledge": ["true model parameters", "complete future demand sequence"]}


def evaluate_myopic(model: Model, demands: Iterable[str]) -> dict[str, Any]:
    demand_path = _validate_demands(demands)
    state = model.initial_state()
    actions: list[int] = []
    for task in demand_path:
        skill = TASK_TO_SKILL[task]
        # Immediate reward only; equal current productivity goes to agent 0.
        chosen = max(ACTION_ORDER, key=lambda a: (model.productivity(a, skill, state), -a))
        actions.append(chosen)
        state = _transition(state, chosen, skill)
    result = evaluate_sequence(model, demand_path, actions)
    return {**result, "policy_knowledge": ["true current productivity", "current task only"]}


def exhaustive_optimum(model: Model, demands: Iterable[str], *, max_horizon: int = 6) -> dict[str, Any]:
    """Independent exhaustive action-sequence enumeration for small horizons."""
    demand_path = _validate_demands(demands)
    if len(demand_path) > max_horizon:
        raise ValueError(f"exhaustive validation is restricted to T <= {max_horizon}")
    best_reward = float("-inf")
    best_actions: tuple[int, ...] | None = None
    count = 0
    for actions in itertools.product(ACTION_ORDER, repeat=len(demand_path)):
        count += 1
        reward = evaluate_sequence(model, demand_path, actions)["reward"]
        if reward > best_reward:
            best_reward, best_actions = reward, actions
    assert best_actions is not None
    return {**evaluate_sequence(model, demand_path, best_actions),
            "sequences_evaluated": count}


def build_scenarios(horizon: int = DEFAULT_HORIZON) -> list[Scenario]:
    sequences = demand_sequences(horizon)
    return [Scenario(f"{profile_id}__{demand_id}", profile_id, demand_id,
                     demands, model)
            for profile_id, model in parameter_profiles().items()
            for demand_id, demands in sequences.items()]


def _demand_ids(demands: tuple[str, ...]) -> dict[str, str]:
    canonical_multiset = json.dumps(sorted(demands), separators=(",", ":"), ensure_ascii=False)
    canonical_order = json.dumps(demands, separators=(",", ":"), ensure_ascii=False)
    return {
        "multiset_sha256": hashlib.sha256(canonical_multiset.encode("utf-8")).hexdigest(),
        "ordered_sequence_sha256": hashlib.sha256(canonical_order.encode("utf-8")).hexdigest(),
    }


def _model_json(model: Model) -> dict[str, Any]:
    return {"k": model.k, "p": model.p, "r": model.r, "initial_experience_D0": model.d0}


def run_scenario(scenario: Scenario, tolerance: float = DEFAULT_TOLERANCE) -> dict[str, Any]:
    dynamic = optimize_dynamic(scenario.model, scenario.demands)
    static = optimize_best_static(scenario.model, scenario.demands)
    myopic = evaluate_myopic(scenario.model, scenario.demands)
    gap = dynamic["reward"] - static["reward"]
    demand_meta = _demand_ids(scenario.demands)
    return {
        "scenario_id": scenario.scenario_id,
        "profile_id": scenario.profile_id,
        "demand_id": scenario.demand_id,
        "configuration": {"N": N_AGENTS, "K": N_SKILLS, "T": len(scenario.demands),
                          "period_duration": 1, "effort_per_period": 1,
                          "task_to_skill": TASK_TO_SKILL,
                          "parameters": _model_json(scenario.model)},
        "demand_sequence": list(scenario.demands),
        "demand_identity": demand_meta,
        "policies": {"OPT-DYNAMIC": dynamic, "BEST-STATIC": static, "MYOPIC": myopic},
        "dynamic_vs_static_gap": gap,
        "dynamic_beats_static_by_tolerance": gap > tolerance,
        "genuine_reassignment": any(
            dynamic["allocations"][t] != dynamic["allocations"][u]
            for t in range(len(scenario.demands)) for u in range(t)
            if scenario.demands[t] == scenario.demands[u]
        ),
        "stationary_by_task_type": all(
            len({dynamic["allocations"][t] for t, task in enumerate(scenario.demands)
                 if task == target}) <= 1
            for target in TASK_TO_SKILL
        ),
        "reward_definition": "sum over periods of productivity of the assigned agent-skill at period start; one unit effort",
    }


def _source_revision() -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], check=True,
                                capture_output=True, text=True, timeout=2)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def run_study(*, tolerance: float = DEFAULT_TOLERANCE) -> dict[str, Any]:
    scenarios = [run_scenario(scenario, tolerance) for scenario in build_scenarios()]
    validation_cases = []
    for scenario in build_scenarios():
        prefix = scenario.demands[:6]
        dynamic = optimize_dynamic(scenario.model, prefix)
        exhaustive = exhaustive_optimum(scenario.model, prefix)
        difference = dynamic["reward"] - exhaustive["reward"]
        validation_cases.append({"scenario_id": scenario.scenario_id,
                                 "horizon": len(prefix),
                                 "dp_reward": dynamic["reward"],
                                 "exhaustive_reward": exhaustive["reward"],
                                 "absolute_difference": abs(difference),
                                 "passed": abs(difference) <= tolerance})
    positive = [row for row in scenarios if row["dynamic_beats_static_by_tolerance"]]
    return {
        "experiment": "HLS-E2.1",
        "status": "small deterministic parameter study; not a campaign",
        "scientific_interpretation": (
            "No positive dynamic-versus-best-static case was observed in this design. "
            "The tested model has independent skill-specific experience and reward, "
            "so this result is consistent with the discrete-convexity argument in the protocol."
            if not positive else
            "At least one positive dynamic-versus-best-static case was found; inspect its full trajectory and parameters."
        ),
        "model": {
            "equation": "P_ik(D)=k_ik*(D+p_ik)/(D+p_ik+r_ik)",
            "production_timing": "evaluate at D_t, then update D_next=D_t+1 for the assigned agent-skill",
            "task_types": TASK_TO_SKILL,
            "feasible_actions": "one unit-effort assignment to either agent for the task's skill",
            "reward_unit": "productivity/output units per one-unit task; assumed calibrated",
            "simplifications": [
                "one task per period; each type requires exactly one corresponding skill",
                "unit effort and unit experience increment; no shared cross-task resource coupling",
                "skills and agent-skill experience cells evolve independently",
                "reward is task-skill output, with no CES, threshold, costs, teaching, noise, or switching cost",
            ],
        },
        "numerical_tolerance": tolerance,
        "reproducibility": {"deterministic": True, "random_seed": None,
                            "randomness": "none", "python_version": platform.python_version(),
                            "repository_head": _source_revision(),
                            "experiment_source_sha256": hashlib.sha256(
                                Path(__file__).read_bytes()
                            ).hexdigest(),
                            "repository_head_is_not_a_claim_of_committed_experiment_source": True,
                            "runtime_measurements_are_reproducible": False},
        "scenario_count": len(scenarios),
        "positive_case_count": len(positive),
        "validation_results": {
            "dp_matches_independent_exhaustive_search": all(x["passed"] for x in validation_cases),
            "tolerance": tolerance,
            "small_horizon_cases": validation_cases,
            "reward_matches_reported_trajectory": all(
                abs(row["policies"][policy]["reward"] - sum(
                    period["reward"] for period in row["policies"][policy]["trajectory"]
                )) <= tolerance
                for row in scenarios for policy in ("OPT-DYNAMIC", "BEST-STATIC", "MYOPIC")
            ),
            "all_dynamic_paths_stationary_by_task_type": all(
                row["stationary_by_task_type"] for row in scenarios
            ),
        },
        "structural_check": {
            "claim": "For each skill, cumulative reward F_i(n)=sum_{m=0}^{n-1}P_i(D0_i+m) has increasing discrete increments. Thus F_0(n0)+F_1(n-n0) is convex in n0 and its maximum occurs at an endpoint; with no cross-skill or shared-resource coupling, assigning every occurrence of a task type to one agent is at least as good as splitting it dynamically.",
            "scope": "applies only to the declared independent-skill, linear-output, unit-task model; it does not establish a result for coupled tasks or shared period capacities",
            "classification": "mathematical deduction from the specified model",
        },
        "scenarios": scenarios,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path("results/analysis/hls_e2/e2_1_results.json"))
    parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE)
    args = parser.parse_args(argv)
    if args.tolerance < 0:
        parser.error("--tolerance must be non-negative")
    payload = run_study(tolerance=args.tolerance)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(f"Wrote {len(payload['scenarios'])} deterministic scenarios to {args.output}")
    print(payload["scientific_interpretation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
