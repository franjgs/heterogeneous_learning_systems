# Sprint 0 — PACS competence-dynamics gate

**Status:** COMPLETE — N=50 ONLY.
**Purpose:** decide whether the existing PACS vehicle can support a direct RQ0 experiment after a minimal structural restriction of development. This is not B6, not a continual-learning contribution, and not an RQ0 test.

## Scientific question

Can restricting which parameters of the existing Fast model are allowed to learn from the *same* B2.4 opportunity-only treatment produce reproducible competence change with operational consequences, without introducing a new protection mechanism?

## Frozen inheritance

Reuse B2.3/B2.4 without reconstruction:
- PACS revision `394113073258ead631f617d2e13bb377c0715c4b`;
- CPU only;
- seeds `{0,1,2,3,4}`;
- domains `{photo, art_painting, cartoon, sketch}`;
- screen only `N=50`;
- exact B2.3 F0 and D states, split manifest, immutable opportunities and hard pseudo-labels;
- exact B2.4 O50 opportunity-only schedule: `T_50=12`, batch 16, 96 informative opportunity exposures and 96 duplicate slots;
- B2.4 transforms, augmentation seeds, per-step seeds, SGD hyperparameters and VALIDATION evaluation;
- B2.4 O50 states are the full-model reference;
- TEST is not read.

The intervention changes **only trainable scope**.

## Methods

### H — head only
Train only MobileNetV2 parameters whose names start with `classifier.`.

### LB — last block + head
Train only parameters whose names start with `features.18.` or `classifier.`.

The runner must record the exact trainable parameter names and fail if either selector is empty or if an unexpected architecture makes these selectors invalid.

All frozen parameters remain in the model and the model remains in `train()` exactly as in B2.4. Therefore BatchNorm running-state behavior is inherited from B2.4; this screen isolates gradient-updated parameter scope, not every mutable buffer. This limitation must be retained in interpretation.

## Screen size

`5 seeds × 4 domains × 1 N × 2 scopes = 40 fits`.

No N=25 or N=100 fit is permitted by this screen protocol.

## Measurements

For every state:
- four-domain VALIDATION competence vector;
- componentwise `DeltaS = S_method - S_F0`;
- local and summed cross-domain change;
- B2.4 operational value for each `c in {0,.02,.05,.10,.15}`;
- `DeltaV` relative to F0;
- routing vector and whether it differs from F0;
- paired differences against the stored full-model O50 state.

## Frozen screen decision

The five seeds remain the replication units. No significance test is used.

For each method and seed, average `DeltaS_local` over the four intervention domains. The **global local-learning screen** is POSITIVE iff this seed-level mean is strictly positive in at least 4/5 seeds and its five-seed mean is strictly positive.

For each cost `c`, average `DeltaV(c)` over the four intervention domains within each seed. The **global operational-value screen at c** is POSITIVE iff this seed-level mean is strictly positive in at least 4/5 seeds and its five-seed mean is strictly positive.

For each exact intervention domain, report the same 4/5-plus-positive-mean rule for local competence and, separately for every c, for `DeltaV`. These exact-domain results are diagnostics; they are not additional replication.

A method **ADVANCES** iff:
1. global local-learning screen is POSITIVE; and
2. global operational-value screen is POSITIVE for at least one of the five predeclared costs; and
3. at least one exact intervention domain has POSITIVE local competence change.

Otherwise it **STOPS**.

This is deliberately a permissive screen, not evidence for RQ0. It contains no arbitrary effect-size threshold and does not count N values or costs as independent replicates.

If neither H nor LB advances, stop PACS development repair and move to a different RQ0 environment. Do not add replay ratios, adapters, protection losses, gradient methods, or hyperparameter searches.

If one or both advance, inspect the complete transition vectors before freezing the full N={25,50,100} competence-dynamics gate. The full gate must be preregistered separately; Sprint 0 does not authorize it automatically.

## Outputs

- `run_manifest.json` (parent-manifest hashes, selected parameter names, and fit counts)
- `state_metrics.csv`
- `method_values.csv`
- `screen_classifications.csv`
- `SPRINT0_DIAGNOSTIC.md`

Every output must state `evaluation_split=validation` where applicable and `test_used=false`.

## Frozen outcome

The 40 planned fits completed with TEST closed. H and LB both **STOP**: neither
has a positive global operational-value screen at any declared cost. `photo`
is the only exact domain with reproducible positive local learning for either
method. This closes PACS development repair: it is a vehicle-screen result, not
an RQ0 result, and it does not authorize N=25/N=100 or any further PACS repair.
