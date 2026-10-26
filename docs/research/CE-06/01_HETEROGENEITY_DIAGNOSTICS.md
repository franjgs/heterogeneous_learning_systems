# CE-06.3 — Isolated heterogeneity diagnostics

**Date:** 2026-10-26
**Status:** descriptive diagnosis and technical pilot completed; no confirmatory campaign run.
**Scope:** N=24, P1, fixed competencies, one agent per task, no cooperation or learning.

## Design and data provenance

The CE-04 campaign already contains the exact task-level records required for
post-hoc diagnostics: [per-task ExperimentRun records](../../../results/experiments/hls_ce04_campaign/replicas.experiment_runs.jsonl.gz).
Its [artifact manifest](../../../results/experiments/hls_ce04_campaign/artifact_manifest.json)
identifies the file as local-only, SHA-256
`4b85a240e2206be6e2f00a7bbd72fce2fca8df33007865124ab9bbe923f6f249`.
We streamed the records and selected only P1, N=24, H0/H1/H2: 90 replicas
(30 seeds per composition). No CE-04 simulations were repeated. Derived
replica and family/phase summaries are in the adjacent CE-06 result directory;
the source task log remains unmodified.

The authorized technical pilot used three new seeds, 30000–30002, for each of
H0/H1/H2 (nine simulations total). For each seed, the same generated demand
trajectory was passed to the three compositions. The frozen CE-04 configuration
hash is `c72bdca82906daa2118b415d3ba76d1fbfac87c47a1c3ee72fea7677e4b8a1b5`.
P1 was not changed: it still selects from the common admissible set by the
existing true-competence × deadline-probability score. The later CE-04 code
additions concern optional P2 causal diagnostics; the P2-only filter cannot
activate under P1. No simulator, scientific parameter, task, or policy code was
edited for CE-06.

## Metric definitions and reconstructibility

All listed metrics are reconstructible from the archived per-task events,
replica configuration, and existing per-agent vectors; therefore no new
simulator instrumentation was needed.

| Diagnostic | Definition / source | Status |
|---|---|---|
| Maximum competence by task family | `max_i q[i,k]`, recomputed from frozen CE-04 composition and seed | Reconstructed |
| Selected-agent competence | `q[selected_agent, family]` for admitted tasks | Reconstructed |
| Gap to family maximum | `max_i q[i,k] - q[selected_agent,k]` | Reconstructed |
| Assignment concentration | Gini and HHI over per-agent assignment counts; effective agents = 1/HHI | Reconstructed |
| Load and utilization | Per-agent service-time vector, utilization vector, assignment counts | Reconstructed |
| Waits | `service_start - arrival`; per-task event timestamps | Reconstructed |
| Rejections / late work | Rejection reason and completion/deadline fields | Reconstructed |
| Family and demand-phase outcomes | Correct-and-on-time divided by arrivals, by family and phase | Reconstructed |
| Instantaneous decision scores and all candidate sets | Not stored in task records | Not reconstructible; would require extra logging, not needed for this report |
| Time-varying internal queue snapshots | Not stored directly; event timestamps permit some external reconstruction, but not exact internal decision-state diagnostics | Partial / new instrumentation if later essential |

Gini is the population Gini of the N-vector; HHI is the sum of squared
assignment shares. Wait is measured only for admitted tasks. Success-on-time
uses all arrived tasks as denominator, consistent with CE-04. Per-family and
per-phase results are descriptive; no new confirmatory tests were introduced.

## Existing CE-04 results (30 seeds per composition)

| H | Success on time | Mean selected q | Mean gap to family max | Assignment Gini | Mean utilization | Mean wait | Late admitted / replica |
|---|---:|---:|---:|---:|---:|---:|---:|
| H0 | 77.39% | 0.7750 | 0.0000 | 0.1969 | 0.6819 | 0.0106 | 5.90 |
| H1 | 82.86% | 0.8438 | 0.0062 | 0.1227 | 0.6821 | 0.2746 | 89.60 |
| H2 | 89.09% | 0.9134 | 0.0116 | 0.1235 | 0.6818 | 0.3100 | 117.57 |

The maximum competence per family is 0.775, 0.850, and 0.925 in H0, H1,
and H2, respectively. Mean utilization remains essentially constant because
service time and resource count are held fixed. P1 selects agents close to
each family’s attainable maximum (small average gap), while its selected
competence rises with specialization. Assignment-count concentration is lower
in H1/H2 than in H0 in these records; this is not a general property of
specialization. Waiting and late admitted tasks also rise with H, showing that
better matching coexists with greater load imbalance across the agents serving
the demand mix. This descriptive association does not identify mediation or
causality.

Pooled success-on-time by family (H0 / H1 / H2): T1 77.5 / 83.0 / 89.4%;
T2 77.3 / 83.4 / 89.8%; T3 77.5 / 83.3 / 89.8%; T4 77.5 / 84.7 / 92.3%.
By demand phase: phase 1 77.4 / 83.6 / 90.4%; phase 2 77.4 / 82.9 / 88.9%;
phase 3 77.6 / 84.4 / 91.6%. These averages pool the original 30 matched
replicates and are descriptive summaries, not additional hypothesis tests.

## New technical pilot (three seeds per composition)

| H | Success on time | Mean selected q | Mean gap to family max | Assignment Gini | Mean utilization | Mean wait | Late admitted / replica |
|---|---:|---:|---:|---:|---:|---:|---:|
| H0 | 77.76% | 0.7750 | 0.0000 | 0.1907 | 0.6902 | 0.0138 | 7.00 |
| H1 | 83.22% | 0.8439 | 0.0061 | 0.1193 | 0.6885 | 0.2757 | 91.33 |
| H2 | 88.91% | 0.9137 | 0.0113 | 0.1221 | 0.6870 | 0.3161 | 128.33 |

The three matched pilot seeds show the same descriptive ordering in success
on time (H2 > H1 > H0). Family-level pilot rates (H0 / H1 / H2) were: T1
78.4 / 83.4 / 89.1%; T2 77.7 / 84.0 / 89.5%; T3 77.5 / 83.0 / 89.6%; T4
77.2 / 85.4 / 92.9%. Phase-level rates were: phase 1 78.3 / 84.4 / 90.5%;
phase 2 77.0 / 82.8 / 88.7%; phase 3 77.8 / 84.7 / 91.7%. With only three
replicates these figures are a technical check, not confirmatory evidence.
Matched success-on-time differences were H1−H0 = +5.53, +5.19, +5.68 pp;
H2−H0 = +11.61, +10.57, +11.29 pp; and H2−H1 = +6.08, +5.57, +5.61 pp
for seeds 30000, 30001, 30002, respectively. No inferential test or campaign
claim is based on these three pairs.

## Validation and interpretation limits

- Competence means were checked for every replica and equal 0.775 per family
  (absolute tolerance `1e-12`); the H-level maxima match the frozen generator.
- N, service law, resource count and arrival intensity were common. Each seed’s
  same task trajectory was reused for H0/H1/H2; the per-seed trajectory hashes
  are in `pilot_replica_diagnostics.csv`.
- Each pilot replica passed the existing CE-04 runtime validator, including
  task conservation, one assignment/execution, FCFS/capacity, deadline outcome,
  common admission and finite metric checks. P1’s code path and parameters
  were not changed.
- A repeated run of seed 30000, H1 produced the identical task-record SHA-256
  `7561168afa59c47325195a415ce7124ed06644cb3884a7866e13913f5a7304a5`.
- Tests: `pytest -q tests/test_ce04.py tests/test_ce04_validation.py
  tests/test_ce06_heterogeneity.py` — **24 passed**.

The pattern is consistent with the designed mechanism: P1 can exploit the
higher family-specific maxima created while keeping means fixed. It does not
show that heterogeneity alone improves collective performance under other
policies, demand profiles, service laws, or constraints. The pilot does not
support inferential claims. No confirmatory campaign was run or authorized by
this task.

## Files and execution

- Analysis: [src/hls/ce06_heterogeneity.py](../../../src/hls/ce06_heterogeneity.py).
- Reuse/post-processing and pilot runner:
- [experiments/run_hls_ce06_heterogeneity_pilot.py](../../../experiments/run_hls_ce06_heterogeneity_pilot.py).
- Tests: [tests/test_ce06_heterogeneity.py](../../../tests/test_ce06_heterogeneity.py).
- Summaries and record hashes: [pilot artifacts](../../../results/experiments/hls_ce06_heterogeneity_pilot/).
- Historical CE-04 artifact manifest:
  [CE-04 manifest](../../../results/experiments/hls_ce04_campaign/artifact_manifest.json).

Technical outcome: the diagnostic pipeline and pilot are ready for CE review
of a separate confirmatory authorization. This report makes no decision to
start that campaign.
