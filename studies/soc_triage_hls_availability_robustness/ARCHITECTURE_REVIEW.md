# SOCTRA–HLS architecture review

## External JSON loader update

An optional loader is now implemented in `scenario_loader.py`. It constructs
the existing frozen `execution_api.py` resources, teams, per-level policy
settings, deadlines, and time settings from schema version 1 JSON. It resolves
the checked-in Q1 classifier operating points and prevalence through explicit
reference IDs, without importing the historical campaign runner, consuming
randomness, or changing globals. `LoadedScenario.request_for()` builds the
existing `SimulationRequest` when the caller supplies existing generated
`Alert` records. Thus alert generation remains a separate established step;
the JSON loader does not invoke the private generator itself.

Three examples are in `config/`: a historical resource/reference snapshot and
two synthetic organizations (continuous and individual mixed shifts). The
historical example is representative of the n_L2=3 roster and records original
campaign provenance; it does not replace campaign settings, cover every
historical condition, or regenerate historical results. Synthetic examples
are not descriptions of GMV-CERT. Calendars currently support repeating
weekly windows, including overnight shifts; holidays and absences are outside
scope. The loader now requires a complete alert-ID-to-severity sidecar for
`severity_map`; use `provided_absolute` to keep generated Alert deadlines.
Priority interruption, reassignment, early/late escalation, new policy
algorithms, and campaign migration remain future work. See
`CONFIGURATION_GUIDE.md` for schema and use.

**Original review baseline:** `research/soctra-hls-availability-robustness` at `2baef4057e8618416130e27924a37f4336e2db69`
**Stage 1–2 implementation baseline:** `a60b1e65772ad1032b882695c57ee765f8713d47`
**Scope:** the original review proposed an architecture; the update below records the two implemented stages. No new campaign was run. SOCTRA, policies, historical results, and LaTeX remain unchanged.

## Implementation update: stages 1 and 2

The minimum configuration and adapter layers now live in `execution_api.py`, with examples in `EXECUTION_API.md`. Frozen types cover analyst resources (reusing `Analyst`), immutable competence/eligibility/service maps, individual calendars, L1/L2 team membership, D1/P1/WAPS plus WAPS parameters, admission/evaluation horizons, deadline-offset metadata, seed, time scale, and an environment-only realization payload. Validation runs deterministically before a backend call and consumes no random values. It checks identifiers and team membership, competence/service keys, positive service durations, calendar validity, horizons, deadlines and policy compatibility. Teams accept independent positive analyst counts and different per-person resources.

`ExecutionBackend` is a small protocol implemented by `ContinuousBackend` and `CalendarBackend`. They call the existing `rq1_allocation.simulate` / frozen hidden-work L2 function and `availability_engine.simulate`, respectively. The native engine result is always retained. Both expose common assignment/task/decision fields; `None` marks task-level data unavailable from a source engine. Continuous execution does not synthesize a lifecycle ledger or work segments; calendar execution forwards the native episodes and service segments. Existing signatures, loops, policies, metrics, generators and JSON campaign configs remain unchanged. The environment realization is not included in dispatcher arguments.

These changes implement only the architecture plan's type/configuration and adapter steps. They do **not** remove campaign module globals, temporary horizon mutation or D1 monkey-patching; those remain concrete stage-3 refactoring targets. No metric evaluator was introduced. The adapters are optional and have no callers in historical campaigns. Focused fixtures compare each adapter's retained native result to a direct call of its engine for D1, P1 and WAPS, and exercise immutable inputs, validation, scale, calendar suspension and hidden-label isolation. No scientific campaign was run.

Still open: explicit campaign dependency injection to remove globals/private helper imports; removal of monkey-patching without changing D1; extraction of campaign composition; metric evaluator separation; task-level continuous lifecycle records if the source engine later exposes them. Interruption, reassignment, escalation timing, new policies, reporting and operational calibration remain out of scope.

## 1. Architecture as it exists

The current experiment is assembled across research modules rather than represented as one explicit system configuration. Its data path is approximately:

```text
Q1 trace generator + fixed classifier operating point
       │  arrival, alert class, recommendation, hidden synthetic need
       ▼
L1 roster/services ── historical allocation engine ── L1 assignment/completion
       │                                                  │
       └──────────────── recommendation + completion ────┘
                                                          ▼
                                               L2 routed arrivals
                                                          │
                ┌─────────────────────────────────────────┴──────────────────┐
                ▼                                                            ▼
      frozen continuous L2 engine                               calendar L2 engine
      (hidden FP service, Q1 study)                            (suspend/resume)
                └──────────────────────────┬─────────────────────────────────┘
                                           ▼
                              campaign-level metrics/bootstrap
```

This is a study-specific composition. It is not a single reusable simulator API, and its JSON configuration describes only part of the full experiment.

### Alert generation and SOCTRA evidence

`studies/soc_triage_hls_q1_integration_evidence/run_primary_campaign.py` calls the frozen Q1 generator and keeps campaign constants in module globals loaded from `primary_campaign.json`. The availability runner imports that campaign module as `old`, then reaches through it to `old.frozen._make_trace`, `_expected_class_factors`, `_expected_route_mix`, and `_trace_hash`. `fp_workload_engine.py` supplies an experiment-only L2 loop in which hidden need affects realized service internally; dispatchers receive ex-ante service information. Classifier operating points and per-alert recommendations are therefore coupled to the Q1 evidence code rather than represented as an independent generator object.

In the availability campaign, `availability_campaign.json` contains classifier operating points, alpha values, load values, roster sizes, policy names, deadlines, horizons and WAPS parameters. Severity-to-deadline mapping is applied in `_make_trace` after trace generation. The trace generator and prevalence are still imported from the Q1 module; `PI`, project names/mix, service assumptions, eligibility, and roster construction are imported from other study modules. Analyst competency and service maps are built in Python rather than fully declared in this JSON file.

### Human resources and composition

`Analyst` holds identity, eligibility and competence; service maps are separate dictionaries keyed by analyst and task class. The campaign uses `build_roster` and constants from `soc_human_ai_organization.soc_parametric_baseline`. The L1 roster and service map are constructed once; L2 rosters are rebuilt for sizes 2, 3 and 4. Calendar identity is resolved in campaign code from a string (`L2_24x7` or `L2_8x5_Mon_Fri_09_17`) to constants in `availability_engine.py`, then copied to each L2 analyst. This is adequate for the specified experiment but does not yet describe arbitrary L1/L2 compositions in one external scenario file.

### Policies and dispatch

`src/hls/rq1_allocation.py` contains the established event engine and dispatch implementations. The frozen Q1 L2 engine imports `_dispatch_d1` and `_dispatch_local_priority` from that module. The calendar engine separately imports those dispatchers and implements its own WAPS-style D1/P1 hysteresis and event loop. Campaign code maps `WAPS` to `HLS-B` for the continuous path, while the calendar path accepts `WAPS` directly. These paths currently share underlying dispatch helpers but duplicate part of the policy-mode and dispatch orchestration.

`D1`, `P1` and `WAPS` are experiment labels; in the historical allocation module the broader public policy vocabulary is different. The campaign's mapping between names and engine APIs is implicit in `_run_l1` and `_run_condition`. No policy algorithm needs to change for the proposed architecture: the interface should wrap and name existing behavior.

### Execution engines and outputs

There are three relevant execution surfaces:

1. `rq1_allocation.simulate(...)` is the fixed-policy historical engine. It accepts an admission horizon and optional drain period, snapshots metrics at the admission boundary and at the end of drain, and returns `SimulationResult` with its established assignment and `Metrics` structures.
2. `rq1_allocation.AllocationSession` exposes incremental events, pending/running/dispatching collections and repeated dispatch calls. It supports roster activation schedules, but those are discrete active-roster changes, not weekly work calendars that suspend and resume service.
3. `availability_engine.simulate(...)` is a separate calendar event loop. Its `horizon` both filters input arrivals (`arrival < horizon`) and acts as the execution cutoff. It returns its own `Outcome`, `Episode`, `work_done_by_alert`, and `work_segments`; those result types are not the historical `SimulationResult`/`Metrics` contract.

The availability campaign uses a frozen continuous fast path for L2 and the calendar engine for 8x5. L1 remains on `rq1_allocation.simulate`. Thus the calendar engine's continuous behavior is not used as a replacement for the frozen continuous reference.

### Metrics

The historical engine owns `_metrics` and `Metrics`. The availability engine returns execution facts and lifecycle statuses, but does not apply the campaign's full metric definitions. `run_availability_campaign.py` constructs L1/L2 waits, backlogs, work, utilization, late fractions, FP-induced work and `S_plus` inline. It also translates engine outputs into status counts and uses different calculations for the continuous and calendar arms. `S_plus` is the existing synthetic endpoint: a hidden L2 need, recommended positively, and completed by its natural-time deadline, divided by all synthetic L2 needs. A deadline equality counts as on time. Queue, suspended, running, completed, and completed-late labels are used by the availability extension; any common interface must preserve those exact meanings and the campaign's metric boundary rules.

## 2. Concrete dependencies and risks

| Coupling | Current location | Concrete risk |
|---|---|---|
| Q1 generator and trace assumptions | `run_availability_campaign.py` imports `run_primary_campaign` and calls `old.frozen.*` helpers | A private helper or global change in the historical study can silently change a new scenario; importing the campaign module also imports its own global configuration and model assumptions. |
| Temporary horizon override | `_make_trace` writes `old.frozen.CONFIG["horizon_h"] = H`, then restores it in `finally` | Process-global mutation is not safe for concurrent episodes or multiple campaigns in one interpreter. Exceptions are restored, but another caller can observe the temporary value. |
| Global campaign configuration | Module-level `CONFIG`, `H`, `CUTOFF`, `PI`, `OUT` in both campaign entry points | Import order and process lifetime influence behavior; a caller cannot readily run two independent configs side by side. |
| Dispatcher monkey-patching | `run()` swaps `_dispatch_d1` in `rq1_allocation` and `availability_engine`, then restores it in `finally` | Shared module state is process-global and unsafe for threads or nested runs. It patches only those imported names; `fp_workload_engine` imports the dispatcher by value and remains a separate path. A failure before entering the protected block could leave setup state difficult to reason about. |
| Hidden Q1 dispatcher imports | `fp_workload_engine.py` and `availability_engine.py` import private functions by value | Each module can retain a different function object after a patch or refactor. The source of policy semantics is not visible from the engine's public API. |
| WAPS orchestration duplication | `fp_workload_engine.py`, `availability_engine.py`, and mapping in campaign code | Threshold/window semantics can drift, and the policy label differs (`WAPS` vs `HLS-B`) despite intended continuity. |
| Repeated L1/L2 composition in campaign | `_run_condition` and nested loops in `run()` | Alert routing, actual-vs-forecast service, alpha, calendars, and policy names are stitched together procedurally; changing one layer can break pairing or leak hidden labels. |
| Roster sources outside scenario JSON | `soc_parametric_baseline.py`, `calibrate_a1_scenarios.py`, `build_roster` | A JSON campaign file alone is insufficient to reproduce the scenario; analyst identity, eligibility, competence and effective service originate in imported Python constants and functions. |
| Different engine result types | `SimulationResult`/`Metrics` vs `Outcome`/`Episode` | Campaign metrics contain engine-specific translation branches; subtle endpoint differences can appear while aggregate names remain the same. |
| Admission and execution horizons | Historical API separates admission and drain; calendar API uses a single `horizon` for both admitted rows and execution cutoff | Reuse outside the current campaign can omit late arrivals or incorrectly treat an accounting cutoff as an admission boundary. A future common request needs distinct horizons without changing either current API's interpretation. |
| Status ownership and counts | Calendar state in `availability_engine`; continuous state inferred in campaign runner | The same public status is derived differently by the two arms. A normalized result view must preserve, not reinterpret, this distinction and its cutoff behavior. |
| Metrics mixed with experiment orchestration | Large `_run_condition` function | Hard to test independently whether metric definitions, episode composition and engine behavior remain stable. |

The campaign's `try/finally` restoration and the full reference regression reduce immediate risk, but do not remove the concurrency and coupling risks above. The full regression's 24x7 arm intentionally calls the frozen continuous backend to preserve historical tie ordering; this is a compatibility boundary, not proof that both event loops are interchangeable for all possible traces.

## 3. Proposed common execution interface

Introduce a small **adapter contract**, not a replacement engine. Keep both existing public APIs and their current defaults unchanged. The common types should live in the new study package initially; migration into a shared library can be considered later.

### Immutable request

`SimulationRequest` (proposed name) should carry explicit values rather than import campaign globals:

- admitted `Alert` records, each retaining the existing ID, class, arrival and absolute natural-time deadline;
- immutable analyst records and per-analyst/per-class ex-ante service and competence maps;
- one calendar per analyst (continuous calendar is an explicit always-available value);
- existing policy ID and its unchanged policy configuration;
- seed/RNG initialization;
- admission horizon and execution/accounting cutoff as separate fields;
- optional realization-only service scale / environment outcome map, explicitly unavailable to the policy;
- time unit/scale metadata, defaulting to current elapsed hours.

The request must not make hidden need, TP/FP, or future arrivals available to a dispatcher. A trace/provider may reveal arrivals incrementally, but it must preserve current draw order and per-alert pairing when used with existing campaigns.

### Backend protocol and result contract

Proposed `ExecutionBackend.run(request) -> ExecutionResult`:

- `ContinuousBackend` adapts the frozen historical simulation path. It calls existing code and maps its output to the common result view; it does not reimplement or change its event ordering, dispatchers or metrics.
- `CalendarBackend` adapts the existing availability event loop, with no new scheduling features in this review.
- The result view exposes exact assignment records; start/completion instants; service-work segments; analyst owner; effective work and remaining service; suspension duration; final status at cutoff; policy decisions/switches already emitted by the engine; and a reference to the engine-native result for audit.
- A `MetricEvaluator` consumes a normalized result and the same trace/environment facts, then applies the existing metric definitions. Initially the historical evaluator remains authoritative for historical outputs; the availability evaluator is a named adapter that must match those definitions where comparable.

The common contract should be intentionally narrow. It must not offer interruption, handoff, escalations or a new policy hook as operational behavior yet. A backend capability descriptor can report calendar support while the continuous adapter declares no suspension behavior. The adapter boundary exists to make composition explicit, not to make the engines falsely identical.

## 4. External configuration and dependency direction

The target scenario should be serializable and validated before simulation, with distinct sections:

```yaml
trace:
  source: q1_frozen
  seed: 711000000
  classifier_point: standardized_lightgbm_apc_symmetric
  prevalence_id: historical_q1
organization:
  levels:
    L1: {backend: continuous, analysts: [L1-01, L1-02]}
    L2: {backend: calendar, analysts: [L2-01, L2-02]}
  analysts:
    L2-01:
      eligible_classes: [class_a, class_b]
      competence: {class_a: 0.8, class_b: 0.6}
      service_hours: {class_a: 0.4, class_b: 0.8}
      calendar: {weekly_windows: [[Mon, 9, 17], [Tue, 9, 17]]}
dispatch:
  L1: {policy: D1}
  L2: {policy: WAPS, config_ref: waps_historical}
time:
  unit: hour
  admission_horizon: 168
  evaluation_cutoff: 240
deadlines:
  mode: severity_map
  offsets: {High: 12, Medium: 24, Low: 72}
```

This is an illustration, not a new accepted config schema. A schema should support arbitrary weekly days/windows and per-analyst calendars; continuous coverage should be a first-class value. References to a historical roster may remain for exact replay, but their resolved analyst/service values should be included in the generated execution manifest. Validate that IDs, competence, eligibility, service, calendars, policies and horizons are mutually consistent before constructing engines.

Desired dependency flow is one-way: configuration resolves into immutable domain objects; trace generation yields alerts and recommendations; composition creates level-specific requests; policies consume only public queue/roster/ex-ante service snapshots; backends emit execution facts; metric evaluators consume those facts. The source generator, policy implementation and backend should not import each other's campaign globals.

## 5. Future extension points (specified, not implemented)

- **Priority interruption:** a future `InterruptionRule` can observe a public dispatch snapshot and emit an explicit interrupt request. It must be distinct from calendar unavailability and must not silently change D1/P1/WAPS ordering. No interrupt behavior is enabled now.
- **Task reassignment:** a future `ReassignmentRule` can explicitly change owner at a documented event, with completed work, remaining work and ownership history retained. Default remains persistent owner and no transfer.
- **Early/late escalation:** a future `EscalationRule` can govern L1→L2 timing using only information observable at that time. It must be opt-in and cannot change current routing, SOCTRA recommendation, hidden-label isolation or current campaigns.
- **New organizational policies:** a future `DispatchPolicy` adapter can consume the same immutable public snapshot and return assignments. Existing D1/P1/WAPS adapters remain frozen and regression-tested; new policy IDs/configs are separate additions.

These are API seams only. This phase does not implement them or add data/decisions to existing experiments.

## 6. Minimum staged refactor plan

1. **Freeze contract fixtures.** Record representative trace, recommendation, assignment, completion, work, backlog, utilization, status, deadline and `S_plus` fixtures for the historical engine and completed availability campaign. Keep the existing full regression and all historical files read-only.
2. **Define types and config loader only.** Add immutable request/resource/config records and schema validation. No engine behavior changes; default values map exactly to the current configuration.
3. **Wrap engines.** Add continuous and calendar adapters that call existing functions. Preserve engine-native outputs and compare normalized fields against fixtures. Do not rewrite dispatch algorithms or merge event loops.
4. **Move campaign composition behind explicit parameters.** Extract functions that currently read globals/private helpers. First retain the original generator and imported defaults via adapters; then pass explicit trace/config values. Avoid module monkey-patching by passing a dispatcher callable to an adapter boundary, or by a scoped private dependency at construction; never mutate shared module globals. The historical engine's dispatcher default remains exactly the current function.
5. **Separate metric evaluation.** Move current calculations out of the large campaign function into named evaluator functions and compare bit-for-bit/exactly where required. Do not change status strings, deadline equality, endpoint denominator, or cutoff inclusion.
6. **Prove compatibility at each stage.** Run focused adapters, then the complete 43,200-episode reference regression, then a small paired calendar fixture. Do not launch scientific campaigns as part of architecture plumbing. Any divergence blocks the stage until explained and accepted.

This plan is deliberately incremental. A broad rewrite, generic plugin framework, or unified event engine is not justified by the current requirements.

## 7. Backward-compatibility guarantees

The architecture proposal requires these invariants for any later implementation:

1. The current `rq1_allocation.simulate` function signature, defaults, event order, RNG use, dispatch decisions, `Metrics` definitions and return contract remain unchanged unless a separately reviewed versioned API is added.
2. The frozen Q1 generator, recommendation mechanism, seed interpretation and historical config/result files remain immutable inputs. No regenerated output replaces historical files.
3. Existing D1/P1/WAPS algorithms, aliases and threshold semantics are not refactored as part of the adapter work. Any adapter maps names to existing implementations and is checked with decision/assignment fixtures.
4. The continuous adapter delegates to the existing engine. Calendar-enabled behavior is opt-in; requesting the old configuration must reproduce the complete historical outputs within the already documented tolerances.
5. `Alert.deadline` remains an absolute natural-time instant; completion exactly at deadline remains on-time. Admission horizon, execution cutoff, queue/status vocabulary, and `S_plus` definition retain their current meanings.
6. Policies see no hidden need, TP/FP label, or future arrival data. Realized service remains inside the environment.
7. The configuration loader itself has no random draws or side effects. Resolved config and source hashes are recorded before execution.
8. Compatibility is claimed only for fields and conditions actually compared. An adapter-level smoke test alone cannot justify campaign-wide equivalence.

## 8. Deliberate non-goals

This review does not modify SOCTRA, alert features, classifiers, recommendations, D1/P1/WAPS, status/deadline definitions, human behavior, historical outputs, or LaTeX. It does not add interruption, reassignment, early/late escalation, client reporting, leave/holiday rules, external waits, new policies, or any GMV-CERT operational claim. Calendars and staffing values remain generic synthetic scenario inputs.
