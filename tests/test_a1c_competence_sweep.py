from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

from hls.a1a import Learner, solve_hls, solve_sep_omega, solve_strong_sep
from hls.a1b import (
    GREATER,
    LESS,
    NEGATIVE_UNEXPECTED,
    NO_ADVANTAGE,
    STRICT_ADVANTAGE,
    analytical_regime,
    conservative_advantage,
    observed_regime,
)
from hls.a1c import (
    BASE_EBAR,
    BASE_ETA,
    BASE_E_11,
    BASE_E_21,
    BASE_KAPPA,
    BASE_RHO,
    EXPECTED_COUNTS,
    FUTURE_THRESHOLD,
    IMMEDIATE_TIE,
    PHASE_1,
    PHASE_2,
    TOL,
    all_configurations,
    configuration_key,
    evaluate_configuration,
    future_geometry_configurations,
    present_gap_configurations,
    relabel_world,
    run_sweep,
    world_for,
)


def test_exact_pre_registered_counts_grids_and_no_extras() -> None:
    phase_1 = present_gap_configurations()
    phase_2 = future_geometry_configurations()
    configurations = all_configurations()

    assert EXPECTED_COUNTS == {PHASE_1: 17, PHASE_2: 441}
    assert len(phase_1) == 17
    assert len(phase_2) == 441
    assert len(configurations) == 458
    assert {configuration.c_21 for configuration in phase_1} == {
        Fraction(index, 20) for index in range(17)
    }
    assert {(configuration.c_12, configuration.c_22) for configuration in phase_2} == {
        (Fraction(i, 20), Fraction(j, 20)) for i in range(21) for j in range(21)
    }
    assert len({configuration.configuration_id for configuration in configurations}) == 458


def test_non_competence_primitives_are_fixed_and_only_intended_c_entries_vary() -> None:
    for configuration in all_configurations():
        world = world_for(configuration)
        assert world.rho == float(BASE_RHO)
        assert world.eta == float(BASE_ETA)
        assert world.kappa == float(BASE_KAPPA)
        assert world.opportunity_baseline == (float(BASE_EBAR), None)
        assert world.executor_opportunity == (
            (float(BASE_E_11), None),
            (float(BASE_E_21), None),
        )
        assert world.beta == 1.0
        assert world.q0 == 1 and world.q1 == 2

    phase_1 = present_gap_configurations()
    assert {(c.c_11, c.c_12, c.c_22) for c in phase_1} == {
        (Fraction(4, 5), Fraction(1, 2), Fraction(1, 5))
    }
    phase_2 = future_geometry_configurations()
    assert {(c.c_11, c.c_21) for c in phase_2} == {
        (Fraction(4, 5), Fraction(7, 10))
    }


def test_conservative_sep_tie_and_transition_sides() -> None:
    rows = {configuration.c_21: evaluate_configuration(configuration)
            for configuration in present_gap_configurations()}
    below = rows[Fraction(3, 5)]
    above = rows[Fraction(13, 20)]
    tie = rows[Fraction(4, 5)]

    assert below["predicted_regime"] == LESS
    assert below["observed_regime"] == NO_ADVANTAGE
    assert above["predicted_regime"] == GREATER
    assert above["observed_regime"] == STRICT_ADVANTAGE
    assert tie["immediate_tie"]
    assert tie["predicted_regime"] == IMMEDIATE_TIE
    assert tie["SEP_immediate_optimal_actions"] == "M1|M2"
    assert tie["Delta_J_cons"] == 0.0

    tie_world = world_for(present_gap_configurations()[-1])
    tie_hls = solve_hls(tie_world)
    tie_sep = solve_strong_sep(tie_world)
    assert conservative_advantage(tie_hls, tie_sep) == (
        tie_hls.optimal_value - tie_sep.value_max
    )


def test_required_development_and_terminal_geometries_are_represented() -> None:
    rows = tuple(evaluate_configuration(c) for c in future_geometry_configurations())
    assert {str(row["development_category"]) for row in rows} == {
        "null", "M1", "M2", "ties"
    }
    assert {str(row["initial_terminal_best_category"]) for row in rows} == {
        "M1", "M2", "tie"
    }
    assert FUTURE_THRESHOLD == Fraction(4, 21)


def test_d_equals_n_never_has_strict_advantage_and_no_negative_is_truncated() -> None:
    rows = tuple(evaluate_configuration(c) for c in future_geometry_configurations())
    d_equals_n = [row for row in rows if abs(float(row["D_minus_N"])) <= TOL]
    assert d_equals_n
    assert all(row["observed_regime"] != STRICT_ADVANTAGE for row in d_equals_n)
    assert observed_regime(-2 * TOL) == NEGATIVE_UNEXPECTED
    assert analytical_regime(-2 * TOL) == LESS


def test_sep_omega_and_full_physical_relabeling_invariance() -> None:
    for configuration in all_configurations():
        world = world_for(configuration)
        hls = solve_hls(world)
        sep = solve_strong_sep(world)
        omega = solve_sep_omega(world)
        relabeled = relabel_world(world)
        relabeled_hls = solve_hls(relabeled)
        relabeled_sep = solve_strong_sep(relabeled)
        relabeled_omega = solve_sep_omega(relabeled)

        assert abs(hls.optimal_value - omega.optimal_value) <= TOL
        assert abs(hls.optimal_value - relabeled_hls.optimal_value) <= TOL
        assert abs(sep.value_min - relabeled_sep.value_min) <= TOL
        assert abs(sep.value_max - relabeled_sep.value_max) <= TOL
        assert abs(omega.optimal_value - relabeled_omega.optimal_value) <= TOL
        assert (
            conservative_advantage(hls, sep)
            == conservative_advantage(relabeled_hls, relabeled_sep)
        )


def test_complete_sweep_passes_frozen_criteria_and_has_unique_ids() -> None:
    rows, summary = run_sweep()
    assert summary["status"] == "PASS"
    assert summary["effective_counts"] == EXPECTED_COUNTS
    assert summary["total_configurations"] == 458
    assert summary["mismatch_count"] == 0
    assert summary["SEP_Omega_violation_count"] == 0
    assert summary["full_relabeling_violation_count"] == 0
    assert summary["future_pair_violation_count"] == 0
    assert len({configuration_key(row) for row in rows}) == 458
    assert all(row["match"] for row in rows)


def test_repeated_complete_sweep_is_deterministic() -> None:
    first_rows, first_summary = run_sweep()
    second_rows, second_summary = run_sweep()
    assert first_rows == second_rows
    assert first_summary == second_summary


def test_relabeling_swaps_action_labels_not_string_identity() -> None:
    configuration = next(
        c for c in future_geometry_configurations()
        if c.c_12 == Fraction(1, 20) and c.c_22 == 0
    )
    world = world_for(configuration)
    relabeled = relabel_world(world)
    original = solve_hls(world)
    swapped = solve_hls(relabeled)
    label_swap = {Learner.M1: Learner.M2, Learner.M2: Learner.M1}
    assert {label_swap[action] for action in original.optimal_operational_actions} == set(
        swapped.optimal_operational_actions
    )
    assert original.optimal_development_actions != swapped.optimal_development_actions


def test_observed_classification_uses_sep_max_even_for_synthetic_tie_perturbation() -> None:
    configuration = present_gap_configurations()[-1]
    world = world_for(configuration)
    sep = solve_strong_sep(world)
    assert sep.value is None
    assert sep.value_min < sep.value_max
    hls = solve_hls(world)
    assert observed_regime(hls.optimal_value - sep.value_max) == NO_ADVANTAGE


def test_configuration_world_is_not_sensitive_to_identifier() -> None:
    configuration = present_gap_configurations()[5]
    renamed = replace(configuration, configuration_id="arbitrary-display-id")
    assert world_for(configuration) == world_for(renamed)
    assert evaluate_configuration(configuration) | {"configuration_id": renamed.configuration_id} == evaluate_configuration(renamed)
