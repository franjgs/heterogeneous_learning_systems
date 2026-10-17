"""Focused controls for the Campaign 1 paired pilot."""

from experiments.synthetic.hls_campaign1.run import (
    DEMAND_RELATIONS,
    PARAMETERS,
    P2ScheduledNoFeedback,
    RESOURCE_BUDGET,
    RESOURCE_COST_PER_UNIT,
    TEACHING_EFFORT,
    INITIAL_ESTIMATES,
    _initial_team,
    _write_csv,
    _efficacy,
    _environment,
    configuration_grid,
)
from hls.hls_lab_dynamic import LearningProfile
from hls.hls_lab_v1 import feasible_actions
from hls.hls_lab_v1_integrated import (
    EfficacyEstimate,
    IntegratedProblem,
    OrganizationMemory,
    ProblemSpec,
    P0ProductionOnly,
    P2AdaptiveTeaching,
    enumerate_feasible_integrated_actions,
    run_integrated_sequence,
)


LEARNING = LearningProfile(((0.06, 0.03), (0.04, 0.08), (0.02, 0.05)))
TEAM = _initial_team("low")
HARD_PROBLEMS = tuple(IntegratedProblem(ProblemSpec(
    "hard-axis-1", (0.0, 0.9), 1.0, max_effort_per_expert=1.0,
)) for _ in range(4))


def test_factorial_is_exactly_sixteen_predeclared_configurations():
    grid = configuration_grid()
    assert len(grid) == 16
    assert {row["demand"] for row in grid} == {"stationary", "changing"}
    assert {row["initial_deficit"] for row in grid} == {"low", "high"}
    assert {row["teaching_effectiveness"] for row in grid} == {"low", "high"}
    assert {row["n_periods"] for row in grid} == {8, 24}
    assert TEAM.estimated_matrix == ((0.4, 0.4),) * 3
    assert TEAM.estimated_matrix != TEAM.real_matrix


def test_csv_uses_explicit_na_for_non_applicable_metrics(tmp_path):
    path = tmp_path / "metrics.csv"
    _write_csv(path, [{"metric": "pre_change", "value": ""}])
    assert path.read_text(encoding="utf-8") == "metric,value\npre_change,NA\n"


def test_budget_allows_teaching_and_positive_production_together():
    problems, _ = _environment("stationary", 1, 2026101500)
    problem = problems[0].problem
    min_positive_production = min(
        sum(sum(row) for row in action)
        for action in feasible_actions(problem)
        if sum(sum(row) for row in action) > 0
    )
    integrated = enumerate_feasible_integrated_actions(problem, teaching_effort=TEACHING_EFFORT)
    assert min_positive_production == 1.0
    assert any(action.teaching is not None
               and sum(sum(row) for row in action.production) >= min_positive_production
               for action in integrated)


def test_policy_comparison_uses_identical_frozen_problems_and_is_reproducible():
    problems, latent = _environment("changing", 8, 2026101501)
    assert len(problems) == len(latent) == 8
    assert {x.demand_label for x in problems} == {"observed-demand"}
    assert tuple(latent[:4]) == ("skill0",) * 4
    assert tuple(latent[4:]) == ("skill1",) * 4
    kwargs = dict(learning=LEARNING, teaching_efficacy=_efficacy(0.85),
                  parameters=PARAMETERS, individual_learning=False,
                  seed=2026101501)
    a = run_integrated_sequence(TEAM, problems, P0ProductionOnly(), **kwargs)
    b = run_integrated_sequence(TEAM, problems, P0ProductionOnly(), **kwargs)
    c = run_integrated_sequence(TEAM, problems, P2ScheduledNoFeedback(), **kwargs)
    assert [r.requirements for r in a.records] == [r.requirements for r in b.records]
    assert [r.requirements for r in a.records] == [r.requirements for r in c.records]
    assert [r.action for r in a.records] == [r.action for r in b.records]
    assert [r.competence_real_after for r in a.records] == [r.competence_real_after for r in b.records]
    for run in (a, b, c):
        assert all(row.total_resource_used <= RESOURCE_BUDGET + 1e-12 for row in run.records)
        assert all(row.total_resource_used == row.production_effort + row.teaching_effort
                   for row in run.records)
        assert all(row.resource_cost == row.total_resource_used * RESOURCE_COST_PER_UNIT
                   for row in run.records)


def test_scheduled_control_ignores_formative_memory_but_adaptive_policy_reads_it():
    problems = HARD_PROBLEMS
    weak = OrganizationMemory((EfficacyEstimate((2, 1, 1), 1, 0.0),))
    strong = OrganizationMemory((EfficacyEstimate((2, 1, 1), 1, 1.0),))
    fixed_kwargs = dict(learning=LEARNING, teaching_efficacy=_efficacy(0.85),
                        parameters=PARAMETERS, individual_learning=False,
                        organizational_learning=False, seed=2026101502)
    scheduled_a = run_integrated_sequence(TEAM, problems, P2ScheduledNoFeedback(),
                                          organization_memory=weak, **fixed_kwargs)
    scheduled_b = run_integrated_sequence(TEAM, problems, P2ScheduledNoFeedback(),
                                          organization_memory=strong, **fixed_kwargs)
    assert [r.action for r in scheduled_a.records] == [r.action for r in scheduled_b.records]
    assert scheduled_a.final_organization == weak
    assert scheduled_b.final_organization == strong

    adaptive_kwargs = {**fixed_kwargs, "organizational_learning": True}
    adaptive_a = run_integrated_sequence(TEAM, problems, P2AdaptiveTeaching(DEMAND_RELATIONS),
                                         organization_memory=weak, **adaptive_kwargs)
    adaptive_b = run_integrated_sequence(TEAM, problems, P2AdaptiveTeaching(DEMAND_RELATIONS),
                                         organization_memory=strong, **adaptive_kwargs)
    assert [r.action for r in adaptive_a.records] != [r.action for r in adaptive_b.records]


def test_organizational_learning_switch_suppresses_knowledge_updates_only():
    problems = HARD_PROBLEMS
    kwargs = dict(learning=LEARNING, teaching_efficacy=_efficacy(0.85),
                  parameters=PARAMETERS, individual_learning=False,
                  seed=2026101503)
    full = run_integrated_sequence(TEAM, problems, P2AdaptiveTeaching(DEMAND_RELATIONS),
                                   organizational_learning=True, **kwargs)
    ablated = run_integrated_sequence(TEAM, problems, P2ScheduledNoFeedback(),
                                      organizational_learning=False, **kwargs)
    assert any(row.organization_updated for row in full.records)
    assert not any(row.organization_updated for row in ablated.records)
    assert ablated.final_organization.efficacy == ()
    # Private teaching remains active in the ablation; only organizational
    # learning from its observation is disabled.
    assert any(row.action.teaching is not None for row in ablated.records)
    assert ablated.final_team.real_matrix != TEAM.real_matrix


def test_latent_environment_state_is_not_exposed_to_policy():
    problems, latent = _environment("changing", 8, 2026101504)
    assert latent[0] == "skill0" and latent[-1] == "skill1"

    class PublicViewPolicy:
        name = "PUBLIC_VIEW_CHECK"

        def choose(self, view, memory, parameters):
            assert not hasattr(view, "latent_state")
            assert not hasattr(view, "teaching_efficacy")
            assert view.demand_label == "observed-demand"
            if view.period == 0:
                assert all(abs(view.estimated_competencies[i][k] - INITIAL_ESTIMATES[i][k]) < 1e-12
                           for i in range(3) for k in range(2))
                assert view.estimated_competencies != TEAM.real_matrix
            return P0ProductionOnly().choose(view, memory, parameters)

    run_integrated_sequence(TEAM, problems, PublicViewPolicy(),
                            learning=LEARNING, teaching_efficacy=_efficacy(0.5),
                            individual_learning=False, seed=2026101504)
