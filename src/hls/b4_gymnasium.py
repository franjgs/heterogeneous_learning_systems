"""Gymnasium adapter for the sequential B4 simulator."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .ia_l1_l2_simulation import B4EpisodeEnv


class B4GymnasiumAdapter(gym.Env):
    """Expose B4EpisodeEnv as a flat Box-observation, Discrete-action Gym env.

    ``scenario_factory`` must return an environment whose scenarios share the
    same ordered class set. Scenario and arrival seeds are derived separately
    from the Gymnasium RNG, making a seeded reset reproducible.
    """

    metadata = {"render_modes": []}

    def __init__(self, scenario_factory: Callable[[int], B4EpisodeEnv], classes: Sequence[str]):
        super().__init__()
        self.scenario_factory = scenario_factory
        self.classes = tuple(classes)
        self.observation_keys = (
            "time_fraction", "l1_backlog_norm", "l2_backlog_norm",
            "l1_available_fraction", "l2_available_fraction", "l1_busy_fraction",
            "l2_busy_fraction", "coordination_cost_norm", "ai_recommendation_rate_so_far",
            "ai_observations_norm", "deadline_pressure_l1", "deadline_pressure_l2",
            "arrival_rate_recent_norm", "arrival_rate_previous_norm", "arrival_rate_trend_norm",
            *(f"l1_queue_class_{key}" for key in self.classes),
            *(f"l2_queue_class_{key}" for key in self.classes),
            *(f"l1_competence_{key}" for key in self.classes),
            *(f"l2_competence_{key}" for key in self.classes),
            *(f"l1_competence_dispersion_{key}" for key in self.classes),
            *(f"l2_competence_dispersion_{key}" for key in self.classes),
            "l1_competence_dispersion", "l2_competence_dispersion",
            "l1_competence_dispersion_coverage", "l2_competence_dispersion_coverage",
        )
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(
            low=np.zeros(len(self.observation_keys), dtype=np.float32),
            high=np.ones(len(self.observation_keys), dtype=np.float32),
            dtype=np.float32,
        )
        self._inner: B4EpisodeEnv | None = None
        self.episode_scenario_seed: int | None = None
        self.episode_trace_seed: int | None = None

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)
        factory_seed = int(self.np_random.integers(0, 2**31 - 1))
        trace_seed = int(self.np_random.integers(0, 2**31 - 1))
        self.episode_trace_seed = trace_seed
        self._inner = self.scenario_factory(factory_seed)
        self.episode_scenario_seed = int(getattr(self._inner, "scenario_seed", factory_seed))
        observation, info = self._inner.reset(trace_seed)
        # Seeds are reproducibility metadata in info, never part of observations.
        info = dict(info, scenario_seed=self.episode_scenario_seed, trace_seed=trace_seed)
        return self._vector(observation), info

    def step(self, action: int):
        if self._inner is None:
            raise RuntimeError("reset must be called before step")
        observation, reward, terminated, truncated, info = self._inner.step(int(action))
        info = dict(info, scenario_seed=self.episode_scenario_seed, trace_seed=self.episode_trace_seed)
        return self._vector(observation), float(reward), bool(terminated), bool(truncated), info

    def _vector(self, observation: dict[str, float]) -> np.ndarray:
        missing = set(self.observation_keys) - observation.keys()
        extra = observation.keys() - set(self.observation_keys)
        if missing or extra:
            raise ValueError(f"observation schema changed (missing={sorted(missing)}, extra={sorted(extra)})")
        vector = np.asarray([observation[key] for key in self.observation_keys], dtype=np.float32)
        if not np.isfinite(vector).all() or (vector < 0).any() or (vector > 1).any():
            raise ValueError("normalized observation values must be finite and within [0,1]")
        return vector
