"""Run the two bounded deterministic S4 exact instances."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hls.synthetic.hls_s4 import canonical_cases, evaluate_case, result_dict


DEFAULT_OUTPUT = Path("results/experiments/hls_s4/results.json")


def main(output: Path = DEFAULT_OUTPUT) -> None:
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing S4 results: {output}")
    cases = [evaluate_case(case) for case in canonical_cases()]
    payload = {
        "experiment_id": "HLS-S4",
        "status": "BOUNDED_EXACT_DETERMINISTIC_COMPARISON",
        "model": {
            "agents": 2,
            "tasks": 2,
            "one_task_per_agent_period": True,
            "one_agent_per_task_period": True,
            "demand": "known deterministic Boolean availability by task and period",
            "reward": "sum of pre-transition competence for assigned pairs",
            "learning": "existing MIS-v2 transition from binary productive exposure, post-reward",
            "transfer_teaching_cooperation": False,
            "intertemporal_resource_budget": False,
            "randomness": False,
        },
        "cases": [result_dict(case) for case in cases],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    for case in cases:
        print(f"{case.case.name}: reactive={case.reactive.reward:.12f}, "
              f"Bellman={case.bellman.reward:.12f}, exhaustive={case.exhaustive.reward:.12f}")
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    main(parser.parse_args().output)
