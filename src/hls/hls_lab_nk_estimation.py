"""N×K wrappers for HLS's existing bounded competence estimator.

The scalar posterior and its Bayesian update are reused from the historical
3×2 implementation. This module only generalizes their container and applies
the already-defined production, MIS-v2, and formative-observation updates
cell-by-cell; it introduces no estimator or observation model.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .hls_lab_dynamic import (
    SkillPosterior,
    predict_skill_posterior_after_mis,
    update_skill_posterior,
)
from .hls_lab_nk_geometry import CompetenceMatrixNK

CompetencePosteriorNK = tuple[tuple[SkillPosterior, ...], ...]


@dataclass(frozen=True)
class CompetenceObservationParametersNK:
    """The corresponding fields of legacy ``TeachingParameters``.

    Values and defaults are preserved: grid posterior, declared prior
    variance, production observation noise and formative observation noise.
    The efficacy prior remains the existing policy parameter so there is one
    shared value rather than two potentially inconsistent controls.
    """

    production_observation_noise_sd: float = 0.02
    outcome_noise_sd: float = 0.0
    competence_grid_points: int = 101
    competence_prior_variance: float = 0.04

    def __post_init__(self) -> None:
        if any(not isfinite(value) or value < 0.0 for value in (
            self.production_observation_noise_sd, self.outcome_noise_sd,
            self.competence_prior_variance,
        )):
            raise ValueError("observation noise and competence prior variance must be finite and non-negative")
        if self.competence_prior_variance > 0.25:
            raise ValueError("competence_prior_variance must lie in [0, .25]")
        if not isinstance(self.competence_grid_points, int) or self.competence_grid_points < 3:
            raise ValueError("competence_grid_points must be an integer >= 3")


def initialize_competence_posterior_nk(
    estimates: CompetenceMatrixNK,
    parameters: CompetenceObservationParametersNK = CompetenceObservationParametersNK(),
) -> CompetencePosteriorNK:
    """Initialize the historical grid prior independently for every N×K cell."""
    grid_points = parameters.competence_grid_points
    support = tuple(index / (grid_points - 1) for index in range(grid_points))
    posterior_rows: list[tuple[SkillPosterior, ...]] = []
    for row in estimates:
        cells: list[SkillPosterior] = []
        for mean in row:
            variance = min(parameters.competence_prior_variance, mean * (1.0 - mean))
            maximum = mean * (1.0 - mean)
            endpoint_mass = 0.0 if maximum <= 1e-15 else min(1.0, max(0.0, variance / maximum))
            atoms = ((0.0, endpoint_mass * (1.0 - mean)),
                     (mean, 1.0 - endpoint_mass),
                     (1.0, endpoint_mass * mean))
            weights = [0.0] * grid_points
            for value, mass in atoms:
                position = value * (grid_points - 1)
                lower = int(position)
                upper = min(grid_points - 1, lower + 1)
                fraction = position - lower
                weights[lower] += mass * (1.0 - fraction)
                weights[upper] += mass * fraction
            # Match the historical grid estimator's support floor.
            floor_mass = 1e-12
            weights = [(1.0 - floor_mass) * weight + floor_mass / grid_points
                       for weight in weights]
            cells.append(SkillPosterior(support, tuple(weights)))
        posterior_rows.append(tuple(cells))
    return tuple(posterior_rows)


def posterior_mean_matrix_nk(posterior: CompetencePosteriorNK) -> CompetenceMatrixNK:
    return tuple(tuple(cell.mean for cell in row) for row in posterior)


def posterior_variance_matrix_nk(posterior: CompetencePosteriorNK) -> CompetenceMatrixNK:
    return tuple(tuple(cell.variance for cell in row) for row in posterior)


def assimilate_production_observations_nk(
    posterior: CompetencePosteriorNK,
    effort: tuple[tuple[float, ...], ...],
    observations: CompetenceMatrixNK,
    noise_sd: float,
) -> CompetencePosteriorNK:
    """Apply the historical scalar likelihood update independently per cell."""
    return tuple(tuple(
        update_skill_posterior(posterior[i][k], effort[i][k], observations[i][k], noise_sd)
        for k in range(len(posterior[i]))
    ) for i in range(len(posterior)))

def predict_mis_v2_nk(
    posterior: CompetencePosteriorNK,
    effort: tuple[tuple[float, ...], ...],
    eta: tuple[tuple[float, ...], ...],
) -> CompetencePosteriorNK:
    """Push each cell posterior through the existing public MIS-v2 law."""
    return tuple(tuple(
        predict_skill_posterior_after_mis(posterior[i][k], effort[i][k], eta[i][k])
        for k in range(len(posterior[i]))
    ) for i in range(len(posterior)))
