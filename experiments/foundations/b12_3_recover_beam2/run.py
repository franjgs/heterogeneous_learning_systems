import importlib.util
import json
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
RESULT_DIR = ROOT / "results" / "foundations" / "b12_3_recover_beam2"
write_result_bundle = runpy.run_path(
    str(ROOT / "experiments" / "foundations" / "_provenance.py")
)["write_result_bundle"]

B12_1_PATH = (
    ROOT / "experiments" / "foundations"
    / "b12_1_closed_feedback" / "run.py"
)

spec = importlib.util.spec_from_file_location("b12_1", B12_1_PATH)
b12_1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b12_1)


def closed_form_state(z_initial, beta, eta, allocation_path, t):
    """
    Gutjahr state at period t+1, with Python t=0 corresponding
    to the initial state.

    z(t) = z(0) - beta*t + eta*sum_{s<t} x(s)
    """
    z_initial = np.asarray(z_initial, dtype=float)
    beta = np.asarray(beta, dtype=float)
    eta = np.asarray(eta, dtype=float)

    if t == 0:
        experience = np.zeros_like(z_initial)
    else:
        experience = np.asarray(
            allocation_path[:t],
            dtype=float,
        ).sum(axis=0)

    return z_initial - beta * t + eta * experience


def simulate_fixed_allocations(config):
    z = np.asarray(config["z_initial"], dtype=float)
    beta = np.asarray(config["beta"], dtype=float)
    eta = np.asarray(config["eta"], dtype=float)
    allocation_path = config["allocation_path"]

    history = []

    for t, allocation in enumerate(allocation_path):
        allocation = np.asarray(allocation, dtype=float)
        z_before = z.copy()

        expected_before = closed_form_state(
            config["z_initial"],
            beta,
            eta,
            allocation_path,
            t,
        )

        z_after = b12_1.learning_step(
            z_before,
            allocation,
            beta,
            eta,
        )

        expected_after = closed_form_state(
            config["z_initial"],
            beta,
            eta,
            allocation_path,
            t + 1,
        )

        history.append({
            "period": t + 1,
            "allocation": allocation.tolist(),
            "z_before": z_before.tolist(),
            "closed_form_before": expected_before.tolist(),
            "z_after": z_after.tolist(),
            "closed_form_after": expected_after.tolist(),
        })

        z = z_after

    return history


def verify_beam2_recovery(history, config):
    tol = float(config["tolerance"])

    for row in history:
        if not np.allclose(
            row["z_before"],
            row["closed_form_before"],
            atol=tol,
            rtol=0.0,
        ):
            return False

        if not np.allclose(
            row["z_after"],
            row["closed_form_after"],
            atol=tol,
            rtol=0.0,
        ):
            return False

    return True


def main():
    config = json.loads(
        (EXP_DIR / "config.json").read_text()
    )

    history = simulate_fixed_allocations(config)
    recovered = verify_beam2_recovery(history, config)

    output = {
        "experiment_id": "B12.3",
        "kind": "limiting_case",
        "source_citekeys": config["source_citekeys"],
        "status": "REPRODUCED" if recovered else "FAILED",
        "beam2_recovered": recovered,
        "routing_enabled": False,
        "allocation_path": config["allocation_path"],
        "initial_state": config["z_initial"],
        "final_state": history[-1]["z_after"],
        "max_closed_form_error": max(
            max(
                abs(a - b)
                for a, b in zip(
                    row["z_after"],
                    row["closed_form_after"],
                )
            )
            for row in history
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

    if not recovered:
        raise SystemExit("B12.3 FAILED")


if __name__ == "__main__":
    main()
