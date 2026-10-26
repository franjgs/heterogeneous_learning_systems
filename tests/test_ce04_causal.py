import numpy as np
import pytest

from hls import ce04
from hls.ce04_causal import (
    CONDITIONS, CONFIRMATORY_SEEDS, analyze_causal_campaign, calibration_outcomes,
    calibration_summary, configuration_hash, confirmatory_configuration,
    run_causal_replica,
)
from hls.ce04_validation import run_replica_traced
from hls.ce04 import RunConfig, Task, filter_admissible_by_load, filter_candidates_by_cutoff


def _tasks():
    early = tuple(Task(i, 0.1 * i, i % 4, 0, 0.1 * i + 3) for i in range(12))
    return early + (Task(12, 399.0, 0, 2, 402.0),)


def test_b00_is_behaviorally_identical_to_original_p2():
    tasks = _tasks()
    original = ce04.run_replica(RunConfig(20030, 12, "H2", "P2"), tasks)
    causal = run_causal_replica(20030, 12, "B00", tasks, "H2")
    assert causal["records"] == original["records"]
    for key in ("n_arrivals", "n_admitted", "n_rejected", "n_success_on_time",
                "success_on_time_rate", "service_time_total", "assignment_counts"):
        assert causal[key] == original[key]
    assert causal["calibration"] is None
    assert causal["calibration_cost_observations"] == 0


def test_load_cap_uses_only_common_admissible_set_and_has_fallback():
    chosen, cutoff, fallback = filter_admissible_by_load([0, 1, 2], [0, 10, 100, -1000])
    assert cutoff == pytest.approx(11.25)  # median of loads at indices 0,1,2 only
    assert chosen == [0, 1]
    assert fallback is False
    restored, fallback = filter_candidates_by_cutoff([0, 2], [1, 2, 3], -1)
    assert restored == [0, 2]
    assert fallback is True
    assert filter_admissible_by_load([], [0, 1]) == ([], None, False)


def test_load_is_expected_residual_plus_expected_queued_work():
    import simpy
    agent = ce04._Agent(simpy.Resource(simpy.Environment(), capacity=1), [3, 4], active_started=0.0)
    # At age zero the residual mean is exactly the original service mean.
    assert ce04.expected_pending_workload(agent, 0.0) == pytest.approx(3 * ce04.SERVICE_MEAN)
    idle = ce04._Agent(simpy.Resource(simpy.Environment(), capacity=1), [])
    assert ce04.expected_pending_workload(idle, 20.0) == 0


def test_calibration_is_20_per_cell_reproducible_and_rng_isolated():
    before = ce04.generate_workload(20031, 12)
    potential_before = [(ce04.potential_service(20031, 12, t.task_id, a),
                         ce04.potential_correct(20031, 12, t.task_id, a, .7))
                        for t in before[:8] for a in range(12)]
    a = calibration_outcomes(20031, 12, "H2")
    b = calibration_outcomes(20031, 12, "H2")
    assert a.shape == (12, 4, 20)
    assert np.array_equal(a, b)
    summary = calibration_summary(a)
    assert summary["n_observations"] == 960
    assert summary["successes"].shape == (12, 4)
    assert np.all(summary["successes"] + summary["failures"] == 20)
    assert before == ce04.generate_workload(20031, 12)
    potential_after = [(ce04.potential_service(20031, 12, t.task_id, agent),
                        ce04.potential_correct(20031, 12, t.task_id, agent, .7))
                       for t in before[:8] for agent in range(12)]
    assert potential_before == potential_after
    assert configuration_hash({"a": 1, "b": 2}) == configuration_hash({"b": 2, "a": 1})


def test_b10_b11_share_calibration_and_rng_draws_do_not_change_potential_outcomes():
    cal = calibration_outcomes(20032, 12, "H2")
    s1 = calibration_summary(cal)["sha256"]
    s2 = calibration_summary(calibration_outcomes(20032, 12, "H2"))["sha256"]
    assert s1 == s2
    tasks = _tasks()
    # Potential outcomes are keyed only by the frozen seed/N/task/agent tuple.
    for task in tasks:
        for agent in range(12):
            assert ce04.potential_service(20032, 12, task.task_id, agent) == \
                   ce04.potential_service(20032, 12, task.task_id, agent)
            assert ce04.potential_correct(20032, 12, task.task_id, agent, .7) == \
                   ce04.potential_correct(20032, 12, task.task_id, agent, .7)
    b10 = run_causal_replica(20032, 12, "B10", tasks, "H2", cal)
    b11 = run_causal_replica(20032, 12, "B11", tasks, "H2", cal)
    assert b10["calibration"]["sha256"] == b11["calibration"]["sha256"]
    assert b10["calibration_cost_observations"] == b11["calibration_cost_observations"] == 960
    assert all(row["selected_agent"] is None or row["f_selected"] >= .50 for row in b11["records"])


def test_calibrated_updates_still_wait_for_observed_completion(monkeypatch):
    monkeypatch.setattr(ce04, "potential_service", lambda *_: 4.0)
    monkeypatch.setattr(ce04, "potential_correct", lambda *_: True)
    cal = calibration_outcomes(20030, 12, "H2")
    config = RunConfig(20030, 12, "H2", "P2")
    result, trace = run_replica_traced(
        config, (Task(0, 399.0, 0, 2, 402.0),),
        p2_initial_successes=cal.sum(axis=2),
        p2_initial_failures=20 - cal.sum(axis=2),
    )
    rec = result["records"][0]
    assert rec["completion"] > rec["deadline"]
    assert trace.beta_updates[0]["time"] == rec["completion"]
    assert trace.beta_updates[0]["time"] > rec["arrival"]
    assert trace.linucb_updates == []


@pytest.mark.parametrize("condition", CONDITIONS)
def test_causal_condition_reproducibility(condition):
    tasks = _tasks()
    calibration = calibration_outcomes(20030, 12, "H2") if condition in ("B10", "B11") else None
    a = run_causal_replica(20030, 12, condition, tasks, "H2", calibration)
    b = run_causal_replica(20030, 12, condition, tasks, "H2", calibration)
    assert a["records"] == b["records"]
    assert a["success_on_time_rate"] == b["success_on_time_rate"]


def test_confirmatory_configuration_uses_authorized_seed_range_and_240_runs():
    config = confirmatory_configuration()
    assert CONFIRMATORY_SEEDS == tuple(range(20000, 20030))
    assert config["expected_replicas"] == 240
    assert config["frozen_design_sha256"] == "0f99dee0b7f1e81e4c768dcac977f9cafe0091b934c69467ce27097408d588c0"


def test_confirmatory_analysis_uses_paired_factorial_contrasts_only():
    rows = []
    for n in (12, 48):
        for seed in CONFIRMATORY_SEEDS:
            for condition, rate in (("B00", .50), ("B10", .52),
                                    ("B01", .49), ("B11", .54)):
                rows.append({"seed": seed, "n_agents": n, "condition": condition,
                             "success_on_time_rate": rate})
    result = analyze_causal_campaign(rows)
    at_12 = result["by_scale"]["12"]
    assert list(at_12) == ["delta_I_B10_minus_B00", "delta_C_B01_minus_B00", "delta_IC_interaction"]
    assert at_12["delta_I_B10_minus_B00"]["mean"] == pytest.approx(2.0)
    assert at_12["delta_C_B01_minus_B00"]["mean"] == pytest.approx(-1.0)
    assert at_12["delta_IC_interaction"]["mean"] == pytest.approx(3.0)
    assert all(row["bootstrap_resamples"] == 10000 for row in at_12.values())
    assert all(row["tost"]["margin"] == 2.0 for row in at_12.values())
