# Experiments

This directory contains small, reproducible research experiments.  Existing
`m0/`, `m01/`, and `microverification/` directories are historical analytical
laboratories and retain their paths and provenance.

## Foundation experiment convention

Future reproductions of the two-beam foundation belong under `foundations/`.
Human-facing identifiers are `B1.x`, `B2.x`, and `B12.x`; filesystem stems use
lowercase underscores, for example `b1_1_garicano_autarky` and
`b12_1_interface`.

Each implemented experiment must contain:

- `README.md`: the source result, citation key, assumptions, intended
  mechanism, and source-reproduction versus HLS-translation status;
- a small configuration fixture with parameters and numerical tolerances; and
- executable source only after the corresponding specification is frozen.

Each generated result directory must contain a `manifest.json` recording the
experiment ID, source citation, kind (`source_reproduction` or
`hls_translation`), command, repository commit, configuration hash, and pass/
fail status.  Figures, tables, and metrics that are reviewed scientific evidence
may be versioned; logs, caches, and temporary arrays are generated artefacts and
must not be edited manually.

No Beam 1, Beam 2, or integration experiment is implemented by this migration.
