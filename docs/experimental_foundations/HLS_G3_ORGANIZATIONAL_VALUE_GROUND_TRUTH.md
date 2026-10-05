# HLS G3 Organizational-Value Ground Truth

**Status:** Canonical G3 scenario, analytical ground truth, verified implementation, and finite adversarial audit
**Scope:** 3-worker × 2-task/competence-type × 2-period scenario; no new HLS theory
**Predecessor:** [HLS Minimal Reference Scenario](HLS_MINIMAL_REFERENCE_SCENARIO.md)
**Phase status:** I conceptual — CLOSED; II algebraic audit — CLOSED / STRONG REDUCTION; III documentation — completed; IV implementation — completed; V finite adversarial validation — completed

## 1. Purpose and boundary

G3 is the next structural scenario after the Minimal Reference Scenario (MIS).
It isolates how additional organizational flexibility changes the collective
value of action-induced competence development.

G3 is an analytical scenario and ground truth. It does not define a new
mathematical class of HLS, a new assignment theory, or an HLS architecture.
Its Phase-II audit reduces development value to standard assignment
sensitivities.

## 2. Common world physics

Let workers be `W={1,2,3}`, task/competence types be `Q={A,B}`, and the
horizon be two periods. The competence state is

$$
S=\begin{pmatrix}a_1&b_1\\a_2&b_2\\a_3&b_3\end{pmatrix}.
$$

Each worker has unit capacity, `B=(1,1,1)`, and `x_{ik}\in\{0,1\}` denotes
assignment of worker `i` to type `k`. For an admissible assignment,

$$
R(S,x)=\sum_{i,k}x_{ik}s_{ik}.
$$

G3 retains exactly the MIS saturating learning-by-doing law. With common
world learning scale `eta`,

$$
\ell_\eta(s)=\min\{1,\ s+\eta(1-s)^2\},\qquad
d_\eta(s)=\ell_\eta(s)-s.
$$

Only competence entries used by the operational assignment are updated. No
training action, cost, noise, communication, or additional learning physics
is introduced. For every regime,

$$
D_\lambda(x)=V_\lambda(F(S,x))-V_\lambda(S),
$$

where `V_lambda` is the exact terminal assignment value under the same
capacity and load regime.

## 3. G3a: unit load with organizational slack

G3a uses `lambda=(1,1)`. It assigns one worker to `A` and a different worker
to `B`; the six admissible assignments are

$$
(1,2),(1,3),(2,1),(2,3),(3,1),(3,2),
$$

where `(i,j)` means `i -> A` and `j -> B`. The terminal operator is

$$
V(S)=\max_{i\ne j}(a_i+b_j).
$$

For action `(i,j)`, let `k` be the remaining worker and set

$$
\alpha_i=d_\eta(a_i),\qquad \beta_j=d_\eta(b_j),
$$

$$
w_{rs}=a_r+b_s,\qquad V=\max_{r\ne s}w_{rs},\qquad g_{rs}=V-w_{rs}.
$$

The exact post-learning value difference is

$$
\boxed{D_{ij}=\max\{0,\ \alpha_i+\beta_j-g_{ij},\ \alpha_i-g_{ik},\ \beta_j-g_{kj}\}.}
$$

The terms respectively cover: no improvement changes terminal value; both
increments are used; only the `A` increment is used; or only the `B`
increment is used. The gaps are ordinary, action-conditioned assignment gaps.

## 4. G3b: full utilization and its dual

G3b uses `lambda=(2,1)`: one worker executes `B`, while the other two execute
`A`. It is a utilization regime/ablation of the same world, not an independent
model. Slack or utilization is only descriptive when derived from `B` and
`lambda`; it is neither primitive nor sufficient statistic.

Define comparative advantage for `B` by

$$
q_j=b_j-a_j,\qquad V(S)=\sum_i a_i+\max_j q_j.
$$

If worker `j` executes `B`, the other workers execute `A`. Let

$$
A_{\mathrm{inc}}=\sum_{r\ne j}\alpha_r,
$$

$$
q_j'=q_j+\beta_j,\qquad q_r'=q_r-\alpha_r\quad(r\ne j).
$$

Then

$$
\boxed{D_{(2,1),j}=A_{\mathrm{inc}}
+\max\left\{q_j+\beta_j,\ \max_{r\ne j}(q_r-\alpha_r)\right\}
 -\max_r q_r.}
$$

This separates direct increase in `A` productivity from change in maximal
comparative advantage without selecting an arbitrary initial optimizer. If
`q^*=max_rq_r` and `g_r=q^*-q_r`, the latter change is equivalently

$$
\max\left\{\beta_j-g_j,\ \max_{r\ne j}(-\alpha_r-g_r)\right\}.
$$

The dual `lambda=(1,2)` exchanges `A` and `B`. With

$$
p_i=a_i-b_i,\qquad V(S)=\sum_i b_i+\max_i p_i,
$$

if worker `i` executes `A`,

$$
\boxed{D_{(1,2),i}=\sum_{r\ne i}\beta_r
+\max\left\{p_i+\alpha_i,\ \max_{r\ne i}(p_r-\beta_r)\right\}
 -\max_r p_r.}
$$

## 5. Phase-II result: strong reduction

**VERDICT: A. STRONG REDUCTION.**

In G3, `D_lambda(x)` is exactly determined by learning-by-doing increments
and standard assignment sensitivities.

| Regime | Algebraically justified information |
| --- | --- |
| G3a `(1,1)` | `alpha_i`, `beta_j`, and conflict-conditioned gaps `g_ij`, `g_ik`, `g_kj`. |
| G3b `(2,1)` | Affected increments, comparative advantages `q`, and adjusted terminal alternatives. |
| Dual `(1,2)` | Corresponding `p=a-b` quantities and affected increments. |

This does not prove general mathematical minimality. G3b cannot generally be
reduced to only the initial best/second-best gap: after `A` workers change, a
third adjusted alternative can become terminal maximizer. The required
objects remain standard assignment sensitivities.

## 6. Structural checks F1--F4

- **F1 — placement effect:** equal or comparable local developments can have
  different `D` because they face different assignment gaps.
- **F2 — organizational mediation:** this difference arises with the same
  learning law; it is created by the terminal assignment operator.
- **F3 — utilization regime:** changing from `(1,1)` to `(2,1)` or `(1,2)`
  changes that operator and can change relative development value. This is not
  a claim that slack alone is causal or sufficient.
- **F4 — nontrivial ordering:** total/local learning need not order `D`; a
  smaller increment can cross a relevant gap while a larger one does not.

Accordingly, in general,

$$
D\ne f(\|\Delta S\|),\qquad D\ne f(\Delta S,\lambda).
$$

The omitted information is ordinary feasible-assignment structure and gaps,
not an HLS-specific latent variable.

## 7. Direct versus reorganization

For G3b, the identity gives a canonical decomposition,

$$
D=\text{direct productivity increment}+\text{change in maximal comparative advantage}.
$$

It remains well defined under ties because it refers to values, not a selected
optimizer. G3a has no retained additive decomposition based on an initial
optimal `y*`: with multiple optima it depends on the arbitrary choice of
`y*`. Its stable objects are `D_ij` and the max/gap formula.

## 8. Symmetries and boundaries

The formulas are invariant under a consistent permutation of workers and dual
under `A<->B` with `(2,1)<->(1,2)`. Worker labels have no standing beyond their
structural position.

Zero learning, saturation, and zero assignment gaps are already included.
At a gap or assignment boundary, value remains continuous while the optimal
assignment may change or become non-unique. These are standard optimization
degeneracies, not additional HLS theory.

## 9. Closure and future boundary

G3 must not be enlarged in search of new theory. Its role is exact analytical
ground truth for organizational value of development. Phase II shows standard
assignment sensitivities are sufficient to calculate `D` exactly in G3.

After implementation and validation, a future hypothesis may test whether a
longer horizon breaks this reduction:

$$
S_0\ \to\ x_0\ \to\ S_1\ \to\ x_1(S_1)\ \to\ S_2.
$$

There, a period-0 action may change later assignment and later learning
recipients. This is only motivation for a future G4 question, not a G3 result
or G4 design.

## 10. Non-claims

G3 does not establish a new assignment theory, new HLS mathematics, universal
minimality of these sensitivities, HLS architectural superiority, a need for
approximate dynamic programming, sufficiency outside G3, causal sufficiency
of slack, or a requirement to approximate `D`. To the contrary, `D` is
exactly calculable in G3 using standard assignment sensitivities.

## 11. G3-H closure: heterogeneous learning rates and future opportunities

G3-H is exactly G3 with fixed worker-specific learning scales `eta_i` in
place of G3's common `eta`; the closed case uses G3a. An executed competence
of worker `i` uses

$$
\ell_{\eta_i}(s)=\min\{1,\ s+\eta_i(1-s)^2\}.
$$

There is no new physics: capacity, assignments, reward, the MIS saturating
learning law, and the G3a terminal operator remain unchanged.  For a state
`S`, write the local organization-development value as

$$
M_S(x)=R(S,x)+\beta D(S,x),\qquad
D(S,x)=V(F(S,x))-V(S),
$$

and compare the additional organization-development opportunity by the
standard deterministic dynamic-programming quantity

$$
Q_S(x)=M_S(x)+\max_y M_{F(S,x)}(y).
$$

The minimum phenomenon therefore requires that additional
organization-development opportunity; it is not present in the one-step
local comparison alone.

With human 1-based worker numbering, let

$$
S_0=\begin{pmatrix}0.5&0.7\\0.3&0.2\\0.5&0.8\end{pmatrix},\qquad
\eta=(0.4,0.6,0.4),\qquad \beta=1,
$$

and compare `x_a=(2,3)` with `x_b=(3,1)`.  Direct evaluation of the G3a
operator gives the following auditable branches.  The displayed future
maxima enumerate all six admissible G3a actions.

| Present action | `R(S_0,x)` | `D(S_0,x)` | `M_{S_0}(x)` | `F(S_0,x)` | maximizing future `y` | `max_y M_{F(S_0,x)}(y)` | `Q_{S_0}(x)` |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| `x_a=(2,3)` | 1.100 | 0.110 | 1.210 | `((0.500,0.700),(0.594,0.200),(0.500,0.816))` | `(2,3)` | 1.522444 | 2.732444 |
| `x_b=(3,1)` | 1.200 | 0.036 | 1.236 | `((0.500,0.736),(0.300,0.200),(0.600,0.800))` | `(3,1)` | 1.4278784 | 2.6638784 |

In the action order `(1,2),(1,3),(2,1),(2,3),(3,1),(3,2)`, the enumerated
future `M` values are respectively

$$
(0.706, 1.3355424, 1.3929016, 1.522444, 1.200, 0.700)
$$

after `x_a`, and

$$
(0.764, 1.380, 1.094, 1.174, 1.4278784, 0.864)
$$

after `x_b`.

Thus the local ranking is reversed by the future opportunity:

$$
M_{S_0}(x_a)<M_{S_0}(x_b),\qquad
Q_{S_0}(x_a)>Q_{S_0}(x_b).
$$

The causal ablation is

$$
Q_{S_0}(x_a)-Q_{S_0}(x_b)
=\underbrace{(1.210-1.236)}_{-0.026}
+\underbrace{(1.522444-1.4278784)}_{0.0945656}
=0.0685656.
$$

**VERDICT: PASS — FUTURE-OPPORTUNITY COMPARISON REQUIRED.**

"In G3-H, local organization-development value can be insufficient because
present actions can alter the value of future organization-development
opportunities, and accounting for those opportunities can change the
present action ranking."

This closed counterexample does not demonstrate irreducibility, constitute
new dynamic theory, or imply a particular HLS architecture.  It is a
deterministic dynamic-programming calculation using the existing G3/MIS
physics, with only `eta -> eta_i`.

## 12. Post-closure C1/C2 audit and boundary

This section records two post-closure audits of the fixed G3-H ground truth.
They introduce neither new G3-H physics nor a new HLS mechanism.

### C1: development-only future opportunity — FALSIFIED

Retain the local baseline

$$
M_S(x)=R(S,x)+\beta D(S,x),
$$

and consider

$$
H_{C1}(S,x)=M_S(x)+\beta^2\max_y D(F(S,x),y).
$$

This expression is well defined using the existing G3-H state transition,
G3a action set, terminal operator, and development value.  It is not
redundant with `M`: writing `S'=F(S,x)`,

$$
\max_yD(S',y)=\max_yV(F(S',y))-V(S').
$$

However, C1 is falsified by the closed counterexample above.  At `beta=1`,

$$
\max_yD(F(S_0,x_a),y)=0.112444,
\qquad
\max_yD(F(S_0,x_b),y)=0.0918784,
$$

so that

$$
H_{C1}(x_a)=1.322444 < 1.3278784=H_{C1}(x_b).
$$

It therefore preserves the incorrect local ranking.  The precise loss is the
future operational reward `R(S',y)`: `max D` retains a best future development
increment but discards the joint future `R`--`D` trade-off.

### C2: joint future opportunity — REDUCTION TO LOOK-AHEAD / DP

Consider instead

$$
H_{C2}(S,x)=M_S(x)+\beta^2\max_yM_{F(S,x)}(y).
$$

With `S'=F(S,x)`, the exact G3-H definitions give

$$
\begin{aligned}
H_{C2}(S,x)
&=R(S,x)+\beta[V(S')-V(S)]\\
&\quad+\beta^2\max_y\{R(S',y)+\beta[V(F(S',y))-V(S')]\}\\
&=R(S,x)-\beta V(S)+\beta(1-\beta^2)V(S')\\
&\quad+\beta^2\max_y\{R(S',y)+\beta V(F(S',y))\}.
\end{aligned}
$$

For `beta=1`, this is exactly the closed G3-H look-ahead

$$
Q_S(x)=M_S(x)+\max_yM_{F(S,x)}(y).
$$

For general `beta`, C2 has the same finite-horizon Bellman/look-ahead
structure with a different temporal weight from the documented `Q`.  It is
not a new HLS mechanism or a structurally cheaper approximation: it explicitly
evaluates the future joint opportunity.

### Negative result and scientific boundary

G3-H currently provides no evidence for an exact intermediate representation
between local organization-development value,

$$
M=R+\beta D,
$$

and explicit future joint-opportunity evaluation,

$$
\max_y\{R+\beta D\}.
$$

The C1 failure establishes only that `max_yD(S',y)` loses information needed
in the audited counterexample: it omits future operational reward and the
joint future `R`--`D` trade-off. No intermediate candidate is inferred from
this gap.

The resulting boundary is limited and negative:

- a local organization-development valuation can be insufficient;
- future development opportunity alone can also be insufficient;
- the joint future organization-development opportunity can matter; and
- calculating it exactly in G3-H reduces to standard look-ahead/DP.

G3-H is closed as the analytical microscope for this question.  It must not
be extended by increasing its horizon or excavating further continuation
structure.
