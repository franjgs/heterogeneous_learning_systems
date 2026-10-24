"""Refutatory HLS-CE-03 pilot: transfer, fixed organization, and reassignment.

This module defines a reproducible 20-seed campaign but does not run it on
import. Execute the campaign explicitly with ``--run-campaign``. Functional
tests use small fixtures and are not campaign results.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import itertools
import json
import platform
import subprocess
import sys
import time
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping

import numpy as np
import scipy
import sklearn
from sklearn.datasets import make_circles, make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler


TASKS = ("T1_linear", "T2_nonlinear", "T3_interactions")
AGENTS = ("A1_logistic", "A2_random_forest", "A3_mlp")
RESULTS_DIR = Path("results/experiments/hls_ce03_h3_transfer")


@dataclass(frozen=True)
class ExperimentConfig:
    train_n: int = 2000
    validation_n: int = 500
    test_n: int = 1000
    n_features: int = 10
    campaign_seeds: tuple[int, ...] = tuple(range(20))
    label_noise: float = 0.03
    circles_factor: float = 0.5
    circles_noise: float = 0.12
    logistic_c: float = 1.0
    logistic_max_iter: int = 500
    forest_trees: int = 100
    mlp_hidden_units: int = 32
    mlp_max_iter: int = 400
    mlp_alpha: float = 0.0001
    mlp_learning_rate_init: float = 0.001
    distillation_alpha: float = 0.5
    distillation_temperature: float = 1.0
    confidence_level: float = 0.95
    decision_threshold: float = 0.0
    ci_method: str = "paired Student-t interval across 20 seeds (df=19)"
    selection_objective: str = "minimum equal-task-weight validation error rate"
    tie_break: str = "lexicographic permutation in fixed AGENTS order"
    seed_pairing: str = "same generated task datasets for C0-C3 and all controls"


CONFIG = ExperimentConfig()


@dataclass(frozen=True)
class TaskSplit:
    X: np.ndarray
    y: np.ndarray


@dataclass(frozen=True)
class TaskData:
    train: TaskSplit
    validation: TaskSplit
    test: TaskSplit


@dataclass
class FittedAgent:
    agent_id: str
    scaler: StandardScaler
    estimator: object
    primary_task: str
    initial_fit_seconds: float

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        values = np.asarray(self.estimator.predict_proba(self.scaler.transform(X)), dtype=float)
        if values.ndim != 2 or values.shape[1] != 2 or not np.isfinite(values).all():
            raise ValueError("binary classifier must return finite two-class probabilities")
        return values


def _rng_seed(seed: int, task_index: int, split_index: int) -> int:
    sequence = np.random.SeedSequence([int(seed), task_index, split_index, 0xCE03])
    return int(sequence.generate_state(1, dtype=np.uint32)[0])


def _make_split(task: str, n: int, random_state: int, config: ExperimentConfig) -> TaskSplit:
    if n <= 0:
        raise ValueError("split size must be positive")
    if task == TASKS[0]:
        X, y = make_classification(
            n_samples=n, n_features=config.n_features, n_informative=6,
            n_redundant=0, n_repeated=0, n_classes=2, n_clusters_per_class=1,
            class_sep=1.0, flip_y=config.label_noise, random_state=random_state,
        )
    elif task == TASKS[1]:
        core, y = make_circles(
            n_samples=n, factor=config.circles_factor, noise=config.circles_noise,
            random_state=random_state,
        )
        rng = np.random.default_rng(_rng_seed(random_state, 1, 0))
        X = np.column_stack((core, rng.normal(size=(n, config.n_features - 2))))
        flips = rng.random(n) < config.label_noise
        y = np.asarray(y, dtype=int) ^ flips.astype(int)
    elif task == TASKS[2]:
        rng = np.random.default_rng(random_state)
        X = rng.normal(size=(n, config.n_features))
        score = X[:, 0] * X[:, 1] + X[:, 2] * X[:, 3]
        y = (score > 0.0).astype(int)
        flips = rng.random(n) < config.label_noise
        y ^= flips.astype(int)
    else:
        raise ValueError(f"unknown task {task!r}")
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    if X.shape != (n, config.n_features) or y.shape != (n,):
        raise ValueError("generated split has unexpected shape")
    if not np.isfinite(X).all() or not np.isin(y, (0, 1)).all():
        raise ValueError("generated split must contain finite features and binary labels")
    return TaskSplit(X=X, y=y)


def generate_tasks(seed: int, config: ExperimentConfig = CONFIG) -> dict[str, TaskData]:
    """Generate disjoint fixed-size splits using independent task/split seeds."""
    counts = (config.train_n, config.validation_n, config.test_n)
    result = {}
    for task_index, task in enumerate(TASKS):
        splits = tuple(
            _make_split(task, n, _rng_seed(seed, task_index, split_index), config)
            for split_index, n in enumerate(counts)
        )
        result[task] = TaskData(*splits)
    return result


def _new_estimator(agent_id: str, seed: int, config: ExperimentConfig):
    if agent_id == AGENTS[0]:
        return LogisticRegression(
            C=config.logistic_c, solver="lbfgs", max_iter=config.logistic_max_iter,
            warm_start=True, random_state=seed,
        )
    if agent_id == AGENTS[1]:
        return RandomForestClassifier(
            n_estimators=config.forest_trees, random_state=seed, n_jobs=1,
        )
    if agent_id == AGENTS[2]:
        return MLPClassifier(
            hidden_layer_sizes=(config.mlp_hidden_units,), activation="relu",
            solver="adam", alpha=config.mlp_alpha,
            learning_rate_init=config.mlp_learning_rate_init,
            max_iter=config.mlp_max_iter, early_stopping=False,
            random_state=seed,
        )
    raise ValueError(f"unknown agent {agent_id!r}")


def _agent_seed(seed: int, agent_index: int, salt: int = 0) -> int:
    sequence = np.random.SeedSequence([int(seed), agent_index, salt, 0xA631])
    return int(sequence.generate_state(1, dtype=np.uint32)[0])


def fit_initial_agents(
    tasks: Mapping[str, TaskData], seed: int, config: ExperimentConfig = CONFIG,
) -> dict[str, FittedAgent]:
    """Train all three models on the same pooled 6,000 labeled examples.

    The protocol specifies equal initial example budgets but no agent/task
    specialization. Sharing all task training examples avoids injecting an
    arbitrary initial task-to-agent advantage.
    """
    pooled_X = np.concatenate([tasks[task].train.X for task in TASKS], axis=0)
    pooled_y = np.concatenate([tasks[task].train.y for task in TASKS], axis=0)
    scaler = StandardScaler().fit(pooled_X)
    agents = {}
    for agent_index, agent_id in enumerate(AGENTS):
        estimator = _new_estimator(agent_id, _agent_seed(seed, agent_index), config)
        start = time.perf_counter()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            estimator.fit(scaler.transform(pooled_X), pooled_y)
        agents[agent_id] = FittedAgent(
            agent_id, scaler, estimator, "pooled_T1_T2_T3", time.perf_counter() - start,
        )
    return agents


def soft_target_expansion(X: np.ndarray, soft_positive_probability: np.ndarray):
    """Encode Bernoulli soft labels as weighted binary rows for sklearn LR."""
    features = np.asarray(X, dtype=float)
    probability = np.asarray(soft_positive_probability, dtype=float)
    if features.ndim != 2 or probability.shape != (len(features),):
        raise ValueError("soft-target inputs must have matching row counts")
    if not np.isfinite(features).all() or not np.isfinite(probability).all():
        raise ValueError("soft-target inputs must be finite")
    if np.any((probability < 0.0) | (probability > 1.0)):
        raise ValueError("soft probabilities must lie in [0, 1]")
    expanded_X = np.repeat(features, 2, axis=0)
    expanded_y = np.tile(np.asarray([0, 1], dtype=int), len(features))
    sample_weight = np.column_stack((1.0 - probability, probability)).reshape(-1)
    return expanded_X, expanded_y, sample_weight


def _temperature_probability(probability: np.ndarray, temperature: float) -> np.ndarray:
    if not np.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be finite and positive")
    eps = np.finfo(float).eps
    clipped = np.clip(np.asarray(probability, dtype=float), eps, 1.0 - eps)
    logits = np.log(clipped / (1.0 - clipped)) / temperature
    return 1.0 / (1.0 + np.exp(-logits))


def _fit_logistic_targets(
    source: FittedAgent,
    X: np.ndarray,
    y: np.ndarray,
    soft_positive_probability: np.ndarray | None,
    *,
    seed: int,
    warm_start: bool,
    config: ExperimentConfig,
) -> tuple[FittedAgent, float, int]:
    if not isinstance(source.estimator, LogisticRegression):
        raise TypeError("only the A1 logistic capability can be retrained")
    estimator = copy.deepcopy(source.estimator) if warm_start else _new_estimator(
        AGENTS[0], seed, config,
    )
    transformed = source.scaler.transform(X)
    if soft_positive_probability is None:
        fit_X, fit_y, weights = transformed, np.asarray(y, dtype=int), None
    else:
        q = (1.0 - config.distillation_alpha) * np.asarray(y, dtype=float)
        q += config.distillation_alpha * np.asarray(soft_positive_probability, dtype=float)
        fit_X, fit_y, weights = soft_target_expansion(transformed, q)
    start = time.perf_counter()
    estimator.fit(fit_X, fit_y, sample_weight=weights)
    elapsed = time.perf_counter() - start
    iterations = int(np.max(estimator.n_iter_))
    return FittedAgent(source.agent_id, source.scaler, estimator, source.primary_task, elapsed), elapsed, iterations


def distill_a1(
    agents: Mapping[str, FittedAgent], tasks: Mapping[str, TaskData], seed: int,
    config: ExperimentConfig = CONFIG,
) -> tuple[FittedAgent, dict[str, object]]:
    """Warm-start A1 on T3 with true/soft labels; teacher is A3 on same train rows."""
    teacher = agents[AGENTS[2]]
    receiver = agents[AGENTS[0]]
    t3 = tasks[TASKS[2]].train
    teacher_start = time.perf_counter()
    teacher_probability = teacher.predict_proba(t3.X)[:, 1]
    teacher_inference_seconds = time.perf_counter() - teacher_start
    teacher_probability = _temperature_probability(
        teacher_probability, config.distillation_temperature,
    )
    transferred, fit_seconds, iterations = _fit_logistic_targets(
        receiver, t3.X, t3.y, teacher_probability,
        seed=_agent_seed(seed, 0, 11), warm_start=True, config=config,
    )
    before = {
        "coef": np.asarray(receiver.estimator.coef_).tolist(),
        "intercept": np.asarray(receiver.estimator.intercept_).tolist(),
    }
    after = {
        "coef": np.asarray(transferred.estimator.coef_).tolist(),
        "intercept": np.asarray(transferred.estimator.intercept_).tolist(),
    }
    metadata = {
        "donor": AGENTS[2], "receiver": AGENTS[0], "task": TASKS[2],
        "teacher_inference_seconds": teacher_inference_seconds,
        "student_fit_seconds": fit_seconds,
        "total_transfer_seconds": teacher_inference_seconds + fit_seconds,
        "student_optimizer_iterations": iterations,
        "temperature": config.distillation_temperature,
        "soft_label_weight": config.distillation_alpha,
        "train_log_loss_hard_labels_before": float(
            log_loss(t3.y, receiver.predict_proba(t3.X), labels=[0, 1])
        ),
        "parameters_before": before, "parameters_after": after,
        "train_log_loss_hard_labels_after": float(
            log_loss(t3.y, transferred.predict_proba(t3.X), labels=[0, 1])
        ),
        "train_log_loss_soft_targets": _soft_log_loss(
            (1-config.distillation_alpha) * t3.y
            + config.distillation_alpha * teacher_probability,
            transferred.predict_proba(t3.X)[:, 1],
        ),
    }
    return transferred, metadata


def _soft_log_loss(target: np.ndarray, positive_probability: np.ndarray) -> float:
    eps = np.finfo(float).eps
    q = np.asarray(target, dtype=float)
    p = np.clip(np.asarray(positive_probability, dtype=float), eps, 1.0-eps)
    return float(-np.mean(q * np.log(p) + (1-q) * np.log(1-p)))


def fit_transfer_controls(
    a1: FittedAgent,
    tasks: Mapping[str, TaskData],
    teacher_probability: np.ndarray,
    seed: int,
    config: ExperimentConfig = CONFIG,
) -> dict[str, tuple[FittedAgent, dict[str, object]]]:
    """Implement the distinct controls specified by E3.

    E3's Controls 1 and 2 both specify retraining A1 on the same real labels,
    with no teacher probabilities and the same optimization budget. They are
    therefore one control, explicitly cross-referenced under both names.
    """
    t3 = tasks[TASKS[2]].train
    if np.asarray(teacher_probability).shape != (len(t3.y),):
        raise ValueError("teacher probabilities must align with T3 training rows")
    hard_label_control, elapsed_hard, iter_hard = _fit_logistic_targets(
        a1, t3.X, t3.y, None, seed=_agent_seed(seed, 0, 21),
        warm_start=True, config=config,
    )
    permutation = np.random.default_rng(_agent_seed(seed, 0, 23)).permutation(len(t3.y))
    permuted, elapsed_permuted, iter_permuted = _fit_logistic_targets(
        a1, t3.X, t3.y, np.asarray(teacher_probability)[permutation],
        seed=_agent_seed(seed, 0, 24), warm_start=True, config=config,
    )
    return {
        "control1_and_control2_identical_hard_label_refit": (hard_label_control, {
            "satisfies_protocol_controls": [1, 2],
            "reason": "Both controls specify the same A1 retraining data, labels, and optimization budget; no distinct operation is defined.",
            "fit_seconds": elapsed_hard, "optimizer_iterations": iter_hard,
        }),
        "control3_permuted_teacher": (permuted, {
            "fit_seconds": elapsed_permuted, "optimizer_iterations": iter_permuted,
            "teacher_probability_permutation": permutation.tolist(),
        }),
    }


def _metric(probability: np.ndarray, y: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y, np.argmax(probability, axis=1))),
        "log_loss": float(log_loss(y, probability, labels=[0, 1])),
    }


def score_matrix(
    agents: Mapping[str, FittedAgent], tasks: Mapping[str, TaskData], split_name: str,
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, dict[str, float]]]:
    if split_name not in {"validation", "test"}:
        raise ValueError("score matrix split must be validation or test")
    metrics: dict[str, dict[str, dict[str, float]]] = {agent: {} for agent in AGENTS}
    timings: dict[str, dict[str, float]] = {agent: {} for agent in AGENTS}
    for agent_id in AGENTS:
        for task in TASKS:
            split = getattr(tasks[task], split_name)
            start = time.perf_counter()
            probability = agents[agent_id].predict_proba(split.X)
            timings[agent_id][task] = time.perf_counter() - start
            metrics[agent_id][task] = _metric(probability, split.y)
    return metrics, timings


def _loss_matrix(metric_matrix: Mapping[str, Mapping[str, Mapping[str, float]]]):
    return {
        task: {agent: 1.0 - metric_matrix[agent][task]["accuracy"] for agent in AGENTS}
        for task in TASKS
    }


def select_assignment(
    validation_loss: Mapping[str, Mapping[str, float]],
) -> tuple[str, str, str]:
    """Enumerate all six one-agent-per-task assignments; ties use AGENTS order."""
    if set(validation_loss) != set(TASKS):
        raise ValueError("validation loss matrix must include exactly the three tasks")
    for task in TASKS:
        if set(validation_loss[task]) != set(AGENTS):
            raise ValueError(f"validation row for {task} must include exactly all agents")
        if not np.isfinite([validation_loss[task][agent] for agent in AGENTS]).all():
            raise ValueError("validation losses must be finite")
    candidates = tuple(itertools.permutations(AGENTS))
    return min(candidates, key=lambda assignment: (
        sum(validation_loss[task][agent] for task, agent in zip(TASKS, assignment)) / len(TASKS),
        tuple(AGENTS.index(agent) for agent in assignment),
    ))


def evaluate_assignment(
    assignment: tuple[str, str, str],
    matrix: Mapping[str, Mapping[str, Mapping[str, float]]],
) -> dict[str, object]:
    if tuple(assignment) not in tuple(itertools.permutations(AGENTS)):
        raise ValueError("assignment must be one of the six one-to-one permutations")
    selected = [matrix[agent][task] for task, agent in zip(TASKS, assignment)]
    return {
        "assignment_by_task": dict(zip(TASKS, assignment)),
        "weighted_accuracy": float(np.mean([cell["accuracy"] for cell in selected])),
        "weighted_log_loss": float(np.mean([cell["log_loss"] for cell in selected])),
        "accuracy_by_task": {task: matrix[agent][task]["accuracy"] for task, agent in zip(TASKS, assignment)},
        "log_loss_by_task": {task: matrix[agent][task]["log_loss"] for task, agent in zip(TASKS, assignment)},
    }


def _unique_condition_results(C0, C1, C2) -> dict[str, object]:
    """Store C0-C2 once and identify C3 as the same C2 reference condition."""
    return {
        "conditions_test": {
            "C0_no_transfer_fixed_O0": C0,
            "C1_transfer_fixed_O0": C1,
            "C2_transfer_readapted_O1": C2,
        },
        "condition_aliases": {
            "C3_validation_optimum_reference": "C2_transfer_readapted_O1",
            "reason": "Both select the post-transfer minimum-error assignment using the same validation matrix; C3 is an alias, not another observation.",
        },
    }


def _assignment_validation_gap(assignment, matrix):
    selected = evaluate_assignment(assignment, matrix)["weighted_accuracy"]
    best_feasible = max(
        evaluate_assignment(candidate, matrix)["weighted_accuracy"]
        for candidate in itertools.permutations(AGENTS)
    )
    return float(best_feasible - selected)


def _test_hindsight_gap(matrix, assignment):
    selected = evaluate_assignment(assignment, matrix)["weighted_accuracy"]
    all_test_assignments = [
        evaluate_assignment(candidate, matrix)["weighted_accuracy"]
        for candidate in itertools.permutations(AGENTS)
    ]
    return float(max(all_test_assignments) - selected)


def _single_agent_metrics(agent, tasks):
    output = {}
    for task in TASKS:
        test = tasks[task].test
        probability = agent.predict_proba(test.X)
        output[task] = _metric(probability, test.y)
    return output


def _run_seed(seed: int, config: ExperimentConfig) -> dict[str, object]:
    tasks = generate_tasks(seed, config)
    train_agents_start = time.perf_counter()
    original_agents = fit_initial_agents(tasks, seed, config)
    total_initial_fit_seconds = time.perf_counter() - train_agents_start
    initial_val_matrix, initial_val_timing = score_matrix(original_agents, tasks, "validation")
    initial_loss = _loss_matrix(initial_val_matrix)
    reorganization_start = time.perf_counter()
    O0 = select_assignment(initial_loss)
    O0_select_seconds = time.perf_counter() - reorganization_start

    transferred_a1, transfer_metadata = distill_a1(original_agents, tasks, seed, config)
    # Obtain exactly the same teacher outputs for the permuted-probability control.
    teacher_p = original_agents[AGENTS[2]].predict_proba(tasks[TASKS[2]].train.X)[:, 1]
    teacher_p = _temperature_probability(teacher_p, config.distillation_temperature)
    controls = fit_transfer_controls(original_agents[AGENTS[0]], tasks, teacher_p, seed, config)
    post_agents = dict(original_agents)
    post_agents[AGENTS[0]] = transferred_a1
    post_val_matrix, post_val_timing = score_matrix(post_agents, tasks, "validation")
    post_loss = _loss_matrix(post_val_matrix)
    reorganization_start = time.perf_counter()
    O1 = select_assignment(post_loss)
    O1_select_seconds = time.perf_counter() - reorganization_start

    pre_test_matrix, pre_test_timing = score_matrix(original_agents, tasks, "test")
    post_test_matrix, post_test_timing = score_matrix(post_agents, tasks, "test")
    C0 = evaluate_assignment(O0, pre_test_matrix)
    C1 = evaluate_assignment(O0, post_test_matrix)
    C2 = evaluate_assignment(O1, post_test_matrix)
    unique_conditions = _unique_condition_results(C0, C1, C2)

    a1_pre = _single_agent_metrics(original_agents[AGENTS[0]], tasks)
    a1_post = _single_agent_metrics(transferred_a1, tasks)
    control_metrics = {
        label: {task: _metric(agent.predict_proba(tasks[task].test.X), tasks[task].test.y)
                for task in TASKS}
        for label, (agent, _) in controls.items()
    }
    return {
        "seed": seed,
        "data_counts": {"train_per_task": config.train_n, "validation_per_task": config.validation_n,
                        "test_per_task": config.test_n, "features": config.n_features},
        "initial_training": "same pooled 6,000 labeled examples (2,000/task) for every agent; no initial task specialization",
        "validation_loss_matrix_initial": initial_loss,
        "validation_loss_matrix_post_transfer": post_loss,
        "O0_initial_validation_optimum": dict(zip(TASKS, O0)),
        "O1_post_transfer_validation_optimum": dict(zip(TASKS, O1)),
        "number_of_responsibilities_changed": int(sum(a != b for a, b in zip(O0, O1))),
        **unique_conditions,
        "validation_selection_gap": {
            "C0": _assignment_validation_gap(O0, initial_val_matrix),
            "C1": _assignment_validation_gap(O0, post_val_matrix),
            "C2": _assignment_validation_gap(O1, post_val_matrix),
        },
        "test_hindsight_assignment_gap_oracle_diagnostic": {
            "C0": _test_hindsight_gap(pre_test_matrix, O0),
            "C1": _test_hindsight_gap(post_test_matrix, O0),
            "C2": _test_hindsight_gap(post_test_matrix, O1),
        },
        "A1_individual_test_metrics_before": a1_pre,
        "A1_individual_test_metrics_after_distillation": a1_post,
        "control_test_metrics_A1": control_metrics,
        "controls": {label: metadata for label, (_, metadata) in controls.items()},
        "transfer": transfer_metadata,
        "costs_seconds": {
            "initial_fit_total": total_initial_fit_seconds,
            "initial_fit_by_agent": {agent: result.initial_fit_seconds for agent, result in original_agents.items()},
            "teacher_inference_for_distillation": transfer_metadata["teacher_inference_seconds"],
            "distillation_student_fit": transfer_metadata["student_fit_seconds"],
            "transfer_total": transfer_metadata["total_transfer_seconds"],
            "organization_selection_O0": O0_select_seconds,
            "organization_selection_O1": O1_select_seconds,
            "validation_inference_initial": initial_val_timing,
            "validation_inference_post_transfer": post_val_timing,
            "test_inference_initial": pre_test_timing,
            "test_inference_post_transfer": post_test_timing,
        },
    }


def paired_seed_summary(values: list[float], confidence: float = CONFIG.confidence_level) -> dict[str, float | int | str]:
    """Summarize one paired contrast per seed; rows/examples are not replicates."""
    from scipy.stats import t

    data = np.asarray(values, dtype=float)
    if data.ndim != 1 or not len(data) or not np.isfinite(data).all():
        raise ValueError("paired seed differences must be a non-empty finite vector")
    mean = float(np.mean(data))
    sd = float(np.std(data, ddof=1)) if len(data) > 1 else 0.0
    if len(data) > 1:
        half = float(t.ppf(0.5 + confidence / 2, df=len(data)-1) * sd / np.sqrt(len(data)))
    else:
        half = 0.0
    return {
        "n_seeds": int(len(data)), "mean": mean, "median": float(np.median(data)),
        "sd": sd, "ci95_low": mean-half, "ci95_high": mean+half,
        "positive_seeds": int(np.sum(data > 0)), "negative_seeds": int(np.sum(data < 0)),
        "zero_seeds": int(np.sum(data == 0)),
        "ci_method": "paired Student-t interval across independent seeds",
    }


def summarize_campaign(runs: list[dict[str, object]]) -> dict[str, object]:
    if not runs:
        raise ValueError("campaign requires at least one seed result")
    seeds = [int(run["seed"]) for run in runs]
    if len(seeds) != len(set(seeds)):
        raise ValueError("campaign seed results must be unique")
    d_individual_transfer_vs_refit = [
        run["A1_individual_test_metrics_after_distillation"][TASKS[2]]["accuracy"]
        - run["control_test_metrics_A1"]["control1_and_control2_identical_hard_label_refit"][TASKS[2]]["accuracy"]
        for run in runs
    ]
    d_individual_distill_vs_initial = [
        run["A1_individual_test_metrics_after_distillation"][TASKS[2]]["accuracy"]
        - run["A1_individual_test_metrics_before"][TASKS[2]]["accuracy"]
        for run in runs
    ]
    d_fixed = [
        run["conditions_test"]["C1_transfer_fixed_O0"]["weighted_accuracy"]
        - run["conditions_test"]["C0_no_transfer_fixed_O0"]["weighted_accuracy"] for run in runs
    ]
    d_readapted = [
        run["conditions_test"]["C2_transfer_readapted_O1"]["weighted_accuracy"]
        - run["conditions_test"]["C1_transfer_fixed_O0"]["weighted_accuracy"] for run in runs
    ]
    summary = {
        "D_individual_transfer_vs_refit_A1_T3": paired_seed_summary(d_individual_transfer_vs_refit),
        "D_individual_distill_vs_initial_A1_T3_descriptive": paired_seed_summary(d_individual_distill_vs_initial),
        "D_fixed_C1_minus_C0": paired_seed_summary(d_fixed),
        "D_readapted_C2_minus_C1": paired_seed_summary(d_readapted),
        "H3_point_signs_both_satisfied": False,
        "H3_supported_by_prespecified_CIs": False,
        "decision_rule": "H3 requires both a positive paired individual effect of distillation versus the hard-label refit control and a negative paired C1-C0 collective effect under the same O0. Statistical support requires the respective 95% seed-level CIs to lie strictly above and below zero. Point signs alone do not confirm H3. C2-C1 is an independent reorganization contrast.",
    }
    summary["H3_point_signs_both_satisfied"] = (
        summary["D_individual_transfer_vs_refit_A1_T3"]["mean"] > CONFIG.decision_threshold
        and summary["D_fixed_C1_minus_C0"]["mean"] < CONFIG.decision_threshold
    )
    summary["H3_supported_by_prespecified_CIs"] = (
        summary["D_individual_transfer_vs_refit_A1_T3"]["ci95_low"] > CONFIG.decision_threshold
        and summary["D_fixed_C1_minus_C0"]["ci95_high"] < CONFIG.decision_threshold
    )
    return summary


def run_campaign(config: ExperimentConfig = CONFIG, output_dir: Path = RESULTS_DIR) -> dict[str, object]:
    """Run the authorized 20-seed campaign; intentionally not invoked by tests."""
    if tuple(config.campaign_seeds) != tuple(range(20)):
        raise ValueError("campaign must use exactly the predeclared seeds 0 through 19")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty results directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    runs = [_run_seed(seed, config) for seed in config.campaign_seeds]
    result = {
        "experiment": "HLS-CE-03 refutatory HLS-H3 transfer pilot",
        "status": "CAMPAIGN_EXECUTED",
        "configuration": asdict(config),
        "interpretation": {
            "C2_C3": "C3 is represented only as an alias of C2; no duplicate observation is stored or emitted.",
            "test_selection": "test outcomes do not enter training, model/hyperparameter choice, or assignment selection",
            "test_hindsight": "reported only as a retrospective diagnostic, never an operational policy",
        },
        "summary": summarize_campaign(runs),
        "runs": runs,
    }
    result_path = output_dir / "results.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    metrics_rows = []
    for run in runs:
        seed = run["seed"]
        for condition, values in run["conditions_test"].items():
            metrics_rows.append({"seed": seed, "condition": condition,
                                 "weighted_accuracy": values["weighted_accuracy"],
                                 "weighted_log_loss": values["weighted_log_loss"]})
    with (output_dir / "condition_metrics_by_seed.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=metrics_rows[0].keys())
        writer.writeheader()
        writer.writerows(metrics_rows)
    source = Path(__file__)
    manifest = {
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "config_sha256": hashlib.sha256(json.dumps(asdict(config), sort_keys=True).encode()).hexdigest(),
        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip(),
        "seeds": list(config.campaign_seeds),
        "result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        "training_or_inference_models": "scikit-learn synthetic classifiers only",
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-campaign", action="store_true", help="explicitly execute all 20 predeclared seeds")
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()
    if not args.run_campaign:
        parser.error("campaign is not run implicitly; pass --run-campaign only after campaign authorization")
    result = run_campaign(output_dir=args.output_dir)
    print(json.dumps({"output_dir": str(args.output_dir), "summary": result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
