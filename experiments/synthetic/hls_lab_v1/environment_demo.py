"""Small reproducible demo of exogenous, regime-switching demand."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.hls_lab_dynamic import DemandRegime, LearningProfile  # noqa: E402
from hls.hls_lab_v1 import make_team  # noqa: E402
from hls.hls_lab_v1_environment import (  # noqa: E402
    ExogenousEnvironmentConfig,
    generate_environment_trajectory,
)
from hls.hls_lab_v1_integrated import (  # noqa: E402
    P0ProductionOnly,
    P1FixedTeaching,
    P2AdaptiveTeaching,
    TeachingEfficacy,
    TeachingParameters,
    compare_integrated_policies,
)
from hls.synthetic.c5 import MarkovTaskDemand  # noqa: E402


def run_demo() -> dict[str, object]:
    process = MarkovTaskDemand(
        {"regime_0": 1.0, "regime_1": 0.0},
        {"regime_0": {"regime_0": 0.0, "regime_1": 1.0},
         "regime_1": {"regime_0": 0.0, "regime_1": 1.0}},
    )
    config = ExogenousEnvironmentConfig(
        process,
        {
            "regime_0": DemandRegime("specialization", ((0.0, 0.6),), (1.0,)),
            "regime_1": DemandRegime("complementarity", ((0.45, 0.45),), (1.0,)),
        },
        horizon=12,
        resource_budget=3.0,
    )
    trajectory = generate_environment_trajectory(config, seed=20261015)
    team = make_team(((0.9, 0.1), (0.1, 0.25), (0.35, 0.8)))
    efficacy = TeachingEfficacy((
        ((0.0, 0.0), (0.1, 0.85), (0.2, 0.2)),
        ((0.1, 0.1), (0.0, 0.0), (0.2, 0.2)),
        ((0.2, 0.2), (0.2, 0.2), (0.0, 0.0)),
    ))
    policies = (
        P0ProductionOnly(),
        P1FixedTeaching((0, 1, 1)),
        P2AdaptiveTeaching(((0, 1, 1), (2, 1, 0))),
    )
    runs = compare_integrated_policies(
        team,
        trajectory.problems,
        policies,
        learning=LearningProfile(((0.04, 0.04), (0.02, 0.03), (0.03, 0.02))),
        teaching_efficacy=efficacy,
        parameters=TeachingParameters(
            transfer_rate=0.7,
            effort=0.25,
            outcome_noise_sd=0.01,
            production_observation_noise_sd=0.01,
        ),
        individual_learning=True,
        seed=20261016,
    )
    return {
        "protocol": "HLS-LAB-V1 exogenous-regime demo v1",
        "seed": trajectory.seed,
        "note": "The frozen problem tuple is shared by policies; latent states are experimenter-only diagnostics.",
        "latent_states_experimenter_only": trajectory.latent_states,
        "problem_requirements": [p.problem.requirements for p in trajectory.problems],
        "policies": [{
            "name": run.policy,
            "ces_reward_sum": sum(row.ces_reward for row in run.records),
            "successes": sum(row.functional_result.success for row in run.records),
            "deficit_sum": sum(row.functional_result.normalized_deficit for row in run.records),
            "teaching_periods": sum(row.action.teaching is not None for row in run.records),
            "final_real_competencies": run.final_team.real_matrix,
            "trace": [{
                "period": row.period,
                "problem_id": row.problem_id,
                "requirements": row.requirements,
                "action": row.production_action_id,
                "teaching_relation": (None if row.action.teaching is None
                                      else row.action.teaching.relation),
                "outputs": row.outputs,
                "success": row.functional_result.success,
                "competence_after": row.competence_real_after,
            } for row in run.records],
        } for run in runs],
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), sort_keys=True, indent=2))
