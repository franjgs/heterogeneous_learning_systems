# Research Doctrine

**Status:** Canonical programme-level research methodology and anti-drift
document.

This document defines **how HLS research should be conducted**. It does not
define HLS, prescribe a particular architecture or formalism, establish a
scientific result, or replace the current research questions.

For the scientific vision and purpose of HLS, see
[HLS_PHILOSOPHY.md](docs/HLS_PHILOSOPHY.md).

For the current research question and scientific state, see
[research_questions.md](docs/research_questions.md) and
[HLS_CURRENT_STATE.md](docs/HLS_CURRENT_STATE.md).

The purpose of this doctrine is simple:

> **Keep the research directed by the scientific problem rather than by the
> mechanisms, mathematical formalisms, experiments, papers, or technical
> branches encountered while investigating it.**

---

## 1. Philosophy before formalism

The HLS philosophy defines the scientific problem.

Research questions isolate uncertainties within that problem. Theory, models,
algorithms, synthetic worlds, experiments, and empirical systems are tools for
investigating those questions.

The direction of influence must therefore be:

```text
HLS philosophy
      |
      v
scientific question or need
      |
      v
theory / formalism / model / experiment
```

not:

```text
current formalism or mechanism
      |
      v
redefinition of HLS
```

A useful formalization may deliberately study only a restricted part of HLS.
Its results must then be interpreted at that scope.

No current mechanism—routing, knowledge transfer, teaching, hierarchy,
specialization, a particular learning rule, or any other mechanism—should
silently become the definition of HLS merely because it is the object currently
being studied.

When a technical branch becomes dominant, ask:

> **Does this genuinely help us build, understand, or test the scientific
> problem posed by HLS?**

If not, park it.

---

## 2. Scientific need before mechanism or literature

Do not begin by looking for papers, theories, algorithms, or mechanisms that
appear similar to HLS.

First identify the missing scientific object:

- What do we need to understand?
- What decision must be made?
- What phenomenon requires explanation?
- What property must be characterized?
- What capability is missing?
- What prevents the current system from solving the problem?

Only then ask whether established knowledge already addresses that object.

The correct direction is:

```text
HLS need
    ->
missing scientific object
    ->
relevant existing knowledge
    ->
mapping
    ->
import / adaptation / new development
```

not:

```text
interesting paper or theory
    ->
possible similarity to HLS
    ->
search for a role inside the programme
```

Search by **problem structure**, not by superficial terminology or keyword
similarity.

The relevant theory may come from machine learning or from another discipline.
Its disciplinary origin is secondary to whether it actually solves a problem
that HLS has.

---

## 3. Reuse before reinvention

HLS is an integrative research programme. Its components do not need to be
individually novel.

When established theory, mechanisms, algorithms, or methods solve a required
piece of the problem, prefer to understand and reuse them rather than recreate
them for the sake of novelty.

The preferred sequence is:

```text
identify need
    ->
find established knowledge
    ->
understand assumptions and result
    ->
map to HLS
    ->
import if valid
    ->
adapt if necessary
    ->
develop new theory only where required
```

This discipline is summarized as:

> **REDUCE BEFORE INVENTING.  BUY BEFORE REBUILDING.  ASSEMBLE BEFORE
> EXTENDING.**

Import a theory when it correctly resolves an HLS piece; assemble the
justified pieces before extending them, and extend only when a demonstrated
scientific need remains.

A reduction of an HLS problem to known theory is not a failure. It may provide
the correct solution, an equivalence result, a boundary, an efficient method,
or evidence that no HLS-specific machinery is required under those conditions.

Conversely, the fact that individual components are known does not imply that
the HLS-level problem has been solved.

Novelty should be assessed at the level where the scientific contribution
actually occurs.

Integration of known components is scientifically relevant only when it
produces a substantive new capability, explanation, method, property,
characterization, or demonstrated improvement.

“Those components have not previously been combined” is not sufficient by
itself.

---

## 4. Map before importing or integrating

Cross-domain similarity is a source of hypotheses and tools, not proof of
equivalence.

Before importing a result, establish how its objects correspond to the HLS
ontology.

For a proposed correspondence, distinguish:

- **EQUIVALENT** — the objects represent the same concept under the stated
  assumptions;
- **RELATED** — they are different objects connected by an explicit
  relationship;
- **INCOMPATIBLE** — they must not be identified;
- **UNRESOLVED** — the relationship has not been established.

Similar notation, mathematical form, numerical range, or normalization does
not establish semantic equivalence.

If a transformation is required,

```text
y = g(x)
```

then that transformation is part of the HLS model and must be explicit.

When several external theories are combined, each should first be mapped
independently into the common HLS semantic layer. Integration should occur
through that layer rather than by directly identifying variables across
sources.

The ontology is therefore a **consistency mechanism for reasoning and
integration**, not the scientific objective of HLS and not a contribution
merely because it exists.

If the current ontology cannot faithfully represent a phenomenon genuinely
required by the HLS philosophy, the ontology may need to evolve.

---

## 5. System relevance before local technical interest

A technically interesting result is not automatically an HLS result.

Every substantial theoretical development, mechanism, algorithm, or experiment
should have an identifiable role in the system-level problem.

Ask:

> **If this problem were solved completely, what would we know or be able to
> do about HLS that we cannot know or do now?**

If the answer is unclear or negligible, reconsider the priority of the branch.

Do not allow:

- a routing mechanism to replace the organization problem;
- a learning rule to replace competence development;
- a toy model to dictate the architecture;
- a source paper to define an entire scientific beam;
- a diagnostic experiment to redefine the research question;
- an attractive mathematical result to become the objective simply because it
  is tractable;
- or a benchmark to determine what HLS is because data happen to be available.

Mechanisms are subordinate to the scientific problem.

---

## 6. Strong alternatives, negative results, and claim discipline

HLS should be tested against scientifically strong alternatives.

Do not construct weak baselines merely to obtain positive results.

If one policy class contains another, weak dominance resulting solely from
that inclusion is not by itself a substantive scientific result. The important
questions concern strict advantage, equality, reducibility, sufficiency,
failure conditions, and the mechanisms that separate those regimes.

Negative results are scientifically useful when they constrain the programme.

A result showing that:

- a mechanism is insufficient;
- an apparent advantage disappears under stronger coordination;
- an HLS problem reduces to established theory;
- a modular architecture is sufficient;
- an analogy fails;
- or a proposed effect occurs only under restrictive conditions

may be as informative as a positive result.

For every important statement, preserve its epistemic status. Useful
categories include:

- **ESTABLISHED** — supported by prior knowledge;
- **REPRODUCED** — independently replicated;
- **TRANSFERRED** — an established result shown to hold in the HLS setting;
- **ADAPTED** — an established result modified for the HLS setting;
- **DERIVED-IN-MODEL** — mathematically obtained under stated model
  assumptions;
- **OBSERVED** — found experimentally;
- **HYPOTHESIS / CONJECTURE** — proposed but not established;
- **NULL RESULT** — tested without the proposed useful effect under the stated
  conditions;
- **REJECTED** — contradicted or abandoned under stated conditions;
- **PARKED** — not currently worth pursuing without implying falsehood.

Never silently promote a definition, intuition, model-scoped theorem,
experimental observation, or analogy into a general HLS claim.

---

## 7. Theory and experiments are instruments, not prescribed stages

HLS does not require a fixed research pipeline.

Some questions may require formal theory. Others may require controlled
experiments, empirical evidence, simulation, imported results, counterexamples,
or combinations of these.

Theory and experiments should interact whenever useful:

```text
question
   ->
appropriate theoretical and/or experimental instrument
   ->
evidence
   ->
interpretation
   ->
refined understanding
```

Use the smallest instrument capable of answering the scientific question.

Before an experiment, make explicit where appropriate:

1. what question or mechanism is being tested;
2. what outcome would support the claim;
3. what outcome would weaken or contradict it;
4. what important confounders exist;
5. what scope the result would have.

Prefer a minimal controlled experiment when it can distinguish the alternatives
more cleanly than a large benchmark.

But do not create a toy experiment merely because it is controllable. The
experiment must still address a genuine HLS question.

When an HLS method or architecture claims improvement, demonstrate that
improvement against strong alternatives under fair conditions and relevant
constraints.

HLS research does not, however, require every result to demonstrate an
improvement. Equality, reducibility, impossibility, sufficiency, boundary, and
negative results may themselves be substantive scientific contributions.

---

## 8. Return to the scientific problem

Technical research naturally creates attractive side branches.

This is expected.

The danger is not exploring them. The danger is allowing them to replace the
problem that motivated the research.

Return to the HLS philosophy when:

- a local mathematical construct begins to dominate the programme;
- substantial effort is being spent on something whose system relevance is
  unclear;
- literature search becomes keyword matching;
- novelty is being manufactured inside components;
- novelty is being dismissed merely because components are known;
- an analogy is being treated as a validated mapping;
- a toy model begins defining HLS;
- an experiment is proposed because it can be run rather than because it
  answers a question;
- a current formalism starts constraining the broader HLS vision;
- or a negative result is being resisted because it threatens a preferred
  narrative.

Then ask:

> **What HLS need are we trying to satisfy?**

> **What do we actually know?**

> **What is hypothesis, definition, imported knowledge, model-scoped result,
> observation, or conjecture?**

> **Does the current branch help us build, understand, or test HLS?**

If not, park it.

---

## Core operating rule

The research doctrine can be summarized as:

> **Let the HLS problem determine what knowledge, theory, formalism, and
> experiments are needed. Reuse established knowledge when it genuinely maps
> to that need. Develop new machinery only where necessary. Test claims
> against strong alternatives. Preserve negative and boundary results. Never
> allow the instrument currently being used to redefine the scientific
> problem.**

Or, more compactly:

```text
PROBLEM
   ->
SCIENTIFIC NEED
   ->
BEST AVAILABLE KNOWLEDGE OR NEW DEVELOPMENT
   ->
RIGOROUS MAPPING / FORMALIZATION
   ->
APPROPRIATE EVIDENCE
   ->
SYSTEM-LEVEL UNDERSTANDING
   ->
BACK TO THE PROBLEM
```
