# META-VOC confirmatory protocol — C3-META-VOC-CONF-v1

Status: **pre-execution freeze**. This protocol and its machine-readable
manifest are fixed before any confirmatory physical history is generated.
The fitted predictor, calibrated costs, scores, thresholds and HLS mechanisms
are inherited from the completed development prototype.

## Scientific question and hypothesis provenance

The question is whether ex-ante `(S,b,tau)` identifies decisions at which
additional computation improves cumulative physical production relative to a
non-informative invocation rule using a comparable computational budget.

The primary comparison is **META-VOC-50 minus RANDOM-50**. The 50% operating
point was designated primary **after inspection of the development results**
in `CAMPAIGN_3_META_VOC.md`. This evaluation is independent in histories and
frozen before their execution, but the primary hypothesis was not selected
fully prospectively. META-VOC-25 and META-VOC-75 are fixed secondary
comparisons. No point will be selected retrospectively as the headline.

The primary physical endpoint is paired difference in cumulative `mu_true`
over 12 problems × three decisions. The primary computational endpoint is
paired difference in measured decision computation seconds per history,
including selector inference. These endpoints are interpreted jointly.

## Four frozen domains and sample size

The source of truth is the frozen team and generator split CSVs, with hashes
recorded in `pre_execution_manifest.json`. There is one **new independent
exogenous history per team × kernel cell**, replicate index 0. This is the
smallest complete factorial crossing of the existing partitions that retains
all four domains. It fixes 868 histories, 6,944 policy trajectories and
249,984 real decision records. No within-cell stochastic replication is
planned; domain-specific uncertainty, particularly G4, may therefore be wide.

| Domain | Team partition | Kernel partition | Cells / histories |
|---|---|---|---:|
| G1: unseen histories from known kernels/teams | development (20) | development (21) | 420 |
| G2: compositional/interpolative unseen kernels | development (20) | held-out (10) | 200 |
| G3: geometrically separated unseen teams | held-out (8) | development (21) | 168 |
| G4: both frozen held-out partitions | held-out (8) | held-out (10) | 80 |

Development teams: `G00 G04 G05 G07 F01 F02 F03 F04 F05 F06 F07 F08 F09 F10 F11 F12 F13 F14 F15 F16`.
Held-out teams: `F17 F18 F19 F20 F21 F22 F23 F24`.

Development kernels: `K01 K02 K03 K05 K06 K07 K10 K11 K13 K15 K16 K17 K20 K21 K23 K25 K26 K27 K31 K32 K33`.
Held-out kernels: `K00 K04 K08 K09 K14 K18 K19 K24 K28 K30`.
`K12/K22/K29` remain static aliases and are not independent treatments.
No new partition, team or kernel is created.

## Frozen predictor and eight policies

The existing C3.3 Ridge predictor is loaded read-only from
`results/campaigns/campaign3_c33/selector_model.json`. It has ten ex-ante
features in this order: `s11,s12,s21,s22,s31,s32,b0,b1,b2,tau`, where the
clock feature is divided by 36. The machine manifest stores the exact
standardization mean/scale, intercept and coefficients, alpha, and file hash.
Its target was the C3.2 single-rollout Q11-minus-Q00 Monte Carlo production
advantage under Q11 continuation. It is an imperfect proxy for recursively
adaptive sequential benefit.

FAST is the frozen immediate expected-production maximizer with canonical
belief model, 64-action enumeration and existing `EXACT_TOL` tie handling.
DEEP is the frozen `INFORMATION_AND_DEVELOPMENT` Q11 prospective operator.
No operator or environment transition is changed. The META-VOC score is

`max(0, Ridge(S,b,tau)) / estimated_incremental_seconds(remaining)`.

The denominator is the frozen uncached median paired DEEP-minus-FAST timing
estimate from 48 VALIDATION states at each remaining count:
`remaining=2: 0.209201959 s`, `remaining=3: 0.20978829100000002 s`.
This clock-stratified estimate does not model residual state dependence.
The existing positive numerical floor and finite-score handling remain fixed.
The three thresholds and ex-ante feature-hash tie cutoff are loaded **exactly**
from `results/campaigns/campaign3_meta_voc/sequential_full/calibration.json`:

| META-VOC point | Frozen score cutoff |
|---|---:|
| 25 | 0.22917335372443143 |
| 50 | 0.16708983036248765 |
| 75 | 0.11085071239096865 |

The complete tie keys are frozen in the machine manifest. No threshold or
cost predictor will be recalibrated using confirmatory data.

Evaluate `FAST`, `DEEP`, `META_VOC_25`, `RANDOM_25`, `META_VOC_50`,
`RANDOM_50`, `META_VOC_75`, `RANDOM_75`. At each terminal within-problem
decision (`remaining=1`), **all eight** use FAST; neither predictor nor DEEP
is invoked. Each policy starts from the same initial team but subsequently
evolves its own capabilities, belief, assignments and visited states.

## Independent seeds, exogenous CRN and RANDOM adapter

History ID is
`campaign3_meta_voc_confirmatory_v1:domain:team_id:kernel_id:0`.
Problem and observation seeds are `stable_seed(history fields, "problem")`
and `stable_seed(history fields, "noise")`, respectively. The existing
`stable_seed` is SHA-256 of pipe-separated components, first eight digest
bytes as big-endian integer modulo `2^63−1`. The complete allocation is
written and hashed **before execution**. Identifiers and numerical seeds are
checked against available prior C3 development/Gate data; the new namespace
also differs from PGCG calibration (`20261008`) and characterization
(`20261009`).

Within a base history, all policies receive the same 12 physical problems and
the same 36 standard-normal observation innovations. Real noisy observations
can differ because policies choose different actions. Beliefs reset at each
problem boundary; capabilities continue through the frozen MIS-v2 dynamics.

The development RANDOM runner used retrospective exact frequency matching.
This confirmatory adapter keeps that runner unchanged and instead freezes
nominal Bernoulli invocation probabilities **before execution**:
`p25=.25`, `p50=.50`, `p75=.75`. For every nonterminal clock and operating
point, an independent SHA-256 priority from
`campaign3_meta_voc_confirmatory_random_v1|history_id|point|clock|priority`
is divided by `2^63−1`; RANDOM invokes DEEP iff the priority is less than
its nominal `p`. The priority schedule is stored and hashed before histories
are generated. Different operating points have separate priority streams.
No realized META-VOC count or outcome affects RANDOM placement or budget.
Report both realized invocation frequencies and measured seconds.

## Analysis frozen before execution

Paired effects use complete matched histories as the resampling unit. For
each domain, draw its histories with replacement 2,000 times using analysis
seed `20261016`. Use the same domain-specific resample indices across
policies and outcomes. Report two-sided percentile 95% intervals. The global
primary estimate is the simple average of the **four domain mean paired
effects**; each bootstrap draw averages its four domain means with weight
`1/4`. Thus G1 does not dominate because it has more cells. Treat the fixed
team/kernel grid as the experimental design: one seed/cell means this
bootstrap cannot identify a separate within-cell stochastic variance or
establish generality to arbitrary new teams/kernels.

Primary report: global META-VOC-50 minus RANDOM-50 mean and 95% interval for
`mu_true` and measured seconds/history, absolute means for each policy,
realized DEEP rates, and selector overhead. Secondary, all fixed in advance:
the same contrasts by G1–G4; 25% and 75% contrasts; META-VOC versus FAST and
DEEP at all points; performance-cost curves; invocation rates; mean, median,
quartile, q90, q95 and q99 decision latency. No favorable subgroup selection.

The three-way scientific verdict uses a conservative joint rule:

- `CONFIRMATORY EVIDENCE FAVORABLE` only if the global primary performance
  interval is entirely positive **and** the global measured-computation
  interval is non-positive throughout.
- `UNFAVORABLE` only if the global performance interval is entirely negative
  **and** the global measured-computation interval is non-negative throughout.
- `INCONCLUSIVE` otherwise, including a performance interval excluding zero
  when the measured-computation interval still admits a positive difference.

The rule makes no claim of statistical equivalence and introduces no
performance-to-computation conversion factor. Outcomes in every domain and
all three operating points remain visible regardless of the verdict.

## Timing, validity and failure handling

Uncached `perf_counter_ns` encloses only the selected FAST or DEEP call plus
META-VOC's selector inference; terminal FAST calls are measured for all
policies. It does not include history generation, simulator dynamics, CSV
writing or analysis. Record worker count, platform, processor, Python and
package versions. Parallel load and call order can affect wall time; the
reported computation endpoint is a measured machine cost under this run.

No planned history or state is excluded. Before execution check all hashes,
factorial membership, seed disjointness, nominal RANDOM probabilities,
independent priority schedule, terminal handling and source integrity. A
missing/duplicate cell, invalid output, CRN disagreement, reward-sum mismatch
or modified frozen input stops execution/analysis. Complete batches are
checkpointed with hashes. An interruption may resume only the **same** frozen
allocation and inputs; completed batches are verified and skipped. Partial
failure information remains in `validation_failure.json`. No history is
replaced and the sample size is unchanged. Scientific analysis begins only
after all 868 histories, 6,944 policy runs and 249,984 decisions validate.

After execution, verify every history has all eight 36-decision trajectories,
consistent exogenous stream hashes, contiguous state transitions,
terminal FAST routing, positive recorded computation durations and exact
equality of each run's cumulative `mu_true` to its trajectory sum. Preserve
the original development outputs and all frozen algorithm inputs.

## Reproducibility and outputs

From the repository root, in this exact order:

```sh
python -m experiments.synthetic.campaign3_meta_voc.confirmatory --freeze
python -m experiments.synthetic.campaign3_meta_voc.confirmatory --verify
python -m experiments.synthetic.campaign3_meta_voc.confirmatory --execute --workers 8
python -m experiments.synthetic.campaign3_meta_voc.analyze_confirmatory --run
```

The pre-execution manifest and seed/RANDOM allocation are under
`results/foundations/campaign3_meta_voc_confirmatory/`. Raw checkpointed and
consolidated results, analysis CSVs, summary JSON, SHA-256 manifests and
Figures 1–4 (SVG/PDF) are under
`results/campaigns/campaign3_meta_voc_confirmatory/`. Protocol, adapter and
analysis source hashes in the pre-execution manifest must match at every
phase. The figures and machine tables are regenerated solely from validated
raw confirmatory records.
