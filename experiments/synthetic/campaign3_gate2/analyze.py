"""Minimum descriptive analysis for Campaign 3 Gate 2."""

from __future__ import annotations

import hashlib
import json
from itertools import combinations, permutations
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "diagnostics" / "campaign3_gate2"
BEHAVIORS = ("D00", "D10", "D01", "D11", "DbetaU")
MODES = ("Q00", "Q10", "Q01", "Q11")
PAIRS = tuple(combinations(MODES, 2))
BEHAVIOR_PAIRS = tuple(combinations(BEHAVIORS, 2))
PERMS = tuple(permutations(range(3)))
TOLERANCE = 1e-12


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def parse_matrix(series: pd.Series, shape: tuple[int, ...]) -> np.ndarray:
    return np.asarray([json.loads(value) for value in series], dtype=float).reshape((len(series),) + shape)


def team_distances(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return np.min(np.stack([np.linalg.norm(left - right[:, perm, :], axis=(1, 2)) for perm in PERMS]), axis=0)


def summarize(values: np.ndarray) -> dict[str, float]:
    q = np.quantile(values, (0.5, 0.75, 0.9, 0.95, 0.99))
    return {"mean": float(values.mean()), "q50": float(q[0]), "q75": float(q[1]),
            "q90": float(q[2]), "q95": float(q[3]), "q99": float(q[4]),
            "max": float(values.max()), "nonzero_rate": float((values > TOLERANCE).mean())}


def main() -> None:
    states = pd.read_csv(OUT / "factual_states.csv.gz")
    histories = pd.read_csv(OUT / "factual_histories.csv.gz")
    if len(states) != 378_000 or len(histories) != 10_500:
        raise RuntimeError("Gate 2 raw counts invalid")
    key = ["team_id", "kernel_id", "replicate", "clock"]

    kx_rows = []
    for source, frame in [("overall", states), *states.groupby("behavior", sort=False)]:
        counts = frame.K_X.value_counts().reindex((1, 2, 3, 4), fill_value=0)
        for k, count in counts.items():
            kx_rows.append({"source": source, "K_X": k, "count": int(count), "rate": float(count / len(frame))})
    pd.DataFrame(kx_rows).to_csv(OUT / "action_diversity_KX.csv", index=False)

    divergence_rows = []
    for source, frame in [("overall", states), *states.groupby("behavior", sort=False)]:
        for left, right in PAIRS:
            divergent = frame[f"action_{left}"] != frame[f"action_{right}"]
            divergence_rows.append({"source": source, "mode_left": left, "mode_right": right,
                                    "states": len(frame), "divergence_count": int(divergent.sum()),
                                    "divergence_rate": float(divergent.mean())})
    pd.DataFrame(divergence_rows).to_csv(OUT / "pairwise_action_divergence.csv", index=False)

    indexed = {behavior: frame.sort_values(key).reset_index(drop=True) for behavior, frame in states.groupby("behavior")}
    reference_keys = indexed["D11"][key]
    if any(not indexed[b][key].equals(reference_keys) for b in BEHAVIORS):
        raise RuntimeError("paired behavior-state keys are not aligned")
    s_arrays = {b: parse_matrix(indexed[b].state_before, (3, 2)) for b in BEHAVIORS}
    b_arrays = {b: parse_matrix(indexed[b].belief_before, (3,)) for b in BEHAVIORS}

    trajectory_rows = []
    paired_cache: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
    clocks = indexed["D11"].clock.to_numpy()
    for left, right in BEHAVIOR_PAIRS:
        sd = team_distances(s_arrays[left], s_arrays[right])
        bd = np.abs(b_arrays[left] - b_arrays[right]).sum(axis=1)
        paired_cache[(left, right)] = (sd, bd)
        for clock in ("all", *range(1, 37)):
            mask = np.ones(len(clocks), dtype=bool) if clock == "all" else clocks == clock
            for component, values in (("S_dS", sd), ("b_L1", bd)):
                trajectory_rows.append({"clock": clock, "source_left": left, "source_right": right,
                                        "component": component, "states": int(mask.sum()),
                                        **summarize(values[mask])})
    pd.DataFrame(trajectory_rows).to_csv(OUT / "trajectory_diversity_by_clock.csv", index=False)

    support_rows = []
    for behavior in BEHAVIORS:
        if behavior == "D11":
            sd = np.zeros(len(clocks)); bd = np.zeros(len(clocks))
        else:
            pair = tuple(sorted((behavior, "D11"), key=BEHAVIORS.index))
            sd, bd = paired_cache[pair]
        for component, values in (("S_dS_to_paired_D11", sd), ("b_L1_to_paired_D11", bd)):
            support_rows.append({"source": behavior, "component": component, "states": len(values), **summarize(values)})

    beta_s = np.min(np.stack([paired_cache[(fixed, "DbetaU")][0] for fixed in BEHAVIORS[:-1]]), axis=0)
    beta_b = np.min(np.stack([paired_cache[(fixed, "DbetaU")][1] for fixed in BEHAVIORS[:-1]]), axis=0)
    for component, values in (("S_dS_beta_to_paired_fixed_union", beta_s), ("b_L1_beta_to_paired_fixed_union", beta_b)):
        support_rows.append({"source": "DbetaU_increment", "component": component, "states": len(values), **summarize(values)})
    pd.DataFrame(support_rows).to_csv(OUT / "observable_support_summary.csv", index=False)

    fixed_s_beyond = np.max(np.stack([paired_cache[(b, "D11")][0] for b in ("D00", "D10", "D01")]), axis=0)
    fixed_b_beyond = np.max(np.stack([paired_cache[(b, "D11")][1] for b in ("D00", "D10", "D01")]), axis=0)
    summary = {
        "artifact_type": "campaign3_gate2_minimum_analysis",
        "counts": {"histories": len(histories), "states": len(states), "states_per_source": 75_600},
        "distances": {"S": "frozen quotient Frobenius d_S", "b": "L1 distance on probability vectors", "combined": None},
        "numerical_equality_tolerance": TOLERANCE,
        "fixed_sources_beyond_D11": {
            "S_nonzero_rate": float((fixed_s_beyond > TOLERANCE).mean()),
            "b_nonzero_rate": float((fixed_b_beyond > TOLERANCE).mean()),
        },
        "beta_increment_beyond_paired_fixed_union": {
            "S_nonzero_rate": float((beta_s > TOLERANCE).mean()),
            "b_nonzero_rate": float((beta_b > TOLERANCE).mean()),
        },
        "selector_observable": ["S", "b", "tau"],
        "forbidden_selector_dimensions": ["true_p_or_z", "C", "N", "M", "phi", "true_reward", "future_information"],
        "counterfactual_value_targets": 0, "predictor_or_metacontroller_training": False,
        "heldout_execution": False,
    }
    output_names = ["action_diversity_KX.csv", "pairwise_action_divergence.csv", "trajectory_diversity_by_clock.csv", "observable_support_summary.csv"]
    summary["sha256"] = {name: digest(OUT / name) for name in output_names}
    dump(OUT / "analysis_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
