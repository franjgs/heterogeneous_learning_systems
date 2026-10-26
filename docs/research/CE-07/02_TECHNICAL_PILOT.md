# HLS-CE-07.3 — Technical pilot

**Date:** 2026-10-26  
**Status:** six of six authorized simulations completed and validated.  
**Interpretation:** descriptive technical pilot only; no inferential analysis
and no confirmatory campaign.

## Frozen pilot scope

The pilot compared only CE-07 organizations A and B at N=12 and K=4, with
`h=0.9`, `l=0.6`, four equiprobable stationary task families, horizon 400,
Poisson arrival rate `0.55 × 12 = 6.6`, CE-04 service (lognormal mean 1.25,
CV 0.30), deadline slack 3, one FCFS queue/one active service per agent, and
the original P1 score `q_ik × F_i`. Learning and cooperation were off. Seeds
were 30010, 30011, and 30012: exactly six runs (three matched A/B pairs).

The scientific configuration SHA-256 is
`1f64ab3b3675adb0a65b3a538f7610bbb86efaabfa8f8c64a8cde6a41bc09770`.
The execution used CE-04 code unchanged from base commit
`b6e17cdab4d2a41e7e93c63e4eb8f566d90a8801`; `src/hls/ce04.py` has no diff
against that base. Source, environment, configuration, result and tie-log
hashes are in the [pilot manifest](../../../results/experiments/hls_ce07_technical_pilot/manifest.json).

## Identifier control and P1 ties

For each seed, a reproducible permutation was generated from
`SeedSequence([seed, 12, 707])`, where 707 is a dedicated profile-label stream.
The mapping is **new array slot → canonical profile ID** and was applied
identically to A and B:

| Seed | Profile ID by slot 0–11 |
|---:|---|
| 30010 | 3, 8, 1, 6, 9, 0, 5, 2, 11, 4, 10, 7 |
| 30011 | 9, 8, 10, 1, 5, 3, 4, 6, 2, 7, 11, 0 |
| 30012 | 4, 1, 2, 6, 8, 0, 10, 3, 9, 5, 11, 7 |

Tie instrumentation wrapped CE-04's `_choose_with_tie`, recorded the exact
top-score tie candidates, selected slot and priority rank, then called the
original helper with the original scores, admissible set and rank vector. It
did not change the chosen agent. The instrumentation and temporary CE-07
competence lookup were restored after every run. The full candidate/decision
trace is in `exact_tie_decisions.json`.

The slot-based priority has observable consequences in exact ties: there were
3,859 such selection decisions under A and 2,337 under B. Each selected slot
is also mapped back to its canonical profile ID in the tie log. The common
per-seed row permutation controls arbitrary profile placement relative to
numeric slot priorities; the recorded finite pilot does not establish that
every identifier assignment yields identical outcomes.

## Results by matched seed

Success-on-time uses all arrived tasks as denominator. `B−A` is shown in
percentage points; no test or confidence interval was calculated.

| Seed | Arrivals each | A correct on time | B correct on time | B−A (pp) | Selected q mean A / B | Mean wait A / B | Rejected A / B | Late A / B | Mean utilization A / B | Exact ties A / B |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 30010 | 2,627 | 1,748 (66.54%) | 2,229 (84.85%) | +18.31 | 0.7112 / 0.8720 | 0.4576 / 0.3877 | 0 / 0 | 137 / 89 | 0.6771 / 0.6837 | 1,255 / 750 |
| 30011 | 2,567 | 1,733 (67.51%) | 2,173 (84.65%) | +17.14 | 0.7143 / 0.8752 | 0.4479 / 0.3595 | 0 / 0 | 118 / 87 | 0.6555 / 0.6666 | 1,283 / 788 |
| 30012 | 2,633 | 1,721 (65.36%) | 2,210 (83.93%) | +18.57 | 0.7090 / 0.8744 | 0.4514 / 0.3425 | 0 / 0 | 150 / 82 | 0.6824 / 0.6800 | 1,321 / 799 |

The mean of the three paired B−A differences is +18.01 pp, reported only as a
descriptive pilot summary. B has greater mean selected competence and fewer
late tasks in all three runs; utilization is similar. These outcomes are
consistent with P1 exploiting the higher per-function competence available
in B, but three seeds do not support a confirmatory claim or generalization.
The pilot does not isolate a causal pathway from competence structure through
queueing to success.

## Validation and reproducibility

- Exact CE-07 marginals: `27/40 = 0.675` for all four functions in A and B;
  every function's maximum is 0.9. The structures have different row-profile
  multisets.
- **Six/six** runs completed at N=12 with P1, and each passed task-ID and
  arrival conservation, competence-mean, selected-agent, service-potential,
  correctness-potential, on-time-outcome, FCFS/capacity and policy-update
  checks. No P1 updates occurred.
- Each A/B pair shares the exact arrival trajectory and profile permutation.
  A pre-run digest covered the complete task×agent service and paired
  correctness-potential table; observed assigned outcomes were also checked
  against CE-04's keyed potential functions. Pair digests and admitted counts
  are in `paired_validation.json`.
- Seeds, permutation streams, profile mappings, tied candidate slots and
  selected physical profile IDs are recorded. Tests confirmed deterministic
  permutation generation, potential-table digest reproduction, tie-helper
  behavior and restoration of CE-04 functions. Focused tests:
  `pytest -q tests/test_ce07_structure.py tests/test_ce07_pilot.py` — **9 passed**.
- No full simulation was repeated, because the instruction required exactly
  six. Reproducibility is supported by deterministic keyed generators,
  recorded configuration/source hashes and per-run output hashes; exact replay
  of the six outputs remains unverified in this pilot.
- No change to `src/hls/ce04.py`, the P1 policy, CE-04 results or parameters.

## Technical disposition

**GO técnico para preparar la campaña confirmatoria; ejecución no autorizada
por esta orden.** El pipeline de seis réplicas, la permutación de
identificadores y el control de potenciales emparejados funcionaron. La
dirección descriptiva fue consistente en los tres pares, pero el piloto no se
diseñó para inferencia estadística. Detenerse aquí y devolver los resultados
al CE; no añadir escenarios, políticas, mecanismos ni experimentos.

## Artifacts

- Runner: [experiments/run_hls_ce07_technical_pilot.py](../../../experiments/run_hls_ce07_technical_pilot.py)
- CE-07 adapter: [src/hls/ce07_pilot.py](../../../src/hls/ce07_pilot.py)
- Structure generator: [src/hls/ce07_structure.py](../../../src/hls/ce07_structure.py)
- Tests: [tests/test_ce07_pilot.py](../../../tests/test_ce07_pilot.py)
- Results: [pilot result directory](../../../results/experiments/hls_ce07_technical_pilot/)
