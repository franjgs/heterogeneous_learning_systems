"""Audit the frozen one-dimensional routing--opportunity intervention."""

from dataclasses import asdict

import pytest

from hls.synthetic.rq0_opportunity_coupling import (
    BETA,
    EPSILON,
    ETA,
    INITIAL_COMPETENCE,
    KAPPA,
    LAMBDA_GRID,
    MEAN_OPPORTUNITY,
    TARGET_BY_TIME,
    TASK_SEQUENCE,
    TERMINAL_TASK,
    build_world,
    evaluate_lambda,
    executor_values,
    run_grid,
)


def _physical_signature(lambda_value: float):
    world = build_world(lambda_value)
    environment = world.environment
    return {
        "initial_state": environment.initial_state(),
        "competence_initial": environment.competence.initial,
        "reward": environment.reward,
        "development": environment.development,
        "eta": environment.development.eta,
        "kappa": environment.resources.kappa,
        "beta": environment.resources.beta,
        "resources": environment.initial_state().resources,
        "task_sequence": environment.tasks.tasks,
        "terminal_task": world.problem.terminal_task,
        "horizon": world.problem.horizon,
        "targets": environment.development.target_by_time,
        "opportunity_baseline": environment.opportunities.baseline,
        "opportunity_executor": environment.opportunities.executor_values,
    }


def test_grid_is_frozen_and_includes_endpoints() -> None:
    assert LAMBDA_GRID == tuple(index / 20.0 for index in range(21))
    assert (LAMBDA_GRID[0], LAMBDA_GRID[-1], len(LAMBDA_GRID)) == (0.0, 1.0, 21)


def test_only_rho_changes_between_family_members() -> None:
    low = _physical_signature(0.0)
    high = _physical_signature(1.0)
    assert low == high
    assert build_world(0.0).environment.opportunities.rho == 0.0
    assert build_world(1.0).environment.opportunities.rho == 1.0


def test_frozen_common_primitives_are_declared() -> None:
    world = build_world(0.5)
    assert world.environment.competence.initial == INITIAL_COMPETENCE
    assert world.environment.tasks.tasks == TASK_SEQUENCE
    assert world.problem.terminal_task == TERMINAL_TASK
    assert world.environment.development.target_by_time == TARGET_BY_TIME
    assert world.environment.development.eta == ETA
    assert world.environment.resources.kappa == KAPPA
    assert world.environment.resources.beta == BETA
    assert world.environment.initial_state().resources == ()


@pytest.mark.parametrize("lambda_value", LAMBDA_GRID)
def test_opportunity_formula_and_task_mean_are_exact(lambda_value: float) -> None:
    world = build_world(lambda_value)
    state = world.environment.initial_state()
    for task in (1, 2):
        p1 = world.environment.opportunities.probability(state, task, "M1", ())
        p2 = world.environment.opportunities.probability(state, task, "M2", ())
        expected_p1 = MEAN_OPPORTUNITY[task] - lambda_value * EPSILON[task] / 2.0
        expected_p2 = MEAN_OPPORTUNITY[task] + lambda_value * EPSILON[task] / 2.0
        assert p1 == pytest.approx(expected_p1, abs=1e-12)
        assert p2 == pytest.approx(expected_p2, abs=1e-12)
        assert (p1 + p2) / 2.0 == pytest.approx(MEAN_OPPORTUNITY[task], abs=1e-12)
        assert p2 - p1 == pytest.approx(lambda_value * EPSILON[task], abs=1e-12)


def test_executor_primitives_are_non_extreme_and_mean_preserving() -> None:
    values = executor_values()
    for task in (1, 2):
        assert values[("M1", task)] == pytest.approx(.25)
        assert values[("M2", task)] == pytest.approx(.75)
        assert 0.0 < values[("M1", task)] < 1.0
        assert 0.0 < values[("M2", task)] < 1.0
        assert (values[("M1", task)] + values[("M2", task)]) / 2.0 == pytest.approx(
            MEAN_OPPORTUNITY[task]
        )


def test_evaluation_uses_conservative_sep_quantity_and_reducibility_control() -> None:
    evaluation = evaluate_lambda(.5)
    assert evaluation.phi == pytest.approx(evaluation.j_hls - evaluation.j_sep_max, abs=1e-12)
    assert evaluation.j_sep_min <= evaluation.j_sep_max + 1e-12
    assert evaluation.j_hls == pytest.approx(evaluation.j_sep_omega, abs=1e-12)
    assert {node.state.time for node in evaluation.nodes} == {0, 1}


def test_grid_is_deterministic_and_has_one_result_per_lambda() -> None:
    first = run_grid()
    second = run_grid()
    assert tuple(item.lambda_value for item in first) == LAMBDA_GRID
    assert tuple(asdict(item) for item in first) == tuple(asdict(item) for item in second)


def test_regime_labels_follow_the_frozen_global_definition() -> None:
    for evaluation in run_grid():
        if evaluation.phi > 1e-12:
            assert evaluation.regime == "HLS_INTEGRATED"
            assert not evaluation.sep_admissible_hls_exists
        elif abs(evaluation.phi) <= 1e-12:
            assert evaluation.regime == "SEP_REDUCIBLE"
            assert evaluation.sep_admissible_hls_exists
        else:
            assert evaluation.regime == "REQUIRES_INVESTIGATION"
