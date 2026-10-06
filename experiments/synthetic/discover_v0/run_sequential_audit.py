"""Write derived sequential-DP diagnostics for frozen DISCOVER-v0."""

from __future__ import annotations

import csv
import json
from math import isclose
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.discover_v0 import DEFAULT_HORIZON, JOINT_ACTIONS, enumerate_canonical_states, evaluate_state  # noqa: E402
from hls.discover_v0_sequential import SequentialDiscoverAudit, entropy  # noqa: E402

OUTPUT = ROOT / "results" / "foundations" / "discover_v0"


def _action_text(action):
    return ";".join(f"({left:g},{right:g})" for left, right in action)


def _write(rows, path):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _weighted_quantile(nodes, quantile):
    ordered = sorted(nodes, key=lambda item: item[0])
    total, threshold, cumulative = sum(mass for _, mass in ordered), quantile * sum(mass for _, mass in ordered), 0.0
    for belief, mass in ordered:
        cumulative += mass
        if cumulative + 1e-15 >= threshold:
            return belief
    return ordered[-1][0]


def _correlation(left, right):
    return None if len(set(left)) < 2 or len(set(right)) < 2 else float(np.corrcoef(left, right)[0, 1])


def run(*, output: Path = OUTPUT):
    states = enumerate_canonical_states()
    decomposition, trajectories, summaries = [], [], []
    for index, state in enumerate(states):
        identifier = f"S{index:03d}"
        evaluation = evaluate_state(state)
        audit = SequentialDiscoverAudit(state)
        if not isclose(audit.value(audit.horizon, audit.prior), evaluation.unknown_value, abs_tol=1e-10):
            raise AssertionError("sequential audit must reproduce DISCOVER-v0 UNKNOWN value")
        nodes, _ = audit.audit()
        by_time = {}
        for mass, decision in nodes:
            time = audit.horizon - decision.remaining
            by_time.setdefault(time, []).append((mass, decision))
            immediate_values = audit.immediate_values(decision.belief)
            for action in decision.actions:
                immediate = immediate_values[action]
                future = audit.continuation(decision.remaining, decision.belief, action)
                noinfo = decision.noinfo
                experiment_cost = decision.immediate_max - immediate
                voi = future - noinfo
                value = immediate + future
                decomposition.append({
                    "configuration_id": identifier, "time": time, "remaining_horizon": decision.remaining,
                    "node_probability": mass, "belief": decision.belief, "action": _action_text(action),
                    "optimal_tie_count": len(decision.actions), "mu_theta1": audit.action_means[action][0], "mu_theta2": audit.action_means[action][1],
                    "g": immediate, "g_max": decision.immediate_max, "c_exp": experiment_cost,
                    "Q_future": future, "Q_noinfo": noinfo, "VOI": voi, "Q": value,
                    "V_h": decision.value, "bellman_residual": decision.value - value,
                    "cost_voi_residual": (value - (decision.immediate_max + noinfo)) - (-experiment_cost + voi),
                })
        total_experiment_cost = total_voi = recovered_after_learning = 0.0
        initial_immediate_max = max(audit.immediate_values(audit.prior).values())
        for time in range(audit.horizon):
            entries = by_time[time]
            aggregate = {"belief": sum(mass * d.belief for mass, d in entries), "entropy": sum(mass * entropy(d.belief) for mass, d in entries), "abs_center": sum(mass * abs(d.belief - .5) for mass, d in entries)}
            action_mass = {action: 0.0 for action in JOINT_ACTIONS}
            reward = cost = voi = 0.0
            for mass, decision in entries:
                values = audit.immediate_values(decision.belief)
                for action in decision.actions:
                    selected_mass = mass / len(decision.actions)
                    immediate, future = values[action], audit.continuation(decision.remaining, decision.belief, action)
                    action_mass[action] += selected_mass
                    reward += selected_mass * immediate
                    cost += selected_mass * (decision.immediate_max - immediate)
                    voi += selected_mass * (future - decision.noinfo)
            total_experiment_cost += cost
            total_voi += voi
            if time:
                recovered_after_learning += reward - initial_immediate_max
            posterior_nodes = {}
            for mass, decision in entries:
                for belief, child_mass in audit.child_nodes(decision):
                    posterior_nodes[belief] = posterior_nodes.get(belief, 0.0) + mass * child_mass
            for action in JOINT_ACTIONS:
                trajectories.append({
                    "configuration_id": identifier, "time": time, "action": _action_text(action), "selection_probability": action_mass[action],
                    "E_belief": aggregate["belief"], "E_entropy": aggregate["entropy"], "E_abs_belief_minus_half": aggregate["abs_center"],
                    "belief_q05_after_action": _weighted_quantile(list(posterior_nodes.items()), .05), "belief_q50_after_action": _weighted_quantile(list(posterior_nodes.items()), .5), "belief_q95_after_action": _weighted_quantile(list(posterior_nodes.items()), .95),
                    "E_reward": reward, "E_c_exp": cost, "E_VOI": voi,
                })
        final_nodes = [(audit.prior, 1.0)]
        for time in range(audit.horizon):
            next_nodes = {}
            for mass, decision in by_time[time]:
                for belief, child_mass in audit.child_nodes(decision):
                    next_nodes[belief] = next_nodes.get(belief, 0.0) + mass * child_mass
            final_nodes = list(next_nodes.items())
        summaries.append({
            "configuration_id": identifier, "V_K": evaluation.known_value, "V_U": evaluation.unknown_value, "C_D": evaluation.discovery_cost,
            "expected_c_exp_total": total_experiment_cost, "local_VOI_sum": total_voi,
            "expected_entropy_reduction": entropy(audit.prior) - sum(mass * entropy(belief) for belief, mass in final_nodes),
            "recovered_reward_after_learning": recovered_after_learning,
            "final_E_abs_belief_minus_half": sum(mass * abs(belief - .5) for belief, mass in final_nodes),
        })
    pairs = []
    for left_index, left in enumerate(summaries):
        for right in summaries[left_index + 1:]:
            row = {"configuration_a": left["configuration_id"], "configuration_b": right["configuration_id"]}
            for field in ("V_K", "C_D", "expected_c_exp_total", "local_VOI_sum", "expected_entropy_reduction", "recovered_reward_after_learning"):
                row[f"Delta_{field}"] = abs(float(left[field]) - float(right[field]))
            pairs.append(row)
    output.mkdir(parents=True, exist_ok=True)
    paths = {"decomposition": output / "discover_sequential_decomposition.csv", "trajectories": output / "discover_belief_trajectories.csv", "pairs": output / "discover_sequential_pair_diagnostics.csv"}
    _write(decomposition, paths["decomposition"]); _write(trajectories, paths["trajectories"]); _write(pairs, paths["pairs"])
    cd = [float(row["C_D"]) for row in summaries]
    fields = ("expected_c_exp_total", "local_VOI_sum", "expected_entropy_reduction", "recovered_reward_after_learning", "final_E_abs_belief_minus_half")
    summary = {"scope": "derived audit of the frozen belief-state DP; local VOI values overlap across decision nodes and are not additive welfare components", "configuration_count": len(summaries), "pair_count": len(pairs), "CD_pearson_correlations": {field: _correlation(cd, [float(row[field]) for row in summaries]) for field in fields}, "configurations": summaries}
    (output / "discover_sequential_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
