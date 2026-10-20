# Minimal proposal: learning instructor–learner–skill efficacy

**State:** proposed documentary design only. Not preregistered, not implemented, and not run. No new HLS mechanism or experiment is authorized by this proposal.

## Falsifiable question

Under which combinations of future-demand uncertainty and relation-specific teaching heterogeneity does updating estimates of teaching efficacy improve held-out cumulative functional production, relative to an otherwise identical prospective planner using fixed efficacy estimates, under the same production/training resource budget?

This does not ask whether teaching is beneficial in general. It asks whether observations about an unknown teaching relation improve subsequent allocation decisions enough to justify the opportunity cost paid to acquire those observations.

## Hypothesis and null

- **Null (H_0):** with the same initial efficacy prior, optimizer, information about demand, action set, horizon, resource budget, and paired scenario/noise streams, online efficacy updating does not improve mean held-out functional production over fixed efficacy estimates.
- **Alternative (H_1):** the paired held-out difference is positive in preregistered conditions where (i) efficacy varies across instructor–learner–skill triples, (ii) training outcomes are sufficiently informative, and (iii) future demand makes the resulting competence changes productive.

The alternative is conditional, not universal. Report conditions where learning has no value or costs more training opportunity than it recovers. Do not select conditions after viewing policy outcomes.

## Minimum scenario family

Use the existing three-expert, two-skill production scale as the initial reference only if its functional output and effort budget support a distinct training allocation without changing the meaning of the legacy action catalogue. Define a small synthetic set of demand contexts with:

1. **Repeated demand:** a skill/context recurs after a train/evaluate boundary.
2. **Demand shift:** the dominant skill changes after training.
3. **Negative control:** all teaching relations have equal efficacy, or the target skill does not recur, so efficacy learning cannot improve held-out allocation value.

The first two conditions distinguish potential information value from mere training benefit; the negative control checks for spurious “learning” gains. Do not call a label-table policy transfer to unseen contexts. Any context key used for learning must be stated explicitly.

Before comparing policies, enumerate feasible production and teaching actions to select instances that include feasible, resource-constrained, and infeasible work requirements. Selection criteria must use the physical model and action feasibility only, never policy outcomes. Keep aggregate initial capability and common resource budget fixed across compared teams, or treat team composition as a separate blocked factor.

## Minimal comparison

Primary comparison:

- **P2 fixed efficacy:** prospective production/training planner with frozen prior-mean efficacy values.
- **P3 online efficacy:** same planner, horizon, feasible actions, information, initial prior, compute/time limit, and tie-breaking; only efficacy posterior updates differ.

Secondary diagnostics: P1 no teaching, an oracle with privileged true efficacy, and exact small-instance optimization. P1 is not the causal control for efficacy learning because it also removes teaching. Oracle is a bound/reference only. Do not compare a computationally stronger P3 to a weaker P2.

Use separate TRAIN and EVAL scenario instances/seeds. Both P2 and P3 receive identical training opportunities and exogenous streams; P2 logs outcomes but its decision rule does not update efficacy estimates. Freeze both states at the boundary and evaluate on paired held-out histories. If the fixed arm continues to consume training actions by its declared policy, preserve and account for that behavior rather than retrospectively replacing it.

## Primary outcome and uncertainty

Primary outcome: cumulative functional production during EVAL, in the existing model's output units. Paired unit: independently seeded scenario history (not decision rows or Monte Carlo branches). Report the paired P3−P2 mean and history-level interval, plus each arm's absolute outcome. Also report functional success/deficit, production-phase effort, teaching effort, total resource use, learned competence, and calibration/error of efficacy beliefs separately. No composite net utility is defined until production and resource units have a defensible common conversion.

Randomize/replicate the latent efficacy map and demand/noise streams only if those are explicit model random variables; otherwise label the enumeration as structural sensitivity, not stochastic replication. Pair policies on the same generated maps and streams, but let each policy's own actions produce its own observations and endogenous competence path.

## Sources of uncertainty and validity controls

- demand sequence / transition uncertainty;
- observation noise and whether it identifies efficacy separately from baseline skill;
- initial competence and efficacy priors;
- optimizer error or unequal compute limits;
- finite evaluation histories and shared team/map clusters;
- teaching-versus-work exposure confounding;
- functional threshold saturation or infeasibility;
- model misspecification in the efficacy transition.

The model must first show that efficacy is identifiable under the proposed observation design. If identical observations can arise from different combinations of learner baseline, individual learning-by-doing, and teacher efficacy, the primary claim is not testable in that design. Stop rather than hide this behind a posterior mean.

## Success and abandonment criteria

Proceed to implementation only after bibliography review confirms a defensible distinction from prior integrated staffing/training and knowledge-transfer models, and after the CE approves a mathematically coherent training transition and observation likelihood.

The experiment is informative if the preregistered P2/P3 contrast is valid, the negative control behaves as predicted, the model's efficacy parameter is identifiable, and results are reproducible. A positive P3−P2 estimate is not required for scientific success. Abandon or redesign before execution if (a) the training observation cannot separate efficacy from other learning, (b) the resource accounting gives teaching free capacity, (c) P2 and P3 do not have equivalent planners, or (d) existing prior art already contains the proposed unknown-relation adaptive decision problem in materially equivalent form.

## Pre-execution blockers

1. Full-text review remains incomplete for Baccara et al. (2023), Borgonjon & Maenhout (2024), Chen et al. (2017, 2018), Valeva et al. (2017), and Su et al. (2025). The register states exact access status; abstract-only evidence is not a basis for a novelty claim.
2. The current HLS lab has no teacher–learner action, relation-specific efficacy state, or training outcome model. This proposal does not fill those gaps.
3. A common production/resource objective and a teaching-time budget contract must be approved before any implementation.
4. The current model must specify whether a training relation is directed and whether efficacy depends on instructor, learner, and skill separately. This is a scientific design choice, not an implementation default.

**Recommendation:** REDESIGN / HOLD before implementation. Continue with complete-paper review and CE approval of the estimand and observation model. Do not describe the residual question as novel until that review and a broader targeted search are complete.
