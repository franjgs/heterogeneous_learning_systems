"""Reproduce the numerical rank-reversal example in docs/models/model_M0.md."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hls.m0 import (  # noqa: E402
    M0Config,
    RegionM0,
    intervention_regret,
    rank_interventions_by_frequency_gap,
    rank_interventions_by_value,
    region_delta,
    region_frequency_gap_score,
    region_intervention_value,
    region_margin,
)


def main() -> None:
    """Print M0's documented example without hard-coding calculated results."""
    config = M0Config(k_cheap=0.0, k_expensive=1.0, lambda_cost=0.15, H=1, gamma=1.0)
    regions = [
        RegionM0(0.5, 0.0, 0.30, 1.0, 0.18, 0.0),
        RegionM0(0.5, 0.0, 0.20, 1.0, 0.18, 0.0),
    ]

    print("region  p      delta  margin  gain   frequency_gap_score  expected_intervention_value")
    for index, region in enumerate(regions, start=1):
        print(
            f"{index:<7d} {region.p:<6.3f} {region_delta(region):<6.3f} "
            f"{region_margin(region, config):<7.3f} {region.gain:<6.3f} "
            f"{region_frequency_gap_score(region):<20.3f} "
            f"{region_intervention_value(region, config):.3f}"
        )

    frequency_choice = rank_interventions_by_frequency_gap(regions) + 1
    value_choice = rank_interventions_by_value(regions, config) + 1
    regret = intervention_regret(regions, config)
    print(f"\nfrequency-gap choice: region {frequency_choice}")
    print(f"value-optimal choice: region {value_choice}")
    print(f"regret: {regret:.3f}")


if __name__ == "__main__":
    main()
