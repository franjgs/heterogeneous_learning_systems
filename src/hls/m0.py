"""Pure functions implementing the equations in ``docs/models/model_M0.md``.

M0 intentionally implements only two-tier deterministic routing and independent,
region-local interventions. It is not an implementation of M1 or a general HLS
simulator. All ranking functions break ties by the lowest region index, making
their output deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Sequence


_PROBABILITY_TOLERANCE = 1e-9


def _require_nonnegative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative; received {value}.")


def operational_utility(q: float, k: float, lambda_cost: float) -> float:
    """Return ``r_iz = q_iz - lambda k_i`` from M0."""
    _require_nonnegative("execution cost", k)
    _require_nonnegative("lambda_cost", lambda_cost)
    return q - lambda_cost * k


def quality_gap(q_expensive: float, q_cheap: float) -> float:
    """Return ``delta_z = q_Ez - q_Cz``."""
    return q_expensive - q_cheap


def routing_margin(delta: float, cost_advantage: float) -> float:
    """Return ``m_z = delta_z - c``."""
    _require_nonnegative("cost_advantage", cost_advantage)
    return delta - cost_advantage


def discount_factor_sum(H: int, gamma: float) -> float:
    """Return ``A_H = sum_{t=1}^H gamma^(t-1)``.

    The explicit ``gamma == 1`` branch implements the M0 special case exactly.
    """
    if isinstance(H, bool) or not isinstance(H, int) or H <= 0:
        raise ValueError(f"H must be a positive integer; received {H!r}.")
    if not 0 <= gamma <= 1:
        raise ValueError(f"gamma must lie in [0, 1]; received {gamma}.")
    if gamma == 1:
        return float(H)
    return (1 - gamma**H) / (1 - gamma)


def frequency_gap_score(p: float, delta: float) -> float:
    """Return the RouteNLP-like M0 score ``S_z = p_z delta_z``."""
    _require_nonnegative("p", p)
    return p * delta


def successful_operational_gain(p: float, g: float, margin: float) -> float:
    """Return ``Delta R_z = p_z [g_z - m_z]_+`` after successful learning."""
    _require_nonnegative("p", p)
    _require_nonnegative("g", g)
    return p * max(g - margin, 0.0)


def expected_intervention_value(
    p: float,
    ell: float,
    g: float,
    margin: float,
    K: float,
    H: int,
    gamma: float,
) -> float:
    """Return ``V_z = -K_z + A_H p_z ell_z [g_z - m_z]_+`` from M0."""
    _require_nonnegative("p", p)
    if not 0 <= ell <= 1:
        raise ValueError(f"ell must lie in [0, 1]; received {ell}.")
    _require_nonnegative("g", g)
    _require_nonnegative("K", K)
    return -K + discount_factor_sum(H, gamma) * ell * successful_operational_gain(p, g, margin)


@dataclass(frozen=True)
class RegionM0:
    """Parameters for one M0 task region and its intervention on the cheap model."""

    p: float
    q_cheap: float
    q_expensive: float
    learnability: float
    gain: float
    training_cost: float

    def __post_init__(self) -> None:
        _require_nonnegative("p", self.p)
        if not 0 <= self.learnability <= 1:
            raise ValueError("learnability must lie in [0, 1].")
        _require_nonnegative("gain", self.gain)
        _require_nonnegative("training_cost", self.training_cost)


@dataclass(frozen=True)
class M0Config:
    """System-level M0 parameters shared by all regions."""

    k_cheap: float
    k_expensive: float
    lambda_cost: float
    H: int
    gamma: float

    def __post_init__(self) -> None:
        _require_nonnegative("k_cheap", self.k_cheap)
        if self.k_expensive <= self.k_cheap:
            raise ValueError("k_expensive must be strictly greater than k_cheap in canonical M0.")
        _require_nonnegative("lambda_cost", self.lambda_cost)
        discount_factor_sum(self.H, self.gamma)

    @property
    def cost_advantage(self) -> float:
        """Return ``c = lambda (k_E - k_C)``."""
        return self.lambda_cost * (self.k_expensive - self.k_cheap)


def validate_system(regions: Sequence[RegionM0], config: M0Config) -> None:
    """Validate a probability-normalized M0 system.

    M0 is documented for two regions. Ranking functions accept a sequence to
    keep their mechanics transparent, but experiments and tests use two.
    """
    del config  # Type validation occurs when M0Config is constructed.
    _validate_probability_distribution(regions)


def _validate_probability_distribution(regions: Sequence[RegionM0]) -> None:
    """Validate nonempty regions whose probabilities sum to one."""
    if len(regions) == 0:
        raise ValueError("At least one region is required.")
    total_probability = sum(region.p for region in regions)
    if not isclose(total_probability, 1.0, abs_tol=_PROBABILITY_TOLERANCE):
        raise ValueError(
            "Region probabilities must sum to approximately 1; "
            f"received {total_probability}."
        )


def validate_canonical_m0_regions(regions: Sequence[RegionM0], config: M0Config) -> None:
    """Require the canonical M0 regime in which the expensive model routes first.

    The documented M0 gain equation is used only where ``m_z > 0``. Regions
    where the cheap model already wins are intentionally outside this laboratory.
    """
    validate_system(regions, config)
    invalid = [index + 1 for index, region in enumerate(regions) if region_margin(region, config) <= 0]
    if invalid:
        raise ValueError(
            "Canonical M0 requires m_z > 0 (equivalently delta_z > c) for every "
            f"region; invalid region indices: {invalid}."
        )


def region_delta(region: RegionM0) -> float:
    """Return the region's quality gap ``q_Ez - q_Cz``."""
    return quality_gap(region.q_expensive, region.q_cheap)


def region_margin(region: RegionM0, config: M0Config) -> float:
    """Return the cost-adjusted routing margin for one region."""
    return routing_margin(region_delta(region), config.cost_advantage)


def region_frequency_gap_score(region: RegionM0) -> float:
    """Return the M0 frequency-gap score for one region."""
    return frequency_gap_score(region.p, region_delta(region))


def region_intervention_value(region: RegionM0, config: M0Config) -> float:
    """Return the M0 expected net intervention value for one region."""
    return expected_intervention_value(
        p=region.p,
        ell=region.learnability,
        g=region.gain,
        margin=region_margin(region, config),
        K=region.training_cost,
        H=config.H,
        gamma=config.gamma,
    )


def _argmax_lowest_index(values: Sequence[float]) -> int:
    """Return the first maximum index, the documented deterministic tie rule."""
    if not values:
        raise ValueError("Cannot rank an empty sequence.")
    return max(range(len(values)), key=lambda index: values[index])


def compare_scores(left: float, right: float, tolerance: float = 1e-12) -> int:
    """Compare scores with an explicit tolerance: -1, 0 (tie), or 1."""
    if isclose(left, right, abs_tol=tolerance):
        return 0
    return 1 if left > right else -1


def strict_rank_reversal(regions: Sequence[RegionM0], config: M0Config) -> bool:
    """Return whether two regions have strictly opposite score and value order.

    Ties in either score are not rank reversals. This predicate is deliberately
    separate from deterministic selection, whose ties choose the lowest index.
    """
    validate_canonical_m0_regions(regions, config)
    if len(regions) != 2:
        raise ValueError("Strict rank reversal is defined here for exactly two regions.")
    score_relation = compare_scores(
        region_frequency_gap_score(regions[0]), region_frequency_gap_score(regions[1])
    )
    value_relation = compare_scores(
        region_intervention_value(regions[0], config),
        region_intervention_value(regions[1], config),
    )
    return score_relation != 0 and value_relation != 0 and score_relation != value_relation


def rank_interventions_by_frequency_gap(regions: Sequence[RegionM0]) -> int:
    """Return the selected region index under ``S_z = p_z delta_z``.

    Equal scores select the lowest index.
    """
    _validate_probability_distribution(regions)
    return _argmax_lowest_index([region_frequency_gap_score(region) for region in regions])


def rank_interventions_by_value(regions: Sequence[RegionM0], config: M0Config) -> int:
    """Return the selected region index under expected M0 intervention value.

    Equal values select the lowest index.
    """
    validate_system(regions, config)
    return _argmax_lowest_index([region_intervention_value(region, config) for region in regions])


def intervention_regret(regions: Sequence[RegionM0], config: M0Config) -> float:
    """Return ``max_z V_z - V_{z_R}`` for frequency-gap selection."""
    validate_system(regions, config)
    values = [region_intervention_value(region, config) for region in regions]
    selected_index = rank_interventions_by_frequency_gap(regions)
    return max(values) - values[selected_index]
