"""Convert S7 policy replays to generic HLS-PEF period records.

The adapter is downstream of policy selection: it only transforms an already
replayed action/state trajectory into evaluation observations.
"""

from __future__ import annotations

from typing import Sequence

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
