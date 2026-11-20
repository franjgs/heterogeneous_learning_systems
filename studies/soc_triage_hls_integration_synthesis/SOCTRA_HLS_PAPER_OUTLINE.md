# Proposed article outline: SOCTRA–HLS integrated evaluation

This outline is limited to an article built from the evidence already available. It does not declare the manuscript complete or accepted, and it does not add experiments.

## Proposed central question

**How do aggregate escalation-triage operating characteristics interact with heterogeneous analyst organization under capacity and deadline constraints, and what can be identified about operational feasibility from the available simulation evidence?**

## Recommended structure

### 1. Introduction

- Describe the two coupled subsystems: AI recommendation generation and human/analyst workflow.
- Motivate why classifier-only statistics and organization-only outcomes may omit the load interface.
- State the limited aim: evaluate the implemented triage-to-organization path and characterize the post hoc feasibility constraints.
- Explicitly avoid claims of universal adaptation superiority or unreviewed novelty.

### 2. Background and evidence provenance

- Summarize SOCTRA’s published escalation operating points and distinctions between label definitions and cost regimes.
- Summarize HLS D1, P1, and WAPS, plus the confirmatory organizational evidence.
- Identify which classifier inputs are aggregate empirical operating points and which workload variables are synthetic.
- Provide branch/commit and source-data provenance in a reproducibility table.

### 3. Integrated model

- Define the arrival stream, prevalence/need variable, classifier operating point, positive recommendation, and class-specific workload.
- State (q=\pi p_D+(1-\pi)p_{FA}) and the class-aware offered-work calculation.
- Describe L1/L2 pools, eligibility, service-time model, deadlines, D1/P1/WAPS and automatic acceptance.
- Define outcomes separately: confusion counts, necessary-work service, (S_+\), global/routed SLA, backlog/utilization, modeled quality and legacy R/N.
- Define the post hoc feasible set in detection, capacity and service dimensions; make clear that it is not a real-time selector.

### 4. Experimental design and statistical analysis

- Separate the 10-seed development pilot, 40-seed phase-2 subsets, 18,720-row frontier campaign and feasibility reanalysis.
- Explain trace/common-random-number matching, compatible episode reuse, repeated seed IDs, denominators and multiplicity.
- Define paired contrasts and difference-in-differences; summarize uncertainty limitations.
- Describe pooled ratio-of-counts bootstrap for (S_+\), including zero-positive seeds and denominator handling.
- Do not pool records from separate label definitions or incompatible outcome estimands.

### 5. Results

1. Audit of 72 SOCTRA operating configurations and four separate statistical Pareto sets.
2. Analytic expected routing/load and heterogeneous capacity checks.
3. Simulated load, backlog, utilization, SLA, correct/on-time outcomes and operational trade-offs.
4. Classifier ordering versus BA and conditional classifier × organization contrasts.
5. Detection–capacity–service feasibility maps with point status and uncertainty.
6. Priority (S_+\) case, reported as sparse and exploratory.
7. Organizational confirmatory results in a clearly separate subsection or contextual comparison, using their own estimands.

### 6. Discussion

- Interpret how false-positive workload can offset gains in detection under low prevalence and constrained capacity.
- Explain that policy modifies timeliness but cannot create capacity or remedy an omitted false negative under the modeled routing logic.
- Discuss why (p_D,p_{FA}\), BA and Bayes benefit alone do not determine operational selection without a service objective and resource specification.
- Contrast evaluated downstream coupling with unimplemented reverse feasibility/control.
- State results that were negative or uncertain as part of the main findings.

### 7. Limitations and external validity

- Aggregate operating points, synthetic recommendation realizations, rare positives, and no individual classifier predictions.
- Synthetic hidden need, automatic acceptance, full L2 work for FP, hypothetical capacity/services/deadlines and continuous-staffing assumptions.
- No error stratification by project/class/severity and no empirical queue/service linkage.
- Bootstrap intervals conditional on fixed published rates and simulation assumptions; exploratory multiplicity.
- No claims about GMV-CERT operational behavior without validated data.

### 8. Conclusion

Conclude that triage rates and organization are coupled in the evaluated simulator and that operational admissibility is multi-constraint. State explicitly that the current evidence does not establish a real deployed classifier ranking, robust WAPS movement of the service frontier, or an operational closed-loop selector.

## Suggested primary figures and tables from existing evidence

- Diagram of the implemented one-way workload path plus the post hoc feasibility relation, with evidence-status labels.
- Table of source operating-point group, label definition, cost regime, (p_D,p_{FA},BA\), and frontier status.
- Load/FP-work projection alongside observed utilization/backlog (clearly separated as analytic versus simulated).
- Operational outcome and policy contrast figures at pre-existing reference strata, with paired uncertainty.
- Feasibility map using the existing threshold grid, separating point admissibility from lower-confidence support.
- Table of assumptions, provenance, and what each data source can/cannot establish.

The source reports contain the corresponding figures and data tables. This outline does not authorize reanalysis beyond the published files or assert that the eventual article has been finalized.
