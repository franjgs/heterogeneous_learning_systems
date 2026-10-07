"""Constant-column-sum capability geometry gate on frozen DISCOVER x DEVELOP."""

from __future__ import annotations

import csv
import json
import sys
from functools import lru_cache
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.discover_develop_v0 import (  # noqa: E402
    DEVELOP_KNOWN,
    DISCOVER_DEVELOP,
    DISCOVER_ONLY,
    MODES,
    STATIC_KNOWN,
    run_sequence,
)
from hls.discover_v0 import (  # noqa: E402
    JOINT_ACTIONS,
    N_AGENTS,
    N_CAPABILITIES,
    RHO,
    THETA_1,
    THETA_2,
    State,
    canonical_state,
    evaluate_state,
    validate_state,
)

OUT = ROOT / "results" / "foundations" / "capability_geometry_gate"
SEED = 20261007
SEEDS = (20261007, 20261008, 20261009)
BUDGET_BY_CAPABILITY = (1.5, 1.5)
ALPHAS = (0.25, 0.5)

ENVIRONMENTS = {
    "persistent_theta1": (THETA_1, THETA_1, THETA_1, THETA_1),
    "persistent_theta2": (THETA_2, THETA_2, THETA_2, THETA_2),
    "change_1122": (THETA_1, THETA_1, THETA_2, THETA_2),
    "alternating_1212": (THETA_1, THETA_2, THETA_1, THETA_2),
    "recurrent_1221": (THETA_1, THETA_2, THETA_2, THETA_1),
}


def _state(rows) -> State:
    state = canonical_state(tuple(tuple(float(value) for value in row) for row in rows))
    validate_state(state)
    return state


def build_configurations() -> tuple[dict, ...]:
    """Build nine non-equivalent designs with exact column sums (1.5, 1.5)."""
    designs = [("generalist", 0.0, _state(((0.5, 0.5),) * 3))]
    for alpha in ALPHAS:
        designs.extend(
            (
                ("complementary", alpha, _state(((0.5 + alpha, 0.5 - alpha), (0.5 - alpha, 0.5 + alpha), (0.5, 0.5)))),
                ("concentrated", alpha, _state(((0.5 + alpha, 0.5 + alpha), (0.5 - alpha, 0.5 - alpha), (0.5, 0.5)))),
                ("partial_overlap", alpha, _state(((0.5 + alpha, 0.5), (0.5 - alpha, 0.5 + alpha), (0.5, 0.5 - alpha)))),
                ("redundant", alpha, _state(((0.5 + alpha / 2, 0.5 - alpha / 2), (0.5 + alpha / 2, 0.5 - alpha / 2), (0.5 - alpha, 0.5 + alpha)))),
            )
        )
    assert len({state for _, _, state in designs}) == len(designs)
    return tuple(
        {"configuration_id": f"G{index:02d}", "family": family, "alpha": alpha, "state": state}
        for index, (family, alpha, state) in enumerate(designs)
    )


CONFIGURATIONS = build_configurations()


def column_sums(state: State) -> tuple[float, float]:
    return tuple(sum(row[k] for row in state) for k in range(N_CAPABILITIES))  # type: ignore[return-value]


def geometry_descriptors(state: State) -> dict[str, float | str]:
    """Transparent, permutation-invariant summaries; none enters a policy."""
    columns = column_sums(state)
    breadths = tuple(sum(value > 0.0 for value in row) for row in state)
    pairwise_sq = [sum((state[i][k] - state[j][k]) ** 2 for k in range(N_CAPABILITIES)) for i, j in combinations(range(N_AGENTS), 2)]
    return {
        "individual_breadth_mean": sum(breadths) / N_AGENTS,
        "individual_breadth_min": min(breadths),
        "individual_breadth_max": max(breadths),
        "collective_breadth": sum(value > 0.0 for value in columns),
        "specialization_concentration": sum((state[i][k] / columns[k]) ** 2 for k in range(N_CAPABILITIES) for i in range(N_AGENTS)),
        "within_person_overlap": sum(min(row) for row in state),
        "redundancy": sum(sum(state[i][k] > 0.0 for i in range(N_AGENTS)) for k in range(N_CAPABILITIES)),
        "between_agent_heterogeneity": sum(pairwise_sq) / len(pairwise_sq),
        "capability_balance": abs(columns[0] - columns[1]),
        "coverage_capability_1": columns[0],
        "coverage_capability_2": columns[1],
        "total_capability": sum(columns),
    }


@lru_cache(maxsize=None)
def initial_known_value(state: State) -> float:
    return evaluate_state(state).known_value


def _text(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def _write(rows: list[dict], filename: str) -> None:
    with (OUT / filename).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _summary(config: dict, environment: str, mode: str, seed: int, steps) -> dict:
    rewards = [step.expected_reward_true for step in steps]
    changed = [i for i in range(1, len(steps)) if steps[i].problem_id != steps[i - 1].problem_id and steps[i].true_theta != steps[i - 1].true_theta]
    return {
        "configuration_id": config["configuration_id"],
        "family": config["family"],
        "alpha": config["alpha"],
        "environment": environment,
        "mode": mode,
        "seed": seed,
        "performance": steps[-1].cumulative_expected_reward,
        "early_performance": sum(rewards[:3]),
        "late_performance": sum(rewards[-3:]),
        "post_change_reward": "" if not changed else sum(rewards[i] for i in changed) / len(changed),
        "assignment_changes": sum(steps[i].action != steps[i - 1].action for i in range(1, len(steps))),
        "initial_V_K": initial_known_value(config["state"]),
        "final_S": _text(steps[-1].state_after),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    configurations, descriptors = [], []
    for config in CONFIGURATIONS:
        state = config["state"]
        common = {"configuration_id": config["configuration_id"], "family": config["family"], "alpha": config["alpha"]}
        configurations.append({**common, "B_1": column_sums(state)[0], "B_2": column_sums(state)[1], "state": _text(state)})
        descriptors.append({**common, **geometry_descriptors(state), "initial_V_K": initial_known_value(state)})

    environments = [
        {"environment": name, "theta_sequence": "|".join("theta1" if theta == THETA_1 else "theta2" for theta in sequence), "problems": len(sequence), "horizon_per_problem": 3}
        for name, sequence in ENVIRONMENTS.items()
    ]
    runs, trajectories = [], []
    control_ids = {"G00", "G06", "G07", "G08"}  # exact-V_K pair plus the observed regime winners
    for config in CONFIGURATIONS:
        for environment, sequence in ENVIRONMENTS.items():
            modes = MODES if config["configuration_id"] in control_ids else (DISCOVER_DEVELOP,)
            for mode in modes:
                for seed in SEEDS:
                    steps = run_sequence(config["state"], sequence, mode=mode, seed=seed)
                    runs.append(_summary(config, environment, mode, seed, steps))
                    for step in steps:
                        delta = tuple(tuple(step.state_after[i][k] - step.state_before[i][k] for k in range(N_CAPABILITIES)) for i in range(N_AGENTS))
                        trajectories.append(
                            {
                                "configuration_id": config["configuration_id"], "family": config["family"], "alpha": config["alpha"],
                                "environment": environment, "mode": mode, "seed": seed, "problem_index": step.problem_id,
                                "step_index": step.step_id, "true_theta_evaluation_only": step.true_theta,
                                "belief_pre": step.belief_before, "belief_post": step.belief_after,
                                "S_pre": _text(step.state_before), "assignment": _text(step.action), "capability_exercised": _text(step.action),
                                "production": step.expected_reward_true, "observed_reward": step.observed_reward,
                                "development_increment": _text(delta), "S_post": _text(step.state_after), "cumulative_performance": step.cumulative_expected_reward,
                            }
                        )

    main_runs = [row for row in runs if row["mode"] == DISCOVER_DEVELOP]
    regime_map = []
    for environment in ENVIRONMENTS:
        cells = []
        for config in CONFIGURATIONS:
            samples = [row for row in main_runs if row["environment"] == environment and row["configuration_id"] == config["configuration_id"]]
            performances = [float(row["performance"]) for row in samples]
            cells.append(
                {
                    "configuration_id": config["configuration_id"], "family": config["family"], "alpha": config["alpha"],
                    "environment": environment, "mean_performance": sum(performances) / len(performances),
                    "min_performance": min(performances), "max_performance": max(performances),
                    "initial_V_K": initial_known_value(config["state"]), "seeds": len(SEEDS),
                }
            )
        ordered = sorted(cells, key=lambda row: (-float(row["mean_performance"]), row["configuration_id"]))
        for rank, row in enumerate(ordered, 1):
            regime_map.append({"environment": environment, "rank": rank, "winner": rank == 1, **row})

    pairs = []
    descriptor_by_id = {row["configuration_id"]: row for row in descriptors}
    for left, right in combinations(CONFIGURATIONS, 2):
        dl, dr = descriptor_by_id[left["configuration_id"]], descriptor_by_id[right["configuration_id"]]
        performance_deltas = {
            f"Delta_mean_performance_{environment}": abs(
                float(next(row["mean_performance"] for row in regime_map if row["configuration_id"] == left["configuration_id"] and row["environment"] == environment))
                - float(next(row["mean_performance"] for row in regime_map if row["configuration_id"] == right["configuration_id"] and row["environment"] == environment))
            )
            for environment in ENVIRONMENTS
        }
        pairs.append(
            {
                "configuration_a": left["configuration_id"], "configuration_b": right["configuration_id"],
                "Delta_V_K": abs(float(dl["initial_V_K"]) - float(dr["initial_V_K"])),
                "Delta_heterogeneity": abs(float(dl["between_agent_heterogeneity"]) - float(dr["between_agent_heterogeneity"])),
                "Delta_overlap": abs(float(dl["within_person_overlap"]) - float(dr["within_person_overlap"])),
                "same_B_1": column_sums(left["state"])[0] == column_sums(right["state"])[0],
                "same_B_2": column_sums(left["state"])[1] == column_sums(right["state"])[1],
                **performance_deltas,
            }
        )
    pairs.sort(key=lambda row: (row["Delta_V_K"], -row["Delta_heterogeneity"], row["configuration_a"], row["configuration_b"]))

    representative_keys = {
        ("G07", "persistent_theta1"), ("G08", "persistent_theta2"), ("G08", "change_1122"),
        ("G06", "alternating_1212"), ("G00", "alternating_1212"),
    }
    representative = [row for row in main_runs if row["seed"] == SEED and (row["configuration_id"], row["environment"]) in representative_keys]

    _write(configurations, "configurations.csv")
    _write(environments, "environments.csv")
    _write(runs, "runs.csv")
    _write(trajectories, "trajectories.csv")
    _write(pairs, "matched_pairs.csv")
    _write(descriptors, "geometry_descriptors.csv")
    _write(regime_map, "regime_map.csv")
    _write(representative, "representative_cases.csv")
    (OUT / "manifest.json").write_text(
        json.dumps(
            {
                "frozen_prototype_head": "7eb7530", "campaign_parent_head": "a352314", "seeds": SEEDS,
                "N": N_AGENTS, "K": N_CAPABILITIES, "rho": RHO, "joint_actions": len(JOINT_ACTIONS),
                "B_k": BUDGET_BY_CAPABILITY, "configurations": len(CONFIGURATIONS), "environments": len(ENVIRONMENTS),
                "main_executions": len(CONFIGURATIONS) * len(ENVIRONMENTS) * len(SEEDS), "control_configurations": sorted(control_ids),
                "physics": "unchanged DISCOVER x DEVELOP prototype",
            }, indent=2,
        ) + "\n", encoding="utf-8",
    )


if __name__ == "__main__":
    main()
