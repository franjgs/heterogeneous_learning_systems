"""Same-state and episode-level diagnostic for coordination value."""
from __future__ import annotations

import math
import statistics
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studies/soc_human_ai_organization"))
sys.path.insert(0, str(ROOT / "src"))

from run_b4_organizational_episodes import (  # noqa: E402
    _make_scenario, CLASSES, L1_SERVICE, L2_SERVICE, DRAIN,
    EDGE_COST, SCREEN_COST, HISTORICAL_LATENCY, REWARD_WEIGHTS,
)
from hls.ia_l1_l2_simulation import B4EpisodeEnv  # noqa: E402
from hls.rq1_allocation import (  # noqa: E402
    _dispatch_organization, _dispatch_coordinated,
)

SCENARIO_NAMES = ("stationary_low", "near_capacity", "overload",
                  "tight_deadlines", "eligibility_restricted",
                  "heterogeneous_skills_speeds")
SEEDS = (970101, 970102, 970103, 970104, 970105, 970106, 970107, 970108)
POLICIES = ("D1-S", "C0P1", "C2P1")
T95_DF7 = 2.365
REPORT = ROOT / "studies/soc_human_ai_organization/COORDINATION_OPPORTUNITY_ANALYSIS.md"


def _build_env(scenario, seed):
    env = B4EpisodeEnv(
        scenario.config, scenario.l1, scenario.l2, L1_SERVICE, L2_SERVICE,
        drain_period=DRAIN,
        coordination_latency=HISTORICAL_LATENCY,
        coordination_edge_cost=EDGE_COST,
        coordination_screen_cost=SCREEN_COST,
        sequential_reward_weights=REWARD_WEIGHTS,
        l1_service_by_analyst_class=scenario.l1_services,
        l2_service_by_analyst_class=scenario.l2_services,
        l1_roster_schedule=scenario.l1_schedule,
        l2_roster_schedule=scenario.l2_schedule,
        diagnostic_d1=True,
    )
    env.reset(seed=seed)
    signature = tuple((x.routed.alert.alert_id, x.routed.alert.arrival,
                       x.routed.alert.task_class, x.routed.alert.deadline,
                       x.severity, x.difficulty, x.true_escalation_need,
                       x.routed.soctra_recommendation) for x in env._admitted)
    return env, signature


def _run_episode(scenario, seed, policy):
    env, signature = _build_env(scenario, seed)
    total_reward = 0.0
    max_backlog = 0
    coordination_decisions = 0
    solo_coordination_decisions = 0
    while True:
        if policy == "D1-S":
            _, reward, terminated, truncated, info = env.step_fixed(policy)
        else:
            if policy == "C2P1":
                for session in (env._l1, env._l2):
                    if session.can_dispatch():
                        coordination_decisions += 1
                        solo_coordination_decisions += int(len(session.available_analysts()) == 1)
            _, reward, terminated, truncated, info = env.step_fixed_organization(policy)
        if truncated:
            raise AssertionError("episode truncated unexpectedly")
        total_reward += float(reward)
        max_backlog = max(max_backlog, len(env._l1.pending), len(env._l2.pending))
        if terminated:
            break
    completed = info["completed"]
    admitted = info["admitted"]
    assert completed + info["pending"] == admitted
    final_jobs = {}
    for aid, escalated in env._routing.items():
        session = env._l2 if escalated else env._l1
        job = next((j for j in session.assignments if j.alert_id == aid), None)
        if job is not None:
            final_jobs[aid] = job
    expected_quality = sum(
        job.competence * (1.0 - 0.35 * env._evaluation[aid].difficulty)
        for aid, job in final_jobs.items()
    ) / admitted if admitted else 0.0
    return {
        "signature": signature,
        "reward": total_reward,
        "sla": info["sla_fraction"],
        "quality": info["resolution_success_per_admitted"],
        "quality_modelled": expected_quality,
        "mean_wait": statistics.mean(
            max(0.0, job.start - session.alerts[job.alert_id].arrival)
            for session in (env._l1, env._l2) for job in session.assignments
        ) if completed else 0.0,
        "completed": completed, "admitted": admitted,
        "pending": info["pending"], "max_backlog": max_backlog,
        "coordination_resource": info["coordination_resource"],
        "coordination_latency": info["coordination_latency_total"],
        "coordination_person_time": info["coordination_person_time"],
        "action_counts": info["organization_action_counts"],
        "coordination_decisions": coordination_decisions,
        "solo_coordination_decisions": solo_coordination_decisions,
    }, env


def _candidate_metrics(pairs, now, latency, services, individual, service_alerts):
    rows = []
    for analyst, alert in pairs:
        service = individual.get(analyst.analyst_id, {}).get(alert.task_class, services[alert.task_class])
        rows.append((analyst, alert, service))
    return {
        "pairs": tuple((a.analyst_id, x.alert_id) for a, x, _ in rows),
        "alerts": {x.alert_id for _, x, _ in rows},
        "competence": sum(a.competence[x.task_class] for a, x, _ in rows),
        "ontime": sum(now + latency + service <= x.deadline for _, x, service in rows),
        "service": sum(service for _, _, service in rows),
        "n": len(rows),
    }


def _assignment_summary(pairs, free, now, services, individual, pending):
    analyst_index = {a.analyst_id: i + 1 for i, a in enumerate(sorted(free, key=lambda a: a.analyst_id))}
    per_class_rank = {}
    for task_class in {a.task_class for a in pending.values()}:
        ordered = sorted((a for a in pending.values() if a.task_class == task_class),
                         key=lambda a: (a.deadline, a.arrival, a.alert_id))
        per_class_rank.update({a.alert_id: i + 1 for i, a in enumerate(ordered)})
    rows = []
    for analyst, alert in sorted(pairs, key=lambda pair: pair[0].analyst_id):
        duration = individual.get(analyst.analyst_id, {}).get(alert.task_class, services[alert.task_class])
        slack = alert.deadline - now - duration
        rows.append(f"A{analyst_index[analyst.analyst_id]}→{alert.task_class}#{per_class_rank[alert.alert_id]}[{slack:+.3f}]")
    return ", ".join(rows) if rows else "—"


def _same_state_opportunities(scenario, seed):
    env, _ = _build_env(scenario, seed)
    while True:
        _, _, terminated, truncated, _ = env.step_fixed("D1-S")
        if truncated:
            raise AssertionError("diagnostic episode truncated")
        if terminated:
            break

    records = []
    for session_name, session in (("L1", env._l1), ("L2", env._l2)):
        analysts_by_id = {a.analyst_id: a for a in session.analysts}
        for snap in session.d1_dispatch_snapshots:
            pending = {aid: session.alerts[aid] for aid in snap.queue_alert_ids}
            free = [analysts_by_id[aid] for aid in snap.available_analyst_ids]
            if len(free) < 2 or len(pending) < 2:
                continue
            eligible_edges = [(a, alert) for a in free for alert in pending.values()
                              if alert.task_class in a.eligible_classes]
            if len(eligible_edges) < 2:
                continue
            feasible_analysts_per_class = {
                k: [a for a in free if k in a.eligible_classes]
                for k in {x.task_class for x in pending.values()}
            }
            heterogeneous = any(
                len(aa) > 1 and (
                    max(a.competence[k] for a in aa) - min(a.competence[k] for a in aa) > 1e-9
                    or max(session.individual_services.get(a.analyst_id, {}).get(k, session.services[k]) for a in aa)
                    - min(session.individual_services.get(a.analyst_id, {}).get(k, session.services[k]) for a in aa) > 1e-9
                ) for k, aa in feasible_analysts_per_class.items()
            )
            local_p1, _, _, _, _ = _dispatch_organization(
                "C0P1", free, pending, session.services, snap.time,
                session.individual_services, EDGE_COST, SCREEN_COST,
            )
            joint_p1, edges, screened, resource, latency = _dispatch_organization(
                "C2P1", free, pending, session.services, snap.time,
                session.individual_services, EDGE_COST, SCREEN_COST,
            )
            d1 = [(analysts_by_id[aid], pending[alert_id]) for aid, alert_id in snap.d1_pairs]
            vals = {
                "D1-S": _candidate_metrics(d1, snap.time, 0.0, session.services,
                                           session.individual_services, pending),
                "C0P1": _candidate_metrics(local_p1, snap.time, 0.0, session.services,
                                           session.individual_services, pending),
                "C2P1": _candidate_metrics(joint_p1, snap.time, latency, session.services,
                                           session.individual_services, pending),
            }
            # A class is compared only across eligible, currently available analysts.
            competence_spread = max((max(a.competence[x.task_class] for a in aa)
                                     - min(a.competence[x.task_class] for a in aa)
                                     for x in pending.values()
                                     if len(aa := [a for a in free if x.task_class in a.eligible_classes]) > 1),
                                    default=0.0)
            speed_spread = max((max(session.individual_services.get(a.analyst_id, {}).get(x.task_class, session.services[x.task_class]) for a in aa)
                                - min(session.individual_services.get(a.analyst_id, {}).get(x.task_class, session.services[x.task_class]) for a in aa)
                                for x in pending.values()
                                if len(aa := [a for a in free if x.task_class in a.eligible_classes]) > 1),
                               default=0.0)
            records.append({
                "stage": session_name, "time": snap.time,
                "free_n": len(free), "queue_n": len(pending),
                "edges": len(eligible_edges), "heterogeneous": heterogeneous,
                "competence_spread": competence_spread, "speed_spread": speed_spread,
                "resource": resource, "latency": latency, "cost_edges": edges,
                "screened": screened, "policies": vals,
                "assignment_summary": {
                    "D1-S": _assignment_summary(d1, free, snap.time, session.services, session.individual_services, pending),
                    "C0P1": _assignment_summary(local_p1, free, snap.time, session.services, session.individual_services, pending),
                    "C2P1": _assignment_summary(joint_p1, free, snap.time + latency, session.services, session.individual_services, pending),
                },
            })
    return records


def _ci(xs):
    mean = statistics.mean(xs)
    half = T95_DF7 * statistics.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else 0.0
    return mean, mean-half, mean+half


def _fmt(xs, digits=3):
    mean, low, high = _ci(xs)
    return f"{mean:+.{digits}f} [{low:+.{digits}f}, {high:+.{digits}f}]"


def main():
    scenarios = tuple(_make_scenario(n) for n in SCENARIO_NAMES)
    point_records = {}
    episodes = {}
    for scenario in scenarios:
        for seed in SEEDS:
            point_records[(scenario.name, seed)] = _same_state_opportunities(scenario, seed)
            for policy in POLICIES:
                episodes[(scenario.name, seed, policy)], _ = _run_episode(scenario, seed, policy)
            sigs = {episodes[(scenario.name, seed, p)]["signature"] for p in POLICIES}
            assert len(sigs) == 1
            assert len({episodes[(scenario.name, seed, p)]["admitted"] for p in POLICIES}) == 1

    point_rows = [(name, seed, row) for (name, seed), records in point_records.items() for row in records]
    qualifies = [r for _, _, r in point_rows]
    n_eligible = len(qualifies)
    n_heterogeneous = sum(r["heterogeneous"] for r in qualifies)

    lines = [
        "# Oportunidad incremental de coordinación entre analistas", "",
        "## Diseño y causalidad", "",
        "Se comparan en estados idénticos tres propuestas de despacho: la asignación efectiva D1-S; C0P1, elección local secuencial equilibrada; y C2P1, matching uno-a-uno de competencia/SLA/velocidad. Los snapshots proceden de rollouts D1-S y contienen solo alertas ya presentes en la cola, analistas libres, perfiles, elegibilidad, tiempos de servicio, deadlines y tiempo actual. No se accede a llegadas futuras para proponer ni puntuar asignaciones. Los estados se consideran oportunidad estructural si hay al menos dos analistas libres, dos alertas pendientes y dos aristas elegibles.", "",
        "C0P1−D1-S describe el efecto de cambiar la regla individual/local, incluyendo la normalización de velocidad de C0P1 que usa los tiempos factibles actuales del conjunto disponible. C2P1−C0P1 contrasta matching conjunto con la asignación local secuencial bajo el mismo objetivo P1. Ninguna diferencia instantánea se interpreta como resultado de episodio. Para estimar efectos de episodio se hicieron rollouts completos separados D1-S, C0P1 y C2P1 con semillas emparejadas y las mismas trazas exógenas; los rollouts usan acciones fijas y no reciben verdad simulada para decidir.", "",
        f"Escenarios: seis regímenes sintéticos; ocho semillas nuevas ({SEEDS[0]}–{SEEDS[-1]}) por régimen. Total: {len(scenarios)*len(SEEDS)*len(POLICIES)} episodios completos. IC95% t pareado, df=7, t=2.365. C2P1 coste configurado: EDGE_COST={EDGE_COST}, SCREEN_COST={SCREEN_COST}; coste de recursos por decisión = EDGE_COST×aristas inspeccionadas + SCREEN_COST×alertas cribadas; latencia del coordinador = coste de recursos / analistas libres. No se atribuye este coste a C0P1 ni D1-S. Pesos de recompensa sin cambios: `{REWARD_WEIGHTS}`.", "",
        "## Frecuencia y magnitud de oportunidades por estado", "",
        f"Se observaron {n_eligible} estados elegibles en rollouts D1-S, de los cuales {n_heterogeneous} ({n_heterogeneous/max(1,n_eligible):.1%}) tenían diferencias de competencia o velocidad entre analistas elegibles para una clase pendiente. Las filas resumen la media por estado dentro de cada escenario; son diagnósticos descriptivos y estados repetidos dentro de episodios no son independientes.", "",
        "| Escenario | Estados elegibles | Estados heterogéneos | % propuestas diferentes D1-S/C0P1 | % matching C2P1 distinto a C0P1 | Δ competencia C0P1−D1-S | Δ SLA previsto C0P1−D1-S | Δ competencia C2P1−C0P1 | Δ SLA previsto C2P1−C0P1 | Δ servicio C0P1−D1-S | Δ servicio C2P1−C0P1 | Alertas seleccionadas distintas C2P1 vs C0P1 | Alertas comunes asignadas a otro analista | Latencia C2P1 media | Recurso coordinador medio |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario in scenarios:
        rs = [r for (name, _, r) in point_rows if name == scenario.name]
        n = len(rs)
        def avg(values):
            items = list(values)
            return statistics.mean(items) if items else 0.0
        d1_c0 = [r["policies"]["C0P1"] for r in rs]
        c2 = [r["policies"]["C2P1"] for r in rs]
        d1 = [r["policies"]["D1-S"] for r in rs]
        p_d1_c0 = sum(x["pairs"] != y["pairs"] for x, y in zip(d1, d1_c0)) / max(1,n)
        p_c0_c2 = sum(x["pairs"] != y["pairs"] for x, y in zip(d1_c0, c2)) / max(1,n)
        selection_changes = avg(len(x["alerts"] ^ y["alerts"]) for x,y in zip(d1_c0,c2))
        analyst_reassignments = avg(sum(
            {alert_id: analyst_id for analyst_id, alert_id in x["pairs"]}[alert_id]
            != {alert_id: analyst_id for analyst_id, alert_id in y["pairs"]}[alert_id]
            for alert_id in (x["alerts"] & y["alerts"])
        ) for x,y in zip(d1_c0,c2))
        lines.append(f"| {scenario.name} | {n} | {sum(r['heterogeneous'] for r in rs)} | {p_d1_c0:.1%} | {p_c0_c2:.1%} | {avg(x['competence']-y['competence'] for x,y in zip(d1_c0,d1)):+.3f} | {avg(x['ontime']-y['ontime'] for x,y in zip(d1_c0,d1)):+.3f} | {avg(x['competence']-y['competence'] for x,y in zip(c2,d1_c0)):+.3f} | {avg(x['ontime']-y['ontime'] for x,y in zip(c2,d1_c0)):+.3f} | {avg(x['service']-y['service'] for x,y in zip(d1_c0,d1)):+.4f} | {avg(x['service']-y['service'] for x,y in zip(c2,d1_c0)):+.4f} | {selection_changes:.2f} | {analyst_reassignments:.2f} | {avg(r['latency'] for r in rs):.6f} | {avg(r['resource'] for r in rs):.6f} |")

    lines += ["", "## Contrafactuales de episodio completos", "",
              "Diferencias pareadas de recompensa, SLA terminal corregido, calidad realizada, calidad modelada, espera y backlog máximo. Son efectos de políticas fijas en estas condiciones simuladas, no efectos causales de cambiar organización dentro de una misma trayectoria.", "",
              "| Escenario | Contraste | Δ recompensa [IC95%] | Δ SLA [IC95%] | Δ calidad realizada [IC95%] | Δ calidad modelada [IC95%] | Δ espera [IC95%] | Δ backlog máximo [IC95%] | Δ coste recurso | Δ latencia |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for scenario in scenarios:
        for left, right in (("C0P1", "D1-S"), ("C2P1", "C0P1"), ("C2P1", "D1-S")):
            a = [episodes[(scenario.name, seed, left)] for seed in SEEDS]
            b = [episodes[(scenario.name, seed, right)] for seed in SEEDS]
            keys = ("reward", "sla", "quality", "quality_modelled", "mean_wait", "max_backlog")
            diffs = {k: [x[k] - y[k] for x,y in zip(a,b)] for k in keys}
            lines.append(f"| {scenario.name} | {left}−{right} | {_fmt(diffs['reward'],2)} | {_fmt(diffs['sla'])} | {_fmt(diffs['quality'])} | {_fmt(diffs['quality_modelled'])} | {_fmt(diffs['mean_wait'],4)} | {_fmt(diffs['max_backlog'],2)} | {statistics.mean(x['coordination_resource']-y['coordination_resource'] for x,y in zip(a,b)):.6f} | {statistics.mean(x['coordination_latency']-y['coordination_latency'] for x,y in zip(a,b)):.6f} |")

    lines += ["", "### C2P1: frecuencia de coordinación sin matching entre varios analistas", "",
              "| Escenario | Decisiones de coordinación/episodio | Con un analista libre | Fracción con un analista libre |",
              "|---|---:|---:|---:|"]
    for scenario in scenarios:
        g = [episodes[(scenario.name, seed, "C2P1")] for seed in SEEDS]
        total = sum(x["coordination_decisions"] for x in g)
        solo = sum(x["solo_coordination_decisions"] for x in g)
        n_ep = len(g)
        lines.append(f"| {scenario.name} | {total/n_ep:.1f} | {solo/n_ep:.1f} | {solo/total if total else 0:.1%} |")

    lines += ["", "## Ejemplos de asignación anonimizados", "",
              "Se muestra el primer estado elegible de cada escenario donde al menos dos propuestas difieren. Los analistas se renombran A1/A2 y las alertas se representan por clase y holgura estimada; no se incluyen IDs. Los ejemplos no se seleccionan por magnitud favorable.", "",
              "| Escenario | D1-S local | C0P1 local equilibrada | C2P1 matching global |",
              "|---|---|---|---|"]
    for scenario in scenarios:
        sample = None
        for seed in SEEDS:
            sample = next((r for r in point_records[(scenario.name, seed)]
                           if r["policies"]["D1-S"]["pairs"] != r["policies"]["C0P1"]["pairs"]
                           or r["policies"]["C0P1"]["pairs"] != r["policies"]["C2P1"]["pairs"]), None)
            if sample:
                break
        if sample:
            q = sample["assignment_summary"]
            lines.append(f"| {scenario.name} | {q['D1-S']} | {q['C0P1']} | {q['C2P1']} |")
        else:
            lines.append(f"| {scenario.name} | sin divergencia observada | sin divergencia observada | sin divergencia observada |")
    lines += ["", "En estos estados emparejados D1-S y C0P1 no difirieron. La única diferencia observada fue C2P1 seleccionando otra alerta de la misma clase; no reasignó una alerta común a otro analista. Las medidas instantáneas de competencia y SLA previstos fueron cero en promedio, y no equivalen a recompensa de episodio.", "",
              "## Qué mecanismo puede explicar una diferencia", "",
              "1. **Heurística individual/local (D1-S→C0P1):** C0P1 compara competencia propia, cumplimiento individual previsto y velocidad en una escala interna fija; D1-S prioriza riesgo temporal y competencia con sus reglas congeladas. Si difieren, la mejora no requiere matching central, aunque C0P1 usa una normalización del servicio basada en el conjunto de aristas factibles observable en ese instante.",
              "2. **Información/intercambio:** exponer perfiles y tiempos de los analistas elegibles puede ayudar a estimar quién es complementario para qué clase. Las métricas de dispersión solo muestran que existen perfiles distintos; no prueban por sí mismas que compartir esa información mejore el sistema.",
              "3. **Asignación conjunta (C0P1→C2P1):** la diferencia de asignación se atribuye al matching uno-a-uno frente a selección local secuencial, dado el mismo conjunto de alertas y perfiles. C2P1 paga el cribado de alertas y revisión de aristas; sus coste y latencia se miden explícitamente. El matching usa solo el estado actual y no planifica llegadas futuras.",
              "",
              "## Limitaciones y decisión", "",
              "Las mejoras de una decisión son predicciones del modelo (competencia y SLA con duración estimada). No incluyen la calidad realizada aleatoria ni el efecto de ocupación posterior. En los episodios completos la divergencia de una primera asignación cambia estados posteriores, aunque las llegadas y etiquetas simuladas son emparejadas por semilla. El coste de coordinación es hipotético y depende de EDGE_COST/SCREEN_COST; sensibilidad a esos valores requeriría un estudio separado. La referencia de velocidad compartida por C0P1 representa disponibilidad de información global en la normalización, no un protocolo humano observado.", "",
              "**Decisión: STOP para afirmar o desarrollar ya un controlador de coordinación con este modelo y estos escenarios.** En 214 estados que cumplen disponibilidad, cola y elegibilidad, ninguno muestra dispersión de competencia o velocidad entre analistas simultáneamente elegibles; D1-S y C0P1 coinciden en todas esas propuestas y C2P1 difiere en solo 0.9% de los estados. La única diferencia observada selecciona otra alerta de la misma clase; no demuestra reasignación cruzada a analistas complementarios. Los rollouts completos de C2P1 pierden recompensa y SLA frente a C0P1 en cinco de seis escenarios. Además, 71–82% de sus decisiones se toman con un solo analista libre, donde no hay matching entre analistas, aunque sí se paga el coste configurado. Esto revela falta de oportunidades y desajuste de coste en el entorno actual, no una refutación universal del valor de coordinación. No se implementó controlador alguno.", "",
              "Reproducir: `python studies/soc_human_ai_organization/analyze_coordination_opportunities.py`."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT}; opportunity states={n_eligible}; episode runs={len(scenarios)*len(SEEDS)*len(POLICIES)}")


if __name__ == "__main__":
    main()
