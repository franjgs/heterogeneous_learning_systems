"""Independent audit and diagnostic reporting for completed B2.2 results."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
SEEDS = (0, 1, 2, 3, 4)
N_VALUES = (25, 50, 100)
COSTS = (0.00, 0.02, 0.05, 0.10, 0.15)
FUTURE_WEIGHTS = (1, 2, 5, 10)
TOLERANCE = 1e-12
FROZEN_COUNTS = {
    "favorable": 4,
    "noncompensating": 800,
    "reproducible_favorable_cells": 0,
    "decision_changes": 4,
    "positive_cross_domain_cases": 0,
    "frontier_checks": 1200,
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _close(actual: pd.Series | np.ndarray, expected: pd.Series | np.ndarray, label: str) -> None:
    _require(bool(np.allclose(np.asarray(actual, float), np.asarray(expected, float), atol=TOLERANCE, rtol=0)), f"{label} does not reproduce")


def audit_results(
    raw: pd.DataFrame,
    update_dir: Path | None,
    metadata_path: Path,
    expected_counts: dict[str, int] | None = None,
) -> dict[str, object]:
    """Recalculate every primary quantity and enforce the frozen completed-run facts."""
    keys = ["seed", "domain", "N", "c", "B"]
    _require(len(raw) == 1200 and not raw.duplicated(keys).any(), "expected 1,200 unique analytical rows")
    _require(raw.update_id.nunique() == 60, "expected 60 unique opportunity updates")
    _require(set(raw.seed) == set(SEEDS), "seed grid differs")
    _require(set(raw.domain) == set(DOMAINS), "domain grid differs")
    _require(set(raw.N) == set(N_VALUES), "N grid differs")
    _require(set(raw.c) == set(COSTS), "cost grid differs")
    _require(set(raw.B) == set(FUTURE_WEIGHTS), "B grid differs")
    _require(set(raw.kappa) == {0.0}, "kappa must be zero")
    _require(not any("test" in column.lower() for column in raw.columns), "raw results expose TEST")

    metadata = json.loads(metadata_path.read_text())
    _require(metadata.get("device") == "cpu", "completed run was not CPU")
    _require(metadata.get("test_used") is False, "run metadata reports TEST use")
    if update_dir is not None:
        artifacts = [json.loads(path.read_text()) for path in sorted(update_dir.glob("*.json"))]
        _require(len(artifacts) == 60, "expected 60 incremental update artifacts")
        artifact_ids = [str(record["metadata"]["update_id"]) for record in artifacts]
        _require(len(set(artifact_ids)) == 60 and set(artifact_ids) == set(raw.update_id), "incremental updates do not match raw results")
        for record in artifacts:
            n = int(record["metadata"]["N"])
            _require(record["metadata"].get("device") == "cpu", "an update was not produced on CPU")
            _require(record.get("test_used") is False and record.get("evaluated_split") == "validation", "an update used a non-validation split")
            _require(record.get("parent_state") == "F0", "an update was not direct from F0")
            fast, deep = record["fast_trajectory"], record["deep_trajectory"]
            _require(fast["teacher_query_count"] == fast["pseudo_label_count"] == 0, "Fast trajectory accessed teacher labels")
            _require(deep["teacher_query_count"] == deep["pseudo_label_count"] == n, "Deep opportunity did not use exactly N pseudo-labels")

    f0 = np.column_stack([raw[f"F0_ba_{domain}"] for domain in DOMAINS])
    fk = np.column_stack([raw[f"Fk_ba_{domain}"] for domain in DOMAINS])
    deep = np.column_stack([raw[f"D_ba_{domain}"] for domain in DOMAINS])
    cost = raw.c.to_numpy()[:, None]
    selected = np.array([DOMAINS.index(domain) for domain in raw.domain])
    rho = f0[np.arange(len(raw)), selected] - (deep[np.arange(len(raw)), selected] - raw.c.to_numpy())
    v_f0 = np.maximum(f0, deep - cost).mean(axis=1)
    v_fk = np.maximum(fk, deep - cost).mean(axis=1)
    delta_v = v_fk - v_f0
    contributions = 0.25 * (np.maximum(fk, deep - cost) - np.maximum(f0, deep - cost))
    local = contributions[np.arange(len(raw)), selected]
    cross = contributions.sum(axis=1) - local
    omega = raw.B.to_numpy() * delta_v
    h_value = -rho + omega
    favorable = (rho > 0) & (h_value > 0)
    frontier = (rho > 0) & (raw.B.to_numpy() * delta_v > rho)
    for values, column in ((rho, "rho"), (v_f0, "V_F0"), (v_fk, "V_Fk"), (delta_v, "DeltaV"), (omega, "Omega"), (h_value, "H"), (local, "DeltaV_local"), (cross, "DeltaV_cross")):
        _close(values, raw[column], column)
    for index, domain in enumerate(DOMAINS):
        _close(contributions[:, index], raw[f"DeltaV_contribution_{domain}"], f"DeltaV contribution {domain}")
    _close(delta_v, local + cross, "DeltaV decomposition")
    _require(np.array_equal(favorable, raw.integration_changes_decision.astype(bool)), "primary decision indicator does not reproduce")
    _require(np.array_equal(favorable, frontier), "strict frontier equivalence failed")

    cells = raw.assign(_favorable=favorable).groupby(["domain", "N", "c", "B"])._favorable.sum()
    noncomp_cells = raw.assign(_noncomp=(rho > 0) & (h_value <= 0)).groupby(["domain", "N", "c", "B"])._noncomp.sum()
    counts = {
        "favorable": int(favorable.sum()),
        "noncompensating": int(((rho > 0) & (h_value <= 0)).sum()),
        "reproducible_favorable_cells": int((cells >= 2).sum()),
        "decision_changes": int(raw.integration_changes_decision.sum()),
        "positive_cross_domain_cases": int(((delta_v > 0) & (cross > 0)).sum()),
        "frontier_checks": int(np.equal(favorable, frontier).sum()),
    }
    if expected_counts is not None:
        _require(counts == expected_counts, f"frozen B2.2 counts differ: {counts}")
    reproducible_favorable = bool((cells >= 2).any())
    reproducible_noncompensating = bool((noncomp_cells >= 2).any())
    classification = "POSITIVE" if reproducible_favorable and reproducible_noncompensating else "NULL" if counts["favorable"] == 0 else "INCONCLUSIVE"
    return {**counts, "updates": 60, "rows": 1200, "cells": 240, "classification": classification, "test": "CLOSED", "device": "cpu"}


def _unique_delta_v(raw: pd.DataFrame) -> pd.DataFrame:
    keys = ["seed", "domain", "N", "c"]
    columns = ["DeltaV", "DeltaV_local", "DeltaV_cross"] + [f"DeltaV_contribution_{d}" for d in DOMAINS]
    for _, group in raw.groupby(keys):
        _require(all(group[column].max() - group[column].min() <= TOLERANCE for column in columns), "DeltaV changed with B")
    return raw.sort_values("B").drop_duplicates(keys).copy()


def _unique_updates(raw: pd.DataFrame) -> pd.DataFrame:
    keys = ["seed", "domain", "N"]
    score_columns = [f"{state}_ba_{domain}" for state in ("F0", "Fk", "D") for domain in DOMAINS]
    for _, group in raw.groupby(keys):
        _require(all(group[column].max() - group[column].min() <= TOLERANCE for column in score_columns), "competence scores changed over the analytical grid")
    return raw.sort_values(["c", "B"]).drop_duplicates(keys).copy()


def _stats(values: pd.Series) -> dict[str, object]:
    array = values.to_numpy(dtype=float)
    return {
        "n": len(array), "mean": array.mean(), "std": array.std(ddof=1) if len(array) > 1 else 0.0,
        "median": np.median(array), "min": array.min(), "max": array.max(),
        "n_positive": int((array > TOLERANCE).sum()), "n_zero": int((np.abs(array) <= TOLERANCE).sum()),
        "n_negative": int((array < -TOLERANCE).sum()), "fraction_positive": float((array > TOLERANCE).mean()),
        "fraction_zero": float((np.abs(array) <= TOLERANCE).mean()), "fraction_negative": float((array < -TOLERANCE).mean()),
    }


def delta_v_summaries(raw: pd.DataFrame) -> pd.DataFrame:
    """Summarize 300 unique seed/domain/N/c realizations, never the four B copies."""
    unique = _unique_delta_v(raw)
    rows: list[dict[str, object]] = []
    groupings = [("global", [], [((), unique)]), ("domain_N", ["domain", "N"], list(unique.groupby(["domain", "N"], sort=False))), ("N", ["N"], list(unique.groupby("N", sort=True))), ("c", ["c"], list(unique.groupby("c", sort=True)))]
    for scope, names, groups in groupings:
        for key, group in groups:
            keys = key if isinstance(key, tuple) else (key,)
            base = {"scope": scope, "domain": "ALL", "N": "ALL", "c": "ALL"}
            base.update(dict(zip(names, keys)))
            for metric in ("DeltaV", "DeltaV_local", "DeltaV_cross"):
                rows.append({**base, "metric": metric, **_stats(group[metric])})
    return pd.DataFrame(rows)


def competence_change_summaries(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    updates = _unique_updates(raw)
    detail: list[dict[str, object]] = []
    for row in updates.itertuples(index=False):
        for affected in DOMAINS:
            detail.append({"seed": row.seed, "intervention_domain": row.domain, "N": row.N, "affected_domain": affected, "DeltaS": getattr(row, f"Fk_ba_{affected}") - getattr(row, f"F0_ba_{affected}"), "is_local": affected == row.domain})
    detail_frame = pd.DataFrame(detail)
    summaries: list[dict[str, object]] = []
    for scope, names, groups in (
        ("matrix_all_N", ["intervention_domain", "affected_domain"], detail_frame.groupby(["intervention_domain", "affected_domain"], sort=False)),
        ("matrix_by_N", ["N", "intervention_domain", "affected_domain"], detail_frame.groupby(["N", "intervention_domain", "affected_domain"], sort=False)),
    ):
        for key, group in groups:
            keys = key if isinstance(key, tuple) else (key,)
            summaries.append({"scope": scope, "N": "ALL", **dict(zip(names, keys)), **_stats(group.DeltaS)})
    return detail_frame, pd.DataFrame(summaries)


def favorable_cases(raw: pd.DataFrame) -> pd.DataFrame:
    selected = raw[(raw.rho > 0) & (raw.H > 0)].copy()
    selected["distance_to_H0"] = selected.H.abs()
    columns = ["update_id", "seed", "domain", "N", "c", "B", "rho", "DeltaV", "Omega", "H", "distance_to_H0", "S_F0", "S_Fk", "S_D", "DeltaV_local", "DeltaV_cross"]
    columns += [f"DeltaV_contribution_{domain}" for domain in DOMAINS]
    columns += ["current_preferred_action", "total_value_preferred_action"]
    return selected[columns].sort_values(["seed", "domain", "N", "c", "B"]).reset_index(drop=True)


def bottleneck_summary(raw: pd.DataFrame) -> pd.DataFrame:
    unique = _unique_delta_v(raw)
    rho = unique[unique.rho > 0]
    positive = rho[rho.DeltaV > TOLERANCE]
    updates = _unique_updates(raw)
    masked = total_changed = 0
    for row in unique.itertuples(index=False):
        for domain in DOMAINS:
            delta_s = getattr(row, f"Fk_ba_{domain}") - getattr(row, f"F0_ba_{domain}")
            if abs(delta_s) > TOLERANCE:
                total_changed += 1
                masked += abs(getattr(row, f"DeltaV_contribution_{domain}")) <= TOLERANCE
    cross_detail, _ = competence_change_summaries(raw)
    cross = cross_detail[~cross_detail.is_local]
    rows = [
        ("rho_positive_unique", len(rho), len(unique), "current Fast-preferred seed/domain/N/c realizations"),
        ("DeltaV_positive_unique", int((unique.DeltaV > TOLERANCE).sum()), len(unique), "positive future-value changes; B copies removed"),
        ("rho_positive_and_DeltaV_positive", len(positive), len(unique), "positive opportunity value where current sacrifice exists"),
        ("positive_DeltaV_compensates_at_B10", int((10 * positive.DeltaV > positive.rho).sum()), len(positive), "positive candidates that cross the frozen largest-B frontier"),
        ("cross_domain_DeltaS_negative", int((cross.DeltaS < -TOLERANCE).sum()), len(cross), "negative nonlocal competence changes"),
        ("routing_masked_nonzero_DeltaS", int(masked), int(total_changed), "nonzero competence changes with zero operational-value contribution"),
        ("favorable_distinct_updates", raw[raw.integration_changes_decision].update_id.nunique(), 60, "distinct learned states among favorable analytical rows"),
        ("favorable_seeds", raw[raw.integration_changes_decision].seed.nunique(), 5, "seeds represented among favorable rows"),
    ]
    return pd.DataFrame(rows, columns=["metric", "count", "denominator", "definition"])


def _markdown(frame: pd.DataFrame, digits: int = 6) -> str:
    view = frame.copy()
    for column in view.select_dtypes(include=["float"]).columns:
        view[column] = view[column].map(lambda value: f"{value:.{digits}f}")
    header = "| " + " | ".join(map(str, view.columns)) + " |"
    rule = "| " + " | ".join(["---"] * len(view.columns)) + " |"
    body = ["| " + " | ".join(map(str, row)) + " |" for row in view.itertuples(index=False, name=None)]
    return "\n".join([header, rule, *body])


def diagnostic_markdown(raw: pd.DataFrame, audit: dict[str, object], delta: pd.DataFrame, competence: pd.DataFrame, bottlenecks: pd.DataFrame) -> str:
    unique = _unique_delta_v(raw)
    updates = _unique_updates(raw)
    for domain in DOMAINS:
        updates[f"DeltaS_{domain}"] = updates[f"Fk_ba_{domain}"] - updates[f"F0_ba_{domain}"]
    updates["DeltaS_local"] = [row[f"DeltaS_{row.domain}"] for _, row in updates.iterrows()]
    updates["DeltaS_cross_mean"] = [np.mean([row[f"DeltaS_{domain}"] for domain in DOMAINS if domain != row.domain]) for _, row in updates.iterrows()]
    favorable = favorable_cases(raw)
    favor_view = favorable[["seed", "domain", "N", "c", "B", "rho", "DeltaV", "Omega", "H", "DeltaV_local", "DeltaV_cross"]]
    favorable_details = []
    for row in favorable.itertuples(index=False):
        contributions = ", ".join(f"{domain}={getattr(row, f'DeltaV_contribution_{domain}'):.6f}" for domain in DOMAINS)
        favorable_details.append(
            f"- `seed={row.seed}, {row.domain}, N={row.N}, c={row.c:.2f}, B={row.B}`: "
            f"S(F0)={row.S_F0}; S(F_k)={row.S_Fk}; S(D)={row.S_D}; "
            f"contributions [{contributions}]; actions {row.current_preferred_action} -> {row.total_value_preferred_action}."
        )
    global_delta = delta[(delta.scope == "global")][["metric", "n", "mean", "std", "median", "min", "max", "fraction_positive", "fraction_zero", "fraction_negative"]]
    matrix = competence[(competence.scope == "matrix_all_N")][["intervention_domain", "affected_domain", "mean", "std", "n_positive", "n_zero", "n_negative"]]
    n_rows = []
    for n in N_VALUES:
        dv = unique[unique.N == n]
        ds = updates[updates.N == n]
        h = raw[(raw.N == n) & (raw.rho > 0)]
        n_rows.append({"N": n, "mean_DeltaS_local": ds.DeltaS_local.mean(), "mean_DeltaS_cross": ds.DeltaS_cross_mean.mean(), "mean_DeltaV": dv.DeltaV.mean(), "positive_DeltaV_fraction": (dv.DeltaV > TOLERANCE).mean(), "mean_H_given_rho_positive": h.H.mean(), "favorable_rows": int((h.H > 0).sum())})
    c_rows = []
    for cost in COSTS:
        group = unique[np.isclose(unique.c, cost)]
        raw_group = raw[np.isclose(raw.c, cost)]
        c_rows.append({"c": cost, "rho_positive_updates": int((group.rho > 0).sum()), "mean_DeltaV": group.DeltaV.mean(), "DeltaV_positive_updates": int((group.DeltaV > TOLERANCE).sum()), "favorable_rows": int(((raw_group.rho > 0) & (raw_group.H > 0)).sum())})
    b_rows = []
    for weight in FUTURE_WEIGHTS:
        group = raw[raw.B == weight]
        b_rows.append({"B": weight, "rho_positive": int((group.rho > 0).sum()), "favorable": int(((group.rho > 0) & (group.H > 0)).sum())})
    return f"""# B2.2 diagnostic

## 1. Validation

The independent reconstruction verified 60 unique opportunity updates and 1,200 unique analytical rows: five seeds, four domains, `N={{25,50,100}}`, `c={{0,.02,.05,.10,.15}}`, `B={{1,2,5,10}}`, and `kappa=0`. All incremental artifacts report CPU, direct-from-F0 updates, VALIDATION evaluation, no TEST use, zero teacher queries on the Fast trajectory, and exactly N teacher queries/pseudo-labels on the Deep trajectory. Recomputed `rho`, `V_F0`, `V_Fk`, `DeltaV`, `Omega`, `H`, the strict primary event, and every contribution agree within {TOLERANCE:g}. The decomposition and all {audit['frontier_checks']}/1200 frontier checks pass.

## 2. Frozen classification

**INCONCLUSIVE.** There are {audit['favorable']}/1200 observations with `rho>0,H>0`, so the frozen NULL criterion (no such observation anywhere) does not apply. None of the 240 domain/N/c/B cells has favorable results in at least two seeds, so the frozen POSITIVE criterion does not apply. There are {audit['noncompensating']}/1200 observations with `rho>0,H<=0`. “NULL” is the protocol's exact no-favorable-observation outcome; it does not mean “the mechanism is rare.”

## 3. Four favorable cases

{_markdown(favor_view)}

{chr(10).join(favorable_details)}

All four analytical observations are `seed=4`, intervention `cartoon`, and `c=.02`; they represent only two learned states (`N=25` and `N=50`). The `N=25` state crosses at `B=2,5,10`; the `N=50` state only at `B=10`. Their distances from the exact frontier are their positive H values shown above. They are non-reproduced across seeds; the nearest is marginal (`H=0.001409`), while even the largest margin does not establish robustness.

## 4. DeltaV analysis

The following uses the 300 unique seed/domain/N/c realizations and removes the four identical B copies of each `DeltaV`.

{_markdown(global_delta)}

`DeltaV` is negative in 283/300 (94.33%), zero in 10/300, and positive in 7/300. Thus these singleton updates normally reduce future operational value in this grid. Positive `DeltaV` never coincides with a positive cross-domain contribution (0/300 unique realizations; equivalently 0/1200 analytical rows). The full domain-by-N summaries are in `b22_deltaV_summary.csv`.

## 5. Competence-change matrix

Entries pool five seeds and three N values (15 updates per intervention/affected-domain cell).

{_markdown(matrix)}

The updates combine occasional local improvement with broad interference/forgetting. Across all 240 competence changes, 34 are positive and 206 negative. Nonlocal changes are negative in 165/180 cases. Operational routing masks 372/1200 nonzero competence changes at a particular c, but does not rescue the prevalent negative cross-domain changes. The per-N matrix in `b22_competence_changes.csv` reports signs across the five seeds separately for every N.

## 6. Effect of N

{_markdown(pd.DataFrame(n_rows))}

More pseudo-labels do not increase useful learning in these aggregates. From N=25 to 50 to 100, mean local competence change falls from -0.006972 to -0.047547 to -0.069836; mean nonlocal change per affected domain falls from -0.064352 to -0.154787 to -0.206948; and mean `DeltaV` falls from -0.021649 to -0.036810 to -0.041729. The aggregate deterioration is monotone over the three frozen N values, and favorable rows fall from 3 to 1 to 0.

## 7. Effect of c

{_markdown(pd.DataFrame(c_rows))}

Increasing c both increases the number of currently Fast-preferred cases and changes which Fast competencies are exposed by the future max. The first effect raises `rho>0` from 18/60 at c=0 to 60/60 at c=.10 and .15. The second makes mean `DeltaV` progressively more negative, from -0.010490 at c=0 to -0.069206 at c=.15, because more of F's degraded competence enters future value. Favorable events occur only at c=.02.

## 8. Effect of B

{_markdown(pd.DataFrame(b_rows))}

B leaves learning and `DeltaV` unchanged and only scales `Omega=B DeltaV`. The four favorable observations occur at B=2 (one), B=5 (one), and B=10 (two); none occurs at B=1. These are repeated valuations of two learned states, not four independent learning outcomes.

## 9. Why B2.2 was inconclusive

{_markdown(bottlenecks)}

The dominant bottleneck is not a shortage of current-sacrifice cases: 201/300 unique c-valuations have `rho>0`. It is the absolute opportunity value: only 7/300 have positive `DeltaV`, only 5/300 combine positive `DeltaV` with `rho>0`, and only 2/5 of those compensate `rho` at the largest frozen B. Broad cross-domain degradation is the main empirical component of negative `DeltaV`; routing additionally masks some competence changes. Favorable outcomes occur in one seed only, so seed reproducibility is also absent.

## 10. Relation to B2.1

B2.1 found positive mean `Gamma_learn` in all 18 N-by-pair cells and measured a second difference between singleton and direct joint updates. B2.2 asks a different question: whether the absolute value of one singleton opportunity is large enough to pay a present operational sacrifice. Strong factorial interaction can coexist with weak or negative absolute singleton value. The results therefore distinguish interaction value from absolute opportunity value and are not contradictory.

## 11. Implications for RQ0

The event required by the proposed mechanism occurs in two learned states and four analytical valuations, but it fails the preregistered reproducibility criterion. B2.2 therefore does not yet provide sufficient support for `operation -> learning opportunity -> competence change -> future operational value`. It neither establishes nor refutes RQ0, does not show HLS superiority, and contains no TEST evidence.

## 12. What remains unresolved

The completed grid does not establish that an ex-ante policy can predict opportunity value, that the favorable event generalizes across seeds, or that its operational association is causal beyond the defined intervention. The relative roles of singleton-update learning dynamics, cross-domain interference, and future routing remain descriptive here.
"""


def write_diagnostics(raw: pd.DataFrame, output_dir: Path, audit: dict[str, object]) -> dict[str, pd.DataFrame]:
    delta = delta_v_summaries(raw)
    _, competence = competence_change_summaries(raw)
    favorable = favorable_cases(raw)
    bottlenecks = bottleneck_summary(raw)
    favorable.to_csv(output_dir / "b22_favorable_cases.csv", index=False)
    delta.to_csv(output_dir / "b22_deltaV_summary.csv", index=False)
    competence.to_csv(output_dir / "b22_competence_changes.csv", index=False)
    bottlenecks.to_csv(output_dir / "b22_bottleneck_summary.csv", index=False)
    (output_dir / "b22_diagnostic.md").write_text(diagnostic_markdown(raw, audit, delta, competence, bottlenecks))
    return {"favorable": favorable, "delta": delta, "competence": competence, "bottlenecks": bottlenecks}
