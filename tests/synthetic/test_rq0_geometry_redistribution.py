"""Acceptance tests for the frozen T2 zero-sum geometry intervention."""

from dataclasses import asdict

import pytest

from hls.synthetic.rq0_geometry_redistribution import (
    ALPHA_GRID,
    BETA,
    ETA,
    KAPPA,
    LAMBDA,
    TARGET_BY_TIME,
    TASK_SEQUENCE,
    TERMINAL_TASK,
    build_world,
    competence_matrix,
    evaluate_alpha,
    run_grid,
)


def _signature(alpha: float):
    world = build_world(alpha)
    environment = world.environment
    return {
        "opportunity_baseline": environment.opportunities.baseline,
        "executor_values": environment.opportunities.executor_values,
        "rho": environment.opportunities.rho,
        "reward": environment.reward,
        "development": environment.development,
        "eta": environment.development.eta,
        "kappa": environment.resources.kappa,
        "beta": environment.resources.beta,
        "tasks": environment.tasks.tasks,
        "targets": environment.development.target_by_time,
        "resources": environment.initial_state().resources,
        "horizon": world.problem.horizon,
        "terminal_task": world.problem.terminal_task,
    }


def test_frozen_grid_and_anchor() -> None:
    assert ALPHA_GRID == tuple(index / 20.0 for index in range(21))
    assert competence_matrix(0.0) == ((.8, .8), (.6, .6))
    assert tuple(value for row in competence_matrix(1.0) for value in row) == pytest.approx(
        (.8, .6, .6, .8), abs=1e-12
    )


@pytest.mark.parametrize("alpha", ALPHA_GRID)
def test_geometry_preserves_declared_means_and_range(alpha: float) -> None:
    matrix = competence_matrix(alpha)
    values = [value for row in matrix for value in row]
    assert sum(values) / 4.0 == pytest.approx(.7, abs=1e-12)
    assert sum(row[0] for row in matrix) / 2.0 == pytest.approx(.7, abs=1e-12)
    assert sum(row[1] for row in matrix) / 2.0 == pytest.approx(.7, abs=1e-12)
    assert max(values) - min(values) == pytest.approx(.2, abs=1e-12)
    assert matrix[0][0] == pytest.approx(.8)
    assert matrix[1][0] == pytest.approx(.6)


def test_alpha_changes_only_competence_model() -> None:
    assert _signature(0.0) == _signature(1.0)
    assert build_world(0.0).environment.competence.initial != build_world(1.0).environment.competence.initial


@pytest.mark.parametrize("alpha", ALPHA_GRID)
def test_opportunity_primitives_are_frozen_and_not_derived_from_competence(alpha: float) -> None:
    world = build_world(alpha)
    kernel = world.environment.opportunities
    assert kernel.rho == LAMBDA == 1.0
    for task in (1, 2):
        assert kernel.baseline[task] == pytest.approx(.5)
        assert kernel.executor_values[("M1", task)] == pytest.approx(.25)
        assert kernel.executor_values[("M2", task)] == pytest.approx(.75)
        state = world.environment.initial_state()
        assert kernel.probability(state, task, "M1", ()) == pytest.approx(.25)
        assert kernel.probability(state, task, "M2", ()) == pytest.approx(.75)


def test_frozen_dynamic_semantics() -> None:
    world = build_world(.5)
    assert world.environment.tasks.tasks == TASK_SEQUENCE
    assert world.problem.terminal_task == TERMINAL_TASK
    assert world.environment.development.target_by_time == TARGET_BY_TIME
    assert world.environment.development.eta == ETA
    assert world.environment.resources.kappa == KAPPA
    assert world.environment.resources.beta == BETA
    assert world.environment.initial_state().resources == ()


@pytest.mark.parametrize("alpha", ALPHA_GRID)
def test_root_t1_identity_and_reducibility_control(alpha: float) -> None:
    evaluation = evaluate_alpha(alpha)
    root = next(node for node in evaluation.nodes if node.state.time == 0)
    assert root.task == 1
    assert root.rewards == {"M1": pytest.approx(.8), "M2": pytest.approx(.6)}
    assert root.opportunity_probabilities == {"M1": pytest.approx(.25), "M2": pytest.approx(.75)}
    assert evaluation.root_delta_r == pytest.approx(.2, abs=1e-12)
    assert evaluation.root_delta_p == pytest.approx(.5, abs=1e-12)
    assert evaluation.root_local_identity_residual == pytest.approx(0.0, abs=1e-12)
    assert evaluation.j_hls == pytest.approx(evaluation.j_sep_omega, abs=1e-12)


def test_structural_t2_tie_preserves_complete_greedy_set() -> None:
    evaluation = evaluate_alpha(.5)
    base_t2 = next(
        node for node in evaluation.nodes
        if node.state.time == 1 and node.state.competence == competence_matrix(.5)
    )
    assert base_t2.task == 2
    assert base_t2.greedy_actions == frozenset({"M1", "M2"})


def test_grid_is_deterministic_and_policy_labels_follow_global_rule() -> None:
    first = run_grid()
    second = run_grid()
    assert tuple(item.alpha for item in first) == ALPHA_GRID
    assert tuple(asdict(item) for item in first) == tuple(asdict(item) for item in second)
    for evaluation in first:
        if evaluation.phi > 1e-12:
            assert evaluation.regime == "HLS_INTEGRATED"
            assert not evaluation.sep_admissible_hls_exists
        elif abs(evaluation.phi) <= 1e-12:
            assert evaluation.regime == "SEP_REDUCIBLE"
            assert evaluation.sep_admissible_hls_exists
        else:
            assert evaluation.regime == "REQUIRES_INVESTIGATION"
