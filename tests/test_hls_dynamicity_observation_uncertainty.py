from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments import run_hls_dynamicity_observation_uncertainty as experiment
from experiments import run_hls_dynamicity_sensitivity as base


def test_observation_noise_is_reproducible_separate_and_shared_seed_field():
    first = experiment.standard_normal_observation_noise(8200, 12)
    second = experiment.standard_normal_observation_noise(8200, 12)
    other = experiment.standard_normal_observation_noise(8201, 12)
    assert first == second
    assert first != other
    assert experiment.OBSERVATION_NOISE_XOR != 0xA11CE
    assert base._potential_uniforms(8200, 12) != first


def test_observed_competence_sigma_zero_identity_and_clipping():
    truth = ((0.0, 0.5, 1.0), (0.2, 0.7, 0.9), (0.1, 0.4, 0.8))
    noise = ((-3.0, 0.5, 3.0), (1.0, -1.0, 0.2), (0.0, 0.0, 0.0))
    assert experiment.observed_competence(truth, noise, 0.0) == truth
    observed = experiment.observed_competence(truth, noise, 0.2)
    assert observed[0] == (0.0, 0.6, 1.0)
    assert all(0.0 <= value <= 1.0 for row in observed for value in row)


def test_p0_and_linucb_share_the_existing_one_to_one_budget_feasible_set():
    assert len(experiment.MATCHINGS) == 34
    assert len(set(experiment.MATCHINGS)) == 34
    for matching in experiment.MATCHINGS:
        assert len(matching) <= 3
        assert len({agent for agent, _ in matching}) == len(matching)
        assert len({task for _, task in matching}) == len(matching)
        assert all(0 <= agent < 3 and 0 <= task < 3 for agent, task in matching)
    assert experiment.MATCHINGS[:6] == tuple(
        tuple(sorted((permutation[task], task) for task in range(3)))
        for permutation in base.PERMUTATIONS
    )


def test_frozen_scenario_paths_are_unchanged_and_shared_across_policies():
    for condition in base.CONDITIONS:
        regimes, competence = base.competence_path(condition, 8200, 30)
        again_regimes, again_competence = base.competence_path(condition, 8200, 30)
        assert regimes == again_regimes
        assert competence == again_competence
    z = experiment.standard_normal_observation_noise(8200, 30)
    true = base.competence_path("D2", 8200, 30)[1]
    obs_p0 = experiment.observed_competence(true[10], z[10], 0.1)
    obs_linucb = experiment.observed_competence(true[10], z[10], 0.1)
    assert obs_p0 == obs_linucb
    assert experiment.observed_competence(true[10], z[10], 0.0) == true[10]


def test_uncertain_observation_episode_is_reproducible_and_feasible():
    mapping, _, _ = base._fit_fixed_map("D1")
    first = experiment.evaluate_episode("D1", 0.1, base.EVAL_SEEDS[0], mapping, horizon=40)
    second = experiment.evaluate_episode("D1", 0.1, base.EVAL_SEEDS[0], mapping, horizon=40)
    for key in (
        "regime_path_bits", "regime_switch_periods", "assignment_path_code_by_policy",
        "realized_reward_digit_series_by_policy", "cumulative_realized_reward",
        "cumulative_expected_reward", "cumulative_pseudo_regret", "resource_use",
        "observation_rmse", "observation_clipped_fraction",
    ):
        assert first[key] == second[key]
    assert first["resource_use"]["FIXED_OPT_TRAIN"] == 120
    assert first["resource_use"]["DYNAMIC_ORACLE_TRUE_EVALUATOR_ONLY"] == 120
    assert all(value <= 120 for value in first["resource_use"].values())
    assert all(len(path) == 40 for path in first["assignment_path_code_by_policy"].values())
    assert all(all(char in experiment.MATCHING_CODE_ALPHABET for char in path)
               for path in first["assignment_path_code_by_policy"].values())
    assert all(all(0 <= int(digit) <= 3 for digit in path)
               for path in first["realized_reward_digit_series_by_policy"].values())
    assert all(value >= -1e-10 for value in first["cumulative_pseudo_regret"].values())
    assert sum(map(sum, first["linucb_observation_counts"])) == first["resource_use"][
        "LINUCB_HUNGARIAN_OBSERVED"
    ]


def test_policies_never_receive_true_matrix_or_future_state_as_arguments():
    import inspect
    assert tuple(inspect.signature(experiment._p0_reactive_matches).parameters) == (
        "competence_observation",
    )
    assert tuple(inspect.signature(experiment.prior.PairwiseLinUCBAdapterNK.score_matrix).parameters) == (
        "self", "contexts",
    )
    assert tuple(inspect.signature(experiment.prior.PairwiseLinUCBAdapterNK.update_selected).parameters) == (
        "self", "selected_pairs", "contexts", "observed_rewards",
    )
