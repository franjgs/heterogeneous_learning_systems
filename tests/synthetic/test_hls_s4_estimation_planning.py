from dataclasses import replace

from hls.hls_lab_nk_estimation import CompetenceObservationParametersNK
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from hls.synthetic.hls_s4 import investment_family
from hls.synthetic.hls_s4_estimation_planning import run_s4_estimation_planning


PARAMETERS = CompetenceObservationParametersNK(
    production_observation_noise_sd=0.02,
    competence_grid_points=101,
    competence_prior_variance=0.04,
)


def test_hidden_real_competence_does_not_affect_first_decision():
    case = investment_family()[0]
    altered = replace(case, initial=((0.8, 0.1), (0.2, 0.7)))
    first = run_s4_estimation_planning(
        case, policy="bellman", estimation="updated", seed=4,
        observation_parameters=PARAMETERS,
    )
    second = run_s4_estimation_planning(
        altered, policy="bellman", estimation="updated", seed=4,
        observation_parameters=PARAMETERS,
    )
    assert first.periods[0].assignment == second.periods[0].assignment


def test_frozen_estimator_predicts_mis_without_assimilating_observations():
    case = investment_family()[0]
    run = run_s4_estimation_planning(
        case, policy="reactive", estimation="frozen", seed=5,
        observation_parameters=PARAMETERS,
    )
    row = run.periods[0]
    assert all(abs(value - 0.5) < 1e-12
               for values in row.estimate_before for value in values)
    # Only the assigned cell changes in the prediction-only posterior.
    for i in range(2):
        for k in range(2):
            if (i, k) in row.assignment:
                assert row.estimate_after[i][k] > row.estimate_before[i][k]
            else:
                assert row.estimate_after[i][k] == row.estimate_before[i][k]


def test_updated_estimator_assimilates_only_executed_pair_outcomes():
    case = investment_family()[0]
    frozen = run_s4_estimation_planning(
        case, policy="reactive", estimation="frozen", seed=6,
        observation_parameters=PARAMETERS,
    )
    updated = run_s4_estimation_planning(
        case, policy="reactive", estimation="updated", seed=6,
        observation_parameters=PARAMETERS,
    )
    assert frozen.periods[0].assignment == updated.periods[0].assignment
    selected = set(updated.periods[0].assignment)
    for i in range(2):
        for k in range(2):
            if (i, k) not in selected:
                assert updated.periods[0].estimate_after[i][k] == frozen.periods[0].estimate_after[i][k]
    assert updated.periods[0].estimate_after != frozen.periods[0].estimate_after


def test_actual_transition_reward_and_run_are_reproducible():
    case = investment_family()[1]
    first = run_s4_estimation_planning(
        case, policy="reactive", estimation="updated", seed=8,
        observation_parameters=PARAMETERS,
    )
    second = run_s4_estimation_planning(
        case, policy="reactive", estimation="updated", seed=8,
        observation_parameters=PARAMETERS,
    )
    assert first.reward == second.reward
    assert [p.assignment for p in first.periods] == [p.assignment for p in second.periods]
    assert [p.competence_after for p in first.periods] == [p.competence_after for p in second.periods]
    assert abs(first.reward - sum(p.reward for p in first.periods)) < 1e-12
    first_period = first.periods[0]
    allocation = [[0.0, 0.0], [0.0, 0.0]]
    for agent, task in first_period.assignment:
        allocation[agent][task] = 1.0
    expected = mis_v2_transition_nk(
        first_period.competence_before,
        tuple(tuple(row) for row in allocation),
        LearningProfileNK(case.eta),
    )
    assert first_period.competence_after == expected


def test_bellman_and_reactive_use_same_estimate_at_decision_time():
    case = investment_family()[0]
    reactive = run_s4_estimation_planning(
        case, policy="reactive", estimation="frozen", seed=10,
        observation_parameters=PARAMETERS,
    )
    bellman = run_s4_estimation_planning(
        case, policy="bellman", estimation="frozen", seed=10,
        observation_parameters=PARAMETERS,
    )
    assert reactive.periods[0].estimate_before == bellman.periods[0].estimate_before
    assert reactive.periods[0].competence_before == bellman.periods[0].competence_before
    assert len(reactive.periods[0].assignment) <= 1
    assert len(bellman.periods[0].assignment) <= 1
