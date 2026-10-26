# CE-04 — Technical Readiness Inspection

**Inspection date:** 2026-10-26
**Inspected branch / baseline:** `feature/hls-laboratory-v1` /
`c8d5cd71fdeaca2ed59589c8a780bbca15b0c238`
**Result:** PARTIAL — substantial components can be reused, but CE-04's
event-driven semantics and five unclosed specifications are not implemented.

## Source and reports

The CE instruction reports that the Mega PI authorized CE-04 and that E1, E2,
E3 and an E3 addendum were received on 2026-10-26. None of those original
reports or a CE-04 protocol file is present in the inspected branch. Their
contents are not reconstructed here. The decision record and pre-freeze
protocol contain only the decisions and parameter values explicitly supplied
by the CE. See [CE decisions](05_CE_DECISIONS.md) and
[consolidated protocol](06_CE04_CONSOLIDATED_PROTOCOL.md).

## Component inventory

| Component | Source and verified semantics | CE-04 classification |
|---|---|---|
| Agent/competence representation | [`hls_lab_nk_geometry.py`](../../../src/hls/hls_lab_nk_geometry.py), `OrganizationConfigNK` / `OrganizationStateNK`, lines 48–126: arbitrary N×K IDs and competence matrices in [0,1], estimates, individual effort limits and shared budget; no worker busy/availability state. | **REUTILIZABLE** for competence arrays; service state needs adaptation. |
| Task representation/generation | [`hls_lab_nk_geometry.py`](../../../src/hls/hls_lab_nk_geometry.py), `ProblemSpecNK`, lines 165–201; [`hls_lab_nk_environment.py`](../../../src/hls/hls_lab_nk_environment.py), finite `DemandRegimeNK` and categorical process, lines 32–100, 170–198. Emits one task per discrete period. | **ADAPTABLE** for four family descriptors and phased proportions; not a Poisson workload generator. |
| Discrete-event execution | [`hls_lab_nk_execution.py`](../../../src/hls/hls_lab_nk_execution.py), `run_nk_production_sequence`, lines 274 onward, iterates frozen problems by period. | **NO DISPONIBLE** for arrival/service/completion event queues. |
| Queue, worker availability, deadlines | Search of Python sources found no FCFS queue, service-time event, busy-worker state, individual deadline or tardiness implementation. | **NO DISPONIBLE**. |
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
estimate in person-days is not possible until the expert originals and open
specifications are incorporated.

The CE must close: (1) H0/H1/H2 construction and parameters; (2) the observation
model shared by P2/P3; (3) P3 method, context, parameters and cadence; (4) the
common P1/P2 decision objective; and (5) event/resource semantics, including
rate interpretation, phase boundaries, service duration, deadline boundary,
cost units, and statistical contrast/resampling definitions. No defaults are
chosen here. See the [pre-freeze protocol](06_CE04_CONSOLIDATED_PROTOCOL.md).

No code, experiment, pilot, or campaign was run as part of this inspection.
