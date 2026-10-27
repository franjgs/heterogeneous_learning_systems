from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_meta_voc import confirmatory as conf  # noqa: E402
from experiments.synthetic.campaign3_meta_voc import analyze_confirmatory as analysis  # noqa: E402


def test_frozen_partition_factorial_and_fresh_history_ids():
    tasks = conf.planned_tasks()
    assert len(tasks) == 868
    assert pd.Series([t["domain"] for t in tasks]).value_counts().to_dict() == conf.EXPECTED_DOMAIN_COUNTS
    assert len({t["history_id"] for t in tasks}) == 868
    assert len({x for t in tasks for x in (t["problem_seed"], t["noise_seed"])}) == 1736
    assert all(t["replicate"] == 0 and t["history_id"].startswith(conf.SEED_NAMESPACE) for t in tasks)
    for task in tasks:
        team_role, kernel_role = conf.DOMAIN_PARTITIONS[task["domain"]]
        assert task["team_id"] in conf.EXPECTED_TEAM_IDS[team_role]
        assert task["kernel_id"] in conf.EXPECTED_KERNEL_IDS[kernel_role]


def test_random_routes_are_fixed_bernoulli_priorities_not_retrospective_counts():
    task = conf.planned_tasks()[0]
    first, rows = conf.random_routes(task)
    second, rows_again = conf.random_routes(task)
    assert first == second and rows == rows_again and len(rows) == 24
    assert conf.RANDOM_PROBABILITIES == {25: .25, 50: .50, 75: .75}
    assert all(row["clock"] % 3 != 0 for row in rows)
    for point, probability in conf.RANDOM_PROBABILITIES.items():
        assert all((row[f"priority_{point}"] < probability) == bool(row[f"invoke_{point}"])
                   for row in rows)
        assert first[point] == {(task["history_id"], row["clock"]) for row in rows if row[f"invoke_{point}"]}
    assert "meta_counts" not in conf.random_routes.__code__.co_varnames


def test_confirmatory_seed_namespace_is_disjoint_from_existing_identifiers():
    previous_ids, previous_seeds = conf._prior_history_ids_and_seeds()
    new = conf.planned_tasks()
    assert not ({t["history_id"] for t in new} & previous_ids)
    assert not ({seed for t in new for seed in (t["problem_seed"], t["noise_seed"])} & previous_seeds)


def test_frozen_ridge_and_calibration_are_read_only_inputs():
    calibration = json.loads(conf.CALIBRATION_FILE.read_text())
    model = json.loads(conf.MODEL_FILE.read_text())
    assert conf.sha256(conf.MODEL_FILE) == "1874b1f06a7122361677f5bb617132bd2eff3976fd1aa890d7152436fb59ba1d"
    assert tuple(model["features"]) == ("s11", "s12", "s21", "s22", "s31", "s32", "b0", "b1", "b2", "tau")
    assert calibration["predicted_extra_cost_seconds_by_remaining"] == {
        "2": 0.209201959, "3": 0.20978829100000002}
    assert set(calibration["thresholds"]) == {"25", "50", "75"}
    source = (ROOT / "experiments/synthetic/campaign3_meta_voc/confirmatory.py").read_text()
    assert "voc.calibrate(" not in source and "c33.train_selector(" not in source


def test_equal_domain_bootstrap_uses_paired_history_units():
    rows = []
    for domain, effect in zip(conf.DOMAINS, (1., 2., 3., 4.), strict=True):
        for history in range(2):
            identity = f"{domain}-{history}"
            for policy in conf.POLICIES:
                value = effect if policy == "META_VOC_50" else 0.
                rows.append({"domain": domain, "history_id": identity, "policy": policy,
                             "cumulative_mu_true": value,
                             "decision_compute_ns": 1000 + (200 if policy == "META_VOC_50" else 0)})
    paired = analysis.paired_tables(pd.DataFrame(rows))
    primary = paired.loc[(paired.domain == "GLOBAL_EQUAL_G") & (paired.point == 50) &
                         (paired.baseline == "RANDOM_50") & (paired.metric == "cumulative_mu_true")].iloc[0]
    assert primary.mean_difference == 2.5
    assert primary.ci95_low == primary.ci95_high == 2.5
    assert primary.n_histories == 8


def test_synthetic_preflight_uses_eight_independent_paths_and_common_exogenous_streams():
    task = dict(conf.planned_tasks()[0])
    task.update(history_id="synthetic_preflight_not_confirmatory",
                problem_seed=123456781, noise_seed=876543211)
    model = json.loads(conf.MODEL_FILE.read_text())
    calibration = json.loads(conf.CALIBRATION_FILE.read_text())
    costs = {int(k): float(v) for k, v in calibration["predicted_extra_cost_seconds_by_remaining"].items()}
    routes, _ = conf.random_routes(task)
    runs, traces = conf._simulate_payload((task, model, costs, calibration["thresholds"], routes))
    conf._validate_batch(runs, traces, [task])
    assert [row["policy"] for row in runs] == list(conf.POLICIES)
    for row in runs:
        assert row["domain"] == "G1"
    for point in (25, 50, 75):
        rows = [row for row in traces if row["policy"] == f"RANDOM_{point}"]
        assert {row["clock"] for row in rows if row["route"] == "DEEP_RANDOM"} == {
            clock for history_id, clock in routes[point] if history_id == task["history_id"]}


def test_pre_execution_manifest_and_raw_integrity_when_present():
    freeze_file = conf.FOUNDATION / "pre_execution_manifest.json"
    if not freeze_file.exists():
        pytest.skip("pre-execution manifest is created after preflight tests")
    manifest = json.loads(freeze_file.read_text())
    from historical_hashes import sha256_in_git_history
    for relative, expected in manifest["input_sha256"].items():
        assert sha256_in_git_history(relative, expected), relative
    # Allocation artifacts are still checked as the exact frozen files.
    assert conf.sha256(conf.FOUNDATION / "planned_histories.csv") == manifest["planned_histories_sha256"]
    assert conf.sha256(conf.FOUNDATION / "random_invocation_schedule.csv") == manifest["random_schedule_sha256"]
    frozen = manifest
    assert frozen["histories_total"] == 868
    assert frozen["domains"] == conf.EXPECTED_DOMAIN_COUNTS
    progress_file = conf.OUTPUT / "execution_progress.json"
    if not progress_file.exists():
        return
    progress = json.loads(progress_file.read_text())
    if progress["status"] != "complete":
        return
    assert progress["run_count"] == 6944
    assert progress["trajectory_count"] == 249984
    assert conf.sha256(conf.OUTPUT / "runs.csv.gz") == progress["runs_sha256"]
    assert conf.sha256(conf.OUTPUT / "trajectories.csv.gz") == progress["trajectories_sha256"]

