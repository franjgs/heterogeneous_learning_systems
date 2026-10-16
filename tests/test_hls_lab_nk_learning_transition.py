"""Unit checks for the dimension-generalized, existing MIS-v2 transition."""

import pytest

from hls.discover_develop_v2 import capability_after_exposure, eta_to_lambda
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk


@pytest.mark.parametrize("n,k", [(1, 1), (2, 2), (3, 2), (4, 3)])
def test_mis_v2_transition_supports_required_nk_shapes(n, k):
    competence = tuple(tuple((i + j) / (n + k) for j in range(k)) for i in range(n))
    effort = tuple(tuple(0.25 if (i + j) % 2 == 0 else 0.0 for j in range(k)) for i in range(n))
    eta = tuple(tuple(0.1 + 0.02 * ((i + j) % 3) for j in range(k)) for i in range(n))
    after = mis_v2_transition_nk(competence, effort, LearningProfileNK(eta))
    for i in range(n):
        for j in range(k):
            expected = capability_after_exposure(
                competence[i][j], effort[i][j], rate=eta_to_lambda(eta[i][j]),
            )
            assert after[i][j] == expected
            assert (after[i][j] > competence[i][j]) == (effort[i][j] > 0 and competence[i][j] < 1)


def test_mis_v2_preserves_zero_effort_boundaries_and_has_no_cross_cell_transfer():
    state = ((0.0, 1.0), (0.4, 0.7))
    profile = LearningProfileNK(((0.2, 0.3), (0.1, 0.25)))
    effort = ((0.5, 0.5), (0.0, 0.0))
    after = mis_v2_transition_nk(state, effort, profile)
    assert after[0][0] > 0.0
    assert after[0][1] == 1.0
    assert after[1] == state[1]
    assert mis_v2_transition_nk(state, effort, profile, enabled=False) == state
    assert mis_v2_transition_nk(state, ((0.0, 0.0), (0.0, 0.0)), profile) == state


def test_mis_v2_exposure_and_eta_monotonicity_match_existing_scalar_contract():
    c = 0.35
    low_eta = LearningProfileNK(((0.1,),))
    high_eta = LearningProfileNK(((0.3,),))
    low_exposure = mis_v2_transition_nk(((c,),), ((0.25,),), low_eta)[0][0]
    high_exposure = mis_v2_transition_nk(((c,),), ((0.75,),), low_eta)[0][0]
    higher_rate = mis_v2_transition_nk(((c,),), ((0.25,),), high_eta)[0][0]
    assert c < low_exposure < high_exposure < 1.0
    assert higher_rate > low_exposure


def test_learning_profile_rejects_invalid_or_mismatched_parameters():
    for eta in (0.0, 1.0, -0.1, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            LearningProfileNK(((eta,),))
    with pytest.raises(ValueError, match="rectangular"):
        LearningProfileNK(((0.2,), (0.3, 0.4)))
    with pytest.raises(ValueError, match="requires 2×2"):
        LearningProfileNK(((0.2,),)).validate_dimensions(2, 2)
    with pytest.raises(ValueError, match="shape 1×1"):
        mis_v2_transition_nk(((0.2,),), ((0.1, 0.1),), LearningProfileNK(((0.2,),)))
