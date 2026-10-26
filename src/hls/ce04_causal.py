"""CE-04-specific optional P2 calibration/load-factor pilot.

The original CE-04 runner remains the execution engine. With condition B00,
this adapter supplies no intervention arguments, preserving the original P2
path. The module is not a general policy or simulation framework.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import gzip

import numpy as np
import scipy
import simpy

from hls import ce04
from hls.ce04_validation import run_replica_traced, validate_replica
from hls.ce04 import holm_adjust, paired_contrast, tost_equivalence


CONDITIONS = ("B00", "B10", "B01", "B11")
PILOT_SEEDS = (20030, 20031, 20032)
PILOT_SCALES = (12, 48)
CALIBRATION_OBSERVATIONS_PER_CELL = 20
LOAD_ALLOWANCE = 1.25
PILOT_COMPOSITION = "H2"
CALIBRATION_STREAM = 6
CONFIRMATORY_SEEDS = tuple(range(20000, 20030))


@dataclass(frozen=True)
class CausalConfig:
    seed: int
    n_agents: int
    composition: str
    condition: str
    calibration_observations_per_cell: int = CALIBRATION_OBSERVATIONS_PER_CELL
    load_allowance: float = LOAD_ALLOWANCE


def calibration_outcomes(seed: int, n_agents: int, composition: str,
                         observations_per_cell: int = CALIBRATION_OBSERVATIONS_PER_CELL) -> np.ndarray:
    """Generate external pre-t=0 Bernoulli observations on an independent RNG stream."""
    if observations_per_cell != CALIBRATION_OBSERVATIONS_PER_CELL:
        raise ValueError("the CE-approved pilot specifies exactly 20 observations per cell")
    q, _ = ce04.competency_matrix(n_agents, composition, seed)
    rng = np.random.default_rng(np.random.SeedSequence([seed, n_agents, CALIBRATION_STREAM]))
    return (rng.random((n_agents, 4, observations_per_cell)) < q[:, :, None]).astype(np.int8)


def calibration_summary(outcomes: np.ndarray) -> dict:
    outcomes = np.asarray(outcomes)
    if outcomes.ndim != 3 or outcomes.shape[1:] != (4, CALIBRATION_OBSERVATIONS_PER_CELL):
        raise ValueError("calibration outcomes must have shape N×4×20")
    if not np.isin(outcomes, (0, 1)).all():
        raise ValueError("calibration outcomes must be Bernoulli values")
    successes = outcomes.sum(axis=2).astype(int)
    failures = CALIBRATION_OBSERVATIONS_PER_CELL - successes
    digest = hashlib.sha256(outcomes.tobytes(order="C")).hexdigest()
    return {"successes": successes, "failures": failures,
            "n_observations": int(outcomes.size), "sha256": digest}


def run_causal_replica(seed: int, n_agents: int, condition: str, tasks,
                       composition: str = PILOT_COMPOSITION,
                       calibration: np.ndarray | None = None) -> dict:
    if condition not in CONDITIONS:
        raise ValueError(f"condition must be one of {CONDITIONS}")
    calibrated = condition in ("B10", "B11")
    load_filtered = condition in ("B01", "B11")
    if calibrated:
        calibration = calibration_outcomes(seed, n_agents, composition) if calibration is None else calibration
        summary = calibration_summary(calibration)
        if calibration.shape != (n_agents, 4, CALIBRATION_OBSERVATIONS_PER_CELL):
            raise ValueError("calibration shape does not match organization")
        successes, failures = summary["successes"], summary["failures"]
    elif calibration is not None:
        raise ValueError("uncalibrated conditions must not receive external observations")
    else:
        summary = None
        successes = failures = None

    config = ce04.RunConfig(seed, n_agents, composition, "P2")
    result, trace = run_replica_traced(
        config, tasks,
        p2_initial_successes=successes,
        p2_initial_failures=failures,
        p2_load_filter=load_filtered,
    )
    validate_replica(result, config, tasks, trace)
    if load_filtered:
        for decision in result["causal_load_decisions"]:
            if not decision["candidates"] or not set(decision["candidates"]).issubset(decision["admissible"]):
                raise AssertionError("load filter violated shared admission or fallback")
    result["causal_condition"] = condition
    result["causal_config"] = asdict(CausalConfig(seed, n_agents, composition, condition))
    result["calibration"] = None if summary is None else {
        "n_observations": summary["n_observations"],
        "sha256": summary["sha256"],
        "successes": summary["successes"].tolist(),
        "failures": summary["failures"].tolist(),
        "generated_before_t0": True,
        "rng_stream": CALIBRATION_STREAM,
    }
    result["calibration_cost_observations"] = 20 * n_agents * 4 if calibrated else 0
    result["potential_outcome_key"] = "(seed,N,task_id,agent_id,stream_id); shared across B cells"
    result["validation"] = "PASS"
    return result


def pilot_configuration(composition: str = PILOT_COMPOSITION) -> dict:
    """Frozen technical-pilot configuration; this function runs no simulations."""
    return {
        "study": "HLS-CE-04.11 causal diagnostic technical pilot",
        "composition": composition,
        "scales": list(PILOT_SCALES), "conditions": list(CONDITIONS),
        "seeds": list(PILOT_SEEDS), "expected_replicas": 24,
        "calibration_observations_per_agent_family": 20,
        "calibration_rng_stream": CALIBRATION_STREAM,
        "load_rule": "A={i:F_i>=0.50}; load=residual expected service+1.25*queued; median(load[A]); retain load<=median+1.25; empty result falls back to A",
        "shared_admission_unchanged": True,
        "p2_online_updates": "correctness at executed-task completion only",
        "potential_outcomes": "keyed by seed,N,task_id,agent_id,stream_id",
        "protocol": "CE-04 §§4–7; causal factors as specified by CE-04.11",
    }


def configuration_hash(configuration: dict) -> str:
    encoded = json.dumps(configuration, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def pairing_digests(seed: int, n_agents: int, composition: str, tasks) -> dict:
    """Fingerprint the shared task path and keyed potential-outcome basis."""
    q, _ = ce04.competency_matrix(n_agents, composition, seed)
    workload = hashlib.sha256(json.dumps([asdict(t) for t in tasks], sort_keys=True,
                                         separators=(",", ":")).encode()).hexdigest()
    competence = hashlib.sha256(q.tobytes(order="C")).hexdigest()
    key_basis = hashlib.sha256(
        f"ce04-potential-v1|{seed}|{n_agents}|{len(tasks)}|{competence}|streams:3,4".encode()
    ).hexdigest()
    return {"workload_sha256": workload, "competence_sha256": competence,
            "potential_outcome_key_basis_sha256": key_basis}


def run_pilot(output_dir: str | os.PathLike[str], composition: str = PILOT_COMPOSITION) -> dict:
    """Execute and validate only the authorized 24 technical-pilot replicas."""
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    config = pilot_configuration(composition)
    config_digest = configuration_hash(config)
    (target / "frozen_config.json").write_text(
        json.dumps({"configuration": config, "sha256": config_digest}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    revision = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=False).stdout.strip() or "unknown"
    summaries = []
    raw_path = target / "replicas.jsonl.gz"
    if raw_path.exists():
        raise FileExistsError(raw_path)
    started = time.perf_counter()
    with gzip.open(raw_path, "wt", encoding="utf-8") as output:
        for n_agents in PILOT_SCALES:
            for seed in PILOT_SEEDS:
                tasks = ce04.generate_workload(seed, n_agents)
                digests = pairing_digests(seed, n_agents, composition, tasks)
                shared_calibration = calibration_outcomes(seed, n_agents, composition)
                group = []
                for condition in CONDITIONS:
                    result = run_causal_replica(seed, n_agents, condition, tasks,
                                                composition, shared_calibration if condition in ("B10", "B11") else None)
                    result["pairing_digests"] = digests
                    result["provenance"] = {
                        "git_revision_before_pilot": revision,
                        "python": sys.version, "numpy": np.__version__,
                        "scipy": scipy.__version__, "simpy": simpy.__version__,
                        "config_sha256": config_digest,
                    }
                    group.append(result)
                    output.write(json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n")
                    output.flush()
                    summaries.append({
                        "seed": seed, "n_agents": n_agents, "composition": composition,
                        "condition": condition,
                        "success_on_time_rate": result["success_on_time_rate"],
                        "n_arrivals": result["n_arrivals"], "n_admitted": result["n_admitted"],
                        "n_rejected": result["n_rejected"], "service_time_total": result["service_time_total"],
                        "cpu_seconds": result["cpu_seconds"], "wall_seconds": result["wall_seconds"],
                        "decision_seconds": result["decision_seconds"], "peak_rss": result["peak_rss"],
                        "calibration_cost_observations": result["calibration_cost_observations"],
                        "validation": result["validation"],
                    })
                signatures = {tuple(sorted(x["pairing_digests"].items())) for x in group}
                if len(signatures) != 1:
                    raise AssertionError("paired workload/potential-outcome basis differs across B cells")
                calibrated = [x["calibration"]["sha256"] for x in group if x["calibration"] is not None]
                if len(calibrated) != 2 or calibrated[0] != calibrated[1]:
                    raise AssertionError("B10 and B11 did not share the same external calibration")
    elapsed = time.perf_counter() - started
    if len(summaries) != 24 or any(row["validation"] != "PASS" for row in summaries):
        raise AssertionError("pilot did not complete 24 validated replicas")
    import pandas as pd
    pd.DataFrame(summaries).to_csv(target / "replica_metrics.csv", index=False)
    manifest = {
        "configuration_sha256": config_digest,
        "raw_jsonl_gzip_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "replicas": len(summaries), "all_validated": True,
        "duration_wall_seconds": elapsed,
        "calibration_observations_per_seed_scale_pair": {
            str(n): 20 * n * 4 for n in PILOT_SCALES
        },
        "raw_artifact": raw_path.name,
    }
    (target / "pilot_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                                                encoding="utf-8")
    return manifest


def confirmatory_configuration() -> dict:
    """Execution manifest; scientific factors remain those in CE-04.11."""
    return {
        "study": "HLS-CE-04.12 P2 causal diagnostic confirmatory campaign",
        "frozen_design_sha256": "0f99dee0b7f1e81e4c768dcac977f9cafe0091b934c69467ce27097408d588c0",
        "composition": PILOT_COMPOSITION, "scales": list(PILOT_SCALES),
        "conditions": list(CONDITIONS), "seeds": list(CONFIRMATORY_SEEDS),
        "expected_replicas": len(PILOT_SCALES) * len(CONDITIONS) * len(CONFIRMATORY_SEEDS),
        "calibration_observations_per_agent_family": 20,
        "calibration_rng_stream": CALIBRATION_STREAM,
        "load_rule": "A={i:F_i>=0.50}; expected residual+queued workload; median over A; keep <= median+1.25; empty filter falls back to A",
        "shared_admission_unchanged": True,
        "p2_online_updates": "correctness at executed-task completion only",
        "potential_outcomes": "keyed by seed,N,task_id,agent_id,stream_id",
    }


def _diagnostics(result: dict) -> dict:
    """Descriptive estimator, allocation, congestion and delay metrics."""
    config = result["config"]
    n_agents = config["n_agents"]
    q, _ = ce04.competency_matrix(n_agents, config["composition"], config["seed"])
    successes = np.zeros((n_agents, 4), dtype=int)
    observations = np.zeros((n_agents, 4), dtype=int)
    calibration = result.get("calibration")
    if calibration is not None:
        successes += np.asarray(calibration["successes"], dtype=int)
        observations += 20
    counts = np.zeros(n_agents, dtype=int)
    waits = []
    for record in result["records"]:
        agent = record["selected_agent"]
        if agent is None:
            continue
        counts[agent] += 1
        if record["p2_label_observed_at"] is not None:
            observations[agent, record["family"]] += 1
            successes[agent, record["family"]] += int(bool(record["correct"]))
        waits.append(float(record["service_start"] - record["arrival"]))
    q_hat = (1 + successes) / (2 + observations)
    error = q_hat - q
    observed_cells = observations > 0
    proportions = counts / max(1, counts.sum())
    positive = proportions > 0
    return {
        "p2_observed_pairs": int(observed_cells.sum()),
        "p2_pair_coverage": float(observed_cells.mean()),
        "p2_rmse_all_pairs": float(np.sqrt(np.mean(error**2))),
        "p2_rmse_observed_pairs": float(np.sqrt(np.mean(error[observed_cells]**2))) if observed_cells.any() else None,
        "p2_observations_total_including_calibration": int(observations.sum()),
        "assignment_hhi": float(np.sum(proportions**2)),
        "assignment_effective_agents": float(1 / np.sum(proportions**2)) if counts.sum() else 0.0,
        "mean_queue_wait": float(np.mean(waits)) if waits else None,
        "p95_queue_wait": float(np.quantile(waits, .95)) if waits else None,
        "late_completion_rate_among_admitted": result["n_late"] / result["n_admitted"] if result["n_admitted"] else 0.0,
        "rejection_rate": result["n_rejected"] / result["n_arrivals"] if result["n_arrivals"] else 0.0,
        "utilization_mean": float(np.mean(result["agent_utilization"])),
        "assignment_count_min": int(counts.min()),
        "assignment_count_max": int(counts.max()),
    }


def analyze_causal_campaign(rows: list[dict], *, bootstrap_seed: int = 20261026) -> dict:
    """Analyze only the three predeclared paired contrasts, separately by N."""
    indexed = {(int(r["seed"]), int(r["n_agents"]), r["condition"]):
               float(r["success_on_time_rate"]) for r in rows}
    scales = (12, 48)
    summaries = {}
    for n in scales:
        raw = {"delta_I_B10_minus_B00": [], "delta_C_B01_minus_B00": [],
               "delta_IC_interaction": []}
        for seed in CONFIRMATORY_SEEDS:
            b00 = indexed[(seed, n, "B00")]
            b10 = indexed[(seed, n, "B10")]
            b01 = indexed[(seed, n, "B01")]
            b11 = indexed[(seed, n, "B11")]
            raw["delta_I_B10_minus_B00"].append((b10 - b00) * 100)
            raw["delta_C_B01_minus_B00"].append((b01 - b00) * 100)
            raw["delta_IC_interaction"].append((b11 - b10 - b01 + b00) * 100)
        result = {}
        for j, (name, values) in enumerate(raw.items()):
            summary = paired_contrast(values, bootstrap_seed=bootstrap_seed + 100 * n + j)
            tost = tost_equivalence(values, margin=2.0)
            summary["tost"] = tost
            summary["tost_p_value"] = max(tost["p_lower"], tost["p_upper"])
            summary["paired_differences_pp"] = values
            result[name] = summary
        p_adj = holm_adjust([x["p_value_paired_t_two_sided"] for x in result.values()])
        tost_adj = holm_adjust([x["tost_p_value"] for x in result.values()])
        for item, p, p_tost in zip(result.values(), p_adj, tost_adj):
            item["p_value_holm_within_scale"] = p
            item["tost_p_holm_within_scale"] = p_tost
            item["equivalent_holm_2pp"] = p_tost < .05
        summaries[str(n)] = result
    return {"unit": "paired independent seed; differences in percentage points",
            "bootstrap_resamples": 10000, "confidence_level": 0.95,
            "holm_family": "three prespecified contrasts within each scale; difference and TOST families adjusted separately",
            "tost_margin_pp": 2.0, "by_scale": summaries}


def run_confirmatory(output_dir: str | os.PathLike[str],
                     pilot_config_path: str | os.PathLike[str]) -> dict:
    """Run the authorized 240-replica campaign; abort on the first failed check."""
    frozen = json.loads(Path(pilot_config_path).read_text(encoding="utf-8"))
    if configuration_hash(frozen["configuration"]) != frozen["sha256"]:
        raise ValueError("pilot frozen configuration digest is invalid")
    execution = confirmatory_configuration()
    if frozen["sha256"] != execution["frozen_design_sha256"]:
        raise ValueError("frozen design hash does not match the CE-authorized value")
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    for name in ("replicas.jsonl.gz", "replica_metrics.csv", "confirmatory_analysis.json", "campaign_manifest.json"):
        if (target / name).exists():
            raise FileExistsError(target / name)
    execution_digest = configuration_hash(execution)
    (target / "execution_config.json").write_text(json.dumps({
        "execution_configuration": execution, "execution_sha256": execution_digest,
        "frozen_design_sha256_verified": frozen["sha256"],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    revision = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=False).stdout.strip() or "unknown"
    raw_path = target / "replicas.jsonl.gz"
    metric_rows = []
    start = time.perf_counter()
    with gzip.open(raw_path, "wt", encoding="utf-8") as output:
        for n_agents in PILOT_SCALES:
            for seed in CONFIRMATORY_SEEDS:
                tasks = ce04.generate_workload(seed, n_agents)
                digests = pairing_digests(seed, n_agents, PILOT_COMPOSITION, tasks)
                shared_calibration = calibration_outcomes(seed, n_agents, PILOT_COMPOSITION)
                group = []
                for condition in CONDITIONS:
                    result = run_causal_replica(seed, n_agents, condition, tasks,
                                                PILOT_COMPOSITION,
                                                shared_calibration if condition in ("B10", "B11") else None)
                    result["pairing_digests"] = digests
                    result["provenance"] = {
                        "git_revision": revision, "python": sys.version,
                        "numpy": np.__version__, "scipy": scipy.__version__,
                        "simpy": simpy.__version__, "frozen_design_sha256": frozen["sha256"],
                        "execution_sha256": execution_digest,
                    }
                    group.append(result)
                    output.write(json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n")
                    output.flush()
                    metric_rows.append({
                        "seed": seed, "n_agents": n_agents, "composition": PILOT_COMPOSITION,
                        "condition": condition, "success_on_time_rate": result["success_on_time_rate"],
                        "n_arrivals": result["n_arrivals"], "n_admitted": result["n_admitted"],
                        "n_rejected": result["n_rejected"], "n_incorrect": result["n_incorrect"],
                        "n_late": result["n_late"], "service_time_total": result["service_time_total"],
                        "service_time_per_success": result["service_time_per_success"],
                        "decision_seconds": result["decision_seconds"], "cpu_seconds": result["cpu_seconds"],
                        "wall_seconds": result["wall_seconds"], "peak_rss": result["peak_rss"],
                        "calibration_cost_observations": result["calibration_cost_observations"],
                        **_diagnostics(result), "validation": result["validation"],
                    })
                if len({tuple(sorted(r["pairing_digests"].items())) for r in group}) != 1:
                    raise AssertionError("paired potential-outcome paths differ within seed-scale block")
                cal_hashes = [r["calibration"]["sha256"] for r in group if r["calibration"] is not None]
                if cal_hashes != [cal_hashes[0], cal_hashes[0]]:
                    raise AssertionError("B10/B11 calibration samples differ")
    elapsed = time.perf_counter() - start
    expected = len(PILOT_SCALES) * len(CONFIRMATORY_SEEDS) * len(CONDITIONS)
    if len(metric_rows) != expected or any(r["validation"] != "PASS" for r in metric_rows):
        raise AssertionError(f"expected {expected} validated replicas, got {len(metric_rows)}")
    import pandas as pd
    pd.DataFrame(metric_rows).to_csv(target / "replica_metrics.csv", index=False)
    analysis = analyze_causal_campaign(metric_rows)
    (target / "confirmatory_analysis.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n",
                                                       encoding="utf-8")
    manifest = {
        "replicas": len(metric_rows), "all_validated": True,
        "frozen_design_sha256": frozen["sha256"], "execution_sha256": execution_digest,
        "duration_wall_seconds": elapsed,
        "unique_calibration_observations": {"N12": 20 * 12 * 4 * len(CONFIRMATORY_SEEDS),
                                             "N48": 20 * 48 * 4 * len(CONFIRMATORY_SEEDS)},
        "tracked_sha256": {name: hashlib.sha256((target / name).read_bytes()).hexdigest()
                           for name in ("execution_config.json", "replica_metrics.csv", "confirmatory_analysis.json")},
        "local_only_raw_log": raw_path.name,
        "raw_log_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
    }
    (target / "campaign_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                                                   encoding="utf-8")
    return manifest
