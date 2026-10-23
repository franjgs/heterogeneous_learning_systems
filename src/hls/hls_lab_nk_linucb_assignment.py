"""Minimal pair-score adapter between existing LinUCB and N×K matching."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .linucb import LinUCBDisjoint


class PairwiseLinUCBAdapterNK:
    """Maintain one existing disjoint LinUCB model for each agent-task pair.

    The adapter only turns an N×K collection of feature vectors into an N×K
    UCB-score matrix and routes feedback to selected pairs. Matching remains
    the responsibility of ``HungarianAssignmentOptimizerNK`` or a comparator.
    Each pair receives one observation only when that pair was assigned.
    Multiple selected pairs are updated after the simultaneous assignment
    (a batched/multiple-play composition, not single-play LinUCB's original
    one-action-per-round protocol).
    """

    def __init__(self, n_agents: int, n_tasks: int, n_features: int, alpha: float) -> None:
        if min(n_agents, n_tasks) < 1:
            raise ValueError("n_agents and n_tasks must be positive")
        self.n_agents = n_agents
        self.n_tasks = n_tasks
        self.n_features = n_features
        self._models = tuple(
            tuple(LinUCBDisjoint(1, n_features, alpha) for _ in range(n_tasks))
            for _ in range(n_agents)
        )
        self._counts = [[0] * n_tasks for _ in range(n_agents)]

    def score_matrix(self, contexts: Sequence[Sequence[Sequence[float]]]) -> tuple[tuple[float, ...], ...]:
        matrix = self._validate_context_matrix(contexts)
        return tuple(
            tuple(self._models[i][j].scores((matrix[i][j],))[0] for j in range(self.n_tasks))
            for i in range(self.n_agents)
        )

    def update_selected(
        self,
        selected_pairs: Sequence[tuple[int, int]],
        contexts: Sequence[Sequence[Sequence[float]]],
        observed_rewards: Mapping[tuple[int, int], float],
    ) -> None:
        """Update exactly the selected pair models from observed scalar rewards."""
        matrix = self._validate_context_matrix(contexts)
        selected = tuple((int(i), int(j)) for i, j in selected_pairs)
        if len(set(selected)) != len(selected):
            raise ValueError("selected_pairs cannot contain duplicates")
        if set(observed_rewards) != set(selected):
            raise ValueError("feedback keys must exactly match selected pairs")
        for i, j in selected:
            if not (0 <= i < self.n_agents and 0 <= j < self.n_tasks):
                raise ValueError("selected pair is outside the N×K index range")
            model = self._models[i][j]
            if model.select((matrix[i][j],)) != 0:
                raise AssertionError("single-arm pair model returned a nonzero arm")
            model.observe_reward(observed_rewards[(i, j)])
            self._counts[i][j] += 1

    @property
    def coefficient_estimates(self) -> tuple[tuple[tuple[float, ...], ...], ...]:
        return tuple(
            tuple(self._models[i][j].coefficient_estimates[0] for j in range(self.n_tasks))
            for i in range(self.n_agents)
        )

    @property
    def observation_counts(self) -> tuple[tuple[int, ...], ...]:
        return tuple(tuple(row) for row in self._counts)

    @property
    def design_matrices(self) -> tuple[tuple[tuple[tuple[float, ...], ...], ...], ...]:
        return tuple(
            tuple(self._models[i][j].design_matrices[0] for j in range(self.n_tasks))
            for i in range(self.n_agents)
        )

    def _validate_context_matrix(self, contexts):
        try:
            matrix = tuple(
                tuple(tuple(float(value) for value in context) for context in row)
                for row in contexts
            )
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("contexts must be an N×K×d numeric array") from exc
        if len(matrix) != self.n_agents or any(len(row) != self.n_tasks for row in matrix):
            raise ValueError("context matrix must match adapter N×K dimensions")
        if any(len(context) != self.n_features for row in matrix for context in row):
            raise ValueError("each pair context must have n_features entries")
        return matrix
