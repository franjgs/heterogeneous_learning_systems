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
