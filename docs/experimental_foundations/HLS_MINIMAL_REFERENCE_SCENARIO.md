# HLS Minimal Reference Scenario

**Status:** Canonical reference-scenario specification; documentation only\
**Scope:** Minimal adaptive HLS scenario for later implementation on G0\
**Authorities:** `HLS_CURRENT_STATE.md`, `HLS_DYNAMIC_THEORY.md`,
`experiments/G0.md`, and `RESEARCH_DOCTRINE.md`

## 1. Purpose and boundary

This document specifies the minimum adaptive reference scenario that remains
after the Phase-II mathematical and adversarial audit.  It is a small,
implementable scenario for testing the distinction between present competence
use and future collective capability.  It is not a redefinition of G0, a new
dynamic-programming theorem, a new HLS mechanism, or an implementation.

G0 remains the policy-neutral generator of worlds.  The scenario below is one
future G0 instantiation: its world physics must be common to every compared
policy (`WORLD != POLICY`).

The scenario uses two workers, two task/competence types, and two periods:

```text
2 workers × 2 task/competence types × 2 periods.
```

It preserves five required features:

- heterogeneous current competence;
- changing demand;
- limited distributed capacity;
- learning by doing; and
- development value that depends on the recipient of an experience
  opportunity.

It is a reference scenario, not a claim that these are the universal or only
relevant HLS ingredients.

## 2. Common world and minimal decisions

Let the workers be `w1,w2`, task/competence types be `A,B`, and periods be
`t=0,1`.  The competence state is a two-by-two state `S_t`; it is heterogeneous
at `t=0`.  `P_0` and `P_1` are demand conditions, with `P_1 != P_0` in the
adaptive configurations.  Capacity is limited, so the location of competence
in the collective affects what can be served under the admissible future
organization `Pi` and constraints `B`.

At `t=0`, compare only two relevant allocations of the same operational
opportunity:

- `E`: present exploitation, the assignment with the higher current return;
- `D`: developmental/anticipatory allocation, which assigns the opportunity
  to the worker for whom its future collective contribution is higher.

An admissible organizational policy selects between these actions; no manager
architecture, information structure beyond the stated comparison, or solution
method is prescribed.

They are realized organization/use actions in the sense of T3, not a separate
training action.  Work supplies the learning-relevant experience; the
state transition determines whether that experience changes competence.
For the displayed comparison, labels are chosen so that `E` assigns the `B`
opportunity to `w2`, while `D` assigns it to `w1`.

Write the operational loss from choosing `D` rather than `E` as

$$
L = R_0(E)-R_0(D)>0.
$$

For an opportunity of type `B`, let `Delta_B(w)` be the increment in future
value, under common future operating conditions, from assigning that
opportunity to worker `w` rather than to the corresponding no-opportunity
counterfactual.  The required recipient difference is

$$
G = \Delta_B(w_1)-\Delta_B(w_2)>0,
$$

where labels are chosen so that `w1` is the higher-development-value
recipient.  `G` is a difference in future value, not a claim that all workers
have different learning rates.

For the two-period objective, with `beta` denoting the stated weight on the
future value,

$$
J(D)-J(E)=-L+\beta G.
$$

This is the standard two-stage continuation-value decomposition already used
by T6.  It is the scenario's analytical ground truth, not new HLS mathematics.
Its regimes are:

| Regime | Interpretation |
| --- | --- |
| `beta G < L` | Present exploitation remains optimal. |
| `beta G = L` | Boundary: `E` and `D` are intertemporally indifferent. |
| `beta G > L` | Anticipatory developmental allocation changes the present decision. |

The future value is evaluated under common future conditions and a T0-compatible
criterion.  Thus the scenario retains the T4-to-T5 consistency condition:
equal future collective capability implies equal future value under those
conditions.  It does not alter T5.

## 3. One scenario, four configurations

`S0`--`S3` are controls/ablations of the same world template, not separate
models or a progression of HLS definitions.

| Configuration | World setting | Required conclusion |
| --- | --- | --- |
| **S0 — static organization** | Demand does not change (`P_1=P_0`) and competence development is inactive (`S_1=S_0` with respect to the period-0 allocation). | Static organization/use is the only relevant comparison. |
| **S1 — adaptive organization** | Demand changes (`P_1 != P_0`), but competences remain fixed with respect to the allocation (`S_1=S_0`). | The organization may adapt to demand, but no allocation-induced future capability is present. |
| **S2 — adaptive development, decision-equivalent** | Demand changes and the recipient produces differential endogenous development with `G>0`, but `0 < beta G < L`. | Future development has value, yet `E` remains the uniquely best present allocation. |
| **S3 — decision-relevant adaptive HLS** | The same adaptive-development structure holds and `beta G>L`. | Future development value changes the best present organization from `E` to `D`. |

The equality `beta G=L` is a boundary control between S2 and S3, not a fifth
scenario.  In every configuration, any comparison must keep the world,
information, admissible policy class, and operational constraints explicit and
common.

## 4. Relation to the HLS Relevance Cascade

The scenario instantiates, but does not extend, the structural HLS screen:

```text
a_t -> S_{t+1} -> C_Pi(S_{t+1}, P_{t+1}, B_{t+1}) -> V_{t+1}
     -> optimal present choice
       F1             F2                         F3          F4
```

S0/S1 block allocation-induced state divergence for the relevant comparison;
S2 reaches future value relevance but not decision relevance; S3 reaches
decision relevance.  As in the dynamic foundation,

$$
F4 \Rightarrow F3 \Rightarrow F2 \Rightarrow F1,
$$

and the converses do not generally hold.  In particular, reaching F1, F2, or
F3 is not sufficient for F4.  The cascade is a structural diagnostic for this
scenario, not a theorem of dynamic programming and not evidence that a
particular HLS policy is superior.

## 5. Negative audit and surviving condition

The first proposed construction used linear, homogeneous learning by doing.
It fails to create the intended future advantage: the specialist who receives
task `B` under the exploitative allocation also learns `B`.  Changing demand
and allowing learning by doing therefore do not by themselves create the
required recipient difference in future value.  This is a rejected
construction under those assumptions, not a general result about learning by
doing.

The minimum condition that survived is:

> **The developmental value of an experience opportunity depends on who
> receives it.**

Diminishing returns, skill ceilings, and heterogeneous learning aptitude are
possible realizations of that condition.  They are not general HLS assumptions.
A first later implementation may use a common diminishing-returns learning law
as one transparent realization, but the reference scenario neither requires
that law nor commits HLS to it.

## 6. Why this is minimal

The retained dimensions each serve a distinct semantic role:

| Retained item | Why it is required here |
| --- | --- |
| 2 workers | Makes the location and distribution of collective competence meaningful. |
| 2 task/competence types | Permits specialization and a change in what the system needs. |
| 2 periods | Is the smallest horizon that links a present action to future capability. |
| Limited capacity | Prevents competence location from being operationally irrelevant. |
| Changing demand | Defines the adaptive problem, although it is not a mathematical prerequisite of T4--T6. |
| Learning by doing | Makes operational work simultaneously an experience and development opportunity. |

The following are deliberately unnecessary at this stage: a separate training
action, training budget, explicit training cost, stochasticity, transfer,
forgetting, heterogeneous learning rates, and more workers, tasks, or periods.
They must not be added unless they are needed to answer a stated question or
to break a documented reduction.

## 7. Literature role and non-claims

The scenario uses only retained, verified sources for its contextual
foundations.  `nembhardbentefouet2015` supports the relevance of selection,
grouping, assignment, learning by doing, and knowledge transfer in a dynamic
assignment setting.  `baccaraleeyariv2023` supports the relevance of dynamic
task allocation when experience changes later expertise.  Neither source is
claimed to prove the HLS inequality above, and neither is imported as a
universal HLS model.

This documentation does not claim:

- a new theorem of dynamic programming or a novel mathematical inequality;
- exclusive HLS ownership of the scenario or of its solution methods;
- superiority of any HLS policy, organization, or joint controller;
- irreducible joint management; or
- empirical realism, prevalence, robustness, or generality beyond the stated
  scenario.

Exact dynamic programming, assignment, optimization, and other established
methods are desirable comparators for a future implementation.  The scenario
only establishes a controlled, implementable reference and its null, boundary,
and decision-relevant regimes.  It does not initiate implementation or decide
which policy class will prevail.
