"""Train and evaluate one PPO for observable within-episode regime adaptation.

The old B0--B3 policies and reward weights are reused unchanged. The final
suite is paired across policies and uses a seed namespace never used by the
initial PPO or the policy-diversity diagnosis.
"""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import time

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/hls_b4_mpl")

import gymnasium
import numpy as np
import stable_baselines3
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor

from hls.b4_gymnasium import B4GymnasiumAdapter
from hls.ia_l1_l2_simulation import B4EpisodeEnv, ScenarioConfig
from hls.rq1_allocation import Analyst
from train_b4_ppo import CLASSES, REWARD_WEIGHTS


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/b4_regime_adaptation"
REPORT = ROOT / "studies/soc_human_ai_organization/B4_REGIME_ADAPTATION_RESULTS.md"
TRAIN_OFFSET, VALID_OFFSET, FINAL_OFFSET = 6_000_000_000_000, 7_000_000_000_000, 8_000_000_000_000
MASTER_SEED = 20261120
TIMESTEPS = 65_536
FINAL_REPLICATES = 20
VALIDATION_REPLICATES = 6
CHANGE_TIME = 0.50
SERVICE = {key: 0.022 for key in CLASSES}
COORDINATION_LATENCY = 0.0022
POLICIES = ("B0", "B1", "B2", "B3", "SEQ", "B4-PPO")
FAMILY_FOR_KIND = {
    "stationary_low": "stationary", "stationary_medium": "stationary",
    "stationary_high": "stationary", "stationary_heterogeneous": "stationary",
    "load_low_to_high": "regime", "load_high_to_low": "regime",
    "competence_hom_to_het": "regime", "competence_het_to_hom": "regime",
    "class_mix_shift": "regime",
    "ood_stationary_low": "ood", "ood_stationary_high": "ood",
    "ood_load_low_to_high": "ood", "ood_load_high_to_low": "ood",
}


@dataclass(frozen=True)
class ScenarioSpec:
    seed: int
    kind: str
    family: str
    config: ScenarioConfig
    l1: tuple[Analyst, ...]
    l2: tuple[Analyst, ...]
    l1_schedule: tuple[tuple[float, tuple[str, ...]], ...]
    l2_schedule: tuple[tuple[float, tuple[str, ...]], ...]
    change_time: float | None


def _analysts(level: str, first_mode: str, second_mode: str | None = None):
    result = []
    for team in (0, 1):
        mode = first_mode if team == 0 else (second_mode or first_mode)
        for member in range(2):
            if mode == "homogeneous":
                competence = {key: 0.70 for key in CLASSES}
            else:
                profiles = (
                    (0.94, 0.58, 0.42),
                    (0.48, 0.91, 0.62),
                )
                competence = dict(zip(CLASSES, profiles[member]))
                if level == "L2":
                    competence = {key: min(0.99, value + 0.04) for key, value in competence.items()}
            result.append(Analyst(f"{level}-team{team}-{member}", frozenset(CLASSES), competence))
    return tuple(result)


def _team_ids(level: str, team: int):
    return tuple(f"{level}-team{team}-{member}" for member in range(2))


def make_scenario(seed: int, *, training: bool = False, kind: str | None = None) -> ScenarioSpec:
    rng = np.random.default_rng(seed)
    kinds = tuple(FAMILY_FOR_KIND)
    if training:
        choices = ("stationary_low", "stationary_medium", "stationary_high", "stationary_heterogeneous",
                   "load_low_to_high", "load_high_to_low",
                   "competence_hom_to_het", "competence_het_to_hom", "class_mix_shift")
        kind = choices[int(rng.integers(0, len(choices)))]
    if kind is None:
        raise ValueError("an evaluation scenario kind is required")
    family = FAMILY_FOR_KIND[kind]
    change_time = float(rng.uniform(0.38, 0.62)) if kind in {
        "load_low_to_high", "load_high_to_low", "competence_hom_to_het",
        "competence_het_to_hom", "class_mix_shift", "ood_load_low_to_high", "ood_load_high_to_low"
    } else None
    low_rate = float(rng.uniform(38.0, 58.0)) if training else 48.0
    high_rate = float(rng.uniform(135.0, 168.0)) if training else 150.0
    initial_rate = float(rng.uniform(40.0, 170.0)) if training else 90.0
    after_rate = None
    if kind in ("load_low_to_high", "ood_load_low_to_high"):
        initial_rate, after_rate = ((low_rate, high_rate) if not kind.startswith("ood") else (22.0, 190.0))
    elif kind in ("load_high_to_low", "ood_load_high_to_low"):
        initial_rate, after_rate = ((high_rate, low_rate) if not kind.startswith("ood") else (190.0, 22.0))
    elif kind == "stationary_low":
        initial_rate = 48.0
    elif kind == "stationary_medium":
        initial_rate = 95.0
    elif kind == "stationary_high":
        initial_rate = 150.0
    elif kind == "stationary_heterogeneous":
        initial_rate = 105.0
    elif kind == "ood_stationary_low":
        initial_rate = 22.0
    elif kind == "ood_stationary_high":
        initial_rate = 190.0

    base_mix = (0.34, 0.33, 0.33)
    shifted_mix = None
    if kind == "class_mix_shift":
        base_mix, shifted_mix = (0.78, 0.12, 0.10), (0.10, 0.12, 0.78)
    elif training and rng.random() < 0.35:
        base_mix = tuple(float(x) for x in rng.dirichlet(np.array([1.4, 1.4, 1.4])))
    comp_mode = "heterogeneous" if kind == "stationary_heterogeneous" else "homogeneous"
    first_mode, second_mode = comp_mode, None
    l1_schedule: tuple[tuple[float, tuple[str, ...]], ...] = ()
    l2_schedule: tuple[tuple[float, tuple[str, ...]], ...] = ()
    if kind == "competence_hom_to_het":
        first_mode, second_mode = "homogeneous", "heterogeneous"
    elif kind == "competence_het_to_hom":
        first_mode, second_mode = "heterogeneous", "homogeneous"
    l1 = _analysts("L1", first_mode, second_mode)
    l2 = _analysts("L2", first_mode, second_mode)
    if second_mode is not None:
        l1_schedule = ((0.0, _team_ids("L1", 0)), (change_time, _team_ids("L1", 1)))
        l2_schedule = ((0.0, _team_ids("L2", 0)), (change_time, _team_ids("L2", 1)))

    config = ScenarioConfig(
        horizon=1.0, arrival_rate=initial_rate,
        arrival_rate_shift_after=change_time if after_rate is not None else None,
        arrival_rate_after=after_rate,
        classes=CLASSES, class_probabilities=base_mix,
        shift_after=change_time if shifted_mix is not None else None,
        shift_class_probabilities=shifted_mix,
        severity_probabilities=(0.34, 0.33, 0.33),
        escalation_probability_by_class=(0.12, 0.18, 0.24),
        deadline_by_severity=(("low", 0.16), ("medium", 0.10), ("high", 0.055)),
        ai_sensitivity=0.84, ai_false_positive_rate=0.11,
    )
    return ScenarioSpec(seed, kind, family, config, l1, l2, l1_schedule, l2_schedule, change_time)


def build_env(spec: ScenarioSpec) -> B4EpisodeEnv:
    env = B4EpisodeEnv(
        spec.config, spec.l1, spec.l2, SERVICE, SERVICE,
        drain_period=0.50, coordination_latency=COORDINATION_LATENCY,
        sequential_reward_weights=REWARD_WEIGHTS,
        l1_roster_schedule=spec.l1_schedule, l2_roster_schedule=spec.l2_schedule,
    )
    env.scenario_seed = spec.seed
    return env


def training_factory(factory_seed: int) -> B4EpisodeEnv:
    return build_env(make_scenario(TRAIN_OFFSET + int(factory_seed % 1_000_000_000), training=True))


class TrainingCallback(BaseCallback):
    def __init__(self):
        super().__init__()
        self.episodes: list[dict[str, object]] = []

    def _on_step(self) -> bool:
        for done, info in zip(self.locals["dones"], self.locals["infos"]):
            if done and "episode" in info:
                self.episodes.append({"timesteps": self.num_timesteps,
                                      "episode_reward": float(info["episode"]["r"]),
                                      "episode_length": int(info["episode"]["l"]),
                                      "scenario_seed": info.get("scenario_seed"),
                                      "trace_seed": info.get("trace_seed")})
        return True


def _obs_keys():
    return B4GymnasiumAdapter(lambda _seed: None, CLASSES).observation_keys


def _sequence_action(obs):
    stress = (obs["l1_backlog_norm"] + obs["l2_backlog_norm"] >= 0.08
              or max(obs["deadline_pressure_l1"], obs["deadline_pressure_l2"]) >= 0.25)
    return "B1" if stress else "B0"


def evaluate(model: PPO | None, spec: ScenarioSpec, policy: str) -> dict[str, object]:
    env = build_env(spec)
    obs, _ = env.reset(seed=spec.seed)
    total_reward = 0.0
    decision_actions: list[tuple[float, str]] = []
    rewards = []
    done = False
    final_info: dict[str, object] = {}
    torch.manual_seed(spec.seed)
    keys = _obs_keys()
    strategy_actions: list[tuple[float, str]] = []
    while not done:
        decision_time = float(obs["time_fraction"])
        old_l1_history = len(env._l1.strategy_history)
        old_l2_history = len(env._l2.strategy_history)
        if policy == "B4-PPO":
            vec = np.asarray([obs[k] for k in keys], dtype=np.float32)
            action, _ = model.predict(vec, deterministic=True)
            selected = ("B0", "B1", "B2")[int(action)]
            obs, reward, done, truncated, final_info = env.step(int(action))
        elif policy == "SEQ":
            selected = _sequence_action(obs)
            obs, reward, done, truncated, final_info = env.step_fixed(selected)
        else:
            selected = policy
            obs, reward, done, truncated, final_info = env.step_fixed(selected)
        if truncated:
            raise RuntimeError("event-driven simulator unexpectedly truncated an episode")
        if policy == "B3":
            for strategy in env._l1.strategy_history[old_l1_history:]:
                strategy_actions.append((decision_time, strategy))
            for strategy in env._l2.strategy_history[old_l2_history:]:
                strategy_actions.append((decision_time, strategy))
        else:
            strategy_actions.append((decision_time, selected))
        total_reward += float(reward)
        rewards.append(float(reward))
        decision_actions.append((decision_time, selected))
    counts = {key: sum(action == key for _, action in strategy_actions) for key in ("B0", "B1", "B2")}
    total_actions = max(1, sum(counts.values()))
    switches = sum(left[1] != right[1] for left, right in zip(strategy_actions, strategy_actions[1:]))
    internal = {key: int(final_info["b3_strategy_counts"].get(key, 0)) for key in ("B0", "B1", "B2")}
    internal_total = max(1, sum(internal.values()))
    b3_switches = sum(a != b for history in (env._l1.strategy_history, env._l2.strategy_history)
                      for a, b in zip(history, history[1:]))
    pre = [(t, a) for t, a in strategy_actions if spec.change_time is not None and t < spec.change_time]
    post = [(t, a) for t, a in strategy_actions if spec.change_time is not None and t >= spec.change_time]
    row = {
        "scenario_seed": spec.seed, "trace_seed": spec.seed, "scenario": spec.kind,
        "family": spec.family, "change_time": spec.change_time,
        "policy": policy, "admitted": final_info["admitted"],
        "reward": total_reward, "sla": final_info["sla_fraction"],
        "resolution_accuracy": final_info["mean_resolution_accuracy"],
        "resolution_per_admitted": final_info["resolution_success_per_admitted"],
        "triage_error": final_info["triage_error_fraction"],
        "coordination_person_time": final_info["coordination_person_time"],
        "backlog": final_info["pending"], "decisions": len(decision_actions),
        "switches": (b3_switches if policy == "B3" else switches if policy in ("B4-PPO", "SEQ") else 0),
        "frequency_B0": counts["B0"] / total_actions,
        "frequency_B1": counts["B1"] / total_actions,
        "frequency_B2": counts["B2"] / total_actions,
        "b3_frequency_B0": internal["B0"] / internal_total,
        "b3_frequency_B1": internal["B1"] / internal_total,
        "b3_frequency_B2": internal["B2"] / internal_total,
        "pre_decisions": len(pre), "post_decisions": len(post),
    }
    for phase, subset in (("pre", pre), ("post", post)):
        denom = max(1, len(subset))
        for action in ("B0", "B1", "B2"):
            row[f"{phase}_{action}"] = sum(a == action for _, a in subset) / denom
    return row


def _ci(values: np.ndarray, seed: int, n_boot: int = 10_000):
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(values), size=(n_boot, len(values)))
    means = values[draws].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def _write_csv(path: Path, rows: list[dict[str, object]]):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _evaluate_suite(model, *, offset: int, replicates: int):
    kinds = tuple(FAMILY_FOR_KIND)
    rows = []
    specs = []
    for kind_ix, kind in enumerate(kinds):
        for replicate in range(replicates):
            seed = offset + kind_ix * 100_000 + replicate
            spec = make_scenario(seed, kind=kind)
            specs.append(spec)
            for policy in POLICIES:
                rows.append(evaluate(model, spec, policy))
    return specs, rows


def _summarize(rows):
    summary = []
    for family in ("stationary", "regime", "ood"):
        for policy in POLICIES:
            subset = [r for r in rows if r["family"] == family and r["policy"] == policy]
            entry = {"family": family, "policy": policy, "episodes": len(subset)}
            for metric in ("reward", "sla", "resolution_accuracy", "resolution_per_admitted",
                           "triage_error", "coordination_person_time", "backlog", "switches",
                           "frequency_B0", "frequency_B1", "frequency_B2"):
                entry[metric] = statistics.mean(float(r[metric]) for r in subset) if subset else 0.0
            summary.append(entry)
    paired = []
    for family in ("stationary", "regime", "ood"):
        by_policy = {p: {r["scenario_seed"]: float(r["reward"]) for r in rows
                         if r["family"] == family and r["policy"] == p} for p in POLICIES}
        for comparator in ("B0", "B1", "B2", "B3", "SEQ"):
            common = sorted(by_policy["B4-PPO"].keys() & by_policy[comparator].keys())
            differences = np.asarray([by_policy["B4-PPO"][s] - by_policy[comparator][s] for s in common])
            lo, hi = _ci(differences, FINAL_OFFSET + len(paired))
            paired.append({"family": family, "contrast": f"B4-PPO minus {comparator}",
                           "episodes": len(common), "mean_difference": float(differences.mean()),
                           "ci95_low": lo, "ci95_high": hi,
                           "method": "paired percentile bootstrap, 10000 resamples"})
    return summary, paired


def _write_report(path, config, summaries, paired, rows, training_episodes):
    lines = [
        "# B4-RL: adaptation to regime changes",
        "",
        "## Protocolo predeclarado",
        "",
        f"One PPO was trained for {TIMESTEPS:,} steps with the initial PPO architecture and algorithm (2×64 MLP, PPO, four environments, CPU, n_steps=128, batch=128, 5 epochs, lr=3e-4, gamma=.99, GAE=.95, clip=.2, entropy=.01, seed {MASTER_SEED}). The event reward and weights were reused unchanged from the initial PPO: SLA + correct simulated resolution − 0.20 normalized coordination − 0.50 triage error. Training episodes observed: {training_episodes}; elapsed training time: {config['training_seconds']:.2f} s; model SHA-256: `{config['model_sha256']}`.",
        "",
        "The predeclared evaluation rule is episode mean reward under that frozen reward; report a paired 95% interval and claim a benefit only if the interval is wholly above zero. A policy must also change actions in response to observable state and preserve or improve reward; switch frequency alone is not evidence of adaptation.",
        "",
        "Training support: stationary and changing scenarios drawn from rates 38–170 alerts per horizon, with changes after a randomized 0.38–0.62 horizon point; all traces are generated from fixed seeds. Final evaluation uses 20 paired realizations per scenario kind, after model freeze. Validation uses a separate 6 realizations per kind and is descriptive only; it did not select a checkpoint or tune a rule. Final seeds begin at 8,000,000,000,000; training and validation namespaces begin at 6,000,000,000,000 and 7,000,000,000,000.",
        "",
        "Controls: B0, B1, B2 and B3 are unchanged. `SEQ` was frozen before evaluation: select B1 if current normalized L1+L2 pending count ≥0.08 or either current deadline-pressure fraction ≥0.25; otherwise select B0. No future-arrival signal or hidden reference is used.",
        "",
        "## Observations and temporal integrity",
        "",
        "New arrival-rate features count only timestamps already processed at the current event. The two consecutive trailing windows each span 0.15H: previous `(t−0.30H, t−0.15H]`, recent `(t−0.15H, t]`, clipped at time zero. Each count is divided by actual elapsed exposure to obtain a rate, then normalized by fixed `200/H` and clipped to [0,1]. `arrival_rate_trend_norm = 0.5 + 0.5*(recent_rate−previous_rate)/(recent_rate+previous_rate+ε)`, clipped to [0,1]; 0.5 means equal rates. No future arrivals are read.",
        "",
        "Competence dispersion is the population standard deviation of competence among currently available analysts eligible for each class, divided by 0.5 and clipped to [0,1]. Pool dispersion is the mean across classes with at least two available eligible analysts; coverage is the fraction of classes with a measurable dispersion. A lone eligible analyst is reported as zero class dispersion with zero coverage contribution. Competence values never change: competence regime scenarios change which fixed analysts are active at t=0.5.",
        "",
        "The previous backlog and AI-observation normalizers used the generated episode’s final alert count, which was future information. For this experiment they now use fixed scale `200 × H`, independent of future arrivals. This correction is required for a causal observation and the new PPO is trained from scratch with it. Terminal metrics may still use the admitted episode total.",
        "",
        "## Scenarios",
        "",
        "Stationary: low, medium, high, and heterogeneous-roster demand. Within-episode changes: low→high arrivals, high→low arrivals, homogeneous→heterogeneous staffing, heterogeneous→homogeneous staffing, and alert class-mix shift. OOD: stationary 22 and 190 arrivals/horizon, plus 22→190 and 190→22 changes; training rates were 38–170. Each evaluation scenario uses the exact same alert generation, IA recommendations, roster schedule, service durations, and coordination latency across all six policies.",
        "",
        "## Evaluation outcomes",
        "",
        "Means across paired episodes by evaluation family. `resolution/admitted` is simulated correct resolutions divided by admitted alerts. `switches` is mean per-episode strategy switches; for B3 it counts internal B0/B1/B2 switches across pools.",
        "",
        "| Family | Policy | Episodes | Reward | SLA | Resolution/admitted | Coordination | Backlog | Switches/episode | B0/B1/B2 selection |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in summaries:
        lines.append(f"| {r['family']} | {r['policy']} | {r['episodes']} | {r['reward']:.2f} | {r['sla']:.3f} | {r['resolution_per_admitted']:.3f} | {r['coordination_person_time']:.4f} | {r['backlog']:.2f} | {r['switches']:.2f} | {r['frequency_B0']:.2f}/{r['frequency_B1']:.2f}/{r['frequency_B2']:.2f} |")
    lines += ["", "### Paired reward differences: B4-PPO minus each control", "", "Positive values favor B4-PPO. Intervals use a paired percentile bootstrap (10,000 resamples over matched episode seeds).", "", "| Family | Control | Episodes | Mean difference | 95% CI |", "|---|---|---:|---:|---:|"]
    for r in paired:
        lines.append(f"| {r['family']} | {r['contrast'].removeprefix('B4-PPO minus ')} | {r['episodes']} | {r['mean_difference']:+.2f} | [{r['ci95_low']:+.2f}, {r['ci95_high']:+.2f}] |")
    lines += ["", "### B4 actions around regime changes", "", "Action fractions use the decision-time observation. Pre/post windows are split at the known evaluator change time; the policy itself does not receive that timestamp or the future regime.", "", "| Scenario | Policy | Pre B0/B1/B2 | Post B0/B1/B2 | Mean switches |", "|---|---|---|---|---:|"]
    change_kinds = {"load_low_to_high", "load_high_to_low", "competence_hom_to_het", "competence_het_to_hom", "class_mix_shift", "ood_load_low_to_high", "ood_load_high_to_low"}
    for kind in sorted(change_kinds):
        for policy in ("B3", "SEQ", "B4-PPO"):
            subset = [r for r in rows if r["scenario"] == kind and r["policy"] == policy]
            if not subset:
                continue
            pre = [statistics.mean(float(r[f"pre_{a}"]) for r in subset) for a in ("B0", "B1", "B2")]
            post = [statistics.mean(float(r[f"post_{a}"]) for r in subset) for a in ("B0", "B1", "B2")]
            fmt = lambda vals: "/".join(f"{v:.2f}" for v in vals)
            lines.append(f"| {kind} | {policy} | {fmt(pre)} | {fmt(post)} | {statistics.mean(float(r['switches']) for r in subset):.2f} |")
    lines += ["", "## Interpretation and limits", "",
              "Compare B4-PPO against B3 and `SEQ` using the paired reward table, separately for stationary, changed-regime and OOD families. If B4-PPO action frequencies vary without paired reward gains, that is switching without evidence of useful adaptation. If intervals include zero, the experiment does not establish superiority.",
              "The simulator uses synthetic ground truth and hypothetical service durations, competence values, SLA deadlines, AI error rates, staffing changes and coordination cost. The observed history windows are reactive, not predictive; rate changes are detected only after arrivals occur. OOD cases intentionally test extrapolation and cannot validate real SOC performance. Sample size is 20 per kind and one PPO seed/configuration; no broad hyperparameter search was conducted.",
              "",
              "Reproduction command: `PYTHONPATH=src:studies/soc_human_ai_organization MPLCONFIGDIR=/private/tmp/hls_b4_mpl python studies/soc_human_ai_organization/train_b4_regime_adaptation.py`. This command trains the single declared model and then writes its validation/final artifacts.",
              "",
              "Artifacts: `results/b4_regime_adaptation/b4_ppo_regime.zip`, `training_config.json`, `split_manifest.json`, `training_curve.csv`, `validation_episodes.csv`, `evaluation_episodes.csv`, `evaluation_summary.csv`, `paired_reward_differences.csv`, and `regime_action_shifts.csv`.",
              ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    config = {
        "algorithm": "PPO", "total_timesteps": TIMESTEPS, "seed": MASTER_SEED,
        "architecture": [64, 64], "n_envs": 4, "n_steps": 128, "batch_size": 128,
        "n_epochs": 5, "learning_rate": 0.0003, "gamma": 0.99, "gae_lambda": 0.95,
        "clip_range": 0.2, "ent_coef": 0.01, "vf_coef": 0.5,
        "reward_weights": REWARD_WEIGHTS,
        "seq_rule": "B1 if current backlog_norm sum >= .08 or max current deadline pressure >= .25, else B0",
        "service_by_class": SERVICE, "coordination_latency": COORDINATION_LATENCY,
        "train_rate_range": [38.0, 170.0], "change_time_range": [0.38, 0.62],
        "training_scenario_sampling": {
            "uniform_kinds": ["stationary_low", "stationary_medium", "stationary_high", "stationary_heterogeneous",
                              "load_low_to_high", "load_high_to_low", "competence_hom_to_het",
                              "competence_het_to_hom", "class_mix_shift"],
            "load_shift_low_rate_range": [38.0, 58.0], "load_shift_high_rate_range": [135.0, 168.0],
            "stationary_rates": {"low": 48.0, "medium": 95.0, "high": 150.0, "heterogeneous": 105.0},
            "competence_shift_rate_range": [40.0, 170.0],
            "class_mix_shift": {"before": [0.78, 0.12, 0.10], "after": [0.10, 0.12, 0.78]},
            "dirichlet_class_mix_probability": 0.35,
        },
        "fixed_operating_parameters": {
            "service_time_per_class": SERVICE, "coordination_latency": COORDINATION_LATENCY,
            "deadline_by_severity": {"low": 0.16, "medium": 0.10, "high": 0.055},
            "escalation_probability_by_class": {"class_0": 0.12, "class_1": 0.18, "class_2": 0.24},
            "ai_sensitivity": 0.84, "ai_false_positive_rate": 0.11,
            "competence_homogeneous": 0.70,
            "competence_heterogeneous_l1": [[0.94, 0.58, 0.42], [0.48, 0.91, 0.62]],
            "competence_heterogeneous_l2_additive_offset": 0.04,
            "competence_shift_active_analysts_per_pool": 2,
            "all_analysts_eligible_for_all_classes": True,
        },
        "final_replicates_per_scenario": FINAL_REPLICATES,
        "validation_replicates_per_scenario": VALIDATION_REPLICATES,
        "evaluation_action_mode": "deterministic PPO actions; fixed controls are deterministic",
        "ood_rates": [22.0, 190.0], "test_policy": "highest mean frozen reward; claim only if paired 95% CI excludes zero",
        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout.strip(),
        "observation_additions": ["two causal trailing-window arrival rates and normalized trend", "per-pool/per-class current-availability competence dispersion and coverage"],
        "normalization_leak_fix": "backlog and AI-observation counts use fixed 200*H scale, not total generated episode admissions",
    }
    split = {
        "training_namespace": str(TRAIN_OFFSET), "validation_namespace": str(VALID_OFFSET),
        "final_namespace": str(FINAL_OFFSET), "final_test_opened_after_model_freeze": True,
        "evaluation_kinds": tuple(FAMILY_FOR_KIND), "replicates_per_kind": FINAL_REPLICATES,
        "validation_only_descriptive": True,
    }
    (OUT / "training_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (OUT / "split_manifest.json").write_text(json.dumps(split, indent=2), encoding="utf-8")

    # Train exactly one model; never inspect final evaluation during training.
    from gymnasium.utils.env_checker import check_env
    check_spec = make_scenario(TRAIN_OFFSET + 42, training=True)
    check_env(B4GymnasiumAdapter(lambda _seed: build_env(check_spec), CLASSES), skip_render_check=True)
    vec = VecMonitor(DummyVecEnv([lambda: B4GymnasiumAdapter(training_factory, CLASSES) for _ in range(4)]),
                     filename=str(OUT / "sb3_monitor"))
    callback = TrainingCallback()
    model = PPO("MlpPolicy", vec, seed=MASTER_SEED, n_steps=128, batch_size=128, n_epochs=5,
                learning_rate=3e-4, gamma=0.99, gae_lambda=0.95, clip_range=0.2,
                ent_coef=0.01, vf_coef=0.5, policy_kwargs={"net_arch": [64, 64]},
                device="cpu", verbose=0)
    started = time.perf_counter()
    model.learn(total_timesteps=TIMESTEPS, callback=callback, progress_bar=False)
    elapsed = time.perf_counter() - started
    model_path = OUT / "b4_ppo_regime.zip"
    model.save(model_path)
    vec.close()
    _write_csv(OUT / "training_curve.csv", callback.episodes)
    config.update({"training_seconds": elapsed, "completed_training_episodes": len(callback.episodes),
                   "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
                   "versions": {"torch": torch.__version__, "gymnasium": gymnasium.__version__,
                                "stable_baselines3": stable_baselines3.__version__, "numpy": np.__version__}})
    (OUT / "training_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    # Separate descriptive validation run; no checkpoint/threshold selection follows.
    _, validation_rows = _evaluate_suite(model, offset=VALID_OFFSET, replicates=VALIDATION_REPLICATES)
    _write_csv(OUT / "validation_episodes.csv", validation_rows)
    # Freeze model/config before constructing final seeds.
    _, final_rows = _evaluate_suite(model, offset=FINAL_OFFSET, replicates=FINAL_REPLICATES)
    _write_csv(OUT / "evaluation_episodes.csv", final_rows)
    summaries, paired = _summarize(final_rows)
    _write_csv(OUT / "evaluation_summary.csv", summaries)
    _write_csv(OUT / "paired_reward_differences.csv", paired)
    shift_rows = [r for r in final_rows if r["change_time"] is not None]
    _write_csv(OUT / "regime_action_shifts.csv", shift_rows)
    _write_report(REPORT, config, summaries, paired, final_rows, len(callback.episodes))
    print(json.dumps({"model": str(model_path), "report": str(REPORT), "training_seconds": elapsed,
                      "training_episodes": len(callback.episodes), "evaluation_episodes": len(final_rows),
                      "paired_reward_differences": paired}, indent=2))


if __name__ == "__main__":
    main()
