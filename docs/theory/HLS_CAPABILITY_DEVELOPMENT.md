# HLS capability development: MIS-v2

## Construct and scientific status

`s_ik(t) in [0,1]` is the effective acquired capability of individual `i`
for function `k` at time `t`. It is a latent normalized state used by the
existing production model. It is not accumulated experience, observed
performance, or a probability of success. The modeled chain is:

`experience -> latent capability s_ik -> performance`.

The literature supports the qualitative premises that practice and individual
experience can develop individual capability, that gains commonly diminish,
and that experience, capability, and performance are distinct constructs. It
does not prescribe the state equation below for this normalized latent state.
MIS-v2 is therefore an **HLS modeling formulation**, not an equation taken
directly from the literature. No novelty is claimed for exponential learning.

## Requirements and HLS assumptions

For exposure `x>=0`, `s+=F(s,x)` must satisfy:

1. boundedness: `0<=F<=1`;
2. no exposure: `F(s,0)=s`;
3. positive development for `s<1, x>0`;
4. mastery fixed point: `F(1,x)=1`;
5. diminishing absolute gain: `d(F-s)/ds<0`;
6. no finite instantaneous mastery for `s<1`;
7. composition: `F(F(s,x1),x2)=F(s,x1+x2)`.

R7 is an explicit HLS discretization-consistency assumption, not an empirical
law. Homogeneous exposure should not change its cumulative effect merely
because a simulation divides it into smaller time steps.

## Derivation

Let the remaining capability gap be `g=1-s`, and assume exposure leaves a
fraction `R(x)` of it:

`1-F(s,x)=(1-s)R(x)`.

No exposure gives `R(0)=1`; R7 gives
`R(x1+x2)=R(x1)R(x2)`. Positivity and continuity yield
`R(x)=exp(-lambda x)`, `lambda>0`. Hence:

`F(s,x)=1-(1-s)exp(-lambda x)`.

For one standard exposure, define `eta=1-exp(-lambda)`, so
`F(s,1)=s+eta(1-s)`, with `0<eta<1`. Eta is the fraction of the remaining gap
removed by one standard exposure. Fractional effort uses the exponential form,
which preserves R7.

The gain is `(1-s)(1-exp(-lambda x))`: it is positive below mastery, strictly
decreases with `s`, never closes a positive gap under finite mathematical
exposure, and converges asymptotically to mastery. Valid inputs need no clipping.
At extreme floating-point exponents, representational rounding remains a
numerical limitation; the implementation contains no mastery clamp.

## MIS-v1 comparison and deprecation

MIS-v1 used `s+=min(1,s+1.5 x(1-s)^2)`. With a unit exposure, every `s<=1/3`
could clip to mastery; in particular `0 -> 1`. This violates R6 and R7 and can
reward geometries containing very low entries. MIS-v1 remains preserved for
historical reproducibility, but it is deprecated for new capability-development
claims. Existing capability-geometry results remain evidence specifically under
MIS-v1 and are not overwritten.

## Calibration and limitations

Eta is not empirically calibrated. Every substantive MIS-v2 result therefore
requires sensitivity analysis. The preregistered gate grid is
`.05,.10,.20,.35,.50,.70,.90`: broad interior slow, moderate, and fast rates
with intermediate points, chosen before outcome analysis. It is a sensitivity
design, not a calibration or an attempt to reproduce MIS-v1.

MIS-v2 assumes a common rate across people and capabilities, homogeneous
additive exposure, no forgetting, no transfer, and a fixed mastery ceiling.
It does not identify eta empirically. The possible HLS contribution concerns
using a coherent latent capability transition inside coupled discovery,
assignment, development, and reorganization—not inventing an exponential
learning curve.
