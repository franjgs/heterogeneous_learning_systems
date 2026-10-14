"""Incremental dynamic scenario extension for HLS Laboratory v1.

Reuses CE-25 problem/action/production/evaluation contracts and MIS-v2's
per-cell exponential capability law. This does not replace G0 or multi-step
DISCOVER.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from random import Random
from typing import Sequence

from .discover_develop_v2 import capability_after_exposure, eta_to_lambda
from .discover_v0 import production_inputs
from .hls_lab_v1 import (
    EpisodeRecord,
    ExpertState,
    Organization,
    OrganizationState,
    ProblemSpec,
    RunResult,
    TeamState,
    _action_id,
    _view,
    evaluate_problem,
)


@dataclass(frozen=True)
class LearningProfile:
    """MIS-v2 eta by expert and capability in the existing 3x2 geometry."""

    eta: tuple[tuple[float, float], tuple[float, float], tuple[float, float]]

    def __post_init__(self) -> None:
        if len(self.eta) != 3 or any(len(row) != 2 for row in self.eta):
            raise ValueError("expected 3x2 learning rates")
        for row in self.eta:
            for value in row:
                eta_to_lambda(value)


@dataclass(frozen=True)
class DemandRegime:
    """A fixed distribution over functional requirements."""

    label: str
    requirements: tuple[tuple[float, float], ...]
    probabilities: tuple[float, ...]

    def __post_init__(self) -> None:
        if (not self.label or not self.requirements
                or len(self.requirements) != len(self.probabilities)):
            raise ValueError("invalid demand regime")
        if any(len(req) != 2 or any(not isfinite(v) or v < 0 for v in req)
               or sum(req) <= 0 for req in self.requirements):
            raise ValueError("invalid requirements")
        if (any(not isfinite(p) or p < 0 for p in self.probabilities)
                or abs(sum(self.probabilities) - 1.0) > 1e-9):
            raise ValueError("probabilities must sum to one")


def generate_problems(
    schedule: Sequence[tuple[DemandRegime, int]], *, seed: int, budget: float = 1.0
) -> tuple[ProblemSpec, ...]:
    """Generate one reproducible exogenous, potentially nonstationary stream."""
    rng = Random(seed)
    result = []
    for regime, count in schedule:
        if count < 0:
            raise ValueError("negative duration")
        for _ in range(count):
            draw = rng.random()
            cumulative = 0.0
            selected = len(regime.probabilities) - 1
            for index, probability in enumerate(regime.probabilities):
                cumulative += probability
                if draw < cumulative:
                    selected = index
                    break
            requirements = regime.requirements[selected]
            # Equal requirement vectors denote the same stable tabular context.
            problem_id = f"r:{requirements[0]:.12g},{requirements[1]:.12g}"
            result.append(ProblemSpec(problem_id, requirements, budget))
    if not result:
        raise ValueError("empty schedule")
    return tuple(result)


def advance_team(
    team: TeamState, action, profile: LearningProfile, *, enabled: bool
) -> TeamState:
    """Apply the frozen MIS-v2 exponential gap law with cell-specific rates."""
    experts = []
    for expert_index, expert in enumerate(team.experts):
        competence = tuple(
            capability_after_exposure(
                expert.competence_real[skill],
                action[expert_index][skill],
                rate=eta_to_lambda(profile.eta[expert_index][skill]),
            )
            if enabled else expert.competence_real[skill]
            for skill in range(2)
        )
        experience = tuple(
            expert.experience[skill] + action[expert_index][skill]
            for skill in range(2)
        )
        performance = tuple(
            expert.performance[skill]
            + expert.competence_real[skill] * action[expert_index][skill]
            for skill in range(2)
        )
        experts.append(ExpertState(
            expert.expert_id, competence, competence, experience, performance
        ))
    return TeamState(tuple(experts))


def run_dynamic_sequence(
    initial_team: TeamState,
    problems: tuple[ProblemSpec, ...],
    organization: Organization,
    *,
    learning: LearningProfile,
    individual_learning: bool = True,
    organizational_learning: bool = False,
    seed: int = 0,
    initial_organization_state: OrganizationState | None = None,
) -> RunResult:
    """Run matched exogenous problems while each policy evolves its own state."""
    if not problems:
        raise ValueError("empty problems")
    team = initial_team
    org = initial_organization_state or OrganizationState()
    records = []
    previous_action = None
    cumulative_successes = 0
    cumulative_cost = 0.0

    if organizational_learning and not callable(getattr(organization, "observe", None)):
        raise ValueError("organizational learning requires an organization observe method")

    for episode, problem in enumerate(problems):
        view = _view(problem, team)
        theta_before = org.values
        version_before = org.update_count
        experience_before = tuple(expert.experience for expert in team.experts)
        action = organization.choose(view, org)
        if action not in view.feasible_actions:
            raise ValueError("organization selected an infeasible action")

        competence_before = team.real_matrix
        estimated_before = team.estimated_matrix
        individual_outputs = tuple(
            tuple(action[i][k] * competence_before[i][k] for k in range(2))
            for i in range(3)
        )
        outputs = production_inputs(competence_before, action)
        outcome = evaluate_problem(outputs, problem.requirements)
        effort = sum(sum(row) for row in action)
        cost = effort * problem.resource_cost_per_unit
        team = advance_team(team, action, learning, enabled=individual_learning)
        reward = float(outcome.success)

        if organizational_learning:
            org = organization.observe(  # type: ignore[attr-defined]
                org, problem.problem_id, action, reward, enabled=True
            )

        cumulative_successes += int(outcome.success)
        cumulative_cost += cost
        records.append(EpisodeRecord(
            episode=episode,
            seed=seed,
            problem_id=problem.problem_id,
            requirements=problem.requirements,
            difficulty=problem.difficulty,
            orientation=problem.orientation,
            budget=problem.resource_budget,
            competence_before=competence_before,
            estimated_before=estimated_before,
            experience_before=experience_before,
            action=action,
            action_id=_action_id(action),
            individual_outputs=individual_outputs,
            outputs=outputs,
            success=outcome.success,
            deficits=outcome.deficits,
            normalized_deficit=outcome.normalized_deficit,
            margin=outcome.margin,
            effort=effort,
            resource_cost=cost,
            individual_performance_cumulative=tuple(
                expert.performance for expert in team.experts
            ),
            competence_after=team.real_matrix,
            estimated_after=team.estimated_matrix,
            experience_after=tuple(expert.experience for expert in team.experts),
            organization_theta_before=theta_before,
            organization_theta_after=org.values,
            organization_updated=org.update_count > version_before,
            organization_action_changed=(
                previous_action is not None and previous_action != action
            ),
            organization_reward=reward,
            cumulative_successes=cumulative_successes,
            cumulative_resource_cost=cumulative_cost,
        ))
        previous_action = action

    return RunResult(
        organization.name, seed, individual_learning, organizational_learning,
        tuple(records), team, org,
    )


def compare_organizations(
    initial_team: TeamState,
    problems: tuple[ProblemSpec, ...],
    organizations: Sequence[tuple[Organization, bool]],
    *,
    learning: LearningProfile,
    seed: int = 0,
) -> tuple[RunResult, ...]:
    """Run each policy from the same initial state and shared problem sequence."""
    return tuple(
        run_dynamic_sequence(
            initial_team, problems, policy, learning=learning,
            organizational_learning=learns, seed=seed,
        )
        for policy, learns in organizations
    )
