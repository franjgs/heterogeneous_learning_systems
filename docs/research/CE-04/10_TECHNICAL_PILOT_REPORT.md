# HLS-CE-04.5 — Technical pilot report

**Date:** 2026-10-26

**Status:** **NO APTO — PILOT STOPPED AT FIRST VALIDATION GATE**

**Branch:** `feature/hls-laboratory-v1`
**Code baseline:** `707573abd551620b05ca82bf470a0e02da1afdce`

## 1. Scope and configuration

The CE authorized the 3 × 3 × 4 × 3 pilot only: `N={12,24,48}`,
`H={H0,H1,H2}`, `P={P0,P1,P2,P3}`, seeds `{0,1,2}` (108 factorial
replicas). The configuration hash is SHA-256
`c72bdca82906daa2118b415d3ba76d1fbfac87c47a1c3ee72fea7677e4b8a1b5`,
computed from canonical sorted compact JSON containing the factorial,
competence matrix, arrival phases/rates, horizon, deadline, admission rule,
service law, policies and statistical settings. The payload was reconstructed
after the stop from the exact pre-run hash input and is preserved in the
diagnostic `config.json` record (SHA-256
`8dc3ff3139356736fea8927df551259ce3b5034ae4831558e36cab1ee28e2b49`); that
record explicitly does not claim to be a completed-run manifest.

Code-file hashes at launch:

| File | SHA-256 |
|---|---|
| `src/hls/ce04.py` | `632b8869c734f244bafe7f962cdd285098d9e0a42314591848277623243abbbb` |
| `src/hls/linucb.py` | `20b0f91f183ba103811592cfc3293ae940f02ed1f05dc658d7bfd330bcfe250b` |
| `pyproject.toml` | `10b6ad60ed7604faa95e8341bbaa9c4c1f0f7744de22febdd9c263f1acf4449e` |
| This protocol, `06_CE04_CONSOLIDATED_PROTOCOL.md` | `39cd594131d302d67116fcc6faf622574969be40702567cd3e733756a50b0aa5` |

Environment: Python 3.11.9, NumPy 1.26.4, SciPy 1.13.1, SimPy 4.1.2,
macOS arm64 / Apple M2 Max. Before execution, the branch matched the stated
reference, the tracked tree was clean, the pilot matrix contained exactly 108
unique conditions over seeds 0–2, and the focused test suite passed (45 tests;
see §4).

The CE directed that recovery after demand shifts be excluded provisionally.
It was not calculated or replaced by another measure.

## 2. Execution and stop condition

The first configured condition was `seed=0, N=12, H0, P0`. One simulation
completed in memory and the post-replica validator halted before its run log
or metrics were written. Thus **1 of 108 replicas was attempted, 0 passed the
pilot validation gate, 107 were not run**, and there are no accepted pilot
performance results. The stop artifact is
[`pilot_failure.json`](../../../results/experiments/hls_ce04_pilot/pilot_failure.json)
(SHA-256 `b8354b936b29de9e8af5d982a33fad598423a7296579b312a21e5f7b5e6a8470`).
No task-level log or replica metrics were persisted for the attempted run.
Elapsed time and peak memory for that run were not captured; no pilot duration
or resource estimate is reported as measured.

The run stopped because the validation wrapper asserted `non-P3 got P3
update`. Inspection identified that this assertion conflated reward
instrumentation with a policy update:

- `src/hls/ce04.py`, `log_p3_reward` (lines 299–309): records the reward and
  observation timestamp for every policy's task record, but calls
  `p3.observe(...)` only when `config.policy == "P3"`.
- `deadline_watch` (lines 311–318): records the deadline outcome for the task
  as diagnostic data. It does not supply that value to P0, P1 or P2.

Therefore the assertion did **not** establish that a non-P3 policy received a
LinUCB update or used future information. It did identify that the validator's
interpretation of these log fields was too broad. Following the CE's
fail-safe instruction, execution was stopped; no code or protocol was changed
and no further replica was run. This report does not silently waive the failed
gate: the pilot remains **NO APTO / incomplete** pending a corrected,
reviewable validation criterion and a new CE instruction to resume.

## 3. Pilot validation status

| Check | Status | Evidence / scope |
|---|---|---|
| Branch/reference and clean tree before launch | PASS | `feature/hls-laboratory-v1`, HEAD and origin matched the reference; clean before output creation. |
| Frozen configuration and 108-cell matrix | PASS | Canonical configuration SHA above; seeds 0–2 only. |
| Automated preflight tests | PASS | 45 focused tests passed before launch. |
| Recovery metric excluded | PASS | Not computed or substituted. |
| Task conservation and per-task completion | NOT COMPLETED | The first run reached validation, but the wrapper stopped on the P3 instrumentation assertion before recording its other check outcomes. |
| FCFS, capacity, deadline semantics | NOT COMPLETED | No full validation record was written for the attempted replica. |
| P2/P3 information and update timing | NOT COMPLETED | The runtime check did not complete; code inspection confirms P2 updates on completion and LinUCB updates only for P3 when the reward is observable. |
| Reproducibility and paired conditions | NOT COMPLETED FOR PILOT | Existing tests cover deterministic replay on a fixed fixture; the full pilot matrix did not run. |
| H0–H2 means and resource/load configuration | PASS IN PREFLIGHT ONLY | Construction tests establish task-wise mean 0.775 at N=12/24/48; this is not a 108-replica validation. |
| Metric domains / finite outputs | NOT COMPLETED | The run was not recorded as a validated replica. |
| Warnings/errors and runtime resources | NOT COMPLETED | No warnings were reported before the assertion, but run-level warning, CPU and memory records were not persisted. |

No condition was selected or tuned by its performance. No campaign seeds
1000–1029 were used. No scientific superiority claim is supported.

## 4. Tests and files

Preflight command:

```text
PYTHONPATH=.:src pytest -q tests/test_ce04.py tests/test_linucb.py tests/test_hls_common_experiment_contract.py tests/test_hls_performance_evaluation.py
45 passed in 13.24s
```

The fixed deadline-probability validation remains: 25 deterministic
convolution cases, two reference probabilities in `[0.45,0.55]`, maximum
absolute error `0.0038559621` (tolerance `0.01`). This numerical check is not a
pilot outcome.

This report records a stopped attempt, not the results of the requested 108
replicas. The local diagnostic JSON is retained as a lightweight artifact;
no large logs or performance datasets were added to Git. The protocol and
scientific parameters were not changed.
