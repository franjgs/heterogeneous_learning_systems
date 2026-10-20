"""CE-16 Small Problem World functional-resolution diagnostic.

Run with ``PYTHONPATH=src:. python experiments/synthetic/functional_problem_ce16/run.py``.
The output directory is immutable-by-default: an existing target is never
overwritten. This is a fixed six-problem, four-team, four-mode, ten-seed run.
"""

from __future__ import annotations

import csv
import hashlib
import json
import argparse
import signal
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.discover_develop_v0 import (  # noqa: E402
    DEVELOP_KNOWN, DISCOVER_DEVELOP, DISCOVER_ONLY, STATIC_KNOWN,
)
from hls.discover_v0 import DEFAULT_SIGMA  # noqa: E402
from hls.finite_problem_belief import run_finite_problem_sequence  # noqa: E402
from hls.functional_problem import observe_trajectory_requirements  # noqa: E402
from hls.small_problem_world import (  # noqa: E402
    HORIZON, HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR, WORLD, requirements_for_problem,
)
from experiments.synthetic.campaign0_discriminative_capacity.run import (  # noqa: E402
    ETA, HISTORIES, SEEDS, TEAMS, validate_protocol,
)


OUT = ROOT / "results/experiments/functional_problem_ce16"
POLICIES = (DISCOVER_DEVELOP, DISCOVER_ONLY, DEVELOP_KNOWN, STATIC_KNOWN)
POLICY_LABELS = {
    DISCOVER_DEVELOP: "DISCOVER+DEVELOP (belief; MIS-v2)",
    DISCOVER_ONLY: "DISCOVER_ONLY (belief; no development)",
    DEVELOP_KNOWN: "DEVELOP_KNOWN (known problem; MIS-v2)",
    STATIC_KNOWN: "STATIC_KNOWN (known problem; no development)",
}
REQUIREMENTS_BY_PROBLEM = {
    stage.problem: stage.requirements for stage in WORLD[:5]
}


def _json(value) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _append_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _max_abs_state_difference(left, right) -> float:
    return max(abs(float(left[i][k]) - float(right[i][k])) for i in range(3) for k in range(2))


def reproduce_campaign0_reference() -> dict:
    """Replay one frozen Campaign-0 cell as an engineering control."""
    reference_dir = ROOT / "results/diagnostics/campaign0_discriminative_capacity"
    with (reference_dir / "runs.csv").open(newline="", encoding="utf-8") as handle:
        frozen_run = next(row for row in csv.DictReader(handle)
                          if row["team"] == "G00" and row["history"] == "H0" and row["seed"] == "0")
    with (reference_dir / "trajectories.csv").open(newline="", encoding="utf-8") as handle:
        frozen_rows = [row for row in csv.DictReader(handle)
                       if row["team"] == "G00" and row["history"] == "H0" and row["seed"] == "0"]
    original_problems = HISTORIES["H0"]
    replay = run_finite_problem_sequence(
        TEAMS["G00"], original_problems, HYPOTHESIS_REPERTOIRE,
        prior=UNIFORM_PRIOR, mode=DISCOVER_DEVELOP, eta=ETA,
        horizon=HORIZON, seed=0,
    )
    if len(replay) != 18 or len(frozen_rows) != 18:
        raise AssertionError("Campaign-0 reference replay has unexpected length")
    errors = {"state_after": 0.0, "belief_after": 0.0, "action_mismatch_count": 0,
              "mu_true": 0.0, "observed_reward": 0.0, "cumulative": 0.0}
    for step, row in zip(replay, frozen_rows):
        errors["state_after"] = max(errors["state_after"], _max_abs_state_difference(
            step.state_after, json.loads(row["S_after"])))
        errors["belief_after"] = max(errors["belief_after"], max(
            abs(a - b) for a, b in zip(step.belief_after, json.loads(row["belief_after"]))))
        errors["action_mismatch_count"] += int(
            [list(pair) for pair in step.action] != json.loads(row["action"]))
        errors["mu_true"] = max(errors["mu_true"], abs(step.true_mean - float(row["mu_true"])))
        errors["observed_reward"] = max(errors["observed_reward"],
                                        abs(step.observed_reward - float(row["observed_reward"])))
        errors["cumulative"] = max(errors["cumulative"],
                                   abs(step.cumulative_reward - float(row["cumulative_performance"])))
    tolerance = 1e-12
    passed = (errors["action_mismatch_count"] == 0
              and all(value <= tolerance for key, value in errors.items() if key != "action_mismatch_count")
              and abs(replay[-1].cumulative_reward - float(frozen_run["cumulative_performance"])) <= tolerance)
    if not passed:
        raise AssertionError(f"Campaign-0 historical replay failed: {errors}")
    return {"cell": "G00/H0/seed0/DISCOVER+DEVELOP", "decisions": len(replay),
            "absolute_tolerance": tolerance, "max_discrepancies": errors,
            "stored_cumulative": float(frozen_run["cumulative_performance"]),
            "replayed_cumulative": replay[-1].cumulative_reward, "passed": True}


def execute(on_cell_done=None, cell_filter=None) -> tuple[list[dict], list[dict], list[dict], list[dict], dict]:
    validate_protocol()
    if tuple(stage.label for stage in WORLD) != ("A", "A'", "B", "B'", "C", "A"):
        raise AssertionError("Small Problem World sequence changed")
    if set(POLICIES) != {DISCOVER_DEVELOP, DISCOVER_ONLY, DEVELOP_KNOWN, STATIC_KNOWN}:
        raise AssertionError("unexpected Campaign-0 policy modes")

    run_rows: list[dict] = []
    trajectory_rows: list[dict] = []
    recurrence_rows: list[dict] = []
    for team_id, initial_state in TEAMS.items():
        for policy in POLICIES:
            for seed in SEEDS:
                if cell_filter is not None and (team_id, policy, seed) not in cell_filter:
                    continue
                steps = run_finite_problem_sequence(
                    initial_state, tuple(stage.problem for stage in WORLD), HYPOTHESIS_REPERTOIRE,
                    prior=UNIFORM_PRIOR, mode=policy, eta=ETA,
                    horizon=HORIZON, seed=seed,
                )
                annotations = observe_trajectory_requirements(steps, REQUIREMENTS_BY_PROBLEM)
                if len(steps) != 18 or len(annotations) != 18:
                    raise AssertionError("unexpected decision or annotation count")
                rows: list[dict] = []
                grouped: dict[int, list[tuple[object, object]]] = defaultdict(list)
                for step, annotation in zip(steps, annotations):
                    grouped[step.problem_id].append((step, annotation))
                    stage = WORLD[step.problem_id]
                    row = {
                        "team_id": team_id, "policy": policy, "policy_label": POLICY_LABELS[policy],
                        "seed": seed, "problem_id": step.problem_id, "problem_label": stage.label,
                        "within_problem_step": step.step_id,
                        "CES_weights": _json(step.true_problem),
                        "S_before": _json(step.state_before), "action": _json(step.action),
                        "production_Y": _json(annotation.outputs),
                        "requirements_r": _json(annotation.requirements),
                        "functional_success": int(annotation.evaluation.met),
                        "deficit_by_dimension": _json(annotation.evaluation.deficits),
                        "normalized_total_deficit": annotation.evaluation.normalized_total_deficit,
                        "assigned_effort": annotation.effort,
                        "CES_reward_mu_true": step.true_mean,
                        "observed_reward": step.observed_reward,
                        "belief_before": _json(step.belief_before),
                        "belief_after": _json(step.belief_after),
                        "S_after": _json(step.state_after),
                        "cumulative_CES_reward": step.cumulative_reward,
                    }
                    rows.append(row)
                    trajectory_rows.append(row)

                problem_successes = sum(
                    any(annotation.evaluation.met for _, annotation in grouped[index])
                    for index in range(len(WORLD))
                )
                total_ces = sum(step.true_mean for step in steps)
                final_state = steps[-1].state_after
                run_rows.append({
                    "team_id": team_id, "policy": policy, "seed": seed,
                    "problems_satisfied": problem_successes,
                    "problem_satisfaction_rate": problem_successes / len(WORLD),
                    "decision_satisfaction_rate": sum(int(a.evaluation.met) for a in annotations) / len(annotations),
                    "mean_normalized_deficit": statistics.mean(a.evaluation.normalized_total_deficit for a in annotations),
                    "cumulative_CES_reward": total_ces,
                    "initial_competence_total": sum(sum(x) for x in initial_state),
                    "final_competence_total": sum(sum(x) for x in final_state),
                    "competence_gain_total": sum(sum(final_state[i][k] - initial_state[i][k]
                                                      for k in range(2)) for i in range(3)),
                    "final_S": _json(final_state),
                })

                first_a = grouped[0]
                last_a = grouped[5]
                first_success = any(a.evaluation.met for _, a in first_a)
                last_success = any(a.evaluation.met for _, a in last_a)
                first_reward = sum(step.true_mean for step, _ in first_a)
                last_reward = sum(step.true_mean for step, _ in last_a)
                recurrence_rows.append({
                    "team_id": team_id, "policy": policy, "seed": seed,
                    "first_A_success": int(first_success), "last_A_success": int(last_success),
                    "first_A_decision_success_rate": sum(int(a.evaluation.met) for _, a in first_a) / HORIZON,
                    "last_A_decision_success_rate": sum(int(a.evaluation.met) for _, a in last_a) / HORIZON,
                    "first_A_mean_deficit": statistics.mean(a.evaluation.normalized_total_deficit for _, a in first_a),
                    "last_A_mean_deficit": statistics.mean(a.evaluation.normalized_total_deficit for _, a in last_a),
                    "first_A_CES_reward": first_reward, "last_A_CES_reward": last_reward,
                    "delta_last_minus_first_A_CES": last_reward - first_reward,
                    "S_before_first_A": _json(first_a[0][0].state_before),
                    "S_before_last_A": _json(last_a[0][0].state_before),
                    "S_after_first_A": _json(first_a[-1][0].state_after),
                    "S_after_last_A": _json(last_a[-1][0].state_after),
                })
                if on_cell_done is not None:
                    on_cell_done(team_id, policy, seed, run_rows[-1], rows, recurrence_rows[-1])

    # CRN audit: infer standardized observation innovations and compare modes.
    innovation_groups: dict[tuple[str, int, int], list[float]] = defaultdict(list)
    for row in trajectory_rows:
        innovation = (float(row["observed_reward"]) - float(row["CES_reward_mu_true"])) / DEFAULT_SIGMA
        innovation_groups[(row["team_id"], row["seed"], row["problem_id"] * HORIZON + row["within_problem_step"])].append(innovation)
    crn_max_difference = max(max(values) - min(values) for values in innovation_groups.values())
    if crn_max_difference > 1e-12:
        raise AssertionError(f"CRN innovations differ across policy modes: {crn_max_difference}")

    return run_rows, trajectory_rows, recurrence_rows, [], {
        "run_count": len(run_rows), "trajectory_count": len(trajectory_rows),
        "CRN_max_innovation_difference": crn_max_difference,
        "CRN_policy_innovations_aligned": crn_max_difference <= 1e-12,
    }


def aggregate(run_rows: list[dict], trajectory_rows: list[dict], recurrence_rows: list[dict]):
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in run_rows:
        grouped[(row["team_id"], row["policy"])].append(row)
    summary = []
    for (team, policy), rows in sorted(grouped.items()):
        summary.append({
            "team_id": team, "policy": policy, "histories": len(rows),
            "mean_problems_satisfied": statistics.mean(r["problems_satisfied"] for r in rows),
            "problem_satisfaction_rate": statistics.mean(r["problem_satisfaction_rate"] for r in rows),
            "decision_satisfaction_rate": statistics.mean(r["decision_satisfaction_rate"] for r in rows),
            "mean_normalized_deficit": statistics.mean(r["mean_normalized_deficit"] for r in rows),
            "mean_cumulative_CES": statistics.mean(r["cumulative_CES_reward"] for r in rows),
            "mean_final_competence_total": statistics.mean(r["final_competence_total"] for r in rows),
            "mean_competence_gain_total": statistics.mean(r["competence_gain_total"] for r in rows),
        })

    by_problem: dict[tuple[str, str, int, str], list[dict]] = defaultdict(list)
    for row in trajectory_rows:
        by_problem[(row["team_id"], row["policy"], row["problem_id"], row["problem_label"])].append(row)
    problem_summary = []
    for (team, policy, problem_id, label), rows in sorted(by_problem.items()):
        problem_summary.append({
            "team_id": team, "policy": policy, "problem_id": problem_id,
            "problem_label": label, "decision_count": len(rows),
            "decision_satisfaction_rate": statistics.mean(int(r["functional_success"]) for r in rows),
            "mean_normalized_deficit": statistics.mean(float(r["normalized_total_deficit"]) for r in rows),
            "mean_CES_reward": statistics.mean(float(r["CES_reward_mu_true"]) for r in rows),
        })

    paired = []
    for team in TEAMS:
        for left_index, left_policy in enumerate(POLICIES):
            for right_policy in POLICIES[left_index + 1:]:
                for seed in SEEDS:
                    left = next((r for r in run_rows if r["team_id"] == team and r["policy"] == left_policy and r["seed"] == seed), None)
                    right = next((r for r in run_rows if r["team_id"] == team and r["policy"] == right_policy and r["seed"] == seed), None)
                    if left is None or right is None:
                        continue
                    paired.append({
                        "team_id": team, "seed": seed,
                        "policy_left": left_policy, "policy_right": right_policy,
                        "delta_satisfied_problems_left_minus_right": left["problems_satisfied"] - right["problems_satisfied"],
                        "delta_CES_left_minus_right": left["cumulative_CES_reward"] - right["cumulative_CES_reward"],
                        "delta_mean_deficit_left_minus_right": left["mean_normalized_deficit"] - right["mean_normalized_deficit"],
                    })
    return summary, problem_summary, paired


def _report(summary: list[dict], problem_summary: list[dict], recurrence: list[dict]) -> str:
    lines = [
        "# CE-16 — Functional problem resolution diagnostic", "",
        "This is a fixed descriptive evaluation, not a new campaign or population estimate. "
        "A problem stage counts as satisfied if at least one of its three decisions meets both registered requirements. "
        "Decision-level rates and deficits are also retained. Each policy receives the same problem sequence and seed; "
        "the modes differ in information and/or planning/development and are not interchangeable causal treatments.", "",
        "## Aggregate by team and mode", "",
        "| Team | Mode | Mean satisfied of 6 | Decision pass rate | Mean normalized deficit | Mean cumulative CES | Mean competence gain |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(f"| {row['team_id']} | {row['policy']} | {row['mean_problems_satisfied']:.2f} | "
                     f"{row['decision_satisfaction_rate']:.3f} | {row['mean_normalized_deficit']:.3f} | "
                     f"{row['mean_cumulative_CES']:.4f} | {row['mean_competence_gain_total']:.4f} |")
    lines += ["", "## First versus recurring A", "",
              "Paired within a team, mode, and seed. This contrast includes the intervening problems, policy choices, "
              "beliefs, and capability trajectory; it does not isolate the causal effect of MIS-v2.", "",
              "| Team | Mode | Mean Δ CES (last−first A) | First A success | Last A success | Δ mean deficit (last−first) |",
              "|---|---|---:|---:|---:|---:|"]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in recurrence:
        groups[(row["team_id"], row["policy"])].append(row)
    for (team, policy), rows in sorted(groups.items()):
        lines.append(f"| {team} | {policy} | {statistics.mean(r['delta_last_minus_first_A_CES'] for r in rows):.4f} | "
                     f"{statistics.mean(r['first_A_success'] for r in rows):.2f} | "
                     f"{statistics.mean(r['last_A_success'] for r in rows):.2f} | "
                     f"{statistics.mean(r['last_A_mean_deficit']-r['first_A_mean_deficit'] for r in rows):.4f} |")
    lines += ["", "## Interpretation limits", "",
              "The modes include uncertain-belief and known-problem controls, and learning/no-learning variants; "
              "pairing matches seed-level observation-noise innovations, not the endogenous observations or trajectories. "
              "CES and functional compliance are distinct outcomes. Cross-team contrasts are descriptive because initial "
              "competence geometry differs. A-versus-A recurrence is a path comparison, not an MIS-only effect. "
              "The four teams, one six-stage sequence, ten seeds, action set, and requirement rule bound all conclusions.", ""]
    return "\n".join(lines)


def finalize_partial(final_status="INCOMPLETE", failure_message=None, extra_provenance=None) -> None:
    """Finalize persisted rows after the alarm, without running simulations."""
    if not OUT.exists():
        raise FileNotFoundError(OUT)

    def read_rows(name: str, numeric: set[str], integer: set[str] = frozenset()):
        path = OUT / name
        if not path.exists():
            return []
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            for key in numeric:
                if key in row and row[key] != "":
                    row[key] = float(row[key])
            for key in integer:
                if key in row and row[key] != "":
                    row[key] = int(row[key])
        return rows

    run_rows = read_rows("runs.csv", {
        "problem_satisfaction_rate", "decision_satisfaction_rate", "mean_normalized_deficit",
        "cumulative_CES_reward", "initial_competence_total", "final_competence_total",
        "competence_gain_total",
    }, {"seed", "problems_satisfied"})
    trajectories = read_rows("functional_trajectories.csv", {
        "normalized_total_deficit", "assigned_effort", "CES_reward_mu_true", "observed_reward",
        "cumulative_CES_reward",
    }, {"seed", "problem_id", "within_problem_step", "functional_success"})
    recurrence = read_rows("A_first_last_comparison.csv", {
        "first_A_decision_success_rate", "last_A_decision_success_rate", "first_A_mean_deficit",
        "last_A_mean_deficit", "first_A_CES_reward", "last_A_CES_reward",
        "delta_last_minus_first_A_CES",
    }, {"seed", "first_A_success", "last_A_success"})
    summary, problem_summary, paired = aggregate(run_rows, trajectories, recurrence) if run_rows else ([], [], [])
    if summary:
        _write_csv(OUT / "aggregate_by_team_policy.csv", summary)
        _write_csv(OUT / "compliance_by_problem.csv", problem_summary)
        _write_csv(OUT / "paired_policy_differences.csv", paired)
        (OUT / "report.md").write_text(_report(summary, problem_summary, recurrence), encoding="utf-8")

    expected_keys = {(team, policy, seed) for team in TEAMS for policy in POLICIES for seed in SEEDS}
    keys = [(r["team_id"], r["policy"], r["seed"]) for r in run_rows]
    status_path = OUT / "execution_status.json"
    prior = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else {}
    status = {
        **prior, "status": final_status, "expected_cells": len(expected_keys),
        "completed_cells": len(keys), "unique_cells": len(set(keys)),
        "completed_decisions": len(trajectories),
        "missing_cells": [list(key) for key in sorted(expected_keys - set(keys))],
        "failure": failure_message,
        "post_timeout_finalization": "persisted CSV rows parsed and summarized; no simulation executed",
    }
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    source_paths = (
        Path(__file__), ROOT / "src/hls/finite_problem_belief.py", ROOT / "src/hls/functional_problem.py",
        ROOT / "src/hls/small_problem_world.py", ROOT / "src/hls/discover_develop_v0.py",
        ROOT / "src/hls/discover_develop_v2.py",
        ROOT / "experiments/synthetic/campaign0_discriminative_capacity/run.py",
    )
    input_paths = tuple(ROOT / p for p in (
        "results/diagnostics/campaign0_discriminative_capacity/runs.csv",
        "results/diagnostics/campaign0_discriminative_capacity/trajectories.csv",
        "results/diagnostics/campaign0_discriminative_capacity/manifest.json",
    ))
    output_paths = sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "manifest.json")
    manifest = {
        "protocol": "HLS-CE-16-functional-problem-diagnostic-v1", "status": final_status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "finalization_only": True, "resume_provenance": extra_provenance,
        "source_commit": __import__("subprocess").check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "design": {"teams": TEAMS, "problems": [(s.label, s.problem, s.requirements) for s in WORLD],
                   "policies": POLICIES, "seeds": SEEDS, "eta": ETA, "horizon_per_problem": HORIZON,
                   "prior": UNIFORM_PRIOR, "hypothesis_repertoire": HYPOTHESIS_REPERTOIRE,
                   "requirements_source": "CE-15 G00 initial attainable frontier, r=L*z"},
        "counts": status,
        "source_sha256": {str(p.relative_to(ROOT)): _sha256(p) for p in source_paths},
        "campaign0_input_sha256": {str(p.relative_to(ROOT)): _sha256(p) for p in input_paths},
        "output_sha256": {p.name: _sha256(p) for p in output_paths},
        "limitations": ["partial factorial; no full-factorial inference", "modes differ in information/planning",
                        "one fixed sequence and four teams"],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": final_status, "completed_cells": len(keys),
                      "completed_decisions": len(trajectories), "manifest_sha256": _sha256(OUT / "manifest.json")}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--finalize-partial", action="store_true",
                        help="summarize already persisted incomplete rows without executing simulations")
    parser.add_argument("--resume-missing", action="store_true",
                        help="execute only absent team-policy-seed cells in the existing output directory")
    args = parser.parse_args()
    if args.finalize_partial:
        finalize_partial()
        return
    if args.resume_missing:
        if not OUT.exists():
            raise FileNotFoundError(f"cannot resume; output directory is missing: {OUT}")
        original_bytes = {}
        original_hashes = {}
        for name in ("runs.csv", "functional_trajectories.csv", "A_first_last_comparison.csv"):
            path = OUT / name
            original_bytes[name] = path.read_bytes()
            original_hashes[name] = hashlib.sha256(original_bytes[name]).hexdigest()
        with (OUT / "runs.csv").open(newline="", encoding="utf-8") as handle:
            prior_runs = list(csv.DictReader(handle))
        prior_keys = {(r["team_id"], r["policy"], int(r["seed"])) for r in prior_runs}
        expected_keys = {(team, policy, seed) for team in TEAMS for policy in POLICIES for seed in SEEDS}
        if len(prior_runs) != 137 or len(prior_keys) != 137 or prior_keys - expected_keys:
            raise AssertionError("existing result cells do not match the verified 137-cell baseline")
        intended = {
            ("G07", DISCOVER_ONLY, seed) for seed in (7, 8, 9)
        } | {
            ("G07", DEVELOP_KNOWN, seed) for seed in SEEDS
        } | {
            ("G07", STATIC_KNOWN, seed) for seed in SEEDS
        }
        missing = expected_keys - prior_keys
        if missing != intended:
            raise AssertionError(f"missing-cell set differs from CE-19 authorization: {sorted(missing ^ intended)}")
        if not reproduce_campaign0_reference()["passed"]:
            raise AssertionError("historical Campaign-0 replay failed")
        started = time.monotonic()
        deadline_hit = False
        failure = None
        new_cells = 0

        def on_cell_done(team_id, policy, seed, run_row, rows, recurrence_row):
            nonlocal new_cells
            _append_csv(OUT / "runs.csv", [run_row])
            _append_csv(OUT / "functional_trajectories.csv", rows)
            _append_csv(OUT / "A_first_last_comparison.csv", [recurrence_row])
            new_cells += 1
            print(f"CE-19 progress {new_cells}/{len(missing)}: team={team_id} policy={policy} seed={seed}", flush=True)

        def time_limit(_signum, _frame):
            raise TimeoutError("CE-19 reached its 30-minute operational limit")

        signal.signal(signal.SIGALRM, time_limit)
        signal.alarm(30 * 60)
        try:
            execute(on_cell_done=on_cell_done, cell_filter=missing)
        except TimeoutError as exc:
            deadline_hit, failure = True, str(exc)
        except Exception as exc:
            failure = f"{type(exc).__name__}: {exc}"
        finally:
            signal.alarm(0)

        for name, before in original_bytes.items():
            if not (OUT / name).read_bytes().startswith(before):
                raise AssertionError(f"previously completed data were modified: {name}")
        with (OUT / "runs.csv").open(newline="", encoding="utf-8") as handle:
            all_runs = list(csv.DictReader(handle))
        all_keys = [(r["team_id"], r["policy"], int(r["seed"])) for r in all_runs]
        complete = len(all_keys) == 160 and len(set(all_keys)) == 160 and set(all_keys) == expected_keys
        validation = {"cells_160_unique": complete}
        with (OUT / "functional_trajectories.csv").open(newline="", encoding="utf-8") as handle:
            all_trajectories = list(csv.DictReader(handle))
        validation["decisions_2880"] = len(all_trajectories) == 2880
        per_cell = defaultdict(int)
        requirements = defaultdict(set)
        innovations = defaultdict(list)
        valid_seeds = True
        for row in all_trajectories:
            key = (row["team_id"], row["policy"], int(row["seed"]))
            per_cell[key] += 1
            valid_seeds &= int(row["seed"]) in SEEDS
            requirements[row["problem_label"]].add(row["requirements_r"])
            location = (row["team_id"], int(row["seed"]), int(row["problem_id"]), int(row["within_problem_step"]))
            innovations[location].append((float(row["observed_reward"]) - float(row["CES_reward_mu_true"])) / DEFAULT_SIGMA)
        validation["18_decisions_per_cell"] = len(per_cell) == 160 and all(v == 18 for v in per_cell.values())
        validation["seeds_0_to_9_only"] = valid_seeds
        validation["requirements_constant_by_problem"] = all(len(v) == 1 for v in requirements.values()) and len(requirements) == 5
        crn_spreads = [max(v) - min(v) for v in innovations.values() if len(v) > 1]
        crn_max = max(crn_spreads) if crn_spreads else float("inf")
        validation["CRN_aligned"] = crn_max <= 1e-12
        validation["CRN_max_innovation_difference"] = crn_max
        validation["historical_replay_passed"] = reproduce_campaign0_reference()["passed"]
        complete = complete and all(v for k, v in validation.items() if k != "CRN_max_innovation_difference")
        final_status = "COMPLETE" if complete and failure is None else "INCOMPLETE" if deadline_hit else "FAILED"
        if final_status == "COMPLETE":
            # Full-data checks are performed by the finalizer's count and requirement audits.
            failure = None
        elif failure is None:
            failure = "resume ended before all authorized cells were completed"
        finalize_partial(final_status, failure, {
            "baseline_cells": 137, "baseline_file_sha256": original_hashes,
            "authorized_cells": len(missing), "newly_completed_cells": new_cells,
            "limit_seconds": 1800, "elapsed_seconds": time.monotonic() - started,
            "validation": validation,
        })
        if final_status != "COMPLETE":
            raise SystemExit(2)
        return
    if OUT.exists():
        raise FileExistsError(f"output directory already exists; refusing to overwrite: {OUT}")
    replay = reproduce_campaign0_reference()
    OUT.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    completed_cells = 0
    (OUT / "execution_status.json").write_text(json.dumps({
        "status": "RUNNING", "expected_cells": 160, "completed_cells": 0,
        "historical_replay": replay,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def save_cell(team_id, policy, seed, run_row, trajectory_cell, recurrence_row):
        nonlocal completed_cells
        _append_csv(OUT / "runs.csv", [run_row])
        _append_csv(OUT / "functional_trajectories.csv", trajectory_cell)
        _append_csv(OUT / "A_first_last_comparison.csv", [recurrence_row])
        completed_cells += 1
        status = {
            "status": "RUNNING", "expected_cells": 160,
            "completed_cells": completed_cells,
            "completed_decisions": completed_cells * 18,
            "last_completed_cell": {"team_id": team_id, "policy": policy, "seed": seed},
            "elapsed_seconds": time.monotonic() - started,
            "historical_replay": replay,
        }
        (OUT / "execution_status.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"CE-16 progress {completed_cells}/160: team={team_id} policy={policy} seed={seed}", flush=True)

    timed_out = False
    failure = None

    def time_limit(_signum, _frame):
        raise TimeoutError("CE-16 reached its 60-minute operational limit")

    signal.signal(signal.SIGALRM, time_limit)
    signal.alarm(60 * 60)
    try:
        run_rows, trajectories, recurrence, _, audits = execute(on_cell_done=save_cell)
    except TimeoutError as exc:
        timed_out = True
        failure = str(exc)
        run_rows, trajectories, recurrence = [], [], []
        for name, target in (("runs.csv", run_rows),
                             ("functional_trajectories.csv", trajectories),
                             ("A_first_last_comparison.csv", recurrence)):
            path = OUT / name
            if path.exists():
                with path.open(newline="", encoding="utf-8") as handle:
                    target.extend(csv.DictReader(handle))
        audits = {"run_count": len(run_rows), "trajectory_count": len(trajectories),
                  "CRN_policy_innovations_aligned": None,
                  "CRN_max_innovation_difference": None}
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        run_rows, trajectories, recurrence = [], [], []
        if (OUT / "runs.csv").exists():
            with (OUT / "runs.csv").open(newline="", encoding="utf-8") as handle:
                run_rows = list(csv.DictReader(handle))
        if (OUT / "functional_trajectories.csv").exists():
            with (OUT / "functional_trajectories.csv").open(newline="", encoding="utf-8") as handle:
                trajectories = list(csv.DictReader(handle))
        if (OUT / "A_first_last_comparison.csv").exists():
            with (OUT / "A_first_last_comparison.csv").open(newline="", encoding="utf-8") as handle:
                recurrence = list(csv.DictReader(handle))
        audits = {"run_count": len(run_rows), "trajectory_count": len(trajectories),
                  "CRN_policy_innovations_aligned": None,
                  "CRN_max_innovation_difference": None}
    finally:
        signal.alarm(0)

    complete = not timed_out and failure is None and len(run_rows) == 160 and len(trajectories) == 2880
    observed_keys = [(r["team_id"], r["policy"], int(r["seed"])) for r in run_rows]
    expected_keys = [(team, policy, seed) for team in TEAMS for policy in POLICIES for seed in SEEDS]
    if len(observed_keys) != len(set(observed_keys)):
        failure = failure or "duplicate team-policy-seed cells detected"
        complete = False
    missing_keys = sorted(set(expected_keys) - set(observed_keys))
    if complete and missing_keys:
        failure = "factorial cells missing after nominal completion"
        complete = False
    if trajectories and any(len({row["requirements_r"] for row in trajectories if row["problem_label"] == label}) != 1
                            for label in ("A", "A'", "B", "B'", "C")):
        failure = failure or "requirements differ within a registered problem type"
        complete = False
    summary, problem_summary, paired = aggregate(run_rows, trajectories, recurrence) if run_rows else ([], [], [])
    if summary:
        _write_csv(OUT / "aggregate_by_team_policy.csv", summary)
    if problem_summary:
        _write_csv(OUT / "compliance_by_problem.csv", problem_summary)
    if paired:
        _write_csv(OUT / "paired_policy_differences.csv", paired)
    if summary:
        (OUT / "report.md").write_text(_report(summary, problem_summary, recurrence), encoding="utf-8")
    source_paths = (
        Path(__file__), ROOT / "src/hls/finite_problem_belief.py",
        ROOT / "src/hls/functional_problem.py", ROOT / "src/hls/small_problem_world.py",
        ROOT / "src/hls/discover_develop_v0.py", ROOT / "src/hls/discover_develop_v2.py",
        ROOT / "experiments/synthetic/campaign0_discriminative_capacity/run.py",
    )
    input_paths = (
        ROOT / "results/diagnostics/campaign0_discriminative_capacity/runs.csv",
        ROOT / "results/diagnostics/campaign0_discriminative_capacity/trajectories.csv",
        ROOT / "results/diagnostics/campaign0_discriminative_capacity/manifest.json",
    )
    status_name = "COMPLETE" if complete else "INCOMPLETE" if timed_out else "FAILED"
    status = {"status": status_name, "expected_cells": 160, "completed_cells": len(run_rows),
              "completed_decisions": len(trajectories), "missing_cells": missing_keys,
              "unique_cells": len(set(observed_keys)), "elapsed_seconds": time.monotonic() - started,
              "failure": failure, "historical_replay": replay, **audits}
    (OUT / "execution_status.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_paths = sorted(path for path in OUT.iterdir() if path.is_file() and path.name != "manifest.json")
    manifest = {
        "protocol": "HLS-CE-16-functional-problem-diagnostic-v1",
        "status": status_name, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": __import__("subprocess").check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "design": {"teams": TEAMS, "problems": [(stage.label, stage.problem, stage.requirements) for stage in WORLD],
                   "policies": POLICIES, "seeds": SEEDS, "eta": ETA, "horizon_per_problem": HORIZON,
                   "prior": UNIFORM_PRIOR, "hypothesis_repertoire": HYPOTHESIS_REPERTOIRE,
                   "requirements_source": "CE-15 G00 initial attainable frontier, r=L*z",
                   "problem_success_rule": "at least one of three decisions meets both requirements",
                   "effort_semantics": "sum of action allocations; not economic cost",
                   "CRN": "same seed; one standard-normal observation innovation at every corresponding decision"},
        "counts": {**status, "team_policy_seed_cells_expected": 160,
                   "expected_decisions": 2880, "paired_policy_contrasts": len(paired)},
        "controls": {"campaign0_reference_replay": replay,
                     "observer_is_post_action_and_not_a_policy_input": True,
                     "campaign0_historical_artifacts_overwritten": False},
        "source_sha256": {str(path.relative_to(ROOT)): _sha256(path) for path in source_paths},
        "campaign0_input_sha256": {str(path.relative_to(ROOT)): _sha256(path) for path in input_paths},
        "output_sha256": {path.name: _sha256(path) for path in output_paths},
        "limitations": ["modes differ in information/planning; not pure isolated treatments",
                        "one fixed six-stage sequence and four teams",
                        "no inference to a broader problem or team population"],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "counts": manifest["counts"],
                      "historical_replay_passed": replay["passed"],
                      "manifest_sha256": _sha256(OUT / "manifest.json")}, indent=2))
    if not complete:
        raise SystemExit(2 if timed_out else 1)


if __name__ == "__main__":
    main()
