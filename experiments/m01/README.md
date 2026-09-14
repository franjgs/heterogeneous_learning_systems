# M0.1 computational verification

This directory verifies the analytical identities in [M0.1](../../docs/models/model_M0_1_gap_dependent_learning.md). It is not a simulation of learning, a distillation experiment, or evidence about the empirical shapes of gain `g`, learnability `ell`, or cost `K`.

## Scope and predictions

All derivative checks remain in the canonical M0 domain `delta > c` and away from the positive-part kink, requiring `h(delta)=g(delta)+c-delta > 0`.

- **P1:** with `g(delta)=a+b delta` and constant `ell`, `K`, the value derivative has the sign of `b-1`.
- **P2:** with `g(delta)=rho delta`, it is negative for `0 < rho < 1` on a strictly switchable canonical interval, and zero for `rho=1`. For `rho=0`, no such canonical interval exists because the switching boundary is `delta=c`.
- **P3:** with `ell(delta)=ell0+s delta`, numerical derivatives recover the exact sign boundary obtained from the full product rule.
- **P4:** for `K(delta)=K0+r delta`, increasing `r` shifts the derivative downward by exactly `r`.

For the linear learnability family, the zero-derivative boundary is not obtained by treating `ell` as fixed. Expanding

```text
s h(delta) + (ell0+s delta)(b-1) = 0
```

gives:

```text
s* = -ell0(b-1) / [a+c+2(b-1)delta],
```

when the denominator is nonzero.

## Run

From the repository root:

```text
python -m pytest
python experiments/m01/verify_linear_response.py
python experiments/m01/verify_learnability_response.py
```

The first script writes `m01_linear_response.csv` and a PNG/PDF value plot. The second writes a small learnability-boundary table and the domain-masked `(b,s)` mechanism map in CSV, PNG, and PDF form. Invalid points (`delta <= c`, `h <= 0`, or `ell` outside `(0,1)`) are left unclassified in the map.

The map's area has no probabilistic or empirical interpretation. It is only a diagnostic of analytical signs under selected response families.
