"""Bounded N×K MIS-v2 × directed-teaching experiment.

The design was fixed in the cumulative engineering record before evaluation.
Run from the repository root with PYTHONPATH=src python experiments/run_hls_s4_transfer_interaction.py.
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
from hls.hls_lab_nk_estimation import CompetenceObservationParametersNK
from hls.hls_lab_nk_execution import NKInformationRunResult, run_nk_production_sequence
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK
from hls.hls_lab_nk_policies import (
    P0ProductionOnlyPolicyNK,
    P1FixedTeachingNK,
    P2AdaptiveTeachingNK,
    TeachingPolicyParametersNK,
    enumerate_feasible_joint_actions_nk,
)
from hls.hls_lab_nk_teaching import JointActionNK, TeachingActionNK, TeachingEfficacyNK, TeachingParametersNK
from hls.synthetic.c5 import MarkovTaskDemand


RESULT_PATH = Path("results/experiments/hls_s4_transfer_interaction/results.json")
TRAIN_SEEDS = tuple(range(42000, 42020))
EVAL_SEEDS = tuple(range(43000, 43030))
HORIZON = 24
CELLS = (("00", False, False), ("10", True, False),
         ("01", False, True), ("11", True, True))
RELATIONS = (("A", "B", "x"), ("A", "B", "y"),
             ("B", "A", "x"), ("B", "A", "y"))


def design():
    organization = OrganizationConfigNK(
        ("A", "B"), ("x", "y"), ((.85, .15), (.20, .20)),
        (1.0, 1.0), 2.0,
    )
    x = ProblemSpecNK("task-x", (.35, 0.0), 2.0, (1.0, 0.0))
    y = ProblemSpecNK("task-y", (0.0, .40), 2.0, (0.0, 1.0))
    environment = ExogenousEnvironmentConfigNK(
        MarkovTaskDemand(
            {"x": .5, "y": .5},
            {"x": {"x": .9, "y": .1}, "y": {"x": .1, "y": .9}},
        ),
        {"x": DemandRegimeNK("x", (x,), (1.0,)),
         "y": DemandRegimeNK("y", (y,), (1.0,))},
        horizon=HORIZON, resource_budget=2.0,
    )
    efficacy = TeachingEfficacyNK(
        organization.agent_ids, organization.skill_ids,
        (((0.0, 0.0), (.75, .80)),
         ((.70, .65), (0.0, 0.0))),
    )
    zero_efficacy = TeachingEfficacyNK(
        organization.agent_ids, organization.skill_ids,
        (((0.0, 0.0), (0.0, 0.0)),
         ((0.0, 0.0), (0.0, 0.0))),
    )
    effort_choices = tuple(
        ((0.0, 0.0), (.5, 0.0), (0.0, .5), (1.0, 0.0),
         (0.0, 1.0), (.5, .5))
        for _ in organization.agent_ids
    )
    return {
        "organization": organization,
        "environment": environment,
        "efficacy": efficacy,
        "zero_efficacy": zero_efficacy,
        "learning": LearningProfileNK(((.20, .15), (.12, .18))),
        "teaching_parameters": TeachingParametersNK(transfer_rate=.4),
        "policy_parameters": TeachingPolicyParametersNK(
            effort=.25, efficacy_prior_mean=.5,
            efficacy_threshold=.35, target_competence=.95,
        ),
        "observation_parameters": CompetenceObservationParametersNK(
            production_observation_noise_sd=0.0,
            outcome_noise_sd=0.0,
            competence_grid_points=101,
            competence_prior_variance=.04,
        ),
        "effort_choices": effort_choices,
    }


def problems_for_seed(setup, seed: int):
    return generate_environment_trajectory_nk(setup["environment"], seed=seed).problems


def controlled_actions(problems):
    lesson = TeachingActionNK("A", "B", "y", .25)
    return tuple(JointActionNK(
        ((.5, 0.0), (0.0, .5)) if problem.problem_id == "task-x"
        else ((0.0, .5), (0.0, .5)),
        lesson,
    ) for problem in problems)


def check_action_catalogs(setup):
    org = setup["organization"]
    for problem in (setup["environment"].emissions["x"].problems[0],
                    setup["environment"].emissions["y"].problems[0]):
        kwargs = dict(max_candidates=216, teaching_enabled=True,
                      teaching_effort=.25,
                      per_agent_effort_choices=setup["effort_choices"])
        actual = enumerate_feasible_joint_actions_nk(
            org, problem, teaching_efficacy=setup["efficacy"], **kwargs)
        disabled = enumerate_feasible_joint_actions_nk(
            org, problem, teaching_efficacy=setup["zero_efficacy"], **kwargs)
        assert actual == disabled
        assert controlled_actions((problem,))[0] in actual


def execute(setup, problems, cell: str, *, policy=None, actions=None) -> NKInformationRunResult:
    row = next((entry for entry in CELLS if entry[0] == cell), None)
    if row is None:
        raise ValueError(f"unknown factorial cell {cell}")
    _, mis_enabled, transfer_enabled = row
    result = run_nk_production_sequence(
        setup["organization"], tuple(problems),
        max_candidates=216,
        per_agent_effort_choices=setup["effort_choices"],
        individual_learning=mis_enabled,
        learning_profile=setup["learning"],
        teaching_enabled=True,
        teaching_efficacy=(setup["efficacy"] if transfer_enabled
                           else setup["zero_efficacy"]),
        teaching_parameters=setup["teaching_parameters"],
        policy_parameters=setup["policy_parameters"],
        observation_parameters=setup["observation_parameters"],
        organizational_learning=True,
        policy=policy,
        explicit_actions=actions,
        information_mode="perfect",
    )
    assert isinstance(result, NKInformationRunResult)
    return result


def summarize(result: NKInformationRunResult):
    records = result.records
    return {
        "ces": sum(row.production.ces_reward for row in records),
        "success": sum(row.production.functional_result.success for row in records),
        "deficit": sum(row.production.functional_result.normalized_deficit for row in records),
        "productive_effort": sum(row.productive_effort_used for row in records),
        "teaching_effort": sum(row.teaching_resource_used for row in records),
        "total_effort": sum(row.total_resource_used for row in records),
        "lessons": sum(row.action.teaching is not None for row in records),
        "final_competence": result.final_state.competence_real,
    }


def trace(result: NKInformationRunResult):
    return [{
        "t": row.period,
        "problem": row.production.problem_id,
        "action": asdict(row.action),
        "ces": row.production.ces_reward,
        "success": row.production.functional_result.success,
        "deficit": row.production.functional_result.normalized_deficit,
        "competence_before": row.competence_actual_before,
        "competence_after_mis": row.competence_after_mis,
        "competence_after": row.competence_actual_after,
        "mis_increment": row.mis_increment,
        "teaching_increment": row.teaching_increment,
        "productive_effort": row.productive_effort_used,
        "teaching_effort": row.teaching_resource_used,
    } for row in result.records]


def interval(values):
    samples = tuple(float(value) for value in values)
    center = mean(samples)
    radius = student_t.ppf(.975, len(samples) - 1) * stdev(samples) / len(samples)**.5
    return {"mean": center, "ci95": [center - radius, center + radius]}


def select_fixed_relation(setup):
    training = {relation: [] for relation in RELATIONS}
    for seed in TRAIN_SEEDS:
        problems = problems_for_seed(setup, seed)
        for relation in RELATIONS:
            run = execute(setup, problems, "11", policy=P1FixedTeachingNK(relation))
            training[relation].append(summarize(run)["ces"])
    selected = max(RELATIONS, key=lambda relation: mean(training[relation]))
    return selected, {
        "/".join(relation): mean(training[relation]) for relation in RELATIONS
    }


def factorial_contrast(seed_rows, metric):
    return interval(
        rows["11"][metric] - rows["10"][metric]
        - rows["01"][metric] + rows["00"][metric]
        for rows in seed_rows
    )


def aggregate_rows(seed_rows):
    return {
        cell: {
            metric: interval(rows[cell][metric] for rows in seed_rows)
            for metric in ("ces", "success", "deficit", "productive_effort",
                           "teaching_effort", "total_effort", "lessons")
        }
        for cell, _, _ in CELLS
    }


def evaluate_design():
    setup = design()
    check_action_catalogs(setup)
    fixed_relation, training_scores = select_fixed_relation(setup)
    policies = {
        "P0": P0ProductionOnlyPolicyNK(),
        "P1_train_selected": P1FixedTeachingNK(fixed_relation),
        "P2": P2AdaptiveTeachingNK(RELATIONS),
    }
    controlled = []
    closed = {name: [] for name in policies}
    example = {"seed": EVAL_SEEDS[0], "controlled": {}, "closed": {}}
    for seed in EVAL_SEEDS:
        problems = problems_for_seed(setup, seed)
        actions = controlled_actions(problems)
        controlled_seed = {}
        controlled_runs = {}
        for cell, _, _ in CELLS:
            run = execute(setup, problems, cell, actions=actions)
            controlled_runs[cell] = run
            controlled_seed[cell] = summarize(run)
        # A disabled transition must not change action cost or feasibility.
        resource_paths = [tuple((row.action, row.total_resource_used,
                                 row.teaching_resource_used)
                                for row in run.records)
                          for run in controlled_runs.values()]
        assert all(path == resource_paths[0] for path in resource_paths)
        controlled.append(controlled_seed)
        if seed == EVAL_SEEDS[0]:
            example["controlled"] = {cell: trace(run) for cell, run in controlled_runs.items()}

        for name, policy in policies.items():
            policy_seed = {}
            for cell, _, _ in CELLS:
                run = execute(setup, problems, cell, policy=policy)
                assert tuple(row.production.problem_id for row in run.records) == tuple(
                    problem.problem_id for problem in problems)
                policy_seed[cell] = summarize(run)
                if seed == EVAL_SEEDS[0]:
                    example["closed"].setdefault(name, {})[cell] = trace(run)
            closed[name].append(policy_seed)

    metrics = ("ces", "success", "deficit", "total_effort")
    contrasts = {
        "controlled": {metric: factorial_contrast(controlled, metric) for metric in metrics},
        "closed": {
            name: {metric: factorial_contrast(rows, metric) for metric in metrics}
            for name, rows in closed.items()
        },
    }
    comparisons = {
        cell: {
            "P2_minus_P1_ces": interval(
                closed["P2"][index][cell]["ces"]
                - closed["P1_train_selected"][index][cell]["ces"]
                for index in range(len(EVAL_SEEDS))
            ),
            "P2_minus_P0_ces": interval(
                closed["P2"][index][cell]["ces"]
                - closed["P0"][index][cell]["ces"]
                for index in range(len(EVAL_SEEDS))
            ),
        }
        for cell, _, _ in CELLS
    }
    return {
        "experiment": "HLS-S4-MISv2-teaching-interaction",
        "design": {
            "cells": CELLS,
            "train_seeds": TRAIN_SEEDS,
            "eval_seeds": EVAL_SEEDS,
            "horizon": HORIZON,
            "organization": asdict(setup["organization"]),
            "environment": {
                "process": "C5 first-order Markov x/y; initial .5/.5; stay .9; switch .1",
                "problem_x": asdict(setup["environment"].emissions["x"].problems[0]),
                "problem_y": asdict(setup["environment"].emissions["y"].problems[0]),
            },
            "eta": setup["learning"].eta,
            "efficacy": setup["efficacy"].values,
            "transfer_rate": setup["teaching_parameters"].transfer_rate,
            "policy_parameters": asdict(setup["policy_parameters"]),
            "fixed_relation": fixed_relation,
            "fixed_training_mean_ces": training_scores,
            "information_mode": "perfect",
        },
        "controlled": {"per_seed": controlled, "summary": aggregate_rows(controlled)},
        "closed": {
            name: {"per_seed": rows, "summary": aggregate_rows(rows)}
            for name, rows in closed.items()
        },
        "interactions": contrasts,
        "paired_policy_differences": comparisons,
        "example_trace": example,
    }


def main(output: Path = RESULT_PATH):
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing result: {output}")
    payload = evaluate_design()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({
        "output": str(output),
        "fixed_relation": payload["design"]["fixed_relation"],
        "controlled_interaction_ces": payload["interactions"]["controlled"]["ces"],
        "closed_ces_J11": {
            name: data["summary"]["11"]["ces"]
            for name, data in payload["closed"].items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
