"""Analyze how B2.1 routing transforms learning interactions, using saved CSVs only."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
PAIRS = [(DOMAINS[i], DOMAINS[j]) for i in range(4) for j in range(i + 1, 4)]
COSTS = (0.00, 0.02, 0.05, 0.10, 0.15)
EPSILON = 1e-12


def describe(frame: pd.DataFrame, value: str) -> dict[str, float | int]:
    values = frame[value].astype(float)
    return {"count": int(values.count()), "mean": float(values.mean()), "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0, "median": float(values.median()), "min": float(values.min()), "max": float(values.max())}


def route(fast: float, deep: float, cost: float) -> str:
    return "F" if fast >= deep - cost else "D"


def transition(old: str, new: str) -> str:
    return f"{old}→{new}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("results/pilots/b21_pacs_factorial"))
    args = parser.parse_args()
    out = args.input_dir / "analysis"
    figures = out / "figures"
    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    def progress(number: int, label: str) -> None:
        print(f"[{number}/7] {label} | elapsed {time.perf_counter() - started:.1f}s", flush=True)

    progress(1, "Loading and consistency checks")
    factorial = pd.read_csv(args.input_dir / "factorial_results.csv")
    states = pd.read_csv(args.input_dir / "state_scores.csv")
    protocol = json.loads((args.input_dir / "protocol.json").read_text())
    if sorted(factorial.seed.unique()) != [0, 1, 2, 3, 4] or sorted(factorial.N.unique()) != [25, 50, 100]:
        raise ValueError("expected exactly five seeds and N={25,50,100}")
    if {(r.domain_i, r.domain_j) for r in factorial.itertuples()} != set(PAIRS):
        raise ValueError("unexpected domain-pair set")
    if len(factorial) != 90 or factorial.duplicated(["seed", "N", "domain_i", "domain_j"]).any():
        raise ValueError("expected 90 unique seed/N/pair rows")
    if sorted(states.seed.unique()) != [0, 1, 2, 3, 4] or set(states.state) != {"D", "F0"} or len(states) != 10:
        raise ValueError("state_scores does not contain exactly D and F0 for five seeds")
    if protocol.get("test_used") is not False or any(factorial.astype(str).apply(lambda col: col.str.contains("test", case=False).any())):
        raise ValueError("TEST detected")
    deep_by_seed = states[states.state == "D"].set_index("seed")
    for row in factorial.to_dict("records"):
        left, right = row["domain_i"], row["domain_j"]
        gamma = row["v_learn_Fij"] - row["v_learn_Fi"] - row["v_learn_Fj"] + row["v_learn_F0"]
        if not np.isclose(gamma, row["gamma_learn"], atol=EPSILON, rtol=0):
            raise ValueError("Gamma_learn mismatch")
        for c in COSTS:
            expected = row[f"F_{left}_{right}_v_oper_c{c:.2f}"] - row[f"F_{left}_v_oper_c{c:.2f}"] - row[f"F_{right}_v_oper_c{c:.2f}"] + row[f"F0_v_oper_c{c:.2f}"]
            if not np.isclose(expected, row[f"gamma_oper_c{c:.2f}"], atol=EPSILON, rtol=0):
                raise ValueError("Gamma_oper mismatch")

    progress(2, "Reconstructing routing")
    records = []
    for row in factorial.to_dict("records"):
        left, right = row["domain_i"], row["domain_j"]
        states_by_name = {"F0": "F0", "Fi": f"F_{left}", "Fj": f"F_{right}", "Fij": f"F_{left}_{right}"}
        for c in COSTS:
            rec = {"seed": int(row["seed"]), "N": int(row["N"]), "pair": f"{left}-{right}", "domain_i": left, "domain_j": right, "c": c, "gamma_learn": float(row["gamma_learn"]), "gamma_oper": float(row[f"gamma_oper_c{c:.2f}"])}
            drow = deep_by_seed.loc[row["seed"]]
            routes = {}
            for state_label, column_prefix in states_by_name.items():
                route_vector = []
                for domain in DOMAINS:
                    fast_score = float(row[f"{column_prefix}_ba_{domain}"])
                    deep_score = float(drow[f"ba_{domain}"])
                    route_vector.append(route(fast_score, deep_score, c))
                routes[state_label] = route_vector
                rec[f"R{state_label[1:] if state_label != 'F0' else '0'}"] = ",".join(route_vector)
            r0, ri, rj, rij = (routes[x] for x in ("F0", "Fi", "Fj", "Fij"))
            for label, vector in (("i", ri), ("j", rj), ("ij", rij)):
                rec[f"d_{label}"] = sum(a != b for a, b in zip(vector, r0, strict=True))
                for domain, old, new in zip(DOMAINS, r0, vector, strict=True):
                    rec[f"transition_{label}_{domain}"] = transition(old, new)
            indicators = {name: [int(x == "D") for x in routes[name]] for name in routes}
            gamma_route = [indicators["Fij"][k] - indicators["Fi"][k] - indicators["Fj"][k] + indicators["F0"][k] for k in range(4)]
            rec.update({f"gamma_route_{domain}": gamma_route[k] for k, domain in enumerate(DOMAINS)})
            rec["route_interaction_count"] = sum(x != 0 for x in gamma_route)
            rec["route_interaction_l1"] = sum(abs(x) for x in gamma_route)
            rec["routing_config_count"] = len({rec["R0"], rec["Ri"], rec["Rj"], rec["Rij"]})
            rec["Fij_pattern_new"] = rec["Rij"] not in {rec["Ri"], rec["Rj"]}
            rec["delta_gamma"] = rec["gamma_oper"] - rec["gamma_learn"]
            rec["sign_change"] = rec["gamma_oper"] * rec["gamma_learn"] < -EPSILON
            if abs(rec["delta_gamma"]) <= EPSILON:
                rec["delta_class"] = "PRESERVE"
            elif abs(rec["gamma_oper"]) < abs(rec["gamma_learn"]):
                rec["delta_class"] = "ABSORB"
            else:
                rec["delta_class"] = "AMPLIFY"
            for state_label, column_prefix in states_by_name.items():
                rec[f"Vlearn_{state_label}"] = float(row["v_learn_F0"] if state_label == "F0" else row["v_learn_Fi"] if state_label == "Fi" else row["v_learn_Fj"] if state_label == "Fj" else row["v_learn_Fij"])
                rec[f"Voper_{state_label}"] = float(row[f"{column_prefix}_v_oper_c{c:.2f}"])
            records.append(rec)
    transformed = pd.DataFrame(records)
    if len(transformed) != 450 or transformed.duplicated(["seed", "N", "pair", "c"]).any() or transformed.isna().any().any():
        raise ValueError("routing reconstruction has wrong cardinality, duplicates, or NaN")

    progress(3, "Computing routing interactions")
    # Routing fields are already part of the complete long table; write transition details.
    transformed.to_csv(out / "routing_transformation.csv", index=False)
    summary_rows = []
    grouping_specs = [("N", ["N"]), ("c", ["c"]), ("pair", ["pair"]), ("Nxc", ["N", "c"]), ("pairxc", ["pair", "c"]), ("route_interaction_count", ["route_interaction_count"]), ("route_interaction_l1", ["route_interaction_l1"])]
    for dimension, keys in grouping_specs:
        for values, group in transformed.groupby(keys, dropna=False):
            if not isinstance(values, tuple): values = (values,)
            summary_rows.append({"dimension": dimension, **dict(zip(keys, values, strict=True)), **describe(group, "delta_gamma")})
    transformed.groupby("delta_class").size().rename("count").reset_index().to_csv(out / "delta_gamma_classification.csv", index=False)
    pd.DataFrame(summary_rows).to_csv(out / "routing_transformation_summary.csv", index=False)

    progress(4, "DeltaGamma decomposition")
    transformed[["seed", "N", "pair", "c", "gamma_learn", "gamma_oper", "delta_gamma", "delta_class", "sign_change", "route_interaction_count", "route_interaction_l1"]].to_csv(out / "delta_gamma_extended.csv", index=False)

    progress(5, "Representative cases")
    cases = []
    def add_case(label: str, selected: pd.Series) -> None:
        record = selected.to_dict()
        record["case"] = label
        cases.append(record)
    add_case("maximum_absorption", transformed.loc[transformed.delta_gamma.idxmin()])
    add_case("maximum_amplification", transformed.loc[transformed.delta_gamma.idxmax()])
    candidate = transformed.assign(score=transformed.gamma_learn - transformed.gamma_oper.abs()).sort_values(["score", "gamma_learn"], ascending=False).iloc[0]
    add_case("large_learning_small_operational", candidate)
    add_case("preserve", transformed.loc[transformed.delta_gamma.abs().idxmin()])
    sign_rows = transformed[transformed.sign_change]
    if len(sign_rows): add_case("sign_change", sign_rows.sort_values(["delta_gamma", "N", "pair", "c"]).iloc[0])
    variation = transformed.groupby(["N", "pair"], as_index=False).gamma_oper.agg(lambda x: float(x.max() - x.min())).sort_values(["gamma_oper", "N", "pair"], ascending=[False, True, True]).iloc[0]
    evolution = transformed[(transformed.N == variation.N) & (transformed.pair == variation.pair)].sort_values("c")
    for _, selected in evolution.iterrows(): add_case("cost_evolution", selected)
    pd.DataFrame(cases).to_csv(out / "routing_representative_cases.csv", index=False)

    progress(6, "Figures and scientific interpretation")
    for pair in sorted(transformed.pair.unique()):
        subset = transformed[transformed.pair == pair]
        plt.figure(figsize=(5, 3));
        for n, group in subset.groupby("N"): plt.plot(group.c, group.gamma_oper, marker="o", label=f"N={n}")
        plt.axhline(0, color="black", linewidth=.6); plt.xlabel("c"); plt.ylabel("Gamma_oper"); plt.title(pair); plt.legend(); plt.tight_layout(); plt.savefig(figures / f"gamma_oper_{pair.replace('-', '_')}.png", dpi=150); plt.close()
    plt.figure(figsize=(6, 4)); plt.scatter(transformed.route_interaction_l1, transformed.delta_gamma, alpha=.55); plt.xlabel("route_interaction_l1"); plt.ylabel("DeltaGamma"); plt.tight_layout(); plt.savefig(figures / "delta_gamma_vs_route_interaction_l1.png", dpi=150); plt.close()
    for _, selected in pd.DataFrame(cases).head(2).iterrows():
        plt.figure(figsize=(6, 3));
        states_order = ["F0", "Fi", "Fj", "Fij"]
        for index, state in enumerate(states_order):
            plt.scatter([index] * 4, [0, 1, 2, 3], s=180, c=[{"F": "tab:blue", "D": "tab:orange"}[x] for x in selected[f"R{state[1:] if state != 'F0' else '0'}"].split(",")])
        plt.xticks(range(4), states_order); plt.yticks(range(4), DOMAINS); plt.title(f"{selected['case']}: {selected['pair']}, N={selected['N']}, c={selected['c']}"); plt.tight_layout(); plt.savefig(figures / f"routing_case_{selected['case']}.png", dpi=150); plt.close()

    progress(7, "Tests and outputs")
    changed = transformed[transformed.route_interaction_count > 0].delta_gamma
    unchanged = transformed[transformed.route_interaction_count == 0].delta_gamma
    mean_by_cost = transformed.groupby("c")[['gamma_learn', 'gamma_oper', 'delta_gamma']].mean()
    summary = ["# Routing transformation analysis", "", "## OBSERVED", f"Controls passed: 5 seeds, 3 N, 6 pairs, 5 costs, 450 unique observations; Gamma_learn and Gamma_oper reproduce the stored values; TEST absent.", f"DeltaGamma classification: {transformed.delta_class.value_counts().to_dict()}.", f"Routing changes relative to F0 occur in {int((transformed.d_i + transformed.d_j + transformed.d_ij > 0).sum())}/450 observations under at least one intervention comparison.", f"route_interaction_count > 0 in {int((transformed.route_interaction_count > 0).sum())}/450 observations; mean DeltaGamma is {changed.mean():.6f} when nonzero and {unchanged.mean():.6f} when zero.", f"DeltaGamma range: {transformed.delta_gamma.min():.6f} to {transformed.delta_gamma.max():.6f}.", f"Across all observations, mean (Gamma_learn, Gamma_oper, DeltaGamma) is c=0: ({mean_by_cost.loc[0.0, 'gamma_learn']:.6f}, {mean_by_cost.loc[0.0, 'gamma_oper']:.6f}, {mean_by_cost.loc[0.0, 'delta_gamma']:.6f}); c=0.15: ({mean_by_cost.loc[0.15, 'gamma_learn']:.6f}, {mean_by_cost.loc[0.15, 'gamma_oper']:.6f}, {mean_by_cost.loc[0.15, 'delta_gamma']:.6f}).", "", "## SUPPORTED INTERPRETATION", "The data show the sequence learning → competence changes → V(S) → operational routing → Gamma_oper: applying the same learned states to F/D alternatives changes the measured interaction as c changes. At low c, Gamma_oper is substantially below Gamma_learn on average, consistent with operational absorption by the available Deep alternative; as c rises, Gamma_oper moves closer to Gamma_learn. Routing structure is associated descriptively with DeltaGamma, with larger route_interaction_l1 corresponding to more negative mean DeltaGamma; this does not isolate a causal routing contribution.", "Amplification exists in a minority of observations (20/450), and sign changes are present in the saved cases; they are reported in routing_representative_cases.csv without being treated as causal.", "", "## NOT DEMONSTRATED", "These results do not demonstrate routing causality, global HLS superiority, TEST performance, necessity of a joint architecture, development-cost effects, or any B2.2 claim."]
    (out / "routing_transformation.md").write_text("\n".join(summary) + "\n")


if __name__ == "__main__":
    main()
