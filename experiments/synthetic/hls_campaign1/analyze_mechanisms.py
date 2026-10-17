"""Reproduce mechanism diagnostics from the published Campaign 1 pilot.

The published episode table is the analysis source. An optional, targeted
replay recovers the per-event private teaching-gain field omitted from CSV;
it replays only policy/seed blocks with at least one logged teaching event and
checks their public and private trajectories against the frozen CSV first.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import platform
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median, stdev
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from experiments.synthetic.hls_campaign1.run import (  # noqa: E402
    HIGH_EFFICACY,
    LEARNING,
    LOW_EFFICACY,
    PARAMETERS,
    RESOURCE_BUDGET,
    SEEDS,
    _environment,
    _initial_team,
    _policy,
    configuration_grid,
)
from hls.hls_lab_v1_integrated import TeachingEfficacy, run_integrated_sequence  # noqa: E402


INPUT = ROOT / "results/experiments/hls_campaign1_pilot"
OUTPUT = ROOT / "results/diagnostics/hls_campaign1_mechanism_diagnostics"
TEACHING_POLICIES = (
    "P1_FIXED_TEACHING", "P2_ADAPTIVE_TEACHING", "P2_SCHEDULED_NO_FEEDBACK"
)
CONFIG_FIELDS = ("demand", "initial_deficit", "teaching_effectiveness", "horizon")
RUN_FIELDS = CONFIG_FIELDS + ("seed", "individual_learning", "policy")
TOL = 1e-12


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty diagnostic table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({k: ("NA" if v is None or v == "" else v)
                          for k, v in row.items()} for row in rows)


def _key(row: dict[str, str], fields=RUN_FIELDS) -> tuple[object, ...]:
    return tuple(row[name] for name in fields)


def _sample_stats(values: list[float]) -> dict[str, object]:
    return {
        "n": len(values), "mean": mean(values) if values else None,
        "sd_between_replicates": stdev(values) if len(values) > 1 else (0.0 if values else None),
        "median": median(values) if values else None,
        "minimum": min(values) if values else None,
        "maximum": max(values) if values else None,
        "positive_fraction": sum(x > TOL for x in values) / len(values) if values else None,
        "negative_fraction": sum(x < -TOL for x in values) / len(values) if values else None,
        "tie_fraction": sum(abs(x) <= TOL for x in values) / len(values) if values else None,
    }


def _run_maps(seed_rows: list[dict[str, str]]) -> dict[tuple[str, ...], dict[str, dict[str, str]]]:
    grouped: dict[tuple[str, ...], dict[str, dict[str, str]]] = defaultdict(dict)
    paired_fields = CONFIG_FIELDS + ("seed", "individual_learning")
    for row in seed_rows:
        grouped[_key(row, paired_fields)][row["policy"]] = row
    return grouped


def interaction_analysis(seed_rows: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    by_condition = _run_maps(seed_rows)
    by_config_seed_li: dict[tuple[str, ...], dict[str, dict[str, str]]] = defaultdict(dict)
    for key, policies in by_condition.items():
        config_seed = key[:-1]
        by_config_seed_li[config_seed][key[-1]] = policies
    raw = []
    for key, li_rows in sorted(by_config_seed_li.items()):
        if set(li_rows) != {"False", "True"}:
            raise ValueError(f"incomplete paired LI block: {key}")
        on = li_rows["True"]
        off = li_rows["False"]
        d_on = float(on["P2_ADAPTIVE_TEACHING"]["ces_reward_sum"]) - float(on["P0_PRODUCTION_ONLY"]["ces_reward_sum"])
        d_off = float(off["P2_ADAPTIVE_TEACHING"]["ces_reward_sum"]) - float(off["P0_PRODUCTION_ONLY"]["ces_reward_sum"])
        raw.append(dict(zip(CONFIG_FIELDS + ("seed",), key),
                        delta_on=d_on, delta_off=d_off, interaction_on_minus_off=d_on-d_off))

    summaries = []
    groupings = [(), *((field,) for field in CONFIG_FIELDS), CONFIG_FIELDS]
    for grouping in groupings:
        groups: dict[tuple[str, ...], list[dict]] = defaultdict(list)
        for row in raw:
            groups[tuple(row[field] for field in grouping)].append(row)
        for key, rows in sorted(groups.items()):
            summary = {field: value for field, value in zip(grouping, key)}
            for name in ("delta_on", "delta_off", "interaction_on_minus_off"):
                for stat, value in _sample_stats([float(row[name]) for row in rows]).items():
                    summary[f"{name}_{stat}"] = value
            summaries.append(summary)
    return raw, summaries


def temporal_analysis(episodes: list[dict[str, str]]) -> tuple[list[dict], list[dict], list[dict]]:
    runs: dict[tuple[str, ...], dict[int, dict[str, dict[str, str]]]] = defaultdict(lambda: defaultdict(dict))
    for row in episodes:
        if row["policy"] not in {"P0_PRODUCTION_ONLY", "P2_ADAPTIVE_TEACHING"}:
            continue
        key = tuple(row[field] for field in CONFIG_FIELDS + ("seed", "individual_learning"))
        runs[key][int(row["period"])][row["policy"]] = row
    temporal = []
    summaries = []
    grouped: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for key, periods in sorted(runs.items()):
        cumulative = 0.0
        negative_in_trace = False
        recovery = None
        taught = False
        ever_negative = False
        first_teaching_period = None
        first_teaching_delta = None
        first_teaching_cumulative = None
        negative_since_teaching = False
        recovered_after_teaching = False
        break_even_after_teaching = None
        for period, pair in sorted(periods.items()):
            if set(pair) != {"P0_PRODUCTION_ONLY", "P2_ADAPTIVE_TEACHING"}:
                raise ValueError(f"incomplete temporal pair {key}, period {period}")
            p0, p2 = pair["P0_PRODUCTION_ONLY"], pair["P2_ADAPTIVE_TEACHING"]
            delta = float(p2["ces_reward"]) - float(p0["ces_reward"])
            cumulative += delta
            if p2["teaching_relation"] != "NA":
                taught = True
                if first_teaching_period is None:
                    first_teaching_period = period
                    first_teaching_delta = delta
                    first_teaching_cumulative = cumulative
            if cumulative < -TOL:
                ever_negative = True
                negative_in_trace = True
                if first_teaching_period is not None and period >= first_teaching_period:
                    negative_since_teaching = True
            elif negative_in_trace and recovery is None:
                recovery = period
            if (first_teaching_period is not None and negative_since_teaching
                    and period > first_teaching_period and cumulative >= -TOL
                    and not recovered_after_teaching):
                recovered_after_teaching = True
                break_even_after_teaching = period
            temporal.append(dict(zip(CONFIG_FIELDS + ("seed", "individual_learning"), key),
                                 period=period, period_delta=delta, cumulative_delta=cumulative,
                                 p2_teaching_this_period=p2["teaching_relation"] != "NA"))
        n = len(periods)
        final = cumulative
        outcome = dict(zip(CONFIG_FIELDS + ("seed", "individual_learning"), key),
                       final_cumulative_delta=final, initial_disadvantage=ever_negative,
                       break_even_period=recovery,
                       teaching_occurred=taught,
                       never_amortized=ever_negative and recovery is None,
                       first_teaching_period=first_teaching_period,
                       first_teaching_episode_delta=first_teaching_delta,
                       cumulative_at_first_teaching=first_teaching_cumulative,
                       cumulative_negative_after_teaching=negative_since_teaching,
                       recovered_after_teaching=recovered_after_teaching,
                       break_even_after_teaching_period=break_even_after_teaching,
                       never_amortized_after_teaching=(negative_since_teaching and not recovered_after_teaching),
                       immediate_delta=sum(float(periods[t]["P2_ADAPTIVE_TEACHING"]["ces_reward"])
                                           - float(periods[t]["P0_PRODUCTION_ONLY"]["ces_reward"])
                                           for t in range(min(2, n))))
        summaries.append(outcome)
        grouped[key[:-2] + (key[-1],)].append(outcome)  # all configuration fields + LI

    reduced = []
    for key, rows in sorted(grouped.items()):
        summary = dict(zip(CONFIG_FIELDS + ("individual_learning",), key))
        final_stats = _sample_stats([float(row["final_cumulative_delta"]) for row in rows])
        summary.update({f"final_delta_{k}": v for k, v in final_stats.items()})
        disadvantage = [row for row in rows if row["initial_disadvantage"]]
        recoveries = [int(row["break_even_period"]) for row in disadvantage
                      if row["break_even_period"] is not None]
        summary.update(
            initial_disadvantage_replicates=len(disadvantage),
            recovered_after_disadvantage=len(recoveries),
            never_amortized=sum(bool(row["never_amortized"]) for row in rows),
            cumulative_negative_after_teaching=sum(bool(row["cumulative_negative_after_teaching"]) for row in rows),
            recovered_after_teaching=sum(bool(row["recovered_after_teaching"]) for row in rows),
            never_amortized_after_teaching=sum(bool(row["never_amortized_after_teaching"]) for row in rows),
            first_teaching_episode_loss=sum(
                row["first_teaching_episode_delta"] is not None
                and float(row["first_teaching_episode_delta"]) < -TOL for row in rows),
            teaching_never_occurred=sum(not bool(row["teaching_occurred"]) for row in rows),
            mean_any_trace_break_even_period=mean(recoveries) if recoveries else None,
            mean_break_even_after_teaching_period=mean(
                [int(row["break_even_after_teaching_period"]) for row in rows
                 if row["break_even_after_teaching_period"] is not None]
            ) if any(row["break_even_after_teaching_period"] is not None for row in rows) else None,
        )
        reduced.append(summary)
    return temporal, summaries, reduced


def cost_analysis(episodes: list[dict[str, str]], seed_rows: list[dict[str, str]]) -> list[dict]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in episodes:
        grouped[_key(row)].append(row)
    p0_production = {}
    for key, rows in grouped.items():
        if key[-1] == "P0_PRODUCTION_ONLY":
            p0_production[key[:-1]] = sum(float(row["production_effort"]) for row in rows)
    summaries = []
    for key, rows in sorted(grouped.items()):
        p = key[-1]
        n = len(rows)
        taught = [row for row in rows if row["teaching_relation"] != "NA"]
        budget_total = sum(float(row["resources_available"]) for row in rows)
        prod = sum(float(row["production_effort"]) for row in rows)
        used = sum(float(row["resources_used"]) for row in rows)
        teach = sum(float(row["teaching_effort"]) for row in rows)
        matched_p0_prod = p0_production.get(key[:-1], 0.0)
        total_gain = 0.0
        total_net_competence_change = 0.0
        for row in rows:
            before = json.loads(row["competence_real_before"])
            after = json.loads(row["competence_real_after"])
            total_net_competence_change += sum(after[i][k]-before[i][k]
                                               for i in range(3) for k in range(2))
        summaries.append(dict(zip(RUN_FIELDS, key), episodes=n,
            teaching_periods=len(taught), nominal_teaching_effort_sum=teach,
            mean_teaching_effort_per_lesson=(teach/len(taught) if taught else None),
            production_effort_sum=prod,
            matched_p0_production_effort_sum=matched_p0_prod if p != "P0_PRODUCTION_ONLY" else None,
            matched_p0_minus_observed_production_effort=(matched_p0_prod-prod if p != "P0_PRODUCTION_ONLY" else None),
            total_resource_use=used, unused_resource_capacity=budget_total-used,
            unused_capacity_mean_per_period=(budget_total-used)/n,
            utilization=used/budget_total if budget_total else None,
            net_real_competence_change_sum=total_net_competence_change,
            teaching_gain_not_in_frozen_csv=True))
    return summaries


def grouped_mean_sd(rows: list[dict[str, object]], keys: tuple[str, ...], measures: tuple[str, ...]) -> list[dict]:
    groups: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[tuple(str(row[key]) for key in keys)].append(row)
    output = []
    for group_key, values in sorted(groups.items()):
        result: dict[str, object] = dict(zip(keys, group_key))
        result["replicates"] = len(values)
        for measure in measures:
            nums = [float(row[measure]) for row in values if row.get(measure) is not None]
            result[f"{measure}_mean"] = mean(nums) if nums else None
            result[f"{measure}_sd_between_replicates"] = stdev(nums) if len(nums) > 1 else (0.0 if nums else None)
        output.append(result)
    return output


def _verify_input(input_dir: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], dict]:
    manifest = json.loads((input_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("campaign") != "HLS-SCIENTIFIC-CAMPAIGN-1-PILOT":
        raise ValueError("unexpected source campaign")
    for name, digest in manifest["artifacts_sha256"].items():
        path = input_dir / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"published source artifact hash mismatch: {name}")
    for name, digest in manifest["source_sha256"].items():
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"published source-code hash mismatch: {name}")
    episodes = _read(input_dir / "episodes.csv")
    seed_rows = _read(input_dir / "seed_summaries.csv")
    if len(episodes) != 20480 or len(seed_rows) != 1280:
        raise ValueError("published source record counts do not match manifest")
    return episodes, seed_rows, manifest


def _replay_gains(input_dir: Path, episodes: list[dict[str, str]], output: Path) -> list[dict]:
    source_manifest = json.loads((input_dir / "manifest.json").read_text(encoding="utf-8"))
    source_path = ROOT / "experiments/synthetic/hls_campaign1/run.py"
    expected_hash = source_manifest["source_sha256"]["experiments/synthetic/hls_campaign1/run.py"]
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != expected_hash:
        raise ValueError("campaign source differs from the frozen pilot source hash")

    by_run: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in episodes:
        if row["policy"] in TEACHING_POLICIES:
            by_run[_key(row)].append(row)
    jobs = [(key, rows) for key, rows in sorted(by_run.items())
            if any(row["teaching_relation"] != "NA" for row in rows)]
    output_rows = []
    for number, (key, frozen_rows) in enumerate(jobs, start=1):
        demand, deficit, efficacy_label, horizon_label, seed, li_text, policy_name = key
        config = next(row for row in configuration_grid()
                      if (row["demand"], row["initial_deficit"],
                          row["teaching_effectiveness"], row["horizon"])
                      == (demand, deficit, efficacy_label, horizon_label))
        n_periods = int(config["n_periods"])
        problems, _latent = _environment(demand, n_periods, int(seed))
        efficacy_value = LOW_EFFICACY if efficacy_label == "low" else HIGH_EFFICACY
        efficacy_matrix = tuple(tuple((0.0, 0.0) if i == j else (efficacy_value, efficacy_value)
                                      for j in range(3)) for i in range(3))
        result = run_integrated_sequence(
            _initial_team(deficit), problems, _policy(policy_name),
            learning=LEARNING,
            teaching_efficacy=TeachingEfficacy(efficacy_matrix), parameters=PARAMETERS,
            individual_learning=li_text == "True",
            organizational_learning=policy_name != "P2_SCHEDULED_NO_FEEDBACK",
            seed=int(seed),
        )
        if len(result.records) != len(frozen_rows):
            raise ValueError(f"replay length mismatch: {key}")
        for live, frozen in zip(result.records, frozen_rows):
            checks = {
                "period": live.period == int(frozen["period"]),
                "problem": live.problem_id == frozen["problem_id"],
                "action": live.production_action_id == int(frozen["production_action_id"]),
                "relation": ("NA" if live.action.teaching is None else ":".join(map(str, live.action.teaching.relation))) == frozen["teaching_relation"],
                "CES": math.isclose(live.ces_reward, float(frozen["ces_reward"]), rel_tol=0.0, abs_tol=TOL),
                "resources": math.isclose(live.total_resource_used, float(frozen["resources_used"]), rel_tol=0.0, abs_tol=TOL),
                "competence_before": live.competence_real_before == tuple(tuple(x) for x in json.loads(frozen["competence_real_before"])),
                "competence_after": live.competence_real_after == tuple(tuple(x) for x in json.loads(frozen["competence_real_after"])),
            }
            if not all(checks.values()):
                raise ValueError(f"targeted replay mismatch {key} period={live.period}: {checks}")
            if live.teaching_gain_real is not None:
                event = live.action.teaching
                assert event is not None
                output_rows.append(dict(
                    demand=demand, initial_deficit=deficit,
                    teaching_effectiveness=efficacy_label, horizon=horizon_label,
                    seed=seed, individual_learning=li_text, policy=policy_name,
                    period=live.period, relation=":".join(map(str, event.relation)),
                    nominal_teaching_effort=live.teaching_effort,
                    realized_teaching_competence_increment=live.teaching_gain_real,
                    teaching_observation=live.teaching_observation,
                    target_skill_real_before=live.competence_real_before[event.learner][event.capability],
                    target_skill_real_after_period=live.competence_real_after[event.learner][event.capability],
                    total_real_competence_change_period=sum(
                        live.competence_real_after[i][k]-live.competence_real_before[i][k]
                        for i in range(3) for k in range(2)),
                    ces_reward=live.ces_reward, production_effort=live.production_effort,
                    resources_used=live.total_resource_used, resource_budget=RESOURCE_BUDGET,
                ))
        print(f"replayed teaching run {number}/{len(jobs)}", file=sys.stderr)
    _write(output, output_rows)
    return output_rows


def _plot(temporal: list[dict], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    grouped: dict[tuple[str, str, int], dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in temporal:
        key = (row["horizon"], row["individual_learning"], int(row["teaching_effectiveness"] == "high"))
        grouped[key][int(row["period"])].append(float(row["cumulative_delta"]))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4), sharey=False)
    for ax, horizon in zip(axes, ("short", "long")):
        for (h, li, high), periods in sorted(grouped.items()):
            if h != horizon:
                continue
            xs = sorted(periods)
            ys = [mean(periods[t]) for t in xs]
            sds = [stdev(periods[t]) if len(periods[t]) > 1 else 0.0 for t in xs]
            label = f"LI={'ON' if li == 'True' else 'OFF'}, efficacy={'high' if high else 'low'}"
            ax.plot(xs, ys, label=label)
            ax.fill_between(xs, [y-s for y, s in zip(ys, sds)],
                            [y+s for y, s in zip(ys, sds)], alpha=0.12)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(f"{horizon.capitalize()} horizon")
        ax.set_xlabel("Period")
        ax.set_ylabel("Mean cumulative CES(P2) − CES(P0)")
        ax.grid(alpha=0.2)
    axes[-1].legend(fontsize=7, loc="best")
    fig.suptitle("Paired cumulative CES difference; band = ±1 between-seed SD\nmean over demand and initial-deficit strata")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="svg")
    # Matplotlib emits trailing spaces in multiline SVG path data; trim them
    # mechanically so generated artifacts satisfy git diff --check.
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n",
                    encoding="utf-8")
    plt.close(fig)


def run(input_dir: Path = INPUT, output_dir: Path = OUTPUT) -> dict[str, int]:
    episodes, seed_rows, manifest = _verify_input(input_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    interactions, interaction_summaries = interaction_analysis(seed_rows)
    temporal, temporal_by_seed, temporal_summaries = temporal_analysis(episodes)
    costs = cost_analysis(episodes, seed_rows)
    _write(output_dir / "learning_interaction_by_seed.csv", interactions)
    _write(output_dir / "learning_interaction_summary.csv", interaction_summaries)
    _write(output_dir / "p2_p0_temporal_by_episode.csv", temporal)
    _write(output_dir / "p2_p0_temporal_by_seed.csv", temporal_by_seed)
    _write(output_dir / "p2_p0_temporal_summary.csv", temporal_summaries)
    _write(output_dir / "teaching_cost_by_run.csv", costs)
    cost_summaries = grouped_mean_sd(
        costs, ("policy", "individual_learning", "teaching_effectiveness"),
        ("teaching_periods", "nominal_teaching_effort_sum", "production_effort_sum",
         "matched_p0_minus_observed_production_effort", "unused_resource_capacity",
         "net_real_competence_change_sum"),
    )
    _write(output_dir / "teaching_cost_summary.csv", cost_summaries)
    gains = _replay_gains(input_dir, episodes,
                          output_dir / "teaching_event_gains_targeted_replay.csv")
    gain_summaries = grouped_mean_sd(
        gains, ("policy", "individual_learning", "teaching_effectiveness"),
        ("realized_teaching_competence_increment", "teaching_observation",
         "total_real_competence_change_period"),
    )
    for row in gain_summaries:
        row["events"] = row.pop("replicates")
    _write(output_dir / "teaching_event_gains_summary.csv", gain_summaries)
    _plot(temporal, output_dir / "p2_p0_cumulative_difference.svg")
    metadata = {
        "source_manifest_sha256": hashlib.sha256((input_dir / "manifest.json").read_bytes()).hexdigest(),
        "source_episode_sha256": hashlib.sha256((input_dir / "episodes.csv").read_bytes()).hexdigest(),
        "source_seed_summary_sha256": hashlib.sha256((input_dir / "seed_summaries.csv").read_bytes()).hexdigest(),
        "source_run_source_sha256": manifest["source_sha256"]["experiments/synthetic/hls_campaign1/run.py"],
        "source_code_hashes_verified": manifest["source_sha256"],
        "analysis_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "execution_timestamp_europe_madrid": datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="seconds"),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "matplotlib": importlib.metadata.version("matplotlib"),
        },
        "targeted_teaching_run_replays": len({tuple(row[k] for k in RUN_FIELDS)
                                               for row in gains}),
        "teaching_event_gain_rows": len(gains),
        "diagnostic_note": "Episode/interaction/temporal measures are calculated from frozen pilot data. Only exact realized teaching-gain fields omitted by the published CSV are recovered by deterministic targeted replays; every replay trajectory is checked against the frozen episode records.",
    }
    metadata["derived_artifacts_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(output_dir.iterdir()) if path.is_file() and path.name != "analysis_manifest.json"
    }
    (output_dir / "analysis_manifest.json").write_text(json.dumps(metadata, indent=2, sort_keys=True)+"\n")
    return {"interaction_pairs": len(interactions), "temporal_rows": len(temporal),
            "cost_runs": len(costs), "teaching_gain_events": len(gains)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output), indent=2))


if __name__ == "__main__":
    main()
