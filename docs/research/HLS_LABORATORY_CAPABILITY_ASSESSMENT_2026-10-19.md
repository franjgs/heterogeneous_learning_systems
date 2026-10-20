# HLS Laboratory Capability Assessment and Published-Method Selection

**Date:** 2026-10-19  
**Decision:** **GO — bounded implementation and measurement, not a new simulator or a general literature review.**  
**Status:** design only; no implementation or experiment was performed for this assessment.

## 1. Purpose and recovered decisions

This assessment uses the existing literature and engineering work as prior evidence. It does not repeat the October 19 novelty, benchmark, or capability audits.

- The primary-source selection report reviewed Nembhard, Borgonjon–Maenhout, Baccara–Lee–Yariv, MixLLM, System-1.x and Liu et al. It rejected calling the extant contextual router a MixLLM reproduction; the HLS selector, predictor, training, cost and latency semantics differ. See [Literature Reproduction Selection](../experiments/HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md), especially §§2–4.
- The targeted search reviewed Cavenaghi et al. (2021), Mettler et al. (2016) and Cheung et al. (2022). It found adaptive benefits in their own settings, but no direct HLS reproduction target matching a dynamic organizational allocation and a strong fixed organizational baseline. See [Targeted Adaptive-Advantage Search](../experiments/HLS_TARGETED_ADAPTIVE_ADVANTAGE_LITERATURE_SEARCH_2026-10-19.md). Those works are not selected here because they do not jointly fill the requested expert-selection and deliberation roles.
- Chen, Hewitt and Thomas (2018) has a complete local paper and formal/compatibility audits. It studies finite-horizon multi-period technician assignment with task-specific experience, stochastic customers, ADPBF and one-day-lookahead ADPOL. The audit found no verified code/instance archive and rated a full reproduction high-effort; current N×K actions/objectives are not the Chen scheduling model. It remains a useful related benchmark, but is not selected for this bounded two-method extension. See [full-text audit](HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md), [compatibility audit](../experiments/HLS_CHEN_SIMULATOR_COMPATIBILITY_AUDIT_2026-10-19.md), and [investment assessment](HLS_BENCHMARK_INVESTMENT_ASSESSMENT_2026-10-19.md).
- G1/G2/MIS/G3/G3-H/RQ0, Campaign 2, and HLS-G0-C6 already provide static-organization, individual learning, joint/selected information, demand, and anticipatory-development evidence. C6 is now **CLOSED — STOP**; do not reopen it as a substitute benchmark. See [C6 closure](../experiments/HLS_G0_C6_CLOSURE_2026-10-19.md).

The assessment therefore focuses on methods already considered that fill two specific capability roles: contextual selection among heterogeneous experts, and adaptive allocation of computational deliberation between fast and slow planning.

## 2. Current capability matrix

Status describes executable repository behavior, not semantic equivalence to the cited research.

| Published mechanism / requirement | Existing HLS support | Gap | Proposed modification | Experimental justification |
| --- | --- | --- | --- | --- |
| Heterogeneous expert competence and complementary skills | **SUPPORTED, bounded.** `OrganizationConfigNK` / `OrganizationStateNK` represent N agents × K competence/resource cells; G0/RQ0 has a separate small competence state. | Agent competence is not the same as an LLM/model’s query-specific quality. | Preserve both meanings; use `CandidateSpec` for method-routing benchmarks, not an implicit NK-agent adapter. | Prevents using one ontology to distort either source method. |
| Sequential heterogeneous tasks and changing demand | **SUPPORTED.** N×K has `ProblemSpecNK`, sequence runners and `generate_environment_trajectory_nk`; `synthetic/c5.py` supplies stationary, scheduled nonstationary and Markov task demand. G0/RQ0 has finite-horizon stochastic task demand and exact solvers. | Existing benchmarks do not automatically reproduce either MixLLM’s query stream or System-1.x maze/Blocksworld tasks. | Add source-specific dataset adapters and frozen task/context streams in independent experiment modules. | Required to compare task/query order under common, reproducible exogenous inputs. |
| Contextual information and partial observability | **PARTIALLY SUPPORTED.** N×K policies receive an `NKDecisionView`; the N×K estimator reuses `SkillPosterior` and `update_skill_posterior` from the dynamic lab. `QuerySpec.context` is observable in contextual routing. G0 exact controllers are full-model-information references. | Context schemas and hidden variables are domain-specific; G0 exact state must not leak to an online router. | Explicit per-method observation views, feature-version manifests and tests that prohibit labels/future outcomes. | Reproduces each paper’s information boundary and distinguishes estimator from oracle. |
| Selecting one expert/candidate | **SUPPORTED as a generic HLS interface; paper method only partially supported.** `contextual_router.py` has candidate-specific ridge quality/cost estimates, selected-only feedback and a threshold/cost selector. N×K allocates divisible effort across agents; Nembhard has its own router. | HLS selector is **not MixLLM**: no MixLLM score, query-tag pipeline, paper predictor/update pipeline or waiting-time model. NK divisible allocation is not query-to-one-candidate routing. | Add a separate `MixLLMMethod` implementation/adapter beside (not replacing) the current HLS router; preserve paper score, predictor/update stages and selected feedback. | Individual validation targets MixLLM’s published offline/online-feedback comparison. |
| Combining experts / coordination | **PARTIALLY SUPPORTED.** NK aggregates productive outputs from multiple agents and has P0/P1/P2 coordination/teaching actions. Contextual routing selects one candidate per query, not answer-level ensemble combination. | Neither NK aggregation nor teaching is LLM answer fusion; System-1.x subgoal decomposition is another distinct operation. | Do not add answer fusion initially. Expose each complete solver as a candidate and preserve the System-1.x planner’s internal decomposition. | Keeps the first interaction limited to method composition rather than inventing a third mechanism. |
| Resource allocation and deliberation | **PARTIALLY SUPPORTED.** NK has individual effort caps/shared effort budgets and execution records consumption. Synthetic Campaign 3 FAST/DEEP/META records invocation and compute time. G0 has a finite development budget. | HLS META is not System-1.x: it predicts production advantage for HLS operators, not learned fast/slow plan decomposition. NK effort, monetary cost, search states and wall time are not interchangeable. | Add an isolated System-1.x task/model adapter; record search expansions and wall time separately. Do not price or merge units without an explicit mapping. | Reproduce System-1.x on its own maze task and compare quality/computation trade-offs. |
| Execution, cost, feedback and adaptation | **PARTIALLY SUPPORTED.** Contextual synthetic executor emits selected quality/cost feedback; Nembhard ADAPTIVE estimates productivity; dynamic N×K tracks competence estimates; campaign traces support paired replay. | No common source-faithful evaluator/pipeline for MixLLM quality, token-dollar cost and latency, or System-1.x plan validity/search effort. | Add source-versioned outcome evaluators and independent random streams; keep raw method-specific metrics. | Needed to measure adaptation, not just execute varying decisions. |
| Reproducible policy comparison | **SUPPORTED in bounded runners.** N×K trajectory generation and replay metadata; C6 common exogenous replays; common experiment envelope; Campaign 3 matched contexts/innovations and manifests. | No single shared data/model artifact or compute normalization across the two published methods. | Use separate original-method run manifests first; interaction uses the same query stream and frozen candidates, paired by context and environment seed. | Makes individual reproduction and composition auditable without claiming cross-paper metric equivalence. |

## 3. Two selected published methods

### A. Adaptive expert selection: MixLLM

**Selected.** Wang et al., “MixLLM: Dynamic Routing in Mixed Large Language Models,” NAACL 2025, DOI [10.18653/v1/2025.naacl-long.545](https://doi.org/10.18653/v1/2025.naacl-long.545). Its target is query-to-LLM routing using query tags, per-model quality/cost predictions, a quality/cost/latency meta-decision, and continual updates from observed feedback. The local paper/register and prior audit describe Table 1’s offline-only versus refined-feedback and binary-feedback comparison. The HLS contextual router is a useful interface/evaluation reference but not a reproduction; implement the source method separately and retain the existing threshold/ridge router as an HLS comparator.

**Artifact check (incremental):** the scoped search verified ACL’s primary paper record/PDF, but did not locate a public official implementation of this *routing* MixLLM. Search results also surfaced a Microsoft repository named MixLLM for mixed-precision quantization; that is a different paper and must not be mistaken for the router. The paper-specific query-response labels, candidate outputs, data split, predictor training artifacts and full evaluation bundle remain a pre-execution dependency. The official ACL record identifies the paper and proceedings metadata ([ACL Anthology](https://aclanthology.org/2025.naacl-long.545/)); no code/data availability beyond the evidence in the existing audit is claimed.

**Minimum source-faithful first target:** reproduce the method pipeline and the paper’s bounded offline-only / refined-selected-feedback / binary-feedback contrast on the source’s frozen split and candidate outputs. If these inputs cannot be obtained, do not call a synthetic ridge-router run a reproduction; the HLS method can only be reported as a conceptual adaptation.

### B. Adaptive deliberation allocation: System-1.x

**Selected.** Saha et al., “System-1.x: Learning to Balance Fast and Slow Planning with Language Models,” ICLR 2025. System-1.x learns to decompose a plan into subgoals and route subgoals between fast direct generation and slower explicit search, then composes the subplans. It is deliberation allocation inside a planner—not worker scheduling, N×K resource allocation, or competence learning.

**Artifact check (incremental):** the official [ICLR proceedings paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/605e59e78284907aa4fce5280838def3-Paper-Conference.pdf) links to the authors’ [System-1.x repository](https://github.com/swarnaHub/System-1.x). The repository describes PyTorch code, includes `data`, `models`, maze/Blocksworld source folders and training/evaluation scripts. Thus a reproducible Maze Navigation target is materially more actionable than a paper-only candidate; dependency/model-download and compute preflight are still required. The paper and repository were already identified in the prior review; this is an artifact-availability verification, not a new source survey.

**Minimum source-faithful first target:** reproduce the paper’s Maze Navigation comparison using its data, scripts, checkpoint/training setup and reported plan-validity/search-state metrics, starting with System-1, System-2 and System-1.5. Keep the paper’s exact split and training recipe; do not substitute HLS META-VOC.

### Why not Chen et al. (2018) here

Chen is the strongest workforce/learning-by-doing reference already audited, but it does not fill either requested method role directly: its ADPBF/ADPOL policies optimize technician-to-request schedules with experience-dependent service times, not contextual expert selection or fast/slow subgoal planning. Its separate request/service-time environment, missing verified code/instance package, high implementation burden, and action/objective mismatch make it a poor companion for this bounded pair. The prior compatibility/investment audit remains authoritative; this document does not repeat its mathematical review.

## 4. Minimal experimental extension

### Problem definition

Use two linked but explicitly different validation domains, followed by one composition pilot. For each query/planning task `q_t`, an eligible solver `i` returns an executable answer/plan. The environment measures declared outcome quality `Y_t` and resource diagnostics `C_t`; a selected-only feedback event updates the adaptive method for later tasks. Candidate quality truth and outcomes for unselected candidates remain evaluator-only. In the System-1.x reproduction, the original fast/slow decomposition is internal to that method. In the interaction pilot, System-1.x solver variants can be candidates to the MixLLM router, but such routing on maze contexts is a **cross-domain adaptation**, not reproduction of MixLLM’s RouterBench experiment.

Do not force query quality, HLS competence, production, plan validity, search states, latency and money into one quantity. For the interaction pilot, report plan validity as quality, actual billed inference cost only if a common billable meter exists, and wall time/search expansions as separate resource diagnostics. A hard budget must use a declared meter; otherwise compare quality-resource Pareto outcomes rather than a fabricated scalar score.

### Reuse and minimum new components

Reuse `contextual_router.py` records/selected-feedback executor patterns, the common run/trace contract, deterministic dataset manifests, paired replay utilities, and Campaign 3’s compute accounting patterns. Reuse the official System-1.x implementation as the algorithm source for its reproduction rather than translating its learned controller into HLS META.

Add only isolated benchmark adapters and runners: (1) frozen MixLLM dataset/candidate-response loader, method-specific predictor/update and selector implementation if source code remains unavailable; (2) pinned System-1.x runner/checkpoint/data manifest; (3) one composition adapter that treats completed planner variants as candidates and records only selected online outcomes. No universal simulator, changes to `ProblemSpecNK`, P0/P1/P2, MIS-v2, Nembhard, G0/RQ0 or the current contextual router are needed.

### Comparisons and validation sequence

1. **MixLLM individual validation:** paper-defined offline-only vs refined selected-feedback vs binary-feedback arms; source paper’s fixed/single-model and routing baselines as required. Reuse the paper’s query stream and split. Validate selected-only feedback, score calculation, predictor fitting and every published metric before interpreting outcome.
2. **System-1.x individual validation:** source-defined fast-only System-1, slow/search System-2, and learned System-1.x/System-1.5. Reuse official Maze Navigation data/splits and training/evaluation commands. Validate trace subgoals, fast/slow assignment, valid plans and search-state accounting. Blocksworld is optional, not required for the first bounded reproduction.
3. **First interaction pilot (after both individual gates):** use a frozen maze-task stream with candidates `{System-1, System-2, System-1.x}`. Compare (a) best fixed candidate chosen on training split, (b) MixLLM-style adaptive query selection, and (c) each candidate alone. System-1.x remains internally unchanged. Train/query features and candidate outcomes must be generated only from the training split; in the held-out stream, the router sees context and selected-candidate feedback only. Pair all policies on identical task order. Report plan validity, search states, wall time, and any genuinely metered monetary cost separately. Mark the result an HLS composition/adaptation, not reproduction of either published paper.

This pilot tests complementarity: whether contextual routing selects the deliberation mode/system suited to task context, beyond either a fixed solver or System-1.x alone. It is not guaranteed to improve quality or cost.

### Controls, reproducibility and stop gates

Freeze paper version, official repository commit, dependencies, model/checkpoint hashes, dataset split, task order, feature transform, candidate set, quality evaluator, price/cost meter, CPU/GPU/software, random seeds and training budget. Separate training, calibration and held-out test data. Preserve independent policy random streams and common exogenous task sequences. Report paired task-level deltas and intervals only at the independent task/run unit; do not count subgoals as independent episodes. Log per-task context, selected candidate, predictions/evidence, reason, realized result, cost/resource diagnostics, update timing and artifact hashes.

Stop before implementation of the MixLLM reproduction if paper-specific response records/split or necessary model/evaluator details cannot be obtained. Stop the interaction pilot if method-level validation fails, source licenses/model access prevent execution, or a shared metric requires changing an algorithm. These are bounded artifact gates, not invitations to repeat the literature audit.

## 5. Effort and calendar estimate

Relative engineering estimate, assuming one engineer and no new core architecture; not a measured runtime forecast:

| Work package | Relative effort | Calendar allowance | Gate |
| --- | --- | --- | --- |
| Freeze/verify MixLLM inputs and exact method contract | Medium–High | 3–5 working days | If required inputs unavailable, stop faithful reproduction; do not replace them with synthetic truth. |
| MixLLM isolated implementation/adapter and paper-metric checks | High | 1–2 weeks | Match source-defined calculations and data flow before any performance claim. |
| System-1.x environment/dependency smoke and bounded source reproduction | Medium–High | 1–2 weeks | Confirm model access/training feasibility; reuse author code/data. |
| Candidate composition adapter and paired pilot | Medium | 3–5 working days | Begin only after both individual method gates pass. |

These work packages overlap in calendar if conducted serially/with shared test infrastructure; overall planning allowance is approximately **3–5 weeks**, conditional on MixLLM source artifacts and System-1.x model/dependency feasibility. Largest risk is data/model artifact access, not simulator-core complexity. Do not schedule an extensive campaign before the small reproduction gates.

## 6. Recommendation

**GO — implement the two selected published methods as isolated benchmark modules, then perform the bounded composition pilot only after individual validation.**

Selected methods:

1. **MixLLM** — adaptive expert/query selection with selected-outcome feedback.
2. **System-1.x** — learned allocation of subgoals between fast and slow planning.

The existing HLS laboratory already supplies useful context, candidate, selected-feedback, task-stream, effort/compute-trace and reproducibility patterns. It does not yet reproduce either paper. The minimum investment is two method-specific adapters/runners plus source-faithful evaluation and one small composition adapter; no general architecture or new HLS strategy is justified. The GO decision is bounded by the artifact and individual-validation stop gates above and does not claim that the combined method will outperform its fixed comparators.

## References and project evidence

- Wang et al. (2025), MixLLM, [NAACL paper / DOI](https://aclanthology.org/2025.naacl-long.545/); local source record `docs/literature/ADAPTIVE_TRAINING_REFERENCE_REGISTER.md`, key `wang2025mixllm`.
- Saha et al. (2025), System-1.x, [ICLR paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/605e59e78284907aa4fce5280838def3-Paper-Conference.pdf); [official code and data](https://github.com/swarnaHub/System-1.x); local key `saha2025system1x`.
- Existing HLS MixLLM-inspired implementation and explicit non-equivalence: [contract](../engineering/HLS_MIXLLM_ROUTER_CONTRACT.md), [implementation record](../engineering/HLS_MIXLLM_ROUTER_IMPLEMENTATION.md), and [routing audit](../literature/audits/HLS_ROUTING_AUDIT_2026-10-17.md).
- Existing fast/deep/meta experiments and compute traces: [Campaign 3 FAST/DEEP/META](../experiments/CAMPAIGN_3_FAST_DEEP_META.md), [runner](../../experiments/synthetic/campaign3_fast_deep_meta/run.py), results under `results/campaigns/campaign3_fast_deep_meta/`.
- Chen et al. full-text mathematical and engineering compatibility records linked above; they remain prior work, not a selected method in this decision.
