"""Non-intrusive adapter from the existing deterministic S2a runner to HLS-PEF."""

from __future__ import annotations

from typing import Any, Mapping

from hls.experiment_contract import (
    ExperimentEvent,
    ExperimentRun,
    MetricValue,
    RunAdapterContext,
    UnitDeclaration,
)
from hls.performance_evaluation import EvaluationProfile, EvaluationRecord, Status


SCENARIO_ID = "S2a"
CONFIGURATION_ID = "s2a_static_demand_3x3_v1"
PROFILE_ID = "s2a_assignment_reward_v1"
ORGANIZATIONAL_PROBLEM_ID = "B2_optional_one_to_one_assignment_capacity_3"
OBJECTIVE_ID = "sum_assigned_competence_scores"
POLICY_IDS = ("exact", "greedy")


def s2a_evaluation_profile() -> EvaluationProfile:
    """Declare only metrics supported by S2a's actual semantics and PEF."""
    unavailable = {
        "ces_cumulative": Status.NOT_APPLICABLE,
        "functional_success_rate": Status.NOT_APPLICABLE,
        "functional_deficit_cumulative": Status.NOT_APPLICABLE,
        "production_cumulative": Status.NOT_APPLICABLE,
    }
    return EvaluationProfile(
        profile_id=PROFILE_ID,
        scenario_id=SCENARIO_ID,
        configuration_id=CONFIGURATION_ID,
        application_domain="synthetic_assignment",
        organizational_problem="optional one-to-one matching under per-period agent capacity",
        decision_objective={policy: OBJECTIVE_ID for policy in POLICY_IDS},
        constraints="one agent and one demanded task unit per assignment; capacity 3; no inter-period coupling",
        primary_metrics=("original_reward_cumulative",),
        secondary_metrics=("resource_usage:assignment_count",),
        diagnostic_metrics=(
            "ces_cumulative", "functional_success_rate",
            "functional_deficit_cumulative", "production_cumulative",
        ),
        diagnostic_fields=("assignments", "demand_by_task", "served_by_task",
                           "unserved_by_task", "capacity_per_period"),
        information_regime="current_period_demand_and_known_static_competence_scores",
        temporal_horizon=4,
        aggregation_rules="sum declared assignment reward and assignment count over four periods",
        demand_distribution_id="s2a_fixed_four_period_demand_sequence_v1",
        metric_availability=unavailable,
        resource_units={"assignment_count": "agent-task assignments"},
    )


def _validate_source_result(result: Mapping[str, Any]) -> None:
    required = {
        "experiment", "matrix_C_agent_by_task", "agents", "tasks", "demands",
        "capacity_per_period", "periods", "horizon_reward", "global_exhaustive_plan",
        "assumptions",
    }
    missing = required - set(result)
    if missing:
        raise ValueError(f"incomplete S2a runner result; missing {sorted(missing)}")
    if result["experiment"] != "HLS-S2a-static-competence-variable-demand":
        raise ValueError("unsupported S2a experiment identity")
    matrix = result["matrix_C_agent_by_task"]
    agents, tasks, demands = result["agents"], result["tasks"], result["demands"]
    capacity, periods = result["capacity_per_period"], result["periods"]
    if (len(matrix) != len(agents) or any(len(row) != len(tasks) for row in matrix)
            or len(demands) != 4 or len(periods) != 4 or capacity != 3):
        raise ValueError("S2a source result dimensions differ from the frozen configuration")
    if tuple(period["period"] for period in periods) != tuple(range(4)):
        raise ValueError("S2a periods must be recorded exactly once in temporal order")
    for period, demand, row in zip(range(4), demands, periods):
        if tuple(row["demand_by_task"][task] for task in tasks) != tuple(demand):
            raise ValueError(f"period {period} demand differs from the declared configuration")
        for policy in POLICY_IDS:
            assignments = row[f"{policy}_assignments"]
            served = row[f"{policy}_demand_satisfied"]
            unserved = row[f"{policy}_demand_unserved"]
            if len(assignments) > capacity:
                raise ValueError(f"period {period} {policy} exceeds capacity")
            if len({item["agent"] for item in assignments}) != len(assignments):
                raise ValueError(f"period {period} {policy} reuses an agent")
            if len({item["unit"] for item in assignments}) != len(assignments):
                raise ValueError(f"period {period} {policy} reuses a work unit")
            if any(item["agent"] not in agents or item["task"] not in tasks for item in assignments):
                raise ValueError(f"period {period} {policy} contains an unknown agent or task")
            recalculated = sum(
                float(matrix[agents.index(item["agent"])][tasks.index(item["task"])])
                for item in assignments
            )
            if abs(recalculated - float(row[f"{policy}_reward"])) > 1e-12:
                raise ValueError(f"period {period} {policy} reward does not match assignments")
            for task_index, task in enumerate(tasks):
                count = sum(item["task"] == task for item in assignments)
                if served[task] != count or served[task] + unserved[task] != demand[task_index]:
                    raise ValueError(f"period {period} {policy} task counts do not reconcile")
    totals = result["horizon_reward"]
    for policy in POLICY_IDS:
        observed_total = sum(float(row[f"{policy}_reward"]) for row in periods)
        if abs(observed_total - float(totals[f"{policy}_per_period"])) > 1e-12:
            raise ValueError(f"{policy} period rewards do not match the horizon total")


def adapt_s2a_policy(
    result: Mapping[str, Any],
    policy_id: str,
    *,
    source_pointer: str = "experiments.run_hls_s2a_static_demand.run_s2a",
) -> tuple[ExperimentRun, tuple[EvaluationRecord, ...]]:
    """Build the common run envelope and PEF rows from one runner result.

    The runner owns decisions and the original result. This function only
    validates and translates the already-produced data.
    """
    _validate_source_result(result)
    if policy_id not in POLICY_IDS:
        raise ValueError(f"S2a has no executable policy {policy_id!r}")
    if not source_pointer:
        raise ValueError("source pointer is required for provenance")

    policy_reward_key = f"{policy_id}_per_period"
    horizon_reward = float(result["horizon_reward"][policy_reward_key])
    assignments_by_period = []
    events: list[ExperimentEvent] = []
    records: list[EvaluationRecord] = []
    for period_row in result["periods"]:
        period = int(period_row["period"])
        assignments = tuple(period_row[f"{policy_id}_assignments"])
        demand_by_task = dict(period_row["demand_by_task"])
        served = dict(period_row[f"{policy_id}_demand_satisfied"])
        unserved = dict(period_row[f"{policy_id}_demand_unserved"])
        reward = float(period_row[f"{policy_id}_reward"])
        assignments_by_period.append(assignments)
        events.append(ExperimentEvent(
            sequence_index=len(events), event_type="decision",
            mechanism_id=policy_id,
            data={"assignments": assignments, "organizational_problem_id": ORGANIZATIONAL_PROBLEM_ID},
            time_index=period,
        ))
        events.append(ExperimentEvent(
            sequence_index=len(events), event_type="execution",
            mechanism_id=policy_id,
            data={
                "original_reward": reward,
                "demand_by_task": demand_by_task,
                "served_by_task": served,
                "unserved_by_task": unserved,
                "assignment_count": len(assignments),
                "capacity": int(result["capacity_per_period"]),
            },
            time_index=period,
        ))
        records.append(EvaluationRecord(
            scenario_id=SCENARIO_ID,
            configuration_id=CONFIGURATION_ID,
            policy_id=policy_id,
            period=period,
            resource_usage={"assignment_count": float(len(assignments))},
            original_reward=reward,
            available_metadata={
                "assignments": assignments,
                "demand_by_task": demand_by_task,
                "served_by_task": served,
                "unserved_by_task": unserved,
                "capacity_per_period": int(result["capacity_per_period"]),
            },
            provenance=f"{source_pointer}#/periods/{period}",
            information_regime="current_period_demand_and_known_static_competence_scores",
            decision_objective=OBJECTIVE_ID,
            field_status={
                "ces": Status.NOT_APPLICABLE,
                "success": Status.NOT_APPLICABLE,
                "deficit": Status.NOT_APPLICABLE,
                "output": Status.NOT_APPLICABLE,
            },
        ))

    context = RunAdapterContext(
        run_id=f"s2a-static-demand-v1-{policy_id}",
        configuration={
            "scenario_id": SCENARIO_ID,
            "scenario_configuration_id": CONFIGURATION_ID,
            "organizational_problem_id": ORGANIZATIONAL_PROBLEM_ID,
            "agents": result["agents"],
            "tasks": result["tasks"],
            "competence_scores_agent_by_task": result["matrix_C_agent_by_task"],
            "demand_by_period": result["demands"],
            "capacity_per_period": result["capacity_per_period"],
            "horizon": 4,
            "period_unit": "operational_period",
            "objective_id": OBJECTIVE_ID,
            "objective_definition": "sum of competence scores for assigned agent-task pairs",
            "method": (
                "existing Hungarian exact bipartite optimizer"
                if policy_id == "exact"
                else "existing greedy edge selection sorted by descending score, then agent and task index"
            ),
        },
        initial_conditions={"competence_scores_agent_by_task": result["matrix_C_agent_by_task"]},
        random_seeds=(),
        information_available={
            "policy_view": "current period demand and known static competence scores",
            "future_demand": "not used by the per-period policy",
        },
        observation_model={"stochastic": False, "reward": "sum assigned competence scores"},
        metadata={
            "evaluation_profile_id": PROFILE_ID,
            "organizational_problem_id": ORGANIZATIONAL_PROBLEM_ID,
            "replicate_id": policy_id,
            "policy_role": "executable_policy",
            "source_runner": "experiments.run_hls_s2a_static_demand.run_s2a",
            "source_result_pointer": source_pointer,
            "result_semantics": "original assignment objective; no physical output or functional requirements",
        },
    )
    total_assignments = sum(len(items) for items in assignments_by_period)
    run = ExperimentRun(
        schema_version="hls-experiment-run/1.0",
        run_id=context.run_id,
        mechanism_id=policy_id,
        policy_id=policy_id,
        configuration=context.configuration,
        initial_conditions=context.initial_conditions,
        random_seeds=context.random_seeds,
        information_available=context.information_available,
        observation_model=context.observation_model,
        software_revision=None,
        units=(
            UnitDeclaration("original_reward", "declared_reward",
                            "Assignment score; the scenario declares no physical or monetary unit."),
            UnitDeclaration("assignment_count", "agent-task assignments",
                            "Count of matched agent-task pairs; capacity is three per period."),
        ),
        events=tuple(events),
        metrics=(
            MetricValue("original_reward_cumulative", horizon_reward, "declared_reward",
                        "Original S2a sum-assignment-score objective over the four periods.", "higher"),
            MetricValue("assignment_count_cumulative", total_assignments, "agent-task assignments",
                        "Diagnostic count of assigned pairs; not a functional-service metric."),
        ),
        mechanism_results={
            "horizon_reward": horizon_reward,
            "assignment_count": total_assignments,
            "period_count": 4,
        },
        metadata=context.metadata or {},
    )
    return run, tuple(records)
