"""Pure utilities for the exploratory B1 empirical interaction pilot."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split


def normalized_confusion_profiles(
    y_true: Iterable[int], y_pred: Iterable[int], n_classes: int = 10
) -> np.ndarray:
    """Return one row-normalized confusion profile per true class."""
    matrix = confusion_matrix(y_true, y_pred, labels=np.arange(n_classes))
    row_totals = matrix.sum(axis=1, keepdims=True)
    if np.any(row_totals == 0):
        raise ValueError("every class must occur in the profiling split")
    return matrix / row_totals


def cluster_competence_profiles(profiles: np.ndarray, n_clusters: int = 4) -> np.ndarray:
    """Cluster class profiles deterministically into competence assignments."""
    if profiles.ndim != 2 or profiles.shape[0] < n_clusters:
        raise ValueError("profiles must have at least n_clusters rows")
    return AgglomerativeClustering(
        n_clusters=n_clusters, linkage="ward"
    ).fit_predict(profiles)


def stratified_four_way_indices(
    labels: Iterable[int], seed: int
) -> dict[str, np.ndarray]:
    """Create disjoint stratified train/transfer/validation/test index sets."""
    labels_array = np.asarray(labels)
    all_indices = np.arange(labels_array.shape[0])
    train, temporary = train_test_split(
        all_indices,
        test_size=0.6,
        stratify=labels_array,
        random_state=seed,
    )
    transfer, remainder = train_test_split(
        temporary,
        test_size=2.0 / 3.0,
        stratify=labels_array[temporary],
        random_state=seed + 1,
    )
    validation, test = train_test_split(
        remainder,
        test_size=0.5,
        stratify=labels_array[remainder],
        random_state=seed + 2,
    )
    return {
        "train": np.sort(train),
        "transfer": np.sort(transfer),
        "validation": np.sort(validation),
        "test": np.sort(test),
    }


def select_transfer_indices(
    transfer_labels: Iterable[int],
    competence_classes: Iterable[int],
    budget: int,
    seed: int,
) -> np.ndarray:
    """Select at most budget transfer examples from the specified classes."""
    labels_array = np.asarray(transfer_labels)
    candidates = np.flatnonzero(np.isin(labels_array, list(competence_classes)))
    rng = np.random.default_rng(seed)
    selected = rng.permutation(candidates)[: min(budget, candidates.size)]
    return np.sort(selected)


def gamma_value(v0: float, vi: float, vj: float, vij: float) -> float:
    """Compute the four-value interaction contrast."""
    return vij - vi - vj + v0


def delta_vector(scores_i: Iterable[float], scores_0: Iterable[float]) -> np.ndarray:
    """Return competence-level change relative to the same F_0 scores."""
    return np.asarray(scores_i, dtype=float) - np.asarray(scores_0, dtype=float)


def bootstrap_mean_ci(
    values: Iterable[float], seed: int, replicates: int = 2000, confidence: float = 0.95
) -> tuple[float, float]:
    """Return a percentile bootstrap interval for a descriptive sample mean."""
    values_array = np.asarray(list(values), dtype=float)
    if values_array.size == 0:
        raise ValueError("cannot bootstrap an empty sample")
    rng = np.random.default_rng(seed)
    sampled = rng.choice(values_array, size=(replicates, values_array.size), replace=True)
    means = sampled.mean(axis=1)
    alpha = (1.0 - confidence) / 2.0
    return float(np.quantile(means, alpha)), float(np.quantile(means, 1.0 - alpha))
