# Scientific implications and final assessment

## What the simulation supports

In this explicitly synthetic model, restricting L2 from 24x7 to weekday 09:00–17:00 lowers deadline-based `S_plus` across the examined paired cells. At `rho_L1=0.85`, alpha 0.25, `n_L2=3`, D1, the decreases range from 0.110 to 0.134, with seed-block 95% intervals excluding zero. The change reflects the combined loss and timing of weekly capacity, not intermittency isolated from capacity.

The size of the calendar effect depends on classifier, alpha, L1 load and L2 team size. False-positive induced service cost is especially consequential under 8x5 for LightGBM and LSEnsemble in the displayed cells; at alpha 0.25 versus 1.0 their paired `S_plus` differences are 0.077 (95% CI 0.066–0.089) and 0.335 (0.316–0.353), respectively. Bayesian MLP's corresponding difference is 0.003 (0.0005–0.0055). At 24x7 these selected contrasts were zero because the tasks relevant to the endpoint met their deadlines despite the modeled FP workload.

Classifier-by-calendar interaction estimates vary across settings. The classifier ordering is not fully invariant: LightGBM and LSEnsemble tie in some 24x7 cells, while their 8x5 outcomes differ slightly; Bayesian MLP is lower in the main cells. In contrast, D1/P1/WAPS differences are very small in this campaign. WAPS had zero switches to its P1 regime, and P1-D1 contrasts were near zero, so the experiment does not provide a useful test of policy separation. This is a limitation of the selected synthetic workload and dispatch opportunities, not evidence of general policy equivalence.

Increasing `rho_L1` to 1.25 generally increases the negative calendar contrast. This suggests a load interaction in the model, but absolute estimates remain scenario-dependent. The confidence intervals quantify variation across paired random seed blocks under the fixed generators; they do not capture uncertainty in model structure or real SOC parameters.

## Interpretation limits

`S_plus` means a synthetic L2 need was recommended positively and the resulting L2 task finished before its synthetic deadline. Completion is not incident resolution. The assumptions include SOCTRA recommendations accepted systematically, synthetic ground truth and service times, no leave or handover, persistent task ownership during suspension, and fixed calendars. The weekday calendar and 12/24/72-hour deadlines are not GMV-CERT operational facts or service commitments.

The campaign is valid for comparing the coded scenarios after the paired regression and calendar invariants, but not for estimating a real SOC's staffing, SLA attainment or classifier value. The complete seed-block intervals and episode outputs are retained; the report does not treat 86,400 episodes as independent samples.

## Recommendation for the article

Do not modify the manuscript in this task. The study is suitable as a follow-on robustness result or a short limitations discussion only after joint scientific review. The structural conclusion—that deadlines depend materially on when specialist capacity is available—is clear within this model. The classifier × alpha interactions are also large in selected 8x5 cells. Policy comparisons are inconclusive because D1/P1/WAPS are barely separated in this design. Before incorporating strong comparative claims, a targeted follow-up should ensure nonzero policy switching and meaningful L2 contention under a prespecified synthetic workload, then repeat the same paired method. Do not add scenarios solely to obtain significance.
