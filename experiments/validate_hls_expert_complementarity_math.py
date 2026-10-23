#!/usr/bin/env python3
"""Exact finite validation for the HLS expert-complementarity pilot.

This is a mathematical check of a three-expert binary model, not a campaign.
All probabilities are rational and all eight error masks are enumerated.
"""

from __future__ import annotations

import json
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path


OUT = Path("results/experiments/hls_expert_complementarity_math_validation/results.json")
TASK_ACCURACY = {
    "X": (F(4, 5), F(7, 10), F(7, 10)),
    "Y": (F(7, 10), F(4, 5), F(7, 10)),
}
RHOS = (F(0), F(1, 4), F(1))
QUALITY_REQUIREMENT = {"X": F(3, 4), "Y": F(41, 50)}
COALITIONS = tuple(
    coalition
    for size in range(1, 4)
    for coalition in combinations(range(3), size)
)


def _fraction_text(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _decimal(value: F) -> float:
    return float(value)


def error_pattern_probabilities(accuracies: tuple[F, ...], rho: F) -> dict[tuple[int, ...], F]:
    """Mixture of independent errors and the specified common-U coupling.

    In the common component, U ~ Uniform[0,1] and E_i = 1[U > p_i].
    This is a copula-mixture weight, not a Pearson correlation coefficient.
    """
    if len(accuracies) != 3 or not F(0) <= rho <= F(1):
        raise ValueError("expected three experts and rho in [0, 1]")
    if any(not F(0) <= p <= F(1) for p in accuracies):
        raise ValueError("expert accuracy must lie in [0, 1]")
    patterns = tuple(product((0, 1), repeat=3))
    boundaries = sorted({F(0), F(1), *accuracies})
    common: dict[tuple[int, ...], F] = {pattern: F(0) for pattern in patterns}
    for lower, upper in zip(boundaries, boundaries[1:]):
        midpoint = (lower + upper) / 2
        pattern = tuple(int(midpoint > p) for p in accuracies)
        common[pattern] += upper - lower

    result = {}
    for pattern in patterns:
        independent = F(1)
        for error, p in zip(pattern, accuracies):
            independent *= (1 - p) if error else p
        result[pattern] = (1 - rho) * independent + rho * common[pattern]
    if sum(result.values(), F(0)) != 1:
        raise AssertionError("error-pattern probabilities do not sum to one")
    return result


def sum_rule_accuracy(accuracies: tuple[F, ...], coalition: tuple[int, ...], rho: F) -> F:
    """Exact accuracy of Kittler's equal-prior sum rule for a fixed coalition.

    Expert i reports p_i for its predicted class and 1-p_i for the other
    class. With a uniform true label, an error mask's posterior-score margin
    for the true class is sum_i (2*p_i-1) with the sign reversed for errors.
    A zero margin is resolved deterministically in favour of class 0; because
    Y is balanced and the errors are label-symmetric, that tie contributes 1/2.
    """
    if not coalition or any(i not in range(3) for i in coalition):
        raise ValueError("coalition must be a non-empty subset of expert indices 0..2")
    pattern_probs = error_pattern_probabilities(accuracies, rho)
    accuracy = F(0)
    for errors, probability in pattern_probs.items():
        margin = sum(
            (1 - 2 * accuracies[i]) if errors[i] else (2 * accuracies[i] - 1)
            for i in coalition
        )
        outcome_accuracy = F(1) if margin > 0 else F(0) if margin < 0 else F(1, 2)
        accuracy += probability * outcome_accuracy
    return accuracy


def coalition_cost(coalition: tuple[int, ...]) -> dict[str, F | int]:
    size = len(coalition)
    execution = F(size)
    coordination = F(size - 1, 4)
    return {
        "expert_calls": size,
        "execution_cost": execution,
        "coordination_messages": size - 1,
        "coordination_cost": coordination,
        "total_cost": execution + coordination,
        "latency": F(1) + coordination,
    }


def feasible(task: str, coalition: tuple[int, ...]) -> bool:
    costs = coalition_cost(coalition)
    if task == "X":
        return (
            costs["expert_calls"] <= 1
            and costs["coordination_messages"] <= 0
            and costs["total_cost"] <= 1
            and costs["latency"] <= 1
        )
    if task == "Y":
        return (
            costs["expert_calls"] <= 3
            and costs["coordination_messages"] <= 2
            and costs["total_cost"] <= F(7, 2)
            and costs["latency"] <= F(3, 2)
        )
    raise ValueError(f"unknown task {task}")


def pareto_frontier(task: str, rho: F) -> tuple[tuple[int, ...], ...]:
    """Nondominated feasible actions on accuracy (higher), total cost/latency (lower)."""
    feasible_rows = [
        (coalition, sum_rule_accuracy(TASK_ACCURACY[task], coalition, rho), coalition_cost(coalition))
        for coalition in COALITIONS if feasible(task, coalition)
    ]
    frontier = []
    for coalition, quality, costs in feasible_rows:
        dominated = False
        for other, other_quality, other_costs in feasible_rows:
            if other == coalition:
                continue
            weakly_better = (
                other_quality >= quality
                and other_costs["total_cost"] <= costs["total_cost"]
                and other_costs["latency"] <= costs["latency"]
            )
            strictly_better = (
                other_quality > quality
                or other_costs["total_cost"] < costs["total_cost"]
                or other_costs["latency"] < costs["latency"]
            )
            if weakly_better and strictly_better:
                dominated = True
                break
        if not dominated:
            frontier.append(coalition)
    return tuple(frontier)


def _named(coalition: tuple[int, ...]) -> str:
    return "{" + ",".join(f"e{i + 1}" for i in coalition) + "}"


def build_result() -> dict:
    pattern_table = {}
    for task, accuracies in TASK_ACCURACY.items():
        pattern_table[task] = {
            _fraction_text(rho): {
                "".join(map(str, pattern)): _fraction_text(probability)
                for pattern, probability in error_pattern_probabilities(accuracies, rho).items()
            }
            for rho in RHOS
        }

    rows = []
    for coalition in COALITIONS:
        cost = coalition_cost(coalition)
        rows.append({
            "coalition": _named(coalition),
            "execution_cost": _fraction_text(cost["execution_cost"]),
            "coordination_messages": cost["coordination_messages"],
            "coordination_cost": _fraction_text(cost["coordination_cost"]),
            "total_cost": _fraction_text(cost["total_cost"]),
            "latency": _fraction_text(cost["latency"]),
            "feasible_X": feasible("X", coalition),
            "feasible_Y": feasible("Y", coalition),
            "quality": {
                task: {
                    _fraction_text(rho): _fraction_text(
                        sum_rule_accuracy(accuracies, coalition, rho)
                    )
                    for rho in RHOS
                }
                for task, accuracies in TASK_ACCURACY.items()
            },
        })

    pareto = {
        task: {
            _fraction_text(rho): [_named(s) for s in pareto_frontier(task, rho)]
            for rho in RHOS
        }
        for task in TASK_ACCURACY
    }
    return {
        "experiment": "exact mathematical validation of HLS expert-complementarity pilot",
        "campaign_executed": False,
        "model": {
            "task_accuracy": {
                task: [_fraction_text(p) for p in accuracies]
                for task, accuracies in TASK_ACCURACY.items()
            },
            "rho_values": [_fraction_text(rho) for rho in RHOS],
            "dependence_definition": "with probability rho, E_i=1[U>p_ik] for one shared U~Uniform[0,1]; otherwise independent U_i",
            "rho_interpretation": "mixture weight for common-U coupling, not Pearson correlation",
            "class_prior": ["1/2", "1/2"],
            "posterior_output": "expert i assigns p_ik to its predicted label and 1-p_ik to the other label",
            "sum_rule": "argmax_y [(1-|S|)P(Y=y) + sum_{i in S} P_i(Y=y|x_i)]; uniform prior reduces to sum of posteriors",
            "tie_rule": "choose class 0; under balanced labels and symmetric errors a score tie contributes exactly 1/2 accuracy",
            "requirements": {task: _fraction_text(q) for task, q in QUALITY_REQUIREMENT.items()},
            "resource_constraints": {
                "X": {"expert_call_budget": 1, "coordination_message_limit": 0, "total_cost_budget": "1", "deadline": "1"},
                "Y": {"expert_call_budget": 3, "coordination_message_limit": 2, "total_cost_budget": "7/2", "deadline": "3/2"},
            },
            "cost_model": "execution cost=1 per expert call; coordination cost=1/4 per additional member; latency=1+1/4*(|S|-1)",
        },
        "error_pattern_probabilities": pattern_table,
        "coalitions": rows,
        "pareto_frontier": pareto,
        "full_coalition_quality_check": {
            _fraction_text(rho): _fraction_text(sum_rule_accuracy(TASK_ACCURACY["X"], (0, 1, 2), rho))
            for rho in RHOS
        },
        "validation": {
            "all_pattern_distributions_sum_to_one": True,
            "seven_nonempty_coalitions_enumerated": len(COALITIONS) == 7,
            "all_posterior_ties_resolved_deterministically": True,
        },
        "scope_note": "DCS-LA is task-stratified local accuracy here; with only two discrete contexts it reduces to selecting the highest-accuracy expert within the task type. The subset oracle is diagnostic, not deployable.",
    }


def main() -> None:
    result = build_result()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": OUT.as_posix(),
        "full_coalition_accuracy": result["full_coalition_quality_check"],
        "pareto_frontier": result["pareto_frontier"],
        "campaign_executed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
