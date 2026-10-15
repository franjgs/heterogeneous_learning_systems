"""Integrated, bounded teaching extension for HLS Laboratory v1.

This additive execution layer composes the frozen v1 production contract,
DISCOVER action catalogue, MIS-v2 individual learning, and the existing
dynamic skill-posterior/demand utilities. It does not modify their semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
from hashlib import sha256
from math import isfinite
from random import Random
from typing import Protocol, Sequence

from .discover_v0 import JointAction, State, ces_reward, production_inputs
from .hls_lab_dynamic import (
    LearningProfile,
    CompetenceEstimatorState,
    SkillPosterior,
    advance_team,
    competence_estimate_matrix,
    competence_variance_matrix,
    indexed_normal_innovation,
    initialize_competence_estimator,
    predict_skill_posterior_after_mis,
    update_skill_posterior,
)
from .hls_lab_v1 import (
    FunctionalResult,
    ProblemSpec,
    TeamState,
    _action_id,
    evaluate_problem,
    feasible_actions,
)

TOL = 1e-12
Relation = tuple[int, int, int]  # instructor, learner, capability


@dataclass(frozen=True)
class TeachingEvent:
    instructor: int
    learner: int
    capability: int
    effort: float

    def __post_init__(self) -> None:
        if self.instructor not in range(3) or self.learner not in range(3):
            raise ValueError("instructor and learner must index the three-person team")
        if self.instructor == self.learner:
            raise ValueError("teaching requires distinct instructor and learner")
        if self.capability not in range(2):
            raise ValueError("capability must be 0 or 1")
        if not isfinite(self.effort) or self.effort <= 0:
            raise ValueError("teaching effort must be finite and positive")

    @property
    def relation(self) -> Relation:
        return self.instructor, self.learner, self.capability


@dataclass(frozen=True)
class IntegratedAction:
    production: JointAction
    teaching: TeachingEvent | None = None


@dataclass(frozen=True)
class IntegratedProblem:
    """An existing v1 functional problem plus explicit CES evaluation weights."""

    problem: ProblemSpec
    ces_weights: tuple[float, float] = (0.5, 0.5)
    demand_label: str = "unspecified"

    def __post_init__(self) -> None:
        if (len(self.ces_weights) != 2 or any(not isfinite(x) or x < 0 for x in self.ces_weights)
                or abs(sum(self.ces_weights) - 1.0) > TOL):
            raise ValueError("CES weights must be non-negative and sum to one")
        if not self.demand_label:
            raise ValueError("demand_label must be non-empty")


@dataclass(frozen=True)
class TeachingEfficacy:
    """Private truth: bounded efficacy indexed by instructor, learner, skill."""

    values: tuple[tuple[tuple[float, float], ...], ...]

    def __post_init__(self) -> None:
        if len(self.values) != 3 or any(len(row) != 3 for row in self.values):
            raise ValueError("teaching efficacy must have shape 3x3x2")
        if any(len(pair) != 2 or any(not isfinite(x) or not 0 <= x <= 1 for x in pair)
               for row in self.values for pair in row):
            raise ValueError("teaching efficacy values must lie in [0, 1]")
        if any(self.values[i][i] != (0.0, 0.0) for i in range(3)):
            raise ValueError("self-teaching efficacy must be zero")

    def get(self, relation: Relation) -> float:
        instructor, learner, capability = relation
        return self.values[instructor][learner][capability]


@dataclass(frozen=True)
class TeachingParameters:
    transfer_rate: float = 0.4
    effort: float = 0.25
    outcome_noise_sd: float = 0.0
    production_observation_noise_sd: float = 0.02
    competence_grid_points: int = 101
    competence_prior_variance: float = 0.04
    efficacy_prior_mean: float = 0.5
    efficacy_threshold: float = 0.35
    target_competence: float = 0.7

    def __post_init__(self) -> None:
        if not isfinite(self.transfer_rate) or not 0 < self.transfer_rate <= 1:
            raise ValueError("transfer_rate must lie in (0, 1]")
        if not isfinite(self.effort) or not 0 < self.effort <= 1:
            raise ValueError("teaching effort must lie in (0, 1]")
        if any(not isfinite(x) or x < 0 for x in
               (self.outcome_noise_sd, self.production_observation_noise_sd)):
            raise ValueError("observation noise must be finite and non-negative")
        if not isinstance(self.competence_grid_points, int) or self.competence_grid_points < 3:
            raise ValueError("competence grid must have at least three points")
        if (not 0 <= self.efficacy_prior_mean <= 1 or not 0 <= self.efficacy_threshold <= 1
                or not 0 <= self.target_competence <= 1):
            raise ValueError("efficacy prior, threshold, and target must lie in [0, 1]")
        if not 0 <= self.competence_prior_variance <= 0.25:
            raise ValueError("competence prior variance must lie in [0, .25]")


@dataclass(frozen=True)
class EfficacyEstimate:
    relation: Relation
    count: int
    mean: float


@dataclass(frozen=True)
class OrganizationMemory:
    """Public organizational memory; stores only noisy formative observations."""

    efficacy: tuple[EfficacyEstimate, ...] = ()

    def estimate(self, relation: Relation, prior: float) -> float:
        row = next((item for item in self.efficacy if item.relation == relation), None)
        return prior if row is None else row.mean

    def count(self, relation: Relation) -> int:
        row = next((item for item in self.efficacy if item.relation == relation), None)
        return 0 if row is None else row.count

    def update(self, relation: Relation, observation: float) -> "OrganizationMemory":
        if not isfinite(observation):
            raise ValueError("formative observation must be finite")
        old = next((item for item in self.efficacy if item.relation == relation), None)
        count = 0 if old is None else old.count
        mean = 0.0 if old is None else old.mean
        count += 1
        # Observation is normalized by the runner to an efficacy-scale signal.
        value = min(1.0, max(0.0, observation))
        updated = EfficacyEstimate(relation, count, mean + (value - mean) / count)
        rows = [item for item in self.efficacy if item.relation != relation]
        rows.append(updated)
        return OrganizationMemory(tuple(sorted(rows, key=lambda x: x.relation)))


@dataclass(frozen=True)
class IntegratedDecisionView:
    """Only observable decision-time data; deliberately excludes private truth."""

    period: int
    periods_remaining: int
    problem_id: str
    demand_label: str
    requirements: tuple[float, float]
    resource_budget: float
    max_effort_per_expert: float
    estimated_competencies: State
    competence_variance: State
    efficacy_estimates: tuple[EfficacyEstimate, ...]
    feasible_actions: tuple[IntegratedAction, ...]

    def efficacy(self, relation: Relation, prior: float) -> float:
        row = next((item for item in self.efficacy_estimates if item.relation == relation), None)
        return prior if row is None else row.mean

    def efficacy_count(self, relation: Relation) -> int:
        row = next((item for item in self.efficacy_estimates if item.relation == relation), None)
        return 0 if row is None else row.count


class IntegratedPolicy(Protocol):
    name: str

    def choose(self, view: IntegratedDecisionView, memory: OrganizationMemory,
               parameters: TeachingParameters) -> IntegratedAction: ...


def _outputs_score(view: IntegratedDecisionView, action: IntegratedAction) -> tuple[float, ...]:
    outputs = production_inputs(view.estimated_competencies, action.production)
    result = evaluate_problem(outputs, view.requirements)
    effort = sum(sum(row) for row in action.production)
    return (int(result.success), -result.normalized_deficit, result.margin, -effort)


def _best_production(actions: Sequence[IntegratedAction], view: IntegratedDecisionView) -> IntegratedAction:
    candidates = tuple(action for action in actions if action.teaching is None)
    if not candidates:
        raise ValueError("no feasible production-only action")
    return max(candidates, key=lambda action: _outputs_score(view, action))


def _best_action(actions: Sequence[IntegratedAction], view: IntegratedDecisionView) -> IntegratedAction:
    if not actions:
        raise ValueError("no feasible action in requested class")
    return max(actions, key=lambda action: _outputs_score(view, action))


@dataclass(frozen=True)
class P0ProductionOnly:
    name: str = "P0_PRODUCTION_ONLY"

    def choose(self, view: IntegratedDecisionView, memory: OrganizationMemory,
               parameters: TeachingParameters) -> IntegratedAction:
        del memory, parameters
        return _best_production(view.feasible_actions, view)


@dataclass(frozen=True)
class P1FixedTeaching:
    relation: Relation
    name: str = "P1_FIXED_TEACHING"

    def choose(self, view: IntegratedDecisionView, memory: OrganizationMemory,
               parameters: TeachingParameters) -> IntegratedAction:
        del memory
        candidates = tuple(action for action in view.feasible_actions
                           if action.teaching is not None
                           and action.teaching.relation == self.relation)
        return (_best_action(candidates, view) if candidates else
                _best_production(view.feasible_actions, view))


@dataclass(frozen=True)
class P2AdaptiveTeaching:
    """Try each configured relation once, then teach only above a fixed threshold."""

    relations: tuple[Relation, ...]
    name: str = "P2_ADAPTIVE_TEACHING"

    def __post_init__(self) -> None:
        if not self.relations or len(set(self.relations)) != len(self.relations):
            raise ValueError("P2 requires a non-empty unique relation list")
        for relation in self.relations:
            TeachingEvent(*relation, effort=0.1)  # validate indices and distinct participants

    def choose(self, view: IntegratedDecisionView, memory: OrganizationMemory,
               parameters: TeachingParameters) -> IntegratedAction:
        del memory
        # Do not spend teaching resources when the best production-only
        # action already meets the current functional requirement.
        if _outputs_score(view, _best_production(view.feasible_actions, view))[0] == 1:
            return _best_production(view.feasible_actions, view)
        eligible = tuple(relation for relation in self.relations
                         if view.requirements[relation[2]] > 0
                         and view.estimated_competencies[relation[1]][relation[2]]
                         < parameters.target_competence)
        unseen = [relation for relation in eligible if view.efficacy_count(relation) == 0]
        if unseen:
            selected = unseen[0]  # prespecified deterministic exploration order
        elif eligible:
            selected = max(eligible,
                           key=lambda relation: (view.efficacy(relation, parameters.efficacy_prior_mean),
                                                 tuple(-x for x in relation)))
            if view.efficacy(selected, parameters.efficacy_prior_mean) < parameters.efficacy_threshold:
                selected = None
        else:
            selected = None
        if selected is None:
            return _best_production(view.feasible_actions, view)
        candidates = tuple(action for action in view.feasible_actions
                           if action.teaching is not None and action.teaching.relation == selected)
        return (_best_action(candidates, view) if candidates else
                _best_production(view.feasible_actions, view))


def enumerate_feasible_integrated_actions(
    problem: ProblemSpec, *, teaching_effort: float
) -> tuple[IntegratedAction, ...]:
    """Compose frozen production allocations with at most one feasible lesson.

    Resource accounting is direct: production effort plus one teaching-effort
    charge for each participant must fit the shared budget and each person's
    existing effort cap. No separate arbitrary teaching penalty is added.
    """
    if not isfinite(teaching_effort) or teaching_effort <= 0:
        raise ValueError("teaching_effort must be finite and positive")
    output: list[IntegratedAction] = []
    for production in feasible_actions(problem):
        production_total = sum(sum(row) for row in production)
        if production_total <= problem.resource_budget + TOL:
            output.append(IntegratedAction(production))
        for teacher in range(3):
            for learner in range(3):
                if teacher == learner:
                    continue
                for skill in range(2):
                    event = TeachingEvent(teacher, learner, skill, teaching_effort)
                    total = production_total + 2.0 * teaching_effort
                    loads = [sum(production[i]) for i in range(3)]
                    loads[teacher] += teaching_effort
                    loads[learner] += teaching_effort
                    if (total <= problem.resource_budget + TOL
                            and all(load <= problem.max_effort_per_expert + TOL for load in loads)):
                        output.append(IntegratedAction(production, event))
    if not output:
        raise ValueError("problem has no feasible integrated actions")
    return tuple(output)


def _training_noise(seed: int, period: int, instructor: int, learner: int, skill: int) -> float:
    payload = f"hls-lab-v1-training-observation-v1|{seed}|{period}|{instructor}|{learner}|{skill}"
    keyed_seed = int.from_bytes(sha256(payload.encode("ascii")).digest()[:8], "big")
    return Random(keyed_seed).gauss(0.0, 1.0)


def _push_posterior(posterior: SkillPosterior, efficacy: float, transfer_rate: float,
                    teaching_effort: float) -> SkillPosterior:
    support = tuple(value + transfer_rate * teaching_effort * efficacy * (1.0 - value)
                    for value in posterior.support)
    return SkillPosterior(support, posterior.weights)


@dataclass(frozen=True)
class IntegratedEpisodeRecord:
    period: int
    problem_id: str
    demand_label: str
    requirements: tuple[float, float]
    competence_real_before: State
    competence_estimated_before: State
    competence_variance_before: State
    action: IntegratedAction
    production_action_id: int
    individual_outputs: State
    outputs: tuple[float, float]
    ces_reward: float
    functional_result: FunctionalResult
    production_effort: float
    teaching_effort: float
    total_resource_used: float
    resource_cost: float
    individual_observations: State
    teaching_gain_real: float | None  # privileged diagnostic; never passed to policy
    teaching_observation: float | None
    efficacy_estimates_before: tuple[EfficacyEstimate, ...]
    efficacy_estimates_after: tuple[EfficacyEstimate, ...]
    organization_updated: bool
    competence_real_after: State
    competence_estimated_after: State
    competence_variance_after: State
    cumulative_ces_reward: float
    cumulative_successes: int
    cumulative_normalized_deficit: float


@dataclass(frozen=True)
class IntegratedRunResult:
    policy: str
    seed: int
    records: tuple[IntegratedEpisodeRecord, ...]
    final_team: TeamState
    final_organization: OrganizationMemory
    snapshots: tuple["OrganizationSnapshot", ...] = ()


@dataclass(frozen=True)
class OrganizationSnapshot:
    """Complete decision-relevant organization state at a period boundary.

    The posterior is part of the organization's information state; it is not
    reconstructed from private competence truth when resuming a run.
    """

    team: TeamState
    competence_posterior: CompetenceEstimatorState
    organization_memory: OrganizationMemory
    next_period: int


def _rate(profile: LearningProfile, expert: int, skill: int) -> float:
    return profile.eta[expert][skill]


def run_integrated_sequence(
    initial_team: TeamState,
    problems: tuple[IntegratedProblem, ...],
    policy: IntegratedPolicy,
    *,
    learning: LearningProfile,
    teaching_efficacy: TeachingEfficacy,
    parameters: TeachingParameters = TeachingParameters(),
    individual_learning: bool = True,
    organizational_learning: bool = True,
    seed: int = 0,
    organization_memory: OrganizationMemory | None = None,
    initial_snapshot: OrganizationSnapshot | None = None,
    period_offset: int = 0,
    first_action_override: IntegratedAction | None = None,
) -> IntegratedRunResult:
    """Run one organization; all external sequences/noise are index-coupled.

    Transition order per period is production, MIS-v2 from productive effort,
    then the optional directed teaching transition. The organization sees
    noisy individual production and formative-response observations only.
    """
    if not problems:
        raise ValueError("problem sequence must be non-empty")
    if not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if period_offset < 0:
        raise ValueError("period_offset must be non-negative")
    if initial_snapshot is not None and (organization_memory is not None or period_offset):
        raise ValueError("snapshot cannot be combined with separate memory or period_offset")
    team = initial_team
    memory = organization_memory or OrganizationMemory()
    if initial_snapshot is None:
        prior_variance: State = tuple(tuple(
            min(parameters.competence_prior_variance, value * (1.0 - value))
            for value in row) for row in team.estimated_matrix)  # type: ignore[assignment]
        posterior = initialize_competence_estimator(
            team.estimated_matrix, prior_variance,
            estimator="grid", grid_points=parameters.competence_grid_points,
        )
    else:
        team = deepcopy(initial_snapshot.team)
        memory = deepcopy(initial_snapshot.organization_memory)
        posterior = deepcopy(initial_snapshot.competence_posterior)
        period_offset = initial_snapshot.next_period
    snapshots = [OrganizationSnapshot(deepcopy(team), deepcopy(posterior),
                                      deepcopy(memory), period_offset)]
    rows: list[IntegratedEpisodeRecord] = []
    cumulative_reward = cumulative_deficit = 0.0
    cumulative_successes = 0

    for local_period, item in enumerate(problems):
        period = period_offset + local_period
        problem = item.problem
        feasible = enumerate_feasible_integrated_actions(problem, teaching_effort=parameters.effort)
        view = IntegratedDecisionView(
            period=period,
            periods_remaining=len(problems) - period,
            problem_id=problem.problem_id,
            demand_label=item.demand_label,
            requirements=problem.requirements,
            resource_budget=problem.resource_budget,
            max_effort_per_expert=problem.max_effort_per_expert,
            estimated_competencies=competence_estimate_matrix(posterior),
            competence_variance=competence_variance_matrix(posterior),
            efficacy_estimates=memory.efficacy,
            feasible_actions=feasible,
        )
        action = (first_action_override if local_period == 0 and first_action_override is not None
                  else policy.choose(view, memory, parameters))
        if action not in feasible:
            raise ValueError("policy returned an infeasible integrated action")

        before = team.real_matrix
        estimate_before = competence_estimate_matrix(posterior)
        variance_before = competence_variance_matrix(posterior)
        memory_before = memory.efficacy
        production = action.production
        outputs = production_inputs(before, production)
        individual_outputs = tuple(tuple(production[i][k] * before[i][k] for k in range(2))
                                   for i in range(3))
        functional = evaluate_problem(outputs, problem.requirements)
        reward = ces_reward(outputs, item.ces_weights)
        production_effort = sum(sum(row) for row in production)
        lesson_effort = 0.0 if action.teaching is None else 2.0 * action.teaching.effort
        total_used = production_effort + lesson_effort
        resource_cost = total_used * problem.resource_cost_per_unit

        observations = tuple(tuple(
            production[i][k] * before[i][k]
            + parameters.production_observation_noise_sd
            * indexed_normal_innovation(seed, period, 0, i, k)
            for k in range(2)) for i in range(3))
        # Private competence evolves through the existing MIS-v2 implementation;
        # its own estimates are deliberately not advanced from private state.
        team = advance_team(team, production, learning, enabled=individual_learning,
                            update_estimated=False)
        posterior_rows: list[tuple[SkillPosterior, SkillPosterior]] = []
        for i in range(3):
            cells = []
            for k in range(2):
                cell = update_skill_posterior(
                    posterior[i][k], production[i][k], observations[i][k],
                    parameters.production_observation_noise_sd,
                )
                if individual_learning:
                    cell = predict_skill_posterior_after_mis(cell, production[i][k], _rate(learning, i, k))
                cells.append(cell)
            posterior_rows.append(tuple(cells))  # type: ignore[arg-type]
        posterior = tuple(posterior_rows)  # type: ignore[assignment]

        training_gain = training_observation = None
        updated = False
        if action.teaching is not None:
            event = action.teaching
            real_skill = team.experts[event.learner].competence_real[event.capability]
            efficacy = teaching_efficacy.get(event.relation)
            training_gain = (parameters.transfer_rate * event.effort * efficacy * (1.0 - real_skill))
            experts = list(team.experts)
            learner = experts[event.learner]
            next_skill = min(1.0, real_skill + training_gain)
            real_skills = list(learner.competence_real)
            real_skills[event.capability] = next_skill
            experts[event.learner] = type(learner)(
                learner.expert_id, tuple(real_skills), learner.competence_estimated,
                learner.experience, learner.performance,
            )
            team = TeamState(tuple(experts))

            innovation = _training_noise(seed, period, event.instructor, event.learner,
                                         event.capability)
            training_observation = training_gain + parameters.outcome_noise_sd * innovation
            estimated_c = competence_estimate_matrix(posterior)[event.learner][event.capability]
            denominator = parameters.transfer_rate * event.effort * (1.0 - estimated_c)
            normalized_signal = (parameters.efficacy_prior_mean if denominator <= TOL
                                else training_observation / denominator)
            # The running-mean efficacy estimator uses only this noisy signal.
            if organizational_learning:
                memory = memory.update(event.relation, normalized_signal)
                updated = True
                efficacy_estimate = memory.estimate(event.relation, parameters.efficacy_prior_mean)
                posterior_rows = [list(row) for row in posterior]
                posterior_rows[event.learner][event.capability] = _push_posterior(
                    posterior_rows[event.learner][event.capability], efficacy_estimate,
                    parameters.transfer_rate, event.effort,
                )
                posterior = tuple(tuple(row) for row in posterior_rows)  # type: ignore[assignment]
            updated_estimate = competence_estimate_matrix(posterior)
            team = TeamState(tuple(
                type(expert)(expert.expert_id, expert.competence_real,
                             updated_estimate[i], expert.experience, expert.performance)
                for i, expert in enumerate(team.experts)
            ))
        else:
            updated_estimate = competence_estimate_matrix(posterior)
            team = TeamState(tuple(
                type(expert)(expert.expert_id, expert.competence_real,
                             updated_estimate[i], expert.experience, expert.performance)
                for i, expert in enumerate(team.experts)
            ))

        cumulative_reward += reward
        cumulative_successes += int(functional.success)
        cumulative_deficit += functional.normalized_deficit
        rows.append(IntegratedEpisodeRecord(
            period=period, problem_id=problem.problem_id, demand_label=item.demand_label,
            requirements=problem.requirements, competence_real_before=before,
            competence_estimated_before=estimate_before, competence_variance_before=variance_before,
            action=action, production_action_id=_action_id(production),
            individual_outputs=individual_outputs, outputs=outputs, ces_reward=reward,
            functional_result=functional, production_effort=production_effort,
            teaching_effort=lesson_effort, total_resource_used=total_used,
            resource_cost=resource_cost, individual_observations=observations,
            teaching_gain_real=training_gain, teaching_observation=training_observation,
            efficacy_estimates_before=memory_before, efficacy_estimates_after=memory.efficacy,
            organization_updated=updated, competence_real_after=team.real_matrix,
            competence_estimated_after=team.estimated_matrix,
            competence_variance_after=competence_variance_matrix(posterior),
            cumulative_ces_reward=cumulative_reward, cumulative_successes=cumulative_successes,
            cumulative_normalized_deficit=cumulative_deficit,
        ))
        snapshots.append(OrganizationSnapshot(deepcopy(team), deepcopy(posterior),
                                              deepcopy(memory), period + 1))

    return IntegratedRunResult(policy.name, seed, tuple(rows), team, memory,
                               tuple(snapshots))


def compare_integrated_policies(
    initial_team: TeamState,
    problems: tuple[IntegratedProblem, ...],
    policies: Sequence[IntegratedPolicy],
    *,
    learning: LearningProfile,
    teaching_efficacy: TeachingEfficacy,
    parameters: TeachingParameters = TeachingParameters(),
    individual_learning: bool = True,
    organizational_learning: bool = True,
    seed: int = 0,
) -> tuple[IntegratedRunResult, ...]:
    """Matched comparison: same start, public problem stream, and indexed shocks."""
    return tuple(run_integrated_sequence(
        initial_team, problems, policy, learning=learning,
        teaching_efficacy=teaching_efficacy, parameters=parameters,
        individual_learning=individual_learning,
        organizational_learning=organizational_learning, seed=seed,
    ) for policy in policies)


def serialize_integrated_result(result: IntegratedRunResult) -> str:
    """Stable JSON trace; private diagnostics are explicitly named in records."""
    import json
    from dataclasses import asdict

    return json.dumps(asdict(result), sort_keys=True, separators=(",", ":"), allow_nan=False)
