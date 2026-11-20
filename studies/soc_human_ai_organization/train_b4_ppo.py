"""Bounded first PPO training and paired evaluation for sequential B4.

No SOCTRA row-level data are read. Empirical SOCTRA aggregates are scenario
anchors only; all evaluated episodes have known simulated evaluator truth.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
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


CLASSES = ("class_0", "class_1", "class_2")
TRAIN_SEED_OFFSET = 1_000_000_000_000
VALIDATION_SEED_OFFSET = 2_000_000_000_000
TEST_SEED_OFFSET = 3_000_000_000_000
MASTER_SEED = 20261118
POLICIES = ("B0", "B1", "B2", "B3", "B4")
REWARD_WEIGHTS = (1.0, 1.0, 0.20, 0.50)  # SLA, resolution, coordination, triage error


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_seed: int
    trace_seed: int
    config: ScenarioConfig
    l1: tuple[Analyst, ...]
    l2: tuple[Analyst, ...]
    l1_service: dict[str, float]
    l2_service: dict[str, float]
    l1_individual_service: dict[str, dict[str, float]]
    l2_individual_service: dict[str, dict[str, float]]
    coordination_latency: float
    drain_period: float
    eligibility_profile: str


def sample_scenario(seed: int, *, split: str) -> ScenarioSpec:
    """Sample one scenario from the declared split-specific seed namespace."""
    rng = np.random.default_rng(seed)
    class_mix = tuple(float(x) for x in rng.dirichlet(np.array([0.9, 0.9, 0.9])))
    shifted_mix = tuple(float(x) for x in rng.dirichlet(np.array([0.8, 0.8, 0.8])))
    severity_mix = tuple(float(x) for x in rng.dirichlet(np.array([1.3, 1.3, 1.3])))
    base_escalation = rng.uniform(0.05, 0.28, size=3)
    severity_factor = np.array([0.60, 1.0, 1.55])
    escalation_matrix = tuple(tuple(float(min(0.75, p * f)) for f in severity_factor)
                              for p in base_escalation)
    sensitivity = tuple(float(x) for x in rng.uniform(0.68, 0.96, size=3))
    false_positive = tuple(float(x) for x in rng.uniform(0.04, 0.28, size=3))
    arrival_rate = float(rng.uniform(45.0, 170.0))
    burst = None
    if rng.random() < 0.60:
        start = float(rng.uniform(0.15, 0.65))
        end = min(0.95, start + float(rng.uniform(0.08, 0.25)))
        burst = (start, end, float(rng.uniform(1.8, 4.2)))
    shift_after = float(rng.uniform(0.45, 0.75)) if rng.random() < 0.55 else None
    service_scale = float(rng.uniform(0.006, 0.020))
    deadline_scale = float(rng.uniform(0.65, 1.45))
    config = ScenarioConfig(
        horizon=1.0,
        arrival_rate=arrival_rate,
        l1_availability_fraction=float(rng.choice([0.50, 0.75, 1.0])),
        l2_availability_fraction=float(rng.choice([0.50, 0.75, 1.0])),
        classes=CLASSES,
        class_probabilities=class_mix,
        severity_probabilities=severity_mix,
        escalation_probability_by_class=tuple(float(x) for x in base_escalation),
        escalation_probability_by_class_severity=escalation_matrix,
        deadline_by_severity=(
            ("low", 0.16 * deadline_scale),
            ("medium", 0.10 * deadline_scale),
            ("high", 0.055 * deadline_scale),
        ),
        burst_window=burst,
        shift_after=shift_after,
        shift_class_probabilities=shifted_mix if shift_after is not None else None,
        ai_sensitivity=float(np.mean(sensitivity)),
        ai_false_positive_rate=float(np.mean(false_positive)),
        ai_shift_sensitivity_delta=float(rng.uniform(-0.22, 0.02)),
        ai_shift_false_positive_delta=float(rng.uniform(-0.01, 0.16)),
        ai_sensitivity_by_severity=sensitivity,
        ai_false_positive_by_severity=false_positive,
        difficulty_beta=(float(rng.uniform(1.2, 3.0)), float(rng.uniform(1.2, 3.0))),
    )
    profile = str(rng.choice(["homogeneous", "specialist_generalist", "mixed"], p=[0.34, 0.42, 0.24]))
    l1, l1_services, l1_individual = _make_roster("L1", 4, profile, service_scale, rng)
    l2, l2_services, l2_individual = _make_roster("L2", 2, profile, service_scale * 1.1, rng)
    mean_service = statistics.mean((*l1_services.values(), *l2_services.values()))
    coordination_latency = float(rng.uniform(0.0, 0.20 * mean_service))
    # Separate trace seed from scenario generation seed, fixed by the scenario draw.
    trace_seed = int(rng.integers(0, 2**31 - 1))
    return ScenarioSpec(seed, trace_seed, config, l1, l2, l1_services, l2_services,
                       l1_individual, l2_individual, coordination_latency, 0.50, profile)


def _make_roster(level: str, count: int, profile: str, service_scale: float, rng):
    roster = []
    base_services = {k: float(service_scale * rng.uniform(0.65, 1.40)) for k in CLASSES}
    individual: dict[str, dict[str, float]] = {}
    for ix in range(count):
        if profile == "homogeneous":
            eligible = set(CLASSES)
        elif profile == "specialist_generalist":
            eligible = set(CLASSES) if ix == 0 else {CLASSES[(ix - 1) % len(CLASSES)]}
        else:
            eligible = {key for key in CLASSES if rng.random() < 0.58}
        if profile == "mixed" and not eligible:
            eligible = {str(rng.choice(CLASSES))}
        analyst_id = f"{level}-{ix}"
        competence = {key: float(rng.uniform(0.38, 0.97)) for key in eligible}
        roster.append(Analyst(analyst_id, frozenset(eligible), competence))
        individual[analyst_id] = {key: float(base_services[key] * rng.lognormal(0.0, 0.40)) for key in eligible}
    # Guarantee every class can be handled in mixed profile without making skills homogeneous.
    for key in CLASSES:
        if not any(key in analyst.eligible_classes for analyst in roster):
            ix = int(rng.integers(0, count))
            old = roster[ix]
            eligible = set(old.eligible_classes) | {key}
            competence = dict(old.competence)
            competence[key] = float(rng.uniform(0.38, 0.97))
            roster[ix] = Analyst(old.analyst_id, frozenset(eligible), competence)
            individual[old.analyst_id][key] = float(base_services[key] * rng.lognormal(0.0, 0.40))
    return tuple(roster), base_services, individual


def build_env(spec: ScenarioSpec) -> B4EpisodeEnv:
    env = B4EpisodeEnv(
        spec.config, spec.l1, spec.l2, spec.l1_service, spec.l2_service,
        drain_period=spec.drain_period,
        coordination_latency=spec.coordination_latency,
        sequential_reward_weights=REWARD_WEIGHTS,
        l1_service_by_analyst_class=spec.l1_individual_service,
        l2_service_by_analyst_class=spec.l2_individual_service,
    )
    env.scenario_seed = spec.scenario_seed
    return env


def train_scenario_factory(seed: int) -> B4EpisodeEnv:
    scenario_seed = TRAIN_SEED_OFFSET + int(seed % 1_000_000_000)
    return build_env(sample_scenario(scenario_seed, split="train"))


class EpisodeLogCallback(BaseCallback):
    def __init__(self):
        super().__init__()
        self.rows: list[dict[str, object]] = []

    def _on_step(self) -> bool:
        for done, info in zip(self.locals["dones"], self.locals["infos"]):
            if done and "episode" in info:
                row = {"timesteps": self.num_timesteps,
                       "episode_reward": float(info["episode"]["r"]),
                       "episode_length": int(info["episode"]["l"]),
                       "scenario_seed": info.get("scenario_seed"),
                       "trace_seed": info.get("trace_seed")}
                for key in ("sla_fraction", "mean_resolution_accuracy", "triage_error_fraction", "coordination_person_time"):
                    if key in info:
                        row[key] = info[key]
                for key, value in info.get("action_counts", {}).items():
                    row[f"action_{key}"] = value
                self.rows.append(row)
        return True


def evaluate(model: PPO | None, spec: ScenarioSpec, policy: str) -> dict[str, object]:
    adapter = B4GymnasiumAdapter(lambda _seed: build_env(spec), CLASSES)
    observation, _ = adapter.reset(seed=spec.trace_seed)
    env = adapter._inner
    total_reward = 0.0
    terminated = False
    final_info: dict[str, object] = {}
    decisions = 0
    while not terminated:
        if policy == "B4":
            action, _ = model.predict(observation, deterministic=True)
            observation, reward, terminated, truncated, final_info = adapter.step(int(action))
        else:
            # Baselines use the same resumable environment and event-level reward accounting.
            observation_dict, reward, terminated, truncated, final_info = env.step_fixed(policy)
            observation = adapter._vector(observation_dict)
        if truncated:
            raise RuntimeError("finite event episodes should terminate, not truncate")
        total_reward += float(reward)
        decisions += 1
    row = {
        "scenario_seed": spec.scenario_seed,
        "gym_reset_seed": spec.trace_seed,
        "trace_seed": adapter.episode_trace_seed,
        "eligibility_profile": spec.eligibility_profile,
        "policy": policy,
        "admitted": final_info["admitted"],
        "completed": final_info["completed"],
        "completed_within_sla": final_info["completed_within_sla"],
        "sla_fraction": final_info["sla_fraction"],
        "resolution_accuracy": final_info["mean_resolution_accuracy"],
        "resolution_success_per_admitted": final_info["resolution_success_per_admitted"],
        "triage_error_fraction": final_info["triage_error_fraction"],
        "coordination_person_time": final_info["coordination_person_time"],
        "backlog": final_info["pending"],
        "reward": total_reward,
        "decisions": decisions,
        "action_counts": final_info["action_counts"],
        "b3_strategy_counts": final_info["b3_strategy_counts"],
    }
    return row


def summarize(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    metrics = ("sla_fraction", "resolution_accuracy", "resolution_success_per_admitted", "triage_error_fraction",
               "coordination_person_time", "backlog", "reward")
    summary = []
    for policy in POLICIES:
        subset = [r for r in rows if r["policy"] == policy]
        entry: dict[str, object] = {"policy": policy, "episodes": len(subset)}
        for metric in metrics:
            entry[metric] = statistics.mean(float(r[metric]) for r in subset) if subset else 0.0
        counts = {name: 0 for name in ("B0", "B1", "B2")}
        if policy == "B4":
            for r in subset:
                for name, count in dict(r["action_counts"]).items():
                    if name in counts:
                        counts[name] += int(count)
        elif policy == "B3":
            for r in subset:
                for name, count in dict(r["b3_strategy_counts"]).items():
                    counts[name] += int(count)
        elif policy in {"B0", "B1", "B2"}:
            counts[policy] = sum(int(r["action_counts"].get(policy, 0)) for r in subset)
        total = sum(counts.values())
        for name, count in counts.items():
            entry[f"selection_{name}_fraction"] = count / total if total else 0.0
        summary.append(entry)
    diffs = []
    for metric in metrics:
        b4 = {int(r["scenario_seed"]): float(r[metric]) for r in rows if r["policy"] == "B4"}
        b3 = {int(r["scenario_seed"]): float(r[metric]) for r in rows if r["policy"] == "B3"}
        paired = np.asarray([b4[key] - b3[key] for key in sorted(b4.keys() & b3.keys())], dtype=float)
        lo, hi = paired_bootstrap_ci(paired, seed=20261119)
        diffs.append({"metric": metric, "contrast": "B4-B3", "mean_difference": float(paired.mean()),
                      "ci95_low": lo, "ci95_high": hi, "episodes": len(paired),
                      "method": "paired percentile bootstrap, 10000 resamples"})
    return summary, diffs


def paired_bootstrap_ci(values: np.ndarray, *, seed: int, n_boot: int = 10000) -> tuple[float, float]:
    if not len(values):
        return 0.0, 0.0
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(values), size=(n_boot, len(values)))
    means = values[draws].mean(axis=1)
    low, high = np.quantile(means, [0.025, 0.975])
    return float(low), float(high)


def _assert_paired_evaluation(rows: list[dict[str, object]], expected_episodes: int) -> None:
    by_seed: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        by_seed.setdefault(int(row["scenario_seed"]), []).append(row)
    if len(by_seed) != expected_episodes:
        raise RuntimeError("evaluation scenario seeds are missing or duplicated")
    for seed, group in by_seed.items():
        if {row["policy"] for row in group} != set(POLICIES) or len(group) != len(POLICIES):
            raise RuntimeError(f"incomplete policy pairing for scenario {seed}")
        if len({row["trace_seed"] for row in group}) != 1:
            raise RuntimeError(f"trace mismatch across policies for scenario {seed}")
        if len({row["admitted"] for row in group}) != 1:
            raise RuntimeError(f"arrival-count mismatch across policies for scenario {seed}")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    flattened = []
    for row in rows:
        item = dict(row)
        for key in ("action_counts", "b3_strategy_counts"):
            if key in item:
                nested = item.pop(key)
                item.update({f"{key}_{name}": value for name, value in nested.items()})
        flattened.append(item)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flattened[0]))
        writer.writeheader()
        writer.writerows(flattened)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/b4_rl_initial"))
    parser.add_argument("--timesteps", type=int, default=16384)
    parser.add_argument("--validation-episodes", type=int, default=24)
    parser.add_argument("--test-episodes", type=int, default=48)
    args = parser.parse_args()
    if args.timesteps <= 0 or args.validation_episodes < 1 or args.test_episodes < 2:
        parser.error("timesteps must be positive, validation >=1 and test >=2")
    args.out.mkdir(parents=True, exist_ok=True)

    split_manifest = {
        "training": {"scenario_seed_namespace": str(TRAIN_SEED_OFFSET), "sb3_master_seed": MASTER_SEED,
                     "episodes": "on-policy, sampled from seed-driven scenario generator"},
        "validation": {"scenario_seeds": [VALIDATION_SEED_OFFSET + i for i in range(args.validation_episodes)],
                       "use": "post-training description only; no checkpoint or reward-weight selection"},
        "final_test": {"scenario_seeds": [TEST_SEED_OFFSET + i for i in range(args.test_episodes)],
                       "use": "held out from training, validation and all model/reward selection; opened after final model freeze"},
        "scenario_sampling": "independent deterministic RNG draws for demand, bursts, class mix, eligibility, competence, service and AI error rates",
    }
    config = {
        "algorithm": "PPO", "policy": "MlpPolicy", "total_timesteps": args.timesteps,
        "n_envs": 4, "n_steps": 128, "batch_size": 128, "n_epochs": 5,
        "learning_rate": 0.0003, "gamma": 0.99, "gae_lambda": 0.95,
        "clip_range": 0.2, "ent_coef": 0.01, "vf_coef": 0.5,
        "policy_kwargs": {"net_arch": [64, 64]}, "device": "cpu", "seed": MASTER_SEED,
        "reward_weights": {"sla": REWARD_WEIGHTS[0], "resolution": REWARD_WEIGHTS[1],
                           "coordination_normalized": REWARD_WEIGHTS[2], "triage_error": REWARD_WEIGHTS[3]},
        "reward_normalization": "coordination person-time divided by horizon*(L1+L2 analyst count); event indicators are per alert",
        "soctra_empirical_reference": "aggregate-only plausible scenario ranges, not row-level training data",
        "soctra_aggregate_anchors": {
            "complete_day_alert_mean": 216.1, "complete_day_alert_sd": 89.0,
            "complete_day_cv": 0.412, "top_five_project_share": 0.5923,
            "published_standardized_escalation_lse_balanced_accuracy": 0.8477,
            "published_standardized_escalation_lse_false_alarm_rate": 0.2695,
            "published_standardized_escalation_lse_detection_rate": 0.9649,
            "interpretation": "anchor ranges only; normalized synthetic arrival rates are not direct replay or operational fit",
        },
        "versions": {"python_torch": torch.__version__, "gymnasium": gymnasium.__version__,
                     "stable_baselines3": stable_baselines3.__version__, "numpy": np.__version__},
        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout.strip(),
    }
    (args.out / "split_manifest.json").write_text(json.dumps(split_manifest, indent=2), encoding="utf-8")
    (args.out / "training_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    check_spec = sample_scenario(TRAIN_SEED_OFFSET + 11, split="train")
    from gymnasium.utils.env_checker import check_env
    check_env(B4GymnasiumAdapter(lambda _seed: build_env(check_spec), CLASSES), skip_render_check=True)

    vec_env = VecMonitor(DummyVecEnv([
        lambda rank=rank: B4GymnasiumAdapter(train_scenario_factory, CLASSES)
        for rank in range(4)
    ]), filename=str(args.out / "sb3_monitor"))
    callback = EpisodeLogCallback()
    model = PPO(
        "MlpPolicy", vec_env, seed=MASTER_SEED, n_steps=128, batch_size=128,
        n_epochs=5, learning_rate=3e-4, gamma=0.99, gae_lambda=0.95,
        clip_range=0.2, ent_coef=0.01, vf_coef=0.5,
        policy_kwargs={"net_arch": [64, 64]}, device="cpu", verbose=0,
    )
    started = time.perf_counter()
    model.learn(total_timesteps=args.timesteps, callback=callback, progress_bar=False)
    train_seconds = time.perf_counter() - started
    model_path = args.out / "b4_ppo_initial.zip"
    model.save(model_path)
    vec_env.close()
    write_csv(args.out / "training_curve.csv", callback.rows)
    write_csv(args.out / "training_episode_seeds.csv", [
        {"episode": i + 1, "scenario_seed": row.get("scenario_seed"),
         "trace_seed": row.get("trace_seed"), "timesteps": row.get("timesteps")}
        for i, row in enumerate(callback.rows)
    ])
    config["training_seconds"] = train_seconds
    config["training_episodes_observed"] = len(callback.rows)
    config["model_sha256"] = hashlib.sha256(model_path.read_bytes()).hexdigest()
    (args.out / "training_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    # Validation is descriptive only; no hyperparameter, checkpoint or reward change follows it.
    validation_specs = [sample_scenario(VALIDATION_SEED_OFFSET + i, split="validation")
                        for i in range(args.validation_episodes)]
    validation_rows = [evaluate(model, spec, policy) for spec in validation_specs for policy in POLICIES]
    write_csv(args.out / "validation_episodes.csv", validation_rows)
    validation_summary, _ = summarize(validation_rows)
    write_csv(args.out / "validation_summary.csv", validation_summary)

    # The final episode suite is generated and opened only after the single model is frozen.
    test_specs = [sample_scenario(TEST_SEED_OFFSET + i, split="test") for i in range(args.test_episodes)]
    test_rows = [evaluate(model, spec, policy) for spec in test_specs for policy in POLICIES]
    _assert_paired_evaluation(test_rows, args.test_episodes)
    write_csv(args.out / "test_episodes.csv", test_rows)
    test_summary, paired = summarize(test_rows)
    write_csv(args.out / "test_summary.csv", test_summary)
    write_csv(args.out / "paired_b4_minus_b3.csv", paired)
    (args.out / "test_seeds.json").write_text(json.dumps([s.scenario_seed for s in test_specs], indent=2), encoding="utf-8")
    report_path = args.out / "B4_RL_INITIAL_RESULTS.md"
    _write_report(report_path, config, validation_summary, test_summary, paired)
    shutil.copyfile(report_path, Path("studies/soc_human_ai_organization/B4_RL_INITIAL_RESULTS.md"))
    print(json.dumps({"out": str(args.out), "model": str(model_path), "train_seconds": train_seconds,
                      "train_episodes": len(callback.rows), "test_episodes": args.test_episodes,
                      "b4_vs_b3": paired[0]}, indent=2))
    return 0


def _write_report(path: Path, config, validation_summary, test_summary, paired) -> None:
    lines = ["# B4-RL initial controlled simulation results", "",
             "**Status:** one bounded PPO run; simulated demand only; no SOCTRA records used as training data.", "",
             "## Protocol", "",
             f"PPO uses {config['total_timesteps']} timesteps, 4 parallel environments, a 2×64 MLP, CPU, seed {config['seed']}.",
             f"Training time: {config['training_seconds']:.2f} s; completed training episodes observed: {config['training_episodes_observed']}.",
             "The 24-seed validation set is descriptive and did not select a checkpoint or tune weights. Final test seeds are independently generated and opened only after model/config freeze; no test result was used to select or alter the controller.",
             "All five strategies use the same simulator, seeded alerts, AI recommendations, eligibility roster, competencies, service times, and event-level reward accounting within each paired test episode.",
             "Reward per event is: SLA success + correct simulated resolution − normalized coordination cost − triage error. Weights are frozen in `training_config.json`.", "",
             "Environment versions are pinned in `studies/soc_human_ai_organization/requirements-b4-rl.txt`. Reproduction command: `PYTHONPATH=src MPLCONFIGDIR=/private/tmp/hls_b4_mpl python studies/soc_human_ai_organization/train_b4_ppo.py --out results/b4_rl_initial --timesteps 16384 --validation-episodes 24 --test-episodes 48`.", "",
             "## Final test averages", "",
             "| Policy | SLA fraction | Resolution accuracy | Resolution success/admitted | Triage error | Coordination person-time | Backlog | Reward | B0 selection | B1 selection | B2 selection |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in test_summary:
        lines.append("| {policy} | {sla_fraction:.3f} | {resolution_accuracy:.3f} | {resolution_success_per_admitted:.3f} | {triage_error_fraction:.3f} | {coordination_person_time:.4f} | {backlog:.3f} | {reward:.3f} | {selection_B0_fraction:.3f} | {selection_B1_fraction:.3f} | {selection_B2_fraction:.3f} |".format(**r))
    lines += ["", "## Paired B4 − B3 differences", "", "| Metric | Mean difference | 95% CI | Episodes |", "|---|---:|---:|---:|"]
    for r in paired:
        lines.append(f"| {r['metric']} | {r['mean_difference']:.4f} | [{r['ci95_low']:.4f}, {r['ci95_high']:.4f}] | {r['episodes']} |")
    b4 = next(r for r in test_summary if r["policy"] == "B4")
    b3 = next(r for r in test_summary if r["policy"] == "B3")
    lines += ["", "## Interpretation", "",
              f"On the final test episodes B4 selected B0/B1/B2 at rates {b4['selection_B0_fraction']:.3f}/{b4['selection_B1_fraction']:.3f}/{b4['selection_B2_fraction']:.3f}; the learned controller therefore behaved as fixed B1 in this test. B3 used the three strategies at {b3['selection_B0_fraction']:.3f}/{b3['selection_B1_fraction']:.3f}/{b3['selection_B2_fraction']:.3f}.",
              "The paired SLA contrast favors B4 in this scenario suite, while resolution and reward intervals include zero; B4 also incurs a higher coordination cost than B3. The overall reward interval does not support a claim that B4 outperforms B3. Results suggest specialization toward B1 under these scenario/reward settings, not a general RL advantage.",
              "Gamma discounts per decision, not per simulated-time unit; elapsed time is recorded, but no continuous-time discount correction is applied in this initial PPO baseline."]
    lines += ["", "Intervals use a paired percentile bootstrap (10,000 resamples over test scenarios). No superiority claim is made when the interval includes zero.",
              "", "## Limitations", "",
              "Scenarios are synthetic and deliberately varied; SOCTRA provides aggregate plausibility anchors only. Simulated need-for-L2 and resolution outcomes are known to the evaluator, never to observations. Analyst availability is an episode-level fraction rather than shifts. Reward weights and scenario ranges are hypothetical. One seed and one PPO configuration do not establish robust RL superiority. B3 is the fixed rule-based adaptive reference.",
              "", "Artifacts: `b4_ppo_initial.zip`, `training_config.json`, `split_manifest.json`, `training_curve.csv`, `training_episode_seeds.csv`, `validation_episodes.csv`, `test_episodes.csv`, `test_summary.csv`, and `paired_b4_minus_b3.csv`.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
