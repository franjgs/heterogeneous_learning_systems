from fractions import Fraction as F

from experiments.validate_hls_expert_complementarity_math import (
    COALITIONS,
    TASK_ACCURACY,
    error_pattern_probabilities,
    feasible,
    pareto_frontier,
    sum_rule_accuracy,
)


def test_all_eight_error_patterns_have_exact_probability_mass_one():
    for task, probabilities in TASK_ACCURACY.items():
        for rho in (F(0), F(1, 4), F(1)):
            distribution = error_pattern_probabilities(probabilities, rho)
            assert len(distribution) == 8
            assert sum(distribution.values(), F(0)) == 1


def test_dependence_mixture_preserves_each_expert_marginal_error_rate():
    for task, probabilities in TASK_ACCURACY.items():
        for rho in (F(0), F(1, 4), F(1)):
            distribution = error_pattern_probabilities(probabilities, rho)
            for expert, accuracy in enumerate(probabilities):
                marginal_error = sum(
                    mass for pattern, mass in distribution.items() if pattern[expert]
                )
                assert marginal_error == 1 - accuracy


def test_sum_rule_reproduces_the_three_full_coalition_predictions_exactly():
    expected = {F(0): F(413, 500), F(1, 4): F(1589, 2000), F(1): F(7, 10)}
    for rho, quality in expected.items():
        assert sum_rule_accuracy(TASK_ACCURACY["X"], (0, 1, 2), rho) == quality
        assert sum_rule_accuracy(TASK_ACCURACY["Y"], (0, 1, 2), rho) == quality


def test_equal_confidence_disagreement_tie_uses_fixed_class_zero():
    # For two identical-accuracy experts, discordant outputs tie. With a
    # balanced label prior, deterministic class-0 resolution yields accuracy p.
    assert sum_rule_accuracy((F(7, 10),) * 3, (0, 1), F(0)) == F(7, 10)


def test_all_seven_coalitions_and_resource_feasibility_are_exact():
    assert len(COALITIONS) == 7
    assert tuple(s for s in COALITIONS if feasible("X", s)) == ((0,), (1,), (2,))
    assert tuple(s for s in COALITIONS if feasible("Y", s)) == COALITIONS


def test_exact_coalition_qualities_for_specialists_and_pair_fusion():
    for rho in (F(0), F(1, 4), F(1)):
        assert sum_rule_accuracy(TASK_ACCURACY["X"], (0,), rho) == F(4, 5)
        assert sum_rule_accuracy(TASK_ACCURACY["Y"], (1,), rho) == F(4, 5)
        assert sum_rule_accuracy(TASK_ACCURACY["X"], (0, 1), rho) == F(4, 5)
        assert sum_rule_accuracy(TASK_ACCURACY["Y"], (1, 2), rho) == F(4, 5)
        assert sum_rule_accuracy(TASK_ACCURACY["X"], (1, 2), rho) == F(7, 10)
        assert sum_rule_accuracy(TASK_ACCURACY["Y"], (0, 2), rho) == F(7, 10)


def test_quality_cost_latency_pareto_frontiers():
    assert pareto_frontier("X", F(0)) == ((0,),)
    assert pareto_frontier("X", F(1, 4)) == ((0,),)
    assert pareto_frontier("X", F(1)) == ((0,),)
    assert pareto_frontier("Y", F(0)) == ((1,), (0, 1, 2))
    assert pareto_frontier("Y", F(1, 4)) == ((1,),)
    assert pareto_frontier("Y", F(1)) == ((1,),)
