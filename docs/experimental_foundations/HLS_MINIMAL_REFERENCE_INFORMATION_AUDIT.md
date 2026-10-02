# HLS Minimal Reference Information Audit

**Status:** Canonical closed audit for the declared Minimal Reference Scenario scope  
**Scope:** Information, algebraic, and numerical audit of the existing 2-worker × 2-task × 2-period scenario; not a new scenario or theory  
**Evidence:** `results/foundations/minimal_reference_information_audit/summary.json` and its manifest  
**Implementation:** `src/hls/minimal_reference_information_audit.py`

## 1. Purpose and boundary

After validating the Minimal Reference Scenario, the question became:

> What is the minimum future-facing information needed to preserve the decision value of jointly considering operation and competence evolution?

This audit separates **value reconstruction** from **decision preservation**.
It asks how much future-facing information is needed to reproduce the oracle
choice in the fixed scenario; it does not propose a new DP, ADP, or HLS
solution method.  All results retain the existing physics, actions `E/D`,
2×2×2 horizon, and Phase-V family.

Every representation receives the common present decision information
`(S0, P0, beta)` needed to evaluate `L`.  Its `phi` component measures only
additional future-facing information.

## 2. First information audit

The initial candidates were constructed without using `G` or `V1`:

| Representation | Additional future-facing information |
| --- | --- |
| `phi0` | None. |
| `phi1` | Total action-induced learning for `E` and `D`, from `F(S,a)-S`. |
| `phi2` | Localized `DeltaS(E), DeltaS(D)`. |
| `phi3` | Localized `DeltaS(E), DeltaS(D)` and `P1`; no terminal assignment or `V1` is evaluated while constructing it. |
| `phi_oracle` | Control only: `G=V1(S1(D))-V1(S1(E))`. It is never a feature of `phi0`--`phi3`. |

For each induced information class, the audit computes the best action that a
rule unable to distinguish worlds inside that class can take.  This is an
information-constrained ceiling, not trained prediction.

| Representation | Classes | Incompatible decision collisions | Inevitable regret | Worst regret | Oracle value recovered over myopic |
| --- | ---: | ---: | ---: | ---: | ---: |
| `phi0` | 11,520 | 1,923 | 130.8636 | 0.1400 | 14.39% |
| `phi1` | 46,080 | 3,213 | 73.1274 | 0.1025 | 52.16% |
| `phi2` | 46,080 | 3,213 | 73.1274 | 0.1025 | 52.16% |
| `phi3` | 221,184 | 0 | 0 | 0 | 100% |
| `phi_oracle` | 206,199 | 0 | 0 | 0 | 100% |

Two results constrain their interpretation.

1. `phi1` and `phi2` induce exactly the same partition in this family.  This
   does **not** establish that learning placement is structurally irrelevant;
   it is a property of the declared family and common information.
2. `phi3` has one class per Phase-V world.  Its 100% result demonstrates
   sufficiency by complete grid discrimination, not a compact representation
   or an executable policy.

Two minimal collision pairs make the missing information concrete.  Under the
same `S0`, `P0`, `P1=(0,1)`, and `beta=.875`, changing only the learning scale
from `1.0` to `1.5` changes `G` from `.09` to `.125` and oracle action from
`E` to `D`; `phi0` cannot distinguish them.  With the same state, present
demand, `beta=.875`, and scale `1.5`, changing `P1` from `(0,1)` to
`(.25,.75)` changes `G` from `.125` to `.1009375` and oracle action from `D`
to `E`; both `phi1` and `phi2` collide on this pair.  Future operational
conditions therefore remain necessary in those representations.

## 3. Algebraic reduction of the fixed model

Write

$$
S_0=\begin{pmatrix}a&b\\c&d\end{pmatrix},\qquad P_1=(p,1-p).
$$

The existing transitions provide, without calling `V1`, the four increments

$$
\alpha=S_E[0,A]-a,\quad \epsilon=S_E[1,B]-d,\quad
\gamma=S_D[0,B]-b,\quad \delta=S_D[1,A]-c.
$$

Define

$$
X=pa+(1-p)d,\qquad Y=(1-p)b+pc,\qquad h=X-Y,
$$

$$
u=p\alpha+(1-p)\epsilon,\qquad
v=(1-p)\gamma+p\delta.
$$

Here `h` is the pre-development organizational advantage of `E` under future
operational conditions; `u` is the future operational value of development
induced by `E`; and `v` is the corresponding value induced by `D`.

For this fixed 2×2×2 model, direct terminal-assignment algebra gives

$$
G=\max(h,v)-\max(h+u,0),
$$

and the existing two-stage decomposition remains

$$
\Delta J=-L+\beta G.
$$

This is a reduction of the specified model, not new HLS mathematics.  The
Phase-V numerical validation found maximum residuals
`3.33e-16` for `G` and `6.25e-16` for `DeltaJ`.

### Algebraic regions

| Region | Condition | Result | Phase-V population |
| --- | --- | --- | ---: |
| A interior | `h > v` | `G=-u` | 16,317 |
| B interior | `h < -u` | `G=v` | 3,843 |
| C interior | `-u < h < v` | `G=v-u-h` | 200,268 |
| Boundary | `h=-u` | Boundary formula | 756 |
| Boundary | `h=v` | Boundary formula | 0 |

Region C has the structural form

$$
G=(v-u)-h:
$$

the differential useful development is offset by pre-existing organizational
advantage.  Its predominance is a property of this grid, not a prevalence
claim.

## 4. Ablations of `(h,u,v)`

| Representation | Classes | Incompatible collisions | Inevitable regret | Worst regret | Oracle value recovered | Determines `G` on Phase-V grid |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `(h,u,v)` | 219,744 | 0 | 0 | 0 | 100% | Yes |
| `h` | 55,296 | 5,188 | 124.3890 | 0.1300 | 18.63% | No |
| `u` | 192,960 | 990 | 21.3105 | 0.07875 | 86.06% | No |
| `v` | 213,984 | 408 | 7.0269 | 0.05250 | 95.40% | No |
| `(h,u)` | 218,304 | 219 | 3.8138 | 0.05000 | 97.51% | No |
| `(h,v)` | 215,424 | 329 | 5.9756 | 0.05250 | 96.09% | No |
| `(u,v)` | 219,564 | 0 | 0 | 0 | 100% | No |
| `(h,v-u)` | 213,264 | 0 | 0 | 0 | 100% | Yes |
| `v-u` | 200,610 | 237 | 1.5563 | 0.02625 | 98.98% | No |
| `h+u` | 214,497 | 464 | 7.4039 | 0.07500 | 95.16% | No |

Thus `v-u` alone recovers 98.98% of oracle value in this audited family, but
is not decision-sufficient.  `(u,v)` preserves the Phase-V decision yet has
180 classes in which `G` varies (maximum span `.095`), so decision preservation
does not imply value reconstruction.  `(h,v-u)` determines `G` on the grid,
but this is a finite-family observation, not a general reduction proof.

## 5. Scope beyond the grid

The exact continuous/adversarial campaign implemented for this audit attacks
the scalar compression below.  It does **not** contain a separate continuous
collision audit for `(h,v-u)` or `(u,v)`.  Consequently, the evidence supports
neither their general sufficiency nor a documented counterexample to either
representation outside Phase V.  Their 100% grid results remain discretized
family properties only.

This corrects a possible over-reading of the Phase-V table: a collision-free
partition on that grid is not a structural universal claim about the model.

## 6. Scalar decision compression

For the stated domain `L>0` and `beta>0`, set

$$
c=L/\beta.
$$

The decision condition can be written concisely as

$$
D\ \text{optimal}
\iff G>c
\iff v>c\ \text{and}\ v-u-h>c
\iff \min(v,v-u-h)>c.
$$

Define

$$
m=\min(v,v-u-h).
$$

Then, under those assumptions,

$$
\begin{aligned}
D\ \text{optimal}&\iff \beta m>L,\\
E,D\ \text{tie}&\iff \beta m=L,\\
E\ \text{optimal}&\iff \beta m<L.
\end{aligned}
$$

`(h,u,v)` reconstructs `G` in the 2×2×2 algebra; `m` is a decision
compression under the stated assumptions.  In particular, `m` is not globally
equal to `G`, so it is not a relabelled continuation value.  The audit does
not claim that it is a unique minimum statistic.

## 7. Computational validation and numerical attack on `m`

### Phase V

On the formal domain `L>0,beta>0`, 141,280 Phase-V worlds gave:

| Exact oracle decision | Agreement with scalar rule |
| --- | ---: |
| `E` | 137,109 |
| `D` | 4,048 |
| tie | 123 |
| disagreement | 0 |

This validates the scalar decision rule on the declared grid at the canonical
decision tolerance `1e-12`.  The unrestricted 221,184-world observational
control has 173 disagreements outside that formal domain and is not used to
extend the claim.

### Continuous same-model campaign

The reproducible continuous campaign sampled 100,000 worlds of the same
diminishing-learning model: 50,000 uniform, 30,000 edge/saturation, and
20,000 demand/beta-extreme worlds.  Of these, 47,654 were in `L>0,beta>0`.

| Exact oracle decision | Agreement with scalar rule |
| --- | ---: |
| `E` | 44,214 |
| `D` | 3,413 |
| tie | 20 |
| disagreement | 7 |

The seven disagreements occur at numerical extremes: near-saturated or
near-zero competences, extreme demand, cancellation in `v-u-h`, and large
`beta` amplifying a double-precision residue.  They are failures of numerical
robustness of direct scalar evaluation, not a contradiction of the symbolic
equivalence in exact arithmetic.  One reproducible record is:

```text
S0 = ((3.302863187436348e-10, 1.4340251260771853e-10),
      (0.9999999998263003, 1.7827303253781281e-10))
P0 = (0, 1); P1 = (1e-12, 1-1e-12)
beta = 1e6; learning_scale = 10
L = 3.487051993009429e-11
h = 3.387051993056341e-11
u = .9999999998217269; v = .9999999998555975
m = 5.3082398405930653e-17
DeltaJ_m = +1.8211878475836364e-11; DeltaJ_exact = -3.487051993009429e-11
```

### Adversarial controls

Interior attacks found 1,000 formal cases in each of A, B, and C, with zero
disagreements in every region.  Algebraic boundary perturbations produced 462
formal `h=v` cases and 238 formal `h=-u` cases, again with zero disagreements.

Decision-boundary worlds used `beta=L/m` where `m>0`, with relative
perturbations `±1e-4`, `±1e-8`, and `±1e-12`.  Among 700 evaluations there
were three disagreements, all at relative perturbation `1e-12`; they are
again tolerance/cancellation effects at the double-precision limit.  The
algebraic and decision boundaries are distinct objects.

Explicit edge controls for `u=0`, `v=0`, `h=0`, zero learning scale, one or
multiple saturations, `P1=(1,0)`, `(0,1)`, and `(.5,.5)`, small positive `L`,
small positive `beta`, and large `beta` all agreed in their recorded cases.

## 8. Findings and non-claims

The audit establishes, within its stated evidence:

1. Full future state/value information is unnecessary in the minimal model
   for preserving the Phase-V decision.
2. Raw amount of competence development is insufficient.
3. Development usefulness is action-dependent and must be interpreted through
   future operational organization.
4. Differential useful development `v-u` is highly informative in Phase V,
   but is not decision-sufficient there without additional information.
5. The exact 2×2 model separates organizational position `h`, useful
   development under `E` (`u`), and useful development under `D` (`v`).
6. For `L>0,beta>0`, these enter the symbolic decision compression
   `m=min(v,v-u-h)`.
7. The resulting direction is not generic value-function approximation: it is
   testing whether compact estimates of organizational value from
   action-induced competence development retain useful decision value in
   richer HLS settings.

These results do **not** establish new mathematical theory, a new class of
systems, general informational minimality, sufficiency of `m` outside 2×2×2,
HLS superiority, real prevalence of S2/S3, persistence of the 98.98% result
in larger settings, or general sufficiency of a scalar signal for HLS.

## 9. Closed microscope question and next question

The information audit of the existing minimal-reference microscope is closed:
the retained record includes its positive grid results, its nulls, and its
numerical robustness limit.  It does not authorize a new mechanism or an
expanded scenario.

The next question is future work, not a current result:

> What is the cheapest approximation to the organizational value of
> action-induced competence development that retains most of the oracle
> decision value once the problem is no longer exactly reducible as 2x2x2?
