"""Pure policy algebra and preregistered analysis for RQ0 confirmation.

This module never loads images or models.  Policy selection consumes frozen
VALIDATION scores; realized evaluation scores are supplied explicitly by the
caller (TEST only in the separately gated confirmatory mode).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

import numpy as np
import pandas as pd

DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
COSTS = (0.0, 0.02, 0.05, 0.10, 0.15)
HORIZONS = (1, 2, 5, 10)
TOLERANCE = 1e-12
ACTION_F0 = "F,0"
ACTION_D0 = "D,0"
ACTION_DREP = "D,REP"


@dataclass(frozen=True)
class Quantities:
    u_f: float
    u_d: float
    v0: float
    v_rep: float

    @property
    def rho(self) -> float:
        return self.u_f - self.u_d

    @property
    def delta_v(self) -> float:
        return self.v_rep - self.v0


def operational_value(
    fast: Mapping[str, float], deep: Mapping[str, float], cost: float
) -> float:
    return float(sum(max(float(fast[d]), float(deep[d]) - cost) for d in DOMAINS) / 4.0)


def quantities(
    domain: str,
    cost: float,
    f0: Mapping[str, float],
    deep: Mapping[str, float],
    rep: Mapping[str, float],
) -> Quantities:
    if domain not in DOMAINS:
        raise ValueError(f"unknown domain {domain!r}")
    return Quantities(
        u_f=float(f0[domain]),
        u_d=float(deep[domain]) - float(cost),
        v0=operational_value(f0, deep, cost),
        v_rep=operational_value(rep, deep, cost),
    )


def kappa_star(q: Quantities, horizon: float) -> float:
    return float(horizon * q.delta_v - max(q.rho, 0.0))


def action_values(q: Quantities, horizon: float, kappa: float) -> dict[str, float]:
    if kappa < 0:
        raise ValueError("kappa must be nonnegative")
    return {
        ACTION_F0: q.u_f + horizon * q.v0,
        ACTION_D0: q.u_d + horizon * q.v0,
        ACTION_DREP: q.u_d - kappa + horizon * q.v_rep,
    }


def choose_sep(q: Quantities, horizon: float, kappa: float) -> str:
    # Immediate tie goes to F, and F cannot release an opportunity.
    if q.rho >= -TOLERANCE:
        return ACTION_F0
    # Conditional development is strict; equality means no development.
    return ACTION_DREP if kappa < horizon * q.delta_v - TOLERANCE else ACTION_D0


def choose_hls(q: Quantities, horizon: float, kappa: float) -> str:
    # The threshold form avoids floating subtraction turning an algebraic tie
    # into a different decision. TOLERANCE is numerical only; inequalities in
    # the scientific outputs remain strict.
    if kappa < kappa_star(q, horizon) - TOLERANCE:
        return ACTION_DREP
    return ACTION_F0 if q.rho >= -TOLERANCE else ACTION_D0


def omega(q: Quantities, horizon: float, kappa: float) -> float:
    return float(max(0.0, -kappa + horizon * q.delta_v))


def choose_sepomega(q: Quantities, horizon: float, kappa: float) -> str:
    continuation = omega(q, horizon, kappa)
    # Routing ties go to F. A D route develops only for a strictly positive
    # maximizing continuation.
    if q.u_f >= q.u_d + continuation - TOLERANCE:
        return ACTION_F0
    return ACTION_DREP if continuation > TOLERANCE else ACTION_D0


def realized_j(action: str, q: Quantities, horizon: float, kappa: float) -> float:
    return action_values(q, horizon, kappa)[action]


def policy_row(
    selected: Quantities,
    realized: Quantities,
    horizon: float,
    kappa: float,
) -> dict[str, object]:
    sep = choose_sep(selected, horizon, kappa)
    hls = choose_hls(selected, horizon, kappa)
    coordinated = choose_sepomega(selected, horizon, kappa)
    j_sep = realized_j(sep, realized, horizon, kappa)
    j_hls = realized_j(hls, realized, horizon, kappa)
    j_coord = realized_j(coordinated, realized, horizon, kappa)
    return {
        "kappa": float(kappa),
        "kappa_star": kappa_star(selected, horizon),
        "sep_action": sep,
        "hls_action": hls,
        "sepomega_action": coordinated,
        "J_SEP": j_sep,
        "J_HLS": j_hls,
        "J_SEP_Omega": j_coord,
        "DeltaJ": j_hls - j_sep,
        "Delta_coord": j_hls - j_coord,
    }


def diagnostic_kappas(q: Quantities, horizon: float) -> tuple[float, ...]:
    thresholds = [0.0, kappa_star(q, horizon), horizon * q.delta_v]
    positive = sorted({float(x) for x in thresholds if x >= 0})
    points = set(positive)
    for left, right in zip(positive, positive[1:]):
        if right > left:
            points.add((left + right) / 2.0)
    if positive:
        points.add(positive[-1] + max(1.0, abs(positive[-1])))
        if positive[0] > 0:
            points.add(positive[0] / 2.0)
    return tuple(sorted(points))


def aggregate_cases(rows: pd.DataFrame) -> pd.DataFrame:
    required = {"seed", "c", "h", "kappa", "J_SEP", "J_HLS", "J_SEP_Omega"}
    if not required.issubset(rows.columns):
        raise ValueError(f"missing aggregation columns: {sorted(required - set(rows.columns))}")
    counts = rows.groupby(["seed", "c", "h", "kappa"]).size()
    if not (counts == 12).all():
        raise ValueError("each seed/c/h/kappa aggregate must contain exactly 12 cases")
    result = rows.groupby(["seed", "c", "h", "kappa"], as_index=False)[
        ["J_SEP", "J_HLS", "J_SEP_Omega"]
    ].mean()
    result["DeltaJ"] = result.J_HLS - result.J_SEP
    result["Delta_coord"] = result.J_HLS - result.J_SEP_Omega
    return result


def _merge_intervals(intervals: Iterable[tuple[float, float]]) -> list[tuple[float, float]]:
    ordered = sorted((float(a), float(b)) for a, b in intervals if b - a > TOLERANCE)
    merged: list[list[float]] = []
    for left, right in ordered:
        if not merged or left > merged[-1][1] + TOLERANCE:
            merged.append([left, right])
        else:
            merged[-1][1] = max(merged[-1][1], right)
    return [(a, b) for a, b in merged]


def intersect_intervals(
    left: Iterable[tuple[float, float]], right: Iterable[tuple[float, float]]
) -> list[tuple[float, float]]:
    intersections = []
    for a, b in left:
        for c, d in right:
            lo, hi = max(a, c), min(b, d)
            if hi - lo > TOLERANCE:
                intersections.append((lo, hi))
    return _merge_intervals(intersections)


def classify_positive_regions(
    cell_regions: Mapping[tuple[float, float], list[tuple[float, float]]],
    any_positive_regions: Iterable[tuple[float, float]],
) -> tuple[str, list[tuple[float, float]]]:
    expected = {(c, h) for c in COSTS for h in HORIZONS}
    if set(cell_regions) != expected:
        raise ValueError("classification requires all 20 frozen c x h cells")
    common: list[tuple[float, float]] = [(0.0, float("inf"))]
    for key in sorted(expected):
        common = intersect_intervals(common, cell_regions[key])
        if not common:
            break
    if common:
        return "POSITIVE", common
    if not _merge_intervals(any_positive_regions):
        return "NULL", []
    return "INCONCLUSIVE", []


def assert_finite(values: Iterable[float]) -> None:
    array = np.asarray(list(values), dtype=float)
    if not np.isfinite(array).all():
        raise ValueError("non-finite scientific value")


def confirmatory_surface(
    validation_scores: Mapping[tuple[str, int, int, str], Mapping[str, float]],
    test_scores: Mapping[tuple[str, int, int, str], Mapping[str, float]],
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Build the exact open-interval kappa surface and frozen classification."""
    seeds = tuple(range(5))
    n_values = (25, 50, 100)
    configs: dict[tuple[int, str, int, float, int], tuple[Quantities, Quantities]] = {}
    positive_stars = [0.0]
    for seed in seeds:
        for domain in DOMAINS:
            for n in n_values:
                for c in COSTS:
                    q_hat = quantities(
                        domain, c,
                        validation_scores[("F0", seed, n, domain)],
                        validation_scores[("D", seed, n, domain)],
                        validation_scores[("REP", seed, n, domain)],
                    )
                    q_test = quantities(
                        domain, c,
                        test_scores[("F0", seed, n, domain)],
                        test_scores[("D", seed, n, domain)],
                        test_scores[("REP", seed, n, domain)],
                    )
                    for h in HORIZONS:
                        configs[(seed, domain, n, c, h)] = q_hat, q_test
                        if kappa_star(q_hat, h) > 0:
                            positive_stars.append(kappa_star(q_hat, h))
    kmax = max(positive_stars)
    segment_rows: list[dict[str, object]] = []
    cell_regions: dict[tuple[float, float], list[tuple[float, float]]] = {}
    any_regions: list[tuple[float, float]] = []
    max_coord = 0.0
    for c in COSTS:
        for h in HORIZONS:
            boundaries = {0.0, kmax}
            for seed in seeds:
                for domain in DOMAINS:
                    for n in n_values:
                        q_hat, _ = configs[(seed, domain, n, c, h)]
                        for value in (kappa_star(q_hat, h), h * q_hat.delta_v):
                            if 0 < value < kmax:
                                boundaries.add(float(value))
            base_segments = list(zip(sorted(boundaries), sorted(boundaries)[1:]))
            split_segments: list[tuple[float, float]] = []
            for left, right in base_segments:
                if right - left <= TOLERANCE:
                    continue
                mid = (left + right) / 2.0
                roots = []
                for seed in seeds:
                    intercepts = []
                    slopes = []
                    for domain in DOMAINS:
                        for n in n_values:
                            q_hat, q_test = configs[(seed, domain, n, c, h)]
                            hls = choose_hls(q_hat, h, mid)
                            sep = choose_sep(q_hat, h, mid)
                            hls0 = realized_j(hls, q_test, h, 0.0)
                            sep0 = realized_j(sep, q_test, h, 0.0)
                            intercepts.append(hls0 - sep0)
                            slopes.append((-1.0 if hls == ACTION_DREP else 0.0) - (-1.0 if sep == ACTION_DREP else 0.0))
                    a, b = float(np.mean(intercepts)), float(np.mean(slopes))
                    if abs(b) > TOLERANCE:
                        root = -a / b
                        if left + TOLERANCE < root < right - TOLERANCE:
                            roots.append(root)
                points = [left, *sorted(set(roots)), right]
                split_segments.extend(zip(points, points[1:]))
            favorable: list[tuple[float, float]] = []
            for left, right in split_segments:
                mid = (left + right) / 2.0
                seed_deltas = []
                for seed in seeds:
                    case_rows = []
                    for domain in DOMAINS:
                        for n in n_values:
                            q_hat, q_test = configs[(seed, domain, n, c, h)]
                            result = policy_row(q_hat, q_test, h, mid)
                            max_coord = max(max_coord, abs(float(result["Delta_coord"])))
                            case_rows.append(result)
                    seed_deltas.append(float(np.mean([float(row["DeltaJ"]) for row in case_rows])))
                positive = sum(value > 0 for value in seed_deltas)
                mean = float(np.mean(seed_deltas))
                is_favorable = positive >= 4 and mean > 0
                if is_favorable:
                    favorable.append((left, right))
                if any(value > 0 for value in seed_deltas):
                    any_regions.append((left, right))
                segment_rows.append({
                    "c": c, "h": h, "kappa_left": left, "kappa_right": right,
                    "positive_seeds": positive, "mean_DeltaJ": mean,
                    "favorable_4of5": is_favorable,
                    **{f"DeltaJ_seed{seed}": seed_deltas[seed] for seed in seeds},
                })
            cell_regions[(c, h)] = _merge_intervals(favorable)
    label, common = classify_positive_regions(cell_regions, any_regions)
    return pd.DataFrame(segment_rows), {
        "classification": label,
        "K_max": kmax,
        "R_positive_all": common,
        "R_positive_by_cell": {f"c={c:g}|h={h}": regions for (c, h), regions in cell_regions.items()},
        "max_delta_coord": max_coord,
    }
