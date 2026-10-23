"""Exact finite-horizon reference for S7 Markov demand and S4 skill dynamics.

This scenario-specific reference composes the existing N×K action feasibility,
CES reward, MIS-v2 and optional transfer transitions with a finite Markov
demand process. It is an oracle for a known demand law, not a deployable policy
when that law is unknown.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import isfinite
from typing import Mapping, Sequence

from hls.hls_lab_nk_geometry import ProblemSpecNK
from hls.hls_lab_nk_production import productive_outputs_nk
from hls.hls_lab_nk_teaching import JointActionNK, TeachingEfficacyNK
from hls.synthetic.hls_s4_transfer_exact import (
    Competence,
    ExactTransferCase,
    _step,
    action_catalogs,
    independent_action_catalogs,
)

TOL = 1e-12


@dataclass(frozen=True)
class S7MarkovDemandCase:
    """Finite Markov demand law over existing S4 problem specifications."""

    physical_case: ExactTransferCase
    demand_states: tuple[ProblemSpecNK, ...]
    initial_probabilities: tuple[float, ...]
    transition_probabilities: tuple[tuple[float, ...], ...]
    horizon: int

    def __post_init__(self) -> None:
        states = tuple(self.demand_states)
        initial = tuple(float(p) for p in self.initial_probabilities)
        transitions = tuple(tuple(float(p) for p in row)
                            for row in self.transition_probabilities)
        n_states = len(states)
        if n_states < 1 or len({state.problem_id for state in states}) != n_states:
            raise ValueError("demand states must be non-empty and have unique problem IDs")
        if (not isinstance(self.horizon, int) or isinstance(self.horizon, bool)
                or self.horizon < 1):
            raise ValueError("horizon must be a positive integer")
        if len(initial) != n_states or len(transitions) != n_states:
            raise ValueError("initial and transition distributions must match demand states")
        if any(len(row) != n_states for row in transitions):
            raise ValueError("transition matrix must be square over demand states")
        distributions = (initial, *transitions)
        for distribution in distributions:
            if (any(not isfinite(p) or p < 0.0 for p in distribution)
                    or abs(sum(distribution) - 1.0) > 1e-10):
                raise ValueError("demand probabilities must be finite and sum to one")
        dimensions = {len(state.requirements) for state in states}
        if len(dimensions) != 1:
            raise ValueError("demand states must share the physical competence dimension")
        object.__setattr__(self, "demand_states", states)
        object.__setattr__(self, "initial_probabilities", initial)
        object.__setattr__(self, "transition_probabilities", transitions)


@dataclass(frozen=True)
class S7ExactResult:
    value: float
    visited_states: int
    transfer_available: bool
    actions_by_state: Mapping[tuple[int, Competence, int], JointActionNK]
    dominated_actions_pruned: int = 0
    value_by_state: Mapping[tuple[int, Competence, int], float] | None = None


def positive_competence_gain(before: Competence, after: Competence) -> float:
    """Sum positive immediate competence increments under the physical step."""
    return sum(max(0.0, after[i][k] - before[i][k])
               for i in range(len(before)) for k in range(len(before[i])))


def _action_key(action: JointActionNK) -> tuple:
    teaching = action.teaching
    teach_key = (("", "", "", 0.0) if teaching is None else
                 (teaching.teacher_id, teaching.learner_id,
                  teaching.skill_id, teaching.effort))
    return action.production, teach_key


def select_best_myopic_action(
    competence: Competence,
    evaluated_actions: Sequence[tuple[JointActionNK, float, Competence]],
) -> tuple[JointActionNK, float, int, float]:
    """Maximize immediate CES, then immediate positive competence gain.

    Remaining secondary ties use a canonical action key, independent of the
    catalog order. No future demand law or Bellman value is consulted.
    """
    if not evaluated_actions:
        raise ValueError("at least one feasible action is required")
    maximum = max(reward for _, reward, _ in evaluated_actions)
    tied = [(action, reward, successor)
            for action, reward, successor in evaluated_actions
            if maximum - reward <= TOL]
    gains = [(positive_competence_gain(competence, successor), action)
             for action, _, successor in tied]
    best_gain = max(gain for gain, _ in gains)
    selected = min((action for gain, action in gains if best_gain - gain <= TOL),
                   key=_action_key)
    return selected, maximum, len(tied), positive_competence_gain(
        competence, next(successor for action, _, successor in tied if action == selected))


def select_current_demand_myopic_action(
    competence: Competence,
    demand: ProblemSpecNK,
    evaluated_actions: Sequence[tuple[JointActionNK, float, Competence]],
) -> tuple[JointActionNK, float, int, float]:
    """Maximize immediate CES, then development for currently demanded skills.

    A skill is currently demanded when its requirement in ``demand`` is
    positive. No transition probabilities, future demand, or Bellman values
    are used. Remaining ties use the canonical action key.
    """
    if not evaluated_actions:
        raise ValueError("at least one feasible action is required")
    demanded_skills = tuple(index for index, requirement in enumerate(demand.requirements)
                            if requirement > 0.0)
    maximum = max(reward for _, reward, _ in evaluated_actions)
    tied = [(action, reward, successor)
            for action, reward, successor in evaluated_actions
            if maximum - reward <= TOL]

    def demanded_gain(successor: Competence) -> float:
        return sum(max(0.0, successor[i][k] - competence[i][k])
                   for i in range(len(competence)) for k in demanded_skills)

    gains = [(demanded_gain(successor), action) for action, _, successor in tied]
    best_gain = max(gain for gain, _ in gains)
    selected = min((action for gain, action in gains if best_gain - gain <= TOL),
                   key=_action_key)
    successor = next(state for action, _, state in tied if action == selected)
    return selected, maximum, len(tied), demanded_gain(successor)


def _state_cases(case: S7MarkovDemandCase, *, transfer_available: bool,
                 efficacy: TeachingEfficacyNK | None):
    """Construct complete existing action catalogs for each demand state."""
    base = case.physical_case
    catalogs = []
    for demand in case.demand_states:
        one_state = ExactTransferCase(
            base.organization, (demand,) * case.horizon, base.profile,
            base.efficacy, base.teaching_parameters, base.teaching_effort,
            base.effort_choices,
        )
        catalogs.append((one_state, action_catalogs(
            one_state, transfer_available=transfer_available, efficacy=efficacy,
        )[0]))
    return tuple(catalogs)


def solve_markov_bellman(case: S7MarkovDemandCase, *,
                         transfer_available: bool,
                         efficacy: TeachingEfficacyNK | None = None,
                         prune_dominated: bool = True) -> S7ExactResult:
    """Maximize expected cumulative CES with current demand observed.

    The demand transition law is known to this exact reference. Future demand
    realizations are not observed early; the action is selected conditional on
    the current demand state only.
    """
    state_cases = _state_cases(case, transfer_available=transfer_available,
                               efficacy=efficacy)
    choices: dict[tuple[int, Competence, int], JointActionNK] = {}
    state_values: dict[tuple[int, Competence, int], float] = {}
    pruned_count = 0

    @lru_cache(maxsize=None)
    def value(time: int, competence: Competence, demand_state: int) -> float:
        nonlocal pruned_count
        if time == case.horizon:
            return 0.0
        physical_case, actions = state_cases[demand_state]
        problem = case.demand_states[demand_state]
        best = float("-inf")
        successors = []
        for action in actions:
            reward, next_competence = _step(
                physical_case, competence, problem, action, efficacy=efficacy,
            )
            successors.append((action, reward, next_competence))
        if prune_dominated:
            nondominated = []
            for index, candidate in enumerate(successors):
                _, reward, next_competence = candidate
                dominated = False
                for other_index, (_, other_reward, other_competence) in enumerate(successors):
                    if other_index == index:
                        continue
                    reward_ge = other_reward >= reward - TOL
                    state_ge = all(
                        other_competence[i][k] >= next_competence[i][k] - TOL
                        for i in range(len(next_competence))
                        for k in range(len(next_competence[i]))
                    )
                    strict = (other_reward > reward + TOL or any(
                        other_competence[i][k] > next_competence[i][k] + TOL
                        for i in range(len(next_competence))
                        for k in range(len(next_competence[i]))
                    ))
                    # Preserve the first action when two candidates are exactly
                    # equivalent, keeping deterministic legacy tie order.
                    equivalent_later = (
                        other_index < index
                        and abs(other_reward - reward) <= TOL
                        and all(abs(other_competence[i][k] - next_competence[i][k]) <= TOL
                                for i in range(len(next_competence))
                                for k in range(len(next_competence[i])))
                    )
                    if reward_ge and state_ge and (strict or equivalent_later):
                        dominated = True
                        break
                if not dominated:
                    nondominated.append(candidate)
            pruned_count += len(successors) - len(nondominated)
            successors = nondominated
        for action, reward, next_competence in successors:
            if time + 1 == case.horizon:
                continuation = 0.0
            else:
                continuation = sum(
                    probability * value(time + 1, next_competence, next_state)
                    for next_state, probability in enumerate(
                        case.transition_probabilities[demand_state]
                    )
                )
            candidate = reward + continuation
            if candidate > best + TOL:
                best = candidate
                choices[(time, competence, demand_state)] = action
        state_values[(time, competence, demand_state)] = best
        return best

    initial_competence = case.physical_case.organization.competence_initial
    expected_value = sum(
        probability * value(0, initial_competence, state)
        for state, probability in enumerate(case.initial_probabilities)
    )
    return S7ExactResult(expected_value, value.cache_info().currsize,
                         transfer_available, choices, pruned_count, state_values)


def solve_reactive_greedy(case: S7MarkovDemandCase, *,
                          transfer_available: bool,
                          efficacy: TeachingEfficacyNK | None = None) -> S7ExactResult:
    """Evaluate the exact immediate-reward action, with no future lookahead."""
    state_cases = _state_cases(case, transfer_available=transfer_available,
                               efficacy=efficacy)
    choices: dict[tuple[int, Competence, int], JointActionNK] = {}

    @lru_cache(maxsize=None)
    def value(time: int, competence: Competence, demand_state: int) -> float:
        if time == case.horizon:
            return 0.0
        physical_case, actions = state_cases[demand_state]
        problem = case.demand_states[demand_state]
        best_reward = float("-inf")
        best_action = None
        best_next = None
        for action in actions:
            reward, next_competence = _step(
                physical_case, competence, problem, action, efficacy=efficacy,
            )
            if reward > best_reward + TOL:
                best_reward, best_action, best_next = reward, action, next_competence
        assert best_action is not None and best_next is not None
        choices[(time, competence, demand_state)] = best_action
        continuation = 0.0
        if time + 1 < case.horizon:
            continuation = sum(
                probability * value(time + 1, best_next, next_state)
                for next_state, probability in enumerate(
                    case.transition_probabilities[demand_state]
                )
            )
        return best_reward + continuation

    initial_competence = case.physical_case.organization.competence_initial
    expected_value = sum(
        probability * value(0, initial_competence, state)
        for state, probability in enumerate(case.initial_probabilities)
    )
    return S7ExactResult(expected_value, value.cache_info().currsize,
                         transfer_available, choices)


def solve_best_myopic(case: S7MarkovDemandCase, *,
                      transfer_available: bool,
                      efficacy: TeachingEfficacyNK | None = None) -> S7ExactResult:
    """Reactive policy: exact immediate CES optimum, development tie-break."""
    state_cases = _state_cases(case, transfer_available=transfer_available,
                               efficacy=efficacy)
    choices: dict[tuple[int, Competence, int], JointActionNK] = {}

    @lru_cache(maxsize=None)
    def value(time: int, competence: Competence, demand_state: int) -> float:
        if time == case.horizon:
            return 0.0
        physical_case, actions = state_cases[demand_state]
        problem = case.demand_states[demand_state]
        evaluated = []
        for action in actions:
            reward, successor = _step(
                physical_case, competence, problem, action, efficacy=efficacy,
            )
            evaluated.append((action, reward, successor))
        action, _, _, _ = select_best_myopic_action(competence, evaluated)
        choices[(time, competence, demand_state)] = action
        selected_immediate = next(reward for candidate, reward, _ in evaluated
                                  if candidate == action)
        successor = next(state for candidate, _, state in evaluated if candidate == action)
        continuation = 0.0
        if time + 1 < case.horizon:
            continuation = sum(
                probability * value(time + 1, successor, next_state)
                for next_state, probability in enumerate(
                    case.transition_probabilities[demand_state]
                )
            )
        return selected_immediate + continuation

    initial = case.physical_case.organization.competence_initial
    expected_value = sum(probability * value(0, initial, state)
                         for state, probability in enumerate(case.initial_probabilities))
    return S7ExactResult(expected_value, value.cache_info().currsize,
                         transfer_available, choices)


def solve_current_demand_myopic(case: S7MarkovDemandCase, *,
                                transfer_available: bool = False,
                                efficacy: TeachingEfficacyNK | None = None) -> S7ExactResult:
    """Reactive CES maximizer, tie-broken by learning demanded right now."""
    state_cases = _state_cases(case, transfer_available=transfer_available,
                               efficacy=efficacy)
    choices: dict[tuple[int, Competence, int], JointActionNK] = {}

    @lru_cache(maxsize=None)
    def value(time: int, competence: Competence, demand_state: int) -> float:
        if time == case.horizon:
            return 0.0
        physical_case, actions = state_cases[demand_state]
        problem = case.demand_states[demand_state]
        evaluated = []
        for action in actions:
            reward, successor = _step(
                physical_case, competence, problem, action, efficacy=efficacy,
            )
            evaluated.append((action, reward, successor))
        action, _, _, _ = select_current_demand_myopic_action(
            competence, problem, evaluated)
        choices[(time, competence, demand_state)] = action
        immediate, successor = next((reward, state) for candidate, reward, state in evaluated
                                    if candidate == action)
        continuation = 0.0
        if time + 1 < case.horizon:
            continuation = sum(
                probability * value(time + 1, successor, next_state)
                for next_state, probability in enumerate(
                    case.transition_probabilities[demand_state]
                )
            )
        return immediate + continuation

    initial = case.physical_case.organization.competence_initial
    expected_value = sum(probability * value(0, initial, state)
                         for state, probability in enumerate(case.initial_probabilities))
    return S7ExactResult(expected_value, value.cache_info().currsize,
                         transfer_available, choices)


def _legacy_myopic_selection(
    competence: Competence,
    evaluated_actions: Sequence[tuple[JointActionNK, float, Competence]],
) -> JointActionNK:
    """Reproduce the original sequential catalog/tolerance tie rule."""
    best_reward = float("-inf")
    best_action = None
    for action, reward, _ in evaluated_actions:
        if reward > best_reward + TOL:
            best_reward, best_action = reward, action
    assert best_action is not None
    return best_action


def audit_myopic_tiebreaks(
    case: S7MarkovDemandCase,
    original: S7ExactResult,
    best_myopic: S7ExactResult,
    *, transfer_available: bool,
    efficacy: TeachingEfficacyNK | None = None,
) -> tuple[dict, ...]:
    """Audit both selectors on the union of their reached states."""
    state_cases = _state_cases(case, transfer_available=transfer_available,
                               efficacy=efficacy)
    states = set(original.actions_by_state) | set(best_myopic.actions_by_state)
    rows = []
    for time, competence, demand_state in sorted(
            states, key=lambda row: (row[0], row[2], row[1])):
        physical_case, actions = state_cases[demand_state]
        problem = case.demand_states[demand_state]
        evaluated = []
        for action in actions:
            reward, successor = _step(
                physical_case, competence, problem, action, efficacy=efficacy,
            )
            evaluated.append((action, reward, successor))
        selected_best, max_reward, tie_count, best_gain = select_best_myopic_action(
            competence, evaluated)
        selected_legacy = _legacy_myopic_selection(competence, evaluated)
        by_action = {action: (reward, successor)
                     for action, reward, successor in evaluated}
        legacy_reward, legacy_successor = by_action[selected_legacy]
        best_reward, best_successor = by_action[selected_best]
        tied = [(action, reward, successor) for action, reward, successor in evaluated
                if max_reward - reward <= TOL]
        successors = [successor for _, _, successor in tied]
        outputs = [productive_outputs_nk(competence, action.production)
                   for action, _, _ in tied]
        resources = [
            (sum(sum(agent) for agent in action.production),
             0.0 if action.teaching is None else 2.0 * action.teaching.effort)
            for action, _, _ in tied
        ]
        competence_different = any(
            any(abs(left[i][k] - right[i][k]) > TOL
                for i in range(len(left)) for k in range(len(left[i])))
            for left in successors for right in successors
        )
        output_different = any(
            any(abs(left[k] - right[k]) > TOL for k in range(len(left)))
            for left in outputs for right in outputs
        )
        resource_different = len(set(resources)) > 1
        equivalent_pair = any(
            all(abs(left_comp[i][k] - right_comp[i][k]) <= TOL
                for i in range(len(left_comp))
                for k in range(len(left_comp[i])))
            and all(abs(left_output[k] - right_output[k]) <= TOL
                    for k in range(len(left_output)))
            and left_resource == right_resource
            for left_index, (left_comp, left_output, left_resource) in enumerate(
                zip(successors, outputs, resources))
            for right_comp, right_output, right_resource in zip(
                successors[left_index + 1:], outputs[left_index + 1:],
                resources[left_index + 1:])
        )
        tie_classes = []
        if equivalent_pair:
            tie_classes.append("A_equivalent_physical_consequences")
        if competence_different:
            tie_classes.append("B_different_competence_successors")
        if output_different or resource_different:
            tie_classes.append("C_other_physical_or_resource_differences")
        rows.append({
            "period": time,
            "demand_state": problem.problem_id,
            "competence_state": competence,
            "admissible_action_count": len(actions),
            "maximum_immediate_CES": max_reward,
            "tied_action_count": tie_count,
            "tie_classes": tuple(tie_classes),
            "tie_set_differing_competences": competence_different,
            "tie_set_differing_outputs": output_different,
            "tie_set_differing_resources": resource_different,
            "tie_set_contains_physically_equivalent_pair": equivalent_pair,
            "legacy_action": selected_legacy,
            "best_myopic_action": selected_best,
            "legacy_immediate_CES": legacy_reward,
            "best_myopic_immediate_CES": best_reward,
            "legacy_positive_competence_gain": positive_competence_gain(
                competence, legacy_successor),
            "best_myopic_positive_competence_gain": best_gain,
            "selected_successor_competence_difference": tuple(
                tuple(best_successor[i][k] - legacy_successor[i][k]
                      for k in range(len(competence[i])))
                for i in range(len(competence))
            ),
            "selected_actions_differ": selected_legacy != selected_best,
            "tolerance": TOL,
        })
    return tuple(rows)


def independent_tree_enumeration(
    case: S7MarkovDemandCase, *, transfer_available: bool,
    efficacy: TeachingEfficacyNK | None = None,
) -> float:
    """Exhaustively evaluate the contingent action tree without memoization."""
    base = case.physical_case
    catalogs = []
    physical_cases = []
    for demand in case.demand_states:
        one_state = ExactTransferCase(
            base.organization, (demand,) * case.horizon, base.profile,
            base.efficacy, base.teaching_parameters, base.teaching_effort,
            base.effort_choices,
        )
        physical_cases.append(one_state)
        catalogs.append(independent_action_catalogs(
            one_state, transfer_available=transfer_available, efficacy=efficacy,
        )[0])

    def enumerate_from(time: int, competence: Competence,
                       demand_state: int) -> float:
        if time == case.horizon:
            return 0.0
        physical_case = physical_cases[demand_state]
        problem = case.demand_states[demand_state]
        best = float("-inf")
        for action in catalogs[demand_state]:
            reward, next_competence = _step(
                physical_case, competence, problem, action, efficacy=efficacy,
            )
            continuation = 0.0
            if time + 1 < case.horizon:
                continuation = sum(
                    probability * enumerate_from(time + 1, next_competence, next_state)
                    for next_state, probability in enumerate(
                        case.transition_probabilities[demand_state]
                    )
                )
            best = max(best, reward + continuation)
        return best

    initial_competence = base.organization.competence_initial
    return sum(
        probability * enumerate_from(0, initial_competence, state)
        for state, probability in enumerate(case.initial_probabilities)
    )


def replay_markov_policy(case: S7MarkovDemandCase, result: S7ExactResult,
                         demand_path: tuple[int, ...], *,
                         efficacy: TeachingEfficacyNK | None = None) -> tuple[dict, ...]:
    """Replay a contingent policy on an observed demand-state path."""
    if len(demand_path) != case.horizon or any(
        not 0 <= state < len(case.demand_states) for state in demand_path
    ):
        raise ValueError("demand_path must contain one valid state per period")
    competence = case.physical_case.organization.competence_initial
    rows = []
    for time, demand_state in enumerate(demand_path):
        problem = case.demand_states[demand_state]
        action = result.actions_by_state[(time, competence, demand_state)]
        one_state = ExactTransferCase(
            case.physical_case.organization, (problem,), case.physical_case.profile,
            case.physical_case.efficacy, case.physical_case.teaching_parameters,
            case.physical_case.teaching_effort, case.physical_case.effort_choices,
        )
        reward, next_competence = _step(
            one_state, competence, problem, action, efficacy=efficacy,
        )
        rows.append({
            "period": time,
            "demand_state": demand_state,
            "problem_id": problem.problem_id,
            "action": action,
            "reward": reward,
            "competence_before": competence,
            "competence_after": next_competence,
        })
        competence = next_competence
    return tuple(rows)
