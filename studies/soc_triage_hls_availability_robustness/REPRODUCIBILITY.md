# Reproducibility

Study code/configuration and its dedicated results directory are isolated under `studies/soc_triage_hls_availability_robustness/` and `results/soc_triage_hls_availability_robustness/`. Preserve synthetic inputs and episode outputs with config hash and code revision. Deadlines are synthetic assumptions, not GMV-CERT SLAs.

Run validation with `pytest -q studies/soc_triage_hls_availability_robustness/tests` (14 deterministic tests at this revision). `config/historical_reference_summary.json` captures a selected, immutable aggregate from the 400-seed Q1 reference campaign. It is a regression fixture, not an output recomputed by this branch. The deterministic engine parity test compares the complete assignment tuples and derived service/S_plus/utilization on fixtures for D1, P1 and WAPS. The 43,200-row campaign has not been replayed against the new code.

The finite pilot is not inferential. Production analysis must bootstrap by seed cluster, maintain pairing across factors, and set seed count from clustered interval precision. No article LaTeX files are involved.
