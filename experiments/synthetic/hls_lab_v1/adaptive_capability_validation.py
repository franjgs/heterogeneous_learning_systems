"""Small integration validation of already-existing HLS adaptive capabilities.

Run from the repository root with ``PYTHONPATH=src python
experiments/synthetic/hls_lab_v1/adaptive_capability_validation.py``. This is
not a scientific campaign. The environment fixtures mirror existing tests;
G2 and the four-period imperfect-information reference are reused verbatim.
The command writes a compact, deterministic evidence record and refuses to
replace a different record at the canonical output path.
"""

from __future__ import annotations

import json
import argparse
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from hls.g2_dynamic import D0, D1, D2  # noqa: E402
from hls.hls_lab_nk_environment import (  # noqa: E402
    DemandRegimeNK,
    ExogenousEnvironmentConfigNK,
)
from hls.hls_lab_nk_execution import (  # noqa: E402
    NKEnvironmentRunResult,
    NKInformationRunResult,
    run_nk_production_sequence,
)
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK  # noqa: E402
from hls.hls_lab_nk_learning import LearningProfileNK  # noqa: E402
from hls.hls_lab_nk_geometry import validate_productive_allocation_nk  # noqa: E402
from hls.hls_lab_nk_nembhard import (  # noqa: E402
    NembhardDirectExecutionNK,
    NembhardDirectProfileNK,
    NembhardOutputUnitContract,
)
from hls.hls_lab_nk_execution import NKNembhardDirectRunResult  # noqa: E402
from hls.hls_lab_nk_policies import P0ProductionOnlyPolicyNK  # noqa: E402
from hls.synthetic.c5 import (  # noqa: E402
    MarkovTaskDemand,
    NonStationaryTaskDemand,
    StationaryTaskDemand,
)
from experiments.synthetic.hls_lab_v1.scientific_model_reference import (  # noqa: E402
    build_reference_evidence,
)

SOURCE_REVISION = "8d16f901b238cfce0ca0df884906e8180e0096c3"
OUTPUT = ROOT / "results/analysis/hls_lab_validation/integrated_validation_results.json"
SEED = 731


def _problem(problem_id: str, requirements: tuple[float, ...], budget: float = 2.0):
    return ProblemSpecNK(problem_id, requirements, budget)


def _regime(label: str, problems: tuple[ProblemSpecNK, ...], probabilities=None):
    probabilities = probabilities or (1.0,) * len(problems)
    return DemandRegimeNK(label, problems, probabilities)


def _organization(n: int, k: int) -> OrganizationConfigNK:
    """Reuse the N×K environment-test heterogeneous competence convention."""
    competence = tuple(
        tuple(0.25 + 0.05 * ((i + j) % 3) for j in range(k))
        for i in range(n)
    )
    estimates = tuple(
        tuple(min(1.0, value + 0.05) for value in row)
        for row in competence
    )
    return OrganizationConfigNK(
        tuple(f"a{i}" for i in range(n)),
        tuple(f"s{j}" for j in range(k)),
        competence,
        (1.0,) * n,
        min(float(n), 2.0),
        estimates,
    )


def _choice_catalog(k: int, n: int):
    zero = (0.0,) * k
    axes = tuple(tuple(float(j == skill) for j in range(k)) for skill in range(k))
    return tuple((zero, *axes) for _ in range(n))


def _episode_summary(row) -> dict:
    production = row.production
    return {
        "period": row.period,
        "problem_id": production.problem_id,
        "requirements": production.requirements,
        "allocation": row.action.production,
        "policy": row.policy_name,
        "production_by_agent_skill": production.individual_outputs,
        "production_by_skill": production.outputs,
        "functional_success": production.functional_result.success,
        "normalized_deficit": production.functional_result.normalized_deficit,
        "ces_gross": production.ces_reward,
        "actual_competence_before": row.competence_actual_before,
        "actual_competence_after": row.competence_actual_after,
        "estimated_competence_before": row.competence_estimated_before,
        "estimated_competence_after": row.competence_estimated_after,
        "production_observations": row.production_observations,
        "mis_increment": row.mis_increment,
        "teaching_increment": row.teaching_increment,
        "teaching_action": None if row.action.teaching is None else {
            "teacher_id": row.action.teaching.teacher_id,
            "learner_id": row.action.teaching.learner_id,
            "skill_id": row.action.teaching.skill_id,
            "effort": row.action.teaching.effort,
        },
        "efficacy_memory_before": row.efficacy_memory_before,
        "efficacy_memory_after": row.efficacy_memory_after,
        "productive_effort": row.productive_effort_used,
        "teaching_resource": row.teaching_resource_used,
        "total_resource": row.total_resource_used,
        "policy_updated": row.organization_updated,
    }


def _run_case(name: str, environment: ExogenousEnvironmentConfigNK, *, seed: int,
              policy=None, information_mode: str = "imperfect",
              organization: OrganizationConfigNK | None = None,
              learning_profile: LearningProfileNK | None = None) -> dict:
    n, k = 2, environment.n_skills
    organization = organization or _organization(n, k)
    learning_profile = learning_profile or LearningProfileNK(
        tuple(tuple(0.2 for _ in range(k)) for _ in range(n))
    )
    kwargs = {
        "max_candidates": (4 ** n) if k == 2 else (k + 1) ** n,
        "per_agent_effort_choices": _choice_catalog(k, n) if k != 2 else None,
        "policy": policy or P0ProductionOnlyPolicyNK(),
        "individual_learning": True,
        "learning_profile": learning_profile,
        "information_mode": information_mode,
        "information_seed": seed + 1,
    }
    first = run_nk_production_sequence(
        organization, environment=environment, environment_seed=seed, **kwargs
    )
    replay = run_nk_production_sequence(
        organization, environment=environment, environment_seed=seed, **kwargs
    )
    if not isinstance(first, NKEnvironmentRunResult) or first != replay:
        raise AssertionError(f"{name}: generated environment/runner replay failed")
    if not isinstance(first.execution, NKInformationRunResult):
        raise AssertionError(f"{name}: expected information-aware MIS-v2 execution")
    trajectory = first.trajectory
    records = first.execution.records
    if tuple(row.production.problem_id for row in records) != tuple(
        problem.problem_id for problem in trajectory.problems
    ):
        raise AssertionError(f"{name}: runner did not execute the frozen environment path")
    if any(row.competence_actual_before != row.production.competence_before for row in records):
        raise AssertionError(f"{name}: physical production did not use actual competence")
    all_feasible = all(
        validate_productive_allocation_nk(row.action.production, organization, problem)
        for row, problem in zip(records, trajectory.problems)
    )
    if not all_feasible:
        raise AssertionError(f"{name}: runner emitted an infeasible allocation")
    return {
        "scenario_id": name,
        "status": "PASS",
        "configuration": {
            "N": n,
            "K": k,
            "horizon": environment.horizon,
            "resource_budget": environment.resource_budget,
            "process": type(environment.process).__name__,
            "environment_seed": seed,
            "information_seed": seed + 1,
            "information_mode": information_mode,
            "policy": (policy or P0ProductionOnlyPolicyNK()).name,
            "MIS_v2": "enabled eta=0.2 per agent-skill cell",
            "initial_actual_competence": _organization(n, k).competence_initial,
            "initial_estimated_competence": organization.competence_estimated_initial,
            "effort_limits": organization.effort_limits,
            "collective_effort_budget": organization.collective_effort_budget,
            "MIS_v2_eta": learning_profile.eta,
        },
        "environment": {
            "latent_states": trajectory.latent_states,
            "regime_labels": trajectory.regime_labels,
            "problems": [
                {"problem_id": problem.problem_id,
                 "requirements": problem.requirements,
                 "budget": problem.resource_budget,
                 "ces_weights": problem.ces_weights}
                for problem in trajectory.problems
            ],
        },
        "measurements": {
            "functional_successes": sum(
                row.production.functional_result.success for row in records
            ),
            "periods": len(records),
            "gross_ces_sum": sum(row.production.ces_reward for row in records),
            "normalized_deficit_sum": sum(
                row.production.functional_result.normalized_deficit for row in records
            ),
            "productive_effort_sum": sum(row.productive_effort_used for row in records),
        },
        "trace": [_episode_summary(row) for row in records],
        "checks": {
            "same_seed_exact_replay": True,
            "environment_path_matches_runner_problems": True,
            "production_uses_actual_competence": True,
            "actual_and_estimated_competence_are_separate": all(
                row.competence_actual_before != row.competence_estimated_before
                for row in records
            ),
            "all_actions_respect_runner_feasibility": all_feasible,
        },
    }


def _heterogeneous_nembhard_diagnostic() -> dict:
    """Run a single explicit, feasible allocation with cell-specific k,p,r."""
    organization = OrganizationConfigNK(
        ("a0", "a1"), ("s0", "s1"), ((0.8, 0.2), (0.3, 0.7)),
        (0.5, 1.0), 1.5,
    )
    allocation = ((0.5, 0.0), (0.0, 0.5))
    profile = NembhardDirectProfileNK(
        ((2.0, 1.0), (1.0, 3.0)),
        ((1.0, 0.0), (0.0, 1.0)),
        ((2.0, 1.0), (1.0, 2.0)),
    )
    problem = _problem("heterogeneous-productivity", (0.1, 0.1), 1.5)
    unit_contract = NembhardOutputUnitContract(
        "effort_per_period", "period", "effort_period", "task_output", "task_output"
    )
    config = NembhardDirectExecutionNK(profile, (allocation,), unit_contract)
    result = run_nk_production_sequence(
        organization, (problem,), max_candidates=1, mechanism_id="nembhard_direct",
        nembhard_execution=config,
    )
    if not isinstance(result, NKNembhardDirectRunResult):
        raise AssertionError("Nembhard heterogeneity diagnostic returned the wrong result type")
    row = result.records[0]
    feasible = validate_productive_allocation_nk(allocation, organization, problem)
    if not feasible or row.productivity_before != ((2.0 / 3.0, 0.0), (0.0, 1.0)):
        raise AssertionError("heterogeneous productivity/resource diagnostic failed")
    return {
        "scope": "single-period heterogeneity and feasibility diagnostic; not a campaign",
        "status": "PASS",
        "parameters": {
            "k": profile.asymptotic_productivity,
            "p": profile.prior_experience,
            "r": profile.experience_scale,
        },
        "initial_competence_not_used_by_Nembhard_output": organization.competence_initial,
        "effort_limits": organization.effort_limits,
        "collective_budget": organization.collective_effort_budget,
        "allocation": allocation,
        "productivity_before": row.productivity_before,
        "individual_output": row.individual_outputs,
        "total_output": row.outputs,
        "productive_effort_used": row.productive_effort_used,
        "experience_after": row.experience_after,
        "checks": {
            "cell_specific_productivity_profile_used": True,
            "different_agent_limits_respected": feasible,
            "actual_competence_not_substituted_for_productivity": True,
        },
    }


def build_validation_evidence() -> dict:
    """Execute five bounded checks, reusing established fixtures and models."""
    steady = _run_case(
        "S0_stationary_control",
        ExogenousEnvironmentConfigNK(
            StationaryTaskDemand({"steady": 1.0}),
            {"steady": _regime("stationary", (
                _problem("a", (0.8, 0.2)), _problem("b", (0.2, 0.8)),
            ), (0.6, 0.4))},
            3, 2.0,
        ),
        seed=SEED,
        information_mode="perfect",
        organization=OrganizationConfigNK(
            ("a0", "a1"), ("s0", "s1"),
            ((0.8, 0.15), (0.25, 0.75)), (0.75, 1.0), 1.5,
            ((0.7, 0.2), (0.3, 0.65)),
        ),
        learning_profile=LearningProfileNK(((0.2, 0.05), (0.08, 0.15))),
    )

    # Exact K=3 indexed-distribution fixture from tests/test_hls_lab_nk_environment.py.
    shift = _run_case(
        "S1_nonstationary_runner_integration",
        ExogenousEnvironmentConfigNK(
            NonStationaryTaskDemand({
                0: {"old": 1.0}, 1: {"old": 1.0},
                2: {"new": 1.0}, 3: {"new": 1.0},
            }),
            {
                "old": _regime("old", (_problem("old", (0.7, 0.1, 0.1)),)),
                "new": _regime("new", (_problem("new", (0.1, 0.1, 0.7)),)),
            },
            4, 3.0,
        ),
        seed=4,
    )

    # Reuses C5's existing 0.9/0.1 sticky-transition contract fixture.
    markov = _run_case(
        "S2_markov_runner_integration",
        ExogenousEnvironmentConfigNK(
            MarkovTaskDemand(
                {"x": 0.5, "y": 0.5},
                {"x": {"x": 0.9, "y": 0.1},
                 "y": {"x": 0.1, "y": 0.9}},
            ),
            {
                "x": _regime("markov-x", (_problem("x", (0.7, 0.1)),)),
                "y": _regime("markov-y", (_problem("y", (0.1, 0.7)),)),
            },
            20, 2.0,
        ),
        seed=17,
    )

    # Reuse the canonical G2 analytical controls; not an N×K/MIS-v2 identity.
    g2_p = 0.75
    g2 = {
        "scenario_id": "S3_G2_competence_development_controls",
        "scope": "canonical G2 law, separate from current exponential MIS-v2",
        "demand_probability_p": g2_p,
        "D0_no_evolution": {
            "delta_development": D0.evaluate(g2_p).delta_dev,
            "delta_total": D0.evaluate(g2_p).delta_j,
        },
        "D1_learning_without_frontier_value": {
            "learning_rate": D1.learning_rates,
            "future_state_after_action_1": D1.evaluate(g2_p).action_1.future_state,
            "delta_development": D1.evaluate(g2_p).delta_dev,
        },
        "D2_learning_with_future_value": {
            "learning_rate": D2.learning_rates,
            "future_state_after_action_1": D2.evaluate(g2_p).action_1.future_state,
            "delta_development": D2.evaluate(g2_p).delta_dev,
            "delta_total": D2.evaluate(g2_p).delta_j,
        },
        "checks": {
            "D0_has_zero_development_value": abs(D0.evaluate(g2_p).delta_dev) < 1e-12,
            "D1_changes_state_but_has_zero_development_value": (
                D1.evaluate(g2_p).action_1.future_state != D1.evaluate(g2_p).action_2.future_state
                and abs(D1.evaluate(g2_p).delta_dev) < 1e-12
            ),
            "D2_has_positive_conditional_development_value": D2.evaluate(g2_p).delta_dev > 0,
        },
        "validation_tests": ["tests/test_g2_dynamic.py", "tests/test_hls_lab_nk_learning.py"],
        "status": "PASS",
    }

    # Reuse the existing four-period P2 + Markov + imperfect-info + MIS + teaching trace.
    reference = build_reference_evidence()
    reference_replay = build_reference_evidence()
    execution = reference["execution"]
    if (reference != reference_replay or execution["information_mode"] != "imperfect"
            or len(execution["records"]) != 4):
        raise AssertionError("S4 reference did not preserve its declared information/horizon")
    separate_states = any(
        row["competence_actual_before"] != row["competence_estimated_before"]
        for row in execution["records"]
    )
    mis_recorded = any(any(value != 0.0 for values in row["mis_increment"] for value in values)
                       for row in execution["records"])
    teaching_recorded = any(any(value != 0.0 for values in row["teaching_increment"] for value in values)
                            for row in execution["records"])
    memory_updated = any(row["efficacy_memory_after"] != row["efficacy_memory_before"]
                         for row in execution["records"])
    if not (separate_states and mis_recorded and teaching_recorded and memory_updated):
        raise AssertionError("S4 did not exercise the declared observation/transition/memory channels")
    s4 = {
        "scenario_id": "S4_existing_adaptive_coordination_reference",
        "status": "PASS",
        "source_runner": "experiments/synthetic/hls_lab_v1/scientific_model_reference.py",
        "source_trace_commit": reference["software_commit"],
        "configuration": reference["configuration"],
        "environment": reference["environment_trajectory"],
        "measurements": {
            "periods": len(execution["records"]),
            "policy": execution["records"][0]["policy_name"],
            "final_actual_competence": execution["final_state"]["competence_real"],
            "final_estimated_competence": execution["records"][-1]["competence_estimated_after"],
            "final_efficacy_memory": execution["final_policy_memory"],
            "total_resource": sum(row["total_resource_used"] for row in execution["records"]),
            "functional_successes": sum(
                row["production"]["functional_result"]["success"]
                for row in execution["records"]
            ),
        },
        "trace": [
            {
                "period": row["period"],
                "problem_id": row["production"]["problem_id"],
                "requirements": row["production"]["requirements"],
                "production_action": row["action"]["production"],
                "teaching_action": row["action"]["teaching"],
                "outputs": row["production"]["outputs"],
                "success": row["production"]["functional_result"]["success"],
                "actual_competence_before": row["competence_actual_before"],
                "actual_competence_after": row["competence_actual_after"],
                "estimated_competence_before": row["competence_estimated_before"],
                "estimated_competence_after": row["competence_estimated_after"],
                "observations": row["production_observations"],
                "mis_increment": row["mis_increment"],
                "teaching_increment": row["teaching_increment"],
                "efficacy_memory_before": row["efficacy_memory_before"],
                "efficacy_memory_after": row["efficacy_memory_after"],
                "resource_used": row["total_resource_used"],
            }
            for row in execution["records"]
        ],
        "checks": {
            "reused_existing_saved_reference_trace": True,
            "same_seed_exact_replay": True,
            "decision_mode_is_imperfect": True,
            "true_and_estimated_competence_separate": separate_states,
            "MIS_and_teaching_transitions_recorded": mis_recorded and teaching_recorded,
            "efficacy_memory_recorded": memory_updated,
        },
    }

    return {
        "artifact_type": "bounded_laboratory_capability_validation_not_campaign",
        "model_code_baseline_revision": SOURCE_REVISION,
        "runtime": {"python": platform.python_version()},
        "interpretation_boundary": (
            "Execution and contract validation only; no policy superiority, prevalence, "
            "or full paper reproduction claim."
        ),
        "scenarios": [steady, shift, markov, g2, s4],
        "capability_checks": {
            "stationary_demand_runner": steady["status"],
            "nonstationary_demand_runner": shift["status"],
            "markov_demand_runner": markov["status"],
            "G2_action_dependent_development_controls": g2["status"],
            "imperfect_information_adaptive_teaching_reference": s4["status"],
        },
        "heterogeneous_productivity_diagnostic": _heterogeneous_nembhard_diagnostic(),
        "reproducibility": "The command reconstructs this compact record from fixed seeds and existing fixtures.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replace-generated-record", action="store_true",
        help="replace the artifact generated by this validator if its content differs",
    )
    args = parser.parse_args()
    payload = json.dumps(build_validation_evidence(), indent=2, sort_keys=True, allow_nan=False) + "\n"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        if OUTPUT.read_text() != payload and not args.replace_generated_record:
            raise FileExistsError(f"refusing to replace different validation evidence: {OUTPUT}")
        if OUTPUT.read_text() != payload:
            OUTPUT.write_text(payload)
            print(f"replaced validator-generated record: {OUTPUT.relative_to(ROOT)}")
            return
        print(f"validated existing identical artifact: {OUTPUT.relative_to(ROOT)}")
        return
    OUTPUT.write_text(payload)
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
