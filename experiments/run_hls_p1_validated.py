"""Run the bounded exact HLS-P1 comparison (never runs on import)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import sys
from time import perf_counter

from hls.synthetic.hls_p1 import default_scenarios, evaluate_scenario


OUTPUT = Path("results/experiments/hls_p1_validated/results.json")
def main(output: Path = OUTPUT) -> None:
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing HLS-P1 result: {output}")
    results = []
    for scenario in default_scenarios():
        started = perf_counter()
        result = evaluate_scenario(scenario)
        result["wall_seconds"] = perf_counter() - started
        results.append(result)
    payload = {
        "experiment_id": "HLS-P1-validated",
        "title": "Anticipatory Capability Development in Dynamic Technical Operations",
        "status": "BOUNDED_EXACT_COMPARISON_EXECUTED",
        "model": {
            "agents": ("A", "B"), "skills_and_tasks": ("x", "y"),
            "objective": "sum over periods of equal-weight mean capped requirement fulfilment; success separately reported",
            "development": "MIS-v2 learning-by-doing from productive effort; no separate development action or monetary cost",
            "resource_accounting": "production effort is both constrained resource and MIS-v2 exposure; never subtracted a second time",
            "observation": "all policies observe current task and true current competence; no future realized task is exposed",
            "future_information": "all policies use the declared exogenous demand law; only FIXED-OPT optimizes its fixed map and HLS uses continuation values",
            "demand_paths": "all 2^4 paths enumerated and paired exactly under each process; no Monte Carlo sampling",
        },
        "software": {"python": sys.version.split()[0], "platform": platform.platform()},
        "scenarios": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT,
                        help="new result path (existing files are never overwritten)")
    main(parser.parse_args().output)
