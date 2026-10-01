"""Deterministic Phase-V validation of the minimal adaptive reference scenario.

This module is deliberately a fixed validation family, not a general sweep
framework.  Every ``L`` and ``G`` reported here is derived by evaluating a
``MinimalReferenceScenario``; neither is a primitive parameter.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from functools import lru_cache
from itertools import product
from math import isfinite
from typing import Iterable

from .minimal_reference_scenario import (
    EXACT_TOL,
    LearningRule,
    MinimalReferenceScenario,
    ScenarioEvaluation,
    identity_residual,
    reference_configurations,
)


CLASS_TOL = 1e-12
LOCAL_PERTURBATION = 0.01
LOCAL_REPLICATES_PER_REGIME = 5
BOUNDARY_PROBES = 20

# Primitive grid: state heterogeneity, present/future demand, common learning
# intensity, and future weight.  L and G are intentionally absent.
A1_VALUES = (0.50, 0.60, 0.70, 0.80)
A2_VALUES = (0.45, 0.55, 0.65, 0.75)
B1_VALUES = (0.20, 0.30, 0.40, 0.50)
B2_VALUES = (0.30, 0.40, 0.50, 0.60)
PRESENT_A_VALUES = (0.20, 0.35, 0.50, 0.65, 0.80)
FUTURE_A_VALUES = (0.00, 0.25, 0.50, 0.75, 1.00)
LEARNING_SCALES = (0.50, 1.00, 1.50, 2.00)
BETA_VALUES = (0.00, 0.125, 0.25, 0.375, 0.50, 0.625, 0.75, 0.875, 1.00)


@dataclass(frozen=True)
class PrimitiveWorld:
    """The primitive quantities varied by the fixed Phase-V family."""

    a1: float
    a2: float
    b1: float
    b2: float
    present_a: float
    future_a: float
    learning_scale: float
    beta: float
    learning_rule: LearningRule = LearningRule.DIMINISHING

    def scenario(self) -> MinimalReferenceScenario:
        return MinimalReferenceScenario(
            state_0=((self.a1, self.b1), (self.a2, self.b2)),
            demand_0=(self.present_a, 1.0 - self.present_a),
            demand_1=(self.future_a, 1.0 - self.future_a),
            beta=self.beta,
            learning_rule=self.learning_rule,
            learning_scale=self.learning_scale,
        )


@dataclass(frozen=True)
class ValidationRow:
    """One evaluated world and its derived regime quantities."""

    primitive: PrimitiveWorld
    loss: float
    gain: float
    beta_gain: float
    delta_j: float
    identity_residual: float
    regime: str
    state_diverges: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "a1": self.primitive.a1,
            "a2": self.primitive.a2,
            "b1": self.primitive.b1,
            "b2": self.primitive.b2,
            "present_A": self.primitive.present_a,
            "future_A": self.primitive.future_a,
            "demand_shift_A": self.primitive.future_a - self.primitive.present_a,
            "learning_scale": self.primitive.learning_scale,
            "beta": self.primitive.beta,
            "learning_rule": self.primitive.learning_rule.value,
            "L": self.loss,
            "G": self.gain,
            "beta_G": self.beta_gain,
            "Delta_J": self.delta_j,
            "identity_residual": self.identity_residual,
            "state_diverges": self.state_diverges,
            "regime": self.regime,
        }


@lru_cache(maxsize=1)
def primary_primitives() -> tuple[PrimitiveWorld, ...]:
    """Return the fixed changing-demand primitive grid before L-positive filtering."""
    return tuple(
        PrimitiveWorld(a1, a2, b1, b2, present_a, future_a, scale, beta)
        for a1, a2, b1, b2, present_a, future_a, scale, beta in product(
            A1_VALUES,
            A2_VALUES,
            B1_VALUES,
            B2_VALUES,
            PRESENT_A_VALUES,
            FUTURE_A_VALUES,
            LEARNING_SCALES,
            BETA_VALUES,
        )
        if future_a != present_a
    )


def classify(loss: float, gain: float, beta: float) -> str:
    """Classify one world only within the documented strict-L comparison domain."""
    if loss <= CLASS_TOL:
        return "outside_strict_present_exploitation_domain"
    margin = beta * gain - loss
    if abs(margin) <= CLASS_TOL:
        return "boundary"
    if margin > CLASS_TOL:
        return "S3_decision_relevant"
    if gain > CLASS_TOL:
        return "S2_positive_G_no_reversal"
    return "present_exploitation_nonpositive_G"


def evaluate_primitive(primitive: PrimitiveWorld) -> ValidationRow:
    """Evaluate a primitive world, deriving all reported comparison quantities."""
    scenario = primitive.scenario()
    evaluation = scenario.evaluate()
    return ValidationRow(
        primitive=primitive,
        loss=evaluation.loss,
        gain=evaluation.gain,
        beta_gain=primitive.beta * evaluation.gain,
        delta_j=evaluation.total_difference,
        identity_residual=identity_residual(scenario),
        regime=classify(evaluation.loss, evaluation.gain, primitive.beta),
        state_diverges=evaluation.state_e != evaluation.state_d,
    )


def evaluate_primitives(primitives: Iterable[PrimitiveWorld]) -> tuple[ValidationRow, ...]:
    return tuple(evaluate_primitive(primitive) for primitive in primitives)


def _counts(rows: Iterable[ValidationRow]) -> dict[str, int]:
    return dict(sorted(Counter(row.regime for row in rows).items()))


def _conditional_counts(rows: Iterable[ValidationRow], key: str) -> dict[str, dict[str, int]]:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        if key == "learning_scale":
            label = f"{row.primitive.learning_scale:.2f}"
        elif key == "future_A":
            label = f"{row.primitive.future_a:.2f}"
        else:
            raise ValueError(f"unknown grouping key: {key}")
        groups[label][row.regime] += 1
    return {label: dict(sorted(counts.items())) for label, counts in sorted(groups.items())}


def _summary(rows: tuple[ValidationRow, ...], input_count: int) -> dict[str, object]:
    eligible = tuple(row for row in rows if row.loss > CLASS_TOL)
    return {
        "input_worlds": input_count,
        "regime_eligible_worlds": len(eligible),
        "excluded_nonpositive_L": input_count - len(eligible),
        "regime_counts": _counts(eligible),
        "all_classification_counts": _counts(rows),
        "positive_S2_region": any(row.regime == "S2_positive_G_no_reversal" for row in eligible),
        "positive_S3_region": any(row.regime == "S3_decision_relevant" for row in eligible),
        "maximum_absolute_identity_residual": max(
            (abs(row.identity_residual) for row in rows), default=0.0
        ),
        "counts_by_learning_scale": _conditional_counts(eligible, "learning_scale"),
        "counts_by_future_A": _conditional_counts(eligible, "future_A"),
    }


def _stationary_primitives() -> tuple[PrimitiveWorld, ...]:
    return tuple(
        PrimitiveWorld(a1, a2, b1, b2, present_a, present_a, scale, beta)
        for a1, a2, b1, b2, present_a, scale, beta in product(
            A1_VALUES,
            A2_VALUES,
            B1_VALUES,
            B2_VALUES,
            PRESENT_A_VALUES,
            LEARNING_SCALES,
            BETA_VALUES,
        )
    )


def _recipient_neutral_primitives() -> tuple[PrimitiveWorld, ...]:
    """Keep LBD but equalize B recipients in a B-only future-demand control."""
    return tuple(
        PrimitiveWorld(a1, a2, b, b, present_a, 0.0, scale, beta, LearningRule.HOMOGENEOUS_LINEAR)
        for a1, a2, b, present_a, scale, beta in product(
            A1_VALUES,
            A2_VALUES,
            B2_VALUES,
            PRESENT_A_VALUES,
            LEARNING_SCALES,
            BETA_VALUES,
        )
    )


def _no_evolution_primitives() -> tuple[PrimitiveWorld, ...]:
    return tuple(replace(primitive, learning_rule=LearningRule.NONE) for primitive in primary_primitives())


def _relaxed_terminal_value(state: tuple[tuple[float, float], tuple[float, float]], demand: tuple[float, float]) -> float:
    """Capacity-relaxed terminal comparator; not an alternative HLS theory."""
    return sum(demand[task] * max(state[0][task], state[1][task]) for task in (0, 1))


def _evaluate_capacity_relaxed(primitive: PrimitiveWorld) -> ValidationRow:
    scenario = primitive.scenario()
    evaluation = scenario.evaluate()
    value_e = _relaxed_terminal_value(evaluation.state_e, scenario.demand_1)
    value_d = _relaxed_terminal_value(evaluation.state_d, scenario.demand_1)
    gain = value_d - value_e
    delta_j = (evaluation.reward_d + primitive.beta * value_d) - (
        evaluation.reward_e + primitive.beta * value_e
    )
    return ValidationRow(
        primitive=primitive,
        loss=evaluation.loss,
        gain=gain,
        beta_gain=primitive.beta * gain,
        delta_j=delta_j,
        identity_residual=delta_j - (-evaluation.loss + primitive.beta * gain),
        regime=classify(evaluation.loss, gain, primitive.beta),
        state_diverges=evaluation.state_e != evaluation.state_d,
    )


def ablations() -> dict[str, dict[str, object]]:
    """Evaluate construction-scoped structural ablations and the audited null."""
    no_evolution = evaluate_primitives(_no_evolution_primitives())
    recipient_neutral = evaluate_primitives(_recipient_neutral_primitives())
    stationary = evaluate_primitives(_stationary_primitives())
    capacity_relaxed = tuple(_evaluate_capacity_relaxed(item) for item in primary_primitives())
    linear_control = reference_configurations()["negative_homogeneous_linear"]
    linear_evaluation = linear_control.evaluate()

    def record(rows: tuple[ValidationRow, ...], *, note: str) -> dict[str, object]:
        summary = _summary(rows, len(rows))
        return {
            "worlds": len(rows),
            "regime_eligible_worlds": summary["regime_eligible_worlds"],
            "regime_counts": summary["regime_counts"],
            "max_abs_G": max((abs(row.gain) for row in rows), default=0.0),
            "max_abs_Delta_J_identity_residual": summary["maximum_absolute_identity_residual"],
            "note": note,
        }

    return {
        "no_competence_evolution": record(
            no_evolution,
            note="Within this family, removing action-induced evolution makes G=0 and eliminates S2/S3.",
        ),
        "recipient_neutral_B_control": record(
            recipient_neutral,
            note="Within this equal-B, B-only-future construction, homogeneous linear LBD gives G=0 while LBD remains active.",
        ),
        "no_changing_demand": record(
            stationary,
            note="This stationary-demand ablation tests this construction only; changing demand is not a T4--T6 mathematical prerequisite.",
        ),
        "capacity_relaxed_terminal_comparator": record(
            capacity_relaxed,
            note="This relaxes only terminal one-worker/one-task capacity; it does not establish a universal necessity claim about capacity or distribution.",
        ),
        "audited_homogeneous_linear_control": {
            "G": linear_evaluation.gain,
            "Delta_J": linear_evaluation.total_difference,
            "identity_residual": identity_residual(linear_control),
            "note": "The documented audited construction has G=0; this does not generalize to every homogeneous-linear world.",
        },
    }


def boundary_probes(rows: Iterable[ValidationRow]) -> tuple[ValidationRow, ...]:
    """Derive exact beta=L/G probes without making G a primitive parameter."""
    probes = []
    for row in rows:
        if row.loss > CLASS_TOL and row.gain > CLASS_TOL:
            beta = row.loss / row.gain
            if 0.0 <= beta <= 1.0:
                probes.append(evaluate_primitive(replace(row.primitive, beta=beta)))
                if len(probes) == BOUNDARY_PROBES:
                    break
    return tuple(probes)


def _is_locally_interior(row: ValidationRow) -> bool:
    primitive = row.primitive
    return (
        all(0.10 < value < 0.90 for value in (primitive.a1, primitive.a2, primitive.b1, primitive.b2))
        and 0.10 < primitive.present_a < 0.90
        and 0.10 < primitive.future_a < 0.90
        and 0.10 < primitive.beta < 0.90
        and 0.10 < primitive.learning_scale < 2.00
    )


def _perturbations(primitive: PrimitiveWorld) -> tuple[PrimitiveWorld, ...]:
    names = ("a1", "a2", "b1", "b2", "present_a", "future_a", "learning_scale", "beta")
    candidates = []
    for name in names:
        for direction in (-1.0, 1.0):
            value = getattr(primitive, name) + direction * LOCAL_PERTURBATION
            upper = 1.0 if name not in {"learning_scale"} else float("inf")
            if 0.0 <= value <= upper:
                candidate = replace(primitive, **{name: value})
                if candidate.present_a != candidate.future_a:
                    candidates.append(candidate)
    return tuple(candidates)


def local_robustness(rows: Iterable[ValidationRow]) -> dict[str, object]:
    """Test small primitive perturbations of interior S2 and S3 worlds."""
    candidates: dict[str, list[ValidationRow]] = {"S2_positive_G_no_reversal": [], "S3_decision_relevant": []}
    for row in rows:
        if row.regime in candidates and _is_locally_interior(row):
            margin = abs(row.beta_gain - row.loss)
            if margin >= 0.02:
                candidates[row.regime].append(row)
    selected = {
        regime: sorted(group, key=lambda row: abs(row.beta_gain - row.loss), reverse=True)[:LOCAL_REPLICATES_PER_REGIME]
        for regime, group in candidates.items()
    }
    report: dict[str, object] = {}
    for regime, seeds in selected.items():
        perturbation_rows = [
            evaluate_primitive(perturbation)
            for seed in seeds
            for perturbation in _perturbations(seed.primitive)
        ]
        report[regime] = {
            "selection_rule": (
                "Interior worlds with absolute margin at least 0.02; select the five "
                "largest nominal absolute margins before evaluating any perturbation."
            ),
            "seeds": [
                {
                    "primitive": seed.as_dict(),
                    "nominal_absolute_margin": abs(seed.beta_gain - seed.loss),
                }
                for seed in seeds
            ],
            "seed_worlds": len(seeds),
            "perturbations": len(perturbation_rows),
            "same_regime": sum(row.regime == regime for row in perturbation_rows),
            "all_preserved": bool(perturbation_rows) and all(row.regime == regime for row in perturbation_rows),
            "minimum_margin": min((abs(row.beta_gain - row.loss) for row in perturbation_rows), default=None),
        }
    return report


@lru_cache(maxsize=1)
def run_validation() -> tuple[tuple[ValidationRow, ...], dict[str, object]]:
    """Run the fixed primary grid, derived boundary probes, ablations, and local checks."""
    primitives = primary_primitives()
    rows = evaluate_primitives(primitives)
    probes = boundary_probes(rows)
    summary = _summary(rows, len(primitives))
    summary["boundary_probes"] = {
        "count": len(probes),
        "all_classified_boundary": all(probe.regime == "boundary" for probe in probes),
        "maximum_absolute_Delta_J": max((abs(probe.delta_j) for probe in probes), default=0.0),
        "maximum_absolute_identity_residual": max((abs(probe.identity_residual) for probe in probes), default=0.0),
        "details": [probe.as_dict() for probe in probes],
    }
    summary["ablations"] = ablations()
    summary["local_robustness"] = local_robustness(rows)
    summary["counterexample_search"] = {
        "competence_change_without_positive_G": sum(row.state_diverges and row.gain <= CLASS_TOL for row in rows),
        "positive_G_without_decision_change": sum(row.regime == "S2_positive_G_no_reversal" for row in rows),
        "nearest_primary_grid_margin": min((abs(row.beta_gain - row.loss) for row in rows if row.loss > CLASS_TOL), default=None),
        "classification_contradictions": sum(
            (row.regime == "S3_decision_relevant" and row.delta_j <= CLASS_TOL)
            or (row.regime == "S2_positive_G_no_reversal" and row.delta_j >= -CLASS_TOL)
            for row in rows
        ),
    }
    return rows, summary
