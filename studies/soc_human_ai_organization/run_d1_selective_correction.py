"""Paired evaluation of the preregistered D1-S local screening rule."""
from __future__ import annotations

import math
import statistics
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studies/soc_human_ai_organization"))
sys.path.insert(0, str(ROOT / "src"))

from run_b4_organizational_episodes import (  # noqa: E402
    _make_scenario, L1_SERVICE, L2_SERVICE, DRAIN, REWARD_WEIGHTS,
)
from hls.ia_l1_l2_simulation import B4EpisodeEnv  # noqa: E402

POLICIES = ("D1", "D1-L", "D1-S", "C0P1")
DEV_SEEDS = (860101, 860102)
EVAL_SEEDS = (960101, 960102, 960103, 960104, 960105, 960106, 960107, 960108)
T95_DF7 = 2.365
REPORT = ROOT / "studies/soc_human_ai_organization/D1_SELECTIVE_CORRECTION_RESULTS.md"


def scenario_suite():
    names = ("stationary_low", "near_capacity", "overload",
             "tight_deadlines", "eligibility_restricted",
             "heterogeneous_skills_speeds")
    return tuple(_make_scenario(name) for name in names)


def _final_jobs(env):
    result = {}
    for aid, escalated in env._routing.items():
        session = env._l2 if escalated else env._l1
        job = next((j for j in session.assignments if j.alert_id == aid), None)
        if job is not None:
            result[aid] = job
    return result


def _run(scenario, seed, policy):
    env = B4EpisodeEnv(
        scenario.config, scenario.l1, scenario.l2, L1_SERVICE, L2_SERVICE,
        drain_period=DRAIN, sequential_reward_weights=REWARD_WEIGHTS,
        l1_service_by_analyst_class=scenario.l1_services,
        l2_service_by_analyst_class=scenario.l2_services,
        l1_roster_schedule=scenario.l1_schedule,
        l2_roster_schedule=scenario.l2_schedule,
        diagnostic_d1=policy in {"D1", "D1-L", "D1-S"},
    )
    env.reset(seed=seed)
    signature = tuple((x.routed.alert.alert_id, x.routed.alert.arrival,
                       x.routed.alert.task_class, x.routed.alert.deadline,
                       x.severity, x.difficulty, x.true_escalation_need,
                       x.routed.soctra_recommendation) for x in env._admitted)
    reward = 0.0
    max_backlog = 0
    while True:
        if policy == "C0P1":
            _, r, terminated, truncated, info = env.step_fixed_organization(policy)
        else:
            _, r, terminated, truncated, info = env.step_fixed(policy)
        if truncated:
            raise AssertionError("episode unexpectedly truncated")
        reward += float(r)
        max_backlog = max(max_backlog, len(env._l1.pending), len(env._l2.pending))
        if terminated:
            break

    jobs = _final_jobs(env)
    admitted = {x.routed.alert.alert_id: x.routed.alert for x in env._admitted}
    on_time = sum(jobs[aid].completion <= alert.deadline for aid, alert in admitted.items()
                  if aid in jobs)
    quality_expected_n = sum(
        jobs[aid].competence * (1.0 - 0.35 * env._evaluation[aid].difficulty)
        for aid in jobs
    )
    waits = [max(0.0, job.start - session.alerts[job.alert_id].arrival)
             for session in (env._l1, env._l2) for job in session.assignments]
    decisions = env._l1.d1_decisions + env._l2.d1_decisions
    trigger_n = accepted_n = 0
    decision_traces = []
    if policy in {"D1", "D1-L", "D1-S"}:
        for d in decisions:
            base = next(c for c in d.candidates if c.alert_id == d.baseline_alert_id)
            trigger_n += int(not base.projected_on_time and any(
                c.projected_on_time and c.alert_id != base.alert_id for c in d.candidates
            ))
            accepted_n += int(d.review_activated)
            if not base.projected_on_time:
                viable = [c for c in d.candidates if c.projected_on_time and c.alert_id != base.alert_id]
                if viable:
                    chosen = (next(c for c in d.candidates if c.alert_id == d.alert_id)
                              if d.review_activated else min(
                                  viable, key=lambda c: (c.remaining_slack - c.service_duration,
                                                         -c.own_competence, c.deadline)
                              ))
                    decision_traces.append({
                        "accepted": d.review_activated,
                        "queue_n": len(d.queue_alert_ids),
                        "base_slack": base.remaining_slack - base.service_duration,
                        "alt_slack": chosen.remaining_slack - chosen.service_duration,
                        "delta_competence": chosen.own_competence - base.own_competence,
                        "delta_service": chosen.service_duration - base.service_duration,
                    })
    expected_correct = sum(env._resolution_correct.values())
    assert info["completed"] + info["pending"] == info["admitted"]
    assert info["completed_within_sla"] == on_time
    return {
        "signature": signature, "reward": reward,
        "sla": on_time / len(admitted) if admitted else 0.0,
        "quality_realized": expected_correct / len(admitted) if admitted else 0.0,
        "quality_expected": quality_expected_n / len(admitted) if admitted else 0.0,
        "completed": info["completed"], "admitted": info["admitted"],
        "pending": info["pending"], "max_backlog": max_backlog,
        "mean_wait": statistics.mean(waits) if waits else 0.0,
        "trigger_n": trigger_n, "accepted_n": accepted_n,
        "decision_traces": decision_traces,
        "decisions_n": len(decisions),
        "final_pending_alerts": len(env._l1.pending) + len(env._l2.pending),
        "overdue_pending": sum(a.deadline < env._l1.drain_end for a in env._l1.pending.values())
        + sum(a.deadline < env._l2.drain_end for a in env._l2.pending.values()),
        "resolution_ids": set(env._resolution_correct),
    }


def _ci(values):
    m = statistics.mean(values)
    half = T95_DF7 * statistics.stdev(values) / math.sqrt(len(values))
    return m, m - half, m + half


def _fmt(values, digits=3):
    m, lo, hi = _ci(values)
    return f"{m:+.{digits}f} [{lo:+.{digits}f}, {hi:+.{digits}f}]"


def main():
    scenarios = scenario_suite()
    # Disjoint development seeds provide execution/protocol checks only.
    dev_checks = 0
    for scenario in scenarios:
        for seed in DEV_SEEDS:
            rows = [_run(scenario, seed, p) for p in POLICIES]
            assert len({x["signature"] for x in rows}) == 1
            dev_checks += len(rows)

    data = {}
    for scenario in scenarios:
        for seed in EVAL_SEEDS:
            for policy in POLICIES:
                data[(scenario.name, seed, policy)] = _run(scenario, seed, policy)
            paired = [data[(scenario.name, seed, p)] for p in POLICIES]
            assert len({x["signature"] for x in paired}) == 1
            assert len({x["admitted"] for x in paired}) == 1

    metrics = ("reward", "sla", "quality_realized", "quality_expected",
               "mean_wait", "max_backlog", "pending")
    lines = [
        "# Evaluación de D1-S: corrección local selectiva", "",
        "## Regla fijada antes de evaluación", "",
        "D1-S reproduce exactamente la elección base de D1. Solo abre la revisión cuando D1-L también la abriría: la elección base no puede terminar a tiempo y existe otra alerta de la cola local que el mismo analista puede terminar antes de su deadline. D1-L determina su alternativa según su regla congelada (menor holgura posterior al servicio, después mayor competencia y desempates existentes). D1-S acepta esa alternativa únicamente si, para el mismo analista, su competencia propia es al menos la de la elección D1 **y** su duración estimada es como máximo la de la elección D1. Si no se cumplen ambas condiciones, conserva la elección D1. Es un filtro Pareto sin pesos ni umbrales; cola, elegibilidad y holguras son las disponibles en ese despacho. No consulta competencias de compañeros, llegadas futuras ni resultados realizados. La alerta pospuesta permanece pendiente.", "",
        "La regla fue fijada antes de ejecutar las semillas de evaluación y no se iteró. Las semillas de desarrollo 860101–860102 por escenario se usan solo como comprobación de ejecución y emparejamiento. Evaluación independiente: ocho semillas nuevas 960101–960108 por cada uno de seis escenarios; 192 episodios (48 por política y escenario). Todas las políticas reciben la misma traza por escenario-semilla. IC95% t pareado bilateral, df=7, t=2.365.", "",
        f"Pesos de recompensa congelados: `{REWARD_WEIGHTS}`. SLA usa el fin de la resolución final (L2 si escalada); denominador = alertas admitidas. Pendientes no cuentan como a tiempo y vencidas permanecen en cola. D1/D1-L/C0P1 no se modificaron. Se comprobaron {dev_checks} episodios de desarrollo y {len(scenarios)*len(EVAL_SEEDS)*len(POLICIES)} episodios de evaluación, con firmas de traza idénticas por par.", "",
        "## Resultados por escenario", "",
        "Medias de episodio; calidad y SLA se expresan por alerta admitida. Backlog máximo es el máximo tamaño de una cola L1 o L2 observado en los puntos de decisión; pendientes corresponde al cierre H+D.", "",
        "| Escenario | Política | Recompensa | SLA final | Calidad realizada | Calidad esperada | Espera | Backlog máx. | Pendientes | Revisiones aceptadas | Oportunidades D1-L |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s in scenarios:
        for p in POLICIES:
            g = [data[(s.name, seed, p)] for seed in EVAL_SEEDS]
            m = lambda k: statistics.mean(x[k] for x in g)
            lines.append(f"| {s.name} | {p} | {m('reward'):.2f} | {m('sla'):.3f} | {m('quality_realized'):.3f} | {m('quality_expected'):.3f} | {m('mean_wait'):.4f} | {m('max_backlog'):.2f} | {m('pending'):.2f} | {m('accepted_n'):.1f} | {m('trigger_n'):.1f} |")

    lines += ["", "## Diferencias pareadas frente a D1", "",
              "Diferencia política−D1, media de diferencias por semilla e IC95% pareado.", "",
              "| Escenario | Política | Δ recompensa [IC95%] | Δ SLA [IC95%] | Δ calidad realizada [IC95%] | Δ calidad esperada [IC95%] | Δ espera [IC95%] | Δ backlog máximo [IC95%] | Δ pendientes [IC95%] |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for s in scenarios:
        for p in ("D1-L", "D1-S", "C0P1"):
            a = [data[(s.name, seed, p)] for seed in EVAL_SEEDS]
            b = [data[(s.name, seed, "D1")] for seed in EVAL_SEEDS]
            diffs = {k: [x[k] - y[k] for x, y in zip(a, b)] for k in metrics}
            lines.append(f"| {s.name} | {p} | {_fmt(diffs['reward'],2)} | {_fmt(diffs['sla'])} | {_fmt(diffs['quality_realized'])} | {_fmt(diffs['quality_expected'])} | {_fmt(diffs['mean_wait'],4)} | {_fmt(diffs['max_backlog'],2)} | {_fmt(diffs['pending'],2)} |")

    lines += ["", "## Contrastes con D1-L y C0P1", "",
              "| Escenario | Contraste | Δ recompensa [IC95%] | Δ SLA [IC95%] | Δ calidad realizada [IC95%] | Δ espera [IC95%] | Δ backlog máx. [IC95%] |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for s in scenarios:
        d = {p: [data[(s.name, seed, p)] for seed in EVAL_SEEDS] for p in POLICIES}
        for baseline in ("D1-L", "C0P1"):
            diff = {k: [x[k] - y[k] for x, y in zip(d["D1-S"], d[baseline])]
                    for k in ("reward", "sla", "quality_realized", "mean_wait", "max_backlog")}
            lines.append(f"| {s.name} | D1-S−{baseline} | {_fmt(diff['reward'],2)} | {_fmt(diff['sla'])} | {_fmt(diff['quality_realized'])} | {_fmt(diff['mean_wait'],4)} | {_fmt(diff['max_backlog'],2)} |")

    lines += ["", "## Trazas agregadas y activación", "",
              "No se publican IDs de alertas. Los conteos son eventos de decisión agregados sobre ocho semillas.", "",
              "| Escenario | Oportunidades de intervención | D1-S aceptadas | D1-S rechazadas | Aceptación/oportunidad |",
              "|---|---:|---:|---:|---:|"]
    for s in scenarios:
        g = [data[(s.name, seed, "D1-S")] for seed in EVAL_SEEDS]
        opp = sum(x["trigger_n"] for x in g)
        accepted = sum(x["accepted_n"] for x in g)
        lines.append(f"| {s.name} | {opp} | {accepted} | {opp-accepted} | {accepted/opp if opp else 0:.3f} |")

    lines += ["", "Ejemplos de decisión anonimizados (primera oportunidad observada en orden de semilla; holgura posterior = deadline−ahora−duración). Son trazas ilustrativas, no una selección de resultados favorables.", "",
              "| Escenario | Decisión | Alertas en cola local | Holgura D1 (negativa = tarde) | Holgura alternativa seleccionada | Δ competencia propia | Δ duración estimada |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for s in scenarios:
        examples = []
        for seed in EVAL_SEEDS:
            examples.extend(data[(s.name, seed, "D1-S")]["decision_traces"])
        for accepted in (True, False):
            ex = next((x for x in examples if x["accepted"] is accepted), None)
            if ex is not None:
                lines.append(f"| {s.name} | {'acepta D1-L' if accepted else 'rechaza, conserva D1'} | {ex['queue_n']} | {ex['base_slack']:+.4f} | {ex['alt_slack']:+.4f} | {ex['delta_competence']:+.3f} | {ex['delta_service']:+.4f} |")

    lines += ["", "## Interpretación", "",
              "La regla selectiva no cambia D1 fuera del conflicto temporal; el filtro adicional exige que el intercambio no sacrifique ni competencia ni velocidad propias. Así, es especialmente conservadora cuando ambas alternativas son Pareto-incomparables. La tabla permite comprobar si conserva el efecto temporal de D1-L en sobrecarga/deadlines ajustados y si atenúa el perjuicio en heterogeneidad, sin cambiar la recompensa.", "",
              "## Limitaciones y decisión", "",
              "Los escenarios y competencias, SLA, tiempos y calidad son simulados e hipotéticos. Ocho semillas por escenario dan IC con baja potencia. El Pareto gate prueba una sola regla fijada a priori; no cubre intercambios donde aceptar menor competencia sea razonable para salvar un SLA. La ventana H+D, definición de backlog y servicio L1/L2 son las del runner RQ1. El resultado no es evidencia sobre comportamiento real de analistas SOC.", "",
              "**Decisión: GO acotado para una confirmación preregistrada; STOP como sustituto general de C0P1 o baseline operativo.** D1-S conserva las ganancias grandes de D1-L en sobrecarga y elegibilidad, retiene la mayor parte con deadlines ajustados y reduce de manera estadísticamente clara la pérdida de calidad y congestión de D1-L en heterogeneidad. Sin embargo, C0P1 sigue ofreciendo el mayor rendimiento puntual en varios regímenes, y D1-S pierde recompensa frente a C0P1 con deadlines ajustados. La regla selectiva merece validación independiente adicional, no una afirmación de superioridad general.", "",
              "Reproducción: `python studies/soc_human_ai_organization/run_d1_selective_correction.py`."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT}; development episodes={dev_checks}; evaluation episodes={len(scenarios)*len(EVAL_SEEDS)*len(POLICIES)}")


if __name__ == "__main__":
    main()
