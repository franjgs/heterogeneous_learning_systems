# HLS Repository Reform Plan

**Status:** design proposal; no migration authorized or performed
**Prepared:** 2026-10-26
**Repository baseline inspected:** `feature/hls-laboratory-v1`, commit `9c3cb26986da506f8f4ac0f75da1fc70caf9b2c2`
**Scope:** scientific/documentary consolidation, result traceability, and a staged code-maintenance plan. This document does not select an article or open a research line.

## 1. Executive diagnosis

The repository contains a substantial, cumulative scientific programme, not one model or one experiment. At the forensic inventory baseline it contained 2,046 tracked files, 4,434 ignored physical files, 223 Markdown files, 527 Python files, 115 files under `src/hls/`, 249 experiment files, and 187 Python test files. The inventory covers 6,481 physical paths outside `.git`; these are census figures from the audit snapshot, not a claim that every file was read semantically. The six audit artifacts are now published on the working branch. See the [forensic audit](HLS_FORENSIC_REPOSITORY_AUDIT_2026-10-26.md), [file inventory](HLS_FILE_INVENTORY_2026-10-26.csv), and [comprehensive scientific audit](../HLS_COMPREHENSIVE_SCIENTIFIC_AUDIT_2026-10-26.md).

The principal maintenance problem is **distributed authority and provenance**, not simply file count. Several documents have legitimate, different responsibilities, but some navigation/status documents repeat conclusions or have not been reconciled with later dated records. In particular, the opening snapshot of [HLS_CURRENT_STATE.md](../../HLS_CURRENT_STATE.md) predates later CE-05 and CE-07 decisions/results in [HISTORY.md](../../HISTORY.md); the audit identifies the snapshot as stale relative to the later CE-07.5 report and CE-05 course correction. [research_questions.md](../../research_questions.md) still calls USE/DEVELOP “foundational beams,” contrary to the higher-level philosophy and doctrine that say it is one possible analytical decomposition, not HLS’s identity. These are substantive interpretation conflicts and should be fixed before rearranging material.

Evidence is unevenly accessible. The audit reports about 634 MB of tracked result files and about 9.46 GB of ignored result files, including raw traces and cached checkpoints. Important CE-04 task-level and causal logs are local-only; CE-07’s replica-metrics CSV is local-only although a tie trace is tracked. Some reported local Nembhard material is untracked and cannot be treated as published evidence. Several investigations also have distinct model semantics despite similar concepts or interfaces. Consolidation must therefore improve links and manifests while retaining separate models and their historical records.

The recommended target is a small authority layer, one machine-readable scientific registry with linked research and result records, and stable source documents. Historical protocols, reports, code, and data remain in place as primary evidence until a separately reviewed, reversible migration explicitly maps every source. No count of semantically redundant documents or duplicated algorithms has been established by filename similarity; the plan calls for content- and dependency-based triage before any consolidation.

## 2. Evidence base and limits

The published audit package consists of:

- [Forensic repository audit](HLS_FORENSIC_REPOSITORY_AUDIT_2026-10-26.md)
- [Tracked, ignored, and untracked file census](HLS_FILE_INVENTORY_2026-10-26.csv)
- [Experiment and evidence matrix](HLS_EXPERIMENT_EVIDENCE_MATRIX_2026-10-26.csv)
- [Theoretical results ledger](HLS_THEORETICAL_RESULTS_LEDGER_2026-10-26.csv)
- [Provenance and incident ledger](HLS_PROVENANCE_AND_INCIDENT_LEDGER_2026-10-26.csv)
- [Comprehensive scientific audit](../HLS_COMPREHENSIVE_SCIENTIFIC_AUDIT_2026-10-26.md)

The census distinguishes Git-tracked, ignored, and untracked paths. The experiment matrix indexes the major research families and their primary evidence; the theory ledger separates proof, exact finite computation, and conjecture; the incident ledger records access and provenance limitations. The audit explicitly does **not** claim semantic review of every physical file, recalculation of all result files, fresh test-suite status, complete external-literature priority, or clean replay where raw evidence is absent. Those limits govern this plan: an indexed item is not automatically validated, reproducible, or scientifically comparable.

The current philosophical authority is [HLS_PHILOSOPHY.md](../../HLS_PHILOSOPHY.md); the method authority is [RESEARCH_DOCTRINE.md](../../../RESEARCH_DOCTRINE.md). The four conceptual levels are Scenarios, Organizational Schemes, Models, and Performance Measures. The three-part mathematical representation in [HLS_UNIFIED_FRAMEWORK.md](../../architecture/HLS_UNIFIED_FRAMEWORK.md) remains a scoped formalization, not a replacement for the four-level architecture. Neither SOC nor a particular simulator belongs in the definition of HLS.

## 3. Structural diagnosis

### 3.1 Confirmed issues

| Issue | Evidence and scale | Reform implication |
|---|---|---|
| Multiple documents summarize overlapping status | Philosophy, doctrine, current state, history, repository guide, research questions, execution plans, and campaign reports have distinct authority roles, but the audit found stale status wording and at least one foundational-framing conflict. | Preserve role separation; make summaries link to evidence and reconcile claims instead of copying report text. |
| Status drift | The dated current-state introduction omits the later CE-05 course correction and CE-07.5 confirmatory outcome recorded in history and primary report. | Update status only from dated decisions and result sources; do not rewrite historical entries. |
| Ignored result volume | Audit census: about 9.46 GB of ignored results; local total about 9.5 GB versus about 634 MB tracked. | Define artifact tiers and manifests; do not bulk-add raw files. |
| Evidence access varies by line | CE-04 raw task traces and causal raw logs are local-only; CE-07 replica metrics are local-only; Nembhard local completion claim is untracked. | Mark evidence as local-only/unverified until independently published with provenance. |
| Many semantically distinct implementations | `src/hls/` has 115 tracked files; N×K, CE-04, exact finite solvers, routing, learning/teaching, and contextual paths embody different assumptions. | Modularize by scientific contract; share code only after semantic compatibility is demonstrated. |
| Experimental packaging varies | The experiment matrix shows differences in protocols, execution records, metrics, manifests, source hashes, and retained raw artifacts; some studies have interrupted or corrected runs. | Normalize metadata/provenance envelopes without converting historical estimands or outcomes. |
| Navigation burden | 223 tracked Markdown documents and 225 docs paths at audit baseline, besides code and results. The repository guide already maps many authorities but contains stale status descriptions. | Keep detailed primary documents; shorten navigation through registries and links, not wholesale summarization. |

### 3.2 Suspected but not yet quantified

The audit did not establish a repository-wide count of true document duplicates, broken Markdown links, cyclic dependencies, or duplicate code. Similar titles and shared vocabulary are not evidence of duplication. During migration, candidate overlap must be demonstrated by content comparison and dependency/use analysis (including Git history and tests). Generated, cache, and temporary files must be identified from actual ignore rules and provenance, not removed because their names look temporary.

### 3.3 Canonical conflicts to resolve first

1. `docs/research_questions.md` frames USE/DEVELOP as foundational beams, while `docs/HLS_PHILOSOPHY.md` and `RESEARCH_DOCTRINE.md` state that HLS is broader and does not require that decomposition. The research-question entry must be reframed as a scoped official question without changing its historical origin or pretending the question itself was never used.
2. The current-state opening snapshot must be reconciled with dated later decisions and reports, including CE-05’s course correction and the corrected CE-07 confirmatory record. It must not turn local-only artifacts into public evidence or silently promote proposals to decisions.
3. The repository guide and README should be checked against the corrected authority/status map. They are navigation sources, not independent evidence authorities.
4. The formal four-level conceptual architecture and the three-part mathematical framework should be cross-linked with an explicit scope note, not mechanically merged.

## 4. Scientific line classification

This classification follows the experiment and theory matrices and primary reports. “Closed” is a decision about continuation, not deletion or invalidation of results. Research status and evidence status are separate fields in the proposed registry.

| Research family | Knowledge retained and evidence type | Limits / current disposition for reform |
|---|---|---|
| M0/M0.1, H1, CR0–CR4, CIV; portfolio prioritization | Exact identities, finite checks, thresholds, nulls, and rank reversals. | No universal failure-frequency × quality-gap priority statistic. Retain as historical diagnostic foundations; do not present as a validated selector. |
| B1/B2/B12, PACS, Office-Home and vehicle gates | Bounded mechanism and source-reproduction work, feasibility checks, and negative/inconclusive gates. | B2.1–B2.2 compatibility failed; B2.3 inconclusive; B2.4 scoped interference/replay. A named implementation is not automatically a faithful reproduction. Preserve STOP outcomes and source mappings. |
| A1/G0/C1–C6; T0–T6; G1–G3/G3-H; RQ0 | Formal definitions, exact finite results, reductions, sufficient conditions, and counterexamples. | Some claims reduce to standard assignment/DP or policy-class inclusion; strict results remain assumption- and family-scoped. No universal HLS law. Maintain theory source files and proof status. RQ0’s status needs reconciliation with current PI direction before any label is changed. |
| Campaign 0–1 / MIS and teaching | Bounded synthetic learning/teaching results, opportunity-cost and demand/timing diagnostics. | Outcomes vary by scenario, action granularity, horizon, and comparator; not general policy superiority. Keep campaign estimands separate from later N×K/CE routes. |
| Campaign 2: prospective adaptation and realized consequence | 5,120 validated runs; state-conditioned contrasts include positive and near-zero/inconclusive cases; strict coupling was rare in the recorded state set. | Not a complete training-versus-no-training policy evaluation or population law. Preserve exact source report and its sampling frame. |
| Campaign 3: META-VOC / value of computation | Bounded positive META-VOC-versus-RANDOM history contrast and compute reduction; held-out G3/G4 do not show a demonstrated production advantage. | Unequal invocation frequencies, selected primary point after development inspection, weak predictor validity. No general detector or algorithmic novelty established; line decisions remain scoped to documented NO-GO/hold. |
| Campaign 4 | Engineering/protocol verification. | Proposed N=800 scientific evaluation did not run; do not register it as a result. |
| S1–S7 and S3b | Exact finite assignment/planning comparisons, temporal/separability constructions, partial-information and observation-dependence evidence. | Scope differs by model. S3b has a narrow memory benefit in one replay cell and inconclusive closed-loop intervals. Do not pool estimands. |
| N×K, MIS-v2, teaching, experience, Nembhard | Implemented/validated component paths and bounded experiment records. | Different learning laws and feedback semantics; Nembhard E1’s tracked 29/1,016 incident conflicts with a local untracked completion claim. No complete public replay claim for the latter. |
| Budgeted LLM routing, classifier fusion, MMLU/DCS-LA | Predictor and assignment comparisons, exact/small pilots, corrected MMLU evidence. | One ILP cell has a limited advantage; DCS-LA difference is inconclusive; cascades did not establish a general advantage. Prior lines stay closed unless a separately justified new question is approved. |
| CE-01 deliberation | Existing-data assessment and paired FAST/DEEP complementarity analyses. | No conditioned review `D(x,F(x))`; independent answers are not revisions. No new causal claim. |
| CE-02 AI aging | Exact synthetic dependence control and partial temporal-benchmark preflight. | No real model inference; scientific originality not established; NO-GO for immediate candidate, while the phenomenon itself is not declared irrelevant. |
| CE-03 transfer H3 | V1/V2 synthetic transfer tests and diagnostics. | V1 had leakage; corrected V2 contrasts were inconclusive. Preserve both with distinct protocol status; do not treat as confirmation. |
| CE-04 and CE-04 causal diagnostic | Confirmatory queued/deadline synthetic campaign and a separate H2 calibration/load intervention; fully validated counts and scoped effects in reports. | No cooperation; one specified model and composition range. Diagnostics do not establish mediation or real SOC effects. Raw logs are partly ignored/local-only. |
| CE-06 heterogeneity diagnostics | Reanalysis of 90 CE-04 P1/N=24 replicas plus nine technical-pilot replicas; descriptive metrics. | Reanalysis is not independent replication; pilot is not confirmatory; congestion mediation is not identified. |
| CE-07 joint competence structure | 30 matched confirmatory pairs, 60 valid simulations; B−A +21.52 pp in a fixed P1, N=12 stationary setup with equal marginal summaries and different joint matrices. | One pair of structures, one policy and one scenario; no general specialization/structure law. First invalid nonstationary attempt and pilot remain archived but excluded from stationary evidence. |

The numerical summaries above are pointers, not replacements for primary reports. The matrix rows and linked sources define the assumptions, uncertainty, run counts, and exact claims. The audit does not select a “promising” line or recommend reopening a closed one.

## 5. Canonical scientific architecture

Organize information by the scientific object it describes, while preserving model-specific semantics:

```text
HLS programme
├── Scenarios       problems, demand, environment, information, constraints
├── Organizations   agents, capability distributions, structure, allocation form
├── Models          state, transitions, observation, objective, assumptions
├── Policies        decision rules, learning, cooperation, planning mechanisms
├── Evaluation      outcomes, comparators, protocols, statistical analysis
├── Evidence        proofs, executions, results, provenance and limitations
└── Applications    domain mappings and domain-specific evidence
```

The first six categories map to the four conceptual philosophy levels plus cross-cutting policy/evidence concerns; they are a repository organization, not a replacement scientific ontology. **Policy is a model component or organizational implementation, not an additional foundational HLS level.** A scenario may pair with multiple organizations/models; a policy can only be compared when information, feasibility, and objective contracts are stated; evidence belongs to a precise configuration and estimand. Application records map a real domain onto HLS objects without changing HLS’s general identity.

The repository must not require a universal simulator. Existing N×K, G1/G2/G3, CE-04, MMLU, PACS, and other model families may remain separate where they encode different transition laws, tasks, objectives, or information. A common run envelope can carry identifiers, units, seeds, code/configuration hashes, and artifact links; it must not claim cross-model metric equivalence or convert historical outputs.

## 6. Minimal document and registry architecture

### 6.1 Human-readable authority layer

Retain and clarify existing documents rather than create parallel prose authorities:

| Purpose | Canonical source | Rule |
|---|---|---|
| Entry and navigation | `README.md`, `docs/REPOSITORY_GUIDE.md` | Point to authorities and registries; do not duplicate detailed findings. |
| Identity and scope | `docs/HLS_PHILOSOPHY.md` | Stable philosophy; no application-specific or experiment status. |
| Methodology | `RESEARCH_DOCTRINE.md` | Problem-first and evidence rules; no current-result ledger. |
| Terms and mappings | `docs/hls_ontology.md` | Definitions and cross-domain mappings with scope, not universal equations. |
| Official research questions | `docs/research_questions.md` | Question status and scope; align wording with philosophy, preserve chronology. |
| Current scientific state | `docs/HLS_CURRENT_STATE.md` | Concise verified snapshot, linked to records; never a second full history. |
| Chronology | `docs/HISTORY.md` | Append-only decisions/events with event date distinct from record/commit date. |
| Research and result index | One structured registry (below) | Stable IDs and links to primary reports, code, tests, configurations, results. |
| Formal theory | Existing theory files and `docs/theory/README.md` | Proofs and assumptions stay with the exact model; index status only. |
| Literature | Existing `docs/literature/README.md` and `references.bib` | Retain source audits and citation provenance; no repeated literature summaries in status. |
| Experiment detail | Protocols and primary reports under existing experiment/research paths | Immutable historical records; current state links to them. |

Use the published forensic/comprehensive audits as a dated audit package, not as new living status authorities. Archive/hide older plans from active navigation only after their remaining decisions, evidence, and links are represented; do not move or delete them in the first migration.

### 6.2 One structured research-and-result registry

Create one versioned, machine-readable registry, proposed path `docs/registry/hls_scientific_registry.jsonl`. The registry contains two record types in the same file—`research` and `result`—so experiment discovery and evidence status are normalized without repeating prose. This is a future design, not created in R1. JSON Lines supports incremental records, ordinary review diffs, and standard-library parsing; no runtime dependency is required.

**Research record fields (minimum):**

```json
{"schema_version":"1.0","record_type":"research","id":"CE-07","name":"Joint competence structure","question":"...","hypotheses":["..."],"scenario_refs":["..."],"organization_refs":["..."],"model_refs":["..."],"policy_refs":["..."],"protocol_refs":["..."],"result_refs":["..."],"research_status":"closed|active|suspended|pending|discarded","evidence_status":["confirmatory","exploratory","negative","technical_validation","not_verified"],"limitations":["..."],"dates":{"event":"2026-10-26","execution":"...","decision":"..."},"sources":[{"path":"docs/research/CE-07/04_CONFIRMATORY_RESULTS.md","section":"..."}],"relations":[{"type":"reuses","id":"CE-04"}],"application_refs":[]}
```

**Result record fields (minimum):**

```json
{"schema_version":"1.0","record_type":"result","id":"CE-07-R1","research_id":"CE-07","claim":"...","result_kind":"formal_proof|exact_computation|confirmatory|exploratory|negative|inconclusive|technical_validation","estimand":"...","value":"...","uncertainty":"...","unit_of_analysis":"replica","configuration":"results/.../config.json","code_commit":"...","config_hash":"...","artifact_manifest":"results/.../manifest.json","raw_artifact_status":"tracked|external|local_only|regenerable|missing","source":"docs/research/CE-07/04_CONFIRMATORY_RESULTS.md#...","scope_and_nonclaims":["..."]}
```

The example values are illustrative schema values, not asserted record contents. Do not coerce evidence into one status: a research item may be closed while containing a valid confirmatory result and a separate unresolved mechanism. Use explicit enums, null for genuinely unknown dates, and provenance references. Every numerical result must point to the report/table and primary data or manifest. Results from separate models or estimands stay separate records.

No hand-maintained generated “results summary” should duplicate the registry. A compact Markdown results index can be generated from it only if generation is deterministic, output is checked in, and CI validates that the checked-in view matches the source; otherwise link directly to the registry and primary reports. Schema validation should initially use a small standard-library script or existing tooling, without a new dependency.

### 6.3 State and date semantics

Use separate research-state and evidence-state vocabularies. Suggested research states: `active`, `closed`, `suspended`, `pending`, `discarded`. Suggested evidence labels: `formal_proof`, `exact_computation`, `confirmatory`, `exploratory`, `inconclusive`, `negative`, `technical_validation`, `not_verified`. A line can be `closed` with positive, negative, or mixed evidence. Distinguish event, execution, decision, documentation, and Git commit dates; do not infer scientific dates from commit timestamps.

## 7. Code and experiment architecture

The forensic audit found useful components but no shared universal semantic model. Preserve this boundary while making dependency direction explicit:

```text
src/hls/
  shared/       validated contracts, units, RNG/keying, serialization only
  models/       model-specific state and transition semantics
  policies/     reusable policies only when information/action contracts match
  evaluation/   metrics/statistics that preserve estimand and units
experiments/<stable-research-id>/
  protocol reference, runner, tests/adapters, analysis entry point
results/<stable-research-id>/
  lightweight config, manifest, aggregate tables, hashes, provenance
```

This is a target boundary, not an instruction to move files immediately. Candidate reusable surfaces from the audit include N×K geometry/production/execution (`src/hls/hls_lab_nk_*`), dynamic environments, CE-04’s SimPy event loop, exact finite solvers, learning/estimation/teaching modules, contextual methods, `experiment_contract.py`, and `performance_evaluation.py`. Their validation is route-specific. CE-04 queues/deadlines, per-period N×K budgets, finite DP, MMLU query routing, and PACS pilots are not interchangeable merely because they assign work or report success.

Before extracting a shared component, require: identical mathematical meaning, units, observation timing, information available at decision time, failure/deadline semantics, RNG coupling, resource accounting, and metric denominator. If any differs, keep separate implementations and offer a narrow adapter or explicit translation; never make an adapter rewrite historical result files. Prefer thin wrappers around verified source modules over a new general framework.

Code disposition categories for a later audited pass:

- **Core candidate:** exercised by multiple scientific routes with matching contracts and tests.
- **Model-specific:** scientifically meaningful but tied to one transition/reward/information model; retain in that model module.
- **Experiment-specific:** runner, fixture, and analysis belonging to one registered study.
- **Semantically incompatible:** parallel implementation that must remain separate.
- **Historical/reproduction-only:** retained to reproduce or explain a closed line.
- **Unverified/obsolete candidate:** no deletion until references, tests, manifests, and Git history establish it is unused and scientifically unnecessary.

No implementation is classified as a duplicate solely because symbols or interfaces resemble one another. Duplicate detection should use code similarity plus call graphs, configuration/schema comparison, test behavior, and report dependency. Every consolidation should preserve a compatibility route or exact reproduction entry for published/frozen results.

## 8. Result conservation and reproducibility policy

### 8.1 Artifact tiers

1. **Tier 1 — Git-tracked essential evidence:** protocol, analysis source, frozen config, environment/dependency lock or version manifest, per-replica aggregates, statistical outputs, tests/validation summary, and a manifest with hashes. Keep small enough for review.
2. **Tier 2 — External immutable artifacts:** large row-level logs, datasets, checkpoints, or traces. Store in an approved durable location; publish stable URI/identifier, size, license/access note, SHA-256, schema/version, and generation commit. A path on one workstation is not an external artifact.
3. **Tier 3 — Regenerable intermediates:** caches and temporary files. Exclude from Git; record exact regeneration command and source hashes only when scientifically necessary.
4. **Tier 4 — Unrecoverable or provenance-insufficient:** mark `missing`/`not_verified`; do not imply replay or promote dependent claims beyond the accessible evidence.

Never bulk-add the 9.46 GB ignored result tree. Check licensing and sensitive content before publishing any dataset or trace. Large artifacts need both immutable storage and a repository manifest; a checksum alone does not supply access.

### 8.2 Required result manifest

Each run or campaign manifest should identify stable research/result IDs; protocol version; exact conditions and seed set; RNG stream derivation; repository commit; configuration hash; code entry point; dependency/runtime versions; execution command; host/hardware for cost-sensitive work; validation/test status; artifact paths, byte sizes and SHA-256; and the statistical unit. Record raw output availability separately from aggregate availability. For paired designs, include scenario/potential-outcome keys and checks verifying common exogenous realizations.

### 8.3 Historical integrity

Treat scientific reports and frozen configurations as immutable evidence. Corrections should be appended or issued in a new dated report linked to the superseded attempt; preserve failed, negative, and protocol-deviation artifacts. Do not silently update old figures, delete result folders, or claim exact reproducibility when source hashes, raw traces, or environment data are incomplete. Existing source-hash mismatches, V1 leakage, false-validator incidents, nonstationary CE-07 attempts, and local-only outputs remain linked incidents, not cleanup opportunities.

## 9. Applications and SOC boundary

Keep applications downstream of the general HLS framework:

```text
HLS concepts and methods
        ↓ explicit mapping + domain assumptions
Application model (SOC first)
        ↓ domain evidence and validation
Application-specific conclusions
```

The SOC can map analysts to heterogeneous capabilities, incidents to tasks/demand, queues and SLAs to temporal/resource constraints, organization to assignment/cooperation, and training/experience to capability change. Each mapping requires a declared operational definition and evidence. Existing CE-04/06/07 queued synthetic models can inform mechanisms and metric design; they do not validate real SOC data, analyst skill estimates, incident arrival laws, SLA costs, or policy effectiveness. No verified SOC dataset or causal operational evidence is established by the audit.

Application modules should state: domain question; mapping of entities/capabilities/tasks; source and licensing of data; domain-specific constraints and outcome semantics; which HLS model/policy is reused or adapted; calibration/validation evidence; and which conclusions do not transfer back to general HLS. SOC is first in application priority, not an architectural root and not an instruction to select an article in R1. Other applications remain possible if a concrete, evidenced mapping exists.

## 10. Migration sequence — proposal only

Each phase is a separate reviewable change. No phase starts automatically by acceptance of this plan. The initial phases are reversible through Git; deletion or result conversion is excluded unless a later explicit review proves exact recoverability.

| Phase | Files / transformation | Dependencies and risks | Checks and acceptance | Reversal |
|---|---|---|---|---|
| **1. Authority and contradiction repair** | `docs/research_questions.md`, opening snapshot and source links in `docs/HLS_CURRENT_STATE.md`, status tables in `docs/REPOSITORY_GUIDE.md`, `README.md`. Reconcile RQ0/USE-DEVELOP framing and update current status only from dated decisions and reports. | Must read higher-authority philosophy/doctrine and verify latest CE decisions. Risk: converting proposals to approvals or history into current truth. | Every current claim cites dated primary evidence; research question scope no longer contradicts philosophy; history unchanged; local-only evidence labeled. | Revert this documentation-only commit; preserve source reports. |
| **2. Canonical scientific registry** | Add `docs/registry/hls_scientific_registry.jsonl` (one source file, research and result records); populate a first pass from experiment/theory matrices and authoritative source links. | Registry IDs must map to existing stable line identifiers; many results need source review. Risk: false completeness and status compression. | Every major line in the experiment matrix has an ID, status on both axes, source, limitation, dates as known; all referenced files exist; unknowns explicit. | Remove registry in its own commit or revert; no source changes. |
| **3. Navigation simplification** | `README.md`, `docs/REPOSITORY_GUIDE.md`, `docs/experiments/README.md`, `docs/theory/README.md`, literature index. Replace repeated prose with role descriptions and links to registry/primary sources. | Requires Phase 1–2. Risk: hiding details from new readers. | A route from question → model → protocol → code/tests → results is available for each major line; no source-only knowledge lost. | Restore prior navigation text; links remain additive. |
| **4. Document redundancy triage** | Candidate status summaries, repeated overview notes, superseded plans, and duplicate summaries identified by exact hash/content/dependency comparison. Mark historical/supporting status or point to the canonical source; do not delete/move in this phase. | Requires path-level inventory and registry. Risk: mistaken equivalence based on title or partial overlap. | Each altered file has a documented disposition and surviving source; content diff reviewed; no proof, caveat, or negative result lost. | Revert each file disposition independently. |
| **5. Experiment/result normalization** | Campaign manifests, configuration and result indexes; add missing lightweight metadata or provenance notes in new dated records. No raw historical outputs rewritten. | Requires artifact availability, result ownership, hashes, storage target and license review. Risk: an inaccessible raw artifact cannot be reconstructed. | Each campaign is labeled executed/partial/not run; replica unit, estimand, protocol, commit/config and evidence tier are explicit; replay claims validated only where possible. | Revert new manifests/index entries; keep original campaign files untouched. |
| **6. Code modularization** | Selected `src/hls/` families and experiment entry points, only after semantic audit; thin shared utilities/contracts where proven. | Requires passing route-level tests and explicit behavior contracts. Risk: changing RNG order, deadlines, queues, feedback, objective, or historical outputs. | Before/after golden fixtures or exact replay for affected routes; all relevant tests pass; scientific configuration hashes and archived outputs unchanged; no universal semantics imposed. | Keep original implementation and switch runner/import back; one module family per change. |
| **7. Full structural validation** | Validate registries, links, manifests, status summaries, tests, and clean-clone reproduction map. | Requires prior phases and access to external artifacts. Risk: external access or licensed data unavailable. | CI/read-only checks detect broken links/IDs, schema errors, undocumented status claims, dirty generated views, missing hashes; reproduction limits visibly listed. | Revert validation tooling independently; do not remove raw evidence. |

### Acceptance gate across all phases

- No primary protocol, proof, result report, negative finding, failure record, or historical decision is removed or silently rewritten.
- Every condensed claim points to its source and states evidence class and scope.
- A clean reader can traverse question → model → scenario/organization → policy → protocol → configuration → result → conclusion.
- Cross-study numerical pooling is prohibited unless the estimand, metric units, population, and dependence structure are demonstrably compatible.
- Each phase changes only its listed files and is reviewed before the next begins.

## 11. Risks, dependencies, and open decisions

### Risks

- **False unification:** merging models with different capability, feedback, deadline, or objective semantics could make results incomparable.
- **Evidence loss:** moving/condensing documents can drop assumptions, negative results, or incident context.
- **Status laundering:** a proposal, technical validation, local result, or exploratory contrast could be relabeled confirmatory.
- **Reproducibility overclaim:** most ignored raw outputs are not in Git; source/environment drift may block exact replay.
- **Registry burden:** a machine-readable index can become another stale authority unless validation and ownership are assigned.
- **Application overreach:** synthetic CE results do not substantiate claims about operational SOC teams.
- **Code regression:** shared RNG, queue, and logging utilities may change historical behavior even when interfaces look identical.

### Dependencies before migration

1. Treat the forensic audit and its baseline date as an evidence map, not a fresh exhaustive validation.
2. Resolve current-state/history/research-question authority conflicts from primary records.
3. Decide who owns registry IDs, review cadence, and status changes (PI/CE roles already documented in governance sources; do not create new roles here).
4. Identify durable external artifact storage and access/licensing rules before making raw results “available.”
5. For each code extraction, identify exact dependent experiments, tests, configs, source hashes, and required replay scope.

### Decisions that remain for PI/CE

- Approve or reject the staged migration and its ordering; this plan itself authorizes no migration.
- Determine whether RQ0 remains the sole official question or whether the official question registry should reflect a broader portfolio; the philosophy is superior on HLS identity, but the PI owns scientific priority.
- Approve a stable identifier convention for research/results and the single registry format/path.
- Select a repository-approved durable store for large artifacts and define public/private access rules.
- Decide whether code changes should be separately gated by exact reproduction requirements for each route.
- Define SOC data-access and validation requirements before making domain-level claims.

## 12. Conclusion

The appropriate reform is not to compress HLS into one simulator or one “best” research line. It is to establish a clear authority layer, resolve known status/framing conflicts, index each research item and result with explicit evidence status and provenance, simplify navigation, and only then consolidate documents or code when semantic equivalence is demonstrated. Preserve the finite theories, distinct models, positive and negative findings, failed attempts, and inaccessible-artifact warnings as part of the scientific record. The SOC belongs as a prioritized application mapping with domain-specific validation, not as the definition of HLS.

This is the sole deliverable of R1. It proposes a migration sequence and stops before refactoring, file moves, result changes, or new research.
