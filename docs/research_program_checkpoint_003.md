# Research Programme Checkpoint 003

> **Historical checkpoint.** It preserves the programme state at the time. Its quoted RQ0 has been superseded; the current canonical wording is in [research_questions.md](research_questions.md).

Date: 2026-09-14  
Status: post-K0 conceptual consolidation; no claim of novelty, theorem, or validated experiment.

## Executive position

RQ0 remains the sole official repository research question:

> Can the deliberate evolution of competence allocation in a heterogeneous learning system improve its long-term performance compared with independently optimizing task allocation and knowledge transfer?

The programme has returned from the narrower H1/M0/M0.1 branch to the original population-level question. H1 remains useful but subordinate. The central object is now again the **distribution of competences across a heterogeneous portfolio**, not the error of one learner or the behaviour of one teacher-student pair.

The working principle is:

```text
individual failure != portfolio competence deficit
individual improvement != portfolio improvement
```

A learning action must therefore be valued conditionally on the state of the whole portfolio and on the operational consequences of the competence change.

## Chronological scientific correction

The route to the current state was:

```text
heterogeneous fast/slow intuition
    -> umbrella HLS / RQ0
    -> horizontal literature audit
    -> RouteNLP as direct operational precedent
    -> H1: failure signal versus intervention value
    -> M0
    -> M0.1
    -> recognition that H1 had become too central
    -> return to deliberate diversity / competence distribution
    -> adversarial expert
    -> candidate "homogenization trap"
    -> line A: useful complementarity vs competence transfer
    -> K0 vertical audit
    -> population-level correction
    -> P1/P2/P3/P4 scaffolding
```

See `research_origin_and_chronology.md` for the detailed chronology.

## K0 result

K0 audited the mechanism:

```text
knowledge transfer / distillation
    -> loss of diversity/complementarity
    -> loss of robustness/adaptability under shift
```

The component claims are not new in isolation. The audit found established work showing that online KD can homogenize peers, that diversity-preserving KD exists, that ensemble diversity can retain useful uncertainty information, that diversity can help concept-drift adaptation, and that KD can struggle under distribution shift. Continual-learning KD also provides an important counterexample to any one-sided claim that distillation is inherently destructive.

The surviving scientific question is not "is diversity good?" or "does KD homogenize?" It is how competence-changing actions reshape the **operational division of labour** of a heterogeneous portfolio and whether deliberate control of that evolution produces system value.

## Reassessment of budgeted learning

A limited learning budget is sufficient to create opportunity-cost effects, but `budgeted learning` alone is too close to mature resource-allocation, active-learning, machine-teaching, knapsack, and submodular-optimization formulations to carry the programme by itself.

This does **not** invalidate budgeted learning as a component. Known components may be reused. The goal is not novelty of every block but a novel and scientifically meaningful system, preferably with one or more novel non-trivial components.

## Current proposition structure

### P1 — Collective competence

A learner failure does not imply a portfolio deficit. A learner improvement can have zero marginal system value if another model already provides superior operational coverage of the same region.

**Role:** structural foundation.  
**Expected novelty in isolation:** low.  
**Importance to programme:** high.

### P2 — Local-collective misalignment

There can be learning actions `u_1`, `u_2` for which a local learning criterion prefers one action while downstream portfolio value prefers the other:

```text
J_local(u_1) > J_local(u_2)
V_portfolio(u_1) < V_portfolio(u_2)
```

Possible mechanisms include redundancy, coverage gaps, scarce learning budget, learnability, interference, specialization loss, useful redundancy, future demand, heterogeneous teachers, and future routing.

**Role:** demonstrate why portfolio-aware competence decisions are needed.  
**Potential:** high if supported by non-trivial mechanisms and strong comparison classes.

### P3 — Evolution can outperform frozen routing

The direct adversary is:

```text
frozen heterogeneous portfolio + strong adaptive router
```

P3 asks whether deliberate competence evolution can produce higher long-term operational value even when routing is already strong and all major task regions have reasonable initial coverage.

**Role:** establish that changing the competence landscape is sometimes necessary.  
**Potential:** very high; critical to RQ0.

### P4 — Coupling advantage

Candidate system-level proposition:

```text
V_coupled > V_strong-decoupled
```

where the decoupled system uses a strong router and a strong learning allocator/teacher/transfer mechanism with the same resources, but optimizes them independently.

**Role:** isolate the value of coupling routing and competence evolution.  
**Potential:** highest, if it survives strong baselines and realistic conditions.

P4 is not promoted to an official RQ or established hypothesis at this checkpoint.

## Novelty policy for system research

Do not discard a piece because it already exists. Routing, distillation, active learning, submodular allocation, continual learning, drift detection, diversity preservation, and related components may be adopted with proper attribution.

The target contribution can have the structure:

```text
known components
+ one or more novel pieces
+ novel coupling/objective
+ demonstrable system-level property
```

Conversely, "A+B+C has not appeared together" is not enough. The integration must solve a meaningful incompatibility, create an identifiable emergent property, or outperform strong systems built from the same pieces without the proposed coupling.

Candidate locations for original contributions include:

- portfolio competence representation;
- competence-gap analysis;
- portfolio-level intervention value;
- recipient/teacher selection;
- competence-redistribution policy;
- useful-complementarity or operational-option-value measures;
- controlled competence differentiation.

None is yet claimed novel.

## Experimental validity policy

**Mandatory rule:** a poor experiment neither proves nor refutes the hypothesis.

Experimental outcome and experimental validity must be recorded separately.

A negative result can count against a hypothesis only when:

- the benchmark actually instantiates the mechanism;
- the intervention has enough scope to change the relevant competence structure;
- model capacity does not trivially dominate the mechanism;
- strong baselines are correctly implemented and fairly tuned;
- the hypothesized benefit is measurable on the chosen horizon;
- the shift or future condition is not irrelevant to the competence being preserved or acquired.

A positive result can count in favour only when:

- baseline strength and tuning are comparable;
- shifts/tasks are not cherry-picked for the method;
- capacity, compute, data, and training budgets are matched;
- leakage and post-hoc benchmark construction are excluded;
- the claimed causal mechanism is distinguished from generic extra training or extra model capacity.

Every future experiment should include an explicit **validity audit** covering construct validity, causal identification, comparison validity, and external validity.

Synthetic and real experiments serve different purposes:

```text
synthetic -> causal isolation / controlled falsification
real      -> realism / practical relevance
```

Neither substitutes for the other.

## Literature position at this checkpoint

Important direct or adjacent precedents include:

- RouteNLP: routing failures -> targeted distillation -> rerouting.
- System-1.x: controlled fast/slow planning allocation.
- MixLLM and CONCUR: dynamic/continual routing over heterogeneous strategies.
- RouteLMT: marginal gain rather than absolute difficulty as a routing signal.
- OKDDip and multi-branch diversity-enhanced online KD: peer homogenization and diversity-preserving distillation.
- Ensemble Distribution Distillation: mean predictive quality need not preserve ensemble diversity information.
- SEED: selective expert training to retain expert heterogeneity in continual learning.
- concept-drift diversity frameworks: diversity can carry adaptation value under changing concepts.
- KD-under-shift work: in-distribution distillation gains do not imply distribution-shift robustness.
- active-learning/submodular and Machine Teaching work: budgeted teaching and heterogeneous learners are known components, not programme-level novelty by themselves.

These references constrain claims but do not close the combined HLS problem.

## Current stop/go logic

Do **not** kill the programme because an isolated component has precedent.

Substantial redirection becomes appropriate if a mature existing formulation already controls the same population-level state, makes the same routing and competence-evolution decisions under the same objective, and provides a strong accepted solution; or if strong decoupled systems systematically match the best coupled system under well-designed experiments across conditions where the hypothesized coupling should matter.

Likewise, a single failed synthetic experiment is not a kill criterion unless its construct and causal validity have first been established.

## Next scientific task

Construct the smallest coherent model in which P1, P2 and P3 are simultaneously relevant. Use known components where appropriate. The purpose is to expose the information that a strong decoupled system lacks, if any, and to determine whether P4 can hold under reasonable conditions.

Do not promote P4, design a large benchmark suite, or introduce a preferred mechanism such as Label Switching before this structural question is understood.
