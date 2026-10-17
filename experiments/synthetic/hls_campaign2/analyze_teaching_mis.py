"""Read-only-to-input analysis of the registered HLS Campaign 2 outputs."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean
from zoneinfo import ZoneInfo

from .teaching_mis_assignment import OUTPUT, ROOT, TOL, encode, sha, write_csv


def read_traces(output):
    with gzip.open(output / "mechanism_traces.csv.gz", "rt", newline="") as stream:
        return list(csv.DictReader(stream))


def analyze_rows(rows):
    blocks = defaultdict(list)
    for row in rows:
        if row["kind"] == "noisy":
            blocks[row["scenario"], int(row["seed"]), row["condition"]].append(row)
    summaries, contrasts = [], []
    for (scenario, seed, condition), block in sorted(blocks.items()):
        block.sort(key=lambda r: int(r["period"]))
        summaries.append({
            "scenario": scenario, "seed": seed, "condition": condition,
            "direct_teaching_gain": sum(float(r["direct_teaching_gain"]) for r in block),
            "learner_target_mis_gain": sum(float(r["learner_target_mis_gain"]) for r in block),
            "total_mis_gain": sum(sum(map(sum, json.loads(r["mis_gain"]))) for r in block),
            "subsequent_learner_target_exposure": sum(float(r["learner_target_effort"]) for r in block[1:]),
            "subsequent_learner_participation_periods": sum(float(r["learner_total_effort"]) > 0 for r in block[1:]),
            "production_effort": sum(float(r["production_effort"]) for r in block),
            "teaching_effort": sum(float(r["teaching_effort"]) for r in block),
            "unused_capacity": sum(float(r["unused_capacity"]) for r in block),
            "resource_cost": sum(float(r["resource_cost"]) for r in block),
            "final_learner_target": json.loads(block[-1]["true_after"])[1][0],
            "first_regime_ces": sum(float(r["ces"]) for r in block if int(r["period"]) < 12),
            "second_regime_ces": sum(float(r["ces"]) for r in block if int(r["period"]) >= 12),
        })
        if condition not in ("C10", "C11"):
            continue
        baseline = blocks[scenario, seed, "C00" if condition == "C10" else "C01"]
        baseline.sort(key=lambda r: int(r["period"]))
        changed = [int(r["period"]) for b,r in zip(baseline[1:],block[1:])
                   if b["production"] != r["production"]]
        contrasts.append({
            "scenario": scenario, "seed": seed, "mis": condition == "C11",
            "subsequent_assignment_change_periods": encode(changed),
            "learner_target_exposure_difference": sum(float(r["learner_target_effort"])-float(b["learner_target_effort"])
                                                       for b,r in zip(baseline[1:],block[1:])),
            "subsequent_learner_mis_gain_difference": sum(float(r["learner_target_mis_gain"])-float(b["learner_target_mis_gain"])
                                                        for b,r in zip(baseline[1:],block[1:])),
        })
    grouped = defaultdict(list)
    for row in summaries:
        grouped[row["scenario"], row["condition"]].append(row)
    aggregate = [{"scenario": s, "condition": c, "n": len(block),
                  **{key: mean(r[key] for r in block) for key in block[0]
                     if key not in ("scenario", "seed", "condition")}}
                 for (s,c),block in sorted(grouped.items())]
    return aggregate, contrasts


def validate_rows(rows):
    blocks = defaultdict(list)
    for row in rows:
        blocks[row["scenario"], row["seed"], row["kind"], row["condition"]].append(row)
    assert len(rows) == 3264 and len(blocks) == 136
    conditions = {"C00", "C10", "C01", "C11"}
    quadruples = {key[:3] for key in blocks}
    assert len(quadruples) == 34
    for key in quadruples:
        assert {k[-1] for k in blocks if k[:3] == key} == conditions
        sequences = []
        for condition in sorted(conditions):
            block = sorted(blocks[key+(condition,)], key=lambda r: int(r["period"]))
            assert len(block) == 24 and [int(r["period"]) for r in block] == list(range(24))
            sequences.append([(r["problem_id"],r["requirements"]) for r in block])
            reference = blocks[key+("C00",)][0]
            for field in ("true_before", "estimated_before", "variance_before", "memory_before", "posterior_before_sha256"):
                assert block[0][field] == reference[field]
            for r in block:
                if condition in ("C00", "C10"):
                    assert all(x == 0 for row in json.loads(r["mis_gain"]) for x in row)
                if condition == "C00":
                    assert r["true_before"] == r["true_after"]
                if key[2] == "zero_efficacy":
                    assert float(r["direct_teaching_gain"]) == 0
                if condition in ("C00","C01") or int(r["period"]) > 0:
                    assert float(r["teaching_effort"]) == 0
                assert abs(float(r["resources_used"])+float(r["unused_capacity"])-2) <= TOL
        assert all(s == sequences[0] for s in sequences)
    return {"unique_quadruples": len(quadruples), "unique_runs": len(blocks),
            "trace_rows": len(rows), "initial_states_matched": True,
            "demand_matched": True, "mis_off_zero_increment": True,
            "no_learning_preserves_true_competencies": True,
            "zero_efficacy_zero_direct_gain": True,
            "resource_accounting": True}


def seed_sensitivity(rows):
    blocks = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row["kind"] == "noisy":
            blocks[row["scenario"],row["condition"]][row["seed"]].append(row)
    summaries = []
    for (scenario, condition), seeds in sorted(blocks.items()):
        paths = [sorted(block, key=lambda r: int(r["period"])) for block in seeds.values()]
        participation = [sum(float(r["learner_total_effort"]) > 0 for r in block) for block in paths]
        summaries.append({"scenario": scenario, "condition": condition,
            "distinct_estimate_paths": len({tuple(r["estimated_after"] for r in block) for block in paths}),
            "distinct_action_paths": len({tuple(r["production"] for r in block) for block in paths}),
            "distinct_ces_totals": len({sum(float(r["ces"]) for r in block) for block in paths}),
            "learner_participation_min": min(participation),
            "learner_participation_max": max(participation)})
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    output = parser.parse_args().output
    manifest = json.loads((output / "manifest.json").read_text())
    for filename, expected in manifest["output_sha256"].items():
        assert sha(output / filename) == expected, filename
    rows = read_traces(output)
    validation = validate_rows(rows)
    aggregate, contrasts = analyze_rows(rows)
    write_csv(output / "mechanism_summary.csv", aggregate)
    write_csv(output / "assignment_contrasts.csv", contrasts)
    write_csv(output / "seed_sensitivity.csv", seed_sensitivity(rows))
    # A variation diagnostic: different posterior means can leave the discrete
    # production ranking unchanged. No inference of zero model uncertainty.
    estimates = defaultdict(set)
    for r in rows:
        if r["kind"] == "noisy":
            estimates[r["scenario"],r["condition"],r["period"]].add(r["estimated_after"])
    validation["max_distinct_estimates_across_seeds_at_same_condition_period"] = max(map(len, estimates.values()))
    (output / "analysis_manifest.json").write_text(json.dumps({
        "recorded_at": datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="seconds"),
        "input_manifest_sha256": sha(output / "manifest.json"),
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in
                          (Path(__file__), ROOT / "tests/test_hls_campaign2_teaching_mis_assignment.py")},
        "validation": validation,
        "output_sha256": {name: sha(output / name) for name in
                          ("mechanism_summary.csv", "assignment_contrasts.csv", "seed_sensitivity.csv", "test_results.xml")
                          if (output / name).exists()},
        "command": f"PYTHONPATH=src:. python -m experiments.synthetic.hls_campaign2.analyze_teaching_mis --output {output}",
    }, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"validation": validation, "mechanisms": aggregate}, indent=2))


if __name__ == "__main__":
    main()
