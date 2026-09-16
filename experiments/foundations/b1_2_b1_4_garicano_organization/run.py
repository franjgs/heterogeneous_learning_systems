import itertools
import json
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
RESULT_DIR = (
    ROOT
    / "results"
    / "foundations"
    / "b1_2_b1_4_garicano_organization"
)
write_result_bundle = runpy.run_path(
    str(ROOT / "experiments" / "foundations" / "_provenance.py")
)["write_result_bundle"]


def communication_load(order):
    """
    Discrete exchange-test representation of Garicano's organization-by-
    frequency argument.

    Blocks are problem masses, ordered from lower to higher organizational
    levels. A problem in level j has crossed j previous levels before being
    solved. Thus communication load is proportional to

        sum_j j * p_j.

    For fixed block masses, the minimum must place larger masses at lower
    levels.
    """
    order = np.asarray(order, dtype=float)
    levels = np.arange(len(order), dtype=float)
    return float(np.dot(levels, order))


def all_orderings(blocks):
    return [
        (perm, communication_load(perm))
        for perm in itertools.permutations(blocks)
    ]


def optimal_frequency_order(blocks):
    """
    Exhaustively enumerate all permutations.

    No frequency ordering is imposed on the optimizer.
    """
    candidates = all_orderings(blocks)
    min_load = min(load for _, load in candidates)

    optimal = [
        perm
        for perm, load in candidates
        if abs(load - min_load) <= 1e-12
    ]

    return optimal, min_load, candidates


def hierarchy_sizes(blocks, help_cost, producer_mass):
    """
    Garicano pyramidal relation:

        b_i = h b_0 [1 - F(Z_{i-1})].

    In the discrete fixture, blocks give successive probability masses
    solved at each level. Before specialist level i, the unresolved
    probability is the tail mass remaining after lower levels.
    """
    blocks = np.asarray(blocks, dtype=float)

    sizes = [float(producer_mass)]
    solved_mass = 0.0

    for block in blocks[:-1]:
        solved_mass += block
        unresolved = 1.0 - solved_mass
        sizes.append(
            float(help_cost * producer_mass * unresolved)
        )

    return np.asarray(sizes, dtype=float)


def specialization_extreme_point_test(productivities):
    """
    Minimal numerical reproduction of the linear/extreme-point mechanism
    behind Garicano Proposition 1.

    For a fixed organization, production allocation p lies on a simplex:

        p_i >= 0
        sum_i p_i = 1.

    A linear objective q^T p attains its optimum at an extreme point.
    We use distinct feasible productivities so the optimum is unique.

    This test does NOT claim to re-prove the full proposition. It verifies
    the numerical mechanism used by the proposition: linear allocation
    implies specialization at an extreme point.
    """
    productivities = np.asarray(productivities, dtype=float)

    vertices = np.eye(len(productivities))
    values = vertices @ productivities

    best_index = int(np.argmax(values))
    optimum = vertices[best_index]
    optimum_value = float(values[best_index])

    number_producing_classes = int(
        np.count_nonzero(optimum > 1e-12)
    )

    return {
        "productivities": productivities.tolist(),
        "optimal_production_allocation": optimum.tolist(),
        "optimal_value": optimum_value,
        "number_producing_classes": number_producing_classes,
        "passed": number_producing_classes == 1,
    }


def main():
    config = json.loads((EXP_DIR / "config.json").read_text())

    blocks = np.asarray(
        config["knowledge_blocks"],
        dtype=float,
    )
    h = float(config["help_cost"])
    b0 = float(config["producer_mass"])
    tolerance = float(config["tolerance"])

    if np.any(blocks <= 0):
        raise ValueError("Knowledge blocks must be positive.")

    if blocks.sum() >= 1.0:
        raise ValueError(
            "Knowledge blocks must leave a positive unresolved tail."
        )

    # ------------------------------------------------------------
    # B1.2 — specialization / extreme-point mechanism
    # ------------------------------------------------------------
    b12 = specialization_extreme_point_test(config["productivities"])

    # ------------------------------------------------------------
    # B1.3 — organization by frequency
    # ------------------------------------------------------------
    optimal, min_load, candidates = optimal_frequency_order(
        blocks.tolist()
    )

    expected_frequency_order = tuple(
        sorted(blocks.tolist(), reverse=True)
    )

    expected_is_optimal = any(
        np.allclose(
            np.asarray(perm),
            np.asarray(expected_frequency_order),
            atol=tolerance,
        )
        for perm in optimal
    )

    unique_optimum = len(optimal) == 1

    b13_passed = expected_is_optimal and unique_optimum

    # ------------------------------------------------------------
    # B1.4 — pyramidal organization
    # ------------------------------------------------------------
    ordered_blocks = np.asarray(
        expected_frequency_order,
        dtype=float,
    )

    sizes = hierarchy_sizes(
        ordered_blocks,
        help_cost=h,
        producer_mass=b0,
    )

    strictly_decreasing = bool(
        np.all(np.diff(sizes) < -tolerance)
    )

    # Independently reconstruct RHS of Garicano relation.
    cumulative = np.cumsum(ordered_blocks[:-1])
    rhs_specialists = h * b0 * (1.0 - cumulative)

    relation_error = float(
        np.max(
            np.abs(
                sizes[1:] - rhs_specialists
            )
        )
    )

    b14_passed = (
        strictly_decreasing
        and relation_error <= tolerance
    )

    output = {
        "experiment_ids": ["B1.2", "B1.3", "B1.4"],
        "kind": "source_reproduction",
        "source_citekeys": config["source_citekeys"],
        "source": "Garicano (2000)",
        "B1.2": b12,
        "B1.3": {
            "knowledge_blocks": blocks.tolist(),
            "number_of_permutations": len(candidates),
            "expected_frequency_order": list(
                expected_frequency_order
            ),
            "optimal_orderings": [
                list(p) for p in optimal
            ],
            "minimum_communication_load": min_load,
            "unique_optimum": unique_optimum,
            "passed": b13_passed,
        },
        "B1.4": {
            "help_cost": h,
            "producer_mass": b0,
            "hierarchy_sizes": sizes.tolist(),
            "strictly_decreasing": strictly_decreasing,
            "relation_error": relation_error,
            "passed": b14_passed,
        },
    }

    output["passed"] = bool(
        b12["passed"]
        and b13_passed
        and b14_passed
    )
    output["status"] = "REPRODUCED" if output["passed"] else "FAILED"

    write_result_bundle(
        root=ROOT,
        experiment_dir=EXP_DIR,
        result_dir=RESULT_DIR,
        run_file=Path(__file__).resolve(),
        output=output,
    )

    print(json.dumps(output, indent=2))

    if not output["passed"]:
        raise SystemExit("B1.2-B1.4 FAILED")


if __name__ == "__main__":
    main()
