"""Controls for the frozen pre-performance Campaign 3 team split."""

import csv
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from hls.campaign3_team_geometry import canonical_team, farthest_point_sequence, team_distance, validate_team


ROOT = Path(__file__).parents[1]
GEOMETRY = ROOT / "results" / "foundations" / "campaign3_team_geometry"
SPLIT = ROOT / "results" / "foundations" / "campaign3_team_split"
DEV_IDS = ("G00", "G04", "G05", "G07", *(f"F{i:02d}" for i in range(1,17)))
HELDOUT_IDS = tuple(f"F{i:02d}" for i in range(17,25))


def matrix(row):
    return tuple(tuple(float(row[f"s{i}{k}"]) for k in (1,2)) for i in (1,2,3))


def load_rows():
    with (SPLIT / "team_split.csv").open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_exact_ids_counts_anchors_and_disjoint_quotient_membership():
    rows = load_rows()
    dev = [row for row in rows if row["partition"] == "development"]
    heldout = [row for row in rows if row["partition"] == "heldout"]
    assert tuple(row["team_id"] for row in dev) == DEV_IDS
    assert tuple(row["team_id"] for row in heldout) == HELDOUT_IDS
    assert len(dev) == 20 and len(heldout) == 8
    assert all(row["historical_anchor"] == "True" for row in dev[:4])
    assert all(row["historical_anchor"] == "False" for row in heldout)
    canonical = [canonical_team(matrix(row)) for row in rows]
    assert len(set(canonical)) == 28
    assert all(team_distance(left, right) > 0 for i,left in enumerate(canonical) for right in canonical[i+1:])


def test_all_matrices_are_valid_and_exactly_canonical():
    for row in load_rows():
        team = matrix(row)
        assert validate_team(team) == team
        assert canonical_team(team) == team


def test_sequence_is_exactly_rederived_from_hashed_primary_pool():
    summary = json.loads((GEOMETRY / "control_summary.json").read_text())
    pool_path = GEOMETRY / "candidate_pool_primary.csv"
    assert hashlib.sha256(pool_path.read_bytes()).hexdigest() == summary["artifacts_sha256"][pool_path.name]
    with pool_path.open(newline="") as handle:
        pool_rows = list(csv.DictReader(handle))
    pool = np.asarray([matrix(row) for row in pool_rows])
    rows = load_rows()
    stored = np.asarray([matrix(row) for row in rows])
    derived, insertion, _ = farthest_point_sequence(pool, stored[:4], 28)
    assert np.array_equal(derived, stored)
    assert tuple(row["team_id"] for row in rows[:20]) == DEV_IDS
    assert tuple(row["team_id"] for row in rows[20:]) == HELDOUT_IDS
    for index in range(4,28):
        assert float(rows[index]["insertion_distance"]) == pytest.approx(insertion[index], abs=1e-15)


def test_heldout_development_distances_and_nearest_ids_recompute():
    rows = load_rows(); development = rows[:20]
    for row in rows[20:]:
        candidates = [(team_distance(matrix(row), matrix(candidate)), candidate["team_id"]) for candidate in development]
        distance, nearest = min(candidates, key=lambda item: (item[0], item[1]))
        assert row["nearest_development_id"] == nearest
        assert float(row["d_dev"]) == pytest.approx(distance, abs=1e-15)


def test_manifest_hashes_and_scientific_contamination_controls():
    manifest = json.loads((SPLIT / "pre_performance_team_split.json").read_text())
    assert manifest["s_dev_ids"] == list(DEV_IDS)
    assert manifest["s_heldout_ids"] == list(HELDOUT_IDS)
    assert manifest["team_split_csv_sha256"] == hashlib.sha256((SPLIT / "team_split.csv").read_bytes()).hexdigest()
    assert manifest["post_performance_modification_prohibited"] is True
    assert manifest["agent_policy_problem_history_reward_performance_execution"] is False
    assert set(path.suffix for path in SPLIT.iterdir()) == {".csv", ".json"}
    freeze_path = ROOT / "experiments" / "synthetic" / "campaign3_team_split" / "freeze.py"
    tree = ast.parse(freeze_path.read_text())
    imports = [alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names]
    forbidden = ("discover", "finite_problem_belief", "campaign2", "problem_geometry")
    assert not any(any(term in imported for term in forbidden) for imported in imports)
