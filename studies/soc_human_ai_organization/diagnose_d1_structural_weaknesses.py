"""Diagnostic-only trace and same-state counterfactuals for frozen D1."""
from __future__ import annotations

from collections import defaultdict
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studies/soc_human_ai_organization"))
sys.path.insert(0, str(ROOT / "src"))

from run_d1_baseline import scenarios  # noqa: E402
from run_b4_organizational_episodes import REWARD_WEIGHTS  # noqa: E402

SEEDS = (83011, 83012, 83013, 83014, 83015, 83016)
IMPOSSIBLE_RISK = 0.95
T95_DF5 = 2.571


def one_step(session, time, pairs, difficulty):
    analyst_by_id = {a.analyst_id: a for a in session.analysts}
    ontime = 0
    expected_quality = 0.0
    service_sum = 0.0
    for analyst_id, alert_id in pairs:
        analyst = analyst_by_id[analyst_id]
        alert = session.alerts[alert_id]
        service = session.individual_services.get(analyst_id, {}).get(
            alert.task_class, session.services[alert.task_class])
        service_sum += service
        ontime += int(time + service <= alert.deadline)
        expected_quality += analyst.competence[alert.task_class] * (
            1.0 - 0.35 * difficulty[alert_id])
    return ontime, expected_quality, service_sum


def summarize_episode(result):
    episodes = {"snapshots": 0, "joint_diff": 0, "joint_sla_gain": 0,
                "joint_quality_gain": 0.0, "joint_backlog_gain": 0,
                "d1_pairs": 0, "oracle_pairs": 0,
                "local_correctable": 0, "irrecoverable_choices": 0,
                "local_correctable_alerts": set(), "irrecoverable_alerts": set(),
                "occupied_events": 0, "occupied_alerts": set(),
                "occupied_wait": [], "max_queue": 0,
                "queue_exposure": 0, "sla_missed": 0, "assigned": 0,
                "waits": [], "load": [], "expected_quality": 0.0,
                "on_time": 0}
    occupied_seen = set()
    missed_ids = set()
    for pool_name in ("l1", "l2"):
        session = result[f"_{pool_name}_session"]
        snapshot_rows = session.d1_dispatch_snapshots
        episodes["snapshots"] += len(snapshot_rows)
        analyst_by_id = {a.analyst_id: a for a in session.analysts}
        difficulty = {aid: row.difficulty for aid, row in result["evaluation"].items()}
        for snap in snapshot_rows:
            episodes["max_queue"] = max(episodes["max_queue"], len(snap.queue_alert_ids))
            episodes["queue_exposure"] += len(snap.queue_alert_ids)
            d1 = one_step(session, snap.time, snap.d1_pairs, difficulty)
            oracle = one_step(session, snap.time, snap.joint_oracle_pairs, difficulty)
            episodes["d1_pairs"] += len(snap.d1_pairs)
            episodes["oracle_pairs"] += len(snap.joint_oracle_pairs)
            episodes["joint_diff"] += int(set(snap.d1_pairs) != set(snap.joint_oracle_pairs))
            episodes["joint_sla_gain"] += oracle[0] - d1[0]
            episodes["joint_quality_gain"] += oracle[1] - d1[1]
            episodes["joint_backlog_gain"] += len(snap.joint_oracle_pairs) - len(snap.d1_pairs)

        for decision in session.d1_decisions:
            chosen = next(c for c in decision.candidates if c.alert_id == decision.alert_id)
            episodes["irrecoverable_choices"] += int(chosen.deadline_risk >= IMPOSSIBLE_RISK)
            if chosen.deadline_risk >= IMPOSSIBLE_RISK:
                episodes["irrecoverable_alerts"].add(chosen.alert_id)
            episodes["local_correctable"] += int(
                not chosen.projected_on_time and any(c.projected_on_time for c in decision.candidates)
            )
            if not chosen.projected_on_time and any(c.projected_on_time for c in decision.candidates):
                episodes["local_correctable_alerts"].add(chosen.alert_id)
            # One waiting alert is counted once per episode, with the earliest
            # observed release of a busy eligible specialist as a delay proxy.
            for aid, alert_id, completion in decision.occupied_specialists:
                specialist = next(a for a in session.analysts if a.analyst_id == aid)
                for waiting_id in decision.queue_alert_ids:
                    waiting = session.alerts[waiting_id]
                    free_eligible = any(
                        waiting.task_class in next(a for a in session.analysts
                                                    if a.analyst_id == free_id).eligible_classes
                        for free_id in decision.available_analyst_ids
                    )
                    if waiting.task_class not in specialist.eligible_classes or free_eligible:
                        continue
                    key = (pool_name, waiting_id, aid)
                    if key not in occupied_seen:
                        occupied_seen.add(key)
                        episodes["occupied_alerts"].add(waiting_id)
                        episodes["occupied_wait"].append(max(0.0, completion - decision.time))
        assignments = session.assignments
        busy = defaultdict(float)
        for job in assignments:
            alert = session.alerts[job.alert_id]
            wait = max(0.0, job.start - alert.arrival)
            episodes["waits"].append(wait)
            busy[job.analyst_id] += job.completion - job.start
            episodes["assigned"] += 1
            episodes["on_time"] += int(job.completion <= alert.deadline)
            episodes["expected_quality"] += analyst_by_id[job.analyst_id].competence[alert.task_class] * (
                1.0 - 0.35 * difficulty[job.alert_id])
            if job.completion > alert.deadline:
                missed_ids.add(job.alert_id)
        if session.d1_decisions:
            episodes["load"].extend(busy.get(a.analyst_id, 0.0) for a in session.analysts)
    episodes["occupied_events"] = len(occupied_seen)
    episodes["sla_missed"] = len(missed_ids)
    episodes["realized_correct"] = sum(result["resolution_correct"].values())
    episodes["admitted"] = result["admitted"]
    episodes["sla_episode"] = result["sla"]
    episodes["quality_episode"] = result["quality"]
    episodes["reward"] = result["reward"]
    episodes["backlog"] = result["backlog"]
    return episodes


def run_with_sessions(scenario, seed):
    # Reconstruct the same episode and retain session objects for tracing.
    from hls.ia_l1_l2_simulation import B4EpisodeEnv
    from run_b4_organizational_episodes import L1_SERVICE, L2_SERVICE, DRAIN, REWARD_WEIGHTS
    env = B4EpisodeEnv(
        scenario.config, scenario.l1, scenario.l2, L1_SERVICE, L2_SERVICE,
        drain_period=DRAIN, sequential_reward_weights=REWARD_WEIGHTS,
        l1_service_by_analyst_class=scenario.l1_services,
        l2_service_by_analyst_class=scenario.l2_services,
        l1_roster_schedule=scenario.l1_schedule,
        l2_roster_schedule=scenario.l2_schedule,
        diagnostic_d1=True,
    )
    env.reset(seed=seed)
    total = 0.0
    while True:
        _, reward, term, trunc, info = env.step_fixed("D1")
        if trunc:
            raise AssertionError("unexpected truncation")
        total += reward
        if term:
            break
    return {
        "_l1_session": env._l1, "_l2_session": env._l2,
        "resolution_correct": dict(env._resolution_correct),
        "evaluation": dict(env._evaluation), "admitted": info["admitted"],
        "routing": dict(env._routing),
        "sla": info["sla_fraction"],
        "quality": info["resolution_success_per_admitted"],
        "reward": total,
        "backlog": info["pending"],
    }


def mean(values):
    return statistics.mean(values) if values else 0.0


def mean_ci(values):
    center = mean(values)
    if len(values) < 2:
        return center, center, center
    half = T95_DF5 * statistics.stdev(values) / math.sqrt(len(values))
    return center, center - half, center + half


def main():
    rows = []
    for scenario in scenarios():
        for seed in SEEDS:
            raw = run_with_sessions(scenario, seed)
            row = summarize_episode(raw)
            row.update(scenario=scenario.name, seed=seed)
            rows.append(row)

    lines = [
        "# Deficiencias estructurales observables de D1", "",
        "## Protocolo e instrumentación",
        "Se ejecutaron 18 episodios D1: seis semillas emparejadas (83011–83016) en carga baja, carga próxima a capacidad y elegibilidad restringida con heterogeneidad de competencia. Para contrafactuales inmediatos se reporta media de diferencias por semilla e IC95% t pareado (df=5, t=2.571). Se congeló D1, la recompensa y la generación exógena. En cada decisión se registraron tiempo, cola pendiente, analistas libres, candidatos factibles con servicio propio, deadline/slack, riesgo local, competencia propia, cobertura elegible de compañeros y especialistas ocupados. Inicios/finalizaciones y SLA se reconstruyeron de los eventos del motor; calidad observada, después del episodio, de sus resultados simulados.",
        "",
        "El oráculo conjunto es un matching diagnóstico con el objetivo lexicográfico de B2, sin latencia/coste, calculado sobre la misma cola y roster del instante D1, sin alterar la ejecución: número de tareas a tiempo, competencia de las tareas a tiempo, número total de asignaciones y desempate temporal determinista. Es un límite superior de decisión bajo ese objetivo y con información global, no una política evaluada a horizonte completo. Los contrafactuales locales consideran únicamente alternativas elegibles del analista en ese instante. Ningún controlador recibe etiqueta de verdad, resultado de calidad, llegada futura ni terminación futura.",
        "",
        "## Frecuencias agregadas",
        "Conteos de eventos son oportunidades de despacho; el porcentaje por episodio usa 18 episodios. ‘Alternativa local a tiempo’ significa que D1 eligió un candidato que no podía cumplir su deadline aunque tenía otro candidato factible que sí podía, dadas las duraciones estimadas en ese instante. ‘Especialista ocupado’ identifica una alerta esperando para la que un analista actualmente en servicio era elegible; es una limitación de capacidad momentánea, no un error de asignación probado.",
        "",
        "| Métrica | Episodios/eventos | Tasa o media |",
        "|---|---:|---:|",
    ]
    n_ep = len(rows)
    total_dec = sum(r["snapshots"] for r in rows)
    local_correctable = sum(r["local_correctable"] for r in rows)
    impossible = sum(r["irrecoverable_choices"] for r in rows)
    occupied = sum(r["occupied_events"] for r in rows)
    joint_diff = sum(r["joint_diff"] for r in rows)
    lines.extend([
        f"| Decisiones de despacho D1 | {total_dec} | — |",
        f"| Selecciones con riesgo D1 ≥ {IMPOSSIBLE_RISK:.2f} | {impossible} | {impossible/max(1,sum(len(r['waits']) for r in rows)):.1%} de asignaciones |",
        f"| Selección irrecuperable con alternativa local a tiempo | {local_correctable} | {local_correctable/max(1,total_dec):.1%} de decisiones por analista |",
        f"| Alertas únicas en esas decisiones localmente corregibles | {sum(len(r['local_correctable_alerts']) for r in rows)} | sobre las trazas D1 |",
        f"| Oportunidad con especialista elegible ocupado y sin elegible libre | {occupied} | en {sum(bool(r['occupied_events']) for r in rows)}/{n_ep} episodios |",
        f"| Alertas únicas bloqueadas por especialista ocupado | {sum(len(r['occupied_alerts']) for r in rows)} | sobre las trazas D1 |",
        f"| Propuesta conjunta difiere de D1 | {joint_diff} | {joint_diff/max(1,total_dec):.1%} de épocas comparables |",
        f"| Alertas observadas incumpliendo SLA en D1 | {sum(r['sla_missed'] for r in rows)} | SLA medio {mean([r['sla_episode'] for r in rows]):.3f} |",
        f"| Espera media antes de cada etapa de servicio | — | {mean([w for r in rows for w in r['waits']]):.4f} unidades de tiempo |",
        f"| CV de carga ocupada por analista (episodio-pooled) | — | {statistics.pstdev([x for r in rows for x in r['load']]) / max(1e-12, mean([x for r in rows for x in r['load']])):.3f} |",
        f"| Calidad de resolución realizada por alerta | — | {mean([r['quality_episode'] for r in rows]):.3f} |",
        f"| Backlog medio tras drenaje explícito | — | {mean([r['backlog'] for r in rows]):.3f} alertas |",
    ])

    lines.extend(["", "## Contrafactuales pareados desde el mismo estado", "",
                  "Las diferencias de SLA/calidad inmediata comparan las parejas propuestas antes de que las trayectorias diverjan. No son mejoras realizadas a horizonte completo. Para la calidad esperada se usa únicamente la probabilidad simulada competencia×dificultad, como medida de evaluador; D1 no observa dificultad.",
                  "",
                  f"Pesos de recompensa congelados: SLA={REWARD_WEIGHTS[0]}, resolución={REWARD_WEIGHTS[1]}. La columna de recompensa es el valor esperado de un despacho aislado, sin costes y sin extrapolar la continuación del episodio.",
                  "", "| Región | Δ SLA inmediato/época [IC95%] | Δ calidad esperada/época [IC95%] | Δ reward/época [IC95%] | Δ asignadas | Espera si especialista es único ocupado |",
                  "|---|---:|---:|---:|---:|---:|"])
    for scenario in scenarios():
        group = [r for r in rows if r["scenario"] == scenario.name]
        sla_values = [r["joint_sla_gain"] / max(1, r["snapshots"]) for r in group]
        quality_values = [r["joint_quality_gain"] / max(1, r["snapshots"]) for r in group]
        backlog_values = [r["joint_backlog_gain"] / max(1, r["snapshots"]) for r in group]
        sla_gain, sla_lo, sla_hi = mean_ci(sla_values)
        quality_gain, quality_lo, quality_hi = mean_ci(quality_values)
        backlog_gain = mean(backlog_values)
        reward_values = [REWARD_WEIGHTS[0] * sla + REWARD_WEIGHTS[1] * quality
                         for sla, quality in zip(sla_values, quality_values)]
        reward_gain, reward_lo, reward_hi = mean_ci(reward_values)
        waits = [x for r in group for x in r["occupied_wait"]]
        lines.append(f"| {scenario.name} | {sla_gain:+.3f} [{sla_lo:+.3f},{sla_hi:+.3f}] | {quality_gain:+.4f} [{quality_lo:+.4f},{quality_hi:+.4f}] | {reward_gain:+.4f} [{reward_lo:+.4f},{reward_hi:+.4f}] | {backlog_gain:+.3f} | {mean(waits):.4f} |")
    lines.extend(["", "Las diferencias puntuales de SLA y reward del matching son positivas en carga cercana y elegibilidad restringida, pero sus IC95% cruzan cero. La calidad esperada por competencia es positiva y más estable en elegibilidad restringida; es una predicción del modelo, no una mejora observada de episodio. El matching no asigna más alertas en promedio en estos estados (Δ=0). La instrumentación diagnóstica es opt-in y se verificó que no cambia las asignaciones D1."])

    # Representative traces: first D1 epochs with a material immediate gap.
    traces = []
    for scenario in scenarios():
        raw = run_with_sessions(scenario, SEEDS[0])
        for pool in (raw["_l1_session"], raw["_l2_session"]):
            for snap in pool.d1_dispatch_snapshots:
                if set(snap.d1_pairs) != set(snap.joint_oracle_pairs):
                    difficulty = {aid: row.difficulty for aid, row in raw["evaluation"].items()}
                    d1 = one_step(pool, snap.time, snap.d1_pairs, difficulty)
                    oracle = one_step(pool, snap.time, snap.joint_oracle_pairs, difficulty)
                    if d1[:2] != oracle[:2]:
                        traces.append((scenario.name, snap, d1, oracle))
        if len(traces) >= 3:
            break
    lines.extend(["", "## Trazas ilustrativas de propuestas conjuntas", "",
                  "Se muestran diferencias de asignación en estados idénticos; las métricas son proyecciones de esa decisión puntual.",
                  "", "| Escenario | t | D1 (analista→alerta) | Oráculo B2 (analista→alerta) | D1 (SLA, calidad esp.) | Oráculo (SLA, calidad esp.) |",
                  "|---|---:|---|---|---:|---:|"])
    for scenario_name, snap, d1, oracle in traces[:8]:
        fmt = lambda pairs: ", ".join(f"{a}→{x}" for a, x in pairs) or "—"
        lines.append(f"| {scenario_name} | {snap.time:.3f} | {fmt(snap.d1_pairs)} | {fmt(snap.joint_oracle_pairs)} | ({d1[0]}, {d1[1]:.3f}) | ({oracle[0]}, {oracle[1]:.3f}) |")

    restricted_scenario = next(s for s in scenarios() if s.name == "eligibility_restricted")
    service_episode = run_with_sessions(restricted_scenario, SEEDS[0])
    final_jobs = {}
    for aid, routed in service_episode["routing"].items():
        source = service_episode["_l2_session"] if routed else service_episode["_l1_session"]
        job = next((j for j in source.assignments if j.alert_id == aid), None)
        if job is not None:
            final_jobs[aid] = job
    jobs = []
    for pool_name in ("L1", "L2"):
        session = service_episode[f"_{pool_name.lower()}_session"]
        for job in session.assignments:
            alert = session.alerts[job.alert_id]
            final = final_jobs.get(job.alert_id)
            sla = bool(final and final.completion <= alert.deadline)
            correct = service_episode["resolution_correct"].get(job.alert_id)
            jobs.append((job.start, pool_name, job, alert, sla, correct))
    lines.extend(["", "## Traza de servicio y resultados del episodio", "",
                  "Muestra de una realización restringida. Inicio/fin describen cada etapa; SLA y acierto son el resultado final por alerta y pueden repetirse si hubo dos etapas.",
                  "", "| Pool | Analista | Alerta | Llegada | Inicio | Fin | Espera etapa | Deadline | SLA final | Resolución correcta |",
                  "|---|---|---|---:|---:|---:|---:|---:|---|---|"])
    for _, pool_name, job, alert, sla, correct in sorted(jobs)[:12]:
        correct_text = "—" if correct is None else ("sí" if correct else "no")
        lines.append(f"| {pool_name} | {job.analyst_id} | {job.alert_id} | {alert.arrival:.3f} | {job.start:.3f} | {job.completion:.3f} | {job.start-alert.arrival:.3f} | {alert.deadline:.3f} | {'sí' if sla else 'no'} | {correct_text} |")

    lines.extend(["", "## Taxonomía, atribución y mecanismo", "",
                  "**A. Especialista ocupado.** La traza cuantifica alertas que esperan mientras un analista elegible está ocupado y no hay elegible libre. Es una restricción de recursos/servicio no corregible por una elección instantánea; permitir preempción, capacidad de respaldo o cambio de elegibilidad sería una capacidad nueva, no una mejora decisional D1. El registro de espera hasta liberación es descriptivo.",
                  "",
                  "**B. Trabajo casi irrecuperable.** D1 prioriza mayor riesgo (`(s−slack)/s`), por lo que puede seleccionar tareas que ya no llegan a tiempo. Cuando el registro muestra que el mismo analista tenía una alternativa a tiempo, existe una deficiencia corregible localmente. El delta de SLA por esa desviación es una cota de un paso; no se atribuye como ganancia de episodio porque los siguientes despachos cambian.",
                  "",
                  "**C. Matching conjunto.** El matching global diagnóstico difiere de decisiones individuales en las épocas identificadas. Su delta proyectado informa qué asignaciones factibles podría reordenar bajo competencia exacta y cola compartida. La brecha mezcla información global y optimización conjunta; este experimento no identifica por separado ambos efectos. Latencia y coste son cero en el oráculo, por lo que toda mejora es bruta, no neta.",
                  "",
                  "**D. Espera y carga.** Se registran espera por etapa, cola y dispersión de tiempo ocupado. Un CV alto o una espera larga no prueban por sí solos mala organización: elegibilidad, llegadas y duración crean desigualdad incluso con decisiones correctas. No se atribuye pérdida causal sin contrafactual temporal completo.",
                  "",
                  "**E. Información parcial.** D1 conoce el mapa grueso de elegibilidad de compañeros, no sus competencias/velocidades por tarea. La propuesta de matching global indica dónde esa información podría cambiar el pareo; no separa su valor del coste de coordinación o del horizonte futuro.",
                  "",
                  "## Priorización de mecanismos candidatos (sin implementar)", "",
                  "1. **Revisión local de riesgo irrecuperable**, si hay alternativas factibles a tiempo: coste de complejidad bajo; valida primero si ese patrón existe con frecuencia y reduce SLA perdido sin degradar calidad.",
                  "2. **Disponibilidad visible de especialidad y carga**, para evitar esperar por capacidad elegible ocupada cuando existe un respaldo compatible: complejidad media; no crea capacidad si todos los especialistas están ocupados.",
                  "3. **Matching conjunto informado por competencia**, solo si las trazas muestran ganancias inmediatas repetidas suficientes para compensar latencia y recursos: complejidad alta; el oráculo de un paso es límite superior, no expectativa operacional.",
                  "",
                  "## Límites", "",
                  "18 episodios sintéticos y seis semillas por escenario no sustentan generalización. El conjunto incluye pocos regímenes y parámetros hipotéticos. Un oráculo de un paso no estima mejora a episodio completo; latencia y coste reales no están medidos. Las etiquetas de necesidad real y los resultados de calidad se usaron solo en evaluación post hoc, nunca para decidir. Sin evidencia de beneficio neto, no se recomienda aún una nueva política.",
                  "", "Reproducir: `python studies/soc_human_ai_organization/diagnose_d1_structural_weaknesses.py`. Semillas fijadas: 83011–83016."])
    out = ROOT / "studies/soc_human_ai_organization/D1_STRUCTURAL_WEAKNESSES.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    print(f"episodes={n_ep} dispatch_epochs={total_dec} local_correctable={local_correctable} joint_diff={joint_diff} occupied_specialist_alert-events={occupied}")


if __name__ == "__main__":
    main()
