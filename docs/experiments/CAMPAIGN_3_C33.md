# Campaign 3.3: first supervised selector

## Scope

C3.2-A is closed. This first C3.3 implementation trains a transparent,
supervised rule selecting between the frozen Q00 and Q11 planners and compares
it with both fixed policies in fresh, development-only sequential histories.
The four-mode C3.2 labels remain unchanged. No held-out team or generator
regime enters fitting or sequential evaluation.

## Features and training target

The selector sees only the six entries of the pre-decision capability matrix
`S`, the three entries of belief `b`, and the known remaining decision clock
`tau`. The model is a standardized linear Ridge regressor. It predicts the
paired Monte-Carlo advantage `raw_mc_G(Q11)-raw_mc_G(Q00)` and selects Q11
when that prediction is nonnegative, otherwise Q00. The deterministic tie rule
therefore selects Q11 at zero predicted advantage.

C3.2 has distinct Q00- and Q11-continuation labels, and its protocol prohibits
averaging them or selecting a continuation because its labels appear easier to
predict. Before fitting, C3.3 fixes Q11 continuation as the proxy for the
intended persistent selector. Q00-continuation labels remain preserved and are
not modified. This is a modeling convention, not a claim that Q11 is optimal
or an oracle. The META policy is evaluated on its own sequentially evolving
states, so the Q11-continuation training proxy is imperfect by construction.

TRAIN fits the model. VALIDATION selects Ridge alpha from the frozen small
grid by mean paired policy regret (MSE breaks ties; lower alpha breaks any
remaining tie). DEVELOPMENT_TEST is opened once after selection and is never
used to revise the model. Its offline result is diagnostic and is not a
substitute for sequential evaluation.

## Sequential comparison

The sequential design crosses the 20 frozen development teams, 21 frozen
development generator regimes, and five fresh replicates (2,100 matched base
histories). On each history, Q00, Q11, and META independently evolve their
capability and belief states. Each policy receives the same generated
12-problem history and the same 36 standard-normal observation innovations;
only policy-induced actions and subsequent states diverge. Fresh deterministic
seed namespaces are separate from the Gate 2 and C3.2 namespaces.

The primary system outcome is cumulative `mu_true` over the full 12-problem
history. Paired differences are summarized at the complete base-history unit
with a deterministic 2,000-resample percentile bootstrap. These are descriptive
uncertainty intervals, not an equivalence test. Decision wall time is recorded
as an implementation-cost diagnostic; it is hardware/runtime dependent.

## Interpretation boundaries

This first version is a development comparison, not confirmatory generalization
and not a selector-equivalence test. The selector is trained on one raw
Monte-Carlo label per C3.2 selected state; label noise and continuation-proxy
mismatch remain. No arbitrary performance/computation scalarization is used.
No results are interpreted as statistical equivalence absent a justified
margin. The sequential study uses only S_dev and Phi_dev; S_heldout and
Phi_heldout are not executed.

## Reproduction

From the repository root, fit once (including the single frozen
DEVELOPMENT_TEST evaluation):

```sh
python experiments/synthetic/campaign3_c33/c33.py --train
```

Run a bounded smoke comparison (three histories by default):

```sh
python experiments/synthetic/campaign3_c33/c33.py --sequential --limit-histories 3
```

Run the complete 2,100-history sequential comparison only with the explicit
full flag:

```sh
python experiments/synthetic/campaign3_c33/c33.py --sequential --full --workers 1
```

Outputs are write-once under `results/campaigns/campaign3_c33/`; the default
CLI does not launch the full experiment. The `--workers` option changes only
execution parallelism, not task seeds or random streams.
