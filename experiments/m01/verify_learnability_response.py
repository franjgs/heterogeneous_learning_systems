"""Verify the M0.1 learnability-dependent derivative and its sign boundary."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hls.m01 import (
    dV_ddelta_variable_ell,
    intervention_value_m01,
    linear_gain,
    linear_learnability,
    operational_surplus,
)


RESULTS = ROOT / "results" / "m01"
EPSILON = 1e-6


def central_difference(function, delta: float) -> float:
    return (function(delta + EPSILON) - function(delta - EPSILON)) / (2 * EPSILON)


def learnability_boundary(a: float, b: float, c: float, delta: float, ell0: float) -> float:
    """Return the exact s boundary for ell(delta)=ell0+s delta.

    Expanding ``s h + (ell0+s delta)(b-1)=0`` gives
    ``s[a+c+2(b-1)delta] + ell0(b-1)=0``.  The extra delta term comes from
    differentiating the learnability factor, so ell cannot be treated as fixed.
    """
    denominator = a + c + 2 * (b - 1) * delta
    if np.isclose(denominator, 0.0):
        raise ValueError("The selected parameters have no finite s boundary.")
    return -ell0 * (b - 1) / denominator


def sign(value: float, tolerance: float = 1e-10) -> int:
    return 1 if value > tolerance else -1 if value < -tolerance else 0


def main() -> None:
    """Verify P3 and produce a domain-masked (b,s) diagnostic map."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    a, c, ell0, p, K, H, gamma = 0.30, 0.15, 0.30, 0.40, 0.02, 3, 0.80
    pairs = ((0.5, 0.30), (0.9, 0.30), (1.1, 0.30))
    rows: list[dict[str, float | int]] = []
    for b, delta in pairs:
        s_star = learnability_boundary(a, b, c, delta, ell0)
        for label, s in (("below", s_star - 0.05), ("boundary", s_star), ("above", s_star + 0.05)):
            gain = linear_gain(delta, a, b)
            ell = linear_learnability(delta, ell0, s)
            h = operational_surplus(delta, c, gain)
            if not 0 < ell < 1 or h <= 0 or delta <= c:
                raise RuntimeError("Verification parameters left the intended strict domain.")
            analytic = dV_ddelta_variable_ell(delta, p, ell, s, gain, b, c, H, gamma)
            numeric = central_difference(
                lambda point: intervention_value_m01(
                    point,
                    p,
                    linear_learnability(point, ell0, s),
                    linear_gain(point, a, b),
                    K,
                    c,
                    H,
                    gamma,
                ),
                delta,
            )
            rows.append(
                {
                    "b": b,
                    "delta": delta,
                    "case": label,
                    "s": s,
                    "s_star": s_star,
                    "ell": ell,
                    "h": h,
                    "dV_analytic": analytic,
                    "dV_numeric": numeric,
                    "sign_analytic": sign(analytic),
                    "sign_numeric": sign(numeric),
                }
            )
    response = pd.DataFrame(rows)

    map_rows: list[dict[str, float | int | bool]] = []
    delta = 0.30
    for b in np.linspace(-1.0, 2.0, 121):
        for s in np.linspace(-1.2, 2.6, 121):
            gain = linear_gain(delta, a, float(b))
            ell = linear_learnability(delta, ell0, float(s))
            h = operational_surplus(delta, c, gain)
            valid = delta > c and h > 0 and 0 < ell < 1
            derivative = np.nan
            classification = np.nan
            if valid:
                derivative = dV_ddelta_variable_ell(
                    delta, p, ell, float(s), gain, float(b), c, H, gamma
                )
                classification = sign(float(derivative))
            map_rows.append(
                {
                    "delta": delta,
                    "b": float(b),
                    "s": float(s),
                    "ell": ell,
                    "h": h,
                    "valid": valid,
                    "dV_analytic": derivative,
                    "classification": classification,
                }
            )
    mechanism = pd.DataFrame(map_rows)
    response.to_csv(RESULTS / "m01_learnability_response.csv", index=False)
    mechanism.to_csv(RESULTS / "m01_mechanism_map.csv", index=False)

    pivot = mechanism.pivot(index="s", columns="b", values="classification")
    figure, axis = plt.subplots(figsize=(7.2, 5.0))
    colormap = plt.get_cmap("coolwarm").copy()
    colormap.set_bad("#d9d9d9")
    image = axis.imshow(
        pivot.to_numpy(),
        origin="lower",
        aspect="auto",
        extent=[pivot.columns.min(), pivot.columns.max(), pivot.index.min(), pivot.index.max()],
        vmin=-1,
        vmax=1,
        cmap=colormap,
    )
    figure.colorbar(image, ax=axis, label="sign of V'(delta); invalid is grey")
    axis.set_xlabel("linear gain slope b")
    axis.set_ylabel("learnability slope s")
    axis.set_title("M0.1 mechanism sign map at delta=0.30")
    figure.tight_layout()
    figure.savefig(RESULTS / "m01_mechanism_map.png", dpi=160)
    figure.savefig(RESULTS / "m01_mechanism_map.pdf")
    plt.close(figure)

    absolute_error = (response["dV_analytic"] - response["dV_numeric"]).abs()
    nonzero = response[response["dV_analytic"].abs() > 1e-10]
    relative_error = (nonzero["dV_analytic"] - nonzero["dV_numeric"]).abs() / nonzero[
        "dV_analytic"
    ].abs()
    print("M0.1 learnability-response verification")
    print(f"maximum absolute derivative error: {absolute_error.max():.3e}")
    print(f"maximum relative derivative error (nonzero analytic derivatives): {relative_error.max():.3e}")
    print(response.to_string(index=False))
    print(f"mechanism-map valid points: {int(mechanism['valid'].sum())} / {len(mechanism)}")


if __name__ == "__main__":
    main()
