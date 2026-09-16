# B1.1 — Garicano autarky

**Type:** source reproduction

**Source:** Garicano (2000), *Hierarchies and the Organization of
Knowledge in Production*.

## Result reproduced

For an isolated worker who knows the solutions to problems in
the interval [0, z], expected net output is

    y^a(z) = F(z) - c z

and an interior optimum satisfies

    f(z*) = c.

## Numerical fixture

We use the decreasing triangular problem distribution

    f(z) = 2(1-z),  0 <= z <= 1

with

    F(z) = 2z - z^2.

For c = 1,

    z* = 1 - c/2 = 0.5.

The numerical grid search must recover this optimum within the
tolerance specified in config.json.

This experiment tests only the autarky result. It introduces no
HLS-specific mechanism and no competence evolution.
