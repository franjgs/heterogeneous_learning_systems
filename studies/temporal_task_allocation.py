"""Run the six small deterministic controls for temporal task allocation."""
from __future__ import annotations

from dataclasses import dataclass
from math import isclose

from hls.sequential_allocation import run_fixed_policy, run_greedy_online_policy
from hls.static_assignment import StaticAllocationModel
from hls.temporal_allocation import (
    run_effectiveness_load_temporal_policy,
    run_fixed_temporal_policy,
    run_max_effectiveness_temporal_policy,
)


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
        "Response mean", "Response P95", "Pending work", "Utilization (agents)", "Makespan",
    )
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        utilization = ",".join(f"{value:.3f}" for value in row["utilization_by_agent"])
        lines.append(
            f"| {row['scenario']} | {row['policy']} | {row['effectiveness_total']:.4f} "
            f"| {row['effectiveness_mean']:.4f} | {row['waiting_mean']:.4f} "
            f"| {row['waiting_p95']:.4f} | {row['response_mean']:.4f} | {row['response_p95']:.4f} "
            f"| {row['pending_work']:.4f} | {utilization} | {row['makespan']:.4f} |"
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
    results = run()
    print(_markdown_table(results))
    print("\n" + _p2_relative_changes(results))
    print("\nAll six cases are constructed deterministic controls, not SOCTRA outcomes.")
