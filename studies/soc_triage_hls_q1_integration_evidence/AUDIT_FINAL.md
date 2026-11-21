# Final audit — SOCTRA–HLS Q1 integration evidence

## 1. Scope, source state and disposition

This audit reads the saved 43,200-row episode file and saved trace audit. It does not run the simulator or alter SOCTRA, D1, P1, WAPS, historical campaigns, or the generated episodes. The analysis branch is `research/soctra-hls-q1-integration-evidence`, based on `cc0880d8f56cb3aa05ff29f55f493441ec01206a`.

The new reproducible reanalysis is `studies/soc_triage_hls_q1_integration_evidence/audit_saved_campaign.py`. It writes `audit_checks.json`, `audit_need_distribution.csv`, and `audit_interaction_contrasts.csv` alongside the existing result files. All three outputs derive only from saved episodes and trace hashes.

## 2. Statistical units and sparse need outcomes

There are 400 distinct seed IDs, 711000000–711000399. Each seed is one independent simulation block under the pseudorandom generator. Every seed contributes 108 rows: 3 classifier points × 4 alpha assumptions × 3 L2 roster sizes × 3 policies. Therefore, 43,200 is the number of condition records, not independent replications. Outcomes within each seed share arrivals, classes, deadlines, severity, difficulty, synthetic need and (where configured) common random numbers. Inference must resample the complete seed block.

The trace audit contains 1,200 rows because the same 400 base traces are recorded once per classifier point. Deduplicating by seed gives 474 unique synthetic L2 needs. They are distributed as follows:

| Needs in a seed | Seed blocks |
|---:|---:|
| 0 | 133 |
| 1 | 136 |
| 2 | 81 |
| 3 | 30 |
| 4 | 15 |
| 5 | 4 |
| 6 | 1 |

Thus positive needs occur in 267 seed blocks. Neither 474 duplicated classifier labels nor the 43,200 rows may be treated as independent positives. The 267 positive-bearing blocks are the support for need outcomes; the independent simulation unit remains all 400 seed blocks. No alert-level cluster-robust effective sample size beyond this seed-block structure is estimated.

## 3. Trace, confusion-count and condition pairing

The audit verified the complete Cartesian product: 3 classifier IDs, 4 alpha values, 3 L2 team sizes, 3 policies and 400 seeds; there are no duplicate factor rows and no missing cells. Admitted alerts per seed range from 759 to 939.

For each seed, the exogenous trace hash is identical across all three classifier points; the saved trace audit also records equal alert and synthetic-need counts. Within each classifier/seed, the episode CSV repeats the same trace hash, recommendation/confusion counts and L1 assignments across all alpha, L2-roster and policy conditions. Every row satisfies:

- (TP+FN=\text{true\_need\_count}), including all need cases as the denominator;
- (TP+FP+FN+TN=\text{admitted});
- timely-need numerator ≤ TP;
- `S_plus_denominator` = all synthetic needs.

The generator applies one alert-keyed uniform variate to each matched trace and compares it with each classifier point's published conditional rate. As a result, common random numbers couple recommendations across operating points; they do not make their outcomes identical. The recommendation and confusion counts are fixed across policy/alpha/roster for a given classifier and seed. This exact coupling is verified from the saved trace hashes and the generation code in `studies/soc_triage_organization_coupling/run_pilot.py` (`_stable_uniform`, `_make_trace`); alert-level raw identifiers are not needed in the published output.

All simulated deadlines mature before the terminal cutoff at 60 h. The saved check file records this as PASS. These checks establish internal pairing and denominator consistency, not external validity.

## 4. Hidden-label use in the alpha implementation

The experiment-only loop is `fp_workload_engine.py`; the caller is `run_primary_campaign.py`.

1. The caller creates the L2 arrival list from positive recommendations after L1 completion. It creates an environment-only hidden-need mapping and realized duration scale: 1 for a need/TP, alpha for a non-need/FP.
2. The L2 event loop's dispatch callbacks receive free analysts, pending alert metadata, current time, an ex-ante service forecast and a D1 random order generator where relevant. They do not receive `need_by_id` or `realized_scale_by_id`.
3. Forecast service is calculated from published (p_D,p_{FA}), the declared synthetic prevalence, class and alpha. WAPS capacity is calculated from expected class/service mixture, not realized hidden statuses.
4. Hidden status affects the environment's realized completion time only. That completion event can affect subsequent dispatch after it occurs; this is causal event information, not advance disclosure.

This supports the conclusion that a dispatcher does not directly use the hidden TP/FP/need label before choosing a task. It does **not** validate the aggregate-duration approximation as a human verification process: there is no explicit verification stage, observation of a verification result, or independently calibrated false-alarm handling time. The alpha values are hypothetical sensitivity parameters.

The deterministic alpha=1 equivalence tests passed for D1, P1 and WAPS against the frozen engine fixture. This checks the experiment-only event loop's baseline dispatch behavior; it does not prove all dynamic details equivalent in every possible state.

## 5. Metric definitions — three different outcomes

### 5.1 Timely attention to a true L2 need: (S_+)

The primary endpoint is

\[
\widehat S_+=\frac{\sum_s N_{s,\,Y=1,\,recommend=1,\,L2\ complete\le deadline}}{\sum_s N_{s,\,Y=1}}.
\]

The numerator requires a synthetic need, a positive recommendation and an L2 completion by both the individual deadline and terminal cutoff. The denominator includes false negatives and all other synthetic needs. This is **correct routing and timely attention** conditional on synthetic need. It is not a verified-correct investigative finding.

The estimate is count-pooled across seeds, not an average of per-seed rates. A zero-need seed is undefined for a per-seed conditional rate; it is never coded as a zero success. In the paired bootstrap, the same seed indices are used for every cell and both numerator and denominator are re-summed. No bootstrap replicate had zero denominator.

### 5.2 Correct resolution of an investigation

The experiment does not observe whether the analyst reached the substantively correct investigative conclusion. There is no outcome truth or adjudicated investigation-quality label in the simulated L2 task. `necessary_quality_timely_per_admitted` is a modeled continuous proxy based on analyst competence and alert difficulty for timely routed true needs. It is neither an observed accuracy rate nor the probability of a correct investigation. The label `necessary_correct_timely_per_admitted` means a true need was correctly routed and completed on time, normalized by admitted alerts; its “correct” refers to routing, not investigative conclusion.

Therefore, “correct resolution of investigation” is not estimable from this campaign. Any article text that treats the competence/difficulty proxy as verified resolution correctness requires correction.

### 5.3 Global correct and punctual resolution

`routed_task_SLA_terminal` is the proportion of all admitted alerts whose physical route (L1 alone or L1 then L2) completed by its deadline. It is a global **timeliness** measure, not global correctness: a false-positive route or a false-negative L1 completion can count as timely. No global correct-and-punctual binary outcome is available because the final correctness of non-need handling and L2 investigations is not modeled. Historical `correct_on_time_expected_per_admitted` fields also have route-qualified semantics and must not be presented as verified global correctness.

Keep the following terms separate in manuscripts and tables: detection (p_D), (S_+), routed-task SLA, and quality proxy.

## 6. Reconstructed interaction contrasts

For classifier pair (A,B) and policy pair (P,Q), the audit computes exactly the requested contrast:

\[
I_{A,B;P,Q}=[S_+(A,P)-S_+(B,P)]-[S_+(A,Q)-S_+(B,Q)].
\]

The 108 contrasts cover 3 classifier pairs × 3 unordered policy pairs × 4 alpha values × 3 L2 team sizes. The direction is explicit in the output columns `classifier_A`, `classifier_B`, `policy_P`, `policy_Q`. Each bootstrap replicate resamples the same 400 seed IDs for every classifier, policy, alpha and roster, then recomputes pooled (S_+) before forming the interaction. There are 10,000 percentile bootstrap replicates, seed 711202611.

Across all 108 contrasts, 46 unadjusted pointwise percentile intervals exclude zero (41 positive, 5 negative); 62 include zero. Since the family is large and exploratory, the script also reports one-step familywise intervals from a paired max-|z| bootstrap over all 108 contrasts (critical value 3.4508). Only 9/108 familywise intervals exclude zero: seven at alpha=.25 and two at alpha=.50; none at alpha=.75 or 1.00. Those nine are all classifier comparisons against Bayesian MLP, with P1 or WAPS relative to D1. This pattern is suggestive that the classifier contrast under D1 differs from that under a more deadline-oriented organization when FP work is short. It is not confirmatory: the familywise procedure is still conditional on this selected simulation design and fixed classifier rates, and there is no independent validation sample.

### Illustrative interaction sensitivity by alpha

At (n_{L2}=3), comparing LightGBM (A) with Bayesian MLP (B), and P1 (P) with D1 (Q):

| alpha | Interaction | Pointwise 95% bootstrap CI | Familywise 95% max-|z| CI |
|---:|---:|---:|---:|
| .25 | +.05696 | [.03720, .07957] | [.01970, .09423] |
| .50 | +.04008 | [.02170, .06040] | [.00545, .07472] |
| .75 | +.03797 | [.01578, .06114] | [−.00205, .07800] |
| 1.00 | +.03797 | [.01735, .06054] | [−.00029, .07624] |

At the same roster/policy pair, LightGBM versus LSEnsemble interaction point estimates are +.00844, +.00422, +.01055 and +.00844 across increasing alpha; all their pointwise intervals include zero and all max-|z| intervals include zero. Across the full family, mean absolute point interaction by alpha is .02391, .02047, .01766 and .02000, respectively. These summaries show sensitivity but no monotonic alpha law.

The prior file `classifier_organization_interactions.csv` answers a narrower contrast: it reports the change in WAPS−D1 organization benefit between classifier B and A, i.e. \([S(B,WAPS)-S(B,D1)]-[S(A,WAPS)-S(A,D1)]\). That is the negative of the audited requested formula when (P=WAPS,Q=D1), (A,B) retain the same order. It is not a data error; its label and orientation differ. Use `audit_interaction_contrasts.csv` for the formula specified in this audit. Preserve the earlier file unchanged.

## 7. Multiple comparisons and uncertainty

- Existing policy contrasts report 36 unadjusted intervals per contrast family. Their consistency is descriptive; pointwise 95% coverage does not provide familywise error control.
- The newly computed 108 interactions include both unadjusted percentile CIs and the stated max-|z| familywise intervals. The latter reduce 46 apparent pointwise exclusions to 9 familywise exclusions.
- The classifier operating rates (p_D,p_{FA}) are fixed at rounded published values in this campaign. Model-specific source confusion numerators/denominators and sampling covariance sufficient to estimate empirical rate intervals were not available in the audited artifact set. It is not valid to infer these counts from rounded rates. Thus bootstrap intervals quantify simulator variation conditional on those rates; they do not include SOCTRA estimation uncertainty.
- For a Monte Carlo diagnostic only, the synthetic recommendation generator realized LightGBM TP 408/474=.8608 and FP 15,139/340,461=.04447; LSEnsemble TP 408/474=.8608 and FP 25,147/340,461=.07386; MLP TP 344/474=.7257 and FP 5,272/340,461=.01548. These finite synthetic outcomes are compatible with generator randomness and must not replace or revise the published (p_D,p_{FA}).
- The seed bootstrap accounts for variation across generated traces and all matched outcomes within a trace. It cannot quantify uncertainty in prevalence transport, true technical need, staffing, service times, alpha, acceptance behavior, scenario distribution, or real SOC operations.

## 8. Possible errors and corrections

### Confirmed interpretive corrections

1. Do not call `routed_task_SLA_terminal`, `necessary_quality_timely_per_admitted`, or historical route-qualified quality fields “correct global resolution.” Use their definitions above.
2. Do not interpret 43,200 records or 474 repeated classifier-labelled needs as independent observations. The resampling unit is seed; there are 400 blocks, including 267 with at least one need.
3. Do not quote the prior WAPS−D1 interaction file as the requested classifier-by-policy contrast without reversing its orientation. The new audit output states the formula directly.
4. Do not describe the 108 unadjusted interaction CIs as confirmatory. Prefer the max-|z| familywise intervals and retain the exploratory qualifier.
5. Do not add empirical confidence intervals to published (p_D,p_{FA}) without source denominators and counts. Keep the operating points fixed and explicitly state this uncertainty gap.

No inconsistency was found in episode cardinality, confusion accounting, trace pairing, terminal deadline maturation, or the hidden-label dispatch boundary. No saved simulation result was altered; all audit outputs are separate reanalyses.

## 9. Defensible conclusions and unproven claims

**Supported within this simulation:** classifier operating points induce different L2 recommendation/work burdens; timely service of synthetic need is a joint function of those burdens, the assumed FP duration, L2 roster and D1/P1/WAPS organization. Several classifier-by-policy interactions are visible in pointwise analyses; a smaller subset survives the specified max-|z| exploratory correction, particularly at alpha .25–.50.

**Not established:** that any classifier or organization is best for GMV-CERT; that the quality proxy equals correct investigation; that WAPS improves over P1; that false alarms take the modeled fraction of a full investigation; that the selected standardized label prevalence is the operational prevalence of objectively necessary L2 work; or that an online feedback controller from organizational state to SOCTRA operating point is effective.

The evidence remains simulation-based, uses synthetic need and automatic recommendation acceptance, and has only three operating points under one elevated L1 demand for the alpha campaign. The results can support a carefully bounded mechanistic article claim, not a deployment claim or a validated joint decision rule.

## 10. Reproduction and artifacts

From repository root, with the saved result directory present:

```bash
python studies/soc_triage_hls_q1_integration_evidence/audit_saved_campaign.py
```

This reads, and does not regenerate, `episodes.csv`. Output files:

- `results/soc_triage_hls_q1_integration_evidence/audit_checks.json`
- `results/soc_triage_hls_q1_integration_evidence/audit_need_distribution.csv`
- `results/soc_triage_hls_q1_integration_evidence/audit_interaction_contrasts.csv`

The full episode CSV, configuration, scripts, reports, existing summaries and figures are retained. SHA-256 hashes are refreshed in `results/soc_triage_hls_q1_integration_evidence/file_manifest.json` after the audit artifacts are finalized. The result files are synthetic and contain no source SOCTRA or GMV records.
