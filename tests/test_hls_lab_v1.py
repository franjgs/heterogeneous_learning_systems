"""Nine contract-level acceptance tests for HLS Laboratory v1 (CE-23)."""

from dataclasses import replace

import pytest

from hls.discover_v0 import JOINT_ACTIONS, production_inputs
from hls.discover_develop_v2 import capability_after_exposure
from hls.hls_lab_v1 import (
    DecisionView, ExploreThenGreedy, FixedRouting, GreedyAdaptive, OrganizationState,
    ProblemSpec, complementarity_class, evaluate_problem, feasible_actions, make_team,
    run_sequence, serialize_episode_records,
)

ETA = 0.35  # Existing Campaign-0/MIS-v2 reference value; not recalibrated here.
S_COMP = ((1.0, 0.0), (0.0, 1.0), (0.0, 0.0))
LEFT = ((1.0, 0.0), (0.0, 0.0), (0.0, 0.0))
RIGHT = ((0.0, 0.0), (0.0, 1.0), (0.0, 0.0))
TOGETHER = ((1.0, 0.0), (0.0, 1.0), (0.0, 0.0))


def view(problem_id, requirements, actions, state=S_COMP, budget=1.0):
    p = ProblemSpec(problem_id, requirements, budget, allowed_actions=actions)
    return DecisionView(p.problem_id, p.requirements, p.difficulty, p.orientation,
                        p.resource_budget, state, feasible_actions(p))


def test_p1_problem_orientation_and_difficulty_are_independent_of_reward():
    p1 = ProblemSpec("same-dir-low", (0.6, 0.4), 2.0)
    p2 = ProblemSpec("same-dir-high", (0.9, 0.6), 2.0)
    p3 = ProblemSpec("rotated", (0.4, 0.6), 2.0)
    assert p1.orientation == pytest.approx(p2.orientation)
    assert p1.difficulty == pytest.approx(1.0)
    assert p2.difficulty == pytest.approx(1.5)
    assert p3.difficulty == pytest.approx(p1.difficulty)
    y1 = production_inputs(S_COMP, LEFT)
    y2 = production_inputs(S_COMP, LEFT)
    assert y1 == y2
    assert evaluate_problem(y1, p1.requirements) != evaluate_problem(y2, p2.requirements)


def test_p2_team_only_complementarity_and_single_expert_control():
    team = make_team(S_COMP)
    joint = ProblemSpec("team-only", (0.8, 0.8), 2.0)
    assert TOGETHER in feasible_actions(joint)
    assert evaluate_problem(production_inputs(team.real_matrix, TOGETHER), joint.requirements).success
    assert complementarity_class(team, joint) == "team_only"
    for expert in range(3):
        assert not any(evaluate_problem(production_inputs(team.real_matrix, a), joint.requirements).success
                       for a in feasible_actions(joint)
                       if all(sum(row) == 0 for i, row in enumerate(a) if i != expert))
    single = ProblemSpec("single-control", (0.8, 0.0), 2.0)
    assert evaluate_problem(production_inputs(team.real_matrix, LEFT), single.requirements).success
    assert complementarity_class(team, single) == "single_sufficient"


def test_p3_no_false_complementarity_label():
    team = make_team(((1.0, 1.0), (1.0, 1.0), (0.0, 0.0)))
    problem = ProblemSpec("single-sufficient", (0.5, 0.5), 1.0)
    single_action = ((0.5, 0.5), (0.0, 0.0), (0.0, 0.0))
    assert single_action in feasible_actions(problem)
    assert evaluate_problem(production_inputs(team.real_matrix, single_action), problem.requirements).success
    assert complementarity_class(team, problem) == "single_sufficient"


def test_p4_individual_mis_v2_is_independent_of_organizational_learning():
    initial = make_team(((0.4, 0.0), (0.0, 1.0), (0.0, 0.0)))
    p = ProblemSpec("expose", (0.5, 0.0), 1.0, allowed_actions=(LEFT,))
    org = ExploreThenGreedy()
    on = run_sequence(initial, (p,), org, eta=ETA, individual_learning=True,
                      organizational_learning=False, seed=13)
    off = run_sequence(initial, (p,), org, eta=ETA, individual_learning=False,
                       organizational_learning=False, seed=13)
    assert on.records[0].competence_after[0][0] == pytest.approx(
        capability_after_exposure(0.4, 1.0, rate=-__import__('math').log1p(-ETA)))
    assert on.records[0].competence_after[1] == off.records[0].competence_after[1]
    assert off.records[0].competence_after == initial.real_matrix
    assert on.records[0].organization_theta_after == off.records[0].organization_theta_after == ()
    assert on.records[0].experience_after[0][0] == 1.0


def test_p5_tabular_organizational_learning_changes_future_choice_only_when_on():
    learner = ExploreThenGreedy()
    candidates = (RIGHT, LEFT)  # predeclared order deliberately starts with the poor A-context route
    a = view("A", (0.8, 0.0), candidates)
    state = OrganizationState()
    first = learner.choose(a, state)
    assert first == RIGHT
    state1 = learner.observe(state, "A", first, 0.0, enabled=True)
    second = learner.choose(a, state1)
    assert second == LEFT
    state2 = learner.observe(state1, "A", second, 1.0, enabled=True)
    future = learner.choose(a, state2)
    assert future == LEFT
    assert state2 != state and state2.update_count == 2

    frozen = OrganizationState()
    chosen = learner.choose(a, frozen)
    after_no_learning = learner.observe(frozen, "A", chosen, 0.0, enabled=False)
    assert after_no_learning == frozen
    assert learner.choose(a, after_no_learning) == chosen

    # Opposite outcome structure is separately represented by context B.
    b = view("B", (0.0, 0.8), candidates)
    assert learner.choose(b, state) == RIGHT
    b1 = learner.observe(state, "B", RIGHT, 1.0, enabled=True)
    assert learner.choose(b, b1) == LEFT  # untried arm exploration
    b2 = learner.observe(b1, "B", LEFT, 0.0, enabled=True)
    assert learner.choose(b, b2) == RIGHT


def test_p6_adaptation_can_change_action_without_policy_learning():
    problem = ProblemSpec("context", (0.5, 0.5), 1.0, allowed_actions=(LEFT, RIGHT))
    adaptive = GreedyAdaptive()
    first = adaptive.choose(view(problem.problem_id, problem.requirements,
                                 problem.allowed_actions, ((1, 0), (0, 1), (0, 0))), OrganizationState())
    second = adaptive.choose(view(problem.problem_id, problem.requirements,
                                  problem.allowed_actions, ((0, 0), (0, 1), (1, 0))), OrganizationState())
    assert first == LEFT and second == RIGHT
    assert first != second
    # GreedyAdaptive has no update operator: θ remains immutable.
    assert OrganizationState().update_count == 0


def test_p7_information_firewall_and_independent_controls():
    p = ProblemSpec("visible", (0.5, 0.0), 1.0, allowed_actions=(LEFT,))
    team = make_team(((0.4, 0.0), (0.0, 1.0), (0.0, 0.0)))
    v = view(p.problem_id, p.requirements, p.allowed_actions, team.estimated_matrix)
    assert not hasattr(v, "competence_real")
    assert not hasattr(v, "future_problems")
    learner = ExploreThenGreedy()
    li_only = run_sequence(team, (p, p), learner, eta=ETA, individual_learning=True,
                           organizational_learning=False, seed=4)
    lo_only = run_sequence(team, (p, p), learner, eta=ETA, individual_learning=False,
                           organizational_learning=True, seed=4)
    assert li_only.records[0].competence_after != li_only.records[0].competence_before
    assert li_only.final_organization.update_count == 0
    assert lo_only.final_team.real_matrix == team.real_matrix
    assert lo_only.final_organization.update_count == 2
    assert all(row.budget == 1.0 for row in li_only.records + lo_only.records)


def test_p8_preregistered_micro_domain_has_feasible_and_infeasible_cases():
    team = make_team(S_COMP)
    feasible = ProblemSpec("balanced-feasible", (0.8, 0.8), 2.0)
    infeasible = ProblemSpec("balanced-high", (0.95, 0.95), 1.0)
    assert any(evaluate_problem(production_inputs(team.real_matrix, a), feasible.requirements).success
               for a in feasible_actions(feasible))
    assert not any(evaluate_problem(production_inputs(team.real_matrix, a), infeasible.requirements).success
                   for a in feasible_actions(infeasible))
    assert feasible.difficulty < infeasible.difficulty
    assert infeasible.requirements == (0.95, 0.95)


def test_p9_seed_and_configuration_serialize_deterministically():
    team = make_team(S_COMP)
    p = ProblemSpec("repeat", (0.8, 0.0), 1.0, allowed_actions=(LEFT, RIGHT))
    org = ExploreThenGreedy()
    a = run_sequence(team, (p, p, p), org, eta=ETA, individual_learning=False,
                     organizational_learning=True, seed=72)
    b = run_sequence(team, (p, p, p), org, eta=ETA, individual_learning=False,
                     organizational_learning=True, seed=72)
    assert a == b
    assert len(a.records) == 3
    assert all(row.problem_id == "repeat" for row in a.records)
    serialized_a = serialize_episode_records(a.records)
    serialized_b = serialize_episode_records(b.records)
    assert serialized_a == serialized_b
    assert '"organization_theta_after"' in serialized_a
    assert '"action_id"' in serialized_a
