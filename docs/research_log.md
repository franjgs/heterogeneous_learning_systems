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
