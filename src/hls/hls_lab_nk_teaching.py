"""N×K adapter for the existing directed teaching transition.

The legacy equation is preserved exactly. Teaching efficacy is indexed by
teacher, learner and competence; current teacher competence is not a direct
term in the historical transition.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .hls_lab_nk_geometry import (
    CompetenceMatrixNK,
    ProductiveAllocationNK,
)


def _ids(values: tuple[str, ...], name: str) -> tuple[str, ...]:
    normalized = tuple(values)
    if (not normalized or any(not isinstance(value, str) or not value.strip()
                              for value in normalized)
            or len(set(normalized)) != len(normalized)):
        raise ValueError(f"{name} must contain unique non-empty identifiers")
    return normalized


@dataclass(frozen=True)
class TeachingActionNK:
    """One directed lesson; identifiers resolve against the configured team."""

    teacher_id: str
    learner_id: str
    skill_id: str
    effort: float

    def __post_init__(self) -> None:
        if any(not isinstance(value, str) or not value.strip()
               for value in (self.teacher_id, self.learner_id, self.skill_id)):
            raise ValueError("teacher_id, learner_id and skill_id must be non-empty strings")
        if self.teacher_id == self.learner_id:
            raise ValueError("teaching requires distinct teacher and learner")
        try:
            effort = float(self.effort)
        except (TypeError, ValueError) as exc:
            raise ValueError("teaching effort must be numeric") from exc
        if not isfinite(effort) or effort <= 0.0:
            raise ValueError("teaching effort must be finite and positive")
        object.__setattr__(self, "effort", effort)


@dataclass(frozen=True)
class JointActionNK:
    """Complete externally selected period action; no teacher policy is implied."""

    production: ProductiveAllocationNK
    teaching: TeachingActionNK | None = None


@dataclass(frozen=True)
class TeachingEfficacyNK:
    """Private efficacy tensor T[teacher, learner, skill] with stable IDs."""

    agent_ids: tuple[str, ...]
    skill_ids: tuple[str, ...]
    values: tuple[tuple[tuple[float, ...], ...], ...]

    def __post_init__(self) -> None:
        agents = _ids(self.agent_ids, "agent_ids")
        skills = _ids(self.skill_ids, "skill_ids")
        try:
            values = tuple(tuple(tuple(float(value) for value in skill_row)
                                 for skill_row in learner_rows)
                           for learner_rows in self.values)
        except (TypeError, ValueError) as exc:
            raise ValueError("teaching efficacy must be a numeric N×N×K tensor") from exc
        n, k = len(agents), len(skills)
        if (len(values) != n or any(len(row) != n for row in values)
                or any(len(skill_row) != k for row in values for skill_row in row)):
            raise ValueError(f"teaching efficacy must have shape {n}×{n}×{k}")
        if any(not isfinite(value) or not 0.0 <= value <= 1.0
               for row in values for skill_row in row for value in skill_row):
            raise ValueError("teaching efficacy values must lie in [0, 1]")
        if any(value != 0.0 for i in range(n) for value in values[i][i]):
            raise ValueError("self-teaching efficacy must be zero")
        object.__setattr__(self, "agent_ids", agents)
        object.__setattr__(self, "skill_ids", skills)
        object.__setattr__(self, "values", values)

    @property
    def n_agents(self) -> int:
        return len(self.agent_ids)

    @property
    def n_skills(self) -> int:
        return len(self.skill_ids)

    def validate_identifiers(self, agent_ids: tuple[str, ...], skill_ids: tuple[str, ...]) -> None:
        if tuple(agent_ids) != self.agent_ids or tuple(skill_ids) != self.skill_ids:
            raise ValueError("teaching efficacy identifiers/order must match the organization")

    def resolve(self, action: TeachingActionNK) -> tuple[int, int, int, float]:
        try:
            teacher = self.agent_ids.index(action.teacher_id)
            learner = self.agent_ids.index(action.learner_id)
            skill = self.skill_ids.index(action.skill_id)
        except ValueError as exc:
            raise ValueError("teaching action contains an unknown agent or skill identifier") from exc
        return teacher, learner, skill, self.values[teacher][learner][skill]


@dataclass(frozen=True)
class TeachingParametersNK:
    """The legacy scalar teaching transfer-rate parameter."""

    transfer_rate: float = 0.4

    def __post_init__(self) -> None:
        try:
            rate = float(self.transfer_rate)
        except (TypeError, ValueError) as exc:
            raise ValueError("transfer_rate must be numeric") from exc
        if not isfinite(rate) or not 0.0 < rate <= 1.0:
            raise ValueError("transfer_rate must lie in (0, 1]")
        object.__setattr__(self, "transfer_rate", rate)


@dataclass(frozen=True)
class TeachingTransitionResultNK:
    competence_after: CompetenceMatrixNK
    competence_increment: CompetenceMatrixNK
    teacher_index: int
    learner_index: int
    skill_index: int
    efficacy: float
    competence_gain: float


def teaching_transition_nk(
    competence: CompetenceMatrixNK,
    action: TeachingActionNK,
    efficacy: TeachingEfficacyNK,
    parameters: TeachingParametersNK = TeachingParametersNK(),
) -> TeachingTransitionResultNK:
    """Apply legacy `c' = min(1, c + r e T[i,j,k] (1-c))` to one learner cell.

    Teacher competence is intentionally absent: the historical mechanism
    represents teacher-specific effectiveness in `T[i,j,k]`, not as a second
    multiplier. No other cell changes; efficacy zero consumes the same action
    effort but yields zero direct competence increment.
    """
    try:
        state = tuple(tuple(float(value) for value in row) for row in competence)
    except (TypeError, ValueError) as exc:
        raise ValueError("competence must be a numeric N×K matrix") from exc
    if not state or not state[0] or any(len(row) != len(state[0]) for row in state):
        raise ValueError("competence must be a non-empty rectangular N×K matrix")
    n, k = len(state), len(state[0])
    if (efficacy.n_agents, efficacy.n_skills) != (n, k):
        raise ValueError(f"teaching efficacy shape must match competence {n}×{k}")
    if any(not isfinite(value) or not 0.0 <= value <= 1.0
           for row in state for value in row):
        raise ValueError("competence values must be finite and lie in [0, 1]")
    teacher, learner, skill, relation_efficacy = efficacy.resolve(action)
    old = state[learner][skill]
    gain = (parameters.transfer_rate * action.effort * relation_efficacy * (1.0 - old))
    updated = min(1.0, old + gain)
    after = [list(row) for row in state]
    after[learner][skill] = updated
    increments = [[0.0 for _ in range(k)] for _ in range(n)]
    increments[learner][skill] = updated - old
    return TeachingTransitionResultNK(
        competence_after=tuple(tuple(row) for row in after),
        competence_increment=tuple(tuple(row) for row in increments),
        teacher_index=teacher,
        learner_index=learner,
        skill_index=skill,
        efficacy=relation_efficacy,
        competence_gain=updated - old,
    )


def validate_joint_action_resources_nk(
    production: ProductiveAllocationNK,
    teaching: TeachingActionNK | None,
    *,
    agent_ids: tuple[str, ...],
    collective_budget: float,
    individual_limits: tuple[float, ...],
    efficacy: TeachingEfficacyNK | None = None,
) -> tuple[tuple[float, ...], float, float]:
    """Validate combined legacy resource charges and return (loads, used, unused).

    Each teaching participant pays one event effort. Thus the collective charge
    is 2e, and the teacher and learner each receive an individual load e.
    """
    n = len(agent_ids)
    if (n < 1 or len(set(agent_ids)) != n or len(production) != n
            or len(individual_limits) != n):
        raise ValueError("production, identifiers and effort limits must agree on N")
    try:
        rows = tuple(tuple(float(value) for value in row) for row in production)
        limits = tuple(float(value) for value in individual_limits)
        budget = float(collective_budget)
    except (TypeError, ValueError) as exc:
        raise ValueError("action resources must be numeric") from exc
    if (not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows)
            or not isfinite(budget) or budget < 0 or
            any(not isfinite(limit) or limit < 0 for limit in limits) or
            any(not isfinite(value) or value < 0 for row in rows for value in row)):
        raise ValueError("action resources must be finite and non-negative")
    loads = [sum(row) for row in rows]
    prod_used = sum(loads)
    teaching_used = 0.0
    if teaching is not None:
        if efficacy is None:
            raise ValueError("teaching efficacy is required for a teaching action")
        if tuple(agent_ids) != efficacy.agent_ids:
            raise ValueError("teaching efficacy agent order must match organization")
        teacher, learner, _, _ = efficacy.resolve(teaching)
        teaching_used = 2.0 * teaching.effort
        loads[teacher] += teaching.effort
        loads[learner] += teaching.effort
    total = prod_used + teaching_used
    if total > budget + 1e-12:
        raise ValueError("joint action exceeds collective resource budget")
    if any(load > limits[i] + 1e-12 for i, load in enumerate(loads)):
        raise ValueError("joint action exceeds an individual effort limit")
    return tuple(loads), total, max(0.0, budget - total)
