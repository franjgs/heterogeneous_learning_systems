# HLS-CE-04.12 — Confirmatory P2 calibration/load experiment

**Date:** 2026-10-26
**Status:** Confirmatory campaign complete; 240/240 replicas validated.
**Scope:** H2 only; N=12 and N=48; seeds 20000–20029.

## Design and integrity

The four conditions were B00 (original P2), B10 (20 external Bernoulli
observations per agent×task family before time zero), B01 (load cap), and B11
(both). Each seed and scale shared one demand trajectory, competence matrix,
tie order and seed-keyed potential-outcome basis across all four conditions.
B10 and B11 shared the same independent calibration draw. The common
`F_i >= 0.50` admission screen was unchanged. The cap used expected active
residual service plus 1.25 per queued task, took its median over the common
admissible set, retained loads `<= median+1.25`, and fell back to that set if
filtering emptied it.

The configuration hash required by the CE was verified before execution:
`0f99dee0b7f1e81e4c768dcac977f9cafe0091b934c69467ce27097408d588c0`.
Because that hash identifies the CE-04.11 pilot configuration (including its
pilot seeds), the confirmatory seed list is recorded separately in
[`execution_config.json`](../../../results/experiments/hls_ce04_causal_confirmatory/execution_config.json),
whose execution hash is
`b8603648a81b1c476af3f166bf3d904c95324e00cfb192d9488d3a009d652d99`. All
four cells within each seed-scale block had matching workload, competence and
potential-outcome key-basis digests; all B10/B11 calibration hashes matched.
The 240 distinct seed×scale×condition combinations are present, and every
replica passed the CE-04 and causal pairing validators.

Pre-execution gate: branch `feature/hls-laboratory-v1` was clean and synced
at commit `3f770dbb4d2966bb0266c015e45ee2b82edd31b2`; the focused command
`python -m pytest -q tests/test_ce04_causal.py tests/test_ce04.py tests/test_ce04_validation.py`
passed 33 tests.

## Confirmatory contrasts

The independent unit is the seed-level replica; differences are paired by
seed and shown in percentage points. Confidence intervals are percentile
bootstrap 95% intervals from 10,000 resamples. Two-sided paired t-test
p-values are Holm-adjusted over the three prespecified contrasts within each
scale. TOST uses ±2 pp; its p-values are Holm-adjusted over those same three
contrasts within each scale, separately from the difference-test family.

| N | Contrast | Mean pp | 95% bootstrap CI | Holm p | TOST ±2 pp (Holm) |
|---:|---|---:|---:|---:|---|
| 12 | ΔI = B10−B00 | +5.266 | [+4.531, +6.073] | 3.42×10⁻¹³ | Not equivalent |
| 12 | ΔC = B01−B00 | +0.553 | [−0.059, +1.164] | 0.184 | Equivalent |
| 12 | ΔIC = B11−B10−B01+B00 | −0.553 | [−1.157, +0.039] | 0.184 | Equivalent |
| 48 | ΔI = B10−B00 | +8.683 | [+8.282, +9.084] | 7.62×10⁻²⁷ | Not equivalent |
| 48 | ΔC = B01−B00 | +0.404 | [−0.012, +0.829] | 0.156 | Equivalent |
| 48 | ΔIC = B11−B10−B01+B00 | −0.404 | [−0.838, +0.016] | 0.156 | Equivalent |

ΔI is positive at both scales, its adjusted intervals exclude zero, and the
effect is outside the ±2 pp equivalence region. ΔC and ΔIC are each
equivalent to zero within ±2 pp under the prespecified TOST procedure. These
are effects of the specified interventions in the H2 synthetic simulator;
the external-label benefit is not adjusted for any unmodeled real-world cost
of acquiring those labels.

## Descriptive mechanism and cost diagnostics

These diagnostics describe the simulated trajectories and are not additional
confirmatory contrasts or causal mediation estimates.

| N | Condition | Success-on-time | Pair coverage* | Final posterior RMSE | Effective agents | Mean queue wait | Late among admitted | Rejects / arrivals |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 12 | B00 | 81.97% | 79.44% | 0.2240 | 11.17 | 0.554 | 4.93% | 2 / 79,330 |
| 12 | B10 | 87.24% | 100.00% | 0.0742 | 11.49 | 0.429 | 2.96% | 1 / 79,330 |
| 12 | B01 | 82.53% | 81.46% | 0.2230 | 11.16 | 0.549 | 4.89% | 0 / 79,330 |
| 12 | B11 | 87.24% | 100.00% | 0.0742 | 11.49 | 0.429 | 2.96% | 1 / 79,330 |
| 48 | B00 | 78.95% | 57.83% | 0.2447 | 39.44 | 0.775 | 7.68% | 0 / 317,069 |
| 48 | B10 | 87.63% | 100.00% | 0.0767 | 42.50 | 0.527 | 3.77% | 0 / 317,069 |
| 48 | B01 | 79.35% | 57.76% | 0.2441 | 39.70 | 0.769 | 7.45% | 0 / 317,069 |
| 48 | B11 | 87.63% | 100.00% | 0.0767 | 42.50 | 0.527 | 3.77% | 0 / 317,069 |

`*` Pair coverage means the proportion of agent×family cells with at least
one available observation, combining calibration and executed-task labels.
The final posterior RMSE compares Beta posterior means with the simulated
true competencies across all cells. B00/B01 online labels cover fewer pairs
at N=48 than N=12; calibration supplies 20 labels in every cell and therefore
makes B10/B11 coverage complete by construction.

Across all 30 seeds B10 and B11 selected exactly the same agents for every
task at each scale. The load filter did exclude some candidates, but did not
change selected agents when calibration was present. Consequently the
observed ΔIC is exactly `−ΔC`; this is a property of these trajectories, not
a general statement about the interventions. No empty-filter fallback was
triggered. Across B01 and B11, the filter removed 52,728 candidate-agent
instances at N=12 and 568,729 at N=48. There were four rejections total, all
at N=12.

External calibration required 960 observations per N=12 seed-scale and 3,840
per N=48 seed-scale; shared acquisitions across B10/B11 total 28,800 and
115,200 labels, respectively (144,000 total). Mean measured decision time
per replica was 0.075 s (B00/B10) and 0.156 s (B01/B11) at N=12; at N=48 it
was 1.096 s (B00/B10) and 1.895 s (B01/B11). The load-filter path includes
per-arrival diagnostic trace construction, so these timings include
instrumentation overhead and should not be read as a clean deployment-cost
estimate. Calibration cost is recorded as observation count; no monetary or
service-time conversion is defined.

## Reproducibility and limitations

The runner and frozen execution configuration are in
[`ce04_causal.py`](../../../src/hls/ce04_causal.py) and the execution
manifest. The 240-row
[`replica_metrics.csv`](../../../results/experiments/hls_ce04_causal_confirmatory/replica_metrics.csv)
and the machine-readable
[`analysis JSON`](../../../results/experiments/hls_ce04_causal_confirmatory/confirmatory_analysis.json)
are tracked. [`campaign_manifest.json`](../../../results/experiments/hls_ce04_causal_confirmatory/campaign_manifest.json)
records artifact digests, validation count, software provenance and unique
calibration costs. Runtime was 477.60 s wall-clock (249.99 s summed replica
CPU) on Python 3.11.9, NumPy 1.26.4, SciPy 1.13.1 and SimPy 4.1.2. The 306 MB
compressed task-level log is local-only, with
SHA-256 `9784916461f6adf47e3f723d93a4aeda5bbbf31656d92024fb52b6240a9d5b17`.

The findings apply to H2, these two organization sizes, this simulated
competence and demand process, and the specific synthetic external-calibration
mechanism. Three-seed pilot metrics were not pooled into confirmatory
inference. No conclusion is drawn about other compositions, acquisition costs
outside the model, or real organizations.
