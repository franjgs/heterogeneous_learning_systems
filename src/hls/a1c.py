"""Deterministic implementation of the pre-registered A1c competence sweep."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Iterable, Mapping

from .a1a import (
    A1aWorld,
    DevelopmentAction,
    Learner,
    LEARNERS,
    PolicySolution,
    StrongSEPSolution,
    optimal_set,
    reference_worlds,
    solve_hls,
    solve_sep_omega,
    solve_strong_sep,
)
from .a1b import (
    BOUNDARY,
    GREATER,
    LESS,
    NEGATIVE_UNEXPECTED,
    NO_ADVANTAGE,
    STRICT_ADVANTAGE,
    TOL,
    analytical_regime,
    conservative_advantage,
    expected_observed_regime,
    observed_regime,
)


PHASE_1 = "A1c.1"
PHASE_2 = "A1c.2"
EXPECTED_COUNTS = {PHASE_1: 17, PHASE_2: 441}
IMMEDIATE_TIE = "IMMEDIATE_TIE"

BASE_RHO = Fraction(3, 4)
BASE_ETA = Fraction(4, 5)
BASE_KAPPA = Fraction(1, 50)
BASE_EBAR = Fraction(1, 2)
BASE_E_11 = Fraction(1, 5)
BASE_E_21 = Fraction(9, 10)
FUTURE_THRESHOLD = Fraction(4, 21)


@dataclass(frozen=True)
class SweepConfiguration:
    """One pre-registered A1c competence configuration."""

    phase: str
    configuration_id: str
    c_11: Fraction
    c_12: Fraction
    c_21: Fraction
    c_22: Fraction


def present_gap_configurations() -> tuple[SweepConfiguration, ...]:
    """Return exactly the 17 frozen A1c.1 present-gap worlds."""
    return tuple(
        SweepConfiguration(
            phase=PHASE_1,
            configuration_id=f"A1c.1-{index + 1:04d}",
            c_11=Fraction(4, 5),
            c_12=Fraction(1, 2),
            c_21=Fraction(index, 20),
            c_22=Fraction(1, 5),
        )
        for index in range(17)
    )


def future_geometry_configurations() -> tuple[SweepConfiguration, ...]:
    """Return exactly the 21-by-21 frozen A1c.2 future square."""
    configurations = []
    for c_12_index in range(21):
        for c_22_index in range(21):
            configurations.append(
                SweepConfiguration(
                    phase=PHASE_2,
                    configuration_id=f"A1c.2-{len(configurations) + 1:04d}",
                    c_11=Fraction(4, 5),
                    c_12=Fraction(c_12_index, 20),
                    c_21=Fraction(7, 10),
                    c_22=Fraction(c_22_index, 20),
                )
            )
    return tuple(configurations)


def all_configurations() -> tuple[SweepConfiguration, ...]:
    """Return exactly the 458 pre-registered A1c configurations."""
    return present_gap_configurations() + future_geometry_configurations()


def world_for(configuration: SweepConfiguration) -> A1aWorld:
    """Construct one A1c world by changing only frozen competence entries."""
    base = reference_worlds()["E"]
    return replace(
        base,
        competence=(
            (float(configuration.c_11), float(configuration.c_12)),
            (float(configuration.c_21), float(configuration.c_22)),
        ),
    )


def relabel_world(world: A1aWorld) -> A1aWorld:
    """Physically exchange learner rows in competence and opportunity geometry."""
    return replace(
        world,
        competence=(world.competence[1], world.competence[0]),
        executor_opportunity=(
            world.executor_opportunity[1],
            world.executor_opportunity[0],
        ),
    )


def _swap_learner(learner: Learner) -> Learner:
    return Learner.M2 if learner == Learner.M1 else Learner.M1


def _swap_learner_set(actions: Iterable[Learner]) -> frozenset[Learner]:
    return frozenset(_swap_learner(action) for action in actions)


def _swap_development_set(
    actions: Iterable[DevelopmentAction],
) -> frozenset[DevelopmentAction]:
    return frozenset(
        action
        if action.is_null
        else DevelopmentAction(_swap_learner(action.recipient), action.task)  # type: ignore[arg-type]
        for action in actions
    )


def _learner_set(actions: Iterable[Learner]) -> str:
    return "|".join(sorted(action.value for action in actions))


def _development_set(actions: Iterable[DevelopmentAction]) -> str:
    labels = []
    for action in actions:
        if action.is_null:
            labels.append("null")
        else:
            assert action.recipient is not None and action.task is not None
            labels.append(f"develop_{action.recipient.value}_task_{action.task}")
    return "|".join(sorted(labels))


def development_category(actions: frozenset[DevelopmentAction]) -> str:
    """Classify the complete optimal development set without discarding ties."""
    if len(actions) != 1:
        return "ties"
    action = next(iter(actions))
    if action.is_null:
        return "null"
    assert action.recipient is not None
    return action.recipient.value


def terminal_best_set(world: A1aWorld) -> frozenset[Learner]:
    """Return all initially terminal-best learners under the frozen tolerance."""
    values = {
        learner: world.competence[index][world.q1 - 1]
        for index, learner in enumerate(LEARNERS)
    }
    return frozenset(optimal_set(values, abs_tol=TOL))  # type: ignore[arg-type]


def terminal_best_category(actions: frozenset[Learner]) -> str:
    if len(actions) != 1:
        return "tie"
    return next(iter(actions)).value


def _solutions(world: A1aWorld) -> tuple[PolicySolution, StrongSEPSolution, PolicySolution]:
    return solve_hls(world), solve_strong_sep(world), solve_sep_omega(world)


def _full_relabeling_check(
    world: A1aWorld,
    hls: PolicySolution,
    sep: StrongSEPSolution,
    sep_omega: PolicySolution,
) -> bool:
    relabeled_hls, relabeled_sep, relabeled_omega = _solutions(relabel_world(world))
    scalar_pairs = (
        (hls.optimal_value, relabeled_hls.optimal_value),
        (sep.value_min, relabeled_sep.value_min),
        (sep.value_max, relabeled_sep.value_max),
        (
            conservative_advantage(hls, sep),
            conservative_advantage(relabeled_hls, relabeled_sep),
        ),
        (sep_omega.optimal_value, relabeled_omega.optimal_value),
    )
    scalars_match = all(abs(left - right) <= TOL for left, right in scalar_pairs)
    sets_match = (
        _swap_learner_set(hls.optimal_operational_actions)
        == relabeled_hls.optimal_operational_actions
        and _swap_learner_set(sep.immediate_optimal_actions)
        == relabeled_sep.immediate_optimal_actions
        and _swap_learner_set(sep_omega.optimal_operational_actions)
        == relabeled_omega.optimal_operational_actions
        and _swap_development_set(hls.optimal_development_actions)
        == relabeled_hls.optimal_development_actions
    )
    return scalars_match and sets_match


def _future_pair_check(configuration: SweepConfiguration, world: A1aWorld) -> bool:
    if configuration.phase != PHASE_2:
        return True
    swapped_configuration = replace(
        configuration,
        c_12=configuration.c_22,
        c_22=configuration.c_12,
    )
    swapped_world = world_for(swapped_configuration)
    hls = solve_hls(world)
    swapped_hls = solve_hls(swapped_world)
    scalar_match = all(
        abs(left - right) <= TOL
        for left, right in (
            (hls.no_opportunity_value, swapped_hls.no_opportunity_value),
            (hls.opportunity_value, swapped_hls.opportunity_value),
            (
                hls.opportunity_value - hls.no_opportunity_value,
                swapped_hls.opportunity_value - swapped_hls.no_opportunity_value,
            ),
        )
    )
    return (
        scalar_match
        and _swap_development_set(hls.optimal_development_actions)
        == swapped_hls.optimal_development_actions
        and _swap_learner_set(terminal_best_set(world))
        == terminal_best_set(swapped_world)
    )


def evaluate_configuration(configuration: SweepConfiguration) -> dict[str, object]:
    """Evaluate one A1c configuration through the unchanged A1a solver."""
    world = world_for(configuration)
    hls, sep, sep_omega = _solutions(world)
    n_value = hls.no_opportunity_value
    d_value = hls.opportunity_value
    d_minus_n = d_value - n_value
    delta_j_cons = conservative_advantage(hls, sep)
    observed = observed_regime(delta_j_cons)
    immediate_tie = len(sep.immediate_optimal_actions) > 1

    if immediate_tie:
        h_label = ""
        s_label = ""
        delta_r: float | None = None
        delta_g: float | None = None
        margin: float | None = None
        predicted = IMMEDIATE_TIE
        expected_observed = NO_ADVANTAGE
    else:
        h = next(iter(sep.immediate_optimal_actions))
        alternatives = tuple(learner for learner in LEARNERS if learner != h)
        if len(alternatives) != 1:
            raise ValueError("A1c requires exactly one alternative action")
        s = alternatives[0]
        h_label, s_label = h.value, s.value
        delta_r = hls.operational_rewards[h] - hls.operational_rewards[s]
        delta_g = hls.continuation_values[s] - hls.continuation_values[h]
        margin = delta_g - delta_r
        predicted = analytical_regime(margin)
        expected_observed = expected_observed_regime(predicted)

    sep_omega_gap = hls.optimal_value - sep_omega.optimal_value
    d_equals_n_violation = abs(d_minus_n) <= TOL and observed == STRICT_ADVANTAGE
    below_threshold_violation = (
        not immediate_tie
        and d_minus_n < float(FUTURE_THRESHOLD) - TOL
        and observed == STRICT_ADVANTAGE
    )
    above_threshold_violation = (
        configuration.phase == PHASE_2
        and d_minus_n > float(FUTURE_THRESHOLD) + TOL
        and observed != STRICT_ADVANTAGE
    )

    terminal_actions = terminal_best_set(world)
    development_actions = hls.optimal_development_actions
    full_relabeling_pass = _full_relabeling_check(world, hls, sep, sep_omega)
    future_pair_pass = _future_pair_check(configuration, world)

    return {
        "phase": configuration.phase,
        "configuration_id": configuration.configuration_id,
        "c_11": world.competence[0][0],
        "c_12": world.competence[0][1],
        "c_21": world.competence[1][0],
        "c_22": world.competence[1][1],
        "rho": world.rho,
        "eta": world.eta,
        "kappa": world.kappa,
        "ebar": world.opportunity_baseline[0],
        "e_11": world.executor_opportunity[0][0],
        "e_21": world.executor_opportunity[1][0],
        "beta": world.beta,
        "q0": world.q0,
        "q1": world.q1,
        "N": n_value,
        "D": d_value,
        "D_minus_N": d_minus_n,
        "optimal_development_actions": _development_set(development_actions),
        "development_category": development_category(development_actions),
        "initial_terminal_best": _learner_set(terminal_actions),
        "initial_terminal_best_category": terminal_best_category(terminal_actions),
        "SEP_immediate_optimal_actions": _learner_set(sep.immediate_optimal_actions),
        "immediate_tie": immediate_tie,
        "h": h_label,
        "s": s_label,
        "delta_R": delta_r,
        "g_M1": hls.opportunity_probabilities[Learner.M1],
        "g_M2": hls.opportunity_probabilities[Learner.M2],
        "G_M1": hls.continuation_values[Learner.M1],
        "G_M2": hls.continuation_values[Learner.M2],
        "delta_G": delta_g,
        "analytical_margin": margin,
        "HLS_optimal_actions": _learner_set(hls.optimal_operational_actions),
        "J_HLS": hls.optimal_value,
        "J_SEP_min": sep.value_min,
        "J_SEP_max": sep.value_max,
        "Delta_J_cons": delta_j_cons,
        "J_SEP_Omega": sep_omega.optimal_value,
        "SEP_Omega_gap": sep_omega_gap,
        "predicted_regime": predicted,
        "observed_regime": observed,
        "expected_observed_regime": expected_observed,
        "match": observed == expected_observed,
        "D_equals_N_violation": d_equals_n_violation,
        "below_threshold_violation": below_threshold_violation,
        "above_threshold_violation": above_threshold_violation,
        "SEP_Omega_violation": abs(sep_omega_gap) > TOL,
        "full_relabeling_pass": full_relabeling_pass,
        "future_pair_pass": future_pair_pass,
    }


def _phase_summary(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    predicted = Counter(str(row["predicted_regime"]) for row in rows)
    observed = Counter(str(row["observed_regime"]) for row in rows)
    mismatches = [str(row["configuration_id"]) for row in rows if not row["match"]]
    omega_violations = [
        str(row["configuration_id"]) for row in rows if row["SEP_Omega_violation"]
    ]
    relabeling_violations = [
        str(row["configuration_id"]) for row in rows if not row["full_relabeling_pass"]
    ]
    future_pair_violations = [
        str(row["configuration_id"]) for row in rows if not row["future_pair_pass"]
    ]
    development = Counter(str(row["development_category"]) for row in rows)
    terminal_best = Counter(str(row["initial_terminal_best_category"]) for row in rows)
    by_recipient: dict[str, dict[str, int]] = {}
    for category in ("null", "M1", "M2", "ties"):
        category_rows = [row for row in rows if row["development_category"] == category]
        by_recipient[category] = {
            "strict_advantage": sum(
                row["observed_regime"] == STRICT_ADVANTAGE for row in category_rows
            ),
            "no_advantage": sum(
                row["observed_regime"] != STRICT_ADVANTAGE for row in category_rows
            ),
        }
    return {
        "n_configurations": len(rows),
        "predicted": {
            LESS: predicted[LESS],
            BOUNDARY: predicted[BOUNDARY],
            GREATER: predicted[GREATER],
            IMMEDIATE_TIE: predicted[IMMEDIATE_TIE],
        },
        "observed": {
            NEGATIVE_UNEXPECTED: observed[NEGATIVE_UNEXPECTED],
            NO_ADVANTAGE: observed[NO_ADVANTAGE],
            STRICT_ADVANTAGE: observed[STRICT_ADVANTAGE],
        },
        "immediate_ties": sum(bool(row["immediate_tie"]) for row in rows),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "D_equals_N_count": sum(abs(float(row["D_minus_N"])) <= TOL for row in rows),
        "D_equals_N_violation_count": sum(bool(row["D_equals_N_violation"]) for row in rows),
        "below_threshold_violation_count": sum(
            bool(row["below_threshold_violation"]) for row in rows
        ),
        "above_threshold_violation_count": sum(
            bool(row["above_threshold_violation"]) for row in rows
        ),
        "SEP_Omega_violation_count": len(omega_violations),
        "SEP_Omega_violations": omega_violations,
        "full_relabeling_violation_count": len(relabeling_violations),
        "full_relabeling_violations": relabeling_violations,
        "future_pair_violation_count": len(future_pair_violations),
        "future_pair_violations": future_pair_violations,
        "development_recipients": {
            "null": development["null"],
            "M1": development["M1"],
            "M2": development["M2"],
            "ties": development["ties"],
        },
        "strict_no_advantage_by_development_recipient": by_recipient,
        "initial_terminal_best": {
            "M1": terminal_best["M1"],
            "M2": terminal_best["M2"],
            "tie": terminal_best["tie"],
        },
    }


def aggregate(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    """Apply exactly the frozen A1c PASS/FAIL criteria."""
    by_phase = {
        phase: tuple(row for row in rows if row["phase"] == phase)
        for phase in (PHASE_1, PHASE_2)
    }
    phases = {phase: _phase_summary(values) for phase, values in by_phase.items()}
    count_match = {
        phase: len(by_phase[phase]) == expected
        for phase, expected in EXPECTED_COUNTS.items()
    }
    mismatch_count = sum(int(value["mismatch_count"]) for value in phases.values())
    d_equals_n_violations = sum(
        int(value["D_equals_N_violation_count"]) for value in phases.values()
    )
    below_violations = sum(
        int(value["below_threshold_violation_count"]) for value in phases.values()
    )
    above_violations = sum(
        int(value["above_threshold_violation_count"]) for value in phases.values()
    )
    omega_violations = sum(
        int(value["SEP_Omega_violation_count"]) for value in phases.values()
    )
    relabeling_violations = sum(
        int(value["full_relabeling_violation_count"]) for value in phases.values()
    )
    future_pair_violations = sum(
        int(value["future_pair_violation_count"]) for value in phases.values()
    )
    phase_2_development = phases[PHASE_2]["development_recipients"]
    phase_2_terminal = phases[PHASE_2]["initial_terminal_best"]
    required_development_coverage = all(
        int(phase_2_development[key]) > 0 for key in ("null", "M1", "M2", "ties")
    )
    required_terminal_coverage = all(
        int(phase_2_terminal[key]) > 0 for key in ("M1", "M2", "tie")
    )
    passed = (
        len(rows) == sum(EXPECTED_COUNTS.values())
        and all(count_match.values())
        and mismatch_count == 0
        and d_equals_n_violations == 0
        and below_violations == 0
        and above_violations == 0
        and omega_violations == 0
        and relabeling_violations == 0
        and future_pair_violations == 0
        and required_development_coverage
        and required_terminal_coverage
    )
    return {
        "experiment_id": "A1c",
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "deterministic": True,
        "seeds": [],
        "tolerance": TOL,
        "conservative_metric": "J_HLS-J_SEP_max",
        "expected_counts": EXPECTED_COUNTS,
        "effective_counts": {phase: len(values) for phase, values in by_phase.items()},
        "total_configurations": len(rows),
        "count_match": count_match,
        "mismatch_count": mismatch_count,
        "D_equals_N_violation_count": d_equals_n_violations,
        "below_threshold_violation_count": below_violations,
        "above_threshold_violation_count": above_violations,
        "SEP_Omega_violation_count": omega_violations,
        "full_relabeling_violation_count": relabeling_violations,
        "future_pair_violation_count": future_pair_violations,
        "required_development_coverage": required_development_coverage,
        "required_terminal_best_coverage": required_terminal_coverage,
        "phases": phases,
        "interpretation": (
            "Controlled competence-geometry phase-structure agreement in the "
            "minimal modeled family; not empirical validation of RQ0."
        ),
    }


def run_sweep() -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    """Evaluate all 458 configurations deterministically and aggregate them."""
    rows = tuple(evaluate_configuration(configuration) for configuration in all_configurations())
    return rows, aggregate(rows)


def configuration_key(row: Mapping[str, object]) -> tuple[object, ...]:
    """Return the complete pre-registered configuration identity."""
    return (
        row["phase"],
        row["c_11"],
        row["c_12"],
        row["c_21"],
        row["c_22"],
    )
