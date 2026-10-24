# Heterogeneous Learning Systems

**Heterogeneous Learning Systems (HLS)** is a general scientific framework
for studying, designing, and evaluating how heterogeneous capabilities are
organized, used, combined, and evolved to solve relevant problems. It seeks
generalizable knowledge within clearly stated classes and assumptions, and
effective solutions grounded in the integration of knowledge across
disciplines. HLS does not assume that heterogeneity, cooperation, learning,
adaptation, or organizational complexity is always beneficial.

Problems may change, remain stable, or impose different demands across
applications. No single component needs to possess every capability required
by a system. HLS therefore studies collectives of people, agents, models, or
other components whose capabilities and operating constraints can differ.

## The four-level HLS architecture

HLS organizes scientific inquiry around four conceptual and experimental
levels. They distinguish responsibilities without requiring four software
modules or a rigid execution sequence:

1. **Scenarios** define systems, capabilities, tasks, environment, resources,
   information, uncertainty, and relevant dynamics.
2. **Organizational schemes** define how capabilities and responsibilities
   are arranged and used, through selection, assignment, cooperation,
   coordination, specialization, or other forms.
3. **Models** represent, analyze, implement, and solve scenarios and
   organizational problems, using mathematical models, estimators,
   optimizers, policies, learning methods, or integrated mechanisms.
4. **Performance measures** evaluate outcomes and compare alternatives using
   measures relevant to the problem. HLS-PEF supports this level; it is not a
   universal objective.

These levels are related but not forced into a one-to-one mapping. See
[HLS Philosophy](docs/HLS_PHILOSOPHY.md) for the programme's stable scientific
identity and [HLS Current State](docs/HLS_CURRENT_STATE.md) for scoped
evidence.

## Research approach

HLS is not intended to replace established theories of learning, allocation,
control, organization, or decision making.

The programme instead seeks to:

```text
identify the system-level problem
        ->
reuse the strongest established foundations
        ->
map them into a common ontology
        ->
integrate compatible mechanisms
        ->
develop theory, mechanisms, or solutions where justified
        ->
test the resulting system and its boundaries
```

An original contribution may arise from a new result or mechanism, or from an
integration of known components that produces an identifiable capability,
property, explanation, or improvement. Integration alone does not establish
novelty; claims must be positioned against relevant work.

Existing theory is a foundation, not an obstacle.

## Scientific scope

The repository contains:

- programme-level philosophy and research doctrine;
- a common HLS ontology;
- formal and model-scoped theory;
- synthetic worlds and exact analyses;
- executable experiments and tests;
- frozen experimental protocols;
- literature mappings;
- and versioned scientific evidence.

Results have explicit scope.

A theorem proved for a particular model is not automatically a general HLS
property. A synthetic existence result does not establish prevalence or
real-world relevance. A pilot experiment is not automatically evidence for the
programme's main research question.

Negative results, equality conditions, reductions to established theory, and
cases in which simpler modular approaches are sufficient are part of the
scientific output.

## Start here

For the conceptual foundations:

1. [HLS Philosophy](docs/HLS_PHILOSOPHY.md) — **what HLS is, why it matters,
   and what it is for**.
2. [Research Doctrine](RESEARCH_DOCTRINE.md) — **how the research programme is
   conducted and kept scientifically disciplined**.
3. [HLS Ontology](docs/hls_ontology.md) — **the common semantic language used
   to represent HLS phenomena and integrate theories consistently**.

For the current research:

4. [Research Questions](docs/research_questions.md) — the questions currently
   under investigation.
5. [HLS Current State](docs/HLS_CURRENT_STATE.md) — what is currently
   established, what has been ruled out, and what remains open.
6. [Repository Guide](docs/REPOSITORY_GUIDE.md) — repository authority,
   provenance, and implementation map.
7. [Research Governance](docs/HLS_RESEARCH_GOVERNANCE.md) — primary research
   responsibilities and the process for explicit changes.

For technical depth:

- [Theory Registry](docs/theory/README.md) — formal results and scoped models;
- [Experimental Documentation Registry](docs/experiments/README.md) — worlds,
  protocols, runners, and evidence;
- [Adaptive-capability validation](docs/experiments/HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md)
  — bounded evidence for existing dynamic-demand, competence, estimation,
  policy, and trace paths; not a policy-superiority claim;
- [Literature Collection](docs/literature/README.md) — source and literature
  policy;
- [Scientific History](docs/HISTORY.md) — the compact scientific path to the
  present state.

## Repository structure

```text
README.md
RESEARCH_DOCTRINE.md

docs/
├── HLS_PHILOSOPHY.md
├── hls_ontology.md
├── research_questions.md
├── HLS_CURRENT_STATE.md
├── HISTORY.md
├── theory/
├── experiments/
├── experimental_foundations/
├── models/
└── literature/

experiments/
results/
src/
tests/
projects/
```

The documentation is deliberately layered:

```text
PHILOSOPHY
    what / why / what for
        |
        v
DOCTRINE
    how research is conducted
        |
        v
ONTOLOGY
    common semantic language
        |
        v
RESEARCH QUESTIONS
    what is currently being investigated
        |
        v
THEORY + EXPERIMENTS + EVIDENCE
```

`HLS_CURRENT_STATE.md` is the single canonical summary of the programme's
present scientific state.

## Project boundary

[`adaptive_routing`](https://github.com/franjgs/adaptive_routing) is an
independent prior project. It is **not** the origin, history, or implementation
base of HLS.

Its relationship to this programme is recorded only as external prior work in
[projects/README.md](projects/README.md).
