from hls.g3_h_organizational_value import G3HLearningProfile
from hls.g3_h_regime_map import evaluate_point
from hls.g3_h_stability_audit import cancelled_dynamic_value, condition_c
from hls.g3_h_structural_autopsy import local_rule_flags


def test_cancelled_q_expansion_matches_evaluator_for_every_action() -> None:
    state = ((0.5, 0.7), (0.3, 0.2), (0.5, 0.8))
    profile = G3HLearningProfile((0.4, 0.6, 0.4))
    evaluation = evaluate_point(state, profile)
    for action in evaluation.actions:
        assert abs(cancelled_dynamic_value(state, action.action, profile) - action.dynamic_value) < 1e-12


def test_condition_c_matches_direct_successor_optimality() -> None:
    evaluation = evaluate_point(
        ((0.2, 0.4), (0.5, 0.1), (0.7, 0.8)),
        G3HLearningProfile((0.3, 0.3, 0.3)),
    )
    audit = condition_c(evaluation)
    assert audit.holds == (audit.margin >= -8.0e-15)
    assert audit.holds == local_rule_flags(evaluation)["no_immediate_crossing"]
