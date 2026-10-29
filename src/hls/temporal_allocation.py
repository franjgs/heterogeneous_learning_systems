"""Deterministic task allocation with temporal arrivals and FCFS service.

Effectiveness is a fixed deterministic contribution, not a measured
competence or stochastic success. Each agent has one FCFS server and an
unbounded queue; service capacity becomes available again at completion.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, fsum, isfinite
from typing import Sequence


@dataclass(frozen=True)
class ArrivalTask:
    arrival_time: float
    task_type: int


@dataclass(frozen=True)
class TemporalTaskDecision:
    task_index: int
    task_type: int
    arrival_time: float
    agent_index: int
    effectiveness: float
    workload_at_decision: float
    service_start: float
    completion_time: float

    @property
    def waiting_time(self) -> float:
        return self.service_start - self.arrival_time

    @property
    def response_time(self) -> float:
        return self.completion_time - self.arrival_time


@dataclass(frozen=True)
class TemporalAllocationResult:
    policy: str
    decisions: tuple[TemporalTaskDecision, ...]
    arrival_horizon: float
    total_effectiveness: float
    mean_effectiveness: float
    mean_waiting_time: float
    p95_waiting_time: float
    mean_response_time: float
    p95_response_time: float
    assigned_count_by_agent: tuple[int, ...]
    effectiveness_by_agent: tuple[float, ...]
    mean_effectiveness_by_agent: tuple[float | None, ...]
    pending_work_at_horizon_by_agent: tuple[float, ...]
    utilization_by_agent: tuple[float, ...]
    makespan: float

    @property
    def pending_work_at_horizon(self) -> float:
        return fsum(self.pending_work_at_horizon_by_agent)


def run_fixed_temporal_policy(
    arrivals: Sequence[ArrivalTask | tuple[float, int]],
    effectiveness: Sequence[Sequence[float]],
    service_times: Sequence[float],
    arrival_horizon: float,
    type_to_agent: Sequence[int],
) -> TemporalAllocationResult:
    """Route each type to its predeclared agent, joining that agent's FCFS queue."""
    return _run("fixed", arrivals, effectiveness, service_times, arrival_horizon, type_to_agent)


def run_max_effectiveness_temporal_policy(
    arrivals: Sequence[ArrivalTask | tuple[float, int]],
    effectiveness: Sequence[Sequence[float]],
    service_times: Sequence[float],
    arrival_horizon: float,
) -> TemporalAllocationResult:
    """Choose the highest-effectiveness agent; ties go to the lowest index."""
    return _run("max_effectiveness", arrivals, effectiveness, service_times, arrival_horizon, None)


def run_effectiveness_load_temporal_policy(
    arrivals: Sequence[ArrivalTask | tuple[float, int]],
    effectiveness: Sequence[Sequence[float]],
    service_times: Sequence[float],
    arrival_horizon: float,
) -> TemporalAllocationResult:
    """Maximize e[i,k] / (W_i + s_k), using only current observable workload."""
    return _run("effectiveness_load_ratio", arrivals, effectiveness, service_times, arrival_horizon, None)


def _run(
    policy: str,
    arrivals: Sequence[ArrivalTask | tuple[float, int]],
    effectiveness: Sequence[Sequence[float]],
    service_times: Sequence[float],
    arrival_horizon: float,
    type_to_agent: Sequence[int] | None,
) -> TemporalAllocationResult:
    tasks, matrix, durations, horizon = _validate(
        arrivals, effectiveness, service_times, arrival_horizon
    )
    n_agents, n_types = len(matrix), len(durations)
    mapping: tuple[int, ...] | None = None
    if type_to_agent is not None:
        mapping = tuple(type_to_agent)
        if len(mapping) != n_types or any(
            not _is_integer(agent) or not 0 <= agent < n_agents for agent in mapping
        ):
            raise ValueError("type_to_agent must contain one valid agent index per task type")

    # Tail completion time is sufficient for a single-server FCFS queue.
    available_at = [0.0] * n_agents
    decisions: list[TemporalTaskDecision] = []
    for index, task in enumerate(tasks):
        time, task_type = task.arrival_time, task.task_type
        if mapping is not None:
            agent = mapping[task_type]
        elif policy == "max_effectiveness":
            agent = max(range(n_agents), key=lambda i: matrix[i][task_type])
        else:
            # All service times are positive. W_i is remaining active service
            # plus queued work, observable from the queue tail at arrival time.
            agent = max(
                range(n_agents),
                key=lambda i: matrix[i][task_type]
                / (max(0.0, available_at[i] - time) + durations[task_type]),
            )

        workload = max(0.0, available_at[agent] - time)
        start = max(time, available_at[agent])
        finish = start + durations[task_type]
        decisions.append(
            TemporalTaskDecision(
                index, task_type, time, agent, matrix[agent][task_type],
                workload, start, finish,
            )
        )
        available_at[agent] = finish

    return _summarize(policy, decisions, horizon, n_agents)


def _validate(
    arrivals: Sequence[ArrivalTask | tuple[float, int]],
    effectiveness: Sequence[Sequence[float]],
    service_times: Sequence[float],
    arrival_horizon: float,
) -> tuple[tuple[ArrivalTask, ...], tuple[tuple[float, ...], ...], tuple[float, ...], float]:
    if not effectiveness:
        raise ValueError("at least one agent is required")
    matrix = tuple(tuple(row) for row in effectiveness)
    if not matrix[0]:
        raise ValueError("at least one task type is required")
    n_types = len(matrix[0])
    if any(len(row) != n_types for row in matrix):
        raise ValueError("effectiveness matrix must be rectangular")
    for row in matrix:
        for value in row:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
                or not 0.0 <= value <= 1.0
            ):
                raise ValueError("effectiveness values must be finite numbers in [0, 1]")

    durations = tuple(service_times)
    if len(durations) != n_types or any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(value)
        or value <= 0
        for value in durations
    ):
        raise ValueError("service_times must contain one finite positive duration per task type")
    if (
        isinstance(arrival_horizon, bool)
        or not isinstance(arrival_horizon, (int, float))
        or not isfinite(arrival_horizon)
        or arrival_horizon <= 0
    ):
        raise ValueError("arrival_horizon must be a finite positive number")
    horizon = float(arrival_horizon)

    normalized: list[ArrivalTask] = []
    for item in arrivals:
        if isinstance(item, ArrivalTask):
            time, task_type = item.arrival_time, item.task_type
        else:
            try:
                time, task_type = item
            except (TypeError, ValueError) as exc:
                raise ValueError("each arrival must be an ArrivalTask or (time, task_type)") from exc
        if (
            isinstance(time, bool)
            or not isinstance(time, (int, float))
            or not isfinite(time)
            or time < 0
            or time >= horizon
        ):
            raise ValueError("arrival times must be finite and in [0, arrival_horizon)")
        if not _is_integer(task_type) or not 0 <= task_type < n_types:
            raise ValueError("arrival contains an invalid task type")
        normalized.append(ArrivalTask(float(time), task_type))
    if not normalized:
        raise ValueError("at least one arrival is required")
    if any(left.arrival_time > right.arrival_time for left, right in zip(normalized, normalized[1:])):
        raise ValueError("arrivals must be ordered by non-decreasing time")
    return tuple(normalized), matrix, tuple(float(value) for value in durations), horizon


def _summarize(
    policy: str,
    decisions: list[TemporalTaskDecision],
    horizon: float,
    n_agents: int,
) -> TemporalAllocationResult:
    total = fsum(task.effectiveness for task in decisions)
    waits = [task.waiting_time for task in decisions]
    responses = [task.response_time for task in decisions]
    assigned_count = tuple(
        sum(task.agent_index == agent for task in decisions) for agent in range(n_agents)
    )
    effectiveness_by_agent = tuple(
        fsum(task.effectiveness for task in decisions if task.agent_index == agent)
        for agent in range(n_agents)
    )
    pending = tuple(
        max(0.0, max((task.completion_time for task in decisions if task.agent_index == agent), default=0.0) - horizon)
        for agent in range(n_agents)
    )
    utilization = tuple(
        fsum(
            max(0.0, min(task.completion_time, horizon) - max(task.service_start, 0.0))
            for task in decisions if task.agent_index == agent
        ) / horizon
        for agent in range(n_agents)
    )
    return TemporalAllocationResult(
        policy=policy,
        decisions=tuple(decisions),
        arrival_horizon=horizon,
        total_effectiveness=total,
        mean_effectiveness=total / len(decisions),
        mean_waiting_time=fsum(waits) / len(waits),
        p95_waiting_time=_nearest_rank(waits, 0.95),
        mean_response_time=fsum(responses) / len(responses),
        p95_response_time=_nearest_rank(responses, 0.95),
        assigned_count_by_agent=assigned_count,
        effectiveness_by_agent=effectiveness_by_agent,
        mean_effectiveness_by_agent=tuple(
            effectiveness_by_agent[i] / assigned_count[i] if assigned_count[i] else None
            for i in range(n_agents)
        ),
        pending_work_at_horizon_by_agent=pending,
        utilization_by_agent=utilization,
        makespan=max(task.completion_time for task in decisions) - min(task.arrival_time for task in decisions),
    )


def _nearest_rank(values: Sequence[float], quantile: float) -> float:
    ordered = sorted(values)
    return ordered[ceil(quantile * len(ordered)) - 1]


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
