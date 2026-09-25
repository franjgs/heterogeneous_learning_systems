# HLS Scientific Checkpoint after B2.3

## 1. Scientific question

B2.3 asked:

> Can individually unprofitable learning opportunities become jointly
> profitable when accumulated and used as a development portfolio?

The tested mechanism was

```text
operation
-> generation of learning opportunities
-> accumulation
-> joint development
-> competence change
-> future operational value.
```

This checkpoint reports the frozen B2.3 experiment. It does not change the
theory, open TEST, claim novelty, or establish a general result beyond the
PACS B2.3 system.

## 2. Design and integrity

B2.3 used PACS, CPU execution, VALIDATION-only evaluation, five seeds,
`N={25,50,100}`, four fixed domains and six pairs. The analytical grid was
`c={0,0.02,0.05,0.10,0.15}`, `B={1,2,5,10}`, and `kappa=0`. TEST remained
closed.

Each seed had one common Fast base state `F0` and one Deep state `D` for all N
and pairs. Immutable opportunity artifacts stored sample IDs, hard teacher
labels, RNG/provenance data, and hashes. Every singleton `F_i` and joint
`F_ij` loaded the same seed-specific `F0`; joint states reused the exact
opportunity artifacts used by their singleton counterfactuals. No derived
state was trained sequentially from another derived state.

The frozen dose was

```text
T_N = 3 ceil(N/16)
E_N = 16 T_N.

F0       = (0, 0)
F_i      = (E_N, 0)
F_j      = (0, E_N)
F_ij     = (E_N, E_N)
F_ij^CM  = (E_N/2, E_N/2).
```

The primary joint endpoint continued one balanced 8+8 trajectory for `2T_N`
steps. Its midpoint `F_ij^CM` used the same total compute as a singleton and
was stored as a secondary compute-dose control, not as another fit or as the
primary factorial endpoint.

The completed run contained 160 fits: five F0, five D, 60 singleton, and 90
joint fits. It produced 250 VALIDATION evaluations, 1,800 primary analytical
rows, and 450 compute-matched valuations. The compatibility audit passed all
250 state vectors and verified the common bases, immutable opportunity hashes,
doses, endpoints, dataset revision, CPU device, VALIDATION evaluation, and
TEST closure.

## 3. Frozen quantities and primary event

For domain `i`,

```text
rho_i(c) = S_i(F0) - [S_i(D) - c].
```

With uniform domain weights,

```text
V(F;c) = (1/4) sum_k max{S_k(F), S_k(D)-c}.

DeltaV_i(c)  = V(F_i;c)  - V(F0;c)
DeltaV_j(c)  = V(F_j;c)  - V(F0;c)
DeltaV_ij(c) = V(F_ij;c) - V(F0;c)

Gamma_ij(c) = DeltaV_ij(c) - DeltaV_i(c) - DeltaV_j(c).
```

The opportunity values were

```text
H_i  = -rho_i + B DeltaV_i
H_j  = -rho_j + B DeltaV_j
H_ij = -(rho_i+rho_j) + B DeltaV_ij,
```

with the checked identity

```text
H_ij = H_i + H_j + B Gamma_ij.
```

The strict primary portfolio-rescue event was

```text
rho_i > 0
rho_j > 0
H_i < 0
H_j < 0
H_ij > 0.
```

The frozen `POSITIVE` criterion required this event in at least 3/5 seeds in
the same exact `N × pair × c × B` cell. `NULL` required no rescue in any of
the 1,800 valid primary rows. Any other valid nonempty result was
`INCONCLUSIVE`.

## 4. Primary result

The completed run passed compatibility and produced all expected outputs:

- fits: 160/160;
- VALIDATION evaluations: 250/250;
- primary rows: 1,800/1,800;
- portfolio rescues: 3/1,800;
- unique learned pair states with a rescue: 2/90;
- exact cells reproduced in at least 3/5 seeds: 0/360;
- TEST: closed.

The frozen classification is **INCONCLUSIVE**. Reproducibility was 357 cells
with 0/5 rescue seeds, three cells with 1/5, and zero cells with 2/5 or more.
The three favorable rows were:

| seed | N | pair | c | B | H_ij |
| ---: | ---: | --- | ---: | ---: | ---: |
| 2 | 100 | photo--sketch | 0.15 | 5 | 0.008476 |
| 2 | 100 | photo--sketch | 0.15 | 10 | 0.159951 |
| 4 | 25 | cartoon--sketch | 0.05 | 10 | 0.008684 |

These observations demonstrate that the rescue condition can occur in the
experiment, but they do **not** provide reproducible empirical support for
portfolio rescue.

## 5. Interaction and rescue funnel

Across the 90 learned pair states, `Gamma_learn` had mean 0.146596, median
0.110116, and sample standard deviation 0.125668. It was positive in 89/90
states and negative in 1/90. Its mean increased with development dose:

| N | mean Gamma_learn |
| ---: | ---: |
| 25 | 0.057592 |
| 50 | 0.131414 |
| 100 | 0.250782 |

Thus positive learning interaction was systematic in this experiment and
increased strongly with N.

Operational interaction was smaller, especially when D was cheap:

| c | mean Gamma_oper |
| ---: | ---: |
| 0.00 | 0.011967 |
| 0.02 | 0.017105 |
| 0.05 | 0.026938 |
| 0.10 | 0.056897 |
| 0.15 | 0.083097 |

Routing usually absorbed part of the learning interaction. This masking
decreased as the relative cost of D increased.

The strict primary funnel was:

| cumulative condition | rows |
| --- | ---: |
| `rho_i>0` and `rho_j>0` | 936/1,800 |
| plus `H_i<0` | 927 |
| plus `H_j<0` | 925 |
| plus `Gamma_oper>0` | 917 |
| plus `H_ij>0` | 3 |

The principal bottleneck was not absence of positive interaction: 917/925
relevant rows had positive `Gamma_oper`. In 914 of those 917 rows it was too
small to overcome `-(H_i+H_j)`.

## 6. Singleton behavior and within-run reconstructions

Using only the common-provenance B2.3 artifacts, the 300 singleton valuations
after removing the four analytical B copies had mean `DeltaV=-0.031059` and
median `-0.024569`. There were 273 negative, 15 positive, and 12 numerically
zero valuations. Only 3/60 unique learned singleton opportunities were
favorable in any analytical cell, yielding 11/1,200 favorable singleton rows.

B2.3 therefore independently reproduces the qualitative B2.2 observation
that singleton development usually reduces future operational value. This is
a within-B2.3 reconstruction; independently trained B2.2 model states were
not combined with B2.3.

The corresponding within-B2.3 B2.1-like reconstruction had mean
`Gamma_learn=0.146596` and mean `Gamma_oper` values
`0.011967, 0.017105, 0.026938, 0.056897, 0.083097` for
`c=0,0.02,0.05,0.10,0.15`. It reproduces the qualitative B2.1 mechanism:
learning interaction is strong, operational routing often masks it, and the
masking decreases as D becomes more expensive. Old B2.1 states were not
numerically combined with B2.3 states.

## 7. Compute-matched sensitivity

The secondary dose contrast was

```text
D_dose = DeltaV_ij - DeltaV_ij_CM.
```

Across 450 valuations, its mean was -0.008046 and median -0.005621; 342 values
were negative, 66 positive, and 42 numerically zero.

For seed 2, N=100, photo--sketch, `DeltaV_ij=0.030295`,
`DeltaV_ij_CM=0.001653`, and `D_dose=0.028641`. Its B=5 and B=10 rescues both
ceased to satisfy the event at the compute-matched midpoint. For seed 4,
N=25, cartoon--sketch, the corresponding values were 0.004147, 0.003060, and
0.001087; this rescue also disappeared. Thus 0/3 primary rescues survived the
secondary compute-matched comparison.

This does not invalidate the preregistered opportunity-matched factorial
comparison. It means B2.3 does not establish portfolio rescue under equal
total training compute.

## 8. Strongest mechanistic realization

The seed 2, N=100, photo--sketch state at `c=0.15` had

```text
DeltaV_i   = -0.032102
DeltaV_j   = -0.121503
DeltaV_ij  =  0.030295
Gamma_learn = 0.356488
Gamma_oper  = 0.183900.
```

At B=5, `H_i=-0.266919`, `H_j=-0.644104`, and `H_ij=0.008476`. At B=10,
the values were `-0.427429`, `-1.251617`, and `0.159951`. This is a clean
realization of the theoretical mechanism: the singleton developments are
harmful while the joint state is beneficial through positive interaction. It
occurred in only one seed and therefore is not reproducible evidence.

## 9. Scientific position after B2.3

B2.3 does not establish the dynamic advantage sought in RQ0. It establishes
three robust empirical facts within a common counterfactual provenance:

1. learning opportunities interact positively and systematically;
2. singleton development usually decreases future operational value;
3. operational routing transforms and usually masks much of the learning
   interaction.

Portfolio rescue is possible in the observed system but rare and
non-reproducible under the frozen B2.3 criterion. The empirical bottleneck is
therefore not the existence of interaction, but whether interaction can be
large enough relative to the individual development deficits.

These statements are scoped to PACS B2.3. They do not establish TEST
generalization, an ex-ante policy, a complete closed loop, universal HLS
superiority, superiority over every rich separated architecture, novelty, or
generality beyond this experiment.

## 10. Execution record

Experiment accumulated time was 13:13:16. Recorded fit-category times were:

| category | time |
| --- | ---: |
| F0 | 00:53:33 |
| D | 05:43:49 |
| singleton | 01:38:53 |
| joint | 04:56:52 |

The restart mechanism recovered the execution after interruptions. One was a
NumPy seed-range incompatibility; the fix retained the scientific 63-bit seed
semantics while passing the low 32 bits to NumPy. Completed F0/D and
opportunity artifacts remained valid. A later interruption followed deletion
of the `/private/tmp` PACS image cache. The cache was reconstructed from the
frozen `flwrlabs/pacs` revision
`394113073258ead631f617d2e13bb377c0715c4b`. The completed run then passed the
full compatibility audit.

## Evidence map

- Frozen protocol: `docs/experimental_foundations/B23_PROTOCOL.md`
- Implementation: `experiments/pilots/b23_portfolio_opportunity/`
- Result and classification: `results/pilots/b23_portfolio_opportunity/summary.md`
- Primary rows: `results/pilots/b23_portfolio_opportunity/primary_results.csv`
- Seed reproducibility: `results/pilots/b23_portfolio_opportunity/reproducibility.csv`
- Compute-dose control: `results/pilots/b23_portfolio_opportunity/compute_dose.csv`
- Competence changes: `results/pilots/b23_portfolio_opportunity/competence_changes.csv`
- State scores: `results/pilots/b23_portfolio_opportunity/state_metrics.csv`
- Common provenance and hashes: `results/pilots/b23_portfolio_opportunity/run_manifest.json`
- Bases, opportunities, and derived-state lineage:
  `results/pilots/b23_portfolio_opportunity/base_states.jsonl`,
  `opportunities.jsonl`, and `development_states.jsonl`
- Dataset split IDs: `results/pilots/b23_portfolio_opportunity/split_manifest.csv`
- Timing: `results/pilots/b23_portfolio_opportunity/timing_summary.json`
- Artifact guide: `results/pilots/b23_portfolio_opportunity/AUDIT_README.md`
