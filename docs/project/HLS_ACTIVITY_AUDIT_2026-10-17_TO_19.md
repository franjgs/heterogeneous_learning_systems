# HLS — Activity audit, 17–19 October 2026

**Scope:** historical reconstruction from Git, repository documents, the
current local worktree and result artifacts. No experiment, test suite or
simulation was run for this audit. **Evidence cut-off:** 19 October 2026.

> **Status vocabulary.** “Implemented” means code/artifact exists; “executed”
> means a recorded run or test occurred; “validated” is limited to its stated
> test/analysis scope; “documented” is not execution. Uncommitted work is
> reported as local evidence, not as published/canonical project state.

## 1. Executive reconstruction

The dated operational plan was established on 17 October and set a 19–30
October sequence from HLS memory/literature review through model analysis,
ontology, reuse/comparability, preliminary design, and a 30 October GO /
REFRAME / STOP close. Its baseline is preserved in the
[`operational plan`](../engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md)
and transcribed with approved amendments in
[`HLS_ORIGINAL_WORK_PLAN_TO_2026-10-30.md`](HLS_ORIGINAL_WORK_PLAN_TO_2026-10-30.md).

Activity was unusually concentrated on 17 and 19 October. On the 17th, the
Nembhard Direct/ORACLE/ADAPTIVE and contextual-router workstreams, the common
experiment record, Nembhard E1 protocol/runner, a campaign interruption repair,
E2.0/E2.1, and a bounded laboratory-capability validation all generated code,
tests or evidence. On the 18th, the planned source-based reproduction selection
has no independently dateable repository artifact; the official record says
that work was resumed on the 19th. On the 19th, a substantial set of literature,
mathematical, compatibility and design audits was produced; the separate
HLS-G0-C6 exploratory campaign ran and was closed after exact analysis.

The evidence does **not** support treating every local file as a published
deliverable. The branch has substantial modified and untracked work. In
particular, the current local E1 output differs from the contemporaneous
interruption count. Both are preserved below without treating the local result
tree as official evidence.

## 2. Evidence and provenance rules

Primary chronology comes from local commit times (Europe/Madrid), the
cumulative project history, dated report content, script/result metadata and
filesystem modification times. A Git commit establishes when a record entered
Git, not necessarily when underlying activity happened. A filesystem mtime
does not establish authorship, review or approval. No repository evidence
allows attribution to a specific individual, so this audit attributes actions
to the project/work session, not a named person.

At inspection, branch was `feature/hls-laboratory-v1`. The tree already had
modified and untracked files across `docs/`, `src/`, `tests/`, `experiments/`
and `results/`. They were not edited, cleaned, staged or otherwise disturbed.
The reports created on 19 October listed below are untracked at this snapshot;
their conclusions are therefore worktree evidence, not published branch
history. The last Git commits in the relevant period are:

| Local time | Commit | What the commit establishes |
|---|---|---|
| 17 Oct 10:38–11:59 | `2e65926`, `f345535`, `be4d1a0`, `f73e688`, `b5f0c36`, `799eb45` | Nembhard Direct mechanism/integration, ORACLE and the initial operational plan. |
| 17 Oct 12:18–16:48 | `d1e0a1f`, `9240b54`, `0636360`, `f6b229c`, `16750eb`, `a4e2591`, `957ef06` | Nembhard ADAPTIVE; conditional MixLLM-inspired contextual-router selection/contract/implementation; architecture and common-run record; consolidated state. |
| 17 Oct 16:58–18:50 | `62a08df`, `eca2976`, `087e13e`, `aee5c8b`, `8d16f90` | Nembhard E1 protocol, ADJUST review, guarded campaign runner, estimator/resume repair and scope clarification. |
| 17 Oct 20:13–20:18 | `32d2288`, `a09dcc4` | Integrated capability-validation evidence and documentary closure/18 Oct priority. |
| 19 Oct 08:55–08:58 | `e6ad5a8`, `8531b08` | Literature-screening result and CE handover. |
| 18 Oct | No commit found in the inspected branch history. | Absence of a commit is not proof that no work occurred. |

The commit summaries are intentionally not treated as the complete activity
record; uncommitted reports and result files provide additional evidence.

## 3. 17 October 2026

### Scientific and engineering activity

1. **Nembhard Direct integration.** The direct experience productivity curve
   was added and integrated into the N×K execution route with explicit
   allocations and unit distinctions. ORACLE was added as a feasible-action,
   true-productivity current-period baseline; ADAPTIVE added selected-work
   observations, an online productivity estimate and reproducible optional
   exploration. These are implemented mechanisms, not full reproduction of
   Nembhard–Bentefouet and not MIS-v2 competence learning. Evidence is in
   commits `2e65926` through `d1e0a1f`,
   [`HLS_CURRENT_STATE.md`](../HLS_CURRENT_STATE.md), and the router reports
   under `docs/engineering/`.
2. **Contextual quality–cost router and common experiment record.** A
   MixLLM-inspired contract was specified and a separate synthetic
   contextual-router implementation added; architecture documentation then
   mapped actual component boundaries. A versioned non-destructive run/event
   contract adapted N×K/MIS-v2, Nembhard and contextual-router results. These
   are HLS components and adaptations, not MixLLM reproduction or a universal
   simulation architecture. Evidence: commits `0636360`–`a4e2591` and their
   files/tests.
3. **Nembhard E1 design and runner.** The 1,018-proposed episode protocol was
   critically reviewed (**ADJUST**) and reduced to 1,016 unique configurations;
   a deterministic registry, safe CLI, fixed policy and result analysis were
   implemented. The runner’s existence/validation is not a scientific result.
   Evidence: `62a08df`, `eca2976`, `087e13e`,
   [`HLS_NEMBHARD_PROTOCOL_REVIEW.md`](../experiments/HLS_NEMBHARD_PROTOCOL_REVIEW.md)
   and `src/hls/nembhard_campaign.py`.
4. **E1 numerical interruption and recovery design.** A Welford update failed
   when initializing the estimator from a zero-count prior; the tracked repair
   treats the first observation exactly, tolerates only small scale-aware
   floating-point residuals, rejects invalid states and adds explicit safe
   resume/status behavior. The incident report recorded 29 valid runs and 987
   pending, no corrupt/incomplete episode directories at that audit, and an
   interrupted—not completed—campaign. The likely failing ID was not persisted.
   Evidence: `aee5c8b`, `8d16f90`,
   [`campaign runner record`](../engineering/HLS_NEMBHARD_CAMPAIGN_RUNNER.md).
5. **HLS-E2.0 / E2.1 standalone deterministic productivity studies.** Local
   scripts reused the scalar Nembhard curve but did not run through the N×K
   simulator. E2.0’s saved output describes 1,000 seeded parameter cases at
   each of horizons 20/60/120, exact DP versus greedy and best initial-agent
   fixed assignment. E2.1’s saved result contains 33 deterministic profile ×
   demand cases, exact dynamic DP, exhaustive checks at small horizons and a
   globally optimized task-dependent static baseline; its stored
   `positive_case_count` is zero. The report gives a structural explanation
   for the separable independent-skill null. These are model-scoped results,
   not a verdict on all HLS adaptive capability. Evidence: mtime-stamped
   scripts and results (`19:21–19:29`),
   [`HLS_E2_1_PROTOCOL.md`](../experiments/HLS_E2_1_PROTOCOL.md),
   `experiments/hls_e2/` and `results/analysis/hls_e2/`. They are untracked at
   the inspected snapshot.
6. **Integrated adaptive-capability validation.** A bounded runner reused
   existing C5 stationary/nonstationary/Markov demand, N×K execution,
   MIS-v2/estimation, P0/P2 and G2 controls, with five named checks S0–S4.
   The report records 135 focused tests passed; the full suite was not run for
   this validation, five historical provenance/inventory failures remained,
   and no large campaign was executed. This validates bounded execution and
   trace/information contracts, not policy superiority or paper reproduction.
   Evidence: commits `32d2288`, `a09dcc4`,
   [`canonical validation report`](../experiments/HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md)
   and its JSON/registry under `results/analysis/hls_lab_validation/`.

### Experiments actually executed and result-status discrepancy

- E2.0 and E2.1 generated saved output files on 17 October. E2.0 is a seeded
  exploratory random parameter search (not population inference); E2.1 is a
  compact deterministic parameter study. Neither is the later HLS-G0-C6
  campaign.
- The integrated validation executed its small deterministic scenarios and
  focused tests; it was explicitly not a campaign.
- Nembhard E1 was started and interrupted. The tracked incident record says
  29 complete/987 pending. The current **untracked** local tree has 1,016
  episode directories and matching counts of `run.json`,
  `native_nembhard_result.json`, and `campaign_metrics.json`; the current
  state/history also records a subsequent read-only audit of 1,016 valid/0
  pending. The local tree additionally has `results/analysis/hls_e1/analysis.json`.
  This is evidence of later local completion relative to the incident snapshot,
  but it is not committed/published; individual output presence must not be
  confused with a tracked canonical result. The precise time and authorization
  record for the transition from 29 to 1,016 is not fully reconstructible from
  the incident document alone.

### Decisions on 17 October

Recorded choices included bounded Direct-model reuse rather than full paper
reproduction; ORACLE then ADAPTIVE as a staged-but-consolidated route; conditional
selection of an independent contextual router; a common record format without
common simulator semantics; E1 protocol **ADJUST** before execution; and a
separate validation-first priority for the 18 October session. The lab remained
**PARTIAL**. No general policy-superiority claim was approved.

## 4. 18 October 2026

The 17 October closure records the intended 18 October work as documentary:
review original papers, choose one reproducible experiment, map its model and
metrics to HLS, write a bounded protocol and seek authorization before
execution. The operational plan and project history explicitly say that this
work was **resumed on 19 October**. No 18 October Git commit or uniquely
dateable 18 October experiment artifact was found in the inspected evidence.

Therefore the reliable classification is:

- **PROPOSED / AUTHORIZED FOR DOCUMENTARY DESIGN:** literature selection and
  protocol preparation.
- **EXECUTED ON 18 OCT:** not established by repository evidence.
- **EXECUTED ON 19 OCT:** the resumed source-review/selection report described
  in the next section.

This is an evidence limit, not a claim that no offline or unrecorded activity
occurred.

## 5. 19 October 2026

### Literature, mathematics and compatibility work

The existing source reviews were extended in a series of bounded documents,
not a new code implementation. Local file times, report dates and commit
`e6ad5a8` support the following sequence; the exact start/end time of the
underlying reading is not known.

| Activity | State / disposition | Evidence |
|---|---|---|
| Resume the planned literature-source selection; inspect six registered papers and compare reproduction readiness | **DOCUMENTED; STOP before execution.** No candidate then met exact/defensible approximate reproduction requirements from available sources/artifacts. | [`HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md`](../experiments/HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md), commit `e6ad5a8`, operational plan register. |
| Targeted search for published adaptive-vs-fixed positive results | **DOCUMENTED; STOP for HLS reproduction authorization.** The found comparisons did not all match the desired organizational question. | [`HLS_TARGETED_ADAPTIVE_ADVANTAGE_LITERATURE_SEARCH_2026-10-19.md`](../experiments/HLS_TARGETED_ADAPTIVE_ADVANTAGE_LITERATURE_SEARCH_2026-10-19.md). |
| Scientific prior-art/novelty audit | **DOCUMENTED in local worktree**, with claim-by-claim limits and a narrow research direction assessment; no experiment. | [`HLS_SCIENTIFIC_NOVELTY_AUDIT_2026-10-19.md`](../research/HLS_SCIENTIFIC_NOVELTY_AUDIT_2026-10-19.md). |
| Formal Baccara–Chen comparison; acquisition/registration of full Chen paper; full-text Chen mathematical audit and simulator compatibility review | **DOCUMENTARY ANALYSIS.** The Chen source limitation was resolved for the local audit; compatibility report gave conditional GO for an isolated future implementation, not implementation authorization. | [`HLS_BACCARA_CHEN_FORMAL_COMPARISON_2026-10-19.md`](../research/HLS_BACCARA_CHEN_FORMAL_COMPARISON_2026-10-19.md), [`HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md`](../research/HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md), [`HLS_CHEN_SIMULATOR_COMPATIBILITY_AUDIT_2026-10-19.md`](../experiments/HLS_CHEN_SIMULATOR_COMPATIBILITY_AUDIT_2026-10-19.md), local Chen PDF. |
| Chen benchmark-investment assessment and laboratory extensibility/capability assessments | **DOCUMENTED proposals/assessments; no implementation.** | [`HLS_BENCHMARK_INVESTMENT_ASSESSMENT_2026-10-19.md`](../research/HLS_BENCHMARK_INVESTMENT_ASSESSMENT_2026-10-19.md), [`HLS_LABORATORY_EXTENSIBILITY_AUDIT_2026-10-19.md`](../architecture/HLS_LABORATORY_EXTENSIBILITY_AUDIT_2026-10-19.md), [`HLS_LABORATORY_CAPABILITY_ASSESSMENT_2026-10-19.md`](../research/HLS_LABORATORY_CAPABILITY_ASSESSMENT_2026-10-19.md). |
| MixLLM/System-1.x preflight and subsequent executable-method selection | Preflight **DOCUMENTED**; selection **REVISE**, no complementary pair selected, no algorithm implementation or campaign. Cavenaghi is identified only as an executable standalone candidate; Emam as an allocation candidate with substantial environment mismatch. | [`HLS_PUBLISHED_METHODS_REPRODUCTION_PREFLIGHT_2026-10-19.md`](../experiments/HLS_PUBLISHED_METHODS_REPRODUCTION_PREFLIGHT_2026-10-19.md), [`HLS_EXECUTABLE_PUBLISHED_METHOD_SELECTION_2026-10-19.md`](../experiments/HLS_EXECUTABLE_PUBLISHED_METHOD_SELECTION_2026-10-19.md). |

These are activity records in the current worktree. Except for the two cited
morning commits, they were untracked at audit time and are not official
published decisions. They do not alter the original calendar by themselves.

### E1 anticipation design and minimum G0/RQ0 implementation

The local [`HLS_E1_VALIDATION_DESIGN_2026-10-19.md`](../experiments/HLS_E1_VALIDATION_DESIGN_2026-10-19.md)
examined a distinct “anticipation” study and recommended REVISE before
implementation; it warns not to conflate this proposed E1 label with the
existing Nembhard HLS-E1. A subsequent task-scoped instruction authorized a
minimum implementation, after which local modifications appeared in
`src/hls/synthetic/exact.py`, new `src/hls/synthetic/e1_minimum.py`,
`tests/synthetic/test_e1_minimum.py`, and the G0/RQ0 runner. These support the
small four-policy experiment below. The implementation is local/uncommitted;
no claim is made here that it was incorporated into the published N×K lab.

### HLS-G0-C6 — actual exploratory campaign, exact analysis, closure

Unlike the literature reviews and proposals, C6 has a trajectory result file.
The local runner `experiments/run_hls_g0_c6.py` wrote
`results/experiments/hls_g0_c6/exploratory_results.json` (file mtime 14:17).
The report specifies 2 agents × 2 tasks × horizon 4; `eta={0,0.1,0.75}`;
stationary/changing demand; 20 paired trajectories per cell; and four policies
`BEST_STATIC`, `MYOPIC`, `STRONG_SEP`, `HLS`: 120 exogenous trajectories / 480
policy evaluations. Tests and validation are reported in the campaign report
(101 focused, 272 synthetic, plus Ruff), not rerun for this audit.

The exact saved/model results are: all policies value 4.0 for `eta=0` and
`0.1`; at `eta=.75`, HLS vs BEST_STATIC is 4.175 vs 4.015625 (stationary,
gap .159375) and 4.130 vs 4.00544 (changing, gap .12456). The exact accounting
decompositions are preserved in the
[`mechanism analysis`](../experiments/HLS_G0_C6_EXACT_MECHANISM_ANALYSIS_2026-10-19.md):
stationary operational +.10625, terminal +.053125, development cost 0;
changing operational +.07232, terminal +.05224, cost 0. The report identifies
opportunity-gated A1 development followed by flexible routing; it explicitly
does not attribute the gap to nonstationarity, establish general superiority,
or claim a new mechanism.

Exact mechanism analysis was documented after the campaign and followed by
[`C6 closure`](../experiments/HLS_G0_C6_CLOSURE_2026-10-19.md):
**CLOSED — STOP** for further C6 campaigns/expansion. The result remains
valuable as a reproducible, quantitative characterization consistent with
G2/G3-H/RQ0. The STOP decision preserves the experiment and its evidence; it
does not say the implementation failed or that the observed finite-instance
gap is invalid. C6 is distinct from the E1 Nembhard campaign and from the
synthetic capability taxonomy's separate “C6”.

### Other visible worktree material

At the evidence cut-off, modified files also included configuration/environment
policy implementations, finite-problem belief, `small_problem_world.py`,
`synthetic/c1.py`, associated tests, and result files; untracked material
included a Campaign 4 counterfactual engine/preflight and reports, adaptive
training proposals, CE16/functional-problem code and results, configuration ×
environment diagnostics, and meta-VOC diagnostics. These are relevant to the
current worktree audit, but a filename or mtime alone cannot reliably assign
all of this material to 17, 18 or 19 October, establish task authorization,
or prove a campaign ran. For example,
`CAMPAIGN_4_ENGINE_VERIFICATION.md` explicitly says preparation only, no N=800
evaluation or scientific counterfactual experiment. Uncommitted results must
not be promoted to published findings merely because files exist.

## 6. Decision register and classification summary

| Activity / question | Implemented | Executed | Validated | Documented | Decision / status |
|---|---:|---:|---:|---:|---|
| Nembhard Direct + ORACLE + ADAPTIVE | Yes, 17 Oct commits | Dedicated tests; E1 run started | Focused tests; E1 campaign status has local-vs-incident discrepancy | Yes | Mechanisms retained; no general superiority conclusion. |
| MixLLM-inspired contextual quality–cost route | Yes, independent synthetic route | Deterministic test/replay | Focused unit/replay tests | Yes | Not MixLLM reproduction; no campaign. |
| Common experiment contract | Yes, adapters/envelope | Adapter tests | Focused compatibility tests | Yes | Common format does not imply scientific comparability. |
| Nembhard HLS-E1 runner | Yes | Campaign started; interrupted record, later local results show all 1,016 IDs | Runner/tests and local result audit; no canonical published completion | Yes | Preserve the two evidence states; no campaign inference from partial/historical run. |
| E2.0 | Standalone script | Seeded random search output saved | Exact DP within its own implementation; not general HLS validation | Partly | Negative/structural result is scoped to one-skill separability. |
| E2.1 | Standalone script | 33 deterministic cases saved | Exhaustive small-horizon validator reported in script/result | Yes, local WIP | Zero dynamic-vs-best-static gaps under stated separable assumptions. |
| Integrated adaptive capability validation | Reused components plus runner | Five bounded scenarios and tests | 135 focused tests; full suite not run for this task | Yes, committed | Bounded integration validated; lab remains PARTIAL. |
| Literature/Chen/method audits | No new mechanism | No literature reproduction | Source/math review only | Yes, mostly untracked | STOP on first candidate selection; REVISE on method-pair selection. |
| HLS-G0-C6 | Existing G0/RQ0 solver and four-policy runner | 120 paired paths | Reported exact solver comparison, replay/test checks | Yes, local WIP | CLOSED — STOP for C6 extension; findings preserved. |
| 18 Oct planned reproduction selection | No | Not evidenced on 18th | N/A | Later recorded as resumed 19th | Documentary work only; no execution authority. |

The five known historical provenance/inventory failures were not resolved by
the 17 October adaptive-capability validation. That validation passed 135
focused tests and did not rerun the full suite. Earlier suite totals in the
plan/history are point-in-time reports; they must not be merged into one
single test result.

## 7. Plan-versus-execution traceability

| Original milestone | Planned date | Work performed / evidence | Status at 19 Oct evidence cut-off |
|---|---:|---|---|
| Audit HLS scientific memory | 19 Oct | Local scientific-novelty audit plus prior-history/model reviews; not committed at cut-off. | **Addressed in WIP, not established as published closure.** |
| Select 6–10 papers | 20 Oct | Six registered sources compared in the reproduction selection report dated 19 Oct; a targeted positive-result search followed. | **Pulled forward / partly met:** candidate screen exists, but no eligible reproduction was selected. |
| Prioritize 3–4 investigations | 21 Oct | Comparative compatibility/benchmark/method assessments; final local method-pair report says REVISE and selects no pair. | **Not completed as an approved shortlist.** |
| Mathematical model analyses | 22 Oct | Baccara–Chen and Chen full-text reports; other source reviews. | **Partial/task-scoped WIP; not a complete model set.** |
| Ontology v0.1 and weekly review | 23 Oct | Existing ontology and architecture audit checked boundaries. | **Partial:** no evidence of an approved v0.1 ontology release or scheduled review. |
| Laboratory reuse matrix | 26 Oct | Capability and extensibility assessments prepared early. | **Prepared in WIP; not canonical/published.** |
| Reproducibility and comparability | 27 Oct | Reproduction selection, targeted search, benchmark investment and preflight assessments. | **Partly performed; conclusion was STOP/REVISE, not a ready reproduction.** |
| Novelty memo | 28 Oct | Original item was formally removed from operational calendar 17 Oct; a local novelty audit was nevertheless requested/performed 19 Oct. | **Removed as plan milestone; local documentary audit exists.** |
| Preliminary experiment design | 29 Oct | E1 anticipation design and other task-scoped proposals exist; C6 was actually run under separate authorization. | **Partly advanced; no single replacement plan authorized. C6 closed.** |
| Final report and GO/REFRAME/STOP | 30 Oct | No phase-closing report dated 30 Oct exists at cutoff. C6 STOP is experiment-specific, not phase close. | **Pending by target date.** |

### Work that displaced or ran outside the baseline

- The Nembhard integration, adaptive router, contextual router, common run
  envelope, E1 protocol/runner and integrated capability validation occupied
  17 October and preceded the original 19–23 October reading milestones.
- E2.0/E2.1 and HLS-G0-C6 were additional standalone G0/Nembhard studies, not
  in the original Oct 19–30 baseline.
- Chen/Baccara and adaptive-method audits, paper registration, the E1
  anticipation design and the local method-selection chain expanded the
  documentary work on 19 October.
- C6's exact analysis and closure add a valuable preserved result outside the
  original plan. Its STOP is scoped to C6 and does not erase its quantitative
  scientific value.
- The worktree contains still more WIP (including Campaign 4 and teaching
  proposals); available timestamps/authorization records are insufficient to
  add these as completed dated milestones.

## 8. Scientific findings to preserve, and duplicate/repeated work

1. **Capability validation is bounded and real:** C5 stationary, scheduled
   nonstationary and Markov demand were generated and traced through the N×K
   runner; G2 positive/null controls were reused; P0 state response and P2
   reference execution were checked. It does not show policy superiority.
2. **E2.1 is an informative structural negative control:** within its
   independent-skill, increasing Nembhard productivity setup, a best
   task-dependent static map matches dynamic optimization across 33 cases.
   Its proof explains why; it does not invalidate adaptive HLS generally.
3. **C6's positive finite-instance gap merits preservation:** it is explained
   by opportunity-conditioned anticipatory development coupled to later
   routing flexibility, and it appears under stationary as well as changing
   demand. It adds exact quantitative characterization consistent with prior
   G2/G3-H/RQ0 findings, not a new general theorem.
4. **E1 Nembhard and HLS-G0-C6 are different experiments.** The Nembhard
   E1 protocol uses its own experience/productivity model and 1,016-run
   registry; G0-C6 is a four-period exact G0/RQ0 experiment. Their names and
   results must not be conflated.
5. **Repeated source/model audits:** Nembhard, MixLLM, System-1.x and
   Chen/Baccara literature were reviewed in multiple targeted passes. This
   audit records the sequence but does not treat repeated reviews as multiple
   independent confirmations or reopen earlier decisions.

## 9. Remaining commitments evidenced through 30 October

The only remaining calendar commitments that can be stated as such are the
items still present in the cumulative operational plan, with their recorded
status: model-information definition (20 Oct, later router tasks absorbed),
MixLLM component review (21 Oct, source review completed but reproduction
blocked), router design/implementation items (22–23 Oct, recorded as absorbed
into the 17 Oct implementation), conditional compatible-policy integration
(26 Oct), Baccara/System-1.x review (27 Oct, documentary material exists),
ontology/architecture consolidation (28 Oct), exploratory protocol design
(29 Oct), and phase-closing report (30 Oct). The original baseline items and
their statuses are shown in the traceability table above. This is a status
reconstruction only; it does not add, reschedule or recommend work.

## 10. Evidence gaps and unresolved historical ambiguities

- No 18 October commit or uniquely dateable result artifact was identified;
  the plan itself documents resumption on 19 October.
- The provenance/approval chain for local, uncommitted 19 October audits and
  code is not represented by Git history. Their existence can be confirmed;
  canonical publication cannot.
- Nembhard E1 has a material status mismatch: contemporaneous incident record
  29 complete/987 pending versus later local 1,016-result tree and a recorded
  read-only validation. The local outputs are untracked; the exact completion
  event and any intervening execution instruction are not established here.
- The result files for E2.0/E2.1 and C6 are local/untracked; their mtime and
  embedded metadata support the dates/configurations but do not establish
  publication status.
- The user-supplied task stream authorizes several bounded actions, but not
  every authorization is separately captured in a committed decision log.
- Mtimes cannot reliably assign all uncommitted C4/CE16/configuration and
  teaching-proposal work to one of the three dates, and reports explicitly
  distinguish some of them from executed experiments.
- No activity on 20–30 October can be audited as completed at a 19 October
  cutoff; only the operational plan's outstanding status is available.

## 11. Source index

- Original and cumulative plan: [`HLS_ORIGINAL_WORK_PLAN_TO_2026-10-30.md`](HLS_ORIGINAL_WORK_PLAN_TO_2026-10-30.md), [`operational plan`](../engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md).
- Git chronology: commits `799eb45`–`a09dcc4` on 17 October; `e6ad5a8` and `8531b08` on 19 October; see local `git log --date=iso-strict`.
- Capability validation: [`report`](../experiments/HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md), [`JSON`](../../results/analysis/hls_lab_validation/integrated_validation_results.json), [`registry`](../../results/analysis/hls_lab_validation/capability_registry.json).
- Nembhard E1: [`protocol`](../experiments/HLS_NEMBHARD_ADAPTIVE_ALLOCATION_PROTOCOL.md), [`review`](../experiments/HLS_NEMBHARD_PROTOCOL_REVIEW.md), [`runner`](../../src/hls/nembhard_campaign.py), local `results/experiments/hls_nembhard_adaptive_allocation/` and `results/analysis/hls_e1/analysis.json`.
- E2: [`E2.0 script`](../../experiments/hls_e2/hls_e2_0.py), [`E2.1 script`](../../experiments/hls_e2/hls_e2_1.py), [`E2.1 protocol`](../experiments/HLS_E2_1_PROTOCOL.md), local results `../../results/analysis/hls_e2/`.
- G0-C6: [`exploratory report`](../experiments/HLS_G0_C6_EXPLORATORY_REPORT_2026-10-19.md), [`exact mechanism analysis`](../experiments/HLS_G0_C6_EXACT_MECHANISM_ANALYSIS_2026-10-19.md), [`closure`](../experiments/HLS_G0_C6_CLOSURE_2026-10-19.md), [`results`](../../results/experiments/hls_g0_c6/exploratory_results.json), [`runner`](../../experiments/run_hls_g0_c6.py).
- Literature, Chen, architecture and method selection reports are linked in §5.
