# HLS Laboratory — Current Roadmap

**State reviewed:** 23 October 2026. **Working branch:** `feature/hls-laboratory-v1`.
**Purpose:** current entry point for building the laboratory. This roadmap
summarizes evidence and proposes engineering gates; it does not authorize a
campaign or replace historical records.

> **Superseding status note — 23 October 2026:** Hito 2.2, the deterministic
> S4 N×K vertical integration, is complete for the audited Bellman reference.
> S3b-E1 is closed; the budgeted-routing campaign and the initial/corrected
> MMLU plus DCS-LA pilots are recorded as completed, bounded research, not as
> authorization to extend them. Earlier roadmap paragraphs below that call
> Hito 2.2 or S3b-E1 pending preserve their original decision-time context and
> are superseded by this note and the dated execution log. The canonical
> scientific summary is [HLS_CURRENT_STATE.md](../HLS_CURRENT_STATE.md).
> There is no currently authorized next experiment in this roadmap.

## 1. Purpose and operating principle

HLS is being built as a laboratory for representing heterogeneous systems,
formulating organizational problems, composing decision mechanisms, and
evaluating their outcomes. The present objective is laboratory capability,
not proof that one organizational mechanism is generally superior.

The operational chain is:

```text
A. Scenario and physical system
        ↓
B. Organizational problem and feasible decisions
        ↓
C. Models and decision mechanisms
        ↓
   Reproducible execution
        ↓
D. HLS-PEF evaluation, comparison, and diagnosis
```

This A/B/C/D workflow is consistent with, and does not replace, the scientific
distinction in the [unified framework](../architecture/HLS_UNIFIED_FRAMEWORK.md):
system model, organizational modality, and decision architecture. Here A
packages the system; B fixes the decision problem; C supplies mechanisms; D
evaluates execution records. A scenario label does not prescribe an
organization or an algorithm. Matching is one optimizer for a suitable B2
problem, not a general definition of organization.

The laboratory should make it possible to configure these components and
their information boundaries, execute repeatable runs, evaluate declared
profiles, compare compatible policies, and inspect mechanisms behind observed
differences. HLS-PEF is a configurable metric catalogue and protocol, not a
universal objective.

## 2. Original plan and its evolution

The source baseline is the [operational plan and cumulative register](HLS_LAB_EXECUTION_PLAN_2026-10-17.md),
whose original calendar is retained in §2. Its targets were: 19 Oct scientific
memory audit; 20 Oct literature selection; 21 Oct investigation priorities;
22 Oct model analysis; 23 Oct ontology and review; 26 Oct laboratory reuse;
27 Oct reproducibility/comparability; 28 Oct novelty memorandum; 29 Oct
preliminary experiment design; and 30 Oct phase report with GO/REFRAME/STOP.
The baseline did not define detailed dependencies, quantitative acceptance
thresholds, or an authorized campaign budget. Listing a date did not
authorize execution.

The original implementation workstream was distinct from this calendar: a
bounded Nembhard Direct adaptation and an adaptive contextual router were
advanced early, while full article reproduction and indirect transfer were
deferred. The historical work plan and the separately created
[reconstruction of the original plan](../project/HLS_ORIGINAL_WORK_PLAN_TO_2026-10-30.md)
preserve those decisions. Subsequent S1–S7 and HLS-PEF work was authorized
incrementally; it did not retroactively become part of the original calendar.

The current PI direction updates the immediate engineering priority: first
consolidate the reusable experiment flow across A/B/C/D, then design further
scientific studies. It does not declare old results invalid or reopen closed
experiment scopes. The original 30 October decision point remains part of the
historical plan unless the PI changes it.

## 3. Development chronology and traceability

Dates below distinguish the date attached to a plan or register entry from an
independently verified execution timestamp. Unless stated otherwise, the
register provides the documentary date but not an exact time of execution.

| Date evidenced | Objective and work recorded | Verifiable result / decision | Current status |
|---|---|---|---|
| 17 Oct | Establish the original work calendar and incrementally build/test bounded mechanisms. Nembhard Direct, ORACLE and estimate-based routing were brought forward; full paper reproduction and indirect transfer deferred. | The plan records commits, test counts, a synthetic Nembhard route, and an unexecuted protocol campaign. | Historical implementation path; not the current integration architecture. |
| 19 Oct | Review scientific memory, literature, laboratory capability and candidate reproductions. | Documentary audits narrowed/withheld reproduction and campaign choices; proposals were not promoted to completed experiments. | Preserved as historical documentary work; see original plan reconstruction and dated audit reports. |
| 20 Oct (register date) | Establish canonical S1, S2a, S2b, S3a, S3b and initial S4 cases. | S1 exact matching agrees with enumeration at 2.60 versus greedy 1.80; S2a exact periodwise solution totals 8.00 and equals global enumeration under separability; S2b shows a finite budget case where Bellman 1.00 beats myopic .90. S3a covers observable exogenous dynamics; the initial S4 comparison was later corrected for tie sensitivity. | Small reference instances tested; conclusions remain conditional on each model. Exact runtime within the dated session is not independently available. |
| 20–21 Oct (register dates) | Investigate S3b under unknown, changing rewards; revise experiment designs and diagnose feedback, memory, exploration, GLR detection, and observation distribution. | UCB1/SW-UCB results depend on scenario and complete policy configuration. GLR-CUCB produced no alarms in evaluated original runs; a later detectability diagnostic and a long-horizon test are separately recorded. The factorial/replay/subsidy studies retain their own estimands and limitations. | Specific campaigns complete; the S3b research line remains open. The UCB1/SW-UCB sequence was parked by PI decision; the later information-subsidy experiment is a separate bounded intervention. |
| 20–22 Oct (register dates) | Develop S4 from MIS-v2 and allocation references toward explicit transfer and planning. | Initial Bellman gap against a catalog-first myopic rule disappeared against BEST-MYOPIC. A restricted one-task family later showed strict Bellman value under MIS-v2. The exact transfer frontier `x^p y^q` tested T=3–5 with no positive transfer value under those settings; this is not evidence that transfer never helps. N×K simulation also contains P0/P1/P2 policies and physical transition experiments. | Several exact and simulated, scenario-specific implementations exist. The available evidence does not support general claims about P2, transfer, or planning. |
| 22 Oct (register date) | Specify S7 as stochastic/Markov demand with endogenous MIS-v2 and optional transfer; characterize preparation and local robustness. | Central T=4 exact case: Bellman no-transfer `J_A=3.1628653621`, transfer `J_B=3.1743777327`, myopic `J_M=3.0346209871`; local sensitivity and functional-service diagnostics show CES is not interchangeable with service completion. | Exact for the declared finite instances; not broad robustness or external validation. |
| 22 Oct (register date) | Audit collective-performance semantics and specify HLS-PEF. | The [collective performance audit](../architecture/HLS_COLLECTIVE_PERFORMANCE_AUDIT.md) distinguishes CES, service, deficit, output and resources. The [PEF specification](../architecture/HLS_PERFORMANCE_EVALUATION_FRAMEWORK.md) defines configurable profiles, metrics, provenance and comparability without a universal objective. | Conceptual and documentary specification established; application-specific choices remain necessary. |
| 22 Oct (register date) | Implement a minimal independent PEF evaluator and retrospective validation. | `performance_evaluation.py` provides typed profiles/records/results, metric availability states and comparisons. Retrospective S4/S7 calculations use stored aggregates/records and retain provenance; missing trajectory data are not fabricated. | Implemented and tested for the supported catalogue; it is not yet a universal event store or all-scenario adapter. |
| 22 Oct (register date) | Integrate PEF into a new S7 pilot. | `s7_pef_adapter.py` and a pilot evaluate four exact S7 policies over 16 demand branches with their probabilities; branch-weighted CES reproduces the solver values. | An operational end-to-end example exists for S7 only. |
| 23 Oct (register date) | Audit the myopic tie-break and anticipatory selection in S7. | BEST-MYOPIC reduced but did not remove the Bellman/BMA CES gap (`0.1183915782`); CURRENT-DEMAND-MYOPIC matched Bellman on the central case. Occupancy-weighted performance-difference identity was verified for the finite tree. | Mechanism diagnostics are exact and specific to one T=4 instance; no campaign expansion is warranted by this record alone. |
| 23 Oct (current review) | Recover the original plan; reconcile implementation and research history; prioritize common lab integration. | This roadmap and the appended cumulative entry document the audit and propose gated engineering milestones. | Documentation update only. No code, model, result, test or campaign changed. |

The date sequence above is a chronology of documentary evidence. The entries
for 20–23 Oct generally report work performed and registered on the same
calendar date, but exact start/end times are not recorded. The 17 Oct original
plan has stronger provenance: its source document records commit `799eb45`
and 11:59 Europe/Madrid. No date is inferred from filenames alone.

**Source map for dated milestones:** the S1/S2a assignment solver is
[`hls_lab_nk_assignment.py`](../../src/hls/hls_lab_nk_assignment.py), with
S1/S2a runners/results linked from the 20 Oct entries; S2b has its
[runner](../../experiments/run_hls_s2b_intertemporal_budget.py),
[tests](../../tests/test_hls_s2b_intertemporal_budget.py) and
[results](../../results/experiments/hls_s2b_intertemporal_budget/results.json).
S3a runners and outputs are indexed in the dated
[consolidation entry](HLS_LAB_EXECUTION_PLAN_2026-10-17.md);
S3b code, individual runners, tests and result directories are linked in its
chronological entries in the same register. S4 uses the shared N×K
[execution](../../src/hls/hls_lab_nk_execution.py),
[learning](../../src/hls/hls_lab_nk_learning.py),
[teaching](../../src/hls/hls_lab_nk_teaching.py) and
[policy](../../src/hls/hls_lab_nk_policies.py) modules plus scenario-specific
exact references and artifacts, including the
[transfer frontier runner](../../experiments/run_hls_s4_transfer_frontier.py)
and [results](../../results/experiments/hls_s4_transfer_frontier/results.json).
S7 sources include the
[uncertain-demand model](../../src/hls/synthetic/hls_s7_uncertain_demand.py),
[PEF adapter](../../src/hls/synthetic/s7_pef_adapter.py),
[preparation results](../../results/experiments/hls_s7_preparation_characterization/results.json),
[robustness results](../../results/experiments/hls_s7_mechanistic_robustness/results.json),
[tie-break report](../experiments/HLS_S7_MYOPIC_TIEBREAK_AUDIT.md) and
[anticipatory-selection report](../experiments/HLS_S7_ANTICIPATORY_SELECTION_AUDIT.md).
PEF phases are evidenced by the
[metric module](../../src/hls/performance_evaluation.py),
[retrospective runner](../../experiments/run_hls_pef_retrospective.py),
[S7 pilot runner](../../experiments/run_hls_pef_s7_pilot.py) and
[pilot output](../../results/experiments/hls_pef_s7_pilot/results.json).

## 4. Current state of scenarios (A)

“Validated” below means validated against the stated finite implementation
contract and checks, not validated for every application or parameterization.
Results and constraints are indexed in the dated scenario entries of the
[cumulative register](HLS_LAB_EXECUTION_PLAN_2026-10-17.md).

| Scenario | System/problem represented | Implemented evidence and usable components | Concrete limits |
|---|---|---|---|
| **S1** | Static known competence/reward; bipartite one-to-one assignment. | Exact SciPy assignment, greedy comparator, independent exhaustive test on a 3×3 instance; result artifact and tests. | One canonical matrix; no uncertainty, learning, temporal coupling, or scale characterization. |
| **S2a** | Known static competence with changing, observed demand and renewed per-period resources. | Reuses assignment solver; exact periodwise and full-sequence enumeration agree on the recorded demand sequence. | No intertemporal state; one finite demand sequence; the route is a runner, not a general scenario plug-in. |
| **S2b** | Same basic assignment with a persistent shared budget coupling periods. | Scenario-specific Bellman recursion and independent sequence enumeration, tests and result artifact. | Small deterministic budget state; not a general planning engine or a tested scale claim. |
| **S3a** | Exogenous changing competence, observable exactly or under declared observation noise. | D0/D1/D2 runners include matching, P0, LinUCB/fixed/oracle comparisons and information/noise controls. | Distinct runners/configurations, limited 3×3 and sampled horizon; no common execution protocol. |
| **S3b** | Unknown exogenous changing pair rewards/competences with selective Bernoulli feedback. | Individual-selection and matching variants; UCB1, SW-UCB, recent/global means, D-UCB and GLR-CUCB references; factorial, offline replay, detectability and information intervention instrumentation. | Multiple designs have different action spaces/estimands. Combinatorial composition is an adaptation; published single-play guarantees do not transfer automatically. Campaign closure is not scientific closure. |
| **S4** | Endogenous capability change by productive experience (MIS-v2), and in N×K routes explicit teaching/transfer under shared resources. | N×K environment/production/execution, MIS-v2, directed transfer, P0/P1/P2; small exact deterministic Bellman/exhaustive references; estimation/planning routes and tests. | Multiple S4 formulations and objectives exist: binary assignment reward, N×K CES, service diagnostics and policy lexicographic criteria are not interchangeable. Exact DP is small-instance and bespoke; transfer may not be used/valuable in evaluated finite profiles. |
| **S5–S6** | Proposed cross-training/bottleneck or experience-versus-transfer questions. | Literature review and candidate analysis only. | Not implemented as scenarios; not operationally available. |
| **S7** | Endogenous MIS-v2/optional transfer with stochastic Markov demand; uncertain future needs. | Exact finite Bellman, reactive/BEST-MYOPIC/CURRENT-DEMAND-MYOPIC controls, exact tree enumeration, local robustness and PEF integration. | Tiny T=4 cases; scenario-specific code; demand/reward/functional-objective assumptions are narrow. Mechanistic findings do not establish general planning superiority. |

## 5. Organizational problems (B)

| Modality | What is implemented | Where it is exercised | What is not yet general |
|---|---|---|---|
| **B1 — individual selection** | Select a single agent/task pair using fixed or learned scores; bandit and contextual selection rules. | S3b B1 experiments; LinUCB/EXP3 validation routes and contextual/Nembhard routing. | No common modality interface shared by all scenario runners; semantics differ between one request, a pair, and a route decision. |
| **B2 — combinatorial assignment** | Exact bipartite solver for additive assignment; task-unit expansion for demand; separate N×K effort/action catalogs; exact matching of UCB-style pair indices. | S1, S2a, S3a/S3b and N×K/S4 routes. | “B2” spans non-identical contracts: binary matching, multi-unit assignment, effort allocation and teaching. Constraints outside bipartite linear assignment require other solvers; no generic constraint model or optimizer registry exists. |
| **B3 — intertemporal planning** | Finite Bellman references for a shared budget, deterministic endogenous MIS-v2 and stochastic demand/transfer; independent enumeration in small cases. | S2b, S4 exact studies, S7. | Separate state/action/reward implementations; no reusable planner protocol across model state, partial observability, stochastic transition and terminal-value contracts. |

These are implemented organizational problem instances and solvers, not a
single extensible organization API. The action space, objective, information
and constraints remain defined locally in each experiment.

## 6. Models and mechanisms (C)

| Mechanism group | Scope and evidence | Reuse boundary |
|---|---|---|
| **Reactive decision rules** | P0/P1/P2 in N×K, immediate exact/reactive assignment, catalog-first myopic and the S7 BEST-MYOPIC/CURRENT-DEMAND-MYOPIC diagnostic variants. | P0/P1/P2 use their functional ranking; S7 myopic variants optimize CES and are not interchangeable policies. |
| **Assignment optimization** | `HungarianAssignmentOptimizerNK`/SciPy exact bipartite linear assignment; tested against enumeration. | Appropriate only when reward and feasible-set structure match. Other action catalogs do not automatically map to it. |
| **Bandit/estimation** | UCB1, SW-UCB, D-UCB and GLR-CUCB for pair rewards; LinUCB and EXP3 modules/tests; N×K competence posterior estimator and production assimilation. | Some algorithms are published-policy implementations; combinations such as pair indices + matching are experiment-specific adaptations, not a blanket transfer of guarantees. Estimating competence is distinct from physical skill development. |
| **Physical development** | MIS-v2 productive learning; directed teaching/transfer transition; Nembhard Direct experience/productivity model and bounded adaptive/oracle routes. | MIS-v2, teaching and Nembhard Direct have distinct state variables and laws. No common physical-mechanism interface means they can be substituted freely. |
| **Planning/adaptation** | Exact Bellman for small declared models; demand Markov tree, resource budget and endogenous capability transitions; independent exhaustive checks. | Bespoke state representations/reward semantics and small state spaces; no general solver service. |
| **Instrumentation/reference policies** | Oracles, replay diagnostics, estimand contrasts, action/tie audits, seed/trace outputs. | Evaluator-only truth and diagnostic offline decisions must not be treated as deployed policies. Tooling is attached to runners, not a central event pipeline. |

The laboratory has tested composition of selected existing mechanisms, but
has not implemented an architecture composer that lets a user select C
components from a reusable registry and bind them to arbitrary A/B contracts.

## 7. Evaluation and HLS-PEF (D)

The framework document defines configurable metrics, profiles, provenance,
comparison rules and an experimental protocol. The code in
[`performance_evaluation.py`](../../src/hls/performance_evaluation.py)
implements `EvaluationProfile`, `EvaluationRecord`, `EvaluationResult`,
explicit availability statuses, pure aggregation, exact probability-weighted
episode aggregation, historical aggregate import, and compatibility-checked
policy comparisons. It keeps original objective, CES, functional success,
deficit, output, resources and paired differences separate; missing data are
not converted to zero. Unit and profile metadata constrain valid comparisons.

The retrospective runner uses stored S4/S7 artifacts and records provenance;
it does not regenerate omitted trajectories. The S7 adapter converts the
exact tree into period records; the pilot checks all 16 branches and
probability weights without placing the evaluator in the decision loop.

**Current boundary:** the metric core is policy-independent, but record
production remains route-specific. S7 is the only demonstrated live
scenario-to-PEF end-to-end pilot. The separate
[`experiment_contract.py`](../../src/hls/experiment_contract.py) provides a
versioned, stable-JSON run envelope and adapters for selected N×K,
Nembhard-direct and contextual-route results. Its module contract expressly
says it describes/adapts executions; it does not execute a simulator,
normalize mechanism-specific quantities or establish scientific
comparability. S3b and exact S1–S4/S7 synthetic paths are not all connected to
this common envelope. Thus the two pieces—common run envelope and PEF
evaluation—exist, but a shared pipeline from a user-declared experiment to
execution and evaluation does not yet.

## 8. Maturity matrix

The labels—**CONCEPTUAL, ESPECIFICADO, IMPLEMENTADO, PROBADO, INTEGRADO,
VALIDADO**—are evidence stages, not automatic consequences of a file existing.
“Validated” is scoped to stated fixtures/contracts. A component can have a
validated narrow instance and still be absent as a reusable laboratory
capability.

| Component | Maturity reached and evidence | Dependency / pending work | Priority |
|---|---|---|---|
| Original HLS model vocabulary | **CONCEPTUAL, ESPECIFICADO** — unified framework and ontology distinguish system, organization, mechanisms, state and observation. | Preserve ontology; map terms to executable contracts without claiming a universal state interface. | Maintain |
| S1 and S2a scenario routes | **ESPECIFICADO, IMPLEMENTADO, PROBADO, VALIDADO** for canonical finite cases — solver/enumeration tests and runners. | Connect output records to common envelope/PEF; no scale/generalization. | Hito 3 |
| S2b route | **ESPECIFICADO, IMPLEMENTADO, PROBADO, VALIDADO** in finite budget instances — Bellman/enumeration tests. | Common planner/record integration if required; preserve narrow scope. | Hito 3 |
| S3a routes | **ESPECIFICADO, IMPLEMENTADO, PROBADO, VALIDADO** in D0–D2/noise experiments. | Common records and cross-route comparable profiles; no new dynamicity campaign by default. | Hito 3 |
| S3b routes | **ESPECIFICADO, IMPLEMENTADO, PROBADO, VALIDADO** across several distinct protocols. | Route adapters/common provenance; maintain distinctions between closed experiments and open science line. | As needed |
| S4 N×K physical/execution layer | **ESPECIFICADO, IMPLEMENTADO, PROBADO, VALIDADO** in targeted environment/execution tests and route runs. | Formal common interface, consistent objective declarations and PEF route integration. | Hito 3 |
| S4 exact references | **ESPECIFICADO, IMPLEMENTADO, PROBADO, VALIDADO** against independent enumeration for small cases. | Do not infer scalable planner capability; share contracts only where semantics match. | Maintenance |
| S7 | **ESPECIFICADO, IMPLEMENTADO, PROBADO, VALIDADO** for exact finite tree and controls; **INTEGRADO** with PEF in one pilot. | Second non-S7 route required to validate reuse; no claim of broad scenario integration. | Hito 3 |
| B1–B3 problem instances | **CONCEPTUAL, ESPECIFICADO, IMPLEMENTADO, PROBADO** in scenario-specific paths. | Stable decision/action/constraint contracts shared by runners; more general optimization is not implied. | Hito 1–2 |
| Mechanism library | **CONCEPTUAL, ESPECIFICADO, IMPLEMENTADO, PROBADO**; selected methods have mathematical/functional tests and scenario results. | Declare capabilities, information needs, state transition and units consistently; composition interface absent. | Hito 2 |
| HLS-PEF metric core | **CONCEPTUAL, ESPECIFICADO, IMPLEMENTADO, PROBADO, VALIDADO** on unit, compatibility and retrospective cases. | Keep missingness/provenance; broaden only against a concrete route contract. | Hito 2 |
| HLS-PEF S7 integration | **IMPLEMENTADO, PROBADO, INTEGRADO, VALIDADO** for the S7 pilot tree and four policies. | Generalize via a second existing scenario; preserve route adapter boundaries. | Hito 3 |
| Common run envelope | **ESPECIFICADO, IMPLEMENTADO, PROBADO** for selected result types; stable serialization tested. | Not a runner/orchestrator; no universal config/action/output schema and incomplete route coverage. | Hito 1 |
| End-to-end laboratory flow | **CONCEPTUAL, PARCIALMENTE ESPECIFICADO**; pieces exist in several independently runnable routes. | No common route that takes scenario + B + C + PEF profile through execution/comparison/diagnosis. | Immediate |

## 9. Target integration architecture

The next engineering step should join existing components through explicit
contracts, not replace their physics or duplicate scenario functionality:

1. **Scenario/configuration declaration:** stable ID/version; dimensions,
   initial conditions, dynamics, demand law, resources, observation law,
   random streams and evaluator-only state.
2. **Organizational-problem declaration:** modality, action/feasible-set
   contract, objective and hard constraints; matching is one implementation
   chosen only if the contract fits.
3. **Mechanism declaration:** mechanism/policy IDs and versions, state,
   permitted information, update/decision hooks and any physical transition
   that changes the system. Keep estimators separate from physical learning.
4. **Execution protocol:** run identity, seeds and stream separation,
   policy-visible inputs, evaluator-only truth, events/actions/outcomes,
   resources, failure status and deterministic serialization.
5. **Evaluation profile and results:** use HLS-PEF as an offline evaluator;
   keep objective, diagnostics, unavailable metrics, units and provenance
   explicit, then compare only compatible profiles or label information
   differences.
6. **Analysis bundle:** exact checks or paired uncertainty, per-period/branch
   summaries when retained, mechanism diagnostics and scoped conclusions.

Existing `ExperimentRun` is a starting envelope for run identity, seeds,
units, events, metrics, provenance and mechanism results. It must not be
mistaken for the complete contract: currently it has selected adapters and
does not execute A/B/C or dispatch a policy. `EvaluationProfile` is a usable
evaluation input but is not yet bound automatically to a scenario's declared
objective, constraints, demand distribution and output records.

## 10. Updated work plan and verifiable milestones

Sequence work by dependency. Every milestone is an engineering gate; experiment
execution remains separately authorized.

### Hito 1 — Consolidate the common experiment contract (complete for first route)

- **Goal:** specify and exercise the minimum shared inputs/outputs for an
  experiment route, reusing `ExperimentRun`, `RunAdapterContext`,
  `EvaluationProfile` and existing result dataclasses.
- **Why:** selected output adapters and PEF already exist, but the same
  boundaries/provenance are not yet expressed for all route families.
- **Dependencies:** inspect actual N×K, S3b and S7 schemas; no new physical
  model or algorithm.
- **Deliverable:** audit/specification plus the S2a vertical slice in
  [`HLS_EXPERIMENT_CONTRACT_INTEGRATION.md`](HLS_EXPERIMENT_CONTRACT_INTEGRATION.md).
  The existing runner produces exact and greedy results, a localized adapter
  builds common runs/records, and HLS-PEF evaluates them. A strict JSON reader
  was added to the existing run envelope to satisfy round-trip validation.
- **Exit checks:** S2a exact 8.0, greedy 7.2, global enumeration 8.0 / 84,388
  sequences; common run serialization round-trip; PEF reward reproduction;
  unsupported metrics explicit; policy-neutral adapter; S7 artifact structural
  compatibility. These checks pass for the bounded routes. The original S7
  runner does not yet emit `ExperimentRun` natively.

### Hito 2 — Bind scenario, organization, mechanisms and PEF profiles

- **Goal:** enable a declared configuration to connect one scenario route,
  one organizational problem, allowed mechanism(s), and an evaluation
  profile, without embedding PEF in decisions.
- **Why:** components now run through bespoke scripts and adapters.
- **Dependencies:** Hito 1 field semantics and versioning.
- **Deliverable:** one thin orchestration path that invokes existing runner
  functions and emits common run/evaluation artifacts; no general plugin
  system unless one concrete route requires it.
- **Exit checks:** a fixed profile maps to actual run settings; decisions are
  unchanged with PEF attached/detached; invalid information/constraint
  contracts fail before execution; artifact points back to source run.

### Hito 3 — Validate reuse across scenarios, starting outside S7 (partially evidenced)

- **Goal:** demonstrate that the contract is reusable for at least two
  semantically distinct existing scenario routes, without a new scenario.
- **Candidate sequence:** S2a (known, separable assignment) as the low-coupling
  route, then an existing S4 N×K execution route or S3b selective-feedback
  route. Select based on record gaps discovered in Hito 1, not expected policy
  rankings.
- **Deliverable:** S2a has a fresh runner→contract→PEF path; S7 uses PEF
  natively and its stored result is wrapped in the same run envelope for a
  structural check. A second live runner-native integration remains untested.
- **Exit checks:** reproduce an existing deterministic result or stored
  aggregate without changing its source artifact; declare not-recorded fields
  rather than reconstruct them; keep differing objectives/units incomparable.

### Hito 4 — Consolidate execution, results and reproducibility

- **Goal:** make seed/configuration/version provenance, output structure,
  failure/resume behavior and statistical/exact comparison rules consistent
  for supported routes.
- **Dependencies:** stable contract and at least two integrations.
- **Deliverable:** route-independent manifest/result validator and minimal
  reproducibility check; use existing stream separation and paired-analysis
  utilities where valid.
- **Exit checks:** repeated deterministic route yields stable artifact;
  stochastic route records seeds/streams and a reproducibility tolerance;
  paired units are explicit; no period is treated as independent seed.

### Hito 5 — Prepare for relevant scientific experiments

- **Goal:** use a validated lab path to specify a problem-organizationally
  relevant experiment and analyze mechanisms rather than select algorithms
  in arbitrary worlds.
- **Dependencies:** at least one cross-scenario validated path, declared
  objective/profile and reproducible comparisons.
- **Deliverable:** preregistered/scoped design stating scenario, organization,
  mechanisms, information, comparators, metrics, diagnostic traces and stop
  criteria; separate PI authorization for execution.
- **Exit checks:** the design tests a specific organizational need; policies
  receive allowed information; comparators are competitive; outcomes and
  mechanisms can be distinguished; negative outcomes remain interpretable.

## 11. Next increment recommendation

**Hito 1 is complete for the first deterministic route.** Keep
`experiment_contract.py` and PEF as the common structures; do not build a
second execution framework. The next technically informative integration
would be an existing S4 N×K execution result with requirements, production,
resources and MIS-v2/teaching fields. It would test semantic adaptation beyond
assignment reward and distinguish physical outputs from the optimized CES.
The route should be selected based on what an existing result actually
records, with no scenario or policy change. This is an engineering integration
recommendation only; it has not been authorized or started. The S7 envelope
adapter should be wired into a future S7 run only if a later requirement
demonstrates that native emission is needed.

## 12. PI decisions pending

No decision below is assumed to have been adopted:

1. Whether the 30 Oct original phase-close / GO-REFRAME-STOP point remains the
   project gate after the current integration-first priority.
2. Which non-S7 route should be the first PEF/end-to-end reuse pilot if S2a's
   records do not preserve needed provenance (S2a, S4 N×K or S3b).
3. Whether run artifacts should remain per-route JSON plus a common manifest,
   or move to another storage format; no storage migration is recommended here.
4. Which common information labels, configuration versioning and software
   revision sources are mandatory when legacy runners cannot infer them.
5. When the scientific program should resume a particular open line such as
   S3b; none is selected by this roadmap.

## 13. Sources and evidence boundaries

- [Cumulative plan, original calendar and dated evidence](HLS_LAB_EXECUTION_PLAN_2026-10-17.md)
- [Original-plan reconstruction and cut-off audit](../project/HLS_ORIGINAL_WORK_PLAN_TO_2026-10-30.md)
- [Unified scientific framework](../architecture/HLS_UNIFIED_FRAMEWORK.md)
- [Ontology v0.1](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md)
- [Collective-performance audit](../architecture/HLS_COLLECTIVE_PERFORMANCE_AUDIT.md)
- [HLS-PEF specification and phase history](../architecture/HLS_PERFORMANCE_EVALUATION_FRAMEWORK.md)
- [S7 BEST-MYOPIC audit](../experiments/HLS_S7_MYOPIC_TIEBREAK_AUDIT.md)
- [S7 anticipatory-selection audit](../experiments/HLS_S7_ANTICIPATORY_SELECTION_AUDIT.md)
- Source code and tests linked from dated scenario entries in the cumulative plan; result artifacts remain in their scenario-specific directories under `results/experiments/`.

**Evidence boundary:** scenario entries report exact results, stochastic
campaigns, tests, or diagnostics within their declared scopes. They do not
establish external validity, universal algorithm rankings, or a common runner
simply because individual runners share some code. The current roadmap is an
engineering plan, not a new scientific result.

## 14. Hito 1 — Incrementos 1 y 2 (23 Oct 2026)

Incremento 1 (auditoría/especificación) e Incremento 2 (primera integración
vertical S2a) están completos en el alcance acotado documentado en
[HLS_EXPERIMENT_CONTRACT_INTEGRATION.md](HLS_EXPERIMENT_CONTRACT_INTEGRATION.md).
La entrada cronológica con resultados y pruebas se añadió al
[registro acumulativo](HLS_LAB_EXECUTION_PLAN_2026-10-17.md); se conservaron
las entradas previas.

**Flujo S2a comprobado:** el runner original ejecuta la instancia existente;
un adaptador downstream crea un `ExperimentRun` por política y registros PEF;
`PerformanceEvaluator` calcula recompensa original, conteo de asignaciones y
disponibilidad de métricas no definidas. No se añadió un ejecutor universal.
Exacto=8.0, greedy=7.2; la enumeración exhaustiva global=8.0 sobre 84,388
secuencias se registra solo como referencia de optimalidad. La diferencia
exacto−greedy=0.8 describe esta instancia determinista.

**Contrato común y S7:** S2a y el artefacto PEF de S7 se validaron con las
mismas clases centrales. La auditoría mostró que el runner S7 histórico
produce PEF, pero no `ExperimentRun`; un adaptador downstream ahora envuelve
sus registros guardados, sin reejecutar ni sobrescribir S7. Es compatibilidad
del artefacto, no emisión nativa del runner S7.

**Disponibilidad:** el catálogo PEF actual no mide cobertura por tipo; los
conteos quedan como diagnósticos estructurados. CES, cumplimiento funcional,
déficit y producción física son `NOT_APPLICABLE` para S2a. La ruta no valida
aprendizaje, feedback parcial ni inferencia estocástica. PEF compare hace una
diferencia compatible, no un análisis estadístico pareado.

**Estado de hitos:** Hito 1 se cierra como primer corte vertical. Hito 2
(orquestación fina de configuración/organización/mecanismo/perfil en otra
ruta) sigue pendiente. Se recomienda como siguiente integración técnica una
ruta existente S4 N×K que ya registra requisitos, producción, recursos y
aprendizaje/enseñanza, después de auditar su resultado fuente. Es una
recomendación no iniciada y requiere decisión/alcance del PI.

## 15. Hito 2.1 — Auditoría semántica de S4 N×K (23 Oct 2026)

La auditoría ejecutable se completó para la instancia determinista exacta
S4 `T=3` (dos agentes, dos competencias, demanda `x,y,y`), usando resultados
históricos y solver/leyes existentes. La recompensa Bellman A y B se
reprodujo como `1.9175000000000004`; HLS-PEF retrospectivo conserva CES,
producción, cumplimiento, déficit y recursos con unidades y denominadores
declarados. Se verificó que producción positiva puede no cumplir requisitos
y que la coincidencia numérica CES/producción es propia de esta instancia.

**Conclusión de integración:** `ExperimentRun` v1 y el catálogo HLS-PEF bastan
para representar las magnitudes colectivas observadas mediante un adaptador
S4 localizado. No se identificó una limitación del contrato ni necesidad de
añadir métricas. Calidad individual no está definida; producción individual
es derivable pero no equivale a calidad. La instancia exacta conoce estado
real y demanda completa, por lo que no acredita compatibilidad con las rutas
S4 parcialmente observadas P0/P1/P2.

**Estado:** Hito 2.1 completado; auditoría y prueba de caracterización en
[`HLS_S4_SEMANTIC_INTEGRATION_AUDIT.md`](HLS_S4_SEMANTIC_INTEGRATION_AUDIT.md)
y `tests/synthetic/test_hls_s4_pef_semantic_characterization.py`. Hito 2.2
(adaptador e integración vertical S4) está pendiente de decisión/autorización
del PI; no se inició. Recomendación técnica: GO acotado con esta referencia,
declarando estado completo y demanda conocida, sin extrapolar a políticas con
información parcial. No se alteraron runner, políticas, física, objetivo,
contrato, PEF ni artefactos históricos.

## 16. Hito 2.2 — Integración operativa S4 N×K con HLS-PEF (23 Oct 2026)

**Estado: completado en el alcance de la referencia exacta auditada.** El
adaptador S4 produce `ExperimentRun` v1 y `EvaluationRecord` desde los
resultados del solver existente; el runner aplica dos perfiles HLS-PEF sobre
los mismos records. El artefacto está en
[`hls_s4_pef_integration/results.json`](../../results/experiments/hls_s4_pef_integration/results.json).
El contrato v1 y el catálogo de métricas no cambiaron.

Regresión: A/B reward `1.9175000000000004`; cumplimiento `1/3`; déficit
`.5325`; esfuerzo productivo `6`, esfuerzo docente `0`, recurso docente `0`
y total `6`. Ambas políticas evaluadas con perfiles básico y ampliado
producen las mismas decisiones, estados y métricas colectivas. Ninguna
selecciona transferencia.

**Validación transversal:** S2a, S4 y S7 utilizan las mismas clases
`ExperimentRun`, `EvaluationProfile`, `EvaluationRecord` y
`PerformanceEvaluator`; cada escenario conserva perfiles, métricas, unidades
y disponibilidad propios. Esto valida reutilización estructural y semántica
local. No demuestra equivalencia de magnitudes, ni valida S4 P0/P1/P2 con
observación parcial, ni transferencia efectiva.

**Siguiente estado:** Hito 2.2 queda cerrado conforme a sus criterios para la
ruta determinista S4. La expansión a rutas S4 parcialmente observadas o a
otros escenarios queda fuera del alcance y requiere decisión del PI. No se
inició otra campaña.

## 17. S3b — Recuperación y reproducción instrumentada (23 Oct 2026)

**Decisión vigente del PI:** prioridad S3b, GO para una reproducción acotada.
Esta ejecución retoma una pregunta dentro de S3b y no borra la decisión
histórica de aparcar la secuencia anterior UCB1/SW-UCB.

Se reutilizó S3b B2 3×3: matching completo, recompensas Bernoulli desconocidas,
cambios exógenos recurrentes y feedback semi-bandit selectivo. Se mantuvieron
los niveles registrados de frecuencia (tau=2500/500), disponibilidad (.75/.25),
UCB1 y SW-UCB (xi=2, W=1214), horizonte 10000, seis matchings y oráculo
dinámico. Se usaron 30 semillas emparejadas nuevas (9000–9029), sin modificar
parámetros ni matrices.

En las 240 réplicas UCB1 obtuvo menor regret en las cuatro celdas; SW-UCB tuvo
menor MSE medio de parejas. Reducir oportunidades elevó el regret de ambas.
La interacción factorial frecuencia × disponibilidad fue +29.17
(IC95% [-3.92,62.25]), no concluyente. La diferencia entre algoritmos no
aísla memoria del bonus de confianza ni de los historiales endógenos.

La ruta produce ExperimentRun v1 y aplica EvaluationProfile/HLS-PEF al reward
esperado. Las trazas detalladas comprimidas conservan las variables
diagnósticas; PEF no calcula regret mediante una métrica genérica nueva. El
modelo S3b evaluado no define costes, producción ni requisitos funcionales.

**Artefactos:** [runner](../../experiments/run_hls_s3b_observability_recovery.py),
[adaptador](../../src/hls/synthetic/s3b_pef_adapter.py),
[resultados](../../results/experiments/hls_s3b_observability_recovery/results.json),
[trazas](../../results/experiments/hls_s3b_observability_recovery/period_traces.jsonl.gz),
[pruebas](../../tests/test_hls_s3b_observability_recovery.py).

**Estado:** esta ejecución está cerrada; S3b sigue abierta. El PI decidirá
si continúa la investigación. No se inició otra campaña ni se tocaron otros
escenarios o resultados históricos.

## 18. S3b-E1 — Diagnóstico final de memoria y feedback (23 Oct 2026)

El PI autorizó el cierre de S3b-E1 con dos controles FULL/WINDOW. Se
reutilizaron las condiciones infrecuente/alta, frecuente/alta y frecuente/
baja, 30 semillas 9000–9029 y horizonte 10000. FULL y WINDOW comparten
estimador de media, inicialización neutral, matching exacto y desempate;
solo difiere el historial retenido (global frente a W=1214). Ninguno usa
bonus de confianza: no son reproducciones de UCB1/SW-UCB.

Con calendario de observaciones común, WINDOW redujo regret en
74.59 [IC95% -89.60,-59.58] para cambios infrecuentes y feedback alto;
en las otras dos celdas el regret no mostró una diferencia concluyente.
En bucle cerrado el regret WINDOW−FULL favoreció en media a WINDOW, pero
los tres IC incluyeron cero. WINDOW tuvo mayor tasa de matching óptimo en
las tres condiciones, pese a mayor MSE global. En frecuente/baja, el MSE
sobre aristas óptimas fue .0458 para WINDOW y .0891 para FULL, aunque el
MSE global fue .0800/.0671. La distribución de feedback por pareja difería
con volumen total parecido.

S3b-E1 queda cerrado. El resultado no separa por completo efectos de la
memoria y trayectorias de feedback, no reproduce los algoritmos UCB
publicados y no estima interacción factorial con el diseño reducido. No
inicia otra campaña ni decide la prioridad científica posterior.

**Evidencia y artefacto:** entrada detallada y límites en el
[registro acumulativo](HLS_LAB_EXECUTION_PLAN_2026-10-17.md); resultados en
[results.json](../../results/experiments/hls_s3b_memory_replay_diagnostic/results.json).
**Estado:** E1 cerrado; S3b general no se declara cerrada por esta ejecución.
