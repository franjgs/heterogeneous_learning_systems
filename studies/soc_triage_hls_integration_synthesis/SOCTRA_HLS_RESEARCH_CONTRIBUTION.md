# Defensible research contribution

## Recommended contribution

The strongest defensible framing is **integrated evaluation of AI triage and human work organization under capacity and service-level constraints**. The contribution is a reproducible evaluation framework plus conditional evidence that classifier operating characteristics can alter the workload presented to heterogeneous L1/L2 teams, and that classifier-level trade-offs must be evaluated together with the organization expected to process the routed work.

This is narrower than claiming a novel general theory or a deployable joint controller. No dedicated literature review is provided here to establish novelty of the general idea.

## What is verifiable

1. **A linked accounting of classifier errors and downstream operations.** Published aggregate (p_D,p_{FA}\) values are translated into synthetic routed demand using explicit prevalence, then workload is evaluated in the frozen organization model with separate accounting for necessary recommended work (TP), unnecessary FP work, and omitted FN need. This is implemented and reproducible within the simulator assumptions.
2. **A multi-constraint feasibility formulation.** Detection, offered heterogeneous capacity, and correct/on-time service are distinct eligibility conditions. Saved outcomes make (S_+\) estimable as a pooled ratio and permit policy comparisons under paired seed-cluster bootstrap. This contribution is analytical/post hoc; the reverse organization-to-triage relation is not a live control.
3. **Evidence of conditional reordering and interaction.** In selected simulated settings, operational performance does not follow BA ordering, and classifier-by-policy differences vary by load/capacity. The evidence is exploratory and sensitive to prevalence, synthetic need, full-investigation FP cost, service map, and rare-positive counts.

## What the evidence does not verify

- It does not show that a specific SOCTRA model’s predictions on individual operational alerts cause the simulated load or outcomes; recommendations are generated synthetically from published aggregate rates.
- It does not validate the hidden need indicator as actual security need or treat historical escalation tags as adjudicated truth.
- It does not validate automatic recommendation acceptance, staffing, continuous availability, skills, service durations, deadlines, or incident mix at GMV-CERT.
- It does not show that WAPS is universally better, that it robustly moves the (S_+\) frontier, or that the maximum-BA classifier is operationally optimal.
- It does not establish a real-time system that changes the classifier in response to capacity or SLA state.
- It does not provide complete uncertainty for (p_D,p_{FA}\), prevalence, or external operating-condition frequencies; 40 seed clusters and scarce positives constrain the simulation intervals.

## Article framing decision

Use **A. Joint triage–organization evaluation** as the principal story. It is the direction actually implemented and experimented: classifier operating characteristics induce a synthetic routing stream, and fixed organization alternatives process it. Use **B. Constrained joint selection** as a formal interpretive layer and a secondary result: given a demand/capacity/SLA specification, which classifier-policy configurations are admissible under stated thresholds? Present it as a post hoc feasibility map, not as an adaptive classifier selector.

This order preserves the scientific object—the interaction of AI triage with human organization—rather than centering on a single classifier or WAPS. It also aligns claims with the asymmetry in evidence: downstream workload effects were simulated; reverse selection/control was not implemented.

## Evidence needed to strengthen the claim

The most consequential missing evidence is aligned individual predictions and independently adjudicated L2 need, joined to observed service/acceptance information. Aggregate operating points cannot reveal whether errors cluster in time, classes, severity, or long-duration tasks. Until such evidence exists, the article should describe the classifier inputs as empirical aggregate rates and the induced workload/outcomes as conditional simulations. No additional campaign is prescribed here.
