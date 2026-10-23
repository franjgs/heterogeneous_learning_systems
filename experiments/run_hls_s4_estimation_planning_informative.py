"""Evaluation of the first calibration candidate on independent seeds."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, stdev

from hls.hls_lab_nk_estimation import CompetenceObservationParametersNK
from hls.synthetic.hls_s4 import S4Case, canonical_cases
from hls.synthetic.hls_s4_estimation_planning import (
    S4EstimationRun,
    run_dict,
    run_s4_estimation_planning,
)


SEEDS = tuple(range(82000, 82030))
CONDITIONS = (("reactive", "frozen"), ("reactive", "updated"),
              ("bellman", "frozen"), ("bellman", "updated"))
PRIOR_MEANS = ((0.52, 0.50), (0.55, 0.50))
PRIOR_SD = 0.12
OBSERVATION_PARAMETERS = CompetenceObservationParametersNK(
    production_observation_noise_sd=0.02,
    competence_grid_points=101,
    competence_prior_variance=0.04,
)


def ci(values: list[float]) -> list[float]:
    avg = mean(values)
    margin = 0.0 if len(values) < 2 else 1.96 * stdev(values) / len(values) ** 0.5
    return [avg, avg - margin, avg + margin]


def summarize(runs: list[S4EstimationRun]) -> dict:
    by_condition = {
        f"{policy}_{estimation}": [
            run for run in runs if run.policy == policy and run.estimation == estimation
        ] for policy, estimation in CONDITIONS
    }
    rewards = {key: {run.seed: run.reward for run in values}
               for key, values in by_condition.items()}
    interaction = {
        seed: ((rewards["bellman_updated"][seed] - rewards["reactive_updated"][seed])
               - (rewards["bellman_frozen"][seed] - rewards["reactive_frozen"][seed]))
        for seed in SEEDS
    }
    def changed_fraction(policy: str) -> float:
        updated = {run.seed: run for run in by_condition[f"{policy}_updated"]}
        frozen = {run.seed: run for run in by_condition[f"{policy}_frozen"]}
        return sum(
            a.assignment != b.assignment
            for seed in SEEDS
            for a, b in zip(updated[seed].periods, frozen[seed].periods)
        ) / (len(SEEDS) * len(updated[SEEDS[0]].periods))

    return {
        "reward_mean_ci95": {key: ci(list(values.values())) for key, values in rewards.items()},
        "factorial_interaction_BA_minus_RA_minus_BF_minus_RF_mean_ci95": ci(list(interaction.values())),
        "planning_effect_updated_mean_ci95": ci([
            rewards["bellman_updated"][s] - rewards["reactive_updated"][s] for s in SEEDS
        ]),
        "planning_effect_frozen_mean_ci95": ci([
            rewards["bellman_frozen"][s] - rewards["reactive_frozen"][s] for s in SEEDS
        ]),
        "updated_vs_frozen_assignment_change_fraction": {
            policy: changed_fraction(policy) for policy in ("reactive", "bellman")
        },
        "mean_posterior_update_l1_by_condition": {
            key: mean([p.posterior_update_l1 for run in values for p in run.periods])
            for key, values in by_condition.items()
        },
        "mean_predecision_mse_by_condition": {
            key: mean([p.mse_before for run in values for p in run.periods])
            for key, values in by_condition.items()
        },
        "mean_decision_seconds_per_period_by_condition": {
            key: mean([run.total_decision_seconds / len(run.periods) for run in values])
            for key, values in by_condition.items()
        },
        "interaction_by_seed": [{"seed": seed, "value": interaction[seed]} for seed in SEEDS],
        "runs": [run_dict(run) for run in runs],
    }


def main() -> None:
    calibration_path = Path("results/experiments/hls_s4_estimation_planning_informative/calibration.json")
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    selected = calibration["selected_candidate"]
    if selected is None:
        raise SystemExit("Calibration found no operational candidate; no evaluation run is authorized")
    eta = tuple(tuple(row) for row in selected["eta"])
    real_initial = tuple(tuple(row) for row in selected["real_initial"])
    family = tuple(
        S4Case(f"investment_horizon_{h}", real_initial, eta,
               tuple((True, False) for _ in range(h)))
        for h in (1, 2, 3, 4)
    )
    cases = (canonical_cases()[0], *family)
    output_cases = []
    for case in cases:
        runs = [
            run_s4_estimation_planning(
                case, policy=policy, estimation=estimation, seed=seed,
                prior_cell_means=PRIOR_MEANS, prior_sd=PRIOR_SD,
                observation_parameters=OBSERVATION_PARAMETERS,
            )
            for seed in SEEDS
            for policy, estimation in CONDITIONS
        ]
        output_cases.append({
            "case": case.name,
            "real_initial_competence": [list(row) for row in case.initial],
            "eta": [list(row) for row in case.eta],
            "demand": [list(row) for row in case.demands],
            "summary": summarize(runs),
        })
    payload = {
        "experiment": "HLS-S4 informative Bayesian estimation × Bellman planning",
        "calibration_artifact": str(calibration_path),
        "evaluation_seeds": list(SEEDS),
        "independent_from_calibration": True,
        "conditions": [f"{p}-{e}" for p, e in CONDITIONS],
        "prior_means": [list(row) for row in PRIOR_MEANS],
        "prior_sd": PRIOR_SD,
        "prior_support": "101-point competence grid [0,1], discrete Gaussian weights centered on prior means",
        "observation_noise_sd": OBSERVATION_PARAMETERS.production_observation_noise_sd,
        "definitions": {
            "frozen": "no observation assimilation; propagate estimate through known MIS-v2 after executed actions",
            "updated": "Bayesian update from executed productive observations, then known MIS-v2 prediction",
            "bellman": "receding-horizon exact S4 recursion from posterior mean; certainty-equivalent only",
            "reactive": "exact immediate maximization from the same current posterior mean",
            "reward": "collective reward from true pre-transition competence",
            "confidence_interval": "paired replicate-level normal approximation 1.96×SE; seed is unit",
        },
        "cases": output_cases,
    }
    output = Path("results/experiments/hls_s4_estimation_planning_informative/results.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(output)
    for case in output_cases:
        summary = case["summary"]
        print(case["case"], json.dumps({
            "reward_mean_ci95": summary["reward_mean_ci95"],
            "interaction": summary["factorial_interaction_BA_minus_RA_minus_BF_minus_RF_mean_ci95"],
            "decision_change": summary["updated_vs_frozen_assignment_change_fraction"],
            "posterior_update": summary["mean_posterior_update_l1_by_condition"],
        }, separators=(",", ":")))


if __name__ == "__main__":
    main()
