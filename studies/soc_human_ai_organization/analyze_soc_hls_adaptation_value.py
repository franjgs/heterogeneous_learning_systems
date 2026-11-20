"""Analyze already published SOCTRA-HLS episode CSVs; runs no simulator."""
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config/soc_hls_adaptation_value.json"
C = json.loads(CONFIG_PATH.read_text())
POLICIES = C["policies"]
GROUPS = C["scenario_groups"]
SCENARIOS = [name for names in GROUPS.values() for name in names]
SEED_COUNT = C["seeds_expected"]
BOOT_N = C["bootstrap"]["replicates"]
BOOT_SEED = C["bootstrap"]["random_seed"]
OUT = ROOT / C["output_dir"]
OUT.mkdir(parents=True, exist_ok=True)


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", newline="") as stream:
        fields = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def mean(values):
    return float(statistics.mean(values))


def ci_t(values):
    """Exploratory paired t interval for n=20, df=19."""
    values = list(map(float, values))
    m = mean(values)
    half = 2.093024054 * statistics.stdev(values) / math.sqrt(len(values))
    return m, m - half, m + half


def file_label(value):
    return f"{value:.8f}"


def read_source_data():
    episode_path = ROOT / C["source_episode_file"]
    sens_path = ROOT / C["source_sensitivity_file"]
    rows = read_csv(episode_path)
    sens = read_csv(sens_path)
    selected = [r for r in rows if float(r["cutoff_h"]) == C["terminal_cutoff_h"]]
    seeds = sorted({int(r["seed"]) for r in selected})
    if len(seeds) != SEED_COUNT:
        raise ValueError(f"Expected {SEED_COUNT} seeds, found {len(seeds)}")
    if len({r["profile"] for r in selected}) != 12:
        raise ValueError("Expected 12 central scenarios")
    if set(SCENARIOS) != {r["profile"] for r in selected}:
        raise ValueError("Configured scenario groups do not partition the CSV profiles")
    if len(SCENARIOS) != len(set(SCENARIOS)):
        raise ValueError("A central scenario appears in multiple weight groups")
    matrix = np.empty((SEED_COUNT, len(SCENARIOS), len(POLICIES)), dtype=float)
    sla = np.empty_like(matrix)
    quality = np.empty_like(matrix)
    admits = np.empty((SEED_COUNT, len(SCENARIOS)), dtype=int)
    for si, seed in enumerate(seeds):
        for xi, scenario in enumerate(SCENARIOS):
            cell = [r for r in selected if int(r["seed"]) == seed and r["profile"] == scenario]
            if len(cell) != len(POLICIES) or {r["policy"] for r in cell} != set(POLICIES):
                raise ValueError(f"Incomplete policy cell: {seed}/{scenario}")
            if len({r["trace_sha256"] for r in cell}) != 1:
                raise ValueError(f"Exogenous trace mismatch: {seed}/{scenario}")
            if len({int(r["admitted"]) for r in cell}) != 1:
                raise ValueError(f"Admitted-alert mismatch: {seed}/{scenario}")
            admits[si, xi] = int(cell[0]["admitted"])
            if any(int(r["admitted"]) != int(r["completed"]) + int(r["pending"]) for r in cell):
                raise ValueError(f"Terminal denominator check failed: {seed}/{scenario}")
            for pi, policy in enumerate(POLICIES):
                row = next(r for r in cell if r["policy"] == policy)
                matrix[si, xi, pi] = float(row["RN"])
                sla[si, xi, pi] = float(row["SLA"])
                quality[si, xi, pi] = float(row["quality_completed"])
    # Sensitivity bundle has 20 matched seeds per case/duration/policy. Hashes
    # are common across policy and (as appropriate) across SLA/roster variants.
    for kind in ("sla", "staff"):
        cases = sorted({r["case"] for r in sens if r["kind"] == kind})
        for duration in (8, 16):
            for seed in sorted({int(r["seed"]) for r in sens if r["kind"] == kind}):
                hashes = set()
                counts = set()
                for case in cases:
                    cell = [r for r in sens if r["kind"] == kind and r["case"] == case and int(r["duration_h"]) == duration and int(r["seed"]) == seed]
                    if not cell:
                        continue
                    if len(cell) != 3 or {r["policy"] for r in cell} != set(POLICIES):
                        raise ValueError(f"Incomplete sensitivity policy cell: {kind}/{case}/{duration}/{seed}")
                    hashes.add(cell[0]["trace_hash"])
                    counts.add(int(cell[0]["admitted"]))
                    if len({int(r["admitted"]) for r in cell}) != 1:
                        raise ValueError("Sensitivity admitted-alert mismatch by policy")
                    if any(int(r["admitted"]) != int(r["completed"]) + int(r["pending"]) for r in cell):
                        raise ValueError("Sensitivity terminal denominator check failed")
                if len(hashes) != 1 or len(counts) != 1:
                    raise ValueError(f"Sensitivity exogenous trace mismatch: {kind}/{duration}/{seed}")
    return seeds, matrix, sla, quality, admits, sens


def group_weights(focus, probability):
    """Vary one disjoint family mass; retain baseline proportions otherwise."""
    sizes = {key: len(names) for key, names in GROUPS.items()}
    denom = sum(v for k, v in sizes.items() if k != focus)
    probs = {k: (probability if k == focus else (1 - probability) * sizes[k] / denom) for k in GROUPS}
    w = np.zeros(len(SCENARIOS), dtype=float)
    for group, names in GROUPS.items():
        for name in names:
            w[SCENARIOS.index(name)] = probs[group] / len(names)
    if not math.isclose(float(w.sum()), 1.0, abs_tol=1e-12):
        raise ValueError("Scenario weights do not sum to one")
    return w, probs


def weighted_metrics(matrix, w):
    scenario_means = matrix.mean(axis=0)
    policy_means = w @ scenario_means
    fixed_index = int(np.argmax(policy_means[:2]))
    oracle = float(w @ np.maximum(scenario_means[:, 0], scenario_means[:, 1]))
    return policy_means, fixed_index, oracle, float(oracle - policy_means[2])


def bootstrap_weight(matrix, w, boot_indices):
    # Resample seed clusters, keeping all 12 profiles and policies together.
    boot_scenario_means = matrix[boot_indices].mean(axis=1)  # B x scenario x policy
    boot_policy_means = np.einsum("bsq,s->bq", boot_scenario_means, w)
    best_fixed = np.maximum(boot_policy_means[:, 0], boot_policy_means[:, 1])
    vadapt = boot_policy_means[:, 2] - best_fixed
    oracle = np.einsum("bs,s->b", np.maximum(boot_scenario_means[:, :, 0], boot_scenario_means[:, :, 1]), w)
    regret = oracle - boot_policy_means[:, 2]
    winner = (boot_policy_means[:, 0] < boot_policy_means[:, 1]).astype(int)
    return boot_policy_means, vadapt, oracle, regret, winner


def svg_polyline(points, color, width=3, opacity=1):
    points_txt = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{points_txt}" fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>'


def plot_weight_curves(rows, path):
    width, height = 1000, 630
    left, right, top, bottom = 90, 950, 65, 525
    ymin, ymax = 0.60, 0.68
    xmap = lambda p: left + p * (right - left)
    ymap = lambda v: bottom - (v - ymin) / (ymax - ymin) * (bottom - top)
    colors = {"D1": "#345995", "P1": "#e07a2d", "HLS-B": "#26855b"}
    pts = [r for r in rows if r["family"] == "prolonged" and r["bootstrap_low"] != ""]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', '<text x="45" y="30" font-family="sans-serif" font-size="19">Expected terminal R/N by weight on prolonged scenarios</text>']
    for tick in np.arange(ymin, ymax + 0.0001, 0.01):
        y = ymap(float(tick)); s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#dddddd"/>')
        s.append(f'<text x="{left-12}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{tick:.2f}</text>')
    for tick in np.arange(0, 1.001, .1):
        x=xmap(float(tick)); s.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="#eeeeee"/>')
        s.append(f'<text x="{x:.1f}" y="{bottom+22}" text-anchor="middle" font-family="sans-serif" font-size="12">{tick:.1f}</text>')
    for policy in POLICIES:
        col = "HLSB" if policy == "HLS-B" else policy
        ci_col = policy
        band=[]
        for r in pts:
            band.append((xmap(float(r["focus_probability"])), ymap(float(r[f"{ci_col}_ci_high"]))))
        for r in reversed(pts):
            band.append((xmap(float(r["focus_probability"])), ymap(float(r[f"{ci_col}_ci_low"]))))
        ptxt=" ".join(f"{x:.1f},{y:.1f}" for x,y in band)
        s.append(f'<polygon points="{ptxt}" fill="{colors[policy]}" opacity="0.12"/>')
        line=[(xmap(float(r["focus_probability"])), ymap(float(r[f"{col}_mean"]))) for r in pts]
        s.append(svg_polyline(line,colors[policy],3))
    ux=xmap(0.25);s.append(f'<line x1="{ux:.1f}" y1="{top}" x2="{ux:.1f}" y2="{bottom}" stroke="#555" stroke-dasharray="6 5"/>')
    s.append(f'<text x="{ux+5:.1f}" y="{top+18}" font-family="sans-serif" font-size="11">uniform: p_long=0.25</text>')
    s.append(f'<text x="{(left+right)/2}" y="{height-35}" text-anchor="middle" font-family="sans-serif" font-size="14">Probability mass assigned to prolonged family</text>')
    s.append(f'<text x="22" y="{(top+bottom)/2}" transform="rotate(-90 22 {(top+bottom)/2})" text-anchor="middle" font-family="sans-serif" font-size="14">Expected R/N</text>')
    for i,policy in enumerate(POLICIES):
        x=690+i*90;s.append(f'<line x1="{x}" y1="{height-18}" x2="{x+25}" y2="{height-18}" stroke="{colors[policy]}" stroke-width="3"/><text x="{x+31}" y="{height-14}" font-family="sans-serif" font-size="12">{policy}</text>')
    s.append('<text x="90" y="585" font-family="sans-serif" font-size="11" fill="#555">Bands: paired-seed bootstrap percentile 95% intervals, 20 seed clusters; weight is a design sensitivity, not an estimated SOC probability.</text>')
    s.append('</svg>')
    path.write_text("\n".join(s))


def plot_adaptation_ci(rows, path):
    width,height=1000,610; left,right,top,bottom=90,950,65,515; ymin,ymax=-.04,.06
    xm=lambda p:left+p*(right-left); ym=lambda v:bottom-(v-ymin)/(ymax-ymin)*(bottom-top)
    pts=[r for r in rows if r["family"]=="prolonged" and r["bootstrap_low"]!=""]
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">','<rect width="100%" height="100%" fill="white"/>','<text x="45" y="30" font-family="sans-serif" font-size="19">Adaptation value against the ex-ante best fixed policy</text>']
    for t in np.arange(ymin,ymax+.0001,.02):
        y=ym(float(t)); s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{"#777" if abs(t)<1e-8 else "#ddd"}" stroke-width="{"2" if abs(t)<1e-8 else "1"}"/>')
        s.append(f'<text x="{left-12}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{t:.2f}</text>')
    for t in np.arange(0,1.001,.1):
        x=xm(float(t));s.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="#eee"/>');s.append(f'<text x="{x:.1f}" y="{bottom+22}" text-anchor="middle" font-family="sans-serif" font-size="12">{t:.1f}</text>')
    band=[(xm(float(r['focus_probability'])),ym(float(r['bootstrap_high']))) for r in pts]+[(xm(float(r['focus_probability'])),ym(float(r['bootstrap_low']))) for r in reversed(pts)]
    s.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in band)}" fill="#26855b" opacity="0.18"/>')
    s.append(svg_polyline([(xm(float(r['focus_probability'])),ym(float(r['V_adapt']))) for r in pts],"#26855b",3))
    ux=xm(.25);s.append(f'<line x1="{ux:.1f}" y1="{top}" x2="{ux:.1f}" y2="{bottom}" stroke="#555" stroke-dasharray="6 5"/>')
    s.append(f'<text x="{(left+right)/2}" y="{height-32}" text-anchor="middle" font-family="sans-serif" font-size="14">Probability mass assigned to prolonged family</text>')
    s.append(f'<text x="22" y="{(top+bottom)/2}" transform="rotate(-90 22 {(top+bottom)/2})" text-anchor="middle" font-family="sans-serif" font-size="14">V_adapt (absolute R/N)</text>')
    s.append('<text x="90" y="580" font-family="sans-serif" font-size="11" fill="#555">Positive values favor HLS-B; negative values favor the best fixed chosen for that weighted distribution. Bootstrap reselects D1/P1 within each replicate.</text>');s.append('</svg>');path.write_text("\n".join(s))


def plot_regret(scenario_rows, path):
    width,height=1180,650;left,right,top,bottom=250,920,55,565
    vals=[float(r['signed_shortfall_oracle_minus_HB']) for r in scenario_rows];lim=max(.01,max(abs(x) for x in vals)*1.15)
    xm=lambda v:left+(v+lim)/(2*lim)*(right-left)
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">','<rect width="100%" height="100%" fill="white"/>','<text x="30" y="30" font-family="sans-serif" font-size="19">Scenario-wise signed shortfall to retrospective fixed-policy reference</text>']
    for tick in np.linspace(-lim,lim,7):
        x=xm(float(tick));s.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="{"#666" if abs(tick)<1e-9 else "#ddd"}" stroke-width="{"2" if abs(tick)<1e-9 else "1"}"/>');s.append(f'<text x="{x:.1f}" y="{bottom+22}" text-anchor="middle" font-family="sans-serif" font-size="11">{tick:+.3f}</text>')
    for i,r in enumerate(scenario_rows):
        y=top+20+i*40;v=float(r['signed_shortfall_oracle_minus_HB']);x0=xm(0);x1=xm(v);color='#c85a54' if v>0 else '#26855b';s.append(f'<text x="{left-12}" y="{y+4}" text-anchor="end" font-family="sans-serif" font-size="11">{r["scenario"]}</text>');s.append(f'<rect x="{min(x0,x1):.1f}" y="{y-8}" width="{max(1,abs(x1-x0)):.1f}" height="16" fill="{color}"/>');s.append(f'<text x="{right+12}" y="{y+4}" font-family="sans-serif" font-size="11">{v:+.4f}</text>')
    s.append(f'<text x="{(left+right)/2}" y="{height-35}" text-anchor="middle" font-family="sans-serif" font-size="13">Fixed-policy oracle R/N − HLS-B R/N (positive = HLS-B shortfall; negative = HLS-B gain)</text>');s.append('</svg>');path.write_text("\n".join(s))


def main():
    seeds, matrix, sla, quality, admits, sens = read_source_data()
    seed_index = {seed: i for i, seed in enumerate(seeds)}
    rng = np.random.default_rng(BOOT_SEED)
    boot_idx = rng.integers(0, SEED_COUNT, size=(BOOT_N, SEED_COUNT))

    # Scenario-specific audit and seed-level signed shortfall.
    scenario_rows = []
    seed_risk = []
    scenario_means = matrix.mean(axis=0)
    scenario_sla = sla.mean(axis=0)
    scenario_quality = quality.mean(axis=0)
    for xi, scenario in enumerate(SCENARIOS):
        dmean, pmean, hmean = scenario_means[xi]
        fixed = int(np.argmax([dmean, pmean]))
        oracle = max(dmean, pmean)
        shortfall = oracle - hmean
        relative = shortfall / oracle * 100 if oracle else 0.0
        row = {
            "scenario": scenario,
            "weight_group": next(g for g, names in GROUPS.items() if scenario in names),
            "admitted_mean": f"{mean(admits[:, xi]):.4f}",
            "D1_mean_RN": f"{dmean:.8f}", "P1_mean_RN": f"{pmean:.8f}", "HLSB_mean_RN": f"{hmean:.8f}",
            "HLSB_minus_D1": f"{hmean-dmean:.8f}", "HLSB_minus_P1": f"{hmean-pmean:.8f}",
            "best_fixed_retrospective": POLICIES[fixed], "best_fixed_mean_RN": f"{oracle:.8f}",
            "signed_shortfall_oracle_minus_HB": f"{shortfall:.8f}", "shortfall_percent_best_fixed": f"{max(shortfall,0)/oracle*100:.4f}",
            "HLSB_gain_percent_best_fixed": f"{max(-shortfall,0)/oracle*100:.4f}",
            "D1_SLA": f"{scenario_sla[xi,0]:.8f}", "P1_SLA": f"{scenario_sla[xi,1]:.8f}", "HLSB_SLA": f"{scenario_sla[xi,2]:.8f}",
            "D1_quality_completed": f"{scenario_quality[xi,0]:.8f}", "P1_quality_completed": f"{scenario_quality[xi,1]:.8f}", "HLSB_quality_completed": f"{scenario_quality[xi,2]:.8f}",
        }
        scenario_rows.append(row)
        for si, seed in enumerate(seeds):
            fixed_seed = float(matrix[si, xi, fixed])
            seed_risk.append({
                "scenario": scenario, "seed": seed,
                "D1_RN": f"{matrix[si,xi,0]:.8f}", "P1_RN": f"{matrix[si,xi,1]:.8f}", "HLSB_RN": f"{matrix[si,xi,2]:.8f}",
                "HLSB_minus_D1": f"{matrix[si,xi,2]-matrix[si,xi,0]:.8f}", "HLSB_minus_P1": f"{matrix[si,xi,2]-matrix[si,xi,1]:.8f}",
                "retrospective_fixed_selected_on_scenario_means": POLICIES[fixed],
                "fixed_minus_HLSB_signed_shortfall": f"{fixed_seed-matrix[si,xi,2]:.8f}",
            })
    write_csv(OUT / "scenario_risk.csv", scenario_rows)
    write_csv(OUT / "seed_scenario_risk.csv", seed_risk)

    uniform_w = np.repeat(1 / len(SCENARIOS), len(SCENARIOS))
    uniform_means, uniform_fixed, uniform_oracle, uniform_regret = weighted_metrics(matrix, uniform_w)
    uniform_point = float(uniform_means[2] - max(uniform_means[0], uniform_means[1]))
    uniform_boot = bootstrap_weight(matrix, uniform_w, boot_idx)
    uniform_v = uniform_boot[1]
    uniform_best = "D1" if uniform_means[0] >= uniform_means[1] else "P1"
    uniform_ci = np.quantile(uniform_v, [.025, .975])
    uniform_rel = uniform_point / float(uniform_means[uniform_fixed]) * 100
    seed_portfolio_uniform = np.einsum("sqp,q->sp", matrix, uniform_w)
    loss_freq_uniform = float(np.mean(seed_portfolio_uniform[:, 2] < seed_portfolio_uniform[:, uniform_fixed]))
    oracle_by_s = np.maximum(scenario_means[:,0], scenario_means[:,1])
    max_shortfall_row = max(scenario_rows, key=lambda r: float(r["signed_shortfall_oracle_minus_HB"]))
    write_csv(OUT / "uniform_summary.csv", [{
        "D1_expected_RN": f"{uniform_means[0]:.8f}", "P1_expected_RN": f"{uniform_means[1]:.8f}", "HLSB_expected_RN": f"{uniform_means[2]:.8f}",
        "best_fixed_ex_ante": uniform_best, "best_fixed_expected_RN": f"{uniform_means[uniform_fixed]:.8f}",
        "V_adapt": f"{uniform_point:.8f}", "V_adapt_relative_percent": f"{uniform_rel:.5f}",
        "bootstrap_95_low": f"{uniform_ci[0]:.8f}", "bootstrap_95_high": f"{uniform_ci[1]:.8f}",
        "bootstrap_probability_V_positive": f"{np.mean(uniform_v > 0):.5f}",
        "bootstrap_best_fixed_D1_frequency": f"{np.mean(uniform_boot[4] == 0):.5f}",
        "bootstrap_best_fixed_P1_frequency": f"{np.mean(uniform_boot[4] == 1):.5f}",
        "oracle_retrospective_RN": f"{uniform_oracle:.8f}", "oracle_minus_HLSB_regret": f"{uniform_regret:.8f}",
        "HLSB_loses_to_ex_ante_fixed_fraction_of_seed_portfolios": f"{loss_freq_uniform:.5f}",
    }])
    uniform_boot_rows = []
    boot_pm, boot_v, boot_o, boot_reg, boot_winner = uniform_boot
    for b in range(BOOT_N):
        uniform_boot_rows.append({"replicate":b,"D1":f"{boot_pm[b,0]:.8f}","P1":f"{boot_pm[b,1]:.8f}","HLS-B":f"{boot_pm[b,2]:.8f}","V_adapt":f"{boot_v[b]:.8f}","oracle_retrospective":f"{boot_o[b]:.8f}","oracle_minus_HLSB":f"{boot_reg[b]:.8f}","best_fixed":POLICIES[int(boot_winner[b])]})
    write_csv(OUT / "uniform_bootstrap.csv", uniform_boot_rows)

    # One-family-at-a-time weight curves. The prolonged sweep is bootstrapped
    # at every grid point; other families are retained as scenario-sensitivity
    # analyses and get point estimates at all grid points.
    sensitivity_rows = []
    key_values = {0.0, 0.25, 0.5, 0.75, 1.0}
    for focus in GROUPS:
        for k in range(101):
            p = k / 100
            w, probs = group_weights(focus, p)
            pm, fi, oracle, regret = weighted_metrics(matrix, w)
            portfolio = np.einsum("sqp,q->sp", matrix, w)
            loss_freq = float(np.mean(portfolio[:,2] < portfolio[:,fi]))
            row = {
                "family":focus,"focus_probability":f"{p:.2f}",
                **{f"weight_{g}":f"{probs[g]:.8f}" for g in GROUPS},
                "D1_mean":f"{pm[0]:.8f}","P1_mean":f"{pm[1]:.8f}","HLSB_mean":f"{pm[2]:.8f}",
                "ex_ante_best_fixed":POLICIES[fi],"V_adapt":f"{pm[2]-pm[fi]:.8f}",
                "V_adapt_relative_percent":f"{(pm[2]-pm[fi])/pm[fi]*100:.5f}",
                "R_oracle_retrospective":f"{oracle:.8f}","oracle_minus_HLSB_regret":f"{regret:.8f}",
                "HLSB_loses_to_ex_ante_fixed_seed_fraction":f"{loss_freq:.5f}",
                "bootstrap_low":"","bootstrap_high":"","bootstrap_P_V_positive":"",
                "bootstrap_best_fixed_D1_frequency":"","bootstrap_best_fixed_P1_frequency":"",
            }
            if focus == "prolonged":
                bp, bv, bo, br, bw = bootstrap_weight(matrix, w, boot_idx)
                lo,hi=np.quantile(bv,[.025,.975])
                row.update({"bootstrap_low":f"{lo:.8f}","bootstrap_high":f"{hi:.8f}","bootstrap_P_V_positive":f"{np.mean(bv>0):.5f}","bootstrap_best_fixed_D1_frequency":f"{np.mean(bw==0):.5f}","bootstrap_best_fixed_P1_frequency":f"{np.mean(bw==1):.5f}"})
                for j, pol in enumerate(POLICIES):
                    qlo,qhi=np.quantile(bp[:,j],[.025,.975])
                    row[f"{pol}_ci_low"]=f"{qlo:.8f}"; row[f"{pol}_ci_high"]=f"{qhi:.8f}"
            sensitivity_rows.append(row)
    # Explicit uniform point; its family masses reflect exactly 12 equal row weights.
    uniform_probs={g:len(names)/len(SCENARIOS) for g,names in GROUPS.items()}
    w=uniform_w; pm,fi,oracle,regret=weighted_metrics(matrix,w); portfolio=np.einsum("sqp,q->sp", matrix, w); bp,bv,bo,br,bw=uniform_boot; lo,hi=np.quantile(bv,[.025,.975])
    sensitivity_rows.append({"family":"uniform_reference","focus_probability":"","**weight_placeholder":"",**{f"weight_{g}":f"{uniform_probs[g]:.8f}" for g in GROUPS},"D1_mean":f"{pm[0]:.8f}","P1_mean":f"{pm[1]:.8f}","HLSB_mean":f"{pm[2]:.8f}","ex_ante_best_fixed":POLICIES[fi],"V_adapt":f"{pm[2]-pm[fi]:.8f}","V_adapt_relative_percent":f"{(pm[2]-pm[fi])/pm[fi]*100:.5f}","R_oracle_retrospective":f"{oracle:.8f}","oracle_minus_HLSB_regret":f"{regret:.8f}","HLSB_loses_to_ex_ante_fixed_seed_fraction":f"{np.mean(portfolio[:,2]<portfolio[:,fi]):.5f}","bootstrap_low":f"{lo:.8f}","bootstrap_high":f"{hi:.8f}","bootstrap_P_V_positive":f"{np.mean(bv>0):.5f}","bootstrap_best_fixed_D1_frequency":f"{np.mean(bw==0):.5f}","bootstrap_best_fixed_P1_frequency":f"{np.mean(bw==1):.5f}"})
    # DictWriter needs a stable schema; remove the marker key in all rows.
    for r in sensitivity_rows:
        r.pop("**weight_placeholder",None)
    write_csv(OUT / "weight_sensitivity.csv", sensitivity_rows)

    # Conditional SLA and staffing adaptations: a single scenario at a time,
    # never pooled with the central 12-profile distribution.
    conditional_rows=[]
    for kind in ("sla","staff"):
        cases=sorted({r["case"] for r in sens if r["kind"]==kind})
        for duration in (8,16):
            for case in cases:
                cell=[r for r in sens if r["kind"]==kind and r["case"]==case and int(r["duration_h"])==duration]
                seed_ids=sorted({int(r["seed"]) for r in cell})
                mm=np.array([[float(next(r["RN"] for r in cell if int(r["seed"])==seed and r["policy"]==pol)) for pol in POLICIES] for seed in seed_ids])
                point=mm.mean(axis=0); fixed=int(np.argmax(point[:2])); v=float(point[2]-point[fixed]);
                local_idx=np.random.default_rng(BOOT_SEED + duration + (0 if kind=="sla" else 100)).integers(0,len(seed_ids),size=(BOOT_N,len(seed_ids)))
                bm=mm[local_idx].mean(axis=1); bv=bm[:,2]-np.maximum(bm[:,0],bm[:,1]); lo,hi=np.quantile(bv,[.025,.975])
                template={"analysis":kind,"case":case,"duration_h":duration,"ex_ante_best_fixed":POLICIES[fixed],"D1_mean":f"{point[0]:.8f}","P1_mean":f"{point[1]:.8f}","HLSB_mean":f"{point[2]:.8f}","V_adapt":f"{v:.8f}","V_adapt_relative_percent":f"{v/point[fixed]*100:.5f}","bootstrap_low":f"{lo:.8f}","bootstrap_high":f"{hi:.8f}","bootstrap_P_V_positive":f"{np.mean(bv>0):.5f}","HLSB_loses_to_ex_ante_fixed_seed_fraction":f"{np.mean(mm[:,2]<mm[:,fixed]):.5f}"}
                if kind=="sla":
                    c=next(c for c in C.get("sla_sets",[]) if c["name"]==case) if "sla_sets" in C else None
                    # Pull parameters from the published sensitivity metadata.
                    sens_config=json.loads((ROOT/"results/soc_hls_operating_sensitivity/metadata.json").read_text())["config"]
                    c=next(c for c in sens_config["sla_sets"] if c["name"]==case)
                    template.update({"T0_h":c["T0"],"f_high":c["f_high"],"f_low":c["f_low"],"pulse_over_critical_deadline":duration/c["T0"]})
                else:
                    c=next(c for c in cell)
                    template.update({"n_l1":c["n_l1"],"n_l2":c["n_l2"],"mu_l1":c["mu_l1"],"mu_l2":c["mu_l2"],"rho_normal":c["rho_normal"],"rho_pulse":c["rho_pulse"],"demand_absolute_fixed":"true"})
                conditional_rows.append(template)
    write_csv(OUT / "conditional_sensitivity.csv", conditional_rows)

    # Main family weight sweep point summaries and exact sign/winner regions.
    def policy_group_mean(group, policy_index):
        ix=[SCENARIOS.index(s) for s in GROUPS[group]]
        return float(scenario_means[ix,policy_index].mean())
    group_means={g:np.array([policy_group_mean(g,i) for i in range(3)]) for g in GROUPS}
    sizes={g:len(GROUPS[g]) for g in GROUPS}
    def focus_policy_means(focus,p):
        others={g:sizes[g] for g in GROUPS if g!=focus}; den=sum(others.values())
        other=np.zeros(3)
        for g,n in others.items(): other += (n/den)*group_means[g]
        return p*group_means[focus]+(1-p)*other
    def focus_weights(focus,p): return group_weights(focus,p)[1]
    def roots_for_pair(focus,a,b):
        # Both expected-return curves are affine in p for each defined family.
        y0=focus_policy_means(focus,0)[a]-focus_policy_means(focus,0)[b]
        y1=focus_policy_means(focus,1)[a]-focus_policy_means(focus,1)[b]
        if abs(y1-y0)<1e-14:return []
        root=-y0/(y1-y0)
        return [root] if 0 < root < 1 else []
    def exact_regions(focus):
        roots=sorted(set(round(x,12) for a in range(3) for b in range(a+1,3) for x in roots_for_pair(focus,a,b)))
        cuts=[0.0]+roots+[1.0]; segments=[]
        for l,r in zip(cuts,cuts[1:]):
            mid=(l+r)/2; vals=focus_policy_means(focus,mid); win=POLICIES[int(np.argmax(vals))]
            if segments and segments[-1]["policy"]==win:segments[-1]["end"]=r
            else:segments.append({"start":l,"end":r,"policy":win})
        # V root on intervals where the identity of ex-ante best fixed is fixed.
        v_roots=[]
        fixed_cuts=sorted(set([0.0,1.0]+roots_for_pair(focus,0,1)))
        for l,r in zip(fixed_cuts,fixed_cuts[1:]):
            mid=(l+r)/2; fixed=int(np.argmax(focus_policy_means(focus,mid)[:2]))
            v0=focus_policy_means(focus,l)[2]-focus_policy_means(focus,l)[fixed]
            v1=focus_policy_means(focus,r)[2]-focus_policy_means(focus,r)[fixed]
            if abs(v0)<1e-12 and 0<l<1:v_roots.append(l)
            if v0*v1<0:
                v_roots.append(l+(r-l)*(-v0)/(v1-v0))
            if abs(v1)<1e-12 and 0<r<1:v_roots.append(r)
        return segments,sorted(set(round(x,8) for x in v_roots))
    region_rows=[]
    for focus in GROUPS:
        segments,roots=exact_regions(focus)
        for seg in segments:region_rows.append({"focus_family":focus,"weight_interval_start":seg["start"],"weight_interval_end":seg["end"],"expected_return_winner":seg["policy"],"V_adapt_sign_change_roots":";".join(map(str,roots))})
    write_csv(OUT/"weight_decision_regions.csv",region_rows)

    # Render SVGs from point and bootstrap outputs.
    plot_rows=[r for r in sensitivity_rows if r["family"]=="prolonged"]
    plot_weight_curves(plot_rows, HERE/"figures/soc_hls_adaptation_weight_sensitivity.svg")
    plot_adaptation_ci(plot_rows, HERE/"figures/soc_hls_adaptation_value_ci.svg")
    plot_regret(scenario_rows, HERE/"figures/soc_hls_adaptation_scenario_regret.svg")

    # Build the audit report from calculations above.
    report=[]
    def line(x=""): report.append(x)
    line("# SOCTRA–HLS — Valor de la adaptación bajo incertidumbre operativa")
    line();line("**Alcance:** análisis secundario de CSV publicados en el commit bec423a54588de2e5157265f810f3617d1994b4d. No se ejecutó el simulador, no se ajustó HLS-B y no se cambiaron D1/P1, motor ni configuraciones. Todas las conclusiones de esta nota son exploratorias, salvo la cita separada a la validación confirmatoria previa.")
    line();line("## Pregunta y estimandos")
    line();line("Para una distribución de escenarios p fijada sin seleccionar resultados favorables, el valor adaptativo se estima como V_adapt = E_p[R(HLS-B)] − max(E_p[R(D1)], E_p[R(P1)]). D1/P1 se elige una sola vez para la distribución completa y representa una organización fija ex ante. El oracle retrospectivo limitado usa E_p[max(mean_s R(D1,s), mean_s R(P1,s))]; selecciona D1 o P1 por escenario con sus medias observadas. No es política implementable ni oracle de decisiones individuales. HLS-B es el supervisor causal evaluado, no una selección retrospectiva.")
    line();line("El regret firmado frente a esa referencia se define como R_oracle−E_p[R(HLS-B)]; puede ser negativo cuando HLS-B supera incluso al mejor fijo retrospectivo. La mejora relativa es V_adapt dividido por el R/N esperado de la mejor fija ex ante. La métrica primaria es V_adapt absoluta en R/N.")
    line();line("## Datos y validaciones")
    line();line(f"Se usaron {len(SCENARIOS)} escenarios, {SEED_COUNT} semillas ({min(seeds)}–{max(seeds)}), tres políticas y el corte H+D=48 h de [`episodes.csv`](../../results/soc_hls_operating_regions/episodes.csv). Para cada escenario-semilla se comprobó una fila por política, hash de traza común, admitidas comunes y admitidas=completadas+pendientes. El valor R/N se usa directamente, sin reconstruir denominadores. Hay {len(sens)} filas de sensibilidad SLA/plantilla; los hashes comunes por política y configuración se comprobaron, y se mantienen fuera de la distribución central.")
    line();line("Los perfiles comparten identificadores de semilla y usan streams aleatorios correlacionados entre escenarios. El bootstrap trata cada identificador de semilla como un clúster y remuestrea juntos sus 12 escenarios y tres políticas; no trata 240 filas como independientes. Los IC de V_adapt son percentiles de 10.000 remuestras emparejadas, con semilla bootstrap 20261120 y mejor política fija reseleccionada en cada réplica. Solo hay 20 clústeres originales: los intervalos son exploratorios y no incluyen incertidumbre sobre la distribución real de escenarios.")
    line();line("## Distribución uniforme: referencia matemática")
    line();line("Uniforme significa 1/12 para cada fila central, no 1/12 para cada tipo real de episodio. Se usa solo como benchmark. Las familias disjuntas son: breve (5 escenarios, pulso ≤4 h), moderada (3 escenarios, pulso de 8 h y recuperación habitual), prolongada (3 escenarios, pulso ≥12 h) y recuperación rápida (1 variante d8, rho recuperación .70). Cada familia reparte su masa por igual entre sus miembros. En la distribución uniforme, masas son 5/12, 3/12, 3/12 y 1/12; la variante rápida queda separada para no duplicar el escenario nominal de 8 h en las familias de duración.")
    line();line("| Política | R/N esperado uniforme | Diferencia vs mejor fija ex ante | Relativa vs mejor fija |");line("|---|---:|---:|---:|")
    for i,p in enumerate(POLICIES):
        diff=float(uniform_means[i]-uniform_means[uniform_fixed]);line(f"| {p} | {uniform_means[i]:.6f} | {diff:+.6f} | {diff/uniform_means[uniform_fixed]*100:+.3f}% |")
    line(f"| Mejor fija ex ante | **{uniform_means[uniform_fixed]:.6f} ({uniform_best})** |  |  |")
    line();line(f"**V_adapt uniforme = {uniform_point:+.6f} R/N** ({uniform_rel:+.3f}% de la mejor fija {uniform_best}); IC95% bootstrap emparejado [{uniform_ci[0]:+.6f}, {uniform_ci[1]:+.6f}], P(V>0) bootstrap={np.mean(uniform_v>0):.3f}. La política fija seleccionada por la media es {uniform_best}; en remuestras bootstrap fue D1 ganadora {np.mean(uniform_boot[4]==0):.1%} y P1 {np.mean(uniform_boot[4]==1):.1%}. HLS-B tuvo menor rendimiento seed-portfolio que esa fija en {loss_freq_uniform:.1%} de los 20 seed portfolios. Estas fracciones describen variabilidad Monte Carlo en el conjunto, no probabilidades operativas.")
    line();line(f"**Oracle retrospectivo uniforme:** R_oracle={uniform_oracle:.6f}; signed shortfall/regret R_oracle−HLS-B={uniform_regret:+.6f}. Diferencia relativa oracle–HLS-B={(uniform_oracle-uniform_means[2])/uniform_means[uniform_fixed]*100:+.3f}% de la mejor fija ex ante. El regret máximo entre medias de escenario es {float(max_shortfall_row['signed_shortfall_oracle_minus_HB']):+.6f} en {max_shortfall_row['scenario']}; es un máximo observado dentro de 12 escenarios seleccionados, no una cota de peor caso.")
    line();line("## Sensibilidad a los pesos: no son prevalencias SOC")
    line();line("Las cuatro familias son una partición exhaustiva y no solapada de las 12 celdas. Para cada barrido se varía la masa de una familia p=0…1; el resto se distribuye proporcionalmente al número de escenarios de las otras familias en el diseño central. Dentro de cada familia, la masa se reparte igualmente. Así la curva de peso prolongado reproduce exactamente la distribución uniforme en p=0.25. No se optimizaron pesos para favorecer HLS-B; no son estimaciones de frecuencia en GMV-CERT.")
    line();line("![R/N esperado por peso prolongado](../../studies/soc_human_ai_organization/figures/soc_hls_adaptation_weight_sensitivity.svg)")
    line();line("![V_adapt e IC bootstrap por peso prolongado](../../studies/soc_human_ai_organization/figures/soc_hls_adaptation_value_ci.svg)")
    line();line("Puntos de lectura de la familia prolongada:");line();line("| Peso prolongado | Peso breve/moderado/rápido | D1 | P1 | HLS-B | Mejor fija ex ante | V_adapt [IC95 bootstrap] | Oracle−HLS-B | Pérdida HLS-B vs fija en seed portfolios |");line("|---:|---|---:|---:|---:|---|---|---:|---:|")
    for p in (0,.25,.5,.75,1):
        row=next(r for r in plot_rows if abs(float(r['focus_probability'])-p)<1e-9)
        rest=f"{float(row['weight_brief']):.3f}/{float(row['weight_moderate']):.3f}/{float(row['weight_fast_recovery']):.3f}"
        line(f"| {p:.2f} | {rest} | {float(row['D1_mean']):.6f} | {float(row['P1_mean']):.6f} | {float(row['HLSB_mean']):.6f} | {row['ex_ante_best_fixed']} | {float(row['V_adapt']):+.6f} [{float(row['bootstrap_low']):+.6f}; {float(row['bootstrap_high']):+.6f}] | {float(row['oracle_minus_HLSB_regret']):+.6f} | {float(row['HLSB_loses_to_ex_ante_fixed_seed_fraction']):.1%} |")
    segments, roots = exact_regions("prolonged")
    line();line("Regiones de ganador por media a lo largo de esta familia 1D:")
    for seg in segments: line(f"- p_prolonged ∈ [{seg['start']:.4f}, {seg['end']:.4f}]: {seg['policy']} tiene mayor R/N esperado entre las tres.")
    line(f"V_adapt cambia de signo en p_prolonged={', '.join(f'{x:.4f}' for x in roots) if roots else 'ningún punto interior'} (frontera calculada sobre medias lineales de grupo). No es una frontera probabilística operativa y su ubicación no incluye incertidumbre estadística.")
    line();line("Sensibilidades focales restantes (pesos para p=0, .25, .50, .75, 1; estas celdas complementan el CSV completo):");line();line("| Familia a la que se da peso focal | p focal | pesos brief/moderate/prolonged/fast-recovery | D1 | P1 | HLS-B | fija ex ante | V_adapt |") ;line("|---|---:|---|---:|---:|---:|---|---:|")
    for focus in ("brief","moderate","fast_recovery"):
        for p in (0,.25,.5,.75,1):
            row=next(r for r in sensitivity_rows if r['family']==focus and abs(float(r['focus_probability'])-p)<1e-9)
            ww="/".join(f"{float(row[f'weight_{g}']):.3f}" for g in GROUPS)
            line(f"| {focus} | {p:.2f} | {ww} | {float(row['D1_mean']):.5f} | {float(row['P1_mean']):.5f} | {float(row['HLSB_mean']):.5f} | {row['ex_ante_best_fixed']} | {float(row['V_adapt']):+.5f} |")
    line();line("Los valores esperados varían linealmente dentro de cada familia porque los pesos dependen linealmente de p; el máximo entre D1/P1 puede producir un quiebre. Los intervalos bootstrap de la curva prolongada miden solo incertidumbre Monte Carlo condicionada a esas ponderaciones. La dispersión entre curvas representa sensibilidad a elecciones de p, no incertidumbre sobre la distribución real.")
    line();line("## Riesgo por escenario y mecanismo observado")
    line();line("![Shortfall firmado por escenario](../../studies/soc_human_ai_organization/figures/soc_hls_adaptation_scenario_regret.svg)")
    line();line("El CSV [`scenario_risk.csv`](../../results/soc_hls_adaptation_value/scenario_risk.csv) da para las 12 celdas R/N D1/P1/HLS-B, diferencias HB−D1/HB−P1, HLS-B−mejor fija retrospectiva, magnitud/porcentaje de pérdida o ganancia, SLA y calidad completada. `seed_scenario_risk.csv` conserva las 240 diferencias por semilla-escenario emparejadas. El shortfall firmado del oracle no es siempre positivo: d12/d16 muestran ganancia de HLS-B sobre ambos fijos por media; el oracle está restringido a fijas.")
    losing=sum(float(r['signed_shortfall_oracle_minus_HB'])>0 for r in scenario_rows); positive=sum(float(r['signed_shortfall_oracle_minus_HB'])<0 for r in scenario_rows)
    lossrows=[r for r in scenario_rows if float(r['signed_shortfall_oracle_minus_HB'])>0]
    worst=max(lossrows,key=lambda r:float(r['signed_shortfall_oracle_minus_HB']))
    line();line(f"HLS-B tiene shortfall positivo frente al fijo retrospectivo por medias en {losing}/12 escenarios y ganancia en {positive}/12. El mayor shortfall de media es {float(worst['signed_shortfall_oracle_minus_HB']):.6f} ({float(worst['shortfall_percent_best_fixed']):.2f}% de esa fija) en {worst['scenario']}; el máximo no ofrece garantía sobre episodios futuros. En d16 rho=1.25, D1 SLA={float(worst['D1_SLA']):.3f}, P1 SLA={float(worst['P1_SLA']):.3f}, HLS-B SLA={float(worst['HLSB_SLA']):.3f}; calidad esperada entre completadas D1/P1/HLS-B={float(worst['D1_quality_completed']):.3f}/{float(worst['P1_quality_completed']):.3f}/{float(worst['HLSB_quality_completed']):.3f}. D1 conserva más calidad modelada pero pierde puntualidad; P1 protege deadlines con pérdida de calidad; HLS-B queda entre medias y mejora R/N frente a ambas en esta celda.")
    line();line("En escenarios breves y la mayoría de moderados, D1 suele ser la fija retrospectiva más alta; HLS-B mantiene rendimiento cerca de D1, pero sus pequeñas pérdidas repetidas pueden hacer preferible D1 ex ante si esos escenarios pesan mucho. En los pulsos prolongados, la acumulación y deadlines tardíos hacen que P1 o HLS-B recupere valor. HLS-B combina modos causalmente mediante estimación de carga e histéresis; esa posibilidad de adaptación no garantiza que detecte a tiempo cada episodio o que supere una fija para toda mezcla.")
    line();line("## SLA y plantilla: valores condicionales, no una mezcla operativa")
    line();line("La sensibilidad publicada solo cruza escenarios nominales de 8/16 h con cinco SLA y cinco plantillas. No hay probabilidades defendibles para configuraciones SLA/roster; no se asignan pesos conjuntos ni se mezclan estas celdas con los 12 escenarios centrales.")
    line();line("Resumen de V_adapt condicional (20 semillas emparejadas, bootstrap por semilla con mejor fija reseleccionada):")
    line();line("| Bloque | Condición | d (h) | Mejor fija ex ante | V_adapt [IC95 bootstrap] | Pérdida HLS-B vs fija entre seeds |");line("|---|---|---:|---|---|---:|")
    for r in conditional_rows:
        cond=(f"T0={r['T0_h']} f={r['f_high']}/{r['f_low']}" if r['analysis']=='sla' else f"{r['n_l1']}×{r['n_l2']} (rho {float(r['rho_normal']):.2f}/{float(r['rho_pulse']):.2f})")
        line(f"| {r['analysis']} | {cond} | {r['duration_h']} | {r['ex_ante_best_fixed']} | {float(r['V_adapt']):+.5f} [{float(r['bootstrap_low']):+.5f}; {float(r['bootstrap_high']):+.5f}] | {float(r['HLSB_loses_to_ex_ante_fixed_seed_fraction']):.1%} |")
    line();line("SLA 1:4:12 y factores alternativos modifican el signo y magnitud de HB−D1; en d16 la referencia da ventaja y T0=1.25 o separación 8:16 la invierten. Con demanda absoluta constante, más L1 reduce rho (7×3 tiene rho .724/1.065); 5×3 la eleva a 1.033/1.519. La ventaja cambia con el entorno y no puede expresarse como valor esperado sobre plantillas sin una distribución externa. Tabla completa y calidad/SLA por episodio permanecen en el CSV original publicado.")
    line();line("## Confirmatorio frente a exploratorio y límites")
    line();line("La validación confirmatoria previa mantuvo HLS-B congelada y halló en su distribución sintética equiponderada HLS-B−D1=+.02820 [+.02526;+.03115], n=100; el beneficio se concentra en sobrecarga estacionaria, no en las dos transiciones individuales. Ese resultado no es V_adapt de los 12 perfiles y no se combina con esta exploración. La comparación estacionaria D1/P1 confirmó complementariedad de régimen, no un óptimo universal.")
    line();line("Las 12 celdas centrales comparten los 20 seed IDs, por lo que el bootstrap por semilla es imprescindible; sin embargo, solo cuantifica Monte Carlo de las realizaciones condicionadas. No conocemos la distribución real de severidad, duración, recuperación, SLA o plantilla. El escenario uniforme y las familias de pesos son referencias matemáticas, no mezcla GMV-CERT. No se hicieron correcciones confirmatorias ni se reutilizaron las semillas confirmatorias para esta inferencia.")
    line();line("La demanda es Poisson por tramos y las cargas, SLA terminales, capacidad continua, competencias, servicios, routing y equipos son hipotéticos. SOCTRA aporta volúmenes de alerta, no tiempos de trabajo ni prevalencia de estos perfiles. El resultado no valida un contrato SLA ni cobertura por turnos. R/N combina puntualidad y calidad esperada y debe interpretarse junto a SLA y calidad completada.")
    line();line("**Conclusión:** con pesos uniformes sobre las 12 filas, el valor esperado de HLS-B frente a la mejor fija seleccionada ex ante es el V_adapt calculado arriba; la sensibilidad muestra en qué familias de pesos se vuelve positivo o negativo. El signo no es universal: D1 puede ser preferible si predominan episodios breves/moderados, mientras suficiente peso en carga prolongada puede favorecer HLS-B o P1. No hay base para determinar qué mezcla representa un SOC real, así que el análisis caracteriza condiciones de valor, no una recomendación operativa universal.")
    line();line("## Reproducción")
    line();line("Análisis puro de CSV, sin simulador: [configuración de pesos](config/soc_hls_adaptation_value.json), [script](analyze_soc_hls_adaptation_value.py). Resultados reproducibles en `results/soc_hls_adaptation_value/`: `uniform_summary.csv`, `uniform_bootstrap.csv`, `weight_sensitivity.csv`, `weight_decision_regions.csv`, `scenario_risk.csv`, `seed_scenario_risk.csv`, `conditional_sensitivity.csv`. Figuras: `figures/soc_hls_adaptation_weight_sensitivity.svg`, `figures/soc_hls_adaptation_value_ci.svg`, `figures/soc_hls_adaptation_scenario_regret.svg`.")
    (HERE/"SOC_HLS_ADAPTATION_VALUE.md").write_text("\n".join(report)+"\n")
    print(json.dumps({"uniform_policy_means":dict(zip(POLICIES,map(float,uniform_means))),"uniform_best_fixed":uniform_best,"V_adapt":uniform_point,"V_CI95":[float(uniform_ci[0]),float(uniform_ci[1])],"R_oracle":uniform_oracle,"oracle_minus_HLSB":uniform_regret,"HLSB_loss_fraction_seed_portfolios":loss_freq_uniform,"max_scenario_shortfall":max_shortfall_row["scenario"],"weight_long_roots":roots,"best_policy_intervals_long":segments,"output":str(OUT)},indent=2))


if __name__ == "__main__":
    main()
