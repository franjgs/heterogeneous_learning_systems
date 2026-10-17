"""Cross-geometry integrated invariants for the HLS research-readiness review.

These are instrument checks, not policy comparisons or scientific findings.
Expected production, CES, resource and transition values are recomputed here
from the declared equations rather than by calling the production runner twice.
"""

from math import exp

import pytest

from hls.discover_v0 import RHO
from hls.discover_develop_v2 import eta_to_lambda
from hls.hls_lab_nk_environment import (
    DemandRegimeNK,
    ExogenousEnvironmentConfigNK,
    generate_environment_trajectory_nk,
)
from hls.hls_lab_nk_execution import run_nk_production_sequence
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK
from hls.hls_lab_nk_policies import (
    P0ProductionOnlyPolicyNK,
    P1FixedTeachingNK,
    P2AdaptiveTeachingNK,
    TeachingPolicyParametersNK,
)
from hls.hls_lab_nk_estimation import CompetenceObservationParametersNK
from hls.hls_lab_nk_teaching import TeachingEfficacyNK, TeachingParametersNK
from hls.synthetic.c5 import MarkovTaskDemand


def _inputs(n, k):
    agent_ids = tuple(f"a{i}" for i in range(n))
    skill_ids = tuple(f"s{j}" for j in range(k))
    actual = tuple(tuple(0.15 + 0.08 * ((2 * i + j) % 7) for j in range(k))
                   for i in range(n))
    estimated = tuple(tuple(min(1.0, value + 0.04) for value in row) for row in actual)
    organization = OrganizationConfigNK(
        agent_ids, skill_ids, actual, (1.0,) * n, 2.0, estimated,
    )
    problem_a = ProblemSpecNK("regime-a", (0.16,) + (0.10,) * (k - 1), 1.75)
    problem_b = ProblemSpecNK("regime-b", (0.10,) * (k - 1) + (0.16,), 1.75)
    environment = ExogenousEnvironmentConfigNK(
        MarkovTaskDemand(
            {"a": 1.0, "b": 0.0},
            {"a": {"a": 0.0, "b": 1.0}, "b": {"a": 0.0, "b": 1.0}},
        ),
        {"a": DemandRegimeNK("regime-a", (problem_a,), (1.0,)),
         "b": DemandRegimeNK("regime-b", (problem_b,), (1.0,))},
        horizon=3,
        resource_budget=1.75,
    )
    if k == 2:
        choices = None  # historical DISCOVER catalog
    else:
        zero = (0.0,) * k
        one_skill = tuple(tuple(0.5 if j == skill else 0.0 for j in range(k))
                          for skill in range(k))
        choices = tuple((zero, *one_skill) for _ in range(n))
    efficacy = TeachingEfficacyNK(
        agent_ids,
        skill_ids,
        tuple(tuple(tuple(0.0 if i == j else 0.65 for _ in range(k))
                    for j in range(n)) for i in range(n)),
    )
    learning = LearningProfileNK(tuple(tuple(0.18 for _ in range(k)) for _ in range(n)))
    return organization, environment, choices, efficacy, learning


def _policies(organization):
    if len(organization.agent_ids) == 1:
        return (P0ProductionOnlyPolicyNK(),)
    a0, a1 = organization.agent_ids[:2]
    s0 = organization.skill_ids[0]
    s1 = organization.skill_ids[-1]
    return (
        P0ProductionOnlyPolicyNK(),
        P1FixedTeachingNK((a0, a1, s0)),
        P2AdaptiveTeachingNK(((a0, a1, s0), (a1, a0, s1))),
    )


def _assert_run_equations(run, organization, trajectory, efficacy, learning,
                          mis_on, teaching_on, information_mode):
    assert tuple(row.production.problem_id for row in run.records) == tuple(
        problem.problem_id for problem in trajectory.problems
    )
    n, k = len(organization.agent_ids), len(organization.skill_ids)
    for record, problem in zip(run.records, trajectory.problems):
        production = record.production
        before = record.competence_actual_before
        action = record.action
        # Independent additive production and weighted CES calculations.
        expected_outputs = tuple(
            sum(action.production[i][skill] * before[i][skill] for i in range(n))
            for skill in range(k)
        )
        assert production.outputs == pytest.approx(expected_outputs)
        assert tuple(sum(production.individual_outputs[i][skill] for i in range(n))
                     for skill in range(k)) == pytest.approx(expected_outputs)
        expected_ces = sum(weight * value**RHO
                           for weight, value in zip(problem.ces_weights, expected_outputs)) ** (1.0 / RHO)
        assert production.ces_reward == pytest.approx(expected_ces)
        active = tuple(j for j, requirement in enumerate(problem.requirements) if requirement > 0)
        assert production.functional_result.success == all(
            expected_outputs[j] + 1e-12 >= problem.requirements[j] for j in active
        )

        productive_by_agent = tuple(sum(row) for row in action.production)
        teaching_load = [0.0] * n
        if action.teaching is not None:
            teacher = organization.agent_ids.index(action.teaching.teacher_id)
            learner_agent = organization.agent_ids.index(action.teaching.learner_id)
            teaching_load[teacher] += action.teaching.effort
            teaching_load[learner_agent] += action.teaching.effort
        assert record.productive_effort_used == pytest.approx(sum(productive_by_agent))
        assert record.teaching_resource_used == pytest.approx(sum(teaching_load))
        assert record.total_resource_used == pytest.approx(
            record.productive_effort_used + record.teaching_resource_used
        )
        assert record.total_resource_used + record.unused_collective_capacity == pytest.approx(
            min(organization.collective_effort_budget, problem.resource_budget)
        )
        individual_used = tuple(
            production.individual_effort_used[i] + teaching_load[i] for i in range(n)
        )
        assert all(individual_used[i] <= organization.effort_limits[i] + 1e-12
                   for i in range(n))

        after_mis = []
        for i in range(n):
            row = []
            for skill in range(k):
                c = before[i][skill]
                effort = action.production[i][skill]
                if mis_on:
                    c = 1.0 - (1.0 - c) * exp(-eta_to_lambda(learning.eta[i][skill]) * effort)
                row.append(c)
            after_mis.append(row)
        assert tuple(value for row in record.competence_after_mis for value in row) == pytest.approx(
            tuple(value for row in after_mis for value in row)
        )

        expected_after = [row[:] for row in after_mis]
        if teaching_on and action.teaching is not None:
            teacher = organization.agent_ids.index(action.teaching.teacher_id)
            learner_agent = organization.agent_ids.index(action.teaching.learner_id)
            skill = organization.skill_ids.index(action.teaching.skill_id)
            t = efficacy.values[teacher][learner_agent][skill]
            expected_after[learner_agent][skill] = after_mis[learner_agent][skill] + (
                TeachingParametersNK().transfer_rate * action.teaching.effort * t
                * (1.0 - after_mis[learner_agent][skill])
            )
            expected_increment = tuple(tuple(
                expected_after[i][j] - after_mis[i][j] for j in range(k)
            ) for i in range(n))
            assert tuple(value for row in record.teaching_increment for value in row) == pytest.approx(
                tuple(value for row in expected_increment for value in row)
            )
        else:
            assert all(value == 0.0 for row in record.teaching_increment for value in row)
        assert tuple(value for row in record.competence_actual_after for value in row) == pytest.approx(
            tuple(value for row in expected_after for value in row)
        )
        assert all(0.0 <= value <= 1.0 for row in record.competence_actual_after for value in row)
        if information_mode == "perfect":
            assert record.competence_estimated_before == record.competence_actual_before
            assert record.competence_estimated_after == record.competence_actual_after
        else:
            assert all(0.0 <= value <= 1.0 for row in record.competence_estimated_after for value in row)


@pytest.mark.parametrize(("n", "k"), ((1, 1), (2, 2), (3, 2), (4, 3)))
def test_integrated_environment_policy_mechanism_matrix_and_independent_trace_checks(n, k):
    organization, environment, choices, efficacy, learning = _inputs(n, k)
    trajectory = generate_environment_trajectory_nk(environment, seed=20261016)
    assert trajectory.latent_states == ("a", "b", "b")
    for policy in _policies(organization):
        for mis_on in (False, True):
            for teaching_on in (False, True):
                for information_mode in ("perfect", "imperfect"):
                    run = run_nk_production_sequence(
                        organization,
                        trajectory.problems,
                        max_candidates=10_000,
                        per_agent_effort_choices=choices,
                        policy=policy,
                        individual_learning=mis_on,
                        learning_profile=learning if mis_on else None,
                        teaching_enabled=teaching_on,
                        teaching_efficacy=efficacy if teaching_on else None,
                        policy_parameters=TeachingPolicyParametersNK(effort=0.25),
                        information_mode=information_mode,
                        observation_parameters=CompetenceObservationParametersNK(
                            production_observation_noise_sd=0.015,
                            outcome_noise_sd=0.01,
                        ),
                        information_seed=719,
                    )
                    _assert_run_equations(
                        run, organization, trajectory, efficacy, learning,
                        mis_on, teaching_on, information_mode,
                    )
