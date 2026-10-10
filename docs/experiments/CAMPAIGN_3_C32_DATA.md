# Campaign 3 C3.2-DATA protocol

## Purpose and status

C3.2-DATA freezes the development allocation and the machinery for generating
raw Monte-Carlo counterfactual mode-value labels. It does not train a predictor
or metacontroller, and it does not execute the complete label campaign.

The source is the closed Gate 2 factual dataset: 10,500 histories, 378,000
pre-action states, 20 development teams, 21 development kernels, five behavior
sources, and five replicates. Held-out teams and kernels are excluded.

## Allocation

Exactly one state is selected from every factual history, producing 10,500
selected states. Assignment uses only the frozen factual identifiers. It never
uses state values, actions, `K_X`, problems, descriptors, rewards, regrets, or
future outcomes.

Replicate partitioning is fixed before labels:

| Factual replicate | Partition | States |
|---:|---|---:|
| 0, 1, 2 | TRAIN | 6,300 |
| 3 | VALIDATION | 2,100 |
| 4 | DEVELOPMENT TEST | 2,100 |

Each partition independently orders its history IDs by the SHA-256 digest of a
frozen seed and history ID, then assigns clocks `1..36` cyclically. TRAIN has
exactly 175 observations per clock; VALIDATION and DEVELOPMENT TEST have 58 or
59. The resulting allocation and hashes are frozen in
`results/foundations/campaign3_c32_data/`.

Gate 2 behavior sources share physical-problem and observation-noise streams
within a team/kernel/replicate cluster. Consequently, behavior sources are not
claimed to be independent merely because their `history_id`s differ. Because
partitioning is by replicate, all five paired behavior sources remain within a
single partition; future evaluation must retain that paired-source provenance.

## Counterfactual estimands and raw labels

For every selected pre-action state, all conceptual labels are retained:

```text
Y_m^c(h_t, ell=11), m in {Q00,Q10,Q01,Q11}, c in {Q00,Q11}.
```

The computed object is named `raw_mc_G`: one CRN-paired Monte-Carlo realization
of the undiscounted cumulative `mu_true` reward from the current decision
through the end of the eleventh subsequent problem. It is not an exact
conditional expectation.

For each continuation separately, paired advantages are:

```text
A_00^c = 0
A_m^c = raw_mc_G_m^c - raw_mc_G_00^c, m in {Q10,Q01,Q11}.
```

The two continuations are not averaged.

## Arbitrary-state continuation and CRN

The selected factual state supplies the current `S`, `b`, problem index, and
within-problem decision. The realized physical prefix `p_1,...,p_j` is recreated
from the frozen factual problem seed and kernel. Future problems are then drawn
from a **fresh, reproducible conditional generator stream given that physical
prefix**, including the original RETURN distinct-history and reflection rules.

This choice avoids conditioning a label on future factual problems that were
unobserved at the selected state while retaining the correct generator law given
the realized history. It is not a restart from the initial problem distribution.

Each state has one future-problem stream and one future observation-noise stream.
All four initial modes and both continuations reuse those exact exogenous draws.
Only actions, Bayesian beliefs, and capability states diverge endogenously.
Belief resets at each new problem; MIS-v2 capability state persists.

Initial actions are recomputed from the frozen planners. For a continuation,
identical initial actions share one rollout. Hence actual physical rollouts per
state equal `2 * K_X`, while all eight conceptual mode-by-continuation labels
are materialized. The frozen allocation has `K_X` counts 7,771 / 2,626 / 102 /
1 for `K_X=1/2/3/4`, respectively: 26,666 actual rollouts for 84,000 conceptual
labels when the full campaign is explicitly authorized.

## Epistemic firewall

Future predictor inputs may only be `S_t`, `b_t`, `tau_t`, and preregistered
deterministic transformations of those variables. The raw target tables retain
privileged experimental metadata and labels for accounting, but those are not
predictor inputs.

Never expose as predictor inputs: true problem, `C/N/M`, kernel/team/behavior
identity, replicate/history/state IDs, future problems/noise, `mu_true`, raw
counterfactual returns, advantages, `K_X`, or mode/planner disagreement.
`K_X` is retained solely for rollout-deduplication and diagnostics.

## Safe execution

`targets.py` is safe by default: without a mode it performs a dry run. A bounded
run requires `--execute --limit N`; the full 10,500-state campaign additionally
requires the explicit `--execute --full`. `--partition
TRAIN|VALIDATION|DEVELOPMENT_TEST` permits write-once partitioned execution,
and `--limit` permits a deterministic bounded prefix for diagnostics. Smoke
labels go to a separate diagnostic directory and cannot overwrite future
scientific outputs. All output
directories are write-once and carry allocation/source hashes.

## Limitations

Labels are conditional on the frozen development data and on one future
Monte-Carlo continuation per selected state. They do not establish policy
superiority, expected value exactly, state-space coverage, or metacontroller
performance. C3.2 model fitting and evaluation require a separate task.

