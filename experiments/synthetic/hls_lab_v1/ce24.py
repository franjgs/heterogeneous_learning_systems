"""Deterministic, small CE-24 train/evaluate experiment for HLS Lab v1.

This is a finite model experiment, not a stochastic sample.  The seed is
recorded for trace compatibility; v1's simulator consumes no random stream.
The output directory is create-only to protect earlier runs.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.discover_v0 import JOINT_ACTIONS, production_inputs  # noqa: E402
from hls.hls_lab_v1 import (  # noqa: E402
    EpisodeRecord,
    ExploreThenGreedy,
    FixedRouting,
    GreedyAdaptive,
    ProblemSpec,
    RunResult,
    TeamState,
    complementarity_class,
    evaluate_problem,
    feasible_actions,
    make_team,
    run_sequence,
    episode_record_to_dict,
)
from experiments.synthetic.campaign0_discriminative_capacity.run import ETA  # noqa: E402

SEED = 20261014  # recorded only; no random API is used by the simulator
TRAIN_CYCLES = 10
EVAL_CYCLES = 4
ETA_V1 = ETA
REFERENCE_STATE = ((1.0, 0.0), (0.0, 1.0), (0.0, 0.0))
REFERENCE_TEAM = make_team(REFERENCE_STATE)
TRAIN_TYPES = ("A", "B")
ALL_TYPES = ("A", "B", "C", "D")


def problem(problem_id: str, *, reverse_actions: bool = False) -> ProblemSpec:
    """Predeclared analytic contexts; requirements/budgets from CE-22 fixtures."""
    specs = {
        "A": ((0.8, 0.0), 1.0),       # E0 can satisfy it alone
        "B": ((0.0, 0.8), 1.0),       # E1 can satisfy it alone
        "C": ((0.8, 0.8), 2.0),       # team-only at the common budget
        "D": ((0.95, 0.95), 1.0),     # infeasible under this budget
    }
    requirements, budget = specs[problem_id]
    allowed = None
    if reverse_actions:
        canonical = ProblemSpec(problem_id, requirements, budget)
        allowed = tuple(reversed(feasible_actions(canonical)))
    return ProblemSpec(problem_id, requirements, budget,
                       allowed_actions=allowed, resource_cost_per_unit=0.0)


def make_training_sequence(*, reverse_actions: bool = False) -> tuple[ProblemSpec, ...]:
    """Ten A/B visits each: exactly exhaust each context's 10 feasible arms."""
    return tuple(problem(kind, reverse_actions=reverse_actions)
                 for _ in range(TRAIN_CYCLES) for kind in TRAIN_TYPES)


def make_evaluation_sequence(*, reverse_actions: bool = False) -> tuple[ProblemSpec, ...]:
    """Fresh episode objects for known A/B contexts plus C/D negative controls."""
    familiar = tuple(problem(kind, reverse_actions=reverse_actions)
                     for _ in range(EVAL_CYCLES) for kind in TRAIN_TYPES)
    controls = tuple(problem(kind, reverse_actions=reverse_actions) for kind in ("C", "D"))
    return familiar + controls


def _rank_action(team: TeamState, item: ProblemSpec, action):
    result = evaluate_problem(production_inputs(team.real_matrix, action), item.requirements)
    effort = sum(sum(row) for row in action)
    return (int(result.success), -result.normalized_deficit, result.margin, -effort)


def exact_context_oracle() -> dict[str, tuple[tuple[float, float], ...]]:
    """Exact per-context reference over the same feasible action set/budget."""
    assignments = {}
    for kind in ALL_TYPES:
        item = problem(kind)
        actions = feasible_actions(item)
        best_score = max(_rank_action(REFERENCE_TEAM, item, action) for action in actions)
        assignments[kind] = next(action for action in actions
                                 if _rank_action(REFERENCE_TEAM, item, action) == best_score)
    return assignments


def experiment_results(*, output_dir: Path) -> tuple[list[dict], list[dict], dict]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_rows: list[dict] = []
    groups: list[tuple[str, str, bool, bool, str, RunResult]] = []
    train_sequence = make_training_sequence()
    eval_sequence = make_evaluation_sequence()

    # The four LI×LO cells use one training stream each.  Reset evaluation
    # estimates a controlled post-training policy on the common reference team;
    # carryover evaluation separately retains acquired competencies.
    for li in (False, True):
        for lo in (False, True):
            label = f"LI{int(li)}_LO{int(lo)}"
            learner = ExploreThenGreedy()
            training = run_sequence(REFERENCE_TEAM, train_sequence, learner,
                                    eta=ETA_V1, individual_learning=li,
                                    organizational_learning=lo, seed=SEED)
            groups.append(("factorial", label, li, lo, "TRAIN", training))
            reset_eval = run_sequence(REFERENCE_TEAM, eval_sequence, learner,
                                      eta=ETA_V1, individual_learning=False,
                                      organizational_learning=False, seed=SEED,
                                      initial_organization_state=training.final_organization)
            groups.append(("factorial", label, li, lo, "EVAL_RESET", reset_eval))
            carry_eval = run_sequence(training.final_team, eval_sequence, learner,
                                      eta=ETA_V1, individual_learning=False,
                                      organizational_learning=False, seed=SEED,
                                      initial_organization_state=training.final_organization)
            groups.append(("factorial", label, li, lo, "EVAL_CARRYOVER", carry_eval))

    # Predeclared action-order sensitivity. The action set is unchanged; only
    # catalogue order/tie-breaking and the learner's first untried arm differ.
    for lo in (False, True):
        label = f"REVERSED_ORDER_LO{int(lo)}"
        learner = ExploreThenGreedy()
        reversed_train = run_sequence(REFERENCE_TEAM, make_training_sequence(reverse_actions=True), learner,
                                      eta=ETA_V1, individual_learning=False,
                                      organizational_learning=lo, seed=SEED)
        groups.append(("order_sensitivity", label, False, lo, "TRAIN", reversed_train))
        reversed_eval = run_sequence(REFERENCE_TEAM,
                                     make_evaluation_sequence(reverse_actions=True), learner,
                                     eta=ETA_V1, individual_learning=False,
                                     organizational_learning=False, seed=SEED,
                                     initial_organization_state=reversed_train.final_organization)
        groups.append(("order_sensitivity", label, False, lo, "EVAL_RESET", reversed_eval))

    # Same-state reference baselines. The fixed/oracle mapping is calculated
    # before runs by exhaustive enumeration; GreedyAdaptive sees exact ŝ=s.
    oracle = exact_context_oracle()
    fixed = FixedRouting(oracle, name="fixed_context_oracle")
    greedy = GreedyAdaptive()
    for policy_name, policy in (("FIXED_CONTEXT_ORACLE", fixed), ("GREEDY_ADAPTIVE", greedy)):
        run = run_sequence(REFERENCE_TEAM, eval_sequence, policy,
                           eta=ETA_V1, individual_learning=False,
                           organizational_learning=False, seed=SEED)
        groups.append(("reference_baseline", policy_name, False, False, "EVAL_RESET", run))

    # Machine-readable episode records preserve full before/after θ and state.
    for experiment, label, li, lo, phase, run in groups:
        for record in run.records:
            row = episode_record_to_dict(record)
            row.update({"experiment": experiment, "condition": label,
                        "individual_learning_training": li,
                        "organizational_learning_training": lo,
                        "phase": phase, "policy": run.policy})
            raw_rows.append(row)

    summaries = []
    for experiment, label, li, lo, phase, run in groups:
        records = run.records
        successes = sum(int(r.success) for r in records)
        distinct_by_context = {}
        for r in records:
            distinct_by_context.setdefault(r.problem_id, set()).add(r.action_id)
        summaries.append({
            "experiment": experiment, "condition": label, "phase": phase,
            "policy": run.policy, "LI_training": li, "LO_training": lo,
            "episodes": len(records), "successes": successes,
            "success_rate": successes / len(records),
            "mean_normalized_deficit": sum(r.normalized_deficit for r in records) / len(records),
            "mean_effort": sum(r.effort for r in records) / len(records),
            "total_effort": sum(r.effort for r in records),
            "resource_cost": sum(r.resource_cost for r in records),
            "unique_actions_by_context": json.dumps(
                {k: len(v) for k, v in sorted(distinct_by_context.items())}, sort_keys=True),
            "theta_updates": run.final_organization.update_count,
            "initial_competencies": json.dumps(REFERENCE_TEAM.real_matrix),
            "phase_final_competencies": json.dumps(run.final_team.real_matrix),
        })

    domain_audit = {}
    for kind in ALL_TYPES:
        item = problem(kind)
        actions = feasible_actions(item)
        successes = [JOINT_ACTIONS.index(a) for a in actions
                     if evaluate_problem(production_inputs(REFERENCE_TEAM.real_matrix, a),
                                         item.requirements).success]
        domain_audit[kind] = {
            "requirements": item.requirements,
            "budget": item.resource_budget,
            "feasible_action_count": len(actions),
            "successful_action_ids": successes,
            "complementarity_class": complementarity_class(REFERENCE_TEAM, item),
        }
    manifest = {
        "protocol": "HLS-LAB-CE24-v1",
        "execution_command": "PYTHONPATH=src:. python experiments/synthetic/hls_lab_v1/ce24.py",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "seed_recorded_only_not_consumed": SEED,
        "eta_from_campaign0_reference": ETA_V1,
        "initial_team": REFERENCE_TEAM.real_matrix,
        "training_cycles_per_context": TRAIN_CYCLES,
        "training_sequence": [p.problem_id for p in train_sequence],
        "evaluation_sequence": [p.problem_id for p in eval_sequence],
        "evaluation_cycles_per_known_context": EVAL_CYCLES,
        "evaluation_contains_untrained_controls": ["C", "D"],
        "full_joint_action_catalog_count": len(JOINT_ACTIONS),
        "domain_audit": domain_audit,
        "exact_context_oracle_action_ids": {
            key: JOINT_ACTIONS.index(value) for key, value in oracle.items()},
        "metric_note": "No statistical intervals: simulator and design are deterministic; seeds do not alter trajectories.",
        "groups": len(groups),
        "episode_records": len(raw_rows),
    }

    episodes_path = output_dir / "episodes.jsonl"
    with episodes_path.open("w", encoding="utf-8") as stream:
        for row in raw_rows:
            stream.write(json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")
    summary_path = output_dir / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(summaries)
    problem_path = output_dir / "problem_metrics.csv"
    problem_rows = []
    for row in raw_rows:
        selected = {key: row[key] for key in (
            "experiment", "condition", "phase", "policy", "problem_id", "action_id",
            "requirements", "outputs", "success", "normalized_deficit", "effort",
            "resource_cost", "competence_before", "competence_after",
            "organization_updated")}
        problem_rows.append({key: json.dumps(value, separators=(",", ":"), allow_nan=False)
                             if isinstance(value, (tuple, list, dict)) else value
                             for key, value in selected.items()})
    with problem_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(problem_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(problem_rows)

    manifest["code_provenance"] = {
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                                 capture_output=True, text=True).stdout.strip(),
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (ROOT / "src/hls/hls_lab_v1.py",
                                       ROOT / "experiments/synthetic/hls_lab_v1/ce24.py",
                                       ROOT / "tests/test_hls_lab_v1_ce24.py") if path.exists()},
    }
    manifest["output_sha256"] = {
        name: hashlib.sha256((output_dir / name).read_bytes()).hexdigest()
        for name in ("episodes.jsonl", "summary.csv", "problem_metrics.csv")}
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return raw_rows, summaries, manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/experiments/hls_lab_ce24")
    args = parser.parse_args()
    rows, summaries, manifest = experiment_results(output_dir=args.output_dir)
    print(json.dumps({"output_dir": str(args.output_dir), "rows": len(rows),
                      "summary_rows": len(summaries), "manifest": manifest}, indent=2,
                     sort_keys=True))


if __name__ == "__main__":
    main()
