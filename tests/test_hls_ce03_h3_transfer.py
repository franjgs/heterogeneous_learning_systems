from dataclasses import replace
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "experiments/synthetic/hls_ce03_h3_transfer.py"
SPEC = importlib.util.spec_from_file_location("hls_ce03_h3_transfer_tested", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

(
    AGENTS,
    TASKS,
    ExperimentConfig,
    fit_initial_agents,
    fit_transfer_controls,
    distill_a1,
    generate_tasks,
    paired_seed_summary,
    select_assignment,
    soft_target_expansion,
) = (
    MODULE.AGENTS, MODULE.TASKS, MODULE.ExperimentConfig, MODULE.fit_initial_agents,
    MODULE.fit_transfer_controls, MODULE.distill_a1, MODULE.generate_tasks,
    MODULE.paired_seed_summary, MODULE.select_assignment, MODULE.soft_target_expansion,
)
summarize_campaign = MODULE.summarize_campaign
unique_condition_results = MODULE._unique_condition_results


def _small_config():
    return ExperimentConfig(
        train_n=80,
        validation_n=30,
        test_n=40,
        logistic_max_iter=60,
        forest_trees=5,
        mlp_max_iter=30,
    )


def test_task_generation_shapes_binary_labels_and_reproducibility():
    config = _small_config()
    first = generate_tasks(4, config)
    second = generate_tasks(4, config)
    assert tuple(first) == TASKS
    for task in TASKS:
        for split_name, expected_n in (("train", 80), ("validation", 30), ("test", 40)):
            a = getattr(first[task], split_name)
            b = getattr(second[task], split_name)
            assert a.X.shape == (expected_n, 10)
            assert a.y.shape == (expected_n,)
            assert set(np.unique(a.y)) == {0, 1}
            np.testing.assert_array_equal(a.X, b.X)
            np.testing.assert_array_equal(a.y, b.y)


def test_task_and_split_random_streams_are_distinct():
    tasks = generate_tasks(5, _small_config())
    assert not np.array_equal(tasks[TASKS[0]].train.X, tasks[TASKS[0]].validation.X)
    assert not np.array_equal(tasks[TASKS[0]].train.X, tasks[TASKS[1]].train.X)


def test_soft_target_expansion_preserves_expected_bernoulli_mass():
    X = np.array([[1.0, 2.0], [3.0, 4.0]])
    q = np.array([0.25, 0.8])
    expanded_X, labels, weights = soft_target_expansion(X, q)
    assert expanded_X.shape == (4, 2)
    np.testing.assert_array_equal(expanded_X, np.repeat(X, 2, axis=0))
    np.testing.assert_array_equal(labels, [0, 1, 0, 1])
    np.testing.assert_allclose(weights.reshape(2, 2).sum(axis=1), 1.0)
    np.testing.assert_allclose(weights.reshape(2, 2)[:, 1], q)
    assert weights.sum() == pytest.approx(len(X))


def test_soft_target_expansion_rejects_invalid_probabilities():
    with pytest.raises(ValueError):
        soft_target_expansion(np.ones((2, 1)), np.array([0.2, 1.2]))


def test_assignment_enumerates_valid_one_to_one_mapping_and_ties_are_deterministic():
    tied = {task: {agent: 0.5 for agent in AGENTS} for task in TASKS}
    assert select_assignment(tied) == AGENTS
    matrix = {
        TASKS[0]: {AGENTS[0]: 0.0, AGENTS[1]: 0.2, AGENTS[2]: 0.3},
        TASKS[1]: {AGENTS[0]: 0.3, AGENTS[1]: 0.0, AGENTS[2]: 0.2},
        TASKS[2]: {AGENTS[0]: 0.2, AGENTS[1]: 0.3, AGENTS[2]: 0.0},
    }
    assert select_assignment(matrix) == AGENTS


def test_assignment_rejects_missing_or_nonfinite_validation_values():
    with pytest.raises(ValueError):
        select_assignment({})
    invalid = {task: {agent: 0.0 for agent in AGENTS} for task in TASKS}
    invalid[TASKS[0]][AGENTS[0]] = np.nan
    with pytest.raises(ValueError):
        select_assignment(invalid)


def test_small_fixture_fits_models_and_control_data_are_aligned():
    config = _small_config()
    tasks = generate_tasks(6, config)
    agents = fit_initial_agents(tasks, 6, config)
    assert tuple(agents) == AGENTS
    assert {agent.primary_task for agent in agents.values()} == {"pooled_T1_T2_T3"}
    for agent in agents.values():
        np.testing.assert_array_equal(agent.scaler.mean_, agents[AGENTS[0]].scaler.mean_)
    teacher_p = agents[AGENTS[2]].predict_proba(tasks[TASKS[2]].train.X)[:, 1]
    controls = fit_transfer_controls(agents[AGENTS[0]], tasks, teacher_p, 6, config)
    assert set(controls) == {
        "control1_and_control2_identical_hard_label_refit",
        "control3_permuted_teacher",
    }
    for agent, metadata in controls.values():
        assert agent.agent_id == AGENTS[0]
        assert metadata["fit_seconds"] >= 0
        assert metadata["optimizer_iterations"] > 0
    perm = controls["control3_permuted_teacher"][1]["teacher_probability_permutation"]
    assert sorted(perm) == list(range(config.train_n))


def test_distillation_is_real_refit_and_does_not_mutate_initial_models():
    config = _small_config()
    tasks = generate_tasks(7, config)
    agents = fit_initial_agents(tasks, 7, config)
    initial_params = agents[AGENTS[0]].estimator.coef_.copy()
    donor_params = agents[AGENTS[2]].estimator.coefs_[0].copy()
    transferred, metadata = distill_a1(agents, tasks, 7, config)
    assert transferred is not agents[AGENTS[0]]
    assert transferred.estimator is not agents[AGENTS[0]].estimator
    np.testing.assert_array_equal(agents[AGENTS[0]].estimator.coef_, initial_params)
    np.testing.assert_array_equal(agents[AGENTS[2]].estimator.coefs_[0], donor_params)
    assert metadata["donor"] == AGENTS[2]
    assert metadata["receiver"] == AGENTS[0]
    assert metadata["task"] == TASKS[2]
    assert metadata["total_transfer_seconds"] >= 0
    assert np.isfinite(metadata["parameters_after"]["coef"]).all()
    assert np.isfinite(metadata["train_log_loss_hard_labels_before"])
    assert np.isfinite(metadata["train_log_loss_hard_labels_after"])


def test_seed_level_paired_summary_uses_seeds_and_reports_signs():
    summary = paired_seed_summary([-0.2, 0.0, 0.1, 0.3])
    assert summary["n_seeds"] == 4
    assert summary["positive_seeds"] == 2
    assert summary["negative_seeds"] == 1
    assert summary["zero_seeds"] == 1
    assert summary["ci95_low"] <= summary["mean"] <= summary["ci95_high"]


def _summary_run(individual_vs_control, individual_vs_initial, fixed_effect, reorg_effect=0.02, seed=0):
    control_accuracy = 0.5
    distilled_accuracy = control_accuracy + individual_vs_control
    before_accuracy = distilled_accuracy - individual_vs_initial
    c0_accuracy = 0.6
    c1_accuracy = c0_accuracy + fixed_effect
    c2_accuracy = c1_accuracy + reorg_effect
    return {
        "seed": seed,
        "A1_individual_test_metrics_after_distillation": {TASKS[2]: {"accuracy": distilled_accuracy}},
        "A1_individual_test_metrics_before": {TASKS[2]: {"accuracy": before_accuracy}},
        "control_test_metrics_A1": {
            "control1_and_control2_identical_hard_label_refit": {
                TASKS[2]: {"accuracy": control_accuracy}
            }
        },
        "conditions_test": {
            "C0_no_transfer_fixed_O0": {"weighted_accuracy": c0_accuracy},
            "C1_transfer_fixed_O0": {"weighted_accuracy": c1_accuracy},
            "C2_transfer_readapted_O1": {"weighted_accuracy": c2_accuracy},
        },
    }


def test_campaign_summary_uses_no_distillation_control_and_keeps_initial_descriptive():
    summary = summarize_campaign([_summary_run(0.04, 0.40, -0.03, seed=seed) for seed in range(20)])
    assert summary["D_individual_transfer_vs_refit_A1_T3"]["mean"] == pytest.approx(0.04)
    assert summary["D_individual_distill_vs_initial_A1_T3_descriptive"]["mean"] == pytest.approx(0.40)


def test_h3_is_supported_only_when_both_paired_ci_directions_hold():
    summary = summarize_campaign([
        _summary_run(0.04, 0.4, -0.03, seed=seed) for seed in range(20)
    ])
    assert summary["H3_point_signs_both_satisfied"]
    assert summary["H3_supported_by_prespecified_CIs"]


def test_c2_c3_reference_is_one_stored_observation():
    conditions = unique_condition_results({"v": 0}, {"v": 1}, {"v": 2})
    assert list(conditions["conditions_test"]) == [
        "C0_no_transfer_fixed_O0", "C1_transfer_fixed_O0", "C2_transfer_readapted_O1"
    ]
    assert len(conditions["conditions_test"]) == 3
    assert conditions["condition_aliases"]["C3_validation_optimum_reference"] == "C2_transfer_readapted_O1"


@pytest.mark.parametrize(
    "individual_vs_control,fixed_effect",
    [(0.0, -0.05), (0.05, 0.0), (-0.01, -0.05), (0.05, 0.01)],
)
def test_h3_is_not_supported_when_either_required_direction_fails(individual_vs_control, fixed_effect):
    summary = summarize_campaign([
        _summary_run(individual_vs_control, 0.5, fixed_effect, seed=seed) for seed in range(20)
    ])
    assert not summary["H3_point_signs_both_satisfied"]
    assert not summary["H3_supported_by_prespecified_CIs"]


def test_h3_point_signs_are_not_mistaken_for_statistical_support():
    individual_effects = [-0.15, -0.10, -0.05, 0.05, 0.10, 0.15] * 3 + [-0.05, 0.05]
    runs = [
        _summary_run(effect, effect + 0.3, -0.03, seed=seed)
        for seed, effect in enumerate(individual_effects)
    ]
    summary = summarize_campaign(runs)
    assert summary["H3_point_signs_both_satisfied"]
    assert not summary["H3_supported_by_prespecified_CIs"]


def test_campaign_configuration_is_fixed_to_seeds_zero_through_nineteen():
    CONFIG = MODULE.CONFIG

    with pytest.raises(ValueError, match="seeds 0 through 19"):
        MODULE.run_campaign(replace(CONFIG, campaign_seeds=(0, 1)), output_dir=Path("unused"))
