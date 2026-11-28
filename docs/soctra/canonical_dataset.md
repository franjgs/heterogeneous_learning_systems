# SOCTRA canonical dataset

`data/soctra/processed/soctra_preprocessed.parquet` is the local HLS snapshot
derived from `dataset_20250919.csv`. The February reference is stored beside it
as `soctra_february_reference.parquet`. All paths under `data/soctra/` are
ignored by Git, including the generated `metadata.json`.

The CSV columns are retained as supplied. The `*_original` aliases clarify the
unmodified labels and ID; `escalada_procedimiento_corregida` records the value
after the original `motivo_sla_otros` 8x5 rule; and
`escalada_combinada_antes_estandarizacion` is the original loader's combined
label. `escalada_estandarizada` and `reportado_estandarizado` are the outputs of
`func_uniform(mode="dynamic", weight_positive=1)`. `*_ordinal_label` and
`*_ambigua` are its original auxiliary outputs. `preprocessed__*` columns hold
the cleaned feature view, before any feature encoding. The original alert ID,
timestamp string, project, handler (`tramitador`), severity, title, use case,
and other source attributes remain queryable in their original columns.

The original pipeline has two materially different row populations: source
label counts cover every CSV row, while labels after preprocessing and
uniformization cover records retained after title, project, and Mailbox
filters. `metadata.json` records counts and distributions at both scopes,
2x2 transition matrices on matching IDs, train/test distributions for each
escalation label stage, temporal bounds, group rates, and ambiguous patterns.
The `A_std` configs specify standard scaling after feature encoding; this
dataset deliberately stops before encoding, so it preserves original feature
values and applies only the source text/category cleaning and label
uniformization. The temporal windows use 12 training months followed
by 4 test months, anchored to the latest retained timestamp, matching the
SOCTRA configuration. Rows outside those windows are not in either partition.

For the February snapshot, the source pipeline gives 170,653 source rows,
122,493 after preprocessing, and 122,493 after uniformization. Its temporal
split has 48,961 train alerts / 230 positives and 14,449 test alerts / 19
positives. This reproduces the historical `19/14449` figure from the February
dataset and its configured split, rather than from the September canonical
snapshot.

Regenerate both local Parquet files and metadata with:

```sh
python tools/prepare_soctra_dataset.py \
  --february-csv /path/to/dataset_2025_febrero.csv \
  --september-csv /path/to/dataset_20250919.csv
```

`--original-library` is optional and only enables an external record-level
comparison. Without it, regeneration uses the vendored HLS implementation and
does not access a SoC_WP4 checkout; metadata records that external comparison
was not run for that invocation.

Install the pinned preparation dependencies with `pip install -e '.[soctra-data]'`.
No HLS
runtime import reaches into the SoC_WP4 checkout. The selected loading,
preprocessing, and uniformization functions are vendored in
`src/hls/soctra/original_pipeline.py` from the source commit identified in the
versioned configuration. Only trailing whitespace was normalized; row-level
outputs were compared with the original checkout.
