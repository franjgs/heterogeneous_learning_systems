"""Controls for the diagnostic regime map over fixed G3-H physics."""

from __future__ import annotations

import pytest

from hls.g3_h_organizational_value import development_g3h, transition_g3h
from hls.g3_h_regime_map import REGIME_TOL, evaluate_point
from hls.g3_organizational_value import G3A_ASSIGNMENTS, development_g3a_direct, transition_g3a


CANONICAL_STATE = ((0.5, 0.7), (0.3, 0.2), (0.5, 0.8))
CANONICAL_PROFILE = (0.4, 0.6, 0.4)


def test_canonical_g3h_ranking_inversion_is_calculated_through_the_evaluator() -> None:
    evaluation = evaluate_point(CANONICAL_STATE, CANONICAL_PROFILE)
    by_action = {observation.action: observation for observation in evaluation.actions}
    xa, xb = (1, 2), (2, 0)  # Documented human actions (2,3) and (3,1).
    assert by_action[xa].local_value == pytest.approx(1.210, abs=REGIME_TOL)
    assert by_action[xb].local_value == pytest.approx(1.236, abs=REGIME_TOL)
    assert by_action[xa].dynamic_value == pytest.approx(2.732444, abs=REGIME_TOL)
    assert by_action[xb].dynamic_value == pytest.approx(2.6638784, abs=REGIME_TOL)
    assert by_action[xa].local_value < by_action[xb].local_value
    assert by_action[xa].dynamic_value > by_action[xb].dynamic_value


@pytest.mark.parametrize(
    ("state", "profile"),
    (
        (CANONICAL_STATE, CANONICAL_PROFILE),
        (((0.5, 0.5), (0.5, 0.5), (0.5, 0.5)), (0.4, 0.4, 0.4)),
        (((0.2, 0.9), (0.8, 0.1), (0.45, 0.55)), (0.2, 0.4, 0.6)),
    ),
)
def test_regimes_are_exclusive_and_regrets_follow_the_decision_contract(state, profile) -> None:
    evaluation = evaluate_point(state, profile)
    assert evaluation.regime in {
        "R0_USE_SUFFICIENT",
        "R1_LOCAL_NECESSARY_SUFFICIENT",
        "R2_LOCAL_INSUFFICIENT",
    }
    if evaluation.regime == "R0_USE_SUFFICIENT":
        assert evaluation.regret_use == pytest.approx(0.0, abs=REGIME_TOL)
    elif evaluation.regime == "R1_LOCAL_NECESSARY_SUFFICIENT":
        assert evaluation.regret_use > REGIME_TOL
        assert evaluation.regret_local == pytest.approx(0.0, abs=REGIME_TOL)
    else:
        assert evaluation.regret_local > REGIME_TOL
    if evaluation.r2_reversion:
        assert evaluation.regret_use == pytest.approx(0.0, abs=REGIME_TOL)
        assert evaluation.regret_local > REGIME_TOL


def test_optimal_sets_regime_and_regrets_do_not_depend_on_action_enumeration_order() -> None:
    forward = evaluate_point(CANONICAL_STATE, CANONICAL_PROFILE)
    reverse = evaluate_point(CANONICAL_STATE, CANONICAL_PROFILE, actions=tuple(reversed(G3A_ASSIGNMENTS)))
    assert reverse.optimal_use == forward.optimal_use
    assert reverse.optimal_local == forward.optimal_local
    assert reverse.optimal_dynamic == forward.optimal_dynamic
    assert reverse.regime == forward.regime
    assert reverse.r2_reversion == forward.r2_reversion
    assert reverse.regret_use == pytest.approx(forward.regret_use, abs=REGIME_TOL)
    assert reverse.regret_local == pytest.approx(forward.regret_local, abs=REGIME_TOL)


def test_homogeneous_profile_uses_the_g3_control_without_special_case() -> None:
    state = ((0.2, 0.9), (0.8, 0.1), (0.45, 0.55))
    action = (1, 0)
    scale = 0.4
    assert transition_g3h(state, action, (scale, scale, scale)) == transition_g3a(state, action, scale)
    assert development_g3h(state, action, (scale, scale, scale)) == pytest.approx(
        development_g3a_direct(state, action, scale), abs=REGIME_TOL
    )


def test_successors_remain_in_the_canonical_competence_bounds() -> None:
    evaluation = evaluate_point(CANONICAL_STATE, CANONICAL_PROFILE)
    for observation in evaluation.actions:
        assert all(0.0 <= value <= 1.0 for row in observation.successor for value in row)
