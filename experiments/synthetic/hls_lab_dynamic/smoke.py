"""Bounded reproducible DISCOVER × dynamic-lab engineering smoke test."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from hls.discover_v0 import THETA_1, THETA_2
from hls.hls_lab_dynamic import (
    DemandRegime,
    DiscoverBeliefPolicy,
    LearningProfile,
    compare_belief_policies,
    generate_uncertain_problems,
)
from hls.hls_lab_v1 import GreedyAdaptive, make_team


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = ROOT / "results/diagnostics/hls_lab_dynamic_smoke"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def run(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    team_matrix = ((0.82, 0.12), (0.18, 0.76), (0.35, 0.28))
    learning = LearningProfile(((0.10, 0.20), (0.70, 0.30), (0.40, 0.60)))
    regime_a = DemandRegime("first-demand", ((0.6, 0.0), (0.0, 0.6)), (0.9, 0.1))
    regime_b = DemandRegime("second-demand", ((0.6, 0.0), (0.0, 0.6)), (0.1, 0.9))
    problems = generate_uncertain_problems(
        ((regime_a, 4), (regime_b, 4)), problem_seed=208,
        environment_seed=409, budget=3.0,
    )
    policies = (DiscoverBeliefPolicy(quadrature_order=3), GreedyAdaptive())
    results = compare_belief_policies(
        make_team(team_matrix), problems, policies, learning=learning,
        decision_horizon=2, prior=0.5, sigma=0.1, noise_seed=610, seed=42,
    )

    trace_path = output_dir / "episode_trace.csv"
    with trace_path.open("w", newline="", encoding="utf-8") as handle:
        fields = (
            "policy", "problem_episode", "decision_in_problem", "problem_id",
            "requirements", "true_environment_type_privileged", "belief_before",
            "belief_after", "observation", "observation_noise", "true_expected_reward",
            "action_id", "outputs", "functional_success", "normalized_deficit",
            "competence_before", "competence_after", "estimated_before",
            "estimated_after", "experience_after", "cumulative_successes",
        )
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for result in results:
            for row in result.records:
                episode = row.episode
                writer.writerow({
                    "policy": result.policy,
                    "problem_episode": row.problem_episode,
                    "decision_in_problem": row.decision_in_problem,
                    "problem_id": episode.problem_id,
                    "requirements": _json(episode.requirements),
                    "true_environment_type_privileged": row.true_environment_type,
                    "belief_before": row.belief_before,
                    "belief_after": row.belief_after,
                    "observation": row.observation,
                    "observation_noise": row.observation_noise,
                    "true_expected_reward": row.true_expected_reward,
                    "action_id": episode.action_id,
                    "outputs": _json(episode.outputs),
                    "functional_success": episode.success,
                    "normalized_deficit": episode.normalized_deficit,
                    "competence_before": _json(episode.competence_before),
                    "competence_after": _json(episode.competence_after),
                    "estimated_before": _json(episode.estimated_before),
                    "estimated_after": _json(episode.estimated_after),
                    "experience_after": _json(episode.experience_after),
                    "cumulative_successes": episode.cumulative_successes,
                })

    summary = {
        result.policy: {
            "decisions": len(result.records),
            "functional_successes": sum(row.episode.success for row in result.records),
            "cumulative_true_ces_reward": result.cumulative_true_expected_reward,
            "final_real_competencies": result.final_team.real_matrix,
            "final_estimated_competencies": result.final_team.estimated_matrix,
            "belief_updates": sum(
                abs(row.belief_after - row.belief_before) > 1e-12
                for row in result.records
            ),
        }
        for result in results
    }
    source_paths = (
        Path(__file__),
        ROOT / "src/hls/hls_lab_dynamic.py",
        ROOT / "src/hls/discover_v0.py",
        ROOT / "src/hls/discover_develop_v2.py",
        ROOT / "src/hls/hls_lab_v1.py",
    )
    manifest = {
        "kind": "bounded_engineering_smoke_not_scientific_campaign",
        "problem_seed": 208,
        "environment_seed": 409,
        "observation_noise_seed": 610,
        "run_seed_metadata": 42,
        "problem_schedule": [
            {"label": "first-demand", "count": 4, "probabilities": [0.9, 0.1]},
            {"label": "second-demand", "count": 4, "probabilities": [0.1, 0.9]},
        ],
        "requirement_options": [[0.6, 0.0], [0.0, 0.6]],
        "latent_environment_types": {"theta1": THETA_1, "theta2": THETA_2},
        "decision_horizon": 2,
        "prior": 0.5,
        "observation_sigma": 0.1,
        "quadrature_order": 3,
        "initial_team": team_matrix,
        "learning_eta_by_expert_capability": learning.eta,
        "policies": [policy.name for policy in policies],
        "policy_pairing": "same task sequence, latent types, and Gaussian innovations",
        "summary": summary,
        "source_sha256": {str(path.relative_to(ROOT)): _digest(path) for path in source_paths},
        "episode_trace_sha256": _digest(trace_path),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"trace={trace_path}")
    print(f"manifest={output_dir / 'manifest.json'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output_dir)


if __name__ == "__main__":
    main()
