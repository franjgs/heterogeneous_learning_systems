"""Controls for the frozen Small Problem World fixture."""

import pytest

from hls.problem_geometry import production_distance
from hls.small_problem_world import (
    A,
    A_PRIME,
    B,
    BELIEF_RESETS_EACH_PROBLEM,
    B_PRIME,
    C,
    HORIZON,
    HYPOTHESIS_REPERTOIRE,
    POSTERIOR_CARRIES_BETWEEN_PROBLEMS,
    STATE_PERSISTS_BETWEEN_PROBLEMS,
    UNIFORM_PRIOR,
    UNIQUE_WORLD_PROBLEMS,
    WORLD,
    pairwise_distance_matrix,
    validate_frozen_world,
    world_descriptors,
)


def test_exact_frozen_world_sequence_and_hypothesis_repertoire():
    assert tuple(stage.label for stage in WORLD) == ("A", "A'", "B", "B'", "C", "A")
    assert tuple(stage.problem for stage in WORLD) == (A, A_PRIME, B, B_PRIME, C, A)
    assert tuple(stage.problem[0] for stage in WORLD) == (0.8, 0.7, 0.3, 0.2, 0.5, 0.8)
    assert HYPOTHESIS_REPERTOIRE == ((0.8, 0.2), (0.5, 0.5), (0.2, 0.8))
    assert HORIZON == 3
    validate_frozen_world()


def test_expected_change_novelty_and_mismatch_trajectory():
    rows = world_descriptors()
    expected = (
        (None, None, 0.0),
        (0.15, 0.15, 0.15),
        (0.40, 0.40, 0.15),
        (0.15, 0.15, 0.0),
        (0.39, 0.24, 0.0),
        (0.39, 0.0, 0.0),
    )
    for row, (change, novelty, mismatch) in zip(rows, expected):
        assert row.change_magnitude == pytest.approx(change) if change is not None else row.change_magnitude is None
        assert row.historical_novelty == pytest.approx(novelty) if novelty is not None else row.historical_novelty is None
        assert row.representational_mismatch == pytest.approx(mismatch, abs=2e-16)


def test_symmetric_local_distances_and_unrepresented_mismatches():
    assert production_distance(A, A_PRIME) == pytest.approx(0.15)
    assert production_distance(B, B_PRIME) == pytest.approx(0.15)
    assert production_distance(A, A_PRIME) == pytest.approx(production_distance(B, B_PRIME))
    rows = world_descriptors()
    assert rows[1].representational_mismatch == pytest.approx(rows[2].representational_mismatch)
    assert rows[1].representational_mismatch == pytest.approx(0.15)


def test_representation_membership_controls():
    assert A in HYPOTHESIS_REPERTOIRE
    assert B_PRIME in HYPOTHESIS_REPERTOIRE
    assert C in HYPOTHESIS_REPERTOIRE
    assert A_PRIME not in HYPOTHESIS_REPERTOIRE
    assert B not in HYPOTHESIS_REPERTOIRE
    assert tuple(row.represented for row in world_descriptors()) == (True, False, False, True, True, True)


def test_c_is_historically_novel_but_exactly_represented():
    row = world_descriptors()[4]
    assert row.label == "C"
    assert row.historical_novelty == pytest.approx(0.24)
    assert row.representational_mismatch == 0.0
    assert row.represented


def test_final_a_is_exact_recurrence_after_nonzero_environmental_change():
    row = world_descriptors()[-1]
    assert row.problem == WORLD[0].problem
    assert row.historical_novelty == 0.0
    assert row.change_magnitude == pytest.approx(0.39)
    assert row.representational_mismatch == 0.0


def test_capability_exchange_symmetry_for_paired_problems():
    assert A_PRIME == tuple(reversed(B))
    assert A == tuple(reversed(B_PRIME))
    assert production_distance(A, A_PRIME) == pytest.approx(production_distance(B_PRIME, B))
    matrix = pairwise_distance_matrix()
    assert all(matrix[i][j] == pytest.approx(matrix[j][i]) for i in range(5) for j in range(5))
    assert tuple(stage.label for stage in UNIQUE_WORLD_PROBLEMS) == ("A", "A'", "B", "B'", "C")


def test_temporal_conventions_are_frozen_without_adding_state_or_execution():
    assert BELIEF_RESETS_EACH_PROBLEM
    assert UNIFORM_PRIOR == (1 / 3, 1 / 3, 1 / 3)
    assert not POSTERIOR_CARRIES_BETWEEN_PROBLEMS
    assert STATE_PERSISTS_BETWEEN_PROBLEMS
