"""Reproducible 2x2x2x2 HLS Campaign 1 pilot.

The protocol constants are fixed before result generation. The runner uses
the published v1 environment, action feasibility, production, MIS-v2 and
teaching transitions. P2_SCHEDULED is a no-feedback teaching control, not a
new learning algorithm.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import sys
from dataclasses import asdict, replace
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.discover_v0 import JOINT_ACTIONS  # noqa: E402
from hls.hls_lab_dynamic import (  # noqa: E402
    CompetenceInformationMode,
    DemandRegime,
    LearningProfile,
    make_dynamic_team,
)
from hls.hls_lab_v1_environment import (  # noqa: E402
    ExogenousEnvironmentConfig,
    generate_environment_trajectory,
)
from hls.hls_lab_v1_integrated import (  # noqa: E402
    IntegratedDecisionView,
    IntegratedProblem,
    IntegratedPolicy,
    OrganizationMemory,
    P0ProductionOnly,
    P1FixedTeaching,
    P2AdaptiveTeaching,
    TeachingEfficacy,
    TeachingParameters,
    _best_production,
    _best_action,
    _outputs_score,
    enumerate_feasible_integrated_actions,
    run_integrated_sequence,
)
from hls.synthetic.c5 import NonStationaryTaskDemand, StationaryTaskDemand  # noqa: E402


CAMPAIGN = "HLS-SCIENTIFIC-CAMPAIGN-1-PILOT"
SEEDS = tuple(range(2026101511, 2026101521))
HORIZONS = {"short": 8, "long": 24}
RESOURCE_BUDGET = 2.0
MAX_EFFORT_PER_EXPERT = 1.0
RESOURCE_COST_PER_UNIT = 0.2
TEACHING_EFFORT = 0.25
TRANSFER_RATE = 0.75
LOW_EFFICACY = 0.10
HIGH_EFFICACY = 0.85
LOW_DEFICIT_TEAM = ((0.80, 0.25), (0.45, 0.45), (0.25, 0.80))
HIGH_DEFICIT_TEAM = ((0.55, 0.15), (0.20, 0.25), (0.15, 0.55))
INITIAL_ESTIMATES = ((0.40, 0.40), (0.40, 0.40), (0.40, 0.40))
LEARNING = LearningProfile(((0.06, 0.03), (0.04, 0.08), (0.02, 0.05)))
DEMAND_RELATIONS = ((2, 1, 1), (0, 1, 0))
FIXED_RELATION = (2, 1, 1)
POLICIES = ("P0_PRODUCTION_ONLY", "P1_FIXED_TEACHING",
            "P2_ADAPTIVE_TEACHING", "P2_SCHEDULED_NO_FEEDBACK")
LEARNING_BY_DOING = (False, True)
LEVELS = {"low": 0.80, "high": 0.90}
CES_WEIGHTS = (0.5, 0.5)
PARAMETERS = TeachingParameters(
    transfer_rate=TRANSFER_RATE,
    effort=TEACHING_EFFORT,
    outcome_noise_sd=0.02,
    production_observation_noise_sd=0.02,
    competence_grid_points=101,
    competence_prior_variance=0.04,
    efficacy_prior_mean=0.5,
    efficacy_threshold=0.35,
    target_competence=0.95,
)


class P2ScheduledNoFeedback:
    """Fixed cyclic teaching schedule; never reads efficacy observations."""

    name = "P2_SCHEDULED_NO_FEEDBACK"

    def __init__(self, relations=DEMAND_RELATIONS):
        self.relations = tuple(relations)

    def choose(self, view: IntegratedDecisionView, memory: OrganizationMemory,
               parameters: TeachingParameters):
        del memory
        production = _best_production(view.feasible_actions, view)
        if _outputs_score(view, production)[0] == 1:
            return production
        eligible = tuple(relation for relation in self.relations
                         if view.requirements[relation[2]] > 0
                         and view.estimated_competencies[relation[1]][relation[2]]
                         < parameters.target_competence)
        if not eligible:
            return production
        # Predetermined cyclic choice using public period/context only.
        relation = eligible[view.period % len(eligible)]
        candidates = tuple(action for action in view.feasible_actions
                           if action.teaching is not None
                           and action.teaching.relation == relation)
        return _best_action(candidates, view) if candidates else production


def _regimes() -> tuple[DemandRegime, DemandRegime, DemandRegime]:
    level_values = (LEVELS["low"], LEVELS["high"])
    probs = (0.5, 0.5)
    all_types = tuple((v, 0.0) for v in level_values) + tuple((0.0, v) for v in level_values)
    all_probs = (0.25, 0.25, 0.25, 0.25)
    return (
        DemandRegime("stationary-mix", all_types, all_probs),
        DemandRegime("skill-0-regime", tuple((v, 0.0) for v in level_values), probs),
        DemandRegime("skill-1-regime", tuple((0.0, v) for v in level_values), probs),
    )


def configuration_grid() -> tuple[dict[str, object], ...]:
    rows = []
    for demand in ("stationary", "changing"):
        for deficit in ("low", "high"):
            for efficacy in ("low", "high"):
                for horizon in ("short", "long"):
                    rows.append({"demand": demand, "initial_deficit": deficit,
                                 "teaching_effectiveness": efficacy, "horizon": horizon,
                                 "n_periods": HORIZONS[horizon]})
    return tuple(rows)


def _efficacy(value: float) -> TeachingEfficacy:
    rows = []
    for teacher in range(3):
        row = []
        for learner in range(3):
            row.append((0.0, 0.0) if teacher == learner else (value, value))
        rows.append(tuple(row))
    return TeachingEfficacy(tuple(rows))


def _initial_team(deficit: str):
    real = LOW_DEFICIT_TEAM if deficit == "low" else HIGH_DEFICIT_TEAM
    return make_dynamic_team(
        real,
        information_mode=CompetenceInformationMode.PARTIAL_STATIC,
        estimated_competencies=INITIAL_ESTIMATES,
    )


def _environment(demand: str, horizon: int, seed: int):
    stationary, regime0, regime1 = _regimes()
    if demand == "stationary":
        process = StationaryTaskDemand({"mixed": 1.0})
        emissions = {"mixed": stationary}
    else:
        split = horizon // 2
        process = NonStationaryTaskDemand({
            time: ({"skill0": 1.0} if time < split else {"skill1": 1.0})
            for time in range(horizon)
        })
        emissions = {"skill0": regime0, "skill1": regime1}
    config = ExogenousEnvironmentConfig(process, emissions, horizon, RESOURCE_BUDGET)
    trajectory = generate_environment_trajectory(config, seed=seed)
    problems = tuple(IntegratedProblem(
        replace(item.problem, max_effort_per_expert=MAX_EFFORT_PER_EXPERT,
                resource_cost_per_unit=RESOURCE_COST_PER_UNIT),
        ces_weights=CES_WEIGHTS,
        demand_label="observed-demand",
    ) for index, item in enumerate(trajectory.problems))
    return problems, trajectory.latent_states


def _policy(name: str):
    if name == "P0_PRODUCTION_ONLY":
        return P0ProductionOnly()
    if name == "P1_FIXED_TEACHING":
        return P1FixedTeaching(FIXED_RELATION)
    if name == "P2_ADAPTIVE_TEACHING":
        return P2AdaptiveTeaching(DEMAND_RELATIONS)
    if name == "P2_SCHEDULED_NO_FEEDBACK":
        return P2ScheduledNoFeedback()
    raise ValueError(name)


def _episode_rows(config, seed, li, policy_name, result, latent):
    records = []
    split = len(result.records) // 2
    for row in result.records:
        event = row.action.teaching
        records.append({
            **config,
            "seed": seed,
            "individual_learning": li,
            "policy": policy_name,
            "period": row.period,
            "latent_regime_experimenter_only": str(latent[row.period]),
            "phase": "pre_change" if config["demand"] == "changing" and row.period < split
                     else ("post_change" if config["demand"] == "changing" else "stationary"),
            "problem_id": row.problem_id,
            "requirements": json.dumps(row.requirements),
            "competence_real_before": json.dumps(row.competence_real_before),
            "competence_real_after": json.dumps(row.competence_real_after),
            "competence_estimated_before": json.dumps(row.competence_estimated_before),
            "competence_estimated_after": json.dumps(row.competence_estimated_after),
            "production_action_id": row.production_action_id,
            "teaching_relation": "" if event is None else ":".join(map(str, event.relation)),
            "teaching_effort": row.teaching_effort,
            "production_effort": row.production_effort,
            "resources_used": row.total_resource_used,
            "resources_available": RESOURCE_BUDGET,
            "resource_cost": row.resource_cost,
            "outputs": json.dumps(row.outputs),
            "ces_reward": row.ces_reward,
            "functional_success": int(row.functional_result.success),
            "normalized_deficit": row.functional_result.normalized_deficit,
            "teaching_observation": "" if row.teaching_observation is None else row.teaching_observation,
            "organization_updated": row.organization_updated,
            "organization_memory": json.dumps([
                {"relation": item.relation, "count": item.count, "mean": item.mean}
                for item in row.efficacy_estimates_after
            ]),
        })
    return records


def run_pilot(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    protocol = {
        "campaign": CAMPAIGN,
        "protocol_version": "1.0",
        "factors": configuration_grid(),
        "seeds": SEEDS,
        "policies": POLICIES,
        "policy_definitions": {
            "P0_PRODUCTION_ONLY": "Existing P0; choose feasible no-teaching action by lexicographic functional score (success, negative normalized deficit, margin, negative effort).",
            "P1_FIXED_TEACHING": f"Existing P1; choose highest functional-score action among feasible lessons for fixed relation {FIXED_RELATION}, otherwise choose P0 action.",
            "P2_ADAPTIVE_TEACHING": "Existing P2; do not teach if best production-only action is predicted successful; otherwise test unseen configured relations in order, then choose the highest observed efficacy if it meets threshold, else produce. Organizational observations update efficacy memory and competence posterior.",
            "P2_SCHEDULED_NO_FEEDBACK": "Campaign control; same no-teaching success gate and candidate relations; cycle over currently eligible relations using public period, ignore efficacy observations, and run with organizational_learning=False. This is a deterministic schedule, not a learned policy.",
        },
        "common_decision_score": "(functional_success, -normalized_deficit, functional_margin, -production_effort); the reported CES is an outcome metric, not the policy objective.",
        "individual_learning_control": LEARNING_BY_DOING,
        "initial_teams": {"low": LOW_DEFICIT_TEAM, "high": HIGH_DEFICIT_TEAM},
        "initial_estimates_all_conditions": INITIAL_ESTIMATES,
        "competence_information_mode": "PARTIAL_STATIC; common prior independent of private real skills",
        "demand_levels": LEVELS,
        "demand_definition": {
            "stationary": "IID equiprobable requirement vectors (0.80,0),(0.90,0),(0,0.80),(0,0.90) each period.",
            "changing": "first floor(H/2) periods draw (0.80,0)/(0.90,0); remaining periods draw (0,0.80)/(0,0.90), each within-regime equiprobably.",
        },
        "resource_budget": RESOURCE_BUDGET,
        "resource_budget_rationale": "The existing 64-action catalogue has minimum positive production effort 1.0; a lesson consumes 2*0.25=0.5. Budget 2.0 permits a lesson plus one minimum productive action and permits up to two production effort units without teaching. This was selected from action/resource granularity, not policy outcomes.",
        "requirement_level_rationale": "The common prior 0.40 can produce at most 0.80 in one dimension under the shared budget and per-expert cap. The low-deficit team's initial per-skill top-two competence sums are 1.25; the high-deficit team's are 0.75 (skill 0) and 0.80 (skill 1). Requirements 0.80/0.90 are therefore fixed at the prior frontier and immediately beyond it; both are feasible for the low-deficit team's initial state, while 0.90 exceeds the high-deficit team's initial frontier. Values are based on action enumeration and initial states, not policy outcomes.",
        "max_effort_per_expert": MAX_EFFORT_PER_EXPERT,
        "resource_cost_per_unit": RESOURCE_COST_PER_UNIT,
        "fixed_teaching_relation": FIXED_RELATION,
        "adaptive_relations": DEMAND_RELATIONS,
        "teaching_efficacy": {"low": LOW_EFFICACY, "high": HIGH_EFFICACY},
        "teaching_parameters": asdict(PARAMETERS),
        "learning_eta": LEARNING.eta,
        "ces_weights": CES_WEIGHTS,
        "randomness_coupling": "One exogenous trajectory is generated per factor-cell/seed and reused for all policies and LI conditions. Production noise is indexed by seed/period/decision/expert/skill; teaching noise by seed/period/instructor/learner/skill.",
        "paired_outcomes": "Each non-P0 run is differenced against P0 at the same factor cell, LI condition, and seed.",
        "metric_definitions": {
            "ces_reward_sum": "Sum of existing DISCOVER CES reward per episode; weights are CES_WEIGHTS.",
            "success_rate": "Mean binary FunctionalResult.success per episode.",
            "resource_utilization": "Sum of production effort plus instructor and learner effort divided by horizon times the shared per-period budget.",
            "resource_cost_sum": "Sum of used resource units times resource cost per unit; reported separately, not subtracted from CES.",
            "teaching_effort_sum": "Sum of both participants' effort per lesson (2 × event effort).",
            "normalized_deficit_mean": "Mean existing normalized functional deficit.",
            "competence": "Real competence is logged to the experimenter only; policy views receive posterior means updated only from public observations and declared MIS-v2 parameters.",
            "pre_post": "For changing demand only, means over periods [0,floor(H/2)) and [floor(H/2),H); stationary demand is summarized over the full horizon.",
        },
        "missing_value_encoding": "NA denotes a metric not applicable to that row, including pre/post-change summaries for stationary demand.",
        "metric_note": "CES and resource cost are reported separately; no arbitrary net utility.",
        "inference_note": "10 predetermined stochastic seed streams per configuration; report descriptive between-seed mean/SD, no significance tests or population-level claims.",
    }
    protocol_path = output_dir / "protocol.json"
    protocol_path.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    protocol_hash = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    timestamp = datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="seconds")
    rows = []
    summaries_seed = []
    for config_index, config in enumerate(configuration_grid(), start=1):
        print(f"configuration {config_index}/16: {config}", flush=True)
        horizon = int(config["n_periods"])
        for seed in SEEDS:
            problems, latent = _environment(str(config["demand"]), horizon, seed)
            initial = _initial_team(str(config["initial_deficit"]))
            teaching_value = LOW_EFFICACY if config["teaching_effectiveness"] == "low" else HIGH_EFFICACY
            efficacy = _efficacy(teaching_value)
            for li in LEARNING_BY_DOING:
                for policy_name in POLICIES:
                    org_learning = policy_name != "P2_SCHEDULED_NO_FEEDBACK"
                    result = run_integrated_sequence(
                        initial, problems, _policy(policy_name), learning=LEARNING,
                        teaching_efficacy=efficacy, parameters=PARAMETERS,
                        individual_learning=li, organizational_learning=org_learning,
                        seed=seed,
                    )
                    episodes = _episode_rows(config, seed, li, policy_name, result, latent)
                    rows.extend(episodes)
                    n = len(episodes)
                    successes = sum(int(x["functional_success"]) for x in episodes)
                    ces = sum(float(x["ces_reward"]) for x in episodes)
                    used = sum(float(x["resources_used"]) for x in episodes)
                    teach = sum(float(x["teaching_effort"]) for x in episodes)
                    deficit = sum(float(x["normalized_deficit"]) for x in episodes)
                    pre = [x for x in episodes if x["phase"] == "pre_change"]
                    post = [x for x in episodes if x["phase"] == "post_change"]
                    summary = {
                        **config, "seed": seed, "individual_learning": li,
                        "policy": policy_name, "periods": n,
                        "ces_reward_sum": ces, "success_rate": successes / n,
                        "resource_utilization": used / (n * RESOURCE_BUDGET),
                        "resource_cost_sum": sum(float(x["resource_cost"]) for x in episodes),
                        "teaching_effort_sum": teach,
                        "teaching_periods": sum(bool(x["teaching_relation"]) for x in episodes),
                        "normalized_deficit_mean": deficit / n,
                        "final_mean_competence": mean(v for row in result.final_team.real_matrix for v in row),
                        "final_competence": json.dumps(result.final_team.real_matrix),
                        "pre_change_success_rate": (mean(int(x["functional_success"]) for x in pre) if pre else ""),
                        "post_change_success_rate": (mean(int(x["functional_success"]) for x in post) if post else ""),
                        "pre_change_ces_mean": (mean(float(x["ces_reward"]) for x in pre) if pre else ""),
                        "post_change_ces_mean": (mean(float(x["ces_reward"]) for x in post) if post else ""),
                    }
                    summaries_seed.append(summary)
    episode_path = output_dir / "episodes.csv"
    _write_csv(episode_path, rows)
    seed_path = output_dir / "seed_summaries.csv"
    _write_csv(seed_path, summaries_seed)
    metrics = ("ces_reward_sum", "success_rate", "resource_utilization",
               "resource_cost_sum", "teaching_effort_sum", "normalized_deficit_mean",
               "final_mean_competence", "pre_change_success_rate", "post_change_success_rate")
    by_key = {}
    for row in summaries_seed:
        key = (row["demand"], row["initial_deficit"], row["teaching_effectiveness"],
               row["horizon"], row["individual_learning"])
        by_key.setdefault(key, {})[row["policy"]] = row
    paired = []
    for key, policies in by_key.items():
        # Each key has one row per policy and seed; seed-level pairing below.
        config_rows = [row for row in summaries_seed if (
            row["demand"], row["initial_deficit"], row["teaching_effectiveness"],
            row["horizon"], row["individual_learning"]) == key]
        seeds = sorted({row["seed"] for row in config_rows})
        lookup = {(row["seed"], row["policy"]): row for row in config_rows}
        for seed in seeds:
            baseline = lookup[(seed, "P0_PRODUCTION_ONLY")]
            for policy in POLICIES[1:]:
                candidate = lookup[(seed, policy)]
                entry = dict(zip(("demand", "initial_deficit", "teaching_effectiveness", "horizon", "individual_learning"), key))
                entry.update(seed=seed, policy=policy, baseline="P0_PRODUCTION_ONLY")
                for metric in metrics:
                    left, right = candidate[metric], baseline[metric]
                    entry[f"delta_{metric}"] = "" if left == "" or right == "" else float(left) - float(right)
                paired.append(entry)
    paired_path = output_dir / "paired_differences.csv"
    _write_csv(paired_path, paired)
    paired_aggregate = []
    paired_groups = {}
    for row in paired:
        key = (row["demand"], row["initial_deficit"], row["teaching_effectiveness"],
               row["horizon"], row["individual_learning"], row["policy"])
        paired_groups.setdefault(key, []).append(row)
    for key, group in paired_groups.items():
        entry = dict(zip(("demand", "initial_deficit", "teaching_effectiveness", "horizon", "individual_learning", "policy"), key))
        entry["replicates"] = len(group)
        for metric in metrics:
            values = [float(row[f"delta_{metric}"]) for row in group
                      if row[f"delta_{metric}"] != ""]
            entry[f"mean_delta_{metric}"] = mean(values) if values else ""
            entry[f"sd_delta_{metric}"] = stdev(values) if len(values) > 1 else (0.0 if values else "")
        paired_aggregate.append(entry)
    paired_aggregate_path = output_dir / "paired_aggregate.csv"
    _write_csv(paired_aggregate_path, paired_aggregate)
    aggregate = []
    by_policy = {}
    for row in summaries_seed:
        key = (row["demand"], row["initial_deficit"], row["teaching_effectiveness"],
               row["horizon"], row["individual_learning"], row["policy"])
        by_policy.setdefault(key, []).append(row)
    for key, group in by_policy.items():
        entry = dict(zip(("demand", "initial_deficit", "teaching_effectiveness", "horizon", "individual_learning", "policy"), key))
        entry["replicates"] = len(group)
        for metric in metrics:
            vals = [float(row[metric]) for row in group if row[metric] != ""]
            entry[f"mean_{metric}"] = mean(vals) if vals else ""
            entry[f"sd_{metric}"] = stdev(vals) if len(vals) > 1 else (0.0 if vals else "")
        aggregate.append(entry)
    aggregate_path = output_dir / "aggregate_summary.csv"
    _write_csv(aggregate_path, aggregate)
    manifest = {
        "campaign": CAMPAIGN,
        "status": "COMPLETE",
        "execution_timestamp_europe_madrid": timestamp,
        "repository_head_before_run": _git_head(),
        "protocol_sha256": protocol_hash,
        "counts": {"factor_configurations": 16, "seeds_per_configuration": len(SEEDS),
                   "policies": len(POLICIES), "individual_learning_conditions": len(LEARNING_BY_DOING),
                   "policy_runs": len(configuration_grid()) * len(SEEDS) * len(POLICIES) * len(LEARNING_BY_DOING),
                   "episode_records": len(rows)},
        "environment": {"python": sys.version, "platform": platform.platform(),
                         "numpy": _package_version("numpy"), "pytest": _package_version("pytest")},
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (
                              ROOT / "src/hls/hls_lab_v1_integrated.py",
                              ROOT / "src/hls/hls_lab_v1_environment.py",
                              ROOT / "src/hls/hls_lab_dynamic.py",
                              ROOT / "src/hls/hls_lab_v1.py",
                              ROOT / "src/hls/discover_v0.py",
                              ROOT / "src/hls/discover_develop_v2.py",
                              ROOT / "src/hls/synthetic/c5.py",
                              Path(__file__).resolve(),
                          )},
        "artifacts_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in (protocol_path, episode_path, seed_path, paired_path,
                                          paired_aggregate_path, aggregate_path)},
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: ("NA" if value == "" else value)
                          for key, value in row.items()} for row in rows)


def _git_head() -> str:
    import subprocess
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout.strip()


def _package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results/experiments/hls_campaign1_pilot")
    args = parser.parse_args()
    print(json.dumps(run_pilot(args.output), indent=2, sort_keys=True))
