"""Small deterministic plausibility checks for existing HLS v1 mechanisms."""

from __future__ import annotations

import json
import csv
import hashlib
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.hls_lab_dynamic import (  # noqa: E402
    LearningProfile, competence_estimate_matrix, competence_variance_matrix,
    initialize_competence_estimator,
)
from hls.hls_lab_v1 import make_team, ProblemSpec  # noqa: E402
from hls.hls_lab_v1_integrated import (  # noqa: E402
    IntegratedDecisionView, IntegratedProblem, OrganizationMemory,
    OrganizationSnapshot, P0ProductionOnly, P2AdaptiveTeaching, TeachingEfficacy,
    TeachingParameters, _best_action, enumerate_feasible_integrated_actions,
    run_integrated_sequence,
)

RELATION = (0, 1, 0)
PARAMS = TeachingParameters(transfer_rate=0.75, effort=0.25,
    outcome_noise_sd=0.0, production_observation_noise_sd=0.0,
    competence_grid_points=101, competence_prior_variance=0.04,
    efficacy_prior_mean=0.5, efficacy_threshold=0.35, target_competence=0.95)
MIS = LearningProfile(((0.06, 0.03), (0.04, 0.08), (0.02, 0.05)))
# Skill-0 frontier with two unit-effort productive assignments is 1.15;
# skill-1 has a competent reserve specialist for the regime-change scenario.
TEAM = ((0.90, 0.20), (0.20, 0.20), (0.25, 0.80))


def _efficacy(value: float) -> TeachingEfficacy:
    return TeachingEfficacy(tuple(tuple(
        (0.0, 0.0) if teacher == learner else (value, value)
        for learner in range(3)) for teacher in range(3)))


def _problem(index: int, skill: int, level: float = 1.0) -> IntegratedProblem:
    req = (level, 0.0) if skill == 0 else (0.0, level)
    spec = ProblemSpec(f"behavior-{index}-skill{skill}", req, 2.0,
                       max_effort_per_expert=1.0, resource_cost_per_unit=0.2)
    weights = (1.0, 0.0) if skill == 0 else (0.0, 1.0)
    return IntegratedProblem(spec, ces_weights=weights, demand_label=f"skill{skill}")


def _snapshot(team_matrix=TEAM) -> OrganizationSnapshot:
    team = make_team(team_matrix)
    prior_variance = tuple(tuple(min(PARAMS.competence_prior_variance, c * (1.0-c))
                                 for c in row) for row in team.estimated_matrix)
    posterior = initialize_competence_estimator(team.estimated_matrix, prior_variance,
        estimator="grid", grid_points=PARAMS.competence_grid_points)
    return OrganizationSnapshot(team, posterior, OrganizationMemory(), 0)


def _view(snapshot: OrganizationSnapshot, problem: IntegratedProblem,
          horizon: int) -> IntegratedDecisionView:
    feasible = enumerate_feasible_integrated_actions(problem.problem,
                                                       teaching_effort=PARAMS.effort)
    posterior = snapshot.competence_posterior
    return IntegratedDecisionView(0, horizon, problem.problem.problem_id,
        problem.demand_label, problem.problem.requirements,
        problem.problem.resource_budget, problem.problem.max_effort_per_expert,
        competence_estimate_matrix(posterior), competence_variance_matrix(posterior),
        snapshot.organization_memory.efficacy, feasible)


def _paired_intervention(*, horizon: int, efficacy: float, individual_learning: bool,
                         demand_change: bool = False,
                         team_matrix=TEAM) -> dict[str, object]:
    snapshot = _snapshot(team_matrix)
    problems = tuple(_problem(t, 0 if not demand_change or t < horizon // 2 else 1)
                     for t in range(horizon))
    view = _view(snapshot, problems[0], horizon)
    policy = P0ProductionOnly()
    no_teach = policy.choose(view, snapshot.organization_memory, PARAMS)
    candidates = tuple(action for action in view.feasible_actions
        if action.teaching is not None and action.teaching.relation == RELATION)
    teach = _best_action(candidates, view)
    common = dict(learning=MIS, teaching_efficacy=_efficacy(efficacy),
        parameters=PARAMS, individual_learning=individual_learning,
        organizational_learning=True, seed=2501, initial_snapshot=snapshot)
    control = run_integrated_sequence(snapshot.team, problems, policy,
        first_action_override=no_teach, **common)
    treatment = run_integrated_sequence(snapshot.team, problems, policy,
        first_action_override=teach, **common)
    rows = []
    cumulative = 0.0
    for baseline, intervention in zip(control.records, treatment.records):
        delta = intervention.ces_reward - baseline.ces_reward
        cumulative += delta
        rows.append({"period": baseline.period, "baseline_ces": baseline.ces_reward,
            "teaching_ces": intervention.ces_reward, "period_delta": delta,
            "cumulative_delta": cumulative,
            "baseline_competencies": baseline.competence_real_after,
            "teaching_competencies": intervention.competence_real_after})
    return {"horizon": horizon, "efficacy": efficacy,
        "individual_learning": individual_learning, "demand_change": demand_change,
        "intervention": asdict(teach), "baseline_intervention": asdict(no_teach),
        "initial_direct_teaching_gain": treatment.records[0].teaching_gain_real,
        "initial_ces_delta": rows[0]["period_delta"], "delta_v_h": cumulative,
        "initial_production_effort_displaced": (control.records[0].production_effort
                                                  - treatment.records[0].production_effort),
        "initial_resource_used_teach": treatment.records[0].total_resource_used,
        "initial_residual_budget_teach": (problems[0].problem.resource_budget
                                           - treatment.records[0].total_resource_used),
        "final_competencies_control": control.final_team.real_matrix,
        "final_competencies_teach": treatment.final_team.real_matrix,
        "trajectory": rows}


def run_plausibility_checks() -> dict[str, object]:
    scenarios = {
        "S1_adequate": _paired_intervention(horizon=24, efficacy=0.85,
            individual_learning=False, team_matrix=((0.9, 0.2), (0.85, 0.2), (0.8, 0.2))),
        "S2_persistent_deficit_early_effective": _paired_intervention(horizon=24,
            efficacy=0.85, individual_learning=False),
        "S3_short_horizon": _paired_intervention(horizon=8, efficacy=0.85,
            individual_learning=False),
        "S4_weak_teaching": _paired_intervention(horizon=24, efficacy=0.10,
            individual_learning=False),
        "S5_learning_by_doing_on": _paired_intervention(horizon=24, efficacy=0.85,
            individual_learning=True),
        "S6_demand_regime_change": _paired_intervention(horizon=24, efficacy=0.85,
            individual_learning=False, demand_change=True),
    }
    adequate = ((0.90, 0.20), (0.85, 0.20), (0.80, 0.20))
    adequate_snapshot = _snapshot(adequate)
    adequate_problem = _problem(0, 0, 1.0)
    p2_action = P2AdaptiveTeaching((RELATION,)).choose(
        _view(adequate_snapshot, adequate_problem, 24),
        adequate_snapshot.organization_memory, PARAMS)
    return {"scenarios": scenarios,
        "adequate_p2_teaches": p2_action.teaching is not None,
        "note": "One-time specified interventions use P0 continuation; adequate-team P2 choice is separately evaluated. Requirements are fixed at 1.0, below the 1.15 skill-0 frontier of the persistent-deficit team under two unit production assignments. Parameters are not selected by policy outcomes."}


def main() -> None:
    result = run_plausibility_checks()
    output = ROOT / "results/diagnostics/hls_behavioral_plausibility"
    output.mkdir(parents=True, exist_ok=True)
    scenarios = result["scenarios"]
    with (output / "scenario_summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("scenario", "horizon", "efficacy",
            "individual_learning", "demand_change", "initial_ces_delta", "delta_v_h",
            "initial_direct_teaching_gain", "initial_production_effort_displaced",
            "initial_residual_budget_teach"), lineterminator="\n")
        writer.writeheader()
        for name, values in scenarios.items():
            writer.writerow({"scenario": name, **{key: values[key] for key in writer.fieldnames[1:]}})
    with (output / "scenario_trajectory.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("scenario", "period", "baseline_ces",
            "teaching_ces", "period_delta", "cumulative_delta", "learner_skill0_delta"),
            lineterminator="\n")
        writer.writeheader()
        for name, values in scenarios.items():
            for row in values["trajectory"]:
                before = row["baseline_competencies"][1][0]
                after = row["teaching_competencies"][1][0]
                writer.writerow({"scenario": name, "period": row["period"],
                    "baseline_ces": row["baseline_ces"], "teaching_ces": row["teaching_ces"],
                    "period_delta": row["period_delta"], "cumulative_delta": row["cumulative_delta"],
                    "learner_skill0_delta": after - before})
    sources = (Path(__file__), ROOT / "src/hls/hls_lab_v1_integrated.py",
               ROOT / "src/hls/hls_lab_v1.py", ROOT / "src/hls/discover_develop_v2.py",
               ROOT / "src/hls/discover_v0.py", ROOT / "src/hls/hls_lab_v1_environment.py")
    manifest = {"recorded_at": datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="seconds"),
        "command": "python experiments/synthetic/hls_lab_v1/behavioral_plausibility.py",
        "seed": 2501, "scenarios": list(scenarios), "adequate_p2_teaches": result["adequate_p2_teaches"],
        "base_commit": "1f3407913b6af87b8d022fe2575bdae10926022c",
        "parameters": {"requirement_level": 1.0, "resource_budget": 2.0,
            "per_expert_effort_cap": 1.0, "teaching_effort_per_participant": 0.25,
            "transfer_rate": PARAMS.transfer_rate, "efficacy_cases": [0.85, 0.10],
            "horizons": [8, 24], "continuation": "P0 production-only",
            "organizational_learning": True, "noise_sd": 0.0},
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sources},
        "output_sha256": {name: hashlib.sha256((output / name).read_bytes()).hexdigest()
                          for name in ("scenario_summary.csv", "scenario_trajectory.csv")}}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                                          encoding="utf-8")
    print(json.dumps({"scenarios": {name: {key: values[key] for key in (
        "horizon", "initial_ces_delta", "delta_v_h", "initial_direct_teaching_gain",
        "initial_production_effort_displaced", "initial_residual_budget_teach")}
        for name, values in scenarios.items()}, "adequate_p2_teaches": result["adequate_p2_teaches"],
        "outputs": str(output.relative_to(ROOT))}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
