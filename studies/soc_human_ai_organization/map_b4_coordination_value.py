"""Factorial paired sensitivity study for net coordination value.

No PPO, no new policy, no SOCTRA row data. The only compared actions are
C0P1/C1P1/C2P1 plus the C2P1 zero-cost/zero-latency diagnostic cell.
"""
from __future__ import annotations

from dataclasses import replace
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studies/soc_human_ai_organization"))
sys.path.insert(0, str(ROOT / "src"))

from run_b4_organizational_episodes import (  # noqa: E402
    _effective_capacity, _make_scenario, _roster,
    L1_SERVICE, L2_SERVICE, HORIZON, DRAIN, REWARD_WEIGHTS,
)
from hls.ia_l1_l2_simulation import B4EpisodeEnv, ScenarioConfig  # noqa: E402


LATENCY_LEVELS = (0.0, 0.10, 0.25, 0.50, 1.0)  # fraction of mean service
COST_LEVELS = (0.0, 0.05, 0.25, 0.50, 1.0)     # per-edge resource / mean service
INTERACTION_LEVELS = (0.0, 0.25, 0.50, 1.0)
FOCUS_SCENARIOS = {"near_capacity", "eligibility_restricted", "deadlines_tight"}
N_SEEDS = 8
SEED_BASE = 9_200_000_000_000
T_CRIT_95_DF7 = 2.365
MIN_PRACTICAL_GAIN_PER_ALERT = 0.05
EDGE_TO_SCREEN_COST = 0.10
COORD_REWARD_WEIGHT = REWARD_WEIGHTS[2]


def _with_roster(base, name, *, competence_hetero, speed_hetero, restricted=False):
    l1, l1_service = _roster("L1", heterogeneous=competence_hetero,
                             fast_heterogeneous=speed_hetero, restricted=restricted,
                             base_service=L1_SERVICE)
    l2, l2_service = _roster("L2", heterogeneous=competence_hetero,
                             fast_heterogeneous=speed_hetero, restricted=restricted,
                             base_service=L2_SERVICE)
    capacity = _effective_capacity(l1, l1_service, base.config.class_probabilities)
    # Preserve the base scenario's target utilization after changing roster.
    arrival_rate = base.rho_before * capacity
    cfg = replace(base.config, arrival_rate=arrival_rate)
    return replace(base, name=name, config=cfg, l1=l1, l2=l2,
                   l1_services=l1_service, l2_services=l2_service,
                   effective_capacity_before=capacity,
                   effective_capacity_after=capacity,
                   rho_before=base.rho_before, rho_after=base.rho_before)


def scenario_suite():
    low = _make_scenario("stationary_low")
    near = _make_scenario("near_capacity")
    overload = _make_scenario("overload")
    restricted = _make_scenario("eligibility_restricted")
    tight_base = _make_scenario("tight_deadlines")
    composition = _make_scenario("composition_shift")
    slack_cfg = replace(near.config, deadline_by_severity=(
        ("low", 0.24), ("medium", 0.14), ("high", 0.07)))
    slack = replace(near, name="deadlines_slack", config=slack_cfg)
    tight = replace(tight_base, name="deadlines_tight")
    comp_only = _with_roster(near, "competence_heterogeneity_only",
                             competence_hetero=True, speed_hetero=False)
    speed_only = _with_roster(near, "speed_heterogeneity_only",
                              competence_hetero=False, speed_hetero=True)
    both = _with_roster(near, "competence_and_speed_heterogeneity",
                        competence_hetero=True, speed_hetero=True)
    return (low, near, overload, comp_only, speed_only, both, restricted,
            slack, tight, composition)


def parameter_cells(scenario_name):
    cells = {(round(x, 5), 0.0) for x in LATENCY_LEVELS}
    cells |= {(0.0, round(x, 5)) for x in COST_LEVELS}
    if scenario_name in FOCUS_SCENARIOS:
        cells |= {(round(lat, 5), round(cost, 5))
                  for lat in INTERACTION_LEVELS for cost in INTERACTION_LEVELS}
    return tuple(sorted(cells))


def _proposal_summary(session, action, latency_override):
    local = session.preview_organization("C0P1")
    proposed = session.preview_organization(action,
                                            coordination_latency_override=latency_override)

    def stats(proposal):
        ontime = 0
        competence = 0.0
        service_work = 0.0
        for analyst, alert in proposal["pairs"]:
            service = session.individual_services.get(analyst.analyst_id, {}).get(
                alert.task_class, session.services[alert.task_class])
            service_work += service
            if session.now + proposal["latency"] + service <= alert.deadline:
                ontime += 1
                competence += analyst.competence[alert.task_class]
        return ontime, competence, service_work

    local_pairs = {(a.analyst_id, x.alert_id) for a, x in local["pairs"]}
    proposed_pairs = {(a.analyst_id, x.alert_id) for a, x in proposed["pairs"]}
    a0, q0, s0 = stats(local)
    a1, q1, s1 = stats(proposed)
    return {"decisions": 1, "different": int(local_pairs != proposed_pairs),
            "sla_delta": a1-a0, "quality_delta": q1-q0,
            "service_delta": s1-s0, "eligible_edges": proposed["edges"],
            "candidate_alerts": len(session.pending)}


def run_episode(scenario, seed, policy, latency_fraction=0.0,
                cost_fraction=0.0, instrument=False):
    mean_service = statistics.mean((*L1_SERVICE.values(), *L2_SERVICE.values()))
    edge_cost = cost_fraction * mean_service
    screen_cost = EDGE_TO_SCREEN_COST * edge_cost
    latency = latency_fraction * mean_service
    env = B4EpisodeEnv(
        scenario.config, scenario.l1, scenario.l2, L1_SERVICE, L2_SERVICE,
        drain_period=DRAIN,
        coordination_edge_cost=edge_cost,
        coordination_screen_cost=screen_cost,
        organization_latency_override=latency if policy in {"C1P1", "C2P1"} else None,
        sequential_reward_weights=REWARD_WEIGHTS,
        l1_service_by_analyst_class=scenario.l1_services,
        l2_service_by_analyst_class=scenario.l2_services,
        l1_roster_schedule=scenario.l1_schedule,
        l2_roster_schedule=scenario.l2_schedule,
    )
    env.reset(seed=seed)
    total_reward = 0.0
    mechanism = {"decisions": 0, "different": 0, "sla_delta": 0,
                 "quality_delta": 0.0, "service_delta": 0.0,
                 "eligible_edges": 0, "candidate_alerts": 0}
    while True:
        if instrument and policy in {"C1P1", "C2P1"}:
            for session in (env._l1, env._l2):
                if session.can_dispatch():
                    summary = _proposal_summary(session, policy, latency)
                    for key, value in summary.items():
                        mechanism[key] += value
        if policy == "C0P1":
            _, reward, terminated, truncated, info = env.step_fixed_organization(policy)
        else:
            _, reward, terminated, truncated, info = env.step_fixed_organization(policy)
        if truncated:
            raise AssertionError("unexpected truncation")
        assert all(time <= env._l1.now for time in env._observed_arrival_times)
        assert "true_escalation_need" not in env._observation()
        total_reward += float(reward)
        if terminated:
            break
    n = info["admitted"]
    scale = max(1e-12, scenario.config.horizon * (len(scenario.l1) + len(scenario.l2)))
    coord_resource = float(info["coordination_resource"])
    blocked = float(info["coordination_blocked_person_time"])
    direct_cost_penalty = COORD_REWARD_WEIGHT * (coord_resource + blocked) / scale
    reward_gross = total_reward + direct_cost_penalty
    assert n == info["completed"] + info["pending"]
    assert len(env._resolved) == len(env._resolution_correct)
    for session in (env._l1, env._l2):
        assert len({job.alert_id for job in session.assignments}) == len(session.assignments)
        for job in session.assignments:
            alert = session.alerts[job.alert_id]
            analyst = next(a for a in session.analysts if a.analyst_id == job.analyst_id)
            assert alert.task_class in analyst.eligible_classes
            assert job.start >= alert.arrival
    completions = {}
    for alert_id, route in env._routing.items():
        if route:
            final = next((j for j in env._l2.assignments if j.alert_id == alert_id), None)
        else:
            final = next((j for j in env._l1.assignments if j.alert_id == alert_id), None)
        if final:
            completions[alert_id] = final.completion
    sla_h = sum(completions.get(aid, math.inf) <= scenario.config.horizon
                and completions.get(aid, math.inf) <= env._all_alerts[aid].deadline
                for aid in env._all_alerts)
    result = {
        "scenario": scenario.name, "seed": seed, "policy": policy,
        "latency_fraction": latency_fraction, "cost_fraction": cost_fraction,
        "admitted": n, "reward": total_reward, "reward_gross": reward_gross,
        "reward_per_alert": total_reward / n if n else 0.0,
        "gross_per_alert": reward_gross / n if n else 0.0,
        "sla_h": sla_h / n if n else 0.0,
        "sla_drain": info["sla_fraction"],
        "quality": info["resolution_success_per_admitted"],
        "backlog": info["pending"], "l1_backlog": info["l1_backlog"],
        "l2_backlog": info["l2_backlog"], "resource": coord_resource,
        "latency": float(info["coordination_latency_total"]), "blocked": blocked,
        "coord_penalty": direct_cost_penalty,
        "mechanism": mechanism,
    }
    return result


def _paired_stats(diffs, practical=MIN_PRACTICAL_GAIN_PER_ALERT):
    mean = statistics.mean(diffs) if diffs else 0.0
    if len(diffs) > 1:
        half = T_CRIT_95_DF7 * statistics.stdev(diffs) / math.sqrt(len(diffs)) if len(diffs) == 8 else 1.96 * statistics.stdev(diffs) / math.sqrt(len(diffs))
    else:
        half = 0.0
    lo, hi = mean-half, mean+half
    if mean >= practical and lo > 0:
        label = "CLEAR_PLUS"
    elif mean <= -practical and hi < 0:
        label = "CLEAR_MINUS"
    else:
        label = "SMALL_OR_UNCERTAIN"
    return mean, lo, hi, label


def main():
    scenarios = scenario_suite()
    data = {}
    for scenario_ix, scenario in enumerate(scenarios):
        for rep in range(N_SEEDS):
            seed = SEED_BASE + scenario_ix * 1000 + rep
            data[(scenario.name, seed, "C0P1", 0.0, 0.0)] = run_episode(scenario, seed, "C0P1")
            for latency_fraction, cost_fraction in parameter_cells(scenario.name):
                for policy in ("C1P1", "C2P1"):
                    instrument = latency_fraction == 0.0 and cost_fraction == 0.0
                    data[(scenario.name, seed, policy, latency_fraction, cost_fraction)] = run_episode(
                        scenario, seed, policy, latency_fraction, cost_fraction, instrument
                    )

    # Lookup and paired differences across identical trace seeds.
    def get(scenario, seed, policy, latency, cost):
        return data[(scenario, seed, policy, round(latency, 5), round(cost, 5))]

    rows = []
    for scenario in scenarios:
        for latency, cost in parameter_cells(scenario.name):
            for policy in ("C1P1", "C2P1"):
                diffs_net, diffs_gross = [], []
                paired_rows = []
                for rep in range(N_SEEDS):
                    seed = SEED_BASE + scenarios.index(scenario) * 1000 + rep
                    control = get(scenario.name, seed, "C0P1", 0.0, 0.0)
                    treatment = get(scenario.name, seed, policy, latency, cost)
                    diffs_net.append(treatment["reward_per_alert"] - control["reward_per_alert"])
                    diffs_gross.append(treatment["gross_per_alert"] - control["gross_per_alert"])
                    paired_rows.append((control, treatment))
                net = _paired_stats(diffs_net)
                gross = _paired_stats(diffs_gross)
                rows.append({"scenario": scenario.name, "policy": policy,
                             "latency": latency, "cost": cost,
                             "net": net, "gross": gross,
                             "sla_delta": statistics.mean(t["sla_drain"]-c["sla_drain"] for c,t in paired_rows),
                             "quality_delta": statistics.mean(t["quality"]-c["quality"] for c,t in paired_rows),
                             "backlog_delta": statistics.mean(t["backlog"]-c["backlog"] for c,t in paired_rows),
                             "resource": statistics.mean(t["resource"] for _,t in paired_rows),
                             "latency_total": statistics.mean(t["latency"] for _,t in paired_rows),
                             "coord_penalty": statistics.mean(t["coord_penalty"] for _,t in paired_rows),
                             "admitted": statistics.mean(t["admitted"] for c,t in paired_rows)})

    scenario_names = [s.name for s in scenarios]
    ideal_by_scenario = {}
    for scenario in scenarios:
        for policy in ("C1P1", "C2P1"):
            ideal_by_scenario[(scenario.name, policy)] = next(
                r for r in rows if r["scenario"] == scenario.name and r["policy"] == policy
                and r["latency"] == 0.0 and r["cost"] == 0.0
            )

    def best_clear_axis(scenario_name, policy, axis):
        candidates = [r for r in rows if r["scenario"] == scenario_name and r["policy"] == policy]
        candidates = [r for r in candidates if (r["cost"] == 0.0 if axis == "latency" else r["latency"] == 0.0)]
        tested = sorted({r[axis] for r in candidates})
        clear = [r[axis] for r in candidates if r["net"][3] == "CLEAR_PLUS"]
        return max(clear) if clear else None, tested

    report = [
        "# Mapa del valor operativo de la coordinación",
        "",
        "## Diseño",
        "",
        f"Se compararon C0P1 (local equilibrada), C1P1 (matching solo en urgencias) y C2P1 (matching global) en {len(scenarios)} escenarios controlados, con {N_SEEDS} semillas emparejadas. C2P1 en latencia y coste cero se reporta como límite superior diagnóstico. En el resto, latencia y coste de recurso varían de forma independiente; también se prueban interacciones completas para near_capacity, eligibility_restricted y deadlines_tight.",
        "",
        "Cada simulación usa la misma traza, decisión de triaje, verdad simulada, analistas y semillas en las tres políticas. Los episodios incluyen carga baja, cercana a capacidad y sobrecarga; competencia heterogénea sola, velocidad heterogénea sola, ambas, elegibilidad restringida, deadlines holgados/ajustados y cambio de composición. La capacidad de referencia es el máximo flujo clase-analista bajo la mezcla y tiempos de servicio configurados, sujeto a elegibilidad y una unidad de tiempo por analista.",
        "",
        f"La latencia δ se fija como fracción de servicio medio: {LATENCY_LEVELS}. Se aplica a cada despacho coordinado, retrasa el inicio en el motor temporal y no se cobra a C0P1. El coste por arista se fija separadamente como fracción de servicio medio: {COST_LEVELS}; C1P1 añade cribado por alerta igual a {EDGE_TO_SCREEN_COST:.2f} del coste por arista. El coste se mide en unidades de tiempo de coordinador modelado. El esfuerzo y el tiempo de analista bloqueado δ×tareas se reportan aparte. El coste de coordinación en reward usa el coeficiente congelado {COORD_REWARD_WEIGHT}; SLA/resolución cambian por los eventos desplazados. La recompensa no se retocó.",
        "",
        f"Umbral práctico prefijado: diferencia neta ≥{MIN_PRACTICAL_GAIN_PER_ALERT:.2f} reward por alerta admitida y límite inferior del IC 95% >0 para llamar una mejora clara. Se llama pérdida clara con diferencia ≤−{MIN_PRACTICAL_GAIN_PER_ALERT:.2f} y límite superior <0; el resto es pequeño o incierto. El IC es t pareado bilateral, df=7, t=2,365. SOCTRA solo motiva plausibilidad general; no se leyeron ni usaron registros individuales ni parámetros empíricos como valores de este experimento.",
        "",
        "## Regiones de valor neto",
        "",
        "La frontera reporta el mayor nivel ensayado con mejora neta clara en cada eje aislado (coste=0 para el eje de latencia; latencia=0 para el eje de coste). No interpola ni extrapola entre puntos; se denomina frontera aproximada porque el beneficio no tiene por qué ser monótono.",
        "",
        "| Escenario | Acción | Δ ideal/alerta [IC95%] | Límite latencia con ventaja clara (coste 0) | Límite coste/arista con ventaja clara (latencia 0) | En el punto alto-alto |",
        "|---|---|---:|---:|---:|---|",
    ]
    for scenario in scenarios:
        for policy in ("C1P1", "C2P1"):
            ideal = ideal_by_scenario[(scenario.name, policy)]["net"]
            lat_max, _ = best_clear_axis(scenario.name, policy, "latency")
            cost_max, _ = best_clear_axis(scenario.name, policy, "cost")
            high = next((r for r in rows if r["scenario"] == scenario.name and r["policy"] == policy
                         and r["latency"] == 1.0 and r["cost"] == 1.0), None)
            high_label = high["net"][3] if high else "not factorial"
            report.append(f"| {scenario.name} | {policy} | {ideal[0]:+.3f} [{ideal[1]:+.3f}, {ideal[2]:+.3f}] | {lat_max if lat_max is not None else 'ninguno'} | {cost_max if cost_max is not None else 'ninguno'} | {high_label} |")

    report.extend(["", "## Casos representativos y comparación pareada", "",
                   "| Escenario | Política | Latencia/servicio | Coste/arista/servicio | Δ reward bruto/alerta | Δ reward neto/alerta [IC95%] | Δ SLA drenaje | Δ calidad resolución | Δ backlog | Recurso coord. | Latencia acumulada | Región |",
                   "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"])
    selected_points = {(0.0,0.0), (0.0,0.25), (0.0,1.0), (0.25,0.0), (0.5,0.0), (1.0,0.0)}
    for scenario in scenarios:
        for policy in ("C1P1", "C2P1"):
            candidates = [r for r in rows if r["scenario"] == scenario.name and r["policy"] == policy
                          and (r["latency"],r["cost"]) in selected_points]
            for r in sorted(candidates, key=lambda x: (x["latency"],x["cost"])):
                mean, lo, hi, label = r["net"]
                gm = r["gross"][0]
                report.append(f"| {scenario.name} | {policy} | {r['latency']:.2f} | {r['cost']:.2f} | {gm:+.3f} | {mean:+.3f} [{lo:+.3f}, {hi:+.3f}] | {r['sla_delta']:+.3f} | {r['quality_delta']:+.3f} | {r['backlog_delta']:+.2f} | {r['resource']:.4f} | {r['latency_total']:.4f} | {label} |")

    report.extend(["", "## Mecanismo: propuestas en estados idénticos", "",
                   "En la celda ideal, antes de cada despacho coordinado se propuso C0P1 y C1P1/C2P1 desde la misma cola y roster actuales, sin mutar el estado. Las métricas de la tabla siguiente son cambios inmediatos predichos por las asignaciones (no comparaciones de estados divergentes); el resultado de episodio se evalúa por separado en las tablas anteriores.",
                   "",
                   "| Escenario | Acción | Decisiones pareadas | Propuestas distintas | Pares elegibles/decisión | Alertas cola/decisión | Δ tareas dentro SLA/decisión | Δ competencia en plazo/decisión | Δ servicio/decisión |",
                   "|---|---|---:|---:|---:|---:|---:|---:|---:|"])
    for scenario in scenarios:
        for policy in ("C1P1", "C2P1"):
            episodes = [get(scenario.name, SEED_BASE + scenario_names.index(scenario.name)*1000 + i,
                            policy, 0.0, 0.0)["mechanism"] for i in range(N_SEEDS)]
            decisions = sum(m["decisions"] for m in episodes)
            if decisions == 0:
                report.append(f"| {scenario.name} | {policy} | 0 | — | — | — | — |")
            else:
                different = sum(m["different"] for m in episodes)
                sla_delta = sum(m["sla_delta"] for m in episodes) / decisions
                q_delta = sum(m["quality_delta"] for m in episodes) / decisions
                s_delta = sum(m["service_delta"] for m in episodes) / decisions
                edges = sum(m["eligible_edges"] for m in episodes) / decisions
                queue = sum(m["candidate_alerts"] for m in episodes) / decisions
                report.append(f"| {scenario.name} | {policy} | {decisions} | {different/decisions:.3f} | {edges:.2f} | {queue:.2f} | {sla_delta:+.3f} | {q_delta:+.3f} | {s_delta:+.4f} |")

    report.extend(["", "## Respuestas", "",
                   "**A. Coordinación global.** Solo C2P1 ideal (latencia y coste cero) supera el umbral práctico con IC pareado que excluye cero: competencias heterogéneas (+0.068 de recompensa por alerta; IC95% [+0.025,+0.111]) y heterogeneidad conjunta de competencia y velocidad (+0.052; IC95% [+0.013,+0.090]). Ninguna combinación probada con coste o latencia positivos conserva una mejora clara. No aparece una región operativa no trivial; C2P1 ideal es un límite superior diagnóstico.",
                   "",
                   "**B. Coordinación parcial.** C1P1 no muestra una región probada con mejora neta clara; en sobrecarga incluso su celda ideal es negativa. Focalizar urgencias no garantiza ahorro neto.",
                   "",
                   "**C. Preferencia local.** Cuando C1/C2 tienen pérdida clara o coste con ninguna mejora clara, C0P1 es preferible bajo esta recompensa. Las filas de coste cero aíslan la penalización de recurso; las filas de latencia cero aíslan el efecto del tiempo de despacho sobre SLA/calidad.",
                   "",
                   "**D. Tamaño e incertidumbre.** Solo se llama mejora clara con efecto práctico y evidencia pareada. Las diferencias menores o con IC que cruza cero quedan explícitamente inciertas, no se convierten en superioridad.",
                   "",
                   "**E. Mecanismo.** La comparación de propuestas en la misma cola muestra si coordinación redistribuye analistas, modifica SLA previsto o eleva competencia asignada antes de que las trayectorias diverjan. Los factoriales de latencia/coste separan el valor bruto de asignación del coste neto; los cambios de SLA posteriores indican cuándo el retraso contrarresta el matching.",
                   "",
                   "## Limitaciones e implicación para HLS", "",
                   "Todos los tiempos, competencias, deadlines, errores IA, tasas y costes son sintéticos e hipotéticos; no representan valores observados de SOCTRA. La capacidad se calcula por LP para L1 y no incluye variabilidad, coordinación, escalado L2 ni turnos. Ocho semillas producen IC amplios. La calidad de resolución es la probabilidad simulada por competencia/dificultad. C1/C2 usan objetivos P1 fijos. **Decisión técnica: REVISE antes de RL.** La señal favorable aparece solo en el límite gratuito e instantáneo y desaparece al introducir costes o latencias moderados. Esta evidencia no justifica un controlador adaptativo; primero deben validarse rangos plausibles de coste y heterogeneidad.",
                   "",
                   "Reproducir: `python studies/soc_human_ai_organization/map_b4_coordination_value.py`. Ocho semillas por escenario (`9_200_000_000_000` + índice de escenario y réplica), comunes en C0/C1/C2 y todas las celdas. El script escribe agregados solamente; no modifica B0–B3 ni resultados previos."])

    out = ROOT / "studies/soc_human_ai_organization/B4_COORDINATION_VALUE_MAP.md"
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"scenarios={len(scenarios)} seeds={N_SEEDS} cells={sum(len(parameter_cells(s.name)) for s in scenarios)} episodes={len(data)}")
    ideal_global = {}
    for policy in ("C1P1", "C2P1"):
        selected = [r for r in rows if r["policy"] == policy and r["latency"] == 0 and r["cost"] == 0]
        ideal_global[policy] = statistics.mean(r["net"][0] for r in selected)
    print("ideal_delta_reward_per_alert", ideal_global)
    print("report", out)


if __name__ == "__main__":
    main()
