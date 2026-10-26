# HLS forensic repository audit

**Audit date:** 2026-10-26
**Repository:** franjgs/heterogeneous_learning_systems
**Branch / HEAD:** feature/hls-laboratory-v1 / bdc0dab2075dc786c93223c10f76a0c27c9758e5
**Mode:** read-only inspection; no experiments, simulations, tests, code edits, or source/result/document changes. The only created files are this audit package under this directory.

At this baseline, local feature branch and origin/feature are aligned; origin/main is at `2e3c4f3caf52f1bea14bb155312e1a0f72117f71`, with 39 commits from that main tip to HEAD and none on main absent from this branch. The recorded Git history contains 278 commits from the 2026-09-14 initial commit through the CE-07 provenance-refresh commit at 2026-10-26 17:42:31 +01:00. These are repository commit times, not necessarily scientific decision times.

## 1. Scope, authority, and evidence rules

This audit reconstructs the evidence physically present in the worktree at the stated HEAD, using the authority hierarchy in [REPOSITORY_GUIDE](../../REPOSITORY_GUIDE.md): [philosophy](../../HLS_PHILOSOPHY.md), [doctrine](../../../RESEARCH_DOCTRINE.md), [ontology](../../hls_ontology.md), [official research questions](../../research_questions.md), [current state](../../HLS_CURRENT_STATE.md), [theory registry](../../theory/README.md), experiment registries, primary reports, source, tests, and result artifacts. [HISTORY](../../HISTORY.md) supplies chronology, not current status. Frozen protocols and result artifacts govern their own scope.

The user-supplied starting document, [HLS_COMPREHENSIVE_SCIENTIFIC_AUDIT_2026-10-26.md](../HLS_COMPREHENSIVE_SCIENTIFIC_AUDIT_2026-10-26.md), is physically present but **untracked** at this audit baseline. It is not part of HEAD/origin and is not a canonical evidence source. Its substantive claims were treated as leads and cross-checked against tracked source documents; its article recommendation was deliberately not adopted because this task excludes article selection.

The audit distinguishes:
- **Formal result:** proof/identity/counterexample in a mathematical source, under its stated assumptions.
- **Exact computational result:** exhaustive or deterministic calculation in a finite declared model; not automatically a theorem about other models.
- **Experimental evidence:** outcome from a registered or described run; statistical unit and sampling frame matter.
- **Technical validation:** tests, trace integrity, replay, or implementation checks; not evidence of scientific superiority.
- **Interpretation / hypothesis:** explanatory reading not identified by the design.
- **NO VERIFICADO:** absent source, unavailable raw trace, unresolved provenance, or no executed evidence.

No outside literature search was run. The literature assessment reports only comparisons documented in repository sources; it does not claim exhaustive priority.

## 2. Repository coverage and material inventory

At inspection there were **2,046 tracked files**, **one untracked file** (the auxiliary audit above), and **4,434 ignored files** in the physical worktree. The file-level inventory records path, status, and bytes for 6,481 files in [HLS_FILE_INVENTORY_2026-10-26.csv](HLS_FILE_INVENTORY_2026-10-26.csv); it intentionally excludes the audit products created afterward so that it preserves the repository baseline. Tracked files comprise 223 Markdown documents, 527 Python files, and substantial JSON/CSV/JSONL/compressed outputs. Tracked result files total about 634 MB. Local results occupy about 9.5 GB; about 9.46 GB of result files are ignored and therefore not supplied by a normal clone. The largest are cached model checkpoints, raw campaign traces, temporary Monte Carlo outputs, and analysis caches. Their individual paths/status/size are listed in the inventory.

The source tree has 115 tracked files under src/hls; experiments has 249 files; tests has 187 Python files; docs has 225 files. This is a file census, not a claim that every historical result has a complete reproducible bundle. No tracked data/ directory exists. The full primary-source map is [REPOSITORY_GUIDE](../../REPOSITORY_GUIDE.md); campaign-specific code, protocol, tests, and evidence are cross-indexed in the experiment matrix.

### Canonical framing

HLS is a general scientific programme about organization, use, combination, and evolution of heterogeneous capabilities. Its conceptual architecture is **Scenarios → Organizational Schemes → Models → Performance Measures**; HLS-PEF is an instrument within performance evaluation, not a fifth level or the programme itself. The three-part mathematical decomposition in [HLS_UNIFIED_FRAMEWORK](../../architecture/HLS_UNIFIED_FRAMEWORK.md) is a model-level representation and can coexist with the four-level scientific architecture. The doctrine requires problem-first work, fair comparators, explicit assumptions, evidence-limited claims, and reduction to established theory before invention.

S1–S7 are problem/scenario families. TR-PR, TR-PM, TR-G, TR-J, TR-R, TR-D, TR-HA and TR-HB are demand/problem histories used by the Campaign 1–3 track. They are not scenario IDs. No canonical S8 exists. These distinctions and the authoritative source paths are stated in [HLS_CURRENT_STATE](../../HLS_CURRENT_STATE.md), §§ “Scenario inventory” and “Other research lines and demand histories.”

The [research-question registry](../../research_questions.md) keeps RQ0 as the official programme question, while CE-labelled work records operational research tasks and bounded studies. This is a hierarchy distinction; RQ0 and CE-04/06/07 results are not interchangeable estimands.

## 3. Scientific programme reconstructed chronologically

The dated record begins at the 14 September 2026 initial commit. The early programme tested a portfolio-investment framing: local failure frequency and quality gap as possible indicators of capability improvement. M0/M0.1, H1, CR0–CR4 and CIV generated scoped identities, thresholds, nulls, and rank reversals; they did not establish a universal training-priority statistic. The project then assembled cross-domain foundations and executed B1/B2/B12 and PACS/Office-Home feasibility work. Important negative knowledge is preserved: B2.1–B2.2 counterfactual compatibility failed; B2.3 remained inconclusive under its rescue criterion; B2.4 gives bounded interference/replay evidence; vehicle gates stopped rather than laundering infeasible data as results. See [HISTORY](../../HISTORY.md), §§1–5; [current state](../../HLS_CURRENT_STATE.md), historical portfolio; [literature and model dossiers](../../literature/README.md), [scientific model dossier](../../engineering/HLS_SCIENTIFIC_MODEL_DOSSIER.md).

The next period built finite exact synthetic worlds: A1a–c, G0, C1–C6, T0–T6, G1–G3/G3-H and RQ0. It established distinctions between individual competence, attainable collective capability, organizational accessibility, and realized outcomes. Some proposed integrations reduced to known assignment/look-ahead/DP structures; some finite witnesses showed strict differences. The result is a collection of scoped exact models and reduction boundaries, not a universal HLS formalism. See [theory registry](../../theory/README.md), [HISTORY](../../HISTORY.md), and [HLS_CURRENT_STATE](../../HLS_CURRENT_STATE.md), especially §§ “Static theoretical foundation,” “Dynamic theoretical foundation,” and RQ0.

Campaign 0–4 studies then investigated teaching/MIS, partial information, prospective adaptation, fast/deep computation and deliberation. Campaign 1 exposed strong dependence on demand, horizon, action granularity, MIS and comparator; Campaign 2 separated prospective preferences from realized short-horizon consequences; Campaign 3 developed a sequential adaptive-computation line with a positive bounded META-VOC versus RANDOM contrast but weak statewise predictor validity and no demonstrated gain on held-out G3/G4. Campaign 4 remained a protocol/engineering gate and did not run its proposed N=800 evaluation. See [Campaign 1](../../experiments/CAMPAIGN_1_RESULTS.md), [Campaign 2](../../experiments/CAMPAIGN_2_RESULTS.md), [Campaign 3 confirmatory](../../experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md), [predictor validity](../../experiments/META_VOC_PREDICTOR_VALIDITY_REPORT.md), [Campaign 4 verification](../../experiments/CAMPAIGN_4_ENGINE_VERIFICATION.md).

The October 24–26 applied/synthetic lines include CE-01 deliberation data assessment, CE-02 exact AI-aging control, CE-03 transfer-to-collective-performance V1/V2, CE-04 dynamic assignment/heterogeneity, CE-06 post-hoc diagnostics, and CE-07 joint competence structure. CE-04/06/07 are complementary but non-identical designs: CE-06 reuses CE-04 records; CE-07 changes the structural contrast and stationary demand; their effects must not be pooled. CE-01 lacks answer-conditioned review; CE-02 has no real inference; CE-03 is statistically unsupported in the tested synthetic setup. See the relevant CE reports listed in the experiment matrix.

### Literature and reproduction records

The bibliography is [docs/literature/references.bib](../../literature/references.bib), indexed by [docs/literature/README.md](../../literature/README.md), with comparative audits under [docs/literature/audits/](../../literature/audits/) and targeted formal analyses in [HLS_SCIENTIFIC_NOVELTY_AUDIT_2026-10-19.md](../HLS_SCIENTIFIC_NOVELTY_AUDIT_2026-10-19.md), [HLS_BACCARA_CHEN_FORMAL_COMPARISON_2026-10-19.md](../HLS_BACCARA_CHEN_FORMAL_COMPARISON_2026-10-19.md), and [HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md](../HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md). The published-method screening document compares six candidate sources and records STOP before a faithful reproduction was authorized; it does not establish that every named HLS mechanism reproduces the corresponding publication. The primary literature accessible in the repository includes Chen et al. (2018) full text; the Baccara et al. and other comparisons are documented with the source-access limits stated in their audits. The current formal mapping is in [hls_ontology.md](../../hls_ontology.md); imported concepts remain discipline-specific rather than being treated as exclusive foundations.

### Manuscripts and contribution records already present

The repository contains two foundations working-paper versions at [v0.1](../../publications/hls_foundations_v01/hls_foundations_v01.tex) and [v0.2](../../publications/hls_foundations_v02/hls_foundations_v02.tex), plus the [conditional prospective deliberation manuscript](../../paper/conditional_prospective_deliberation/main.tex) and a separate [META-VOC scientific record](../../paper/META_VOC_SCIENTIFIC_RECORD.md). The 2026-10-19 [novelty audit](../HLS_SCIENTIFIC_NOVELTY_AUDIT_2026-10-19.md) gives an ADJUST verdict to the broad integrated claim and identifies prior-art threats; it does not supply a distinct readiness verdict for each v0.x version. This is a recorded prior-art assessment, not an experimental result. The prospective-deliberation paper is a draft tied to Campaign 3; the source map marks literature review, discussion and LaTeX manuscript as pending in its paper-readiness table, while the later META-VOC record contains a publication-positioning section. These status records differ by document date and scope; they do not establish a submission-ready manuscript or a final novelty decision. This audit does not select among them or propose an article. See [paper source map](../../paper/PAPER_SOURCE_MAP.md), [claim-evidence ledger](../../paper/CLAIM_EVIDENCE_LEDGER.md), [literature needs](../../paper/LITERATURE_NEEDS.md), and [META-VOC record](../../paper/META_VOC_SCIENTIFIC_RECORD.md).

## 4. Experiment and result reconstruction

The row-level campaign matrix is [HLS_EXPERIMENT_EVIDENCE_MATRIX_2026-10-26.csv](HLS_EXPERIMENT_EVIDENCE_MATRIX_2026-10-26.csv). It records question, source code/protocol, conditions and replica counts where verified, estimand/outcome, uncertainty, limits, and primary artifacts. It covers the portfolio/M0/CIV line; B1/B2/B12 and PACS; vehicle gates; A1/G0/C1–C6; T0–T6/G1–G3/RQ0; Q1; Campaigns 0–4; S1–S7; S3b; N×K and Nembhard; LLM budgeted routing; classifier fusion; MMLU/DCS-LA; and CE-01–CE-07.

Selected confirmatory or exact outcomes, with the authoritative reports retained:

| Study | Verified result | What it supports / does not support |
|---|---|---|
| S1/S2a/S2b | Finite exact assignment: 2.60 vs greedy 1.80; S2a exact/global 8.0 vs greedy 7.2 with 84,388 sequences; S2b Bellman 1.00 vs myopic .90 and sufficient-budget control 1.90. | Exact instance properties; not general planner superiority. [Current State scenario table](../../HLS_CURRENT_STATE.md). |
| S3b-E1 | Shared-observation WINDOW benefit only in infrequent-change/high-feedback cell: regret 184.88 vs 259.47; paired Δ −74.59, 95% CI [−89.60,−59.58]. Other shared cells null/non-conclusive; closed-loop paired intervals all include zero. | Memory effect is conditional; endogenous observations compromise causal attribution. [Current State S3b-E1](../../HLS_CURRENT_STATE.md); [result JSON](../../../results/experiments/hls_s3b_memory_replay_diagnostic/results.json). |
| Campaign 1 | 1,280-run pilot plus bounded mechanism/counterfactual analyses; teaching may incur immediate production/CES losses, with remaining-horizon value changing by scenario and timing. Counterfactual ΔV_H mean −.074 across 64 paired state branches, 19 positive/45 negative. | Descriptive state-conditioned effects and resource/action-granularity lessons, not population policy superiority. [Campaign 1 results](../../experiments/CAMPAIGN_1_RESULTS.md); [findings](../../experiments/HLS_CAMPAIGN1_FINDINGS.md). |
| Campaign 2 | 5,120 validated runs; Q10/Q11 state-conditioned ΔG positive means .1623/.1669; Q01 mean .00145, 95% CI [−.01939,.01931]; strict-coupling frequency 71/15,360 (.462%). | Bounded state-conditioned realized return in frozen synthetic population; not full-policy or training-vs-no-training value. [Campaign 2](../../experiments/CAMPAIGN_2_RESULTS.md). |
| Campaign 3 META-VOC | META-VOC-50 minus RANDOM-50 cumulative μ_true +.1167/history, 95% interval [.0310,.2013]; decision compute −.1924s, interval [−.3539,−.0228]. G3/G4 held-out domains show no demonstrated production advantage. | Joint rule contrast only; budget frequencies not exactly equal, selected primary point followed development inspection, predictor audit AUC .624. No reliable opportunity detector or algorithmic novelty established. [Confirmatory](../../experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md), [predictor audit](../../experiments/META_VOC_PREDICTOR_VALIDITY_REPORT.md). |
| LLM budgeted routing | MIRT Brier .2698 vs constant .2314; logistic correction Brier .2174/log-loss .6240. One clear ILP-over-greedy cell +2.16pp; remaining tested cells do not establish general ILP advantage. | Predictor quality and optimizer effects are distinct. [Consolidated report](../../experiments/HLS_BUDGETED_LLM_ROUTING_CONSOLIDATED_REPORT.md). |
| MMLU corrected + DCS-LA | Subject selector 51.25%/124.20ms; best fixed 45.00%/141.61ms; DCS-LA 46.25%/139.27ms, Δ +1.25pp, paired 95% CI [−1.25,+3.75], same model 149/160, selection cost .456ms/query. | DCS-LA gain not conclusive; subject point estimate is best executable observed policy, pairwise superiority not assumed. Initial FAST/DEEP timing inversion retained as a separate invalid-comparability pilot. [Corrected report](../../experiments/HLS_DYNAMIC_CAPACITY_ORGANIZATION_CORRECTED.md); [DCS-LA](../../experiments/HLS_CONTEXTUAL_CAPACITY_SELECTION.md). |
| CE-03 H3 V1/V2 | V1 primary paired intervals include zero and has a training-label leakage issue. V2 C2−C1 +.18pp [−1.06,+1.42], C2−C3 +.59 [−.43,+1.61], collective C2−C0 −.34 [−1.61,+.93]. | No statistical support for H3 in these synthetic tasks; V1/V2 are distinct, not independent confirmation. [V1/V2 reports](../HLS_CE_03_H3_CAMPAIGN_RESULTS.md), [diagnostics](../HLS_CE_03_H3_FIRST_CAMPAIGN_DIAGNOSTIC.md). |
| CE-04 | 1,080/1,080 validated. H2−H0 under P1: +11.19/+11.69/+11.55pp at N=12/24/48; P1−P0 under H2: +11.25/+11.65/+11.54pp; P2−P1: −6.46/−7.42/−9.90pp; P3−P2: +.78/+1.41/+4.19pp; H2×(P3−P0) interaction: +6.14/+6.28/+6.53pp. | Strong, reproducible within the one frozen synthetic queued/deadline model; no cooperation, learning, universal or real-organization conclusion. [Results](../CE-04/11_CONFIRMATORY_RESULTS.md). |
| CE-04 causal diagnostic | 240/240 validated, H2 only, N=12/48. External calibration ΔI +5.266pp [4.531,6.073] and +8.683pp [8.282,9.084]; load-only ΔC and interaction ΔIC TOST-equivalent within ±2pp at both scales. | Intervention-specific effect; calibration-label costs not monetized; B10/B11 identical assignments in this data. [Results](../CE-04/15_CAUSAL_RESULTS.md). |
| CE-06 | 90 CE-04 P1/N24 records reanalyzed, plus nine diagnostic pilot runs. H0/H1/H2 success 77.39/82.86/89.09%; selected competence .7750/.8438/.9134; Gini .1969/.1227/.1235; wait .0106/.2746/.3100; late 5.9/89.6/117.6 per replica. | Diagnostics are descriptive, not independent replication or causal mediation. [CE-06](../CE-06/01_HETEROGENEITY_DIAGNOSTICS.md). |
| CE-07 | 30 matched pairs, 60 valid confirmatory simulations. A 65.81%, B 87.33%; B−A +21.52pp, SD1.13, bootstrap 95% CI [+21.12,+21.92], 30/30 positive, paired p=7.41e−39; not equivalent within ±2pp. | Same per-function marginals/maxima but different joint structures matter under this P1, N=12 stationary setup; no mediation or general specialization claim. First 60-run attempt and pilot used nonstationary family-phase generator and are excluded as stationary evidence. [CE-07](../CE-07/04_CONFIRMATORY_RESULTS.md). |

The primary status and result files—not a reanalysis in this audit—are the sources for each entry. Bootstrap and hypothesis-test values use the seed/replica as unit where those reports specify it. CE-06 is not a new replication; per-task samples, event rows and multiple policies within seed are not counted as independent replications.

## 5. Theoretical results and proof status

The [theory ledger](HLS_THEORETICAL_RESULTS_LEDGER_2026-10-26.csv) distinguishes formal definitions, exact calculations and hypotheses. The core chain is:
- **T0–T3:** static feasible collective outcome set, expansion relative to baseline, organizational sufficiency, and realization mapping at fixed competence.
- **T4–T6:** dynamic reachability of collective capability, value of development conditional on future use, and organization–development coupling.
- **G1/G2/G3:** finite ground truths and counterexamples used to make boundaries concrete.
- **RQ0:** policy-class inclusion and strong-SEP admissibility criteria, with a constructive C(alpha) strict-gap family under its formal assumptions.
- **Minimal HLS / OPV:** conditional Bellman inequalities, threshold witnesses, opportunity-value identities and smoothness-based sufficient bounds.
- **Q1-R:** an exact finite negative/design result; it does not repair the registered Q1 estimand.

Important interpretation: the inequality from policy-class inclusion is standard and not original merely in HLS notation. Strict separation needs the additional finite criterion, information/action restrictions and a reachable optimal-policy witness. Local opportunity inversion does not by itself imply a root value gap. Likewise, T4 competence change is not T5 organizational value; T5 value is not T6 unavoidable coupling. No repository theorem establishes a universal HLS law.

The primary proof sources are [HLS_STATIC_THEORY](../../theory/HLS_STATIC_THEORY.md), [HLS_DYNAMIC_THEORY](../../theory/HLS_DYNAMIC_THEORY.md), [G1](../../theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md), [G2](../../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md), [G3/G3-H](../../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md), [RQ0 boundaries](../../theory/rq0_routing_integration_boundaries.md), [minimal model](../../theory/minimal_hls_model.md), [opportunity-value propositions](../../theory/operational_development_opportunity_value.md), and [Q1-R](../../theory/HLS_Q1R_ANALYTICAL_VERIFICATION.md). The ledger identifies exact scope and marks standard reductions versus HLS finite constructions.

## 6. Cross-investigation map and comparability

Relationships supported by source evidence:
1. **Composition × organization:** G1 and CE-04/06/07 show that competence distribution and allocation rules alter attainable/realized outcome in particular models. CE-07 isolates two joint matrices at equal marginal summaries more directly than CE-04, but only under P1 and stationary equal task mix.
2. **Information × decision:** S3b, Campaign 2, META-VOC, budgeted routing, DCS-LA and CE-04 P2 all show that estimator/global predictive quality need not map directly to decision utility. The estimands differ (regret, state-conditioned returns, sequential μ_true, latency-budget utility, query accuracy, deadline success); they cannot be pooled.
3. **Action × observation:** S3b and adaptive P2/P3 produce selective/endogenous feedback. That complicates causal attribution and can make observations available to one policy depend on its previous actions.
4. **Use × future state:** S2b, S4, S7, G2/G3, Campaigns 1–2 and C6 show intertemporal effects in finite worlds, alongside separable/null/reducible cases. This is not evidence that all HLS work requires USE/DEVELOP or joint control.
5. **Quality × resource/time:** CE-04, MMLU, DCS-LA and budgeted routing explicitly measure latency, deadlines, service/decision cost or budgets; objective/units differ. Cost overhead may change an efficiency judgment but has not been converted to one common utility scale.
6. **Joint dependence × aggregate performance:** classifier fusion, AI-aging exact control and CE-07 show different senses of dependence/structure. Error dependence, competence matrix dependence and organization geometry are not the same mathematical object; analogy is not a shared causal estimate.

Apparent conflicts resolve by model and estimand. CE-04 H2 superiority and Campaign 1 teaching losses are not contradictory: one has static competence and no learning; the other has teaching/MIS and shared finite effort. CE-04 H2-H0 and CE-07 B-A differ in generator, demand stationarity, policy contrast and organization structure. META-VOC versus MMLU/DCS-LA measures sequential synthetic cumulative reward versus single-query classification/latency. S3b MSE and regret can diverge because decision-critical edges need not match global estimation loss. These relationships are descriptive/structural readings from cited reports, not cross-study causal mediation.

## 7. Existing implementation and technical capability

The repository contains substantial executable, tested routes, but no universal simulator or shared semantic model. Actual source/API entries are enumerated in the file inventory and [repository map](../../REPOSITORY_GUIDE.md).

| Capability | Existing implementation | Validation boundary |
|---|---|---|
| N×K agents, competence, task/action catalogs | src/hls/hls_lab_nk_geometry.py, hls_lab_nk_production.py, hls_lab_nk_execution.py | Validated finite geometries/compatibility tests; not all campaign dimensions integrated. |
| Dynamic task generation / environment | src/hls/hls_lab_nk_environment.py; src/hls/hls_lab_dynamic.py; src/hls/ce04.py | C5 IID/stationary, time-varying and Markov paths; CE-04 SimPy continuous arrival/queue model. Distinct semantics. |
| Assignment / planning | src/hls/hls_lab_nk_policies.py, hls_lab_nk_assignment.py, synthetic exact solvers, ce04.py | Exact enumeration small; P0/P1/P2 and LinUCB paths tested in declared worlds. No universal optimizer. |
| Competence learning and estimation | src/hls/hls_lab_nk_learning.py; hls_lab_nk_estimation.py; src/hls/ce04.py | MIS-v2, partial observations and Beta estimates are model-specific; calibration/observation protocols differ. |
| Teaching / transfer | src/hls/hls_lab_nk_teaching.py; src/hls/hls_s4_transfer_exact.py; CE-03 distillation scripts | Implemented in bounded contracts; effectiveness/collective transfer not generally validated. |
| Cooperation/complementarity | Exact classifier fusion and pair-cooperation formulation in expert complementarity pilot; theoretical κ in E1 report | No generic multi-agent cooperative execution engine or CE-04 cooperation experiment. |
| Contextual adaptation | src/hls/linucb.py; ce04 P3; Nembhard adaptive, contextual router, DCS-LA | Tested in bounded settings; no cross-route policy equivalence or general advantage. |
| Queues, deadlines, resource budget | src/hls/ce04.py with SimPy; N×K per-period budgets/teaching; S2b exact shared budget | Different operational/resource semantics; don't transplant without contract. |
| Metrics and experiment records | src/hls/experiment_contract.py; performance_evaluation.py; adapters | ExperimentRun/HLS-PEF schemas and selected vertical slices; preserve route semantics; does not automatically pair/analyze all studies. |
| Tests/reproducibility | tests/, seed-keyed generators, manifests, frozen config hashes | Strong route-specific tests; provenance incidents and ignored raw artifacts mean repository-wide reproduction is not guaranteed. |

These are engineering capabilities and validation facts, not evidence that every mechanism is scientifically useful or mutually composable. The lab status and known boundaries are documented in [HLS Current State](../../HLS_CURRENT_STATE.md), [architecture/reuse audits](../../engineering/HLS_LAB_ARCHITECTURE_2026-10-17.md), and [common contract](../../engineering/HLS_COMMON_EXPERIMENT_CONTRACT.md).

## 8. Traceability, omissions, and integrity

The four accompanying registers provide exhaustive path coverage and a compact scientific index:
- [file census](HLS_FILE_INVENTORY_2026-10-26.csv) — tracked, ignored and untracked physical files with sizes.
- [experiment/evidence matrix](HLS_EXPERIMENT_EVIDENCE_MATRIX_2026-10-26.csv) — major campaign families, protocols, code, results, statistics and limitations.
- [theory ledger](HLS_THEORETICAL_RESULTS_LEDGER_2026-10-26.csv) — result type, assumptions/scope and proof status.
- [incident ledger](HLS_PROVENANCE_AND_INCIDENT_LEDGER_2026-10-26.csv) — absent/untracked/ignored evidence and historical defects.

Key limitations and provenance cases:
- Full CE-04 task-level logs and CE-04 causal raw logs are local-only/ignored; reports/manifests and lightweight aggregate outputs are tracked. The CE-07 exact tie trace is tracked but its replica_metrics CSV is local-only. Therefore the public Git tree does not contain every row-level artifact needed for independent full replay.
- Nembhard E1 has a tracked interrupted/29-of-1,016 incident and a later local untracked check claiming 1,016 valid episodes; do not call the latter published/verified.
- Full-suite integrity failures were historically reported (first 13, later five). This audit did not rerun tests, and those historical counts are not asserted as today's test status.
- Initial MMLU output hashes validate, but its source hash does not match current evolved source.
- CE-03 V1 has T3 training-label leakage; V2 is a separate corrected protocol and remains statistically inconclusive.
- CE-04.5 stopped due to a false-positive validator; correction and CSV writer incident are preserved before validated rerun.
- CE-07's first 60-run confirmatory attempt violated stationary family demand; it is explicitly preserved and excluded. The CE-07.3 pilot had the same family-phase issue and is not evidence that the stationary pilot criterion passed.
- Several older HLS_CURRENT_STATE sections are expressly historical and contain status language superseded by the dated opening snapshot. A few embedded “uncommitted/current worktree” notes are stale relative to the current HEAD; use actual git status plus current dated snapshot, not stale prose.
- More materially, the dated opening snapshot of HLS_CURRENT_STATE reports CE-04/CE-06 and retains CE-03 as active priority, while the later HISTORY entries and CE-07.5 report record the completed, corrected CE-07 confirmatory campaign and its +21.52 pp result. The current-state summary does not yet include that latest result. It also omits the CE-05 course correction present in HISTORY. As documents stand, the latest dated chronology is newer than the nominal current-state summary; this is a documentary status discrepancy, not a reason to rewrite historical entries. This audit records it without correcting either source.
- Literature reproduction and expert/LLM audit documents are not proof that an algorithm was reproduced faithfully. Reports distinguish source model, adaptation, and exact implementation; the external reviewer material mentioned in some project conversations is not stored and is NO VERIFICADO here.
- Raw/checkpoint-heavy ignored directories mean local availability is not Git availability. No claim is made that ignored files are complete, licensed for redistribution, or reproducible from a clean clone.

## 9. Consolidated scientific knowledge (without selecting a paper or application)

The accumulated evidence supports conditional, not universal, lessons:

- Heterogeneity is a structured distribution of capabilities, not a scalar virtue. Its effect depends on the task mix, organizational policy, feasibility, and resource/time constraints. CE-04’s mean-preserving H2 profile benefits P1 in that queue model; CE-07’s two joint structures differ under equal marginals and a fixed P1; neither implies all heterogeneous organizations win.
- Greater individual competence, a changed competence state, or lower estimation error does not guarantee greater collective value. T0–T6, G2/G3, S3b, Campaign 2 and CE-04 expose distinct boundaries between state, information, attainable capability, policy choice and realized collective outcome.
- Organization affects which capability is used, where observations accrue, and how load/queues develop. CE-06 diagnostics show higher success can coexist with more waiting/tardy admitted work; they do not identify queue congestion as mediator.
- Learning and transfer are conditional mechanisms. Campaign 1, S4/S7, CE-03 and exact theory contain positive, negative, null and boundary cases; no broad “learning always helps” claim is supported.
- Sophistication is not automatically beneficial: many RQ0 constructions reduce to simpler policies; the S7 alternative tie-break nearly closes an apparent planning gap; MMLU cascades lost on the measured frontier; DCS-LA's gain was inconclusive; contextual and budgeted routing depend on the predictor and scale.
- Performance is multi-dimensional. CES, success-on-time, quality, delay, resource cost, computation time, regret, and fit error are different outcomes. Without a declared common utility they must not be collapsed or compared numerically across studies.
- Negative, null, failed-gate and stopped results are part of the evidence base and are retained in the ledgers.

## 10. Coverage boundary and audit conclusion

**Covered:** all versioned file paths (2,046), all currently physical paths not under .git (6,481), document authority and repository maps, the current dated science snapshot, chronology, all major named model/campaign families in docs/theory/experiments/research and src/hls, the tracked result hierarchy, top-level model/test/campaign routes, selected primary confirmatory reports, major exact proof sources, and documented provenance incidents.

**Not claimed as verified:** semantic read of every one of 6,481 physical files; reproduction or recalculation of all 5,095 result files; integrity/completeness of ignored outputs; fresh test-suite status; external literature priority; untracked expert/reviewer records; or exact raw replay where artifacts are absent from Git. The CSV inventory makes the physical coverage auditable; scientific conclusions are taken from identified canonical sources, not inferred from filenames.

This is the terminal audit record for the requested scope. It makes no new experimental proposal, chooses no application or manuscript, and stops here.
