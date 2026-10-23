"""DCS-LA style contextual selection for pre-scored model capacities.

The estimator selects one model by its empirical accuracy on the k nearest
training queries. It neither combines model outputs nor uses query outcomes
at inference time. Feature construction is fitted on training text only.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter_ns
from typing import Sequence

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class DCSLAConfig:
    k: int
    ngram_range: tuple[int, int]
    task_weight: float

    def __post_init__(self) -> None:
        if self.k < 1:
            raise ValueError("k must be positive")
        if self.ngram_range not in {(1, 1), (1, 2)}:
            raise ValueError("unsupported ngram range")
        if not np.isfinite(self.task_weight) or self.task_weight < 0:
            raise ValueError("task weight must be finite and non-negative")


class DCSLASelector:
    """Local-accuracy model selector with TF-IDF and an observed task feature.

    The vectorizer vocabulary/IDF and task vocabulary are learned from training
    rows. Missing training task metadata is represented by an all-zero task
    vector, rather than inferred from a label or answer.
    """

    def __init__(self, config: DCSLAConfig, model_ids: Sequence[str]):
        self.config = config
        self.model_ids = tuple(map(str, model_ids))
        if not self.model_ids or len(set(self.model_ids)) != len(self.model_ids):
            raise ValueError("model_ids must be non-empty and unique")
        self.vectorizer: TfidfVectorizer | None = None
        self.task_to_index: dict[str, int] = {}
        self.training_matrix = None
        self.train_outcomes: np.ndarray | None = None
        self.train_ids: tuple[str, ...] = ()

    def fit(self, questions: Sequence[str], tasks: Sequence[str | None],
            outcomes: np.ndarray, query_ids: Sequence[str]) -> "DCSLASelector":
        text = tuple(self._clean_text(q) for q in questions)
        task_values = tuple(self._clean_task(task) for task in tasks)
        y = np.asarray(outcomes, dtype=np.uint8)
        if not text or len(text) != len(task_values) or len(text) != len(query_ids):
            raise ValueError("training contexts and IDs must have matching non-zero lengths")
        if y.shape != (len(text), len(self.model_ids)) or not np.isin(y, (0, 1)).all():
            raise ValueError("outcomes must be a binary row-by-model matrix")
        if len(set(query_ids)) != len(query_ids):
            raise ValueError("training query IDs must be unique")
        self.vectorizer = TfidfVectorizer(ngram_range=self.config.ngram_range,
                                          lowercase=True, strip_accents="unicode",
                                          norm="l2", dtype=np.float64)
        text_matrix = self.vectorizer.fit_transform(text)
        observed_tasks = sorted({task for task in task_values if task is not None})
        self.task_to_index = {task: i for i, task in enumerate(observed_tasks)}
        self.training_matrix = self._combine(text_matrix, task_values)
        self.train_outcomes = y.copy()
        self.train_ids = tuple(map(str, query_ids))
        return self

    @staticmethod
    def _clean_text(question: str) -> str:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("query question text must be non-empty")
        return " ".join(question.split())

    @staticmethod
    def _clean_task(task: str | None) -> str | None:
        if task is None or not str(task).strip():
            return None
        return str(task).strip()

    def _combine(self, text_matrix, tasks: Sequence[str | None]):
        if not self.task_to_index or self.config.task_weight == 0:
            return normalize(text_matrix, norm="l2", copy=True)
        rows, cols, values = [], [], []
        for row_index, task in enumerate(tasks):
            task_index = self.task_to_index.get(task) if task is not None else None
            if task_index is not None:
                rows.append(row_index)
                cols.append(task_index)
                values.append(self.config.task_weight)
        categorical = csr_matrix((values, (rows, cols)),
                                 shape=(len(tasks), len(self.task_to_index)), dtype=np.float64)
        combined = hstack((text_matrix, categorical), format="csr")
        return normalize(combined, norm="l2", copy=False)

    def transform(self, questions: Sequence[str], tasks: Sequence[str | None]):
        if self.vectorizer is None or self.training_matrix is None:
            raise RuntimeError("selector must be fitted before transform")
        if len(questions) != len(tasks) or not questions:
            raise ValueError("query contexts must have matching non-zero lengths")
        text = tuple(self._clean_text(q) for q in questions)
        task_values = tuple(self._clean_task(task) for task in tasks)
        text_matrix = self.vectorizer.transform(text)
        return self._combine(text_matrix, task_values)

    def predict_one(self, question: str, task: str | None) -> dict[str, object]:
        """Return selected model and auditable local-competence details."""
        if self.train_outcomes is None or self.training_matrix is None:
            raise RuntimeError("selector must be fitted before prediction")
        started = perf_counter_ns()
        clean_question = self._clean_text(question)
        cleaned_task = self._clean_task(task)
        extracted_ns = perf_counter_ns() - started

        started = perf_counter_ns()
        text_row = self.vectorizer.transform([clean_question])
        text_ns = perf_counter_ns() - started

        started = perf_counter_ns()
        query_row = self._combine(text_row, [cleaned_task])
        feature_combination_ns = perf_counter_ns() - started

        started = perf_counter_ns()
        similarities = cosine_similarity(query_row, self.training_matrix, dense_output=True)[0]
        # Stable tie-breaking: larger similarity first, then training query ID.
        order = sorted(range(len(similarities)), key=lambda i: (-float(similarities[i]), self.train_ids[i]))
        neighbors = np.asarray(order[:min(self.config.k, len(order))], dtype=int)
        search_ns = perf_counter_ns() - started

        started = perf_counter_ns()
        local_accuracy = self.train_outcomes[neighbors].mean(axis=0)
        # Equal local accuracy resolves by the predeclared model_ids order.
        selected_index = int(np.argmax(local_accuracy))
        decision_ns = perf_counter_ns() - started
        return {
            "selected_model": self.model_ids[selected_index],
            "selected_model_index": selected_index,
            "local_accuracy": local_accuracy.tolist(),
            "neighbor_query_ids": [self.train_ids[i] for i in neighbors],
            "neighbor_similarity": [float(similarities[i]) for i in neighbors],
            "timing_ns": {
                "context_extraction": int(extracted_ns),
                "tfidf_transform": int(text_ns),
                "feature_combination_and_normalization": int(feature_combination_ns),
                "neighbor_search": int(search_ns),
                "local_competence_and_selection": int(decision_ns),
                "total_selection": int(extracted_ns + text_ns + feature_combination_ns + search_ns + decision_ns),
            },
        }

    def predict(self, questions: Sequence[str], tasks: Sequence[str | None]) -> list[str]:
        return [str(self.predict_one(q, t)["selected_model"]) for q, t in zip(questions, tasks)]


def choose_dcs_config(validation_scores: Sequence[tuple[DCSLAConfig, float]]) -> DCSLAConfig:
    """Select max validation accuracy; ties prefer smoother/lower-complexity config.

    Tie order is larger k, unigrams, then lower task feature weight.
    """
    if not validation_scores:
        raise ValueError("validation scores cannot be empty")
    return max(validation_scores, key=lambda item: (
        float(item[1]), item[0].k, -item[0].ngram_range[1], -item[0].task_weight
    ))[0]
