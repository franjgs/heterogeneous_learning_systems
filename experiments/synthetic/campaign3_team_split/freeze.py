"""Freeze the pre-performance Campaign 3 team split from geometry artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.campaign3_team_geometry import canonical_team, farthest_point_sequence, team_distance  # noqa: E402


SOURCE = ROOT / "results" / "foundations" / "campaign3_team_geometry"
OUT = ROOT / "results" / "foundations" / "campaign3_team_split"
DEV_IDS = ("G00", "G04", "G05", "G07", *(f"F{i:02d}" for i in range(1, 17)))
HELDOUT_IDS = tuple(f"F{i:02d}" for i in range(17, 25))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix(row: dict[str, str]) -> np.ndarray:
    return np.array([[float(row[f"s{i}{k}"]) for k in (1, 2)] for i in (1, 2, 3)])


def main() -> None:
    pool_path = SOURCE / "candidate_pool_primary.csv"
    sequence_path = SOURCE / "selected_sequence.csv"
    summary_path = SOURCE / "control_summary.json"
    summary = json.loads(summary_path.read_text())
    if digest(pool_path) != summary["artifacts_sha256"][pool_path.name]:
        raise RuntimeError("primary candidate-pool hash mismatch")
    with pool_path.open(newline="", encoding="utf-8") as handle:
        pool_rows = list(csv.DictReader(handle))
    with sequence_path.open(newline="", encoding="utf-8") as handle:
        sequence_rows = list(csv.DictReader(handle))
    pool = np.asarray([matrix(row) for row in pool_rows])
    stored = np.asarray([matrix(row) for row in sequence_rows])
    derived, insertion, _ = farthest_point_sequence(pool, stored[:4], 28)
    if not np.array_equal(derived, stored[:28]):
        raise RuntimeError("stored sequence disagrees with algorithmic derivation")
    expected_ids = DEV_IDS + HELDOUT_IDS
    if tuple(row["identity"] for row in sequence_rows[:28]) != expected_ids:
        raise RuntimeError("stored IDs disagree with expected G00/G04/G05/G07/F01-F24 order")

    development = {team_id: derived[index] for index, team_id in enumerate(DEV_IDS)}
    output_rows = []
    heldout_diagnostics = []
    for index, (team_id, team) in enumerate(zip(expected_ids, derived, strict=True)):
        partition = "development" if index < 20 else "heldout"
        nearest_id = ""
        d_dev = None
        if partition == "heldout":
            distances = [(team_distance(team, candidate), candidate_id) for candidate_id, candidate in development.items()]
            d_dev, nearest_id = min(distances, key=lambda item: (item[0], item[1]))
            heldout_diagnostics.append({"team_id": team_id, "nearest_development_id": nearest_id,
                                        "d_dev": d_dev, "insertion_distance": insertion[index]})
        output_rows.append({
            "team_id": team_id, "partition": partition, "selection_order": index + 1,
            "historical_anchor": index < 4,
            **{f"s{i+1}{k+1}": team[i, k] for i in range(3) for k in range(2)},
            "nearest_development_id": nearest_id, "d_dev": d_dev,
            "insertion_distance": None if index < 4 else insertion[index],
            "source": "campaign3_team_geometry/selected_sequence.csv; independently rederived from frozen primary pool",
        })

    OUT.mkdir(parents=True, exist_ok=True)
    table_path = OUT / "team_split.csv"
    with table_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(output_rows)
    d_values = np.array([row["d_dev"] for row in heldout_diagnostics])
    manifest = {
        "artifact_type": "pre_performance_campaign3_team_split",
        "scientific_claim": "GENERALIZATION TO GEOMETRICALLY SEPARATED UNSEEN TEAM GEOMETRIES",
        "operational_description": "A GEOMETRIC TEAM-SPACE STRESS TEST",
        "not_claimed": ["representative random sample", "geometric extrapolation", "out-of-domain teams",
                        "wholly unseen structural region", "new class of team structures"],
        "team_space": "3x2 [0,1] matrices, each column sum 1.5, quotient by common row permutations",
        "distance": "d_S(A,B)=min over six common row permutations P of ||A-PB||_F",
        "canonicalization": "six common row permutations; row-major flatten; lexicographic minimum",
        "selection": "four frozen anchors then deterministic farthest-point over frozen primary pool; exact-distance maximum and lexicographic-coordinate tie-break",
        "anchors": ["G00", "G04", "G05", "G07"],
        "s_dev_ids": list(DEV_IDS), "s_heldout_ids": list(HELDOUT_IDS),
        "development_count": 20, "heldout_count": 8,
        "teams": [{"team_id": row["team_id"], "partition": row["partition"], "selection_order": row["selection_order"],
                   "historical_anchor": row["historical_anchor"],
                   "matrix": [[row[f"s{i}{k}"] for k in (1,2)] for i in (1,2,3)]} for row in output_rows],
        "heldout_diagnostics": heldout_diagnostics,
        "d_dev_summary": {"min": d_values.min(), "median": np.median(d_values), "max": d_values.max()},
        "source_artifacts": {path.name: digest(path) for path in (pool_path, sequence_path, summary_path, SOURCE / "protocol.json")},
        "primary_pool_sha256": digest(pool_path),
        "team_split_csv_sha256": digest(table_path),
        "discretization_caveat": "individual representatives depend on the frozen finite pool; aggregate coverage was numerically robust; all frozen split objects are now immutable",
        "generalization_claims_kept_separate": ["unseen histories from development generator kernels",
            "compositional/interpolative unseen generator kernels", "geometrically separated unseen team geometries"],
        "post_performance_modification_prohibited": True,
        "agent_policy_problem_history_reward_performance_execution": False
    }
    with (OUT / "pre_performance_team_split.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True); handle.write("\n")


if __name__ == "__main__":
    main()
