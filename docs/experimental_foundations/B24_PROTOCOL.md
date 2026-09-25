# B2.4 — Interference-Controlled Development

**Status:** PROPOSED PREREGISTRATION — READY TO FREEZE, NOT IMPLEMENTED, NOT
EXECUTED. No B2.4 result may be inspected before this document is frozen.

## 1. Scientific question

> Can cross-domain interference be reduced while preserving learning from the
> same operational opportunity, and how does this affect the future value of
> development?

B2.4 tests whether a controlled change in the student-development mechanism
alters the cross-domain competence losses diagnosed after B2.3. It does not
test pairs of opportunities, learning or operational Gamma, portfolio rescue,
or an end-to-end HLS policy.

The four learned counterfactuals are:

- **STD:** the original B2.3 singleton update using only opportunity `O_i`;
- **O50:** an equal-compute opportunity-only control using exactly the same
  informative opportunity exposures as REP and filling the other batch slots
  with exact duplicates of those exposures;
- **REP:** an equal-compute update whose batch slots are divided equally
  between `O_i` and historical replay from the other three domains;
- **REP2:** a secondary dose contrast that continues the REP trajectory until
  both `O_i` and replay have received the full STD exposure dose.

## 2. Frozen experimental base

B2.4 uses the completed B2.3 artifacts under a common provenance:

- PACS revision `394113073258ead631f617d2e13bb377c0715c4b`;
- CPU only;
- VALIDATION supplies all competence scores; TEST remains closed and
  inaccessible;
- seeds `{0,1,2,3,4}`;
- canonical domains `photo`, `art_painting`, `cartoon`, `sketch`;
- `N in {25,50,100}`;
- the exact B2.3 split manifest, five `F0` checkpoints, five `D` checkpoints,
  and 60 immutable opportunity views;
- the exact B2.3 hard pseudo-label attached to each opportunity example;
- MobileNetV2 student, ResNet-50 teacher, optimizer, normalization, and
  deterministic settings frozen in B2.3.

There are 60 learned cases `seed × intervention-domain × N`. The five seeds
are the units of replication. N-specific opportunities and replay buffers are
nested regimes, not independent replicates. No pair, Gamma, `H`, or
`portfolio_rescue` quantity is defined in B2.4.

Before any new fit, an integrity audit must verify the B2.3 protocol,
configuration, dataset revision, split hashes, F0 and D checkpoint hashes,
opportunity hashes, validation-ID hashes, and `test_used=false`. An
incompatible or incomplete B2.3 parent makes the affected B2.4 case invalid;
it may not be silently reconstructed from a different state.

## 3. Common starting state and frozen STD

For a case `(seed,i,N)`, all counterfactual development starts from the exact
same stored B2.3 `F0(seed)` checkpoint and a fresh optimizer with B2.3's Fast
settings. No developed state is an ancestor of another independent
counterfactual.

STD is the completed B2.3 singleton `F_i` for the same `(seed,i,N)`. Its
checkpoint, schedule hash, opportunity hash, F0-parent hash, and VALIDATION
scores are reused after compatibility validation; STD is not retrained or
relabelled in B2.4.

O50 is one new independent trajectory from F0. REP is saved at the midpoint
of a second new deterministic trajectory from F0. Continuing that same mixed
trajectory produces REP2, so REP2 is not an additional fit. Validation of the
saved REP midpoint occurs only after the REP2 trajectory has finished, so
validation cannot alter the training RNG path.

## 4. Immutable operational opportunity

`O_i(seed,N)` is exactly the corresponding B2.3 opportunity artifact:

- its N TRANSFER sample IDs are the frozen prefix of the seed/domain stream;
- each sample retains its stored B2.3 hard pseudo-label from D;
- no sample is replaced or resampled;
- D is never queried again;
- no additional TRANSFER sample is available to development.

The STD, O50, REP, and REP2 records must all reference the same opportunity
hash.

## 5. Historical replay buffer

### 5.1 Eligible information

For intervention domain `i`, the replay pool contains only the exact PACS
training IDs recorded in the parent F0 artifact, restricted to the other three
domains. Domain `i` is excluded. Each replay sample uses the original PACS
ground-truth label that F0 already observed.

The following are forbidden:

- VALIDATION or TEST IDs, images, labels, predictions, or scores;
- any TRANSFER example outside `O_i`, including another stored opportunity;
- BASE examples not used to train the exact parent F0;
- newly generated D pseudo-labels;
- pseudo-labels from another opportunity.

Because the replay pool is in BASE and `O_i` is in TRANSFER, every replay
buffer must be disjoint from every B2.3 opportunity. This is checked by ID,
not inferred from filenames.

### 5.2 Exact deterministic construction

The replay-buffer size is exactly N unique examples. This is the minimum
balanced 1:1 unique-data contrast: N opportunity examples and N historical
examples.

Let the three eligible source domains be sorted by the full SHA-256 digest of

```text
B2.4-PACS-interference-v1|replay-domain-order|seed|i|source-domain
```

For a given N, assign `floor(N/3)` samples to every source domain and assign
the `N mod 3` remaining samples to the first domains in that fixed order. Thus
the quotas are permutations of:

| N | Three source-domain quotas |
| ---: | --- |
| 25 | `(9,8,8)` |
| 50 | `(17,17,16)` |
| 100 | `(34,33,33)` |

Within a source domain, sort all eligible F0 training IDs by the full SHA-256
digest of

```text
B2.4-PACS-interference-v1|replay|seed|i|source-domain|sample-id
```

and take the quota-length prefix. Selection does not inspect class labels,
model outputs, or validation results. Since every source-domain quota grows
monotonically, the N=25, 50, and 100 buffers are nested.

Each materialized buffer stores the ordered sample IDs, relative paths,
ground-truth labels, source domains, N, seed, intervention domain, parent F0
checkpoint hash, split-manifest hash, construction rule, payload hash, and
buffer hash. The same buffer artifact is used by REP and REP2.

## 6. Exact update dose and minibatches

B2.4 inherits B2.3's batch size 16 and reference dose

\[
T_N=3\left\lceil\frac{N}{16}\right\rceil,
\qquad E_N=16T_N.
\]

An exposure is one selected sample entering one forward/backward pass; one
batch produces one optimizer step. Consequently:

| N | T_N | E_N |
| ---: | ---: | ---: |
| 25 | 6 | 96 |
| 50 | 12 | 192 |
| 100 | 21 | 336 |

The exact treatments are:

| Endpoint | Steps | Batch composition | Opportunity exposures | Replay exposures | Total exposures |
| --- | ---: | --- | ---: | ---: | ---: |
| STD | `T_N` | 16 from `O_i` | `E_N` | 0 | `E_N` |
| O50 | `T_N` | 8 informative `O_i` + 8 exact duplicates | `E_N/2` informative (`E_N` processed slots) | 0 | `E_N` |
| REP | `T_N` | 8 from `O_i` + 8 replay | `E_N/2` | `E_N/2` | `E_N` |
| REP2 | `2T_N` | 8 from `O_i` + 8 replay | `E_N` | `E_N` | `2E_N` |

Thus STD, O50, and REP have exactly equal optimizer steps, batch size, and
total processed batch slots. O50 and REP have exactly the same `E_N/2`
informative opportunity exposures. In O50 each informative augmented tensor
is copied once to fill the other half-batch; a copy consumes compute but is not
counted as a new exposure to opportunity information. In REP those duplicate
slots are replaced by historical replay. REP2 restores the full STD
opportunity exposure dose and adds an equally large replay dose; it has
exactly twice STD's steps and total exposures, rather than an informal or
minibatch-dependent approximation.

All N unique opportunity and all N unique replay samples occur at least once
in REP for every declared N because `E_N/2 >= N`.

### 6.1 Ordered schedules

The stored B2.3 opportunity exposure sequence is reused. O50 and REP consume
the same first `E_N/2` entries, partitioned into the same ordered groups of
eight. REP2 consumes all `E_N` entries. This preserves the same sample-level
exposure ordering used by STD, although batch grouping is necessarily
different.

For each step, construct the eight opportunity tensors once, using the exact
B2.3 sample IDs, exposure indices, augmentations, and labels. Place these
original tensors in the same half and positions in O50 and REP. In O50, fill
the other eight positions by copying each already-augmented tensor and label
once, in the same within-half order. A duplicate is not transformed again,
does not receive a new augmentation seed, and does not increment the sample's
informative exposure index. In REP, fill those same positions with replay.
The opportunity half is first on odd one-indexed steps and second on even
steps in both methods.

Replay samples are cycled deterministically. Within each source domain and
cycle, order by the full SHA-256 digest of

```text
B2.4-PACS-interference-v1|replay-schedule|seed|i|N|source-domain|cycle|sample-id
```

At each mixed step, the replay half-batch contains eight samples drawn from a
single merged replay stream formed by round-robin interleaving the three
source-domain sequences in their fixed replay-domain order. Across every
prefix, source-domain exposure counts differ by at most one. The complete
ordered O50, REP, and REP2 schedules and their hashes are stored.

REP is the checkpoint immediately after step `T_N`; REP2 continues without
optimizer reset through step `2T_N`.

## 7. Transforms and deterministic stochasticity

STD remains bit-for-bit the B2.3 state. O50, REP, and REP2 use B2.3's training
transform: random resized crop to 224 with scale 0.8–1.0, horizontal flip with
probability 0.5, tensor conversion, and ImageNet normalization. VALIDATION
uses resize to 256, center crop to 224, tensor conversion, and ImageNet
normalization. Data-loader workers are zero.

The B2.3 derived training seed for `(seed,N)` is reused independently for the
O50 and mixed trajectories. Their initial model, fresh optimizer, and initial
RNG state are identical. For every opportunity sample/exposure shared by O50
and REP, the sample ID, exposure index, tensor position, label, and exact B2.3
stateless augmentation seed are identical. Shared opportunity entries also
occupy the same batch positions, so per-step model-stochastic RNG draws for
those positions are aligned. Replay augmentation seeds use

```text
SHA256(B2.4-PACS-interference-v1|augmentation|seed|N|sample-id|exposure-index)
```

with the same 63-bit derivation rule as B2.3. Per-step Torch seeds in O50 and
REP are identical and, for the first `T_N` steps, equal B2.3's
`(seed,N,step)` seeds; the same rule extends REP2 through steps
`T_N+1,...,2T_N`. Python, NumPy, and Torch seeds, deterministic settings,
thread count, library versions, schedules, optimizer state at REP, and RNG
continuation state are stored.

## 8. Competence and interference variables

All states are evaluated once on the same complete VALIDATION IDs. Let
`S_k(F)` be validation balanced accuracy on domain k. For
`m in {STD,O50,REP,REP2}` define

\[
\Delta S_{i\to k}^{m}=S_k(F_i^m)-S_k(F_0),
\]

\[
\Delta S_{local}^{m}=\Delta S_{i\to i}^{m},
\qquad
\Delta S_{cross}^{m}=\sum_{k\ne i}\Delta S_{i\to k}^{m},
\]

and

\[
I_i^m=-\Delta S_{cross}^m.
\]

The primary causal contrast for replay is REP versus O50:

\[
\Delta I_i=I_i^{REP}-I_i^{O50}.
\]

Interference reduction corresponds to the strict inequality
`Delta I_i < 0`. Numerical zero is classified only at absolute tolerance
`1e-12`; the tolerance does not change a scientific inequality.

The paired local-learning contrast is

\[
\Delta L_i=\Delta S_{local}^{REP}-\Delta S_{local}^{O50}.
\]

The full `(DeltaS_local, DeltaS_cross)` plane and all four competence changes
are retained. Interference reduction is never reported as satisfactory
preservation merely because local learning was removed. No non-inferiority or
practical-equivalence margin is used.

When `DeltaL_i<0`, define recovered cross-domain competence

\[
G_i=\Delta S_{cross}^{REP}-\Delta S_{cross}^{O50}=-\Delta I_i
\]

and local sacrifice `C_i=-DeltaL_i`. Cross-domain recovery exceeds local
sacrifice exactly when `G_i>C_i`, equivalently `G_i+DeltaL_i>0`. This
unweighted competence-coordinate comparison is reported alongside, and never
substituted for, the operational value contrast.

## 9. Future operational value

B2.4 retains B2.3's operational value without modification. For
`c in {0,0.02,0.05,0.10,0.15}` and uniform `p_k=1/4`,

\[
V(F;c)=\sum_k\frac14\max\{S_k(F),S_k(D)-c\},
\]

\[
\Delta V_i^m(c)=V(F_i^m;c)-V(F_0;c).
\]

The primary paired value contrast is

\[
\Delta Q_i(c)=\Delta V_i^{REP}(c)-\Delta V_i^{O50}(c).
\]

Each domain-level contribution to DeltaV and the routing choice `F/D` are
stored. Costs c are analytical valuations of the same learned state and are
not replicates.

STD remains the original B2.3 reference. Report `O50-STD` and `REP-STD`
descriptively to show the consequences of reducing informative opportunity
exposure and of the equal-compute replay mechanism relative to that reference.
REP2 is secondary: report `REP2-STD`, `REP2-O50`, and `REP2-REP` contrasts for
DeltaS, interference, and DeltaV. REP2 assesses whether conclusions change
when the full opportunity dose is restored together with replay; it does not
enter the primary classification.

## 10. Unit of analysis and summaries

The learned case is one `seed × intervention-domain × N` family sharing F0,
D, opportunity, and replay buffer. Comparisons are paired within that family.
There are 60 families and five independent seed realizations per exact
`domain × N` regime.

N prefixes are dependent dose regimes. They are reported separately and may
also enter a predeclared within-seed global summary, but they are never counted
as independent replication. The five c values are reported separately for
value and likewise are not replications.

For seed s define the global summaries over the fixed 12 domain×N cases:

\[
R_s=\frac1{12}\sum_{i,N}(-\Delta I_{s,i,N}),
\qquad
P_s=\frac1{12}\sum_{i,N}\Delta L_{s,i,N},
\]

and, separately for each c,

\[
Q_s(c)=\frac1{12}\sum_{i,N}\Delta Q_{s,i,N}(c).
\]

Exact domain×N seed-sign counts accompany these global summaries. Means,
medians, standard deviations, minima, maxima, and all five seed values are
reported; no inferential significance test is planned for n=5.

## 11. Frozen outcome classification

B2.4 reports a three-part classification rather than collapsing distinct
scientific questions into one label.

### 11.1 Interference reduction

- **POSITIVE:** `R_s>0` in at least 4/5 seeds and `mean_s(R_s)>0`.
- **NULL:** `R_s<=0` in at least 4/5 seeds and `mean_s(R_s)<=0`.
- **INCONCLUSIVE:** neither condition holds.

The same rule is reported descriptively for each exact domain×N regime, but a
favorable isolated regime cannot replace the global primary classification.

### 11.2 Effect on local learning

- **POSITIVE:** `P_s>0` in at least 4/5 seeds and `mean_s(P_s)>0`.
- **NULL:** `P_s<=0` in at least 4/5 seeds and `mean_s(P_s)<=0`.
- **INCONCLUSIVE:** neither condition holds.

No margin is applied. NULL here means that replay does not produce a
reproducible favorable local-learning effect relative to O50; the report must
state separately whether the observed direction is zero or adverse. For every
case with `DeltaL_i<0`, report `G_i`, `-DeltaL_i`, and whether
`G_i+DeltaL_i>0`, so an interference reduction cannot conceal the amount of
local competence sacrificed.

### 11.3 Future-value improvement

For each predeclared c separately, using REP minus O50:

- **POSITIVE:** `Q_s(c)>0` in at least 4/5 seeds and `mean_s Q_s(c)>0`;
- **NULL:** `Q_s(c)<=0` in at least 4/5 seeds and `mean_s Q_s(c)<=0`;
- **INCONCLUSIVE:** neither condition holds.

There is no post-hoc selection of the most favorable c and no count over c as
replication. Any positive statement names the cost regime explicitly. A
compact overall descriptor may say “positive at all five costs” only if every
one of the five separately classified costs is POSITIVE.

### 11.4 Interpretation map

- **Result A:** interference reduction is POSITIVE and the local-learning
  effect is POSITIVE. This is evidence that replacing redundant opportunity
  exposures with historical replay reduces the B2.3 interference pattern
  without a local-learning sacrifice in the declared aggregate comparison.
- **Result B:** interference reduction is POSITIVE but the local-learning
  effect is NULL. Report whether recovered cross-domain competence exceeds
  local sacrifice. This is a stability/plasticity trade-off, not by itself
  sufficient evidence of improved development.
- **Result C:** interference reduction is NULL, or INCONCLUSIVE without any
  exact domain×N regime reaching the positive seed criterion. The minimal
  historical replay tested does not reproducibly control the B2.3 pattern.
- **Result D:** in addition to the interference/local classifications, future
  value is POSITIVE at one or more explicitly named predeclared c values. This
  is evidence that interference control changes future development value in
  those cost regimes.

No classification uses portfolio rescue.

## 12. Interpretation limits of the dose contrasts

The primary REP-versus-O50 comparison holds fixed F0, optimizer, training
seed, steps, batch size, processed slots, informative opportunity IDs,
opportunity exposure indices, opportunity augmentations, tensor positions,
and per-step RNG. Its intervention replaces the eight duplicated-opportunity
slots in each O50 batch with eight historical replay slots. It therefore
identifies the effect of that specific replay substitution relative to an
opportunity-duplication control. It does not establish that every replay
policy or replay ratio has the same effect.

STD retains twice the informative opportunity exposure of O50 and REP. The
STD comparisons are references to the original B2.3 mechanism, not the causal
replay contrast. REP2 restores the full STD opportunity dose while adding
replay, but also doubles total steps and exposures. It is a secondary dose
contrast and cannot by itself identify a compute-free replay effect.

Likewise, competence changes cannot identify catastrophic forgetting,
pseudo-label noise, optimization failure, or another latent learning cause.

## 13. Required outputs and integrity checks

For every learned case store:

- seed, domain, N, method, parent F0 and D hashes;
- opportunity and replay-buffer hashes and exact ordered IDs;
- labels and label provenance (`B2.3_D_pseudo` or `F0_observed_ground_truth`);
- training seed, RNG scheme, ordered schedule and hash;
- steps, batch size, per-source exposures, unique examples, optimizer, and
  transforms;
- checkpoint hash and complete four-domain VALIDATION vector;
- all DeltaS components, local/cross sums, I, DeltaI, DeltaL, G, and local
  sacrifice;
- for each c, V, DeltaV, domain contributions, routes, and DeltaQ;
- REP2 dose contrasts;
- elapsed timing and status as operational metadata outside scientific hashes.

Before analysis verify:

1. exactly five seeds, four domains, three N values, and 60 complete families;
2. exact B2.3 F0, D, split, opportunity, STD, and VALIDATION hashes;
3. every replay ID belongs to its parent F0 training IDs and one of the other
   three domains;
4. replay is disjoint from all opportunities, VALIDATION, and TEST;
5. exact N, nested-prefix, quota, label-provenance, and replay-hash rules;
6. STD, O50, and REP each have `T_N` steps, batch 16, and `E_N` processed
   slots;
7. O50 and REP contain identical opportunity IDs, exposure indices,
   augmentations, positions, and RNG for all `E_N/2` informative opportunity
   exposures;
8. every O50 filler is an exact tensor/label duplicate, with no new transform
   or informative-exposure increment;
9. REP and REP2 are the same trajectory, with endpoints at `T_N` and `2T_N`;
10. exact opportunity/replay exposures in the dose table;
11. every state starts from the same F0 and no developed state is used as an
   independent parent;
12. complete VALIDATION only, no TEST access, no NaN, no duplicates, and exact
    reconstruction of every reported quantity.

Any failed integrity, provenance, completeness, deterministic-reproduction,
or TEST-closure check makes the affected experiment **INVALID** and prevents
POSITIVE/NULL/INCONCLUSIVE classification.

## 14. Expected computation

B2.3 supplies 60 frozen STD states and their scores. B2.4 adds 60 independent
O50 trajectories and 60 mixed trajectories, each of the latter producing REP
and REP2 endpoints. Thus the planned new training is 120 fits; it adds 180
VALIDATION evaluations. Including the reused STD vectors gives 240
derived-state vectors and `60 × 4 × 5 = 1,200` method-specific c-valuations.

Dry-run, restart, incremental manifests, hash validation, CPU enforcement,
and explicit TEST guards are required at implementation time. This section
does not authorize implementation or execution.

## 15. Permitted and prohibited claims

A valid Result A permits the narrow statement that the tested equal-compute
replay development mechanism reproducibly reduces cross-domain interference
relative to its matched O50 control and improves local learning in the
declared directional comparison. A valid Result D additionally permits a
statement about future operational value at the named c regimes.

B2.4 cannot establish:

- portfolio rescue, Gamma, or superiority of accumulated opportunities;
- effects of replay ratios or baselines other than the declared O50
  substitution;
- the latent cause of cross-domain interference;
- an ex-ante policy, complete closed loop, or universal HLS superiority;
- TEST generalization, results outside PACS, or novelty.

## 16. Stopping and amendment rules

After this document is frozen, do not change seeds, N, replay size, sample
selection, dose, schedules, c grid, classification rules, or interpretation
rules.

Stop before scientific analysis if a parent artifact is incompatible, replay
construction fails, TEST is accessed, a scheduled dose differs, a required
state is missing, or deterministic provenance cannot be verified. Engineering
repairs may resume only from valid artifacts and must be documented. Any
scientific amendment requires a versioned protocol change made before outcome
inspection; otherwise the affected analysis is explicitly exploratory.
