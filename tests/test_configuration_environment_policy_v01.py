"""Controls for the known-environment configuration × environment v0.1 sweep."""

from __future__ import annotations

from itertools import permutations

import pytest

from hls.configuration_environment_policy_v0 import (
    CONFIGURATIONS,
    ENVIRONMENTS,
    brute_force_joint_value,
    evaluate_matrix,
    evaluate_policy,
    transition,
)
from hls.configuration_environment_policy_v01 import (
    ENABLED_LEARNING_SCALE,
    EnvironmentSpec,
    argmax_configurations,
    environment_diagnostics,
    environment_specs,
    evaluate_sweep,
    paired_development_rows,
)


def _swap_capabilities(state):
    return tuple((row[1], row[0]) for row in state)


def test_resource_equality_is_preserved_from_v0() -> None:
    totals = {sum(sum(row) for row in state) for state in CONFIGURATIONS.values()}
    by_capability = {tuple(sum(row[task] for row in state) for task in (0, 1)) for state in CONFIGURATIONS.values()}
    assert totals == {3.0}
    assert by_capability == {(1.5, 1.5)}


def test_environment_grid_is_deterministic_and_common_to_all_configurations() -> None:
    specs = environment_specs()
    assert len(specs) == 125
    assert tuple(environment_diagnostics(spec) for spec in specs) == tuple(environment_diagnostics(spec) for spec in specs)
    selected = (EnvironmentSpec(0.5, 0.5, 0.5), EnvironmentSpec(0.25, 0.75, 1.0))
    points = evaluate_sweep(specifications=selected)
    assert points == evaluate_sweep(specifications=selected)
    for specification in selected:
        sequences = {point.diagnostics.sequence for point in points if point.environment == specification}
        assert len(sequences) == 1


def test_nu_changes_only_aggregate_composition_when_chi_is_zero() -> None:
    diagnostics = [environment_diagnostics(EnvironmentSpec(nu, 0.0, 0.5)) for nu in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert [item.aggregate_a_count for item in diagnostics] == [4, 6, 8, 10, 12]
    assert all(item.inter_half_change_count == 0 for item in diagnostics)


def test_chi_preserves_aggregate_composition_and_changes_only_half_allocation_at_interior_nu() -> None:
    diagnostics = [environment_diagnostics(EnvironmentSpec(0.5, chi, 0.5)) for chi in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert {item.aggregate_a_count for item in diagnostics} == {8}
    assert [item.inter_half_change_count for item in diagnostics] == [0, 2, 4, 6, 8]


def test_chi_boundary_clipping_is_explicit_and_never_changes_aggregate_composition() -> None:
    boundary = environment_diagnostics(EnvironmentSpec(0.0, 1.0, 0.5))
    assert boundary.requested_shift == 4
    assert boundary.effective_shift == 2
    assert boundary.aggregate_a_count == 4
    assert (boundary.first_half_a_count, boundary.second_half_a_count) == (0, 4)


def test_rho_preserves_composition_and_change_but_orders_with_weakly_more_persistence() -> None:
    diagnostics = [environment_diagnostics(EnvironmentSpec(0.5, 0.5, rho)) for rho in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert {(item.first_half_a_count, item.second_half_a_count) for item in diagnostics} == {(2, 6)}
    persistence = [item.adjacent_same_pairs for item in diagnostics]
    assert persistence == sorted(persistence)


def test_dp_dominates_greedy_and_disabled_learning_is_identity() -> None:
    specs = (EnvironmentSpec(0.5, 0.5, 0.5), EnvironmentSpec(0.25, 0.75, 1.0))
    for enabled in (True, False):
        for point in evaluate_sweep(development_enabled=enabled, specifications=specs):
            assert point.joint_dp.value >= point.greedy.value - 1e-12
            if not enabled:
                for agent in range(3):
                    for task in range(2):
                        assert transition(CONFIGURATIONS[point.configuration], agent, task, 0.0) == CONFIGURATIONS[point.configuration]


def test_dp_matches_independent_brute_force_on_small_known_sequence() -> None:
    sequence = environment_diagnostics(EnvironmentSpec(0.5, 0.5, 0.5)).sequence[:5]
    value = evaluate_policy(CONFIGURATIONS["DIVERSE"], sequence, ENABLED_LEARNING_SCALE, "JOINT_DP").value
    assert value == pytest.approx(brute_force_joint_value(CONFIGURATIONS["DIVERSE"], sequence, ENABLED_LEARNING_SCALE))


def test_v0_reference_points_are_unchanged() -> None:
    matrix = evaluate_matrix(learning_scale=0.5, development_enabled=True)
    values = {(point.configuration, point.environment): point.joint_dp.value for point in matrix}
    assert values[("GENERALIST", "E0_STABLE_BALANCED")] == pytest.approx(3.640625)
    assert values[("SPECIALIST", "E1_STABLE_SKEWED")] == pytest.approx(6.0)
    assert values[("DIVERSE", "E2_SHIFT")] == pytest.approx(4.9124)
    assert ENVIRONMENTS["E2_SHIFT"] == (0, 0, 0, 1, 1, 1)


def test_worker_permutation_invariance() -> None:
    state = CONFIGURATIONS["DIVERSE"]
    sequence = environment_diagnostics(EnvironmentSpec(0.75, 0.5, 0.75)).sequence
    baseline = evaluate_policy(state, sequence, ENABLED_LEARNING_SCALE, "JOINT_DP").value
    for permutation in permutations(range(3)):
        permuted = tuple(state[index] for index in permutation)
        assert evaluate_policy(permuted, sequence, ENABLED_LEARNING_SCALE, "JOINT_DP").value == pytest.approx(baseline)


def test_a_b_duality_of_fixed_sequence_evaluation() -> None:
    state = CONFIGURATIONS["DIVERSE"]
    sequence = environment_diagnostics(EnvironmentSpec(0.25, 0.5, 0.25)).sequence
    dual_sequence = tuple(1 - task for task in sequence)
    dual_state = _swap_capabilities(state)
    for policy in ("GREEDY_USE", "JOINT_DP"):
        original = evaluate_policy(state, sequence, ENABLED_LEARNING_SCALE, policy)
        dual = evaluate_policy(dual_state, dual_sequence, ENABLED_LEARNING_SCALE, policy)
        assert dual.value == pytest.approx(original.value)


def test_development_ledger_and_regime_map_preserve_complete_ties() -> None:
    specs = (EnvironmentSpec(0.5, 0.5, 0.5),)
    enabled = evaluate_sweep(specifications=specs)
    disabled = evaluate_sweep(development_enabled=False, specifications=specs)
    rows = paired_development_rows(enabled, disabled)
    assert len(rows) == 3
    assert all(row["P"] - row["P0"] == pytest.approx(row["L"]) for row in rows)
    mapping = argmax_configurations(enabled)
    assert mapping[0]["argmax_configurations"]
