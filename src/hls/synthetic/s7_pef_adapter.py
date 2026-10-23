"""Convert S7 policy replays to generic HLS-PEF period records.

The adapter is downstream of policy selection: it only transforms an already
replayed action/state trajectory into evaluation observations.
"""

from __future__ import annotations

from typing import Mapping, Sequence

from hls.experiment_contract import (
    ExperimentEvent,
    ExperimentRun,
    MetricValue,
    UnitDeclaration,
)
from hls.hls_lab_nk_production import evaluate_problem_nk, productive_outputs_nk
from hls.performance_evaluation import EvaluationRecord, Status
from hls.synthetic.hls_s7_uncertain_demand import S7MarkovDemandCase


def adapt_s7_episode(
    case: S7MarkovDemandCase,
    policy_id: str,
    episode_id: str,
    demand_path: Sequence[int],
    branch_probability: float,
    replay_rows: Sequence[dict],
    *,
    information_regime: str,
    decision_objective: str = "CES",
    provenance_prefix: str = "s7_pilot",
) -> tuple[EvaluationRecord, ...]:
    """Map one existing S7 replay to generic records; do not choose actions."""
    if len(demand_path) != case.horizon or len(replay_rows) != case.horizon:
        raise ValueError("demand path and replay must match the declared horizon")
    if not 0.0 <= branch_probability <= 1.0:
        raise ValueError("branch probability must be in [0,1]")
    branch = "-".join(case.demand_states[index].problem_id for index in demand_path)
    rows: list[EvaluationRecord] = []
    for period, (demand_index, replay) in enumerate(zip(demand_path, replay_rows)):
        problem = case.demand_states[demand_index]
        if replay["period"] != period or replay["demand_state"] != demand_index:
            raise ValueError("replay period or demand state differs from requested branch")
        action = replay["action"]
        outputs = productive_outputs_nk(replay["competence_before"], action.production)
        functional = evaluate_problem_nk(outputs, problem.requirements)
        teaching = action.teaching
        teaching_cost = 0.0 if teaching is None else 2.0 * teaching.effort
        production_effort = sum(sum(row) for row in action.production)
        resource_usage = {
            "productive_effort": production_effort,
            "teaching_effort": 0.0 if teaching is None else teaching.effort,
            "teaching_resource": teaching_cost,
            "total_effort": production_effort + teaching_cost,
        }
        rows.append(EvaluationRecord(
            scenario_id="S7", configuration_id="opportunity_T4_C5",
            policy_id=policy_id, period=period,
            unit_id=f"{problem.problem_id}:period-{period}",
            demand=problem.problem_id, task_type=problem.problem_id,
            importance=None, output=tuple(outputs), quality=None,
            requirements=tuple(problem.requirements), success=functional.success,
            deficit=tuple(functional.deficits), resource_usage=resource_usage,
            original_reward=float(replay["reward"]), ces=float(replay["reward"]),
            episode_id=branch, branch_probability=branch_probability,
            information_regime=information_regime,
            decision_objective=decision_objective,
            competence_state={"before": replay["competence_before"],
                              "after": replay["competence_after"]},
            field_status={"importance": Status.NOT_APPLICABLE,
                          "quality": Status.NOT_APPLICABLE},
            teaching_action_count=int(teaching is not None),
            available_metadata={
                "action": {"production": action.production,
                           "teaching": None if teaching is None else {
                               "teacher_id": teaching.teacher_id,
                               "learner_id": teaching.learner_id,
                               "skill_id": teaching.skill_id,
                               "effort": teaching.effort,
                           }},
                "observed_demand_state": demand_index,
                "requirements_from_s7_problem_spec": True,
            },
            provenance=f"{provenance_prefix}#/episodes/{branch}/periods/{period}",
        ))
    return tuple(rows)


def adapt_s7_pilot_artifact_to_experiment_run(
    artifact: Mapping,
    policy_id: str,
    *,
    source_pointer: str = "results/experiments/hls_pef_s7_pilot/results.json",
) -> ExperimentRun:
    """Wrap an existing S7 PEF pilot result in the common run envelope.

    This is a downstream structural adapter: it neither reruns S7 nor
    changes policy decisions. The pilot historically emitted PEF records but
    not ``ExperimentRun``; this adapter makes that gap explicit and reusable.
    """
    required = {"experiment", "configuration", "profile", "policies",
                "branch_records", "exact_solver_values_CES", "branch_probability_sum"}
    missing = required - set(artifact)
    if missing:
        raise ValueError(f"incomplete S7 PEF artifact; missing {sorted(missing)}")
    if policy_id not in artifact["policies"] or policy_id not in artifact["branch_records"]:
        raise ValueError(f"S7 artifact does not contain policy {policy_id!r}")
    if not source_pointer:
        raise ValueError("source pointer is required")

    branches = artifact["branch_records"][policy_id]
    branch_probability_sum = sum(float(branch["probability"]) for branch in branches)
    if abs(branch_probability_sum - 1.0) > 1e-10:
        raise ValueError("S7 artifact branch probabilities do not sum to one")
    profile = artifact["profile"]
    policy_metrics = artifact["policies"][policy_id]
    events: list[ExperimentEvent] = []
    for branch in branches:
        if len(branch["period_records"]) != int(profile["temporal_horizon"]):
            raise ValueError("S7 branch period count differs from profile horizon")
        for row in branch["period_records"]:
            events.append(ExperimentEvent(
                sequence_index=len(events),
                event_type="branch_period_evaluation",
                mechanism_id="s7_exact_policy_replay",
                data={
                    "episode_id": branch["episode_id"],
                    "branch_probability": float(branch["probability"]),
                    "demand_path": branch["demand_path"],
                    "period_record": row,
                },
                time_index=int(row["period"]),
            ))

    metric_values: list[MetricValue] = []
    units: dict[tuple[str, str], UnitDeclaration] = {}
    for metric_id, metric in policy_metrics.items():
        metric_status = metric.get("status")
        if metric_status == Status.VALID.value and metric.get("value") is not None:
            unit = str(metric["unit"])
            value = metric["value"]
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                metric_values.append(MetricValue(
                    metric_id, value, unit,
                    f"S7 HLS-PEF result using {metric['definition_id']}; {metric['aggregation']}.",
                ))
                units[(metric_id, unit)] = UnitDeclaration(
                    metric_id, unit, f"Unit recorded in the source S7 PEF result for {metric_id}."
                )

    return ExperimentRun(
        schema_version="hls-experiment-run/1.0",
        run_id=f"s7-pef-pilot-v1-{policy_id}",
        mechanism_id="s7_exact_policy_replay",
        policy_id=policy_id,
        configuration={
            "scenario_id": profile["scenario_id"],
            "scenario_configuration_id": profile["configuration_id"],
            "organizational_problem_id": profile["organizational_problem"],
            "configuration": artifact["configuration"],
            "temporal_horizon": profile["temporal_horizon"],
        },
        initial_conditions={
            "source": "S7 pilot configuration stored in artifact",
            "initial_demand_distribution": artifact["configuration"].get("initial_probabilities"),
            "initial_competence": artifact["configuration"].get("initial_competence"),
        },
        random_seeds=(),
        information_available={"declared_policy_regime": profile["information_regime"]},
        observation_model={
            "kind": "complete demand tree with exact branch probabilities",
            "demand_distribution_id": profile["demand_distribution_id"],
            "branch_count": len(branches),
        },
        software_revision=None,
        units=tuple(units.values()),
        events=tuple(events),
        metrics=tuple(metric_values),
        mechanism_results={
            "exact_solver_value_CES": artifact["exact_solver_values_CES"][policy_id],
            "branch_probability_sum": branch_probability_sum,
            "pef_metric_status": {key: value.get("status") for key, value in policy_metrics.items()},
            "source_artifact": source_pointer,
        },
        metadata={
            "evaluation_profile_id": profile["profile_id"],
            "organizational_problem_id": profile["organizational_problem"],
            "policy_role": "exact_policy_replay",
            "source_artifact": source_pointer,
            "source_execution": artifact["execution"],
            "conversion_scope": "existing PEF pilot records only; no S7 rerun",
        },
    )
