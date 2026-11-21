"""Audit saved episode invariants and bootstrap classifier×policy interactions.

This script only reads saved result CSVs; it does not generate traces or run
the simulator. The same bootstrap seed indices are applied to every factor.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results/soc_triage_hls_q1_integration_evidence"
EPISODES = RESULTS / "episodes.csv"
TRACE_AUDIT = RESULTS / "trace_audit.csv"
CONFIG = json.loads((ROOT / "studies/soc_triage_hls_q1_integration_evidence/config/primary_campaign.json").read_text())
OUT_INTERACTIONS = RESULTS / "audit_interaction_contrasts.csv"
OUT_NEEDS = RESULTS / "audit_need_distribution.csv"
OUT_CHECKS = RESULTS / "audit_checks.json"

CLASSIFIER_PAIRS = (
    ("standardized_lightgbm_apc_symmetric", "standardized_lsensemble_apc_symmetric"),
    ("standardized_lightgbm_apc_symmetric", "standardized_bayesian_mlp_apc_symmetric"),
    ("standardized_lsensemble_apc_symmetric", "standardized_bayesian_mlp_apc_symmetric"),
)
POLICY_PAIRS = (("HLS-B", "D1"), ("P1", "D1"), ("HLS-B", "P1"))


def main() -> None:
    ep = pd.read_csv(EPISODES, low_memory=False)
    ta = pd.read_csv(TRACE_AUDIT)
    classifiers = list(CONFIG["classifiers"][i]["id"] for i in range(len(CONFIG["classifiers"])))
    alphas = [float(x) for x in CONFIG["simulation"]["fp_service_fraction_alpha"]]
    rosters = [int(x) for x in CONFIG["simulation"]["n_L2"]]
    policies = list(CONFIG["simulation"]["policies"])
    expected_seeds = list(range(
        int(CONFIG["simulation"]["seed_base"]),
        int(CONFIG["simulation"]["seed_base"]) + int(CONFIG["simulation"]["n_new_paired_seeds"]),
    ))

    factors = ["classifier_id", "alpha_fp_service_fraction", "n_L2", "policy", "seed"]
    duplicate_count = int(ep.duplicated(factors).sum())
    expected_n = len(classifiers) * len(alphas) * len(rosters) * len(policies) * len(expected_seeds)
    if len(ep) != expected_n or duplicate_count:
        raise AssertionError(f"row/uniqueness check failed: rows={len(ep)}, duplicates={duplicate_count}, expected={expected_n}")
    if (ep.groupby(factors, dropna=False).size() != 1).any():
        raise AssertionError("episode factor grid has missing or repeated cells")

    # Seed-level exogenous needs are the independent simulation block units.
    unique_need_rows = ta[ta.classifier_id == classifiers[0]].set_index("seed").sort_index()
    if unique_need_rows.index.tolist() != expected_seeds:
        raise AssertionError("trace audit does not contain the expected seed IDs")
    if ta.groupby("seed").exogenous_sha256.nunique().max() != 1:
        raise AssertionError("exogenous hashes differ by classifier within seed")
    if ta.groupby("seed").alerts.nunique().max() != 1 or ta.groupby("seed").synthetic_needs.nunique().max() != 1:
        raise AssertionError("alert or need counts differ by classifier within seed")
    needs_by_seed = unique_need_rows.synthetic_needs.astype(int)
    need_distribution = Counter(needs_by_seed.tolist())
    need_rows = [{"synthetic_needs_in_seed": k, "seed_blocks": v} for k, v in sorted(need_distribution.items())]
    with OUT_NEEDS.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["synthetic_needs_in_seed", "seed_blocks"], lineterminator="\n")
        writer.writeheader(); writer.writerows(need_rows)

    # Denominators/confusion counts and routed trace hashes must repeat exactly
    # across policies, alpha, and roster for a given classifier/seed.
    invariant_cols = ["admitted", "true_need_count", "TP", "FP", "FN", "TN", "recommendations",
                      "l1_tasks_assigned", "exogenous_sha256", "trace_sha256"]
    invariant_groups = ep.groupby(["classifier_id", "seed"], sort=False)[invariant_cols].nunique(dropna=False)
    if (invariant_groups > 1).any().any():
        bad = invariant_groups[(invariant_groups > 1).any(axis=1)].head().to_dict("index")
        raise AssertionError(f"trace or confusion values vary across matched cells: {bad}")
    if not (ep.TP.astype(int) + ep.FN.astype(int) == ep.true_need_count.astype(int)).all():
        raise AssertionError("TP+FN differs from need denominator")
    if not (ep.TP.astype(int) + ep.FP.astype(int) + ep.FN.astype(int) + ep.TN.astype(int) == ep.admitted.astype(int)).all():
        raise AssertionError("confusion totals differ from admitted alerts")
    if not (ep.timely_needs_numerator.astype(int) <= ep.TP.astype(int)).all():
        raise AssertionError("timely need numerator exceeds TP")
    if not (ep.S_plus_denominator.astype(int) == ep.true_need_count.astype(int)).all():
        raise AssertionError("S+ denominator differs from all synthetic needs")

    seeds = expected_seeds
    seed_index = {s: i for i, s in enumerate(seeds)}
    boot_n = int(CONFIG["statistics"]["bootstrap"]["replicates"])
    boot_seed = int(CONFIG["statistics"]["bootstrap"]["seed"])
    rng = np.random.default_rng(boot_seed)
    sample = rng.integers(0, len(seeds), size=(boot_n, len(seeds)))
    # Each condition's ratio is recalculated from sampled integer counts.
    cell_values = {}
    cell_numerators = {}
    for classifier in classifiers:
        for alpha in alphas:
            for roster in rosters:
                for policy in policies:
                    rows = ep[(ep.classifier_id == classifier)
                              & (ep.alpha_fp_service_fraction == alpha)
                              & (ep.n_L2 == roster) & (ep.policy == policy)].sort_values("seed")
                    if rows.seed.astype(int).tolist() != seeds:
                        raise AssertionError("cell missing seed or seed order mismatch")
                    nums = rows.timely_needs_numerator.astype(int).to_numpy()
                    dens = rows.S_plus_denominator.astype(int).to_numpy()
                    numerator = nums[sample].sum(axis=1)
                    denominator = dens[sample].sum(axis=1)
                    if (denominator == 0).any():
                        raise AssertionError("zero-denominator bootstrap draw; report and handle before interpreting")
                    cell_values[(classifier, alpha, roster, policy)] = numerator / denominator
                    cell_numerators[(classifier, alpha, roster, policy)] = (int(nums.sum()), int(dens.sum()))

    rows_out = []
    interaction_draws = []
    for alpha in alphas:
        for roster in rosters:
            for a, b in CLASSIFIER_PAIRS:
                for p, q in POLICY_PAIRS:
                    # Requested direction: [S+(A,P)-S+(B,P)] - [S+(A,Q)-S+(B,Q)].
                    p_ap = cell_values[(a, alpha, roster, p)]
                    p_bp = cell_values[(b, alpha, roster, p)]
                    p_aq = cell_values[(a, alpha, roster, q)]
                    p_bq = cell_values[(b, alpha, roster, q)]
                    draws = (p_ap - p_bp) - (p_aq - p_bq)
                    n_ap, d_ap = cell_numerators[(a, alpha, roster, p)]
                    n_bp, d_bp = cell_numerators[(b, alpha, roster, p)]
                    n_aq, d_aq = cell_numerators[(a, alpha, roster, q)]
                    n_bq, d_bq = cell_numerators[(b, alpha, roster, q)]
                    point = (n_ap/d_ap - n_bp/d_bp) - (n_aq/d_aq - n_bq/d_bq)
                    interaction_draws.append((point, draws))
                    rows_out.append({
                        "classifier_A": a, "classifier_B": b, "alpha": alpha, "n_L2": roster,
                        "policy_P": p, "policy_Q": q,
                        "contrast_definition": "(S_A_P-S_B_P)-(S_A_Q-S_B_Q)",
                        "interaction_S_plus": point,
                        "bootstrap_CI95_low": float(np.quantile(draws, .025)),
                        "bootstrap_CI95_high": float(np.quantile(draws, .975)),
                        "bootstrap_replicates": boot_n, "bootstrap_seed": boot_seed,
                        "independent_seed_blocks": len(seeds),
                        "need_clusters_with_positive_count": int((needs_by_seed > 0).sum()),
                        "need_count_total": int(needs_by_seed.sum()),
                        "multiplicity": "108 pointwise exploratory contrasts; unadjusted",
                    })
    # Family-wise simultaneous bands over the full prespecified 108-contrast
    # family using a paired, non-studentized max-|z| bootstrap statistic.
    point_vector = np.array([point for point, _ in interaction_draws])
    draw_matrix = np.column_stack([draws for _, draws in interaction_draws])
    se_vector = draw_matrix.std(axis=0, ddof=1)
    active = se_vector > 0
    max_z = np.max(np.abs((draw_matrix[:, active] - point_vector[active]) / se_vector[active]), axis=1)
    max_z_critical = float(np.quantile(max_z, .95))
    for index, row in enumerate(rows_out):
        half_width = max_z_critical * se_vector[index]
        row["maxT_familywise95_low"] = point_vector[index] - half_width
        row["maxT_familywise95_high"] = point_vector[index] + half_width
        row["maxT_critical_value"] = max_z_critical
        row["maxT_family"] = "all 108 classifier-pair × policy-pair × alpha × L2-roster interactions"
    pd.DataFrame(rows_out).to_csv(OUT_INTERACTIONS, index=False, float_format="%.10g", lineterminator="\n")

    checks = {
        "status": "PASS",
        "episode_rows": len(ep), "expected_rows": expected_n, "duplicate_factor_rows": duplicate_count,
        "factor_grid": {"classifiers": classifiers, "alpha": alphas, "n_L2": rosters, "policies": policies},
        "independent_simulation_units": len(seeds),
        "rows_per_seed_block": expected_n // len(seeds),
        "positive_need_alerts": int(needs_by_seed.sum()),
        "positive_need_seed_blocks": int((needs_by_seed > 0).sum()),
        "zero_need_seed_blocks": int((needs_by_seed == 0).sum()),
        "need_count_distribution": {str(k): int(v) for k, v in sorted(need_distribution.items())},
        "admitted_alert_count_min_max": [int(ep.groupby("seed").admitted.first().min()), int(ep.groupby("seed").admitted.first().max())],
        "exogenous_trace_hashes_shared_across_classifiers": True,
        "confusion_and_recommendation_counts_constant_within_classifier_seed": True,
        "S_plus_denominator_equals_all_needs": True,
        "S_plus_numerator_not_greater_than_TP": True,
        "bootstrap": {"replicates": boot_n, "seed": boot_seed, "block": "seed ID; same index matrix for all classifiers/policies/alpha/rosters", "zero_denominator_replicates": 0},
        "interaction_rows": len(rows_out), "interaction_formula": "(S_A_P-S_B_P)-(S_A_Q-S_B_Q)",
        "maxT_familywise_intervals": "paired non-studentized max-|z| bootstrap over all 108 contrasts",
        "maxT_critical_value": max_z_critical,
        "maxT_intervals_excluding_zero": int(sum((r["maxT_familywise95_low"] > 0) or (r["maxT_familywise95_high"] < 0) for r in rows_out)),
        "multiplicity_adjustment": "none; exploratory intervals are pointwise",
        "published_pD_pFA_uncertainty": "not estimated: audited model-specific source counts/denominators unavailable; rates held fixed",
    }
    OUT_CHECKS.write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
