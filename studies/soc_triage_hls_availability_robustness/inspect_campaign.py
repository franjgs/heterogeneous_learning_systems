"""Print compact descriptive views of the precomputed paired contrasts."""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

def read(path):
    with Path(path).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("results_dir",type=Path)
    d=p.parse_args().results_dir
    rows=read(d/"paired_calendar_contrasts.csv")
    groups=defaultdict(list)
    for r in rows: groups[(r["rho_L1"],r["alpha"])].append(r)
    print("Calendar delta S_plus (8x5 - 24x7), mean of matched subgroup contrasts")
    for k,rs in sorted(groups.items()):
        print(k, "mean",sum(float(x["S_plus_difference"]) for x in rs)/len(rs),
              "range",min(float(x["S_plus_difference"]) for x in rs),
              max(float(x["S_plus_difference"]) for x in rs), "n",len(rs))
    fs=read(d/"paired_factor_contrasts.csv")
    print("\nFactor contrast schema", list(fs[0]))
    for kind in sorted({r["contrast_type"] for r in fs}):
        rs=[r for r in fs if r["contrast_type"]==kind]
        print("\n",kind,"n",len(rs),"schema",{k:rs[0][k] for k in rs[0] if k not in {"contrast_type"}})
        for r in rs[:2]: print(r)
    summ=read(d/"summary_by_condition.csv")
    print("\nPrimary design summary: rho=.85, nL2=3")
    for r in summ:
        if r["rho_L1"]=="0.85" and r["n_L2"]=="3" and r["alpha"]=="0.25" and r["policy"]=="D1":
            print(r["classifier_id"].replace("standardized_", ""),r["calendar"],
                  "S+",r["S_plus_pooled"],"CI",r["S_plus_CI95_low"],r["S_plus_CI95_high"],
                  "L2wait",r["L2_wait_mean_h_mean"],"late",r["L2_late_fraction_mean"],
                  "FPwork",r["L2_FP_work_executed_mean"],"L2util",r["L2_utilization_available_H_mean"])
    print("\nPolicy contrasts rho=.85 alpha=.25 nL2=3")
    for r in fs:
        if r["contrast_type"]=="policy" and r["rho_L1"]=="0.85" and r["alpha"]=="0.25" and r["n_L2"]=="3":
            print(r["classifier_id"].replace("standardized_", ""),r["calendar"],r["contrast"],
                  r["estimate"],r["CI95_low"],r["CI95_high"])
    print("\nAlpha sensitivity rho=.85 nL2=3, selected policy D1")
    for r in fs:
        if r["contrast_type"]=="alpha_sensitivity" and r["rho_L1"]=="0.85" and r["n_L2"]=="3" and r["contrast"]=="alpha_0.25-minus-alpha_1.0":
            print(r["classifier_id"].replace("standardized_", ""),r["calendar"],r["estimate"],r["CI95_low"],r["CI95_high"])
if __name__=="__main__": main()
