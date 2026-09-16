import itertools
import json
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
RESULT_DIR = ROOT / "results" / "foundations" / "b2_3_gutjahr_mixed"
write_result_bundle = runpy.run_path(
    str(ROOT / "experiments" / "foundations" / "_provenance.py")
)["write_result_bundle"]


def phi(z):
    z = np.asarray(z, dtype=float)
    return np.where(
        z < -1.0,
        0.0,
        np.where(z <= 1.0, (1.0 + z) / 2.0, 1.0),
    )


def objective(x11, x12):
    """
    Exact Gutjahr (2011), Example 2.

    x21 = 1 - x11
    x22 = 1 - x12
    """
    x21 = 1.0 - x11
    x22 = 1.0 - x12

    g1 = x11 * phi(0.0) + 1.5 * x21 * phi(0.0)
    g2 = x12 * phi(2.0 * x11) + 1.5 * x22 * phi(0.0)

    return float(g1 + g2)


def exhaustive_grid(step):
    values = np.arange(0.0, 1.0 + step / 2.0, step)

    best_value = -np.inf
    best = None

    for x11 in values:
        for x12 in values:
            value = objective(x11, x12)

            if value > best_value:
                best_value = value
                best = (float(x11), float(x12))

    return best, float(best_value)


def best_extremal_policy():
    candidates = []

    for x11, x12 in itertools.product([0.0, 1.0], repeat=2):
        value = objective(x11, x12)
        candidates.append(((x11, x12), value))

    return max(candidates, key=lambda item: item[1]), candidates


def main():
    config = json.loads((EXP_DIR / "config.json").read_text())

    step = float(config["grid_step"])
    tol = float(config["tolerance"])

    grid_policy, grid_value = exhaustive_grid(step)
    (extreme_policy, extreme_value), extreme_candidates = (
        best_extremal_policy()
    )

    expected_policy = (
        float(config["expected_x11"]),
        float(config["expected_x12"]),
    )
    expected_value = float(config["expected_objective"])

    policy_error = max(
        abs(grid_policy[0] - expected_policy[0]),
        abs(grid_policy[1] - expected_policy[1]),
    )
    value_error = abs(grid_value - expected_value)

    mixed_strictly_better = grid_value > extreme_value + tol

    passed = (
        policy_error <= step / 2.0 + tol
        and value_error <= tol
        and mixed_strictly_better
    )

    output = {
        "experiment_id": "B2.3",
        "kind": "source_reproduction",
        "status": "REPRODUCED" if passed else "FAILED",
        "source_citekeys": config["source_citekeys"],
        "source": "Gutjahr (2011), Example 2",
        "expected_policy": list(expected_policy),
        "numerical_policy": list(grid_policy),
        "expected_objective": expected_value,
        "numerical_objective": grid_value,
        "best_extremal_policy": list(extreme_policy),
        "best_extremal_objective": extreme_value,
        "mixed_advantage": grid_value - extreme_value,
        "extremal_candidates": [
            {
                "policy": list(policy),
                "objective": value
            }
            for policy, value in extreme_candidates
        ],
        "policy_error": policy_error,
        "objective_error": value_error,
        "mixed_strictly_better": mixed_strictly_better,
        "passed": passed
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
        raise SystemExit("B2.3 FAILED")


if __name__ == "__main__":
    main()
