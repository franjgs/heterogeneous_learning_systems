"""Summarize paired coupling-pilot CSVs and create audit figures."""
from __future__ import annotations

import csv
import math
from pathlib import Path
import statistics
import sys

import pandas as pd
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "soc_triage_organization_coupling"
FIG = ROOT / "studies" / "soc_triage_organization_coupling" / "figures"
POLICIES = ("D1", "P1", "HLS-B")
KEYS = ["prevalence_scenario", "pi_expected", "classifier_point", "pD_target", "pFA_target", "rho_L1_target"]
METRICS = (
    "legacy_RN", "correct_on_time_expected_per_admitted", "routed_SLA_terminal",
    "required_resolution_SLA_terminal", "routing_accuracy", "backlog_L1_H",
    "backlog_L2_H", "backlog_L1_terminal", "backlog_L2_terminal",
    "peak_queue_L1_pre_dispatch", "peak_queue_L2_pre_dispatch",
    "utilization_L1_mean_H", "utilization_L2_mean_H",
)
PRIMARY = "correct_on_time_expected_per_admitted"


def _ci(values):
    values = [float(x) for x in values]
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    half = student_t.ppf(.975, len(values)-1)*sd/math.sqrt(len(values)) if len(values)>1 else 0.0
    return mean, sd, mean-half, mean+half


def _write(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for row in rows for k in row)))
        writer.writeheader(); writer.writerows(rows)


def summarize() -> dict[str, list[dict]]:
    episodes = pd.read_csv(OUT / "episodes.csv")
    triage = pd.read_csv(OUT / "triage_by_seed.csv")
    summary = []
    for key, group in episodes.groupby(KEYS, sort=True):
        base = dict(zip(KEYS, key))
        for policy in POLICIES:
            g = group[group.policy == policy]
            item = {**base, "policy": policy, "n_seeds": len(g)}
            for metric in METRICS:
                m, sd, lo, hi = _ci(g[metric])
                item.update({f"{metric}_mean": m, f"{metric}_sd": sd,
                             f"{metric}_ci95_low": lo, f"{metric}_ci95_high": hi})
            item["WAPS_P1_fraction_L1_mean"] = float(g.P1_fraction_of_WAPS_dispatches_L1.mean())
            item["WAPS_P1_fraction_L2_mean"] = float(g.P1_fraction_of_WAPS_dispatches_L2.mean())
            item["WAPS_switches_L1_mean"] = float(g.switches_L1.mean())
            item["WAPS_switches_L2_mean"] = float(g.switches_L2.mean())
            item["L1_service_hours_mean"] = float(g.service_hours_L1_consumed_by_terminal.mean())
            item["L2_service_hours_mean"] = float(g.service_hours_L2_consumed_by_terminal.mean())
            summary.append(item)
    _write(OUT / "summary_by_config_policy.csv", summary)

    paired = []
    for key, group in episodes.groupby(KEYS, sort=True):
        base = dict(zip(KEYS, key))
        wide = group.pivot(index="seed", columns="policy", values=list(METRICS))
        for left, right in (("HLS-B", "D1"), ("HLS-B", "P1"), ("D1", "P1")):
            for metric in METRICS:
                values = wide[(metric, left)] - wide[(metric, right)]
                mean, sd, lo, hi = _ci(values)
                paired.append({**base, "contrast": f"{left}-{right}", "metric": metric,
                               "n_paired_seeds": len(values), "mean_difference": mean,
                               "sd_paired_difference": sd, "ci95_low": lo, "ci95_high": hi})
    _write(OUT / "paired_contrasts.csv", paired)

    # Selection of a best fixed policy is explicitly retrospective, within cell.
    lookup = {(tuple(row[k] for k in KEYS), row["policy"]): row for row in summary}
    for item in summary:
        k = tuple(item[x] for x in KEYS)
        d1 = lookup[(k, "D1")][f"{PRIMARY}_mean"]
        p1 = lookup[(k, "P1")][f"{PRIMARY}_mean"]
        hb = lookup[(k, "HLS-B")][f"{PRIMARY}_mean"]
        item["best_fixed_primary_mean_retrospective"] = max(d1,p1)
        item["best_fixed_primary_policy_retrospective"] = "D1" if d1 >= p1 else "P1"
        item["HLSB_minus_best_fixed_primary_mean_retrospective"] = hb-max(d1,p1)
        d1r = lookup[(k,"D1")]["legacy_RN_mean"]
        p1r = lookup[(k,"P1")]["legacy_RN_mean"]
        hbr = lookup[(k,"HLS-B")]["legacy_RN_mean"]
        item["best_fixed_legacy_RN_mean_retrospective"] = max(d1r,p1r)
        item["best_fixed_legacy_RN_policy_retrospective"] = "D1" if d1r >= p1r else "P1"
        item["HLSB_minus_best_fixed_legacy_RN_mean_retrospective"] = hbr-max(d1r,p1r)
    _write(OUT / "summary_by_config_policy.csv", summary)

    triage_summary = []
    for key, group in triage.groupby([k for k in KEYS if k != "pi_expected"] + ["pi_expected"], sort=True):
        base = dict(zip([k for k in KEYS if k != "pi_expected"] + ["pi_expected"], key))
        counts = {name: int(group[name].sum()) for name in ("TP", "FP", "FN", "TN", "alert_count", "true_need_positive", "recommendations_positive")}
        negatives = counts["alert_count"] - counts["true_need_positive"]
        positives = counts["true_need_positive"]
        triage_summary.append({**base, **counts,
            "pD_pooled_over_seeds": counts["TP"]/positives if positives else 0.0,
            "pFA_pooled_over_seeds": counts["FP"]/negatives if negatives else 0.0,
            "recommendation_fraction_pooled": counts["recommendations_positive"]/counts["alert_count"] if counts["alert_count"] else 0.0,
            "expected_recommendation_fraction_mean": float(group.q_expected.mean()),
            "expected_L2_offered_per_h_mean": float(group.expected_L2_offered_per_h.mean()),
            "expected_L2_TP_per_h_mean": float(group.expected_L2_true_positive_per_h.mean()),
            "expected_L2_FP_per_h_mean": float(group.expected_L2_false_positive_per_h.mean()),
            "expected_L2_FN_per_h_mean": float(group.expected_L2_false_negative_per_h.mean()),
        })
    _write(OUT / "triage_summary.csv", triage_summary)

    interactions = []
    for (prevalence, rho), group in episodes.groupby(["prevalence_scenario", "rho_L1_target"]):
        for metric in (PRIMARY, "legacy_RN", "required_resolution_SLA_terminal"):
            for fixed in ("D1", "P1"):
                by_seed = {}
                for point_name in ("grid_pd07965_pfa2859", "grid_pd090_pfa001"):
                    g = group[group.classifier_point == point_name]
                    pivot = g.pivot(index="seed", columns="policy", values=metric)
                    by_seed[point_name] = pivot["HLS-B"] - pivot[fixed]
                a, b = by_seed["grid_pd07965_pfa2859"], by_seed["grid_pd090_pfa001"]
                values = b-a
                m, sd, lo, hi = _ci(values)
                interactions.append({"prevalence_scenario": prevalence, "rho_L1_target": rho,
                    "metric": metric, "adaptive_contrast": f"HLS-B-{fixed}",
                    "configuration_A": "grid_pd07965_pfa2859", "configuration_B": "grid_pd090_pfa001",
                    "n_paired_seeds": len(values), "interaction_difference_in_differences": m,
                    "sd_paired_interaction": sd, "ci95_low": lo, "ci95_high": hi,
                    "definition": "(HLS-B-fixed)_B - (HLS-B-fixed)_A; controlled synthetic points, not an ROC effect"})
    _write(OUT / "interaction_contrasts.csv", interactions)

    _figures(episodes, triage)
    return {"summary": summary, "paired": paired, "triage": triage_summary,
            "interactions": interactions}


def _figures(episodes: pd.DataFrame, triage: pd.DataFrame):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIG.mkdir(parents=True, exist_ok=True)
    # The old exact empirical point is nearly identical to the rounded grid
    # endpoint; exclude it from lines to avoid an unreadable duplicate. It
    # remains present in every CSV table.
    triage_grid = triage[triage.classifier_point != "historical_old_exact"]
    points = triage_grid.groupby(["prevalence_scenario", "rho_L1_target", "pD_target", "pFA_target"], as_index=False).agg(
        lambda_l2=("expected_L2_offered_per_h", "mean"),
        lambda_fp=("expected_L2_false_positive_per_h", "mean"),
        route_fraction=("recommendation_fraction", "mean"),
    )
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True, constrained_layout=True)
    for (prev, rho), ax in zip(((p,r) for p in sorted(points.prevalence_scenario.unique()) for r in sorted(points.rho_L1_target.unique())), axes.flat):
        sub = points[(points.prevalence_scenario == prev) & (points.rho_L1_target == rho)]
        for pd_, g in sub.groupby("pD_target"):
            g = g.sort_values("pFA_target")
            ax.plot(g.pFA_target, g.lambda_l2, marker="o", label=f"pD={pd_:.3f}")
        ax.set_title(f"{prev.replace('_',' ')}; rho_L1={rho:.2f}")
        ax.set_ylabel("Expected L2 recommendations / h")
        ax.grid(alpha=.25)
    for ax in axes[-1,:]: ax.set_xlabel("pFA operating point")
    axes[0,0].legend(frameon=False)
    fig.suptitle("Analytical offered L2 arrival rate by classifier point")
    fig.savefig(FIG / "l2_offered_load.png", dpi=160)
    plt.close(fig)

    primary = "correct_on_time_expected_per_admitted"
    hb = episodes[(episodes.policy == "HLS-B") & (episodes.classifier_point != "historical_old_exact")]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), sharex=True)
    for (prev, rho), ax in zip(((p,r) for p in sorted(hb.prevalence_scenario.unique()) for r in sorted(hb.rho_L1_target.unique())), axes.flat):
        h = hb[(hb.prevalence_scenario == prev) & (hb.rho_L1_target == rho)]
        for fixed, marker in (("D1", "o"), ("P1", "s")):
            rows=[]
            for (pname,pd_,pfa), hrow in h.groupby(["classifier_point","pD_target","pFA_target"]):
                other=episodes[(episodes.prevalence_scenario==prev)&(episodes.rho_L1_target==rho)&
                               (episodes.classifier_point==pname)&(episodes.policy==fixed)]
                merged=hrow[["seed",primary]].merge(other[["seed",primary]],on="seed",suffixes=("_h","_f"))
                dif=merged[f"{primary}_h"]-merged[f"{primary}_f"]
                m,sd,lo,hi=_ci(dif)
                rows.append((pfa,pd_,m,m-lo,hi-m,pname))
            for pd_ in sorted(set(x[1] for x in rows)):
                g=sorted([x for x in rows if x[1]==pd_],key=lambda x:x[0])
                ax.errorbar([x[0] for x in g],[x[2] for x in g],
                    yerr=[[x[3] for x in g],[x[4] for x in g]], marker=marker,
                    capsize=2, label=f"HLS-B − {fixed}, pD={pd_:.3f}")
        ax.axhline(0,color="black",linewidth=.8)
        prevalence_label = "historical prevalence" if prev == "historical_evaluation_prevalence" else "synthetic prevalence"
        ax.set_title(f"{prevalence_label}; rho_L1={rho:.2f}")
        ax.grid(alpha=.25)
    for ax in axes[-1,:]: ax.set_xlabel("pFA operating point")
    fig.supylabel("HLS-B difference in expected correct-and-on-time resolutions / admitted alert")
    fig.subplots_adjust(left=.12, bottom=.10, top=.90, right=.98, wspace=.20, hspace=.28)
    axes[0,0].legend(fontsize=7,frameon=False)
    fig.suptitle("Paired organizational effects by classifier point (mean and 95% paired t CI)")
    fig.savefig(FIG / "organizational_effect_by_classifier.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    data=summarize()
    print(f"Summarized {len(data['summary'])} policy/configuration means and {len(data['paired'])} paired contrasts")
