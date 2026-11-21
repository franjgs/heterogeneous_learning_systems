# Article-ready results summary

## Bounded claim

In a paired simulation using three published standardized-label SOCTRA operating points as fixed probability inputs, classifier-induced L2 workload and organizational policy jointly affected the proportion of synthetic L2 needs completed within deadline. Under elevated L1 demand, 2–4 L2 analysts, automatic recommendation acceptance, and illustrative false-positive service fractions α=.25–1.00, pooled (S_+) varied materially across D1, P1 and WAPS. Across the 36 prespecified cells, P1 and WAPS had higher point estimates than D1, while WAPS did not exceed P1 in any cell; these are exploratory pointwise results without multiplicity correction and conditional on the model.

## Mechanistic result

At the standardized test-label proxy prevalence π=19/14,449, the three fixed classifier points imply different expected recommendations per 1,000 alerts: 46.0 for LightGBM, 75.3 for LSEnsemble, and 16.3 for Bayesian MLP. Expected TP counts are 1.11, 1.11, and 0.93 per 1,000, respectively. Consequently, LSEnsemble's higher false-positive rate adds substantial workload without a detection gain over LightGBM at the reported operating points. Whether that extra work depresses timely service depends on the assumed duration of FP work and L2 capacity: the simulated operational ordering between LSEnsemble and MLP changed with α in a paired P1/two-L2 comparison.

## Uncertainty and limits

The primary (S_+) estimator pools integer timely-need counts over 474 synthetic needs in 400 paired seed clusters; 133 seeds had no need. Seed-cluster bootstrap intervals quantify simulator Monte Carlo uncertainty conditional on fixed published (p_D,p_{FA}). They omit uncertainty in published rates, prevalence transport, actual L2 need, analyst acceptance, task times, and scenario frequencies. No individual SOCTRA test predictions are used. Therefore results demonstrate a mechanism in a transparent simulation, not realized GMV-CERT outcomes or a validated classifier recommendation.

## Recommended wording for Results

“The simulation indicates that classifier operating points with similar detection can induce markedly different L2 workloads when their false-alarm rates differ. Under the modeled elevated-load condition, timely service of synthetic L2 needs depended on both the classifier-generated workload and the organizational policy. The observed sensitivity to the assumed duration of false-positive work shows that statistical operating-point metrics alone do not determine downstream service performance. These findings are conditional on synthetic need, automatic acceptance, and modeled service times; they do not establish the operational ranking of classifiers or policies in GMV-CERT.”

## Recommended wording for Discussion

“Our results support evaluating automated triage jointly with the human service system that receives its recommendations. In this model, more favorable detection or balanced-accuracy values did not uniquely determine timely operational service, because false-positive workload interacted with L2 capacity and policy. The findings motivate reporting detection, induced work, backlog, and need-specific SLA outcomes separately. They do not validate an online feedback controller from organizational state to classifier threshold, and the assumed effort associated with false alarms requires empirical calibration before external application.”

The complete tables, intervals, figures and reproduction artifacts are in [EXPERIMENTAL_RESULTS.md](EXPERIMENTAL_RESULTS.md) and `results/soc_triage_hls_q1_integration_evidence/`.
