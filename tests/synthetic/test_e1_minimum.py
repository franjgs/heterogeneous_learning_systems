from __future__ import annotations

from dataclasses import replace

import pytest

from hls.synthetic.e1_minimum import (
    build_e1_instance,
    four_policies,
    make_replay,
    run_paired,
    run_policy,
)
from hls.synthetic.c3 import BUDGET_KEY
from hls.synthetic.c5 import StationaryTaskDemand
from hls.synthetic.components import BoundedMatrixCompetence
from hls.synthetic.exact import (
    DemandExecutablePolicy,
    _demand_distribution,
    solve_demand_best_static_routing,
    solve_demand_exact_hls,
    solve_demand_exact_strong_sep,
    solve_demand_myopic,
)
from hls.synthetic.interfaces import DevelopmentDecision, NULL_DEVELOPMENT


@pytest.mark.parametrize("demand", ["stationary", "changing"])
def test_all_four_policies_are_executable_on_same_g0_instance(demand):
    instance = build_e1_instance(eta=0.1, demand=demand, horizon=4)
    policies = four_policies(instance)
    replay = make_replay(instance, 17)
    results = run_paired(instance, policies, replay)

    assert set(results) == {"BEST_STATIC", "MYOPIC", "STRONG_SEP", "HLS"}
    assert all(result.task_path == replay.task_path for result in results.values())
    for result in results.values():
        assert len(result.trace.transitions) == 4
        assert result.objective == pytest.approx(
            result.cumulative_reward - result.development_cost
        )
        assert result.trace.transitions[0].state.time == 0
        assert result.trace.transitions[-1].next_state.time == 4
        spent = 1.0 - dict(result.trace.transitions[-1].next_state.resources)[BUDGET_KEY]
        assert 0.0 <= spent <= 1.0
        assert spent == pytest.approx(
            sum(not transition.development_action.is_null for transition in result.trace.transitions)
        )


def test_exact_and_static_solvers_use_expected_demand_not_a_realized_path():
    instance = build_e1_instance(eta=0.75, demand="changing", horizon=4)
    problem = instance.problem
    hls = solve_demand_exact_hls(problem, initial_state=instance.initial_state)
    strong = solve_demand_exact_strong_sep(problem, initial_state=instance.initial_state)
    static = solve_demand_best_static_routing(problem, initial_state=instance.initial_state)
    myopic = solve_demand_myopic(problem, initial_state=instance.initial_state)

    assert len(static.candidates) == 2 ** 2
    assert all(task in dict(static.routing) for task in (1, 2))
    assert static.value <= hls.value + 1e-12
    assert strong.value <= hls.value + 1e-12
    assert myopic.value <= hls.value + 1e-12
    assert hls.value >= static.value

    # A policy depends on the current observed state/task, not on a sampled
    # future path. Different paired tapes leave the policy object unchanged.
    same_model_policy = solve_demand_exact_hls(
        problem, initial_state=instance.initial_state
    ).policy
    assert hls.policy == same_model_policy
    assert not hasattr(hls.policy, "task_path")


@pytest.mark.parametrize("eta", [0.0, 0.1, 0.75])
@pytest.mark.parametrize("demand", ["stationary", "changing"])
def test_all_six_design_cells_build_and_solve(eta, demand):
    """Bounded solver-feasibility check; this is not a campaign run."""
    instance = build_e1_instance(eta=eta, demand=demand, horizon=4)
    policies = four_policies(instance)
    assert len(policies) == 4
    assert all(policy.operational_decisions for policy in policies.values())


def test_exact_recursion_matches_independent_two_period_enumeration():
    instance = build_e1_instance(eta=0.1, demand="stationary", horizon=2)
    problem, initial = instance.problem, instance.initial_state
    environment = problem.environment
    demand = problem.demand_process

    def terminal(state):
        return max(
            environment.reward.operational_reward(state, problem.terminal_task, action)
            for action in problem.operational_actions
        )

    # Independent, uncached depth-first Bellman enumeration for the tiny
    # two-period check. It explicitly enumerates task and opportunity branches.
    def brute(state, task):
        if state.time == problem.horizon:
            return terminal(state)
        action_values = []
        for action in problem.operational_actions:
            reward = environment.reward.operational_reward(state, task, action)
            probability = environment.opportunities.probability(state, task, action, ())
            branch_total = 0.0
            for available, weight in ((False, 1.0 - probability), (True, probability)):
                if weight == 0.0:
                    continue
                from hls.synthetic.interfaces import Opportunity

                opportunity = Opportunity(available)
                development_values = []
                for decision in environment.development.admissible_actions(state, opportunity):
                    if not environment.resources.development_is_admissible(
                        state, decision, opportunity
                    ):
                        continue
                    next_state = replace(
                        environment.development.transition(state, opportunity, decision),
                        resources=environment.resources.consume(state, decision),
                    )
                    if next_state.time == problem.horizon:
                        future = terminal(next_state)
                    else:
                        distribution = _demand_distribution(demand, next_state.time, task)
                        future = sum(
                            probability_next * brute(next_state, next_task)
                            for next_task, probability_next in distribution.items()
                        )
                    development_values.append(
                        -environment.resources.development_cost(decision)
                        + environment.resources.beta * future
                    )
                branch_total += weight * max(development_values)
            action_values.append(reward + branch_total)
        return max(action_values)

    initial_distribution = _demand_distribution(demand, 0, None)
    expected = sum(
        probability * brute(initial, task)
        for task, probability in initial_distribution.items()
    )
    exact = solve_demand_exact_hls(problem, initial_state=initial)
    assert exact.value == pytest.approx(expected, abs=1e-12)


def test_baselines_obey_action_and_information_timing():
    instance = build_e1_instance(eta=0.75, demand="stationary", horizon=2)
    policies = four_policies(instance)
    static = policies["BEST_STATIC"]
    assert static.static_routing is not None
    # Every route assignment is a deterministic task-to-agent mapping.
    assert set(static.static_routing) == {1, 2}
    assert set(static.static_routing.values()) <= {"M1", "M2"}

    strong = policies["STRONG_SEP"]
    for (state, task), selected in strong.operational_decisions.items():
        rewards = {
            action: instance.problem.environment.reward.operational_reward(
                state, task, action
            )
            for action in instance.problem.operational_actions
        }
        assert rewards[selected] == pytest.approx(max(rewards.values()))

    # A direct policy fixture makes opportunity timing observable: the
    # operational assignment is selected first; development is selected only
    # from the realized admissible set supplied by the runner.
    timing_development = {
        (state, task, action, available): NULL_DEVELOPMENT
        for state in (
            instance.initial_state,
            instance.initial_state.advanced(instance.initial_state.competence),
        )
        for task in (1, 2)
        for action in ("M1", "M2")
        for available in (False, True)
    }
    null_policy = DemandExecutablePolicy(
        operational_decisions={},
        development_decisions=timing_development,
        static_routing={1: "M1", 2: "M2"},
    )
    replay = make_replay(instance, 3)
    replay = replace(replay, task_path=(1, 1), opportunity_uniforms=(0.5, 0.5))
    result = run_policy(instance, "timing-control", null_policy, replay)
    first = result.trace.transitions[0]
    assert first.operational_action == "M1"
    assert first.opportunity.available is False
    assert first.development_action.is_null


def test_replay_is_reproducible_and_streams_are_separate():
    instance = build_e1_instance(eta=0.1, demand="changing", horizon=4)
    first = make_replay(instance, 91)
    again = make_replay(instance, 91)
    other = make_replay(instance, 92)
    assert first == again
    assert first.demand_seed != first.opportunity_seed
    assert first != other

    policies = four_policies(instance)
    results_a = run_paired(instance, policies, first)
    results_b = run_paired(instance, policies, again)
    assert results_a == results_b


def test_runner_rejects_infeasible_operational_and_development_actions():
    instance = build_e1_instance(eta=0.1, demand="stationary", horizon=1)
    replay = make_replay(instance, 7)
    invalid_operation = DemandExecutablePolicy(
        operational_decisions={},
        development_decisions={},
        static_routing={1: "M3", 2: "M3"},
    )
    with pytest.raises(ValueError, match="infeasible operational"):
        run_policy(instance, "invalid-operation", invalid_operation, replay)

    invalid_development = DemandExecutablePolicy(
        operational_decisions={},
        development_decisions={
            (instance.initial_state, task, "M1", False): DevelopmentDecision("M1", 1)
            for task in (1, 2)
        },
        static_routing={1: "M1", 2: "M1"},
    )
    replay_without_opportunity = replace(
        replay, task_path=(1,), opportunity_uniforms=(0.5,)
    )
    with pytest.raises(ValueError, match="infeasible development"):
        run_policy(
            instance,
            "invalid-development",
            invalid_development,
            replay_without_opportunity,
        )


def test_zero_probability_tasks_do_not_enter_static_policy_domain():
    instance = build_e1_instance(eta=0.1, demand="stationary", horizon=2)
    problem = replace(
        instance.problem,
        demand_process=StationaryTaskDemand({1: 1.0, 2: 0.0}),
    )
    static = solve_demand_best_static_routing(
        problem, initial_state=instance.initial_state
    )
    assert static.routing[0][0] == 1
    assert all(task == 1 for task, _ in static.routing)


def test_strong_sep_uses_continuation_only_to_resolve_immediate_ties():
    instance = build_e1_instance(eta=0.75, demand="stationary", horizon=2)
    competence = BoundedMatrixCompetence(((0.6, 0.6), (0.6, 0.6)))
    environment = replace(instance.problem.environment, competence=competence)
    problem = replace(instance.problem, environment=environment)
    initial = replace(instance.initial_state, competence=competence.initial)

    strong = solve_demand_exact_strong_sep(problem, initial_state=initial)
    selected = strong.policy.operational_decisions[(initial, 1)]
    immediate = {
        action: environment.reward.operational_reward(initial, 1, action)
        for action in problem.operational_actions
    }

    assert immediate["M1"] == immediate["M2"]
    assert selected == "M2"  # only M2 generates development opportunity
    assert strong.policy.tie_coordination == (
        "continuation value only among immediate-reward maximizers"
    )
    hls = solve_demand_exact_hls(problem, initial_state=initial)
    assert strong.value == pytest.approx(hls.value, abs=1e-12)
