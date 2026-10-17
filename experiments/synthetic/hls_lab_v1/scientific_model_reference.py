"""Generate the small Phase 5A diagnostic reference trace.

This is a model-behavior fixture, not a scientific campaign. From the
repository root run ``python experiments/synthetic/hls_lab_v1/scientific_model_reference.py``.
It writes a deterministic JSON evidence record under results/diagnostics.
"""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from hls.hls_lab_nk_environment import DemandRegimeNK, ExogenousEnvironmentConfigNK
from hls.hls_lab_nk_execution import NKEnvironmentRunResult, run_nk_production_sequence
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK
from hls.hls_lab_nk_policies import P2AdaptiveTeachingNK, TeachingPolicyParametersNK
from hls.hls_lab_nk_estimation import CompetenceObservationParametersNK
from hls.hls_lab_nk_teaching import TeachingEfficacyNK, TeachingParametersNK
from hls.synthetic.c5 import MarkovTaskDemand

REFERENCE_SOURCE_COMMIT = "e8e115030e064df23f07f1b5824264f97513099a"


def build_reference_evidence() -> dict:
    """Run and return an independently reproducible 2-agent × 2-skill trace."""
    agent_ids = ("A", "B")
    skill_ids = ("x", "y")
    actual = ((0.85, 0.15), (0.20, 0.20))
    estimated = ((0.75, 0.25), (0.30, 0.30))
    organization = OrganizationConfigNK(
        agent_ids, skill_ids, actual, (1.0, 1.0), 2.0, estimated,
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
        agent_ids, skill_ids,
        (
            ((0.0, 0.0), (0.75, 0.80)),
            ((0.70, 0.65), (0.0, 0.0)),
        ),
    )
    learning = LearningProfileNK(((0.20, 0.15), (0.12, 0.18)))
    policy = P2AdaptiveTeachingNK((("A", "B", "y"), ("B", "A", "x")))
    policy_parameters = TeachingPolicyParametersNK(
        effort=0.25, efficacy_prior_mean=0.5,
        efficacy_threshold=0.35, target_competence=0.95,
    )
    effort_choices = tuple(
        ((0.0, 0.0), (0.5, 0.0), (0.0, 0.5), (1.0, 0.0),
         (0.0, 1.0), (0.5, 0.5))
        for _ in agent_ids
    )
    observation_parameters = CompetenceObservationParametersNK(
        production_observation_noise_sd=0.02,
        outcome_noise_sd=0.0,
        competence_grid_points=101,
        competence_prior_variance=0.04,
    )
    environment_seed = 24016
    information_seed = 24017
    result = run_nk_production_sequence(
        organization,
        max_candidates=216,
        environment=environment,
        environment_seed=environment_seed,
        per_agent_effort_choices=effort_choices,
        policy=policy,
        policy_parameters=policy_parameters,
        individual_learning=True,
        organizational_learning=True,
        learning_profile=learning,
        teaching_enabled=True,
        teaching_efficacy=efficacy,
        teaching_parameters=TeachingParametersNK(transfer_rate=0.4),
        information_mode="imperfect",
        observation_parameters=observation_parameters,
        information_seed=information_seed,
    )
    if not isinstance(result, NKEnvironmentRunResult):
        raise AssertionError("generated environment did not return environment wrapper")
    execution = result.execution
    return {
        "purpose": "diagnostic_reference_trace_not_campaign_data",
        "software_commit": REFERENCE_SOURCE_COMMIT,
        "runtime": {"python": __import__("sys").version.split()[0]},
        "configuration": {
            "geometry": {"agent_ids": agent_ids, "skill_ids": skill_ids},
            "initial_actual_competence": actual,
            "initial_estimated_competence": estimated,
            "effort_limits": (1.0, 1.0),
            "collective_budget": 2.0,
            "demand": {
                "process": "first-order Markov",
                "initial_distribution": {"x": 1.0, "y": 0.0},
                "transitions": {"x": {"x": 0.0, "y": 1.0},
                                "y": {"x": 1.0, "y": 0.0}},
                "horizon": 4,
                "environment_seed": environment_seed,
                "emissions": {
                    "x": {"problem_id": "task-x", "requirements": problem_x.requirements,
                          "ces_weights": problem_x.ces_weights},
                    "y": {"problem_id": "task-y", "requirements": problem_y.requirements,
                          "ces_weights": problem_y.ces_weights},
                },
            },
            "policy": {"name": policy.name, "relations": policy.relations,
                       "parameters": asdict(policy_parameters)},
            "MIS_v2": {"enabled": True, "eta": learning.eta},
            "teaching": {"enabled": True, "efficacy": efficacy.values,
                         "transfer_rate": 0.4, "one_event_maximum": True},
            "information": {"mode": "imperfect", "seed": information_seed,
                            "parameters": asdict(observation_parameters)},
            "per_agent_effort_choices": effort_choices,
            "candidate_limit": 216,
        },
        "environment_trajectory": {
            "seed": result.trajectory.seed,
            "latent_states": result.trajectory.latent_states,
            "regime_labels": result.trajectory.regime_labels,
            "problems": [asdict(item) for item in result.trajectory.problems],
        },
        "execution": asdict(execution),
    }


def main() -> None:
    evidence = build_reference_evidence()
    output = Path("results/diagnostics/hls_scientific_model_dossier/reference_trace.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(output)


if __name__ == "__main__":
    main()
