"""Run the frozen exact RQ0 T2 zero-sum competence-redistribution family."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from hls.synthetic.rq0_geometry_redistribution import (
    ALPHA_GRID,
    BETA,
    EPSILON,
    ETA,
    KAPPA,
    LAMBDA,
    MEAN_OPPORTUNITY,
    TARGET_BY_TIME,
    TASK_SEQUENCE,
    TERMINAL_TASK,
    run_grid,
)


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "results" / "foundations" / "rq0_geometry_redistribution"
MODULE = ROOT / "src" / "hls" / "synthetic" / "rq0_geometry_redistribution.py"
SOLVER = ROOT / "src" / "hls" / "synthetic" / "exact.py"
RUNNER = Path(__file__).resolve()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _actions(actions) -> str:
    return "|".join(sorted(str(action) for action in actions))


def _decision(decision) -> str:
    return "null" if decision.is_null else f"{decision.recipient}:{decision.competence}"


def run(output: Path = OUTPUT) -> tuple[dict[str, object], ...]:
    """Execute the frozen grid once and write machine-readable exact results."""
    evaluations = run_grid()
    summary_rows: list[dict[str, object]] = []
    node_rows: list[dict[str, object]] = []
    for evaluation in evaluations:
        summary_rows.append(
            {
                "alpha": evaluation.alpha,
                "competence": json.dumps(evaluation.competence),
                "J_HLS": evaluation.j_hls,
                "J_SEP_min": evaluation.j_sep_min,
                "J_SEP_max": evaluation.j_sep_max,
                "J_SEP_Omega": evaluation.j_sep_omega,
                "Phi": evaluation.phi,
                "regime": evaluation.regime,
                "sep_admissible_hls_exists": evaluation.sep_admissible_hls_exists,
                "HLS_initial_actions": _actions(evaluation.hls_initial_actions),
                "SEP_initial_actions": _actions(evaluation.sep_initial_actions),
                "root_Delta_R": evaluation.root_delta_r,
                "root_Delta_p": evaluation.root_delta_p,
                "root_Delta_p_times_D_star": evaluation.root_delta_p * evaluation.nodes[0].d_star,
                "root_local_identity_residual": evaluation.root_local_identity_residual,
            }
        )
        for node_index, node in enumerate(evaluation.nodes):
            node_rows.append(
                {
                    "alpha": evaluation.alpha,
                    "node_index": node_index,
                    "time": node.state.time,
                    "task": node.task,
                    "competence": json.dumps(node.state.competence),
                    "resources": json.dumps(dict(node.state.resources)),
                    "J_HLS": evaluation.j_hls,
                    "J_SEP_min": evaluation.j_sep_min,
                    "J_SEP_max": evaluation.j_sep_max,
                    "J_SEP_Omega": evaluation.j_sep_omega,
                    "Phi": evaluation.phi,
                    "regime": evaluation.regime,
                    "sep_admissible_hls_exists": evaluation.sep_admissible_hls_exists,
                    "R_M1": node.rewards["M1"],
                    "R_M2": node.rewards["M2"],
                    "Q_HLS_M1": node.q_values["M1"],
                    "Q_HLS_M2": node.q_values["M2"],
                    "greedy_actions": _actions(node.greedy_actions),
                    "HLS_optimal_actions": _actions(node.hls_actions),
                    "p_M1": node.opportunity_probabilities["M1"],
                    "p_M2": node.opportunity_probabilities["M2"],
                    "W0": node.w0,
                    "W1": node.w1,
                    "D_star": node.d_star,
                    "optimal_development_O0": "|".join(
                        _decision(item) for item in sorted(
                            node.optimal_development_o0,
                            key=lambda item: (str(item.recipient), str(item.competence)),
                        )
                    ),
                    "optimal_development_O1": "|".join(
                        _decision(item) for item in sorted(
                            node.optimal_development_o1,
                            key=lambda item: (str(item.recipient), str(item.competence)),
                        )
                    ),
                    "successor_competence": json.dumps(
                        [
                            {
                                "O": item.available,
                                "decision": _decision(item.decision),
                                "competence": item.competence,
                            }
                            for item in node.successors
                        ]
                    ),
                }
            )

    output.mkdir(parents=True, exist_ok=True)
    summary_path = output / "summary_by_alpha.csv"
    with summary_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
        writer.writeheader()
        writer.writerows(summary_rows)
    nodes_path = output / "on_policy_nodes.csv"
    with nodes_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(node_rows[0]))
        writer.writeheader()
        writer.writerows(node_rows)

    configuration = {
        "family": "zero-sum T2 competence redistribution",
        "alpha_grid": list(ALPHA_GRID),
        "competence_formula": [
            ["0.8", "0.8 - 0.2 * alpha"],
            ["0.6", "0.6 + 0.2 * alpha"],
        ],
        "lambda": LAMBDA,
        "baseline": MEAN_OPPORTUNITY,
        "executor_values": {str(key): value for key, value in {
            ("M1", 1): .25, ("M2", 1): .75,
            ("M1", 2): .25, ("M2", 2): .75,
        }.items()},
        "epsilon": EPSILON,
        "eta": ETA,
        "kappa": KAPPA,
        "beta": BETA,
        "task_sequence": TASK_SEQUENCE,
        "terminal_task": TERMINAL_TASK,
        "development_targets": TARGET_BY_TIME,
        "gamma": 0.0,
        "persistent_budget": None,
        "deterministic": True,
        "seeds": None,
    }
    configuration_path = output / "configuration.json"
    configuration_path.write_text(
        json.dumps(configuration, indent=2, sort_keys=True) + "\n"
    )
    manifest = {
        "family_module_sha256": _sha256(MODULE),
        "exact_solver_sha256": _sha256(SOLVER),
        "runner_sha256": _sha256(RUNNER),
        "summary_by_alpha_sha256": _sha256(summary_path),
        "on_policy_nodes_sha256": _sha256(nodes_path),
        "configuration_sha256": _sha256(configuration_path),
        "n_alpha": len(evaluations),
        "alpha_grid": list(ALPHA_GRID),
        "deterministic": True,
        "seeds": None,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return tuple(summary_rows)


def main() -> None:
    rows = run()
    print(f"wrote {len(rows)} frozen alpha summaries")
    for row in rows:
        print(
            f"alpha={float(row['alpha']):.2f} "
            f"J_HLS={float(row['J_HLS']):.12f} "
            f"J_SEP_max={float(row['J_SEP_max']):.12f} "
            f"Phi={float(row['Phi']):.12f} "
            f"{row['regime']}"
        )


if __name__ == "__main__":
    main()
