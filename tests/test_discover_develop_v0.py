"""Focused controls for the DISCOVER x DEVELOP functional prototype."""
from hls.discover_develop_v0 import DEVELOP_KNOWN, DISCOVER_ONLY, MIS_LEARNING_SCALE, mis_transition, run_sequence
from hls.discover_v0 import THETA_1, THETA_2

S001 = ((0.0, 0.0), (0.5, 0.5), (1.0, 1.0))

def test_mis_matches_canonical_diminishing_reference_and_only_exercised_cells_change():
    action = ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))
    after = mis_transition(S001, action, enabled=True)
    assert MIS_LEARNING_SCALE == 1.5
    assert after[1][0] == min(1.0, .5 + 1.5 * .5**2)
    assert after[2][1] == 1.0
    assert after[0] == S001[0] and after[1][1] == S001[1][1] and after[2][0] == S001[2][0]

def test_develop_off_leaves_state_fixed_and_runs_reproducibly():
    first = run_sequence(S001, (THETA_1, THETA_2), mode=DISCOVER_ONLY, seed=7)
    second = run_sequence(S001, (THETA_1, THETA_2), mode=DISCOVER_ONLY, seed=7)
    assert first == second
    assert all(row.state_before == row.state_after for row in first)

def test_discover_policy_does_not_receive_true_theta_as_an_argument():
    first = run_sequence(S001, (THETA_1,), mode=DISCOVER_ONLY, seed=9)
    second = run_sequence(S001, (THETA_2,), mode=DISCOVER_ONLY, seed=9)
    assert first[0].action == second[0].action

def test_known_theta_keeps_policy_belief_revealed():
    rows = run_sequence(S001, (THETA_2,), mode=DEVELOP_KNOWN, seed=3)
    assert all(row.belief_before == 0.0 and row.belief_after == 0.0 for row in rows)
