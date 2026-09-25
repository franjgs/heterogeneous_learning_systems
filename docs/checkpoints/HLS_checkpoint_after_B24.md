# HLS Scientific Checkpoint after B2.4

## 1. Scientific question

B2.4 asked:

> Can cross-domain interference be reduced while preserving learning from the
> same operational opportunity, and how does this affect the future value of
> development?

The experiment tested whether replacing redundant exposure to an immutable
B2.3 opportunity with historical replay changes competence interference and
future operational value. It does not change RQ0, open TEST, identify an
internal learning mechanism, or establish a result beyond PACS/VALIDATION and
the replay policy tested.

## 2. Frozen design and execution

The scientific protocol is frozen in
[`B24_PROTOCOL.md`](../experimental_foundations/B24_PROTOCOL.md) at commit
`491659c`. B2.4 used PACS, CPU execution, VALIDATION-only evaluation, the same
five seeds, F0, D, splits, immutable opportunities, and STD states as B2.3,
with `N={25,50,100}` and the four domains `photo`, `art_painting`, `cartoon`,
and `sketch`. TEST remained closed.

Each of the 60 `seed × domain × N` families compared states derived directly
from the same F0:

- **STD:** the original B2.3 update, with full opportunity exposure;
- **O50:** equal compute to REP, using only the exact effective opportunity
  exposure shared with REP and duplicating it into the remaining batch slots;
- **REP:** equal compute and the same opportunity IDs, exposure indices,
  augmentations, tensor positions, seeds, and RNG as O50, while replacing the
  duplicated slots with historical replay from the other three domains;
- **REP2:** continuation of REP that restores full opportunity exposure while
  adding compute and an equal replay exposure.

Replay used only ground-truth-labelled training IDs already used by the
corresponding F0. It used no VALIDATION, TEST, additional TRANSFER data, or new
teacher queries. The run completed:

- 120/120 new fits;
- 180/180 new VALIDATION evaluations;
- 1,200/1,200 value rows;
- accumulated runtime `04:57:04`;
- compatibility audit: **PASS**;
- TEST: **CLOSED**.

The scientific CSVs contain 240 method states: 60 each for STD, O50, REP, and
REP2. A terminal line reported `360/240 method states` because its numerator
also counted 120 repeated F0/D lookup views. This is a reporting-label issue;
it does not change the 240 method states or any scientific result.

## 3. Frozen outcomes

For intervention domain `i`, the protocol defined

```text
DeltaS_local^m = S_i(F_i^m) - S_i(F0)
DeltaS_cross^m = sum_{k != i} [S_k(F_i^m) - S_k(F0)]
I_i^m          = -DeltaS_cross^m
DeltaV_i^m(c)  = V(F_i^m;c) - V(F0;c).
```

The primary causal contrast is REP minus O50:

```text
DeltaI = I_REP - I_O50
DeltaL = DeltaS_local_REP - DeltaS_local_O50
DeltaQ(c) = DeltaV_REP(c) - DeltaV_O50(c).
```

The frozen classifications were:

| Outcome | Classification |
| --- | --- |
| interference reduction | **POSITIVE** |
| local learning | **POSITIVE** |
| future value, `c=0` | **POSITIVE** |
| future value, `c=0.02` | **POSITIVE** |
| future value, `c=0.05` | **POSITIVE** |
| future value, `c=0.10` | **POSITIVE** |
| future value, `c=0.15` | **POSITIVE** |

The five seeds are the replication units. N and c are not independent
replicates.

## 4. Primary REP--O50 result

### 4.1 Cross-domain interference

Mean cross-domain competence recovery was `+0.336271`, equivalently mean
`DeltaI=-0.336271`. REP was favorable in 59/60 learned states. All 12 exact
`domain × N` cells reached the frozen favorable direction in at least 4/5
seeds, and 11/12 reached 5/5. The mean recovery increased with dose: 0.143734
at N=25, 0.324717 at N=50, and 0.540361 at N=100.

### 4.2 Local learning

Mean `DeltaL` was `+0.032682`; 39/60 states improved locally. In the 21 states
with `DeltaL<0`, recovered cross-domain competence exceeded local competence
loss in 20/21. The global seed-level local-learning classification was
**POSITIVE** without an added preservation margin.

### 4.3 Future operational value

Mean REP-minus-O50 future-value changes were:

| c | mean DeltaQ(c) |
| ---: | ---: |
| 0.00 | +0.005406 |
| 0.02 | +0.008802 |
| 0.05 | +0.017846 |
| 0.10 | +0.038176 |
| 0.15 | +0.055304 |

The seed-level mean was positive for all five seeds at every c. Among the 60
separately classified `domain × N × c` regimes, 47 were **POSITIVE** and 13
were **INCONCLUSIVE**.

Across the five c values, the exact mean value decomposition was:

```text
local contribution        +0.002806
cross-domain contribution +0.022300
total                     +0.025107
```

Thus 88.8% of the mean improvement in `DeltaV` came from non-target
competences. This links the observed interference reduction directly to the
change in future operational value under the declared routing/value function.

## 5. Dose controls

STD minus O50 had a small aggregate effect: halving informative opportunity
exposure without replay did not reproduce the main REP-minus-O50 change.

REP2 minus REP had mean `DeltaS_local=-0.011301` and
`DeltaS_cross=-0.028334`; its mean `DeltaV` was lower for every c. Restoring
the full opportunity dose by adding compute therefore did not improve REP.

REP2 remained better than STD: mean `DeltaS_local=+0.014694`, mean
`DeltaS_cross=+0.303038`, and mean `DeltaV` improved at every c. Because REP2
changes both dose and compute, it is a secondary sensitivity contrast rather
than the primary causal replay comparison.

## 6. Connection to B2.3

The reused STD artifacts exactly reproduced the closed B2.3 singleton
diagnosis:

| Quantity | STD |
| --- | ---: |
| states with negative cross-domain sum | 60/60 |
| states with positive local change | 33/60 |
| mean cross-domain sum | -0.369923 |
| mean local change | -0.020938 |
| mean DeltaV | -0.031059 |

Under REP, mean cross-domain change was `-0.038552`, mean local change was
`+0.005057`, and mean `DeltaV` was `-0.006134`.

B2.4 therefore shows that much of the cross-domain interference observed in
B2.3 is not inevitable for the same operational opportunity: it depends on
the tested development mechanism. Within this experiment, the supported
empirical chain is:

```text
historical replay
-> lower cross-domain interference
-> improved competence portfolio
-> higher future operational value.
```

## 7. What B2.4 does and does not establish

B2.4 establishes a reproducible effect of the specific REP substitution
relative to O50 under matched compute and matched effective opportunity
exposure. It also shows that the improvement in value is predominantly
associated with recovered non-target competence.

It does **not** identify catastrophic forgetting or any other internal cause;
distinguish among pseudo-label noise, optimization dynamics, or other latent
mechanisms; establish generalization outside PACS/VALIDATION or to other replay
policies; answer RQ0; establish a complete HLS policy; or provide a TEST
result. No portfolio-rescue claim is made.

## 8. Evidence and audit map

- frozen protocol:
  `docs/experimental_foundations/B24_PROTOCOL.md`;
- implementation and execution instructions:
  `experiments/pilots/b24_interference_controlled/`;
- run integrity, parent hashes, schedules, and validation provenance:
  `results/pilots/b24_interference_controlled/run_manifest.json`;
- replay IDs, labels, parent hashes, and buffer hashes:
  `results/pilots/b24_interference_controlled/replay_buffers.jsonl`;
- state genealogy and competence vectors:
  `results/pilots/b24_interference_controlled/development_states.jsonl` and
  `state_metrics.csv`;
- value rows and primary contrasts:
  `method_values.csv`, `primary_contrasts.csv`, and
  `competence_contrasts.csv`;
- frozen classifications:
  `classifications.csv`, `exact_regime_classifications.csv`, and
  `seed_summaries.csv`;
- concise run result: `summary.md`;
- operational timing: `timing_summary.json`;
- artifact-to-claim guide: `AUDIT_README.md`.

All reported identities were reconstructed to floating-point precision, no
NaN was present, compatibility passed, and TEST remained closed.
