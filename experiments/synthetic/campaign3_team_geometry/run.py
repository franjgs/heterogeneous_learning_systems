"""Pure geometric characterization of the Campaign 3 quotient team space."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.campaign3_team_geometry import (  # noqa: E402
    ROW_PERMUTATIONS,
    boundary_clearance,
    canonical_team,
    constrained_pool,
    distances_to_team,
    farthest_point_sequence,
    pairwise_distances,
    team_distance,
)


OUT = ROOT / "results" / "foundations" / "campaign3_team_geometry"
ANCHOR_SOURCE = ROOT / "experiments" / "synthetic" / "campaign0_discriminative_capacity" / "run.py"
ANCHOR_IDS = ("G00", "G04", "G05", "G07")
PRIMARY_RAW = 20_000
PRIMARY_SEED = 20261010
VALIDATION_RAW = 40_000
VALIDATION_SEED = 20261012
PAIRWISE_SAMPLE = 2_000
PAIRWISE_SEED = 20261011
REQUESTED_N = (4, 6, 8, 10, 12, 16, 20, 24, 32, 40)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def recover_anchors() -> dict[str, tuple[tuple[float, float], ...]]:
    """Read the frozen literal without importing its agent/performance runner."""
    tree = ast.parse(ANCHOR_SOURCE.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "TEAMS" for target in node.targets):
            values = ast.literal_eval(node.value)
            return {key: values[key] for key in ANCHOR_IDS}
    raise RuntimeError("frozen TEAMS literal not found in anchor source")


def summaries(values: np.ndarray) -> dict[str, float]:
    quantiles = np.quantile(values, (0.05, 0.25, 0.5, 0.75, 0.95))
    return {"min": float(values.min()), "q05": quantiles[0], "q25": quantiles[1],
            "median": quantiles[2], "q75": quantiles[3], "q95": quantiles[4], "max": float(values.max())}


def occupancy_diagnostics(valid: np.ndarray) -> list[dict]:
    rows = []
    for capability in range(2):
        first, second = valid[:, 0, capability], valid[:, 1, capability]
        histogram, _, _ = np.histogram2d(first, second, bins=10, range=((0, 1), (0, 1)))
        admissible = histogram[histogram > 0]
        all_cells = valid[:, :, capability].ravel()
        rows.append({"capability": capability + 1, "mean": all_cells.mean(), "std": all_cells.std(ddof=1),
                     "q05": np.quantile(all_cells, .05), "q50": np.quantile(all_cells, .5),
                     "q95": np.quantile(all_cells, .95), "occupied_grid_cells": len(admissible),
                     "occupancy_cv": admissible.std(ddof=1) / admissible.mean()})
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    recovered = recover_anchors()
    canonical = {key: canonical_team(value) for key, value in recovered.items()}
    anchors = np.asarray([canonical[key] for key in ANCHOR_IDS])
    primary_valid, primary = constrained_pool(PRIMARY_RAW, PRIMARY_SEED)
    validation_valid, validation = constrained_pool(VALIDATION_RAW, VALIDATION_SEED)

    selected, insertion, primary_radii = farthest_point_sequence(primary, anchors, 40)
    validation_selected, validation_insertion, validation_radii = farthest_point_sequence(validation, anchors, 40)

    rng = np.random.default_rng(PAIRWISE_SEED)
    sample_indices = np.sort(rng.choice(len(primary), size=PAIRWISE_SAMPLE, replace=False))
    sample = primary[sample_indices]
    pairwise = pairwise_distances(sample)
    nearest = np.full(PAIRWISE_SAMPLE, np.inf)
    cursor = 0
    for index in range(PAIRWISE_SAMPLE - 1):
        length = PAIRWISE_SAMPLE - index - 1
        values = pairwise[cursor : cursor + length]
        nearest[index] = min(nearest[index], values.min())
        nearest[index + 1 :] = np.minimum(nearest[index + 1 :], values)
        cursor += length

    anchor_matrix = np.array([[team_distance(canonical[a], canonical[b]) for b in ANCHOR_IDS] for a in ANCHOR_IDS])
    anchor_rows = []
    for i, left in enumerate(ANCHOR_IDS):
        for j, right in enumerate(ANCHOR_IDS):
            anchor_rows.append({"anchor_a": left, "anchor_b": right, "distance": anchor_matrix[i, j]})

    coverage_rows = []
    for n in REQUESTED_N:
        chosen = selected[:n]
        chosen_pairwise = pairwise_distances(chosen)
        validation_distance = np.full(len(validation), np.inf)
        for team in chosen:
            validation_distance = np.minimum(validation_distance, distances_to_team(validation, team))
        validation_chosen = validation_selected[:n]
        directed_a = max(min(team_distance(team, other) for other in validation_chosen) for team in chosen)
        directed_b = max(min(team_distance(team, other) for other in chosen) for team in validation_chosen)
        clearances = boundary_clearance(chosen)
        coverage_rows.append({
            "n": n, "primary_pool_radius": primary_radii[n - 4], "validation_pool_radius_primary_design": validation_distance.max(),
            "validation_pool_own_design_radius": validation_radii[n - 4], "selected_set_hausdorff_primary_vs_validation": max(directed_a, directed_b),
            "minimum_selected_pairwise_distance": chosen_pairwise.min(), "median_selected_pairwise_distance": np.median(chosen_pairwise),
            "last_insertion_distance": None if n == 4 else insertion[n - 1],
            "minimum_boundary_clearance": clearances.min(), "median_boundary_clearance": np.median(clearances),
        })

    selected_rows = []
    for index, team in enumerate(selected):
        selected_rows.append({"selection_index": index + 1, "identity": ANCHOR_IDS[index] if index < 4 else f"F{index-3:02d}",
                              "anchor": index < 4, "insertion_distance": None if index < 4 else insertion[index],
                              **{f"s{i+1}{k+1}": team[i, k] for i in range(3) for k in range(2)},
                              "boundary_clearance": boundary_clearance(team[None])[0]})

    pool_rows = [{"pool_index": index, **{f"s{i+1}{k+1}": team[i,k] for i in range(3) for k in range(2)}} for index, team in enumerate(primary)]
    anchor_detail = []
    for index, key in enumerate(ANCHOR_IDS):
        other = np.delete(anchor_matrix[index], index)
        nearest_anchor = min((anchor_matrix[index,j], ANCHOR_IDS[j]) for j in range(4) if j != index)
        anchor_detail.append({"anchor": key, "nearest_anchor": nearest_anchor[1], "nearest_anchor_distance": nearest_anchor[0],
                              "nearest_anchor_distance_pairwise_percentile": 100*np.mean(pairwise <= nearest_anchor[0]),
                              "nearest_anchor_distance_nn_percentile": 100*np.mean(nearest <= nearest_anchor[0])})

    write_csv(OUT / "candidate_pool_primary.csv", pool_rows)
    write_csv(OUT / "selected_sequence.csv", selected_rows)
    write_csv(OUT / "coverage_curve.csv", coverage_rows)
    write_csv(OUT / "anchor_distance_matrix.csv", anchor_rows)
    write_csv(OUT / "anchor_geometry.csv", anchor_detail)
    write_csv(OUT / "column_sampling_diagnostics.csv", occupancy_diagnostics(primary_valid))
    np.savez_compressed(OUT / "validation_pool.npz", teams=validation)

    pool_clearance = boundary_clearance(primary)
    summary = {
        "status": "COMPLETE_GEOMETRY_ONLY",
        "team_space": "3x2 entries in [0,1], each column sum 1.5, quotient by common row permutation",
        "canonicalization": "enumerate six common row permutations; row-major flatten; lexicographic minimum",
        "duplicate_rule": "exact canonical float equality only; no approximate clustering",
        "distance": "minimum Frobenius distance over six common row permutations; design geometry only",
        "anchor_source": str(ANCHOR_SOURCE.relative_to(ROOT)), "anchor_source_sha256": sha256(ANCHOR_SOURCE),
        "anchors": {key: canonical[key] for key in ANCHOR_IDS},
        "anchor_permutation_equivalent_pairs": [[ANCHOR_IDS[i],ANCHOR_IDS[j]] for i in range(4) for j in range(i+1,4) if anchor_matrix[i,j] == 0],
        "generation": {"method": "4D Halton bases 2,3,5,7 plus seeded Cranley-Patterson shift; exact polygon filtering",
                       "primary_seed": PRIMARY_SEED, "primary_raw": PRIMARY_RAW, "primary_valid": len(primary_valid), "primary_quotient_unique": len(primary),
                       "validation_seed": VALIDATION_SEED, "validation_raw": VALIDATION_RAW, "validation_valid": len(validation_valid), "validation_quotient_unique": len(validation)},
        "pairwise_sample": {"seed": PAIRWISE_SEED, "size": PAIRWISE_SAMPLE, "pair_count": len(pairwise), "summary": summaries(pairwise),
                            "nearest_neighbor_summary": summaries(nearest)},
        "boundary_clearance_pool_summary": summaries(pool_clearance),
        "requested_n": REQUESTED_N,
        "final_team_count_or_split_selected": False,
        "agent_policy_problem_performance_dependencies": False,
    }
    artifact_paths = [path for path in OUT.iterdir() if path.is_file() and path.name != "control_summary.json"]
    summary["artifacts_sha256"] = {path.name: sha256(path) for path in artifact_paths}
    with (OUT / "control_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True); handle.write("\n")


if __name__ == "__main__":
    main()
