# HLS Current State

This is the single canonical summary of the programme's present scientific
state. It records both established results and the current methodological
position of the HLS research programme.

Frozen protocols, detailed derivations, executable code, and result artifacts
remain authoritative for their own scope; this file does not replace them.

The programme-level philosophy is defined in [HLS_PHILOSOPHY.md](HLS_PHILOSOPHY.md),
and the common semantic contract is defined in [the HLS ontology](hls_ontology.md).

## 1. Programme-level scientific objective

The HLS programme studies how a collective of heterogeneous, limited, and
evolvable competences can be organized and developed over time to solve
changing problems effectively and efficiently under constraints.

At programme level, the central object is therefore not a particular routing
policy, learning rule, or comparison between two policy classes. It is the
interaction between:

- problems, requests, and changing demand;
- heterogeneous and individually limited workers;
- individual and collective competence;
- organization and allocation of work;
- operational constraints and resource limits;
- experience generated through work;
- learning, transfer, and competence development;
- specialization and other forms of competence evolution;
- system-level performance over time.

Two coupled questions motivate the programme:

> Who should do what?

and

> Who should learn what, how, and from whom?

The scientific objective is not to prove that heterogeneous, specialized,
jointly managed, or learning systems are universally superior. The objective
is to determine under which conditions particular forms of heterogeneity,
organization, learning, specialization, and joint adaptation have system-level
value, and under which conditions simpler organizations are sufficient or
preferable.

Accordingly, monolithic, homogeneous, heterogeneous, static, modular,
separated, adaptive, or jointly managed solutions are all admissible outcomes
of the investigation.

## 2. Current methodological position

The programme is returning to a more foundational level after an intensive
analysis of one specific organization/development question.

### Static theoretical foundation

T0--T3 are now consolidated in the canonical
[static HLS theoretical foundation](theory/HLS_STATIC_THEORY.md): feasible
capability (T0), static collective capability expansion (T1), organizational
sufficiency (T2), and organizational realization (T3). The static block is
provisionally closed at the level needed to continue the programme. Its next
theoretical boundary is T4 --- Dynamic Capability; no dynamic mechanism is
part of T0--T3.

The immediate foundational objective is to define a minimal but complete HLS
reference problem in which the essential programme-level concepts have explicit
operational semantics.

This reference problem must contain, at minimum:

- a stream or distribution of problems/requests;
- multiple workers or problem-solving units;
- heterogeneous and limited competences;
- a manager, organization, or allocation mechanism;
- explicit constraints and finite resources;
- operational outcomes;
- system-level performance measures;
- experience resulting from work;
- a mechanism by which experience or deliberate development can modify competence;
- repeated interaction over time.

The initial reference problem should be as small as possible while preserving
these semantics. Additional mechanisms such as changing demand, richer
specialization, knowledge transfer, interference, forgetting, communication,
hierarchy, referral, collaboration, or explicit development actions should be
introduced only when required to answer a previously stated HLS question.

The reference problem must be neutral with respect to architectural outcome.
It must not be constructed so that an HLS architecture wins by design.

Instead, it should permit different organizational regimes to be appropriate
under different conditions, including potentially:

- a monolithic or generalist solver;
- a homogeneous portfolio;
- a heterogeneous but static portfolio;
- an organized heterogeneous portfolio;
- an adaptive or learning portfolio;
- an organized and evolving HLS.

The intended scientific product is therefore a characterization of regimes:

```text
problem conditions
+ resource constraints
+ competence structure
+ organization
+ learning/development dynamics
+ demand dynamics
        |
        v
appropriate organizational/development regime
```

rather than a universal inequality asserting the superiority of one architecture.

## 3. Theoretical foundations for the reference problem

The reference problem should not be invented from scratch.

Its initial construction is based on four existing foundations.

### 3.1 Organization and use of limited competence

The Garicano line provides a primary theoretical reference for the operational
side of the system: heterogeneous problems, limited knowledge, specialization,
problem assignment, referral/escalation, organizational structure, capacity,
and the system-level consequences of organizing distributed knowledge.

Only constructs that survive explicit mapping to the HLS ontology should be imported.

### 3.2 Development and evolution of competence

The Gutjahr line provides a primary theoretical reference for competence
development and the allocation of development/training resources.

Again, HLS does not inherit the complete model automatically. The relevant
objects and results must be mapped explicitly to the HLS ontology and adapted
where the HLS problem requires properties absent from the source theory.

### 3.3 HLS ontology and philosophy

[HLS_PHILOSOPHY.md](HLS_PHILOSOPHY.md) defines the programme-level scientific direction.

[hls_ontology.md](hls_ontology.md) defines the semantic contract used to
distinguish, among other concepts:

- competence from performance;
- experience from competence change;
- individual competence from collective competence;
- work allocation from development allocation;
- organization from learning;
- operational outcome from long-term system value.

These distinctions must be preserved in the reference problem.

### 3.4 Existing HLS routing/development theory

The existing RQ0 work provides a developed theory for one specific interaction:
when operational routing influences future learning/development opportunities,
and when managing routing and development separately can or cannot reproduce
the value of joint decision making.

This theory is retained as an HLS theoretical asset. It does not define HLS as
a whole and must not dictate the construction of the general reference problem.

## 4. Performance and constraints are an open foundational requirement

The programme does not yet have a sufficiently complete operational definition
of HLS system performance for the new reference problem.

This is now an explicit foundational gap.

A useful HLS evaluation must distinguish at least:

```text
competence / capability
        !=
realized operational performance
        !=
resources consumed to obtain that performance.
```

Potential performance dimensions include, depending on the reference problem:

- quality or success of problem resolution;
- coverage of the problem/request distribution;
- throughput or served demand;
- latency or resolution time;
- unresolved or failed problems;
- computational or other resource consumption;
- capacity utilization;
- learning/development cost;
- robustness;
- adaptation to changing demand;
- long-term accumulated system value.

These are not yet declared to be the definitive HLS metrics.

The reference problem must determine which quantities are scientifically
necessary and how they should be combined or kept separate.

In particular, comparisons between architectures must be made under explicit
and scientifically fair resource constraints. A heterogeneous portfolio must
not obtain an apparent advantage merely because it receives more effective
resources than the architecture against which it is compared.

A scalar long-term objective `J` may subsequently be defined for particular
questions, but the programme should not prematurely collapse all system
performance into a single quantity before the relevant performance dimensions
and constraints are understood.

## 5. RQ0 and its current role

RQ0 remains an active research question:

> Can the dynamic allocation and development of competences in a heterogeneous
> learning system improve long-term system performance compared with
> architectures that manage task allocation and knowledge transfer separately?

At programme level, RQ0 asks when the interaction between the organization/use
of current competences and the development/evolution of future competences has
system-level value, and when the two can instead be managed separately or
through sufficient coordination.

The work completed so far studies a narrower routing/development instantiation
of this question.

RQ0 is therefore an important subproblem of HLS, but the HLS programme must not
be reduced to proving `J_HLS > J_SEP`.

Nor should the existing strong-SEP comparison be treated as a universal
definition of the value of HLS.

The current exact theory instead establishes conditions and counterconditions
for one particular form of organization/development coupling.

## 6. What is established for the current RQ0 formalization

### 6.1 Programme and policy classes

Under common world physics and information, strong SEP is a restricted policy
class of HLS policies. Therefore

```text
Pi_SEP subseteq Pi_HLS
J_SEP,max <= J_HLS.
```

This inequality alone is not a substantive HLS result; it follows from policy
class inclusion.

In the finite exact setting, strict value relative to strong SEP occurs iff no
HLS-optimal policy is strong-SEP-admissible on its positive-probability support.

A local non-greedy Bellman action alone is insufficient.

The local identity

```text
Q(b)-Q(g) = -DeltaR + DeltaP D*
```

is exact under its stated one-step factorization, but is a local Bellman
advantage identity and not a global integration criterion.

The formal source is
[RQ0 routing integration boundaries](theory/rq0_routing_integration_boundaries.md).

### 6.2 Existing synthetic framework

The existing synthetic G0 framework was constructed to investigate the current
RQ0 routing/development formalization.

It should therefore be interpreted as the existing **RQ0 synthetic framework**,
not as the final minimal reference model of the complete HLS programme.

Within its intended scope:

- G0 passed its architecture and A1 compatibility gates.
- A1 is closed/pass: A1a exact worlds, A1b 1,020 preregistered boundary
  configurations, and A1c 458 competence-geometry configurations.
- C1--C5 are implemented and passed their reference gates on the common,
  policy-neutral G0 framework.
- C6--C8 are not implemented.
- The framework remains a valid instrument for testing RQ0 mechanisms and boundaries.
- It is not itself evidence that HLS architectures are generally superior.

The current framework contract is in [G0](experiments/G0.md); the exact A1
reference specification and compatibility record remain in the frozen
[synthetic environment record](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md).

The existing G0 must not be retrospectively redefined to serve the new
programme-level reference problem. Scientific provenance and frozen results
must be preserved.

## 7. Exact and synthetic RQ0 results

- A1 World E and C1 R5 are constructive, exact existence cases relative to
  strong SEP. They do not establish prevalence or superiority over SEP-Omega.
- The original eta=.5 diagnostic found physically reachable local routing
  inversions that were off every HLS-optimal root continuation. Constrained
  reachability and demand-persistence audits therefore established a local
  mechanism without a global root-value result in that family.
- The frozen routing-to-opportunity lambda family was SEP-reducible at all 21
  points. Persistence strengthened local incentives in its tested worlds but
  did not remove the observed global barrier.
- The frozen zero-sum competence redistribution family

  ```text
  C(alpha)=((4/5,4/5-alpha/5),(3/5,3/5+alpha/5))
  ```

  gives the exact model-scoped result

  ```text
  Phi(alpha) = 0                         for 0 <= alpha <= 5/16
               3 alpha/10 - 3/32         for 5/16 < alpha < 1/2
               0                         for 1/2 <= alpha <= 1.
  ```

  Thus it establishes existence of strict integration relative to strong SEP
  on the open interval `5/16 < alpha < 1/2`.

- `alpha=5/16` is a Bellman inversion boundary.
- `alpha=1/2` is a greedy-admissibility boundary: the required action enters
  the SEP greedy set.
- These boundaries are properties of this family, not universal HLS boundaries.
- SEP-Omega equals HLS in the audited A1, A1b, A1c, lambda, and geometry
  families within the declared tolerance.

This establishes that sufficient continuation information can remove the value
gap in the tested worlds. SEP-Omega is therefore a coordination/reducibility
boundary for this formalization, not an independent algorithmic benchmark and
not evidence against the broader HLS programme.

## 8. What is not established

The repository does not establish:

- universal superiority of heterogeneous systems over monolithic systems;
- universal superiority of specialization over generalism;
- universal superiority of adaptive organization over static organization;
- universal superiority of joint organization/development over separated architectures;
- prevalence, genericity, robustness, or empirical realism of the current
  synthetic integration window;
- that complementarity, specialization, persistence, or stronger coupling is
  sufficient for strict integration;
- that the C(alpha) interval transfers to all G0+C1--C5 worlds or to real systems;
- that HLS intrinsically outperforms every sufficiently coordinated modular architecture;
- that the existing RQ0 synthetic environment constitutes a complete HLS reference problem.

The PACS and Office-Home records are scoped vehicle and mechanism evidence,
with negative/inconclusive outcomes where stated. They are not general
validation of HLS or RQ0.

## 9. Current structural understanding of RQ0

Within the current finite exact routing/development formalization, the analysis
distinguishes three levels:

1. **physical/local non-separability**: a state admits a Bellman-optimal
   non-greedy action;
2. **on-policy non-separability**: an HLS-optimal policy uses such an action on
   its own positive-probability support;
3. **irreducible integration relative to strong SEP**: every HLS-optimal policy
   requires such a violation of the strong-SEP restriction.

Only the third level implies `J_HLS > J_SEP,max` in the finite exact setting.

SEP-Omega demonstrates that the positive result is about the strong-SEP
contract, especially its routing objective and continuation information, not
about centralization versus modular software as such.

These distinctions remain valid theoretical results for their declared scope.
They are not definitions of HLS itself and need not constitute the appropriate
formalism for other HLS organization/development mechanisms.

## 10. Current foundational gaps

Before extending the experimental programme, the following programme-level
objects require explicit definition or consolidation.

### 10.1 Minimal HLS reference problem

A minimal but complete problem must be specified without embedding the desired
answer in its physics.

### 10.2 Workers

The minimum state and limitations of a worker must be defined, including how
competence relates to its ability to solve different problem types.

### 10.3 Problems and demand

The semantics of a problem/request and its distribution must be explicit.

The minimal world may initially use stationary demand. Changing demand should
be introduced when the corresponding HLS question requires it.

### 10.4 Manager and organization

The authority, information, actions, and limitations of the organizing
mechanism must be explicit.

Organization must not be identified automatically with routing.

### 10.5 Constraints

Finite resources and other relevant limits must make organizational decisions
meaningful and comparisons fair.

### 10.6 Performance

Operational and long-term system performance measures must be defined before
claims of architectural superiority can be made.

### 10.7 Experience and competence evolution

The reference problem must distinguish work from experience and experience
from actual competence change.

A minimal competence-evolution mechanism is required, but richer mechanisms
should not be added without a scientific reason.

### 10.8 Collective competence and complementarity

The programme requires operational definitions that allow collective
competence and useful complementarity to be measured without assuming that
heterogeneity or diversity is intrinsically beneficial.

## 11. Methodological reset: from RQ0-specific worlds to an HLS reference system

The programme will not proceed by progressively enriching the existing RQ0
synthetic world merely to obtain broader positive HLS results.

The next foundational objective is to construct a minimal, neutral, and
scientifically controlled HLS reference problem.

The construction should proceed from established theoretical components where
they genuinely match the HLS ontology, particularly the organization/use and
development/evolution foundations, and should introduce new HLS-specific
machinery only where those foundations leave a demonstrated gap.

The methodological sequence is:

```text
HLS philosophy
      |
      v
ontology
      |
      v
existing theoretical foundations
      |
      v
identify missing HLS primitives
      |
      v
minimal HLS reference problem
      |
      v
constraints + performance measures
      |
      v
theoretical analysis
      |
      v
controlled experimental validation
      |
      v
release one additional property when scientifically required
```

Each new property or mechanism must answer a previously formulated scientific
question.

Realism by itself is not a reason to enlarge the model.

Likewise, a mechanism must not be introduced merely because it makes a
positive HLS result easier to obtain.

Positive, negative, and equality regimes are all scientifically admissible.

## 12. Intended theoretical programme

The longer-term objective is to characterize relationships of the form

```text
problem structure
x demand structure
x individual limitations
x competence geometry
x resource constraints
x organizational possibilities
x learning/development dynamics
            |
            v
system performance and appropriate organizational regime.
```

This may reveal regimes in which:

- a monolithic/generalist solution is sufficient;
- homogeneous replication is appropriate;
- static heterogeneity is useful;
- dynamic organization adds value;
- specialization emerges or is deliberately useful;
- competence development adds value;
- organization and development can be separated without loss;
- organization and development require coordination;
- genuinely joint adaptation has strict value.

The purpose is to characterize these regimes and their boundaries, not to
assume their ordering in advance.

The existing RQ0 theory becomes one component of this broader programme:
it characterizes one possible boundary between separated and jointly managed
organization/development.

## 13. Immediate next scientific task

The next task is **not** another parameter sweep or an extension of the
existing RQ0 synthetic campaign.

It is the scientific specification of the minimal HLS reference problem.

Before implementation, that specification should determine:

1. which primitives can be imported from the Garicano organizational model;
2. which primitives can be imported from the Gutjahr competence-development model;
3. how those primitives map to the HLS ontology;
4. which HLS primitives remain missing after that mapping;
5. the minimum worker model;
6. the minimum problem/request model;
7. the minimum manager/organization model;
8. the minimum constraints required to make organization meaningful;
9. the minimum experience and competence-evolution dynamics;
10. the performance quantities required for fair comparison;
11. the negative/control regimes in which complex HLS organization should
    provide no advantage;
12. the first non-trivial theoretical questions that the resulting reference
    problem can answer.

Only after this specification is stable should the new reference environment
be implemented.

## 14. Current research position

The HLS programme is in **foundational consolidation and reference-problem design**.

The previous RQ0 phase has established a useful exact result:

```text
strict integration relative to strong SEP:
EXISTS in the declared exact model.
```

For that formalization:

```text
existence:                   YES
structural characterization: PARTIAL / IN PROGRESS
robustness/prevalence:       NOT ESTABLISHED
empirical relevance:         NOT ESTABLISHED
```

Those results are retained.

However, the immediate programme-level priority is now broader: establish a
minimal HLS reference problem with explicit organization, limitations,
constraints, performance, experience, learning, and competence evolution,
grounded in existing theory and the HLS ontology.

This is not a rejection of RQ0 or of the existing synthetic work. It is a
change in scientific hierarchy:

```text
HLS programme
    |
    +-- minimal HLS reference problem
    |       |
    |       +-- organization/use of competence
    |       +-- development/evolution of competence
    |       +-- performance under constraints
    |       +-- interaction between organization and development
    |
    +-- RQ0 and its specific formalizations
            |
            +-- current routing/development model
            +-- strong SEP
            +-- SEP-Omega
            +-- exact integration results
```

The reference problem should ultimately provide the common laboratory in which
RQ0 and other HLS questions can be investigated without allowing any one of
them to define HLS itself.

## 15. Evidence pointers

### Programme level

- Philosophy: [HLS_PHILOSOPHY.md](HLS_PHILOSOPHY.md)
- Semantics: [hls_ontology.md](hls_ontology.md)
- Research questions: [research_questions.md](research_questions.md)
- Method: [RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md)

### Current RQ0 theory and evidence

- Formal theory:
  [rq0_routing_integration_boundaries.md](theory/rq0_routing_integration_boundaries.md)
- Existing RQ0 synthetic contract:
  [G0.md](experiments/G0.md)
- A1/C1--C5 gates:
  [HLS_SYNTHETIC_ENVIRONMENT.md](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md)
- Campaign chronology:
  [RQ0_EXPERIMENTAL_CAMPAIGN.md](experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md)
- Geometry protocol/outcome:
  [RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md](experimental_foundations/RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md)
- Coupling protocol/outcome:
  [RQ0_ROUTING_OPPORTUNITY_COUPLING_PROTOCOL.md](experimental_foundations/RQ0_ROUTING_OPPORTUNITY_COUPLING_PROTOCOL.md)
- Executable synthetic gates:
  [experiments/synthetic](../experiments/synthetic/)
