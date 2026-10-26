# Experiment and Evidence Index

This page helps locate experimental material; it is not a second results
ledger. The [scientific registry](../registry/hls_scientific_registry.jsonl)
indexes investigations and results, [HLS Current State](../HLS_CURRENT_STATE.md)
summarizes present status, and [History](../HISTORY.md) records chronology.
Protocols define designs; result reports and artifacts provide evidence.

## Formal and synthetic foundations

- [Theory index](../theory/README.md) — scoped formal results and exact
  constructions, including T0–T6 and G1/G2.
- [`experimental_foundations/`](../experimental_foundations/) — reference
  scenarios, RQ0 protocols, and finite ground-truth records.
- [`experiments/foundations/`](../../experiments/foundations/) — executable
  foundation reproductions and outputs.
- [`experiments/synthetic/`](../../experiments/synthetic/) — synthetic
  runners organized by study.

## Campaigns and research lines

Use the registry to find all studies. Primary documentation is organized by
line, including:

- [Campaign 1](CAMPAIGN_1_PROTOCOL.md) and [results](CAMPAIGN_1_RESULTS.md).
- [Campaign 2 results](CAMPAIGN_2_RESULTS.md).
- [Campaign 3 META-VOC confirmatory protocol](CAMPAIGN_3_META_VOC_CONFIRMATORY_PROTOCOL.md)
  and [results](CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md).
- [HLS-CE-01](../research/HLS_CE_01_DYNAMIC_DELIBERATION_2026-10-24.md),
  [CE-02](../research/HLS_CE_02_AI_AGING_PREFLIGHT.md), and the CE-03/04/06/07
  records under [`docs/research/`](../research/).
- [HLS Laboratory v1](HLS_LAB_V1.md) and its bounded validation and mechanism
  reports.

The registry and Current State carry the navigation/status role; do not infer
that a study is active or confirmatory from its directory name.

## Reproduction materials

- [`experiments/pilots/`](../../experiments/pilots/) — pilot runners and
  supporting artifacts.
- [`results/`](../../results/) — tracked results, tables, figures, and
  manifests. Full raw artifacts may be local-only or ignored; their
  availability is stated in the corresponding report/manifest.
- [`tests/`](../../tests/) — functional and contract checks; passing tests
  validate code behavior, not a scientific hypothesis.

Consult [Current State](../HLS_CURRENT_STATE.md) before reading an older
protocol or result. Follow each report's scope and limitations; do not combine
results across models or campaigns unless the source establishes their
comparability.
