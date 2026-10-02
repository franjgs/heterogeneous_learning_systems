"""Deterministic implementation controls for the fixed 3x2 G3 ground truth."""

import pytest

from hls.g3_organizational_value import (
    G3A_ASSIGNMENTS,
    G3B_ASSIGNMENTS,
    G3DUAL_ASSIGNMENTS,
    development_g3a_algebraic,
    development_g3a_direct,
    development_g3b_algebraic,
    development_g3b_direct,
    development_g3dual_algebraic,
    development_g3dual_direct,
    learning_increment,
    random_identity_audit,
    transition_g3a,
    transition_g3b,
    transition_g3dual,
    value_g3a_algebraic,
    value_g3a_direct,
    value_g3b_algebraic,
    value_g3b_direct,
    value_g3dual_algebraic,
    value_g3dual_direct,
)
from hls.minimal_reference_scenario import EXACT_TOL


STATES = (
    ((0.20, 0.90), (0.80, 0.10), (0.45, 0.55)),
    ((0.50, 0.10), (1.00, 0.50), (0.10, 1.00)),
    ((0.50, 0.10), (0.40, 0.50), (0.10, 0.40)),
    ((0.75, 0.75), (0.75, 0.75), (0.75, 0.75)),
    ((1.00, 0.00), (0.00, 1.00), (0.60, 0.60)),
)


def _permute(state, old_to_new):
    result = [None, None, None]
    for old, new in enumerate(old_to_new):
        result[new] = state[old]
    return tuple(result)


def _swap_competences(state):
    return tuple((row[1], row[0]) for row in state)


def test_assignment_enumerations_are_exact_and_fixed() -> None:
    assert G3A_ASSIGNMENTS == ((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1))
    assert G3B_ASSIGNMENTS == G3DUAL_ASSIGNMENTS == (0, 1, 2)


def test_terminal_operators_match_the_independent_algebraic_identities() -> None:
    for state in STATES:
        assert value_g3a_direct(state) == pytest.approx(value_g3a_algebraic(state), abs=EXACT_TOL)
        assert value_g3b_direct(state) == pytest.approx(value_g3b_algebraic(state), abs=EXACT_TOL)
        assert value_g3dual_direct(state) == pytest.approx(value_g3dual_algebraic(state), abs=EXACT_TOL)


def test_development_identities_hold_for_every_action_on_deterministic_states() -> None:
    for state in STATES:
        for scale in (0.0, 0.25, 2.0):
            for action in G3A_ASSIGNMENTS:
                assert development_g3a_direct(state, action, scale) == pytest.approx(development_g3a_algebraic(state, action, scale), abs=EXACT_TOL)
            for worker in G3B_ASSIGNMENTS:
                assert development_g3b_direct(state, worker, scale) == pytest.approx(development_g3b_algebraic(state, worker, scale), abs=EXACT_TOL)
                assert development_g3dual_direct(state, worker, scale) == pytest.approx(development_g3dual_algebraic(state, worker, scale), abs=EXACT_TOL)


def test_learning_updates_only_executed_competences_and_obeys_mis_saturation() -> None:
    state = ((0.50, 0.25), (0.75, 0.90), (0.10, 1.00))
    evolved = transition_g3a(state, (0, 1), 2.0)
    assert evolved[0][0] == pytest.approx(1.0)
    assert evolved[1][1] == pytest.approx(0.92)
    assert evolved[0][1] == state[0][1]
    assert evolved[1][0] == state[1][0]
    assert evolved[2] == state[2]
    assert learning_increment(1.0, 4.0) == 0.0
    for transition, action in ((transition_g3a, (0, 1)), (transition_g3b, 0), (transition_g3dual, 0)):
        assert transition(state, action, 0.0) == state


def test_worker_permutation_preserves_values_and_development() -> None:
    state = STATES[0]
    mapping = (2, 0, 1)
    permuted = _permute(state, mapping)
    assert value_g3a_direct(permuted) == pytest.approx(value_g3a_direct(state), abs=EXACT_TOL)
    assert value_g3b_direct(permuted) == pytest.approx(value_g3b_direct(state), abs=EXACT_TOL)
    assert value_g3dual_direct(permuted) == pytest.approx(value_g3dual_direct(state), abs=EXACT_TOL)
    for i, j in G3A_ASSIGNMENTS:
        assert development_g3a_direct(permuted, (mapping[i], mapping[j]), 0.4) == pytest.approx(development_g3a_direct(state, (i, j), 0.4), abs=EXACT_TOL)
    for worker in G3B_ASSIGNMENTS:
        assert development_g3b_direct(permuted, mapping[worker], 0.4) == pytest.approx(development_g3b_direct(state, worker, 0.4), abs=EXACT_TOL)
        assert development_g3dual_direct(permuted, mapping[worker], 0.4) == pytest.approx(development_g3dual_direct(state, worker, 0.4), abs=EXACT_TOL)


def test_a_b_exchange_maps_g3b_to_its_explicit_dual() -> None:
    state = STATES[0]
    swapped = _swap_competences(state)
    assert value_g3b_direct(state) == pytest.approx(value_g3dual_direct(swapped), abs=EXACT_TOL)
    for worker in G3B_ASSIGNMENTS:
        assert development_g3b_direct(state, worker, 0.4) == pytest.approx(development_g3dual_direct(swapped, worker, 0.4), abs=EXACT_TOL)


def test_degenerate_ties_zero_increment_saturation_and_assignment_crossing_are_stable() -> None:
    identical = ((0.5, 0.5), (0.5, 0.5), (0.5, 0.5))
    assert len({development_g3a_direct(identical, action, 0.5) for action in G3A_ASSIGNMENTS}) == 1
    saturated = ((1.0, 1.0), (1.0, 1.0), (1.0, 1.0))
    for action in G3A_ASSIGNMENTS:
        assert development_g3a_direct(saturated, action, 3.0) == pytest.approx(0.0, abs=EXACT_TOL)
    # A local increment crosses the best-assignment boundary; values remain continuous.
    state = ((0.49, 0.00), (0.50, 0.00), (0.00, 0.50))
    assert value_g3a_direct(state) == pytest.approx(1.0)
    evolved = transition_g3a(state, (0, 1), 1.0)
    assert evolved[0][0] > state[0][0]
    assert development_g3a_direct(state, (0, 1), 1.0) == pytest.approx(development_g3a_algebraic(state, (0, 1), 1.0), abs=EXACT_TOL)


def test_f1_f2_same_local_development_has_different_value_through_assignment_gaps() -> None:
    blocked = ((0.50, 0.10), (1.00, 0.50), (0.10, 1.00))
    exposed = ((0.50, 0.10), (0.40, 0.50), (0.10, 0.40))
    action = (0, 1)
    assert learning_increment(blocked[0][0], 0.5) == learning_increment(exposed[0][0], 0.5)
    assert learning_increment(blocked[1][1], 0.5) == learning_increment(exposed[1][1], 0.5)
    assert development_g3a_direct(blocked, action, 0.5) == pytest.approx(0.0, abs=EXACT_TOL)
    assert development_g3a_direct(exposed, action, 0.5) > 0.0


def test_f3_utilization_regime_changes_the_value_of_a_common_b_experience() -> None:
    state = ((0.50, 0.10), (0.40, 0.50), (0.10, 0.40))
    scale = 0.5
    # Worker 1's B experience is common; the operators differ by load regime.
    assert transition_g3a(state, (0, 1), scale)[1][1] == transition_g3b(state, 1, scale)[1][1]
    assert development_g3a_direct(state, (0, 1), scale) != pytest.approx(development_g3b_direct(state, 1, scale), abs=EXACT_TOL)


def test_f4_learning_amount_ranking_can_disagree_with_organizational_value_ranking() -> None:
    state = ((0.20, 0.90), (0.80, 0.10), (0.45, 0.55))
    scale = 0.5
    high_amount = (0, 1)
    high_value = (1, 0)
    amount_high = learning_increment(state[0][0], scale) + learning_increment(state[1][1], scale)
    amount_value = learning_increment(state[1][0], scale) + learning_increment(state[0][1], scale)
    assert amount_high > amount_value
    assert development_g3a_direct(state, high_amount, scale) < development_g3a_direct(state, high_value, scale)


def test_reproducible_random_implementation_audit() -> None:
    first = random_identity_audit(states=1_000, seed=7357)
    second = random_identity_audit(states=1_000, seed=7357)
    assert first == second
    assert first.action_evaluations == 12_000
    assert max(first.max_residual_g3a, first.max_residual_g3b, first.max_residual_dual) <= 16 * EXACT_TOL
