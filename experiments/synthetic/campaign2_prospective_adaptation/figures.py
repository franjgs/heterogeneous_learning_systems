"""Fixed primary-summary figures, derived entirely from retained tables."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from . import run


def main():
    summary=json.loads((run.OUT/"analysis_summary.json").read_text())
    estimates=summary["estimates"]
    plt.rcParams.update({"svg.hashsalt":"campaign2-preregistered","font.size":10})
    fig,axes=plt.subplots(1,3,figsize=(11,3.3))
    for ax,prefix,title in ((axes[0],"H1_regret","Hypothesis-conditioned myopic regret"),
                             (axes[1],"H2_headroom","Capability headroom")):
        for i in (0,1):
            e=estimates[f"{prefix}_mean_D{i}"]
            if e["estimate"] is not None:
                ax.errorbar(i,e["estimate"],yerr=[[e["estimate"]-e["lower"]],[e["upper"]-e["estimate"]]],fmt="o",capsize=3)
        ax.set_xticks([0,1],["same action","divergent"]); ax.set_title(title)
        ax.set_xlabel("Q10 vs Q00" if prefix=="H1_regret" else "Q01 vs Q00")
    names=["D_10_prevalence","D_01_prevalence","D_11_prevalence","D_coupled_prevalence"]
    for i,name in enumerate(names):
        e=estimates[name]
        axes[2].errorbar(i,e["estimate"],yerr=[[e["estimate"]-e["lower"]],[e["upper"]-e["estimate"]]],fmt="o",capsize=3)
    axes[2].set_xticks(range(4),["Q10","Q01","Q11","coupled"])
    axes[2].set_ylabel("Prevalence");axes[2].set_title("Exact selected-action divergence")
    fig.suptitle("Campaign 2: Q11-reference states; whole-seed 95% intervals")
    fig.tight_layout();fig.savefig(run.OUT/"decision_structure.svg",metadata={"Date":None});plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(8,3.5))
    labels=["Q10","Q01","Q11"]; bottom=np.zeros(3)
    for suffix,label,color in (("p_plus","positive","#2a9d8f"),("p_zero","zero","#bdbdbd"),("p_negative","negative","#e76f51")):
        vals=np.array([estimates[p+"_"+suffix]["estimate"]
                       if estimates[p+"_"+suffix]["estimate"] is not None else np.nan for p in labels])
        axes[0].bar(labels,vals,bottom=bottom,label=label,color=color);bottom+=vals
    axes[0].set_ylim(0,1);axes[0].set_ylabel("Conditional frequency");axes[0].legend(fontsize=8)
    axes[0].set_title("Realized two-reward consequence")
    for i,p in enumerate(labels):
        e=estimates[p+"_mean_DeltaG"]
        if e["estimate"] is not None:
            axes[1].errorbar(i,e["estimate"],yerr=[[e["estimate"]-e["lower"]],[e["upper"]-e["estimate"]]],fmt="o",capsize=3)
    axes[1].axhline(0,color="gray",lw=.8); axes[1].set_xticks(range(3),labels)
    axes[1].set_ylabel("Mean raw ΔG (mu_true scale)")
    axes[1].set_title("Whole-seed 95% intervals")
    fig.suptitle("Divergent decisions only; null-action controls excluded")
    fig.tight_layout();fig.savefig(run.OUT/"counterfactual_consequences.svg",metadata={"Date":None});plt.close(fig)


if __name__=="__main__":
    main()
