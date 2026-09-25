from __future__ import annotations

import importlib.util
import sys
from argparse import Namespace
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


analysis = load("test_rq0_analysis", ROOT / "experiments/confirmatory/rq0_integrated/analyze.py")
runner = load("test_rq0_runner", ROOT / "experiments/confirmatory/rq0_integrated/run.py")


def q(rho: float, delta: float):
    return analysis.Quantities(u_f=rho, u_d=0.0, v0=1.0, v_rep=1.0 + delta)


def test_frozen_grid_and_counts():
    assert runner.SEEDS == (0, 1, 2, 3, 4)
    assert runner.DOMAINS == ("photo", "art_painting", "cartoon", "sketch")
    assert runner.N_VALUES == (25, 50, 100)
    assert runner.COSTS == (0.0, 0.02, 0.05, 0.10, 0.15)
    assert runner.HORIZONS == (1, 2, 5, 10)
    assert 5 + 5 + 5 * 4 * 3 == runner.EXPECTED_STATES == 70
    assert 5 * 4 * 3 == 60
    assert 5 * 4 * 3 * 5 * 4 == 1200


def test_pretest_explicitly_blocks_test_access():
    with pytest.raises(runner.TestAccessError):
        runner.ModeGuard(False).require_test_access("resolve split")
    runner.ModeGuard(True).require_test_access("explicit confirmation")


def test_default_mode_is_pretest_and_cpu_only():
    args = runner.parse_args([])
    assert args.confirmatory_test is False
    assert args.device == "cpu"
    with pytest.raises(SystemExit):
        runner.parse_args(["--device", "mps"])
    with pytest.raises(SystemExit):
        runner.parse_args(["--confirmatory-test"])


@pytest.mark.parametrize(
    "rho,delta,h,kappa,expected_sep,expected_hls",
    [
        (0.0, 0.1, 1, 0.0, analysis.ACTION_F0, analysis.ACTION_DREP),
        (0.1, 0.1, 1, 0.0, analysis.ACTION_F0, analysis.ACTION_F0),
        (-0.1, 0.1, 1, 0.1, analysis.ACTION_D0, analysis.ACTION_D0),
        (-0.1, 0.1, 1, 0.099, analysis.ACTION_DREP, analysis.ACTION_DREP),
    ],
)
def test_policy_ties_and_strict_thresholds(rho, delta, h, kappa, expected_sep, expected_hls):
    state = q(rho, delta)
    assert analysis.choose_sep(state, h, kappa) == expected_sep
    assert analysis.choose_hls(state, h, kappa) == expected_hls
    assert analysis.choose_sepomega(state, h, kappa) == expected_hls


def test_kappa_star_and_hls_sepomega_equivalence():
    for rho in (-0.2, 0.0, 0.1, 0.4):
        for delta in (-0.1, 0.0, 0.05, 0.3):
            state = q(rho, delta)
            for h in analysis.HORIZONS:
                assert analysis.kappa_star(state, h) == pytest.approx(h * delta - max(rho, 0.0))
                for kappa in analysis.diagnostic_kappas(state, h):
                    row = analysis.policy_row(state, state, h, kappa)
                    assert row["hls_action"] == row["sepomega_action"]
                    assert abs(row["Delta_coord"]) <= 1e-12


def test_aggregation_requires_twelve_cases_and_signs():
    rows = []
    for seed in runner.SEEDS:
        for case in range(12):
            rows.append({"seed": seed, "c": 0.0, "h": 1, "kappa": 0.0,
                         "J_SEP": 1.0, "J_HLS": 1.25, "J_SEP_Omega": 1.25})
    result = analysis.aggregate_cases(pd.DataFrame(rows))
    assert len(result) == 5
    assert (result.DeltaJ.sub(0.25).abs() <= 1e-12).all()
    assert (result.Delta_coord.abs() <= 1e-12).all()


def full_cells(intervals):
    return {(c, h): list(intervals) for c in analysis.COSTS for h in analysis.HORIZONS}


def test_frozen_classification_positive_null_inconclusive():
    assert analysis.classify_positive_regions(full_cells([(0.0, 1.0)]), [(0.0, 1.0)])[0] == "POSITIVE"
    assert analysis.classify_positive_regions(full_cells([]), [])[0] == "NULL"
    cells = full_cells([(0.0, 1.0)])
    cells[(0.0, 1)] = []
    assert analysis.classify_positive_regions(cells, [(0.0, 1.0)])[0] == "INCONCLUSIVE"


def test_real_inventory_provenance_hashes_and_validation_reconstruction():
    inventory, scores, compatibility = runner.build_inventory()
    assert compatibility == {
        "compatible": True, "test": "CLOSED", "families": 60,
        "new_fits": 120, "new_evaluations": 180,
        "method_states": 360, "matched_opportunity_projections": 60,
    }
    assert len(inventory) == 70
    assert pd.Series([row["state_type"] for row in inventory]).value_counts().to_dict() == {"REP": 60, "F0": 5, "D": 5}
    rows, error = runner.validation_reconstruction(inventory, scores)
    assert len(rows) == 70
    assert error <= 1e-12
    assert all(str(row["split_identifier"]).startswith(runner.TEST_SPLIT_IDENTIFIER) for row in inventory)


def test_validation_policy_checks_are_finite_and_equivalent():
    _, scores, _ = runner.build_inventory()
    rows, summary = runner.policy_checks(scores)
    assert rows
    assert summary["hls_sepomega_mismatches"] == 0
    assert summary["max_identity_error"] <= 1e-12
    assert summary["nan_count"] == 0


def test_refuses_to_overwrite_completed_confirmation(tmp_path):
    out = tmp_path
    (out / "confirmatory_test").mkdir(parents=True)
    (out / "confirmatory_test" / "COMPLETE.json").write_text("{}")
    runner.atomic_json(out / "pretest_summary.json", {"pretest_status": "PASS", "TEST_STATUS": "CLOSED"})
    runner.atomic_json(out / "evaluation_manifest.json", {
        "protocol_commit": runner.PROTOCOL_COMMIT,
        "protocol_sha256": runner.sha256_file(runner.PROTOCOL_PATH),
        "implementation_sha256": runner.sha256_file(runner.RUN_PATH),
        "analysis_sha256": runner.sha256_file(runner.ANALYZE_PATH),
    })
    runner.atomic_json(out / "pretest_manifest.json", {
        "evaluation_manifest_sha256": runner.sha256_file(out / "evaluation_manifest.json")
    })
    args = Namespace(output_dir=out, audit_existing=False, image_root=tmp_path, dataset_manifest=tmp_path / "unused.csv", device="cpu")
    with pytest.raises(RuntimeError, match="already complete"):
        runner.run_confirmatory_test(args)


def test_restart_reuses_only_complete_hash_matching_evaluation(tmp_path):
    path = tmp_path / "eval.json"
    runner.atomic_json(path, {"checkpoint_sha256": "model", "evaluation_split": "test"})
    prior = {"status": "complete", "sha256": runner.sha256_file(path)}
    assert runner.valid_cached_evaluation(prior, path, "model") is not None
    assert runner.valid_cached_evaluation(prior, path, "other") is None
    path.write_text("{}")
    assert runner.valid_cached_evaluation(prior, path, "model") is None


def test_pretest_does_not_dispatch_confirmatory_evaluator(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "_confirmatory_evaluator", lambda *a, **k: pytest.fail("TEST evaluator called"))
    monkeypatch.setattr(runner, "build_inventory", lambda: ([], {}, {"compatible": True, "test": "CLOSED"}))
    monkeypatch.setattr(runner, "validation_reconstruction", lambda inventory, scores: ([], 0.0))
    monkeypatch.setattr(runner, "policy_checks", lambda scores: ([], {"hls_sepomega_mismatches": 0, "max_identity_error": 0.0, "max_frozen_value_error": 0.0, "nan_count": 0}))
    summary = runner.run_pretest(tmp_path, tests_passed=True)
    assert summary["TEST_STATUS"] == "CLOSED"


def test_protocol_commit_is_present_in_head_history():
    import subprocess
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", runner.PROTOCOL_COMMIT, "HEAD"],
        cwd=ROOT, check=False,
    )
    assert completed.returncode == 0


def test_runner_contains_no_training_operations():
    source = runner.RUN_PATH.read_text()
    assert "optimizer.step(" not in source
    assert ".backward(" not in source
    assert "model.train(" not in source


def synthetic_scores(rep_value: float, bad_seed: int | None = None):
    values = {}
    for seed in runner.SEEDS:
        f0 = {d: 0.5 for d in runner.DOMAINS}
        deep = {d: 0.4 for d in runner.DOMAINS}
        rep = {d: (0.0 if seed == bad_seed else rep_value) for d in runner.DOMAINS}
        for domain in runner.DOMAINS:
            for n in runner.N_VALUES:
                values[("F0", seed, n, domain)] = f0
                values[("D", seed, n, domain)] = deep
                values[("REP", seed, n, domain)] = rep
    return values


def test_exact_surface_classification_synthetic():
    positive = synthetic_scores(0.8)
    surface, result = analysis.confirmatory_surface(positive, positive)
    assert not surface.empty
    assert result["classification"] == "POSITIVE"
    assert result["max_delta_coord"] <= 1e-12
    null = synthetic_scores(0.5)
    _, result = analysis.confirmatory_surface(null, null)
    assert result["classification"] == "NULL"
