import numpy as np
import pytest

import hls.ce04 as ce04
from hls.ce04 import RunConfig, Task
from hls.ce04_validation import run_replica_traced, validate_admission_replay, validate_replica


def one_task_config(policy):
    return RunConfig(seed=31, n_agents=12, composition="H0", policy=policy, horizon=1.0)


def one_task():
    return (Task(task_id=0, arrival=0.0, family=0, phase=0, deadline=3.0),)


def fixed_outcomes(monkeypatch, duration, correct=True):
    monkeypatch.setattr(ce04, "potential_service", lambda *_: duration)
    monkeypatch.setattr(ce04, "potential_correct", lambda *_: correct)


def test_observable_reward_field_can_be_logged_without_any_policy_update(monkeypatch):
    fixed_outcomes(monkeypatch, duration=4.0, correct=True)
    config, tasks = one_task_config("P0"), one_task()
    result, trace = run_replica_traced(config, tasks)
    record = result["records"][0]

    assert record["p3_reward_observed_at"] == record["deadline"]
    assert record["reward_p3"] == 0
    assert trace.beta_updates == []
    assert trace.linucb_updates == []
    validate_replica(result, config, tasks, trace)


def test_p1_uses_true_competence_without_updating_estimators(monkeypatch):
    fixed_outcomes(monkeypatch, duration=.5, correct=True)
    config, tasks = one_task_config("P1"), one_task()
    result, trace = run_replica_traced(config, tasks)
    assert trace.beta_updates == []
    assert trace.linucb_updates == []
    assert result["records"][0]["p2_label_observed_at"] is None
    validate_replica(result, config, tasks, trace)


def test_common_admission_rule_is_replayed_from_decision_time_queue(monkeypatch):
    fixed_outcomes(monkeypatch, duration=.5, correct=True)
    result, _ = run_replica_traced(one_task_config("P0"), one_task())
    validate_admission_replay(result)

    result["records"][0]["f_selected"] = .49
    with pytest.raises(AssertionError, match="differs from common rule|threshold"):
        validate_admission_replay(result)


def test_validator_rejects_false_rejection_when_agent_is_admissible(monkeypatch):
    fixed_outcomes(monkeypatch, duration=.5, correct=True)
    result, _ = run_replica_traced(one_task_config("P0"), one_task())
    result["records"][0]["selected_agent"] = None
    with pytest.raises(AssertionError, match="rejected despite"):
        validate_admission_replay(result)


def test_p2_updates_only_beta_after_correctness_is_observed(monkeypatch):
    fixed_outcomes(monkeypatch, duration=.5, correct=True)
    config, tasks = one_task_config("P2"), one_task()
    result, trace = run_replica_traced(config, tasks)
    record = result["records"][0]

    assert len(trace.beta_updates) == 1
    assert trace.beta_updates[0]["kind"] == "beta_success"
    assert trace.beta_updates[0]["index"] == (record["selected_agent"], record["family"])
    assert trace.beta_updates[0]["time"] == record["completion"]
    assert trace.linucb_updates == []
    validate_replica(result, config, tasks, trace)


def test_p3_updates_only_linucb_from_its_observed_binary_reward(monkeypatch):
    fixed_outcomes(monkeypatch, duration=4.0, correct=True)
    config, tasks = one_task_config("P3"), one_task()
    result, trace = run_replica_traced(config, tasks)
    record = result["records"][0]

    assert trace.beta_updates == []
    assert len(trace.linucb_updates) == 1
    update = trace.linucb_updates[0]
    assert update["arm"] == record["selected_agent"]
    assert update["reward"] == 0
    assert update["time"] == record["deadline"]
    validate_replica(result, config, tasks, trace)


@pytest.mark.parametrize("policy,trace_field", [("P2", "beta_updates"), ("P3", "linucb_updates")])
def test_validator_rejects_update_before_corresponding_feedback(monkeypatch, policy, trace_field):
    fixed_outcomes(monkeypatch, duration=.5, correct=True)
    config, tasks = one_task_config(policy), one_task()
    result, trace = run_replica_traced(config, tasks)
    events = getattr(trace, trace_field)
    assert events
    events[0]["time"] -= .01

    with pytest.raises(AssertionError, match="updates differ|update does not match"):
        validate_replica(result, config, tasks, trace)
