from dataclasses import FrozenInstanceError
import inspect

import pytest

import hls.synthetic.c1 as c1
from hls.synthetic import DevelopmentDecision, NULL_DEVELOPMENT, Opportunity
from hls.synthetic.components import ScheduledSaturatingDevelopmentKernel


EXPECTED = {
    "R1_no_evolution": (False, False, False, 2.4, 2.4, 0.0),
    "R2_evolution_no_decision_feedback": (True, False, False, 2.7, 2.7, 0.0),
    "R3_decision_feedback_no_second_order": (True, True, False, 2.55, 2.55, 0.0),
    "R4_recursive_value_neutral_boundary": (True, True, True, 2.4, 2.4, 0.0),
    "R5_recursive_strict_value": (True, True, True, 2.45, 2.4, 0.05),
}


@pytest.mark.parametrize("name", tuple(EXPECTED))
def test_exact_reference_world(name: str) -> None:
    world = c1.reference_worlds()[name]
    result = c1.evaluate_world(world)
    i, ii, iii, j_hls, j_sep, delta = EXPECTED[name]
    assert (result.links.state_effect, result.links.decision_effect, result.links.second_order_effect) == (i, ii, iii)
    assert result.links.genuine is (i and ii and iii)
    assert result.hls.value == pytest.approx(j_hls, abs=1e-12)
    assert result.sep.value_min == pytest.approx(j_sep, abs=1e-12)
    assert result.sep.value_max == pytest.approx(j_sep, abs=1e-12)
    assert result.delta_j_cons == pytest.approx(delta, abs=1e-12)
    assert result.sep_omega.value == pytest.approx(result.hls.value, abs=1e-12)


def test_reference_set_is_minimal_and_named() -> None:
    assert tuple(c1.reference_worlds()) == tuple(EXPECTED)


def test_learning_and_decision_change_are_not_c1() -> None:
    worlds = c1.reference_worlds()
    assert c1.evaluate_world(worlds["R2_evolution_no_decision_feedback"]).links.genuine is False
    assert c1.evaluate_world(worlds["R3_decision_feedback_no_second_order"]).links.genuine is False


def test_recursive_feedback_can_be_value_neutral_and_boundary_is_preserved() -> None:
    result = c1.evaluate_world(c1.reference_worlds()["R4_recursive_value_neutral_boundary"])
    assert result.links.genuine
    assert result.delta_j_cons == pytest.approx(0.0, abs=1e-12)
    assert result.hls.optimal_actions == frozenset({"M1", "M2"})


def test_strict_world_has_honest_conservative_advantage_and_persistent_path() -> None:
    world = c1.reference_worlds()["R5_recursive_strict_value"]
    result = c1.evaluate_world(world)
    assert result.hls.optimal_actions == frozenset({"M2"})
    assert result.sep.immediate_optimal_actions == frozenset({"M1"})
    assert result.delta_j_cons == pytest.approx(0.05, abs=1e-12)
    left, right = world.interventions
    s1_sep = c1._apply_intervention(world, left)
    s1_hls = c1._apply_intervention(world, right)
    assert s1_sep.competence != s1_hls.competence
    opportunity = Opportunity(True)
    s2_hls = world.environment.development.transition(
        s1_hls, opportunity, DevelopmentDecision("M1", 1)
    )
    assert s2_hls.competence != s1_sep.competence
    assert s2_hls.time == 2


def test_two_transitions_use_the_development_kernel_and_actor_can_differ_from_recipient() -> None:
    world = c1.reference_worlds()["R5_recursive_strict_value"]
    kernel = world.environment.development
    assert isinstance(kernel, ScheduledSaturatingDevelopmentKernel)
    s0 = world.environment.initial_state()
    s1 = kernel.transition(s0, Opportunity(True), DevelopmentDecision("M2", 2))
    s2 = kernel.transition(s1, Opportunity(True), DevelopmentDecision("M1", 1))
    assert (s0.time, s1.time, s2.time) == (0, 1, 2)
    assert s1.competence[1][1] == pytest.approx(0.9)
    assert s2.competence[0][0] == pytest.approx(0.95)


def test_removing_second_order_effect_destroys_c1_but_not_decision_feedback() -> None:
    result = c1.evaluate_world(c1.reference_worlds()["R3_decision_feedback_no_second_order"])
    assert result.links.state_effect
    assert result.links.decision_effect
    assert not result.links.second_order_effect
    assert not result.links.genuine


def test_strong_sep_keeps_immediate_ties_and_interval_without_label_resolution() -> None:
    world = c1._make_world(
        "tie_audit", ((0.8, 0.8), (0.8, 0.6)), eta=0.75,
        task1_executor=(0.0, 1.0), task2_executor=(0.0, 1.0),
        interventions=(
            c1.Intervention("M1", NULL_DEVELOPMENT),
            c1.Intervention("M2", DevelopmentDecision("M2", 2)),
        ),
    )
    sep = c1.solve_strong_sep(world)
    assert sep.immediate_optimal_actions == frozenset({"M1", "M2"})
    assert sep.value_min <= sep.value_max
    assert set(sep.action_value_bounds) == {"M1", "M2"}


def test_strong_sep_retains_later_routing_ties_as_value_bounds() -> None:
    world = c1._make_world(
        "later_tie_audit", ((0.8, 0.8), (0.6, 0.8)), eta=0.75,
        task1_executor=(0.0, 0.0), task2_executor=(0.0, 1.0),
        interventions=(
            c1.Intervention("M1", NULL_DEVELOPMENT),
            c1.Intervention("M2", NULL_DEVELOPMENT),
        ),
    )
    sep = c1.solve_strong_sep(world)
    assert sep.immediate_optimal_actions == frozenset({"M1"})
    assert sep.value_min < sep.value_max


@pytest.mark.parametrize("name", tuple(EXPECTED))
def test_physical_relabeling_preserves_values_and_swaps_actions(name: str) -> None:
    world = c1.reference_worlds()[name]
    original = c1.evaluate_world(world)
    relabeled = c1.evaluate_world(c1.relabel_world(world))
    swap = {"M1": "M2", "M2": "M1"}
    assert relabeled.hls.value == pytest.approx(original.hls.value, abs=1e-12)
    assert relabeled.sep.value_min == pytest.approx(original.sep.value_min, abs=1e-12)
    assert relabeled.sep.value_max == pytest.approx(original.sep.value_max, abs=1e-12)
    assert relabeled.delta_j_cons == pytest.approx(original.delta_j_cons, abs=1e-12)
    assert relabeled.sep_omega.value == pytest.approx(original.sep_omega.value, abs=1e-12)
    assert relabeled.hls.optimal_actions == frozenset(swap[a] for a in original.hls.optimal_actions)
    assert relabeled.sep.immediate_optimal_actions == frozenset(
        swap[a] for a in original.sep.immediate_optimal_actions
    )


def test_same_physical_world_is_used_by_all_policies_and_state_is_immutable() -> None:
    world = c1.reference_worlds()["R5_recursive_strict_value"]
    environment_id = id(world.environment)
    c1.solve_hls(world); c1.solve_strong_sep(world); c1.solve_sep_omega(world)
    assert id(world.environment) == environment_id
    state = world.environment.initial_state()
    with pytest.raises(FrozenInstanceError):
        state.time = 1  # type: ignore[misc]


def test_sep_omega_is_not_an_alias_or_call_to_hls(monkeypatch) -> None:
    world = c1.reference_worlds()["R5_recursive_strict_value"]
    monkeypatch.setattr(c1, "solve_hls", lambda _: (_ for _ in ()).throw(AssertionError()))
    assert c1.solve_sep_omega(world).value == pytest.approx(2.45, abs=1e-12)


def test_worlds_use_only_c1_physics_and_no_name_branches() -> None:
    for world in c1.reference_worlds().values():
        state = world.environment.initial_state()
        assert (state.n_learners, state.n_competences) == (2, 2)
        assert world.environment.resources.kappa == 0.0
        assert world.environment.resources.beta == 1.0
        assert world.environment.development.eta in (0.0, 0.75)
        assert all(
            value in (0.0, 1.0)
            for value in world.environment.opportunities.executor_values.values()
        )
    solver_source = inspect.getsource(c1.solve_hls) + inspect.getsource(c1.solve_strong_sep)
    assert not any(name in solver_source for name in EXPECTED)


def test_reference_results_are_derived_not_stored_in_world() -> None:
    world = c1.reference_worlds()["R5_recursive_strict_value"]
    assert not hasattr(world, "expected_value")
    assert not hasattr(world, "desired_winner")
