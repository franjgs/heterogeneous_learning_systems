"""Adapt the existing exact S4 N×K Bellman result to ExperimentRun v1/PEF.

This module translates an already solved trajectory. It does not select
actions, replay physics, or give the evaluator access to the solver.
"""

from __future__ import annotations

from dataclasses import asdict
from math import isclose
from typing import Sequence

from hls.experiment_contract import (
    ExperimentEvent,
    ExperimentRun,
    MetricValue,
    UnitDeclaration,
)
from hls.performance_evaluation import EvaluationProfile, EvaluationRecord
from hls.synthetic.hls_s4_transfer_exact import ExactResult, ExactTransferCase


SCENARIO_ID = "S4"
CONFIGURATION_ID = "s4_exact_transfer_reference_T3_v1"
ORGANIZATIONAL_PROBLEM_ID = "NK_productive_effort_with_optional_transfer"
INFORMATION_REGIME = "exact_true_competence_and_known_deterministic_demand_sequence"
OBJECTIVE_ID = "cumulative_CES"
POLICY_IDS = ("A", "B")
PROFILE_BASIC_ID = "s4_collective_basic_v1"
PROFILE_EXTENDED_ID = "s4_collective_resources_diagnostics_v1"
AGGREGATION_RULES = (
    "one demanded problem per period; sum cumulative measures over T; "
    "functional success is successes divided by demanded periods"
)


def s4_evaluation_profiles() -> tuple[EvaluationProfile, EvaluationProfile]:
    """Return two metric selections over the same S4 semantics and records."""
    shared = dict(
        scenario_id=SCENARIO_ID,
        configuration_id=CONFIGURATION_ID,
        application_domain="synthetic_workforce",
        organizational_problem="N×K productive effort with MIS-v2 and optional transfer",
        decision_objective={policy: OBJECTIVE_ID for policy in POLICY_IDS},
        constraints="existing per-agent effort limits and shared collective/problem resource budgets",
        information_regime=INFORMATION_REGIME,
        temporal_horizon=3,
        aggregation_rules=AGGREGATION_RULES,
        demand_distribution_id="S4_exact_known_sequence_task-x_task-y_task-y_v1",
    )
    collective_metrics = (
        "original_reward_cumulative",
        "ces_cumulative",
        "production_cumulative",
        "functional_success_rate",
        "functional_deficit_cumulative",
    )
    basic = EvaluationProfile(
        profile_id=PROFILE_BASIC_ID,
        primary_metrics=("original_reward_cumulative",),
        secondary_metrics=("ces_cumulative", "production_cumulative",
                           "functional_success_rate", "functional_deficit_cumulative"),
        diagnostic_fields=("decision", "competence_transition", "demand", "requirements"),
        **shared,
    )
    extended = EvaluationProfile(
        profile_id=PROFILE_EXTENDED_ID,
        primary_metrics=("original_reward_cumulative",),
        secondary_metrics=(
            "ces_cumulative", "production_cumulative", "functional_success_rate",
            "functional_deficit_cumulative", "resource_usage:productive_effort",
            "resource_usage:teaching_effort", "resource_usage:teaching_resource",
            "resource_usage:total_resource",
            "teaching_actions_cumulative",
        ),
        diagnostic_fields=(
            "decision", "competence_before", "competence_after_mis",
            "competence_after", "mis_increment", "transfer_increment",
            "productive_effort", "teaching_resource", "total_resource",
            "unused_resource",
        ),
        resource_units={
            "productive_effort": "effort",
            "teaching_effort": "effort",
            "teaching_resource": "effort",
            "total_resource": "effort",
        },
        **shared,
    )
    assert set(basic.metrics).issubset(set(extended.metrics))
    assert set(basic.metrics) == set(collective_metrics)
    return basic, extended


def _validate_result(case: ExactTransferCase, result: ExactResult,
                     policy_id: str, transfer_available: bool) -> None:
    if policy_id not in POLICY_IDS:
        raise ValueError(f"unsupported S4 reference policy: {policy_id!r}")
    horizon = len(case.problems)
    if horizon != 3 or len(result.periods) != horizon or len(result.actions) != horizon:
        raise ValueError("S4 reference result must cover the declared T=3 horizon")
    if policy_id == "A" and transfer_available:
        raise ValueError("policy A is defined without transfer")
    if policy_id == "B" and not transfer_available:
        raise ValueError("policy B is defined with optional transfer")
    if not isclose(result.value, sum(row.reward for row in result.periods),
                    rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("solver value does not equal recorded period rewards")
    for period, (problem, row, action) in enumerate(
        zip(case.problems, result.periods, result.actions)
    ):
        if row.period != period or row.problem_id != problem.problem_id:
            raise ValueError("S4 result periods do not match the declared demand sequence")
        if row.action != action:
            raise ValueError("S4 result action sequence differs from period records")
        if policy_id == "A" and action.teaching is not None:
            raise ValueError("no-transfer policy A contains a teaching action")


def adapt_s4_policy(
    case: ExactTransferCase,
    result: ExactResult,
    policy_id: str,
    *,
    transfer_available: bool,
    source_pointer: str,
    software_revision: str | None = None,
) -> tuple[ExperimentRun, tuple[EvaluationRecord, ...]]:
    """Create the common run envelope and PEF rows from a solved S4 result."""
    if not source_pointer or not isinstance(source_pointer, str):
        raise ValueError("source pointer is required for provenance")
    _validate_result(case, result, policy_id, transfer_available)
    demand_names = tuple(problem.problem_id for problem in case.problems)
    configuration = {
        "scenario_id": SCENARIO_ID,
        "scenario_configuration_id": CONFIGURATION_ID,
        "organizational_problem_id": ORGANIZATIONAL_PROBLEM_ID,
        "agents": case.organization.agent_ids,
        "competencies": case.organization.skill_ids,
        "initial_competence": case.organization.competence_initial,
        "eta": case.profile.eta,
        "demand_sequence": demand_names,
        "requirements": tuple(problem.requirements for problem in case.problems),
        "ces_weights": tuple(problem.ces_weights for problem in case.problems),
        "individual_effort_limits": case.organization.effort_limits,
        "collective_effort_budget": case.organization.collective_effort_budget,
        "problem_resource_budgets": tuple(problem.resource_budget for problem in case.problems),
        "teaching_effort": case.teaching_effort,
        "teaching_parameters": asdict(case.teaching_parameters),
        "teaching_efficacy": asdict(case.efficacy),
        "production_action_choices": case.effort_choices,
        "horizon": len(case.problems),
        "period_unit": "operational_period",
        "objective_id": OBJECTIVE_ID,
        "objective_definition": "sum of existing per-period CES rewards, before physical transitions",
        "mechanism": "exact finite-horizon Bellman reference",
        "transfer_availability": transfer_available,
        "policy_interpretation": (
            "MIS-v2-only Bellman reference" if policy_id == "A"
            else "Bellman reference with optional teaching actions"
        ),
    }
    events: list[ExperimentEvent] = []
    records: list[EvaluationRecord] = []
    for period, (problem, row) in enumerate(zip(case.problems, result.periods)):
        action_data = asdict(row.action)
        events.append(ExperimentEvent(
            len(events), "decision", "finite_horizon_bellman", action_data, period,
        ))
        events.append(ExperimentEvent(
            len(events), "physical_transition", "S4_MIS-v2_then_optional_transfer",
            {
                "competence_before": row.competence_before,
                "competence_after_mis": row.competence_after_mis,
                "competence_after": row.competence_after,
                "mis_increment": row.mis_increment,
                "transfer_increment": row.transfer_increment,
            }, period,
        ))
        events.append(ExperimentEvent(
            len(events), "execution", "S4_NK_physical_model",
            {
                "demand": problem.problem_id,
                "output": row.outputs,
                "requirements": problem.requirements,
                "ces_weights": problem.ces_weights,
                "original_reward": row.reward,
                "ces": row.reward,
                "success": row.success,
                "absolute_deficit": row.deficits,
                "resources": {
                    "productive_effort": row.productive_effort,
                    "teaching_resource": row.teaching_resource,
                    "total_resource": row.total_resource,
                    "unused_resource": row.unused_resource,
                },
            }, period,
        ))
        teaching_count = int(row.action.teaching is not None)
        teaching_effort = 0.0 if row.action.teaching is None else row.action.teaching.effort
        records.append(EvaluationRecord(
            scenario_id=SCENARIO_ID,
            configuration_id=CONFIGURATION_ID,
            policy_id=policy_id,
            period=period,
            demand=problem.problem_id,
            output=tuple(row.outputs),
            requirements=tuple(problem.requirements),
            success=row.success,
            deficit=tuple(row.deficits),
            resource_usage={
                "productive_effort": row.productive_effort,
                "teaching_effort": teaching_effort,
                "teaching_resource": row.teaching_resource,
                "total_resource": row.total_resource,
            },
            original_reward=row.reward,
            ces=row.reward,
            available_metadata={
                "action": action_data,
                "competence_before": row.competence_before,
                "competence_after_mis": row.competence_after_mis,
                "competence_after": row.competence_after,
                "mis_increment": row.mis_increment,
                "transfer_increment": row.transfer_increment,
                "productive_effort": row.productive_effort,
                "teaching_effort": teaching_effort,
                "teaching_resource": row.teaching_resource,
                "total_resource": row.total_resource,
                "unused_resource": row.unused_resource,
                "requirement_source": "case.problems[period].requirements",
            },
            provenance=f"{source_pointer}#/{policy_id}/periods/{period}",
            unit_id=f"{problem.problem_id}:period-{period}",
            task_type=problem.problem_id,
            information_regime=INFORMATION_REGIME,
            decision_objective=OBJECTIVE_ID,
            competence_state={
                "before": row.competence_before,
                "after_mis": row.competence_after_mis,
                "after": row.competence_after,
            },
            teaching_action_count=teaching_count,
        ))

    total_reward = sum(row.reward for row in result.periods)
    production_total = sum(sum(row.outputs) for row in result.periods)
    success_rate = sum(row.success for row in result.periods) / len(result.periods)
    deficit_total = sum(sum(row.deficits) for row in result.periods)
    productive_total = sum(row.productive_effort for row in result.periods)
    teaching_total = sum(row.teaching_resource for row in result.periods)
    total_resource = sum(row.total_resource for row in result.periods)
    run = ExperimentRun(
        schema_version="hls-experiment-run/1.0",
        run_id=f"{CONFIGURATION_ID}-{policy_id}",
        mechanism_id="finite_horizon_bellman",
        policy_id=policy_id,
        configuration=configuration,
        initial_conditions={"competence": case.organization.competence_initial,
                            "demand_sequence": demand_names},
        random_seeds=(),
        information_available={
            "policy_view": "exact true competence state",
            "demand": "complete deterministic sequence known to the Bellman reference",
            "future_information": "no uncertainty or hidden future realization in this instance",
        },
        observation_model={"stochastic": False, "kind": "deterministic physical transitions"},
        software_revision=software_revision,
        units=(
            UnitDeclaration("original_reward", "declared_reward", "Original S4 objective; CES per-period reward."),
            UnitDeclaration("ces", "CES_output", "Recorded per-period CES reward; summed over the horizon."),
            UnitDeclaration("production", "output", "Scenario output scale; no external physical unit is declared."),
            UnitDeclaration("effort", "effort", "Abstract S4 resource/effort unit; not time, energy, or money."),
            UnitDeclaration("teaching_actions", "actions", "Count of periods with a teaching action."),
        ),
        events=tuple(events),
        metrics=(
            MetricValue("original_reward_cumulative", total_reward, "declared_reward",
                        "Original Bellman objective: sum of per-period CES reward."),
            MetricValue("ces_cumulative", total_reward, "CES_output",
                        "Recorded CES; separate metric from physical production."),
            MetricValue("production_cumulative", production_total, "output",
                        "Sum over periods and competencies of aggregate production."),
            MetricValue("functional_success_rate", success_rate, "fraction",
                        "Successful demanded periods divided by three."),
            MetricValue("functional_deficit_cumulative", deficit_total, "output",
                        "Sum of absolute per-competency deficits over periods."),
            MetricValue("resource_usage:productive_effort", productive_total, "effort",
                        "Sum of productive effort over periods."),
            MetricValue("resource_usage:teaching_effort",
                        sum(0.0 if row.action.teaching is None else row.action.teaching.effort
                            for row in result.periods), "effort",
                        "Sum of teaching action effort h; distinct from teaching resource 2h."),
            MetricValue("resource_usage:teaching_resource", teaching_total, "effort",
                        "Sum of teaching resource consumption over periods."),
            MetricValue("resource_usage:total_resource", total_resource, "effort",
                        "Sum of productive and teaching resource consumption."),
            MetricValue("teaching_actions_cumulative", sum(row.action.teaching is not None
                                                           for row in result.periods), "actions",
                        "Number of periods containing a teaching action."),
        ),
        mechanism_results={
            "solver_value": result.value,
            "visited_states": result.visited_states,
            "period_count": len(result.periods),
            "transfer_selected": any(row.action.teaching is not None for row in result.periods),
            "source_result": {
                "value": result.value,
                "actions": [asdict(row.action) for row in result.periods],
                "periods": [asdict(row) for row in result.periods],
            },
        },
        metadata={
            "evaluation_profile_ids": [PROFILE_BASIC_ID, PROFILE_EXTENDED_ID],
            "organizational_problem_id": ORGANIZATIONAL_PROBLEM_ID,
            "policy_role": "exact_reference_not_partially_observed_deployed_policy",
            "source_pointer": source_pointer,
            "transfer_available": transfer_available,
            "transfer_selected": any(row.action.teaching is not None for row in result.periods),
        },
    )
    return run, tuple(records)


def evaluate_s4_records(
    profile: EvaluationProfile,
    policy_id: str,
    records: Sequence[EvaluationRecord],
) -> dict:
    """Evaluate records with the common pure evaluator under one S4 profile."""
    from hls.performance_evaluation import PerformanceEvaluator

    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile)
    return evaluator.evaluate(profile.profile_id, policy_id, records)
