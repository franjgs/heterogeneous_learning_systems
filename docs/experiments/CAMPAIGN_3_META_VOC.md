# Campaign 3 META-VOC sequential comparison

## Design and interpretation

This development-only comparison tests whether an ex-ante estimate of the
benefit per extra computation selects useful DEEP invocations better than
frequency-matched random routing. It reuses the frozen C3.3 Ridge model and
does not retrain it or generate labels. Its target is the Q11-continuation
Monte Carlo Q11-minus-Q00 production advantage. That target is only a proxy:
it is not an unbiased estimate of the recursively adaptive sequential benefit
of invoking DEEP now.

FAST is the exact immediate Q00 action; DEEP is the existing Q11 prospective
operator. META-VOC predicts benefit with the existing C3.3 ex-ante features
`(S,b,tau)`, divides `max(0, predicted benefit)` by the estimated incremental
DEEP-minus-FAST wall time, and routes by validation-calibrated score ranks at
the preregistered 25%, 50%, and 75% operating points. The incremental cost was
measured, uncached, on a hash-fixed sample of 48 VALIDATION states at each of
remaining=2 and remaining=3, with FAST/DEEP call order alternated. Estimated
extra costs were 0.20920 s and 0.20979 s respectively. Cost estimates are
noisy machine-time measurements, not scientific utility weights.

Thresholds were set using the 1,400 nonterminal VALIDATION states only and
achieved exactly 350, 700, and 1,050 validation invocations. At remaining=1,
all methods use FAST and META-VOC does not call the selector or DEEP.

The sequential evaluation used one fresh history in every cell of the frozen
20 development teams × 21 development generator regimes (420 matched base
histories), with 12 problems and 36 decisions per history. FAST, DEEP, three
META-VOC variants, and three RANDOM variants each evolved separate capability
and belief paths under the same problem and observation-noise innovations for
each base history. No held-out team/kernel or prior evaluation history was
used. RANDOM received exactly the same total nonterminal DEEP-call count as its
META-VOC counterpart. Its locations were chosen by an independent, stable
hash-derived priority order over all eligible history/clock slots; the
retrospective META count determined only the number of slots, never their
locations.

Uncertainty intervals are paired, complete-history bootstrap percentile 95%
intervals (2,000 resamples; seed 20261014). Decision times are uncached
measured operator + selector times. No statistical equivalence margin was
specified or inferred.

## Observed results

| Policy | Mean cumulative `mu_true` | Measured seconds/history | Total measured seconds | Nonterminal DEEP calls / 10,080 | Invocation rate | Selector total (s) | Latency mean / median / q90 / q95 (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAST | 53.5388 | 0.0142 | 5.956 | 0 / 10,080 | 0.000% | 0.000 | 0.394 / 0.390 / 0.398 / 0.403 |
| DEEP | 55.0398 | 5.5491 | 2,330.638 | 10,080 / 10,080 | 100.000% | 0.000 | 154.143 / 227.918 / 234.642 / 236.079 |
| META-VOC-25 | 54.2735 | 1.3405 | 563.015 | 2,451 / 10,080 | 24.315% | 0.255 | 37.236 / 0.408 / 225.437 / 228.891 |
| RANDOM-25 | 54.1455 | 1.3625 | 572.239 | 2,451 / 10,080 | 24.315% | 0.000 | 37.846 / 0.392 / 230.298 / 232.965 |
| META-VOC-50 | 54.7260 | 2.7129 | 1,139.421 | 5,003 / 10,080 | 49.633% | 0.304 | 75.359 / 0.410 / 227.682 / 230.646 |
| RANDOM-50 | 54.4923 | 2.7403 | 1,150.931 | 5,003 / 10,080 | 49.633% | 0.000 | 76.120 / 0.395 / 231.644 / 233.461 |
| META-VOC-75 | 54.8948 | 4.0339 | 1,694.225 | 7,474 / 10,080 | 74.147% | 0.373 | 112.052 / 0.469 / 227.865 / 229.887 |
| RANDOM-75 | 54.7785 | 4.0722 | 1,710.309 | 7,474 / 10,080 | 74.147% | 0.000 | 113.116 / 0.434 / 232.182 / 233.775 |

| Contrast, META-VOC minus matched RANDOM | Paired mean performance difference [95% CI] | Paired mean computation difference, seconds/history [95% CI] |
|---|---:|---:|
| 25 | +0.1281 [-0.0522, +0.2979] | -0.0220 [-0.1871, +0.1503] |
| 50 | +0.2337 [+0.1030, +0.3686] | -0.0274 [-0.2276, +0.1697] |
| 75 | +0.1163 [+0.0090, +0.2307] | -0.0383 [-0.1982, +0.1204] |

Paired comparisons to the constant baselines are secondary reference points
(performance and compute differences are META-VOC minus baseline):

| Operating point | vs FAST: performance [95% CI] | vs FAST: seconds/history [95% CI] | vs DEEP: performance [95% CI] | vs DEEP: seconds/history [95% CI] |
|---|---:|---:|---:|---:|
| 25 | +0.7348 [+0.5552, +0.9303] | +1.3263 [+1.1615, +1.4834] | -0.7663 [-0.9395, -0.5848] | -4.2086 [-4.3711, -4.0499] |
| 50 | +1.1872 [+0.9574, +1.4071] | +2.6987 [+2.5130, +2.8873] | -0.3138 [-0.4242, -0.1983] | -2.8362 [-3.0290, -2.6366] |
| 75 | +1.3560 [+1.1169, +1.6097] | +4.0197 [+3.8707, +4.1761] | -0.1450 [-0.2331, -0.0546] | -1.5153 [-1.6775, -1.3648] |

Intervals span zero for all three computation contrasts: measured costs were
similar at their exactly matched call frequencies. The paired performance
interval spans zero at 25; at 50 and 75 its lower endpoint is above zero in
this development evaluation. META-VOC's mean performance was above FAST and
below DEEP at all three rates; these are secondary reference comparisons, not
the decisive META-VOC-versus-RANDOM test.

## Bounded conclusion

In these 420 fresh development histories, META-VOC produced a positive mean
paired performance difference over frequency-matched RANDOM at all three
predefined operating points. The history-bootstrap interval excluded zero at
50% and 75%, but not at 25%. The measured computation differences were small
relative to total computation and their intervals included zero. This is
initial evidence that ex-ante state-based routing can outperform random
placement of the same number of DEEP calls at two of the three evaluated
operating points; it is not evidence of equivalence at 25%, a universal
benefit, or an unbiased estimate of adaptive deliberation value. There was no
post-hoc selection of a single winning operating point: all three are reported.

Limitations include one replicate per team × kernel cell; the reused Ridge
target is a proxy rather than the sequential treatment effect; wall-clock
timing depends on machine load; frequency is exactly matched but measured
cost is not forced to match; and inference is limited to the frozen
development teams, kernels, simulator and fresh-history design.

## Reproduction and provenance

From the repository root:

```sh
python -m experiments.synthetic.campaign3_meta_voc.run --full --workers 8
pytest -q tests/test_campaign3_meta_voc.py tests/test_campaign3_fast_deep_meta.py
```

The full command refuses to overwrite an existing `sequential_full` output.
Artifacts (raw runs, trajectories, calibration sample, independent RANDOM
schedule, summary and SHA-256 manifest) are in
`results/campaigns/campaign3_meta_voc/sequential_full/`. The reused selector
hash is `1874b1f06a7122361677f5bb617132bd2eff3976fd1aa890d7152436fb59ba1d`.
