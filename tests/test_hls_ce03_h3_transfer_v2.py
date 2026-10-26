from dataclasses import replace
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "experiments/synthetic/hls_ce03_h3_transfer_v2.py"
SPEC = importlib.util.spec_from_file_location("hls_ce03_h3_transfer_v2_tested", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def _small_config():
    return replace(
        MODULE.CONFIG,
        train_n=80,
        validation_n=30,
        test_n=40,
        logistic_max_iter=80,
        forest_trees=5,
        mlp_max_iter=30,
    )


def test_new_t3_transfer_set_is_1000_binary_examples_and_disjoint():
    config = _small_config()
    tasks = MODULE.BASE.generate_tasks(0, config)
    transfer, stream_seed = MODULE.generate_new_t3_transfer_data(0, config)
    MODULE.check_transfer_split_disjoint(tasks, transfer)
    assert transfer.X.shape == (1000, config.n_features)
    assert transfer.y.shape == (1000,)
    assert set(np.unique(transfer.y)) == {0, 1}
    assert isinstance(stream_seed, int)


def test_common_budget_targets_use_same_inputs_with_direct_soft_and_permuted_labels():
    labels = np.array([0.0, 1.0, 0.0, 1.0])
    teacher = np.array([0.1, 0.8, 0.4, 0.7])
    permutation = np.array([2, 0, 3, 1])
    targets = MODULE.common_budget_targets(labels, teacher, permutation)
    assert set(targets) == {"C1_direct_labels", "C2_A3_distillation", "C3_permuted_A3_distillation"}
    np.testing.assert_array_equal(targets["C1_direct_labels"], labels)
    np.testing.assert_array_equal(targets["C2_A3_distillation"], teacher)
    np.testing.assert_array_equal(targets["C3_permuted_A3_distillation"], teacher[permutation])
    np.testing.assert_array_equal(np.sort(targets["C3_permuted_A3_distillation"]), np.sort(targets["C2_A3_distillation"]))
    assert not np.array_equal(targets["C3_permuted_A3_distillation"], targets["C2_A3_distillation"])


def test_c3_uses_c2_inputs_and_records_reproducible_per_seed_permutation(monkeypatch):
    config = _small_config()
    tasks = MODULE.BASE.generate_tasks(4, config)
    agents = MODULE.BASE.fit_initial_agents(tasks, 4, config)
    transfer, _ = MODULE.generate_new_t3_transfer_data(4, config, n=35)
    captured = {}
    original_fit = MODULE.fit_common_budget_update

    def capture_fit(initial_a1, split, target, fit_config):
        condition_index = len(captured)
        captured[condition_index] = {
            "X": split.X.copy(),
            "target": np.asarray(target).copy(),
            "coef_before": initial_a1.estimator.coef_.copy(),
            "config": fit_config,
        }
        return original_fit(initial_a1, split, target, fit_config)

    monkeypatch.setattr(MODULE, "fit_common_budget_update", capture_fit)
    _, metadata = MODULE.prepare_updates(agents, transfer, 4, config)
    c1, c2, c3 = (captured[index] for index in range(3))

    # All treatments see the same exact input rows and frozen A1 initialization.
    np.testing.assert_array_equal(c2["X"], c3["X"])
    np.testing.assert_array_equal(c1["X"], c2["X"])
    np.testing.assert_array_equal(c2["coef_before"], c3["coef_before"])
    assert c2["config"] is c3["config"]
    # C3 changes only the row-to-probability correspondence; the donor targets remain intact.
    np.testing.assert_array_equal(np.sort(c2["target"]), np.sort(c3["target"]))
    assert not np.array_equal(c2["target"], c3["target"])

    recorded_permutation = np.asarray(metadata["permutation"], dtype=int)
    assert metadata["c3_permutation_seed"] == MODULE._permutation_seed(4)
    np.testing.assert_array_equal(
        recorded_permutation,
        np.random.default_rng(metadata["c3_permutation_seed"]).permutation(len(transfer.y)),
    )
    assert MODULE._permutation_seed(4) != MODULE._permutation_seed(5)
    assert not np.array_equal(
        recorded_permutation,
        np.random.default_rng(MODULE._permutation_seed(5)).permutation(len(transfer.y)),
    )


def test_all_three_updates_use_same_optimizer_and_weighted_row_budget():
    config = _small_config()
    tasks = MODULE.BASE.generate_tasks(1, config)
    agents = MODULE.BASE.fit_initial_agents(tasks, 1, config)
    transfer, _ = MODULE.generate_new_t3_transfer_data(1, config, n=35)
    original_coef = agents[MODULE.AGENTS[0]].estimator.coef_.copy()
    updates, metadata = MODULE.prepare_updates(agents, transfer, 1, config)
    assert set(updates) == set(MODULE.CONDITIONS[1:])
    budget = metadata["optimization_budget"]
    assert budget["same_examples"] == 35
    assert budget["same_weighted_rows_per_pass"] == 70
    assert budget["same_solver"] and budget["same_C"] and budget["same_max_iter_cap"]
    iteration_counts = set()
    for condition, updated in updates.items():
        assert isinstance(updated.estimator, MODULE.BASE.LogisticRegression)
        assert updated.estimator.max_iter == agents[MODULE.AGENTS[0]].estimator.max_iter
        detail = metadata["conditions"][condition]
        assert detail["original_examples"] == 35
        assert detail["weighted_rows_per_pass"] == 70
        assert detail["sample_weight_sum"] == pytest.approx(35)
        assert 0 < detail["optimizer_iterations"] <= detail["max_iter_cap"]
        iteration_counts.add(detail["optimizer_iterations"])
    np.testing.assert_array_equal(agents[MODULE.AGENTS[0]].estimator.coef_, original_coef)
    assert len(iteration_counts) >= 1


def test_validation_utilities_enumerate_six_and_choose_validation_optimum():
    task_for_agent = dict(zip(MODULE.AGENTS, MODULE.TASKS))
    metrics = {
        agent: {
            task: {"accuracy": 0.9 if task_for_agent[agent] == task else 0.4,
                   "log_loss": 0.2 if task_for_agent[agent] == task else 0.8}
            for task in MODULE.TASKS
        }
        for agent, task in zip(MODULE.AGENTS, MODULE.TASKS)
    }
    utilities = MODULE.assignment_utilities(metrics)
    assert len(utilities) == 6
    chosen = MODULE.BASE.select_assignment(MODULE.BASE._loss_matrix(metrics))
    assert tuple(chosen) == MODULE.AGENTS
    assert utilities[0]["mean_validation_accuracy"] == pytest.approx(0.9)


def test_small_seed_run_records_full_condition_matrices_and_no_duplicate_c0_readaptation():
    run = MODULE._make_seed_run(2, _small_config(), transfer_n=35)
    assert set(run["test_agent_task_matrices"]) == set(MODULE.CONDITIONS)
    for condition in MODULE.CONDITIONS:
        assert set(run["test_agent_task_matrices"][condition]) == set(MODULE.AGENTS)
        for agent in MODULE.AGENTS:
            assert set(run["test_agent_task_matrices"][condition][agent]) == set(MODULE.TASKS)
    assert set(run["validation_assignment_utilities_all_six"]) == set(MODULE.CONDITIONS)
    assert all(len(rows) == 6 for rows in run["validation_assignment_utilities_all_six"].values())
    assert run["C0_readapted_assignment_alias"] == "O0_fixed_validation_selected"
    assert "C0_no_update" not in run["readapted_team_results"]
    assert set(run["readapted_team_results"]) == set(MODULE.CONDITIONS[1:])
    assert "true labels" in run["condition_interpretation_caveat"]
    o0 = run["O0_fixed_validation_selected"]
    val_utilities_c0 = run["validation_assignment_utilities_all_six"]["C0_no_update"]
    assert any(row["assignment_by_task"] == o0 and row["mean_validation_accuracy"] == max(
        item["mean_validation_accuracy"] for item in val_utilities_c0
    ) for row in val_utilities_c0)
    for condition, selected in run["readapted_assignment_by_condition_validation_selected"].items():
        utilities = run["validation_assignment_utilities_all_six"][condition]
        assert any(row["assignment_by_task"] == selected and row["mean_validation_accuracy"] == max(
            item["mean_validation_accuracy"] for item in utilities
        ) for row in utilities)


def test_paired_summary_uses_seed_level_differences_and_documents_c2_c1_caveat():
    runs = []
    for seed in range(20):
        cells = {}
        for condition_index, condition in enumerate(MODULE.CONDITIONS):
            cells[condition] = {
                "A1_logistic": {task: {"accuracy": 0.5 + 0.01 * condition_index, "log_loss": 0.7 - 0.02 * condition_index}
                                for task in MODULE.TASKS}
            }
        fixed = {
            condition: {"weighted_accuracy": 0.6 + 0.01 * i, "weighted_log_loss": 0.8 - 0.02 * i}
            for i, condition in enumerate(MODULE.CONDITIONS)
        }
        readapted = {
            condition: {"weighted_accuracy": 0.61 + 0.01 * i, "weighted_log_loss": 0.79 - 0.02 * i}
            for i, condition in enumerate(MODULE.CONDITIONS[1:])
        }
        update_details = {
            condition: {"fit_seconds": 0.01 + i * 0.001, "optimizer_iterations": 5 + i}
            for i, condition in enumerate(MODULE.CONDITIONS[1:], start=1)
        }
        runs.append({"seed": seed, "test_agent_task_matrices": cells,
                     "fixed_O0_team_results": fixed, "readapted_team_results": readapted,
                     "updates": {"conditions": update_details}})
    summary = MODULE.summarize_runs(runs)
    contrast = summary["collective_fixed_O0_pairwise_accuracy_differences"]["C1_direct_labels_minus_C2_A3_distillation"]
    assert contrast["n_seeds"] == 20
    assert contrast["mean"] == pytest.approx(-0.01)
    assert "does not identify" in summary["C2_minus_C1_interpretation"]


def test_campaign_guard_rejects_nonprotocol_transfer_size_before_creating_output(tmp_path):
    output = tmp_path / "must_not_be_created"
    with pytest.raises(ValueError, match="exactly 1,000"):
        MODULE.run_campaign(transfer_n=999, output_dir=output)
    assert not output.exists()
