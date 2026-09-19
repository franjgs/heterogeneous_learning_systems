# Minimal HLS Mathematical Model v1

**Status:** CONSOLIDATED (2026-09-19). This is a model-scoped analytical result, not a novelty or general-superiority claim.

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

## 5. Interpretation, scope, and next problem

The fixed orders fail on complementary parameter regions. Operation first is strictly inferior where development has the greater marginal value; development first is strictly inferior where operation has the greater marginal value. Consequently, no fixed priority between these actions is universally optimal in this minimal T=2 model. This is a first existence result in favour of joint management under the stated fixed-priority baselines.

The result does **not** show that joint management dominates every conceivable separated architecture, establish novelty, establish RQ0 in general, or extend beyond T=2. A separated architecture with sufficient coordination or information exchange could reproduce the joint choice. The next theoretical problem is therefore precisely to characterize stronger, genuinely separated policy classes and determine which equality or strict-advantage conditions remain—without adding mechanisms or extending this model in the present work.
