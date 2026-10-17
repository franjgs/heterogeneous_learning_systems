"""Reproducible engineering demonstration of integrated HLS Laboratory v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.hls_lab_dynamic import LearningProfile  # noqa: E402
from hls.hls_lab_v1 import make_team, ProblemSpec  # noqa: E402
from hls.hls_lab_v1_integrated import (  # noqa: E402
    IntegratedProblem,
    P0ProductionOnly,
    P1FixedTeaching,
    P2AdaptiveTeaching,
    TeachingEfficacy,
    TeachingParameters,
    compare_integrated_policies,
)


INITIAL_A = make_team(((0.20, 0.40), (0.10, 0.05), (0.95, 0.10)))
INITIAL_B = make_team(((0.60, 0.10), (0.60, 0.20), (0.95, 0.40)))
LEARNING = LearningProfile(((0.04, 0.0001), (0.04, 0.0001), (0.04, 0.0001)))
EFFICACY = TeachingEfficacy((
    ((0.0, 0.0), (0.10, 0.95), (0.10, 0.20)),
    ((0.10, 0.10), (0.0, 0.0), (0.10, 0.10)),
    ((0.10, 0.10), (0.08, 0.08), (0.0, 0.0)),
))
PARAMETERS = TeachingParameters(
    transfer_rate=0.8,
    effort=0.25,
    outcome_noise_sd=0.002,
    production_observation_noise_sd=0.01,
    competence_grid_points=101,
    competence_prior_variance=0.04,
    efficacy_prior_mean=0.5,
    efficacy_threshold=0.35,
    target_competence=0.60,
)


def _problem(problem_id: str, requirement: tuple[float, float], demand: str) -> IntegratedProblem:
    return IntegratedProblem(ProblemSpec(problem_id, requirement, 3.0,
                                         max_effort_per_expert=1.25,
                                         resource_cost_per_unit=0.2),
                             demand_label=demand)


def run_demo() -> dict[str, object]:
    # Predeclared changing/recurrent schedule: skill 1 demand, a skill 0
    # interruption, then a return to skill 1. The same tuple is passed to all.
    beneficial = tuple(
        [_problem("skill-1", (0.0, 0.60), "early-skill-1") for _ in range(2)]
        + [_problem("skill-0", (0.75, 0.0), "interruption-skill-0") for _ in range(2)]
        + [_problem("skill-1", (0.0, 0.60), "return-skill-1") for _ in range(30)]
    )
    # Short, skill-0-only demand is a negative control for a fixed lesson in
    # skill 1; adaptive P2 is only offered a low-efficacy skill-0 relationship.
    harmful = tuple(_problem("skill-0", (2.0, 0.0), "stationary-skill-0") for _ in range(4))
    policies_a = (P0ProductionOnly(), P1FixedTeaching((0, 1, 1)),
                  P2AdaptiveTeaching(((0, 1, 1),)))
    policies_b = (P0ProductionOnly(), P1FixedTeaching((0, 1, 1)),
                  P2AdaptiveTeaching(((2, 1, 0),)))

    def summarize(name, initial_team, sequence, policies, seed):
        runs = compare_integrated_policies(
            initial_team, sequence, policies, learning=LEARNING,
            teaching_efficacy=EFFICACY, parameters=PARAMETERS,
            individual_learning=True, seed=seed,
        )
        return {
            "scenario": name,
            "seed": seed,
            "shared_problem_ids": [item.problem.problem_id for item in sequence],
            "policies": [{
                "policy": run.policy,
                "ces_reward_sum": sum(row.ces_reward for row in run.records),
                "successes": sum(row.functional_result.success for row in run.records),
                "normalized_deficit_sum": sum(row.functional_result.normalized_deficit for row in run.records),
                "resource_cost_sum": sum(row.resource_cost for row in run.records),
                "teaching_periods": sum(row.action.teaching is not None for row in run.records),
                "final_real_competencies": run.final_team.real_matrix,
                "final_estimated_competencies": run.final_team.estimated_matrix,
                "observed_relations": [
                    {"relation": row.relation, "count": row.count, "mean": row.mean}
                    for row in run.final_organization.efficacy
                ],
                "trace": [{
                    "period": row.period,
                    "demand": row.demand_label,
                    "teaching": None if row.action.teaching is None else {
                        "instructor": row.action.teaching.instructor,
                        "learner": row.action.teaching.learner,
                        "skill": row.action.teaching.capability,
                    },
                    "success": row.functional_result.success,
                    "outputs": row.outputs,
                } for row in run.records],
            } for run in runs],
        }

    return {
        "protocol": "HLS-LAB-V1-INTEGRATED engineering demo v1",
        "note": "Deterministic, common-sequence functional demonstration; not scientific evidence.",
        "individual_learning": True,
        "initial_real_competencies": {"A": INITIAL_A.real_matrix, "B": INITIAL_B.real_matrix},
        "learning_rates": LEARNING.eta,
        "transfer_parameters": {
            "transfer_rate": PARAMETERS.transfer_rate,
            "effort_per_participant": PARAMETERS.effort,
            "observation_noise_sd": PARAMETERS.outcome_noise_sd,
        },
        "scenarios": [
            summarize("A_LONG_RECURRENT_DEMAND", INITIAL_A, beneficial, policies_a, 20261015),
            summarize("B_SHORT_MISMATCHED_DEMAND", INITIAL_B, harmful, policies_b, 20261016),
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), sort_keys=True, indent=2))
