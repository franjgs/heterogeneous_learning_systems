# Backward compatibility report

## Frozen reference

Reference branch: `research/soctra-hls-q1-integration-evidence`, commit `9772abae1bfcd2c810760e68ecd8fba107d320f0`. The campaign is the 43,200-row Q1 integration campaign. Its source, config, metrics, policies, traces, seeds and historical results were not modified. The fixed aggregate fixture is in `config/historical_reference_summary.json`.

## Full campaign regression

`run_full_regression.py` replayed the exact source configuration and seeds: 400 seed blocks × 3 classifiers × 3 policies × 4 alpha values × 3 L2 roster sizes = 43,200 episodes. It generated 1,200 trace audits and compared 1,681,848 L2 task records: selected analyst, start, completion and competence. Episode comparisons include trace/recommendation/need hashes, confusion counts, S_plus numerator/denominator, L1/L2 backlog, effective work, utilization and WAPS switches.

Result: 43,200/43,200 episodes passed, zero divergent episodes, zero task assignment differences. Absolute tolerance was `1e-10` for time/metric values; alert IDs, analyst IDs, states, and hashes were exact. Full results are under `results/soc_triage_hls_availability_robustness/regression/` with compressed CSVs and a SHA-256 manifest.

The all-continuous calendar uses the frozen hidden-work event loop as an exact compatibility fast path. A parallel run through the standalone event loop exposed femtosecond-scale completion drift at simultaneous events; one later D1 tie selected another analyst and changed downstream service totals. The historical module was left untouched and this altered path is not used for 24x7. The calendar event loop is used for non-continuous calendars. Deterministic fixture tests compare the standalone engine to D1/P1/WAPS on smaller scenarios.

## Additional checks

- Reference aggregate fixture: 340/474 timely needs; pooled S_plus 0.7172995780590717; mean admission-end L1/L2 backlogs 219.755/1.2075; admission-end utilization 0.994798829497767/0.48015773945870843.
- Tests cover 24x7, configurable 8x5, 6x7, Sunday overnight/week rollover, repeated suspension, work/owner retention, independent deadlines, time scaling, and exact fast-D1 decisions/RNG state.
- Dispatch APIs do not accept hidden need or TP/FP labels.

No source Q1 simulator/campaign file, historical result, SOCTRA artifact, or manuscript LaTeX file was changed. This demonstrates full compatibility through the continuous-mode adapter; it does not establish operational validity of synthetic calendars.
