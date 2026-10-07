"""Invariants for the constant-column-sum capability geometry gate."""

from experiments.synthetic.capability_geometry_gate.run import (
    BUDGET_BY_CAPABILITY,
    CONFIGURATIONS,
    ENVIRONMENTS,
    SEED,
    SEEDS,
    column_sums,
    geometry_descriptors,
)
from hls.discover_develop_v0 import DISCOVER_DEVELOP, MIS_LEARNING_SCALE, choose_dynamic_action, run_sequence
from hls.discover_v0 import (
    DEFAULT_HORIZON,
    DEFAULT_PRIOR,
    DEFAULT_SIGMA,
    INDIVIDUAL_ACTIONS,
    JOINT_ACTIONS,
    N_AGENTS,
    N_CAPABILITIES,
    RHO,
    THETA_1,
    THETA_2,
    capability_dual,
    evaluate_state,
    means,
)


def test_every_design_conserves_exact_capability_budgets_and_bounds():
    assert {column_sums(config["state"]) for config in CONFIGURATIONS} == {BUDGET_BY_CAPABILITY}
    assert all(0.0 <= value <= 1.0 for config in CONFIGURATIONS for row in config["state"] for value in row)
    assert len(JOINT_ACTIONS) == 64


def test_campaign_uses_the_frozen_prototype_physics_and_resources():
    assert (N_AGENTS, N_CAPABILITIES, RHO) == (3, 2, 0.5)
    assert (DEFAULT_PRIOR, DEFAULT_SIGMA, DEFAULT_HORIZON) == (0.5, 0.1, 3)
    assert (THETA_1, THETA_2, MIS_LEARNING_SCALE) == ((0.8, 0.2), (0.2, 0.8), 1.5)
    assert INDIVIDUAL_ACTIONS == ((0.0, 0.0), (0.0, 1.0), (0.5, 0.5), (1.0, 0.0))
    assert all(len(config["state"]) == N_AGENTS and all(len(row) == N_CAPABILITIES for row in config["state"]) for config in CONFIGURATIONS)


def test_descriptors_and_known_value_are_agent_permutation_invariant():
    state = CONFIGURATIONS[-1]["state"]
    permuted = (state[2], state[0], state[1])
    assert geometry_descriptors(state) == geometry_descriptors(permuted)
    assert evaluate_state(state).known_value == evaluate_state(permuted).known_value
    assert abs(choose_dynamic_action(state, 0.5, remaining=3, develop=True)[1] - choose_dynamic_action(permuted, 0.5, remaining=3, develop=True)[1]) < 1e-12


def test_capability_duality_preserves_symmetric_physics_and_control_value():
    state = CONFIGURATIONS[2]["state"]
    dual = capability_dual(state)
    assert evaluate_state(state).known_value == evaluate_state(dual).known_value
    action = JOINT_ACTIONS[19]
    dual_action = tuple((right, left) for left, right in action)
    mu_1, mu_2 = means(state, action)
    dual_mu_1, dual_mu_2 = means(dual, dual_action)
    assert (mu_1, mu_2) == (dual_mu_2, dual_mu_1)
    assert abs(choose_dynamic_action(state, 0.3, remaining=3, develop=True)[1] - choose_dynamic_action(dual, 0.7, remaining=3, develop=True)[1]) < 1e-12


def test_execution_is_deterministic_and_environments_are_shared():
    state = CONFIGURATIONS[0]["state"]
    sequence = ENVIRONMENTS["change_1122"]
    assert run_sequence(state, sequence, mode=DISCOVER_DEVELOP, seed=SEED) == run_sequence(state, sequence, mode=DISCOVER_DEVELOP, seed=SEED)
    assert all(len(sequence) == 4 for sequence in ENVIRONMENTS.values())
    assert SEEDS == (20261007, 20261008, 20261009)


def test_discover_policy_cannot_use_true_theta_before_observing():
    state = CONFIGURATIONS[3]["state"]
    theta_1 = run_sequence(state, (THETA_1,), mode=DISCOVER_DEVELOP, seed=SEED)
    theta_2 = run_sequence(state, (THETA_2,), mode=DISCOVER_DEVELOP, seed=SEED)
    assert theta_1[0].belief_before == theta_2[0].belief_before == 0.5
    assert theta_1[0].action == theta_2[0].action


def test_frozen_prototype_reference_case_is_reproduced():
    state = CONFIGURATIONS[6]["state"]  # concentrated alpha=.5 == canonical S001
    rows = run_sequence(state, (THETA_1, THETA_1, THETA_2), mode=DISCOVER_DEVELOP, seed=20261006)
    assert abs(rows[-1].cumulative_expected_reward - 13.914785604406937) < 1e-12
