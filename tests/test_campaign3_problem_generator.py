"""Focused controls for the generator-only Campaign 3 PGCG path."""

import ast
import importlib.util
from pathlib import Path

import numpy as np
import pytest

from hls.campaign3_problem_generator import (
    eligible_returns,
    executable_compositions,
    generator_transition,
    move,
    nominal_kernels,
    reflect,
    select_scales,
    simplex_lattice_degree4,
)
from hls.problem_geometry import production_distance


def test_reflection_handles_boundaries_and_repeated_overshoots():
    values = np.array([0.2, 0.8, 0.1, 0.9, -0.5, 1.5])
    assert np.allclose(reflect(values), [0.2, 0.8, 0.3, 0.7, 0.7, 0.3])
    assert np.all((reflect(np.linspace(-5, 5, 101)) >= 0.2) & (reflect(np.linspace(-5, 5, 101)) <= 0.8))


def test_move_and_distance_use_frozen_definitions():
    moved, reflected = move(np.array([0.8]), 0.1, np.array([1.0]))
    assert moved[0] == pytest.approx(0.7)
    assert reflected[0]
    assert production_distance(0.8, 0.7) == pytest.approx(0.15)


def test_scale_selection_is_deterministic_with_lexicographic_ties():
    sigmas = (0.01, 0.02, 0.04, 0.08)
    medians = (1.0, 2.0, 4.0, 8.0)
    assert select_scales(sigmas, medians) == (0, 1, 2)


def test_simplex_and_operational_kernel_counts():
    lattice = simplex_lattice_degree4()
    assert len(lattice) == 15
    assert (0.0, 0.0, 1.0) in lattice
    assert len(executable_compositions()) == 14
    kernels = nominal_kernels((0.01, 0.08, 0.32))
    assert len(kernels) == len(set(kernels)) == 34
    assert sum(kernel[-1] is None for kernel in kernels) == 4


def test_return_is_uniform_over_distinct_prior_values_not_occurrences():
    assert eligible_returns((0.2, 0.4, 0.4, 0.8)) == (0.2, 0.4)
    rng = np.random.default_rng(7)
    draws = [generator_transition((0.2, 0.4, 0.4, 0.8), (0, 0, 1, None), rng).p_next for _ in range(4000)]
    assert set(draws) == {0.2, 0.4}
    assert abs(draws.count(0.2) / len(draws) - 0.5) < 0.04


def test_return_never_selects_current_and_only_selects_strict_history():
    rng = np.random.default_rng(11)
    history = (0.2, 0.5, 0.8, 0.5)
    for _ in range(100):
        transition = generator_transition(history, (0, 0, 1, None), rng)
        assert transition.p_next in {0.2, 0.8}
        assert transition.p_next != history[-1]


def test_return_unavailable_renormalizes_stay_and_move():
    rng = np.random.default_rng(3)
    for _ in range(100):
        transition = generator_transition((0.5,), (0.25, 0.25, 0.5, 0.08), rng)
        assert transition.mechanism in {"STAY", "MOVE"}
        assert transition.return_unavailable and transition.renormalized
    with pytest.raises(ValueError):
        generator_transition((0.5,), (0, 0, 1, None), rng)


def test_pgcg_module_has_no_forbidden_agent_or_performance_imports():
    path = Path(__file__).parents[1] / "src" / "hls" / "campaign3_problem_generator.py"
    tree = ast.parse(path.read_text())
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    forbidden = {"finite_problem_belief", "discover_v0", "discover_develop_v2", "campaign2_theory"}
    assert not any(any(part in imported for part in forbidden) for imported in imports)


def test_fixed_seed_calibration_selects_frozen_scales_deterministically():
    path = Path(__file__).parents[1] / "experiments" / "synthetic" / "campaign3_pgcg" / "run.py"
    spec = importlib.util.spec_from_file_location("campaign3_pgcg_run", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    first = module.calibrate()
    second = module.calibrate()
    assert first[2] == second[2] == (0.01, 0.04, 0.32)
    assert first[0] == second[0]
    assert first[3]["median_order_all_candidates"]
    assert first[3]["quantile_order_all_candidates"]
    assert first[3]["empirical_distribution_order_all_adjacent_candidates"]


def test_generated_pgcg_artifacts_have_frozen_shapes_and_no_performance_fields():
    root = Path(__file__).parents[1]
    out = root / "results" / "foundations" / "campaign3_pgcg"
    raw = np.load(out / "raw_generator_histories.npz")
    assert raw["histories"].shape == (34, 10_000, 12)
    assert raw["mechanisms"].shape == raw["flags"].shape == (34, 10_000, 11)
    assert set(raw.files) == {"histories", "mechanisms", "flags"}
    runner = (root / "experiments" / "synthetic" / "campaign3_pgcg" / "run.py").read_text()
    for forbidden in ("finite_problem_belief", "discover_develop_v2", "mu_true", "reward", "Q00", "Q11"):
        assert forbidden not in runner
