"""Small development-only pilot for the observable HLS-A selector."""
from __future__ import annotations

import csv
import json
import statistics
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_allocation import HLSAConfig
from hls.rq1_l1_l2 import simulate_l1_l2
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE, BASE_SERVICE_L1_H, BASE_SERVICE_L2_H

HERE = Path(__file__).resolve().parent
cfg = json.loads((HERE / "config/soc_hlsa_pilot.json").read_text())
out = ROOT / "results/soc_hlsa_pilot"
out.mkdir(parents=True, exist_ok=True)
l1, l2, s1, s2 = _roster([0, 1, 2, 3, 4, 5])
rows = []
switches = []
mode_history = []

for scenario in cfg["scenarios"]:
    base = REFERENCE.scenario_config(arrival_rate_per_h=cfg["base_capacity_alerts_per_h"] * scenario["base_rho"])
    base = replace(base, horizon=cfg["horizon_h"])
    if "burst_window_h" in scenario:
        begin, end = scenario["burst_window_h"]
        base = replace(base, burst_window=(begin, end, scenario["burst_rho"] / scenario["base_rho"]))
    if "shift_h" in scenario:
        base = replace(base, arrival_rate_shift_after=scenario["shift_h"],
                       arrival_rate_after=cfg["base_capacity_alerts_per_h"] * scenario["after_rho"])
    for seed in cfg["seeds"]:
        generated = generate_alerts(base, seed)
        admitted = [x for x in generated if x.routed.alert.arrival < cfg["horizon_h"]]
        for label, thresholds in [("D1", None), ("P1", None)] + [
            (f'HLS-A_{x["low"]}_{x["high"]}', x) for x in cfg["candidates"]
        ]:
            sim = simulate_l1_l2(tuple(x.routed for x in generated), l1, l2,
                                 BASE_SERVICE_L1_H, BASE_SERVICE_L2_H,
                                 policy="HLS-A" if thresholds else label,
                                 admission_horizon=cfg["horizon_h"], drain_period=cfg["drain_h"],
                                 coordination_latency=0.0, coordination_edge_cost=0.0,
                                 decision_mode="hypothetical_recommendation_acceptance", random_seed=seed,
                                 l1_service_by_analyst_class=s1, l2_service_by_analyst_class=s2,
                                 hlsa_config=HLSAConfig(**thresholds) if thresholds else HLSAConfig())
            first = {a.alert_id: a for a in sim.l1_simulation.assignments}
            second = {a.alert_id: a for a in sim.l2_simulation.assignments}
            route = {x.alert_id: x.scenario_routing_decision for x in sim.escalation_records}
            assert len(first) == len(sim.l1_simulation.assignments)
            assert len(second) == len(sim.l2_simulation.assignments)
            final = [(x, second.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id]
                      else first.get(x.routed.alert.alert_id)) for x in admitted]
            n = len(admitted)
            ontime = [(x, a) for x, a in final if a is not None and a.completion <= 48.0
                      and a.completion <= x.routed.alert.deadline]
            rn = sum(a.competence * (1 - .35 * x.difficulty) for x, a in ontime) / n
            history = sim.l1_simulation.hlsa_history
            rows.append(dict(scenario=scenario["name"], seed=seed, policy=label, admitted=n,
                             R_per_admitted=rn, sla=len(ontime)/n,
                             quality_completed=statistics.mean(a.competence * (1-.35*x.difficulty)
                                 for x, a in final if a is not None and a.completion <= 48.0),
                             switches=sum(x.switched for x in history),
                             d1_decisions=sum(x.mode == "D1" for x in history),
                             p1_decisions=sum(x.mode == "P1" for x in history)))
            switches += [dict(scenario=scenario["name"], seed=seed, policy=label, time_h=x.time,
                              mode=x.mode, pressure=x.pressure, pending=x.pending,
                              occupied=x.occupied, switched=x.switched) for x in history if x.switched]
            mode_history += [dict(scenario=scenario["name"], seed=seed, policy=label, time_h=x.time,
                                  mode=x.mode, pressure=x.pressure, pending=x.pending,
                                  occupied=x.occupied, switched=x.switched) for x in history]
    print(scenario["name"], "complete", flush=True)

for name, data in [("episodes.csv", rows), ("switches.csv", switches),
                   ("mode_history.csv", mode_history)]:
    with (out / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
print("development results:")
for scenario in cfg["scenarios"]:
    for label in sorted({x["policy"] for x in rows}):
        group = [x for x in rows if x["scenario"] == scenario["name"] and x["policy"] == label]
        print(scenario["name"], label,
              round(statistics.mean(x["R_per_admitted"] for x in group), 4),
              round(statistics.mean(x["switches"] for x in group), 2))
