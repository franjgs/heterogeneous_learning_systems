"""Small paired execution harness for the HLS-E1 anticipation design.

This module supplies a bounded 2-agent/2-task G0 instance and deterministic
replay tapes. It is infrastructure for tests and later explicitly authorized
small runs; importing it never launches an experiment or campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Hashable, Mapping

from hls.synthetic.c3 import BudgetedDevelopmentResources, with_development_budget
from hls.synthetic.c5 import (
    NonStationaryTaskDemand,
    StationaryTaskDemand,
)
from hls.synthetic.components import (
    A1MixtureOpportunityKernel,
    A1SaturatingDevelopmentKernel,
    BoundedMatrixCompetence,
    CompetenceRewardModel,
    ContractInformationModel,
)
from hls.synthetic.environment import SyntheticEnvironment
from hls.synthetic.exact import (
    BestStaticRoutingSolution,
    DemandExecutablePolicy,
    DemandPolicySolution,
    ExactProblem,
    _admissible_development_actions,
    _physical_next_state,
    solve_demand_best_static_routing,
    solve_demand_exact_hls,
    solve_demand_exact_strong_sep,
    solve_demand_myopic,
)
from hls.synthetic.interfaces import Opportunity
from hls.synthetic.randomness import SeededRandomSource
from hls.synthetic.state import WorldState
from hls.synthetic.trajectory import Trajectory, TransitionRecord


AGENTS = ("M1", "M2")
TASKS = (1, 2)
INITIAL_COMPETENCE = ((0.8, 0.8), (0.6, 0.6))
TERMINAL_TASK = 1


@dataclass(frozen=True)
class E1Instance:
    problem: ExactProblem
    initial_state: WorldState


@dataclass(frozen=True)
class ExogenousReplay:
    demand_seed: int
    opportunity_seed: int
    task_path: tuple[Hashable, ...]
    opportunity_uniforms: tuple[float, ...]


@dataclass(frozen=True)
class PairedEpisodeResult:
    policy_id: str
    task_path: tuple[Hashable, ...]
    trace: Trajectory
    terminal_reward: float
    cumulative_reward: float
    development_cost: float
    objective: float


def build_e1_instance(
    *,
    eta: float,
    demand: str,
    horizon: int = 4,
) -> E1Instance:
    """Build one design cell; no random draws or execution occur here."""
    if not 0.0 <= eta <= 1.0:
        raise ValueError("eta must lie in [0, 1]")
    if horizon < 1:
        raise ValueError("horizon must be positive")
    if demand == "stationary":
        task_process = StationaryTaskDemand({1: 0.5, 2: 0.5})
    elif demand == "changing":
        task_process = NonStationaryTaskDemand(
            {
                time: ({1: 0.8, 2: 0.2} if time < horizon // 2 else {1: 0.2, 2: 0.8})
                for time in range(horizon)
            }
        )
    else:
        raise ValueError("demand must be 'stationary' or 'changing'")

    learner_indices = {agent: index for index, agent in enumerate(AGENTS)}
    task_indices = {task: index for index, task in enumerate(TASKS)}
    environment = SyntheticEnvironment(
        tasks=task_process,
        competence=BoundedMatrixCompetence(INITIAL_COMPETENCE),
        opportunities=A1MixtureOpportunityKernel(
            baseline={1: 0.0, 2: 0.0},
            executor_values={
                ("M1", 1): 0.0,
                ("M2", 1): 1.0,
                ("M1", 2): 0.0,
                ("M2", 2): 1.0,
            },
            rho=1.0,
        ),
        development=A1SaturatingDevelopmentKernel(
            learner_indices=learner_indices,
            competence_indices=task_indices,
            target_competence=1,
            eta=eta,
        ),
        reward=CompetenceRewardModel(learner_indices, task_indices),
        resources=BudgetedDevelopmentResources(
            budget_per_development=1.0,
            objective_cost_per_development=0.0,
            beta=1.0,
        ),
        information=ContractInformationModel(),
        randomness=SeededRandomSource(0),
    )
    problem = ExactProblem(
        environment=environment,
        operational_actions=AGENTS,
        horizon=horizon,
        terminal_task=TERMINAL_TASK,
        demand_process=task_process,
    )
    return E1Instance(
        problem=problem,
        initial_state=with_development_budget(environment.initial_state(), 1.0),
    )


@dataclass(frozen=True)
class _PreviousTask:
    task: Hashable


def make_replay(instance: E1Instance, seed: int) -> ExogenousReplay:
    """Generate independent, policy-invariant demand and opportunity tapes."""
    demand_seed = seed ^ 0x5EED_1001
    opportunity_seed = seed ^ 0x5EED_2002
    demand_rng = random.Random(demand_seed)
    opportunity_rng = random.Random(opportunity_seed)
    process = instance.problem.demand_process
    if process is None:
        raise ValueError("E1 instance must declare a demand process")

    history: list[_PreviousTask] = []
    task_path = []
    initial_state = instance.initial_state
    for time in range(instance.problem.horizon):
        task = process.sample_task(
            time, initial_state, tuple(history), demand_rng
        )
        task_path.append(task)
        history.append(_PreviousTask(task))
    uniforms = tuple(
        opportunity_rng.random() for _ in range(instance.problem.horizon)
    )
    return ExogenousReplay(
        demand_seed=demand_seed,
        opportunity_seed=opportunity_seed,
        task_path=tuple(task_path),
        opportunity_uniforms=uniforms,
    )


def four_policies(instance: E1Instance) -> Mapping[str, DemandExecutablePolicy]:
    """Construct all four executable policies on the identical G0 problem."""
    return {
        policy_id: solution.policy
        for policy_id, solution in four_policy_solutions(instance).items()
    }


def four_policy_solutions(
    instance: E1Instance,
) -> Mapping[str, DemandPolicySolution | BestStaticRoutingSolution]:
    """Return executable policy solutions and exact expected values."""
    problem, initial = instance.problem, instance.initial_state
    return {
        "BEST_STATIC": solve_demand_best_static_routing(problem, initial_state=initial),
        "MYOPIC": solve_demand_myopic(problem, initial_state=initial),
        "STRONG_SEP": solve_demand_exact_strong_sep(problem, initial_state=initial),
        "HLS": solve_demand_exact_hls(problem, initial_state=initial),
    }


def run_policy(
    instance: E1Instance,
    policy_id: str,
    policy: DemandExecutablePolicy,
    replay: ExogenousReplay,
) -> PairedEpisodeResult:
    """Execute one policy on a pre-generated exogenous path and shock tape."""
    problem = instance.problem
    environment = problem.environment
    if environment.resources.beta != 1.0:
        raise ValueError("E1 replay accounting currently requires beta=1")
    if (
        len(replay.task_path) != problem.horizon
        or len(replay.opportunity_uniforms) != problem.horizon
    ):
        raise ValueError("replay length must equal the declared horizon")

    state = instance.initial_state
    trace = Trajectory()
    operational_total = 0.0
    development_total = 0.0
    for time, (task, opportunity_uniform) in enumerate(
        zip(replay.task_path, replay.opportunity_uniforms)
    ):
        if state.time != time:
            raise ValueError("state time is inconsistent with replay period")
        action = policy.choose_operational_action(state, task)
        if action not in problem.operational_actions:
            raise ValueError("policy selected an infeasible operational action")
        probability = environment.opportunities.probability(
            state, task, action, trace.transitions
        )
        if not 0.0 <= probability <= 1.0:
            raise ValueError("opportunity probability must lie in [0, 1]")
        opportunity = Opportunity(opportunity_uniform < probability)
        admissible = _admissible_development_actions(
            problem, state, opportunity
        )
        development = policy.choose_development_action(
            state, task, action, opportunity
        )
        if development not in admissible:
            raise ValueError("policy selected an infeasible development action")
        next_state = _physical_next_state(
            problem, state, opportunity, development
        )
        reward = environment.reward.operational_reward(state, task, action)
        cost = environment.resources.development_cost(development)
        transition = TransitionRecord(
            state=state,
            task=task,
            operational_action=action,
            opportunity=opportunity,
            development_action=development,
            operational_reward=reward,
            development_cost=cost,
            next_state=next_state,
        )
        trace = trace.append(transition)
        operational_total += reward
        development_total += cost
        state = next_state

    terminal_reward = max(
        environment.reward.operational_reward(
            state, problem.terminal_task, action
        )
        for action in problem.operational_actions
    )
    objective = operational_total - development_total + terminal_reward
    return PairedEpisodeResult(
        policy_id=policy_id,
        task_path=replay.task_path,
        trace=trace,
        terminal_reward=terminal_reward,
        cumulative_reward=operational_total + terminal_reward,
        development_cost=development_total,
        objective=objective,
    )


def run_paired(
    instance: E1Instance,
    policies: Mapping[str, DemandExecutablePolicy],
    replay: ExogenousReplay,
) -> Mapping[str, PairedEpisodeResult]:
    """Run policy order-independently on one immutable replay realization."""
    return {
        policy_id: run_policy(instance, policy_id, policy, replay)
        for policy_id, policy in policies.items()
    }
