# Backward compatibility report

## Frozen reference

Reference branch: `research/soctra-hls-q1-integration-evidence`, commit `9772abae1bfcd2c810760e68ecd8fba107d320f0`. The campaign is the 43,200-row Q1 integration evidence campaign documented in its `EXPERIMENTAL_RESULTS.md`; its original configuration, code, result files, metrics, policies, traces, and seeds are not edited by this branch. The reference aggregate fixture is `config/historical_reference_summary.json` (LightGBM A+C, symmetric, alpha=1, n_L2=2, P1, 400 paired seeds).

## Checks completed

- Direct deterministic continuous-calendar comparisons between the new engine and the frozen `simulate_l2_hidden_work` report exact assignments, analyst IDs, starts, completions, and competence for D1, P1 and WAPS on two-analyst fixtures using the same arrivals, services, policy configuration, seed, and horizon.
- The fixed Q1 aggregate reference is recorded and checked: 340/474 timely synthetic needs; pooled S_plus 0.7172995780590717; mean admission-end L1/L2 backlogs 219.755/1.2075; mean admission-end utilization L1/L2 0.994798829497767/0.48015773945870843.
- Historical source modules and campaign configuration remain unchanged; the new engine is opt-in in a separate study directory. Historical defaults and result paths are not changed.
- New tests cover 24x7, configurable five-day schedules, 6x7, Sunday overnight/week rollover, repeated suspension, work conservation, owner retention, severity-independent deadlines, and a factor-60 uniform time transformation.
- The dispatcher API takes alerts, analyst roster, expected service, policy, and seed; it does not accept hidden TP/FP/need mappings.

## Equivalence boundaries

Continuous equivalence is established only for the deterministic fixture described above and the checked historical aggregate fixture value. The stored aggregate is a regression reference, not a newly recomputed campaign output. This report does not claim bit-for-bit reproduction of all 43,200 campaign rows, every seed trace, or every WAPS episode. The availability engine's 8x5 behavior, pause/resume scheduling, and new explicit-deadline scenarios are intentionally new behavior. WAPS thresholds/state logic are passed through the existing HLSB configuration; its behavior is not recalibrated.

## Changes and outstanding work

Files added/updated and exact test commands are recorded in the commit and reproducibility note. No source historical simulator module, source Q1 campaign file, historical result, or manuscript LaTeX file is changed. A complete campaign-level checksum replay is still a separate validation step; until then compatibility is demonstrated for the stated fixtures, not claimed globally.
