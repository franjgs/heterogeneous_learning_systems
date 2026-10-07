from experiments.synthetic.campaign0_discriminative_capacity.run import (
    ETA, HISTORIES_P, SEEDS, TEAMS, validate_protocol,
)
from hls.small_problem_world import HORIZON, HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR
import csv
import json
from pathlib import Path


def test_campaign0_protocol_is_exactly_frozen():
    validate_protocol()
    assert ETA == 0.35
    assert SEEDS == tuple(range(10))
    assert HORIZON == 3
    assert HYPOTHESIS_REPERTOIRE == ((0.8, 0.2), (0.5, 0.5), (0.2, 0.8))
    assert UNIFORM_PRIOR == (1 / 3,) * 3


def test_campaign0_teams_and_resources_are_exact():
    assert TEAMS == {
        "G00": ((0.5, 0.5), (0.5, 0.5), (0.5, 0.5)),
        "G04": ((0.25, 0.75), (0.625, 0.375), (0.625, 0.375)),
        "G05": ((0.0, 1.0), (0.5, 0.5), (1.0, 0.0)),
        "G07": ((0.0, 1.0), (0.5, 0.0), (1.0, 0.5)),
    }
    assert all(tuple(sum(row[k] for row in state) for k in range(2)) == (1.5, 1.5) for state in TEAMS.values())


def test_campaign0_histories_are_exact_and_h0_h1_content_matched():
    assert HISTORIES_P == {
        "H0": (0.8, 0.7, 0.3, 0.2, 0.5, 0.8),
        "H1": (0.8, 0.2, 0.3, 0.7, 0.5, 0.8),
        "H2": (0.8, 0.8, 0.8, 0.8, 0.8, 0.8),
        "H3": (0.8, 0.2, 0.8, 0.2, 0.8, 0.8),
    }
    assert sorted(HISTORIES_P["H0"]) == sorted(HISTORIES_P["H1"])


def test_materialized_campaign0_is_complete_and_matches_protocol():
    out = Path("results/diagnostics/campaign0_discriminative_capacity")
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["run_count"] == 160
    assert manifest["trajectory_row_count"] == 2880
    assert manifest["eta"] == ETA and manifest["seeds"] == list(SEEDS)
    assert manifest["analysis"]["classification"] == "PASS"
    with (out / "runs.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 160
    assert {(row["team"], row["history"], int(row["seed"])) for row in rows} == {
        (team, history, seed) for team in TEAMS for history in HISTORIES_P for seed in SEEDS
    }
