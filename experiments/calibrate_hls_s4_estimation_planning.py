"""Select the first S4 setting meeting predeclared information/decision criteria."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

from hls.hls_lab_nk_estimation import CompetenceObservationParametersNK
from hls.synthetic.hls_s4 import S4Case
from hls.synthetic.hls_s4_estimation_planning import run_s4_estimation_planning


CALIBRATION_SEEDS = tuple(range(80000, 80010))
THRESHOLD_POSTERIOR_SHIFT = 0.025
THRESHOLD_DECISION_SWITCH_FRACTION = 0.50
THRESHOLD_PLAN_REACTIVE_DIFFERENCE = 0.50
PRIOR_MEANS = ((0.52, 0.50), (0.55, 0.50))
PRIOR_SD = 0.12


def candidates() -> tuple[tuple[S4Case, float], ...]:
    eta = ((0.15, 0.15), (0.05, 0.25))
    demands = tuple((True, False) for _ in range(4))
    return tuple(
        (S4Case(name, ((left, 0.175), (right, 0.175)), eta, demands), noise)
        for name, left, right, noise in (
            ("candidate_1", 0.55, 0.45, 0.02),
            ("candidate_2", 0.55, 0.45, 0.05),
            ("candidate_3", 0.60, 0.40, 0.02),
        )
    )


def _assignment_path(run) -> tuple[tuple[tuple[int, int], ...], ...]:
    return tuple(period.assignment for period in run.periods)


def assess(case: S4Case, noise: float) -> dict:
    params = CompetenceObservationParametersNK(
        production_observation_noise_sd=noise,
        competence_grid_points=101,
        competence_prior_variance=0.04,
    )
    runs = {
        (policy, estimation, seed): run_s4_estimation_planning(
            case, policy=policy, estimation=estimation, seed=seed,
            prior_cell_means=PRIOR_MEANS, prior_sd=PRIOR_SD,
            observation_parameters=params,
        )
        for seed in CALIBRATION_SEEDS
        for policy in ("reactive", "bellman")
        for estimation in ("frozen", "updated")
    }
    shifts = []
    for seed in CALIBRATION_SEEDS:
        for policy in ("reactive", "bellman"):
            frozen = runs[(policy, "frozen", seed)].periods[0]
            updated = runs[(policy, "updated", seed)].periods[0]
            selected = set(frozen.assignment)
            shifts.extend(
                abs(updated.estimate_after[i][k] - frozen.estimate_after[i][k])
                for i, k in selected
            )
    reactive_switch_fraction = mean(
        _assignment_path(runs[("reactive", "updated", seed)])[1:]
        != _assignment_path(runs[("reactive", "frozen", seed)])[1:]
        for seed in CALIBRATION_SEEDS
    )
    planning_difference_fraction = mean(
        _assignment_path(runs[("bellman", "frozen", seed)])
        != _assignment_path(runs[("reactive", "frozen", seed)])
        for seed in CALIBRATION_SEEDS
    )
    mean_shift = mean(shifts) if shifts else 0.0
    selected = (mean_shift >= THRESHOLD_POSTERIOR_SHIFT
                and reactive_switch_fraction >= THRESHOLD_DECISION_SWITCH_FRACTION
                and planning_difference_fraction >= THRESHOLD_PLAN_REACTIVE_DIFFERENCE)
    return {
        "case": case.name,
        "real_initial": [list(row) for row in case.initial],
        "eta": [list(row) for row in case.eta],
        "demand": [list(row) for row in case.demands],
        "prior_means": [list(row) for row in PRIOR_MEANS],
        "prior_sd": PRIOR_SD,
        "observation_noise_sd": noise,
        "mean_first_period_posterior_shift_on_observed_pairs": mean_shift,
        "reactive_decision_switch_fraction_after_first_observation": reactive_switch_fraction,
        "bellman_vs_reactive_path_difference_fraction_frozen": planning_difference_fraction,
        "meets_predeclared_operational_criteria": selected,
    }


def main() -> None:
    evaluated = []
    selected = None
    for case, noise in candidates():
        diagnostic = assess(case, noise)
        evaluated.append(diagnostic)
        if diagnostic["meets_predeclared_operational_criteria"]:
            selected = diagnostic
            break
    payload = {
        "experiment": "S4 estimation-planning diagnostic calibration",
        "calibration_seeds": list(CALIBRATION_SEEDS),
        "selection_rule": {
            "order": [case.name for case, _ in candidates()],
            "mean_posterior_shift_min": THRESHOLD_POSTERIOR_SHIFT,
            "reactive_later_decision_switch_fraction_min": THRESHOLD_DECISION_SWITCH_FRACTION,
            "bellman_reactive_path_difference_fraction_min": THRESHOLD_PLAN_REACTIVE_DIFFERENCE,
            "outcomes_used_for_selection": False,
            "reward_and_factorial_interaction_used": False,
        },
        "evaluated_candidates": evaluated,
        "selected_candidate": selected,
    }
    output = Path("results/experiments/hls_s4_estimation_planning_informative/calibration.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if selected is None:
        raise SystemExit("No candidate met the predeclared operational criteria")


if __name__ == "__main__":
    main()
