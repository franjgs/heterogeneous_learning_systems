"""Exact static two-agent/two-task ground truth for G1.1.

G1.1 isolates Beam 1 organization/use of fixed competences.  It has no state
transition, learning, competence evolution, or unequal-resource mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping


POLICIES = ("11", "12", "21", "22")
ONE_POLICIES = ("11", "22")
EXACT_TOL = 1e-12


@dataclass(frozen=True)
class G11Evaluation:
    """Values of all G1.1 routing policies at one demand mixture."""

    p: float
    policy_values: Mapping[str, float]
    y_one: float
    y_route: float
    delta_y: float
    delta_y_closed_form: float | None


@dataclass(frozen=True)
class G11Model:
    """Equal-resource static effectiveness matrix for two agents and two tasks.

    ``yij`` denotes the effectiveness of agent ``i`` on task ``j``.  The
    resource cost is intentionally absent from the numerical objective because
    all four assignments have the same consumption and the fixed budget makes
    every pure policy feasible.
    """

    y11: float
    y12: float
    y21: float
    y22: float

    def __post_init__(self) -> None:
        if not all(isfinite(value) for value in (self.y11, self.y12, self.y21, self.y22)):
            raise ValueError("effectiveness values must be finite")

    @property
    def strict_crossed_advantage(self) -> bool:
        """Whether the task-wise best agent changes strictly between tasks."""
        return (self.y11 - self.y21) * (self.y12 - self.y22) < 0.0

    @property
    def advantage_gaps(self) -> tuple[float, float]:
        """Return positive task-wise gaps when strict crossed advantage holds."""
        if not self.strict_crossed_advantage:
            raise ValueError("closed-form crossed-advantage quantities are inapplicable")
        return (abs(self.y11 - self.y21), abs(self.y12 - self.y22))

    def policy_values(self, p: float) -> dict[str, float]:
        """Compute Y11, Y12, Y21, and Y22 for ``P(q=1)=p``."""
        _validate_demand_probability(p)
        return {
            "11": p * self.y11 + (1.0 - p) * self.y12,
            "12": p * self.y11 + (1.0 - p) * self.y22,
            "21": p * self.y21 + (1.0 - p) * self.y12,
            "22": p * self.y21 + (1.0 - p) * self.y22,
        }

    def y_one(self, p: float) -> float:
        """Best same-agent-for-both-tasks effectiveness."""
        values = self.policy_values(p)
        return max(values[policy] for policy in ONE_POLICIES)

    def y_route(self, p: float) -> float:
        """Best independently task-routed effectiveness."""
        return max(self.policy_values(p).values())

    def delta_y(self, p: float) -> float:
        """Organizational gain of ROUTE over the best ONE policy."""
        return self.y_route(p) - self.y_one(p)

    def delta_y_closed_form(self, p: float) -> float | None:
        """Return min(p*A1, (1-p)*A2) when strict crossed advantage holds."""
        _validate_demand_probability(p)
        if not self.strict_crossed_advantage:
            return None
        a1, a2 = self.advantage_gaps
        return min(p * a1, (1.0 - p) * a2)

    def switching_probability(self) -> float | None:
        """Return p*=A2/(A1+A2) for strict crossed advantage."""
        if not self.strict_crossed_advantage:
            return None
        a1, a2 = self.advantage_gaps
        return a2 / (a1 + a2)

    def maximum_gain(self) -> float | None:
        """Return A1*A2/(A1+A2) for strict crossed advantage."""
        if not self.strict_crossed_advantage:
            return None
        a1, a2 = self.advantage_gaps
        return a1 * a2 / (a1 + a2)

    def one_time_sharing_value(self, p: float, weight_on_11: float) -> float:
        """Scalar value of a convex combination of the two ONE endpoints."""
        _validate_demand_probability(p)
        if not 0.0 <= weight_on_11 <= 1.0:
            raise ValueError("time-sharing weight must lie in [0, 1]")
        values = self.policy_values(p)
        return weight_on_11 * values["11"] + (1.0 - weight_on_11) * values["22"]

    def evaluate(self, p: float) -> G11Evaluation:
        values = self.policy_values(p)
        y_one = max(values[policy] for policy in ONE_POLICIES)
        y_route = max(values.values())
        return G11Evaluation(
            p=p,
            policy_values=values,
            y_one=y_one,
            y_route=y_route,
            delta_y=y_route - y_one,
            delta_y_closed_form=self.delta_y_closed_form(p),
        )


def demand_sweep(model: G11Model, points: int = 1001) -> tuple[G11Evaluation, ...]:
    """Evaluate an inclusive, uniformly spaced demand sweep on [0, 1]."""
    if points < 2:
        raise ValueError("a demand sweep needs at least two points")
    return tuple(model.evaluate(index / (points - 1)) for index in range(points))


def _validate_demand_probability(p: float) -> None:
    if not isfinite(p) or not 0.0 <= p <= 1.0:
        raise ValueError("p must be finite and lie in [0, 1]")


@dataclass(frozen=True, order=True)
class ResourceEffectivenessPoint:
    """A static attainable point represented as ``(resource, effectiveness)``."""

    resource: float
    effectiveness: float

    def __post_init__(self) -> None:
        if not isfinite(self.resource) or not isfinite(self.effectiveness):
            raise ValueError("resource/effectiveness coordinates must be finite")


@dataclass(frozen=True)
class G12Evaluation:
    """Bicriterion G1.2 values at one demand mixture and budget."""

    p: float
    budget: float
    policy_points: Mapping[str, ResourceEffectivenessPoint]
    one_hull: tuple[ResourceEffectivenessPoint, ...]
    route_hull: tuple[ResourceEffectivenessPoint, ...]
    y_one: float | None
    y_route: float | None
    delta_y: float | None


@dataclass(frozen=True)
class G12MaximumGain:
    """Maximum gain over the common feasible budget domain."""

    budget: float
    delta_y: float


@dataclass(frozen=True)
class G12Model:
    """Static equal-demand-weight bicriterion two-agent/two-task model.

    Each ``yij`` is effectiveness and each ``rij`` is resource consumption.
    The model only constructs deterministic routing points and their admissible
    time-sharing convex hulls; it has no state transition or development term.
    """

    y11: float
    r11: float
    y12: float
    r12: float
    y21: float
    r21: float
    y22: float
    r22: float

    def __post_init__(self) -> None:
        values = (self.y11, self.r11, self.y12, self.r12, self.y21, self.r21, self.y22, self.r22)
        if not all(isfinite(value) for value in values):
            raise ValueError("effectiveness/resource values must be finite")

    def policy_points(self, p: float) -> dict[str, ResourceEffectivenessPoint]:
        """Return Z11, Z12, Z21, and Z22 as ``(R,Y)`` points."""
        _validate_demand_probability(p)
        return {
            "11": ResourceEffectivenessPoint(
                p * self.r11 + (1.0 - p) * self.r12,
                p * self.y11 + (1.0 - p) * self.y12,
            ),
            "12": ResourceEffectivenessPoint(
                p * self.r11 + (1.0 - p) * self.r22,
                p * self.y11 + (1.0 - p) * self.y22,
            ),
            "21": ResourceEffectivenessPoint(
                p * self.r21 + (1.0 - p) * self.r12,
                p * self.y21 + (1.0 - p) * self.y12,
            ),
            "22": ResourceEffectivenessPoint(
                p * self.r21 + (1.0 - p) * self.r22,
                p * self.y21 + (1.0 - p) * self.y22,
            ),
        }

    def one_hull(self, p: float) -> tuple[ResourceEffectivenessPoint, ...]:
        points = self.policy_points(p)
        return upper_efficient_hull(points[key] for key in ONE_POLICIES)

    def route_hull(self, p: float) -> tuple[ResourceEffectivenessPoint, ...]:
        return upper_efficient_hull(self.policy_points(p).values())

    def evaluate(self, p: float, budget: float) -> G12Evaluation:
        if not isfinite(budget):
            raise ValueError("budget must be finite")
        points = self.policy_points(p)
        one_hull = upper_efficient_hull(points[key] for key in ONE_POLICIES)
        route_hull = upper_efficient_hull(points.values())
        y_one = upper_hull_value(one_hull, budget)
        y_route = upper_hull_value(route_hull, budget)
        delta_y = None if y_one is None or y_route is None else y_route - y_one
        return G12Evaluation(
            p=p,
            budget=budget,
            policy_points=points,
            one_hull=one_hull,
            route_hull=route_hull,
            y_one=y_one,
            y_route=y_route,
            delta_y=delta_y,
        )

    @property
    def determinant_d(self) -> float:
        """D = delta_r1*delta_y2 - delta_y1*delta_r2."""
        delta_y1 = self.y11 - self.y21
        delta_r1 = self.r11 - self.r21
        delta_y2 = self.y12 - self.y22
        delta_r2 = self.r12 - self.r22
        return delta_r1 * delta_y2 - delta_y1 * delta_r2

    def parallelogram_area(self, p: float) -> float:
        """Geometric area of the four routing points at demand mixture ``p``."""
        points = self.policy_points(p)
        first = _subtract(points["11"], points["21"])
        second = _subtract(points["12"], points["11"])
        return abs(first.resource * second.effectiveness - first.effectiveness * second.resource)

    def parallelogram_identity_error(self, p: float) -> float:
        """Maximum componentwise error in Z11 + Z22 = Z12 + Z21."""
        points = self.policy_points(p)
        return max(
            abs(points["11"].resource + points["22"].resource - points["12"].resource - points["21"].resource),
            abs(points["11"].effectiveness + points["22"].effectiveness - points["12"].effectiveness - points["21"].effectiveness),
        )

    def parallelogram_area_closed_form(self, p: float) -> float:
        _validate_demand_probability(p)
        return p * (1.0 - p) * abs(self.determinant_d)

    def maximum_gain(self, p: float) -> G12MaximumGain | None:
        """Evaluate gain at all relevant upper-hull breakpoints exactly."""
        one_hull = self.one_hull(p)
        route_hull = self.route_hull(p)
        common_minimum = max(one_hull[0].resource, route_hull[0].resource)
        candidates = sorted(
            {
                common_minimum,
                *(point.resource for point in one_hull if point.resource >= common_minimum - EXACT_TOL),
                *(point.resource for point in route_hull if point.resource >= common_minimum - EXACT_TOL),
            }
        )
        values = []
        for budget in candidates:
            evaluation = self.evaluate(p, budget)
            if evaluation.delta_y is not None:
                values.append(G12MaximumGain(budget, evaluation.delta_y))
        return max(values, key=lambda item: item.delta_y) if values else None

    def positive_gain_intervals(self, p: float) -> tuple[tuple[float, float | None], ...]:
        """Return exact piecewise-linear open intervals with strictly positive gain.

        ``None`` denotes an interval that remains positive after both frontiers
        have saturated.
        """
        one_hull = self.one_hull(p)
        route_hull = self.route_hull(p)
        lower = max(one_hull[0].resource, route_hull[0].resource)
        breakpoints = sorted(
            {
                lower,
                *(point.resource for point in one_hull if point.resource >= lower - EXACT_TOL),
                *(point.resource for point in route_hull if point.resource >= lower - EXACT_TOL),
            }
        )
        intervals: list[tuple[float, float | None]] = []
        for left, right in zip(breakpoints, breakpoints[1:]):
            left_gain = self.evaluate(p, left).delta_y
            right_gain = self.evaluate(p, right).delta_y
            assert left_gain is not None and right_gain is not None
            interval = _strict_positive_interval(left, right, left_gain, right_gain)
            if interval is not None:
                intervals.append(interval)
        tail_start = breakpoints[-1]
        tail_gain = self.evaluate(p, tail_start).delta_y
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


CANONICAL_G12_SCENARIOS: Mapping[str, G12Model] = {
    "S0_homogeneous_null": G12Model(.8, .5, .8, .5, .8, .5, .8, .5),
    "S1_pareto_dominance_null": G12Model(.9, .4, .8, .5, .6, .7, .5, .8),
    "S2_g11_embedded_equal_resource": G12Model(1.0, .5, .2, .5, .2, .5, 1.0, .5),
    "S3_bicriterion_tradeoff": G12Model(1.0, .8, .3, .4, .4, .4, .9, .8),
    "S4_geometric_expansion_null": G12Model(1.0, .4, 1.0, .4, .5, .8, .3, .6),
    "S5_bounded_gain_window": G12Model(.7, .6, .9, .7, .5, .3, .9, .2),
}
