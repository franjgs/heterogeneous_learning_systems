"""Non-destructive common run envelope for existing HLS Laboratory routes.

This module describes executions and adapts existing results. It does not
execute a simulator, normalize mechanism-specific quantities, or imply that
the adapted routes are scientifically comparable.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, replace
from enum import Enum
from hashlib import sha256
import json
from math import isfinite
from typing import Any, Mapping, Sequence

from .contextual_router import RoutingRunResult, summarize_routing_run
from .hls_lab_nk_execution import (
    NKEnvironmentRunResult,
    NKInformationRunResult,
    NKLearningRunResult,
    NKProductionRunResult,
    NKTeachingRunResult,
    NKNembhardDirectRunResult,
)


SCHEMA_VERSION = "hls-experiment-run/1.0"
_HLS_RESULT_TYPES = (
    NKProductionRunResult, NKLearningRunResult, NKTeachingRunResult,
    NKInformationRunResult,
)


def _json_value(value: Any, path: str = "value") -> Any:
    """Copy supported data into JSON primitives and reject non-finite values."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError(f"{path} contains NaN or infinity")
        return value
    if isinstance(value, Enum):
        return _json_value(value.value, path)
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _json_value(getattr(value, field.name), f"{path}.{field.name}")
                for field in fields(value)}
    if isinstance(value, Mapping):
        if all(isinstance(key, str) for key in value):
            return {key: _json_value(item, f"{path}.{key}")
                    for key, item in value.items()}
        # Some environment process contracts use integer/enum/tuple states as
        # mapping keys. Preserve those keys as typed JSON values instead of
        # lossy stringification or unsupported JSON object keys.
        entries = [(_json_value(key, f"{path}.key"),
                    _json_value(item, f"{path}[{key!r}]")) for key, item in value.items()]
        entries.sort(key=lambda pair: json.dumps(pair[0], sort_keys=True, separators=(",", ":")))
        return {"__mapping_entries__": [[key, item] for key, item in entries]}
    if isinstance(value, (tuple, list)):
        return [_json_value(item, f"{path}[{index}]") for index, item in enumerate(value)]
    raise TypeError(f"{path} contains unsupported JSON value {type(value).__name__}")


@dataclass(frozen=True)
class SeedRecord:
    stream: str
    value: int
    purpose: str

    def __post_init__(self) -> None:
        for name in ("stream", "purpose"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.value, int) or isinstance(self.value, bool):
            raise ValueError("seed value must be an integer")


@dataclass(frozen=True)
class UnitDeclaration:
    quantity: str
    unit: str
    interpretation: str

    def __post_init__(self) -> None:
        for name in ("quantity", "unit", "interpretation"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")


@dataclass(frozen=True)
class MetricValue:
    name: str
    value: float | int | bool
    unit: str
    interpretation: str
    preferred_direction: str | None = None

    def __post_init__(self) -> None:
        for name in ("name", "unit", "interpretation"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.value, bool):
            pass
        elif isinstance(self.value, (int, float)) and isfinite(float(self.value)):
            pass
        else:
            raise ValueError("metric value must be a finite number or boolean")
        if self.preferred_direction not in {None, "higher", "lower"}:
            raise ValueError("preferred_direction must be higher, lower, or None")


@dataclass(frozen=True)
class ExperimentEvent:
    sequence_index: int
    event_type: str
    mechanism_id: str
    data: Mapping[str, Any]
    time_index: int | None = None

    def __post_init__(self) -> None:
        if (not isinstance(self.sequence_index, int) or isinstance(self.sequence_index, bool)
                or self.sequence_index < 0):
            raise ValueError("sequence_index must be a non-negative integer")
        if self.time_index is not None and (
            not isinstance(self.time_index, int) or isinstance(self.time_index, bool)
            or self.time_index < 0
        ):
            raise ValueError("time_index must be a non-negative integer or None")
        for name in ("event_type", "mechanism_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        payload = _json_value(self.data, "event.data")
        if not isinstance(payload, dict):
            raise TypeError("event.data must be a JSON object")
        object.__setattr__(self, "data", payload)


@dataclass(frozen=True)
class RunAdapterContext:
    """Caller-supplied provenance absent from legacy run result objects.

    A ``None`` mapping means not recorded/unknown, while an empty mapping is
    an explicitly supplied empty snapshot. ``random_seeds=None`` means seed
    provenance is incomplete or unavailable; an empty tuple means the caller
    confirms no stochastic stream was used.
    """

    run_id: str | None = None
    configuration: Mapping[str, Any] | None = None
    initial_conditions: Mapping[str, Any] | None = None
    random_seeds: tuple[SeedRecord, ...] | None = None
    information_available: Mapping[str, Any] | None = None
    observation_model: Mapping[str, Any] | None = None
    software_revision: str | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class ExperimentRun:
    schema_version: str
    run_id: str
    mechanism_id: str
    policy_id: str | None
    configuration: Mapping[str, Any] | None
    initial_conditions: Mapping[str, Any] | None
    random_seeds: tuple[SeedRecord, ...] | None
    information_available: Mapping[str, Any] | None
    observation_model: Mapping[str, Any] | None
    software_revision: str | None
    units: tuple[UnitDeclaration, ...]
    events: tuple[ExperimentEvent, ...]
    metrics: tuple[MetricValue, ...]
    mechanism_results: Any
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in ("schema_version", "run_id", "mechanism_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.policy_id is not None and not isinstance(self.policy_id, str):
            raise TypeError("policy_id must be a string or None")
        for name in ("configuration", "initial_conditions", "information_available",
                     "observation_model", "metadata"):
            value = getattr(self, name)
            if value is not None:
                copied = _json_value(value, name)
                if not isinstance(copied, dict):
                    raise TypeError(f"{name} must be a JSON object or None")
                object.__setattr__(self, name, copied)
        if self.software_revision is not None and not isinstance(self.software_revision, str):
            raise TypeError("software_revision must be a string or None")
        if self.random_seeds is not None:
            seeds = tuple(self.random_seeds)
            if any(not isinstance(seed, SeedRecord) for seed in seeds):
                raise TypeError("random_seeds must contain SeedRecord values")
            if len({seed.stream for seed in seeds}) != len(seeds):
                raise ValueError("random seed stream names must be unique")
            object.__setattr__(self, "random_seeds", seeds)
        object.__setattr__(self, "units", tuple(self.units))
        object.__setattr__(self, "events", tuple(self.events))
        object.__setattr__(self, "metrics", tuple(self.metrics))
        if any(not isinstance(item, UnitDeclaration) for item in self.units):
            raise TypeError("units must contain UnitDeclaration values")
        if any(not isinstance(item, ExperimentEvent) for item in self.events):
            raise TypeError("events must contain ExperimentEvent values")
        if any(not isinstance(item, MetricValue) for item in self.metrics):
            raise TypeError("metrics must contain MetricValue values")

    def to_dict(self) -> dict[str, Any]:
        return _json_value(self, "experiment_run")

    def to_json(self) -> str:
        """Stable canonical JSON; non-finite or unsupported values fail closed."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False)


def _digest_id(result: Any, prefix: str) -> str:
    payload = json.dumps(_json_value(result, "source_result"), sort_keys=True,
                         separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return f"{prefix}-{sha256(payload.encode('utf-8')).hexdigest()[:16]}"


def _ctx_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any] | None:
    return None if value is None else _json_value(value)


def _event_builder(mechanism_id: str):
    events: list[ExperimentEvent] = []

    def add(time_index: int | None, event_type: str, **data: Any) -> None:
        events.append(ExperimentEvent(len(events), event_type, mechanism_id, data, time_index))

    return events, add


def _matrix_nonzero(matrix: Any) -> bool:
    return any(value is not None and float(value) != 0.0
               for row in matrix for value in row)


def _base_metrics(records: Sequence[Any], effort_unit: str, output_unit: str,
                  dimension_ids: Sequence[str] | None = None) -> tuple[MetricValue, ...]:
    if not records:
        return ()
    success = sum(bool(record.functional_result.success) for record in records) / len(records)
    metrics = [
        MetricValue("functional_success_rate", success, "fraction",
                    "Fraction of recorded periods meeting all active requirements.", "higher"),
        MetricValue("gross_ces_mean", sum(record.ces_reward for record in records) / len(records),
                    f"{output_unit} (CES scale)", "Mean gross CES over recorded periods; not net utility.", "higher"),
        MetricValue("productive_effort_total", sum(record.productive_effort_used for record in records),
                    effort_unit, "Sum of productive effort consumed; not monetary cost.", "lower"),
    ]
    skill_ids = getattr(records[0], "skill_ids", None)
    for skill_index in range(len(records[0].outputs)):
        labels = skill_ids if skill_ids is not None else dimension_ids
        skill_label = str(skill_index) if labels is None else str(labels[skill_index])
        metrics.append(MetricValue(
            f"production_total[{skill_label}]",
            sum(record.outputs[skill_index] for record in records), output_unit,
            "Total model output for this competence/problem dimension.", None,
        ))
    return tuple(metrics)


def _derive_nk_initial(result: Any) -> Mapping[str, Any] | None:
    records = getattr(result, "records", ())
    if not records:
        return None
    record = records[0]
    production = getattr(record, "production", record)
    if hasattr(record, "competence_actual_before"):
        return {"competence_actual": record.competence_actual_before,
                "competence_estimated": record.competence_estimated_before}
    if hasattr(production, "competence_before"):
        return {"competence_actual_and_estimated": production.competence_before,
                "source": "first recorded pre-decision state"}
    return None


def _adapt_nk(result: Any, context: RunAdapterContext,
              environment: NKEnvironmentRunResult | None = None) -> ExperimentRun:
    if isinstance(result, NKInformationRunResult):
        mechanism_id = "mis_v2"
        policy_id = result.records[0].policy_name if result.records else None
        records = result.records
        information = context.information_available
        if information is None:
            information = {"mode": result.information_mode,
                           "policy_view": "estimated_competence; actual competence retained for execution diagnostics"}
        observation_model = context.observation_model
        if observation_model is None and result.information_mode == "imperfect":
            observation_model = {"status": "not captured in run result; supply through RunAdapterContext"}
    elif isinstance(result, NKTeachingRunResult):
        mechanism_id = "mis_v2"
        policy_id = result.records[0].policy_name if result.records else None
        records = result.records
        information = context.information_available or {"mode": "perfect"}
        observation_model = context.observation_model
    elif isinstance(result, NKLearningRunResult):
        mechanism_id = "mis_v2"
        policy_id = "p0"
        records = result.records
        information = context.information_available or {"mode": "perfect"}
        observation_model = context.observation_model
    elif isinstance(result, NKProductionRunResult):
        mechanism_id = "mis_v2"
        policy_id = "p0"
        records = result.records
        information = context.information_available or {"mode": "perfect"}
        observation_model = context.observation_model
    else:
        raise TypeError("unsupported HLS N×K result type")

    raw_result = _json_value(result, "mechanism_results")
    if environment is not None:
        raw_result = {"execution": raw_result,
                      "environment_trajectory": _json_value(environment.trajectory,
                                                             "environment_trajectory")}
    events, add = _event_builder(mechanism_id)
    if environment is not None:
        add(None, "environment_frozen", seed=environment.trajectory.seed,
            latent_states=environment.trajectory.latent_states,
            regime_labels=environment.trajectory.regime_labels,
            problems=environment.trajectory.problems)
    production_records = []
    for index, record in enumerate(records):
        info_record = record if hasattr(record, "competence_actual_before") else None
        policy_name = getattr(record, "policy_name", policy_id)
        if hasattr(record, "production"):
            production = record.production
        else:
            production = record
        production_records.append(production)
        decision_data = {
            "policy_id": policy_name,
            "action_id": getattr(production, "action_id", getattr(record, "action_id", None)),
            "joint_action_id": getattr(record, "joint_action_id", None),
            "allocation": getattr(record, "action", getattr(production, "allocation", None)),
            "teaching_action": (getattr(record, "teaching_action", None)
                                or (record.action.teaching if hasattr(record, "action") else None)),
        }
        if info_record is not None:
            decision_data["estimated_competence_used"] = info_record.competence_estimated_before
        add(index, "decision", **decision_data)
        add(index, "execution", problem_id=production.problem_id,
            requirements=production.requirements, outputs=production.outputs,
            individual_outputs=production.individual_outputs,
            functional_result=production.functional_result, gross_ces=production.ces_reward,
            productive_effort_used=production.productive_effort_used,
            teaching_resource_used=getattr(record, "teaching_resource_used", 0.0),
            total_resource_used=getattr(record, "total_resource_used", production.productive_effort_used),
            unused_collective_capacity=getattr(record, "unused_collective_capacity",
                                               production.unused_collective_capacity))
        if info_record is not None:
            if any(value is not None for row in info_record.production_observations for value in row):
                add(index, "observation", observation_kind="production_by_agent_skill",
                    values=info_record.production_observations,
                    available_to_decision=(result.information_mode == "imperfect"),
                    used_for_estimation=(result.information_mode == "imperfect"))
        if hasattr(record, "competence_increment") and hasattr(record, "learning_eta"):
            add(index, "state_update", update_kind="mis_v2_competence",
                competence_increment=record.competence_increment,
                learning_eta=record.learning_eta,
                competence_before=production.competence_before,
                competence_after=production.competence_after)
        if hasattr(record, "mis_increment"):
            if _matrix_nonzero(record.mis_increment):
                add(index, "state_update", update_kind="mis_v2_competence",
                    competence_increment=record.mis_increment,
                    competence_after_mis=record.competence_after_mis)
            teaching_observation = getattr(record, "teaching_observation", None)
            if teaching_observation is None:
                teaching_observation = getattr(record, "formative_efficacy_observation", None)
            if teaching_observation is not None:
                add(index, "observation", observation_kind="formative_teaching_efficacy",
                    value=teaching_observation, used_for_policy_memory=True)
            teaching_increment = (record.teaching_increment if hasattr(record, "teaching_increment")
                                  else record.competence_increment_from_teaching)
            teaching_action = getattr(record, "teaching_action", None)
            if teaching_action is None and hasattr(record, "action"):
                teaching_action = record.action.teaching
            if teaching_action is not None:
                add(index, "state_update", update_kind="directed_teaching",
                    teaching_action=teaching_action,
                    competence_increment=teaching_increment,
                    competence_actual_after=(record.competence_actual_after
                                             if hasattr(record, "competence_actual_after")
                                             else record.competence_after_mis))
            if record.efficacy_memory_before != record.efficacy_memory_after:
                add(index, "policy_memory_update",
                    memory_before=record.efficacy_memory_before,
                    memory_after=record.efficacy_memory_after)
        if info_record is not None and result.information_mode == "imperfect":
            add(index, "estimator_update", timing="post-period recorded estimate; source trace does not expose intermediate posterior states",
                estimated_before=info_record.competence_estimated_before,
                estimated_after=info_record.competence_estimated_after,
                variance_before=info_record.competence_variance_before,
                variance_after=info_record.competence_variance_after,
                estimation_error=info_record.estimation_error,
                efficacy_memory_before=info_record.efficacy_memory_before,
                efficacy_memory_after=info_record.efficacy_memory_after)

    success_records = production_records
    if not success_records and records:
        success_records = [getattr(record, "production", record) for record in records]
    metrics = _base_metrics(success_records, "HLS effort units (source unit unspecified)",
                            "model output units (not declared by ProblemSpecNK)")
    if isinstance(result, NKLearningRunResult):
        for agent_index, row in enumerate(result.final_state.competence_real):
            for skill_index, value in enumerate(row):
                metrics += (MetricValue(f"final_competence[{agent_index},{skill_index}]", value,
                                        "normalized competence [0,1]",
                                        "Final actual competence cell; mechanism state, not performance.", None),)
    if isinstance(result, NKInformationRunResult) and result.records:
        metrics += (MetricValue("mean_absolute_estimation_error",
                                sum(abs(value) for row in result.records[-1].estimation_error
                                    for value in row) /
                                max(1, sum(len(row) for row in result.records[-1].estimation_error)),
                                "normalized competence [0,1]",
                                "Mean absolute actual-estimated difference in final recorded period.", "lower"),)

    seeds = context.random_seeds
    if seeds is None and environment is not None:
        seeds = (SeedRecord("environment", environment.trajectory.seed,
                            "exogenous demand generation"),)
    elif seeds is None and not isinstance(result, NKInformationRunResult):
        # The non-information N×K paths are deterministic given their inputs.
        seeds = ()
    configuration = _ctx_mapping(context.configuration)
    initial = _ctx_mapping(context.initial_conditions)
    if initial is None:
        initial = _derive_nk_initial(result)
    metadata = dict(context.metadata or {})
    metadata.update({"source_result_type": type(result).__name__,
                     "configuration_status": "caller-supplied" if configuration is not None else "not captured by source result",
                     "initial_conditions_status": "caller-supplied or derived from first record" if initial is not None else "not captured",
                     "seed_status": "caller-supplied" if context.random_seeds is not None else
                     ("partial: information seed is not retained by source result" if isinstance(result, NKInformationRunResult) and environment is not None else
                      "not captured by source result" if isinstance(result, NKInformationRunResult) else
                      "environment seed captured" if environment is not None else "no stochastic stream in this deterministic route")})
    if environment is not None:
        metadata["environment_config"] = _json_value(environment.trajectory.config, "environment_config")
    units = (
        UnitDeclaration("productive_effort", "HLS effort units (source unit unspecified)",
                        "Resource intensity reported by the existing N×K trace; not currency."),
        UnitDeclaration("gross_ces", "model output units (unit not declared by ProblemSpecNK)",
                        "Existing gross CES scale; not net utility."),
    )
    return ExperimentRun(
        SCHEMA_VERSION, context.run_id or _digest_id(result, "hls-nk"), mechanism_id,
        policy_id, configuration, initial, seeds, _ctx_mapping(information),
        _ctx_mapping(observation_model), context.software_revision, units,
        tuple(events), metrics, raw_result, metadata,
    )


def adapt_hls_nk_run(result: Any, *, context: RunAdapterContext = RunAdapterContext()) -> ExperimentRun:
    """Adapt HLS MIS-v2/N×K output without changing its native serializer."""
    if isinstance(result, NKEnvironmentRunResult):
        if context.run_id is None:
            context = replace(context, run_id=_digest_id(result, "hls-nk"))
        if isinstance(result.execution, NKNembhardDirectRunResult):
            return adapt_nembhard_run(result.execution, context=context, environment=result)
        return _adapt_nk(result.execution, context, environment=result)
    return _adapt_nk(result, context)


def adapt_nembhard_run(
    result: NKNembhardDirectRunResult, *,
    context: RunAdapterContext = RunAdapterContext(),
    environment: NKEnvironmentRunResult | None = None,
) -> ExperimentRun:
    """Adapt Nembhard Direct, retaining its state, router diagnostics and units."""
    if not isinstance(result, NKNembhardDirectRunResult):
        raise TypeError("result must be NKNembhardDirectRunResult")
    mechanism_id = result.mechanism_id
    policy_id = result.router_id or "explicit_allocations"
    events, add = _event_builder(mechanism_id)
    if environment is not None:
        add(None, "environment_frozen", seed=environment.trajectory.seed,
            latent_states=environment.trajectory.latent_states,
            regime_labels=environment.trajectory.regime_labels,
            problems=environment.trajectory.problems)
    for index, record in enumerate(result.records):
        add(index, "decision", policy_id=policy_id, allocation=record.allocation,
            catalog_action_id=record.router_action_id,
            candidate_count=record.router_candidate_count,
            predicted_outputs=record.router_predicted_outputs,
            predicted_rank=record.router_rank, exploratory=record.router_exploratory,
            observable_experience=record.router_observable_experience)
        add(index, "execution", problem_id=record.problem_id,
            requirements=record.requirements, outputs=record.outputs,
            individual_outputs=record.individual_outputs,
            functional_result=record.functional_result, gross_ces=record.ces_reward,
            effort_used=record.productive_effort_used,
            effective_work_used=record.effective_work_used,
            unused_collective_capacity=record.unused_collective_capacity,
            productivity_before=record.productivity_before)
        add(index, "state_update", update_kind="nembhard_direct_experience",
            experience_before=record.experience_before,
            increment=record.experience_increment,
            experience_after=record.experience_after)
        if record.adaptive_observations is not None and any(
            value is not None for row in record.adaptive_observations for value in row
        ):
            add(index, "observation", observation_kind="individual_agent_skill_output",
                values=record.adaptive_observations)
        if record.adaptive_estimator_before is not None:
            add(index, "estimator_update", estimator_before=record.adaptive_estimator_before,
                estimator_after=record.adaptive_estimator_after)
    metrics = list(_base_metrics(result.records, result.effort_intensity_unit,
                                 result.output_unit, result.skill_ids))
    for skill_index, skill_id in enumerate(result.skill_ids):
        metrics.append(MetricValue(
            f"experience_final_total[{skill_id}]",
            sum(row[skill_index] for row in result.final_experience), result.exposure_unit,
            "Sum of direct experience across agents for this skill; not effort or competence.", None))
    seeds = context.random_seeds
    if seeds is None:
        known: list[SeedRecord] = []
        if result.adaptive_router_config is not None:
            known.extend((
                SeedRecord("nembhard_observation", result.adaptive_router_config.observation_seed,
                           "individual productivity observation noise"),
                SeedRecord("nembhard_exploration", result.adaptive_router_config.exploration_seed,
                           "epsilon-greedy allocation exploration"),
            ))
        if environment is not None:
            known.append(SeedRecord("environment", environment.trajectory.seed,
                                    "exogenous demand generation"))
        seeds = tuple(known) if (known or result.router_id == "nembhard_oracle" or result.router_id is None) else None
    configuration = _ctx_mapping(context.configuration)
    if configuration is None:
        configuration = {
            "profile_k": result.profile_k, "profile_p": result.profile_p,
            "profile_r": result.profile_r, "period_duration": (result.records[0].duration if result.records else None),
            "adaptive_router_config": result.adaptive_router_config,
            "effort_intensity_unit": result.effort_intensity_unit,
            "duration_unit": result.duration_unit,
            "exposure_unit": result.exposure_unit,
            "output_unit": result.output_unit,
            "requirement_unit": result.requirement_unit,
        }
    initial = _ctx_mapping(context.initial_conditions) or {
        "agent_ids": result.agent_ids, "skill_ids": result.skill_ids,
        "experience": result.initial_experience,
    }
    info = context.information_available
    if info is None:
        info = {"decision_state": "true experience/profile for ORACLE; estimated productivity and reconstructed episode exposure for ADAPTIVE; none for explicit allocation"}
    observation = context.observation_model
    if observation is None and result.adaptive_router_config is not None:
        observation = {"kind": "individual agent-skill output",
                       "noise_stddev": result.adaptive_router_config.observation_noise_stddev,
                       "minimum_observation_work": result.adaptive_router_config.minimum_observation_work}
    metadata = dict(context.metadata or {})
    metadata.update({"source_result_type": type(result).__name__,
                     "configuration_status": "derived from source result" if context.configuration is None else "caller-supplied",
                     "seed_status": "caller-supplied" if context.random_seeds is not None else "captured streams may be incomplete"})
    if environment is not None:
        metadata["environment_config"] = _json_value(environment.trajectory.config, "environment_config")
    units = (
        UnitDeclaration("productive_effort", result.effort_intensity_unit,
                        "Per-period effort intensity; resource cap, not currency."),
        UnitDeclaration("duration", result.duration_unit, "Period duration under the Nembhard adaptation."),
        UnitDeclaration("direct_experience", result.exposure_unit, "Accumulated D state; distinct from HLS competence."),
        UnitDeclaration("production_output", result.output_unit, "Nembhard Direct output unit under explicit calibration."),
        UnitDeclaration("problem_requirement", result.requirement_unit, "Requirement unit matched by the declared output contract."),
    )
    return ExperimentRun(SCHEMA_VERSION, context.run_id or _digest_id(result, "nembhard"),
                         mechanism_id, policy_id, configuration, initial, seeds,
                         _ctx_mapping(info), _ctx_mapping(observation), context.software_revision,
                         units, tuple(events), tuple(metrics), _json_value(result), metadata)


def adapt_contextual_run(
    result: RoutingRunResult, *, context: RunAdapterContext = RunAdapterContext()
) -> ExperimentRun:
    """Adapt contextual query routing, keeping quality and cost separate."""
    if not isinstance(result, RoutingRunResult):
        raise TypeError("result must be RoutingRunResult")
    mechanism_id = "contextual_quality_cost_hls_v0.1"
    events, add = _event_builder(mechanism_id)
    for index, trace in enumerate(result.traces):
        add(index, "decision", policy_id="contextual_quality_cost_router",
            query=trace.query, selected_candidate_id=trace.decision.selected_candidate_id,
            reason=trace.decision.reason, exploratory=trace.decision.exploratory,
            predictions=trace.decision.forecasts,
            router_state_version_before=trace.decision.state_version_before)
        if trace.outcome is not None:
            add(index, "execution", candidate_id=trace.outcome.candidate_id,
                status=trace.outcome.status,
                diagnostic_metadata=trace.outcome.diagnostic_metadata)
            if trace.outcome.observed_quality is not None or trace.outcome.observed_cost is not None:
                add(index, "observation", observed_quality=trace.outcome.observed_quality,
                    observed_cost=trace.outcome.observed_cost,
                    quality_meets_target=trace.observed_quality_meets_target,
                    predicted_budget_compliant=trace.predicted_budget_compliant,
                    actual_budget_compliant=trace.actual_budget_compliant)
        if trace.update is not None:
            add(index, "estimator_update", receipt=trace.update)
    summary = summarize_routing_run(result)
    metrics: list[MetricValue] = [
        MetricValue("queries_executed", summary["executed"], "queries",
                    "Number of selected candidate executions.", None),
    ]
    for name, unit, meaning, direction in (
        ("mean_observed_quality", "quality [0,1]", "Mean available observed quality under the configured evaluator.", "higher"),
        ("mean_observed_cost", result.currency, "Mean available observed monetary cost per query.", "lower"),
        ("quality_target_rate", "fraction", "Fraction of executions with observed quality meeting query target.", "higher"),
        ("predicted_budget_compliance_rate", "fraction", "Fraction within predicted-cost budget; not a spend guarantee.", "higher"),
        ("actual_budget_compliance_rate", "fraction", "Fraction within observed-cost budget.", "higher"),
    ):
        value = summary[name]
        if value is not None:
            metrics.append(MetricValue(name, value, unit, meaning, direction))
    q_errors: list[float] = []
    c_errors: list[float] = []
    for trace in result.traces:
        if trace.outcome is None:
            continue
        forecast = next((item for item in trace.decision.forecasts
                         if item.candidate_id == trace.outcome.candidate_id), None)
        if forecast is None:
            continue
        if trace.outcome.observed_quality is not None:
            q_errors.append(abs(forecast.predicted_quality - trace.outcome.observed_quality))
        if trace.outcome.observed_cost is not None:
            c_errors.append(abs(forecast.predicted_cost - trace.outcome.observed_cost))
    if q_errors:
        metrics.append(MetricValue("mean_absolute_quality_prediction_error",
                                   sum(q_errors) / len(q_errors), "quality [0,1]",
                                   "Descriptive absolute error on selected executed candidates only.", "lower"))
    if c_errors:
        metrics.append(MetricValue("mean_absolute_cost_prediction_error",
                                   sum(c_errors) / len(c_errors), result.currency,
                                   "Descriptive absolute error on selected executed candidates only.", "lower"))
    seeds = context.random_seeds
    if seeds is None:
        known = [SeedRecord("contextual_exploration", result.exploration_seed,
                            "epsilon-greedy candidate exploration")]
        executor_seed = dict(result.executor_replay_metadata).get("executor_seed")
        if executor_seed is not None:
            try:
                known.append(SeedRecord("contextual_executor", int(executor_seed),
                                        "synthetic query outcome/noise streams"))
            except (TypeError, ValueError):
                pass
        seeds = tuple(known)
    config = _ctx_mapping(context.configuration) or {
        "context_dimension": result.context_dimension,
        "include_intercept": result.include_intercept,
        "quality_regularization": result.quality_regularization,
        "cost_regularization": result.cost_regularization,
        "epsilon": result.epsilon,
        "currency": result.currency,
        "evaluator_version": result.evaluator_version,
        "accounting_version": result.accounting_version,
        "candidates": result.candidates,
        "initial_priors": result.initial_priors,
    }
    metadata = dict(context.metadata or {})
    metadata.update({"source_result_type": type(result).__name__,
                     "executor_replay_metadata": result.executor_replay_metadata,
                     "seed_status": "captured from router and executor replay metadata where exposed"})
    units = (
        UnitDeclaration("quality", "quality [0,1]",
                        f"Outcome under evaluator version {result.evaluator_version}; not CES."),
        UnitDeclaration("monetary_cost", result.currency,
                        f"Per-query monetary cost under accounting version {result.accounting_version}."),
    )
    return ExperimentRun(SCHEMA_VERSION, context.run_id or result.run_id, mechanism_id,
                         "contextual_quality_cost_router", config,
                         (_ctx_mapping(context.initial_conditions) if context.initial_conditions is not None
                          else {"predictor_initial_priors": result.initial_priors}), seeds,
                         _ctx_mapping(context.information_available) or {
                             "router_receives": "query context, eligibility, priors, and feedback from selected candidate only",
                             "environment_truth": "not exposed to router",
                         },
                         _ctx_mapping(context.observation_model) or {
                             "status": "executor outcome observation model not fully represented in RoutingRunResult; see executor metadata"
                         }, context.software_revision, units, tuple(events), tuple(metrics),
                         _json_value(result), metadata)


def adapt_experiment_run(result: Any, *, context: RunAdapterContext = RunAdapterContext()) -> ExperimentRun:
    """Dispatch to one of the three implemented, non-destructive adapters."""
    if isinstance(result, NKEnvironmentRunResult):
        return adapt_hls_nk_run(result, context=context)
    if isinstance(result, _HLS_RESULT_TYPES):
        return adapt_hls_nk_run(result, context=context)
    if isinstance(result, NKNembhardDirectRunResult):
        return adapt_nembhard_run(result, context=context)
    if isinstance(result, RoutingRunResult):
        return adapt_contextual_run(result, context=context)
    raise TypeError(f"unsupported result type for common experiment contract: {type(result).__name__}")
