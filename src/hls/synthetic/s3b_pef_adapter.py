"""Scenario-specific S3b adapter for paired matching-bandit traces."""

from __future__ import annotations

from math import isclose
from typing import Mapping, Sequence

from hls.experiment_contract import (
    ExperimentEvent,
    ExperimentRun,
    MetricValue,
    SeedRecord,
    UnitDeclaration,
)
from hls.performance_evaluation import EvaluationProfile, EvaluationRecord, Status


SCENARIO_ID = "S3b"
ORGANIZATIONAL_PROBLEM_ID = "B2_complete_one_to_one_matching_3x3"
PROFILE_PREFIX = "s3b_b2_ucb_memory_factorial"
PAIR_ORDER = tuple((i, k) for i in range(3) for k in range(3))
HORIZON = 10_000
REWARD_SEED_XOR = 0xA17E5B
OPPORTUNITY_SEED_XOR = 0x0B5E7A


def s3b_evaluation_profile(change_level: str, interval: int,
                           availability_level: str, probability: float
                           ) -> EvaluationProfile:
    if change_level not in {"infrequent", "frequent"}:
        raise ValueError("unknown S3b change-frequency level")
    if availability_level not in {"high", "low"} or not 0 < probability <= 1:
        raise ValueError("invalid S3b observation-opportunity level")
    configuration_id = f"s3b_b2_{change_level}_{availability_level}_T{HORIZON}_v1"
    return EvaluationProfile(
        profile_id=f"{PROFILE_PREFIX}_{change_level}_{availability_level}_v1",
        scenario_id=SCENARIO_ID,
        configuration_id=configuration_id,
        application_domain="synthetic_assignment_bandit",
        organizational_problem=ORGANIZATIONAL_PROBLEM_ID,
        decision_objective={
            "UCB1": "cumulative_expected_B2_matching_reward",
            "SW-UCB": "cumulative_expected_B2_matching_reward",
        },
        constraints="exact full 3x3 one-to-one matching; same six feasible matchings in every condition",
        primary_metrics=("original_reward_cumulative",),
        diagnostic_fields=(
            "assignment", "oracle_assignment", "observation_opportunities",
            "observed_pair_feedback", "pairwise_estimates", "pairwise_indices",
            "expected_regret", "realized_reward", "optimal_matching",
        ),
        information_regime=(
            f"B2 semi-bandit; per-pair feedback opportunity p={probability:g} "
            "is hidden until after matching; only executed pairs with available feedback are observed"
        ),
        temporal_horizon=HORIZON,
        aggregation_rules="sum expected reward over 10,000 complete-matching periods",
        demand_distribution_id=f"S3b_recurrent_base_transient_tau{interval}_v1",
    )


def adapt_s3b_episode(
    episode: Mapping,
    detailed_periods: Sequence[Mapping],
    profile: EvaluationProfile,
    *,
    trace_artifact: str,
    run_id: str,
    software_revision: str | None,
    base_git_revision: str,
    seed: int,
    configuration: Mapping,
    pair_information: Mapping,
) -> tuple[ExperimentRun, tuple[EvaluationRecord, ...]]:
    """Build one compact ExperimentRun and PEF rows for a single seed/policy.

    Detailed decisions and estimator diagnostics stay in the compressed trace;
    the common run references that trace instead of duplicating 10,000 events.
    """
    policy_id = episode.get("policy")
    if policy_id not in {"UCB1", "SW-UCB"}:
        raise ValueError("unsupported S3b policy")
    if not trace_artifact or not run_id or not base_git_revision:
        raise ValueError("run identity and trace/revision provenance are required")
    if len(detailed_periods) != profile.temporal_horizon:
        raise ValueError("detailed trace must cover the declared horizon")
    if any(row.get("t") != period for period, row in enumerate(detailed_periods)):
        raise ValueError("trace periods must be contiguous and ordered")
    expected_reward = sum(float(row["expected_reward"]) for row in detailed_periods)
    expected_regret = sum(float(row["expected_regret"]) for row in detailed_periods)
    realized_reward = sum(float(row["realized_reward"]) for row in detailed_periods)
    optimal_rate = sum(bool(row["optimal_matching"]) for row in detailed_periods) / len(detailed_periods)
    if not isclose(expected_reward, float(episode["expected_reward"]), rel_tol=0.0, abs_tol=1e-8):
        raise ValueError("trace expected reward does not reconcile with episode summary")
    if not isclose(expected_regret, float(episode["expected_regret"]), rel_tol=0.0, abs_tol=1e-8):
        raise ValueError("trace regret does not reconcile with episode summary")
    if not isclose(realized_reward, float(episode["realized_reward"]), rel_tol=0.0, abs_tol=1e-8):
        raise ValueError("trace realized reward does not reconcile with episode summary")
    if not isclose(optimal_rate, float(episode["optimal_rate"]), rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("trace optimal-matching rate does not reconcile with episode summary")

    records = tuple(EvaluationRecord(
        scenario_id=SCENARIO_ID,
        configuration_id=profile.configuration_id,
        policy_id=policy_id,
        period=int(row["t"]),
        demand="complete_three_task_matching",
        original_reward=float(row["expected_reward"]),
        available_metadata={
            "trace_artifact": trace_artifact,
            "replicate_id": run_id,
            "period_trace_index": int(row["t"]),
        },
        provenance=f"{trace_artifact}#run_id={run_id}&period={row['t']}",
        information_regime=profile.information_regime,
        decision_objective=profile.decision_objective[policy_id],
        field_status={
            "output": Status.NOT_APPLICABLE,
            "requirements": Status.NOT_APPLICABLE,
            "success": Status.NOT_APPLICABLE,
            "deficit": Status.NOT_APPLICABLE,
            "resource_usage": Status.NOT_APPLICABLE,
        },
    ) for row in detailed_periods)

    seeds = (
        SeedRecord("bernoulli_rewards", int(seed) ^ REWARD_SEED_XOR,
                   "potential task-pair outcomes, indexed by period-agent-task"),
        SeedRecord("observation_opportunities", int(seed) ^ OPPORTUNITY_SEED_XOR,
                   "exogenous per-pair feedback masks; nested availability levels"),
    )
    metrics = (
        MetricValue("original_reward_cumulative", expected_reward, "declared_reward",
                    "Sum of expected rewards of executed complete matchings."),
        MetricValue("realized_reward_cumulative", realized_reward, "Bernoulli_reward",
                    "Sum of realized rewards for selected pairs, whether feedback was observed or not."),
        MetricValue("expected_regret_cumulative", expected_regret, "declared_reward_gap",
                    "Sum of exact true-mean matching oracle reward minus selected matching expected reward.",
                    "lower"),
        MetricValue("optimal_matching_rate", optimal_rate, "fraction",
                    "Fraction of periods matching the exact true-mean oracle matching."),
        MetricValue("assignment_count_cumulative", 3 * len(detailed_periods), "agent-task_assignments",
                    "Three executed pairs per complete matching; structural count, not a modeled cost."),
        MetricValue("mean_estimation_mse", statistics_mean(
            float(episode["pair_information"][f"{i},{k}"]["mean_estimation_squared_error"])
            for i, k in PAIR_ORDER), "squared_reward_probability_error",
                    "Unweighted mean of per-pair temporal squared estimation errors."),
    )
    run = ExperimentRun(
        schema_version="hls-experiment-run/1.0",
        run_id=run_id,
        mechanism_id="pairwise_UCB_indices_plus_exact_matching",
        policy_id=policy_id,
        configuration=dict(configuration),
        initial_conditions={"competence_matrix": configuration["competence_base"]},
        random_seeds=seeds,
        information_available={
            "policy_view": "past observed outcomes on executed pairs only",
            "competence_matrices": "hidden from policy; evaluation-only in period trace",
            "observation_opportunity_mask": "unavailable before matching; feedback mask revealed after execution",
            "future_competence_regime": "not revealed to policy",
        },
        observation_model={
            "reward": "Bernoulli competence for each selected pair",
            "feedback": "selected pair outcome observed iff its exogenous mask is available",
            "random_streams": ["bernoulli_rewards", "observation_opportunities"],
        },
        software_revision=software_revision,
        units=(
            UnitDeclaration("original_reward", "declared_reward", "Expected collective matching reward per period."),
            UnitDeclaration("realized_reward", "Bernoulli_reward", "Sum of realized selected-pair outcomes."),
            UnitDeclaration("expected_regret", "declared_reward_gap", "Difference from exact true-mean matching oracle."),
            UnitDeclaration("assignment_count", "agent-task_assignments", "Three pairs are executed per period; not a resource cost."),
            UnitDeclaration("competence_estimation_error", "squared_reward_probability_error", "Squared probability-scale estimation error."),
        ),
        events=(ExperimentEvent(
            0, "external_period_trace", "pairwise_UCB_indices_plus_exact_matching",
            {"artifact": trace_artifact, "run_id_filter": run_id,
             "period_count": profile.temporal_horizon,
             "trace_schema": "s3b_compact_pairwise_diagnostics_v1"},
        ),),
        metrics=metrics,
        mechanism_results={
            "expected_reward": expected_reward,
            "realized_reward": realized_reward,
            "oracle_expected_reward": float(episode["oracle_expected_reward"]),
            "expected_regret": expected_regret,
            "optimal_matching_rate": optimal_rate,
            "assignment_changes": int(episode["assignment_changes"]),
            "pair_information": dict(pair_information),
            "recovery_lags": list(episode["recovery_lags"]),
            "resource_cost": None,
            "resource_cost_status": "NOT_APPLICABLE: the S3b matching model has no per-assignment resource cost"},
        metadata={
            "evaluation_profile_id": profile.profile_id,
            "organizational_problem_id": ORGANIZATIONAL_PROBLEM_ID,
            "replicate_id": run_id,
            "policy_role": "published_index_adaptation_to_pairwise_matching",
            "trace_artifact": trace_artifact,
            "base_git_revision": base_git_revision,
            "software_revision_exact": software_revision is not None,
        },
    )
    return run, records


def statistics_mean(values) -> float:
    rows = tuple(values)
    if not rows:
        raise ValueError("at least one pair is needed for mean estimation error")
    return sum(rows) / len(rows)
