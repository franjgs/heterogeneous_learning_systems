"""Controls for finite internal problem beliefs and continuous world truth."""

from math import isclose

import pytest

from hls.discover_develop_v0 import DEVELOP_KNOWN, DISCOVER_DEVELOP, DISCOVER_ONLY, STATIC_KNOWN
from hls.discover_develop_v2 import mis_v2_transition, run_sequence_v2
from hls.discover_v0 import (
    DEFAULT_SIGMA,
    JOINT_ACTIONS,
    THETA_1,
    THETA_2,
    bayes_update,
    ces_reward,
    means,
    production_inputs,
    unknown_policy_value,
)
from hls.finite_problem_belief import (
    canonical_model,
    expected_reward,
    finite_bayes_update,
    finite_choose_dynamic_action_v2,
    finite_unknown_policy_value,
    hypothesis_means,
    run_finite_problem_sequence,
    uniform_prior,
    validate_belief,
    validate_problem,
)


STATE = ((0.0, 0.5), (0.5, 1.0), (1.0, 0.0))
GENERALIST = ((0.5, 0.5),) * 3
BINARY_MODEL = (THETA_1, THETA_2)
TERNARY_MODEL = (THETA_1, (0.5, 0.5), THETA_2)
G00 = GENERALIST
G06 = ((0.0, 0.0), (0.5, 0.5), (1.0, 1.0))


def _assert_binary_trajectory_equal(old, new):
    assert len(old) == len(new)
    for binary, finite in zip(old, new):
        assert binary.action == finite.action
        assert binary.state_before == finite.state_before
        assert binary.state_after == finite.state_after
        assert binary.belief_before == pytest.approx(finite.belief_before[0], abs=2e-15)
        assert binary.belief_after == pytest.approx(finite.belief_after[0], abs=2e-15)
        assert binary.expected_reward_true == finite.true_mean
        assert binary.observed_reward == finite.observed_reward
        assert binary.cumulative_expected_reward == finite.cumulative_reward


def test_problem_belief_and_hypothesis_validation_has_no_hidden_normalization():
    assert validate_problem((0.63, 0.37)) == (0.63, 0.37)
    assert validate_belief((0.2, 0.3, 0.5), 3) == (0.2, 0.3, 0.5)
    assert uniform_prior(3) == (1 / 3,) * 3
    for invalid in ((0.6, 0.5), (-0.1, 1.1), (float("nan"), 0.0)):
        with pytest.raises(ValueError):
            validate_problem(invalid)
    for invalid in ((0.2, 0.2), (-0.1, 1.1), (float("inf"), 0.0)):
        with pytest.raises(ValueError):
            validate_belief(invalid, 2)
    with pytest.raises(ValueError):
        canonical_model((THETA_1, THETA_1))


def test_generalized_bayes_normalizes_and_m1_is_degenerate():
    posterior = finite_bayes_update((0.2, 0.3, 0.5), 0.7, (0.3, 0.6, 0.9))
    assert all(0.0 <= probability <= 1.0 for probability in posterior)
    assert sum(posterior) == pytest.approx(1.0, abs=1e-15)
    assert finite_bayes_update((1.0,), 99.0, (0.4,)) == (1.0,)
    value = finite_unknown_policy_value(STATE, ((0.63, 0.37),), horizon=2)
    assert value.first_actions


def test_m2_bayes_and_expected_reward_reproduce_scalar_binary_equations():
    action = JOINT_ACTIONS[37]
    mu_1, mu_2 = means(STATE, action)
    belief, observation = 0.37, 0.61
    posterior = finite_bayes_update((belief, 1.0 - belief), observation, (mu_1, mu_2))
    scalar = bayes_update(belief, observation, mu_1, mu_2, DEFAULT_SIGMA)
    assert posterior == pytest.approx((scalar, 1.0 - scalar), abs=2e-15)
    assert expected_reward((belief, 1.0 - belief), (mu_1, mu_2)) == belief * mu_1 + (1.0 - belief) * mu_2


def test_m2_policy_value_and_first_actions_exactly_regress_binary_dp():
    old = unknown_policy_value(STATE, horizon=2, prior=0.5)
    new = finite_unknown_policy_value(STATE, BINARY_MODEL, horizon=2, prior=(0.5, 0.5))
    assert new.value == old.value
    assert new.first_actions == old.first_actions
    assert tuple(action for action, _ in new.first_action_values) == tuple(action for action, _ in old.first_action_values)
    assert max(
        abs(new_value - old_value)
        for (_, new_value), (_, old_value) in zip(new.first_action_values, old.first_action_values)
    ) < 1e-14


def test_m3_exact_dp_has_valid_value_and_action_with_continuation():
    result = finite_unknown_policy_value(STATE, TERNARY_MODEL, horizon=2)
    assert result.value > 0.0
    assert result.first_actions and all(action in JOINT_ACTIONS for action in result.first_actions)


@pytest.mark.parametrize("mode", (DISCOVER_ONLY, DISCOVER_DEVELOP))
def test_m2_unknown_trajectory_regression(mode):
    old = run_sequence_v2(GENERALIST, (THETA_1,), mode=mode, eta=0.7, horizon=3, seed=17)
    new = run_finite_problem_sequence(
        GENERALIST, (THETA_1,), BINARY_MODEL, mode=mode, eta=0.7, horizon=3, seed=17
    )
    _assert_binary_trajectory_equal(old, new)


def test_m3_represented_problem_updates_valid_posterior_and_uses_all_hypotheses():
    action = JOINT_ACTIONS[39]
    predicted = hypothesis_means(STATE, action, TERNARY_MODEL)
    posterior = finite_bayes_update(uniform_prior(3), predicted[1], predicted)
    assert sum(posterior) == pytest.approx(1.0, abs=1e-15)
    assert posterior[1] > 1 / 3
    manual = sum(probability * mean for probability, mean in zip((0.2, 0.5, 0.3), predicted))
    assert expected_reward((0.2, 0.5, 0.3), predicted) == manual
    action_three, value_three = finite_choose_dynamic_action_v2(
        STATE, (0.2, 0.5, 0.3), TERNARY_MODEL, remaining=2, develop=True, eta=0.35
    )
    action_two, value_two = finite_choose_dynamic_action_v2(
        STATE, (0.4, 0.6), (THETA_1, THETA_2), remaining=2, develop=True, eta=0.35
    )
    assert action_three in JOINT_ACTIONS and value_three != value_two


def test_hypothesis_permutation_with_prior_permutation_is_physically_invariant():
    first_model, first_prior = canonical_model(TERNARY_MODEL, (0.2, 0.5, 0.3))
    second_model, second_prior = canonical_model((THETA_2, THETA_1, (0.5, 0.5)), (0.3, 0.2, 0.5))
    assert (first_model, first_prior) == (second_model, second_prior)
    first = finite_unknown_policy_value(STATE, TERNARY_MODEL, prior=(0.2, 0.5, 0.3), horizon=1)
    second = finite_unknown_policy_value(
        STATE, (THETA_2, THETA_1, (0.5, 0.5)), prior=(0.3, 0.2, 0.5), horizon=1
    )
    assert first == second


def test_unrepresented_true_problem_remains_world_truth_not_a_dispatched_hypothesis():
    truth = (0.63, 0.37)
    rows = run_finite_problem_sequence(
        STATE, (truth,), TERNARY_MODEL, mode=DISCOVER_DEVELOP, eta=0.35, horizon=2, seed=23
    )
    first = rows[0]
    exact_true_mean = ces_reward(production_inputs(STATE, first.action), truth)
    represented = hypothesis_means(STATE, first.action, TERNARY_MODEL)
    assert first.true_problem == truth
    assert first.true_mean == exact_true_mean
    assert exact_true_mean not in represented
    assert len(first.belief_before) == len(first.belief_after) == 3
    assert sum(first.belief_after) == pytest.approx(1.0, abs=1e-15)


def test_known_oracle_uses_true_problem_outside_hypothesis_set_directly():
    truth = (0.63, 0.37)
    rows = run_finite_problem_sequence(
        STATE, (truth,), TERNARY_MODEL, mode=STATIC_KNOWN, eta=0.35, horizon=1, seed=11
    )
    row = rows[0]
    rewards = {action: ces_reward(production_inputs(STATE, action), truth) for action in JOINT_ACTIONS}
    assert row.belief_before is row.belief_after is None
    assert row.true_mean == max(rewards.values())
    assert row.action == next(action for action in JOINT_ACTIONS if abs(rewards[action] - row.true_mean) <= 1e-10)


def test_unknown_policy_has_no_true_problem_leakage_and_belief_resets_between_problems():
    left = run_finite_problem_sequence(
        STATE, ((0.63, 0.37),), TERNARY_MODEL, mode=DISCOVER_DEVELOP, eta=0.35, horizon=1, seed=7
    )
    right = run_finite_problem_sequence(
        STATE, ((0.31, 0.69),), TERNARY_MODEL, mode=DISCOVER_DEVELOP, eta=0.35, horizon=1, seed=7
    )
    assert left[0].action == right[0].action
    assert left[0].belief_before == right[0].belief_before == uniform_prior(3)
    repeated = run_finite_problem_sequence(
        STATE, ((0.63, 0.37), (0.63, 0.37)), TERNARY_MODEL,
        mode=DISCOVER_DEVELOP, eta=0.35, horizon=1, seed=7
    )
    assert repeated[1].belief_before == uniform_prior(3)


def test_finite_problem_execution_is_deterministic_for_fixed_seed():
    arguments = (STATE, ((0.63, 0.37),), TERNARY_MODEL)
    first = run_finite_problem_sequence(
        *arguments, mode=DISCOVER_DEVELOP, eta=0.35, horizon=2, seed=101
    )
    second = run_finite_problem_sequence(
        *arguments, mode=DISCOVER_DEVELOP, eta=0.35, horizon=2, seed=101
    )
    assert first == second


def test_mis_v2_transition_is_the_unchanged_transition_used_by_finite_runner():
    row = run_finite_problem_sequence(
        STATE, (THETA_1,), BINARY_MODEL, mode=DISCOVER_DEVELOP, eta=0.35, horizon=1, seed=5
    )[0]
    assert row.state_after == mis_v2_transition(STATE, row.action, enabled=True, eta=0.35)


def test_g00_g06_eta_070_diagnostic_regresses_binary_actions_states_and_rewards():
    sequence = (THETA_1, THETA_2, THETA_1, THETA_2)
    for configuration in (G00, G06):
        old = run_sequence_v2(
            configuration, sequence, mode=DISCOVER_DEVELOP, eta=0.70, seed=20261007
        )
        new = run_finite_problem_sequence(
            configuration, sequence, BINARY_MODEL,
            mode=DISCOVER_DEVELOP, eta=0.70, seed=20261007
        )
        _assert_binary_trajectory_equal(old, new)


@pytest.mark.parametrize("mode", (STATIC_KNOWN, DEVELOP_KNOWN))
def test_known_modes_accept_truth_outside_internal_model(mode):
    rows = run_finite_problem_sequence(
        GENERALIST, ((0.63, 0.37),), TERNARY_MODEL, mode=mode, eta=0.35, horizon=2, seed=29
    )
    assert all(row.belief_before is None and row.true_problem == (0.63, 0.37) for row in rows)


@pytest.mark.parametrize("mode", (STATIC_KNOWN, DEVELOP_KNOWN))
def test_known_modes_regress_binary_world_without_using_finite_belief(mode):
    old = run_sequence_v2(STATE, (THETA_1, THETA_2), mode=mode, eta=0.35, seed=9)
    new = run_finite_problem_sequence(
        STATE, (THETA_1, THETA_2), BINARY_MODEL, mode=mode, eta=0.35, seed=9
    )
    assert [row.action for row in old] == [row.action for row in new]
    assert [row.state_after for row in old] == [row.state_after for row in new]
    assert old[-1].cumulative_expected_reward == new[-1].cumulative_reward
    assert all(row.belief_before is None and row.belief_after is None for row in new)
