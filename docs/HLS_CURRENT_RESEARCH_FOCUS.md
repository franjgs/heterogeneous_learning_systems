# HLS — CURRENT RESEARCH FOCUS

**Status:** ACTIVE OPERATING ANCHOR  
**Purpose:** Prevent research drift. Read this document before proposing the next experiment, implementation, theoretical extension, literature search, or dataset.

## 1. What we are doing NOW

We are designing and progressively validating a **configurable synthetic data/scenario generation framework for Heterogeneous Learning Systems (HLS)**.

Its purpose is to provide a controlled experimental testbed in which we can investigate the central hypothesis behind RQ0:

> Can the dynamic allocation and development of competences in a heterogeneous learning system improve long-term system performance compared with architectures that manage task allocation and knowledge transfer separately?

The framework must allow us to determine:

- **when** joint management can improve long-term system performance;
- **why** it can improve it;
- **when it does not** improve it;
- the **capabilities and limitations** of HLS;
- the **boundaries/equivalence regimes** in which separated management is sufficient;
- which properties of the system and environment make the integration of competence organization/use and competence development/evolution relevant.

The objective is **not to construct synthetic examples where HLS wins**. The objective is to construct a falsifiable family of worlds in which positive, null, boundary, negative, and reducible cases can emerge.

---

## 2. The scientific object

The programme is organized around two master beams.

### Beam 1 — organization/use of competences

How current problems/tasks are allocated to the available heterogeneous competences.

In compact form:

> **Who does what?**

Relevant structure may include specialization, complementarity, redundancy, dominance, costs, latency, capacity, escalation, and division of labour.

### Beam 2 — development/evolution of competences

How operational experience, learning, retention, forgetting, transfer, teaching, or other development mechanisms change future competences.

In compact form:

> **Who learns what, how, and from whom?**

### HLS integration

The research object is the interaction between these beams:

```text
organization/use of current competences
        ↕
development/evolution of future competences
```

The novelty or scientific usefulness is **not required to reside in every individual component**. Established theoretical mechanisms should be reused when appropriate, with explicit HLS ontology mappings. The scientific question concerns their integration in heterogeneous learning systems.

---

## 3. The synthetic framework is the current priority

The canonical experimental object is a family of worlds

\[
\mathcal E(\Theta),
\qquad
\Theta=(\Theta_Q,\Theta_C,\Theta_O,\Theta_D,
        \Theta_R,\Theta_K,\Theta_I),
\]

where the blocks control:

- `Theta_Q`: task/problem process;
- `Theta_C`: competence structure and initial geometry;
- `Theta_O`: experience/opportunity generation;
- `Theta_D`: competence-development dynamics;
- `Theta_R`: operational reward/performance;
- `Theta_K`: costs, capacities, and budgets;
- `Theta_I`: information and coordination available to policies.

The framework must keep **WORLD** and **POLICY** separate.

HLS, strong SEP, SEP-Omega, and oracle/reference policies must operate in the same generated world under explicitly declared information and coordination contracts.

The generator must progressively support controlled variation of the properties needed to test RQ0, rather than being tied to one favorable mechanism or one dataset.

---

## 4. Role of A1

**A1 is not the framework.**

A1 is the first minimal analytical validation/use of the framework.

A1a–A1c established that the framework can represent and distinguish, within the frozen L0 assumptions:

- no-learning regimes;
- learning without operational-development coupling;
- coupled but insufficient regimes;
- exact boundaries;
- strict HLS-vs-SEP advantage regions;
- reducibility/equivalence with sufficiently coordinated separated management (`HLS = SEP-Omega`);
- variation of coupling, development value, opportunity geometry, present operational sacrifice, and competence geometry.

Within A1/L0, the core exact condition is

\[
\delta_G > \delta_R,
\]

and under the frozen A1 parameterization,

\[
\rho(e_s-e_h)(D-N)>\delta_R.
\]

This is an **A1/L0 result**, not a universal HLS theorem.

**A1 status: CLOSED / PASS.**  
**RQ0 status: OPEN.**

Do not create further A1 sweeps merely to reconfirm the same L0 boundary unless a specific unresolved theoretical ambiguity requires them.

---

## 5. What we are NOT doing now

Unless explicitly required by the development of the synthetic framework, do **not** drift into:

- designing a new paper;
- searching for novelty for every mechanism;
- proving that every individual HLS component is new;
- looking for a real dataset prematurely;
- returning to PACS or Office-Home to repair them;
- constructing an experiment solely because it is the chronological “next experiment”;
- introducing complexity simply to make the synthetic world more realistic;
- trying to prove universal `HLS > SEP`;
- treating `SEP-Omega` as a weak baseline;
- redefining RQ0 around A1;
- treating the A1 opportunity kernel as the definition of the two-beam interface;
- adding mechanisms without explaining what capability or limitation of the framework they allow us to test.

PACS and Office-Home are historical vehicle screens. They do not define the current synthetic programme.

---

## 6. Immediate methodological objective

The current task is to **develop the synthetic framework into a sufficiently expressive, controllable, falsifiable experimental instrument** for studying RQ0.

For every proposed extension, ask first:

1. **What capability of HLS does this let us test?**
2. **What limitation or boundary can it expose?**
3. **Which beam or beam interaction does it manipulate?**
4. **Can it generate both favorable and unfavorable/null regimes?**
5. **Is the mechanism already theoretically established elsewhere and reusable through the HLS ontology?**
6. **Does it add genuinely new experimental capability beyond A1?**
7. **Can the same world be evaluated fairly under HLS, strong SEP, SEP-Omega, and an oracle/reference where feasible?**

If these questions do not have good answers, the extension should not be prioritized.

---

## 7. Required properties of the mature framework

The framework should progressively be capable of generating and controlling, when scientifically warranted:

### Competence structure
- homogeneous portfolios;
- redundancy;
- complementarity;
- specialists/generalists;
- dominated and non-dominated portfolios;
- different competence magnitudes and geometries.

### Task/environment structure
- controlled task mixtures;
- fixed and stochastic sequences;
- stationary and later non-stationary demand;
- task-dependent value/cost.

### Development structure
- no learning;
- learning by doing / task-specific learning;
- heterogeneous learning rates;
- diminishing returns and saturation;
- retention and forgetting;
- positive transfer;
- negative transfer/interference;
- capacity limitations;
- asymmetric development.

### Beam coupling
- decoupled organization and development;
- weak and strong coupling;
- action-dependent development opportunities;
- transferable/non-transferable opportunities;
- repeated feedback between current allocation, experience, competence evolution, and future allocation.

### Information/coordination
- joint HLS management;
- strong separated management;
- sufficiently coordinated separated management (`SEP-Omega`);
- partial/inexact information in later adversarial levels.

These are **capabilities of the generator**, not a checklist that must all be implemented immediately.

---

## 8. Experimental philosophy

The synthetic framework exists to produce **phase and boundary maps**, not a collection of favorable examples.

The desired scientific outputs are of the form:

```text
system/environment structure
        ->
HLS advantage / equality / disadvantage / reducibility
        ->
causal explanation and boundary conditions
```

Negative and equality regions are scientific results.

A synthetic positive result establishes existence/mechanism only inside the modeled family. It does not establish prevalence or practical superiority in real systems.

Realistic synthetic systems and real datasets come later, after the controlled framework identifies mechanisms and boundaries worth transferring.

---

## 9. Anti-drift rule

Before recommending “what comes next”, first identify whether the recommendation advances the **synthetic framework as an experimental instrument for RQ0**.

If it does not, stop and return to this document.

The default next question is therefore **not**:

> “What experiment comes after A1?”

It is:

> **“What capability does the synthetic framework still need in order to test a scientifically important capability, limitation, or boundary of HLS that A1 cannot test?”**

Only after answering that question should a new experimental protocol be designed.

---

## 10. Current checkpoint

```text
THEORETICAL FOUNDATIONS
    Two master beams established and mapped to external foundations
            |
            v
HLS SYNTHETIC ENVIRONMENT
    Configurable/falsifiable world-family contract established
            |
            v
A1 / L0
    First analytical use and validation of the framework
    A1a constructive/exact semantics
    A1b primitive phase boundaries
    A1c competence-geometry boundaries
            |
            v
    A1 CLOSED / PASS
            |
            v
CURRENT WORK
    Develop/audit the capabilities of the synthetic framework
    needed to investigate HLS capabilities, limitations, and
    validity regimes under RQ0
            |
            v
LATER
    controlled richer scenarios
    -> adversarial scenarios
    -> realistic synthetic systems
    -> real datasets
```

**RQ0 remains OPEN.**

---

## 11. One-sentence anchor

> **We are building a configurable and falsifiable synthetic HLS world generator whose purpose is to discover and test the conditions, capabilities, limitations, and equivalence boundaries of dynamically integrating competence allocation/use with competence development/evolution; A1 is only its first minimal validated regime.**
