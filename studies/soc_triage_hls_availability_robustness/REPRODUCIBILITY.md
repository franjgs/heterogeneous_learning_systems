# Reproducibility

Run deterministic tests with `pytest -q studies/soc_triage_hls_availability_robustness/tests` (17 pass). Recompute the full prior campaign regression with `python studies/soc_triage_hls_availability_robustness/run_full_regression.py`; output is isolated to the new results directory. It reuses the exact reference branch source configuration and seed IDs and never writes to historical result paths.

The availability campaign fixes seed base 711000000, 400 seed blocks, classifier operating points, rho, alpha, policies, L2 rosters, weekly calendars, synthetic severity deadline map, admission/cutoff horizons, and seed-block bootstrap in `config/availability_campaign.json`. For reproducible parallel execution, split seed offsets into four 100-seed shards, for example offsets 0, 100, 200, 300, each with its own `--output-dir`; then run `merge_campaign_shards.py` over all four directories. The merger validates disjoint seeds, full coverage, paired hashes, matured deadlines, and recomputes all global bootstrap summaries and contrasts.

Compress generated CSV artifacts and create hashes with `compress_results.py`. Each manifest records compressed SHA-256, byte sizes and code revision. Historical and experimental outputs are never written into one another's directories.

The full Q1 regression is complete and passed. The eight-seed availability run is a technical pilot only. No study result describes measured SOC operations or GMV-CERT. No article LaTeX files are involved.
