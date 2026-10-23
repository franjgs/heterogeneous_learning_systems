"""Local policy and analysis helpers for the HLS dynamic-capacity pilot.

The module contains no model loading or benchmark access. It implements
validation-fitted thresholds and deterministic selectors over supplied data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class CascadeThreshold:
    target_escalation_rate: float
    threshold: float
    validation_escalation_rate: float


def fit_escalation_threshold(confidence: Sequence[float], target_rate: float) -> CascadeThreshold:
    """Choose a confidence cutoff nearest to a target escalation rate.

    This uses validation confidence values only (not correctness labels).
    Ties among attainable rates prefer the lower escalation rate.
    """
    scores = np.asarray(confidence, dtype=float)
    if scores.ndim != 1 or not len(scores) or not np.isfinite(scores).all():
        raise ValueError("confidence must be a non-empty finite vector")
    if not 0 <= target_rate <= 1:
        raise ValueError("target_rate must be in [0, 1]")
    unique = np.unique(scores)
    candidates = [float(np.nextafter(unique[0], -np.inf))]
    candidates.extend(float((left + right) / 2) for left, right in zip(unique[:-1], unique[1:]))
    candidates.append(float(np.nextafter(unique[-1], np.inf)))
    candidates = sorted(set(candidates))
    rates = [float(np.mean(scores < cutoff)) for cutoff in candidates]
    best = min(range(len(candidates)), key=lambda i: (abs(rates[i] - target_rate), rates[i], candidates[i]))
    return CascadeThreshold(float(target_rate), candidates[best], rates[best])


def cascade_predictions(
    fast_letters: Sequence[str], fast_confidence: Sequence[float],
    deep_letters: Sequence[str], threshold: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Use FAST unless its observable confidence is below threshold; then DEEP."""
    fast = np.asarray(fast_letters, dtype=str)
    deep = np.asarray(deep_letters, dtype=str)
    confidence = np.asarray(fast_confidence, dtype=float)
    if fast.ndim != 1 or fast.shape != deep.shape or fast.shape != confidence.shape:
        raise ValueError("FAST, DEEP and confidence vectors must have equal one-dimensional shape")
    if not np.isfinite(confidence).all():
        raise ValueError("confidence values must be finite")
    escalated = confidence < float(threshold)
    return np.where(escalated, deep, fast), escalated


def sequential_cascade_cost(
    initial_cost: Sequence[float], fallback_cost: Sequence[float],
    escalated: Sequence[bool],
) -> np.ndarray:
    """Return serial cascade cost, charging the initial and invoked fallback."""
    first = np.asarray(initial_cost, dtype=float)
    second = np.asarray(fallback_cost, dtype=float)
    use_second = np.asarray(escalated, dtype=bool)
    if first.ndim != 1 or first.shape != second.shape or first.shape != use_second.shape:
        raise ValueError("initial, fallback and escalation vectors must have equal shape")
    if not np.isfinite(first).all() or not np.isfinite(second).all() or np.any(first < 0) or np.any(second < 0):
        raise ValueError("costs must be finite and non-negative")
    return first + use_second * second


def static_model_by_task(
    train_tasks: Sequence[str], train_correct: np.ndarray,
    test_tasks: Sequence[str], model_ids: Sequence[str],
) -> tuple[np.ndarray, dict[str, str]]:
    """Choose the best empirical model per task using train labels only.

    Ties resolve by the supplied model order, which must be fixed in advance.
    A test task without training examples is rejected rather than backfilled.
    """
    tasks = np.asarray(train_tasks, dtype=str)
    outcomes = np.asarray(train_correct, dtype=int)
    test = np.asarray(test_tasks, dtype=str)
    models = tuple(map(str, model_ids))
    if outcomes.shape != (len(tasks), len(models)) or not np.isin(outcomes, (0, 1)).all():
        raise ValueError("train_correct must be a binary query-by-model matrix")
    lookup: dict[str, str] = {}
    for task in sorted(set(test.tolist())):
        indices = np.flatnonzero(tasks == task)
        if not len(indices):
            raise ValueError(f"no training examples for task {task!r}")
        means = outcomes[indices].mean(axis=0)
        lookup[task] = models[int(np.argmax(means))]
    model_to_index = {model: i for i, model in enumerate(models)}
    return np.asarray([model_to_index[lookup[task]] for task in test], dtype=int), lookup


def irt_route(
    predicted_quality: np.ndarray, predicted_cost: np.ndarray, price: float,
) -> np.ndarray:
    """Select argmax predicted correctness minus price times predicted cost."""
    q = np.asarray(predicted_quality, dtype=float)
    c = np.asarray(predicted_cost, dtype=float)
    if q.ndim != 2 or q.shape != c.shape or not np.isfinite(q).all() or not np.isfinite(c).all():
        raise ValueError("quality and cost must be finite equal query-by-model matrices")
    if price < 0 or np.any(c < 0):
        raise ValueError("price and costs must be non-negative")
    return np.argmax(q - float(price) * c, axis=1)


def fit_router_price(
    predicted_quality: np.ndarray, predicted_cost: np.ndarray, target_fraction: float,
) -> tuple[float, float]:
    """Fit price on validation to target a fraction of its min-to-max cost span."""
    q = np.asarray(predicted_quality, dtype=float)
    c = np.asarray(predicted_cost, dtype=float)
    if q.ndim != 2 or q.shape != c.shape or not len(q) or np.any(c < 0):
        raise ValueError("validation quality/cost matrices must be non-empty and shape matched")
    if not 0 <= target_fraction <= 1:
        raise ValueError("target_fraction must be in [0, 1]")
    low = float(c.min(axis=1).sum())
    high = float(c.max(axis=1).sum())
    target = low + target_fraction * (high - low)
    grid = np.r_[0.0, np.geomspace(1e-6, 1e6, 2000)]
    options = []
    for price in grid:
        choice = irt_route(q, c, float(price))
        spent = float(c[np.arange(len(choice)), choice].sum())
        options.append((abs(spent - target), float(price), spent))
    _, price, spent = min(options, key=lambda row: (row[0], row[1]))
    return price, spent / len(q)


def majority_vote(
    answers: np.ndarray, tie_break_model_index: int,
) -> np.ndarray:
    """Deterministic per-query plurality; ties use the declared model's answer."""
    values = np.asarray(answers, dtype=str)
    if values.ndim != 2 or values.shape[1] < 2:
        raise ValueError("answers must be a query-by-model matrix with at least two models")
    if not 0 <= tie_break_model_index < values.shape[1]:
        raise ValueError("tie-break model index is out of range")
    out = []
    for row in values:
        labels, counts = np.unique(row, return_counts=True)
        winners = labels[counts == counts.max()]
        fallback = row[tie_break_model_index]
        out.append(fallback if fallback in winners else str(winners[0]))
    return np.asarray(out, dtype=str)


def paired_stratified_bootstrap_delta(
    first: Sequence[float], second: Sequence[float], tasks: Sequence[str],
    *, n_boot: int = 5000, seed: int = 20261023,
) -> tuple[float, float, float]:
    """CI for mean(first-second), resampling paired queries within task."""
    a, b, strata = np.asarray(first, dtype=float), np.asarray(second, dtype=float), np.asarray(tasks, dtype=str)
    if a.ndim != 1 or a.shape != b.shape or a.shape != strata.shape or not len(a):
        raise ValueError("paired outcomes and task strata must be matching non-empty vectors")
    if not np.isfinite(a).all() or not np.isfinite(b).all() or n_boot < 100:
        raise ValueError("finite outcomes and at least 100 bootstrap replicates are required")
    delta = a - b
    groups = [np.flatnonzero(strata == task) for task in sorted(set(strata.tolist()))]
    rng = np.random.default_rng(seed)
    samples = np.empty(n_boot, dtype=float)
    for j in range(n_boot):
        picks = np.concatenate([rng.choice(idx, size=len(idx), replace=True) for idx in groups])
        samples[j] = float(delta[picks].mean())
    low, high = np.quantile(samples, [0.025, 0.975])
    return float(delta.mean()), float(low), float(high)


def per_task_accuracy(predicted: Sequence[str], correct_letters: Sequence[str],
                      tasks: Sequence[str]) -> dict[str, float]:
    pred, truth, task = map(lambda x: np.asarray(x, dtype=str), (predicted, correct_letters, tasks))
    if pred.ndim != 1 or pred.shape != truth.shape or pred.shape != task.shape:
        raise ValueError("prediction, answer and task vectors must have equal shape")
    return {key: float(np.mean(pred[task == key] == truth[task == key]))
            for key in sorted(set(task.tolist()))}


def select_train_validation_tradeoff_pair(
    model_ids: Sequence[str], train_accuracy: Mapping[str, float],
    train_latency: Mapping[str, float], validation_accuracy: Mapping[str, float],
    validation_latency: Mapping[str, float],
) -> tuple[str, str] | None:
    """Select (lower-cost, higher-quality) pair using train and validation only.

    A pair is eligible only when B is both more accurate and slower than A
    on train and validation. Among eligible pairs, choose the strongest B on
    train, then the fastest B, then the fastest A; model order breaks ties.
    """
    models = tuple(map(str, model_ids))
    mappings = (train_accuracy, train_latency, validation_accuracy, validation_latency)
    if len(set(models)) != len(models) or any(set(m) != set(models) for m in mappings):
        raise ValueError("each metric mapping must contain exactly the candidate model IDs")
    for values in mappings:
        if any(not np.isfinite(float(value)) for value in values.values()):
            raise ValueError("profile metrics must be finite")
    if any(float(x) < 0 for x in (train_latency.values())) or any(float(x) < 0 for x in validation_latency.values()):
        raise ValueError("latencies must be non-negative")
    eligible = []
    for ia, a in enumerate(models):
        for ib, b in enumerate(models):
            if a == b:
                continue
            if (train_accuracy[b] > train_accuracy[a]
                    and train_latency[b] > train_latency[a]
                    and validation_accuracy[b] > validation_accuracy[a]
                    and validation_latency[b] > validation_latency[a]):
                eligible.append((a, b, ia, ib))
    if not eligible:
        return None
    a, b, _, _ = min(
        eligible,
        key=lambda pair: (-float(train_accuracy[pair[1]]),
                          float(train_latency[pair[1]]),
                          float(train_latency[pair[0]]),
                          pair[3], pair[2]),
    )
    return a, b

