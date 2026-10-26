# HLS-CE-04 — Confirmatory campaign results

**Date:** 2026-10-26
**Status:** Campaign complete; 1,080/1,080 replicas passed runtime validation.
**Scope:** Confirmatory results for the CE-04 synthetic assignment scenario.

## 1. Campaign and provenance

The campaign followed the frozen CE-04 configuration: 30 seeds (1000–1029),
N∈{12,24,48}, H∈{H0,H1,H2}, and P∈{P0,P1,P2,P3}, giving 1,080 replicas.
The canonical scientific configuration hash is
`c72bdca82906daa2118b415d3ba76d1fbfac87c47a1c3ee72fea7677e4b8a1b5`, identical
to the technical pilot. The execution baseline was commit
`70d1f95cd5d0a19ca998c5d996cd673530262e95`. The focused preflight suite passed
(53 tests). Environment: Python 3.11.9, NumPy 1.26.4, SciPy 1.13.1, SimPy
4.1.2, macOS arm64 / Apple M2 Max.

Each replica was checked for task conservation and identity, one assignment
and final execution per admitted task, FCFS and single-agent capacity,
deadline scoring, common admission at F≥0.50, mean competence 0.775 per task
family, metric finiteness, and policy-specific effective estimator updates
after observable feedback. Reconstructed admission checks were retrospective
and were not made available to policies. Task IDs matched across all 12
conditions in each of the 90 seed×scale workload blocks, and reconstructed
task trajectories matched their recorded SHA-256 signatures. The
[pairing audit](../../../results/experiments/hls_ce04_campaign/pairing_audit.json)
records this check. Keyed outcome streams kept service and correctness
potential outcomes policy-independent. There
were zero validation failures and no warnings. Recovery after demand changes
remained excluded as ordered; it was not replaced by another measure.

Execution took **1,820.88 s wall time** (30 min 20.88 s), **1,114.69 s summed
replica CPU time**, and **887.52 s accumulated decision time**. Process peak
RSS was **287,866,880 bytes** (`ru_maxrss`, macOS). The full task-level
ExperimentRun log is a 396 MB compressed local artifact; its digest is
recorded in the [manifest](../../../results/experiments/hls_ce04_campaign/artifact_manifest.json).
The lighter configuration, 1,080-row metrics file, validation summary and
analysis are published alongside the manifest. Reproduction commands and
exact hashes are in that manifest; the confirmatory analysis is reproducible
with [`experiments/analyze_hls_ce04_confirmatory.py`](../../../experiments/analyze_hls_ce04_confirmatory.py).

## 2. Statistical analysis

The unit of analysis is the independent seed-level replica. Differences are
paired within seed at a fixed N; all values below are percentage points (pp).
Each 95% interval is a percentile paired bootstrap over 30 seed differences
(10,000 resamples). Two-sided paired t-test p-values were adjusted with Holm
over the complete, prespecified family of 25 contrasts: the 15 C1–C5
contrasts by scale plus 10 adjacent-scale differences. The intervals shown
are nominal 95% intervals and are not multiplicity-adjusted. TOST tests use
the preregistered ±2 pp margin; their p-values are Holm-adjusted over the same
25 contrasts. Positive-seed counts show directional consistency, not a
separate significance test.

### 2.1 C1–C5 at each scale

| Contrast | N | Mean pp | Paired bootstrap 95% CI | Positive seeds | Holm p | TOST Holm p | Equivalent within ±2 pp? |
|---|---:|---:|---:|---:|---:|---:|:---:|
| C1: H2−H0 under P1 | 12 | +11.19 | [10.89, 11.50] | 30/30 | 1.17e−32 | 1.000 | No |
| C1: H2−H0 under P1 | 24 | +11.69 | [11.47, 11.91] | 30/30 | 2.65e−37 | 1.000 | No |
| C1: H2−H0 under P1 | 48 | +11.55 | [11.42, 11.68] | 30/30 | 1.05e−43 | 1.000 | No |
| C2: P1−P0 under H2 | 12 | +11.25 | [10.97, 11.54] | 30/30 | 1.26e−33 | 1.000 | No |
| C2: P1−P0 under H2 | 24 | +11.65 | [11.41, 11.88] | 30/30 | 1.14e−36 | 1.000 | No |
| C2: P1−P0 under H2 | 48 | +11.54 | [11.40, 11.68] | 30/30 | 5.98e−43 | 1.000 | No |
| C3: P2−P1 under H2 | 12 | −6.46 | [−7.27, −5.65] | 0/30 | 2.44e−14 | 1.000 | No |
| C3: P2−P1 under H2 | 24 | −7.42 | [−7.90, −6.95] | 0/30 | 3.24e−22 | 1.000 | No |
| C3: P2−P1 under H2 | 48 | −9.90 | [−10.31, −9.53] | 0/30 | 1.69e−28 | 1.000 | No |
| C4: P3−P2 under H2 | 12 | +0.78 | [0.01, 1.55] | 18/30 | 0.457 | 0.047 | Yes |
| C4: P3−P2 under H2 | 24 | +1.41 | [0.93, 1.90] | 25/30 | 4.49e−05 | 0.231 | No |
| C4: P3−P2 under H2 | 48 | +4.19 | [3.77, 4.61] | 30/30 | 5.21e−17 | 1.000 | No |
| C5: interaction, P3 vs P0 | 12 | +6.14 | [5.72, 6.57] | 30/30 | 5.85e−21 | 1.000 | No |
| C5: interaction, P3 vs P0 | 24 | +6.28 | [5.99, 6.58] | 30/30 | 6.80e−26 | 1.000 | No |
| C5: interaction, P3 vs P0 | 48 | +6.53 | [6.32, 6.76] | 30/30 | 2.58e−30 | 1.000 | No |

All 30 seed-level differences for every confirmatory contrast are retained in
[`confirmatory_analysis.json`](../../../results/experiments/hls_ce04_campaign/confirmatory_analysis.json).

### 2.2 Adjacent-scale contrasts

Each entry is the change in a given C contrast when increasing scale, with
the seed paired across N. The demand and resources scale proportionally as
specified.

| Effect contrast | Scale comparison | Mean pp | Paired bootstrap 95% CI | Positive seeds | Holm p | TOST Holm p | Equivalent within ±2 pp? |
|---|---|---:|---:|---:|---:|---:|:---:|
| C1 | N24−N12 | +0.50 | [0.10, 0.88] | 21/30 | 0.177 | 3.73e−07 | Yes |
| C1 | N48−N24 | −0.14 | [−0.39, 0.11] | 11/30 | 0.907 | 2.41e−13 | Yes |
| C2 | N24−N12 | +0.40 | [−0.00, 0.78] | 22/30 | 0.457 | 1.14e−07 | Yes |
| C2 | N48−N24 | −0.12 | [−0.38, 0.15] | 12/30 | 0.907 | 5.70e−13 | Yes |
| C3 | N24−N12 | −0.96 | [−1.98, 0.03] | 13/30 | 0.460 | 0.451 | No |
| C3 | N48−N24 | −2.48 | [−3.06, −1.89] | 2/30 | 8.21e−08 | 1.000 | No |
| C4 | N24−N12 | +0.64 | [−0.29, 1.59] | 17/30 | 0.859 | 0.081 | No |
| C4 | N48−N24 | +2.77 | [2.11, 3.44] | 29/30 | 8.52e−08 | 1.000 | No |
| C5 | N24−N12 | +0.14 | [−0.36, 0.64] | 14/30 | 0.907 | 9.68e−07 | Yes |
| C5 | N48−N24 | +0.25 | [−0.09, 0.60] | 18/30 | 0.859 | 1.62e−09 | Yes |

The C1, C2 and C5 effects are equivalent across adjacent scales within the
specified ±2 pp margin under the adjusted TOST tests. For C3 and C4, at least
one adjacent-scale difference is not equivalent; C3 becomes more negative
from N=24 to 48, while C4 increases from N=24 to 48. The N=24−12 scale
differences for C3 and C4 remain indeterminate relative to both zero and the
equivalence margin.

## 3. Descriptive operating characteristics

The following values are descriptive means across H0/H1/H2 and 30 seeds at
each scale. They are not additional confirmatory comparisons, and no
confidence intervals or tests are attached. Latency is completion minus
arrival for completed tasks; service cost per success is total service time
divided by on-time correct tasks. Decision time is accumulated per replica.

| N | Policy | Success-on-time | Mean latency (time units) | Service time / success | Decision time (s/replica) |
|---:|---|---:|---:|---:|---:|
| 12 | P0 | 77.20% | 1.295 | 1.618 | 0.100 |
| 12 | P1 | 82.67% | 1.476 | 1.516 | 0.068 |
| 12 | P2 | 77.71% | 1.773 | 1.612 | 0.075 |
| 12 | P3 | 79.13% | 1.472 | 1.582 | 0.257 |
| 24 | P0 | 77.42% | 1.259 | 1.613 | 0.386 |
| 24 | P1 | 83.11% | 1.447 | 1.508 | 0.257 |
| 24 | P2 | 77.37% | 1.852 | 1.619 | 0.286 |
| 24 | P3 | 79.44% | 1.451 | 1.575 | 0.985 |
| 48 | P0 | 77.47% | 1.252 | 1.614 | 1.512 |
| 48 | P1 | 83.10% | 1.458 | 1.509 | 0.998 |
| 48 | P2 | 75.80% | 1.962 | 1.651 | 1.107 |
| 48 | P3 | 79.44% | 1.455 | 1.575 | 3.831 |

Descriptive task-family success rates averaged over scales, compositions and
seeds were, for P0: 77.5%, 77.2%, 77.4%, 77.4%; P1: 82.5%, 82.7%, 82.7%,
84.5%; P2: 77.3%, 76.4%, 76.6%, 77.9%; and P3: 79.2%, 79.5%, 79.5%, 79.0%.
Across the same aggregation, phase success rates were P0: 77.2%, 77.2%,
77.7%; P1: 83.2%, 81.7%, 84.4%; P2: 75.8%, 76.5%, 79.5%; and P3: 78.2%,
79.7%, 80.6%. These summaries are exploratory descriptions of the existing
factorial and should not be read as additional tests.

## 4. Interpretation

### Findings supported in this scenario

- **C1 and C2:** H2 exceeds H0 under the information-complete P1 reference by
  about 11.2–11.7 pp at all three scales. P1 also exceeds P0 under H2 by
  about 11.3–11.7 pp. Effects are positive in all 30 seeds and remain
  significant after Holm adjustment. The ±2 pp TOST tests reject equivalence.
- **C3:** P2, which uses observed-history Beta estimates, performs 6.5–9.9 pp
  below P1, consistently across all seeds and scales. The difference grows
  more negative between N=24 and N=48. This is evidence about this estimator,
  decision rule and observation process, not about learned information in
  general.
- **C4:** P3 does not show a supported gain over P2 at N=12; the adjusted
  TOST supports equivalence within ±2 pp there. At N=24, the +1.41 pp estimate
  is statistically different from zero after Holm adjustment, but below the
  2 pp practical margin and equivalence is not established after correction.
  At N=48, P3 is +4.19 pp over P2, positive in all seeds and significant
  after adjustment.
- **C5:** The H2−H0 effect is about 6.1–6.5 pp larger under P3 than under P0,
  positive in every seed and significant after adjustment. The corresponding
  interaction differences are equivalent across adjacent scales within ±2 pp.

The descriptive summaries show a quality/latency tradeoff for P1 relative to
P0: P1 has higher success-on-time and slightly lower service time per
successful task, while mean completion latency is higher. P3's decision
overhead grows with N in this implementation; at N=48 its accumulated
decision time is about 3.83 s per replica versus 1.51 s for P0. These costs
are measured separately from organizational service-time cost.

### Scientific interpretation and limits

Within this synthetic setting, heterogeneity with equal mean competence can
be exploited by competence-informed assignment. Adaptive contextual
assignment also interacts positively with the H2 composition relative to
load-only P0. The results do not show that heterogeneity or adaptation is
universally beneficial, and they say nothing about cooperative execution:
each task is assigned to one agent, with no cooperation, learning, or transfer.

The large P2−P1 loss is compatible with limited or selectively observed
per-agent evidence making the Beta estimates less useful as the organization
scales. The campaign does not isolate that explanation from other properties
of the P2 estimator and its assignment feedback, so it remains an
interpretation, not a demonstrated mechanism. Likewise, P3's better result
than P2 at N=48 does not establish that LinUCB is generally superior or that
it matches P1's information.

External validity is limited to four task families, the specified mean-
preserving competence profile, stationary individual competencies, the
three demand phases and service law, the common 0.50 deadline admission
screen, and the implemented P0–P3 policies. P1 is an information-complete
reference, not a globally optimal planner. The 30 seeds characterize
simulation variability under this model, not a population of real
organizations. No universal claim about HLS, organizational scale, or
complementarity is warranted.

## 5. Provisional conclusion

The campaign provides a clear result for the implemented scenario: known
competence plus assignment (P1) substantially improves success-on-time over
load-only assignment (P0) in H2, while estimated-competence P2 loses much of
that advantage. P3 closes some of the gap at larger N, at measurable decision
cost; whether that tradeoff is practically worthwhile depends on the
application's valuation of compute overhead. The pattern supports continued
scientific interpretation of information quality, organizational
adaptation, and scale **within this model**, but does not itself establish a
novel algorithmic contribution or justify a general superiority claim.

The technical campaign is complete. Scientific assessment of the result and
any decision about further work remain with the CE/PI. No additional campaign
is implied by this report.
