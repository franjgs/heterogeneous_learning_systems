# Campaign 3 frozen development / held-out team split

## Status

This is a pre-performance experimental-design freeze derived solely from the
completed Campaign 3 quotient team-geometry characterization. It executes no
agent, policy, problem history, belief, action, reward, or performance process.

## Authoritative derivation

The frozen primary candidate pool, four anchors, canonicalization, distance,
farthest-point algorithm, and exact-coordinate tie-break are unchanged. The
algorithmic derivation is authoritative over human-readable IDs.

```text
S_dev =
G00 G04 G05 G07 F01 F02 F03 F04 F05 F06
F07 F08 F09 F10 F11 F12 F13 F14 F15 F16

S_heldout = F17 F18 F19 F20 F21 F22 F23 F24
```

Exact unrounded canonical matrices and source hashes are frozen in
`results/foundations/campaign3_team_split/`. All 28 matrices were independently
rederived from the hashed primary pool and reproduce the retained selection
sequence exactly.

## Held-out separation

For held-out team `H`, `d_dev(H)` minimizes `d_S` over only the 20 development
teams. It is distinct from insertion distance, which also includes previously
selected held-out teams.

| Team | Nearest development team | d_dev | Insertion distance |
|---|---|---:|---:|
| F17 | F04 | .405930 | .405930 |
| F18 | G04 | .404298 | .404298 |
| F19 | F01 | .401803 | .401803 |
| F20 | F14 | .399695 | .399695 |
| F21 | F06 | .370586 | .370586 |
| F22 | F08 | .363997 | .363997 |
| F23 | F04 | .360818 | .360818 |
| F24 | F03 | .356634 | .356549 |

The eight `d_dev` values have minimum `.356634`, median `.385140`, and maximum
`.405930`. No acceptance threshold is attached to these values.

## Intended claim and boundaries

The frozen claim is **GENERALIZATION TO GEOMETRICALLY SEPARATED UNSEEN TEAM
GEOMETRIES**, also described operationally as a **GEOMETRIC TEAM-SPACE STRESS
TEST**. Held-out teams remain inside the same frozen structural domain. They
are not a representative random sample, geometric extrapolation, out-of-domain
teams, a wholly unseen region, or a new class of team structures.

This claim remains separate from unseen-history generalization and
compositional/interpolative generalization to unseen generator kernels. A
wholly withheld team-space region is not part of Campaign 3.

Individual representatives depend on finite-pool discretization, while the
completed characterization found aggregate coverage reasonably robust. After
this freeze, the primary pool, metric, anchors, algorithm, order, exact
matrices, and split are immutable and cannot be replaced using behavioral or
performance evidence.
