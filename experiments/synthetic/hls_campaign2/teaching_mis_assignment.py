"""Prespecified paired teaching x MIS experiment; reuses the integrated runner."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import platform
import subprocess
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime
from math import sqrt
from pathlib import Path
from random import Random
from statistics import mean, stdev
from zoneinfo import ZoneInfo

from hls.hls_lab_dynamic import (
    DemandRegime, LearningProfile, advance_team, competence_estimate_matrix,
    competence_variance_matrix, initialize_competence_estimator,
)
from hls.hls_lab_v1 import ExpertState, TeamState
from hls.hls_lab_v1_environment import ExogenousEnvironmentConfig, generate_environment_trajectory
from hls.hls_lab_v1_integrated import (
    IntegratedDecisionView, OrganizationMemory, OrganizationSnapshot,
    P0ProductionOnly, TeachingEfficacy, TeachingParameters, _best_action,
    enumerate_feasible_integrated_actions, run_integrated_sequence,
)
from hls.synthetic.c5 import NonStationaryTaskDemand, StationaryTaskDemand

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "results/experiments/hls_campaign2_teaching_mis_assignment"
HORIZON = 24
SEEDS = tuple(range(2026101601, 2026101611))
FIXTURE_SEED = 2026101600
RELATION = (0, 1, 0)
LEARNING = LearningProfile(((0.06, 0.03), (0.04, 0.08), (0.02, 0.05)))
PARAMETERS = TeachingParameters(
    transfer_rate=0.75, effort=0.25, outcome_noise_sd=0.02,
    production_observation_noise_sd=0.02, competence_grid_points=101,
    competence_prior_variance=0.0025,
)
SCENARIOS = {
    "A_substitution_candidate": {
        "team": ((0.90, 0.20), (0.45, 0.20), (0.25, 0.80)),
        "change": False,
        "rationale": "Learner 0.45 already exceeds reserve 0.25 in skill 0; both mechanisms can develop an already productive skill.",
    },
    "B_enabling_candidate": {
        "team": ((0.90, 0.20), (0.20, 0.20), (0.25, 0.80)),
        "change": False,
        "rationale": "Learner 0.20 starts below reserve 0.25; the specified lesson can close this rank gap. Participation is endogenous, not prohibited by a gate.",
    },
    "C_demand_change": {
        "team": ((0.90, 0.20), (0.20, 0.20), (0.25, 0.80)),
        "change": True,
        "rationale": "Same team as B; exogenous switch at period 12 from skill 0 to skill 1 changes relevance of the taught skill.",
    },
}
CONDITIONS = {"C00": (False, False), "C10": (True, False),
              "C01": (False, True), "C11": (True, True)}
TOL = 1e-12


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(encode(asdict(value)).encode()).hexdigest()


def protocol():
    return {
        "campaign": "HLS-CAMPAIGN-2-TEACHING-MIS-ASSIGNMENT",
        "hypotheses": {
            "H1": "Teaching may complement MIS when it opens subsequent productive exposure.",
            "H2": "Teaching may substitute for MIS when the learner already exercises the skill.",
            "H3": "The interaction may depend on future demand.",
        },
        "scenarios": SCENARIOS, "horizon": HORIZON, "seeds": SEEDS,
        "deterministic_fixture_seed": FIXTURE_SEED, "conditions": CONDITIONS,
        "intervention_period": 0, "relation": RELATION,
        "efficacy": 0.85, "parameters": asdict(PARAMETERS),
        "learning": asdict(LEARNING), "resource_budget": 2.0,
        "max_effort_per_expert": 1.0, "resource_cost_per_unit": 0.2,
        "requirements": [[1.0, 0.0], [0.0, 1.0]],
        "continuation": "Existing P0ProductionOnly in all conditions; no subsequent teaching.",
        "initial_information": "Explicit calibrated means equal numerical initial skills with variance .0025; same grid posterior and empty efficacy memory in all branches. No policy reads truth.",
        "production_score": "success, -normalized_deficit, margin, -productive_effort",
        "ces_weights": "(1,0) for skill-0 demand and (0,1) for skill-1 demand; fixed before evaluation, no cross-skill synergy",
        "randomness": "Demand fixed by scenario; independent replicate seeds vary indexed individual/formative Gaussian observation innovations; four branches share innovations by coordinate.",
        "negative_control": "Additional deterministic B quadruple at zero efficacy; effort and allocation cost remain.",
        "primary_estimand": "I_R = (R11-R01)-(R10-R00), conditional on scenario, P0 continuation, observation model and fixed initial state.",
        "uncertainty": "Paired seed SD, range, MCSE and percentile bootstrap 95% interval for conditional noise-mean (5000 resamples, seed 2026101599); deterministic fixtures have no interval; no significance tests.",
        "selection": "Three analytical configurations fixed before outcomes; no parameter or policy search.",
    }


def initial_snapshot(scenario, parameters=PARAMETERS):
    matrix = SCENARIOS[scenario]["team"]
    # Priors are explicitly specified experimental inputs, not refreshed from
    # private simulator truth during decisions or continuation.
    team = TeamState(tuple(ExpertState(f"E{i}", tuple(row), tuple(row))
                           for i, row in enumerate(matrix)))
    posterior = initialize_competence_estimator(
        team.estimated_matrix, parameters.competence_prior_variance,
        estimator="grid", grid_points=parameters.competence_grid_points)
    return OrganizationSnapshot(team, posterior, OrganizationMemory(), 0)


def environment(scenario, seed):
    change = SCENARIOS[scenario]["change"]
    emissions = {
        "s0": DemandRegime("s0", ((1.0, 0.0),), (1.0,)),
        "s1": DemandRegime("s1", ((0.0, 1.0),), (1.0,)),
    }
    process = (NonStationaryTaskDemand({t: {"s0" if t < 12 else "s1": 1.0}
                                       for t in range(HORIZON)}) if change
               else StationaryTaskDemand({"s0": 1.0}))
    trajectory = generate_environment_trajectory(
        ExogenousEnvironmentConfig(process, emissions, HORIZON, resource_budget=2.0), seed=seed)
    # CES orientation and resource price are fixed evaluation inputs. Generator,
    # production, functional thresholds and policy score are left intact.
    return tuple(replace(item,
        problem=replace(item.problem, resource_cost_per_unit=0.2),
        ces_weights=(1.0, 0.0) if item.problem.requirements[0] else (0.0, 1.0))
        for item in trajectory.problems)


def initial_actions(snapshot, problem, parameters):
    view = IntegratedDecisionView(
        period=0, periods_remaining=HORIZON, problem_id=problem.problem.problem_id,
        demand_label=problem.demand_label, requirements=problem.problem.requirements,
        resource_budget=problem.problem.resource_budget,
        max_effort_per_expert=problem.problem.max_effort_per_expert,
        estimated_competencies=competence_estimate_matrix(snapshot.competence_posterior),
        competence_variance=competence_variance_matrix(snapshot.competence_posterior),
        efficacy_estimates=snapshot.organization_memory.efficacy,
        feasible_actions=enumerate_feasible_integrated_actions(
            problem.problem, teaching_effort=parameters.effort))
    no_teach = P0ProductionOnly().choose(view, snapshot.organization_memory, parameters)
    teach = _best_action(tuple(a for a in view.feasible_actions
        if a.teaching is not None and a.teaching.relation == RELATION), view)
    return no_teach, teach


def run_quadruple(scenario, seed, *, deterministic=False, efficacy=0.85):
    parameters = (replace(PARAMETERS, outcome_noise_sd=0.0,
                           production_observation_noise_sd=0.0)
                  if deterministic else PARAMETERS)
    snapshot = initial_snapshot(scenario, parameters)
    original = deepcopy(snapshot)
    problems = environment(scenario, seed)
    no_teach, teach = initial_actions(snapshot, problems[0], parameters)
    physics = TeachingEfficacy(tuple(tuple(
        (0.0, 0.0) if i == j else (efficacy, efficacy)
        for j in range(3)) for i in range(3)))
    runs = {}
    for condition, (teaching, mis) in CONDITIONS.items():
        runs[condition] = run_integrated_sequence(
            snapshot.team, problems, P0ProductionOnly(), learning=LEARNING,
            teaching_efficacy=physics, parameters=parameters,
            individual_learning=mis, organizational_learning=True, seed=seed,
            initial_snapshot=deepcopy(snapshot),
            first_action_override=teach if teaching else no_teach)
    assert snapshot == original, "branching contaminated original state"
    assert all(run.snapshots[0] == snapshot for run in runs.values())
    assert runs["C10"].records[0].action == runs["C11"].records[0].action
    assert runs["C00"].records[0].action == runs["C01"].records[0].action
    assert all(record.action.teaching is None
               for run in runs.values() for record in run.records[1:])
    return runs, problems, parameters


def stable_break_even(deltas):
    """First nonnegative cumulative period after a loss that stays nonnegative."""
    cumulative, path = 0.0, []
    for value in deltas:
        cumulative += value
        path.append(cumulative)
    negative = [t for t, value in enumerate(path) if value < -TOL]
    if not negative:
        return "NA"  # no initial cumulative disadvantage to recover
    last_negative = max(negative)
    return last_negative + 1 if last_negative + 1 < len(path) else "NA"


def summarize_quadruple(scenario, seed, runs, kind):
    row = {"scenario": scenario, "seed": seed, "kind": kind}
    for condition, run in runs.items():
        records = run.records
        row[f"R{condition[1:]}"] = sum(r.ces_reward for r in records)
        row[f"success_{condition}"] = mean(r.functional_result.success for r in records)
        row[f"final_competencies_{condition}"] = encode(run.final_team.real_matrix)
        row[f"learner_target_exposure_{condition}"] = sum(r.action.production[1][0] for r in records[1:])
    row["effect_mis_off"] = row["R10"] - row["R00"]
    row["effect_mis_on"] = row["R11"] - row["R01"]
    row["interaction"] = row["effect_mis_on"] - row["effect_mis_off"]
    for mis, baseline, taught in (("off", "C00", "C10"), ("on", "C01", "C11")):
        a, b = runs[baseline].records, runs[taught].records
        row[f"initial_delta_{mis}"] = b[0].ces_reward - a[0].ces_reward
        row[f"break_even_{mis}"] = stable_break_even([y.ces_reward-x.ces_reward for x, y in zip(a, b)])
        row[f"assignment_changes_{mis}"] = sum(x.action.production != y.action.production
                                                 for x, y in zip(a[1:], b[1:]))
        row[f"learner_exposure_delta_{mis}"] = sum(y.action.production[1][0] - x.action.production[1][0]
                                                     for x, y in zip(a[1:], b[1:]))
    return row


def mechanism_rows(scenario, seed, kind, runs, problems):
    rows = []
    for condition, run in runs.items():
        teaching, mis = CONDITIONS[condition]
        for t, record in enumerate(run.records):
            before, after = run.snapshots[t], run.snapshots[t+1]
            mis_team = advance_team(before.team, record.action.production, LEARNING,
                                    enabled=mis, update_estimated=False)
            mis_gain = tuple(tuple(mis_team.real_matrix[i][k] - before.team.real_matrix[i][k]
                                   for k in range(2)) for i in range(3))
            direct = record.teaching_gain_real or 0.0
            for i in range(3):
                for k in range(2):
                    expected = mis_team.real_matrix[i][k] + (direct if (i, k) == (1, 0) else 0)
                    assert abs(expected - after.team.real_matrix[i][k]) <= TOL
            assert record.total_resource_used <= problems[t].problem.resource_budget + TOL
            rows.append({
                "scenario": scenario, "seed": seed, "kind": kind,
                "condition": condition, "teaching_enabled": teaching, "mis_enabled": mis,
                "period": t, "problem_id": record.problem_id,
                "requirements": encode(record.requirements),
                "true_before": encode(record.competence_real_before),
                "true_after": encode(record.competence_real_after),
                "estimated_before": encode(record.competence_estimated_before),
                "estimated_after": encode(record.competence_estimated_after),
                "variance_before": encode(record.competence_variance_before),
                "variance_after": encode(record.competence_variance_after),
                "posterior_before_sha256": hashlib.sha256(encode(asdict_cell(before.competence_posterior)).encode()).hexdigest(),
                "memory_before": encode([asdict(x) for x in record.efficacy_estimates_before]),
                "memory_after": encode([asdict(x) for x in record.efficacy_estimates_after]),
                "production": encode(record.action.production),
                "action_id": record.production_action_id,
                "individual_outputs": encode(record.individual_outputs),
                "outputs": encode(record.outputs),
                "individual_observations": encode(record.individual_observations),
                "teaching_observation": record.teaching_observation if record.teaching_observation is not None else "NA",
                "direct_teaching_gain": direct, "mis_gain": encode(mis_gain),
                "learner_target_mis_gain": mis_gain[1][0],
                "learner_target_effort": record.action.production[1][0],
                "learner_total_effort": sum(record.action.production[1]),
                "experience_before": encode([e.experience for e in before.team.experts]),
                "experience_after": encode([e.experience for e in after.team.experts]),
                "ces": record.ces_reward, "cumulative_ces": record.cumulative_ces_reward,
                "success": record.functional_result.success,
                "normalized_deficit": record.functional_result.normalized_deficit,
                "production_effort": record.production_effort,
                "teaching_effort": record.teaching_effort,
                "resources_used": record.total_resource_used,
                "unused_capacity": problems[t].problem.resource_budget-record.total_resource_used,
                "resource_cost": record.resource_cost,
            })
    return rows


def asdict_cell(posterior):
    return [[asdict(cell) for cell in row] for row in posterior]


def _quantile(values, fraction):
    ordered = sorted(values)
    index = (len(ordered)-1)*fraction
    lower = int(index)
    upper = min(lower+1, len(ordered)-1)
    return ordered[lower] + (index-lower)*(ordered[upper]-ordered[lower])


def interaction_summaries(outcomes):
    result = []
    for scenario in SCENARIOS:
        selected = [r for r in outcomes if r["scenario"] == scenario and r["kind"] == "noisy"]
        values = [r["interaction"] for r in selected]
        rng = Random(2026101599)
        boot = [mean(rng.choices(values, k=len(values))) for _ in range(5000)]
        result.append({"scenario": scenario, "n": len(values),
            **{key: mean(r[key] for r in selected) for key in
               ("R00", "R10", "R01", "R11", "effect_mis_off", "effect_mis_on")},
            "interaction_mean": mean(values), "interaction_sd": stdev(values),
            "interaction_mcse": stdev(values)/sqrt(len(values)),
            "interaction_min": min(values), "interaction_max": max(values),
            "bootstrap_mean_ci95_low": _quantile(boot, .025),
            "bootstrap_mean_ci95_high": _quantile(boot, .975),
            "positive": sum(v > TOL for v in values),
            "negative": sum(v < -TOL for v in values),
            "neutral": sum(abs(v) <= TOL for v in values)})
    return result


def write_csv(path, rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    data = buffer.getvalue().encode()
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == ".gz" else data)


def prepare(output):
    output.mkdir(parents=True, exist_ok=True)
    path = output / "protocol.json"
    content = json.loads(encode(protocol()))
    if path.exists():
        if json.loads(path.read_text())["configuration"] != content:
            raise RuntimeError("refusing to change a previously recorded protocol")
        return
    path.write_text(json.dumps({
        "registered_at": datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="seconds"),
        "configuration": content, "runner_sha256_at_registration": sha(__file__),
    }, indent=2, sort_keys=True)+"\n")


def execute(output):
    protocol_path = output / "protocol.json"
    saved = json.loads(protocol_path.read_text())
    if saved["configuration"] != json.loads(encode(protocol())):
        raise RuntimeError("configuration differs from registered protocol")
    if (output / "manifest.json").exists():
        raise RuntimeError("refusing to overwrite an existing campaign; use a new output directory")
    started = datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="seconds")
    outcomes, traces, controls = [], [], []
    for scenario in SCENARIOS:
        for kind, seeds in (("deterministic", (FIXTURE_SEED,)), ("noisy", SEEDS)):
            for seed in seeds:
                runs, problems, _ = run_quadruple(scenario, seed, deterministic=kind == "deterministic")
                outcomes.append(summarize_quadruple(scenario, seed, runs, kind))
                traces.extend(mechanism_rows(scenario, seed, kind, runs, problems))
            print(f"{scenario}: {kind} {len(seeds)} matched quadruples", flush=True)
    runs, problems, _ = run_quadruple("B_enabling_candidate", FIXTURE_SEED,
                                     deterministic=True, efficacy=0.0)
    control_rows = mechanism_rows("B_enabling_candidate", FIXTURE_SEED, "zero_efficacy", runs, problems)
    assert all(r["direct_teaching_gain"] == 0 for r in control_rows)
    assert all(r["learner_target_mis_gain"] == 0 for r in traces if not r["mis_enabled"])
    assert runs["C00"].final_team.real_matrix == runs["C00"].snapshots[0].team.real_matrix
    controls.append(summarize_quadruple("B_enabling_candidate", FIXTURE_SEED, runs, "zero_efficacy"))
    traces.extend(control_rows)
    write_csv(output / "paired_outcomes.csv", outcomes)
    write_csv(output / "mechanism_traces.csv.gz", traces)
    write_csv(output / "interaction_summary.csv", interaction_summaries(outcomes))
    write_csv(output / "negative_control_outcomes.csv", controls)
    (output / "initial_states.json").write_text(json.dumps({
        name: asdict(initial_snapshot(name)) for name in SCENARIOS}, sort_keys=True)+"\n")
    sources = [Path(__file__), ROOT / "src/hls/hls_lab_v1_integrated.py",
        ROOT / "src/hls/hls_lab_v1_environment.py", ROOT / "src/hls/hls_lab_dynamic.py",
        ROOT / "src/hls/hls_lab_v1.py", ROOT / "src/hls/discover_v0.py",
        ROOT / "src/hls/discover_develop_v2.py", ROOT / "src/hls/synthetic/c5.py"]
    manifest = {
        "status": "COMPLETE", "started_at": started,
        "completed_at": datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="seconds"),
        "repository_base": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "command": "PYTHONPATH=src:. python -m experiments.synthetic.hls_campaign2.teaching_mis_assignment",
        "main_quadruples": 33, "noisy_quadruples": 30, "deterministic_quadruples": 3,
        "negative_control_quadruples": 1, "policy_runs": 136,
        "trace_rows": len(traces), "python": platform.python_version(),
        "platform": platform.platform(), "continuation": "P0ProductionOnly",
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sources},
        "output_sha256": {p.name: sha(p) for p in sorted(output.iterdir()) if p.is_file()},
        "limitations": ["Additive production", "Discrete catalogue and stranded resources",
            "Gross CES; separate resource costs", "Policy optimizes functional score, not CES",
            "Conditional on P0 continuation", "Assignment changes are not identified causal mediation",
            "Seed variability is observation noise only; demand path fixed per scenario",
            "Calibrated initial means; finite grid and approximate teaching posterior",
            "Repository full suite has 13 historical provenance/integrity failures"],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status": "COMPLETE", "quadruples": 34, "trace_rows": len(traces),
                      "summary": interaction_summaries(outcomes)}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--prepare", action="store_true", help="Register design only; do not simulate")
    args = parser.parse_args()
    if args.prepare:
        prepare(args.output)
    else:
        execute(args.output)


if __name__ == "__main__":
    main()
