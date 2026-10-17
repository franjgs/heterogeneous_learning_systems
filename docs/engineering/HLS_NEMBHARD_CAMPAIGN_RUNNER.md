# HLS Nembhard E1 campaign runner and analysis

**Status:** implementation and small-test validation complete; HLS-E1 execution
was started and interrupted. The campaign is **NOT COMPLETED** and partial
outputs are not scientific conclusions. HLS Laboratory remains **PARTIAL**.

This module operationalizes the reviewed protocol in
[`docs/experiments/HLS_NEMBHARD_ADAPTIVE_ALLOCATION_PROTOCOL.md`](../experiments/HLS_NEMBHARD_ADAPTIVE_ALLOCATION_PROTOCOL.md).
It is an orchestrator around the existing Nembhard route, not a new simulator,
policy, learning law, or demand process.

## Components and interfaces

Implementation: `src/hls/nembhard_campaign.py`.

- `build_design_registry()` and `list_configurations()` construct immutable
  `EpisodeConfig` records and alias metadata without running an episode.
- `validate_configuration()` verifies one record against the frozen protocol;
  `validate_design()` checks the full factorial, resource constraints, action
  feasibility, paired demand identities, exact counts, and the diagnostic
  de-duplication without executing the scientific runner.
- `build_demand_sequence(order, seed)` creates an explicit tuple of
  `ProblemSpecNK` objects. `ordered_demand_hash()` uses the protocol's ordered
  canonical JSON encoding. `demand_multiset_hash()` sorts those canonical
  records before hashing, preserving multiplicity but discarding order.
- `execute_episode(config, output_root, persist=True)` executes one selected
  120-period episode through `run_nk_production_sequence` with
  `mechanism_id="nembhard_direct"`. The result is wrapped using
  `adapt_nembhard_run`; native fields are retained as well.
- `load_completed_results()`, `paired_differences()`,
  `paired_period_differences()`, `paired_order_differences()`,
  `protocol_interaction_contrasts()`, `grouped_descriptives()`,
  `temporal_summary()`, `allocation_share_summary()`, and `analyze_campaign()`
  provide post-execution analysis. Bootstrap resamples replicate bundles, not
  periods.

The four arms are exactly FIXED, ORACLE, ADAPTIVE with zero observation noise,
and ADAPTIVE with 0.05 output-unit noise. The latter two use the existing
`nembhard_adaptive` implementation, including initial estimate 0.6, epsilon
0.05, Welford mean/dispersion, and the prescribed independent seed streams.
FIXED uses only the current problem ID and the predeclared role map in the
protocol. ORACLE and ADAPTIVE remain the existing routers; their information
boundaries, tie rules, and one-period objective are unchanged.

## Design and demand identities

The generator returns 960 primary episodes, 40 epsilon-zero sensitivity
episodes, and 16 additional permutation-diagnostic episodes. The nominal 18
diagnostic cells include FIXED and ORACLE identity-permutation runs already in
the primary matrix; `diagnostic_aliases` points to these two existing IDs.
Thus the unique registry contains exactly **1,016** episodes / **121,920**
periods. IDs are derived from a digest of the semantic experimental identity;
duplicate checks do not rely on labels such as “primary” or “diagnostic.”

Within each seed bundle, interleaved and clustered paths both contain exactly
40 problems of each of `skill1`, `skill2`, and `joint`; their multiset hashes
match while their ordered hashes differ. Interleaved order shuffles 40 fresh
triples with the declared seed. Clustered order chooses by
`randrange(len(valid_orders))` from lexicographically sorted unique valid
six-block orders. Both paths are frozen and passed to the runner as explicit
problem sequences.

Seed bundle `r` uses `20261017 + 10000*r + 1` for interleaved demand, `+2` for
clustered demand, `+3` for observations, and `+4` for exploration. Only streams
actually used by a policy are listed as run-level random seeds; all assigned
seed values remain in the full episode configuration. Equal seed values do
not imply equal trajectories. The protocol's positive-noise coordinate/time
draw alignment and sigma-zero caveat are preserved.

The FIXED role map and all profiles, `p=r` values, requirements, resource
limits, duration, and horizon are literal protocol constants. The HLS
competence matrix is a fixed zero placeholder required by the shared
organization structure; Nembhard physics does not read it. Productivity,
experience, effort, exposure, output, and normalized deficit remain distinct.

## Results and metric definitions

Results are written under
`results/experiments/hls_nembhard_adaptive_allocation/<episode_id>/` as:

- `run.json`: `hls-experiment-run/1.0` envelope, including trace events,
  mechanism-specific records, configuration, decision information, units,
  seeds and finite scalar metrics;
- `campaign_metrics.json`: demand hashes/sequence, unit-declared campaign
  metrics, by-problem summaries, period records, per-cell true productivity
  and experience diagnostics, allocations, and adaptive prediction errors;
- `native_nembhard_result.json`: native Nembhard result representation.

An existing episode directory is an error; results are never silently
overwritten. These files are generated only by an explicit `run` command.

Primary outcomes are task-relevant cumulative output (output units), success
proportion (fraction), and cumulative normalized deficit (dimensionless).
Secondary measures keep effort (per-period effort amount), effective exposure
(work-exposure units), productivity (output/exposure), allocation totals and
shares, actual experience, per-period outcomes, exploration frequency, and
prediction error separate. No aggregate score or cross-mechanism conversion is
introduced. When a test/subset contains no instance of a problem type, its
problem-specific values are JSON `null` with a zero count; campaign validation
requires the full 40/40/40 sequences.

Analysis requires all 1,016 unique episode results, matched cells for each
contrast, and fails on missing or duplicate results instead of silently
dropping them. It computes the reviewed primary paired contrasts,
first-period summaries, H1–H3 difference-in-differences, H4 noise
sensitivity, the epsilon-zero control, clustered-minus-interleaved matched
contrasts, grouped descriptives, allocation shares and period-wise timecourses.
Each uncertainty summary is stratified by the remaining factorial scenario
levels: a stratum contains its 20 paired seed bundles, rather than pooling
different profiles, learning scales, or demand orders as if they were
replicates. Bootstrap intervals use 10,000 resamples by default and resample
seed bundles. They describe
uncertainty under the selected schedule/seed construction, not uncertainty
over a population of organizations.

## CLI

No command runs on import. With the project `src` path available:

```text
python -m hls.nembhard_campaign list --limit 10
python -m hls.nembhard_campaign list --all
python -m hls.nembhard_campaign validate
python -m hls.nembhard_campaign run --episode-id <episode-id>
python -m hls.nembhard_campaign run --episode-ids <id-1> <id-2>
python -m hls.nembhard_campaign analyze --input-root results/experiments/hls_nembhard_adaptive_allocation
```

The full campaign additionally requires the explicit token:

```text
python -m hls.nembhard_campaign run --all --confirm-campaign HLS-EXECUTE-1016
```

`validate` only constructs and checks the registry and does not simulate any
configuration. A caller may provide
`--software-revision` when running to record a revision; the tool does not
guess one. Analysis output written with `--output` also refuses overwrite.

### Inspecting and resuming an interrupted campaign

`status --output-root <path>` reads and validates every present episode
directory, reports complete and pending counts, and does not execute episodes.
It rejects unknown episode directories, directories missing any of the three
expected files, malformed/non-finite JSON, and trajectory/provenance mismatches.
Completion requires valid `run.json`, `campaign_metrics.json`, and
`native_nembhard_result.json`, all 120 problem/period records, matching demand
hashes and expected common trace events. Directory existence alone is not
completion.

After an interrupted run, the explicit resume command is:

```text
python -m hls.nembhard_campaign resume --confirm-resume HLS-RESUME-E1 \
  --output-root results/experiments/hls_nembhard_adaptive_allocation
```

Resume first validates all existing runs, requires at least one valid completed
episode, then dispatches only missing IDs in registry order. Existing outputs
are never replaced. Incomplete or inconsistent episode directories stop the
resume and require manual investigation; the command never deletes or repairs
them. `run --all` retains its original behavior and confirmation token.
Neither `status` nor this documentation update started a resume.

## Incident record — 2026-10-17

HLS-E1 execution was **STARTED AND INTERRUPTED; CAMPAIGN NOT COMPLETED**. The
reported exception occurred in `ProductivityEstimateCellNK.update()` while
constructing the Welford state. A minimal reproducible floating-point case is:

```text
initial estimate / mean_old = 0.6; observation_count = 0
work = 0.5; observed work output = 0.8336012378255072
x = observed_output / work = 1.6672024756510144
delta = 1.0672024756510146
mean_new = 1.6672024756510146
delta_after = -2.220446049250313e-16
m2_old = 0.0; delta * delta_after = -2.3696655208094487e-16
```

Mathematically, a first observation with count zero must set the sample mean to
`x` and `m2` to zero. The generic Welford expression `mean_old + delta / 1`
can round one ULP beyond `x`; this is a small cancellation artifact, not a
materially negative variance. The `0.6` value is the decision prior, not an
observed sample. The first-update branch now installs `(x, 1, 0)` directly.
For subsequent updates, a negative `m2` is normalized only when its magnitude
fits an eight-ULP bound based on the input/product scale; non-finite and
materially negative values remain errors. No estimator, observation, seed,
exploration, production, or experience semantics were changed.

The persisted campaign outputs do not contain the failed episode's in-memory
observation, so the exact operands from the interruption cannot be recovered.
The reproduced tuple above establishes the source defect and a valid input
that triggered the same exception. The 16 completed adaptive traces were
replayed through the pre-fix arithmetic offline; none had a negative update.
Observation noise is not mathematically required for the defect, though the
likely interrupted registry item was the noisy ADAPTIVE run
`nembhard-e1-07fa9df8f35b0d9e064a` (the 30th item in default registry order).
The run order and absence of its output directory make this the probable, not
trace-confirmed, failing ID.

Read-only result audit found **29 complete episodes**, **0 incomplete episode
directories**, and **0 corrupt JSON files**. All 29 pass the result loader's
three-file, JSON, demand-hash, mechanism/router, and 120-period trace checks.
There are **987 pending episodes**. The first pending ID is
`nembhard-e1-07fa9df8f35b0d9e064a`. No partial result was modified or included
in version control. These partial trajectories are not campaign findings.

## Validation and limitations

`tests/test_hls_nembhard_campaign.py` checks count reconciliation, exact
seed formula, deterministic demand construction, same multiset/different
order hashes, all profiles, resource-feasible FIXED actions, short synthetic
end-to-end calls to the existing runner, adaptive replay and information
separation, common-envelope adaptation, no-overwrite persistence, paired
contrasts, scenario-stratified summaries, and H1–H3 interaction calculations.
Most synthetic route fixtures use at most three periods. One isolated 120-period
FIXED fixture is created under the test temporary directory to validate full
result integrity and resume skipping; the subsequent 1,015-item resume dispatch
is mocked. No campaign output is created or changed by that test. Existing
Nembhard and common-contract tests remain the mechanism and serialization
authorities.

Incident regression and safe-resume validation passed 74 focused tests across
the adaptive estimator, Nembhard execution, campaign runner, and common
experiment contract. The final repository suite passed 1,512 tests and retained
the same five known historical inventory/provenance failures. No campaign run
was launched for these checks.

This is an implementation of the existing reviewed protocol, not scientific
evidence. It does not make ORACLE a long-horizon optimum, isolate the causal
effect of adaptation from information/exploration, establish FIXED as the
best possible static baseline, or add MIS-v2/teaching. The campaign is
interrupted and incomplete; resume remains an explicit operation requiring
review/authorization.
