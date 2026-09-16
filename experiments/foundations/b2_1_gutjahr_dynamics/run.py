import json
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
RESULT_DIR = ROOT / "results" / "foundations" / "b2_1_gutjahr_dynamics"
write_result_bundle = runpy.run_path(
    str(ROOT / "experiments" / "foundations" / "_provenance.py")
)["write_result_bundle"]


def logistic_phi(z):
    """
    Logistic competence-to-efficiency mapping:

        phi(z) = 1 / (1 + exp(-z))
    """
    z = np.asarray(z, dtype=float)
    return 1.0 / (1.0 + np.exp(-z))


def competence_trajectory(z_initial, beta, eta, allocations):
    """
    Gutjahr (2011):

        z_it = z_i1 - beta_i (t-1)
               + eta_i * sum_{s=1}^{t-1} x_is

    allocations[s] contains x_i,s+1.

    Therefore the allocation in period t affects competence from
    period t+1 onward.
    """
    allocations = np.asarray(allocations, dtype=float)
    periods = len(allocations)

    z = np.empty(periods, dtype=float)

    for t in range(periods):
        previous_experience = allocations[:t].sum()
        z[t] = (
            z_initial
            - beta * t
            + eta * previous_experience
        )

    return z


def recursive_trajectory(z_initial, beta, eta, allocations):
    """
    Equivalent recursive form:

        z_i,t+1 = z_it - beta_i + eta_i x_it
    """
    allocations = np.asarray(allocations, dtype=float)
    periods = len(allocations)

    z = np.empty(periods, dtype=float)
    z[0] = z_initial

    for t in range(1, periods):
        z[t] = (
            z[t - 1]
            - beta
            + eta * allocations[t - 1]
        )

    return z


def main():
    config = json.loads((EXP_DIR / "config.json").read_text())

    periods = int(config["periods"])
    classes = config["classes"]
    x = np.asarray(config["allocations"], dtype=float)
    tolerance = float(config["tolerance"])

    if x.shape != (periods, len(classes)):
        raise ValueError(
            f"Allocation matrix has shape {x.shape}; "
            f"expected {(periods, len(classes))}"
        )

    simplex_error = float(
        np.max(np.abs(x.sum(axis=1) - 1.0))
    )

    results = []
    max_equivalence_error = 0.0

    for i, params in enumerate(classes):
        allocations_i = x[:, i]

        z_closed = competence_trajectory(
            params["z_initial"],
            params["beta"],
            params["eta"],
            allocations_i,
        )

        z_recursive = recursive_trajectory(
            params["z_initial"],
            params["beta"],
            params["eta"],
            allocations_i,
        )

        equivalence_error = float(
            np.max(np.abs(z_closed - z_recursive))
        )

        max_equivalence_error = max(
            max_equivalence_error,
            equivalence_error,
        )

        gamma = logistic_phi(z_closed)

        results.append(
            {
                "class": i + 1,
                "z": z_closed.tolist(),
                "gamma": gamma.tolist(),
                "closed_recursive_error": equivalence_error,
            }
        )

    passed = (
        simplex_error <= tolerance
        and max_equivalence_error <= tolerance
    )

    output = {
        "experiment_id": "B2.1",
        "kind": "source_reproduction",
        "status": "REPRODUCED" if passed else "FAILED",
        "source_citekeys": config["source_citekeys"],
        "source": "Gutjahr (2011)",
        "periods": periods,
        "simplex_error": simplex_error,
        "closed_recursive_error": max_equivalence_error,
        "tolerance": tolerance,
        "classes": results,
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
        raise SystemExit("B2.1 FAILED")


if __name__ == "__main__":
    main()
