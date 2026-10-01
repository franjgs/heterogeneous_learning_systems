# G1 — Static Beam-1 experimental ground truth

**Status:** validated static reference instrument for the HLS programme.  
**Scope:** T0--T3 only; two-agent/two-task analytical ground truths.  
**Not a claim:** novel static Operations Research theory, learning value, or
dynamic HLS evidence.

G1 is the canonical experimental support for **Beam 1 — organization/use of
current competences**: *who should do what?* It operationalizes the static
foundation in [HLS Static Theoretical Foundation — T0--T3](HLS_STATIC_THEORY.md)
with fixed competence structure `S`, demand `P`, operational constraints `B`,
and admissible organizational policy class `Pi`.

The central static question is:

> Given `(S, P, B, Pi)`, what collective outcomes are attainable, and what
> additional capability can be realized by changing how the existing
> competences are organized?

G1 contains no competence evolution, learning, knowledge transfer, learning by
doing, forgetting, Beam-2 intervention, or `a_t -> E_t -> S_{t+1}` loop. It
ends at the static chain:

```text
(S, P, B, Pi) -> pi -> a -> z.
```

The executable specification and reproduction commands are in
[the G1 experiment README](../../experiments/synthetic/g1/README.md); numerical
artifacts are in [`results/foundations/g1_static/`](../../results/foundations/g1_static/).

## 1. Static theory-to-evidence mapping

| Static theory | G1 realization |
| --- | --- |
| **T0 — feasible collective outcome set** | Computes attainable effectiveness or effectiveness-resource points for fixed `S`, `P`, `B`, and policy class. |
| **T1 — static capability / null baseline** | Uses the appropriate time-sharing closure, so a deterministic comparison is not mistaken for frontier expansion. |
| **T2 — organizational sufficiency** | Includes explicit homogeneous and dominance nulls in which richer organization adds no efficient collective capability. |
| **T3 — organizational realization** | Holds `S`, `P`, and `B` fixed while enlarging `Pi_ONE` to `Pi_ROUTE`; measures the realized difference on the common feasible domain. |

Thus G1 implements an operational T3 comparison:

```text
Pi_ONE subset Pi_ROUTE,
Delta_Y = Y_ROUTE* - Y_ONE*.
```

It does not assert that every richer policy class is useful. Its null cases are
as important as its positive controls.

## 2. The central static lesson

> **Heterogeneity is not the same thing as organizationally exploitable
> heterogeneity.**

The value of a fixed competence structure is not a property of `S` alone. It
depends on the interaction:

```text
fixed competence structure + demand/problem structure
+ operational constraints + admissible organization
-> realized collective capability.
```

G1 keeps these distinctions explicit:

1. **Heterogeneity:** agents differ.
2. **Attainable-set expansion:** a richer organization adds attainable
   outcomes.
3. **Efficient capability expansion:** the relevant efficient frontier
   improves.
4. **Organizational value:** that improvement matters at the actual `P` and
   `B`.

None of the following implications holds generally:

```text
heterogeneity                  !=> organizational value
attainable-set expansion       !=> efficient capability expansion
efficient capability expansion !=> value at every operating point.
```

## 3. G1.1 — equal-resource specialization baseline

G1.1 is the minimal two-agent/two-task, equal-resource case. `ONE` assigns
both task types to one agent; `ROUTE` may assign each task type independently.
For demand `p = P(q=1)`, it evaluates:

```text
Delta_Y(p) = Y_ROUTE*(p) - Y_ONE*(p).
```

It validates that homogeneous agents and task-wise dominance yield no
organizational gain; crossed task-dependent advantage can yield gain; demand
composition determines how much of that advantage is exploitable; and the
gain vanishes at degenerate demand endpoints.

The stored analytical controls are reproduced to floating-point precision:

| Control | Result |
| --- | --- |
| Symmetric crossed specialization | `Delta_Y(p) = 0.8 min(p, 1-p)`, `p*=0.5`, `Delta_Y_max=0.4`; maximum closed-form error `1.11e-16`. |
| Asymmetric crossed specialization | `A1=0.6`, `A2=0.4`, `p*=0.4`, `Delta_Y_max=0.24`; maximum closed-form error `1.39e-16`. |

G1.1 is a static specialization baseline, not evidence about learning,
competence development, or joint organization-development value.

## 4. G1.2 — effectiveness-resource extension

G1.2 retains the fixed two-agent/two-task setting and represents each
agent-task outcome by `z_mj = (y_mj, r_mj)`, where effectiveness `y` is
maximized and resource consumption `r` is minimized. For deterministic
assignment `ab`, with `p=P(q1)`:

```text
R_ab(p) = p r_a1 + (1-p) r_b2
Y_ab(p) = p y_a1 + (1-p) y_b2
Z_ab    = (R_ab, Y_ab).
```

The policy classes and their time-sharing closures are:

```text
K_ONE   = {Z_11, Z_22}              F_ONE   = conv(K_ONE)
K_ROUTE = {Z_11, Z_12, Z_21, Z_22}  F_ROUTE = conv(K_ROUTE).
```

For budget `B`, G1.2 evaluates the upper efficient convex hull:

```text
Y_Pi*(B,p) = max Y  subject to (R,Y) in F_Pi and R <= B.
Delta_Y(B,p) = Y_ROUTE*(B,p) - Y_ONE*(B,p).
```

`Delta_Y` is interpreted only on the **common feasible domain**. A
ROUTE-only feasible point is an additional feasibility fact, not silently
reported as an effectiveness gain.

For fixed `p`, the hull makes `Y_ONE*`, `Y_ROUTE*`, and `Delta_Y` piecewise
affine in `B`. Consequently the exact maximum is found at a relevant hull
breakpoint (up to equivalent flat maxima), not by a generic continuous
optimizer. Because `F_ONE` is a subset of `F_ROUTE`, organizational
monotonicity gives `Delta_Y(B,p) >= 0` on the common feasible domain. The
largest observed numerical violation is `2.22e-16`, consistent with
floating-point noise.

### 4.1 Parallelogram diagnostic

The four deterministic points obey:

```text
Z_11 + Z_22 = Z_12 + Z_21.
```

With:

```text
delta_y1 = y_11 - y_21    delta_r1 = r_11 - r_21
delta_y2 = y_12 - y_22    delta_r2 = r_12 - r_22
D = delta_r1 delta_y2 - delta_y1 delta_r2,
```

their attainable parallelogram has area:

```text
Area_ROUTE(p) = p(1-p)|D|.
```

This is a geometric diagnostic, not a gain criterion: `D != 0` does **not**
imply `Delta_Y > 0`. The largest identity and area-formula errors observed are
respectively `2.22e-16` and `2.78e-17`.

## 5. Canonical G1.2 controls

| Scenario | Control and validated lesson |
| --- | --- |
| **S0 — homogeneous null** | Additional organization without heterogeneity has `Delta_Y=0`. |
| **S1 — Pareto-dominance null** | Heterogeneity alone is insufficient: task-wise Pareto dominance gives `Delta_Y=0`. |
| **S2 — equal-resource G1.1 embedding** | At `p=0.5`, `Delta_Y_max=0.4` at `B=0.5`, while `D=0`. Efficient organizational gain does not require two-dimensional attainable-set expansion. |
| **S3 — genuine bicriterion trade-off** | At `p=0.5`, the organizational effectiveness-resource frontier yields `Delta_Y_max=0.3` at `B=0.8`. |
| **S4 — geometric-expansion null** | At `p=0.5`, `D=-0.18` and attainable area is `0.045`, but `Delta_Y=0`. Geometric expansion is not efficient organizational value. |
| **S5 — bounded organizational-gain window** | At `p=0.5`, the same fixed competence structure has zero, then positive, then zero organizational value as `B` changes. |

For the key S5 control at `p=0.5`, the exact hulls are:

```text
ONE:   (0.25, 0.70) -> (0.65, 0.80)
ROUTE: (0.25, 0.70) -> (0.40, 0.80).
```

The breakpoints are `0.25`, `0.40`, and `0.65`; the positive-gain region is
the open interval `(0.25, 0.65)`; and the maximum is:

```text
B* = 0.40,    Delta_Y_max = 0.0625.
```

The maximum S5 analytical/computational discrepancy is `1.145e-16`. S5
therefore demonstrates that, with fixed `S`, fixed demand, and fixed policy
classes, a change only in operational budget can yield:

```text
Delta_Y = 0 -> Delta_Y > 0 -> Delta_Y = 0.
```

## 6. Relation to established theory and dynamic boundary

The G1 mathematics is closely related to established assignment/resource
allocation, bicriterion assignment, process/resource flexibility,
skill-based routing, and convexified/time-sharing decision rules. G1 does not
relabel those bodies of work as novel HLS theory. It imports a static
organizational principle into HLS language, establishes the appropriate static
null/baseline, validates the T0--T3 interpretation computationally, and
provides the reference point for later competence-evolution questions.

Its Garicano-like role is limited to the programme-level principle that
distributed heterogeneous capabilities, problem structure, and organizational
access/allocation jointly determine collective problem-solving capability. It
is not a reproduction of a complete Garicano model.

The static boundary is explicit:

```text
fixed S -> organization -> realized static capability.
```

The later dynamic question begins only when competence can change:

```text
S_t -> organization/action -> operation/experience/development
    -> S_{t+1} -> future organization.
```

G1 does not analyze that loop. It supplies the fixed-`S` reference needed
before asking what, if anything, competence evolution adds.

## 7. Non-claims

G1 does **not** establish novelty of static assignment theory; superiority of
HLS over Operations Research; routing superiority in every heterogeneous
system; intrinsic value of heterogeneity; universal value of organizational
flexibility; learning or competence-development value; Beam-2 value; joint
organization-development value; RQ0; T4--T6; or empirical performance on real
ML portfolios.

It is a static ground truth and baseline. Its evidence supports only the
scoped T0--T3 realization described here.
