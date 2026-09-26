# B4 Protected Portfolio Development

Status: **FULL RUN COMPLETE** (`60/60` fits; `COMPLETE.json` status:
`complete`).

- Device: CPU only.
- TEST status: `PREVIOUSLY_OPENED_NOT_USED_IN_B4`.
- Baseline: frozen B2.4 REP, reused without retraining.
- PREP: one candidate block per B2.4 REP optimizer step; zero-tolerance
  protection against the fixed F0 reference.
- Protection set: 28 F0-training examples per domain
  (4 per class), 112 per seed, chosen by
  deterministic SHA-256 ordering.
- Rejected blocks restore model and optimizer exactly, advance the scheduled
  RNG stream, and are not retried.

The completed run used the explicit `--run-full` mode. Restart reuses only
hash-valid completed PREP fits.
