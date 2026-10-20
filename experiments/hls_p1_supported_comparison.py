"""Bounded HLS-P1 comparison using the existing N×K/MIS-v2 reference.

This is a policy-path diagnostic, not the complete HLS-P1 experiment:
FIXED-OPT and an anticipatory MIS-v2 policy do not exist in this route.
It reuses the published-in-repository four-period S4 diagnostic configuration
and executes only the existing P0/P1/P2 rules on a common frozen path.

Run from the repository root with ``PYTHONPATH=src python
experiments/hls_p1_supported_comparison.py``. Result creation is exclusive;
the script refuses to overwrite an existing artifact.
"""

from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path
import sys

from hls.hls_lab_nk_environment import DemandRegimeNK, ExogenousEnvironmentConfigNK
from hls.hls_lab_nk_execution import NKEnvironmentRunResult, NKInformationRunResult, run_nk_production_sequence
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK
from hls.hls_lab_nk_policies import (
    P0ProductionOnlyPolicyNK,
    P1FixedTeachingNK,
    P2AdaptiveTeachingNK,
    TeachingPolicyParametersNK,
)
from hls.hls_lab_nk_estimation import CompetenceObservationParametersNK
from hls.hls_lab_nk_teaching import TeachingEfficacyNK, TeachingParametersNK
from hls.synthetic.c5 import MarkovTaskDemand, StationaryTaskDemand


OUTPUT = Path("results/experiments/hls_p1_supported_comparison/results.json")
AGENTS = ("A", "B")
SKILLS = ("x", "y")
RELATIONS = (("A", "B", "y"), ("B", "A", "x"))
ENVIRONMENT_SEED = 24016
INFORMATION_SEED = 24017


def _configuration():
    actual = ((0.85, 0.15), (0.20, 0.20))
    estimated = ((0.75, 0.25), (0.30, 0.30))
    organization = OrganizationConfigNK(
        AGENTS, SKILLS, actual, (1.0, 1.0), 2.0, estimated,
    )
    problem_x = ProblemSpecNK("task-x", (1.10, 0.10), 2.0, (0.5, 0.5))
    problem_y = ProblemSpecNK("task-y", (0.10, 1.20), 2.0, (0.5, 0.5))
    environment = ExogenousEnvironmentConfigNK(
        MarkovTaskDemand(
            {"x": 1.0, "y": 0.0},
            {"x": {"x": 0.0, "y": 1.0}, "y": {"x": 1.0, "y": 0.0}},
        ),
        {
            "x": DemandRegimeNK("x-regime", (problem_x,), (1.0,)),
            "y": DemandRegimeNK("y-regime", (problem_y,), (1.0,)),
        },
        horizon=4,
        resource_budget=2.0,
    )
    efficacy = TeachingEfficacyNK(
        AGENTS, SKILLS,
        (
            ((0.0, 0.0), (0.75, 0.80)),
            ((0.70, 0.65), (0.0, 0.0)),
        ),
    )
    learning = LearningProfileNK(((0.20, 0.15), (0.12, 0.18)))
    parameters = TeachingPolicyParametersNK(
        effort=0.25, efficacy_prior_mean=0.5,
        efficacy_threshold=0.35, target_competence=0.95,
    )
    effort_choices = tuple(
        ((0.0, 0.0), (0.5, 0.0), (0.0, 0.5), (1.0, 0.0),
         (0.0, 1.0), (0.5, 0.5))
        for _ in AGENTS
    )
    observation = CompetenceObservationParametersNK(
        production_observation_noise_sd=0.02, outcome_noise_sd=0.0,
        competence_grid_points=101, competence_prior_variance=0.04,
    )
    policies = (
        P0ProductionOnlyPolicyNK(),
        P1FixedTeachingNK(RELATIONS[0]),
        P2AdaptiveTeachingNK(RELATIONS),
    )
    return (organization, environment, efficacy, learning, parameters,
            effort_choices, observation, policies)


def _summarize(result: NKInformationRunResult) -> dict:
    records = result.records
    return {
        "policy_id": records[0].policy_name,
        "periods": len(records),
        "cumulative_ces_reward": sum(row.production.ces_reward for row in records),
        "functional_success_periods": sum(row.production.functional_result.success for row in records),
        "cumulative_normalized_deficit": sum(
            row.production.functional_result.normalized_deficit for row in records
        ),
        "productive_effort": sum(row.productive_effort_used for row in records),
        "teaching_effort_charge": sum(row.teaching_resource_used for row in records),
        "total_effort_charge": sum(row.total_resource_used for row in records),
        "final_true_competence": result.final_state.competence_real,
        "periods_with_teaching": sum(row.action.teaching is not None for row in records),
        "periods_with_mis_learning": sum(
            any(value > 0.0 for row in record.mis_increment for value in row)
            for record in records
        ),
        "period_trace": [
            {
                "period": row.period,
                "task": row.production.problem_id,
                "action": asdict(row.action),
                "reward": row.production.ces_reward,
                "success": row.production.functional_result.success,
                "normalized_deficit": row.production.functional_result.normalized_deficit,
                "competence_before": row.competence_actual_before,
                "competence_after_mis": row.competence_after_mis,
                "competence_after_all_transitions": row.competence_actual_after,
                "competence_estimate_before": row.competence_estimated_before,
                "mis_increment": row.mis_increment,
                "teaching_increment": row.teaching_increment,
                "resource_used": row.total_resource_used,
                "policy_memory_before": [asdict(item) for item in row.efficacy_memory_before],
                "policy_memory_after": [asdict(item) for item in row.efficacy_memory_after],
            }
            for row in records
        ],
    }


def build_results() -> dict:
    (organization, environment, efficacy, learning, policy_parameters,
     effort_choices, observation, policies) = _configuration()
    scenarios = {
        "stationary_mis_v2": (
            replace(environment, process=StationaryTaskDemand({"x": 0.5, "y": 0.5})),
            True, True, learning,
        ),
        "alternating_mis_v2": (environment, True, True, learning),
        "alternating_no_development": (environment, False, False, learning),
    }
    scenario_runs = {}
    for scenario_id, (scenario_environment, individual_learning,
                      teaching_enabled, scenario_learning) in scenarios.items():
        runs = {}
        frozen_path = None
        for policy in policies:
            result = run_nk_production_sequence(
                organization,
                max_candidates=216,
                environment=scenario_environment,
                environment_seed=ENVIRONMENT_SEED,
                per_agent_effort_choices=effort_choices,
                policy=policy,
                policy_parameters=policy_parameters,
                individual_learning=individual_learning,
                organizational_learning=True,
                learning_profile=scenario_learning,
                teaching_enabled=teaching_enabled,
                teaching_efficacy=efficacy,
                teaching_parameters=TeachingParametersNK(transfer_rate=0.4),
                information_mode="imperfect",
                observation_parameters=observation,
                information_seed=INFORMATION_SEED,
            )
            if not isinstance(result, NKEnvironmentRunResult) or not isinstance(
                result.execution, NKInformationRunResult
            ):
                raise AssertionError("expected generated-path information-aware N×K execution")
            trajectory = (result.trajectory.latent_states,
                          tuple(asdict(problem).items() for problem in result.trajectory.problems))
            if frozen_path is None:
                frozen_path = trajectory
            elif trajectory != frozen_path:
                raise AssertionError("policies did not receive identical exogenous trajectories")
            runs[policy.name] = _summarize(result.execution)

        baseline = runs["P0_PRODUCTION_ONLY"]["cumulative_ces_reward"]
        for row in runs.values():
            row["ces_difference_vs_p0"] = row["cumulative_ces_reward"] - baseline
        scenario_runs[scenario_id] = {
            "conditions": {
                "demand_process": "IID stationary 50/50" if scenario_id == "stationary_mis_v2"
                                  else "deterministic Markov alternation x,y,x,y",
                "individual_learning": individual_learning,
                "teaching_enabled": teaching_enabled,
                "eta": scenario_learning.eta,
            },
            "common_frozen_trajectory_verified": True,
            "latent_demand_path": list(result.trajectory.latent_states),
            "realized_problem_ids": [p.problem_id for p in result.trajectory.problems],
            "runs": runs,
        }
    return {
        "experiment_id": "HLS-P1-supported-policy-comparison",
        "title": "Bounded existing-policy comparison on the S4 N×K/MIS-v2 diagnostic",
        "status": "EXECUTED_BOUNDED_SUBCOMPARISON_NOT_FULL_HLS_P1",
        "scientific_question_coverage": (
            "Does not test FIXED-OPT or anticipatory optimization, nor vary demand persistence. "
            "Reports existing P0/P1/P2 behavior on the already-defined S4 deterministic alternating path."
        ),
        "configuration_source": "experiments/synthetic/hls_lab_v1/scientific_model_reference.py S4",
        "randomness": {
            "environment_seed": ENVIRONMENT_SEED,
            "information_seed": INFORMATION_SEED,
            "policy_randomness": "none in these P0/P1/P2 rules",
            "common_random_numbers": "same exogenous seed and frozen demand path within each scenario; same indexed information seed",
        },
        "policies": {
            "P0_PRODUCTION_ONLY": "reactive current-view production rule; no teaching actions",
            "P1_FIXED_TEACHING": "fixed A→B on skill y relation; production remains reactive",
            "P2_ADAPTIVE_TEACHING": "existing relation-memory heuristic over A→B/y and B→A/x; not anticipatory",
            "unavailable": {
                "FIXED_OPT": "No globally optimized fixed organization is implemented in the N×K/MIS-v2 route.",
                "HLS_ANTICIPATORY": "No exact anticipatory policy is implemented for the N×K/MIS-v2 transition. G0/RQ0 HLS exact uses a different A1 model."
            },
        },
        "model": {
            "agents": organization.agent_ids,
            "skills": organization.skill_ids,
            "initial_true_competence": organization.competence_initial,
            "initial_estimated_competence": organization.competence_estimated_initial,
            "individual_effort_limits": organization.effort_limits,
            "collective_effort_budget": organization.collective_effort_budget,
            "horizon": environment.horizon,
            "demand_processes": "existing S4 deterministic Markov alternation; stationary control uses existing IID StationaryTaskDemand at 0.5/0.5",
            "task_requirements": {
                "task-x": (1.10, 0.10),
                "task-y": (0.10, 1.20),
            },
            "mis_v2_eta": learning.eta,
            "teaching_efficacy": efficacy.values,
            "transfer_rate": 0.4,
            "teaching_effort": policy_parameters.effort,
            "observation_mode": "imperfect, same coordinate-indexed observation seed across policies",
            "observation_parameters": asdict(observation),
            "reward": "period CES production; separately reports functional success and deficit",
        },
        "interpretation_limits": [
            "P1 is not a fixed task-to-agent organization: only its teaching relation is fixed; production is state-responsive.",
            "P0 has no teaching actions in its policy action catalog; P1/P2 do. Physical budgets and accounting are shared, but action spaces differ by policy class.",
            "Only stationary IID versus deterministic perfect alternation is contrasted; this does not estimate a demand-persistence response curve.",
            "No Monte Carlo uncertainty estimate or population inference is supported.",
            "This subcomparison cannot answer the HLS-P1 question about anticipatory development versus FIXED-OPT and REACTIVE."
        ],
        "scenario_runs": scenario_runs,
    }


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite existing pilot result: {OUTPUT}")
    payload = build_results()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
