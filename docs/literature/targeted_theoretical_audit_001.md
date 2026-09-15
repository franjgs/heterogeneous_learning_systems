# Targeted theoretical audit 001 — competence allocation, learning, and collective capability

Date: 2026-09-15
Status: focused literature audit. This document constrains and informs the HLS programme; it does not establish novelty, RQ0, P4, or a general HLS result.

## 1. Audit question and equivalence criterion

This audit asks whether three focused precedents structurally reduce the HLS programme, rather than whether they use overlapping vocabulary. A comparison is meaningful only through the actual model: state, heterogeneity, operation or task allocation, competence dynamics, decision variables, objective, information assumptions, operation--learning coupling, horizon, endogenous quantities, and exogenous quantities. Abstract, introduction, and conclusion framing are not treated as substitutes for those model elements.

The question is not whether the words *competence*, *learning*, *teaching*, *dynamic capability*, *reconfiguration*, or *specialization* appear elsewhere. A structural reduction would require substantially the same phenomenon or proposition for the same, or a genuinely equivalent, class of learning systems under comparable assumptions.

## 2. Borgonjon & Maenhout (2024)

### Problem and actual model

Borgonjon and Maenhout study personnel staffing under a prescribed task and scheduling environment. Their integrated model combines personnel staffing, days-off scheduling, task assignment, and scheduling of training activities. Workers have dynamically changing competence scores; a nonlinear competence-to-efficiency relation is approximated through discrete task-operation modes whose durations depend on prevailing worker skill. The objective is a staffing-budget/cost objective while satisfying the imposed work and scheduling requirements over a planning horizon.

Regular-task execution yields traditional learning-by-doing; forgetting can reduce skill; on-the-job and off-the-job training are explicit scheduled activities; and shadow training can involve another worker. Training has opportunity cost because it consumes worker time and interacts with task and staffing scarcity. The paper studies regimes in which learning rates, training duration, task structure, and costs make different mechanisms relevant to the staffing objective.

### Structural consequence for HLS

This is the strongest structural adversary in this audit. HLS cannot claim novelty merely from combining task assignment, learning-by-doing, explicit training, forgetting, peer or shadow training, a changing skill mix, and future operational consequences. These ingredients are jointly present in a normative dynamic workforce model.

The result must nevertheless be bounded by the actual formulation. The future skill mix is altered by assignment and training decisions, but the objective is workforce staffing cost under an externally prescribed task and scheduling environment. The desired competence distribution is not formulated as an independently selected HLS portfolio target valued through future collective artificial-system operation. This audit does not infer that the distinction is sufficient for novelty, nor that the paper resolves RQ0.

### Importable apparatus and limits

Useful apparatus includes a competence state separate from operational efficiency, nonlinear/discrete competence-to-efficiency mappings, learning-by-doing, forgetting, explicit and shadow training, opportunity cost, scarcity induced by task/staffing constraints, and regime analysis. It does not establish an HLS competence representation, an artificial learning portfolio, a general portfolio-utility objective, a frozen/reactive/local/decoupled comparison, or P4.

## 3. Argote & Ren (2012)

### Conceptual contribution and scope

Argote and Ren develop transactive memory as a microfoundation for dynamic capabilities. The key idea is *who knows what*: distributed specialization, credibility, and coordination permit access to knowledge beyond isolated individual expertise. Expertise can be complementary, so its value depends on team configuration. Experience can reinforce specialization; recognized experts can receive knowledge in their domain; and the resulting collective capability can be path- and context-dependent. The paper discusses building, integrating, and reconfiguring knowledge assets.

### Structural consequence for HLS

HLS cannot claim isolated novelty for who-knows-what, distributed expertise, complementary specialization, portfolio-conditional expertise value, knowledge reconfiguration, or collective capability not reducible to isolated expertise. The work is a strong conceptual precedent for treating a competence distribution as more than a list of independent qualities.

It is not a normative dynamic optimization model that chooses which learner should acquire which competence because of downstream system-level operational utility. It does not specify an HLS comparison between deliberate evolution and frozen, reactive, local, or decoupled policies. It therefore does not establish RQ0 or P4.

### Importable apparatus and warning

The useful apparatus is the distributed-competence or who-knows-what analogy; specialization and complementarity; portfolio-dependent value; path dependence; coordination distinct from possession of knowledge; and knowledge-asset reconfiguration under changing or obsolete knowledge. A future HLS theory must not automatically assume that `C_t=[c_iz]` exhausts collective capability if coordination, accessibility, or knowledge about who knows what are operationally relevant. This is a warning for future modelling, not a change to `C_t` here.

## 4. Yeo et al. (2019)

### Problem and actual model

Yeo et al. formulate iterative classroom teaching for multiple heterogeneous learners. Learners have different initial internal states and learning rates. A sequential teacher chooses common examples, may partition the classroom into groups, and is analysed under full, noisy, or incomplete knowledge of learner dynamics. The model treats teacher orchestration cost and learner workload, proving convergence/sample-complexity results for stated projected-gradient learners.

The structural boundary is explicit: the target hypothesis `w*` is fixed and exogenous. The problem is how heterogeneous learners should be taught toward `w*`, not which heterogeneous competence distribution should be built because of future collective operation.

### Structural consequence for HLS

HLS cannot claim isolated novelty for heterogeneous learners, heterogeneous learnability, learner-state-dependent sequential teaching, teaching cost, or grouping/partitioning trade-offs. Yeo et al. do not endogenize a desired future competence allocation from downstream portfolio operation, and do not establish RQ0 or P4.

### Importable apparatus and limits

Useful apparatus includes learner-state-dependent intervention, heterogeneous learning rates and initial states, omniscient versus noisy/incomplete teachers, grouping, teacher/learner cost trade-offs, and convergence reasoning for shared interventions. The fixed target, teaching objective, and lack of an operational portfolio value are substantive formulation limits, not merely differences in language.

## 5. Cross-paper structural comparison

This table is an audit tool, not evidence of novelty.

| Dimension | Borgonjon & Maenhout | Argote & Ren | Yeo et al. | HLS programme target |
| --- | --- | --- | --- | --- |
| Heterogeneous members | Workers with differing skills and availability. | Team members with differentiated expertise. | Learners with different states and learning rates. | Heterogeneous learners/models/agents. |
| Distributed competence/knowledge | Dynamic worker skill mix. | Explicit who-knows-what and collective memory. | Learner internal states relative to a common target. | Usable competence distributed across a portfolio. |
| Operational task allocation | Days-off scheduling and task assignment. | Descriptive coordination and task matching. | No external operational task allocation. | Division of labour gives current competence value. |
| Operation changes future competence | Regular-task learning and forgetting. | Experience can reinforce specialization. | Teaching iterations change learner state. | Operation may generate formative experience. |
| Explicit learning/training action | On/off-job and shadow training. | Knowledge direction, integration, and reconfiguration discussed conceptually. | Sequential teacher-selected examples and grouping. | Learning/transfer can reshape competence allocation. |
| Transfer/teacher-recipient relation | Shadow training can involve another worker. | Knowledge directed to recognized experts. | Teacher to learners via common examples. | Candidate transfer among heterogeneous members. |
| Forgetting/interference | Forgetting explicit; interference not the stated model. | Obsolescence/context discussed; no formal interference dynamics. | Not a continual-learning/forgetting model. | May be relevant only in later physically specified transformations. |
| Future target competence allocation endogenous from operation | Skill mix follows staffing and training decisions under prescribed demand. | No normative target-selection optimisation. | No: `w*` is fixed and exogenous. | Candidate question: desired configuration may be endogenous to future collective operation. |
| Portfolio-conditional operational value | Staffing cost and task efficiency under constraints. | Conceptual collective capability and coordination value. | Teaching convergence/workload/orchestration value. | Future system utility conditioned on portfolio, environment, and horizon. |
| Normative long-horizon competence evolution | Yes, within workforce staffing cost formulation. | No formal normative optimisation. | Sequential teaching toward fixed target. | Open: characterize and compare deliberate evolution policies. |
| Establishes P4 | No. | No. | No. | Not established. |

## 6. What this audit removes from the novelty space

The following are not defensible novelty claims by themselves:

1. task assignment changes future competence through learning-by-doing;
2. explicit training can be scheduled jointly with productive work;
3. forgetting changes dynamic competence;
4. tutor or peer relations can transfer competence;
5. changing skill mix affects future operational cost;
6. who-knows-what affects collective performance;
7. complementary specialization affects collective capability;
8. knowledge assets can be reconfigured;
9. heterogeneous learners can receive learner-state-dependent sequential teaching; and
10. teaching heterogeneous learners can require grouping/cost trade-offs.

This does not mean that an HLS theory using these mechanisms lacks novelty. It means that any contribution must be stronger than their isolated presence.

## 7. Residual HLS structure after the audit

A provisional residual question is whether, in an artificial learning portfolio, the future distribution of usable competences is itself a decision-relevant system state whose desired configuration is endogenous to future collective operation.

The candidate distinction remains:

```text
current competence
    != current operational value
    != learning / transfer potential
    != future system value.
```

This is not claimed new. The scientific task is to characterize natural HLS conditions under which these quantities coincide or diverge. A member can simultaneously be an operational resource, holder of distributed competence, learner with a heterogeneous transformation law, source or recipient of transferable knowledge, generator of formative experience through operation, and component whose modification changes future division of labour. The conjunction is not claimed novel and must be subjected to future reduction attempts against strong prior models.

## 8. Consequence for the next theoretical search

Before claiming an HLS residual, attempt a formal structural reduction to the strongest prior model. A failed reduction is informative only if it identifies the exact assumption, endogenous quantity, or comparison class that prevents equivalence. The next search should therefore target reductions, null cases, and strong adversaries rather than additional nominal analogies.

## 9. Epistemic conclusion

Borgonjon and Maenhout substantially raise the novelty bar for dynamic operation/training/competence models. Argote and Ren constrain claims about distributed expertise and collective capability. Yeo et al. constrain claims about heterogeneous learner-aware sequential teaching. None alone establishes RQ0, P4, a general HLS algorithm, a general HLS result, or an established novelty claim.
