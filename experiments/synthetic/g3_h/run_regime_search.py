"""Run the adversarial G3-H existence search for USE/local regret."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.g3_h_regime_map import REGIME_TOL  # noqa: E402
from hls.g3_h_regime_search import SearchResult, local_refinement, positive, search  # noqa: E402


OUTPUT = ROOT / "results" / "foundations" / "g3_h_regime_search"
G3H = ROOT / "src" / "hls" / "g3_h_organizational_value.py"
REGIME_MAP = ROOT / "src" / "hls" / "g3_h_regime_map.py"
SEARCH = ROOT / "src" / "hls" / "g3_h_regime_search.py"
RUNNER = Path(__file__).resolve()
SEED = 20261005
STAGES = (("smoke", 2_000), ("medium", 20_000), ("large", 50_000))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _action(action: tuple[int, int]) -> list[int]:
    return [action[0] + 1, action[1] + 1]


def _actions(actions: frozenset[tuple[int, int]]) -> str:
    return json.dumps([_action(action) for action in sorted(actions)])


def _state_columns(prefix: str, state) -> dict[str, float]:
    return {
        f"{prefix}_w1_a": state[0][0], f"{prefix}_w1_b": state[0][1],
        f"{prefix}_w2_a": state[1][0], f"{prefix}_w2_b": state[1][1],
        f"{prefix}_w3_a": state[2][0], f"{prefix}_w3_b": state[2][1],
    }


def _point_row(condition: str, objective: str, stage: str, result: SearchResult, evaluation) -> dict[str, object]:
    row: dict[str, object] = {
        "condition": condition,
        "objective": objective,
        "stage": stage,
        "samples": result.samples,
        "seed": result.seed,
        "eta_1": evaluation.learning_profile[0],
        "eta_2": evaluation.learning_profile[1],
        "eta_3": evaluation.learning_profile[2],
        "A_U_star": _actions(evaluation.optimal_use),
        "A_L_star": _actions(evaluation.optimal_local),
        "A_Q_star": _actions(evaluation.optimal_dynamic),
        "regime": evaluation.regime,
        "R2_REVERSION": evaluation.r2_reversion,
        "J_star": evaluation.j_star,
        "J_U": evaluation.j_use,
        "J_L": evaluation.j_local,
        "regret_U": evaluation.regret_use,
        "regret_L": evaluation.regret_local,
    }
    row.update(_state_columns("s", evaluation.state))
    return row


def _action_rows(candidate_id: str, evaluation) -> list[dict[str, object]]:
    rows = []
    for observation in evaluation.actions:
        row: dict[str, object] = {
            "candidate_id": candidate_id,
            "action_a_worker_1based": observation.action[0] + 1,
            "action_b_worker_1based": observation.action[1] + 1,
            "R": observation.reward,
            "D": observation.development,
            "M": observation.local_value,
            "Q": observation.dynamic_value,
            "operational_gap": observation.operational_gap,
        }
        row.update(_state_columns("successor", observation.successor))
        rows.append(row)
    return rows


def _write_csv(rows: list[dict[str, object]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(*, output: Path = OUTPUT, stages=STAGES) -> dict[str, object]:
    """Run homogeneous then heterogeneous existence search; stop a condition after a positive result."""
    output.mkdir(parents=True, exist_ok=True)
    all_results: dict[str, list[tuple[str, SearchResult]]] = {"homogeneous": [], "heterogeneous": []}
    candidates: list[dict[str, object]] = []
    action_rows: list[dict[str, object]] = []
    refinements: list[dict[str, object]] = []
    for condition_index, condition in enumerate(("homogeneous", "heterogeneous")):
        for stage_index, (stage, samples) in enumerate(stages):
            result = search(condition=condition, samples=samples, seed=SEED + 10_000 * condition_index + stage_index)
            all_results[condition].append((stage, result))
            for objective, evaluation in (("regret_U", result.best_use), ("regret_L", result.best_local)):
                candidate_id = f"{condition}_{stage}_{objective}"
                candidates.append(_point_row(condition, objective, stage, result, evaluation) | {"candidate_id": candidate_id})
                action_rows.extend(_action_rows(candidate_id, evaluation))
            if positive(result):
                for objective_index, (objective, center, regret) in enumerate((
                    ("regret_U", result.best_use, result.best_use.regret_use),
                    ("regret_L", result.best_local, result.best_local.regret_local),
                )):
                    if regret <= REGIME_TOL:
                        continue
                    refinement = local_refinement(
                        center,
                        condition=condition,
                        samples=1_000,
                        seed=SEED + 20_000 * condition_index + 100 * stage_index + objective_index,
                    )
                    refinements.append({
                        "condition": condition,
                        "objective": objective,
                        "stage": stage,
                        "samples": refinement.samples,
                        "runtime_seconds": refinement.runtime_seconds,
                        "best_regret_U": refinement.best_use.regret_use,
                        "best_regret_L": refinement.best_local.regret_local,
                        "positive_regret_U_count": refinement.positive_use_count,
                        "positive_regret_L_count": refinement.positive_local_count,
                    })
                break

    def best(condition: str, objective: str):
        evaluations = [result.best_use if objective == "regret_U" else result.best_local for _, result in all_results[condition]]
        return max(evaluations, key=lambda item: item.regret_use if objective == "regret_U" else item.regret_local)

    summary = {
        "experiment_id": "g3_h_adversarial_regime_existence_search",
        "deterministic": True,
        "tolerance": REGIME_TOL,
        "sampler": {
            "state": "independent uniform interior samples in (1e-6, 1-1e-6)^6",
            "eta": "independent Exponential(rate=1) samples with support [0, infinity)",
            "prevalence_interpretation": False,
        },
        "seed": SEED,
        "stages": {
            condition: [
                {
                    "stage": stage, "samples": result.samples, "runtime_seconds": result.runtime_seconds,
                    "state_observed_range": [result.state_min, result.state_max],
                    "eta_observed_range": [result.eta_min, result.eta_max],
                    "max_regret_U": result.best_use.regret_use,
                    "max_regret_L": result.best_local.regret_local,
                    "positive_regret_U_count": result.positive_use_count,
                    "positive_regret_L_count": result.positive_local_count,
                }
                for stage, result in results
            ]
            for condition, results in all_results.items()
        },
        "objectives": {
            condition: {
                "max_regret_U": best(condition, "regret_U").regret_use,
                "max_regret_L": best(condition, "regret_L").regret_local,
            }
            for condition in all_results
        },
        "refinements": refinements,
    }
    candidates_path = output / "best_candidates.csv"
    actions_path = output / "counterexample_actions.csv"
    summary_path = output / "search_summary.json"
    _write_csv(candidates, candidates_path)
    _write_csv(action_rows, actions_path)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "experiment_id": summary["experiment_id"],
        "command": "python experiments/synthetic/g3_h/run_regime_search.py",
        "repository_commit_at_run": _git("rev-parse", "HEAD"),
        "working_tree_dirty_at_run": bool(_git("status", "--porcelain")),
        "seed": SEED,
        "stages": list(stages),
        "tolerance": REGIME_TOL,
        "g3h_evaluator_sha256": _sha256(G3H),
        "regime_map_sha256": _sha256(REGIME_MAP),
        "search_sha256": _sha256(SEARCH),
        "runner_sha256": _sha256(RUNNER),
        "summary_sha256": _sha256(summary_path),
        "best_candidates_sha256": _sha256(candidates_path),
        "counterexample_actions_sha256": _sha256(actions_path),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--smoke", action="store_true", help="run only the first 2,000-sample stage")
    args = parser.parse_args()
    summary = run(output=args.output, stages=STAGES[:1] if args.smoke else STAGES)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
