from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FOUNDATION = ROOT / "results" / "foundations" / "campaign3_c32_data"
GATE2 = ROOT / "results" / "diagnostics" / "campaign3_gate2"
SMOKE = ROOT / "results" / "diagnostics" / "campaign3_c32_data_smoke"


def module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


ALLOCATE = module("campaign3_c32_allocate", "experiments/synthetic/campaign3_c32_data/allocate.py")
TARGETS = module("campaign3_c32_targets", "experiments/synthetic/campaign3_c32_data/targets.py")
PILOT = module("campaign3_horizon_pilot_run", "experiments/synthetic/campaign3_horizon_pilot/run.py")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_gate2_factual_inputs_and_allocation_coverage() -> None:
    histories = pd.read_csv(GATE2 / "factual_histories.csv.gz")
    states = pd.read_csv(GATE2 / "factual_states.csv.gz")
    allocation = pd.read_csv(FOUNDATION / "history_clock_assignment.csv")
    assert len(histories) == 10_500 and len(states) == 378_000
    assert states.groupby("history_id").size().eq(36).all()
    assert len(allocation) == 10_500 and allocation.history_id.nunique() == 10_500
    assert set(allocation.history_id) == set(histories.history_id)
    assert allocation.partition.value_counts().to_dict() == {"TRAIN": 6300, "VALIDATION": 2100, "DEVELOPMENT_TEST": 2100}
    assert allocation.groupby("history_id").partition.nunique().eq(1).all()
    assert set(allocation.replicate).issubset({0, 1, 2, 3, 4})
    assert set(allocation.loc[allocation.partition == "TRAIN", "replicate"]) == {0, 1, 2}
    assert set(allocation.loc[allocation.partition == "VALIDATION", "replicate"]) == {3}
    assert set(allocation.loc[allocation.partition == "DEVELOPMENT_TEST", "replicate"]) == {4}


def test_clock_balance_determinism_and_selected_state_identity() -> None:
    allocation = pd.read_csv(FOUNDATION / "history_clock_assignment.csv")
    clocks = allocation.groupby(["partition", "selected_clock"]).size()
    assert clocks.loc["TRAIN"].eq(175).all()
    assert clocks.loc["VALIDATION"].isin((58, 59)).all()
    assert clocks.loc["DEVELOPMENT_TEST"].isin((58, 59)).all()
    assert set(allocation.selected_clock) == set(range(1, 37))
    expected = []
    for partition, frame in allocation.groupby("partition"):
        ordered = frame.assign(_rank=frame.history_id.map(ALLOCATE.rank)).sort_values(["_rank", "history_id"])
        expected.extend((history_id, index % 36 + 1) for index, history_id in enumerate(ordered.history_id))
    assert dict(expected) == dict(zip(allocation.history_id, allocation.selected_clock, strict=True))
    states = pd.read_csv(GATE2 / "factual_states.csv.gz", usecols=["history_id", "clock", "state_id", "K_X"])
    selected = allocation.merge(states, left_on=["history_id", "selected_clock"], right_on=["history_id", "clock"])
    assert len(selected) == 10_500
    assert (selected.selected_state_id == selected.state_id).all()
    assert selected.K_X.value_counts().sort_index().to_dict() == {1: 7771, 2: 2626, 3: 102, 4: 1}
    assert int((2 * selected.K_X).sum()) == 26666


def test_manifest_hashes_and_no_heldout_membership() -> None:
    manifest = json.loads((FOUNDATION / "allocation_manifest.json").read_text())
    allocation = FOUNDATION / "history_clock_assignment.csv"
    assert manifest["assignment_sha256"] == digest(allocation)
    assert manifest["gate2_input_sha256"]["factual_histories.csv.gz"] == digest(GATE2 / "factual_histories.csv.gz")
    assert manifest["gate2_input_sha256"]["factual_states.csv.gz"] == digest(GATE2 / "factual_states.csv.gz")
    split_t = pd.read_csv(ROOT / "results/foundations/campaign3_team_split/team_split.csv")
    split_k = pd.read_csv(ROOT / "results/foundations/campaign3_generator_split/kernel_split.csv")
    allocation_df = pd.read_csv(allocation)
    assert set(allocation_df.team_id) == set(split_t.loc[split_t.partition == "development", "team_id"])
    assert set(allocation_df.kernel_id) == set(split_k.loc[split_k.split_role == "development", "kernel_id"])
    diagnostic = json.loads((FOUNDATION / "clock_association_diagnostics.json").read_text())
    assert diagnostic["allocation_sha256"] == digest(allocation)
    assert diagnostic["partition_replicate_confounding"].startswith("intentional")


def test_conditional_generator_and_distinct_return_semantics() -> None:
    kernel = TARGETS.kernel_map()["K01"]
    prefix = TARGETS.realized_prefix(12345, kernel, 3)
    future_a = TARGETS.conditional_future(prefix, kernel, 67890)
    future_b = TARGETS.conditional_future(prefix, kernel, 67890)
    assert len(prefix) == 4 and len(future_a) == 11 and future_a == future_b
    assert tuple(TARGETS.conditional_future(prefix, kernel, 67891)) != future_a
    from hls.campaign3_problem_generator import eligible_returns
    assert eligible_returns((0.4, 0.2, 0.4, 0.4)) == (0.2,)


def test_arbitrary_state_rollout_matches_horizon_pilot_when_streams_match() -> None:
    task = PILOT.load_tasks()[0]
    problems, _, _, innovations = PILOT.generate_history(task)
    model, prior = PILOT.planner.canonical_model(PILOT.HYPOTHESIS_REPERTOIRE, PILOT.UNIFORM_PRIOR)
    state = task["team"]
    action = PILOT.select_action(state, prior, 3, "Q00")
    pilot_returns, _, _ = PILOT.rollout(state, prior, problems, innovations, start_problem=0, start_step=0, forced_action=action, continuation="Q00")
    value, actions, _, _ = TARGETS.rollout(state, prior, problems[0], tuple(problems[1:]), innovations, step=0, forced_action=action, continuation="Q00")
    assert np.isclose(value, pilot_returns[-1], atol=1e-12, rtol=0.0)
    assert len(actions) == 36


def test_rollout_resets_belief_and_persists_capability_at_problem_boundary(monkeypatch) -> None:
    task = TARGETS.tasks(1)[0]
    state = tuple(tuple(float(x) for x in row) for row in json.loads(task["state_before"]))
    belief = tuple(float(x) for x in json.loads(task["belief_before"]))
    prefix = TARGETS.realized_prefix(int(task["problem_seed"]), task["kernel"], int(task["problem_index"]) - 1)
    future = TARGETS.conditional_future(prefix, task["kernel"], 111)
    step = int(task["decision"]) - 1
    eps = tuple(float(x) for x in np.random.default_rng(222).standard_normal((3 - step) + 3 * TARGETS.ELL))
    action = TARGETS.select_action(state, belief, 3 - step, "Q00")
    calls = []
    original = TARGETS.theory._real_decision

    def recording(current_state, current_belief, *args, **kwargs):
        result = original(current_state, current_belief, *args, **kwargs)
        calls.append((current_state, current_belief, result.state_after))
        return result

    monkeypatch.setattr(TARGETS.theory, "_real_decision", recording)
    TARGETS.rollout(state, belief, prefix[-1], future, eps, step=step, forced_action=action, continuation="Q00")
    current_problem_calls = 3 - step
    assert calls[current_problem_calls][1] == tuple(TARGETS.UNIFORM_PRIOR)
    assert calls[current_problem_calls][0] == calls[current_problem_calls - 1][2]


def test_smoke_crn_dedup_advantages_and_reproducibility() -> None:
    values = pd.read_csv(SMOKE / "raw_mc_targets.csv.gz")
    manifest = json.loads((SMOKE / "execution_manifest.json").read_text())
    assert len(values) == 16 and values.groupby("selected_state_id").size().eq(8).all()
    assert values.groupby("selected_state_id").future_problem_sha256.nunique().eq(1).all()
    assert values.groupby("selected_state_id").noise_sha256.nunique().eq(1).all()
    assert (values.loc[values.initial_mode == "Q00", "advantage_vs_Q00"] == 0.0).all()
    expected_rollouts = int(sum(2 * frame.K_X.iloc[0] for _, frame in values.groupby("selected_state_id")))
    assert manifest["actual_rollouts"] == expected_rollouts
    assert manifest["targets_sha256"] == digest(SMOKE / "raw_mc_targets.csv.gz")
    first = TARGETS.tasks(1)[0]
    assert TARGETS.target_rows(first) == TARGETS.target_rows(first)


def test_epistemic_firewall_and_safe_artifacts() -> None:
    values = pd.read_csv(SMOKE / "raw_mc_targets.csv.gz", nrows=1)
    # These fields are privileged labels/metadata, not a model feature matrix.
    assert "raw_mc_G" in values and "advantage_vs_Q00" in values and "K_X" in values
    assert not (ROOT / "results" / "campaigns" / "campaign3_c32_data").exists()
    protocol = (ROOT / "docs/experiments/CAMPAIGN_3_C32_DATA.md").read_text()
    assert "S_t`, `b_t`, `tau_t" in protocol
    assert "Never expose as predictor inputs" in protocol
    assert "--partition" in protocol
