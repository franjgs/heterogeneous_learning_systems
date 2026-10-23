"""Bounded p/q study of the exact S4 transfer option value."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from math import isclose, prod
from pathlib import Path
from time import perf_counter

from hls.synthetic.hls_s4_transfer_exact import (
    ExactTransferCase,
    _zero_efficacy,
    action_catalogs,
    independent_exhaustive,
    solve_bellman,
)
from experiments.run_hls_s4_transfer_opportunities import scenario


RESULT = Path("results/experiments/hls_s4_transfer_frontier/results.json")
FRONTIER_CONFIGS = ((2, 2), (1, 3), (3, 1))
ENUMERATION_VALIDATION = (1, 2)  # previously established T=3 minimum


def make_case(p: int, q: int) -> ExactTransferCase:
    if p < 1 or q < 1:
        raise ValueError("p and q must both be positive")
    setup = scenario(0.05)
    x = setup["environment"].emissions["x"].problems[0]
    y = setup["environment"].emissions["y"].problems[0]
    return ExactTransferCase(
        organization=setup["organization"],
        problems=(x,) * p + (y,) * q,
        profile=setup["learning"],
        efficacy=setup["efficacy"],
        teaching_parameters=setup["teaching_parameters"],
        teaching_effort=setup["policy_parameters"].effort,
        effort_choices=setup["effort_choices"],
    )


def summarize_path(result) -> dict:
    return {
        "value": result.value,
        "visited_states": result.visited_states,
        "teaching_count": sum(row.action.teaching is not None for row in result.periods),
        "teaching_actions": [
            {"period": row.period, **asdict(row.action.teaching)}
            for row in result.periods if row.action.teaching is not None
        ],
        "periods": [asdict(row) for row in result.periods],
    }


def solve_instance(p: int, q: int) -> dict:
    case = make_case(p, q)
    catalogs_a = action_catalogs(case, transfer_available=False)
    catalogs_b = action_catalogs(case, transfer_available=True)
    if any(not set(a).issubset(set(b)) for a, b in zip(catalogs_a, catalogs_b)):
        raise AssertionError("B must contain all feasible A actions at every period")

    started = perf_counter()
    a = solve_bellman(case, transfer_available=False)
    a_seconds = perf_counter() - started
    started = perf_counter()
    b = solve_bellman(case, transfer_available=True)
    b_seconds = perf_counter() - started
    if b.value < a.value - 1e-10:
        raise AssertionError(f"optional transfer reduced exact optimum for p={p}, q={q}")

    zero = solve_bellman(case, transfer_available=True,
                         efficacy=_zero_efficacy(case.efficacy))
    if not isclose(zero.value, a.value, rel_tol=0.0, abs_tol=1e-10):
        raise AssertionError("zero physical transfer must equal the MIS-only optimum")

    return {
        "p": p,
        "q": q,
        "horizon": p + q,
        "action_counts_per_period": {
            "A": [len(row) for row in catalogs_a],
            "B": [len(row) for row in catalogs_b],
        },
        "enumerated_sequence_upper_bounds": {
            "A": prod(map(len, catalogs_a)),
            "B": prod(map(len, catalogs_b)),
        },
        "A": summarize_path(a),
        "B": summarize_path(b),
        "delta_B_minus_A": b.value - a.value,
        "zero_efficacy_B_value": zero.value,
        "runtime_seconds_descriptive": {"A": a_seconds, "B": b_seconds},
    }


def run() -> dict:
    cases = [solve_instance(p, q) for p, q in FRONTIER_CONFIGS]
    p, q = ENUMERATION_VALIDATION
    validation_case = make_case(p, q)
    bellman_a = solve_bellman(validation_case, transfer_available=False)
    bellman_b = solve_bellman(validation_case, transfer_available=True)
    exhaustive_a, _, _, _ = independent_exhaustive(
        validation_case, transfer_available=False,
    )
    exhaustive_b, _, _, _ = independent_exhaustive(
        validation_case, transfer_available=True,
    )
    if not isclose(bellman_a.value, exhaustive_a, rel_tol=0.0, abs_tol=1e-10):
        raise AssertionError("T=3 A Bellman/exhaustive mismatch")
    if not isclose(bellman_b.value, exhaustive_b, rel_tol=0.0, abs_tol=1e-10):
        raise AssertionError("T=3 B Bellman/exhaustive mismatch")

    result = {
        "experiment": "S4 exact transfer option value across preparation/demand lengths",
        "fixed_physical_configuration": {
            "agents": ["A", "B"],
            "competencies": ["x", "y"],
            "initial_competence": validation_case.organization.competence_initial,
            "MIS_eta": validation_case.profile.eta,
            "individual_effort_limits": validation_case.organization.effort_limits,
            "collective_budget": validation_case.organization.collective_effort_budget,
            "teaching_effort": validation_case.teaching_effort,
            "transfer_rate": validation_case.teaching_parameters.transfer_rate,
            "efficacy_tensor": validation_case.efficacy.values,
            "production_effort_catalog": validation_case.effort_choices,
            "all_declared_feasible_actions_enumerated": True,
            "reward": "existing CES, evaluated before transitions; functional success is reported separately",
            "demand_family": "x repeated p periods, followed by y repeated q periods",
        },
        "frontier_cases": cases,
        "independent_enumeration_validation": {
            "p": p,
            "q": q,
            "bellman_A": bellman_a.value,
            "exhaustive_A": exhaustive_a,
            "bellman_B": bellman_b.value,
            "exhaustive_B": exhaustive_b,
            "sequence_counts": cases[0]["enumerated_sequence_upper_bounds"],
            "matches": True,
        },
        "scope_note": "Only predeclared neighboring p/q configurations; no physical parameters were tuned.",
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def extend(p: int, q: int) -> dict:
    """Append one predeclared complexity-frontier point to an existing run."""
    if not RESULT.exists():
        raise FileNotFoundError("run the base p/q frontier before extending it")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    if any(row["p"] == p and row["q"] == q for row in result["frontier_cases"]):
        raise ValueError(f"p={p}, q={q} is already in the frontier artifact")
    row = solve_instance(p, q)
    result["frontier_cases"].append(row)
    result["scope_note"] += f" Added one sequential extension p={p}, q={q} after the prior point's runtime check."
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return row


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extend", nargs=2, type=int, metavar=("P", "Q"))
    args = parser.parse_args()
    if args.extend:
        rows = [extend(*args.extend)]
    else:
        rows = run()["frontier_cases"]
    print(json.dumps([
        {"p": row["p"], "q": row["q"], "JA": row["A"]["value"],
         "JB": row["B"]["value"], "delta": row["delta_B_minus_A"],
         "teachings_B": row["B"]["teaching_count"],
         "states_B": row["B"]["visited_states"],
         "runtime_B": row["runtime_seconds_descriptive"]["B"]}
        for row in rows
    ], indent=2))
