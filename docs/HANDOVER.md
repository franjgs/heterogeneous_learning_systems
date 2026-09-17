# Heterogeneous Learning Systems — Handover

Last updated: 2026-09-17
Repository state: RQ0 updated to dynamic allocation and development of competences; common HLS ontology established as the mandatory consistency layer; P1--P4, CIV, B13, and CR0--CR4 remain subordinate scaffolding or diagnostic evidence.

## Mandatory first reads

Before proposing new theory, algorithms, or experiments, read in this order:

1. [RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md) — general methodology and anti-drift rules above any individual HLS mechanism.
2. `README.md` — short project entry point. **Do not rewrite it to follow every intermediate hypothesis.**
3. [general_research_model.md](general_research_model.md) — canonical HLS scientific object and architecture.
4. [research_questions.md](research_questions.md) — canonical wording of official RQ0 and subordinate H1.
5. [hls_ontology.md](hls_ontology.md) — canonical HLS concepts, units/ranges, mapping classes, and source-to-HLS mapping discipline.
6. [theoretical_foundations_cross_domain.md](theoretical_foundations_cross_domain.md) — canonical map of established principles to understand, map, translate, and test.
7. [theory/two_beam/README.md](theory/two_beam/README.md) — current technical skeleton connecting organization/use with competence development/evolution; not a complete HLS model.
8. [experimental_foundations/README.md](experimental_foundations/README.md) and [experimental_foundations/EXPERIMENTAL_SPEC_V0.md](experimental_foundations/EXPERIMENTAL_SPEC_V0.md) — audited Beam 1, Beam 2, and interface-reproduction block; B2.5 remains `FAILED_SOURCE_REPRODUCTION`, and B13 is diagnostic only.
9. `research_origin_and_chronology.md` — historical provenance and superseded directions.
10. [research_program_checkpoint_004.md](research_program_checkpoint_004.md) — historical pre-ontology checkpoint, not the current RQ0 source.
11. `research_strategy_cross_domain_toolkit.md` — supporting protocol for importing mathematics without replacing the HLS problem.
12. `landscape/landscape_001_consolidated.md` and `literature/references.bib`.
13. [theory_integrated_competence_investment_model.md](theory_integrated_competence_investment_model.md) and [theory_civ_adversarial_stress_test.md](theory_civ_adversarial_stress_test.md) — subordinate CIV model and its branch register; portfolio exposure is not a current programme priority.
14. `models/model_M0.md` and `models/model_M0_1_gap_dependent_learning.md` only as diagnostic history, not as the current centre.
15. [theory_competence_evolution_minimal_model.md](theory_competence_evolution_minimal_model.md) and [experiments/microverification/](../experiments/microverification/) — CR0--CR4 minimal-model audit; not a general HLS result.
16. [paper/](../paper/) — working draft with a stale RQ0 formulation; do not let it set programme direction and do not update it without a dedicated paper task.

## Central programme

The project studies heterogeneous portfolios in which routing and learning can alter each other over time:

```text
heterogeneous learners
    -> dynamic task allocation
    -> operational experience
    -> learning / knowledge transfer
    -> competence redistribution
    -> future task allocation
```

The central problem is the dynamic allocation and development of competences at system level. Operational allocation determines who performs work; learning and transfer decisions determine who learns what and from whom; present use may change future competence and performance.

Do not reduce the programme to:

- `frequency * quality_gap`;
- RouteNLP;
- a single teacher/student pair;
- "distillation causes homogenization";
- generic diversity preservation;
- Label Switching;
- M0/M0.1;
- a particular fast/slow cognitive analogy.

Those are possible components, adversaries, mechanisms, or historical steps.

## Official research question

RQ0 remains the sole promoted repository research question:

> Can the dynamic allocation and development of competences in a heterogeneous learning system improve long-term system performance compared with architectures that manage task allocation and knowledge transfer separately?

H1 about failure frequency/quality gap is subordinate. It is a useful diagnostic problem, not the central hypothesis.

## Population-level correction

The relevant object is the competence distribution across a portfolio, conceptually:

```text
C_t = [c_iz(t)]
```

This matrix is provisional. The canonical ontology distinguishes competence coverage from competence proficiency and does not assume both fit one scalar entry.

The system may contain multiple learners and multiple teachers.

Two current structural principles are:

```text
individual failure != portfolio competence deficit
individual improvement != portfolio improvement
```

A model can fail on a region that another model already covers well. Teaching the failing model may create no system value, may create useful redundancy, may waste scarce learning capacity, or may alter specialization and future routing. The decision must be portfolio-conditional.

## Current proposition scaffolding

### P1 — Collective competence

Local failure/improvement must be valued against the whole portfolio. Structural foundation; not expected to be novel in isolation.

### P2 — Local-collective misalignment

A locally preferred learning action can be inferior in downstream portfolio value. Possible mechanisms include redundancy, coverage gaps, budget, learnability, specialization/interference, future demand, teacher heterogeneity, and future routing.

### P3 — Evolution can beat frozen routing

Direct adversary: a frozen heterogeneous portfolio with a strong adaptive router. P3 asks whether competence evolution can still improve long-term operational value under non-trivial conditions.

### P4 — Coupling advantage

Candidate subordinate comparison:

```text
J(pi_joint) > J(pi_separate)
```

The separate-management baseline must itself be strong and use comparable routing, learning/transfer machinery, compute, data, and budget. It must not be reduced to weak myopia. P4 is not an official RQ or established result, and weak dominance is tautological if the joint policy class simply contains the separate class.

## Scientific priority

Current order:

1. preserve the whole-system view of HLS as an evolving distribution of usable competences;
2. build theoretical foundations by extracting assumptions, mathematical content, limits, and HLS translations from strong cross-domain results;
3. reproduce important mechanisms minimally when useful;
4. map every source independently into the common ontology before translation or integration;
5. integrate supported components only when their role in the whole HLS, null cases, compatible units, and fair comparisons are explicit.

Do not let CR0--CR4, reachability, P4, or another tractable mechanism replace this programme-level priority.

## Policy on existing pieces

Do not discard components because they have prior art. A strong paper can use known routing, KD, Machine Teaching, active learning, submodular allocation, continual learning, drift detection, or diversity mechanisms with proper citation.

The desired contribution may be:

```text
known components
+ one or more genuinely new pieces
+ a new coupling/objective
+ a demonstrable system-level property
```

At the same time, a mere unexplored combination is insufficient. The coupling should resolve a real limitation, expose an emergent property, or beat strong decoupled systems built from comparable pieces.

Potential locations for original pieces include competence-state representation, portfolio-gap analysis, intervention value, teacher/recipient selection, competence-redistribution policy, useful-complementarity measures, or controlled differentiation. None is yet claimed novel.

## Literature state

K0 established that several component claims already have strong precedent:

- online KD can homogenize peers;
- diversity-preserving online KD exists;
- ensemble diversity can contain information lost by ordinary ensemble distillation;
- expert diversity/selective expert training exists in continual learning;
- diversity can help under concept drift;
- KD can be weak under distribution shift;
- continual-learning KD can also preserve knowledge, so KD is not intrinsically destructive.

Recent routing precedents include RouteNLP, System-1.x, MixLLM, CONCUR and RouteLMT.

Budgeted learning/resource allocation and heterogeneous Machine Teaching are known areas. Their existence is not grounds to discard them as components and is not programme-level novelty by itself.

## Experimental epistemology — non-negotiable

A poorly designed experiment neither proves nor refutes the hypothesis.

Always separate **experimental outcome** from **experimental validity**.

Before treating a negative experiment as evidence against P2/P3/P4, establish that the benchmark actually instantiates the proposed mechanism, the intervention can affect it, the horizon makes the benefit observable, capacity is not a trivial confound, and strong baselines are correctly implemented.

Before treating a positive result as support, rule out weak baselines, extra compute/data/capacity, tuning asymmetry, leakage, favourable shift selection, and post-hoc benchmark construction.

Every experiment must explicitly audit:

1. construct validity;
2. causal identification;
3. comparison validity;
4. external validity.

Synthetic experiments provide controlled causal tests; real benchmarks provide realism. Neither alone is decisive.

## Methodological discipline

For every important paper ask:

- What exact decision problem is solved?
- What is the state and action?
- What is optimized?
- What is assumed known?
- Which components are fixed and which evolve?
- Is heterogeneity nominal or operationally important?
- What actually changes after learning?
- Is the evidence synthetic, benchmarked, deployed, or only theoretical?
- What strong baseline is beaten?
- What failure modes, hidden assumptions, favourable regimes, or cherry-picking remain?
- What does the paper **not** establish?

A recent related paper is evidence of an active area, not automatically evidence that the programme is closed.

## Immediate next action

Use [RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md), [research_questions.md](research_questions.md), [general_research_model.md](general_research_model.md), and [hls_ontology.md](hls_ontology.md) as active anchors. Garicano and Gutjahr are primary current references, not the theories of their beams. The B1/B2/B12 block reproduces source mechanisms and limiting cases; B2.5 remains an explicit failed source reproduction, and B12.4 supports only the configured causal channel, not benefit. B13 is a diagnostic model that exposed a present-versus-future value structure and semantic incompatibilities; it is not a proof of `J(pi_joint) > J(pi_separate)`. The next documentation/theory work must map additional verified foundations through the ontology and define fair joint/separate policy classes and compatible operational value before another integration claim.

Do not start a large experiment until the proposition, competence transformation, adversaries, matched information and resources, and validity conditions are explicit.

## Independent prior project

`adaptive_routing` remains an independent prior project and must not be silently imported as HLS evidence.
