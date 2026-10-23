"""S4 closed-loop MIS-v2/transfer evaluation with ex-ante transfer opportunity.

The calibration uses only the physical transition equations and a fixed
feasible action path; it never runs P0/P1/P2 or selects on their rewards.
Evaluation reuses the existing N×K transitions, C5 demand, and policies.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from statistics import mean, stdev

from scipy.stats import t as student_t

from hls.hls_lab_nk_environment import (
    DemandRegimeNK,
    ExogenousEnvironmentConfigNK,
    generate_environment_trajectory_nk,
)
from hls.hls_lab_nk_geometry import ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from hls.hls_lab_nk_policies import (
    P0ProductionOnlyPolicyNK,
    P1FixedTeachingNK,
    P2AdaptiveTeachingNK,
    enumerate_feasible_joint_actions_nk,
)
from hls.hls_lab_nk_production import ces_reward_nk, productive_outputs_nk
from hls.hls_lab_nk_teaching import (
    TeachingActionNK,
    TeachingEfficacyNK,
    TeachingParametersNK,
    teaching_transition_nk,
)
from hls.hls_lab_nk_execution import NKInformationRunResult, run_nk_production_sequence
from hls.hls_lab_nk_estimation import CompetenceObservationParametersNK
from hls.synthetic.c5 import MarkovTaskDemand

from experiments.run_hls_s4_transfer_interaction import (
    RELATIONS,
    design as reference_design,
    interval,
)


RESULT_PATH = Path("results/experiments/hls_s4_transfer_opportunities/results.json")
HORIZON = 24
CALIBRATION_SEEDS = tuple(range(44000, 44010))
TRAIN_SEEDS = tuple(range(44100, 44120))
EVAL_SEEDS = tuple(range(44200, 44230))
ETA_CANDIDATES = (0.18, 0.10, 0.05)
Y_REQUIREMENT = 0.70


def scenario(eta_b_y: float):
    """Use the existing 2×2 system, C5 process, laws, costs and action catalogs."""
    base = reference_design()
    organization = base["organization"]
    old_environment = base["environment"]
    x = old_environment.emissions["x"].problems[0]
    y = ProblemSpecNK("task-y", (0.0, Y_REQUIREMENT), 2.0, (0.0, 1.0))
    environment = ExogenousEnvironmentConfigNK(
        old_environment.process,
        {"x": DemandRegimeNK("x", (x,), (1.0,)),
         "y": DemandRegimeNK("y", (y,), (1.0,))},
        horizon=HORIZON,
        resource_budget=old_environment.resource_budget,
    )
    eta = [list(row) for row in base["learning"].eta]
    eta[1][1] = eta_b_y
    return {
        **base,
        "environment": environment,
        "learning": LearningProfileNK(tuple(tuple(row) for row in eta)),
    }


def fixed_path_transfer_diagnostic(setup) -> dict:
    """Evaluate a resource-matched fixed action path, never a policy.

    On the first y-demand period, the baseline spends 1.5 units productively
    (A=1, B=.5); the transfer path spends .5 teaching and 1.0 productively
    (A=.5, B=.5). Thus the immediate cost is explicit and total resource use
    is equal. Later actions are identical and use the same C5 demand path.
    This is an ex-ante physical plausibility check, not P0/P1/P2 calibration.
    """
    initial = setup["organization"].competence_initial
    profile = setup["learning"]
    efficacy = setup["efficacy"]
    teaching_parameters = setup["teaching_parameters"]
    per_seed = []
    example_rows = []
    for seed in CALIBRATION_SEEDS:
        problems = problems_for_seed(setup, seed)
        no_lesson = initial
        with_lesson = initial
        no_lesson_total = 0.0
        with_lesson_total = 0.0
        lesson_done = False
        first_y_reward_cost = None
        rows = []
        for period, problem in enumerate(problems):
            y_demand = problem.problem_id == "task-y"
            first_y = y_demand and not lesson_done
            if y_demand:
                no_action = ((0.0, 1.0), (0.0, 0.5)) if first_y else ((0.0, 1.0), (0.0, 1.0))
                lesson_action = ((0.0, 0.5), (0.0, 0.5)) if first_y else ((0.0, 1.0), (0.0, 1.0))
            else:
                no_action = lesson_action = ((1.0, 0.0), (0.5, 0.0))
            no_output = productive_outputs_nk(no_lesson, no_action)
            lesson_output = productive_outputs_nk(with_lesson, lesson_action)
            no_reward = ces_reward_nk(no_output, problem.ces_weights)
            lesson_reward = ces_reward_nk(lesson_output, problem.ces_weights)
            if first_y:
                first_y_reward_cost = no_reward - lesson_reward
            no_lesson_total += no_reward
            with_lesson_total += lesson_reward
            no_lesson = mis_v2_transition_nk(no_lesson, no_action, profile)
            with_lesson = mis_v2_transition_nk(with_lesson, lesson_action, profile)
            if first_y:
                with_lesson = teaching_transition_nk(
                    with_lesson,
                    TeachingActionNK("A", "B", "y", setup["policy_parameters"].effort),
                    efficacy,
                    teaching_parameters,
                ).competence_after
                lesson_done = True
            if seed == CALIBRATION_SEEDS[0] and period < 5:
                rows.append({
                    "period": period,
                    "problem": problem.problem_id,
                    "no_lesson_ces": no_reward,
                    "lesson_ces": lesson_reward,
                    "no_lesson_competence_after": no_lesson,
                    "lesson_competence_after": with_lesson,
                })
        per_seed.append({
            "seed": seed,
            "y_periods": sum(problem.problem_id == "task-y" for problem in problems),
            "cumulative_ces_no_lesson": no_lesson_total,
            "cumulative_ces_with_lesson": with_lesson_total,
            "difference": with_lesson_total - no_lesson_total,
            "first_y_reward_cost": first_y_reward_cost,
        })
        if seed == CALIBRATION_SEEDS[0]:
            example_rows = rows
    initial_teacher_learner_gain = (
        setup["teaching_parameters"].transfer_rate
        * setup["policy_parameters"].effort
        * setup["efficacy"].values[0][1][1]
        * (1.0 - initial[1][1])
    )
    return {
        "fixed_action_path": "C5 demand; first y: no-lesson A=1,B=.5 vs A=.5,B=.5 plus A→B/y lesson e=.25; later production actions identical (both agents effort 1 on current skill)",
        "resource_use_first_y_no_lesson": 1.5,
        "resource_use_first_y_with_lesson": 1.5,
        "initial_max_y_output_no_lesson": sum(initial[i][1] for i in range(2)),
        "initial_y_requirement": Y_REQUIREMENT,
        "competence_sum_after_lesson_without_production": initial[0][1] + initial[1][1] + initial_teacher_learner_gain,
        "one_lesson_gain_at_initial_B_y": initial_teacher_learner_gain,
        "first_y_period_reward_cost_mean": mean(
            row["first_y_reward_cost"] for row in per_seed
            if row["first_y_reward_cost"] is not None
        ),
        "cumulative_ces_difference_lesson_minus_no_lesson_mean": mean(row["difference"] for row in per_seed),
        "cumulative_ces_difference_by_calibration_seed": per_seed,
        "period_examples_first_calibration_seed": example_rows,
    }


def calibrate() -> tuple[float, dict]:
    """Choose the first fixed-path physical regime with future transfer value."""
    candidate_rows = []
    selected = None
    for eta_b_y in ETA_CANDIDATES:
        setup = scenario(eta_b_y)
        diagnostic = fixed_path_transfer_diagnostic(setup)
        # Demand opportunity is checked on exogenous calibration seeds only;
        # no organization policy or policy reward is evaluated here.
        y_counts = tuple(
            sum(problem.problem_id == "task-y" for problem in
                generate_environment_trajectory_nk(setup["environment"], seed=seed).problems)
            for seed in CALIBRATION_SEEDS
        )
        diagnostic["calibration_y_periods_by_seed"] = y_counts
        diagnostic["calibration_y_periods_mean"] = mean(y_counts)
        diagnostic["criteria_pass"] = (
            diagnostic["initial_max_y_output_no_lesson"] < Y_REQUIREMENT
            and diagnostic["one_lesson_gain_at_initial_B_y"] > 0.0
            and diagnostic["calibration_y_periods_mean"] >= 8.0
            and diagnostic["cumulative_ces_difference_lesson_minus_no_lesson_mean"] > 0.0
            and sum(row["difference"] > 0.0
                    for row in diagnostic["cumulative_ces_difference_by_calibration_seed"]) >= 8
        )
        candidate_rows.append({"eta_B_y": eta_b_y, **diagnostic})
        if selected is None and diagnostic["criteria_pass"]:
            selected = eta_b_y
    if selected is None:
        raise RuntimeError("no preregistered calibration candidate met the physical criteria")
    return selected, {
        "method": "ordered deterministic candidate screen; no P0/P1/P2 evaluation and no policy reward used",
        "candidate_order_eta_B_y": ETA_CANDIDATES,
        "fixed_horizon": HORIZON,
        "fixed_y_requirement": Y_REQUIREMENT,
        "selection_rule": "first candidate with initial y shortfall, positive A→B/y transition, mean >=8 exogenous y periods, and a positive cumulative CES difference on the resource-matched fixed action path in at least 8/10 calibration demand trajectories; this is a structural screen, not policy evaluation",
        "calibration_seeds": CALIBRATION_SEEDS,
        "selected_eta_B_y": selected,
        "candidates": candidate_rows,
    }


def problems_for_seed(setup, seed: int):
    return generate_environment_trajectory_nk(setup["environment"], seed=seed).problems


def opportunity_diagnostics(setup, problems) -> dict:
    """Count ex-ante feasible lesson opportunities, independent of policy choice."""
    rows = []
    for period, problem in enumerate(problems):
        actions = enumerate_feasible_joint_actions_nk(
            setup["organization"], problem,
            max_candidates=216,
            teaching_enabled=True,
            teaching_efficacy=setup["efficacy"],
            teaching_effort=setup["policy_parameters"].effort,
            per_agent_effort_choices=setup["effort_choices"],
        )
        feasible = tuple(action for action in actions if action.teaching is not None)
        required = {skill for skill, value in enumerate(problem.requirements) if value > 0}
        relevant = tuple(action for action in feasible
                         if setup["organization"].skill_ids.index(action.teaching.skill_id) in required)
        rows.append({
            "period": period,
            "problem": problem.problem_id,
            "feasible_lesson_actions": len(feasible),
            "feasible_current_skill_lesson_actions": len(relevant),
        })
    return {
        "periods_with_any_feasible_lesson": sum(row["feasible_lesson_actions"] > 0 for row in rows),
        "periods_with_feasible_current_skill_lesson": sum(
            row["feasible_current_skill_lesson_actions"] > 0 for row in rows
        ),
        "per_period": rows,
    }


def execute(setup, problems, policy):
    result = run_nk_production_sequence(
        setup["organization"], tuple(problems),
        max_candidates=216,
        per_agent_effort_choices=setup["effort_choices"],
        individual_learning=True,
        learning_profile=setup["learning"],
        teaching_enabled=True,
        teaching_efficacy=setup["efficacy"],
        teaching_parameters=setup["teaching_parameters"],
        policy_parameters=setup["policy_parameters"],
        observation_parameters=setup["observation_parameters"],
        organizational_learning=True,
        policy=policy,
        information_mode="perfect",
    )
    if not isinstance(result, NKInformationRunResult):
        raise AssertionError("S4 policy execution must return information-aware records")
    return result


def summarize(result: NKInformationRunResult) -> dict:
    rows = result.records
    return {
        "ces": sum(row.production.ces_reward for row in rows),
        "successes": sum(row.production.functional_result.success for row in rows),
        "normalized_deficit": sum(row.production.functional_result.normalized_deficit for row in rows),
        "lessons": sum(row.action.teaching is not None for row in rows),
        "lesson_periods": [row.period for row in rows if row.action.teaching is not None],
        "productive_effort": sum(row.productive_effort_used for row in rows),
        "teaching_effort": sum(row.teaching_resource_used for row in rows),
        "total_effort": sum(row.total_resource_used for row in rows),
        "idle_resources": sum(row.unused_collective_capacity for row in rows),
        "initial_competence": rows[0].competence_actual_before,
        "final_competence": result.final_state.competence_real,
        "mis_increment_total": tuple(tuple(
            sum(row.mis_increment[i][k] for row in rows)
            for k in range(len(rows[0].mis_increment[0]))
        ) for i in range(len(rows[0].mis_increment))),
        "transfer_increment_total": tuple(tuple(
            sum(row.teaching_increment[i][k] for row in rows)
            for k in range(len(rows[0].teaching_increment[0]))
        ) for i in range(len(rows[0].teaching_increment))),
    }


def period_trace(result: NKInformationRunResult) -> list[dict]:
    return [{
        "period": row.period,
        "problem": row.production.problem_id,
        "requirements": row.production.requirements,
        "action": asdict(row.action),
        "ces": row.production.ces_reward,
        "success": row.production.functional_result.success,
        "normalized_deficit": row.production.functional_result.normalized_deficit,
        "competence_before": row.competence_actual_before,
        "competence_after_mis": row.competence_after_mis,
        "competence_after_transfer": row.competence_actual_after,
        "mis_increment": row.mis_increment,
        "transfer_increment": row.teaching_increment,
        "productive_effort": row.productive_effort_used,
        "teaching_effort": row.teaching_resource_used,
        "total_effort": row.total_resource_used,
        "idle_resources": row.unused_collective_capacity,
    } for row in result.records]


def evaluate() -> dict:
    eta_b_y, calibration = calibrate()
    setup = scenario(eta_b_y)
    fixed_scores = {relation: [] for relation in RELATIONS}
    for seed in TRAIN_SEEDS:
        problems = problems_for_seed(setup, seed)
        for relation in RELATIONS:
            fixed_scores[relation].append(summarize(
                execute(setup, problems, P1FixedTeachingNK(relation))
            )["ces"])
    selected_relation = max(RELATIONS, key=lambda relation: mean(fixed_scores[relation]))
    policies = {
        "P0": P0ProductionOnlyPolicyNK(),
        "P1_train_selected": P1FixedTeachingNK(selected_relation),
        "P2": P2AdaptiveTeachingNK(RELATIONS),
    }
    per_seed = {name: [] for name in policies}
    traces = {name: [] for name in policies}
    feasible_opportunities = []
    for seed in EVAL_SEEDS:
        problems = problems_for_seed(setup, seed)
        feasible_opportunities.append({
            "seed": seed,
            **opportunity_diagnostics(setup, problems),
        })
        for name, policy in policies.items():
            run = execute(setup, problems, policy)
            per_seed[name].append({"seed": seed, **summarize(run)})
            traces[name].append({"seed": seed, "periods": period_trace(run)})
    metrics = ("ces", "successes", "normalized_deficit", "lessons",
               "productive_effort", "teaching_effort", "total_effort", "idle_resources")
    summaries = {
        name: {metric: interval(row[metric] for row in rows)
               for metric in metrics}
        for name, rows in per_seed.items()
    }
    paired = {}
    for left, right, label in (
        ("P2", "P0", "P2_minus_P0"),
        ("P2", "P1_train_selected", "P2_minus_P1"),
        ("P1_train_selected", "P0", "P1_minus_P0"),
    ):
        paired[label] = {
            metric: interval(
                per_seed[left][i][metric] - per_seed[right][i][metric]
                for i in range(len(EVAL_SEEDS))
            ) for metric in metrics
        }
    return {
        "experiment": "HLS-S4 transfer opportunity calibration and closed-loop evaluation",
        "design": {
            "A_system": "2 agents × 2 competencies; exogenous C5 x/y Markov demand; hidden policy state is not used (perfect information mode retained from reference); endogenous MIS-v2 and directed transfer",
            "B_organizational_mode": "existing N×K resource-constrained productive effort plus at most one directed lesson per period",
            "C_decision_architectures": ["P0 production-only", "P1 fixed relation trained independently", "P2 existing adaptive teaching"],
            "horizon": HORIZON,
            "training_seeds": TRAIN_SEEDS,
            "evaluation_seeds": EVAL_SEEDS,
            "calibration_seeds": CALIBRATION_SEEDS,
            "initial_competence": setup["organization"].competence_initial,
            "requirements": {"x": setup["environment"].emissions["x"].problems[0].requirements,
                             "y": setup["environment"].emissions["y"].problems[0].requirements},
            "MIS_eta": setup["learning"].eta,
            "teaching_efficacy": setup["efficacy"].values,
            "transfer_rate": setup["teaching_parameters"].transfer_rate,
            "teaching_effort": setup["policy_parameters"].effort,
            "resource_budget": setup["organization"].collective_effort_budget,
            "individual_effort_limits": setup["organization"].effort_limits,
            "demand_process": "C5 Markov: initial x/y=.5/.5; stay=.9; switch=.1",
            "policy_information": "same existing perfect-information setting as prior S4 transfer study; no policy rules changed",
            "selected_P1_relation": selected_relation,
            "P1_training_mean_CES_by_relation": {
                "/".join(relation): mean(values) for relation, values in fixed_scores.items()
            },
            "formula_changes": "none; only scenario parameter eta[B,y], y requirement, horizon and existing resources configuration are calibration dimensions; final horizon/resources equal prior (24, budget 2)",
        },
        "calibration": calibration,
        "summary": summaries,
        "paired_differences": paired,
        "feasible_teaching_opportunities": feasible_opportunities,
        "per_seed": per_seed,
        "period_traces": traces,
        "artifacts": {
            "runner": "experiments/run_hls_s4_transfer_opportunities.py",
            "tests": "tests/test_hls_s4_transfer_opportunities.py",
            "reference_runner": "experiments/run_hls_s4_transfer_interaction.py",
        },
    }


def main(output: Path = RESULT_PATH):
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing result: {output}")
    payload = evaluate()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({
        "output": str(output),
        "selected_eta_B_y": payload["calibration"]["selected_eta_B_y"],
        "paired_CES": {name: result["ces"] for name, result in payload["paired_differences"].items()},
        "lessons": {name: result["lessons"] for name, result in payload["summary"].items()},
    }, indent=2))


if __name__ == "__main__":
    main()
