from dataclasses import replace
from itertools import product
import inspect

import pytest

from hls.synthetic.hls_p1 import (
    build_policies,
    default_scenarios,
    demand_paths,
    evaluate_scenario,
    next_competence,
    task_performance,
)


@pytest.fixture(scope="module")
def pilot_scenarios():
    return default_scenarios()


def test_functional_success_is_feasible_and_reward_is_demand_dependent(pilot_scenarios):
    scenario = pilot_scenarios[0]
    actions, _, _ = build_policies(scenario)
    success_action = ((1.0, 0.0), (0.0, 1.0))
    assert success_action in actions
    competence = scenario.initial_competence
    for _ in range(scenario.horizon):
        score_x, success_x, _ = task_performance(scenario, competence, success_action, "x")
        assert success_x
        competence = next_competence(scenario, competence, success_action)
    score_y, success_y, _ = task_performance(
        scenario, scenario.initial_competence, success_action, "y")
    assert not success_y
    assert score_x != score_y

    y_development_path = (
        ((0.0, 1.0), (0.0, 1.0)),
        ((0.0, 1.0), (0.0, 1.0)),
        ((0.0, 1.0), (0.0, 1.0)),
        ((0.5, 0.5), (0.0, 1.0)),
    )
    competence = scenario.initial_competence
    for period, development_action in enumerate(y_development_path):
        score, success, _ = task_performance(scenario, competence,
                                             development_action, "y")
        assert sum(map(sum, development_action)) <= scenario.collective_budget
        if period < 3:
            assert not success
        else:
            assert success and score == pytest.approx(1.0)
        competence = next_competence(scenario, competence, development_action)


def test_all_policy_actions_share_the_same_feasible_catalog(pilot_scenarios):
    for scenario in pilot_scenarios:
        actions, policies, _ = build_policies(scenario)
        assert len(policies) == 3
        for action in actions:
            assert all(sum(row) <= scenario.individual_budget + 1e-12 for row in action)
            assert sum(sum(row) for row in action) <= scenario.collective_budget + 1e-12


def test_fixed_opt_is_exhaustive_over_stationary_task_maps(pilot_scenarios):
    scenario = pilot_scenarios[0]
    actions, policies, solution = build_policies(scenario)
    assert solution["fixed_policy_candidates"] == len(actions) ** 2
    fixed = policies["FIXED_OPT"]
    mapping = fixed.fixed_mapping
    assert mapping is not None
    assert fixed.action_for(0, "x", scenario.initial_competence) == mapping[0]
    assert fixed.action_for(3, "x", ((0.99, 0.99), (0.99, 0.99))) == mapping[0]
    assert fixed.action_for(1, "y", scenario.initial_competence) == mapping[1]
    best = solution["fixed_expected_value"]
    brute_force_values = []
    for candidate in product(range(len(actions)), repeat=2):
        mapping_score = 0.0
        for path, probability in demand_paths(scenario):
            competence = scenario.initial_competence
            total = 0.0
            for task in path:
                action = actions[candidate[scenario.task_index(task)]]
                total += task_performance(scenario, competence, action, task)[0]
                competence = next_competence(scenario, competence, action)
            mapping_score += probability * total
        brute_force_values.append(mapping_score)
    assert best == pytest.approx(max(brute_force_values), abs=1e-11)


def test_reactive_is_current_period_only(pilot_scenarios):
    scenario = pilot_scenarios[0]
    actions, policies, _ = build_policies(scenario)
    reactive = policies["REACTIVE"]
    state = scenario.initial_competence
    action_index = reactive.action_for(0, "x", state)
    score = task_performance(scenario, state, actions[action_index], "x")[0]
    assert score == max(task_performance(scenario, state, action, "x")[0]
                        for action in actions)
    assert action_index == reactive.action_for(3, "x", state)


def test_anticipatory_value_matches_exact_paired_path_evaluation(pilot_scenarios):
    for scenario in pilot_scenarios:
        result = evaluate_scenario(scenario)
        hls = result["policy_summaries"]["HLS_ANTICIPATORY"][
            "expected_cumulative_functional_performance"]
        assert hls == pytest.approx(result["policy_solution"][
            "anticipatory_expected_value"], abs=1e-11)
        assert len(demand_paths(scenario)) == 2 ** scenario.horizon
        assert sum(probability for _, probability in demand_paths(scenario)) == pytest.approx(1.0)
        assert len(result["paired_episodes"]) == 3 * 2 ** scenario.horizon


def test_anticipatory_solver_accounts_for_future_mis_v2_transitions(pilot_scenarios):
    scenario = pilot_scenarios[1]
    before = scenario.initial_competence
    action = ((0.0, 1.0), (0.0, 1.0))
    after = next_competence(scenario, before, action)
    assert after != before
    result = evaluate_scenario(scenario)
    assert result["policy_solution"]["anticipatory_states_explored"] > 0
    assert result["policy_summaries"]["HLS_ANTICIPATORY"][
        "expected_cumulative_functional_performance"] >= 0

    actions, policies, _ = build_policies(scenario)
    seed_action = ((1.0, 0.0), (0.0, 1.0))
    state = next_competence(scenario, before, seed_action)
    hls_index = policies["HLS_ANTICIPATORY"].action_for(1, "x", state)
    reactive_index = policies["REACTIVE"].action_for(1, "x", state)
    assert hls_index != reactive_index
    assert task_performance(scenario, state, actions[hls_index], "x")[0] == pytest.approx(
        task_performance(scenario, state, actions[reactive_index], "x")[0])
    assert actions[hls_index][1][1] > actions[reactive_index][1][1]
    assert next_competence(scenario, state, actions[hls_index])[1][1] > next_competence(
        scenario, state, actions[reactive_index])[1][1]


def test_changing_demand_is_paired_and_uses_same_task_paths(pilot_scenarios):
    scenario = pilot_scenarios[1]
    result = evaluate_scenario(scenario)
    by_path = {}
    for row in result["paired_episodes"]:
        by_path.setdefault(row["demand_path"], set()).add(row["policy_id"])
    assert len(by_path) == 2 ** scenario.horizon
    assert all(policies == {"FIXED_OPT", "REACTIVE", "HLS_ANTICIPATORY"}
               for policies in by_path.values())
    assert all(episode["trace"][0]["competence_before"] == scenario.initial_competence
               for episode in result["paired_episodes"])


def test_policy_interfaces_receive_current_state_not_future_realizations(pilot_scenarios):
    _, policies, _ = build_policies(pilot_scenarios[1])
    for policy in policies.values():
        assert tuple(inspect.signature(policy.action_for).parameters) == (
            "t", "task", "competence")


def test_development_exposure_has_measurable_production_opportunity_cost(pilot_scenarios):
    scenario = pilot_scenarios[0]
    actions, _, _ = build_policies(scenario)
    current_x_focused = ((1.0, 0.0), (0.0, 1.0))
    future_y_investing = ((0.5, 0.5), (0.0, 1.0))
    assert current_x_focused in actions and future_y_investing in actions
    assert sum(map(sum, current_x_focused)) == sum(map(sum, future_y_investing)) == 2.0
    current_score = task_performance(scenario, scenario.initial_competence,
                                    current_x_focused, "x")[0]
    development_score = task_performance(scenario, scenario.initial_competence,
                                         future_y_investing, "x")[0]
    current_next = next_competence(scenario, scenario.initial_competence,
                                   current_x_focused)
    development_next = next_competence(scenario, scenario.initial_competence,
                                       future_y_investing)
    assert development_score < current_score
    assert development_next[0][1] > current_next[0][1]


def test_resource_exposure_is_recorded_once_and_within_budget(pilot_scenarios):
    scenario = pilot_scenarios[0]
    actions, _, _ = build_policies(scenario)
    result = evaluate_scenario(scenario)
    for episode in result["paired_episodes"]:
        assert episode["development_exposure"] == episode["resource_consumption"]
        assert all(row["development_resource_cost"] == 0.0 for row in episode["trace"])
        for row in episode["trace"]:
            assert row["allocation"] in actions
            assert row["resource_used"] <= scenario.collective_budget
            assert all(sum(agent_effort) <= scenario.individual_budget
                       for agent_effort in row["allocation"])


def test_disabled_mis_v2_ablation_preserves_state_and_exact_policy_comparison(pilot_scenarios):
    base = pilot_scenarios[0]
    ablation = replace(
        base,
        scenario_id="stationary_positive_no_learning",
        initial_competence=((0.525, 0.175), (0.525, 0.175)),
        learning_enabled=False,
    )
    assert ablation.eta == base.eta
    assert ablation.action_catalog == base.action_catalog
    assert next_competence(ablation, ablation.initial_competence,
                           ((1.0, 0.0), (0.0, 1.0))) == ablation.initial_competence

    result = evaluate_scenario(ablation)
    assert result["learning_enabled"] is False
    assert result["exact_path_count"] == 2 ** ablation.horizon
    assert result["policy_solution"]["fixed_policy_candidates"] == 36 ** 2
    assert len(result["paired_episodes"]) == 3 * 2 ** ablation.horizon
    expected_value = result["policy_solution"]["anticipatory_expected_value"]
    assert expected_value == pytest.approx(3.211538461538461, abs=1e-12)
    for policy_id in ("FIXED_OPT", "REACTIVE", "HLS_ANTICIPATORY"):
        summary = result["policy_summaries"][policy_id]
        assert summary["expected_cumulative_functional_performance"] == pytest.approx(
            expected_value, abs=1e-12)
        assert summary["expected_success_rate"] == 0.0
        assert summary["expected_resource_consumption"] == pytest.approx(8.0)
    for episode in result["paired_episodes"]:
        assert all(row["competence_after"] == row["competence_before"]
                   for row in episode["trace"])
