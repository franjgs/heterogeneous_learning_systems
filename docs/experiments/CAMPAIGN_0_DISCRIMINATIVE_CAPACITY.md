# Campaign 0 — frozen discriminative-capacity test

## Epistemic status

Campaign 0 is a diagnostic of the frozen HLS laboratory, not the main evidential campaign and not evidence for a general advantage of heterogeneous teams. This record separates: (A) the design fixed before execution, (B) observations produced by that design, (C) a mechanistic interpretation formulated after observing those results, and (D) mathematical consequences of MIS-v2. These categories must not be collapsed in later paper prose.

## A. Pre-specified before execution

### Purpose and frozen model

The purpose was to test whether the existing laboratory could discriminate the chain

```text
initial capability geometry x problem history
-> assignment/exposure
-> capability trajectory
-> later assignment/performance.
```

The initial repository state was clean at foundation commit `20106d3`. Production, finite-belief DISCOVER, MPC, MIS-v2, problem representation, action space, and temporal physics were frozen. Execution used `DISCOVER_DEVELOP`, eta `0.35`, horizon three per problem, uniform prior over `((.8,.2),(.5,.5),(.2,.8))`, deterministic seeds `0,...,9`, and common random numbers across configurations within a history.

Teams were fixed from geometry alone: G00 `((.5,.5),(.5,.5),(.5,.5))`; G04 `((.25,.75),(.625,.375),(.625,.375))`; G05 `((0,1),(.5,.5),(1,0))`; and G07 `((0,1),(.5,0),(1,.5))`. Each has per-capability totals `(1.5,1.5)`. G05 and G07 have identical repository aggregate geometry descriptors but different interpersonal placement.

Histories were H0 `.8,.7,.3,.2,.5,.8`; H1 `.8,.2,.3,.7,.5,.8`; H2 `.8,.8,.8,.8,.8,.8`; and H3 `.8,.2,.8,.2,.8,.8`. H0/H1 contain the same problem multiset and were the primary order control.

### Pre-specified outcomes and assessment rule

Recorded outcomes included step-level actions, exposures, capability states, true production, noisy observations, beliefs, cumulative production, problem-level rankings, and final recurrent-A performance. The primary contrast was

```text
Delta_order(g)=P_g(final A | H0)-P_g(final A | H1).
```

The frozen assessment was PASS for clear development-mediated path dependence plus some history-dependent ranking change; PARTIAL for path dependence without a meaningful ranking change, or an uninterpretable/non-robust change; and FAIL for essentially invariant rankings, noise-only differences, no interpretable adaptive mechanism, or near-universal domination that prevented discrimination. No threshold for effect size was added.

## B. Observed in Campaign 0

Campaign 0 executed 160 runs and 2,880 within-problem steps and was classified **PASS** under its frozen rule. This is a diagnostic classification, not confirmation of the future paper hypothesis.

### Configuration x history matrix

Entries are mean cumulative true production over ten seeds; parentheses contain mean final-A production. Ordering is cumulative rank.

| History | 1st | 2nd | 3rd | 4th |
|---|---:|---:|---:|---:|
| H0 | G07 27.2043 (5.2611) | G05 26.8677 (5.0880) | G04 26.2866 (5.2549) | G00 25.7103 (5.3314) |
| H1 | G07 27.2991 (5.2611) | G05 26.5011 (4.5948) | G04 26.2972 (5.2547) | G00 25.3942 (4.9361) |
| H2 | G07 30.8236 (5.3164) | G04 30.1005 (5.3156) | G00 29.5371 (5.5822) | G05 29.5243 (5.2570) |
| H3 | G07 28.7539 (5.2603) | G04 27.9087 (5.2543) | G05 27.3174 (5.1593) | G00 27.0949 (5.4636) |

G07 won cumulative performance in all four histories. Campaign 0 therefore did **not** produce diversity in cumulative winners.

### Content-matched H0/H1 order effect

Mean `Delta_order` was G00 `0.395264`, G04 `0.000221`, G05 `0.493247`, and G07 exactly `0`. Mean final-A ranking changed from G00 > G07 > G04 > G05 under H0 to G07 > G04 > G00 > G05 under H1. At seed level, the first pattern occurred in 8/10 H0 runs and 2/10 H1 runs; the second occurred in 2/10 H0 and 8/10 H1.

Observed cases include positive order dependence (G00 and G05), a near-null final-A effect (G04), and an exactly null final-A effect across all seeds (G07). Path dependence was configuration-dependent rather than universal.

## C. Post-hoc cumulative-exposure mechanism audit

This explanation was formulated **after** observing Campaign 0. It was not a preregistered Campaign 0 hypothesis. The audit used the existing H0/H1 trajectories only; it did not alter or rerun the experiment.

### Exposure and exact reconstruction

MIS-v2 uses the continuous action entry itself as exposure:

```text
x_ik(t)=X_t[i,k],
E_ik(t)=sum_(tau<t) X_tau[i,k].
```

Campaign 0 actions contain exposures `0`, `.5`, and `1`; exposure is not a binary action count. With `eta=.35` and `lambda=-log(1-eta)`, the independently audited cumulative form is

```text
s_ik(t)=1-(1-s_ik(0)) exp(-lambda E_ik(t))
       =1-(1-s_ik(0)) (1-eta)^(E_ik(t)).
```

Across 80 pre-final-A states and 480 capability cells, the maximum absolute discrepancy between this reconstruction and the stored simulator state was `1.1102230246251565e-16`.

### Team diagnoses

- **G00 — state and behavioral divergence.** H0/H1 produced unequal cumulative exposure in 8/10 seeds. Exposure shifted primarily between the two capabilities of agents 2 and 3, breaking the initial interpersonal symmetry. This changed later state and, conditional on belief/policy branches, final-A behavior and performance.
- **G04 — state difference with near behavioral convergence.** Exposure/state differed in 7/10 seeds, but the mean final-A effect was only `0.000221`. Important residual differences frequently lay in a capability not exercised by final-A assignments, while relevant first-capability cells were near their ceiling.
- **G05 — mirrored development and behavioral divergence.** Exposure differed in 8/10 seeds and was concentrated in the initially balanced agent. In representative seed 0 its cumulative exposure was `(9,6)` under H0 and `(6,9)` under H1, producing approximately mirrored states `(.989644,.962291)` and `(.962291,.989644)` and different final-A allocation/performance.
- **G07 — behavioral convergence does not imply state convergence.** Final-A performance was identical under H0/H1 in all ten seeds, but cumulative exposure and pre-A state were identical in only 5/10. In the other seeds, residual state differences occurred in a capability not used by the final-A policy; exposure directed to an already mastered cell also could not change that cell. The previous representative seed-0 trace showed genuine state convergence, but it must not be generalized to every seed.

The audit therefore distinguishes:

1. **state convergence:** equal `S_preA`;
2. **behavioral convergence:** equal subsequent action/performance despite possibly unequal state;
3. **behavioral divergence:** state differences affect subsequent policy and/or production.

A capability-state difference is not necessarily a performance-relevant capability-state difference. Performance additionally depends on the next problem, belief, MPC assignment, and CES production.

## D. Mathematical consequence of the HLS MIS-v2 formulation

For fixed initial capability and exposures,

```text
F(F(s,x1),x2)=1-(1-s) exp[-lambda(x1+x2)].
```

Consequently, conditional on `S_0` and cumulative exposure `E`, MIS-v2 produces the same capability state regardless of exposure order. This is an algebraic consequence of the HLS MIS-v2 formulation—not an empirical discovery, an externally established learning theorem, or a claim about real teams.

Under the frozen model, capability-state path dependence is therefore policy-mediated:

```text
problem history
-> adaptive assignments
-> cumulative exposure
-> persistent capability state
-> subsequent assignment
-> performance.
```

The implementation qualifies this statement only in interpretation: exposure is continuous; exposure differences at `s=1` need not produce state differences; and state differences need not affect performance when the differing cells are not subsequently exercised.

## Limitations and allowed inference

- Campaign 0 establishes no general superiority of heterogeneous teams.
- No diversity of cumulative winners was observed: G07 led all four histories.
- Path dependence was configuration-dependent.
- State difference does not imply behavioral or performance difference.
- Cumulative exposure explains capability state under MIS-v2, not performance directly.
- The exposure mechanism interpretation is post hoc.
- Campaign 0 is diagnostic, not the main evidential campaign.
- Results are confined to the frozen teams, histories, eta, seeds, controller, and production physics.

No Campaign 1 hypothesis or protocol is defined here. Theory consolidation and targeted literature review must precede any Campaign 1 design.

## Provenance and artifacts

The execution commit is `bdcc8bd`. Raw and derived artifacts are under `results/diagnostics/campaign0_discriminative_capacity/`. The frozen manifest is `manifest.json`; step-level evidence is `trajectories.csv`; summaries are `runs.csv`, `configuration_history_matrix.csv`, `ranking_through_time.csv`, and `order_effects.csv`. Representative cases and figures are descriptive views over those machine-readable records. `closure_provenance.json` records immutable artifact hashes and the epistemic status of this closure.
