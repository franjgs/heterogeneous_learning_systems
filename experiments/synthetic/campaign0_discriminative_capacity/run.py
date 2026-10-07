"""Frozen Campaign 0 discriminative-capacity diagnostic.

Protocol constants in this file are fixed before execution.  This diagnostic
does not alter or tune the finite-belief, CES, MPC, or MIS-v2 implementation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.discover_develop_v0 import DISCOVER_DEVELOP  # noqa: E402
from hls.finite_problem_belief import run_finite_problem_sequence  # noqa: E402
from hls.small_problem_world import HORIZON, HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402

OUT = ROOT / "results" / "diagnostics" / "campaign0_discriminative_capacity"
ETA = 0.35
SEEDS = tuple(range(10))
TEAMS = {
    "G00": ((0.5, 0.5), (0.5, 0.5), (0.5, 0.5)),
    "G04": ((0.25, 0.75), (0.625, 0.375), (0.625, 0.375)),
    "G05": ((0.0, 1.0), (0.5, 0.5), (1.0, 0.0)),
    "G07": ((0.0, 1.0), (0.5, 0.0), (1.0, 0.5)),
}
TEAM_LABELS = {
    "G00": "generalist reference",
    "G04": "intermediate/redundant",
    "G05": "strong complementary specialization",
    "G07": "asymmetric heterogeneous",
}
HISTORIES_P = {
    "H0": (0.8, 0.7, 0.3, 0.2, 0.5, 0.8),
    "H1": (0.8, 0.2, 0.3, 0.7, 0.5, 0.8),
    "H2": (0.8, 0.8, 0.8, 0.8, 0.8, 0.8),
    "H3": (0.8, 0.2, 0.8, 0.2, 0.8, 0.8),
}
HISTORIES = {key: tuple((p, 1.0 - p) for p in values) for key, values in HISTORIES_P.items()}


def _compact(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def validate_protocol() -> None:
    assert ETA == 0.35 and SEEDS == tuple(range(10)) and HORIZON == 3
    assert tuple(TEAMS) == ("G00", "G04", "G05", "G07")
    assert HISTORIES_P["H0"] == (0.8, 0.7, 0.3, 0.2, 0.5, 0.8)
    assert HISTORIES_P["H1"] == (0.8, 0.2, 0.3, 0.7, 0.5, 0.8)
    assert sorted(HISTORIES_P["H0"]) == sorted(HISTORIES_P["H1"])
    assert all(tuple(sum(row[k] for row in state) for k in range(2)) == (1.5, 1.5) for state in TEAMS.values())
    assert HYPOTHESIS_REPERTOIRE == ((0.8, 0.2), (0.5, 0.5), (0.2, 0.8))
    assert UNIFORM_PRIOR == (1 / 3,) * 3


def execute() -> tuple[list[dict], list[dict]]:
    runs: list[dict] = []
    trajectories: list[dict] = []
    for history_id, problems in HISTORIES.items():
        for seed in SEEDS:
            for team_id, initial_state in TEAMS.items():
                steps = run_finite_problem_sequence(
                    initial_state, problems, HYPOTHESIS_REPERTOIRE,
                    prior=UNIFORM_PRIOR, mode=DISCOVER_DEVELOP,
                    eta=ETA, horizon=HORIZON, seed=seed,
                )
                problem_rewards = defaultdict(float)
                for row in steps:
                    problem_rewards[row.problem_id] += row.true_mean
                    delta = tuple(tuple(row.state_after[i][k] - row.state_before[i][k] for k in range(2)) for i in range(3))
                    trajectories.append({
                        "team": team_id, "team_label": TEAM_LABELS[team_id], "history": history_id,
                        "seed": seed, "problem_index": row.problem_id, "within_problem_step": row.step_id,
                        "true_problem": _compact(row.true_problem), "p": row.true_problem[0],
                        "belief_before": _compact(row.belief_before), "belief_after": _compact(row.belief_after),
                        "S_before": _compact(row.state_before), "action": _compact(row.action),
                        "exposure": _compact(row.action), "development_increment": _compact(delta),
                        "S_after": _compact(row.state_after), "mu_true": row.true_mean,
                        "observed_reward": row.observed_reward, "cumulative_performance": row.cumulative_reward,
                    })
                runs.append({
                    "team": team_id, "team_label": TEAM_LABELS[team_id], "history": history_id, "seed": seed,
                    "eta": ETA, "horizon": HORIZON, "problems": len(problems),
                    "cumulative_performance": steps[-1].cumulative_reward,
                    "initial_A_performance": problem_rewards[0], "final_A_performance": problem_rewards[5],
                    "final_S": _compact(steps[-1].state_after),
                })
    return runs, trajectories


def analyze(runs: list[dict], trajectories: list[dict]) -> tuple[list[dict], list[dict], list[dict], dict]:
    matrix, rankings, order = [], [], []
    for history in HISTORIES:
        cells = []
        for team in TEAMS:
            sample = [r for r in runs if r["history"] == history and r["team"] == team]
            values = [float(r["cumulative_performance"]) for r in sample]
            finals = [float(r["final_A_performance"]) for r in sample]
            cells.append({
                "history": history, "team": team, "mean_cumulative_performance": sum(values) / len(values),
                "min_cumulative_performance": min(values), "max_cumulative_performance": max(values),
                "mean_final_A_performance": sum(finals) / len(finals), "seeds": len(sample),
            })
        ranked = sorted(cells, key=lambda x: (-x["mean_cumulative_performance"], x["team"]))
        for rank, cell in enumerate(ranked, 1):
            matrix.append({**cell, "cumulative_rank": rank})

        for problem_index in range(6):
            pcells = []
            for team in TEAMS:
                vals = []
                for seed in SEEDS:
                    vals.append(sum(float(r["mu_true"]) for r in trajectories if r["history"] == history and r["team"] == team and r["seed"] == seed and r["problem_index"] == problem_index))
                pcells.append((team, sum(vals) / len(vals)))
            for rank, (team, value) in enumerate(sorted(pcells, key=lambda x: (-x[1], x[0])), 1):
                rankings.append({"history": history, "problem_index": problem_index, "p": HISTORIES_P[history][problem_index], "team": team, "mean_problem_performance": value, "rank": rank})

    for team in TEAMS:
        for seed in SEEDS:
            h0 = next(float(r["final_A_performance"]) for r in runs if r["team"] == team and r["history"] == "H0" and r["seed"] == seed)
            h1 = next(float(r["final_A_performance"]) for r in runs if r["team"] == team and r["history"] == "H1" and r["seed"] == seed)
            order.append({"team": team, "seed": seed, "final_A_H0": h0, "final_A_H1": h1, "Delta_order": h0 - h1})

    mean_order = {team: sum(float(x["Delta_order"]) for x in order if x["team"] == team) / len(SEEDS) for team in TEAMS}
    final_rank = {}
    for history in ("H0", "H1"):
        vals = [(team, next(float(x["mean_final_A_performance"]) for x in matrix if x["history"] == history and x["team"] == team)) for team in TEAMS]
        final_rank[history] = [team for team, _ in sorted(vals, key=lambda x: (-x[1], x[0]))]
    summary = {
        "mean_Delta_order": mean_order,
        "final_A_ranking": final_rank,
        "final_A_ranking_changes_between_H0_H1": final_rank["H0"] != final_rank["H1"],
        "per_seed_ranking_patterns": {
            history: {">".join(pattern): count for pattern, count in Counter(tuple(team for team, _ in sorted(
                ((team, next(float(r["final_A_performance"]) for r in runs if r["history"] == history and r["seed"] == seed and r["team"] == team)) for team in TEAMS),
                key=lambda x: (-x[1], x[0]))) for seed in SEEDS).items()}
            for history in ("H0", "H1")
        },
    }
    return matrix, rankings, order, summary


def make_plots(rankings: list[dict]) -> None:
    import matplotlib.pyplot as plt
    for history in HISTORIES:
        fig, ax = plt.subplots(figsize=(7, 4))
        for team in TEAMS:
            rows = [r for r in rankings if r["history"] == history and r["team"] == team]
            ax.plot([r["problem_index"] + 1 for r in rows], [r["rank"] for r in rows], marker="o", label=team)
        ax.invert_yaxis(); ax.set_yticks((1, 2, 3, 4)); ax.set_xlabel("Problem stage"); ax.set_ylabel("Performance rank")
        ax.set_title(f"Campaign 0 ranking through problem time — {history}"); ax.legend(ncol=4)
        fig.tight_layout(); fig.savefig(OUT / f"ranking_through_time_{history}.png", dpi=160); plt.close(fig)


def main() -> None:
    validate_protocol()
    OUT.mkdir(parents=True, exist_ok=True)
    runs, trajectories = execute()
    matrix, rankings, order, summary = analyze(runs, trajectories)
    _write_csv(OUT / "runs.csv", runs)
    _write_csv(OUT / "trajectories.csv", trajectories)
    _write_csv(OUT / "configuration_history_matrix.csv", matrix)
    _write_csv(OUT / "ranking_through_time.csv", rankings)
    _write_csv(OUT / "order_effects.csv", order)
    make_plots(rankings)
    protocol = {
        "status": "frozen_before_execution", "diagnostic_not_main_campaign": True,
        "teams": TEAMS, "team_labels": TEAM_LABELS, "histories_p": HISTORIES_P,
        "eta": ETA, "seeds": SEEDS, "common_random_numbers": "same seed for every team within each history",
        "mode": DISCOVER_DEVELOP, "hypothesis_repertoire": HYPOTHESIS_REPERTOIRE,
        "prior": UNIFORM_PRIOR, "horizon_per_problem": HORIZON,
        "physics_changes": "none", "run_count": len(runs), "trajectory_row_count": len(trajectories),
    }
    protocol_hash = hashlib.sha256(json.dumps(protocol, sort_keys=True).encode()).hexdigest()
    with (OUT / "manifest.json").open("w", encoding="utf-8") as handle:
        json.dump({**protocol, "protocol_sha256": protocol_hash, "analysis": summary}, handle, indent=2, sort_keys=True); handle.write("\n")


if __name__ == "__main__":
    main()
