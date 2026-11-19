"""Preregistered small development/evaluation comparison of frozen D1-L."""
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

POLICIES = ("D1", "D1-L", "B0", "C0P1")
DEV_SEEDS = (640101, 640102)
EVAL_SEEDS = (740101, 740102, 740103, 740104, 740105, 740106, 740107, 740108)
T95_DF7 = 2.365


def scenario_suite():
    names = ("stationary_low", "near_capacity", "overload",
             "eligibility_restricted", "heterogeneous_skills_speeds",
             "tight_deadlines")
    return tuple(_make_scenario(name) for name in names)


def final_outcomes(env):
    final_jobs = {}
    for alert_id, route in env._routing.items():
        session = env._l2 if route else env._l1
        job = next((j for j in session.assignments if j.alert_id == alert_id), None)
        if job is not None:
            final_jobs[alert_id] = job
    return final_jobs


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
    reward = 0.0
    max_queue = max_expired_pending = 0
    while True:
        if policy == "C0P1":
            _, step_reward, term, trunc, info = env.step_fixed_organization(policy)
        else:
            _, step_reward, term, trunc, info = env.step_fixed(policy)
        if trunc:
            raise AssertionError("unexpected truncation")
        reward += float(step_reward)
        for session in (env._l1, env._l2):
            max_queue = max(max_queue, len(session.pending))
            max_expired_pending = max(max_expired_pending, sum(
                alert.deadline < session.now for alert in session.pending.values()))
        if term:
            break

    final_jobs = final_outcomes(env)
    alerts = {row.routed.alert.alert_id: row.routed.alert for row in env._admitted}
    met = {aid for aid, job in final_jobs.items() if job.completion <= alerts[aid].deadline}
    completed = set(env._resolved)
    missed = completed - met
    unresolved = set(alerts) - completed
    stages = []
    for session in (env._l1, env._l2):
        for job in session.assignments:
            alert = session.alerts[job.alert_id]
            stages.append((job.start, job.completion, max(0.0, job.start-alert.arrival)))
    waits = [x[2] for x in stages]
    expired_final = sum(alerts[aid].deadline < env._l1.drain_end
                        for aid in env._l1.pending)
    expired_final += sum(alerts[aid].deadline < env._l2.drain_end
                         for aid in env._l2.pending)

    d1l_trace = env._l1.d1_decisions + env._l2.d1_decisions
    local_counterfactuals = []
    for decision in d1l_trace:
        baseline = next(c for c in decision.candidates
                        if c.alert_id == decision.baseline_alert_id)
        viable = [c for c in decision.candidates if c.projected_on_time]
        local_counterfactuals.append((not baseline.projected_on_time and bool(viable),
                                      decision.review_activated))
    return {
        "scenario": scenario.name, "seed": seed, "policy": policy,
        "reward": reward, "sla": info["sla_fraction"],
        "quality": info["resolution_success_per_admitted"],
        "completed": info["completed"], "admitted": info["admitted"],
        "backlog": info["pending"], "max_queue": max_queue,
        "max_expired_pending": max_expired_pending,
        "expired_pending_final": expired_final,
        "mean_wait": statistics.mean(waits) if waits else 0.0,
        "review_count": info["d1l_review_count"],
        "d1l_decisions": len(d1l_trace),
        "review_trigger_conditions": sum(x[0] for x in local_counterfactuals),
        "missed_ids": missed, "unresolved_ids": unresolved,
        "recovered_from_d1": (), "regressed_from_d1": (),
        "resolution_correct": dict(env._resolution_correct),
    }


def ci95(values):
    mean = statistics.mean(values) if values else 0.0
    half = T95_DF7 * statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0.0
    return mean, mean-half, mean+half


def fmt_ci(values, digits=3):
    m, lo, hi = ci95(values)
    return f"{m:+.{digits}f} [{lo:+.{digits}f}, {hi:+.{digits}f}]"


def main():
    scenarios = scenario_suite()
    # Development episodes are run only as a protocol/smoke check. The rule
    # and all thresholds above were fixed before final-seed execution.
    dev = {}
    for scenario in scenarios:
        for seed in DEV_SEEDS:
            for policy in POLICIES:
                dev[(scenario.name, seed, policy)] = run_episode(scenario, seed, policy)

    rows = {}
    for scenario in scenarios:
        for seed in EVAL_SEEDS:
            for policy in POLICIES:
                rows[(scenario.name, seed, policy)] = run_episode(scenario, seed, policy)

    # Pair missed-SLA alerts by alert ID from identical generated traces.
    for scenario in scenarios:
        for seed in EVAL_SEEDS:
            base = rows[(scenario.name, seed, "D1")]
            corrected = rows[(scenario.name, seed, "D1-L")]
            corrected["recovered_from_d1"] = base["missed_ids"] - corrected["missed_ids"]
            corrected["regressed_from_d1"] = corrected["missed_ids"] - base["missed_ids"]

    lines = [
        "# Evaluación de la corrección local D1-L", "",
        "## Regla preregistrada",
        "D1-L conserva el orden reproducible de analistas y la decisión original D1. Solo revisa si la alerta que D1 habría elegido no se completaría antes de su deadline y queda otra alerta que ese mismo analista sí completaría a tiempo usando su duración propia. Entre esas alternativas escoge la menor holgura posterior al servicio (`deadline − ahora − duración`), después mayor competencia propia y finalmente deadline, llegada e ID ascendentes. No consulta compañeros, etiquetas, resultados ni eventos futuros. La tarea original no se elimina ni reserva: permanece en la cola y se vuelve a considerar en el siguiente punto de decisión. Sin alternativa viable, D1-L es idéntica a D1.", "",
        "## Protocolo",
        "Escenarios sintéticos: baja carga, cerca de capacidad, sobrecarga, elegibilidad restringida, competencias/velocidades heterogéneas y deadlines ajustados. Desarrollo: 2 semillas (640101–640102) por escenario, usadas solo para comprobar ejecución y frecuencia de activación. Evaluación final independiente: 8 semillas (740101–740108) por escenario, 192 episodios emparejados. Regla y recompensa congeladas antes de evaluar. IC95% t pareado bilateral sobre diferencias por semilla, df=7, t=2.365. B0 y C0P1 mantienen sus implementaciones. Backlog máximo es el máximo de alertas en cola observado en puntos de decisión; vencidas pendientes se miden en esos estados y al cierre con drenaje.", "",
        "Pesos de recompensa congelados: `(1.0, 1.0, 0.20, 0.50)`. No se añadieron términos ni penalizaciones.", "",
        "## Resultados por escenario",
        "| Escenario | Política | Reward | SLA | Calidad | Completadas/admitidas | Backlog medio final | Backlog máx. observado | Vencidas pendientes máx. | Vencidas pendientes H+D | Espera media | Activaciones D1-L |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    metrics = ("reward", "sla", "quality", "completed", "admitted", "backlog",
               "max_queue", "max_expired_pending", "expired_pending_final",
               "mean_wait", "review_count")
    for scenario in scenarios:
        for policy in POLICIES:
            group = [rows[(scenario.name, seed, policy)] for seed in EVAL_SEEDS]
            means = {key: statistics.mean(r[key] for r in group) for key in metrics}
            overdue_at_close = statistics.mean(r["expired_pending_final"] for r in group)
            lines.append(f"| {scenario.name} | {policy} | {means['reward']:.2f} | {means['sla']:.3f} | {means['quality']:.3f} | {means['completed']:.1f}/{means['admitted']:.1f} | {means['backlog']:.2f} | {means['max_queue']:.2f} | {means['max_expired_pending']:.2f} | {overdue_at_close:.2f} | {means['mean_wait']:.4f} | {means['review_count']:.1f} |")

        lines.append("")
        for metric, label in (("reward", "Reward"), ("sla", "SLA"),
                              ("quality", "Calidad"), ("completed", "Completadas"),
                              ("mean_wait", "Espera media"), ("max_queue", "Backlog máximo")):
            diffs = [rows[(scenario.name, seed, "D1-L")][metric]
                     - rows[(scenario.name, seed, "D1")][metric] for seed in EVAL_SEEDS]
            lines.append(f"- {scenario.name}: Δ {label} D1-L−D1 = {fmt_ci(diffs, 4 if metric == 'mean_wait' else 3)}.")
        reviews = sum(rows[(scenario.name, seed, "D1-L")]["review_count"] for seed in EVAL_SEEDS)
        flagged = sum(rows[(scenario.name, seed, "D1-L")]["review_trigger_conditions"] for seed in EVAL_SEEDS)
        recoveries = sum(len(rows[(scenario.name, seed, "D1-L")]["recovered_from_d1"]) for seed in EVAL_SEEDS)
        regressions = sum(len(rows[(scenario.name, seed, "D1-L")]["regressed_from_d1"]) for seed in EVAL_SEEDS)
        lines.append(f"- {scenario.name}: revisión activada {reviews} veces; condiciones D1 desfavorables observadas antes de revisar {flagged}; fallos SLA recuperados frente a D1 {recoveries}, regresiones a otras alertas {regressions}.")

    lines.extend(["", "## Comparación pareada con B0 y C0P1", "",
                  "| Escenario | D1-L − B0: Δ reward [IC95%] | D1-L − C0P1: Δ reward [IC95%] | C0P1 − D1-L: Δ SLA [IC95%] |",
                  "|---|---:|---:|---:|"])
    for scenario in scenarios:
        d_l_b0 = [rows[(scenario.name, seed, "D1-L")]["reward"] - rows[(scenario.name, seed, "B0")]["reward"] for seed in EVAL_SEEDS]
        d_l_c0 = [rows[(scenario.name, seed, "D1-L")]["reward"] - rows[(scenario.name, seed, "C0P1")]["reward"] for seed in EVAL_SEEDS]
        c0_d1l_sla = [rows[(scenario.name, seed, "C0P1")]["sla"] - rows[(scenario.name, seed, "D1-L")]["sla"] for seed in EVAL_SEEDS]
        lines.append(f"| {scenario.name} | {fmt_ci(d_l_b0, 2)} | {fmt_ci(d_l_c0, 2)} | {fmt_ci(c0_d1l_sla, 3)} |")

    trace_rows = []
    sample_scenario = next(s for s in scenarios if s.name == "eligibility_restricted")
    sample_seed = EVAL_SEEDS[0]
    for policy in ("D1", "D1-L"):
        # Rerun only the prespecified first evaluation seed with decision trace.
        env = B4EpisodeEnv(sample_scenario.config, sample_scenario.l1, sample_scenario.l2,
                           L1_SERVICE, L2_SERVICE, drain_period=DRAIN,
                           sequential_reward_weights=REWARD_WEIGHTS,
                           l1_service_by_analyst_class=sample_scenario.l1_services,
                           l2_service_by_analyst_class=sample_scenario.l2_services,
                           l1_roster_schedule=sample_scenario.l1_schedule,
                           l2_roster_schedule=sample_scenario.l2_schedule,
                           diagnostic_d1=True)
        env.reset(seed=sample_seed)
        while True:
            _, _, term, _, _ = env.step_fixed(policy)
            if term:
                break
        for pool in (env._l1, env._l2):
            for d in pool.d1_decisions:
                if d.review_activated or d.baseline_alert_id != d.alert_id:
                    baseline = next(c for c in d.candidates if c.alert_id == d.baseline_alert_id)
                    chosen = next(c for c in d.candidates if c.alert_id == d.alert_id)
                    trace_rows.append((policy, d.time, d.analyst_id, d.baseline_alert_id,
                                       d.alert_id, baseline.deadline_risk,
                                       baseline.projected_on_time, chosen.projected_on_time,
                                       baseline.own_competence, chosen.own_competence))
    lines.extend(["", "## Traza antes y después", "",
                  "Muestra emparejada: la primera semilla final del escenario restringido. Alternativas y scores se calculan en el estado local antes del servicio; no son resultados futuros.",
                  "", "| Política | t | Analista | Elección D1 | Elección aplicada | Riesgo elección D1 | D1 llegaría a tiempo | Aplicada llegaría a tiempo | Competencia D1 | Competencia aplicada |",
                  "|---|---:|---|---|---|---:|---|---|---:|---:|"])
    for row in trace_rows[:20]:
        policy, t, analyst, baseline, chosen, risk, baseline_ontime, chosen_ontime, base_comp, chosen_comp = row
        lines.append(f"| {policy} | {t:.3f} | {analyst} | {baseline} | {chosen} | {risk:.3f} | {'sí' if baseline_ontime else 'no'} | {'sí' if chosen_ontime else 'no'} | {base_comp:.3f} | {chosen_comp:.3f} |")

    lines.extend(["", "## Interpretación y decisión", "",
                  "La revisión corrige una elección local únicamente cuando su propia duración muestra que la opción D1 incumple y otra opción individual sí cumple. El informe diferencia esta condición y su frecuencia del SLA final pareado; el cambio de una asignación puede desplazar fallos a otras alertas, que se cuentan como recuperaciones/regresiones por ID.",
                  "",
                  "**Decisión: REVISE.** D1-L mejora claramente la recompensa frente a D1 en sobrecarga, elegibilidad restringida y deadlines ajustados; no cambia la baja carga ni ofrece diferencia clara cerca de capacidad. En el escenario de competencias/velocidades heterogéneas, la calidad cae de forma significativa, la espera aumenta y el backlog máximo empeora; D1-L tampoco alcanza C0P1 en recompensa/SLA allí. La corrección tiene valor en regímenes de alta presión, pero no es robusta entre escenarios y desplaza parte de la carga/errores. No debe promoverse como baseline general sin resolver el coste de calidad y el efecto de cola en heterogeneidad.",
                  "",
                  "## Límites y reproducción", "",
                  "Los escenarios, latencias de servicio, competencias, deadlines, calidad simulada y reglas de escalado son hipotéticos. Ocho semillas por régimen producen IC amplios. Backlog y vencidas durante el episodio se muestrean en puntos de decisión; no representan una integral continua. La corrección no usa información exacta de compañeros y no puede liberar especialistas ocupados. Desarrollo y evaluación usan seeds disjuntas; la regla no se ajustó con ninguna.",
                  "", "Reproducir: `python studies/soc_human_ai_organization/run_d1_local_correction.py`."])

    out = ROOT / "studies/soc_human_ai_organization/D1_LOCAL_CORRECTION_RESULTS.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    print(f"development_episodes={len(dev)} evaluation_episodes={len(rows)}")


if __name__ == "__main__":
    main()
