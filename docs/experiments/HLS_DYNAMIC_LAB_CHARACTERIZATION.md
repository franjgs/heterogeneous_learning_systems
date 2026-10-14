# HLS dynamic laboratory characterization pilot

## Purpose and scope

This bounded pilot asks when existing information-using/adaptive policies
perform differently in the integrated dynamic laboratory. It is descriptive
engineering-science characterization, not a new campaign or a claim that
coordination always improves performance. No simulator physics, MIS-v2,
DISCOVER, estimator, or policy implementation was changed. Results are isolated
in `results/experiments/hls_dynamic_characterization/`.

The runner compares existing policies and information/learning settings under
paired problem/noise seeds. It deliberately reports CES production, functional
success, effort/resource accounting, and estimation error separately; it does
not combine them into an arbitrary net utility.

## Experimental matrix

The primary block crosses four conditions—stationary/switching demand and
similar/heterogeneous initial teams—with decision horizons H=1 and H=3, four
seeds (0–3), and seven existing-policy arms. Each sequence has eight physical
problems. This yields 224 runs. In stationary sequences the same visible demand
regime is used throughout; in switching sequences EAST is used for four
problems and WEST for four. The existing generator still draws the latent
problem type per problem in either condition, so “stationary” here means
stationary visible demand regime, not an invariant realized problem.

| Contrast | Compared arms | What it can say | Main confound/limit |
|---|---|---|---|
| Planning/beliefs | `DiscoverBeliefPolicy` vs `GreedyAdaptive`, ORACLE, LI off | Existing belief/planning policy versus estimated-model greedy policy | Information and planning operator differ together |
| Information | Greedy ORACLE vs PARTIAL_STATIC, and PARTIAL_LEARNING vs PARTIAL_STATIC | Cost of an intentionally biased fixed estimate; effect of updating that estimate from individual observations | Not an oracle-randomized information treatment; partial estimate is common prior |
| Individual learning | Greedy ORACLE, LI off/on at eta=.03; separate eta=.25 comparison | Paired effect of enabling the existing individual development transition in these conditions | Development changes capabilities and later experience endogenously |
| Learning rate | LI on at eta=.03 vs eta=.25 | Sensitivity to declared learning rate | Only two rates; no general response curve |

Similar teams start at `((.55,.45),)*3`; heterogeneous teams at
`((.82,.18),(.18,.82),(.50,.50))`. Partial modes start from
`((.55,.45),)*3`. Slow and fast declared learning rates are .03 and .25 per
skill. Belief prior is .5, aggregate observation sigma .08, and individual
competence-observation sigma .06. Identical seed-derived exogenous streams are
used within each paired set.

A separate organizational train/evaluate block contributes 32 runs. Existing
`ExploreThenGreedy` is compared with organizational updates enabled or disabled,
with individual learning off. The ON policy performs complete action sweeps
(64 actions per task context), updates its table from observed rewards, then
evaluates with the resulting state frozen. OFF repeats its initial action and
does not update. Stationary evaluation is 32 repetitions; switching evaluation
has 16 EAST then 16 WEST problems. This is a bundled contrast of exploration,
experience retention, and reward-dependent table update—not an isolated
estimate of a generic organizational-learning effect.

The run installs `resource_cost_per_unit=1` only as an observer, so recorded
resource cost equals effort. It does not affect CES reward, choices, or
transitions. Costs therefore document resource use; they are not evidence of a
cost-adjusted policy ranking.

## Results

The run completed: 256 run records and 5,632 decision records. The summary
below averages cumulative `mu_true` over the four scenarios and four seeds at
each H; functional success and competence-estimation MAE are also shown.

| Existing arm | H=1 CES | H=1 success | H=1 MAE | H=3 CES | H=3 success | H=3 MAE |
|---|---:|---:|---:|---:|---:|---:|
| Greedy, ORACLE, LI off | 7.223 | 1.000 | 0.000 | 21.668 | 1.000 | 0.000 |
| DISCOVER, ORACLE, LI off | 7.435 | 0.891 | 0.000 | 24.795 | 0.755 | 0.000 |
| Greedy, PARTIAL_STATIC, LI off | 5.042 | 1.000 | 0.115 | 15.127 | 1.000 | 0.115 |
| Greedy, PARTIAL_LEARNING, LI off | 6.896 | 1.000 | 0.081 | 21.401 | 1.000 | 0.076 |
| Greedy, ORACLE, LI on, eta=.03 | 7.595 | 1.000 | 0.000 | 24.915 | 1.000 | 0.000 |
| Greedy, ORACLE, LI on, eta=.25 | 9.388 | 1.000 | 0.000 | 32.256 | 1.000 | 0.000 |

Mean per-condition paired reward differences and seed-cluster bootstrap 95%
percentile intervals (B=2,000; seed 20261015) are in
`paired_contrasts.csv`. At H=3, DISCOVER minus Greedy was positive in each of
the four conditions: +1.788 [0.318, 2.702] for stationary/heterogeneous,
+4.068 [2.648, 5.944] stationary/similar, +2.238 [1.232, 3.693]
switching/heterogeneous, and +4.416 [3.458, 4.970] switching/similar. At H=1
the corresponding intervals all included zero. Yet DISCOVER functional success
was lower: at H=3 it averaged .755 versus 1.000 for Greedy. This reflects
different objectives/decision behavior; it is not an unconditional policy
dominance result. Across the 32 scenario-seed comparisons, DISCOVER reward was
higher in 26 and lower in 6.

For heterogeneous teams, updating partial estimates versus keeping them static
improved mean cumulative CES by +3.541 [3.339, 3.786] at H=1 and +12.049
[11.315, 12.790] at H=3 in stationary demand; under switching demand the
differences were +3.873 [3.789, 3.920] and +13.045 [13.039, 13.057]. In
similar-team conditions the paired difference was exactly zero. Static partial
estimates versus ORACLE were also tied in similar conditions and lower in all
heterogeneous conditions. Because the partial estimates were deliberately
biased, this supports only the value of updating in this tested setup, not a
general causal effect of information quality.

With ORACLE information, enabling individual learning at eta=.03 increased
mean cumulative CES by +0.245 to +0.499 at H=1 and +2.181 to +4.303 at H=3
across the four conditions. Eta=.25 versus .03 with LI on gained +1.226 to
+2.354 at H=1 and +5.188 to +9.522 at H=3. Each of these contrasts was positive
in all 32 paired scenario-seed comparisons for LI on/off and rate comparison.
Functional success was saturated at 1.0 for the Greedy arms, so it did not
discriminate these production changes.

In the organizational block, ON achieved frozen-state EVAL success 1.0,
compared with 0 for OFF; paired cumulative CES differences were +17.846 in
stationary and +14.763 in switching evaluation. However, OFF is an especially
weak comparator: it repeats the first action, while ON explores all 64 actions
and updates a reward-conditioned table. ON also used 64 more units of effort in
stationary evaluation and 80 more in switching evaluation. These deterministic
contrasts demonstrate that this implementation can retain and use the explored
table; they do not isolate learning from exploration/memory, and the four seed
rows are identical repetitions, not independent stochastic evidence.

## Interpretation and validity limits

- **Observed information-related pattern:** updating competence estimates
  helped only for the heterogeneous team with the deliberately common, biased
  starting estimate; the similar team showed no effect.
- **Observed individual-development pattern:** the tested MIS-v2 learning
  settings raised CES production while success was already saturated. This is
  condition-specific and not a population estimate.
- **Planning/belief pattern:** longer H showed greater CES reward for DISCOVER
  in this design, alongside lower functional success. The policy contrast
  bundles belief-sensitive planning and operator differences; it cannot
  identify either mechanism alone.
- **Organizational update pattern:** the train/evaluate result is not a clean
  causal attribution because exploration and reward use differ, and the OFF
  policy repeats one action. It should be treated as an implementation
  diagnostic, not a fair adaptive-versus-nonadaptive effectiveness estimate.
- The four seeds provide very limited uncertainty information. Bootstrap
  resampling is at the seed/history level, but scenario cells are deliberately
  small; intervals are descriptive and do not justify broad inference. In the
  organizational block, seed replicates are deterministic duplicates, so its
  point intervals are not inferential confidence intervals.
- The H=1/H=3 comparison is a bounded horizon contrast, not a general horizon
  response. The switching sequence is a single predetermined EAST-to-WEST
  change. No held-out generalization was evaluated.
- “Rendimiento colectivo neto” is not calculated: no defensible conversion
  between CES production and effort cost was specified. Reported resource cost
  equals effort and is presented separately.

Accordingly, the pilot finds condition-specific reward differences explained
by differences in policy information/planning, estimate updating, and
individual capability development. It does **not** establish a universal
organizational advantage or cleanly separate organizational learning from
exploration. The organizational result is not interpretable as a controlled
adaptation advantage. No result supports the assumption that coordination
always improves performance.

## Reproduction and provenance

From the repository root:

```sh
PYTHONPATH=src:. python experiments/synthetic/hls_lab_dynamic/characterize_laboratory.py
PYTHONPATH=src:. pytest -q tests/test_hls_lab_dynamic.py tests/test_hls_lab_dynamic_characterization.py
```

The runner refuses to overwrite an existing output directory. The checked-in
pilot manifest records the base Git HEAD, Python/platform, seed set, settings,
source hashes, and SHA-256 hashes for all three CSV artifacts. It records 256
runs and 5,632 decisions. The result directory contains the full per-run
summary, decision traces, paired contrasts, and machine-readable manifest.
