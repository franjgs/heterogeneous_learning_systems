# RQ0 Routing Integration Boundaries

## Epistemic scope

This document records definitions and proofs for finite exact synthetic worlds
under a common physical world and the repository's strong-SEP contract. It is
not a universal theorem about all HLS systems, a claim of empirical relevance,
or a claim that HLS dominates sufficiently coordinated separation.

RQ0 remains:

> Can the dynamic allocation and development of competences in a heterogeneous
> learning system improve long-term system performance compared with
> architectures that manage task allocation and knowledge transfer separately?

The exact constructive results here establish an **existence** answer under
their model assumptions and the stated strong-SEP contract. They do not settle
structural characterization, robustness, prevalence, or empirical relevance.

## 1. Scope and common-world contract

Let a finite exact world have common state, action, reward, opportunity,
development, resource, and information semantics for every evaluated policy.
The world never branches on the policy label. A history `h` determines state
`S(h)`, task `q(h)`, and the authorized operational actions. Define the
immediate-reward greedy correspondence:

\[
\mathcal G(h)=\arg\max_a R(S(h),q(h),a).
\]

All ties are sets. A statement about a policy tree concerns only histories
with positive probability under that tree.

## 2. HLS, strong SEP, and SEP-Omega

**Definition — HLS.** HLS may choose every operational and development action
admissible under the common world and information contract, maximizing the
exact finite-horizon return.

**Definition — strong SEP.** Its router must select an element of
`G(h)` at every reached history. Conditional on the actual operational action
and opportunity, its development manager optimizes admissible development
exactly. With routing ties, it retains the full resulting interval
`[J_SEP_min,J_SEP_max]`.

**Definition — SEP-Omega.** A separated router that receives sufficient exact
action-conditioned continuation information may maximize the same Bellman
objective as HLS. Equality with HLS is therefore a coordination/reducibility
boundary, not an independent algorithmic benchmark.

## 3. Policy-class inclusion theorem

**Theorem 1 — inclusion.** Under the common-world and common-information
contract:

\[
\Pi_{\mathrm{SEP}}\subseteq\Pi_{\mathrm{HLS}},
\qquad
J_{\mathrm{SEP,max}}(S_0)\le J_{\mathrm{HLS}}(S_0).
\]

**Proof.** A strong-SEP policy uses the same state, operational actions,
development actions, opportunity physics, costs, and rewards available to
HLS. HLS can imitate every such routing and development decision. The only
additional restriction is SEP's requirement that routing lie in
`G(h)`. Maximization over the superset cannot yield a lower value. ∎

This theorem would not be the relevant fairness relation if HLS received
extra observations or actions.

## 4. Necessary and sufficient strict-integration criterion

**Theorem 2 — on-policy criterion.** Assume a finite exact problem in which
optimal policies exist. Then:

\[
J_{\mathrm{HLS}}(S_0)>J_{\mathrm{SEP,max}}(S_0)
\]

if and only if no HLS-optimal policy selects only members of
`G(h)` on every positive-probability history.

**Proof.** If an HLS-optimal policy is strong-SEP-admissible, it belongs to
`Pi_SEP`; SEP therefore attains the HLS value. Conversely, if no HLS-optimal
policy lies in `Pi_SEP`, no SEP policy attains the HLS optimum. Since the
finite exact setting attains both maxima, the SEP maximum is strictly lower.
∎

A non-greedy action on a zero-probability branch does not satisfy the
criterion.

## 5. Local routing-as-teaching Bellman identity

Suppose, at a state `s`, routing action `a` affects only opportunity
probability `p(a)`. Let optimized continuation values conditional on
opportunity and no opportunity be action-independent values `V_1` and `V_0`.
Then:

\[
Q(s,a)=R(s,a)+p(a)V_1+[1-p(a)]V_0.
\]

For immediate-greedy `g` and alternative `b`:

\[
Q(s,b)-Q(s,g)
=[R(s,b)-R(s,g)]+[p(b)-p(g)](V_1-V_0).
\]

If `g` is uniquely greedy and `p(b)>p(g)`, a local routing inversion occurs
exactly when:

\[
[p(b)-p(g)](V_1-V_0)>R(s,g)-R(s,b).
\]

This is an exact local Bellman identity under its assumptions. It neither
implies a root-value advantage nor defines a universal opportunity mechanism.

## 6. Why local inversion is not sufficient globally

A local inversion establishes only a conditional preference given arrival at
that state. Strict root integration requires the state to lie on an
HLS-optimal root policy with positive probability and requires no
strong-SEP-admissible optimum to match root value.

Constrained reachability cost and local inversion gain are distinct Bellman
objects. There is no general scalar rule comparing them: predecessor actions,
branch probabilities, remaining horizon, and later policy adaptation matter.
The diagnostic world with `eta=.5` supplies an exact counterexample to the
claim that physical reachability of an inversion is sufficient for strict root
value.

## 7. Optimal-policy-tree interpretation

Writing `u` for the temporally valid operational/development sequence of one
cycle, the two values are:

\[
V_H(h)=\max_{u\in\mathcal U(h)}
\left[r(h,u)-k(h,u)+\mathbb E[V_H(h')\mid h,u]\right],
\]

\[
V_S(h)=\max_{\substack{u\in\mathcal U(h)\\a(u)\in\mathcal G(h)}}
\left[r(h,u)-k(h,u)+\mathbb E[V_S(h')\mid h,u]\right].
\]

A downstream non-greedy action matters at `S0` only if it is required on an
optimal positive-probability policy branch. This is the global condition in
Theorem 2.

## 8. A1 World E: one-step constructive reference

In frozen A1 World E:

\[
R_g=.80,\quad R_b=.70,\quad p_g=.275,\quad p_b=.80,
\quad V_0=.50,\quad V_1=.88.
\]

Thus:

\[
(p_b-p_g)(V_1-V_0)=.525\cdot.38=.1995>.10=R_g-R_b.
\]

HLS routes M2 rather than greedy M1 at the root:

\[
J_{\mathrm{HLS}}=1.504>1.4045=J_{\mathrm{SEP,max}}.
\]

The actor is M2 and the optimal opportunity recipient is M1. This is a
one-step constructive reference, not a prevalence result.

## 9. C1 R5: recursive constructive reference

In C1 R5, at cycle zero:

\[
R_g=.8,\quad R_b=.6,\quad p_g=0,\quad p_b=1,
\quad V_0=1.6,\quad V_1=1.85.
\]

Therefore:

\[
(p_b-p_g)(V_1-V_0)=.25>.2=R_g-R_b.
\]

HLS routes M2, develops M2 on task 2, then routes M2 again and develops M1
on task 1. It has genuine recursive feedback and:

\[
J_{\mathrm{HLS}}=49/20>12/5=J_{\mathrm{SEP,max}}.
\]

This is a reference-gate existence case under its explicitly declared
opportunity construction. It is not a phase study.

## 10. Exact zero-sum geometry family

The frozen family is:

\[
C(\alpha)=
\begin{pmatrix}
4/5 & 4/5-\alpha/5\\
3/5 & 3/5+\alpha/5
\end{pmatrix},\qquad 0\le\alpha\le1.
\]

It keeps task means, global mean, T1 rewards, T1 reward gap, and opportunity
primitives fixed. In particular, for both tasks:

\[
p(M1)=1/4,\qquad p(M2)=3/4.
\]

The chronology is task 1, then task 2, then terminal task 1. Development
targets task 2 after cycle zero and task 1 after cycle one, with
`eta=3/4`, `kappa=0`, and `beta=1`.

Write:

\[
A=4/5-\alpha/5,\qquad B=3/5+\alpha/5.
\]

## 11. Full analytical derivation of the integration window

At cycle one, no opportunity gives terminal value:

\[
W_0=4/5.
\]

With opportunity, M1 is the unique optimal recipient for task 1:

\[
4/5+\frac34(1-4/5)=19/20>9/10,
\qquad W_1=19/20.
\]

Hence, for every `alpha`:

\[
D^*=W_1-W_0=3/20.
\]

On the cycle-one base branch `O0=0`, the exact HLS action values are:

\[
Q_1(M1)=A+67/80=131/80-\alpha/5,
\]

\[
Q_1(M2)=B+73/80=121/80+\alpha/5.
\]

Their difference is:

\[
Q_1(M2)-Q_1(M1)=-1/8+2\alpha/5.
\]

Thus HLS selects M1 below `5/16`, both at `5/16`, and M2 above it.

At cycle zero, an opportunity develops M2 on task 2 uniquely:

\[
B^+=B+\frac34(1-B)=9/10+\alpha/20.
\]

The enriched cycle-one value is:

\[
V^+=B^++73/80=29/16+\alpha/20.
\]

The base value is:

\[
V^0_H=
\begin{cases}
131/80-\alpha/5,&0\le\alpha\le5/16,\\
121/80+\alpha/5,&5/16\le\alpha\le1.
\end{cases}
\]

The root action M1 is uniquely HLS-optimal throughout. Its `O0=0` and
`O0=1` branches occur with probabilities `3/4` and `1/4`, respectively.
Therefore:

\[
J_{\mathrm{HLS}}(\alpha)=
\begin{cases}
397/160-11\alpha/80,&0\le\alpha\le5/16,\\
191/80+13\alpha/80,&5/16\le\alpha\le1.
\end{cases}
\]

Strong SEP is constrained by immediate task-2 reward. On the base branch:

\[
\mathcal G_{T2}=
\begin{cases}
\{M1\},&\alpha<1/2,\\
\{M1,M2\},&\alpha=1/2,\\
\{M2\},&\alpha>1/2.
\end{cases}
\]

Its conservative maximum is:

\[
J_{\mathrm{SEP,max}}(\alpha)=
\begin{cases}
397/160-11\alpha/80,&0\le\alpha<1/2,\\
191/80+13\alpha/80,&1/2\le\alpha\le1.
\end{cases}
\]

At `alpha=1/2`, strong SEP retains the full tie interval:

\[
J_{\mathrm{SEP,min}}=193/80,
\qquad J_{\mathrm{SEP,max}}=79/32.
\]

Subtracting gives:

\[
\Phi(\alpha)=
\begin{cases}
0,&0\le\alpha\le5/16,\\
3\alpha/10-3/32,&5/16<\alpha<1/2,\\
0,&1/2\le\alpha\le1.
\end{cases}
\]

Consequently:

\[
J_{\mathrm{HLS}}>J_{\mathrm{SEP,max}}
\iff 5/16<\alpha<1/2.
\]

## 12. Lower boundary: Bellman inversion

For `alpha<1/2`, M1 is strictly greedy in the base task-2 state. Its immediate
sacrifice for M2 is:

\[
\Delta R_{T2}=1/5-2\alpha/5.
\]

The opportunity advantage is fixed:

\[
\Delta pD^*=\frac12\frac3{20}=\frac3{40}.
\]

At `alpha=5/16`, these are equal. M2 remains strictly non-greedy there, but
its Bellman advantage is zero. Above the boundary, M2 is strictly Bellman
optimal and strictly non-greedy until `alpha=1/2`.

## 13. Upper boundary: greedy admissibility

At `alpha=1/2`, M2 enters the immediate-reward greedy set. HLS still selects
M2 in the base state, but M2 is now strong-SEP-admissible. Strong SEP can use
M2 and attain the HLS root value. Thus disappearance of `Phi` at this boundary
does not mean that continuation value ceased to favor M2; it means that the
strong-SEP routing constraint no longer excludes M2.

For `5/16<alpha<1/2`, the root uses M1 and `P(O0=0|a0=M1)=3/4`. On that
positive-probability base history HLS uniquely uses M2, while M1 is uniquely
greedy. Every HLS-optimal policy therefore contains this non-greedy action;
by Theorem 2, no HLS-optimal policy is completely strong-SEP-admissible.

## 14. SEP-Omega coordination boundary

SEP-Omega receives the action-conditioned continuation values that strong SEP
does not internalize. It solves the same finite Bellman maximization as HLS in
these worlds, so:

\[
J_{\mathrm{SEP\text{-}Omega}}=J_{\mathrm{HLS}}.
\]

This equality is expected constructive reducibility with sufficient
coordination. It does not negate strict integration value relative to the
defined strong-SEP comparator.

## 15. Epistemological status

| Claim | Status |
| --- | --- |
| RQ0 existence under this exact model and strong-SEP contract | **YES** |
| structural characterization beyond this family | **IN PROGRESS** |
| robustness or prevalence | **NOT ESTABLISHED** |
| empirical relevance | **NOT ESTABLISHED** |

The exact geometry result must not be generalized to all G0+C1--C5 worlds.
It does not show that every family has a window, that windows are unique, that
complementarity suffices, that increasing heterogeneity increases `Phi`, or
that HLS exceeds SEP-Omega.

## 16. Open structural characterization problem

The next theoretical object is not a new numerical family. It is to formulate
conditions, independent of `5/16` and `1/2`, under which a parametric family
can have separate Bellman-inversion and greedy-admissibility boundaries and
therefore an open region of irreducibly integrated behavior. Continuity,
optimal-policy correspondences, on-policy reachability, and tie semantics must
be treated explicitly before any such statement becomes a theorem.

## 17. Paper-facing theoretical structure

- Policy classes and fair comparison
- Reducibility and strict integration
- Routing as teaching
- Local versus root integration value
- Integration windows
- Exact constructive specialization `C(alpha)`
- Coordination boundary SEP-Omega
- Scope and limitations
