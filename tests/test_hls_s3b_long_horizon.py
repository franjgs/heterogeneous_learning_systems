from experiments import run_hls_s3b_long_horizon as experiment


def test_long_horizon_configuration_and_predeclared_parameters():
    assert experiment.HORIZON == 2400
    assert len(experiment.EVAL_SEEDS) == 30
    assert experiment.CONDITIONS["S3b-L1_abrupt"]["switches"] == (1200,)
    assert experiment.CONDITIONS["S3b-L2_recurrent"]["switches"] == (600, 1200, 1800)
    assert experiment.sw_window("S3b-L0_stationary") == 2400
    assert experiment.sw_window("S3b-L1_abrupt") == 273
    assert experiment.sw_window("S3b-L2_recurrent") == 158
    params = experiment.glr_parameters()
    assert params["base_arm_count"] == 9
    assert params["delta_glr"] == 1 / 2400
    assert 0 < params["epsilon_uniform_exploration"] < 1


def test_regime_matrices_change_optimum_and_preserve_original_amplitude():
    from experiments.run_hls_s3b_nonstationary_unknown_assignment import permutation_id

    for condition in experiment.CONDITIONS:
        spec = experiment.CONDITIONS[condition]
        for regime, start in enumerate((0,) + spec["switches"]):
            matrix = experiment.means_at(condition, start)
            assert set(value for row in matrix for value in row) == {0.2, 0.8}
    for condition in ("S3b-L1_abrupt", "S3b-L2_recurrent"):
        spec = experiment.CONDITIONS[condition]
        optima = [permutation_id(experiment.solve(experiment.means_at(condition, t)))
                  for t in (0,) + spec["switches"]]
        assert all(left != right for left, right in zip(optima, optima[1:]))


def test_common_calibration_feedback_and_no_environment_state_in_policy():
    uniforms = experiment.paired_uniforms(experiment.EVAL_SEEDS[0])
    histories = []
    for condition in experiment.CONDITIONS:
        history, ids = experiment.initial_history(condition, uniforms)
        assert len(ids) == experiment.CALIBRATION_PERIODS
        assert all(len(rows) == 3 for rows in history.values())
        model = experiment._new_model("GLR_CUCB", condition, experiment.EVAL_SEEDS[0], history)
        assert not hasattr(model, "competencies")
        assert not hasattr(model, "breakpoints")
        histories.append(history)
    # The common first nine periods precede every scheduled change.
    assert histories[0] == histories[1] == histories[2]
    assert experiment.paired_uniforms(experiment.EVAL_SEEDS[0]) == uniforms


def test_glr_forced_matching_respects_the_shared_bipartite_constraints():
    from experiments.run_hls_s3b_nonstationary_unknown_assignment import (
        matches_from_id,
    )

    condition = "S3b-L2_recurrent"
    uniforms = experiment.paired_uniforms(experiment.EVAL_SEEDS[0])
    history, _ = experiment.initial_history(condition, uniforms)
    model = experiment._new_model("GLR_CUCB", condition, experiment.EVAL_SEEDS[0], history)
    arm = model.forced_arm(experiment.CALIBRATION_PERIODS)
    assert arm is not None
    selected = model.forced_matching(arm, experiment._all_perfect_matchings())
    assert arm in selected
    assert len(selected) == 3
    assert len({i for i, _ in selected}) == 3
    assert len({k for _, k in selected}) == 3
    assert matches_from_id(experiment.permutation_id(selected)) == selected


def test_compact_episode_preserves_seed_metrics_not_repeated_trajectories():
    episode = {
        "seed": 9300,
        "policies": {
            "UCB1_MATCHING": {"cumulative_expected_reward": 10.0,
                              "expected_reward_by_period": [1.0, 2.0],
                              "expected_regret_by_period": [0.0, 1.0],
                              "assignment_ids": [5, 6]},
            "GLR_CUCB": {"cumulative_expected_reward": 9.0,
                         "detections": [{"period": 12, "arms": [[0, 0]],
                                         "statistics": [10.0], "thresholds": [9.0],
                                         "samples": [20]}],
                         "assignment_ids": [5, 6]},
        },
    }
    compact = experiment.compact_episode(episode)
    assert compact["seed"] == 9300
    assert compact["policies"]["UCB1_MATCHING"]["cumulative_expected_reward"] == 10.0
    assert "assignment_ids" not in compact["policies"]["UCB1_MATCHING"]
    assert compact["policies"]["GLR_CUCB"]["detections"][0]["period"] == 12
