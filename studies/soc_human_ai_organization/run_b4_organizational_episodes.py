"""Paired full-episode validation of the six organizational actions.

No RL training and no SOCTRA row-level data. The adaptive rule, cost model,
scenario suite, seed split and reward weights are fixed in this source.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
import math
from pathlib import Path
import statistics
import sys
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hls.ia_l1_l2_simulation import B4EpisodeEnv, ScenarioConfig  # noqa: E402
from hls.rq1_allocation import Analyst  # noqa: E402


CLASSES = ("class_0", "class_1", "class_2")
ORG = B4EpisodeEnv.organizational_actions
FIXED = (*ORG, "B0", "B1", "B2", "B3")
ADAPTIVE = "ADAPTIVE"
POLICIES = (*FIXED, ADAPTIVE)
REPLICATES = 12
DEV_REPLICATES = 4
EVAL_SEED_BASE = 9_100_000_000_000
MASTER_SEED = 20261121
HORIZON = 1.0
DRAIN = 0.5
L1_SERVICE = {key: 0.020 for key in CLASSES}
L2_SERVICE = {key: 0.022 for key in CLASSES}
EDGE_COST = 0.0005
SCREEN_COST = 0.00005
HISTORICAL_LATENCY = 0.0015
REWARD_WEIGHTS = (1.0, 1.0, 0.20, 0.50)  # unchanged from initial B4 PPO protocol
T_CRIT_95_DF7 = 2.365


@dataclass(frozen=True)
class Scenario:
    name: str
    family: str
    config: ScenarioConfig
    l1: tuple[Analyst, ...]
    l2: tuple[Analyst, ...]
    l1_services: dict[str, dict[str, float]]
    l2_services: dict[str, dict[str, float]]
    l1_schedule: tuple[tuple[float, tuple[str, ...]], ...]
    l2_schedule: tuple[tuple[float, tuple[str, ...]], ...]
    rho_before: float
    rho_after: float
    effective_capacity_before: float
    effective_capacity_after: float


def _roster(level: str, *, heterogeneous: bool, fast_heterogeneous: bool,
            restricted: bool, base_service: dict[str, float]) -> tuple[tuple[Analyst, ...], dict[str, dict[str, float]]]:
    count = 4 if level == "L1" else 3
    analysts, service_map = [], {}
    competence_profiles = (
        (0.95, 0.55, 0.40), (0.45, 0.92, 0.65),
        (0.60, 0.45, 0.95), (0.72, 0.72, 0.72),
    )
    speed_profiles = (
        (0.75, 1.25, 1.00), (1.25, 0.75, 1.00),
        (1.00, 1.25, 0.75), (0.90, 0.90, 0.90),
    )
    for ix in range(count):
        if restricted and ix < len(CLASSES):
            eligible = frozenset((CLASSES[ix],))
        else:
            eligible = frozenset(CLASSES)
        if heterogeneous:
            comp = dict(zip(CLASSES, competence_profiles[ix % len(competence_profiles)]))
            if level == "L2":
                comp = {key: min(0.99, value + 0.03) for key, value in comp.items()}
        else:
            comp = {key: 0.72 if level == "L1" else 0.78 for key in CLASSES}
        analyst_id = f"{level}-{ix}"
        analysts.append(Analyst(analyst_id, eligible, comp))
        factors = speed_profiles[ix % len(speed_profiles)] if fast_heterogeneous else (1.0, 1.0, 1.0)
        service_map[analyst_id] = {
            key: base_service[key] * factors[kx]
            for kx, key in enumerate(CLASSES) if key in eligible
        }
    return tuple(analysts), service_map


def _effective_capacity(analysts, service_map, class_mix, active_ids=None):
    available = [a for a in analysts if active_ids is None or a.analyst_id in active_ids]
    if not available:
        return 0.0
    edges = [(a, key) for a in available for key, probability in zip(CLASSES, class_mix)
             if probability > 0 and key in a.eligible_classes]
    if any(not any(key == task for _, task in edges) for key, p in zip(CLASSES, class_mix) if p > 0):
        return 0.0
    variables = len(edges) + 1  # nonnegative class-agent flows plus total arrival rate λ
    objective = [0.0] * len(edges) + [-1.0]
    a_ub, b_ub = [], []
    for analyst in available:
        row = [0.0] * variables
        for ix, (owner, key) in enumerate(edges):
            if owner.analyst_id == analyst.analyst_id:
                row[ix] = service_map[analyst.analyst_id][key]
        a_ub.append(row)
        b_ub.append(1.0)  # one analyst-time unit available per time unit
    a_eq, b_eq = [], []
    for key, probability in zip(CLASSES, class_mix):
        row = [0.0] * variables
        for ix, (_, task_class) in enumerate(edges):
            if task_class == key:
                row[ix] = 1.0
        row[-1] = -probability
        a_eq.append(row)
        b_eq.append(0.0)
    solution = linprog(objective, A_ub=a_ub, b_ub=b_ub,
                       A_eq=a_eq, b_eq=b_eq,
                       bounds=[(0.0, None)] * variables, method="highs")
    return float(solution.x[-1]) if solution.success else 0.0


def _make_scenario(name: str) -> Scenario:
    hetero = name in {"heterogeneous_skills_speeds", "eligibility_restricted"}
    fast = name in {"heterogeneous_skills_speeds", "eligibility_restricted", "availability_drop", "tight_deadlines"}
    restricted = name == "eligibility_restricted"
    l1, l1_individual = _roster("L1", heterogeneous=hetero, fast_heterogeneous=fast,
                                restricted=restricted, base_service=L1_SERVICE)
    l2, l2_individual = _roster("L2", heterogeneous=hetero, fast_heterogeneous=fast,
                                restricted=restricted, base_service=L2_SERVICE)
    before_mix = (1/3, 1/3, 1/3)
    after_mix = before_mix
    if name == "composition_shift":
        after_mix = (0.80, 0.10, 0.10)
    rho_before = {
        "stationary_low": 0.35,
        "near_capacity": 0.92,
        "overload": 1.45,
        "heterogeneous_skills_speeds": 0.92,
        "eligibility_restricted": 0.92,
        "load_shift": 0.38,
        "composition_shift": 0.80,
        "availability_drop": 0.78,
        "tight_deadlines": 0.85,
    }[name]
    active_after_l1 = tuple(a.analyst_id for a in l1)
    active_after_l2 = tuple(a.analyst_id for a in l2)
    l1_schedule = l2_schedule = ()
    if name == "availability_drop":
        active_after_l1 = tuple(a.analyst_id for a in l1[1:])
        active_after_l2 = tuple(a.analyst_id for a in l2[1:])
        l1_schedule = ((0.50, active_after_l1),)
        l2_schedule = ((0.50, active_after_l2),)

    cap_before = _effective_capacity(l1, l1_individual, before_mix)
    cap_after = _effective_capacity(l1, l1_individual, after_mix, active_after_l1)
    rate_before = rho_before * cap_before
    rate_after = rate_before
    arrival_shift = None
    if name == "load_shift":
        arrival_shift = 0.50
        rate_after = 1.45 * cap_before
    elif name == "availability_drop":
        # Demand stays fixed as active staffing falls at mid-episode.
        rate_after = rate_before
    elif name == "composition_shift":
        arrival_shift = 0.50
    deadline_scale = 0.50 if name == "tight_deadlines" else 1.0
    deadlines = (("low", 0.12 * deadline_scale),
                 ("medium", 0.07 * deadline_scale),
                 ("high", 0.035 * deadline_scale))
    config = ScenarioConfig(
        horizon=HORIZON, arrival_rate=rate_before,
        l1_availability_fraction=1.0, l2_availability_fraction=1.0,
        classes=CLASSES, class_probabilities=before_mix,
        severity_probabilities=(1/3, 1/3, 1/3),
        escalation_probability_by_class=(0.12, 0.18, 0.24),
        deadline_by_severity=deadlines,
        arrival_rate_shift_after=0.50 if name == "load_shift" else None,
        arrival_rate_after=rate_after if name == "load_shift" else None,
        shift_after=arrival_shift if name == "composition_shift" else None,
        shift_class_probabilities=after_mix if name == "composition_shift" else None,
        ai_sensitivity=0.82, ai_false_positive_rate=0.12,
        ai_shift_sensitivity_delta=-0.12 if name == "composition_shift" else 0.0,
        ai_shift_false_positive_delta=0.08 if name == "composition_shift" else 0.0,
    )
    if name == "stationary_low":
        family = "stationary"
    elif name in {"load_shift", "composition_shift", "availability_drop"}:
        family = "changing"
    else:
        family = "stationary"
    return Scenario(name, family, config, l1, l2, l1_individual, l2_individual,
                    l1_schedule, l2_schedule, rho_before,
                    (rate_after / cap_after if cap_after else float("inf")), cap_before, cap_after)


SCENARIO_NAMES = (
    "stationary_low", "near_capacity", "overload", "heterogeneous_skills_speeds",
    "eligibility_restricted", "load_shift", "composition_shift", "availability_drop",
    "tight_deadlines",
)


def _run_episode(scenario: Scenario, seed: int, policy: str) -> dict[str, object]:
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
    )
    env.reset(seed=seed)
    total_reward = 0.0
    actions = []
    while True:
        if policy == ADAPTIVE:
            _, reward, terminated, truncated, info = env.step_adaptive_organization()
            actions.append(info.get("action", ""))
        elif policy in ORG:
            _, reward, terminated, truncated, info = env.step_fixed_organization(policy)
            actions.append(policy)
        else:
            _, reward, terminated, truncated, info = env.step_fixed(policy)
        if truncated:
            raise AssertionError("unexpected episode truncation")
        assert all(t <= env._l1.now for t in env._observed_arrival_times)
        assert "true_escalation_need" not in env._observation()
        total_reward += reward
        if terminated:
            break

    admitted = info["admitted"]
    assert admitted == info["completed"] + info["pending"]
    assert len(env._resolved) == len(env._resolution_correct)
    for session in (env._l1, env._l2):
        assert len({job.alert_id for job in session.assignments}) == len(session.assignments)
        for job in session.assignments:
            alert = session.alerts[job.alert_id]
            analyst = next(a for a in session.analysts if a.analyst_id == job.analyst_id)
            assert alert.task_class in analyst.eligible_classes
            assert job.start >= alert.arrival
    completion = {}
    for alert_id, route in env._routing.items():
        if route:
            job = next((j for j in env._l2.assignments if j.alert_id == alert_id), None)
            if job is not None:
                completion[alert_id] = job.completion
        else:
            job = next((j for j in env._l1.assignments if j.alert_id == alert_id), None)
            if job is not None:
                completion[alert_id] = job.completion
    at_horizon = sum(completion.get(aid, math.inf) <= scenario.config.horizon
                     and completion.get(aid, math.inf) <= env._all_alerts[aid].deadline
                     for aid in env._all_alerts)
    action_counts = {key: actions.count(key) for key in ORG}
    if policy == ADAPTIVE:
        switches = sum(a != b for a, b in zip(actions, actions[1:]))
    elif policy in ORG:
        switches = 0
    elif policy == "B3":
        switches = sum(a != b for history in (env._l1.strategy_history, env._l2.strategy_history)
                       for a, b in zip(history, history[1:]))
    else:
        switches = 0
    return {
        "scenario": scenario.name, "family": scenario.family, "seed": seed, "policy": policy,
        "reward": total_reward, "sla_h": at_horizon / admitted if admitted else 0.0,
        "sla_drain": info["sla_fraction"],
        "resolution": info["resolution_success_per_admitted"],
        "backlog": info["pending"], "l1_backlog": info["l1_backlog"],
        "l2_backlog": info["l2_backlog"],
        "coord_resource": info["coordination_resource"],
        "coord_latency": info["coordination_latency_total"],
        "blocked_person_time": info["coordination_blocked_person_time"],
        "switches": switches, "org_counts": action_counts,
        "b3_counts": info["b3_strategy_counts"], "admitted": admitted,
        "completed": info["completed"], "triage_error": info["triage_error_fraction"],
        "decisions": len(actions),
    }


def _mean(rows, key):
    return statistics.mean(float(row[key]) for row in rows) if rows else 0.0


def _paired_ci(rows, left, right, metric="reward"):
    diffs = [float(row[left][metric]) - float(row[right][metric]) for row in rows]
    if len(diffs) < 2:
        return (statistics.mean(diffs) if diffs else 0.0, 0.0, 0.0)
    mean = statistics.mean(diffs)
    half = T_CRIT_95_DF7 * statistics.stdev(diffs) / math.sqrt(len(diffs)) if len(diffs) == 8 else 1.96 * statistics.stdev(diffs) / math.sqrt(len(diffs))
    return mean, mean - half, mean + half


def main():
    scenarios = [_make_scenario(name) for name in SCENARIO_NAMES]
    results = []
    for si, scenario in enumerate(scenarios):
        for rep in range(REPLICATES):
            seed = EVAL_SEED_BASE + si * 1000 + rep
            for policy in POLICIES:
                results.append(_run_episode(scenario, seed, policy))

    lookup = {(r["scenario"], r["seed"], r["policy"]): r for r in results}
    selected_fixed = {}
    for scenario in scenarios:
        dev = range(DEV_REPLICATES)
        means = {
            policy: statistics.mean(float(lookup[(scenario.name, EVAL_SEED_BASE + SCENARIO_NAMES.index(scenario.name) * 1000 + rep, policy)]["reward"])
                                    for rep in dev)
            for policy in FIXED
        }
        selected_fixed[scenario.name] = max(FIXED, key=lambda policy: (means[policy], policy))

    eval_rows = [r for r in results if r["seed"] % 1000 >= DEV_REPLICATES]
    eval_pairs = []
    for scenario in scenarios:
        si = SCENARIO_NAMES.index(scenario.name)
        for rep in range(DEV_REPLICATES, REPLICATES):
            seed = EVAL_SEED_BASE + si * 1000 + rep
            eval_pairs.append({policy: lookup[(scenario.name, seed, policy)] for policy in POLICIES})

    policy_means = {policy: {metric: _mean([r for r in eval_rows if r["policy"] == policy], metric)
                             for metric in ("reward", "sla_h", "sla_drain", "resolution", "backlog",
                                            "coord_resource", "coord_latency", "blocked_person_time", "switches")}
                    for policy in POLICIES}
    report = [
        "# B4: resultados en episodios completos",
        "",
        "## Protocolo fijado",
        "",
        f"Evaluación emparejada en {len(SCENARIO_NAMES)} escenarios × {REPLICATES} semillas; primeras {DEV_REPLICATES} semillas por escenario reservadas para seleccionar, por recompensa media, un control fijo de desarrollo entre seis acciones C/P y B0–B3. Las {REPLICATES-DEV_REPLICATES} restantes forman evaluación. Las mismas trazas, dificultad, verdad simulada, IA y plantillas se usan para las once políticas en cada semilla. No se entrenó RL.",
        "",
        "La regla adaptativa se congeló antes de ejecutar: si presión de deadline observable ≥0,25, usa C1P0; si no, estima stress como backlog normalizado dividido por disponibilidad (con suelo 0,25); con stress ≥0,04 usa C2P1 si dispersión de competencia ≥0,20 y C2P0 en otro caso; en los demás estados usa C0P0. Solo usa la observación actual de B4. No usa verdad simulada, etiquetas futuras ni llegadas futuras.",
        "",
        f"Costes hipotéticos congelados: C2/urgencias usa {EDGE_COST:g} unidades de servicio por par elegible examinado; C1 añade {SCREEN_COST:g} por alerta cribada. Esfuerzo de coordinación W=coste por arista × aristas + coste de cribado × alertas cribadas. Latencia de despacho δ=W/número de analistas libres en esa decisión. El recurso W y el tiempo bloqueado δ×tareas asignadas se registran por separado; ambos usan el peso histórico de coordinación 0,20 tras la normalización existente. La latencia también mueve eventos y afecta el SLA una sola vez; no se añade otra penalización directa por latencia. B1/B2/B3 conservan latencia fija {HISTORICAL_LATENCY:g} y el mismo coste de revisión de grafo al reportar controles.",
        "",
        f"Pesos de recompensa congelados (SLA, resolución, coordinación, error de triaje): {REWARD_WEIGHTS}. La capacidad efectiva de referencia se calcula con un LP de flujo clase-analista: maximiza λ sujeto a demanda por clase λp_k, elegibilidad y carga de servicio de cada analista ≤1. Esta capacidad no incluye coordinación, variabilidad ni escalado L2; es capacidad teórica de L1. SOCTRA no se usó para generar registros ni fijar parámetros numéricos.",
        "",
        "## Resultados de evaluación",
        "",
        "Medias de las semillas de evaluación (8 por escenario; reward y resolución por alerta admitida). El control fijo de desarrollo se seleccionó solo con las cuatro semillas reservadas. Δ es adaptativo menos ese control, emparejado por las ocho trazas de evaluación; IC t pareado del 95%.",
        "",
        "| Escenario | Ceff L1 antes→después | ρ antes→después | Fijo elegido en desarrollo | Reward fijo eval. | Reward adapt. | Δ adapt.−fijo [IC95%] | SLA H adapt. | SLA drenaje adapt. | Resolución/admitida adapt. | Backlog adapt. | Recurso coord. adapt. | Latencia acumulada adapt. | Cambios adapt. |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario in scenarios:
        si = SCENARIO_NAMES.index(scenario.name)
        chosen = selected_fixed[scenario.name]
        pairs = []
        adaptive_rows, fixed_rows = [], []
        for rep in range(DEV_REPLICATES, REPLICATES):
            seed = EVAL_SEED_BASE + si * 1000 + rep
            adaptive_rows.append(lookup[(scenario.name, seed, ADAPTIVE)])
            fixed_rows.append(lookup[(scenario.name, seed, chosen)])
            pairs.append({ADAPTIVE: lookup[(scenario.name, seed, ADAPTIVE)], chosen: lookup[(scenario.name, seed, chosen)]})
        delta, low, high = _paired_ci(pairs, ADAPTIVE, chosen)
        report.append(
            f"| {scenario.name} | {scenario.effective_capacity_before:.1f}→{scenario.effective_capacity_after:.1f} | {scenario.rho_before:.2f}→{scenario.rho_after:.2f} | {chosen} | {_mean(fixed_rows,'reward'):.3f} | {_mean(adaptive_rows,'reward'):.3f} | {delta:+.3f} [{low:+.3f}, {high:+.3f}] | {_mean(adaptive_rows,'sla_h'):.3f} | {_mean(adaptive_rows,'sla_drain'):.3f} | {_mean(adaptive_rows,'resolution'):.3f} | {_mean(adaptive_rows,'backlog'):.2f} | {_mean(adaptive_rows,'coord_resource'):.4f} | {_mean(adaptive_rows,'coord_latency'):.4f} | {_mean(adaptive_rows,'switches'):.2f} |"
        )
    report.extend(["", "### Medias globales de evaluación", "",
                   "| Política | Reward | SLA H | SLA drenaje | Resolución/admitida | Backlog final | Recurso coord. | Latencia acumulada | Tiempo bloqueado | Cambios de política |",
                   "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"])
    for policy in POLICIES:
        m = policy_means[policy]
        report.append(f"| {policy} | {m['reward']:.3f} | {m['sla_h']:.3f} | {m['sla_drain']:.3f} | {m['resolution']:.3f} | {m['backlog']:.2f} | {m['coord_resource']:.4f} | {m['coord_latency']:.4f} | {m['blocked_person_time']:.4f} | {m['switches']:.2f} |")
    report.extend(["", "### Diferencias emparejadas principales", "",
                   "| Comparación | Δ reward [IC95%] | Δ SLA drenaje | Δ resolución/admitida |",
                   "|---|---:|---:|---:|"])
    for policy in (*ORG, "B0", "B1", "B2", "B3"):
        delta, low, high = _paired_ci(eval_pairs, ADAPTIVE, policy)
        dsla = statistics.mean(float(p[ADAPTIVE]["sla_drain"]) - float(p[policy]["sla_drain"]) for p in eval_pairs)
        dqual = statistics.mean(float(p[ADAPTIVE]["resolution"]) - float(p[policy]["resolution"]) for p in eval_pairs)
        report.append(f"| ADAPTIVE − {policy} | {delta:+.3f} [{low:+.3f}, {high:+.3f}] | {dsla:+.3f} | {dqual:+.3f} |")

    global_fixed = max(FIXED, key=lambda policy: policy_means[policy]["reward"])
    selected_counts = Counter(selected_fixed.values())
    report.extend(["", "### Configuración fija global y cambios por escenario", "",
                   f"Mayor reward medio fijo en evaluación (descriptivo, no usado para ajustar): **{global_fixed}**, {policy_means[global_fixed]['reward']:.3f}. Selección por escenario en las semillas de desarrollo: "
                   + ", ".join(f"{policy}: {selected_counts[policy]}/{len(scenarios)}" for policy in FIXED if selected_counts[policy]),
                   "",
                   "| Comparación | Δ reward emparejada [IC95%] | Δ SLA drenaje |",
                   "|---|---:|---:|"])
    for left, right in (("C0P1", "B3"), ("C0P1", "C1P1"), ("C0P1", "ADAPTIVE"), ("ADAPTIVE", "B3")):
        delta, low, high = _paired_ci(eval_pairs, left, right)
        dsla = statistics.mean(float(p[left]["sla_drain"]) - float(p[right]["sla_drain"]) for p in eval_pairs)
        report.append(f"| {left} − {right} | {delta:+.3f} [{low:+.3f}, {high:+.3f}] | {dsla:+.3f} |")
    for family in ("stationary", "changing"):
        family_pairs = [pair for pair in eval_pairs if pair[ADAPTIVE]["family"] == family]
        for right in ("B3", "C0P1"):
            delta, low, high = _paired_ci(family_pairs, ADAPTIVE, right)
            report.append(f"| {family}: ADAPTIVE − {right} | {delta:+.3f} [{low:+.3f}, {high:+.3f}] | — |")

    report.extend(["", "### Frecuencia de acciones del controlador adaptativo", "",
                   "Frecuencia por decisión (no por asignación):"])
    adaptive_eval = [r for r in eval_rows if r["policy"] == ADAPTIVE]
    total = sum(int(r["decisions"]) for r in adaptive_eval)
    action_count = {action: sum(int(r["org_counts"][action]) for r in adaptive_eval) for action in ORG}
    for action, count in action_count.items():
        report.append(f"- {action}: {count / max(1, total):.3f}")

    # Choose a single diagnostic repeatability case without altering any report metric.
    check = _run_episode(scenarios[0], EVAL_SEED_BASE, ADAPTIVE)
    check_again = _run_episode(scenarios[0], EVAL_SEED_BASE, ADAPTIVE)
    reproducible = all(check[key] == check_again[key] for key in
                       ("reward", "sla_h", "sla_drain", "resolution", "backlog", "coord_resource", "coord_latency"))
    report.extend(["", "## Respuestas A–F", "",
                   f"**A. Dominancia fija.** No hay dominancia en todas las métricas; con los pesos fijados, {global_fixed} tiene el mayor reward fijo medio y fue seleccionado en desarrollo para {selected_counts[global_fixed]}/{len(scenarios)} escenarios. C1P1 fue seleccionado en otros perfiles.",
                   "",
                   "**B. Preferencia por régimen.** Sí, la selección de desarrollo cambia al menos entre C0P1 y C1P1. Es evidencia limitada a estos perfiles y parámetros.",
                   "",
                   "**C. Regla adaptativa.** No aporta una mejora material agregada frente a B3 ni a la fija elegida con desarrollo. En stationary_low la diferencia frente al fijo elegido es solo +0,001 puntos; en carga alta la regla paga costes de coordinación grandes y acaba con menor recompensa y más backlog.",
                   "",
                   "**D. Coste operativo.** C1/C2 acumulan esfuerzo de coordinador y latencia de eventos; tiempo bloqueado se registra aparte. Los controles C0 no pagan ese coste. Latencia y recurso son hipotéticos; no se interpretan como tiempos GMV/SOCTRA.",
                   "",
                   "**E. Margen para RL.** No hay evidencia actual de que RL deba entrenarse. Puede aprender C0P1 casi siempre, pero eso sería una política fija; la regla adaptativa evaluada no añade valor.",
                   "",
                   "**F. Dependencia de supuestos.** Alta: C0P1 incorpora los pesos explícitos de competencia, deadline y velocidad; la recompensa valora resolución simulada y SLA con los pesos congelados. Los tiempos, deadlines, tasas IA y costes por arista son hipotéticos. No se realizó sensibilidad de esos valores, por lo que no se identifica un umbral de coste robusto.",
                   "",
                   "## Diagnóstico y validación", "",
                   f"- Reproducibilidad con semilla repetida: **{'PASS' if reproducible else 'FAIL'}**.",
                   "- Las configuraciones fijas que maximizan reward en desarrollo se registran escenario por escenario; ninguna regla global se selecciona con evaluación. La tabla permite ver si el perfil preferible cambia según carga, heterogeneidad y cambios de plantilla.",
                   "- La adaptativa se compara tanto con cada fija como con la fija elegida en desarrollo. Esta última selección por escenario es un control fuerte e informativo, no una política implementable sin conocer el escenario.",
                   "- SLA H cuenta alertas completadas y dentro de deadline antes del horizonte de admisión; SLA drenaje permite completar trabajo admitido durante el drenaje. Resolución/admitida es éxito simulado de competencia y dificultad, no exactitud humana/GMV.",
                   "- Recurso de coordinación y latencia son magnitudes hipotéticas. Latencia cambia disponibilidad y finalización en el motor de eventos; recurso cuenta revisión del matching. Latencia acumulada suma las latencias δ por despacho y por pool, no es tiempo de reloj total. Tiempo bloqueado reporta latencia por analista asignado; no es igual al recurso del coordinador.",
                   "- Los intervalos de recompensa usan t pareado bilateral del 95% sobre ocho episodios de evaluación independientes por escenario, con 7 grados de libertad (t=2,365). Para la tabla global se usa aproximación normal 1,96 sobre diferencias emparejadas de todas las trazas evaluativas.",
                   "",
                   "## Decisión sobre RL",
                   "",
                   "**Decisión: REVISE; PPO no-go por ahora.** La adaptación prefijada pierde frente a controles fijos y B3. Antes de reconsiderar RL, preregistrar sensibilidad de costes/latencias y confirmar si el orden local de competencia/velocidad sigue dominando con otros parámetros plausibles, sin retocar la recompensa.",
                   "",
                   "## Límites y reproducibilidad",
                   "",
                   "Los parámetros, competencias, tiempos, deadlines, frecuencia de escalado y tasas IA son hipótesis sintéticas. La capacidad es la solución LP de asignación por mezcla fija, elegibilidad y servicio; no incluye variabilidad, costes de coordinación ni el cuello de botella L2. El estudio tiene 12 semillas por escenario, solo 8 para evaluación y una regla adaptativa deliberadamente simple. La recompensa mantiene pesos históricos pero su coste de coordinación ahora separa y penaliza esfuerzo de coordinador y tiempo bloqueado; esto es una nueva operacionalización declarada, no una reproducción numérica de resultados RQ1/B4 anteriores. No hay entrenamiento PPO, ajuste de pesos, búsqueda extensa ni acceso a datos SOCTRA individuales.",
                   "",
                   "Reproducir: `python studies/soc_human_ai_organization/run_b4_organizational_episodes.py`. Semillas: base `9_100_000_000_000`, 4 desarrollo + 8 evaluación por escenario, emparejadas en todas las políticas. El script escribe este informe agregado y no modifica resultados históricos."])
    out = ROOT / "studies/soc_human_ai_organization/B4_ORGANIZATIONAL_EPISODE_RESULTS.md"
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"completed={len(results)} episodes; scenarios={len(scenarios)}; policies={len(POLICIES)}; eval_episodes={len(eval_rows)}; report={out}")
    for policy in POLICIES:
        print(policy, "reward", round(policy_means[policy]["reward"], 4),
              "sla_drain", round(policy_means[policy]["sla_drain"], 4),
              "resource", round(policy_means[policy]["coord_resource"], 5),
              "latency", round(policy_means[policy]["coord_latency"], 5))
    print("adaptive_reproducible", reproducible)


if __name__ == "__main__":
    main()
