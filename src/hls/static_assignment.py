"""Exact finite static allocation and effectiveness-resource models.

The models compare one-agent assignment with task-wise routing and, separately,
resource-constrained time-sharing. They have fixed competence and no learning.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping


ASSIGNMENTS = ("same_agent_1", "agent_1_task_1__agent_2_task_2", "agent_2_task_1__agent_1_task_2", "same_agent_2")
SAME_AGENT_ASSIGNMENTS = ("same_agent_1", "same_agent_2")
EXACT_TOL = 1e-12


@dataclass(frozen=True)
class AllocationEvaluation:
    """Values of all static routing policies at one demand mixture."""

    task_1_probability: float
    policy_values: Mapping[str, float]
    best_same_agent_effectiveness: float
    best_taskwise_effectiveness: float
    allocation_gain: float
    allocation_gain_closed_form: float | None


@dataclass(frozen=True)
class StaticAllocationModel:
    """Equal-resource static effectiveness matrix for two agents and two tasks.

    Each matrix entry is the effectiveness of an agent on a task. The
    resource cost is intentionally absent from the numerical objective because
    all four assignments have the same consumption and the fixed budget makes
    every pure policy feasible.
    """

    effect_agent1_task1: float
    effect_agent1_task2: float
    effect_agent2_task1: float
    effect_agent2_task2: float

    def __post_init__(self) -> None:
        if not all(isfinite(value) for value in (self.effect_agent1_task1, self.effect_agent1_task2, self.effect_agent2_task1, self.effect_agent2_task2)):
            raise ValueError("effectiveness values must be finite")

    @property
    def strict_crossed_advantage(self) -> bool:
        """Whether the task-wise best agent changes strictly between tasks."""
        return (self.effect_agent1_task1 - self.effect_agent2_task1) * (self.effect_agent1_task2 - self.effect_agent2_task2) < 0.0

    @property
    def advantage_gaps(self) -> tuple[float, float]:
        """Return positive task-wise gaps when strict crossed advantage holds."""
        if not self.strict_crossed_advantage:
            raise ValueError("closed-form crossed-advantage quantities are inapplicable")
        return (abs(self.effect_agent1_task1 - self.effect_agent2_task1), abs(self.effect_agent1_task2 - self.effect_agent2_task2))

    def policy_values(self, task_1_probability: float) -> dict[str, float]:
        """Compute the four possible assignment values for ``P(q=1)=task_1_probability``."""
        _validate_demand_probability(task_1_probability)
        return {
            "same_agent_1": task_1_probability * self.effect_agent1_task1 + (1.0 - task_1_probability) * self.effect_agent1_task2,
            "agent_1_task_1__agent_2_task_2": task_1_probability * self.effect_agent1_task1 + (1.0 - task_1_probability) * self.effect_agent2_task2,
            "agent_2_task_1__agent_1_task_2": task_1_probability * self.effect_agent2_task1 + (1.0 - task_1_probability) * self.effect_agent1_task2,
            "same_agent_2": task_1_probability * self.effect_agent2_task1 + (1.0 - task_1_probability) * self.effect_agent2_task2,
        }

    def best_same_agent_effectiveness(self, task_1_probability: float) -> float:
        """Best same-agent-for-both-tasks effectiveness."""
        values = self.policy_values(task_1_probability)
        return max(values[policy] for policy in SAME_AGENT_ASSIGNMENTS)

    def best_taskwise_effectiveness(self, task_1_probability: float) -> float:
        """Best independently task-routed effectiveness."""
        return max(self.policy_values(task_1_probability).values())

    def allocation_gain(self, task_1_probability: float) -> float:
        """Organizational gain of ROUTE over the best ONE policy."""
        return self.best_taskwise_effectiveness(task_1_probability) - self.best_same_agent_effectiveness(task_1_probability)

    def allocation_gain_closed_form(self, task_1_probability: float) -> float | None:
        """Return min(task_1_probability*A1, (1-task_1_probability)*A2) when strict crossed advantage holds."""
        _validate_demand_probability(task_1_probability)
        if not self.strict_crossed_advantage:
            return None
        a1, a2 = self.advantage_gaps
        return min(task_1_probability * a1, (1.0 - task_1_probability) * a2)

    def switching_probability(self) -> float | None:
        """Return task_1_probability*=A2/(A1+A2) for strict crossed advantage."""
        if not self.strict_crossed_advantage:
            return None
        a1, a2 = self.advantage_gaps
        return a2 / (a1 + a2)

    def maximum_allocation_gain(self) -> float | None:
        """Return A1*A2/(A1+A2) for strict crossed advantage."""
        if not self.strict_crossed_advantage:
            return None
        a1, a2 = self.advantage_gaps
        return a1 * a2 / (a1 + a2)

    def one_time_sharing_value(self, task_1_probability: float, weight_on_same_agent_1: float) -> float:
        """Scalar value of a convex combination of the two ONE endpoints."""
        _validate_demand_probability(task_1_probability)
        if not 0.0 <= weight_on_same_agent_1 <= 1.0:
            raise ValueError("time-sharing weight must lie in [0, 1]")
        values = self.policy_values(task_1_probability)
        return weight_on_same_agent_1 * values["same_agent_1"] + (1.0 - weight_on_same_agent_1) * values["same_agent_2"]

    def evaluate(self, task_1_probability: float) -> AllocationEvaluation:
        values = self.policy_values(task_1_probability)
        best_same_agent_effectiveness = max(values[policy] for policy in SAME_AGENT_ASSIGNMENTS)
        best_taskwise_effectiveness = max(values.values())
        return AllocationEvaluation(
            task_1_probability=task_1_probability,
            policy_values=values,
            best_same_agent_effectiveness=best_same_agent_effectiveness,
            best_taskwise_effectiveness=best_taskwise_effectiveness,
            allocation_gain=best_taskwise_effectiveness - best_same_agent_effectiveness,
            allocation_gain_closed_form=self.allocation_gain_closed_form(task_1_probability),
        )


def demand_sweep(model: StaticAllocationModel, points: int = 1001) -> tuple[AllocationEvaluation, ...]:
    """Evaluate an inclusive, uniformly spaced demand sweep on [0, 1]."""
    if points < 2:
        raise ValueError("a demand sweep needs at least two points")
    return tuple(model.evaluate(index / (points - 1)) for index in range(points))


def _validate_demand_probability(task_1_probability: float) -> None:
    if not isfinite(task_1_probability) or not 0.0 <= task_1_probability <= 1.0:
        raise ValueError("task_1_probability must be finite and lie in [0, 1]")


@dataclass(frozen=True, order=True)
class ResourceEffectivenessPoint:
    """A static attainable point represented as ``(resource, effectiveness)``."""

    resource: float
    effectiveness: float

    def __post_init__(self) -> None:
        if not isfinite(self.resource) or not isfinite(self.effectiveness):
            raise ValueError("resource/effectiveness coordinates must be finite")


@dataclass(frozen=True)
class ResourceAllocationEvaluation:
    """Bicriterion resource-constrained allocation values at one demand mixture and budget."""

    task_1_probability: float
    budget: float
    policy_points: Mapping[str, ResourceEffectivenessPoint]
    same_agent_hull: tuple[ResourceEffectivenessPoint, ...]
    taskwise_hull: tuple[ResourceEffectivenessPoint, ...]
    best_same_agent_effectiveness: float | None
    best_taskwise_effectiveness: float | None
    allocation_gain: float | None


@dataclass(frozen=True)
class ResourceAllocationMaximumGain:
    """Maximum gain over the common feasible budget domain."""

    budget: float
    allocation_gain: float


@dataclass(frozen=True)
class ResourceConstrainedAllocationModel:
    """Static equal-demand-weight bicriterion two-agent/two-task model.

    Each entry pairs agent-task effectiveness with its resource consumption.
    The model only constructs deterministic routing points and their admissible
    time-sharing convex hulls; it has no state transition or development term.
    """

    effect_agent1_task1: float
    resource_agent1_task1: float
    effect_agent1_task2: float
    resource_agent1_task2: float
    effect_agent2_task1: float
    resource_agent2_task1: float
    effect_agent2_task2: float
    resource_agent2_task2: float

    def __post_init__(self) -> None:
        values = (self.effect_agent1_task1, self.resource_agent1_task1, self.effect_agent1_task2, self.resource_agent1_task2, self.effect_agent2_task1, self.resource_agent2_task1, self.effect_agent2_task2, self.resource_agent2_task2)
        if not all(isfinite(value) for value in values):
            raise ValueError("effectiveness/resource values must be finite")

    def policy_points(self, task_1_probability: float) -> dict[str, ResourceEffectivenessPoint]:
        """Return Z11, Z12, Z21, and Z22 as ``(R,Y)`` points."""
        _validate_demand_probability(task_1_probability)
        return {
            "same_agent_1": ResourceEffectivenessPoint(
                task_1_probability * self.resource_agent1_task1 + (1.0 - task_1_probability) * self.resource_agent1_task2,
                task_1_probability * self.effect_agent1_task1 + (1.0 - task_1_probability) * self.effect_agent1_task2,
            ),
            "agent_1_task_1__agent_2_task_2": ResourceEffectivenessPoint(
                task_1_probability * self.resource_agent1_task1 + (1.0 - task_1_probability) * self.resource_agent2_task2,
                task_1_probability * self.effect_agent1_task1 + (1.0 - task_1_probability) * self.effect_agent2_task2,
            ),
            "agent_2_task_1__agent_1_task_2": ResourceEffectivenessPoint(
                task_1_probability * self.resource_agent2_task1 + (1.0 - task_1_probability) * self.resource_agent1_task2,
                task_1_probability * self.effect_agent2_task1 + (1.0 - task_1_probability) * self.effect_agent1_task2,
            ),
            "same_agent_2": ResourceEffectivenessPoint(
                task_1_probability * self.resource_agent2_task1 + (1.0 - task_1_probability) * self.resource_agent2_task2,
                task_1_probability * self.effect_agent2_task1 + (1.0 - task_1_probability) * self.effect_agent2_task2,
            ),
        }

    def same_agent_hull(self, task_1_probability: float) -> tuple[ResourceEffectivenessPoint, ...]:
        points = self.policy_points(task_1_probability)
        return upper_efficient_hull(points[key] for key in SAME_AGENT_ASSIGNMENTS)

    def taskwise_hull(self, task_1_probability: float) -> tuple[ResourceEffectivenessPoint, ...]:
        return upper_efficient_hull(self.policy_points(task_1_probability).values())

    def evaluate(self, task_1_probability: float, budget: float) -> ResourceAllocationEvaluation:
        if not isfinite(budget):
            raise ValueError("budget must be finite")
        points = self.policy_points(task_1_probability)
        same_agent_hull = upper_efficient_hull(points[key] for key in SAME_AGENT_ASSIGNMENTS)
        taskwise_hull = upper_efficient_hull(points.values())
        best_same_agent_effectiveness = upper_hull_value(same_agent_hull, budget)
        best_taskwise_effectiveness = upper_hull_value(taskwise_hull, budget)
        allocation_gain = None if best_same_agent_effectiveness is None or best_taskwise_effectiveness is None else best_taskwise_effectiveness - best_same_agent_effectiveness
        return ResourceAllocationEvaluation(
            task_1_probability=task_1_probability,
            budget=budget,
            policy_points=points,
            same_agent_hull=same_agent_hull,
            taskwise_hull=taskwise_hull,
            best_same_agent_effectiveness=best_same_agent_effectiveness,
            best_taskwise_effectiveness=best_taskwise_effectiveness,
            allocation_gain=allocation_gain,
        )

    @property
    def determinant_d(self) -> float:
        """D = Δr_1 Δy_2 − Δy_1 Δr_2, the determinant of task-wise resource/effectiveness differences."""
        effect_advantage_task1 = self.effect_agent1_task1 - self.effect_agent2_task1
        resource_difference_task1 = self.resource_agent1_task1 - self.resource_agent2_task1
        effect_advantage_task2 = self.effect_agent1_task2 - self.effect_agent2_task2
        resource_difference_task2 = self.resource_agent1_task2 - self.resource_agent2_task2
        return resource_difference_task1 * effect_advantage_task2 - effect_advantage_task1 * resource_difference_task2

    def parallelogram_area(self, task_1_probability: float) -> float:
        """Geometric area of the four routing points at demand mixture ``task_1_probability``."""
        points = self.policy_points(task_1_probability)
        first = _subtract(points["same_agent_1"], points["agent_2_task_1__agent_1_task_2"])
        second = _subtract(points["agent_1_task_1__agent_2_task_2"], points["same_agent_1"])
        return abs(first.resource * second.effectiveness - first.effectiveness * second.resource)

    def parallelogram_identity_error(self, task_1_probability: float) -> float:
        """Maximum componentwise error in Z11 + Z22 = Z12 + Z21."""
        points = self.policy_points(task_1_probability)
        return max(
            abs(points["same_agent_1"].resource + points["same_agent_2"].resource - points["agent_1_task_1__agent_2_task_2"].resource - points["agent_2_task_1__agent_1_task_2"].resource),
            abs(points["same_agent_1"].effectiveness + points["same_agent_2"].effectiveness - points["agent_1_task_1__agent_2_task_2"].effectiveness - points["agent_2_task_1__agent_1_task_2"].effectiveness),
        )

    def parallelogram_area_closed_form(self, task_1_probability: float) -> float:
        _validate_demand_probability(task_1_probability)
        return task_1_probability * (1.0 - task_1_probability) * abs(self.determinant_d)

    def maximum_allocation_gain(self, task_1_probability: float) -> ResourceAllocationMaximumGain | None:
        """Evaluate gain at all relevant upper-hull breakpoints exactly."""
        same_agent_hull = self.same_agent_hull(task_1_probability)
        taskwise_hull = self.taskwise_hull(task_1_probability)
        common_minimum = max(same_agent_hull[0].resource, taskwise_hull[0].resource)
        candidates = sorted(
            {
                common_minimum,
                *(point.resource for point in same_agent_hull if point.resource >= common_minimum - EXACT_TOL),
                *(point.resource for point in taskwise_hull if point.resource >= common_minimum - EXACT_TOL),
            }
        )
        values = []
        for budget in candidates:
            evaluation = self.evaluate(task_1_probability, budget)
            if evaluation.allocation_gain is not None:
                values.append(ResourceAllocationMaximumGain(budget, evaluation.allocation_gain))
        return max(values, key=lambda item: item.allocation_gain) if values else None

    def positive_gain_intervals(self, task_1_probability: float) -> tuple[tuple[float, float | None], ...]:
        """Return exact piecewise-linear open intervals with strictly positive gain.

        ``None`` denotes an interval that remains positive after both frontiers
        have saturated.
        """
        same_agent_hull = self.same_agent_hull(task_1_probability)
        taskwise_hull = self.taskwise_hull(task_1_probability)
        lower = max(same_agent_hull[0].resource, taskwise_hull[0].resource)
        breakpoints = sorted(
            {
                lower,
                *(point.resource for point in same_agent_hull if point.resource >= lower - EXACT_TOL),
                *(point.resource for point in taskwise_hull if point.resource >= lower - EXACT_TOL),
            }
        )
        intervals: list[tuple[float, float | None]] = []
        for left, right in zip(breakpoints, breakpoints[1:]):
            left_gain = self.evaluate(task_1_probability, left).allocation_gain
            right_gain = self.evaluate(task_1_probability, right).allocation_gain
            assert left_gain is not None and right_gain is not None
            interval = _strict_positive_interval(left, right, left_gain, right_gain)
            if interval is not None:
                intervals.append(interval)
        tail_start = breakpoints[-1]
        tail_gain = self.evaluate(task_1_probability, tail_start).allocation_gain
        assert tail_gain is not None
        if tail_gain > EXACT_TOL:
            intervals.append((tail_start, None))
        return _merge_intervals(intervals)


def upper_efficient_hull(
    points: Iterable[ResourceEffectivenessPoint], tol: float = EXACT_TOL
) -> tuple[ResourceEffectivenessPoint, ...]:
    """Construct the increasing-resource upper concave hull of finite points.

    At a shared resource coordinate only the greatest effectiveness is retained.
    Any point dominated by a lower-resource point is removed. Collinear middle
    points are removed so the returned vertices define the value function
    directly by affine interpolation.
    """
    raw = sorted(points)
    if not raw:
        raise ValueError("an upper hull requires at least one point")
    by_resource: list[ResourceEffectivenessPoint] = []
    for point in raw:
        if by_resource and abs(point.resource - by_resource[-1].resource) <= tol:
            previous = by_resource[-1]
            if point.effectiveness > previous.effectiveness + tol:
                by_resource[-1] = ResourceEffectivenessPoint(previous.resource, point.effectiveness)
            continue
        by_resource.append(point)

    nondominated: list[ResourceEffectivenessPoint] = []
    best_effectiveness = float("-inf")
    for point in by_resource:
        if point.effectiveness <= best_effectiveness + tol:
            continue
        nondominated.append(point)
        best_effectiveness = point.effectiveness

    hull: list[ResourceEffectivenessPoint] = []
    for point in nondominated:
        while len(hull) >= 2 and _slope(hull[-2], hull[-1]) <= _slope(hull[-1], point) + tol:
            hull.pop()
        hull.append(point)
    return tuple(hull)


def upper_hull_value(
    hull: tuple[ResourceEffectivenessPoint, ...], budget: float, tol: float = EXACT_TOL
) -> float | None:
    """Evaluate the attainable maximum effectiveness at a resource budget."""
    if not hull:
        raise ValueError("an upper hull requires at least one point")
    if budget < hull[0].resource - tol:
        return None
    if len(hull) == 1 or budget <= hull[0].resource + tol:
        return hull[0].effectiveness
    if budget >= hull[-1].resource - tol:
        return hull[-1].effectiveness
    for left, right in zip(hull, hull[1:]):
        if budget <= right.resource + tol:
            return left.effectiveness + _slope(left, right) * (budget - left.resource)
    raise AssertionError("budget evaluation did not find a hull segment")


def _slope(left: ResourceEffectivenessPoint, right: ResourceEffectivenessPoint) -> float:
    return (right.effectiveness - left.effectiveness) / (right.resource - left.resource)


def _subtract(
    left: ResourceEffectivenessPoint, right: ResourceEffectivenessPoint
) -> ResourceEffectivenessPoint:
    return ResourceEffectivenessPoint(
        left.resource - right.resource,
        left.effectiveness - right.effectiveness,
    )


def _strict_positive_interval(
    left: float, right: float, left_value: float, right_value: float
) -> tuple[float, float] | None:
    if left_value <= EXACT_TOL and right_value <= EXACT_TOL:
        return None
    if left_value > EXACT_TOL and right_value > EXACT_TOL:
        return (left, right)
    root = left + (right - left) * (-left_value) / (right_value - left_value)
    return (root, right) if right_value > EXACT_TOL else (left, root)


def _merge_intervals(
    intervals: list[tuple[float, float | None]]
) -> tuple[tuple[float, float | None], ...]:
    if not intervals:
        return ()
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        previous_start, previous_end = merged[-1]
        if previous_end is not None and abs(previous_end - start) <= EXACT_TOL:
            merged[-1] = (previous_start, end)
        else:
            merged.append((start, end))
    return tuple(merged)


REFERENCE_RESOURCE_ALLOCATION_CASES: Mapping[str, ResourceConstrainedAllocationModel] = {
    "homogeneous_null": ResourceConstrainedAllocationModel(.8, .5, .8, .5, .8, .5, .8, .5),
    "taskwise_dominance_null": ResourceConstrainedAllocationModel(.9, .4, .8, .5, .6, .7, .5, .8),
    "equal_resource_crossed_specialization": ResourceConstrainedAllocationModel(1.0, .5, .2, .5, .2, .5, 1.0, .5),
    "effectiveness_resource_tradeoff": ResourceConstrainedAllocationModel(1.0, .8, .3, .4, .4, .4, .9, .8),
    "geometric_expansion_without_gain": ResourceConstrainedAllocationModel(1.0, .4, 1.0, .4, .5, .8, .3, .6),
    "bounded_gain_budget_window": ResourceConstrainedAllocationModel(.7, .6, .9, .7, .5, .3, .9, .2),
}
