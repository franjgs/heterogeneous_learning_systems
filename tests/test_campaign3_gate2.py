from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "diagnostics" / "campaign3_gate2"


def load_run():
    path = ROOT / "experiments" / "synthetic" / "campaign3_gate2" / "run.py"
    spec = importlib.util.spec_from_file_location("campaign3_gate2_run", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_design_counts_membership_and_firewall() -> None:
    histories = pd.read_csv(OUT / "factual_histories.csv.gz")
    states = pd.read_csv(OUT / "factual_states.csv.gz")
    team_split = pd.read_csv(ROOT / "results/foundations/campaign3_team_split/team_split.csv")
    kernel_split = pd.read_csv(ROOT / "results/foundations/campaign3_generator_split/kernel_split.csv")
    dev_teams = set(team_split.loc[team_split.partition == "development", "team_id"])
    heldout_teams = set(team_split.loc[team_split.partition == "heldout", "team_id"])
    dev_kernels = set(kernel_split.loc[kernel_split.split_role == "development", "kernel_id"])
    heldout_kernels = set(kernel_split.loc[kernel_split.split_role == "heldout", "kernel_id"])
    assert len(histories) == 10_500 and len(states) == 378_000
    assert set(histories.team_id) == dev_teams and not (set(histories.team_id) & heldout_teams)
    assert set(histories.kernel_id) == dev_kernels and not (set(histories.kernel_id) & heldout_kernels)
    assert histories.behavior.value_counts().to_dict() == {b: 2100 for b in ("D00", "D10", "D01", "D11", "DbetaU")}
    assert set(histories.J) == {12} and set(histories.state_count) == {36}
    assert not histories.duplicated(["team_id", "kernel_id", "replicate", "behavior"]).any()


def test_fixed_modes_beta_reproducibility_and_crn() -> None:
    histories = pd.read_csv(OUT / "factual_histories.csv.gz")
    states = pd.read_csv(OUT / "factual_states.csv.gz")
    expected = {"D00": "Q00", "D10": "Q10", "D01": "Q01", "D11": "Q11"}
    for behavior, mode in expected.items():
        assert set(states.loc[states.behavior == behavior, "factual_mode"]) == {mode}
    beta = states[states.behavior == "DbetaU"]
    assert beta.factual_mode.value_counts().sort_index().to_dict() == {
        "Q00": 18772, "Q01": 19062, "Q10": 19006, "Q11": 18760,
    }
    grouped = histories.groupby(["team_id", "kernel_id", "replicate"])
    assert grouped.size().eq(5).all()
    for column in ("problem_seed", "noise_seed", "other_seed", "problem_stream_sha256", "noise_stream_sha256"):
        assert grouped[column].nunique().eq(1).all()
    assert grouped.beta_mode_seed.nunique().eq(1).all()
    assert histories.beta_mode_seed.nunique() == 2100


def test_action_diagnostics_are_complete_and_terminal_collapse_holds() -> None:
    states = pd.read_csv(OUT / "factual_states.csv.gz")
    action_columns = ["action_Q00", "action_Q10", "action_Q01", "action_Q11"]
    assert states[action_columns].notna().all().all()
    assert (states.K_X == states[action_columns].nunique(axis=1)).all()
    terminal = states[states.decision == 3]
    assert (terminal.K_X == 1).all()
    for behavior, frame in states.groupby("behavior"):
        if behavior != "DbetaU":
            mode = "Q" + behavior[1:]
            assert (frame.factual_action_id == frame[f"action_{mode}"]).all()
        else:
            selected = np.asarray([row[f"action_{row.factual_mode}"] for _, row in frame.iterrows()])
            assert np.array_equal(selected, frame.factual_action_id.to_numpy())


def test_state_continuity_and_clock_only_tau() -> None:
    states = pd.read_csv(OUT / "factual_states.csv.gz").sort_values(["history_id", "clock"])
    assert set(states.clock) == set(range(1, 37))
    assert (states.tau == 37 - states.clock).all()
    assert states.groupby("history_id").size().eq(36).all()
    previous = states.groupby("history_id").shift(1)
    within_problem = states.decision != 1
    assert (states.loc[within_problem, "state_before"].to_numpy() == previous.loc[within_problem, "state_after"].to_numpy()).all()
    assert (states.loc[within_problem, "belief_before"].to_numpy() == previous.loc[within_problem, "belief_after"].to_numpy()).all()


def test_diagnostic_call_does_not_mutate_and_real_update_matches() -> None:
    run = load_run()
    task = run.make_tasks()[0]
    problems, innovations = run.generate_exogenous(task)
    model, prior = run.planner.canonical_model(run.HYPOTHESIS_REPERTOIRE, run.UNIFORM_PRIOR)
    state, belief = task["team"], prior
    before_state, before_belief = tuple(map(tuple, state)), tuple(belief)
    actions = run.diagnostic_actions(state, belief, 3)
    assert state == before_state and belief == before_belief
    expected = run.theory._real_decision(state, belief, actions["Q00"], (problems[0], 1.0 - problems[0]), innovations[0], model)
    result = run.execute_history(task)["states"][0]
    assert np.allclose(json.loads(result["state_after"]), expected.state_after)
    assert np.allclose(json.loads(result["belief_after"]), expected.belief_after)


def test_selector_observable_and_no_target_or_training_artifacts() -> None:
    states = pd.read_csv(OUT / "factual_states.csv.gz", nrows=1)
    forbidden = {"p", "z", "C", "N", "M", "phi", "mu_true", "reward", "G", "Delta", "target"}
    assert not (forbidden & set(states.columns))
    manifest = json.loads((OUT / "execution_manifest.json").read_text())
    analysis = json.loads((OUT / "analysis_summary.json").read_text())
    classification = json.loads((OUT / "gate2_classification.json").read_text())
    assert manifest["selector_observable"] == ["S", "b", "tau"]
    assert manifest["counterfactual_value_targets"] == 0
    assert not manifest["heldout_execution"] and not manifest["predictor_or_metacontroller_training"]
    assert analysis["distances"]["combined"] is None
    assert classification["classification"] == "SUFFICIENT DEVELOPMENT DIVERSITY"
    assert not classification["c3_2_started"]


def test_persisted_and_analysis_hashes() -> None:
    raw = json.loads((OUT / "raw_completion.json").read_text())
    analysis = json.loads((OUT / "analysis_summary.json").read_text())
    assert raw["counts"] == {"histories": 10500, "states": 378000}
    for name, expected in raw["sha256"].items():
        assert sha256(OUT / name) == expected
    for name, expected in analysis["sha256"].items():
        assert sha256(OUT / name) == expected
