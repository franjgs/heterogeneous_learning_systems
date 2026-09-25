# PACS B2.4 interference-controlled development

Status: **IMPLEMENTED — NOT RUN**. The frozen scientific authority is
[`B24_PROTOCOL.md`](../../../docs/experimental_foundations/B24_PROTOCOL.md),
commit `491659c`.

B2.4 reuses the exact compatible B2.3 F0, D, split, opportunity, and STD
artifacts. For each of 60 `seed × domain × N` families it trains one O50
control and one continuous REP-to-REP2 trajectory. This requires 120 new CPU
fits and 180 new VALIDATION evaluations. TEST remains closed.

Runtime artifacts and checkpoints are stored under
`results/pilots/b24_interference_controlled/.cache/` and are ignored by Git.
`run_manifest.json` records parent hashes, immutable replay buffers, schedules,
doses, RNG provenance, checkpoints, and validation provenance. A restart
reuses only complete hash-valid artifacts. A valid REP midpoint resumes its
same trajectory toward REP2. `--force` explicitly discards B2.4 artifacts
only; it never modifies B2.3.

Dry-run, without training or teacher inference:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b24_interference_controlled/run.py \
  --device cpu \
  --image-root /private/tmp/hls-pacs-cache/prepared/394113073258ead631f617d2e13bb377c0715c4b/images \
  --dry-run
```

Full execution and automatic restart use the same command:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b24_interference_controlled/run.py \
  --device cpu \
  --image-root /private/tmp/hls-pacs-cache/prepared/394113073258ead631f617d2e13bb377c0715c4b/images
```

Analysis-only never loads a training pipeline or performs model updates:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b24_interference_controlled/run.py \
  --device cpu \
  --analyze-only
```

The common timing logger persists operational metadata at
`.cache/experiment_timing.json`, separately from scientific hashes. It reports
O50 and mixed-trajectory timing, session elapsed time, accumulated restart
time, and ETA from observed work.
