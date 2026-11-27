# Uncertainty analysis

> **AVISO DE VERSIÓN HISTÓRICA:** este documento conserva el diseño, metodología o resultados de una versión anterior, en la que las alertas podían recibir servicio L1 antes de pasar a L2. No describe el modelo organizativo vigente ni debe reinterpretarse como evidencia de la ruta de investigación única tras triaje. Se conserva íntegro para reproducibilidad. Decisiones actuales y estado de implementación: [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

## Two uncertainty sources

### Simulation uncertainty

The new campaign has 400 new paired seed clusters. All classifier points use the same exogenous arrivals, class, severity, difficulty and hidden need per seed; recommendations use the same alert-keyed uniform variate and the published rates as cutpoints. Policies share the same recommendation outcomes within each seed. Repeated alpha and L2 roster conditions remain inside the seed block.

For each condition/policy, \(S_+\) is estimated as total timely true needs divided by total synthetic needs. Bootstrap replicates resample the same seed IDs for every policy and condition, sum integer numerators and denominators, then recompute each ratio and paired difference. A bootstrap resample with denominator zero is omitted from ratio quantiles and counted. The registered bootstrap is 10,000 paired seed-cluster percentile draws, RNG seed 711202611. Means for other episode outcomes use the same seed-index matrix. Intervals are exploratory Monte Carlo intervals, not confirmatory evidence.

### SOCTRA parameter uncertainty

The 72-point inventory records rounded pD/pFA/BA from article tables. It does not supply auditable model-specific confusion numerators, denominators and sampling covariance for all operating points. The independent standardized test has 19 positive and 14,430 negative historical labels, but the published operating-point table cannot be assumed to be a simple binomial evaluation on those same cases: for example, .7042 cannot be reconstructed as an integer fraction over 19 positives. A rounded value such as .0450 is compatible with multiple possible false-positive counts at denominator 14,430. It would be incorrect to invent counts or treat a coincidental rational match as provenance.

Accordingly, the analysis does not put confidence intervals around published pD/pFA and does not propagate such intervals into recommendations or load. The reported points are fixed empirical inputs. Results describe simulator variability conditional on those points. A separate inferential uncertainty layer for the empirical classifier rates remains unavailable from the audited aggregate files.

## Positive-case scarcity and effective information

With \(\pi=19/14,449\), the expected need count per 24 h seed is below one at the specified rate. In the old high-load 40-seed traces, 35 needs were observed and 16 seeds had none. Therefore, per-seed \(S_+\) values are frequently undefined and cannot be averaged after coding zero-positive seeds as zero. The pooled count ratio is used instead. Bootstrap resampling by seed preserves extra variation due to differing need counts, arrival counts and service outcomes.

The nominal precision calculation treats positive needs as independent Bernoulli observations and is only a planning approximation. The seed bootstrap is the inference used. It may still be unstable if a few seed blocks contain multiple needs or if outcome correlation within a seed is substantial. Actual positive counts, zero-positive seeds, bootstrap denominators and effective seed support are reported in outputs.

## Interpretation rules

- A 95% interval excluding zero is a descriptive exploratory contrast within a prespecified synthetic condition, not independent validation.
- Overlapping intervals are not evidence of equivalence.
- Pointwise condition intervals are not corrected for the many classifier × alpha × capacity × policy comparisons.
- No interval covers uncertainty about real SOC demand frequencies, analyst acceptance, false-positive verification times, or class-specific classifier errors.
- The labels used to set \(\pi\) are not adjudicated ground truth for required L2 work; need remains synthetic.
