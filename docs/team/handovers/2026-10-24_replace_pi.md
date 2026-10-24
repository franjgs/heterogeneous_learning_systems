# HLS Role Handover — Principal Investigator — REPLACE

**Baseline:** `bab29af7665c4185bb84babb1bc70209d0fabffb`  
**Branch:** `feature/hls-laboratory-v1` (same commit as local and remote `main`)  
**Date:** `2026-10-24`  
**Status:** `PENDING_ACCEPTANCE`

> **Governance boundary:** this package follows the repository's
> [generic handover template](../HANDOVER_TEMPLATE.md) and source-authority
> rules. The [canonical team protocol](../HLS_TEAM_HANDOVER_PROTOCOL.md)
> defines replacement of experts and the Chief Engineer, but does not define
> a PI-replacement operation, acceptance procedure, or PI successor status
> transition. The role register does not identify either PI by name. This is a
> source-grounded outgoing briefing prepared for continuity; it does not
> complete a formal role transfer or change anyone's authority.

## ROLE

Outgoing role: **Principal Investigator — outgoing**, identity not materialized
in repository sources. Incoming role: **Principal Investigator — successor**,
identity not supplied or materialized. The initiating instruction explicitly
orders a PI handover, but the current register records only
`PI | ACTIVE | UNKNOWN / TO BE INITIALIZED`.

The current [role register](../HLS_ROLE_REGISTER.md) remains unchanged.
Incoming acceptance and a PI-specific governance disposition have not been
received.

## MISSION

Transfer HLS's scientific identity, evidence, decisions, limitations, active
formal questions, team responsibilities, and repository state so the incoming
PI can independently continue the programme without relying on prior chats.

This briefing is not a new scientific decision, an experiment authorization,
or a substitute for the incoming PI's independent review.

## AUTHORITY / SCOPE

**Outgoing PI direction recorded for this handover:** maintain HLS as a general,
interdisciplinary scientific programme; pursue defensible original and
publishable contributions; do not define HLS by USE/DEVELOP, a method, agent
architecture, experiment, or laboratory; do not continue a line merely because
its implementation exists; preserve negative results; and do not authorize a
new campaign through this briefing.

**Incoming PI authority:** ultimate scientific and strategic authority belongs
to the PI under the [team protocol](../HLS_TEAM_HANDOVER_PROTOCOL.md). It
transfers only through a PI-replacement procedure accepted by the successor;
the repository currently lacks that procedure and the successor's identity.

**May decide within this package:** factual source mapping, status labels, and
WIP classification supported by the current repository.

**Must escalate:** any change to scientific doctrine, the official research
question, frozen results, experiment authorization, role activation, or the
missing PI-replacement governance process.

**Must not decide:** infer the incoming PI's identity, update the role register
as if the transfer were accepted, convert a proposal into an approved
direction, or promote a scoped result to a general HLS principle.

## PROJECT QUESTION

HLS is a general scientific framework for studying, designing, and evaluating
the organization, utilization, combination, and evolution of heterogeneous
capabilities. Its aims include understanding the determinants of individual
and collective performance, identifying principles that generalize within
stated classes and assumptions, developing effective solutions, integrating
knowledge across disciplines, and accumulating coherent scientific
knowledge. Generalizable does not mean universal.

Its conceptual and experimental architecture has four levels:

1. **Scenarios** — systems, capabilities, tasks, demand, conditions,
   constraints, information, uncertainty, and applicable dynamics.
2. **Organizational schemes** — how capabilities and responsibilities are
   organized and used.
3. **Models** — mathematical models, algorithms, mechanisms, policies,
   estimators, optimizers, and integrations of components.
4. **Performance measures** — problem-relevant evaluation of effectiveness,
   quality, efficiency, cost, robustness, adaptability, and other outcomes.

These are conceptual responsibilities, not necessarily software modules or a
rigid pipeline. HLS-PEF is an instrument within performance evaluation.
The three-part mathematical formulation in the
[unified framework](../../architecture/HLS_UNIFIED_FRAMEWORK.md)—system model,
problem/organizational modality, and decision architecture—is compatible with,
but does not replace, the four-level architecture.

**USE/DEVELOP is not foundational.** It is one possible analytical
decomposition. HLS may study static or dynamic capabilities, demand, and
organizations, with or without learning. The original
[HLS philosophy](../../HLS_PHILOSOPHY.md) is the current authority for this
identity.

## PI DOCTRINE

The governing method is **REDUCE BEFORE INVENTING. BUY BEFORE REBUILDING.
ASSEMBLE BEFORE EXTENDING**. Reuse published theories and mechanisms when
their assumptions fit; integration can contribute scientifically, but
combining known components alone does not establish originality. Contributions
must be compared with the state of the art and supported by evidence.

Other standing claim rules in the [Research Doctrine](../../../RESEARCH_DOCTRINE.md):
start from the scientific need rather than a mechanism; distinguish world,
policy, information, and evaluation; preserve source-specific semantics; use
fair competitive baselines; state scope and limits; preserve null and negative
results; do not equate implementation validation with scientific validity.

## CANONICAL BASELINE

**HEAD / branch:** `bab29af7665c4185bb84babb1bc70209d0fabffb` on
`feature/hls-laboratory-v1`. At handover preparation, local `main`,
`origin/main`, and `origin/feature/hls-laboratory-v1` were also at this
commit. It is the published commit `docs(hls): establish four-level scientific
philosophy`.

**Worktree:** `git status --short --untracked-files=all` is clean. No tracked
or untracked WIP was present. The ignored working tree contains local caches
(`.pytest_cache`, `.ruff_cache`, Python `__pycache__`) and local reference
PDFs under `docs/literature/`; they were not staged or changed. The
`HLS_CURRENT_STATE.md` records that some raw experiment traces (including a
318 MB compressed S3b trace) are excluded by repository policy; consult that
record before attempting to reproduce from raw data. A read-only process-list
check found no active HLS/experiment/campaign run (only the inspection
command itself).

**Sources consulted:** [HLS Philosophy](../../HLS_PHILOSOPHY.md), root
[Research Doctrine](../../../RESEARCH_DOCTRINE.md),
[HLS ontology](../../hls_ontology.md),
[Research Questions](../../research_questions.md),
[HLS Current State](../../HLS_CURRENT_STATE.md),
[Repository Guide](../../REPOSITORY_GUIDE.md),
[HLS Unified Framework](../../architecture/HLS_UNIFIED_FRAMEWORK.md),
[HLS ontology v0.1](../../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md),
[HLS Theory Registry](../../theory/README.md),
[HLS cumulative execution plan](../../engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md),
[HLS Laboratory Roadmap](../../engineering/HLS_LAB_ROADMAP_CURRENT.md),
[Team Handover Protocol](../HLS_TEAM_HANDOVER_PROTOCOL.md),
[Handover template](../HANDOVER_TEMPLATE.md),
[Role Register](../HLS_ROLE_REGISTER.md), and the scientific reports linked
from Current State.

**WIP classification:** committed documentation at the stated HEAD is the
audited baseline. No tracked/untracked WIP exists. Ignored caches and local
literature PDFs are outside the commit; ignored result traces remain governed
by the artifact/integrity notes in Current State and experiment reports, not
by this briefing.

**Known contradictions / gaps:**

- The team protocol has no PI-replacement operation, while this instruction
  requests one. It also has no PI-specific successor acceptance or authority
  transfer sequence.
- Outgoing and incoming PI identities are absent from the role register and
  the incoming identity is absent from the instruction. The protocol prohibits
  inferring a role identity or changing status before the required acceptance.
- The [role register](../HLS_ROLE_REGISTER.md) still records the outgoing CE
  as `OUTGOING` and the incoming CE as `PENDING` from 2026-10-19. Its CE
  baseline is `e6ad5a80…`, older than this package's repository baseline.
  No CE acceptance report or subsequent PI disposition is recorded in the
  register.
- The [Research Questions](../../research_questions.md) document still calls
  organization/use and development/evolution “two foundational beams” and
  says RQ0 arises from them. That terminology conflicts with the revised
  philosophy. RQ0 can remain a specific formal research question, but should
  not define HLS or imply that USE/DEVELOP is foundational.
- Older sections of Current State, History, theory records, and experiment
  documents retain Beam 1/Beam 2 language. Where explicitly historical or
  model-scoped, preserve it; update a canonical current authority only through
  an approved, traceable correction.
- Current State marks RQ0 **OPEN** and reports the 2026-10-23 USE/DEVELOP
  originality assessment as **NO-GO for an immediate standalone publication**.
  It identifies S3b-E1 as an originality-positioning alternative while also
  stating that S3b-E1 is closed and no campaign is authorized. The incoming PI
  should distinguish the open formal question from an approved next campaign.
- The current Current State snapshot is dated 2026-10-23; this package records
  the repository and outgoing handover instruction on 2026-10-24.

## ESTABLISHED RESULTS

The authoritative synthesis is [HLS Current State](../../HLS_CURRENT_STATE.md);
the entries below summarize scoped results, not universal laws.

### Formal and scenario evidence

- **S1 — static assignment:** the exact finite assignment value is 2.60 versus
  greedy 1.80, checked against enumeration. It is a bounded solver/reference
  result.
- **S2a — varying demand with period separability:** exact and global
  enumeration give 8.00 versus greedy 7.20 over 84,388 sequences. This shows
  separability under the instance's assumptions; changing demand alone does
  not require a temporal planner.
- **S2b — shared intertemporal budget:** with binding budget, Bellman gives
  1.00 versus myopic 0.90; with sufficient budget both give 1.90. A
  constructive finite example, not a general planning advantage.
- **S3a — observed exogenous competence change:** reactive exact assignment
  captures the current optimum for the declared mapping; the tested selector
  learning did not add value in the zero-noise case. Results are specific to
  the configured trajectories and observation process.
- **S3b — unknown, changing rewards and partial feedback:** the 240-run
  UCB1/SW-UCB factorial favored UCB1 in regret in all four tested cells while
  SW-UCB had lower global competence MSE. The algorithms differ beyond
  memory, so this does not isolate memory.
- **S3b-E1 — memory diagnostic:** FULL and WINDOW shared-observation controls
  use the same estimation/decision rules and differ in retained history.
  With infrequent changes/high feedback, WINDOW reduced regret by 74.59
  (paired 95% CI [−89.60, −59.58]); other shared-observation cells were null
  or nonconclusive. Under closed-loop observation, WINDOW mean regret was
  lower in three conditions but all paired intervals included zero. The
  diagnostic is closed, not a general result about memory.
- **S4 — endogenous MIS-v2 learning and transfer:** exact finite references
  expose planning/tie-break sensitivity and no transfer gain in tested
  parameter/frontier settings. For the audited T=3 `x,y,y` case, both
  Bellman policies have reward 1.9175000000000004, functional compliance
  1/3, deficit 0.5325, productive effort 6, teaching effort 0. This
  integration does not validate P0/P1/P2 or demonstrate effective transfer.
- **S7 — uncertain demand and planning:** the central T=4 CES is
  3.1628653621 without transfer and 3.1743777327 with transfer, versus
  3.0346209871 for original myopic. BEST-MYOPIC is 3.0444737839; its gap to
  Bellman is 0.1183915782. CURRENT-DEMAND-MYOPIC matched Bellman CES in the
  central instance. CES can improve while service worsens; no general planner
  or transfer claim follows.
- **T0–T6/G1–G3 and RQ0 formalization:** static and dynamic theory documents
  contain scoped capability, sufficiency, realization, reachability,
  development-value, and coupling results. Under the declared finite
  formalization, `Pi_SEP ⊆ Pi_HLS`; that value inequality is trivial by class
  inclusion. Strictness against strong SEP occurs iff no HLS-optimal policy
  is strong-SEP admissible on its positive-probability support. The exact
  `C(alpha)` family has a strict interval `5/16 < alpha < 1/2`; these are
  model-family results. C1's `max D` shortcut was falsified; C2's correction
  reduces to look-ahead/dynamic programming. G0-C6 is closed STOP.

### Campaign and applied-model evidence

- **Campaign 2:** preregistered findings are conditional on the sampled
  synthetic population. Q01 realized utility was not established (mean
  0.0015, 95% CI [−0.0194, 0.0193]); reported coupling was rare (71/15,360,
  about 0.46%). Do not conclude universal Q11 superiority or that development
  is useless.
- **Campaign 3 / META-VOC:** the confirmatory equal-domain contrast was
  +0.1167 cumulative `mu_true` per history (95% CI [0.0310, 0.2013]) and
  decision-computation difference −0.1924 s (95% CI [−0.3539, −0.0228]).
  Invocation counts were not exactly equal; predictor discrimination was
  weak (AUC 0.624; deep-fast contrast +0.0104, CI [−0.020, 0.0431]). This
  does not establish a reliable real-world opportunity detector.
- **Classifier combination:** exact enumeration confirmed dependence-sensitive
  ensemble behavior in a synthetic construction; it is an antecedent, not a
  novel result or evidence of practical organizational benefit.
- **Budgeted LLM allocation:** the only clear ILP-over-greedy contrast was
  +2.16 percentage points for contextual logistic prediction, homogeneous
  batches, budget 0.35. Most cells were tied or inconclusive; optimizer value
  depends on predictor and batch composition.
- **MMLU dynamic organization:** the initial FAST/DEEP measurement had inverted
  latency ordering and was retained as a separate pilot. The corrected
  direct-choice protocol showed a quality-latency tradeoff among candidates,
  but the tested cascade did not improve the observed frontier; confidence
  had AUC 0.508. This does not reject all cascades.
- **Contextual DCS-LA:** on 160 test queries, DCS-LA achieved 46.25% and
  139.27 ms; the best fixed model achieved 45.00% and 141.61 ms. The paired
  accuracy gain was +1.25 pp, 95% CI [−1.25, +3.75], hence inconclusive.
  Subject-fixed selection scored 51.25%/124.20 ms, but superiority is not
  established from point estimates. DCS-LA selected the same model on
  149/160 queries; the retrospective oracle is not executable.

## NON-CLAIMS

No universal HLS theory; no universal benefit of heterogeneity, specialization,
cooperation, learning, transfer, adaptation, planning, routing, ensembles,
joint management, or a named optimizer; no external validation across
applications; no claim that MMLU cascades are universally ineffective; no
claim that global estimation error determines organizational value; no
scientific novelty from infrastructure or combination alone. The model-
specific T0–T6 and S1–S7 results do not establish prevalence in real systems.

## REDUCTIONS / FALSIFIED DIRECTIONS

- **FALSIFIED / NARROWED:** S7's original Bellman advantage over the original
  myopic comparator partly depended on the latter's tie-break. BEST-MYOPIC
  reduces but does not eliminate Bellman's gap; CURRENT-DEMAND-MYOPIC equals
  Bellman on the central instance. These do not prove universal irrelevance of
  planning.
- **REDUCED TO STANDARD METHODS:** in the USE/DEVELOP formal line, unrestricted
  modules can represent joint behavior under explicit assumptions; the
  class-inclusion inequality is not a contribution. C2 resolves with explicit
  continuation/look-ahead.
- **CLOSED:** S3b-E1, classifier-combination pilot, budgeted-routing campaign,
  original/corrected MMLU and DCS-LA studies. No automatic extensions.
- **HOLD / NO-GO:** Campaign 4 full N=800 execution in its recorded protocol.
- **FROZEN:** `hls_foundations_v02` publication package is not to be modified
  or incorporated into official paper state without a new decision.

## FROZEN DECISIONS

- HLS identity and four-level conceptual architecture are governed by
  [HLS Philosophy](../../HLS_PHILOSOPHY.md); USE/DEVELOP and static/dynamic are
  optional research dimensions, not the programme's definition.
- Reductions to established theory are valid outcomes; no original HLS
  mechanism is required unless a demonstrated need remains.
- Preserve historical results, hashes, frozen protocols, negative results,
  and scope limitations.
- No new campaign or mechanism is authorized by this handover.
- Do not silently promote CE recommendations or a chat-only proposal to an
  approved scientific direction.
- RQ0 remains the sole official question in the current
  [Research Questions](../../research_questions.md) source, but the
  philosophical status of its USE/DEVELOP framing requires an explicit,
  traceable alignment decision.

## OPEN QUESTIONS

- RQ0 is **OPEN** as a formal, model-scoped question; standalone publication
  potential is **NO-GO at present** under the 2026-10-23 originality review.
- The 2026-10-23 Current State suggests S3b-E1 for further originality
  positioning but explicitly closes S3b-E1 and authorizes no new campaign.
  The new PI must decide whether any existing evidence can be positioned
  without reopening the campaign.
- Campaign 2/3 may support narrowly framed synthetic work after originality
  positioning, but external validity and the novel contribution are not
  established.
- The overall immediate publication priority and the next scientific question
  are not unambiguously reconciled in the current repository. No campaign
  should begin until the incoming PI records that choice.
- Canonical current scientific snapshot is dated 2026-10-23; align
  `research_questions.md` and selected historical-framework wording with the
  four-level philosophy without rewriting historical decisions.

## INTERFACES

| Role | Input received | Output owed | Escalation condition |
|---|---|---|---|
| PI | Evidence, independent CE recommendations, governance record | Strategic/scientific direction, novelty judgment, campaign authorization | Doctrine, publication strategy, formal scope, unresolved authority |
| CE (outgoing/ incoming) | PI direction, source hierarchy, bounded mission | Integrated theory-to-experiment-to-evidence traceability; risk and recommendation | Scope expansion, literature/research decision, resource/significant design |
| Expert / scoped specialist | Explicit mission and theory/evidence sources | Source-grounded result with failures, limitations, and WIP status | Scope or authority conflict |
| Codex / Handover Steward | Repository baseline and a delegated task | Read-only inspection, implementation/documentation, checks, provenance | Missing authority, unsafe WIP, canonical conflict |
| Incoming PI | This package and linked authorities | Independent reconstruction and acceptance/decision | Identity, authority, or doctrine ambiguity |

## CURRENT TASK

**Outgoing:** transfer this package to the incoming PI and keep the scientific
and governance state unchanged pending acceptance.

**Incoming PI:** identify yourself in the repository governance process;
independently review the required sources; confirm or challenge the scientific
interpretation; set the next research question and publication priority;
resolve the PI-replacement protocol gap; then request the role register update
through an explicitly approved governance action.

No experiment is currently authorized by this package.

## REQUIRED READING

1. [HLS Philosophy](../../HLS_PHILOSOPHY.md) — governing scientific identity.
2. [Research Doctrine](../../../RESEARCH_DOCTRINE.md) — claim and integration rules.
3. [HLS ontology](../../hls_ontology.md) and
   [Research Questions](../../research_questions.md) — semantics and current
   official RQ0.
4. [HLS Current State](../../HLS_CURRENT_STATE.md) — scientific snapshot and
   evidence links.
5. [Repository Guide](../../REPOSITORY_GUIDE.md), [History](../../HISTORY.md),
   and [Theory Registry](../../theory/README.md) — authority and chronology.
6. [Unified Framework](../../architecture/HLS_UNIFIED_FRAMEWORK.md),
   [HLS Ontology v0.1](../../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md),
   and [HLS-PEF](../../architecture/HLS_PERFORMANCE_EVALUATION_FRAMEWORK.md).
7. [Cumulative execution plan](../../engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md),
   [current roadmap](../../engineering/HLS_LAB_ROADMAP_CURRENT.md), and the
   experiment reports linked from Current State.
8. [Team Protocol](../HLS_TEAM_HANDOVER_PROTOCOL.md),
   [Role Register](../HLS_ROLE_REGISTER.md), and
   [CE handover supplement](../CE_HANDOVER_EXECUTION_PROTOCOL.md).

## OUTGOING MEMBER MATERIAL

**Work performed:** the full PI handover audit of the current repository;
verified current branch, commit, worktree, ignored material, running processes,
governance sources, scientific status, team roles, and source conflicts.

**Artifacts:** this draft handover record. No source code, experimental data,
historical result, hash manifest, role register, or protocol was modified.

**Decisions and limits transferred:** HLS identity is general and four-level;
USE/DEVELOP is not foundational; the RQ0 formal line is a scoped open question
but not currently an established standalone publication contribution; all
quantitative results retain the limits listed above.

**Unresolved items:** PI successor identity; absence of PI replacement
procedure; existing pending CE transfer; reconciliation of the official RQ0
wording with the new philosophy; incoming PI's research priority and acceptance.

## INCOMING CONFIRMATION

**Not received.** Incoming PI identity and independent acceptance report are
not present in repository sources. This package must remain
`PENDING_ACCEPTANCE`; the PI role register must not be changed until the
governance gap, identities, and acceptance are resolved.

## GOVERNANCE RESULT / STOP CONDITION

The audit and source-grounded outgoing package are prepared. The formal
replacement itself is **NOT COMPLETED**. This is required by the source
authority boundary: the canonical protocol has no PI-replacement procedure,
the successor is unnamed, and the role register requires confirmation before
status changes. The outgoing PI remains the only PI recorded as active
(`UNKNOWN / TO BE INITIALIZED`) until a valid successor acceptance and
documented PI disposition exist.

