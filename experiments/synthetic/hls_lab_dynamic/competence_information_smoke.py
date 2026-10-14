"""Bounded engineering check for partial competence information.

This is a deterministic smoke fixture, not a scientific campaign. It compares
two existing policies on the same generated tasks, latent types, and CRN.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from hls.discover_v0 import THETA_1, THETA_2
from hls.hls_lab_dynamic import (
    CompetenceInformationMode,
    DemandRegime,
    DiscoverBeliefPolicy,
    LearningProfile,
    compare_belief_policies,
    generate_uncertain_problems,
    make_dynamic_team,
)
from hls.hls_lab_v1 import GreedyAdaptive
from hls import hls_lab_dynamic


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(output_dir: Path) -> None:
    # Fixed fixture: demand mixture changes after three problems.
    east = DemandRegime("east", ((0.2, 0.0), (0.0, 0.2)), (0.8, 0.2))
    west = DemandRegime("west", ((0.2, 0.0), (0.0, 0.2)), (0.2, 0.8))
    problems = generate_uncertain_problems(
        ((east, 3), (west, 3)), problem_seed=3107,
        environment_seed=3108, prior=0.5, budget=3.0,
    )
    real = ((0.85, 0.2), (0.2, 0.8), (0.4, 0.35))
    estimate = ((0.3, 0.7), (0.7, 0.3), (0.5, 0.5))
    team = make_dynamic_team(
        real, information_mode=CompetenceInformationMode.PARTIAL,
        estimated_competencies=estimate,
    )
    policies = (
        GreedyAdaptive(),
        DiscoverBeliefPolicy(sigma=0.03, quadrature_order=3),
    )
    runs = compare_belief_policies(
        team, problems, policies,
        learning=LearningProfile(((0.2, 0.2), (0.2, 0.2), (0.2, 0.2))),
        decision_horizon=2, prior=0.5, sigma=0.03,
        noise_seed=3110, seed=3109,
        information_mode=CompetenceInformationMode.PARTIAL,
    )
    output_dir.mkdir(parents=True, exist_ok=False)
    trace_path = output_dir / "trace.csv"
    with trace_path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=(
            "policy", "problem_episode", "decision_in_problem", "problem_id",
            "environment_type_privileged_metadata", "action_id", "mu_true",
            "observation", "noise_innovation", "belief_before", "belief_after",
            "real_competencies_before", "estimated_competencies_before",
            "real_competencies_after", "estimated_competencies_after",
        ), lineterminator="\n")
        writer.writeheader()
        for result in runs:
            for record in result.records:
                episode = record.episode
                writer.writerow({
                    "policy": result.policy,
                    "problem_episode": record.problem_episode,
                    "decision_in_problem": record.decision_in_problem,
                    "problem_id": episode.problem_id,
                    "environment_type_privileged_metadata": record.true_environment_type,
                    "action_id": episode.action_id,
                    "mu_true": format(record.true_expected_reward, ".17g"),
                    "observation": format(record.observation, ".17g"),
                    "noise_innovation": format(record.observation_noise, ".17g"),
                    "belief_before": format(record.belief_before, ".17g"),
                    "belief_after": format(record.belief_after, ".17g"),
                    "real_competencies_before": json.dumps(episode.competence_before),
                    "estimated_competencies_before": json.dumps(episode.estimated_before),
                    "real_competencies_after": json.dumps(episode.competence_after),
                    "estimated_competencies_after": json.dumps(episode.estimated_after),
                })
    manifest_path = output_dir / "manifest.json"
    manifest = {
        "classification": "bounded engineering smoke; not scientific evidence",
        "information_mode": "PARTIAL",
        "problem_seed": 3107,
        "environment_seed": 3108,
        "noise_seed": 3110,
        "run_seed": 3109,
        "problems": len(problems),
        "decisions_per_problem": 2,
        "policies": [result.policy for result in runs],
        "initial_real_competencies": real,
        "initial_estimated_competencies": estimate,
        "source_sha256": {
            "hls_lab_dynamic.py": sha256(Path(hls_lab_dynamic.__file__)),
            "competence_information_smoke.py": sha256(Path(__file__)),
        },
        "results": [{
            "policy": result.policy,
            "cumulative_true_expected_reward": result.cumulative_true_expected_reward,
            "final_real_competencies": result.final_team.real_matrix,
            "final_estimated_competencies": result.final_team.estimated_matrix,
            "final_belief": result.records[-1].belief_after,
        } for result in runs],
        "files": {"trace.csv": sha256(trace_path)},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("results/diagnostics/hls_lab_competence_information_smoke"),
    )
    args = parser.parse_args()
    run(args.output_dir)
    print(f"Wrote bounded competence-information smoke to {args.output_dir}")


if __name__ == "__main__":
    main()
