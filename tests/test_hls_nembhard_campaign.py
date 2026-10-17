from collections import Counter
from dataclasses import replace
import math

import pytest

from hls.nembhard_campaign import (
    ARMS,
    PROFILE_K,
    _fixed_allocation,
    _build_result_payload,
    _persist_result_payload,
    _run_configuration,
    allocation_share_summary,
    grouped_descriptives,
    analyze_campaign,
    bootstrap_interval,
    build_design_registry,
    build_demand_sequence,
    demand_multiset_hash,
    ordered_demand_hash,
    paired_differences,
    paired_order_differences,
    paired_period_differences,
    policy_condition_id,
    protocol_interaction_contrasts,
    seed_bundle,
    summarize_paired_contrast,
    temporal_summary,
    validate_design,
    validate_configuration,
)
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK, validate_productive_allocation_nk


def test_design_reconciles_to_1016_unique_configs_without_running_episodes():
    registry = build_design_registry()
    assert len(registry.episodes) == 1016
    assert Counter(config.design_component for config in registry.episodes) == {
        "primary": 960, "epsilon_zero": 40, "permutation_diagnostic": 16,
    }
    assert registry.nominal_diagnostic_count == 18
    assert registry.duplicate_diagnostic_count == 2
    assert len(registry.diagnostic_aliases) == 2
    assert len({config.episode_id for config in registry.episodes}) == 1016
    assert set(config.arm for config in registry.episodes) == set(ARMS)
    assert validate_design(registry)["episodes_executed"] == 0


def test_seed_formula_and_demand_builders_are_deterministic_and_paired_by_multiset():
    bundle = seed_bundle(3)
    assert (bundle.interleaved_demand, bundle.clustered_demand,
            bundle.observations, bundle.exploration) == (20291018, 20291019, 20291020, 20291021)
    interleaved = build_demand_sequence("interleaved", bundle.interleaved_demand)
    clustered = build_demand_sequence("clustered", bundle.clustered_demand)
    assert len(interleaved.problems) == len(clustered.problems) == 120
    assert Counter(p.problem_id for p in interleaved.problems) == {
        "skill1": 40, "skill2": 40, "joint": 40,
    }
    assert Counter(p.problem_id for p in clustered.problems) == Counter(
        p.problem_id for p in interleaved.problems)
    assert interleaved.maximum_run <= 2
    assert clustered.maximum_run >= 20
    assert interleaved.multiset_hash == clustered.multiset_hash
    assert interleaved.ordered_hash != clustered.ordered_hash
    assert interleaved.ordered_hash == ordered_demand_hash(interleaved.problems)
    assert interleaved.multiset_hash == demand_multiset_hash(clustered.problems)
    assert build_demand_sequence("clustered", bundle.clustered_demand) == clustered


def test_profiles_and_learning_parameters_match_protocol():
    assert tuple(PROFILE_K) == ("homogeneous", "mixed", "specialists")
    for matrix in PROFILE_K.values():
        assert all(math.isclose(sum(row[k] for row in matrix), 3.6) for k in range(2))
    registry = build_design_registry()
    for config in registry.episodes:
        validate_configuration(config)


def test_fixed_mapping_is_static_role_conditioned_and_feasible():
    org = OrganizationConfigNK(
        ("skill1_role", "skill2_role", "generalist_role"),
        ("skill1", "skill2"), ((0, 0),) * 3, (1, 1, 1), 2,
    )
    problems = (
        ProblemSpecNK("skill1", (1.4, 0), 2, (0.5, 0.5)),
        ProblemSpecNK("skill2", (0, 1.4), 2, (0.5, 0.5)),
        ProblemSpecNK("joint", (0.7, 0.7), 2, (0.5, 0.5)),
    )
    actions = tuple(_fixed_allocation(problem, org.agent_ids) for problem in problems)
    assert actions == (
        ((1, 0), (0, 0), (1, 0)),
        ((0, 0), (0, 1), (0, 1)),
        ((1, 0), (0, 1), (0, 0)),
    )
    assert all(validate_productive_allocation_nk(action, org, problem)
               for action, problem in zip(actions, problems))


def test_short_synthetic_episode_uses_existing_nembhard_runner_and_transitions():
    registry = build_design_registry()
    config = next(config for config in registry.episodes
                  if config.arm == "fixed" and config.design_component == "primary")
    short = (
        ProblemSpecNK("skill1", (1.4, 0), 2, (0.5, 0.5)),
        ProblemSpecNK("joint", (0.7, 0.7), 2, (0.5, 0.5)),
    )
    result, used_problems = _run_configuration(config, problems_override=short)
    assert used_problems == short
    assert len(result.records) == 2
    first = result.records[0]
    assert first.experience_before == ((0, 0), (0, 0), (0, 0))
    assert first.experience_increment == first.allocation
    assert first.productivity_before[0][0] == PROFILE_K[config.profile_id][0][0] / 2
    assert first.outputs[0] == sum(first.individual_outputs[i][0] for i in range(3))
    assert result.final_experience == result.records[-1].experience_after


def test_short_adaptive_episode_replays_and_records_decision_information_separately():
    registry = build_design_registry()
    config = next(config for config in registry.episodes
                  if config.arm == "adaptive_sigma_0" and config.epsilon == 0.0)
    short = (
        ProblemSpecNK("skill1", (1.4, 0), 2, (0.5, 0.5)),
        ProblemSpecNK("skill2", (0, 1.4), 2, (0.5, 0.5)),
        ProblemSpecNK("joint", (0.7, 0.7), 2, (0.5, 0.5)),
    )
    first, _ = _run_configuration(config, problems_override=short)
    replay, _ = _run_configuration(config, problems_override=short)
    assert first == replay
    assert all(record.adaptive_estimator_before is not None for record in first.records)
    assert first.records[0].adaptive_estimator_before.means == ((0.6, 0.6),) * 3
    assert first.records[0].adaptive_observations is not None
    assert first.records[0].router_observable_experience == ((0.0, 0.0),) * 3
    assert first.records[0].router_predicted_outputs is not None
    assert first.records[0].experience_after != first.records[0].router_observable_experience
    payload = _build_result_payload(config, first, short)
    run = payload["experiment_run"]
    assert run["schema_version"] == "hls-experiment-run/1.0"
    assert run["policy_id"] == "nembhard_adaptive"
    metric_names = [item["name"] for item in run["metrics"]]
    assert len(metric_names) == len(set(metric_names))
    assert run["configuration"]["profile_k"]
    assert run["mechanism_results"]["records"][0]["adaptive_estimator_before"]
    assert {item["name"] for item in run["metrics"]} >= {
        "cumulative_task_relevant_production", "functional_success_proportion",
        "cumulative_normalized_deficit", "adaptive_prediction_error_mean[skill1]",
    }


def _metric_payload(value):
    return {"campaign_metrics": {"metrics": [{"name": "m", "value": value}]}}


def test_paired_contrast_and_interaction_helpers_preserve_replicate_pairing():
    registry = build_design_registry()
    fixed = next(c for c in registry.episodes if c.profile_id == "mixed"
                 and c.learning_scale_id == "fast" and c.demand_order == "interleaved"
                 and c.replicate == 0 and c.arm == "fixed" and c.design_component == "primary")
    adaptive = next(c for c in registry.episodes if c.profile_id == "mixed"
                    and c.learning_scale_id == "fast" and c.demand_order == "interleaved"
                    and c.replicate == 0 and c.arm == "adaptive_sigma_0"
                    and c.epsilon == 0.05 and c.design_component == "primary")
    pairs = paired_differences(((fixed, _metric_payload(2)),
                                (adaptive, _metric_payload(5))),
                               policy_condition_id(adaptive), "fixed", "m")
    assert pairs[0]["difference"] == 3
    with pytest.raises(ValueError, match="unmatched"):
        paired_differences(((fixed, _metric_payload(2)),), "oracle", "fixed", "m")


def test_bootstrap_is_deterministic_and_summary_keeps_bundle_count():
    values = ({"difference": value} for value in (-2.0, -1.0, 1.0, 2.0))
    pairs = tuple(values)
    assert bootstrap_interval((-2, -1, 1, 2), seed=7, resamples=1000) == \
        bootstrap_interval((-2, -1, 1, 2), seed=7, resamples=1000)
    summary = summarize_paired_contrast(pairs, seed=7, resamples=1000)
    assert summary["n_pairs"] == 4
    assert summary["mean"] == 0
    assert summary["proportion_positive"] == 0.5


def test_epsilon_sensitivity_pairs_only_the_controlled_mixed_fast_clustered_slice():
    registry = build_design_registry()
    selected = [config for config in registry.episodes
                if config.profile_id == "mixed" and config.learning_scale_id == "fast"
                and config.demand_order == "clustered" and config.arm == "adaptive_sigma_0"
                and config.design_component in {"primary", "epsilon_zero"}]
    rows = [(config, _metric_payload(config.epsilon)) for config in selected]
    pairs = paired_differences(rows, "adaptive_sigma_0_eps_0.00",
                               "adaptive_sigma_0_eps_0.05", "m",
                               components=("primary", "epsilon_zero"))
    assert len(pairs) == 20
    assert {pair["difference"] for pair in pairs} == {-0.05}


def test_predeclared_h1_h3_difference_in_differences_are_bundle_level():
    registry = build_design_registry()
    rows = []
    profiles = {"homogeneous": 1.0, "mixed": 3.0, "specialists": 5.0}
    for config in registry.episodes:
        if config.design_component != "primary" or config.arm not in {"fixed", "adaptive_sigma_0"}:
            continue
        if config.arm == "fixed":
            value = 0.0
        else:
            value = (profiles[config.profile_id]
                     + (2.0 if config.learning_scale_id == "fast" else 0.0)
                     + (4.0 if config.demand_order == "clustered" else 0.0))
        rows.append((config, _metric_payload(value)))
    contrasts = protocol_interaction_contrasts(
        rows, "adaptive_sigma_0_eps_0.05", "fixed", "m")
    h1_mixed = contrasts["H1_mixed_minus_homogeneous"]
    assert len(h1_mixed) == 4
    assert all(len(values) == 20 and set(values) == {2.0} for values in h1_mixed.values())
    h1_specialists = contrasts["H1_specialists_minus_homogeneous"]
    assert all(len(values) == 20 and set(values) == {4.0}
               for values in h1_specialists.values())
    assert all(len(values) == 20 and set(values) == {2.0}
               for values in contrasts["H2_fast_minus_slow"].values())
    assert all(len(values) == 20 and set(values) == {4.0}
               for values in contrasts["H3_clustered_minus_interleaved"].values())


def test_period_level_pairing_keeps_episode_as_unit():
    registry = build_design_registry()
    fixed = next(c for c in registry.episodes if c.profile_id == "homogeneous"
                 and c.learning_scale_id == "fast" and c.demand_order == "interleaved"
                 and c.replicate == 0 and c.arm == "fixed" and c.design_component == "primary")
    adaptive = next(c for c in registry.episodes if c.profile_id == "homogeneous"
                    and c.learning_scale_id == "fast" and c.demand_order == "interleaved"
                    and c.replicate == 0 and c.arm == "adaptive_sigma_0"
                    and c.epsilon == 0.05 and c.design_component == "primary")
    def period_payload(value):
        return {"campaign_metrics": {"period_metrics": [
            {"task_relevant_output": value, "functional_success": value > 0,
             "normalized_deficit": 2 - value}
        ]}}
    pairs = paired_period_differences(
        ((fixed, period_payload(1.0)), (adaptive, period_payload(1.5))),
        policy_condition_id(adaptive), "fixed", 0,
        "cumulative_task_relevant_production",
    )
    assert len(pairs) == 1 and pairs[0]["difference"] == 0.5


def test_order_contrast_pairs_same_replicate_and_multiset_not_sequence_hash():
    registry = build_design_registry()
    selected = [config for config in registry.episodes
                if config.profile_id == "mixed" and config.learning_scale_id == "fast"
                and config.replicate == 0 and config.arm == "fixed"
                and config.design_component == "primary"]
    rows = [(config, _metric_payload(3 if config.demand_order == "clustered" else 1))
            for config in selected]
    pairs = paired_order_differences(rows, "fixed", "m")
    assert len(pairs) == 1
    assert pairs[0]["difference"] == 2


def test_campaign_analysis_refuses_incomplete_or_duplicate_campaign_data():
    with pytest.raises(ValueError, match="complete 1,016-run design"):
        analyze_campaign(())


def test_analysis_keeps_uncertainty_stratified_and_uses_complete_registry():
    registry = build_design_registry()
    profile_value = {"homogeneous": 0, "mixed": 1, "specialists": 2}
    rows = []
    for config in registry.episodes:
        value = (10 + profile_value[config.profile_id]
                 + (1 if config.learning_scale_id == "fast" else 0)
                 + (2 if config.demand_order == "clustered" else 0)
                 + (0.5 if config.arm.startswith("adaptive") else 0)
                 + config.replicate / 100)
        payload = {"campaign_metrics": {
            "metrics": [
                {"name": "cumulative_task_relevant_production", "value": value},
                {"name": "functional_success_proportion", "value": value / 20},
                {"name": "cumulative_normalized_deficit", "value": 20 - value},
            ],
            "period_metrics": [{"task_relevant_output": value / 120,
                                "functional_success": value > 0,
                                "normalized_deficit": (20 - value) / 120}],
        }}
        rows.append((config, payload))
    analysis = analyze_campaign(rows, resamples=20)
    production_contrasts = analysis["results"]["cumulative_task_relevant_production"]
    assert len(production_contrasts["adaptive_sigma_0_eps_0.05_minus_fixed"]) == 12
    assert all(stratum["n_pairs"] == 20 for stratum in
               production_contrasts["adaptive_sigma_0_eps_0.05_minus_fixed"])
    order = analysis["results"]["demand_order_contrasts"][
        "cumulative_task_relevant_production"]["fixed"]
    assert len(order) == 6 and all(stratum["n_pairs"] == 20 for stratum in order)
    assert len(production_contrasts["predeclared_interactions"][
        "H1_mixed_minus_homogeneous"]) == 4


def test_config_validation_rejects_wrong_protocol_resources_or_hash():
    config = build_design_registry().episodes[0]
    with pytest.raises(ValueError, match="resource"):
        validate_configuration(replace(config, collective_budget=1.5))
    with pytest.raises(ValueError, match="identifiers"):
        validate_configuration(replace(config, sequence_id="0" * 64))


def test_result_persistence_is_stable_and_refuses_overwrite(tmp_path):
    registry = build_design_registry()
    config = next(config for config in registry.episodes
                  if config.arm == "fixed" and config.design_component == "primary")
    short = (ProblemSpecNK("skill1", (1.4, 0), 2, (0.5, 0.5)),)
    result, used_problems = _run_configuration(config, problems_override=short)
    payload = _build_result_payload(config, result, used_problems)
    assert len(temporal_summary(((config, payload),))) == 1
    shares = allocation_share_summary(((config, payload),))
    skill1_shares = next(row for row in shares if row["problem_id"] == "skill1")
    assert sum(skill1_shares["mean_agent_effort_shares"]) == 1.0
    assert grouped_descriptives(((config, payload),))[0]["metrics"]
    destination = _persist_result_payload(config, payload, tmp_path)
    original = (destination / "run.json").read_bytes()
    assert (destination / "campaign_metrics.json").is_file()
    assert (destination / "native_nembhard_result.json").is_file()
    with pytest.raises(FileExistsError):
        _persist_result_payload(config, payload, tmp_path)
    assert (destination / "run.json").read_bytes() == original
