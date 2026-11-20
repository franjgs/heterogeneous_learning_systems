# SOCTRA–HLS triage–organization coupling pilot

This independent exploratory line evaluates how synthetic escalation
recommendations alter L1/L2 offered work, queueing and the relative performance
of the frozen D1, P1 and HLS-B/WAPS dispatch rules. It does not read SOCTRA
records, train a classifier, alter the SOC engine, or modify those policies.

The branch is based on the published SOC study state; the frozen organizational
reference is commit `20cffed6b7a325cb44b7e73b7295ad946be46982`. The classifier's
old empirical point is used only as a synthetic operating point, never as the
published AIAI classifier result or as individual predictions from its
chronological test set.

## Reproduce

From the repository root:

```bash
python studies/soc_triage_organization_coupling/run_pilot.py
python studies/soc_triage_organization_coupling/summarize_pilot.py
python -m pytest tests/test_soc_triage_organization_coupling.py -q
```

The frozen roster, eligibility, analyst-class service times, deadline model,
and allocation implementation are imported from the original SOC study. The
runner only assembles synthetic alert traces and computes integration metrics.
The pilot uses 10 new paired seeds (`271200000–271200009`) for each of
2 prevalence assumptions × 11 classifier operating points × 2 L1 load levels;
each trace is run under D1, P1 and HLS-B. The classifier grid is a controlled
sensitivity matrix, not a claimed ROC curve.

## Main artifacts

- [Critical report](SOC_TRIAGE_ORGANIZATION_COUPLING_PILOT.md)
- [Fixed pilot configuration](config/pilot.json)
- [Runner](run_pilot.py)
- [Statistical summary and figures](summarize_pilot.py)
- `results/soc_triage_organization_coupling/episodes.csv`: one row per policy,
  seed and condition, including common-trace hashes and dynamic outcomes.
- `triage_by_seed.csv`: confusion counts and realized rates per paired trace.
- `analytic_workload.csv`, `analytic_l2_frontiers.csv`: fluid offered-load
  calculations with composition-specific L2 capacity.
- `summary_by_config_policy.csv`, `paired_contrasts.csv`,
  `interaction_contrasts.csv`, `triage_summary.csv`.
- `waps_switches.csv`, `validation_checks.json`, `metadata.json`.
- `figures/l2_offered_load.png`, `figures/organizational_effect_by_classifier.png`.

The output CSVs contain synthetic aggregates only. They contain no real alert
IDs, project names, or SOCTRA records. Results are exploratory and conditional
on the synthetic prevalence, service, deadline and continuous-capacity
assumptions in the report.
