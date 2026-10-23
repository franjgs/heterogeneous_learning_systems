from experiments.run_hls_s4_transfer_frontier import make_case, solve_instance


def test_pq_case_reuses_fixed_physics_and_declared_demand_sequence():
    case = make_case(2, 3)
    assert [problem.problem_id for problem in case.problems] == [
        "task-x", "task-x", "task-y", "task-y", "task-y",
    ]
    assert case.organization.competence_initial == ((0.85, 0.15), (0.20, 0.20))
    assert case.profile.eta == ((0.20, 0.15), (0.12, 0.05))


def test_small_pq_instance_has_optional_transfer_and_nonnegative_value():
    row = solve_instance(1, 1)
    assert row["action_counts_per_period"]["A"] == [36, 36]
    assert row["action_counts_per_period"]["B"] == [72, 72]
    assert row["delta_B_minus_A"] >= -1e-10
    assert row["zero_efficacy_B_value"] == row["A"]["value"]
