#!/usr/bin/env python3
"""Small paired comparison of MIS-v2 and Nembhard Direct in one HLS setup."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path
from types import SimpleNamespace

from hls.hls_lab_nk_geometry import (
    OrganizationConfigNK,
    OrganizationResourcesNK,
    ProblemSpecNK,
    ProductiveAllocationNK,
    validate_productive_allocation_nk,
)
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from hls.hls_lab_nk_nembhard import (
    NembhardDirectProfileNK,
    NembhardDirectStateNK,
    NembhardOutputUnitContract,
    advance_nembhard_experience_nk,
    nembhard_productive_outputs_nk,
)
from hls.hls_lab_nk_nembhard_router import (
    NembhardOracleDecisionViewNK,
    NembhardOracleRouterNK,
)
from hls.hls_lab_nk_production import P0ProductionOnlyNK
from hls.linucb import LinUCBDisjoint, alpha_from_delta
from hls.synthetic.c5 import NonStationaryTaskDemand
from hls.synthetic.state import WorldState


OUTPUT = Path("results/experiments/hls_learning_mechanism_comparison/results.json")
AGENTS = ("agent_0", "agent_1", "agent_2")
TASKS = ("task_0", "task_1", "task_2")
INITIAL_COMPETENCE = (
    (0.85, 0.20, 0.20),
    (0.20, 0.85, 0.20),
    (0.20, 0.20, 0.85),
)
ETA = ((0.15, 0.15, 0.15),) * 3
LEARNING = LearningProfileNK(ETA)
HORIZON = 90
REPETITIONS = 10
DELTA = 0.05
RESOURCE_BUDGET = 1.0
TASK_REQUIREMENT = 0.90
SPECIALIZED_MAP = (0, 1, 2)
MECHANISMS = ("MIS_V2", "NEMBHARD_DIRECT")
ORGANIZATIONS = ("LINUCB", "FIXED_SPECIALIZED", "REACTIVE_P0")
ORG = OrganizationConfigNK(
    AGENTS, TASKS, INITIAL_COMPETENCE, (1.0, 1.0, 1.0), RESOURCE_BUDGET,
)
RESOURCES = OrganizationResourcesNK.from_organization(ORG)
NEMBHARD_PROFILE = NembhardDirectProfileNK(
    asymptotic_productivity=((1.0,) * 3,) * 3,
    # Calibration: with k=r=1, p=C0/(1-C0) makes P(D=0)=C0.
    prior_experience=tuple(
        tuple(value / (1.0 - value) for value in row)
        for row in INITIAL_COMPETENCE
    ),
    experience_scale=((1.0,) * 3,) * 3,
)
NEMBHARD_UNITS = NembhardOutputUnitContract(
    "one assignment per period", "period", "assignment-period",
    "normalized effective output", "normalized effective output",
)


def c5_demand(horizon: int = HORIZON) -> NonStationaryTaskDemand:
    phases = (
        (0.70, 0.20, 0.10),
        (0.10, 0.20, 0.70),
        (0.20, 0.70, 0.10),
    )
    distributions = {
        period: dict(zip(TASKS, phases[min(2, 3 * period // horizon)]))
        for period in range(horizon)
    }
    return NonStationaryTaskDemand(distributions)


def make_demand_trajectory(seed: int, horizon: int) -> tuple[int, ...]:
    process = c5_demand(horizon)
    rng = random.Random(seed)
    history = []
    state = WorldState(INITIAL_COMPETENCE, time=0)
    sequence = []
    for period in range(horizon):
        task = process.sample_task(period, state, history, rng)
        sequence.append(TASKS.index(task))
        history.append(SimpleNamespace(task=task))
    return tuple(sequence)


def actions_for_task(task: int) -> tuple[ProductiveAllocationNK, ...]:
    return tuple(
        tuple(tuple(1.0 if agent == i and task == k else 0.0
                    for k in range(len(TASKS)))
              for i in range(len(AGENTS)))
        for agent in range(len(AGENTS))
    )


def problem_for_task(task: int) -> ProblemSpecNK:
    return ProblemSpecNK(
        TASKS[task],
        tuple(TASK_REQUIREMENT if k == task else 0.0 for k in range(len(TASKS))),
        RESOURCE_BUDGET,
    )


def _productivity(mechanism: str, state):
    if mechanism == "MIS_V2":
        return state
    if mechanism == "NEMBHARD_DIRECT":
        zero = tuple((0.0,) * len(TASKS) for _ in AGENTS)
        _, productivity = nembhard_productive_outputs_nk(
            zero, state, NEMBHARD_PROFILE, period_duration=1.0,
        )
        return productivity
    raise ValueError(f"unknown mechanism {mechanism!r}")


def _linucb_contexts(task: int, productivity):
    task_one_hot = tuple(1.0 if k == task else 0.0 for k in range(len(TASKS)))
    current_quality = tuple(productivity[agent][task] for agent in range(len(AGENTS)))
    vector = task_one_hot + current_quality
    return (vector,) * len(AGENTS)


def _reactive_agent(mechanism: str, task: int, state, productivity,
                    problem: ProblemSpecNK, actions: tuple[ProductiveAllocationNK, ...]) -> int:
    if mechanism == "MIS_V2":
        _, action = P0ProductionOnlyNK().choose(actions, productivity, problem)
    else:
        # The existing Nembhard ORACLE uses the same P0 functional-effort
        # ordering over current productivity, with the same one-agent catalog.
        zero = (0.0,) * len(TASKS)
        one = tuple(1.0 if k == task else 0.0 for k in range(len(TASKS)))
        catalog = tuple((zero, one) for _ in AGENTS)
        choice = NembhardOracleRouterNK().choose(
            NembhardOracleDecisionViewNK(
                RESOURCES, problem, state, NEMBHARD_PROFILE, period_duration=1.0,
            ),
            max_candidates=2 ** len(AGENTS),
            per_agent_effort_choices=catalog,
        )
        action = choice.allocation
    return next(i for i, row in enumerate(action) if row[task] == 1.0)


def _initial_state(mechanism: str):
    if mechanism == "MIS_V2":
        return INITIAL_COMPETENCE
    return NembhardDirectStateNK.zeros(len(AGENTS), len(TASKS))


def run_episode(mechanism: str, organization: str, tasks: tuple[int, ...],
                alpha: float, *, keep_trace: bool = True) -> dict:
    state = _initial_state(mechanism)
    linucb = LinUCBDisjoint(len(AGENTS), 2 * len(TASKS), alpha) if organization == "LINUCB" else None
    total_reward = 0.0
    successful_tasks = 0
    decisions = [[0 for _ in TASKS] for _ in AGENTS]
    trace = []
    for period, task in enumerate(tasks):
        productivity = _productivity(mechanism, state)
        contexts = _linucb_contexts(task, productivity)
        actions = actions_for_task(task)
        problem = problem_for_task(task)
        scores = None
        if organization == "LINUCB":
            assert linucb is not None
            scores = linucb.scores(contexts)
            agent = linucb.select(contexts)
        elif organization == "FIXED_SPECIALIZED":
            agent = SPECIALIZED_MAP[task]
        elif organization == "REACTIVE_P0":
            agent = _reactive_agent(mechanism, task, state, productivity, problem, actions)
        else:
            raise ValueError(f"unknown organization {organization!r}")

        allocation = actions[agent]
        if not validate_productive_allocation_nk(allocation, ORG, problem):
            raise AssertionError("selected action violates the common resource/action contract")
        reward = productivity[agent][task]
        total_reward += reward
        successful_tasks += int(reward + 1e-12 >= TASK_REQUIREMENT)
        decisions[agent][task] += 1

        if mechanism == "MIS_V2":
            next_state = mis_v2_transition_nk(state, allocation, LEARNING, enabled=True)
        else:
            next_state = advance_nembhard_experience_nk(state, allocation, period_duration=1.0)
        if linucb is not None:
            linucb.observe_reward(reward)

        if keep_trace:
            row = {
                "period": period,
                "task": TASKS[task],
                "context_features": list(contexts[0]),
                "selected_agent": AGENTS[agent],
                "reward_effective_output": reward,
                "task_success_at_0_90": reward + 1e-12 >= TASK_REQUIREMENT,
                "productivity_by_agent_task_before": [list(values) for values in productivity],
                "resource_used": sum(map(sum, allocation)),
            }
            if mechanism == "MIS_V2":
                row["competence_before"] = [list(values) for values in state]
                row["competence_after"] = [list(values) for values in next_state]
            else:
                row["experience_before"] = [list(values) for values in state.experience]
                row["experience_after"] = [list(values) for values in next_state.experience]
            if linucb is not None:
                row["linucb_scores_before"] = list(scores)
                row["linucb_coefficients_after"] = [list(values) for values in linucb.coefficient_estimates]
            trace.append(row)
        state = next_state

    result = {
        "cumulative_effective_output": total_reward,
        "mean_effective_output_per_period": total_reward / len(tasks),
        "functional_success_rate_threshold_0_90": successful_tasks / len(tasks),
        "total_resource_used": float(len(tasks)),
        "assignment_counts_agent_by_task": decisions,
        "final_state": ([list(row) for row in state] if mechanism == "MIS_V2"
                        else [list(row) for row in state.experience]),
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
        raise ValueError("need at least two seeds and all three C5 demand phases")
    alpha = alpha_from_delta(delta)
    trajectories = {seed: make_demand_trajectory(seed, horizon) for seed in range(repetitions)}
    replications = []
    for seed, tasks in trajectories.items():
        mechanisms = {
            mechanism: {
                organization: run_episode(mechanism, organization, tasks, alpha)
                for organization in ORGANIZATIONS
            }
            for mechanism in MECHANISMS
        }
        replications.append({
            "seed": seed,
            "task_sequence": [TASKS[task] for task in tasks],
            "mechanisms": mechanisms,
        })

    summary = {}
    for mechanism in MECHANISMS:
        summary[mechanism] = {}
        for organization in ORGANIZATIONS:
            episodes = [rep["mechanisms"][mechanism][organization] for rep in replications]
            summary[mechanism][organization] = {
                "mean_cumulative_effective_output": _mean([e["cumulative_effective_output"] for e in episodes]),
                "sd_cumulative_effective_output": _sd([e["cumulative_effective_output"] for e in episodes]),
                "mean_effective_output_per_period": _mean([e["mean_effective_output_per_period"] for e in episodes]),
                "mean_functional_success_rate": _mean([e["functional_success_rate_threshold_0_90"] for e in episodes]),
                "mean_total_resource_used": _mean([e["total_resource_used"] for e in episodes]),
                "mean_assignment_counts_agent_by_task": [
                    [_mean([e["assignment_counts_agent_by_task"][i][k] for e in episodes])
                     for k in range(len(TASKS))]
                    for i in range(len(AGENTS))
                ],
                "mean_final_state": [
                    [_mean([e["final_state"][i][k] for e in episodes]) for k in range(len(TASKS))]
                    for i in range(len(AGENTS))
                ],
            }

    paired = {}
    for mechanism in MECHANISMS:
        for left, right in (("LINUCB", "FIXED_SPECIALIZED"),
                            ("LINUCB", "REACTIVE_P0"),
                            ("REACTIVE_P0", "FIXED_SPECIALIZED")):
            values = [
                rep["mechanisms"][mechanism][left]["cumulative_effective_output"]
                - rep["mechanisms"][mechanism][right]["cumulative_effective_output"]
                for rep in replications
            ]
            paired[f"{mechanism}:{left}_minus_{right}"] = {"mean": _mean(values), "sd": _sd(values), "per_seed": values}
    for organization in ORGANIZATIONS:
        values = [
            rep["mechanisms"]["NEMBHARD_DIRECT"][organization]["cumulative_effective_output"]
            - rep["mechanisms"]["MIS_V2"][organization]["cumulative_effective_output"]
            for rep in replications
        ]
        paired[f"NEMBHARD_DIRECT_minus_MIS_V2:{organization}"] = {
            "mean": _mean(values), "sd": _sd(values), "per_seed": values,
        }

    return {
        "experiment": "HLS external learning-mechanism comparison: MIS-v2 vs Nembhard Direct",
        "ontology": {
            "A_scenario": "3 agents × 3 task types; C5 demand; one unit of current-task work per period; same paired task path and resource catalog.",
            "B_mechanisms": "MIS-v2 evolves bounded competence; Nembhard Direct evolves cumulative task-specific experience and evaluates the published direct productivity curve. Nembhard indirect-transfer component is excluded.",
            "C_organizations": "same LinUCB-disjoint, fixed specialist map and current-output reactive selector under both mechanisms.",
            "policy_learning_vs_agent_learning": "LinUCB updates its arm-specific selection model; the mechanism updates only the agent-task physical state. These states are logged separately.",
        },
        "configuration": {
            "agents": list(AGENTS), "tasks": list(TASKS), "horizon": horizon,
            "repetitions": repetitions, "seeds": list(trajectories),
            "initial_competence_agent_by_task": [list(row) for row in INITIAL_COMPETENCE],
            "MIS_v2_eta": [list(row) for row in ETA],
            "Nembhard_parameters": {
                "asymptotic_productivity_k": [list(row) for row in NEMBHARD_PROFILE.asymptotic_productivity],
                "prior_experience_p": [list(row) for row in NEMBHARD_PROFILE.prior_experience],
                "experience_scale_r": [list(row) for row in NEMBHARD_PROFILE.experience_scale],
                "calibration": "k=1,r=1,p=C0/(1-C0), hence Eq.(1) gives P(D=0)=C0 cellwise; p is an equivalent-prior-exposure calibration, not an empirical Nembhard parameter estimate.",
                "unit_contract": {
                    "effort_intensity_unit": NEMBHARD_UNITS.effort_intensity_unit,
                    "duration_unit": NEMBHARD_UNITS.duration_unit,
                    "exposure_unit": NEMBHARD_UNITS.exposure_unit,
                    "output_unit": NEMBHARD_UNITS.output_unit,
                    "requirement_unit": NEMBHARD_UNITS.requirement_unit,
                },
            },
            "demand": "existing C5 NonStationaryTaskDemand, three 30-period phases (0.70,0.20,0.10), (0.10,0.20,0.70), (0.20,0.70,0.10)",
            "reward": "deterministic normalized effective output per assigned unit: MIS competence C[i,k] or Nembhard P[i,k](D), both in [0,1]; initial expected output matrices are exactly matched.",
            "resources": "one selected agent, effort=1, shared budget=1, individual limit=1, period duration=1; no separate development cost",
            "action_catalog": "for task k, exactly three actions, one unit assigned to a single agent on k; same catalog for all methods and mechanisms",
            "fixed_policy": "task_i maps to agent_i; predeclared from the diagonal initial specialization, no evaluation outcomes used",
            "reactive_policy": "current-period P0 functional-effort ranking; MIS uses existing P0ProductionOnlyNK, Nembhard uses existing NembhardOracleRouterNK with the same one-agent catalog and current true productivity; no lookahead",
            "LinUCB": "unmodified disjoint implementation; 6 features (task one-hot plus current productivity of all agents for that task), alpha from Li et al. Eq.(4) with delta=0.05; only selected reward observed",
            "information": "task and current true task-specific competence/productivity are observable to all; no future demand; no unselected reward; Nembhard k,p,r and D are known in this synthetic validation",
            "transfer": "disabled / absent in both compared transitions; no cross-task or cross-agent state update",
            "Nembhard_fidelity_boundary": "Eq.(1) direct-experience curve and HLS D+=effort×duration convention only; not a full reproduction of Nembhard & Bentefouet (2015).",
        },
        "paired_comparisons": paired,
        "summary": summary,
        "replications": replications,
        "limitations": [
            "The Nembhard source's indirect-transfer model is not integrated; prior source audit records unresolved simultaneity and dimensional ambiguities in Eqs. (A-3)/(A-4).",
            "Nembhard p values are calibrated to match the MIS initial output profile; they are not published empirical estimates.",
            "The comparison uses normalized synthetic effective output and perfect state observation, not a practical production dataset.",
            "C5 task sequence is stochastic and paired; rewards are deterministic conditional on state and assignment, so SD reflects demand-path variation only.",
            "LinUCB's context/reward relation is linear by construction, but this small pilot does not claim its published regret guarantee or general superiority.",
        ],
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
    for mechanism, organizations in results["summary"].items():
        print(mechanism)
        for organization, metrics in organizations.items():
            print(f"  {organization}: output={metrics['mean_cumulative_effective_output']:.3f} "
                  f"(SD {metrics['sd_cumulative_effective_output']:.3f}), "
                  f"success={metrics['mean_functional_success_rate']:.3f}, "
                  f"state={metrics['mean_final_state']}")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
