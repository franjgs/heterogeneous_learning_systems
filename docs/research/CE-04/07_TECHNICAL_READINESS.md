# CE-04 — Technical Readiness Inspection

**Inspection date:** 2026-10-26
**Inspected branch / baseline:** `feature/hls-laboratory-v1` /
`c8d5cd71fdeaca2ed59589c8a780bbca15b0c238`
**Updated documentary status:** 2026-10-26, after the CE supplied E1, E2, E3
and E3 addendum originals. The assessment below now records their contents
and decision differences; its code inventory remains based on the stated
baseline.
**Result:** PARTIAL — substantial components can be reused, but CE-04's
event-driven semantics and five unclosed specifications are not implemented.

## Source and reports

The first technical inspection found no expert originals in the branch or
conversation context then available. On 2026-10-26, the CE supplied all four
original texts, now incorporated verbatim in files 01–04. The decision record
and consolidated protocol distinguish those proposals from CE-approved
decisions; the originals have not been rewritten. See [CE decisions](05_CE_DECISIONS.md)
and [consolidated protocol](06_CE04_CONSOLIDATED_PROTOCOL.md) for the explicit
discrepancy record.

In particular, E3's first H0/H1/H2 profiles with match/mismatch accuracies
0.90/0.65 do not equal mean competence per task family. The CE adopted E1's
equal-per-task-mean criterion; E3's addendum later refers to E1's generator,
but E1 gives a possible parameterization rather than exact profiles/values.
Those remain pending. E3's first protocol has three policies and 27 cells;
the CE adopted four policy roles and 36 cells, consistent with E3's addendum.
The details of these differences are documented in [05_CE_DECISIONS.md](05_CE_DECISIONS.md).

## Component inventory

| Component | Source and verified semantics | CE-04 classification |
|---|---|---|
| Agent/competence representation | [`hls_lab_nk_geometry.py`](../../../src/hls/hls_lab_nk_geometry.py), `OrganizationConfigNK` / `OrganizationStateNK`, lines 48–126: arbitrary N×K IDs and competence matrices in [0,1], estimates, individual effort limits and shared budget; no worker busy/availability state. | **REUTILIZABLE** for competence arrays; service state needs adaptation. |
| Task representation/generation | [`hls_lab_nk_geometry.py`](../../../src/hls/hls_lab_nk_geometry.py), `ProblemSpecNK`, lines 165–201; [`hls_lab_nk_environment.py`](../../../src/hls/hls_lab_nk_environment.py), finite `DemandRegimeNK` and categorical process, lines 32–100, 170–198. Emits one task per discrete period. | **ADAPTABLE** for four family descriptors and phased proportions; not a Poisson workload generator. |
| Discrete-event execution | [`hls_lab_nk_execution.py`](../../../src/hls/hls_lab_nk_execution.py), `run_nk_production_sequence`, lines 274 onward, iterates frozen problems by period. | **NO DISPONIBLE** for arrival/service/completion event queues. |
| Queue, worker availability, deadlines | Search of Python sources found no FCFS queue, service-time event, busy-worker state, individual deadline or tardiness implementation. E2 recommends SimPy, but it is not declared in `pyproject.toml` and no CE-04 SimPy runner exists. | **NO DISPONIBLE**. |
| Static assignment | [`hls_lab_nk_assignment.py`](../../../src/hls/hls_lab_nk_assignment.py), `HungarianAssignmentOptimizerNK.optimize`, lines 59–112: static one-to-one unit assignment from supplied scores. N×K joint action enumeration in [`hls_lab_nk_geometry.py`](../../../src/hls/hls_lab_nk_geometry.py), lines 237–279, has M(K)^N catalog growth. | **ADAPTABLE** as static assignment baseline; not as a scheduler. General enumeration is unsuitable for N=12/24/48. |
| Competence estimation | [`hls_lab_nk_estimation.py`](../../../src/hls/hls_lab_nk_estimation.py), posterior initialization and production-observation assimilation, lines 25–114; observed-work productivity estimator in [`hls_lab_nk_nembhard_adaptive.py`](../../../src/hls/hls_lab_nk_nembhard_adaptive.py), lines 121–302. | **ADAPTABLE** after CE defines observed task outcome, estimator target and noise model. |
| Contextual policy | [`linucb.py`](../../../src/hls/linucb.py), `LinUCBDisjoint`, lines 11–95; [`hls_lab_nk_linucb_assignment.py`](../../../src/hls/hls_lab_nk_linucb_assignment.py), pair-score/selected-feedback adapter, lines 10–61. Nembhard adaptation is based on observed productivity with optional epsilon exploration, not CE-04 queue context. | **ADAPTABLE** primitives only; CE-04 P3 is not implemented. |
| Existing N×K P0/P1/P2 | [`hls_lab_nk_policies.py`](../../../src/hls/hls_lab_nk_policies.py), lines 106–242: production-only, fixed teaching and adaptive teaching. They do not implement CE-04's load, service-time and deadline objective. | **NO DISPONIBLE** for CE-04 policy definitions; do not reuse names as if equivalent. |
| Metrics/evaluation | [`performance_evaluation.py`](../../../src/hls/performance_evaluation.py), `EvaluationProfile` / `PerformanceEvaluator`, lines 24–72 onward: read-only aggregation of declared reward, CES, success, deficit, production, teaching and resources. No queue wait/tardiness/service metrics. | **ADAPTABLE** for run evaluation and new event-level measures after their definitions are frozen. |
| Statistics | Paired bootstrap helpers exist in study-specific modules including [`nembhard_campaign.py`](../../../src/hls/nembhard_campaign.py), `bootstrap_interval`, lines 1271 onward. No common CE-04 pipeline combining paired bootstrap, Holm and TOST was located. | **ADAPTABLE**; methods can be reused only with CE-frozen contrast family and replication unit. |
| Reproducibility | [`experiment_contract.py`](../../../src/hls/experiment_contract.py), `SeedRecord` / `ExperimentRun`, lines 64–78 and 142–205, records named seed streams, configuration, initial state, revision, events and metrics. N×K environment freezes policy-independent demand but uses one sequential process stream and coordinate emission stream ([`hls_lab_nk_environment.py`](../../../src/hls/hls_lab_nk_environment.py), 170–198). | **ADAPTABLE**; CE-04 needs independent event-level streams and exact pair/replay mapping. |

## Status of the five pending specifications

| Item | Status | Evidence |
|---|---|---|
| A. H0/H1/H2 composition generator preserving task means | **NO DISPONIBLE** | Matrix representation exists, but not this generator. The separate 12-agent/two-task proposal is not equivalent and is not substituted. |
| B. Exact heterogeneity parameters/profiles | **ADAPTABLE** | Generic N×K matrices and scenario-specific profiles exist; no CE-04 H0/H1/H2 values are established. |
| C. P2/P3 observed-results estimator | **ADAPTABLE** | Existing estimators learn from production observations or selected-work outputs, not a CE-04-defined result likelihood. |
| D. Contextual adaptive P3 | **ADAPTABLE** | LinUCB primitives and pairwise matching adapter exist; no full arrival/queue-aware P3, context, parameters or cadence. |
| E. Common P1/P2 decision function | **NO DISPONIBLE** | No shared competence + expected service time + load + deadline function. Existing P0/P1/P2 rank a different production/teaching action space. |

The CE dispositions do not close these five specifications. The consolidated
protocol records the CE-approved workload/factorial conditions and separately
labels the expert-original proposals that were not adopted.

## Protocol compatibility and limits

- N=12/24/48 are representable in the matrix containers, but this does not
  make exhaustive N×K action enumeration feasible: its candidate count grows
  as M(K)^N, with an explicit guard and no truncation. Hungarian assignment
  avoids that enumeration only for its narrower static unit matching.
- Four competence/task dimensions and multiple finite task types can be
  encoded, but task-family semantics and CE-04 generator are missing.
- Existing demand is one categorical task per discrete period; it cannot
  directly express Poisson arrivals, asynchronous service, FCFS queues or
  deadline completion.
- A time-indexed demand distribution can express three discrete mix phases,
  but the boundary convention and arrival-rate interpretation remain open.
- Per-agent and shared effort budgets exist; proportional resource scaling
  and queue capacity rules do not.
- Single-agent-per-task, no cooperation and no development can be imposed as
  restrictions in some existing action paths, but those paths do not provide
  event-driven worker service semantics.

## Reproducibility checks

- Named seed records and software revision/configuration fields are supported
  by ExperimentRun.
- Existing N×K environment trajectories are policy-independent and replayable;
  separate streams currently cover demand process and per-period emission,
  not CE-04's arrivals, task types, service outcomes and policy randomization.
- Existing results can be recorded by episode/period. No CE-04 event-level
  task result schema or paired potential-outcome store exists.
- Study-specific paired bootstrap code exists. The exact CE-04 replication
  unit, Holm family and TOST contrasts need to be frozen before execution.
- Focused existing-component suite: **128 passed** across seven NK geometry,
  environment, assignment, estimation, policy, LinUCB-adapter and adaptive
  Nembhard test modules. These tests do not validate CE-04 compatibility or
  its protocol.

## Minimum work and blockers

Implementation should reuse the competence containers, selected assignment
solver where mathematically applicable, observed-feedback primitives,
ExperimentRun/HLS-PEF and existing statistical helpers. It must add the
missing discrete-event queue/service model and event-level task records; these
are not incremental changes to the fixed-period runner. A defensible effort
estimate in person-days is not possible until the five open specifications
and operational semantics are closed.

The CE must close: (1) H0/H1/H2 construction and parameters; (2) the observation
model shared by P2/P3; (3) P3 method, context, parameters and cadence; (4) the
common P1/P2 decision objective; and (5) event/resource semantics, including
rate interpretation, phase boundaries, service duration, deadline boundary,
cost units, and statistical contrast/resampling definitions. No defaults are
chosen here. See the [pre-freeze protocol](06_CE04_CONSOLIDATED_PROTOCOL.md).

No code, experiment, pilot, or campaign was run as part of this inspection.

## CE-04.4 implementation status — 2026-10-26

**Current result:** IMPLEMENTED; focused validation passed; protocol approved;
**pilot and campaign not run**. This section supersedes the earlier readiness
blockers, which remain a record of the pre-CE-04.4 state.

### Implemented components

| Requirement | Implementation | Verification status |
|---|---|---|
| Mean-preserving H0–H2 competence matrices | `src/hls/ce04.py`, `competency_matrix` | Exact analytical construction; tests at N=12/24/48 check task-wise means 0.775, bounds and increasing variance. |
| Continuous-time demand and phase marks | `generate_workload` | Seeded Poisson rate 0.55N, arrivals in `[0,400)`, half-open phases, stable task IDs. |
| Potential service/correctness outcomes | `potential_service`, `potential_correct` | Keyed by replicate, N, task and agent with distinct stream IDs; repeatability tested. |
| FCFS event simulation | `run_replica`, SimPy resources | One resource per agent, one active task, FIFO requests, completion drain; focused arrival/conservation/non-overlap checks. |
| Common deadline admission | `deadline_probability_*`, `run_replica` | Same F and 0.50 cut for all policies; competence excluded from admission. |
| P0–P3 | `run_replica`, `_DelayedDisjointLinUCB`; additive `LinUCBDisjoint.observe_delayed` | Load, q×F, Beta(1,1) posterior and existing disjoint LinUCB equations with four-dimensional `F e_k` context/delayed reward. The original select/observe contract is unchanged. |
| Replica records | `to_experiment_run`, `run_factorial` | Existing `ExperimentRun` schema; task-level events and provenance; writer refuses to overwrite an existing output file. |
| Paired inference helpers | `paired_bootstrap`, `paired_contrast`, `holm_adjust`, `tost_equivalence`, `analyze_factorial` | Fixed 10,000 replicate-level bootstrap resamples; Holm and ±2 pp TOST are implemented. No inferential results have been produced. |

SimPy 4.1.2 is an explicit dependency in `pyproject.toml`. The existing
LinUCB production contract and HLS-PEF metric registry were not changed. The
current HLS-PEF success metric has different fixed semantics, so CE-04's
event-level success-on-time measure is stored in ExperimentRun and is not
misrepresented as a PEF metric.

### Deadline-probability numerical check

The fixed 25-case battery includes idle queues and active-service ages and
queue lengths around the admission boundary. The deterministic reference is
probability-mass convolution with 0.001 time-unit bins. Two reference cases
fall in `[0.45,0.55]`; their maximum absolute difference from the
conditional-residual two-moment lognormal approximation is **0.0038559621**.
The approved tolerance is **0.01**. The approximation therefore passes and
remains the runtime method. This is a numerical method check, not an HLS
performance experiment.

### Tests and execution boundary

Executed:

```text
PYTHONPATH=.:src pytest -q tests/test_ce04.py tests/test_linucb.py tests/test_hls_common_experiment_contract.py tests/test_hls_performance_evaluation.py
45 passed
```

The tests cover composition means/ranges, demand and stream reproducibility,
probability validation, delayed LinUCB feedback, queue non-overlap/order,
arrival preservation, admission threshold, delayed reward immutability,
ExperimentRun serialization and factorial sizes; existing ExperimentRun,
HLS-PEF and LinUCB checks also passed. No pilot or full-factorial
configuration was executed. No historical result or expert original was
modified.

### Remaining boundary

The approved primary protocol is implementable. E3's original text also
mentions post-demand-change “recovery” but does not operationally define its
stable reference; CE-04.4 did not provide that reference. No recovery value is
therefore emitted or used to tune policies. If retained as a confirmatory
measure, its reference needs CE clarification before the pilot; it is not a
blocker for the approved primary/confirmatory outcomes. The pilot itself still
requires separate CE authorization; the full campaign remains separately
gated. LinUCB has no random exploration draw, so its approved exploration
seed namespace is recorded as reserved/unused.

The pilot workload is about 665,280 arrivals and 23.95 million agent
admissibility evaluations, plus about 5.99 million P3 candidate score
calculations. A provisional runtime estimate is **10–40 minutes on the
workspace host (Apple M2 Max)**, derived from operation counts, not benchmarked
execution; no campaign or pilot timing was performed.
