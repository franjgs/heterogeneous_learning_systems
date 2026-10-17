"""N×K emissions for the existing exogenous C5 demand processes.

This module generalizes only the problem catalogue/emission layer.  Task
arrival dynamics are the existing stationary, time-indexed and first-order
Markov processes in :mod:`hls.synthetic.c5`; no organization state is read.
Environmental state is experimenter-facing metadata and is never inserted in
the N×K policy decision view.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from random import Random
from types import MappingProxyType, SimpleNamespace
from typing import Hashable, Mapping

from .hls_lab_dynamic import DemandRegime, generate_problems
from .hls_lab_nk_geometry import ProblemSpecNK
from .synthetic.c5 import (
    MarkovTaskDemand,
    NonStationaryTaskDemand,
    StationaryTaskDemand,
)
from .synthetic.state import WorldState

TaskProcessNK = MarkovTaskDemand | NonStationaryTaskDemand | StationaryTaskDemand


@dataclass(frozen=True)
class DemandRegimeNK:
    """A finite emission catalogue selected under one latent demand state.

    Problem types are independent of K: a K-dimensional organization may
    face any positive number of distinct problem types.  Each type reuses the
    canonical :class:`ProblemSpecNK` contract; the environment-level budget
    is applied at emission, matching the historical v1 environment.
    """

    label: str
    problems: tuple[ProblemSpecNK, ...]
    probabilities: tuple[float, ...]

    def __post_init__(self) -> None:
        problems = tuple(self.problems)
        probabilities = tuple(float(value) for value in self.probabilities)
        if (not isinstance(self.label, str) or not self.label.strip() or not problems
                or len(problems) != len(probabilities)):
            raise ValueError("invalid N×K demand regime")
        if len({problem.problem_id for problem in problems}) != len(problems):
            raise ValueError("problem identifiers must be unique within a demand regime")
        if (any(not isfinite(value) or value < 0 for value in probabilities)
                or abs(sum(probabilities) - 1.0) > 1e-9):
            raise ValueError("problem probabilities must be finite, non-negative and sum to one")
        dimensions = {len(problem.requirements) for problem in problems}
        if len(dimensions) != 1:
            raise ValueError("all problem types in a demand regime must share K")
        object.__setattr__(self, "problems", problems)
        object.__setattr__(self, "probabilities", probabilities)

    @property
    def n_skills(self) -> int:
        return len(self.problems[0].requirements)


@dataclass(frozen=True)
class ExogenousEnvironmentConfigNK:
    """Existing C5 demand law, finite emissions, horizon and shared budget."""

    process: TaskProcessNK
    emissions: Mapping[Hashable, DemandRegimeNK]
    horizon: int
    resource_budget: float = 3.0

    def __post_init__(self) -> None:
        if not isinstance(self.horizon, int) or isinstance(self.horizon, bool) or self.horizon < 1:
            raise ValueError("horizon must be a positive integer")
        if not isfinite(self.resource_budget) or self.resource_budget < 0:
            raise ValueError("resource_budget must be finite and non-negative")
        emissions = dict(self.emissions)
        if not emissions:
            raise ValueError("at least one emission regime is required")
        states = _process_states(self.process)
        if not states.issubset(emissions):
            raise ValueError(f"missing emission regime(s) for {states - set(emissions)}")
        if any(not isinstance(regime, DemandRegimeNK) for regime in emissions.values()):
            raise TypeError("every emission must be a DemandRegimeNK")
        dimensions = {regime.n_skills for regime in emissions.values()}
        if len(dimensions) != 1:
            raise ValueError("all emissions must have the same competence dimension K")
        if isinstance(self.process, NonStationaryTaskDemand):
            missing_times = set(range(self.horizon)) - set(self.process.distributions)
            if missing_times:
                raise ValueError(f"non-stationary process has no distribution for times {missing_times}")
        object.__setattr__(self, "emissions", MappingProxyType(emissions))

    @property
    def n_skills(self) -> int:
        return next(iter(self.emissions.values())).n_skills


@dataclass(frozen=True)
class EnvironmentTrajectoryNK:
    """Frozen exogenous problems plus environment-only replay metadata."""

    seed: int
    config: ExogenousEnvironmentConfigNK
    problems: tuple[ProblemSpecNK, ...]
    latent_states: tuple[Hashable, ...]
    regime_labels: tuple[str, ...]

    def __post_init__(self) -> None:
        if (not self.problems or len(self.problems) != len(self.latent_states)
                or len(self.problems) != len(self.regime_labels)
                or len(self.problems) != self.config.horizon):
            raise ValueError("trajectory problems and environment metadata must be aligned")


def _process_states(process: TaskProcessNK) -> set[Hashable]:
    if isinstance(process, MarkovTaskDemand):
        return set(process.initial_distribution)
    if isinstance(process, StationaryTaskDemand):
        return set(process.distribution)
    if isinstance(process, NonStationaryTaskDemand):
        return {task for distribution in process.distributions.values() for task in distribution}
    raise TypeError(f"unsupported demand process: {type(process).__name__}")


def _emission_seed(seed: int, time: int) -> int:
    """Keep the v1 coordinate-separated emission random stream convention."""
    payload = f"hls-lab-v1-emission-v1|{seed}|{time}".encode("utf-8")
    return int.from_bytes(sha256(payload).digest()[:8], "big")


def _select_problem(regime: DemandRegimeNK, *, seed: int, budget: float) -> ProblemSpecNK:
    # Preserve the legacy emitter's draw ordering, stable requirement-derived
    # identifiers, and equal 2-skill CES weights for its exact 3×2-compatible
    # case.  Other K values use the same categorical inverse-CDF convention.
    legacy_2d = (
        regime.n_skills == 2
        and all(problem.ces_weights == (0.5, 0.5) for problem in regime.problems)
    )
    if legacy_2d:
        old = DemandRegime(
            regime.label,
            tuple(problem.requirements for problem in regime.problems),
            regime.probabilities,
        )
        emitted = generate_problems(((old, 1),), seed=seed, budget=budget)[0]
        return ProblemSpecNK(
            emitted.problem_id, emitted.requirements, budget, (0.5, 0.5)
        )

    rng = Random(seed)
    draw = rng.random()
    cumulative = 0.0
    selected = len(regime.probabilities) - 1
    for index, probability in enumerate(regime.probabilities):
        cumulative += probability
        if draw < cumulative:
            selected = index
            break
    problem = regime.problems[selected]
    return ProblemSpecNK(
        problem.problem_id, problem.requirements, budget, problem.ces_weights
    )


def generate_environment_trajectory_nk(
    config: ExogenousEnvironmentConfigNK, *, seed: int
) -> EnvironmentTrajectoryNK:
    """Generate and freeze a policy-independent K-dimensional demand path.

    C5 process randomness uses one sequential ``Random(seed)`` stream as in
    the existing v1 generator. Emissions use the existing SHA-256
    seed/period coordinate stream, so organization policies and their
    observation draws cannot consume or perturb future demand randomness.
    The C5 ``WorldState`` argument is a fixed-shape environmental placeholder;
    it is not initialized from or coupled to the organization.
    """
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    rng = Random(seed)
    history: list[object] = []
    problems: list[ProblemSpecNK] = []
    states: list[Hashable] = []
    labels: list[str] = []
    for time in range(config.horizon):
        environment_state = WorldState(((0.0,),), time=time)
        latent = config.process.sample_task(time, environment_state, history, rng)
        regime = config.emissions[latent]
        problems.append(_select_problem(regime, seed=_emission_seed(seed, time),
                                        budget=config.resource_budget))
        states.append(latent)
        labels.append(regime.label)
        history.append(SimpleNamespace(task=latent))
    return EnvironmentTrajectoryNK(seed, config, tuple(problems), tuple(states), tuple(labels))
