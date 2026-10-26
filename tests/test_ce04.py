import json

import numpy as np
import pytest
import simpy

from hls.ce04 import (
    ALPHAS, RunConfig, Task, _Agent, _DelayedDisjointLinUCB,
    analyze_factorial, competency_matrix, deadline_probability_convolution,
    deadline_probability_two_moment, factorial_configs, generate_workload,
    paired_bootstrap, potential_correct, potential_service, run_replica,
    to_experiment_run, tost_equivalence, validate_probability_approximation,
)
from hls.experiment_contract import ExperimentRun


@pytest.mark.parametrize("n", [12, 24, 48])
def test_mean_preserving_competence_and_specialization(n):
    matrices = {h: competency_matrix(n, h, seed=9)[0] for h in ALPHAS}
    for matrix in matrices.values():
        assert np.all((matrix >= 0) & (matrix <= 1))
        assert matrix.mean(axis=0) == pytest.approx(np.full(4, 0.775), abs=1e-12)
    assert np.var(matrices["H0"], axis=0).max() == pytest.approx(0.0, abs=1e-28)
    assert np.var(matrices["H1"], axis=0).mean() < np.var(matrices["H2"], axis=0).mean()


def test_demand_is_continuous_correctly_partitioned_and_reproducible():
    first = generate_workload(11, 12)
    assert first == generate_workload(11, 12)
    assert all(0 <= t.arrival < 400 for t in first)
    assert all(t.deadline == pytest.approx(t.arrival + 3) for t in first)
    assert all(t.phase == (0 if t.arrival < 150 else 1 if t.arrival < 300 else 2) for t in first)
    assert all(a.arrival < b.arrival for a, b in zip(first, first[1:]))


def test_counterfactual_service_and_correctness_are_policy_independent():
    a = potential_service(5, 12, 3, 4)
    assert a == potential_service(5, 12, 3, 4)
    assert potential_correct(5, 12, 3, 4, .7) == potential_correct(5, 12, 3, 4, .7)
    assert a != potential_service(6, 12, 3, 4)


def test_two_moment_probability_agrees_near_admission_threshold():
    report = validate_probability_approximation(step=.001)
    assert report["near_threshold_cases"] >= 1
    assert report["max_near_threshold_error"] <= .01
    assert report["passes_tolerance"]
    assert deadline_probability_two_moment(.70, 1) == pytest.approx(.49568, abs=.001)
    assert deadline_probability_convolution(.70, 1, step=.001) == pytest.approx(.49182, abs=.001)


def test_log_normal_workload_probability_idle_and_invalid_queue():
    assert deadline_probability_two_moment(None, 0) == pytest.approx(.999123, abs=2e-6)
    with pytest.raises(ValueError):
        deadline_probability_two_moment(None, -1)


def test_linucb_delayed_feedback_allows_decisions_before_updates():
    policy = _DelayedDisjointLinUCB(3, alpha=1.0)
    contexts = [np.array([.8, 0, 0, 0.]), np.array([.8, 0, 0, 0.]), np.array([.8, 0, 0, 0.])]
    before = policy.model.design_matrices
    policy.scores(contexts)
    policy.scores(contexts)  # outstanding tasks do not block subsequent decisions
    assert policy.model.design_matrices == before
    policy.observe(1, contexts[1], 0)
    assert policy.model.design_matrices[1][0][0] > 1
    assert policy.model.response_vectors[1][0] == 0
    assert policy.model.design_matrices[0] == before[0]


def test_assignment_simulation_preserves_arrivals_and_capacity_and_drain():
    tasks = tuple(Task(i, .1 * i, i % 4, 0, .1 * i + 3) for i in range(15))
    result = run_replica(RunConfig(2, 12, "H1", "P0"), tasks)
    assert result["n_arrivals"] == len(tasks)
    assert result["task_ids"] == list(range(len(tasks)))
    rows = result["records"]
    assert len(rows) == len(tasks) and len({r["task_id"] for r in rows}) == len(tasks)
    accepted = [r for r in rows if r["selected_agent"] is not None]
    for agent in range(12):
        jobs = sorted((r for r in accepted if r["selected_agent"] == agent),
                      key=lambda x: x["service_start"])
        assert all(a["completion"] <= b["service_start"] + 1e-12
                   for a, b in zip(jobs, jobs[1:]))
        assert [r["task_id"] for r in jobs] == sorted(r["task_id"] for r in jobs)
    assert all(r["completion"] is not None for r in accepted)
    assert all(r["on_time"] == bool(r["correct"] and r["completion"] <= r["deadline"])
               for r in accepted)


def test_common_admission_does_not_depend_on_policy_or_competence_visibility():
    tasks = tuple(Task(i, .1 * i, i % 4, 0, .1 * i + 3) for i in range(20))
    results = [run_replica(RunConfig(3, 12, "H2", p), tasks) for p in ("P0", "P1", "P2", "P3")]
    # The same cut is used; assignment may change load and later feasible sets,
    # so the invariant is that every selected task crossed the shared cut.
    for result in results:
        assert all(r["f_selected"] >= .50 for r in result["records"] if r["selected_agent"] is not None)
        assert all(r["selected_agent"] is None for r in result["records"]
                   if r["rejection_reason"] is not None)


def test_p3_delayed_deadline_reward_is_not_revised_by_later_correctness(monkeypatch):
    task = (Task(0, 0.0, 0, 0, 3.0),)
    import hls.ce04 as ce04
    monkeypatch.setattr(ce04, "potential_service", lambda *_: 4.0)
    monkeypatch.setattr(ce04, "potential_correct", lambda *_: True)
    result = run_replica(RunConfig(19, 12, "H0", "P3"), task)
    late = [r for r in result["records"] if r["selected_agent"] is not None and r["completion"] > r["deadline"]]
    for record in late:
        assert record["reward_p3"] == 0
        assert record["p3_reward_observed_at"] == pytest.approx(record["deadline"])
        assert record["correct"] in (True, False)
        assert record["completion"] > record["p3_reward_observed_at"]


def test_replica_reproducibility_and_experimentrun_round_trip():
    tasks = tuple(Task(i, .2 * i, i % 4, 0, .2 * i + 3) for i in range(8))
    a = run_replica(RunConfig(4, 12, "H0", "P2"), tasks)
    b = run_replica(RunConfig(4, 12, "H0", "P2"), tasks)
    assert a["records"] == b["records"]
    run = to_experiment_run(a)
    restored = ExperimentRun.from_json(run.to_json())
    assert run.to_json() == restored.to_json()
    assert len(run.events) == len(tasks)


def test_design_sizes_bootstrap_and_holm_analysis():
    assert len(factorial_configs("pilot")) == 108
    assert len(factorial_configs("campaign")) == 1080
    summary = paired_bootstrap([.01, .02, -.01], n_resamples=1000)
    assert summary["n_replicates"] == 3
    assert len(summary["ci95"]) == 2
    assert tost_equivalence([.001, -.001, .002])["equivalent_at_0_05"]
    # Missing conditions fail closed rather than silently dropping contrasts.
    with pytest.raises(ValueError):
        analyze_factorial([])
