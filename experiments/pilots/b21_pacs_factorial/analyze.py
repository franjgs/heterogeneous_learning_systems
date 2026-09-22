"""Reproducible descriptive analysis of generated B2.1 validation results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
PAIRS = [(DOMAINS[i], DOMAINS[j]) for i in range(4) for j in range(i + 1, 4)]
COSTS = (0.00, 0.02, 0.05, 0.10, 0.15)
ZERO_TOL = 1e-12


def stats(values: pd.Series, prefix: str = "") -> dict[str, float | int]:
    x = values.astype(float).to_numpy()
    zero = np.abs(x) <= ZERO_TOL
    return {f"{prefix}mean": float(x.mean()), f"{prefix}std": float(x.std(ddof=1)), f"{prefix}min": float(x.min()), f"{prefix}max": float(x.max()), f"{prefix}n_positive": int((x > ZERO_TOL).sum()), f"{prefix}n_negative": int((x < -ZERO_TOL).sum()), f"{prefix}n_zero": int(zero.sum())}


def pair_key(i: str, j: str) -> str:
    return f"{i}-{j}"


def routing(row: pd.Series, state: str, cost: float) -> str:
    value = row[f"{state}_routing_c{cost:.2f}"]
    if not isinstance(value, str) or not value:
        raise ValueError(f"missing routing for {state}, c={cost}")
    data = json.loads(value)
    return ",".join(data[d] for d in DOMAINS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("results/pilots/b21_pacs_factorial"))
    args = parser.parse_args()
    out = args.input_dir / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    started = pd.Timestamp.now().timestamp()
    phase_times = []

    def phase(number: int, label: str) -> None:
        elapsed = pd.Timestamp.now().timestamp() - started
        eta = (elapsed / number * (7 - number)) if number else 0.0
        print(f"[{number}/7] {label} | elapsed {elapsed:.1f}s | ETA {max(0.0, eta):.1f}s", flush=True)
        phase_times.append(elapsed)

    phase(1, "Loading and consistency checks")
    factorial = pd.read_csv(args.input_dir / "factorial_results.csv")
    states = pd.read_csv(args.input_dir / "state_scores.csv")
    protocol = json.loads((args.input_dir / "protocol.json").read_text())

    if sorted(factorial.seed.unique().tolist()) != [0, 1, 2, 3, 4]:
        raise ValueError("expected exactly five seeds")
    if sorted(factorial.N.unique().tolist()) != [25, 50, 100]:
        raise ValueError("expected exactly N=25,50,100")
    observed_pairs = {(r["domain_i"], r["domain_j"]) for r in factorial.to_dict("records")}
    if observed_pairs != set(PAIRS):
        raise ValueError(f"unexpected pairs: {observed_pairs}")
    if len(factorial) != 90 or factorial.duplicated(["seed", "N", "domain_i", "domain_j"]).any():
        raise ValueError("expected 90 unique seed/N/pair rows")
    required_base = ["gamma_learn", "v_learn_F0", "v_learn_Fi", "v_learn_Fj", "v_learn_Fij"]
    for row in factorial.to_dict("records"):
        left, right = row["domain_i"], row["domain_j"]
        required = required_base[:]
        for state in ("F0", f"F_{left}", f"F_{right}", f"F_{left}_{right}"):
            required += [f"{state}_v_oper_c{c:.2f}" for c in COSTS]
            required += [f"{state}_routing_c{c:.2f}" for c in COSTS]
        values = row
        if any(pd.isna(values[column]) for column in required):
            raise ValueError(f"NaN in relevant factorial fields at {row['seed']}/{row['N']}/{left}-{right}")
    if any(factorial.astype(str).apply(lambda s: s.str.contains("test", case=False).any()).tolist()):
        raise ValueError("TEST-like value found in factorial results")
    if protocol.get("test_used") is not False or set(protocol["costs"]) != set(COSTS):
        raise ValueError("protocol metadata inconsistent")

    # Recompute both interaction definitions from the stored factorial values.
    gamma_check = factorial.v_learn_Fij - factorial.v_learn_Fi - factorial.v_learn_Fj + factorial.v_learn_F0
    if not np.allclose(gamma_check, factorial.gamma_learn, atol=1e-12, rtol=0):
        raise ValueError("Gamma_learn does not recompute from stored V_learn values")
    for c in COSTS:
        for row in factorial.to_dict("records"):
            left, right = row["domain_i"], row["domain_j"]
            values = row
            got = values[f"gamma_oper_c{c:.2f}"]
            expected = values[f"F_{left}_{right}_v_oper_c{c:.2f}"] - values[f"F_{left}_v_oper_c{c:.2f}"] - values[f"F_{right}_v_oper_c{c:.2f}"] + values[f"F0_v_oper_c{c:.2f}"]
            if not np.isclose(got, expected, atol=1e-12, rtol=0):
                raise ValueError(f"Gamma_oper mismatch at {row['seed']}/{row['N']}/{left}-{right}/c={c}")

    phase(2, "Gamma_learn analysis")
    phase(3, "Gamma_oper analysis")
    phase(4, "Routing reconstruction")
    learn_rows = []
    oper_rows = []
    routing_rows = []
    delta_rows = []
    for row in factorial.to_dict("records"):
        left, right = row["domain_i"], row["domain_j"]
        pair = pair_key(left, right)
        for c in COSTS:
            value = row[f"gamma_oper_c{c:.2f}"]
            oper_rows.append({"N": row["N"], "pair": pair, "c": c, "gamma_oper": value})
            delta_rows.append({"seed": row["seed"], "N": row["N"], "pair": pair, "c": c, "delta_gamma": value - row["gamma_learn"]})
            state_names = ["F0", f"F_{left}", f"F_{right}", f"F_{left}_{right}"]
            pats = {s: routing(pd.Series(row), s, c) for s in state_names}
            changes = {f"F0_to_{label}": sum(a != b for a, b in zip(pats["F0"].split(","), pats[state].split(","), strict=True)) for label, state in zip(("Fi", "Fj", "Fij"), state_names[1:], strict=True)}
            routing_rows.append({"seed": row["seed"], "N": row["N"], "pair": pair, "c": c, "routing_F0": pats["F0"], "routing_Fi": pats[state_names[1]], "routing_Fj": pats[state_names[2]], "routing_Fij": pats[state_names[3]], **changes, "Fij_pattern_new": pats[state_names[3]] not in {pats[state_names[1]], pats[state_names[2]]}, "total_routing_changes": sum(changes.values()), "gamma_oper": value})
    for n in sorted(factorial.N.unique()):
        print(f"Gamma_learn: N={n} ({list(sorted(factorial.N.unique())).index(n)+1}/3)", flush=True)
    # Aggregate all five seed values explicitly.
    learn = factorial.groupby(["N", "domain_i", "domain_j"], as_index=False).gamma_learn.agg(list)
    learn_rows = []
    for r in learn.itertuples(index=False):
        learn_rows.append({"N": r.N, "pair": pair_key(r.domain_i, r.domain_j), **stats(pd.Series(r.gamma_learn))})
    pd.DataFrame(learn_rows).to_csv(out / "gamma_learn_by_pair.csv", index=False)
    oper = pd.DataFrame(oper_rows)
    oper_summary = []
    for (n, pair, c), group in oper.groupby(["N", "pair", "c"]):
        s = stats(group.gamma_oper)
        oper_summary.append({"N": n, "pair": pair, "c": c, "mean_gamma_oper": s["mean"], "std_gamma_oper": s["std"], "min": s["min"], "max": s["max"], "n_positive": s["n_positive"], "n_negative": s["n_negative"], "n_zero": s["n_zero"]})
    for index, (n, c) in enumerate(( (n, c) for n in sorted(factorial.N.unique()) for c in COSTS), 1):
        print(f"Gamma_oper: N={n}, c={c:.2f} ({index}/15)", flush=True)
    pd.DataFrame(oper_summary).to_csv(out / "gamma_oper_by_pair.csv", index=False)
    routing_df = pd.DataFrame(routing_rows)
    routing_df.to_csv(out / "routing_analysis.csv", index=False)
    delta = pd.DataFrame(delta_rows)
    delta_summary = delta.groupby(["N", "pair", "c"], as_index=False).delta_gamma.agg(["mean", "std", "median", "min", "max"]).reset_index()
    delta_summary.to_csv(out / "delta_gamma.csv", index=False)
    for index, (n, c) in enumerate(((n, c) for n in sorted(factorial.N.unique()) for c in COSTS), 1):
        print(f"Routing: N={n}, c={c:.2f} ({index}/15)", flush=True)
    routing_df["routing_change"] = routing_df.total_routing_changes > 0
    phase(5, "Routing vs Gamma analysis")
    rv = routing_df.groupby(["N", "pair", "c", "routing_change"], as_index=False).gamma_oper.agg(["count", "mean", "std", "median", "min", "max"]).reset_index()
    rv["std"] = rv["std"].fillna(0.0)
    rv.to_csv(out / "routing_vs_gamma.csv", index=False)

    phase(6, "Representative cases and figures")
    # Objective representative-case rules, with full factorial values and routing.
    learn_summary = pd.DataFrame(learn_rows)
    op_summary = pd.DataFrame(oper_summary)
    cases = []
    def add_case(label, n, pair, c=None):
        left, right = pair.split("-")
        subset = factorial[(factorial.N == n) & (factorial.domain_i == left) & (factorial.domain_j == right)]
        row = subset.iloc[0]
        states = {"F0": float(subset.v_learn_F0.mean()), f"F_{left}": float(subset.v_learn_Fi.mean()), f"F_{right}": float(subset.v_learn_Fj.mean()), f"F_{left}_{right}": float(subset.v_learn_Fij.mean())}
        rec = {"case": label, "N": n, "pair": pair, "c": c, "seed_for_routing": int(row.seed), "V_F0": states["F0"], "V_Fi": states[f"F_{left}"], "V_Fj": states[f"F_{right}"], "V_Fij": states[f"F_{left}_{right}"]}
        if c is None:
            rec["gamma"] = states[f"F_{left}_{right}"] - states[f"F_{left}"] - states[f"F_{right}"] + states["F0"]
        else:
            rec["V_oper_F0"] = float(subset[f"F0_v_oper_c{c:.2f}"].mean()); rec["V_oper_Fi"] = float(subset[f"F_{left}_v_oper_c{c:.2f}"].mean()); rec["V_oper_Fj"] = float(subset[f"F_{right}_v_oper_c{c:.2f}"].mean()); rec["V_oper_Fij"] = float(subset[f"F_{left}_{right}_v_oper_c{c:.2f}"].mean()); rec["gamma"] = rec["V_oper_Fij"] - rec["V_oper_Fi"] - rec["V_oper_Fj"] + rec["V_oper_F0"]
            rec["routing_F0"] = row[f"F0_routing_c{c:.2f}"]; rec["routing_Fi"] = row[f"F_{left}_routing_c{c:.2f}"]; rec["routing_Fj"] = row[f"F_{right}_routing_c{c:.2f}"]; rec["routing_Fij"] = row[f"F_{left}_{right}_routing_c{c:.2f}"]
        cases.append(rec)
    pos = learn_summary.loc[learn_summary["mean"] > ZERO_TOL].sort_values(["mean", "N", "pair"], ascending=[False, True, True]).iloc[0]
    low = learn_summary.sort_values(["mean", "N", "pair"]).iloc[0]
    add_case("largest_mean_gamma_learn_positive", int(pos.N), pos.pair)
    add_case("smallest_mean_gamma_learn", int(low.N), low.pair)
    op_pos = op_summary.loc[op_summary.mean_gamma_oper > ZERO_TOL].sort_values(["mean_gamma_oper", "N", "pair", "c"], ascending=[False, True, True, True]).iloc[0]
    op_low = op_summary.sort_values(["mean_gamma_oper", "N", "pair", "c"]).iloc[0]
    add_case("largest_mean_gamma_oper_positive", int(op_pos.N), op_pos.pair, float(op_pos.c))
    add_case("smallest_mean_gamma_oper", int(op_low.N), op_low.pair, float(op_low.c))
    dg = delta.assign(abs_delta=delta.delta_gamma.abs()).groupby(["N", "pair", "c"], as_index=False).abs_delta.mean().sort_values(["abs_delta", "N", "pair", "c"], ascending=[False, True, True, True]).iloc[0]
    add_case("largest_abs_delta_gamma", int(dg.N), dg.pair, float(dg.c))
    signs = op_summary.merge(learn_summary[["N", "pair", "mean"]], on=["N", "pair"])
    changed = signs[(signs.mean_gamma_oper * signs["mean"] < 0)].sort_values(["N", "pair", "c"])
    if len(changed):
        x = changed.iloc[0]; add_case("sign_change_learn_vs_oper", int(x.N), x.pair, float(x.c))
    pd.DataFrame(cases).to_csv(out / "representative_cases.csv", index=False)

    routing_change = routing_df.groupby(["N", "pair", "c"], as_index=False).routing_change.mean()
    summary = ["# B2.1 PACS factorial analysis", "", f"Controls passed: 5 seeds, 3 N, 6 pairs, 5 costs; 90 factorial rows; Gamma values recomputed from stored values; no TEST values detected. Zero tolerance: {ZERO_TOL:g}.", "", f"Gamma_learn mean range: {learn_summary['mean'].min():.6f} to {learn_summary['mean'].max():.6f} across N/pairs."]
    for n in sorted(learn_summary.N.unique()):
        g = learn_summary[learn_summary.N == n]; summary.append(f"N={n}: positive pair means {int((g['mean']>ZERO_TOL).sum())}/6; negative {int((g['mean']<-ZERO_TOL).sum())}/6.")
    learn_consistent_pos = [f"N={r.N} {r.pair}" for r in learn_summary.itertuples() if r.n_positive == 5]
    learn_consistent_neg = [f"N={r.N} {r.pair}" for r in learn_summary.itertuples() if r.n_negative == 5]
    op_consistent_pos = [f"N={r.N} {r.pair} c={r.c:.2f}" for r in op_summary.itertuples() if r.n_positive == 5]
    op_consistent_neg = [f"N={r.N} {r.pair} c={r.c:.2f}" for r in op_summary.itertuples() if r.n_negative == 5]
    flips = int((signs.mean_gamma_oper * signs["mean"] < 0).sum())
    routing_group = routing_df.assign(changed=routing_df.total_routing_changes > 0).groupby("changed").gamma_oper.agg(["count", "mean", "std", "median", "min", "max"])
    trend_lines = []
    for pair, group in learn_summary.groupby("pair"):
        values = group.sort_values("N")["mean"].abs().tolist()
        trend = "crece" if values[0] < values[1] < values[2] else "decrece" if values[0] > values[1] > values[2] else "sin patrón consistente"
        trend_lines.append(f"{pair}: |Gamma_learn| {trend} ({', '.join(f'{v:.3f}' for v in values)}).")
    summary += [
        "",
        f"Consistent Gamma_learn complementarity (5/5 positive): {', '.join(learn_consistent_pos) or 'none'}.",
        f"Consistent Gamma_learn substitution (5/5 negative): {', '.join(learn_consistent_neg) or 'none'}.",
        f"Consistent Gamma_oper complementarity: {', '.join(op_consistent_pos) or 'none'}.",
        f"Consistent Gamma_oper substitution: {', '.join(op_consistent_neg) or 'none'}.",
        f"Mean-sign changes between Gamma_learn and Gamma_oper: {flips} of {len(signs)} N/pair/c cells.",
        f"Routing-change observations: {routing_group.to_dict('index')}.",
        "Magnitud |Gamma_learn| por par y N:",
        *trend_lines,
        "Routing-change comparisons are descriptive; they do not identify a causal routing effect. See routing_vs_gamma.csv and delta_gamma.csv.",
        "",
        "B2.1 supports descriptive evidence about pairwise validation interactions and their dependence on N and the fixed operational cost grid. It does not establish inferential significance, global HLS superiority, development costs, TEST performance, or B2.2 claims.",
    ]
    phase(7, "Writing outputs and validation")
    (out / "analysis_summary.md").write_text("\n".join(summary) + "\n")


if __name__ == "__main__":
    main()
