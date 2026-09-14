# Heterogeneous Learning Systems — Handover

Last updated: 2026-09-14  
Repository state: post-K0 conceptual consolidation; RQ0 unchanged; P1-P4 are analytical scaffolding.

## Mandatory first reads

Before proposing new theory, algorithms, or experiments, read in this order:

1. `README.md` — stable programme-level framing. **Do not rewrite it to follow every intermediate hypothesis.**
2. `research_origin_and_chronology.md` — chronological origin and corrections; prevents subproblems from replacing the main idea.
3. `research_program_checkpoint_003.md` — current scientific state.
4. `research_questions.md` — official RQ0 and subordinate H1.
5. `landscape/landscape_001_consolidated.md` and `literature/references.bib`.
6. `models/model_M0.md` and `models/model_M0_1_gap_dependent_learning.md` only as diagnostic history, not as the current centre.

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

The central idea is population-level **deliberate evolution of competence allocation**.

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

> Can the deliberate evolution of competence allocation in a heterogeneous learning system improve its long-term performance compared with independently optimizing task allocation and knowledge transfer?

H1 about failure frequency/quality gap is subordinate. It is a useful diagnostic problem, not the central hypothesis.

## Population-level correction

The relevant object is the competence distribution across a portfolio, conceptually:

```text
C_t = [c_iz(t)]
```

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

Direct adversary: a frozen heterogeneous portfolio with a strong adaptive router. P3 asks whether deliberate competence evolution can still improve long-term operational value under non-trivial conditions.

### P4 — Coupling advantage

Candidate strongest system-level claim:

```text
V_coupled > V_strong-decoupled
```

The decoupled baseline must itself be strong and use comparable routing, learning/transfer machinery, compute, data, and budget. P4 is not yet an official RQ or established hypothesis.

## Scientific priority

Current order:

1. make P1-P3 simultaneously meaningful in the smallest coherent portfolio model;
2. identify what information, if any, a strong decoupled routing+learning system lacks;
3. determine whether that information can create a genuine P4 coupling advantage;
4. only then design a larger algorithmic system and realistic experiments.

Do not return to more M0/M0.1 algebra unless it directly supports this programme.

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

Build the minimal portfolio-level formalization for P1-P3 and use it to ask whether P4 can hold against a strong decoupled baseline. The formal model is a device for exposing assumptions and counterexamples, not an end in itself.

Do not start a large experiment until the mechanism, adversaries, and validity conditions are explicit.

## Independent prior project

`adaptive_routing` remains an independent prior project and must not be silently imported as HLS evidence.
