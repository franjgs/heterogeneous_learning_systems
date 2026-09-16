import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
RESULT_DIR = ROOT / "results" / "foundations" / "b1_1_garicano_autarky"


def density(z):
    """
    Decreasing triangular density on [0,1]:

        f(z) = 2(1-z)
    """
    z = np.asarray(z)
    return 2.0 * (1.0 - z)


def cdf(z):
    """
    CDF corresponding to f(z)=2(1-z):

        F(z) = 2z - z^2
    """
    z = np.asarray(z)
    return 2.0 * z - z**2


def autarky_output(z, c):
    """
    Garicano (2000) autarky objective:

        y^a(z) = F(z) - c z
    """
    return cdf(z) - c * z


def analytical_optimum(c):
    """
    Interior first-order condition:

        f(z*) = c

    For f(z)=2(1-z):

        z* = 1 - c/2
    """
    return 1.0 - c / 2.0


def main():
    config = json.loads((EXP_DIR / "config.json").read_text())

    c = float(config["knowledge_cost"])
    n = int(config["grid_points"])
    tolerance = float(config["tolerance"])

    z = np.linspace(0.0, 1.0, n)
    y = autarky_output(z, c)

    numerical_z = float(z[np.argmax(y)])
    analytical_z = float(analytical_optimum(c))

    error = abs(numerical_z - analytical_z)
    foc_residual = abs(float(density(numerical_z)) - c)
    passed = error <= tolerance

    result = {
        "experiment_id": "B1.1",
        "kind": "source_reproduction",
        "source": "Garicano (2000)",
        "objective": "F(z) - c*z",
        "first_order_condition": "f(z*) = c",
        "knowledge_cost": c,
        "analytical_optimum": analytical_z,
        "numerical_optimum": numerical_z,
        "absolute_error": error,
        "foc_residual": foc_residual,
        "tolerance": tolerance,
        "passed": passed
    }

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    (RESULT_DIR / "metrics.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )

    print(json.dumps(result, indent=2))

    if not passed:
        raise SystemExit("B1.1 FAILED")


if __name__ == "__main__":
    main()
