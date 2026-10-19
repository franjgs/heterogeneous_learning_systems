# HLS literature reproduction selection — 2026-10-19

**Decision: STOP before execution.** No reviewed experiment meets the project's
acceptance condition for exact or defensibly approximate reproduction with the
currently validated HLS implementation and available inputs. MixLLM's §4.3
continual-training comparison (Table 1) is the strongest *candidate screened*
because query-to-candidate routing and selected-only feedback resemble an HLS
execution surface. It is **not selected as an authorized reproduction**: the
existing router is expressly a different synthetic mechanism, and required
primary data/model artifacts and implementation details are not established.
This is a literature-selection outcome, not a negative result about HLS
capability or MixLLM.

No simulation, campaign, or code change was made. HLS Laboratory remains
**PARTIAL**. A later proposal must first resolve the blockers in §8 and obtain
PI authorization; do not describe the HLS contextual router as MixLLM.

## 1. Scope and evidence standard

Primary sources were read in the locally retained source versions listed in
the [literature register](../literature/ADAPTIVE_TRAINING_REFERENCE_REGISTER.md)
and checked against publisher/proceedings records. Page references below are
the printed journal/proceedings pages when available; “PDF p.” means the
source file's page index. Local PDFs remain reference material and are not
included in this change. The Liu et al. (2017) primary PMLR PDF was consulted
from the official proceedings source, not retained in the repository.

Prior HLS source audits are used for implementation pointers, not as substitutes
for the papers: [routing audit](../literature/audits/HLS_ROUTING_AUDIT_2026-10-17.md),
[Nembhard fidelity review](../literature/audits/HLS_NEMBHARD_FIDELITY_AND_CONTRACT_REVIEW_2026-10-17.md),
[cross-model matrix](../literature/audits/HLS_CROSS_MODEL_COMPARABILITY_MATRIX_2026-10-17.md),
and the [adaptive capability validation](HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md).
“Reproduction” here means preserving the source model, experiment, baselines,
data, and outcomes—not merely implementing an equation with related terms.

Classification used below: **EXACT** preserves equations, assumptions,
protocol, data and metrics; **APPROXIMATE** reproduces a declared source subset
while bounding and documenting differences; **CONCEPTUAL** shares an idea but
changes a material mechanism or environment. Only the first two are eligible
for this first reproduction study. **INCOMPATIBLE** means a required construct
is materially different or absent; **INSUFFICIENT EVIDENCE** means source or
artifact details are not verified.

## 2. Primary-source candidate review

| Primary source and concrete experiment reviewed | Original problem, model, decisions, and information | Experimental evidence and reproduction inputs | HLS fit and classification |
|---|---|---|---|
| **Nembhard & Bentefouet (2015), §3–4, Tables 1–5, Figs. 1–2**; [publisher/DOI record](https://doi.org/10.1016/j.cie.2014.11.006). Local published article, 13 pages. | Worker selection, group formation, and assignment in serial/parallel production systems. Productivity Eq. (3) (journal p. 3) depends on direct experience plus indirect team experience \(T_{ijt}\), scaled by transfer receptivity \(h_{ij}\); decisions include selecting workers, grouping, and assigning groups to stations. It is a simulated known-parameter policy study, not online parameter estimation. | Empirical basis: 176,000 inspection items/75 workers from a radio production-line station; worker-level \((k,p,r,h)\) fit by nonlinear least squares, mean fit \(R^2=96\%\), then MVN-based pools are sampled. The simulation uses 3 machine types × 3 instances, selects 9 from 45, groups of 3, 10 policies at each of 3 stages (1,000 combinations), and 25 newly sampled populations; parallel and serial topologies (§3.1–3.5; journal pp. 3–5). Random allocation yields mean throughput 752 parallel/192 serial. Best policy means: 808.89 (SD 3.681; 1.15% gap) parallel and 259.07 (SD 7.670; 6.22% gap) serial (Tables 4–5, journal p. 6). | HLS has a bounded direct-experience curve and a declared HLS output convention, but not the source's team spillover, production topology, or three-stage policy experiment. Temporal interpretation issues are recorded in the fidelity review. **INCOMPATIBLE** for this published experiment; implementing the curve alone is conceptual adaptation, not reproduction. |
| **Borgonjon & Maenhout (2024), §§3, 5–6, Tables 2–5, Figs. 5–10**; [publisher/DOI record](https://doi.org/10.1016/j.cie.2023.109784). Local published article, 19 pages. | Integrated days-off scheduling, personnel/task assignment, staffing, and training. Competence at task start is initial class competence plus \(\alpha\) times prior same-class task count minus day-indexed \(\beta\) forgetting (Eq. (3), journal p. 5); Eq. (4) adds internal training \(\gamma\) and shadow/apprentice training \(\epsilon\), subject to tutor competence. Competence maps through Eq. (1) and discrete task modes to durations (Table 2). The objective minimizes staffing/hiring requirements within scheduling and coverage constraints. | §6.1 (journal pp. 12–13): generated 7-day instances based on Krishnamoorthy–Ernst; Groups A/B/C each have 20 instances, 70/140/280 tasks, 5/10/20 input workers, tightness .30, average task duration 216; one worker per task. Defaults: \(\alpha=.10,\beta=.05,\gamma=.15,\epsilon=.135\), off-job gains \((\chi,\psi,\omega)=(1,.485,.315)\), transformation parameters \((a,b)=(12.5,18)\), shadow tutor advantage \(p=.15\). Table 4 reports proven-optimal rates for proposed method of 100%, 55%, 25% for groups A/B/C; Table 5 reports staffing counts (proposed 5.10, 8.70, 14.55 vs no-learning upper-bound 6.05, 10.30, 18.00). §6.2–6.3 (pp. 14–17) compare MIP, constructive heuristic, branch-and-price and sensitivity conditions. Paper says data available on request; no instance dataset/code registered locally. | HLS has competence, MIS-v2, resources and episode assignment, but lacks days-off scheduling, hiring/staffing objective, task windows/durations/modes, forgetting, source training variants and branch-and-price. Nembhard Direct is not this competence equation. **INCOMPATIBLE** without substantial new model/solver work and source instances. |
| **Baccara, Lee & Yariv (2023), §§2–6, Propositions 1–5**; [DOI](https://doi.org/10.1016/j.jet.2022.105587), [author source](https://www.lyariv.com/papers/TaskAllocation.pdf). Local file is a 44-page author manuscript dated 24 Nov 2022, not the final journal layout. | Continuous-time matching/queue model: Poisson clients at rate \(\lambda\); junior service value \(l\), no wait; senior service value \(h>l\), service rate/mass \(\mu\), waiting cost \(c\); junior-served work creates senior capacity through \(\mu=f(x)\). Decisions are centralized threshold/probability rules or discretionary client equilibrium; perfect/limited monitoring changes queue observability. | This is a theoretical paper: Propositions 1–5 characterize equilibrium/planner policies and comparative statics, including the linear technology case \(f(x)=ax\); it does not report a sampled computational experiment or empirical parameter estimate. Hence no “published numerical result” exists for an experiment to replay in this paper; a numerical illustration would require choosing parameters not prescribed as an experimental benchmark. The retained source is an earlier author manuscript, not final journal pagination. | HLS has neither event-driven queues, waiting-time utility, endogenous service capacity nor decentralized equilibrium. Its teaching transfer is a different state transition. **INCOMPATIBLE**; a newly parameterized illustration would be conceptual adaptation, not reproduction. |
| **Wang et al. (2025), MixLLM, §§3–4.8, Eqs. (1)–(22), Tables 1–3, Figs. 4–7**; [ACL Anthology primary record/PDF](https://aclanthology.org/2025.naacl-long.545/), DOI `10.18653/v1/2025.naacl-long.545`. Local NAACL paper, 11 pages. | Sequential query-to-LLM contextual routing. Query embeddings are tag-enhanced and unsupervised-fine-tuned (Eqs. 1–3); per-model response-quality and output-length/cost predictors (Eqs. 4–6); a score combines willingness-to-pay quality/cost, uncertainty, and queue-wait penalty (Eqs. 7–11). Offline refined feedback trains predictors (12–14); selected-model online feedback updates a shared contextual-bandit feedback model (15–22). The router observes context/predictions and runtime waiting state; outcomes of unselected candidates are not online feedback. | §4.1 (printed pp. 6–7): RouterBench, 36,497 queries/eight NLP datasets and 11 LLMs, extended by authors with Llama 3.1 8B/70B; 80/20 train/test; baselines include AutoMix, RouteLLM, Zooter, RouterBench, FORC, OptLLM, MetaLLM, random and individual models. Quality is [0,1], cost dollars, latency cap; seed 42, stream 100 queries/10 seconds, \(\tau=30\) s, wait updated every 10 s. Table 1 (p. 7) reports 80:20 response quality: offline-only 75.54%, refined-feedback 76.45% (reported improvement 1.21%), binary-feedback 75.93% (0.52%). Overall §4.2 reports at \(\lambda=1.4\) 97.25% of GPT-4 quality for 24.18% of its cost. No dataset/code artifact is identified by the local paper/register sufficient to reconstruct the exact paper pipeline; source relies on RouterBench plus authors' Llama response extension and external pricing/latency data. | Closest HLS decision contract: `src/hls/contextual_router.py` has contextual per-candidate quality/cost ridge prediction and selected-only feedback; synthetic executor in `src/hls/contextual_router_synthetic.py`. But it has a different selector (quality threshold then minimum cost), predictor/training, no tag embedding, no output-token-cost predictor, uncertainty scoring, wait queues/latency model, LLMs, RouterBench, or the published baselines. Its tests validate its own contract only. **APPROXIMATE only after substantial, declared changes and source artifact recovery; not currently defensible as approximate reproduction.** |
| **Saha et al. (2025), System-1.x, §§2–4, Appendix E, Tables 3–8**; [ICLR proceedings primary record and PDF](https://proceedings.iclr.cc/paper_files/paper/2025/hash/605e59e78284907aa4fce5280838def3-Abstract-Conference.html). Local ICLR paper, 28 pages. | Trains System-1, System-2, and a controller; controller decomposes plans into subgoals and routes each to fast generation or explicit search, with hybridization parameter \(x\). Input includes problem start/goal and generated/reference plans/search traces; inference concatenates subplans. This is planning composition, not query routing or HLS competence development. | §3 (printed pp. 6–7): generated 4K 5×5 mazes, 40% obstacles, optimal plan length 1–8, 3200/400/400 split; base Mistral-7B-Instruct-v0.2, LoRA rank 8, max 3 epochs, batch 4. Table 3 (Appendix E, p. 25): System-1.5 with subgoals 70.4% plan validity at 13.6 explored states; System-1 48.7% at 3.1; System-2 default 93.7% at 24.4; test-time controlled System-1.5 reaches 96.7% at 27.3. Paper gives code URL `github.com/swarnaHub/System-1.x`; source task generation and trained artifacts are distinct dependencies. | HLS has unrelated fast/deep and routing experiments, not the three trained planner/controller components, search-state budget, maze/blocksworld execution or plan-validity evaluator. “Fast/deep” names do not establish equivalence. **INCOMPATIBLE** with current HLS. |
| **Liu et al. (2017), Iterative Machine Teaching, §§3–7, Eqs. (1)–(4), Figs. 2–6**; [PMLR primary source/PDF](https://proceedings.mlr.press/v70/liu17b.html), pp. 2149–2158. Official PMLR PDF consulted; no repository copy. | Teacher sequentially supplies one labeled example per SGD iteration to a learner minimizing convex expected loss; teacher's information varies (omniscient, surrogate, imitation). Omniscient teacher uses current learner parameters/features/loss/algorithm and selects an example to reduce next-step parameter error (Eq. 4). | Experiments include synthetic Gaussian data and real image/vision tasks: MNIST binary classification, CIFAR-10 CNN final layers, and infant egocentric images (Figs. 2–7, §7 and appendices). Curves report objective/convergence, parameter distance or test accuracy; the inspected source does not provide a consolidated numeric table for plotted comparisons. Exact reproduction requires source splits, learner/training configuration and plotted data/code, not digitized estimates. | HLS directed teaching transfers competence between agents; it is not sequential labeled-example selection for SGD. No compatible learner, example pool, loss, or training trace. **INCOMPATIBLE**. |

The candidate review finds no source experiment satisfying the first-study
criterion. The classifications concern faithful reproduction, not whether a
paper is scientifically relevant or whether an HLS-inspired follow-up might be
useful.

## 3. Candidate selection and decision

MixLLM §4.3/Table 1 is the strongest candidate for *further feasibility work*
because the HLS contextual router already shares the abstract sequence
“context → candidate selection → execute selected candidate → receive its
feedback.” It has a quantitative online-feedback comparison, baselines, and a
published dataset description. This is only a structural resemblance.

It fails the no-new-model requirement for this first reproduction: substituting
HLS ridge predictors and its threshold selector changes the studied model;
implementing the paper instead requires query tag/embedding processing,
paper-specific quality/length predictors, uncertainty and waiting-time state,
the feedback-score network/policy-gradient update, LLM responses/evaluator,
and matching candidate/runtime data. Running the synthetic HLS router against
synthetic outcomes would be a **conceptual adaptation**, explicitly outside
the permitted reproduction classes. The paper's Table 1 additionally needs
the authors' exact split, candidate response records, model checkpoints or
training pipeline, and metric implementation. Those are not established as
available in this repository.

Therefore the recommendation is **STOP** for experiment execution and for
calling any current HLS run a reproduction. The selected candidate for a
future feasibility decision is MixLLM Table 1, not Nembhard by default. This
does not authorize implementing missing components. A PI may instead choose
another source after obtaining the relevant exact data and model artifacts.

### What original claim/result would be targeted if blockers are resolved

The bounded target would be Wang et al. §4.3, Table 1, the 80:20 offline/online
split: online refined per-selected-model feedback raises reported mean query
quality from 75.54% to 76.45%, while binary satisfaction feedback yields
75.93%; the table reports improvements of 1.21% and 0.52%, respectively. The
paper defines binary satisfaction as quality >0.7 and waiting time <15 s; its
stream and latency parameters are in §4.1.4. This is a comparison of the
authors' offline-trained router with/without online feedback, not a claim that
all adaptive routing wins and not an HLS result.

The paper does not report uncertainty intervals or a replication tolerance for
Table 1. A future protocol cannot invent a statistical tolerance. Until the
authors' split/seed/data and run-level results are recovered, the only source-
faithful numeric check available is the table's displayed precision; exact
matching of those rounded values is not a defensible standalone success rule.

## 4. HLS correspondence for the screened MixLLM experiment

| Original component | Original definition | HLS candidate and source | Correspondence | Existing evidence | Missing functionality / required action |
|---|---|---|---|---|---|
| Query stream and representation | Ordered query set; encoder embedding with InsTag tags/domains (§3.1–3.3, Eqs. 1–3). | `QuerySpec.context` in `src/hls/contextual_router.py`; `run_contextual_routing`. | **INCOMPATIBLE** representation; numeric context only, no query text/tags/encoder fine-tuning. | `tests/test_hls_contextual_router.py`; synthetic deterministic validation only. | Recover frozen preprocessing, tag corpus/model and embeddings; do not map HLS `ProblemSpecNK` to a prompt/query without an approved semantic contract. |
| Candidate set | Independently operated LLM candidates, with possible add/remove over time. | `CandidateSpec`, fixed candidate tuple in `contextual_router.py`. | **APPROXIMATE** finite candidate identity only. | Candidate validation/selection tests. | Exact paper candidate roster/checkpoints and version behavior. |
| Quality truth/feedback | Per-query, per-LLM response quality in [0,1], refined or thresholded satisfaction (§4.1.3, 4.3). | `ExecutionOutcome.observed_quality`, synthetic executor in `contextual_router_synthetic.py`. | **INCOMPATIBLE** evaluator/data. HLS synthetic linear functions are not answer-quality labels. | Outcome validation and selected-only update tests. | Obtain query-response-quality corpus and reproduce exact quality evaluator/labels. |
| Cost and latency truth | Dollar cost from input tokens + predicted output length; waiting-time model and \(\tau=30\) s cap (Eqs. 5–6, 10; §4.1). | HLS `observed_cost` is a simulated currency/query. | **INCOMPATIBLE** units and dynamics. HLS has no tokens, runtime queue, LLM latency, or zero-quality timeout rule. | Budget-overrun tests cover synthetic cost only. | Source price snapshot, prompt/response lengths, latency data/simulation and queue evolution. |
| Quality/cost predictors | Per-LLM RF quality; model-dependent MLP/RF/KNN response length (§4.1.4); online updates Eqs. 12–14. | Separate per-candidate ridge states (`RidgeState`) in `contextual_router.py`. | **INCOMPATIBLE** learning model. | Hand-computed ridge tests support HLS's own estimator, not source models. | Implement paper predictor/model training only after explicit authorization and exact hyperparameters/data are fixed. |
| Meta decision | Argmax weighted tradeoff + uncertainty bonus − exponential waiting penalty (Eqs. 7–11). | Quality-threshold/min-predicted-cost rule in `ContextualQualityCostRouter.decide`. | **INCOMPATIBLE**, not a harmless baseline swap. | Selector tests verify HLS contract. | Exact \(\lambda,\alpha,\beta,\gamma,\xi,\tau\) and queue traces from source experiment; implement source decision, not reuse selector. |
| Online feedback learning | Selected-candidate feedback updates quality/length predictors and shared 3-layer MLP with contextual policy gradient (Eqs. 15–22); refined feedback and binary satisfaction are distinct arms. | `observe` updates only selected candidate's ridge predictors. | **INCOMPATIBLE** update mechanism. | Selected-only and temporal-order tests. | Source network, initialization, optimizer/state, reward encoding and online split. |
| Baselines and result | §4.1.2 baseline systems; §4.3 Table 1 compares offline-only/refined/binary feedback under same split and comparable cost. | No HLS equivalents for the paper's individual LLMs or baseline routers. | **NOT IMPLEMENTED**. | None for this experiment. | Obtain/recreate all required baseline predictions under the same data and latency rules; otherwise do not claim reproduction. |

Existing HLS routes are meaningful for other questions: N×K/MIS-v2 and
Nembhard model agent/task production and state evolution; the contextual route
models a synthetic quality/cost query decision. They are not interchangeable.
In particular, production is not response quality, HLS effort is not dollar
cost, and candidate feedback does not imply candidate capability learning.

## 5. Bounded source-faithful protocol target (blocked, not executable)

This section freezes what would need to be reproduced, not an authorization or
implementation proposal.

| Protocol element | Source-prescribed target | Readiness |
|---|---|---|
| Experiment | MixLLM §4.3, Table 1, 80:20 offline:online. | Identifiable. |
| Data | RouterBench 36,497 queries/eight NLP datasets plus authors' Llama 3.1 8B/70B responses, labels and prompt/response lengths; exact split and rows per run. | **BLOCKED:** exact data snapshot, release/version, filtering and split IDs not established. |
| Model | Tag generation/domain clustering and encoder (Eqs. 1–3); quality RF per model; response-length model type per candidate (RF/MLP/KNN); shared dynamic-feedback MLP; uncertainty matrices. | **BLOCKED:** complete preprocessing, model hyperparameters/checkpoints, optimizer and training code/artifacts not established in repo. |
| Conditions | Offline-only vs online refined feedback vs online binary satisfaction. Satisfaction: quality >0.7 and wait <15s. Same 80:20 split and stream. | Identifiable conceptually; exact episode/query ordering and feedback timing need source artifact/code confirmation. |
| Decision and environment | Score Eqs. (7)–(11); use source wait penalty, queue/wait update every 10 s, 100 queries/10 s, \(\tau=30\) s; \(\alpha=.01,\beta=.1,\gamma=.1\); seed 42; learning rates \(\eta_1=\eta_2=1,\eta_3=.001\); candidate-specific prices/speeds. | Values reported in §4.1.4, but source-specific deployment replay state/data and exact implementations are unavailable here. |
| Outcomes | Table 1 mean query quality for all three splits; primary bounded target 80:20 values 75.54%, 76.45%, 75.93%. Report cost and latency separately as source does. | Values available at printed precision; run-level observations/uncertainty not reported in the paper table. |
| Repetitions/seeds | Paper states all random seeds are 42; no independent repetition count or confidence interval for Table 1 is stated. | Do not invent repetitions. Recover original code or author clarification; otherwise report single-protocol reproduction limitations, not sampling inference. |
| Comparison rule | Recreate all three arms using the same ordered query split, candidates, initialized training state, cost/latency data and source code version. Compare reproduced means against printed Table 1, disclose rounding and any non-determinism. | No justified tolerance can be fixed until exact artifacts and deterministic behavior are verified. If source pipeline cannot be recovered, stop rather than substitute HLS ridge. |

**Success criteria if the source pipeline becomes available:** (1) an
independent implementation passes equation/data/decision unit checks against
source-defined cases; (2) the exact 80:20 split and all three Table 1 arms are
reproduced with the original candidates and evaluator; (3) per-arm query-level
quality, cost, and latency outputs reproduce the displayed table at its
published precision, with deviations and uncertainty reported; and (4) no
unselected-candidate outcomes enter online updates. These criteria do not
claim the online arms must be better on a new sample. The paper supplies no
variance estimate, so a statistical equivalence margin is unresolved and must
not be fabricated.

**Failure conditions:** missing/unverifiable data or split; mismatch in model
or queue/latency semantics; use of HLS's alternate selector/predictors while
calling it MixLLM; counterfactual leakage; or inability to reproduce the source
baseline. A result that differs from Table 1 after exact inputs/code are
verified is a reproduction discrepancy to report, not a reason to tune until
agreement.

**Preflight before any future authorization:** verify source/data availability
and licence; freeze data hashes, split IDs, query stream, candidate versions,
pricing/latency snapshot and source commit; independently test Eqs. 4–22 and
queue accounting; reproduce the source's baseline/oracle and metric aggregation;
run one tiny conformance fixture only after authorization; estimate cost from
the actual source model/runtime. None of these checks was executed as an
experiment in this review.

## 6. Why alternatives were not selected

* **Nembhard–Bentefouet:** closest to HLS's Nembhard Direct state variable, but
  the source experiment is a joint selection/grouping/assignment and
  direct-plus-indirect team-learning study. Current HLS implements only a
  bounded direct curve adaptation; the source production topology and full
  policy stack are absent. Re-running the HLS curve would repeat neither the
  paper's state nor its experiment.
* **Borgonjon–Maenhout:** strong, fully specified staffing benchmark and
  reported quantitative comparisons, but requires the integrated scheduling,
  mode, forgetting, training, and branch-and-price model absent in HLS; exact
  generated instance files/code are not locally registered (paper says data
  on request).
* **Baccara–Lee–Yariv:** rigorous analytical queueing/matching result, but its
  continuous-time arrivals, queue length, service process, training capacity,
  and equilibrium/planner distinction have no HLS implementation. Its retained
  text is an earlier author manuscript, so journal-version equation/page
  reconciliation is also needed before a numerical reproduction.
* **Liu et al.:** iterative supervised-example teaching of an SGD learner is
  semantically different from HLS's directed competence-transfer mechanism;
  HLS lacks the learner, example pool, model/loss and teaching algorithms.
* **System-1.x:** requires trained LLM planner/controller adapters, symbolic or
  neural search traces, subgoal generation, Maze/Blocksworld generators and
  plan-validity evaluation. Existing HLS fast/deep labels do not reproduce
  those components. The paper reports an official code URL, but an external
  codebase is not an existing HLS implementation and requires separate
  artifact/version verification.

## 7. Literature boundary and scientific limitations

The 135 focused tests and saved integrated validation show selected HLS paths
execute reproducibly; they do not reproduce any candidate paper. The E1/E2
results and their limits are summarized in the canonical validation report;
they are not substitutes for the original sources reviewed here. This task
does not alter or reinterpret E1/E2 evidence.

The MixLLM Table 1 result is an author-reported benchmark result over a
particular query/LLM/data/runtime system. It is not evidence about HLS agents,
MIS-v2 competence, Nembhard productivity, or organizational coordination.
Even a faithful replication would verify that bounded result, not establish
general routing superiority or HLS external validity.

## 8. Missing information and decision gate

For the screened candidate, these are critical unresolved dependencies:

1. Exact RouterBench and Llama extension data release, licensing, row IDs,
   preprocessing and 80:20 split identifiers.
2. Original executable/code version and all model architecture, initialization,
   training, tag/domain, and feedback-network details sufficient to recreate
   Table 1. The article's equations/settings do not alone supply the complete
   pipeline.
3. Candidate-specific response-length, pricing, initial-latency, generation
   speed, and queue evolution data in the precise version used for Table 1.
4. Run-level outcomes, repetitions/variance or author guidance for a
   scientifically justified reproduction tolerance. Printed percentages
   alone do not determine such a tolerance.
5. A decision whether the reproduction is allowed to recover the published
   MixLLM pipeline as an external implementation (rather than modifying HLS's
   router). This is necessary to preserve semantics and is outside current
   authorization to implement models.

**Final recommendation: STOP.** Do not execute. Do not use the current HLS
synthetic router as a substitute and do not label any conceptual adaptation a
reproduction. The next permitted step is a documentary/source-artifact
resolution for the five dependencies above and PI selection/authorization; if
they cannot be resolved, select a different fully specified source experiment
or end this reproduction attempt. No new mechanism is justified by this
selection review alone.

## 9. Source and evidence index

* HLS code: `src/hls/contextual_router.py` (`ContextualQualityCostRouter`,
  `RidgeState`, `run_contextual_routing`); `src/hls/contextual_router_synthetic.py`
  (`SyntheticContextualEnvironment`); `src/hls/hls_lab_nk_nembhard.py`;
  `src/hls/hls_lab_nk_execution.py`; `src/hls/hls_lab_nk_policies.py`.
* HLS tests: `tests/test_hls_contextual_router.py`,
  `tests/test_hls_lab_nk_nembhard.py`,
  `tests/test_hls_lab_nk_execution.py`, plus the scoped registry listed in
  `results/analysis/hls_lab_validation/capability_registry.json`.
* Primary-source register and local PDF/version/SHA information:
  [`ADAPTIVE_TRAINING_REFERENCE_REGISTER.md`](../literature/ADAPTIVE_TRAINING_REFERENCE_REGISTER.md)
  and [`references.bib`](../literature/references.bib).
* MixLLM source audit and implementation boundary:
  [`HLS_ROUTING_AUDIT_2026-10-17.md`](../literature/audits/HLS_ROUTING_AUDIT_2026-10-17.md),
  [`HLS_MIXLLM_ROUTER_CONTRACT.md`](../engineering/HLS_MIXLLM_ROUTER_CONTRACT.md),
  [`HLS_MIXLLM_ROUTER_IMPLEMENTATION.md`](../engineering/HLS_MIXLLM_ROUTER_IMPLEMENTATION.md).
* Canonical bounded capability evidence:
  [`HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md`](HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md),
  `results/analysis/hls_lab_validation/integrated_validation_results.json`,
  `results/analysis/hls_lab_validation/capability_registry.json`.
