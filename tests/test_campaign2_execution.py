"""C2 infrastructure and artifact integrity; no extra scientific runs."""
import json
from pathlib import Path
import numpy as np
import pytest

from experiments.synthetic.campaign2_prospective_adaptation import run


def test_streaming_csv_persistence(tmp_path):
    # Pure serialization check: no HLS state, policy call, seed or simulation.
    import csv,gzip,io
    from contextlib import ExitStack
    paths=[tmp_path/"plain.csv",tmp_path/"compressed.csv.gz"]
    with ExitStack() as stack:
        writers={}
        for path in paths:
            raw=stack.enter_context(path.open("wb"))
            stream=stack.enter_context(gzip.GzipFile(fileobj=raw,mode="wb",mtime=0)) if path.suffix==".gz" else raw
            handle=stack.enter_context(io.TextIOWrapper(stream,encoding="utf-8",newline=""))
            writers[path]=(handle,None)
        for path,rows in ((paths[0],[{"a":1}]),(paths[1],[{"a":2}])):
            stream,writer=writers[path]
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator="\n")
            writer.writeheader();writer.writerows(rows)
    assert paths[0].read_text()=="a\n1\n"
    with gzip.open(paths[1],"rt") as f:
        assert f.read()=="a\n2\n"


def _synthetic_table_task(n):
    return {"table":[{"n":n}]}


def _synthetic_full_tables_task(task):
    return {name:[{"value":2*task[0]},{"value":2*task[0]+1}] for name in run.FILENAMES}


def test_replaced_public_inodes_reproduce_failure_and_private_staging_fixes_it(tmp_path):
    import csv,io,os,tempfile
    from contextlib import ExitStack
    from experiments.synthetic.campaign2_prospective_adaptation.artifact_io import persist_tables
    old=tmp_path/"legacy";old.mkdir()
    filenames={"one":"one.csv","two":"two.csv"}
    def replace_public_files(directory):
        for filename in filenames.values():
            with tempfile.NamedTemporaryFile(dir=directory,delete=False) as f:
                replacement=Path(f.name)
            os.replace(replacement,directory/filename)
    with ExitStack() as stack:
        handles={name:stack.enter_context(io.TextIOWrapper(stack.enter_context((old/file).open("wb")),encoding="utf-8"))
                 for name,file in filenames.items()}
        before={name:(old/file).stat().st_ino for name,file in filenames.items()}
        replace_public_files(old)
        assert all((old/file).stat().st_ino!=before[name] for name,file in filenames.items())
        for handle in handles.values():
            writer=csv.DictWriter(handle,fieldnames=["value"])
            writer.writeheader();writer.writerows([{"value":1}])
    assert all((old/file).stat().st_size==0 for file in filenames.values())
    fresh=tmp_path/"fixed";fresh.mkdir()
    def batches():
        replace_public_files(fresh)  # Same external replacement during computation.
        yield {name:[{"value":1}] for name in filenames}
    counts,metadata=persist_tables(batches(),fresh,filenames)
    assert counts=={"one":1,"two":1}
    assert all(v["rows"]==1 and v["bytes"]>0 for v in metadata.values())
    assert all((fresh/file).read_text()=="value\n1\n" for file in filenames.values())


def test_post_publication_corruption_blocks_success(tmp_path,monkeypatch):
    from experiments.synthetic.campaign2_prospective_adaptation import artifact_io
    original=artifact_io.os.replace
    def corrupted(source,dest):
        original(source,dest)
        Path(dest).write_bytes(b"")
    monkeypatch.setattr(artifact_io.os,"replace",corrupted)
    with pytest.raises(IOError,match="empty artifact"):
        artifact_io.persist_tables(iter([{"one":[{"value":1}]}]),tmp_path,{"one":"one.csv"})


def test_actual_main_process_pool_roundtrip(tmp_path,monkeypatch):
    import csv,gzip
    from concurrent.futures import ProcessPoolExecutor
    from experiments.synthetic.campaign2_prospective_adaptation.artifact_io import persist_tables
    destination=tmp_path/"synthetic-process-output"
    with ProcessPoolExecutor(max_workers=2) as pool:
        counts,metadata=persist_tables(pool.map(_synthetic_full_tables_task,[(i,) for i in range(1280)]),destination,run.FILENAMES)
    assert all(n==2560 for n in counts.values())
    for filename in run.FILENAMES.values():
        path=destination/filename
        assert path.stat().st_size>0
        opener=gzip.open if filename.endswith(".gz") else open
        with opener(path,"rt",newline="") as f:
            assert [int(row["value"]) for row in csv.DictReader(f)]==list(range(2560))


def test_actual_main_synthetic_tables_roundtrip(tmp_path,monkeypatch):
    """Exercise all seven output streams without HLS state or simulation calls."""
    import csv,gzip
    class SyntheticPool:
        def __init__(self,**kwargs): pass
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def map(self,*args,**kwargs):
            for n in range(3):
                yield {name:[{"value":2*n},{"value":2*n+1}] for name in run.FILENAMES}
    from experiments.synthetic.campaign2_prospective_adaptation.artifact_io import persist_tables
    destination=tmp_path/"synthetic-output"
    counts,metadata=persist_tables(SyntheticPool().map(),destination,run.FILENAMES)
    assert all(n==6 for n in counts.values())
    for filename in run.FILENAMES.values():
        path=destination/filename
        assert path.stat().st_size>0
        opener=gzip.open if filename.endswith(".gz") else open
        with opener(path,"rt",newline="") as f:
            assert [int(row["value"]) for row in csv.DictReader(f)]==list(range(6))


def test_closed_loop_generator_unchanged_except_counterfactual_deferral():
    import ast
    old=ast.parse((run.INCIDENT/"failed_attempt_01_runner.py.txt").read_text())
    new=ast.parse(Path(run.__file__).read_text())
    original=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=="task_data")
    current=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=="task_data")
    class DeferOnly(ast.NodeTransformer):
        def visit_Tuple(self,node):
            self.generic_visit(node)
            if any(isinstance(e,ast.Constant) and e.value=="branches" for e in node.elts):
                node.elts=[e for e in node.elts if not (isinstance(e,ast.Constant) and e.value in ("branches","counterfactuals"))]
            return node
        def visit_For(self,node):
            if isinstance(node.target,ast.Name) and node.target.id=="p" and isinstance(node.iter,ast.Tuple):
                if [e.value for e in node.iter.elts if isinstance(e,ast.Constant)]==["Q10","Q01","Q11"]:
                    return None
            return self.generic_visit(node)
    expected=DeferOnly().visit(original)
    assert ast.dump(expected)==ast.dump(current)


def test_failed_attempt_evidence_and_analysis_sources_unchanged():
    evidence=json.loads((run.INCIDENT/"io_forensic_evidence.json").read_text())
    assert run.digest(run.INCIDENT/"validation_failure.json")==evidence["incident_sha256"]
    assert run.digest(run.INCIDENT/"failed_attempt_01_runner.py.txt")==evidence["failed_runner_sha256"]
    for filename,expected in evidence["analysis_sources_sha256"].items():
        assert run.digest(Path(run.__file__).parent/filename)==expected


def test_count_gate_blocks_counterfactuals_on_bad_persisted_counts(tmp_path):
    with pytest.raises(IOError,match="count failure"):
        run.verify_persisted_closed_counts(tmp_path,{"runs":0})


def test_deferred_counterfactual_exactly_reuses_frozen_primitive():
    s=((.2,.8),(.5,.3),(.9,.4));b=(.2,.3,.5);z=(.7,.3);eps=(.123456789,-.25)
    actions={p:run.first(run.values(s,b,2,p)) for p in run.MODE_BY_ID}
    row=dict(state_id="1",remaining="2",S=run.packed(s),b=run.packed(b),
             true_theta=run.packed(z),epsilon0=repr(eps[0]),epsilon1=repr(eps[1]),
             **{p:str(run.ACTION_IDS[x]) for p,x in actions.items()})
    records=run.counterfactual_task([row])
    assert len(records["counterfactuals"])==3 and len(records["branches"])==12
    for p in ("Q10","Q01","Q11"):
        direct=run.theory.two_decision_counterfactual(s,b,z,remaining=2,
            policy_mode=run.MODE_BY_ID[p],innovations=eps)
        stored=next(r for r in records["counterfactuals"] if r["policy"]==p)
        assert stored["DeltaG"]==direct.delta_production
        for name,branch in (("prospective",direct.prospective),("baseline",direct.baseline)):
            for n,step in enumerate(branch.steps):
                saved=next(r for r in records["branches"] if r["policy"]==p and r["branch"]==name and r["branch_step"]==n)
                assert saved["observation"]==step.observation and saved["mu_true"]==step.mu_true
                assert saved["S_after"]==run.packed(step.state_after)
                assert saved["b_after"]==run.packed(step.belief_after)


def test_process_pool_csv_persistence_on_repository_volume():
    # Synthetic serialization on the same volume as the failed Campaign output.
    import csv,io,tempfile
    from contextlib import ExitStack
    from concurrent.futures import ProcessPoolExecutor
    with tempfile.TemporaryDirectory(prefix="c2-io-test-",dir=run.ROOT/".pytest_cache") as directory:
        path=Path(directory)/"synthetic.csv"
        with ExitStack() as stack:
            raw=stack.enter_context(path.open("wb"))
            handle=stack.enter_context(io.TextIOWrapper(raw,encoding="utf-8",newline=""))
            writer=None
            with ProcessPoolExecutor(max_workers=2) as pool:
                for data in pool.map(_synthetic_table_task,range(3)):
                    rows=data["table"]
                    if writer is None:
                        writer=csv.DictWriter(handle,fieldnames=list(rows[0]),lineterminator="\n")
                        writer.writeheader()
                    writer.writerows(rows)
        assert path.read_text()=="n\n0\n1\n2\n"


def test_design_inherited():
    p = run.preflight()
    assert list(run.CONFIG_BY_ID) == p["design"]["configuration_ids"]
    assert list(run.HISTORIES) == p["design"]["scenario_ids"]
    assert list(run.SEEDS) == p["confirmatory_seeds"] == list(range(10,50))
    assert len(run.CONFIG_BY_ID)*len(run.HISTORIES)*len(run.SEEDS)*len(run.MODE_BY_ID)==5120


@pytest.mark.parametrize("remaining", (1,2,3))
@pytest.mark.parametrize("pid", run.MODE_BY_ID)
def test_exact_cache_preserves_all_candidates_and_actions(remaining, pid):
    s = ((.2,.8),(.5,.3),(.9,.4)); b=(.2,.3,.5)
    before = run.values(s,b,remaining,pid)
    with run.exact_cache():
        after = run.values(s,b,remaining,pid)
        assert after == before
        assert run.first(after) == run.first(before)
        after.clear()
        assert run.values(s,b,remaining,pid) == before


def test_counterfactual_original_state_and_null():
    s=((1.,1.),(1.,1.),(1.,1.)); b=(1.,0.,0.)
    with run.exact_cache():
        for mode in tuple(run.MODE_BY_ID.values())[1:]:
            cf=run.theory.two_decision_counterfactual(s,b,(.8,.2),remaining=2,
                policy_mode=mode,innovations=(.125,-.25))
            assert cf.delta_production==0 and cf.prospective==cf.baseline
    assert s==((1.,1.),)*3 and b==(1.,0.,0.)


def test_completed_artifacts():
    path=run.OUT/"validation_summary.json"
    if not path.exists():
        pytest.skip("full preregistered execution not yet complete")
    summary=json.loads(path.read_text())
    assert summary["passed"]
    assert summary["counts"]["runs"]==5120
    assert summary["counts"]["reference_states"]==23040
    assert summary["eligible_reference_states"]==15360
    assert summary["max_null_return_error"]==0
    assert summary["terminal_divergences"]==0
    for name, expected in summary["raw_sha256"].items():
        assert run.digest(run.OUT/name)==expected


def test_bootstrap_cluster_repetition_not_state_resampling():
    from experiments.synthetic.campaign2_prospective_adaptation.analyze import weights_for, weighted_mean
    # A: one event with sum1; B: three events with sum9. Repeated A gives 11/5.
    weights=weights_for(np.array([0,0,1]))
    clusters=np.array([0,1,1,1])
    assert weighted_mean(np.array([1.,3.,3.,3.]),weights[clusters])==2.2


def test_bootstrap_deterministic_whole_seed_draws():
    from experiments.synthetic.campaign2_prospective_adaptation.analyze import bootstrap_indices
    a,b=bootstrap_indices(),bootstrap_indices()
    assert a.shape==(10000,40) and np.array_equal(a,b)
    assert a.min()==0 and a.max()==39


@pytest.mark.parametrize("x,w", [([1.,4.],[2,1]),([1.,4.],[1,1]),([1.,4.,8.],[2,0,3])])
def test_weighted_median_matches_literal_cluster_copies(x,w):
    from experiments.synthetic.campaign2_prospective_adaptation.analyze import weighted_median
    assert weighted_median(np.array(x),np.array(w))==np.median(np.repeat(x,w))


def test_undefined_estimands_remain_explicit():
    from experiments.synthetic.campaign2_prospective_adaptation.analyze import interval,ols_from_clusters
    out=interval("toy",np.nan,np.array([np.nan,np.nan]))
    assert out["estimate"] is None and out["lower"] is None and out["undefined_resamples"]==2
    blocks=[(np.ones((2,4)),np.ones(2))]*40
    assert np.isnan(ols_from_clusters(blocks,np.arange(40))).all()


def test_analysis_registry_and_integrity_after_execution():
    path=run.OUT/"analysis_summary.json"
    if not path.exists():
        pytest.skip("analysis not yet complete")
    a=json.loads(path.read_text())
    assert a["bootstrap"]["replicates"]==10000
    assert a["primary_reference"]=="Q11 only"
    # Inherited constant-addition tie-boundary caveat is recorded, not repaired.
    assert a["immediate_myopic_vs_Q00_action_mismatches"]>=0
    for p in ("Q10","Q01","Q11"):
        assert a["estimates"][p+"_p_plus"]["status"]=="confirmatory"
        assert a["estimates"][p+"_OLS_M"]["status"]=="secondary confirmatory"
    assert "logistic regression (not frozen in final preregistration)" in a["registry"]["not_run"]
