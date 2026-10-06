"""Known-environment configuration × environment sweep over prototype-v0 physics.

The module deliberately reuses the v0 state, reward, MIS transition, and fair
policy-class evaluators.  It adds only a deterministic representation of known
task sequences parameterized by composition (nu), between-half change (chi),
and within-half clustering (rho).  It does not define an HLS mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from math import isclose
from typing import Iterable

from .configuration_environment_policy_v0 import (
    CONFIGURATIONS,
    EXACT_TOL,
    PolicyEvaluation,
    State,
    Task,
    evaluate_policy,
)


GRID_LEVELS: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)
HALF_HORIZON = 8
HORIZON = 2 * HALF_HORIZON
ENABLED_LEARNING_SCALE = 0.5


def _grid_index(value: float, *, name: str) -> int:
    """Return the exact declared grid index; arbitrary reals are not silently rounded."""
    for index, level in enumerate(GRID_LEVELS):
        if isclose(value, level, abs_tol=EXACT_TOL):
            return index
    raise ValueError(f"{name} must be one of {GRID_LEVELS}")


@dataclass(frozen=True, order=True)
class EnvironmentSpec:
    """One fully known deterministic environment.

    ``nu`` is the normalized A-composition coordinate: its five levels map to
    2, 3, 4, 5, and 6 A tasks per half before temporal change.  Thus the
    aggregate A share ranges from .25 to .75; the endpoints are deliberately
    interior so that a nonzero inter-half change remains feasible.

    ``chi`` requests 0--4 A tasks to move from the first to the second half.
    At composition boundaries the requested move is clipped by feasibility;
    the effective shift is recorded rather than hidden.

    ``rho`` selects a deterministic ordering quantile from least to most
    persistent among binary sequences with the already fixed half composition.
    It cannot alter composition or inter-half change.
    """

    nu: float
    chi: float
    rho: float

    def __post_init__(self) -> None:
        _grid_index(self.nu, name="nu")
        _grid_index(self.chi, name="chi")
        _grid_index(self.rho, name="rho")

    @property
    def identifier(self) -> str:
        return f"nu_{self.nu:.2f}_chi_{self.chi:.2f}_rho_{self.rho:.2f}"


@dataclass(frozen=True)
class EnvironmentDiagnostics:
    """Auditable semantics of a generated known sequence."""

    sequence: tuple[Task, ...]
    first_half_a_count: int
    second_half_a_count: int
    aggregate_a_count: int
    requested_shift: int
    effective_shift: int
    adjacent_same_pairs: int

    @property
    def inter_half_change_count(self) -> int:
        return self.second_half_a_count - self.first_half_a_count


def _persistence(sequence: tuple[Task, ...]) -> int:
    return sum(left == right for left, right in zip(sequence, sequence[1:]))


def _half_patterns(a_count: int) -> tuple[tuple[Task, ...], ...]:
    """Order all fixed-composition half sequences from least to most clustered."""
    if not 0 <= a_count <= HALF_HORIZON:
        raise ValueError("A count must be feasible in a half horizon")
    patterns = []
    for a_positions in combinations(range(HALF_HORIZON), a_count):
        pattern = [1] * HALF_HORIZON
        for index in a_positions:
            pattern[index] = 0
        patterns.append(tuple(pattern))
    # Fewer adjacent-equal pairs means less persistence. Lexicographic order resolves ties.
    return tuple(sorted(patterns, key=lambda pattern: (_persistence(pattern), pattern)))


def _ordered_half(a_count: int, rho: float) -> tuple[Task, ...]:
    patterns = _half_patterns(a_count)
    rho_index = _grid_index(rho, name="rho")
    selected_index = (rho_index * (len(patterns) - 1)) // (len(GRID_LEVELS) - 1)
    return patterns[selected_index]


def environment_diagnostics(spec: EnvironmentSpec) -> EnvironmentDiagnostics:
    """Construct a sequence and preserve every effective, finite-grid property."""
    base_a = 2 + _grid_index(spec.nu, name="nu")
    requested_shift = _grid_index(spec.chi, name="chi")
    feasible_shift = min(base_a, HALF_HORIZON - base_a)
    effective_shift = min(requested_shift, feasible_shift)
    first_a = base_a - effective_shift
    second_a = base_a + effective_shift
    first = _ordered_half(first_a, spec.rho)
    second = _ordered_half(second_a, spec.rho)
    sequence = first + second
    return EnvironmentDiagnostics(
        sequence=sequence,
        first_half_a_count=first_a,
        second_half_a_count=second_a,
        aggregate_a_count=first_a + second_a,
        requested_shift=requested_shift,
        effective_shift=effective_shift,
        adjacent_same_pairs=_persistence(sequence),
    )


def environment_specs() -> tuple[EnvironmentSpec, ...]:
    """Return the declared 5 × 5 × 5 known-environment grid."""
    return tuple(EnvironmentSpec(nu, chi, rho) for nu, chi, rho in product(GRID_LEVELS, repeat=3))


@dataclass(frozen=True)
class SweepPoint:
    configuration: str
    environment: EnvironmentSpec
    development_enabled: bool
    learning_scale: float
    diagnostics: EnvironmentDiagnostics
    greedy: PolicyEvaluation
    joint_dp: PolicyEvaluation

    @property
    def performance(self) -> float:
        """``P``: development-conditioned joint-oracle performance."""
        return self.joint_dp.value

    @property
    def management_value(self) -> float:
        """``M``: joint-oracle value over the strong fair greedy comparator."""
        return self.joint_dp.value - self.greedy.value


def evaluate_sweep(
    *,
    learning_scale: float = ENABLED_LEARNING_SCALE,
    development_enabled: bool = True,
    specifications: Iterable[EnvironmentSpec] | None = None,
) -> tuple[SweepPoint, ...]:
    """Evaluate every configuration against the same known environment grid."""
    if learning_scale < 0.0:
        raise ValueError("learning_scale must be non-negative")
    effective_scale = learning_scale if development_enabled else 0.0
    specs = environment_specs() if specifications is None else tuple(specifications)
    points: list[SweepPoint] = []
    for spec in specs:
        diagnostics = environment_diagnostics(spec)
        for configuration, state in CONFIGURATIONS.items():
            greedy = evaluate_policy(state, diagnostics.sequence, effective_scale, "GREEDY_USE")
            joint = evaluate_policy(state, diagnostics.sequence, effective_scale, "JOINT_DP")
            if joint.value + EXACT_TOL < greedy.value:
                raise AssertionError("JOINT_DP must weakly dominate the fair GREEDY_USE policy class")
            points.append(
                SweepPoint(
                    configuration=configuration,
                    environment=spec,
                    development_enabled=development_enabled,
                    learning_scale=effective_scale,
                    diagnostics=diagnostics,
                    greedy=greedy,
                    joint_dp=joint,
                )
            )
    return tuple(points)


def _point_index(points: Iterable[SweepPoint]) -> dict[tuple[str, EnvironmentSpec], SweepPoint]:
    index = {(point.configuration, point.environment): point for point in points}
    if len(index) != len(tuple(points)):
        raise ValueError("each configuration/environment pair must occur exactly once")
    return index


def paired_development_rows(
    enabled: tuple[SweepPoint, ...],
    disabled: tuple[SweepPoint, ...],
) -> tuple[dict[str, object], ...]:
    """Return P, M, and L ledgers for matching ON/OFF conditions."""
    off_index = _point_index(disabled)
    rows: list[dict[str, object]] = []
    for on in enabled:
        off = off_index[(on.configuration, on.environment)]
        if off.diagnostics.sequence != on.diagnostics.sequence:
            raise AssertionError("development ablation must use the identical known sequence")
        rows.append(
            {
                "environment": on.environment.identifier,
                "nu": on.environment.nu,
                "chi": on.environment.chi,
                "rho": on.environment.rho,
                "configuration": on.configuration,
                "sequence": "".join("A" if task == 0 else "B" for task in on.diagnostics.sequence),
                "P": on.performance,
                "J_GREEDY_plus": on.greedy.value,
                "M": on.management_value,
                "P0": off.performance,
                "J_GREEDY_0": off.greedy.value,
                "M0": off.management_value,
                "L": on.performance - off.performance,
                "first_half_A": on.diagnostics.first_half_a_count,
                "second_half_A": on.diagnostics.second_half_a_count,
                "aggregate_A": on.diagnostics.aggregate_a_count,
                "requested_shift": on.diagnostics.requested_shift,
                "effective_shift": on.diagnostics.effective_shift,
                "adjacent_same_pairs": on.diagnostics.adjacent_same_pairs,
            }
        )
    return tuple(rows)


def pairwise_interactions(
    enabled: tuple[SweepPoint, ...],
    disabled: tuple[SweepPoint, ...],
) -> tuple[dict[str, object], ...]:
    """Return the declared development-by-configuration interaction ``I``."""
    on_index = _point_index(enabled)
    off_index = _point_index(disabled)
    rows: list[dict[str, object]] = []
    for spec in sorted({point.environment for point in enabled}):
        for left, right in combinations(sorted(CONFIGURATIONS), 2):
            on_gap = on_index[(left, spec)].performance - on_index[(right, spec)].performance
            off_gap = off_index[(left, spec)].performance - off_index[(right, spec)].performance
            rows.append(
                {
                    "environment": spec.identifier,
                    "nu": spec.nu,
                    "chi": spec.chi,
                    "rho": spec.rho,
                    "configuration_1": left,
                    "configuration_2": right,
                    "I": on_gap - off_gap,
                    "P_gap_plus": on_gap,
                    "P_gap_0": off_gap,
                }
            )
    return tuple(rows)


def argmax_configurations(points: tuple[SweepPoint, ...]) -> tuple[dict[str, object], ...]:
    """Map each environment to all DP-optimal configurations and their ranking."""
    index = _point_index(points)
    rows: list[dict[str, object]] = []
    for spec in sorted({point.environment for point in points}):
        values = {configuration: index[(configuration, spec)].performance for configuration in CONFIGURATIONS}
        best = max(values.values())
        winners = tuple(name for name in sorted(values) if best - values[name] <= EXACT_TOL)
        ranking = tuple(sorted(values, key=lambda name: (-values[name], name)))
        rows.append(
            {
                "environment": spec.identifier,
                "nu": spec.nu,
                "chi": spec.chi,
                "rho": spec.rho,
                "development_enabled": points[0].development_enabled,
                "argmax_configurations": "|".join(winners),
                "ranking": "|".join(ranking),
                "best_P": best,
            }
        )
    return tuple(rows)
