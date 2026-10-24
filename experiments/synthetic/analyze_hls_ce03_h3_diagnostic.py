"""Read-only diagnostic analysis of the already completed HLS-CE-03 run."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.stats import t


DEFAULT_DIR = Path("results/experiments/hls_ce03_h3_transfer")
TASKS = ("T1_linear", "T2_nonlinear", "T3_interactions")
AGENTS = ("A1_logistic", "A2_random_forest", "A3_mlp")
CONTROL = "control1_and_control2_identical_hard_label_refit"


def _summary(values: list[float]) -> dict[str, float | int]:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.isfinite(x).all():
        raise ValueError("need at least two finite paired seed-level observations")
    mean = float(np.mean(x))
    sd = float(np.std(x, ddof=1))
    half = float(t.ppf(0.975, df=len(x) - 1) * sd / np.sqrt(len(x)))
    return {
        "n_seeds": int(len(x)), "mean": mean, "median": float(np.median(x)), "sd": sd,
        "ci95_low": mean - half, "ci95_high": mean + half,
        "positive": int(np.sum(x > 0)), "negative": int(np.sum(x < 0)),
        "zero": int(np.sum(x == 0)), "minimum": float(np.min(x)), "maximum": float(np.max(x)),
    }


def _accuracy_matrix(error_matrix):
    return {task: {agent: 1.0 - error_matrix[task][agent] for agent in AGENTS} for task in TASKS}


def _rank_assignments(accuracy_matrix):
    candidates = []
    for assignment in itertools.permutations(AGENTS):
        score = float(np.mean([
            accuracy_matrix[task][agent] for task, agent in zip(TASKS, assignment)
        ]))
        tie_key = tuple(AGENTS.index(agent) for agent in assignment)
        candidates.append((score, tie_key, assignment))
    return sorted(candidates, key=lambda item: (-item[0], item[1]))


def analyze(results_dir: Path = DEFAULT_DIR) -> dict:
    result_path = results_dir / "results.json"
    raw_bytes = result_path.read_bytes()
    raw_hash = hashlib.sha256(raw_bytes).hexdigest()
    manifest = json.loads((results_dir / "manifest.json").read_text())
    if raw_hash != manifest["result_sha256"]:
        raise ValueError("raw campaign result hash does not match manifest")
    raw = json.loads(raw_bytes)
    if [run["seed"] for run in raw["runs"]] != list(range(20)):
        raise ValueError("expected exactly seeds 0 through 19")

    rows = []
    assignment_rows = []
    pre_accuracy_by_agent_task = {agent: {task: [] for task in TASKS} for agent in AGENTS}
    post_a1_val_deltas = {task: [] for task in TASKS}
    assignment_frequencies = {"O0": {}, "O1": {}}
    for run in raw["runs"]:
        seed = int(run["seed"])
        pre = _accuracy_matrix(run["validation_loss_matrix_initial"])
        post = _accuracy_matrix(run["validation_loss_matrix_post_transfer"])
        pre_rank = _rank_assignments(pre)
        post_rank = _rank_assignments(post)
        o0 = tuple(run["O0_initial_validation_optimum"][task] for task in TASKS)
        o1 = tuple(run["O1_post_transfer_validation_optimum"][task] for task in TASKS)
        if o0 != pre_rank[0][2] or o1 != post_rank[0][2]:
            raise ValueError(f"recorded assignment does not match validation matrix at seed {seed}")
        o0_key = "|".join(o0)
        o1_key = "|".join(o1)
        assignment_frequencies["O0"][o0_key] = assignment_frequencies["O0"].get(o0_key, 0) + 1
        assignment_frequencies["O1"][o1_key] = assignment_frequencies["O1"].get(o1_key, 0) + 1

        for agent in AGENTS:
            for task in TASKS:
                pre_accuracy_by_agent_task[agent][task].append(pre[task][agent])
        for task in TASKS:
            post_a1_val_deltas[task].append(post[task]["A1_logistic"] - pre[task]["A1_logistic"])

        best_pre, second_pre = pre_rank[:2]
        best_post, second_post = post_rank[:2]
        post_o0_score = next(item[0] for item in post_rank if item[2] == o0)
        c0 = run["conditions_test"]["C0_no_transfer_fixed_O0"]
        c1 = run["conditions_test"]["C1_transfer_fixed_O0"]
        hard_control = run["control_test_metrics_A1"][CONTROL]
        row = {
            "seed": seed,
            "O0": json.dumps(dict(zip(TASKS, o0)), sort_keys=True),
            "O1": json.dumps(dict(zip(TASKS, o1)), sort_keys=True),
            "O0_equals_O1": o0 == o1,
            "responsibilities_changed": run["number_of_responsibilities_changed"],
            "pre_best_val_accuracy": best_pre[0],
            "pre_runner_up_val_accuracy": second_pre[0],
            "pre_best_minus_runnerup_pp": 100.0 * (best_pre[0] - second_pre[0]),
            "post_best_val_accuracy": best_post[0],
            "post_runner_up_val_accuracy": second_post[0],
            "post_best_minus_runnerup_pp": 100.0 * (best_post[0] - second_post[0]),
            "post_O0_regret_vs_O1_pp": 100.0 * (best_post[0] - post_o0_score),
            "A3_minus_initial_A1_T3_validation_pp": 100.0 * (pre["T3_interactions"]["A3_mlp"] - pre["T3_interactions"]["A1_logistic"]),
        }
        for task in TASKS:
            row[f"A1_{task}_validation_pre"] = pre[task]["A1_logistic"]
            row[f"A1_{task}_validation_post"] = post[task]["A1_logistic"]
            row[f"A1_{task}_validation_delta_pp"] = 100.0 * post_a1_val_deltas[task][-1]
            row[f"A1_{task}_test_initial"] = run["A1_individual_test_metrics_before"][task]["accuracy"]
            row[f"A1_{task}_test_distilled"] = run["A1_individual_test_metrics_after_distillation"][task]["accuracy"]
            row[f"A1_{task}_test_hard_refit"] = hard_control[task]["accuracy"]
            row[f"A1_{task}_test_distilled_minus_refit_pp"] = 100.0 * (
                run["A1_individual_test_metrics_after_distillation"][task]["accuracy"] - hard_control[task]["accuracy"]
            )
            row[f"assigned_collective_{task}_C1_minus_C0_pp"] = 100.0 * (
                c1["accuracy_by_task"][task] - c0["accuracy_by_task"][task]
            )
        if o0[2] == "A3_mlp":
            # C0's T3 test score is A3's only where the validation-selected O0 assigns A3 to T3.
            row["A3_T3_test_accuracy_observed_under_O0"] = c0["accuracy_by_task"]["T3_interactions"]
            row["A3_minus_initial_A1_T3_test_pp_observed_under_O0"] = 100.0 * (
                c0["accuracy_by_task"]["T3_interactions"]
                - run["A1_individual_test_metrics_before"]["T3_interactions"]["accuracy"]
            )
        else:
            row["A3_T3_test_accuracy_observed_under_O0"] = ""
            row["A3_minus_initial_A1_T3_test_pp_observed_under_O0"] = ""
        rows.append(row)

        for rank, (score, _tie_key, assignment) in enumerate(pre_rank, start=1):
            score_post = next(item[0] for item in post_rank if item[2] == assignment)
            assignment_rows.append({
                "seed": seed, "rank_pre": rank,
                "assignment": json.dumps(dict(zip(TASKS, assignment)), sort_keys=True),
                "pre_validation_mean_accuracy": score,
                "post_validation_mean_accuracy": score_post,
                "post_minus_pre_pp": 100.0 * (score_post - score),
            })

    def each_agent_task_summary(matrix):
        return {
            agent: {task: _summary(values) for task, values in by_task.items()}
            for agent, by_task in matrix.items()
        }

    donor_val_gap = [row["A3_minus_initial_A1_T3_validation_pp"] for row in rows]
    donor_test_subset = [
        float(row["A3_minus_initial_A1_T3_test_pp_observed_under_O0"])
        for row in rows if row["A3_minus_initial_A1_T3_test_pp_observed_under_O0"] != ""
    ]
    margins_pre = [row["pre_best_minus_runnerup_pp"] for row in rows]
    margins_post = [row["post_best_minus_runnerup_pp"] for row in rows]
    post_o0_regret = [row["post_O0_regret_vs_O1_pp"] for row in rows]
    summary = {
        "validation_accuracy_by_agent_and_task": each_agent_task_summary(pre_accuracy_by_agent_task),
        "A1_validation_accuracy_change_by_task_pp": {
            task: _summary([100.0 * value for value in values])
            for task, values in post_a1_val_deltas.items()
        },
        "A3_minus_initial_A1_T3_validation_pp": _summary(donor_val_gap),
        "A3_minus_initial_A1_T3_test_pp_when_O0_selected_A3_for_T3": _summary(donor_test_subset),
        "O0_assignment_counts": assignment_frequencies["O0"],
        "O1_assignment_counts": assignment_frequencies["O1"],
        "O0_equals_O1_seeds": sum(row["O0_equals_O1"] for row in rows),
        "best_vs_runnerup_validation_margin_pp": {
            "pre_transfer": _summary(margins_pre), "post_transfer": _summary(margins_post),
            "post_minus_pre": _summary([b-a for a, b in zip(margins_pre, margins_post)]),
        },
        "post_transfer_validation_regret_of_retaining_O0_vs_O1_pp": _summary(post_o0_regret),
        "A1_test_distilled_minus_initial_by_task_pp": {
            task: _summary([100.0 * (row[f"A1_{task}_test_distilled"] - row[f"A1_{task}_test_initial"]) for row in rows])
            for task in TASKS
        },
        "A1_test_distilled_minus_hard_refit_by_task_pp": {
            task: _summary([row[f"A1_{task}_test_distilled_minus_refit_pp"] for row in rows])
            for task in TASKS
        },
        "fixed_organization_assigned_task_change_C1_minus_C0_pp": {
            task: _summary([row[f"assigned_collective_{task}_C1_minus_C0_pp"] for row in rows])
            for task in TASKS
        },
    }
    return {
        "source_results": "results.json; read-only, no model fitting or inference",
        "source_sha256": raw_hash,
        "campaign_commit": manifest["git_head"],
        "seeds": list(range(20)),
        "summary": summary,
        "per_seed": rows,
        "six_assignment_validation_utilities": assignment_rows,
        "limitations": [
            "A3 individual test metrics are not stored for all seeds; its test score is available only for the 18 seeds where O0 assigned A3 to T3.",
            "All agents were initially trained on the same pooled labeled data, including the same T3 training examples later used for transfer; transfer therefore adds no new labeled examples to A1.",
            "Teacher probabilities are in-sample for A3 on T3 training examples.",
            "The result artifact stores validation error matrices and A1/control test metrics, but not the full individual test matrix for every agent/task.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()
    result = analyze(args.results_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "diagnostic_analysis.json"
    seed_path = args.output_dir / "diagnostic_by_seed.csv"
    assignment_path = args.output_dir / "assignment_utilities_by_seed.csv"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    for path, records in ((seed_path, result["per_seed"]), (assignment_path, result["six_assignment_validation_utilities"])):
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(records)
    (args.output_dir / "diagnostic_manifest.json").write_text(json.dumps({
        "source_results_sha256": result["source_sha256"],
        "diagnostic_analysis_sha256": hashlib.sha256(json_path.read_bytes()).hexdigest(),
        "diagnostic_by_seed_sha256": hashlib.sha256(seed_path.read_bytes()).hexdigest(),
        "assignment_utilities_by_seed_sha256": hashlib.sha256(assignment_path.read_bytes()).hexdigest(),
        "analysis_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "analysis_git_head": subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True,
        ).stdout.strip(),
        "command": "python experiments/synthetic/analyze_hls_ce03_h3_diagnostic.py",
        "models_trained_or_invoked": False,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
