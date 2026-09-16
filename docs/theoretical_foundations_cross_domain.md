# Cross-domain theoretical foundations for Heterogeneous Learning Systems

## Purpose

This document records established theoretical principles from other
fields that may provide foundations for Heterogeneous Learning Systems
(HLS).

The strategy is:

> reuse what is established -\> integrate what is compatible -\> derive
> what is specific to HLS -\> develop new theory only where necessary.

The research object is a system of models or agents with different
competences, costs, response times, and learning capabilities. The
system decides who performs each task and can also decide who learns
what and from whom. Competences evolve, and the environment may be
non-stationary.

The purpose is not to claim the principles below as novel, but to use
them as established foundations.

The current foundational skeleton is organized around two **master
beams**:

1.  **Beam 1 --- organization of competences:** how current problems are
    allocated to available knowledge and when they are escalated.
2.  **Beam 2 --- evolution of competences:** how operational experience,
    learning, retention and knowledge transfer change future competence.

The remaining foundations in this document support, constrain or extend
these two beams; they are not additional master beams.

## How to use this map

This is a canonical foundation map, not a claim that every listed
principle transfers directly to HLS. The project doctrine is in
[RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md); the HLS scientific
object is in [general_research_model.md](general_research_model.md). For
each foundation selected for active work, record:

1.  a canonical or strong reference;
2.  the original established result and assumptions;
3.  mathematical formulation when available;
4.  what has actually been demonstrated;
5.  a precise HLS translation;
6.  what cannot be inferred for HLS;
7.  whether independent reproduction is useful; and
8.  whether translation requires adaptation or extension.

The list is deliberately open. Search by structural
problems---heterogeneous resources, complementary capabilities,
specialization, redundancy, coordination, distributed knowledge, cost,
latency, capacity, learning, adaptation, and non-stationary
environments---rather than only by HLS terminology or by the word
"diversity."

## 1. Requisite variety --- cybernetics and control

**Canonical source:** W. Ross Ashby, *An Introduction to Cybernetics*,
1956.

**Established principle.** Effective regulation requires a repertoire of
responses sufficient for the relevant variety of environmental states or
disturbances.

**HLS translation.** A system facing heterogeneous or changing problems
may need a sufficiently rich repertoire of competences:

`problem/environment repertoire <-> competence repertoire`.

The relevant issue is not the number of models but the situations for
which the system has effective responses.

**Does not establish:** that maximum heterogeneity is optimal, how
competences should be distributed, or how the repertoire should evolve.

## 2. Portfolio theory --- finance

**Canonical source:** Harry Markowitz, "Portfolio Selection", *The
Journal of Finance*, 1952.

**Established principle.** An asset cannot be assessed only from its
individual expected return. Portfolio value depends on its relation with
the other assets, including covariance. Individually imperfect assets
can jointly improve the return-risk trade-off.

**HLS translation.**

`competence != value of competence`.

A competence/model may have value because of what it contributes to the
whole set, including complementarity with other models and differences
in failure behaviour.

**Does not establish:** that competence is literally a financial asset.
HLS counterparts of return, risk, covariance and efficient frontier must
be defined rather than assumed.

## 3. Collective problem solving and functional complementarity

**Canonical source:** Lu Hong and Scott E. Page, "Groups of diverse
problem solvers can outperform groups of high-ability problem solvers",
*PNAS*, 2004.

**Established principle.** Under explicit assumptions, groups with
different problem-solving perspectives or heuristics can outperform
groups selected only for high individual ability.

**HLS translation.** Selecting the individually strongest models need
not yield the strongest system. Complementary competences or failure
patterns can have collective value.

**Does not establish:** that heterogeneity is always beneficial or that
competence evolution is valuable.

## 4. Transactive memory systems --- organizational knowledge

**Canonical foundations:** Daniel M. Wegner; Linda Argote and Yuqing
Ren, "Transactive Memory Systems: A Microfoundation of Dynamic
Capabilities", *Journal of Management Studies*, 2012.

**Established principle.** Groups can distribute knowledge among
members. Effective collective performance depends on specialization,
credibility, coordination and knowing "who knows what".

**HLS translation.** Distributed competence can be useful only if the
system can identify and exploit where relevant competence resides.

**Does not establish:** the optimal competence distribution or how
teaching should modify it.

## 5. Exploration and exploitation --- organizational learning

**Canonical source:** James G. March, "Exploration and Exploitation in
Organizational Learning", *Organization Science*, 1991.

**Established principle.** Exploiting current knowledge and developing
future capability create a fundamental tension. Excessive exploitation
can improve short-term performance while reducing long-term
adaptability.

**HLS translation.** The model that should work now need not be the
model in which learning resources should be invested.

**Does not establish:** who should learn which competence or the optimal
HLS policy.

## 6. Dynamic capabilities --- strategy and organizational theory

**Canonical source:** David J. Teece, Gary Pisano and Amy Shuen,
"Dynamic Capabilities and Strategic Management", *Strategic Management
Journal*, 1997.

**Established principle.** In changing environments, performance depends
not only on current resources but on the ability to integrate, build and
reconfigure competences. Historical trajectories constrain future
possibilities.

**HLS translation.** The competence distribution should not necessarily
be treated as fixed:

`C_t -> C_(t+1)`.

**Does not establish:** an HLS objective or algorithm.

## 7. Beam 1 --- comparative advantage, division of labour and knowledge hierarchies

**Primary foundation:** Luis Garicano, "Hierarchies and the Organization
of Knowledge in Production", *Journal of Political Economy*, 108(5),
874--904, 2000.

**Established principle.** Knowledge acquisition is costly and obtaining
help from another knowledgeable agent also consumes resources. Efficient
organization can therefore distribute knowledge rather than require
every operational unit to know every solution. Frequent problems are
handled closer to production, while exceptional problems are escalated
to more specialized knowledge holders. This provides a formal foundation
for division of labour and management by exception.

**HLS translation.** Fast/cheap models and more capable/costly models
can have different operational roles. Current problem demand, available
competence and the costs of using or accessing expertise determine how
work should be organized and when escalation is valuable.

**Role in the programme.** Garicano is the primary foundation for **Beam
1: organization of competences** --- essentially, *who does what* given
the current competence distribution.

**Does not establish:** how current task allocation changes future
competence, or that a fixed student/teacher hierarchy is optimal when
models can learn.

## 8. Beam 2 --- experience, learning, retention and competence evolution

Beam 2 is supported by several complementary foundations rather than by
a single paper.

### 8.1 Learning by doing

**Canonical source:** Kenneth J. Arrow, "The Economic Implications of
Learning by Doing", *Review of Economic Studies*, 29(3), 155--173, 1962.

**Established principle.** Productive experience can generate learning.
Current operation can therefore affect future productive capability.

**HLS translation.** Performing tasks can be both current service and a
source of future competence.

**Does not establish:** which task-specific competences are acquired or
how a heterogeneous system should allocate tasks.

### 8.2 Task-specific human capital

**Relevant foundation:** Robert Gibbons and Michael Waldman,
"Task-Specific Human Capital", *American Economic Review*, 94(2),
203--207, 2004.

**Established principle.** Learning by doing can be task-specific:
experience accumulated on a task can increase capability relevant to
that task rather than only a generic stock of experience.

**HLS translation.** Experience and competence should be representable
over a task/problem space rather than necessarily as one scalar amount
of practice.

### 8.3 Explicit competence dynamics

**Primary operations-research foundation:** Walter J. Gutjahr, "Optimal
dynamic portfolio selection for projects under a competence development
model", *OR Spectrum*, 33, 173--206, 2011. DOI
10.1007/s00291-009-0180-9.

Gutjahr provides an explicit dynamic competence state. In a compact
HLS-oriented notation,

`C_(i,t) = C_(i,1) - beta_i (t-1) + eta_i sum_(s<t) x_(i,s)`,

where `x_(i,s)` is work invested in project/task class `i`, `eta_i`
represents learning and `beta_i` depreciation/forgetting. Efficiency is
a monotone function of competence.

**Established consequence.** Present work allocation can change future
competence and therefore future productivity. The model also shows that
concentration versus mixed allocation is conditional on the learning
function, depreciation, horizon and constraints; neither is universally
optimal.

**Does not establish:** a heterogeneous multi-model controller, explicit
teacher-to-learner transfer, or joint decisions about who performs and
who learns. Competence is modeled at aggregate team/project-class level.

### 8.4 Experience-to-knowledge cycle

**Canonical synthesis:** Linda Argote and Ella Miron-Spektor,
"Organizational Learning: From Experience to Knowledge", *Organization
Science*, 22(5), 1123--1137, 2011. DOI 10.1287/orsc.1100.0621.

**Established framework.** Organizational learning is change in
organizational knowledge as a function of experience. Task-performance
experience is converted into knowledge; acquired knowledge changes
organizational context and thereby affects future experience. The
framework distinguishes **knowledge creation**, **knowledge retention**
and **knowledge transfer**.

The review also supports a fine-grained characterization of experience,
including the task on which it was acquired, and documents knowledge
depreciation/forgetting as an important empirical phenomenon.

**HLS translation.** This provides the conceptual bridge from
operational task performance to future competence state. It supports
task-indexed experience, retention/forgetting and the feedback cycle
from current operation to future capability.

**Does not establish:** a unique HLS state-transition equation or an
optimal routing policy. Explicit teacher-to-learner transfer is part of
the wider framework but is not required for the minimal two-beam model.

### 8.5 Complementary competence-development literature

**Additional foundations already audited:** Gutjahr et al. (2010); Hopp,
Tekin and Van Oyen (2004); Borgonjon and Maenhout (2024); and literature
on assignment with learning-by-doing, cross-training and knowledge
transfer.

These works support the broader propositions that skills have
acquisition costs, learning and forgetting affect future productivity,
and training/assignment can change future operational possibilities.

**Role in the programme.** Together, these foundations support **Beam 2:
evolution of competences** --- how current experience and learning
change what the system will be able to do later.

## 9. Response diversity and resilience --- ecology

**Canonical source:** Thomas Elmqvist et al., "Response diversity,
ecosystem change, and resilience", *Frontiers in Ecology and the
Environment*, 2003.

**Established principle.** Organisms contributing to similar functions
but responding differently to environmental change can increase
resilience.

**HLS translation.** Models with apparently overlapping competence can
still have value if they respond differently when tasks or conditions
change.

**Does not establish:** that redundancy or response diversity should
always be increased.

## 10. Bet hedging --- evolutionary biology

**Established principle.** Under environmental uncertainty, maintaining
alternative phenotypes or strategies can improve long-term outcomes even
when some alternatives are inferior in the current environment.

**HLS translation.** A competence that is not currently the most
efficient can retain future value under uncertainty.

**Does not establish:** a direct equivalence between biological fitness
and HLS utility.

## 11. Redundancy and design diversity --- dependable systems

**Canonical foundations:** Brian Randell; Algirdas Avizienis and
subsequent fault-tolerant computing literature.

**Established principle.** Redundancy can improve reliability,
especially when redundant components do not share the same failure
modes. Correlated failures reduce its value.

**HLS translation.** Multiple models with nominally similar competence
may provide robustness when their weaknesses differ. Replicating
identical failure behaviour provides little such benefit.

**Does not establish:** that redundancy is preferable to specialization;
redundancy has costs.

## 12. Ensemble learning --- Machine Learning

**Established principle.** Combining predictors can improve performance
when individual predictive quality is accompanied by sufficiently
complementary errors. Ensemble theory formalizes relationships among
individual performance, error dependence and collective performance.

**HLS translation.** System value depends on both individual competence
and relationships among models.

**Does not establish:** the broader HLS problem of task allocation,
heterogeneous costs, selective learning and competence evolution.

## 13. No Free Lunch results --- optimization

**Canonical source:** David H. Wolpert and William G. Macready, "No Free
Lunch Theorems for Optimization", *IEEE Transactions on Evolutionary
Computation*, 1997.

**Established principle.** Over sufficiently broad classes of problems,
no optimizer has universal superiority. Advantage requires assumptions
or specialization to properties of the problem distribution.

**HLS translation.** There is no general reason to expect one model to
dominate every relevant task distribution.

**Does not establish:** that heterogeneous portfolios are superior.

# Two-beam theoretical synthesis

The minimal theoretical skeleton now has a defensible cross-domain
foundation:

`problem demand + current competence`
`-> operational organization / routing        [Beam 1: Garicano]`
`-> task-performance experience` `-> learning / retention`
`-> future competence                         [Beam 2: Arrow; Gibbons-Waldman; Gutjahr; Argote]`
`-> future operational organization / routing`.

A useful task-indexed HLS representation is:

`e_(t+1)(q) = rho_q e_t(q) + x_t(q)`

`C_t(q) = L_q(e_t(q))`

where `q` denotes a task/problem region, `x_t(q)` is relevant experience
generated by operation, `rho_q` represents retention, and `L_q` maps
effective accumulated experience into competence.

**Epistemic status.** This exact representation is an HLS synthesis, not
a theorem copied from any one source. Its components are grounded
separately: learning from experience, task-specificity, explicit
learning/depreciation dynamics, and the experience -\> knowledge -\>
future experience cycle.

The natural interface between the two beams is therefore **operational
experience**:

`routing -> work performed on q -> experience x_t(q) -> future competence C_(t+1)(q)`.

This avoids introducing an artificial mapping between Garicano's
knowledge-acquisition cost and HLS competence. The same operational
allocation that creates current value can alter the competence state on
which future operational organization depends.

## What is already supported

Subject to the assumptions of the source theories, the foundations
support that:

-   knowledge can be organized according to problem demand and the costs
    of possessing/accessing expertise;
-   task performance can generate learning;
-   learning can be task-specific;
-   accumulated experience can alter future competence/productivity;
-   acquired knowledge can depreciate or be forgotten;
-   experience and knowledge form a feedback cycle;
-   consequently, when task allocation determines experience, current
    operational allocation can affect future competence and future
    operational possibilities.

The last statement is the structural integration of the two beams. It is
a synthesis of established mechanisms, not yet a claimed novel HLS
theorem.

## What remains open

The foundations do **not** yet provide:

-   a unique mathematical form for learning, retention, cross-task
    generalization or competence measurement in machine-learning
    systems;
-   an optimal dynamic policy for Garicano-style organization with
    endogenous competence evolution;
-   conditions under which the myopic operational optimum differs from
    the long-horizon optimum once competence evolution is active;
-   evidence that the combined dynamic organization creates material
    advantage for real learning models;
-   the later multi-agent questions of heterogeneous competence
    allocation, teacher selection, explicit knowledge transfer, and
    jointly deciding who performs versus who learns.

The immediate theoretical task is therefore no longer to search for a
conceptual bridge between Beam 1 and Beam 2. It is to derive the
consequences of their combination.

A minimal dynamic comparison is between

`a_t^myopic = argmax_a R_t`

and

`a_t^dynamic = argmax_a { R_t + delta V_(t+1)(C_(t+1)) }`,

with `C_(t+1)` generated by task-specific experience resulting from
`a_t`.

The useful theoretical target is to characterize explicit conditions
under which these decisions coincide or differ, including null cases.

# Common structure

Across these domains, collective value repeatedly depends on:

1.  **Repertoire** --- capabilities appropriate to situations the system
    may face.
2.  **Individual quality** --- useful competence of each component.
3.  **Complementarity** --- contribution relative to what other
    components provide.
4.  **Specialization and division of labour** --- use of resources where
    they have comparative advantage.
5.  **Redundancy** --- overlapping capability when it provides capacity
    or robustness.
6.  **Coordination** --- ability to locate and exploit distributed
    competence.
7.  **Future value** --- present performance is insufficient when
    environment or competence can change.
8.  **Competence acquisition** --- new capability has a cost and a
    possible future return.
9.  **Reconfiguration** --- the useful organization of competence can
    change with the environment.
10. **Uncertainty** --- capabilities that are not optimal today may
    preserve useful future options.

These are established ideas to support and constrain HLS theory, not
proposed HLS novelties.

# Working synthesis for HLS

A compact representation is:

`problem repertoire <-> competence repertoire <-> organization of competences <-> use of competences <-> learning and competence evolution <-> future competence repertoire`.

For model `i`, competence `z`, and time `t`, distinguish the competence
itself, `c_(iz,t)`, from its value to the system, `V_(iz,t)`.

That value may depend on future task demand, other available
competences, operational cost and latency, capacity, complementarity,
correlated failure, learning and maintenance costs, environmental change
and acquisition delay.

Therefore:

> A competence should not be valued only by how much it improves an
> individual model. Its value depends on what it contributes to the
> competence organization of the whole system and on the environments in
> which that organization will operate.

This is a synthesis of established principles, not yet a claimed HLS
theorem.

# Relation to current research

Competence Investment Value (CIV) is one possible mathematical tool for
representing the cost and future operational value of acquiring or
modifying competence. It is subordinate to the broader foundations.

Replication, rebalancing and specialization are possible competence
transformations, not the organizing theory.

The research question at this level is:

> How should a system of learning models with different competences,
> costs and response times organize the use and development of those
> competences when the problems it faces can change?

The objective is not to rediscover portfolio diversification,
specialization, resilience, exploration, cross-training or dynamic
capabilities. It is to determine how established principles interact
when the resources are learning models whose competences can themselves
change.

# Research discipline

For every imported principle, record:

1.  original established result;
2.  assumptions;
3.  mathematical formulation where available;
4.  precise HLS translation;
5.  what the result does not imply for HLS;
6.  whether combining it with other principles produces an HLS-specific
    property, question or method.

Do not reject an idea merely because one component is already known.
Established results are theoretical assets to be reused.
