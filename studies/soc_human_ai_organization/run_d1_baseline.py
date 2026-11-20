"""Small paired comparison of decentralized human-informed D1."""
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
from map_b4_coordination_value import _with_roster  # noqa: E402
from hls.ia_l1_l2_simulation import B4EpisodeEnv  # noqa: E402

POLICIES = ("D1", "B0", "C0P1")
SEEDS = (71031, 71032, 71033, 71034, 71035, 71036)
T95_DF5 = 2.571


def scenarios():
    low = _make_scenario("stationary_low")
    near = _make_scenario("near_capacity")
    restricted = _make_scenario("eligibility_restricted")
    restricted = _with_roster(restricted, "eligibility_restricted",
                               competence_hetero=True, speed_hetero=False,
                               restricted=True)
    return (low, near, restricted)


def run_one(scenario, seed, policy):
    env = B4EpisodeEnv(
        scenario.config, scenario.l1, scenario.l2, L1_SERVICE, L2_SERVICE,
        drain_period=DRAIN,
        sequential_reward_weights=REWARD_WEIGHTS,
        l1_service_by_analyst_class=scenario.l1_services,
        l2_service_by_analyst_class=scenario.l2_services,
        l1_roster_schedule=scenario.l1_schedule,
        l2_roster_schedule=scenario.l2_schedule,
        diagnostic_d1=(policy == "D1"),
    )
    env.reset(seed=seed)
    reward = 0.0
    while True:
        if policy == "C0P1":
            _, step_reward, terminated, truncated, info = env.step_fixed_organization(policy)
        else:
            _, step_reward, terminated, truncated, info = env.step_fixed(policy)
        if truncated:
            raise AssertionError("unexpected truncation")
        reward += float(step_reward)
        if terminated:
            break
    n = info["admitted"]
    return {
        "scenario": scenario.name, "seed": seed, "policy": policy,
        "reward": reward, "sla": info["sla_fraction"],
        "quality": info["resolution_success_per_admitted"],
        "backlog": info["pending"], "l1_backlog": info["l1_backlog"],
        "l2_backlog": info["l2_backlog"], "admitted": n,
        "decisions": tuple(env._l1.d1_decisions) + tuple(env._l2.d1_decisions),
        "snapshots": tuple(env._l1.d1_dispatch_snapshots) + tuple(env._l2.d1_dispatch_snapshots),
        "assignments": tuple(env._l1.assignments) + tuple(env._l2.assignments),
        "resolution_correct": dict(env._resolution_correct),
        "alerts": dict(env._all_alerts),
        "evaluation": dict(env._evaluation),
        "coord_resource": info["coordination_resource"],
        "coord_latency": info["coordination_latency_total"],
    }


def paired_ci(values):
    mean = statistics.mean(values)
    half = T95_DF5 * statistics.stdev(values) / math.sqrt(len(values))
    return mean, mean - half, mean + half


def main():
    rows = {}
    for scenario in scenarios():
        for seed in SEEDS:
            for policy in POLICIES:
                rows[(scenario.name, seed, policy)] = run_one(scenario, seed, policy)

    report = [
        "# Baseline descentralizado informado por conocimiento humano (D1)", "",
        "## Protocolo",
        "D1 se comparó con B0 y C0P1 en tres escenarios sintéticos (carga baja, próxima a capacidad y elegibilidad restringida con competencias heterogéneas), seis semillas emparejadas y 54 episodios. Las llegadas y demás aleatoriedad se regeneraron con la misma semilla dentro de cada tripleta. Pesos de recompensa congelados de la configuración B4 existente; sin coste ni latencia de coordinación. IC95% t pareados bilaterales, df=5 (t=2.571). No se ajustó la regla con estas semillas.", "",
        "## Regla implementada",
        "En cada época, se barajan reproduciblemente los analistas libres y deciden uno por uno. Para cada alerta elegible, el analista estima riesgo de incumplir SLA como `clip((s_ik - (d_k - t))/s_ik, 0, 1)`, usando su duración propia `s_ik`. Elige lexicográficamente: mayor riesgo; mayor competencia propia; menor número de compañeros libres que son elegibles para esa clase; deadline, llegada e ID en orden ascendente. El conocimiento de compañeros es solo su conjunto general de clases elegibles; nunca se consulta su competencia exacta. La alerta se retira inmediatamente y siempre se selecciona una si queda alguna elegible, sin reserva ni coordinación conjunta.", "",
        "## Resultados agregados",
        "Recompensa es la suma del simulador, reportada por episodio; diferencia e IC usan pares de la misma semilla.",
        "| Escenario | Política | Recompensa media | SLA medio | Calidad/alerta | Backlog medio | Δ recompensa vs B0 [IC95%] | Δ recompensa vs C0P1 [IC95%] |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario in scenarios():
        means = {}
        for policy in POLICIES:
            vals = [rows[(scenario.name, seed, policy)] for seed in SEEDS]
            means[policy] = {key: statistics.mean(r[key] for r in vals)
                             for key in ("reward", "sla", "quality", "backlog")}
        for policy in POLICIES:
            deltas = {}
            for control in ("B0", "C0P1"):
                diffs = [rows[(scenario.name, seed, policy)]["reward"]
                         - rows[(scenario.name, seed, control)]["reward"] for seed in SEEDS]
                m, lo, hi = paired_ci(diffs)
                deltas[control] = f"{m:+.2f} [{lo:+.2f}, {hi:+.2f}]"
            report.append(f"| {scenario.name} | {policy} | {means[policy]['reward']:.2f} | {means[policy]['sla']:.3f} | {means[policy]['quality']:.3f} | {means[policy]['backlog']:.2f} | {deltas['B0']} | {deltas['C0P1']} |")

    example = rows[("eligibility_restricted", SEEDS[0], "D1")]
    report.extend(["", "## Registro ilustrativo de decisiones D1", "",
                   "Filas iniciales de una misma realización; los IDs son sintéticos. `riesgo` es la estimación local antes de iniciar el servicio.",
                   "| Tiempo | Analista | Alerta | Riesgo SLA | Competencia propia | Compañeros elegibles |",
                   "|---:|---|---|---:|---:|---:|"])
    for d in example["decisions"][:12]:
        report.append(f"| {d.time:.3f} | {d.analyst_id} | {d.alert_id} | {d.deadline_risk:.3f} | {d.own_competence:.3f} | {d.eligible_peers} |")
    report.extend(["", "## Diferencias y limitaciones", "",
                   "B0 realiza selección local EDF sin considerar duración ni competencia. C0P1 realiza asignación local equilibrada con sus reglas existentes, sin el perfil de especialidades de compañeros. D1 no calcula matching conjunto: el orden aleatorio reproducible decide quién elige primero y cada elección elimina inmediatamente la alerta. La política es una idealización de autonomía informada; elegibilidad se usa como proxy público de especialidad y no se ha medido que los SOC compartan ese mapa con esta precisión. Seis semillas dan intervalos amplios; resultados pequeños o con IC que cruza cero no son evidencia de superioridad.",
                   "", "## Pruebas", "",
                   "Incluye escenarios de competencias cruzadas, deadlines y duraciones distintas, conocimiento parcial de elegibilidad, simultaneidad reproducible, elegibilidad restringida y drenaje finito sin starvation. Reproducir la comparación: `python studies/soc_human_ai_organization/run_d1_baseline.py`."])
    out = ROOT / "docs/experimental_foundations/SOC_HUMAN_BASELINE_D1.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    for s in scenarios():
        for policy in POLICIES:
            values = [rows[(s.name, seed, policy)] for seed in SEEDS]
            print(s.name, policy, f"reward={statistics.mean(x['reward'] for x in values):.3f}",
                  f"sla={statistics.mean(x['sla'] for x in values):.3f}",
                  f"quality={statistics.mean(x['quality'] for x in values):.3f}",
                  f"backlog={statistics.mean(x['backlog'] for x in values):.3f}")


if __name__ == "__main__":
    main()
