# B2.1 — Gutjahr competence dynamics

**Type:** source reproduction

**Source:** Gutjahr (2011), *Optimal dynamic portfolio selection for
projects under a competence development model*.

## Result reproduced

For project class i and period t, Gutjahr models competence as

    z_it = z_i1 - beta_i (t-1)
           + eta_i sum_{s<t} x_is

where:

- z_i1 is initial competence,
- beta_i is competence depreciation,
- eta_i is the learning coefficient,
- x_it is the share of work capacity allocated to class i.

Efficiency is

    gamma_it = phi(z_it).

This experiment verifies directly that the closed-form expression is
numerically identical to the recursive transition

    z_i,t+1 = z_it - beta_i + eta_i x_it.

## Scope

The allocation sequence is fixed.

No optimization is performed.

No Garicano mechanism, routing mechanism, knowledge transfer, or
HLS-specific assumption is introduced.

The experiment only validates the executable implementation of the
Beam 2 state dynamics.
