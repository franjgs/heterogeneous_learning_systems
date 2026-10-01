# HLS Dynamic Theoretical Foundation --- T4--T6

**Status:** Consolidated working foundation\
**Scope:** Minimal dynamic Heterogeneous Learning Systems (HLS)\
**Static prerequisite:** `HLS_STATIC_THEORY.md`\
**Constructive reference:** `HLS_G2_DYNAMIC_GROUND_TRUTH.md`

## 1. Purpose

This document consolidates the minimum dynamic structure required after
T0--T3. It follows the sequence:

**T4 --- REACHABILITY → T5 --- VALUE → T6 --- COUPLING**

These are three questions about one dynamic system, not three
increasingly complicated models. The foundation does not claim new
reachability, control, dynamic-programming, assignment, or learning
theory. Established theory is imported where it solves the corresponding
subproblem.

## 2. Static/dynamic boundary

The static block keeps competence fixed. The first genuinely dynamic
primitive is

\[ S\_{t+1}=F(S_t,a_t). \]

The action (a_t) is the realized organizational/use action retained by
T3. The transition (F) may instantiate learning by doing, training,
teaching, transfer, forgetting, interference, or another development
mechanism.

A changing state alone is insufficient. If (S\_{t+1}) changes
independently of present decisions, the system is a succession of static
T0--T3 problems. The minimum endogenous boundary is:

\[ a_t `\rightarrow `{=tex}S\_{t+1}. \]

## 3. Reuse of the static capability operator

Dynamic HLS does not redefine collective capability. For a future state,
T0--T3 determine the feasible/reproducible outcomes and non-dominated
capability frontier under the future operating conditions.

Compactly,

\[ `\mathcal `{=tex}C\_{t+1}(a_t) =
`\mathcal `{=tex}C\_{`\Pi`{=tex}*{t+1}} (F(S_t,a_t),P*{t+1},B\_{t+1}).
\]

The feasible set and efficient frontier remain distinct as in the static
theory.

## 4. T4 --- Dynamic Collective Capability

**Question:** Can present decisions induce different future collective
capabilities by changing the future competence state?

The positive condition is the existence of (a,a') such that

\[ `\boxed{\mathcal C_{t+1}(a)\neq\mathcal C_{t+1}(a').}`{=tex} \]

This says nothing yet about which action is preferable.

### T4 null boundary

It may happen that

\[ F(S_t,a)`\neq `{=tex}F(S_t,a') \]

and even that attainable outcome sets differ, while

\[ `\boxed{\mathcal C_{t+1}(a)=\mathcal C_{t+1}(a').}`{=tex} \]

Hence

\[ `\boxed{\text{competence evolution}\not\Rightarrow
\text{efficient collective-capability evolution}.}`{=tex} \]

An individual competence improvement may be collectively redundant.

## 5. T5 --- Competence-Development Value

**Question:** When do action-induced differences in future collective
capability matter under future operating conditions?

Let

\[ V\_{t+1}(S;`\theta`{=tex}\_{t+1}) \]

be the best future collective performance attainable from state (S)
under

\[ `\theta`{=tex}*{t+1}=(P*{t+1},B\_{t+1},`\Pi`{=tex}\_{t+1}) \]

for the performance criterion of the instantiated problem. This does not
assert a universal scalar HLS utility.

For two present actions define comparative development value:

\[ `\boxed{
\Delta^{dev}_{t+1}(a,a')
=
V_{t+1}(F(S_t,a);\theta_{t+1})
-
V_{t+1}(F(S_t,a');\theta_{t+1}).
}`{=tex} \]

### T5 null boundary

Different efficient future capabilities can have equal value:

\[
`\mathcal `{=tex}C\_{t+1}(a)`\neq`{=tex}`\mathcal `{=tex}C\_{t+1}(a'),
`\qquad`{=tex} `\boxed{\Delta^{dev}_{t+1}(a,a')=0.}`{=tex} \]

Therefore

\[ `\boxed{\text{efficient collective-capability evolution}
\not\Rightarrow\text{positive development value}.}`{=tex} \]

## 6. T6 --- Organization--Development Coupling

**Question:** How does future development value induced by a present
decision interact with its present operational value?

For two alternatives define

\[ `\Delta `{=tex}R_t(a,a')=R_t(a)-R_t(a'). \]

In the minimum two-period setting,

\[ `\boxed{\Delta J_t=\Delta R_t+\Delta^{dev}_{t+1}.}`{=tex} \]

This is a standard two-stage continuation-value decomposition. Its HLS
role is to expose the interaction between current competence use and
future competence development.

The minimal regimes are:

-   **Static sufficiency:** (`\Delta`{=tex}\^{dev}=0), hence
    (`\Delta `{=tex}J=`\Delta `{=tex}R).
-   **Alignment:** present and future terms favor the same action.
-   **Trade-off:** (`\Delta `{=tex}R,`\Delta`{=tex}\^{dev}\<0).
-   **Decision reversal:**
    (`\operatorname{sign}`{=tex}(`\Delta `{=tex}J)`\neq`{=tex}`\operatorname{sign}`{=tex}(`\Delta `{=tex}R)).

Thus

\[
`\boxed{\text{trade-off}\not\Rightarrow\text{decision reversal}.}`{=tex}
\]

And, critically,

\[ `\boxed{\text{decision reversal}\not\Rightarrow
\text{need for irreducibly joint HLS management}.}`{=tex} \]

A sufficient continuation value, price, threshold, incentive, or other
coordination signal may still reproduce the dynamic optimum.
Irreducibility is outside this minimal T4--T6 foundation.

## 7. Minimality

All three blocks are required.

Removing T4 loses the distinction between internal competence change and
collective-capability change. Removing T5 loses the distinction between
capability change and useful development. Removing T6 leaves
organization/use and development/value disconnected.

No additional foundational block is required between them.

The following are deliberately not required: stochastic transitions,
long horizons, discount factors, explicit teaching, explicit development
actions, changing demand, forgetting, interference, multiple resource
dimensions, partial information, centralized management, or irreducible
joint management.

**Complexity rule:** no new mechanism without a reduction it is intended
to break.

## 8. Relation to established theory

T4 admits a reachability/control interpretation. T5 is a value
comparison over reachable future capability. T6 is a two-stage
dynamic-programming/continuation-value decomposition. These reductions
are intentional baselines, not defects.

## 9. Consolidated chain

``` text
T0–T3: fixed competence
        |
realized action a_t
        |
================ STATIC / DYNAMIC BOUNDARY ================
        |
S_{t+1}=F(S_t,a_t)
        |
        v
T4: future collective capability
        |
        v
T5: future development value
        |
        +----------------------+
                               |
current operational value -----+
                               |
                               v
T6: organization–development coupling
```

## 10. Scoped claims

The foundation supports only these claims:

1.  endogenous action-dependent competence change is the minimal
    boundary beyond a succession of static HLS problems;
2.  competence evolution need not change efficient collective
    capability;
3.  different efficient future capabilities need not have different
    future value;
4.  positive development value need not alter the statically preferred
    present action;
5.  sufficiently large development value can reverse a static preference
    in a two-period model;
6.  none of the above establishes irreducibly joint management, RQ0,
    prevalence, robustness, or empirical relevance.
