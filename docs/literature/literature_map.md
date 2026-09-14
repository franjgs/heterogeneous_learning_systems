# Literature map

Status: consolidated audit snapshot, 2026-09-14. This is not a completeness claim, a novelty audit, or evidence that a scientific gap exists. Entries below have been checked against a primary proceedings, publisher, DOI, or arXiv page; their implications for HLS remain bounded by the stated formulations.

## Review protocol

For each important source, record the problem, decision variable, objective, state/context, heterogeneity, learning or transfer mechanism, evidence, assumptions, limitations, relevance to RQ0/H1, importable mechanism, and what it does not establish. Similar vocabulary or mathematics is precedent, not closure. Status labels are **verified metadata**, **preliminarily reviewed**, and **critically mapped**; the entries below are critically mapped only for the limited HLS purpose described here.

## Routing and portfolio adaptation

### `guo2026routenlp` — RouteNLP (2026, arXiv; ACL Industry Track acceptance reported by the authors)

- **Problem / decision variable:** Route each query in a tiered LLM portfolio; identify escalation-failure clusters for targeted distillation.
- **Objective / state:** Minimize cost under per-task quality constraints using task-conditioned router representations and quality signals. Cluster ranking is approximately size/frequency times mean quality gap.
- **Heterogeneity and transfer:** A frontier model distils into cheaper tiers; the router is retrained after the portfolio changes.
- **Evidence / assumptions:** Reports benchmark evidence and a pilot shadow deployment; assumes an ordered tier structure, available teacher inference, and its quality/cost evaluation setup.
- **Limits and HLS relevance:** Recipient selection is not general and no explicit long-term portfolio-utility objective is supplied. It is the direct empirical adversary for H1.
- **Import / does not establish:** Import escalation-derived intervention discovery and retraining mechanics. It does not establish sufficiency of frequency and gap, a general competence state, or H1 novelty.

## Machine Teaching and learner-state-dependent intervention

### `liu2017iterative` — Iterative Machine Teaching (ICML 2017)

- **Problem / decision variable:** Sequentially choose teaching examples for an iterative learner.
- **Objective / state:** Accelerate convergence or reduce teaching complexity; the teacher uses a specified level of learner-state information.
- **Heterogeneity / learning:** Learner dynamics are central, but this is not a routed operational portfolio problem.
- **Evidence / assumptions:** Theoretical analyses under stated learner and example-construction conditions plus experiments on distributions and images.
- **Limits and HLS relevance:** Teaches a learner toward a teaching objective; it does not value a change through future portfolio operation.
- **Import / does not establish:** Import sequential learner-aware intervention. It does not establish a recipient-selection objective for HLS.

### `liu2018blackbox` — Towards Black-box Iterative Machine Teaching (ICML 2018)

- **Problem / decision variable:** Choose teaching examples and learner queries when teacher and learner have different representations and learner state is not fully observed.
- **Objective / state:** Estimate learner status and speed convergence; state is partially inferred by examinations.
- **Heterogeneity / learning:** Cross-space teacher/learner representation mismatch is explicit.
- **Evidence / assumptions:** Provides sample-complexity results and experiments relative to omniscient and passive teachers.
- **Limits and HLS relevance:** Partial observability is relevant to estimating learnability, but the downstream objective remains learner convergence.
- **Import / does not establish:** Import learner probing and state estimation; it does not establish portfolio-level intervention value.

## Active Learning, Value of Information, and decisions

### `bickfordsmith2023prediction` — Prediction-Oriented Bayesian Active Learning (AISTATS 2023)

- **Problem / decision variable:** Select labels/acquisitions in Bayesian active learning.
- **Objective / state:** EPIG measures expected information about predictions under an input distribution, rather than parameter information alone.
- **Heterogeneity / learning:** No heterogeneous operational portfolio is required; a posterior predictive model is updated.
- **Evidence / assumptions:** Experiments across datasets and models; requires a model and relevant prediction distribution.
- **Limits and HLS relevance:** Distinguishes parameter information from future predictive value, but acquisition changes knowledge rather than necessarily changing the operational system.
- **Import / does not establish:** Import target-distribution-aware valuation; it does not define HLS operational utility.

### `filstroff2024targeted` — Targeted Active Learning for Bayesian Decision-Making (TMLR 2024)

- **Problem / decision variable:** Select a sample/model observation to improve a later Bayesian decision.
- **Objective / state:** Expected information gain on the posterior distribution of the optimal decision; posterior uncertainty is computed by sampling.
- **Heterogeneity / learning:** Multiple decision models can be considered; information is acquired and Gaussian-process models are retrained.
- **Evidence / assumptions:** Synthetic and applied experiments; exact lookahead is intractable and approximated by sampling/retraining.
- **Limits and HLS relevance:** Shows decision-aware acquisition but not a competence-altering portfolio transition.
- **Import / does not establish:** Import downstream-decision alignment and approximation awareness; it does not establish an HLS transition model.

## Bandits and resource allocation

### `genalti2024graph` — Graph-Triggered Rising Bandits (ICML 2024)

- **Problem / decision variable:** Select arms whose pulls can change the expected reward evolution of connected arms.
- **Objective / state:** Maximize cumulative reward under rising, graph-triggered arm dynamics; graph structure governs interactions.
- **Heterogeneity / learning:** Heterogeneous arms and cross-arm effects are explicit; deterministic and stochastic regret settings are analysed.
- **Evidence / assumptions:** Proves NP-hardness generally, a tractable clique case, and regret results under its dynamics.
- **Limits and HLS relevance:** A plausible abstraction for transfer/interference and budgeted interventions, conditional on strong structural assumptions.
- **Import / does not establish:** Import interaction-aware allocation; it does not prove that HLS has graph-triggered or rising rewards.

## Continual and lifelong learning

### `lee2021sharing` — Sharing Less is More (ICML 2021)

- **Problem / decision variable:** Select layers/configurations to transfer in lifelong deep learning.
- **Objective / state:** Balance transfer performance over tasks with avoidance of catastrophic forgetting; task relationships are inferred from data.
- **Heterogeneity / learning:** Tasks have different useful transfer granularity; an EM procedure selects configurations and weights.
- **Evidence / assumptions:** Experiments in lifelong object classification on several architectures; assumes the specified network and task setting.
- **Limits and HLS relevance:** Supports modelling positive and negative effects of a learning action, not a scalar competence increment.
- **Import / does not establish:** Import selective-transfer and interference mechanisms; it does not decide whether a portfolio-level change is worthwhile.

## Decision-focused optimization

### `elmachtoub2021smart` — Smart Predict, then Optimize (Management Science 2021)

- **Problem / decision variable:** Train predictions that feed a constrained downstream optimization problem.
- **Objective / state:** SPO loss measures decision error induced by predictions; SPO+ is a convex surrogate for linear-objective optimization settings.
- **Heterogeneity / learning:** Not an intervention portfolio; it is a general predict-then-optimize formulation.
- **Evidence / assumptions:** Consistency results under mild stated conditions and numerical shortest-path/portfolio experiments.
- **Limits and HLS relevance:** Directly motivates separating prediction accuracy from decision quality, but relies on a given downstream optimization model.
- **Import / does not establish:** Import decision-error evaluation; it does not specify the correct HLS system objective.

### `mandi2024decision` — Decision-Focused Learning survey (JAIR 2024)

- **Problem / decision variable:** Survey end-to-end learning with constrained downstream optimization.
- **Objective / state:** Compare gradient-based and gradient-free approaches to decision quality under uncertainty.
- **Heterogeneity / learning:** Heterogeneous application settings; no shared HLS competence ontology is asserted.
- **Evidence / assumptions:** Review plus an empirical benchmark of eleven methods across seven problems.
- **Limits and HLS relevance:** Documents methods and limitations of aligning predictions with decisions; requires a well-specified decision problem.
- **Import / does not establish:** Import the prediction-versus-decision distinction; it does not validate a proposed HLS objective.

### `wang2023scalable` — Decision-Focused Learning in RMAB (AAAI 2023)

- **Problem / decision variable:** Learn transition dynamics from correlated arm features for a Whittle-index restless-bandit allocation policy.
- **Objective / state:** Train transition predictions for final RMAB solution quality rather than predictive accuracy.
- **Heterogeneity / learning:** Arms have correlated features and unknown stateful dynamics; a limited activation budget is explicit.
- **Evidence / assumptions:** Differentiability of the Whittle-index policy and application to a previously collected maternal/child-health dataset.
- **Limits and HLS relevance:** Close evidence that transition prediction and final allocation quality differ, but its RMAB and index assumptions are not established for HLS.
- **Import / does not establish:** Import intervention-selection regret as a distinct quantity; it does not define competence transitions or utility.

## Pending targeted audit

The prompt-priority works not entered in `references.bib` remain pending exact metadata verification and focused reading: CONCUR, MixLLM, RouteLMT, Learning to Defer with Advice, the remaining named Machine Teaching/curriculum works, capacity-expansion/real-options sources, Hiratani (2024), Holton et al. (2025), SPOT (2025), and the requested Xiong and Li RMAB work. This is a deliberate bibliographic boundary, not a statement about their relevance.
