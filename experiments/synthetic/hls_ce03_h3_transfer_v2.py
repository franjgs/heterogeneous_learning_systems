"""HLS-CE-03 second-iteration runner; importing this module runs no campaign."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import itertools
import json
import platform
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy
import sklearn


ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = Path(__file__).with_name("hls_ce03_h3_transfer.py")
BASE_SPEC = importlib.util.spec_from_file_location("hls_ce03_h3_v1_base", BASE_PATH)
BASE = importlib.util.module_from_spec(BASE_SPEC)
sys.modules[BASE_SPEC.name] = BASE
BASE_SPEC.loader.exec_module(BASE)

TASKS = BASE.TASKS
AGENTS = BASE.AGENTS
CONFIG = BASE.CONFIG
TRANSFER_N = 1000
CONDITIONS = ("C0_no_update", "C1_direct_labels", "C2_A3_distillation", "C3_permuted_A3_distillation")
RESULTS_DIR = ROOT / "results/experiments/hls_ce03_h3_transfer_v2"
CONTROL_NOTES = {
    "C0_no_update": "A1 remains at its initial fit.",
    "C1_direct_labels": "A1 is warm-start refit on the new T3 examples using their true labels.",
    "C2_A3_distillation": "A1 is warm-start refit on the same new T3 inputs using only A3's soft probabilities.",
    "C3_permuted_A3_distillation": "A1 is warm-start refit on the same new T3 inputs using A3 probabilities permuted across examples.",
}
INTERPRETATION_CAVEAT = (
    "C2-C1 compares teacher-derived soft targets with true labels. By itself it does not identify "
    "positive or negative transfer: the information supplied to the learner differs."
)


def generate_new_t3_transfer_data(seed: int, config=CONFIG, n: int = TRANSFER_N):
    """Generate a separately seeded T3 transfer set outside initial train/validation/test."""
    if n <= 0:
        raise ValueError("transfer example count must be positive")
    transfer_stream_seed = BASE._rng_seed(seed, 2, 3)
    split = BASE._make_split(TASKS[2], n, transfer_stream_seed, config)
    return split, transfer_stream_seed


def check_transfer_split_disjoint(tasks, transfer_split) -> None:
    """Reject exact feature-row overlap with any original task split."""
    transfer_rows = {row.tobytes() for row in np.ascontiguousarray(transfer_split.X)}
    for task_data in tasks.values():
        for name in ("train", "validation", "test"):
            rows = {row.tobytes() for row in np.ascontiguousarray(getattr(task_data, name).X)}
            if transfer_rows.intersection(rows):
                raise ValueError(f"transfer inputs overlap exact feature rows in {name}")


def common_budget_targets(y_true: np.ndarray, teacher_probability: np.ndarray, permutation: np.ndarray):
    """Return targets encoded with identical N examples and 2N weighted rows."""
    y = np.asarray(y_true, dtype=float)
    teacher = np.asarray(teacher_probability, dtype=float)
    order = np.asarray(permutation, dtype=int)
    if y.ndim != 1 or teacher.shape != y.shape or order.shape != y.shape:
        raise ValueError("labels, teacher probabilities, and permutation must have matching vectors")
    if not np.isfinite(y).all() or not np.isin(y, (0.0, 1.0)).all():
        raise ValueError("true labels must be finite binary values")
    if not np.isfinite(teacher).all() or np.any((teacher < 0.0) | (teacher > 1.0)):
        raise ValueError("teacher probabilities must be finite and in [0, 1]")
    if not np.array_equal(np.sort(order), np.arange(len(y))):
        raise ValueError("permutation must be a permutation of all transfer examples")
    return {
        "C1_direct_labels": y.copy(),
        "C2_A3_distillation": teacher.copy(),
        "C3_permuted_A3_distillation": teacher[order].copy(),
    }


def _permutation_seed(seed: int) -> int:
    """Return an independent deterministic stream for this seed's C3 shuffle."""
    return BASE._agent_seed(seed, 0, 303)


def fit_common_budget_update(initial_a1, transfer_split, target_probability, config=CONFIG):
    """Warm-start the same logistic model on a fixed-size weighted binary dataset."""
    if not isinstance(initial_a1.estimator, BASE.LogisticRegression):
        raise TypeError("A1 must remain the original LogisticRegression architecture")
    target = np.asarray(target_probability, dtype=float)
    if target.shape != (len(transfer_split.y),) or not np.isfinite(target).all():
        raise ValueError("target vector must align with transfer examples and be finite")
    if np.any((target < 0.0) | (target > 1.0)):
        raise ValueError("target probabilities must lie in [0, 1]")
    scaled = initial_a1.scaler.transform(transfer_split.X)
    fit_X, fit_y, sample_weight = BASE.soft_target_expansion(scaled, target)
    if fit_X.shape[0] != 2 * len(transfer_split.y) or not np.isclose(sample_weight.sum(), len(transfer_split.y)):
        raise AssertionError("the shared optimizer budget encoding is inconsistent")
    estimator = copy.deepcopy(initial_a1.estimator)
    start = time.perf_counter()
    estimator.fit(fit_X, fit_y, sample_weight=sample_weight)
    elapsed = time.perf_counter() - start
    updated = BASE.FittedAgent(
        initial_a1.agent_id, initial_a1.scaler, estimator, initial_a1.primary_task, elapsed,
    )
    return updated, {
        "fit_seconds": elapsed,
        "optimizer_iterations": int(np.max(estimator.n_iter_)),
        "max_iter_cap": int(estimator.max_iter),
        "solver": estimator.solver,
        "C": float(estimator.C),
        "original_examples": int(len(transfer_split.y)),
        "weighted_rows_per_pass": int(len(fit_y)),
        "sample_weight_sum": float(sample_weight.sum()),
        "target_mean": float(target.mean()),
        "parameters_before": {
            "coef": np.asarray(initial_a1.estimator.coef_).tolist(),
            "intercept": np.asarray(initial_a1.estimator.intercept_).tolist(),
        },
        "parameters_after": {
            "coef": np.asarray(estimator.coef_).tolist(),
            "intercept": np.asarray(estimator.intercept_).tolist(),
        },
    }


def prepare_updates(agents, transfer_split, seed: int, config=CONFIG):
    """Prepare C1-C3 from the same frozen A1, examples, optimizer settings and row budget."""
    teacher = agents[AGENTS[2]]
    donor_start = time.perf_counter()
    teacher_probability = teacher.predict_proba(transfer_split.X)[:, 1]
    donor_inference_seconds = time.perf_counter() - donor_start
    c3_permutation_seed = _permutation_seed(seed)
    permutation = np.random.default_rng(c3_permutation_seed).permutation(len(transfer_split.y))
    targets = common_budget_targets(transfer_split.y, teacher_probability, permutation)
    initial_a1 = agents[AGENTS[0]]
    updates, details = {}, {}
    for condition, target in targets.items():
        updated, metadata = fit_common_budget_update(initial_a1, transfer_split, target, config)
        updates[condition] = updated
        details[condition] = metadata
    return updates, {
        "donor": AGENTS[2], "receiver": AGENTS[0], "task": TASKS[2],
        "teacher_inference_seconds": donor_inference_seconds,
        "c3_permutation_seed": int(c3_permutation_seed),
        "permutation": permutation.tolist(),
        "conditions": details,
        "optimization_budget": {
            "same_model_initialization": True,
            "same_examples": int(len(transfer_split.y)),
            "same_weighted_rows_per_pass": int(2 * len(transfer_split.y)),
            "same_solver": initial_a1.estimator.solver,
            "same_C": float(initial_a1.estimator.C),
            "same_max_iter_cap": int(initial_a1.estimator.max_iter),
            "same_scaler": True,
            "realized_iterations_recorded_per_condition": True,
            "note": "Configured optimization budget and weighted-row workload match; realized convergence iterations and wall time may differ.",
        },
    }


def assignment_utilities(validation_matrix):
    """All six equal-task-weight utilities from a validation agent×task matrix."""
    rows = []
    for assignment in itertools.permutations(AGENTS):
        scores = [validation_matrix[agent][task]["accuracy"] for task, agent in zip(TASKS, assignment)]
        rows.append({
            "assignment_by_task": dict(zip(TASKS, assignment)),
            "mean_validation_accuracy": float(np.mean(scores)),
            "mean_validation_log_loss": float(np.mean([
                validation_matrix[agent][task]["log_loss"] for task, agent in zip(TASKS, assignment)
            ])),
        })
    return rows


def _team_metrics(assignment, matrix):
    return BASE.evaluate_assignment(assignment, matrix)


def _pairwise_differences(condition_values, metric):
    outputs = {}
    for left, right in itertools.combinations(CONDITIONS, 2):
        outputs[f"{left}_minus_{right}"] = {
            "mean": float(np.mean([condition_values[left][i][metric] - condition_values[right][i][metric]
                                   for i in range(len(condition_values[left]))]))
        }
    return outputs


def _paired_seed_summary(values):
    return BASE.paired_seed_summary(list(values), confidence=0.95)


def _make_seed_run(seed: int, config=CONFIG, transfer_n: int = TRANSFER_N):
    tasks = BASE.generate_tasks(seed, config)
    transfer_split, transfer_stream_seed = generate_new_t3_transfer_data(seed, config, transfer_n)
    check_transfer_split_disjoint(tasks, transfer_split)

    initial_fit_start = time.perf_counter()
    initial_agents = BASE.fit_initial_agents(tasks, seed, config)
    initial_fit_seconds = time.perf_counter() - initial_fit_start
    initial_validation, initial_validation_times = BASE.score_matrix(initial_agents, tasks, "validation")
    O0 = BASE.select_assignment(BASE._loss_matrix(initial_validation))
    initial_test, initial_test_times = BASE.score_matrix(initial_agents, tasks, "test")

    updates, update_metadata = prepare_updates(initial_agents, transfer_split, seed, config)
    test_matrices = {"C0_no_update": initial_test}
    validation_matrices = {"C0_no_update": initial_validation}
    validation_times = {"C0_no_update": initial_validation_times}
    test_times = {"C0_no_update": initial_test_times}
    assignments = {"C0_no_update": O0}
    utilities = {"C0_no_update": assignment_utilities(initial_validation)}
    fixed_results = {"C0_no_update": _team_metrics(O0, initial_test)}
    readapted_results = {}

    for condition in CONDITIONS[1:]:
        agents = dict(initial_agents)
        agents[AGENTS[0]] = updates[condition]
        val_matrix, val_times = BASE.score_matrix(agents, tasks, "validation")
        selected = BASE.select_assignment(BASE._loss_matrix(val_matrix))
        test_matrix, test_time = BASE.score_matrix(agents, tasks, "test")
        validation_matrices[condition] = val_matrix
        validation_times[condition] = val_times
        test_matrices[condition] = test_matrix
        test_times[condition] = test_time
        assignments[condition] = selected
        utilities[condition] = assignment_utilities(val_matrix)
        fixed_results[condition] = _team_metrics(O0, test_matrix)
        readapted_results[condition] = _team_metrics(selected, test_matrix)

    return {
        "seed": int(seed),
        "split_sizes": {"per_task_train": config.train_n, "per_task_validation": config.validation_n,
                        "per_task_test": config.test_n, "new_T3_transfer": int(transfer_n)},
        "transfer_split_stream_seed": int(transfer_stream_seed),
        "transfer_split_exact_feature_overlap": False,
        "initial_training": "all agents use same pooled T1/T2/T3 initial training data; the new T3 transfer split is excluded",
        "initial_training_total_seconds": initial_fit_seconds,
        "O0_fixed_validation_selected": dict(zip(TASKS, O0)),
        "readapted_assignment_by_condition_validation_selected": {
            condition: dict(zip(TASKS, assignments[condition])) for condition in CONDITIONS[1:]
        },
        "C0_readapted_assignment_alias": "O0_fixed_validation_selected",
        "validation_agent_task_matrices": validation_matrices,
        "validation_assignment_utilities_all_six": utilities,
        "test_agent_task_matrices": test_matrices,
        "fixed_O0_team_results": fixed_results,
        "readapted_team_results": readapted_results,
        "readapted_C0_alias": "fixed_O0_team_results.C0_no_update",
        "updates": update_metadata,
        "condition_interpretation_caveat": INTERPRETATION_CAVEAT,
        "costs_seconds": {
            "initial_training_total": initial_fit_seconds,
            "teacher_inference_on_new_T3": update_metadata["teacher_inference_seconds"],
            "condition_fit_seconds": {condition: update_metadata["conditions"][condition]["fit_seconds"]
                                       for condition in CONDITIONS[1:]},
            "validation_inference": validation_times,
            "test_inference": test_times,
        },
    }


def summarize_runs(runs):
    if len(runs) != 20 or [run["seed"] for run in runs] != list(range(20)):
        raise ValueError("summary requires exactly the paired seeds 0 through 19 in order")
    output = {"unit": "seed; paired contrasts use the same original train/validation/test sets per seed"}

    def paired(condition_metric, keys):
        values = {condition: [] for condition in CONDITIONS}
        for run in runs:
            for condition in CONDITIONS:
                item = condition_metric(run, condition)
                for key in keys:
                    values[condition].append(item[key])
        return values

    # Individual A1 outcomes are evaluated on the same original held-out task test sets.
    individual = {condition: {task: [] for task in TASKS} for condition in CONDITIONS}
    individual_logloss = {condition: {task: [] for task in TASKS} for condition in CONDITIONS}
    for run in runs:
        for condition in CONDITIONS:
            for task in TASKS:
                cell = run["test_agent_task_matrices"][condition]["A1_logistic"][task]
                individual[condition][task].append(cell["accuracy"])
                individual_logloss[condition][task].append(cell["log_loss"])
    output["individual_A1_accuracy_by_condition_and_task"] = {
        condition: {task: _paired_seed_summary(individual[condition][task]) for task in TASKS}
        for condition in CONDITIONS
    }
    output["individual_A1_log_loss_by_condition_and_task"] = {
        condition: {task: _paired_seed_summary(individual_logloss[condition][task]) for task in TASKS}
        for condition in CONDITIONS
    }
    output["individual_A1_pairwise_accuracy_differences_by_task"] = {
        task: {
            f"{left}_minus_{right}": _paired_seed_summary([
                individual[left][task][i] - individual[right][task][i] for i in range(20)
            ]) for left, right in itertools.combinations(CONDITIONS, 2)
        } for task in TASKS
    }
    output["individual_A1_pairwise_log_loss_differences_by_task"] = {
        task: {
            f"{left}_minus_{right}": _paired_seed_summary([
                individual_logloss[left][task][i] - individual_logloss[right][task][i] for i in range(20)
            ]) for left, right in itertools.combinations(CONDITIONS, 2)
        } for task in TASKS
    }

    for org_kind, source_name in (("fixed_O0", "fixed_O0_team_results"), ("readapted", "readapted_team_results")):
        conds = CONDITIONS if org_kind == "fixed_O0" else CONDITIONS[1:]
        accuracy = {condition: [] for condition in conds}
        logloss = {condition: [] for condition in conds}
        for run in runs:
            for condition in conds:
                item = run[source_name][condition]
                accuracy[condition].append(item["weighted_accuracy"])
                logloss[condition].append(item["weighted_log_loss"])
        output[f"collective_{org_kind}_accuracy"] = {
            condition: _paired_seed_summary(values) for condition, values in accuracy.items()
        }
        output[f"collective_{org_kind}_log_loss"] = {
            condition: _paired_seed_summary(values) for condition, values in logloss.items()
        }
        output[f"collective_{org_kind}_pairwise_accuracy_differences"] = {
            f"{left}_minus_{right}": _paired_seed_summary([
                accuracy[left][i] - accuracy[right][i] for i in range(20)
            ]) for left, right in itertools.combinations(conds, 2)
        }
        output[f"collective_{org_kind}_pairwise_log_loss_differences"] = {
            f"{left}_minus_{right}": _paired_seed_summary([
                logloss[left][i] - logloss[right][i] for i in range(20)
            ]) for left, right in itertools.combinations(conds, 2)
        }

    output["readaptation_minus_fixed_by_updated_condition"] = {
        condition: _paired_seed_summary([
            run["readapted_team_results"][condition]["weighted_accuracy"]
            - run["fixed_O0_team_results"][condition]["weighted_accuracy"] for run in runs
        ]) for condition in CONDITIONS[1:]
    }
    output["update_costs_by_condition"] = {
        "fit_seconds": {
            condition: _paired_seed_summary([
                run["updates"]["conditions"][condition]["fit_seconds"] for run in runs
            ]) for condition in CONDITIONS[1:]
        },
        "optimizer_iterations": {
            condition: _paired_seed_summary([
                run["updates"]["conditions"][condition]["optimizer_iterations"] for run in runs
            ]) for condition in CONDITIONS[1:]
        },
        "paired_fit_time_differences_seconds": {
            f"{left}_minus_{right}": _paired_seed_summary([
                run["updates"]["conditions"][left]["fit_seconds"]
                - run["updates"]["conditions"][right]["fit_seconds"] for run in runs
            ]) for left, right in itertools.combinations(CONDITIONS[1:], 2)
        },
        "paired_iteration_differences": {
            f"{left}_minus_{right}": _paired_seed_summary([
                run["updates"]["conditions"][left]["optimizer_iterations"]
                - run["updates"]["conditions"][right]["optimizer_iterations"] for run in runs
            ]) for left, right in itertools.combinations(CONDITIONS[1:], 2)
        },
    }
    output["C2_minus_C1_interpretation"] = INTERPRETATION_CAVEAT
    output["C3_scope"] = "permuted teacher-probability control; not an additional transfer-positive claim"
    return output


def run_campaign(config=CONFIG, transfer_n: int = TRANSFER_N, output_dir: Path = RESULTS_DIR):
    if tuple(config.campaign_seeds) != tuple(range(20)):
        raise ValueError("V2 campaign must use exactly seeds 0 through 19")
    if transfer_n != TRANSFER_N:
        raise ValueError("V2 protocol fixes exactly 1,000 new T3 transfer examples per seed")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty V2 results directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    runs = [_make_seed_run(seed, config, transfer_n) for seed in config.campaign_seeds]
    result = {
        "experiment": "HLS-CE-03 H3 second information-protocol iteration",
        "status": "CAMPAIGN_EXECUTED",
        "protocol_version": 2,
        "configuration": asdict(config),
        "new_T3_transfer_examples_per_seed": transfer_n,
        "conditions": {name: CONTROL_NOTES[name] for name in CONDITIONS},
        "interpretation_caveat": INTERPRETATION_CAVEAT,
        "optimization_budget": runs[0]["updates"]["optimization_budget"],
        "summary": summarize_runs(runs),
        "runs": runs,
    }
    result_path = output_dir / "results.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    metrics_rows = []
    for run in runs:
        for condition in CONDITIONS:
            org_labels = {"fixed_O0": run["fixed_O0_team_results"][condition]}
            if condition != "C0_no_update":
                org_labels["readapted"] = run["readapted_team_results"][condition]
            for organization, item in org_labels.items():
                metrics_rows.append({"seed": run["seed"], "condition": condition,
                                     "organization": organization,
                                     "weighted_accuracy": item["weighted_accuracy"],
                                     "weighted_log_loss": item["weighted_log_loss"]})
    csv_path = output_dir / "team_metrics_by_seed.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metrics_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(metrics_rows)
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (output_dir / "manifest.json").write_text(json.dumps({
        "run_code_sha256": source_hash,
        "results_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        "team_metrics_csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip(),
        "campaign_seeds": list(config.campaign_seeds),
        "transfer_examples_per_seed": transfer_n,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(),
                        "numpy": np.__version__, "scipy": scipy.__version__,
                        "scikit_learn": sklearn.__version__},
        "models_trained_or_invoked": "scikit-learn models on synthetic data only",
        "command": "python experiments/synthetic/hls_ce03_h3_transfer_v2.py --run-campaign",
    }, indent=2, sort_keys=True) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-campaign", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()
    if not args.run_campaign:
        parser.error("V2 campaign is not run implicitly; this phase is implementation and functional tests only")
    result = run_campaign(output_dir=args.output_dir)
    print(json.dumps({"output_dir": str(args.output_dir), "summary": result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
