"""Post-Campaign-2 state-coverage audit over retained trajectories only.

This module performs no environment transitions, observations, RNG draws, or
new experiment. It evaluates frozen, side-effect-free diagnostics on states
already retained by Campaign 2.

The operational support rule is fixed in source before reading audit outcomes.
Within each exact (scenario, configuration, problem, decision) stratum, use
equal-weight RMS distance over the primitive 3 belief + 6 capability cells.
Exclude the same seed from possible Q11 neighbours. A target is empirically
covered iff its nearest-Q11 distance is no larger than the maximum Q11
leave-one-seed-out nearest-neighbour distance in that stratum. This conservative
rule asks whether Q11-only development avoids extrapolating beyond its own
observed seed-to-seed spacing; it is a diagnostic convention, not a scientific
effect threshold. Coordinate-envelope coverage is reported separately.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from math import log, sqrt
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign2_prospective_adaptation import run as c2run
from experiments.synthetic.campaign2_prospective_adaptation.artifact_io import persist_tables


BASE_COMMIT = "41d918da3d13ea6380064c76166d7248b00935ac"
INPUT = ROOT / "results/campaigns/campaign2_prospective_adaptation/attempt_02"
OUT = ROOT / "results/diagnostics/campaign2_state_coverage_audit"
TRAJECTORIES = INPUT / "closed_loop_trajectories.csv.gz"
REFERENCE = INPUT / "reference_states.csv"
STRATUM = ("scenario", "configuration", "problem_index", "decision")
POLICIES = ("Q00", "Q10", "Q01", "Q11")
CORE = ("b0", "b1", "b2", "s00", "s01", "s10", "s11", "s20", "s21")
FEATURE_SCALES = {
    **{f"b{i}": 1.0 for i in range(3)},
    **{f"s{i}{k}": 1.0 for i in range(3) for k in range(2)},
    "H": log(3.0), "D_I": 1.0 / 3.0, "D_I_norm": 1.0,
    "D_I_loss": 3.0, "H_S": 6.0, "C": 1.0, "N": 1.0,
    "M": 1.0, "p": 1.0,
}
FILES = {
    "states": "state_descriptors.csv.gz",
    "support": "support_rows.csv.gz",
    "marginals": "marginal_comparisons.csv",
    "summary": "support_summary.csv",
    "strata": "stratified_support.csv",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def _unpack(value):
    return json.loads(value)


def enrich_chunk(rows):
    """Pure descriptors and frozen Q11 action on already visited states."""
    out = []
    with c2run.exact_cache():
        for row in rows:
            s = tuple(tuple(float(x) for x in pair) for pair in _unpack(row["S_before"]))
            b = tuple(float(x) for x in _unpack(row["b_before"]))
            d = c2run.theory.structural_descriptors(s, b)
            remaining = 3 - int(row["decision"])
            # The audit population is nonterminal. No environment transition occurs.
            q11 = c2run.first(c2run.values(s, b, remaining, "Q11"))
            record = {k: row[k] for k in (
                "scenario", "configuration", "seed", "problem_index", "decision",
                "policy", "C", "N", "M", "represented", "action_id")}
            record.update(p=float(_unpack(row["true_theta"])[0]),
                H=d.entropy, D_I=d.disagreement,
                D_I_norm=d.disagreement_normalized,
                D_I_loss=d.myopic_regret, H_S=d.capability_headroom,
                q11_action_id=c2run.ACTION_IDS[q11],
                owner_differs_from_q11=int(int(row["action_id"]) != c2run.ACTION_IDS[q11]))
            record.update({f"b{i}": b[i] for i in range(3)})
            record.update({f"s{i}{k}": s[i][k] for i in range(3) for k in range(2)})
            out.append(record)
    return out


def ks_distance(a, b):
    a = np.sort(np.asarray(a, dtype=float)); b = np.sort(np.asarray(b, dtype=float))
    grid = np.sort(np.unique(np.concatenate((a, b))))
    return float(np.max(np.abs(np.searchsorted(a, grid, side="right") / len(a)
                               - np.searchsorted(b, grid, side="right") / len(b))))


def marginal_rows(states):
    rows = []
    reference = states[states.policy == "Q11"]
    for policy in POLICIES:
        target = states[states.policy == policy]
        for feature, scale in FEATURE_SCALES.items():
            a = target[feature].to_numpy(float); b = reference[feature].to_numpy(float)
            missing_a = float(np.isnan(a).mean()); missing_b = float(np.isnan(b).mean())
            a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
            rows.append(dict(policy=policy, feature=feature, scale=scale,
                n=len(a), missing_rate=missing_a, q11_missing_rate=missing_b,
                mean=float(a.mean()), q11_mean=float(b.mean()),
                mean_difference=float(a.mean() - b.mean()),
                median=float(np.median(a)), q11_median=float(np.median(b)),
                q05=float(np.quantile(a, .05)), q95=float(np.quantile(a, .95)),
                q11_q05=float(np.quantile(b, .05)), q11_q95=float(np.quantile(b, .95)),
                ks=ks_distance(a, b),
                normalized_w1=float(np.mean(np.abs(np.sort(a) - np.sort(b))) / scale)))
    # Frozen structural fields must have identical empirical distributions.
    for feature in ("scenario", "configuration", "problem_index", "decision", "represented"):
        levels = sorted(set(states[feature].astype(str)))
        pa = reference[feature].astype(str).value_counts(normalize=True)
        for policy in POLICIES:
            pb = states[states.policy == policy][feature].astype(str).value_counts(normalize=True)
            tv = .5 * sum(abs(float(pa.get(x, 0.0)) - float(pb.get(x, 0.0))) for x in levels)
            rows.append(dict(policy=policy, feature=feature, scale=None, n=len(reference),
                missing_rate=0.0, q11_missing_rate=0.0, mean=None, q11_mean=None,
                mean_difference=None, median=None, q11_median=None, q05=None, q95=None,
                q11_q05=None, q11_q95=None, ks=None, normalized_w1=None,
                categorical_total_variation=tv))
    return rows


def support_rows(states):
    records = []
    for keys, group in states.groupby(list(STRATUM), sort=False):
        ref = group[group.policy == "Q11"].copy()
        assert len(ref) == 40 and set(ref.seed) == set(range(10, 50))
        ref_x = ref[list(CORE)].to_numpy(float)
        ref_seed = ref.seed.to_numpy(int)
        self_radius = []
        for i in range(len(ref)):
            mask = ref_seed != ref_seed[i]
            distances = np.sqrt(np.mean((ref_x[mask] - ref_x[i]) ** 2, axis=1))
            self_radius.append(float(distances.min()))
        threshold = max(self_radius)
        for row in group.itertuples(index=False):
            x = np.array([getattr(row, feature) for feature in CORE], dtype=float)
            mask = ref_seed != row.seed
            candidates = ref_x[mask]
            distances = np.sqrt(np.mean((candidates - x) ** 2, axis=1))
            j = int(np.argmin(distances)); nearest = float(distances[j])
            candidate_seeds = ref_seed[mask]
            lows, highs = candidates.min(axis=0), candidates.max(axis=0)
            outside = ((x < lows) | (x > highs))
            records.append(dict(**{k: getattr(row, k) for k in STRATUM},
                seed=int(row.seed), policy=row.policy,
                owner_differs_from_q11=int(row.owner_differs_from_q11),
                nearest_q11_seed=int(candidate_seeds[j]),
                nearest_q11_rms=nearest,
                q11_self_max_rms=threshold,
                distance_ratio_to_q11_self_max=nearest / threshold if threshold > 0 else (0.0 if nearest == 0 else None),
                covered_by_q11_spacing=int(nearest <= threshold + 1e-15),
                inside_q11_coordinate_envelope=int(not outside.any()),
                outside_coordinate_count=int(outside.sum())))
    return records


def support_summaries(support):
    rows = []
    for policy, group in support.groupby("policy", sort=False):
        for subset, data in (("all", group),
                             ("owner_action_differs_from_q11", group[group.owner_differs_from_q11 == 1]),
                             ("owner_action_equals_q11", group[group.owner_differs_from_q11 == 0])):
            rows.append(dict(policy=policy, subset=subset, n=len(data),
                action_difference_rate=float(group.owner_differs_from_q11.mean()),
                spacing_coverage=float(data.covered_by_q11_spacing.mean()) if len(data) else None,
                coordinate_envelope_coverage=float(data.inside_q11_coordinate_envelope.mean()) if len(data) else None,
                nearest_rms_mean=float(data.nearest_q11_rms.mean()) if len(data) else None,
                nearest_rms_median=float(data.nearest_q11_rms.median()) if len(data) else None,
                nearest_rms_q95=float(data.nearest_q11_rms.quantile(.95)) if len(data) else None,
                distance_ratio_q95=float(data.distance_ratio_to_q11_self_max.dropna().quantile(.95)) if len(data) else None,
                uncovered_states=int((data.covered_by_q11_spacing == 0).sum())))
    return rows


def stratified_rows(support):
    rows = []
    dimensions = ("scenario", "configuration", "problem_index", "decision")
    for dimension in dimensions:
        for (policy, level), group in support.groupby(["policy", dimension], sort=False):
            rows.append(dict(dimension=dimension, level=level, policy=policy, n=len(group),
                action_difference_rate=float(group.owner_differs_from_q11.mean()),
                spacing_coverage=float(group.covered_by_q11_spacing.mean()),
                coordinate_envelope_coverage=float(group.inside_q11_coordinate_envelope.mean()),
                nearest_rms_mean=float(group.nearest_q11_rms.mean()),
                nearest_rms_q95=float(group.nearest_q11_rms.quantile(.95)),
                uncovered_states=int((group.covered_by_q11_spacing == 0).sum())))
    return rows


def main(workers=8):
    if OUT.exists():
        raise FileExistsError(f"refuse to overwrite {OUT}")
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == BASE_COMMIT
    validation = json.loads((INPUT / "validation_summary.json").read_text())
    assert validation["passed"] and validation["counts"]["trajectories"] == 92160
    trajectories = pd.read_csv(TRAJECTORIES, float_precision="round_trip")
    trajectories = trajectories[trajectories.decision < 2].copy()
    assert len(trajectories) == 61440
    assert (trajectories.groupby("policy").size() == 15360).all()
    rows = trajectories.to_dict("records")
    chunks = [rows[i:i + 128] for i in range(0, len(rows), 128)]
    enriched = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for n, batch in enumerate(pool.map(enrich_chunk, chunks, chunksize=1), 1):
            enriched.extend(batch)
            if n % 40 == 0:
                print(f"descriptor chunks {n}/{len(chunks)}", flush=True)
    states = pd.DataFrame(enriched)
    assert len(states) == 61440 and not states.duplicated([
        "scenario", "configuration", "seed", "problem_index", "decision", "policy"]).any()
    # Reproduce every pre-existing Q11 descriptor/action exactly.
    prior = pd.read_csv(REFERENCE, float_precision="round_trip")
    prior = prior[prior.remaining > 1]
    q11 = states[states.policy == "Q11"].merge(prior,
        on=["scenario", "configuration", "seed", "problem_index", "decision"],
        suffixes=("_audit", "_original"), validate="one_to_one")
    for name in ("H", "D_I", "D_I_norm", "D_I_loss", "H_S"):
        assert np.nanmax(np.abs(q11[f"{name}_audit"] - q11[f"{name}_original"])) < 1e-13
    assert (q11.action_id == q11.q11_action_id).all()
    support = pd.DataFrame(support_rows(states))
    marginals = marginal_rows(states)
    summaries = support_summaries(support)
    strata = stratified_rows(support)
    non_q11 = support[support.policy != "Q11"]
    # Pre-fixed conservative no-extrapolation decision rule.
    sufficient = bool(non_q11.covered_by_q11_spacing.all())
    tables = dict(states=states.to_dict("records"), support=support.to_dict("records"),
        marginals=marginals, summary=summaries, strata=strata)
    counts, metadata = persist_tables(iter([tables]), OUT, FILES)
    manifest = dict(
        audit_id="campaign2-state-coverage-audit-v1", base_commit=BASE_COMMIT,
        purpose="diagnostic suitability of Q11-only states for future C3 development",
        no_new_experiments=True, no_new_environment_transitions=True,
        input_sha256={"closed_loop_trajectories.csv.gz": digest(TRAJECTORIES),
            "reference_states.csv": digest(REFERENCE),
            "validation_summary.json": digest(INPUT / "validation_summary.json")},
        input_counts=dict(all_real_steps=92160, nonterminal_states=61440,
            nonterminal_states_per_policy=15360), policies=POLICIES,
        core_features=CORE, descriptor_features=list(FEATURE_SCALES),
        exact_strata=STRATUM, same_seed_q11_neighbour_excluded=True,
        distance="equal-weight RMS over primitive b[3] and S[6], all coordinates in [0,1]",
        operational_coverage=("nearest Q11 distance <= maximum Q11 leave-one-seed-out nearest-neighbour "
            "distance in the same scenario/configuration/problem/decision stratum"),
        criterion_status="diagnostic conservative non-extrapolation convention; not confirmatory threshold",
        coordinate_envelope="reported separately; not used for binary decision",
        binary_rule="SUFFICIENT only if every non-Q11 retained state satisfies the operational spacing criterion",
        counts=counts, persisted_file_metadata=metadata)
    dump(OUT / "execution_manifest.json", manifest)
    result = dict(classification="SUFFICIENT COVERAGE" if sufficient else "INSUFFICIENT COVERAGE",
        criterion=manifest["binary_rule"], non_q11_states=len(non_q11),
        uncovered_non_q11_states=int((non_q11.covered_by_q11_spacing == 0).sum()),
        policy_summary={row["policy"]: row for row in summaries if row["subset"] == "all"},
        action_disagreement_summary={row["policy"]: row for row in summaries
            if row["subset"] == "owner_action_differs_from_q11"},
        recommendation=("Q11-only retained states meet the conservative empirical support rule."
            if sufficient else "Use development-state coverage from all four frozen policies, rather than Q11 alone; "
                "do not design a new exploration policy from this audit."),
        limitations=["diagnostic empirical support, not population coverage proof",
            "finite 40-seed frozen test range and four capability configurations",
            "raw agent/capability coordinates preserve identity and are equally weighted",
            "derived descriptors are audited marginally but not double-counted in support distance",
            "no C3 selector or controller is designed or executed"])
    dump(OUT / "audit_summary.json", result)
    dump(OUT / "provenance.json", dict(base_commit=BASE_COMMIT,
        output_sha256={p.name: digest(p) for p in sorted(OUT.iterdir()) if p.is_file()},
        Campaign2_results_unchanged=True, Campaign3_executions=0))
    print(json.dumps({"classification": result["classification"], "counts": counts,
        "uncovered_non_q11_states": result["uncovered_non_q11_states"]}), flush=True)


if __name__ == "__main__":
    main()
