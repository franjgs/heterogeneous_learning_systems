# B2.2 result directory

The valid CPU execution completed 60 opportunity updates and 1,200 analytical
rows in 08:10:14 with TEST closed. The preregistered classification is
`INCONCLUSIVE`: four favorable observations exist, but zero of 240 cells are
favorable in at least two seeds.

The completed run wrote `raw_results.csv`, `aggregate_results.csv`,
`decision_regions.csv`, `representative_cases.csv`, `analysis_summary.md`,
`run_metadata.json`, and scientific figures after all 60 opportunity updates
passed their provenance controls. Restart
checkpoints and incremental artifacts live in the ignored `.cache/` directory
and must not be committed. The independent audit and scientific diagnosis are
in [b22_diagnostic.md](b22_diagnostic.md).
