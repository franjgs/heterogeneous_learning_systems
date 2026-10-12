# HLS Campaign 4 — Counterfactual deliberation: engineering preparation

**Status (12 October 2026): PREPARATION ONLY. NO SIMULATIONS AUTHORIZED.**

## Scientific priority

1. **Where** is deliberation beneficial? Estimate the true paired FAST-versus-DEEP return difference on recorded states.
2. **How** does its distribution evolve with capability maturity, specialization, dispersion, belief, and trajectory time? Report associations; do not infer mediation.
3. **Can the frozen Ridge/META-VOC recognize these opportunities** across G1–G4? Predictor diagnostics are subordinate to (1) and (2).

## Verified repository interfaces and provenance

Directly inspected through the connected GitHub repository `franjgs/heterogeneous_learning_systems`:

- `experiments/synthetic/campaign3_meta_voc/run.py`: `ex_ante_score(state,belief,tau,model_spec,costs)`, `threshold_route(score,key,threshold)`, `feature_tie_key`, `make_exogenous`, `simulate`.
- `experiments/synthetic/campaign3_meta_voc/confirmatory.py`: `planned_tasks()`, `partitions()`, `random_routes()`. Frozen namespace `campaign3_meta_voc_confirmatory_v1`; domain sizes 420/200/168/80.
- `experiments/synthetic/campaign3_fast_deep_meta/run.py`: `choose_fast_action(state,belief,remaining)`, `choose_deep_action(state,belief,remaining)`.
- `experiments/synthetic/campaign3_c33/c33.py`: `feature_vector(state,belief,tau)` and `predict(model,x)`; `supervised_table` constructs `raw_mc_G(Q11)-raw_mc_G(Q00)` from C3.2 data with `continuation==Q11`.
- `src/hls/campaign2_theory.py`: `_real_decision(state,belief,action,true_problem,epsilon,model)`; `two_decision_counterfactual` explicitly forces initial Q11 versus Q00 and continues both branches with Q11 for **exactly two real decisions**, even when `remaining=3`.
- `src/hls/campaign3_problem_generator.py`: `generator_transition(history,kernel,rng)`; STAY/MOVE/RETURN kernel and reflection into `[0.2,0.8]`.
- `docs/paper/META_VOC_SCIENTIFIC_RECORD.md`: CES rho=.5; Gaussian observation sigma=.10; MIS-v2 eta=.35; 12 physical problems ×3 decisions; belief resets at each problem boundary while capabilities persist.

**Frozen artifact SHA-256 verified from user-provided original files:** `runs.csv.gz`: `3c2d7310a510deed03264b9a6df30ffc09a0af5915cc76dba233d29eadfd9e28`; `trajectories.csv.gz`: `b4022b7a76c2aece607138d6d740ae854517fa171e889d09c557350c8da2e498`.

**Critical discrepancy:** C3.2's two-decision target is **not** generally the full-current-problem return for `remaining=3`. Use separate horizons. Ridge input is exactly the six capability entries, three subjective belief masses, and `tau/36`. Frozen cost estimates: 0.209201959 s (`remaining=2`), 0.209788291 s (`remaining=3`); frozen META-50 threshold score 0.16708983036248765 plus its feature-hash tie rule. **Read the complete frozen calibration and model JSON at execution time and verify hashes; never hard-code tie cutoffs or fitted coefficients.**

## A. Mathematical estimands

Let `x=(S,b,h,t,j,history_id,source_policy)` be a recorded pre-decision state, and `z_j=(p_j,1-p_j)` the latent physical problem from its exogenous history. The true latent `p_j` is **not** distributed according to the agent's three-mass `b`. Initial `p_1 ~ Uniform(.2,.8)` and subsequent `p_j` arise from the physical STAY/MOVE/RETURN process; `b` is a subjective filter over three fixed hypotheses. The exact `P(z_j | S,b,h,t)` is not identified by the logged state alone, because it depends on unrecorded full histories and the physical generator. **Primary estimand is conditional on the realized latent history and averaged over a defined empirical source-state population**, not an exact Bayes value conditional on `S,b`.

`a_F(x)=choose_fast_action(S,b,h)[0]`; `a_D(x)=choose_deep_action(S,b,h)[0]`.

- **Immediate:** `d0(x,z)=mu_true(S,a_D,z)-mu_true(S,a_F,z)` (deterministic given state, action, and z).
- **Paired sequential:** `D_i,r^(c,H)=sum_{k=t}^{H} mu_true[k|do(a_D),pi_c,omega_i,r] - sum_{k=t}^{H} mu_true[k|do(a_F),pi_c,omega_i,r]`. The same `pi_c` rule applies after the first action in both branches, but subsequent states and actions may differ. Conditional mean `Delta_i^(c,H)=E_omega[D_i,r^(c,H)|x_i,z_history]`.
- **H0 (target-fidelity):** two real decisions, Q11 continuation; `remaining=3` stops before terminal step. This matches the documented *structure* of C3.2's single-realization Q11-minus-Q00 label, subject to exact C3.2 code audit.
- **H1 (current problem):** `h` real decisions, Q11 continuation; when `remaining=2`, H0=H1 if all other conventions match.
- **H2 (global):** `37-t` decisions through clock 36, primary continuation frozen META-VOC-50; Q11 continuation is an optional separately budgeted sensitivity analysis.
- **Population mean:** `Theta_g^(c,H)=sum_{i in U_g} Delta_i^(c,H)/|U_g|`, where `U_g` is the finite population of **nonterminal decision rows** for FAST, DEEP, META_VOC_50, RANDOM_50 in domain `g`. Other populations (e.g. META-only states) are separate estimands. Sample weights are inverse inclusion probabilities.

**Causal interpretation:** The initial forced-action contrast is an intervention effect **conditional on the simulation model, recorded state, fixed exogenous history, continuation rule, and horizon**. Temporal associations between `Delta` and capability descriptors do **not** identify the causal effect of capability maturation or the mediation of production by capability changes.

## B. State sampling (implemented, NOT run)

`campaign4_counterfactual_deliberation/sampling.py` provides a reproducible outcome-blind design. For each domain × nine-decision block, select **50 distinct histories** by deterministic SHA-256 priorities. Independently permute 50 labels covering `remaining=2/3` equally (25 each) and source policies FAST/DEEP/META_VOC_50/RANDOM_50 with quotas 6 or 7 per label (rotated). Each selected history receives exactly one label and one uniformly hash-ranked candidate clock among the three eligible clocks in that block. This yields 4 domains × 4 blocks × 50 = **800 states**, with no repeated history *within a domain × block*. G4 has 80 histories, enough for 50. A history may recur in other blocks: inference clusters by history.

Each original candidate in `(g,block,h,policy)` has inclusion probability `q/(3 H_g)` where `q=6 or 7`, `H_g` is the number of distinct histories in domain `g`, and there are exactly three candidate clocks per block/horizon. The Horvitz–Thompson estimator for the finite frame is `sum_selected(delta_i / pi_i) / |U_g|`; a Hájek ratio estimator is a prespecified robustness analysis. This is **not** equal to naïvely averaging the 200 sampled states per domain, because policy/horizon quotas and history sampling change inclusion rates. `sampling_weight=1/pi_i` is recorded. Source-policy mixtures must be reported explicitly.

Long-horizon subsample: select 10 of the 50 selected states independently by another deterministic hash within each domain × block: **160 states**, 40/domain. Conditional probability `.2`, overall inclusion probability `.2*pi_i`. Record all frame counts, identifiers, seeds, and hashes. Selection must be frozen before any counterfactual outcome is computed. The script does not execute the simulator.

## C. Counterfactual engine (implementation contract; not yet written)

For each selected state, recover `S`, `b`, `clock`, `remaining`, `tau`, `history_id`, source policy. Join original `runs.csv.gz` to retrieve exact `problem_seed` and `noise_seed` (use integer-preserving CSV dtypes); reconstruct 12 physical problems via **the frozen** `voc.make_exogenous(task)` or equivalent exact generator, after reconstructing the correct team/kernel task from `confirmatory.planned_tasks()`. Verify reconstructed exogenous SHA against `runs.csv.gz` for **every sampled history**. Check original observed `mu_true` by replaying the factual action at the selected clock using `theory._real_decision` with recorded `state_before`, `belief_before`, true problem and original epsilon; match logged `mu_true`, `state_after`, `belief_after` within explicit numeric tolerance. This is a **reconstruction check**, not a new policy simulation.

For each state compute FAST and DEEP once, with no state mutation; record both action IDs, action equality, raw Ridge prediction, truncated benefit, ratio score, threshold and tie result. For replicate `r`, produce exogenous observation innovations by a **counter-based hash of `(state_id,replicate,clock,'observation')`**, converted deterministically into a standard normal via a specified NumPy PCG64 seeded from the hash. This avoids branch-dependent PRNG consumption. At horizon H2, **prefer replaying the full original physical-problem stream from the frozen problem seed**, which is action-independent and therefore valid to share between branches; this estimates effects conditional on the original exogenous physical history. Do not reuse the factual observations, which are action-dependent. The alternative estimand integrating new future physical histories is explicitly out of scope.

Intervene at initial action; run `_real_decision` with the same clock-indexed epsilon in both branches; continue using exactly the same frozen decision rule. On each new physical problem reset belief to `UNIFORM_PRIOR` and retain capabilities. At terminal step call FAST. The planning horizon of DEEP stays unchanged (effective 2,2,1); H0/H1/H2 are **evaluation** horizons, not changes to Q11.

**Mandatory invariants:** when `a_F==a_D`, all paired returns, states, beliefs and future routing decisions coincide exactly within floating tolerance; branch execution order invariance; stable results across worker counts; correct terminal behavior and belief resets; unchanged original file hashes. Any failed invariant aborts execution before analysis.

## D. Statistics: primary ordering of questions

1. **Opportunity landscape:** weighted `E[Delta]`, median/quantiles, `Pr(Delta>0)`, positive/negative benefit magnitude, action coincidence rate, by domain, temporal block and horizon. Use **H0 Q11** as a target-fidelity anchor and **H1 Q11** as the main *scientific* opportunity outcome. Clearly label their distinction.
2. **Evolution:** weighted associations with capability mean, specialization `mean_i |S_i1-S_i2|`, overall SD, between-agent SD, belief entropy, time, and remaining horizon. Predefine descriptive smooths with domain × horizon stratification; analyze entropy variation **within remaining=2** because remaining=3 always starts from uniform belief. Time/capability correlations cannot be interpreted causally. Primary contrast: change in H1 opportunity mean between B1 and B4 within each domain; secondary contrast: difference in that change between development-team domains G1/G2 and held-out-team domains G3/G4. Report effect sizes and CIs, not only p-values.
3. **Selector quality:** compare *untruncated* frozen Ridge prediction to H0 Q11 `Delta`; bias, MAE, RMSE, Spearman, calibration curves, positive-benefit detection and captured benefit at **prespecified** invocation budget. Report both the raw predicted advantage and its `max(0,prediction)/cost` score and frozen threshold decision. G3/G4 generalization vs G1/G2, separating held-out teams and held-out kernels.
4. **Matched-budget diagnostics:** choose a fixed number `K` of selected states based on the **frozen META route count** within a prespecified evaluation population (K does not depend on observed deltas). RANDOM uses independent hash priorities with exactly K; repeat random schedules with fixed prespecified seeds, reporting their variation. Compare production benefit captured and cost estimated using frozen clock-stratum costs. **Oracle** is retrospective and nondeployable; rank with MC replicates 1–16 and evaluate with independent replicates 17–32, explicitly noting winner's curse and reduced precision. A policy comparison over sampled states is a **one-step opportunity diagnostic**, not a replacement for the original full closed-loop Campaign 3 policy comparison.
5. **Long horizon:** decompose **accounting identity** `Delta_H2=Delta_current_problem+Delta_future_problems`, plus final capability/specialization, future DEEP calls, and state divergence; this is not causal mediation. Use 160 preselected states and primary META-VOC continuation; Q11 long continuation requires separate budget authorization.

**Inference:** treat each `history_id` as the primary resampling cluster and preserve all selected rows of a history across blocks. Stratify bootstrap by domain (2,000 replicates predeclared). Within-state MC error: `Var_MC(Delta_hat_i)=s²_i/M`. To propagate uncertainty, resample independent paired MC replicates **within each selected state** inside each history-cluster bootstrap, without pretending 32 replicas are 32 histories. Sensitivity: multiway team/kernel clustering or hierarchical resampling is desirable but must respect the crossed finite-factorial design; do not assume team/kernel identifiers are random draws from an external population. G4 has only 80 distinct histories; effective precision is limited.

**Important measurement-error caveat:** MAE/RMSE computed against noisy `Delta_hat` are inflated; report Monte Carlo SEs and optionally subtract estimated MC variance from squared-error averages (with possible nonnegative truncation of the corrected aggregate). Rank correlation is attenuated by label noise. Do not treat non-significance as equivalence.

## E. Budget and feasibility

Measured C3 references: DEEP policy ~5.5785 s/36-decision history (24 nonterminal DEEP calls), hence **~0.2324 s/DEEP call** as a rough mean under the original machine and workload; frozen cost calibration median ~0.209–0.210 s extra per DEEP call. FAST ~0.0143 s/history. These exclude physical simulator and I/O, and may change under parallel execution. The C3 end-to-end execution took 2,719.5 s for 868 histories ×8 policies using eight workers; this is not a per-branch benchmark.

- H0, Q11, N=800, M=32, two branches: 51,200 branches, **102,400 real decisions**. For `remaining=3`, each branch has **one** nonterminal Q11 continuation call; for `remaining=2`, its continuation is terminal FAST. With exactly 400 states of each horizon, the H0 continuation uses **25,600 DEEP calls**. Initial action calculations require at most 800 additional DEEP calls (one per state), total **26,400 calls**. Rough DEEP CPU-wall reference **6,136 s** (26,400 ×.2324), plus physical transitions/FAST/reconstruction/I/O. This is an approximation, not a measured forecast.
- H1, Q11, **if run separately without caching H0**, `remaining=3` adds a terminal FAST decision per branch: 400 × 32 × 2 = **25,600 extra FAST decisions**, no extra DEEP continuation calls. Prefer recording H0 as a prefix of H1 where `remaining=3`; H0/H1 can share the first two decisions, avoiding redundant computation.
- H0 + H1 shared engine: 102,400 two-decision transitions + 25,600 terminal transitions = **128,000 real decisions** and ~26,400 DEEP calls, ignoring equal-action optimization.
- H2, 160 states ×32 reps ×2 branches = **10,240 branches**. Because selected clocks range from 1 to 35, maximum is 36 physical decisions/branch; worst-case **368,640 physical decisions**. At most 24 nonterminal DEEP calls/branch under Q11, i.e. 245,760 additional DEEP calls in an extreme upper bound. Under frozen META-50 actual call count is state-dependent and cannot be known without execution; **do not claim a precise long-horizon runtime**.

**Pre-execution hard stop proposal:** H0/H1 phase maximum **30,000 DEEP calls and 3 wall-clock hours** on the reference eight-worker machine, whichever first; H2 phase **250,000 DEEP calls and 24 wall-clock hours**, whichever first, **pending CE feasibility review**. These are safety ceilings, not evidence of sufficient compute. Run phases separately; record resumable atomic batches, progress counters, and failure state; never partially interpret a stopped sample as complete without accounting for missingness.

**N/M justification:** 800 states are a **stratified diagnostic design**, not a power-calibrated confirmatory sample. M=32 is a provisional MC precision budget; for a paired-difference SD `sigma_D`, state-level MC SE = `sigma_D/sqrt(32)≈0.177 sigma_D`. No prior same-state paired variance is available from Campaign 3 (different policies visit different states), so a numeric power guarantee is impossible. A limited, separately authorized technical pilot is required if reviewer demands a formal precision target. Predefine an MC SE tolerance in units of production and a minimum detectable domain/temporal contrast before authorizing a definitive execution; do not choose M after significance inspection.

## F. Implementation plan and gates

Proposed repo structure:

```
experiments/synthetic/campaign4_counterfactual_deliberation/
  sampling.py             # provided in preparation package
  reconstruction.py       # exact exogenous replay and factual checks
  interventions.py        # frozen FAST, DEEP, Ridge and routing
  innovations.py          # keyed, branch-independent normal draws
  rollout.py              # H0/H1/H2, continuation, boundary handling
  records.py              # atomic batch persistence and manifests
  analysis.py             # weighted estimators, clustered uncertainty
  figures.py              # opportunities first, selector second
  cli.py                  # --verify / --prepare / --execute gated
```

Outputs only under `results/campaigns/campaign4_counterfactual_deliberation/`: frozen frame/selection and manifest; paired replicate data; per-state outcomes; opportunity landscape tables; predictor diagnostics; long-horizon decomposition; final hash manifest. Freeze source commit, all source/model/calibration hashes, software/hardware versions and configuration. **No write path may target Campaign 3.**

### Five mandatory pre-execution closure gates

1. **C3.2 equivalence:** inspect the exact C3.2 data-generation function, not only C3.3's `supervised_table`, to verify `raw_mc_G`, Q00 action, Q11 continuation, two-decision horizon, epsilon pairing, and state construction. If differences exist, name H0 an approximation rather than the exact training estimand.
2. **Latent stream/reconstruction:** prove replay of all sampled original latent problems and factual one-step observations/transitions against frozen hashes and logs; distinguish conditioning on realized z from integrating a hypothetical true posterior given observable s.
3. **Sampling/inclusion:** validate quotas, nonzero candidate probabilities, formula `q/(3H_g)`, exact 800/160 counts, source-policy composition, and no outcome-dependent selection; freeze selected IDs and weights.
4. **MC precision/inference:** declare smallest scientifically relevant contrasts, cluster unit, MC uncertainty method, and whether M=32 meets precision needs. If unknowable, explicitly mark the study exploratory or request a **separately authorized** pilot.
5. **Runtime/engineering:** audit the full continuation call count and action-equality shortcuts, verify hard ceilings and crash-safe resumability; confirm original source hashes and that all C4 writes are isolated.

**Present status:** sampling code is prepared and syntax-checked; the counterfactual runner has **not** been implemented or run. C3.2 generation code, model/calibration JSON and foundation allocation files were **not** available as local working copies during this preparation. Consequently, gates 1, 2, 4 and 5 are not certified, and no execution is authorized. The engineer should implement and close those gates before requesting GO.
