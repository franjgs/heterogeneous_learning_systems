from __future__ import annotations

import sys
from inspect import signature
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments import run_hls_dynamicity_information_ablation as ablation
from experiments import run_hls_dynamicity_sensitivity as base
from hls.hls_lab_nk_production import p0_rank_nk


def test_information_ablation_preserves_frozen_scenario_and_seeds():
    checks = ablation._preflight()
    assert checks["same_seed_sets_and_scenario_constants"]
    assert base.HORIZON == 300
    assert base.EVAL_SEEDS == tuple(range(8200, 8220))
    assert base.CONDITIONS == {
        "D0": {"amplitude": 0.0, "mean_dwell_periods": None, "switch_probability": 0.0},
        "D1": {"amplitude": 0.15, "mean_dwell_periods": 100, "switch_probability": 0.01},
        "D2": {"amplitude": 0.30, "mean_dwell_periods": 25, "switch_probability": 0.04},
    }


def test_p0_uses_existing_rank_over_only_feasible_perfect_matchings():
    competence = base.competence_path("D2", 8200, 300)[1][81]
    matches = ablation._p0_matching(competence)
    assert len(matches) == 3
    assert len({agent for agent, _ in matches}) == 3
    assert len({task for _, task in matches}) == 3
    selected = next(action for action in ablation.FEASIBLE_MATCHINGS
                    if all(action[i][k] == float((i, k) in matches)
                           for i in range(3) for k in range(3)))
    assert p0_rank_nk(selected, competence, ablation.P0_PROBLEM) == max(
        p0_rank_nk(action, competence, ablation.P0_PROBLEM)
        for action in ablation.FEASIBLE_MATCHINGS
    )
    assert sum(competence[i][k] for i, k in matches) == sum(
        competence[i][k] for i, k in base._oracle_matches(competence)
    )


def test_ablated_context_excludes_competence_but_keeps_task_identity():
    contexts = ablation._task_only_contexts()
    assert len(contexts) == 3 and all(len(row) == 3 for row in contexts)
    assert all(len(context) == 3 for row in contexts for context in row)
    assert contexts[0] == contexts[1] == contexts[2]
    assert contexts[0] == ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def test_short_episode_is_reproducible_paired_and_resource_feasible():
    mapping, _, _ = base._fit_fixed_map("D1")
    first = ablation.evaluate_episode("D1", base.EVAL_SEEDS[0], mapping, horizon=40)
    second = ablation.evaluate_episode("D1", base.EVAL_SEEDS[0], mapping, horizon=40)
    for key in (
        "regime_path_bits", "regime_switch_periods", "assignment_path_code_by_policy",
        "reward_digit_series_by_policy", "cumulative_realized_reward",
        "cumulative_expected_reward", "cumulative_pseudo_regret", "resource_use",
    ):
        assert first[key] == second[key]
    assert set(first["resource_use"].values()) == {120}
    assert all(len(path) == 40 for path in first["assignment_path_code_by_policy"].values())
    assert all(len(path) == 40 for path in first["reward_digit_series_by_policy"].values())
    assert all(all("0" <= digit <= "5" for digit in path)
               for path in first["assignment_path_code_by_policy"].values())
    assert all(all(0 <= int(digit) <= 3 for digit in path)
               for path in first["reward_digit_series_by_policy"].values())
    assert sum(map(sum, first["linucb_observation_counts"][
        "LINUCB_HUNGARIAN_FULL_CONTEXT"])) == 120
    assert sum(map(sum, first["linucb_observation_counts"][
        "LINUCB_HUNGARIAN_NO_COMPETENCE"])) == 120
    assert all(value >= -1e-10 for value in first["cumulative_pseudo_regret"].values())


def test_learners_receive_only_selected_feedback_and_p0_has_no_learning_state():
    competence = base.competence_path("D1", 8200, 2)[1][0]
    contexts = tuple(tuple((competence[i][k],) for k in range(3)) for i in range(3))
    model = ablation.PairwiseLinUCBAdapterNK(3, 3, 1, ablation.ALPHA)
    before = model.observation_counts
    selected = ((0, 0), (1, 1), (2, 2))
    model.update_selected(selected, contexts, {pair: 0.5 for pair in selected})
    after = model.observation_counts
    assert sum(map(sum, before)) == 0
    assert sum(map(sum, after)) == 3
    assert after == ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    assert not hasattr(ablation.P0, "observation_counts")
    assert not hasattr(ablation.P0, "update")
    assert tuple(signature(ablation.P0.choose).parameters) == (
        "feasible_actions", "estimated_competencies", "problem",
    )
