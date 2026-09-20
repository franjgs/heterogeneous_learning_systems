"""Pure data and metric helpers for the B2.0 PACS calibration pilot."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.model_selection import train_test_split

DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
CLASSES = ("dog", "elephant", "giraffe", "guitar", "horse", "house", "person")
SPLITS = ("base", "transfer", "validation", "test")
SPLIT_FRACTIONS = {"base": 0.50, "transfer": 0.20, "validation": 0.15, "test": 0.15}


def validate_manifest(manifest: pd.DataFrame) -> None:
    required = {"sample_id", "domain", "label", "class_name", "sha256", "relative_path"}
    missing = required.difference(manifest.columns)
    if missing:
        raise ValueError(f"manifest missing columns: {sorted(missing)}")
    if manifest["sample_id"].duplicated().any() or manifest["relative_path"].duplicated().any():
        raise ValueError("sample IDs and relative paths must be unique")
    if set(manifest["domain"].unique()) != set(DOMAINS):
        raise ValueError("manifest must contain exactly the four PACS domains")
    if set(manifest["label"].unique()) != set(range(len(CLASSES))):
        raise ValueError("manifest must contain exactly the seven PACS classes")
    if manifest["sha256"].duplicated().any():
        raise ValueError("byte-identical image content detected in the manifest")
    observed = set(zip(manifest["label"], manifest["class_name"], strict=True))
    expected = set(enumerate(CLASSES))
    if observed != expected:
        raise ValueError("class IDs and names do not match the canonical PACS mapping")


def stratified_splits(
    manifest: pd.DataFrame, seed: int, fractions: dict[str, float] | None = None
) -> dict[str, np.ndarray]:
    """Return disjoint sample IDs stratified on the domain × class cell."""
    validate_manifest(manifest)
    fractions = fractions or SPLIT_FRACTIONS
    if tuple(fractions) != SPLITS or not np.isclose(sum(fractions.values()), 1.0):
        raise ValueError("fractions must define base/transfer/validation/test and sum to 1")
    ids = manifest["sample_id"].to_numpy()
    strata = (manifest["domain"].astype(str) + "::" + manifest["label"].astype(str)).to_numpy()

    base_ids, remainder_ids, base_strata, remainder_strata = train_test_split(
        ids,
        strata,
        train_size=fractions["base"],
        random_state=seed,
        stratify=strata,
    )
    remainder_fraction = 1.0 - fractions["base"]
    transfer_share = fractions["transfer"] / remainder_fraction
    transfer_ids, holdout_ids, _, holdout_strata = train_test_split(
        remainder_ids,
        remainder_strata,
        train_size=transfer_share,
        random_state=seed + 1,
        stratify=remainder_strata,
    )
    validation_share = fractions["validation"] / (fractions["validation"] + fractions["test"])
    validation_ids, test_ids = train_test_split(
        holdout_ids,
        train_size=validation_share,
        random_state=seed + 2,
        stratify=holdout_strata,
    )
    result = {
        "base": np.sort(base_ids),
        "transfer": np.sort(transfer_ids),
        "validation": np.sort(validation_ids),
        "test": np.sort(test_ids),
    }
    validate_disjoint_splits(result, set(ids))
    return result


def validate_disjoint_splits(
    splits: dict[str, Sequence[int]], expected_ids: set[int] | None = None
) -> None:
    if set(splits) != set(SPLITS):
        raise ValueError(f"splits must be exactly {SPLITS}")
    arrays = {name: np.asarray(ids) for name, ids in splits.items()}
    for i, left in enumerate(SPLITS):
        for right in SPLITS[i + 1 :]:
            if np.intersect1d(arrays[left], arrays[right]).size:
                raise ValueError(f"overlap between {left} and {right}")
    if expected_ids is not None:
        union = set(np.concatenate(list(arrays.values())).tolist())
        if union != expected_ids:
            raise ValueError("split union does not equal the dataset IDs")


def select_base_fraction(
    manifest: pd.DataFrame, base_ids: Sequence[int], fraction: float, seed: int
) -> np.ndarray:
    """Sample a reproducible, balanced fraction within every domain × class cell."""
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    base = manifest[manifest["sample_id"].isin(base_ids)]
    rng = np.random.default_rng(seed)
    chosen: list[int] = []
    for _, cell in base.groupby(["domain", "label"], sort=True):
        ids = cell["sample_id"].to_numpy()
        n = min(len(ids), max(1, int(round(len(ids) * fraction))))
        chosen.extend(rng.choice(ids, size=n, replace=False).tolist())
    return np.asarray(sorted(chosen), dtype=int)


def domain_metrics(
    y_true: Sequence[int], y_pred: Sequence[int], domains: Sequence[str]
) -> dict[str, dict[str, float]]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    domains = np.asarray(domains)
    if not (len(y_true) == len(y_pred) == len(domains)):
        raise ValueError("labels and domains must have equal lengths")
    result: dict[str, dict[str, float]] = {}
    for domain in DOMAINS:
        mask = domains == domain
        if not np.any(mask):
            raise ValueError(f"no examples for domain {domain}")
        result[domain] = {
            "balanced_accuracy": float(balanced_accuracy_score(y_true[mask], y_pred[mask])),
            "accuracy": float(accuracy_score(y_true[mask], y_pred[mask])),
            "n": int(mask.sum()),
        }
    return result


def domain_gaps(deep: dict[str, float], fast: dict[str, float]) -> dict[str, float]:
    if set(deep) != set(DOMAINS) or set(fast) != set(DOMAINS):
        raise ValueError("gap inputs must contain all four domains")
    return {domain: float(deep[domain] - fast[domain]) for domain in DOMAINS}
