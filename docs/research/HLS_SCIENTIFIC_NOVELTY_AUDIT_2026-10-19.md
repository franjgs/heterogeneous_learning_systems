# HLS — Scientific Novelty and Prior-Art Audit

**Date:** 19 October 2026
**Purpose:** independent assessment of scientific overlap and research viability
**Repository branch inspected:** `feature/hls-laboratory-v1`
**Scope:** literature research and theoretical analysis only; no code, results, or experiments changed or run.

## 1. Executive scientific verdict

**Recommendation: ADJUST.** The broad proposition that adaptive task allocation in heterogeneous systems can interact with learning or changing capabilities is not a defensible novelty claim: it is established or substantially covered in workforce scheduling, learning-by-doing, multi-robot allocation, and nonstationary bandits. The more specific HLS question—when joint allocation and endogenous capability development has value relative to a carefully specified, sufficiently coordinated separate architecture—remains potentially researchable, but current HLS results establish only model-scoped boundaries, and the closest workforce literature already contains a closely related finite-horizon stochastic assignment problem with experience-based service times and ADP.

This audit does **not** clear a general HLS originality claim. Nor does it recommend stopping the programme. It recommends narrowing the claim to a precise comparison class and state-transition/reward structure, then checking it against the complete Chen et al. model and other workforce papers before investing in new theory or experiments.

**Closest threat to the integrated allocation–development question:** Baccara, Lee and Yariv (2023), *Task Allocation and On-the-job Training* (Journal of Economic Theory 207, article 105587; DOI [10.1016/j.jet.2022.105587](https://doi.org/10.1016/j.jet.2022.105587)). Its full accepted manuscript was inspected. It models tasks arriving over time, endogenous provider expertise through junior-to-senior training, and derives optimal centralized assignment and discretionary equilibrium outcomes under perfect and limited queue monitoring. It proves comparative statics for welfare, training, service quality and waiting. This is direct peer-reviewed prior art for endogenous expertise coupled to allocation and conditional organizational value. It does **not** compare against an optimized fixed task-to-agent map or HLS’s strong-SEP policy class: its decentralized comparator is client choice with queue/training externalities, and its state is an aggregate queue/provider composition under stationary Poisson arrivals, not a heterogeneous multi-skill workforce. Chen, Hewitt and Thomas (2018) is the closest computational workforce-scheduling threat: it models heterogeneous learning rates, task-specific experience, stochastic future demand and finite-horizon ADP; it reports ADP beating one-step lookahead, not an optimized stationary policy. Neither paper is equivalent to HLS, but together they substantially narrow the broad contribution claim.

**Other major threat to broad adaptive-allocation claims:** Emam et al. (2020), DOI [10.1109/ICRA40945.2020.9197283](https://doi.org/10.1109/ICRA40945.2020.9197283), directly studies heterogeneous robot teams, online performance feedback, changing/unknown suitability and reassignment. Its “evolving capabilities” are specialization estimates responsive to environmental/task-execution mismatch, not experience-acquired competence in the workforce-learning sense.

The HLS result set is appropriately bounded when read with its canonical caveats. RQ0 policy-class inclusion alone is a tautological upper-bound relation, not proof of a substantive advantage. Constructive strictness exists relative to a particular strong-SEP class in exact synthetic worlds; SEP-Omega equality in tested worlds shows that richer continuation information can eliminate the gap. G2 establishes a small action-dependent learning/value example with null controls; G3 reduces development value to standard assignment sensitivities; G3-H/C1/C2 are scoped counterexamples/reductions, not a general theory of adaptive organization. E1 and E2.1 do not answer the full HLS question.

## 2. HLS problem reconstructed

### 2.1 Formal problem class

**FACT — canonical question.** RQ0 asks whether dynamic allocation and competence development in heterogeneous systems improve long-run performance relative to architectures managing allocation and knowledge transfer separately. It explicitly requires strong separate-management comparators and disclaims policy-class nesting as a substantive result ([`docs/research_questions.md`, lines 3–38](../research_questions.md); [`docs/HLS_CURRENT_STATE.md`, §5–§8](../HLS_CURRENT_STATE.md#5-rq0-and-its-current-role)).

A general finite-horizon instantiation can be written:

\[
X_{t+1}=F(X_t,a_t,E_t,\xi_t),\qquad E_{t+1}\sim P(\cdot\mid E_t),
\]
\[
Y_t=R(X_t,E_t,a_t),\qquad
J_\pi(x_0,e_0)=\mathbb E_\pi\!\left[\sum_{t=0}^{T-1}\gamma^tY_t+G(X_T,E_T)\right].
\]

Here `X` may include agent capabilities, experience, resources, and/or beliefs; `E` is an exogenous task/demand regime; `a` may jointly specify task assignment and development actions; `ξ` denotes transition randomness; `I_t` is the information available to the policy. This is a *general organizing notation*, not one universal HLS objective or a claim that every HLS implementation contains every state. The implementation/protocol must name which variables are true state, observed state, estimates, and exogenous process in each instance.

The RQ0 comparison is not simply “joint policy versus a bad fixed rule.” In the current formalization, `Π_SEP ⊆ Π_HLS` under common world physics and information, giving `J_SEP,max ≤ J_HLS` by feasible-class inclusion. Strictness in a finite exact world occurs iff no HLS-optimal policy is strong-SEP-admissible on its own support. A separated router with exact action-conditioned continuation information (SEP-Omega) matches HLS in audited families. These are proved in [`docs/theory/rq0_routing_integration_boundaries.md`, §§2–9](../theory/rq0_routing_integration_boundaries.md), with the current scope summarized in [`docs/HLS_CURRENT_STATE.md`, lines 1040–1153](../HLS_CURRENT_STATE.md#6-what-is-established-for-the-current-rq0-formalization).

### 2.2 What HLS has and has not established

* **FACT — G2:** two agents, two tasks, two periods; task-1 performance changes only for the worker assigned that task; future terminal routing values the resulting capability state. D0 is no-evolution; D1 changes an individual state without changing efficient collective value; D2 has action-dependent development that changes future value. See [`docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md`, §§2–5](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md). This is an exact existence/null instrument, not a general empirical claim.
* **FACT — G3:** a 3-worker, 2-task, 2-period scenario using the MIS saturating law. Its phase-II result expresses development value exactly through learning increments and feasible assignment gaps; the authors’ own ground truth labels this a “strong reduction” to standard assignment sensitivity, not new assignment theory ([`docs/experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md`, §§1–9](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md)).
* **FACT — G3-H/C1/C2:** the local continuation proxy can fail when future assignment opportunities matter; C1 falsifies that shortcut and C2 reduces the corrected calculation to ordinary look-ahead/Bellman dynamic programming under its assumptions. These are useful boundary and falsification results, not a new general solution method; see [`docs/HLS_HISTORICAL_MEMORY_AND_NOVELTY_GUARD.md`](../HLS_HISTORICAL_MEMORY_AND_NOVELTY_GUARD.md) and [`docs/theory/HLS_DYNAMIC_THEORY.md`](../theory/HLS_DYNAMIC_THEORY.md).
* **FACT — E1 status boundary:** the supplied project history reports an exploratory 1,016-episode Nembhard-curve study, not reproduction of the source paper. The local WIP protocol/results examined describe a task-type-to-role FIXED map aligned to constructed productivity profiles, a true-state but one-period ORACLE, and estimate/exploration ADAPTIVE. This supports only the local contrast, not general failure of adaptive allocation. **Provenance caution:** `docs/experiments/HLS_NEMBHARD_PROTOCOL_REVIEW.md`, `docs/experiments/HLS_NEMBHARD_ADAPTIVE_ALLOCATION_PROTOCOL.md`, and `results/analysis/hls_e1/` are not Git-tracked at this revision; these are audit leads, not canonical published evidence.
* **FACT — E2.1 status boundary:** the supplied project history reports 33 deterministic cases in a decoupled 2-agent × 2-skill model, with no OPT-DYNAMIC advantage over globally optimized task-type-to-agent BEST-STATIC. The local protocol's structural argument is that, for each skill, cumulative reward as a function of allocation count is discrete convex under the monotone Nembhard curve, so an endpoint maximizer exists and independent skill endpoints are representable by BEST-STATIC. This is a model-scoped deduction. **Provenance caution:** `docs/experiments/HLS_E2_1_PROTOCOL.md`, `experiments/hls_e2/`, and `results/analysis/hls_e2/e2_1_results.json` are untracked local WIP at this revision; reported 0/33 is not promoted as canonical experimental evidence. It does not test all HLS adaptive capacity.

**INFERENCE.** HLS’s strongest plausible contribution is not “adaptivity works,” “experience matters,” or “joint decisions beat separated decisions.” It would need to be a nontrivial, useful characterization of *which restrictions on information, coupling, feasible action sets, and policy classes* create an irreducible long-horizon value gap, beyond known finite-horizon workforce ADP and ordinary policy-class/Bellman arguments.

## 3. Search methodology and evidence limits

### 3.1 Prior work incorporated, not repeated

The repository contains a broad code-reuse/cross-model audit, Nembhard mathematical extraction/fidelity review, a MixLLM/System-1.x routing audit, cross-model comparability work, and literature-reproduction selection. This audit uses the tracked scientific documents as an index and checks HLS-theory statements against canonical sources; it does not redo their component inventory. Additional local, untracked audit drafts were read only as contextual leads; they are not canonical evidence and are not relied on for the final scientific verdict.

The most relevant prior documents are:

* [`docs/experiments/HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md`](../experiments/HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md), which reviewed six candidate sources for an initial faithful reproduction and did not authorize one.
* [`docs/literature/audits/HLS_NEMBHARD_FIDELITY_AND_CONTRACT_REVIEW_2026-10-17.md`](../literature/audits/HLS_NEMBHARD_FIDELITY_AND_CONTRACT_REVIEW_2026-10-17.md), [`HLS_ROUTING_AUDIT_2026-10-17.md`](../literature/audits/HLS_ROUTING_AUDIT_2026-10-17.md), and [`HLS_CROSS_MODEL_COMPARABILITY_MATRIX_2026-10-17.md`](../literature/audits/HLS_CROSS_MODEL_COMPARABILITY_MATRIX_2026-10-17.md).

The local targeted adaptive-advantage search draft and differential capability-audit draft were present but untracked. Their leads were checked against primary sources where possible; their conclusions are not treated as established facts.

### 3.2 Additional search performed

Search focus: exact combinations of “multi-period technician scheduling,” “experience-based service times,” “learning by doing” plus assignment, “multi-skilled workforce dynamic assignment ADP,” “adaptive task allocation evolving unknown capabilities,” workforce learning/forgetting assignment, and nonstationary-bandit dynamic-regret literature. Backward-reference checking was performed through the selected articles’ stated related-work references where source text was available; forward-citation tracing is incomplete. The search is **targeted and high-priority**, not a systematic review with a registered database query, duplicate-screening log, or exhaustive citation graph. Novelty is therefore not finally adjudicated.

### 3.3 Primary-source access labels

* **Full primary text inspected:** Baccara, Lee & Yariv (2023), author-hosted 44-page accepted manuscript; Emam et al. (2020), arXiv version (7 pages), including equations (1)–(8), §§III–V and Figs. 2–6; Besbes et al. (2014), full NeurIPS paper, including model, regret definitions, Theorems 1–2 and experiments.
* **Primary publisher abstract/preview and bibliographic record inspected, not full text:** Chen et al. (2017, 2018), Annear et al. (2023), Valeva et al. (2017), Borgonjon & Maenhout (2024), Nembhard (2001), Nembhard & Osothsilp (2005), Luo et al. (2018), Cavenaghi et al. (2021), Mettler et al. (2016), Cheung et al. (2022). Local repository audits/extractions supplement but do not replace the unavailable full source where noted.
* **Primary full text not verified:** 2026 warehouse paper by Wang, Xiang and Chen, DOI [10.1016/j.tre.2026.105040](https://doi.org/10.1016/j.tre.2026.105040); only bibliographic/abstract-level secondary indexing was accessible during this audit. No detailed claim about its model/results is relied upon.

## 4. Verified prior art: mathematical and experimental substance

### 4.1 Baccara, Lee & Yariv — closest integrated allocation/training antecedent

**FACT.** The model has identical clients/tasks arriving over continuous time according to a Poisson process at rate \(\lambda\), an infinite pool of juniors, and a mass \(\mu\) of seniors. A senior provides service value \(h\), a junior value \(l\), with \(h>l>0\). Senior service forms an M/M/1-style FIFO queue with service rate \(\mu\); waiting yields cost \(cW\). If the long-run flow of clients served by juniors is \(x\), training determines the senior service-capacity proxy by \(\mu=f(x)\), where \(f\) is differentiable, weakly increasing, weakly concave and \(f(0)=0\) (paper §2, pp. 6–8). Thus assignment changes future expertise/capacity through training and changes queue delay, which feeds back into welfare.

For a stationary fraction (q) routed to seniors under limited monitoring, (x=(1-q)\lambda), (mu=f((1-q)\lambda)), and average client payoff is ((1-q)l+q[h-c\mathbb E W(q,\mu)]). The planner maximizes this subject to queue stability/training feasibility; in the discretionary case (q) is determined by client indifference rather than planner maximization. Under perfect monitoring the decision is a queue-length threshold, and the welfare objective accounts for the stationary distribution of the queue. This captures the paper’s actual economic trade-off; it is not HLS CES or a production sum.

Under **perfect monitoring**, policies condition on the senior queue length; the paper focuses on threshold rules sending clients to juniors when the senior queue reaches threshold \(k\) (§3.1). Under **limited monitoring**, policies use a constant probability/fraction \(q\) for senior service, with \(\mu=f((1-q)\lambda)\) (§3.2). The centralized social planner maximizes average client payoff subject to queue/training feasibility; discretionary clients choose providers in equilibrium. Proposition 1 characterizes the perfect-monitoring planner/equilibrium; Proposition 2 characterizes limited monitoring; Proposition 3 gives comparative statics; Corollary 2 (§6) shows centralized allocation routes weakly fewer clients to seniors and yields weakly greater senior capacity/training than discretionary allocation (strict under stated conditions). The authors attribute the gap to the queue-wait externality and the foregone junior-training externality. The paper’s abstract/conclusion report centralization gains are greater with higher arrival rates and more effective training, with monitoring improving welfare but sometimes reducing training. Full primary source: [author-hosted accepted manuscript](https://www.lyariv.com/papers/TaskAllocation.pdf); final publication [DOI](https://doi.org/10.1016/j.jet.2022.105587).

This is a **stationary stochastic equilibrium/steady-state model**, not a finite sequence of externally shifting task regimes. Heterogeneity is two provider seniority types generated endogenously at the population/service-capacity level, not an arbitrary agent-by-skill competence matrix. Its fixed arrival rate and identical task type intentionally simplify the environment. The comparator is decentralized client choice—not an optimized fixed task-to-agent map, not HLS strong SEP, and not a one-period heuristic. There is no reported randomized experimental campaign; the result is theoretical characterization/comparative statics. The paper itself (intro §1.2, p. 5) states that it was unaware of work combining assignment protocols and endogenous provider types at its writing; that is author-attributed historical context, not a current exhaustive novelty proof.

**Why this is the closest RQ0 threat.** It has the direct conjunction “assignment affects training, training changes future capability/capacity, and a centralized allocation policy is compared to a decentralized alternative with conditions for value gains.” Its theorem already establishes a meaningful organizational allocation/training benefit in its queueing model. HLS cannot claim this broad conjunction or the generic existence of coordination value as new. HLS still differs in multi-agent/multi-skill capability geometry, individual assignment-dependent learning, possibly nonstationary exogenous demand, explicit true-vs-estimated information, and comparison to a strong centralized modular/stationary architecture. Those differences are candidates for a narrower extension, not proof of novelty.

### 4.2 Chen, Hewitt & Thomas — closest finite-horizon workforce-ADP antecedent

**FACT.** Chen et al. define a multi-period technician/task scheduling problem. A set of heterogeneous technicians serve task types; each technician’s experience is tracked by task type and counts how many times that task was performed. Experience changes service time (greater experience means faster service); technician learning rates and initial experience are known. Current-day demand is observed for assignment, while later-day demand is stochastic/unrevealed. The objective is to minimize expected cumulative service times over a finite horizon, a productivity proxy. The 2018 paper uses ADP with a parameterized linear approximation of the cost-to-go, approximate value iteration and iterative regression; it compares against one-step lookahead that values experience only for the next day. The publisher’s abstract reports ADP outperforming that one-step baseline and computational insights including near-term productivity sacrifice to position future capacity. See the primary publisher pages: [2018 IJPE article](https://doi.org/10.1016/j.ijpe.2017.10.028), abstract and preview; [2017 C&OR model paper](https://doi.org/10.1016/j.cor.2016.12.026).

For clarity, this is the state/action/reward structure recoverable from the primary publisher preview—not a full equation transcription:

\[
S_t=(t,\{E_{kr,t}\}_{k\in\mathcal K,r\in\mathcal R},\text{current demand/availability}),
\quad a_t\in\mathcal A(S_t),
\]
\[
E_{kr,t+1}=E_{kr,t}+n_{kr}(a_t),\qquad
\min_\pi\;\mathbb E_\pi\sum_{t=1}^T\sum_{k,r} d_{kr}(E_{kr,t};\theta_k)\,n_{kr,t}(a_t).
\]

Here `d` is service time, `θ` learning parameters, and assignments are constrained by daily demand and technician availability. The expression is a *notation-level reconstruction from the publisher abstract/preview*, not a claimed verbatim article equation; the full paper is needed to validate exact notation, service-time formula, feasibility constraints, distributions, and all numerical tables.

**Interpretation.** This overlaps strongly with HLS’s joint long-horizon allocation/development concern. It does not establish that HLS’s exact (i) competence state, (ii) nonlinear production/CES evaluation, (iii) development-action/teaching architecture, (iv) strong-SEP comparison, or (v) partial-observation problem reduces to MTSP-ESTSC. A rigorous reduction would require mapping HLS skill/task cells to technician-task experience, HLS assignment to daily technician scheduling, HLS output/reward to negative service time, and matching feasible capacity, demand, transitions and information. That mapping is not currently established; HLS Nembhard Direct also makes per-cell productivity (P_{ik}(D)=k_{ik}(D+p_{ik})/(D+p_{ik}+r_{ik})), not the paper’s as-yet-unverified service-time formula.

### 4.2 Emam et al. — closest adaptive allocation under unknown/changing capability

**FACT.** In Emam et al., each robot has state/control dynamics \(\dot x_i=f(x_i)+g(x_i)u_i\). Task execution is encoded using robot/task cost functions (V_{ij}(x_i)); a specialization/suitability parameter (s_{ij}\ge0) weights robot state/task contribution. The allocation-and-control optimization (Eq. 6) balances desired global task-priority distribution, control effort and task slack subject to control-barrier and priority constraints. Specialization is updated from expected-vs-actual task progress:

\[
\Delta V_{ij}[k]=V_{ij}(x_i^{sim}[k])-V_{ij}(x_i^{act}[k]),\qquad
s_{ij}[k+1]=s_{ij}[k]+\beta_1\alpha_{ij}[k]\Delta V_{ij}[k]
\tag{Emam Eq. 7}
\]

with a separate slow recovery term in Eq. (8). The paper tests simulated and Robotarium scenarios, including unknown obstacle/terrain effects and an environment change. Source locations: [full primary arXiv paper](https://arxiv.org/abs/2003.03344), §§III–V, Eqs. (1)–(8), Figs. 2–6; peer-reviewed ICRA DOI above.

This is true state-responsive reallocation based on online feedback and uncertain suitability. But (s_{ij}) is a *specialization/effectiveness estimate* inferred from mismatch in modeled and actual robot progress. It is not a capability that grows because an agent repeatedly practices a task. Thus it overlaps HLS’s imperfect-information/adaptive-allocation direction, not directly MIS-v2/Nembhard endogenous learning. The paper demonstrates successful reassignment in examples; the examined source does not provide a controlled estimate of superiority over a globally optimized fixed policy with repeated-seed inferential statistics. Its high-level task allocation specification is supplied to the allocator, so it is not a general long-horizon assignment/development optimizer.

### 4.3 Annear et al. — dynamic multi-skilled workforce assignment

**FACT.** Annear et al. (EJOR 306(3), 1109–1125; DOI [10.1016/j.ejor.2022.08.049](https://doi.org/10.1016/j.ejor.2022.08.049)) model assigning a multi-skilled workforce dynamically to job-shop stations under stochastic demand and resource availability. Worker skills restrict eligible stations; machine utilization stages and stochastic processing/demand are part of the environment. The objective is manufactured glass surface area/productivity over a horizon. They formulate an MDP and use ADP with hill-climbing action selection; source abstract reports an average 15% improvement against the best-performing benchmark using real company data. The full article was not available for inspection, so exact baseline definitions, table values, runs, confidence intervals, and whether worker skills themselves evolve are **not verified here**. Based on the publisher abstract, the paper is strong evidence that dynamic assignment under stochastic job-shop conditions can improve on operational benchmark policies, but not yet evidence for endogenous learning-by-doing or an optimized stationary mapping.

### 4.4 Other directly relevant prior art

| Source (verified identity) | Established overlap | Important boundary/evidence limit |
|---|---|---|
| Valeva, Hewitt, Thomas & Brown (2017), “A two-stage stochastic programming approach to workforce assignment with learning,” IJPE 183, 194–207, DOI [10.1016/j.ijpe.2016.10.026](https://doi.org/10.1016/j.ijpe.2016.10.026) | Two-stage stochastic assignment with heterogeneous worker experience/productivity, learning, uncertain future demand; reports cross-training changes with demand uncertainty and inventory costs. | Publisher abstract/preview only. Two-stage stochastic assignment is not online policy learning; exact theorem/experiment scope needs full text. |
| Borgonjon & Maenhout (2024), “The impact of dynamic learning and training on the personnel staffing decision,” C&IE 187, 109784, DOI [10.1016/j.cie.2023.109784](https://doi.org/10.1016/j.cie.2023.109784) | Staffing, assignment, on-/off-job training, learning and forgetting over time; branch-and-price solution. | Accepted-manuscript abstract/metadata inspected, not full numerical results. Year is 2024 although DOI includes 2023. |
| Nembhard (2001), “Heuristic approach for assigning workers to tasks based on individual learning rates,” IJPR 39(9), 1955–1968, DOI [10.1080/00207540110036696](https://doi.org/10.1080/00207540110036696) | Heterogeneous individual learning rates already inform task assignment heuristics; article reports simulation gains under empirical productivity conditions. | Full text not inspected. Do not attribute the Nembhard–Bentefouet curve or full multi-period optimality to this paper. |
| Nembhard & Osothsilp (2005), “Learning and forgetting-based worker selection for tasks of varying difficulty,” JORS 56(5), 576–587, DOI [10.1057/palgrave.jors.2601842](https://doi.org/10.1057/palgrave.jors.2601842) | Worker selection under learning/forgetting and task difficulty. | Full text not inspected; no claim that this is dynamic organizational allocation under exogenous demand. |
| Besbes, Gur & Zeevi (2014), NeurIPS 27, 199–207, “Stochastic Multi-Armed-Bandit Problem with Non-stationary Rewards,” [primary proceedings source](https://proceedings.neurips.cc/paper/2014/hash/91ba7292e5388b90b58d0b839a7f19ec-Abstract.html) | Formal nonstationary reward model; only selected-arm feedback; variation-budget condition; dynamic oracle regret; matching minimax rate up to logarithmic factors. | No endogenous capability evolution or multi-agent assignment. Dynamic comparator is not “best static allocation”; this is bandit policy learning. |
| Luo, Wei, Agarwal & Langford (2018), “Efficient Contextual Bandits in Non-stationary Worlds,” COLT/PMLR 75, 1739–1776, [PMLR](https://proceedings.mlr.press/v75/luo18a.html) | Contextual online learning with change/drift and dynamic/switching-regret guarantees. | Abstract-level primary record checked; no organizational learning-by-doing model. |
| Cavenaghi et al. (2021), *Entropy* 23(3):380, DOI [10.3390/e23030380](https://doi.org/10.3390/e23030380) | Drift-aware bandit; Fig. 9 reports an adaptive algorithm responding to changing reward means; source code linked by authors. | It compares bandit algorithms, not task allocation against optimized fixed organization; reported averages/plots are not equivalent to strong fixed-policy evidence. See prior targeted review for bounded source-specific analysis. |
| Mettler, Massey & Kellman (2016), *JEP: General* 145(7), 897–917, DOI [10.1037/xge0000170](https://doi.org/10.1037/xge0000170) | Adaptive practice schedule compared to yoke-matched fixed schedules; credible fixed comparator in a human learning task. | Endogenous item/learner memory changes, not organizational assignment under exogenous demand. Results differ by outcome/timepoint. |
| Cheung, Simchi-Levi & Zhu (2022), *Management Science* 68(3), 1696–1713, DOI [10.1287/mnsc.2021.4024](https://doi.org/10.1287/mnsc.2021.4024) | Nonstationary pricing and dynamic regret; adaptive methods under temporal reward variation. | Fixed organizational allocation is not its main comparator; pricing response model differs from HLS. |
| Wang, Xiang & Chen (2026), DOI [10.1016/j.tre.2026.105040](https://doi.org/10.1016/j.tre.2026.105040) | Potential recent warehouse-picker dynamic capability assignment overlap. | Primary full text was inaccessible; treat as unresolved prior-art threat and obtain paper before novelty clearance. |

**Besbes et al. (2014) formal benchmark.** For (K) arms over horizon (T), arm (k) yields reward (X_t^k\in[0,1]) with time-varying mean \(\mu_t^k\); the policy observes only the selected arm’s reward. Their variation budget is
\[
V_T=\sum_{t=1}^{T-1}\sup_{k\in[K]}|\mu_{t+1}^k-\mu_t^k|,
\]
and dynamic regret is relative to the per-period best-mean arm, not one best fixed arm. Theorem 1 gives a minimax lower bound of order \(\Omega((K V_T)^{1/3}T^{2/3})\) in its stated range; Theorem 2 gives a restarted-Exp3 upper bound \(\widetilde O((K\log K\,V_T)^{1/3}T^{2/3})\). This rigorously separates a nonstationary reward problem and dynamic-oracle comparator from HLS’s joint assignment/endogenous-capability question; it should not be translated into a fixed-vs-adaptive organizational superiority claim. See the [full NeurIPS paper](https://proceedings.neurips.cc/paper_files/paper/2014/file/91ba7292e5388b90b58d0b839a7f19ec-Paper.pdf), model §2 and Theorems 1–2.

### 4.5 Adjacent papers from the earlier HLS reference set

These works matter to the scope of HLS, but their central problem is not the same as joint organizational task allocation and endogenous agent capability development.

* **Nembhard & Bentefouet (2015)** study selection, grouping and assignment with direct/indirect experience effects in serial/parallel production settings (DOI [10.1016/j.cie.2014.11.006](https://doi.org/10.1016/j.cie.2014.11.006)). The local mathematical extraction and fidelity review report ambiguities in temporal indexing and indirect-transfer recursion; HLS’s Nembhard Direct module explicitly adapts only a direct productivity curve and is not a full-paper reproduction. This work is prior art for experience-sensitive worker assignment, not evidence that the HLS adaptation reproduces their complete optimizer or experiment.
* **Liu et al. (2017), Iterative Machine Teaching**, ICML/PMLR 70:2149–2158 ([primary paper](https://proceedings.mlr.press/v70/liu17b.html)), studies a teacher sequentially choosing examples based on an iterative learner’s current performance, with convergence/teaching-complexity results and experiments. The teacher’s action is an information/example choice; this is not workforce task allocation, productivity learning-by-doing, or a multi-agent capability allocation model.
* **Wang et al. (2025), MixLLM**, NAACL 2025, DOI [10.18653/v1/2025.naacl-long.545](https://doi.org/10.18653/v1/2025.naacl-long.545), treats query-to-LLM selection as contextual routing with predictions of query-specific answer quality/cost and trade-offs including latency, using feedback/continued training. Candidates are models and observations are query outcomes; this is a router-learning antecedent, not agent capability acquisition through assigned work.
* **Saha et al. (2025), System-1.x**, ICLR 2025 ([primary proceedings PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/605e59e78284907aa4fce5280838def3-Paper-Conference.pdf)), learns a controller that decomposes planning into subgoals and allocates them between fast direct generation and slower search/planning components. It compares planner variants on Maze Navigation and Blocksworld; it is computational deliberation allocation within a planner, not allocation among workers whose capabilities evolve through experience.

These distinctions prevent “adaptive,” “teaching,” “routing,” or “planning” from being mistaken for mathematical equivalence. They also show that HLS’s modular-router and fast/deep capabilities have their own prior art and should be claimed only as specific adaptations, not new general mechanisms.

**Bibliographic correction.** “Chen et al. (2018)” refers to the IJPE ADP algorithm paper. Its closely related C&OR model paper appeared in 2017. They are separate publications with separate DOIs and should not be conflated. “Borgonjon & Maenhout” is a 2024 journal publication (online DOI year 2023), not a 2023 final publication.

## 5. HLS–literature comparison and reductions

| Antecedent | Same mathematical problem? | Exact/special-case mapping established? | Endogenous capability development? | Strong adaptive-vs-fixed conclusion relevant to HLS? |
|---|---|---|---|---|
| Baccara et al. 2023 | Dynamic assignment with on-the-job training, endogenous provider types, queue congestion, and central planner vs discretionary allocation. | **Not equivalent.** Aggregate junior/senior flow-training function and queue state differ from HLS’s individual N×K states and feasible assignment actions. | Yes, junior allocation/training changes future senior capacity. | Theoretical centralization value and comparative statics are established against client-choice equilibrium, not an optimized strong fixed HLS comparator. |
| Chen et al. 2017/2018 | Closest computational structure: finite-horizon worker-task assignment, stochastic demand and assignment-dependent experience/service time. | **Not established.** A possible special-case mapping requires HLS tasks→service jobs, capability→task experience, HLS output→negative service time, and exact matching of capacity, reward, information and transition. HLS’s Nembhard curve is not yet shown equal to their service-time law. | Yes, experience affects later service time; learning rates and experience are known. | ADP beats a one-step lookahead baseline per abstract, not proven here against optimized stationary task mapping/SEP. This prior art substantially limits broad HLS claim N3. |
| Emam et al. 2020 | Same broad adaptive heterogeneous assignment theme, different control problem. | **Incompatible as exact reduction** without replacing HLS task completion, robot dynamics and progress-based suitability update. | No learning-by-doing capability accumulation; online specialization parameter responds to performance/model mismatch. | Demonstrates adaptive reassignment in scenarios, but no verified strong optimized static comparator. |
| Annear et al. 2023 | Dynamic workforce assignment in stochastic job shop. | **Insufficient evidence** for equation-level equivalence; paper full model not inspected. | Abstract does not establish endogenous skill development. | Reports 15% over benchmark policies on industrial data, but exact comparator strength/statistical uncertainty not verified. |
| Valeva et al. 2017 / Borgonjon & Maenhout 2024 | Workforce allocation/staffing with learning/training and uncertainty. | **Insufficient evidence** pending full text and precise policy mapping. | Yes, learning; Borgonjon additionally training/forgetting per abstract. | Stochastic optimization / staffing results, not a verified general adaptive-vs-optimized-static theorem. |
| Besbes et al. 2014 / Luo et al. 2018 | Online decisions under changing rewards. | **Not the same problem.** Arms/contextual decisions can only map to HLS allocations after adopting bandit payoff/feedback semantics. | Reward process changes; agents do not gain task capability from assignment. | Strong benchmark/regret theory, but dynamic oracle vs stationary benchmark is a different comparator question. |

### Explicit non-equivalence: HLS current Nembhard Direct

Current HLS Nembhard Direct uses
\[
P_{ik}(D)=k_{ik}\frac{D_{ik}+p_{ik}}{D_{ik}+p_{ik}+r_{ik}},\quad
y_k=\sum_i e_{ik}P_{ik}(D_{ik})\Delta t,
\quad D_{ik}^{+}=D_{ik}+e_{ik}\Delta t.
\]
The last two expressions are explicit HLS operational conventions; they are not claimed as the original article’s full production/experience equations. In code, `nembhard_productive_outputs_nk` evaluates productivity from current `D_t` and scales assigned work by duration (`src/hls/hls_lab_nk_nembhard.py`, lines 167–210); `advance_nembhard_experience_nk` then applies `D_next=D_current+e·delta_t` (lines 213–237). See also [`docs/engineering/HLS_EXTERNAL_MECHANISM_INTEGRATION_01.md`](../engineering/HLS_EXTERNAL_MECHANISM_INTEGRATION_01.md). The learning curve alone does not make the full Nembhard–Bentefouet paper or Chen MTSP-ESTSC model equivalent to HLS.

### Policy comparison categories that must remain distinct

* **Fixed action/map:** decision does not change with current state, though a task-dependent static map need not be one constant action.
* **Stationary state-responsive policy:** same mapping from current state to action, recomputed each period; no parameter learning is implied.
* **Online estimator/adaptation:** decision uses estimates updated from realized feedback.
* **Dynamic reoptimization:** each-period optimization given state/information; may be myopic.
* **Offline dynamic oracle/DP:** knows full future sequence and optimizes trajectory; not deployable online.
* **Endogenous capability development:** assignment changes true future capabilities/productivity.

Chen ADP is long-horizon approximation using known experience/learning structure. Emam adjusts online suitability from execution mismatch. HLS Nembhard ADAPTIVE is a current-period router with a running mean of observed productivity and optional exploration; it does not learn (k,p,r) or optimize future value. These are not interchangeable meanings of “adaptive.”

## 6. Novelty claims N1–N8

| Claim | Assessment | Reason and boundary |
|---|---|---|
| **N1. Adaptive allocation in heterogeneous systems** | **ALREADY ESTABLISHED** | Established across heterogeneous MRTA (Emam et al.), multi-skilled workforce ADP (Annear et al.), workforce scheduling and bandits. HLS cannot claim this general capability as novel. |
| **N2. Adaptive allocation under evolving capabilities** | **SUBSTANTIALLY COVERED** | Chen et al. combine allocation with experience-dependent service times; Emam handles unknown/time-varying specialization. Their meanings differ, but the broad conjunction is prior art. |
| **N3. Joint optimization of allocation and endogenous capability development** | **SUBSTANTIALLY COVERED** | Baccara et al. characterize planner allocation with endogenous training-generated senior capacity and compare welfare to discretionary allocation; Chen et al. optimize assignment accounting for task experience over a horizon; Valeva and Borgonjon cover stochastic workforce assignment/training. These establish the broad combination in restricted models, though not exact HLS semantics. |
| **N4. Conditions where adaptive strictly beats strong fixed/stationary policy** | **PARTIALLY COVERED** | Published ADP/bandit results show gains over stated comparators; the reviewed Chen abstract uses one-step lookahead; bandit work uses regret benchmarks. The exact strong-SEP/optimized stationary comparison is not verified as already solved in the same HLS model. |
| **N5. Conditions where fixed/stationary is sufficient despite dynamics** | **PARTIALLY COVERED** | HLS E2.1 gives a model-scoped separable null, and dynamic optimization literature contains stationary/state-responsive optimal structures under particular assumptions. A general boundary for assignment-dependent learning with coupled tasks is not established by this audit. E2.1 WIP evidence is not treated as canonical experimental validation. |
| **N6. Regime boundary R0/R1/R2** | **POTENTIALLY NOVEL, ONLY IF FORMALIZED NARROWLY** | A taxonomy alone restates policy classes and Bellman optimization. Novelty might reside in nontrivial necessary/sufficient boundaries under a clearly differentiated coupling/information model; current HLS exact families do not establish a generic phase diagram. |
| **N7. Joint interaction of heterogeneity, information, environmental change, capability evolution and adaptation costs** | **NOT ASSESSABLE WITH AVAILABLE EVIDENCE** | Too broad as stated; literature covers many intersections and primary full texts/data remain unreviewed. A finite explicit model and targeted systematic search are prerequisites. |
| **N8. Reproducible framework distinguishing environmental dynamics from decision-relevant opportunity** | **POTENTIALLY NOVEL as a methods contribution, not yet established** | HLS has meaningful infrastructure and validated scenarios, but infrastructure alone is not a scientific result. Need a public operational definition, demonstrative falsification controls, and comparison against existing benchmark suites/frameworks. |

These labels concern the broad claims as worded, not an assertion that every exact formal proposition has been published.

## 7. Closest scientific threat

### Baccara, Lee & Yariv (2023)

**What it already establishes:** In a theoretically analyzed model, allocation choices determine how much junior service/training occurs; training changes future senior service capacity; the queue creates waiting costs and externalities. The authors characterize both the social planner’s optimal allocation and discretionary client-choice equilibrium with perfect and limited queue monitoring. Corollary 2 (§6, pp. 24–25) establishes that centralized policies send weakly fewer clients to seniors and induce weakly greater senior mass/training than discretionary equilibria (strictness under stated cases), while comparative statics identify when welfare/quality/training changes with arrival rate, training technology and monitoring. This directly establishes that endogenous capability accumulation and allocation can interact and that organizational allocation can have conditional welfare value.

**HLS assumptions shared:** allocation affects future organizational capability; current service quality trades off against training opportunities; agents/providers are heterogeneous; information/monitoring changes feasible decisions; the objective is system/client welfare over a dynamic queueing process.

**What differs:** Baccara’s task stream is stationary Poisson with one identical task type; the evolving capability is aggregate junior-to-senior capacity via \(\mu=f(x)\), not an individual multi-skill matrix; congestion/waiting is central; comparison is planner vs strategic decentralized client choice. It does not compare a centralized policy to an optimized fixed task-to-agent map, an HLS strong-SEP router, or a separated architecture given exact continuation values. It does not have unknown-capability online estimation. The paper is a theoretical steady-state analysis, not a multi-seed experimental comparison.

**Could HLS reduce to it?** Not by variable renaming alone. A reduction would need agents grouped into junior/senior types, a Poisson queue of identical tasks, all junior assignments feeding a common concave training production function, senior capacity as a service rate, waiting costs as reward penalties, and client-choice vs planner action semantics. HLS’s current N×K and Nembhard state/actions do not implement these conditions. Conversely, Baccara does not subsume HLS’s individual skill geometry or strong-SEP/SEP-Omega results.

**What would distinguish a defensible HLS extension:** a new nontrivial theorem in a materially different and explicitly useful class—e.g. multiple task types and individual task-specific learning with a strong optimized separate-management baseline—showing a necessary/sufficient boundary not already implied by queue externalities or Bellman inclusion. A mere finite example of “training today raises future value” is insufficient.

### Chen et al. (2018) and Emam et al. (2020): complementary threats

Chen et al. are the closest finite-horizon algorithmic workforce antecedent: known heterogeneous learning rates and task experience, stochastic future demand, ADP vs one-step lookahead. Their full equations/baseline tables still need inspection. Emam et al. are the closest unknown/changing-capability adaptive-reassignment antecedent, but their updated specialization is an estimate from task progress mismatch rather than experience-acquired skill. Together, Baccara, Chen and Emam cover much of the broad conceptual territory; combining them does not itself make a new contribution.

**What would distinguish HLS from all three:** the precise RQ0 information/architecture boundary, if it yields more than standard policy nesting and remains nontrivial under a strong comparator. HLS must formally show the exact mapping that the prior models fail to cover and establish why the extra multi-skill/state/information structure changes a theorem or measurable result. Until then, broad novelty is not cleared.

## 8. Existing HLS results against prior art

| HLS result | What it supports | Relation to established literature / publication judgment |
|---|---|---|
| **RQ0 policy-class inclusion** | `Π_SEP ⊆ Π_HLS` implies weak value inequality; exact finite-world strictness criterion from absence of an SEP-admissible HLS optimum. | Inclusion is generic optimization logic, not novel. The strictness criterion is precise and useful in this formalization; its contribution depends on a nontrivial new characterization, not theorem restatement. |
| **A1 / C1 R5 strict existence** | Constructive exact value gaps relative to strong SEP under specified opportunity coupling. | Useful as a boundary/existence result; not prevalence, empirical external validity, or advantage over SEP-Omega. Need full comparison to stochastic workforce ADP literature before publication claim. |
| **SEP-Omega equality** | Exact continuation information can make separated decision/development reproduce HLS in audited families. | Valuable countercondition; resonates with standard centralized/decomposed DP/coordination, so likely not novel absent a sharper general theorem. |
| **G2 D0/D1/D2** | Separates no learning, individual learning without efficient set change, and learning with future collective value change. | Strong didactic/exact test fixtures; existence logic follows standard dynamic programming/capability-investment models. Likely internal ground truth unless generalized or empirically anchored. |
| **G3 reduction** | Development value equals ordinary assignment sensitivity to competence increments in the 3×2 regimes. | Explicitly a reduction to standard assignment analysis; useful validation, not a standalone new theory claim. |
| **G3-H/C1/C2** | Demonstrates insufficiency of a local continuation shortcut and need for exact look-ahead in the specified case. | Falsification/diagnostic contribution; exact Bellman look-ahead itself is established. Publishability depends on whether the failure boundary is non-obvious and generalizes to a useful theorem. |
| **E1** | In the chosen profiles, fixed specialization-aligned dispatch can match myopic oracle behavior and outperform current adaptive estimator bundle. | Methodologically useful negative study; no broad policy ranking. It is neither a paper reproduction nor evidence that adaptive allocation is ineffective. |
| **E2.1** | Under independent skills, increasing productivity, unit task reward and task-dependent static mapping, no dynamic reassignment advantage in tested configurations; proof explains the structural result for this class. | Good negative control; mathematical reason is discrete convexity and separability. It does not validate online adaptation or coupled task portfolios. |

**Critical RQ0 qualification.** `J_HLS ≥ J_SEP` says only that the larger class can imitate the smaller. It does not imply strict advantage; no result follows unless strictness is shown under a non-artificial strong comparator and common information. Moreover, when SEP receives exact action-conditioned continuation value, current audited families have equality. The current HLS evidence itself explicitly disallows converting local Bellman inversion into global value, or reporting its exact C(alpha) interval outside that family ([RQ0 boundaries, §§4–9](../theory/rq0_routing_integration_boundaries.md); current state §§6–9).

## 9. Up to three defensible research gaps

These are **PROPOSALS**, not approved research claims.

### Gap 1 — Information sufficiency boundary for modular allocation/development

**Question.** In a finite-horizon assignment model with action-dependent skill acquisition, what is the smallest decision information available to a separated router that makes joint allocation-development value-equivalent, and when does a restricted but otherwise optimal separate architecture have a strict value gap?

* **Closest prior art:** Baccara et al. centralized allocation/training versus discretionary equilibrium; Chen et al. ADP/one-step comparison; HLS RQ0 strong SEP/SEP-Omega.
* **Difference:** characterize a *strongly optimized modular architecture under explicit information restriction*, not merely compare ADP with one-day lookahead or invoke policy inclusion.
* **Risk:** could reduce to standard Bellman sufficiency/POMDP information-state results; if SEP-Omega’s exact continuation is allowed, equality may be immediate.
* **Minimum publishable result:** a nontrivial necessary/sufficient condition in a clearly defined family, validated on positive and null cases, plus exact baseline inclusion and literature reduction.
* **Negative result meaning:** if sufficient modular state reproduces joint optimum throughout natural classes, RQ0 should be reframed around estimation/coordination cost rather than intrinsic integration value.
* **Difficulty:** high theory, moderate exact computation.

### Gap 2 — Boundary for dynamic reassignment versus optimized task-dependent static maps under coupled learning

**Question.** Which departures from independent skill/task experience (shared capacity, cross-task learning, task complementarity, or stochastic availability) are necessary/sufficient for a finite-horizon dynamic reassignment policy to strictly beat the globally optimized stationary task-to-agent mapping?

* **Closest prior art:** Chen et al.; Valeva et al.; E2.1 separable convex null result.
* **Difference:** strong stationary comparator and explicit structural boundary rather than a weak greedy baseline or a demonstration of one ADP gain.
* **Risk:** workforce scheduling literature may already contain the relevant boundary. Full Chen/Valeva/Borgonjon and the 2026 warehouse article must be inspected first; no new mechanism should be invented simply to force a positive result.
* **Minimum publishable result:** theorem or exact finite enumeration identifying a robust non-degenerate coupling boundary, with matched positive/null cases and equivalence to relevant prior scheduling formulations.
* **Negative result meaning:** dynamic reassignment may be unnecessary under broad monotone/separable learning conditions; this would delimit where adaptive allocation research should focus.
* **Difficulty:** moderate-to-high theory and computation.

### Gap 3 — Decision-relevant versus merely nonstationary demand under endogenous learning and partial information

**Question.** For a predeclared finite class of demand processes and capability transitions, can one characterize when environmental variation changes the identity of the value-maximizing allocation after accounting for learning, estimator uncertainty and adaptation costs, relative to a globally optimized stationary policy?

* **Closest prior art:** nonstationary bandit regret (Besbes et al.; Luo et al.), Emam’s feedback reassignment, Chen’s stochastic future demand/experience.
* **Difference:** distinguish “environment changes” from “decision-relevant changes” in a coupled workforce/capability model with a strong static benchmark.
* **Risk:** too broad; could be a restatement of a finite MDP’s policy evaluation, and all interacting factors may make conclusions uninterpretable.
* **Minimum publishable result:** one precise model class, explicit information sets, sufficient/necessary decision-relevance criterion and calibrated null/positive controls; avoid a broad factorial claim.
* **Negative result meaning:** demand nonstationarity alone may have no organizational value when the optimal policy is invariant; this is a meaningful boundary.
* **Difficulty:** high; requires careful separation of exogenous transition, endogenous state, and estimator.

**Recommendation among gaps:** pursue Gap 1 only after the exact Baccara comparison class and full Chen/adjacent workforce models have been mapped. It directly sharpens RQ0 and uses existing exact HLS theory; however, no novelty claim should be made until a reduction/novelty proof survives Baccara’s allocation/training result, Chen’s workforce ADP, and classical stochastic-programming/MDP literature.

## 10. Minimal next steps before new development

1. Obtain and read complete primary texts for Chen et al. (2018), Valeva et al. (2017), Borgonjon & Maenhout (2024), Annear et al. (2023), and the 2026 warehouse paper; extract exact states, service/skill dynamics, baselines, theorems and numerical tables. The current abstract-based absences must not be treated as verified.
2. Build a formal reduction table: HLS state/action/reward/transition/information to Baccara’s two-type queue/training model, Chen MTSP-ESTSC and adjacent workforce formulations. Prove equivalence or identify a concrete obstruction, especially around Nembhard productivity, HLS competence, multi-skill resource coupling, queue externalities, and optimized stationary policies.
3. Search backward/forward citations around Chen, Valeva, and workforce learning-by-doing assignment for exact optimized stationary-versus-dynamic policy comparisons. Use a documented search log before stating “no prior work found.”

No implementation, protocol execution, campaign or code modification is recommended by this audit.

## 11. Final decision

### **ADJUST — narrow the scientific claim before further development**

* **STOP** any broad novelty claim that adaptive allocation, heterogeneous adaptive coordination, or joint task assignment and learning-by-doing is itself new.
* **GO** for a bounded theoretical prior-art continuation focused on whether HLS’s specific strong-SEP/SEP-Omega information boundary is new relative to technician/workforce ADP and stochastic scheduling.
* **HOLD** new mechanism implementation and experiments until that reduction audit is complete and reviewed.

This decision is about scientific direction; it does not authorize code or experimentation.

## 12. Source index and local evidence

### Primary literature

* Annear, Akhavan-Tabatabaei & Schmid (2023), EJOR 306(3), 1109–1125. [DOI](https://doi.org/10.1016/j.ejor.2022.08.049).
* Baccara, Lee & Yariv (2023), *Journal of Economic Theory* 207, 105587. [DOI](https://doi.org/10.1016/j.jet.2022.105587) · [full accepted manuscript](https://www.lyariv.com/papers/TaskAllocation.pdf).
* Besbes, Gur & Zeevi (2014), NeurIPS 27, 199–207. [Proceedings paper](https://proceedings.neurips.cc/paper/2014/hash/91ba7292e5388b90b58d0b839a7f19ec-Abstract.html).
* Borgonjon & Maenhout (2024), C&IE 187, 109784. [DOI](https://doi.org/10.1016/j.cie.2023.109784).
* Cavenaghi et al. (2021), *Entropy* 23(3), 380. [DOI](https://doi.org/10.3390/e23030380).
* Chen, Xi, Hewitt & Thomas (2017), C&OR 82, 1–14. [DOI](https://doi.org/10.1016/j.cor.2016.12.026).
* Chen, Hewitt & Thomas (2018), IJPE 196, 122–134. [DOI](https://doi.org/10.1016/j.ijpe.2017.10.028).
* Cheung, Simchi-Levi & Zhu (2022), *Management Science* 68(3), 1696–1713. [DOI](https://doi.org/10.1287/mnsc.2021.4024).
* Emam et al. (2020), ICRA, 7719–7725. [DOI](https://doi.org/10.1109/ICRA40945.2020.9197283) · [primary preprint](https://arxiv.org/abs/2003.03344).
* Luo et al. (2018), COLT/PMLR 75, 1739–1776. [PMLR](https://proceedings.mlr.press/v75/luo18a.html).
* Mettler, Massey & Kellman (2016), *JEP: General* 145(7), 897–917. [DOI](https://doi.org/10.1037/xge0000170).
* Nembhard (2001), IJPR 39(9), 1955–1968. [DOI](https://doi.org/10.1080/00207540110036696).
* Nembhard & Bentefouet (2015), C&IE 80, 80–93. [DOI](https://doi.org/10.1016/j.cie.2014.11.006).
* Nembhard & Osothsilp (2005), JORS 56(5), 576–587. [DOI](https://doi.org/10.1057/palgrave.jors.2601842).
* Liu et al. (2017), “Iterative Machine Teaching,” ICML/PMLR 70, 2149–2158. [Primary paper](https://proceedings.mlr.press/v70/liu17b.html).
* Saha et al. (2025), “System-1.x: Learning to Balance Fast and Slow Planning with Language Models,” ICLR 2025. [Primary proceedings paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/605e59e78284907aa4fce5280838def3-Paper-Conference.pdf).
* Valeva, Hewitt, Thomas & Brown (2017), IJPE 183, 194–207. [DOI](https://doi.org/10.1016/j.ijpe.2016.10.026).
* Wang et al. (2025), “MixLLM: Dynamic Routing in Mixed Large Language Models,” NAACL 2025. [DOI](https://doi.org/10.18653/v1/2025.naacl-long.545).
* Wang, Xiang & Chen (2026), *Transportation Research Part E*, article 105040. [DOI](https://doi.org/10.1016/j.tre.2026.105040); full source not verified in this audit.

### HLS evidence

* Official question and policy comparison requirement: [`docs/research_questions.md`](../research_questions.md).
* Scope and established RQ0 results/nonclaims: [`docs/HLS_CURRENT_STATE.md`, §§5–11](../HLS_CURRENT_STATE.md#5-rq0-and-its-current-role).
* Exact strong-SEP formalism: [`docs/theory/rq0_routing_integration_boundaries.md`](../theory/rq0_routing_integration_boundaries.md).
* G2/G3: [`docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md`](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md); [`docs/experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md`](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md).
* E1/E2.1: [`docs/experiments/HLS_NEMBHARD_ADAPTIVE_ALLOCATION_PROTOCOL.md`](../experiments/HLS_NEMBHARD_ADAPTIVE_ALLOCATION_PROTOCOL.md), [`docs/experiments/HLS_NEMBHARD_PROTOCOL_REVIEW.md`](../experiments/HLS_NEMBHARD_PROTOCOL_REVIEW.md), [`docs/experiments/HLS_E2_1_PROTOCOL.md`](../experiments/HLS_E2_1_PROTOCOL.md).
