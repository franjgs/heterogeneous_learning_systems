"""Reproducible controls for the finite problem-belief gate."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.discover_develop_v0 import DEVELOP_KNOWN, DISCOVER_DEVELOP, DISCOVER_ONLY, STATIC_KNOWN  # noqa: E402
from hls.discover_develop_v2 import run_sequence_v2  # noqa: E402
from hls.discover_v0 import THETA_1, THETA_2, unknown_policy_value  # noqa: E402
from hls.finite_problem_belief import (  # noqa: E402
    canonical_model,
    finite_unknown_policy_value,
    run_finite_problem_sequence,
)

OUT = ROOT / "results" / "foundations" / "finite_problem_belief_gate"
BINARY_MODEL = (THETA_1, THETA_2)
TERNARY_MODEL = (THETA_1, (0.5, 0.5), THETA_2)
G00 = ((0.5, 0.5),) * 3
G06 = ((0.0, 0.0), (0.5, 0.5), (1.0, 1.0))
SEQUENCE = (THETA_1, THETA_2, THETA_1, THETA_2)
SEED = 20261007


def _json(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def _trajectory_rows(case: str, rows) -> list[dict]:
    return [
        {
            "case": case,
            "mode": row.mode,
            "problem_id": row.problem_id,
            "step_id": row.step_id,
            "true_problem": _json(row.true_problem),
            "belief_before": _json(row.belief_before),
            "belief_after": _json(row.belief_after),
            "state_before": _json(row.state_before),
            "action": _json(row.action),
            "true_mean": row.true_mean,
            "observed_reward": row.observed_reward,
            "state_after": _json(row.state_after),
            "cumulative_reward": row.cumulative_reward,
        }
        for row in rows
    ]


def _binary_discrepancies(old, new) -> dict:
    return {
        "same_actions": all(left.action == right.action for left, right in zip(old, new)),
        "same_observations": all(left.observed_reward == right.observed_reward for left, right in zip(old, new)),
        "same_state_trajectory": all(left.state_after == right.state_after for left, right in zip(old, new)),
        "max_belief_probability_difference": max(
            abs(left.belief_after - right.belief_after[0]) for left, right in zip(old, new)
        ),
        "old_cumulative_reward": old[-1].cumulative_expected_reward,
        "new_cumulative_reward": new[-1].cumulative_reward,
        "cumulative_reward_difference": new[-1].cumulative_reward - old[-1].cumulative_expected_reward,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary: dict[str, object] = {
        "world_domain": "Delta^1",
        "binary_hypotheses": BINARY_MODEL,
        "ternary_hypotheses": TERNARY_MODEL,
        "seed": SEED,
        "eta": 0.70,
    }
    trajectories: list[dict] = []

    old_value = unknown_policy_value(G06)
    new_value = finite_unknown_policy_value(G06, BINARY_MODEL)
    summary["m2_policy"] = {
        "old_value": old_value.value,
        "new_value": new_value.value,
        "value_difference": new_value.value - old_value.value,
        "same_first_actions": old_value.first_actions == new_value.first_actions,
        "max_action_value_difference": max(
            abs(new_item[1] - old_item[1])
            for old_item, new_item in zip(old_value.first_action_values, new_value.first_action_values)
        ),
    }

    binary_controls = {}
    for identifier, state in (("G00", G00), ("G06", G06)):
        old = run_sequence_v2(state, SEQUENCE, mode=DISCOVER_DEVELOP, eta=0.70, seed=SEED)
        new = run_finite_problem_sequence(
            state, SEQUENCE, BINARY_MODEL, mode=DISCOVER_DEVELOP, eta=0.70, seed=SEED
        )
        binary_controls[identifier] = _binary_discrepancies(old, new)
        trajectories.extend(_trajectory_rows(f"m2_{identifier}", new))
    summary["m2_g00_g06"] = binary_controls

    old_discover = run_sequence_v2(G00, (THETA_1,), mode=DISCOVER_ONLY, eta=0.70, seed=SEED)
    new_discover = run_finite_problem_sequence(
        G00, (THETA_1,), BINARY_MODEL, mode=DISCOVER_ONLY, eta=0.70, seed=SEED
    )
    summary["m2_discover_only"] = _binary_discrepancies(old_discover, new_discover)

    represented = run_finite_problem_sequence(
        G06, ((0.5, 0.5),), TERNARY_MODEL, mode=DISCOVER_DEVELOP, eta=0.35, seed=SEED
    )
    unrepresented = run_finite_problem_sequence(
        G06, ((0.63, 0.37),), TERNARY_MODEL, mode=DISCOVER_DEVELOP, eta=0.35, seed=SEED
    )
    known_outside = run_finite_problem_sequence(
        G06, ((0.63, 0.37),), TERNARY_MODEL, mode=DEVELOP_KNOWN, eta=0.35, seed=SEED
    )
    trajectories.extend(_trajectory_rows("m3_represented", represented))
    trajectories.extend(_trajectory_rows("m3_unrepresented", unrepresented))
    trajectories.extend(_trajectory_rows("known_outside", known_outside))
    summary["m3_represented"] = {
        "true_problem": represented[0].true_problem,
        "final_belief": represented[-1].belief_after,
        "belief_sum": sum(represented[-1].belief_after),
        "cumulative_reward": represented[-1].cumulative_reward,
    }
    summary["m3_unrepresented"] = {
        "true_problem": unrepresented[0].true_problem,
        "hypotheses": TERNARY_MODEL,
        "final_belief": unrepresented[-1].belief_after,
        "belief_sum": sum(unrepresented[-1].belief_after),
        "cumulative_reward": unrepresented[-1].cumulative_reward,
    }
    summary["known_outside"] = {
        "true_problem": known_outside[0].true_problem,
        "belief_is_absent": all(row.belief_before is None and row.belief_after is None for row in known_outside),
        "cumulative_reward": known_outside[-1].cumulative_reward,
    }

    model_a = canonical_model(TERNARY_MODEL, (0.2, 0.5, 0.3))
    model_b = canonical_model((THETA_2, THETA_1, (0.5, 0.5)), (0.3, 0.2, 0.5))
    summary["hypothesis_permutation_invariance"] = model_a == model_b
    summary["known_modes_exercised"] = (STATIC_KNOWN, DEVELOP_KNOWN)

    with (OUT / "control_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with (OUT / "control_trajectories.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(trajectories[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(trajectories)


if __name__ == "__main__":
    main()
