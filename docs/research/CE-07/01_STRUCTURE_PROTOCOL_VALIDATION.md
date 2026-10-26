# HLS-CE-07.2 — Structure protocol validation

**Date:** 2026-10-26
**Status:** structure generation and pre-pilot checks implemented; no
experimental simulation or pilot executed.
**Scope:** the approved comparison of joint competence structures A and B at
N=12, K=4, under the unchanged CE-04 P1 simulator and operational semantics.

## Approved structure

Rows are agents and columns are functions. `h=0.9`, `l=0.6`.

```text
A = [h h h h] × 3; [l l l l] × 9
B = [h l l l] × 3; [l h l l] × 3;
    [l l h l] × 3; [l l l h] × 3
```

The mean of each function is exactly
`(3·0.9 + 9·0.6)/12 = 27/40 = 0.675` in both structures. Both have maximum
competence 0.9 for every function. Values and resources are unchanged by row
permutation. The structures are not equivalent by agent permutation: A's row
profile multiset is three all-high and nine all-low agents; B's is twelve
single-function specialists. No column permutation can make those row
profile multisets equal either.

The module `src/hls/ce07_structure.py` constructs the two exact matrices,
provides row-renaming and inverse-permutation utilities, checks the approved
invariants, and defines a serializable immutable pilot configuration. The
configuration requires exactly three distinct seed IDs but intentionally
does not choose them: this order supplies no IDs. The seeds used in unit tests
are test fixtures, not pilot assignments.

## CE-04 conditions reused without changes

The CE-04 protocol supplies the requested horizon (400), continuous-time
Poisson demand at `0.55N`, service lognormal mean 1.25/CV 0.30, deadline
arrival+3, one FCFS queue and one active service per agent, and the original
P1 score `q_ik × F_i` over the shared admissible set. CE-07 has stationary,
equiprobable task families. Learning and cooperation remain off. The CE-04
simulator source was not modified, and no task simulation was run for this
validation.

For matched comparisons, CE-04's demand generator is independent of
composition. Service variates are keyed by `(seed, N, task_id, agent_id,
service_stream)`; correctness uses the same key structure with its own stream
and compares a shared underlying uniform draw with the structure-specific
competence. Therefore A and B can use the same arrival trajectory, service
potential for each task-agent pair, and common-random-number coupling for
correctness. The success outcomes need not be equal because the competence
thresholds differ. These keys were checked in the CE-04 implementation and
exercised by focused tests; no campaign data were generated.

## P1 tie-breaking and renaming audit

P1 computes `q_ik × F_i`; ties are resolved by CE-04's deterministic,
seeded priority rank over agent array indices (`_choose_with_tie`). The
decision rule is permutation-equivariant **if the rename is consistent**:
competence rows, `F_i`, admissible IDs, the priority rank, assignments,
and agent-indexed potential outcomes must all be relabeled together. Tests
use the actual CE-04 tie-selection helper to verify that the chosen physical
agent is then unchanged; aggregate outcome and Gini calculations are
invariant to vector ordering.

A matrix-only renaming while retaining the same slot-indexed priority is not
equivariant under exact ties. A minimal test with B/F1 has three equal
high-competence candidates: before row swap, rank chooses physical agent 1;
after swapping the first two competence rows but leaving rank fixed to slots,
slot 1 is chosen, which now denotes the other physical agent. In a dynamic
run, different selected agents can have different keyed service/correctness
potentials and queues, so later decisions and finite-run metrics can diverge.
This is an index/tie coupling, not a change in the P1 objective. It does not
show that the fixed A-vs-B comparison is invalid; both structures use the
same slot priority and paired random streams under the stated labels.

**Control proposal, without changing P1:** for the later pilot, randomize the
mapping of each structure's agent profiles to numeric slots with a
predeclared, independent label-permutation stream, using the same permutation
for A and B within a matched seed. Keep the CE-04 tie rank and keyed
potential-outcome streams unchanged by slot. This averages arbitrary profile
placement relative to index-based tie priorities while retaining common
random numbers and the exact multiset of each approved structure. Record the
permutation in the run configuration. The control is a renaming/randomization
of equivalent rows, not a new policy. It should be included in the pilot
configuration before freeze; do not silently add it after outcomes are seen.

The present validation tests the algebraic consistent-renaming property and
the fixed-slot tie counterexample. The CE-04 runner has no interface to inject
a simultaneous rename of tie ranks and keyed potential outcomes. Consequently
an end-to-end event-simulator rename invariance test is not available without
changing that runner; CE-07 does not modify it. The proposed row-label
randomization is the compatible control for the subsequent pilot.

## Validation performed

- Exact rational marginal check: `27/40` for all four columns under A and B.
- Competence bounds and maxima: only 0.6/0.9; maxima are 0.9 in all columns.
- Joint structures differ by row-profile multiset, so no agent permutation
  maps A to B.
- Renaming utilities reject malformed permutations and preserve structure
  invariants.
- P1 tie-selection equivariance passes when priority is renamed consistently;
  matrix-only renaming demonstrably changes the physical tie winner.
- CE-04 paired streams are composition-independent; tests confirm the same
  workload and the common-uniform monotonic coupling for correctness.
- Tests: `pytest -q tests/test_ce07_structure.py tests/test_ce04.py
  tests/test_ce04_validation.py` — **27 passed**.
- `src/hls/ce04.py`, its P1 code and historical results are unchanged.
- No experiment, pilot, or campaign was run.

## Pilot readiness and remaining gate

The two competence matrices and mathematical validators are ready. **The pilot
is not ready to freeze or execute yet.** The CE must assign three new seed IDs
and disposition the label-randomization control above. The order's scientific
conditions are otherwise represented without adding a policy, mechanism,
learning, or cooperation. No other factors or research questions are proposed.

Keep CE-07 within its approved plan: compare these two joint structures under
the stated controls, then stop for CE review. Do not expand the pilot into a
new mechanism or additional heterogeneity scenarios.
