# Campaign 3.3 results: first supervised selector

## Design and model

The selector was a standardized linear Ridge regressor over only the six
pre-decision entries of `S`, the three belief probabilities, and `tau/36`.
Its target was the C3.2 Q11-continuation paired Monte-Carlo advantage
`raw_mc_G(Q11)-raw_mc_G(Q00)`. This continuation was fixed before fitting as a
persistent-selector proxy; no continuation averaging or retrospective
continuation selection was used. META selects Q11 when predicted advantage is
nonnegative and Q00 otherwise.

TRAIN supplied 6,300 states. VALIDATION selected alpha `10.0` from
`{0.001, 0.01, 0.1, 1, 10}` by paired decision regret, with MSE and then lower
alpha as deterministic tie-breaks. Validation regret was `0.02135` production
units/state. DEVELOPMENT_TEST was evaluated once after selection (2,100
states): regret `0.02890`, MSE `0.18656`, sign accuracy `87.24%`. These are
offline diagnostics on single Monte-Carlo labels, not sequential-policy
performance.

## Sequential development comparison

Fresh histories crossed 20 `S_dev` teams, 21 `Phi_dev` kernels, and five
replicates per cell: 420 cells, 2,100 base histories, 12 problems/history.
Q00, Q11, and META each independently evolved `S` and `b` for 36 decisions
per history. The three policies shared the same physical problem sequence and
standard-normal observation innovations within each base history. There were
6,300 policy runs and 226,800 policy-decision rows (75,600 decisions/policy).
No held-out team or kernel was used.

Mean cumulative `mu_true` was:

| Policy | Mean | SD | Median |
|---|---:|---:|---:|
| Q00 | 53.30565 | 2.83397 | 52.36962 |
| Q11 | 54.69695 | 3.31465 | 54.06206 |
| META | 54.69220 | 3.31362 | 54.05867 |

Paired differences use a 2,000-replicate bootstrap of complete base histories,
resampled within each team × kernel cell. Intervals are descriptive 95%
percentile intervals; they are not an equivalence test.

| Paired difference | Mean | Median | 95% bootstrap interval | Positive / zero / negative histories |
|---|---:|---:|---:|---:|
| Q11 − Q00 | 1.39130 | 0.21386 | [1.29855, 1.48738] | 57.19% / 17.71% / 25.10% |
| META − Q00 | 1.38655 | 0.20345 | [1.29057, 1.47902] | 56.90% / 18.19% / 24.90% |
| META − Q11 | −0.00475 | 0.00000 | [−0.00734, −0.00224] | 1.71% / 95.95% / 2.33% |

The META–Q11 aggregate difference is small in these development histories,
but no equivalence margin was preregistered or justified; equivalence is not
claimed. The paired sign distribution also retains nonzero favorable and
unfavorable cases. These outcomes do not establish superiority or generalize
beyond the frozen development design.

## Computational cost and limitations

The full three-policy execution took 1,290.5 seconds wall-clock with eight
workers. An isolated, uncached decision-operator timing diagnostic on 64
existing pre-decision states gave median / 90th-percentile milliseconds:

| Decision rule | Median ms | 90th percentile ms |
|---|---:|---:|
| Q00 | 0.374 | 0.395 |
| Q11 | 0.373 | 0.399 |
| META (prediction plus selected planner) | 0.380 | 0.416 |

These timings are machine-dependent and are not converted into a performance
penalty or scalarized objective. Per-row timings collected during the parallel
run can benefit from pure-action memoization across identical policy states;
the isolated timing diagnostic is therefore the appropriate comparison of
decision computation. Training runtime was not separately instrumented.

This is an initial on-policy development comparison, not confirmatory
generalization. The training target is one Monte-Carlo realization and uses a
Q11 continuation proxy although META later continues with its own decisions.
No causal, equivalence, or universal-value claim follows. C3.2 source labels
and the frozen DEVELOPMENT_TEST partition remain unchanged.

## Reproduction and provenance

```sh
python experiments/synthetic/campaign3_c33/c33.py --train
python experiments/synthetic/campaign3_c33/c33.py --sequential --full --workers 8
python experiments/synthetic/campaign3_c33/c33.py --summarize
```

The fit is reproducible from the preserved C3.2 inputs. Their SHA-256 hashes
are:

| Input | SHA-256 |
|---|---|
| C3.2 TRAIN labels | `1891e5c7f32b70ff5628a5dd1055aca751e30363b5a783593ff07238daf287c9` |
| C3.2 VALIDATION labels | `64a1743c27e92cdd82a559a14512e84dc8e1d7c2469e3321a3d9c6ca354b652f` |
| C3.2 DEVELOPMENT_TEST labels | `4a29834948123269926b4bf137f59ecbd34a2d82d91dab754a6c27156a894cbc` |
| C3.2 allocation | `3fbb198c20da035d2b9417487f5e0320ec8395fb204eb7329815878beaa6e1d7` |

Generated model and reports are under `results/campaigns/campaign3_c33/`.
The full sequential raw-table hashes are recorded in
`sequential_full/execution_manifest.json` and `analysis_summary.json`.
