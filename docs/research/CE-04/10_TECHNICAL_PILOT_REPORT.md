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

This report retains the stopped attempt above and records the corrected rerun
below; the original attempt has not been overwritten.

---

## 5. CE-04.6 — validator correction and completed rerun

**CE instruction date:** 2026-10-26. **Execution result:** **APTO — 108/108
technical replicas passed the pilot validation gate.** This is a technical
pilot disposition only, not evidence for a scientific advantage of any
composition or policy.

### 5.1 Diagnosis and correction

The CE-04.5 wrapper treated the presence of `p3_reward_observed_at` as proof
that LinUCB had updated. In `src/hls/ce04.py`, that field and the associated
reward event are diagnostic records written for task outcomes; the actual
`p3.observe(...)` call is guarded by `config.policy == "P3"`. Thus a P0
deadline event can have the field without any effective estimator update.
This was a validator false positive, not a reproduced simulator defect.

The validation-only helper [`src/hls/ce04_validation.py`](../../../src/hls/ce04_validation.py)
now traces effective Beta-array writes and actual LinUCB update calls while
the simulation runs. It requires: P0/P1 no estimator updates; P2 Beta–Bernoulli
updates only at observed completion labels; and P3 LinUCB updates only from
its observable completion/deadline reward. The trace audit matches each update
to its feedback time and arm/context/reward. It does not infer updates from
record fields. The same helper retrospectively replays the common 0.50
admission rule from the logged decision-time queue; this replay is not visible
to or used by a policy. No change was made to `ce04.py`, LinUCB, or any
scientific parameter.

Focused regression tests cover a logged reward without an update, P1 with no
updates, P2-only Beta updates, P3-only LinUCB updates, and injected updates
before feedback. The latter cases assert that validation raises, so the tests
would detect the targeted timing defect. Admission-replay tests also reject a
wrong selected probability and a false rejection despite an admissible agent.
The focused suite passed: **53 passed**.

The admission audit originally scanned all previous records for every arrival.
It was changed to a sorted per-agent event replay with binary searches; this
changes validation cost only, not the simulator or admission calculation.

### 5.2 Rerun and provenance

The rerun used exactly the 108 configurations returned by
`factorial_configs("pilot")`: seeds 0–2, N=12/24/48, H0/H1/H2, P0–P3. The
canonical scientific configuration hash remained
`c72bdca82906daa2118b415d3ba76d1fbfac87c47a1c3ee72fea7677e4b8a1b5`.
Execution used code commit `3071de45889dedeffa5e0d09edec54bcfa4dde0e`;
the validator-only source hash and configuration are recorded in the
[rerun artifact manifest](../../../results/experiments/hls_ce04_pilot_retry/attempt_02/artifact_manifest.json).
Environment remained Python 3.11.9, NumPy 1.26.4, SciPy 1.13.1, SimPy 4.1.2,
macOS arm64 / Apple M2 Max.

| Check | Result | Evidence |
|---|---|---|
| Exact configured matrix | PASS | 108 unique configurations; no campaign seeds. |
| Conservation and identity | PASS | Each of 108 replicas had arrivals = admitted + rejected and one unique record per generated task. |
| Assignment/completion and capacity | PASS | Every admitted task had one selected agent and one final completion; per-agent FCFS/non-overlap checks passed. |
| Deadline success definition | PASS | All task outcomes matched `correct AND completion <= deadline`; rejected tasks had no execution labels. |
| P0/P1/P2/P3 estimator separation and feedback timing | PASS | Effective-update traces passed for each replica. |
| No future information in P2/P3 | PASS | P2 update timestamps equal actual completion; P3 update timestamps equal observable completion or deadline. Policies do not receive the audit trace. |
| Common admission rule | PASS | Retrospective replay passed for each arrival in all replicas; selected agents met F≥0.50 and no rejection occurred when any agent met the cutoff. |
| H0–H2 mean competence | PASS | Each replica's task-family means were exactly 0.775 within 1e-12. |
| Resource/load scaling and drain | PASS | N restricted to 12/24/48; each trajectory used the configured 0.55N rate and simulation drained admitted tasks. |
| Reproducibility and pairing | PASS | Existing deterministic replay test passed; across the rerun, task identifiers matched in all 9 seed×scale blocks and all 12 composition×policy conditions within each block. Potential service/correctness are keyed by seed, N, task, and agent. |
| Metric domains / finite values | PASS | All per-replica metrics were finite and within their declared domains. |
| Recovery metric | EXCLUDED | Not calculated or replaced, as ordered in CE-04.5. |

The rerun completed in **185.90 s wall time**; summed replica CPU time was
**114.24 s**, and summed decision time was **91.22 s**. Process peak RSS was
**277,544,960 bytes** (platform-native `ru_maxrss`; macOS reports bytes).
There were zero validation failures and no warnings. Unique workload sizes
were 2,640–2,681 tasks for N=12, 5,249–5,306 for N=24, and 10,412–10,654 for
N=48 across the three seeds. Observed success-on-time rates ranged from
72.99% to 89.84% across conditions; these small-pilot descriptive values are
not inferential evidence and are not used to select a policy.

Full per-task `ExperimentRun` records are preserved locally as a 41 MB gzip
artifact at `results/experiments/hls_ce04_pilot_retry/attempt_02/` and are
identified by SHA-256 in the manifest. They were excluded from Git because of
their size. The 108-row replica metrics, exact config, validation summary,
and manifest are lightweight tracked artifacts. No historical output was
overwritten.

### 5.3 Execution incident and final disposition

An initial attempt at the corrected rerun stopped after a replica had passed
validation because the one-off CSV writer supplied RunConfig fields absent
from its declared columns. This was a runner serialization error after the
validation gate, not a simulator or protocol failure. The partial artifact and
incident record are preserved under
[`attempt_01`](../../../results/experiments/hls_ce04_pilot_retry/attempt_01/).
The writer was corrected, and a fresh, separate `attempt_02` executed all 108
conditions. The original CE-04.5 false-positive stop, this runner incident,
and the successful rerun remain separate records.

**Final technical-pilot status: APTO.** No claim is made about the superiority
of HLS, H0/H1/H2, or P0–P3. CE-04's separate full campaign (seeds 1000–1029)
was not run; no merge to `main` was performed.
