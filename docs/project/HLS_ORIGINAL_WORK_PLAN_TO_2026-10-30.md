# HLS — Original work plan through 30 October 2026

**Purpose:** historical reconstruction of the work plan established for 19–30
October 2026. This is not a replacement roadmap and makes no new decision.
**Evidence cut-off:** repository/worktree state inspected on 19 October 2026.

## 1. Source and date of the original plan

The original dated plan was published on 17 October 2026 in commit
`799eb45`
(`docs(hls): publish execution plan and decision register`, 11:59 Europe/Madrid).
The plan's calendar was explicitly retained as a “línea base, no borrar” in
the later cumulative operational record. The controlling document is
[`HLS_LAB_EXECUTION_PLAN_2026-10-17.md`](../engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md).

The first version set an operational goal of constructing and validating HLS
components incrementally, preserving the scientific distinctions between
competence, productivity, experience, effort, output, budgets and observations.
It required explicit documentation of scope/date changes, separate campaign
authorization, protection of historical artifacts, and a final 30 October
phase report and decision. It did not authorize campaigns merely by listing
them on the calendar.

## 2. ORIGINAL PLAN — baseline calendar

| Target date | Original planned work | Intended output / success condition recoverable from the plan |
|---|---|---|
| 19 Oct | Audit HLS scientific memory | Evidence-based account of established HLS scientific memory. No separate acceptance metric was stated. |
| 20 Oct | Initial selection of 6–10 papers | Candidate literature set. The original baseline does not specify a scoring rule. |
| 21 Oct | Prioritize 3–4 investigations | Shortlisted investigations. Detailed decision criteria were not specified in the baseline. |
| 22 Oct | Mathematical analysis of models | Mathematical model analysis; no per-model template or exact deliverable was fixed in the baseline. |
| 23 Oct | HLS ontology v0.1 and weekly review | Ontology draft and review. |
| 26 Oct | Laboratory-reuse matrix | Map research needs to reusable laboratory capability. |
| 27 Oct | Reproducibility and comparability | Review of reproducibility and valid comparison conditions. |
| 28 Oct | Scientific-novelty memorandum | A novelty assessment was in the original baseline; it was later removed from the operational calendar by an explicit PI instruction. |
| 29 Oct | Preliminary experimental design | A bounded design with scenarios, metrics and controls; execution required separate authorization. |
| 30 Oct | Phase-closing report and GO / REFRAME / STOP decision | Report of capability, tests, limitations and decision on the next phase. |

### Original dependencies and success criteria

The baseline provides only a high-level sequence: review the scientific
memory and literature, analyze models, consolidate ontology and reuse,
consider reproducibility/comparability, then design and close. It does **not**
specify a dependency graph, named paper candidates, numerical acceptance
thresholds, a campaign budget, or criteria for choosing among GO/REFRAME/STOP.
Campaign execution was explicitly outside the authority of the calendar.
Those details cannot be reconstructed as original commitments.

## 3. ORIGINAL PLAN — initial mechanism workstream

The same 17 October plan also recorded an implementation workstream, distinct
from the dated calendar. In its initial version, Nembhard Direct integration
and focused regression were complete; indirect transfer and full article
reproduction were deferred; the next item was a MixLLM-inspired adaptive
router. The router was subsequently split into an ORACLE baseline and an
estimate-based router, and then consolidated into one bounded implementation.
The present worktree's cumulative plan records the final states and evidence.

## 4. FORMALLY APPROVED MODIFICATIONS recorded in the cumulative plan

These are recorded decisions, not retroactive changes to the original
calendar:

1. **17 Oct — incremental build/validation and Nembhard scope.** Work already
   advanced beyond the original day-by-day reading schedule; a bounded Direct
   productivity adaptation was accepted without requiring full Nembhard-paper
   reproduction. Indirect transfer and full reproduction were deferred.
2. **17 Oct — move Nembhard work earlier.** The Nembhard adapter originally
   expected around 19–20 Oct was brought forward. ORACLE was added first as a
   perfect-information current-period baseline; estimate-based routing was
   then delivered with it in a single integrated item.
3. **17 Oct — remove novelty/publicability evaluation from the operational
   calendar.** By explicit PI instruction, the 28 October operational
   novelty-memo milestone was replaced by ontology/architecture consolidation.
   The earlier baseline remains visible as history.
4. **17 Oct — conditional mechanism choice and implementation.** A bounded
   contextual quality–cost router inspired by components of MixLLM was selected,
   specified and implemented in an independent synthetic route. This was not
   a reproduction of MixLLM and did not authorize a campaign.
5. **17 Oct — prioritize Nembhard protocol design, then implementation.** The
   cumulative register records a 1,016-episode protocol, critical review
   (ADJUST), and implementation of its deterministic runner/analysis. The
   runner required an explicit confirmation for full execution; implementation
   did not itself authorize a campaign.
6. **17 Oct — campaign safety and incident response.** E1 interruption repair
   added estimator numerical handling and explicit safe resumption. The
   contemporaneous documented status was “started and interrupted,” with 29
   valid episodes and 987 pending; no partial output was a scientific finding.
7. **17 Oct — bounded adaptive-capability validation, next session 18 Oct.**
   The integrated validation was declared complete within its stated scope;
   literature reproduction selection/protocol design became the next
   documentary priority. HLS stayed PARTIAL.
8. **19 Oct — resume the 18 Oct documentary task.** The source review produced
   a STOP-before-execution recommendation: no eligible faithful reproduction
   candidate was ready with the then-available source artifacts and HLS
   components. No article reproduction was run.

The above are formal modifications because they appear in the cumulative
decision register/current plan. Per-session instructions and uncommitted
designs below are not silently promoted to additional calendar revisions.

## 5. LATER PROPOSALS OR TASK-SCOPED AUTHORIZATIONS — not baseline commitments

The repository contains several later, bounded task documents. Their presence
does not rewrite the original calendar:

- HLS-E1 anticipation design and minimum G0/RQ0 implementation were separately
  authorized as bounded tasks; they were not the original Nembhard E1 task.
- HLS-G0-C6 received an explicit exploratory-execution authorization on 19
  October, then an exact mechanism analysis and a **CLOSED — STOP** decision.
  This STOP closes C6 only; it is not the October 30 phase decision.
- Chen/Baccara comparisons, novelty and benchmark-investment assessments,
  laboratory extensibility assessment, and MixLLM/System-1.x reproduction
  preflights are documentary work products. The executability assessment
  concluded REVISE rather than selecting a method pair.
- The current worktree contains proposals and uncommitted engineering/experiment
  material (including Campaign 4 verification and adaptive-training proposals).
  Such material is not an approved replacement plan or evidence of a completed
  campaign. See the activity audit for exact status boundaries.

## 6. Current execution status against the original plan

As of 19 October, the original 19 October memory-audit objective has been
addressed by a local scientific-novelty audit and related reviews, but these
records are uncommitted in the inspected worktree. The 20 October literature
candidate selection and later work were pulled forward in the separately
recorded literature-reproduction task; six sources were reviewed, but no
reproduction-ready candidate was approved for execution. This is not evidence
that the baseline's 6–10 shortlist and 3–4 prioritization criteria were fully
satisfied.

The original 21–30 October milestones had not yet reached their target dates
at the evidence cut-off. Later, task-scoped documents partially cover model
analysis, reuse, reproducibility, experimental design and architecture, but
they do not constitute completion of every original milestone or the 30
October closure decision. The current tree keeps HLS Laboratory **PARTIAL**.

For the day-by-day evidence, experiments, worktree provenance and milestone
traceability, see
[`HLS_ACTIVITY_AUDIT_2026-10-17_TO_19.md`](HLS_ACTIVITY_AUDIT_2026-10-17_TO_19.md).

## 7. Unresolved historical ambiguities

- The original baseline has no author field, exact approval timestamp, detailed
  dependencies, paper-selection rubric, or quantitative success criteria.
- Calendar entries specify target days, but not daily sequencing or ownership.
- Several 19 October documents and code/results are uncommitted; their local
  file timestamps can date a filesystem write but do not establish author,
  review/approval, or whether an artifact was considered canonical at that
  moment.
- The initial versus revised router calendar changed during 17 October. The
  cumulative register records the transition; it does not preserve every
  intermediate deliberation as a separately approved plan.
- The local E1 result tree and the earlier interruption record disagree on
  completion count. This audit preserves both records and does not silently
  promote untracked outputs to published status.
