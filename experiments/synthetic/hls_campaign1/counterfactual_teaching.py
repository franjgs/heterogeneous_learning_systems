"""Paired, state-conditional teaching interventions from the published pilot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from experiments.synthetic.hls_campaign1.run import (  # noqa: E402
    DEMAND_RELATIONS, HIGH_EFFICACY, LEARNING, LOW_EFFICACY, PARAMETERS, SEEDS,
    _efficacy, _environment, _initial_team, _policy, configuration_grid,
)
from hls.hls_lab_dynamic import (  # noqa: E402
    competence_estimate_matrix, competence_variance_matrix,
)
from hls.hls_lab_v1_integrated import (  # noqa: E402
    IntegratedAction, IntegratedDecisionView, OrganizationSnapshot,
    P0ProductionOnly, P2AdaptiveTeaching,
    enumerate_feasible_integrated_actions, run_integrated_sequence,
    _best_action,
)

PILOT = ROOT / "results/experiments/hls_campaign1_pilot"
OUTPUT = ROOT / "results/diagnostics/hls_campaign1_counterfactual_teaching_value"
INTERVENTION_PERIODS = (("early", 2), ("late", 16))
DIRECTED_CANDIDATES = tuple(dict.fromkeys(DEMAND_RELATIONS))
TOL = 1e-12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write empty result: {path}")
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _selection_keys() -> list[dict[str, object]]:
    """Full 2x2x2x2x2 fixed strata; first published seed, long horizon."""
    configs = [item for item in configuration_grid() if item["horizon"] == "long"]
    selected = []
    for config in configs:
        for individual_learning in (False, True):
            for phase, period in INTERVENTION_PERIODS:
                selected.append({**config, "seed": SEEDS[0],
                                 "individual_learning": individual_learning,
                                 "intervention_phase": phase,
                                 "intervention_period": period})
    return selected


def _pilot_row_lookup(rows: list[dict[str, str]]) -> dict[tuple[object, ...], dict[str, str]]:
    result = {}
    for row in rows:
        if row["policy"] != "P2_ADAPTIVE_TEACHING":
            continue
        key = (row["demand"], row["initial_deficit"], row["teaching_effectiveness"],
               row["horizon"], int(row["seed"]), row["individual_learning"],
               int(row["period"]))
        result[key] = row
    return result


def _view(snapshot: OrganizationSnapshot, problem, demand_label: str,
          periods_remaining: int) -> IntegratedDecisionView:
    feasible = enumerate_feasible_integrated_actions(problem, teaching_effort=PARAMETERS.effort)
    posterior = snapshot.competence_posterior
    return IntegratedDecisionView(
        period=snapshot.next_period, periods_remaining=periods_remaining,
        problem_id=problem.problem_id, demand_label=demand_label,
        requirements=problem.requirements, resource_budget=problem.resource_budget,
        max_effort_per_expert=problem.max_effort_per_expert,
        estimated_competencies=competence_estimate_matrix(posterior),
        competence_variance=competence_variance_matrix(posterior),
        efficacy_estimates=snapshot.organization_memory.efficacy,
        feasible_actions=feasible,
    )


def _verify_replay(result, pilot_run: list[dict[str, str]]) -> None:
    if len(result.records) != len(pilot_run):
        raise AssertionError("replayed history length differs from published pilot")
    for record, frozen in zip(result.records, pilot_run):
        expected = {
            "problem_id": record.problem_id,
            "production_action_id": str(record.production_action_id),
            "teaching_relation": ("NA" if record.action.teaching is None else
                                  ":".join(map(str, record.action.teaching.relation))),
            "ces_reward": record.ces_reward,
            "production_effort": record.production_effort,
            "teaching_effort": record.teaching_effort,
            "resources_used": record.total_resource_used,
            "competence_real_before": record.competence_real_before,
            "competence_real_after": record.competence_real_after,
            "competence_estimated_before": record.competence_estimated_before,
            "competence_estimated_after": record.competence_estimated_after,
        }
        for key, actual in expected.items():
            target = frozen[key]
            if isinstance(actual, float):
                if abs(actual - float(target)) > TOL:
                    raise AssertionError(f"pilot replay mismatch at period {record.period}: {key}")
            elif key.endswith("before") or key.endswith("after"):
                if json.loads(target) != [list(cell) for cell in actual]:
                    raise AssertionError(f"pilot replay mismatch at period {record.period}: {key}")
            elif str(actual) != target:
                raise AssertionError(f"pilot replay mismatch at period {record.period}: {key}")


def _action_for_relation(view: IntegratedDecisionView, relation) -> IntegratedAction:
    candidates = tuple(action for action in view.feasible_actions
                       if action.teaching is not None and action.teaching.relation == relation)
    return _best_action(candidates, view)


def run_audit(output_dir: Path = OUTPUT) -> dict[str, object]:
    manifest_path = PILOT / "manifest.json"
    pilot_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for filename, expected_hash in pilot_manifest["artifacts_sha256"].items():
        actual = sha256(PILOT / filename)
        if actual != expected_hash:
            raise RuntimeError(f"frozen pilot artifact hash mismatch: {filename}")
    pilot_rows = _read_csv(PILOT / "episodes.csv")
    lookup = _pilot_row_lookup(pilot_rows)
    seed = SEEDS[0]
    state_rows: list[dict[str, object]] = []
    time_rows: list[dict[str, object]] = []
    p2_rows: list[dict[str, object]] = []
    prefix_cache = {}

    for selection in _selection_keys():
        config = {k: selection[k] for k in
                  ("demand", "initial_deficit", "teaching_effectiveness", "horizon", "n_periods")}
        li = bool(selection["individual_learning"])
        period = int(selection["intervention_period"])
        efficacy_value = LOW_EFFICACY if config["teaching_effectiveness"] == "low" else HIGH_EFFICACY
        problems, _latent = _environment(str(config["demand"]), int(config["n_periods"]), seed)
        efficacy = _efficacy(efficacy_value)
        initial = _initial_team(str(config["initial_deficit"]))
        cache_key = (tuple(config.items()), li)
        if cache_key not in prefix_cache:
            replay = run_integrated_sequence(
                initial, problems, _policy("P2_ADAPTIVE_TEACHING"),
                learning=LEARNING,
                teaching_efficacy=efficacy, parameters=PARAMETERS,
                individual_learning=li, organizational_learning=True, seed=seed,
            )
            config_rows = [r for r in pilot_rows if all(r[k] == str(v) for k, v in config.items()
                            if k != "n_periods") and r["seed"] == str(seed)
                           and r["individual_learning"] == str(li)
                           and r["policy"] == "P2_ADAPTIVE_TEACHING"]
            config_rows.sort(key=lambda r: int(r["period"]))
            _verify_replay(replay, config_rows)
            prefix_cache[cache_key] = replay
        replay = prefix_cache[cache_key]
        snapshot = deepcopy(replay.snapshots[period])
        frozen_key = (str(config["demand"]), str(config["initial_deficit"]),
                      str(config["teaching_effectiveness"]), str(config["horizon"]),
                      seed, str(li), period)
        frozen_row = lookup[frozen_key]
        if frozen_row["problem_id"] != problems[period].problem.problem_id:
            raise AssertionError("selected state problem does not match frozen pilot")
        if json.loads(frozen_row["competence_real_before"]) != [list(row) for row in snapshot.team.real_matrix]:
            raise AssertionError("snapshot real state does not match published state")
        if json.loads(frozen_row["competence_estimated_before"]) != [list(row) for row in
                competence_estimate_matrix(snapshot.competence_posterior)]:
            raise AssertionError("snapshot estimate does not match published state")
        if period > 0:
            previous = lookup[(str(config["demand"]), str(config["initial_deficit"]),
                               str(config["teaching_effectiveness"]), str(config["horizon"]),
                               seed, str(li), period - 1)]
            frozen_memory = json.loads(previous["organization_memory"])
            snapshot_memory = [{"relation": list(row.relation), "count": row.count, "mean": row.mean}
                               for row in snapshot.organization_memory.efficacy]
            if frozen_memory != snapshot_memory:
                raise AssertionError("snapshot organizational memory does not match published prefix")

        suffix = problems[period:]
        view = _view(snapshot, suffix[0].problem, suffix[0].demand_label, len(suffix))
        policy = P2AdaptiveTeaching(DEMAND_RELATIONS)
        p2_action = policy.choose(view, snapshot.organization_memory, PARAMETERS)
        no_teach = P0ProductionOnly().choose(view, snapshot.organization_memory, PARAMETERS)
        if no_teach.teaching is not None:
            raise AssertionError("production-only intervention unexpectedly teaches")

        base_key = {**config, "seed": seed, "individual_learning": li,
                    "intervention_phase": selection["intervention_phase"],
                    "intervention_period": period}
        for candidate_index, relation in enumerate(DIRECTED_CANDIDATES):
            teach_action = _action_for_relation(view, relation)
            # Branches start from independent copies of the complete public and
            # private simulator state; only the forced first intervention differs.
            branch_a = run_integrated_sequence(
                snapshot.team, suffix, policy, learning=LEARNING,
                teaching_efficacy=efficacy, parameters=PARAMETERS,
                individual_learning=li, organizational_learning=True, seed=seed,
                initial_snapshot=deepcopy(snapshot), first_action_override=no_teach,
            )
            branch_b = run_integrated_sequence(
                snapshot.team, suffix, policy, learning=LEARNING,
                teaching_efficacy=efficacy, parameters=PARAMETERS,
                individual_learning=li, organizational_learning=True, seed=seed,
                initial_snapshot=deepcopy(snapshot), first_action_override=teach_action,
            )
            if tuple(x.problem_id for x in branch_a.records) != tuple(x.problem_id for x in branch_b.records):
                raise AssertionError("counterfactual branches received different exogenous problems")
            cumulative = 0.0
            for offset, (a, b) in enumerate(zip(branch_a.records, branch_b.records)):
                delta = b.ces_reward - a.ces_reward
                cumulative += delta
                time_rows.append({**base_key, "candidate_index": candidate_index,
                    "candidate_relation": ":".join(map(str, relation)),
                    "absolute_period": period + offset, "no_teach_ces": a.ces_reward,
                    "teach_ces": b.ces_reward, "period_delta": delta,
                    "cumulative_delta": cumulative,
                    "no_teach_real_competencies": json.dumps(a.competence_real_after),
                    "teach_real_competencies": json.dumps(b.competence_real_after),
                    "competence_difference": json.dumps(tuple(tuple(
                        b.competence_real_after[i][k] - a.competence_real_after[i][k]
                        for k in range(2)) for i in range(3))),
                    "teaching_effort": b.teaching_effort,
                    "productive_effort_displaced_vs_no_teach": a.production_effort-b.production_effort,
                    "unused_capacity_no_teach": suffix[offset].problem.resource_budget-a.total_resource_used,
                    "unused_capacity_teach": suffix[offset].problem.resource_budget-b.total_resource_used,
                    "environment_regime": suffix[offset].demand_label})
            final_delta = cumulative
            selected_relation = ("none" if p2_action.teaching is None else
                                 ":".join(map(str, p2_action.teaching.relation)))
            state_rows.append({**base_key, "candidate_index": candidate_index,
                "candidate_relation": ":".join(map(str, relation)),
                "mis_enabled": li, "starting_problem_id": suffix[0].problem.problem_id,
                "current_requirements": json.dumps(suffix[0].problem.requirements),
                "remaining_problem_ids": json.dumps([x.problem.problem_id for x in suffix]),
                "starting_real_competencies": json.dumps(snapshot.team.real_matrix),
                "starting_estimated_competencies": json.dumps(view.estimated_competencies),
                "starting_efficacy_memory": json.dumps([asdict(x) for x in snapshot.organization_memory.efficacy]),
                "p2_choice_relation": selected_relation,
                "p2_choice_action": json.dumps(p2_action.production),
                "counterfactual_teach_action": json.dumps(asdict(teach_action)),
                "no_teach_action": json.dumps(asdict(no_teach)),
                "remaining_horizon": len(suffix), "immediate_delta":
                    branch_b.records[0].ces_reward-branch_a.records[0].ces_reward,
                "initial_teaching_effort": branch_b.records[0].teaching_effort,
                "initial_production_effort_displaced": (branch_a.records[0].production_effort-
                                                         branch_b.records[0].production_effort),
                "initial_unused_capacity_no_teach": (suffix[0].problem.resource_budget-
                                                       branch_a.records[0].total_resource_used),
                "initial_unused_capacity_teach": (suffix[0].problem.resource_budget-
                                                    branch_b.records[0].total_resource_used),
                "delta_v_h": final_delta,
                "no_teach_ces_sum": sum(x.ces_reward for x in branch_a.records),
                "teach_ces_sum": sum(x.ces_reward for x in branch_b.records),
                "no_teach_final_competencies": json.dumps(branch_a.final_team.real_matrix),
                "teach_final_competencies": json.dumps(branch_b.final_team.real_matrix),
                "no_teach_total_teaching_effort": sum(x.teaching_effort for x in branch_a.records),
                "teach_total_teaching_effort": sum(x.teaching_effort for x in branch_b.records),
                "no_teach_total_production_effort": sum(x.production_effort for x in branch_a.records),
                "teach_total_production_effort": sum(x.production_effort for x in branch_b.records),
                "no_teach_unused_capacity": sum(suffix[i].problem.resource_budget-x.total_resource_used
                                                   for i, x in enumerate(branch_a.records)),
                "teach_unused_capacity": sum(suffix[i].problem.resource_budget-x.total_resource_used
                                               for i, x in enumerate(branch_b.records)),
                "p2_missed_positive_opportunity": p2_action.teaching is None and final_delta > TOL,
                "p2_selected_harmful_candidate": p2_action.teaching is not None and
                    p2_action.teaching.relation == relation and final_delta < -TOL,
                "outcome_class": "positive" if final_delta > TOL else
                    ("negative" if final_delta < -TOL else "neutral")})

    by_state: dict[tuple[object, ...], list[dict[str, object]]] = {}
    state_fields = ("demand", "initial_deficit", "teaching_effectiveness", "horizon",
                    "seed", "individual_learning", "intervention_phase", "intervention_period")
    for row in state_rows:
        key = tuple(row[field] for field in state_fields)
        by_state.setdefault(key, []).append(row)
    for key, candidates in sorted(by_state.items(), key=lambda pair: str(pair[0])):
        choice = str(candidates[0]["p2_choice_relation"])
        values = {str(row["candidate_relation"]): float(row["delta_v_h"]) for row in candidates}
        if choice == "none":
            profitable = [relation for relation, value in values.items() if value > TOL]
            classification = "missed_profitable_opportunity" if profitable else "correct_no_teaching_under_tested_candidates"
            chosen_value = None
        else:
            chosen_value = values.get(choice)
            if chosen_value is None:
                raise AssertionError(f"P2 chose an unevaluated teaching candidate: {choice}")
            classification = ("correct_teaching_under_tested_candidate" if chosen_value > TOL
                              else "harmful_teaching_under_tested_candidate" if chosen_value < -TOL
                              else "neutral_teaching_under_tested_candidate")
            profitable = []
        p2_rows.append({**dict(zip(state_fields, key)), "p2_choice_relation": choice,
                        "chosen_relation_delta_v_h": chosen_value,
                        "profitable_untaken_relations": ":".join(sorted(profitable)),
                        "decision_classification": classification})

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "paired_outcomes.csv", state_rows)
    _write_csv(output_dir / "cumulative_trajectories.csv", time_rows)
    _write_csv(output_dir / "p2_decisions.csv", p2_rows)
    manifest = {
        "campaign": "HLS-CAMPAIGN-1-COUNTERFACTUAL-TEACHING-VALUE",
        "repository_base": "f27ffba557b3c82bbf9618e6e0743bc4bd2d990a",
        "execution_command": "PYTHONPATH=src:. python -m experiments.synthetic.hls_campaign1.counterfactual_teaching",
        "generated_at_europe_madrid": datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="seconds"),
        "state_selection": "Published pilot only; long-horizon cells; seed 2026101511; full factorial demand x initial deficit x teaching efficacy x MIS ON/OFF x period 2/16 (early/late); selected without outcome filtering.",
        "states": len(_selection_keys()), "directed_candidate_relations": DIRECTED_CANDIDATES,
        "paired_comparisons": len(state_rows), "continuation_policy": "P2_ADAPTIVE_TEACHING in both branches after forced first action; same policy rule, independently evolving observations/state.",
        "initial_interventions": "No-teach branch: P0-selected production-only action. Teach branch: best feasible production allocation under the specified existing directed relation, scored on current observable estimates. Resource budget is common; first-period production assignments can differ due to teaching feasibility.",
        "estimand": "Remaining-horizon paired cumulative CES(teach)-CES(no-teach), conditional on frozen state, intervention, continuation rule, common exogenous problem suffix, seed-indexed innovations, and MIS condition.",
        "input_sha256": {"pilot_manifest.json": sha256(manifest_path),
                         "episodes.csv": sha256(PILOT / "episodes.csv"),
                         "run.py": sha256(ROOT / "experiments/synthetic/hls_campaign1/run.py"),
                         "integrated.py": sha256(ROOT / "src/hls/hls_lab_v1_integrated.py")},
        "environment": {"python": sys.version, "platform": platform.platform()},
        "frozen_parameters": {"seed": seed, "long_horizon": 24,
            "intervention_periods": dict(INTERVENTION_PERIODS),
            "teaching_relations": DIRECTED_CANDIDATES,
            "teaching_effort_per_participant": PARAMETERS.effort,
            "transfer_rate": PARAMETERS.transfer_rate,
            "production_observation_noise_sd": PARAMETERS.production_observation_noise_sd,
            "teaching_observation_noise_sd": PARAMETERS.outcome_noise_sd,
            "individual_learning_eta": LEARNING.eta,
            "resource_budget": 2.0},
        "output_sha256": {},
        "notes": ["No population inference: one fixed published seed per prespecified stratum.",
                  "P2 decision diagnostics use only the captured observable decision view.",
                  "Pilot CSV lacks full posterior and direct teaching increment; deterministic replay reconstructs/captures them.",
                  "CES difference is not cost-adjusted utility or globally optimal teaching value."],
    }
    for name in ("paired_outcomes.csv", "cumulative_trajectories.csv", "p2_decisions.csv"):
        manifest["output_sha256"][name] = sha256(output_dir / name)
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    manifest = run_audit(args.output)
    print(json.dumps({key: manifest[key] for key in
          ("generated_at_europe_madrid", "states", "paired_comparisons", "output_sha256")}, indent=2))


if __name__ == "__main__":
    main()
