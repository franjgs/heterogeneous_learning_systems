"""Deterministic controls for the documented minimal HLS reference scenario."""

import math

import pytest

from hls.minimal_reference_scenario import (
    EXACT_TOL,
    LearningRule,
    MinimalReferenceScenario,
    identity_residual,
    reference_configurations,
)


def _configs():
    return reference_configurations()


def _assert_identity(scenario: MinimalReferenceScenario) -> None:
    assert abs(identity_residual(scenario)) <= EXACT_TOL


def test_s0_is_static_organization_with_no_state_or_future_value_difference() -> None:
    scenario = _configs()["S0_static"]
    evaluation = scenario.evaluate()
    assert scenario.demand_0 == scenario.demand_1
    assert scenario.learning_rule is LearningRule.NONE
    assert evaluation.state_e == evaluation.state_d == scenario.state_0
    assert evaluation.gain == pytest.approx(0.0, abs=EXACT_TOL)
    assert evaluation.loss > 0.0
    assert evaluation.optimal_actions() == ("E",)
    _assert_identity(scenario)


def test_s1_changes_demand_but_keeps_competence_fixed_and_decision_static() -> None:
    scenario = _configs()["S1_adaptive_fixed"]
    evaluation = scenario.evaluate()
    assert scenario.demand_0 != scenario.demand_1
    assert evaluation.state_e == evaluation.state_d == scenario.state_0
    assert evaluation.value_e == pytest.approx(evaluation.value_d, abs=EXACT_TOL)
    assert evaluation.gain == pytest.approx(0.0, abs=EXACT_TOL)
    assert evaluation.optimal_actions() == ("E",)
    _assert_identity(scenario)


def test_s2_has_positive_simulated_development_value_without_decision_reversal() -> None:
    scenario = _configs()["S2_decision_equivalent"]
    evaluation = scenario.evaluate()
    assert evaluation.state_e != evaluation.state_d
    assert evaluation.state_e[0][0] == pytest.approx(0.83375, abs=EXACT_TOL)
    assert evaluation.state_e[0][1] == pytest.approx(0.40, abs=EXACT_TOL)
    assert evaluation.state_e[1] == (0.70, 0.875)
    assert evaluation.state_d[0][0] == pytest.approx(0.65, abs=EXACT_TOL)
    assert evaluation.state_d[0][1] == pytest.approx(0.94, abs=EXACT_TOL)
    assert evaluation.state_d[1][0] == pytest.approx(0.835, abs=EXACT_TOL)
    assert evaluation.state_d[1][1] == pytest.approx(0.50, abs=EXACT_TOL)
    assert evaluation.value_e == pytest.approx(0.875, abs=EXACT_TOL)
    assert evaluation.value_d == pytest.approx(0.94, abs=EXACT_TOL)
    assert evaluation.gain > 0.0
    assert scenario.beta * evaluation.gain < evaluation.loss
    assert evaluation.total_difference < 0.0
    assert evaluation.optimal_actions() == ("E",)
    _assert_identity(scenario)


def test_boundary_is_constructed_from_simulated_l_and_g_not_a_g_parameter() -> None:
    scenario = _configs()["boundary"]
    evaluation = scenario.evaluate()
    assert evaluation.gain > 0.0
    assert scenario.beta == pytest.approx(evaluation.loss / evaluation.gain, abs=EXACT_TOL)
    assert scenario.beta * evaluation.gain == pytest.approx(evaluation.loss, abs=EXACT_TOL)
    assert evaluation.total_difference == pytest.approx(0.0, abs=EXACT_TOL)
    assert evaluation.optimal_actions() == ("E", "D")
    _assert_identity(scenario)


def test_s3_emerges_when_simulated_future_value_outweighs_present_loss() -> None:
    scenario = _configs()["S3_decision_relevant"]
    evaluation = scenario.evaluate()
    assert evaluation.gain > 0.0
    assert scenario.beta * evaluation.gain > evaluation.loss
    assert evaluation.total_difference > 0.0
    assert evaluation.optimal_actions() == ("D",)
    _assert_identity(scenario)


def test_homogeneous_linear_learning_negative_control_has_zero_g() -> None:
    scenario = _configs()["negative_homogeneous_linear"]
    evaluation = scenario.evaluate()
    assert scenario.learning_rule is LearningRule.HOMOGENEOUS_LINEAR
    assert evaluation.state_e != evaluation.state_d
    assert evaluation.value_e == pytest.approx(evaluation.value_d, abs=EXACT_TOL)
    assert evaluation.gain == pytest.approx(0.0, abs=EXACT_TOL)
    assert evaluation.loss > 0.0
    assert evaluation.optimal_actions() == ("E",)
    _assert_identity(scenario)


def test_joint_assignment_is_capacity_limited_at_both_periods() -> None:
    scenario = _configs()["S3_decision_relevant"]
    evaluation = scenario.evaluate()
    assert scenario.present_reward("E") > scenario.present_reward("D")
    assert scenario.terminal_value(evaluation.state_e) == pytest.approx(evaluation.value_e)
    assert scenario.terminal_value(evaluation.state_d) == pytest.approx(evaluation.value_d)


def test_terminal_value_optimizes_the_future_assignment_rather_than_encoding_g() -> None:
    scenario = MinimalReferenceScenario(
        state_0=((0.20, 0.90), (0.80, 0.10)),
        demand_0=(0.50, 0.50),
        demand_1=(0.50, 0.50),
        beta=0.0,
    )
    state = ((0.90, 0.20), (0.10, 0.80))
    assert scenario.terminal_value(state) == pytest.approx(0.85, abs=EXACT_TOL)


def test_learning_by_doing_updates_each_workers_actually_assigned_task() -> None:
    scenario = _configs()["S2_decision_equivalent"]
    state_e = scenario.transition("E")
    state_d = scenario.transition("D")
    # E is w1 -> A, w2 -> B; D is w1 -> B, w2 -> A.
    assert state_e[0][0] > scenario.state_0[0][0]
    assert state_e[1][1] > scenario.state_0[1][1]
    assert state_e[0][1] == scenario.state_0[0][1]
    assert state_e[1][0] == scenario.state_0[1][0]
    assert state_d[0][1] > scenario.state_0[0][1]
    assert state_d[1][0] > scenario.state_0[1][0]
    assert state_d[0][0] == scenario.state_0[0][0]
    assert state_d[1][1] == scenario.state_0[1][1]


def test_zero_learning_scale_is_the_no_development_limit_of_each_learning_rule() -> None:
    for rule in (LearningRule.DIMINISHING, LearningRule.HOMOGENEOUS_LINEAR):
        scenario = MinimalReferenceScenario(
            state_0=((0.65, 0.40), (0.70, 0.50)),
            demand_0=(0.50, 0.50),
            demand_1=(0.00, 1.00),
            beta=0.50,
            learning_rule=rule,
            learning_scale=0.0,
        )
        evaluation = scenario.evaluate()
        assert evaluation.state_e == evaluation.state_d == scenario.state_0
        assert evaluation.gain == pytest.approx(0.0, abs=EXACT_TOL)
        _assert_identity(scenario)


def test_no_action_label_is_privileged_when_d_is_statically_better() -> None:
    scenario = MinimalReferenceScenario(
        state_0=((0.20, 0.90), (0.80, 0.10)),
        demand_0=(0.50, 0.50),
        demand_1=(0.50, 0.50),
        beta=0.0,
    )
    evaluation = scenario.evaluate()
    assert evaluation.reward_d > evaluation.reward_e
    assert evaluation.optimal_actions() == ("D",)
    _assert_identity(scenario)


def test_invalid_world_inputs_are_rejected() -> None:
    with pytest.raises(ValueError):
        MinimalReferenceScenario(
            state_0=((0.0, 0.0), (0.0, 1.1)),
            demand_0=(0.5, 0.5),
            demand_1=(0.5, 0.5),
            beta=0.5,
        )
    with pytest.raises(ValueError):
        MinimalReferenceScenario(
            state_0=((0.0, 0.0), (0.0, 1.0)),
            demand_0=(0.6, 0.6),
            demand_1=(0.5, 0.5),
            beta=0.5,
        )
    with pytest.raises(ValueError):
        MinimalReferenceScenario(
            state_0=((0.0, 0.0), (0.0, 1.0)),
            demand_0=(0.5, 0.5),
            demand_1=(0.5, 0.5),
            beta=math.nan,
        )
