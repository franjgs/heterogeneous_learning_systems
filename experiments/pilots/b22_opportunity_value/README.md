# B2.2 PACS operational opportunity value

Status: **IMPLEMENTED — NOT EXECUTED**. The scientific authority is
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

Explicit full repetition:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b22_opportunity_value/run.py \
  --device cpu \
  --image-root /private/tmp/hls-pacs-cache/prepared/394113073258ead631f617d2e13bb377c0715c4b/images \
  --force
```

Historical B2.0 measurements for the five Deep and five 25%-BASE Fast fits
total 6.07 CPU hours. The B2.1 structural estimate was about 7.1 hours for 160
fits. B2.2 retains those ten expensive base fits and performs 60 singleton
updates plus validation, so its estimated total is approximately 6.5–7 CPU
hours. This is an estimate, not a measured B2.2 duration or guarantee; no B2.2
smoke training was used to derive it.
