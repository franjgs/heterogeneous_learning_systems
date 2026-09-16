import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT
    / "experiments"
    / "foundations"
    / "b1_2_b1_4_garicano_organization"
    / "run.py"
)

spec = importlib.util.spec_from_file_location(
    "b1_2_b1_4",
    MODULE_PATH,
)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def test_b12_linear_allocation_specializes():
    productivities = [0.62, 0.71, 0.83, 0.68]
    result = g.specialization_extreme_point_test(productivities)

    assert result["passed"]
    assert result["number_producing_classes"] == 1
    assert result["optimal_production_allocation"] == [0.0, 0.0, 1.0, 0.0]
    assert result["optimal_value"] == max(productivities)


def test_b13_frequency_order_is_global_optimum():
    blocks = [0.30, 0.25, 0.20, 0.15]

    optimal, _, candidates = g.optimal_frequency_order(
        blocks
    )

    assert len(candidates) == 24
    assert len(optimal) == 1
    assert np.allclose(
        optimal[0],
        [0.30, 0.25, 0.20, 0.15],
    )


def test_b13_adverse_swap_increases_communication():
    ordered = [0.30, 0.25, 0.20, 0.15]
    adverse = [0.15, 0.25, 0.20, 0.30]

    assert (
        g.communication_load(ordered)
        < g.communication_load(adverse)
    )


def test_b14_hierarchy_is_pyramidal():
    blocks = [0.30, 0.25, 0.20, 0.15]

    sizes = g.hierarchy_sizes(
        blocks,
        help_cost=0.20,
        producer_mass=1.0,
    )

    assert np.all(np.diff(sizes) < 0.0)
    assert np.allclose(sizes, [1.0, 0.14, 0.09, 0.05])


def test_b14_garicano_size_relation():
    blocks = np.array(
        [0.30, 0.25, 0.20, 0.15]
    )

    h = 0.20
    b0 = 1.0

    sizes = g.hierarchy_sizes(
        blocks,
        help_cost=h,
        producer_mass=b0,
    )

    cumulative = np.cumsum(blocks[:-1])
    expected = h * b0 * (1.0 - cumulative)

    assert np.allclose(
        sizes[1:],
        expected,
        atol=1e-12,
    )
