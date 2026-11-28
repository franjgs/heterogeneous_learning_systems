"""Paired-seed exploratory staffing diagnosis for the frozen CONOPS.

One exogenous alert trace is generated per seed and reused unchanged for all
nine L1/L2 roster combinations. D1 remains at L1 and P1 at L2. This is a
staffing/capacity study, not a policy comparison.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter, defaultdict
from dataclasses import replace
import hashlib
import json
from math import isclose
from pathlib import Path
import sys
from statistics import mean, pstdev

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from studies.soc_triage_hls_availability_robustness.execution_api import (  # noqa: E402
    CalendarBackend, OrganizationConfig, TeamConfig,
)
from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import (  # noqa: E402
    CapacityDemandProfile, DemandRegime, assess_capacity,
)
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario  # noqa: E402
from studies.soc_triage_hls_availability_robustness.triage_execution import run_triage_flow  # noqa: E402


STUDY_CONFIG = Path(__file__).with_name("config") / "SOC_NEW_MODEL_STAFFING_SIZING.json"
BASE_CONFIG = Path(__file__).with_name("config") / "SOC_NEW_MODEL_CONOPS_REFERENCE.json"
DEFAULT_OUTPUT = Path(__file__).with_name("results") / "soc_new_model_staffing_sizing.json"


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def trace_sha256(rows) -> str:
    canonical = [{
        "alert_id": row.routed.alert.alert_id,
        "arrival_h": float(row.routed.alert.arrival),
        "deadline_h": float(row.routed.alert.deadline),
        "class": str(row.routed.alert.task_class),
        "severity": row.severity,
        "q": float(row.difficulty),
        "reference_l2": bool(row.true_escalation_need),
        "recommend_l2": bool(row.routed.soctra_recommendation),
    } for row in rows]
    return _sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode())


def build_organization(base, l1_ids: list[str], l2_ids: list[str]) -> OrganizationConfig:
    chosen = set(l1_ids) | set(l2_ids)
    by_id = {r.analyst.analyst_id: r for r in base.organization.analysts}
    if chosen - set(by_id):
        raise ValueError(f"unknown roster IDs: {sorted(chosen - set(by_id))}")
    resources = tuple(by_id[aid] for aid in (*l1_ids, *l2_ids))
    for level, ids in (("L1", l1_ids), ("L2", l2_ids)):
        eligible = set().union(*(set(by_id[aid].analyst.eligible_classes) for aid in ids))
        classes = set(base.demand_profile["class_mix"])
        if eligible != classes:
            raise ValueError(f"{level} roster fails project coverage: {sorted(classes - eligible)}")
    return OrganizationConfig(resources, (
        TeamConfig("L1", tuple(l1_ids)), TeamConfig("L2", tuple(l2_ids)),
    ))


def _summarize(rows: list[dict]) -> dict:
    n = len(rows)
    counts = Counter(r["status"] for r in rows)
    completed = [r for r in rows if r["completion_h"] is not None]
    service = [r["service_h"] for r in completed if r["service_h"] is not None]
    wait = [r["wait_h"] for r in rows if r["wait_h"] is not None]
    response = [r["response_h"] for r in completed if r["response_h"] is not None]
    quality = [r["quality_proxy"] for r in rows]
    def p90(values):
        return sorted(values)[min(len(values) - 1, int(0.9 * (len(values) - 1)))] if values else None
    return {
        "n": n,
        "sla": {"within": counts["completed_within_sla"],
                "late": counts["completed_late"], "pending": counts["pending"]},
        "sla_within_fraction": counts["completed_within_sla"] / n if n else None,
        "mean_service_h": mean(service) if service else None,
        "p90_service_h": p90(service),
        "mean_wait_h": mean(wait) if wait else None,
        "p90_wait_h": p90(wait),
        "mean_response_h": mean(response) if response else None,
        "p90_response_h": p90(response),
        "mean_quality_proxy": mean(quality) if quality else None,
        "mean_quality_proxy_completed": mean(r["quality_proxy"] for r in completed) if completed else None,
        "mean_quality_proxy_within_sla": mean(
            r["quality_proxy"] for r in rows if r["status"] == "completed_within_sla"
        ) if counts["completed_within_sla"] else None,
    }


def _queue_samples(rows: list[dict], horizon: float, interval: float) -> list[dict]:
    arrival_times = sorted(r["arrival_h"] for r in rows)
    starts = sorted(r["start_h"] for r in rows if r["start_h"] is not None)
    count = int(round(horizon / interval))
    out = []
    for i in range(count + 1):
        t = i * interval
        arrived = bisect_right(arrival_times, t)
        started = bisect_right(starts, t)
        out.append(arrived - started)
    return out


def _episode(base, organization, triage, trace, trace_hash: str, seed: int,
             config_id: str, queue_interval: float) -> tuple[dict, dict]:
    variant = replace(triage, organization=organization)
    if variant.policies["L1"].name != "D1" or variant.policies["L2"].name != "P1":
        raise AssertionError("staffing diagnostic must hold D1/L1 and P1/L2 fixed")
    result = run_triage_flow(variant, flow_mode=base.flow_mode, backend=CalendarBackend())
    by_id = {row.routed.alert.alert_id: row for row in trace}
    outcome_by_id = {o.alert_id: o for o in result.outcomes}
    assignments = {
        a.alert_id: (level, a)
        for level, stage in result.stage_results.items()
        for a in stage.assignments
    }
    records_by_level: dict[str, list[dict]] = {"L1": [], "L2": []}
    for aid, row in by_id.items():
        outcome = outcome_by_id[aid]
        level, assignment = assignments[aid]
        task = result.stage_results[level].tasks_by_alert[aid]
        alert = row.routed.alert
        records_by_level[level].append({
            "alert_id": aid,
            "level": level,
            "class": str(alert.task_class),
            "severity": row.severity,
            "q": float(row.difficulty),
            "confusion": outcome.confusion,
            "arrival_h": float(alert.arrival),
            "deadline_h": float(alert.deadline),
            "analyst_id": assignment.analyst_id,
            "start_h": task.start,
            "completion_h": task.completion,
            "service_h": task.effective_work,
            "wait_h": task.start - alert.arrival if task.start is not None else None,
            "response_h": task.completion - alert.arrival if task.completion is not None else None,
            "status": outcome.status,
            "quality_proxy": float(assignment.competence) * (1.0 - 0.35 * float(row.difficulty)),
            "investigations": outcome.investigation_count,
        })

    level_results = {}
    per_analyst = {}
    queues = {}
    horizon = float(base.settings.admission_horizon)
    for level in ("L1", "L2"):
        records = records_by_level[level]
        stage = result.stage_results[level]
        segments = stage.work_segments or ()
        members = organization.resources_for(level)
        utilization = {}
        for resource in members:
            aid = resource.analyst.analyst_id
            work_h = sum(max(0.0, min(end, horizon) - max(start, 0.0))
                         for segment in segments if segment.analyst_id == aid
                         for start, end in ((segment.start, segment.end),))
            owned = [r for r in records if r["analyst_id"] == aid]
            utilization[aid] = {
                "active_work_h_admission": work_h,
                "available_work_h_admission": horizon,
                "utilization": work_h / horizon,
                "assigned_alerts": len(owned),
                "mean_service_h": mean(r["service_h"] for r in owned
                                         if r["completion_h"] is not None and r["service_h"] is not None)
                if any(r["completion_h"] is not None for r in owned) else None,
                "mean_wait_h": mean(r["wait_h"] for r in owned if r["wait_h"] is not None)
                if any(r["wait_h"] is not None for r in owned) else None,
                "mean_response_h": mean(r["response_h"] for r in owned if r["response_h"] is not None)
                if any(r["response_h"] is not None for r in owned) else None,
                "completed_alerts": sum(r["completion_h"] is not None for r in owned),
            }
        level_results[level] = _summarize(records)
        level_results[level]["route_rate_per_h"] = len(records) / horizon
        level_results[level]["aggregate_utilization"] = (
            sum(x["active_work_h_admission"] for x in utilization.values()) /
            (len(members) * horizon)
        )
        severity_results = {}
        for severity in ("high", "medium", "low"):
            severity_results[severity] = _summarize([r for r in records if r["severity"] == severity])
        level_results[level]["by_severity"] = severity_results
        per_analyst[level] = utilization
        queues[level] = _queue_samples(records, float(base.settings.evaluation_horizon), queue_interval)

    checks = {
        "same_trace_alert_count": len(trace) == len(result.outcomes),
        "one_investigation_per_alert": all(o.investigation_count == 1 for o in result.outcomes),
        "routes_match_recommendations": all(
            outcome.final_investigation_level == ("L2" if row.routed.soctra_recommendation else "L1")
            for aid, row in by_id.items() for outcome in (outcome_by_id[aid],)
        ),
        "deadline_preserved": all(
            isclose(outcome.deadline, by_id[aid].routed.alert.deadline, rel_tol=0, abs_tol=1e-12)
            for aid, outcome in outcome_by_id.items()
        ),
        "no_pending_at_cutoff": result.status_counts["pending"] == 0,
        "same_configured_policies": variant.policies["L1"].name == "D1" and variant.policies["L2"].name == "P1",
    }
    if not all(checks.values()):
        raise AssertionError(f"staffing episode invariants failed for {config_id}/{seed}: {checks}")
    episode = {
        "configuration": config_id,
        "seed": seed,
        "trace_sha256": trace_hash,
        "n_alerts": len(trace),
        "confusion": dict(Counter(o.confusion for o in result.outcomes)),
        "levels": level_results,
        "per_analyst": per_analyst,
        "max_sampled_queue": {level: max(values, default=0) for level, values in queues.items()},
        "mean_sampled_queue": {level: mean(values) if values else 0.0 for level, values in queues.items()},
        "late_or_pending_alerts": [
            row for level in ("L1", "L2") for row in records_by_level[level]
            if row["status"] != "completed_within_sla"
        ],
        "validation": checks,
    }
    return episode, queues


def _capacity_profile(base) -> CapacityDemandProfile:
    demand = base.demand_profile
    regime = demand["regimes"][0]
    return CapacityDemandProfile(
        regimes=(DemandRegime(regime["name"], regime["start_h"], regime["end_h"],
                              regime["arrival_rate_by_class"]),),
        prevalence_by_class=demand["prevalence_by_class"],
        sensitivity_by_class=demand["sensitivity_by_class"],
        false_positive_rate_by_class=demand["false_positive_rate_by_class"],
        alpha=demand["alpha"], beta=demand["beta"],
        difficulty_mean_by_class_and_need=demand.get("difficulty_mean_by_class_and_need"),
        gamma=demand["gamma"], flow_mode=base.flow_mode,
    )


def _mean_sd(values: list[float]) -> dict:
    if not values:
        return None
    return {"mean": mean(values), "sd_between_seeds": pstdev(values) if len(values) > 1 else 0.0,
            "min": min(values), "max": max(values)}


def _aggregate(episodes: list[dict], queue_matrices: dict[str, dict[str, list[list[int]]]],
               interval: float, evaluation_h: float) -> tuple[dict, dict]:
    summary, queue_profiles = {}, {}
    for config_id in sorted({episode["configuration"] for episode in episodes}):
        rows = [episode for episode in episodes if episode["configuration"] == config_id]
        summary[config_id] = {"episodes": len(rows), "n_alerts_mean": mean(r["n_alerts"] for r in rows),
                              "confusion_mean_count": {label: mean(r["confusion"].get(label, 0) for r in rows)
                                                       for label in ("TP", "FP", "TN", "FN")},
                              "levels": {}, "per_analyst": {}, "max_sampled_queue": {},
                              "mean_sampled_queue": {}}
        for level in ("L1", "L2"):
            level_rows = [r["levels"][level] for r in rows]
            keys = ("n", "route_rate_per_h", "aggregate_utilization", "sla_within_fraction",
                    "mean_service_h", "p90_service_h", "mean_wait_h", "p90_wait_h",
                    "mean_response_h", "p90_response_h", "mean_quality_proxy",
                    "mean_quality_proxy_completed", "mean_quality_proxy_within_sla")
            summary[config_id]["levels"][level] = {
                key: _mean_sd([float(r[key]) for r in level_rows if r[key] is not None])
                for key in keys
            }
            summary[config_id]["levels"][level]["sla_counts_mean"] = {
                label: mean(r["sla"][label] for r in level_rows)
                for label in ("within", "late", "pending")
            }
            summary[config_id]["levels"][level]["by_severity"] = {}
            for severity in ("high", "medium", "low"):
                severity_rows = [r["by_severity"][severity] for r in level_rows]
                summary[config_id]["levels"][level]["by_severity"][severity] = {
                    "n_mean": mean(r["n"] for r in severity_rows),
                    "within_sla_fraction_mean": mean(r["sla_within_fraction"] for r in severity_rows
                                                     if r["sla_within_fraction"] is not None),
                    "late_mean": mean(r["sla"]["late"] for r in severity_rows),
                    "pending_mean": mean(r["sla"]["pending"] for r in severity_rows),
                }
            summary[config_id]["max_sampled_queue"][level] = _mean_sd(
                [float(r["max_sampled_queue"][level]) for r in rows]
            )
            summary[config_id]["mean_sampled_queue"][level] = _mean_sd(
                [float(r["mean_sampled_queue"][level]) for r in rows]
            )
            analyst_ids = sorted({aid for r in rows for aid in r["per_analyst"][level]})
            summary[config_id]["per_analyst"][level] = {}
            for aid in analyst_ids:
                analyst_rows = [r["per_analyst"][level][aid] for r in rows if aid in r["per_analyst"][level]]
                summary[config_id]["per_analyst"][level][aid] = {
                    key: _mean_sd([float(r[key]) for r in analyst_rows if r[key] is not None])
                    for key in ("utilization", "assigned_alerts", "completed_alerts",
                                "mean_service_h", "mean_wait_h", "mean_response_h")
                }

        queue_profiles[config_id] = {}
        series = queue_matrices[config_id]
        steps = int(round(evaluation_h / interval)) + 1
        for level in ("L1", "L2"):
            profile = []
            for i in range(steps):
                observations = [matrix[i] for matrix in series[level]]
                ordered = sorted(observations)
                profile.append({
                    "time_h": i * interval,
                    "mean_queue": mean(observations),
                    "p95_queue": ordered[min(len(ordered) - 1, int(0.95 * (len(ordered) - 1)))],
                    "max_queue": max(observations),
                })
            queue_profiles[config_id][level] = profile
    return summary, queue_profiles


def run_study(study_config: Path = STUDY_CONFIG, base_config: Path = BASE_CONFIG) -> dict:
    study = json.loads(study_config.read_text(encoding="utf-8"))
    base_bytes = base_config.read_bytes()
    base_hash = _sha256(base_bytes)
    if base_hash != study["base_scenario_sha256"]:
        raise ValueError("CONOPS base JSON hash differs from the frozen staffing-sizing specification")
    base = load_scenario(base_config)
    if base.flow_mode != "triage_single_investigation":
        raise ValueError("staffing-sizing requires triage_single_investigation")
    demand = base.demand_profile
    if base.settings.admission_horizon <= 0 or base.settings.evaluation_horizon <= base.settings.admission_horizon:
        raise ValueError("scenario must have a positive admission horizon and later terminal cutoff")
    seeds = tuple(study["seed_block"]["seeds"])
    roster_profiles = study["roster_profiles"]
    profile_ids = {name: list(value["analyst_ids"]) for name, value in roster_profiles.items()}
    all_configs = study["configurations"]
    organizations = {}
    for config in all_configs:
        l1_ids = profile_ids[config["l1_profile"]]
        l2_ids = profile_ids[config["l2_profile"]]
        organizations[config["id"]] = build_organization(base, l1_ids, l2_ids)

    capacity_profile = _capacity_profile(base)
    capacities = {}
    for level, profiles in (("L1", ("L1_5", "L1_4", "L1_3")),
                             ("L2", ("L2_3", "L2_2", "L2_1"))):
        capacities[level] = {}
        for profile_name in profiles:
            for config in all_configs:
                if (config["l1_profile"] if level == "L1" else config["l2_profile"]) != profile_name:
                    continue
                organization = organizations[config["id"]]
                cap = assess_capacity(organization, capacity_profile)
                row = next(r for r in cap.regimes if r.level == level)
                capacities[level][profile_name] = {
                    "analyst_ids": profile_ids[profile_name],
                    "n_analysts": len(profile_ids[profile_name]),
                    "incoming_rate_per_h": row.offered_rate_per_h,
                    "offered_work_h_person_h": row.offered_l1_work_h_per_h + row.offered_l2_work_h_per_h,
                    "available_person_h_per_h": float(len(profile_ids[profile_name])),
                    "mean_workload_fraction_of_person_hours": (
                        (row.offered_l1_work_h_per_h + row.offered_l2_work_h_per_h) /
                        len(profile_ids[profile_name])
                    ),
                    "lp_assignable_capacity_alerts_per_h": row.capacity_per_h,
                    "lp_relative_load": row.relative_load,
                    "lp_status": row.load_status,
                    "uncovered_classes": list(row.unstaffed_classes),
                    "lp_utilization_at_assignable_capacity": dict(row.analyst_utilization_at_capacity),
                    "bottleneck_analysts": list(row.bottleneck_analysts),
                }
                break

    episodes = []
    queue_matrices: dict[str, dict[str, list[list[int]]]] = {
        config["id"]: {"L1": [], "L2": []} for config in all_configs
    }
    trace_hash_by_seed = {}
    trace_count_by_seed = {}
    for seed in seeds:
        triage, trace = base.triage_scenario_for(seed)
        trace_hash = trace_sha256(trace)
        trace_hash_by_seed[str(seed)] = trace_hash
        trace_count_by_seed[str(seed)] = len(trace)
        for config in all_configs:
            org = organizations[config["id"]]
            episode, queues = _episode(
                base, org, triage, trace, trace_hash, seed, config["id"],
                float(study["queue_sampling_interval_h"]),
            )
            episodes.append(episode)
            for level in ("L1", "L2"):
                queue_matrices[config["id"]][level].append(queues[level])

    summary, queue_profiles = _aggregate(
        episodes, queue_matrices, float(study["queue_sampling_interval_h"]),
        float(base.settings.evaluation_horizon),
    )
    return {
        "study_id": study["study_id"],
        "base_scenario": base_config.resolve().relative_to(ROOT.resolve()).as_posix(),
        "base_scenario_sha256": base_hash,
        "study_config": study_config.resolve().relative_to(ROOT.resolve()).as_posix(),
        "study_config_sha256": _sha256(study_config.read_bytes()),
        "flow_mode": base.flow_mode,
        "policies": {"L1": "D1", "L2": "P1"},
        "seeds": list(seeds),
        "n_configurations": len(all_configs),
        "n_episodes": len(episodes),
        "trace_count_by_seed": trace_count_by_seed,
        "trace_sha256_by_seed": trace_hash_by_seed,
        "all_configs_share_each_seed_trace": True,
        "capacity_by_team_profile": capacities,
        "episode_results": episodes,
        "summary_by_configuration": summary,
        "queue_profiles_15min": queue_profiles,
        "notes": [
            "Twelve paired seeded episodes per roster; each seed's trace is generated once and reused across all staffing combinations.",
            "LP capacity uses fractional assignment, class mix, eligibility, individual service, continuous calendars and conditional expected difficulty effort.",
            "Workload fraction of person-hours uses the existing average-service-over-eligible-analysts convention; it is distinct from LP assignable capacity and realized policy utilization.",
            "Per-analyst utilization is actual active work divided by 168 continuously available hours during admission; work completed during drain is excluded from that denominator.",
            "Quality is the simulator's modeled proxy, competence*(1-0.35*q), not an empirical probability of correct resolution.",
            "Queue lengths are exact at 15-minute sample instants; inter-sample peaks are not captured. SLA failures remain episode-level finite-trace outcomes.",
            "The L2 one-person profile is a capacity bound under idealized continuous availability, not a realistic 24x7 employment/coverage recommendation.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-config", type=Path, default=STUDY_CONFIG)
    parser.add_argument("--base-config", type=Path, default=BASE_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run_study(args.study_config, args.base_config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "episodes": result["n_episodes"],
                      "configurations": result["n_configurations"],
                      "trace_hashes": result["trace_sha256_by_seed"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
