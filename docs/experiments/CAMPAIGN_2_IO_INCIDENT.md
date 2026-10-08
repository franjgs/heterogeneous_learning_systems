# Campaign 2 — output-persistence incident and deterministic reconstruction

## Immutable failed-attempt evidence

The first attempt ran from 2026-10-07 22:04:51.336985 UTC to 22:32:36.232389 UTC.
Its seven table paths remained zero bytes despite positive in-memory counters.
No numerical scientific outcomes were inspected and no H1–H4/bootstrap analysis
was performed. This is an infrastructure failure, not a scientific FAIL.

The original files, `execution_manifest.json`, `raw_completion.json`, and
`validation_failure.json` remain unchanged in the parent result directory.
`failed_attempt_01_runner.py.txt` preserves the exact executed runner, SHA256
`0410c4d82e226d4e7a0a7a2bf44c50e2d2ac114b4ffe566f5d21ca9754898771`.
The failure record's SHA256 is
`3dd95eb4a7e6a49b4510d3e14c23745c6a107eee0b95f20c4ecd638318474e19`.
The successful reconstruction, if validated, is separately under `attempt_02/`;
it does not overwrite or relabel the failed attempt.

## Root-cause diagnosis and evidence strength

The persistence design exposed empty, public CSV paths in a synchronized
directory while holding writable descriptors to them throughout computation.
Replacing such a path does not redirect the already-open descriptor: subsequent
CSV/gzip writes can succeed into an unlinked inode while the visible path stays
empty. The original runner then declared completion from counters and hashes
without reopening and checking table contents. Thus successful computation and
successful writes did not imply persistent, accessible records.

There is direct evidence of synchronization activity in the vulnerable window:
Google Drive's local structured log contains two records at
22:05:02.904631 and 22:05:02.905118 UTC listing **all seven incident table paths
and seven `.tmp.drivedownload/` paths in the same batches**. The visible empty
files have change times at approximately 22:05:06 UTC and mode 0600, unlike the
0644 ordinary new probe files. These are extracted in `io_forensic_evidence.json`
with record offsets, timestamps and hashes. No unrelated log records are copied.
The generic decoder reads four-byte little-endian frame lengths and protobuf
wire fields; numeric event codes 41/42 are preserved **without inventing names
or undocumented syscall semantics**.

The engineering diagnosis is a public-path/open-descriptor identity race in
the synchronized namespace, with Drive rematerialization the supported forensic
explanation for the triggering replacement. **Historical descriptor inode IDs
were not recorded, so the exact historical rename syscall and initiator cannot
be proved directly.** The Drive trace is observed evidence; attributing the
historical path replacement to that activity is a forensic inference, not a
mathematical proof or a new HLS scientific result. Ordinary serialization,
process-pool and delayed-write probes did not spontaneously reproduce it.

The replacement failure mode itself is independently reproduced deterministically:
open public files using the original descriptor pattern, atomically replace
their paths with empty files, then write/close the original descriptors. All
visible files stay zero bytes despite successful writes. This exactly matches
the incident's persistence signature and explains why the earlier short tests
passed: they never replaced a public path while it was open.

## I/O-only correction and regression checks

`artifact_io.persist_tables` writes unchanged row dictionaries into private
`/private/tmp` staging files, outside the mirrored workspace. It closes all
streams, fsyncs, and reloads every plain/gzip table to verify headers, schema,
positive row counts and SHA256. Only then are closed, verified files copied
briefly into same-directory temporary files, fsynced and atomically published.
Every final public path is reopened and revalidated. A rewrite after publication
is an I/O exception, not successful completion. No public zero-byte placeholder
or long-lived public writable descriptor is needed during computation.

The fault-injection regression applies the same path replacement during private
staging: persisted/reloaded data now match exactly. A separate corruption test
forces truncation after publication and verifies a hard failure. The seven-table
synthetic end-to-end checks cover both plain/gzip formats, exact reloaded values,
and actual process-pool orchestration. They do not execute HLS teams or seeds.

The closed-loop generator's AST is checked against the archived failed runner:
it is identical except for deferring the side-effect-free counterfactual block.
This deferral implements the explicitly requested ordering: first persist and
verify 5,120 closed-loop runs and 15,360 eligible Q11-reference states; **only
after that gate passes** execute the unchanged C2.0 counterfactual primitive
from those reloaded states and the same recorded innovations. Fixed synthetic
states verify exact equality of deferred returns, branch observations, Bayes
posteriors and MIS-v2 states against direct frozen primitive calls.

The hypotheses, estimands, analysis source, bootstrap procedure, policies,
physics, inference, scenarios, teams, seeds and counterfactual definitions are
unchanged. Moving pure calculations after a persistence gate changes execution
ordering, not the generated closed-loop or counterfactual scientific values.
No RNG draws are added; JSON/CSV round trips preserve original float values.

## Retry and interpretation boundary

The user explicitly authorized an identical deterministic reconstruction after
diagnosis/regression/end-to-end I/O verification. This is not a new draw, seed
search, tuned outcome, or fresh preregistration. Seeds 10–49 were already computed
in the failed attempt and are replayed exactly. Both attempts remain traceable.
The original failure document remains a point-in-time record and is not rewritten
as though its cause had already been diagnosed. Results and interpretation exist
only if the reconstructed retained-data validation passes.

## Validated reconstruction

The retry passed its persisted/read-back count gate before any counterfactual
calculation: 5,120 closed-loop runs and 15,360 eligible Q11-reference states.
It then retained and independently validated all 46,080 counterfactual pairs,
184,320 branch decisions and the complete frozen factorial. The 38,846
equal-action controls returned exactly zero; branch transitions and branch
sums reproduced exactly. Only after full validation did the unchanged H1–H4
analysis and 10,000 whole-seed bootstrap run.

`attempt_02/closed_loop_count_validation.json`, `raw_completion.json`,
`validation_summary.json` and final `provenance.json` bind these phases and
their file hashes. The results report describes the scientific outcomes;
successful reconstruction does not erase the original infrastructure failure
or upgrade its forensic attribution from inference to direct syscall evidence.
