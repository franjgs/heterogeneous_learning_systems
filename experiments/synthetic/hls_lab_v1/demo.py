"""Small, deterministic CE-23 demonstration; no factorial or campaign run."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.discover_v0 import JOINT_ACTIONS  # noqa: E402
from hls.hls_lab_v1 import (  # noqa: E402
    ExploreThenGreedy, FixedRouting, GreedyAdaptive, ProblemSpec,
    complementarity_class, make_team, run_sequence,
)
from experiments.synthetic.campaign0_discriminative_capacity.run import ETA  # noqa: E402

LEFT = ((1.0, 0.0), (0.0, 0.0), (0.0, 0.0))
RIGHT = ((0.0, 0.0), (0.0, 1.0), (0.0, 0.0))
TOGETHER = ((1.0, 0.0), (0.0, 1.0), (0.0, 0.0))
TEAM = make_team(((1.0, 0.0), (0.0, 1.0), (0.5, 0.5)))
THIRD_EXPERT = ((0.0, 0.0), (0.0, 0.0), (1.0, 0.0))


def main() -> None:
    action_catalog = (RIGHT, LEFT)
    left_task = ProblemSpec("A", (0.8, 0.0), 1.0, allowed_actions=action_catalog)
    right_task = ProblemSpec("B", (0.0, 0.8), 1.0, allowed_actions=action_catalog)
    complementary = ProblemSpec("TEAM_ONLY", (0.8, 0.8), 2.0,
                                allowed_actions=(TOGETHER, LEFT, RIGHT))
    sequence = (left_task, left_task, right_task, right_task,
                left_task, right_task, complementary)
    fixed = FixedRouting({"A": LEFT, "B": RIGHT, "TEAM_ONLY": TOGETHER})
    policies = (fixed, GreedyAdaptive(), ExploreThenGreedy())
    results = []
    for policy in policies:
        run = run_sequence(TEAM, sequence, policy, eta=ETA,
                           individual_learning=False,
                           organizational_learning=isinstance(policy, ExploreThenGreedy),
                           seed=20261014)
        results.append({
            "policy": run.policy,
            "successes": sum(row.success for row in run.records),
            "episodes": len(run.records),
            "team_only_classification": complementarity_class(TEAM, complementary),
            "decision_trace": [
                {"problem": row.problem_id, "action_id": row.action_id, "success": row.success,
                 "theta_updated": row.organization_updated, "action_changed": row.organization_action_changed,
                 "theta_entries": len(row.organization_theta_after)}
                for row in run.records
            ],
            "organization_updates": run.final_organization.update_count,
        })

    # A separate deterministic control exposes a sub-maximal expert, so LI
    # ON/OFF is visible without changing the main policy comparison fixture.
    learning_team = make_team(((0.4, 0.0), (0.0, 1.0), (0.2, 0.0)))
    learning_probe = ProblemSpec("LEARNING_CONTROL", (0.35, 0.0), 1.0,
                                 allowed_actions=(THIRD_EXPERT, LEFT))
    learning_sequence = (learning_probe, learning_probe, learning_probe)
    toggles = []
    learner = ExploreThenGreedy()
    for individual in (False, True):
        for organizational in (False, True):
            run = run_sequence(learning_team, learning_sequence, learner, eta=ETA,
                               individual_learning=individual,
                               organizational_learning=organizational,
                               seed=20261014)
            toggles.append({
                "individual_learning": individual,
                "organizational_learning": organizational,
                "initial_competence": learning_team.real_matrix,
                "final_competence": run.final_team.real_matrix,
                "organizational_updates": run.final_organization.update_count,
                "successes": sum(row.success for row in run.records),
            })

    solo = ProblemSpec("SOLO", (0.8, 0.0), 1.0, allowed_actions=(LEFT, RIGHT))
    solo_action = LEFT
    summary = {
        "protocol": "HLS Laboratory v1 / CE-23 vertical slice",
        "eta": ETA,
        "seed": 20261014,
        "solo_control": {"problem": solo.problem_id, "requirements": solo.requirements,
                         "output": __import__("hls.discover_v0", fromlist=["production_inputs"])
                         .production_inputs(TEAM.real_matrix, solo_action),
                         "classification": complementarity_class(TEAM, solo)},
        "policies": results,
        "independent_controls": toggles,
        "action_catalog_size": len(JOINT_ACTIONS),
        "note": "One-decision problem episodes; deterministic fixture demonstration, not scientific evidence.",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
