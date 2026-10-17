"""CE-25 deterministic mechanism decomposition for HLS Laboratory v1.

This runner reuses v1's frozen problem, production, feasibility, functional
evaluation, MIS-v2, and ExploreThenGreedy implementations. It adds only the
protocol-level exploration schedule and trace accounting needed to compare
reward-blind cycling with reward-informed selection.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Iterable

from hls.discover_develop_v2 import mis_v2_transition
from hls.discover_v0 import JOINT_ACTIONS, JointAction, production_inputs
from hls.hls_lab_v1 import (
    DecisionView, ExploreThenGreedy, ExpertState, OrganizationState, ProblemSpec,
    TeamState, evaluate_problem, feasible_actions, make_team,
)

ROOT = Path(__file__).resolve().parents[3]
ETA = 0.35
SEED_METADATA = 20261025  # v1 is deterministic; this is provenance only.
REFERENCE_TEAM = make_team(((1.0, 0.0), (0.0, 1.0), (0.0, 0.0)))
AB_ORDER_FAMILIES = (
    "CANONICAL", "REVERSE", "BALANCED_A_FIRST_B_LAST",
    "BALANCED_A_LAST_B_FIRST", "SUCCESS_FIRST", "SUCCESS_LAST",
)
AB_EVAL_HORIZONS = (1, 10, 20)  # decisions/context, K=10 legal actions/context
C_EVAL_HORIZONS = (1, 37, 74)   # decisions, K=37 legal actions in C
POLICIES = ("FIXED", "MEMORY_ONLY", "EXPLORATION_ONLY", "LEARNED")


def problem(context: str, order: tuple[JointAction, ...] | None = None) -> ProblemSpec:
    specs = {
        "A": ((0.8, 0.0), 1.0),
        "B": ((0.0, 0.8), 1.0),
        "C": ((0.8, 0.8), 2.0),
        "D": ((0.95, 0.95), 1.0),
        "EQ": ((0.1, 0.1), 1.0),
    }
    requirements, budget = specs[context]
    return ProblemSpec(context, requirements, budget, allowed_actions=order)


def successful_action(context: str) -> JointAction:
    ids = {"A": 48, "B": 4, "C": 52}
    return JOINT_ACTIONS[ids[context]]


def move_action_to_rank(actions: tuple[JointAction, ...], action: JointAction,
                        one_based_rank: int) -> tuple[JointAction, ...]:
    """Place one identified action at a fixed rank, preserving other order."""
    if action not in actions or not 1 <= one_based_rank <= len(actions):
        raise ValueError("action/rank is outside the declared action sequence")
    remainder = [candidate for candidate in actions if candidate != action]
    remainder.insert(one_based_rank - 1, action)
    return tuple(remainder)


def ab_orders(family: str) -> dict[str, tuple[JointAction, ...]]:
    """Six declared paired order profiles; no outcome-selected permutations."""
    if family not in AB_ORDER_FAMILIES:
        raise ValueError(f"unknown A/B order family: {family}")
    base = {key: feasible_actions(problem(key)) for key in ("A", "B")}
    if family == "CANONICAL":
        return base
    if family == "REVERSE":
        return {key: tuple(reversed(value)) for key, value in base.items()}
    k = len(base["A"])
    if family == "BALANCED_A_FIRST_B_LAST":
        ranks = {"A": 1, "B": k}
    elif family == "BALANCED_A_LAST_B_FIRST":
        ranks = {"A": k, "B": 1}
    elif family == "SUCCESS_FIRST":
        ranks = {"A": 1, "B": 1}
    else:  # SUCCESS_LAST
        ranks = {"A": k, "B": k}
    return {key: move_action_to_rank(base[key], successful_action(key), ranks[key])
            for key in ("A", "B")}


def c_order(success_rank: int) -> tuple[JointAction, ...]:
    base = feasible_actions(problem("C"))
    return move_action_to_rank(base, successful_action("C"), success_rank)


def training_sequence(contexts: tuple[str, ...], orders: dict[str, tuple[JointAction, ...]]) -> tuple[ProblemSpec, ...]:
    sizes = {context: len(orders[context]) for context in contexts}
    result = []
    for index in range(max(sizes.values())):
        for context in contexts:
            if index < sizes[context]:
                result.append(problem(context, orders[context]))
    return tuple(result)


def repeated_sequence(contexts: tuple[str, ...], orders: dict[str, tuple[JointAction, ...]],
                      horizon: int) -> tuple[ProblemSpec, ...]:
    return tuple(problem(context, orders[context])
                 for _ in range(horizon) for context in contexts)


def equivalent_outcome_actions() -> tuple[JointAction, JointAction]:
    """Two frozen actions spending one unit on distinct skills of null expert E2."""
    selected = []
    for action in JOINT_ACTIONS:
        if action[0] == (0.0, 0.0) and action[1] == (0.0, 0.0) and action[2] in ((0.0, 1.0), (1.0, 0.0)):
            selected.append(action)
    if len(selected) != 2:
        raise AssertionError("expected the two unit actions on the zero-capability expert")
    return tuple(selected)  # type: ignore[return-value]


@dataclass
class ControllerState:
    theta: OrganizationState = field(default_factory=OrganizationState)
    cursor: dict[str, int] = field(default_factory=dict)
    memory_log: list[tuple[str, int, float]] = field(default_factory=list)


def _decision_view(spec: ProblemSpec, team: TeamState) -> DecisionView:
    actions = feasible_actions(spec)
    return DecisionView(spec.problem_id, spec.requirements, spec.difficulty,
                        spec.orientation, spec.resource_budget,
                        team.estimated_matrix, actions)


def _select(policy: str, phase: str, spec: ProblemSpec, team: TeamState,
            state: ControllerState, learner: ExploreThenGreedy) -> tuple[JointAction, bool, int]:
    actions = feasible_actions(spec)
    context = spec.problem_id
    cursor_before = state.cursor.get(context, 0)
    if policy in {"FIXED", "MEMORY_ONLY"}:
        return actions[0], False, cursor_before
    if policy == "EXPLORATION_ONLY":
        action = actions[cursor_before % len(actions)]
        state.cursor[context] = cursor_before + 1
        return action, True, cursor_before
    if policy != "LEARNED":
        raise ValueError(f"unknown CE-25 policy {policy}")
    view = _decision_view(spec, team)
    if phase == "TRAIN":
        # Existing ExploreThenGreedy supplies the declared untried-arm sweep.
        action = learner.choose(view, state.theta)
        state.cursor[context] = cursor_before + 1
        return action, True, cursor_before
    # Training is complete (K visits/context) in the confirmatory contrasts;
    # unseen contexts deliberately have no transferable row and choose first.
    return learner.choose(view, state.theta), False, cursor_before


def _step(policy: str, phase: str, spec: ProblemSpec, team: TeamState,
          state: ControllerState, learner: ExploreThenGreedy, *,
          individual_learning: bool, feedback_mode: str, episode: int) -> tuple[dict[str, object], TeamState]:
    action, schedule_driven, cursor_before = _select(policy, phase, spec, team, state, learner)
    if action not in feasible_actions(spec):
        raise AssertionError("selected action violates the shared feasibility constraints")
    s_before = team.real_matrix
    individual_outputs = tuple(tuple(action[i][k] * s_before[i][k] for k in range(2))
                               for i in range(3))
    outputs = production_inputs(s_before, action)
    functional = evaluate_problem(outputs, spec.requirements)
    effort = sum(sum(row) for row in action)
    experience_before = tuple(expert.experience for expert in team.experts)
    performance_before = tuple(expert.performance for expert in team.experts)
    updated_experience = tuple(tuple(experience_before[i][k] + action[i][k] for k in range(2))
                               for i in range(3))
    updated_performance = tuple(tuple(performance_before[i][k] + individual_outputs[i][k]
                                      for k in range(2)) for i in range(3))
    s_after = mis_v2_transition(s_before, action, enabled=individual_learning, eta=ETA)
    next_team = TeamState(tuple(
        ExpertState(team.experts[i].expert_id, s_after[i], s_after[i],
                    updated_experience[i], updated_performance[i]) for i in range(3)))

    physical_reward = float(functional.success)
    observed_label = physical_reward
    if feedback_mode not in {"TRUE", "INVERTED"}:
        raise ValueError("feedback_mode must be TRUE or INVERTED")
    if feedback_mode == "INVERTED" and policy == "LEARNED" and phase == "TRAIN":
        observed_label = 1.0 - physical_reward
    theta_before = state.theta.values
    memory_before_count = len(state.memory_log)
    updated = False
    action_id = JOINT_ACTIONS.index(action)
    if phase == "TRAIN" and policy in {"LEARNED", "MEMORY_ONLY", "EXPLORATION_ONLY"}:
        state.memory_log.append((spec.problem_id, action_id, physical_reward))
    if phase == "TRAIN" and policy == "LEARNED":
        state.theta = learner.observe(state.theta, spec.problem_id, action,
                                      observed_label, enabled=True)
        updated = True
    elif phase == "TRAIN" and policy == "MEMORY_ONLY":
        # It persists observations but selection never reads theta.
        state.theta = learner.observe(state.theta, spec.problem_id, action,
                                      physical_reward, enabled=True)
    memory_after_count = len(state.memory_log)
    theta_changed = state.theta.values != theta_before
    row = {
        "phase": phase, "episode": episode, "problem_id": spec.problem_id,
        "requirements": spec.requirements, "budget": spec.resource_budget,
        "action_id": action_id, "action": action, "schedule_driven": schedule_driven,
        "cursor_before": cursor_before,
        "cursor_after": state.cursor.get(spec.problem_id, cursor_before),
        "outputs": outputs, "individual_outputs": individual_outputs,
        "success": functional.success, "normalized_deficit": functional.normalized_deficit,
        "margin": functional.margin, "effort": effort,
        "resource_cost": effort * spec.resource_cost_per_unit,
        "competence_before": s_before, "competence_after": next_team.real_matrix,
        "experience_before": experience_before,
        "experience_after": tuple(expert.experience for expert in next_team.experts),
        "theta_before": theta_before, "theta_after": state.theta.values,
        "theta_updated": updated, "memory_state_changed": theta_changed,
        "memory_observation_count_before": memory_before_count,
        "memory_observation_count_after": memory_after_count,
        "physical_reward": physical_reward,
        "label_used_for_learning": observed_label,
        "feedback_mode": feedback_mode,
    }
    return row, next_team


def run_condition(policy: str, train: tuple[ProblemSpec, ...], evaluation: tuple[ProblemSpec, ...],
                  *, individual_learning: bool = False, feedback_mode: str = "TRUE",
                  eval_state: str = "RESET", trial_id: str = "") -> list[dict[str, object]]:
    """Run a fresh controller, with frozen θ and LI during the evaluation phase."""
    learner = ExploreThenGreedy()
    state = ControllerState()
    team = REFERENCE_TEAM
    rows: list[dict[str, object]] = []
    for index, spec in enumerate(train):
        row, team = _step(policy, "TRAIN", spec, team, state, learner,
                          individual_learning=individual_learning,
                          feedback_mode=feedback_mode, episode=index)
        row.update({"policy": policy, "trial_id": trial_id, "seed_metadata": SEED_METADATA})
        rows.append(row)
    trained_team = team
    eval_team = REFERENCE_TEAM if eval_state == "RESET" else trained_team
    if eval_state not in {"RESET", "CARRYOVER"}:
        raise ValueError("eval_state must be RESET or CARRYOVER")
    theta_at_eval = state.theta.values
    for index, spec in enumerate(evaluation):
        row, eval_team = _step(policy, "EVAL", spec, eval_team, state, learner,
                               individual_learning=False, feedback_mode=feedback_mode,
                               episode=index)
        if state.theta.values != theta_at_eval:
            raise AssertionError("organizational state changed during frozen evaluation")
        row.update({"policy": policy, "trial_id": trial_id, "seed_metadata": SEED_METADATA,
                    "eval_state": eval_state})
        rows.append(row)
    return rows


def _summary(rows: list[dict[str, object]], *, design: dict[str, object]) -> dict[str, object]:
    train = [row for row in rows if row["phase"] == "TRAIN"]
    evaluation = [row for row in rows if row["phase"] == "EVAL"]
    all_rows = train + evaluation
    def metrics(selected: list[dict[str, object]]) -> dict[str, object]:
        return {
            "episodes": len(selected),
            "successes": sum(bool(row["success"]) for row in selected),
            "success_rate": (sum(bool(row["success"]) for row in selected) / len(selected)
                             if selected else None),
            "mean_normalized_deficit": (sum(float(row["normalized_deficit"]) for row in selected) / len(selected)
                                         if selected else None),
            "effort_total": sum(float(row["effort"]) for row in selected),
            "resource_cost_total": sum(float(row["resource_cost"]) for row in selected),
        }
    return {**design, "policy": rows[0]["policy"], "H_train": len(train),
            "H_eval": len(evaluation), "H_total": len(all_rows),
            "train": metrics(train), "eval": metrics(evaluation),
            "total": metrics(all_rows),
            "theta_updates_train": sum(bool(row["theta_updated"]) for row in train),
            "exploration_decisions_train": sum(bool(row["schedule_driven"]) for row in train),
            "exploration_decisions_eval": sum(bool(row["schedule_driven"]) for row in evaluation),
            "unique_actions_train_by_context": {
                context: len({int(row["action_id"]) for row in train if row["problem_id"] == context})
                for context in sorted({str(row["problem_id"]) for row in train})},
            "final_theta": rows[-1]["theta_after"] if rows else ()}


def _trial(trial_id: str, orders: dict[str, tuple[JointAction, ...]], contexts: tuple[str, ...],
           eval_contexts: tuple[str, ...], h_eval: int, policies: Iterable[str], *,
           individual_learning: bool = False, feedback_mode: str = "TRUE",
           eval_state: str = "RESET") -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    training = training_sequence(contexts, orders)
    evaluation = repeated_sequence(eval_contexts, orders, h_eval)
    all_rows: list[dict[str, object]] = []
    summaries = []
    design = {"trial_id": trial_id, "order_family": trial_id.split("|")[1] if "|" in trial_id else "CUSTOM",
              "contexts_train": contexts, "contexts_eval": eval_contexts,
              "eval_cycles_per_context": h_eval, "feedback_mode": feedback_mode,
              "individual_learning_train": individual_learning, "eval_state": eval_state,
              "action_count_by_context": {key: len(value) for key, value in orders.items()},
              "success_rank_by_context": {key: value.index(successful_action(key)) + 1
                                           for key, value in orders.items() if key in {"A", "B", "C"}}
              }
    for policy in policies:
        rows = run_condition(policy, training, evaluation,
                             individual_learning=individual_learning,
                             feedback_mode=feedback_mode, eval_state=eval_state,
                             trial_id=trial_id)
        all_rows.extend(rows)
        summaries.append(_summary(rows, design=design))
    return all_rows, summaries


def run_experiment() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    raw: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []

    # Mechanism contrast, sensitivity, and horizons. Same complete training
    # sweep and order for all four organizations in each cell.
    for family in AB_ORDER_FAMILIES:
        orders = ab_orders(family)
        for horizon in AB_EVAL_HORIZONS:
            trial = f"AB_MAIN|{family}|E{horizon}"
            rows, table = _trial(trial, orders, ("A", "B"), ("A", "B"), horizon, POLICIES)
            raw.extend(rows); summaries.extend(table)

    # Unseen C (and impossible D): train only A/B; no evaluation feedback.
    # The context-unseen control uses the canonical C order. No post-result
    # order selection is permitted; whether its first action solves C is
    # reported as a design coincidence, not interpreted as transfer.
    c_unseen_orders = {**ab_orders("CANONICAL"), "C": c_order(1), "D": feasible_actions(problem("D"))}
    rows, table = _trial("C_UNSEEN|AB_TRAIN", c_unseen_orders, ("A", "B"), ("C", "D"), 10,
                         ("EXPLORATION_ONLY", "LEARNED"))
    raw.extend(rows); summaries.extend(table)

    # Seen complementarity context: exhaustive K=37 train, then repeated eval.
    for rank in (1, 19, 37):
        orders = {"C": c_order(rank)}
        for horizon in C_EVAL_HORIZONS:
            trial = f"C_SEEN|R{rank}|E{horizon}"
            rows, table = _trial(trial, orders, ("C",), ("C",), horizon,
                                 ("EXPLORATION_ONLY", "LEARNED"))
            raw.extend(rows); summaries.extend(table)

    # Equivalent-outcome negative control: two distinct frozen actions, same
    # physical output, success, effort and resource cost under this reference team.
    eq_actions = equivalent_outcome_actions()
    eq_problem = ProblemSpec("EQ", (0.1, 0.1), 1.0, allowed_actions=eq_actions)
    eq_orders = {"EQ": feasible_actions(eq_problem)}
    rows, table = _trial("CONTROL|EQUIVALENT_OUTCOME", eq_orders, ("EQ",), ("EQ",), 2, POLICIES)
    raw.extend(rows); summaries.extend(table)

    # Feedback-decoupling intervention: physical result unchanged; only labels
    # used by LEARNED's TRAIN updater are inverted.
    inv_orders = ab_orders("SUCCESS_LAST")
    train = training_sequence(("A", "B"), inv_orders)
    evaluation = repeated_sequence(("A", "B"), inv_orders, 10)
    for mode in ("TRUE", "INVERTED"):
        trial = f"FEEDBACK|{mode}"
        rows = run_condition("LEARNED", train, evaluation, feedback_mode=mode, trial_id=trial)
        raw.extend(rows)
        summaries.append(_summary(rows, design={"trial_id": trial, "order_family": "SUCCESS_LAST",
            "contexts_train": ("A", "B"), "contexts_eval": ("A", "B"),
            "eval_cycles_per_context": 10, "feedback_mode": mode,
            "individual_learning_train": False, "eval_state": "RESET",
            "action_count_by_context": {"A": 10, "B": 10},
            "success_rank_by_context": {"A": 10, "B": 10}}))

    # LI×LO mechanism check, canonical order; LO OFF is reward-blind cycling,
    # LO ON is the same exploration followed by frozen reward-informed choice.
    for li in (False, True):
        for policy in ("EXPLORATION_ONLY", "LEARNED"):
            trial = f"LI_LO|LI{int(li)}|LO{int(policy == 'LEARNED')}"
            rows, table = _trial(trial, ab_orders("CANONICAL"), ("A", "B"), ("A", "B"), 10,
                                 (policy,), individual_learning=li, eval_state="CARRYOVER")
            raw.extend(rows); summaries.extend(table)
            # Reset-capability evaluation is derived from the same exact TRAIN
            # paths with only the initial evaluation team restored.
            training = training_sequence(("A", "B"), ab_orders("CANONICAL"))
            evaluation = repeated_sequence(("A", "B"), ab_orders("CANONICAL"), 10)
            reset_rows = run_condition(policy, training, evaluation,
                individual_learning=li, eval_state="RESET", trial_id=trial + "|RESET")
            # Keep only EVAL rows: TRAIN is already in the carryover-design run.
            eval_rows = [row for row in reset_rows if row["phase"] == "EVAL"]
            raw.extend(eval_rows)
            summaries.append(_summary(
                [row for row in raw if row.get("trial_id") == trial and row["phase"] == "TRAIN"] + eval_rows,
                design={"trial_id": trial + "|RESET", "order_family": "CANONICAL",
                        "contexts_train": ("A", "B"), "contexts_eval": ("A", "B"),
                        "eval_cycles_per_context": 10, "feedback_mode": "TRUE",
                        "individual_learning_train": li, "eval_state": "RESET",
                        "action_count_by_context": {"A": 10, "B": 10},
                        "success_rank_by_context": {"A": ab_orders("CANONICAL")["A"].index(successful_action("A"))+1,
                                                    "B": ab_orders("CANONICAL")["B"].index(successful_action("B"))+1}}))

    manifest = {
        "protocol": "HLS-LAB-CE25-v1",
        "seed_metadata_only_not_consumed": SEED_METADATA,
        "deterministic": True,
        "core_reuse": ["ProblemSpec", "feasible_actions", "production_inputs", "evaluate_problem",
                       "mis_v2_transition", "ExploreThenGreedy"],
        "primary_paired_contrast": "LEARNED minus EXPLORATION_ONLY",
        "paired_train_action_reward_identity_required": True,
        "orders": list(AB_ORDER_FAMILIES),
        "ab_eval_cycles": list(AB_EVAL_HORIZONS),
        "c_eval_decisions": list(C_EVAL_HORIZONS),
        "raw_records": len(raw), "summary_rows": len(summaries),
        "interpretation": "finite deterministic mechanism check; no population intervals",
    }
    return raw, summaries, manifest


def paired_contrasts(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Summarize predeclared within-design comparisons, without inference."""
    by_trial_policy: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        by_trial_policy.setdefault((str(row["trial_id"]), str(row["policy"])), []).append(row)
    output = []
    trial_ids = sorted({trial for trial, _ in by_trial_policy})
    for trial in trial_ids:
        available = {policy for current, policy in by_trial_policy if current == trial}
        pair = None
        if {"LEARNED", "EXPLORATION_ONLY"} <= available:
            pair = ("LEARNED", "EXPLORATION_ONLY")
        elif {"MEMORY_ONLY", "FIXED"} <= available:
            pair = ("MEMORY_ONLY", "FIXED")
        if pair is None:
            continue
        left, right = (by_trial_policy[(trial, policy)] for policy in pair)
        left_train = [row for row in left if row["phase"] == "TRAIN"]
        right_train = [row for row in right if row["phase"] == "TRAIN"]
        signature = lambda values: [(row["problem_id"], row["action_id"], row["success"],
                                     row["outputs"], row["effort"], row["competence_before"],
                                     row["competence_after"]) for row in values]
        left_eval = [row for row in left if row["phase"] == "EVAL"]
        right_eval = [row for row in right if row["phase"] == "EVAL"]
        metrics = lambda values: {
            "episodes": len(values),
            "successes": sum(bool(row["success"]) for row in values),
            "mean_normalized_deficit": (sum(float(row["normalized_deficit"]) for row in values) / len(values)
                                         if values else None),
            "effort_total": sum(float(row["effort"]) for row in values),
        }
        a, b = metrics(left_eval), metrics(right_eval)
        output.append({
            "trial_id": trial, "contrast": f"{pair[0]}_MINUS_{pair[1]}",
            "training_decisions_each": len(left_train),
            "training_action_reward_state_identical": signature(left_train) == signature(right_train),
            "eval_decisions_left": len(left_eval), "eval_decisions_right": len(right_eval),
            "eval_success_difference": a["successes"] - b["successes"],
            "eval_mean_deficit_difference": ((a["mean_normalized_deficit"] or 0.0)
                                              - (b["mean_normalized_deficit"] or 0.0)),
            "eval_effort_difference": a["effort_total"] - b["effort_total"],
            "left_eval": a, "right_eval": b,
            "deterministic_descriptive_only": True,
        })
    return output


def write_experiment(output_dir: Path) -> dict[str, object]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty results directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    rows, summaries, manifest = run_experiment()
    episodes_path = output_dir / "episodes.jsonl"
    episodes_path.write_text("".join(json.dumps(row, sort_keys=True, separators=(",", ":"),
                                                allow_nan=False) + "\n" for row in rows), encoding="utf-8")
    summary_path = output_dir / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]), lineterminator="\n")
        writer.writeheader()
        for summary in summaries:
            writer.writerow({key: json.dumps(value, separators=(",", ":"), allow_nan=False)
                             if isinstance(value, (dict, list, tuple)) else value
                             for key, value in summary.items()})
    contrast_path = output_dir / "paired_contrasts.csv"
    contrasts = paired_contrasts(rows)
    with contrast_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(contrasts[0]), lineterminator="\n")
        writer.writeheader()
        for contrast in contrasts:
            writer.writerow({key: json.dumps(value, separators=(",", ":"), allow_nan=False)
                             if isinstance(value, (dict, list, tuple)) else value
                             for key, value in contrast.items()})
    manifest["source_sha256"] = {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in ("src/hls/hls_lab_v1.py", "experiments/synthetic/hls_lab_v1/ce25.py")}
    manifest["output_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (episodes_path, summary_path, contrast_path)}
    manifest["commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                                        capture_output=True, text=True).stdout.strip()
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def add_derived_contrasts(output_dir: Path) -> dict[str, object]:
    """Add a deterministic derived contrast table without rerunning episodes."""
    episodes_path = output_dir / "episodes.jsonl"
    manifest_path = output_dir / "manifest.json"
    contrasts_path = output_dir / "paired_contrasts.csv"
    if contrasts_path.exists():
        raise FileExistsError(f"refusing to overwrite derived artifact: {contrasts_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    observed = hashlib.sha256(episodes_path.read_bytes()).hexdigest()
    if observed != manifest["output_sha256"]["episodes.jsonl"]:
        raise ValueError("episodes.jsonl hash does not match its frozen manifest")
    rows = [json.loads(line) for line in episodes_path.read_text(encoding="utf-8").splitlines()]
    contrasts = paired_contrasts(rows)
    if not contrasts:
        raise ValueError("no preregistered paired contrasts found")
    with contrasts_path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(contrasts[0]), lineterminator="\n")
        writer.writeheader()
        for contrast in contrasts:
            writer.writerow({key: json.dumps(value, separators=(",", ":"), allow_nan=False)
                             if isinstance(value, (dict, list, tuple)) else value
                             for key, value in contrast.items()})
    manifest.setdefault("output_sha256", {})["paired_contrasts.csv"] = hashlib.sha256(
        contrasts_path.read_bytes()).hexdigest()
    manifest["analysis_provenance"] = {
        "kind": "derived paired descriptive contrasts; no simulator rerun",
        "command": "--analyze-existing results/experiments/hls_lab_ce25",
        "analysis_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "contrast_rows": len(contrasts),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/experiments/hls_lab_ce25")
    parser.add_argument("--analyze-existing", type=Path,
                        help="derive paired contrasts from existing CE-25 raw rows without rerunning episodes")
    args = parser.parse_args()
    manifest = (add_derived_contrasts(args.analyze_existing) if args.analyze_existing
                else write_experiment(args.output_dir))
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
