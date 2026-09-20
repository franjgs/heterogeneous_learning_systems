# B1 — Empirical interaction pilot

Status: exploratory pilot. Results are `OBSERVED`; they are not a test of
novelty, RQ0, or superiority of joint management.

## Question

On a small real multiclasse classification problem, do independent
development opportunities produce measurable

```text
Gamma_ij = V(F_ij) - V(F_i) - V(F_j) + V(F_0)
```

without putting complementarity into the value function? The pilot also checks
whether the sign and magnitude of Gamma vary with transfer budget, whether
competence regions defined before transfer are stable, and whether developing
one region changes performance on other regions.

## Fixed protocol

The data are `sklearn.datasets.load_digits`, loaded offline. Each seed creates
stratified `train`, `transfer`, `validation`, and `test` splits with fractions
0.4/0.2/0.2/0.2. The test split is held out from clustering, transfer
selection, and hyperparameter choice.

Fast `F` is `LogisticRegression(solver="lbfgs", max_iter=1000)`. Deep `D` is
`RandomForestClassifier(n_estimators=80, n_jobs=1)`. Both are trained on the
same TRAIN split. “Deep” is only an operational label here; it does not mean a
deep neural network.

For each true class, the validation profile is the normalized row of the
`F_0` confusion matrix. Four deterministic agglomerative clusters of these ten
profiles define the competence regions. D is not used to define them. A
random-group control uses the same group sizes after an independent seeded
permutation of class labels.

For each group and budget `B` in `{5,10,20,40}`, the transfer pool provides
examples from that group. D supplies hard pseudo-labels (`argmax` of D's class
probabilities) in the primary scenario. A true-label transfer is retained as
a diagnostic control only. Every `F_i` and `F_ij` is retrained from the same
TRAIN base with the same algorithm, hyperparameters, and seed; pairs use the
union of the two B-example opportunities and are not sequential updates.

The primary value is test balanced accuracy. Competence-level scores are
balanced accuracy restricted to each pre-defined class group. The resulting
vectors `Delta^(i)` are diagnostic only. Gamma is summarized per seed, pair,
budget, grouping, and label mode; bootstrap intervals describe the pilot and
are not significance claims.

## Controls and outputs

The true-label and random-group scenarios are controls, not alternative HLS
claims. CSV files preserve individual seed results; JSON records the complete
configuration and summary; PNG files are diagnostic heatmaps/distributions.
The executable is `run.py`. From the repository root:

```text
python experiments/pilots/b1_empirical_interaction/run.py
```

Generated outputs are under `results/pilots/b1_empirical_interaction/`:
`model_results.csv`, `gamma.csv`, `delta.csv`, `competence_assignments.csv`,
`stability.csv`, `summary.csv`, `summary.json`, and diagnostic figures.

## Observed pilot result

The executed run used all ten configured seeds, all four budgets, and produced
1,620 model fits in about 85 seconds. Mean validation/test balanced accuracy
was 0.9543/0.9533 for `F_0` and 0.9627/0.9652 for `D`. Competence clustering
stability was ARI mean 0.1330 (SD 0.2075, range -0.1638 to 0.6828), so the
pre-transfer regions were not highly stable across seeds.

For the primary competence/pseudo-label scenario, the aggregate Gamma means
(SDs) over six pairs and ten seeds were: `B=5` 0.000324 (0.001842), `B=10`
-0.000388 (0.002334), `B=20` -0.000825 (0.003259), and `B=40` -0.000458
(0.004038). Both signs occurred across pairs/seeds; the largest primary
observation was +0.008422 and the smallest was -0.014057. The control scenarios
showed comparable small magnitudes, including competence/true-label means
0.000552, 0.000492, 0.000162, -0.000906 and random/pseudo means -0.000132,
-0.000591, -0.000106, -0.001133 for `B=5,10,20,40` respectively.

The predeclared descriptive classification is **WEAK / UNSTABLE INTERACTION**:
Gamma is measurable in individual observations and changes sign, but its means
are comparable with seed variability and the controls do not isolate a strong
competence-specific pattern. This is an exploratory observation, not a
significance claim. The run emitted no model-convergence or metric warnings;
the shell environment printed external Matplotlib/fontconfig cache warnings.

## Interpretation limits

The pilot does not introduce `H_i`, costs, beta, routing decisions, or a
designed complementary objective. A nonzero Gamma can reflect genuine
cross-effects, pseudo-label noise, finite-sample variation, or interference.
Ten seeds are descriptive rather than a high-powered statistical study. The
pilot does not establish novelty, generality, or superiority of any
architecture.
