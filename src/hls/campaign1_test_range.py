"""Frozen, team-free Campaign 1 test-range fixture.

This module contains problem histories and geometry only.  It does not import
or execute a team controller, production campaign, or performance analysis.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .problem_geometry import (
    Problem,
    change_magnitudes,
    historical_novelties,
    production_distance,
    representational_mismatches,
    validate_problem,
)
from .small_problem_world import HORIZON, HYPOTHESIS_REPERTOIRE


POINTS_P = {"A": 0.8, "U": 0.7, "C": 0.5, "V": 0.3, "B": 0.2}
# Literal decimal tuples preserve exact membership in the already frozen Z_hat;
# problem_from_p(.8) would contain the benign float complement .199999... .
POINTS: dict[str, Problem] = {
    "A": validate_problem((0.8, 0.2)),
    "U": validate_problem((0.7, 0.3)),
    "C": validate_problem((0.5, 0.5)),
    "V": validate_problem((0.3, 0.7)),
    "B": validate_problem((0.2, 0.8)),
}

HISTORY_LABELS: dict[str, tuple[str, ...]] = {
    "TR-PR": ("A", "A", "A", "A", "A", "A"),
    "TR-PM": ("U", "U", "U", "U", "U", "U"),
    "TR-G": ("A", "U", "C", "V", "B", "A"),
    "TR-J": ("A", "B", "V", "C", "U", "A"),
    "TR-R": ("A", "U", "A", "U", "A", "A"),
    "TR-D": ("A", "U", "C", "V", "B", "B"),
    "TR-HA": ("A", "U", "C", "B", "V", "A"),
    "TR-HB": ("A", "V", "B", "C", "U", "A"),
}
HISTORIES: dict[str, tuple[Problem, ...]] = {
    identifier: tuple(POINTS[label] for label in labels)
    for identifier, labels in HISTORY_LABELS.items()
}

INTENDED_CONTRASTS = {
    "persistence_representation": ("TR-PR", "TR-PM"),
    "ordered_displacement": ("TR-G", "TR-J"),
    "recurrence_displacement": ("TR-R", "TR-D"),
    "developmental_history_return": ("TR-HA", "TR-HB"),
}
FUTURE_PROBE_CONFIGURATIONS = ("G00", "G04", "G05", "G07")
FUTURE_PRIMARY_CONDITION = "DISCOVER_DEVELOP"
FUTURE_ETA = 0.35
TEAM_EXECUTIONS = 0

# This is provenance, not a performance covariate.
CONTAMINATION_STATUS = {
    "TR-PR": "PRIOR-DIAGNOSTIC / NOT OUT-OF-SAMPLE: identical to Campaign 0 H2",
    "TR-PM": "PRE-PERFORMANCE CAMPAIGN-1 SCENARIO",
    "TR-G": "PRIOR-DIAGNOSTIC / NOT OUT-OF-SAMPLE: new ordering of Campaign 0 H0/H1 problem multiset",
    "TR-J": "PRIOR-DIAGNOSTIC / NOT OUT-OF-SAMPLE: new ordering of Campaign 0 H0/H1 problem multiset",
    "TR-R": "PRIOR-DIAGNOSTIC / NOT OUT-OF-SAMPLE: recurrence analogue of Campaign 0 H3 using U instead of B",
    "TR-D": "PRE-PERFORMANCE CAMPAIGN-1 SCENARIO",
    "TR-HA": "PRIOR-DIAGNOSTIC / NOT OUT-OF-SAMPLE: new ordering of Campaign 0 H0/H1 problem multiset",
    "TR-HB": "PRIOR-DIAGNOSTIC / NOT OUT-OF-SAMPLE: new ordering of Campaign 0 H0/H1 problem multiset",
}


@dataclass(frozen=True)
class TestRangeStep:
    scenario_id: str
    step: int
    label: str
    problem: Problem
    change: float | None
    novelty: float | None
    mismatch: float
    represented: bool
    exact_recurrence: bool


def pairwise_distance_matrix() -> tuple[tuple[float, ...], ...]:
    return tuple(
        tuple(production_distance(POINTS[left], POINTS[right]) for right in POINTS)
        for left in POINTS
    )


def history_steps(scenario_id: str) -> tuple[TestRangeStep, ...]:
    sequence = HISTORIES[scenario_id]
    changes = change_magnitudes(sequence)
    novelties = historical_novelties(sequence)
    mismatches = representational_mismatches(sequence, HYPOTHESIS_REPERTOIRE)
    return tuple(
        TestRangeStep(
            scenario_id=scenario_id,
            step=index + 1,
            label=HISTORY_LABELS[scenario_id][index],
            problem=problem,
            change=changes[index],
            novelty=novelties[index],
            mismatch=mismatches[index],
            represented=problem in HYPOTHESIS_REPERTOIRE,
            exact_recurrence=problem in sequence[:index],
        )
        for index, problem in enumerate(sequence)
    )


def problem_multiset(scenario_id: str) -> tuple[tuple[str, int], ...]:
    counts = Counter(HISTORY_LABELS[scenario_id])
    return tuple((label, counts[label]) for label in POINTS if counts[label])


def transition_multiset(scenario_id: str) -> tuple[float, ...]:
    return tuple(sorted(step.change for step in history_steps(scenario_id)[1:] if step.change is not None))


def recurrence_locations(scenario_id: str) -> tuple[int, ...]:
    return tuple(step.step for step in history_steps(scenario_id) if step.exact_recurrence)


def validate_test_range() -> None:
    if tuple(POINTS) != ("A", "U", "C", "V", "B"):
        raise AssertionError("problem-point order changed")
    if tuple(HISTORIES) != ("TR-PR", "TR-PM", "TR-G", "TR-J", "TR-R", "TR-D", "TR-HA", "TR-HB"):
        raise AssertionError("test-range scenario order changed")
    if any(len(sequence) != 6 for sequence in HISTORIES.values()):
        raise AssertionError("every test-range history must have six problems")
    if HYPOTHESIS_REPERTOIRE != (POINTS["A"], POINTS["C"], POINTS["B"]):
        raise AssertionError("frozen finite hypothesis repertoire changed")
    if HORIZON != 3 or TEAM_EXECUTIONS != 0:
        raise AssertionError("frozen horizon or no-execution invariant changed")
