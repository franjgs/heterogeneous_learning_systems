"""Verify M0.1 linear and proportional response identities numerically."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hls.m0 import discount_factor_sum
from hls.m01 import (
    dV_ddelta_constant_ell,
    intervention_value_m01,
    linear_gain,
    operational_surplus,
    proportional_gain,
)


RESULTS = ROOT / "results" / "m01"
EPSILON = 1e-6


def central_difference(function, delta: float) -> float:
    """Use a symmetric difference only at points away from M0.1 kinks."""
    return (function(delta + EPSILON) - function(delta - EPSILON)) / (2 * EPSILON)


def sign(value: float, tolerance: float = 1e-10) -> int:
    if value > tolerance:
        return 1
    if value < -tolerance:
        return -1
    return 0


def main() -> None:
    """Verify P1 and P2 from the M0.1 computational-verification plan."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    a, c = 0.30, 0.15
    p, ell, K, H, gamma = 0.40, 0.70, 0.02, 3, 0.80
    b_values = (0.0, 0.5, 0.9, 1.0, 1.1, 1.5)
    deltas = np.linspace(c + 0.002, 0.90, 180)
    rows: list[dict[str, float | int | bool]] = []

    figure, axis = plt.subplots(figsize=(7.2, 4.8))
    for b in b_values:
        values = []
        for delta in deltas:
            gain = linear_gain(float(delta), a, b)
            h = operational_surplus(float(delta), c, gain)
            switchable = h > 0
            value = intervention_value_m01(float(delta), p, ell, gain, K, c, H, gamma)
            analytic = np.nan
            numeric = np.nan
            if switchable and delta - EPSILON > c and h > 5 * EPSILON:
                analytic = dV_ddelta_constant_ell(p, ell, b, H, gamma)
                numeric = central_difference(
                    lambda point: intervention_value_m01(
                        point, p, ell, linear_gain(point, a, b), K, c, H, gamma
                    ),
                    float(delta),
                )
            rows.append(
                {
                    "b": b,
                    "delta": float(delta),
                    "g": gain,
                    "h": h,
                    "V": value,
                    "dV_analytic": analytic,
                    "dV_numeric": numeric,
                    "sign_analytic": sign(float(analytic)) if not np.isnan(analytic) else np.nan,
                    "sign_numeric": sign(float(numeric)) if not np.isnan(numeric) else np.nan,
                    "switchable": switchable,
                }
            )
            values.append(value if switchable else np.nan)
        axis.plot(deltas, values, label=f"b={b:g}")

    axis.axvline(c, color="black", linestyle=":", linewidth=1, label="canonical boundary c")
    axis.set_xlabel("quality gap delta")
    axis.set_ylabel("intervention value V(delta)")
    axis.set_title("M0.1 linear response: switchable segments only")
    axis.legend(ncol=2, fontsize=8)
    figure.tight_layout()
    figure.savefig(RESULTS / "m01_linear_response.png", dpi=160)
    figure.savefig(RESULTS / "m01_linear_response.pdf")
    plt.close(figure)

    table = pd.DataFrame(rows)
    table.to_csv(RESULTS / "m01_linear_response.csv", index=False)
    verified = table.dropna(subset=["dV_analytic", "dV_numeric"]).copy()
    absolute_error = (verified["dV_analytic"] - verified["dV_numeric"]).abs()
    nonzero = verified[verified["dV_analytic"].abs() > 1e-10]
    relative_error = (nonzero["dV_analytic"] - nonzero["dV_numeric"]).abs() / nonzero[
        "dV_analytic"
    ].abs()

    print("M0.1 linear response verification")
    print(f"rows: {len(table)}; strictly switchable derivative checks: {len(verified)}")
    print(f"maximum absolute derivative error: {absolute_error.max():.3e}")
    print(f"maximum relative derivative error (nonzero analytic derivatives): {relative_error.max():.3e}")
    for b in b_values:
        expected = sign(b - 1.0)
        observed = set(verified.loc[verified["b"] == b, "sign_numeric"].astype(int))
        print(f"b={b:g}: expected sign {expected:+d}; observed {sorted(observed)}")

    rho_rows = []
    for rho in (0.0, 0.25, 0.5, 0.9, 1.0):
        delta_switch = np.inf if rho == 1.0 else c / (1 - rho)
        if rho == 0.0:
            # For rho=0, delta_switch=c: no point can be both canonical
            # (delta>c) and strictly switchable (delta<delta_switch).
            rho_rows.append((rho, np.nan, np.nan, np.nan))
            continue
        delta = 0.20 if rho == 1.0 else c + (delta_switch - c) / 2
        gain = proportional_gain(delta, rho)
        h = operational_surplus(delta, c, gain)
        analytic = dV_ddelta_constant_ell(p, ell, rho, H, gamma)
        numeric = central_difference(
            lambda point: intervention_value_m01(
                point, p, ell, proportional_gain(point, rho), K, c, H, gamma
            ),
            delta,
        )
        rho_rows.append((rho, h, analytic, numeric))
    print("proportional response checks (rho, h, analytic, numeric):")
    for row in rho_rows:
        if np.isnan(row[1]):
            print(f"  rho={row[0]:.2f}: no strictly switchable canonical interval")
        else:
            print("  " + ", ".join(f"{value:.8f}" for value in row))


if __name__ == "__main__":
    main()
