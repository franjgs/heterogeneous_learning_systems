"""Microverify the explicitly documented CR0--CR4 minimal theory.

This is a diagnostic calculation under the model assumptions, not an HLS
benchmark or evidence about real learning systems.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hls.competence_evolution_minimal import (
    beta_critical,
    complementary_switch_gain,
    numeric_rebalancing_argmin,
    rebalancing_solution,
    rk4_specialization,
    specialization_eigenvalues,
    specialization_jacobian_at_symmetric,
    symmetric_equilibrium,
)


RESULTS = ROOT / "results" / "microverification"


def symbolic_jacobian_audit() -> str:
    """Derive the 4x4 symmetric Jacobian and its critical eigenvalue in SymPy."""
    eta, depreciation, beta = sp.symbols("eta delta beta", positive=True)
    a1, b2, a2, b1 = sp.symbols("a1 b2 a2 b1")
    state = sp.Matrix([a1, b2, a2, b1])
    routing = 1 / (1 + sp.exp(-beta * (a1 + b2 - a2 - b1)))
    rhs = sp.Matrix(
        [
            eta * routing * (1 - a1) - depreciation * a1,
            eta * routing * (1 - b2) - depreciation * b2,
            eta * (1 - routing) * (1 - a2) - depreciation * a2,
            eta * (1 - routing) * (1 - b1) - depreciation * b1,
        ]
    )
    c_star = eta / (eta + 2 * depreciation)
    jacobian = sp.simplify(rhs.jacobian(state).subs({a1: c_star, b2: c_star, a2: c_star, b1: c_star}))
    characteristic = sp.factor(jacobian.charpoly().as_expr())
    critical = sp.solve(sp.Eq(-eta / 2 - depreciation + 2 * eta * depreciation * beta / (eta + 2 * depreciation), 0), beta)[0]
    return "\n".join(
        [
            "SymPy audit of the symmetric 2x2 equilibrium",
            f"c* = {c_star}",
            "Jacobian:",
            str(jacobian),
            f"characteristic polynomial = {characteristic}",
            f"critical beta = {sp.factor(critical)}",
            "Eigenvalues: -(eta+2 delta)/2 (multiplicity 3) and",
            "-(eta+2 delta)/2 + 2 eta delta beta/(eta+2 delta).",
        ]
    )


def verify_complementarity() -> pd.DataFrame:
    delta_0 = 1.0
    rows = []
    for label, x, y in (("A-only", 0.6, 0.0), ("B-only", 0.0, 0.6), ("joint", 0.6, 0.6)):
        rows.append({"case": label, "delta_0": delta_0, "x": x, "y": y, "G": complementary_switch_gain(delta_0, x, y)})
    return pd.DataFrame(rows)


def verify_specialization() -> pd.DataFrame:
    eta, depreciation = 0.4, 0.2
    c_star = symmetric_equilibrium(eta, depreciation)
    beta_c = beta_critical(eta, depreciation)
    direction = np.array([1.0, 1.0, -1.0, -1.0])
    rows = []
    trajectories: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for beta_label, beta in (("below", 0.5 * beta_c), ("critical", beta_c), ("above", 1.5 * beta_c)):
        for sign in (-1.0, 1.0):
            initial = np.full(4, c_star) + sign * 0.05 * direction
            trajectory = rk4_specialization(initial, eta, depreciation, beta, dt=0.01, steps=12000)
            final = trajectory[-1]
            final_gap = final[0] + final[1] - final[2] - final[3]
            eigenvalues = specialization_eigenvalues(eta, depreciation, beta)
            rows.append(
                {
                    "beta_case": beta_label,
                    "beta": beta,
                    "perturbation_sign": int(sign),
                    "c_star": c_star,
                    "lambda_max": float(eigenvalues[-1]),
                    "final_A1": final[0],
                    "final_B2": final[1],
                    "final_A2": final[2],
                    "final_B1": final[3],
                    "final_gap": final_gap,
                    "distance_from_symmetric": float(np.linalg.norm(final - c_star)),
                }
            )
            trajectories[f"{beta_label}, perturbation {int(sign):+d}"] = (
                np.arange(len(trajectory)) * 0.01,
                trajectory @ direction,
            )

    figure, axis = plt.subplots(figsize=(7.2, 4.5))
    for label, (time, gap) in trajectories.items():
        axis.plot(time, gap, label=label)
    axis.axhline(0.0, color="black", linewidth=0.8)
    axis.set_xlabel("time")
    axis.set_ylabel("Delta = A1 + B2 - A2 - B1")
    axis.set_title("2x2 learning-by-doing: symmetric perturbations")
    axis.legend(ncol=2, fontsize=8)
    figure.tight_layout()
    figure.savefig(RESULTS / "specialization_dynamics.png", dpi=160)
    figure.savefig(RESULTS / "specialization_dynamics.pdf")
    plt.close(figure)
    return pd.DataFrame(rows)


def verify_rebalancing() -> pd.DataFrame:
    cases = [
        ("train", 1.0, 0.5, 1.0, 1.0),
        ("boundary_train_mixed", 1.0, 1.0, 1.0, 1.0),
        ("mixed", 1.0, 1.5, 1.0, 1.0),
        ("boundary_mixed_route", 1.0, 2.0, 1.0, 1.0),
        ("route", 1.0, 2.5, 1.0, 1.0),
        ("small_d0", 1e-6, 1.5, 1.0, 1.0),
        ("fast_route", 1.0, 1.5, 100.0, 1.0),
        ("slow_route", 1.0, 1.5, 0.05, 1.0),
        ("cheap_train", 1.0, 0.01, 1.0, 1.0),
        ("costly_train", 1.0, 10.0, 1.0, 1.0),
        ("small_gain", 1.0, 1.5, 1.0, 0.01),
        ("large_gain", 1.0, 1.5, 1.0, 10.0),
    ]
    rows = []
    for label, d_0, a, v, g in cases:
        x_star, y_star, regime, q_star, h_star = rebalancing_solution(d_0, a, v, g)
        y_numeric, q_numeric = numeric_rebalancing_argmin(d_0, a, v, g, resolution=20001)
        q_train = a * d_0
        q_route = d_0**2 / (2.0 * v) + g * d_0 / v
        rows.append(
            {
                "case": label,
                "d_0": d_0,
                "a": a,
                "v": v,
                "g": g,
                "regime": regime,
                "x_star": x_star,
                "y_star": y_star,
                "Q_star": q_star,
                "H_star": h_star,
                "y_numeric": y_numeric,
                "Q_numeric": q_numeric,
                "argmin_abs_error": abs(y_star - y_numeric),
                "Q_abs_error": abs(q_star - q_numeric),
                "Q_train": q_train,
                "Q_route": q_route,
                "mixed_strictly_better_than_both": regime == "MIXED" and q_star < min(q_train, q_route),
            }
        )

    d_0, v, g = 1.0, 1.0, 1.0
    figure, axis = plt.subplots(figsize=(7.2, 4.5))
    grid = np.linspace(0, d_0, 400)
    for a in (0.5, 1.0, 1.5, 2.0, 2.5):
        values = a * (d_0 - grid) + grid**2 / (2 * v) + g * grid / v
        _, y_star, regime, _, _ = rebalancing_solution(d_0, a, v, g)
        axis.plot(grid, values, label=f"a={a:g} ({regime})")
        axis.scatter([y_star], [a * (d_0-y_star) + y_star**2/(2*v) + g*y_star/v], s=15)
    axis.set_xlabel("routing-induced displacement y")
    axis.set_ylabel("effective cost Q(y)")
    axis.set_title("Two-actuator rebalancing: convex effective cost")
    axis.legend(fontsize=8)
    figure.tight_layout()
    figure.savefig(RESULTS / "rebalancing_costs.png", dpi=160)
    figure.savefig(RESULTS / "rebalancing_costs.pdf")
    plt.close(figure)
    return pd.DataFrame(rows)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "symbolic_jacobian_audit.txt").write_text(symbolic_jacobian_audit() + "\n", encoding="utf-8")
    complementarity = verify_complementarity()
    specialization = verify_specialization()
    rebalancing = verify_rebalancing()
    complementarity.to_csv(RESULTS / "complementarity.csv", index=False)
    specialization.to_csv(RESULTS / "specialization.csv", index=False)
    rebalancing.to_csv(RESULTS / "rebalancing.csv", index=False)

    summary = {
        "epistemic_scope": "numerical checks of explicitly stated minimal-model identities only",
        "complementarity_joint_gain": float(complementarity.loc[complementarity["case"] == "joint", "G"].iloc[0]),
        "beta_critical_eta_0.4_delta_0.2": beta_critical(0.4, 0.2),
        "specialization_max_abs_gap_below": float(specialization.loc[specialization["beta_case"] == "below", "final_gap"].abs().max()),
        "specialization_min_abs_gap_above": float(specialization.loc[specialization["beta_case"] == "above", "final_gap"].abs().min()),
        "rebalancing_max_argmin_abs_error": float(rebalancing["argmin_abs_error"].max()),
        "rebalancing_max_Q_abs_error": float(rebalancing["Q_abs_error"].max()),
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
