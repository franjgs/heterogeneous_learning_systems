"""Read-only preflight: verifies frozen files and internal CSV consistency.

No simulation or sampling is performed. Run only on explicit user authorization.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
from .sampling import SOURCE_SHA, sha

RUN_SHA="3c2d7310a510deed03264b9a6df30ffc09a0af5915cc76dba233d29eadfd9e28"

def inspect(runs: Path, trajectories: Path, model: Path, calibration: Path):
    if sha(runs)!=RUN_SHA or sha(trajectories)!=SOURCE_SHA:
        raise ValueError("frozen confirmatory hashes mismatch")
    d=pd.read_csv(trajectories)
    r=pd.read_csv(runs)
    if len(d)!=249984 or len(r)!=6944:
        raise ValueError("unexpected confirmatory row count")
    if d.duplicated(["history_id","policy","clock"]).any():
        raise ValueError("duplicate decision key")
    if d.groupby(["history_id","policy"]).size().ne(36).any():
        raise ValueError("not 36 decisions per trajectory")
    m=json.loads(model.read_text()); c=json.loads(calibration.read_text())
    return {"runs_sha256":sha(runs),"trajectories_sha256":sha(trajectories),
            "ridge_sha256":sha(model),"calibration_sha256":sha(calibration),
            "n_histories":int(r.history_id.nunique()),"n_decisions":len(d),
            "ridge_top_level_keys":sorted(m),"calibration_top_level_keys":sorted(c)}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ("runs","trajectories","model","calibration"):
        p.add_argument("--"+arg,type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(inspect(a.runs,a.trajectories,a.model,a.calibration),indent=2))
