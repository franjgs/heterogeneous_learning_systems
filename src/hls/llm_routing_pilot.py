"""Small, reproducible batch-routing methods for the MMLU pilot.

The score predictor is a content-conditioned multidimensional IRT model;
allocation methods consume the same predicted-quality and latency matrices.
This module is an experiment adapter, not a general HLS execution framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, minimize, milp
from scipy.sparse import csr_matrix, hstack, lil_matrix
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold


MODEL_IDS = (
    "HuggingFaceTB/SmolLM2-360M-Instruct",
    "Qwen/Qwen2.5-0.5B-Instruct",
    "HuggingFaceTB/SmolLM2-1.7B-Instruct",
)


class ContextualLogisticQualityPredictor:
    """Regularized binary quality model with text, task, model and task×model.

    Hyperparameter selection is grouped by query so candidate outcomes for one
    question never straddle training and validation folds.
    """

    def __init__(self, c_grid: Sequence[float] = (0.01, 0.1, 1.0, 10.0),
                 n_features: int = 4096, seed: int = 20261023):
        if not c_grid or any(float(c) <= 0 for c in c_grid):
            raise ValueError("c_grid must contain positive regularization values")
        self.c_grid = tuple(float(c) for c in c_grid)
        self.vectorizer = HashingVectorizer(
            n_features=n_features, alternate_sign=False, norm="l2",
            ngram_range=(1, 2), token_pattern=r"(?u)\b\w+\b",
        )
        self.seed = int(seed)
        self.model_ids: tuple[str, ...] | None = None
        self.task_types: tuple[str, ...] | None = None
        self.classifier: LogisticRegression | None = None
        self.cv_results: list[dict[str, float]] = []

    def _features(self, queries: Sequence[str], task_types: Sequence[str],
                  model_indices: np.ndarray) -> csr_matrix:
        if self.model_ids is None or self.task_types is None:
            raise RuntimeError("predictor categories are not initialized")
        if len(queries) != len(task_types) or len(queries) != len(model_indices):
            raise ValueError("query, task and model rows must have equal length")
        text = self.vectorizer.transform(queries)
        model_col = np.asarray(model_indices, dtype=int)
        task_lookup = {task: i for i, task in enumerate(self.task_types)}
        task_col = np.asarray([task_lookup.get(str(task), -1) for task in task_types], dtype=int)
        n, m, k = len(queries), len(self.model_ids), len(self.task_types)
        model_onehot = csr_matrix((np.ones(n), (np.arange(n), model_col)), shape=(n, m))
        known = task_col >= 0
        task_onehot = csr_matrix((np.ones(int(known.sum())),
                                  (np.flatnonzero(known), task_col[known])), shape=(n, k))
        interaction_valid = known
        interaction_rows = np.flatnonzero(interaction_valid)
        interaction_cols = model_col[interaction_valid] * k + task_col[interaction_valid]
        interaction = csr_matrix((np.ones(len(interaction_rows)),
                                  (interaction_rows, interaction_cols)), shape=(n, m * k))
        return hstack((text, model_onehot, task_onehot, interaction), format="csr")

    def fit(self, queries: Sequence[str], task_types: Sequence[str],
            model_ids: Sequence[str], outcomes: np.ndarray,
            query_groups: Sequence[str]) -> "ContextualLogisticQualityPredictor":
        model_ids = tuple(model_ids)
        if len(set(model_ids)) != len(model_ids):
            raise ValueError("model_ids must be unique")
        y_matrix = np.asarray(outcomes, dtype=int)
        if y_matrix.shape != (len(queries), len(model_ids)) or not np.isin(y_matrix, (0, 1)).all():
            raise ValueError("outcomes must be a binary query-by-model matrix")
        if len(task_types) != len(queries) or len(query_groups) != len(queries):
            raise ValueError("task types and query groups must match the query count")
        self.model_ids = model_ids
        self.task_types = tuple(sorted(set(map(str, task_types))))
        n, m = y_matrix.shape
        row_queries = [queries[i] for i in range(n) for _ in range(m)]
        row_tasks = [str(task_types[i]) for i in range(n) for _ in range(m)]
        row_models = np.tile(np.arange(m), n)
        y = y_matrix.reshape(-1)
        groups = np.repeat(np.asarray(query_groups), m)
        x = self._features(row_queries, row_tasks, row_models)
        splitter = GroupKFold(n_splits=min(5, len(set(query_groups))))
        folds = list(splitter.split(np.zeros(len(y)), y, groups))
        self.cv_results = []
        for c_value in self.c_grid:
            losses = []
            for train_idx, valid_idx in folds:
                clf = LogisticRegression(
                    C=c_value, penalty="l2", solver="liblinear", max_iter=2000,
                    random_state=self.seed,
                )
                clf.fit(x[train_idx], y[train_idx])
                p = np.clip(clf.predict_proba(x[valid_idx])[:, 1], 1e-9, 1 - 1e-9)
                losses.append(float(np.mean((p - y[valid_idx]) ** 2)))
            self.cv_results.append({"C": c_value, "mean_grouped_cv_brier": float(np.mean(losses))})
        best = min(self.cv_results, key=lambda row: (row["mean_grouped_cv_brier"], row["C"]))
        self.selected_c = float(best["C"])
        self.classifier = LogisticRegression(
            C=self.selected_c, penalty="l2", solver="liblinear", max_iter=2000,
            random_state=self.seed,
        ).fit(x, y)
        self.fit_info = {
            "selected_C": self.selected_c,
            "cv_mean_brier": float(best["mean_grouped_cv_brier"]),
            "n_grouped_folds": len(folds),
            "n_training_queries": n,
            "n_training_query_model_pairs": int(len(y)),
            "cv_results": self.cv_results,
        }
        return self

    def predict(self, queries: Sequence[str], task_types: Sequence[str]) -> np.ndarray:
        if self.classifier is None or self.model_ids is None:
            raise RuntimeError("predictor is not fitted")
        n, m = len(queries), len(self.model_ids)
        row_queries = [queries[i] for i in range(n) for _ in range(m)]
        row_tasks = [str(task_types[i]) for i in range(n) for _ in range(m)]
        row_models = np.tile(np.arange(m), n)
        x = self._features(row_queries, row_tasks, row_models)
        return self.classifier.predict_proba(x)[:, 1].reshape(n, m)


class MIRTQualityPredictor:
    """Content-conditioned multidimensional 2PL item-response predictor.

    A fixed text map produces item discrimination ``a_i`` and difficulty
    ``b_i``; each candidate has a fitted latent ability vector ``theta_m``.
    The response probability is sigmoid(theta_m' a_i - b_i). This preserves
    the published M-IRT response form while replacing its pretrained BERT
    embeddings with a fixed hashing map for this small, license-safe pilot.
    """

    def __init__(self, n_features: int = 256, l2: float = 1.0, seed: int = 20261023):
        self.vectorizer = HashingVectorizer(
            n_features=n_features, alternate_sign=False, norm="l2",
            ngram_range=(1, 2), token_pattern=r"(?u)\b\w+\b",
        )
        self.l2 = float(l2)
        self.seed = int(seed)
        self.theta: np.ndarray | None = None
        self.item_a: np.ndarray | None = None
        self.item_b: np.ndarray | None = None
        self._raw_a: np.ndarray | None = None
        self._raw_b: np.ndarray | None = None
        self.model_ids: tuple[str, ...] | None = None

    @staticmethod
    def _sigmoid(values: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(values, -35, 35)))

    def fit(self, queries: Sequence[str], model_ids: Sequence[str], outcomes: np.ndarray) -> "MIRTQualityPredictor":
        x = self.vectorizer.transform(queries).toarray().astype(float)
        model_ids = tuple(model_ids)
        y = np.asarray(outcomes, dtype=float)
        if y.shape != (len(queries), len(model_ids)) or not np.isin(y, (0.0, 1.0)).all():
            raise ValueError("outcomes must be a binary query by model matrix")
        # Centering/scale keeps the regularized latent-ability fit stable.
        f = x.shape[1]
        m = len(model_ids)
        d = min(8, max(2, f // 32))
        rng = np.random.default_rng(self.seed)
        initial = np.concatenate((
            rng.normal(0.0, 0.02, m * d),
            rng.normal(0.0, 0.02, d * f),
            np.zeros(f),
        ))

        def objective(params: np.ndarray) -> tuple[float, np.ndarray]:
            offset = m * d
            theta = params[:offset].reshape(m, d)
            raw_a = params[offset:offset + d * f].reshape(d, f)
            raw_b = params[offset + d * f:]
            item_a = np.logaddexp(0.0, x @ raw_a.T)
            item_b = x @ raw_b
            logits = item_a @ theta.T - item_b[:, None]
            probs = self._sigmoid(logits)
            residual = probs - y
            loss = float(np.sum(np.logaddexp(0.0, logits) - y * logits))
            loss += 0.5 * self.l2 * float(np.square(params).sum())
            grad_theta = residual.T @ item_a + self.l2 * theta
            grad_item_a = residual @ theta
            grad_raw_a = (grad_item_a * self._sigmoid(x @ raw_a.T)).T @ x + self.l2 * raw_a
            grad_item_b = -residual.sum(axis=1)
            grad_raw_b = x.T @ grad_item_b + self.l2 * raw_b
            grad = np.concatenate((grad_theta.ravel(), grad_raw_a.ravel(), grad_raw_b))
            return loss, grad

        fitted = minimize(objective, initial, jac=True, method="L-BFGS-B",
                          options={"maxiter": 5000, "ftol": 1e-9})
        if not fitted.success or not np.isfinite(fitted.fun):
            raise RuntimeError(f"MIRT fit did not converge: {fitted.message}")
        offset = m * d
        self.theta = fitted.x[:offset].reshape(m, d)
        raw_a = fitted.x[offset:offset + d * f].reshape(d, f)
        raw_b = fitted.x[offset + d * f:]
        self.item_a = np.logaddexp(0.0, x @ raw_a.T)
        self.item_b = x @ raw_b
        self._raw_a = raw_a
        self._raw_b = raw_b
        self.model_ids = model_ids
        self.fit_info = {"success": bool(fitted.success), "message": str(fitted.message),
                         "iterations": int(fitted.nit), "objective": float(fitted.fun)}
        return self

    def predict(self, queries: Sequence[str]) -> np.ndarray:
        if self.theta is None or self._raw_a is None or self._raw_b is None:
            raise RuntimeError("predictor is not fitted")
        x = self.vectorizer.transform(queries).toarray().astype(float)
        item_a = np.logaddexp(0.0, x @ self._raw_a.T)
        item_b = x @ self._raw_b
        return self._sigmoid(item_a @ self.theta.T - item_b[:, None])


def predict_latency(input_tokens: np.ndarray, latency_seconds: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fit nonnegative per-model affine latency predictors from train only."""
    tokens = np.asarray(input_tokens, dtype=float)
    lat = np.asarray(latency_seconds, dtype=float)
    if tokens.ndim != 2 or lat.shape != tokens.shape or np.any(lat <= 0):
        raise ValueError("token and latency matrices must be positive and have equal shape")
    coefficients = np.zeros((2, tokens.shape[1]), dtype=float)
    for m in range(tokens.shape[1]):
        slope, intercept = np.polyfit(tokens[:, m], lat[:, m], 1)
        coefficients[:, m] = (max(0.0, slope), max(0.0, intercept))
    return coefficients[0], coefficients[1]


def apply_latency(input_tokens: np.ndarray, coefficients: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    slope, intercept = coefficients
    return np.maximum(np.asarray(input_tokens, dtype=float) * slope + intercept, 1e-6)


def budget_between_extremes(costs: np.ndarray, fraction: float) -> float:
    costs = np.asarray(costs, dtype=float)
    if costs.ndim != 2 or not 0 <= fraction <= 1:
        raise ValueError("costs must be query by model and fraction in [0,1]")
    return float(costs.min(axis=1).sum() + fraction * (costs.max(axis=1) - costs.min(axis=1)).sum())


def solve_batch_ilp(quality: np.ndarray, costs: np.ndarray, budget: float) -> np.ndarray:
    """Exact single-model-per-query 0-1 ILP, with a hard shared budget."""
    q, c = np.asarray(quality, dtype=float), np.asarray(costs, dtype=float)
    if q.ndim != 2 or q.shape != c.shape or np.any(c < 0) or budget < 0:
        raise ValueError("quality/cost must be equal query-by-model matrices")
    n, m = q.shape
    constraints = lil_matrix((n + 1, n * m), dtype=float)
    for i in range(n):
        constraints[i, i * m:(i + 1) * m] = 1.0
    constraints[n, :] = c.reshape(1, -1)
    lower = np.r_[np.ones(n), -np.inf]
    upper = np.r_[np.ones(n), budget]
    result = milp(
        c=-q.ravel(), integrality=np.ones(n * m), bounds=Bounds(0, 1),
        constraints=LinearConstraint(constraints.tocsr(), lower, upper),
        options={"presolve": True},
    )
    if not result.success or result.x is None:
        raise RuntimeError(f"batch ILP failed: {result.message}")
    return np.argmax(result.x.reshape(n, m), axis=1)


def greedy_feasible(quality: np.ndarray, costs: np.ndarray, budget: float) -> np.ndarray:
    """Start with cheapest options, then buy best feasible quality upgrades."""
    q, c = np.asarray(quality, dtype=float), np.asarray(costs, dtype=float)
    if q.shape != c.shape or q.ndim != 2:
        raise ValueError("quality/cost must be equal query-by-model matrices")
    choice = np.argmin(c, axis=1)
    spent = float(c[np.arange(len(choice)), choice].sum())
    if spent > budget + 1e-9:
        raise ValueError("budget is below the cheapest feasible assignment")
    while True:
        candidates = []
        for i in range(len(choice)):
            old = choice[i]
            for model in range(q.shape[1]):
                delta_cost = c[i, model] - c[i, old]
                delta_q = q[i, model] - q[i, old]
                if delta_q > 1e-12 and delta_cost <= budget - spent + 1e-12:
                    ratio = delta_q / max(delta_cost, 1e-12)
                    candidates.append((-ratio, -delta_q, i, model, delta_cost))
        if not candidates:
            break
        _, _, i, model, delta_cost = min(candidates)
        choice[i] = model
        spent += float(delta_cost)
    return choice


def independent_with_repair(
    quality: np.ndarray, costs: np.ndarray, budget: float, price: float,
) -> np.ndarray:
    """Per-query price routing followed by deterministic cheapest-loss repair."""
    q, c = np.asarray(quality, dtype=float), np.asarray(costs, dtype=float)
    choice = np.argmax(q - price * c, axis=1)
    spent = float(c[np.arange(len(choice)), choice].sum())
    while spent > budget + 1e-9:
        downgrades = []
        for i, old in enumerate(choice):
            for model in range(q.shape[1]):
                saved = c[i, old] - c[i, model]
                loss = q[i, old] - q[i, model]
                if saved > 1e-12:
                    downgrades.append((loss / saved, loss, i, model, saved))
        if not downgrades:
            raise ValueError("cannot repair assignment to budget")
        _, _, i, model, saved = min(downgrades)
        choice[i] = model
        spent -= float(saved)
    return choice


def fixed_model(quality: np.ndarray, costs: np.ndarray, model_index: int) -> np.ndarray:
    if np.asarray(quality).shape != np.asarray(costs).shape:
        raise ValueError("quality/cost shapes differ")
    return np.full(np.asarray(quality).shape[0], int(model_index), dtype=int)


def retrospective_oracle(observed: np.ndarray, costs: np.ndarray, budget: float) -> np.ndarray:
    return solve_batch_ilp(np.asarray(observed, dtype=float), costs, budget)


@dataclass(frozen=True)
class PolicyMetrics:
    accuracy: float
    cost_estimated_seconds: float
    latency_observed_seconds: float
    budget_seconds: float
    budget_compliant_estimated: bool
    budget_compliant_observed: bool


def score_assignment(choice: np.ndarray, quality_observed: np.ndarray,
                     costs_estimated: np.ndarray, latency_observed: np.ndarray,
                     budget: float) -> PolicyMetrics:
    choice = np.asarray(choice, dtype=int)
    rows = np.arange(len(choice))
    estimated = float(costs_estimated[rows, choice].sum())
    observed = float(latency_observed[rows, choice].sum())
    accuracy = float(np.asarray(quality_observed)[rows, choice].mean())
    return PolicyMetrics(accuracy, estimated, observed, float(budget),
                         estimated <= budget + 1e-8, observed <= budget + 1e-8)
