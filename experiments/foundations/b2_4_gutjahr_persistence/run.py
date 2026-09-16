import itertools
import json
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
RESULT_DIR = (
    ROOT / "results" / "foundations"
    / "b2_4_gutjahr_persistence"
)
write_result_bundle = runpy.run_path(
    str(ROOT / "experiments" / "foundations" / "_provenance.py")
)["write_result_bundle"]


def phi(z):
    """Strictly increasing logistic efficiency."""
    z = np.asarray(z, dtype=float)
    return 1.0 / (1.0 + np.exp(-z))


def evaluate_extremal_policy(
    choices,
    z_initial,
    eta,
    weights,
):
    """
    No-forgetting case beta_i = 0.

    choices[t] is the class selected in period t.
    """
    z_initial = np.asarray(z_initial, dtype=float)
    eta = np.asarray(eta, dtype=float)
    weights = np.asarray(weights, dtype=float)

    experience = np.zeros(len(z_initial), dtype=float)

    total = 0.0
    z_history = []

    for choice in choices:
        z = z_initial + eta * experience
        z_history.append(z.copy())

        total += weights[choice] * phi(z[choice])
        experience[choice] += 1.0

    return float(total), np.asarray(z_history)


def enumerate_extremal_policies(periods, classes, params):
    results = []

    for choices in itertools.product(
        range(classes),
        repeat=periods,
    ):
        value, z = evaluate_extremal_policy(
            choices,
            params["z_initial"],
            params["eta"],
            params["weights"],
        )

        results.append(
            {
                "choices": choices,
                "value": value,
                "z": z,
            }
        )

    return results


def is_persistent(choices):
    return len(set(choices)) == 1


def main():
    config = json.loads(
        (EXP_DIR / "config.json").read_text()
    )

    periods = int(config["periods"])
    classes = len(config["z_initial"])
    tolerance = float(config["tolerance"])

    beta = np.asarray(config["beta"], dtype=float)
    eta = np.asarray(config["eta"], dtype=float)

    no_forgetting = bool(
        np.all(np.abs(beta) <= tolerance)
    )
    positive_learning = bool(
        np.all(eta > 0.0)
    )
    positive_weights = bool(
        np.all(np.asarray(config["weights"], dtype=float) > 0.0)
    )

    results = enumerate_extremal_policies(
        periods,
        classes,
        config,
    )

    best_value = max(r["value"] for r in results)

    optimal = [
        r for r in results
        if abs(r["value"] - best_value) <= tolerance
    ]

    persistent_optimal = [
        r for r in optimal
        if is_persistent(r["choices"])
    ]

    # Evaluate the n possible persistent policies independently.
    persistent_candidates = []

    for i in range(classes):
        choices = tuple([i] * periods)

        value, _ = evaluate_extremal_policy(
            choices,
            config["z_initial"],
            config["eta"],
            config["weights"],
        )

        persistent_candidates.append(
            {
                "class": i + 1,
                "choices": list(choices),
                "objective": value,
            }
        )

    best_persistent_value = max(
        p["objective"]
        for p in persistent_candidates
    )

    persistence_gap = (
        best_value - best_persistent_value
    )

    theorem_instance_recovered = bool(
        no_forgetting
        and positive_learning
        and positive_weights
        and len(persistent_optimal) >= 1
        and abs(persistence_gap) <= tolerance
    )

    output = {
        "experiment_id": "B2.4",
        "kind": "source_reproduction",
        "status": (
            "REPRODUCED" if theorem_instance_recovered else "FAILED"
        ),
        "source_citekeys": config["source_citekeys"],
        "source": "Gutjahr (2011), Theorem 3",
        "periods": periods,
        "classes": classes,
        "number_extremal_policies": classes ** periods,
        "no_forgetting_verified": no_forgetting,
        "positive_learning_verified": positive_learning,
        "positive_weights_verified": positive_weights,
        "best_extremal_objective": best_value,
        "number_optimal_policies": len(optimal),
        "number_persistent_optimal_policies": len(
            persistent_optimal
        ),
        "persistent_optimal_policies": [
            list(r["choices"])
            for r in persistent_optimal
        ],
        "persistent_candidates": persistent_candidates,
        "best_persistent_objective": best_persistent_value,
        "persistence_gap": persistence_gap,
        "passed": theorem_instance_recovered,
    }

    write_result_bundle(
        root=ROOT,
        experiment_dir=EXP_DIR,
        result_dir=RESULT_DIR,
        run_file=Path(__file__).resolve(),
        output=output,
    )

    print(json.dumps(output, indent=2))

    if not theorem_instance_recovered:
        raise SystemExit("B2.4 FAILED")


if __name__ == "__main__":
    main()
