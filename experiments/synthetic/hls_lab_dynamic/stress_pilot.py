"""Paired stress pilot for existing HLS dynamic-laboratory organizations.

Scenario thresholds are selected by exhaustive production-frontier checks,
before comparing policy outcomes. No policy or physical mechanism is added.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from random import Random
from time import time

from hls.discover_v0 import JOINT_ACTIONS, THETA_1, production_inputs, ces_reward
from hls.hls_lab_dynamic import (
    CompetenceInformationMode as Info, DemandRegime, DiscoverBeliefPolicy,
    LearningProfile, UncertainProblem, generate_uncertain_problems,
    run_belief_sequence, run_dynamic_sequence,
)
from hls.hls_lab_v1 import (
    ExploreThenGreedy, GreedyAdaptive, OrganizationState, ProblemSpec,
    evaluate_problem, feasible_actions, make_team,
)

SEEDS = tuple(range(8))
BOOTSTRAPS = 5000
BOOTSTRAP_SEED = 20261016
N_PROBLEMS = 8
PRIOR = 0.5
SIGMA = 0.08
SKILL_SIGMA = 0.06
SIMILAR = ((0.55, 0.45),) * 3
HETEROGENEOUS = ((0.82, 0.18), (0.18, 0.82), (0.50, 0.50))
PARTIAL = ((0.55, 0.45),) * 3
SLOW = LearningProfile(((0.03, 0.03),) * 3)
FAST = LearningProfile(((0.25, 0.25),) * 3)

BALANCED_NEAR_FRONTIER = (0.62, 0.62)
COMPLEMENTARY = (0.90, 0.90)
EAST_REQ = (1.20, 0.25)
WEST_REQ = (0.25, 1.20)
RESTRICTED_REQ = (0.21, 0.21)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frontier(team, budget=3.0):
    actions = tuple(a for a in JOINT_ACTIONS if sum(sum(row) for row in a) <= budget + 1e-12)
    values = tuple(production_inputs(team, action) for action in actions)
    return {
        "action_count": len(actions),
        "max_each": tuple(max(y[k] for y in values) for k in range(2)),
        "max_balanced": max(min(y) for y in values),
        "success_count": lambda req: sum(evaluate_problem(y, req).success for y in values),
    }


def validate_scenarios():
    sim = frontier(SIMILAR)
    het = frontier(HETEROGENEOUS)
    assert sim["action_count"] == het["action_count"] == 64
    assert BALANCED_NEAR_FRONTIER[0] < sim["max_balanced"]
    assert BALANCED_NEAR_FRONTIER[1] < sim["max_balanced"]
    assert COMPLEMENTARY[0] > sim["max_balanced"]
    assert COMPLEMENTARY[1] < het["max_balanced"]
    assert sim["success_count"](BALANCED_NEAR_FRONTIER) > 0
    assert het["success_count"](BALANCED_NEAR_FRONTIER) > 0
    assert sim["success_count"](COMPLEMENTARY) == 0
    assert het["success_count"](COMPLEMENTARY) > 0
    tight = frontier(SIMILAR, budget=1.5)
    assert tight["action_count"] == 10
    assert 0 < tight["success_count"](RESTRICTED_REQ) < tight["action_count"]
    return sim, het, tight


def dynamic_sequence(seed: int, scenario: str):
    if scenario == "balanced_near_frontier":
        schedule = ((DemandRegime("balanced", (BALANCED_NEAR_FRONTIER,), (1.0,)), N_PROBLEMS),)
    elif scenario == "complementary_static":
        schedule = ((DemandRegime("complementary", (COMPLEMENTARY,), (1.0,)), N_PROBLEMS),)
    elif scenario == "switching_orientation":
        east = DemandRegime("east_requirement", (EAST_REQ,), (1.0,))
        west = DemandRegime("west_requirement", (WEST_REQ,), (1.0,))
        schedule = ((east, 4), (west, 4))
    else:
        raise ValueError(scenario)
    generated = generate_uncertain_problems(
        schedule, problem_seed=181000 + seed, environment_seed=182000 + seed,
        prior=PRIOR, budget=3.0,
    )
    return tuple(UncertainProblem(replace(x.problem, resource_cost_per_unit=1.0), x.theta)
                 for x in generated)


def execute_belief(policy, seed, problems, team_state, mode, learning, li, horizon):
    team = make_team(team_state) if mode == "ORACLE" else None
    if mode != "ORACLE":
        from hls.hls_lab_dynamic import make_dynamic_team
        team = make_dynamic_team(team_state, information_mode=Info(mode),
                                 estimated_competencies=PARTIAL)
    return run_belief_sequence(
        team, problems, policy, learning=learning, decision_horizon=horizon,
        individual_learning=li, prior=PRIOR, sigma=SIGMA,
        noise_seed=183000 + seed, competence_observation_sigma=SKILL_SIGMA,
        competence_noise_seed=184000 + seed, information_mode=Info(mode),
    )


def mean_ci(values, seed=BOOTSTRAP_SEED):
    rng = Random(seed)
    n = len(values)
    means = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n
                   for _ in range(BOOTSTRAPS))
    return sum(values) / n, means[int(.025 * BOOTSTRAPS)], means[int(.975 * BOOTSTRAPS)]


def summarize(result, block, scenario, team_kind, horizon, seed, phase):
    records = result.records
    eps = [r.episode if hasattr(r, "true_expected_reward") else r for r in records]
    err = [abs(a-b) for e in eps for er, rr in zip(e.estimated_before, e.competence_before)
           for a, b in zip(er, rr)]
    total_reward = (result.cumulative_true_expected_reward
                    if hasattr(result, "cumulative_true_expected_reward")
                    else sum(ces_reward(e.outputs, THETA_1) for e in eps))
    return {
        "block": block, "scenario": scenario, "team": team_kind,
        "horizon": horizon, "seed": seed, "phase": phase,
        "policy": result.policy, "decisions": len(eps),
        "success_rate": sum(e.success for e in eps) / len(eps),
        "cumulative_mu_true": total_reward,
        "mean_normalized_deficit": sum(e.normalized_deficit for e in eps) / len(eps),
        "resource_cost": sum(e.resource_cost for e in eps),
        "effort": sum(e.effort for e in eps),
        "competence_mae": sum(err) / len(err) if err else 0.0,
        "unique_actions": len({e.action_id for e in eps}),
        "second_segment_success": (
            sum(e.success for e in eps[len(eps)//2:]) / len(eps[len(eps)//2:])
            if scenario == "switching_orientation" else ""),
        "second_segment_mu_true": (
            sum((r.true_expected_reward if hasattr(r, "true_expected_reward")
                 else ces_reward(r.outputs, THETA_1)) for r in records[len(records)//2:])
            if scenario == "switching_orientation" else ""),
        "final_competencies": json.dumps(result.final_team.real_matrix),
    }


def trace_rows(result, block, scenario, team_kind, horizon, seed, phase):
    for r in result.records:
        e = r.episode if hasattr(r, "true_expected_reward") else r
        yield {
            "block": block, "scenario": scenario, "team": team_kind,
            "horizon": horizon, "seed": seed, "phase": phase,
            "problem_episode": getattr(r, "problem_episode", e.episode),
            "decision_in_problem": getattr(r, "decision_in_problem", 0),
            "problem_id": e.problem_id,
            "environment": getattr(r, "true_environment_type", "fixed_theta1_no_belief_model"),
            "requirements": json.dumps(e.requirements),
            "belief_before": getattr(r, "belief_before", ""),
            "belief_after": getattr(r, "belief_after", ""),
            "action_id": e.action_id, "success": int(e.success),
            "mu_true": (r.true_expected_reward if hasattr(r, "true_expected_reward")
                        else ces_reward(e.outputs, THETA_1)),
            "normalized_deficit": e.normalized_deficit,
            "resource_cost": e.resource_cost, "effort": e.effort,
            "competence_before": json.dumps(e.competence_before),
            "competence_after": json.dumps(e.competence_after),
            "estimated_before": json.dumps(e.estimated_before),
            "estimated_after": json.dumps(e.estimated_after),
        }


def run(output_dir: Path):
    validate_scenarios()
    output_dir.mkdir(parents=True, exist_ok=False)
    summaries, traces = [], []
    paired = {}
    # Deliberately sparse matrix: each block targets a stated mechanism.
    design = [
        ("balanced_near_frontier", team, h)
        for team in ("similar", "heterogeneous") for h in (1, 3)
    ] + [("complementary_static", team, 1) for team in ("similar", "heterogeneous")]
    design += [("switching_orientation", team, 3) for team in ("similar", "heterogeneous")]
    for scenario, team_kind, horizon in design:
        state = SIMILAR if team_kind == "similar" else HETEROGENEOUS
        for seed in SEEDS:
            problems = dynamic_sequence(seed, scenario)
            arms = [
                ("GREEDY_ORACLE_LI_OFF", GreedyAdaptive(), "ORACLE", SLOW, False),
                ("DISCOVER_ORACLE_LI_OFF", DiscoverBeliefPolicy(), "ORACLE", SLOW, False),
                ("GREEDY_PARTIAL_STATIC_LI_OFF", GreedyAdaptive(), "PARTIAL_STATIC", SLOW, False),
                ("GREEDY_PARTIAL_LEARNING_LI_OFF", GreedyAdaptive(), "PARTIAL_LEARNING", SLOW, False),
                ("GREEDY_ORACLE_LI_ON_SLOW", GreedyAdaptive(), "ORACLE", SLOW, True),
                ("GREEDY_ORACLE_LI_ON_FAST", GreedyAdaptive(), "ORACLE", FAST, True),
            ]
            current = {}
            for label, policy, mode, learning, li in arms:
                res = execute_belief(policy, seed, problems, state, mode, learning, li, horizon)
                current[label] = res
                summaries.append(summarize(res, "full_catalog", scenario, team_kind, horizon, seed, label))
                traces.extend(trace_rows(res, "full_catalog", scenario, team_kind, horizon, seed, label))
            contrasts = [
                ("discover_minus_greedy", "DISCOVER_ORACLE_LI_OFF", "GREEDY_ORACLE_LI_OFF"),
                ("partial_static_minus_oracle", "GREEDY_PARTIAL_STATIC_LI_OFF", "GREEDY_ORACLE_LI_OFF"),
                ("partial_updated_minus_static", "GREEDY_PARTIAL_LEARNING_LI_OFF", "GREEDY_PARTIAL_STATIC_LI_OFF"),
                ("individual_learning_slow_minus_off", "GREEDY_ORACLE_LI_ON_SLOW", "GREEDY_ORACLE_LI_OFF"),
                ("individual_learning_fast_minus_off", "GREEDY_ORACLE_LI_ON_FAST", "GREEDY_ORACLE_LI_OFF"),
            ]
            for cname, left, right in contrasts:
                a, b = current[left], current[right]
                diffs = paired.setdefault((scenario, team_kind, horizon, cname), {})
                diffs[seed] = {
                    "mu_true": a.cumulative_true_expected_reward-b.cumulative_true_expected_reward,
                    "success_count": sum(r.episode.success for r in a.records)-sum(r.episode.success for r in b.records),
                    "cost": sum(r.episode.resource_cost for r in a.records)-sum(r.episode.resource_cost for r in b.records),
                    "deficit": sum(r.episode.normalized_deficit for r in a.records)-sum(r.episode.normalized_deficit for r in b.records),
                }

    # Tight-resource control: 10 feasible arms at budget 1.5. DISCOVER is
    # omitted because its frozen adapter requires the complete 64-action set.
    tight = ProblemSpec("tight-frontier", RESTRICTED_REQ, 1.5,
                        resource_cost_per_unit=1.0)
    assert len(feasible_actions(tight)) == 10
    for team_kind, state in (("similar", SIMILAR), ("heterogeneous", HETEROGENEOUS)):
        for seed in SEEDS:
            for lo in (False, True):
                org = ExploreThenGreedy()
                trained = run_dynamic_sequence(make_team(state), (tight,)*10, org,
                    learning=SLOW, individual_learning=False,
                    organizational_learning=lo, seed=seed,
                    initial_organization_state=OrganizationState())
                frozen = run_dynamic_sequence(make_team(state), (tight,)*20, org,
                    learning=SLOW, individual_learning=False,
                    organizational_learning=False, seed=seed,
                    initial_organization_state=trained.final_organization)
                summaries.append(summarize(trained, "tight_resource_train", "tight_frontier", team_kind, 1, seed, f"LO_{int(lo)}_TRAIN"))
                summaries.append(summarize(frozen, "tight_resource_eval", "tight_frontier", team_kind, 1, seed, f"LO_{int(lo)}_EVAL"))
                traces.extend(trace_rows(trained, "tight_resource_train", "tight_frontier", team_kind, 1, seed, f"LO_{int(lo)}_TRAIN"))
                traces.extend(trace_rows(frozen, "tight_resource_eval", "tight_frontier", team_kind, 1, seed, f"LO_{int(lo)}_EVAL"))
            # Paired deterministic outcomes retained; duplicate seeds are not
            # treated as independent random evidence in the report.
            a = next(x for x in summaries if x["block"] == "tight_resource_eval" and x["team"] == team_kind and x["seed"] == seed and x["phase"] == "LO_1_EVAL")
            b = next(x for x in summaries if x["block"] == "tight_resource_eval" and x["team"] == team_kind and x["seed"] == seed and x["phase"] == "LO_0_EVAL")
            paired.setdefault(("tight_frontier", team_kind, 1, "tabular_on_minus_off"), {})[seed] = {
                "mu_true": float(a["cumulative_mu_true"])-float(b["cumulative_mu_true"]),
                "success_count": float(a["success_rate"])*20-float(b["success_rate"])*20,
                "cost": float(a["resource_cost"])-float(b["resource_cost"]),
                "deficit": float(a["mean_normalized_deficit"])*20-float(b["mean_normalized_deficit"])*20,
            }

    contrasts_out = []
    for key, by_seed in sorted(paired.items()):
        for metric in ("mu_true", "success_count", "cost", "deficit"):
            vals = [by_seed[s][metric] for s in SEEDS]
            mean, lo, hi = mean_ci(vals)
            contrasts_out.append({"scenario": key[0], "team": key[1], "horizon": key[2],
                "contrast": key[3], "outcome": metric, "mean_paired_difference": mean,
                "bootstrap_95_low": lo, "bootstrap_95_high": hi,
                "paired_seeds": len(vals), "bootstrap_replicates": BOOTSTRAPS})

    def write_csv(path, rows):
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
    summary_path = output_dir / "run_summary.csv"
    trace_path = output_dir / "decision_traces.csv"
    contrasts_path = output_dir / "paired_contrasts.csv"
    write_csv(summary_path, summaries); write_csv(trace_path, traces); write_csv(contrasts_path, contrasts_out)
    sim, het, tight_frontier = validate_scenarios()
    manifest = {
        "protocol": "hls-dynamic-stress-pilot-v1", "created_unix": time(),
        "base_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "python": sys.version, "platform": platform.platform(), "seeds": list(SEEDS),
        "bootstrap": {"B": BOOTSTRAPS, "seed": BOOTSTRAP_SEED, "unit": "paired history seed"},
        "definitions": {"similar": SIMILAR, "heterogeneous": HETEROGENEOUS,
            "balanced_near_frontier": BALANCED_NEAR_FRONTIER,
            "complementary": COMPLEMENTARY, "switching": [EAST_REQ, WEST_REQ],
            "tight_budget": 1.5, "tight_requirements": RESTRICTED_REQ,
            "full_catalog_budget": 3.0, "H": [1, 3], "N_problems": N_PROBLEMS,
            "prior": PRIOR, "aggregate_sigma": SIGMA, "individual_sigma": SKILL_SIGMA,
            "eta_slow": SLOW.eta, "eta_fast": FAST.eta},
        "frontier_checks": {"similar_max_balanced": sim["max_balanced"],
            "heterogeneous_max_balanced": het["max_balanced"],
            "tight_feasible_action_count": tight_frontier["action_count"],
            "discover_excluded_from_tight_budget_reason": "frozen DISCOVER adapter requires all 64 JOINT_ACTIONS feasible"},
        "runs": len(summaries), "decisions": len(traces),
        "source_sha256": {p: sha(Path(p)) for p in (
            "src/hls/hls_lab_v1.py", "src/hls/hls_lab_dynamic.py",
            "experiments/synthetic/hls_lab_dynamic/stress_pilot.py")},
        "artifact_sha256": {p.name: sha(p) for p in (summary_path, trace_path, contrasts_path)},
        "no_policy_or_physics_changes": True,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"output_dir": str(output_dir), **manifest}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
        default=Path("results/experiments/hls_dynamic_stress_pilot"))
    args = parser.parse_args()
    run(args.output_dir)


if __name__ == "__main__":
    main()
