"""Validate S4 planning against tie-aware myopia and a frozen-competence control."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hls.synthetic.hls_s4 import (
    canonical_cases,
    investment_family,
    validate_case,
    validation_dict,
)


DEFAULT_OUTPUT = Path("results/experiments/hls_s4_validation/results.json")


def main(output: Path = DEFAULT_OUTPUT) -> None:
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing S4 validation: {output}")
    original_b = canonical_cases()[1]
    family = investment_family()
    reports = [validate_case(original_b)]
    reports.extend(validate_case(case) for case in family)
    reports.append(validate_case(family[-1], learning_enabled=False))
    payload = {
        "experiment_id": "HLS-S4-scientific-validation",
        "status": "BOUNDED_EXACT_TIE_AWARE_COMPARISON",
        "model": {
            "transition": "existing MIS-v2; binary exposure from executed assignments",
            "reward": "sum of pre-transition competence over assigned pairs",
            "planning_information": "known complete deterministic demand and MIS-v2 parameters",
            "best_myopic": "DP restricted at every state to immediate maximizers within tolerance 1e-12",
            "enumeration": "independent enumeration of all action sequences; restricted filter for BEST-MYOPIC",
        },
        "results": [validation_dict(report) for report in reports],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    for report in reports:
        print(f"{report.case.name} learning={report.learning_enabled}: "
              f"reactive={report.reactive.reward:.12f}, "
              f"BEST-MYOPIC={report.best_myopic.reward:.12f}, "
              f"Bellman={report.bellman.reward:.12f}, "
              f"enumerated-myopic={report.exhaustive_best_myopic_value:.12f}")
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    main(parser.parse_args().output)
