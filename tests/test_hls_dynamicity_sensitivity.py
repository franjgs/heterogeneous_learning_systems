from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.run_hls_dynamicity_sensitivity import (
    BASE_COMPETENCE,
    CONDITIONS,
    EVAL_SEEDS,
    PERMUTATION_TO_ID,
    POLICIES,
    TRAIN_SEEDS,
    _potential_uniforms,
    _fit_fixed_map,
    _oracle_matches,
    competence_path,
    evaluate_episode,
    preflight,
)


def test_dynamicity_configuration_is_bounded_seeded_and_same_initial_state():
    for condition, spec in CONDITIONS.items():
        regimes_a, matrices_a = competence_path(condition, 8200, 300)
        regimes_b, matrices_b = competence_path(condition, 8200, 300)
        assert regimes_a == regimes_b
        assert matrices_a == matrices_b
        assert matrices_a[0] == BASE_COMPETENCE
        assert all(0.0 <= value <= 1.0 for matrix in matrices_a
                   for row in matrix for value in row)
        if condition == "D0":
            assert not any(regimes_a)
        else:
            assert spec["amplitude"] > 0
            assert spec["mean_dwell_periods"] == round(1 / spec["switch_probability"])
    assert competence_path("D1", 8200, 300)[1][0] == competence_path("D2", 8200, 300)[1][0]


def test_dynamic_regime_changes_the_true_optimal_assignment_by_design():
    checks = preflight()
    assert checks["D1_and_D2_change_oracle_assignment"]
    for condition in ("D1", "D2"):
        regimes = checks["oracle_assignment_by_static_regime"][condition]
        assert regimes["stable"]["matching"] != regimes["shifted"]["matching"]
        path, matrices = competence_path(condition, 8200, 300)
        optimal = tuple(_oracle_matches(matrix) for matrix in matrices)
        regime_changes = sum(path[t] != path[t - 1] for t in range(1, len(path)))
        assert sum(optimal[t] != optimal[t - 1] for t in range(1, len(optimal))) == regime_changes


def test_potential_outcomes_are_seeded_and_common_across_conditions():
    assert _potential_uniforms(8200, 30) == _potential_uniforms(8200, 30)
    assert _potential_uniforms(8200, 30) != _potential_uniforms(8201, 30)


def test_train_test_seeds_are_disjoint_and_fixed_map_uses_training_only():
    assert len(EVAL_SEEDS) == 20
    assert len(TRAIN_SEEDS) == 20
    assert not set(EVAL_SEEDS) & set(TRAIN_SEEDS)
    for condition in CONDITIONS:
        mapping, _, _ = _fit_fixed_map(condition)
        assert tuple(sorted(mapping)) == (0, 1, 2)


def test_paired_episode_is_reproducible_and_respects_matching_resources():
    mapping, _, _ = _fit_fixed_map("D2")
    first = evaluate_episode("D2", EVAL_SEEDS[0], mapping, horizon=40)
    second = evaluate_episode("D2", EVAL_SEEDS[0], mapping, horizon=40)
    for key in (
        "regime_path_bits", "regime_switch_periods", "assignment_ids_by_policy",
        "realized_reward_series_by_policy", "expected_reward_series_by_policy",
        "cumulative_realized_reward", "cumulative_pseudo_regret", "resource_use",
    ):
        assert first[key] == second[key]
    assert set(first["resource_use"].values()) == {40 * 3}
    for policy in POLICIES:
        assert len(first["assignment_ids_by_policy"][policy]) == 40
        assert set(first["assignment_ids_by_policy"][policy]) <= set(PERMUTATION_TO_ID.values())
        assert len(first["realized_reward_series_by_policy"][policy]) == 40
    assert all(value >= -1e-12 for value in first["cumulative_pseudo_regret"].values())
    assert sum(map(sum, first["linucb_observation_counts"]["LINUCB_HUNGARIAN"])) == 40 * 3
    assert sum(map(sum, first["linucb_observation_counts"]["LINUCB_GREEDY_ONLINE"])) == 40 * 3


def test_evaluator_oracle_is_optimal_for_each_competence_state():
    _, matrices = competence_path("D2", 8311, 25)
    for matrix in matrices:
        selected = _oracle_matches(matrix)
        selected_value = sum(matrix[i][k] for i, k in selected)
        exhaustive = max(
            sum(matrix[permutation[k]][k] for k in range(3))
            for permutation in PERMUTATION_TO_ID
        )
        assert selected_value == exhaustive

