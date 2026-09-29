import pytest

from hls.a1a import (
    Learner,
    reference_worlds,
    solve_hls,
    solve_sep_omega,
    solve_strong_sep,
)
from hls.synthetic.adapters.a1 import build_a1_environment, evaluate_a1_exact


def _old_learners(actions):
    return frozenset(action.value for action in actions)


def _old_development(actions):
    return frozenset(
        (None, None) if action.is_null else (action.recipient.value, action.task)
        for action in actions
    )


def _new_development(actions):
    return frozenset((action.recipient, action.competence) for action in actions)


@pytest.mark.parametrize("name", tuple("ABCDEF"))
def test_g0_reproduces_each_reference_world(name: str) -> None:
    world = reference_worlds()[name]
    old_hls = solve_hls(world)
    old_sep = solve_strong_sep(world)
    old_omega = solve_sep_omega(world)
    new = evaluate_a1_exact(build_a1_environment(world))

    assert new.no_opportunity_value == pytest.approx(old_hls.no_opportunity_value, abs=1e-12)
    assert new.opportunity_value == pytest.approx(old_hls.opportunity_value, abs=1e-12)
    assert new.hls.value == pytest.approx(old_hls.optimal_value, abs=1e-12)
    assert new.strong_sep.value_min == pytest.approx(old_sep.value_min, abs=1e-12)
    assert new.strong_sep.value_max == pytest.approx(old_sep.value_max, abs=1e-12)
    assert new.sep_omega.value == pytest.approx(old_omega.optimal_value, abs=1e-12)
    assert new.hls.optimal_actions == _old_learners(old_hls.optimal_operational_actions)
    assert new.strong_sep.immediate_optimal_actions == _old_learners(old_sep.immediate_optimal_actions)
    assert new.sep_omega.optimal_actions == _old_learners(old_omega.optimal_operational_actions)
    assert _new_development(new.optimal_development_actions) == _old_development(
        old_hls.optimal_development_actions
    )
    for learner in (Learner.M1, Learner.M2):
        label = learner.value
        assert new.operational_rewards[label] == pytest.approx(old_hls.operational_rewards[learner], abs=1e-12)
        assert new.opportunity_probabilities[label] == pytest.approx(old_hls.opportunity_probabilities[learner], abs=1e-12)
        assert new.continuation_values[label] == pytest.approx(old_hls.continuation_values[learner], abs=1e-12)
        assert new.total_values[label] == pytest.approx(old_hls.total_values[learner], abs=1e-12)


def test_reference_values_remain_frozen() -> None:
    evaluations = {
        name: evaluate_a1_exact(build_a1_environment(world))
        for name, world in reference_worlds().items()
    }
    expected = {"A": 1.30, "B": 1.49, "C": 1.4615, "D": 1013 / 700, "E": 1.504, "F": 1.504}
    for name, value in expected.items():
        assert evaluations[name].hls.value == pytest.approx(value, abs=1e-12)
    assert evaluations["D"].hls.optimal_actions == frozenset({"M1", "M2"})
    assert evaluations["E"].strong_sep.value_max == pytest.approx(1.4045, abs=1e-12)
    assert evaluations["E"].delta_j_cons == pytest.approx(0.0995, abs=1e-12)
    assert evaluations["F"].sep_omega.value == pytest.approx(1.504, abs=1e-12)
