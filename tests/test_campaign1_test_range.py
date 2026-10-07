"""Pre-results geometry controls for the Campaign 1 test range."""

from collections import Counter
from itertools import combinations
import csv
import json
from pathlib import Path

import pytest

from hls.campaign1_test_range import (
    CONTAMINATION_STATUS,
    FUTURE_ETA,
    FUTURE_PROBE_CONFIGURATIONS,
    HISTORIES,
    HISTORY_LABELS,
    INTENDED_CONTRASTS,
    POINTS,
    POINTS_P,
    TEAM_EXECUTIONS,
    history_steps,
    pairwise_distance_matrix,
    problem_multiset,
    recurrence_locations,
    transition_multiset,
    validate_test_range,
)
from hls.problem_geometry import production_distance


EXPECTED = {
    "TR-PR": (0.8, 0.8, 0.8, 0.8, 0.8, 0.8),
    "TR-PM": (0.7, 0.7, 0.7, 0.7, 0.7, 0.7),
    "TR-G": (0.8, 0.7, 0.5, 0.3, 0.2, 0.8),
    "TR-J": (0.8, 0.2, 0.3, 0.5, 0.7, 0.8),
    "TR-R": (0.8, 0.7, 0.8, 0.7, 0.8, 0.8),
    "TR-D": (0.8, 0.7, 0.5, 0.3, 0.2, 0.2),
    "TR-HA": (0.8, 0.7, 0.5, 0.2, 0.3, 0.8),
    "TR-HB": (0.8, 0.3, 0.2, 0.5, 0.7, 0.8),
}


def test_exact_points_histories_and_no_team_execution():
    validate_test_range()
    assert POINTS_P == {"A": 0.8, "U": 0.7, "C": 0.5, "V": 0.3, "B": 0.2}
    assert {key: tuple(p[0] for p in value) for key, value in HISTORIES.items()} == EXPECTED
    assert TEAM_EXECUTIONS == 0
    assert FUTURE_PROBE_CONFIGURATIONS == ("G00", "G04", "G05", "G07")
    assert FUTURE_ETA == 0.35


def test_pairwise_distance_matrix_is_exactly_the_proposed_geometry():
    expected = (
        (0, .15, .39, .55, .60),
        (.15, 0, .24, .40, .55),
        (.39, .24, 0, .24, .39),
        (.55, .40, .24, 0, .15),
        (.60, .55, .39, .15, 0),
    )
    for actual_row, expected_row in zip(pairwise_distance_matrix(), expected):
        assert actual_row == pytest.approx(expected_row, abs=2e-15)


def test_persistence_representation_contrast():
    left, right = INTENDED_CONTRASTS["persistence_representation"]
    assert all(step.change == 0 for step in history_steps(left)[1:] + history_steps(right)[1:])
    assert all(step.mismatch == 0 and step.represented for step in history_steps(left))
    assert all(step.mismatch == pytest.approx(.15) and not step.represented for step in history_steps(right))


def test_gradual_jump_pair_controls_content_and_transition_multiset():
    left, right = INTENDED_CONTRASTS["ordered_displacement"]
    assert problem_multiset(left) == problem_multiset(right) == (("A", 2), ("U", 1), ("C", 1), ("V", 1), ("B", 1))
    assert tuple(s.change for s in history_steps(left)[1:]) == pytest.approx((.15, .24, .24, .15, .60))
    assert tuple(s.change for s in history_steps(right)[1:]) == pytest.approx((.60, .15, .24, .24, .15))
    assert transition_multiset(left) == pytest.approx(transition_multiset(right))
    assert HISTORY_LABELS[right] == tuple(reversed(HISTORY_LABELS[left]))


def test_recurrence_displacement_pair_is_not_a_matched_change_control():
    recurrent, displacement = INTENDED_CONTRASTS["recurrence_displacement"]
    assert recurrence_locations(recurrent) == (3, 4, 5, 6)
    assert recurrence_locations(displacement) == (6,)
    assert sum(s.change for s in history_steps(recurrent)[1:]) == pytest.approx(.60)
    assert sum(s.change for s in history_steps(displacement)[1:]) == pytest.approx(.78)
    assert transition_multiset(recurrent) != transition_multiset(displacement)


def test_developmental_history_return_pair_is_content_matched_and_recurrent():
    left, right = INTENDED_CONTRASTS["developmental_history_return"]
    assert problem_multiset(left) == problem_multiset(right) == (("A", 2), ("U", 1), ("C", 1), ("V", 1), ("B", 1))
    assert HISTORY_LABELS[right] == tuple(reversed(HISTORY_LABELS[left]))
    assert transition_multiset(left) == pytest.approx(transition_multiset(right))
    for scenario in (left, right):
        final = history_steps(scenario)[-1]
        assert final.label == "A" and final.novelty == 0 and final.mismatch == 0
        assert recurrence_locations(scenario) == (6,)


def test_representation_and_recurrence_are_derived_not_hard_coded():
    for scenario in HISTORIES:
        steps = history_steps(scenario)
        for index, step in enumerate(steps):
            assert step.represented is (step.problem in (POINTS["A"], POINTS["C"], POINTS["B"]))
            assert step.exact_recurrence is (step.problem in tuple(s.problem for s in steps[:index]))


def test_no_two_histories_are_exactly_equal_or_full_descriptor_duplicates():
    signatures = {}
    for scenario in HISTORIES:
        steps = history_steps(scenario)
        signature = tuple((s.label, s.change, s.novelty, s.mismatch, s.represented, s.exact_recurrence) for s in steps)
        assert signature not in signatures
        signatures[signature] = scenario
    assert len({HISTORIES[key] for key in HISTORIES}) == 8


def test_capability_exchange_symmetry_holds_for_declared_points():
    exchange = {"A": "B", "U": "V", "C": "C", "V": "U", "B": "A"}
    for left, right in combinations(POINTS, 2):
        assert production_distance(POINTS[left], POINTS[right]) == pytest.approx(
            production_distance(POINTS[exchange[left]], POINTS[exchange[right]])
        )


def test_contamination_status_is_explicit_and_not_performance_based():
    assert "identical to Campaign 0 H2" in CONTAMINATION_STATUS["TR-PR"]
    assert CONTAMINATION_STATUS["TR-PM"] == "PRE-PERFORMANCE CAMPAIGN-1 SCENARIO"
    assert CONTAMINATION_STATUS["TR-D"] == "PRE-PERFORMANCE CAMPAIGN-1 SCENARIO"
    assert all("winner" not in value.lower() and "outperformed" not in value.lower() for value in CONTAMINATION_STATUS.values())


def test_campaign0_contamination_classification_uses_sequences_only():
    campaign0_h0 = (0.8, 0.7, 0.3, 0.2, 0.5, 0.8)
    campaign0_h1 = (0.8, 0.2, 0.3, 0.7, 0.5, 0.8)
    campaign0_h2 = (0.8,) * 6
    campaign0_h3 = (0.8, 0.2, 0.8, 0.2, 0.8, 0.8)
    assert EXPECTED["TR-PR"] == campaign0_h2
    content_matched = ("TR-G", "TR-J", "TR-HA", "TR-HB")
    assert all(Counter(EXPECTED[key]) == Counter(campaign0_h0) == Counter(campaign0_h1) for key in content_matched)
    assert EXPECTED["TR-R"] == tuple(0.7 if p == 0.2 else p for p in campaign0_h3)
    assert EXPECTED["TR-PM"] not in (campaign0_h0, campaign0_h1, campaign0_h2, campaign0_h3)
    assert EXPECTED["TR-D"] not in (campaign0_h0, campaign0_h1, campaign0_h2, campaign0_h3)


def test_materialized_gate_manifest_has_zero_team_execution_and_all_descriptors():
    out = Path("results/foundations/campaign1_test_range_gate")
    manifest = json.loads((out / "pre_experiment_manifest.json").read_text())
    assert manifest["team_executions"] == 0
    assert manifest["campaign1_performance_artifacts"] == 0
    assert manifest["selection_basis"].startswith("problem geometry only")
    assert tuple(manifest["future_probe_configurations"]) == FUTURE_PROBE_CONFIGURATIONS
    assert set(manifest["descriptors"]) == set(HISTORIES)
    assert all(len(rows) == 6 for rows in manifest["descriptors"].values())
    with (out / "history_steps.csv").open() as handle:
        assert sum(1 for _ in csv.DictReader(handle)) == 48
    with (out / "histories.csv").open() as handle:
        assert sum(1 for _ in csv.DictReader(handle)) == 8
