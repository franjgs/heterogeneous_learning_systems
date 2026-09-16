# B12.2 — Recover Beam 1

**Type:** limiting case

This experiment verifies that the integrated B12 model reduces to its
static allocation component when competence evolution is disabled.

We set

    beta_i = 0
    eta_i = 0

for every competence.

Therefore

    z_{i,t+1} = z_{it}

and the competence state remains constant.

Because the routing rule receives the same state and the same problem
distribution in every period, its scores and allocation must also remain
constant.

The experiment checks that the integrated feedback model therefore
recovers exactly its Beam-1 allocation behavior when Beam-2 evolution is
removed.

This is a limiting-case consistency test, not a claim of optimality or
novelty.

## Audit contract and reproduction

- Citekeys: `garicano2000`, `gutjahr2011`.
- Assumptions: fixed environment and `beta=eta=0` for every competence.
- Parameters: six periods and the state/probabilities in `config.json`.
- Pass criterion: state, scores, choice, and allocation remain equal to their first-period values within `1e-12`.
- Expected status: `REPRODUCED` limiting case.

Run `python experiments/foundations/b12_2_recover_beam1/run.py`. This recovers the integrated model's static allocation component, not Garicano's full model.
