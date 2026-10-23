from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.run_hls_linucb_bipartite_hybrid import (
    ASSIGNER,
    EVAL_SEEDS,
    ORG,
    PROBLEM,
    TRAIN_SEEDS,
    contexts_for_mode,
    evaluate_episode,
    greedy_from_scores,
    mode_trajectory,
    reward_coefficients,
    true_reward_matrix,
)
from hls.hls_lab_nk_linucb_assignment import PairwiseLinUCBAdapterNK
from hls.linucb import alpha_from_delta


def test_pair_score_adapter_matches_uninformative_linucb_confidence_scores():
    model = PairwiseLinUCBAdapterNK(2, 2, 4, alpha=0.7)
    contexts = (
        ((1.0, 1.0, 0.0, 0.0), (1.0, 1.0, 0.0, 0.0)),
        ((1.0, 1.0, 0.0, 0.0), (1.0, 1.0, 0.0, 0.0)),
    )
    scores = model.score_matrix(contexts)
    expected = 0.7 * (2.0 ** 0.5)
    assert all(score == pytest.approx(expected) for row in scores for score in row)
    assert model.observation_counts == ((0, 0), (0, 0))


def test_only_selected_pair_models_receive_the_observed_linucb_update():
    model = PairwiseLinUCBAdapterNK(2, 2, 4, alpha=0.5)
    contexts = (
        ((1.0, 1.0, 0.0, 0.0), (1.0, 1.0, 0.0, 0.0)),
        ((1.0, 1.0, 0.0, 0.0), (1.0, 1.0, 0.0, 0.0)),
    )
    before = model.design_matrices
    selected = ((0, 1),)
    model.update_selected(selected, contexts, {(0, 1): 0.4})
    after = model.design_matrices
    assert model.observation_counts == ((0, 1), (0, 0))
    assert after[0][1][0][0] == pytest.approx(before[0][1][0][0] + 1.0)
    assert model.coefficient_estimates[0][1][0] == pytest.approx(0.4 / 3.0)
    assert after[0][0] == before[0][0]
    assert after[1] == before[1]
    with pytest.raises(ValueError, match="exactly match selected"):
        model.update_selected(selected, contexts, {(0, 1): 0.4, (1, 0): 0.9})


def test_context_and_true_reward_generator_are_reproducible_and_bounded():
    assert mode_trajectory(77, 40) == mode_trajectory(77, 40)
    assert reward_coefficients() == reward_coefficients()
    for mode in range(3):
        context = contexts_for_mode(mode)
        assert all(len(context[i][j]) == 4 for i in range(3) for j in range(3))
        rewards = true_reward_matrix(mode)
        assert all(0.0 <= reward <= 1.0 for row in rewards for reward in row)


def test_evaluation_seeds_are_independent_from_fixed_mapping_training_seeds():
    assert set(TRAIN_SEEDS).isdisjoint(EVAL_SEEDS)


def test_evaluation_replays_and_records_all_constraints_and_oracle_regret():
    fixed_map = (0, 1, 2)
    first = evaluate_episode(EVAL_SEEDS[0], fixed_map)
    second = evaluate_episode(EVAL_SEEDS[0], fixed_map)
    for key in ("mode_sequence", "cumulative_reward", "cumulative_oracle_regret",
                "resource_use", "final_hybrid_coefficients", "final_hybrid_observation_counts",
                "final_greedy_coefficients", "final_greedy_observation_counts"):
        assert first[key] == second[key]
    assert first["resource_use"] == {policy: 3 * 36 for policy in first["resource_use"]}
    assert all(value >= -1e-12 for value in first["cumulative_oracle_regret"].values())
    assert len(first["trace"]) == 36
    previous_counts = [[0] * 3 for _ in range(3)]
    for period, row in enumerate(first["trace"]):
        hybrid_pairs = tuple((next(i for i, agent in enumerate(("agent_0", "agent_1", "agent_2"))
                                   if agent == edge["agent"]),
                              next(j for j, task in enumerate(("task_0", "task_1", "task_2"))
                                   if task == edge["task"]))
                             for edge in row["assignments"]["LINUCB_HUNGARIAN"])
        scores = row["linucb_hybrid_scores_before"]
        optimal_score_assignment = ASSIGNER.optimize(scores, ORG, PROBLEM).matches
        assert set(hybrid_pairs) == set(optimal_score_assignment)
        assert tuple(sorted(greedy_from_scores(scores))) == tuple(sorted(
            (next(i for i, agent in enumerate(("agent_0", "agent_1", "agent_2")) if agent == edge["agent"]),
             next(j for j, task in enumerate(("task_0", "task_1", "task_2")) if task == edge["task"]))
            for edge in row["assignments"]["GREEDY_SAME_LINUCB_SCORES"]
        ))
        assert len(hybrid_pairs) == 3
        assert len({i for i, _ in hybrid_pairs}) == 3
        assert len({j for _, j in hybrid_pairs}) == 3
        hybrid_observed = {(next(i for i, agent in enumerate(("agent_0", "agent_1", "agent_2"))
                                  if agent == entry["agent"]),
                            next(j for j, task in enumerate(("task_0", "task_1", "task_2"))
                                 if task == entry["task"]))
                           for entry in row["observed_rewards_hybrid_selected_only"]}
        assert hybrid_observed == set(hybrid_pairs)
        counts = row["hybrid_observation_counts_after"]
        assert sum(map(sum, counts)) == 3 * (period + 1)
        for i in range(3):
            for j in range(3):
                assert counts[i][j] - previous_counts[i][j] == int((i, j) in hybrid_pairs)
        previous_counts = counts


def test_adapter_uses_the_existing_published_linucb_delta_parameter():
    assert alpha_from_delta(0.05) > 1.0
