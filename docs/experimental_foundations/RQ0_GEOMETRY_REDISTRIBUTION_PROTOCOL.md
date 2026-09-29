# RQ0 Zero-Sum T2 Competence Redistribution

## Epistemic status

This record separates the frozen intervention from its subsequent exact
execution and analysis. It is a controlled synthetic result under the stated
world physics and the strong-SEP contract. It is not an empirical result and
does not establish prevalence beyond this family.

## PRE-RUN FROZEN PROTOCOL

### Motivation and scope

The preceding frozen routing--opportunity coupling family held the competence
matrix fixed and found `Phi = 0` at all 21 predeclared coupling points. The
present intervention was defined to test competence geometry while preserving
the resulting opportunity primitives, rather than increasing coupling or
searching for a positive result.

It uses the same exact two-cycle G0/C1 topology:

```text
S0 -- q0=1, O0, d0(target=2) --> S1
   -- q1=2, O1, d1(target=1) --> S2
   -- terminal use qT=1.
```

The sole varying primitive is the initial competence matrix:

\[
C(\alpha)=
\begin{pmatrix}
0.8 & 0.8-0.2\alpha\\
0.6 & 0.6+0.2\alpha
\end{pmatrix},
\qquad \alpha\in\{0,.05,.10,\ldots,1\}.
\]

This is a zero-sum redistribution of T2 competence from M1 to M2. It keeps
global competence mean, each task mean, and global range fixed. It must not be
described as a generic intervention of “specialization.”

### Frozen physical invariants

All quantities below are invariant in `alpha`:

| Primitive | Frozen value |
| --- | --- |
| learners/tasks | `M1,M2` / `1,2` |
| routing tasks / terminal task | `(1,2)` / `1` |
| opportunity mixture | `rho=lambda=1`, baseline `.5` for both tasks |
| executor opportunity values | M1 `.25`, M2 `.75`, for both tasks |
| opportunity probabilities | `p(M1,k)=.25`, `p(M2,k)=.75` |
| development targets | `t=0 -> 2`, `t=1 -> 1` |
| development | saturating update with `eta=.75` |
| development cost / discount | `kappa=0`, `beta=1` |
| resources / interactions | no persistent budget; `Gamma=0` |
| information / randomness | common full information; deterministic exact evaluation |

In particular, executor opportunity values are frozen primitives of the
kernel; they are not derived from `C(alpha)`.

For every `alpha`, the following were required as intervention audits:

\[
\bar C=\bar C_{T1}=\bar C_{T2}=0.7,
\qquad \operatorname{range}(C)=0.2.
\]

T1 is fixed:

\[
R(M1,T1)=0.8,\quad R(M2,T1)=0.6,\quad \Delta R_{T1}=0.2,
\quad \mathcal G(T1)=\{M1\}.
\]

### Metrics and decision semantics

Each point must report exact `J_HLS`, `J_SEP_min`, `J_SEP_max`,
`J_SEP-Omega`, and

\[
\Phi(\alpha)=J_{\mathrm{HLS}}-J_{\mathrm{SEP,max}}.
\]

It must retain complete immediate-greedy and HLS-optimal action sets. An
immediate routing tie cannot be resolved by learner label. The global labels
are:

- **SEP-reducible:** `Phi=0` and at least one HLS-optimal policy is
  strong-SEP-admissible on all positive-probability on-policy histories.
- **HLS-integrated:** `Phi>0` and every HLS-optimal policy contains at least
  one non-greedy routing action on such a history.

The local quantity `Delta p * D*` is diagnostic only; it does not replace the
root-policy criterion. No point may be added adaptively and no parameter may
be changed after observing the frozen grid.

## POST-RUN OUTCOME

### Exact frozen execution

The 21-point grid was executed once with no changes to the frozen primitives.
The exact results are stored in
[summary_by_alpha.csv](../../results/foundations/rq0_geometry_redistribution/summary_by_alpha.csv),
[on_policy_nodes.csv](../../results/foundations/rq0_geometry_redistribution/on_policy_nodes.csv),
[configuration.json](../../results/foundations/rq0_geometry_redistribution/configuration.json),
and [manifest.json](../../results/foundations/rq0_geometry_redistribution/manifest.json).

The sampled integrated points were exactly:

```text
alpha = .35, .40, .45.
```

All other sampled points were SEP-reducible. `J_HLS = J_SEP-Omega` at every
point within the frozen exact tolerance. No grid refinement or post hoc
physical change was made.

### Post-run analytical observation

Only after the frozen execution and its `.35/.40/.45` observation was the
finite Bellman tree solved symbolically. That derivation establishes exact
boundaries at `alpha=5/16` and `alpha=1/2`; it was not part of the pre-run
protocol and must not be represented as a parameter chosen before execution.

The complete model-scoped proof, its two distinct boundary mechanisms, and
its epistemic limits are in
[rq0_routing_integration_boundaries.md](../theory/rq0_routing_integration_boundaries.md).

This outcome is an existence result relative to strong SEP in this exact
family. It does not establish an empirical answer, prevalence, robustness, or
superiority over SEP-Omega.
