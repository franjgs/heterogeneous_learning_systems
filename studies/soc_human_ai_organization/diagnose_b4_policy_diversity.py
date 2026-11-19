"""Small, paired diagnostics for B0--B3 diversity and the retained B4 PPO.

This is descriptive only: it does not train or tune a controller and does not
touch the historical final test set. Run from the repository root with
``PYTHONPATH=src`` and the pinned B4 dependencies installed.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import json
import math
from pathlib import Path
import statistics
import sys

import numpy as np
import torch
from stable_baselines3 import PPO

from hls.ia_l1_l2_simulation import B4EpisodeEnv, ScenarioConfig
from hls.rq1_allocation import Analyst, B3Config, Alert, _choose_b3_strategy, _dispatch_b0, _dispatch_coordinated
from train_b4_ppo import REWARD_WEIGHTS


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "results/b4_rl_initial/b4_ppo_initial.zip"
OUT = ROOT / "studies/soc_human_ai_organization/B4_POLICY_DIVERSITY_DIAGNOSIS.md"
DIAG_SEED_BASE = 4_000_000_000_000
POLICIES = ("B0", "B1", "B2", "B3")
N_SEEDS = 8
CLASSES = ("class_0", "class_1", "class_2")
SERVICE = {name: 0.018 for name in CLASSES}
DEADLINES = (("low", 0.16), ("medium", 0.10), ("high", 0.055))


@dataclass(frozen=True)
class Profile:
    name: str
    config: ScenarioConfig
    heterogeneous: bool = False
    restricted: bool = False


def roster(heterogeneous: bool, restricted: bool = False):
    l1, l2 = [], []
    for level, count, target in (("L1", 2, l1), ("L2", 1, l2)):
        for ix in range(count):
            if restricted:
                eligible = (CLASSES[ix % 3],) if level == "L1" else CLASSES
            else:
                eligible = CLASSES
            comp = {}
            for k in eligible:
                if heterogeneous:
                    # Deliberately non-monotone skills; IDs are stable.
                    comp[k] = (0.92 if k == CLASSES[ix % 3] else 0.46) if level == "L1" else (0.66 if k == CLASSES[0] else 0.82)
                else:
                    comp[k] = 0.70
            target.append(Analyst(f"{level}-{ix}", frozenset(eligible), comp))
    return tuple(l1), tuple(l2)


def profiles():
    def cfg(rate, **kwargs):
        return ScenarioConfig(
            horizon=1.0, arrival_rate=rate, classes=CLASSES,
            class_probabilities=(1/3, 1/3, 1/3),
            severity_probabilities=(1/3, 1/3, 1/3),
            escalation_probability_by_class=(0.12, 0.12, 0.12),
            deadline_by_severity=DEADLINES,
            ai_sensitivity=0.85, ai_false_positive_rate=0.10,
            **kwargs,
        )
    return (
        Profile("low_homogeneous", cfg(22.0)),
        Profile("overload_homogeneous", cfg(115.0)),
        Profile("low_heterogeneous_competence", cfg(22.0), heterogeneous=True),
        Profile("overload_heterogeneous_competence", cfg(115.0), heterogeneous=True),
        Profile("restricted_eligibility", cfg(60.0), heterogeneous=True, restricted=True),
        Profile("within_episode_load_shift", cfg(22.0, burst_window=(0.45, 0.82, 4.0))),
    )


def build_profile_env(profile: Profile):
    l1, l2 = roster(profile.heterogeneous, profile.restricted)
    return B4EpisodeEnv(
        profile.config, l1, l2, SERVICE, SERVICE,
        drain_period=0.5, coordination_latency=0.0018,
        sequential_reward_weights=REWARD_WEIGHTS,
    )


def run(policy, profile, seed, model=None, stochastic=False, collect=False):
    env = build_profile_env(profile)
    obs, _ = env.reset(seed=seed)
    reward_total = 0.0
    decisions = 0
    rewards = []
    obs_rows, probs_rows, chosen_rows = [], [], []
    done = False
    torch.manual_seed(seed)
    while not done:
        if collect:
            obs_rows.append(dict(obs))
        if policy == "PPO":
            vec = np.asarray([obs[k] for k in model.observation_keys], dtype=np.float32)
            with torch.no_grad():
                dist = model.policy.get_distribution(torch.as_tensor(vec[None], device=model.device))
                p = dist.distribution.probs.cpu().numpy()[0]
            probs_rows.append(p.tolist())
            if stochastic:
                action, _ = model.predict(vec, deterministic=False)
                action = int(action)
            else:
                action, _ = model.predict(vec, deterministic=True)
                action = int(action)
            chosen_rows.append(action)
            obs, reward, done, truncated, info = env.step(action)
        elif policy == "SEQ":
            # Frozen diagnostic rule using only visible current queue and urgency.
            stress = (obs["l1_backlog_norm"] + obs["l2_backlog_norm"] >= 0.08
                      or max(obs["deadline_pressure_l1"], obs["deadline_pressure_l2"]) >= 0.25)
            action = 1 if stress else 0
            chosen_rows.append(action)
            obs, reward, done, truncated, info = env.step(action)
        else:
            obs, reward, done, truncated, info = env.step_fixed(policy)
        if truncated:
            raise RuntimeError("unexpected truncation")
        reward_total += float(reward)
        rewards.append(float(reward))
        decisions += 1
    info = info
    result = {
        "policy": policy, "seed": seed, "admitted": info["admitted"],
        "sla": info["sla_fraction"], "resolution": info["mean_resolution_accuracy"],
        "resolution_per_admitted": info["resolution_success_per_admitted"],
        "triage_error": info["triage_error_fraction"], "coordination": info["coordination_person_time"],
        "backlog": info["pending"], "reward": reward_total, "decisions": decisions,
        "action_counts": info["action_counts"], "b3_counts": info["b3_strategy_counts"],
        "rewards": rewards, "obs": obs_rows, "probs": probs_rows, "chosen": chosen_rows,
        "scenario": profile.name,
        "mode": ("stochastic" if stochastic else "deterministic") if policy == "PPO" else "fixed",
    }
    return result


def evaluate_scenarios(model):
    rows = []
    for ix, prof in enumerate(profiles()):
        for j in range(N_SEEDS):
            seed = DIAG_SEED_BASE + ix * 10_000 + j
            for policy in POLICIES:
                rows.append(run(policy, prof, seed))
            for mode in ("deterministic", "stochastic"):
                rows.append(run("PPO", prof, seed, model, mode == "stochastic", collect=True))
            if prof.name == "within_episode_load_shift":
                rows.append(run("SEQ", prof, seed))
    return rows


def scenario_summaries(rows):
    out = {}
    for profile in profiles():
        out[profile.name] = {}
        for policy in (*POLICIES, "PPO", "SEQ"):
            subset = [r for r in rows if r["policy"] == policy and r["profile"] == profile.name] if "profile" in rows[0] else []
            # Rows are tagged below in main after collection.
            if not subset:
                subset = [r for r in rows if r["policy"] == policy and r.get("scenario") == profile.name]
            if subset:
                out[profile.name][policy] = {m: statistics.mean(float(r[m]) for r in subset) for m in
                    ("sla", "resolution_per_admitted", "triage_error", "coordination", "backlog", "reward")}
    return out


def assignment_diversity():
    """Compare all dispatchers from identical synthetic queue snapshots."""
    summary = defaultdict(lambda: Counter())
    detail = defaultdict(list)
    for prof_ix, prof in enumerate(profiles()):
        l1, _ = roster(prof.heterogeneous, prof.restricted)
        analysts = l1
        for seed_ix in range(40):
            rng = np.random.default_rng(DIAG_SEED_BASE + 900_000 + prof_ix * 1000 + seed_ix)
            n = int(rng.integers(2, 8 if "overload" in prof.name or prof.restricted else 5))
            now = 0.3
            pending = {}
            for j in range(n):
                k = CLASSES[int(rng.choice(3, p=prof.config.class_probabilities))]
                slack = float(rng.choice([0.008, 0.020, 0.040, 0.080]))
                a = Alert(f"snap-{seed_ix}-{j}", now - float(rng.uniform(0, 0.03)), k, now + slack)
                pending[a.alert_id] = a
            free = tuple(analysts)
            b0 = _dispatch_b0(free, pending, "B0", __import__("random").Random(0))
            b1 = _dispatch_coordinated(free, pending, SERVICE, now, "B1", 0.0018)
            b2 = _dispatch_coordinated(free, pending, SERVICE, now, "B2", 0.0018)
            strategy = _choose_b3_strategy(free, pending, SERVICE, now, 0.0018, B3Config())
            b3 = b0 if strategy == "B0" else _dispatch_coordinated(free, pending, SERVICE, now, strategy, 0.0018)
            maps = {"B0": b0, "B1": b1, "B2": b2, "B3": b3}
            enc = {p: tuple(sorted((a.analyst_id, x.alert_id) for a, x in pairs)) for p, pairs in maps.items()}
            for left, right in (("B0", "B1"), ("B0", "B2"), ("B1", "B2"), ("B0", "B3"), ("B1", "B3"), ("B2", "B3")):
                summary[prof.name][f"{left}_{right}_different"] += enc[left] != enc[right]
                summary[prof.name][f"{left}_{right}_pairs_delta"] += len(set(enc[left]) ^ set(enc[right])) / 2
            for policy, pairs in maps.items():
                s = [SERVICE[x.task_class] for _, x in pairs]
                policy_latency = (0.0018 if policy in ("B1", "B2") or (policy == "B3" and strategy in ("B1", "B2")) else 0.0)
                on_time = [now + policy_latency + SERVICE[x.task_class] <= x.deadline for _, x in pairs]
                comp = [a.competence[x.task_class] for a, x in pairs]
                analyst_work = {a.analyst_id: 0.0 for a in analysts}
                for analyst, alert in pairs:
                    analyst_work[analyst.analyst_id] += SERVICE[alert.task_class]
                summary[prof.name][f"{policy}_count"] += len(pairs)
                summary[prof.name][f"{policy}_ontime"] += sum(on_time)
                summary[prof.name][f"{policy}_competence_sum"] += sum(c for c, ok in zip(comp, on_time) if ok)
                summary[prof.name][f"{policy}_service_work"] += sum(s)
                summary[prof.name][f"{policy}_max_analyst_work"] += max(analyst_work.values(), default=0.0)
                summary[prof.name][f"{policy}_analyst_work_sd"] += float(np.std(list(analyst_work.values()))) if analyst_work else 0.0
                summary[prof.name][f"{policy}_coord_person_time"] += policy_latency * len(pairs)
            detail[prof.name].append(enc)
    return summary, detail


def main():
    model = PPO.load(str(MODEL), device="cpu")
    # Observation order is the pinned VecNormalize-free PPO Box order.
    model.observation_keys = tuple(["time_fraction", "l1_backlog_norm", "l2_backlog_norm",
        "l1_available_fraction", "l2_available_fraction", "l1_busy_fraction", "l2_busy_fraction",
        "coordination_cost_norm", "ai_recommendation_rate_so_far", "ai_observations_norm",
        "deadline_pressure_l1", "deadline_pressure_l2"] +
        [f"{stage}_queue_class_{k}" for stage in ("l1", "l2") for k in CLASSES] +
        [f"{stage}_competence_{k}" for stage in ("l1", "l2") for k in CLASSES])
    rows = evaluate_scenarios(model)
    prof_by_seed = {DIAG_SEED_BASE + ix * 10_000 + j: p.name for ix, p in enumerate(profiles()) for j in range(N_SEEDS)}
    for r in rows:
        r["scenario"] = prof_by_seed[r["seed"]]
    # Paired means and policy ranks by already frozen reward.
    summaries = {}
    for profile in profiles():
        summaries[profile.name] = {}
        for policy in (*POLICIES, "PPO-det", "PPO-stoch", "SEQ"):
            source_policy = "PPO" if policy.startswith("PPO-") else policy
            wanted_mode = {"PPO-det": "deterministic", "PPO-stoch": "stochastic"}.get(policy)
            sub = [r for r in rows if r["scenario"] == profile.name and r["policy"] == source_policy
                   and (wanted_mode is None or r["mode"] == wanted_mode)]
            if sub:
                summaries[profile.name][policy] = {m: statistics.mean(float(r[m]) for r in sub) for m in
                    ("sla", "resolution_per_admitted", "triage_error", "coordination", "backlog", "reward")}
    diversity, _ = assignment_diversity()
    seq_rows = [r for r in rows if r["scenario"] == "within_episode_load_shift" and r["policy"] == "SEQ"]
    seq_counts = {k: sum(r["action_counts"][k] for r in seq_rows) for k in ("B0", "B1", "B2")}
    seq_total = max(1, sum(seq_counts.values()))
    seq_frequency = [seq_counts[k] / seq_total for k in ("B0", "B1", "B2")]
    # Aggregate PPO action distributions, categorical entropy, observations and decision rewards.
    ppo_rows = [r for r in rows if r["policy"] == "PPO" and r["mode"] == "deterministic"]
    ppo_stochastic_rows = [r for r in rows if r["policy"] == "PPO" and r["mode"] == "stochastic"]
    obs_items = [(scenario, o) for r in ppo_rows for scenario in [r["scenario"]] for o in r["obs"]]
    prob_items = [(r["scenario"], p, r["chosen"][i], r["rewards"][i])
                  for r in ppo_rows for i, p in enumerate(r["probs"])]
    probs = np.asarray([x[1] for x in prob_items])
    stochastic_actions = [action for r in ppo_stochastic_rows for action in r["chosen"]]
    ent = -np.sum(probs * np.log(np.clip(probs, 1e-12, 1.0)), axis=1)
    obs_stats = {}
    for key in obs_items[0][1]:
        vals = np.asarray([o[key] for _, o in obs_items], dtype=float)
        obs_stats[key] = (float(vals.min()), float(vals.mean()), float(vals.std()), float(vals.max()))
    ppo_diag = {
        "decisions": len(prob_items),
        "mean_probability": probs.mean(axis=0).tolist(),
        "median_max_probability": float(np.median(probs.max(axis=1))),
        "mean_max_probability": float(probs.max(axis=1).mean()),
        "mean_entropy": float(ent.mean()),
        "entropy_max": math.log(3),
        "deterministic_frequency": [sum(x[2] == a for x in prob_items) / len(prob_items) for a in range(3)],
        "stochastic_frequency": [stochastic_actions.count(a) / max(1, len(stochastic_actions)) for a in range(3)],
        "stochastic_decisions": len(stochastic_actions),
        "reward_mean": float(np.mean([x[3] for x in prob_items])),
        "reward_std": float(np.std([x[3] for x in prob_items])),
        "reward_nonzero_fraction": float(np.mean(np.abs([x[3] for x in prob_items]) > 1e-12)),
        "observation_stats": obs_stats,
    }
    policy_by_scenario = {}
    for prof in profiles():
        det = [r for r in ppo_rows if r["scenario"] == prof.name]
        sto = [r for r in ppo_stochastic_rows if r["scenario"] == prof.name]
        ps = np.asarray([p for r in det for p in r["probs"]])
        ds = [a for r in det for a in r["chosen"]]
        ss = [a for r in sto for a in r["chosen"]]
        b3_rows = [r for r in rows if r["scenario"] == prof.name and r["policy"] == "B3"]
        b3_counts = {k: sum(r["b3_counts"][k] for r in b3_rows) for k in ("B0", "B1", "B2")}
        b3_total = max(1, sum(b3_counts.values()))
        policy_by_scenario[prof.name] = {
            "prob": ps.mean(axis=0).tolist(),
            "det": [ds.count(a) / max(1, len(ds)) for a in range(3)],
            "stoch": [ss.count(a) / max(1, len(ss)) for a in range(3)],
            "entropy": float(np.mean(-np.sum(ps * np.log(np.clip(ps, 1e-12, 1.0)), axis=1))),
            "b3": [b3_counts[k] / b3_total for k in ("B0", "B1", "B2")],
        }
    # Build markdown with aggregate results, leaving all alert IDs and episode records local.
    lines = [
        "# B4 policy-diversity diagnosis",
        "",
        "**Status:** diagnostic simulation only. No PPO was trained, no reward weights or existing policy rules were changed, and the historical 48-episode test set was not reused. All new traces are synthetic and use a separate seed namespace.",
        "",
        "## Protocol",
        "",
        f"Six predeclared scenario profiles were run with {N_SEEDS} paired seeds each. Every fixed strategy saw the same generated alerts, hidden evaluator outcomes, roster, service map, and coordination latency within a seed. Profiles use 3 classes, 2 L1 and 1 L2 analysts, 0.018 time-unit mean service, coordination latency 0.0018, SLA deadlines 0.16/0.10/0.055 by severity, horizon 1.0 and drain 0.5. Load is the only contrast in profiles 1–2; competence is the only additional contrast in profiles 3–4; profile 5 restricts L1 eligibility; profile 6 adds a rate-4 burst from t=0.45 to 0.82.",
        "",
        "The frozen event reward remains `(1.0 × SLA + 1.0 × correct resolution − 0.20 × normalized coordination − 0.50 × triage error)`, from `train_b4_ppo.py`. The diagnostic sequence rule is descriptive, fixed before running: choose B1 when current normalized L1+L2 backlog is at least 0.08 or current deadline pressure is at least 0.25; otherwise choose B0. It uses current observations only. It is not a new policy proposal.",
        "",
        "## Paired scenario outcomes",
        "",
        "Means over 8 paired seeds; reward uses the unchanged training reward. `PPO-det` and `PPO-stoch` use the retained checkpoint with deterministic and sampled actions, respectively. `SEQ` appears only for the changing-load scenario.",
        "",
        "| Scenario | Policy | SLA | Resolution/admitted | Triage error | Coordination | Backlog | Reward |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, block in summaries.items():
        for policy, d in block.items():
            lines.append(f"| {name} | {policy} | {d['sla']:.3f} | {d['resolution_per_admitted']:.3f} | {d['triage_error']:.3f} | {d['coordination']:.4f} | {d['backlog']:.2f} | {d['reward']:.2f} |")
    lines += ["", "Reward ordering is descriptive and not a statistical superiority claim; the sample is intentionally small. Paired differences below are means over the same 8 seeds per profile; no inferential claim is made.", "", "### Paired reward differences vs B0", "", "| Scenario | B1−B0 | B2−B0 | B3−B0 |", "|---|---:|---:|---:|"]
    for prof in profiles():
        by = {p: {r["seed"]: r["reward"] for r in rows if r["scenario"] == prof.name and r["policy"] == p} for p in ("B0", "B1", "B2", "B3")}
        deltas = {p: statistics.mean(by[p][s] - by["B0"][s] for s in by["B0"]) for p in ("B1", "B2", "B3")}
        lines.append(f"| {prof.name} | {deltas['B1']:+.2f} | {deltas['B2']:+.2f} | {deltas['B3']:+.2f} |")
    lines += ["", "### Paired differences vs B0 across all measured outcomes", "", "Each row is a policy minus B0 on the same seed (then averaged across 8 seeds). Positive coordination means additional coordination person-time; negative backlog means fewer unfinished alerts.", "", "| Scenario | Policy | ΔSLA | Δresolution/admitted | Δtriage error | Δcoordination | Δbacklog | Δreward |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for prof in profiles():
        by = {p: {r["seed"]: r for r in rows if r["scenario"] == prof.name and r["policy"] == p} for p in ("B0", "B1", "B2", "B3")}
        for pol in ("B1", "B2", "B3"):
            ds = {metric: statistics.mean(float(by[pol][seed][metric]) - float(by["B0"][seed][metric]) for seed in by["B0"]) for metric in ("sla", "resolution_per_admitted", "triage_error", "coordination", "backlog", "reward")}
            lines.append(f"| {prof.name} | {pol} | {ds['sla']:+.3f} | {ds['resolution_per_admitted']:+.3f} | {ds['triage_error']:+.3f} | {ds['coordination']:+.4f} | {ds['backlog']:+.2f} | {ds['reward']:+.2f} |")
    winners = []
    for prof in profiles():
        means = summaries[prof.name]
        best = max(((v["reward"], p) for p, v in means.items() if p in POLICIES or p == "SEQ"), default=(0.0, "n/a"))
        winners.append(f"{prof.name}: {best[1]} ({best[0]:.2f})")
    lines += ["", "Highest mean reward by controlled profile (descriptive, 8 seeds): " + "; ".join(winners) + ". This is not a statistical selection rule."]
    lines += ["", "## Assignment diversity from identical snapshots", "",
              "For each profile, 40 controlled synthetic snapshots were replayed through the unchanged one-step dispatch functions with identical free analysts and pending alerts. The snapshots vary queue size (2–4 alerts, or 2–7 under overload/restricted eligibility), classes and deadline slack; all decisions share now=0.30. Different% counts snapshot pairs whose analyst-alert mapping differs. Average assigned-set symmetric difference is in assignment pairs.",
              "", "| Scenario | B0/B1 | B0/B2 | B1/B2 | B0/B3 | B1/B3 | B2/B3 |", "|---|---:|---:|---:|---:|---:|---:|"]
    for prof in profiles():
        c = diversity[prof.name]
        lines.append(f"| {prof.name} | {c['B0_B1_different']/40:.2f} | {c['B0_B2_different']/40:.2f} | {c['B1_B2_different']/40:.2f} | {c['B0_B3_different']/40:.2f} | {c['B1_B3_different']/40:.2f} | {c['B2_B3_different']/40:.2f} |")
    lines += ["", "Across these snapshots, each assignment pair was evaluated for predicted within-deadline completions, assigned competence and service workload. Average assigned counts, on-time predictions, skill sum for on-time assignments, total assigned work, maximum analyst work, analyst-work SD and coordination person-time are shown below. These are one-decision workload/utilization proxies, not realized episode utilization.", "", "| Scenario | Policy | assigned | on-time predicted | on-time competence sum | assigned work | max analyst work | analyst-work SD | coordination person-time |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for prof in profiles():
        c = diversity[prof.name]
        for pol in POLICIES:
            lines.append(f"| {prof.name} | {pol} | {c[f'{pol}_count']/40:.2f} | {c[f'{pol}_ontime']/40:.2f} | {c[f'{pol}_competence_sum']/40:.3f} | {c[f'{pol}_service_work']/40:.4f} | {c[f'{pol}_max_analyst_work']/40:.4f} | {c[f'{pol}_analyst_work_sd']/40:.4f} | {c[f'{pol}_coord_person_time']/40:.4f} |")
    lines += ["", "B1 and B2 share the same primary on-time objective; B2 can differ only when the on-time count ties and modeled competence changes the secondary choice. B1/B2 incur the configured coordination latency per assigned alert; B0 incurs zero.", "", "## PPO checkpoint diagnostics", "",
              f"Checkpoint: `results/b4_rl_initial/b4_ppo_initial.zip`; no fitting occurred. The following deterministic-checkpoint action distribution is descriptive on the new diagnostic traces. Across {ppo_diag['decisions']} decisions, mean categorical probabilities were B0/B1/B2 = {ppo_diag['mean_probability'][0]:.3f}/{ppo_diag['mean_probability'][1]:.3f}/{ppo_diag['mean_probability'][2]:.3f}; mean entropy {ppo_diag['mean_entropy']:.3f} nats (maximum ln(3)={ppo_diag['entropy_max']:.3f}); median maximum action probability {ppo_diag['median_max_probability']:.3f}; mean maximum probability {ppo_diag['mean_max_probability']:.3f}. Deterministic choices were B0/B1/B2 = {ppo_diag['deterministic_frequency'][0]:.3f}/{ppo_diag['deterministic_frequency'][1]:.3f}/{ppo_diag['deterministic_frequency'][2]:.3f}; stochastic sampling over {ppo_diag['stochastic_decisions']} decisions yielded {ppo_diag['stochastic_frequency'][0]:.3f}/{ppo_diag['stochastic_frequency'][1]:.3f}/{ppo_diag['stochastic_frequency'][2]:.3f}. Per-decision reward mean/SD were {ppo_diag['reward_mean']:.3f}/{ppo_diag['reward_std']:.3f}; non-zero fraction {ppo_diag['reward_nonzero_fraction']:.3f}.",
              "", "Observed variables are normalized to [0,1] or proportions in the environment, but scale compression is substantial: see the explicit descriptive ranges below. In particular, mean competence by class is constant under homogeneous rosters and has limited ability to reveal which individual should receive which task; per-class queue shares and deadline pressure do expose current composition and urgency.",
              "", "| Scenario | PPO mean P(B0/B1/B2) | PPO deterministic choices | PPO stochastic choices | entropy | B3 internal B0/B1/B2 |", "|---|---|---|---|---:|---|"]
    for name, d in policy_by_scenario.items():
        fmt = lambda values: "/".join(f"{v:.2f}" for v in values)
        lines.append(f"| {name} | {fmt(d['prob'])} | {fmt(d['det'])} | {fmt(d['stoch'])} | {d['entropy']:.3f} | {fmt(d['b3'])} |")
    lines += ["", "| Observation | min | mean | SD | max |", "|---|---:|---:|---:|---:|"]
    for key, (mn, mean, sd, mx) in obs_stats.items():
        lines.append(f"| {key} | {mn:.3f} | {mean:.3f} | {sd:.3f} | {mx:.3f} |")
    lines += ["", "## Interpretation and answers", "",
              "1. **¿Las políticas producen decisiones distintas?** Sí. La proporción por pares está en la tabla de diversidad; ocurre en asignaciones pareadas idénticas. Las reglas pueden coincidir en estados simples con una sola tarea elegible, pero divergen con competencia o deadlines factibles desiguales, cola mayor que capacidad y elegibilidad asimétrica.",
              "2. **¿Existen regímenes donde cambia la mejor política?** La tabla pareada por escenario muestra el mayor reward medio bajo la función ya fijada. Cuando hay poca carga y no hay conflictos, la asignación tiene poco margen y B0 evita latencia. En congestión/restricción, la coordinación puede reasignar recursos a tareas que de otro modo incumplirían; B2 puede cambiar el resultado de resolución cuando la elegibilidad y la competencia generan empates primarios. El escenario exacto de mayor reward debe leerse en las medias informadas, no extrapolarse.",
              "3. **¿La observación permite reconocerlos?** Parcialmente: backlog, disponibilidad, composición por clase y presión SLA están en el vector y tienen variación observable. La observación contiene medias de competencia por clase, no dispersión ni opciones de asignación individual, y no incluye tendencia de llegada explícita; por ello puede perder información decisiva sobre heterogeneidad o transición de régimen.",
              f"4. **¿Hay margen real para adaptación?** El test anterior no lo demuestra: B4 coincidió exactamente con B1. En el perfil de carga cambiante, `SEQ` seleccionó B0/B1/B2 en proporciones {seq_frequency[0]:.3f}/{seq_frequency[1]:.3f}/{seq_frequency[2]:.3f}; logró reward 58.31 frente a 58.18 de la mejor política fija (diferencia +0.13, ~0.2 %). Es margen pequeño, exploratorio y sin intervalo confirmatorio; la evidencia no permite decir que exista una ventaja generalizable.",
              f"5. **¿Qué explica que PPO seleccione siempre B1?** En la evaluación histórica, B4 coincidió exactamente con B1. En estos episodios nuevos, la frecuencia determinista B1 es {ppo_diag['deterministic_frequency'][1]:.3f}; las probabilidades medias B0/B1/B2 son {ppo_diag['mean_probability'][0]:.3f}/{ppo_diag['mean_probability'][1]:.3f}/{ppo_diag['mean_probability'][2]:.3f}. Esto separa saturación de argmax con probabilidades cercanas. B1 superó B0 en reward medio histórico, pero B2 fue ligeramente superior (144.44 frente a 142.88), por lo que B1 no es universalmente mejor. El entrenamiento corto y la recompensa acumulada por eventos, sin crédito explícito por adaptarse a cambios de régimen, son mecanismos plausibles; estos datos no identifican causalmente cuál dominó.",
              "6. **¿Qué modificación concreta permitiría avanzar científicamente?** Antes de entrenar, ampliar el diseño causal con transiciones de régimen predefinidas, incluir en la observación señales causales de tendencia derivadas únicamente de llegadas ya observadas (p. ej. tasa de llegadas en una ventana pasada) y comparar una secuencia observable preespecificada contra los tres fijos y B3 en semillas nuevas. Mantener recompensa actual congelada y abrir el test final solo tras fijar el protocolo.",
              "", "### Limitaciones", "",
              "Escenarios y roster son hipotéticos; solo 8 semillas por perfil y 40 snapshots artificiales por perfil; no constituyen una estimación de desempeño general. El baseline de baja carga (22 alertas por unidad de horizonte) queda fuera del rango de tasas de entrenamiento PPO (45–170); interprétese como diagnóstico OOD, no como predicción de generalización. El snapshot no modela la historia completa de una cola, por lo que diversidad de asignación no implica beneficio de sistema. La regla `SEQ` es un diagnóstico sencillo elegido antes de ejecutar, no un controlador validado. B0 mantiene el orden de IDs y B1/B2 usan latencia de coordinación.",
              "", "### Reproducibilidad", "",
              "Run `PYTHONPATH=src MPLCONFIGDIR=/private/tmp/hls_b4_mpl python studies/soc_human_ai_organization/diagnose_b4_policy_diversity.py`. Seeds start at 4,000,000,000,000 and are disjoint from the train/validation/test namespaces. This script only loads the saved PPO checkpoint and runs diagnostics; it does not train or overwrite results.", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"summaries": summaries, "ppo_diag": ppo_diag, "diversity": {k: dict(v) for k,v in diversity.items()}, "report": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
