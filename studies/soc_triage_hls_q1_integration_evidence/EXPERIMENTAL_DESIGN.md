# Experimental design (prespecified)

## Question and unit

The unit is a synthetic SOC episode under a joint operating condition \(u=(\theta,P,C)\). The primary question is whether a published standardized escalation point's trade-off between detections and induced L2 work changes \(S_+\) or its contrast between D1, P1 and WAPS as false-positive work and L2 resources vary.

## Fixed classifier points

All three are published Table 5, p.39, standardized labels, symmetric costs, A+C. Their SOCTRA rates are held at reported values and used to generate synthetic Bernoulli recommendations.

| Point | pD | pFA | BA | Role fixed before simulation |
|---|---:|---:|---:|---|
| LightGBM | .8421 | .0450 | .8986 | Higher detection with moderate pFA; statistical reference. |
| LSEnsemble | .8421 | .0743 | .8839 | Dominated control: same pD, higher pFA. |
| Bayesian MLP | .7042 | .0154 | .8444 | Lower pFA and lower detection trade-off. |

No new point is chosen from observed operational outcomes. The standardized group is kept separate from original labels. Published pD/pFA do not equal individual test predictions.

## Design matrix

| Factor | Prespecified values |
|---|---|
| Demand | rhoL1=1.25, 6 L1; elevated-load condition prioritizes the mechanism where L2 work competes for scarce service. |
| L2 roster | 2, 3, 4 analysts; absolute L1 demand remains constant. |
| Policy | D1, P1, HLS-B/WAPS, unchanged. |
| FP service fraction | alpha=.25,.50,.75,1.00. |
| Replication | 400 new seed IDs, 711000000–711000399. |
| Admission / drain | H=24 h, D=36 h. |

Total: 3 classifier points × 3 rosters × 3 policies × 4 alpha levels × 400 paired seeds = **43,200 policy-episode rows**. The 400 seed trajectories are paired across classifiers via keyed common random numbers, across policies and alpha, and L2 capacity. D1/P1/WAPS see the same L1 alerts and hidden needs for a matched classifier/seed. L1 trajectories are computed once per seed/policy and reused across the three L2 rosters because L1 staff and demand are identical.

This is an alpha sensitivity campaign at elevated L1 load, not a full classifier × demand × alpha factorial. Existing 18,720-row campaign remains the evidence for normal-load comparisons and alpha=1 conditions across both L1 loads. The new analysis adds three L2 capacities to identify how FP work assumptions interact with resources.

## Precision rationale

For a proportion near .70, a nominal independent-case 95% half-width of .05 requires \(n\approx1.96^2(.70)(.30)/.05^2=323\) positive needs (worst-case p=.5 gives 385). The previous priority condition had 35 needs/40 seeds and 16 zero-need seeds, giving a much wider interval. The expected needs per new seed under the same 24 h arrival process and \(\pi=19/14,449\) are about .875; 400 seeds therefore target roughly 350 needs before accounting for clustering and random variation. The episode seed, not each alert or each policy row, is the resampling unit. The actual number of needs and zero-need seeds will be reported; the precision target is not presumed achieved.

The repeated L2 roster, alpha and policy results on one seed are correlated. All confidence intervals resample the 400 seed identifiers as blocks and preserve all matched outcomes. The 400 blocks are independent simulation seeds under the generator, but this only addresses simulator Monte Carlo uncertainty.

## Primary outcome and comparisons

Primary: pooled \(\widehat S_+\) with need counts aggregated before division. Primary contrasts: WAPS−D1, P1−D1 and WAPS−P1 in pooled \(S_+\), with paired seed bootstrap percentile intervals. Secondary outcomes are fixed in [simulator specification](SIMULATOR_SPECIFICATION.md): per-admitted correct timely need, modeled quality on timely TPs, all-route SLA, FP work, FN omitted work, L1/L2 backlog, utilization, WAPS P1 share and switches.

Classifier × policy interaction is a difference-in-differences in \(S_+\):
\[
[(S_+(B,WAPS)-S_+(B,D1))-(S_+(A,WAPS)-S_+(A,D1))].
\]
All classifier pair contrasts are reported descriptively. No multiplicity correction is used; intervals are exploratory and not used as universal superiority claims.

## Reuse and non-reuse

Prior campaign evidence and results are read-only and used for audit, context and alpha=1 benchmark comparison. The alpha=1 equivalence *test* uses a small deterministic fixture. No old simulation seeds are reused in the new campaign. No results are selected or stopped based on interim performance.
