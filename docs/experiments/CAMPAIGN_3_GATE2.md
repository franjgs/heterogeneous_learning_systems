# Campaign 3 Gate 2: minimal hybrid state-coverage audit

## Scope

Gate 2 is a development-only data-validity safeguard. It asks whether multiple
behavior sources produce enough mode-to-action and trajectory/state diversity
that C3.2 need not be trained only on `h ~ d_Q11`. It is not a coverage claim
over the continuous state space and does not train a predictor or
metacontroller.

The frozen design crosses all 20 `S_dev` teams, all 21 `Phi_dev` regimes, five
fresh replicates, and behavior sources `D00`, `D10`, `D01`, `D11`, and
`DbetaU`. Each of the resulting 10,500 histories has 12 problems and 36
decisions, yielding 378,000 pre-action states. Problem and observation-noise
streams are paired across behavior sources within team/kernel/replicate;
`DbetaU` has a separate deterministic stream solely for uniform mode choice.

At each state, the four frozen mode selectors were evaluated without advancing
the factual state or RNG. No `ell=11` value target or other C3.2 target was
generated.

## Level 1: mode-to-action diversity

| Source | KX=1 | KX=2 | KX=3 | KX=4 |
|---|---:|---:|---:|---:|
| Overall | 74.13% | 25.00% | .865% | .0056% |
| D00 | 61.88% | 36.83% | 1.287% | .0053% |
| D10 | 82.79% | 16.72% | .485% | .0040% |
| D01 | 68.64% | 30.11% | 1.241% | .0093% |
| D11 | 82.22% | 17.31% | .471% | .0040% |
| DbetaU | 75.12% | 24.03% | .841% | .0053% |

Overall pairwise action-divergence rates were:

| Pair | Rate |
|---|---:|
| Q00/Q10 | 25.08% |
| Q00/Q01 | 1.95% |
| Q00/Q11 | 25.13% |
| Q10/Q01 | 24.72% |
| Q10/Q11 | 1.27% |
| Q01/Q11 | 24.31% |

The full source-conditioned rates are retained in
`pairwise_action_divergence.csv`.

## Level 2: policy-to-trajectory diversity

Capability and belief geometry were kept separate. Capability differences use
the frozen quotient Frobenius distance `d_S`; belief differences use ordinary
L1 distance on probability vectors. No combined metric was constructed.

Relative to paired D11 trajectories, D00 differs in capability state at 67.69%
of states and belief at 47.79%; D01 differs at 55.50% and 39.60%; D10 differs
at 18.42% and 12.13%. Corresponding mean `(d_S, L1)` values are D00
`(.1093,.4308)`, D01 `(.1069,.3515)`, and D10 `(.03395,.02596)`.

The clock-conditioned summaries show genuine trajectory accumulation rather
than initial-state imbalance: every paired source is identical at clock 1.
For D00 versus D11, nonzero `(S,b)` rates rise to `(65.62%,69.62%)` at clock
12 and `(80.86%,81.29%)` at clock 36. For D01 they rise to
`(50.38%,56.19%)` and `(72.76%,73.43%)`. D10/D11 differences are smaller but
increase to `(25.14%,23.76%)` by clock 36. Complete clock trajectories and
distributional summaries are retained in `trajectory_diversity_by_clock.csv`.

## Level 3: selector-observable distributions

The observable representation is exactly `(S,b,tau)`. True `p/z`, `C`, `N`,
`M`, generator parameters, true rewards, and future information are excluded.
Without combining `S` and `b`, the union of fixed sources reaches paired states
beyond D11 in 72.45% of cases for `S` and 50.37% for `b`.

`DbetaU` selected `Q00/Q01/Q10/Q11` 18,772 / 19,062 / 19,006 / 18,760 times.
Relative to the closest paired fixed-source state, it adds nonzero capability
distance in 34.01% of states and belief distance in 25.47%. Median incremental
distance is zero, while q90 is `.03788` for `d_S` and `.00505` for belief L1.
Thus beta_U contributes additional states, but the result is not described as
exhaustive support.

## Classification

**SUFFICIENT DEVELOPMENT DIVERSITY.**

Mode differences generate substantial action diversity, and the fixed behavior
sources generate meaningful, clock-dependent capability and belief trajectories
beyond D11. The neutral beta_U source also adds observable states beyond the
paired fixed-source union. These findings satisfy the qualitative Gate 2 rule
without a post-hoc coverage threshold.

Decision: **CLOSE GATE 2 AND PROCEED IMMEDIATELY TO C3.2 DATASET
CONSTRUCTION.** C3.2 construction was not begun in this task.

## Firewalls and limitations

No held-out team or kernel was executed. No policy, physics, inference,
generator, split, or operational horizon was changed. No performance outcome,
counterfactual target, predictor, or metacontroller was constructed. Results
describe the frozen development distribution and do not establish exhaustive
continuous-state coverage.
