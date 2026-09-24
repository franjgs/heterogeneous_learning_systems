# PACS B2.3 accumulated-opportunity portfolio protocol

**Status:** PREREGISTERED — NOT IMPLEMENTED.
**Date frozen:** 2026-09-24.
**Scope:** CPU, PACS development splits, VALIDATION only. TEST remains closed
and inaccessible.

This document freezes the scientific design before implementation, training,
or inspection of any B2.3 result. B2.3 is self-contained. It does not combine
B2.1 and B2.2 learned states, which failed the retrospective counterfactual
compatibility audit.

## 1. Scientific question and hypothesis

> Can individually unprofitable learning opportunities become jointly
> profitable when accumulated and used as a development portfolio?

The mechanism under test is

```text
operation
    -> generation of learning opportunities
    -> accumulation of opportunities
    -> joint development
    -> competence change
    -> future operational value.
```

The empirical hypothesis is existential but seed-reproducible: within the
frozen grid, there is at least one exact `N × domain-pair × c × B` regime in
which multiple independent seeds exhibit two individually unprofitable
opportunities whose joint development has positive net value.

B2.3 does not test an ex-ante policy that predicts which opportunities to
accumulate. It tests whether the portfolio mechanism required by such a policy
is realized under matched counterfactuals.

## 2. Frozen system and data roles

- Dataset: `flwrlabs/pacs` at revision
  `394113073258ead631f617d2e13bb377c0715c4b`.
- Source artifact: `data/train-00000-of-00001.parquet`, SHA-256
  `4fc041ee92eec6043fe6e2859e8bdd138e5f958bc621afd153879812cbe65ff5`.
- Fast/student (F): ImageNet-pretrained MobileNetV2.
- Deep/teacher (D): ImageNet-pretrained ResNet-50.
- Seeds: `{0,1,2,3,4}`.
- Opportunity sizes: `N in {25,50,100}`.
- Competence domains, in canonical stored order: `photo`, `art_painting`,
  `cartoon`, `sketch`. The short label `art` means `art_painting` only.
- BASE trains (F_0); BASE+TRANSFER trains (D); TRANSFER supplies
  opportunities; VALIDATION supplies all scores and decisions.
- TEST IDs, labels, images, predictions, and scores are inaccessible to the
  B2.3 data path.
- Device: CPU only.

The split algorithm and memberships are frozen before training. B2.3 stores
their IDs and hashes rather than relying on a later reconstruction.

### 2.1 Exact inherited configuration

The implementation must copy and hash the B2.0 configuration values rather
than silently inheriting whatever a mutable default later contains:

- split proportions are BASE 0.50, TRANSFER 0.20, VALIDATION 0.15, and closed
  TEST 0.15, stratified by domain × class with split seeds `seed`, `seed+1`,
  and `seed+2` as in the canonical splitter;
- the seven label IDs, in order, are `dog`, `elephant`, `giraffe`, `guitar`,
  `horse`, `house`, and `person`;
- F0 uses the domain × class-balanced 25% subset of BASE selected with
  `seed+250`, and its training seed is `seed+2500`;
- D uses BASE+TRANSFER and training seed `seed+30000`;
- F uses `MobileNet_V2_Weights.DEFAULT`, replaces only the seven-class head,
  and trains every parameter with SGD, learning rate 0.001, momentum 0.9,
  weight decay 0, and cross-entropy;
- D uses `ResNet50_Weights.DEFAULT`, replaces only the seven-class head, and
  trains every parameter with SGD, learning rate 0.0001, momentum 0.9, weight
  decay 0, and cross-entropy;
- base fits use three epochs and batch size 16; derived F updates use the
  step rule in Section 5 with F's optimizer settings and a fresh optimizer;
- training transforms are random resized crop to 224 with scale 0.8–1.0,
  horizontal flip with probability 0.5, tensor conversion, and ImageNet
  normalization; validation and teacher pseudo-label transforms are resize to
  256, center crop to 224, tensor conversion, and ImageNet normalization;
- data-loader workers are zero and no parameter is frozen.

Any library-version change that alters named default weights, transforms,
splitting, or deterministic kernels requires an explicit compatibility review
before execution; it cannot be accepted silently.

## 3. Common base states

For each seed, train exactly one (F_0) and one (D). (F_0) uses the B2.1
25%-BASE configuration. (D) uses BASE+TRANSFER. Both retain the PACS
architectures, ImageNet initialization, optimizer parameters, preprocessing,
and three base-training epochs already declared for B2.1/B2.2.

(F_0) depends on seed, not on (N). (N) controls the size of a later
opportunity and cannot alter the pre-opportunity state. Training a separate
(F_0) for each (N) would add noise, cost, and an invalid source of
counterfactual variation.

Every derived state for a seed is initialized by loading the exact same stored
(F_0) checkpoint. No derived state may be an ancestor of another derived
state. In particular, sequential training such as `F_i -> F_ij` is
forbidden.

## 4. Opportunity generation and persistence

The protocol identifier is `B2.3-PACS-portfolio-v1`. For each
`seed × domain`, sort all eligible TRANSFER sample IDs by the full SHA-256
digest of
`protocol ID | opportunity | seed | canonical domain | sample ID` and take
the first 100. This selection does not inspect class labels or model outputs.
The `N={25,50,100}` opportunities are nested prefixes of that ordered stream.
N is an experimental stratum, not an independent replicate. Fewer than 100
eligible samples in any domain is an integrity failure that stops the run.

Deep processes each of the 100 unique examples once in evaluation mode with
the deterministic pseudo-label transform frozen in Section 2.1 and produces
one argmax hard pseudo-label per example. The resulting maximum opportunity
stream is stored before any student update. Its N-specific opportunity view is


\[
e_{i,N}=\{(\text{sample ID},\text{Deep pseudo-label})_r:1\le r\le N\}.
\]

Thus there are 20 maximum streams (`5 seeds × 4 domains`), 2,000 unique Deep
queries, and 60 N-specific opportunity views. The labels for a prefix are never
regenerated. For every pair `(i,j)`, the singleton and joint states reference
the exact same immutable `e_i,N` and `e_j,N` objects by hash.

The operational gate is real:

- action (F): F handles the batch; D is not queried; no opportunity exists;
- action (D): D handles the selected examples and materializes the stored
  opportunity.

An implementation that queries D after recording action F is invalid. Stored
opportunities persist without decay for the two-opportunity horizon. This is a
scoped experimental assumption, not a general HLS claim.

## 5. Derived development states

For every seed and N, train:

- four singletons `F_i = Update(F0, e_i,N)`;
- six unordered joint states
  `F_ij = Update(F0, union(e_i,N, e_j,N))`, with `i<j`.

The union contains exactly N examples from each domain, with no resampling,
new teacher query, or pseudo-label regeneration.

### 5.1 Compute-matched update rule

The B2.1 convention of three epochs would give a 2N joint dataset roughly
twice as many optimizer steps as an N singleton. B2.3 therefore freezes a
step-based rule:

\[
T_N=3\left\lceil\frac{N}{16}\right\rceil,
\]

giving (T_{25}=6), (T_{50}=12), and (T_{100}=21) SGD steps. Every
singleton and every joint state at the same N receives exactly (T_N) steps,
batch size 16, the same optimizer, learning rate, momentum, loss, and no new
freezing rule.

- A singleton batch contains 16 cyclically scheduled examples from its one
  opportunity.
- A joint batch contains eight cyclically scheduled examples from each
  opportunity. Which domain occupies the first half alternates by step.
- Each opportunity list is deterministically reordered once per cycle by
  sorting on the SHA-256 digest of
  `protocol ID | schedule | seed | N | domain | cycle | sample ID`. Cycling
  continues until `T_N` full batches have been consumed.
- This schedule exposes every stored example at least once for every N.

The joint therefore has more unique information, as required by opportunity
accumulation, but receives neither more optimizer steps nor more processed
training examples. Each constituent opportunity consequently receives half of
the joint batch slots that the corresponding singleton receives; that is the
frozen fixed-total-compute estimand. The singleton states are the same-compute,
one-opportunity controls. Every derived fit loads F0 weights and starts a fresh
optimizer; it never loads another derived optimizer or model state.

### 5.2 Deterministic stochasticity

All base and derived training runs set and record Python, NumPy, and Torch RNG
seeds, Torch version, torchvision version, thread count, and deterministic
algorithm settings. Derived states sharing `seed × N` use the same declared
training seed. The implementation must additionally use:

- a stateless augmentation seed derived from
  `(protocol ID, seed, N, sample ID, exposure index)` so that a shared example
  receives the same augmentation at a shared exposure index;
- a per-step Torch seed derived from `(protocol ID, seed, N, step)` for model
  stochastic operations;
- `num_workers=0`, or a tested worker-seeding scheme with an identical recorded
  schedule.

Every derived integer seed is computed by taking the first eight bytes of
`SHA256(UTF-8("B2.3-PACS-portfolio-v1|" + x))` in big-endian order and masking
with `2^63-1`. Here `x` is the exact tuple listed above, serialized with the
literal ASCII delimiter `|`. No process-global RNG state may determine
opportunity membership, batch order, augmentation, or a model operation
without a recorded seed.

The exact ordered batch/sample/exposure schedule is stored and hashed. Results
are invalid if rerunning a fixture from the same checkpoint and opportunity
does not reproduce its final state hash on the execution environment.

## 6. Competence profiles and learning interaction

Evaluate (F_0,D,F_i,F_j,F_{ij}) once on the complete VALIDATION split. For
every state retain

\[
S(F)=(BA_{photo},BA_{art\_painting},BA_{cartoon},BA_{sketch}).
\]

With uniform (p_k=1/4), define the learning-only value

\[
V_{learn}(F)=\frac14\sum_kS_k(F)
\]

and

\[
\Gamma_{learn,ij}=V_{learn}(F_{ij})-V_{learn}(F_i)
-V_{learn}(F_j)+V_{learn}(F_0).
\]

Store the competence changes

\[
\Delta S_i=S(F_i)-S(F_0),\quad
\Delta S_j=S(F_j)-S(F_0),\quad
\Delta S_{ij}=S(F_{ij})-S(F_0),
\]

and their componentwise interaction residual

\[
I^S_{ij}=\Delta S_{ij}-\Delta S_i-\Delta S_j.
\]

These quantities distinguish local learning, cross-domain degradation, and
joint departures from the additive singleton benchmark.

## 7. Operational value and present sacrifice

Retain the B2.2 operational value and frozen cost grid:

\[
V(F;c)=\frac14\sum_k\max\{S_k(F),S_k(D)-c\},
\qquad c\in\{0,0.02,0.05,0.10,0.15\}.
\]

For each opportunity in pair `(i,j)`,

\[
\rho_i(c)=S_i(F_0)-[S_i(D)-c],\qquad
\rho_j(c)=S_j(F_0)-[S_j(D)-c].
\]

The pair represents two current domain batches, so their normalized current
sacrifices add. Each opportunity is one normalized current action/batch in
this inherited value model; `N` changes its stored information, not the
coefficient on current sacrifice. The scientifically relevant region requires
both strict conditions `rho_i>0` and `rho_j>0`.

Define

\[
\Delta V_i=V(F_i;c)-V(F_0;c),\qquad
\Delta V_j=V(F_j;c)-V(F_0;c),
\]

\[
\Delta V_{ij}=V(F_{ij};c)-V(F_0;c),
\]

and

\[
\Gamma_{oper,ij}(c)=\Delta V_{ij}-\Delta V_i-\Delta V_j.
\]

The implementation must independently verify the equivalent four-state
formula

\[
\Gamma_{oper,ij}(c)=V(F_{ij};c)-V(F_i;c)-V(F_j;c)+V(F_0;c).
\]

Store per-domain routing and value contributions for every state so routing
interaction can be separated descriptively from competence interaction.

## 8. Portfolio value and primary event

Freeze the B2.2 continuation grid and primary development cost:

\[
B\in\{1,2,5,10\},\qquad\kappa=0.
\]

For every `seed × N × pair × c × B`, define

\[
H_i=-\rho_i+B\Delta V_i,
\qquad H_j=-\rho_j+B\Delta V_j,
\]

\[
H_{ij}=-(\rho_i+\rho_j)+B\Delta V_{ij}.
\]

The primary event is exactly

\[
\boxed{
\begin{aligned}
portfolio\_rescue={}&(\rho_i>0)\land(\rho_j>0)\\
&\land(H_i<0)\land(H_j<0)\land(H_{ij}>0).
\end{aligned}}
\]

All inequalities are strict and use stored unrounded values. Equality is not a
rescue. The definition is not circular: state training and score evaluation do
not use `rho`, `DeltaV`, `Gamma`, `H`, `c`, or `B`.

The exact identity

\[
\boxed{H_{ij}=H_i+H_j+B\Gamma_{oper,ij}}
\]

must pass within (10^{-12}) for every row. Under the primary event,

\[
B\Gamma_{oper,ij}>-(H_i+H_j)>0,
\]

so the interaction term is mathematically necessary and sufficient to rescue
the negative singleton sum. `interaction_needed` records this equivalence and
must equal `portfolio_rescue`.

## 9. Static rescue and sequential consistency

Record the requested conditional set marginals

\[
H_{j\mid i}=H_{ij}-H_i=H_j+B\Gamma_{oper,ij},
\]

\[
H_{i\mid j}=H_{ij}-H_j=H_i+B\Gamma_{oper,ij}.
\]

For a primary rescue, both are automatically positive because (H_{ij}>0)
and each singleton H is negative. They are consistency checks, not additional
primary filters.

For the literal temporal trajectory, the first opportunity is generated and
stored without updating F. After its sacrifice is sunk, generating the second
opportunity and jointly developing has completion values

\[
M_{j\mid store(i)}=-\rho_j+B\Delta V_{ij}=H_{ij}+\rho_i>0,
\]

and symmetrically (M_{i\mid store(j)}=H_{ij}+\rho_j>0). These inequalities
also follow from a primary rescue. A temporal interpretation additionally
requires verified opportunity persistence, no intermediate F update, exact
joint use of the two stored opportunity hashes, and the real operational gate.

This experiment does not show why an ex-ante policy would accept the first
negative prefix. It establishes only that a committed or anticipatory
accumulation trajectory can have positive completed value.

## 10. Unit of analysis and pseudoreplication

The learned experimental unit is one independent
`seed × N × unordered-domain-pair` state family sharing its seed's F0, D, and
opportunities. There are 90 such pair families. Values of c and B are
deterministic analytical revaluations of the same learned states; they are not
new experimental replicates. Nested N prefixes are separate predeclared
regimes but are statistically dependent and are not pooled as independent
replications.

The complete primary table has

\[
5\times3\times6\times5\times4=1{,}800
\]

analytical rows. Reproducibility is evaluated across the five seeds within one
exact `N × pair × c × B` cell. Counts across different c, B, N, or pairs are
reported descriptively and never substituted for seed replication.

No inferential significance test is planned for (n=5).

## 11. Frozen outcome classification

Classification occurs only after every integrity check passes and the full
grid is complete.

- **POSITIVE:** at least one exact `N × pair × c × B` cell exhibits
  `portfolio_rescue` in at least 3 of 5 seeds.
- **NULL:** no one of the 1,800 predeclared rows exhibits
  `portfolio_rescue`.
- **INCONCLUSIVE:** at least one rescue exists, but no exact cell reaches 3 of
  5 seeds.

An integrity, provenance, TEST-closure, determinism, missing-state, or
compatibility failure makes the run **INVALID** and prevents these three
scientific labels. INVALID is a validity status, not a fourth empirical
outcome.

The existential POSITIVE label may describe a narrow regime. It does not
license a prevalence claim. Multiple favorable c/B values from one learned
state remain one seed realization.

## 12. Controls and threat-specific comparisons

1. **No-opportunity control:** the shared F0 gives the counterfactual action-F
   trajectory with no Deep query and no development.
2. **Singleton controls:** (F_i,F_j) use each immutable opportunity alone and
   identify their absolute values and competence changes.
3. **Compute-dose control:** (F_i,F_j,F_{ij}) have identical optimizer-step,
   batch-size, and processed-example budgets at a fixed N. This removes a
   trivial double-step advantage.
4. **Additive portfolio control:** (Delta V_i+Delta V_j), equivalently
   (Gamma_{oper}=0), is the no-interaction benchmark. A rescue necessarily
   requires the observed (B\Gamma_{oper}) to exceed the summed singleton
   deficit.
5. **Routing decomposition:** recompute the four state values with domain-level
   routing and store which domains change router. Compare
   (Gamma_{learn}) and (Gamma_{oper}) without calling their difference a
   causal routing effect.
6. **Opportunity-gate control:** log zero teacher queries and zero pseudo-labels
   for every action-F trajectory; log exactly N for each action-D opportunity.

A trained label-permutation control was considered and rejected before
freezing: it destroys teacher information rather than isolating portfolio
structure, and would add 90 fits. A 2N same-domain control would require
generating a different, larger opportunity and a different operational
sacrifice. Neither is a matched counterfactual for the stated mechanism. The
singletons plus fixed-step and exact additive controls address the relevant
compute and interaction threats without changing the treatment.

## 13. Decomposition of any rescue

For every rescue report:

- (H_i,H_j,H_{ij},B\Gamma_{oper}) and
  (B\Gamma_{oper}/H_{ij}), while noting that this ratio can exceed one
  because singleton terms are negative;
- (Delta V_i,Delta V_j,Delta V_{ij});
- (Gamma_{learn}) and (Gamma_{oper}(c));
- all four components of (Delta S_i,Delta S_j,Delta S_{ij},I^S_{ij});
- local changes on i and j, and changes on the other two domains;
- routing patterns and per-domain operational-value contributions;
- (H_{j\mid i},H_{i\mid j},M_{j\mid store(i)},M_{i\mid store(j)}).

Avoided cross-domain interference is supported descriptively when joint
nonlocal degradation is smaller than the additive singleton benchmark.
Greater local learning is supported when joint local changes exceed that
benchmark. Routing transformation is supported descriptively when competence
interaction and operational interaction differ alongside router changes.
These are comparisons among trained counterfactuals, not general causal claims
beyond the frozen intervention.

## 14. Required machine-readable provenance

The future implementation must create, before scientific analysis:

- `run_manifest.json`: protocol/config/source hashes, Git commit, command,
  package versions, device, thread/determinism settings, dataset revision and
  artifact hash;
- `split_manifest.csv`: every sample ID and its BASE/TRANSFER/VALIDATION role;
- `base_states.jsonl`: seed, training IDs/hash, seed/RNG procedure, F0/D
  checkpoint paths and SHA-256 hashes, and complete validation S vectors;
- `opportunities.jsonl`: seed, domain, maximum ordered ID list, each
  pseudo-label, N-prefix hashes, D checkpoint hash, query count, and creation
  action;
- `development_states.jsonl`: state ID, parent F0 hash, exact opportunity
  hashes, N, unordered pair if applicable, step/batch schedule hash, seeds,
  hyperparameters, final checkpoint hash, and complete validation S vector;
- incremental completion records and checksums sufficient for safe restart.

No image, model checkpoint, or cache belongs in Git. Manifests and scientific
CSV/JSON summaries do.

The state relation must be machine-checkable:

```text
seed -> {F0 hash, D hash}
seed,N,domain -> opportunity hash -> Fi hash
seed,N,pair -> {same two opportunity hashes, same F0 hash} -> Fij hash
```

## 15. Mandatory pre-analysis compatibility audit

Abort before calculating Gamma or H unless all checks pass:

1. exactly five F0 and five D states, one pair per seed;
2. every derived state's parent hash equals its seed's F0 hash;
3. every (F_i) references exactly one declared opportunity;
4. every (F_{ij}) references exactly the two same opportunity hashes used by
   (F_i,F_j), with no resampling or relabeling;
5. opportunity sample counts, IDs, pseudo-labels, D hash, and prefix relations
   are exact;
6. derived step counts equal (T_N), batch sizes equal 16, and schedule/RNG
   hashes match the protocol;
7. no sequential derived parent exists;
8. all scores use the same complete VALIDATION IDs;
9. TEST is absent from code-visible split objects, manifests, logs, and outputs;
10. all expected checkpoints, score vectors, hashes, and 160 evaluations are
    present without duplicates or NaN;
11. a deterministic fixture reproduces its checkpoint and score vector;
12. all Gamma and H algebraic identities pass within (10^{-12}).

## 16. Analysis plan

Report without selecting regimes retrospectively:

- all 1,800 primary rows;
- rescue counts by exact cell and number of seeds (0 through 5);
- learned-state counts separately from analytical row counts;
- cells with rescue in at least 2, at least 3, and 5/5 seeds;
- distributions and signs of (Delta S,Delta V,Gamma_{learn},Gamma_{oper},H)
  by N and pair;
- the exact minimum continuation thresholds, when denominators are positive:
  (B^*=(\rho_i+\rho_j)/\Delta V_{ij}),
  (B_i^*=\rho_i/\Delta V_i), and
  (B_j^*=\rho_j/\Delta V_j), without adding new B values;
- automatically selected largest H, nearest-boundary, largest interaction,
  most seed-reproducible, negative-singletons/positive-joint, and
  learning/operational-sign-change cases when they exist;
- both favorable and non-favorable regions.

The primary conclusion uses only the frozen classification. Thresholds,
decompositions, and cases are descriptive.

## 17. Computational design and estimate

Exact trained objects:

| Object | Count |
| --- | ---: |
| F0 base fits | 5 |
| D base fits | 5 |
| Maximum opportunity streams | 20 |
| N-specific opportunity views | 60 |
| Singleton updates | 60 |
| Joint updates | 90 |
| **Total model fits** | **160** |
| **Validation evaluations** | **160** |
| **Primary analytical rows** | **1,800** |

F0 and D are shared across every N and intervention for a seed. Each singleton
is trained once and reused in its three pairs. c and B are analytical only.

Measured references on this CPU are 6.07 hours for the five D plus five
25%-BASE F0 fits, 1.68 hours summed across the 60 B2.2 singleton updates and
their validation work, and 08:10:14 total for B2.2. Scaling the observed
N-specific update times to 150 compute-matched derived states gives about 4.21
hours beyond the base fits. The resulting planning estimate is approximately
10.3 hours before extra manifest/integrity overhead; reserve **10–12 CPU
hours**. This is an estimate, not a guaranteed runtime.

## 18. Relationship to B2.1 and B2.2

B2.3 reuses conceptually:

- B2.1's four-state factorial geometry and competence interactions;
- B2.2's real operation-dependent opportunity gate, operational value,
  sacrifice, c/B grid, and absolute H value.

It corrects the inability to bridge those runs by training every base,
singleton, and joint state in one provenance-locked execution. It also removes
the trivial joint step advantage through fixed-step development.

From valid B2.3 artifacts, without retraining, one may reconstruct:

- a B2.1-type analysis: (Delta S,Gamma_{learn},Gamma_{oper}), and routing
  for all singleton/joint states;
- a B2.2-type analysis: singleton `(rho, DeltaV, Omega, H)` over the frozen c/B
  grid;
- the B2.3 portfolio analysis: pair sacrifices, joint (Delta V), Gamma, H,
  rescue, and sequential consistency.

These are B2.1-type and B2.2-type results under the B2.3 fixed-step protocol,
not retroactive replacements for the historical three-epoch results.

## 19. Stopping, restart, and result discipline

- Do not stop early for favorable or unfavorable outcomes.
- Complete all 160 fits and 160 validation evaluations before analysis.
- An interrupted run may resume only from hash-compatible complete artifacts.
- Stop and mark INVALID on provenance, determinism, compatibility, split,
  opportunity-gate, or TEST-closure failure.
- Do not change N, c, B, kappa, pairs, seeds, step budgets, classification, or
  controls after result inspection.
- Do not open TEST for selection, diagnosis, reporting, or confirmation.

## 20. Adversarial protocol audit

The final design addresses the following reviewer objections:

- **Trivial joint compute advantage:** removed by identical (T_N), batch
  size, and processed-example budgets.
- **Extra unique data:** retained because two distinct stored opportunities are
  the treatment; its non-additive value is tested against both singletons.
- **Pseudoreplication:** seeds within an exact cell are the reproducibility
  units; c/B rows and nested N values are not replicates.
- **Leakage:** TRANSFER creates opportunities, VALIDATION scores states, TEST is
  inaccessible. D is trained on BASE+TRANSFER, so these are teacher-output
  opportunities on D's training role; B2.3 cannot support a claim about
  out-of-sample teacher labeling.
- **RNG/order effects:** stateless augmentations, per-step seeds, deterministic
  schedules, stored hashes, and a reproduction fixture are mandatory.
- **Post-hoc selection:** all N, pairs, c, B, thresholds, and the 3/5 criterion
  are frozen and fully reported.
- **Circular rescue:** H is calculated only after state training and validation;
  no value quantity affects training or selection.
- **Unfair singleton/joint comparison:** exact shared F0/opportunities and
  equal compute are audited before analysis.
- **Temporal overclaim:** static rescue is primary; persistence and completion
  consistency are checked, while ex-ante selection remains untested.
- **Multiple favorable rows:** classification never treats analytical c/B
  revaluations as independent experiments.

No unresolved issue requires changing the frozen primary event. The strict
event is algebraically coherent with the exact H decomposition and the scoped
two-action sacrifice model.

## 21. Claims allowed and prohibited

A POSITIVE result permits the scoped statement:

> Under at least one predeclared PACS regime reproduced in a majority of seeds,
> two operation-generated learning opportunities that are individually
> unprofitable become jointly profitable when accumulated and developed under
> the matched B2.3 portfolio intervention.

It would support a stronger empirical piece of the RQ0 mechanism:

```text
operation -> opportunities -> accumulation -> joint development
          -> competence change -> future operational value.
```

It would not demonstrate:

- an implementable ex-ante policy that identifies the opportunities;
- universal HLS or joint-management superiority;
- superiority over every sufficiently rich separated architecture;
- a complete closed-loop answer to RQ0;
- TEST generalization;
- causality outside the frozen intervention and value mapping;
- prevalence across tasks, models, or datasets;
- novelty.

A NULL result means only that the strict event is absent from this frozen grid.
An INCONCLUSIVE result records isolated/non-majority rescues without sufficient
seed reproduction. Neither result refutes RQ0 in general.

## 22. Canonical dependencies

- `RESEARCH_DOCTRINE.md`
- `docs/research_questions.md`
- `docs/hls_ontology.md`
- `docs/theory/minimal_hls_model.md`
- `docs/theory/operational_development_opportunity_value.md`
- `docs/checkpoints/HLS_checkpoint_after_B21.md`
- `docs/experimental_foundations/B22_PROTOCOL.md`
- `results/pilots/b22_opportunity_value/b22_diagnostic.md`
- `results/pilots/b22_opportunity_value/portfolio_bridge/portfolio_bridge.md`
