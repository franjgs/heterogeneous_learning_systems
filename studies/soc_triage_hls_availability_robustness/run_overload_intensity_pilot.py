"""Run the predeclared NEW MODEL intensity/duration pilot on existing engines."""
from __future__ import annotations

import argparse
import hashlib
import json
from math import sqrt
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from studies.soc_triage_hls_availability_robustness.run_policy_pilot import (  # noqa: E402
    POLICIES, run_pilot,
)
from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import (  # noqa: E402
    CapacityDemandProfile, DemandRegime, assess_capacity,
)
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario  # noqa: E402


HERE = Path(__file__).resolve().parent
CONFIG_DIR = HERE / "config"
PROFILES = ("A", "B", "C", "D")
SEEDS = tuple(range(2026112801, 2026112813))
PAIRS = (("P1", "D1"), ("WAPS", "D1"), ("WAPS", "P1"))
T_CRIT_95_DF11 = 2.200985160082949


def _paired_summary(values: list[float]) -> dict:
    n = len(values)
    mean = sum(values) / n
    sd = (sum((value - mean) ** 2 for value in values) / (n - 1)) ** 0.5 if n > 1 else 0.0
    half = T_CRIT_95_DF11 * sd / sqrt(n) if n == 12 else None
    return {
        "n_seed_episodes": n,
        "mean": mean,
        "sample_sd": sd,
        "descriptive_95_percent_t_interval": [mean - half, mean + half] if half is not None else None,
        "left_better_count": sum(x > 1e-12 for x in values),
        "right_better_count": sum(x < -1e-12 for x in values),
        "ties_within_1e-12": sum(abs(x) <= 1e-12 for x in values),
    }


def _capacity_diagnostic(scenario) -> list[dict]:
    demand = scenario.demand_profile
    profile = CapacityDemandProfile(
        regimes=tuple(DemandRegime(r["name"], r["start_h"], r["end_h"], r["arrival_rate_by_class"])
                      for r in demand["regimes"]),
        prevalence_by_class=demand["prevalence_by_class"],
        sensitivity_by_class=demand["sensitivity_by_class"],
        false_positive_rate_by_class=demand["false_positive_rate_by_class"],
        alpha=demand["alpha"], beta=demand["beta"], gamma=demand.get("gamma", 1.0),
        flow_mode=scenario.flow_mode,
    )
    return [vars(item) for item in assess_capacity(scenario.organization, profile).regimes]


def _mode_occupancy(run: dict, horizon: float) -> dict:
    """Integrate logged WAPS state changes over natural time; initial mode is D1."""
    output = {}
    for level in ("L1", "L2"):
        events = sorted((item for item in run["hlsb_switches"] if item["level"] == level),
                        key=lambda item: item["time"])
        mode, last, durations = "D1", 0.0, {"D1": 0.0, "P1": 0.0}
        for event in events:
            at = min(horizon, max(last, float(event["time"])))
            durations[mode] += at - last
            mode = event["mode"]
            last = at
        durations[mode] += horizon - last
        epochs = int(run["dispatch_epochs_by_level"].get(level, 0))
        p1_epochs = int(run["p1_dispatch_epochs_by_level"].get(level, 0))
        output[level] = {
            "logged_state_hours": durations,
            "logged_state_fraction_of_evaluation_horizon": {
                key: value / horizon if horizon else 0.0 for key, value in durations.items()
            },
            "dispatch_epochs": epochs,
            "dispatch_epochs_by_mode": {"D1": epochs - p1_epochs, "P1": p1_epochs},
            "dispatch_epoch_fraction_by_mode": {
                "D1": (epochs - p1_epochs) / epochs if epochs else 0.0,
                "P1": p1_epochs / epochs if epochs else 0.0,
            },
            "switches": len(events),
        }
    return output


def _paired_differences(rows: list[dict]) -> dict:
    by_seed_policy = {(row["seed"], row["policy"]): row for row in rows}
    result = {}
    for left, right in PAIRS:
        label = f"{left} - {right}"
        result[label] = {}
        metrics = ("R_over_N", "sla_fraction_on_time", "sla_fraction_late",
                   "quality_mean_completed", "mean_response_completed_h", "mean_wait_to_start_h")
        for metric in metrics:
            result[label][metric] = _paired_summary([
                by_seed_policy[seed, left][metric] - by_seed_policy[seed, right][metric]
                for seed in SEEDS
            ])
        for regime in ("ordinary", "overload_pulse", "recovery"):
            for metric in ("R_over_N", "sla_fraction_on_time", "sla_fraction_late",
                           "quality_mean_completed", "mean_response_completed_h", "mean_wait_to_start_h"):
                result[label][f"regime:{regime}:{metric}"] = _paired_summary([
                    by_seed_policy[seed, left]["strata"][f"regime:{regime}"][metric] -
                    by_seed_policy[seed, right]["strata"][f"regime:{regime}"][metric]
                    for seed in SEEDS
                ])
    return result


def run_experiment(output: Path) -> dict:
    if len(SEEDS) != 12 or len(set(SEEDS)) != 12:
        raise AssertionError("pilot requires twelve unique paired seeds")
    prior_seed_blocks = [set(range(2026112701, 2026112711)), {998001},
                         set(range(711000000, 711000400)), set(range(910000, 911000)),
                         set(range(920000, 921000)), set(range(930000, 931000))]
    if any(set(SEEDS) & block for block in prior_seed_blocks):
        raise AssertionError("predeclared seed block overlaps a documented pilot/campaign block")

    profiles = {}
    organization_hashes = set()
    for label in PROFILES:
        config = CONFIG_DIR / f"SOC_NEW_MODEL_OVERLOAD_PROFILE_{label}.json"
        config_bytes = config.read_bytes()
        config_doc = json.loads(config_bytes)
        scenario = load_scenario(config)
        organization_hashes.add(hashlib.sha256(json.dumps(
            config_doc["organization"], sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest())
        payload = run_pilot(config, SEEDS)
        if len(payload["runs"]) != len(SEEDS) * len(POLICIES):
            raise AssertionError(f"profile {label}: expected 36 policy episodes")
        evaluation_horizon = scenario.settings.evaluation_horizon
        for row in payload["runs"]:
            if row["policy"] == "WAPS":
                row["hlsb_mode_occupancy"] = _mode_occupancy(row, evaluation_horizon)
        payload["paired_differences"] = _paired_differences(payload["runs"])
        payload["capacity_diagnostics"] = _capacity_diagnostic(scenario)
        payload["profile_design"] = dict(config_doc["demand_profile"]["design_metadata"])
        payload["evaluation_horizon_h"] = evaluation_horizon
        payload["admission_horizon_h"] = scenario.settings.admission_horizon
        payload["config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
        profiles[label] = payload
    if len(organization_hashes) != 1:
        raise AssertionError("organization differs between the four demand profiles")

    manifest = {
        "schema_version": 1,
        "experiment_id": "soc-new-model-overload-intensity-duration-pilot",
        "classification": "exploratory, paired; not confirmatory",
        "branch": "research/soctra-hls-new-model",
        "starting_commit": "5026e303c51e6dd4523d5aad90b276309385ea2b",
        "seed_selection": "predeclared fixed block after search of repository campaign/pilot seed declarations; disjoint from the known historical and NEW MODEL pilot blocks",
        "seeds": list(SEEDS),
        "policies": list(POLICIES),
        "runs_total": len(PROFILES) * len(SEEDS) * len(POLICIES),
        "organization_sha256": next(iter(organization_hashes)),
        "interval": "paired seed-level Student-t descriptive 95% interval, df=11; cohort contrasts are not independent replications",
        "mode_metrics_note": "dispatch mode counts are exact engine counters; state-hours integrate logged D1/P1 mode transitions over each level's full evaluation horizon, initial state D1",
        "profiles": profiles,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "SOC_NEW_MODEL_OVERLOAD_INTENSITY_RESULTS.json")
    args = parser.parse_args()
    payload = run_experiment(args.output)
    print(json.dumps({"output": str(args.output), "runs": payload["runs_total"],
                      "seeds": payload["seeds"], "profiles": list(payload["profiles"])}, indent=2))


if __name__ == "__main__":
    main()
