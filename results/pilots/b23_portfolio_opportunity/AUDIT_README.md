# B2.3 audit artifacts

This directory preserves the small textual outputs needed to audit the
completed PACS B2.3 result. Model checkpoints and runtime caches remain under
the ignored `.cache/` directory and are not versioned.

## Scientific outputs

- `summary.md`: frozen classification and top-level integrity counts.
- `primary_results.csv`: all 1,800 preregistered analytical rows and the full
  value, routing, competence, interaction, and rescue decomposition.
- `reproducibility.csv`: the 360 exact `N × pair × c × B` cells across seeds.
- `compute_dose.csv`: all 450 midpoint dose-control valuations.
- `competence_changes.csv`: `DeltaS` and interaction vectors for 90 pair
  states.
- `analysis_aggregates.csv`, `representative_cases.csv`, and
  `continuation_thresholds.csv`: compact generated summaries and cases.
- `state_metrics.csv`: all 250 VALIDATION competence vectors.
- `singleton_diagnosis.csv`: 300 post-hoc `singleton × c` rows containing the
  four `DeltaS` components, local/cross summaries and classes, exact
  domain-level `DeltaV` contributions, routing adjustment, and dominant
  negative term. It uses only B2.3 common-provenance states and does not amend
  the preregistered primary analysis.
- `timing_summary.json`: compact operational timing extracted from the ignored
  restart timing log; timing is outside scientific fingerprints.

## Compatibility and provenance

- `run_manifest.json`: protocol/configuration hashes, frozen grid, software
  versions, device, TEST closure, artifact hashes, parentage, dose, and status.
- `base_states.jsonl`: the five F0 and five D records.
- `opportunities.jsonl`: immutable sample IDs, pseudo-labels, RNG provenance,
  and opportunity hashes.
- `development_states.jsonl`: singleton, midpoint, and final joint genealogy,
  hashes, dose, RNG provenance, and validation metrics.
- `split_manifest.csv`: exact PACS split membership used by the run.

The authoritative closure is
`docs/checkpoints/HLS_checkpoint_after_B23.md`. The dataset revision is
`394113073258ead631f617d2e13bb377c0715c4b`; TEST remained closed. Absolute
cache paths inside manifests document the execution environment and are not
expected to resolve on another machine without reconstructing the ignored
runtime artifacts.
