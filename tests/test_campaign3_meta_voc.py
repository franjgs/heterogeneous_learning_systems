from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_meta_voc import run  # noqa: E402


def test_thresholds_are_deterministic_and_calibrated_only_from_supplied_validation_scores():
    validation = [(float(i), f"{i:064x}") for i in range(100)]
    first = run.calibrate_thresholds(validation)
    second = run.calibrate_thresholds(list(reversed(validation)))
    assert first == second
    assert [first[str(p)]["target_validation_invocations"] for p in (25, 50, 75)] == [25, 50, 75]
    assert sum(run.threshold_route(score, key, first["25"]) for score, key in validation) == 25


def test_random_routes_match_retrospective_budget_without_using_meta_locations():
    tasks = run.tasks()[:2]
    meta_counts = {25: 7, 50: 13, 75: 31}
    routes, table = run.make_random_routes(meta_counts, tasks)
    assert len(table) == 48
    assert {point: len(route) for point, route in routes.items()} == meta_counts
    assert not any((clock - 1) % 3 == 2 for _, clock in routes[25])
    # Changing only the retrospective budget cannot change the independent
    # priority order; each rate is a prefix of the same random ordering.
    other, _ = run.make_random_routes({25: 13, 50: 13, 75: 31}, tasks)
    assert routes[50] == other[25]


def test_meta_voc_score_uses_only_frozen_ex_ante_c33_features():
    state = ((0.2, 0.3), (0.5, 0.4), (0.8, 0.8))
    belief = (0.2, 0.3, 0.5)
    model = {"mean": [0.0] * 10, "scale": [1.0] * 10, "coef": [0.0] * 11}
    score, benefit, cost = run.ex_ante_score(state, belief, 17, model, {2: 0.5, 3: 0.25})
    assert score == 0.0 and benefit == 0.0 and cost == 0.5
    assert len(run.c33.feature_vector(state, belief, 17)) == 10
    assert np.isfinite([score, benefit, cost]).all()


def test_output_schema_and_scientific_firewalls_are_explicit():
    source = (ROOT / "experiments/synthetic/campaign3_meta_voc/run.py").read_text()
    assert "RANDOM_NAMESPACE" in source
    assert "heldout_used\": False" in source
    assert "Q11-continuation raw Monte Carlo Q11-Q00" in source
    assert "24 nonterminal clock slots/history" in source
    assert "--full" in source and "default" in source


def test_completed_artifacts_have_exact_cells_frequency_match_and_valid_hashes():
    output = ROOT / "results/campaigns/campaign3_meta_voc/sequential_full"
    manifest = json.loads((output / "execution_manifest.json").read_text())
    summary = json.loads((output / "analysis_summary.json").read_text())
    for filename, field in (("runs.csv", "runs_sha256"),
                             ("trajectories.csv.gz", "trajectories_sha256"),
                             ("random_invocation_schedule.csv", "random_schedule_sha256"),
                             ("analysis_summary.json", "analysis_summary_sha256")):
        assert hashlib.sha256((output / filename).read_bytes()).hexdigest() == manifest[field]
    assert manifest["base_histories"] == 420
    assert manifest["policy_runs"] == 3360
    assert manifest["trajectory_rows"] == 120960
    assert manifest["heldout_used"] is False
    assert summary["frequency_match_exact"] is True
    assert summary["meta_voc_actual_invocation_counts"] == {"25": 2451, "50": 5003, "75": 7474}
    assert summary["random_actual_invocation_counts"] == summary["meta_voc_actual_invocation_counts"]

