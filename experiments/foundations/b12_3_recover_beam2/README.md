# B12.3 — Recover Beam 2

**Type:** limiting case

This experiment verifies that the integrated B12 model reduces exactly
to the competence-evolution dynamics of Beam 2 when routing is removed.

The allocation sequence x_t is supplied externally rather than being
computed by the routing rule.

Competence evolves recursively according to

    z_{i,t+1} = z_it - beta_i + eta_i x_it.

The resulting trajectory is compared period by period with Gutjahr's
closed-form expression

    z_it = z_i1 - beta_i(t-1)
           + eta_i sum_{s<t} x_is.

The recursive and closed-form trajectories must agree numerically.

This is a limiting-case consistency test. It makes no claim about the
optimality of the externally supplied allocation sequence.

## Audit contract and reproduction

- Citekey: `gutjahr2011`.
- Assumptions: routing is removed and the complete allocation path is supplied externally.
- Parameters: the state, coefficients, six allocations, and `1e-12` tolerance in `config.json`.
- Pass criterion: recursive before/after states equal the closed-form states in every period.
- Expected status: `REPRODUCED` limiting case.

Run `python experiments/foundations/b12_3_recover_beam2/run.py`. Passing verifies the reduction to Beam 2 dynamics only.
