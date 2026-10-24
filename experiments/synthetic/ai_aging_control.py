"""Exact AI-aging dependence control specified by E2 for HLS-CE-02.

Three binary classifier-error indicators are encoded as strings ``e1e2e3``.
This is an exact finite-distribution control, not an HLS decision algorithm.
All probability calculations use rational arithmetic.
"""

from __future__ import annotations

import json
from fractions import Fraction as F
from itertools import product
from math import isqrt
from pathlib import Path
from typing import Mapping


PATTERNS = tuple("".join(bits) for bits in product("01", repeat=3))
P_A = {
    pattern: F(7, 10) if pattern == "000" else F(1, 10) if pattern in {"110", "101", "011"} else F(0)
    for pattern in PATTERNS
}
P_B = {
    pattern: F(4, 5) if pattern == "000" else F(1, 5) if pattern == "111" else F(0)
    for pattern in PATTERNS
}
LAMBDA_GRID = (F(0), F(1, 4), F(1, 2), F(3, 4), F(1))
OUTPUT = Path("results/experiments/hls_ce02_ai_aging/synthetic_control.json")


def _as_fraction(value: F | int | float) -> F:
    if isinstance(value, bool):
        raise ValueError("lambda must be a real number in [0, 1]")
    if isinstance(value, F):
        return value
    if isinstance(value, int):
        return F(value)
    if isinstance(value, float):
        return F(str(value))
    raise TypeError("lambda must be Fraction, int, or float")


def validate_distribution(pmf: Mapping[str, F]) -> None:
    """Reject incomplete, negative, or unnormalized three-error PMFs."""
    if set(pmf) != set(PATTERNS):
        raise ValueError("PMF must specify exactly all eight three-bit patterns")
    if any(not isinstance(probability, F) or probability < 0 for probability in pmf.values()):
        raise ValueError("probabilities must be non-negative Fractions")
    if sum(pmf.values(), F(0)) != 1:
        raise ValueError("probability mass must sum exactly to one")


def p_lambda(lam: F | int | float) -> dict[str, F]:
    """Linear mixture ``(1-lambda) P_A + lambda P_B`` for lambda in [0,1]."""
    weight = _as_fraction(lam)
    if not F(0) <= weight <= F(1):
        raise ValueError("lambda must lie in [0, 1]")
    result = {pattern: (1 - weight) * P_A[pattern] + weight * P_B[pattern] for pattern in PATTERNS}
    validate_distribution(result)
    return result


def marginal_error(pmf: Mapping[str, F], classifier: int) -> F:
    if classifier not in range(3):
        raise ValueError("classifier index must be 0, 1, or 2")
    validate_distribution(pmf)
    return sum((mass for pattern, mass in pmf.items() if pattern[classifier] == "1"), F(0))


def pair_joint_error(pmf: Mapping[str, F], first: int, second: int) -> F:
    if first not in range(3) or second not in range(3) or first == second:
        raise ValueError("pair must contain two distinct classifier indices 0, 1, 2")
    validate_distribution(pmf)
    return sum((mass for pattern, mass in pmf.items() if pattern[first] == pattern[second] == "1"), F(0))


def pair_covariance(pmf: Mapping[str, F], first: int, second: int) -> F:
    p_first = marginal_error(pmf, first)
    p_second = marginal_error(pmf, second)
    return pair_joint_error(pmf, first, second) - p_first * p_second


def pair_correlation(pmf: Mapping[str, F], first: int, second: int) -> F:
    p_first = marginal_error(pmf, first)
    p_second = marginal_error(pmf, second)
    variance_product = p_first * (1 - p_first) * p_second * (1 - p_second)
    if variance_product == 0:
        raise ValueError("pairwise correlation is undefined for a zero-variance error indicator")
    numerator_root = isqrt(variance_product.numerator)
    denominator_root = isqrt(variance_product.denominator)
    if numerator_root**2 != variance_product.numerator or denominator_root**2 != variance_product.denominator:
        raise ValueError("exact rational correlation is unavailable for an irrational variance product")
    return pair_covariance(pmf, first, second) / F(numerator_root, denominator_root)


def majority_error_risk(pmf: Mapping[str, F]) -> F:
    """Probability at least two of three classifiers err (majority error)."""
    validate_distribution(pmf)
    return sum((mass for pattern, mass in pmf.items() if pattern.count("1") >= 2), F(0))


def fraction_text(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def summarize(pmf: Mapping[str, F]) -> dict:
    validate_distribution(pmf)
    return {
        "joint_pmf": {pattern: fraction_text(pmf[pattern]) for pattern in PATTERNS},
        "individual_error_rates": [fraction_text(marginal_error(pmf, i)) for i in range(3)],
        "pairwise_joint_error": {
            f"{i + 1}{j + 1}": fraction_text(pair_joint_error(pmf, i, j))
            for i, j in ((0, 1), (0, 2), (1, 2))
        },
        "pairwise_covariance": {
            f"{i + 1}{j + 1}": fraction_text(pair_covariance(pmf, i, j))
            for i, j in ((0, 1), (0, 2), (1, 2))
        },
        "pairwise_correlation": {
            f"{i + 1}{j + 1}": fraction_text(pair_correlation(pmf, i, j))
            for i, j in ((0, 1), (0, 2), (1, 2))
        },
        "majority_error_risk": fraction_text(majority_error_risk(pmf)),
    }


def build_result() -> dict:
    return {
        "experiment": "HLS-CE-02 exact synthetic AI-aging dependence control",
        "source_status": "implemented from exact probabilities supplied in the CE task; no E2 source code was available or integrated",
        "campaign_executed": False,
        "classifier_count": 3,
        "error_encoding": "pattern e1e2e3; 1 means classifier error and 0 means correct",
        "risk_definition": "probability of error; majority rule errs when at least two of three classifiers err",
        "dependence_definition": "pairwise covariance of binary error indicators; correlations reported only as derived quantities",
        "transition": "P_lambda=(1-lambda)P_A+lambda P_B; lambda in [0,1]",
        "distributions": {"A": summarize(P_A), "B": summarize(P_B)},
        "transition_grid": {
            fraction_text(lam): summarize(p_lambda(lam)) for lam in LAMBDA_GRID
        },
        "validation": {
            "both_distributions_exactly_normalized": True,
            "both_distributions_nonnegative": True,
            "all_transition_marginals_equal_one_fifth": True,
            "dependency_changes_across_endpoints": True,
            "exact_rational_arithmetic": True,
        },
        "limitations": [
            "The synthetic construction establishes a mathematical contrast only; it is not empirical evidence of AI aging.",
            "P_lambda is the declared linear interpolation between the supplied endpoint distributions.",
        ],
    }


def main() -> None:
    result = build_result()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": OUTPUT.as_posix(), "A": result["distributions"]["A"],
                      "B": result["distributions"]["B"], "lambda_half": result["transition_grid"]["1/2"]}, indent=2))


if __name__ == "__main__":
    main()
