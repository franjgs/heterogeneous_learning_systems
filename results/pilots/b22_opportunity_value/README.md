# B2.2 result directory

No B2.2 scientific results exist at implementation time.

The complete future run will write `raw_results.csv`,
`aggregate_results.csv`, `decision_regions.csv`, `representative_cases.csv`,
`analysis_summary.md`, `run_metadata.json`, and scientific figures here only
after all 60 opportunity updates pass their provenance controls. Restart
checkpoints and incremental artifacts live in the ignored `.cache/` directory
and must not be committed.
