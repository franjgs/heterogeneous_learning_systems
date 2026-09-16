# Cross-domain theoretical foundations for Heterogeneous Learning Systems

## Purpose

This document records established theoretical principles from other fields that may provide foundations for Heterogeneous Learning Systems (HLS).

The strategy is:

> reuse what is established -> integrate what is compatible -> derive what is specific to HLS -> develop new theory only where necessary.

The research object is a system of models or agents with different competences, costs, response times, and learning capabilities. The system decides who performs each task and can also decide who learns what and from whom. Competences evolve, and the environment may be non-stationary.

The purpose is not to claim the principles below as novel, but to use them as established foundations.

## How to use this map

This is a canonical foundation map, not a claim that every listed principle transfers directly to HLS. The project doctrine is in [RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md); the HLS scientific object is in [general_research_model.md](general_research_model.md). For each foundation selected for active work, record:

1. a canonical or strong reference;
2. the original established result and assumptions;
3. mathematical formulation when available;
4. what has actually been demonstrated;
5. a precise HLS translation;
6. what cannot be inferred for HLS;
7. whether independent reproduction is useful; and
8. whether translation requires adaptation or extension.

The list is deliberately open. Search by structural problems---heterogeneous resources, complementary capabilities, specialization, redundancy, coordination, distributed knowledge, cost, latency, capacity, learning, adaptation, and non-stationary environments---rather than only by HLS terminology or by the word “diversity.”

## 1. Requisite variety — cybernetics and control

**Canonical source:** W. Ross Ashby, *An Introduction to Cybernetics*, 1956.

**Established principle.** Effective regulation requires a repertoire of responses sufficient for the relevant variety of environmental states or disturbances.

**HLS translation.** A system facing heterogeneous or changing problems may need a sufficiently rich repertoire of competences:

`problem/environment repertoire <-> competence repertoire`.

The relevant issue is not the number of models but the situations for which the system has effective responses.

**Does not establish:** that maximum heterogeneity is optimal, how competences should be distributed, or how the repertoire should evolve.

## 2. Portfolio theory — finance

**Canonical source:** Harry Markowitz, “Portfolio Selection”, *The Journal of Finance*, 1952.

**Established principle.** An asset cannot be assessed only from its individual expected return. Portfolio value depends on its relation with the other assets, including covariance. Individually imperfect assets can jointly improve the return-risk trade-off.

**HLS translation.**

`competence != value of competence`.

A competence/model may have value because of what it contributes to the whole set, including complementarity with other models and differences in failure behaviour.

**Does not establish:** that competence is literally a financial asset. HLS counterparts of return, risk, covariance and efficient frontier must be defined rather than assumed.

## 3. Collective problem solving and functional complementarity

**Canonical source:** Lu Hong and Scott E. Page, “Groups of diverse problem solvers can outperform groups of high-ability problem solvers”, *PNAS*, 2004.

**Established principle.** Under explicit assumptions, groups with different problem-solving perspectives or heuristics can outperform groups selected only for high individual ability.

**HLS translation.** Selecting the individually strongest models need not yield the strongest system. Complementary competences or failure patterns can have collective value.

**Does not establish:** that heterogeneity is always beneficial or that competence evolution is valuable.

## 4. Transactive memory systems — organizational knowledge

**Canonical foundations:** Daniel M. Wegner; Linda Argote and Yuqing Ren, “Transactive Memory Systems: A Microfoundation of Dynamic Capabilities”, *Journal of Management Studies*, 2012.

**Established principle.** Groups can distribute knowledge among members. Effective collective performance depends on specialization, credibility, coordination and knowing “who knows what”.

**HLS translation.** Distributed competence can be useful only if the system can identify and exploit where relevant competence resides.

**Does not establish:** the optimal competence distribution or how teaching should modify it.

## 5. Exploration and exploitation — organizational learning

**Canonical source:** James G. March, “Exploration and Exploitation in Organizational Learning”, *Organization Science*, 1991.

**Established principle.** Exploiting current knowledge and developing future capability create a fundamental tension. Excessive exploitation can improve short-term performance while reducing long-term adaptability.

**HLS translation.** The model that should work now need not be the model in which learning resources should be invested.

**Does not establish:** who should learn which competence or the optimal HLS policy.

## 6. Dynamic capabilities — strategy and organizational theory

**Canonical source:** David J. Teece, Gary Pisano and Amy Shuen, “Dynamic Capabilities and Strategic Management”, *Strategic Management Journal*, 1997.

**Established principle.** In changing environments, performance depends not only on current resources but on the ability to integrate, build and reconfigure competences. Historical trajectories constrain future possibilities.

**HLS translation.** The competence distribution should not necessarily be treated as fixed:

`C_t -> C_(t+1)`.

**Does not establish:** an HLS objective or algorithm.

## 7. Comparative advantage, division of labour and knowledge hierarchies

**Canonical foundations:** comparative advantage and specialization; Luis Garicano, “Hierarchies and the Organization of Knowledge in Production”, *Journal of Political Economy*, 2000.

**Established principle.** Efficient organization does not require identical capabilities. Division of labour exploits comparative advantage. Knowledge hierarchies can allocate common problems to lower-cost workers and difficult/rare problems to specialists.

**HLS translation.** Fast/cheap models and more capable/costly models can have different operational roles. Specialization and hierarchy can reduce the cost of possessing and using knowledge.

**Does not establish:** that a fixed student/teacher hierarchy is optimal when models can learn.

## 8. Workforce flexibility, cross-training and competence development — operations research

**Relevant foundations already audited:** Gutjahr et al. (2010); Gutjahr (2011); Hopp, Tekin and Van Oyen (2004); Borgonjon and Maenhout (2024); literature on assignment with learning-by-doing and knowledge transfer.

**Established principle.** Skills have acquisition costs but create future operational flexibility and value. Assignment can influence learning, and training changes future assignment possibilities.

**HLS translation.** Competence acquisition has a cost; use can change competence; current allocation can affect future capability; additional competence has value only if it changes future system performance.

**Does not establish:** the HLS problem, where learning models may transfer knowledge and a capable model may simultaneously provide service and teaching.

## 9. Response diversity and resilience — ecology

**Canonical source:** Thomas Elmqvist et al., “Response diversity, ecosystem change, and resilience”, *Frontiers in Ecology and the Environment*, 2003.

**Established principle.** Organisms contributing to similar functions but responding differently to environmental change can increase resilience.

**HLS translation.** Models with apparently overlapping competence can still have value if they respond differently when tasks or conditions change.

**Does not establish:** that redundancy or response diversity should always be increased.

## 10. Bet hedging — evolutionary biology

**Established principle.** Under environmental uncertainty, maintaining alternative phenotypes or strategies can improve long-term outcomes even when some alternatives are inferior in the current environment.

**HLS translation.** A competence that is not currently the most efficient can retain future value under uncertainty.

**Does not establish:** a direct equivalence between biological fitness and HLS utility.

## 11. Redundancy and design diversity — dependable systems

**Canonical foundations:** Brian Randell; Algirdas Avizienis and subsequent fault-tolerant computing literature.

**Established principle.** Redundancy can improve reliability, especially when redundant components do not share the same failure modes. Correlated failures reduce its value.

**HLS translation.** Multiple models with nominally similar competence may provide robustness when their weaknesses differ. Replicating identical failure behaviour provides little such benefit.

**Does not establish:** that redundancy is preferable to specialization; redundancy has costs.

## 12. Ensemble learning — Machine Learning

**Established principle.** Combining predictors can improve performance when individual predictive quality is accompanied by sufficiently complementary errors. Ensemble theory formalizes relationships among individual performance, error dependence and collective performance.

**HLS translation.** System value depends on both individual competence and relationships among models.

**Does not establish:** the broader HLS problem of task allocation, heterogeneous costs, selective learning and competence evolution.

## 13. No Free Lunch results — optimization

**Canonical source:** David H. Wolpert and William G. Macready, “No Free Lunch Theorems for Optimization”, *IEEE Transactions on Evolutionary Computation*, 1997.

**Established principle.** Over sufficiently broad classes of problems, no optimizer has universal superiority. Advantage requires assumptions or specialization to properties of the problem distribution.

**HLS translation.** There is no general reason to expect one model to dominate every relevant task distribution.

**Does not establish:** that heterogeneous portfolios are superior.

# Common structure

Across these domains, collective value repeatedly depends on:

1. **Repertoire** — capabilities appropriate to situations the system may face.
2. **Individual quality** — useful competence of each component.
3. **Complementarity** — contribution relative to what other components provide.
4. **Specialization and division of labour** — use of resources where they have comparative advantage.
5. **Redundancy** — overlapping capability when it provides capacity or robustness.
6. **Coordination** — ability to locate and exploit distributed competence.
7. **Future value** — present performance is insufficient when environment or competence can change.
8. **Competence acquisition** — new capability has a cost and a possible future return.
9. **Reconfiguration** — the useful organization of competence can change with the environment.
10. **Uncertainty** — capabilities that are not optimal today may preserve useful future options.

These are established ideas to support and constrain HLS theory, not proposed HLS novelties.

# Working synthesis for HLS

A compact representation is:

`problem repertoire <-> competence repertoire <-> organization of competences <-> use of competences <-> learning and competence evolution <-> future competence repertoire`.

For model `i`, competence `z`, and time `t`, distinguish the competence itself, `c_(iz,t)`, from its value to the system, `V_(iz,t)`.

That value may depend on future task demand, other available competences, operational cost and latency, capacity, complementarity, correlated failure, learning and maintenance costs, environmental change and acquisition delay.

Therefore:

> A competence should not be valued only by how much it improves an individual model. Its value depends on what it contributes to the competence organization of the whole system and on the environments in which that organization will operate.

This is a synthesis of established principles, not yet a claimed HLS theorem.

# Relation to current research

Competence Investment Value (CIV) is one possible mathematical tool for representing the cost and future operational value of acquiring or modifying competence. It is subordinate to the broader foundations.

Replication, rebalancing and specialization are possible competence transformations, not the organizing theory.

The research question at this level is:

> How should a system of learning models with different competences, costs and response times organize the use and development of those competences when the problems it faces can change?

The objective is not to rediscover portfolio diversification, specialization, resilience, exploration, cross-training or dynamic capabilities. It is to determine how established principles interact when the resources are learning models whose competences can themselves change.

# Research discipline

For every imported principle, record:

1. original established result;
2. assumptions;
3. mathematical formulation where available;
4. precise HLS translation;
5. what the result does not imply for HLS;
6. whether combining it with other principles produces an HLS-specific property, question or method.

Do not reject an idea merely because one component is already known. Established results are theoretical assets to be reused.
