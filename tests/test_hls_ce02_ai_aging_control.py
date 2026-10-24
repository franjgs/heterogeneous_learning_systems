from fractions import Fraction as F
from itertools import combinations

import pytest

from experiments.synthetic.ai_aging_control import (
    P_A,
    P_B,
    PATTERNS,
    majority_error_risk,
    marginal_error,
    p_lambda,
    pair_correlation,
    pair_covariance,
    pair_joint_error,
    validate_distribution,
)


PAIRS = tuple(combinations(range(3), 2))


@pytest.mark.parametrize("pmf", [P_A, P_B])
def test_exact_pmfs_are_complete_normalized_and_nonnegative(pmf):
    validate_distribution(pmf)
    assert tuple(pmf) == PATTERNS
    assert all(probability >= 0 for probability in pmf.values())
    assert sum(pmf.values(), F(0)) == 1


@pytest.mark.parametrize("pmf", [P_A, P_B])
def test_each_classifier_has_exact_marginal_error_rate_one_fifth(pmf):
    assert tuple(marginal_error(pmf, i) for i in range(3)) == (F(1, 5),) * 3


def test_distribution_a_pairwise_joint_error_covariance_and_majority_risk():
    assert tuple(pair_joint_error(P_A, i, j) for i, j in PAIRS) == (F(1, 10),) * 3
    assert tuple(pair_covariance(P_A, i, j) for i, j in PAIRS) == (F(3, 50),) * 3
    assert tuple(pair_correlation(P_A, i, j) for i, j in PAIRS) == (F(3, 8),) * 3
    assert majority_error_risk(P_A) == F(3, 10)


def test_distribution_b_pairwise_joint_error_covariance_and_majority_risk():
    assert tuple(pair_joint_error(P_B, i, j) for i, j in PAIRS) == (F(1, 5),) * 3
    assert tuple(pair_covariance(P_B, i, j) for i, j in PAIRS) == (F(4, 25),) * 3
    assert tuple(pair_correlation(P_B, i, j) for i, j in PAIRS) == (F(1),) * 3
    assert majority_error_risk(P_B) == F(1, 5)


@pytest.mark.parametrize("lam", [F(0), F(1, 4), F(1, 2), F(3, 4), F(1)])
def test_transition_preserves_marginals_and_changes_dependence_exactly(lam):
    pmf = p_lambda(lam)
    assert tuple(marginal_error(pmf, i) for i in range(3)) == (F(1, 5),) * 3
    assert tuple(pair_joint_error(pmf, i, j) for i, j in PAIRS) == (F(1, 10) + F(1, 10) * lam,) * 3
    assert tuple(pair_covariance(pmf, i, j) for i, j in PAIRS) == (F(3, 50) + F(1, 10) * lam,) * 3
    assert majority_error_risk(pmf) == F(3, 10) - F(1, 10) * lam


def test_transition_endpoints_are_the_supplied_distributions():
    assert p_lambda(0) == P_A
    assert p_lambda(1) == P_B


@pytest.mark.parametrize("lam", [F(-1, 100), F(101, 100)])
def test_transition_rejects_lambda_outside_unit_interval(lam):
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        p_lambda(lam)


def test_distribution_validator_rejects_incomplete_and_unnormalized_inputs():
    with pytest.raises(ValueError, match="exactly all eight"):
        validate_distribution({"000": F(1)})
    invalid = dict(P_A)
    invalid["000"] += F(1, 100)
    with pytest.raises(ValueError, match="sum exactly to one"):
        validate_distribution(invalid)
