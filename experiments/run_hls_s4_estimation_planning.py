"""Paired factorial: competence observation updates × S4 planning."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, stdev

from hls.hls_lab_nk_estimation import CompetenceObservationParametersNK
from hls.synthetic.hls_s4 import canonical_cases, investment_family
from hls.synthetic.hls_s4_estimation_planning import (
    S4EstimationRun,
    run_dict,
    run_s4_estimation_planning,
)


SEEDS = tuple(range(81000, 81030))
PRIOR_MEAN = 0.5
OBSERVATION_PARAMETERS = CompetenceObservationParametersNK(
    production_observation_noise_sd=0.02,
    outcome_noise_sd=0.0,
    competence_grid_points=101,
    competence_prior_variance=0.04,
)
CONDITIONS = (("reactive", "frozen"), ("reactive", "updated"),
              ("bellman", "frozen"), ("bellman", "updated"))


def _ci(values: list[float]) -> list[float]:
    avg = mean(values)
    margin = 0.0 if len(values) < 2 else 1.96 * stdev(values) / (len(values) ** 0.5)
    return [avg, avg - margin, avg + margin]


def summarize_case(runs: list[S4EstimationRun]) -> dict:
    by_condition = {
        f"{policy}_{estimation}": [
            run for run in runs if run.policy == policy and run.estimation == estimation
        ]
        for policy, estimation in CONDITIONS
    }
    rewards = {key: {run.seed: run.reward for run in values}
               for key, values in by_condition.items()}
    factorial = {
        seed: ((rewards["bellman_updated"][seed] - rewards["reactive_updated"][seed])
               - (rewards["bellman_frozen"][seed] - rewards["reactive_frozen"][seed]))
        for seed in SEEDS
    }
    mse = {
        key: [mean([period.mse_before for period in run.periods]) for run in values]
        for key, values in by_condition.items()
    }
    compute = {
        key: [run.total_decision_seconds / max(1, len(run.periods)) for run in values]
        for key, values in by_condition.items()
    }
    return {
        "n_seeds": len(SEEDS),
        "reward_mean_ci95": {key: _ci(list(values.values())) for key, values in rewards.items()},
        "paired_factorial_interaction_BA_RA_minus_BF_RF_mean_ci95": _ci(list(factorial.values())),
        "paired_simple_effect_planning_updated_mean_ci95": _ci([
            rewards["bellman_updated"][seed] - rewards["reactive_updated"][seed]
            for seed in SEEDS
        ]),
        "paired_simple_effect_planning_frozen_mean_ci95": _ci([
            rewards["bellman_frozen"][seed] - rewards["reactive_frozen"][seed]
            for seed in SEEDS
        ]),
        "mean_period_mse_by_condition": {key: mean(values) for key, values in mse.items()},
        "mean_decision_seconds_per_period_by_condition": {
            key: mean(values) for key, values in compute.items()
        },
        "paired_interaction_by_seed": [
            {"seed": seed, "value": factorial[seed]} for seed in SEEDS
        ],
        "runs": [run_dict(run) for run in runs],
    }


def main() -> None:
    no_return = canonical_cases()[0]
    cases = (no_return, *investment_family())
    all_results = []
    for case in cases:
        runs = [
            run_s4_estimation_planning(
                case, policy=policy, estimation=estimation, seed=seed,
                prior_mean=PRIOR_MEAN,
                observation_parameters=OBSERVATION_PARAMETERS,
            )
            for seed in SEEDS
            for policy, estimation in CONDITIONS
        ]
        all_results.append({
            "case": case.name,
            "initial_real_competence": [list(row) for row in case.initial],
            "eta": [list(row) for row in case.eta],
            "demand": [list(row) for row in case.demands],
            "prior_mean_all_cells": PRIOR_MEAN,
            "prior_distribution": "uniform over the 101-point grid on [0,1]",
            "observation_noise_sd": OBSERVATION_PARAMETERS.production_observation_noise_sd,
            "prior_adjustment": "validation smoke test found the moment-matched default prior had effectively no mass at intermediate hidden values; only the prior distribution changed, not the Bayesian update rule",
            "prior_variance": "uniform_grid",
            "summary": summarize_case(runs),
        })
    payload = {
        "experiment": "HLS-S4 Bayesian estimation × certainty-equivalent Bellman planning",
        "date": "2026-10-22",
        "seeds": list(SEEDS),
        "conditions": [f"{policy}_{estimation}" for policy, estimation in CONDITIONS],
        "definitions": {
            "reward": "sum of real pre-transition competence over assigned pairs",
            "frozen": "no observation likelihood updates; posterior is propagated through known MIS-v2 after executed actions",
            "updated": "assimilate noisy observations from executed pairs, then propagate posterior through MIS-v2",
            "prior": "same uniform discrete prior in every cell and condition; mean 0.5",
            "bellman": "existing exact S4 recursion replanned from posterior mean and known remaining demand; certainty-equivalent, not Bayesian-optimal",
            "reactive": "existing exact immediate S4 assignment from the same posterior mean",
            "pairing": "same seed-indexed observation noise streams across four conditions; action-dependent observed pairs may differ",
            "ci": "paired replicate means with normal-approximation 95% intervals (1.96 × SE), seeds are units",
        },
        "cases": all_results,
    }
    output = Path("results/experiments/hls_s4_estimation_planning/results.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(output)
    for case in all_results:
        print(case["case"], json.dumps(case["summary"], separators=(",", ":"))[:900])


if __name__ == "__main__":
    main()
