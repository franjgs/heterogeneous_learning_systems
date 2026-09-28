from __future__ import annotations

from dataclasses import fields, replace
from fractions import Fraction
import inspect
import math

import pytest

import hls.a1a as a1a
from hls.a1a import (
    DEFAULT_ABS_TOL,
    DevelopmentAction,
    Learner,
    NULL_DEVELOPMENT,
    continuation_value,
    development_cost,
    development_transition,
    general_diagnostics,
    no_opportunity_value,
    opportunity_probability,
    opportunity_value,
    reference_diagnostics,
    reference_worlds,
    solve_hls,
    solve_sep_omega,
    solve_strong_sep,
)


TOL = 1e-12
M1_ONLY = frozenset({Learner.M1})
M2_ONLY = frozenset({Learner.M2})
BOTH = frozenset({Learner.M1, Learner.M2})


def close(actual: float, expected: float) -> None:
    assert math.isclose(actual, expected, rel_tol=0.0, abs_tol=TOL)


def test_world_a_no_learning_acceptance() -> None:
    world = reference_worlds()["A"]
    hls = solve_hls(world)
    sep = solve_strong_sep(world)
    diagnostics = reference_diagnostics(world)

    assert world.eta == 0.0
    assert world.rho == 1.0
    close(hls.opportunity_value, 0.50)
    close(hls.no_opportunity_value, 0.50)
    close(diagnostics["delta_G"], 0.0)
    close(hls.optimal_value, 1.30)
    close(sep.value, 1.30)
    assert hls.optimal_operational_actions == M1_ONLY
    assert hls.optimal_development_actions == frozenset({NULL_DEVELOPMENT})


def test_world_b_learning_without_coupling_acceptance() -> None:
    world = reference_worlds()["B"]
    hls = solve_hls(world)
    sep = solve_strong_sep(world)

    assert world.eta == 0.8
    assert world.rho == 0.0
    close(hls.opportunity_value, 0.88)
    close(hls.no_opportunity_value, 0.50)
    close(hls.continuation_values[Learner.M1], 0.69)
    close(hls.continuation_values[Learner.M2], 0.69)
    close(hls.optimal_value, 1.49)
    close(sep.value, 1.49)
    assert hls.optimal_operational_actions == M1_ONLY


def test_world_c_insufficient_coupling_acceptance() -> None:
    world = reference_worlds()["C"]
    hls = solve_hls(world)
    sep = solve_strong_sep(world)
    diagnostics = reference_diagnostics(world)

    close(opportunity_probability(world, Learner.M1, 1), 0.425)
    close(opportunity_probability(world, Learner.M2, 1), 0.600)
    close(hls.continuation_values[Learner.M1], 0.6615)
    close(hls.continuation_values[Learner.M2], 0.728)
    close(diagnostics["delta_G"], 0.0665)
    close(diagnostics["delta_R"], 0.10)
    close(hls.optimal_value, 1.4615)
    close(sep.value, 1.4615)
    assert hls.optimal_operational_actions == M1_ONLY


def test_world_d_exact_boundary_preserves_tie() -> None:
    world = reference_worlds()["D"]
    hls = solve_hls(world)
    sep = solve_strong_sep(world)
    diagnostics = reference_diagnostics(world)
    expected = float(Fraction(1013, 700))

    close(world.rho, float(Fraction(50, 133)))
    close(diagnostics["delta_G"], 0.10)
    close(diagnostics["delta_R"], 0.10)
    close(hls.total_values[Learner.M1], expected)
    close(hls.total_values[Learner.M2], expected)
    close(hls.optimal_value, expected)
    close(sep.value, expected)
    assert hls.optimal_operational_actions == BOTH
    assert hls.optimal_value - sep.value <= TOL


def test_world_e_strict_joint_advantage_and_causal_separation() -> None:
    world = reference_worlds()["E"]
    hls = solve_hls(world)
    sep = solve_strong_sep(world)
    diagnostics = reference_diagnostics(world)
    develop_m1 = DevelopmentAction(Learner.M1, 2)

    close(opportunity_probability(world, Learner.M1, 1), 0.275)
    close(opportunity_probability(world, Learner.M2, 1), 0.800)
    close(hls.opportunity_value, 0.88)
    close(hls.no_opportunity_value, 0.50)
    assert hls.optimal_development_actions == frozenset({develop_m1})
    close(hls.continuation_values[Learner.M1], 0.6045)
    close(hls.continuation_values[Learner.M2], 0.804)
    close(diagnostics["delta_G"], 0.1995)
    close(diagnostics["delta_R"], 0.10)
    assert sep.immediate_optimal_actions == M1_ONLY
    assert hls.optimal_operational_actions == M2_ONLY
    close(sep.value, 1.4045)
    close(hls.optimal_value, 1.504)
    close(hls.optimal_value - sep.value, 0.0995)
    assert hls.selected_operational_action != develop_m1.recipient
    assert hls.selected_operational_action == Learner.M2
    assert develop_m1.recipient == Learner.M1


def test_world_f_sep_omega_reducibility_and_same_physical_world() -> None:
    worlds = reference_worlds()
    world_e = worlds["E"]
    world_f = worlds["F"]
    assert world_f is world_e

    hls = solve_hls(world_f)
    sep = solve_strong_sep(world_f)
    sep_omega = solve_sep_omega(world_f)

    assert sep_omega.optimal_operational_actions == M2_ONLY
    close(sep_omega.optimal_value, 1.504)
    close(hls.optimal_value, 1.504)
    close(sep.value, 1.4045)
    close(hls.optimal_value, sep_omega.optimal_value)


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        ("A", 1.30),
        ("B", 1.49),
        ("C", 1.4615),
        ("D", float(Fraction(1013, 700))),
        ("E", 1.4045),
        ("F", 1.4045),
    ),
)
def test_reference_world_sep_values_remain_unambiguous(
    name: str, expected: float
) -> None:
    sep = solve_strong_sep(reference_worlds()[name])
    assert sep.value is not None
    close(sep.value, expected)
    close(sep.value_min, expected)
    close(sep.value_max, expected)


def test_strong_sep_tie_interval_is_invariant_to_physical_relabeling() -> None:
    world = reference_worlds()["E"]
    tied = replace(world, competence=((0.80, 0.50), (0.80, 0.20)))
    relabeled = replace(
        world,
        competence=((0.80, 0.20), (0.80, 0.50)),
        executor_opportunity=((0.90, None), (0.20, None)),
    )

    original = solve_strong_sep(tied)
    swapped = solve_strong_sep(relabeled)

    assert original.immediate_optimal_actions == BOTH
    assert swapped.immediate_optimal_actions == BOTH
    assert original.value is None
    assert swapped.value is None
    close(original.value_min, 1.4045)
    close(original.value_max, 1.604)
    close(swapped.value_min, original.value_min)
    close(swapped.value_max, original.value_max)
    assert sorted(original.expected_total_values.values()) == sorted(
        swapped.expected_total_values.values()
    )


def test_sep_solvers_do_not_depend_on_solve_hls(monkeypatch: pytest.MonkeyPatch) -> None:
    world = reference_worlds()["F"]

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("separated solver called solve_hls")

    monkeypatch.setattr(a1a, "solve_hls", forbidden)
    close(a1a.solve_strong_sep(world).value, 1.4045)
    close(a1a.solve_sep_omega(world).optimal_value, 1.504)
    assert "solve_hls(" not in inspect.getsource(a1a.solve_strong_sep)
    assert "solve_hls(" not in inspect.getsource(a1a.solve_sep_omega)


def test_rho_zero_opportunity_is_learner_independent() -> None:
    world = reference_worlds()["B"]
    close(
        opportunity_probability(world, Learner.M1, 1),
        opportunity_probability(world, Learner.M2, 1),
    )


def test_rho_one_opportunity_equals_executor_primitive() -> None:
    world = reference_worlds()["A"]
    close(opportunity_probability(world, Learner.M1, 1), 0.20)
    close(opportunity_probability(world, Learner.M2, 1), 0.90)


def test_development_transition_changes_only_selected_entry() -> None:
    world = reference_worlds()["E"]
    action = DevelopmentAction(Learner.M2, 2)
    changed = development_transition(world, world.competence, action)

    assert changed[0] == world.competence[0]
    assert changed[1][0] == world.competence[1][0]
    close(changed[1][1], 0.84)


def test_null_development_preserves_state_and_has_zero_cost() -> None:
    world = reference_worlds()["E"]
    assert development_transition(world, world.competence, NULL_DEVELOPMENT) is world.competence
    close(development_cost(world, NULL_DEVELOPMENT), 0.0)


def test_development_recipient_can_differ_from_operational_actor() -> None:
    world = reference_worlds()["E"]
    hls = solve_hls(world)
    recipients = {
        action.recipient
        for action in hls.optimal_development_actions
        if not action.is_null
    }
    assert hls.optimal_operational_actions == M2_ONLY
    assert recipients == {Learner.M1}


def test_m2_can_be_unique_optimal_development_recipient() -> None:
    world = replace(
        reference_worlds()["E"],
        competence=((0.80, 0.10), (0.70, 0.60)),
    )
    development = opportunity_value(world)

    close(development.value, 0.90)
    assert development.optimal_actions == frozenset(
        {DevelopmentAction(Learner.M2, 2)}
    )


def test_continuation_is_derived_and_not_a_world_parameter() -> None:
    world = reference_worlds()["E"]
    development = opportunity_value(world)
    no_opportunity = no_opportunity_value(world)
    primitive_fields = {field.name for field in fields(world)}

    assert {"G", "delta_G", "delta_R", "Omega", "J_HLS", "J_SEP"}.isdisjoint(
        primitive_fields
    )
    for learner in (Learner.M1, Learner.M2):
        probability = opportunity_probability(world, learner, world.q0)
        expected = probability * development.value + (1.0 - probability) * no_opportunity
        close(continuation_value(world, learner), expected)


def test_eta_zero_with_positive_cost_makes_null_uniquely_optimal() -> None:
    world = reference_worlds()["A"]
    assert world.kappa > 0
    assert opportunity_value(world).optimal_actions == frozenset({NULL_DEVELOPMENT})


def test_strong_sep_routes_only_by_immediate_reward() -> None:
    world = reference_worlds()["E"]
    sep = solve_strong_sep(world)
    hls = solve_hls(world)

    assert sep.operational_rewards[Learner.M1] > sep.operational_rewards[Learner.M2]
    assert sep.immediate_optimal_actions == M1_ONLY
    assert hls.total_values[Learner.M2] > hls.total_values[Learner.M1]


def test_general_diagnostics_derive_reversed_immediate_optimum() -> None:
    world = replace(
        reference_worlds()["E"],
        competence=((0.70, 0.50), (0.80, 0.20)),
    )
    diagnostics = general_diagnostics(world)

    assert diagnostics.immediate_optimal_actions == M2_ONLY
    assert len(diagnostics.comparisons) == 1
    comparison = diagnostics.comparisons[0]
    assert comparison.immediate_optimum == Learner.M2
    assert comparison.alternative == Learner.M1
    close(comparison.delta_R, 0.10)
    with pytest.raises(ValueError, match="unique immediate optimum M1"):
        reference_diagnostics(world)


def test_hls_and_sep_omega_preserve_operational_ties() -> None:
    world = reference_worlds()["D"]
    assert solve_hls(world).optimal_operational_actions == BOTH
    assert solve_sep_omega(world).optimal_operational_actions == BOTH


@pytest.mark.parametrize(
    ("field_name", "invalid"),
    (("rho", -0.1), ("eta", 1.1), ("beta", 1.1), ("kappa", -0.1)),
)
def test_world_validates_scalar_ranges(field_name: str, invalid: float) -> None:
    world = reference_worlds()["B"]
    with pytest.raises(ValueError):
        replace(world, **{field_name: invalid})


def test_tie_tolerance_is_explicit_and_strict() -> None:
    assert DEFAULT_ABS_TOL == 1e-12
    values = {Learner.M1: 1.0, Learner.M2: 1.0 - 0.5e-12}
    assert a1a.optimal_set(values) == BOTH
    values[Learner.M2] = 1.0 - 2.0e-12
    assert a1a.optimal_set(values) == M1_ONLY
