# META-VOC confirmatory evaluation — C3-META-VOC-CONF-v1

Status: **completed; CONFIRMATORY EVIDENCE FAVORABLE under the frozen joint rule**. The [pre-execution protocol](CAMPAIGN_3_META_VOC_CONFIRMATORY_PROTOCOL.md) and [machine freeze](../../results/foundations/campaign3_meta_voc_confirmatory/pre_execution_manifest.json) preceded generation of all confirmatory histories. The 50% point was designated primary *after* reviewing development results, not as a fully prospective hypothesis. No fitted model, threshold, operator, physics, split or development artifact was changed for this evaluation.

## Integrity and experimental scope

The four frozen domain sizes were G1=420, G2=200, G3=168 and G4=80, with one new exogenous history per team × kernel cell. All **868** histories completed under all eight policies: **6,944** independent policy trajectories and **249,984** decision records (36 per trajectory). The 55 checkpoint batches validated; the consolidated raw files and all 12 derived artifacts match their SHA-256 manifests. There were no planned exclusions, interrupted/resumed batches or validation failures. No history identifier or numerical exogenous seed overlapped the available development/Gate/PGCG records at the pre-execution check.

The policies were FAST, DEEP, META-VOC-{25,50,75} and RANDOM-{25,50,75}. Terminal decisions always used FAST. Within each matched history they received identical physical problems and standard-normal observation innovations, while capabilities, beliefs, assignments and visited states evolved separately. RANDOM used frozen independent Bernoulli priorities at nominal probabilities .25/.50/.75, **not** retrospective META call-count matching. All measurements below use cumulative physical `mu_true`; compute seconds are uncached wall-time measurements around chosen decisions, including META selector inference but excluding simulation and I/O.

## Primary paired comparison: META-VOC-50 minus RANDOM-50

The primary estimand weights the four domain-specific means equally. Two thousand domain-stratified, paired whole-history bootstrap resamples (seed `20261016`) give percentile 95% intervals.

| Outcome per history | Equal-domain mean difference | 95% interval |
|---|---:|---:|
| Cumulative `mu_true` | **+0.1167** | **[+0.0310, +0.2013]** |
| Measured decision-computation seconds | **−0.1924 s** | **[−0.3539, −0.0228] s** |

Both intervals satisfy the frozen favorable rule: the production interval is entirely positive and the computation interval is entirely negative. This is evidence for the **joint measured performance–cost contrast in this fixed HLS design**, not an equivalence claim or a universal advantage. The corresponding equal-domain absolute means are META-VOC-50 `54.1445 mu_true / 2.5660 s` and RANDOM-50 `54.0278 mu_true / 2.7584 s` per history.

Importantly, the realized budgets are **not exactly matched**. Across all 20,832 nonterminal decision slots, META-VOC-50 invoked DEEP 10,062 times (48.30% pooled), versus RANDOM-50 10,408 times (49.80% pooled). Equal-domain averaged invocation rates are 46.43% and 49.80%, respectively. This invocation difference can contribute to the computation contrast; the result does not isolate a pure efficiency effect at an exactly fixed call count. It tests the two frozen routing rules at their prespecified operating point and nominal RANDOM probability.

## Frozen generalization domains

| Domain | Histories | Δ production | 95% interval | Δ computation, s | 95% interval, s |
|---|---:|---:|---:|---:|---:|
| G1: development teams × kernels, fresh histories | 420 | +0.2053 | [+0.0712, +0.3394] | +0.0354 | [−0.1576, +0.2345] |
| G2: development teams × held-out kernels | 200 | +0.3101 | [+0.1158, +0.5030] | −0.0038 | [−0.2836, +0.2912] |
| G3: held-out teams × development kernels | 168 | −0.0267 | [−0.1643, +0.1015] | −0.4461 | [−0.7695, −0.1394] |
| G4: held-out teams × held-out kernels | 80 | −0.0218 | [−0.2372, +0.1968] | −0.3552 | [−0.8217, +0.1027] |

The performance contrast is positive with intervals excluding zero in G1/G2 but not G3/G4. Thus the favorable equal-domain aggregate **does not demonstrate a production advantage on held-out team geometries**. G3/G4 have lower META invocation rates than their RANDOM counterparts; no team-geometry mechanism is inferred from this descriptive contrast. G4 has only 80 independent histories and wide intervals.

## All operating points and baselines

The fixed secondary META-VOC minus RANDOM contrasts, with equal-domain weighting globally, are:

| Point | Domain | Δ production [95% interval] | Δ computation, s [95% interval] |
|---:|---|---|---|
| 25 | Global | +0.0448 [−0.0437, +0.1388] | −0.1865 [−0.2983, −0.0684] |
| 25 | G1 | +0.1717 [−0.0003, +0.3481] | +0.0251 [−0.1495, +0.1988] |
| 25 | G2 | +0.2424 [−0.0182, +0.5238] | +0.0505 [−0.1798, +0.2927] |
| 25 | G3 | −0.1197 [−0.2553, +0.0023] | −0.4214 [−0.6229, −0.2005] |
| 25 | G4 | −0.1152 [−0.2233, −0.0012] | −0.4004 [−0.6860, −0.1114] |
| 50 | Global | +0.1167 [+0.0310, +0.2013] | −0.1924 [−0.3539, −0.0228] |
| 50 | G1 | +0.2053 [+0.0712, +0.3394] | +0.0354 [−0.1576, +0.2345] |
| 50 | G2 | +0.3101 [+0.1158, +0.5030] | −0.0038 [−0.2836, +0.2912] |
| 50 | G3 | −0.0267 [−0.1643, +0.1015] | −0.4461 [−0.7695, −0.1394] |
| 50 | G4 | −0.0218 [−0.2372, +0.1968] | −0.3552 [−0.8217, +0.1027] |
| 75 | Global | +0.0310 [−0.0297, +0.0942] | −0.2361 [−0.3878, −0.0872] |
| 75 | G1 | +0.1369 [+0.0487, +0.2297] | +0.0368 [−0.1241, +0.1953] |
| 75 | G2 | +0.0404 [−0.0744, +0.1539] | −0.0717 [−0.2954, +0.1610] |
| 75 | G3 | −0.0801 [−0.2152, +0.0532] | −0.4973 [−0.8165, −0.1884] |
| 75 | G4 | +0.0270 [−0.1212, +0.1703] | −0.4121 [−0.8680, +0.0259] |

Neither secondary global production interval excludes zero. The G4 25% production interval is negative; this negative result is retained. The complete machine-readable [paired comparisons](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/paired_comparisons.csv) additionally include all fixed META-VOC-versus-FAST and META-VOC-versus-DEEP contrasts. Equal-domain META-VOC-50 exceeds FAST by `+0.9535 mu_true` [0.8230, 1.0871] while using `+2.5516 s` [2.3922, 2.7105]; it trails DEEP by `−0.3863 mu_true` [−0.4863, −0.2916] while using `−3.0126 s` [−3.1713, −2.8531]. These are performance–cost trade-offs, not policy equivalence.

| Policy | Equal-domain mean cumulative `mu_true` | Mean measured s/history | Pooled DEEP calls / 20,832 | Equal-domain DEEP rate | Mean selector s/history |
|---|---:|---:|---:|---:|---:|
| FAST | 53.1911 | 0.0143 | 0 | 0% | 0 |
| DEEP | 54.5308 | 5.5785 | 20,832 | 100% | 0 |
| META-VOC-25 | 53.6839 | 1.1831 | 4,801 | 21.27% | 0.000598 |
| RANDOM-25 | 53.6391 | 1.3696 | 5,114 | 24.50% | 0 |
| META-VOC-50 | 54.1445 | 2.5660 | 10,062 | 46.43% | 0.000766 |
| RANDOM-50 | 54.0278 | 2.7584 | 10,408 | 49.80% | 0 |
| META-VOC-75 | 54.3427 | 3.8584 | 15,066 | 70.53% | 0.000968 |
| RANDOM-75 | 54.3117 | 4.0945 | 15,551 | 74.79% | 0 |

The invocation-rate column is an equal-domain mean; the call-count column pools all histories, so its numerator divided by 20,832 need not equal that displayed rate. Selector overhead is included in META's measured computation totals. Full domain-specific means, invocation frequencies and decision-latency mean/median/Q25/Q75/Q90/Q95/Q99 are in [policy_summary.csv](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/policy_summary.csv) and [performance_cost_curve.csv](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/performance_cost_curve.csv). In the equal-domain summary, median decision latency is approximately 0.414 ms for META-VOC-50 and 0.398 ms for RANDOM-50; their Q95 latencies are 233.34 ms and 234.39 ms, respectively. Timing is machine- and load-sensitive, and the bootstrap intervals here characterize the paired histories, not repeated hardware runs.

## Figures and scientific interpretation

- [Figure 1: routing architecture (SVG)](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure1_architecture.svg) / [PDF](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure1_architecture.pdf)
- [Figure 2: performance against measured computation (SVG)](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure2_performance_cost.svg) / [PDF](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure2_performance_cost.pdf)
- [Figure 3: domain-specific primary production differences and intervals (SVG)](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure3_primary_domain_effects.svg) / [PDF](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure3_primary_domain_effects.pdf)
- [Figure 4: realized DEEP invocation by domain (SVG)](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure4_invocation_rates.svg) / [PDF](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure4_invocation_rates.pdf)

The predefined verdict is **CONFIRMATORY EVIDENCE FAVORABLE** for this joint global comparison. It does not imply an exactly frequency-matched computational budget, advantage in every domain, or an optimal adaptive computation policy. The frozen Ridge target is a C3.2 single-rollout Q11−Q00 proxy under Q11 continuation, not the true recursively adaptive sequential benefit. One stochastic history per cell and the finite HLS team/kernel families limit generalization. The post-development choice of 50% as primary limits the strength of a conventional prospectively selected confirmatory claim. No production-to-computation conversion, new effect threshold, retrospective subgroup selection or recalibration was used.

## Provenance and reproduction

The [freeze manifest](../../results/foundations/campaign3_meta_voc_confirmatory/pre_execution_manifest.json) records all frozen source, model, calibration, split, protocol, feature, cost and threshold hashes, plus exact history and RANDOM-priority allocations. Its SHA-256 is `782c84f1cd454dc121ef5f6ff4f83d28565d6edd98f00bff1350032e55bce335`; planned-history CSV SHA-256 is `fc1837fcf23ce0b49d576c54447a9e77289e59bae41e3b7b5786664b64ade93f`, and priority-schedule SHA-256 is `d15970cb992473f80ef97c934c93915731930bfa9b35baa2f9cbb078a7b9140c`. Raw [runs](../../results/campaigns/campaign3_meta_voc_confirmatory/runs.csv.gz) and [trajectories](../../results/campaigns/campaign3_meta_voc_confirmatory/trajectories.csv.gz) have SHA-256 `3c2d7310a510deed03264b9a6df30ffc09a0af5915cc76dba233d29eadfd9e28` and `b4022b7a76c2aece607138d6d740ae854517fa171e889d09c557350c8da2e498`. All derived hashes appear in the [analysis manifest](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis_manifest.json). The [execution record](../../results/campaigns/campaign3_meta_voc_confirmatory/execution_progress.json) documents 8 workers and 2,719.5 s elapsed on macOS arm64, Python 3.11.9, NumPy 1.26.4 and pandas 2.2.3. Analysis used matplotlib 3.9.2.

The exact frozen seed for each history is stored in [planned_histories.csv](../../results/foundations/campaign3_meta_voc_confirmatory/planned_histories.csv), derived from `campaign3_meta_voc_confirmatory_v1:domain:team:kernel:0`; independent RANDOM priorities are in [random_invocation_schedule.csv](../../results/foundations/campaign3_meta_voc_confirmatory/random_invocation_schedule.csv). On a clean environment, run the four commands in the protocol in order. The freeze and analysis commands refuse silent replacement of existing artifacts. Existing frozen development outcomes are not included in this confirmatory bootstrap.
