# Nembhard-inspired direct-experience productivity mechanism

This note documents a standalone scalar mechanism implemented from the
direct-experience productivity curve in Nembhard and Bentefouet (2015), Eq. 1
(printed p. 176). It is a mechanism component, not a reproduction of the
article's organization, assignment, grouping, indirect-transfer, or production
model. Source interpretation and unresolved article-level issues are recorded
in [the fidelity review](../literature/audits/HLS_NEMBHARD_FIDELITY_AND_CONTRACT_REVIEW_2026-10-17.md).

## Equation and units

The implementation evaluates

\[
P(D) = k\,\frac{D+p}{D+p+r}.
\]

Here `D` is accumulated direct experience, `p` is prior experience expressed
in equivalent exposure units, and `r` is the experience scale. `D`, `p`, and
`r` must use the same caller-declared exposure unit. `k` and `P` use the same
caller-declared productivity unit. The module performs no unit conversion.
`P` is not HLS's normalized competence and is not substituted for it.

The module's validated domain is `k >= 0`, `p >= 0`, `r > 0`, and `D >= 0`,
with all inputs finite real values. The source equation prints the broader
condition `p + r > 0`; choosing positive `r` here gives a well-defined,
monotone, saturating scale parameter without the degenerate denominator case.
This explicit software-domain choice does not claim to resolve every domain
interpretation in the paper.

For fixed parameters,

\[
P'(D)=\frac{kr}{(D+p+r)^2},\qquad
P''(D)=-\frac{2kr}{(D+p+r)^3}.
\]

Thus, for `k > 0`, productivity is increasing and concave, with
`P(0)=kp/(p+r)` and limit `k` as `D` tends to infinity. If `D+p=r`, then
`P=k/2`; a nonnegative exposure reaching that point exists only when `r >= p`
and is `D=r-p`. In particular, `r` is the half-asymptote threshold in total
effective experience `D+p`, not necessarily the additional experience needed
from the initial state.

## Explicit experience transition

`advance_direct_experience(D, delta_D)` returns
`D_next = D + delta_D`, requiring finite `D >= 0` and finite `delta_D >= 0`.
`evaluate_direct_exposure` reports productivity before and after that update.
These helpers do not mutate shared state. `delta_D` has the mechanism's
exposure unit; it is not assumed to equal productive effort in HLS.

## API and example

The implementation is in [`src/hls/mechanisms/nembhard_direct.py`](../../src/hls/mechanisms/nembhard_direct.py).
`DirectExperienceParameters` is an immutable parameter record;
`direct_productivity` evaluates one scalar; and `direct_productivity_many`
provides dependency-free sequence evaluation returning a tuple.

```python
from hls.mechanisms.nembhard_direct import (
    DirectExperienceParameters,
    direct_productivity,
    evaluate_direct_exposure,
)

parameters = DirectExperienceParameters(
    asymptotic_productivity=10.0,  # productivity units
    prior_experience=2.0,          # exposure units
    experience_scale=8.0,          # exposure units
)
assert direct_productivity(6.0, parameters) == 5.0
step = evaluate_direct_exposure(6.0, 2.0, parameters)
```

## Separation from MIS-v2 and limitations

This is the **Nembhard-inspired direct-experience productivity mechanism**.
It is deliberately independent of MIS-v2, whose exponential competence
transition is a distinct model. It does not update HLS competence, determine
how task effort maps to experience, represent indirect learning, or alter
production/assignment decisions. Those mappings require a separately
specified integration contract and are not implemented here. No campaign was
run and no claim is made that the full Nembhard and Bentefouet model has been
reproduced.

Focused equation and domain checks are in
[`tests/test_nembhard_direct.py`](../../tests/test_nembhard_direct.py).
