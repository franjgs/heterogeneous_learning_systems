import importlib.util
import json
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
RESULT_DIR = ROOT / "results" / "foundations" / "b12_2_recover_beam1"
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


def verify_beam1_recovery(history, config):
    tol = float(config["tolerance"])
    z0 = np.asarray(config["z_initial"], dtype=float)

    expected_choice, expected_allocation, expected_scores = b12_1.routing(
        config["problem_probabilities"],
        z0,
    )

    for row in history:
        if not np.allclose(row["z_before"], z0, atol=tol, rtol=0.0):
            return False

        if not np.allclose(row["z_after"], z0, atol=tol, rtol=0.0):
            return False

        if row["choice"] != expected_choice:
            return False

        if not np.allclose(
            row["allocation"],
            expected_allocation,
            atol=tol,
            rtol=0.0,
        ):
            return False

        if not np.allclose(
            row["routing_scores"],
            expected_scores,
            atol=tol,
            rtol=0.0,
        ):
            return False

    return True


def main():
    config = json.loads(
        (EXP_DIR / "config.json").read_text()
    )

    history = b12_1.simulate(config)
    recovered = verify_beam1_recovery(history, config)

    output = {
        "experiment_id": "B12.2",
        "kind": "limiting_case",
        "source_citekeys": config["source_citekeys"],
        "status": "REPRODUCED" if recovered else "FAILED",
        "beam1_recovered": recovered,
        "beta": config["beta"],
        "eta": config["eta"],
        "static_choice": history[0]["choice"],
        "static_routing_scores": history[0]["routing_scores"],
        "initial_state": config["z_initial"],
        "final_state": history[-1]["z_after"],
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
        raise SystemExit("B12.2 FAILED")


if __name__ == "__main__":
    main()
