"""Execute the frozen Campaign 1 protocol without changing model physics."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.synthetic.capability_geometry_gate.run import CONFIGURATIONS  # noqa: E402
from hls.campaign1_protocol import (  # noqa: E402
    CONDITIONS,
    CONFIGURATION_IDS,
    PARAMETERS,
    PROTOCOL_ID,
    SCENARIO_IDS,
    SEEDS,
    TOTAL_RUNS,
    validate_protocol,
)
from hls.campaign1_test_range import (  # noqa: E402
    CONTAMINATION_STATUS,
    HISTORIES,
    history_steps,
)
from hls.discover_develop_v0 import DEVELOP_KNOWN, DISCOVER_DEVELOP  # noqa: E402
from hls.discover_develop_v2 import mis_v2_transition  # noqa: E402
from hls.discover_v0 import (  # noqa: E402
    DEFAULT_SIGMA,
    N_AGENTS,
    N_CAPABILITIES,
    ces_reward,
    production_inputs,
    validate_state,
)
from hls.finite_problem_belief import (  # noqa: E402
    FiniteBeliefStep,
    canonical_model,
    finite_bayes_update,
    finite_choose_dynamic_action_v2,
    hypothesis_means,
    run_finite_problem_sequence,
)
from hls.problem_geometry import validate_problem  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402

OUT = ROOT / "results" / "campaigns" / "campaign1_test_range"
PRE_PROTOCOL = ROOT / "results" / "foundations" / "campaign1_protocol" / "pre_experiment_protocol.json"
CONFIG_BY_ID = {row["configuration_id"]: row["state"] for row in CONFIGURATIONS}


def _json(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def run_no_develop(
    initial_state, true_problems, *, eta: float, horizon: int, seed: int
) -> tuple[FiniteBeliefStep, ...]:
    """Use the frozen dynamic MPC with develop=False; never historical DISCOVER_ONLY."""
    validate_state(initial_state)
    model, reset_prior = canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    problems = tuple(validate_problem(problem) for problem in true_problems)
    rng, state, cumulative, rows = Random(seed), initial_state, 0.0, []
    for problem_id, problem in enumerate(problems):
        belief = reset_prior
        for step_id in range(horizon):
            before = state
            action = finite_choose_dynamic_action_v2(
                state, belief, model, remaining=horizon - step_id,
                develop=False, eta=eta,
            )[0]
            true_mean = ces_reward(production_inputs(state, action), problem)
            observed = true_mean + DEFAULT_SIGMA * rng.gauss(0.0, 1.0)
            predicted = hypothesis_means(state, action, model)
            posterior = finite_bayes_update(belief, observed, predicted, DEFAULT_SIGMA)
            state = mis_v2_transition(state, action, enabled=False, eta=eta)
            cumulative += true_mean
            rows.append(FiniteBeliefStep(
                problem_id, step_id, problem, belief, posterior, before, state,
                action, true_mean, observed, cumulative, "campaign1_no_develop_mpc",
            ))
            belief = posterior
    return tuple(rows)


def run_condition(configuration_id: str, scenario_id: str, condition: str, seed: int):
    state, problems = CONFIG_BY_ID[configuration_id], HISTORIES[scenario_id]
    eta, horizon = PARAMETERS["eta"], PARAMETERS["horizon_per_problem"]
    if condition == "FULL":
        return run_finite_problem_sequence(
            state, problems, HYPOTHESIS_REPERTOIRE, prior=UNIFORM_PRIOR,
            mode=DISCOVER_DEVELOP, eta=eta, horizon=horizon, seed=seed,
        )
    if condition == "NO-DEVELOP":
        return run_no_develop(state, problems, eta=eta, horizon=horizon, seed=seed)
    if condition == "KNOWN-Z":
        return run_finite_problem_sequence(
            state, problems, HYPOTHESIS_REPERTOIRE, prior=UNIFORM_PRIOR,
            mode=DEVELOP_KNOWN, eta=eta, horizon=horizon, seed=seed,
        )
    raise ValueError(f"unknown frozen condition: {condition}")


def _task(task):
    scenario_id, configuration_id, condition, seed = task
    steps = run_condition(configuration_id, scenario_id, condition, seed)
    descriptors = history_steps(scenario_id)
    cumulative_exposure = [[0.0] * N_CAPABILITIES for _ in range(N_AGENTS)]
    trajectory_rows = []
    problem_performance = [0.0] * len(HISTORIES[scenario_id])
    for row in steps:
        descriptor = descriptors[row.problem_id]
        exposure_before = tuple(tuple(values) for values in cumulative_exposure)
        for i in range(N_AGENTS):
            for k in range(N_CAPABILITIES):
                cumulative_exposure[i][k] += row.action[i][k]
        exposure_after = tuple(tuple(values) for values in cumulative_exposure)
        problem_performance[row.problem_id] += row.true_mean
        delta_state = tuple(
            tuple(row.state_after[i][k] - row.state_before[i][k] for k in range(N_CAPABILITIES))
            for i in range(N_AGENTS)
        )
        trajectory_rows.append({
            "scenario_id": scenario_id, "configuration_id": configuration_id,
            "condition": condition, "seed": seed, "problem_index": row.problem_id,
            "within_problem_step": row.step_id, "point": descriptor.label,
            "true_problem": _json(row.true_problem), "p": row.true_problem[0],
            "C_t": descriptor.change, "N_t": descriptor.novelty, "M_t": descriptor.mismatch,
            "represented": descriptor.represented,
            "belief_before": "" if row.belief_before is None else _json(row.belief_before),
            "belief_after": "" if row.belief_after is None else _json(row.belief_after),
            "action": _json(row.action), "exposure_before": _json(exposure_before),
            "exposure_after": _json(exposure_after), "state_before": _json(row.state_before),
            "development_increment": _json(delta_state), "state_after": _json(row.state_after),
            "mu_true": row.true_mean, "observed_reward": row.observed_reward,
            "noise_innovation": (row.observed_reward - row.true_mean) / DEFAULT_SIGMA,
            "cumulative_performance": row.cumulative_reward,
        })
    summary = {
        "scenario_id": scenario_id, "configuration_id": configuration_id,
        "condition": condition, "seed": seed, "eta": PARAMETERS["eta"],
        "horizon": PARAMETERS["horizon_per_problem"], "problems": len(HISTORIES[scenario_id]),
        "cumulative_performance": steps[-1].cumulative_reward,
        "problem_performance": _json(problem_performance),
        "final_exposure": _json(tuple(tuple(values) for values in cumulative_exposure)),
        "final_state": _json(steps[-1].state_after),
        "contamination_status": CONTAMINATION_STATUS[scenario_id],
    }
    return summary, trajectory_rows


def build_tasks() -> list[tuple[str, str, str, int]]:
    return [
        (scenario, configuration, condition, seed)
        for scenario in SCENARIO_IDS
        for configuration in CONFIGURATION_IDS
        for condition in CONDITIONS
        for seed in SEEDS
    ]


def main(*, workers: int) -> None:
    validate_protocol()
    tasks = build_tasks()
    if len(tasks) != TOTAL_RUNS or len(set(tasks)) != TOTAL_RUNS:
        raise AssertionError("frozen run-key matrix is incomplete or duplicated")
    OUT.mkdir(parents=True, exist_ok=True)
    if workers == 1:
        computed = map(_task, tasks)
    else:
        executor = ProcessPoolExecutor(max_workers=workers)
        computed = executor.map(_task, tasks, chunksize=2)
    runs, trajectories = [], []
    for summary, rows in computed:
        runs.append(summary); trajectories.extend(rows)
    if workers != 1:
        executor.shutdown()
    runs.sort(key=lambda r: (SCENARIO_IDS.index(r["scenario_id"]), CONFIGURATION_IDS.index(r["configuration_id"]), CONDITIONS.index(r["condition"]), r["seed"]))
    trajectories.sort(key=lambda r: (SCENARIO_IDS.index(r["scenario_id"]), CONFIGURATION_IDS.index(r["configuration_id"]), CONDITIONS.index(r["condition"]), r["seed"], r["problem_index"], r["within_problem_step"]))
    _write_csv(OUT / "runs.csv", runs)
    _write_csv(OUT / "trajectories.csv", trajectories)
    protocol_hash = hashlib.sha256(PRE_PROTOCOL.read_bytes()).hexdigest()
    counts = {condition: sum(row["condition"] == condition for row in runs) for condition in CONDITIONS}
    manifest = {
        "campaign_id": "campaign1-test-range-characterization-v1",
        "status": "execution complete; analysis pending",
        "pre_results_head": "bcc3ad8",
        "test_range_commit": "05b86cb",
        "protocol_id": PROTOCOL_ID,
        "pre_experiment_protocol_sha256": protocol_hash,
        "parameters": PARAMETERS,
        "scenario_ids": SCENARIO_IDS, "configuration_ids": CONFIGURATION_IDS,
        "conditions": CONDITIONS, "seeds": SEEDS,
        "run_count": len(runs), "trajectory_rows": len(trajectories),
        "runs_by_condition": counts,
        "crn_verified": all(
            max(values) - min(values) <= 2e-14
            for scenario in SCENARIO_IDS for config in CONFIGURATION_IDS for seed in SEEDS
            for problem in range(6) for step in range(3)
            for values in [[float(row["noise_innovation"]) for row in trajectories if row["scenario_id"] == scenario and row["configuration_id"] == config and row["seed"] == seed and row["problem_index"] == problem and row["within_problem_step"] == step]]
        ),
        "performance_field": "mu_true",
        "observed_reward_role": "Bayesian observation only; retained but not performance",
        "condition_implementation": {
            "FULL": "run_finite_problem_sequence mode DISCOVER_DEVELOP",
            "NO-DEVELOP": "finite_choose_dynamic_action_v2 develop=False; state transition disabled",
            "KNOWN-Z": "run_finite_problem_sequence mode DEVELOP_KNOWN",
        },
    }
    with (OUT / "execution_manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True); handle.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    main(workers=args.workers)
