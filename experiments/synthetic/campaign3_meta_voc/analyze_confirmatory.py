"""Predefined equal-domain, paired-history analysis and vector figures."""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_meta_voc import confirmatory as conf  # noqa: E402

B = 2000
BOOTSTRAP_SEED = 20261016
METRICS = ("cumulative_mu_true", "decision_compute_seconds")
POINTS = (25, 50, 75)
BASELINES = ("RANDOM", "FAST", "DEEP")
DOMAINS = conf.DOMAINS
COLORS = {"FAST": "#54606d", "DEEP": "#173f68", "META": "#007f73", "RANDOM": "#bd6b1e"}


def _bootstrap_indices(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    return {domain: rng.integers(0, int((frame.domain == domain).sum()),
                                 size=(B, int((frame.domain == domain).sum())))
            for domain in DOMAINS}


def paired_tables(runs: pd.DataFrame) -> pd.DataFrame:
    frame = runs.copy()
    frame["decision_compute_seconds"] = frame.decision_compute_ns / 1e9
    indices = _bootstrap_indices(frame.drop_duplicates("history_id"))
    records = []
    for point in POINTS:
        treatment = f"META_VOC_{point}"
        for baseline_kind in BASELINES:
            baseline = f"RANDOM_{point}" if baseline_kind == "RANDOM" else baseline_kind
            for metric in METRICS:
                arrays = {}
                draws = {}
                for domain in DOMAINS:
                    sub = frame.loc[frame.domain == domain]
                    wide = sub.pivot(index="history_id", columns="policy", values=metric).sort_index()
                    differences = (wide[treatment] - wide[baseline]).to_numpy(dtype=float)
                    arrays[domain] = differences
                    draws[domain] = differences[indices[domain]].mean(axis=1)
                    records.append({"domain": domain, "point": point, "treatment": treatment,
                                    "baseline": baseline, "metric": metric, "n_histories": len(differences),
                                    "mean_difference": differences.mean(),
                                    "ci95_low": np.quantile(draws[domain], .025),
                                    "ci95_high": np.quantile(draws[domain], .975),
                                    "median_difference": np.median(differences)})
                global_draws = np.mean(np.stack([draws[d] for d in DOMAINS]), axis=0)
                records.append({"domain": "GLOBAL_EQUAL_G", "point": point, "treatment": treatment,
                                "baseline": baseline, "metric": metric,
                                "n_histories": sum(len(arrays[d]) for d in DOMAINS),
                                "mean_difference": np.mean([arrays[d].mean() for d in DOMAINS]),
                                "ci95_low": np.quantile(global_draws, .025),
                                "ci95_high": np.quantile(global_draws, .975),
                                "median_difference": np.nan})
    return pd.DataFrame(records)


def policy_table(runs: pd.DataFrame, traces: pd.DataFrame) -> pd.DataFrame:
    records = []
    for domain in (*DOMAINS, "GLOBAL_EQUAL_G"):
        sub_runs = runs if domain == "GLOBAL_EQUAL_G" else runs.loc[runs.domain == domain]
        sub_traces = traces if domain == "GLOBAL_EQUAL_G" else traces.loc[traces.domain == domain]
        for policy in conf.POLICIES:
            group = sub_runs.loc[sub_runs.policy == policy]
            decisions = sub_traces.loc[sub_traces.policy == policy]
            if domain == "GLOBAL_EQUAL_G":
                performance = np.mean([group.loc[group.domain == d, "cumulative_mu_true"].mean() for d in DOMAINS])
                cost = np.mean([group.loc[group.domain == d, "decision_compute_ns"].mean() for d in DOMAINS]) / 1e9
                invocation = np.mean([group.loc[group.domain == d, "deep_invocations_nonterminal"].sum() /
                                      (24 * len(group.loc[group.domain == d])) for d in DOMAINS])
                selector = np.mean([group.loc[group.domain == d, "selector_ns"].mean() for d in DOMAINS]) / 1e9
            else:
                performance = group.cumulative_mu_true.mean()
                cost = group.decision_compute_ns.mean() / 1e9
                invocation = group.deep_invocations_nonterminal.sum() / (24 * len(group))
                selector = group.selector_ns.mean() / 1e9
            latency = decisions.decision_compute_ns.to_numpy(dtype=float) / 1e6
            records.append({"domain": domain, "policy": policy, "n_histories": len(group),
                            "mean_cumulative_mu_true": performance, "mean_compute_seconds_per_history": cost,
                            "total_measured_compute_seconds": group.decision_compute_ns.sum() / 1e9,
                            "deep_invocations_nonterminal": int(group.deep_invocations_nonterminal.sum()),
                            "nonterminal_decisions": 24 * len(group), "deep_invocation_fraction": invocation,
                            "selector_seconds_per_history": selector,
                            "selector_total_seconds": group.selector_ns.sum() / 1e9,
                            "latency_mean_ms": latency.mean(), "latency_median_ms": np.median(latency),
                            "latency_q25_ms": np.quantile(latency, .25), "latency_q75_ms": np.quantile(latency, .75),
                            "latency_q90_ms": np.quantile(latency, .90), "latency_q95_ms": np.quantile(latency, .95),
                            "latency_q99_ms": np.quantile(latency, .99)})
    return pd.DataFrame(records)


def verdict(pair: pd.DataFrame) -> tuple[str, str]:
    primary = pair.loc[(pair.domain == "GLOBAL_EQUAL_G") & (pair.point == 50) &
                       (pair.baseline == "RANDOM_50")]
    performance = primary.loc[primary.metric == "cumulative_mu_true"].iloc[0]
    computation = primary.loc[primary.metric == "decision_compute_seconds"].iloc[0]
    if performance.ci95_low > 0 and computation.ci95_high <= 0:
        return "CONFIRMATORY EVIDENCE FAVORABLE", "paired performance CI is positive and paired measured-computation CI is non-positive"
    if performance.ci95_high < 0 and computation.ci95_low >= 0:
        return "UNFAVORABLE", "paired performance CI is negative and paired measured-computation CI is non-negative"
    return "INCONCLUSIVE", "strict joint performance/computation rule not met; inspect both paired intervals without an equivalence claim"


def _style():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "pdf.fonttype": 42,
                         "figure.dpi": 150, "savefig.bbox": "tight"})


def _save(fig, stem: str, directory: Path):
    fig.savefig(directory / f"{stem}.svg")
    fig.savefig(directory / f"{stem}.pdf")
    plt.close(fig)


def figure_architecture(directory: Path):
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    fig, ax = plt.subplots(figsize=(10.6, 2.8))
    ax.set_xlim(0, 11); ax.set_ylim(0, 3); ax.axis("off")
    def box(x, y, width, label, color):
        ax.add_patch(FancyBboxPatch((x, y), width, .7, boxstyle="round,pad=0.10",
                                    linewidth=1.2, edgecolor=color, facecolor="white"))
        ax.text(x + width/2, y + .35, label, ha="center", va="center", color=color, fontsize=10)
    def arrow(a, b):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=12,
                                      lw=1.3, color="#465260"))
    box(.25, 1.15, 2.0, "Pre-action state\nS, b, clock", COLORS["FAST"])
    box(3.00, 1.15, 2.25, "Frozen Ridge proxy\nbenefit / estimated cost", COLORS["META"])
    box(6.15, 1.9, 2.0, "FAST: immediate\nexpected production", COLORS["FAST"])
    box(6.15, .4, 2.0, "DEEP: Q11\nprospective planning", COLORS["DEEP"])
    box(8.95, 1.15, 1.55, "Real HLS\ntransition", "#333333")
    arrow((2.35, 1.5), (2.90, 1.5)); arrow((5.35, 1.5), (6.05, 2.23))
    arrow((5.35, 1.5), (6.05, .73)); arrow((8.25, 2.23), (8.84, 1.63))
    arrow((8.25, .73), (8.84, 1.37))
    ax.text(5.65, 2.26, "accept", color=COLORS["FAST"], fontsize=9)
    ax.text(5.65, .46, "invoke", color=COLORS["DEEP"], fontsize=9)
    fig.suptitle("Conditional deliberation with frozen FAST and DEEP operators", y=.99)
    _save(fig, "figure1_architecture", directory)


def figure_performance_cost(policy: pd.DataFrame, directory: Path):
    _style()
    global_frame = policy.loc[policy.domain == "GLOBAL_EQUAL_G"]
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    for name, label, color, marker in (("FAST", "FAST", COLORS["FAST"], "s"),
                                       ("DEEP", "DEEP", COLORS["DEEP"], "s")):
        row = global_frame.loc[global_frame.policy == name].iloc[0]
        ax.scatter(row.mean_compute_seconds_per_history, row.mean_cumulative_mu_true,
                   s=75, color=color, marker=marker, label=label, zorder=3)
    for point in POINTS:
        for prefix, color, marker in (("META_VOC", COLORS["META"], "o"),
                                      ("RANDOM", COLORS["RANDOM"], "^")):
            row = global_frame.loc[global_frame.policy == f"{prefix}_{point}"].iloc[0]
            ax.scatter(row.mean_compute_seconds_per_history, row.mean_cumulative_mu_true,
                       s=70, color=color, marker=marker, zorder=3)
            ax.annotate(str(point), (row.mean_compute_seconds_per_history,
                                     row.mean_cumulative_mu_true), xytext=(4, 4),
                        textcoords="offset points", fontsize=9, color=color)
    for prefix, color, marker, title in (("META_VOC", COLORS["META"], "o", "META-VOC"),
                                          ("RANDOM", COLORS["RANDOM"], "^", "RANDOM")):
        rows = global_frame.loc[global_frame.policy.isin([f"{prefix}_{p}" for p in POINTS])].sort_values("mean_compute_seconds_per_history")
        ax.plot(rows.mean_compute_seconds_per_history, rows.mean_cumulative_mu_true,
                color=color, lw=1.4, label=title)
    ax.set_xlabel("Measured decision computation (s per history; equal domain weight)")
    ax.set_ylabel("Cumulative true production (equal domain weight)")
    ax.grid(alpha=.2); ax.legend(frameon=False, loc="lower right")
    ax.set_title("Performance and measured computation across frozen domains")
    _save(fig, "figure2_performance_cost", directory)


def figure_primary_domains(paired: pd.DataFrame, directory: Path):
    _style()
    frame = paired.loc[(paired.point == 50) & (paired.baseline == "RANDOM_50") &
                       (paired.metric == "cumulative_mu_true")].set_index("domain")
    order = [*DOMAINS, "GLOBAL_EQUAL_G"]
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    for index, domain in enumerate(order):
        row = frame.loc[domain]
        color = COLORS["META"] if domain != "GLOBAL_EQUAL_G" else COLORS["DEEP"]
        ax.errorbar(row.mean_difference, index,
                    xerr=np.array([[row.mean_difference-row.ci95_low],
                                   [row.ci95_high-row.mean_difference]]),
                    fmt="o", color=color, capsize=3, lw=1.6)
    ax.axvline(0, color="#666", ls="--", lw=1)
    ax.set_yticks(range(len(order)), ["G1: dev × dev", "G2: dev × held-out kernel",
                                     "G3: held-out team × dev", "G4: held-out × held-out",
                                     "Global: equal G weight"])
    ax.invert_yaxis(); ax.grid(axis="x", alpha=.2)
    ax.set_xlabel("META-VOC-50 − RANDOM-50 cumulative true production\npaired mean and 95% history-bootstrap interval")
    ax.set_title("Primary comparison by frozen generalization condition")
    _save(fig, "figure3_primary_domain_effects", directory)


def figure_invocations(policy: pd.DataFrame, directory: Path):
    _style()
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8), sharey=True)
    xs = np.arange(4)
    for ax, point in zip(axes, POINTS, strict=True):
        for offset, prefix, label, color in ((-.18, "META_VOC", "META-VOC", COLORS["META"]),
                                              (.18, "RANDOM", "RANDOM", COLORS["RANDOM"])):
            vals = [policy.loc[(policy.domain == d) & (policy.policy == f"{prefix}_{point}"),
                               "deep_invocation_fraction"].iloc[0] for d in DOMAINS]
            ax.bar(xs + offset, vals, width=.32, color=color, label=label)
        ax.axhline(point / 100, color="#666", lw=1, ls="--")
        ax.set_title(f"Nominal {point}%")
        ax.set_xticks(xs, DOMAINS)
        ax.set_ylim(0, 1)
        ax.grid(axis="y", alpha=.15)
    axes[0].set_ylabel("Realized DEEP calls / nonterminal decisions")
    axes[-1].legend(frameon=False, loc="upper right")
    fig.suptitle("Realized deliberation frequency by frozen domain")
    _save(fig, "figure4_invocation_rates", directory)


def analyze() -> Path:
    conf.verify_frozen()
    progress_path = conf.OUTPUT / "execution_progress.json"
    progress = json.loads(progress_path.read_text())
    if progress["status"] != "complete":
        raise RuntimeError("confirmatory raw execution is incomplete")
    for filename, field in (("runs.csv.gz", "runs_sha256"),
                            ("trajectories.csv.gz", "trajectories_sha256")):
        if conf.sha256(conf.OUTPUT / filename) != progress[field]:
            raise RuntimeError(f"raw artifact hash mismatch: {filename}")
    if (conf.OUTPUT / "analysis_summary.json").exists():
        raise RuntimeError("analysis already exists; refusing to overwrite")
    runs = pd.read_csv(conf.OUTPUT / "runs.csv.gz")
    traces = pd.read_csv(conf.OUTPUT / "trajectories.csv.gz")
    if len(runs) != 868 * 8 or len(traces) != 868 * 8 * 36:
        raise RuntimeError("unexpected raw count")
    if runs.groupby("domain").history_id.nunique().to_dict() != conf.EXPECTED_DOMAIN_COUNTS:
        raise RuntimeError("unexpected domain composition")
    if runs.groupby(["history_id", "policy"]).size().ne(1).any() or traces.groupby(["history_id", "policy"]).size().ne(36).any():
        raise RuntimeError("missing or duplicated policy trajectory")
    paired = paired_tables(runs)
    policies = policy_table(runs, traces)
    status, reason = verdict(paired)
    analysis_dir = conf.OUTPUT / "analysis"
    if analysis_dir.exists():
        raise RuntimeError("analysis directory already exists")
    analysis_dir.mkdir()
    paired.to_csv(analysis_dir / "paired_comparisons.csv", index=False)
    policies.to_csv(analysis_dir / "policy_summary.csv", index=False)
    performance_cost = policies[["domain", "policy", "n_histories", "mean_cumulative_mu_true",
                                 "mean_compute_seconds_per_history", "deep_invocation_fraction"]]
    performance_cost.to_csv(analysis_dir / "performance_cost_curve.csv", index=False)
    figure_architecture(analysis_dir)
    figure_performance_cost(policies, analysis_dir)
    figure_primary_domains(paired, analysis_dir)
    figure_invocations(policies, analysis_dir)
    summary = {"protocol": conf.PROTOCOL, "verdict": status, "verdict_basis": reason,
               "primary": paired.loc[(paired.domain == "GLOBAL_EQUAL_G") & (paired.point == 50) &
                                     (paired.baseline == "RANDOM_50")].to_dict("records"),
               "n_histories_by_domain": conf.EXPECTED_DOMAIN_COUNTS,
               "equal_domain_weight": .25, "bootstrap": {"unit": "complete matched history",
                                                   "stratified_by_domain": True, "resamples": B,
                                                   "seed": BOOTSTRAP_SEED, "interval": "percentile 95%"},
               "confirmatory_primary_selected_after_development_review": True,
               "timing": "uncached perf_counter_ns around chosen solver and META selector; within-process measured duration under parallel execution",
               "dependencies": {"python": sys.version, "numpy": np.__version__, "pandas": pd.__version__,
                                "matplotlib": matplotlib.__version__, "platform": platform.platform()},
               "raw_progress_sha256": conf.sha256(progress_path)}
    (conf.OUTPUT / "analysis_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    files = [*analysis_dir.iterdir(), conf.OUTPUT / "analysis_summary.json"]
    manifest = {"protocol": conf.PROTOCOL, "analysis_status": "complete",
                "pre_execution_manifest_sha256": conf.sha256(conf.FOUNDATION / "pre_execution_manifest.json"),
                "raw_runs_sha256": progress["runs_sha256"], "raw_trajectories_sha256": progress["trajectories_sha256"],
                "artifact_sha256": {str(path.relative_to(conf.OUTPUT)): conf.sha256(path) for path in sorted(files)}}
    (conf.OUTPUT / "analysis_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return conf.OUTPUT / "analysis_summary.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="analyze complete frozen raw execution once")
    args = parser.parse_args()
    if not args.run:
        parser.print_help()
    else:
        print(analyze())


if __name__ == "__main__":
    main()
