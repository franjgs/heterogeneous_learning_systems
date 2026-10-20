# HLS-G0-C6 — Exploratory Campaign Report

**Anticipatory Capability Development under Stochastic Demand**  
Date: 19 October 2026  
Status: exploratory campaign completed; not confirmatory.

## A. Configuration and evidence

`HLS-G0-C6` was not previously assigned in the experiment catalogue or
source search. This is the experiment identifier, not implementation of the
separately catalogued synthetic capability C6 (information/coordination
restrictions).

The run uses the existing G0/RQ0 environment and bounded replay runner in
[e1_minimum.py](../../src/hls/synthetic/e1_minimum.py), with exact solvers in
[exact.py](../../src/hls/synthetic/exact.py). It crossed:

| Factor | Levels |
|---|---|
| Agents / tasks / horizon | 2 / 2 / 4 |
| A1 development intensity `eta` | 0, 0.1, 0.75 |
| Demand | stationary; changing at periods 2–3 |
| Paired seed blocks per cell | 20 |
| Policies per trajectory | BEST_STATIC, MYOPIC, STRONG_SEP, HLS |

Stationary demand assigns each task probability 0.5 each period. Changing
demand uses `(0.8, 0.2)` for tasks `(1, 2)` in periods 0–1 and `(0.2, 0.8)` in
periods 2–3. The same 20 seed IDs are used in all six cells; demand and
opportunity use independent derived seeds within each block. Total:
6 cells × 20 = **120 exogenous trajectory records** and **480 policy
evaluations**. Each record stores its task path and opportunity-uniform tape.

Initial competence is `((0.8, 0.8), (0.6, 0.6))` for agents `(M1, M2)` and
tasks `(1, 2)`. Operational reward is the assigned agent's competence for
the current task. A1 development targets task 1 and updates the learner as
`c' = c + eta(1-c)`. Initial development budget is 1; one non-null action
consumes the full budget. Objective development cost is 0 and `beta=1`, so
budget use and objective cost are distinct. The common horizon reward
includes the configured terminal reward for task 1. Each period assigns the
task to one agent; there is no additional operational resource constraint.

The inherited A1 opportunity kernel has baseline 0, `rho=1`, and executor
opportunity values 0 for M1 and 1 for M2 for both tasks. Thus opportunity is
deterministically unavailable after M1 and available after M2. The same
uniform tape is replayed and the Bernoulli threshold is applied after each
policy's action, a valid common-shock coupling. **Here that coupling is
vacuous because probabilities are only 0 or 1.** The experiment tests
stochastic demand, not non-degenerate stochastic opportunity availability.

The trajectory-level, machine-readable evidence is
[`exploratory_results.json`](../../results/experiments/hls_g0_c6/exploratory_results.json).
The runner is [`run_hls_g0_c6.py`](../../experiments/run_hls_g0_c6.py); it
refuses to overwrite an existing output. The JSON records configurations,
seeds, sampled task paths, opportunity tapes, policy identities, traces,
rewards, costs, exact expected values, paired comparisons, execution times,
and provenance hashes.

## B. STRONG-SEP verification

The canonical routing restriction is that an operational action must belong
to the immediate operational-reward argmax set. Canonical HLS synthetic
definitions require ties to be exposed/frozen or resolved by an explicit
coordination rule; arbitrary action-order tie-breaking is not justified.
See [HLS_SYNTHETIC_ENVIRONMENT.md](../experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md)
and [rq0_routing_integration_boundaries.md](../theory/rq0_routing_integration_boundaries.md)
for the policy class and tie semantics.

The executed STRONG_SEP policy uses the strongest continuation-aware rule
admissible within that definition: maximize continuation value **only among
current immediate-reward maximizers**. It never selects a lower-immediate-
reward action and is not SEP-Omega. The coordination rule is recorded in its
policy identity. Regression test
`test_strong_sep_uses_continuation_only_to_resolve_immediate_ties` constructs
a tie where continuation selects the tied action with higher future value.
No routing ties occurred in the campaign, so this rule did not alter its
results; MYOPIC and STRONG_SEP routed identically in all observed periods.

## C. Validation

Focused tests for the demand solver, replay harness, resource constraints,
dynamic demand, and reference fixtures passed (**101 tests**). Then the full
synthetic suite passed (**272 passed**). `ruff check` passed on the relevant
implementation, tests, and runner; `git diff --check` passed. The saved JSON
parses and contains six cells, 20 records per cell, 120 total seed/cell
records, and four policy records per trajectory. No full E1 campaign or
other campaign was run.

Each empirical mean was checked against the exact expected value calculated
for that policy, initial state, and demand law. All non-degenerate empirical
means lay within descriptive two-sided 95% Student-t intervals (df=19);
zero-variance cases matched exact values within floating-point tolerance.
This is a solver/replay consistency check, not a policy significance test.

## D. Policy performance

Exact expected cumulative objective and empirical mean over 20 paired paths:

| Demand | `eta` | BEST_STATIC exact / mean | MYOPIC exact / mean | STRONG_SEP exact / mean | HLS exact / mean |
|---|---:|---:|---:|---:|---:|
| Stationary | 0 | 4.000 / 4.000 | 4.000 / 4.000 | 4.000 / 4.000 | 4.000 / 4.000 |
| Stationary | 0.1 | 4.000 / 4.000 | 4.000 / 4.000 | 4.000 / 4.000 | 4.000 / 4.000 |
| Stationary | 0.75 | 4.016 / 4.013 | 4.000 / 4.000 | 4.000 / 4.000 | 4.175 / 4.138 |
| Changing | 0 | 4.000 / 4.000 | 4.000 / 4.000 | 4.000 / 4.000 | 4.000 / 4.000 |
| Changing | 0.1 | 4.000 / 4.000 | 4.000 / 4.000 | 4.000 / 4.000 | 4.000 / 4.000 |
| Changing | 0.75 | 4.005 / 4.005 | 4.000 / 4.000 | 4.000 / 4.000 | 4.130 / 4.108 |

At `eta=0` and `0.1`, the four exact expected objectives coincide at 4.0 in
both demand regimes. At `eta=0.75`, exact HLS exceeds BEST_STATIC by 0.1594
under stationary demand and 0.1246 under changing demand; it exceeds MYOPIC
and STRONG_SEP by 0.175 and 0.130 respectively. These are exact model
expectations, not estimates from the sample paths.

## E. Paired comparisons

HLS-minus-baseline differences at `eta=0.75`:

| Demand | Comparator | Mean paired difference | Sample SD | HLS higher / lower (n=20) |
|---|---|---:|---:|---:|
| Stationary | BEST_STATIC | 0.1250 | 0.0803 | 18 / 2 |
| Stationary | MYOPIC | 0.1375 | 0.1366 | 16 / 4 |
| Stationary | STRONG_SEP | 0.1375 | 0.1366 | 16 / 4 |
| Changing | BEST_STATIC | 0.1025 | 0.0413 | 20 / 0 |
| Changing | MYOPIC | 0.1075 | 0.1238 | 15 / 5 |
| Changing | STRONG_SEP | 0.1075 | 0.1238 | 15 / 5 |

All paired differences and routing coincidences are in the JSON. They are
descriptive only; no hypothesis test or confirmatory claim is made.
BEST_STATIC is strong in its class: its task-to-agent map is optimized over
the complete demand law before test trajectories, while development remains
state-responsive and uses exact continuation. At high development its map is
task 1→M2, task 2→M1. It is therefore a static-routing baseline, not a
wholly fixed organization.

## F. Computational cost

Exact construction of all four policies took approximately 0.0010–0.0018 s
per cell in this runtime. Mean execution time per four-period trajectory was
about 0.020–0.030 ms per policy. These are small-run local timings, not
benchmarks. Construction time per cell and per-policy execution means are
saved in the artifact.

## G. Development, saturation, and coincidence

There were zero routing ties. MYOPIC and STRONG_SEP coincided in all 480
policy-period comparisons. HLS also coincided with them on every decision
for `eta≤0.1`. At `eta=0.75`, HLS routing coincidence with MYOPIC/STRONG_SEP
was 75% in both demand regimes. BEST_STATIC coincidence with HLS was 60% in
stationary and 73.8% in changing demand. Other pairwise values are saved.

No competence reached 1.0. With zero or moderate development, every policy
chose null development throughout this setup. At high intensity HLS consumed
the one-unit development budget in every path; BEST_STATIC did so in 18/20
stationary and 20/20 changing paths. HLS null-development frequency was
0.75 per period (one development in each four-period path); BEST_STATIC's
was 0.775 stationary and 0.75 changing. MYOPIC and STRONG_SEP never
developed. Objective development cost was always zero by design; resource
use is reported separately.

The high-intensity advantage is associated with joint routing/development
continuation decisions in this A1 opportunity structure. It is not evidence
that nonstationarity caused the advantage: the gap also occurs under
stationary demand, and this small design does not isolate demand change as a
causal factor.

## H. Limitations

- Only two agents, two tasks, four periods, one initial competence matrix,
  one development budget, and one opportunity profile were used.
- Opportunity outcomes are deterministic conditional on routing; genuinely
  stochastic opportunity coupling remains untested.
- `eta=0.75` and demand distributions are exploratory, not calibrated.
- BEST_STATIC fixes routing by task type but optimizes development
  adaptively; do not call it a wholly fixed policy.
- STRONG_SEP's continuation tie rule was tested but no campaign ties occurred.
- Twenty paths per cell do not support confirmatory generalization. The
  exact-value interval check does not test policy superiority.
- HLS knows the model and demand law, but not future realized demands. It is
  a finite-horizon nonclairvoyant optimal reference, not an online learner.
- This is synthetic evidence, not reproduction of an external paper.

## I. Recommendation

**GO — for bounded follow-up investigation, not a confirmatory campaign.**

This instance is discriminating: the zero/moderate-development controls
produce equality, while high development yields a positive exact-value gap
for HLS over optimized static routing and immediate-reward policies. The
paired paths show the same pattern without solver/replay inconsistency.
That justifies further investigation of the mechanism and its boundary
conditions, but not a general adaptive-superiority claim or a claim that
nonstationarity is responsible.

Before a broader study, the PI should decide whether non-degenerate
opportunity uncertainty is required. If it is, specify that probability
structure separately; do not silently substitute one. Preserve this run as
exploratory evidence.

## Reproduction

From the repository root:

```sh
PYTHONPATH=src pytest -q tests/synthetic
ruff check src/hls/synthetic/exact.py src/hls/synthetic/e1_minimum.py tests/synthetic/test_e1_minimum.py experiments/run_hls_g0_c6.py
PYTHONPATH=src python experiments/run_hls_g0_c6.py
```

The runner writes to `results/experiments/hls_g0_c6/exploratory_results.json`
using exclusive-create semantics and refuses to overwrite it. Do not rerun
against the archived output path.
