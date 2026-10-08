import json
from pathlib import Path

import numpy as np
import pandas as pd

from experiments.synthetic.campaign2_state_coverage_audit import run


def synthetic_states(offset=0.0):
    rows=[]
    for seed in range(10,50):
        for policy in run.POLICIES:
            x=(seed-10)/100.0 + (offset if policy=="Q00" else 0.0)
            row=dict(scenario="S",configuration="G",seed=seed,problem_index=0,
                decision=0,policy=policy,owner_differs_from_q11=int(policy=="Q00"))
            row.update({feature:x for feature in run.CORE})
            rows.append(row)
    return pd.DataFrame(rows)


def test_support_excludes_same_seed_and_self_calibrates():
    support=pd.DataFrame(run.support_rows(synthetic_states()))
    assert (support.nearest_q11_seed!=support.seed).all()
    assert support[support.policy=="Q11"].covered_by_q11_spacing.all()
    assert support.covered_by_q11_spacing.all()


def test_shifted_target_detects_uncovered_support():
    support=pd.DataFrame(run.support_rows(synthetic_states(offset=2.0)))
    q00=support[support.policy=="Q00"]
    assert not q00.covered_by_q11_spacing.any()
    assert not q00.inside_q11_coordinate_envelope.any()
    assert (q00.outside_coordinate_count==len(run.CORE)).all()


def test_ks_and_wasserstein_known_values():
    assert run.ks_distance([0,0],[1,1])==1.0
    rows=run.marginal_rows(pd.DataFrame([
        dict(policy=p,scenario="S",configuration="G",problem_index=0,decision=0,
             represented=True,**{k:0.0 for k in run.FEATURE_SCALES})
        for p in run.POLICIES]))
    assert all(r.get("normalized_w1") in (0.0,None) for r in rows)
    assert all(r.get("categorical_total_variation",0.0)==0.0 for r in rows)


def test_frozen_inputs_and_completed_artifacts():
    validation=json.loads((run.INPUT/"validation_summary.json").read_text())
    assert validation["passed"] and validation["counts"]["trajectories"]==92160
    if not run.OUT.exists():
        return
    summary=json.loads((run.OUT/"audit_summary.json").read_text())
    manifest=json.loads((run.OUT/"execution_manifest.json").read_text())
    assert manifest["no_new_experiments"] and manifest["counts"]["states"]==61440
    assert summary["non_q11_states"]==46080
    assert (run.OUT/"provenance.json").exists()
    for name,meta in manifest["persisted_file_metadata"].items():
        path=run.OUT/run.FILES[name]
        assert path.stat().st_size==meta["bytes"] and run.digest(path)==meta["sha256"]
    provenance=json.loads((run.OUT/"provenance.json").read_text())
    for name,expected in provenance["output_sha256"].items():
        assert run.digest(run.OUT/name)==expected
    closure=json.loads((run.ROOT/"results/campaigns/campaign2_prospective_adaptation/closure_provenance.json").read_text())
    for relative,expected in closure["sha256"].items():
        path=(run.ROOT/relative) if relative.startswith(("docs/","results/")) else run.INPUT.parent/relative
        assert run.digest(path)==expected
