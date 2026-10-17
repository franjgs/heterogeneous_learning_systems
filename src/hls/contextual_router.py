"""Contextual quality/cost routing with selected-candidate-only feedback.

This is an HLS adaptation specified in ``HLS_MIXLLM_ROUTER_CONTRACT.md``.
It is deliberately separate from N×K competence, MIS-v2 and Nembhard routes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from math import isfinite, sqrt
from random import Random
from typing import Protocol, Sequence


Vector = tuple[float, ...]
Matrix = tuple[tuple[float, ...], ...]


def _number(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be finite")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _vector(values, name: str, *, nonnegative: bool = False) -> Vector:
    try:
        result = tuple(_number(value, name) for value in values)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite numeric vector") from exc
    if not result:
        raise ValueError(f"{name} must be non-empty")
    if nonnegative and any(value < 0 for value in result):
        raise ValueError(f"{name} must be non-negative")
    return result


def _matvec(matrix: Matrix, vector: Vector) -> Vector:
    return tuple(sum(value * coefficient for value, coefficient in zip(row, vector))
                 for row in matrix)


def _dot(left: Vector, right: Vector) -> float:
    result = sum(a * b for a, b in zip(left, right))
    if not isfinite(result):
        raise ArithmeticError("prediction arithmetic produced a non-finite value")
    return result


def _solve(matrix: Matrix, rhs: Vector) -> Vector:
    """Solve a small positive-definite system with pivoted Gauss-Jordan."""
    n = len(rhs)
    augmented = [list(matrix[i]) + [rhs[i]] for i in range(n)]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) <= 1e-15:
            raise ArithmeticError("ridge system is numerically singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [value - factor * pivot_value
                              for value, pivot_value in zip(augmented[row], augmented[column])]
    return tuple(augmented[i][-1] for i in range(n))


@dataclass(frozen=True)
class QuerySpec:
    query_id: str
    context: Vector
    quality_requirement: float
    cost_budget: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.query_id, str) or not self.query_id.strip():
            raise ValueError("query_id must be a non-empty string")
        context = _vector(self.context, "context")
        quality = _number(self.quality_requirement, "quality_requirement")
        if not 0.0 <= quality <= 1.0:
            raise ValueError("quality_requirement must lie in [0, 1]")
        budget = self.cost_budget
        if budget is not None:
            budget = _number(budget, "cost_budget")
            if budget < 0:
                raise ValueError("cost_budget must be non-negative")
        object.__setattr__(self, "context", context)
        object.__setattr__(self, "quality_requirement", quality)
        object.__setattr__(self, "cost_budget", budget)


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    eligible_query_ids: tuple[str, ...] | None = None
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.candidate_id, str) or not self.candidate_id.strip():
            raise ValueError("candidate_id must be a non-empty string")
        eligible = self.eligible_query_ids
        if eligible is not None:
            eligible = tuple(eligible)
            if any(not isinstance(item, str) or not item for item in eligible):
                raise ValueError("eligible_query_ids must contain non-empty strings")
            if len(set(eligible)) != len(eligible):
                raise ValueError("eligible_query_ids cannot contain duplicates")
        metadata = tuple(tuple(item) for item in self.metadata)
        if any(len(item) != 2 or any(not isinstance(x, str) for x in item)
               for item in metadata):
            raise ValueError("metadata must be (string key, string value) pairs")
        if len({item[0] for item in metadata}) != len(metadata):
            raise ValueError("candidate metadata keys must be unique")
        object.__setattr__(self, "eligible_query_ids", eligible)
        object.__setattr__(self, "metadata", metadata)

    def is_eligible_for(self, query: QuerySpec) -> bool:
        return self.eligible_query_ids is None or query.query_id in self.eligible_query_ids


@dataclass(frozen=True)
class CandidatePrior:
    candidate_id: str
    quality_coefficients: Vector
    cost_coefficients: Vector

    def __post_init__(self) -> None:
        if not isinstance(self.candidate_id, str) or not self.candidate_id.strip():
            raise ValueError("prior candidate_id must be a non-empty string")
        object.__setattr__(self, "quality_coefficients",
                           _vector(self.quality_coefficients, "quality prior coefficients"))
        object.__setattr__(self, "cost_coefficients",
                           _vector(self.cost_coefficients, "cost prior coefficients"))
        if len(self.quality_coefficients) != len(self.cost_coefficients):
            raise ValueError("quality and cost prior dimensions must match")


@dataclass(frozen=True)
class ContextualRouterConfig:
    context_dimension: int
    include_intercept: bool = True
    quality_regularization: float = 1.0
    cost_regularization: float = 1.0
    currency: str = "SIM-USD"
    accounting_version: str = "sim-accounting-v1"
    evaluator_version: str = "quality-rubric-v1"
    epsilon: float = 0.0
    exploration_seed: int = 0

    def __post_init__(self) -> None:
        if (not isinstance(self.context_dimension, int) or isinstance(self.context_dimension, bool)
                or self.context_dimension < 1):
            raise ValueError("context_dimension must be a positive integer")
        for name in ("quality_regularization", "cost_regularization"):
            value = _number(getattr(self, name), name)
            if value <= 0:
                raise ValueError(f"{name} must be strictly positive")
            object.__setattr__(self, name, value)
        for name in ("currency", "accounting_version", "evaluator_version"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        epsilon = _number(self.epsilon, "epsilon")
        if not 0.0 <= epsilon <= 1.0:
            raise ValueError("epsilon must lie in [0, 1]")
        if (not isinstance(self.exploration_seed, int)
                or isinstance(self.exploration_seed, bool)):
            raise ValueError("exploration_seed must be an integer")
        object.__setattr__(self, "epsilon", epsilon)

    @property
    def feature_dimension(self) -> int:
        return self.context_dimension + int(self.include_intercept)


@dataclass(frozen=True)
class RidgeState:
    prior: Vector
    regularization: float
    gram: Matrix
    cross_product: Vector
    sum_squares: float = 0.0
    observation_count: int = 0

    @classmethod
    def initialize(cls, prior: Vector, regularization: float) -> "RidgeState":
        dimension = len(prior)
        return cls(prior, regularization,
                   tuple((0.0,) * dimension for _ in range(dimension)),
                   (0.0,) * dimension)

    @property
    def system_matrix(self) -> Matrix:
        return tuple(tuple(self.gram[i][j] + (self.regularization if i == j else 0.0)
                           for j in range(len(self.prior)))
                     for i in range(len(self.prior)))

    @property
    def coefficients(self) -> Vector:
        rhs = tuple(self.regularization * self.prior[i] + self.cross_product[i]
                    for i in range(len(self.prior)))
        return _solve(self.system_matrix, rhs)

    def update(self, features: Vector, outcome: float) -> "RidgeState":
        if len(features) != len(self.prior):
            raise ValueError("feature dimension does not match ridge prior")
        y = _number(outcome, "observed outcome")
        gram = tuple(tuple(self.gram[i][j] + features[i] * features[j]
                           for j in range(len(self.prior)))
                     for i in range(len(self.prior)))
        cross = tuple(self.cross_product[i] + features[i] * y
                      for i in range(len(self.prior)))
        return RidgeState(self.prior, self.regularization, gram, cross,
                          self.sum_squares + y * y, self.observation_count + 1)

    def predict_raw(self, features: Vector) -> tuple[float, float, float | None]:
        beta = self.coefficients
        prediction = _dot(features, beta)
        leverage_vector = _solve(self.system_matrix, features)
        leverage = max(0.0, _dot(features, leverage_vector))
        residual_std: float | None = None
        degrees = self.observation_count - len(self.prior)
        if degrees > 0:
            fitted_data_term = _dot(beta, self.cross_product)
            quadratic = sum(beta[i] * self.gram[i][j] * beta[j]
                            for i in range(len(beta)) for j in range(len(beta)))
            rss = max(0.0, self.sum_squares - 2.0 * fitted_data_term + quadratic)
            residual_std = sqrt(rss / degrees)
        return prediction, leverage, residual_std


@dataclass(frozen=True)
class CandidatePredictorState:
    candidate_id: str
    quality: RidgeState
    cost: RidgeState


@dataclass(frozen=True)
class CandidateForecast:
    candidate_id: str
    eligible: bool
    predicted_quality: float
    predicted_cost: float
    quality_count: int
    cost_count: int
    quality_status: str
    cost_status: str
    quality_leverage: float
    cost_leverage: float
    quality_residual_std: float | None
    cost_residual_std: float | None
    within_predicted_budget: bool | None
    meets_quality_target: bool


@dataclass(frozen=True)
class RouterDecision:
    query_id: str
    selected_candidate_id: str | None
    reason: str
    exploratory: bool
    quality_threshold_overridden: bool
    quality_requirement: float
    cost_budget: float | None
    currency: str
    state_version_before: int
    forecasts: tuple[CandidateForecast, ...]


@dataclass(frozen=True)
class ExecutionOutcome:
    query_id: str
    candidate_id: str
    observed_quality: float | None
    observed_cost: float | None
    currency: str
    accounting_version: str
    evaluator_version: str
    status: str = "ok"
    diagnostic_metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.query_id or not self.candidate_id:
            raise ValueError("outcome query_id and candidate_id must be non-empty")
        if self.observed_quality is not None:
            quality = _number(self.observed_quality, "observed_quality")
            if not 0.0 <= quality <= 1.0:
                raise ValueError("observed_quality must lie in [0, 1]")
            object.__setattr__(self, "observed_quality", quality)
        if self.observed_cost is not None:
            cost = _number(self.observed_cost, "observed_cost")
            if cost < 0:
                raise ValueError("observed_cost must be non-negative")
            object.__setattr__(self, "observed_cost", cost)
        if self.observed_quality is None and self.observed_cost is None:
            # Valid: failed executions can return no usable feedback.
            pass
        for name in ("currency", "accounting_version", "evaluator_version", "status"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be a non-empty string")
        object.__setattr__(self, "diagnostic_metadata", tuple(self.diagnostic_metadata))


@dataclass(frozen=True)
class UpdateReceipt:
    candidate_id: str
    quality_updated: bool
    cost_updated: bool
    quality_count_before: int
    quality_count_after: int
    cost_count_before: int
    cost_count_after: int
    state_version_before: int
    state_version_after: int


@dataclass(frozen=True)
class RoutingTrace:
    query: QuerySpec
    decision: RouterDecision
    outcome: ExecutionOutcome | None
    update: UpdateReceipt | None
    observed_quality_meets_target: bool | None
    predicted_budget_compliant: bool | None
    actual_budget_compliant: bool | None


@dataclass(frozen=True)
class RoutingRunResult:
    traces: tuple[RoutingTrace, ...]
    currency: str
    evaluator_version: str
    accounting_version: str
    run_id: str
    context_dimension: int
    include_intercept: bool
    quality_regularization: float
    cost_regularization: float
    epsilon: float
    exploration_seed: int
    candidates: tuple[CandidateSpec, ...]
    initial_priors: tuple[CandidatePrior, ...]
    executor_replay_metadata: tuple[tuple[str, str], ...]


class QueryExecutor(Protocol):
    def execute(self, candidate: CandidateSpec, query: QuerySpec) -> ExecutionOutcome: ...


class ContextualQualityCostRouter:
    """Per-candidate contextual ridge router; owns no environment truth."""

    __slots__ = ("config", "candidates", "_states", "_rng", "_version", "_seen")

    def __init__(self, config: ContextualRouterConfig,
                 candidates: Sequence[CandidateSpec], priors: Sequence[CandidatePrior]):
        ordered = tuple(sorted(candidates, key=lambda item: item.candidate_id))
        if not ordered:
            raise ValueError("at least one candidate is required")
        ids = tuple(item.candidate_id for item in ordered)
        if len(set(ids)) != len(ids):
            raise ValueError("candidate IDs must be unique")
        prior_map = {item.candidate_id: item for item in priors}
        if len(prior_map) != len(tuple(priors)) or set(prior_map) != set(ids):
            raise ValueError("exactly one prior is required for each candidate")
        expected = config.feature_dimension
        states = []
        for candidate in ordered:
            prior = prior_map[candidate.candidate_id]
            if len(prior.quality_coefficients) != expected:
                raise ValueError("prior coefficient length must match feature dimension")
            states.append(CandidatePredictorState(
                candidate.candidate_id,
                RidgeState.initialize(prior.quality_coefficients,
                                      config.quality_regularization),
                RidgeState.initialize(prior.cost_coefficients,
                                      config.cost_regularization),
            ))
        self.config = config
        self.candidates = ordered
        self._states = tuple(states)
        self._rng = Random(config.exploration_seed)
        self._version = 0
        self._seen: set[tuple[str, str]] = set()

    @property
    def state_version(self) -> int:
        return self._version

    def _features(self, query: QuerySpec) -> Vector:
        if len(query.context) != self.config.context_dimension:
            raise ValueError("query context dimension does not match router configuration")
        return ((1.0,) + query.context if self.config.include_intercept else query.context)

    def _forecast(self, query: QuerySpec, features: Vector,
                  eligible_ids: set[str]) -> tuple[CandidateForecast, ...]:
        forecasts = []
        for candidate, state in zip(self.candidates, self._states):
            quality_raw, q_leverage, q_resid = state.quality.predict_raw(features)
            cost_raw, c_leverage, c_resid = state.cost.predict_raw(features)
            quality = min(1.0, max(0.0, quality_raw))
            cost = max(0.0, cost_raw)
            eligible = candidate.candidate_id in eligible_ids and candidate.is_eligible_for(query)
            budget_ok = None if query.cost_budget is None else cost <= query.cost_budget
            forecasts.append(CandidateForecast(
                candidate.candidate_id, eligible, quality, cost,
                state.quality.observation_count, state.cost.observation_count,
                "OBSERVED" if state.quality.observation_count else "PRIOR_ONLY",
                "OBSERVED" if state.cost.observation_count else "PRIOR_ONLY",
                q_leverage, c_leverage, q_resid, c_resid, budget_ok,
                quality >= query.quality_requirement,
            ))
        return tuple(forecasts)

    def decide(self, query: QuerySpec,
               eligible_candidate_ids: Sequence[str] | None = None) -> RouterDecision:
        features = self._features(query)
        known_ids = {candidate.candidate_id for candidate in self.candidates}
        eligible_ids = known_ids if eligible_candidate_ids is None else set(eligible_candidate_ids)
        if not eligible_ids <= known_ids:
            raise ValueError("eligible_candidate_ids contains an unknown candidate")
        forecasts = self._forecast(query, features, eligible_ids)
        feasible = [item for item in forecasts if item.eligible]
        if query.cost_budget is not None:
            feasible = [item for item in feasible if item.predicted_cost <= query.cost_budget]
        if not feasible:
            resource_eligible = [item for item in forecasts if item.eligible]
            reason = ("no_predicted_budget_feasible_candidate" if resource_eligible
                      and query.cost_budget is not None
                      else "no_resource_eligible_candidate")
        else:
            reason = ""
        selected: CandidateForecast | None = None
        exploratory = False
        if feasible:
            if self.config.epsilon > 0.0 and self._rng.random() < self.config.epsilon:
                selected = feasible[self._rng.randrange(len(feasible))]
                exploratory = True
                reason = "epsilon_exploration"
            else:
                target = [item for item in feasible if item.meets_quality_target]
                if target:
                    selected = min(target, key=lambda item: (
                        item.predicted_cost, -item.predicted_quality, item.candidate_id
                    ))
                    reason = "minimum_predicted_cost_meeting_quality_target"
                else:
                    selected = min(feasible, key=lambda item: (
                        -item.predicted_quality, item.predicted_cost, item.candidate_id
                    ))
                    reason = "maximum_predicted_quality_fallback"
        return RouterDecision(
            query.query_id,
            None if selected is None else selected.candidate_id,
            reason,
            exploratory,
            bool(selected and exploratory and not selected.meets_quality_target),
            query.quality_requirement,
            query.cost_budget,
            self.config.currency,
            self._version,
            forecasts,
        )

    def observe(self, query: QuerySpec, outcome: ExecutionOutcome) -> UpdateReceipt:
        if outcome.query_id != query.query_id:
            raise ValueError("outcome query_id does not match query")
        if outcome.candidate_id not in {item.candidate_id for item in self.candidates}:
            raise ValueError("outcome candidate is not registered")
        if outcome.currency != self.config.currency:
            raise ValueError("outcome currency does not match router run currency")
        if outcome.accounting_version != self.config.accounting_version:
            raise ValueError("outcome accounting version mismatch")
        if outcome.evaluator_version != self.config.evaluator_version:
            raise ValueError("outcome evaluator version mismatch")
        key = (outcome.query_id, outcome.candidate_id)
        if key in self._seen:
            raise ValueError("duplicate feedback for the same query/candidate execution")
        features = self._features(query)
        index = next(i for i, state in enumerate(self._states)
                     if state.candidate_id == outcome.candidate_id)
        old = self._states[index]
        q_before, c_before = old.quality.observation_count, old.cost.observation_count
        quality = old.quality if outcome.observed_quality is None else old.quality.update(
            features, outcome.observed_quality
        )
        cost = old.cost if outcome.observed_cost is None else old.cost.update(
            features, outcome.observed_cost
        )
        updated = CandidatePredictorState(old.candidate_id, quality, cost)
        states = list(self._states)
        states[index] = updated
        self._states = tuple(states)
        before = self._version
        if outcome.observed_quality is not None or outcome.observed_cost is not None:
            self._version += 1
        self._seen.add(key)
        return UpdateReceipt(
            outcome.candidate_id,
            outcome.observed_quality is not None,
            outcome.observed_cost is not None,
            q_before, quality.observation_count,
            c_before, cost.observation_count,
            before, self._version,
        )


def run_contextual_routing(
    queries: Sequence[QuerySpec],
    router: ContextualQualityCostRouter,
    executor: QueryExecutor,
    *,
    eligibility_by_query: dict[str, Sequence[str]] | None = None,
    run_id: str = "contextual-run",
) -> RoutingRunResult:
    """Run sequential observe→predict→select→execute→update routing."""
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be a non-empty string")
    query_ids = tuple(query.query_id for query in queries)
    if len(set(query_ids)) != len(query_ids):
        raise ValueError("query IDs must be unique within a routing run")
    traces = []
    for query in queries:
        eligible = None if eligibility_by_query is None else eligibility_by_query.get(query.query_id)
        decision = router.decide(query, eligible)
        outcome = update = None
        if decision.selected_candidate_id is not None:
            candidate = next(item for item in router.candidates
                             if item.candidate_id == decision.selected_candidate_id)
            outcome = executor.execute(candidate, query)
            if outcome.candidate_id != decision.selected_candidate_id:
                raise ValueError("executor returned feedback for a non-selected candidate")
            update = router.observe(query, outcome)
        chosen_forecast = next((item for item in decision.forecasts
                                if item.candidate_id == decision.selected_candidate_id), None)
        q_met = (None if outcome is None or outcome.observed_quality is None else
                 outcome.observed_quality >= query.quality_requirement)
        predicted_budget_ok = (None if chosen_forecast is None or query.cost_budget is None else
                               chosen_forecast.predicted_cost <= query.cost_budget)
        actual_budget_ok = (None if outcome is None or outcome.observed_cost is None
                            or query.cost_budget is None else
                            outcome.observed_cost <= query.cost_budget)
        traces.append(RoutingTrace(query, decision, outcome, update, q_met,
                                   predicted_budget_ok, actual_budget_ok))
    config = router.config
    states_by_id = {state.candidate_id: state for state in router._states}
    initial_priors = tuple(CandidatePrior(
        candidate.candidate_id,
        states_by_id[candidate.candidate_id].quality.prior,
        states_by_id[candidate.candidate_id].cost.prior,
    ) for candidate in router.candidates)
    # Executors may expose non-outcome replay metadata (for example synthetic
    # noise seed/radii). It is captured only in run provenance, never passed to
    # a decision or predictor.
    replay_metadata = getattr(executor, "replay_metadata", ())
    replay_metadata = tuple(sorted(tuple(item) for item in replay_metadata))
    return RoutingRunResult(
        tuple(traces), config.currency, config.evaluator_version,
        config.accounting_version, run_id, config.context_dimension,
        config.include_intercept, config.quality_regularization,
        config.cost_regularization, config.epsilon, config.exploration_seed,
        router.candidates, initial_priors, replay_metadata,
    )


def summarize_routing_run(result: RoutingRunResult) -> dict[str, object]:
    """Return separate descriptive counts/means; no combined utility score."""
    traces = result.traces
    selected = [trace for trace in traces if trace.outcome is not None]
    qualities = [trace.outcome.observed_quality for trace in selected
                 if trace.outcome and trace.outcome.observed_quality is not None]
    costs = [trace.outcome.observed_cost for trace in selected
             if trace.outcome and trace.outcome.observed_cost is not None]
    observed_quality_targets = [trace.observed_quality_meets_target for trace in traces
                                if trace.observed_quality_meets_target is not None]
    predicted_budget = [trace.predicted_budget_compliant for trace in traces
                        if trace.predicted_budget_compliant is not None]
    actual_budget = [trace.actual_budget_compliant for trace in traces
                     if trace.actual_budget_compliant is not None]
    by_candidate: dict[str, int] = {}
    for trace in selected:
        assert trace.decision.selected_candidate_id is not None
        by_candidate[trace.decision.selected_candidate_id] = (
            by_candidate.get(trace.decision.selected_candidate_id, 0) + 1
        )
    return {
        "queries": len(traces),
        "executed": len(selected),
        "no_selection": len(traces) - len(selected),
        "mean_observed_quality": None if not qualities else sum(qualities) / len(qualities),
        "mean_observed_cost": None if not costs else sum(costs) / len(costs),
        "quality_target_rate": (None if not observed_quality_targets else
                                 sum(observed_quality_targets) / len(observed_quality_targets)),
        "predicted_budget_compliance_rate": (None if not predicted_budget else
                                             sum(predicted_budget) / len(predicted_budget)),
        "actual_budget_compliance_rate": (None if not actual_budget else
                                           sum(actual_budget) / len(actual_budget)),
        "exploratory_decisions": sum(trace.decision.exploratory for trace in traces),
        "fallback_decisions": sum(trace.decision.reason ==
                                   "maximum_predicted_quality_fallback" for trace in traces),
        "selected_by_candidate": dict(sorted(by_candidate.items())),
        "currency": result.currency,
        "evaluator_version": result.evaluator_version,
        "accounting_version": result.accounting_version,
    }


def serialize_routing_run(result: RoutingRunResult) -> str:
    return json.dumps(asdict(result), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)
