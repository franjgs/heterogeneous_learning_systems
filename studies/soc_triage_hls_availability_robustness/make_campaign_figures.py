"""Create deterministic figures from merged paired campaign CSV results."""
from __future__ import annotations
import argparse, csv
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
DEFAULT=ROOT/"results"/"soc_triage_hls_availability_robustness"/"campaign"

def read_csv(path):
    with path.open(encoding="utf-8") as f: return list(csv.DictReader(f))

def main():
    p=argparse.ArgumentParser(); p.add_argument("--results-dir",type=Path,default=DEFAULT)
    args=p.parse_args(); d=args.results_dir if args.results_dir.is_absolute() else ROOT/args.results_dir
    out=d/"figures"; out.mkdir(parents=True,exist_ok=True)
    cal=read_csv(d/"paired_calendar_contrasts.csv")
    keep=[r for r in cal if float(r["n_L2"])==3 and float(r["alpha"])==1.0]
    classifiers=["LightGBM","LSEnsemble","Bayesian MLP"]
    ids={"LightGBM":"standardized_lightgbm_apc_symmetric",
         "LSEnsemble":"standardized_lsensemble_apc_symmetric",
         "Bayesian MLP":"standardized_bayesian_mlp_apc_symmetric"}
    fig,axes=plt.subplots(1,2,figsize=(12,5),sharey=True)
    colors={"D1":"#4467a5","P1":"#d27b32","WAPS":"#4b8b67"}
    for ax,rho in zip(axes,(0.85,1.25)):
        rows=[r for r in keep if float(r["rho_L1"])==rho]
        labels=[]; y=[]
        for ci,cl in enumerate(classifiers):
            for pi,policy in enumerate(("D1","P1","WAPS")):
                row=next(r for r in rows if r["classifier_id"]==ids[cl] and r["policy"]==policy)
                yy=ci*4+pi
                x=float(row["S_plus_difference"]); lo=float(row["CI95_low"]); hi=float(row["CI95_high"])
                ax.errorbar(x,yy,xerr=[[x-lo],[hi-x]],fmt="o",color=colors[policy],capsize=3)
                if pi==0: labels.append((yy,cl))
        ax.axvline(0,color="black",lw=.8,ls="--")
        ax.set_title(f"rho_L1 = {rho:g}"); ax.set_xlabel("S_plus difference (8x5 − 24x7)")
        ax.grid(axis="x",alpha=.2)
    axes[0].set_yticks([1,5,9],classifiers)
    fig.suptitle("Paired L2 calendar effect, alpha=1, n_L2=3 (95% seed-block bootstrap CI)")
    fig.tight_layout(); fig.savefig(out/"splus_calendar_contrasts.png",dpi=220,bbox_inches="tight"); plt.close(fig)

    factors=read_csv(d/"paired_factor_contrasts.csv")
    rows=[r for r in factors if r["contrast_type"]=="alpha_sensitivity" and
          r["calendar"]=="L2_8x5_Mon_Fri_09_17" and float(r["rho_L1"])==.85 and
          float(r["n_L2"])==3]
    fig,ax=plt.subplots(figsize=(10,6)); y=0
    for cl in classifiers:
        for policy in ("D1","P1","WAPS"):
            r=next(x for x in rows if x["classifier_id"]==ids[cl] and x["policy"]==policy)
            x=float(r["estimate"]); lo=float(r["CI95_low"]); hi=float(r["CI95_high"])
            ax.errorbar(x,y,xerr=[[x-lo],[hi-x]],fmt="o",color=colors[policy],capsize=3)
            y+=1
        y+=.5
    ax.axvline(0,color="black",lw=.8,ls="--"); ax.set_xlabel("S_plus difference (alpha=.25 − alpha=1)")
    ax.set_yticks([1,5,9],[f"{c}: D1 / P1 / WAPS" for c in classifiers])
    ax.set_title("FP service-cost sensitivity, 8x5, rho_L1=.85, n_L2=3")
    ax.grid(axis="x",alpha=.2); fig.tight_layout()
    fig.savefig(out/"splus_alpha_contrasts.png",dpi=220,bbox_inches="tight"); plt.close(fig)

if __name__=="__main__": main()
