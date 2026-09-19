# Minimal HLS model: v1, equivalence boundary, and coordination result

**Status:** CONSOLIDATED (2026-09-19). Sections 1–5 retain minimal model v1 and its fixed-priority result. Sections 6–9 consolidate the subsequent additive-equivalence and operation-dependent development results. Both propositions are DERIVED-IN-MODEL; neither establishes novelty or general superiority.

## 1. Purpose

This document fixes the smallest Heterogeneous Learning Systems (HLS) model used to ask whether jointly choosing operational allocation and competence development can improve expected long-term operational value relative to two specified, fixed-priority separated architectures. It does not introduce an algorithm, a new HLS mechanism, or a claim about all separated architectures.

It instantiates [hls_ontology.md](../hls_ontology.md): competence is a state, work is an action-realized quantity, experience is exposure, development is a decision, and operational value is the objective contribution. None is identified with another outside the explicit maps below.

## 2. Model

There are two agents, one competence, and two decision periods:

\[
\mathcal M=\{1,2\}, \qquad t\in\{1,2\}.
\]

The scalar competence state of agent \(m\), at the start of period \(t\), is \(S_{m,t}\geq0\). The exogenous operational workload is \(D_t\geq0\), and each agent has time-invariant capacity \(b_m>0\). The decisions are operational allocation \(a_{m,t}\geq0\) and competence-development allocation \(d_{m,t}\geq0\):

\[
u_t=(\mathbf a_t,\mathbf d_t).
\]

They obey

\[
a_{m,t}+d_{m,t}\leq b_m, \qquad \sum_{m\in\mathcal M}a_{m,t}\leq D_t.
\]

Thus operation and development use the same capacity. The model has no additional resource cost: the opportunity cost of development is already its use of capacity and is not counted again.

### Ontology-realization maps

For this deliberately linear one-competence realization,

\[
W_{m,t}=a_{m,t}, \qquad \bar Q_{m,t}=S_{m,t}, \qquad Y_t=\sum_{m\in\mathcal M}S_{m,t}a_{m,t}.
\]

Here \(W_{m,t}\) is operational work, \(\bar Q_{m,t}\) is *expected* quality, and \(Y_t\) is additive operational value. This is a chosen competence-to-expected-quality and work/quality-to-value realization; it does not mean \(S=\bar Q=Q=W=Y\). In particular, the model has no observed-quality variable \(Q\).

Learning-relevant exposure is

\[
E^{dir}_{m,t}=a_{m,t}, \qquad E^{ind}_{m,t}=d_{m,t},
\]

and competence evolves as

\[
S_{m,t+1}=S_{m,t}+\eta_m a_{m,t}+\lambda_m d_{m,t}, \qquad \eta_m,\lambda_m\geq0.
\]

Thus \(d\) is neither indirect experience nor competence change: it generates the former, which enters the displayed transition to generate the latter. No saturation, forgetting, interference, noise, cross-agent transfer, or terminal competence reward is present.

The objective is

\[
J(\pi)=\mathbb E_\pi[Y_1+Y_2].
\]

Since \(d_{m,2}\) can affect neither \(Y_1\) nor \(Y_2\), choosing \(d_{m,2}^*=0\) is optimal. (Other values can be weakly tied only if unused capacity is costless; this document adopts the zero-development representative.)

## 3. Policies compared

The joint policy \(\pi_J\) chooses \(\mathbf a_t\) and \(\mathbf d_t\) simultaneously under the same feasibility constraints, dynamics, demand, information, horizon, and objective:

\[
\pi_J\in\arg\max_\pi J(\pi).
\]

The comparison baselines are not all possible modular architectures. They are two fixed-priority sequential rules for period 1; the lower-priority action can use only capacity left by the higher-priority one. In period 2, the adopted zero-development convention leaves capacity for operation.

- **Operation first (\(A\mathbin{\to}D\)).** Reserve each agent's period-1 capacity for operation: \(a_{m,1}=1,d_{m,1}=0\) in the normalized case. Development is considered only on residual capacity, which is zero.
- **Development first (\(D\mathbin{\to}A\)).** Reserve each agent's period-1 capacity for development: \(d_{m,1}=1,a_{m,1}=0\) in the normalized case. Operation is considered only on residual capacity, which is zero.

This explicit fixed-priority/tie convention is necessary. If an upstream subproblem has a zero-valued action, an unconstrained sequential argmax alone does not determine how a tie is resolved; the formula below is for the stated priority rules.

## 4. T=2 derivation

For the closed form, impose \(b_1=b_2=1\). Assume period 1 has enough demand to operate both agents, and period 2, when an operational opportunity occurs, also has enough demand to operate both agents. Let that period-2 opportunity occur with probability \(p\in[0,1]\). Equivalently, conditional period-2 value is weighted by \(p\) in the expected objective. These full-demand assumptions remove cross-agent demand coupling; they are not claims about general HLS demand.

With \(d_{m,2}=0\), one unit of agent \(m\)'s period-1 capacity allocated to operation yields current value \(S_{m,1}\) and expected period-2 learning value \(p\eta_m\). One unit allocated to development yields no current operational value and expected period-2 value \(p\lambda_m\). Define

\[
V_m^A=S_{m,1}+p\eta_m, \qquad V_m^D=p\lambda_m.
\]

For any full use of agent \(m\)'s period-1 capacity, write \(d_{m,1}=1-a_{m,1}\). Its expected contribution is

\[
\begin{aligned}
S_{m,1}a_{m,1}+p\bigl(S_{m,1}+\eta_m a_{m,1}+\lambda_m d_{m,1}\bigr)
=pS_{m,1}+a_{m,1}V_m^A+(1-a_{m,1})V_m^D.
\end{aligned}
\]

The common constant \(pS_{m,1}\) is present under either period-1 use. Hence the joint policy chooses the larger marginal value:

\[
(a_{m,1}^J,d_{m,1}^J)=(1,0) \text{ if } V_m^A>V_m^D, \qquad (0,1) \text{ if } V_m^D>V_m^A,
\]

and every mixture is optimal if \(V_m^A=V_m^D\). Therefore

\[
J_J=\sum_m\left(pS_{m,1}+\max\{V_m^A,V_m^D\}\right).
\]

The two fixed-priority policies have, respectively,

\[
J_{A\to D}=\sum_m(pS_{m,1}+V_m^A), \qquad J_{D\to A}=\sum_m(pS_{m,1}+V_m^D).
\]

Subtracting gives the verified identities

\[
\boxed{J_J-J_{A\to D}=\sum_m[V_m^D-V_m^A]_+}, \qquad
\boxed{J_J-J_{D\to A}=\sum_m[V_m^A-V_m^D]_+},
\]

where \([x]_+=\max\{x,0\}\).

### Equality and strict advantage

For \(A\to D\), equality holds exactly when \(V_m^D\leq V_m^A\) for every \(m\), and strict advantage holds exactly when

\[
\exists m:\ V_m^D>V_m^A,
\]

that is, \(p\lambda_m>S_{m,1}+p\eta_m\) for at least one agent.

For \(D\to A\), equality holds exactly when \(V_m^A\leq V_m^D\) for every \(m\), and strict advantage holds exactly when

\[
\exists m:\ V_m^A>V_m^D.
\]

## 5. Interpretation and scope of v1

The fixed orders fail on complementary parameter regions. Operation first is strictly inferior where development has the greater marginal value; development first is strictly inferior where operation has the greater marginal value. Consequently, no fixed priority between these actions is universally optimal in this minimal T=2 model. This is a first existence result in favour of joint management under the stated fixed-priority baselines.

The result does **not** show that joint management dominates every conceivable separated architecture, establish novelty, establish RQ0 in general, or extend beyond T=2. The stronger comparison below makes the possibility of reproducing the joint choice precise.

## 6. Proposition 1 — Equivalence boundary under additive separability

### Hypotheses and architecture

Consider one normalized agent/capacity block in the reduced T=2 problem of section 4, suppressing its agent and time indices:

\[
J(a,d)=C+V^A a+V^D d,\qquad
a\geq0,\quad d\geq0,\quad a+d\leq1.
\]

Here \(C\) is independent of the decisions and \(V^A,V^D\geq0\), as inherited from v1. For that block, \(C=pS_{m,1}\), \(V^A=S_{m,1}+p\eta_m\), and \(V^D=p\lambda_m\). With the sufficient-demand assumptions in section 4, these blocks add across the two agents.

A stronger separated architecture can choose an optimal prior resource share \(\rho\in[0,1]\) using both marginal values, then execute

\[
a=\rho,\qquad d=1-\rho,\qquad
J_S(\rho)=C+\rho V^A+(1-\rho)V^D.
\]

This grants the resource allocator optimal coordination; separate execution of the two activities does not imply separate decision criteria for choosing their resource shares. It is stronger than either fixed priority in section 3.

### Conclusion

\[
\boxed{J_S^*:=\max_{\rho\in[0,1]}J_S(\rho)
      =J_J^*:=\max_{a,d\geq0,\ a+d\leq1}J(a,d)
      =C+\max\{V^A,V^D\}.}
\]

### Proof

Set \(M=\max\{V^A,V^D\}\geq0\). Every feasible pair satisfies

\[
V^A a+V^D d\leq M(a+d)\leq M.
\]

The bound is attained by \((1,0)\) when \(V^A\geq V^D\), and by \((0,1)\) when \(V^D\geq V^A\). The separated architecture attains those same endpoints with \(\rho=1\) or \(\rho=0\). If \(V^A=V^D\), every share attains the optimum. If both vanish, slack capacity is also optimal in the joint feasible set. This proves equality. \(\square\)

**Assumption audit.** Nonnegativity is inherited from v1, rather than an additional physical mechanism. Omitting a sign condition would make the displayed optimum false for two negative marginal values: on the triangle it would be \(C+\max\{0,V^A,V^D\}\), whereas the full-capacity share forces one of those negative contributions. The proposition therefore states the inherited signs explicitly.

**Interpretation.** Operation, development, and competition for capacity alone do not require joint decision making to attain the optimum. Under this additive structure, optimal resource allocation followed by separate execution suffices. This is an equivalence boundary for the HLS comparison, not a negative result for HLS.

## 7. Minimal extension and corrected separate decision criteria

### Only physical change: operation-dependent indirect experience

In v1, \(E^{ind}=d\) does not depend on operational activity. The extension replaces only this exposure map with

\[
E^{ind}=ad.
\]

Here \(a\) and \(d\) are normalized capacity allocations in the same reduced block. The product represents indirect exposure that requires both operational activity and a development action during the period; it does not assert a detailed within-period schedule. Exposure is expressed in normalized exposure units. Neither the development decision nor the work performed is identified with experience or competence.

Keeping direct exposure and the linear experience-to-competence law gives the same T=2 reduction with the substitution

\[
S_{m,2}=S_{m,1}+\eta_m a+\lambda_m ad,
\qquad
J(a,d)=C+Va+Lad,
\]

where \(C=pS_{m,1}\), \(V=S_{m,1}+p\eta_m\), and \(L=p\lambda_m\). The regime studied here has \(V>0,L>0\). These are reduced coefficients, not new fundamental HLS variables: \(C\) is a constant value contribution, not resource cost; \(V\) is a coefficient, not the ontology's value mapping; \(L\) is a coefficient, not latency or the competence-transition function. All objective terms have the same operational-value units. The shared constraint remains \(a,d\geq0,\ a+d\leq1\); demand, capacity, horizon, operational-value mapping, and absence of terminal competence reward are unchanged.

### Discarded formulation and its correction

An intermediate formulation gave both managers the global objective \(J(a,d)\), each maximizing it with respect to its own variable while holding the other fixed. That formulation is **discarded as a definition of strict separate management**: it separates execution of optimization steps while supplying both decision makers with the global criterion.

The corrected local objectives are

\[
J_A(a)=Va,\qquad J_D(d;a)=Lad.
\]

They are distinct objective functions, \(J_A\neq J_D\neq J\), although their numerical values may coincide at particular points. The operational manager does not optimize the indirect-learning term. The development manager knows the physical exposure technology \(ad\) and the current \(a\), but optimizes only its development contribution. Global performance of every resulting allocation is still evaluated with the same physical \(J\); local optimization objectives are not extra system rewards.

The two managers control \(a\) and \(d\), not the two physical agents of v1. Each unilateral deviation must respect the other's fixed allocation and the shared capacity constraint. Thus a separated equilibrium means a feasible pair of mutual best responses:

\[
a\in\arg\max_{0\leq x\leq1-d}Vx,\qquad
d\in\arg\max_{0\leq y\leq1-a}Lay.
\]

This is an equilibrium definition with shared constraints, not an assumed iterative algorithm or a convergence claim. In this particular model, the discarded common-objective formulation happens to yield the same best responses: its operational slope is \(V+Ld>0\), while its development slope is \(La\). That coincidence does not make its decision criteria a valid definition of strict separation.

## 8. Proposition 2 — Coordination/selection under operation-dependent competence development

### Hypotheses

Use precisely the physical objective, shared feasible set, and corrected local objectives in section 7. Assume \(0<V<L\). Write \(J_S(a):=J(a,1-a)\) for the **global performance** of a separated equilibrium, distinct from either local objective.

### Conclusion

1. The separated equilibria with positive operational activity form the continuum
   \[
   \mathcal E_S=\{(a,1-a):0<a\leq1\}.
   \]
2. The joint optimum over the full feasible triangle is unique and lies in the interior of the full-capacity segment:
   \[
   a_J^*=\frac{V+L}{2L},\qquad
   d_J^*=\frac{L-V}{2L},\qquad
   J_J^*=C+\frac{(V+L)^2}{4L}.
   \]
   Both activities are positive; the point is on the triangle's capacity boundary, not in its two-dimensional interior.
3. At every equilibrium in \(\mathcal E_S\),
   \[
   \boxed{J_J^*-J_S(a)=L(a-a_J^*)^2\geq0.}
   \]
4. Equality holds exactly at \(a=a_J^*\). In particular,
   \[
   (a_J^*,d_J^*)\in\mathcal E_S,\qquad
   \max_{(a,d)\in\mathcal E_S}J(a,d)=J_J^*.
   \]

### Proof

For fixed \(d\in[0,1]\), \(V>0\) gives the unique operational best response

\[
BR_A(d)=1-d.
\]

For fixed \(a>0\), \(La>0\) gives the unique development best response

\[
BR_D(a)=1-a.
\]

Every pair \((a,1-a)\) with \(0<a\leq1\) satisfies both responses, and the first response forces every positive-activity equilibrium to have this form.

For joint optimization at any \(a>0\), increasing \(d\) raises \(J\), so the joint optimizer uses \(d=1-a\). Points with \(a=0\) have value \(C\), strictly below the feasible value \(C+V\) at \((1,0)\); they cannot be joint optima. It suffices to maximize

\[
f(a):=J(a,1-a)=C+(V+L)a-La^2,\qquad 0\leq a\leq1.
\]

Its derivatives are

\[
f'(a)=V+L-2La,\qquad f''(a)=-2L<0.
\]

The unique stationary point is \(a_J^*=(V+L)/(2L)\). Under \(0<V<L\), it satisfies \(1/2<a_J^*<1\), so it is the unique maximizer on the segment; \(d_J^*=1-a_J^*>0\). The preceding reduction establishes uniqueness on the full feasible triangle.

Completing the square yields the exact identity

\[
f(a)=C+\frac{(V+L)^2}{4L}
       -L\left(a-\frac{V+L}{2L}\right)^2.
\]

This proves the optimal value and gap formula. Since \(L>0\), the gap vanishes only at \(a_J^*\), which itself belongs to the separated equilibrium continuum. \(\square\)

### Boundary and degeneracy audit

At **\(V=L>0\)**, the stationary point reaches \(a_J^*=1,d_J^*=0\). The joint optimum remains unique, but is no longer an interior split. The exact formula becomes

\[
J_J^*=C+L,\qquad J_J^*-J_S(a)=L(1-a)^2.
\]

At **\(a=0\)**, \(J_D(d;0)=0\) for every feasible \(d\), hence \(BR_D(0)=[0,1]\) is set-valued. The operational best response is zero only if \(d=1\), so \((0,1)\) is the sole additional, degenerate mutual-best-response equilibrium. Other feasible pairs \((0,d)\) are not equilibria. The full equilibrium set is therefore \(\mathcal E_S\cup\{(0,1)\}\). The degenerate point has global value \(C\), and the completed-square identity remains exact there. This endpoint is not needed to establish multiplicity or the positive-activity selection problem.

## 9. Current interpretation and exact limits

Proposition 1 establishes equality with a separated architecture that can optimize the prior resource share. Proposition 2 uses a different, explicit decision structure: two local objectives with no rule selecting among their mutual best responses. These two comparators must not be conflated.

With operation-dependent development, the local best-response conditions permit many allocations and do not specify which equilibrium is selected. Joint optimization identifies one optimal split under \(0<V<L\). Selecting another separated equilibrium incurs exactly \(L(a-a_J^*)^2\), but the joint optimum remains an available separated equilibrium. Thus the result concerns selection, **not** a strict gap between the joint optimum and the best separated equilibrium. No average loss, probability of selecting a suboptimal equilibrium, convergence property, or necessary failure of decentralized control is established.

The interaction \(E^{ind}=ad\) invalidates the additive decomposition used in Proposition 1; it does not preclude a sufficiently coordinated resource allocator from choosing the same optimal split. Separation of physical execution, separation of optimization steps, and separation of decision objectives are different properties. HLS is not established as the only mechanism capable of selecting the optimum.

Additional decentralized coordination through incentives or internal prices could potentially select that point. Such mechanisms have not been studied here, and none is specified or validated by these propositions. Their ability to select the optimum remains an open issue for a later task. The present consolidation ends with these T=2 results; it makes no novelty, empirical, or universal decentralized-architecture claim and does not change RQ0.

## 10. Proposition 3 — Nonlocal information under complementary competences

### Hypotheses

Consider a separate reduced T=2 block with two complementary competence states

\[
S_1,S_2\in[0,1].
\]

At period 2, an operational task arrives with probability \(p\in(0,1]\), has value
\(R>0\), and requires both competences. Its expected operational value is

\[
V_2(S_1,S_2)=pRS_1S_2.
\]

At period 1, one normalized capacity unit is divided between operation and
development:

\[
a+d=1,\qquad a,d\geq0,
\]

with immediate operational value \(Va\), \(V>0\), and state transition

\[
S_{1,2}=S_{1,1}+\lambda d,\qquad S_{2,2}=S_{2,1},\qquad \lambda>0.
\]

To retain the declared state space for every feasible \(d\), assume

\[
S_{1,1}+\lambda\leq1.
\]

The development decision changes \(S_1\), while \(S_2\) is the distinct,
complementary competence whose value must be known. This is a scalar
realization of the ontology's competence vector, not a replacement of the v1
one-competence model.

### Conclusion

The joint objective is

\[
\max_{0\leq d\leq1}
\left\{V(1-d)+pR(S_{1,1}+\lambda d)S_{2,1}\right\}.
\]

Let

\[
S_2^*=\frac{V}{pR\lambda}.
\]

Then

\[
d_J^*(S_2)=
\begin{cases}
1, & pR\lambda S_2>V,\\
0, & pR\lambda S_2<V,
\end{cases}
\]

and every \(d\in[0,1]\) is optimal at equality. If admissible states satisfy

\[
S_2^-<S_2^*<S_2^+,
\]

then the joint action is \(0\) at \(S_2^-\) and \(1\) at \(S_2^+\).

For a development manager facing the local net criterion

\[
\max_{0\leq d\leq1}(\tau-V)d,
\]

no incentive \(\tau\) that is independent of \(S_2\) implements both strict
joint actions. The state-dependent incentive

\[
\boxed{\tau^*(S_2)=pR\lambda S_2}
\]

does implement them, including the same indifference at the threshold. It is
the competence-development increment times the marginal future operational
value:

\[
\frac{\partial V_2}{\partial S_1}=pRS_2,
\qquad
\tau^*(S_2)=\lambda\frac{\partial V_2}{\partial S_1}.
\]

The complementarity is strict:

\[
\frac{\partial^2V_2}{\partial S_1\partial S_2}=pR>0.
\]

### Proof

Substitution of \(a=1-d\) makes the joint objective affine in \(d\), with
slope

\[
-V+pR\lambda S_2.
\]

Its sign gives the displayed endpoint solution and equality case. A local
criterion with an \(S_2\)-independent \(\tau\) has the same slope
\(\tau-V\) in the two admissible states, so it cannot choose \(d=0\) in one
and \(d=1\) in the other. Setting \(\tau= pR\lambda S_2\) makes the local
slope equal to the joint slope pointwise. The derivatives of \(pRS_1S_2\)
give the two displayed marginal-value identities. \(\square\)

### Interpretation and limitation

This proposition establishes an information requirement for this local pricing
rule: the correct development incentive depends on a competence other than the
one being developed. It does not establish that decentralized coordination is
impossible or that joint management is strictly superior. A price carrying that
state information reproduces the joint choice exactly. The result also does not
claim that every decentralized design must expose \(S_2\) directly; it only
rules out the stated constant marginal incentive across the two states.

## 11. T=3 continuation-policy boundary

This separate reduced block extends only the horizon to test whether a
decentralizing price can depend on an endogenous continuation decision. It is a
frontier result, not a superiority theorem.

### Assumptions and domain

Retain the complementary terminal operational value, now realized at period 3
when its task arrives with probability \(p\in(0,1]\),

\[
Y_3=RS_{1,3}S_{2,3}.
\]

At period 2, the continuation controller selects \(x\in[0,1]\). Its
operational use is \(1-x\), with value \(K(1-x)\), \(K>0\), and its
development changes the second competence:

\[
S_{2,3}=S_{2,2}+\mu x,\qquad
S_{1,3}=S_{1,2},\qquad \mu>0.
\]

The expected continuation value is therefore

\[
\begin{aligned}
V_2(S_1,S_2)
&=\max_{0\leq x\leq1}\{K(1-x)+pRS_1(S_2+\mu x)\}\\
&=pRS_1S_2+\max\{K,pR\mu S_1\}.
\end{aligned}
\]

For all feasible actions to preserve \(S_1,S_2\in[0,1]\), assume

\[
S_{1,1}+\lambda\leq1,\qquad S_{2,2}+\mu\leq1.
\]

These are feasibility assumptions for the bounded-state realization, not
additional learning mechanisms. They also require initial states in \([0,1]\).

### Derivation of the continuation policy

The term optimized over \(x\) is affine, with slope

\[
pR\mu S_1-K.
\]

Define

\[
S_1^\dagger=\frac{K}{pR\mu}.
\]

Then

\[
x^*(S_1)=
\begin{cases}
0, & pR\mu S_1<K,\\
1, & pR\mu S_1>K,
\end{cases}
\]

and every \(x\in[0,1]\) is optimal when \(S_1=S_1^\dagger\). The threshold
is decision-relevant only if it lies in the admissible \([0,1]\) state range;
otherwise the same formula gives a constant endpoint continuation policy over
that range.

Away from the indifference point, differentiating the two smooth branches gives

\[
\frac{\partial V_2}{\partial S_1}=
\begin{cases}
pRS_2, & S_1<S_1^\dagger,\\
pR(S_2+\mu), & S_1>S_1^\dagger.
\end{cases}
\]

At \(S_1=S_1^\dagger\), \(V_2\) has a kink and is not differentiable. Its
subgradient interval is

\[
\partial_{S_1}V_2=
\bigl[pRS_2,\;pR(S_2+\mu)\bigr].
\]

### Period-1 incentive and interpretation

At period 1, retain

\[
S_{1,2}=S_{1,1}+\lambda d,
\]

and the joint problem

\[
\max_{0\leq d\leq1}\{V(1-d)+V_2(S_{1,1}+\lambda d,S_2)\}.
\]

Away from the continuation threshold, the decentralizing marginal incentive is

\[
\boxed{
\tau_1^*
=\lambda\frac{\partial V_2}{\partial S_1}
=\lambda pR\,[S_2+\mu x^*(S_{1,2})].
}
\]

At the threshold, the corresponding price is set-valued:

\[
\tau_1^*\in
\lambda\bigl[pRS_2,\;pR(S_2+\mu)\bigr],
\]

consistent with the continuation controller's indifference over \(x\). The
formula shows that the period-1 marginal incentive incorporates which
continuation action is optimal. It does not require a claim that an entire
Bellman value function must be communicated: here the required continuation
information reduces to one explicit threshold, or equivalently the relevant
branch gradient.

### Provisional boundary and next recorded audit

Increasing the horizon alone does not make joint management necessary. In this
model, once \(S_1^\dagger\) is known, a separated coordinator can implement the
same continuation-aware price with an extremely simple threshold rule. The
result demonstrates dependence on a continuation policy, not irreducible
complexity, a strict joint-management advantage, or a need to solve a general
Bellman problem at execution time.

The next task, not undertaken here, is an adversarial audit of whether any of
these previously excluded mechanisms creates a dependency that does not reduce
immediately to another simple price or threshold:

- **A.** changing or uncertain future demand;
- **B.** several agents with alternative competences, where development changes
  subsequent use, development, or knowledge-source choices;
- **C.** learning by doing, where operational allocation \(a_t\) generates
  direct experience and changes future competences.

This is only a recorded question. No mechanism A/B/C is added, analysed, or
claimed in the present model.

## 12. Methodological role of the derived boundaries

The results in this document are useful constraints on the programme, not
grounds to discard the HLS phenomena they simplify. They show, within their
stated reduced models, that simple operation-development competition can be
additively separable; an operation-transfer interaction can be decentralized by
a state-dependent price; complementary competences create portfolio-dependent
value even though sufficiently informed coordination can recover the optimum;
and a continuation-aware price or sufficiently rich contract can overcome the
specific marginal-price limitation exposed by routing boundaries. Thus joint or
central management has no intrinsic superiority over a perfectly coordinated
modular architecture in these cases.

The common lesson is constructive: competence development has a continuation
value that can depend on the rest of the portfolio and on future decisions.
Information needed for that value, computational effort to obtain it, and
communication needed to coordinate action are distinct quantities; a count of
communicated bits alone is not a measure of coordination difficulty.

The earlier M0 minimal intervention model supplies a complementary
DERIVED-IN-MODEL margin identity:

\[
g(q)=N_q[\lambda_q-m(q)]_+-\kappa_q.
\]

Under its stated assumptions, it makes the value of learning depend jointly on
the operational margin, future use, learnability, and learning cost. In the
M0 notation this is the same reduced form as
\(-K_z+A_Hp_z\ell_z[g_z-m_z]_+\): \(N_q\) compresses future use,
horizon, and learnability; \(\lambda_q\) is the conditional competence gain;
\(m(q)\) is the operational margin; and \(\kappa_q\) is learning cost. With
generalization across competences, that value becomes a portfolio property and
interventions can be complementary. Static specializations of such allocation
problems can sometimes reduce to established combinatorial optimization. Each
such reduction is a boundary of sufficiency and a potential source of rigorous
methods, not an automatic reason to abandon the HLS phenomenon.

No generalization mechanism, combinatorial reduction, routing contract, or
additional coordination architecture is derived in this document. These are
methodological consequences and constructive routes for later work, with their
own ontology mappings, assumptions, and audits required.
