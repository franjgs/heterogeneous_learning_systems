# Research Principles and Operating Doctrine

Status: canonical programme-level methodology and anti-drift document. It does not alter RQ0 or establish any HLS result.

## Purpose

This document defines the **general research doctrine** of the project. It is not a description of a particular Heterogeneous Learning System (HLS), model, paper, experiment, or research question. For the HLS scientific object, use [docs/general_research_model.md](docs/general_research_model.md); for the current foundation map, use [docs/theoretical_foundations_cross_domain.md](docs/theoretical_foundations_cross_domain.md).

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

`established result -> understand -> reproduce when useful -> translate -> adapt -> extend only if necessary`.

New theory should be developed where the existing foundations are insufficient for the system, not merely because novelty is desirable.

---

## 4. Two parallel research lines

The project follows two complementary research lines.

### Line A — Theoretical foundations

Capture the strongest theoretical foundations that can support the system.

For each foundation:

`original problem -> established result -> assumptions -> mathematical structure -> relevance to our system -> limitations -> possible adaptation`.

The objective is to build a theoretical base from proven knowledge.

Theoretical work should answer questions such as:
- Which established results justify a component?
- Under what conditions are they valid?
- Can they be transferred directly?
- What changes when the resources are learning models?
- What part, if any, requires new theory?

### Line B — Experimental foundations

Build minimal experiments that reproduce important established results and test their transfer to our setting.

The preferred sequence is:

`reproduce known result -> verify mechanism -> translate to learning models -> test limits -> adapt to our problem`.

The objective is not merely to obtain positive results. Experiments must reveal whether the imported principle actually survives the translation.

Negative results are useful when they identify where an analogy breaks.

---

## 5. Theory and experiments must interact

The two lines are not sequential.

Theory suggests experiments.

Experiments test assumptions and expose missing theory.

Results from one domain may suggest a mechanism; a minimal experiment can determine whether that mechanism exists when the resources are Machine Learning models or Large Language Models.

The cycle is:

`established theory -> minimal reproduction -> translation -> experimental stress test -> theoretical refinement`.

---

## 6. Build from foundations toward the complete system

Do not let a local mechanism become the research objective merely because it is mathematically interesting or easy to experiment with.

Every theoretical development or experiment must be traceable to the system.

Ask:

> What part of the system does this support?

If there is no clear answer, park it.

The research should progress approximately as:

`fundamental principles -> supported components -> interactions among components -> system architecture/method -> system-level properties -> validation`.

---

## 7. Distinguish imported knowledge from our contribution

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

---

## 8. Novelty should emerge at the correct level

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

## 9. Improvement must be demonstrated

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

---

## 10. Experimental discipline

Before large experiments:

1. state the theoretical principle being tested;
2. define what outcome supports it;
3. define what outcome contradicts it;
4. identify confounders;
5. use the smallest experiment capable of distinguishing the alternatives.

Prefer:

`minimal controlled experiment -> adversarial test -> realistic scenario -> broader validation`.

Do not begin with a large benchmark when a small experiment can answer the scientific question.

---

## 11. Do not overinterpret analogies

Cross-domain similarity is a source of theory, not proof.

For every imported idea, ask:
- What is structurally equivalent?
- What is not equivalent?
- Which assumptions survive?
- Which quantities need new definitions?
- Which conclusions cannot be transferred?

For example, a competence may be treated *like* an asset for some purposes, but that does not make every result of financial portfolio theory automatically valid for competences.

Translation must be demonstrated, not asserted.

---

## 12. Terminology discipline

Use the simplest term that accurately describes the phenomenon.

Do not create terminology merely to make an idea sound novel.

Do not add qualifiers unless they distinguish scientifically different cases.

Define every acronym before first use.

Prefer clear statements such as:

> who does what

> who learns what and from whom

over abstract terminology when the abstraction adds no precision.

---

## 13. Anti-drift rules

Stop and return to this document when any of the following occurs:

- a secondary mathematical construct begins to dominate the research;
- substantial effort is spent proving something that the system does not require;
- novelty is rejected because individual pieces have prior literature;
- new terminology replaces a simple underlying idea;
- experiments are proposed without a theoretical question;
- theory is developed without an identifiable role in the system;
- literature search becomes keyword matching instead of structural reasoning;
- a toy model starts dictating the architecture;
- an attractive side result pulls the project away from the main objective.

The corrective question is:

> Does this strengthen the theoretical foundation, the construction, or the demonstrated value of the system?

If not, park it.

---

## 14. Core operating rule

The general research strategy is:

> **Use the strongest knowledge already available. Verify that it transfers. Adapt it where necessary. Develop new theory only where the system genuinely requires it. Integrate the pieces into a system whose novelty and improvement are demonstrated at system level.**

Or, compactly:

`FOUNDATIONS -> REPRODUCTION -> TRANSFER -> ADAPTATION -> INTEGRATION -> SYSTEM -> DEMONSTRATED IMPROVEMENT`

This is the project's research doctrine.
