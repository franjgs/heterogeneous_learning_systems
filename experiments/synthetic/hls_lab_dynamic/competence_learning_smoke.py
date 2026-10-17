"""Bounded functional check for individual competence observations.

Engineering verification only; this is not a scientific campaign or a
comparison intended to rank organizations.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from hls.discover_v0 import THETA_1
from hls.hls_lab_dynamic import (
    CompetenceInformationMode,
    DemandRegime,
    DiscoverBeliefPolicy,
    LearningProfile,
    compare_belief_policies,
    generate_uncertain_problems,
    make_dynamic_team,
)
from hls import hls_lab_dynamic


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(output_dir: Path) -> None:
    axis_a = DemandRegime("axis-a", ((0.2, 0.0), (0.0, 0.2)), (0.8, 0.2))
    axis_b = DemandRegime("axis-b", ((0.2, 0.0), (0.0, 0.2)), (0.2, 0.8))
    problems = generate_uncertain_problems(
        ((axis_a, 3), (axis_b, 3)), problem_seed=4107,
        environment_seed=4108, prior=1.0, budget=3.0,
    )
    real = ((0.84, 0.18), (0.22, 0.79), (0.43, 0.34))
    misspecified = ((0.30, 0.70), (0.70, 0.30), (0.50, 0.50))
    learning = LearningProfile(((0.08, 0.21), (0.42, 0.13), (0.27, 0.56)))
    modes = (
        CompetenceInformationMode.ORACLE,
        CompetenceInformationMode.PARTIAL_STATIC,
        CompetenceInformationMode.PARTIAL_LEARNING,
    )
    results = []
    for mode in modes:
        team = make_dynamic_team(
            real, information_mode=mode,
            estimated_competencies=None if mode == CompetenceInformationMode.ORACLE else misspecified,
        )
        (result,) = compare_belief_policies(
            team, problems, (DiscoverBeliefPolicy(sigma=0.04, quadrature_order=3),), learning=learning,
            decision_horizon=3, prior=1.0, sigma=0.04, noise_seed=4110,
            seed=4109, information_mode=mode,
            competence_observation_sigma=0.035,
            competence_noise_seed=4111,
            competence_prior_variance=0.035,
        )
        results.append(result)

    if [r.episode.action_id for r in results[1].records] == [
        r.episode.action_id for r in results[2].records
    ]:
        raise AssertionError("fixture failed to show an information-dependent decision change")

    output_dir.mkdir(parents=True, exist_ok=False)
    trace = output_dir / "decision_trace.csv"
    fields = (
        "information_mode", "problem_episode", "decision_in_problem", "problem_id",
        "action_id", "efforts", "real_competencies_before", "estimated_before",
        "estimated_variance_before", "individual_production_observations",
        "individual_competence_observation_noise", "real_competencies_after",
        "estimated_after", "estimated_variance_after", "mu_true_collective",
        "noisy_ces_observation", "environment_belief_before", "environment_belief_after",
    )
    with trace.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for result in results:
            for record in result.records:
                episode = record.episode
                noise = tuple(tuple(
                    record.individual_observations[i][k]
                    - episode.action[i][k] * episode.competence_before[i][k]
                    for k in range(2)
                ) for i in range(3))
                writer.writerow({
                    "information_mode": result.information_mode,
                    "problem_episode": record.problem_episode,
                    "decision_in_problem": record.decision_in_problem,
                    "problem_id": episode.problem_id,
                    "action_id": episode.action_id,
                    "efforts": json.dumps(episode.action, separators=(",", ":")),
                    "real_competencies_before": json.dumps(episode.competence_before, separators=(",", ":")),
                    "estimated_before": json.dumps(episode.estimated_before, separators=(",", ":")),
                    "estimated_variance_before": json.dumps(record.competence_variance_before, separators=(",", ":")),
                    "individual_production_observations": json.dumps(record.individual_observations, separators=(",", ":")),
                    "individual_competence_observation_noise": json.dumps(noise, separators=(",", ":")),
                    "real_competencies_after": json.dumps(episode.competence_after, separators=(",", ":")),
                    "estimated_after": json.dumps(episode.estimated_after, separators=(",", ":")),
                    "estimated_variance_after": json.dumps(record.competence_variance_after, separators=(",", ":")),
                    "mu_true_collective": format(record.true_expected_reward, ".17g"),
                    "noisy_ces_observation": format(record.observation, ".17g"),
                    "environment_belief_before": format(record.belief_before, ".17g"),
                    "environment_belief_after": format(record.belief_after, ".17g"),
                })

    manifest_path = output_dir / "manifest.json"
    manifest = {
        "classification": "bounded engineering verification; not scientific evidence",
        "problem_seed": 4107,
        "environment_seed": 4108,
        "environment_noise_seed": 4110,
        "individual_observation_noise_seed": 4111,
        "run_seed": 4109,
        "problems": len(problems),
        "decisions_per_problem": 3,
        "decision_records_per_mode": len(problems) * 3,
        "external_problem_stream_shared": True,
        "environment_noise_stream_shared": True,
        "individual_observation_innovations_coordinate_keyed": True,
        "initial_real_competencies": real,
        "initial_partial_estimate": misspecified,
        "eta_by_expert_and_capability": learning.eta,
        "competence_observation_model": "y[i,k]=effort[i,k]*competence_real_before[i,k]+Normal(0,0.035^2)",
        "prior_variance": 0.035,
        "results": [{
            "mode": result.information_mode,
            "cumulative_mu_true": result.cumulative_true_expected_reward,
            "action_ids": [r.episode.action_id for r in result.records],
            "final_real_competencies": result.final_team.real_matrix,
            "final_estimated_competencies": result.final_team.estimated_matrix,
            "final_environment_belief": result.records[-1].belief_after,
        } for result in results],
        "sha256": {
            "decision_trace.csv": sha256(trace),
            "hls_lab_dynamic.py": sha256(Path(hls_lab_dynamic.__file__)),
            "competence_learning_smoke.py": sha256(Path(__file__)),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("results/diagnostics/hls_lab_competence_learning_smoke"),
    )
    run(parser.parse_args().output_dir)
    print("Wrote bounded competence-learning verification")


if __name__ == "__main__":
    main()
