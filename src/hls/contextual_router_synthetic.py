"""Self-contained synthetic environment for contextual-router validation.

The true response functions remain inside the executor. The router receives
only the selected candidate's noisy quality/cost outcome after execution.
"""

from __future__ import annotations

from math import isfinite
from random import Random

from .contextual_router import CandidateSpec, ExecutionOutcome, QuerySpec, _number, _vector


def _clip(value: float, low: float, high: float) -> float:
    return min(high, max(low, value))


class SyntheticCandidateResponse:
    """Latent synthetic functions; construct for the environment only."""

    __slots__ = ("candidate_id", "quality_intercept", "quality_weights",
                 "cost_intercept", "cost_weights")

    def __init__(self, candidate_id: str, quality_intercept: float,
                 quality_weights, cost_intercept: float, cost_weights):
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ValueError("candidate_id must be non-empty")
        q_intercept = _number(quality_intercept, "quality_intercept")
        c_intercept = _number(cost_intercept, "cost_intercept")
        q_weights = _vector(quality_weights, "quality_weights")
        c_weights = _vector(cost_weights, "cost_weights")
        if len(q_weights) != len(c_weights):
            raise ValueError("synthetic quality/cost context dimensions must match")
        self.candidate_id = candidate_id
        self.quality_intercept = q_intercept
        self.quality_weights = q_weights
        self.cost_intercept = c_intercept
        self.cost_weights = c_weights

    def _quality(self, query: QuerySpec) -> float:
        raw = self.quality_intercept + sum(
            a * x for a, x in zip(self.quality_weights, query.context)
        )
        if not isfinite(raw):
            raise ArithmeticError("synthetic quality arithmetic is non-finite")
        return _clip(raw, 0.0, 1.0)

    def _cost(self, query: QuerySpec) -> float:
        raw = self.cost_intercept + sum(
            a * x for a, x in zip(self.cost_weights, query.context)
        )
        if not isfinite(raw):
            raise ArithmeticError("synthetic cost arithmetic is non-finite")
        return max(0.0, raw)


class SyntheticContextualEnvironment:
    """No-external-service executor with reproducible bounded feedback noise.

    Latent quality is ``clip(a_i + b_i @ context, 0, 1)`` and latent monetary
    cost is ``max(0, d_i + g_i @ context)``. Each observed value receives
    independent zero-mean uniform noise, bounded so the declared outcome
    domains remain valid. Noise radii are instrumentation controls, not HLS
    resources or article parameters.
    """

    __slots__ = ("currency", "accounting_version", "evaluator_version",
                 "_responses", "_quality_rng", "_cost_rng",
                 "_quality_noise_radius", "_cost_noise_radius", "_seed")

    def __init__(self, responses, *, currency: str = "SIM-USD",
                 accounting_version: str = "sim-accounting-v1",
                 evaluator_version: str = "quality-rubric-v1",
                 quality_noise_radius: float = 0.0,
                 cost_noise_radius: float = 0.0,
                 seed: int = 0):
        rows = tuple(responses)
        if not rows:
            raise ValueError("at least one synthetic response is required")
        ids = tuple(row.candidate_id for row in rows)
        if len(set(ids)) != len(ids):
            raise ValueError("synthetic response candidate IDs must be unique")
        dimensions = {len(row.quality_weights) for row in rows}
        if len(dimensions) != 1:
            raise ValueError("all synthetic responses must share context dimension")
        for name, value in (("currency", currency),
                            ("accounting_version", accounting_version),
                            ("evaluator_version", evaluator_version)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        q_radius = _number(quality_noise_radius, "quality_noise_radius")
        c_radius = _number(cost_noise_radius, "cost_noise_radius")
        if q_radius < 0 or c_radius < 0:
            raise ValueError("noise radii must be non-negative")
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise ValueError("seed must be an integer")
        self.currency = currency
        self.accounting_version = accounting_version
        self.evaluator_version = evaluator_version
        self._seed = seed
        self._responses = {row.candidate_id: row for row in rows}
        # Independent deterministic streams; no dependence on router draws.
        self._quality_rng = Random(seed ^ 0x5A17)
        self._cost_rng = Random(seed ^ 0xC057)
        self._quality_noise_radius = q_radius
        self._cost_noise_radius = c_radius

    @property
    def replay_metadata(self) -> tuple[tuple[str, str], ...]:
        """Non-oracle replay settings; latent response functions are excluded."""
        return (
            ("executor_seed", str(self._seed)),
            ("quality_noise_radius", repr(self._quality_noise_radius)),
            ("cost_noise_radius", repr(self._cost_noise_radius)),
            ("currency", self.currency),
            ("accounting_version", self.accounting_version),
            ("evaluator_version", self.evaluator_version),
        )

    def execute(self, candidate: CandidateSpec, query: QuerySpec) -> ExecutionOutcome:
        try:
            response = self._responses[candidate.candidate_id]
        except KeyError as exc:
            raise ValueError("candidate has no synthetic response model") from exc
        if len(query.context) != len(response.quality_weights):
            raise ValueError("query context dimension does not match environment")
        quality_true = response._quality(query)
        cost_true = response._cost(query)
        q_radius = min(self._quality_noise_radius, quality_true, 1.0 - quality_true)
        c_radius = min(self._cost_noise_radius, cost_true)
        quality_observed = quality_true + self._quality_rng.uniform(-q_radius, q_radius)
        cost_observed = cost_true + self._cost_rng.uniform(-c_radius, c_radius)
        if not isfinite(quality_observed) or not isfinite(cost_observed):
            raise ArithmeticError("synthetic outcome is non-finite")
        return ExecutionOutcome(
            query.query_id,
            candidate.candidate_id,
            _clip(quality_observed, 0.0, 1.0),
            max(0.0, cost_observed),
            self.currency,
            self.accounting_version,
            self.evaluator_version,
        )
