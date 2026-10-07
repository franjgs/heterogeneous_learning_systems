"""Focused invariants for the frozen DISCOVER x DEVELOP campaign."""

from experiments.synthetic.discover_develop_campaign.run import CONFIG, ENV, desc
from hls.discover_develop_v0 import DISCOVER_DEVELOP, MIS_LEARNING_SCALE, run_sequence
from hls.discover_v0 import JOINT_ACTIONS, THETA_1, THETA_2


def test_campaign_configurations_share_the_existing_capacity_budget():
    assert {desc(state)["budget"] for state in CONFIG.values()} == {3.0}
    assert len(JOINT_ACTIONS) == 64


def test_geometric_descriptors_are_agent_permutation_invariant():
    state = CONFIG["S001"]
    permuted = (state[2], state[0], state[1])
    left, right = desc(state), desc(permuted)
    for key in ("budget", "concentration", "agent_heterogeneity", "coverage_capability1", "coverage_capability2", "balance", "redundancy", "V_K_initial"):
        assert left[key] == right[key]


def test_campaign_reproduces_prototype_deterministically_with_shared_environment():
    sequence = ENV["change"]
    first = run_sequence(CONFIG["S001"], sequence, mode=DISCOVER_DEVELOP, seed=20261006)
    second = run_sequence(CONFIG["S001"], sequence, mode=DISCOVER_DEVELOP, seed=20261006)
    assert first == second
    assert tuple(step.true_theta for step in first[::3]) == ("theta1", "theta1", "theta2")
    assert MIS_LEARNING_SCALE == 1.5


def test_discover_first_decision_is_identical_before_theta_specific_evidence():
    left = run_sequence(CONFIG["S002"], (THETA_1,), mode=DISCOVER_DEVELOP, seed=12)
    right = run_sequence(CONFIG["S002"], (THETA_2,), mode=DISCOVER_DEVELOP, seed=12)
    assert left[0].belief_before == right[0].belief_before == 0.5
    assert left[0].action == right[0].action
