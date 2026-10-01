# G2 --- Dynamic HLS Ground Truth

**Status:** Canonical minimal constructive ground truth for T4--T6<br>
**Theory:** `HLS_DYNAMIC_THEORY.md`<br>
**Purpose:** Null and positive controls for the first dynamic HLS baseline.

## 1. Scope

G2 is not a universal dynamic HLS model. It is a deliberately minimal
2-agent × 2-task × 2-period instrument that realizes the distinctions in
T4--T6 without unnecessary mechanisms.

It uses deterministic learning by doing only as a concrete realization of the
general transition $F$.

## 2. Common model

Two agents $(A_1,A_2)$, two task types $(q_1,q_2)$, and two periods $(t=0,1)$.

$$
S_t=
\begin{pmatrix}
s_{11,t} & s_{12,t}\\
s_{21,t} & s_{22,t}
\end{pmatrix}.
$$

At $t=0$, $q_0=q_1$. The decision is $a_0\in\{1,2\}$, with present reward

$$
R_0(a_0)=s_{a_0 1,0}.
$$

Learning by doing is

$$
s_{ij,1}=s_{ij,0}+\lambda_i\mathbf 1_{\{a_0=i,\,j=1\}},
$$

with saturation at 1 if needed.

At the terminal period there is complete task-dependent routing:

$$
\Pi=\{11,12,21,22\}.
$$

For a state $S$,

$$
\mathcal A(S)=
\{(s_{\pi(1),1},s_{\pi(2),2}):\pi\in\Pi\},
$$

and

$$
\mathcal E(S)=ND[\mathcal A(S)].
$$

Only for T5 is future demand introduced:

$$
P_1=(p,1-p).
$$

Terminal value is

$$
V(S;p)=\max_{(y_1,y_2)\in\mathcal E(S)}\{py_1+(1-p)y_2\}.
$$

For the two present actions,

$$
\Delta^{dev}(p)=V(S_1^{(1)};p)-V(S_1^{(2)};p),
$$

$$
\Delta R=R_0(1)-R_0(2),
$$

and

$$
\boxed{\Delta J(p)=\Delta R+\Delta^{dev}(p).}
$$

## 3. D0 --- No-evolution sanity control

Set

$$
\lambda_1=\lambda_2=0.
$$

Then

$$
S_1^{(1)}=S_1^{(2)},
$$

hence their attainable sets, efficient frontiers, and future values coincide.
This is a consistency test, not a substantive scenario.

## 4. D1 --- Learning without efficient collective-capability change

Use

$$
S_0=
\begin{pmatrix}
0.4 & 0.8\\
0.8 & 0.4
\end{pmatrix},
\qquad
\lambda_1=0.1,\quad\lambda_2=0.
$$

If $A_1$ performs $q_1$,

$$
S_1^{(1)}=
\begin{pmatrix}
0.5 & 0.8\\
0.8 & 0.4
\end{pmatrix}.
$$

If $A_2$ performs it,

$$
S_1^{(2)}=
\begin{pmatrix}
0.4 & 0.8\\
0.8 & 0.4
\end{pmatrix}.
$$

The attainable sets differ, but in both cases

$$
\boxed{\mathcal E^{(1)}=\mathcal E^{(2)}=\{(0.8,0.8)\}.}
$$

Therefore

$$
\boxed{\text{action-dependent learning}
\not\Rightarrow
\text{efficient collective-capability evolution}.}
$$

Moreover $V_1(p)=V_2(p)=0.8$ for all $p$, so $\Delta^{dev}=0$.

D1 is the canonical T4 null.

## 5. D2 --- Capability → value → coupling

Use

$$
S_0=
\begin{pmatrix}
0.7 & 0.8\\
0.8 & 0.6
\end{pmatrix},
\qquad
\lambda_1=0.3,\quad\lambda_2=0.
$$

### Action 1

Present reward:

$$
R_0(1)=0.7.
$$

Future state:

$$
S_1^{(1)}=
\begin{pmatrix}
1.0 & 0.8\\
0.8 & 0.6
\end{pmatrix},
$$

with efficient frontier

$$
\boxed{\mathcal E^{(1)}=\{(1.0,0.8)\}.}
$$

### Action 2

Present reward:

$$
R_0(2)=0.8.
$$

Future state:

$$
S_1^{(2)}=
\begin{pmatrix}
0.7 & 0.8\\
0.8 & 0.6
\end{pmatrix},
$$

with

$$
\boxed{\mathcal E^{(2)}=\{(0.8,0.8)\}.}
$$

Thus T4 is positive:

$$
\mathcal E^{(1)}\neq\mathcal E^{(2)}.
$$

## 6. D2 as T5 ground truth

For $P_1=(p,1-p)$,

$$
V_1(p)=0.8+0.2p,
\qquad
V_2(p)=0.8.
$$

Hence

$$
\boxed{\Delta^{dev}(p)=0.2p.}
$$

At $p=0$, the efficient capabilities differ but

$$
\Delta^{dev}(0)=0.
$$

This is the T5 boundary null:

$$
\boxed{\text{efficient capability difference}
\not\Rightarrow
\text{development value}.}
$$

For every $p>0$,

$$
\Delta^{dev}(p)>0.
$$

Thus the value boundary in this minimal model is $p_V^\star=0$. No interior
T5 threshold is manufactured by restricting the terminal policy class.

## 7. D2 as T6 ground truth

Present operational difference:

$$
\boxed{\Delta R=0.7-0.8=-0.1.}
$$

Therefore

$$
\boxed{\Delta J(p)=-0.1+0.2p.}
$$

The intertemporal indifference point is

$$
\boxed{p_J^\star=0.5.}
$$

The regimes are:

- $p=0$: $\Delta^{dev}=0$, so static comparison suffices.
- $0<p<0.5$: $\Delta^{dev}>0$ but $\Delta J<0$. There is an
  organization--development trade-off without reversal.
- $p=0.5$: exact intertemporal indifference.
- $0.5<p\leq 1$: $\Delta J>0$. The statically preferred action is reversed
  by future development value.

Thus

$$
\boxed{\text{development value/trade-off}
\not\Rightarrow
\text{decision reversal}.}
$$

And D2 provides a constructive case in which sufficiently large future
development value does reverse the static preference.

## 8. Canonical scenario table

| Scenario | $S_0$ | $\lambda_1$ | $\lambda_2$ | Role |
| --- | --- | ---: | ---: | --- |
| D0 | arbitrary | 0 | 0 | no-evolution sanity control |
| D1 | $\begin{pmatrix}0.4 & 0.8\\0.8 & 0.4\end{pmatrix}$ | 0.1 | 0 | attainable change; efficient-capability null |
| D2 | $\begin{pmatrix}0.7 & 0.8\\0.8 & 0.6\end{pmatrix}$ | 0.3 | 0 | T4 capability change → T5 value → T6 trade-off/reversal |

D2 canonical identities:

$$
\boxed{
\Delta R=-0.1,\qquad
\Delta^{dev}(p)=0.2p,\qquad
\Delta J(p)=-0.1+0.2p,\qquad
p_V^\star=0,\qquad
p_J^\star=0.5.
}
$$

## 9. What G2 establishes

G2 constructively supports the scoped logical boundaries:

$$
\text{competence evolution}
\not\Rightarrow
\text{efficient collective-capability evolution},
$$

$$
\text{efficient collective-capability evolution}
\not\Rightarrow
\text{development value},
$$

$$
\text{development value/trade-off}
\not\Rightarrow
\text{decision reversal}.
$$

It also supplies a minimal case where future development value reverses the
statically preferred action.

## 10. What G2 does not establish

G2 does not establish:

- universal learning value;
- universal heterogeneity value;
- superiority of dynamic organization;
- necessity of joint management;
- irreducibility relative to separated or coordinated architectures;
- RQ0;
- prevalence, robustness, or empirical relevance;
- a universal dynamic HLS model.

G2 is the dynamic null/reference baseline, analogous in role to G1 for the
static block.
