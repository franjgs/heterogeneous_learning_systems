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
from .discover_v0 import (
    DEFAULT_PRIOR,
    DEFAULT_SIGMA,
    DEFAULT_QUADRATURE_ORDER,
    THETA_1,
    THETA_2,
    bayes_update,
    ces_reward,
    means,
    production_inputs,
    unknown_policy_value,
)
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
    feasible_actions,
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
        competence_real = tuple(
            capability_after_exposure(
                expert.competence_real[skill],
                action[expert_index][skill],
                rate=eta_to_lambda(profile.eta[expert_index][skill]),
            )
            if enabled else expert.competence_real[skill]
            for skill in range(2)
        )
        competence_estimated = tuple(
            capability_after_exposure(
                expert.competence_estimated[skill],
                action[expert_index][skill],
                rate=eta_to_lambda(profile.eta[expert_index][skill]),
            )
            if enabled else expert.competence_estimated[skill]
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
            expert.expert_id, competence_real, competence_estimated,
            experience, performance,
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


@dataclass(frozen=True)
class UncertainProblem:
    """One functional task with a hidden DISCOVER CES environment type.

    ``theta`` is privileged simulator state and must never be passed to a
    policy. Functional requirements remain the visible task specification.
    """

    problem: ProblemSpec
    theta: tuple[float, float]

    def __post_init__(self) -> None:
        if self.theta not in (THETA_1, THETA_2):
            raise ValueError("theta must be one of DISCOVER's frozen environment types")


@dataclass(frozen=True)
class BeliefEpisodeRecord:
    """Decision record combining the v1 functional trace and DISCOVER belief."""

    problem_episode: int
    decision_in_problem: int
    true_environment_type: str  # privileged output metadata, never a policy input
    belief_before: float
    belief_after: float
    observation: float
    observation_noise: float
    true_expected_reward: float
    episode: EpisodeRecord


@dataclass(frozen=True)
class BeliefRunResult:
    policy: str
    seed: int
    decision_horizon: int
    records: tuple[BeliefEpisodeRecord, ...]
    final_team: TeamState
    final_organization: OrganizationState
    cumulative_true_expected_reward: float


@dataclass(frozen=True)
class DiscoverBeliefPolicy:
    """Adapter to DISCOVER's existing finite-horizon belief-state solver."""

    sigma: float = DEFAULT_SIGMA
    quadrature_order: int = DEFAULT_QUADRATURE_ORDER
    theta_1: tuple[float, float] = THETA_1
    theta_2: tuple[float, float] = THETA_2
    name: str = "discover_unknown_policy"

    def choose_belief(self, view, belief: float, remaining: int):
        value = unknown_policy_value(
            view.estimated_competencies,
            horizon=remaining,
            prior=belief,
            sigma=self.sigma,
            quadrature_order=self.quadrature_order,
            theta_1=self.theta_1,
            theta_2=self.theta_2,
        )
        action = value.first_actions[0]
        if action not in view.feasible_actions:
            raise ValueError(
                "DISCOVER's frozen solver uses the full action catalog; "
                "this problem's resource constraints exclude its selected action"
            )
        return action


def generate_uncertain_problems(
    schedule: Sequence[tuple[DemandRegime, int]],
    *,
    problem_seed: int,
    environment_seed: int,
    prior: float = DEFAULT_PRIOR,
    budget: float = 3.0,
) -> tuple[UncertainProblem, ...]:
    """Generate observable tasks and independent hidden DISCOVER types.

    The functional task stream and hidden reward-type stream use distinct
    seeded RNGs. Each type is fixed for one problem and redrawn at the next
    problem boundary, matching DISCOVER's belief-reset semantics.
    """
    if not isfinite(prior) or not 0.0 <= prior <= 1.0:
        raise ValueError("prior must lie in [0, 1]")
    problems = generate_problems(schedule, seed=problem_seed, budget=budget)
    rng = Random(environment_seed)
    return tuple(
        UncertainProblem(problem, THETA_1 if rng.random() < prior else THETA_2)
        for problem in problems
    )


def run_belief_sequence(
    initial_team: TeamState,
    problems: tuple[UncertainProblem, ...],
    organization,
    *,
    learning: LearningProfile,
    decision_horizon: int = 1,
    individual_learning: bool = True,
    organizational_learning: bool = False,
    prior: float = DEFAULT_PRIOR,
    sigma: float = DEFAULT_SIGMA,
    noise_seed: int = 0,
    seed: int = 0,
    initial_organization_state: OrganizationState | None = None,
) -> BeliefRunResult:
    """Run H decisions per task with latent types, observations, and MIS-v2.

    This is an additive DISCOVER-backed execution path. H=1 remains the
    one-decision case. Since DISCOVER's frozen value solver enumerates all 64
    actions, every task must admit that full catalog. The solver plans over
    fixed capabilities as in DISCOVER-v0; actual MIS-v2 development occurs
    between decisions but is not forecast inside its Bellman recursion.
    """
    if not problems:
        raise ValueError("empty problems")
    if not isinstance(decision_horizon, int) or decision_horizon < 1:
        raise ValueError("decision_horizon must be a positive integer")
    if not isfinite(prior) or not 0.0 <= prior <= 1.0:
        raise ValueError("prior must lie in [0, 1]")
    if not isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be finite and positive")
    if organizational_learning and not callable(getattr(organization, "observe", None)):
        raise ValueError("organizational learning requires an organization observe method")

    from .discover_v0 import JOINT_ACTIONS
    for item in problems:
        if feasible_actions(item.problem) != JOINT_ACTIONS:
            raise ValueError(
                "DISCOVER-backed execution requires all frozen joint actions "
                "to be feasible under each problem's resource limits"
            )

    team = initial_team
    org = initial_organization_state or OrganizationState()
    noise_rng = Random(noise_seed)
    records = []
    total_true_reward = 0.0
    cumulative_successes = 0
    cumulative_cost = 0.0
    previous_action = None

    for problem_episode, item in enumerate(problems):
        problem = item.problem
        # Frozen DISCOVER convention: belief resets at each problem boundary.
        belief = prior
        for decision_index in range(decision_horizon):
            remaining = decision_horizon - decision_index
            view = _view(problem, team)
            theta_before = org.values
            org_version_before = org.update_count
            experience_before = tuple(expert.experience for expert in team.experts)
            choose_belief = getattr(organization, "choose_belief", None)
            if callable(choose_belief):
                action = choose_belief(view, belief, remaining)
            else:
                action = organization.choose(view, org)
            if action not in view.feasible_actions:
                raise ValueError("organization selected an infeasible action")

            competence_before = team.real_matrix
            estimated_before = team.estimated_matrix
            outputs = production_inputs(competence_before, action)
            functional = evaluate_problem(outputs, problem.requirements)
            mu_true = ces_reward(outputs, item.theta)
            innovation = noise_rng.gauss(0.0, 1.0)
            observation = mu_true + sigma * innovation

            # Likelihood means are computed from the information available to
            # the organization; the generated observation uses physical truth.
            mu_1, mu_2 = means(
                estimated_before, action,
                theta_1=getattr(organization, "theta_1", THETA_1),
                theta_2=getattr(organization, "theta_2", THETA_2),
            )
            next_belief = bayes_update(belief, observation, mu_1, mu_2, sigma)

            individual_outputs = tuple(
                tuple(action[i][k] * competence_before[i][k] for k in range(2))
                for i in range(3)
            )
            effort = sum(sum(row) for row in action)
            cost = effort * problem.resource_cost_per_unit
            team = advance_team(team, action, learning, enabled=individual_learning)
            functional_reward = float(functional.success)
            if organizational_learning:
                org = organization.observe(
                    org, problem.problem_id, action, functional_reward, enabled=True
                )
            cumulative_successes += int(functional.success)
            cumulative_cost += cost
            total_true_reward += mu_true
            step = EpisodeRecord(
                episode=problem_episode * decision_horizon + decision_index,
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
                success=functional.success,
                deficits=functional.deficits,
                normalized_deficit=functional.normalized_deficit,
                margin=functional.margin,
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
                organization_updated=org.update_count > org_version_before,
                organization_action_changed=(
                    previous_action is not None and previous_action != action
                ),
                organization_reward=functional_reward,
                cumulative_successes=cumulative_successes,
                cumulative_resource_cost=cumulative_cost,
            )
            records.append(BeliefEpisodeRecord(
                problem_episode=problem_episode,
                decision_in_problem=decision_index,
                true_environment_type=(
                    "theta1" if item.theta == THETA_1 else "theta2"
                ),
                belief_before=belief,
                belief_after=next_belief,
                observation=observation,
                observation_noise=innovation,
                true_expected_reward=mu_true,
                episode=step,
            ))
            belief = next_belief
            previous_action = action

    return BeliefRunResult(
        policy=getattr(organization, "name", type(organization).__name__),
        seed=seed,
        decision_horizon=decision_horizon,
        records=tuple(records),
        final_team=team,
        final_organization=org,
        cumulative_true_expected_reward=total_true_reward,
    )


def compare_belief_policies(
    initial_team: TeamState,
    problems: tuple[UncertainProblem, ...],
    organizations: Sequence[object],
    *,
    learning: LearningProfile,
    decision_horizon: int,
    prior: float = DEFAULT_PRIOR,
    sigma: float = DEFAULT_SIGMA,
    noise_seed: int,
    seed: int = 0,
) -> tuple[BeliefRunResult, ...]:
    """Pair policies on identical latent problems and Gaussian innovations."""
    return tuple(
        run_belief_sequence(
            initial_team, problems, organization, learning=learning,
            decision_horizon=decision_horizon, prior=prior, sigma=sigma,
            noise_seed=noise_seed, seed=seed,
        )
        for organization in organizations
    )
