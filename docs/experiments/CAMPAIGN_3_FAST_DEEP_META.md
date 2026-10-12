# Campaign 3 conditional deliberation: FAST / DEEP / META

## Frozen components and routing

FAST chooses the action maximizing immediate belief-expected production with
the existing canonical hypothesis model, `JOINT_ACTIONS`, and `EXACT_TOL`.
It does not evaluate prospective transitions. Its selected action is exactly
Q00's because Q00's continuation is independent of the candidate current
action. The Q00 implementation was not changed. DEEP is the unchanged Q11
operator (`INFORMATION_AND_DEVELOPMENT`).

META reuses the existing C3.3 Ridge model and fitted coefficients without
retraining. At nonterminal decisions it predicts the existing ex-ante
Q11-continuation Monte-Carlo advantage: `Q11` is invoked for predicted
advantage `>= 0`; otherwise FAST is accepted. The model predicts a production
advantage, **not computational utility**. At one remaining decision META
uses FAST directly without predictor or DEEP invocation because the operators
are action-equivalent. A FAST route never computes DEEP.

The only META inputs are the six `S` entries, three `b` entries, and normalized
known clock `tau/36`. Physical state labels, generator identities, rewards,
and future information are not inputs.

## Sequential development comparison

The minimal complete development crossing used one fresh independent history
per each of the 20 frozen development teams × 21 development generator kernels:
420 matched base histories. FAST, DEEP, and META each independently evolved
their own capabilities, beliefs, actions, and states through 12 problems (36
decisions). Within each base history, all three used the same 12 physical
problem values and 36 standard-normal observation innovations. No held-out
team or kernel was used. This is a one-replicate-per-cell prototype comparison,
not confirmatory generalization.

Mean cumulative physical performance (`mu_true`) was:

| Policy | Mean cumulative `mu_true` |
|---|---:|
| FAST | 53.29952 |
| DEEP | 54.66907 |
| META | 54.66117 |

Paired differences use percentile 95% intervals from 2,000 resamples of
complete matched base histories (seed 20261012):

| Contrast | Mean difference | 95% interval |
|---|---:|---:|
| DEEP − FAST | 1.36956 | [1.11809, 1.62514] |
| META − FAST | 1.36166 | [1.10780, 1.61275] |
| META − DEEP | −0.00790 | [−0.01465, −0.00241] |

META's aggregate performance was close to DEEP in these development histories,
but no equivalence margin was defined; equivalence is not claimed. META was
not a learned computational-utility rule and its nonterminal routing invoked
DEEP frequently, so these results do not establish an efficient or general
conditional-deliberation strategy.

## Actual compute and invocation accounting

META made 15,120 decisions: 9,785 DEEP invocations (64.72% of all decisions,
97.07% of nonterminal decisions), 295 FAST acceptances (1.95% of all; 2.93% of
nonterminal), and 5,040 terminal FAST decisions (33.33%). No DEEP operator ran
on a FAST-accepted or terminal route.

Uncached measured decision computation across the experiment:

| Policy | Total measured decision compute | Mean / median / p90 latency |
|---|---:|---:|
| FAST | 5.93 s | 0.392 / 0.389 / 0.395 ms |
| DEEP | 2,320.38 s | 153.464 / 227.066 / 233.409 ms |
| META | 2,199.09 s | 145.442 / 222.435 / 226.031 ms |

These are summed per-decision wall-clock measurements recorded in the
eight-worker run and therefore reflect contention on that machine. Paired
per-history compute differences (same bootstrap procedure) were:

| Contrast | Mean compute difference | 95% interval |
|---|---:|---:|
| DEEP − FAST | 5.5106 s/history | [5.5032, 5.5176] |
| META − FAST | 5.2218 s/history | [5.1796, 5.2618] |
| META − DEEP | −0.2888 s/history | [−0.3336, −0.2488] |

A separate deterministic 60-state microbenchmark stratified evenly across
remaining decisions `{1,2,3}` distinguished cold/uncached operator calls from
warm exact-action memoization (META still paid selector inference). Cold
median/p90 latency was FAST `0.376/0.399 ms`, DEEP `218.123/221.253 ms`, META
`211.696/213.846 ms`; warm cached median was FAST `0.000292 ms`, DEEP
`0.000938 ms`, META `0.007667 ms`. Cache figures are lookup diagnostics, not
the uncached sequential cost. The cached benchmark is hardware- and cache-key-
specific.

## Persistence note and limitations

The first simulation process completed and persisted both raw tables, then
raised a serialization error while writing the manifest because task/model
payload tuples were treated as dictionaries. The raw outputs were retained
unchanged. Counts, CRN alignment, analysis, and provenance were reconstructed
from those persisted tables without rerunning simulations; the incident is
preserved in `results/campaigns/campaign3_fast_deep_meta/sequential_full/execution_failure.json`.
The exact wall time was not recoverable after that post-run exception. The
measured per-decision compute totals remain available in the analysis summary.

The comparison is development-only, has one history per team×kernel cell, and
does not support confirmatory generalization. The model's output estimates
production advantage, not computational utility. Its predominantly DEEP
routing is a negative result for substantial deliberation avoidance in this
prototype. No physical model, inference, MIS-v2, policy operator, generator,
or frozen split was changed.

## Reproduction

```sh
pytest -q tests/test_campaign3_fast_deep_meta.py tests/test_finite_problem_belief.py
python experiments/synthetic/campaign3_fast_deep_meta/run.py --full --workers 8
```

The driver defaults to a two-cell diagnostic; `--full` explicitly runs the
420-cell minimal complete development comparison. The fitted C3.3 model is
read-only. Existing C3.2/C3.3 result artifacts are not overwritten.
