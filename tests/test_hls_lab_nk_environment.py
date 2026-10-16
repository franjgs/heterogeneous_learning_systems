from dataclasses import replace

import pytest

from hls.hls_lab_dynamic import DemandRegime
from hls.hls_lab_nk_environment import (
    DemandRegimeNK,
    ExogenousEnvironmentConfigNK,
    generate_environment_trajectory_nk,
)
from hls.hls_lab_nk_execution import NKEnvironmentRunResult, run_nk_production_sequence
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK
from hls.hls_lab_nk_policies import (
    P0ProductionOnlyPolicyNK,
    P1FixedTeachingNK,
    P2AdaptiveTeachingNK,
    TeachingPolicyParametersNK,
)
from hls.hls_lab_nk_teaching import TeachingEfficacyNK
from hls.hls_lab_v1_environment import (
    ExogenousEnvironmentConfig,
    generate_environment_trajectory,
)
from hls.synthetic.c5 import MarkovTaskDemand, NonStationaryTaskDemand, StationaryTaskDemand


def _problem(problem_id, requirements, budget=2.0, weights=None):
    return ProblemSpecNK(problem_id, tuple(requirements), budget, weights)


def _regime(label, problems, probabilities=None):
    return DemandRegimeNK(label, tuple(problems), tuple(probabilities or (1.0,) * len(problems)))


def _org(n, k):
    return OrganizationConfigNK(
        tuple(f"a{i}" for i in range(n)), tuple(f"s{j}" for j in range(k)),
        tuple(tuple(0.25 + 0.05 * ((i + j) % 3) for j in range(k)) for i in range(n)),
        (1.0,) * n, min(float(n), 2.0),
    )


@pytest.mark.parametrize(("n", "k"), ((1, 1), (2, 2), (3, 2), (4, 3)))
def test_environment_emits_configured_nk_problems_reproducibly(n, k):
    types = (
        _problem("type-a", tuple(0.2 + 0.03 * j for j in range(k))),
        _problem("type-b", tuple(0.1 + 0.05 * j for j in range(k)), weights=(1.0,) + (0.0,) * (k - 1)),
    )
    config = ExogenousEnvironmentConfigNK(
        StationaryTaskDemand({"steady": 1.0}), {"steady": _regime("steady", types, (0.4, 0.6))}, 12, 1.25
    )
    first = generate_environment_trajectory_nk(config, seed=321)
    assert first == generate_environment_trajectory_nk(config, seed=321)
    assert len(first.problems) == 12
    assert all(len(p.requirements) == k and p.resource_budget == 1.25 for p in first.problems)
    assert set(p.problem_id for p in first.problems) <= {"type-a", "type-b"}
    assert first.latent_states == ("steady",) * 12
    assert first.regime_labels == ("steady",) * 12


def test_markov_demand_uses_existing_transitions_and_is_frozen_before_policies():
    problems = {"x": _regime("x-emission", (_problem("x", (0.8, 0.1)),)),
                "y": _regime("y-emission", (_problem("y", (0.1, 0.8)),))}
    process = MarkovTaskDemand(
        {"x": 1.0, "y": 0.0},
        {"x": {"x": 0.0, "y": 1.0}, "y": {"x": 0.0, "y": 1.0}},
    )
    trajectory = generate_environment_trajectory_nk(
        ExogenousEnvironmentConfigNK(process, problems, 5, 2.0), seed=13
    )
    assert trajectory.latent_states == ("x", "y", "y", "y", "y")
    assert trajectory.regime_labels == ("x-emission", "y-emission", "y-emission", "y-emission", "y-emission")
    assert tuple(p.requirements for p in trajectory.problems) == ((0.8, 0.1),) + ((0.1, 0.8),) * 4


def test_independent_environment_seeds_control_distinct_demand_realizations():
    config = ExogenousEnvironmentConfigNK(
        StationaryTaskDemand({"x": 0.5, "y": 0.5}),
        {"x": _regime("x", (_problem("x", (0.5,)),)),
         "y": _regime("y", (_problem("y", (0.2,)),))},
        12,
    )
    first = generate_environment_trajectory_nk(config, seed=100)
    other_seed = generate_environment_trajectory_nk(config, seed=101)
    assert first.seed == 100 and other_seed.seed == 101
    assert first.latent_states != other_seed.latent_states
    assert first.problems != other_seed.problems


def test_nonstationary_process_changes_only_at_existing_indexed_times():
    emissions = {
        "old": _regime("old", (_problem("old", (0.7, 0.1, 0.1)),)),
        "new": _regime("new", (_problem("new", (0.1, 0.1, 0.7)),)),
    }
    config = ExogenousEnvironmentConfigNK(
        NonStationaryTaskDemand({0: {"old": 1.0}, 1: {"old": 1.0}, 2: {"new": 1.0}, 3: {"new": 1.0}}),
        emissions, 4, 3.0,
    )
    trajectory = generate_environment_trajectory_nk(config, seed=4)
    assert trajectory.latent_states == ("old", "old", "new", "new")
    assert trajectory.regime_labels == ("old", "old", "new", "new")
    with pytest.raises(ValueError, match="no distribution"):
        replace(config, horizon=5)


def test_stationary_and_markov_configuration_validation():
    with pytest.raises(ValueError, match="share K"):
        DemandRegimeNK("bad", (_problem("a", (0.2,)), _problem("b", (0.2, 0.3))), (0.5, 0.5))
    with pytest.raises(ValueError, match="sum to one"):
        DemandRegimeNK("bad", (_problem("a", (0.2,)),), (0.8,))
    with pytest.raises(ValueError, match="missing emission"):
        ExogenousEnvironmentConfigNK(StationaryTaskDemand({"missing": 1.0}),
                                     {"other": _regime("other", (_problem("a", (0.2,)),))}, 1)
    with pytest.raises(ValueError, match="resource_budget"):
        replace(ExogenousEnvironmentConfigNK(StationaryTaskDemand({"x": 1.0}),
                                             {"x": _regime("x", (_problem("a", (0.2,)),))}, 1),
                resource_budget=float("nan"))


def test_legacy_3x2_environment_emission_equivalence():
    legacy_regime = DemandRegime("historical", ((0.7, 0.1), (0.1, 0.7)), (0.3, 0.7))
    legacy = generate_environment_trajectory(
        ExogenousEnvironmentConfig(StationaryTaskDemand({"steady": 1.0}),
                                   {"steady": legacy_regime}, 20, 1.75), seed=902
    )
    nk_regime = _regime("historical", (
        _problem("unused-0", (0.7, 0.1)), _problem("unused-1", (0.1, 0.7)),
    ), (0.3, 0.7))
    nk = generate_environment_trajectory_nk(
        ExogenousEnvironmentConfigNK(StationaryTaskDemand({"steady": 1.0}),
                                     {"steady": nk_regime}, 20, 1.75), seed=902
    )
    assert tuple(p.problem.problem_id for p in legacy.problems) == tuple(p.problem_id for p in nk.problems)
    assert tuple(p.problem.requirements for p in legacy.problems) == tuple(p.requirements for p in nk.problems)
    assert tuple(p.ces_weights for p in legacy.problems) == tuple(p.ces_weights for p in nk.problems)
    assert tuple(p.problem.resource_budget for p in legacy.problems) == tuple(p.resource_budget for p in nk.problems)
    assert legacy.latent_states == nk.latent_states


def test_one_frozen_path_is_reusable_across_organizations_with_same_k():
    config = ExogenousEnvironmentConfigNK(
        StationaryTaskDemand({"r": 1.0}),
        {"r": _regime("r", (_problem("a", (0.7, 0.2)), _problem("b", (0.2, 0.7))), (0.5, 0.5))},
        2, 2.0,
    )
    trajectory = generate_environment_trajectory_nk(config, seed=88)
    records = []
    for n in (2, 4):
        organization = _org(n, 2)
        result = run_nk_production_sequence(
            organization, trajectory.problems, max_candidates=1000,
            policy=P0ProductionOnlyPolicyNK(),
        )
        records.append(tuple((row.production.problem_id, row.production.requirements)
                             for row in result.records))
    assert records[0] == records[1]


@pytest.mark.parametrize("policy_kind", ("P0", "P1", "P2"))
@pytest.mark.parametrize("information_mode", ("perfect", "imperfect"))
@pytest.mark.parametrize("mis_enabled", (False, True))
@pytest.mark.parametrize("teaching_enabled", (False, True))
def test_runner_accepts_frozen_generated_demand_across_valid_mechanism_combinations(
    policy_kind, information_mode, mis_enabled, teaching_enabled
):
    org = _org(2, 2)
    regime = _regime("stationary", (_problem("a", (0.8, 0.2)), _problem("b", (0.2, 0.8))), (0.6, 0.4))
    environment = ExogenousEnvironmentConfigNK(StationaryTaskDemand({"r": 1.0}), {"r": regime}, 3, 2.0)
    relations = (("a0", "a1", "s0"), ("a1", "a0", "s1"))
    policies = {
        "P0": P0ProductionOnlyPolicyNK(),
        "P1": P1FixedTeachingNK(relations[0]),
        "P2": P2AdaptiveTeachingNK(relations),
    }
    efficacy_values = tuple(tuple((0.0, 0.0) if i == j else (0.5, 0.4) for j in range(2)) for i in range(2))
    efficacy = TeachingEfficacyNK(org.agent_ids, org.skill_ids, efficacy_values)
    kwargs = dict(
        max_candidates=1000, policy=policies[policy_kind],
        individual_learning=mis_enabled, learning_profile=LearningProfileNK(((0.2, 0.2),) * 2) if mis_enabled else None,
        teaching_enabled=teaching_enabled, teaching_efficacy=efficacy if teaching_enabled else None,
        information_mode=information_mode, information_seed=123,
        policy_parameters=TeachingPolicyParametersNK(effort=0.25),
    )
    first = run_nk_production_sequence(org, environment=environment, environment_seed=72, **kwargs)
    second = run_nk_production_sequence(org, environment=environment, environment_seed=72, **kwargs)
    assert isinstance(first, NKEnvironmentRunResult)
    assert first.trajectory == second.trajectory
    assert first.execution == second.execution
    assert tuple(row.production.problem_id for row in first.execution.records) == tuple(
        problem.problem_id for problem in first.trajectory.problems
    )
    assert len(first.execution.records) == 3


def test_runner_rejects_ambiguous_problem_source_and_missing_environment_seed():
    org = _org(1, 1)
    config = ExogenousEnvironmentConfigNK(StationaryTaskDemand({"r": 1.0}),
                                          {"r": _regime("r", (_problem("p", (0.2,)),))}, 1)
    with pytest.raises(ValueError, match="either problems or environment"):
        run_nk_production_sequence(org, (_problem("p", (0.2,)),), max_candidates=10,
                                   environment=config, environment_seed=1)
    with pytest.raises(ValueError, match="environment_seed is required"):
        run_nk_production_sequence(org, max_candidates=10, environment=config)
