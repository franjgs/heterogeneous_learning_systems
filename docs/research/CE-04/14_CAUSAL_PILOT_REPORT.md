# HLS-CE-04.11 — P2 causal diagnostic implementation and technical pilot

**Date:** 2026-10-26
**Status:** Technical pilot complete; confirmatory 240-replica study not run.
**Branch:** `feature/hls-laboratory-v1`

## 1. Scope and frozen configuration

Implemented the CE-authorized four conditions: B00 (original P2), B10 (P2
with 20 external Bernoulli observations per agent×family), B01 (P2 with the
load filter), and B11 (both interventions). The unchanged common admission
set is formed first. For the filter, expected load is the conditional
expected residual service of an active task plus 1.25 per waiting task; the
median is taken over A only, agents with load `<= median(A)+1.25` remain, and
an empty filtered set falls back to A. Calibration is generated before the
simulation on independent RNG stream 6, shared by B10/B11 per seed and scale;
P2 receives only success/failure counts and continues completion-time online
updates.

The order gave N, conditions and seeds but did not name a CE-04 composition.
For this technical pilot, composition was fixed to **H2**, the focal setting
for P2's sparse-coverage and estimation-error diagnosis in [12](12_MECHANISM_DIAGNOSTICS.md).
This scope choice is explicit in the frozen configuration and is not inferred
from pilot results. No other H level was run.

Frozen configuration SHA-256:
`0f99dee0b7f1e81e4c768dcac977f9cafe0091b934c69467ce27097408d588c0`.
The canonical configuration is in
[`frozen_config.json`](../../../results/experiments/hls_ce04_causal_pilot/frozen_config.json).
It specifies N=12/48, seeds 20030–20032, four B cells, H2, 20 observations
per cell, and the approved load rule. The 240 confirmatory replications were
not run.

## 2. Implementation

The CE-04 runner gained optional initial P2 counts and an optional P2-only
load filter. With both options absent, B00 follows the original P2 decision
and update path; the existing simulator remains the execution engine. The
causal adapter generates and hashes the calibration sample, records its
success/failure counts and observation cost, logs load-filter decisions, and
checks paired workload and keyed-outcome bases. The common `F_i >= 0.50`
admission rule is unchanged. No future service realization is used for load
or selection.

Calibration acquisition count was `20×N×4`: 960 observations per N=12
seed-scale pair and 3,840 per N=48 pair. B10 and B11 share one draw, counted
once for acquisition accounting. Across the three seeds, the unique counts
were 2,880 (N=12) and 11,520 (N=48). These are observation counts; no
conversion to service time or monetary cost is specified.

Code and tests:

- [`ce04.py`](../../../src/hls/ce04.py): optional P2 initialization and
  decision-time load filter; original defaults preserved.
- [`ce04_causal.py`](../../../src/hls/ce04_causal.py): calibration stream,
  four-cell adapter, configuration hash, pairing checks, and pilot runner.
- [`ce04_validation.py`](../../../src/hls/ce04_validation.py): allows the
  existing effective-update validator to trace the optional runner path.
- [`test_ce04_causal.py`](../../../tests/test_ce04_causal.py): B00 parity,
  admission/cap/fallback, load arithmetic, calibration isolation and sharing,
  keyed outcome stability, delayed feedback, and reproducibility.

## 3. Tests and validation

Command:

```text
python -m pytest -q tests/test_ce04_causal.py tests/test_ce04.py tests/test_ce04_validation.py
```

Result: **31 passed**. Coverage includes B00 record and outcome parity with
the unmodified default P2 call; calibration shape/count and RNG isolation;
shared B10/B11 sample hash; load median computed on A; fallback; preserved
admission; completion-only P2 updates; and repeatability. During implementation,
the update-trace test exposed an instrumentation interaction with extra array
initialization; initialization was changed to retain the existing two live
Beta arrays, then the full focused set passed before the pilot.

All 24 pilot replicas passed the existing CE-04 replica checks, including task
conservation, one execution per admitted task, FCFS/capacity, deadline
semantics, finite metrics, common admission replay and effective P2 update
timing. Additional pilot checks confirmed that B10 and B11 shared calibration
hashes and that each four-cell seed-scale block had identical workload,
competence and keyed potential-outcome basis. No fallback was needed. No
replica was dropped.

## 4. Pilot results (descriptive only)

Mean success-on-time rates over three seeds; these small pilot summaries are
diagnostic and are **not** confirmatory estimates or evidence of treatment
effects.

| N | B00 | B10 | B01 | B11 | B10−B00 (pp) | B01−B00 (pp) | B11−B00 (pp) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 12 | 84.44% | 87.54% | 83.72% | 87.54% | +3.10 | −0.72 | +3.10 |
| 48 | 78.78% | 88.17% | 78.26% | 88.17% | +9.40 | −0.52 | +9.40 |

All cells admitted the same number of tasks within each seed-scale pair;
there were zero rejections. The load filter removed candidate agents on
1,792 decisions for B01 and 1,651 for B11 at N=12; at N=48 the counts were
7,068 and 6,022. It changed the selected agent versus B00 on 4,656 B01
assignments at N=12 and 28,402 at N=48. Yet B10 and B11 selected identical
agents in these three seed pairs and had identical success rates. This is a
pilot observation in H2, not evidence that the load intervention has no
effect generally.

## 5. Runtime and artifacts

Runtime environment: Python 3.11.9, NumPy 1.26.4, pandas 2.2.3, SciPy 1.13.1,
SimPy 4.1.2. Elapsed pilot wall time including validation: 47.55 s; summed
replica CPU: 24.87 s; summed replica wall time: 24.88 s; maximum recorded
platform-native peak RSS: 314,900,480 bytes. The large compressed task log is
31,945,428 bytes and remains local-only; SHA-256:
`5466955d90c36190f1cf6aaab28cdd9a9168fc8a1a4bf6c7424d384577268f6c`.
The tracked [`pilot_manifest.json`](../../../results/experiments/hls_ce04_causal_pilot/pilot_manifest.json)
records this digest and the configuration hash. [`replica_metrics.csv`](../../../results/experiments/hls_ce04_causal_pilot/replica_metrics.csv)
contains all 24 lightweight per-replica summaries.

## 6. Technical verdict and limits

**Technical pilot: PASS (24/24).** Optional calibration and load components
preserve the baseline path and shared admission contract, and the paired
random-outcome construction worked as specified. Calibration is a synthetic
external-information intervention; its real acquisition cost is not
identified. The pilot has only three seeds and one composition (H2); the
descriptive differences must not be interpreted as inferential or causal
confirmation. No confirmatory seeds, additional compositions, or parameter
adjustments were used. The next 240-replica study is not run or authorized by
this report.
