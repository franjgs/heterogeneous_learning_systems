# B2.0 — PACS calibration

Status: **DATASET AUDIT OBSERVED; MODEL CALIBRATION COMPUTE-BLOCKED**. No model
quality or PACS suitability conclusion has been obtained. This is calibration
only: it contains no transfer intervention, factorial, `Gamma`, routing, cost,
or `H` analysis.

## Question and competence definition

B2.0 asks only whether PACS can provide a practical, stable experimental bank
for a later study of competence development. The four competence coordinates
are fixed by dataset domain:

```text
S(M) = (balanced_accuracy_photo, balanced_accuracy_art_painting,
        balanced_accuracy_cartoon, balanced_accuracy_sketch)
```

They do not depend on a model, seed, clustering, or downstream result.

## Dataset source and audit

The reproducible source is the public Hugging Face dataset repository
[`flwrlabs/pacs`](https://huggingface.co/datasets/flwrlabs/pacs), snapshot
revision `394113073258ead631f617d2e13bb377c0715c4b`, file
`data/train-00000-of-00001.parquet`. The pinned direct URL is recorded in
`results/pilots/b2_pacs_calibration/dataset_audit.json`. The artifact is
191,395,900 bytes with SHA-256
`4fc041ee92eec6043fe6e2859e8bdd138e5f958bc621afd153879812cbe65ff5`.
The source dataset card points to the original PACS site and reports 9,991
images; the pinned Parquet schema declares all seven labels, including
`house` (the prose list on the card omits that label).

| Domain | dog | elephant | giraffe | guitar | horse | house | person | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Photo | 189 | 202 | 182 | 186 | 199 | 280 | 432 | 1,670 |
| Art painting | 379 | 255 | 285 | 184 | 201 | 295 | 449 | 2,048 |
| Cartoon | 389 | 457 | 346 | 135 | 324 | 288 | 405 | 2,344 |
| Sketch | 772 | 740 | 753 | 608 | 816 | 80 | 160 | 3,929 |
| Total | 1,729 | 1,654 | 1,566 | 1,113 | 1,540 | 943 | 1,446 | 9,991 |

All 9,991 rows were decoded and checked with Pillow: no missing image bytes,
corrupt/unreadable images, or exact byte-hash duplicates were detected. The
row-level manifest records stable row ID, domain, class, source path, image
SHA-256, dimensions, format, and a cache-relative path. The image dataset is
stored outside the repository; only manifests and audit results are versioned.

## Planned splits and models

Each of five fixed seeds stratifies the `domain × class` cells into disjoint
BASE (4,995), TRANSFER (1,998), VALIDATION (1,499), and TEST (1,499) rows.
`split_manifest.csv` contains every per-seed membership. F0 trains only on a
balanced within-cell subset of BASE at fractions `{10%, 25%, 50%, 100%}`. The
Deep teacher trains once per seed on BASE + TRANSFER (6,993 rows), never on
VALIDATION or TEST. This deliberately leaves TRANSFER unseen by F0.

Fast is torchvision MobileNetV2 with ImageNet `MobileNet_V2_Weights.DEFAULT`;
Deep is torchvision ResNet-50 with `ResNet50_Weights.DEFAULT`. Only their
classifier heads change to seven outputs. The configured fixed protocol uses
SGD (Fast learning rate `1e-3`, Deep `1e-4`, momentum `0.9`), three epochs,
batch size 16, RandomResizedCrop(224, scale 0.8–1.0) and horizontal flip for
training, and Resize(256)+CenterCrop(224) for evaluation with ImageNet
normalization. There is no architecture search. The script uses identical
evaluation preprocessing for all four domains.

The regime-selection rule is fixed before TEST is opened. Among the four
fractions, choose the smallest whose validation results across the five seeds
meet all conditions: bootstrap lower interval for F0 exceeds chance `1/7` in
each domain; bootstrap upper interval is below the perfect-score boundary `1`
in at least two domains; and the paired Deep-minus-F0 lower interval is above
zero in at least two domains. This is a neutral calibration rule, not a
claim of statistical significance. TEST is evaluated only after that
validation-only selection; if no fraction qualifies, TEST remains unused.

## What was actually executed

The pinned dataset was downloaded to an external cache and audited. Split
membership was generated for all five seeds and checked for disjointness and
full coverage. No model fit was started, so no validation/test metrics, domain
gaps, accuracy curves, or regime selection exist yet.

The runtime is macOS arm64 with 12 logical CPUs. PyTorch 2.4.1 reports no CUDA
and no available MPS device (`mps_built=true`, `mps_available=false`), so the
effective device is CPU. A minimal throughput profile ran four synthetic
224×224 forward/backward/SGD batches of size 8 per architecture, with random
initialization (not PACS data and not pretrained weights): MobileNetV2
23.95 images/s and ResNet-50 15.35 images/s. The synthetic profile itself
took about 3.9 seconds. Based on the actual split sizes,
the configured 25 fits require about 46,185 Fast and 34,965 Deep training
images per epoch across seeds. The estimated training-only lower bound is
70.1 minutes per epoch, or 3.51 hours for the configured three epochs,
excluding decoding/augmentation, validation/test inference, weight downloads,
and checkpoint I/O. Because the complete five-seed calibration is therefore
not reasonable on the available CPU-only backend, execution stopped after
the prespecified profile; architectures and protocol were not changed to
obtain a cheaper or more favorable result.

The available experimental setup is **NOT VIABLE on this CPU-only machine**:
even this calibration has a multi-hour lower bound before I/O and evaluation,
which is not a practical base for the many later fits. This is a compute
feasibility classification for the current setup, not evidence that PACS
lacks empirical headroom. PACS model-performance viability remains unassessed.
The status is `COMPUTE_BLOCKED_BEFORE_MODEL_CALIBRATION`.

## Reproduction entry points and outputs

```text
python experiments/pilots/b2_pacs_calibration/prepare_dataset.py \
  --cache-dir /path/outside/repository/pacs-cache
python experiments/pilots/b2_pacs_calibration/profile_cpu.py
python experiments/pilots/b2_pacs_calibration/run.py \
  --image-root /path/outside/repository/pacs-cache/394113073258ead631f617d2e13bb377c0715c4b/images
```

The full-run script refuses a CPU run by default; `--allow-cpu` is an explicit
override. Expected outputs after a completed calibration are `metrics.csv`,
`domain_metrics.csv`, `gaps.csv`, `confusion_matrices.csv`,
`validation_metrics.csv`, `test_metrics.csv`, `split_manifest.csv`,
`fit_times.csv`, `summary.json`, and `run_metadata.json`. Presently available
outputs are dataset/audit/split manifests and the CPU profile under
`results/pilots/b2_pacs_calibration/`. No checkpoint or dataset image is
committed.
