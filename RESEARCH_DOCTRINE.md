# Research Principles and Operating Doctrine

Status: canonical programme-level methodology and anti-drift document. It does not alter RQ0 or establish any HLS result.

## Purpose

This document defines the **general research doctrine** of the project. It is not a description of a particular Heterogeneous Learning System (HLS), model, paper, experiment, or research question. For the HLS scientific object, use [docs/general_research_model.md](docs/general_research_model.md); for canonical concepts and source mappings, use [docs/hls_ontology.md](docs/hls_ontology.md); for the current foundation map, use [docs/theoretical_foundations_cross_domain.md](docs/theoretical_foundations_cross_domain.md).

Its purpose is to prevent the research from losing focus.

When there is uncertainty about what to investigate next, what deserves theoretical effort, whether an existing result threatens novelty, or whether an experiment is worth running, **return to this document first**.

---

## 1. The unit of novelty is the system, not every component

A research system is built from pieces.

Those pieces do **not** need to be individually novel.

A strong contribution may combine:
- established theory;
- known mathematical results;
- existing mechanisms;
- standard algorithms;
- results imported from other disciplines;
- adaptations of known methods;
- and genuinely new components where they are actually required.

The scientific question is whether the resulting system, its organization, its interactions, or the behaviour that emerges from them is new and useful.

Therefore:

> The existence of previous work on one component is not evidence that the research direction is occupied.

And:

> Do not manufacture novelty in a component when a sound established result already provides what the system needs.

---

## 2. Start from what is already known

Before developing new theory for a component, search broadly for established foundations that may already solve or illuminate the problem.

The search is **cross-domain**.

Relevant knowledge may come from Machine Learning, economics, finance, operations research, control, cybernetics, organizational science, human resources, psychology, education, biology, ecology, evolution, reliability engineering, robotics, multi-agent systems, statistics, decision theory, or any other field.

Do not constrain the search by the vocabulary of the current application.

Search for the **underlying problem structure**.

Examples include:
- allocation of heterogeneous resources;
- specialization;
- complementarity;
- redundancy;
- distributed knowledge;
- coordination;
- learning;
- competence acquisition;
- changing value of capabilities;
- adaptation;
- reconfiguration;
- uncertainty;
- costs;
- response time;
- capacity;
- robustness;
- changing environments.

---

## 3. Prefer established foundations to unnecessary reinvention

For each important component, identify whenever possible:

1. the canonical or strongest reference;
2. the established principle, theorem, result, hypothesis, or model;
3. its assumptions;
4. its mathematical formulation;
5. what has actually been demonstrated;
6. its limitations;
7. what can legitimately be transferred to our problem.

The preferred sequence is:

`established result -> understand -> reproduce when useful -> map to common ontology -> translate -> adapt -> extend only if necessary`.

New theory should be developed where the existing foundations are insufficient for the system, not merely because novelty is desirable.

### Constructive use of reductions and adversarial analysis

Do not ask whether HLS escapes existing theory. Ask what structure HLS induces, which established theories exploit that structure, how compatible results can be integrated, and what useful HLS-specific consequences follow.

A reduction to optimal control, an MDP, restless multi-armed bandits (RMAB), Whittle indices, resource allocation, portfolio theory, Machine Teaching, state abstraction, or combinatorial optimization is not a reason to discard an HLS phenomenon. Depending on the assumptions, it can supply a rigorous solution, a scalable and interpretable policy, a guarantee, an equivalence boundary, or one component of a wider HLS architecture.

Use adversarial analysis after constructive translation and integration. Its role is to delimit claims: identify equality, reducibility, no-advantage, sufficiency, and failure conditions. It is not a default filter that turns “can be represented by established theory” into “is not worth studying.” A negative or boundary result is scientifically useful because it states when no new HLS-specific machinery is needed.

---

## 4. Establish a common ontology before transferring theory

Before translating or integrating results from another domain, define the common conceptual layer that connects the source theory to our system.

For every relevant object or quantity, specify:

- its definition;
- its mathematical nature;
- its units or normalization;
- its admissible domain or range;
- its operational meaning;
- its role in the source theory;
- its corresponding concept in our system, if one exists.

Classify every proposed mapping as:

- **EQUIVALENT** — the quantities represent the same concept and can be identified;
- **RELATED** — they are different quantities connected by an explicit mapping or model;
- **INCOMPATIBLE** — they must not be identified;
- **UNRESOLVED** — the relationship has not yet been established.

The translation must therefore proceed through a common ontology:

\[
\text{source theory}
\longleftrightarrow
\text{common system ontology}
\longleftrightarrow
\text{our model}.
\]

Do not combine equations merely because variables have similar interpretations, mathematical forms, numerical ranges, or normalizations.

In particular, **semantic and dimensional compatibility must be established before quantities imported from different theories are equated, compared, added, or used as inputs to one another**.

A common numerical range does not imply a common physical or operational meaning. Normalization does not establish dimensional equivalence.

When several external theories are integrated, each must first be mapped independently to the common ontology:

\[
\text{Theory A}
\longleftrightarrow
\text{common ontology}
\longleftrightarrow
\text{Theory B}.
\]

Integration must then be performed through that common layer rather than by directly identifying variables across papers.

If a valid mapping requires an additional transformation,

\[
y=g(x),
\]

that transformation is part of our model and must be stated explicitly. It must not be silently treated as if \(x\) and \(y\) were the same quantity.

If no defensible mapping can be established, the theories must remain separate until the incompatibility is resolved.

The ontology is therefore not merely terminology. It is a **consistency layer for theoretical integration**.

It is not the scientific objective or a contribution by itself. Its role is to prevent incoherent transfer while supporting the construction and evaluation of the HLS system.

---

## 5. Two parallel research lines

The project follows two complementary research lines.

### Line A — Theoretical foundations

Capture the strongest theoretical foundations that can support the system.

For each foundation:

`original problem -> established result -> assumptions -> mathematical structure -> ontology mapping -> relevance to our system -> limitations -> possible adaptation`.

The objective is to build a theoretical base from proven knowledge.

Theoretical work should answer questions such as:
- Which established results justify a component?
- Under what conditions are they valid?
- Can they be transferred directly?
- Which source concepts are genuinely equivalent to concepts in our system?
- Which require an explicit mapping?
- Are their units, domains, and operational meanings compatible?
- What changes when the resources are learning models?
- What part, if any, requires new theory?

### Line B — Experimental foundations

Build minimal experiments that reproduce important established results and test their transfer to our setting.

The preferred sequence is:

`reproduce known result -> verify mechanism -> map to common ontology -> translate to learning models -> test limits -> adapt to our problem`.

The objective is not merely to obtain positive results. Experiments must reveal whether the imported principle actually survives the translation.

Negative results are useful when they identify where an analogy or ontology mapping breaks.

---

## 6. Theory and experiments must interact

The two lines are not sequential.

Theory suggests experiments.

Experiments test assumptions and expose missing theory.

Results from one domain may suggest a mechanism; a minimal experiment can determine whether that mechanism exists when the resources are Machine Learning models or Large Language Models.

The cycle is:

`established theory -> minimal reproduction -> ontology mapping -> translation -> experimental stress test -> theoretical refinement`.

A failed translation may indicate that:
- an assumption does not survive;
- two quantities thought to be equivalent are only related;
- a mapping function is missing;
- units or scales are incompatible;
- or the imported theory does not apply.

Such failures are scientific results, not reasons to force the analogy.

---

## 7. Build from foundations toward the complete system

Do not let a local mechanism become the research objective merely because it is mathematically interesting or easy to experiment with.

Every theoretical development or experiment must be traceable to the system.

Ask:

> What part of the system does this support?

If there is no clear answer, park it.

The research should progress approximately as:

`fundamental principles -> supported components -> interactions among components -> system architecture/method -> system-level properties -> validation`.

---

## 8. Distinguish imported knowledge from our contribution

Maintain explicit epistemic status.

For every important statement, distinguish among:

- **ESTABLISHED** — supported by prior literature.
- **REPRODUCED** — independently replicated experimentally.
- **TRANSFERRED** — established result shown to hold in our setting.
- **ADAPTED** — established result modified for our setting.
- **DERIVED-IN-MODEL** — result mathematically obtained within our stated model.
- **OBSERVED** — empirical result in our experiments.
- **CANDIDATE / HYPOTHESIS** — plausible but not established.
- **PARKED** — not currently worth pursuing, without implying falsehood.
- **REJECTED** — contradicted or abandoned under the stated conditions.
- **NULL RESULT** — a tested mechanism produces no useful effect under the stated conditions.

Never present imported theory as our novelty.

Never discard imported theory merely because it is not novel.

A proposed correspondence between concepts from different theories is not **TRANSFERRED** merely because it is plausible. The ontology mapping itself must be justified.

---

## 9. Novelty should emerge at the correct level

Possible sources of genuine contribution include:
- a new system architecture;
- a new way of combining established principles;
- interactions between components that have not previously been studied together;
- a new decision problem created by those interactions;
- an adaptation required because the resources are learning models;
- a new mathematical property of the integrated system;
- a new method for managing the system;
- a new empirical phenomenon;
- a demonstrated improvement over strong alternatives;
- a generalization that unifies previously separate results.

The project does **not** require every item in this list.

The contribution should be judged at the level where the scientific novelty actually occurs.

---

## 10. Improvement must be demonstrated

Novel organization alone is insufficient.

The final system must provide a measurable advantage under clearly stated conditions.

The relevant advantage may involve:
- quality;
- cost;
- latency;
- capacity;
- robustness;
- adaptability;
- learning efficiency;
- long-term performance;
- or a justified combination of these.

Comparisons must use strong alternatives and fair budgets.

Do not weaken baselines to create an apparent contribution.

In comparisons between joint and separate management, the separate policy must be scientifically strong and must not be defined as weak myopia merely to obtain a strict advantage. If the joint policy is defined as the global optimum over a policy class containing the separate policy, weak dominance is tautological; the research content lies in meaningful policy definitions and strict, equality, and no-advantage conditions.

If several components contribute to a common objective, their contributions must be expressed in compatible quantities or connected through explicitly defined mappings before system-level improvement is computed.

---

## 11. Experimental discipline

Before large experiments:

1. state the theoretical principle being tested;
2. define what outcome supports it;
3. define what outcome contradicts it;
4. identify confounders;
5. verify that the quantities being compared have compatible meanings and scales;
6. use the smallest experiment capable of distinguishing the alternatives.

Prefer:

`minimal controlled experiment -> constructive transfer/integration test -> adversarial audit of claims -> realistic scenario -> broader validation`.

Do not begin with a large benchmark when a small experiment can answer the scientific question.

---

## 12. Do not overinterpret analogies

Cross-domain similarity is a source of theory, not proof.

For every imported idea, ask:
- What is structurally equivalent?
- What is merely related?
- What is incompatible?
- What remains unresolved?
- Which assumptions survive?
- Which quantities need new definitions?
- Are their units and domains compatible?
- Which conclusions cannot be transferred?

For example, a competence may be treated *like* an asset for some purposes, but that does not make every result of financial portfolio theory automatically valid for competences.

Likewise, two quantities normalized to \([0,1]\) are not interchangeable merely because they share the same numerical range.

Translation must be demonstrated, not asserted.

---

## 13. Terminology discipline

Use the simplest term that accurately describes the phenomenon.

Do not create terminology merely to make an idea sound novel.

Do not add qualifiers unless they distinguish scientifically different cases.

Define every acronym before first use.

Prefer clear statements such as:

> who does what

> who learns what and from whom

over abstract terminology when the abstraction adds no precision.

The common ontology should stabilize terminology across imported theories. Source-specific terminology may be retained when discussing a source, but its relationship to the common system terminology must remain explicit.

---

## 14. Anti-drift rules

Stop and return to this document when any of the following occurs:

- a secondary mathematical construct begins to dominate the research;
- substantial effort is spent proving something that the system does not require;
- novelty is rejected because individual pieces have prior literature;
- new terminology replaces a simple underlying idea;
- experiments are proposed without a theoretical question;
- theory is developed without an identifiable role in the system;
- literature search becomes keyword matching instead of structural reasoning;
- a toy model starts dictating the architecture;
- one current source paper starts defining an entire theoretical beam;
- a diagnostic experiment starts dictating the research question;
- an attractive side result pulls the project away from the main objective;
- quantities from different theories are identified because their notation or mathematical form looks similar;
- normalized quantities are combined without establishing semantic or dimensional compatibility;
- a cross-domain analogy is used as if it were already a validated mapping.

The corrective questions are:

> Does this strengthen the theoretical foundation, the construction, or the demonstrated value of the system?

and, when importing or combining theories:

> Are we combining genuinely compatible concepts, or merely mathematically similar quantities?

If not, park it.

---

## 15. Core operating rule

The general research strategy is:

> **Use the strongest knowledge already available. Map it rigorously to a common ontology. Verify that it transfers. Adapt it where necessary. Develop new theory only where the system genuinely requires it. Integrate the pieces into a system whose novelty and improvement are demonstrated at system level.**

Or, compactly:

`FOUNDATIONS -> REPRODUCTION -> ONTOLOGY -> TRANSFER -> ADAPTATION -> INTEGRATION -> SYSTEM -> DEMONSTRATED IMPROVEMENT`

This is the project's research doctrine.
