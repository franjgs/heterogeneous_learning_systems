# Campaign 1 — test range gate

## Status

This is a pre-results, team-free design validation. It freezes a small geometric test range before Campaign 1 execution. No G00–G08 configuration was run; `team_executions=0`. Scenario selection uses no team performance, Campaign 0 winner, adaptive outcome, or seed-dependent result.

## Pre-specified design

The frozen problem points are A `.8`, U `.7`, C `.5`, V `.3`, and B `.2`; A/C/B are represented in `Z_hat`, while U/V are not. The eight histories are:

| ID | Exact p sequence | Intended design role |
|---|---|---|
| TR-PR | `.8,.8,.8,.8,.8,.8` | represented persistence |
| TR-PM | `.7,.7,.7,.7,.7,.7` | mismatched persistence |
| TR-G | `.8,.7,.5,.3,.2,.8` | gradual displacement, abrupt return |
| TR-J | `.8,.2,.3,.5,.7,.8` | abrupt displacement, gradual return |
| TR-R | `.8,.7,.8,.7,.8,.8` | exact recurrence |
| TR-D | `.8,.7,.5,.3,.2,.2` | continued displacement, then persistence |
| TR-HA | `.8,.7,.5,.2,.3,.8` | familiar return after intervening history A |
| TR-HB | `.8,.3,.2,.5,.7,.8` | familiar return after intervening history B |

The future probes are exactly G00, G04, G05, and G07. They are probes, not competitors, and are not executed here. The future primary condition is DISCOVER+DEVELOP with eta `.35`, rho `.5`, sigma `.10`, horizon three, current CES, finite Bayesian DISCOVER, MPC, MIS-v2, belief reset between problems, and persistent capability state. NO-DEVELOP and KNOWN-z are candidate mechanistic controls whose replication counts and final protocol remain unfrozen.

## Geometrically verified properties

The pairwise matrix, independently computed through the existing `production_distance`, is:

| | A | U | C | V | B |
|---|---:|---:|---:|---:|---:|
| A | 0 | .15 | .39 | .55 | .60 |
| U | .15 | 0 | .24 | .40 | .55 |
| C | .39 | .24 | 0 | .24 | .39 |
| V | .55 | .40 | .24 | 0 | .15 |
| B | .60 | .55 | .39 | .15 | 0 |

Descriptor sequences use `—` for the intentionally missing first-step C/N value. `R/U` denotes represented/unrepresented. Recurrence locations are one-based.

| ID | C sequence | N sequence | M sequence | Representation | Recurrence locations |
|---|---|---|---|---|---|
| TR-PR | `—,0,0,0,0,0` | `—,0,0,0,0,0` | `0,0,0,0,0,0` | `RRRRRR` | `2,3,4,5,6` |
| TR-PM | `—,0,0,0,0,0` | `—,0,0,0,0,0` | `.15,.15,.15,.15,.15,.15` | `UUUUUU` | `2,3,4,5,6` |
| TR-G | `—,.15,.24,.24,.15,.60` | `—,.15,.24,.24,.15,0` | `0,.15,0,.15,0,0` | `RURURR` | `6` |
| TR-J | `—,.60,.15,.24,.24,.15` | `—,.60,.15,.24,.15,0` | `0,0,.15,0,.15,0` | `RRURUR` | `6` |
| TR-R | `—,.15,.15,.15,.15,0` | `—,.15,0,0,0,0` | `0,.15,0,.15,0,0` | `RURURR` | `3,4,5,6` |
| TR-D | `—,.15,.24,.24,.15,0` | `—,.15,.24,.24,.15,0` | `0,.15,0,.15,0,0` | `RURURR` | `6` |
| TR-HA | `—,.15,.24,.39,.15,.55` | `—,.15,.24,.39,.15,0` | `0,.15,0,0,.15,0` | `RURRUR` | `6` |
| TR-HB | `—,.55,.15,.39,.24,.15` | `—,.55,.15,.24,.15,0` | `0,.15,0,0,.15,0` | `RURRUR` | `6` |

All proposed numerical claims are correct; no geometric correction is required.

### Controlled contrasts

- **TR-PR/TR-PM:** both have zero change after step one. They differ in representation: M is always zero versus always `.15`.
- **TR-G/TR-J:** same point multiset `{A:2,U:1,C:1,V:1,B:1}`, same transition-distance multiset `{.15,.15,.24,.24,.60}`, and different ordering. TR-J is the exact temporal reversal of TR-G.
- **TR-R/TR-D:** recurrence locations are `(3,4,5,6)` versus `(6)`. Total change is `.60` versus `.78`; this is deliberately not a matched-total-change contrast.
- **TR-HA/TR-HB:** same point and transition-distance multisets, same A endpoints, final `N=M=0`, and different intervening order. TR-HB is the exact temporal reversal of TR-HA.

No two histories are identical or duplicates under the complete ordered C/N/M, representation, recurrence, and point-label signature. Partial structural redundancy is intentional: the persistence pair shares C/N; the two reversal pairs share content and transition multisets. Capability exchange maps A↔B and U↔V while preserving distances, but no complete candidate history is the capability-exchanged image of another candidate.

## Campaign 0 contamination and prior observation

- **TR-PR:** identical to Campaign 0 H2; `PRIOR-DIAGNOSTIC / NOT OUT-OF-SAMPLE`.
- **TR-G, TR-J, TR-HA, TR-HB:** new orderings of the exact H0/H1 problem multiset and endpoints. Campaign 0 already showed that order can matter for other orderings of this content; these are `PRIOR-DIAGNOSTIC / NOT OUT-OF-SAMPLE`, though their own team outcomes are unobserved.
- **TR-R:** structural recurrence analogue of Campaign 0 H3, replacing B (`.2`) with U (`.7`); `PRIOR-DIAGNOSTIC / NOT OUT-OF-SAMPLE`.
- **TR-PM and TR-D:** no identical Campaign 0 execution and classified `PRE-PERFORMANCE CAMPAIGN-1 SCENARIO`.

These labels record provenance; they do not remove scenarios or predict results.

## Intended adaptive challenge

The range is designed to expose the frozen agents to persistent represented/mismatched problems, alternative orderings of fixed content, recurrence versus continued displacement, and familiar return after different histories. These are challenge descriptions derived from problem geometry, not claims that adaptation will help or hurt.

## Empirically unknown

The gate does not establish whether adaptation is valuable or negligible; whether prior development helps or is a liability; whether configurations are sensitive or insensitive; any performance ordering; or Campaign 1 PASS/PARTIAL/FAIL. Geometry cannot answer these questions. Theory consolidation and literature review precede any final Campaign 1 protocol.

## Artifacts

The machine-readable fixture is `src/hls/campaign1_test_range.py`. Gate artifacts are under `results/foundations/campaign1_test_range_gate/`: the five-point distance matrix, step descriptors, history summaries, and pre-experiment manifest.
