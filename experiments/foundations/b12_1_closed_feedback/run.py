import json
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
RESULT_DIR = ROOT / "results" / "foundations" / "b12_1_closed_feedback"
write_result_bundle = runpy.run_path(
    str(ROOT / "experiments" / "foundations" / "_provenance.py")
)["write_result_bundle"]


def phi(z):
    """Gutjahr-style competence-to-efficiency mapping."""
    z = np.asarray(z, dtype=float)
    return 1.0 / (1.0 + np.exp(-z))


def routing(problem_probabilities, z):
    """
    Minimal Beam-1-inspired allocation.

    Operational value of competence i:
        p_i * phi(z_i)

    All work is assigned to the competence with highest value.
    """
    p = np.asarray(problem_probabilities, dtype=float)
    gamma = phi(z)
    scores = p * gamma

    choice = int(np.argmax(scores))

    allocation = np.zeros(len(z), dtype=float)
    allocation[choice] = 1.0

    return choice, allocation, scores


def learning_step(z, allocation, beta, eta):
    """
    Beam-2 competence evolution:
        z_{i,t+1} = z_{it} - beta_i + eta_i x_{it}
    """
    z = np.asarray(z, dtype=float)
    allocation = np.asarray(allocation, dtype=float)
    beta = np.asarray(beta, dtype=float)
    eta = np.asarray(eta, dtype=float)

    return z - beta + eta * allocation


def simulate(config):
    periods = int(config["periods"])

    p = np.asarray(config["problem_probabilities"], dtype=float)
    z = np.asarray(config["z_initial"], dtype=float)
    beta = np.asarray(config["beta"], dtype=float)
    eta = np.asarray(config["eta"], dtype=float)

    history = []

    for t in range(periods):
        z_before = z.copy()

        choice, allocation, scores = routing(p, z_before)

        z_after = learning_step(
            z_before,
            allocation,
            beta,
            eta,
        )

        history.append({
            "period": t + 1,
            "z_before": z_before.tolist(),
            "gamma": phi(z_before).tolist(),
            "routing_scores": scores.tolist(),
            "choice": choice,
            "allocation": allocation.tolist(),
            "z_after": z_after.tolist(),
        })

        z = z_after

    return history


def verify_closed_feedback(history, config):
    beta = np.asarray(config["beta"], dtype=float)
    eta = np.asarray(config["eta"], dtype=float)
    tol = float(config["tolerance"])

    for t, row in enumerate(history):
        z_before = np.asarray(row["z_before"])
        allocation = np.asarray(row["allocation"])
        z_after = np.asarray(row["z_after"])

        expected_after = z_before - beta + eta * allocation

        if not np.allclose(
            z_after,
            expected_after,
            atol=tol,
            rtol=0.0,
        ):
            return False

        if t + 1 < len(history):
            next_before = np.asarray(history[t + 1]["z_before"])

            if not np.allclose(
                z_after,
                next_before,
                atol=tol,
                rtol=0.0,
            ):
                return False

    return True


def main():
    config = json.loads(
        (EXP_DIR / "config.json").read_text()
    )

    history = simulate(config)
    closed_feedback_verified = verify_closed_feedback(
        history,
        config,
    )

    output = {
        "experiment_id": "B12.1",
        "kind": "hls_translation",
        "source_citekeys": config["source_citekeys"],
        "status": (
            "SUPPORTED"
            if closed_feedback_verified
            else "FAILED"
        ),
        "closed_feedback_verified": closed_feedback_verified,
        "history": history,
    }

    write_result_bundle(
        root=ROOT,
        experiment_dir=EXP_DIR,
        result_dir=RESULT_DIR,
        run_file=Path(__file__).resolve(),
        output=output,
    )

    print(json.dumps(output, indent=2))

    if not closed_feedback_verified:
        raise SystemExit("B12.1 FAILED")


if __name__ == "__main__":
    main()
