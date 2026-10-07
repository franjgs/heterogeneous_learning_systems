"""Mathematical and conceptual controls for production-surface distance."""

from itertools import product

import pytest

from hls.problem_geometry import (
    change_magnitudes,
    historical_novelties,
    numerical_production_supremum,
    problem_from_p,
    production_distance,
    representational_mismatches,
    validate_problem,
)


GRID = tuple(index / 20 for index in range(21))
FINE_GRID = tuple(index / 40 for index in range(41))
HYPOTHESES = tuple(problem_from_p(p) for p in (0.8, 0.5, 0.2))


def test_problem_validation_and_construction_do_not_normalize_invalid_inputs():
    assert problem_from_p(0.63) == (0.63, 0.37)
    assert validate_problem((0.25, 0.75)) == (0.25, 0.75)
    for p in (-0.01, 1.01, float("inf"), float("nan")):
        with pytest.raises(ValueError):
            problem_from_p(p)
    for problem in ((0.6, 0.5), (-0.1, 1.1), (float("nan"), 0.0), (1.0,)):
        with pytest.raises(ValueError):
            validate_problem(problem)


def test_closed_form_known_values_and_equal_parameter_displacement_diagnostic():
    assert production_distance(0.8, 0.7) == pytest.approx(0.15, abs=1e-15)
    assert production_distance(0.5, 0.4) == pytest.approx(0.11, abs=1e-15)
    assert abs(0.8 - 0.7) == pytest.approx(abs(0.5 - 0.4))
    assert production_distance(0.8, 0.7) != pytest.approx(production_distance(0.5, 0.4))
    assert production_distance(0.0, 1.0) == 1.0


def test_nonnegativity_identity_symmetry_normalization_and_injectivity():
    for p, q in product(GRID, repeat=2):
        distance = production_distance(p, q)
        assert 0.0 <= distance <= 1.0 + 1e-15
        assert production_distance(p, q) == production_distance(q, p)
        assert (distance == 0.0) is (p == q)
        if p != q:
            # The pure capability-1 endpoint gives R_p(3,0)=3p^2.
            assert 3.0 * p**2 != 3.0 * q**2


def test_capability_exchange_symmetry():
    for p, q in product(GRID, repeat=2):
        assert production_distance(p, q) == pytest.approx(
            production_distance(1.0 - p, 1.0 - q), abs=3e-16
        )


def test_triangle_inequality_on_broad_deterministic_grid():
    for p, q, r in product(FINE_GRID, repeat=3):
        assert production_distance(p, r) <= (
            production_distance(p, q) + production_distance(q, r) + 2e-15
        )


def test_independent_full_envelope_supremum_matches_closed_form_and_pure_endpoints():
    validation_grid = (0.0, 0.01, 0.1, 0.2, 0.4, 0.49, 0.5, 0.51, 0.6, 0.8, 0.9, 0.99, 1.0)
    for p, q in product(validation_grid, repeat=2):
        numerical = numerical_production_supremum(p, q, resolution=120)
        assert numerical.distance == pytest.approx(production_distance(p, q), abs=8e-15)
        if p != q:
            assert numerical.output in ((0.0, 3.0), (3.0, 0.0))
            if p + q > 1.0:
                assert numerical.output == (3.0, 0.0)
            elif p + q < 1.0:
                assert numerical.output == (0.0, 3.0)


def test_first_problem_change_and_novelty_are_explicitly_missing():
    sequence = (problem_from_p(0.8), problem_from_p(0.5))
    assert change_magnitudes(sequence)[0] is None
    assert historical_novelties(sequence)[0] is None
    assert representational_mismatches(sequence, HYPOTHESES)[0] == 0.0
    assert change_magnitudes(()) == historical_novelties(()) == ()


def test_exact_recurrence_has_zero_novelty_but_positive_current_change():
    a, b = problem_from_p(0.8), problem_from_p(0.2)
    sequence = (a, b, a)
    change = change_magnitudes(sequence)
    novelty = historical_novelties(sequence)
    assert novelty[-1] == 0.0
    assert change[-1] == production_distance(a, b) > 0.0


def test_historically_novel_problem_can_be_exactly_represented():
    sequence = (problem_from_p(0.8), problem_from_p(0.5))
    assert historical_novelties(sequence)[-1] > 0.0
    assert representational_mismatches(sequence, HYPOTHESES)[-1] == 0.0


def test_historically_novel_problem_can_be_unrepresented():
    sequence = (problem_from_p(0.8), problem_from_p(0.63))
    assert historical_novelties(sequence)[-1] > 0.0
    assert representational_mismatches(sequence, HYPOTHESES)[-1] > 0.0


def test_recurrent_problem_can_remain_representationally_mismatched():
    unrepresented = problem_from_p(0.63)
    sequence = (unrepresented, problem_from_p(0.8), unrepresented)
    assert historical_novelties(sequence)[-1] == 0.0
    assert representational_mismatches(sequence, HYPOTHESES)[-1] > 0.0
    assert change_magnitudes(sequence)[-1] > 0.0


def test_empty_hypothesis_repertoire_is_invalid_for_mismatch():
    with pytest.raises(ValueError):
        representational_mismatches((problem_from_p(0.5),), ())
