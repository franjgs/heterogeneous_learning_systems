from __future__ import annotations

from dataclasses import replace

import pytest

from experiments import run_hls_s3b_change_observation_factorial as source
from experiments import run_hls_s3b_observability_recovery as recovery
from hls.experiment_contract import ExperimentRun
from hls.performance_evaluation import PerformanceEvaluator
from hls.synthetic.s3b_pef_adapter import adapt_s3b_episode, s3b_evaluation_profile


def test_optional_detailed_trace_does_not_change_s3b_episode_results(monkeypatch):
    monkeypatch.setattr(source, "HORIZON", 24)
    monkeypatch.setattr(source, "CALIBRATION", 3)
    reward_uniforms, opportunity_uniforms = source.generate_randomness(9024)
    ordinary = source.run_episode(
        9024, 8, 0.5, "UCB1", reward_uniforms, opportunity_uniforms,
    )
    instrumented = source.run_episode(
        9024, 8, 0.5, "UCB1", reward_uniforms, opportunity_uniforms,
        detailed_trace=True,
    )
    ordinary_summary = {key: value for key, value in ordinary.items() if key != "trace"}
    instrumented_summary = {key: value for key, value in instrumented.items() if key != "trace"}
    assert instrumented_summary == ordinary_summary
    rows = instrumented["trace"]["detailed_periods"]
    assert len(rows) == 24
    assert rows[0]["decision_source"] == "fixed_calibration_cycle"
    assert rows[3]["decision_source"] == "estimated_pairwise_indices"
    assert len(rows[3]["estimated_mean_flat_nk"]) == 9
    assert len(rows[3]["index_flat_nk"]) == 9
    assert len(rows[3]["pair_outcomes_in_assignment_order"]) == 3


def test_s3b_run_adapter_and_pef_preserve_policy_and_information_semantics(monkeypatch):
    monkeypatch.setattr(source, "HORIZON", 24)
    monkeypatch.setattr(source, "CALIBRATION", 3)
    seed = 9025
    interval, probability = 8, 0.5
    reward_uniforms, opportunity_uniforms = source.generate_randomness(seed)
    episode = source.run_episode(
        seed, interval, probability, "SW-UCB", reward_uniforms,
        opportunity_uniforms, detailed_trace=True,
    )
    detailed = episode.pop("trace")["detailed_periods"]
    profile = replace(
        s3b_evaluation_profile("infrequent", interval, "high", probability),
        temporal_horizon=24,
    )
    run_record, records = adapt_s3b_episode(
        episode, detailed, profile,
        trace_artifact="period_traces.jsonl.gz#run_id=test",
        run_id="test-run", software_revision=None, base_git_revision="deadbeef",
        seed=seed,
        configuration={"competence_base": source.BASE, "policy": "SW-UCB"},
        pair_information=episode["pair_information"],
    )
    assert run_record.information_available["competence_matrices"].startswith("hidden")
    assert run_record.information_available["observation_opportunity_mask"].startswith("unavailable")
    assert run_record.random_seeds is not None and len(run_record.random_seeds) == 2
    assert ExperimentRun.from_json(run_record.to_json()).to_json() == run_record.to_json()
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile)
    evaluated = evaluator.evaluate(profile.profile_id, "SW-UCB", records)
    assert evaluated["original_reward_cumulative"].value == pytest.approx(episode["expected_reward"])
    assert all(record.field_status["success"].value == "NOT_APPLICABLE" for record in records)


def test_s3b_adapter_rejects_incomplete_trace_and_nonreconciled_regret(monkeypatch):
    monkeypatch.setattr(source, "HORIZON", 12)
    monkeypatch.setattr(source, "CALIBRATION", 2)
    reward_uniforms, opportunity_uniforms = source.generate_randomness(9026)
    episode = source.run_episode(
        9026, 5, 0.5, "UCB1", reward_uniforms, opportunity_uniforms,
        detailed_trace=True,
    )
    trace = episode.pop("trace")["detailed_periods"]
    profile = replace(s3b_evaluation_profile("frequent", 5, "high", 0.5), temporal_horizon=12)
    common = dict(
        profile=profile,
        trace_artifact="trace.gz",
        run_id="r",
        software_revision=None,
        base_git_revision="deadbeef",
        seed=9026,
        configuration={"competence_base": source.BASE},
        pair_information=episode["pair_information"],
    )
    with pytest.raises(ValueError, match="cover the declared horizon"):
        adapt_s3b_episode(episode, trace[:-1], **common)
    corrupted = [dict(row) for row in trace]
    corrupted[0]["expected_regret"] += 1
    with pytest.raises(ValueError, match="regret does not reconcile"):
        adapt_s3b_episode(episode, corrupted, **common)


def test_small_runner_smoke_builds_common_runs_pef_and_paired_contrasts(monkeypatch, tmp_path):
    monkeypatch.setattr(source, "HORIZON", 24)
    monkeypatch.setattr(source, "CALIBRATION", 3)
    levels = {"infrequent": 8, "frequent": 4}
    monkeypatch.setattr(source, "CHANGE_INTERVALS", levels)
    monkeypatch.setattr(recovery, "CHANGE_INTERVALS", levels)
    monkeypatch.setattr(recovery, "SEEDS", (9027,))
    monkeypatch.setattr("hls.synthetic.s3b_pef_adapter.HORIZON", 24)
    monkeypatch.setattr(recovery, "OUT_DIR", tmp_path)
    monkeypatch.setattr(recovery, "TRACE_PATH", tmp_path / "period_traces.jsonl.gz")
    artifact = recovery.run()
    assert len(artifact["episodes"]) == 8
    assert len(artifact["experiment_runs"]) == 8
    assert len(artifact["summary"]["cells"]) == 8
    assert artifact["hls_pef_paired_reward_comparisons"][
        "infrequent/high/SW_minus_UCB/reward"]["n_seeds"] == 1
    assert artifact["validation"]["experiment_run_json_round_trips"]
    assert (tmp_path / "period_traces.jsonl.gz").is_file()
