"""Run the six small deterministic controls for temporal task allocation."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from math import isclose, fsum
from statistics import median

from hls.sequential_allocation import run_fixed_policy, run_greedy_online_policy
from hls.static_assignment import StaticAllocationModel
from hls.temporal_allocation import (
    ArrivalTask,
    run_effectiveness_load_temporal_policy,
    run_fixed_temporal_policy,
    run_max_effectiveness_temporal_policy,
)


SENSITIVITY_EFFECTIVENESS = {
    "H0_homogeneous": ((0.6, 0.6), (0.6, 0.6)),
    "H1_moderate_crossed": ((0.8, 0.4), (0.4, 0.8)),
    "H2_marked_specialization": ((1.0, 0.2), (0.2, 1.0)),
    "H3_agent_dominance": ((0.9, 0.8), (0.4, 0.2)),
}
SENSITIVITY_DEMANDS = ("D0_distributed", "D1_balanced_bursts", "D2_class_concentrated_bursts", "D3_mixture_shift")
SENSITIVITY_AGENT_COUNTS = (2, 4)
SENSITIVITY_HORIZONS = (24.0, 48.0, 96.0)
SENSITIVITY_TASK_COUNT = 48
SENSITIVITY_SERVICE_TIMES = (1.0, 1.0)
NOMINAL_CLASS_MIX = (0.75, 0.25)
FOCUSED_ORGANIZATIONS = {
    "R1_equivalent": ((0.7, 0.7), (0.7, 0.7)),
    "R2_crossed_specialization": ((0.9, 0.3), (0.3, 0.9)),
    "R3_moderate_specialization": ((0.8, 0.55), (0.55, 0.8)),
    "R4_dominant_worker": ((0.9, 0.8), (0.4, 0.3)),
    "R5_partial_polyvalence": ((0.8, 0.72), (0.45, 0.85)),
}
FOCUSED_DEMANDS = {
    "balanced_simultaneous": tuple((0.0, k) for k in (0, 1) * 12),
    "class0_concentrated": tuple((0.0, 0) for _ in range(24)),
}


@dataclass(frozen=True)
class Scenario:
    name: str
    arrivals: tuple[tuple[float, int], ...]
    effectiveness: tuple[tuple[float, ...], ...]
    service_times: tuple[float, ...]
    horizon: float
    type_to_agent: tuple[int, ...]


def scenarios() -> tuple[Scenario, ...]:
    crossed = ((1.0, 0.2), (0.2, 1.0))
    return (
        Scenario(
            "S1_spaced_arrivals",
            tuple((2.0 * index, index % 2) for index in range(6)),
            crossed, (1.0, 1.0), 12.0, (0, 1),
        ),
        Scenario(
            "S2_balanced_bursts",
            tuple((0.0 if i < 4 else 2.0, i % 2) for i in range(8)),
            crossed, (1.0, 1.0), 3.0, (0, 1),
        ),
        Scenario(
            "S3_concentrated_class_burst",
            tuple((0.0, 0) for _ in range(12)),
            crossed, (1.0, 1.0), 1.0, (0, 1),
        ),
        Scenario(
            "S4_cross_specialization_block_demand",
            tuple((0.0, task_type) for task_type in (0,) * 8 + (1,) * 4),
            crossed, (1.0, 1.0), 1.0, (0, 1),
        ),
        Scenario(
            "S5_homogeneous_effectiveness",
            tuple((0.2 * i, i % 2) for i in range(8)),
            ((0.7, 0.4), (0.7, 0.4)), (1.0, 1.0), 2.0, (0, 0),
        ),
        Scenario(
            "S6_agent_dominance",
            tuple((0.2 * i, i % 2) for i in range(10)),
            ((0.9, 0.8), (0.4, 0.2)), (1.0, 1.0), 2.0, (0, 0),
        ),
    )


def _sensitivity_matrix(profile: str, n_agents: int) -> tuple[tuple[float, ...], ...]:
    base = SENSITIVITY_EFFECTIVENESS[profile]
    if n_agents == 2:
        return base
    if n_agents == 4:
        if profile == "H3_agent_dominance":
            return (base[0], base[1], base[1], base[1])
        return (base[0], base[1], base[0], base[1])
    raise ValueError("sensitivity design supports N=2 or N=4")


def _sensitivity_arrivals(profile: str, horizon: float) -> tuple[tuple[float, int], ...]:
    count = SENSITIVITY_TASK_COUNT
    if profile == "D0_distributed":
        return tuple((horizon * (i + 0.5) / count, i % 2) for i in range(count))
    if profile in {"D1_balanced_bursts", "D2_class_concentrated_bursts"}:
        window = horizon / 12.0
        bursts = []
        for burst, start_fraction in enumerate((0.125, 0.625)):
            for j in range(count // 2):
                time = horizon * start_fraction + (j + 0.5) * window / (count // 2)
                task_type = 0 if profile == "D2_class_concentrated_bursts" else j % 2
                bursts.append((time, task_type))
        return tuple(sorted(bursts))
    if profile == "D3_mixture_shift":
        return tuple(
            (horizon * (i + 0.5) / count, 0 if i < count // 2 else 1)
            for i in range(count)
        )
    raise ValueError(f"unknown demand profile: {profile}")


def _fixed_mapping_variants(
    profile: str, matrix: tuple[tuple[float, ...], ...]
) -> dict[str, tuple[int, ...]]:
    n_agents = len(matrix)
    # Responsibility by class, declared from the competence profile before
    # test demand. In H0, the balanced (0,1) roster is a fixed organization.
    if profile == "H0_homogeneous":
        by_class = (0, 1)
    else:
        by_class = tuple(
            max(range(n_agents), key=lambda agent: matrix[agent][task_type])
            for task_type in range(2)
        )
    duty_roster = (0, 1)
    owner = max(
        range(n_agents),
        key=lambda agent: fsum(
            NOMINAL_CLASS_MIX[k] * matrix[agent][k] for k in range(2)
        ),
    )
    return {
        "P0_class_responsibility": by_class,
        "P0_fixed_duty_roster": duty_roster,
        "P0_nominal_mix_owner_75_25": (owner, owner),
    }


def _peak_window_load(arrivals: tuple[tuple[float, int], ...], horizon: float, n_agents: int) -> float:
    """Maximum offered work / available server-work in any H/12 window."""
    width = horizon / 12.0
    times = [time for time, _ in arrivals]
    maximum = 0
    for left in times:
        right = left + width
        maximum = max(maximum, sum(left <= time < right - 1e-12 * horizon for time in times))
    return maximum / (n_agents * width)


def _relative_change(value: float, baseline: float) -> float | None:
    return 100.0 * (value - baseline) / baseline if baseline != 0 else None


def run_focused_organizations() -> tuple[dict[str, object], ...]:
    """Compare five two-agent organization profiles on two matched bursts."""
    rows: list[dict[str, object]] = []
    for organization, matrix in FOCUSED_ORGANIZATIONS.items():
        if organization == "R1_equivalent":
            fixed_mapping = (0, 1)  # predeclared split to avoid the P1 tie-to-0 roster
        else:
            fixed_mapping = tuple(
                max(range(len(matrix)), key=lambda agent: matrix[agent][task_type])
                for task_type in range(2)
            )
        for demand, arrivals in FOCUSED_DEMANDS.items():
            results = (
                run_fixed_temporal_policy(arrivals, matrix, (1.0, 1.0), 24.0, fixed_mapping),
                run_max_effectiveness_temporal_policy(arrivals, matrix, (1.0, 1.0), 24.0),
                run_effectiveness_load_temporal_policy(arrivals, matrix, (1.0, 1.0), 24.0),
            )
            for result in results:
                rows.append({
                    "organization": organization,
                    "demand": demand,
                    "fixed_mapping": fixed_mapping,
                    "policy": result.policy,
                    "effectiveness_total": result.total_effectiveness,
                    "effectiveness_mean": result.mean_effectiveness,
                    "response_mean": result.mean_response_time,
                    "response_p95": result.p95_response_time,
                    "assigned_count_by_agent": result.assigned_count_by_agent,
                    "pending_tasks": result.pending_task_count,
                    "pending_work": result.pending_work_at_horizon,
                    "utilization_by_agent": result.utilization_by_agent,
                })
    return tuple(rows)


def _focused_report(rows: tuple[dict[str, object], ...]) -> str:
    headers = (
        "Organization", "Demand", "Policy", "Fixed map", "Effect mean", "Response mean",
        "Response P95", "Tasks/agent", "Pending tasks", "Pending work", "Utilization",
    )
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in rows:
        lines.append(
            f"| {row['organization']} | {row['demand']} | {row['policy']} | {row['fixed_mapping']} "
            f"| {row['effectiveness_mean']:.4f} | {row['response_mean']:.4f} | {row['response_p95']:.4f} "
            f"| {row['assigned_count_by_agent']} | {row['pending_tasks']} | {row['pending_work']:.4f} "
            f"| {row['utilization_by_agent']} |"
        )
    lines.append("\nSynthetic fixed-control study only; no SOCTRA operational parameters are inferred.")
    return "\n".join(lines)


def run_sensitivity() -> dict[str, object]:
    """Evaluate a fixed deterministic H×D×N×horizon grid, paired by cell."""
    rows: list[dict[str, object]] = []
    contrasts: list[dict[str, object]] = []
    cells = 0
    for h_profile in SENSITIVITY_EFFECTIVENESS:
        for d_profile in SENSITIVITY_DEMANDS:
            for n_agents in SENSITIVITY_AGENT_COUNTS:
                matrix = _sensitivity_matrix(h_profile, n_agents)
                fixed_variants = _fixed_mapping_variants(h_profile, matrix)
                for horizon in SENSITIVITY_HORIZONS:
                    arrivals = _sensitivity_arrivals(d_profile, horizon)
                    service_total = fsum(SENSITIVITY_SERVICE_TIMES[k] for _, k in arrivals)
                    rho_offered = service_total / (n_agents * horizon)
                    rho_peak = _peak_window_load(arrivals, horizon, n_agents)
                    load_band = "low" if rho_offered <= 0.25 else "intermediate" if rho_offered <= 0.5 else "high"
                    cell = f"{h_profile}|{d_profile}|N{n_agents}|H{horizon:g}"
                    cells += 1

                    p1 = run_max_effectiveness_temporal_policy(
                        arrivals, matrix, SENSITIVITY_SERVICE_TIMES, horizon
                    )
                    p2 = run_effectiveness_load_temporal_policy(
                        arrivals, matrix, SENSITIVITY_SERVICE_TIMES, horizon
                    )
                    p1_upper = fsum(max(row[k] for row in matrix) for _, k in arrivals)
                    assert isclose(p1.total_effectiveness, p1_upper)
                    assert p1.total_effectiveness + 1e-12 >= p2.total_effectiveness

                    policy_results = {"P1_max_effectiveness": p1, "P2_effectiveness_load": p2}
                    fixed_results: dict[str, object] = {}
                    by_mapping: dict[tuple[int, ...], list[str]] = {}
                    for label, mapping in fixed_variants.items():
                        by_mapping.setdefault(mapping, []).append(label)
                    for mapping, labels in by_mapping.items():
                        label = "+".join(labels)
                        result = run_fixed_temporal_policy(
                            arrivals, matrix, SENSITIVITY_SERVICE_TIMES, horizon, mapping
                        )
                        fixed_results[label] = result
                        policy_results[label] = result

                    for label, result in policy_results.items():
                        rows.append({
                            "cell": cell,
                            "heterogeneity": h_profile,
                            "demand": d_profile,
                            "agents": n_agents,
                            "horizon": horizon,
                            "rho_offered": rho_offered,
                            "load_band": load_band,
                            "rho_peak_window": rho_peak,
                            "temporal_overload": rho_peak > 1.0,
                            "policy": label,
                            "effectiveness_mean": result.mean_effectiveness,
                            "effectiveness_total": result.total_effectiveness,
                            "response_mean": result.mean_response_time,
                            "response_p95": result.p95_response_time,
                            "waiting_mean": result.mean_waiting_time,
                            "waiting_p95": result.p95_waiting_time,
                            "pending_tasks": result.pending_task_count,
                            "pending_work": result.pending_work_at_horizon,
                            "assigned_count_by_agent": result.assigned_count_by_agent,
                            "effectiveness_by_agent": result.effectiveness_by_agent,
                            "mean_effectiveness_by_agent": result.mean_effectiveness_by_agent,
                            "utilization": result.utilization_by_agent,
                            "makespan": result.makespan,
                        })

                    # P2-P1 is one contrast per scenario. P0 comparisons are
                    # repeated only for distinct predeclared fixed mappings.
                    contrasts.append({
                        "cell": cell,
                        "heterogeneity": h_profile,
                        "demand": d_profile,
                        "agents": n_agents,
                        "horizon": horizon,
                        "rho_offered": rho_offered,
                        "rho_peak_window": rho_peak,
                        "contrast": "P2-P1",
                        "delta_effectiveness_mean": p2.mean_effectiveness - p1.mean_effectiveness,
                        "relative_effectiveness_percent": _relative_change(p2.mean_effectiveness, p1.mean_effectiveness),
                        "delta_response_mean": p2.mean_response_time - p1.mean_response_time,
                        "relative_response_percent": _relative_change(p2.mean_response_time, p1.mean_response_time),
                        "delta_response_p95": p2.p95_response_time - p1.p95_response_time,
                    })
                    for p0_label, p0 in fixed_results.items():
                        for alias in p0_label.split("+"):
                            for left_label, left, right_label, right in (
                                ("P1", p1, alias, p0),
                                ("P2", p2, alias, p0),
                            ):
                                contrasts.append({
                                    "cell": cell,
                                    "heterogeneity": h_profile,
                                    "demand": d_profile,
                                    "agents": n_agents,
                                    "horizon": horizon,
                                    "rho_offered": rho_offered,
                                    "rho_peak_window": rho_peak,
                                    "contrast": f"{left_label}-{right_label}",
                                    "delta_effectiveness_mean": left.mean_effectiveness - right.mean_effectiveness,
                                    "relative_effectiveness_percent": _relative_change(left.mean_effectiveness, right.mean_effectiveness),
                                    "delta_response_mean": left.mean_response_time - right.mean_response_time,
                                    "relative_response_percent": _relative_change(left.mean_response_time, right.mean_response_time),
                                    "delta_response_p95": left.p95_response_time - right.p95_response_time,
                                })

    assert cells == 4 * 4 * 2 * len(SENSITIVITY_HORIZONS)
    return {"cells": cells, "policy_rows": tuple(rows), "contrasts": tuple(contrasts)}


def _sensitivity_report(result: dict[str, object]) -> str:
    rows = result["policy_rows"]
    contrasts = result["contrasts"]
    p2p1 = [row for row in contrasts if row["contrast"] == "P2-P1"]
    faster = [row for row in p2p1 if row["delta_response_mean"] < -1e-12]
    slower = [row for row in p2p1 if row["delta_response_mean"] > 1e-12]
    same = len(p2p1) - len(faster) - len(slower)
    effect_deltas = [row["delta_effectiveness_mean"] for row in p2p1]
    response_changes = [row["relative_response_percent"] for row in p2p1]
    overload_cells = {
        row["cell"] for row in rows if row["temporal_overload"]
    }

    lines = [
        f"Deterministic sensitivity grid: {result['cells']} scenario cells; {len(rows)} policy rows; {len(contrasts)} paired contrasts.",
        "P2-P1 over cells: response faster/same/slower = "
        f"{len(faster)}/{same}/{len(slower)}; median response change = "
        f"{median(response_changes):+.2f}%; range = [{min(response_changes):+.2f}%, {max(response_changes):+.2f}%].",
        f"P2-P1 mean-effectiveness difference range = [{min(effect_deltas):+.4f}, {max(effect_deltas):+.4f}] (absolute contribution per task).",
        f"Transiently overloaded cells (peak H/12 offered ratio > 1): {len(overload_cells)} of {result['cells']}; these are offered-load indicators, not observed utilization.",
        "",
        "P2-P1 descriptive summary by heterogeneity profile:",
        "| H profile | Cells | faster/same/slower | Median response change | Effect difference range |",
        "|---|---:|---:|---:|---:|",
    ]
    for profile in SENSITIVITY_EFFECTIVENESS:
        group = [row for row in p2p1 if row["heterogeneity"] == profile]
        changes = [row["relative_response_percent"] for row in group]
        group_faster = sum(row["delta_response_mean"] < -1e-12 for row in group)
        group_slower = sum(row["delta_response_mean"] > 1e-12 for row in group)
        group_same = len(group) - group_faster - group_slower
        group_effect = [row["delta_effectiveness_mean"] for row in group]
        lines.append(
            f"| {profile} | {len(group)} | {group_faster}/{group_same}/{group_slower} "
            f"| {median(changes):+.2f}% | [{min(group_effect):+.3f}, {max(group_effect):+.3f}] |"
        )

    lines += [
        "",
        "P2-P1 descriptive summary by demand profile:",
        "| Demand | Cells | faster/same/slower | Median response change | Effect difference range |",
        "|---|---:|---:|---:|---:|",
    ]
    for profile in SENSITIVITY_DEMANDS:
        group = [row for row in p2p1 if row["demand"] == profile]
        changes = [row["relative_response_percent"] for row in group]
        group_faster = sum(row["delta_response_mean"] < -1e-12 for row in group)
        group_slower = sum(row["delta_response_mean"] > 1e-12 for row in group)
        group_same = len(group) - group_faster - group_slower
        group_effect = [row["delta_effectiveness_mean"] for row in group]
        lines.append(
            f"| {profile} | {len(group)} | {group_faster}/{group_same}/{group_slower} "
            f"| {median(changes):+.2f}% | [{min(group_effect):+.3f}, {max(group_effect):+.3f}] |"
        )

    lines += [
        "",
        "P2-P1 by offered-load band and workforce size (descriptive grid cells, not statistical replicates):",
        "| N | Offered-load band | Cells | Faster/same/slower | Median response change |",
        "|---:|---|---:|---:|---:|",
    ]
    for n_agents in SENSITIVITY_AGENT_COUNTS:
        for band in ("low", "intermediate", "high"):
            cell_ids = {
                row["cell"] for row in rows
                if row["agents"] == n_agents and row["load_band"] == band
            }
            group = [row for row in p2p1 if row["cell"] in cell_ids]
            if not group:
                continue
            changes = [row["relative_response_percent"] for row in group]
            group_faster = sum(row["delta_response_mean"] < -1e-12 for row in group)
            group_slower = sum(row["delta_response_mean"] > 1e-12 for row in group)
            group_same = len(group) - group_faster - group_slower
            lines.append(
                f"| {n_agents} | {band} | {len(group)} | {group_faster}/{group_same}/{group_slower} "
                f"| {median(changes):+.2f}% |"
            )

    lines += [
        "",
        "Fixed baselines (each mapping was declared from the profile/nominal mix before test traces):",
        "| P0 mapping | P1 greater effectiveness | P2 faster response | P2 lower/equal/higher effectiveness vs P0 |",
        "|---|---:|---:|---:|",
    ]
    for label in ("P0_class_responsibility", "P0_fixed_duty_roster", "P0_nominal_mix_owner_75_25"):
        relevant = [row for row in contrasts if row["contrast"] == f"P1-{label}"]
        if not relevant:
            continue
        p2_vs = [row for row in contrasts if row["contrast"] == f"P2-{label}"]
        p1_better = sum(row["delta_effectiveness_mean"] > 1e-12 for row in relevant)
        p2_faster = sum(row["delta_response_mean"] < -1e-12 for row in p2_vs)
        low = sum(row["delta_effectiveness_mean"] < -1e-12 for row in p2_vs)
        equal = sum(abs(row["delta_effectiveness_mean"]) <= 1e-12 for row in p2_vs)
        high = sum(row["delta_effectiveness_mean"] > 1e-12 for row in p2_vs)
        lines.append(f"| {label} | {p1_better}/{len(relevant)} | {p2_faster}/{len(p2_vs)} | {low}/{equal}/{high} |")

    row_lookup = {(row["cell"], row["policy"]): row for row in rows}
    p0_slower = [
        row for row in contrasts
        if row["contrast"] == "P2-P0_fixed_duty_roster"
        and row["delta_response_mean"] > 1e-12
    ]
    lines += [
        "",
        "Cells where fixed duty-roster P0 has lower mean response than P2:",
        "| Cell | P0 mapping | Policy | Effect mean/total | Response mean/P95 | Tasks/agent | Pending tasks/work | Utilization |",
        "|---|---|---|---:|---:|---|---|---|",
    ]
    for contrast in p0_slower:
        for policy in ("P0_fixed_duty_roster", "P1_max_effectiveness", "P2_effectiveness_load"):
            row = row_lookup[(contrast["cell"], policy)]
            lines.append(
                f"| {row['cell']} | (0, 1) | {policy} | {row['effectiveness_mean']:.4f}/{row['effectiveness_total']:.4f} "
                f"| {row['response_mean']:.4f}/{row['response_p95']:.4f} | {row['assigned_count_by_agent']} "
                f"| {row['pending_tasks']}/{row['pending_work']:.4f} | {row['utilization']} |"
            )

    worst = sorted(p2p1, key=lambda row: row["relative_response_percent"], reverse=True)[:3]
    lines += ["", "Largest P2 response-time worsenings relative to P1:"]
    if worst and worst[0]["relative_response_percent"] > 1e-12:
        for row in worst:
            if row["relative_response_percent"] > 1e-12:
                lines.append(
                    f"- {row['cell']}: {row['relative_response_percent']:+.2f}% response, "
                    f"effectiveness difference {row['delta_effectiveness_mean']:+.4f}."
                )
    else:
        lines.append("- None in this declared parameter grid.")
    lines.append("\nAll profiles, demand traces, service times and policies are synthetic deterministic controls; no SOC values are inferred.")
    return "\n".join(lines)


def run() -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for scenario in scenarios():
        results = (
            run_fixed_temporal_policy(
                scenario.arrivals, scenario.effectiveness, scenario.service_times,
                scenario.horizon, scenario.type_to_agent,
            ),
            run_max_effectiveness_temporal_policy(
                scenario.arrivals, scenario.effectiveness, scenario.service_times,
                scenario.horizon,
            ),
            run_effectiveness_load_temporal_policy(
                scenario.arrivals, scenario.effectiveness, scenario.service_times,
                scenario.horizon,
            ),
        )
        p1 = results[1]
        taskwise_max = sum(max(row[k] for row in scenario.effectiveness) for _, k in scenario.arrivals)
        assert isclose(p1.total_effectiveness, taskwise_max)
        assert all(p1.total_effectiveness + 1e-12 >= result.total_effectiveness for result in results)

        for result in results:
            rows.append({
                "scenario": scenario.name,
                "policy": result.policy,
                "effectiveness_mean": result.mean_effectiveness,
                "effectiveness_total": result.total_effectiveness,
                "response_mean": result.mean_response_time,
                "response_p95": result.p95_response_time,
                "waiting_mean": result.mean_waiting_time,
                "waiting_p95": result.p95_waiting_time,
                "pending_tasks": result.pending_task_count,
                "pending_work": result.pending_work_at_horizon,
                "utilization_by_agent": result.utilization_by_agent,
                "agent_sequence": tuple(d.agent_index for d in result.decisions),
                "makespan": result.makespan,
            })

    # Direct compatibility controls with the finite HLS-01 contract.
    task_types = (0, 1) * 5
    matrix = ((1.0, 0.2), (0.2, 1.0))
    static = StaticAllocationModel(1.0, 0.2, 0.2, 1.0).evaluate(0.5)
    sequential_fixed = run_fixed_policy(task_types, matrix, (10, 10), (0, 1))
    sequential_greedy = run_greedy_online_policy(task_types, matrix, (10, 10))
    temporal_control = run_fixed_temporal_policy(
        tuple((float(t), k) for t, k in enumerate(task_types)), matrix,
        (1.0, 1.0), 10.0, (0, 1),
    )
    assert isclose(sequential_fixed.mean_effectiveness, static.best_taskwise_effectiveness)
    assert isclose(sequential_greedy.mean_effectiveness, static.best_taskwise_effectiveness)
    assert isclose(temporal_control.mean_effectiveness, sequential_fixed.mean_effectiveness)

    by_scenario: dict[str, dict[str, dict[str, object]]] = {}
    for row in rows:
        by_scenario.setdefault(row["scenario"], {})[row["policy"]] = row
    for name in by_scenario:
        fixed, p1, p2 = (by_scenario[name][key] for key in ("fixed", "max_effectiveness", "effectiveness_load_ratio"))
        assert fixed["agent_sequence"] == p1["agent_sequence"]
    for name in ("S1_spaced_arrivals", "S2_balanced_bursts"):
        _, p1, p2 = (by_scenario[name][key] for key in ("fixed", "max_effectiveness", "effectiveness_load_ratio"))
        assert isclose(p1["effectiveness_mean"], p2["effectiveness_mean"])
        assert isclose(p1["response_mean"], p2["response_mean"])
    concentrated_p1 = by_scenario["S3_concentrated_class_burst"]["max_effectiveness"]
    concentrated_p2 = by_scenario["S3_concentrated_class_burst"]["effectiveness_load_ratio"]
    assert concentrated_p2["effectiveness_mean"] < concentrated_p1["effectiveness_mean"]
    assert concentrated_p2["response_mean"] < concentrated_p1["response_mean"]
    return tuple(rows)


def _markdown_table(rows: tuple[dict[str, object], ...]) -> str:
    headers = (
        "Scenario", "Policy", "Effect total", "Effect mean", "Wait mean", "Wait P95",
        "Response mean", "Response P95", "Pending tasks", "Pending work (time)",
        "Utilization (agents)", "Makespan",
    )
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        utilization = ",".join(f"{value:.3f}" for value in row["utilization_by_agent"])
        lines.append(
            f"| {row['scenario']} | {row['policy']} | {row['effectiveness_total']:.4f} "
            f"| {row['effectiveness_mean']:.4f} | {row['waiting_mean']:.4f} "
            f"| {row['waiting_p95']:.4f} | {row['response_mean']:.4f} | {row['response_p95']:.4f} "
            f"| {row['pending_tasks']} | {row['pending_work']:.4f} | {utilization} | {row['makespan']:.4f} |"
        )
    return "\n".join(lines)


def _p2_relative_changes(rows: tuple[dict[str, object], ...]) -> str:
    lines = ["P2 relative to P1 (%): effectiveness mean and response mean"]
    for scenario in scenarios():
        subset = [row for row in rows if row["scenario"] == scenario.name]
        p1 = next(row for row in subset if row["policy"] == "max_effectiveness")
        p2 = next(row for row in subset if row["policy"] == "effectiveness_load_ratio")
        effect_change = 100 * (p2["effectiveness_mean"] - p1["effectiveness_mean"]) / p1["effectiveness_mean"]
        response_change = 100 * (p2["response_mean"] - p1["response_mean"]) / p1["response_mean"]
        lines.append(f"- {scenario.name}: effectiveness {effect_change:+.2f}%; response {response_change:+.2f}%")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sensitivity", action="store_true",
        help="run the deterministic H×D×N×horizon sensitivity grid",
    )
    parser.add_argument(
        "--focused-organizations", action="store_true",
        help="compare five fixed-effectiveness organizations on two matched bursts",
    )
    args = parser.parse_args()
    if args.sensitivity and args.focused_organizations:
        parser.error("choose only one optional study mode")
    if args.focused_organizations:
        print(_focused_report(run_focused_organizations()))
    elif args.sensitivity:
        print(_sensitivity_report(run_sensitivity()))
    else:
        results = run()
        print(_markdown_table(results))
        print("\n" + _p2_relative_changes(results))
        print("\nAll six cases are constructed deterministic controls, not SOCTRA outcomes.")
