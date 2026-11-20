"""Deterministic task allocation with temporal arrivals and FCFS service.

Effectiveness is a fixed deterministic contribution, not a measured
competence or stochastic success. Each agent has one FCFS server and an
unbounded queue; service capacity becomes available again at completion.
"""
from __future__ import annotations

from collections import Counter
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
    completed_effectiveness_total_at_horizon: float
    j_h: float
    mean_waiting_time: float
    p95_waiting_time: float
    mean_response_time: float
    p95_response_time: float
    assigned_count_by_agent: tuple[int, ...]
    effectiveness_by_agent: tuple[float, ...]
    mean_effectiveness_by_agent: tuple[float | None, ...]
    pending_task_count_by_agent: tuple[int, ...]
    pending_work_at_horizon_by_agent: tuple[float, ...]
    utilization_by_agent: tuple[float, ...]
    makespan: float

    @property
    def pending_work_at_horizon(self) -> float:
        return fsum(self.pending_work_at_horizon_by_agent)

    @property
    def pending_task_count(self) -> int:
        return sum(self.pending_task_count_by_agent)


@dataclass(frozen=True)
class AdaptiveThresholds:
    """Congestion/imbalance thresholds for the rule-based S4 controller."""

    congestion_balanced_enter: float = 0.25
    congestion_load_enter: float = 1.0
    congestion_load_exit: float = 0.75
    congestion_specialization_exit: float = 0.15
    imbalance_balanced_enter: float = 0.35
    imbalance_specialization_exit: float = 0.25

    def validate(self) -> None:
        values = (
            self.congestion_balanced_enter,
            self.congestion_load_enter,
            self.congestion_load_exit,
            self.congestion_specialization_exit,
            self.imbalance_balanced_enter,
            self.imbalance_specialization_exit,
        )
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x) for x in values):
            raise ValueError("adaptive thresholds must be finite real numbers")
        if not (
            0 <= self.congestion_specialization_exit
            <= self.congestion_balanced_enter
            < self.congestion_load_enter
            and self.congestion_balanced_enter
            <= self.congestion_load_exit
            <= self.congestion_load_enter
        ):
            raise ValueError("congestion thresholds must preserve ordered entry/exit bands")
        if not (
            0 <= self.imbalance_specialization_exit
            <= self.imbalance_balanced_enter
            <= 1
        ):
            raise ValueError("imbalance thresholds must lie in [0,1] with an exit margin")


@dataclass(frozen=True)
class AdaptivePolicyDiagnostics:
    state_decision_counts: tuple[tuple[str, int], ...]
    strategy_decision_counts: tuple[tuple[str, int], ...]
    state_counts_by_time_quartile: tuple[tuple[str, tuple[int, int, int, int]], ...]
    transition_counts: tuple[tuple[str, int], ...]
    transition_congestion_mean: float | None
    transition_congestion_min: float | None
    transition_congestion_max: float | None
    transition_imbalance_mean: float | None
    transition_imbalance_min: float | None
    transition_imbalance_max: float | None

    @property
    def transition_count(self) -> int:
        return sum(count for _, count in self.transition_counts)


@dataclass(frozen=True)
class AdaptiveTemporalPolicyResult:
    allocation: TemporalAllocationResult
    diagnostics: AdaptivePolicyDiagnostics


class _AdaptiveDiagnosticsAccumulator:
    """Keep aggregates only; never retain an alert/task-level state trace."""

    _states = ("SPECIALIZATION", "BALANCED", "LOAD_DISTRIBUTION")

    def __init__(self) -> None:
        self.state_counts: Counter[str] = Counter()
        self.quartile_counts: dict[str, list[int]] = {
            state: [0, 0, 0, 0] for state in self._states
        }
        self.transitions: Counter[str] = Counter()
        self.transition_count = 0
        self.congestion_sum = 0.0
        self.congestion_min: float | None = None
        self.congestion_max: float | None = None
        self.imbalance_sum = 0.0
        self.imbalance_min: float | None = None
        self.imbalance_max: float | None = None

    def record(
        self,
        arrival_time: float,
        horizon: float,
        old_state: str,
        new_state: str,
        congestion: float,
        imbalance: float,
    ) -> None:
        self.state_counts[new_state] += 1
        quartile = min(3, int(4 * arrival_time / horizon))
        self.quartile_counts[new_state][quartile] += 1
        if old_state != new_state:
            self.transitions[f"{old_state}->{new_state}"] += 1
            self.transition_count += 1
            self.congestion_sum += congestion
            self.congestion_min = congestion if self.congestion_min is None else min(self.congestion_min, congestion)
            self.congestion_max = congestion if self.congestion_max is None else max(self.congestion_max, congestion)
            self.imbalance_sum += imbalance
            self.imbalance_min = imbalance if self.imbalance_min is None else min(self.imbalance_min, imbalance)
            self.imbalance_max = imbalance if self.imbalance_max is None else max(self.imbalance_max, imbalance)

    def snapshot(self) -> AdaptivePolicyDiagnostics:
        c_mean = self.congestion_sum / self.transition_count if self.transition_count else None
        i_mean = self.imbalance_sum / self.transition_count if self.transition_count else None
        state_counts = tuple((state, self.state_counts[state]) for state in self._states)
        strategy_for_state = {
            "SPECIALIZATION": "S1",
            "BALANCED": "S2",
            "LOAD_DISTRIBUTION": "S0",
        }
        strategy_counts = tuple(
            (strategy, self.state_counts[state])
            for state, strategy in strategy_for_state.items()
        )
        return AdaptivePolicyDiagnostics(
            state_counts,
            strategy_counts,
            tuple((state, tuple(self.quartile_counts[state])) for state in self._states),
            tuple(sorted(self.transitions.items())),
            c_mean, self.congestion_min, self.congestion_max,
            i_mean, self.imbalance_min, self.imbalance_max,
        )


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


def run_lowest_workload_temporal_policy(
    arrivals: Sequence[ArrivalTask | tuple[float, int]],
    effectiveness: Sequence[Sequence[float]],
    service_times: Sequence[float],
    arrival_horizon: float,
) -> TemporalAllocationResult:
    """Choose the agent minimizing observable pending work W_i(t); ties use index.

    Here W_i(t)=max(0, queue_tail_i-t), including residual service and all
    queued work. Effectiveness is deliberately ignored.
    """
    return _run("lowest_workload", arrivals, effectiveness, service_times, arrival_horizon, None)


def run_specialist_backup_temporal_policy(
    arrivals: Sequence[ArrivalTask | tuple[float, int]],
    effectiveness: Sequence[Sequence[float]],
    service_times: Sequence[float],
    arrival_horizon: float,
    workload_threshold_multiplier: float = 1.0,
    minimum_backup_effectiveness: float = 0.5,
) -> TemporalAllocationResult:
    """Use the top-effectiveness specialist, with an idle qualified backup.

    The specialist is the maximum-e[i,k] agent (index breaks ties). If its
    workload exceeds ``threshold_multiplier * s_k``, route instead to the
    most effective *other idle* agent with e[i,k] at least the declared
    floor. Ties go to index. If no backup qualifies, use the specialist.
    This is a deterministic heuristic; it has no rejection or queue limit.
    """
    if (
        isinstance(workload_threshold_multiplier, bool)
        or not isinstance(workload_threshold_multiplier, (int, float))
        or not isfinite(workload_threshold_multiplier)
        or workload_threshold_multiplier < 0
    ):
        raise ValueError("workload threshold multiplier must be finite and nonnegative")
    if (
        isinstance(minimum_backup_effectiveness, bool)
        or not isinstance(minimum_backup_effectiveness, (int, float))
        or not isfinite(minimum_backup_effectiveness)
        or not 0 <= minimum_backup_effectiveness <= 1
    ):
        raise ValueError("minimum backup effectiveness must be finite and in [0, 1]")
    return _run(
        "specialist_backup", arrivals, effectiveness, service_times,
        arrival_horizon, None, workload_threshold_multiplier,
        minimum_backup_effectiveness,
    )


def run_adaptive_temporal_policy(
    arrivals: Sequence[ArrivalTask | tuple[float, int]],
    effectiveness: Sequence[Sequence[float]],
    service_times: Sequence[float],
    arrival_horizon: float,
    thresholds: AdaptiveThresholds = AdaptiveThresholds(),
) -> AdaptiveTemporalPolicyResult:
    """Run online S4, switching among unchanged S1/S2/S0 decision rules."""
    thresholds.validate()
    diagnostics = _AdaptiveDiagnosticsAccumulator()
    allocation = _run(
        "adaptive_state_controller",
        arrivals,
        effectiveness,
        service_times,
        arrival_horizon,
        None,
        adaptive_thresholds=thresholds,
        adaptive_diagnostics=diagnostics,
    )
    return AdaptiveTemporalPolicyResult(allocation, diagnostics.snapshot())


def _run(
    policy: str,
    arrivals: Sequence[ArrivalTask | tuple[float, int]],
    effectiveness: Sequence[Sequence[float]],
    service_times: Sequence[float],
    arrival_horizon: float,
    type_to_agent: Sequence[int] | None,
    workload_threshold_multiplier: float = 1.0,
    minimum_backup_effectiveness: float = 0.5,
    adaptive_thresholds: AdaptiveThresholds | None = None,
    adaptive_diagnostics: _AdaptiveDiagnosticsAccumulator | None = None,
) -> TemporalAllocationResult:
    tasks, matrix, durations, horizon = _validate(
        arrivals, effectiveness, service_times, arrival_horizon
    )
    n_agents, n_types = len(matrix), len(durations)
    if policy == "adaptive_state_controller":
        if n_agents < 2:
            raise ValueError("adaptive imbalance normalization requires at least two agents")
        if adaptive_thresholds is None or adaptive_diagnostics is None:
            raise ValueError("adaptive policy requires thresholds and an aggregate diagnostics sink")
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
    adaptive_state = "SPECIALIZATION"
    for index, task in enumerate(tasks):
        time, task_type = task.arrival_time, task.task_type
        selected_adaptive_strategy: str | None = None
        if policy == "adaptive_state_controller":
            workloads = tuple(max(0.0, available_at[i] - time) for i in range(n_agents))
            congestion, imbalance = _adaptive_state_metrics(
                workloads, fsum(durations) / len(durations)
            )
            previous_state = adaptive_state
            adaptive_state = _next_adaptive_state(
                adaptive_state, congestion, imbalance, adaptive_thresholds
            )
            adaptive_diagnostics.record(
                time, horizon, previous_state, adaptive_state, congestion, imbalance
            )
            selected_adaptive_strategy = {
                "SPECIALIZATION": "S1",
                "BALANCED": "S2",
                "LOAD_DISTRIBUTION": "S0",
            }[adaptive_state]
        if mapping is not None:
            agent = mapping[task_type]
        elif policy == "adaptive_state_controller" and selected_adaptive_strategy == "S1":
            agent = max(range(n_agents), key=lambda i: matrix[i][task_type])
        elif policy == "adaptive_state_controller" and selected_adaptive_strategy == "S2":
            agent = max(
                range(n_agents),
                key=lambda i: matrix[i][task_type]
                / (max(0.0, available_at[i] - time) + durations[task_type]),
            )
        elif policy == "adaptive_state_controller":  # LOAD_DISTRIBUTION -> unchanged S0
            agent = min(range(n_agents), key=lambda i: max(0.0, available_at[i] - time))
        elif policy == "max_effectiveness":
            agent = max(range(n_agents), key=lambda i: matrix[i][task_type])
        elif policy == "lowest_workload":
            agent = min(
                range(n_agents),
                key=lambda i: max(0.0, available_at[i] - time),
            )
        elif policy == "specialist_backup":
            specialist = max(range(n_agents), key=lambda i: matrix[i][task_type])
            specialist_work = max(0.0, available_at[specialist] - time)
            if specialist_work <= workload_threshold_multiplier * durations[task_type]:
                agent = specialist
            else:
                available_backups = [
                    i for i in range(n_agents)
                    if i != specialist
                    and max(0.0, available_at[i] - time) == 0.0
                    and matrix[i][task_type] >= minimum_backup_effectiveness
                ]
                agent = (
                    max(available_backups, key=lambda i: matrix[i][task_type])
                    if available_backups else specialist
                )
        elif policy == "effectiveness_load_ratio":
            # All service times are positive. W_i is remaining active service
            # plus queued work, observable from the queue tail at arrival time.
            agent = max(
                range(n_agents),
                key=lambda i: matrix[i][task_type]
                / (max(0.0, available_at[i] - time) + durations[task_type]),
            )
        else:
            raise ValueError(f"unknown temporal allocation policy: {policy}")

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


def _adaptive_state_metrics(
    workloads: Sequence[float], reference_service_time: float
) -> tuple[float, float]:
    """Return normalized congestion C and imbalance I from pre-decision W_i."""
    if (
        not workloads
        or isinstance(reference_service_time, bool)
        or not isinstance(reference_service_time, (int, float))
        or not isfinite(reference_service_time)
        or reference_service_time <= 0
        or any(not isfinite(value) or value < 0 for value in workloads)
    ):
        raise ValueError("workloads and reference service time must be finite and nonnegative/positive")
    total = fsum(workloads)
    if total == 0:
        return 0.0, 0.0
    concentration = max(workloads) / total
    n_agents = len(workloads)
    imbalance = (n_agents * concentration - 1.0) / (n_agents - 1)
    congestion = total / (n_agents * reference_service_time)
    return congestion, max(0.0, min(1.0, imbalance))


def _next_adaptive_state(
    current: str,
    congestion: float,
    imbalance: float,
    thresholds: AdaptiveThresholds,
) -> str:
    """Apply deterministic three-state rule with separate entry/exit bands."""
    if current not in {"SPECIALIZATION", "BALANCED", "LOAD_DISTRIBUTION"}:
        raise ValueError(f"unknown adaptive state: {current}")
    if not isfinite(congestion) or congestion < 0 or not isfinite(imbalance) or not 0 <= imbalance <= 1:
        raise ValueError("adaptive state metrics are outside their valid domains")
    thresholds.validate()
    if current == "LOAD_DISTRIBUTION":
        return "BALANCED" if congestion < thresholds.congestion_load_exit else current
    if congestion >= thresholds.congestion_load_enter:
        return "LOAD_DISTRIBUTION"
    if current == "SPECIALIZATION":
        return (
            "BALANCED"
            if congestion >= thresholds.congestion_balanced_enter
            or imbalance >= thresholds.imbalance_balanced_enter
            else current
        )
    if (
        congestion < thresholds.congestion_specialization_exit
        and imbalance < thresholds.imbalance_specialization_exit
    ):
        return "SPECIALIZATION"
    return current


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
    completed_at_horizon = tuple(
        task for task in decisions if task.completion_time <= horizon
    )
    completed_effectiveness = fsum(task.effectiveness for task in completed_at_horizon)
    waits = [task.waiting_time for task in decisions]
    responses = [task.response_time for task in decisions]
    assigned_count = tuple(
        sum(task.agent_index == agent for task in decisions) for agent in range(n_agents)
    )
    effectiveness_by_agent = tuple(
        fsum(task.effectiveness for task in decisions if task.agent_index == agent)
        for agent in range(n_agents)
    )
    unfinished_by_agent = tuple(
        tuple(
            task for task in decisions
            if task.agent_index == agent and task.completion_time > horizon
        )
        for agent in range(n_agents)
    )
    pending_count = tuple(len(tasks) for tasks in unfinished_by_agent)
    pending_work = tuple(
        fsum(task.completion_time - max(task.service_start, horizon) for task in tasks)
        for tasks in unfinished_by_agent
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
        completed_effectiveness_total_at_horizon=completed_effectiveness,
        j_h=completed_effectiveness / len(decisions),
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
        pending_task_count_by_agent=pending_count,
        pending_work_at_horizon_by_agent=pending_work,
        utilization_by_agent=utilization,
        makespan=max(task.completion_time for task in decisions) - min(task.arrival_time for task in decisions),
    )


def _nearest_rank(values: Sequence[float], quantile: float) -> float:
    ordered = sorted(values)
    return ordered[ceil(quantile * len(ordered)) - 1]


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
