"""Audit the D1-L episode comparison after correcting terminal SLA reporting."""
from __future__ import annotations

import math
import statistics
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studies/soc_human_ai_organization"))
sys.path.insert(0, str(ROOT / "src"))

from run_d1_local_correction import (  # noqa: E402
    scenario_suite, EVAL_SEEDS, POLICIES, ci95, fmt_ci, final_outcomes,
)
from run_b4_organizational_episodes import (  # noqa: E402
    L1_SERVICE, L2_SERVICE, DRAIN, REWARD_WEIGHTS,
)
from hls.ia_l1_l2_simulation import B4EpisodeEnv  # noqa: E402

REPORT = ROOT / "studies/soc_human_ai_organization/D1_ADAPTATION_FEASIBILITY.md"


def generate_signature(env):
    return tuple((row.routed.alert.alert_id, row.routed.alert.arrival,
                  row.routed.alert.task_class, row.routed.alert.deadline,
                  row.severity, row.difficulty, row.true_escalation_need,
                  row.routed.soctra_recommendation) for row in env._admitted)


def run_episode(scenario, seed, policy):
    env = B4EpisodeEnv(
        scenario.config, scenario.l1, scenario.l2, L1_SERVICE, L2_SERVICE,
        drain_period=DRAIN, sequential_reward_weights=REWARD_WEIGHTS,
        l1_service_by_analyst_class=scenario.l1_services,
        l2_service_by_analyst_class=scenario.l2_services,
        l1_roster_schedule=scenario.l1_schedule,
        l2_roster_schedule=scenario.l2_schedule,
        diagnostic_d1=policy in {"D1", "D1-L"},
    )
    env.reset(seed=seed)
    signature = generate_signature(env)
    reward = 0.0
    max_backlog = 0
    max_overdue = 0
    local_pressure = []
    trigger_conditions = 0
    while True:
        if policy == "C0P1":
            _, step_reward, terminated, truncated, info = env.step_fixed_organization(policy)
        else:
            _, step_reward, terminated, truncated, info = env.step_fixed(policy)
        if truncated:
            raise AssertionError("unexpected truncation")
        reward += step_reward
        for session in (env._l1, env._l2):
            max_backlog = max(max_backlog, len(session.pending))
            max_overdue = max(max_overdue, sum(a.deadline < session.now for a in session.pending.values()))
        if terminated:
            break

    final_jobs = final_outcomes(env)
    admitted = {row.routed.alert.alert_id: row for row in env._admitted}
    manual_ontime = sum(
        job.completion <= admitted[aid].routed.alert.deadline
        for aid, job in final_jobs.items()
    )
    # Reconstruct the old bug: first matching job in L1-then-L2 concatenation.
    all_jobs = (*env._l1.assignments, *env._l2.assignments)
    old_firststage_ontime = sum(
        next(job.completion for job in all_jobs if job.alert_id == aid)
        <= admitted[aid].routed.alert.deadline
        for aid in env._resolved
    )
    completed = len(env._resolved)
    correct = sum(env._resolution_correct.values())
    expected_correct = 0.0
    for aid, job in final_jobs.items():
        row = env._evaluation[aid]
        expected_correct += job.competence * (1.0 - 0.35 * row.difficulty)
    n = len(admitted)
    horizon = scenario.config.horizon
    drain_end = env._l1.drain_end
    final_completion = {aid: job.completion for aid, job in final_jobs.items()}
    ontime_h = sum(final_completion.get(aid, math.inf) <= min(row.routed.alert.deadline, horizon)
                   for aid, row in admitted.items())
    pending_h = sum(final_completion.get(aid, math.inf) > horizon for aid in admitted)
    overdue_open_h = sum(final_completion.get(aid, math.inf) > horizon
                         and row.routed.alert.deadline < horizon
                         for aid, row in admitted.items())
    overdue_open_hd = sum(final_completion.get(aid, math.inf) > drain_end
                          and row.routed.alert.deadline < drain_end
                          for aid, row in admitted.items())
    assert n == completed + info["pending"]
    assert info["completed_within_sla"] == manual_ontime
    assert info["sla_fraction"] == manual_ontime / n if n else 0.0
    assert info["completed"] == completed
    assert len(env._resolution_correct) == completed
    # The compared policies have no coordination charge; triage errors are
    # fixed by the identical trace. Therefore reward is final SLA count plus
    # realized correctness minus the fixed triage-error penalty.
    reconstructed_reward = (REWARD_WEIGHTS[0] * manual_ontime
                            + REWARD_WEIGHTS[1] * correct
                            - REWARD_WEIGHTS[3] * env._triage_errors)
    assert math.isclose(reward, reconstructed_reward, rel_tol=1e-10, abs_tol=1e-8)

    if policy in {"D1", "D1-L"}:
        for session in (env._l1, env._l2):
            for d in session.d1_decisions:
                baseline = next(c for c in d.candidates if c.alert_id == d.baseline_alert_id)
                viable = [c for c in d.candidates if c.projected_on_time]
                trigger_conditions += int(not baseline.projected_on_time and bool(viable))
                if d.candidates:
                    chosen = next(c for c in d.candidates if c.alert_id == d.alert_id)
                    local_pressure.append((
                        len(d.queue_alert_ids), len(d.available_analyst_ids),
                        sum(c.projected_on_time for c in d.candidates) / len(d.candidates),
                        min(c.remaining_slack for c in d.candidates),
                        max(c.deadline_risk for c in d.candidates),
                        int(not baseline.projected_on_time and bool(viable)),
                        chosen.own_competence - baseline.own_competence,
                        chosen.service_duration - baseline.service_duration,
                    ))
    else:
        local_pressure = []
    overdue_at_close = sum(
        admitted[aid].routed.alert.deadline < env._l1.drain_end
        for aid in env._l1.pending
    ) + sum(admitted[aid].routed.alert.deadline < env._l2.drain_end
            for aid in env._l2.pending)
    missed = set(env._resolved) - {
        aid for aid, job in final_jobs.items()
        if job.completion <= admitted[aid].routed.alert.deadline
    }
    return {
        "scenario": scenario.name, "seed": seed, "policy": policy,
        "signature": signature, "reward": reward, "n": n,
        "completed": completed, "pending": info["pending"],
        "sla_n": manual_ontime, "sla": manual_ontime/n if n else 0.0,
        "old_sla_n": old_firststage_ontime,
        "old_sla": old_firststage_ontime/n if n else 0.0,
        "sla_h": ontime_h/n if n else 0.0,
        "pending_h": pending_h,
        "overdue_open_h": overdue_open_h,
        "overdue_open_hd": overdue_open_hd,
        "realized_quality_n": correct,
        "realized_quality": correct/n if n else 0.0,
        "expected_quality_n": expected_correct,
        "expected_quality": expected_correct/n if n else 0.0,
        "triage_errors": env._triage_errors,
        "max_backlog": max_backlog, "max_overdue_pending": max_overdue,
        "overdue_pending_close": overdue_at_close,
        "waits": [max(0.0, j.start - session.alerts[j.alert_id].arrival)
                  for session in (env._l1, env._l2) for j in session.assignments],
        "review_count": info["d1l_review_count"],
        "trigger_conditions": trigger_conditions,
        "local_pressure": local_pressure,
        "missed_ids": missed,
        "correct_ids": set(env._resolution_correct),
    }


def main():
    rows = {}
    generated = {}
    for scenario in scenario_suite():
        for seed in EVAL_SEEDS:
            for policy in POLICIES:
                row = run_episode(scenario, seed, policy)
                rows[(scenario.name, seed, policy)] = row
                generated.setdefault((scenario.name, seed), row["signature"])
                assert generated[(scenario.name, seed)] == row["signature"]

    # Label propagation/reward invariant across policies must be exact.
    for scenario in scenario_suite():
        for seed in EVAL_SEEDS:
            trace_rows = [rows[(scenario.name, seed, policy)] for policy in POLICIES]
            assert len({r["n"] for r in trace_rows}) == 1
            assert len({r["triage_errors"] for r in trace_rows}) == 1
            assert len({r["n"] for r in trace_rows}) == 1

    lines = [
        "# Viabilidad de adaptación entre D1 y D1-L", "",
        "## Auditoría y corrección de métricas",
        "La auditoría detectó que el resumen terminal SLA tomaba la primera asignación por alerta en una concatenación L1→L2. Para alertas recomendadas y completadas en L2, contaba el fin L1 en vez del fin final L2. La recompensa ya se anotaba en la resolución final mediante `_record_resolution`, por lo que el error contaminaba la métrica SLA reportada, pero no reward ni asignaciones. Se corrigió únicamente el agregador terminal; los resultados del documento histórico D1_LOCAL_CORRECTION_RESULTS.md no se sobrescribieron.", "",
        "Las tasas usan admitted como denominador; unresolved cuentan como no completadas a tiempo y como pendientes al cierre. `completed + pending = admitted`. El drenaje es el valor configurado D, tanto L1 como L2 cierran en H+D. Una alerta escalada solo recibe crédito SLA por su fin L2; una no escalada por su fin L1. Las colas vencidas se conservan y se reportan, no se eliminan.", "",
        f"Se repitieron las cuatro políticas en las mismas 6×8 trazas de evaluación ({len(rows)} episodios). Para cada escenario/semilla, ID, llegada, clase, deadline, severidad, dificultad, referencia simulada y recomendación fueron idénticos entre políticas. Verificación de recompensa: `reward = w_SLA × finales_a_tiempo + w_Q × resoluciones_correctas − w_error × errores_triaje`; coordinación es cero en estas cuatro políticas. Todas las comprobaciones de conservación y denominadores se verificaron.", "",
        "El informe anterior queda como registro histórico de la métrica incorrecta; las cifras de SLA de este documento son las recalculadas. Reward se mantuvo sin cambios y se reconstruyó exactamente con la misma suma de eventos terminales.", "",
        "| Escenario | Política | SLA histórico (primera etapa, H+D) | SLA validado H | SLA validado H+D | Sobreestimación previa | Reward | Calidad realizada | Calidad esperada | Pendientes H | Pendientes H+D | Vencidas abiertas H / H+D |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario in scenario_suite():
        for policy in POLICIES:
            group = [rows[(scenario.name, seed, policy)] for seed in EVAL_SEEDS]
            m = lambda key: statistics.mean(r[key] for r in group)
            lines.append(f"| {scenario.name} | {policy} | {m('old_sla'):.3f} | {m('sla_h'):.3f} | {m('sla'):.3f} | {m('old_sla')-m('sla'):+.3f} | {m('reward'):.2f} | {m('realized_quality'):.3f} | {m('expected_quality'):.3f} | {m('pending_h'):.2f} | {m('pending'):.2f} | {m('overdue_open_h'):.2f} / {m('overdue_open_hd'):.2f} |")

    lines.extend(["", "## Diferencias emparejadas validadas", "",
                  "IC95% t pareado, df=7, t=2.365. La calidad esperada usa competencia×(1−0.35×dificultad), por alerta admitida; complementa la exactitud binaria realizada para separar valor de asignación de ruido Bernoulli.",
                  "", "| Escenario | Comparación | Δ SLA [IC95%] | Δ reward [IC95%] | Δ calidad realizada [IC95%] | Δ calidad esperada [IC95%] | Δ espera [IC95%] |",
                  "|---|---|---:|---:|---:|---:|---:|"])
    for scenario in scenario_suite():
        for policy_a, policy_b in (("D1-L", "D1"), ("D1-L", "B0"), ("D1-L", "C0P1"), ("C0P1", "D1-L")):
            group_a = [rows[(scenario.name, seed, policy_a)] for seed in EVAL_SEEDS]
            group_b = [rows[(scenario.name, seed, policy_b)] for seed in EVAL_SEEDS]
            diff = lambda key: [a[key] - b[key] for a, b in zip(group_a, group_b)]
            lines.append(f"| {scenario.name} | {policy_a}−{policy_b} | {fmt_ci(diff('sla'))} | {fmt_ci(diff('reward'),2)} | {fmt_ci(diff('realized_quality'))} | {fmt_ci(diff('expected_quality'))} | {fmt_ci([statistics.mean(a['waits'])-statistics.mean(b['waits']) for a,b in zip(group_a,group_b)],4)} |")

    lines.extend(["", "## Descomposición cuantitativa de las grandes mejoras", "",
                  "Reward se descompone en puntos absolutos, no en tasas. Para D1-L−D1, el término SLA equivale al cambio en finales a tiempo (puntos reward); el término de calidad realizada es el cambio en correctas. Ambos suman el cambio total porque errores IA y costes son invariantes entre las políticas emparejadas.",
                  "", "| Escenario | Δ finales a tiempo | Δ correctas realizadas | Δ reward total | Recuperadas / regresiones SLA por alert ID | Activaciones revisión | Condiciones locales detectadas |",
                  "|---|---:|---:|---:|---:|---:|---:|"])
    for scenario in scenario_suite():
        group = [(rows[(scenario.name, seed, "D1-L")], rows[(scenario.name, seed, "D1")]) for seed in EVAL_SEEDS]
        sla_delta = [a["sla_n"] - b["sla_n"] for a,b in group]
        quality_delta = [a["realized_quality_n"] - b["realized_quality_n"] for a,b in group]
        reward_delta = [a["reward"] - b["reward"] for a,b in group]
        recovered = sum(len(b["missed_ids"] - a["missed_ids"]) for a,b in group)
        regressed = sum(len(a["missed_ids"] - b["missed_ids"]) for a,b in group)
        reviews = sum(a["review_count"] for a,b in group)
        triggers = sum(a["trigger_conditions"] for a,b in group)
        lines.append(f"| {scenario.name} | {fmt_ci(sla_delta,1)} | {fmt_ci(quality_delta,1)} | {fmt_ci(reward_delta,1)} | {recovered} / {regressed} | {reviews} | {triggers} |")

    lines.extend(["", "## Condiciones observables al decidir", "",
                  "La señal causal local de D1-L existe solo en el estado actual: elección D1 inviable a tiempo y al menos una alternativa viable para el mismo analista. Estas dos condiciones, slack, duración propia, competencia propia, tamaño de cola y disponibilidad están en la instantánea antes de la elección. La calidad realizada, SLA final, reward, dificultad generadora y competencia/velocidad global son variables de evaluación posterior; no se usan para anticipar ni activar la revisión.",
                  "", "| Escenario | Decisiones D1-L observadas | Activaciones | Fracción trigger | Tamaño de cola medio en decisiones revisables | Alternativas a tiempo/decisión revisable |",
                  "|---|---:|---:|---:|---:|---:|"])
    for scenario in scenario_suite():
        group = [rows[(scenario.name, seed, "D1-L")] for seed in EVAL_SEEDS]
        pressures = [p for r in group for p in r["local_pressure"]]
        triggers = sum(r["trigger_conditions"] for r in group)
        decs = len(pressures)
        triggered_rows = [p for p in pressures if p[5]]
        lines.append(f"| {scenario.name} | {decs} | {triggers} | {triggers/max(1,decs):.3f} | {statistics.mean(p[0] for p in triggered_rows) if triggered_rows else 0:.2f} | {statistics.mean(p[2] for p in triggered_rows) if triggered_rows else 0:.3f} |")

    lines.extend(["", "En los triggers, la diferencia entre la alternativa aplicada y la selección original también es observable localmente antes del servicio:",
                  "", "| Escenario | Δ competencia propia | Δ duración estimada |",
                  "|---|---:|---:|"])
    for scenario in scenario_suite():
        triggered = [p for seed in EVAL_SEEDS
                     for p in rows[(scenario.name, seed, "D1-L")]["local_pressure"] if p[5]]
        dc = statistics.mean(p[6] for p in triggered) if triggered else 0.0
        ds = statistics.mean(p[7] for p in triggered) if triggered else 0.0
        lines.append(f"| {scenario.name} | {dc:+.4f} | {ds:+.5f} |")

    lines.extend(["", "## Selección adaptativa: factibilidad y riesgos", "",
                  "1. **Validez de la mejora:** las antiguas tasas de SLA estaban infladas para alertas escaladas porque medían L1, no resolución final. El reward no tenía ese error: se contabilizaba en la resolución efectiva. La repetición actualiza por tanto todas las conclusiones sobre SLA; las conclusiones de reward solo cambian donde una decisión previa se apoyaba además en SLA reportado.",
                  "2. **Anticipación observable:** la condición para cambiar D1→D1-L es observable exactamente en el mismo despacho. El cambio de duración y competencia propia entre la alerta original y la alternativa también es visible antes de empezar servicio; es relevante bajo heterogeneidad.",
                  "3. **Complementariedad:** D1-L es un no-op fuera de su trigger; por construcción no necesita un selector externo para evitar activarse en baja carga. En heterogeneidad el coste de calidad aparece junto con diferencias locales observables de skill/velocidad. Un selector podría, en principio, usar esa información, pero esta campaña no validó un criterio que prediga utilidad al horizonte completo.",
                  "4. **Riesgos de alternar durante el episodio:** el trigger repetido puede posponer muchas veces una alerta vencida; eleva su tiempo en cola, altera qué especialistas quedan disponibles y puede acumular backlog o degradar la calidad si la alternativa urgente es menos competente. La frecuencia del trigger puede causar oscilación solo si se añade un mecanismo externo, que aquí no se probó.",
                  "5. **Decisión:** GO para diseñar y validar un selector adaptativo local de alcance acotado, pero STOP para entrenar/promover un controlador general en esta fase. Las ganancias de reward/SLA son robustas en sobrecarga, elegibilidad restringida y deadlines ajustados. La señal de calidad adversa bajo heterogeneidad tiene indicadores locales observables, aunque aún no se ha probado que predigan la utilidad total de episodio.",
                  "", "## Limitaciones", "",
                  "Se reutilizaron seis regímenes y ocho semillas, todos sintéticos. Los intervalos son amplios y los cambios de analista alteran la aleatoriedad binaria de calidad, por eso se reporta además esperanza modelada. Las tasas de trigger son mediciones del estado de D1-L a medida que se ejecuta, no una variable exógena ni una garantía de selección rentable antes del episodio. Heterogeneidad global de plantilla es una condición configurada conocida por el evaluador, no necesariamente observable al controlador.",
                  "", "Reproducir: `python studies/soc_human_ai_organization/audit_d1_adaptation_feasibility.py`. Reutiliza seeds finales 740101–740108 para auditar la métrica; no ajusta políticas ni parámetros."])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT}; verified {len(rows)} episodes across identical traces")


if __name__ == "__main__":
    main()
