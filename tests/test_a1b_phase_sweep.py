from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

from hls.a1a import reference_worlds, solve_hls, solve_strong_sep
from hls.a1b import (
    BASE_E_H,
    BASE_ETA,
    BASE_KAPPA,
    BASE_RHO,
    BOUNDARY,
    EXPECTED_COUNTS,
    GREATER,
    LESS,
    NEGATIVE_UNEXPECTED,
    NO_ADVANTAGE,
    OPPORTUNITY_THRESHOLD,
    PHASE_1,
    PHASE_2,
    PHASE_3,
    RHO_STAR,
    STRICT_ADVANTAGE,
    TOL,
    all_configurations,
    analytical_regime,
    conservative_advantage,
    coupling_configurations,
    development_configurations,
    evaluate_configuration,
    observed_regime,
    opportunity_configurations,
    run_sweep,
)


def test_pre_registered_configuration_counts_and_total() -> None:
    phases = {
        PHASE_1: coupling_configurations(),
        PHASE_2: development_configurations(),
        PHASE_3: opportunity_configurations(),
    }
    assert {phase: len(configs) for phase, configs in phases.items()} == EXPECTED_COUNTS
    assert len(all_configurations()) == 1020
    for configurations in phases.values():
        primitive_keys = {
            (config.rho, config.eta, config.kappa, config.e_h, config.e_s)
            for config in configurations
        }
        assert len(primitive_keys) == len(configurations)


def test_coupling_grid_contains_exactly_the_pre_registered_points() -> None:
    global_grid = {Fraction(index, 20) for index in range(21)}
    probes = {RHO_STAR}
    for distance in (Fraction(1, 100), Fraction(1, 1000), Fraction(1, 10000)):
        probes |= {RHO_STAR - distance, RHO_STAR + distance}
    actual = {config.rho for config in coupling_configurations()}

    assert actual == global_grid | probes
    assert len(probes) == 7
    assert not global_grid & probes


def test_development_grid_contains_no_extra_configurations() -> None:
    expected = {
        (Fraction(eta_index, 20), Fraction(kappa_index, 50))
        for eta_index in range(21)
        for kappa_index in range(26)
    }
    actual = {(config.eta, config.kappa) for config in development_configurations()}
    assert actual == expected
    assert all(config.rho == BASE_RHO for config in development_configurations())


def test_opportunity_grid_and_probes_are_exactly_pre_registered() -> None:
    grid = {
        (Fraction(e_h_index, 20), Fraction(e_s_index, 20))
        for e_h_index in range(21)
        for e_s_index in range(21)
    }
    boundary = BASE_E_H + OPPORTUNITY_THRESHOLD
    probes = {(BASE_E_H, boundary)}
    for distance in (Fraction(1, 100), Fraction(1, 1000)):
        probes |= {
            (BASE_E_H, boundary - distance),
            (BASE_E_H, boundary + distance),
        }
    actual = {(config.e_h, config.e_s) for config in opportunity_configurations()}

    assert actual == grid | probes
    assert len(probes) == 5
    assert not grid & probes
    assert all(0 <= e_s <= 1 for _, e_s in probes)


def test_frozen_tolerance_and_classifiers_preserve_negative_values() -> None:
    assert TOL == 1e-12
    assert analytical_regime(-2 * TOL) == LESS
    assert analytical_regime(-TOL) == BOUNDARY
    assert analytical_regime(0.0) == BOUNDARY
    assert analytical_regime(TOL) == BOUNDARY
    assert analytical_regime(2 * TOL) == GREATER
    assert observed_regime(-2 * TOL) == NEGATIVE_UNEXPECTED
    assert observed_regime(-TOL) == NO_ADVANTAGE
    assert observed_regime(0.0) == NO_ADVANTAGE
    assert observed_regime(TOL) == NO_ADVANTAGE
    assert observed_regime(2 * TOL) == STRICT_ADVANTAGE


def test_conservative_advantage_uses_sep_max_under_immediate_tie() -> None:
    world = replace(
        reference_worlds()["E"],
        competence=((0.80, 0.50), (0.80, 0.20)),
    )
    hls = solve_hls(world)
    sep = solve_strong_sep(world)

    assert sep.value is None
    assert sep.value_min < sep.value_max
    assert conservative_advantage(hls, sep) == hls.optimal_value - sep.value_max
    assert conservative_advantage(hls, sep) == 0.0


def test_exact_coupling_boundary_is_derived_not_identified_by_id() -> None:
    boundary = next(
        config for config in coupling_configurations() if config.rho == RHO_STAR
    )
    row = evaluate_configuration(boundary)

    assert abs(float(row["analytical_margin"])) <= TOL
    assert row["predicted_regime"] == BOUNDARY
    assert row["observed_regime"] == NO_ADVANTAGE
    assert row["match"]


def test_complete_sweep_controls_reducibility_and_constant_competence() -> None:
    rows, summary = run_sweep()

    assert summary["effective_counts"] == EXPECTED_COUNTS
    assert summary["negative_controls_complete"]
    assert summary["negative_control_violation_count"] == 0
    assert summary["SEP_Omega_violation_count"] == 0
    assert all(not row["SEP_Omega_violation"] for row in rows)
    assert {
        (row["c_11"], row["c_12"], row["c_21"], row["c_22"])
        for row in rows
    } == {(0.80, 0.50, 0.70, 0.20)}
    assert all(row["SEP_immediate_optimal_actions"] == "M1" for row in rows)


def test_repeated_complete_sweep_is_deterministic() -> None:
    first_rows, first_summary = run_sweep()
    second_rows, second_summary = run_sweep()
    assert first_rows == second_rows
    assert first_summary == second_summary


def test_base_parameters_remain_frozen_outside_each_phase() -> None:
    assert all(
        config.eta == BASE_ETA and config.kappa == BASE_KAPPA
        for config in coupling_configurations()
    )
    assert all(
        config.rho == BASE_RHO and config.e_h == BASE_E_H
        for config in development_configurations()
    )
    assert all(
        config.rho == BASE_RHO
        and config.eta == BASE_ETA
        and config.kappa == BASE_KAPPA
        for config in opportunity_configurations()
    )
