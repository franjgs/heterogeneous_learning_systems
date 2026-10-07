"""Gate integrity and existing operator reuse; no additional closed-loop runs."""

import hashlib
import json

import pandas as pd
import pytest

from experiments.synthetic.strategy_discrimination_gate.run import (
    OUT, ROOT, MODE_BY_ID, action_l1, evaluate, pattern,
)
from hls.discover_v0 import EXACT_TOL


def test_frozen_factorial_and_all_materialized_counts():
    manifest=json.loads((OUT/"execution_manifest.json").read_text())
    runs=pd.read_csv(OUT/"closed_loop_runs.csv")
    steps=pd.read_csv(OUT/"closed_loop_trajectories.csv")
    decisions=pd.read_csv(OUT/"paired_state_decisions.csv")
    pairs=pd.read_csv(OUT/"paired_state_comparisons.csv")
    assert manifest["policy_ablation_commit"]=="3cf4eec"
    assert len(runs)==1280 and len(steps)==23040 and len(decisions)==23040 and len(pairs)==34560
    assert (runs.groupby(["scenario_id","configuration_id","policy"]).seed.agg(lambda s:set(s)==set(range(10)))).all()
    assert (runs.groupby("policy").size()==320).all()
    assert not runs.duplicated(["scenario_id","configuration_id","seed","policy"]).any()
    assert not pairs[pairs.terminal].exact_different.any()
    assert (steps.groupby(["seed","problem_index","within_problem_step"]).noise_innovation.nunique()==1).all()


def test_source_hashes_and_raw_output_hashes():
    manifest=json.loads((OUT/"execution_manifest.json").read_text())
    for path,digest in manifest["source_hashes"].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    for path,digest in manifest["output_hashes"].items():
        assert hashlib.sha256((OUT/path).read_bytes()).hexdigest()==digest


def test_q11_historical_regression_blocks_interpretation_on_failure():
    result=json.loads((OUT/"analysis_summary.json").read_text())
    checks=result["validation"]
    assert all(checks["Q11_historical_json_exact"].values())
    assert max(checks["Q11_historical_maximum_numeric_errors"].values())==0
    assert checks["real_state_transition_max_error"]==0
    assert checks["real_bayes_transition_max_error"]<=1e-12
    assert checks["terminal_divergences"]==0
    assert checks["frozen_descriptors_match"]


def test_counterfactual_reproduction_without_state_mutation():
    rows=pd.read_csv(OUT/"paired_state_decisions.csv").head(4)
    state=tuple(tuple(x) for x in json.loads(rows.iloc[0].state_before))
    belief=tuple(json.loads(rows.iloc[0].belief_before))
    original=(state,belief)
    for row in rows.itertuples():
        action,maximum,values=evaluate(state,belief,3-row.within_problem_step,row.policy)
        assert json.loads(row.action)==[list(x) for x in action]
        assert values[action]==pytest.approx(row.selected_objective,abs=1e-14)
        assert maximum==pytest.approx(row.maximum_objective,abs=1e-14)
    assert (state,belief)==original


def test_pairwise_artifact_uses_symmetric_tie_definition_and_exact_discrete_actions():
    pairs=pd.read_csv(OUT/"paired_state_comparisons.csv")
    mutual=(pairs.left_regret_of_right<=EXACT_TOL)&(pairs.right_regret_of_left<=EXACT_TOL)
    assert (pairs.mutual_tie_equivalent==mutual).all()
    assert (pairs.beyond_mutual_tie==(pairs.exact_different&~mutual)).all()
    assert ((pairs.action_l1>0)==pairs.exact_different).all()
    assert action_l1(((0,1),(.5,.5),(1,0)),((1,0),(.5,.5),(1,0)))==2


def test_pattern_taxonomy_is_exhaustive_for_all_equalities():
    from itertools import product
    for actions in product(range(4),repeat=4):
        result=pattern(dict(zip(MODE_BY_ID,actions)))
        assert result in {"ALL_SAME","INFORMATION_SENSITIVE","DEVELOPMENT_SENSITIVE",
            "BOTH_SINGLE_ABLATIONS_CHANGE","COUPLED_ONLY","OTHER_MIXED"}
    assert pattern(dict(zip(MODE_BY_ID,(0,0,0,1))))=="COUPLED_ONLY"
