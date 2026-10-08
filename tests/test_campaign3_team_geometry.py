"""Focused controls for Campaign 3 team-space geometry characterization."""

import ast
import csv
import hashlib
import importlib.util
import json
from itertools import permutations
from pathlib import Path

import numpy as np
import pytest

from hls.campaign3_team_geometry import (
    TEAM_TOLERANCE,
    canonical_team,
    constrained_pool,
    farthest_point_sequence,
    team_distance,
    validate_team,
)


ROOT = Path(__file__).parents[1]
ANCHORS = {
    "G00": ((0.5, 0.5), (0.5, 0.5), (0.5, 0.5)),
    "G04": ((0.25, 0.75), (0.625, 0.375), (0.625, 0.375)),
    "G05": ((0.0, 1.0), (0.5, 0.5), (1.0, 0.0)),
    "G07": ((0.0, 1.0), (0.5, 0.0), (1.0, 0.5)),
}


def test_generated_teams_obey_bounds_and_column_constraints():
    valid, unique = constrained_pool(500, 123)
    for collection in (valid, unique):
        assert np.all((collection >= 0) & (collection <= 1))
        assert np.allclose(collection.sum(axis=1), 1.5, rtol=0, atol=TEAM_TOLERANCE)


def test_canonicalization_is_invariant_under_all_common_row_permutations():
    team = ANCHORS["G07"]
    expected = canonical_team(team)
    for permutation in permutations(range(3)):
        assert canonical_team(tuple(team[index] for index in permutation)) == expected


def test_distance_metric_controls_and_permutation_invariance():
    left, right = ANCHORS["G04"], ANCHORS["G07"]
    assert team_distance(left, left) == 0
    assert team_distance(left, right) == pytest.approx(team_distance(right, left), abs=1e-15)
    for p, q in zip(permutations(range(3)), reversed(tuple(permutations(range(3))))):
        permuted_left = tuple(left[index] for index in p)
        permuted_right = tuple(right[index] for index in q)
        assert team_distance(permuted_left, permuted_right) == pytest.approx(team_distance(left, right), abs=1e-15)
        assert team_distance(left, permuted_left) == 0


def test_exact_canonical_duplicates_are_removed():
    _, unique = constrained_pool(1000, 456)
    flattened = unique.reshape(len(unique), 6)
    assert len(np.unique(flattened, axis=0)) == len(unique)


def test_historical_anchors_are_recovered_from_frozen_source_and_valid():
    path = ROOT / "experiments" / "synthetic" / "campaign3_team_geometry" / "run.py"
    spec = importlib.util.spec_from_file_location("campaign3_team_geometry_run", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    assert module.recover_anchors() == ANCHORS
    for team in ANCHORS.values():
        validate_team(team)


def test_maximin_is_deterministic_and_insertions_nonincreasing():
    _, pool = constrained_pool(1000, 789)
    anchors = np.asarray([canonical_team(team) for team in ANCHORS.values()])
    first = farthest_point_sequence(pool, anchors, 20)
    second = farthest_point_sequence(pool, anchors, 20)
    assert np.array_equal(first[0], second[0])
    assert np.array_equal(first[1], second[1], equal_nan=True)
    assert np.all(np.diff(first[1][4:]) <= 1e-14)
    assert np.all(np.diff(first[2]) <= 1e-14)


def test_characterization_has_no_forbidden_scientific_dependencies():
    paths = [ROOT / "src" / "hls" / "campaign3_team_geometry.py",
             ROOT / "experiments" / "synthetic" / "campaign3_team_geometry" / "run.py"]
    forbidden = {"finite_problem_belief", "discover_develop", "campaign2", "problem_geometry"}
    for path in paths:
        tree = ast.parse(path.read_text())
        imports = [alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names]
        assert not any(any(term in imported for term in forbidden) for imported in imports)


def test_materialized_geometry_artifacts_are_complete_and_geometry_only():
    out = ROOT / "results" / "foundations" / "campaign3_team_geometry"
    summary = json.loads((out / "control_summary.json").read_text())
    assert summary["generation"]["primary_raw"] == 20_000
    assert summary["generation"]["primary_valid"] == summary["generation"]["primary_quotient_unique"] == 11_245
    assert summary["generation"]["validation_raw"] == 40_000
    assert summary["generation"]["validation_valid"] == summary["generation"]["validation_quotient_unique"] == 22_462
    assert summary["anchor_permutation_equivalent_pairs"] == []
    assert summary["final_team_count_or_split_selected"] is False
    assert summary["agent_policy_problem_performance_dependencies"] is False
    with (out / "selected_sequence.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 40
    assert [row["identity"] for row in rows[:4]] == ["G00", "G04", "G05", "G07"]
    assert all(float(rows[index]["insertion_distance"]) >= float(rows[index + 1]["insertion_distance"]) - 1e-14 for index in range(4, 39))
    for name, digest in summary["artifacts_sha256"].items():
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == digest
    prohibited_names = {"reward", "belief", "action", "performance", "problem", "history", "C", "N", "M"}
    assert not prohibited_names & set(rows[0])
