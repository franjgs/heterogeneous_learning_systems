# Reproducibility

> **AVISO DE VERSIÓN HISTÓRICA:** este informe o protocolo documenta la campaña de disponibilidad ejecutada con servicio L1 previo para todas las alertas y posible L2 posterior. Se preserva para reproducibilidad; no describe ni valida el flujo organizativo vigente. Véase [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

## Software and provenance

Reference source branch: `research/soctra-hls-q1-integration-evidence`, commit `9772abae1bfcd2c810760e68ecd8fba107d320f0`. The new code was developed on `research/soctra-hls-availability-robustness`; campaign workers recorded code revision `d088a7994104994f03ce919b070883fbc8e28859`. Later changes only correct merger validation, identify policy in derived alpha contrasts, and add result reporting/figures; no simulator episodes were rerun or altered. Campaign config is `config/availability_campaign.json`; its full copy is stored in each shard's execution manifest.

## Tests and reference regression

```bash
pytest -q studies/soc_triage_hls_availability_robustness/tests
python studies/soc_triage_hls_availability_robustness/run_full_regression.py
```

The regression uses exact original 400 seed IDs, source configs, 108 condition definitions, generation rules and historical outputs as comparison inputs. It writes only to the new `results/soc_triage_hls_availability_robustness/regression/` location. `regression_checks.json` records exact counts, fields and tolerances. The historical reference directory is read-only for this workflow.

## Full 400-block campaign

Config: three classifier points, D1/P1/WAPS, `rho_L1` 0.85 and 1.25, alpha 0.25 and 1.00, L2 team sizes 2/3/4, calendars 24x7 and Mon–Fri 09:00–17:00, seed base 711000000, admission 168 h, cutoff 240 h, no terminal drain, 10,000 bootstrap replicates with seed 711202611. One episode exists per condition × seed. The seed, not the episode row, is the resampling block.

The four completed shard directories are `campaign/shard0` … `campaign/shard3`, offsets 0/100/200/300, each containing 100 seeds and 21,600 episodes. Reproduction commands from repository root:

```bash
python studies/soc_triage_hls_availability_robustness/run_availability_campaign.py --seed-count 100 --seed-offset 0 --output-dir results/soc_triage_hls_availability_robustness/campaign/shard0
python studies/soc_triage_hls_availability_robustness/run_availability_campaign.py --seed-count 100 --seed-offset 100 --output-dir results/soc_triage_hls_availability_robustness/campaign/shard1
python studies/soc_triage_hls_availability_robustness/run_availability_campaign.py --seed-count 100 --seed-offset 200 --output-dir results/soc_triage_hls_availability_robustness/campaign/shard2
python studies/soc_triage_hls_availability_robustness/run_availability_campaign.py --seed-count 100 --seed-offset 300 --output-dir results/soc_triage_hls_availability_robustness/campaign/shard3
python studies/soc_triage_hls_availability_robustness/merge_campaign_shards.py results/soc_triage_hls_availability_robustness/campaign/shard0 results/soc_triage_hls_availability_robustness/campaign/shard1 results/soc_triage_hls_availability_robustness/campaign/shard2 results/soc_triage_hls_availability_robustness/campaign/shard3
MPLCONFIGDIR=/tmp/soctra_mpl python studies/soc_triage_hls_availability_robustness/make_campaign_figures.py --results-dir results/soc_triage_hls_availability_robustness/campaign
```

Run the shards sequentially or with sufficient isolated compute. Their outputs must not overwrite the merged root until merging. The merger rejects overlapping or missing seeds and mismatched paired traces/L1 assignments. `validation_checks.json` records 86,400 rows, 400 seed blocks, all deadlines matured and zero drain.

## Output inventory and hashes

Merged campaign data: `episodes.csv.gz`, `trace_audit.csv.gz`, `summary_by_condition.csv.gz`, `paired_calendar_contrasts.csv.gz`, `paired_factor_contrasts.csv.gz`, `validation_checks.json`, `execution_manifest.json`, and `figures/*.png`. Historical regression data: compressed episode, assignment and trace comparison CSVs plus `regression_checks.json`. SHA-256 values, byte sizes and source code revision are listed in each directory's `artifact_manifest.json`. Recreate compressed outputs and manifests with `compress_results.py` after merging.

Episode rows retain task-state counts and workload metrics. The large run did not write per-task audit rows; detailed task traces are available only in the smaller pilot run. No generated output is substituted into the historical campaign.

No manuscript LaTeX, SOCTRA source/model outputs, or historical campaign artifacts were changed. These are reproducible synthetic scenarios only; the qualitative expert input does not constitute operational measurement.
