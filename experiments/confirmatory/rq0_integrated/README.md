# RQ0 integrated confirmation

This runner implements the frozen pre-TEST protocol at commit `8b16394`.
Its default mode is PRETEST and explicitly blocks every TEST access. It audits
the common-provenance B2.3/B2.4 F0, D, opportunity, replay, and REP artifacts;
reconstructs frozen VALIDATION values; and checks SEP, HLS, and SEP-Omega.

```bash
python experiments/confirmatory/rq0_integrated/run.py --tests-passed
```

The separate confirmatory command is intentionally never run during pipeline
construction. After the code and generated PRETEST manifests are reviewed and
frozen, its explicit form is:

```bash
KMP_DUPLICATE_LIB_OK=TRUE /Users/fran/Programs/miniconda3/bin/python \
  experiments/confirmatory/rq0_integrated/run.py \
  --confirmatory-test --device cpu \
  --image-root /private/tmp/hls-pacs-cache/prepared/394113073258ead631f617d2e13bb377c0715c4b/images
```

That future mode must evaluate exactly 5 F0, 5 D, and 60 REP checkpoints. It
must never train or mutate them. A completed confirmation refuses overwrite;
`--audit-existing` is reserved for a read-only audit of frozen outputs.
