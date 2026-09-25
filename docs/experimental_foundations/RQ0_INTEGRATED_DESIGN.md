# RQ0 Integrated Confirmatory Protocol

**Status:** PRE-TEST PROTOCOL — READY TO FREEZE. TEST remains closed.

This protocol defines the first confirmatory experiment whose primary outcome
is accumulated system value under an integrated operation/development policy:

\[
\Delta J=J_{HLS}-J_{SEP}.
\]

It does not change RQ0, the HLS ontology, theory, or any B2.0–B2.4 result. It
introduces no learning mechanism: development is exactly REP from B2.4. No
model is trained, selected, or modified after TEST is opened.

## 1. Question and scope

RQ0 asks:

> Can the dynamic allocation and development of competences in a heterogeneous
> learning system improve long-term system performance compared with
> architectures that manage task allocation and knowledge transfer separately?

The experiment tests one precise part of that question: whether internalizing
the effect of current routing on opportunity availability and future
competence can improve accumulated value relative to a sequential architecture
that first routes for current operation and only then manages development.

It does **not** test whether a monolithic implementation intrinsically
dominates every modular architecture. A mandatory coordinated modular control,
SEP-Omega, is algebraically equivalent to HLS under this protocol. The result
therefore separates the value of internalizing the operation-development
cross-effect from any claim about physical or software centralization.

## 2. Frozen empirical basis

Only common-provenance B2.3/B2.4 artifacts enter the counterfactual:

- five CPU-trained Fast base checkpoints `F0_s`;
- five CPU-trained Deep checkpoints `D_s`;
- 60 immutable opportunities `O_(s,i,N)`;
- 60 deterministic replay buffers;
- 60 B2.4 REP checkpoints, each derived directly from its seed's F0;
- exact checkpoint, split, opportunity, replay, schedule, RNG, and parent
  hashes;
- complete VALIDATION competence vectors for every F0, D, and REP state;
- the frozen routing/value convention and F tie rule.

The indices are

```text
s in {0,1,2,3,4}
i in {photo, art_painting, cartoon, sketch}
N in {25,50,100}.
```

B2.1 and B2.2 results may supply scientific context but their independently
trained states are incompatible and are excluded. STD, O50, and REP2 explain
the selection of REP in B2.4 but are not policy endpoints in this experiment.

Everything above, including REP, is fixed before TEST. No state may be added,
removed, retrained, or selected after TEST access.

## 3. Confirmatory endpoint and exact evaluation count

The confirmatory endpoint is the PACS TEST split that remained closed
throughout B2.0–B2.4. TEST is used exactly once for inference/evaluation of
already frozen states.

The unique states required are:

| State type | Count | Reason |
| --- | ---: | --- |
| F0 | 5 | one shared base per seed |
| D | 5 | one shared Deep model per seed |
| REP | 60 | one per `seed × domain × N` |
| **Total** | **70** | unique checkpoint evaluations |

Thus the prior count of 70 is correct. Each checkpoint is evaluated once over
the complete TEST IDs belonging to its seed, producing one four-domain balanced
accuracy vector and optional per-example predictions needed to reconstruct it.
Repeated analytical uses across c, h, kappa, domains, or policies are not new
TEST evaluations.

TEST may not be used for training, parameter/state selection, policy or
estimator construction, choosing c/h/kappa, changing aggregation or tie rules,
selective reruns, debugging, or protocol amendment.

If one of the 70 evaluations fails technically, the run stops. A rerun is
permitted only for a documented infrastructure failure and must repeat the
failed evaluation under identical frozen code/configuration; partial output
cannot influence any decision.

## 4. Minimal integrated model

### 4.1 Experimental unit and state

One learned experimental unit is `(s,i,N)`: 12 cases within each seed and five
seed replicates. Before current operation,

\[
X_0=(s,i,N,S^F_0,S^D,\mathcal O_0=\varnothing,b=1,c,h,\kappa,\mathcal I_0),
\]

where `b=1` permits at most one REP update, c is Deep's relative operational
cost, h is the number of future workload-equivalent uses, kappa is the
nonnegative development cost in operational-value units, and `I_0` is the
common pre-TEST information set.

Potential opportunity `O_(s,i,N)` is sealed initially. Its offline existence
supports paired counterfactual evaluation; it becomes legally available only
if the policy selects D.

### 4.2 Horizon

The horizon has two stages:

1. current domain-i operation, opportunity generation, and optional
   development;
2. h future workload-equivalent uses drawn from frozen uniform exposure
   `p_k=1/4`, with operational F/D routing and no further development.

This is the shortest closed cycle containing

```text
operation -> opportunity -> development -> competence change -> future operation.
```

No additional temporal discount is introduced: `delta=1`. The declared h
already fixes the number/weight of future uses.

### 4.3 Actions, opportunity gate, and transition

The operational action is `a_0 in {F,D}`. If F is selected, D is not queried,
no D output is released, and no development is feasible. If D is selected,
the exact immutable opportunity becomes available.

The development action satisfies

\[
d_0\in\{0,1\},\qquad d_0\leq\mathbf 1[a_0=D],\qquad d_0\leq b.
\]

`d_0=1` means exactly B2.4 REP: same opportunity IDs and hard D pseudo-labels,
replay IDs and labels, schedule, optimizer, transforms, seeds,
`T_N=3 ceil(N/16)` steps, and F0 parent. No D query can occur after F.

\[
S^F_1(a_0,d_0)=
\begin{cases}
S(F^{REP}_{s,i,N}),& (a_0,d_0)=(D,1),\\
S(F0_s),& (a_0,d_0)\in\{(F,0),(D,0)\}.
\end{cases}
\]

The admissible pairs are exactly `(F,0)`, `(D,0)`, and `(D,REP)`.

### 4.4 Immediate and future value

\[
u_F(i)=S_i(F0),\qquad u_D(i;c)=S_i(D)-c,
\]

\[
\rho_i(c)=u_F(i)-u_D(i;c).
\]

Future domain routing uses F on ties:

\[
r(k;S,c)=
\begin{cases}
F,&S_k\geq S_k(D)-c,\\
D,&S_k<S_k(D)-c.
\end{cases}
\]

\[
V(S;c)=\frac14\sum_k\max\{S_k,S_k(D)-c\},
\]

\[
\Delta V_{s,i,N}(c)=V(S(F^{REP}_{s,i,N});c)-V(S(F0_s);c).
\]

## 5. Common objective, physical compute, and kappa

Every policy is evaluated by

\[
\boxed{J(a_0,d_0)=u_{a_0}(i;c)-\kappa d_0+hV(S^F_1(a_0,d_0);c).}
\]

`kappa>=0` is explicit development cost in the same normalized value units as
J. No conversion from CPU seconds to accuracy or utility is assumed. The
complete result is reported as a function of kappa and exact break-even costs.

REP CPU time, steps, examples, and other physical resources are reported
separately. Every policy has the same maximum compute budget: at most one REP
update per case. Different consumption follows from frozen actions, while
`-kappa d_0` accounts for development in J without inventing a conversion.

## 6. Pre-TEST estimators and TEST realizations

Hatted quantities come only from frozen B2.4 VALIDATION vectors:

```text
hat u_F = VALIDATION S_i(F0_s)
hat u_D = VALIDATION S_i(D_s) - c
hat V_0 = V(VALIDATION S(F0_s); c)
hat V_R = V(VALIDATION S(REP_s,i,N); c)
hat DeltaV = hat V_R - hat V_0.
```

There is no fitted predictive model or post-hoc smoothing. Before TEST these
values generate the complete policy action maps for every `(s,i,N,c,h)` and
every interval of `kappa>=0`. Store the maps with protocol, input, threshold,
and tie-decision hashes.

After TEST opens, unhatted quantities are computed once from TEST vectors and
only evaluate frozen actions. `DeltaV_TEST`, `rho_TEST`, and TEST routing can
never alter an action.

```text
policy selection  = frozen VALIDATION information only
policy evaluation = one-shot TEST information only.
```

SEP, HLS, and SEP-Omega therefore execute on TEST without reoptimization.

## 7. Frozen c × h grid

```text
c in {0, 0.02, 0.05, 0.10, 0.15}
h in {1, 2, 5, 10}.
```

These are the B2.2/B2.3 values. Retain all 20 cells. No cell is primary, no
best cell is selected, and c/h cells are not replicates. Report the complete
piecewise surfaces

\[
\Delta J(c,h,\kappa),\qquad \kappa\geq0,
\]

and their break-even thresholds. The global criterion requires a common
reproducible kappa region across the full grid.

## 8. Algebraic policy audit

Fix `(s,i,N,c,h)` and use pre-TEST quantities. The three action values are

\[
\hat J_{F0}=\hat u_F+h\hat V_0,
\]

\[
\hat J_{D0}=\hat u_D+h\hat V_0,
\]

\[
\hat J_{DR}=\hat u_D-\kappa+h\hat V_R.
\]

Let `hat rho=hat u_F-hat u_D` and
`hat DeltaV=hat V_R-hat V_0`.

### 8.1 Break-even cost

The best no-development action is

\[
\hat J_0=h\hat V_0+\max\{\hat u_F,\hat u_D\}.
\]

Hence

\[
\hat J_{DR}-\hat J_0
=h\widehat{\Delta V}-\max\{\hat\rho,0\}-\kappa.
\]

Define

\[
\boxed{\hat\kappa^*=h\widehat{\Delta V}-\max\{\hat\rho,0\}.}
\]

`(D,REP)` is strictly preferable to the relevant no-development alternative
if and only if

\[
\boxed{\kappa<\hat\kappa^*.}
\]

At equality select no development. A nonpositive threshold has no admissible
strict REP region because `kappa>=0`.

The realized TEST analogue is

\[
\boxed{\kappa^*_{TEST}=h\Delta V_{TEST}-\max\{\rho_{TEST},0\}.}
\]

It describes realized value but never changes the frozen policy.

### 8.2 SEP

SEP routes first on immediate utility only:

\[
a_{SEP}=F\ \text{if }\hat\rho\geq0,
\qquad a_{SEP}=D\ \text{if }\hat\rho<0.
\]

An immediate tie goes to F. If F is chosen, `d_SEP=0`. If D is chosen,

\[
d_{SEP}=1\iff\kappa<h\widehat{\Delta V}.
\]

At equality SEP chooses no development.

### 8.3 HLS

HLS maximizes the three displayed action values. Ties use fixed priority

```text
(F,0) before (D,0) before (D,REP).
```

Equivalently, choose `(D,REP)` iff `kappa<hat kappa*`; otherwise choose the
better immediate no-development action, with F on an immediate tie.

### 8.4 SEP-Omega and equivalence

The separate development module sends

\[
\hat\Omega_D(\kappa)=\max\{0,-\kappa+h\widehat{\Delta V}\}.
\]

The routing module compares `hat u_F` with `hat u_D+hat Omega_D`, using F on
equality. If D wins, develop iff Omega's maximizing continuation is strictly
positive.

When `-kappa+h hat DeltaV<=0`, Omega is zero and both policies choose the same
best no-development action. When positive, the D-side comparison is exactly
the HLS comparison after subtracting common `h hat V_0`. Shared tie rules also
coincide. Therefore

\[
\boxed{\pi_{SEP\text{-}\Omega}=\pi_{HLS}}
\]

for every seed, domain, N, c, h, and kappa. Their realized TEST actions and J
are identical even when VALIDATION estimates fail to transfer.

### 8.5 When HLS and SEP differ

If `hat rho<0`, SEP routes D and uses the same development threshold as HLS;
they coincide. They differ exactly when

\[
\boxed{\hat\rho\geq0
\quad\text{and}\quad
0\leq\kappa<h\widehat{\Delta V}-\hat\rho.}
\]

Then SEP chooses `(F,0)` and HLS chooses `(D,REP)`.

### 8.6 Exact realized DeltaJ and sign regions

Let `A_(s,i,N,c,h)(kappa)` indicate that pre-TEST divergence condition. Then

\[
\boxed{
\Delta J_{s,i,N}(c,h,\kappa)
=A(\kappa)[-\rho^{TEST}_{s,i}(c)-\kappa
+h\Delta V^{TEST}_{s,i,N}(c)].
}
\]

In a divergent case define the relevant realized break-even against SEP's F:

\[
\boxed{\kappa^*_{TEST,F}=h\Delta V_{TEST}-\rho_{TEST}.}
\]

Then `DeltaJ=kappa*_(TEST,F)-kappa`. Consequently:

- **HLS = SEP:** frozen actions coincide, or divergent actions have
  `kappa=kappa*_(TEST,F)`;
- **HLS > SEP:** actions diverge and `kappa<kappa*_(TEST,F)`;
- **HLS < SEP:** actions diverge and `kappa>kappa*_(TEST,F)` because the
  VALIDATION continuation estimate transferred insufficiently to TEST.

Positive DeltaJ is therefore not constructed. HLS has no TEST oracle: action
divergence is fixed entirely by hatted VALIDATION quantities. SEP-Omega equals
HLS in every region because its action is the same frozen action.

## 9. Aggregation and sign conventions

Within seed, aggregate the 12 cases with equal frozen weights:

\[
J^{(s)}_\pi(c,h,\kappa)
=\frac1{12}\sum_{i,N}J^{(s)}_{\pi,i,N}(c,h,\kappa).
\]

\[
\Delta J_s=J^{(s)}_{HLS}-J^{(s)}_{SEP},
\qquad
\Delta coord_s=J^{(s)}_{HLS}-J^{(s)}_{SEP\text{-}\Omega}.
\]

Positive DeltaJ favors HLS; negative favors SEP. Nonzero Delta coord
contradicts proven equivalence and invalidates the execution. Seeds are the
only replicates; domains, N, c, h, and kappa intervals are paired cases or
analytical valuations.

## 10. Exact kappa surface

Decisions are piecewise constant in kappa and J is piecewise linear. Construct
the surface analytically:

1. collect zero and all nonnegative pre-TEST thresholds `hat kappa*` and
   `h hat DeltaV`;
2. sort and deduplicate within numerical tolerance;
3. evaluate frozen actions on every open interval and boundary;
4. add zeros of realized linear DeltaJ inside intervals;
5. report closed/open sign intervals for every seed and c/h;
6. above the largest positive pre-TEST threshold all policy differences vanish.

Define

\[
K_{max}=\max(\{0\}\cup\{\hat\kappa^*:\hat\kappa^*>0\}).
\]

All potentially nonzero comparisons lie in `[0,K_max)`. No arbitrary finite
kappa grid or upper limit is introduced.

## 11. Confirmatory classification

For each c/h cell define

\[
R^+_{c,h}=\{\kappa\in[0,K_{max}):
\#\{s:\Delta J_s(c,h,\kappa)>0\}\geq4
\text{ and }\overline{\Delta J}(c,h,\kappa)>0\}.
\]

Define

\[
R^+_{all}=\bigcap_{c,h}R^+_{c,h},
\]

and

\[
R^+_{any}=\{\kappa:\exists(s,c,h)\text{ with }
\Delta J_s(c,h,\kappa)>0\}.
\]

Use exact piecewise-linear interval arithmetic. A boundary point has zero width
and is not a positive region.

- **POSITIVE:** `R^+_all` contains an interval of strictly positive width. The
  same nonempty kappa range then favors HLS in at least 4/5 seeds for every one
  of the 20 predeclared c/h cells.
- **NULL:** `R^+_any` is empty; no seed in any c/h cell has a positive interval
  for any `kappa>=0`.
- **INCONCLUSIVE:** every other valid result, including benefits confined to
  some cells, fewer than 4/5 seeds, disjoint kappa regions, or isolated
  zero-width crossings.

This rule does not select c, h, or kappa after TEST. Report every
`R^+_(c,h)`, `R^+_all`, seed surface, threshold, and interval alongside the
global label.

SEP-Omega must satisfy

\[
|\Delta coord_s(c,h,\kappa)|\leq10^{-12}
\]

at all breakpoints and one interior point per interval. Failure makes the
experiment INVALID rather than POSITIVE/NULL/INCONCLUSIVE.

## 12. Secondary explanation

Secondary variables are `rho`, `Omega=-kappa+h DeltaV`, all four DeltaS
components, DeltaV and its domain contributions, routing changes, selection
and realized kappa*, and physical REP resources. Gamma is unnecessary for the
singleton primary experiment and may appear only as historical B2.1/B2.3
context.

For every divergent trajectory reconstruct

```text
current sacrifice rho
-> D releases opportunity
-> REP
-> competence change
-> future routing/value change
-> DeltaJ.
```

These variables explain DeltaJ and cannot redefine success.

## 13. Fairness and adversarial audit

1. **Common objective:** all policies are evaluated by the same J. The gap
   measures internalization of a cross-effect, not universal architectural
   dominance.
2. **Strong SEP within its interface:** SEP optimizes immediate routing and
   then optimizes conditional development with the same estimator as HLS.
3. **Rich separated boundary:** SEP-Omega exactly reproduces HLS. The
   experiment cannot establish superiority over sufficiently coordinated
   modular control.
4. **Joint versus look-ahead:** the identified difference is anticipatory
   internalization versus non-internalizing sequencing, not physical
   centralization.
5. **Equal information:** HLS receives only frozen VALIDATION quantities also
   available to SEP's development module and SEP-Omega; never realized TEST.
6. **No selection/evaluation reuse:** VALIDATION freezes actions; TEST evaluates
   them once.
7. **No leakage:** TEST paths, IDs, labels, outputs, and metrics remain
   inaccessible until freeze.
8. **Equal resources:** policies share states, data, opportunities, REP,
   budget, kappa, c, h, estimator, endpoint, and J. Only D releases an
   opportunity.
9. **Real NULL/negative outcomes:** policies can coincide, or a VALIDATION
   decision can yield zero/negative TEST DeltaJ.
10. **Direct endpoint:** policy-level accumulated DeltaJ is primary;
    opportunity and competence quantities are explanatory.

## 14. Integrity, leakage, and sanity checks

Before TEST:

1. verify frozen protocol and implementation hashes;
2. verify exactly 5 F0, 5 D, 60 REP, 60 opportunities, and 60 replay buffers;
3. verify all checkpoint, split, opportunity, replay, schedule, RNG, and parent
   hashes against B2.3/B2.4;
4. verify every REP starts directly from its seed's F0 and has exact B2.4 dose;
5. verify no TEST path, ID, label, image, output, or metric was accessed;
6. construct hatted quantities, thresholds, complete action maps, and ties from
   VALIDATION only, then hash them;
7. verify SEP-Omega/HLS action equality symbolically and on synthetic boundary
   fixtures;
8. verify formulas for kappa*, divergence, J, DeltaJ, and aggregation;
9. verify no NaN, missing case, duplicate, or unresolved tie.

During one-shot TEST:

10. enforce inference/evaluation mode; prohibit optimizer construction,
    backward calls, and checkpoint writes;
11. evaluate exactly 70 frozen states once on complete TEST IDs;
12. store outputs, four-domain vectors, IDs, hashes, environment, and provenance;
13. verify identical TEST IDs within seed;
14. perform no reoptimization or mutation.

After TEST:

15. reconstruct J and DeltaJ from frozen actions;
16. verify `Delta coord=0` within `1e-12` everywhere;
17. verify every per-case DeltaJ identity;
18. verify 5 seeds × 4 domains × 3 N × 5 c × 4 h before kappa expansion;
19. verify intervals cover `[0,K_max)` without gaps/overlaps;
20. verify no NaN and complete provenance;
21. generate all predeclared outputs once without selective reruns.

Any failure makes the execution INVALID until a non-outcome-informed
engineering diagnosis is documented. It cannot be relabelled NULL.

## 15. Required outputs and claim limits

Required outputs are the freeze manifest/action map, 70-state TEST manifest,
per-case actions and utilities, J/DeltaJ/Delta coord identities, selection and
realized break-even surfaces, seed aggregates, every positive region,
classification, explanatory trajectory decomposition, physical REP resources,
and a concise audit summary.

A POSITIVE result permits the scoped statement that across the full frozen
PACS c/h grid and a common nonzero development-cost range, internalizing the
operation-development cross-effect improves held-out accumulated value versus
the declared SEP architecture with reproducible seed direction.

No result establishes novelty, universal HLS superiority, dominance over rich
modular coordination, generalization outside PACS, a multi-stage policy beyond
this two-stage cycle, or an internal cause of competence interference.

## 16. PRE-TEST FREEZE DECISION

# READY TO FREEZE

The endpoint, 70-state evaluation set, continuous kappa representation,
break-even surface, c × h grid, policies, pre-TEST estimators, aggregation,
classification, tie rules, modular-equivalence proof, TEST boundary, and
integrity checks are completely specified. Actions depend only on frozen
VALIDATION quantities. TEST remains unopened and will be used only for
one-shot evaluation after protocol and implementation are committed.
