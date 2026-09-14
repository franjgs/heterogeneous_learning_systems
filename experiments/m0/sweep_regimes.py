"""Sweep the equal-parameter M0 regime and write diagnostic result artifacts.

With equal p, ell, K, and g, frequency-gap ranking increases in delta whereas
value is proportional to [g + c - delta]_+. Thus, inside c < delta < c + g,
the two rankings have opposite strict monotonicity away from ties. This is an
exact M0 structural property caused by fixed gains and threshold switching, not
a general HLS claim.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

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
    compare_scores,
    strict_rank_reversal,
    validate_canonical_m0_regions,
)


CANONICAL_EPSILON = 1e-6


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sweep equal-parameter M0 regimes.")
    parser.add_argument("--resolution", type=int, default=101)
    parser.add_argument("--delta-min", type=float, default=None)
    parser.add_argument("--delta-max", type=float, default=0.5)
    parser.add_argument("--cost-advantage", type=float, default=0.15)
    parser.add_argument("--gain", type=float, default=0.18)
    parser.add_argument("--p", type=float, default=0.5)
    parser.add_argument("--learnability", type=float, default=1.0)
    parser.add_argument("--training-cost", type=float, default=0.0)
    parser.add_argument("--horizon", type=int, default=1)
    parser.add_argument("--gamma", type=float, default=1.0)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "m0")
    return parser.parse_args()


def make_region(delta: float, args: argparse.Namespace) -> RegionM0:
    return RegionM0(
        p=args.p,
        q_cheap=0.0,
        q_expensive=delta,
        learnability=args.learnability,
        gain=args.gain,
        training_cost=args.training_cost,
    )


def resolved_delta_min(args: argparse.Namespace) -> float:
    """Return an explicitly strict canonical lower boundary or fail loudly."""
    requested = args.cost_advantage + CANONICAL_EPSILON if args.delta_min is None else args.delta_min
    if requested <= args.cost_advantage:
        raise ValueError(
            "Canonical M0 requires delta_min > cost_advantage so every grid point "
            "satisfies m_z > 0; use a value above c."
        )
    return requested


def regime(delta: float, cost_advantage: float, gain: float) -> str:
    """Classify a valid canonical point by its M0 switching condition."""
    return "switchable" if delta < cost_advantage + gain else "non_switchable"


def relation_label(relation: int) -> str:
    return {1: "region_1_higher", -1: "region_2_higher", 0: "tie"}[relation]


def build_dataframe(args: argparse.Namespace) -> pd.DataFrame:
    if args.resolution < 2:
        raise ValueError("resolution must be at least 2.")
    if not np.isclose(2 * args.p, 1.0):
        raise ValueError("The equal-parameter two-region sweep requires p1 = p2 = 0.5.")
    if args.cost_advantage <= 0:
        raise ValueError("cost_advantage must be positive for canonical M0 experiments.")
    delta_min = resolved_delta_min(args)
    if args.delta_max <= delta_min:
        raise ValueError("delta_max must be greater than canonical delta_min.")

    config = M0Config(
        k_cheap=0.0,
        k_expensive=1.0,
        lambda_cost=args.cost_advantage,
        H=args.horizon,
        gamma=args.gamma,
    )
    deltas = np.linspace(delta_min, args.delta_max, args.resolution)
    rows: list[dict[str, float | int]] = []
    for delta_1 in deltas:
        for delta_2 in deltas:
            regions = [make_region(float(delta_1), args), make_region(float(delta_2), args)]
            validate_canonical_m0_regions(regions, config)
            choice_frequency_gap = rank_interventions_by_frequency_gap(regions) + 1
            choice_value = rank_interventions_by_value(regions, config) + 1
            score_1 = region_frequency_gap_score(regions[0])
            score_2 = region_frequency_gap_score(regions[1])
            value_1 = region_intervention_value(regions[0], config)
            value_2 = region_intervention_value(regions[1], config)
            score_relation = compare_scores(score_1, score_2)
            value_relation = compare_scores(value_1, value_2)
            regime_1 = regime(float(delta_1), config.cost_advantage, args.gain)
            regime_2 = regime(float(delta_2), config.cost_advantage, args.gain)
            rows.append(
                {
                    "delta_1": float(delta_1),
                    "delta_2": float(delta_2),
                    "margin_1": region_margin(regions[0], config),
                    "margin_2": region_margin(regions[1], config),
                    "S_1": score_1,
                    "S_2": score_2,
                    "V_1": value_1,
                    "V_2": value_2,
                    "choice_frequency_gap": choice_frequency_gap,
                    "choice_value": choice_value,
                    "frequency_gap_relation": relation_label(score_relation),
                    "value_relation": relation_label(value_relation),
                    "tie_frequency_gap": int(score_relation == 0),
                    "tie_value": int(value_relation == 0),
                    "strict_agreement": int(score_relation != 0 and score_relation == value_relation),
                    "strict_rank_reversal": int(strict_rank_reversal(regions, config)),
                    "rank_reversal": int(strict_rank_reversal(regions, config)),
                    "selection_agreement": int(choice_frequency_gap == choice_value),
                    "regime_1": regime_1,
                    "regime_2": regime_2,
                    "regime_pair": (
                        "both_switchable"
                        if regime_1 == regime_2 == "switchable"
                        else "both_non_switchable"
                        if regime_1 == regime_2 == "non_switchable"
                        else "one_switchable"
                    ),
                    "regret": intervention_regret(regions, config),
                    "cost_advantage": config.cost_advantage,
                    "gain": args.gain,
                    "p": args.p,
                    "learnability": args.learnability,
                    "training_cost": args.training_cost,
                    "H": args.horizon,
                    "gamma": args.gamma,
                }
            )
    return pd.DataFrame(rows)


def save_figures(frame: pd.DataFrame, args: argparse.Namespace, delta_min: float) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.colors import BoundaryNorm, ListedColormap

    deltas = np.sort(frame["delta_1"].unique())
    phase_codes = np.where(
        frame["strict_rank_reversal"].to_numpy() == 1,
        1,
        np.where(
            (frame["tie_frequency_gap"].to_numpy() == 1) & (frame["tie_value"].to_numpy() == 1),
            4,
            np.where(frame["tie_frequency_gap"].to_numpy() == 1, 2, np.where(frame["tie_value"].to_numpy() == 1, 3, 0)),
        ),
    )
    phase_frame = frame[["delta_1", "delta_2"]].copy()
    phase_frame["phase_code"] = phase_codes
    phase = phase_frame.pivot(index="delta_2", columns="delta_1", values="phase_code").loc[deltas, deltas]
    regret = frame.pivot(index="delta_2", columns="delta_1", values="regret").loc[deltas, deltas]
    extent = [delta_min, deltas.max(), delta_min, deltas.max()]

    phase_colors = ListedColormap(["#4daf4a", "#e41a1c", "#377eb8", "#984ea3", "#999999"])
    phase_norm = BoundaryNorm(np.arange(-0.5, 5.5, 1), phase_colors.N)
    specifications = [
        (phase.to_numpy(), "M0 strict rank reversal and ties", "m0_rank_reversal_phase_map", phase_colors, phase_norm),
        (regret.to_numpy(), "M0 frequency-gap regret", "m0_regret_map", "magma", None),
    ]
    for values, title, stem, cmap, norm in specifications:
        figure, axis = plt.subplots(figsize=(6, 5))
        image = axis.imshow(
            values,
            origin="lower",
            extent=extent,
            aspect="equal",
            cmap=cmap,
            norm=norm,
            interpolation="nearest",
        )
        for boundary in (args.cost_advantage + args.gain,):
            axis.axvline(boundary, color="white", linestyle="--", linewidth=1)
            axis.axhline(boundary, color="white", linestyle="--", linewidth=1)
        axis.set_xlabel("delta_1")
        axis.set_ylabel("delta_2")
        axis.set_title(title)
        colorbar = figure.colorbar(image, ax=axis)
        if stem == "m0_rank_reversal_phase_map":
            colorbar.set_ticks([0, 1, 2, 3, 4])
            colorbar.set_ticklabels(
                ["strict agreement", "strict reversal", "frequency tie", "value tie", "both ties"]
            )
        else:
            colorbar.set_label("Regret_FG")
        figure.tight_layout()
        figure.savefig(args.output_dir / f"{stem}.png", dpi=180)
        figure.savefig(args.output_dir / f"{stem}.pdf")
        plt.close(figure)


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    delta_min = resolved_delta_min(args)
    frame = build_dataframe(args)
    frame.to_csv(args.output_dir / "m0_regime_sweep.csv", index=False)
    metadata = {
        "resolution": args.resolution,
        "delta_domain": [delta_min, args.delta_max],
        "canonical_assumption": "delta_z > c, equivalently m_z > 0",
        "canonical_epsilon": CANONICAL_EPSILON,
        "equal_parameters": {"p": args.p, "learnability": args.learnability, "training_cost": args.training_cost, "gain": args.gain},
        "cost_advantage": args.cost_advantage,
        "H": args.horizon,
        "gamma": args.gamma,
        "canonical_core_band": [args.cost_advantage, args.cost_advantage + args.gain],
        "tie_rule": "lowest region index",
    }
    (args.output_dir / "m0_regime_sweep_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    save_figures(frame, args, delta_min)

    maximum = frame.loc[frame["regret"].idxmax()]
    print(f"wrote {len(frame)} grid points to {args.output_dir / 'm0_regime_sweep.csv'}")
    print(f"strict rank-reversal cells: {int(frame['strict_rank_reversal'].sum())}")
    print(
        "maximum regret: "
        f"{maximum['regret']:.6f} at delta_1={maximum['delta_1']:.3f}, "
        f"delta_2={maximum['delta_2']:.3f}"
    )


if __name__ == "__main__":
    main()
