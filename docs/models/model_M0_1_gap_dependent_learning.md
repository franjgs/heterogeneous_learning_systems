# M0.1 — Gap-dependent learning response

M0.1 is an analytical extension of M0 that relaxes one assumption only: the competence gain produced by a learning intervention need not be independent of the current quality gap.

M0 remains unchanged. M0.1 is not M1, does not introduce cross-competence effects, interference, forgetting, demand uncertainty, bandit learning, stochastic routing, teacher selection, or a dynamic portfolio beyond M0's persistence horizon. No novelty claim is made.

## 1. Motivation from M0

In canonical M0, the routing margin is `m(delta) = delta - c > 0` and, for a region with fixed gain `g`, the expected intervention value is:

```text
V(delta) = -K + A_H p ell [g + c - delta]_+.
```

The computational M0 sweep held `p`, `ell`, `K`, and `g` equal across regions. Inside the switchable band, `c < delta < c + g`, the frequency-gap score `S(delta) = p delta` increases with `delta`, whereas `V(delta) = -K + A_H p ell (g + c - delta)` decreases with it. The opposite monotonicity observed in that sweep is therefore mathematically correct, but it depends strongly on the fixed-gain assumption.

The previously reported 75.953% strict-rank-reversal fraction is grid geometry under the selected M0 parameter domain. It is neither empirical evidence nor an estimate of real-world prevalence. M0.1 asks which gap-to-learning-response assumptions would make the current gap informative about downstream intervention value.

## 2. Gap-dependent competence gain

M0.1 replaces only the fixed-gain assumption with:

```text
g_z = g(delta_z).
```

For one region, omit the region subscript. In canonical M0, `delta > c`; the intervention value becomes:

```text
V(delta) = -K + A_H p ell [g(delta) + c - delta]_+.
```

Define the post-learning operational surplus of the cheap model over the expensive model, conditional on successful learning, as:

```text
h(delta) = g(delta) + c - delta.
```

The intervention is switchable precisely when `h(delta) > 0`, equivalently when `g(delta) > delta - c`. This retains M0's existing routing interpretation: the expensive model wins before learning and the cheap model wins after a successful intervention.

## 3. Local monotonicity with constant learnability

Consider a strictly switchable interval, so `h(delta) > 0` throughout it. The positive-part operator is then inactive:

```text
V(delta) = -K + A_H p ell [g(delta) + c - delta].
```

If `p`, `ell`, `K`, `c`, and `A_H` are constant with respect to `delta`, differentiation gives:

```text
V'(delta) = A_H p ell [g'(delta) - 1].
```

For positive `p` and `ell`, value decreases, is locally constant, or increases with gap according as `g'(delta)` is less than, equal to, or greater than one. Meanwhile, `S(delta) = p delta` has derivative `S'(delta) = p > 0`. Thus the frequency-gap score always favours larger gaps at fixed frequency, while intervention value favours larger gaps only when conditional competence gain grows faster than one-for-one with the gap.

## 4. Proposition M0.2 — Gap-value monotonicity under gap-dependent gain

Within a strictly switchable interval of canonical M0, suppose `g(delta)` is differentiable and `p`, `ell`, `K`, `c`, and `A_H` are constant. Then:

```text
V'(delta) = A_H p ell [g'(delta) - 1].
```

Consequently, for `p > 0` and `ell > 0`, downstream intervention value is locally decreasing, constant, or increasing with the current quality gap when `g'(delta) < 1`, `g'(delta) = 1`, or `g'(delta) > 1`, respectively. Since `S'(delta) = p > 0`, frequency-gap and intervention-value orderings are locally opposed whenever `g'(delta) < 1`.

**Derivation.** On a strictly switchable interval, substitute `h(delta) = g(delta)+c-delta` into the M0 value expression and differentiate. The derivative of `h` is `g'(delta)-1`; the stated result follows after multiplication by the constant non-negative factor `A_H p ell`.

This is a local result, restricted to a strictly switchable interval with constant learnability and cost. It is not a claim about realistic distillation behaviour.

## 5. Linear response family

Let the conditional gain be `g(delta) = a + b delta`. Then:

```text
V(delta) = -K + A_H p ell [a + c + (b - 1) delta]_+.
```

Within the switchable region, value decreases for `b < 1`, is independent of gap for `b = 1`, and increases for `b > 1`. The switching condition is:

```text
a + c + (b - 1) delta > 0.
```

For `b < 1`, this requires `delta < (a+c)/(1-b)`, so a finite maximum switchable gap appears. For `b = 1`, switchability requires `a+c > 0`; equality is the non-switchable boundary. For `b > 1`, the algebraic condition is `delta > -(a+c)/(b-1)`, subject to the canonical domain and any other admissibility constraints. No further behavioural interpretation follows from this linear family alone.

## 6. Proportional gap recovery

Consider `g(delta) = rho delta`, with `0 <= rho <= 1`: a successful intervention recovers a fraction `rho` of the current quality gap. Then:

```text
V(delta) = -K + A_H p ell [c - (1-rho) delta]_+.
```

For `0 <= rho < 1`, switchability requires `delta < c/(1-rho)`. Within that region:

```text
V'(delta) = -A_H p ell (1-rho) < 0,
```

provided `p > 0` and `ell > 0`. Thus, even proportional gain does not make larger gaps more valuable under M0 when less than the full gap is recovered. For `rho = 1`, `g(delta) = delta` and:

```text
V(delta) = -K + A_H p ell c.
```

The downstream value is then independent of the quality gap. This is exactly the perfect-quality-matching special case already recorded in M0. At the equality boundaries of these conditions, the relevant derivative or switching surplus is zero, so strict claims should not be inferred.

## 7. Gap-dependent learnability

Now allow `ell = ell(delta)`, without specifying how this quantity would be learned. On a strictly switchable interval:

```text
V(delta) = -K + A_H p ell(delta) [g(delta)+c-delta].
```

Using `h(delta) = g(delta)+c-delta`, differentiation yields:

```text
V'(delta) = A_H p [ell'(delta) h(delta) + ell(delta) (g'(delta)-1)].
```

This is the central M0.1 expression before training cost is allowed to vary. For `p > 0`, `ell(delta) > 0`, and `h(delta) > 0`, larger gaps have locally larger value exactly when:

```text
ell'(delta) h(delta) + ell(delta) [g'(delta)-1] > 0,
```

or equivalently:

```text
ell'(delta) / ell(delta) > [1-g'(delta)] / h(delta).
```

If `g'(delta) < 1`, learnability must increase sufficiently rapidly with gap to compensate for the larger routing margin that must be overcome. M0.1 makes no empirical assertion about whether learnability rises or falls with gap.

## 8. Corollary M0.2 — Opposite monotonicity under non-increasing learnability

Within a strictly switchable interval, suppose `p > 0`, `ell(delta) > 0`, `ell'(delta) <= 0`, and `g'(delta) <= 1`. Then `V'(delta) <= 0`. If either derivative inequality is strict in a term with positive multiplier, then `V'(delta) < 0`.

**Derivation.** Here `h(delta) > 0`. Both terms in the preceding derivative are non-positive: `ell'(delta) h(delta) <= 0` and `ell(delta)[g'(delta)-1] <= 0`. Strict negativity follows when either term is strictly negative. As `S'(delta)=p>0`, the two scores cannot share a strictly increasing dependence on gap under these assumptions. Equality cases permit a locally constant intervention value rather than strict opposition.

## 9. Gap-dependent training cost

Finally, let training cost vary as `K = K(delta)`. On a strictly switchable interval:

```text
V(delta) = -K(delta) + A_H p ell(delta) [g(delta)+c-delta].
```

The most general differential expression considered in M0.1 is:

```text
V'(delta) = -K'(delta) + A_H p [ell'(delta) h(delta) + ell(delta) (g'(delta)-1)].
```

If `K'(delta) >= 0`, `ell'(delta) <= 0`, and `g'(delta) <= 1` on a strictly switchable interval with `p > 0` and `ell(delta) > 0`, then `V'(delta) <= 0`. The inequality is strict if `K'(delta) > 0`, or if either response term is strictly negative. Hence, if larger gaps do not become disproportionately more recoverable, more learnable, or cheaper to train, M0.1 provides no basis for treating a larger quality gap as evidence of larger competence-investment value. This statement is conditional on M0.1 assumptions, not universal.

## 10. Conceptual separation

M0.1 separates four objects:

- **Observed failure severity:** `delta`.
- **Learning response:** `g(delta)`, `ell(delta)`, and `K(delta)`.
- **Operational consequence:** `h(delta) = g(delta)+c-delta`.
- **Downstream intervention value:** `V(delta)`.

In particular:

```text
failure severity != learning response != downstream operational value.
```

A quality gap observes current relative performance. It is not, by itself, a model of how a recipient will respond to learning.

## 11. Sufficiency of frequency x gap

The objective is not to prove that frequency x quality gap is bad. The emerging question is: under which assumptions is `p delta` a valid proxy for competence-investment value, and which violations make it order-equivalent, approximately order-preserving, uninformative, or systematically reversed relative to downstream intervention value?

The frequency-gap baseline observes approximately `(p, delta)`. M0.1 value can depend on `(p, delta, g(delta), ell(delta), K(delta), c, H, gamma)`. Merely observing that additional variables occur in this expression is not a scientific contribution. M0.1 only begins a structural characterization of the assumptions needed for frequency-gap ordering to be justified.

## 12. The response functions are not universal learning laws

M0.1 does not assume real learning gain is universally determined by quality gap. In a heterogeneous system, `g`, `ell`, and `K` may depend on the recipient model, task region, teacher, training method, available data, current competence state, intervention budget or intensity, representation compatibility, and other factors. The functions `g(delta)`, `ell(delta)`, and `K(delta)` are analytical devices: they expose which implicit relationship between observed gap and learning response would be required for gap-based prioritisation to be rational.

## 13. Relation to H1

H1 is unchanged. M0.1 sharpens its interpretation: it is not merely a proposal to add learnability to frequency x gap. Current failure statistics may be insufficient because the value of an intervention depends on the competence transition it induces and on the downstream operational consequence of that transition:

```text
delta -> learning response -> post-learning routing consequence -> intervention value.
```

M0.1 isolates the first portion of this chain without introducing a new official research question.

## 14. What M0.1 establishes and does not establish

Under its stated assumptions, M0.1 establishes analytically that:

- M0's fixed-gain opposite monotonicity is a special case;
- the sign of `V'(delta)` depends on learning-response derivatives;
- `g'(delta)=1` is the critical boundary when learnability and cost are constant;
- gap-dependent learnability changes that boundary;
- increasing training cost can further penalise larger-gap interventions; and
- explicit conditions can imply opposite monotonicity of gap and intervention value.

M0.1 does not establish the empirical shapes of `g(delta)`, `ell(delta)`, or `K(delta)`; realistic LLM distillation response; that RouteNLP is empirically suboptimal; that frequency-gap ranking fails on real workloads; novelty; or a final HLS intervention policy.

## 15. Next computational test

The next planned task is computational verification, not new model development. The first response family should be `g(delta) = a+b delta` with constant `ell` and `K`, checking the analytical boundary at `b=1`. A later, optional diagnostic could use `ell(delta) = clip(ell_0+s delta, 0, 1)` only over intervals where clipping does not obscure derivative interpretation. A mechanism-space map over parameters such as `(b,s)` would classify the sign of `V'(delta)`; its purpose would be to verify analytical boundaries, not to produce arbitrary rank-reversal percentages.

## 16. Relation to M1

M1 remains reserved for vector-valued competence changes and cross-competence effects:

```text
Delta q_i = (Delta q_i1, ..., Delta q_iZ).
```

M0.1 does not address forgetting, interference, specialisation, or portfolio coverage changes outside the target region. M1 is not started by this extension.
