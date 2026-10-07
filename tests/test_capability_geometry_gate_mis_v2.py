"""Design and generated-result controls for the MIS-v2 geometry replication."""

import csv
from pathlib import Path

from experiments.synthetic.capability_geometry_gate.run import CONFIGURATIONS as V1_CONFIGURATIONS
from experiments.synthetic.capability_geometry_gate.run import ENVIRONMENTS as V1_ENVIRONMENTS
from experiments.synthetic.capability_geometry_gate_mis_v2.run import ETA_GRID


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "foundations" / "capability_geometry_gate_mis_v2"


def _rows(filename):
    with (OUT / filename).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_preregistered_grid_is_broad_strictly_interior_and_unchanged():
    assert ETA_GRID == (0.05, 0.10, 0.20, 0.35, 0.50, 0.70, 0.90)
    assert all(0.0 < eta < 1.0 for eta in ETA_GRID)


def test_replication_reuses_exact_v1_configurations_and_environments():
    configs = _rows("configurations.csv")
    environments = _rows("environments.csv")
    assert len(configs) == len(V1_CONFIGURATIONS) == 9
    assert [row["configuration_id"] for row in configs] == [row["configuration_id"] for row in V1_CONFIGURATIONS]
    assert [row["environment"] for row in environments] == list(V1_ENVIRONMENTS)
    assert {(float(row["B_1"]), float(row["B_2"])) for row in configs} == {(1.5, 1.5)}


def test_generated_counts_seeds_and_complete_regime_map():
    runs = _rows("runs.csv")
    trajectories = _rows("trajectories.csv")
    regime = _rows("regime_map_by_eta.csv")
    assert len(runs) == 2205 and len(trajectories) == 26460
    assert {int(row["seed"]) for row in runs} == {20261007, 20261008, 20261009}
    assert len(regime) == 7 * 5 * 9
    assert sum(row["winner"] == "True" for row in regime) == 7 * 5


def test_no_development_controls_are_exactly_eta_invariant():
    runs = _rows("runs.csv")
    for configuration in ("G00", "G06", "G07", "G08"):
        for environment in V1_ENVIRONMENTS:
            for mode in ("discover_only", "static_known"):
                for seed in (20261007, 20261008, 20261009):
                    values = {float(row["performance"]) for row in runs if row["configuration_id"] == configuration and row["environment"] == environment and row["mode"] == mode and int(row["seed"]) == seed}
                    assert len(values) == 1


def test_matched_g00_g06_identity_effect_and_interior_crossovers_exist():
    pairs = _rows("matched_pairs.csv")
    matched = [row for row in pairs if row["configuration_a"] == "G00" and row["configuration_b"] == "G06"]
    assert len(matched) == len(ETA_GRID)
    assert all(float(row["Delta_V_K"]) == 0.0 for row in matched)
    assert all(float(row["Delta_performance_alternating_1212"]) > 0.5 for row in matched)
    interior = _rows("interior_geometry_check.csv")
    for eta in ETA_GRID:
        winners = {row["configuration_id"] for row in interior if float(row["eta"]) == eta and row["interior_winner"] == "True"}
        assert len(winners) >= 2


def test_historical_mis_v1_artifacts_still_exist_separately():
    old = ROOT / "results" / "foundations" / "capability_geometry_gate"
    assert (old / "manifest.json").is_file()
    assert (old / "regime_map.csv").is_file()
