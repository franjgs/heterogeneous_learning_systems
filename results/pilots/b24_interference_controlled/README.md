# B2.4 result artifacts

Status: **COMPLETE**. The CPU run completed 120/120 new fits, 180/180 new
VALIDATION evaluations, and 1,200/1,200 value rows. Compatibility passed and
TEST remained closed. Accumulated runtime was `04:57:04`.

The frozen protocol is
[`B24_PROTOCOL.md`](../../../docs/experimental_foundations/B24_PROTOCOL.md),
commit `491659c`. The scientific result is consolidated in
[`HLS_checkpoint_after_B24.md`](../../../docs/checkpoints/HLS_checkpoint_after_B24.md).
[`AUDIT_README.md`](AUDIT_README.md) maps each claim to the compact textual
artifacts in this directory.

No model checkpoint, PACS image, or dataset cache belongs in Git. Heavy
restart artifacts remain under `.cache/` and are excluded. The compact
`timing_summary.json` preserves the execution totals outside the cache.

The scientific CSVs contain 240 method states: 60 STD, 60 O50, 60 REP, and 60
REP2. The `360/240` line in the generated `summary.md` counted 120 repeated
F0/D lookup views in its numerator; it is a reporting-label issue, not a
scientific state-count discrepancy.
