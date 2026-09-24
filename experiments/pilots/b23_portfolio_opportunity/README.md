# PACS B2.3 portfolio opportunity experiment

Status: **IMPLEMENTED — NOT RUN**. The frozen scientific authority is
[`B23_PROTOCOL.md`](../../../docs/experimental_foundations/B23_PROTOCOL.md).
This implementation does not alter its models, grids, dose rule, event, or
classification.

The CPU-only runner creates one `F0` and one `D` for each seed, 20 immutable
100-example teacher streams with 60 nested `N={25,50,100}` opportunity views,
60 singleton fits, and 90 joint fits. Every derived state loads its seed's
exact `F0` hash. A joint fit saves `F_ij^CM` after `T_N` steps and continues
without restart to the primary `F_ij` endpoint at `2T_N`; the midpoint is not
an additional fit.

The restart cache is under `results/pilots/b23_portfolio_opportunity/.cache/`
and is ignored by Git. `run_manifest.json` binds every artifact to its file
SHA-256, parents, opportunity hashes, dose, and status. Relaunching the same
command reuses only complete artifacts whose hashes and provenance validate.
Corrupt or incomplete artifacts are recomputed. `--force` explicitly removes
all generated B2.3 artifacts and repeats the complete run.

Dry-run, with no training and no teacher query:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b23_portfolio_opportunity/run.py \
  --device cpu \
  --image-root /private/tmp/hls-pacs-cache/prepared/394113073258ead631f617d2e13bb377c0715c4b/images \
  --dry-run
```

Full execution and automatic restart after interruption use the same command:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b23_portfolio_opportunity/run.py \
  --device cpu \
  --image-root /private/tmp/hls-pacs-cache/prepared/394113073258ead631f617d2e13bb377c0715c4b/images
```

Analysis-only, after all artifacts exist:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b23_portfolio_opportunity/run.py \
  --device cpu \
  --analyze-only
```

Explicit complete repetition:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/pilots/b23_portfolio_opportunity/run.py \
  --device cpu \
  --image-root /private/tmp/hls-pacs-cache/prepared/394113073258ead631f617d2e13bb377c0715c4b/images \
  --force
```

The compatibility audit runs before scientific analysis. It requires the
complete 250 validation vectors and verifies F0/D parentage, immutable
opportunity hashes, nested prefixes, exact doses, midpoint continuity,
dataset/protocol provenance, CPU, and TEST closure. Any failure prevents the
`POSITIVE`/`NULL`/`INCONCLUSIVE` labels and reports an invalid/incomplete run.

The preregistered planning estimate is **13–15 CPU hours**, based on the
observed B2.1/B2.2 times. It is an estimate, not a guaranteed duration.
