"""Small S4 evaluation of competence estimation and finite-horizon planning.

This is an adapter around the existing bounded posterior, MIS-v2 transition,
and small exact S4 solvers. Bellman plans over the current posterior mean; it
is a certainty-equivalent policy, not a Bayesian-optimal POMDP solution.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
from time import perf_counter

from hls.hls_lab_dynamic import indexed_normal_innovation
from hls.hls_lab_nk_estimation import (
    CompetenceObservationParametersNK,
    CompetencePosteriorNK,
    assimilate_production_observations_nk,
    posterior_mean_matrix_nk,
    predict_mis_v2_nk,
)
from hls.hls_lab_dynamic import SkillPosterior
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from hls.synthetic.hls_s4 import (
    Assignment,
    Competence,
    S4Case,
    _allocation,
    _bellman,
    _reactive,
    _reward,
)


@dataclass(frozen=True)
class S4EstimationPeriod:
    period: int
    assignment: Assignment
    reward: float
    competence_before: Competence
    competence_after: Competence
    estimate_before: Competence
    estimate_after: Competence
    observations: tuple[tuple[int, int, float], ...]
    mse_before: float
    posterior_update_l1: float
    decision_seconds: float


@dataclass(frozen=True)
class S4EstimationRun:
    case: str
    policy: str
    estimation: str
    seed: int
    reward: float
    periods: tuple[S4EstimationPeriod, ...]
    total_decision_seconds: float


def _mean_squared_error(estimate: Competence, actual: Competence) -> float:
    cells = [
        (estimate[i][k] - actual[i][k]) ** 2
        for i in range(len(actual)) for k in range(len(actual[i]))
    ]
    return sum(cells) / len(cells)


def _grid_prior(
    n: int, k: int, points: int, means: Competence, sd: float | None,
) -> CompetencePosteriorNK:
    """Bounded grid prior; ``sd=None`` gives the uniform prior."""
    support = tuple(index / (points - 1) for index in range(points))
    rows = []
    for i in range(n):
        row = []
        for j in range(k):
            if sd is None:
                weights = tuple(1.0 / points for _ in support)
            else:
                raw = tuple(exp(-0.5 * ((value - means[i][j]) / sd) ** 2)
                            for value in support)
                total = sum(raw)
                weights = tuple(weight / total for weight in raw)
            row.append(SkillPosterior(support, weights))
        rows.append(tuple(row))
    return tuple(rows)


def run_s4_estimation_planning(
    case: S4Case,
    *,
    policy: str,
    estimation: str,
    seed: int,
    prior_mean: float = 0.5,
    prior_cell_means: Competence | None = None,
    prior_sd: float | None = None,
    observation_parameters: CompetenceObservationParametersNK =
        CompetenceObservationParametersNK(
            production_observation_noise_sd=0.02,
            competence_grid_points=101,
            competence_prior_variance=0.04,
        ),
) -> S4EstimationRun:
    """Run one of the four predeclared S4 factorial conditions.

    Frozen estimation means no likelihood update from observations. Both
    estimation conditions propagate their current posterior through the
    known MIS-v2 transition after executed production, so neither mistakes
    predictable endogenous development for new information.
    """
    if policy not in {"reactive", "bellman"}:
        raise ValueError("policy must be 'reactive' or 'bellman'")
    if estimation not in {"frozen", "updated"}:
        raise ValueError("estimation must be 'frozen' or 'updated'")
    if not 0.0 <= prior_mean <= 1.0:
        raise ValueError("prior_mean must lie in [0, 1]")
    if prior_sd is not None and not 0.0 < prior_sd <= 1.0:
        raise ValueError("prior_sd must lie in (0, 1]")

    n, k = len(case.initial), len(case.initial[0])
    actual = case.initial
    means = (prior_cell_means if prior_cell_means is not None else
             tuple(tuple(prior_mean for _ in range(k)) for _ in range(n)))
    if len(means) != n or any(len(row) != k for row in means):
        raise ValueError("prior_cell_means must match the S4 competence dimensions")
    if any(not 0.0 <= value <= 1.0 for row in means for value in row):
        raise ValueError("prior_cell_means values must lie in [0, 1]")
    posterior = _grid_prior(n, k, observation_parameters.competence_grid_points,
                            means, prior_sd)
    profile = LearningProfileNK(case.eta)
    total_reward = 0.0
    total_decision_seconds = 0.0
    records: list[S4EstimationPeriod] = []

    for period, demand in enumerate(case.demands):
        estimate = posterior_mean_matrix_nk(posterior)
        suffix = S4Case(
            f"{case.name}_suffix_{period}", estimate, case.eta,
            case.demands[period:],
        )
        started = perf_counter()
        if policy == "bellman":
            _, path = _bellman(suffix)
            assignment = path[0]
        else:
            assignment = _reactive(suffix).periods[0].assignment
        decision_seconds = perf_counter() - started
        total_decision_seconds += decision_seconds

        before = actual
        reward = _reward(before, assignment)
        allocation = _allocation(assignment, n, k)
        observed = tuple(
            (agent, task,
             before[agent][task]
             + observation_parameters.production_observation_noise_sd
             * indexed_normal_innovation(seed, period, 0, agent, task))
            for agent, task in assignment
        )
        observation_matrix = [[0.0] * k for _ in range(n)]
        for agent, task, value in observed:
            observation_matrix[agent][task] = value

        # The physical transition is the same MIS-v2 function used by S4.
        actual = mis_v2_transition_nk(before, allocation, profile)
        posterior_update_l1 = 0.0
        if estimation == "updated":
            mean_before_observation = posterior_mean_matrix_nk(posterior)
            posterior = assimilate_production_observations_nk(
                posterior, allocation,
                tuple(tuple(row) for row in observation_matrix),
                observation_parameters.production_observation_noise_sd,
            )
            mean_after_observation = posterior_mean_matrix_nk(posterior)
            posterior_update_l1 = sum(
                abs(mean_after_observation[i][k] - mean_before_observation[i][k])
                for i in range(n) for k in range(len(mean_before_observation[i]))
            ) / (n * k)
        # Prediction is available in both arms; only observed evidence differs.
        posterior = predict_mis_v2_nk(posterior, allocation, case.eta)
        estimate_after = posterior_mean_matrix_nk(posterior)
        total_reward += reward
        records.append(S4EstimationPeriod(
            period=period,
            assignment=assignment,
            reward=reward,
            competence_before=before,
            competence_after=actual,
            estimate_before=estimate,
            estimate_after=estimate_after,
            observations=observed,
            mse_before=_mean_squared_error(estimate, before),
            posterior_update_l1=posterior_update_l1,
            decision_seconds=decision_seconds,
        ))

    return S4EstimationRun(
        case.name, policy, estimation, seed, total_reward, tuple(records),
        total_decision_seconds,
    )


def run_dict(run: S4EstimationRun) -> dict:
    return {
        "case": run.case,
        "policy": run.policy,
        "estimation": run.estimation,
        "seed": run.seed,
        "reward": run.reward,
        "total_decision_seconds": run.total_decision_seconds,
        "periods": [
            {
                "period": row.period,
                "assignment": [list(edge) for edge in row.assignment],
                "reward": row.reward,
                "competence_before": [list(values) for values in row.competence_before],
                "competence_after": [list(values) for values in row.competence_after],
                "estimate_before": [list(values) for values in row.estimate_before],
                "estimate_after": [list(values) for values in row.estimate_after],
                "observations": [list(value) for value in row.observations],
                "mse_before": row.mse_before,
                "posterior_update_l1": row.posterior_update_l1,
                "decision_seconds": row.decision_seconds,
            }
            for row in run.periods
        ],
    }
