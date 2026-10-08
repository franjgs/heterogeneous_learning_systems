# Campaign 3 team-space geometry characterization

## Scope

This is a pre-performance numerical-design characterization of

```text
S={S in [0,1]^(3x2): column sums=(1.5,1.5)}/S_3.
```

It uses no agents, policies, problems, histories, beliefs, actions, rewards,
performance, or Campaign 2 outcomes. It does not choose a final team count or
development/held-out team split.

## Quotient representation and distance

Canonicalization enumerates all six common row permutations, flattens each
matrix row-major, and chooses the lexicographic minimum. Exact canonical float
equality alone removes duplicates; geometrically close teams are never merged.
Constraint validation uses absolute tolerance `1e-12`.

The design-only distance is

```text
d_S(A,B)=min_P ||A-PB||_F.
```

It is invariant to a common row relabeling of either input. It is not a
cognitive, functional, behavioral, performance, or difficulty distance.

## Frozen anchors and candidate construction

The four anchors are recovered by parsing the frozen `TEAMS` literal in
`experiments/synthetic/campaign0_discriminative_capacity/run.py`; the runner is
not imported or executed. No anchors are permutation-equivalent.

The primary pool starts from 20,000 four-dimensional Halton points (bases
2,3,5,7), shifted modulo one by a seeded Cranley--Patterson shift
(`20261010`). Each capability column uses two coordinates and reconstructs the
third as `1.5-x-y`; exact polygon filtering enforces all bounds. It yields
11,245 valid and quotient-unique teams. A predefined dense validation pool
uses 40,000 raw points and seed `20261012`, yielding 22,462 valid unique teams.

Capability-column means are exactly .5 to displayed precision and marginal
quantiles are nearly symmetric across columns. Coarse 10x10 admissible-cell
occupancy CVs are .183 and .179; this includes unequal partial boundary-cell
areas and shows no evident column-specific asymmetry.

## Pure geometry results

A fixed 2,000-team subsample (seed `20261011`) gives 1,999,000 pairwise
distances: min `.00892`, Q05 `.25157`, Q25 `.40618`, median `.52171`, Q75
`.63465`, Q95 `.79115`, max `1.28579`. Nearest-neighbor distances have median
`.06817` and Q05/Q95 `.03496/.10069`.

The anchor nearest-neighbor distances are `.43301` for G00/G04 and `.66144`
for G05/G07. Both exceed every nearest-neighbor distance in the fixed pool
subsample, so the anchors are not unusually clustered by that diagnostic.

Anchor-initialized deterministic farthest-point selection was continued to 40.
Primary covering radius decreases from `.96469` at n=4 to `.31584` at n=40;
evaluation on the independent dense pool gives `.98180` and `.33100`.
Independent dense-pool optimization gives broadly similar coverage curves,
although selected locations are discretization-sensitive: selected-set
Hausdorff differences range roughly `.31--.41` after expansion. Thus aggregate
coverage is numerically stable while individual proposed points must not be
treated as uniquely determined by the continuous optimum.

Candidate boundary clearance has median `.08013` (Q05 `.00658`, Q95 `.26344`).
Farthest-point designs retain the exact boundary anchors and emphasize
near-boundary points; at n=40 selected median clearance is `.01349`. Interior
points remain present, but the sequence is not a uniform sample of the space.

Authoritative matrices, insertion distances, coverage curves, anchor matrix,
sampling diagnostics, validation pool, hashes, and provenance are retained in
`results/foundations/campaign3_team_geometry/`.

## Scientific boundary

The sequence and requested values of n are descriptive numerical diagnostics,
not thresholds or a frozen Campaign 3 team design. No `S_dev`, `S_heldout`, or
final team count is defined here. Any later choice requires a separate
pre-performance scientific decision.
