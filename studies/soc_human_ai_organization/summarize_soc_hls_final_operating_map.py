"""Summarize and plot the paired final SOC operating-map simulations."""
from __future__ import annotations
import csv, json, math, statistics
from pathlib import Path
from collections import defaultdict
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/"results/soc_hls_final_operating_map"
C=json.loads((HERE/"config/soc_hls_final_operating_map.json").read_text())
POLICIES=C["policies"]

def read(path):
    with path.open(newline="") as f:return list(csv.DictReader(f))
def write(path,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=keys,lineterminator="\n");w.writeheader();w.writerows(rows)
def avg(xs):return statistics.mean(xs) if xs else float("nan")
def ci(xs):
    n=len(xs);m=avg(xs)
    if n<2:return (m,m)
    half=student_t.ppf(.975,n-1)*statistics.stdev(xs)/math.sqrt(n)
    return m-half,m+half
def fmt(v,n=5):return f"{v:.{n}f}"
def paired(a,b):
    common=sorted(set(a)&set(b)); vals=[a[s]-b[s] for s in common]
    lo,hi=ci(vals)
    return avg(vals),lo,hi,len(vals),vals
def scenario_design():
    ret=[]
    for rho in C["rho_high_grid"]:
        for d in C["pulse_duration_grid_h"]:
            rho=float(rho);d=int(d);B=max(rho-1,0)*d;gamma=B/((1-C["rho_normal"])*C["post_pulse_recovery_h"])
            ret.append((f"rho{int(round(rho*100)):03d}_d{d:02d}",rho,d,B,gamma))
    return ret
def collect_runs():
    eps=[];series=[];modes=[];cohorts=[];priority=[]
    for phase in ("main_initial","main_extension","sla_staff"):
        base=OUT/phase
        if not base.exists():continue
        for filename,dest in (("episodes.csv",eps),("timeseries.csv",series),("modes.csv",modes),("cohorts.csv",cohorts),("priority.csv",priority)):
            p=base/filename
            if p.exists():dest.extend(read(p))
    # Identical local retry of the initial batch is deduplicated by key.
    def dedupe(rows,key):
        d={tuple(r.get(k,"") for k in key):r for r in rows};return list(d.values())
    condition_keys=["condition_kind","condition"]
    eps=dedupe(eps,["profile","seed","policy","cutoff",*condition_keys])
    series=dedupe(series,["profile","seed","policy","time_h",*condition_keys])
    modes=dedupe(modes,["profile","seed","policy","pool","time_h","mode",*condition_keys])
    cohorts=dedupe(cohorts,["profile","seed","policy","cohort",*condition_keys])
    priority=dedupe(priority,["profile","seed","policy","priority",*condition_keys])
    return eps,series,modes,cohorts,priority
def validate(eps,series):
    by=defaultdict(list)
    for r in eps:by[(r["profile"],r["seed"],r.get("condition_kind","reference"),r.get("condition",""),r["cutoff"])].append(r)
    assert all({r["policy"] for r in cell}==set(POLICIES) for cell in by.values()),"policy cell incomplete"
    assert all(len({r["trace_sha256"] for r in cell})==1 for cell in by.values()),"policy exogenous trace mismatch"
    assert all(len({r["admitted"] for r in cell})==1 for cell in by.values()),"policy denominators differ"
    assert all(int(r["admitted"])==int(r["completed"])+int(r["pending"]) for r in eps),"conservation failed"
    assert all(float(r["RN"])+1e-10>=0 and float(r["RN"])<=float(r["SLA"])+1e-8 for r in eps),"R/N outside SLA bound"
    # Deadline-free trace hashes must remain identical under deadline and roster changes.
    for kind in ("sla","staff"):
        z=defaultdict(set)
        for r in eps:
            if r.get("condition_kind")==kind:z[(r["profile"],r["seed"])].add(r["trace_sha256"])
        assert all(len(x)==1 for x in z.values()),f"exogenous traces differ across {kind} conditions"
    by_cut=defaultdict(set)
    for r in eps:by_cut[(r["profile"],r["seed"],r.get("condition_kind","reference"),r.get("condition",""),r["policy"])].add(r["cutoff"])
    assert all(cuts=={"H","HD"} for cuts in by_cut.values()),"H/H+D cutoff pair missing"
    return {"episode_cut_rows":len(eps),"scenario_seed_condition_policy_cut_cells":len(by),
            "all_policies_paired_on_trace_and_admitted_denominator":True,
            "admitted_equals_completed_plus_pending":True,"RN_bounded_by_SLA":True,
            "deadline_free_exogenous_hashes_equal_across_SLA_and_staff_conditions":True,
            "all_runs_have_H_and_HD_cutoffs":True,
            "time_series_rows":len(series),"deadline_cutoff_no_truncation":"H+24h drain exceeds max 12h deadline"}
def write_svg(path,body):path.write_text(body,encoding="utf-8")
def heatmap(path,summary,mode):
    width,height=1040,520;left,top=150,82;cw,ch=150,68
    colors={"D1":"#4676a9","P1":"#e28e40","HLS-B":"#42a176","practical_equivalence":"#b8bdc3","uncertain":"#eee4a8"}
    labels={"D1":"D1","P1":"P1","HLS-B":"HLS-B","practical_equivalence":"≈ empate","uncertain":"? incierto"}
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">','<rect width="100%" height="100%" fill="white"/>']
    title="Rendimiento terminal y diferencias pareadas" if mode=="winner" else "Presión física: Γ exceso/recovery surplus"
    s.append(f'<text x="35" y="34" font-family="sans-serif" font-size="20">{title}</text>')
    ds=[2,4,8,12,16];rhos=[1.,1.1,1.2,1.25,1.4,1.6]
    for j,d in enumerate(ds):s.append(f'<text x="{left+j*cw+cw/2}" y="65" text-anchor="middle" font-family="sans-serif" font-size="14">{d} h</text>')
    for i,rho in enumerate(rhos):s.append(f'<text x="{left-18}" y="{top+i*ch+ch/2+5}" text-anchor="end" font-family="sans-serif" font-size="14">ρ={rho:.2f}</text>')
    ix={(r["profile"]):r for r in summary}
    for i,rho in enumerate(rhos):
      for j,d in enumerate(ds):
        name=f"rho{int(round(rho*100)):03d}_d{d:02d}";r=ix[name]
        if mode=="winner":
            c=r["map_class"];label=labels[c]+"\n"+r["mean_winner"]
        else:
            gamma=float(r["Gamma"]);c="#f4f4f4" if gamma==0 else ("#f0ba81" if gamma<1 else "#d97c74")
            label=f"Γ={gamma:.2f}\nB={r['B']}"
        x=left+j*cw;y=top+i*ch
        s.append(f'<rect x="{x}" y="{y}" width="{cw-4}" height="{ch-4}" fill="{colors.get(c,c)}" stroke="#555"/>')
        lines=label.split("\n")
        for k,line in enumerate(lines):s.append(f'<text x="{x+(cw-4)/2}" y="{y+28+k*18}" text-anchor="middle" font-family="sans-serif" font-size="14">{line}</text>')
    s.append(f'<text x="{left+cw*2.5}" y="{top+6*ch+25}" text-anchor="middle" font-family="sans-serif" font-size="14">Duración del pulso (h)</text>')
    s.append(f'<text x="28" y="{top+3*ch}" transform="rotate(-90 28 {top+3*ch})" text-anchor="middle" font-family="sans-serif" font-size="14">ρ alta relativa a capacidad fluida L1</text>')
    foot="Empate práctico: todas las diferencias medias ≤0,005 R/N (umbral descriptivo). Incierto: IC95 pareado no separa al líder de todos los demás." if mode=="winner" else "B=max(ρ−1,0)·T; Γ=B/(0,15·20 h). Clasificación basada en demanda/capacidad y recuperación fijadas, antes de observar políticas."
    s.append(f'<text x="40" y="{height-20}" font-family="sans-serif" font-size="12" fill="#555">{foot}</text></svg>')
    write_svg(path,"\n".join(s))
def sla_plot(path,rows):
    width,height=1180,560;colors={"D1":"#4676a9","P1":"#e28e40","HLS-B":"#42a176"};s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">','<rect width="100%" height="100%" fill="white"/>','<text x="32" y="32" font-family="sans-serif" font-size="19">R/N por configuración SLA y perfil dinámico (cortes individuales, no mezclados)</text>']
    profiles=sorted(set(r["profile"] for r in rows));slas=["scale_075","reference","scale_125","separation_2_8","separation_8_16"]
    y0=88;group_h=145;maxv=.70;minv=.35;plotleft=250;plotright=1110
    for gi,p in enumerate(profiles):
      ybase=y0+gi*group_h;s.append(f'<text x="20" y="{ybase+55}" font-family="sans-serif" font-size="14">{p}</text>')
      for tick in (.4,.5,.6,.7):
        yy=ybase+115-(tick-minv)/(maxv-minv)*92
        s.append(f'<line x1="{plotleft}" y1="{yy:.1f}" x2="{plotright}" y2="{yy:.1f}" stroke="#e5e5e5"/><text x="{plotleft-8}" y="{yy+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="10">{tick:.1f}</text>')
      cell={r["case"]:r for r in rows if r["profile"]==p}
      for j,sla in enumerate(slas):
        x=plotleft+j*170+30
        for k,pol in enumerate(POLICIES):
          row=cell.get(sla);value_key={"D1":"D1_RN","P1":"P1_RN","HLS-B":"HLSB_RN"}[pol]
          v=float(row[value_key]) if row else float("nan"); yy=ybase+115-(v-minv)/(maxv-minv)*92
          s.append(f'<circle cx="{x+k*23}" cy="{yy:.1f}" r="5" fill="{colors[pol]}"/>')
        s.append(f'<text x="{x+15}" y="{ybase+135}" text-anchor="middle" font-family="sans-serif" font-size="11">{sla}</text>')
    for i,pol in enumerate(POLICIES):
      x=770+i*100;s.append(f'<circle cx="{x}" cy="{height-22}" r="5" fill="{colors[pol]}"/><text x="{x+10}" y="{height-18}" font-family="sans-serif" font-size="12">{pol}</text>')
    s.append(f'<text x="25" y="{height/2}" transform="rotate(-90 25 {height/2})" text-anchor="middle" font-family="sans-serif" font-size="13">R/N terminal medio</text>')
    s.append('</svg>');write_svg(path,"\n".join(s))
def main():
    eps,series,modes,cohorts,priority=collect_runs()
    validation=validate(eps,series)
    (OUT/"validation_checks.json").write_text(json.dumps(validation,indent=2)+"\n")
    base_mu=float(json.loads((OUT/"main_initial/metadata.json").read_text())["base_mu_l1"])
    main_rows=[r for r in eps if r.get("condition_kind")=="reference" and r["cutoff"]=="HD"]
    g=defaultdict(lambda:defaultdict(dict))
    for r in main_rows:g[r["profile"]][r["policy"]][int(r["seed"])]=r
    scen=[]
    for name,rho,d,b,gamma in scenario_design():
        if name not in g:continue
        cell=g[name];seed_ids=sorted(set.intersection(*(set(cell[p]) for p in POLICIES)))
        means={p:avg([float(cell[p][s]["RN"]) for s in seed_ids]) for p in POLICIES}
        diff_stats={}
        for a,bp in (("D1","P1"),("HLS-B","D1"),("HLS-B","P1")):
            delta,lo,hi,n,vals=paired({s:float(cell[a][s]["RN"]) for s in seed_ids},{s:float(cell[bp][s]["RN"]) for s in seed_ids})
            diff_stats[f"{a}_minus_{bp}"]=delta;diff_stats[f"{a}_minus_{bp}_ci_low"]=lo;diff_stats[f"{a}_minus_{bp}_ci_high"]=hi
        best=max(POLICIES,key=lambda p:means[p]);sortedmeans=sorted(means.values(),reverse=True)
        practical=all(abs(means[a]-means[bp])<=C["reporting_equivalence_margin_RN"] for a in POLICIES for bp in POLICIES)
        # Strictly separated leader: paired CI of leader-minus-each competitor excludes zero.
        leader_sep=True
        for other in POLICIES:
            if other==best:continue
            delta,lo,hi,n,_=paired({s:float(cell[best][s]["RN"]) for s in seed_ids},{s:float(cell[other][s]["RN"]) for s in seed_ids})
            if lo<=0:leader_sep=False
        map_class="practical_equivalence" if practical else (best if leader_sep else "uncertain")
        bypol={p:[r for r in eps if r["profile"]==name and r["policy"]==p and r.get("condition_kind")=="reference"] for p in POLICIES}
        hrows={p:next((r for r in bypol[p] if r["cutoff"]=="H"),None) for p in POLICIES}
        # seed-averaged H-cut backlog and R/N/SLA/quality summary.
        phys={}
        for p in POLICIES:
            ps=[r for r in bypol[p] if r["cutoff"]=="H"]
            for key in ("SLA","quality_completed","queue_l1","queue_l2","work_l1_h_est","work_l2_h_est","pending"):
                phys[f"{p}_{key}_at_H"]=avg([float(r[key]) for r in ps]) if ps else float("nan")
            pshd=[r for r in bypol[p] if r["cutoff"]=="HD"]
            for key in ("SLA","quality_completed","pending","RN"):
                phys[f"{p}_{key}_at_HD"]=avg([float(r[key]) for r in pshd]) if pshd else float("nan")
            pulse_states=[r for r in series if r["profile"]==name and r["policy"]==p and r.get("condition_kind")=="reference" and abs(float(r["time_h"])-(4+d))<1e-8]
            for key in ("queue_l1","queue_l2","work_l1_h_est","work_l2_h_est"):
                phys[f"{p}_{key}_at_pulse_end"]=avg([float(r[key]) for r in pulse_states]) if pulse_states else float("nan")
        # Recovery criterion: each queue and pending-service estimate returns to
        # its t=4h baseline for three consecutive hourly observations.
        for recovery_policy in POLICIES:
            recs=[];policy_series=[r for r in series if r["profile"]==name and r["policy"]==recovery_policy and r.get("condition_kind")=="reference"]
            for seed in seed_ids:
                ss=sorted([r for r in policy_series if int(r["seed"])==seed],key=lambda r:float(r["time_h"]))
                base=next((r for r in ss if abs(float(r["time_h"])-4)<1e-8),None)
                if not base:continue
                end=4+d;recovered=None
                for idx,r in enumerate(ss):
                    t=float(r["time_h"])
                    if t<end:continue
                    if idx+2>=len(ss):break
                    trio=ss[idx:idx+3]
                    if len(trio)<3 or any(float(trio[k]["time_h"])!=t+k for k in range(3)):continue
                    ok=True
                    for x in trio:
                        for q in ("queue_l1","queue_l2","work_l1_h_est","work_l2_h_est"):
                            if float(x[q])>float(base[q])+1e-9:ok=False
                    if ok:recovered=t-end;break
                recs.append(recovered)
            phys[f"{recovery_policy}_recovery_time_h_mean"]=avg([x for x in recs if x is not None]) if any(x is not None for x in recs) else "NR"
            phys[f"{recovery_policy}_recovery_n_recovered"]=sum(x is not None for x in recs);phys[f"{recovery_policy}_recovery_n"]=len(recs)
        # HLS-B share of pulse time in P1 using L1 history.
        shares=[];switch_in=[];switch_out=[];return_backlogs=[];return_work=[]
        for seed in seed_ids:
            ev=sorted([r for r in modes if r["profile"]==name and r["policy"]=="HLS-B" and r["pool"]=="L1" and int(r["seed"])==seed],key=lambda r:float(r["time_h"]))
            state="D1";last=0.;p1=0.;entered=None;returned=None
            for e in ev:
                t=float(e["time_h"])
                if t>last:
                    lo=max(last,4);hi=min(t,4+d)
                    if hi>lo and state=="P1":p1+=hi-lo
                new=e["mode"]
                if entered is None and state!="P1" and new=="P1" and t>=4:entered=t-4
                if entered is not None and returned is None and new=="D1" and t>=4+d:returned=t-(4+d)
                state=new;last=t
            if last<4+d and state=="P1":p1+=4+d-max(last,4)
            shares.append(p1/d);switch_in.append(entered);switch_out.append(returned)
            if returned is not None:
                return_time=4+d+returned
                candidates=[r for r in series if r["profile"]==name and r["policy"]=="HLS-B" and r.get("condition_kind")=="reference" and int(r["seed"])==seed]
                if candidates:
                    near=min(candidates,key=lambda r:abs(float(r["time_h"])-return_time))
                    return_backlogs.append(float(near["queue_l1"])+float(near["queue_l2"]))
                    return_work.append(float(near["work_l1_h_est"])+float(near["work_l2_h_est"]))
        phys["HLSB_P1_pulse_fraction_mean"]=avg(shares) if shares else float("nan")
        phys["HLSB_first_D1_to_P1_delay_mean_h"]=avg([x for x in switch_in if x is not None]) if any(x is not None for x in switch_in) else "never"
        phys["HLSB_first_P1_to_D1_after_pulse_delay_mean_h"]=avg([x for x in switch_out if x is not None]) if any(x is not None for x in switch_out) else "never"
        phys["HLSB_backlog_at_return_mean"]=avg(return_backlogs) if return_backlogs else "no returns"
        phys["HLSB_work_h_at_return_mean"]=avg(return_work) if return_work else "no returns"
        row={"profile":name,"rho_high":rho,"duration_h":d,"B":fmt(b,3),"Gamma":fmt(gamma,3),
             "design_region":"normal_or_capacity_edge" if rho<=1 else ("congestion_severe" if gamma>=1 else "congestion_operational"),
             "n_seeds":len(seed_ids),"admitted_mean":avg([float(cell["D1"][s]["admitted"]) for s in seed_ids]),
             "expected_admitted":base_mu*(float(C["rho_normal"])*(float(C["pulse_start_h"])+float(C["post_pulse_recovery_h"]))+rho*d),"expected_pulse_arrivals":base_mu*rho*d,
             "observed_pulse_arrivals_mean":avg([float(r["admitted"]) for r in cohorts if r["profile"]==name and r.get("condition_kind")=="reference" and r["cohort"]=="pulse"]),
             **{f"{p}_RN_mean":means[p] for p in POLICIES},**diff_stats,"mean_winner":best,
             "map_class":map_class,**phys}
        scen.append(row)
    write(OUT/"scenario_summary.csv",scen)
    cohort_summary=[]
    for profile in sorted({r["profile"] for r in cohorts if r.get("condition_kind")=="reference"}):
      for co in ("pre","pulse","recovery"):
        for p in POLICIES:
          vals=[r for r in cohorts if r["profile"]==profile and r.get("condition_kind")=="reference" and r["cohort"]==co and r["policy"]==p]
          cohort_summary.append({"profile":profile,"cohort":co,"policy":p,"n_seeds":len(vals),"admitted_mean":avg([float(r["admitted"]) for r in vals]),"RN_mean":avg([float(r["RN"]) for r in vals]),"SLA_mean":avg([float(r["SLA"]) for r in vals])})
    write(OUT/"cohort_summary.csv",cohort_summary)
    priority_summary=[]
    for profile in sorted({r["profile"] for r in priority if r.get("condition_kind")=="reference"}):
      for sev in ("high","medium","low"):
        for p in POLICIES:
          vals=[r for r in priority if r["profile"]==profile and r.get("condition_kind")=="reference" and r["priority"]==sev and r["policy"]==p]
          priority_summary.append({"profile":profile,"priority":sev,"policy":p,"n_seeds":len(vals),"admitted_mean":avg([float(r["admitted"]) for r in vals]),"RN_mean":avg([float(r["RN"]) for r in vals]),"SLA_mean":avg([float(r["SLA"]) for r in vals]),"quality_completed_mean":avg([float(r["quality_completed"]) for r in vals])})
    write(OUT/"priority_summary.csv",priority_summary)
    # Per-seed paired table, all 30 cells retained together for audit.
    paired_rows=[]
    for name,cell in g.items():
        seeds=sorted(set.intersection(*(set(cell[p]) for p in POLICIES)))
        for seed in seeds:
            d1=float(cell["D1"][seed]["RN"]);p1=float(cell["P1"][seed]["RN"]);hb=float(cell["HLS-B"][seed]["RN"])
            paired_rows.append({"profile":name,"seed":seed,"D1_RN":d1,"P1_RN":p1,"HLSB_RN":hb,"HLSB_minus_D1":hb-d1,"HLSB_minus_P1":hb-p1,"D1_minus_P1":d1-p1})
    write(OUT/"paired_seed_results.csv",paired_rows)
    # SLA and team conditionals are kept separate; each trace has all three policies paired.
    sensitivity=[]
    sensrows=[r for r in eps if r["condition_kind"] in ("sla","staff") and r["cutoff"]=="HD"]
    sg=defaultdict(lambda:defaultdict(dict))
    for r in sensrows:sg[(r["profile"],r["condition_kind"],r["condition"])][r["policy"]][int(r["seed"])]=r
    for (profile,kind,case),cell in sorted(sg.items()):
        common=sorted(set.intersection(*(set(cell[p]) for p in POLICIES)))
        means={p:avg([float(cell[p][s]["RN"]) for s in common]) for p in POLICIES}
        d,dl,dh,_,_=paired({s:float(cell["HLS-B"][s]["RN"]) for s in common},{s:float(cell["D1"][s]["RN"]) for s in common})
        p,pl,ph,_,_=paired({s:float(cell["HLS-B"][s]["RN"]) for s in common},{s:float(cell["P1"][s]["RN"]) for s in common})
        best=max(("D1","P1"),key=lambda x:means[x]);v=means["HLS-B"]-means[best]
        first=next(iter(cell["D1"].values()))
        r={"profile":profile,"kind":kind,"case":case,"n_seeds":len(common),"D1_RN":means["D1"],"P1_RN":means["P1"],"HLSB_RN":means["HLS-B"],"HLSB_minus_D1":d,"HLSB_D1_CI_low":dl,"HLSB_D1_CI_high":dh,"HLSB_minus_P1":p,"HLSB_P1_CI_low":pl,"HLSB_P1_CI_high":ph,"best_fixed_ex_ante_in_cell":best,"HLSB_minus_best_fixed":v}
        for k in ("T0_h","f_high","f_low","Tpulse_over_Tcrit","n_l1","n_l2","mu_l1_common_alerts_per_h","mu_l2_tasks_per_h","rho_normal_l1","rho_high_l1","rho_normal_l2","rho_high_l2","demand_absolute_base_team"):
            if k in first:r[k]=first[k]
        sensitivity.append(r)
    # Matched changes from the within-profile reference SLA or 6x3 roster.
    sens_index={(r["profile"],r["kind"],r["case"]):r for r in sensitivity}
    seed_cells={(profile,kind,case):cell for (profile,kind,case),cell in sg.items()}
    base_mu=float(json.loads((OUT/"sla_staff/metadata.json").read_text())["base_mu_l1"])
    for row in sensitivity:
        baseline_case="reference" if row["kind"]=="sla" else "L1_6_L2_3"
        base=seed_cells.get((row["profile"],row["kind"],baseline_case))
        own=seed_cells[(row["profile"],row["kind"],row["case"])]
        row["arrival_rate_high_absolute_per_h"]=base_mu*float(own["D1"][next(iter(own["D1"]))]["rho_high"])
        if base is None:
            for pol in POLICIES:row[f"{pol}_delta_vs_baseline"]=0.0;row[f"{pol}_delta_vs_baseline_CI_low"]=0.0;row[f"{pol}_delta_vs_baseline_CI_high"]=0.0
            continue
        for pol in POLICIES:
            delta,lo,hi,_,_=paired({s:float(own[pol][s]["RN"]) for s in own[pol]},
                                   {s:float(base[pol][s]["RN"]) for s in base[pol]})
            row[f"{pol}_delta_vs_baseline"]=delta;row[f"{pol}_delta_vs_baseline_CI_low"]=lo;row[f"{pol}_delta_vs_baseline_CI_high"]=hi
    write(OUT/"sla_staff_summary.csv",sensitivity)
    heatmap(HERE/"figures/soc_hls_final_policy_map.svg",scen,"winner")
    heatmap(HERE/"figures/soc_hls_final_pressure_map.svg",scen,"pressure")
    sla_plot(HERE/"figures/soc_hls_final_sla_sensitivity.svg",[r for r in sensitivity if r["kind"]=="sla"])
    # Compact resource panel: HLS-B terminal R/N per team/profile.
    staff=[r for r in sensitivity if r["kind"]=="staff"]
    staff_svg=["<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1100\" height=\"490\"><rect width=\"100%\" height=\"100%\" fill=\"white\"/><text x=\"25\" y=\"30\" font-family=\"sans-serif\" font-size=\"19\">Plantilla y R/N terminal condicional; demanda absoluta fija</text>"]
    for i,r in enumerate(staff):
        yy=70+i*19;label=f"{r['profile']} | {r['case']} ({r.get('rho_high_l1','')}/{r.get('rho_high_l2','')})"
        staff_svg.append(f"<text x=\"10\" y=\"{yy}\" font-family=\"sans-serif\" font-size=\"12\">{label}</text><text x=\"920\" y=\"{yy}\" font-family=\"sans-serif\" font-size=\"12\">D1 {float(r['D1_RN']):.3f} · P1 {float(r['P1_RN']):.3f} · HLS-B {float(r['HLSB_RN']):.3f}</text>")
    staff_svg.append("</svg>");write_svg(HERE/"figures/soc_hls_final_staffing_sensitivity.svg","\n".join(staff_svg))
    print(json.dumps({"scenario_cells":len(scen),"sensitivity_cells":len(sensitivity),"paired_episode_seed_rows":len(paired_rows),"map_classes":{k:sum(r['map_class']==k for r in scen) for k in set(r['map_class'] for r in scen)},"results":str(OUT)},indent=2))
if __name__=="__main__":main()
