# Campaign 3 Gate 1: continuation sensitivity of local mode value

## Frozen scope

Gate 1 is a narrow, development-only diagnostic. It asks whether the value of
changing one current decision has enough local structure under two contrasting
continuation probes to justify attempting to learn it from ex-ante state
information. It is not a strategy comparison, continuation-policy ranking, or
selector experiment.

The prerequisite horizon pilot was closed at commit `b485b1b` with
**PERSISTENT BOUNDARY EVOLUTION** preserved. By subsequent CE decision,
Campaign 3 uses `ell=11` as a pragmatic operational temporal assessment range,
not an identified optimal or saturation horizon.

Gate 1 reuses the validated initial-pilot development data: eight development
teams, all 21 `Phi_dev` regimes, five histories per cell, and factual Q11
trajectories. All results are conditional on `h ~ d_Q11`. No held-out team or
kernel was executed.

## Operator and temporal definitions

At every eligible factual pre-action state, all four current-decision modes
`Q00`, `Q10`, `Q01`, and `Q11` are evaluated under continuation probes `Q00`
and `Q11`, using the frozen paired exogenous realization. The current-mode
intervention lasts one decision. The probes are contrasting continuations;
they are not bounds, extrema, an envelope, or approximations to every possible
continuation.

For continuation `c`, `A_m^c = Y_m^c - Y_00^c`. Best modes maximize `Y` using
tolerance `1e-10` and tie order `Q00,Q10,Q01,Q11`. Cross-continuation regrets
are retained in absolute `mu_true` units:

```text
R_00_to_11 = Y^11_{m*11} - Y^11_{m*00}
R_11_to_00 = Y^00_{m*00} - Y^00_{m*11}
```

No normalized `R/D` quantity or materiality threshold is used.

Eligibility is `j(t)+11<=12`, so only the first problem contributes. The known
experimental clock defines `tau` as the number of real rewards from the current
decision through `e(j(t)+11)`, inclusive:

```text
tau = 3*(11+1) - (within_problem_decision-1)
```

The three decisions have `tau=36,35,34`. This uses no privileged future state
or outcome information.

## Design and integrity

The analysis contains 840 complete histories, 2,520 eligible states, and
20,160 mode-by-continuation branch values. Each `tau` stratum contains 840
states. Uncertainty summaries resample complete histories using the frozen
2,000 bootstrap draws and seed `20261013`; decisions are not treated as
independent.

## Best-mode and ranking stability

| Scope | Best-mode agreement | Full ranking agreement | Mean pairwise relation agreement |
|---|---:|---:|---:|
| Overall | 95.87% | 95.32% | 97.80% |
| tau=36 | 90.00% | 88.57% | 94.76% |
| tau=35 | 97.62% | 97.38% | 98.63% |
| tau=34 | 100.00% | 100.00% | 100.00% |

The history-bootstrap interval for overall best-mode agreement is
`[95.12%,96.63%]`; at `tau=36` it is `[87.98%,91.90%]`. Near-terminal exact
agreement is clock-conditioned, not evidence of intrinsic continuation
invariance.

## Sign stability

| Mode | Overall | tau=36 | tau=35 | tau=34 |
|---|---:|---:|---:|---:|
| Q10 | 96.47% | 91.07% | 98.33% | 100.00% |
| Q01 | 96.71% | 91.19% | 98.93% | 100.00% |
| Q11 | 96.39% | 91.07% | 98.10% | 100.00% |

Zeros and ties are retained. At `tau=34`, all 840 advantages for every mode
are zero under both continuations. Complete directional sign counts are in
`sign_stability_summary.csv`.

## Absolute cross-continuation regret

| Scope | Direction | Mean | q50 | q75 | q90 | q95 | q99 | Max |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Overall | 00→11 | .02146 | 0 | 0 | 0 | 0 | .57878 | 4.09495 |
| Overall | 11→00 | .04404 | 0 | 0 | 0 | 0 | .93620 | 10.74521 |
| tau=36 | 00→11 | .05807 | 0 | 0 | .000009 | .28479 | 1.72269 | 4.09495 |
| tau=36 | 11→00 | .11610 | 0 | 0 | .000515 | .35125 | 3.42194 | 10.74521 |
| tau=35 | 00→11 | .00632 | 0 | 0 | 0 | 0 | .29561 | .71302 |
| tau=35 | 11→00 | .01601 | 0 | 0 | 0 | 0 | .23887 | 4.51100 |
| tau=34 | both | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Most states have zero regret, while the early-state tail is nontrivial and
asymmetric. These natural-unit tails do not establish continuation superiority.
The full distribution is retained in `cross_continuation_regrets.csv`.

## Classification and decision

**PARTIAL LOCAL STRUCTURE — GO CONDITIONED TO C3.2.**

Local structure is strong over most Q11-sourced development states: overall
best-mode and sign agreement exceed 95%, and medians through q95 of both regret
directions are zero. But continuation-sensitive regions coexist with those
robust regions. At `tau=36`, best-mode disagreement is 10%, ranking disagreement
is 11.43%, all sign-agreement rates are about 91%, and both regret directions
have nonzero upper tails, including rare large values. Sensitivity falls
sharply with remaining temporal opportunity and disappears at `tau=34`.

This does not support **ROBUST LOCAL STRUCTURE**, because early-state
disagreements can be consequential. It does not support **STRONG POLICY
DEPENDENCE**, because disagreement is neither widespread over the full
distribution nor persistent across `tau`. Under the frozen decision rule,
coexisting robust and continuation-sensitive regions imply a conditioned go
directly to C3.2. Whether vulnerability is predictable from ex-ante state
information was not analyzed here.

## Firewalls and limitations

No held-out execution, Gate 2 analysis, predictor training, feature selection,
or metacontroller training occurred. Physics, inference, policies, factual
state source, and operational range were unchanged. True `p/z`, `C/N/M`, and
future information were not used for classification. Conclusions apply only
to Q11-sourced states in this frozen development design and to the two named
continuation probes.
