# Small Problem World Gate

## Status and purpose

The Small Problem World is a deliberately constructed experimental fixture,
not an empirically estimated distribution of real problems. It was frozen from
the validated intrinsic production-surface geometry before observing team
performance. No team is executed in this gate.

Its purpose is controlled separation of environmental change, historical
novelty, representational mismatch, and exact recurrence. It neither combines
those descriptors nor introduces qualitative distance thresholds.

## Frozen world and internal representation

The finite agent repertoire and reset prior are

```text
Z_hat = ((.8,.2),(.5,.5),(.2,.8))
b_0   = (1/3,1/3,1/3).
```

The true six-problem sequence is

```text
A -> A' -> B -> B' -> C -> A
.8   .7    .3   .2   .5   .8
```

where each displayed scalar is `p` in `z(p)=(p,1-p)`. Each problem remains
fixed for the existing horizon `H=3`.

The world reuses `production_distance`, `change_magnitudes`,
`historical_novelties`, and `representational_mismatches`. It does not duplicate
the distance formula and does not modify CES, DISCOVER, finite Bayes, MIS-v2,
MPC, actions, or horizon semantics.

## Descriptor trajectory

| stage | p | C_t | N_t | M_t | represented |
|---|---:|---:|---:|---:|---|
| A | .8 | missing | missing | 0 | yes |
| A' | .7 | .15 | .15 | .15 | no |
| B | .3 | .40 | .40 | .15 | no |
| B' | .2 | .15 | .15 | 0 | yes |
| C | .5 | .39 | .24 | 0 | yes |
| A recurrence | .8 | .39 | 0 | 0 | yes |

Thus the two unrepresented symmetric problems have identical mismatch, the
two symmetric local transitions have identical distance, and C is historically
novel while exactly represented.

## Pairwise intrinsic distances

| | A | A' | B | B' | C |
|---|---:|---:|---:|---:|---:|
| A | 0 | .15 | .55 | .60 | .39 |
| A' | .15 | 0 | .40 | .55 | .24 |
| B | .55 | .40 | 0 | .15 | .24 |
| B' | .60 | .55 | .15 | 0 | .39 |
| C | .39 | .24 | .24 | .39 | 0 |

Capability exchange maps `A'=(.7,.3)` to `B=(.3,.7)` and `A=(.8,.2)`
to `B'=(.2,.8)`. The complete matrix is symmetric under this relabeling.

## Temporal convention and recurrence

At every new problem, UNKNOWN belief resets to the uniform prior over `Z_hat`.
The previous posterior is not carried forward; there is no environmental
transition model or familiarity prior. The team state `S`, when teams are run
in a later experiment, remains the sole persistent adaptive state under the
current prototype conventions.

The final A is exactly the same true problem as the initial A. Consequently,
any later behavioral or performance difference at recurrent A can arise from
persistent state such as developed `S`, not from persistence of A's previous
posterior. This must not be described as the agent remembering A.

No REFRAME, transfer, TMS, communication, environmental learning, or new
learning mechanism is present.

## Scientific limitations

This fixture provides controlled geometry, not ecological validity. It does
not estimate real problem frequencies, transition probabilities, novelty
thresholds, or representational repertoires. It demonstrates no team advantage,
adaptation, transfer, recognition of recurrence, or recognition of
misspecification. Those questions require later experiments using the unchanged
world fixture.

## Reproduction and artifacts

Run `python experiments/synthetic/small_problem_world_gate/run.py`. It writes:

- `world.csv`, containing every stage and its separate `C_t`, `N_t`, and `M_t`;
- `pairwise_distances.csv`, the complete matrix for the five unique problems;
- `control_summary.json`, representation, symmetry, recurrence, and temporal
  convention controls.
