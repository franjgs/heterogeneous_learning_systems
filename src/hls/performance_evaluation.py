"""HLS-PEF v0: read-only evaluation of declared policy outcomes.

No physical transition, decision policy, or objective implementation is imported.
Historical aggregates can be registered, but never masquerade as recalculated
period metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isclose, isfinite
from typing import Mapping, Sequence


class Status(str, Enum):
    VALID = "VALID"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_OBSERVABLE = "NOT_OBSERVABLE"
    NOT_RECORDED = "NOT_RECORDED"
    UNDEFINED = "UNDEFINED"


METRICS = {
    "original_reward_cumulative": ("original_reward:v1", "declared_reward", "sum_periods"),
    "ces_cumulative": ("ces_recorded:v1", "CES_output", "sum_periods"),
    "functional_success_rate": ("full_requirements_success:v1", "fraction", "successes/demanded_periods"),
    "functional_deficit_cumulative": ("raw_positive_deficit:v1", "output", "sum_periods_and_skills"),
    "production_cumulative": ("productive_output:v1", "output", "sum_periods_and_skills"),
    "teaching_actions_cumulative": ("teaching_action_count:v1", "actions", "sum_periods"),
}


@dataclass(frozen=True)
class EvaluationProfile:
    profile_id: str
    scenario_id: str
    configuration_id: str
    application_domain: str
    organizational_problem: str
    decision_objective: Mapping[str, str]
    constraints: str
    primary_metrics: tuple[str, ...]
    secondary_metrics: tuple[str, ...] = ()
    diagnostic_metrics: tuple[str, ...] = ()
    diagnostic_fields: tuple[str, ...] = ()
    information_regime: str = ""
    temporal_horizon: int = 0
    aggregation_rules: str = "one demanded problem per period"
    demand_distribution_id: str = ""
    metric_availability: Mapping[str, Status] = field(default_factory=dict)
    resource_units: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all((self.profile_id, self.scenario_id, self.configuration_id,
                    self.information_regime, self.demand_distribution_id,
                    self.aggregation_rules)):
            raise ValueError("profile, context, information, demand and aggregation IDs are required")
        if self.temporal_horizon < 1:
            raise ValueError("horizon must be positive")
        requested = self.metrics
        if len(requested) != len(set(requested)):
            raise ValueError("metric IDs must not be repeated")
        for metric in requested:
            if metric not in METRICS and not metric.startswith("resource_usage:"):
                raise ValueError(f"unknown metric: {metric}")
            if metric.startswith("resource_usage:") and metric.split(":", 1)[1] not in self.resource_units:
                raise ValueError(f"resource unit missing: {metric}")
        if any(key not in requested for key in self.metric_availability):
            raise ValueError("availability refers to an undeclared metric")
        if any(status is Status.VALID for status in self.metric_availability.values()):
            raise ValueError("VALID cannot be predeclared without a measured value")

    @property
    def metrics(self) -> tuple[str, ...]:
        return self.primary_metrics + self.secondary_metrics + self.diagnostic_metrics


@dataclass(frozen=True)
class EvaluationRecord:
    scenario_id: str
    configuration_id: str
    policy_id: str
    period: int
    demand: str | None = None
    output: tuple[float, ...] | None = None
    requirements: tuple[float, ...] | None = None
    success: bool | None = None
    deficit: tuple[float, ...] | None = None
    resource_usage: Mapping[str, float] | None = None
    original_reward: float | None = None
    ces: float | None = None
    available_metadata: Mapping[str, object] = field(default_factory=dict)
    provenance: str = ""
    unit_id: str | None = None
    task_type: str | None = None
    importance: float | None = None
    quality: float | None = None
    episode_id: str | None = None
    branch_probability: float | None = None
    information_regime: str | None = None
    decision_objective: str | None = None
    competence_state: object | None = None
    field_status: Mapping[str, Status] = field(default_factory=dict)
    teaching_action_count: int | None = None


@dataclass(frozen=True)
class EvaluationResult:
    scenario_id: str
    configuration_id: str
    policy_id: str
    metric_id: str
    definition_id: str
    value: float | None
    unit: str
    aggregation: str
    status: Status
    provenance: tuple[str, ...]
    temporal_horizon: int
    demand_distribution_id: str
    information_regime: str
    aggregation_context: str
    note: str = ""

    def __post_init__(self) -> None:
        if self.status is Status.VALID:
            if self.value is None or not isfinite(self.value):
                raise ValueError("VALID requires a finite value")
            if not self.provenance:
                raise ValueError("VALID requires provenance")
        elif self.value is not None:
            raise ValueError("unavailable/undefined results must not have a numeric value")


def _definition(profile: EvaluationProfile, metric: str,
                policy_id: str) -> tuple[str, str, str]:
    if metric.startswith("resource_usage:"):
        kind = metric.split(":", 1)[1]
        return (f"resource_usage:{kind}:v1", profile.resource_units[kind], "sum_periods")
    definition, unit, aggregation = METRICS[metric]
    if metric == "original_reward_cumulative":
        objective = profile.decision_objective.get(policy_id)
        if not objective:
            raise ValueError("original reward requires the policy's declared objective")
        return (f"{definition}:{objective}", unit, aggregation)
    return definition, unit, aggregation


class PerformanceEvaluator:
    """Small registry and pure aggregation API; it never invokes a policy."""

    def __init__(self) -> None:
        self._profiles: dict[str, EvaluationProfile] = {}

    def register_profile(self, profile: EvaluationProfile) -> None:
        if profile.profile_id in self._profiles:
            raise ValueError(f"duplicate profile: {profile.profile_id}")
        self._profiles[profile.profile_id] = profile

    def evaluate(self, profile_id: str, policy_id: str,
                 records: Sequence[EvaluationRecord]) -> dict[str, EvaluationResult]:
        profile = self._profiles[profile_id]
        if not records:
            raise ValueError("period records required; use import_historical for aggregates")
        if len(records) != profile.temporal_horizon or {r.period for r in records} != set(range(profile.temporal_horizon)):
            raise ValueError("records must cover each declared period exactly once")
        if any((r.scenario_id, r.configuration_id, r.policy_id) !=
               (profile.scenario_id, profile.configuration_id, policy_id) for r in records):
            raise ValueError("record context differs from profile or policy")
        if any(r.information_regime not in (None, profile.information_regime) for r in records):
            raise ValueError("record information regime differs from profile")
        expected_objective = profile.decision_objective.get(policy_id)
        if any(r.decision_objective not in (None, expected_objective) for r in records):
            raise ValueError("record decision objective differs from profile")
        episode_ids = {r.episode_id for r in records}
        if len(episode_ids) > 1:
            raise ValueError("evaluate accepts one episode; use evaluate_weighted_episodes")
        ordered = sorted(records, key=lambda r: r.period)
        provenance = tuple(r.provenance for r in ordered)
        if any(not item for item in provenance):
            raise ValueError("period records need provenance")
        result: dict[str, EvaluationResult] = {}
        for metric in profile.metrics:
            definition, unit, aggregation = _definition(profile, metric, policy_id)
            status = profile.metric_availability.get(metric)
            value: float | None = None
            note = "recomputed_from_period_records"
            if status is None:
                if metric == "functional_success_rate" and not any(
                        r.demand is not None for r in ordered):
                    status, note = Status.UNDEFINED, "zero demanded periods"
                rows = ([r for r in ordered if r.demand is not None]
                        if metric == "functional_success_rate" else ordered)
                values: list[float] = []
                missing_statuses: set[Status] = set()
                for row in rows if status is None else ():
                    raw: object
                    field_name = metric
                    if metric == "original_reward_cumulative":
                        raw = row.original_reward
                        field_name = "original_reward"
                    elif metric == "ces_cumulative":
                        raw = row.ces
                        field_name = "ces"
                    elif metric == "functional_success_rate":
                        raw = row.success
                        field_name = "success"
                    elif metric == "functional_deficit_cumulative":
                        raw = None if row.deficit is None else sum(row.deficit)
                        field_name = "deficit"
                    elif metric == "production_cumulative":
                        raw = None if row.output is None else sum(row.output)
                        field_name = "output"
                    elif metric == "teaching_actions_cumulative":
                        raw = row.teaching_action_count
                        field_name = "teaching_action_count"
                    else:
                        field_name = metric
                        raw = None if row.resource_usage is None else row.resource_usage.get(metric.split(":", 1)[1])
                    if raw is None:
                        missing_statuses.add(row.field_status.get(field_name, Status.NOT_RECORDED))
                        continue
                    number = float(raw)
                    if not isfinite(number):
                        raise ValueError("recorded metric components must be finite")
                    values.append(number)
                if status is None and missing_statuses:
                    status = (next(iter(missing_statuses)) if len(missing_statuses) == 1
                              else Status.NOT_RECORDED)
                    note = "missing field status declared by record" if len(missing_statuses) == 1 else "multiple missing-data states"
                if status is None:
                    if metric == "functional_success_rate":
                        value, status = sum(values) / len(rows), Status.VALID
                    else:
                        value, status = sum(values), Status.VALID
            result[metric] = EvaluationResult(
                profile.scenario_id, profile.configuration_id, policy_id,
                metric, definition, value, unit, aggregation, status,
                provenance, profile.temporal_horizon,
                profile.demand_distribution_id, profile.information_regime,
                profile.aggregation_rules, note,
            )
        return result

    def evaluate_weighted_episodes(
        self, profile_id: str, policy_id: str,
        episodes: Sequence[Sequence[EvaluationRecord]],
    ) -> dict[str, EvaluationResult]:
        """Aggregate exact episode results by declared branch probability."""
        if not episodes:
            raise ValueError("at least one episode is required")
        if any(not episode for episode in episodes):
            raise ValueError("episodes cannot be empty")
        weights = []
        episode_ids: set[str] = set()
        for episode in episodes:
            ids = {record.episode_id for record in episode}
            if len(ids) != 1 or None in ids or "" in ids:
                raise ValueError("each weighted episode needs one non-empty episode ID")
            episode_id = str(next(iter(ids)))
            if episode_id in episode_ids:
                raise ValueError("weighted episode IDs must be unique")
            episode_ids.add(episode_id)
            probabilities = {record.branch_probability for record in episode}
            if len(probabilities) != 1 or None in probabilities:
                raise ValueError("each episode needs one consistent branch probability")
            probability = float(next(iter(probabilities)))
            if probability < 0.0 or probability > 1.0:
                raise ValueError("branch probabilities must be in [0,1]")
            weights.append(probability)
        episode_results = [self.evaluate(profile_id, policy_id, episode) for episode in episodes]
        if not isclose(sum(weights), 1.0, rel_tol=0.0, abs_tol=1e-10):
            raise ValueError("episode branch probabilities must sum to one")
        output: dict[str, EvaluationResult] = {}
        profile = self._profiles[profile_id]
        for metric in profile.metrics:
            entries = [item[metric] for item in episode_results]
            statuses = {entry.status for entry in entries}
            if statuses == {Status.VALID}:
                value = sum(weight * entry.value for weight, entry in zip(weights, entries))
                status, note = Status.VALID, "exact_probability_weighted_episode_expectation"
            elif len(statuses) == 1:
                value, status, note = None, entries[0].status, entries[0].note
            else:
                value, status, note = None, Status.NOT_RECORDED, "metric availability differs across episodes"
            first = entries[0]
            output[metric] = EvaluationResult(
                first.scenario_id, first.configuration_id, policy_id,
                first.metric_id, first.definition_id, value, first.unit,
                "exact_branch_probability_expectation", status,
                tuple(source for entry in entries for source in entry.provenance),
                first.temporal_horizon, first.demand_distribution_id,
                first.information_regime,
                first.aggregation_context, note,
            )
        return output

    def import_historical(self, profile_id: str, policy_id: str, metric_id: str,
                          value: float, source_pointer: str,
                          *, note: str = "stored_historical_aggregate") -> EvaluationResult:
        """Label an existing aggregate, without implying trajectory reconstruction."""
        profile = self._profiles[profile_id]
        if metric_id not in profile.metrics or not source_pointer:
            raise ValueError("declared metric and source JSON pointer required")
        if metric_id in profile.metric_availability:
            raise ValueError("cannot import a metric declared unavailable")
        definition, unit, aggregation = _definition(profile, metric_id, policy_id)
        return EvaluationResult(
            profile.scenario_id, profile.configuration_id, policy_id,
            metric_id, definition, float(value), unit, aggregation, Status.VALID,
            (source_pointer,), profile.temporal_horizon,
            profile.demand_distribution_id, profile.information_regime,
            profile.aggregation_rules, note,
        )

    def unavailable(self, profile_id: str, policy_id: str, metric_id: str,
                    status: Status, reason: str, source_pointer: str) -> EvaluationResult:
        profile = self._profiles[profile_id]
        if metric_id not in profile.metrics or status is Status.VALID or not reason:
            raise ValueError("declared metric, non-VALID status and reason required")
        definition, unit, aggregation = _definition(profile, metric_id, policy_id)
        return EvaluationResult(
            profile.scenario_id, profile.configuration_id, policy_id,
            metric_id, definition, None, unit, aggregation, status,
            (source_pointer,), profile.temporal_horizon,
            profile.demand_distribution_id, profile.information_regime,
            profile.aggregation_rules, reason,
        )

    @staticmethod
    def compare(left: EvaluationResult, right: EvaluationResult, *,
                allow_information_inequality: bool = False) -> EvaluationResult:
        context_left = (left.scenario_id, left.configuration_id, left.metric_id,
                        left.definition_id, left.unit, left.aggregation,
                        left.temporal_horizon, left.demand_distribution_id,
                        left.aggregation_context)
        context_right = (right.scenario_id, right.configuration_id, right.metric_id,
                         right.definition_id, right.unit, right.aggregation,
                         right.temporal_horizon, right.demand_distribution_id,
                         right.aggregation_context)
        if context_left != context_right:
            raise ValueError("incompatible scenario, metric, horizon, or demand distribution")
        if left.status is not Status.VALID or right.status is not Status.VALID:
            raise ValueError("comparison requires two VALID metrics")
        unequal = left.information_regime != right.information_regime
        if unequal and not allow_information_inequality:
            raise ValueError("information regimes differ; explicit acknowledgement required")
        return EvaluationResult(
            left.scenario_id, left.configuration_id,
            f"{left.policy_id}-minus-{right.policy_id}",
            f"difference:{left.metric_id}", f"difference:{left.definition_id}",
            left.value - right.value, left.unit, "paired_policy_difference",
            Status.VALID, left.provenance + right.provenance,
            left.temporal_horizon, left.demand_distribution_id,
            "unequal_information" if unequal else left.information_regime,
            left.aggregation_context,
            "informationally_unequal" if unequal else "same_information_regime",
        )
