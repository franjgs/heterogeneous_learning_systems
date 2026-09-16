# B2.3 — Gutjahr Example 2: mixed portfolio

**Type:** exact source reproduction

**Source:** Gutjahr (2011), Example 2.

Parameters:

    n = 2
    T = 2
    z11 = z21 = 0
    beta1 = beta2 = 0
    eta1 = 2
    eta2 = 0
    w1 = 1
    w2 = 3/2

Learning function:

    phi(z) = 0                 if z < -1
             (1+z)/2           if -1 <= z <= 1
             1                 if z > 1

Gutjahr derives the optimal policy

    x11* = 0.5
    x12* = 1

with objective value

    13/8 = 1.625.

Thus the first-period portfolio is mixed and strictly outperforms every
policy that is extremal in every period.

This experiment reproduces that exact counterexample numerically.
No HLS-specific mechanism is introduced.

## Audit contract and reproduction

- Citekey: `gutjahr2011`; source detail: Example 2.
- Assumptions and parameters: the two-period piecewise efficiency function and objective above, evaluated on a `0.001` grid.
- Pass criterion: recover `(x11,x12)=(0.5,1)` and objective `13/8`, strictly above every extremal alternative.
- Expected status: `REPRODUCED`.

Run `python experiments/foundations/b2_3_gutjahr_mixed/run.py`. This establishes only the published counterexample under its fixture.
