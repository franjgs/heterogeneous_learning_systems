# Campaign 3 Problem-Generator Calibration Gate (PGCG)

## Status and scope

PGCG is a generator-only calibration and characterization gate under the
authoritative C3.0 specification frozen at `3c282f4`. It neither invokes nor
inspects agents, Q00/Q10/Q01/Q11, beliefs, capabilities, MIS-v2, rewards, or
performance. Its generated histories are calibration data and are ineligible
for later C3 development or confirmation.

## Frozen protocol

The physical domain remains `p in [0,1]`; the initial C3 generator domain is
`[.2,.8]`. MOVE is

```text
p'=reflect(p+sigma*u;.2,.8), p~Uniform(.2,.8), u~Normal(0,1).
```

Calibration uses common `p,u` draws, seed `20261008`, `N=100000`, and candidates
`.01,.02,.04,.08,.16,.32`. Its primary descriptor is median `d_R(p,p')`.
Every ordered triple maximizes the minimum adjacent log-median separation;
ties use the lexicographically first candidate-index triple. Candidate removal
after inspection is prohibited. Acceptance requires ordered realized-change
distributions, paired-CRN and 12-bin diagnostics, and no unregistered
reflection-pathology threshold.

The mathematical degree-4 STAY/MOVE/RETURN simplex has 15 compositions. Pure
RETURN `(0,0,1)` is structurally non-initializable and is not given an
artificial fallback. The operational design therefore has 14 executable
compositions and, after representing MOVE-free compositions once, 34 unique
kernels.

Histories start with `p_1~Uniform(.2,.8)`. RETURN samples uniformly over the
distinct eligible set `R_j={p_k:k<j,p_k!=p_j}`; repeated occurrences do not
increase probability. If empty, RETURN is unavailable and positive STAY/MOVE
weights are renormalized. MOVE has no novelty constraint.

Characterization uses seed `20261009`, 10,000 independent 12-problem histories
per kernel. This is a descriptive calibration size, not a later C3 sample
size. Retained outputs cover nominal/realized mechanisms, unavailable RETURN,
renormalization, MOVE reflection, C/N/M, unchanged-run lengths, distinct
problems, strict returns, and first RETURN feasibility. Exact raw histories and
transition flags are retained in compressed machine-readable form.

## Failure and separation rules

The gate stops on MOVE ordering failure, scientifically ambiguous reflection,
count failure, conflict with strict RETURN, forbidden agent/performance
dependency, or another unspecified scientific choice. Nominally different
near-neighbours are flagged rather than merged; no post-hoc collapse threshold
is introduced.

PGCG itself did not choose `Phi_dev/Phi_heldout` or future histories. The
subsequent [crossed generator split](CAMPAIGN_3_GENERATOR_SPLIT.md) freezes that
structural partition before any fresh independent history is drawn and
distinguishes unseen histories from known kernels from unseen generator
regimes.

## Results

**PGCG PASS.** The deterministic maximin rule selected
`sigma_L=.01`, `sigma_M=.04`, and `sigma_H=.32`.

| sigma | mean C | sd C | Q10 | Q25 | Q50 | Q75 | Q90 | Q95 | reflection |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| .01 | .010276 | .007892 | .001599 | .004054 | .008598 | .014759 | .021288 | .025509 | 1.329% |
| .02 | .020287 | .015572 | .003137 | .007999 | .016958 | .029156 | .042107 | .050385 | 2.655% |
| .04 | .039479 | .030281 | .006088 | .015539 | .032998 | .056839 | .081993 | .097910 | 5.384% |
| .08 | .074724 | .057005 | .011466 | .029399 | .062574 | .108149 | .155422 | .185135 | 10.677% |
| .16 | .132223 | .099102 | .020132 | .051976 | .111789 | .192534 | .274356 | .324279 | 21.386% |
| .32 | .201090 | .141059 | .031881 | .082808 | .177578 | .299327 | .410566 | .467968 | 41.381% |

The complete empirical quantile functions were ordered for every adjacent
candidate pair, and all reported quantiles and medians were strictly ordered;
selected-scale bin medians were ordered in all 12 initial-p bins. Adjacent
paired-CRN ordering rates decreased from 98.988% to 83.731% as reflection
increased. The `.32` reflection rate is therefore a material diagnostic to
retain, but it did not reverse global quantile or conditional-bin ordering and
no unregistered rejection threshold was applied.

The verified design has 15 mathematical compositions, 14 executable
compositions, and 34 unique executable kernels. Characterization retained
340,000 histories and 3.74 million transitions. Across kernels, realized mean
`C` ranged from 0 to .205196, mean novelty from 0 to .081289, mean mismatch
from .095616 to .097391, mean distinct visited values from 1 to 12, and mean
strict returns from 0 to 7.5207. Complete distributions and index-specific
frequencies are retained in the result tables and compressed raw arrays.

Four MOVE-free executable kernels (`K12|K22|K29|K33`) are exactly equivalent
in their problem-history distribution: with only one initial value they cannot
create a distinct value, so RETURN stays unavailable and positive STAY mass
produces a constant history. They remain separate nominal kernels and are
flagged for later scientific review; PGCG does not merge them. Ranked nearest
descriptor pairs are descriptive diagnostics without a collapse threshold.
