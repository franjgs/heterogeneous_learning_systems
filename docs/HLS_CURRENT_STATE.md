# HLS Current State

> **Current scientific snapshot — 23 October 2026.** This section is the
> authoritative entry point for the PI. The dated records and artifacts linked
> here remain the source of detail; older material below is retained for
> historical traceability and must not override this snapshot where dates
> differ.

**USE/DEVELOP status — 23 October 2026:** the focused grounding phase ended
with an initial **REFRAME**; the subsequent originality assessment concludes
**NO-GO as an immediate standalone publication candidate**. Unrestricted,
fully coordinated USE and DEVELOP modules implement the same behavior class
as joint policies under explicit common-information, synchronization,
feasibility, and computation assumptions. Existing HLS results remain
bounded evidence, not a general claim that joint management is necessary. The
[research note](research/HLS_USE_DEVELOP_SEPARABILITY_NOTE.md) records the
formal equivalence, literature comparison, and decision. S3b-E1 is the sole
priority alternative for further originality positioning, not an open or
authorized campaign. No historical result was changed.

**Strategic proposal — 24 October 2026 (pending PI ratification):** the PI has
proposed prioritizing (1) dynamic organization of fast and deliberative
capabilities, (2) selective cooperation among heterogeneous capabilities, and
(3) organizational learning and emergent specialization, in that order. The
CE considers this direction suitable for a feasibility assessment. The
documentary mission [HLS-CE-01](research/HLS_CE_01_DYNAMIC_DELIBERATION_2026-10-24.md)
is in planning/feasibility only: no new campaign, algorithm, or manuscript is
authorized. This proposal does not redefine HLS or reopen closed studies.

## Executive status

HLS is a general scientific programme for studying, designing, and evaluating
the organization, use, combination, and evolution of heterogeneous
capabilities. The [HLS philosophy](HLS_PHILOSOPHY.md) defines its identity
through a conceptual and experimental architecture of four levels: scenarios,
organizational schemes, models, and performance measures. This identity does
not require a particular mechanism, a dynamic system, or a USE/DEVELOP
decomposition. The [unified framework](architecture/HLS_UNIFIED_FRAMEWORK.md)
provides a compatible three-part mathematical formulation of specified
decision problems (system model, problem and organizational modality,
decision architecture); it is a formal view within the broader architecture,
not a competing conceptual architecture. The [ontology v0.1](architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md)
supports semantic mappings. Operationally, experiments also declare
evaluation independently through
[HLS-PEF](architecture/HLS_PERFORMANCE_EVALUATION_FRAMEWORK.md). Scenario
labels identify problem regimes; they are not maturity levels. The notation
`S1`–`S7` names scenario families, whereas `TR-PR`, `TR-PM`, `TR-G`, `TR-J`,
`TR-R`, `TR-D`, `TR-HA`, and `TR-HB` identify ordered demand/problem histories
in the Campaign 1–3 line. There is no canonical HLS scenario S8.

The laboratory now contains tested models for assignment, selective-feedback
learning, endogenous skill development, transfer, uncertain demand and
intertemporal planning, plus `ExperimentRun` v1 and an independent metric
evaluator. Vertical integrations show that S2a, one deterministic S4 N×K
reference and S7 records can use common contracts while retaining different
physical meanings. This is not yet a universal runner: integrations are
scenario-specific adapters, and not all legacy runners emit common records
natively. HLS-PEF evaluates outcomes; it does not select actions or impose a
universal objective.

**Scientific position:** there are several bounded, reproducible findings,
including negative and null results. They do not establish a universal
organizational policy, broad superiority of a named optimizer, or external
validity across applications. “Validated” below means checked against the
declared mathematical/software contract and evidence for the stated finite
scope; it does not mean independently replicated or validated in a real
organization.

## Philosophy, ontology, and evidence rules

- **A — System:** agents, tasks, competencies, demand, state, dynamics,
  resources, observation and transitions.
- **B — Organizational problem:** the decisions and feasible action set.
  B1 individual selection, B2 combinatorial assignment and B3 intertemporal
  planning are useful, non-exhaustive modalities.
- **C — Decision architecture:** estimation, learning, optimization,
  adaptation and planning components under a declared information regime.
- **Evaluation:** an explicit profile and metrics. The objective optimized
  by a policy remains distinct from evaluation metrics, service requirements,
  resource constraints and diagnostics.

Evidence statuses used in this snapshot are deliberately separate:
**defined** (problem specified), **implemented** (code exists), **executed**
(runs/results exist), **evaluated** (metrics and comparisons are reported),
and **validated** (specific claims checked against tests, exact enumeration,
or a declared reproducible design). A published-method name alone does not
establish faithful reproduction of its literature formulation.

## Scenario inventory: S1–S7

| Family | Problem and implemented route | Evidence and bounded conclusion | Current limit |
|---|---|---|---|
| **S1** | Known static assignment; exact bipartite assignment and greedy reference. | Small deterministic reference: exact value 2.60 versus greedy 1.80; exact solver checked against enumeration. | One bounded assignment geometry; no general superiority claim. |
| **S2a** | Known, period-separable demand and capacity-constrained assignment. | Exact 8.0, greedy 7.2, global enumeration 8.0 over 84,388 sequences. Hito 1/2 integration builds `ExperimentRun` and evaluates with HLS-PEF without changing the runner. | The result depends on period separability; it does not show intertemporal planning value. |
| **S2b** | Shared nonrenewable budget couples decisions across periods (B3). | In a finite exact reference, Bellman 1.00 versus myopic 0.90; sufficient-budget control 1.90. | Small constructed instance; not evidence that planning generally wins. |
| **S3a** | Exogenous changing competence/reward with observation regimes and assignment. | Implemented estimator/observation controls and bounded comparisons; exact assignment can attain the declared oracle under the fully observed mapping. | No evidence that online learning is needed or useful in that mapping; scope is the encoded regimes. |
| **S3b** | Unknown, exogenously changing pair rewards/competencies; selective Bernoulli feedback; individual or matching decisions. | UCB1, SW-UCB and diagnostic controls have separate experiments. In the recovered 240-run factorial, UCB1 had lower regret in all four cells while SW-UCB had lower global MSE. Final S3b-E1 isolates memory more carefully: shared-observation controls found a WINDOW benefit only in infrequent-change/high-feedback (regret 184.88 vs 259.47; paired Δ WINDOW−FULL −74.59, 95% CI [−89.60,−59.58]); other shared cells were null/nonconclusive. In closed loop, WINDOW mean regret was lower in three cells but every paired CI included zero. | The UCB algorithms differ beyond memory. FULL/WINDOW are diagnostics, not UCB reproductions. Endogenous observations prevent a pure feedback-mediated causal estimate; S3b-E1 is closed, broader S3b is not declared closed. |
| **S4** | Endogenous MIS-v2 learning by production, optional directed teaching/transfer, shared resources; exact and N×K routes. | Exact small references, N×K transitions/policies, and deterministic HLS-PEF integration. In the audited T=3 `x,y,y` instance, both Bellman variants reward 1.9175000000000004, functional compliance 1/3, deficit .5325, productive effort 6, teaching effort 0. Exact transfer frontier tested finite `x^p y^q` instances without positive transfer gain under those parameters. | No claim transfer never helps. The integration’s optimum does not teach and does not validate P0/P1/P2 or effective transfer. S4 studies use distinct objectives and information regimes. |
| **S5 / S6** | Specialization/bottlenecks/cross-training and experience-versus-transfer were candidate research problems. | Document/literature analyses only. | Not implemented as scenario families; no experimental conclusions. |
| **S7** | Uncertain Markov demand, MIS-v2 competence dynamics, optional transfer, finite B3 planning. | Exact finite tree and independent enumeration. Central T=4 CES: Bellman without transfer 3.1628653621; with transfer 3.1743777327; myopic 3.0346209871. A BEST-MYOPIC tie audit gives 3.0444737839, reducing Bellman’s gap to .1183915782. Mechanistic audit found CURRENT-DEMAND-MYOPIC matches Bellman’s central CES (3.1628653621); key Bellman/BEST-MYOPIC divergences were CES ties with different learning allocation and continuation value. | Exact for small declared instances, not a general planner result. CES can rise while functional service worsens (transfer case: expected services 3.001→3.000 and deficit .04995→.175); CES is not service compliance. Tie-breaking is a material comparator issue. |

The full chronological technical record, including code, tests, configurations
and limits, is the [cumulative execution plan](engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md).

## Other research lines and demand histories

The Campaign 0–4 / G0 / Q1 / META-VOC work is a related historical research
track, not another S-scenario numbering system. The Campaign 1 histories
`TR-*` are ordered demand/problem sequences, not scenarios S1–S7 and not a
hierarchy. For example, TR-PR reuses Campaign 0 H2; TR-G/TR-J and TR-HA/TR-HB
reuse or reorder previously used content; TR-PM and TR-D are the narrower
pre-performance Campaign 1 cases. See [Campaign 1 results](experiments/CAMPAIGN_1_RESULTS.md),
[Campaign 2 results](experiments/CAMPAIGN_2_RESULTS.md), and the
[Campaign 3 META-VOC confirmatory report](experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md).

The Campaign 2 record supports a bounded positive result alongside important
nulls: specific preregistered hypotheses held in the sampled problem
population, while Q01 realized utility was not established (mean .0015,
95% CI [−.0194,.0193]); reported coupling was rare (71/15,360, about .46%).
It does not establish universal superiority of Q11 or that development is
useless. Campaign 3 META-VOC reported a confirmatory equal-domain
META-VOC-50 minus RANDOM-50 cumulative `mu_true` difference of +.1167 per
history (95% CI [.0310,.2013]) and decision-computation difference −.1924 s
(95% CI [−.3539,−.0228]); invocation counts were not exactly equal, and the
predictor-validity audit found weak discrimination (AUC .624; deep-versus-fast
contrast +.0104, CI [−.020,.0431]). These are bounded synthetic findings, not
evidence of a reliable real-world opportunity detector. Campaign 4 remained
HOLD/NO-GO for full execution in its recorded protocol. Historical details
and frozen records remain in their linked reports; this snapshot does not
reinterpret them as S1–S7 results.

## Investigations and scientific findings

### S3b-E1 — memory and organization-dependent observations

The controlled shared-observation result demonstrates that retaining a
shorter history can improve regret under one tested combination of rare
changes and high feedback, while MSE improvements in other cells need not
change assignment quality. In closed loop, actions change which pairs are
observed; regret uncertainty remains too large to claim a decisive FULL versus
WINDOW winner. Global MSE can mis-rank organizational decisions because it
weights all pairs equally, whereas matching utility depends on which edges
change the feasible optimum and its margin. This is evidence about these
3×3 matrices, policies, horizon and observation schedules only. The detailed
[S3b-E1 result and diagnostic JSON](../results/experiments/hls_s3b_memory_replay_diagnostic/results.json)
and append-only execution log preserve the controls and provenance. A
separate 240-run UCB1/SW-UCB factorial is recorded in the
[observability-recovery results](../results/experiments/hls_s3b_observability_recovery/results.json);
it must not be conflated with the memory-isolating controls.

### Complementarity and budgeted model allocation

The small classifier-combination pilot used exact enumeration, Kittler sum
fusion and a declared common-U mixture for error dependence. The seven
coalitions and error-pattern probabilities were computed exactly. Fusion
quality depended on task, dependence and feasibility: under rho=0, the full
coalition had accuracy 413/500=.826 for both task types; under rho=1 it had
.700; under rho=.25 it had 1589/2000=.7945. These numbers validate this
synthetic construction and are consistent with known ensemble behavior; they
do not establish scientific novelty or practical organizational benefit.
See the [machine-readable exact result](../results/experiments/hls_expert_complementarity_math_validation/results.json)
and [validator](../experiments/validate_hls_expert_complementarity_math.py).

The budgeted MMLU routing study assigned one model per query under a shared
predicted-latency budget. Its original MIRT adaptation had Brier .2698 versus
.2314 for a constant baseline; a logistic correction improved predictive
Brier to .2174 and log-loss to .6240, but did not uniformly improve
organizational outcomes. ILP and greedy were essentially tied in most cells;
the only clear local ILP-over-greedy result was +2.16 percentage points for
contextual logistic prediction, homogeneous batches and budget .35 (95% CIs
by packing [1.63,2.72] pp and by query [.72,3.78] pp). Other tested cells did
not establish a general ILP advantage. This shows that optimizer comparisons
depend on predictor quality and batch composition; the optimizer and
predictor effects must remain separate. The [consolidated report](experiments/HLS_BUDGETED_LLM_ROUTING_CONSOLIDATED_REPORT.md)
links both pilots and structured results.

### MMLU dynamic capacity and contextual selection

The initial free-generation pilot was retained separately: the nominally
smaller FAST model was slower (23.1%, .519 s) than DEEP (45.0%, .406 s),
plausibly because it generated more tokens under a non-comparable timing
protocol. The corrected direct-choice protocol measured SmolLM2-360M at
24.4%/96.2 ms, SmolLM2-1.7B at 45.0%/141.6 ms, and Qwen2.5-0.5B at
46.3%/88.9 ms. Static selection by subject reached 51.3%/124.2 ms. The
tested confidence cascade reached 34.4%/152.3 ms and did not improve the
observed quality-latency frontier; first-model confidence had AUC .508 for
error detection. This is a negative result for this signal, models and
protocol, not for all cascades.

The later contextual DCS-LA adaptation selected `k=21`, unigram TF-IDF,
subject weight zero using validation, then evaluated 160 held-out queries.
It reached 46.25%/139.27 ms versus 45.00%/141.61 ms for the best global fixed
model: +1.25 pp, 95% paired CI [−1.25,+3.75], hence not conclusive. It chose
the same 1.7B model in 149/160 queries; online selection cost averaged
.456 ms/query. The subject-fixed selector scored 51.25%/124.20 ms, but its
accuracy advantage over DCS-LA is not established solely by point estimates;
there were only 20 training examples with explicit subject metadata. The
68.75% retrospective oracle is not deployable and excludes the cost of
oracle information. These findings do not show that TF-IDF is generally
useless or that subject routing always wins. See the [corrected dynamic
capacity report](experiments/HLS_DYNAMIC_CAPACITY_ORGANIZATION_CORRECTED.md)
and [DCS-LA report](experiments/HLS_CONTEXTUAL_CAPACITY_SELECTION.md).

## Cross-cutting knowledge, with scope

| Observation supported in studied cases | What it does not establish |
|---|---|
| More diverse errors do not guarantee that the evaluated fusion rule exploits complementarity; plurality was below a fixed model in the corrected MMLU pilot. | That combinations are generally ineffective. |
| Predictive MSE/Brier and organizational utility are distinct; errors on decision-critical alternatives can matter more than global average error. | A universal decision-weighted estimator or causal decomposition. |
| Better calibration does not guarantee better budgeted assignments; ILP gains were conditional on predictor and batch regime. | General superiority of ILP, greedy, or contextual routing. |
| Coordination/latency costs can move an organizational mechanism outside the measured frontier. | Transfer of local MPS timing to serving, monetary, energy, or concurrent costs. |
| Myopic tie-breaking can explain part of apparent planning value; a current-task reactive diagnostic matched Bellman CES in the central S7 instance. | That planning has no value in other dynamics, objectives or horizons. |
| CES, production, service success, deficit, effort and resource consumption are distinct quantities. | That a single metric is appropriate for every HLS application. |
| In feedback systems, organizational actions shape later observations. | A pure causal feedback effect from the closed-loop FULL/WINDOW contrast. |

Dimensions still weakly characterized include real-world outcome and cost
measurement; robustness across independent task populations and systems;
scalable intertemporal planning; realistic teacher/learner effectiveness;
coordination under concurrency; causal identification with endogenous
observations; generalization beyond the tested agents/tasks; and consistent
provenance across all legacy runners. S5/S6 remain candidate problem families,
not operational scenarios.

## Publication potential (evidence-based, not a novelty claim)

| Class | Current material | Evidence still needed / risk |
|---|---|---|
| **A. Potentially publishable with current evidence, after positioning and consolidation** | Bounded Campaign 2 / Campaign 3 META-VOC findings may support a narrowly framed synthetic methods/results paper; S3b-E1 provides a controlled memory contrast. | Establish literature novelty, explain frozen-population scope, address weak predictor discrimination and selected contrasts, and avoid treating synthetic results as external validation. Current evidence is not enough for a general HLS theory claim. |
| **B. Promising but needs more validation before a standalone claim** | Budgeted routing, dynamic MMLU organization, DCS-LA, S4/S7 planning and transfer analyses. | Small task/model sets, predictor and timing dependence, uncertain pairwise contrasts, finite exact instances, limited independent populations, and known overlap with published ensemble/routing/planning results. |
| **C. Technical/scientific antecedents** | S1–S2b exact references; classifier exact enumeration; HLS-PEF/ExperimentRun; S4/S7 finite solver checks. | Useful as methods, controls, reusable infrastructure and bounded demonstrations; infrastructure alone is not a novel scientific result. |
| **D. Closed or not currently justified for further investment** | S3b-E1 is closed; classifier-combination pilot is complete and not extended; original/corrected routing and MMLU pilots have reports; no S8 exists. | Do not reopen or extend by default. This status does not declare all broader research questions closed. |

## Laboratory implementation state

- **Scenario/mechanism code:** substantial, runnable, and tested for the
  represented finite and synthetic routes; definitions and state semantics
  remain route-specific.
- **Organizational problems:** B1/B2/B3 are represented in different
  scenarios, but there is no universal modality interface or optimizer
  registry.
- **ExperimentRun v1 / HLS-PEF:** implemented, tested and used in S2a/S4/S7
  vertical slices and recent S3b/model-routing experiments. Shared structures
  preserve provenance and availability; they do not make unlike physical
  metrics equivalent or perform paired statistical inference automatically.
- **Integration:** adapters and runners remain scenario-specific. The
  deterministic S4 integration does not validate S4 P0/P1/P2 or effective
  transfer. S3b-MMLU records use the common run/evaluation structures, but
  not every historical runner is natively integrated.
- **Publication and external validity:** open; reproducible code is necessary
  infrastructure, not by itself a publication contribution.
- **Artifact integrity:** the saved-output hashes in the corrected MMLU,
  DCS-LA and routing manifests verified. The initial dynamic-MMLU manifest
  verifies its eight output artifacts, while its source-code hash does not
  match the current evolved source file; the historical manifest and results
  are preserved, and that source hash is not represented as verified.

## Evidence index

- [Unified scientific framework](architecture/HLS_UNIFIED_FRAMEWORK.md)
- [Ontology v0.1](architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md)
- [HLS-PEF specification](architecture/HLS_PERFORMANCE_EVALUATION_FRAMEWORK.md)
- [Collective-performance audit](architecture/HLS_COLLECTIVE_PERFORMANCE_AUDIT.md)
- [Cumulative execution plan and dated experiment log](engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md)
- [Current laboratory roadmap](engineering/HLS_LAB_ROADMAP_CURRENT.md)
- [Experiment contract integration](engineering/HLS_EXPERIMENT_CONTRACT_INTEGRATION.md)
- [S4 semantic integration audit](engineering/HLS_S4_SEMANTIC_INTEGRATION_AUDIT.md)
- [S2a/S4/S7 HLS-PEF integration results](../results/experiments/hls_s2a_pef_integration/results.json), [S4](../results/experiments/hls_s4_pef_integration/results.json), [S7 pilot](../results/experiments/hls_pef_s7_pilot/results.json)
- [S3b memory diagnostic](../results/experiments/hls_s3b_memory_replay_diagnostic/results.json), [S3b observability factorial](../results/experiments/hls_s3b_observability_recovery/results.json)
- [Classifier-combination exact validation](../results/experiments/hls_expert_complementarity_math_validation/results.json)
- [Budgeted routing report](experiments/HLS_BUDGETED_LLM_ROUTING_CONSOLIDATED_REPORT.md)
- [Corrected MMLU organization](experiments/HLS_DYNAMIC_CAPACITY_ORGANIZATION_CORRECTED.md), [DCS-LA](experiments/HLS_CONTEXTUAL_CAPACITY_SELECTION.md)

The detailed dated account below preserves prior project status, historical
decisions, integrity notes and experiments outside the current S1–S7 work.
Where an older status paragraph says that a later-dated Hito or result is
pending, the dated cumulative log and this 23 October snapshot supersede it;
the historic entry itself remains unchanged.

This is the single canonical summary of the programme's present scientific
state. It records both established results and the current methodological
position of the HLS research programme.

Frozen protocols, detailed derivations, executable code, and result artifacts
remain authoritative for their own scope; this file does not replace them.

## HLS-G0-C6 experiment disposition — 2026-10-19

**HLS-G0-C6 is CLOSED — STOP.** Its exact finite-instance HLS versus
BEST_STATIC gap is documented in the [canonical closure record](experiments/HLS_G0_C6_CLOSURE_2026-10-19.md),
with trajectory evidence in `results/experiments/hls_g0_c6/`. C6 quantifies
an anticipatory-development and subsequent flexible-routing mechanism already
consistent with G2, G3-H and RQ0; it does not establish general superiority or
a new structural result. Do not reopen or extend this experiment. This
experiment identifier is distinct from the separately named synthetic
capability C6 in the capability taxonomy. The STOP decision does not change
RQ0's status or the broader HLS programme.

## Consolidated laboratory status — 2026-10-17

The published laboratory retains an operational HLS N×K / MIS-v2 route.
Nembhard Direct is available with explicit feasible allocations,
`nembhard_oracle`, and `nembhard_adaptive`. The contextual quality–cost router
is an independent capability, not connected to the N×K runner. A versioned
common experiment envelope adapts these route results with typed events,
route-specific metrics, units, provenance fields, and stable JSON; it does not
establish scientific comparability across mechanisms. System-1.x and Baccara
remain deferred. HLS Laboratory remains **PARTIAL**.

The final full suite after the estimator/resume repair completed with 1,512
passed and the same 5 known historical integrity/inventory failures in 611.98 seconds.
The five were `test_every_foundation_result_has_consistent_manifest` (12 result
directories versus frozen count 11), `test_frozen_inputs_and_completed_artifacts`
(Campaign 2 closure digest), `test_preexperiment_manifest_and_contamination_boundary`
(frozen theory-source digest), `test_pre_execution_manifest_and_raw_integrity_when_present`
(frozen `finite_problem_belief.py` input), and
`test_source_hashes_and_raw_output_hashes` (strategy-gate source digest).
These match the previously documented provenance/inventory failures; this
task did not alter their manifests, hashes or artifacts. The reviewed Nembhard
allocation protocol has a deterministic configuration registry, guarded
execution CLI, common-contract result adapter, and post-run analysis in
`src/hls/nembhard_campaign.py`. The registry contains 1,016 unique
configurations after reuse of two identity diagnostics. HLS-E1 execution was
started and interrupted; the earlier tracked incident record counted 29
valid completed episodes and 987 pending. A later read-only inspection of the
current local result tree validates 1,016 complete episodes and zero pending;
the result directory and analysis file are untracked/unpublished in this
worktree, so this discrepancy is recorded rather than silently treating the
local files as repository-published evidence. Neither record is changed by
the adaptive-capability validation below. Resume validates all three result
files and requires an explicit command/token. See the [runner record](engineering/HLS_NEMBHARD_CAMPAIGN_RUNNER.md),
[execution plan](engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md), and
[history](HISTORY.md).

## Bounded adaptive-capability validation — 2026-10-17

Five small checks reuse existing C5/N×K fixtures, the current runner, the
canonical G2 D0/D1/D2 references and the saved four-period imperfect-information
P2 reference. Stationary, time-indexed nonstationary and seeded Markov demand
were generated and then verified against problem IDs executed by the N×K
runner. In the indexed shift fixture, P0's selected allocation changed across
the changed current problem. The reference trace preserves actual and
estimated competence, observations, MIS-v2, teaching increments, efficacy
memory, output and resource accounting. This validates bounded execution and
trace contracts, not policy superiority, demand inference, external validity
or full literature reproduction. The G2 controls are explicitly not identified
with the MIS-v2 transition. The focused suite passed 135 tests; the full suite
was not rerun. No large campaign was run. See the [canonical validation
record](experiments/HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md), its
[machine-readable registry](../results/analysis/hls_lab_validation/capability_registry.json),
and [compact evidence](../results/analysis/hls_lab_validation/integrated_validation_results.json).
HLS Laboratory remains **PARTIAL**.

**Prior-session priority — recorded 2026-10-17 for 2026-10-18; resumed
2026-10-19:** the task was to inspect primary papers, compare concrete
experiments with existing HLS components, select one, and prepare a bounded
protocol. This was documentary work only. The source review found no candidate
that currently meets exact or defensibly approximate reproduction requirements
with the available HLS mechanisms and source artifacts. MixLLM §4.3/Table 1
was the closest candidate screened, but the HLS contextual router has a
different predictor, selector, feedback model, and synthetic data; source
data/runtime dependencies also remain unresolved. The recommendation is
**STOP before execution**, not a claim that HLS lacks adaptive capability. See
the [selection report](experiments/HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md)
and [cumulative plan decision](engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md).
No experiment or campaign was run, no model was changed, and HLS remains
**PARTIAL**. Any later reproduction requires resolving the documented
dependencies, a faithful protocol, and separate PI authorization.

The programme-level philosophy is defined in [HLS_PHILOSOPHY.md](HLS_PHILOSOPHY.md),
and the common semantic contract is defined in [the HLS ontology](hls_ontology.md).

## Current operational direction — 15 October 2026

**Decision event:** 2026-10-15; exact decision time was not supplied.
**Documented:** 2026-10-15 09:45 +02:00 (Europe/Madrid). See the dated entry
in the [canonical project history](HISTORY.md).

The PI and Chief Engineer approved prioritizing completion of **HLS Laboratory
v1 as integrated experimental infrastructure**. The active milestone is
**HLS-LAB-V1-INTEGRATED — APPROVED / IMPLEMENTATION PARTIAL**. An additive
integrated teaching runner, P0/P1/P2 policies, a policy-independent exogenous
problem-trajectory generator and focused acceptance tests now exist. The
generator composes C5 demand processes with the existing dynamic problem
emitter; problem trajectories are frozen before policy evaluation. Two
authorized provenance validators were corrected: B2.3 now verifies the
protocol blob at the run's recorded Git revision, and Campaign 2 preregistration
checks source/artifact scope against its immutable freeze snapshot. The latest
full suite (2026-10-16 18:23 +02:00) reports 1,337 passed and the same 5
historical provenance/integrity failures: foundation inventory/B13 manifest,
unavailable `finite_problem_belief.py` source evidence, and Campaign 2
closure-document hashes. Provenance is not fully restored. See the
[provenance diagnosis](engineering/HLS_PROVENANCE_FAILURE_DIAGNOSIS.md) and
the dated [history entry](HISTORY.md).
As of **2026-10-16 14:56 +02:00** (Europe/Madrid), the additive N×K path
supports deterministic production-only episodes with dimension-independent
P0 under frozen competencies and perfect information. It reuses Phase 1's
validated geometry/catalogue, supports K-dimensional requirements and CES
weights, and records production, functional outcomes and resource use without
modifying the legacy simulator. Direct 3×2 comparisons match legacy P0
decisions and episode metrics; the existing 64-production / 508-integrated
catalogue and serialized P0/P1/P2 hash regressions remain covered. See the
[N×K technical design and Phase 1–2 record](engineering/HLS_NK_GEOMETRY_TECHNICAL_DESIGN.md).
N×K MIS-v2, learning, teaching, estimation, P1/P2 and environment emission
remain unsupported; the full legacy 3×2 simulator remains operational. Phase
1's 50-test validation and current Phase 2 validation (99 focused passes;
full suite 1288 passed / 5 failed) are retained in `HISTORY.md`. The five
known failures are unchanged repository provenance/integrity issues; no frozen
expected hash or historical artifact was changed.

**Current N×K status — 2026-10-16 15:50 +02:00 (Europe/Madrid):** Phase 3A
adds MIS-v2 learning-by-doing to the N×K P0 episode runner. It reuses the
unchanged scalar DISCOVER-v2 law, applies cell-specific eta values to the
effort assigned in each period, and records output/reward from pre-learning
competence before applying the transition for the next decision. Both MIS-OFF
(Phase 2 contract) and MIS-ON are available. N×K episodes remain perfect
information; teaching, estimation, P1/P2 and environment generation are not
generalized. Validation: 87 focused tests passed; full suite 1303 passed and
the same five historical provenance/integrity tests failed. A paired MIS
OFF/ON regression verifies identical initial state, problem sequence and first
period before any learning-induced divergence. Engineering timing
and trace-memory measurements and the exact transition contract are in the
[N×K geometry technical design](engineering/HLS_NK_GEOMETRY_TECHNICAL_DESIGN.md).
HLS Laboratory remains **PARTIAL**; this is a mechanism validation, not a
scientific campaign.

**Current N×K status — 2026-10-16 16:22 +02:00 (Europe/Madrid):** Phase 3B
adds a dimension-independent directed teaching transition and explicit joint
actions to the N×K episode runner. Teaching efficacy is an `N×N×K` relation
tensor; teaching charges both participants and competes with production for
the same collective budget. The explicit action path supports MIS OFF/ON ×
teaching OFF/ON, preserving production → MIS-v2 → teaching order. It does not
select teaching actions automatically and does not generalize P1/P2 or
competence estimation. Historical 3×2 transition and episode checks match;
the old paths remain untouched. Focused validation: 95 passed. Full suite:
1320 passed, 5 failed in 479.80s; all five match the documented provenance
baseline (foundation inventory count, Campaign 2 closure/source hashes,
Campaign 3 frozen source hash, and strategy-gate source hash); no functional
regressions appeared. Performance and equation details are recorded in the
[N×K technical design](engineering/HLS_NK_GEOMETRY_TECHNICAL_DESIGN.md).
HLS Laboratory remains **PARTIAL**; no campaign was run.

**Current N×K status — 2026-10-16 18:23 +02:00 (Europe/Madrid):** Phase 3C adds
dimension-independent P0/P1/P2 coordination with one shared decision-view,
memory and policy-parameter interface, and automatic joint production /
teaching action selection to the N×K runner. P0 remains production-only. The
historical lexicographic production ranking, P1 fixed directed relation, P2
success-first/unseen-relation/efficacy-threshold rules, catalogue tie order,
and production → MIS-v2 → teaching timing are retained. Joint actions enforce
individual participant loads and the shared budget, with explicit
`max_candidates` failure rather than truncation. Policy views contain problem
requirements, current estimated competence (the required perfect-information
condition), allowed feasible actions and observed efficacy memory, but no
private efficacy tensor or organization configuration. P2's formative update
uses the existing deterministic zero-noise observation case. Direct 3×2
decision and outcome checks match the legacy policies under matched perfect
information; the 64-production/508-integrated catalogues remain pinned. N=1
supports P0; P1/P2 require a valid distinct-agent teaching relation and
therefore cannot be instantiated for N=1. Competence estimation, imperfect
information and noisy formative observations remain unsupported. Focused
validation and engineering measurements are recorded in the [N×K technical
design](engineering/HLS_NK_GEOMETRY_TECHNICAL_DESIGN.md). No scientific
campaign was run. Phase 3C focused validation passed 93 tests; the final full
suite passed 1,337 in 475.44 seconds and retained the same five documented historical provenance /
integrity failures. HLS Laboratory remains **PARTIAL**.

**Current N×K status — 2026-10-16 19:10 +02:00 (Europe/Madrid):** Phase 3D
adds explicit perfect- and imperfect-information execution modes. Imperfect
mode reuses the historical finite-grid competence posterior, per-cell noisy
production observations, MIS-v2 posterior prediction, and noisy formative
efficacy observation; actual competence remains the production/transition
state, estimates drive only policy views, and observation/latent diagnostics
are not exposed to policies. The established runner remains unchanged when
the new `information_mode` argument is omitted. Focused validation covered
N×K dimensions and matched legacy 3×2 trajectories for P1/P2, MIS, teaching,
both observation streams, posterior updates and efficacy memory; 86 focused /
regression tests passed. The full suite had 1,357 passed and the same five
documented provenance/integrity failures, with no new functional regression.
Measurements and failure names are in the [N×K technical design](engineering/HLS_NK_GEOMETRY_TECHNICAL_DESIGN.md)
and dated [history](HISTORY.md). No campaign was run; HLS Laboratory remains
**PARTIAL**.

**Current N×K status — 2026-10-16 20:08 +02:00 (Europe/Madrid):** Phase 4
adds K-dimensional demand emission using the existing C5 stationary (IID),
time-indexed nonstationary and first-order Markov task processes. Each
environment maps its latent task state to an independent finite catalogue of
`ProblemSpecNK` types; problem-type count is not tied to K. Generated paths
record the seed, configuration, sampled environment states/regime labels and
emitted problem specifications. Environmental randomness is completed before
organization execution and is separated from Phase 3D observation randomness.
The N×K runner now accepts either its existing explicit problem sequence or an
environment configuration plus seed; the generated path is then passed through
the same runner. Fixed sequences therefore remain a supported experimental
input, while stationarity remains a process property rather than a generator
class. The existing 3×2 environment was matched on demand states, problem IDs,
requirements, equal CES weights and budget. Focused environment and Phase 1–3D
regressions passed 155 tests. Full suite: 1,390 passed and the same five
documented provenance/integrity failures in 515.55 seconds; this full-suite run
preceded two final controls for seed variation and replay across different
organizations, which passed in the complete 155-test focused environment/C5/
dynamic/Phase 1–3D selection. HLS Laboratory remains **PARTIAL**; this is
infrastructure validation, not a scientific campaign. Details and local
microbenchmarks are in the [N×K technical design](engineering/HLS_NK_GEOMETRY_TECHNICAL_DESIGN.md)
and [history](HISTORY.md).

**Current validation — 2026-10-16 20:22 +02:00 (Europe/Madrid):** Phase 5
cross-validated complete generated-demand episodes across 1×1, 2×2, 3×2 and
4×3, with all valid P0/P1/P2 × MIS × teaching × perfect/imperfect-information
combinations. Independent trace checks cover production, CES, success,
resources and ordered competence transitions. Fresh-process serialization
matched. The focused HLS/Phase 1–4 regression selection passed 172 tests; the
final full suite passed 1,396 and retained the same five provenance/integrity
failures. Stage-level measurements identify exhaustive joint-action enumeration
as the principal 4×3 bottleneck. No equations, historical results or campaigns
changed. Recommendation: **CONDITIONALLY READY** for a bounded, preregistered
study only if its harness archives a full run manifest, frozen demand and
source/runtime metadata. See the [Phase 5 research-readiness review](engineering/HLS_RESEARCH_READINESS_REVIEW.md).
HLS Laboratory remains **PARTIAL**, pending PI review.

**Current mechanism status — 2026-10-17 11:46 +02:00 (Europe/Madrid):** Nembhard Direct v0.1 is now an
explicit alternative execution branch in the N×K runner, alongside the
unchanged default MIS-v2 path. It maintains a separate `D[N,K]` state and
cell-specific `k,p,r`; caller-supplied feasible allocations produce output
from beginning-of-period productivity, then update experience by `e*Δt`.
This exposure mapping and the declared output/requirement-unit calibration
are HLS adaptation conventions, not claims about the article's unresolved
timing. The branch reuses existing task evaluation and effort/resource
validation, requires an explicit unit contract, and records separate
productivity/experience traces. It does not use HLS competence values and
rejects P0/P1/P2, MIS-v2, teaching and estimation in this mode. Explicit
`mechanism_id="mis_v2"` is byte-identical to the default in frozen and MIS-v2
learning tests. See the [integration contract](engineering/HLS_EXTERNAL_MECHANISM_INTEGRATION_01.md).
The final focused mechanism/N×K regression selection passed 222 tests,
including generated-environment replay. No campaigns were run; HLS Laboratory
remains **PARTIAL**.

The ten-file minimum reproducible package is published on
`feature/hls-laboratory-v1` at `37a011804f9ea013fc3a5436c00a72eb0b8280da`.
The acceptance gate is therefore not closed. See the implementation record in
[HLS Laboratory v1](experiments/HLS_LAB_V1.md). This changes the
operational priority, not HLS's research questions or general scientific
doctrine: HLS continues to ask **WHO SHOULD DO WHAT?** and **WHO SHOULD LEARN
WHAT, HOW, AND FROM WHOM?** HLS concerns dynamic management of heterogeneous
capabilities; it is not exclusively a worker-training simulator, and teaching
is one possible competence-development action.

**Nembhard routing status — 2026-10-17 11:58 +02:00 (Europe/Madrid):** The
N×K runner now optionally supports `router_id="nembhard_oracle"` with
`mechanism_id="nembhard_direct"`. This deterministic oracle uses the true
Nembhard experience/profile state, enumerates resource-feasible actions, and
shares the exact P0 functional lexicographic rank (success, normalized
deficit, margin, effort); it predicts only current-period output and breaks
ties by existing catalogue order. A competence-free resource view keeps HLS
competence out of this policy interface. The trace records the selected
catalogue action and predicted output for comparison with execution. This is
an information-perfect baseline, not a learned router or MixLLM reproduction;
future-learning value is not optimized. Focused Nembhard and N×K regressions:
166 passed. MIS-v2 default/explicit equivalence tests remain passing. No full
suite or campaign was run. The next planned step is a router based on
productivity estimates. HLS Laboratory remains **PARTIAL**; details are in the
[oracle-router contract](engineering/HLS_NEMBHARD_ORACLE_ROUTER.md) and the
[execution plan](engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md).

**Nembhard adaptive-router status — 2026-10-17 12:17 +02:00 (Europe/Madrid):**
The N×K Nembhard route now also supports `router_id="nembhard_adaptive"`.
It uses a per-cell online running mean and Welford dispersion from configurable
individual work-output observations; negative observed rates are clipped to
zero, zero-work cells are unobserved, and a minimum-work threshold avoids
unstable division. The estimate-based selector shares the existing P0
functional/effort rank and catalogue tie-breaking. Optional epsilon-greedy
exploration uses a separate seed from observation noise. Its decision view
contains no true `k,p,r`, productivity, or HLS competence; decision-visible
experience is reconstructed only from allocations executed in this run. The
runner executes true Nembhard production, then observes/updates the estimator
for subsequent decisions, with experience likewise available to next-period
production. Per-period traces distinguish predictions, observations,
estimator state and diagnostic truth. The default MIS-v2 path, historical
P0/P1/P2 and ORACLE route are unchanged. Final focused Nembhard selection: 48
passed; full N×K/Nembhard selection: 180 passed. Full suite: 1,458 passed and
5 failed in 633.87s; the failures are the known foundation inventory,
Campaign 2 closure/theory digests, Campaign 3 frozen source, and strategy-gate
source integrity checks. One additional focused test was added and passed
after that suite run. No campaign was run. See the
[adaptive-router contract](engineering/HLS_NEMBHARD_ADAPTIVE_ROUTER.md) and
the updated [execution plan](engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md).
No historical evidence or PDFs were altered; HLS Laboratory remains
**PARTIAL**.

**Contextual quality–cost router status — 2026-10-17 (Europe/Madrid):** HLS
now has a separate, bounded contextual-routing implementation in
`src/hls/contextual_router.py` and a local synthetic execution environment in
`src/hls/contextual_router_synthetic.py`. It predicts per-candidate quality
and simulated monetary cost with separate ridge regressions, selects by the
approved quality-threshold/minimum-predicted-cost rule (with its maximum-
quality fallback), and updates only from feedback of the candidate actually
executed. Optional seeded epsilon exploration is off by default. Traces and
descriptive summaries keep observed quality, cost, and budget compliance
separate. This is an independent contextual query-router capability, not a
mapping onto agents or `ProblemSpecNK`, not a MixLLM reproduction, and not
evidence of scientific benefit. Real-domain schema, priors, evaluator and
accounting remain caller responsibilities. Focused validation: 17 passed;
related N×K regressions: 162 passed; full suite: 1,476 passed and the same 5
known provenance/integrity failures in 595.25s. No campaign was run. MIS-v2,
Nembhard, P0/P1/P2, and historical results were not changed. See the
[implementation note](engineering/HLS_MIXLLM_ROUTER_IMPLEMENTATION.md) and
[normative v0.1 contract](engineering/HLS_MIXLLM_ROUTER_CONTRACT.md). HLS
Laboratory remains **PARTIAL**.

**Common experiment-envelope status — 2026-10-17:**
`src/hls/experiment_contract.py` now adapts existing N×K/MIS-v2, Nembhard
Direct and contextual-router results into the versioned
`hls-experiment-run/1.0` record. It adds ordered events, explicitly named
units, separate route-specific metrics, optional provenance, and stable JSON
without changing source result objects or native serializers. 11 contract
tests passed, with 184 combined focused adapter and route regressions. The
envelope is post-execution only: it does not supply a shared runner, infer
missing seeds/configuration, convert metrics, or establish cross-route
scientific comparability. See the [common experiment contract](engineering/HLS_COMMON_EXPERIMENT_CONTRACT.md).
HLS Laboratory remains **PARTIAL**.

Work is separated into two levels. **Infrastructure (first):** functional
completeness, coherent states/transitions, shared-resource constraints,
real/observed-state separation, reproducibility, policy comparability, and
replaceable mechanisms. **Scientific research (subsequently):** theory,
literature review, hypotheses, baselines, experiments, statistical analysis,
and publishable claims. Simple infrastructure mechanisms need not be optimal
or empirically definitive, but must remain causally coherent, reproducible,
and verifiable; this priority does not relax scientific rigor.

The approved implementation is one milestone, organized as B1 joint actions
and shared resources; B2 teaching transition; B3 observations and elementary
estimation; B4 minimal adaptive policy; B5 integrated multi-period execution;
and B6 tests and reproducible demonstration. Teaching must consume resources
that could otherwise support production; individual learning and teaching
remain distinct; policies must not receive private simulator state; teaching
may help or hurt and may be declined; and disabling new mechanisms must
preserve historical behavior under an explicit compatibility contract.
Small collectives, two competence dimensions, short horizons, fixed but
heterogeneous teaching efficacy, configurable observation noise, elementary
estimators, and heuristic policies are permitted as explicit replaceable
simplifications—not as empirically validated models.

At the time this earlier status was recorded, the active next action was to
resolve or formally disposition unrelated full-suite integrity failures and
close remaining acceptance gaps against [HLS Laboratory v1](experiments/HLS_LAB_V1.md).
That remains relevant to claims of full milestone completion; it does not
block the documentary literature-selection task now authorized for
2026-10-18. Previous recommendations to prioritize a narrower research line
are historical and superseded as the immediate operational priority, not
erased as evidence of the project's evolution. The 2026-10-17 decision above
supersedes the earlier next action for the 2026-10-18 session; the five known
provenance/inventory failures remain unresolved and are not represented as
fixed. The dated history is the chronology authority; this file records the
current status rather than duplicating that chronology.

### Campaign 2 sensitivity audit — 16 October 2026

The read-only [experimental sensitivity audit](experiments/HLS_EXPERIMENTAL_SENSITIVITY_AUDIT.md)
verified why Campaign 2's ten noisy replicates per scenario have identical
CES: indexed noise changes observations and estimates, but not outcome-relevant
P0 choices in A/B; the action-path changes in C are output-equivalent ties.
All scenario/condition cells have one demand path, one true-competence path,
one CES trajectory and one success trajectory. P0's score boundaries,
success saturation, capability frontiers, source-to-outcome dependency map,
and causal-identifiability limits are documented against the published traces
and code. The audit reran 16 focused Campaign 2 tests successfully and
verified all eight source and six frozen output hashes. It did not rerun the full repository
suite; the known 13 provenance/integrity failures remain unresolved. This
diagnostic does not change the laboratory's **PARTIAL** status or authorize a
new campaign.

### Minimal theoretical model — 16 October 2026

The domain-independent [minimal HLS theoretical model](theory/HLS_MINIMAL_THEORETICAL_MODEL.md)
now states the common finite-horizon, partially observed assignment and
development problem, including multiple pending tasks and shared resources.
It derives conditional comparisons for current-best versus learning-oriented
assignment, teaching versus learning-by-doing, same-skill substitution versus
assignment-mediated complementarity, and a narrow greedy concentration case.
These are model-scoped results, not novelty claims or empirical findings. The
document maps each quantity to the existing simulator and records gaps,
including the absence of general multi-task queueing and of an objective that
values CES and resource use in a common unit. No code or experiment changed;
the lab remains **PARTIAL**.

### Authorized scientific pilot — 15 October 2026

The CE authorized and completed a bounded **Scientific Campaign 1 pilot** on
exploitation versus teaching/capability development. The protocol covers 16
predeclared demand × initial-deficit × teaching-effectiveness × horizon cells,
10 paired seeds per cell, four policy conditions, and a matched individual
MIS-v2 learning ON/OFF block (1,280 policy runs). Results and machine-readable
traces are in `results/experiments/hls_campaign1_pilot/`; the runner is
`experiments/synthetic/hls_campaign1/run.py`.

The validated run completed 2026-10-15 10:22:04 +02:00 (Europe/Madrid), using
10 non-overlapping seeds (`2026101511`–`2026101520`) per cell, a common
PARTIAL_STATIC prior (0.40 for each skill), and a shared budget of 2.0. P0
production-only had higher CES than P1 in 320/320 paired comparisons. Against
P2, P0 was higher in 241/320, lower in 37/320, and tied in 42/320; against
the scheduled no-feedback control it was higher in 258/320, lower in 20/320,
and tied in 42/320. P2 nevertheless outperformed P0 on both CES and success
in high-deficit/high-efficacy/long-horizon cells with individual learning
OFF: ΔCES +0.313 (SD 0.194) and
Δsuccess +0.483 (SD 0.074) under stationary demand; ΔCES +0.380 (SD 0.107)
and Δsuccess +0.537 (SD 0.105) under changing demand. These advantages did
not appear with individual learning ON. P2 outperformed the no-feedback
teaching schedule in some matched cells, while P1 fixed teaching was
consistently harmful. P2 declined to teach in 4,497/5,120 episodes. These are
bounded pilot observations, with ten-seed descriptive variability only—not
population inference or a general claim that teaching is beneficial.

Three earlier executions were excluded and retained as invalid-attempt
manifests: one exposed an experimenter-only regime label; one initialized
estimated skills from private truth; and one used budget 1.0, which made all
teaching-period production zero because the frozen action catalogue's
minimum positive productive allocation costs 1.0 and a lesson consumes 0.5.
The final budget 2.0 was selected by that action-granularity check, not by
policy outcomes, and a fresh seed namespace was used. The final policy input
contains only the generic observed label and a shared PARTIAL_STATIC estimate.
Non-applicable CSV metrics are explicitly encoded as `NA`.

One remaining resource limitation is that frozen production actions have
integer total effort: a teaching period consumes 0.5 units and leaves 1.5
available, but at most one full productive unit can be assigned; without
teaching, two units can be productive. Thus the realized production
opportunity cost is shaped by the existing action granularity, not just the
0.5 teaching charge.

This scientific pilot does not close `HLS-LAB-V1-INTEGRATED`, change its
acceptance status, or resolve the previously recorded 13 full-suite
integrity/provenance failures. See the dated [history entry](HISTORY.md) and
the manifest for protocol, source, seed, and artifact hashes.

The consolidated evidence across the pilot, mechanism diagnostics,
counterfactual teaching analysis, and behavioral-plausibility checks is in
[HLS Campaign 1 findings](experiments/HLS_CAMPAIGN1_FINDINGS.md). It preserves
the conditional positive and negative cases, the resource/action-granularity
limitation, and the distinction between verified behavior and the open
teaching × learning-by-doing hypothesis. No new campaign was run for that
synthesis; the laboratory remains **PARTIAL**.

### Campaign 1 mechanism diagnostics — 15 October 2026

Diagnostic analysis timestamp: 2026-10-15 14:28:17 +02:00 (Europe/Madrid).

The published pilot traces were analyzed without rerunning its 1,280 runs.
The paired P2−P0 CES contrast averaged −0.241 (between-seed SD 0.181) with
MIS-v2 ON and −0.126 (SD 0.246) with MIS-v2 OFF. The descriptive difference
in differences, `Delta_ON − Delta_OFF`, was −0.115 (SD 0.196; 160
configuration-seed pairs: 28 positive, 112 negative, 20 ties). This is an
in-simulator factorial interaction, not a population-level or mechanism-share
estimate.

Across the 320 P2/P0 trajectories, 278 experienced a negative cumulative CES
difference during a run in which P2 taught. Thirty-nine later crossed back to
nonnegative cumulative difference; 239 never did. At the end, P2 was ahead in
37, behind in 241, and tied in 42. The 42 P2 trajectories with no teaching
were ties. In the high-deficit/high-efficacy/long-horizon cells, every
first-teaching episode had lower same-period CES than P0. With MIS OFF all 20
such trajectories later crossed break-even and ended ahead (mean crossing
period 8.2 after changing demand, 17.3 under stationary demand). With MIS ON,
only 4/20 crossed after the teaching-associated negative path; 3/20 ended
ahead, so a crossing did not always persist.

Resource accounting was recoverable directly: each lesson used 0.5 total
participant effort, and all 7,422 logged teaching episodes paired with 1.0
production effort versus P0's 2.0, leaving 0.5 budget unused because of the
discrete action catalogue. Across 320 run blocks per policy, P1 taught 5,120
times, P2 623 times, and the scheduled no-feedback control 1,679 times.
Exact per-event `teaching_gain_real` was absent from the published CSV, so
876 teaching-containing policy/seed blocks were deterministically replayed;
actions, CES, resources, and real-competence trajectories matched the frozen
records. The replay recovered 7,422 direct teaching increments. These are
simulator-private diagnostics, not policy observations. The original CSV's
net competence change cannot by itself separate MIS-v2 from teaching when LI
is ON.

The analysis and provenance are in
`results/diagnostics/hls_campaign1_mechanism_diagnostics/`, generated by
`experiments/synthetic/hls_campaign1/analyze_mechanisms.py`. The P2−P0 contrast
is a total policy-package comparison. The MIS ON/OFF difference-in-differences
isolates the interaction of that toggle with the policy contrast only within
this simulator and fixed design. P2 versus scheduled no-feedback does not
isolate organizational information: their teaching choices/exposures differ.
Teaching effort and residual capacity are exact; translating them into
productive value is limited by action granularity. All seed summaries remain
descriptive, without significance tests or population inference. The pilot's
production-choice score remains functional success/deficit/margin/effort,
not CES.

Among recorded teaching events, mean direct competence increment was 0.0352
for P1 at high efficacy and 0.0103 at low efficacy; P2's selected events
averaged 0.1024/0.0131 with MIS OFF and 0.1014/0.0128 with MIS ON (high/low
efficacy). These per-event summaries are conditional on each policy's
selection and state trajectory, and are not comparable efficacy estimates.
The reproducible command is
`PYTHONPATH=.:src python experiments/synthetic/hls_campaign1/analyze_mechanisms.py`.

### Campaign 1 counterfactual teaching value — 15 October 2026

At 2026-10-15 15:34:12 +02:00, a bounded, state-conditional intervention
analysis completed from the published pilot. Its prespecified sample is the
full long-horizon grid of demand (stationary/changing), initial deficit
(low/high), efficacy (0.10/0.85), MIS (OFF/ON), and intervention timing
(period 2/16), with the first published seed `2026101511`: 32 states. Each
state compared the existing directed relations `(2,1,1)` and `(0,1,0)`, for
64 paired remaining-horizon branches. States were not outcome-selected.

The continuation rule was the same existing P2 in both branches. The
no-teaching intervention used P0's observable, production-only action; the
teaching intervention used the best feasible production allocation for the
specified relation under the same observable decision score. Thus this is a
conditional intervention contrast, not an optimal policy comparison. In all
64 initial pairs, the lesson used 0.5 effort, displaced 1.0 productive effort,
and left 0.5 of the shared budget unused under the frozen action granularity.
Immediate CES difference averaged −0.142 (SD 0.103). Remaining-horizon
`DeltaV_H` averaged −0.074 (SD 0.181; range −0.370 to +0.565): 19 positive
and 45 negative cases. Early interventions (22 decisions remaining) averaged
+0.033 (SD 0.186; 19 positive, 13 negative); late interventions (8 remaining)
averaged −0.181 (SD 0.093; all 32 negative). These are one-seed-per-stratum
descriptive simulator outcomes, not population estimates.

At selected states, P2 chose no teaching in 22/32 and the `(0,1,0)` relation
in 10/32. Against the tested candidate-specific counterfactual values, its
choices classified as 17 no-teaching decisions with no positive tested
candidate, 5 missed positive opportunities, 4 selected positive teaching
cases, and 6 harmful selected teaching cases. These labels are conditional
diagnostics, not policy regret against an oracle. The full posterior was not
saved in the pilot CSV; deterministic prefix replay reconstructed it and
matched the frozen pilot trace before branching. Results and hashes are in
`results/diagnostics/hls_campaign1_counterfactual_teaching_value/`; code and
focused tests are `experiments/synthetic/hls_campaign1/counterfactual_teaching.py`
and `tests/test_hls_campaign1_counterfactual_teaching.py`. The test command
is `PYTHONPATH=src:. pytest -q tests/test_hls_lab_v1_integrated.py tests/test_hls_campaign1_pilot.py tests/test_hls_campaign1_mechanism_diagnostics.py tests/test_hls_campaign1_counterfactual_teaching.py`;
the trace manifest records the run command and hashes. This estimate is
conditional on the selected state, specified event, P2 continuation, frozen
exogenous suffix, and common indexed innovations; it is not globally optimal
teaching value.

### Campaign 2: teaching × MIS × work assignment — 15 October 2026

The CE-authorized bounded experiment completed at **2026-10-15 20:39:04 +02:00**,
with this record updated **2026-10-15 20:44 +02:00** (Europe/Madrid).
Three prespecified scenarios each used one deterministic and ten noisy
matched teaching ON/OFF × MIS ON/OFF quadruples, plus a zero-efficacy control:
34 quadruples, 136 runs, 3,264 decisions. All branches used the same P0
production-only continuation after one forced period-0 lesson.

The CES interaction `(R11−R01)−(R10−R00)` was −1.092473 when the learner
already participated, +1.561953 when teaching changed its preferred
productive assignment, and +0.339151 after an exogenous demand switch.
The latter two scenarios opened respectively 23 and 11 subsequent learner
target-skill exposures; the first left subsequent assignments unchanged.
These are conditional model results, not identified causal mediation.
No-teaching functional success was 24/24; teaching was 23/24 even where
cumulative CES improved. All ten noise seeds per scenario had the same CES
totals despite distinct estimates and some different equally productive
assignments; collapsed bootstrap intervals do not establish zero uncertainty.

See [Campaign 2 findings](experiments/HLS_CAMPAIGN2_FINDINGS.md) for the
registered rationale, four-condition outcomes, direct/MIS gains, negative
controls, full traces, source hashes and reproduction commands. Results are
isolated in `results/experiments/hls_campaign2_teaching_mis_assignment/`.
Sixteen new tests plus 107 relevant regressions passed. The full suite was
not rerun; the 13 historical provenance/integrity failures remain and
`HLS-LAB-V1-INTEGRATED` stays **PARTIAL**. No laboratory physics or policy
was changed; Campaign 1 findings remain intact.

## Current empirical status — 13 October 2026

### Behavioral plausibility validation — 15 October 2026

Validation run: **2026-10-15 17:42:56 +02:00** (final reproducible artifact
generation); status recorded at **17:43 +02:00** (Europe/Madrid).

Small deterministic checks were added in `tests/test_hls_behavioral_plausibility.py`
and run with `experiments/synthetic/hls_lab_v1/behavioral_plausibility.py`.
They exercise existing production, resource, MIS-v2, teaching and exogenous
environment mechanisms; they do not modify their physics or constitute a
campaign. Production is additive (`Y_k=Σ_i x_ik s_ik`), so specialization and
multidisciplinary complementarity here mean relevance to explicit functional
requirements, not superadditive agent interaction. The discrete production
catalogue intentionally permits total production effort only in integer
steps. In the reproduced budget-2 teaching example, a 0.5 participant-effort
lesson leaves 1.5 budget, but the catalogue allows only 1.0 productive effort;
the residual 0.5 is stranded and 1.0 productive effort is displaced versus
the no-teaching maximum. No global divisible-allocation control was added.

The deterministic paired intervention fixtures use a fixed requirement of
1.0 on the active skill (the deficit team's two-unit skill-0 frontier is 1.15),
the same P0 continuation, and organizational updates from observations. Their
remaining-horizon CES differences were: adequate team −0.4002 (24 periods;
P2 independently declined teaching); persistent deficit/effective early
teaching +0.8825 (24); short horizon −0.3575 (8); weak efficacy −0.9000 (24);
learning-by-doing ON +2.4445 (24); regime change −0.0475 (24). The positive
long-horizon result crosses cumulative break-even at period 12; the learning-
by-doing case crosses at period 10. These are conditional deterministic
mechanism checks, not estimates of policy superiority. In this fixture,
learning-by-doing increased rather than reduced the intervention's measured
increment; no universal marginal-substitution claim follows. The full result
and source/output hashes are in
`results/diagnostics/hls_behavioral_plausibility/`.

Focused plausibility plus v1/CE-24/CE-25 tests: **54 passed**; DISCOVER-v0,
MIS-v2, dynamic laboratory and published Campaign 1 regression tests:
**56 passed**. The full repository suite was not rerun; its last recorded
result remains 1,189 passed / 13 provenance-integrity failures. No historical
hashes or results were changed. MIS-v2's existing eta domain excludes eta=0;
the zero-learning control is its supported `enabled=False` condition, not a
new per-cell zero-rate parameter. The HLS Laboratory milestone remains
**PARTIAL** pending its previously recorded full-suite provenance disposition.

This dated status block supplements the broader programme and foundational
discussion below. Campaign 3 is a completed, scoped finite-problem study; it
does **not** replace the programme-level HLS reference-problem agenda or
establish a universal account of organization and competence development.

- **Campaign 2 — closed:** its recorded classification is **ROBUST POSITIVE
  WITH IMPORTANT NULL RESULT**. In the frozen Q11-reference population, H1
  (information-conflict descriptors associated with Q10 sensitivity) and H2
  (headroom alone insufficient to characterize development sensitivity) were
  supported; H3 coupling was supported at low prevalence (71/15,360, about
  0.46%). Conditional two-real-reward returns were robustly positive for Q10
  and Q11, while Q01 realized utility was **not supported** (mean return
  0.0015; 95% interval [−0.0194, 0.0193]). The result is not “development is
  useless”; nor does it establish Q11 superiority to Q10, an additive causal
  decomposition, or value beyond the frozen physics and state population.
  G07's Q11 lead in all eight scenarios is secondary, not universal
  superiority. See [Campaign 2 results](experiments/CAMPAIGN_2_RESULTS.md)
  and the separate [state-coverage audit](experiments/CAMPAIGN_2_STATE_COVERAGE_AUDIT.md).
- **Campaign 3 design/gates — closed:** the frozen generator and team-space
  partitions define 21 development generator regimes plus a 10-kernel
  compositional/interpolative holdout, and 20 development team geometries plus
  eight geometrically separated held-out geometries. The pilot was classified
  **PERSISTENT BOUNDARY EVOLUTION** at J=12; the CE pragmatically closed it
  without J=18/J=24 and adopted `ell=11` as a development assessment range,
  not an optimal or saturation horizon. Gate 1 was **PARTIAL LOCAL STRUCTURE**
  (**GO CONDITIONED TO C3.2**); Gate 2 was **SUFFICIENT DEVELOPMENT
  DIVERSITY** and closed. These are development-scope decisions, not
  confirmatory findings.
- **Campaign 3.2/3.3 and confirmatory META-VOC — completed:** C3.2 labels are
  single Monte Carlo realizations of Q11-versus-Q00 initial intervention with
  Q11 continuation, over the current-problem remainder plus eleven subsequent
  problems. C3.3's first selector and later META-VOC development are not
  themselves confirmatory. In the frozen confirmatory comparison, the
  equal-domain META-VOC-50 minus RANDOM-50 cumulative `mu_true` difference was
  +0.1167 per history [95% interval +0.0310,+0.2013], with measured decision
  computation −0.1924 seconds [−0.3539,−0.0228]. The primary 50% point was
  designated after inspecting development results, and realized invocation
  frequencies were not exactly equal. Production differences were positive
  in G1/G2 and not demonstrated in G3/G4. This is evidence for the joint
  frozen-rule contrast in this laboratory, not universal superiority,
  exactly budget-matched efficiency, or a novel selector algorithm. See the
  [confirmatory report](experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md)
  and [scientific record](paper/META_VOC_SCIENTIFIC_RECORD.md).
- **Predictor validity — bounded audit completed in the current worktree,
  not yet committed:** 800 outcome-blind sampled states were evaluated with 32
  independent paired Monte Carlo continuations per state under the exact
  C3.2 horizon/generation and Q11 continuation. Ridge showed limited/modest
  rank discrimination (equal-domain AUC 0.624 [0.572,0.667], Pearson 0.076),
  high error, and only 4.6% specificity at raw predicted advantage zero.
  META-VOC-50's DEEP-routed versus FAST-routed mean C3.2-matched advantage
  contrast was +0.0104 [−0.0200,+0.0431]. Thus reliable opportunity
  identification is **not established**; 71.6% of statewise Monte Carlo
  intervals spanned zero. This narrows the proposed mechanism behind the
  sequential result but does not alter that result. The audit's report,
  code, tests, and outputs remain local uncommitted artifacts; see
  [validity report](experiments/META_VOC_PREDICTOR_VALIDITY_REPORT.md) and
  `results/diagnostics/meta_voc_predictor_validity/`.
- **Campaign 4 — HOLD / NO-GO for full N=800 execution:** preparation and
  bounded engineering verification exist, but no C4 scientific counterfactual
  evaluation was run. Engineering verification found that C4 H0's two-decision
  horizon is not C3.2-label-equivalent; C4 H2 also uses a different horizon
  and physical-stream convention. The bounded predictor-validity audit above
  reproduces C3.2 semantics but does not execute or validate the broader C4
  estimands. The engine report recommends no N=800 execution until the
  scientific status of H0 as a separate diagnostic and remaining precision /
  feasibility issues are explicitly accepted. See [C4 engineering
  verification](experiments/CAMPAIGN_4_ENGINE_VERIFICATION.md). C4 code and
  protocol edits are currently uncommitted; no further gate or campaign is
  authorized by this status entry.

### Consolidated open questions

1. **FAST/DEEP complementarity:** selected actions differ in a minority of
   frozen states (for example, Q00/Q11 diverged on 25.13% of Gate-2 states),
   while many statewise two-policy Monte Carlo values remain sign-uncertain.
   This establishes neither a general complementarity law nor reliable
   statewise routing. The sequential benefit of META-VOC versus RANDOM in
   G1/G2 and the weak C3.2-target prediction audit answer different questions.
2. **Environment-change representation:** C3 represents the latent physical
   world through a generated scalar problem coordinate `p` and a finite
   subjective belief repertoire; generator identity, true problem labels,
   and privileged descriptors are excluded from META-VOC inputs. Whether
   `(S,b,tau)` adequately represents decision-relevant environmental change,
   and how this representation relates to the `C/N/M` experimenter
   descriptors, remains unresolved. The confirmatory domain contrasts do not
   identify causal effects of team geometry, generator dynamics, or visited
   state distributions.
3. **Novelty/publication boundary:** no novelty is claimed for choosing
   between shallow/deep computation, conditional computation allocation,
   supervised selector fitting, benefit estimation, cost use, or a
   benefit-per-cost score. The defensible current description is a bounded
   experimental characterization in a sequential adaptive-capability
   laboratory. There is no recorded comparison against informed alternative
   selectors, and the independent-reviewer publication assessment is not
   stored as a repository source; claims attributed specifically to that
   review must therefore remain traceable to its external review record.

## 1. Programme-level scientific objective

The HLS programme studies how a collective of heterogeneous, limited, and
evolvable competences can be organized and developed over time to solve
changing problems effectively and efficiently under constraints.

At programme level, the central object is therefore not a particular routing
policy, learning rule, or comparison between two policy classes. It is the
interaction between:

- problems, requests, and changing demand;
- heterogeneous and individually limited workers;
- individual and collective competence;
- organization and allocation of work;
- operational constraints and resource limits;
- experience generated through work;
- learning, transfer, and competence development;
- specialization and other forms of competence evolution;
- system-level performance over time.

Two coupled questions motivate the programme:

> Who should do what?

and

> Who should learn what, how, and from whom?

The scientific objective is not to prove that heterogeneous, specialized,
jointly managed, or learning systems are universally superior. The objective
is to determine under which conditions particular forms of heterogeneity,
organization, learning, specialization, and joint adaptation have system-level
value, and under which conditions simpler organizations are sufficient or
preferable.

Accordingly, monolithic, homogeneous, heterogeneous, static, modular,
separated, adaptive, or jointly managed solutions are all admissible outcomes
of the investigation.

## 2. Current methodological position

The programme is returning to a more foundational level after an intensive
analysis of one specific organization/development question.

**Historical terminology note:** the following decision-time discussion uses
“Beam 1” and “Beam 2” for a local organization/allocation versus
capability-development decomposition. These labels record that research
decision and its scope; they are not the current conceptual architecture or
foundational divisions of HLS. See the current [HLS philosophy](HLS_PHILOSOPHY.md)
and the compatibility note in the [unified framework](architecture/HLS_UNIFIED_FRAMEWORK.md).

### Current scientific orientation and experimental strategy

HLS is not intended to constitute a new mathematical class of systems. Beam 1
and Beam 2 are deliberately grounded in the best existing theories of
organization/allocation and competence evolution/development. Antecedents for
an HLS component are a strength, not a weakness. T0--T6, G1/G2, the HLS
Relevance Cascade, and the Minimal Reference Scenario remain foundations for
understanding structure, interactions, limits, nulls, and results; they need
not be the principal novelty.

### Decision: characterization / assembly

**SEARCH FOR A NOVEL BEAM-1 × BEAM-2 INTEGRATION MECHANISM: CLOSED.**

Successive internal reductions and audits, together with the external
placement-value audit, support a conservative conclusion: Beam 1 can use
existing organization, assignment, and flexibility theory; Beam 2 can use
existing competence-learning/evolution theory; and their intertemporal
interaction can be formulated with standard optimization, control, and
dynamic-programming machinery.  Attempts to obtain a distinct local HLS
integration mechanism have either reduced to those foundations or restored
explicit continuation/look-ahead.  No justified irreducible HLS-specific
integration mechanism has been established.

**STRUCTURE SURVIVES.  SPECIFIC HLS INTEGRATION MECHANISM NOT FOUND.**

This changes the level of the contribution, not the HLS problem.  The current
target is **CHARACTERIZATION / ASSEMBLY**: correctly assemble justified
existing pieces and characterize the conditions under which the resulting
system lies in one of these regimes:

```text
USE only is sufficient
    -> DEVELOP matters, but separated/sequential treatment is sufficient
    -> joint intertemporal USE × DEVELOP management is relevant
```

The programme asks which properties of heterogeneity, organization, demand,
learning, resources, and horizon determine those regimes.  This is not yet a
theorem, a completed characterization, or an application-first strategy.
It does not require new mathematics for every component.  The governing
discipline is: **REDUCE BEFORE INVENTING.  BUY BEFORE REBUILDING.  ASSEMBLE
BEFORE EXTENDING.**

No expansion to additional workers, tasks, uncertainty, LLMs, communication,
hierarchies, or other mechanisms is authorized at this stage; the next work
starts in the already validated minimal environment.

The file `hls_foundations_v02` is frozen for now. It is neither to be modified
nor incorporated into the paper's official state. This orientation changes the
role and priority of the pieces; it does not retrospectively invalidate prior
valid evidence or results.

### Static theoretical foundation

T0--T3 are now consolidated in the canonical
[static HLS theoretical foundation](theory/HLS_STATIC_THEORY.md): feasible
capability (T0), static collective capability expansion (T1), organizational
sufficiency (T2), and organizational realization (T3). The static block is
provisionally closed at the level needed to continue the programme. Its next
theoretical boundary is T4 --- Dynamic Capability; no dynamic mechanism is
part of T0--T3.

The [G1 static experimental ground truth](theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md)
is the validated computational support for this block. It establishes only
scoped fixed-competence Beam-1 results: heterogeneity, attainable-set
expansion, efficient frontier expansion, and organizational value are distinct;
the latter depends on `(S, P, B, Pi)`, not on `S` alone. G1 is a static
baseline, not evidence about learning, competence evolution, RQ0, or T4--T6.

### Dynamic theoretical foundation

T4--T6 are consolidated as a scoped dynamic working foundation in
[HLS Dynamic Theoretical Foundation](theory/HLS_DYNAMIC_THEORY.md): dynamic
collective capability/reachability (T4), competence-development value (T5),
and organization--development coupling (T6). The accompanying
[G2 Dynamic Ground Truth](theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md) is a minimal
analytical constructive/null reference for these distinctions.

The dynamic foundation also records the HLS Relevance Cascade as a structural
screen from action-induced state divergence through capability and value
relevance to decision relevance. Its D0/D1/D2 controls identify where that
screen stops; it is not a new dynamic-programming result.

This foundation does not claim new general control or dynamic-programming
theory, irreducibly joint management, RQ0, prevalence, robustness, empirical
relevance, or a universal dynamic HLS model. G2 is not yet an implemented
computational campaign beyond its minimal scope. Its D0/D1/D2 analytical
controls are now deterministically implemented and validated; G0 remains the
existing synthetic instrument for the separate RQ0 formalization.

The T4--T6/G2 baseline supplies a minimal analytical dynamic reference. The
broader programme-level reference problem remains subject to the explicit
operational semantics, constraints, performance choices, and scope discipline
described below.

The first documentary step is now closed: the
[HLS Minimal Reference Scenario](experimental_foundations/HLS_MINIMAL_REFERENCE_SCENARIO.md)
specifies a policy-neutral, implementable 2-worker × 2-task/competence ×
2-period adaptive scenario for later instantiation on G0.  It preserves
static, adaptive-but-fixed-competence, decision-equivalent-development, and
decision-relevant controls.  Its deterministic reference evaluator and tests
are now available without extending G0; this is not evidence of policy
superiority or a replacement for G0.

This reference problem must contain, at minimum:

- a stream or distribution of problems/requests;
- multiple workers or problem-solving units;
- heterogeneous and limited competences;
- a manager, organization, or allocation mechanism;
- explicit constraints and finite resources;
- operational outcomes;
- system-level performance measures;
- experience resulting from work;
- a mechanism by which experience or deliberate development can modify competence;
- repeated interaction over time.

The initial reference problem should be as small as possible while preserving
these semantics. Additional mechanisms such as changing demand, richer
specialization, knowledge transfer, interference, forgetting, communication,
hierarchy, referral, collaboration, or explicit development actions should be
introduced only when required to answer a previously stated HLS question.

The reference problem must be neutral with respect to architectural outcome.
It must not be constructed so that an HLS architecture wins by design.

Instead, it should permit different organizational regimes to be appropriate
under different conditions, including potentially:

- a monolithic or generalist solver;
- a homogeneous portfolio;
- a heterogeneous but static portfolio;
- an organized heterogeneous portfolio;
- an adaptive or learning portfolio;
- an organized and evolving HLS.

The intended scientific product is therefore a characterization of regimes:

```text
problem conditions
+ resource constraints
+ competence structure
+ organization
+ learning/development dynamics
+ demand dynamics
        |
        v
appropriate organizational/development regime
```

rather than a universal inequality asserting the superiority of one architecture.

## 3. Theoretical foundations for the reference problem

The reference problem should not be invented from scratch.

Its initial construction is based on four existing foundations.

### 3.1 Organization and use of limited competence

The Garicano line provides a primary theoretical reference for the operational
side of the system: heterogeneous problems, limited knowledge, specialization,
problem assignment, referral/escalation, organizational structure, capacity,
and the system-level consequences of organizing distributed knowledge.

Only constructs that survive explicit mapping to the HLS ontology should be imported.

### 3.2 Development and evolution of competence

The Gutjahr line provides a primary theoretical reference for competence
development and the allocation of development/training resources.

Again, HLS does not inherit the complete model automatically. The relevant
objects and results must be mapped explicitly to the HLS ontology and adapted
where the HLS problem requires properties absent from the source theory.

### 3.3 HLS ontology and philosophy

[HLS_PHILOSOPHY.md](HLS_PHILOSOPHY.md) defines the programme-level scientific direction.

[hls_ontology.md](hls_ontology.md) defines the semantic contract used to
distinguish, among other concepts:

- competence from performance;
- experience from competence change;
- individual competence from collective competence;
- work allocation from development allocation;
- organization from learning;
- operational outcome from long-term system value.

These distinctions must be preserved in the reference problem.

### 3.4 Existing HLS routing/development theory

The existing RQ0 work provides a developed theory for one specific interaction:
when operational routing influences future learning/development opportunities,
and when managing routing and development separately can or cannot reproduce
the value of joint decision making.

This theory is retained as an HLS theoretical asset. It does not define HLS as
a whole and must not dictate the construction of the general reference problem.

## 4. Performance and constraints are an open foundational requirement

The programme does not yet have a sufficiently complete operational definition
of HLS system performance for the new reference problem.

This is now an explicit foundational gap.

A useful HLS evaluation must distinguish at least:

```text
competence / capability
        !=
realized operational performance
        !=
resources consumed to obtain that performance.
```

Potential performance dimensions include, depending on the reference problem:

- quality or success of problem resolution;
- coverage of the problem/request distribution;
- throughput or served demand;
- latency or resolution time;
- unresolved or failed problems;
- computational or other resource consumption;
- capacity utilization;
- learning/development cost;
- robustness;
- adaptation to changing demand;
- long-term accumulated system value.

These are not yet declared to be the definitive HLS metrics.

The reference problem must determine which quantities are scientifically
necessary and how they should be combined or kept separate.

In particular, comparisons between architectures must be made under explicit
and scientifically fair resource constraints. A heterogeneous portfolio must
not obtain an apparent advantage merely because it receives more effective
resources than the architecture against which it is compared.

A scalar long-term objective `J` may subsequently be defined for particular
questions, but the programme should not prematurely collapse all system
performance into a single quantity before the relevant performance dimensions
and constraints are understood.

## 5. RQ0 and its current role

RQ0 remains an active research question:

> Can the dynamic allocation and development of competences in a heterogeneous
> learning system improve long-term system performance compared with
> architectures that manage task allocation and knowledge transfer separately?

At programme level, RQ0 asks when the interaction between the organization/use
of current competences and the development/evolution of future competences has
system-level value, and when the two can instead be managed separately or
through sufficient coordination.

The work completed so far studies a narrower routing/development instantiation
of this question.

RQ0 is therefore an important subproblem of HLS, but the HLS programme must not
be reduced to proving `J_HLS > J_SEP`.

Nor should the existing strong-SEP comparison be treated as a universal
definition of the value of HLS.

The current exact theory instead establishes conditions and counterconditions
for one particular form of organization/development coupling.

## 6. What is established for the current RQ0 formalization

### 6.1 Programme and policy classes

Under common world physics and information, strong SEP is a restricted policy
class of HLS policies. Therefore

```text
Pi_SEP subseteq Pi_HLS
J_SEP,max <= J_HLS.
```

This inequality alone is not a substantive HLS result; it follows from policy
class inclusion.

In the finite exact setting, strict value relative to strong SEP occurs iff no
HLS-optimal policy is strong-SEP-admissible on its positive-probability support.

A local non-greedy Bellman action alone is insufficient.

The local identity

```text
Q(b)-Q(g) = -DeltaR + DeltaP D*
```

is exact under its stated one-step factorization, but is a local Bellman
advantage identity and not a global integration criterion.

The formal source is
[RQ0 routing integration boundaries](theory/rq0_routing_integration_boundaries.md).

### 6.2 Existing synthetic framework

The existing synthetic G0 framework was constructed to investigate the current
RQ0 routing/development formalization.

It should therefore be interpreted as the existing **RQ0 synthetic framework**,
not as the final minimal reference model of the complete HLS programme.

Within its intended scope:

- G0 passed its architecture and A1 compatibility gates.
- A1 is closed/pass: A1a exact worlds, A1b 1,020 preregistered boundary
  configurations, and A1c 458 competence-geometry configurations.
- C1--C5 are implemented and passed their reference gates on the common,
  policy-neutral G0 framework.
- C6--C8 are not implemented.
- The framework remains a valid instrument for testing RQ0 mechanisms and boundaries.
- It is not itself evidence that HLS architectures are generally superior.

The current framework contract is in [G0](experiments/G0.md); the exact A1
reference specification and compatibility record remain in the frozen
[synthetic environment record](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md).

The existing G0 must not be retrospectively redefined to serve the new
programme-level reference problem. Scientific provenance and frozen results
must be preserved.

## 7. Exact and synthetic RQ0 results

- A1 World E and C1 R5 are constructive, exact existence cases relative to
  strong SEP. They do not establish prevalence or superiority over SEP-Omega.
- The original eta=.5 diagnostic found physically reachable local routing
  inversions that were off every HLS-optimal root continuation. Constrained
  reachability and demand-persistence audits therefore established a local
  mechanism without a global root-value result in that family.
- The frozen routing-to-opportunity lambda family was SEP-reducible at all 21
  points. Persistence strengthened local incentives in its tested worlds but
  did not remove the observed global barrier.
- The frozen zero-sum competence redistribution family

  ```text
  C(alpha)=((4/5,4/5-alpha/5),(3/5,3/5+alpha/5))
  ```

  gives the exact model-scoped result

  ```text
  Phi(alpha) = 0                         for 0 <= alpha <= 5/16
               3 alpha/10 - 3/32         for 5/16 < alpha < 1/2
               0                         for 1/2 <= alpha <= 1.
  ```

  Thus it establishes existence of strict integration relative to strong SEP
  on the open interval `5/16 < alpha < 1/2`.

- `alpha=5/16` is a Bellman inversion boundary.
- `alpha=1/2` is a greedy-admissibility boundary: the required action enters
  the SEP greedy set.
- These boundaries are properties of this family, not universal HLS boundaries.
- SEP-Omega equals HLS in the audited A1, A1b, A1c, lambda, and geometry
  families within the declared tolerance.

This establishes that sufficient continuation information can remove the value
gap in the tested worlds. SEP-Omega is therefore a coordination/reducibility
boundary for this formalization, not an independent algorithmic benchmark and
not evidence against the broader HLS programme.

## 8. What is not established

The repository does not establish:

- universal superiority of heterogeneous systems over monolithic systems;
- universal superiority of specialization over generalism;
- universal superiority of adaptive organization over static organization;
- universal superiority of joint organization/development over separated architectures;
- prevalence, genericity, robustness, or empirical realism of the current
  synthetic integration window;
- that complementarity, specialization, persistence, or stronger coupling is
  sufficient for strict integration;
- that the C(alpha) interval transfers to all G0+C1--C5 worlds or to real systems;
- that HLS intrinsically outperforms every sufficiently coordinated modular architecture;
- that the existing RQ0 synthetic environment constitutes a complete HLS reference problem.

The PACS and Office-Home records are scoped vehicle and mechanism evidence,
with negative/inconclusive outcomes where stated. They are not general
validation of HLS or RQ0.

## 9. Current structural understanding of RQ0

Within the current finite exact routing/development formalization, the analysis
distinguishes three levels:

1. **physical/local non-separability**: a state admits a Bellman-optimal
   non-greedy action;
2. **on-policy non-separability**: an HLS-optimal policy uses such an action on
   its own positive-probability support;
3. **irreducible integration relative to strong SEP**: every HLS-optimal policy
   requires such a violation of the strong-SEP restriction.

Only the third level implies `J_HLS > J_SEP,max` in the finite exact setting.

SEP-Omega demonstrates that the positive result is about the strong-SEP
contract, especially its routing objective and continuation information, not
about centralization versus modular software as such.

These distinctions remain valid theoretical results for their declared scope.
They are not definitions of HLS itself and need not constitute the appropriate
formalism for other HLS organization/development mechanisms.

## 10. Current foundational gaps

Before extending the experimental programme beyond the T4--T6/G2 analytical
baseline, the following programme-level objects require explicit definition or
consolidation.

### 10.1 Minimal HLS reference problem

The minimal reference scenario is now documented in
[HLS Minimal Reference Scenario](experimental_foundations/HLS_MINIMAL_REFERENCE_SCENARIO.md)
without embedding the desired answer in its physics.  It is a 2×2×2 adaptive
reference for later G0 implementation, not a complete universal reference
problem.  T4--T6/G2 remain its initial analytical dynamic baseline.

### 10.2 Workers

The minimum state and limitations of a worker must be defined, including how
competence relates to its ability to solve different problem types.

### 10.3 Problems and demand

The semantics of a problem/request and its distribution must be explicit.

The minimal world may initially use stationary demand. Changing demand should
be introduced when the corresponding HLS question requires it.

### 10.4 Manager and organization

The authority, information, actions, and limitations of the organizing
mechanism must be explicit.

Organization must not be identified automatically with routing.

### 10.5 Constraints

Finite resources and other relevant limits must make organizational decisions
meaningful and comparisons fair.

### 10.6 Performance

Operational and long-term system performance measures must be defined before
claims of architectural superiority can be made.

### 10.7 Experience and competence evolution

The reference problem must distinguish work from experience and experience
from actual competence change.

G2 provides deterministic action-dependent learning by doing as the minimal
constructive realization. Richer mechanisms should not be added without a
scientific reason.

### 10.8 Collective competence and complementarity

The programme requires operational definitions that allow collective
competence and useful complementarity to be measured without assuming that
heterogeneity or diversity is intrinsically beneficial.

## 11. Methodological reset: from RQ0-specific worlds to an HLS reference system

The programme will not proceed by progressively enriching the existing RQ0
synthetic world merely to obtain broader positive HLS results.

The T4--T6/G2 analytical baseline now supplies the minimum dynamic structure
for a neutral, scientifically controlled HLS reference problem. Its use or
extension must preserve the following discipline.

The construction should proceed from established theoretical components where
they genuinely match the HLS ontology, particularly the organization/use and
development/evolution foundations, and should introduce new HLS-specific
machinery only where those foundations leave a demonstrated gap.

The methodological sequence is:

```text
HLS philosophy
      |
      v
ontology
      |
      v
existing theoretical foundations
      |
      v
identify missing HLS primitives
      |
      v
minimal HLS reference problem
      |
      v
constraints + performance measures
      |
      v
theoretical analysis
      |
      v
controlled experimental validation
      |
      v
release one additional property when scientifically required
```

Each new property or mechanism must answer a previously formulated scientific
question.

Realism by itself is not a reason to enlarge the model.

Likewise, a mechanism must not be introduced merely because it makes a
positive HLS result easier to obtain.

Positive, negative, and equality regimes are all scientifically admissible.

## 12. Intended theoretical programme

The longer-term objective is to characterize relationships of the form

```text
problem structure
x demand structure
x individual limitations
x competence geometry
x resource constraints
x organizational possibilities
x learning/development dynamics
            |
            v
system performance and appropriate organizational regime.
```

This may reveal regimes in which:

- a monolithic/generalist solution is sufficient;
- homogeneous replication is appropriate;
- static heterogeneity is useful;
- dynamic organization adds value;
- specialization emerges or is deliberately useful;
- competence development adds value;
- organization and development can be separated without loss;
- organization and development require coordination;
- genuinely joint adaptation has strict value.

The purpose is to characterize these regimes and their boundaries, not to
assume their ordering in advance.

The existing RQ0 theory becomes one component of this broader programme:
it characterizes one possible boundary between separated and jointly managed
organization/development.

## 13. Current implementation boundary

**Historical scope note (13 October 2026; priority superseded 15 October
2026):** this section records the separate programme-level
minimal-reference-system track as it stood then. It is not a status inventory
of all later campaign-specific laboratories. Campaign 2/3 finite-problem
experiments and Campaign 4 preparation did not, by themselves, close the
general HLS reference-system requirements. The active operational response is
now the approved HLS-LAB-V1-INTEGRATED milestone above; this does not
retroactively change the historical scope or evidence below.

The next work is **not** another parameter sweep or an extension of the
existing RQ0 synthetic campaign.  The minimum reference scenario has been
documented and has a deterministic reference evaluator.  Its closed
[information audit](experimental_foundations/HLS_MINIMAL_REFERENCE_INFORMATION_AUDIT.md)
retains a model-scoped exact reconstruction
`G=max(h,v)-max(h+u,0)` and, for `L>0,beta>0`, the decision compression
`m=min(v,v-u-h)`.  The latter matches the oracle on the declared Phase-V
formal domain but has a documented direct-double numerical robustness limit
under continuous extreme/saturation attacks.  The methodological result is to
seek compact estimates of organizational value from action-induced competence
development, not to claim general scalar sufficiency.  No broader G0
integration or experimental campaign has begun.

The [G3 organizational-value ground truth](experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md)
is implemented as a fixed 3×2 direct-assignment evaluator with independently
implemented algebraic identities. Its conceptual, algebraic, documentation,
implementation, and finite adversarial validation phases are closed with a
strong reduction to standard assignment sensitivities. The finite audit found
that the full documented sensitivities reconstruct `D` exactly, while poorer
signals can preserve action ranking only on its tested grid; it establishes no
general minimality claim. G3 is an exact analytical reference for
organizational value of development, not new HLS or assignment theory.
The closed G3-H entry in that canonical source changes only the fixed learning scale to
worker-specific `eta_i` and shows that a local organization-development
ranking can reverse when a further G3 organization-development opportunity is
included; it is standard deterministic DP, not irreducibility, new dynamic
theory, or an HLS-architecture claim. Its post-closure C1 audit falsifies the
specified development-only future-opportunity scalar: it omits future operational reward
and retains the wrong ranking in the closed counterexample. Its C2 audit
reduces the joint future opportunity to standard finite-horizon
look-ahead/DP (exactly the documented look-ahead at `beta=1`). Accordingly,
G3-H supplies no evidence for an exact intermediate representation between
local `M=R+beta D` and explicit future joint-opportunity evaluation. It is
closed as the analytical microscope for this question.

T4--T6 and G2 establish an analytical baseline with deterministic D0/D1/D2
computational validation.  Any implementation must preserve the declared
reference-scenario scope and determine:

1. which primitives can be imported from the Garicano organizational model;
2. which primitives can be imported from the Gutjahr competence-development model;
3. how those primitives map to the HLS ontology;
4. which HLS primitives remain missing after that mapping;
5. the minimum worker model;
6. the minimum problem/request model;
7. the minimum manager/organization model;
8. the minimum constraints required to make organization meaningful;
9. the minimum experience and competence-evolution dynamics;
10. the performance quantities required for fair comparison;
11. the negative/control regimes in which complex HLS organization should
    provide no advantage;
12. the first non-trivial theoretical questions that the resulting reference
    problem can answer.

The general reference environment described by this checklist remains an
open foundational object; the later finite-problem campaign laboratory is a
distinct scoped instrument and must not be silently equated with it.

## 14. Current research position

At programme level HLS remains in **foundational consolidation and
characterization / assembly**: T0--T3 and the scoped T4--T6/G2 analytical
baseline are in place, while broader reference-problem operationalization and
validation beyond D0/D1/D2 remain open. In parallel, the later Campaign 2 and
Campaign 3 finite-problem studies have completed their explicitly frozen
scopes; they are not evidence that the broader foundational object is closed.
For the current empirical findings and C4 stop status, the dated status block
at the beginning of this file and its linked primary reports take precedence
over the historical sequencing language below.

The previous RQ0 phase has established a useful exact result:

```text
strict integration relative to strong SEP:
EXISTS in the declared exact model.
```

For that formalization:

```text
existence:                   YES
structural characterization: PARTIAL / IN PROGRESS
robustness/prevalence:       NOT ESTABLISHED
empirical relevance:         NOT ESTABLISHED
```

Those results are retained.

The following records the priority as stated in the 13 October 2026 status
snapshot; it is **historical and superseded as the immediate operational
priority** by the 15 October approval to complete HLS Laboratory v1. Its
scientific motivation remains relevant, but implementation now follows the
bounded B1–B6 scope in [the v1 reference](experiments/HLS_LAB_V1.md).

The then-outstanding direction was to operationalize and validate the
documented minimal HLS reference scenario with explicit organization,
limitations, constraints, performance, experience, learning, and competence
evolution, grounded in the T0--T6 baseline, existing theory, and the HLS
ontology. That dated text was not authorization for an experiment.

This is not a rejection of RQ0 or of the existing synthetic work. It is a
change in scientific hierarchy:

```text
HLS programme
    |
    +-- minimal HLS reference problem
    |       |
    |       +-- organization/use of competence
    |       +-- development/evolution of competence
    |       +-- performance under constraints
    |       +-- interaction between organization and development
    |
    +-- RQ0 and its specific formalizations
            |
            +-- current routing/development model
            +-- strong SEP
            +-- SEP-Omega
            +-- exact integration results
```

The reference problem should ultimately provide the common laboratory in which
RQ0 and other HLS questions can be investigated without allowing any one of
them to define HLS itself.

## 15. Evidence pointers

### Programme level

- Philosophy: [HLS_PHILOSOPHY.md](HLS_PHILOSOPHY.md)
- Semantics: [hls_ontology.md](hls_ontology.md)
- Research questions: [research_questions.md](research_questions.md)
- Method: [RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md)
- Static foundation: [HLS_STATIC_THEORY.md](theory/HLS_STATIC_THEORY.md)
- Dynamic foundation: [HLS_DYNAMIC_THEORY.md](theory/HLS_DYNAMIC_THEORY.md)
- Dynamic ground truth: [HLS_G2_DYNAMIC_GROUND_TRUTH.md](theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md)
- G2 implementation and results: [experiments/synthetic/g2](../experiments/synthetic/g2/) and [results/foundations/g2_dynamic](../results/foundations/g2_dynamic/)

### Current RQ0 theory and evidence

- Formal theory:
  [rq0_routing_integration_boundaries.md](theory/rq0_routing_integration_boundaries.md)
- Existing RQ0 synthetic contract:
  [G0.md](experiments/G0.md)
- A1/C1--C5 gates:
  [HLS_SYNTHETIC_ENVIRONMENT.md](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md)
- Campaign chronology:
  [RQ0_EXPERIMENTAL_CAMPAIGN.md](experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md)
- Geometry protocol/outcome:
  [RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md](experimental_foundations/RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md)
- Coupling protocol/outcome:
  [RQ0_ROUTING_OPPORTUNITY_COUPLING_PROTOCOL.md](experimental_foundations/RQ0_ROUTING_OPPORTUNITY_COUPLING_PROTOCOL.md)
- Executable synthetic gates:
  [experiments/synthetic](../experiments/synthetic/)

### Experimental-validity diagnostics — 16 October 2026

Recorded at **2026-10-16 10:15 +02:00** (Europe/Madrid). A predeclared,
deterministic instrument suite passed eight checks covering equivalence,
competence response, the enumerated 1.15 feasibility frontier, assignment
sensitivity, isolated MIS-v2, resource accounting, zero teaching efficacy,
and matched P0/P1/P2 inputs. Focused integrated/environment/plausibility
tests passed (26). Results and hashes are in
[the validity assessment](experiments/HLS_LABORATORY_VALIDITY_ASSESSMENT.md)
and `results/diagnostics/hls_laboratory_validity_assessment/`.

This verifies internal behaviors only. P0/P1/P2 remain bundled strategy
comparisons; CES is gross, costs are separate, and equal budgets do not ensure
equal use. The laboratory still lacks an agreed comparison estimand and
external calibration for broad architecture or policy superiority claims.
No campaign was run; the integrated laboratory remains **PARTIAL** and new
scientific campaigns remain on hold pending the outcome-contract decision.

### First scientific campaign design — 16 October 2026

Recorded at **2026-10-16 10:29 +02:00** (Europe/Madrid). The proposed first
scientific question is the interaction between matched aggregate competence
distribution and temporal demand structure, with the existing P0 policy held
fixed and MIS-v2 as a matched ON/OFF mechanism block. The design reuses the
three-agent/two-skill model, C5 IID/Markov demand and frontier-enumerated
scenarios; no simulator changes or campaign execution are authorized. The
proposal is **GO for preflight/registration, HOLD for execution** pending
preflight, an approved minimum meaningful CES effect (or estimation-only
decision), and a novelty check. See
[HLS first scientific campaign design](experiments/HLS_FIRST_SCIENTIFIC_CAMPAIGN_DESIGN.md).

### Q1 campaign preflight — 16 October 2026

Recorded at **2026-10-16 10:45 +02:00** (Europe/Madrid). The registered
architecture match, C5 IID/Markov process, frontier controls, outcome/resource
instrumentation, MIS-v2 toggles and reproducibility checks passed. However,
the preregistered primary estimand (architecture effect under Markov minus
architecture effect under IID, near-boundary, MIS OFF) was structurally
insensitive to temporal persistence: the matched architecture effect was
`+2.4` cumulative gross CES in every diagnostic path, and the one-period
effect was `+.1` for each of the three task types. With common stationary task
marginals and no material state transition in that block, the expected
moderation is zero. Therefore the 960-run campaign is **NO-GO as registered**;
the registered MIS-ON secondary is not promoted after observing results. No
main campaign was run. The diagnostic runner, preregistration hashes and
machine-readable evidence are in
[HLS Q1 preflight](experiments/HLS_Q1_PREFLIGHT.md) and
`results/diagnostics/hls_q1_preflight/`. The laboratory remains **PARTIAL**;
the 13 known repository integrity/provenance failures were not rerun or
modified. Chronology: [HISTORY.md](HISTORY.md).

### Q1-R analytical verification — 16 October 2026

Recorded at **2026-10-16 11:05:36 +02:00** (Europe/Madrid). An exact
two-period enumeration through the current P0/MIS-v2 integrated runner
established a conditional stationary-marginal result: with fixed competence,
memoryless task-specific decisions, per-period reset resources, and stationary
initialization, IID and Markov demand have equal expected cumulative CES, so
the architecture × persistence interaction is zero. A minimal current-HLS
construction with the registered matched competence matrices, two equally
likely skill-specific demands, budget 2, cap 1, and η=.10 gives
Θ(MIS OFF)=0 and Θ(MIS ON)=−.003 CES over two periods. The negative
interaction arises because persistent repetition reuses an already exposed
skill with architecture-dependent remaining MIS headroom; it is a model-bound
existence result, not evidence of general advantage. The registered Q1
24-period MIS-OFF primary remains structurally null and **NO-GO as registered**;
campaign design/execution remain on HOLD. Details and exact reproducible
checks: [Q1-R analytical verification](theory/HLS_Q1R_ANALYTICAL_VERIFICATION.md)
and `tests/test_hls_q1r_analytical.py`. HLS Laboratory remains **PARTIAL**.

### Research laboratory framework — 16 October 2026

Recorded at **2026-10-16 11:15:38 +02:00** (Europe/Madrid). The new
[HLS Laboratory Research Framework](HLS_LABORATORY_RESEARCH_FRAMEWORK.md)
consolidates five separable components—organization, decision policies,
learning mechanisms, exogenous environment, and evaluation—and maps them to
the executable code and bounded campaign evidence. Current experimental
support is strongest for paired exogenous paths, deterministic mechanism
controls and the fixed 3-agent × 2-skill model; architecture/policy/mechanism
comparisons remain partial where their factors are bundled or interfaces are
hard-coded. The primary structural ceiling is fixed agent/skill/action
geometry; concurrent-task coordination and latent-demand inference are not
implemented. The proposed first implementation, subject to separate
authorization, is bounded n-agent/k-skill state/action generalization with
an exact 3×2 compatibility gate. No code or scientific campaign was run for
this framework. Historical registrations and results remain unchanged; the
laboratory remains **PARTIAL**.

### Phase 5A scientific model dossier — 16 October 2026

Recorded at **2026-10-16 20:59 +02:00** (Europe/Madrid), against audited
source commit `e8e115030e064df23f07f1b5824264f97513099a`. The
[scientific model dossier](engineering/HLS_SCIENTIFIC_MODEL_DOSSIER.md)
extracts production/CES, MIS-v2, teaching, policy, observation/estimation,
resource and demand equations; maps constructs and mathematical properties;
and links historical G1/G2/MIS/G3-H/RQ0 and Campaign 1–2 evidence. A four-period
diagnostic reference trace (script and JSON) was replayed exactly and exercises
production, MIS-v2, P2-directed teaching, imperfect observations, competence
posterior updates, efficacy memory and resource accounting. This validates
trace reproducibility, not empirical validity. The dossier records an
unresolved equation-lineage distinction: the G3/MIS reference's
`s + eta*(1-s)^2` law is not identical to current DISCOVER-v2 MIS-v2 at unit
effort, `s + eta*(1-s)`. It also identifies that the 11:14 research framework
describes the pre-Phase-1 fixed 3×2 implementation; later N×K addenda and
current code supersede that dated capability map. No scientific source,
historical artifact, or expected hash was changed. Focused HLS/Phase 1–5
checks: 161 passed. Final full suite on the current worktree: 1,397 passed,
5 failed in 634.58s; the five failures are the same known provenance/integrity
checks (foundation result inventory, Campaign 2 closure/source digests, and
Campaign 3 / strategy-gate frozen source digests). No failure implicates the
scientific mechanisms audited here. HLS Laboratory remains **PARTIAL**.

### G3 / MIS-v2 learning-law reconciliation — 16 October 2026

Recorded at **2026-10-16 21:09 +02:00** (Europe/Madrid). The former open
lineage question in the Phase 5A dossier is resolved: the historical quadratic
law `min(1, c + α·e·(1−c)²)` and exponential MIS-v2 law
`1 − (1−c)(1−η)^e` are distinct models, with no fixed parameter conversion
valid across states and effort. MIS-v2 remains the N×K laboratory reference;
the quadratic formulation remains in the original MIS scenario,
DISCOVER-v0, G3 and G3-H. The dossier now specifies that every experimental
configuration identify the law, equation, exposure convention and parameters.
This addendum clarifies the 20:59 Phase 5A record without rewriting it or the
historical G3 ground truth. No code, equation, parameter or result changed;
HLS Laboratory remains **PARTIAL**.
