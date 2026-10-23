from __future__ import annotations

from dataclasses import replace

from experiments import run_hls_s3b_change_observation_factorial as source
from experiments import run_hls_s3b_memory_replay_diagnostic as diagnostic
from hls.experiment_contract import ExperimentRun
from hls.nonstationary_assignment import PairwiseBanditEstimator


def _shrink(monkeypatch, horizon=42):
    monkeypatch.setattr(source, "HORIZON", horizon)
    monkeypatch.setattr(source, "CALIBRATION", 9)
    monkeypatch.setattr(diagnostic, "HORIZON", horizon)
    monkeypatch.setattr(diagnostic, "CALIBRATION", 9)


def test_mean_memory_estimators_differ_only_by_time_filter(monkeypatch):
    _shrink(monkeypatch)
    full = PairwiseBanditEstimator(1, 1, method="global_mean", window=5)
    window = PairwiseBanditEstimator(1, 1, method="recent_mean", window=5)
    for period, value in ((0, 1.0), (9, 0.0)):
        full.update(period, ((0, 0),), {(0, 0): value})
        window.update(period, ((0, 0),), {(0, 0): value})
    assert full.empirical_mean_matrix(10) == ((.5,),)
    assert window.empirical_mean_matrix(10) == ((0.0,),)
    assert full.score_matrix(10) == full.empirical_mean_matrix(10)
    assert window.score_matrix(10) == window.empirical_mean_matrix(10)


def test_matching_rule_is_catalog_order_independent_and_maximizes_mean():
    values = ((.8, .2, .1), (.1, .7, .2), (.3, .1, .6))
    forward = diagnostic.choose_matching(values, diagnostic.MATCHING_CATALOG)
    reverse = diagnostic.choose_matching(values, tuple(reversed(diagnostic.MATCHING_CATALOG)))
    assert forward == reverse
    value = sum(values[i][k] for i, k in forward)
    assert value == max(sum(values[i][k] for i, k in m)
                        for m in diagnostic.MATCHING_CATALOG)


def test_shared_control_gives_identical_observation_history(monkeypatch):
    _shrink(monkeypatch)
    seed = 9000
    reward, opportunity = source.generate_randomness(seed)
    condition = {"label": "infrequent/high", "interval": 20, "p": .75}
    full = diagnostic.run_episode(seed, condition, "shared_observations", "FULL", reward, opportunity)
    window = diagnostic.run_episode(seed, condition, "shared_observations", "WINDOW", reward, opportunity)
    assert full["observation_sequence_sha256"] == window["observation_sequence_sha256"]
    assert full["competence_path_sha256"] == window["competence_path_sha256"]
    assert full["observations_per_pair"] == window["observations_per_pair"]
    assert len(full["time_metrics"]["expected_regret"]) == 42


def test_closed_loop_uses_policy_assignments_for_feedback(monkeypatch):
    _shrink(monkeypatch)
    seed = 9001
    reward, opportunity = source.generate_randomness(seed)
    condition = {"label": "frequent/low", "interval": 10, "p": .25}
    full = diagnostic.run_episode(seed, condition, "closed_loop", "FULL", reward, opportunity)
    window = diagnostic.run_episode(seed, condition, "closed_loop", "WINDOW", reward, opportunity)
    assert sum(full["scheduled_or_executed_count_per_pair"].values()) == 3 * 42
    assert sum(window["scheduled_or_executed_count_per_pair"].values()) == 3 * 42
    assert full["competence_path_sha256"] == window["competence_path_sha256"]
    assert full["expected_regret"] >= 0 and window["expected_regret"] >= 0


def test_runner_builds_pef_runs_and_checks_roundtrip(monkeypatch):
    _shrink(monkeypatch, 42)
    monkeypatch.setattr(diagnostic, "SEEDS", (9002,))
    artifact = diagnostic.run()
    assert len(artifact["episodes"]) == 12
    assert len(artifact["experiment_runs"]) == 12
    assert artifact["validation"]["shared_observation_hashes_equal"]
    for run in artifact["experiment_runs"].values():
        record = ExperimentRun.from_dict(run)
        assert record.metadata["diagnostic_only"] is True
        assert record.policy_id in {"FULL_DIAGNOSTIC", "WINDOW_DIAGNOSTIC"}
    assert all(len(curve["expected_regret"]) == 42
               for curve in artifact["period_curves_mean_across_seeds"].values())
