"""Operator restrictions only: no sequence runner or campaign execution."""

import hashlib
import inspect
import json
from pathlib import Path
from unittest.mock import patch

import pytest

import hls.finite_problem_belief as policy
from hls.discover_develop_v2 import mis_v2_transition
from hls.discover_v0 import DEFAULT_SIGMA, EXACT_TOL, JOINT_ACTIONS, gaussian_quadrature_nodes
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE


STATES = (
    ((.1, .6), (.5, .5), (.9, .2)),
    ((.2, .2), (.2, .2), (.2, .2)),
)
BELIEFS = ((.2, .5, .3), (1 / 3,) * 3)
MODES = tuple(policy.ProspectivePolicyMode)
ETA = .35


def audited_current_values(state, belief, hypotheses, remaining, develop=True):
    """Literal pre-refactor calculation from 7f0df6f, returning its local values.

    Kept independent of prospective_action_values for regression; the reference
    has the same arithmetic order as the audited function, including mixture loops.
    """
    model, current_belief = policy.canonical_model(hypotheses, belief)
    values = {}
    for action in JOINT_ACTIONS:
        predicted = policy.hypothesis_means(state, action, model)
        immediate = policy.expected_reward(current_belief, predicted)
        if remaining == 1:
            values[action] = immediate
            continue
        next_state = mis_v2_transition(state, action, enabled=develop, eta=ETA)
        future = 0.0
        for probability, mean in zip(current_belief, predicted):
            if probability == 0.0:
                continue
            for observation, weight in gaussian_quadrature_nodes(mean, DEFAULT_SIGMA, 3):
                posterior = policy.finite_bayes_update(current_belief, observation, predicted, DEFAULT_SIGMA)
                future += probability * weight * policy._best_immediate(next_state, posterior, model)[1]
        values[action] = immediate + future
    return values


def select(values):
    maximum = max(values.values())
    return next(action for action in JOINT_ACTIONS if abs(values[action] - maximum) <= EXACT_TOL), maximum


def values_for(state, belief, mode, remaining=2):
    information, development = mode.value
    return policy.prospective_action_values(
        state, belief, HYPOTHESIS_REPERTOIRE, remaining=remaining, eta=ETA,
        anticipate_information=information, anticipate_development=development,
    )


@pytest.mark.parametrize("state,belief", zip(STATES, BELIEFS))
@pytest.mark.parametrize("remaining", (1, 2, 3))
def test_q11_all_candidate_values_and_action_exactly_reproduce_current(state, belief, remaining):
    reference = audited_current_values(state, belief, HYPOTHESIS_REPERTOIRE, remaining)
    actual = values_for(state, belief, policy.ProspectivePolicyMode.INFORMATION_AND_DEVELOPMENT, remaining)
    assert actual == reference
    selected = policy.choose_prospective_action(
        state, belief, HYPOTHESIS_REPERTOIRE, remaining=remaining,
        policy_mode=policy.ProspectivePolicyMode.INFORMATION_AND_DEVELOPMENT, eta=ETA,
    )
    assert selected == select(reference)
    assert policy.finite_choose_dynamic_action_v2(
        state, belief, HYPOTHESIS_REPERTOIRE, remaining=remaining, develop=True, eta=ETA,
    ) == selected


@pytest.mark.parametrize("state,belief", zip(STATES, BELIEFS))
def test_q00_keeps_constant_continuation_and_myopic_policy_including_ties(state, belief):
    immediate = values_for(state, belief, MODES[0], remaining=1)
    continuation = max(immediate.values())
    q00 = values_for(state, belief, policy.ProspectivePolicyMode.NONE)
    assert q00 == {action: value + continuation for action, value in immediate.items()}
    assert select(q00)[0] == select(immediate)[0]
    if state == STATES[1]:
        assert sum(abs(v - continuation) <= EXACT_TOL for v in immediate.values()) > 1


def test_terminal_all_modes_equal_without_any_prospective_transition():
    with patch.object(policy, "mis_v2_transition", side_effect=AssertionError), patch.object(
        policy, "finite_bayes_update", side_effect=AssertionError
    ), patch.object(policy, "gaussian_quadrature_nodes", side_effect=AssertionError):
        results = [values_for(STATES[0], BELIEFS[0], mode, remaining=1) for mode in MODES]
    assert all(result == results[0] for result in results)


def test_q10_freezes_state_and_reoptimizes_on_alternative_posteriors():
    state, belief = STATES[0], BELIEFS[0]
    recorded = []
    original = policy._best_immediate

    def leaf(next_state, posterior, model):
        action, value = original(next_state, posterior, model)
        recorded.append((next_state, posterior, action))
        return action, value

    with patch.object(policy, "_best_immediate", side_effect=leaf):
        actual = values_for(state, belief, policy.ProspectivePolicyMode.INFORMATION_ONLY)
    assert actual == audited_current_values(state, belief, HYPOTHESIS_REPERTOIRE, 2, develop=False)
    assert all(next_state is state for next_state, _, _ in recorded)
    assert len({posterior for _, posterior, _ in recorded}) > 1
    assert len({action for _, _, action in recorded}) > 1


def test_q01_freezes_belief_but_evolves_state_and_terminal_options():
    state, belief = STATES[0], BELIEFS[0]
    recorded = []
    original = policy._best_immediate

    def leaf(next_state, posterior, model):
        result = original(next_state, posterior, model)
        recorded.append((next_state, posterior, result))
        return result

    with patch.object(policy, "_best_immediate", side_effect=leaf), patch.object(
        policy, "finite_bayes_update", side_effect=AssertionError
    ), patch.object(policy, "gaussian_quadrature_nodes", side_effect=AssertionError):
        actual = values_for(state, belief, policy.ProspectivePolicyMode.DEVELOPMENT_ONLY)
    assert all(posterior == belief for _, posterior, _ in recorded)
    assert any(next_state != state for next_state, _, _ in recorded)
    assert len({result for _, _, result in recorded}) > 1
    for action in JOINT_ACTIONS:
        immediate = policy.expected_reward(belief, policy.hypothesis_means(state, action, HYPOTHESIS_REPERTOIRE))
        next_state = mis_v2_transition(state, action, enabled=True, eta=ETA)
        leaf_value = original(next_state, belief, HYPOTHESIS_REPERTOIRE)[1]
        assert actual[action] == immediate + leaf_value
        integrated = sum(
            probability * weight * leaf_value
            for probability, mean in zip(belief, policy.hypothesis_means(state, action, HYPOTHESIS_REPERTOIRE))
            for _, weight in gaussian_quadrature_nodes(mean, DEFAULT_SIGMA, 3)
        )
        assert integrated == pytest.approx(leaf_value, abs=1e-14)


def test_real_transitions_have_no_policy_switch_and_inputs_are_unmodified():
    state, belief, action, observation = STATES[0], BELIEFS[0], JOINT_ACTIONS[39], .73
    predicted = policy.hypothesis_means(state, action, HYPOTHESIS_REPERTOIRE)
    expected = (
        policy.finite_bayes_update(belief, observation, predicted),
        mis_v2_transition(state, action, enabled=True, eta=ETA),
    )
    for mode in MODES:
        values_for(state, belief, mode)
        assert (
            policy.finite_bayes_update(belief, observation, predicted),
            mis_v2_transition(state, action, enabled=True, eta=ETA),
        ) == expected
    assert "policy_mode" not in inspect.signature(policy.finite_bayes_update).parameters
    assert "policy_mode" not in inspect.signature(mis_v2_transition).parameters


@pytest.mark.parametrize("mode", MODES)
def test_common_selection_preserves_action_order_and_tolerance(mode):
    values = {action: 0.0 for action in JOINT_ACTIONS}
    values[JOINT_ACTIONS[0]] = 1.0 - EXACT_TOL / 2
    values[JOINT_ACTIONS[-1]] = 1.0
    with patch.object(policy, "prospective_action_values", return_value=values):
        assert policy.choose_prospective_action(
            STATES[0], BELIEFS[0], HYPOTHESIS_REPERTOIRE, remaining=2, policy_mode=mode, eta=ETA
        ) == (JOINT_ACTIONS[0], 1.0)


def test_freeze_manifest_hashes_and_no_experiment_status():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "results/foundations/policy_ablation/pre_experiment_policy_ablation.json").read_text())
    assert manifest["source_audit_commit"] == "7f0df6f"
    assert manifest["new_team_simulations"] == 0
    assert manifest["strategy_discrimination_gate_run"] is False
    assert manifest["campaign2_run"] is False
    assert set(manifest["modes"]) == {mode.name for mode in MODES}
    for source in manifest["source_artifacts"]:
        assert hashlib.sha256((root / source["path"]).read_bytes()).hexdigest() == source["sha256"]
