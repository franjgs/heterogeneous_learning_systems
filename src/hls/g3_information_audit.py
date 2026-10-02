"""Finite, adversarial information audit for the fixed G3 ground truth.

The audit is deliberately descriptive: it groups a declared finite campaign by
progressively poorer standard assignment information.  It neither changes G3
physics nor learns a policy.  "Decision" means choosing the action with the
largest organizational-development value ``D`` within a G3 world.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Literal

from .g3_organizational_value import (
    G3A_ASSIGNMENTS,
    G3B_ASSIGNMENTS,
    G3DualAction,
    G3State,
    development_g3a_algebraic,
    development_g3a_direct,
    development_g3b_algebraic,
    development_g3b_direct,
    development_g3dual_algebraic,
    development_g3dual_direct,
    learning_increment,
    reward_g3a,
    reward_g3b,
    reward_g3dual,
    transition_g3a,
    transition_g3b,
    transition_g3dual,
)
from .minimal_reference_scenario import EXACT_TOL


KEY_DIGITS = 12
D_TOL = 1e-10
GRID_VALUES: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)
GRID_SCALES: tuple[float, ...] = (0.0, 0.25, 0.5, 1.0, 2.0)
Regime = Literal["g3a", "g3b", "dual"]


def _number(value: float) -> float:
    return round(value, KEY_DIGITS)


def _key(values: Iterable[float]) -> tuple[float, ...]:
    return tuple(_number(value) for value in values)


def _state_key(state: G3State) -> tuple[float, ...]:
    return tuple(value for row in state for value in row)


def _states(values: tuple[float, ...]) -> Iterable[G3State]:
    for flat in product(values, repeat=6):
        yield ((flat[0], flat[1]), (flat[2], flat[3]), (flat[4], flat[5]))


@dataclass(frozen=True)
class ActionObservation:
    state: G3State
    scale: float
    action: int | tuple[int, int]
    development: float
    feature: tuple[float, ...]

    def example(self) -> dict[str, object]:
        return {
            "state": [list(row) for row in self.state],
            "learning_scale": self.scale,
            "action": list(self.action) if isinstance(self.action, tuple) else self.action,
            "D": self.development,
            "feature": list(self.feature),
        }


@dataclass(frozen=True)
class RepresentationResult:
    action_classes: int
    d_collision_classes: int
    d_collision_observations: int
    max_d_span: float
    ranking_classes: int
    ranking_collision_classes: int
    oracle_agreement: float
    regret_total: float
    regret_mean: float
    regret_worst: float
    oracle_development_value_recovered: float
    d_counterexample: dict[str, object] | None
    ranking_counterexample: dict[str, object] | None


def _g3a_features(state: G3State, action: tuple[int, int], scale: float) -> dict[str, tuple[float, ...]]:
    i, j = action
    k = next(worker for worker in range(3) if worker not in action)
    alpha = learning_increment(state[i][0], scale)
    beta = learning_increment(state[j][1], scale)
    weights = {(r, s): state[r][0] + state[s][1] for r, s in G3A_ASSIGNMENTS}
    best = max(weights.values())
    ordered = sorted(weights.values(), reverse=True)
    global_gap = best - ordered[1]
    gaps = (best - weights[(i, j)], best - weights[(i, k)], best - weights[(k, j)])
    local = (alpha, beta)
    return {
        "amount": _key((alpha + beta,)),
        "localized": _key(local),
        "localized_global_gap": _key(local + (global_gap,)),
        "localized_g_ij": _key(local + gaps[:1]),
        "localized_g_ik": _key(local + gaps[1:2]),
        "localized_g_kj": _key(local + gaps[2:]),
        "localized_g_ij_g_ik": _key(local + gaps[:2]),
        "localized_g_ij_g_kj": _key(local + (gaps[0], gaps[2])),
        "localized_g_ik_g_kj": _key(local + gaps[1:]),
        "full_exact": _key(local + gaps),
    }


def _full_regime_features(
    state: G3State,
    distinguished: int,
    scale: float,
    *,
    dual: bool,
) -> dict[str, tuple[float, ...]]:
    # Under (2,1), q=b-a and the distinguished worker executes B.  Under the
    # explicit dual, p=a-b and the distinguished worker executes A.
    advantage = tuple((row[0] - row[1]) if dual else (row[1] - row[0]) for row in state)
    own_increment = learning_increment(state[distinguished][0 if dual else 1], scale)
    other_increments = tuple(
        learning_increment(state[worker][1 if dual else 0], scale)
        for worker in range(3) if worker != distinguished
    )
    best = max(advantage)
    ordered = sorted(advantage, reverse=True)
    gaps = tuple(best - value for value in advantage)
    other = tuple(worker for worker in range(3) if worker != distinguished)
    # Align roles rather than worker names: own is the candidate whose
    # advantage increases; each other candidate's advantage decreases.
    # This preserves the candidate/increment relation without treating a
    # worker label as informative.
    local = (own_increment,) + other_increments
    role_gaps = (gaps[distinguished],) + tuple(gaps[worker] for worker in other)
    partial = role_gaps[:2]
    return {
        "amount": _key((sum(local),)),
        "localized": _key(local),
        "localized_best_advantage": _key(local + (best,)),
        "localized_best_second_advantage": _key(local + (ordered[0], ordered[1])),
        "localized_own_gap": _key(local + role_gaps[:1]),
        "localized_two_gaps": _key(local + partial),
        "full_exact": _key(local + role_gaps),
    }


def _observations(
    regime: Regime,
    values: tuple[float, ...],
    scales: tuple[float, ...],
) -> tuple[dict[str, list[ActionObservation]], float]:
    by_representation: dict[str, list[ActionObservation]] = defaultdict(list)
    max_residual = 0.0
    for state in _states(values):
        for scale in scales:
            if regime == "g3a":
                actions = G3A_ASSIGNMENTS
                direct: Callable[[G3State, object, float], float] = development_g3a_direct
                algebraic: Callable[[G3State, object, float], float] = development_g3a_algebraic
                feature = _g3a_features
            elif regime == "g3b":
                actions = G3B_ASSIGNMENTS
                direct = development_g3b_direct
                algebraic = development_g3b_algebraic
                feature = lambda s, a, e: _full_regime_features(s, a, e, dual=False)
            else:
                actions = G3B_ASSIGNMENTS
                direct = development_g3dual_direct
                algebraic = development_g3dual_algebraic
                feature = lambda s, a, e: _full_regime_features(s, a, e, dual=True)
            for action in actions:
                d_direct = direct(state, action, scale)
                d_alg = algebraic(state, action, scale)
                max_residual = max(max_residual, abs(d_direct - d_alg))
                for name, values_for_action in feature(state, action, scale).items():
                    observation = ActionObservation(state, scale, action, d_direct, values_for_action)
                    by_representation[name].append(observation)
    return by_representation, max_residual


def _analyze_action_classes(observations: list[ActionObservation]) -> tuple[int, int, int, float, dict[str, object] | None]:
    grouped: dict[tuple[float, ...], list[ActionObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.feature].append(observation)
    collision_classes = 0
    collision_observations = 0
    max_span = 0.0
    example = None
    for feature, group in grouped.items():
        span = max(item.development for item in group) - min(item.development for item in group)
        max_span = max(max_span, span)
        if span > D_TOL:
            collision_classes += 1
            collision_observations += len(group)
            if example is None:
                low = min(group, key=lambda item: item.development)
                high = max(group, key=lambda item: item.development)
                example = {"feature": list(feature), "low": low.example(), "high": high.example(), "D_span": span}
    return len(grouped), collision_classes, collision_observations, max_span, example


def _analyze_decision_classes(observations: list[ActionObservation]) -> tuple[int, int, float, float, float, float, dict[str, object] | None]:
    # Reconstruct worlds from observations.  Within a candidate representation,
    # its ordered action features are all information available to an action
    # chooser; the action order is the fixed documented action enumeration.
    worlds: dict[tuple[tuple[float, ...], float], list[ActionObservation]] = defaultdict(list)
    for observation in observations:
        worlds[(_state_key(observation.state), observation.scale)].append(observation)
    classes: dict[tuple[tuple[float, ...], ...], list[list[ActionObservation]]] = defaultdict(list)
    for action_observations in worlds.values():
        ordered = sorted(action_observations, key=lambda item: repr(item.action))
        classes[tuple(item.feature for item in ordered)].append(ordered)
    collision_classes = 0
    example = None
    selections: dict[tuple[tuple[float, ...], ...], int] = {}
    for signature, grouped_worlds in classes.items():
        choices = [max(range(len(world)), key=lambda index: world[index].development) for world in grouped_worlds]
        if len(set(choices)) > 1:
            collision_classes += 1
            if example is None:
                first_choice = choices[0]
                other_index = next(index for index, choice in enumerate(choices) if choice != first_choice)
                example = {
                    "signature": [list(feature) for feature in signature],
                    "first": {"oracle_action": list(grouped_worlds[0][first_choice].action) if isinstance(grouped_worlds[0][first_choice].action, tuple) else grouped_worlds[0][first_choice].action, "world": grouped_worlds[0][0].example()},
                    "second": {"oracle_action": list(grouped_worlds[other_index][choices[other_index]].action) if isinstance(grouped_worlds[other_index][choices[other_index]].action, tuple) else grouped_worlds[other_index][choices[other_index]].action, "world": grouped_worlds[other_index][0].example()},
                }
        totals = [sum(world[index].development for world in grouped_worlds) for index in range(len(grouped_worlds[0]))]
        selections[signature] = max(range(len(totals)), key=lambda index: totals[index])
    agreements = 0
    regret_total = 0.0
    regret_worst = 0.0
    oracle_total = 0.0
    world_count = 0
    for signature, grouped_worlds in classes.items():
        chosen = selections[signature]
        for world in grouped_worlds:
            oracle = max(item.development for item in world)
            chosen_value = world[chosen].development
            regret = max(0.0, oracle - chosen_value)
            agreements += int(regret <= D_TOL)
            regret_total += regret
            regret_worst = max(regret_worst, regret)
            oracle_total += oracle
            world_count += 1
    recovered = 1.0 if oracle_total <= D_TOL else 1.0 - regret_total / oracle_total
    return len(classes), collision_classes, agreements / world_count, regret_total, regret_total / world_count, regret_worst, recovered, example


def _optimal_indices(rewards: tuple[float, ...]) -> tuple[int, ...]:
    maximum = max(rewards)
    return tuple(index for index, value in enumerate(rewards) if maximum - value <= EXACT_TOL)


def _structural_diagnostics(
    regime: Regime,
    values: tuple[float, ...],
    scales: tuple[float, ...],
) -> dict[str, object]:
    """Describe ordinary assignment boundaries without treating frequency as prevalence."""
    worlds = 0
    pre_ties = 0
    assignment_changes = 0
    saturation_worlds = 0
    specialist_worlds = 0
    generalist_worlds = 0
    f4_reversed_pairs = 0
    f4_comparable_pairs = 0
    f3_shared_b_comparisons = 0
    f3_shared_b_differences = 0
    for state in _states(values):
        specialist_world = any(row in ((0.0, 1.0), (1.0, 0.0)) for row in state)
        generalist_world = any(abs(row[0] - row[1]) <= EXACT_TOL for row in state)
        for scale in scales:
            worlds += 1
            if any(value >= 1.0 - EXACT_TOL for row in state for value in row):
                saturation_worlds += 1
            specialist_worlds += int(specialist_world)
            generalist_worlds += int(generalist_world)
            if regime == "g3a":
                actions = G3A_ASSIGNMENTS
                rewards = tuple(reward_g3a(state, action) for action in actions)
                transitions = tuple(transition_g3a(state, action, scale) for action in actions)
                direct = development_g3a_direct
                amounts = tuple(
                    learning_increment(state[action[0]][0], scale) + learning_increment(state[action[1]][1], scale)
                    for action in actions
                )
            elif regime == "g3b":
                actions = G3B_ASSIGNMENTS
                rewards = tuple(reward_g3b(state, action) for action in actions)
                transitions = tuple(transition_g3b(state, action, scale) for action in actions)
                direct = development_g3b_direct
                amounts = tuple(
                    learning_increment(state[action][1], scale)
                    + sum(learning_increment(state[worker][0], scale) for worker in range(3) if worker != action)
                    for action in actions
                )
            else:
                actions = G3B_ASSIGNMENTS
                rewards = tuple(reward_g3dual(state, action) for action in actions)
                transitions = tuple(transition_g3dual(state, action, scale) for action in actions)
                direct = development_g3dual_direct
                amounts = tuple(
                    learning_increment(state[action][0], scale)
                    + sum(learning_increment(state[worker][1], scale) for worker in range(3) if worker != action)
                    for action in actions
                )
            optimal_before = _optimal_indices(rewards)
            pre_ties += int(len(optimal_before) > 1)
            developments = tuple(direct(state, action, scale) for action in actions)
            if any(_optimal_indices(tuple(reward(state_after, candidate) for candidate in actions)) != optimal_before for state_after, reward in zip(transitions, [reward_g3a if regime == "g3a" else reward_g3b if regime == "g3b" else reward_g3dual] * len(transitions))):
                assignment_changes += 1
            for left in range(len(actions)):
                for right in range(left + 1, len(actions)):
                    amount_difference = amounts[left] - amounts[right]
                    development_difference = developments[left] - developments[right]
                    if abs(amount_difference) > EXACT_TOL and abs(development_difference) > EXACT_TOL:
                        f4_comparable_pairs += 1
                        if amount_difference * development_difference < 0.0:
                            f4_reversed_pairs += 1
            if regime == "g3a":
                for i, j in actions:
                    f3_shared_b_comparisons += 1
                    f3_shared_b_differences += int(abs(development_g3a_direct(state, (i, j), scale) - development_g3b_direct(state, j, scale)) > D_TOL)
    return {
        "worlds": worlds,
        "pre_assignment_tie_worlds": pre_ties,
        "any_action_changes_terminal_assignment_worlds": assignment_changes,
        "saturation_state_worlds": saturation_worlds,
        "pure_specialist_state_worlds": specialist_worlds,
        "generalist_or_equal_competence_state_worlds": generalist_worlds,
        "f4_comparable_action_pairs": f4_comparable_pairs,
        "f4_amount_vs_D_reversed_pairs": f4_reversed_pairs,
        "f3_shared_B_comparisons": f3_shared_b_comparisons,
        "f3_shared_B_D_differences": f3_shared_b_differences,
    }


def audit_regime(
    regime: Regime,
    *,
    values: tuple[float, ...] = GRID_VALUES,
    scales: tuple[float, ...] = GRID_SCALES,
) -> dict[str, object]:
    """Audit a declared finite state/scale family for one fixed G3 regime."""
    observations_by_name, max_residual = _observations(regime, values, scales)
    representations: dict[str, dict[str, object]] = {}
    for name, observations in observations_by_name.items():
        action_classes, d_collisions, d_observations, d_span, d_example = _analyze_action_classes(observations)
        decision = _analyze_decision_classes(observations)
        ranking_classes, ranking_collisions, agreement, regret_total, regret_mean, regret_worst, recovered, ranking_example = decision
        representations[name] = RepresentationResult(
            action_classes, d_collisions, d_observations, d_span,
            ranking_classes, ranking_collisions, agreement, regret_total,
            regret_mean, regret_worst, recovered, d_example, ranking_example,
        ).__dict__
    return {
        "regime": regime,
        "state_values": list(values),
        "learning_scales": list(scales),
        "worlds": len(values) ** 6 * len(scales),
        "action_observations": sum(len(items) for items in observations_by_name.values()) // len(observations_by_name),
        "max_direct_algebraic_residual": max_residual,
        "representations": representations,
        "structural_diagnostics": _structural_diagnostics(regime, values, scales),
    }


def run_g3_information_audit() -> dict[str, object]:
    """Run the complete fixed-grid audit for G3a, G3b, and its dual."""
    regimes = {name: audit_regime(name) for name in ("g3a", "g3b", "dual")}
    return {
        "campaign": "g3_phase_v_adversarial_information_audit",
        "scope": "finite 5^6 state grid x five learning scales; no general sufficiency claim",
        "regimes": regimes,
    }
