# AIAI 2026 source recovery and extension analysis

**Assessment date:** 2026-10-27.
**Scope:** documentary analysis only. The paper, presentation, SOCTRA reports, manuscripts and source code were inspected read-only. No source artifact, data, HLS core, model, or experiment was modified or reproduced.
**Canonical publication:** M. Lázaro et al., “AI-Driven Alert Triage in Security Operations Centers: Imbalanced Learning with Human-in-the-Loop Contextual Bias Modeling,” *Artificial Intelligence Applications and Innovations (AIAI 2026)*, IFIP AICT 794, pp. 150–164, Springer. First online 2026-07-16; Springer’s recommended citation gives 2027. DOI: [10.1007/978-3-032-30805-4_11](https://doi.org/10.1007/978-3-032-30805-4_11). The DOI landing page and the chapter in the proceedings are the authority for the published version.

## 1. Version determination and source comparison

The definitive article is the Springer proceedings chapter, not either 14-page LaTeX-produced PDF. The full proceedings PDF contains the article on printed pages 150–164 (PDF pages 172–186, one-based); `Justificantes/AIAI2026_Paper.pdf` is an extract containing front matter and that published chapter. Springer identifies the article, authors, pagination, series, publication date and DOI on its public chapter record. The 19-page `692777_1_En_11_Chapter_Author.pdf` is an author-version chapter file with Springer metadata, not the publisher’s final proceedings file.

The two 14-page files, `EANN2026_paper.pdf` and `EANN_2026_SOCTRA.pdf`, are author-produced prepublication versions (both PDF metadata dates are 2026-05-06). The associated `.tex`, `.bbl` and `refs.bib` are source material, not evidence that a particular PDF was the exact submitted or accepted file. Their exact submission status cannot be established from filenames or metadata alone. Comparison of the published chapter with the author chapter confirms the same title, central method, dataset description, principal tables and conclusions; the chapter-author text has 0.929 normalized word-set Jaccard overlap with the published chapter body. This is a coarse text-extraction comparison, not a line-by-line editorial diff. The published chapter is the version to cite and use for reported findings.

The requested `AIAI2026_SOC_Alert_Triage_presentation_final.pptx` contains 13 slides and PPTX metadata last modified 2026-07-13. A sibling `AIAI2026_SOC_Alert_Triage_presentation.pptx` is a distinct 8-slide file with a later metadata modification date (2026-07-20). Filenames and metadata do not establish which deck was actually presented. This analysis reviews the explicitly requested `*_final.pptx` and treats the sibling only as a version-control ambiguity, not as the definitive deck.

## 2. Source inventory and handling

The source root below is recorded as supplied by the researcher. Hashes identify the exact local files inspected; they are not claims that those files are in the HLS repository. No source file was copied into this repository.

**Primary source root:** `/Volumes/Lacie_8Tb/UC3M.Drive/Proyectos/GMV/INCIBE/SOCTRA/SOCTRA_UC3M/Congresos/AIAI2026/`
**Supplementary SOCTRA root:** `/Volumes/Lacie_8Tb/UC3M.Drive/Proyectos/GMV/INCIBE/SOCTRA/SOCTRA_UC3M/`
Paths beginning `WP4/`, `Journal/` or `Congresos/trazabilidad_` in the following table are relative to the supplementary root; AIAI paths are relative to the primary root.

| Original path relative to source root | Type/version and relation | Relevant information used | Reuse and handling restriction |
|---|---|---|---|
| `Proceedings/978-3-032-30805-4.pdf` | Full Springer proceedings; contains the published chapter | Primary source for final wording, methods, tables, conclusions and rights statement. SHA-256 `78ea4193be4be0c3239066fa29d82b7e9285987ef0965eb75ca10e06a872eed9`. | Public proceedings PDF; do not duplicate the 49 MiB book in HLS. Cite the chapter DOI. Chapter states CC BY 4.0, subject to third-party material notices. |
| `Justificantes/AIAI2026_Paper.pdf` | Extract of proceedings chapter plus front matter | Convenient local copy of the same published chapter, printed pp. 150–164. SHA-256 `5f73ce97d1f1355dbdd6675390e9f7e658eb8b5db4900e03ac01d9677d3befe2`. | Same publication/license caveat; do not copy into HLS. |
| `692777_1_En_11_Chapter_Author.pdf` | Springer chapter-author version with publication metadata; 19 PDF pages | Cross-check of chapter text, figures/tables and title-page metadata. SHA-256 `58add976e0ec3516489448b7c963dcb4d26a548acc23aeac57ea8f6c7de3c47a`. | Author file; no separate permission to redistribute inferred. Do not copy. |
| `EANN2026_paper.tex` | LaTeX author source; prepublication state not established | Section structure, model description, table source and prose comparison. SHA-256 `a6750943edd99962396dc62489a136157a9292ad011c6ec453ae5f50df7e69c5`. | Author/source material; retain at its controlled source location. Do not copy or modify. |
| `EANN2026_paper.pdf` | 14-page author-produced PDF; metadata 2026-05-06, dvips/Ghostscript | Earlier rendered text/results. SHA-256 `d032dec20f271b4ef72775ec3f614beebce7ee95e46ebb405ce31e890908b6ad`. | Not the publication authority; do not redistribute as the final article. |
| `EANN_2026_SOCTRA.pdf` | 14-page author-produced PDF; metadata 2026-05-06, pdfTeX | Another prepublication rendering; useful for identifying manuscript evolution. SHA-256 `eb7bf4f7b9fe99dd49665f8e700dc5e1fe5fc6f8571551e46a76b75a376b7a48`. | Exact submission/acceptance status unknown; do not treat as final or copy. |
| `refs.bib` | Author bibliography source | Bibliographic records considered when matching cited work. SHA-256 `29661d9d81d4eb42625074d596f6501800ff101b522ccb1269143105a9ee25a3`. | Not an authoritative verified bibliography for the extension; do not copy wholesale. |
| `EANN2026_paper.bbl` | Generated bibliography for an author-source build | Checks which references that build emitted. SHA-256 `e64304dd110e5d97622713e21b6b155157c535220fdc804889596b3a906f631f`. | Build artifact, not a separate scientific source; do not copy. |
| `Presentacion/Final/AIAI2026_SOC_Alert_Triage_presentation_final.pptx` | Requested 13-slide conference deck; metadata last modified 2026-07-13 | Operational SOC framing, stated L1/L2 roles, triage decisions, workload context and additional LSE claims. SHA-256 `44f3ff6802196bd7d6b15af578bed6496a27107f35ff6c52d9ece37f4af56dda`. | Internal presentation; no public reuse license verified. Do not copy slides, figures or branding. Verify with authors/project owner before reuse. |
| `WP4/Docs/WP4_SOCTRA_Entregable_Etapa3_v1.docx` | Internal SOCTRA technical deliverable | Supplementary data/processing and operational-context detail; records a change to the definition of an 8×5 monitoring schedule. SHA-256 `cda680d80c54f482bf2f51a517029a7c1833c6c7d640716d3532a5d30266ab42`. | Internal contractual project material; summary only here. Do not redistribute or generalize a project-specific rule. |
| `WP4/Docs/Informe Final Etapa 2/WP4_SOCTRA_TriajeAlertas-DTS_v1-2.docx` | Internal technical report, versioned deliverable | Data preparation, contradictory labels, expertise-weighting rationale and model-development history. SHA-256 `1c5037e550dee460a13d21aca18fc07c50fe7419cc1fe4db1b4d2bc580973137`. | Internal project material; no source text copied. |
| `Congresos/trazabilidad_contexto_escalada_marce.docx` | Internal context/escalation note | Checked for operational corroboration; it did not provide an independent quantitative measurement of analyst time saved. SHA-256 `dd78eff0839928529b181ff26e946beb31cf7a18aec34d35a15c810b00157e68`. | Internal project material; no source text copied. |
| `Journal/Alert_Triage_No_Authors_manuscript.tex` and `Journal/Alert_Triage_No_Authors.pdf` | Internal journal-manuscript snapshot with additional classifier experiments, including LSEnsemble | Source of the non-AIAI LSE method description and tables summarized in §3.1. SHA-256s `5416ce479545c2568967e73d54005cc496d5440c1d6c581e969388899eec5dc3` and `f59b8e8cbc7b4cb6536f1511562ea396b0d0f59f8c8e3f7ff35191a18bd65707`. | Unpublished author material; not AIAI publication evidence. Do not redistribute or submit overlapping material until author/editorial status and rights are confirmed. |
| `Journal/EAAI-26-22748.pdf` | Editorial-system manuscript-draft package; metadata date 2026-07-22 | Establishes that a separate journal-manuscript snapshot exists; its current editorial status cannot be established from this file. SHA-256 `2d0d65cca552ca11e889cd692046852556a67cf829878432ec6871674ada19f2`. | Potentially confidential editorial material. Its contents and submission identifier are not reproduced here. Confirm status with authors before any overlapping journal submission. |
| `WP4/New_Code_2025/uc3m/labelswitching.py` and `WP4/New_Code_2025/task_cv_model_new.py` | Internal implementation and experiment-runner snapshots | Inspected read-only for LSE operation, parameter grids and reproducibility concerns. SHA-256s `d5b06cf6a506b6bd88a78866d450bb2b93da5c35cf6baa554506b73280fbd261` and `085e5d4192a2a29a99b735bc2319ad0962bfe04762929b4ea01c485d378d017b`. | Internal code; not executed or copied. It is not demonstrated to reproduce the manuscript tables exactly. |
| `Presentacion/Final/AIAI2026_SOC_Alert_Triage_presentation.pptx` | Distinct 8-slide sibling deck; metadata last modified 2026-07-20 | Used only to detect that `*_final.pptx` is not demonstrably the latest deck. SHA-256 `4fe8602972985fda5e7a7e7ee0ac7f60244247622192688ce6115e2a5520f06d`. | Internal material; not treated as final evidence; do not copy. |

The reviewed priority files contain no alert-level dataset. The paper says the source collection contained 170,653 alerts over 24 projects, but analysis used a filtered 63,410-alert subset and excluded four projects for contractual data-sharing restrictions. Additional internal SOCTRA code and data files exist under the supplied project root, but their reuse rights, authoritative version, linkage to the published tables and eligibility for release are not established here. Raw data, permissions and a validated data dictionary were not copied or treated as publishable evidence. This is not a claim that such material is absent elsewhere.

**Access classes:** the final article is public and identifies a CC BY 4.0 chapter license; the conference decks and LaTeX/author materials are treated as internal author/project materials unless their owners confirm otherwise; alert telemetry is contractually/privacy restricted as described by the article. Publicly stated anonymization does not itself grant rights to reuse or redistribute underlying data.

The evidence is kept in four distinct layers: **(A)** results published in the AIAI chapter; **(B)** additional SOCTRA experiments and implementations in internal manuscript/code artifacts, not published by AIAI; **(C)** operational descriptions in the deck and SOCTRA deliverables; **(D)** new HLS questions and mechanisms, which remain hypotheses. Claims are not promoted from B/C to A, and HLS proposals in D are not evidence about SOC practice.

## 3. What AIAI 2026 studied

### Setting, data and target

The paper models two separate binary decisions in initial L1 triage: escalation to L2/24×7 response and reporting to the client. It does not model the downstream L2 investigation as an operational process. The source pool is described as 170,653 alerts from 24 monitored projects (January 2023–February 2025); the evaluated subset has 63,410 alerts from November 2023–February 2025 after selecting the recent 16 months, excluding four projects under data-sharing restrictions and removing records with incomplete telemetry. A chronological split uses 48,961 alerts for the first 12 months of training and 14,449 for the final four months as held-out test data.

The paper describes 22 intrinsic alert fields, a reception timestamp, analyst identifier and three expertise fields, plus six post-processing annotation fields used to derive labels. It says post-workflow fields are excluded from the 27 fields available at receipt. This distinction is central to any reuse: annotation fields are label-generation provenance, not permitted prediction inputs. The exact feature availability, analyst-identifier use, label construction timing and cross-split repeated-pattern handling should be checked against the original data dictionary/code before any reproduction.

### Method

The method is an offline decision-support classification pipeline, not a workforce organization or training intervention:

- It standardizes data and contradictory labels using “Labeling Dynamics”: retain the latest label for a pattern with one change; use an expertise-weighted majority when patterns change multiple times.
- It encodes intrinsic categorical/numeric/text features (the paper reports a 1,030-dimensional intrinsic representation) and adds 141 rolling contextual workload statistics at alert arrival, summarized at analyst, project and SOC levels over past events.
- It compares logistic regression, Random Forest, XGBoost, LightGBM, Bayesian MLP, and in some experiments linear SVC/SGD. Feature comparisons include intrinsic (A), contextual (C), and combined (A+C) data.
- It uses analyst “expertise” weights as sample weights and a normalized Bayes cost/benefit framing for asymmetric false-alarm/miss costs. The main reported metrics are balanced accuracy, false-alarm probability and detection probability. Hyperparameter search is described as grid search with five-fold CV targeting balanced accuracy.

The article does not establish that the expertise weight is a validated competence measure. It is a proxy constructed from operational seniority/historical accuracy under GMV criteria. Nor does the article test whether the AI changes human decisions or learning: the system is described as decision support with the human retaining the final decision, but no controlled human–AI interaction treatment is reported.

### Reported results (published chapter)

The following are the article’s held-out results, not HLS results and not independent replications. `A` denotes intrinsic features; `A+C` denotes intrinsic plus contextual features.

| Task/labels | Published comparison | Reported balanced accuracy and accompanying rates | Bounded reading |
|---|---|---|---|
| Escalation, original labels | Bayesian MLP A: 0.7849; A+C: 0.8222 | A+C: false-alarm 0.2056; detection 0.8500 | A+C is better for this listed model/holdout; no interval or significance test is given. |
| Escalation, standardized labels | LightGBM A: 0.8643; A+C: 0.8986 | A+C: false-alarm 0.0450; detection 0.8421 | Reported best table result; the standardized test positive class is extremely rare (paper gives test IR 759.47). |
| Escalation, context-only, standardized labels | Best reported window: 6 h | Maximum BAcc 0.752 (SGD); 1/4/8 h maxima 0.681/0.674/0.730 | Descriptive feature/window comparison; not a causal estimate of workload or fatigue. |
| Reporting, standardized labels | LightGBM A: 0.8751; A+C: 0.8705 | A: false-alarm 0.0777, detection 0.8279; A+C: 0.0780, 0.8190 | Context does not improve this listed LightGBM result; context-only BAcc is about 0.506–0.521 across reported models. |

The paper’s initial class-imbalance ratios are reported as 298.4 for escalation and 3.87 for reporting in the full data, changing to 276.1 and 2.78 after project filtering. These are not the same as the train/test ratios after label standardization; the test standardized escalation IR is reported as 759.47. Do not conflate these denominators or label conditions.


## 3.1 Additional SOCTRA classifier experiments: Label Switching Ensemble

**Evidence class:** internal SOCTRA experiment/manuscript snapshot, not part of the published AIAI chapter. The presentation names “LSEnsemble” among the strongest classifiers; the published chapter’s model list and result tables do not include it. A separate internal journal-manuscript snapshot reports additional experiments. These results must not be cited as AIAI-published findings or as HLS organizational evidence.

### Problem and method

The method targets binary classification under class imbalance and asymmetric error costs. In the inspected implementation, a collection of 31 classifier experts is trained with independently switched labels: a fraction `alpha` of majority labels is switched toward the minority and a fraction `beta` of minority labels toward the majority, with sample weights adjusted. Optional SMOTE-style population rebalancing can be applied. Expert outputs are averaged; the final decision threshold is corrected for switching, class imbalance, rebalancing and decision-cost factors. The manuscript describes use with several probabilistic base learners. This is a predictive-classification method; it does not allocate analysts, change roles, train workers, or define an organizational policy. It is **not** part of the proposed HLS organizational model.

### Configurations and reported results

The internal manuscript evaluates LSEnsemble across escalation/reporting; intrinsic (A), contextual (C), and combined (A+C) features; original and standardized labels; and symmetric and asymmetric costs. It says the ensemble has 31 experts, no population rebalance (`Q_RB,S=1`), tunes switching rates and cost factors, and considers Asymmetric MLP, logistic regression, and calibrated RF/LightGBM/XGBoost base learners. The inspected experiment runner instead contains two successive LSE parameter blocks, of which the latter is effective under ordinary Python assignment: `alpha` 0.43/0.46, `beta` 0, `Q_RB_C` 1, `Q_RB_S` 50/60, 31 experts, hidden size 30, batch 128, 100 epochs, and `mode=representative`. Values `Q_RB_S=50/60` imply population resampling in the inspected implementation, unlike the manuscript’s stated `Q_RB,S=1`. The runner and class implementation also show only the FAMLP initialization path directly; they do not, by themselves, substantiate the manuscript’s full base-learner list. The exact code/configuration that generated each table is unresolved.

The internal manuscript’s symmetric-cost test tables report these LSEnsemble balanced accuracies:

| Decision | Labels | A | C | A+C | Comparison stated in manuscript |
|---|---|---:|---:|---:|---|
| Escalation | Original | 0.7581 | 0.7378 | 0.7995 | Bayesian MLP is best at A+C (0.8222); LSE is best among the listed context-only classifiers. |
| Escalation | Standardized | 0.8751 | 0.7509 | 0.8839 | LightGBM is best at A+C (0.8986); LSE is competitive, not uniformly best. |
| Reporting | Original | 0.6798 | 0.5339 | 0.7010 | A+C LSE slightly exceeds the other reported classifiers; the manuscript describes the margin over LightGBM as marginal. |
| Reporting | Standardized | 0.8704 | 0.5188 | 0.8701 | LightGBM is slightly higher on A (0.8751) and A+C (0.8705); LSE has higher detection in some settings at a different false-alarm rate. |

Under the manuscript’s asymmetric-cost tables, false-negative cost is set to three times false-alarm cost for escalation; false-alarm cost is set to twice miss cost for reporting. These are normalized classification-cost ratios, not measured monetary or labor costs. The standardized-label table reports LSE values of normalized Bayes benefit / balanced accuracy / false-alarm probability / detection probability: escalation A = 0.9063 / 0.8477 / 0.2695 / 0.9649; reporting A = 0.8934 / 0.8639 / 0.0476 / 0.7754; reporting A+C = 0.8919 / 0.8568 / 0.0381 / 0.7517. LSE is the highest reported normalized benefit in those listed reporting A and A+C conditions, but LightGBM is strongest for the standardized escalation C and A+C settings (0.8819 and 0.9162). Original-label LSE reporting benefits are 0.7293 (A) and 0.7288 (A+C). These rankings are conditional on the chosen cost ratios, one temporal holdout and the manuscript’s target construction; they are not universal model rankings. No confidence intervals, independent data replications, or measured inference/workload cost are given for these LSE comparisons.

### Limits and source discrepancies

- These are internal manuscript results, not published AIAI evidence and not independently verifiable from released data and code.
- Parameter reporting conflicts with the inspected runner (`Q_RB,S=1` in the manuscript versus effective `Q_RB_S` values 50/60 in code). The manuscript’s broad base-learner support is not demonstrated by the inspected class initialization path. Do not assume the manuscript or code is the exact executed version.
- The runner defines `n_simus=10`, but the supplied sources do not link those repetitions/seeds to manuscript table rows. Label switching uses NumPy’s global random state; its optional SMOTE call uses Python’s `random.randint`. Complete RNG seeding and table provenance are not established by the inspected files.
- The inspected `predict_proba` implementation casts normalized outputs to integer type. This raises a reproducibility/implementation question for consumers expecting calibrated probabilities; without tracing the exact table-producing version, this is a concern, not a claim that any published result is invalid.
- Per-configuration hyperparameter selection, asymmetric cost settings and a single rare-positive chronological test set limit generalization. No uncertainty intervals establish that close model rankings differ reliably.
- Even if LSE improves a classifier metric, that result alone says nothing about analyst time saved, workload relieved, released capacity, competence development or team performance.

## 4. Demonstrated contribution and limits

### Supported, within the paper’s scope

1. A particular offline pipeline was evaluated for two L1 binary triage labels using one managed SOC’s filtered, historical alert data and a chronological four-month holdout.
2. On that holdout, adding contextual workload features improved selected escalation model results shown in Tables 3 and 5, while the best reported reporting results were obtained with intrinsic features alone. Context-only classification was substantially more informative for escalation than reporting in the reported tables.
3. The authors report a label-standardization procedure, expertise-aware sample weighting, temporal feature construction, and comparisons among several classifier families.

These are empirical observations from the paper’s specific data and split. The abstract/conclusion’s language that context “improves” escalation is supported as a within-dataset feature ablation result, but not as a causal claim that workload pressure changes analyst decisions, causes fatigue, or that deploying the model improves operational SOC outcomes.

### Not established

- No analyst assignment policy, organizational design, specialization strategy, task routing policy or L1-to-L2 capacity allocation is experimentally compared.
- No L2 investigation performance, service time, queue, SLA compliance outcome, throughput, staffing requirement, training, mentoring, experience accumulation, competence development, transfer or adaptation to a new client/threat is evaluated.
- “Human-in-the-loop” means the analyst remains the decision-maker in the described design; the paper does not report a human-subject trial or quantify reliance, overrides, human error, workload change, learning or joint human–AI performance.
- Workload features are predictive correlates constructed from past event activity. They do not identify a causal effect of workload, time pressure, fatigue or analyst availability.
- The chronological holdout is from the same SOC and projects/time population; no external SOC or unseen-client evaluation is reported. One temporal split, without reported confidence intervals, seed replications or significance tests, does not quantify sampling uncertainty or robustness to alternative periods.
- Reported ground truth is based on historical SOC decisions and a derived standardization rule, not an independently adjudicated threat outcome. Expertise weights are not shown to be calibrated competence estimates. Label standardization may change the target and deserves sensitivity analysis.
- The reported five-fold CV target and chronological holdout are described, but the article does not provide enough public detail to independently reconstruct all preprocessing, feature selection, tuning, exact threshold selection, or split-level uncertainty from the supplied files. The standardized escalation holdout has a very small positive-class share (IR 759.47), making point estimates especially sensitive to a few cases.
- The paper presents normalized error costs and classification metrics, not monetary or analyst/mentor opportunity costs. No cost-benefit claim for workforce development follows.

The article’s future-work statement itself points to real-time integration and multi-class incident labeling; it does not claim those were implemented.

## 5. What can be reused in the HLS study

The article provides an application-specific L1 alert/decision vocabulary and an existence proof that operational context and intrinsic alert content may have different predictive value for escalation and reporting in one dataset. It motivates, but does not validate, further investigation of heterogeneity. Its analyst ID/expertise fields and rolling temporal features suggest data requirements to investigate with the data owner; they do not supply a ready-made competence matrix or HLS organization model.

Reusable as **documented candidates**, subject to source/data access and semantic review:

- Scenario boundary: L1 escalation and client reporting, with escalation as a hand-off decision; the paper’s “two independent binary tasks” should not be silently converted into a joint/sequential workflow.
- Historical labels, time stamps, analyst-proxy weights and past-event context as candidate observations, only if available, legally reusable, well-defined and leakage-safe.
- Intrinsic-only versus intrinsic-plus-context prediction as a baseline comparison for a future predictive subquestion.
- Balanced accuracy, false-alarm rate and detection probability as classification measures; these do not measure collective operational performance and must not replace outcomes such as correct on-time resolution, queueing, cost or individual burden where those are the research estimands.
- Cost-sensitive classification as a model objective; this is not equivalent to explicitly measuring financial, training or opportunity costs.

Existing HLS theoretical candidates are linked in [the evidence ledger](EVIDENCE.md): static assignment and crossed-specialization exact construction; two-period competence development; deadline-constrained allocation; matched-marginal competence structure; and inconclusive synthetic transfer results. Each has important scope limits. None is an empirical finding about SOC analysts. No component is promoted to the HLS core by this analysis.

## 6. Presentation and SOCTRA operational-context audit

The requested 13-slide deck is a source for project-level operational context, not merely a summary of the article. It describes GMV-CERT as a two-level analyst organization: L1 triage and L2 deep analysis (slide 2); it identifies escalation and reporting as two triage decisions (slide 3); and it depicts workload context at analyst, project and SOC levels (slide 8). The internal SOCTRA technical deliverable also records that a monitoring-schedule definition changed over the project to better represent operator availability. These are source-reported descriptions, not universal SOC procedures. They support treating L1 and L2 as different work roles/processes in the testbed, while requiring the project/data owner to validate task boundaries, handoffs, authority and actual capacity constraints.

The deck labels its dataset slide as 170,653 alerts; the article's experimental subset is 63,410. These are source-pool versus analyzed-subset quantities, not interchangeable sample sizes.

The deck also contains statements not established as results by the published chapter:

- Slide 8 characterizes the six-hour window as the best trade-off; the paper reports a maximum BAcc among its tested windows, not a prespecified trade-off analysis or causal fatigue finding.
- Slide 11 gives operational targets/examples such as detection above 95% for escalation and false reporting below 5%. They are not achieved thresholds in the reported standardized test table (e.g. escalation detection 0.8421; reporting false-alarm 0.0780 for LightGBM A+C).
- Slides 12–13 name “LSEnsemble” and claim it is strongest under an asymmetric reporting operating point. The internal journal-manuscript snapshot contains additional LSE experiments, but they are distinct from AIAI publication evidence and have unresolved configuration/provenance differences (§3.1). They require author/project clearance before external reuse.
- The deck calls the approach human-in-the-loop and describes workflow, but it provides no evidence of a controlled human–AI study.

Use the deck and internal SOCTRA deliverables first for project-specific operational descriptions; use the Springer chapter for claims and results actually published at AIAI; use internal manuscript/code only to track additional SOCTRA experiments and unresolved LSE provenance. Do not merge these evidence classes. The later-modified sibling deck also makes the presented version uncertain; obtain author confirmation before citing a deck or reusing its figures.

## 7. A scientifically substantial Electronics extension

The Special Issue flyer invites expanded AIAI/EAAAI 2026 papers with at least a 50% increase, requests novel insight and rigorous validation, and lists 15 March 2027 as the deadline. *Electronics*’ current author instructions require a Data Availability Statement, including when data cannot be shared for legal/privacy/ethical reasons. These are verified editorial requirements as of this assessment; recheck them at submission. Editorial fit and acceptance are not established.

A defensible extension has three separate layers. **(1) Triage classifier:** the AIAI chapter supplies a predictive-method baseline; LSEnsemble is a separate SOCTRA classifier result, not an organization method. **(2) Operational tool effect:** SOCTRA demonstrated reduced operational triage burden (per PI clarification received 2026-10-28); that finding is distinct from a quantitative estimate of analyst-hours or capacity released, which the reviewed sources do not provide. **(3) Team organization:** how capacity is used for training, learning, specialization/polivalence, task redistribution or adaptation is the candidate HLS contribution. Costs, service constraints and performance trade-offs belong in this third-level analysis.

The demonstrated SOCTRA reduction in triage burden must not be conflated with a measured amount of analyst time or operational capacity released. AIAI reports retrospective classification metrics and error trade-offs; the deck and reviewed SOCTRA deliverables do not provide a direct before/after measure in analyst minutes, queue burden, staffing or released capacity. A classifier metric or lower false-alarm rate alone is not a labor-time estimate. Any numerical capacity-release value in a future simulation is therefore a separate hypothetical input unless an operational measurement supplies it. The reduction is treated as a PI-confirmed project finding; its quantitative workforce/capacity magnitude remains unverified in the inspected source set.

A substantial extension should add distinct scientific evidence, for example:

1. **A longitudinal organizational decision problem:** measure task-relevant competence and evaluate allocation across validated L1/L2 tasks under finite availability, queues and deadlines, against documented current practice and matched-information baselines.
2. **A capacity-release mechanism:** separately measure or explicitly assume how the triage tool changes time per alert, rework, false-positive handling or queueing. Account for costs and constraints and keep measured effects separate from simulated capacity scenarios.
3. **A competence-development question:** evaluate a defined training/learning intervention, its effect on task-specific competence, and net value after trainee time, mentor time, direct cost and displaced operational work. Experience and an expertise weight are not competence measures.
4. **A team-level outcome:** test how available capacity is used—for training, learning-by-doing, specialization/polivalence, task redistribution or adaptation—and measure individual, collective and resilience outcomes. This third layer is the candidate main contribution; LSEnsemble need not enter the organization model.
5. **New validation evidence:** use an approved longitudinal or otherwise defensible design with adequate independent units, uncertainty, label/competence sensitivity and temporal/client generalization where permitted. If only retrospective records are available, limit claims to prediction/replay association; do not claim causal organization, workload relief or training effects.

These are candidate directions, not a frozen protocol or novelty claim. A narrow paper is preferable to bundling allocation, training, adaptation and AI treatment without enough evidence. The internal journal-manuscript snapshot already contains LSE, asymmetric-cost experiments and broader triage analysis; its status and overlap must be established before defining the Electronics contribution. To meet the 50% expansion rule, make a section/table/figure/result overlap map against the Springer chapter and any other submitted manuscript, then confirm with the editors how the increase is calculated. The new contribution must be separable in question, organization/model, protocol, data/intervention, results and discussion—not just added background text.

### Required prerequisites before any extension claim

- Authors confirm the intended AIAI baseline and the presentation version to cite.
- Data owner and relevant institutions approve access, reuse, publication and any linkage to analyst-level records; resolve contract, GDPR, employment, ethics and retention requirements.
- Obtain the data dictionary, label-generation process, competence/expertise definitions, code/model/configuration and permission to reproduce or extend the baseline.
- Determine whether service duration, assignment, queue, training, mentor, override and outcome fields exist; none is established by the paper’s summary fields.
- Define the scientific estimand, non-AI/current-practice baselines, units of replication, uncertainty and costs before looking at confirmatory outcomes.
- Prepare a truthful Data Availability Statement and code/data release plan. Do not promise open data; use an access-controlled or restricted-data statement only when justified and approved.

## 8. Source citations

- Published article: Lázaro et al., Springer chapter, DOI [10.1007/978-3-032-30805-4_11](https://doi.org/10.1007/978-3-032-30805-4_11), especially pp. 150–164; dataset pp. 152–154; feature and label pipeline pp. 155–157; evaluation pp. 157–158; experiments pp. 159–162; conclusion p. 162.
- Full volume: [Artificial Intelligence Applications and Innovations, AIAI 2026, Part III](https://link.springer.com/book/10.1007/978-3-032-30805-4).
- Special Issue: [Electronics — “Timely AI Advancements and Interdisciplinary Synergies for Intelligent Modeling”](https://www.mdpi.com/journal/electronics/special_issues/MET7IZ3S8B) and [official flyer](https://www.mdpi.com/journal/electronics/special_issue_flyer_pdf_v2/MET7IZ3S8B).
- Journal requirements: [Electronics Instructions for Authors](https://www.mdpi.com/journal/Electronics/instructions), including mandatory Data Availability Statement.

The AIAI contribution should be cited as the published Springer chapter, not as an unpublished HLS result. The HLS project status remains preparatory; this analysis itself adds no experimental evidence.
