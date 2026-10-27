# Heterogeneous Learning Systems

Heterogeneous Learning Systems (HLS) is a general research programme about systems whose members or components differ in what they can do, how well they do it, what it costs, what they know, and how their properties can change. HLS asks how those differences interact with the problem being solved and the arrangements through which work is performed.

## Why this programme exists

An inventory of individual strengths does not determine what a group can accomplish. Demand may not match available strengths; work may arrive over time; resources, deadlines and information may constrain assignment; coordination may consume resources; and experience or deliberate development may change future performance. The same individual capabilities can therefore yield different collective outcomes under different organizations and environments.

Studying individual performance remains necessary. It is insufficient for questions about access, allocation, coordination, joint work, learning and collective results. Conversely, a group-level result does not explain which individual properties or organizational mechanisms produced it. HLS studies these levels together while keeping their meanings distinct.

## What HLS is—and is not

HLS is a research programme, not a single algorithm, simulator, objective function, application, or fixed architecture. Its recurring scientific responsibilities are:

1. **Scenarios:** the problems, tasks, environments, demand and constraints.
2. **Organizations:** the entities and the arrangements governing roles, access and coordination.
3. **Models:** explicit assumptions and mathematical or computational representations of the phenomenon.
4. **Performance evaluation:** the outcomes, costs, estimands and comparisons used to assess a system.

These responsibilities need not be implemented as four software packages, and not every study needs to model every aspect. USE/DEVELOP, static allocation, routing, deliberation, cooperation and any particular agent technology are possible analytical choices, not defining conditions for HLS. A SOC, human team, industrial workforce, software-agent group, AI system or hybrid organization can be an application; none defines the general programme.

## Questions HLS seeks to explain

HLS investigates when capability distributions matter; when specialization helps, harms or has no material effect; how an organization realizes or fails to realize attainable outcomes; when routing, joint work or coordination is useful; how information and uncertainty change decisions; and how experience, learning or deliberate development affect future collective potential. Answers are conditional on the modeled task, organization, information, resources, time horizon and evaluation.

An improvement in one agent’s measured competence does not entail an improvement in collective performance. A larger attainable set does not entail that a feasible policy will realize its desirable outcomes. Better immediate performance may carry costs or reduce future options. Organizational overhead, development cost, latency and risk may matter alongside success rate. These are questions to test, not universal laws presumed by the programme.

## Central tensions

The research programme treats the following as context-dependent trade-offs:

- specialization and peak expertise versus flexibility and coverage;
- exploiting current competence versus developing future competence;
- local decisions versus collective objectives;
- centralized coordination versus distributed authority;
- immediate performance versus long-horizon value;
- adaptation to new evidence versus stability under noise;
- information value versus acquisition and decision cost;
- organizational complexity versus incremental performance;
- efficiency versus robustness to changing demand or failure.

No universal solution is asserted for these tensions. A study should identify which tension it operationalizes and which alternatives it compares.

## Individual and collective quantities

HLS distinguishes an agent’s **capability** (what outcomes are attainable under stated conditions) from **competence** (a modeled disposition or state relevant to performance on specified tasks). Neither is automatically an observed success rate. Individual performance is an outcome under a particular task, environment and action. Collective attainable capability concerns outcomes feasible to an organization under a declared policy class and constraints. Realized collective performance is what a particular policy actually produces. Costs and longer-term value may change the comparison. These distinctions are formalized in the ontology and theory.

## Scientific modesty and evidence

Motivating intuitions are not hypotheses; hypotheses are not results; simulations are not proofs; and a formal result in a finite model is not a general empirical law. HLS records assumptions, evidence type, uncertainty and limits alongside conclusions. Positive, negative, null and inconclusive findings all constrain what can responsibly be claimed. A successful implementation or a statistically detectable difference does not by itself establish a publishable contribution.

The current active branch contains exact, tested implementations of two finite mathematical constructions and a catalog validator. Other findings are documented from historical sources and are not thereby reproducible from this branch. The research record marks that distinction explicitly.

## Relation to established science

HLS draws on decision theory, operations research, scheduling, dynamic programming, learning and bandit methods, multi-agent coordination, organizational theory, queueing and value-of-information analysis. It does not claim these bodies of knowledge as new. Its scientific contribution, when established, must come from a precise question, a justified model or method, evidence and a comparison that shows what is learned beyond those antecedents.

## Further reading

The operational research standards are in [Research doctrine](RESEARCH_DOCTRINE.md). The entity and relation semantics are in [Ontology](ONTOLOGY.md); scoped mathematical results are in [Theory](THEORY.md); prior work is critically reviewed in [Literature](LITERATURE.md); completed work and its limits are in [Research record](RESEARCH.md); the chronology is in [History](HISTORY.md); and machine-readable component relationships are in [the catalog](../registry/catalog.json).
