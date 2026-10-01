# HLS Philosophy

**Status:** philosophical compass for the Heterogeneous Learning Systems
(HLS) research programme.

**Purpose:** state the **what**, the **why**, and the **what for** of
HLS. This document is intended to remain stable while particular
research questions, theories, models, methods, experiments, and
implementations evolve, succeed, fail, or are abandoned.

> **This document does not define how HLS must be investigated.**
>
> Research doctrine, formal models, ontology, experimental frameworks,
> algorithms, baselines, and evidence belong to other documents. This
> document states the problem and the direction to which the programme
> should return when technical work risks becoming the objective itself.

------------------------------------------------------------------------

## 1. Why HLS exists --- Limited capabilities, changing problems

Many relevant problems require different kinds and levels of competence.
No single agent can necessarily provide all of them effectively and
efficiently under all operating conditions.

HLS considers systems composed of multiple models or agents with
different competences, specializations, costs, latencies, capacities,
learning potential, and limitations. Some may be deep specialists; some
may be broader but less proficient; some may be cheap and fast; others
expensive and powerful. Some may readily acquire a particular
competence, while others may learn it slowly, only partially, or not at
all.

**Heterogeneity is therefore not necessarily a defect to eliminate. It
can be a resource to organize.**

At the same time, the problems faced by the system are not necessarily
fixed. Needs may change in frequency, importance, difficulty,
composition, or type. New problems may appear. Existing problems may
disappear. Existing competences may gain or lose value, while previously
unnecessary competences may become important.

HLS starts from the coexistence of two fundamental facts:

1. **capabilities are distributed, heterogeneous, limited, and potentially evolvable;**
2. **the problems and needs that give those capabilities value may also change over time.**

These two facts create two related system-level problems. The
capabilities that exist at a given moment have to be organized and used;
and the distribution of capabilities itself may have to be developed as
future needs change. Neither problem is unique to artificial
intelligence. Human organizations have long faced the problem of
organizing distributed knowledge, while learning and competence
development have long been studied as allocation and investment
problems. HLS builds on such established knowledge where it transfers,
while asking what changes when the members of the collective are
heterogeneous artificial learning systems.

The fundamental challenge is consequently not to make every agent know
everything. It is to organize and develop limited capabilities as both
the system and the problems it faces evolve.

A compact statement of the HLS vision is:

> **HLS studies how to organize and develop heterogeneous, limited, and
> evolving learning capabilities so that changing problems and needs can
> be addressed effectively and efficiently over time.**

------------------------------------------------------------------------

## 2. The system-level object --- The collective distribution of capabilities

The fundamental object in HLS is not an isolated learner.

It is a **collective distribution of competences and capabilities**.

The value of a member cannot in general be assessed independently of:

- what other members can do;
- what the current and future problems require;
- how members are organized;
- what resources they consume;
- what roles they can play;
- what they can learn;
- what they cannot learn;
- what knowledge can be transferred among them;
- and how the resulting organization can be used.

Accordingly, HLS does not adopt individual omniscience as an ideal end
state.

Improving every agent on every competence may be impossible, wasteful,
or harmful to system-level efficiency. A useful organization may
preserve specialization, maintain selected redundancy, create
complementary capabilities, or leave some agents without competences
that they do not need or are poorly suited to acquire.

The relevant question is not:

> How much can every member learn?

but rather:

> **What distribution of capabilities should the system possess, and how
> should that distribution be used and changed as problems and needs
> evolve?**

Diversity is not an objective by itself. Its value is instrumental:
diversity matters when it improves the collective's ability to solve the
problems it faces under relevant constraints.

------------------------------------------------------------------------

## 3. Beam 1 --- Organization / Use of Competences

The first foundational beam asks:

> **Who should do what?**

Given the capabilities currently available and the problems currently
faced, how should the system organize their use?

This is fundamentally a problem of **organizing distributed
competence**. The central idea is not specific to machine learning.
Established theories of organizations have studied how distributed
knowledge, specialization, problem solving, communication, and limited
individual capabilities can be organized so that a collective can solve
problems that its members face.

A particularly important theoretical antecedent for this beam is
Garicano's theory of the organization of knowledge. HLS does not treat
that theory as a model of artificial intelligence, nor does it identify
human knowledge workers directly with learning agents. Rather, it takes
from this line of work a more general organizational principle: when
knowledge or competence is distributed and problems differ in what they
require, **how access to those capabilities is organized can affect what
the collective can achieve and at what cost**.

HLS therefore asks which parts of this organizational logic transfer to
heterogeneous artificial learning systems, which require adaptation,
and which cease to apply because artificial agents have different
capabilities, costs, communication mechanisms, capacities, or operating
constraints.

Depending on the HLS, organization may involve task allocation and
routing, specialization and division of labour, collaboration,
delegation, escalation, temporary teams or task forces, specialists and
generalists, redundancy, sequencing, scarce capacity, cost, latency,
communication, and organizational or coordination roles.

The essential point is broader than any particular mechanism:

> **Beam 1 concerns how the collective uses and organizes the
> capabilities it currently possesses in order to solve problems
> effectively and efficiently.**

Routing is one possible mechanism inside Beam 1. It is not Beam 1
itself.

This beam also has an important boundary. Heterogeneity alone does not
imply collective advantage, and a more elaborate organization is not
necessarily useful. In some conditions, a single member or a simple
organization may already reproduce everything that a richer collective
organization can achieve.

Accordingly, HLS is concerned not only with demonstrating organizational
advantages, but also with determining **when organization matters, when
it does not, how much it can contribute, and under which operating
conditions additional organizational complexity is justified**.

------------------------------------------------------------------------

## 4. Beam 2 --- Development / Evolution of Competences

The second foundational beam asks:

> **Who should learn what, how, and from whom?**

Given current capabilities, possible future problems and needs, learning
possibilities, and relevant constraints, how should the collective's
distribution of competences evolve?

This is fundamentally a problem of **developing distributed
competence**. Here too HLS need not begin from first principles.
Established work on competence development and learning investment,
including the line represented by Gutjahr, provides theoretical
foundations for reasoning about how limited resources can be allocated
to the development of capabilities whose benefits may be heterogeneous
and realized in the future.

HLS does not assume that such models transfer unchanged to artificial
learning systems. Their concepts and assumptions must be mapped to the
HLS setting, where learning may depend on data, experience, teachers,
knowledge sources, architecture, specialization, operational exposure,
compute, time, or other mechanisms, and where agents may differ
substantially in what they can learn and at what cost.

The transferable principle is broader than any particular learning
mechanism: **competence development is a selective system-level
decision whose value depends on what is learned, by whom, at what cost,
and on the future usefulness of the resulting capability**.

Development may arise through learning by doing, explicit training,
teaching, knowledge transfer, observation, distillation,
teacher--student interaction, specialization, broadening, retention,
forgetting, interference, or other justified mechanisms of competence
change.

Beam 2 does not seek to make every member better at everything.

A valid development choice may be to teach one member but not another,
deepen an existing specialization, preserve a competence, create useful
redundancy, avoid developing a competence in an agent poorly suited to
acquire it, or make no competence change at all.

> **The objective is the useful evolution of collective capabilities,
> not universal learning or homogenization.**

As with Beam 1, more development is not automatically better. There are
conditions under which competence development has value, conditions
under which it does not, and conditions under which apparently
sophisticated development strategies may reduce to simpler established
decision problems. Characterizing these boundaries is part of HLS.

------------------------------------------------------------------------

## 5. The defining HLS problem --- Organization and development can be coupled

The two beams address different questions and have meaningful
theoretical foundations independently of HLS:

- **Beam 1 — organization / use of competence:** Who should do what?
- **Beam 2 — development / evolution of competence:** Who should learn what, how, and from whom?

This distinction is important. HLS is not intended to rename either
problem, nor would simply placing an organizational model beside a
competence-development model constitute a substantive HLS contribution.

The central HLS question appears when the two problems interact.

How capabilities are organized and used can determine who obtains
experience, who interacts with whom, which knowledge is generated or
exposed, which learning opportunities arise, and which development
actions become possible.

Conversely, competence development changes what members can do, their
relative strengths and limitations, the value of specialization or
collaboration, and therefore how the collective may be organized in the
future.

The conceptual loop is therefore:

**problems / needs → organization / use of current capabilities →
operation, interaction, experience, knowledge → development / evolution
of capabilities → future distribution of capabilities → future
organization / use → ...**

While this loop operates, the problems and needs themselves may continue
to change.

The conceptual architecture of the programme is:

**Garicano-type organizational foundation → Beam 1 → organization and use of current competences**

**Gutjahr-type competence-development foundation → Beam 2 → development and evolution of competences**

**Beam 1 + Beam 2 → HLS organization--development interaction**

Garicano and Gutjahr are important theoretical anchors for the two
beams, respectively, but **HLS is not the sum of Garicano and Gutjahr**.
Each foundation must first be understood, mapped, tested for
transferability, and adapted where required to heterogeneous artificial
learning systems.

More importantly, the existence of both beams does not establish that
they must be optimized jointly.

It may be possible under some conditions to organize current
capabilities optimally and develop future capabilities independently
without any loss. A sufficiently coordinated modular architecture may
sometimes reproduce the same result. In such cases, separation is a
valid solution and no stronger HLS-specific coupling mechanism is
required.

In other conditions, decisions about current use may change the future
competence distribution, or the value of competence development may
depend on future organization, so that treating the two problems
independently may cease to be sufficient.

Determining the boundary between these regimes is central to the HLS
programme:

> **When can organization of current capabilities and development of
> future capabilities be treated separately, and when does their
> interaction materially change what the collective can achieve?**

This is not answered in advance.

> **HLS is especially concerned with identifying, characterizing, and
> exploiting consequential interactions between how capabilities are
> used and how they develop, while also establishing the conditions
> under which those interactions can safely be ignored.**

------------------------------------------------------------------------

## 6. Problem solving, collective organization, and the biological/human--AI bridge

The starting point is not work organization itself. It is **problem
solving**.

Living systems have always faced changing problems under limited
capabilities and resources. Problems appear, disappear, change in
importance, and may exceed what an individual can solve alone. Across
biological evolution, social organisms have developed forms of
collective action that combine individual capabilities through
mechanisms such as cooperation, coordination, communication,
specialization, and social learning.

Humans have developed this capacity much further. Over long historical
periods, people have organized themselves into groups, teams,
professions, hierarchies, institutions, and temporary organizations in
order to solve changing problems. Division of labour, specialization,
delegation, teaching, apprenticeship, coordination, redundancy,
training, and organizational adaptation are part of a vast accumulated
experience in combining limited individual capabilities into collective
problem-solving capability.

This accumulated experience is relevant to **both HLS beams**. Human
organizations do not only allocate existing knowledge; they also decide
where expertise should be created, maintained, transferred, deepened,
or made redundant. Organization and competence development have
therefore been studied separately and together in several established
disciplines.

HLS does not assume that biological or human organizations should be
copied into artificial systems.

Their importance is more fundamental: they provide evidence that
**organization can transform distributed and limited individual
capabilities into collective problem-solving capability**, and that the
distribution of those capabilities can itself be deliberately developed
in response to present and anticipated needs.

HLS can therefore draw on what is known about collective problem solving,
organization, and competence development while asking which principles
remain useful when the problem solvers are artificial learning agents.
Some principles may transfer. Some may depend on specifically biological
or human constraints. Artificial learners may also make possible forms
of organization, communication, replication, learning, or adaptation
that have no practical human equivalent.

The bridge is therefore not simple imitation of human organization.
Rather, HLS lies at the intersection of:

- established knowledge about collective problem solving, organization,
  and competence development; and
- the distinctive properties and possibilities of artificial learning
  systems.

> **Organization and development are means; collective problem solving
> is the purpose.**

------------------------------------------------------------------------

## 7. Dynamics and adaptation --- Both sides evolve

HLS is fundamentally dynamic.

The problems and needs faced by the system may evolve:

\[
D_t ightarrow D_{t+1}.
\]

The collective's capabilities may also evolve:

\[
C_t ightarrow C_{t+1}.
\]

Learning, transfer, specialization, retention, forgetting, interference,
saturation, and other processes may change what the collective can do.
At the same time, new problems may appear, old ones may disappear, and
the relative value of existing capabilities may change.

Organization therefore has both a present and potentially a future
role. It determines how current capabilities are used, but that use may
also affect the information, experience, resources, and learning
opportunities from which future capabilities develop.

Conversely, competence development is not valuable in isolation. Its
value depends on how the resulting capabilities can contribute to
future collective problem solving and on how the collective will be
organized to exploit them.

The core adaptive relationship is therefore:

**changing problems and needs ↔ changing organization and distribution
of capabilities**

HLS does not merely seek the best organization of a fixed portfolio
against a fixed task distribution.

> **It seeks to understand how a collective can remain appropriately
> organized and capable as both its competences and the problems it
> faces evolve.**

A competence has value because of its contribution to problem solving. A
competence change has value because of how it changes future collective
capability relative to future problems and needs.

------------------------------------------------------------------------

## 8. Effectiveness, efficiency, and constraints

Organization and learning are not ends in themselves.

The purpose is to solve problems **effectively and efficiently under
relevant constraints**.

Depending on the application, those constraints may include quality,
operational value, latency, compute, energy, memory, communication,
capacity, monetary cost, learning cost, development time, reliability,
deadlines, or other scarce resources.

There is no requirement that every HLS instantiate the same costs or
performance measures. The general principle is that capabilities and
resources are limited, and organization matters partly because of those
limitations.

If one zero-cost, zero-latency, unlimited-capacity, instantly learning,
omniscient agent could solve every relevant problem, much of the HLS
organizational and development problem would disappear.

> **The objective is not merely collective capability, but effective and
> efficient collective problem solving under real limitations.**

------------------------------------------------------------------------

## 9. HLS is a question, not a predetermined answer

HLS does not assume that:

- every agent should learn every competence;
- every agent can learn every competence;
- competence improvement is always beneficial;
- heterogeneity is always beneficial;
- diversity should be rewarded for its own sake;
- specialization is always preferable to generalization;
- learning opportunities always produce competence change;
- operational experience is the only source of learning;
- one agent must solve each problem;
- a central coordinator must be omniscient;
- hierarchy is always useful;
- biological or human organizational structures should be copied;
- organization and competence development must always be jointly managed;
- or HLS-specific mechanisms must outperform established organizational or competence-development methods.

HLS therefore does not prescribe in advance what a good heterogeneous
learning system must look like.

A particular problem may favour specialization or generalization,
heterogeneity or homogeneity, hierarchy or decentralization, integrated
or modular organization, learning or no learning, or independent rather
than coupled management of organization and development.

A scientifically important HLS result may therefore be a positive
capability result, a limit, an equivalence, a sufficiency condition, or
a reduction to an established theory.

> **HLS defines a problem and a space of possibilities; it does not
> predetermine the answers that scientific investigation should
> produce.**

------------------------------------------------------------------------

## 10. The HLS compass --- What are we ultimately trying to achieve?

The long-term purpose of HLS is to understand how limited learning
agents can become an effective adaptive collective.

The programme seeks principles for organizing the capabilities that
exist now and developing the capabilities that may be needed later,
while the problems themselves continue to change.

The two-beam structure provides the conceptual backbone:

> **Beam 1:** How should existing distributed competences be organized
> and used?

> **Beam 2:** How should distributed competences be developed and
> evolved?

And their interaction provides the central integrative question:

> **When is it sufficient to solve these two problems separately, and
> when does their coupling materially affect collective capability?**

The sentence to return to when the programme becomes technically
complicated is:

> **HLS seeks to understand how a collective of heterogeneous, limited,
> and evolvable learning agents should be organized and developed so
> that, together, they can solve changing problems effectively and
> efficiently over time.**

The two foundational operational questions are:

> **Who should do what?**

> **Who should learn what, how, and from whom?**

And the question that keeps the research aligned with its purpose is:

> **Does what we are studying help us understand collective problem
> solving through the organization of current capabilities, the
> development of future capabilities, or the interaction between them?**

If not, it may be scientifically interesting, but it is not central to
HLS.

------------------------------------------------------------------------

## Closing principle

HLS is not ultimately about routing, ensembles, teaching, hierarchy,
task allocation, knowledge transfer, or any other individual mechanism.

Nor is HLS simply the application to artificial agents of an existing
theory of organization or competence development.

Those theories provide foundations. Individual mechanisms provide
possible implementations. The scientific object remains the collective
system and the relationship between its present organization, its future
development, and the problems it must solve.

Those elements matter only insofar as they contribute to the central
problem:

> **How can a collective of limited learning agents organize and evolve
> its distributed capabilities to solve changing problems effectively
> and efficiently over time?**
