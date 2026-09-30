# B0 — Office-Home heterogeneous frozen-representation vehicle gate

Status: **FROZEN VEHICLE-SCREEN DESIGN**

## Purpose

B0 asks only whether a second experimental vehicle is viable for a direct future
test of RQ0. It is not an RQ0 test and does not implement HLS, SEP or SEP-Omega.

The vehicle advances only if it provides:

1. non-degenerate heterogeneity between two learners;
2. reproducible competence development under explicit development interventions;
3. sufficiently predictable competence-transition vectors.

Failure stops this vehicle. It does not count as evidence against RQ0.

## Dataset

Office-Home, with the four natural domains:

- Art
- Clipart
- Product
- Real World

The runner expects an already available Office-Home image tree and never
downloads data implicitly.

## Learners

Two ImageNet-pretrained frozen representations:

- `resnet18`
- `mobilenet_v2`

Only a linear classification head is trainable. The backbone is used in eval
mode and embeddings are precomputed once per run.

No backbone fine-tuning, adapters, replay, protection mechanisms or
continual-learning repair is allowed in B0.

## Competence state

For learner i and domain k,

    C_{i,k} = balanced accuracy on the frozen VALIDATION split of domain k.

The collective competence state is the 2 x 4 matrix S = {C_{i,k}}.

TEST is not defined or read by this experiment.

## Frozen splits

For every seed and every domain/class, images are deterministically shuffled and
partitioned into:

- BASE: exactly `base_per_class=3` examples per class;
- DEVELOPMENT: the next available examples;
- VALIDATION: `val_fraction=0.25` of the remaining examples, with at least one
  validation example whenever possible.

The exact membership is written to `split_manifest.csv`.

BASE trains the initial linear head from scratch. DEVELOPMENT supplies the
development opportunities. VALIDATION measures all competence components.

## Development intervention

For each learner i, seed s and target domain k:

1. start from the exact base head for (i,s);
2. take a stratified DEVELOPMENT opportunity of N=50 from domain k;
3. train only the linear head on those 50 embeddings for a fixed number of
   epochs;
4. evaluate all four VALIDATION domains.

This gives 2 learners x 5 seeds x 4 target domains = 40 interventions.

The same split and opportunity IDs are used by both representations for a given
seed/domain.

## Optimisation

- linear head only;
- SGD;
- learning rate `0.05` and weight decay `1e-4`;
- 25 BASE epochs and 10 DEVELOPMENT epochs;
- deterministic PyTorch seeds where supported;
- no hyperparameter search in B0.

The purpose is transition screening, not accuracy optimisation.

## Gate outputs

### G1 — Heterogeneity

Report, by seed and domain, the base competence difference between ResNet-18
and MobileNetV2.

B0 does not impose a post-hoc numerical effect-size threshold. The diagnostic
must report:

- per-domain mean competence for each learner;
- per-domain paired differences;
- whether one learner dominates the other on all four domains in every seed;
- whether the base competence vectors are exactly/numerically identical.

The runner emits no numerical indistinguishability threshold. Raw paired
differences by seed/domain and exact all-cell equality/dominance indicators are
retained for the later scientific decision.

### G2 — Development effectiveness

For each learner x target-domain intervention, compute the local change

    Delta C_local = C_after(target) - C_base(target).

A learner-domain cell is locally POSITIVE iff:

- Delta C_local > 0 in at least 4/5 seeds; and
- the five-seed mean Delta C_local > 0.

The runner reports every cell and the total count but does not invent an
additional post-hoc threshold.

### G3 — Transition predictability

For every learner x target domain x measured domain, report:

- mean Delta C;
- standard deviation;
- number of positive / negative / zero seeds;
- majority sign;
- whether at least 4/5 seeds share the same sign (including a stable zero).

A component has 4/5 sign agreement iff at least 4/5 seeds share the same sign.
The complete transition vector is retained; cross-domain transfer/interference
is allowed and is not treated as failure by itself.

The scientific decision ADVANCE/STOP must be based on the preregistered
structural questions above, not on tuning after seeing the results.

## Kill rule

STOP the B vehicle if any structural requirement fails:

- no useful heterogeneous portfolio;
- development interventions do not produce reproducible local competence
  changes;
- transition vectors are too seed-dependent to estimate a useful
  P(S' | S,d).

If STOP, do not repair B0 by adding representations, changing N, tuning the
optimizer, adding replay/adapters/protection, or fine-tuning the backbone.
Return to vehicle selection rather than repairing B0.

## Integrity

- VALIDATION only.
- No TEST surface exists in the runner.
- No HLS/SEP comparison is performed.
- No automatic dataset download.
- No model checkpoints are required for reproducibility; embeddings/cache are
  disposable and ignored.
