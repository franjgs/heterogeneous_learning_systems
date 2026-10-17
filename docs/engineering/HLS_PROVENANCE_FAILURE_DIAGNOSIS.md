# HLS provenance and integrity failure diagnosis

**Audit started:** 2026-10-16 11:26 +02:00. **Recorded:** 2026-10-16 11:37 +02:00 (Europe/Madrid).
**Repository state:** branch `feature/hls-laboratory-v1`, `HEAD` `4940d4b22d7ea67e49b0f55f9e8afac37c4850da`.
**Scope:** read-only diagnosis. No source, manifest, output, or expected hash was changed.

## Executive result

The documented count of 13 failures still reproduces in the complete suite:
`PYTHONPATH=src:. pytest -q` → **1237 passed, 13 failed in 318.30 s**. These
are 13 failing test cases but six underlying failure families. The targeted
safe provenance run also reproduced the relevant source and artifact checks;
the complete run supplies the current total and exact identities. No campaign
runner was invoked directly. The failures do not all have the same meaning:
some are validators tied to a different point in time, while two provenance
gaps prevent full reconstruction of frozen source evidence.

The test suite did not change any of the scoped historical result directories.
The initial dirty worktree was preserved; in particular,
`src/hls/finite_problem_belief.py` was already modified before this audit.

Classification key: **A** referenced content differs from its frozen digest;
**B** stale path/count/reference; **C** manifest or verifier applies the wrong
provenance contract; **D** required historical evidence is unavailable;
**E** environmental dependency; **F** cause undetermined. No failure was
classified as E or F based on the evidence below.

## Reproduced failures

| # | Test and exact observed failure | Classification and evidence | Confidence / reproducibility impact | Minimum correction proposal (not performed) |
|---:|---|---|---|---|
| 1 | `tests/foundations/test_result_manifests.py::test_every_foundation_result_has_consistent_manifest` — assertion expected 11 `metrics.json` directories; observed 12. The additional `b2_5_gutjahr_switching` directory has a manifest, and its config/code/result hashes and metrics metadata all match. Manual read-only validation found that `b13_joint_value` has `metrics.json` but no `manifest.json`; the count assertion currently masks this second defect. | **B** for the stale expected inventory count; **D** for the separate missing B13 manifest. | High. Inventory gate fails; B13 provenance cannot be reconstructed from this test’s required manifest contract. Other 11 available manifests passed a manual check of fields and hashes. | Update the inventory to enumerate intended artifacts; recover B13’s original provenance if available. If it cannot be recovered, record the gap explicitly rather than fabricate a manifest. This needs review because a new/reconstructed manifest changes historical evidence. |
| 2 | `tests/test_b3_adaptive_development.py::test_real_provenance_and_validation_only_tables` — `RuntimeError: run-level provenance mismatch: protocol_sha256`. | **C.** B3 inherits B2.3’s frozen run. Its header expects `57f86fed…`; current `docs/experimental_foundations/B23_PROTOCOL.md` is `740ca26e…`. The run header identifies commit `541708a0…`; `git show 541708a0…:docs/experimental_foundations/B23_PROTOCOL.md` hashes to the expected `57f86fed…`. Thus the historical protocol is recoverable at the recorded commit, but the validator compares it with today’s source. | High. Blocks downstream B3 reproduction but does not by itself show B2.3 output corruption. | Validate the protocol blob at the manifest’s recorded source commit (and keep a separate current-source comparison); do not rewrite the run manifest. |
| 3 | `tests/test_b4_protected_development.py::test_protection_manifest_is_train_only_balanced_and_deterministic` — same B2.3 `protocol_sha256` mismatch through B4→B2.4→B2.3 parent audit. | **C**, same shared root as #2. | High. Blocks B4 parent provenance audit. | Same commit-pinned validation correction as #2; preserve both parent manifests. |
| 4 | `tests/test_b5_gradient_protected.py::test_parent_provenance_and_no_test_training_inputs` — same B2.3 `protocol_sha256` mismatch in B5’s parent audit. | **C**, same shared root as #2. | High. Blocks B5 parent provenance audit. | Same commit-pinned validation correction as #2. |
| 5 | `tests/test_rq0_integrated.py::test_real_inventory_provenance_hashes_and_validation_reconstruction` — same B2.3 `protocol_sha256` mismatch while building RQ0’s inherited inventory. | **C**, same shared root as #2. | High. Blocks reconstruction of the RQ0 inherited inventory. | Same commit-pinned validation correction as #2. |
| 6 | `tests/test_rq0_integrated.py::test_validation_policy_checks_are_finite_and_equivalent` — same upstream mismatch from `runner.build_inventory()`. | **C**, same shared root as #2. | High. This is a second downstream test blocked by one parent provenance check, not an independent scientific discrepancy. | Same commit-pinned validation correction as #2. |
| 7 | `tests/test_campaign2_execution.py::test_design_inherited` — `run.preflight()` asserts the frozen source digest for `src/hls/finite_problem_belief.py`; expected `4ea7e964…`, observed worktree `992a8eed…`. | **A**, with **D** as the recovery problem. The branch `HEAD` blob is `6625f1f1…`, also not the expected hash; the expected source blob was not found in available local Git history. The worktree file was dirty at audit start, so the worktree value is not a clean-HEAD value. | High that the current checkout fails the frozen digest; medium-high that the exact frozen source is unavailable locally. This materially weakens semantic provenance for consumers of that source. | Preserve the local file. Locate the exact frozen source in an authoritative archive/remote/history and verify its relation to the frozen outputs; otherwise explicitly disposition the missing source. Never replace the expected digest with the current one. |
| 8 | `tests/test_campaign2_preregistration.py::test_prerequisite_and_source_hashes_are_frozen` — same expected `4ea7e964…` vs worktree `992a8eed…`. | **A + D**, same shared root as #7. | High. Frozen Campaign 2 source identity cannot be checked against the current file. | Same source-recovery and review path as #7. |
| 9 | `tests/test_campaign2_theory.py::test_preexperiment_manifest_and_contamination_boundary` — manifest source-hash comparison fails on `src/hls/finite_problem_belief.py` with the same values. | **A + D**, same shared root as #7. | High. Blocks a source-integrity subcheck of the theory preregistration; not evidence that its frozen numerical output changed. | Same source-recovery and review path as #7. |
| 10 | `tests/test_campaign3_meta_voc_confirmatory.py::test_pre_execution_manifest_and_raw_integrity_when_present` — `verify_frozen()` reports `frozen input hash changed: src/hls/finite_problem_belief.py`. | **A + D**, same shared root as #7. | High. Blocks current reconstruction of the confirmatory input firewall. | Same source-recovery and review path as #7. |
| 11 | `tests/test_strategy_discrimination_gate.py::test_source_hashes_and_raw_output_hashes` — frozen source digest expected `4ea7e964…`, observed `992a8eed…`. | **A + D**, same shared root as #7. | High. Gate output hashes are checked only after this source check, so this failure alone does not demonstrate a raw-output mismatch. | Same source-recovery and review path as #7. |
| 12 | `tests/test_campaign2_preregistration.py::test_no_confirmatory_execution_result_artifacts_or_frozen_file_changes` — the preregistration’s zero-at-freeze contamination audit passes, but the test finds later Campaign 2 result files under `results/**` and rejects them. | **C.** The test applies a historical “nothing executed yet” condition to the current tree, after Campaign 2 was later executed and archived. The test’s own manifest records the freeze-time audit separately. | High. It invalidates this present-day contamination guard; it does not establish that the preregistration was contaminated when frozen. | Check the frozen audit and repository state at the preregistration commit, or explicitly scope allowed post-registration Campaign 2 outputs. Do not remove valid results. |
| 13 | `tests/test_campaign2_state_coverage_audit.py::test_frozen_inputs_and_completed_artifacts` — closure digest comparison first fails for `docs/experiments/CAMPAIGN_2_RESULTS.md`: expected `08771555…`, observed `79ae9645…`. Three further declared document digests also mismatch: `CLAIM_EVIDENCE_LEDGER.md` (`3bb0abe3…` vs `6a8c3afd…`), `EQUATION_TRACEABILITY.md` (`8e023e97…` vs `920dadab…`), and `PAPER_SOURCE_MAP.md` (`31cb6676…` vs `f87a6c68…`). The closure declares `results_commit=dabf6bab…`, but those files at that commit also do not match the recorded digests; expected document blobs were not found in available branch history. | **C + D.** The closure provenance is internally inconsistent with its declared commit for these four mutable documents, and the frozen document snapshots are unavailable in reachable history. Other closure-listed files checked before this mismatch remain untouched; the test stops at the first mismatch. | High for the four exact mismatches; medium-high for non-recoverability from available Git history. Blocks full closure-document provenance, not automatically the frozen numeric result files. | Do not rewrite the closure JSON. Recover original document snapshots if an authoritative copy exists; otherwise add a separately approved disposition/supplemental provenance record and narrow validation to immutable outputs and commit-pinned sources. |

The test suite’s current 13 failures are therefore reproducible, but several
are downstream manifestations of the same root cause. The six root-cause
issues are: stale foundation count, missing B13 manifest, B2.3 current-source
comparison instead of commit-pinned verification, missing frozen
`finite_problem_belief.py` source snapshot, time-insensitive preregistration
contamination check, and Campaign 2 closure/document hash inconsistency.
The latter two missing-evidence issues materially limit reconstruction. B2.3
is different: its frozen protocol is present at the recorded Git commit, so a
commit-aware verifier can restore verification without changing historical
evidence.

## Repair order and approval boundary

1. **Recover missing frozen source evidence** for
   `src/hls/finite_problem_belief.py` and B13’s manifest, using authoritative
   provenance only. Scope: source/result archaeology; potentially material to
   interpretation. Do not restore over current local work or synthesize hashes.
2. **Make validators time/commit aware** for B2.3 and Campaign 2 preregistration
   contamination. Scope: tests and validation code; low change to evidence,
   but requires maintaining the historical contracts rather than relaxing
   them.
3. **Disposition closure-document hashes** against the closure’s declared
   commit or recover the intended snapshots. Scope: provenance validator and
   an approved supplemental record; medium-to-high risk if the old closure is
   edited.
4. **Correct the foundation inventory expectation** and test B13 explicitly.
   Scope: test only if B13 provenance is recovered; otherwise preserve a
   visible missing-manifest failure.

Corrections 2 and the narrow inventory assertion could restore valid
verification without changing scientific evidence. Recovering missing source
or manifest evidence, or amending frozen closure provenance, requires explicit
PI/CE disposition. No repair was made under this diagnosis authorization.

## Exact validation performed

- `PYTHONPATH=src:. pytest -q` — **1237 passed, 13 failed in 318.30 s**.
- A focused subset of 17 provenance/integrity nodes was also run to capture
  stack traces safely; it reproduced 11 failures and passed 6 checks. The
  full suite subsequently confirmed the exact 13 current identities above.
- Manual read-only checks: all 11 extant foundation manifests were checked
  against their `metrics.json`, config, code and result hashes; 10 passed,
  B2.5 passed, B13 manifest absent. B2.3 historical protocol digest was
  confirmed from commit `541708a0…`. All four Campaign 2 closure document
  mismatches were enumerated.
- No simulator, test, manifest, frozen hash or result file was edited.
