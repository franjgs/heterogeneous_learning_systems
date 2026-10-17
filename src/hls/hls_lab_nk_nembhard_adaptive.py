"""Observation, online productivity estimation, and adaptive Nembhard routing.

The decision view intentionally contains no true profile or true productivity.
The execution layer owns those latent values and reveals only post-action
observations to the estimator.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from random import Random

from .hls_lab_nk_geometry import (
    OrganizationResourcesNK,
    ProblemSpecNK,
    ProductiveAllocationNK,
    enumerate_productive_action_entries_nk,
)
from .hls_lab_nk_production import FunctionalResultNK, evaluate_problem_nk, functional_effort_rank_nk

Matrix = tuple[tuple[float, ...], ...]
NullableMatrix = tuple[tuple[float | None, ...], ...]


def _finite_nonnegative(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be finite and non-negative")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite and non-negative") from exc
    if not isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return result


def _nonnegative_matrix(values, name: str) -> Matrix:
    try:
        result = tuple(tuple(_finite_nonnegative(value, name) for value in row) for row in values)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite non-negative matrix") from exc
    if not result or not result[0] or any(len(row) != len(result[0]) for row in result):
        raise ValueError(f"{name} must be a non-empty rectangular matrix")
    return result


@dataclass(frozen=True)
class NembhardAdaptiveRouterConfigNK:
    """Observation and exploration controls for one reproducible episode.

    Observation noise is additive Gaussian noise on work-output ``z_obs``.
    Exploration and observation use independent seeded random streams.
    """

    epsilon: float = 0.0
    exploration_seed: int = 0
    observation_noise_stddev: float = 0.0
    observation_seed: int = 0
    initial_productivity_estimate: float | Matrix = 0.0
    minimum_observation_work: float = 1e-9

    def __post_init__(self) -> None:
        if isinstance(self.epsilon, bool):
            raise ValueError("epsilon must lie in [0, 1]")
        try:
            epsilon = float(self.epsilon)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("epsilon must lie in [0, 1]") from exc
        if not isfinite(epsilon) or not 0.0 <= epsilon <= 1.0:
            raise ValueError("epsilon must lie in [0, 1]")
        for name in ("exploration_seed", "observation_seed"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"{name} must be an integer")
        noise = _finite_nonnegative(self.observation_noise_stddev, "observation_noise_stddev")
        threshold = _finite_nonnegative(self.minimum_observation_work, "minimum_observation_work")
        if threshold <= 0:
            raise ValueError("minimum_observation_work must be strictly positive")
        initial = self.initial_productivity_estimate
        if isinstance(initial, (int, float)) and not isinstance(initial, bool):
            initial = _finite_nonnegative(initial, "initial_productivity_estimate")
        else:
            initial = _nonnegative_matrix(initial, "initial_productivity_estimate")
        object.__setattr__(self, "epsilon", epsilon)
        object.__setattr__(self, "observation_noise_stddev", noise)
        object.__setattr__(self, "minimum_observation_work", threshold)
        object.__setattr__(self, "initial_productivity_estimate", initial)


@dataclass(frozen=True)
class ProductivityEstimateCellNK:
    """Welford running statistics for nonnegative observed productivity."""

    mean: float
    observation_count: int = 0
    m2: float = 0.0

    def __post_init__(self) -> None:
        mean = _finite_nonnegative(self.mean, "productivity estimate")
        m2 = _finite_nonnegative(self.m2, "productivity dispersion")
        if (not isinstance(self.observation_count, int)
                or isinstance(self.observation_count, bool) or self.observation_count < 0):
            raise ValueError("observation_count must be a non-negative integer")
        if self.observation_count == 0 and m2 != 0:
            raise ValueError("unobserved estimator cells must have zero dispersion")
        object.__setattr__(self, "mean", mean)
        object.__setattr__(self, "m2", m2)

    @property
    def sample_variance(self) -> float | None:
        if self.observation_count < 2:
            return None
        return self.m2 / (self.observation_count - 1)

    def update(self, value: float) -> "ProductivityEstimateCellNK":
        observed = _finite_nonnegative(value, "observed productivity")
        count = self.observation_count + 1
        delta = observed - self.mean
        mean = self.mean + delta / count
        delta_after = observed - mean
        return ProductivityEstimateCellNK(mean, count, self.m2 + delta * delta_after)


@dataclass(frozen=True)
class ProductivityEstimatorStateNK:
    """Cell-specific online mean and dispersion state."""

    cells: tuple[tuple[ProductivityEstimateCellNK, ...], ...]

    def __post_init__(self) -> None:
        rows = tuple(tuple(cell for cell in row) for row in self.cells)
        if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
            raise ValueError("estimator cells must be a non-empty rectangular N×K matrix")
        if any(not isinstance(cell, ProductivityEstimateCellNK) for row in rows for cell in row):
            raise TypeError("estimator state requires ProductivityEstimateCellNK cells")
        object.__setattr__(self, "cells", rows)

    @property
    def means(self) -> Matrix:
        return tuple(tuple(cell.mean for cell in row) for row in self.cells)

    @property
    def counts(self) -> tuple[tuple[int, ...], ...]:
        return tuple(tuple(cell.observation_count for cell in row) for row in self.cells)

    @property
    def sample_variances(self) -> tuple[tuple[float | None, ...], ...]:
        return tuple(tuple(cell.sample_variance for cell in row) for row in self.cells)

    @property
    def n_agents(self) -> int:
        return len(self.cells)

    @property
    def n_skills(self) -> int:
        return len(self.cells[0])


def initialize_productivity_estimator_nk(
    n_agents: int,
    n_skills: int,
    initial_estimate: float | Matrix = 0.0,
) -> ProductivityEstimatorStateNK:
    if (not isinstance(n_agents, int) or isinstance(n_agents, bool) or n_agents < 1
            or not isinstance(n_skills, int) or isinstance(n_skills, bool) or n_skills < 1):
        raise ValueError("estimator dimensions must be positive integers")
    if isinstance(initial_estimate, (int, float)) and not isinstance(initial_estimate, bool):
        value = _finite_nonnegative(initial_estimate, "initial_productivity_estimate")
        means = ((value,) * n_skills,) * n_agents
    else:
        means = _nonnegative_matrix(initial_estimate, "initial_productivity_estimate")
        if (len(means), len(means[0])) != (n_agents, n_skills):
            raise ValueError("initial productivity estimate dimensions must match N×K")
    return ProductivityEstimatorStateNK(tuple(tuple(
        ProductivityEstimateCellNK(value) for value in row
    ) for row in means))


def observe_nembhard_work_outputs_nk(
    work: Matrix,
    true_work_outputs: Matrix,
    *,
    noise_stddev: float,
    rng: Random,
) -> NullableMatrix:
    """Observe per-cell work output; zero-work cells return ``None``.

    A noise draw is consumed for each coordinate when noise is enabled, even
    for zero work. Its value is discarded, preserving coordinatewise stream
    alignment across different assignments without creating an observation.
    """
    noise = _finite_nonnegative(noise_stddev, "noise_stddev")
    exposure = _nonnegative_matrix(work, "work")
    outputs = _nonnegative_matrix(true_work_outputs, "true_work_outputs")
    if (len(exposure), len(exposure[0])) != (len(outputs), len(outputs[0])):
        raise ValueError("work and output dimensions must match")
    result: list[tuple[float | None, ...]] = []
    for i, row in enumerate(exposure):
        observations: list[float | None] = []
        for k, amount in enumerate(row):
            epsilon = rng.gauss(0.0, noise) if noise > 0.0 else 0.0
            observations.append(None if amount == 0.0 else outputs[i][k] + epsilon)
        result.append(tuple(observations))
    return tuple(result)


def update_productivity_estimator_nk(
    state: ProductivityEstimatorStateNK,
    work: Matrix,
    observations: NullableMatrix,
    *,
    minimum_observation_work: float,
) -> ProductivityEstimatorStateNK:
    """Update from ``z_obs / work`` only; negative rates are clipped to zero.

    Positive work at or below the configured threshold is traceable but does
    not update the estimator because division would amplify observation noise.
    """
    threshold = _finite_nonnegative(minimum_observation_work, "minimum_observation_work")
    if threshold <= 0:
        raise ValueError("minimum_observation_work must be strictly positive")
    exposures = _nonnegative_matrix(work, "work")
    obs = tuple(tuple(value for value in row) for row in observations)
    if ((len(exposures), len(exposures[0])) != (state.n_agents, state.n_skills)
            or len(obs) != state.n_agents or any(len(row) != state.n_skills for row in obs)):
        raise ValueError("work and observations must match estimator N×K dimensions")
    cells: list[tuple[ProductivityEstimateCellNK, ...]] = []
    for i in range(state.n_agents):
        row: list[ProductivityEstimateCellNK] = []
        for k in range(state.n_skills):
            exposure = exposures[i][k]
            observation = obs[i][k]
            old = state.cells[i][k]
            if observation is None:
                if exposure != 0.0:
                    raise ValueError("positive work requires an observation")
                row.append(old)
                continue
            if isinstance(observation, bool):
                raise ValueError("observations must be finite numbers or None")
            try:
                observed_output = float(observation)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("observations must be finite numbers or None") from exc
            if not isfinite(observed_output):
                raise ValueError("observations must be finite numbers or None")
            if exposure == 0.0:
                raise ValueError("zero work cannot carry an informative observation")
            if exposure <= threshold:
                row.append(old)
                continue
            observed_productivity = max(0.0, observed_output / exposure)
            row.append(old.update(observed_productivity))
        cells.append(tuple(row))
    return ProductivityEstimatorStateNK(tuple(cells))


@dataclass(frozen=True)
class NembhardAdaptiveDecisionViewNK:
    """Decision-only information; true ``k,p,r`` and output are absent."""

    resources: OrganizationResourcesNK
    problem: ProblemSpecNK
    estimator: ProductivityEstimatorStateNK
    previous_allocations: tuple[ProductiveAllocationNK, ...]
    observable_experience: Matrix
    period_duration: float

    def __post_init__(self) -> None:
        n, k = len(self.resources.agent_ids), len(self.resources.skill_ids)
        if len(self.problem.requirements) != k:
            raise ValueError("problem dimension must match router resources")
        if (self.estimator.n_agents, self.estimator.n_skills) != (n, k):
            raise ValueError("estimator dimensions must match router resources")
        experience = _nonnegative_matrix(self.observable_experience, "observable_experience")
        if (len(experience), len(experience[0])) != (n, k):
            raise ValueError("observable experience dimensions must match N×K")
        history = tuple(tuple(tuple(float(x) for x in row) for row in action)
                        for action in self.previous_allocations)
        if any(len(action) != n or any(len(row) != k for row in action) for action in history):
            raise ValueError("previous allocation history must contain N×K actions")
        duration = _finite_nonnegative(self.period_duration, "period_duration")
        if duration <= 0:
            raise ValueError("period_duration must be positive")
        object.__setattr__(self, "observable_experience", experience)
        object.__setattr__(self, "previous_allocations", history)
        object.__setattr__(self, "period_duration", duration)


@dataclass(frozen=True)
class NembhardAdaptiveDecisionNK:
    router_id: str
    catalog_action_id: int
    allocation: ProductiveAllocationNK
    predicted_outputs: tuple[float, ...]
    predicted_functional_result: FunctionalResultNK
    rank: tuple[float, float, float, float]
    feasible_candidate_count: int
    exploratory: bool


@dataclass(frozen=True)
class NembhardAdaptiveRouterNK:
    """Epsilon-greedy router over estimated current productivity."""

    router_id: str = "nembhard_adaptive"

    def __post_init__(self) -> None:
        if self.router_id != "nembhard_adaptive":
            raise ValueError("router_id must be 'nembhard_adaptive'")

    def choose(
        self,
        view: NembhardAdaptiveDecisionViewNK,
        *,
        epsilon: float,
        rng: Random,
        max_candidates: int,
        per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None = None,
    ) -> NembhardAdaptiveDecisionNK:
        if isinstance(epsilon, bool):
            raise ValueError("epsilon must lie in [0, 1]")
        try:
            exploration_probability = float(epsilon)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("epsilon must lie in [0, 1]") from exc
        if not isfinite(exploration_probability) or not 0 <= exploration_probability <= 1:
            raise ValueError("epsilon must lie in [0, 1]")
        entries = enumerate_productive_action_entries_nk(
            view.resources,
            view.problem,
            max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
        )
        means = view.estimator.means
        ranked = []
        for catalog_id, allocation in entries:
            outputs = tuple(sum(
                allocation[i][skill] * means[i][skill] * view.period_duration
                for i in range(view.estimator.n_agents)
            ) for skill in range(view.estimator.n_skills))
            effort = sum(sum(row) for row in allocation)
            rank = functional_effort_rank_nk(outputs, view.problem.requirements, effort)
            ranked.append((rank, catalog_id, allocation, outputs))
        best_index = max(range(len(ranked)), key=lambda index: ranked[index][0])
        exploratory = exploration_probability > 0.0 and rng.random() < exploration_probability
        selected_index = rng.randrange(len(ranked)) if exploratory else best_index
        rank, catalog_id, allocation, outputs = ranked[selected_index]
        return NembhardAdaptiveDecisionNK(
            self.router_id,
            catalog_id,
            allocation,
            outputs,
            evaluate_problem_nk(outputs, view.problem.requirements),
            rank,
            len(entries),
            exploratory,
        )
