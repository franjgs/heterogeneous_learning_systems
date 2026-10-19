# HLS Role Handover — Chief Engineer — REPLACE

**Baseline:** `e6ad5a80e31986610bd2b597d3a4078c11d2b5f4`<br>
**Branch:** `feature/hls-laboratory-v1`<br>
**Date:** `2026-10-19`<br>
**Status:** `PENDING_ACCEPTANCE`

## ROLE

Outgoing Chief Engineer: previous ChatGPT instance coordinating HLS; status
`OUTGOING`. Incoming Chief Engineer: current GPT-6 instance in this
conversation; status `PENDING`. The PI explicitly authorized this replacement
and specified these identities. Neither status changes before the required
incoming report and PI disposition.

## MISSION

The incoming CE coordinates HLS scientific architecture and theory →
experiment → evidence → paper traceability, integrates scoped work, enforces
PI doctrine and repository authority, and stops work outside scope or against
documented reductions. Immediate task: independently reconstruct this record
and return the acceptance report required by §8 of the Team Handover Protocol.
No research execution is authorized by this handover.

## AUTHORITY / SCOPE

**May decide:** repository-grounded coordination, sequencing, WIP classification,
scoped integration, and stopping work inconsistent with doctrine/evidence.

**Must escalate:** doctrine or strategic changes, reopening frozen directions,
material conflicts among canonical sources, unresolved governance authority,
and decisions that exist only in chat.

**Must not decide:** override PI doctrine or evidence; promote WIP, literature,
or drafts to canonical status; reinterpret falsifications; or infer missing
scientific decisions.

## PROJECT QUESTION

The programme studies how heterogeneous, limited, evolvable collective
capabilities should be organized and developed over time as problems and needs
change. The official current question is RQ0: within its declared formal scope,
can dynamic allocation and development improve long-run performance over
architectures managing allocation and transfer separately? Sources:
[Philosophy](../../HLS_PHILOSOPHY.md),
[Research Questions](../../research_questions.md),
[Current State](../../HLS_CURRENT_STATE.md).

## PI DOCTRINE

The governing method is **REDUCE BEFORE INVENTING. BUY BEFORE REBUILDING.
ASSEMBLE BEFORE EXTENDING** ([Research Doctrine](../../../RESEARCH_DOCTRINE.md)).
The literature reproduction selection dated 2026-10-19 records **STOP before
execution**: resolve the listed source-artifact dependencies or choose another
defensible candidate and obtain authorization. The lab remains **PARTIAL**.
This record does not authorize execution.

## CANONICAL BASELINE

**HEAD / branch:** `e6ad5a80e31986610bd2b597d3a4078c11d2b5f4` on
`feature/hls-laboratory-v1`. `git ls-remote origin
refs/heads/feature/hls-laboratory-v1` returned the same SHA. The user-supplied
prior baseline `a09dcc4a79e969b93e66f2c4b38414651bb3cd78` does not match the
current local/remote branch and is superseded as the effective handover
baseline by this observed state. No fetch or branch movement was performed.

**Worktree:** dirty; all pre-existing modifications remain untouched. Tracked
changes: `docs/literature/references.bib`; the two configuration-environment
policy modules; `finite_problem_belief.py`, `small_problem_world.py`,
`synthetic/c1.py`; and their six listed tests. The complete untracked inventory
is preserved by `git status --short` at this baseline. Its main groups are:

- engineering, experimental-foundation, experiment, literature-analysis,
  paper, research, and governance documents;
- HLS-E2, campaign 4, functional-problem, Meta-VOC, and prototype code/tests;
- untracked scientific result trees under `results/analysis`,
  `results/diagnostics`, and `results/experiments`, plus
  `hls_e2_0_results.json`;
- `src/hls/functional_problem.py` and associated tests.

The WIP is classified **pending decision / excluded from canonical handover
evidence** unless independently accepted by the incoming CE through normal
review. Untracked scientific outputs are not canonical merely by presence.
No WIP was staged, executed, regenerated, or modified. The `git status`
inventory is large (notably the Nembhard E1 result tree); individual ownership
and acceptance state are not materialized. A process-list check was denied by
the environment, so whether an experiment process is active could not be
verified; do not treat this as evidence that no process is running.

**Sources consulted:** protocols and template; role register; 2026-10-05
handover; Philosophy, Doctrine, Ontology, Research Questions, Current State,
Repository Guide, Theory Registry and History; adaptive-capability validation;
Campaign 4 engine verification; current execution plan; literature-selection
artifact. See Required Reading for the canonical reconstruction sequence.

**Excluded or classified WIP:** all current tracked modifications and
untracked artifacts listed above are excluded from the handover commit and
remain pending; details are not inferred from filenames. In particular,
`docs/experiments/HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md` is
untracked, documentary WIP, and is described separately below.

**Known contradictions or gaps:** the recorded previous baseline and branch
(`a09dcc4…` in the initiating instruction) differ from current local and
remote (`e6ad5a80…`). The October 5 register had unknown identities and a
pending transfer; the PI's current decision now names both identities and
supersedes that transfer. The previous record is retained unchanged. The
working tree includes broad unreviewed scientific WIP, including experiment
result trees, and process status could not be inspected. These facts require
incoming independent review; no scientific interpretation is inferred from
those artifacts.

## ESTABLISHED RESULTS

Status labels below follow the Current State and its source map; they are
scoped, not universal claims.

- **CONSOLIDATED / SCOPED:** static capability/organization foundations and
  dynamic D0/D1/D2 controls have their stated theory and ground-truth scope.
- **CANONICAL ESTABLISHED:** Minimal Reference Scenario and information audit
  establish their declared finite scenario and information partitions.
- **CANONICAL ESTABLISHED:** G3 establishes its exact assignment-sensitivity
  reduction; G3-H's fixed heterogeneous learning-rate case supplies its
  audited local-versus-future ranking counterexample.
- **CANONICAL ESTABLISHED (formalization-scoped):** `Pi_SEP` is a restricted
  subset of `Pi_HLS`; finite-exact strictness against strong SEP holds iff no
  HLS-optimal policy is strong-SEP admissible. The documented `C(alpha)` strict
  value interval is `5/16 < alpha < 1/2`; SEP-Omega is a sufficient-continuation
  coordination/reducibility boundary.
- **VERIFIED BUT SCOPED:** laboratory validation confirms execution and
  reproducibility of selected existing mechanisms. It does not establish
  policy superiority, generality, or full-paper reproduction.

Consult Current State and its linked primary records for exact assumptions,
proofs, artifacts, and claim boundaries.

## NON-CLAIMS

No universal HLS, heterogeneity, specialization, adaptation, or joint-management
superiority; no established prevalence, genericity, robustness, or empirical
realism of synthetic integration conditions; no universal dynamic HLS model;
no superiority over sufficiently informed modular control; no inference of
substantive advantage from policy-class inclusion alone. Capability validation
is not policy-performance evidence or external validation. Literature
compatibility is not reproduction.

## REDUCTIONS / FALSIFIED DIRECTIONS

- **FALSIFIED:** C1's `max D` future-opportunity shortcut preserves the wrong
  G3-H ranking.
- **REDUCED TO STANDARD DYNAMICS:** C2's exact correction is explicit
  look-ahead / dynamic programming, not an intermediate HLS mechanism.
- **HISTORICAL / NON-CANONICAL:** local `g,rho,m`, regime, stability,
  screening, and continuation-relevance lines did not establish an exact local
  certificate; C-stability remains unresolved, not proved or falsified.
- **HISTORICAL REDUCTION — STOP:** matched-`Delta S` would refine causal
  identification, not supply a missing theoretical dependency; it was not run.
- **REPRODUCIBILITY STOP:** MixLLM Table 1 cannot currently be reproduced
  faithfully from identified local data/code/runtime artifacts. Do not
  substitute HLS ridge routing or call it reproduction.

## FROZEN DECISIONS

- Novel Beam-1 × Beam-2 integration-mechanism search is closed absent explicit
  PI reopening on a genuinely new dependency/evidence basis.
- Do not relaunch the local-versus-continuation loop under renamed scores,
  certificates, screening, or metareasoning if exact validation reconstructs
  continuation/look-ahead.
- Do not use literature, publication drafts, protocols, WIP directories, or
  diagnostics as canonical evidence without explicit review/promotion.
- No experiment, literature reproduction, new mechanism, lab redesign,
  frozen-experiment modification, or feature-branch merge is authorized by
  this handover. No force-push.

## OPEN QUESTIONS

- **CANONICAL CURRENT:** RQ0's structural characterization, robustness, and
  empirical relevance remain open within the formal scope.
- **CURRENT HYPOTHESIS / DIRECTION:** characterize when R0 use is sufficient,
  R1 development is relevant but separable, and R2 joint intertemporal
  management is relevant; these are not established boundaries.
- **FOUNDATIONAL GAP:** sufficiently complete operational performance and
  fair resource-constraint definitions remain open.
- **OPERATIONAL PRIORITY:** current execution plan records documentary
  literature screening STOP. Before any GO, resolve source/data/code/runtime
  dependencies or select a sufficiently specified source experiment, then
  secure separate PI authorization.

## INTERFACES

| Role | Input received | Output owed | Escalation condition |
| --- | --- | --- | --- |
| PI | Doctrine, strategic direction, authorization | Evidence-backed decision on material conflicts | Authority, doctrine, or scientific-direction changes |
| Incoming CE | This package and canonical sources | §8 written independent acceptance report | Baseline/WIP disagreement or material source contradiction |
| Handover Steward | Repository/protocol/register | Baseline, WIP and package checks; no activation | Unresolved authority or unsafe baseline |
| Experts / Beam Owners | Explicit scoped missions only | Auditable results with failures/reductions and WIP status | Scope expansion or conflicting authority |

## CURRENT TASK

Incoming CE: perform independent source reconstruction and submit all required
§8 acceptance headings: baseline; project question; established claims and
non-claims; reductions/failures; PI direction; WIP; contradictions/gaps;
independent diagnosis; one bounded first recommendation; necessary PI
escalations. Keep status `PENDING` until PI disposition. Escalate unresolved
material conflicts to the PI. Do not run experiments or the literature task.

## REQUIRED READING

Follow the live authority map and this sequence:

1. [HLS Philosophy](../../HLS_PHILOSOPHY.md), [Research Doctrine](../../../RESEARCH_DOCTRINE.md),
   [Ontology](../../hls_ontology.md), [Research Questions](../../research_questions.md).
2. [Current State](../../HLS_CURRENT_STATE.md), [Repository Guide](../../REPOSITORY_GUIDE.md),
   [History](../../HISTORY.md), [Historical Memory and Novelty Guard](../../HLS_HISTORICAL_MEMORY_AND_NOVELTY_GUARD.md).
3. [Theory Registry](../../theory/README.md), then linked static/dynamic theory
   and ground truths relevant to RQ0.
4. Minimal scenario and information audit; MIS/information materials; G3/G3-H
   reductions; RQ0 integration sources and G0.
5. Current lab validation, execution plan, relevant protocols/manifests/code/
   tests/results, and only then literature records as needed.
6. [Team Protocol](../HLS_TEAM_HANDOVER_PROTOCOL.md),
   [Execution Supplement](../CE_HANDOVER_EXECUTION_PROTOCOL.md), this record,
   the [Template](../HANDOVER_TEMPLATE.md), [Role Register](../HLS_ROLE_REGISTER.md),
   and preserved [2026-10-05 handover](2026-10-05_replace_chief_engineer.md).

## OUTGOING MEMBER MATERIAL

No separate outgoing CE report or personal work log is present in repository
sources. This package reconstructs responsibility from canonical sources and
labels missing personal transfer material as missing. The predecessor's
2026-10-05 handover remains preserved as a historical pending record; its
transfer is superseded, not accepted or deleted.

## INCOMING CONFIRMATION

**PI governance decision (2026-10-19):** PI explicitly authorizes replacement;
outgoing is the previous coordinating ChatGPT instance; incoming is current
GPT-6; the 2026-10-05 pending transfer is superseded by this dated transfer;
historical documentation must be preserved; incoming remains pending until
formal independent review, acceptance, and registration.

**Literature-selection artifact:**
`docs/experiments/HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md` exists
as an untracked document (not in HEAD and not published/registered as
canonical). It contains a multi-candidate primary-source comparison, HLS
mapping and compatibility judgments, a blocked MixLLM Table 1 protocol target,
missing data/code/runtime dependencies, a STOP recommendation, and source
index. It reports no experiment execution and explicitly rejects substitution
of the current HLS contextual router. It is substantive and internally
structured, but remains WIP: artifact provenance/author and independent review
are not registered, and its claims must be checked against cited sources before
promotion. This handover neither executes nor duplicates the task.

## TRANSFER COMPLETION RECORD

PI authorization: received in the 2026-10-19 instruction.<br>
Outgoing / incoming: previous ChatGPT CE / current GPT-6 CE.<br>
Baseline: `e6ad5a80e31986610bd2b597d3a4078c11d2b5f4` / `feature/hls-laboratory-v1`; remote matched at preparation.<br>
Worktree and WIP: dirty; classified above, preserved; active-process state unavailable.<br>
Outgoing transfer: reconstructed from repository sources; no separate report found.<br>
Incoming acceptance report: pending.<br>
Unresolved items: incoming independent diagnosis; WIP ownership/acceptance; process status; any source conflicts found during reconstruction.<br>
PI disposition: pending acceptance report.<br>
Role-register update: records identities, supersession and new baseline only; statuses remain OUTGOING/PENDING.<br>
Final status: `PENDING_ACCEPTANCE`.
