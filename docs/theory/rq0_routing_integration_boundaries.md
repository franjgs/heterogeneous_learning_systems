# RQ0 Routing Integration Boundaries

## Epistemic scope

This document records definitions, finite-exact theorems, exact
computational/reference results, and their limits for synthetic worlds under a
common physical world and the repository's strong-SEP contract. It is not a
universal theorem about all HLS systems, an empirical result, or a claim that
joint architectures dominate sufficiently coordinated separation.

RQ0 remains:

> Can the dynamic allocation and development of competences in a heterogeneous
> learning system improve long-term system performance compared with
> architectures that manage task allocation and knowledge transfer separately?

The constructive cases below establish **existence YES** under their exact
model and strong-SEP contract. Structural characterization is in progress;
robustness, prevalence, and empirical relevance are not established.

## 1. Scope and common-world contract

Let a finite exact world give every evaluated policy the same state, actions,
reward, opportunity, development, resource, and authorized-information
semantics. The world never branches on a policy label. A history `h` determines
`S(h)`, `q(h)`, and feasible actions. Define the immediate-reward greedy
correspondence:

\[
G(h)=\arg\max_a R(h,a).
\]

All ties are sets. A statement about an on-policy history concerns only a
history that has positive probability under that policy. These common-world
and common-information assumptions are required for the fair policy-class
relation below.

## 2. Policy classes

**Definition — HLS.** `Pi_HLS` is the set of policies that may choose every
operational and development action admissible under the common world and
information contract.

**Definition — strong SEP.**

\[
\Pi_{\mathrm{SEP}}=\{\pi\in\Pi_{\mathrm{HLS}}:
a_\pi(h)\in G(h)\text{ for every positive-probability history under }\pi\}.
\]

Conditional on its actual routing action and realized opportunity, strong
SEP's development manager optimizes development exactly. Routing ties are not
resolved by learner label: they induce the interval
`[J_SEP_min,J_SEP_max]`.

**Definition — SEP-Omega.** SEP-Omega is a separated architecture whose router
receives sufficient exact action-conditioned continuation information. Where
it therefore solves the same Bellman choice as HLS, equality is a coordination
or reducibility boundary, not an independent algorithmic benchmark.

## 3. Policy inclusion

**Theorem 1 — policy inclusion.** Under the common-world and
common-information contract:

\[
\Pi_{\mathrm{SEP}}\subseteq\Pi_{\mathrm{HLS}},
\qquad J_{\mathrm{SEP,max}}(S_0)\le J_{\mathrm{HLS}}(S_0).
\]

**Proof.** Every strong-SEP policy uses the same state, operational actions,
development actions, opportunity physics, costs, and rewards available to
HLS. HLS can imitate its routing and development choices. SEP adds only the
constraint that routing lie in `G(h)`, so it is a subclass. Maximization over a
superset cannot yield a smaller value. ∎

## 4. Exact global reducibility criterion

Let:

\[
\Pi_H^*(S_0)=\arg\max_{\pi\in\Pi_{\mathrm{HLS}}}J_\pi(S_0).
\]

**Theorem 2 — exact reducibility relative to strong SEP.** In the finite exact
setting, where the maxima are attained:

\[
J_{\mathrm{HLS}}(S_0)=J_{\mathrm{SEP,max}}(S_0)
\iff\Pi_H^*(S_0)\cap\Pi_{\mathrm{SEP}}\ne\varnothing.
\]

Equivalently:

\[
J_{\mathrm{HLS}}(S_0)>J_{\mathrm{SEP,max}}(S_0)
\iff\Pi_H^*(S_0)\cap\Pi_{\mathrm{SEP}}=\varnothing.
\]

**Proof.** If an HLS-optimal policy lies in `Pi_SEP`, SEP attains the HLS
value; inclusion gives equality. Conversely, if the intersection is empty,
no SEP policy attains the HLS maximum. Since the finite exact strong-SEP
maximum is attained, it is strictly lower. ∎

**Corollary — unavoidable on-policy non-greediness.** In the same setting,
strict integration holds if and only if every HLS-optimal policy has at least
one positive-probability history on its own support where its routing action is
not in `G(h)`. One fully SEP-admissible HLS optimum is sufficient to eliminate
strict value. This tie semantics is fundamental.

## 5. Local routing-as-teaching Bellman identity

The following is a local proposition, not the global criterion. Suppose at
history `h` that routing action `a` affects only opportunity probability
`p(h,a)`, and that optimized continuation values conditional on no opportunity
and opportunity are action-independent `W_0(h)` and `W_1(h)`. Then:

\[
Q(h,a)=R(h,a)+[1-p(h,a)]W_0(h)+p(h,a)W_1(h).
\]

Define:

\[
D^*(h)=W_1(h)-W_0(h).
\]

For greedy action `g` and alternative `b`:

\[
Q(h,b)-Q(h,g)=-[R(h,g)-R(h,b)]+[p(h,b)-p(h,g)]D^*(h).
\]

Writing `Delta R(h)=R(h,g)-R(h,b)` and
`Delta p(h)=p(h,b)-p(h,g)`:

\[
Q(h,b)-Q(h,g)=-\Delta R(h)+\Delta p(h)D^*(h).
\]

If `g` is uniquely greedy and `Delta p>0`, a local routing inversion occurs
when `Delta p(h) D*(h) > Delta R(h)`.

## 6. Why local inversion is insufficient

Local Bellman inversion does **not** imply strict root integration value. It
establishes only a conditional preference given arrival at a history. A local
inversion may be physically reachable yet absent from every HLS-optimal root
policy, as in the exact `eta=.5` diagnostic world. Constrained-reachability
cost and local inversion gain are different Bellman objects; there is no
general scalar comparison rule between them.

Theorem 2 adds two requirements beyond local inversion: the relevant history
must lie on the support of HLS-optimal policy choices, and no other HLS-optimal
policy may remain fully SEP-admissible.

## 7. Hierarchy of non-separability

The following hierarchy is conceptual terminology. Only level 3 is equivalent
to strict integration under Theorem 2's finite-exact assumptions.

1. **Physical/local non-separability.** A physically reachable state has a
   Bellman-optimal non-greedy routing action. This does not imply `Phi>0`.
2. **Optimal-path non-separability.** Some HLS-optimal policy reaches with
   positive probability a history at which it uses non-greedy routing. This
   still does not suffice if another HLS optimum is SEP-admissible.
3. **Irreducible integration relative to strong SEP.** Every HLS-optimal
   policy needs non-greedy routing somewhere on its own positive-probability
   support. In the finite exact setting this is equivalent to
   `Phi = J_HLS-J_SEP,max > 0`.

```text
local inversion -> on-policy inversion -> unavoidable on-policy inversion.
```

## 8. Optimal-policy selection, not pointwise action sets

It can be useful locally to write:

\[
B(h)=\arg\max_a Q_H(h,a).
\]

Then \(B(h)\cap G(h)\) diagnoses whether a particular history admits a routing
action that is both HLS-Bellman-optimal and immediate-greedy. It is not the
primary global object.

**Observation — SEP-reducibility is an optimal-policy selection property, not
merely a pointwise action-set property.** Selecting a Bellman-optimal action
at one history determines which later histories enter that policy's support.
Independent pointwise selections from \(B(h)\cap G(h)\) need not form one
globally consistent HLS-optimal policy. The reducibility question is whether
\(\Pi_H^*(S_0)\cap\Pi_{\mathrm{SEP}}\) is empty, not merely whether local
intersections are empty.

## 9. SEP-Omega: coordination and information boundary

SEP-Omega can reconstruct HLS where its separated router receives exact
continuation information sufficient to choose the HLS Bellman action. In all
audited exact A1, C1, lambda, and `C(alpha)` families where this was evaluated:

\[
J_{\mathrm{SEP\text{-}Omega}}=J_{\mathrm{HLS}}.
\]

The positive result is relative to the strong-SEP routing contract: separation
can lose value when its router excludes continuation information needed to
value learning opportunity induced by routing. It is not a claim of intrinsic
superiority over every separated architecture.

## 10. Constructive references

### A1 World E — one-step reference

Frozen A1 World E has:

\[
R_g=.80,\quad R_b=.70,\quad p_g=.275,\quad p_b=.80,
\quad W_0=.50,\quad W_1=.88.
\]

Thus `(p_b-p_g)(W_1-W_0)=.525*.38=.1995>.10=R_g-R_b`, and:

\[
J_{\mathrm{HLS}}=1.504>1.4045=J_{\mathrm{SEP,max}}.
\]

The actor is M2 and the optimal opportunity recipient is M1. This is an exact
one-step constructive reference, not a prevalence result.

### C1 R5 — recursive reference

At cycle zero of C1 R5:

\[
R_g=.8,\quad R_b=.6,\quad p_g=0,\quad p_b=1,
\quad W_0=1.6,\quad W_1=1.85.
\]

Hence `(p_b-p_g)(W_1-W_0)=.25>.2=R_g-R_b`, and:

\[
J_{\mathrm{HLS}}=49/20>12/5=J_{\mathrm{SEP,max}}.
\]

HLS routes M2, develops M2 on task 2, then routes M2 again and develops M1
on task 1. This is a reference-gate existence case under its declared
construction, not a phase study or empirical observation.

## 11. Canonical exact family C(alpha)

The frozen zero-sum T2 redistribution family is:

\[
C(\alpha)=
\begin{pmatrix}
4/5 & 4/5-\alpha/5\\
3/5 & 3/5+\alpha/5
\end{pmatrix},\qquad 0\le\alpha\le1.
\]

It keeps global and per-task competence means, T1 rewards, T1 reward gap, and
opportunity primitives fixed. At both tasks:

\[
p(M1)=1/4,\qquad p(M2)=3/4.
\]

The chronology is task 1, then task 2, then terminal task 1. Development
targets task 2 after cycle zero and task 1 after cycle one, with
`eta=3/4`, `kappa=0`, and `beta=1`. Write:

\[
A=4/5-\alpha/5,\qquad B=3/5+\alpha/5.
\]

The 21-point frozen execution preceded the symbolic derivation below; see
[RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md](../experimental_foundations/RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md).

## 12. Exact derivation for C(alpha)

At cycle one, no opportunity gives terminal value `W0=4/5`. With opportunity,
M1 is the unique optimal recipient for task 1:

\[
4/5+\frac34(1-4/5)=19/20>9/10,
\qquad W_1=19/20,
\qquad D^*=3/20.
\]

On the base cycle-one branch `O0=0`:

\[
Q_1(M1)=A+67/80=131/80-\alpha/5,
\]

\[
Q_1(M2)=B+73/80=121/80+\alpha/5,
\]

so:

\[
Q_1(M2)-Q_1(M1)=-1/8+2\alpha/5.
\]

HLS selects M1 below `5/16`, both actions at `5/16`, and M2 above it.

At cycle zero, an opportunity develops M2 on task 2 uniquely:

\[
B^+=B+\frac34(1-B)=9/10+\alpha/20.
\]

The enriched cycle-one value is
`V^+=B^++73/80=29/16+alpha/20`; the base value is:

\[
V_H^0=
\begin{cases}
131/80-\alpha/5,&0\le\alpha\le5/16,\\
121/80+\alpha/5,&5/16\le\alpha\le1.
\end{cases}
\]

The root action M1 is uniquely HLS-optimal throughout. Its `O0=0` and `O0=1`
branches have probabilities `3/4` and `1/4`. Hence:

\[
J_{\mathrm{HLS}}(\alpha)=
\begin{cases}
397/160-11\alpha/80,&0\le\alpha\le5/16,\\
191/80+13\alpha/80,&5/16\le\alpha\le1.
\end{cases}
\]

Strong SEP selects by immediate T2 reward on the base branch:

\[
G_{T2}=
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

At `alpha=1/2`, strong SEP retains the complete routing tie:

\[
J_{\mathrm{SEP,min}}=193/80,
\qquad J_{\mathrm{SEP,max}}=79/32.
\]

Subtracting proves:

\[
\Phi(\alpha)=
\begin{cases}
0,&0\le\alpha\le5/16,\\
3\alpha/10-3/32,&5/16<\alpha<1/2,\\
0,&1/2\le\alpha\le1.
\end{cases}
\]

Therefore `J_HLS > J_SEP,max` if and only if `5/16 < alpha < 1/2`.

## 13. Boundary mechanisms in C(alpha) only

These are exact properties of this family, not a general two-boundary theory.

**Bellman inversion boundary, `alpha_B=5/16`.** For `alpha<1/2`, M1 is
strictly greedy on the base task-2 branch, with:

\[
\Delta R_{T2}=1/5-2\alpha/5,
\qquad \Delta pD^*=\frac12\frac3{20}=\frac3{40}.
\]

At `5/16`, the local Bellman difference is zero. M2 is still strictly
immediate-reward non-greedy; above it M2 becomes Bellman-preferred while
remaining non-greedy until `1/2`.

**Greedy-admissibility boundary, `alpha_G=1/2`.** M2 enters `G_T2`. HLS still
selects M2 on the base branch, but strong SEP may now select the same action.
The closure of `Phi` does not mean continuation value ceased to favor M2. It
means that the strong-SEP routing contract no longer excludes M2.

For `5/16<alpha<1/2`, the root uniquely uses M1 and
`P(O0=0 | a0=M1)=3/4`. On that positive-probability history HLS uniquely uses
M2 while M1 is uniquely greedy. Every HLS-optimal policy must contain that
action; by Theorem 2, no HLS-optimal policy is completely SEP-admissible.

## 14. What C(alpha) proves and does not prove

**Proved for the exact family.** A zero-sum redistribution of T2 competence
can alter continuation values and immediate rankings so that a nonempty open
interval requires routing-as-teaching that is non-greedy under strong SEP.
For larger `alpha`, reducibility returns because the required action becomes
greedy-admissible.

This does **not** mean specialization implies integration, complementarity
forces HLS, increasing heterogeneity increases `Phi`, or any G0+C1--C5 family
has one, unique, or any integration window. A family may have multiple
Bellman boundaries, no greedy-admissibility boundary, non-monotone behavior,
off-policy critical states, multiple HLS optima, development-policy changes,
or no integrated region.

The limited interpretation is: in this canonical family, zero-sum T2
competence redistribution changes continuation values and operational rankings
such that an intermediate region requires non-greedy routing-as-teaching. At
higher `alpha`, strong SEP recovers reducibility because that action becomes
greedy-admissible.

## 15. Open structural characterization problem

The open question is: which properties of world physics, development
correspondences, opportunity dynamics, and the optimal support tree determine
whether:

\[
\Pi_H^*(S_0)\cap\Pi_{\mathrm{SEP}}
\]

is empty? For parameterized families, how does this intersection change with a
parameter and under what hypotheses do open regions of irreducible integration
arise? The `5/16` and `1/2` boundaries of `C(alpha)` are one exactly solvable
specialization, not the general theory.

## 16. Paper-facing theoretical structure

- Policy classes and fair comparison
- Reducibility and strict integration
- Routing as teaching
- Local versus root integration value
- Integration windows
- Exact constructive specialization `C(alpha)`
- Coordination boundary SEP-Omega
- Scope and limitations
