# B2.5 — Gutjahr Example 3: failed source reproduction

**Type:** source reproduction

**Status:** FAILED_SOURCE_REPRODUCTION

**Source:** Gutjahr (2011), Example 3.

The experiment implements literally the published parameters:

    n = 2
    T = 2
    z11 = 1
    z21 = 0
    beta1 = 3
    beta2 = 0
    eta1 = 4
    eta2 = 1
    w1 = w2 = 1

and the piecewise efficiency function used in Examples 2 and 3:

    phi(z) = 0                 if z < -1
             (1+z)/2           if -1 <= z <= 1
             1                 if z > 1

The published Example 3 claims that the optimal extremal policy switches
from class 1 to class 2:

    (e1, e2).

Literal evaluation of the published equations and parameters does not
recover that conclusion.

The computed objectives are:

    (e1, e1): 2.0
    (e1, e2): 1.5
    (e2, e1): 0.5
    (e2, e2): 1.5

Therefore the literal model yields the persistent policy

    (e1, e1)

as the unique optimum.

This experiment is intentionally retained as a failed source
reproduction. The implementation must not be modified merely to recover
the published conclusion.

No erratum or published correction for Example 3 was identified in the
bibliographic search performed during this reproduction.

The source simplification drops

    x12 phi(-2 + 4 x11)

from

    x12 phi(-2 + 4 x11) + (1-x12) phi(x21).

The omitted term is not identically zero over the feasible range of `x11`, so
the simplification cannot justify the claimed optimum.

## Audit contract and reproduction

- Citekey: `gutjahr2011`; source detail: Example 3.
- Assumptions and parameters: exactly the published values and piecewise `phi` above.
- Pass criterion for the implementation audit: recover objectives `2.0`, `1.5`, `0.5`, `1.5` for `(e1,e1)`, `(e1,e2)`, `(e2,e1)`, `(e2,e2)`.
- Required source status: `FAILED_SOURCE_REPRODUCTION`.

Run `python experiments/foundations/b2_5_gutjahr_switching/run.py`. A zero exit status means the equations and discrepancy were reproduced correctly; it does not mean the source conclusion passed.
