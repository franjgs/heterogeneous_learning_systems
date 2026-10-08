"""Frozen minimum analysis for Campaign 3 Gate 1."""

from __future__ import annotations

import csv
import hashlib
import json
from functools import cmp_to_key
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "results" / "campaigns" / "campaign3_horizon_pilot" / "initial_j12"
OUT = ROOT / "results" / "diagnostics" / "campaign3_gate1"
FREEZE = OUT / "pre_analysis_gate1.json"
MODES = ("Q00", "Q10", "Q01", "Q11")
NONREFERENCE = ("Q10", "Q01", "Q11")
CONTINUATIONS = ("Q00", "Q11")
PAIRS = tuple(combinations(MODES, 2))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def relation(left: float, right: float, tolerance: float) -> int:
    difference = left - right
    return 0 if abs(difference) <= tolerance else 1 if difference > 0 else -1


def sign_label(value: float, tolerance: float) -> str:
    sign = relation(value, 0.0, tolerance)
    return "POSITIVE" if sign > 0 else "NEGATIVE" if sign < 0 else "ZERO"


def deterministic_ranking(values: dict[str, float], tolerance: float) -> tuple[str, ...]:
    order = {mode: index for index, mode in enumerate(MODES)}

    def compare(left: str, right: str) -> int:
        rel = relation(values[left], values[right], tolerance)
        if rel:
            return -rel
        return -1 if order[left] < order[right] else 1 if order[left] > order[right] else 0

    return tuple(sorted(MODES, key=cmp_to_key(compare)))


def bootstrap_interval(values_by_history: np.ndarray, indices: np.ndarray, statistic: str) -> tuple[float, float]:
    sampled = values_by_history[indices].reshape(indices.shape[0], -1)
    if statistic == "mean":
        draws = sampled.mean(axis=1)
    elif statistic == "q95":
        draws = np.quantile(sampled, 0.95, axis=1)
    else:
        raise ValueError(statistic)
    return tuple(float(value) for value in np.quantile(draws, (0.025, 0.975)))


def history_matrix(frame: pd.DataFrame, column: str) -> np.ndarray:
    grouped = frame.sort_values(["history_id", "tau", "state_id"]).groupby("history_id", sort=True)[column].apply(list)
    if len(grouped) != 840 or len({len(values) for values in grouped}) != 1:
        raise RuntimeError("Gate 1 bootstrap requires balanced complete-history clusters")
    return np.asarray(grouped.tolist(), dtype=float)


def scopes(frame: pd.DataFrame):
    yield "overall", "all", frame
    for tau in (36, 35, 34):
        yield "tau", tau, frame[frame.tau == tau]


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    tolerance = float(freeze["mode_tie_break"]["tolerance"])
    branches = pd.read_csv(
        PILOT / "counterfactual_branch_returns.csv.gz",
        usecols=["state_id", "history_id", "team_id", "kernel_id", "problem_index", "decision", "initial_mode", "continuation", "ell", "G"],
    )
    branches = branches[(branches.problem_index == 1) & (branches.ell == 11)].copy()
    if len(branches) != 20_160:
        raise RuntimeError("Gate 1 requires 2,520 states x 4 modes x 2 continuations")
    if set(branches.initial_mode) != set(MODES) or set(branches.continuation) != set(CONTINUATIONS):
        raise RuntimeError("mode or continuation firewall failed")
    if set(branches.team_id) != set(freeze["team_ids"]) or set(branches.kernel_id) != set(freeze["kernel_ids"]):
        raise RuntimeError("development design mismatch")
    index_columns = ["state_id", "history_id", "team_id", "kernel_id", "problem_index", "decision"]
    wide = branches.pivot(index=index_columns, columns=["continuation", "initial_mode"], values="G").reset_index()
    wide.columns = [name if isinstance(name, str) else "__".join(part for part in name if part) for name in wide.columns]
    if len(wide) != 2_520:
        raise RuntimeError("Gate 1 state count mismatch")
    wide["tau"] = 3 * 12 - (wide["decision"] - 1)
    if set(wide.tau) != {34, 35, 36}:
        raise RuntimeError("tau derivation failed")

    diagnostic_rows = []
    regret_rows = []
    for row in wide.to_dict("records"):
        values = {
            continuation: {mode: float(row[f"{continuation}__{mode}"]) for mode in MODES}
            for continuation in CONTINUATIONS
        }
        rankings = {continuation: deterministic_ranking(values[continuation], tolerance) for continuation in CONTINUATIONS}
        best = {continuation: rankings[continuation][0] for continuation in CONTINUATIONS}
        signatures = {
            continuation: tuple(relation(values[continuation][left], values[continuation][right], tolerance) for left, right in PAIRS)
            for continuation in CONTINUATIONS
        }
        pairwise_agreement_count = sum(a == b for a, b in zip(signatures["Q00"], signatures["Q11"], strict=True))
        advantages = {
            continuation: {mode: values[continuation][mode] - values[continuation]["Q00"] for mode in NONREFERENCE}
            for continuation in CONTINUATIONS
        }
        regret_00_to_11 = values["Q11"][best["Q11"]] - values["Q11"][best["Q00"]]
        regret_11_to_00 = values["Q00"][best["Q00"]] - values["Q00"][best["Q11"]]
        if regret_00_to_11 < -tolerance or regret_11_to_00 < -tolerance:
            raise RuntimeError("cross-continuation regret must be nonnegative")
        base = {name: row[name] for name in index_columns}
        diag = {
            **base,
            "tau": int(row["tau"]),
            "best_Q00_continuation": best["Q00"],
            "best_Q11_continuation": best["Q11"],
            "best_mode_agreement": best["Q00"] == best["Q11"],
            "ranking_Q00": ">".join(rankings["Q00"]),
            "ranking_Q11": ">".join(rankings["Q11"]),
            "deterministic_ranking_agreement": rankings["Q00"] == rankings["Q11"],
            "pairwise_relation_agreement_count": pairwise_agreement_count,
            "pairwise_relation_agreement_fraction": pairwise_agreement_count / 6.0,
            "R_00_to_11": max(0.0, regret_00_to_11),
            "R_11_to_00": max(0.0, regret_11_to_00),
        }
        for continuation in CONTINUATIONS:
            for mode in NONREFERENCE:
                diag[f"A_{mode}_{continuation}"] = advantages[continuation][mode]
                diag[f"sign_{mode}_{continuation}"] = sign_label(advantages[continuation][mode], tolerance)
        diagnostic_rows.append(diag)
        for direction, regret in (("R_00_to_11", regret_00_to_11), ("R_11_to_00", regret_11_to_00)):
            regret_rows.append({
                "state_id": row["state_id"], "history_id": row["history_id"], "tau": int(row["tau"]),
                "direction": direction, "absolute_regret": max(0.0, regret),
            })

    diagnostics = pd.DataFrame(diagnostic_rows)
    regrets = pd.DataFrame(regret_rows)
    diagnostics_path = OUT / "gate1_state_diagnostics.csv"
    regret_path = OUT / "cross_continuation_regrets.csv"
    diagnostics.to_csv(diagnostics_path, index=False, float_format="%.17g")
    regrets.to_csv(regret_path, index=False, float_format="%.17g")

    best_rows = []
    contingency_rows = []
    sign_rows = []
    regret_summary_rows = []
    bootstrap_rows = []
    bootstrap_indices = np.load(PILOT / "bootstrap_history_indices.npy", allow_pickle=False)
    for scope, tau, frame in scopes(diagnostics):
        n = len(frame)
        best_agreement = frame.best_mode_agreement.astype(float)
        rank_agreement = frame.deterministic_ranking_agreement.astype(float)
        pair_agreement = frame.pairwise_relation_agreement_fraction.astype(float)
        best_rows.append({
            "scope": scope, "tau": tau, "states": n,
            "best_mode_agreement_count": int(best_agreement.sum()),
            "best_mode_agreement_rate": float(best_agreement.mean()),
            "deterministic_ranking_agreement_count": int(rank_agreement.sum()),
            "deterministic_ranking_agreement_rate": float(rank_agreement.mean()),
            "mean_pairwise_relation_agreement": float(pair_agreement.mean()),
        })
        for left in MODES:
            for right in MODES:
                count = int(((frame.best_Q00_continuation == left) & (frame.best_Q11_continuation == right)).sum())
                contingency_rows.append({"scope": scope, "tau": tau, "best_under_Q00": left, "best_under_Q11": right, "count": count, "rate": count / n})
        for mode in NONREFERENCE:
            left = frame[f"sign_{mode}_Q00"]
            right = frame[f"sign_{mode}_Q11"]
            record = {"scope": scope, "tau": tau, "mode": mode, "states": n,
                      "same_sign_count": int((left == right).sum()), "same_sign_rate": float((left == right).mean())}
            for left_sign in ("NEGATIVE", "ZERO", "POSITIVE"):
                for right_sign in ("NEGATIVE", "ZERO", "POSITIVE"):
                    record[f"{left_sign}_to_{right_sign}"] = int(((left == left_sign) & (right == right_sign)).sum())
            sign_rows.append(record)
        for direction in ("R_00_to_11", "R_11_to_00"):
            values = frame[direction].to_numpy(dtype=float)
            quantiles = np.quantile(values, (0.50, 0.75, 0.90, 0.95, 0.99))
            regret_summary_rows.append({
                "scope": scope, "tau": tau, "direction": direction, "states": n,
                "mean": float(values.mean()), "q50": quantiles[0], "q75": quantiles[1],
                "q90": quantiles[2], "q95": quantiles[3], "q99": quantiles[4], "max": float(values.max()),
            })

        metrics = {
            "best_mode_agreement_rate": best_agreement,
            "deterministic_ranking_agreement_rate": rank_agreement,
            "mean_pairwise_relation_agreement": pair_agreement,
        }
        for mode in NONREFERENCE:
            metrics[f"sign_agreement_{mode}"] = (frame[f"sign_{mode}_Q00"] == frame[f"sign_{mode}_Q11"]).astype(float)
        for metric, values in metrics.items():
            matrix = history_matrix(frame.assign(_metric=values), "_metric")
            low, high = bootstrap_interval(matrix, bootstrap_indices, "mean")
            bootstrap_rows.append({"scope": scope, "tau": tau, "metric": metric, "estimate": float(values.mean()), "ci_low": low, "ci_high": high})
        for direction in ("R_00_to_11", "R_11_to_00"):
            matrix = history_matrix(frame, direction)
            for statistic in ("mean", "q95"):
                estimate = float(matrix.mean()) if statistic == "mean" else float(np.quantile(matrix, 0.95))
                low, high = bootstrap_interval(matrix, bootstrap_indices, statistic)
                bootstrap_rows.append({"scope": scope, "tau": tau, "metric": f"{direction}_{statistic}", "estimate": estimate, "ci_low": low, "ci_high": high})

    write_csv(OUT / "best_mode_ranking_summary.csv", best_rows)
    write_csv(OUT / "best_mode_contingency.csv", contingency_rows)
    write_csv(OUT / "sign_stability_summary.csv", sign_rows)
    write_csv(OUT / "regret_summary.csv", regret_summary_rows)
    write_csv(OUT / "history_bootstrap_summary.csv", bootstrap_rows)
    manifest = {
        "artifact_type": "campaign3_gate1_minimum_analysis",
        "pre_analysis_freeze_sha256": digest(FREEZE),
        "source_branch_sha256": digest(PILOT / "counterfactual_branch_returns.csv.gz"),
        "state_source": "h ~ d_Q11",
        "operational_ell": 11,
        "tau_values": [36, 35, 34],
        "eligible_states": 2520,
        "branch_rows_used": 20160,
        "normalized_regret_metric": False,
        "materiality_threshold": None,
        "significance_tests": False,
        "heldout_execution": False,
        "gate_2": False,
        "predictor_or_metacontroller_training": False,
        "sha256": {
            path.name: digest(path)
            for path in (
                diagnostics_path, regret_path, OUT / "best_mode_ranking_summary.csv",
                OUT / "best_mode_contingency.csv", OUT / "sign_stability_summary.csv",
                OUT / "regret_summary.csv", OUT / "history_bootstrap_summary.csv",
            )
        },
    }
    dump(OUT / "analysis_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
