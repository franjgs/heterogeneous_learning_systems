# HLS Scientific Checkpoint after B5

Status: current scientific checkpoint, 2026-09-26. This document closes the PACS B2.1--B5 sequence and is the required entry point for subsequent work with [RESEARCH_DOCTRINE.md](../../RESEARCH_DOCTRINE.md). It does not alter RQ0, the ontology, theory, frozen protocols, or historical results.

## 1. Research question and scientific target

RQ0 is:

> Can the dynamic allocation and development of competences in a heterogeneous learning system improve long-term system performance compared with architectures that manage task allocation and knowledge transfer separately?

The target cycle is `operation -> learning opportunities -> competence development -> future operational possibilities -> operation`. The two decisions are who does what and who learns what and from whom. Competence is not observed performance, experience, or work; opportunity generation is not competence change; and an operational action is distinct from a development action.

## 2. Retained theory and boundaries

The model-scoped opportunity-value decomposition retains `Omega`: present operation may change the feasible set of future development opportunities. Portfolio interaction is the finite difference `Gamma`, which can be positive or negative according to the geometry of `V(S)`, including routing-induced interaction. In the minimal Fast/Deep result, the integrated action is better than the specified separated alternative precisely when

\[
J_{HLS}>J_{SEP}\iff \beta\Delta>(s-h)+\kappa
\]

under that result's stated assumptions. This is not a universal claim.

The retained negative boundaries are equally important: additive separability, simple work-dependent transfer, scalar/state-dependent prices, and sufficiently rich separated coordination can reproduce a joint optimum. In particular, SEP-Omega can reproduce HLS when it receives the exact continuation value. No result establishes universal joint-management superiority or novelty.

## 3. Experimental evidence map

| Experiment | Status | Main result |
| --- | --- | --- |
| B2.1 PACS factorial | VALIDATION-only | Learning interaction was robustly positive; operational routing transformed and often masked `Gamma`. |
| B2.2 singleton opportunity value | INCONCLUSIVE | Singleton development usually had negative `DeltaV`; the action-to-opportunity mechanism was not reproducibly favorable. |
| B2.3 accumulated opportunities | INCONCLUSIVE | `Gamma_learn>0` in 89/90 pair states, but portfolio rescue was rare; cross-domain competence loss was the bottleneck. |
| B2.4 replay intervention | POSITIVE | REP minus O50 reduced interference and improved future value under its preregistered equal-compute contrast, while seed dependence remained. |
| RQ0 confirmatory evaluation | INCONCLUSIVE | One-shot PACS TEST evaluation found no common positive interval across the frozen grid; HLS and SEP-Omega were exactly equal. |
| B3 adaptive retrospective analysis | Viability NO | Retrospective selection among `0, STD, O50, REP` did not rescue seeds 0, 1, and 3. |
| B4 protected development | INCONCLUSIVE | Small TRAIN protection-set accuracy was not a reliable generalizable preservation signal. |
| B5 gradient-protected development | NULL | Projecting instantaneous opportunity/memory gradient conflicts did not control generalizable competence interference. |

## 4. Integrated RQ0 confirmatory result

The frozen integrated protocol evaluated exactly 70 pre-existing states on PACS TEST once: 5 F0, 5 D, and 60 REP states. Classification was **INCONCLUSIVE**. `max_delta_coord=0`, so the required algebraic equivalence `HLS = SEP-Omega` held exactly. Frozen HLS and SEP actions diverged only for seeds 2 and 4; this is not confirmation of RQ0. TEST was opened once only for that confirmatory evaluation. B3, B4, and B5 do not read or use TEST metrics.

## 5. Seed-dependence diagnosis and B3

Within the common B2.4 provenance, positive `DeltaV` for REP relative to F0 required an empirical combination of sufficient local learning and controlled cross-domain interference. B3 retrospectively chose among `0, STD, O50, REP` from VALIDATION only. It produced viability **NO**: adaptive selection did not create a reproducible positive development region and did not rescue seeds 0, 1, or 3. It is diagnostic, not confirmatory.

## 6. B2.3 ideal-protection ceiling

The retrospective ideal-protected counterfactual preserved observed REP local change while truncating only cross-domain losses to zero. It found a ceiling: 9/12 exact domain-by-N structures had `DeltaV>0` in at least 4/5 seeds, and 15/20 `c x h` cells had some `kappa*>0` region in all 5 seeds. This is **POTENTIAL YES**, not an implementable algorithm or evidence that protection is achievable.

## 7. B4 protected portfolio development

B4 used fixed F0-referenced TRAIN protection-set accuracy to accept or reject REP blocks. It was **INCONCLUSIVE**: mean cross-domain change was nonnegative in only 1/5 seeds, local change in 4/5, no domain-by-N value structure was robust, and 8 `c x h` integration cells reached 4/5. The result shows that the small TRAIN protection-set score was not a reliable generalizable preservation signal and can overprotect; it does not identify an internal learning cause.

## 8. B5 gradient-protected development

### Method and numerical correction

B5 GREP reused the same B2.4 F0, opportunity, replay, SGD optimizer, learning rate, batch construction, seeds, and `T_N` steps. For each 8-opportunity/8-memory batch it computed `g_opp=grad L_opp` and `g_mem=grad L_mem` on the same trainable parameters. If `<g_opp,g_mem> >= 0`, it used `g=g_opp+g_mem`; if the dot product was negative, it used

\[
g_{opp}^{proj}=g_{opp}-\frac{\langle g_{opp},g_{mem}\rangle}{\lVert g_{mem}\rVert^2+10^{-12}}g_{mem},\qquad g=g_{opp}^{proj}+g_{mem}.
\]

Only the opportunity gradient is projected.

The first scientific invocation stopped in its second fit because the projection coefficient had been converted prematurely to float32, leaving an audited residual `-4.77839116053147e-07`. The frozen `1e-7` tolerance was not relaxed. Dot products, memory norm squared, coefficient, projected vector, and `dot_after` audit were moved to float64; only the final combined gradient is converted to float32 immediately before `optimizer.step()`. The partial fit was invalidated by fingerprint and was not reused. Subsequent tests found minimum audited `dot_after` approximately `+9.947598e-14` and maximum violation zero. This was a numerical correction, not a scientific-method change.

### Valid execution and result

The valid CPU-only run completed 60/60 fits and 780 optimizer steps, used VALIDATION only, and recorded `TEST_STATUS=PREVIOUSLY_OPENED_NOT_USED_IN_B5`. Accumulated duration was 01:54:08; session duration was 01:54:26, from 2026-09-25 23:45:53 +0200 to 2026-09-26 01:40:20 +0200. Provenance and technical status passed.

The frozen classification is **NULL**:

```text
cross_improved_vs_REP_seeds          1
cross_nonnegative_seeds              1
local_nonnegative_seeds              1
integration_cells_4of5               0
value_structures_4of5_all_costs      0
```

| Seed | Cross GREP | Local GREP | Cross REP | Local REP |
| ---: | ---: | ---: | ---: | ---: |
| 0 | -0.114658264 | -0.049444439 | -0.083141492 | -0.034938807 |
| 1 | -0.085041706 | -0.013399731 | -0.048071479 | +0.012230664 |
| 2 | +0.006021022 | +0.022558400 | +0.021531725 | +0.030424969 |
| 3 | -0.095277842 | -0.002814447 | -0.078805294 | +0.008369469 |
| 4 | -0.003079600 | -0.005744353 | -0.004271379 | +0.009201000 |

GREP therefore did not resolve the observed interference and generally worsened both cross-domain preservation and local learning relative to REP. Only seed 2 retained positive mean local and cross-domain changes. The result supports the narrow statement that instantaneous gradient conflict was not a sufficient proxy for generalizable competence interference in this experiment. It does not show that gradient projection, continual learning, or HLS fails in general.

## 9. What is established

### Theoretical/model-scoped

- Opportunity value `Omega` and portfolio interaction `Gamma` are distinct mechanisms in the retained model.
- The exact equality and non-superiority boundaries above delimit claims about joint versus separated organization.

### Empirical PACS/VALIDATION

- Positive learning interaction can coexist with destructive singleton cross-domain competence changes.
- The B2.4 replay substitution can substantially reduce those losses and increase future operational value in its declared comparison.
- B4 and B5 did not robustly turn that potential into generalizable protected development across seeds.

### Confirmatory TEST

- The declared 70-state PACS TEST evaluation was completed once and was INCONCLUSIVE; HLS and SEP-Omega were equivalent as derived.

## 10. What is not established

RQ0 is not confirmed. There is no generalization beyond PACS, universal HLS superiority, general competence-preservation method, identified internal cause of seed dependence, or global novelty claim. The work does not establish that the observed failures are catastrophic forgetting, pseudo-label noise, optimization failure, or any other particular latent mechanism.

## 11. Paths closed for now and strategic decision

Do not automatically create B6 as another replay variant, epsilon choice, larger protection set, TRAIN filter, gradient-projection method, or continual learning algorithm on this PACS setup. B4 and B5 show that two local, realizable preservation mechanisms did not robustly realize the available counterfactual ceiling. Continuing mechanically risks replacing RQ0 with “how to avoid interference/forgetting in MobileNet on PACS.”

The next scientific decision is:

> What minimal but non-artificial environment can control competence dynamics sufficiently to demonstrate or falsify RQ0 directly?

It must retain real competence heterogeneity; cost, quality, or latency differences; operationally distinct opportunity generation; competence-changing development; future routing changes; present/future trade-offs; and genuine possibilities of HLS=SEP, SEP winning, or HLS winning. It must not be a toy constructed to guarantee HLS superiority. Seek a connection to a real, current problem and a plausibly publishable trajectory of roughly one year. No next experiment is designed in this checkpoint.

## 12. Mandatory documents and evidence paths

Read [RESEARCH_DOCTRINE.md](../../RESEARCH_DOCTRINE.md), [research_questions.md](../research_questions.md), [hls_ontology.md](../hls_ontology.md), [minimal_hls_model.md](../theory/minimal_hls_model.md), and [operational_development_opportunity_value.md](../theory/operational_development_opportunity_value.md) before new design work.

Primary evidence:

- B2.1/B2.3/B2.4 protocols and checkpoints in `docs/experimental_foundations/` and `docs/checkpoints/`.
- RQ0 one-shot result: `results/confirmatory/rq0_integrated/confirmatory_test/`.
- B3: `results/foundations/b3_adaptive_development/`.
- B4: `results/foundations/b4_protected_development/`.
- B5: `results/foundations/b5_gradient_protected/`.

Relevant freezes and engineering record: B2.4 protocol `491659c`, RQ0 pre-TEST protocol `8b16394`, B4 freeze `8438e48`, B5 freeze `d6a41ec`, and the B5 numerical correction `cf54f81`.
