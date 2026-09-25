# B2.4 audit map

This directory contains the small textual artifacts needed to reconstruct and
audit the completed PACS B2.4 conclusions. TEST remained closed.

| Artifact | Audit role |
| --- | --- |
| `summary.md` | Generated integrity counts and frozen classifications. Its `360/240` label includes 120 repeated F0/D lookup views; the scientific method-state count is 240. |
| `run_manifest.json` | CPU/TEST status, B2.3 parent provenance, hashes, schedules, validation metadata, and completion state. |
| `replay_buffers.jsonl` | Deterministic replay IDs and labels, F0 parents, RNG provenance, and buffer hashes. |
| `development_states.jsonl` | STD/O50/REP/REP2 genealogy, opportunity/replay hashes, doses, checkpoints hashes, and complete competence vectors. |
| `state_metrics.csv` | The 240 scientific method states and their validation competence changes. |
| `method_values.csv` | The 1,200 `method × c` operational value rows and per-domain value contributions. |
| `primary_contrasts.csv` | The 300 REP-minus-O50 value contrasts plus preregistered controls. |
| `competence_contrasts.csv` | The 60 paired interference/local-learning contrasts. |
| `seed_summaries.csv` | Five seed-level global summaries used as replication units. |
| `classifications.csv` | Frozen global POSITIVE/NULL/INCONCLUSIVE classifications. |
| `exact_regime_classifications.csv` | Descriptive classifications for exact `domain × N` regimes and each declared c. |
| `timing_summary.json` | Compact operational timing summary derived from the logger ledger; timing is excluded from scientific hashes. |

The principal reconstruction checks are:

- 60 compatible `seed × domain × N` families;
- 120/120 new fits and 180/180 new VALIDATION evaluations;
- 60 states each for STD, O50, REP, and REP2;
- 1,200 value rows and 300 primary contrast rows;
- O50 and REP share the required opportunity projection in all 60 families;
- all value-contribution and paired-contrast identities hold to floating-point
  precision;
- no NaN;
- compatibility PASS and TEST CLOSED.

The files contain no model weights or PACS images. Checkpoints and dataset
caches are deliberately excluded from version control.
