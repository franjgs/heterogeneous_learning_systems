# HLS Static Theoretical Foundation --- T0--T3

**Status:** Consolidated working foundation
**Scope:** Static Heterogeneous Learning Systems (HLS)\
**Boundary:** Time, state transitions, experience accumulation, learning
and competence evolution are deliberately excluded until T4.

## 1. Purpose and methodological status

This document consolidates the minimum static theoretical structure
required by the HLS programme before introducing dynamics.

It follows the programme research doctrine:

-   the HLS scientific problem determines the formalism;
-   the ontology is a translation and consistency layer, not a closed
    theory;
-   established theory should be imported when it solves a required
    subproblem;
-   reductions, sufficiency and negative results are legitimate
    outcomes;
-   no current mechanism or toy formalism should silently become the
    definition of HLS.

The static block is:

\[ T0 `\rightarrow `{=tex}T1 `\rightarrow `{=tex}T2
`\rightarrow `{=tex}T3 \]

with:

-   **T0 --- Feasible Capability**
-   **T1 --- Static Collective Capability Expansion**
-   **T2 --- Organizational Sufficiency**
-   **T3 --- Organizational Realization**

T0--T3 answer complementary questions:

1.  What can the system achieve?
2.  Does a richer collective/organizational structure add capability?
3.  When is that richer structure unnecessary?
4.  How does an admissible organization actually use distributed
    competence to realize outcomes?

The next block, beginning at T4, introduces dynamics.

------------------------------------------------------------------------

# 2. Core static objects

Let an HLS contain (M) heterogeneous units/agents.

## 2.1 Competence state

\[ S=(S_1,`\ldots`{=tex},S_M). \]

(S_m) describes the competence/capability state of unit (m).

Competence is not identified with observed performance.

## 2.2 Problem space and demand

Let (Q) be the problem/task space and

\[ q`\sim `{=tex}P \]

the operational demand distribution.

\(Q\) describes what problems may exist; (P) describes which problems
matter operationally and with what frequency or importance.

## 2.3 Operational constraints

\[ B \]

collects relevant external/operational constraints, such as compute,
energy, time, capacity, communication, monetary budgets, deadlines or
other real restrictions.

The representation of (B) is model-dependent and should remain minimal.

## 2.4 Organizational class and policy

\[ `\Pi`{=tex} \]

is a class of admissible organizational policies.

A particular policy is

\[ `\pi`{=tex}`\in`{=tex}`\Pi`{=tex}. \]

Organization is deliberately broader than routing. Depending on the
model, it may encode assignment, delegation, sequencing, collaboration,
escalation, redundancy, hierarchy or other admissible mechanisms for
using distributed competence.

## 2.5 Outcomes

A policy produces an outcome

\[ z^`\pi`{=tex}=(y^`\pi`{=tex},r\^`\pi`{=tex}), \]

where:

-   \(y\) contains desirable effectiveness quantities;
-   \(r\) contains resource use, cost or other undesirable quantities.

Orientation:

\[ `\text{larger }`{=tex}y`\text{ is better}`{=tex},`\qquad`{=tex}
`\text{smaller }`{=tex}r`\text{ is better}`{=tex}. \]

No scalar utility is assumed at the foundational level.

------------------------------------------------------------------------

# 3. T0 --- Feasible Capability

For fixed ((S,P,B,`\Pi`{=tex})), let
(`\Pi`{=tex}\_B`\subseteq`{=tex}`\Pi`{=tex}) denote the policies
admissible under the relevant constraints.

The feasible outcome set is

\[ `\boxed{
\mathcal F_\Pi(S,P,B)
=
\{z^\pi(S,P):\pi\in\Pi_B\}.
}`{=tex} \]

## 3.1 Pareto dominance

For

\[ z=(y,r),`\qquad `{=tex}z'=(y',r'), \]

define weak Pareto dominance by

\[ z`\succeq `{=tex}z' \]

iff, componentwise,

\[ y`\ge `{=tex}y',`\qquad `{=tex}r`\le `{=tex}r'. \]

Strict dominance additionally requires at least one strict inequality.

The non-dominated capability frontier is

\[ `\boxed{
\mathcal C_\Pi(S,P,B)
=
ND[\mathcal F_\Pi(S,P,B)].
}`{=tex} \]

The dominance closure of a set (`\mathcal `{=tex}F) is

\[ `\boxed{
D(\mathcal F)
=
\{z:\exists z'\in\mathcal F,\ z'\succeq z\}.
}`{=tex} \]

## 3.2 Interpretation

T0 separates:

\[ `\text{competence}`{=tex} `\neq`{=tex}
`\text{feasible collective outcomes}`{=tex} `\neq`{=tex}
`\text{realized performance}`{=tex} `\neq`{=tex}
`\text{utility/value}`{=tex}. \]

It answers:

> Given available competence, operational demand, constraints and
> admissible organization, what can the system achieve?

## 3.3 Fair comparison principle

Alternative organizations are compared under the same external demand
(P) and external constraints (B).

Their realized resource consumption (r) need not be equal; differences
in efficiency belong to the outcome comparison.

Historical costs of acquiring/developing the fixed competence state (S)
are not mixed into the static operational comparison.
Competence-development costs belong to later theory.

------------------------------------------------------------------------

# 4. Reproducibility closure

When comparing organizational classes, the benchmark must contain all
outcomes reproducible through the operations admissible to that class,
not merely its pure deterministic outcomes.

Write

\[ `\overline{\mathcal F}`{=tex}\_`\Pi`{=tex} \]

for this reproducible outcome set.

In a static linear model in which admissible randomization/time-sharing
produces linear mixtures of outcomes,

\[ `\overline{\mathcal F}`{=tex}*`\Pi`{=tex} =
`\operatorname{conv}`{=tex}(`\mathcal `{=tex}F*`\Pi`{=tex}\^{`\mathrm{pure}`{=tex}}).
\]

This convexification is **not** a universal HLS axiom. It depends on the
semantics of outcomes, mixing and constraints (B). The fundamental
notion is admissible reproducibility.

------------------------------------------------------------------------

# 5. T1 --- Static Collective Capability Expansion

Let

\[ `\Pi`{=tex}\_0`\subseteq`{=tex}`\Pi`{=tex}\_1 \]

be a benchmark organizational class and a richer class.

There is strict static capability expansion when

\[ `\boxed{
\overline{\mathcal F}_{\Pi_1}
\not\subseteq
D(\overline{\mathcal F}_{\Pi_0}).
}`{=tex} \]

Equivalently,

\[ `\boxed{
\exists z_1\in\overline{\mathcal F}_{\Pi_1}
:
\nexists z_0\in\overline{\mathcal F}_{\Pi_0}
\text{ such that }z_0\succeq z_1.
}`{=tex} \]

Thus a richer organization adds capability only if it produces an
outcome that cannot be reproduced or dominated by the complete
admissible benchmark.

T1 is currently a **static reduction/baseline**, not a claimed central
novelty of HLS.

In static additive separable cases, much of T1 can reduce to established
multiobjective assignment/resource-allocation theory. Such a reduction
is useful: effects fully explained by that theory should not be
attributed to an HLS-specific mechanism.

------------------------------------------------------------------------

# 6. T2 --- Organizational Sufficiency

For

\[ `\Pi`{=tex}\_0`\subseteq`{=tex}`\Pi`{=tex}\_1, \]

the simpler class (`\Pi`{=tex}\_0) is sufficient relative to
(`\Pi`{=tex}\_1) under ((S,P,B)) when

\[ `\boxed{
\overline{\mathcal F}_{\Pi_1}(S,P,B)
\subseteq
D(\overline{\mathcal F}_{\Pi_0}(S,P,B)).
}`{=tex} \]

Interpretation:

> Every outcome obtainable with the richer organization can be
> reproduced or dominated by the simpler organization.

T2 does not require equality of feasible sets. The richer class may
generate additional outcomes that add no efficient capability.

T2 is the complementary static notion to T1 and provides a
reducibility/sufficiency baseline. No exhaustive characterization of all
sufficiency conditions is required before moving to the dynamic block.

------------------------------------------------------------------------

# 7. T3 --- Organizational Realization

## 7.1 Why T3 is needed

T0 deliberately treats (`\Pi`{=tex}) as a high-level primitive. T3 opens
that box only as far as necessary.

Available competence does not imply that every possible use or
combination of that competence is organizationally accessible.

The static structure therefore distinguishes:

\[ `\boxed{
\text{available competence}
\neq
\text{admissible competence use}
\neq
\text{outcome capability}.
}`{=tex} \]

## 7.2 Policy versus realized organizational action

A separate generic variable (u) for "competence-use configuration" is
**not required**.

Statically, any (u) that merely records what policy (`\pi`{=tex}) does
can be absorbed into the definition of (`\pi`{=tex}). Introducing it as
a new HLS primitive would therefore duplicate structure.

However, one distinction is necessary and should be retained:

\[ `\boxed{\pi \neq a.}`{=tex} \]

Here:

-   (`\pi`{=tex}) is an organizational **policy/rule**;
-   \(a\) is the organizational/use **action actually realized** for a
    particular problem/context.

This is already compatible with the HLS ontology and becomes essential
once time is introduced.

Write, abstractly,

\[ `\boxed{
a=\pi(q)
}`{=tex} \]

in the simplest static case.

More generally, (`\pi`{=tex}) may condition on whatever information the
model makes admissible; HLS does not prescribe that information
structure at the foundational level.

## 7.3 Admissible organizational actions

Let

\[ `\mathcal `{=tex}A\_`\Pi`{=tex}(q;S) \]

denote the set of organizational/use actions available under class
(`\Pi`{=tex}) for problem (q), given competence state (S).

An action (a) may represent, depending on the instantiated model:

-   assignment to one unit;
-   use of several units;
-   delegation;
-   escalation;
-   sequencing;
-   collaboration;
-   redundancy;
-   or another admissible use of distributed competence.

These are examples, not a closed HLS taxonomy.

Operational constraints (B) remain conceptually distinct from
organizational admissibility. A model may therefore distinguish

\[ a`\in`{=tex}`\mathcal `{=tex}A\_`\Pi`{=tex}(q;S) \]

from the subset of actions that are operationally feasible under (B).

## 7.4 Static realization map

The static realization chain is

\[ `\boxed{
q
\xrightarrow{\pi}
a
\xrightarrow{S}
z.
}`{=tex} \]

At aggregate level,

\[ `\boxed{
(S,P,B,\Pi)
\longrightarrow
\pi
\longrightarrow
a
\longrightarrow
z^\pi.
}`{=tex} \]

T3 therefore explains the internal organizational mechanism hidden
inside the T0 mapping (`\pi`{=tex}`\mapsto `{=tex}z\^`\pi`{=tex}).

## 7.5 Organizational accessibility principle

A competence present in (S) contributes to system capability only
through organizationally admissible uses of that competence.

Accordingly, the same ((S,P,B)) can generate different feasible outcome
sets under different organizational classes:

\[ `\mathcal `{=tex}F\_{`\Pi`{=tex}*0}(S,P,B) `\neq`{=tex}
`\mathcal `{=tex}F*{`\Pi`{=tex}\_1}(S,P,B). \]

The organizational class does not create competence merely by enlarging
the action set; it changes which uses of the available competence can be
realized.

## 7.6 Organizational monotonicity

If

\[ `\Pi`{=tex}\_0`\subseteq`{=tex}`\Pi`{=tex}\_1 \]

under a consistent interpretation of admissibility, then

\[ `\boxed{
\mathcal F_{\Pi_0}(S,P,B)
\subseteq
\mathcal F_{\Pi_1}(S,P,B).
}`{=tex} \]

But strict inclusion of policy classes does not imply strict efficient
capability expansion:

\[ `\boxed{
\Pi_0\subsetneq\Pi_1
\centernot\Rightarrow
\overline{\mathcal F}_{\Pi_1}
\not\subseteq
D(\overline{\mathcal F}_{\Pi_0}).
}`{=tex} \]

The additional organizational possibilities may be redundant or
dominated. T1 and T2 determine which case holds.

------------------------------------------------------------------------

# 8. Why the action variable (a) is retained but (u) is not

The proposed competence-use variable (u) fails the minimality test as an
independent foundational object.

If its only static role is

\[ u=`\pi`{=tex}(q), `\qquad`{=tex} z=z(S,q,u), \]

then it is simply the realized action of the policy and should be
denoted by the existing organizational/use variable (a).

Therefore:

\[ `\boxed{
u\text{ is absorbed into }a.
}`{=tex} \]

The action (a), however, cannot be absorbed completely into
(`\pi`{=tex}) without losing a distinction that becomes structurally
important at the static/dynamic boundary:

\[ `\boxed{
\pi=\text{decision rule},
\qquad
a=\text{realized use of competence}.
}`{=tex} \]

Two policies may prescribe different actions on different problems;
future dynamic theory may depend on which action was actually executed,
not merely on the abstract identity of the policy.

No experience or learning variable is introduced in T3. T3 only
preserves the object to which such consequences may later attach.

------------------------------------------------------------------------

# 9. Static block consolidated

The complete static HLS chain is

\[ `\boxed{
(S,P,B,\Pi)
\longrightarrow
\pi
\longrightarrow
a
\longrightarrow
z
}`{=tex} \]

with four theoretical questions:

### T0 --- Feasible Capability

\[ `\boxed{\text{What outcomes are achievable?}}`{=tex} \]

### T1 --- Static Collective Capability Expansion

\[
`\boxed{\text{When does a richer organization add efficient capability?}}`{=tex}
\]

### T2 --- Organizational Sufficiency

\[
`\boxed{\text{When can the richer organization be reduced without capability loss?}}`{=tex}
\]

### T3 --- Organizational Realization

\[
`\boxed{\text{How does an organizational policy access and use distributed competence to realize outcomes?}}`{=tex}
\]

This closes the static block at the level required for the HLS
programme.

------------------------------------------------------------------------

# 10. Boundary to T4

No time index, memory, experience accumulation, learning, competence
evolution or future value is part of T0--T3.

The static endpoint is

\[ `\boxed{
(S,P,B,\Pi)\rightarrow\pi\rightarrow a\rightarrow z.
}`{=tex} \]

The dynamic block begins when execution can affect or depend on a
persistent state:

\[ `\boxed{
X_t,\pi_t
\rightarrow
(a_t,z_t,X_{t+1}).
}`{=tex} \]

The content and minimal structure of (X_t), and which transitions are
exogenous or endogenous, are questions for T4 and later blocks.

In particular, T3 does **not** yet assume

\[ a_t`\rightarrow `{=tex}E_t`\rightarrow `{=tex}S\_{t+1}. \]

That mechanism belongs beyond the static boundary.

------------------------------------------------------------------------

# 11. Status of the theoretical architecture

The current programme structure is:

\[ `\boxed{
\underbrace{
T0\rightarrow T1\rightarrow T2\rightarrow T3
}_{\text{STATIC HLS}}
\quad\Big|\quad
\underbrace{
T4\rightarrow T5\rightarrow T6
}_{\text{DYNAMIC HLS}}
}`{=tex} \]

with the provisional dynamic blocks:

-   **T4 --- Dynamic Capability**
-   **T5 --- Competence Development**
-   **T6 --- Organization--Development Coupling**

RQ0 may be studied within the later dynamic theory, but it does not
define the HLS programme or the T0--T6 architecture.

------------------------------------------------------------------------

# 12. Claims and non-claims

The present document establishes a **working theoretical scaffold**, not
a novelty claim.

In particular:

-   T0--T3 are intended to provide a minimal common mathematical
    language for static HLS;
-   T1 may reduce to classical assignment/resource-allocation theory
    under restrictive static assumptions;
-   T2 records reducibility rather than assuming organizational
    complexity is valuable;
-   T3 does not claim that organizational accessibility is a new
    scientific principle;
-   the ontology remains a translation/consistency tool and may evolve;
-   no theorem is claimed novel merely because it is expressed in HLS
    notation;
-   external theory should be mapped rigorously before being imported;
-   the static formalism must not be allowed to redefine the broader HLS
    scientific object.

The next scientific step is not to deepen T0--T3 indefinitely, but to
determine the minimum dynamic state and transition structure required by
T4.
