"""Minimal HLS Laboratory v1: one functional decision per problem episode.

This is a new assembly layer, not a replacement for Small Problem World,
G0/C1, G3, or the historical finite-belief simulator.  Production and the
legal joint-action catalogue come from DISCOVER-v0; individual capability
change uses the frozen MIS-v2 law.  The v1 contract intentionally has a single
decision per problem and uses perfect capability estimates.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from math import isfinite
from typing import Mapping, Protocol

from .discover_develop_v2 import mis_v2_transition
from .discover_v0 import JOINT_ACTIONS, JointAction, State, production_inputs, validate_action, validate_state

TOL = 1e-12
ActionKey = tuple[tuple[float, float], ...]
ValueKey = tuple[str, ActionKey]


def _action_key(action: JointAction) -> ActionKey:
    return tuple((float(x), float(y)) for x, y in action)


def _action_id(action: JointAction) -> int:
    return JOINT_ACTIONS.index(action)


@dataclass(frozen=True)
class ProblemSpec:
    """One one-decision problem; requirements are team/policy independent.

    ``difficulty`` is the operational label rho=sum(r), not another physical
    mechanism.  An optional action restriction must be a subset of the frozen
    JOINT_ACTIONS catalog and applies identically to every organization.
    """

    problem_id: str
    requirements: tuple[float, float]
    resource_budget: float
    max_effort_per_expert: float = 1.0
    horizon: int = 1
    allowed_actions: tuple[JointAction, ...] | None = None
    resource_cost_per_unit: float = 0.0

    def __post_init__(self) -> None:
        if not self.problem_id:
            raise ValueError("problem_id must be non-empty")
        if len(self.requirements) != 2 or any(not isfinite(x) or x < 0 for x in self.requirements):
            raise ValueError("requirements must be two finite non-negative values")
        if not any(x > 0 for x in self.requirements):
            raise ValueError("at least one requirement must be positive")
        if not isfinite(self.resource_budget) or self.resource_budget < 0:
            raise ValueError("resource_budget must be finite and non-negative")
        if not isfinite(self.max_effort_per_expert) or self.max_effort_per_expert < 0:
            raise ValueError("max_effort_per_expert must be finite and non-negative")
        if self.horizon != 1:
            raise ValueError("HLS Laboratory v1 requires exactly one decision per problem")
        if not isfinite(self.resource_cost_per_unit) or self.resource_cost_per_unit < 0:
            raise ValueError("resource_cost_per_unit must be finite and non-negative")
        if self.allowed_actions is not None:
            if not self.allowed_actions or len(set(self.allowed_actions)) != len(self.allowed_actions):
                raise ValueError("allowed_actions must be a non-empty unique sequence")
            for action in self.allowed_actions:
                validate_action(action)

    @property
    def difficulty(self) -> float:
        return float(sum(self.requirements))

    @property
    def orientation(self) -> tuple[float, float]:
        rho = self.difficulty
        return tuple(x / rho for x in self.requirements)  # type: ignore[return-value]


@dataclass(frozen=True)
class ExpertState:
    expert_id: str
    competence_real: tuple[float, float]
    competence_estimated: tuple[float, float] | None = None
    experience: tuple[float, float] = (0.0, 0.0)
    performance: tuple[float, float] = (0.0, 0.0)

    def __post_init__(self) -> None:
        for name, vector in (("competence_real", self.competence_real),
                             ("experience", self.experience), ("performance", self.performance)):
            if len(vector) != 2 or any(not isfinite(x) or (x < 0 if name != "competence_real" else not 0 <= x <= 1)
                                       for x in vector):
                raise ValueError(f"invalid {name}")
        estimate = self.competence_real if self.competence_estimated is None else self.competence_estimated
        if len(estimate) != 2 or any(not isfinite(x) or not 0 <= x <= 1 for x in estimate):
            raise ValueError("competence_estimated must be a two-vector in [0,1]")
        object.__setattr__(self, "competence_estimated", tuple(estimate))


@dataclass(frozen=True)
class TeamState:
    experts: tuple[ExpertState, ...]

    def __post_init__(self) -> None:
        if len(self.experts) != 3:
            raise ValueError("the reused production operator requires exactly three experts")
        if len({x.expert_id for x in self.experts}) != 3:
            raise ValueError("expert identities must be unique")
        validate_state(self.real_matrix)

    @property
    def real_matrix(self) -> State:
        return tuple(x.competence_real for x in self.experts)  # type: ignore[return-value]

    @property
    def estimated_matrix(self) -> State:
        return tuple(x.competence_estimated for x in self.experts)  # type: ignore[return-value]


def make_team(state: State, expert_ids: tuple[str, str, str] = ("E0", "E1", "E2")) -> TeamState:
    """Create a team under the v1 perfect-knowledge control ŝ=s."""
    validate_state(state)
    return TeamState(tuple(ExpertState(name, row, row) for name, row in zip(expert_ids, state)))


@dataclass(frozen=True)
class FunctionalResult:
    success: bool
    deficits: tuple[float, float]
    normalized_deficit: float
    margin: float


def evaluate_problem(outputs: tuple[float, float], requirements: tuple[float, float]) -> FunctionalResult:
    """Apply the CE-23 threshold, deficit, and margin definitions.

    Zero requirements are omitted from normalized deficit and margin.  This
    deliberately extends (without changing) functional_problem's historical
    strictly-positive-requirement observer.
    """
    if len(outputs) != 2 or len(requirements) != 2:
        raise ValueError("outputs and requirements must be two-vectors")
    if any(not isfinite(y) or y < 0 for y in outputs):
        raise ValueError("outputs must be finite and non-negative")
    if any(not isfinite(r) or r < 0 for r in requirements) or not any(requirements):
        raise ValueError("requirements must be finite, non-negative, and not both zero")
    deficits = tuple(max(0.0, r - y) for y, r in zip(outputs, requirements))
    active = [i for i, r in enumerate(requirements) if r > 0]
    normalized = sum(deficits[i] / requirements[i] for i in active)
    margin = min(outputs[i] - requirements[i] for i in active)
    success = all(outputs[i] + TOL >= requirements[i] for i in active)
    return FunctionalResult(success, deficits, normalized, margin)  # type: ignore[arg-type]


def feasible_actions(problem: ProblemSpec) -> tuple[JointAction, ...]:
    """Filter the frozen action catalog by the episode's declared budgets."""
    catalog = JOINT_ACTIONS if problem.allowed_actions is None else problem.allowed_actions
    result = tuple(action for action in catalog
                   if sum(sum(row) for row in action) <= problem.resource_budget + TOL
                   and all(sum(row) <= problem.max_effort_per_expert + TOL for row in action))
    if not result:
        raise ValueError(f"problem {problem.problem_id} has no feasible frozen joint action")
    return result


def complementarity_class(team: TeamState, problem: ProblemSpec) -> str:
    """Classify functional feasibility at the same total budget.

    ``team_only`` is a constrained operational label, not superadditive
    synergy. A single-expert alternative may use the full problem budget but
    remains subject to the same frozen per-expert action cap.
    """
    actions = feasible_actions(problem)
    team_feasible = any(evaluate_problem(production_inputs(team.real_matrix, action),
                                         problem.requirements).success for action in actions)
    single_feasible = False
    for expert in range(3):
        for action in actions:
            if all(sum(row) <= TOL for i, row in enumerate(action) if i != expert):
                if evaluate_problem(production_inputs(team.real_matrix, action), problem.requirements).success:
                    single_feasible = True
                    break
        if single_feasible:
            break
    if single_feasible:
        return "single_sufficient"
    if team_feasible:
        return "team_only"
    return "none_feasible"


@dataclass(frozen=True)
class DecisionView:
    """Information exposed to any organization before its current decision."""

    problem_id: str
    requirements: tuple[float, float]
    difficulty: float
    orientation: tuple[float, float]
    resource_budget: float
    estimated_competencies: State
    feasible_actions: tuple[JointAction, ...]


@dataclass(frozen=True)
class OrganizationState:
    """Persistent tabular state θ; entries store sample-average success values."""

    values: tuple[tuple[ValueKey, int, float], ...] = ()
    update_count: int = 0

    def lookup(self) -> dict[ValueKey, tuple[int, float]]:
        return {key: (count, value) for key, count, value in self.values}


class Organization(Protocol):
    name: str

    def choose(self, view: DecisionView, state: OrganizationState) -> JointAction: ...


@dataclass(frozen=True)
class FixedRouting:
    """Frozen problem-type→joint-allocation table; never changes within type."""

    routing: Mapping[str, JointAction]
    name: str = "fixed"

    def choose(self, view: DecisionView, state: OrganizationState) -> JointAction:
        action = self.routing.get(view.problem_id)
        if action is None or action not in view.feasible_actions:
            raise ValueError(f"fixed routing has no feasible action for {view.problem_id}")
        return action


@dataclass(frozen=True)
class GreedyAdaptive:
    """Predeclared state-responsive rule; uses ŝ, but has immutable θ."""

    name: str = "adaptive_greedy"

    def choose(self, view: DecisionView, state: OrganizationState) -> JointAction:
        ranked = []
        for action in view.feasible_actions:
            outputs = production_inputs(view.estimated_competencies, action)
            result = evaluate_problem(outputs, view.requirements)
            effort = sum(sum(row) for row in action)
            ranked.append(((int(result.success), -result.normalized_deficit, result.margin, -effort), action))
        best = max(score for score, _ in ranked)
        return next(action for score, action in ranked if score == best)


@dataclass(frozen=True)
class ExploreThenGreedy:
    """Standard tabular bandit: try each legal arm once, then greedy sample mean."""

    name: str = "learned_tabular"

    def choose(self, view: DecisionView, state: OrganizationState) -> JointAction:
        values = state.lookup()
        context = view.problem_id
        for action in view.feasible_actions:
            if values.get((context, _action_key(action)), (0, 0.0))[0] == 0:
                return action
        estimates = [(values[(context, _action_key(action))][1], action)
                     for action in view.feasible_actions]
        best = max(value for value, _ in estimates)
        return next(action for value, action in estimates if value == best)

    def observe(self, state: OrganizationState, problem_id: str, action: JointAction,
                reward: float, *, enabled: bool) -> OrganizationState:
        if not enabled:
            return state
        if not isfinite(reward) or not 0 <= reward <= 1:
            raise ValueError("organizational reward must be success in [0,1]")
        values = state.lookup()
        key = (problem_id, _action_key(action))
        count, mean = values.get(key, (0, 0.0))
        count += 1
        values[key] = (count, mean + (reward - mean) / count)
        return OrganizationState(tuple(sorted((k, n, q) for k, (n, q) in values.items())),
                                 state.update_count + 1)


@dataclass(frozen=True)
class EpisodeRecord:
    episode: int
    seed: int
    problem_id: str
    requirements: tuple[float, float]
    difficulty: float
    orientation: tuple[float, float]
    budget: float
    competence_before: State
    estimated_before: State
    experience_before: tuple[tuple[float, float], ...]
    action: JointAction
    action_id: int
    individual_outputs: tuple[tuple[float, float], ...]
    outputs: tuple[float, float]
    success: bool
    deficits: tuple[float, float]
    normalized_deficit: float
    margin: float
    effort: float
    resource_cost: float
    individual_performance_cumulative: tuple[tuple[float, float], ...]
    competence_after: State
    estimated_after: State
    experience_after: tuple[tuple[float, float], ...]
    organization_theta_before: tuple[tuple[ValueKey, int, float], ...]
    organization_theta_after: tuple[tuple[ValueKey, int, float], ...]
    organization_updated: bool
    organization_action_changed: bool
    organization_reward: float
    cumulative_successes: int
    cumulative_resource_cost: float


@dataclass(frozen=True)
class RunResult:
    policy: str
    seed: int
    individual_learning: bool
    organizational_learning: bool
    records: tuple[EpisodeRecord, ...]
    final_team: TeamState
    final_organization: OrganizationState


def episode_record_to_dict(record: EpisodeRecord) -> dict[str, object]:
    """Return a JSON-safe, stable representation of one v1 episode.

    Organizational parameter keys contain tuples internally.  They are
    represented as rows with a problem context and frozen action-catalog ID
    so serialization is portable and does not depend on Python tuple-key
    handling.
    """
    theta_before = [
        {"problem_context": key[0], "action_id": JOINT_ACTIONS.index(key[1]),
         "count": count, "mean_success": mean}
        for key, count, mean in record.organization_theta_before
    ]
    theta_after = [
        {"problem_context": key[0], "action_id": JOINT_ACTIONS.index(key[1]),
         "count": count, "mean_success": mean}
        for key, count, mean in record.organization_theta_after
    ]
    result = {name: getattr(record, name) for name in EpisodeRecord.__dataclass_fields__}
    result["organization_theta_before"] = theta_before
    result["organization_theta_after"] = theta_after
    return result


def serialize_episode_records(records: tuple[EpisodeRecord, ...]) -> str:
    """Serialize episode traces deterministically for P9 provenance."""
    return json.dumps([episode_record_to_dict(row) for row in records],
                      sort_keys=True, separators=(",", ":"), allow_nan=False)


def _view(problem: ProblemSpec, team: TeamState) -> DecisionView:
    return DecisionView(problem.problem_id, problem.requirements, problem.difficulty,
                        problem.orientation, problem.resource_budget, team.estimated_matrix,
                        feasible_actions(problem))


def run_sequence(
    initial_team: TeamState,
    problems: tuple[ProblemSpec, ...],
    organization: Organization,
    *,
    eta: float,
    individual_learning: bool = True,
    organizational_learning: bool = False,
    seed: int = 0,
) -> RunResult:
    """Execute one decision per problem, independently controlling LI and LO."""
    if not problems:
        raise ValueError("problem sequence must be non-empty")
    if not isfinite(eta) or not 0 < eta < 1:
        raise ValueError("eta must lie strictly inside (0,1)")
    if organizational_learning and not isinstance(organization, ExploreThenGreedy):
        raise ValueError("organizational learning is implemented only for ExploreThenGreedy")
    team, org = initial_team, OrganizationState()
    previous_action = None
    records = []
    cumulative_successes = 0
    cumulative_cost = 0.0
    for episode, problem in enumerate(problems):
        view = _view(problem, team)
        theta_before = org.values
        org_version_before = org.update_count
        experience_before = tuple(x.experience for x in team.experts)
        action = organization.choose(view, org)
        if action not in view.feasible_actions:
            raise AssertionError("organization selected an infeasible action")
        action_id = _action_id(action)
        s_before, shat_before = team.real_matrix, team.estimated_matrix
        individual_outputs = tuple(tuple(action[i][k] * s_before[i][k] for k in range(2)) for i in range(3))
        outputs = production_inputs(s_before, action)
        result = evaluate_problem(outputs, problem.requirements)
        effort = sum(sum(row) for row in action)
        cost = effort * problem.resource_cost_per_unit
        updated_experience = tuple(tuple(team.experts[i].experience[k] + action[i][k]
                                         for k in range(2)) for i in range(3))
        updated_performance = tuple(tuple(team.experts[i].performance[k] + individual_outputs[i][k]
                                          for k in range(2)) for i in range(3))
        new_real = mis_v2_transition(s_before, action, enabled=individual_learning, eta=eta)
        # v1 uses the declared perfect-knowledge control, including after MIS.
        team = TeamState(tuple(ExpertState(team.experts[i].expert_id, new_real[i], new_real[i],
                                             updated_experience[i], updated_performance[i]) for i in range(3)))
        reward = float(result.success)
        if isinstance(organization, ExploreThenGreedy):
            org = organization.observe(org, problem.problem_id, action, reward,
                                       enabled=organizational_learning)
        changed = previous_action is not None and previous_action != action
        cumulative_successes += int(result.success)
        cumulative_cost += cost
        records.append(EpisodeRecord(
            episode, seed, problem.problem_id, problem.requirements, problem.difficulty,
            problem.orientation, problem.resource_budget, s_before, shat_before,
            experience_before,
            action, action_id, individual_outputs, outputs, result.success, result.deficits,
            result.normalized_deficit, result.margin, effort, cost,
            tuple(x.performance for x in team.experts), team.real_matrix, team.estimated_matrix,
            tuple(x.experience for x in team.experts), theta_before, org.values,
            org.update_count > org_version_before,
            changed, reward, cumulative_successes, cumulative_cost,
        ))
        previous_action = action
    return RunResult(organization.name, seed, individual_learning, organizational_learning,
                     tuple(records), team, org)
