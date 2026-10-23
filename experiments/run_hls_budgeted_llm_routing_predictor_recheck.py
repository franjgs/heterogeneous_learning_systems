"""Predictor-focused re-evaluation of the existing MMLU routing pilot.

Uses the exact model outcomes, queries, costs, packings, and budgets from the
first pilot. It writes to a separate results directory and never runs inference.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "experiments")]

import run_hls_budgeted_llm_routing_pilot as original  # noqa: E402
from hls.experiment_contract import (  # noqa: E402
    ExperimentEvent, ExperimentRun, MetricValue, SeedRecord, UnitDeclaration,
)
from hls.llm_routing_pilot import (  # noqa: E402
    MODEL_IDS, ContextualLogisticQualityPredictor, MIRTQualityPredictor,
    apply_latency, budget_between_extremes, greedy_feasible,
    independent_with_repair, predict_latency, score_assignment,
    solve_batch_ilp,
)
from hls.performance_evaluation import (  # noqa: E402
    EvaluationProfile, EvaluationRecord, PerformanceEvaluator,
)


OUT = ROOT / "results/experiments/hls_budgeted_llm_routing_predictor_recheck"
OUTCOMES = ROOT / "results/experiments/hls_budgeted_llm_routing_pilot/model_outcomes.csv"
PREDICTOR_IDS = ("mirt_adapted", "train_prevalence", "contextual_logistic")
POLICY_IDS = ("batch_ilp", "greedy_feasible", "independent_repaired")


def _metric_summary(values: np.ndarray, seed: int) -> dict[str, Any]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(10000, len(values)), replace=True).mean(axis=1)
    return {
        "mean": float(values.mean()),
        "ci95_stratified_query_bootstrap": [
            float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975)),
        ],
    }


def _stratified_bootstrap(frame: pd.DataFrame, column: str, seed: int) -> list[float]:
    rng = np.random.default_rng(seed)
    arrays = [frame.loc[frame.task_type == task, column].to_numpy(dtype=float)
              for task in original.TEST_SUBJECTS]
    draws = np.zeros(10000)
    for values in arrays:
        draws += rng.choice(values, size=(len(draws), len(values)), replace=True).mean(axis=1) / len(arrays)
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def _binary_logloss(pred: np.ndarray, truth: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, 1e-9, 1 - 1e-9)
    return -(truth * np.log(pred) + (1 - truth) * np.log(1 - pred))


def _pairwise_rank_contributions(pred: np.ndarray, truth: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    correct = np.zeros(truth.shape[0], dtype=float)
    total = np.zeros(truth.shape[0], dtype=float)
    for i in range(truth.shape[0]):
        for a in range(truth.shape[1]):
            for b in range(a + 1, truth.shape[1]):
                if truth[i, a] == truth[i, b]:
                    continue
                diff = pred[i, a] - pred[i, b]
                total[i] += 1.0
                correct[i] += (1.0 if diff * (truth[i, a] - truth[i, b]) > 0
                               else (0.5 if diff == 0 else 0.0))
    return correct, total


def _pairwise_rank_bootstrap(
    correct: np.ndarray, total: np.ndarray, task_types: np.ndarray, seed: int,
) -> list[float]:
    rng = np.random.default_rng(seed)
    draws_n = np.zeros(10000)
    draws_d = np.zeros(10000)
    for task in original.TEST_SUBJECTS:
        indices = np.flatnonzero(task_types == task)
        sampled = rng.choice(indices, size=(len(draws_n), len(indices)), replace=True)
        draws_n += correct[sampled].sum(axis=1)
        draws_d += total[sampled].sum(axis=1)
    valid = draws_d > 0
    ratios = draws_n[valid] / draws_d[valid]
    return [float(np.quantile(ratios, 0.025)), float(np.quantile(ratios, 0.975))]


def _calibration(pred: np.ndarray, truth: np.ndarray, bins: int = 10) -> dict[str, Any]:
    flat_p, flat_y = pred.ravel(), truth.ravel()
    edges = np.linspace(0, 1, bins + 1)
    rows = []
    ece = 0.0
    for i in range(bins):
        mask = (flat_p >= edges[i]) & (flat_p < edges[i + 1] if i < bins - 1 else flat_p <= edges[i + 1])
        if not mask.any():
            rows.append({"lower": float(edges[i]), "upper": float(edges[i + 1]), "count": 0,
                         "mean_predicted": None, "observed_rate": None})
            continue
        mean_p, rate = float(flat_p[mask].mean()), float(flat_y[mask].mean())
        ece += float(mask.mean()) * abs(mean_p - rate)
        rows.append({"lower": float(edges[i]), "upper": float(edges[i + 1]),
                     "count": int(mask.sum()), "mean_predicted": mean_p,
                     "observed_rate": rate})
    return {"ece_10_equal_width": ece, "reliability_bins": rows,
            "mean_prediction_minus_prevalence": float(flat_p.mean() - flat_y.mean())}


def _predictive_evaluation(
    test: pd.DataFrame, truth: np.ndarray, predictions: dict[str, np.ndarray],
) -> dict[str, Any]:
    out: dict[str, Any] = {"overall": {}, "by_task": {}, "paired_predictor_differences": {}}
    per_query_losses: dict[str, dict[str, np.ndarray]] = {}
    per_query_rank: dict[str, np.ndarray] = {}
    for predictor_id, pred in predictions.items():
        brier_q = np.mean((pred - truth) ** 2, axis=1)
        logloss_q = np.mean(_binary_logloss(pred, truth), axis=1)
        per_query_losses[predictor_id] = {"brier": brier_q, "log_loss": logloss_q}
        rank_correct, rank_total = _pairwise_rank_contributions(pred, truth)
        per_query_rank[predictor_id] = (rank_correct, rank_total)
        picked = np.argmax(pred, axis=1)
        top_correct = truth[np.arange(len(test)), picked]
        out["overall"][predictor_id] = {
            "brier": {"mean": float(brier_q.mean()),
                      "ci95_stratified_query_bootstrap": _stratified_bootstrap(
                          test.assign(value=brier_q), "value", original.TRAIN_SEED + 31)},
            "log_loss": {"mean": float(logloss_q.mean()),
                         "ci95_stratified_query_bootstrap": _stratified_bootstrap(
                             test.assign(value=logloss_q), "value", original.TRAIN_SEED + 32)},
            "calibration": _calibration(pred, truth),
            "pairwise_model_order_accuracy": {
                "mean": float(rank_correct.sum() / rank_total.sum()),
                "ci95_stratified_query_bootstrap": _pairwise_rank_bootstrap(
                    rank_correct, rank_total, test.task_type.to_numpy(), original.TRAIN_SEED + 33),
                "informative_query_pairs": int(rank_total.sum()),
            },
            "top_predicted_model_is_correct": _metric_summary(top_correct, original.TRAIN_SEED + 34),
        }
        out["by_task"][predictor_id] = {}
        for task in original.TEST_SUBJECTS:
            mask = test.task_type.to_numpy() == task
            task_pred, task_truth = pred[mask], truth[mask]
            task_brier = np.mean((task_pred - task_truth) ** 2, axis=1)
            task_log = np.mean(_binary_logloss(task_pred, task_truth), axis=1)
            task_rank_correct, task_rank_total = _pairwise_rank_contributions(task_pred, task_truth)
            task_top = task_truth[np.arange(len(task_pred)), np.argmax(task_pred, axis=1)]
            out["by_task"][predictor_id][task] = {
                "n_queries": int(mask.sum()),
                "brier": _metric_summary(task_brier, original.TRAIN_SEED + 35),
                "log_loss": _metric_summary(task_log, original.TRAIN_SEED + 36),
                "calibration": _calibration(task_pred, task_truth),
                "pairwise_model_order_accuracy": {
                    "mean": float(task_rank_correct.sum() / task_rank_total.sum()) if task_rank_total.sum() else None,
                    "informative_query_pairs": int(task_rank_total.sum()),
                },
                "top_predicted_model_is_correct": _metric_summary(task_top, original.TRAIN_SEED + 38),
            }
    for other, reference in (("train_prevalence", "mirt_adapted"),
                             ("contextual_logistic", "mirt_adapted"),
                             ("contextual_logistic", "train_prevalence")):
        for metric in ("brier", "log_loss"):
            diff = per_query_losses[other][metric] - per_query_losses[reference][metric]
            out["paired_predictor_differences"][f"{other}-minus-{reference}:{metric}"] = {
                "mean": float(diff.mean()),
                "ci95_stratified_query_bootstrap": _stratified_bootstrap(
                    test.assign(value=diff), "value", original.TRAIN_SEED + 39),
                "negative_favors_other_predictor": True,
            }
        other_correct, other_total = per_query_rank[other]
        ref_correct, ref_total = per_query_rank[reference]
        diff_rank = other_correct - ref_correct
        rank_denominator = other_total
        # Paired resampling of queries; a query contributes its pairwise wins/losses
        # and the common number of informative model pairs.
        rank_task_types = test.task_type.to_numpy()
        rng = np.random.default_rng(original.TRAIN_SEED + 40)
        rank_num = np.zeros(10000)
        rank_den = np.zeros(10000)
        for task in original.TEST_SUBJECTS:
            indices = np.flatnonzero(rank_task_types == task)
            sampled = rng.choice(indices, size=(len(rank_num), len(indices)), replace=True)
            rank_num += diff_rank[sampled].sum(axis=1)
            rank_den += rank_denominator[sampled].sum(axis=1)
        valid = rank_den > 0
        rank_ci = [float(np.quantile(rank_num[valid] / rank_den[valid], .025)),
                   float(np.quantile(rank_num[valid] / rank_den[valid], .975))]
        out["paired_predictor_differences"][f"{other}-minus-{reference}:pairwise_order_accuracy"] = {
            "mean": float(diff_rank.sum() / rank_denominator.sum()),
            "ci95_stratified_query_bootstrap": rank_ci,
        }
    return out


def _load_exact_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train, test = original.load_pilot_data()
    if not OUTCOMES.is_file():
        raise FileNotFoundError(f"original pilot outcomes are missing: {OUTCOMES}")
    outcomes = pd.read_csv(OUTCOMES)
    expected_rows = len(MODEL_IDS) * (len(train) + len(test))
    if len(outcomes) != expected_rows:
        raise ValueError(f"outcome cache has {len(outcomes)} rows; expected {expected_rows}")
    expected_ids = set(train.query_id) | set(test.query_id)
    if set(outcomes.query_id) != expected_ids or set(outcomes.model_id) != set(MODEL_IDS):
        raise ValueError("cached outcomes do not match the original train/test query and model sets")
    if set(outcomes.model_revision) != set(original.MODEL_REVISIONS.values()):
        raise ValueError("cached outcomes use unexpected model revisions")
    return train, test, outcomes


def _policy_choices(q: np.ndarray, costs: np.ndarray, budget: float, price: float) -> dict[str, np.ndarray]:
    return {
        "batch_ilp": solve_batch_ilp(q, costs, budget),
        "greedy_feasible": greedy_feasible(q, costs, budget),
        "independent_repaired": independent_with_repair(q, costs, budget, price),
    }


def run_recheck(out_dir: Path = OUT) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        git_revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                      check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_revision = None
    source_paths = [
        Path(__file__), ROOT / "src/hls/llm_routing_pilot.py",
        ROOT / "experiments/run_hls_budgeted_llm_routing_pilot.py",
        ROOT / "src/hls/experiment_contract.py", ROOT / "src/hls/performance_evaluation.py",
    ]
    source_hashes = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source_paths
    }
    train, test, outcomes = _load_exact_inputs()
    fit_n = int(len(train) * 0.8)
    split_rng = np.random.default_rng(original.TRAIN_SEED + 1)
    order = split_rng.permutation(len(train))
    fit_frame = train.iloc[order[:fit_n]].reset_index(drop=True)
    calibration_frame = train.iloc[order[fit_n:]].reset_index(drop=True)
    fit_y = original.matrix_for(fit_frame, outcomes, "correct")
    cal_y = original.matrix_for(calibration_frame, outcomes, "correct")
    test_y = original.matrix_for(test, outcomes, "correct")
    fit_text = original.request_features(fit_frame)
    cal_text = original.request_features(calibration_frame)
    test_text = original.request_features(test)

    mirt = MIRTQualityPredictor(seed=original.TRAIN_SEED).fit(fit_text, MODEL_IDS, fit_y)
    predictions = {
        "mirt_adapted": mirt.predict(test_text),
        "train_prevalence": np.broadcast_to(fit_y.mean(axis=0), (len(test), len(MODEL_IDS))).copy(),
    }
    cal_predictions = {
        "mirt_adapted": mirt.predict(cal_text),
        "train_prevalence": np.broadcast_to(fit_y.mean(axis=0), (len(calibration_frame), len(MODEL_IDS))).copy(),
    }
    logistic = ContextualLogisticQualityPredictor(seed=original.TRAIN_SEED)
    logistic.fit(
        fit_text, fit_frame.task_type.astype(str).tolist(), MODEL_IDS, fit_y,
        fit_frame.query_id.astype(str).tolist(),
    )
    predictions["contextual_logistic"] = logistic.predict(
        test_text, test.task_type.astype(str).tolist(),
    )
    cal_predictions["contextual_logistic"] = logistic.predict(
        cal_text, calibration_frame.task_type.astype(str).tolist(),
    )

    input_fit = original.matrix_for(fit_frame, outcomes, "input_tokens")
    latency_fit = original.matrix_for(fit_frame, outcomes, "latency_seconds")
    latency_coeff = predict_latency(input_fit, latency_fit)
    recomputed_test_costs = apply_latency(original.matrix_for(test, outcomes, "input_tokens"), latency_coeff)
    original_cost_path = ROOT / "results/experiments/hls_budgeted_llm_routing_pilot/quality_cost_predictions.csv"
    original_cost_table = pd.read_csv(original_cost_path).pivot(
        index="query_id", columns="model_id", values="predicted_cost_seconds",
    )
    costs_test = original_cost_table.loc[test.query_id, list(MODEL_IDS)].to_numpy(dtype=float)
    if not np.allclose(costs_test, recomputed_test_costs, rtol=0.0, atol=1e-12):
        raise AssertionError("recomputed costs differ from the original pilot cost matrix")
    costs_cal = apply_latency(original.matrix_for(calibration_frame, outcomes, "input_tokens"), latency_coeff)
    actual_latency = original.matrix_for(test, outcomes, "latency_seconds")
    lambdas = {
        predictor_id: {
            fraction: original._lambda_for_budget(cal_predictions[predictor_id], costs_cal, fraction)
            for fraction in original.BUDGET_FRACTIONS
        }
        for predictor_id in PREDICTOR_IDS
    }
    predictive = _predictive_evaluation(test, test_y, predictions)

    evaluator = PerformanceEvaluator()
    assignment_rows: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []
    run_objects: list[ExperimentRun] = []
    for predictor_id in PREDICTOR_IDS:
        q_test = predictions[predictor_id]
        for seed in original.PACKING_SEEDS:
            for condition, batches in original.make_batchings(test, seed).items():
                for fraction in original.BUDGET_FRACTIONS:
                    profile_id = f"recheck-{predictor_id}-{condition}-{fraction:.2f}-seed{seed}"
                    composite_ids = tuple(f"{predictor_id}:{policy}" for policy in POLICY_IDS)
                    profile = EvaluationProfile(
                        profile_id=profile_id, scenario_id="mmlu_mit_pilot_v1",
                        configuration_id=f"{condition}-n{len(test)}-budget-frac{fraction:.2f}",
                        application_domain="local open-weight language models",
                        organizational_problem="single-model query assignment under shared batch inference-time budget",
                        decision_objective={pid: pid.split(":", 1)[1] for pid in composite_ids},
                        constraints="one model per query; sum predicted local inference seconds <= batch budget",
                        primary_metrics=("functional_success_rate", "original_reward_cumulative"),
                        secondary_metrics=("resource_usage:inference_latency_seconds",),
                        information_regime="official MMLU auxiliary_train fit/CV/calibration; test labels hidden from predictors",
                        temporal_horizon=len(test), aggregation_rules="one MMLU test query per period; exact answer-letter match",
                        demand_distribution_id=f"mmlu-four-subjects-{condition}-seeded",
                        resource_units={"inference_latency_seconds": "seconds"},
                    )
                    evaluator.register_profile(profile)
                    records_by_policy: dict[str, list[EvaluationRecord]] = {pid: [] for pid in composite_ids}
                    batches_by_policy: dict[str, list[dict[str, float]]] = {pid: [] for pid in composite_ids}
                    sequence = 0
                    for batch_num, indices in enumerate(batches):
                        q_batch, c_batch = q_test[indices], costs_test[indices]
                        truth_batch, latency_batch = test_y[indices], actual_latency[indices]
                        budget = budget_between_extremes(c_batch, fraction)
                        choices = _policy_choices(q_batch, c_batch, budget, lambdas[predictor_id][fraction])
                        for policy_id, selected in choices.items():
                            composite = f"{predictor_id}:{policy_id}"
                            metric = score_assignment(selected, truth_batch, c_batch, latency_batch, budget)
                            if not metric.budget_compliant_estimated:
                                raise AssertionError(f"{composite} violated predicted budget")
                            batches_by_policy[composite].append({
                                "accuracy": metric.accuracy,
                                "estimated_cost_seconds": metric.cost_estimated_seconds,
                                "observed_latency_seconds": metric.latency_observed_seconds,
                                "budget_seconds": metric.budget_seconds,
                                "estimated_compliant": float(metric.budget_compliant_estimated),
                                "observed_compliant": float(metric.budget_compliant_observed),
                            })
                            for local_i, query_index in enumerate(indices):
                                model_idx = int(selected[local_i])
                                correct = int(truth_batch[local_i, model_idx])
                                record = EvaluationRecord(
                                    scenario_id=profile.scenario_id,
                                    configuration_id=profile.configuration_id,
                                    policy_id=composite, period=sequence + local_i,
                                    demand=str(test.iloc[query_index].subject), success=bool(correct),
                                    original_reward=float(correct),
                                    resource_usage={"inference_latency_seconds": float(latency_batch[local_i, model_idx])},
                                    quality=float(correct), task_type=str(test.iloc[query_index].subject),
                                    provenance=f"cais/mmlu@{original.DATASET_REVISION}#test:{test.iloc[query_index].query_id}:{MODEL_IDS[model_idx]}:{seed}",
                                    unit_id=str(test.iloc[query_index].query_id),
                                    information_regime=profile.information_regime,
                                    decision_objective=policy_id,
                                    available_metadata={
                                        "predictor_id": predictor_id, "model_id": MODEL_IDS[model_idx],
                                        "batch_index": batch_num, "predicted_quality": float(q_batch[local_i, model_idx]),
                                        "predicted_cost_seconds": float(c_batch[local_i, model_idx]),
                                        "batch_budget_seconds": budget,
                                    },
                                )
                                records_by_policy[composite].append(record)
                                assignment_rows.append({
                                    "predictor_id": predictor_id, "packing_seed": seed,
                                    "condition": condition, "budget_fraction": fraction,
                                    "batch_index": batch_num, "query_id": test.iloc[query_index].query_id,
                                    "task_type": str(test.iloc[query_index].subject),
                                    "policy_id": policy_id, "model_id": MODEL_IDS[model_idx],
                                    "correct": correct,
                                    "predicted_quality": float(q_batch[local_i, model_idx]),
                                    "predicted_cost_seconds": float(c_batch[local_i, model_idx]),
                                    "observed_latency_seconds": float(latency_batch[local_i, model_idx]),
                                    "batch_budget_seconds": budget,
                                })
                        sequence += len(indices)
                    for policy_id in POLICY_IDS:
                        composite = f"{predictor_id}:{policy_id}"
                        eval_results = evaluator.evaluate(profile_id, composite, records_by_policy[composite])
                        batch_metrics = batches_by_policy[composite]
                        by_task = {
                            task: float(np.mean([r.success for r in records_by_policy[composite]
                                                 if r.task_type == task])
                                        ) for task in original.TEST_SUBJECTS
                        }
                        seed_rows.append({
                            "predictor_id": predictor_id, "packing_seed": seed,
                            "condition": condition, "budget_fraction": fraction,
                            "policy_id": policy_id,
                            "accuracy": float(np.mean([x["accuracy"] for x in batch_metrics])),
                            "estimated_cost_seconds": float(np.mean([x["estimated_cost_seconds"] for x in batch_metrics])),
                            "observed_latency_seconds": float(np.mean([x["observed_latency_seconds"] for x in batch_metrics])),
                            "budget_seconds": float(np.mean([x["budget_seconds"] for x in batch_metrics])),
                            "estimated_budget_compliance": float(np.mean([x["estimated_compliant"] for x in batch_metrics])),
                            "observed_latency_budget_compliance": float(np.mean([x["observed_compliant"] for x in batch_metrics])),
                            **{f"accuracy:{task}": value for task, value in by_task.items()},
                        })
                        events = tuple(ExperimentEvent(
                            sequence_index=i, event_type="batch_assignment_summary",
                            mechanism_id=composite, time_index=i,
                            data={"batch_index": i, **batch},
                        ) for i, batch in enumerate(batch_metrics))
                        metric_values = tuple(MetricValue(
                            name=name, value=float(value.value), unit=value.unit,
                            interpretation=value.definition_id,
                            preferred_direction="lower" if name.startswith("resource_usage:") else "higher",
                        ) for name, value in eval_results.items() if value.value is not None)
                        run_objects.append(ExperimentRun(
                            schema_version="hls-experiment-run/1.0",
                            run_id=f"recheck-{predictor_id}-{condition}-b{fraction:.2f}-{policy_id}-seed{seed}",
                            mechanism_id=f"{predictor_id}+{policy_id}", policy_id=composite,
                            configuration={
                                "scenario_id": profile.scenario_id,
                                "configuration_id": profile.configuration_id,
                                "problem": "one model per query under shared batch latency budget",
                                "predictor_id": predictor_id, "policy_id": policy_id,
                                "model_ids": list(MODEL_IDS), "batch_size": original.BATCH_SIZE,
                                "batch_condition": condition, "budget_fraction": fraction,
                                "quality_features": "question/options text + MMLU subject + model identity",
                                "cost_predictor": "unchanged per-model affine token-to-local-latency regression from original pilot",
                            },
                            initial_conditions={"test_queries": len(test), "test_subjects": list(original.TEST_SUBJECTS)},
                            random_seeds=(
                                SeedRecord("train_sample", original.TRAIN_SEED, "original auxiliary_train sample"),
                                SeedRecord("test_sample", original.TEST_SEED, "original official test sample"),
                                SeedRecord("packing", seed, "original paired batch packing"),
                            ),
                            information_available={"query_text": "available", "subject": "available",
                                                   "training_outcomes": "auxiliary_train only",
                                                   "test_outcomes": "hidden from predictors and assignment policies"},
                            observation_model={"stochastic_generation": False,
                                               "decoding": "original greedy generation cache; max_new_tokens=8",
                                               "device": "measured in original pilot"},
                            software_revision=git_revision,
                            units=(UnitDeclaration("accuracy", "fraction", "balanced four-subject exact match"),
                                   UnitDeclaration("inference_latency", "seconds", "original observed local wall time")),
                            events=events, metrics=metric_values,
                            mechanism_results={
                                "profile_evaluation": {k: {"value": v.value, "unit": v.unit,
                                                           "status": v.status.value, "definition_id": v.definition_id,
                                                           "aggregation": v.aggregation}
                                                      for k, v in eval_results.items()},
                                "per_task_accuracy": by_task,
                            },
                            metadata={
                                "evaluation_profile_id": profile_id,
                                "source_run": "original hls_budgeted_llm_routing_pilot",
                                "dataset_revision": original.DATASET_REVISION,
                                "model_revisions": original.MODEL_REVISIONS,
                                "git_revision": git_revision,
                                "source_hashes_sha256": source_hashes,
                                "costs_and_model_outcomes_reused": True,
                                "test_labels_used_only_for_retrospective_evaluation": True,
                            },
                        ))

    assignments = pd.DataFrame(assignment_rows)
    summary = pd.DataFrame(seed_rows)
    expected = (len(PREDICTOR_IDS) * len(POLICY_IDS) * len(original.PACKING_SEEDS)
                * 2 * len(original.BUDGET_FRACTIONS) * len(test))
    if len(assignments) != expected:
        raise AssertionError(f"assignment count {len(assignments)} != {expected}")
    counts = assignments.groupby(
        ["predictor_id", "packing_seed", "condition", "budget_fraction", "policy_id"],
        sort=False,
    ).query_id.agg(["size", "nunique"])
    if not ((counts["size"] == len(test)) & (counts["nunique"] == len(test))).all():
        raise AssertionError("each predictor/policy run must assign every held-out query once")
    if len(run_objects) != len(PREDICTOR_IDS) * len(POLICY_IDS) * len(original.PACKING_SEEDS) * 2 * len(original.BUDGET_FRACTIONS):
        raise AssertionError("ExperimentRun count does not match factorial")
    if len(summary) != len(run_objects):
        raise AssertionError("one summary row per ExperimentRun is required")
    assignments.to_csv(out_dir / "test_assignments.csv.gz", index=False, compression="gzip")
    summary.to_csv(out_dir / "seed_level_metrics.csv", index=False)
    runs_json = [json.loads(run.to_json()) for run in run_objects]
    ExperimentRun.from_json(json.dumps(runs_json[0]))
    (out_dir / "experiment_runs.json").write_text(json.dumps(runs_json, indent=2, sort_keys=True))

    metrics = {}
    for key, frame in summary.groupby(["predictor_id", "condition", "budget_fraction", "policy_id"], sort=True):
        group_key = "|".join(map(str, key))
        metrics[group_key] = {}
        for col in ("accuracy", "estimated_cost_seconds", "observed_latency_seconds",
                    "estimated_budget_compliance", "observed_latency_budget_compliance"):
            mean = float(frame[col].mean())
            rng = np.random.default_rng(original.TRAIN_SEED + 52)
            vals = frame[col].to_numpy(dtype=float)
            draws = rng.choice(vals, size=(10000, len(vals)), replace=True).mean(axis=1)
            metrics[group_key][col] = {
                "mean": mean,
                "ci95_repacking": [float(np.quantile(draws, .025)), float(np.quantile(draws, .975))],
            }
        qframe = assignments[
            (assignments.predictor_id == key[0]) & (assignments.condition == key[1])
            & (assignments.budget_fraction == key[2]) & (assignments.policy_id == key[3])
        ].groupby(["task_type", "query_id"], as_index=False).correct.mean()
        task_types = assignments[
            (assignments.predictor_id == key[0]) & (assignments.condition == key[1])
            & (assignments.budget_fraction == key[2])
        ][["task_type", "query_id"]].drop_duplicates()
        qframe = qframe.merge(task_types, on=["task_type", "query_id"], how="left")
        metrics[group_key]["accuracy"]["ci95_stratified_query_bootstrap"] = _stratified_bootstrap(
            qframe.rename(columns={"correct": "value"}), "value", original.TRAIN_SEED + 53)

    contrasts = {}
    for condition in ("homogeneous", "heterogeneous"):
        for fraction in original.BUDGET_FRACTIONS:
            for predictor_id in PREDICTOR_IDS:
                sub = summary[(summary.condition == condition)
                              & (summary.budget_fraction == fraction)
                              & (summary.predictor_id == predictor_id)]
                pivot = sub.pivot(index="packing_seed", columns="policy_id", values="accuracy")
                for a, b in (("batch_ilp", "greedy_feasible"),
                             ("batch_ilp", "independent_repaired")):
                    vals = (pivot[a] - pivot[b]).to_numpy()
                    rng = np.random.default_rng(original.TRAIN_SEED + 54)
                    draws = rng.choice(vals, size=(10000, len(vals)), replace=True).mean(axis=1)
                    pair_rows = assignments[
                        (assignments.predictor_id == predictor_id)
                        & (assignments.condition == condition)
                        & (assignments.budget_fraction == fraction)
                        & (assignments.policy_id.isin((a, b)))
                    ].groupby(["task_type", "query_id", "policy_id"], as_index=False).correct.mean()
                    pair_wide = pair_rows.pivot(index=["task_type", "query_id"],
                                                columns="policy_id", values="correct").reset_index()
                    pair_wide["difference"] = pair_wide[a] - pair_wide[b]
                    contrasts[f"{predictor_id}|{condition}|{fraction:.2f}|{a}-minus-{b}"] = {
                        "mean": float(vals.mean()),
                        "ci95_paired_repacking": [float(np.quantile(draws, .025)), float(np.quantile(draws, .975))],
                        "ci95_stratified_query_bootstrap": _stratified_bootstrap(
                            pair_wide, "difference", original.TRAIN_SEED + 57),
                    }
            # Paired predictor changes for each policy, with same query, packing and costs.
            for policy_id in POLICY_IDS:
                sub = summary[(summary.condition == condition)
                              & (summary.budget_fraction == fraction)
                              & (summary.policy_id == policy_id)]
                pivot = sub.pivot(index="packing_seed", columns="predictor_id", values="accuracy")
                for other, reference in (("train_prevalence", "mirt_adapted"),
                                         ("contextual_logistic", "mirt_adapted"),
                                         ("contextual_logistic", "train_prevalence")):
                    vals = (pivot[other] - pivot[reference]).to_numpy()
                    rng = np.random.default_rng(original.TRAIN_SEED + 55)
                    draws = rng.choice(vals, size=(10000, len(vals)), replace=True).mean(axis=1)
                    pair_rows = assignments[
                        (assignments.condition == condition)
                        & (assignments.budget_fraction == fraction)
                        & (assignments.policy_id == policy_id)
                        & (assignments.predictor_id.isin((other, reference)))
                    ].groupby(["task_type", "query_id", "predictor_id"], as_index=False).correct.mean()
                    pair_wide = pair_rows.pivot(index=["task_type", "query_id"],
                                                columns="predictor_id", values="correct").reset_index()
                    pair_wide["difference"] = pair_wide[other] - pair_wide[reference]
                    contrasts[f"{condition}|{fraction:.2f}|{policy_id}|{other}-minus-{reference}"] = {
                        "mean": float(vals.mean()),
                        "ci95_paired_repacking": [float(np.quantile(draws, .025)), float(np.quantile(draws, .975))],
                        "ci95_stratified_query_bootstrap": _stratified_bootstrap(
                            pair_wide, "difference", original.TRAIN_SEED + 58),
                    }

    decision_changes = {}
    model_assignment_shares = {}
    for key, frame in assignments.groupby(
            ["predictor_id", "condition", "budget_fraction", "policy_id"], sort=True):
        group_key = "|".join(map(str, key))
        model_assignment_shares[group_key] = {
            model: float((frame.model_id == model).mean()) for model in MODEL_IDS
        }
    for condition in ("homogeneous", "heterogeneous"):
        for fraction in original.BUDGET_FRACTIONS:
            for policy_id in POLICY_IDS:
                sub = assignments[(assignments.condition == condition)
                                  & (assignments.budget_fraction == fraction)
                                  & (assignments.policy_id == policy_id)]
                wide = sub.pivot(index=["packing_seed", "query_id"], columns="predictor_id",
                                 values=["model_id", "correct"])
                for other, reference in (("train_prevalence", "mirt_adapted"),
                                         ("contextual_logistic", "mirt_adapted"),
                                         ("contextual_logistic", "train_prevalence")):
                    switched = wide[("model_id", other)] != wide[("model_id", reference)]
                    correct_delta = (wide[("correct", other)] - wide[("correct", reference)]).astype(float)
                    decision_changes[f"{condition}|{fraction:.2f}|{policy_id}|{other}-vs-{reference}"] = {
                        "fraction_of_query_packing_decisions_changed": float(switched.mean()),
                        "accuracy_delta_all_decisions": float(correct_delta.mean()),
                        "accuracy_delta_on_changed_decisions": (
                            float(correct_delta[switched].mean()) if switched.any() else None
                        ),
                        "interpretation": "descriptive paired change; not a causal mediation estimate",
                    }

    task_accuracy = {}
    for key, frame in summary.groupby(["predictor_id", "condition", "budget_fraction", "policy_id"], sort=True):
        group_key = "|".join(map(str, key))
        task_accuracy[group_key] = {}
        for task in original.TEST_SUBJECTS:
            vals = frame[f"accuracy:{task}"].to_numpy(dtype=float)
            rng = np.random.default_rng(original.TRAIN_SEED + 56)
            draws = rng.choice(vals, size=(10000, len(vals)), replace=True).mean(axis=1)
            task_accuracy[group_key][task] = {
                "mean": float(vals.mean()),
                "ci95_repacking": [float(np.quantile(draws, .025)), float(np.quantile(draws, .975))],
            }

    result = {
        "design": {
            "predictors": list(PREDICTOR_IDS), "policies": list(POLICY_IDS),
            "packing_seeds": list(original.PACKING_SEEDS),
            "conditions": ["homogeneous", "heterogeneous"],
            "budget_fractions": list(original.BUDGET_FRACTIONS),
            "test_query_ids_sha256": hashlib.sha256("\n".join(test.query_id).encode()).hexdigest(),
            "outcomes_sha256": hashlib.sha256(OUTCOMES.read_bytes()).hexdigest(),
            "cost_model_unchanged": True, "test_outcomes_used_for_decisions": False,
        },
        "predictive_evaluation": predictive,
        "contextual_predictor_training": logistic.fit_info,
        "task_type_feature_coverage": {
            "training_task_types": sorted(set(fit_frame.task_type.astype(str))),
            "test_task_types": list(original.TEST_SUBJECTS),
            "unseen_test_task_types_in_predictor_fit": sorted(
                set(test.task_type.astype(str)) - set(fit_frame.task_type.astype(str))
            ),
        },
        "mirt_training": mirt.fit_info,
        "metrics_by_predictor_condition_budget_policy": metrics,
        "per_task_accuracy": task_accuracy,
        "paired_contrasts": contrasts,
        "decision_changes_vs_mirt": decision_changes,
        "model_assignment_shares": model_assignment_shares,
        "cost_model_diagnostics": {
            "cost_rmse_seconds_per_query_model": float(np.sqrt(np.mean((
                costs_test - actual_latency
            ) ** 2))),
            "test_observed_latency_mean_by_model": {
                model: float(actual_latency[:, i].mean()) for i, model in enumerate(MODEL_IDS)
            },
        },
        "provenance": {
            "source_dataset": original.DATASET_ID,
            "dataset_revision": original.DATASET_REVISION,
            "model_revisions": original.MODEL_REVISIONS,
            "outcomes_reused_from_original_pilot": True,
            "original_cost_matrix_sha256": hashlib.sha256(original_cost_path.read_bytes()).hexdigest(),
            "source_hashes_sha256": source_hashes,
            "git_revision": git_revision,
            "test_subjects": list(original.TEST_SUBJECTS),
            "train_fit_calibration_sizes": [fit_n, len(calibration_frame)],
            "cost_fit_split_and_seed_unchanged": True,
            "pef_records": len(run_objects), "assignment_rows": len(assignments),
            "software": {"python": sys.version.split()[0], "platform": platform.platform()},
        },
    }
    (out_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True))
    hashes = {}
    for name in ("test_assignments.csv.gz", "seed_level_metrics.csv", "experiment_runs.json", "results.json"):
        hashes[name] = hashlib.sha256((out_dir / name).read_bytes()).hexdigest()
    (out_dir / "artifact_hashes.json").write_text(json.dumps(hashes, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    result = run_recheck()
    print(json.dumps({"output": str(OUT), "runs": result["provenance"]["pef_records"],
                      "predictive": {k: {m: v["mean"] for m, v in vals.items()
                                         if m in ("brier", "log_loss", "pairwise_model_order_accuracy",
                                                  "top_predicted_model_is_correct")}
                                     for k, vals in result["predictive_evaluation"]["overall"].items()}}, indent=2))
