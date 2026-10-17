"""CE-25 protocol and mechanism checks; no stochastic campaigns are run."""

from hls.discover_v0 import JOINT_ACTIONS, production_inputs
from hls.hls_lab_v1 import (ExploreThenGreedy, FixedRouting, evaluate_problem,
                            feasible_actions, run_sequence)
from experiments.synthetic.hls_lab_v1.ce25 import (
    AB_ORDER_FAMILIES, REFERENCE_TEAM, ab_orders, c_order, equivalent_outcome_actions,
    move_action_to_rank, problem, repeated_sequence, run_condition, successful_action,
    training_sequence, write_experiment,
)


def test_preregistered_order_family_ranks_and_action_sets():
    assert len(AB_ORDER_FAMILIES) == 6
    for family in AB_ORDER_FAMILIES:
        orders = ab_orders(family)
        for context in ("A", "B"):
            assert set(orders[context]) == set(feasible_actions(problem(context)))
            assert len(orders[context]) == 10
    assert ab_orders("SUCCESS_FIRST")["A"][0] == successful_action("A")
    assert ab_orders("SUCCESS_FIRST")["B"][0] == successful_action("B")
    assert ab_orders("SUCCESS_LAST")["A"][-1] == successful_action("A")
    assert ab_orders("SUCCESS_LAST")["B"][-1] == successful_action("B")
    assert ab_orders("BALANCED_A_FIRST_B_LAST")["A"][0] == successful_action("A")
    assert ab_orders("BALANCED_A_FIRST_B_LAST")["B"][-1] == successful_action("B")
    assert ab_orders("BALANCED_A_LAST_B_FIRST")["A"][-1] == successful_action("A")
    assert ab_orders("BALANCED_A_LAST_B_FIRST")["B"][0] == successful_action("B")


def test_paired_learned_and_exploration_only_have_identical_train_actions_and_rewards():
    orders = ab_orders("SUCCESS_LAST")
    train = training_sequence(("A", "B"), orders)
    evaluation = repeated_sequence(("A", "B"), orders, 10)
    learned = run_condition("LEARNED", train, evaluation, trial_id="paired")
    exploration = run_condition("EXPLORATION_ONLY", train, evaluation, trial_id="paired")
    learned_train = [row for row in learned if row["phase"] == "TRAIN"]
    exploration_train = [row for row in exploration if row["phase"] == "TRAIN"]
    assert [(r["problem_id"], r["action_id"], r["success"]) for r in learned_train] == [
        (r["problem_id"], r["action_id"], r["success"]) for r in exploration_train]
    assert len(learned_train) == 20
    assert all(row["theta_updated"] for row in learned_train)
    assert not any(row["theta_updated"] for row in exploration_train)
    assert all(row["competence_before"] == row["competence_after"] for row in learned_train)


def test_exploration_schedule_is_reward_blind_and_matches_every_declared_order():
    for family in AB_ORDER_FAMILIES:
        orders = ab_orders(family)
        train = training_sequence(("A", "B"), orders)
        evaluation = repeated_sequence(("A", "B"), orders, 1)
        normal = run_condition("EXPLORATION_ONLY", train, evaluation,
                               trial_id=family, feedback_mode="TRUE")
        inverted = run_condition("EXPLORATION_ONLY", train, evaluation,
                                 trial_id=family, feedback_mode="INVERTED")
        assert [(r["problem_id"], r["action_id"]) for r in normal] == [
            (r["problem_id"], r["action_id"]) for r in inverted]
        training = [row for row in normal if row["phase"] == "TRAIN"]
        for context in ("A", "B"):
            context_rows = [row for row in training if row["problem_id"] == context]
            assert [row["action_id"] for row in context_rows] == [
                JOINT_ACTIONS.index(action) for action in orders[context]]
            successful_position = next(i + 1 for i, row in enumerate(context_rows) if row["success"])
            assert successful_position == orders[context].index(successful_action(context)) + 1


def test_memory_only_persists_observations_but_is_behaviorally_fixed():
    orders = ab_orders("SUCCESS_LAST")
    train = training_sequence(("A", "B"), orders)
    evaluation = repeated_sequence(("A", "B"), orders, 2)
    fixed = run_condition("FIXED", train, evaluation, trial_id="memory")
    memory = run_condition("MEMORY_ONLY", train, evaluation, trial_id="memory")
    assert [(r["problem_id"], r["action_id"], r["success"]) for r in fixed] == [
        (r["problem_id"], r["action_id"], r["success"]) for r in memory]
    assert len(memory[-1]["theta_after"]) == 2
    assert memory[-1]["memory_observation_count_after"] == 20
    eval_rows = [row for row in memory if row["phase"] == "EVAL"]
    assert all(row["memory_observation_count_before"] == 20 == row["memory_observation_count_after"]
               for row in eval_rows)
    assert not any(row["theta_updated"] for row in memory)


def test_learned_choice_uses_reward_and_inverted_feedback_is_only_a_label_intervention():
    orders = ab_orders("SUCCESS_LAST")
    train = training_sequence(("A", "B"), orders)
    evaluation = repeated_sequence(("A", "B"), orders, 1)
    true_rows = run_condition("LEARNED", train, evaluation, trial_id="reward")
    inverted_rows = run_condition("LEARNED", train, evaluation,
                                  feedback_mode="INVERTED", trial_id="reward")
    true_eval = [row for row in true_rows if row["phase"] == "EVAL"]
    inverted_eval = [row for row in inverted_rows if row["phase"] == "EVAL"]
    assert [row["action_id"] for row in true_eval] == [48, 4]
    assert all(row["success"] is True for row in true_eval)
    assert all(row["success"] is False for row in inverted_eval)
    assert [(row["problem_id"], row["action_id"], row["outputs"], row["success"])
            for row in [r for r in true_rows if r["phase"] == "TRAIN"]] == [
            (row["problem_id"], row["action_id"], row["outputs"], row["success"])
            for row in [r for r in inverted_rows if r["phase"] == "TRAIN"]]
    assert true_eval[0]["label_used_for_learning"] == 1.0
    assert inverted_eval[0]["label_used_for_learning"] == 0.0


def test_equal_outcome_control_has_identical_physics_and_resource_use():
    actions = equivalent_outcome_actions()
    spec = problem("EQ", actions)
    outputs = [production_inputs(REFERENCE_TEAM.real_matrix, action) for action in actions]
    efforts = [sum(sum(row) for row in action) for action in actions]
    outcomes = [evaluate_problem(value, (0.1, 0.1)) for value in outputs]
    assert outputs == [(0.0, 0.0), (0.0, 0.0)]
    assert efforts == [1.0, 1.0]
    assert [value.success for value in outcomes] == [False, False]
    assert spec.resource_budget == 1.0


def test_complementarity_context_orders_and_unseen_context_have_no_transfer():
    for rank in (1, 19, 37):
        order = c_order(rank)
        assert len(order) == len(set(order)) == 37
        assert order[rank - 1] == successful_action("C")
    orders = ab_orders("CANONICAL")
    train = training_sequence(("A", "B"), orders)
    unseen = repeated_sequence(("C",), {"C": c_order(1)}, 3)
    rows = run_condition("LEARNED", train, unseen, trial_id="unseen")
    eval_rows = [row for row in rows if row["phase"] == "EVAL"]
    assert len(eval_rows) == 3
    assert len({row["action_id"] for row in eval_rows}) == 1
    assert all(row["theta_before"] == row["theta_after"] for row in eval_rows)
    assert all(not row["theta_updated"] for row in eval_rows)
    assert not any(key[0] == "C" for key, _, _ in eval_rows[0]["theta_before"])
    # The default first action happens to be the C solution in this fixed
    # diagnostic order; success is not evidence of transfer (no C theta row).
    assert all(row["success"] for row in eval_rows)
    assert all(row["action_id"] == JOINT_ACTIONS.index(successful_action("C")) for row in eval_rows)


def test_analytical_discovery_and_horizon_predictions_match_policy_rollouts():
    orders = ab_orders("SUCCESS_LAST")
    train = training_sequence(("A", "B"), orders)
    for horizon in (1, 10, 20):
        evaluation = repeated_sequence(("A", "B"), orders, horizon)
        learned = run_condition("LEARNED", train, evaluation, trial_id=f"theory-{horizon}")
        exploration = run_condition("EXPLORATION_ONLY", train, evaluation,
                                    trial_id=f"theory-{horizon}")
        lt = [row for row in learned if row["phase"] == "TRAIN"]
        le = [row for row in learned if row["phase"] == "EVAL"]
        ee = [row for row in exploration if row["phase"] == "EVAL"]
        assert sum(bool(row["success"]) for row in lt) == 2
        predicted_exploration = 2 * (horizon // 10)
        # With success at rank K, each context's evaluation cycle hits it at K.
        assert sum(bool(row["success"]) for row in ee) == predicted_exploration
        assert sum(bool(row["success"]) for row in le) == 2 * horizon


def test_li_off_keeps_capabilities_fixed_and_budgets_respected():
    orders = ab_orders("CANONICAL")
    train = training_sequence(("A", "B"), orders)
    evaluation = repeated_sequence(("A", "B"), orders, 1)
    for policy in ("FIXED", "MEMORY_ONLY", "EXPLORATION_ONLY", "LEARNED"):
        rows = run_condition(policy, train, evaluation, trial_id="budget")
        assert all(row["competence_before"] == row["competence_after"] for row in rows)
        assert all(row["effort"] <= row["budget"] + 1e-12 for row in rows)
        assert all(row["action"] in feasible_actions(problem(str(row["problem_id"]),
                                                             orders[str(row["problem_id"])])) for row in rows)


def test_complete_artifact_is_reproducible_and_contains_paired_integrity_checks(tmp_path):
    import csv
    import hashlib
    import json

    first, second = tmp_path / "ce25-a", tmp_path / "ce25-b"
    manifest_a = write_experiment(first)
    manifest_b = write_experiment(second)
    assert manifest_a["raw_records"] == manifest_b["raw_records"] == 4682
    assert manifest_a["summary_rows"] == manifest_b["summary_rows"] == 106
    for name in ("episodes.jsonl", "summary.csv", "paired_contrasts.csv"):
        a, b = (first / name).read_bytes(), (second / name).read_bytes()
        assert a == b
        assert hashlib.sha256(a).hexdigest() == manifest_a["output_sha256"][name]
    contrasts = list(csv.DictReader((first / "paired_contrasts.csv").open()))
    main_pairs = [row for row in contrasts if row["trial_id"].startswith("AB_MAIN|")]
    assert len(main_pairs) == 18
    assert all(row["training_action_reward_state_identical"] == "True" for row in main_pairs)
    episode_rows = [json.loads(line) for line in (first / "episodes.jsonl").read_text().splitlines()]
    assert len(episode_rows) == 4682
    assert {row["phase"] for row in episode_rows} == {"TRAIN", "EVAL"}


def test_ce25_physical_step_matches_frozen_v1_sequence_engine():
    chosen = feasible_actions(problem("A"))[0]
    spec = problem("A", (chosen,))
    ce25 = run_condition("FIXED", (spec,), (), individual_learning=True,
                         trial_id="core-reuse")
    reference = run_sequence(REFERENCE_TEAM, (spec,), FixedRouting({"A": chosen}), eta=0.35,
                             individual_learning=True, organizational_learning=False)
    row, episode = ce25[0], reference.records[0]
    assert row["action"] == episode.action
    assert row["outputs"] == episode.outputs
    assert row["success"] == episode.success
    assert row["normalized_deficit"] == episode.normalized_deficit
    assert row["competence_after"] == episode.competence_after
    assert row["experience_after"] == episode.experience_after
    assert row["effort"] == episode.effort
