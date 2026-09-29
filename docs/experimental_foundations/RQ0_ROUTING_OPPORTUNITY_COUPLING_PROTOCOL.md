# RQ0 Routing--Opportunity Coupling — Frozen Dynamic Family

STATUS: EXECUTED — 21/21 SEP-REDUCIBLE / POST-RUN OUTCOME RECORDED

## Purpose

This protocol isolates one physical intervention in the existing G0/C1
semantics: the action-conditioned contrast in development-opportunity
probability.  It is neither an A1 repetition nor a parameter search for an
HLS win.  It evaluates whether a fixed, repeated
operation--opportunity--development feedback topology changes between the
following root-policy classes:

- **SEP-reducible:** an HLS-optimal policy exists whose routing is
  immediate-reward greedy on every positive-probability on-policy history;
- **HLS-integrated:** every HLS-optimal policy uses a non-greedy routing action
  on at least one such history and
  \(\Phi=J_{\mathrm{HLS}}-J_{\mathrm{SEP,max}}>0\).

RQ0 remains open regardless of the result.

## Frozen common world

The family has two learners, two competence/task dimensions, two operational
cycles, and terminal use:

```text
S0 -- q0=1, O0, d0(target=2) --> S1
   -- q1=2, O1, d1(target=1) --> S2
   -- terminal operational use qT=1.
```

The common primitives are frozen before evaluating any `lambda` point:

| Primitive | Frozen value | Basis |
| --- | --- | --- |
| learners/tasks | `M1,M2` / `1,2` | minimal existing C1 topology |
| initial competence | `((0.80,0.80),(0.60,0.60))` | C1 reference-world common state |
| task sequence / terminal task | `(1,2)` / `1` | C1 reference-world chronology |
| development targets | `{0: 2, 1: 1}` | C1 reference-world chronology |
| development rule | saturating \(c'=c+.75(1-c)\) | C1 convention |
| `eta` | `.75` | C1 convention |
| development cost | `kappa=0` | C1 convention |
| discount | `beta=1` | C1 convention |
| persistent budget | absent | A1/C1 minimal resource control |
| interactions | absent (`Gamma=0`) | independent-development control |
| reward | \(R(S,q,i)=c_{iq}\) | G0 competence reward model |
| mean opportunity | \(m_1=m_2=.5\) | existing RQ0 campaign baseline |
| opportunity contrast | \(\epsilon_1=\epsilon_2=.5\) | explicit non-extreme symmetric design choice |

The contrast is an explicit design choice, not a fitted value.  It fixes
executor primitives to `.25` and `.75` at both tasks, so neither the primitives
nor the resulting probabilities use the `0/1` construction of C1 R5.

## Sole intervention

For each task \(k\), the A1 mixture kernel receives

\[
\bar e_k=m_k,
\qquad e_{M1,k}=m_k-\epsilon_k/2,
\qquad e_{M2,k}=m_k+\epsilon_k/2,
\qquad \rho=\lambda.
\]

Therefore

\[
p_\lambda(M1,k)=m_k-\lambda\epsilon_k/2,
\qquad
p_\lambda(M2,k)=m_k+\lambda\epsilon_k/2,
\]

and

\[
\Delta p_k(\lambda)=\lambda\epsilon_k,
\qquad
\frac{p_\lambda(M1,k)+p_\lambda(M2,k)}{2}=m_k.
\]

No other world primitive may change with `lambda`.

## Exact evaluation and interpretation

The predeclared grid is

\[
\lambda\in\{0,.05,.10,\ldots,1.00\}.
\]

Every point is solved exactly with the existing HLS, strong-SEP, and
SEP-Omega solvers.  For each HLS-optimal positive-probability state, the run
records the immediate-greedy and HLS-optimal action sets, opportunity
probabilities, and the exact conditional branch values

\[
W_o(s)=\max_d\{-K(d)+\beta V(T(s,o,d))\},
\qquad D^*(s)=W_1(s)-W_0(s).
\]

The local Bellman identity is diagnostic only:

\[
Q(b)-Q(g)=-\Delta R+\Delta p(\lambda)D^*(\lambda).
\]

The scientific regime boundary is instead the root-policy quantity

\[
\Phi(\lambda)=J_{\mathrm{HLS}}(S_0)-J_{\mathrm{SEP,max}}(S_0).
\]

No grid point, frozen primitive, tolerance, or interpretation rule may be
changed after this one execution.  A null result is a result for this family,
not a statement of universal G0+C1--C5 separability.

## POST-RUN OUTCOME

The frozen 21-point grid was executed exactly once. Every point was
SEP-reducible:

\[
\Phi(\lambda)=J_{\mathrm{HLS}}-J_{\mathrm{SEP,max}}=0
\]

at all 21 declared `lambda` values, and `J_HLS = J_SEP-Omega` throughout.
No physical primitive, grid point, tolerance, or policy contract was changed
after this outcome. The machine-readable record is
[summary.json](../../results/foundations/rq0_routing_opportunity_coupling/summary.json)
with its accompanying
[manifest.json](../../results/foundations/rq0_routing_opportunity_coupling/manifest.json).

This is a null result for this frozen coupling family only. A later, separate
zero-sum competence-redistribution intervention is documented in
[RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md](RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md);
it did not revise this protocol or its outcome.
