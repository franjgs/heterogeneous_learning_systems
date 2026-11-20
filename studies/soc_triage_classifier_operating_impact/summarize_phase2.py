"""Summarize paired phase-two episodes and create audit-friendly figures."""
from __future__ import annotations

import csv
import itertools
import math
import os
import random
import statistics
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "soc_triage_classifier_operating_impact"
PRIMARY = "correct_on_time_expected_per_admitted"
T95_DF39 = 2.02269092


def read_csv(name):
    with (OUT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(name, rows):
    if not rows:
        return
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def mean_ci(values):
    vals = [float(x) for x in values]
    avg = statistics.mean(vals)
    half = T95_DF39 * statistics.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else float("nan")
    return avg, avg-half, avg+half


def main():
    episodes = read_csv("episodes.csv")
    triage_rows = read_csv("triage_by_seed.csv")
    keys = ("label_definition", "prevalence_scenario", "classifier_id", "rho_L1", "n_L2")
    grouped = defaultdict(dict)
    for row in episodes:
        k = tuple(row[c] for c in keys)
        grouped[k][(int(row["seed"]), row["policy"])] = row
    metrics = [PRIMARY, "required_resolution_SLA_terminal", "routed_SLA_terminal",
               "legacy_RN", "necessary_L2_timely_per_need",
               "FP_L2_work_nominal_generated_by_terminal_h", "FN_L2_work_nominal_omitted_h",
               "backlog_L1_H", "backlog_L2_H", "utilization_L1_mean_H", "utilization_L2_mean_H",
               "P1_fraction_of_WAPS_dispatches_L1", "P1_fraction_of_WAPS_dispatches_L2"]
    summaries, paired = [], []
    for k, cells in grouped.items():
        present = sorted({s for s, _ in cells})
        for pol in ("D1", "P1", "HLS-B"):
            sample = [cells[(s, pol)] for s in present]
            row = dict(zip(keys, k), policy=pol, n_seeds=len(sample))
            for m in metrics:
                vals = [float(x[m]) for x in sample if x.get(m) not in (None, "")]
                if vals:
                    row[f"{m}_mean"], row[f"{m}_ci95_low"], row[f"{m}_ci95_high"] = mean_ci(vals)
            needs_by_seed = [int(cells[(s, pol)]["true_need_count"]) for s in present]
            tp_by_seed = [int(cells[(s, pol)]["TP_count"]) for s in present]
            pooled_need = sum(needs_by_seed)
            pooled_tp = sum(tp_by_seed)
            row["necessary_L2_detection_fraction_mean"] = pooled_tp / pooled_need if pooled_need else 0.0
            if pooled_need:
                rng = random.Random(int(sha256(repr((k, pol, "detection_bootstrap")).encode()).hexdigest()[:16], 16))
                ratios = []
                for _ in range(1000):
                    indexes = [rng.randrange(len(present)) for _ in present]
                    denom = sum(needs_by_seed[i] for i in indexes)
                    if denom:
                        ratios.append(sum(tp_by_seed[i] for i in indexes) / denom)
                ratios.sort()
                row["necessary_L2_detection_fraction_ci95_low"] = ratios[int(.025 * (len(ratios)-1))]
                row["necessary_L2_detection_fraction_ci95_high"] = ratios[int(.975 * (len(ratios)-1))]
            row["true_need_total_over_seeds"] = pooled_need
            row["TP_total_over_seeds"] = pooled_tp
            summaries.append(row)
        for comparator in ("D1", "P1"):
            diffs = [float(cells[(s, "HLS-B")][PRIMARY])-float(cells[(s, comparator)][PRIMARY]) for s in present]
            avg, lo, hi = mean_ci(diffs)
            paired.append(dict(zip(keys, k), contrast=f"HLS-B-{comparator}", n_seeds=len(diffs),
                                mean_difference=avg, ci95_low=lo, ci95_high=hi,
                                interpretation="exploratory paired t interval; unadjusted across comparisons"))

    # Direct paired classifier contrasts within the same trace, policy, and stratum.
    classifier_contrasts = []
    strata = defaultdict(dict)
    for k, cells in grouped.items():
        stratum = tuple(k[i] for i in (0, 1, 3, 4))
        strata[stratum][k[2]] = cells
    for stratum, point_cells in strata.items():
        for a, b in itertools.combinations(sorted(point_cells), 2):
            common_seeds = sorted({s for s, _ in point_cells[a]} & {s for s, _ in point_cells[b]})
            for policy in ("D1", "P1", "HLS-B"):
                diffs = [float(point_cells[b][(s, policy)][PRIMARY])-float(point_cells[a][(s, policy)][PRIMARY])
                         for s in common_seeds]
                avg, lo, hi = mean_ci(diffs)
                classifier_contrasts.append({"label_definition":stratum[0],"prevalence_scenario":stratum[1],
                    "rho_L1":stratum[2],"n_L2":stratum[3],"classifier_A":a,"classifier_B":b,
                    "policy":policy,"outcome":PRIMARY,"n_seeds":len(diffs),"mean_difference_B_minus_A":avg,
                    "ci95_low":lo,"ci95_high":hi,"interpretation":"exploratory paired classifier contrast; unadjusted"})

    # Paired difference-in-differences: does WAPS-vs-fixed advantage vary by classifier point?
    interaction = []
    outer = defaultdict(dict)
    for k, cells in grouped.items():
        condition = tuple(k[i] for i in (0, 1, 3, 4))
        outer[condition][k[2]] = cells
    for condition, point_cells in outer.items():
        for a, b in itertools.combinations(sorted(point_cells), 2):
            common_seeds = sorted({s for s, _ in point_cells[a]} & {s for s, _ in point_cells[b]})
            for comparator in ("D1", "P1"):
                vals = [(float(point_cells[b][(s, "HLS-B")][PRIMARY])-float(point_cells[b][(s, comparator)][PRIMARY]))
                        -(float(point_cells[a][(s, "HLS-B")][PRIMARY])-float(point_cells[a][(s, comparator)][PRIMARY]))
                        for s in common_seeds]
                avg, lo, hi = mean_ci(vals)
                interaction.append({"label_definition":condition[0],"prevalence_scenario":condition[1],
                    "rho_L1":condition[2],"n_L2":condition[3],"classifier_A":a,"classifier_B":b,
                    "contrast":"WAPS-vs-"+comparator,"n_seeds":len(vals),"difference_in_differences":avg,
                    "ci95_low":lo,"ci95_high":hi,"interpretation":"exploratory paired interaction; unadjusted"})

    # Multiobjective Pareto labels are descriptive mean comparisons, not inferential dominance.
    pareto = []
    obj = [("necessary_L2_detection_fraction_mean", 1), (f"{PRIMARY}_mean", 1),
           ("required_resolution_SLA_terminal_mean", 1),
           ("FP_L2_work_nominal_generated_by_terminal_h_mean", -1),
           ("FN_L2_work_nominal_omitted_h_mean", -1), ("backlog_L2_H_mean", -1)]
    for scenario in sorted({tuple(s[k] for k in keys[:2]+keys[3:]) for s in summaries}):
        candidates = [s for s in summaries if tuple(s[k] for k in keys[:2]+keys[3:]) == scenario]
        for target in candidates:
            dominated = False
            for other in candidates:
                if target is other: continue
                no_worse = all(d*float(other.get(m, "nan")) >= d*float(target.get(m, "nan")) for m,d in obj)
                strictly = any(d*float(other.get(m, "nan")) > d*float(target.get(m, "nan")) for m,d in obj)
                if no_worse and strictly: dominated=True; break
            pareto.append({**{k:target[k] for k in keys[:2]+keys[3:]}, "classifier_id":target["classifier_id"],
                           "policy":target["policy"], "mean_vector_dominated":dominated,
                           "rule":"descriptive six-objective mean Pareto comparison; no uncertainty adjustment"})

    # Pooled confusion rates preserve correct denominators when positives are rare.
    triage_groups = defaultdict(list)
    triage_keys = ("label_definition", "prevalence_scenario", "classifier_id", "rho_L1")
    for row in triage_rows:
        triage_groups[tuple(row[k] for k in triage_keys)].append(row)
    triage_summary = []
    for key, sample in triage_groups.items():
        totals = {m:sum(int(r[m]) for r in sample) for m in ("TP","FP","FN","TN","alert_count")}
        p_d = totals["TP"] / (totals["TP"]+totals["FN"]) if totals["TP"]+totals["FN"] else 0.0
        p_fa = totals["FP"] / (totals["FP"]+totals["TN"]) if totals["FP"]+totals["TN"] else 0.0
        triage_summary.append(dict(zip(triage_keys,key),n_seeds=len(sample),**totals,
            pD_target=sample[0]["pD_target"],pFA_target=sample[0]["pFA_target"],
            pD_pooled=p_d,pFA_pooled=p_fa,BA_pooled=(1-p_fa+p_d)/2,
            note="pooled confusion rates; 40 paired seed traces, low-prevalence rate uncertainty remains"))
    write_csv("triage_confusion_pooled.csv", triage_summary)
    write_csv("summary_by_condition.csv", summaries)
    write_csv("paired_policy_contrasts.csv", paired)
    write_csv("paired_classifier_contrasts.csv", classifier_contrasts)
    write_csv("classifier_organization_interactions.csv", interaction)
    write_csv("operational_pareto_descriptive.csv", pareto)
    make_figures(episodes, summaries, paired)
    print(f"Summarized {len(episodes)} episodes into {len(summaries)} condition means, {len(paired)} policy contrasts, {len(classifier_contrasts)} classifier contrasts, {len(interaction)} interactions")


def make_figures(episodes, summaries, paired):
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/soctra_hls_phase2_mpl")
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Analytic recommendation load versus false-alarm probability for all points.
    points = read_csv("all_published_operating_points.csv")
    analytic = read_csv("analytic_load_by_point.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), constrained_layout=True)
    for ax, label in zip(axes, ("original", "standardized")):
        subset = [r for r in analytic if r["label_definition"] == label and r["prevalence_scenario"] in (
            "original_test_exact_audited", "standardized_article_test_table2_inferred")
            and float(r["rho_L1"]) == 0.85 and int(r["n_L2"]) == 3]
        for r in subset:
            ax.scatter(float(r["pFA"]), float(r["rho_L2_offered"]), s=28)
            ax.annotate(r["classifier_id"].replace(label+"_", ""), (float(r["pFA"]), float(r["rho_L2_offered"])), fontsize=6)
        ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
        ax.set(title=f"{label.capitalize()} labels; normal L1, 3 L2", xlabel="Published pFA", ylabel="Analytical offered load L2 / capacity")
    fig.savefig(OUT/"analytic_load_by_false_alarm.png", dpi=180); plt.close(fig)

    # Paired operational result by classifier and load, at reference 3-L2 roster.
    picks = [r for r in paired if r["prevalence_scenario"] in (
        "original_test_exact_audited", "standardized_article_test_table2_inferred") and int(r["n_L2"]) == 3]
    fig, axes = plt.subplots(2, 4, figsize=(17, 8), sharey=True, constrained_layout=True)
    conditions = list(itertools.product(("original","standardized"),("0.85","1.25"),("HLS-B-D1","HLS-B-P1")))
    for ax, (label, rho, contrast) in zip(axes.flat, conditions):
        rows=[r for r in picks if r["label_definition"]==label and r["rho_L1"]==rho and r["contrast"]==contrast]
        rows.sort(key=lambda r:r["classifier_id"])
        x=range(len(rows)); means=[float(r["mean_difference"]) for r in rows]
        lo=[m-float(r["ci95_low"]) for m,r in zip(means,rows)]; hi=[float(r["ci95_high"])-m for m,r in zip(means,rows)]
        ax.errorbar(list(x),means,yerr=[lo,hi],fmt="o",capsize=3); ax.axhline(0,color="black",linewidth=.8)
        short = [r["classifier_id"].replace(label+"_","").replace("bayesian_mlp", "BMLP").replace("lightgbm", "LGBM") for r in rows]
        ax.set_xticks(list(x), short, rotation=40, ha="right", fontsize=7)
        ax.set_title(f"{label}, rhoL1={rho}, {contrast}", fontsize=10)
        if ax in (axes[0, 0], axes[1, 0]):
            ax.set_ylabel("WAPS − fixed policy\n(correct/on-time per admitted)")
        else:
            ax.set_ylabel("")
    fig.savefig(OUT/"paired_policy_effects.png",dpi=180); plt.close(fig)

    # Policy interaction by pFA for observed operational outcomes; descriptive means.
    fig, axes=plt.subplots(1,2,figsize=(10,4.2),sharey=True,constrained_layout=True)
    for ax,label in zip(axes,("original","standardized")):
        rows=[r for r in summaries if r["label_definition"]==label and r["prevalence_scenario"] in (
            "original_test_exact_audited","standardized_article_test_table2_inferred")
            and float(r["rho_L1"])==1.25 and int(r["n_L2"])==3]
        pmap={p["id"]:p for p in points if p["label_definition"]==label}
        for pol in ("D1","P1","HLS-B"):
            rr=sorted([r for r in rows if r["policy"]==pol],key=lambda r:pmap[r["classifier_id"]]["pFA"])
            ax.plot([pmap[r["classifier_id"]]["pFA"] for r in rr],[float(r[f"{PRIMARY}_mean"]) for r in rr],"o-",label=pol)
        ax.set(xlabel="Published pFA",ylabel="Correct and on-time expected resolutions / admitted",title=f"{label.capitalize()} labels; high L1, 3 L2")
        ax.legend()
    fig.savefig(OUT/"operational_outcome_vs_false_alarm.png",dpi=180);plt.close(fig)

    # Operational trade-off: unnecessary FP work against correct/on-time output.
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    markers = {"D1":"o", "P1":"s", "HLS-B":"^"}
    colors = {"D1":"#4477AA", "P1":"#CC6677", "HLS-B":"#228833"}
    for ax, (label, rho) in zip(axes.flat, itertools.product(("original","standardized"),("0.85","1.25"))):
        prev = "original_test_exact_audited" if label == "original" else "standardized_article_test_table2_inferred"
        rows=[r for r in summaries if r["label_definition"]==label and r["prevalence_scenario"]==prev
              and r["rho_L1"]==rho and int(r["n_L2"])==3]
        pmap={p["id"]:p for p in points if p["label_definition"]==label}
        for r in rows:
            ax.scatter(float(r["FP_L2_work_nominal_generated_by_terminal_h_mean"]),
                       float(r[f"{PRIMARY}_mean"]), marker=markers[r["policy"]],
                       color=colors[r["policy"]], s=48, alpha=.8,
                       label=r["policy"] if r["classifier_id"]==rows[0]["classifier_id"] else None)
            short=r["classifier_id"].replace(label+"_","").replace("bayesian_mlp","BMLP").replace("lightgbm","LGBM")
            ax.annotate(short, (float(r["FP_L2_work_nominal_generated_by_terminal_h_mean"]),
                                float(r[f"{PRIMARY}_mean"])), fontsize=6, xytext=(3,2),textcoords="offset points")
        ax.set_title(f"{label.capitalize()} labels; rhoL1={rho}; 3 L2 analysts",fontsize=10)
        ax.set_xlabel("FP L2 nominal service work generated by H (h)")
        ax.set_ylabel("Correct/on-time expected per admitted")
        ax.grid(alpha=.2)
    handles=[plt.Line2D([0],[0],marker=markers[p],color="w",markerfacecolor=colors[p],label=p,markersize=8) for p in markers]
    fig.legend(handles=handles,loc="upper center",ncol=3)
    fig.savefig(OUT/"operational_tradeoff_reference_roster.png",dpi=180);plt.close(fig)


if __name__ == "__main__":
    main()
