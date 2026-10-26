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


CONDITIONS = ("B00", "B10", "B01", "B11")
PILOT_SEEDS = (20030, 20031, 20032)
PILOT_SCALES = (12, 48)
CALIBRATION_OBSERVATIONS_PER_CELL = 20
LOAD_ALLOWANCE = 1.25
PILOT_COMPOSITION = "H2"
CALIBRATION_STREAM = 6


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
