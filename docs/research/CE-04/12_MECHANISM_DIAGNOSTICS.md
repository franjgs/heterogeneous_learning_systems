# HLS-CE-04.8 — Mechanism diagnostics from the existing campaign

**Date:** 2026-10-26
**Scope:** Post-hoc descriptive diagnostics only. No simulation, parameter
selection, or additional confirmatory contrast was run.

## Data and calculation scope

The analysis uses the 1,080 replica metrics and per-task `ExperimentRun`
records from CE-04. The summary metrics, confirmatory analysis, configuration
and provenance are indexed by the [campaign manifest](../../../results/experiments/hls_ce04_campaign/artifact_manifest.json).
The 396 MB compressed task-level log is local-only; its SHA-256 is in that
manifest. The tables below were computed from those records. Rates are pooled
descriptive proportions unless otherwise stated; they are not new tests and
are not causal mediation estimates. For P2, true competence is used only
retrospectively to score estimation error; it was not available to the policy.

## 1. Absolute success-on-time by composition and scale

Percent of all arrived tasks that were correct and completed by deadline;
means pool task outcomes over the 30 seeds at each condition.

| N | H | P0 | P1 | P2 | P3 |
|---:|---|---:|---:|---:|---:|
| 12 | H0 | 77.3% | 77.3% | 74.4% | 76.7% |
| 12 | H1 | 77.2% | 82.3% | 76.8% | 77.9% |
| 12 | H2 | 77.2% | 88.4% | 82.0% | 82.8% |
| 24 | H0 | 77.4% | 77.4% | 74.3% | 76.8% |
| 24 | H1 | 77.4% | 82.9% | 76.1% | 78.5% |
| 24 | H2 | 77.4% | 89.1% | 81.7% | 83.1% |
| 48 | H0 | 77.5% | 77.5% | 73.4% | 76.8% |
| 48 | H1 | 77.4% | 82.8% | 74.9% | 78.3% |
| 48 | H2 | 77.5% | 89.0% | 79.1% | 83.3% |

H0 remains near 77% for every policy and scale. P1 gains strongly in H1/H2;
P2 also exploits specialization but falls below P1, with a larger shortfall
at N=48. P3 is between P1 and P2 in H2 and varies less across compositions.
These are descriptive repetitions of the campaign outcomes, not additional
significance claims.

## 2. Admission, correctness and deadlines

Pooling over H0–H2 within each N and policy:

| N | Policy | Admitted | Rejected | Correct among admitted | Completed by deadline | Late among admitted |
|---:|---|---:|---:|---:|---:|---:|
| 12 | P0 | 100.000% | 0.000% | 77.38% | 99.76% | 0.24% |
| 12 | P1 | 100.000% | 0.000% | 84.01% | 98.47% | 1.53% |
| 12 | P2 | 99.999% | 0.001% | 81.25% | 95.68% | 4.32% |
| 12 | P3 | 100.000% | <0.001% | 79.95% | 98.98% | 1.02% |
| 24 | P0 | 100.000% | 0.000% | 77.50% | 99.89% | 0.11% |
| 24 | P1 | 100.000% | 0.000% | 84.31% | 98.65% | 1.35% |
| 24 | P2 | 100.000% | 0.000% | 81.51% | 94.98% | 5.02% |
| 24 | P3 | 100.000% | 0.000% | 80.13% | 99.13% | 0.87% |
| 48 | P0 | 100.000% | 0.000% | 77.53% | 99.92% | 0.08% |
| 48 | P1 | 100.000% | 0.000% | 84.56% | 98.36% | 1.64% |
| 48 | P2 | 100.000% | 0.000% | 81.10% | 93.59% | 6.41% |
| 48 | P3 | 100.000% | 0.000% | 80.16% | 99.10% | 0.90% |

Admission was effectively universal: only a handful of tasks were rejected
across the full campaign. The distinction is after admission. P2 has the
largest late fraction, increasing with N; P3 has fewer late completions but
lower correctness than P1. Thus P2's deficit is associated descriptively
with both correctness and deadline performance, with the deadline component
especially pronounced. This does not by itself identify why P2 creates more
late work.

## 3. Differences by task family

Pooled success-on-time rate over H, N and seeds, by task family:

| Task family | P0 | P1 | P2 | P3 |
|---|---:|---:|---:|---:|
| T1 | 77.49% | 82.55% | 76.93% | 79.32% |
| T2 | 77.31% | 82.77% | 75.97% | 79.52% |
| T3 | 77.42% | 82.72% | 76.10% | 79.52% |
| T4 | 77.45% | 84.71% | 77.53% | 79.11% |

P1's higher T4 result is consistent with its ability to use the true
competence matrix and assign work to task specialists. P2's lower rates are
seen across all four families, not isolated to one family. The table pools
composition and scale; it does not test a policy×task interaction.

## 4. Assignment distribution and agent load

Mean coefficient of variation (CV) across agents for assigned-task counts,
averaged over scales and seeds:

| Composition | P0 | P1 | P2 | P3 | Primary-family match: P0 / P1 / P2 / P3 |
|---|---:|---:|---:|---:|---|
| H0 | 0.358 | 0.358 | 0.357 | 0.172 | n/a |
| H1 | 0.358 | 0.222 | 0.372 | 0.174 | 25.0% / 94.2% / 51.6% / 40.4% |
| H2 | 0.358 | 0.224 | 0.368 | 0.173 | 25.0% / 94.5% / 68.0% / 57.0% |

P1 sends about 91–96% of assignments to the agent's primary family in H1/H2
when inspected by scale, compared with 25% under composition-blind P0. P2
partly identifies specialists but has the highest task-count and service-load
dispersion. P3 keeps assignment counts more even; its specialist match is
above chance in H2 but well below P1. Across policies, the assignment-count
CV rises with N for P0/P1/P2 (the larger pool has more uneven per-agent
allocation), while P3's pooled CV is comparatively stable. These patterns
describe assignments and realized loads; they do not show that load
concentration alone caused lateness.

## 5. P2 competence observations and estimation error

P2 receives a correctness label for each executed task at completion. Across
H and N, it averages about 55 observations per possible agent×family cell,
but this mean hides a strongly skewed allocation of observations:

| N | Unobserved agent×family cells | Median observations/cell | 90th percentile | Maximum observed |
|---:|---:|---:|---:|---:|
| 12 | 18.3–19.8% | 10–11 | 174–198 | 293–301 |
| 24 | 31.0–33.4% | 2–3 | 195–210 | 312–325 |
| 48 | 41.9–43.0% | 1 | 208–216 | 326–328 |

The distribution becomes increasingly concentrated as the organization
scales: many agent×family pairs receive no evidence while a small number
receive hundreds of labels. The prior `Beta(1,1)` posterior starts at 0.5.
The following RMSE is over all agent×family cells, including unobserved cells
at their prior/posterior mean. It is a retrospective diagnostic against the
simulation's true competence matrix.

| N | H | Prior RMSE | t=100 | t=200 | t=300 | t=400 | After drain |
|---:|---|---:|---:|---:|---:|---:|---:|
| 12 | H0 | 0.275 | 0.258 | 0.251 | 0.250 | 0.249 | 0.249 |
| 12 | H1 | 0.278 | 0.254 | 0.249 | 0.245 | 0.243 | 0.243 |
| 12 | H2 | 0.288 | 0.240 | 0.232 | 0.230 | 0.226 | 0.226 |
| 24 | H0 | 0.275 | 0.257 | 0.252 | 0.251 | 0.250 | 0.250 |
| 24 | H1 | 0.278 | 0.256 | 0.249 | 0.246 | 0.246 | 0.246 |
| 24 | H2 | 0.288 | 0.249 | 0.239 | 0.237 | 0.234 | 0.234 |
| 48 | H0 | 0.275 | 0.262 | 0.259 | 0.258 | 0.258 | 0.258 |
| 48 | H1 | 0.278 | 0.262 | 0.256 | 0.254 | 0.253 | 0.253 |
| 48 | H2 | 0.288 | 0.258 | 0.248 | 0.246 | 0.244 | 0.244 |

RMSE declines over time but remains substantial; final RMSE on observed pairs
alone ranges about 0.211–0.245, while 31–43% of pairs at N=24/48 remain
unobserved. The larger C3 penalty at N=48 is therefore compatible with
incomplete, highly selective competence information. It is not proof that
selection bias, lack of exploration, shrinkage, or prior choice is the unique
cause. The campaign does not compare alternate P2 estimators or exploration
rules.

## 6. P3 rewards, updates and temporal performance

P3 receives one binary update per admitted task: reward 1 for correct and
on-time, otherwise 0. Counts below aggregate the 30 seeds for each N,H. The
feedback-delay measure is time from task arrival to reward observability.

| N | H | Updates | Reward=1 | Deadline-observed updates | Median delay | 95th-percentile delay |
|---:|---|---:|---:|---:|---:|---:|
| 12 | H0 | 79,037 | 76.68% | 1.03% | 1.387 | 2.450 |
| 12 | H1 | 79,036 | 77.95% | 1.04% | 1.386 | 2.439 |
| 12 | H2 | 79,037 | 82.77% | 0.98% | 1.378 | 2.438 |
| 24 | H0 | 158,404 | 76.75% | 0.91% | 1.372 | 2.409 |
| 24 | H1 | 158,404 | 78.47% | 0.87% | 1.368 | 2.399 |
| 24 | H2 | 158,404 | 83.08% | 0.84% | 1.360 | 2.386 |
| 48 | H0 | 316,751 | 76.76% | 0.93% | 1.376 | 2.420 |
| 48 | H1 | 316,751 | 78.26% | 0.90% | 1.374 | 2.407 |
| 48 | H2 | 316,751 | 83.31% | 0.86% | 1.358 | 2.391 |

For P3, about 99% of feedback is observed at completion and about 1% at the
deadline; late task correctness is not later substituted for the zero reward.
Pooled retrospectively by task arrival interval over all P3 conditions,
success-on-time was 77.83% at t∈[0,100), 79.17% at [100,200), 79.91% at
[200,300), and 80.69% at [300,400). These intervals cross the demand-phase
boundaries at 150 and 300, and task mix, queue state and accumulated updates
all change over time. The upward pattern cannot identify learning as its
cause. ExperimentRun records contain selected actions and reward events, but
not per-decision LinUCB scores or coefficient/covariance snapshots; the
internal source of P3's temporal behavior is therefore not directly observed.

## 7. Why C1 and C2 are similar

For each seed and scale, the definitions imply exactly:

`C1 − C2 = success(P0,H2) − success(P1,H0)`.

The mean absolute gap between those two baseline outcomes is only 0.418 pp
at N=12, 0.291 pp at N=24 and 0.218 pp at N=48 (maximum absolute seed-level
gaps: 1.195, 0.948 and 0.609 pp). The identity holds to numerical precision.
This explains why C1 and C2 estimates are close: both subtract nearly the
same baseline from `P1,H2`.

The design makes that near-symmetry plausible. Under H0 all agents have the
same q, so P1's `q×F` ranking reduces to ranking by deadline probability;
P0's least-expected-workload rule usually makes the same selection. Their
H0 assignment vectors were exactly identical in 30/30 seeds at N=12, 26/30
at N=24 and 29/30 at N=48. Under H2, P0 does not observe specialization and
its selection is independent of primary family; the task-wise mean q remains
0.775. These facts explain similarity in this setup; C1 and C2 are not two
independent replications of a scientific effect.

## 8. What can and cannot be distinguished

**Distinguishable from these data, within this simulator:** the policy-level
outcome differences in the frozen factorial; whether P1 routes toward true
specialists; P2's selected-label coverage and posterior error trajectory; P3's
observed reward frequency/timing and retrospective cohort performance; and
the algebraic source of C1/C2 similarity.

**Not identified by these records:** why P2's selective observations and
concentrated allocations produce its errors and lateness (no exploration,
prior, estimator or update-rule ablation); whether P3's temporal pattern is
caused by learning rather than changing demand/task mix/load (no no-update P3
control, and internal LinUCB scores are not logged); how much P3−P2 is due to
the algorithm versus its different feedback target (P2 learns correctness at
completion, including late answers; P3 learns on-time success with deadline
zeros); or effects of cooperation, transfer or changing competencies, which
were absent. Descriptive association between load, estimation error and
performance is not sufficient to assign mediation or causality.

All results remain specific to four synthetic task families, the chosen
competence matrix and service law, one task per agent at a time, the fixed
admission rule, and these four policies. No new confirmatory contrast or
scientific claim of general superiority is introduced here.
