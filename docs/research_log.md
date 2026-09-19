# Research log

## Decision 001 — Creation of the umbrella research programme

Date: 2026-09-14.

### Decision

Create **Heterogeneous Learning Systems** as an umbrella research programme.
The purpose is to investigate whether competence allocation across heterogeneous
agents can be deliberately evolved through operation and knowledge transfer.

`adaptive_routing` was judged too narrow to serve as the main programme axis:
it addresses a particular two-agent execution/learning coupling. It remains a
valid, independent subproject. It is neither abandoned, rewritten, moved, nor
treated as historical data belonging to this repository.

### Initial scientific status

**HYPOTHESIS.** Competence distribution may be a controllable dynamic property
of a heterogeneous learning system. This is not a model, theorem, algorithm,
or novelty claim.

**KNOWN RESULT / landscape observation.** MARL, mixture-of-experts, machine
teaching, collaborative intelligence/co-distillation, lifelong multi-agent
learning, orchestration/routing, edge/cloud collaboration, federated/continual
learning, and knowledge valuation each cover relevant ingredients.

**OPEN QUESTION.** Whether their interaction has an accepted formulation or
solution for deliberate competence-distribution evolution is unknown.

### Methodological rule

Prior work combining some or even most ingredients does not by itself settle
the direction. Each candidate literature family must be evaluated for
conceptual precedent, methodological maturity, accepted-solution status,
limitations/open problems, and potential for meaningful improvement. Novelty is
not ``being the first paper to mention an idea.''

### Next action

Create and maintain a literature map before promoting additional research
questions, methods, experiments, or formal models.

## Decision 002 — Provisional consolidation of the landscape phase

Date: 2026-09-14.

### Decision

Close the broad horizontal landscape phase provisionally and record its
technical synthesis in `landscape/landscape_001_consolidated.md` and research
checkpoint 002. This is a documentation decision, not a conclusion that the
literature is complete or that the programme has a scientific gap.

### Consolidated position

The audit covered routing/RouteNLP, Machine Teaching and curriculum, Active
Learning/Value of Information, bandits/resource allocation, capacity
expansion/optimal control, continual/lifelong learning, and decision-focused
optimization. The principal correction is that Machine Teaching must not be
caricatured as fixed-single-target teaching: the audited literature includes
iterative, learner-state-dependent, partially observed, and selective teaching
mechanisms.

H1 survives as a better-specified working hypothesis: the relevant comparison
is whether an intervention should be valued by expected future portfolio
operation rather than solely observed routing failure frequency and quality
gap. No novelty claim follows. RQ0 remains the only official research question.

### Next action

Develop a minimal model and a synthetic falsification experiment only after
documenting their assumptions. Neither is started by this decision.

## Decision 003 — Formalization of M0

Date: 2026-09-14.

### Decision

Formalize `models/model_M0.md` as a deliberately minimal working model for H1.
M0 distinguishes observed failure severity, learnability, and downstream
operational value without claiming to be the final HLS model.

### Result

M0 values an intervention as:

```text
V_z = -K_z + A_H p_z ell_z [g_z - m_z]_+.
```

It supplies a rank-reversal construction in which a frequency-gap baseline
selects a different region from downstream operational value, and a
perfect-gap-closure special case in which the quality gap cancels from the
conditional downstream value. These results support mathematical coherence of
H1, but are not by themselves considered a sufficient research contribution.

### Limitations and next action

M0 excludes cross-competence effects, forgetting, transfer, and realistic
routing uncertainty. The next planned critical analysis is M1: vector-valued
competence changes and interference. M1 is not formulated or started here.

## Decision 004 — M0 implementation and canonical regime verification

Date: 2026-09-14.

### Decision

Create the minimal computational laboratory for M0: pure model functions,
unit tests, a reproduction of the documented rank-reversal example, and a
reproducible equal-parameter regime sweep.

### Result

The formulas are numerically verified and the documented rank reversal is
reproduced. The canonical sweep is restricted to `m_z > 0` (`delta_z > c`) so
that it does not mix regions where the cheap model already routes. Within the
strict switchable band `c < delta_z < c + g`, it confirms the opposite
monotonicity of frequency-gap score and M0 intervention value when the other
region-level parameters are equal. This is an M0 structural observation caused
by its fixed gain and deterministic switching threshold, not a general result.

### Limitations and next action

Ties and non-switchable regions are recorded separately rather than being
labelled as rank reversals. The next scientific decision is analysis of M0
results before any M1 work; M1 is not implemented or started here.

## Decision 005 — Analytical M0.1 gap-dependent learning response

Date: 2026-09-14.

### Decision

Interpret the M0 computational result critically: its 75.953% strict
rank-reversal fraction is grid geometry under a selected parameter range, not
an empirical prevalence estimate. The fixed conditional gain is an important
structural assumption of that result. Document `models/model_M0_1_gap_dependent_learning.md`
as an analytical extension of M0, not as M1 or a new complete model.

### Result

M0.1 permits gain, learnability, and training cost to depend on the observed
quality gap. Within a strictly switchable interval, its central derivative is:

```text
V'(delta) = -K'(delta) + A_H p [ell'(delta) h(delta) + ell(delta)(g'(delta)-1)].
```

The theoretical objective is therefore reframed from showing that a
frequency-gap score can fail to characterising the assumptions under which it
is, or is not, a useful proxy for downstream intervention value. No novelty or
empirical claim follows.

### Next action

Perform a narrow computational verification of the analytical response
families, beginning with linear gain `g(delta)=a+b delta` and its boundary at
`b=1`. M1 remains deferred; do not restart broad horizontal literature search.

## Decision 006 — Computational verification of M0.1 response identities

Date: 2026-09-14.

### Decision

Implement a separate M0.1 verification module and narrow numerical checks,
without modifying M0 or adding learning mechanisms.

### Result

Finite-difference checks recover the analytical linear-gain boundary `b=1`,
the proportional-response boundary `rho=1`, the exact sign boundary for
unclipped `ell(delta)=ell0+s delta`, and the one-for-one negative shift from a
linear training-cost slope. Points outside `delta>c`, `h(delta)>0`, or the
chosen strict learnability interval are rejected or masked. The `rho=0` case
has no strictly switchable canonical interval. These are consistency checks of
M0.1 identities, not empirical claims about learning response or distillation.

### Next action

The next theoretical task is to characterise order-equivalence of
`p_i delta_i` and `V_i` when task frequencies differ. Do not start M1.


## Decision 007 — Return from H1 to the population-level HLS programme

Date: 2026-09-14.

### Decision

Do not allow H1, RouteNLP, or further `frequency * quality_gap` mathematics to
replace the repository-level programme. M0/M0.1 remain valid diagnostic work,
but the central object is again the distribution of competences across a
heterogeneous portfolio and its deliberate evolution through operation and
learning.

### Reason

The original programme concerns multiple heterogeneous learners, potentially
multiple teachers, dynamic routing, experience-driven learning, and deliberate
management of specialization, redundancy, and complementarity. The value of a
learner is not its isolated quality.

### Consequence

Create `research_origin_and_chronology.md` so future sessions reconstruct the
chronology before proposing narrower work.

## Decision 008 — K0 vertical audit of complementarity/homogenization mechanism

Date: 2026-09-14.

### Decision

Audit vertically the candidate mechanism:

```text
knowledge transfer
    -> loss of functional diversity/complementarity
    -> loss of robustness/adaptability under shift
```

### Result

The audit found strong precedents for homogenization in online KD,
diversity-preserving KD, information loss in ordinary ensemble distillation,
diversity for concept-drift adaptation, and KD under distribution shift.
Continual-learning KD also provides evidence that distillation can preserve
knowledge. Therefore no general claim such as `KD -> homogenization -> failure`
is justified.

The open system-level issue is narrower: how competence-changing actions alter
the operational structure of a heterogeneous portfolio and its future value.

## Decision 009 — Population-level correction and P1-P4 scaffolding

Date: 2026-09-14.

### Decision

Replace single weak-learner/teacher reasoning with a portfolio view. Adopt the
structural distinctions:

```text
individual failure != portfolio competence deficit
individual improvement != portfolio improvement
```

Use P1-P4 as analytical scaffolding without promoting them to official RQs.

### Current propositions

- **P1 — Collective competence:** local failure/improvement must be evaluated
  against portfolio coverage and operational alternatives.
- **P2 — Local-collective misalignment:** a learning action preferred by a
  local criterion can be inferior in downstream portfolio value.
- **P3 — Evolution can outperform frozen routing:** competence evolution must
  be tested against a strong frozen heterogeneous portfolio plus adaptive
  router.
- **P4 — Coupling advantage:** candidate strongest claim; a coupled
  routing/competence-evolution system may outperform a strong decoupled system
  using comparable components and resources.

### Policy on prior work

Do not discard pieces because they are known. Existing routing, distillation,
active-learning, submodular/resource-allocation, continual-learning,
diversity-preservation, or drift-detection methods can be adopted and cited.
The desired contribution may combine known blocks with one or more original
pieces, a new coupling/objective, and a demonstrable system-level property.
Conversely, an unexplored combination alone is insufficient.

## Decision 010 — Experimental validity is separate from experimental outcome

Date: 2026-09-14.

### Decision

A poorly designed experiment must not be interpreted as proving or refuting the
research hypothesis. Experimental validity and experimental outcome are
separate records.

### Required checks

Every experiment must explicitly assess:

1. construct validity;
2. causal identification;
3. comparison validity;
4. external validity.

Negative evidence counts against P2/P3/P4 only when the benchmark genuinely
instantiates the mechanism, the intervention can affect it, the relevant
horizon is observable, capacity is not a trivial confound, and strong
baselines are correctly implemented.

Positive evidence counts in favour only when weak baselines, compute/data
advantages, tuning asymmetry, leakage, favourable shift selection, and
post-hoc benchmark construction have been excluded.

Synthetic tests provide causal control; realistic benchmarks provide external
relevance. Neither alone establishes the full claim.

### Next action

Construct the smallest coherent portfolio model in which P1, P2, and P3 are
simultaneously relevant, then test whether P4 can arise against a genuinely
strong decoupled baseline. Formalization is a falsification tool, not the
research objective itself.

## Decision 011 — Cross-domain mathematics as apparatus, not programme replacement

Date: 2026-09-15.

Use Operations Research, portfolio management, economics, optimal/stochastic control, organizational science, human competence management, Machine Teaching, and adjacent fields as sources of mathematics, mechanisms, and theoretical structures. The methodological rule is: “Import mechanisms and mathematical tools; do not import or replace the HLS research problem.”

Usable knowledge or competence is the distributed material managed by an HLS; learning transforms that distribution; operation gives competence value; and time makes competence acquisition an investment. Competence trajectories, marginal value, opportunity cost, specialization, redundancy, rebalancing, depreciation, and option value are legitimate apparatus when they help study RQ0. Mathematical resemblance to another domain neither demonstrates HLS novelty nor automatically removes it. **SPECIALIZE**, **BROADEN**, **REPLICATE**, and **REBALANCE** are provisional strategy families, not results. See `research_strategy_cross_domain_toolkit.md`.

## Decision 012 — Minimal competence-evolution theory and microverification

Date: 2026-09-15.

Construct a minimal analytical laboratory to check internal coherence, expose null cases, and subject restricted parts of the programme to falsification before larger experiments. Its model-scoped results are **CR0** strict separability, **CR1** a finite complementary competence threshold, **CR2** a local stability threshold for endogenous division-of-labour specialization, **CR3** scalar deliberate-rebalancing identities, and **CR4** a dual-actuator competence-evolution optimum.

Microverification checks the covered identities and behaviours. These results show only that some competence/operation/learning interactions are coherent and non-trivial inside the stated minimal model. They do not establish general real-HLS behaviour, general value of specialization/broadening/replication, RQ0, P4, novelty, or superiority of a coupled controller. CR0--CR4 therefore remain consistency/falsification evidence and a theoretical laboratory, not the programme centre. See `theory_competence_evolution_minimal_model.md` and `../experiments/microverification/`.

## Decision 013 — Paper skeleton as a theory nucleus, not the programme itself

Date: 2026-09-15.

Create `../paper/` as a compilable scientific skeleton around the minimal theory. The draft shows that the minimal theory can be organized and communicated coherently; it does not imply that CR0--CR4 are a sufficient publishable HLS contribution. Adversarial review reinforced the risk that mathematically tractable results can narrow the programme too far.

Do not expand the paper by inertia. Before deciding what paper should emerge, its introduction, HLS framework, implications and limits, research programme, and conclusion must be aligned with the general programme model. This decision does not modify `paper/`.

## Decision 014 — Consolidation of the general HLS research model

Date: 2026-09-15.

Adopt `general_research_model.md` as the programme-level conceptual anchor while preserving RQ0 exactly.

> “An HLS should be viewed not only as a heterogeneous portfolio to be exploited, but as an evolving distribution of competences.”

> “Operational decisions determine not only who performs current tasks, but potentially who gains the experience that shapes future competence; learning and knowledge-transfer decisions provide additional mechanisms for changing that distribution.”

> “The central question is therefore whether deliberately shaping who will be competent at what can create greater long-term system value than simply optimizing the use and local improvement of the competences available today.”

Future competence allocation is a **candidate** system-level decision variable, not a universal conclusion. The hierarchy is:

```text
RQ0
    -> general HLS competence-evolution model
        -> P1–P4 analytical scaffolding
        -> strategy families / cross-domain apparatus
        -> minimal models and CR0–CR4
        -> controlled experiments and realistic validation.
```

RQ0 remains a hypothesis. The programme has a coherent scientific object and explicit falsification discipline, but no general HLS algorithm, realistic empirical validation, established novelty claim, established P4, or established general superiority of deliberate competence evolution.

## Decision 015 — Structural prior-work equivalence, not nominal coincidence

Date: 2026-09-15.

The first directed theoretical audit examined dynamic workforce learning/training, transactive memory/dynamic capabilities, and heterogeneous Machine Teaching. Novelty barriers must be based on structural equivalence, not terminology: reconstruct state, actions, transition, objective, information, horizon, and endogenous and exogenous quantities from the actual model.

Borgonjon & Maenhout substantially raises the novelty bar because operation, learning, training, forgetting, shadow training, and future efficiency are already integrated. Argote & Ren removes isolated novelty claims around who-knows-what, complementary expertise, and reconfiguration. Yeo et al. removes isolated novelty claims around heterogeneous learner-aware sequential teaching toward a fixed target.

None of these three papers alone establishes RQ0 or P4. The residual HLS question remains provisional and must now be tested by structural reduction against strong prior models; it is not promoted to a new official RQ. See `literature/targeted_theoretical_audit_001.md`.

## Decision 016 — Reframe the paper around collaborative HLS architecture and competence evolution

Date: 2026-09-15.

Reframe `paper/` from a minimal-dynamic-theory draft into a working architecture-to-theory-to-validation paper. The paper now presents the provisional A1--A5 functional architecture, distinguishes work allocation from knowledge/learning allocation, and records a candidate competence-orchestration scaffold. Environmental dynamics are a condition for analysis, not a sixth architectural pillar.

CR0--CR4 and their microverification are retained as preliminary model-scoped results. General integration theory remains under development and general experiments do not yet exist. This decision makes no novelty claim, does not change RQ0, and does not establish P4 or HLS superiority.

## Decision 017 — Integrated competence-investment scaffold

Date: 2026-09-15.

Document one candidate competence-investment value (CIV) model spanning the A1--A5 architecture. R1 (whether), R2 (where), and R3 (organization) are resolutions of one investment decision, not separate models. Under an explicit two-student/one-teacher/two-region Markov specialization, the invest/do-nothing threshold, local-gain/system-value reversal construction, pairwise action boundaries, and volatility-alone replication null result are derived in-model.

Teacher buffering remains conditional behaviour, not an axiom. CIV does not establish novelty, broad practical relevance, superiority over modular control, RQ0, or P4. See `theory_integrated_competence_investment_model.md`.

## Decision 018 — Adversarial CIV stress test and branch register

Date: 2026-09-15.

Stress-test the two-regime CIV specialization rather than treating nominal strategy labels as results. The active derived implications are that persistence values current-regime alignment rather than a named transformation, dominance can remove an action, REPLICATE can relieve capacity/cost exposure, REBALANCE can be valuable under a persistent operational mismatch, and non-negative benefits are penalized by learning delay and short horizon.

The audit rejects “volatility implies replication,” “persistence implies specialization,” and a fundamental SPECIALIZE/REPLICATE/REBALANCE regime map as the current organizing framework. Replication without operational exposure and rebalancing without mismatch are retained as null results. SPECIALIZE remains a possible vocabulary item but is parked as a fundamental regime until it has a justified independent system-level mechanism. Teacher buffering remains candidate conditional behaviour.

The current working direction is discounted future portfolio exposure and the value of feasible transformations that remove it. All implications remain model-scoped: this decision does not establish novelty, a practical policy, superiority over modular control, P4, or RQ0. See `theory_civ_adversarial_stress_test.md`.
## 2026-09-16 — Research refocused on established cross-domain foundations

Created `docs/theoretical_foundations_cross_domain.md`.

The project moves away from further refinement of local constructs such as portfolio exposure and nominal specialization/replication/rebalancing regime maps.

Foundations selected for systematic study include Ashby's requisite variety, Markowitz portfolio theory, collective problem solving, transactive memory systems, exploration/exploitation, dynamic capabilities, comparative advantage and knowledge hierarchies, workforce flexibility and cross-training, ecological response diversity, evolutionary bet hedging, dependable-system redundancy, ensemble learning and No Free Lunch results.

Common working structure:

`repertoire -> individual quality -> complementarity -> division of labour -> redundancy -> coordination -> future value -> competence acquisition -> reconfiguration -> uncertainty`.

Key distinction:

`competence != value of competence`.

Research strategy:

`reuse what is established -> integrate what is compatible -> derive what is HLS-specific -> develop new theory only where necessary`.

No paper claims are changed at this stage. This material is research infrastructure and theoretical grounding.

## Decision 019 — Research doctrine and canonical documentary backbone

Date: 2026-09-16.

Adopt `RESEARCH_DOCTRINE.md` as the general anti-drift document above the HLS line, and make `general_research_model.md` and `theoretical_foundations_cross_domain.md` the canonical scientific-object and foundation-map documents. The programme does not require novelty in every component: established theory, mechanisms, algorithms, and results should be reused, reproduced when useful, translated to HLS, adapted where necessary, and extended only where the learning-model system requires it.

The active programme has two parallel lines: theoretical foundations and experimental foundations. CIV, portfolio exposure, P1--P4, named transformation families, and minimal models remain subordinate tools, historical results, or diagnostic scaffolding. Portfolio exposure is retained only as model-scoped CIV vocabulary, not as the next central research problem. The immediate task is to select and rigorously translate an established cross-domain foundation, then decide whether a minimal reproduction tests that transfer.

This is a documentation and methodology consolidation. It changes neither RQ0 nor the epistemic status of existing theory, experiments, or novelty claims.

## Decision 020 — Audit of the B1+B2+B12 experimental foundations

Date: 2026-09-16.

Audit the implemented foundation experiments against their documented equations, source papers, limiting cases, and epistemic labels before extending the experimental programme. The audited block comprises Garicano organization reproductions B1.1--B1.4, Gutjahr competence-evolution reproductions B2.1--B2.5, and interface checks B12.1--B12.4.

B2.5 remains **FAILED_SOURCE_REPRODUCTION**. Direct evaluation of Gutjahr's published Example 3 equations gives objective values `2.0`, `1.5`, `0.5`, and `1.5` for `(e1,e1)`, `(e1,e2)`, `(e2,e1)`, and `(e2,e2)`, respectively, rather than the claimed optimum at `(e1,e2)`. The implementation reproduces the published equations and detects the invalid cancellation of the term `x12 phi(-2+4x11)`; parameters and equations are not altered to recover the paper's conclusion.

An independent enumeration of B12.4 recovers 36 effective-coupling cases among 96 declared configurations and zero effects among the 96 matched controls with `eta=0`. In every comparison, the initial intervention is the only trajectory difference and both trajectories subsequently use the same allocation rule. This result is **SUPPORTED** only as evidence that the channel

```text
allocation -> experience -> competence -> future allocation
```

can change future allocation in a non-degenerate part of the declared grid. The fraction 0.375 is grid geometry, not performance, prevalence, or evidence that coupling is beneficial. The audit adds uniform result manifests, exact bibliography keys, explicit pass/fail contracts, and independent tests. It does not establish RQ0, P4, novelty, or superiority of an HLS policy.

## Decision 021 — Current RQ0 and common HLS ontology

Date: 2026-09-17.

Replace the official RQ0 wording based on “deliberate evolution of competence allocation” with:

> Can the dynamic allocation and development of competences in a heterogeneous learning system improve long-term system performance compared with architectures that manage task allocation and knowledge transfer separately?

The earlier wording remains part of the historical record but is no longer the current research question. The scientific comparison is `J(pi_joint) > J(pi_separate)`, together with equality and no-advantage conditions. `pi_separate` must be scientifically strong rather than weak myopia, and weak dominance is tautological if the joint policy is defined only as an optimum over a class containing the separate policy.

Adopt `hls_ontology.md` as the canonical semantic and dimensional consistency layer. It distinguishes competence coverage, competence proficiency, operational performance, real work, learning exposure, allocation, interaction, learning/transfer, useful work, operational value, and cumulative objective. Every source theory must be mapped independently as `EQUIVALENT`, `RELATED`, `INCOMPATIBLE`, or `UNRESOLVED` before integration.

Garicano (2000) and Gutjahr (2011) remain primary current references for the organization/use and development/evolution beams, respectively; neither defines an entire beam. The general candidate interface is now written with explicit allocation-to-work, work-to-exposure, and exposure-to-competence mappings. B13 is retained as diagnostic evidence that exposed present-versus-future value structure and semantic problems; `G_G > D_G` is not the programme proof. This consolidation introduces no new scientific result.

## Decision 022 — Consolidate minimal HLS model v1 and T=2 fixed-priority result

Date: 2026-09-19.

Consolidate `theory/minimal_hls_model.md` as the self-contained minimal HLS model v1. It uses two agents, one competence, `T=2`, operational allocation `a`, competence-development action `d`, shared capacity, direct and indirect experience maps, additive competence dynamics, and expected operational value only. The document explicitly preserves the ontology distinctions among competence, expected/observed quality, work, experience, development action, and operational value.

The algebraic audit retains the two stated identities under normalized capacity, demand sufficient to use both agents operationally, a period-2 opportunity probability `p`, and explicit fixed-priority/tie conventions:

```text
J_J - J_A->D = sum_m [V_m^D - V_m^A]_+
J_J - J_D->A = sum_m [V_m^A - V_m^D]_+
V_m^A = S_m,1 + p eta_m
V_m^D = p lambda_m.
```

The audit found a documentation precision issue, not a changed mathematical result: a sequential argmax does not uniquely force full use of a zero-valued priority action. The consolidated document therefore defines the two baselines as fixed-priority reservation rules and states their tie convention. It also makes the full-demand and period-2-opportunity assumptions explicit. The result is that the two fixed orders fail in complementary parameter regions; neither is universally optimal in this minimal model.

This remains a first existence result only against those two fixed-priority separated architectures. It does not establish novelty, general superiority of joint management, RQ0 in general, or a result against coordinated separated architectures, which may reproduce the joint solution. The next theoretical problem is to specify stronger genuinely separated policy classes and characterize equality and strict-advantage conditions, without expanding this `T=2` model in the current task.
