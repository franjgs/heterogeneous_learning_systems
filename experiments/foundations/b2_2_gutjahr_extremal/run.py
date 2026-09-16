import itertools
import json
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
RESULT_DIR = (
    ROOT / "results" / "foundations" / "b2_2_gutjahr_extremal"
)
write_result_bundle = runpy.run_path(
    str(ROOT / "experiments" / "foundations" / "_provenance.py")
)["write_result_bundle"]


def phi(z):
    """Logistic efficiency function."""
    z = np.asarray(z, dtype=float)
    return 1.0 / (1.0 + np.exp(-z))


def phi_second_derivative(z):
    """
    phi''(z) = phi(z)(1-phi(z))(1-2phi(z)).

    Hence logistic phi is strictly convex for z < 0.
    """
    p = phi(z)
    return p * (1.0 - p) * (1.0 - 2.0 * p)


def evaluate_policy(policy, z_initial, beta, eta, weights):
    """
    Gutjahr dynamic portfolio objective.

    policy[t, i] = x_it

    z_it = z_i1 - beta_i (t-1)
           + eta_i sum_{s<t} x_is

    objective = sum_t sum_i w_i x_it phi(z_it)
    """
    policy = np.asarray(policy, dtype=float)
    z_initial = np.asarray(z_initial, dtype=float)
    beta = np.asarray(beta, dtype=float)
    eta = np.asarray(eta, dtype=float)
    weights = np.asarray(weights, dtype=float)

    periods, classes = policy.shape

    z_history = np.empty((periods, classes), dtype=float)
    gamma_history = np.empty_like(z_history)

    total = 0.0
    cumulative_x = np.zeros(classes, dtype=float)

    for t in range(periods):
        z = z_initial - beta * t + eta * cumulative_x
        gamma = phi(z)

        z_history[t] = z
        gamma_history[t] = gamma

        total += np.sum(
            weights * policy[t] * gamma
        )

        cumulative_x += policy[t]

    return float(total), z_history, gamma_history


def extremal_policies(periods):
    """
    All policies selecting exactly one of two classes per period.
    """
    policies = []

    for choices in itertools.product([0, 1], repeat=periods):
        p = np.zeros((periods, 2), dtype=float)
        p[np.arange(periods), choices] = 1.0
        policies.append(p)

    return policies


def grid_policies(periods, step):
    """
    Exhaustive discretization of the two-class simplex.

    x_t = (a, 1-a).
    """
    values = np.arange(
        0.0,
        1.0 + step / 2.0,
        step,
    )

    for allocations in itertools.product(values, repeat=periods):
        p = np.empty((periods, 2), dtype=float)

        for t, a in enumerate(allocations):
            p[t] = [a, 1.0 - a]

        yield p


def optimize(policies, params):
    best_value = -np.inf
    best_policy = None
    best_z = None
    best_gamma = None

    for policy in policies:
        value, z, gamma = evaluate_policy(
            policy,
            params["z_initial"],
            params["beta"],
            params["eta"],
            params["weights"],
        )

        if value > best_value:
            best_value = value
            best_policy = policy.copy()
            best_z = z.copy()
            best_gamma = gamma.copy()

    return best_value, best_policy, best_z, best_gamma


def main():
    config = json.loads(
        (EXP_DIR / "config.json").read_text()
    )

    periods = int(config["periods"])
    step = float(config["grid_step"])
    tolerance = float(config["tolerance"])

    # Exact search over all extremal policies.
    extreme_value, extreme_policy, extreme_z, extreme_gamma = optimize(
        extremal_policies(periods),
        config,
    )

    # Exhaustive search over a much larger set including mixed policies.
    grid_value, grid_policy, grid_z, grid_gamma = optimize(
        grid_policies(periods, step),
        config,
    )

    # Verify that every state encountered in the whole feasible region
    # remains inside the convex part of logistic phi.
    #
    # With beta = 0 and x_it <= 1, maximum reachable competence is:
    # z_i1 + eta_i * (T-1).
    z_initial = np.asarray(config["z_initial"], dtype=float)
    beta = np.asarray(config["beta"], dtype=float)
    eta = np.asarray(config["eta"], dtype=float)

    if np.any(beta != 0.0):
        raise ValueError(
            "This fixture assumes beta = 0 for the convex-region bound."
        )

    max_reachable_z = (
        z_initial + eta * (periods - 1)
    )

    convexity_values = phi_second_derivative(max_reachable_z)

    convex_region_verified = bool(
        np.all(max_reachable_z < 0.0)
        and np.all(convexity_values > 0.0)
    )

    objective_gap = float(grid_value - extreme_value)

    extremal_matches_global = bool(
        abs(objective_gap) <= tolerance
    )

    passed = (
        convex_region_verified
        and extremal_matches_global
    )

    output = {
        "experiment_id": "B2.2",
        "kind": "source_reproduction",
        "status": "REPRODUCED" if passed else "FAILED",
        "source_citekeys": config["source_citekeys"],
        "source": "Gutjahr (2011)",
        "theoretical_property": (
            "Existence of an optimal extremal policy "
            "when phi is convex on the relevant region."
        ),
        "periods": periods,
        "grid_step": step,
        "number_extremal_policies": 2 ** periods,
        "number_grid_policies": int(
            round(1.0 / step) + 1
        ) ** periods,
        "max_reachable_z": max_reachable_z.tolist(),
        "phi_second_derivative_at_max_z": (
            convexity_values.tolist()
        ),
        "convex_region_verified": convex_region_verified,
        "best_extremal_value": extreme_value,
        "best_grid_value": grid_value,
        "objective_gap_grid_minus_extremal": objective_gap,
        "best_extremal_policy": extreme_policy.tolist(),
        "best_grid_policy": grid_policy.tolist(),
        "best_extremal_z": extreme_z.tolist(),
        "best_extremal_gamma": extreme_gamma.tolist(),
        "extremal_matches_full_grid_optimum": (
            extremal_matches_global
        ),
        "passed": passed,
    }

    write_result_bundle(
        root=ROOT,
        experiment_dir=EXP_DIR,
        result_dir=RESULT_DIR,
        run_file=Path(__file__).resolve(),
        output=output,
    )

    print(json.dumps(output, indent=2))

    if not passed:
        raise SystemExit("B2.2 FAILED")


if __name__ == "__main__":
    main()
