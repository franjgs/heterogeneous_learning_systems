"""Run one reproducible configured scenario (not a comparative campaign)."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Mapping

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from studies.soc_triage_hls_availability_robustness.execution_api import CalendarBackend  # noqa: E402
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario  # noqa: E402
from studies.soc_triage_hls_availability_robustness.triage_execution import (  # noqa: E402
    FLOW_MODES, run_triage_flow,
)


DEFAULT_CONFIG = Path(__file__).with_name("config") / "SOC_REFERENCE_ORGANIZATION_V2_24X7.json"


def run_one(config_path: str | Path = DEFAULT_CONFIG, *, seed: int | None = None,
            policy: str | Mapping[str, str] | None = None, flow_mode: str | None = None) -> dict:
    scenario = load_scenario(config_path)
    selected_seed = scenario.seed_start if seed is None else int(seed)
    triage, trace = scenario.triage_scenario_for(selected_seed, policy=policy)
    selected_flow = flow_mode or scenario.flow_mode
    if selected_flow not in FLOW_MODES:
        raise ValueError(f"flow_mode must be one of {sorted(FLOW_MODES)}")
    result = run_triage_flow(triage, flow_mode=selected_flow,
                             backend=CalendarBackend())
    confusion = Counter(outcome.confusion for outcome in result.outcomes)
    statuses = result.status_counts
    route_counts = Counter(outcome.final_investigation_level for outcome in result.outcomes)
    alert_by_id = {alert.alert_id: alert for alert in triage.alerts}
    task_services = {
        level: sum(task.effective_work or 0.0 for task in stage.tasks_by_alert.values())
        for level, stage in result.stage_results.items()
    }
    completed = [x for x in result.outcomes if x.completion is not None and x.completion <= result.cutoff]
    response_times = [x.completion - alert_by_id[x.alert_id].arrival for x in completed]
    mean_wait_by_level = None
    started_by_level = None
    if selected_flow == "triage_single_investigation":
        mean_wait_by_level = {}
        started_by_level = {}
        for level, stage in result.stage_results.items():
            waits = [task.start - alert_by_id[aid].arrival
                     for aid, task in stage.tasks_by_alert.items()
                     if task.start is not None and aid in alert_by_id]
            mean_wait_by_level[level] = sum(waits) / len(waits) if waits else 0.0
            started_by_level[level] = len(waits)
    return {
        "scenario_id": scenario.scenario_id,
        "config": str(Path(config_path)),
        "seed": selected_seed,
        "flow_mode": selected_flow,
        "policy": policy or "per-level-configured-default",
        "backend": "CalendarBackend",
        "generated_alerts": len(trace),
        "class_counts": dict(Counter(row.routed.alert.task_class for row in trace)),
        "severity_counts": dict(Counter(row.severity for row in trace)),
        "confusion_counts": {key: confusion.get(key, 0) for key in ("TP", "FP", "TN", "FN")},
        "route_counts": dict(route_counts),
        "investigation_counts": dict(Counter(x.investigation_count for x in result.outcomes)),
        "sla_status_counts": dict(statuses),
        "sla_status_fractions": dict(result.status_fractions),
        "effective_service_work_h_by_stage": task_services,
        "mean_response_time_h_for_completed": sum(response_times) / len(response_times) if response_times else None,
        "mean_pre_service_wait_h_by_level": mean_wait_by_level,
        "service_start_count_by_level": started_by_level,
        "completed_count": len(completed),
        "pending_at_cutoff_count": statuses["pending"],
        "recommendation_acceptance": 1.0,
        "evaluation_cutoff_h": result.cutoff,
        "diagnostic_note": "single technical execution; not a policy comparison or scientific campaign",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--policy", choices=("D1", "P1", "WAPS"))
    parser.add_argument("--l1-policy", choices=("D1", "P1", "WAPS"),
                        help="override only L1; L2 keeps its configured policy")
    parser.add_argument("--l2-policy", choices=("D1", "P1", "WAPS"),
                        help="override only L2; L1 keeps its configured policy")
    parser.add_argument("--flow-mode", choices=sorted(FLOW_MODES))
    args = parser.parse_args()
    if args.policy and (args.l1_policy or args.l2_policy):
        parser.error("--policy cannot be combined with --l1-policy/--l2-policy")
    policy = args.policy
    if args.l1_policy or args.l2_policy:
        policy = {level: value for level, value in (("L1", args.l1_policy), ("L2", args.l2_policy))
                  if value is not None}
    print(json.dumps(run_one(args.config, seed=args.seed, policy=policy,
                             flow_mode=args.flow_mode), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
