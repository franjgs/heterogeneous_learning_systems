from experiments.run_hls_s3b_change_observation_factorial import (
    BASE, CALIBRATION, HORIZON, TRANSIENT, calibration_matching,
    change_times, generate_randomness, matrix_at, opportunity_mask,
)


def test_recurrent_change_schedules_preserve_matrices_and_amplitudes():
    assert change_times(2_500) == (2_500, 5_000, 7_500)
    assert change_times(500) == tuple(range(500, HORIZON, 500))
    assert matrix_at(0, 2_500) == BASE
    assert matrix_at(2_500, 2_500) == TRANSIENT
    assert matrix_at(5_000, 2_500) == BASE
    assert matrix_at(500, 500) == TRANSIENT
    assert matrix_at(1_000, 500) == BASE
    assert TRANSIENT[2][0] - BASE[2][0] == 0.5


def test_opportunity_masks_are_paired_and_high_availability_contains_low():
    _, opportunity_uniforms = generate_randomness(8200)
    low = opportunity_mask(opportunity_uniforms[0], 0.25)
    high = opportunity_mask(opportunity_uniforms[0], 0.75)
    assert low & ~high == 0
    assert low != high


def test_calibration_retains_full_matching_action_catalog():
    matches = [calibration_matching(period) for period in range(CALIBRATION)]
    assert all(len(match) == 3 for match in matches)
    assert all(len({i for i, _ in match}) == 3 for match in matches)
    assert all(len({k for _, k in match}) == 3 for match in matches)
    assert set(edge for match in matches[:3] for edge in match) == {
        (i, k) for i in range(3) for k in range(3)
    }
