# B2.2 PACS operational opportunity value

Status: **COMPLETED — INCONCLUSIVE**. The scientific authority is
[B22_PROTOCOL.md](../../../docs/experimental_foundations/B22_PROTOCOL.md).
This runner does not change its test, grid, models, seeds, splits, or outcome
criteria.

`run.py` reconstructs the five CPU-only B2.1 `F0`/`D` pairs, then performs
exactly 60 direct-from-`F0` opportunity updates: five seeds by four PACS
domains by `N={25,50,100}`. The Fast trajectory has no teacher-query interface.
The Deep trajectory processes exactly the selected `N` TRANSFER examples and
uses exactly their `N` hard pseudo-labels. The runner evaluates only VALIDATION.
TEST has no exposed split in the B2.2 data path.

After the 60 learned states exist, the runner expands them analytically over
the frozen five costs and four future-use weights to produce 1,200 rows. It
then applies the preregistered definitions and classification rule. No model is
retrained for a different `c` or `B`.

Restart artifacts and base checkpoints are written atomically under
`results/pilots/b22_opportunity_value/.cache/`, which is excluded by the
repository `.gitignore`. Each artifact binds the seed, domain, `N`, selected
IDs, parent `F0`, protocol, configuration, manifest, and implementation hashes.
Rerunning the same command skips compatible completed updates. An incompatible
artifact stops with an explicit error. `--force` removes the B2.2 restart cache
and generated B2.2 outputs before repeating all work.

Dry-run, without training:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b22_opportunity_value/run.py \
  --device cpu \
  --image-root /private/tmp/hls-pacs-cache/prepared/394113073258ead631f617d2e13bb377c0715c4b/images \
  --dry-run
```

Full execution, with automatic restart after interruption:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b22_opportunity_value/run.py \
  --device cpu \
  --image-root /private/tmp/hls-pacs-cache/prepared/394113073258ead631f617d2e13bb377c0715c4b/images
```

Analyze the completed artifacts without loading or training models:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b22_opportunity_value/run.py \
  --device cpu \
  --analyze-only
```

Explicit full repetition:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b22_opportunity_value/run.py \
  --device cpu \
  --image-root /private/tmp/hls-pacs-cache/prepared/394113073258ead631f617d2e13bb377c0715c4b/images \
  --force
```

The completed CPU execution took 08:10:14. It produced four favorable
analytical observations, none reproduced in at least two seeds, with TEST
closed. See the [diagnostic](../../../results/pilots/b22_opportunity_value/b22_diagnostic.md)
for the independent reconstruction and the distinction between analytical rows
and unique learned states.
