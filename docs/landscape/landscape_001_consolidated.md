# Landscape 001 — Consolidated technical synthesis

Date: 2026-09-14
Status: synthesis of a provisional audit; not a novelty claim, formal model, or solution survey.

## 1. Scope

This document consolidates the landscape relevant to RQ0 and working hypothesis H1. It distinguishes known results and reported empirical evidence from inferences for HLS and unresolved questions. References cited by key are verified in the accompanying bibliography.

## 2. Core HLS problem

HLS concerns coupled execution and competence-improvement decisions in a heterogeneous portfolio. A provisional ontology is `C_t`, task demand `x_t ~ D_t`, routing action `a_t`, intervention `u_t` (possibly null), and stochastic evolution `C_{t+1} ~ P(C' | C_t,u_t)`. `C_t` is not known to be observable or sufficient.

The decision of interest is not competence gain in isolation. It is whether an intervention changes later operational utility through routing, cost, quality, latency, coverage, specialization, redundancy, complementarity, and possible transfer or interference.

## 3. RouteNLP as concrete empirical adversary

**Problem and decision.** RouteNLP routes a workload through a tiered LLM portfolio under quality constraints, then chooses failure clusters for targeted distillation [@guo2026routenlp]. Its loop uses router representations, PCA and k-means to identify escalations; distills from a frontier model to cheaper tiers; and retrains/recalibrates the router.

**Objective and evidence.** Its reported objective is cost-aware routing subject to quality; it reports benchmark and pilot shadow-deployment evidence that targeted distillation plus retraining can lower cost and shift traffic toward cheaper tiers.

**Importable mechanism.** Failure-derived opportunity discovery, targeted data selection, and recalibration after competence change are concrete operational mechanisms.

**Assumptions and limits relative to HLS.** Selection is approximately cluster size/frequency times mean quality gap, recipients follow a frontier-to-cheaper hierarchy, and the paper does not provide a general recipient-selection or long-term portfolio-utility objective. A benchmark loop and a pilot shadow deployment need not equal a production learning loop; outcomes may depend materially on the cost structure.

**What this does not establish.** It does not establish that frequency and gap are sufficient, that a general competence landscape is observable, or that H1 is novel. It is a strong baseline/adversary for H1.

## 4. Machine Teaching

**Problem and decision.** Iterative machine teaching selects teaching examples sequentially to accelerate a learner [@liu2017iterative]; black-box variants estimate learner state through queries [@liu2018blackbox]. The decision variable is generally a teaching example, sequence, query, or teaching configuration.

**Objective, state, and mechanism.** Objectives include fast convergence, teaching complexity, or target performance; learner state may be observed, approximated, or partially hidden. These works provide state-dependent sequential interventions and explicit information/cost trade-offs.

**Assumptions and limits relative to HLS.** The reviewed formulations specify a learner-side target or performance criterion. They do not by themselves evaluate the future operational value of changing one member of a heterogeneous portfolio with routing and portfolio externalities.

**What this does not establish.** It does not support caricaturing the field as fixed-target only: it already covers iterative, black-box, and learner-state-dependent teaching. The targeted audit did not determine whether all target/task/competence-selection variants under downstream portfolio utility are absent; that remains open.

## 5. Active Learning / Value of Information

**Problem and decision.** Active learning selects observations or labels. EPIG selects acquisitions by information about future predictions under a target distribution [@bickfordsmith2023prediction]. Targeted active learning selects information to reduce uncertainty about a downstream optimal decision [@filstroff2024targeted].

**Importable mechanism.** These works separate parameter information, prediction relevance, and downstream decision relevance. They offer a vocabulary for expected future value and approximations when exact look-ahead is intractable.

**Assumptions and limits relative to HLS.** Their actions primarily acquire information and update beliefs/models. An HLS learning intervention can alter the operational capability state itself. Entropy reduction is not economic utility, and decision accuracy is not necessarily operational utility.

**What this does not establish.** It does not supply an HLS intervention-transition model or a portfolio utility objective, but it makes a useful warning explicit: acquisition value must be aligned to the downstream quantity that matters.

## 6. Bandits / Resource Allocation

**Problem and decision.** Bandit families repeatedly select opportunities under uncertainty and budget. Graph-triggered rising bandits allow selecting one arm to affect the evolution of others [@genalti2024graph].

**Importable mechanism.** Contextual features can represent recipients and regions; restless/rising dynamics can represent stateful benefit; graph-triggered interactions can represent transfer or interference; and regret concepts support exploration/exploitation and budget allocation.

**Assumptions and limits relative to HLS.** Tractability depends on interaction structure and reward assumptions. Learning gain or arm reward is not automatically future portfolio utility.

**What this does not establish.** It does not determine the HLS state, reward, or whether intervention interactions satisfy a bandit structure.

## 7. Capacity Expansion / Optimal Control

**Problem and decision.** Capacity-investment models choose timing and scale of costly changes in capability under demand uncertainty. The useful analogy is competence as capacity, training/distillation as investment, routing as dispatch, and demand as future workload.

**Importable mechanism.** Timing, waiting, lead time, maintenance, irreversibility, and option value provide questions that a myopic error-cluster score omits.

**Assumptions and limits relative to HLS.** Capacity is usually more directly measurable and physically specified than competence. The analogy is conceptual, not an asserted equivalence.

**What this does not establish.** It does not justify a diversity bonus or a monotone rule from uncertainty to diversity; waiting, specialization, redundancy, generalism, and later investment may each be preferable under different assumptions.

## 8. Continual / Lifelong Learning

**Problem and decision.** Continual learning manages acquisition and retention across tasks. Selective layer transfer explicitly balances transfer against catastrophic forgetting [@lee2021sharing].

**Importable mechanism.** Competence evolution should permit a vector-valued change, including forward/backward transfer, forgetting, negative transfer, and interference:

```text
c_i(t+1) = c_i(t) + Delta c_i
```

or more generally `C_{t+1} ~ P(C' | C_t,u_t)`.

**Assumptions and limits relative to HLS.** Task relationships and transfer granularity matter; similarity is not a sufficient substitute for transferability. The portfolio, rather than a single learner, is the relevant HLS unit.

**What this does not establish.** Individual forgetting is not automatically system-level harm: loss can be acceptable if another portfolio member covers the competence better or more cheaply.

## 9. Decision-Focused / Bilevel Optimization

**Problem and decision.** Decision-focused learning trains predictive models according to the quality of downstream optimization decisions rather than pointwise prediction error [@elmachtoub2021smart; @mandi2024decision]. A restless-bandit instance trains transition predictions for final allocation quality [@wang2023scalable].

**Importable mechanism.** Separate physical transition `P*`, learned transition representation `P_hat_phi`, intervention-selection regret, and final system utility. Accurate transitions everywhere are not necessarily required if an approximation induces good choices.

**Assumptions and limits relative to HLS.** This requires a specified downstream objective and an optimization interface. Approximation and optimization can be expensive, and an optimizer may exploit transition-model errors.

**What this does not establish.** Decision-focused learning cannot rescue a wrongly specified operational objective; robustness and uncertainty may matter as much as point-prediction accuracy.

## 10. Cross-domain synthesis

The fields collectively support mechanisms for choosing interventions, estimating learner state, valuing future prediction or decisions, allocating budget under uncertainty, handling state evolution, and training models for decisions. The targeted audit did not identify a verified formulation that, as its explicit objective, selects competence-modification actions for the expected future operational value of a heterogeneous routed portfolio. This is an audit observation, not a novelty claim or proof of absence.

## 11. What these fields collectively imply for HLS

The useful conceptual baseline is:

```text
Value(u) = -C_learning(u) + E[V(C') | C,u] - baseline value
```

This is not a final objective. It records that a learning action may have cost, stochastic capability effects, and future operational consequences. RouteNLP supplies the immediate concrete comparator, while the other fields constrain what can responsibly be claimed about its extensions.

## 12. What remains unresolved

Observability and sufficiency of `C_t`; appropriate intervention actions; estimation of `P(C'|C,u)`; portfolio-level utility; recipient selection; demand uncertainty; transfer/interference effects; decision regret; and an honest falsification protocol remain unresolved.

## 13. Consequences for the minimal model

The next model should remain minimal: distinguish routing `a_t` from intervention `u_t`; allow null intervention; allow stochastic positive and negative competence effects; value interventions through later operation; and expose the assumptions under which RouteNLP's `frequency * quality_gap` is sufficient or insufficient. It should not prematurely choose a Bellman equation, bandit, MDP, POMDP, bilevel, or real-options formalism.

## 14. Bibliographic notes

The map records only verified entries actually used in this synthesis. Prompt-supplied references with unverified metadata are held as pending in checkpoint 002 rather than fabricated. See `../literature/references.bib` and `../literature/literature_map.md`.
