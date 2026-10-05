"""Run the fixed-physics G3-H structural autopsy diagnostic."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter
from pathlib import Path
from time import perf_counter

import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

from hls.g3_h_regime_map import REGIME_TOL
from hls.g3_h_structural_autopsy import (
    MAIN_REGIMES,
    Population,
    feature_columns,
    generate_population,
    iter_action_rows,
    local_feature_row,
    local_rule_flags,
)


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = ROOT / "results/foundations/g3_h_structural_autopsy"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path.name}")
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def git_revision() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def rule_audit(populations: list[Population]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    targets = {
        "all_action_transitions_identity": ("USE sufficient", lambda point: point.regret_use <= REGIME_TOL),
        "no_immediate_crossing": ("USE sufficient", lambda point: point.regret_use <= REGIME_TOL),
        "unique_use_and_no_immediate_crossing": ("USE sufficient", lambda point: point.regret_use <= REGIME_TOL),
        "use_local_optimal_overlap": ("USE sufficient", lambda point: point.regret_use <= REGIME_TOL),
        "unique_local_and_no_immediate_crossing": ("LOCAL sufficient", lambda point: point.regret_local <= REGIME_TOL),
    }
    for population in populations:
        for rule, (target, succeeds) in targets.items():
            selected = [point for point in population.retained if local_rule_flags(point)[rule]]
            correct = sum(succeeds(point) for point in selected)
            rows.append(
                {
                    "audit_scope": "retained_balanced_diagnostic_set",
                    "condition": population.condition,
                    "rule": rule,
                    "target": target,
                    "support": len(selected),
                    "coverage": len(selected) / len(population.retained),
                    "correct": correct,
                    "violations": len(selected) - correct,
                    "finite_audit_correctness": None if not selected else correct / len(selected),
                }
            )
    return rows


def independent_rule_audit(*, condition: str, seed: int, samples: int) -> list[dict[str, object]]:
    """Try to falsify candidate rules on fresh, unretained interior draws."""
    # Imports here keep the normal reporting path explicit about the sampler.
    from random import Random
    from hls.g3_h_regime_map import evaluate_point
    from hls.g3_h_regime_search import _interior_state, _learning_profile

    rng = Random(seed)
    tracked = {
        "no_immediate_crossing": ("USE sufficient", lambda point: point.regret_use <= REGIME_TOL),
        "unique_use_and_no_immediate_crossing": ("USE sufficient", lambda point: point.regret_use <= REGIME_TOL),
        "unique_local_and_no_immediate_crossing": ("LOCAL sufficient", lambda point: point.regret_local <= REGIME_TOL),
    }
    support = {key: 0 for key in tracked}
    correct = {key: 0 for key in tracked}
    for _ in range(samples):
        point = evaluate_point(_interior_state(rng), _learning_profile(rng, condition))
        flags = local_rule_flags(point)
        for rule, (_, predicate) in tracked.items():
            if flags[rule]:
                support[rule] += 1
                correct[rule] += predicate(point)
    return [
        {
            "audit_scope": "fresh_unretained_adversarial_draws",
            "condition": condition,
            "rule": rule,
            "target": target,
            "support": support[rule],
            "coverage": support[rule] / samples,
            "correct": correct[rule],
            "violations": support[rule] - correct[rule],
            "finite_audit_correctness": None if not support[rule] else correct[rule] / support[rule],
            "draws": samples,
            "seed": seed,
        }
        for rule, (target, _) in tracked.items()
    ]


def nearest_pairs(rows: list[dict[str, object]], condition: str) -> list[dict[str, object]]:
    columns = feature_columns()
    output: list[dict[str, object]] = []
    for left, right in (("R0_USE_SUFFICIENT", "R2_LOCAL_INSUFFICIENT"), ("R1_LOCAL_NECESSARY_SUFFICIENT", "R2_LOCAL_INSUFFICIENT")):
        a = [row for row in rows if row["condition"] == condition and row["regime_oracle_label"] == left]
        b = [row for row in rows if row["condition"] == condition and row["regime_oracle_label"] == right]
        combined = a + b
        scales = {column: max(np.std([float(row[column]) for row in combined]), 1e-12) for column in columns}
        best = None
        for first in a:
            for second in b:
                distance = float(np.sqrt(sum(((float(first[c]) - float(second[c])) / scales[c]) ** 2 for c in columns)))
                if best is None or distance < best[0]:
                    best = (distance, first, second)
        assert best is not None
        distance, first, second = best
        output.append(
            {
                "condition": condition,
                "regime_pair": f"{left} vs {right}",
                "standardized_local_feature_distance": distance,
                "first_point_id": first["point_id"],
                "second_point_id": second["point_id"],
                "first_state": first["state"], "first_eta": first["eta"],
                "second_state": second["state"], "second_eta": second["eta"],
                "first_regret_U": first["regret_U_oracle_label"], "first_regret_L": first["regret_L_oracle_label"],
                "second_regret_U": second["regret_U_oracle_label"], "second_regret_L": second["regret_L_oracle_label"],
            }
        )
    return output


def probe(rows: list[dict[str, object]], condition: str) -> dict[str, object]:
    subset = [row for row in rows if row["condition"] == condition]
    cols = feature_columns()
    x = np.array([[float(row[column]) for column in cols] for row in subset])
    y = np.array([str(row["regime_oracle_label"]) for row in subset])
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.30, random_state=20261005, stratify=y)
    model = DecisionTreeClassifier(max_depth=3, min_samples_leaf=10, random_state=20261005)
    model.fit(train_x, train_y)
    prediction = model.predict(test_x)
    matrix = confusion_matrix(test_y, prediction, labels=list(MAIN_REGIMES)).tolist()
    return {
        "condition": condition,
        "features": list(cols),
        "train_size": len(train_y), "test_size": len(test_y),
        "accuracy": accuracy_score(test_y, prediction),
        "balanced_accuracy": balanced_accuracy_score(test_y, prediction),
        "labels": list(MAIN_REGIMES), "confusion_matrix": matrix,
        "tree": export_text(model, feature_names=list(cols)),
        "feature_importances": {column: float(value) for column, value in zip(cols, model.feature_importances_) if value},
    }


def tension_summary(rows: list[dict[str, object]]) -> dict[str, dict[str, dict[str, float]]]:
    """Describe, but do not fit, the canonical local M advantage over USE."""
    result: dict[str, dict[str, dict[str, float]]] = {}
    for condition in ("homogeneous", "heterogeneous"):
        result[condition] = {}
        for regime in MAIN_REGIMES:
            subset = [row for row in rows if row["condition"] == condition and row["regime_oracle_label"] == regime]
            values = []
            for row in subset:
                m_values = [float(row[f"M_({i},{j})"]) for i, j in ((1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2))]
                use_actions = json.loads(str(row["A_U"]))
                use_m = [float(row[f"M_{action}"]) for action in use_actions]
                values.append(max(m_values) - max(use_m))
            result[condition][regime] = {"min": float(np.min(values)), "median": float(np.median(values)), "max": float(np.max(values))}
    return result


def action_autopsy_summary(populations: list[Population]) -> dict[str, object]:
    """Oracle-labelled comparison of the selected action sets, never a feature."""
    result: dict[str, object] = {}
    for population in populations:
        by_regime: dict[str, object] = {}
        for regime in MAIN_REGIMES:
            points = [point for point in population.retained if point.regime == regime]
            reward_sacrifices = [
                min(record.operational_gap for record in point.actions if record.action in point.optimal_dynamic)
                for point in points
            ]
            development_advantages = [
                max(record.development for record in point.actions if record.action in point.optimal_dynamic)
                - max(record.development for record in point.actions if record.action in point.optimal_use)
                for point in points
            ]
            local_matches_use = sum(bool(point.optimal_use & point.optimal_local) for point in points)
            by_regime[regime] = {
                "points": len(points),
                "use_local_optimal_overlap": local_matches_use,
                "median_oracle_current_reward_sacrifice": float(np.median(reward_sacrifices)),
                "median_oracle_minus_use_development": float(np.median(development_advantages)),
            }
        result[population.condition] = by_regime
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--quota", type=int, default=250)
    parser.add_argument("--homogeneous-maximum", type=int, default=30000)
    parser.add_argument("--heterogeneous-maximum", type=int, default=10000)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    start = perf_counter()
    populations = [
        generate_population(condition="homogeneous", seed=20261005, quota_per_regime=args.quota, maximum_samples=args.homogeneous_maximum),
        generate_population(condition="heterogeneous", seed=20261006, quota_per_regime=args.quota, maximum_samples=args.heterogeneous_maximum),
    ]
    point_rows: list[dict[str, object]] = []
    action_rows: list[dict[str, object]] = []
    for population in populations:
        for point_id, evaluation in enumerate(population.retained):
            point_rows.append({"point_id": point_id, "condition": population.condition, **local_feature_row(evaluation)})
        action_rows.extend(iter_action_rows(population))
    rules = rule_audit(populations)
    rules.extend(independent_rule_audit(condition="homogeneous", seed=20261007, samples=10000))
    rules.extend(independent_rule_audit(condition="heterogeneous", seed=20261008, samples=10000))
    pairs = [pair for condition in ("homogeneous", "heterogeneous") for pair in nearest_pairs(point_rows, condition)]
    probes = {condition: probe(point_rows, condition) for condition in ("homogeneous", "heterogeneous")}
    write_csv(args.output / "diagnostic_points.csv", point_rows)
    write_csv(args.output / "action_diagnostics.csv", action_rows)
    write_csv(args.output / "simple_rules.csv", rules)
    write_csv(args.output / "certificate_audit.csv", rules)
    write_csv(args.output / "near_indistinguishable_pairs.csv", pairs)
    (args.output / "statistical_probe_summary.json").write_text(json.dumps(probes, indent=2) + "\n")
    summary = {
        "population": [{"condition": item.condition, "generated": item.generated, "original_regime_counts": item.regime_counts, "original_r2_reversion_count": item.reversion_count, "retained_counts": dict(Counter(point.regime for point in item.retained))} for item in populations],
        "algebraic_identities": ["M(S,a)=R(S,a)+D(S,a)", "g(bar,x)=max_a R(S,a)-R(S,x) for bar in A_U*", "m(bar,x)=g(bar,x)-rho(bar,x)=R(F(S,x),bar)-R(F(S,x),x)", "immediate_crossing iff m < -REGIME_TOL"],
        "probe": probes,
        "natural_local_tension": {
            "quantity": "max_a M(S,a) - max_{a in A_U*(S)} M(S,a)",
            "interpretation": "canonical local-value improvement available beyond current USE; descriptive only, not a regime rule",
            "by_condition_and_regime": tension_summary(point_rows),
        },
        "action_autopsy_oracle_labelled": action_autopsy_summary(populations),
        "runtime_seconds": perf_counter() - start,
    }
    (args.output / "structural_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    manifest = {
        "git_revision": git_revision(), "seed_homogeneous": 20261005, "seed_heterogeneous": 20261006,
        "state_sampler": "independent Uniform(1e-6, 1-1e-6) entries", "eta_sampler": "independent Exponential(rate=1); homogeneous profile repeats one draw",
        "eta_domain": "canonical finite nonnegative domain [0, infinity)", "tolerance": REGIME_TOL,
        "quota_per_main_regime": args.quota, "homogeneous_maximum": args.homogeneous_maximum, "heterogeneous_maximum": args.heterogeneous_maximum,
        "dynamic_value_role": "oracle label only; excluded from local feature vectors and rule conditions",
        "fresh_rule_audits": {"homogeneous": {"seed": 20261007, "samples": 10000}, "heterogeneous": {"seed": 20261008, "samples": 10000}},
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
