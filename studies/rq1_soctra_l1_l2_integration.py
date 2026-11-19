"""Bounded SOCTRA-pattern replay through hypothetical L1/L2 pools.

Run only with authorized local source files:
  PYTHONPATH=src python studies/rq1_soctra_l1_l2_integration.py \
    --source /restricted/dataset_20250919.csv --report /private/report.md
An optional prediction CSV must satisfy the strict out-of-sample checks below.
The script emits aggregate results only and never writes alert/project IDs.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
from hashlib import sha256
from pathlib import Path

from hls.rq1_allocation import Alert, Analyst, B3Config
from hls.rq1_l1_l2 import RoutedAlert, simulate_l1_l2
try:  # direct script execution versus import by pytest
    from soctra_demand_experiment import SourceAlertDemand, SourceDemand, load_soctra_demand
except ModuleNotFoundError:
    from studies.soctra_demand_experiment import SourceAlertDemand, SourceDemand, load_soctra_demand


HORIZON = 1.0
DRAIN = 0.02
L1_ANALYSTS = 4
L2_ANALYSTS = 2
L1_SERVICE_BASE = 0.0005
L2_SERVICE_BASE = 0.0030
SLA_WINDOW = 0.006
COORDINATION_LATENCY = 0.0001
B3_CONFIG = B3Config(0.75, 0.25, 0.15, 0.25)
POLICIES = ("B0", "B1", "B2", "B3")
WINDOWS = ("usual_28d", "peak_28d")
ELIGIBILITY_PROFILES = ("homogeneous", "specialist_backup")


def _bool_value(value: str) -> bool:
    normalized = value.strip().casefold()
    if normalized in {"true", "1", "yes", "y", "si", "sí"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    raise ValueError("prediction recommendation must be boolean")


def load_oos_predictions(path: str | Path, source_alerts: tuple[SourceAlertDemand, ...]) -> dict[str, bool]:
    """Load only row-linked predictions with temporal out-of-sample evidence.

    Required columns: id_alerta, recommendation, out_of_sample,
    available_at, training_cutoff, model_id, evaluation_split. Prediction must
    have been available no later than the alert timestamp, with its training
    cutoff strictly earlier than prediction time. This is a conservative gate;
    it does not certify model quality or label validity.
    """
    expected = {row.alert_key: row for row in source_alerts}
    result: dict[str, bool] = {}
    with Path(path).open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {
            "id_alerta", "recommendation", "out_of_sample", "available_at",
            "training_cutoff", "model_id", "evaluation_split",
        }
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError("prediction CSV lacks required OOS provenance fields")
        for row in reader:
            key = sha256(b"hls-rq1-alert-key-v1\0" + row["id_alerta"].strip().encode("utf-8")).hexdigest()
            source = expected.get(key)
            if source is None:
                raise ValueError("prediction row does not link to an input alert")
            if key in result:
                raise ValueError("duplicate out-of-sample prediction for an alert")
            if not row["model_id"].strip() or row["evaluation_split"].strip().casefold() not in {"test", "heldout", "out_of_sample"}:
                raise ValueError("prediction lacks held-out model/split provenance")
            if not _bool_value(row["out_of_sample"]):
                raise ValueError("prediction row is not marked out of sample")
            try:
                available_at = datetime.fromisoformat(row["available_at"].strip())
                training_cutoff = datetime.fromisoformat(row["training_cutoff"].strip())
            except ValueError as exc:
                raise ValueError("invalid prediction provenance timestamp") from exc
            if available_at.tzinfo or training_cutoff.tzinfo or source.timestamp.tzinfo:
                raise ValueError("timezone-aware prediction timestamps need an explicit reviewed conversion")
            if not training_cutoff < available_at <= source.timestamp:
                raise ValueError("prediction is not demonstrably available out of sample by alert time")
            result[key] = _bool_value(row["recommendation"])
    return result


def _trace_rows(source: SourceDemand, window: str, predictions: dict[str, bool] | None):
    trace = source.traces[window]
    duration = (trace.end - trace.start).total_seconds()
    selected = [row for row in source.source_alerts if trace.start <= row.timestamp < trace.end]
    return tuple(
        RoutedAlert(
            Alert(
                row.alert_key,
                (row.timestamp - trace.start).total_seconds() / duration,
                row.project_class,
                (row.timestamp - trace.start).total_seconds() / duration + SLA_WINDOW,
            ),
            row.historical_escalation_label,
            predictions.get(row.alert_key) if predictions is not None else None,
        )
        for row in selected
    )


def _pool(level: str, count: int, n_classes: int, profile: str) -> tuple[Analyst, ...]:
    agents = []
    for ix in range(count):
        if profile == "homogeneous":
            eligible = frozenset(range(n_classes))
        elif profile == "specialist_backup":
            if count == 2:
                # Two L2 specialists cannot each have a distinct backup while
                # retaining project restrictions, so every class has one owner.
                eligible = frozenset(task_class for task_class in range(n_classes) if task_class % count == ix)
            else:
                eligible = frozenset(
                    task_class for task_class in range(n_classes)
                    if task_class % count in {ix, (ix + 1) % count}
                )
        else:
            raise ValueError("unknown hypothetical project-eligibility profile")
        competence = {
            task_class: (0.90 if task_class % count == ix else 0.60)
            for task_class in eligible
        }
        agents.append(Analyst(f"{level}-{ix:02d}", eligible, competence))
    return tuple(agents)


def _services(n_classes: int, base: float) -> dict[int, float]:
    # Hypothetical project-class duration pattern; 0.8/1.0/1.2 repeats.
    factors = (0.8, 1.0, 1.2)
    return {task_class: base * factors[task_class % len(factors)] for task_class in range(n_classes)}


def run_replay(source: SourceDemand, prediction_path: str | Path | None = None):
    predictions = load_oos_predictions(prediction_path, source.source_alerts) if prediction_path else None
    if not source.historical_escalation_labels_present or any(
        row.historical_escalation_label is None for row in source.source_alerts
    ):
        raise ValueError("historical escalation reference requires a populated escalada_L2 field")
    results = []
    for window in WINDOWS:
        if window not in source.traces:
            continue
        window_rows = _trace_rows(source, window, predictions)
        n_classes = source.project_class_count
        profiles = {}
        for profile in ELIGIBILITY_PROFILES:
            profiles[profile] = (
                _pool("L1", L1_ANALYSTS, n_classes, profile),
                _pool("L2", L2_ANALYSTS, n_classes, profile),
            )
        modes = ["historical_label_reference"]
        if predictions is not None and all(row.soctra_recommendation is not None for row in window_rows):
            modes.append("hypothetical_recommendation_acceptance")
        for mode in modes:
            for profile, (l1, l2) in profiles.items():
                for policy in POLICIES:
                    result = simulate_l1_l2(
                        window_rows, l1, l2,
                        _services(n_classes, L1_SERVICE_BASE),
                        _services(n_classes, L2_SERVICE_BASE),
                        policy=policy, admission_horizon=HORIZON,
                        drain_period=DRAIN, coordination_latency=COORDINATION_LATENCY,
                        decision_mode=mode, b3_config=B3_CONFIG,
                    )
                    results.append({"window": window, "profile": profile, "mode": mode, "result": result})
    return tuple(results)


def format_report(source: SourceDemand, results) -> str:
    lines = [
        "# SOCTRA-pattern replay in the RQ1 L1/L2 simulator", "",
        "## Data provenance and boundaries", "",
        "The replay consumes only timestamp, project class, a hashed alert key, and the historical escalation label from the local restricted source. The key is never emitted. Historical `escalada_L2` is a process label used as a fixed routing proxy; it is not treated as objective ground truth or verified human-effective decision. SOCTRA recommendation is a separate optional input. Any acceptance scenario is hypothetical and is not evidence of analyst behavior.", "",
        f"The supplied source has historical escalation labels: {source.historical_escalation_labels_present}. Out-of-sample predictions are used only when a complete alert-linked set passes the strict provenance/time-availability gate; otherwise the acceptance scenario is omitted.", "",
        "The adapter preserves each selected event timestamp's order and relative gap, and maps timestamps affinely into the existing 28-day window horizon [0,1). The project labels are mapped to deterministic opaque integer classes; names and source IDs are not written. The prior HLS-02 adapter is reused and extended only to retain in-memory hashed IDs and the separate historical label needed for routing.", "",
        "## Hypothetical operating parameters", "",
        f"H=1 normalized 28-day window; drain D={DRAIN}; L1 analysts={L1_ANALYSTS}; L2 analysts={L2_ANALYSTS}; L1 service base={L1_SERVICE_BASE}H; L2 service base={L2_SERVICE_BASE}H; class multipliers repeat 0.8/1.0/1.2; absolute SLA={SLA_WINDOW}H; coordinated dispatch latency={COORDINATION_LATENCY}H. These values are scenario inputs, not observed labor times, staffing, SLAs or coordination costs. All agents are continuously available. Eligibility profiles are homogeneous or an explicitly hypothetical mapping where L1 project classes have a specialist/backup pair and L2 classes have one specialist pool. Competence is hypothetical (.90 on a designated class and .60 otherwise) and never changes service time.", "",
        "The historical-label reference freezes routing inputs for every policy. B0/B1/B2/B3 are the existing RQ1 dispatch policies, applied separately to L1 and L2. A fixed L1 label-proxy decision sends the alert to L2 only after L1 service completion. No model is trained. B3 uses the previously selected thresholds (load .75; deadline pressure .25; competence spread .15; cost/service cap .25).", "",
        "## Paired replay results", "",
        "Each row is the same window, eligibility profile, escalation input and service assumptions under B0–B3. This is a deterministic replay of a trace, not independent sampling; no inferential confidence interval is reported. Values in this report are aggregate only.", "",
        "| Window | Eligibility | Escalation scenario | Policy | SLA H | SLA H+D | L1 backlog H | L2 backlog H | L1 backlog H+D | L2 backlog H+D | Wait H+D | Response H+D | Quality H | Quality H+D | Coordination person-time | B3 choices (B0/B1/B2) |", "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in results:
        result = row["result"]
        h, d = result.at_horizon, result.after_drain
        response = "NA" if d.mean_response_completed is None else f"{d.mean_response_completed:.6f}"
        choices = "/".join(str(n) for _, n in result.selected_strategy_counts) if result.policy == "B3" else "—"
        lines.append(
            f"| {row['window']} | {row['profile']} | {row['mode']} | {result.policy} | "
            f"{h.fraction_within_sla:.4f} | {d.fraction_within_sla:.4f} | {h.l1_backlog} | {h.l2_backlog} | {d.l1_backlog} | {d.l2_backlog} | "
            f"{d.mean_wait_accrued:.6f} | {response} | {h.modeled_quality_per_admitted:.4f} | {d.modeled_quality_per_admitted:.4f} | "
            f"{result.coordination_person_time:.6f} | {choices} |"
        )
    lines += [
        "", "## Interpretation and limitations", "",
        "The comparison is conditional on the alert-record-as-arrival proxy, fixed historical escalation labels, hypothetical role pools, service, competence, eligibility, SLA and coordination latency. A change in B0–B3 outcomes cannot be described as measured operational improvement. Historical escalation labels may reflect process choices or data construction; the scenario does not infer what an analyst would have chosen under a different policy. Recommendation acceptance is shown only if a complete, linked prediction set passes temporal out-of-sample checks, and remains hypothetical.", "",
        "The source contains no validated analyst service times, staffing/availability, queue waits, project eligibility roster, competence, adjudicated security outcome, or contract SLA in the inputs used here. The model omits shifts, L3, learning, variable service, interruption and human override. Historical traces are not evidence of current portfolio representativeness. Prediction provenance and permission must be reviewed before any reuse or publication.", "",
        "## Useful conclusion for the article", "",
        "This integration can support a bounded replay-method description: observed alert timestamps and project mix can drive a hypothetical two-pool L1/L2 organization while preserving the distinction between historical routing labels, model recommendations, modeled analyst decisions, and L2 entry. It cannot establish causal organizational benefits or convert SOCTRA predictions/labels into observed human decisions. No policy should be described as superior unless the relevant trace and operational assumptions support that narrow statement.", "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="authorized local SOCTRA CSV (not copied)")
    parser.add_argument("--predictions", help="optional alert-linked out-of-sample recommendation CSV")
    parser.add_argument("--report", required=True, help="aggregate-only report output path")
    args = parser.parse_args()
    source = load_soctra_demand(args.source)
    rows = run_replay(source, args.predictions)
    output = Path(args.report)
    output.write_text(format_report(source, rows), encoding="utf-8")
    print(f"Wrote aggregate report: {output}; policy/scenario rows={len(rows)}")


if __name__ == "__main__":
    main()
