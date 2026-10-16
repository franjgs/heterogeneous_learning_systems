"""Small deterministic validity fixtures for the integrated HLS Laboratory.

This is an instrument check, not a policy comparison campaign. It uses the
existing action catalogue, runner, policies, MIS-v2 transition and C5
environment interface. Results are written to a dedicated diagnostics path.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.discover_v0 import JOINT_ACTIONS, production_inputs  # noqa: E402
from hls.hls_lab_dynamic import DemandRegime, LearningProfile  # noqa: E402
from hls.hls_lab_v1 import ProblemSpec, feasible_actions, make_team  # noqa: E402
from hls.hls_lab_v1_environment import (  # noqa: E402
    ExogenousEnvironmentConfig,
    generate_environment_trajectory,
)
from hls.hls_lab_v1_integrated import (  # noqa: E402
    IntegratedAction,
    IntegratedProblem,
    P0ProductionOnly,
    P1FixedTeaching,
    P2AdaptiveTeaching,
    TeachingEfficacy,
    TeachingEvent,
    TeachingParameters,
    enumerate_feasible_integrated_actions,
    run_integrated_sequence,
)
from hls.synthetic.c5 import StationaryTaskDemand  # noqa: E402


OUT = ROOT / "results/diagnostics/hls_laboratory_validity_assessment"
SEED = 2026101607
PARAMETERS = TeachingParameters(
    transfer_rate=0.75,
    effort=0.25,
    outcome_noise_sd=0.0,
    production_observation_noise_sd=0.0,
    competence_grid_points=21,
    competence_prior_variance=0.04,
)
LEARNING = LearningProfile(((0.5, 0.1), (0.2, 0.2), (0.1, 0.1)))
ZERO_EFFICACY = TeachingEfficacy(tuple(
    tuple((0.0, 0.0) if i == j else (0.0, 0.0) for j in range(3))
    for i in range(3)
))
EFFICIENCY = TeachingEfficacy(tuple(
    tuple((0.0, 0.0) if i == j else (0.8, 0.8) for j in range(3))
    for i in range(3)
))
SKILL0_E0 = ((1.0, 0.0), (0.0, 0.0), (0.0, 0.0))
SKILL0_E1 = ((0.0, 0.0), (1.0, 0.0), (0.0, 0.0))


def _problem(
    problem_id: str,
    requirements: tuple[float, float],
    *,
    budget: float = 2.0,
    cap: float = 1.0,
    allowed_actions=None,
    cost: float = 0.2,
) -> IntegratedProblem:
    return IntegratedProblem(
        ProblemSpec(problem_id, requirements, budget, cap, 1, allowed_actions, cost),
        ces_weights=(1.0, 0.0),
        demand_label="fixed-diagnostic-demand",
    )


def _run(
    team,
    problems: tuple[IntegratedProblem, ...],
    *,
    seed: int = SEED,
    learning: LearningProfile = LEARNING,
    individual_learning: bool = False,
    efficacy: TeachingEfficacy = ZERO_EFFICACY,
    action: IntegratedAction | None = None,
    policy=None,
):
    return run_integrated_sequence(
        team,
        problems,
        policy or P0ProductionOnly(),
        learning=learning,
        teaching_efficacy=efficacy,
        parameters=PARAMETERS,
        individual_learning=individual_learning,
        organizational_learning=True,
        seed=seed,
        first_action_override=action,
    )


def _record_signature(result) -> list[dict[str, object]]:
    return [{
        "problem_id": row.problem_id,
        "requirements": row.requirements,
        "action": row.action,
        "outputs": row.outputs,
        "ces": row.ces_reward,
        "success": row.functional_result.success,
        "real_before": row.competence_real_before,
        "real_after": row.competence_real_after,
        "estimated_before": row.competence_estimated_before,
        "estimated_after": row.competence_estimated_after,
        "production_effort": row.production_effort,
        "teaching_effort": row.teaching_effort,
        "resource_used": row.total_resource_used,
        "observations": row.individual_observations,
    } for row in result.records]


def _action_json(action: IntegratedAction) -> dict[str, object]:
    teaching = action.teaching
    return {
        "production": action.production,
        "teaching": None if teaching is None else {
            "instructor": teaching.instructor,
            "learner": teaching.learner,
            "capability": teaching.capability,
            "effort": teaching.effort,
        },
    }


def run_diagnostics() -> dict[str, object]:
    # A. Same model inputs with zero observation noise: seeds cannot alter
    # decisions, state transitions, or outcomes in this deterministic fixture.
    equivalence_team = make_team(((0.7, 0.2), (0.4, 0.3), (0.2, 0.5)))
    equivalence_problems = (_problem("eq-0", (0.5, 0.0)), _problem("eq-1", (0.5, 0.0)))
    eq_a = _run(equivalence_team, equivalence_problems, seed=11)
    eq_b = _run(equivalence_team, equivalence_problems, seed=93)
    equivalence = {
        "status": "PASS" if _record_signature(eq_a) == _record_signature(eq_b) else "FAIL",
        "expected": "identical episode signatures with identical inputs and zero observation noise",
        "actual_identical": _record_signature(eq_a) == _record_signature(eq_b),
        "ces": [sum(row.ces_reward for row in run.records) for run in (eq_a, eq_b)],
        "successes": [sum(row.functional_result.success for row in run.records) for run in (eq_a, eq_b)],
    }
    assert equivalence["actual_identical"]

    # B. Increase one relevant real competence while fixing the action and
    # information. The active CES dimension is exactly the additive output.
    action_e0 = IntegratedAction(SKILL0_E0)
    low_team = make_team(((0.5, 0.2), (0.2, 0.2), (0.2, 0.2)))
    high_team = make_team(((0.6, 0.2), (0.2, 0.2), (0.2, 0.2)))
    low = _run(low_team, (_problem("skill-low", (0.4, 0.0)),), action=action_e0)
    high = _run(high_team, (_problem("skill-high", (0.4, 0.0)),), action=action_e0)
    competence = {
        "status": "PASS" if (
            high.records[0].outputs[0] > low.records[0].outputs[0]
            and high.records[0].functional_result.success == low.records[0].functional_result.success
        ) else "FAIL",
        "expected": "same fixed assignment; +0.1 relevant skill yields +0.1 output while both remain successful",
        "actual": {
            "outputs": [low.records[0].outputs, high.records[0].outputs],
            "ces": [low.records[0].ces_reward, high.records[0].ces_reward],
            "success": [low.records[0].functional_result.success, high.records[0].functional_result.success],
        },
    }
    assert competence["status"] == "PASS"

    # C. Compute the actual discrete action frontier, then test immediately
    # below and above it. The threshold is not selected from policy outcomes.
    frontier_team = make_team(((0.90, 0.20), (0.20, 0.20), (0.25, 0.80)))
    frontier_base = ProblemSpec("frontier-enumeration", (0.1, 0.0), 2.0, 1.0)
    frontier_actions = feasible_actions(frontier_base)
    frontier = max(
        production_inputs(frontier_team.real_matrix, action)[0]
        for action in frontier_actions
    )
    epsilon = 0.01
    below = _run(frontier_team, (_problem("below-frontier", (frontier - epsilon, 0.0)),))
    above = _run(frontier_team, (_problem("above-frontier", (frontier + epsilon, 0.0)),))
    boundary = {
        "status": "PASS" if (
            below.records[0].functional_result.success
            and not above.records[0].functional_result.success
            and abs(max(production_inputs(frontier_team.real_matrix, a)[0] for a in frontier_actions) - frontier) < 1e-12
        ) else "FAIL",
        "expected": "success just below and failure just above the enumerated production frontier",
        "actual": {
            "frontier": frontier,
            "epsilon": epsilon,
            "requirements": [frontier - epsilon, frontier + epsilon],
            "outputs": [below.records[0].outputs, above.records[0].outputs],
            "success": [below.records[0].functional_result.success, above.records[0].functional_result.success],
            "maximizing_actions": [
                JOINT_ACTIONS.index(a) for a in frontier_actions
                if abs(production_inputs(frontier_team.real_matrix, a)[0] - frontier) < 1e-12
            ],
        },
    }
    assert boundary["status"] == "PASS"

    # D. Same team/problem/budget, two feasible allocations. Overrides provide
    # a one-period action-level intervention without adding a policy.
    assignment_team = make_team(((0.8, 0.2), (0.2, 0.2), (0.3, 0.2)))
    assignment_problem = _problem("assignment-sensitive", (0.5, 0.0))
    assigned_best = _run(assignment_team, (assignment_problem,), action=IntegratedAction(SKILL0_E0))
    assigned_weak = _run(assignment_team, (assignment_problem,), action=IntegratedAction(SKILL0_E1))
    assignment = {
        "status": "PASS" if (
            assigned_best.records[0].outputs[0] > assigned_weak.records[0].outputs[0]
            and assigned_best.records[0].functional_result.success
            and not assigned_weak.records[0].functional_result.success
        ) else "FAIL",
        "expected": "assigning one unit to E0 succeeds; the same action to lower-skill E1 fails",
        "actual": {
            "actions": [assigned_best.records[0].action.production, assigned_weak.records[0].action.production],
            "outputs": [assigned_best.records[0].outputs, assigned_weak.records[0].outputs],
            "success": [assigned_best.records[0].functional_result.success, assigned_weak.records[0].functional_result.success],
        },
    }
    assert assignment["status"] == "PASS"

    # E. Only MIS-v2 is toggled. A one-action catalogue fixes the assignment
    # across both periods; the first-period output must match, the second must
    # reflect the prior competence transition.
    lbd_action = JOINT_ACTIONS[JOINT_ACTIONS.index(SKILL0_E0)]
    lbd_problem = _problem("lbd-fixed", (0.3, 0.0), allowed_actions=(lbd_action,))
    lbd_sequence = (lbd_problem, lbd_problem)
    lbd_team = make_team(((0.4, 0.2), (0.2, 0.2), (0.2, 0.2)))
    lbd_off = _run(lbd_team, lbd_sequence, individual_learning=False)
    lbd_on = _run(lbd_team, lbd_sequence, individual_learning=True)
    lbd = {
        "status": "PASS" if (
            lbd_off.records[0].outputs == lbd_on.records[0].outputs
            and lbd_off.records[1].outputs[0] == lbd_off.records[0].outputs[0]
            and lbd_on.records[1].outputs[0] > lbd_on.records[0].outputs[0]
            and lbd_off.final_team.real_matrix != lbd_on.final_team.real_matrix
        ) else "FAIL",
        "expected": "identical first output; LI ON increases the same expert's skill and second output; LI OFF remains fixed",
        "actual": {
            "outputs_off": [row.outputs for row in lbd_off.records],
            "outputs_on": [row.outputs for row in lbd_on.records],
            "competence_off": lbd_off.final_team.real_matrix,
            "competence_on": lbd_on.final_team.real_matrix,
        },
    }
    assert lbd["status"] == "PASS"

    # F. Compare the enumerated no-lesson and lesson action sets under the
    # same budget, then verify actual runner accounting for both branches.
    resource_problem = _problem("resource-control", (0.5, 0.0), budget=2.0, cap=1.0)
    integrated_actions = enumerate_feasible_integrated_actions(
        resource_problem.problem, teaching_effort=PARAMETERS.effort
    )
    production_only = tuple(a for a in integrated_actions if a.teaching is None)
    lesson_actions = tuple(
        a for a in integrated_actions
        if a.teaching is not None and a.teaching.relation == (0, 1, 0)
    )
    max_free_effort = max(sum(sum(row) for row in a.production) for a in production_only)
    max_lesson_effort = max(sum(sum(row) for row in a.production) for a in lesson_actions)
    lesson_action = max(
        lesson_actions,
        key=lambda a: (sum(sum(row) for row in a.production), a.production),
    )
    resource_team = make_team(((0.9, 0.2), (0.2, 0.2), (0.25, 0.8)))
    no_lesson = _run(resource_team, (resource_problem,))
    with_lesson = _run(resource_team, (resource_problem,), action=lesson_action, efficacy=ZERO_EFFICACY)
    no_row, lesson_row = no_lesson.records[0], with_lesson.records[0]
    residual = resource_problem.problem.resource_budget - lesson_row.total_resource_used
    resource = {
        "status": "PASS" if (
            max_free_effort == 2.0 and max_lesson_effort == 1.0
            and abs(lesson_row.teaching_effort - 0.5) < 1e-12
            and abs(lesson_row.total_resource_used - 1.5) < 1e-12
            and abs(residual - 0.5) < 1e-12
            and abs(no_row.production_effort - max_free_effort) < 1e-12
        ) else "FAIL",
        "expected": "budget 2; no-lesson catalog supports 2.0 production; lesson uses 0.5 and caps catalog production at 1.0, stranding 0.5",
        "actual": {
            "budget_each": resource_problem.problem.resource_budget,
            "catalog_max_production_effort": [max_free_effort, max_lesson_effort],
            "recorded": {
                "no_lesson_production_effort": no_row.production_effort,
                "lesson_production_effort": lesson_row.production_effort,
                "lesson_effort": lesson_row.teaching_effort,
                "lesson_total_used": lesson_row.total_resource_used,
                "lesson_residual": residual,
                "resource_cost": [no_row.resource_cost, lesson_row.resource_cost],
                "ces": [no_row.ces_reward, lesson_row.ces_reward],
            },
        },
    }
    assert resource["status"] == "PASS"

    # Negative mechanism control: zero efficacy still consumes lesson effort.
    zero_gain = _run(
        resource_team,
        (resource_problem,),
        action=lesson_action,
        efficacy=ZERO_EFFICACY,
    )
    zero_control = {
        "status": "PASS" if (
            zero_gain.records[0].teaching_gain_real == 0.0
            and zero_gain.records[0].teaching_effort == 0.5
        ) else "FAIL",
        "expected": "zero efficacy gives zero direct gain while lesson resources remain charged",
        "actual": {
            "direct_gain": zero_gain.records[0].teaching_gain_real,
            "teaching_effort": zero_gain.records[0].teaching_effort,
            "total_resource_used": zero_gain.records[0].total_resource_used,
        },
    }
    assert zero_control["status"] == "PASS"

    # Verify actual policy comparability on a frozen, generated C5 sequence:
    # same initial team, tuple of problems, budget rules, and indexed shocks.
    env_config = ExogenousEnvironmentConfig(
        StationaryTaskDemand({"skill0": 1.0}),
        {"skill0": DemandRegime("skill0", ((0.5, 0.0),), (1.0,))},
        horizon=3,
        resource_budget=2.0,
    )
    trajectory = generate_environment_trajectory(env_config, seed=SEED)
    generated_again = generate_environment_trajectory(env_config, seed=SEED)
    env_team = make_team(((0.8, 0.2), (0.3, 0.2), (0.2, 0.3)))
    policies = (
        P0ProductionOnly(),
        P1FixedTeaching((0, 1, 0)),
        P2AdaptiveTeaching(((0, 1, 0),)),
    )
    policy_runs = [
        _run(
            env_team,
            trajectory.problems,
            seed=SEED,
            individual_learning=False,
            efficacy=EFFICIENCY,
            policy=policy,
        )
        for policy in policies
    ]
    shared_signature = [
        (item.problem.problem_id, item.problem.requirements, item.problem.resource_budget)
        for item in trajectory.problems
    ]
    assert trajectory.problems == generated_again.problems
    assert all(
        [(row.problem_id, row.requirements) for row in run.records]
        == [(p.problem.problem_id, p.problem.requirements) for p in trajectory.problems]
        for run in policy_runs
    )
    policy_comparison = {
        "status": "PASS",
        "expected": "P0/P1/P2 receive the same frozen generated problems and resource limits",
        "exogenous_seed": SEED,
        "trajectory_reproducible": trajectory.problems == generated_again.problems,
        "shared_problems": shared_signature,
        "policies": [{
            "policy": run.policy,
            "actions": [_action_json(row.action) for row in run.records],
            "ces": sum(row.ces_reward for row in run.records),
            "successes": sum(row.functional_result.success for row in run.records),
            "production_effort": sum(row.production_effort for row in run.records),
            "teaching_effort": sum(row.teaching_effort for row in run.records),
            "resource_used": sum(row.total_resource_used for row in run.records),
            "resource_cost": sum(row.resource_cost for row in run.records),
            "competence_final": run.final_team.real_matrix,
            "estimates_final": run.final_team.estimated_matrix,
            "observations": [row.individual_observations for row in run.records],
        } for run in policy_runs],
    }

    return {
        "design": {
            "seed": SEED,
            "production_observation_noise_sd": PARAMETERS.production_observation_noise_sd,
            "teaching_observation_noise_sd": PARAMETERS.outcome_noise_sd,
            "learning_profile_eta": LEARNING.eta,
            "budget_frontier": {"budget": 2.0, "expert_cap": 1.0},
            "conditions": "deterministic diagnostics; no population sampling",
        },
        "diagnostics": {
            "A_equivalence": equivalence,
            "B_competence_sensitive": competence,
            "C_feasibility_boundary": boundary,
            "D_assignment_sensitive": assignment,
            "E_MIS_v2_control": lbd,
            "F_resource_accounting": resource,
            "negative_zero_efficacy": zero_control,
            "matched_policy_comparison": policy_comparison,
        },
    }


def main() -> None:
    results = run_diagnostics()
    OUT.mkdir(parents=True, exist_ok=True)
    data_path = OUT / "diagnostics.json"
    data_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sources = (
        Path(__file__),
        ROOT / "src/hls/discover_v0.py",
        ROOT / "src/hls/discover_develop_v2.py",
        ROOT / "src/hls/hls_lab_v1.py",
        ROOT / "src/hls/hls_lab_dynamic.py",
        ROOT / "src/hls/hls_lab_v1_integrated.py",
        ROOT / "src/hls/hls_lab_v1_environment.py",
        ROOT / "src/hls/synthetic/c5.py",
    )
    manifest = {
        "created_at": datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="seconds"),
        "command": "PYTHONPATH=src python experiments/synthetic/hls_lab_v1/laboratory_validity_diagnostics.py",
        "base_commit": "dcfd99c7e3ee38204f2f3a99a21372712fa5d127",
        "seed": SEED,
        "scope": "deterministic instrument diagnostics; not scientific policy evidence",
        "source_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sources
        },
        "output_sha256": {
            "diagnostics.json": hashlib.sha256(data_path.read_bytes()).hexdigest()
        },
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "statuses": {key: value["status"] for key, value in results["diagnostics"].items()},
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
