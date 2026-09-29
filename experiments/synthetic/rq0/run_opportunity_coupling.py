"""Execute the one frozen exact RQ0 routing--opportunity coupling family."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from hls.synthetic.rq0_opportunity_coupling import (
    BETA,
    EPSILON,
    ETA,
    INITIAL_COMPETENCE,
    KAPPA,
    LAMBDA_GRID,
    MEAN_OPPORTUNITY,
    TARGET_BY_TIME,
    TASK_SEQUENCE,
    TERMINAL_TASK,
    run_grid,
)


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "results" / "foundations" / "rq0_routing_opportunity_coupling"
PROTOCOL = ROOT / "docs" / "experimental_foundations" / "RQ0_ROUTING_OPPORTUNITY_COUPLING_PROTOCOL.md"
MODULE = ROOT / "src" / "hls" / "synthetic" / "rq0_opportunity_coupling.py"
SOLVER = ROOT / "src" / "hls" / "synthetic" / "exact.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _actions(actions) -> str:
    return "|".join(sorted(str(action) for action in actions))


def run(output: Path = OUTPUT) -> tuple[dict[str, object], ...]:
    """Execute exactly the frozen 21-point grid and write reviewed outputs."""
    evaluations = run_grid()
    rows: list[dict[str, object]] = []
    for evaluation in evaluations:
        for node_index, node in enumerate(evaluation.nodes):
            rows.append(
                {
                    "lambda": evaluation.lambda_value,
                    "node_index": node_index,
                    "time": node.state.time,
                    "competence": json.dumps(node.state.competence),
                    "resources": json.dumps(dict(node.state.resources)),
                    "task": node.task,
                    "J_HLS": evaluation.j_hls,
                    "J_SEP_min": evaluation.j_sep_min,
                    "J_SEP_max": evaluation.j_sep_max,
                    "J_SEP_Omega": evaluation.j_sep_omega,
                    "Phi": evaluation.phi,
                    "regime": evaluation.regime,
                    "sep_admissible_hls_exists": evaluation.sep_admissible_hls_exists,
                    "HLS_initial_actions": _actions(evaluation.hls_initial_actions),
                    "SEP_initial_actions": _actions(evaluation.sep_initial_actions),
                    "greedy_actions": _actions(node.greedy_actions),
                    "HLS_optimal_actions": _actions(node.hls_actions),
                    "p_M1": node.opportunity_probabilities["M1"],
                    "p_M2": node.opportunity_probabilities["M2"],
                    "W0": node.w0,
                    "W1": node.w1,
                    "D_star": node.d_star,
                }
            )

    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "all_lambda_nodes.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "grid": list(LAMBDA_GRID),
        "n_lambda": len(evaluations),
        "common_primitives": {
            "initial_competence": INITIAL_COMPETENCE,
            "task_sequence": TASK_SEQUENCE,
            "terminal_task": TERMINAL_TASK,
            "target_by_time": TARGET_BY_TIME,
            "eta": ETA,
            "kappa": KAPPA,
            "beta": BETA,
            "mean_opportunity": MEAN_OPPORTUNITY,
            "epsilon": EPSILON,
            "persistent_budget": None,
            "gamma": None,
        },
        "lambda_results": [
            {
                "lambda": evaluation.lambda_value,
                "J_HLS": evaluation.j_hls,
                "J_SEP_min": evaluation.j_sep_min,
                "J_SEP_max": evaluation.j_sep_max,
                "J_SEP_Omega": evaluation.j_sep_omega,
                "Phi": evaluation.phi,
                "regime": evaluation.regime,
                "sep_admissible_hls_exists": evaluation.sep_admissible_hls_exists,
                "HLS_initial_actions": sorted(evaluation.hls_initial_actions),
                "SEP_initial_actions": sorted(evaluation.sep_initial_actions),
            }
            for evaluation in evaluations
        ],
    }
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    manifest = {
        "protocol_sha256": _sha256(PROTOCOL),
        "family_module_sha256": _sha256(MODULE),
        "exact_solver_sha256": _sha256(SOLVER),
        "runner_sha256": _sha256(Path(__file__).resolve()),
        "all_lambda_nodes_sha256": _sha256(csv_path),
        "summary_sha256": _sha256(summary_path),
        "deterministic": True,
        "seeds": None,
        "n_lambda": len(evaluations),
        "lambda_grid": list(LAMBDA_GRID),
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return tuple(rows)


def main() -> None:
    rows = run()
    first_rows = {row["lambda"]: row for row in rows if row["time"] == 0}
    print(f"wrote {len(rows)} node rows for {len(first_rows)} frozen lambda points")
    for lambda_value, row in first_rows.items():
        print(
            f"lambda={lambda_value:.2f} "
            f"J_HLS={float(row['J_HLS']):.12f} "
            f"J_SEP_max={float(row['J_SEP_max']):.12f} "
            f"Phi={float(row['Phi']):.12f} "
            f"{row['regime']}"
        )


if __name__ == "__main__":
    main()
