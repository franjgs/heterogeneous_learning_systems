import itertools
import json
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
RESULT_DIR = (
    ROOT / "results" / "foundations"
    / "b2_5_gutjahr_switching"
)
write_result_bundle = runpy.run_path(
    str(ROOT / "experiments" / "foundations" / "_provenance.py")
)["write_result_bundle"]


def phi(z):
    """Piecewise efficiency function used in Gutjahr Examples 2 and 3."""
    z = np.asarray(z, dtype=float)
    return np.where(
        z < -1.0,
        0.0,
        np.where(z <= 1.0, (1.0 + z) / 2.0, 1.0),
    )


def evaluate_extremal_policy(
    choices, z_initial, beta, eta, weights
):
    z_initial = np.asarray(z_initial, dtype=float)
    beta = np.asarray(beta, dtype=float)
    eta = np.asarray(eta, dtype=float)
    weights = np.asarray(weights, dtype=float)

    experience = np.zeros(len(z_initial), dtype=float)
    total = 0.0
    history = []

    for t, choice in enumerate(choices):
        z = z_initial - beta * t + eta * experience
        gamma = phi(z)
        reward = float(weights[choice] * gamma[choice])
        total += reward

        history.append({
            "period": t + 1,
            "choice": int(choice),
            "z": z.tolist(),
            "gamma": gamma.tolist(),
            "reward": reward,
        })

        experience[choice] += 1.0

    return float(total), history


def enumerate_extremal_policies(params):
    classes = len(params["z_initial"])
    periods = int(params["periods"])
    results = []

    for choices in itertools.product(range(classes), repeat=periods):
        value, history = evaluate_extremal_policy(
            choices,
            params["z_initial"],
            params["beta"],
            params["eta"],
            params["weights"],
        )
        results.append({
            "choices": choices,
            "objective": value,
            "history": history,
        })

    return results


def main():
    config = json.loads(
        (EXP_DIR / "config.json").read_text()
    )

    tol = float(config["tolerance"])
    published_policy = tuple(config["published_claimed_optimal_policy"])

    results = enumerate_extremal_policies(config)
    best_value = max(r["objective"] for r in results)

    computed_optimal = [
        r for r in results
        if abs(r["objective"] - best_value) <= tol
    ]

    published_result = next(
        r for r in results
        if r["choices"] == published_policy
    )

    source_reproduced = (
        len(computed_optimal) == 1
        and computed_optimal[0]["choices"] == published_policy
    )

    expected_objectives = {
        tuple(int(i) for i in key.split(",")): float(value)
        for key, value in config[
            "expected_objectives_from_published_equations"
        ].items()
    }
    computed_objectives = {
        result["choices"]: result["objective"]
        for result in results
    }
    implementation_check_passed = (
        set(computed_objectives) == set(expected_objectives)
        and all(
            abs(computed_objectives[policy] - expected) <= tol
            for policy, expected in expected_objectives.items()
        )
        and not source_reproduced
        and computed_optimal[0]["choices"] == (0, 0)
    )

    output = {
        "experiment_id": "B2.5",
        "kind": "source_reproduction",
        "source_citekeys": config["source_citekeys"],
        "source": "Gutjahr (2011), Example 3",
        "status": (
            "REPRODUCED"
            if source_reproduced
            else "FAILED_SOURCE_REPRODUCTION"
        ),
        "parameters_as_published": {
            "z_initial": config["z_initial"],
            "beta": config["beta"],
            "eta": config["eta"],
            "weights": config["weights"],
        },
        "published_claimed_optimal_policy": list(published_policy),
        "published_policy_objective_from_equations": (
            published_result["objective"]
        ),
        "computed_optimal_policies": [
            list(r["choices"]) for r in computed_optimal
        ],
        "computed_best_objective": best_value,
        "all_extremal_policies": [
            {
                "policy": list(r["choices"]),
                "objective": r["objective"],
            }
            for r in results
        ],
        "source_reproduced": source_reproduced,
        "implementation_check_passed": implementation_check_passed,
        "note": (
            "Using the published parameters, competence dynamics, and "
            "piecewise efficiency function literally, the claimed "
            "switching optimum is not recovered. The omitted first-class "
            "term in the source simplification is nonzero when x11 > 0."
        ),
    }

    write_result_bundle(
        root=ROOT,
        experiment_dir=EXP_DIR,
        result_dir=RESULT_DIR,
        run_file=Path(__file__).resolve(),
        output=output,
    )

    print(json.dumps(output, indent=2))

    if not implementation_check_passed:
        raise SystemExit("B2.5 IMPLEMENTATION AUDIT FAILED")


if __name__ == "__main__":
    main()
