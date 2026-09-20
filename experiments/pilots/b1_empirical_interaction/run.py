"""Execute the exploratory B1 empirical interaction pilot."""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import adjusted_rand_score, balanced_accuracy_score, recall_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.b1_empirical_interaction import (  # noqa: E402
    bootstrap_mean_ci,
    cluster_competence_profiles,
    delta_vector,
    gamma_value,
    normalized_confusion_profiles,
    select_transfer_indices,
    stratified_four_way_indices,
)


N_CLASSES = 10
GROUPINGS = ("competence", "random")
LABEL_MODES = ("pseudo", "true")


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _fit_fast(X: np.ndarray, y: np.ndarray, seed: int) -> LogisticRegression:
    model = LogisticRegression(solver="lbfgs", max_iter=1000, random_state=seed)
    model.fit(X, y)
    return model


def _fit_deep(X: np.ndarray, y: np.ndarray, seed: int) -> RandomForestClassifier:
    model = RandomForestClassifier(
        n_estimators=80, random_state=seed, n_jobs=1
    )
    model.fit(X, y)
    return model


def _global_score(model, X: np.ndarray, y: np.ndarray) -> float:
    return float(balanced_accuracy_score(y, model.predict(X)))


def _competence_scores(
    model, X: np.ndarray, y: np.ndarray, groups: list[list[int]]
) -> list[float]:
    predictions = model.predict(X)
    return [
        float(
            recall_score(
                y[np.isin(y, classes)],
                predictions[np.isin(y, classes)],
                labels=classes,
                average="macro",
                zero_division=0,
            )
        )
        for classes in groups
    ]


def _groups_from_assignments(assignments: np.ndarray) -> list[list[int]]:
    return [
        sorted(np.flatnonzero(assignments == group_id).astype(int).tolist())
        for group_id in sorted(np.unique(assignments).tolist())
    ]


def _random_groups(sizes: list[int], seed: int) -> list[list[int]]:
    permutation = np.random.default_rng(seed).permutation(N_CLASSES).tolist()
    groups: list[list[int]] = []
    cursor = 0
    for size in sizes:
        groups.append(sorted(permutation[cursor : cursor + size]))
        cursor += size
    return groups


def _split_membership_rows(seed: int, splits: dict[str, np.ndarray]) -> list[dict[str, object]]:
    rows = []
    for split, indices in splits.items():
        rows.extend(
            {"seed": seed, "split": split, "sample_index": int(index)}
            for index in indices
        )
    return rows


def _summary_rows(gamma: pd.DataFrame, config: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    grouped = gamma.groupby(
        ["grouping", "label_mode", "budget", "i", "j"], sort=True
    )
    for keys, frame in grouped:
        grouping, label_mode, budget, i, j = keys
        values = frame["gamma"].to_numpy(dtype=float)
        ci_seed = (
            int(config["bootstrap"]["seed"])
            + int(budget) * 1000
            + int(i) * 100
            + int(j) * 10
            + (0 if label_mode == "pseudo" else 1)
            + (0 if grouping == "competence" else 100000)
        )
        ci_low, ci_high = bootstrap_mean_ci(
            values,
            seed=ci_seed,
            replicates=int(config["bootstrap"]["replicates"]),
        )
        rows.append(
            {
                "scope": "pair",
                "grouping": grouping,
                "label_mode": label_mode,
                "budget": int(budget),
                "i": int(i),
                "j": int(j),
                "n": int(values.size),
                "mean_gamma": float(np.mean(values)),
                "std_gamma": float(np.std(values, ddof=1)),
                "median_gamma": float(np.median(values)),
                "min_gamma": float(np.min(values)),
                "max_gamma": float(np.max(values)),
                "fraction_positive": float(np.mean(values > 0.0)),
                "fraction_negative": float(np.mean(values < 0.0)),
                "bootstrap95_low": ci_low,
                "bootstrap95_high": ci_high,
            }
        )

    primary = gamma[(gamma["grouping"] == "competence") & (gamma["label_mode"] == "pseudo")]
    for budget, frame in primary.groupby("budget", sort=True):
        values = frame["gamma"].to_numpy(dtype=float)
        ci_low, ci_high = bootstrap_mean_ci(
            values,
            seed=int(config["bootstrap"]["seed"]) + int(budget) * 10000,
            replicates=int(config["bootstrap"]["replicates"]),
        )
        rows.append(
            {
                "scope": "global_primary",
                "grouping": "competence",
                "label_mode": "pseudo",
                "budget": int(budget),
                "i": "all",
                "j": "all",
                "n": int(values.size),
                "mean_gamma": float(np.mean(values)),
                "std_gamma": float(np.std(values, ddof=1)),
                "median_gamma": float(np.median(values)),
                "min_gamma": float(np.min(values)),
                "max_gamma": float(np.max(values)),
                "fraction_positive": float(np.mean(values > 0.0)),
                "fraction_negative": float(np.mean(values < 0.0)),
                "bootstrap95_low": ci_low,
                "bootstrap95_high": ci_high,
            }
        )
    return rows


def _classification(summary: pd.DataFrame) -> str:
    primary = summary[summary["scope"] == "pair"]
    primary = primary[
        (primary["grouping"] == "competence")
        & (primary["label_mode"] == "pseudo")
    ]
    if primary.empty:
        return "PILOT INCONCLUSIVE"
    ratios = np.abs(primary["mean_gamma"]) / primary["std_gamma"].replace(0.0, np.nan)
    max_ratio = float(ratios.max(skipna=True)) if ratios.notna().any() else 0.0
    has_both_signs = bool(
        (primary["fraction_positive"] > 0.0).any()
        and (primary["fraction_negative"] > 0.0).any()
    )
    if max_ratio > 2.0 and not has_both_signs:
        return "INTERACTION DETECTED"
    if max_ratio > 0.25 or has_both_signs:
        return "WEAK / UNSTABLE INTERACTION"
    return "APPROXIMATELY MODULAR"


def _make_figures(
    result_dir: Path,
    gamma: pd.DataFrame,
    delta: pd.DataFrame,
    stability: pd.DataFrame,
    budgets: list[int],
) -> None:
    primary = gamma[
        (gamma["grouping"] == "competence") & (gamma["label_mode"] == "pseudo")
    ]
    for budget in budgets:
        means = primary[primary["budget"] == budget].groupby(["i", "j"])["gamma"].mean()
        matrix = np.full((4, 4), np.nan)
        for (i, j), value in means.items():
            matrix[int(i) - 1, int(j) - 1] = value
            matrix[int(j) - 1, int(i) - 1] = value
        fig, ax = plt.subplots(figsize=(5, 4))
        image = ax.imshow(matrix, cmap="coolwarm", aspect="auto")
        ax.set_title(f"Mean Gamma, competence/pseudo, B={budget}")
        ax.set_xlabel("competence j")
        ax.set_ylabel("competence i")
        ax.set_xticks(range(4), range(1, 5))
        ax.set_yticks(range(4), range(1, 5))
        fig.colorbar(image, ax=ax, label="mean Gamma")
        fig.tight_layout()
        fig.savefig(result_dir / f"gamma_heatmap_B{budget}.png", dpi=140)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot(
        [primary[primary["budget"] == budget]["gamma"].to_numpy() for budget in budgets],
        tick_labels=[str(budget) for budget in budgets],
    )
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xlabel("transfer budget B per competence")
    ax.set_ylabel("Gamma")
    ax.set_title("Gamma distribution by budget, competence/pseudo")
    fig.tight_layout()
    fig.savefig(result_dir / "gamma_distribution.png", dpi=140)
    plt.close(fig)

    delta_primary = delta[
        (delta["grouping"] == "competence")
        & (delta["label_mode"] == "pseudo")
        & (delta["budget"] == 20)
    ]
    matrix = delta_primary.pivot_table(
        index="intervention", columns="competence", values="delta", aggfunc="mean"
    ).sort_index()
    fig, ax = plt.subplots(figsize=(7, 4))
    image = ax.imshow(matrix.to_numpy(), cmap="coolwarm", aspect="auto")
    ax.set_title("Mean competence effects, B=20, competence/pseudo")
    ax.set_xlabel("measured competence")
    ax.set_ylabel("intervention competence")
    ax.set_xticks(range(4), range(1, 5))
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    fig.colorbar(image, ax=ax, label="Delta score")
    fig.tight_layout()
    fig.savefig(result_dir / "delta_effects_B20.png", dpi=140)
    plt.close(fig)

    if not stability.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(stability["ari"], bins=8, range=(0.0, 1.0), edgecolor="black")
        ax.set_xlabel("ARI")
        ax.set_ylabel("seed pairs")
        ax.set_title("Competence clustering stability")
        fig.tight_layout()
        fig.savefig(result_dir / "clustering_stability.png", dpi=140)
        plt.close(fig)


def run(config_path: Path, result_dir: Path) -> dict[str, object]:
    config = json.loads(config_path.read_text())
    result_dir.mkdir(parents=True, exist_ok=True)
    (result_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")

    from sklearn.datasets import load_digits

    dataset = load_digits()
    X = dataset.data
    y = dataset.target
    budgets = [int(value) for value in config["budgets"]]
    seeds = [int(value) for value in config["seeds"]]
    baseline_rows: list[dict[str, object]] = []
    profile_rows: list[dict[str, object]] = []
    assignment_rows: list[dict[str, object]] = []
    split_rows: list[dict[str, object]] = []
    transfer_rows: list[dict[str, object]] = []
    model_rows: list[dict[str, object]] = []
    gamma_rows: list[dict[str, object]] = []
    delta_rows: list[dict[str, object]] = []
    competence_assignments: dict[int, np.ndarray] = {}
    fit_count = 0
    warnings_seen: list[str] = []
    started = time.perf_counter()

    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        for seed in seeds:
            splits = stratified_four_way_indices(y, seed)
            split_rows.extend(_split_membership_rows(seed, splits))
            train_idx = splits["train"]
            transfer_idx = splits["transfer"]
            validation_idx = splits["validation"]
            test_idx = splits["test"]

            fast0 = _fit_fast(X[train_idx], y[train_idx], seed)
            deep = _fit_deep(X[train_idx], y[train_idx], seed)
            fit_count += 2
            baseline_rows.extend(
                [
                    {
                        "seed": seed,
                        "model": "F_0",
                        "validation_balanced_accuracy": _global_score(
                            fast0, X[validation_idx], y[validation_idx]
                        ),
                        "test_balanced_accuracy": _global_score(
                            fast0, X[test_idx], y[test_idx]
                        ),
                    },
                    {
                        "seed": seed,
                        "model": "D",
                        "validation_balanced_accuracy": _global_score(
                            deep, X[validation_idx], y[validation_idx]
                        ),
                        "test_balanced_accuracy": _global_score(
                            deep, X[test_idx], y[test_idx]
                        ),
                    },
                ]
            )

            profiles = normalized_confusion_profiles(
                y[validation_idx], fast0.predict(X[validation_idx]), N_CLASSES
            )
            assignments = cluster_competence_profiles(profiles, 4)
            competence_assignments[seed] = assignments
            competence_groups = _groups_from_assignments(assignments)
            random_groups = _random_groups(
                [len(classes) for classes in competence_groups], seed + 1000003
            )
            for class_id in range(N_CLASSES):
                profile_rows.append(
                    {
                        "seed": seed,
                        "class": class_id,
                        **{f"profile_{target}": float(profiles[class_id, target]) for target in range(N_CLASSES)},
                    }
                )
            for grouping, groups in (
                ("competence", competence_groups),
                ("random", random_groups),
            ):
                for group_id, classes in enumerate(groups, start=1):
                    assignment_rows.append(
                        {
                            "seed": seed,
                            "grouping": grouping,
                            "competence": group_id,
                            "classes": _json(classes),
                            "size": len(classes),
                        }
                    )

            f0_test = _global_score(fast0, X[test_idx], y[test_idx])
            f0_val = _global_score(fast0, X[validation_idx], y[validation_idx])
            f0_group_scores = _competence_scores(
                fast0, X[test_idx], y[test_idx], competence_groups
            )
            for grouping, groups in (
                ("competence", competence_groups),
                ("random", random_groups),
            ):
                for label_mode in LABEL_MODES:
                    for budget in budgets:
                        selected_by_group: dict[int, np.ndarray] = {}
                        labels_by_group: dict[int, dict[str, np.ndarray]] = {}
                        for group_id, classes in enumerate(groups, start=1):
                            selected = select_transfer_indices(
                                y[transfer_idx],
                                classes,
                                budget,
                                seed * 100000 + budget * 100 + group_id,
                            )
                            selected_by_group[group_id] = selected
                            pseudo_labels = deep.classes_[
                                np.argmax(deep.predict_proba(X[transfer_idx[selected]]), axis=1)
                            ]
                            labels_by_group[group_id] = {
                                "pseudo": pseudo_labels,
                                "true": y[transfer_idx[selected]],
                            }
                            transfer_rows.append(
                                {
                                    "seed": seed,
                                    "grouping": grouping,
                                    "label_mode": label_mode,
                                    "budget": budget,
                                    "competence": group_id,
                                    "classes": _json(classes),
                                    "requested_examples": budget,
                                    "actual_examples": int(selected.size),
                                    "transfer_indices": _json(transfer_idx[selected].tolist()),
                                }
                            )

                        values: dict[str, float] = {"0": f0_test}
                        value_validation: dict[str, float] = {"0": f0_val}
                        group_scores: dict[str, list[float]] = {"0": f0_group_scores}
                        model_rows.append(
                            {
                                "seed": seed,
                                "grouping": grouping,
                                "label_mode": label_mode,
                                "budget": budget,
                                "intervention": "0",
                                "source_groups": "[]",
                                "actual_examples": 0,
                                "validation_balanced_accuracy": f0_val,
                                "test_balanced_accuracy": f0_test,
                            }
                        )
                        for group_id, classes in enumerate(groups, start=1):
                            intervention = str(group_id)
                            selected = selected_by_group[group_id]
                            train_indices = np.concatenate((train_idx, transfer_idx[selected]))
                            train_labels = np.concatenate(
                                (y[train_idx], labels_by_group[group_id][label_mode])
                            )
                            model = _fit_fast(X[train_indices], train_labels, seed)
                            fit_count += 1
                            values[intervention] = _global_score(model, X[test_idx], y[test_idx])
                            value_validation[intervention] = _global_score(
                                model, X[validation_idx], y[validation_idx]
                            )
                            group_scores[intervention] = _competence_scores(
                                model, X[test_idx], y[test_idx], competence_groups
                            )
                            model_rows.append(
                                {
                                    "seed": seed,
                                    "grouping": grouping,
                                    "label_mode": label_mode,
                                    "budget": budget,
                                    "intervention": intervention,
                                    "source_groups": _json([group_id]),
                                    "actual_examples": int(selected.size),
                                    "validation_balanced_accuracy": value_validation[intervention],
                                    "test_balanced_accuracy": values[intervention],
                                }
                            )
                            for measured_group, score in enumerate(group_scores[intervention], start=1):
                                delta_rows.append(
                                    {
                                        "seed": seed,
                                        "grouping": grouping,
                                        "label_mode": label_mode,
                                        "budget": budget,
                                        "intervention": intervention,
                                        "competence": measured_group,
                                        "score": score,
                                        "delta": delta_vector([score], [f0_group_scores[measured_group - 1]])[0],
                                    }
                                )

                        for i, j in combinations(range(1, len(groups) + 1), 2):
                            intervention = f"{i}+{j}"
                            selected_i = selected_by_group[i]
                            selected_j = selected_by_group[j]
                            selected = np.concatenate((selected_i, selected_j))
                            train_indices = np.concatenate((train_idx, transfer_idx[selected]))
                            train_labels = np.concatenate(
                                (
                                    y[train_idx],
                                    labels_by_group[i][label_mode],
                                    labels_by_group[j][label_mode],
                                )
                            )
                            model = _fit_fast(X[train_indices], train_labels, seed)
                            fit_count += 1
                            values[intervention] = _global_score(model, X[test_idx], y[test_idx])
                            value_validation[intervention] = _global_score(
                                model, X[validation_idx], y[validation_idx]
                            )
                            model_rows.append(
                                {
                                    "seed": seed,
                                    "grouping": grouping,
                                    "label_mode": label_mode,
                                    "budget": budget,
                                    "intervention": intervention,
                                    "source_groups": _json([i, j]),
                                    "actual_examples": int(selected.size),
                                    "validation_balanced_accuracy": value_validation[intervention],
                                    "test_balanced_accuracy": values[intervention],
                                }
                            )
                            gamma_rows.append(
                                {
                                    "seed": seed,
                                    "grouping": grouping,
                                    "label_mode": label_mode,
                                    "budget": budget,
                                    "i": i,
                                    "j": j,
                                    "classes_i": _json(groups[i - 1]),
                                    "classes_j": _json(groups[j - 1]),
                                    "actual_examples_i": int(selected_i.size),
                                    "actual_examples_j": int(selected_j.size),
                                    "v0": values["0"],
                                    "vi": values[str(i)],
                                    "vj": values[str(j)],
                                    "vij": values[intervention],
                                    "gamma": gamma_value(
                                        values["0"], values[str(i)], values[str(j)], values[intervention]
                                    ),
                                }
                            )
        warnings_seen = [str(item.message) for item in caught_warnings]

    assignments_by_seed = [competence_assignments[seed] for seed in seeds]
    stability_rows: list[dict[str, object]] = []
    for (seed_i, assignment_i), (seed_j, assignment_j) in combinations(
        zip(seeds, assignments_by_seed), 2
    ):
        stability_rows.append(
            {
                "seed_i": seed_i,
                "seed_j": seed_j,
                "ari": float(adjusted_rand_score(assignment_i, assignment_j)),
            }
        )

    baseline = pd.DataFrame(baseline_rows)
    profiles = pd.DataFrame(profile_rows)
    assignments = pd.DataFrame(assignment_rows)
    split_membership = pd.DataFrame(split_rows)
    transfers = pd.DataFrame(transfer_rows)
    models = pd.DataFrame(model_rows)
    gamma = pd.DataFrame(gamma_rows)
    delta = pd.DataFrame(delta_rows)
    stability = pd.DataFrame(stability_rows)
    summary = pd.DataFrame(_summary_rows(gamma, config))
    classification = _classification(summary)
    elapsed = time.perf_counter() - started

    baseline.to_csv(result_dir / "baseline_metrics.csv", index=False)
    profiles.to_csv(result_dir / "competence_profiles.csv", index=False)
    assignments.to_csv(result_dir / "competence_assignments.csv", index=False)
    split_membership.to_csv(result_dir / "split_membership.csv", index=False)
    transfers.to_csv(result_dir / "transfer_selection.csv", index=False)
    models.to_csv(result_dir / "model_results.csv", index=False)
    gamma.to_csv(result_dir / "gamma.csv", index=False)
    delta.to_csv(result_dir / "delta.csv", index=False)
    stability.to_csv(result_dir / "stability.csv", index=False)
    summary.to_csv(result_dir / "summary.csv", index=False)
    _make_figures(result_dir, gamma, delta, stability, budgets)

    summary_payload = {
        "experiment_id": config["experiment_id"],
        "status": "OBSERVED",
        "pilot_classification": classification,
        "classification_rule": "descriptive ratio of primary mean Gamma to seed std; no inferential claim",
        "dataset": "load_digits",
        "seeds": seeds,
        "budgets": budgets,
        "fit_count": fit_count,
        "elapsed_seconds": elapsed,
        "warning_count": len(warnings_seen),
        "warnings": sorted(set(warnings_seen)),
        "f0_validation_mean": float(baseline.loc[baseline.model == "F_0", "validation_balanced_accuracy"].mean()),
        "f0_test_mean": float(baseline.loc[baseline.model == "F_0", "test_balanced_accuracy"].mean()),
        "deep_validation_mean": float(baseline.loc[baseline.model == "D", "validation_balanced_accuracy"].mean()),
        "deep_test_mean": float(baseline.loc[baseline.model == "D", "test_balanced_accuracy"].mean()),
        "clustering_ari_mean": float(stability["ari"].mean()),
        "clustering_ari_std": float(stability["ari"].std(ddof=1)),
        "clustering_ari_min": float(stability["ari"].min()),
        "clustering_ari_max": float(stability["ari"].max()),
        "results": "OBSERVED descriptive pilot outputs; not evidence of novelty or superiority",
    }
    (result_dir / "summary.json").write_text(json.dumps(summary_payload, indent=2) + "\n")
    return summary_payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).with_name("config.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "pilots" / "b1_empirical_interaction",
    )
    args = parser.parse_args()
    summary = run(args.config, args.output_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
