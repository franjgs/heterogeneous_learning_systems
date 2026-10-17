"""Policy-independent exogenous problem generation for HLS Laboratory v1.

The demand process reuses the task-process implementations in synthetic/C5;
emission distributions reuse ``DemandRegime`` and ``generate_problems`` from
the dynamic laboratory. The latent demand state is retained only in the
experimenter-facing trajectory, never added to a policy's decision view.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from random import Random
from types import MappingProxyType, SimpleNamespace
from typing import Hashable, Mapping

from .hls_lab_dynamic import DemandRegime, generate_problems
from .hls_lab_v1_integrated import IntegratedProblem
from .synthetic.c5 import MarkovTaskDemand, NonStationaryTaskDemand, StationaryTaskDemand
from .synthetic.state import WorldState


TaskProcess = MarkovTaskDemand | NonStationaryTaskDemand | StationaryTaskDemand


@dataclass(frozen=True)
class ExogenousEnvironmentConfig:
    """Frozen generator parameters θ and a mapping from latent states to emissions."""

    process: TaskProcess
    emissions: Mapping[Hashable, DemandRegime]
    horizon: int
    resource_budget: float = 3.0

    def __post_init__(self) -> None:
        if not isinstance(self.horizon, int) or self.horizon < 1:
            raise ValueError("horizon must be a positive integer")
        if not isfinite(self.resource_budget) or self.resource_budget < 0:
            raise ValueError("resource_budget must be non-negative")
        emissions = dict(self.emissions)
        if not emissions:
            raise ValueError("at least one emission regime is required")
        process_states = _process_states(self.process)
        if not process_states.issubset(emissions):
            raise ValueError(f"missing emission regime(s) for {process_states - set(emissions)}")
        if isinstance(self.process, NonStationaryTaskDemand):
            missing_times = set(range(self.horizon)) - set(self.process.distributions)
            if missing_times:
                raise ValueError(f"non-stationary process has no distribution for times {missing_times}")
        if any(not isinstance(regime, DemandRegime) for regime in emissions.values()):
            raise TypeError("every environment emission must be a DemandRegime")
        object.__setattr__(self, "emissions", MappingProxyType(emissions))


@dataclass(frozen=True)
class EnvironmentTrajectory:
    """Frozen emitted problems; latent states are experimenter-only diagnostics."""

    seed: int
    problems: tuple[IntegratedProblem, ...]
    latent_states: tuple[Hashable, ...]

    def __post_init__(self) -> None:
        if not self.problems or len(self.problems) != len(self.latent_states):
            raise ValueError("trajectory problems and latent states must be non-empty and aligned")


def _process_states(process: TaskProcess) -> set[Hashable]:
    if isinstance(process, MarkovTaskDemand):
        return set(process.initial_distribution)
    if isinstance(process, StationaryTaskDemand):
        return set(process.distribution)
    if isinstance(process, NonStationaryTaskDemand):
        return {task for distribution in process.distributions.values() for task in distribution}
    raise TypeError(f"unsupported exogenous demand process: {type(process).__name__}")


def _emission_seed(seed: int, time: int) -> int:
    # Separate stream by coordinate without depending on latent-state repr;
    # this also makes emission randomness reproducible for arbitrary hashable
    # task identifiers accepted by the existing C5 process contract.
    payload = f"hls-lab-v1-emission-v1|{seed}|{time}".encode("utf-8")
    return int.from_bytes(sha256(payload).digest()[:8], "big")


def generate_environment_trajectory(
    config: ExogenousEnvironmentConfig, *, seed: int
) -> EnvironmentTrajectory:
    """Generate and freeze one trajectory without reading any organization state.

    For Markov demand, ``process`` generates latent ``z[t]`` and the selected
    existing ``DemandRegime`` emits ``p[t]``. State-transition and emission
    random streams are separate and coordinate seeded. Emitted problems are
    safe to pass to P0/P1/P2; ``latent_states`` is not.
    """
    if not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    rng = Random(seed)
    history: list[object] = []
    latent_states: list[Hashable] = []
    problems: list[IntegratedProblem] = []
    for time in range(config.horizon):
        # C5 task generators are policy-neutral. Their WorldState argument is
        # a constant-shape environment placeholder, not the evolving team.
        environment_state = WorldState(((0.0,),), time=time)
        latent = config.process.sample_task(time, environment_state, history, rng)
        regime = config.emissions[latent]
        emitted = generate_problems(
            ((regime, 1),), seed=_emission_seed(seed, time),
            budget=config.resource_budget,
        )[0]
        # Do not copy the latent-state label into demand_label or problem_id.
        problems.append(IntegratedProblem(emitted, demand_label="observed-demand"))
        latent_states.append(latent)
        history.append(SimpleNamespace(task=latent))
    return EnvironmentTrajectory(seed, tuple(problems), tuple(latent_states))
