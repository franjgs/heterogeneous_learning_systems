"""Execute the generator-only Campaign 3 PGCG protocol."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.campaign3_problem_generator import (  # noqa: E402
    HYPOTHESES_P,
    executable_compositions,
    generator_transition,
    nominal_kernels,
    reflect,
    select_scales,
    simplex_lattice_degree4,
)
from hls.problem_geometry import production_distance  # noqa: E402


OUT = ROOT / "results" / "foundations" / "campaign3_pgcg"
SIGMAS = (0.01, 0.02, 0.04, 0.08, 0.16, 0.32)
CALIBRATION_N = 100_000
CALIBRATION_SEED = 20261008
CHARACTERIZATION_N = 10_000
CHARACTERIZATION_SEED = 20261009
J = 12
QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90, 0.95)


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def calibrate() -> tuple[list[dict], list[dict], tuple[float, float, float], dict]:
    rng = np.random.default_rng(CALIBRATION_SEED)
    p = rng.uniform(0.2, 0.8, CALIBRATION_N)
    u = rng.normal(size=CALIBRATION_N)
    c_by_sigma = []
    reflection_by_sigma = []
    rows, bins = [], []
    edges = np.linspace(0.2, 0.8, 13)
    for sigma in SIGMAS:
        raw = p + sigma * u
        p_next = reflect(raw)
        reflected = (raw < 0.2) | (raw > 0.8)
        c = np.abs(p - p_next) * (1.0 + np.abs(p + p_next - 1.0))
        delta = np.abs(p_next - p)
        values = np.quantile(c, QUANTILES)
        rows.append({
            "sigma": sigma, "n": CALIBRATION_N, "mean_C": c.mean(), "std_C": c.std(ddof=1),
            **{f"q{int(q*100):02d}_C": value for q, value in zip(QUANTILES, values)},
            "mean_abs_delta_p": delta.mean(), "median_abs_delta_p": np.median(delta),
            "reflection_rate": reflected.mean(),
        })
        c_by_sigma.append(c)
        reflection_by_sigma.append(reflected)
        indices = np.minimum(np.searchsorted(edges, p, side="right") - 1, 11)
        for index in range(12):
            mask = indices == index
            bins.append({"sigma": sigma, "bin": index + 1, "p_lower": edges[index],
                         "p_upper": edges[index + 1], "n": int(mask.sum()),
                         "median_C": float(np.median(c[mask])),
                         "reflection_rate": float(reflected[mask].mean())})
    medians = tuple(row["q50_C"] for row in rows)
    indices = select_scales(SIGMAS, medians)
    selected = tuple(SIGMAS[index] for index in indices)
    quantile_order = all(
        np.all(np.diff([row[f"q{int(q*100):02d}_C"] for row in rows]) > 0) for q in QUANTILES
    )
    empirical_distribution_order = all(
        np.all(np.sort(c_by_sigma[index + 1]) >= np.sort(c_by_sigma[index]))
        for index in range(len(SIGMAS) - 1)
    )
    median_order = bool(np.all(np.diff(medians) > 0))
    paired = []
    for left in range(len(SIGMAS) - 1):
        right = left + 1
        paired.append({"sigma_low": SIGMAS[left], "sigma_high": SIGMAS[right],
                       "fraction_high_gt_low": float(np.mean(c_by_sigma[right] > c_by_sigma[left])),
                       "fraction_equal": float(np.mean(c_by_sigma[right] == c_by_sigma[left]))})
    selected_bin_order = True
    for bin_index in range(12):
        selected_medians = [next(row["median_C"] for row in bins if row["sigma"] == sigma and row["bin"] == bin_index + 1) for sigma in selected]
        selected_bin_order &= bool(np.all(np.diff(selected_medians) > 0))
    audit = {"median_order_all_candidates": median_order, "quantile_order_all_candidates": quantile_order,
             "empirical_distribution_order_all_adjacent_candidates": empirical_distribution_order,
             "selected_bin_median_order_all_bins": selected_bin_order, "paired_adjacent": paired,
             "maximum_reflection_rate": max(row["reflection_rate"] for row in rows),
             "selected_indices": indices, "selected_sigmas": selected}
    return rows, bins, selected, audit


def characterize(kernels):
    histories = np.empty((len(kernels), CHARACTERIZATION_N, J), dtype=np.float64)
    mechanisms = np.zeros((len(kernels), CHARACTERIZATION_N, J - 1), dtype=np.uint8)
    flags = np.zeros((len(kernels), CHARACTERIZATION_N, J - 1), dtype=np.uint8)
    kernel_rows, step_rows = [], []
    mechanism_code = {"STAY": 0, "MOVE": 1, "RETURN": 2}
    for kernel_index, kernel in enumerate(kernels):
        rng = np.random.default_rng(np.random.SeedSequence([CHARACTERIZATION_SEED, kernel_index]))
        per_history = []
        for history_index in range(CHARACTERIZATION_N):
            values = [float(rng.uniform(0.2, 0.8))]
            transition_records = []
            for step in range(J - 1):
                transition = generator_transition(values, kernel, rng)
                values.append(transition.p_next)
                transition_records.append(transition)
                mechanisms[kernel_index, history_index, step] = mechanism_code[transition.mechanism]
                flags[kernel_index, history_index, step] = (
                    int(transition.return_unavailable) | (int(transition.renormalized) << 1) | (int(transition.reflected) << 2)
                )
            histories[kernel_index, history_index] = values
            changes = np.array([production_distance(values[j-1], values[j]) for j in range(1, J)])
            novelties = np.array([min(production_distance(values[j], prior) for prior in values[:j]) for j in range(1, J)])
            mismatches = np.array([min(production_distance(value, h) for h in HYPOTHESES_P) for value in values])
            unchanged_runs, run = [], 1
            for j in range(1, J):
                if values[j] == values[j-1]: run += 1
                else: unchanged_runs.append(run); run = 1
            unchanged_runs.append(run)
            feasible = next((j for j in range(1, J) if len(set(values[:j]) - {values[j-1]}) > 0), None)
            per_history.append((changes, novelties, mismatches, max(unchanged_runs), len(set(values)),
                                sum(record.mechanism == "RETURN" for record in transition_records), feasible))
        mech = mechanisms[kernel_index].ravel()
        flg = flags[kernel_index].ravel()
        c_all = np.concatenate([item[0] for item in per_history]); n_all = np.concatenate([item[1] for item in per_history]); m_all = np.concatenate([item[2] for item in per_history])
        stay, movement, returning, sigma = kernel
        kernel_id = f"K{kernel_index:02d}"
        max_runs = np.array([x[3] for x in per_history]); distinct_counts = np.array([x[4] for x in per_history])
        strict_returns = np.array([x[5] for x in per_history]); feasible_times = np.array([x[6] for x in per_history if x[6] is not None])
        distribution = {}
        for name, values in (("C", c_all), ("N", n_all), ("M", m_all), ("max_unchanged_run", max_runs),
                             ("distinct_p", distinct_counts), ("strict_returns", strict_returns)):
            distribution.update({f"q10_{name}": np.quantile(values, .1), f"q50_{name}": np.quantile(values, .5),
                                 f"q90_{name}": np.quantile(values, .9)})
        kernel_rows.append({"kernel_id": kernel_id, "alpha_stay": stay, "alpha_move": movement,
                            "alpha_return": returning, "sigma": sigma, "histories": CHARACTERIZATION_N,
                            "realized_stay": np.mean(mech == 0), "realized_move": np.mean(mech == 1),
                            "realized_return": np.mean(mech == 2), "return_unavailable": np.mean(flg & 1 > 0),
                            "renormalization": np.mean(flg & 2 > 0),
                            "reflection_given_move": np.mean((flg[mech == 1] & 4) > 0) if np.any(mech == 1) else None,
                            "mean_C": c_all.mean(), "median_C": np.median(c_all), "mean_N": n_all.mean(),
                            "median_N": np.median(n_all), "mean_M": m_all.mean(), "median_M": np.median(m_all),
                            "mean_max_unchanged_run": np.mean([x[3] for x in per_history]),
                            "mean_distinct_p": np.mean([x[4] for x in per_history]),
                            "mean_strict_returns": strict_returns.mean(),
                            "fraction_return_ever_feasible": len(feasible_times) / CHARACTERIZATION_N,
                            "mean_first_return_feasible_problem": feasible_times.mean() if len(feasible_times) else None,
                            **distribution})
        for step in range(J - 1):
            step_mech = mechanisms[kernel_index, :, step]; step_flags = flags[kernel_index, :, step]
            step_rows.append({"kernel_id": kernel_id, "transition": step + 1,
                              "stay": np.mean(step_mech == 0), "move": np.mean(step_mech == 1),
                              "return": np.mean(step_mech == 2), "return_unavailable": np.mean(step_flags & 1 > 0),
                              "renormalization": np.mean(step_flags & 2 > 0)})
    return histories, mechanisms, flags, kernel_rows, step_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--calibrate-only", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    calibration, bins, selected, audit = calibrate()
    write_csv(OUT / "move_calibration.csv", calibration); write_csv(OUT / "move_bins.csv", bins)
    with (OUT / "move_audit.json").open("w") as handle: json.dump(audit, handle, indent=2); handle.write("\n")
    if not (audit["median_order_all_candidates"] and audit["quantile_order_all_candidates"]
            and audit["empirical_distribution_order_all_adjacent_candidates"]
            and audit["selected_bin_median_order_all_bins"]):
        raise RuntimeError("PGCG MOVE ordering failure")
    if args.calibrate_only:
        return
    lattice = simplex_lattice_degree4(); compositions = executable_compositions(); kernels = nominal_kernels(selected)
    if (len(lattice), len(compositions), len(kernels)) != (15, 14, 34): raise RuntimeError("PGCG design-count failure")
    composition_rows = [{"alpha_stay": x[0], "alpha_move": x[1], "alpha_return": x[2],
                         "executable": x != (0, 0, 1), "reason": "" if x != (0,0,1) else "pure RETURN structurally non-initializable"} for x in lattice]
    kernel_design = [{"kernel_id": f"K{i:02d}", "alpha_stay": k[0], "alpha_move": k[1], "alpha_return": k[2], "sigma": k[3]} for i,k in enumerate(kernels)]
    write_csv(OUT / "simplex_compositions.csv", composition_rows); write_csv(OUT / "nominal_kernels.csv", kernel_design)
    histories, mechanisms, flags, summaries, steps = characterize(kernels)
    np.savez_compressed(OUT / "raw_generator_histories.npz", histories=histories, mechanisms=mechanisms, flags=flags)
    write_csv(OUT / "kernel_summary.csv", summaries); write_csv(OUT / "transition_summary.csv", steps)
    numeric = np.array([[row[key] if row[key] is not None else np.nan for key in ("realized_stay","realized_move","realized_return","return_unavailable","reflection_given_move","mean_C","mean_N","mean_M","mean_max_unchanged_run","mean_distinct_p","mean_strict_returns")] for row in summaries])
    scale = np.nanstd(numeric, axis=0); scale[scale == 0] = 1
    distances = []
    for i in range(len(kernels)):
        for j in range(i + 1, len(kernels)):
            mask = np.isfinite(numeric[i]) & np.isfinite(numeric[j])
            distance = float(np.sqrt(np.mean(((numeric[i,mask]-numeric[j,mask])/scale[mask])**2)))
            distances.append({"kernel_a": f"K{i:02d}", "kernel_b": f"K{j:02d}", "standardized_rms_descriptor_distance": distance})
    distances.sort(key=lambda row: (row["standardized_rms_descriptor_distance"], row["kernel_a"], row["kernel_b"]))
    write_csv(OUT / "nearest_kernel_pairs.csv", distances[:20])
    no_move_ids = [f"K{i:02d}" for i, kernel in enumerate(kernels) if kernel[1] == 0.0]
    write_csv(OUT / "structural_duplicate_flags.csv", [{
        "flag": "exact_constant-history_equivalence",
        "kernel_ids": "|".join(no_move_ids),
        "basis": "alpha_move=0 cannot create a distinct value from one initial p; RETURN remains unavailable",
        "action": "retain all nominal kernels for later scientific review; do not merge",
    }])
    artifacts = {path.name: sha256(path) for path in OUT.iterdir() if path.is_file()}
    summary = {"status": "PASS", "selected_sigmas": selected, "mathematical_compositions": 15,
               "executable_compositions": 14, "unique_executable_kernels": 34,
               "histories_per_kernel": CHARACTERIZATION_N, "problems_per_history": J,
               "total_histories": len(kernels)*CHARACTERIZATION_N, "agent_or_performance_execution": False,
               "pgcg_histories_eligible_for_future_c3": False, "artifacts_sha256": artifacts}
    with (OUT / "control_summary.json").open("w") as handle: json.dump(summary, handle, indent=2, sort_keys=True); handle.write("\n")


if __name__ == "__main__":
    main()
