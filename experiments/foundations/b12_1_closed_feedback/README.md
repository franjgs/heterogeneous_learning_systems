# B12.1 — Closed feedback

**Type:** HLS translation

This experiment checks the minimal executable connection between the two
theoretical beams.

The sequence is:

    competence state
        -> task allocation
        -> operational experience
        -> competence evolution
        -> next task allocation

The routing rule assigns work according to

    p_i * phi(z_i),

where p_i represents problem frequency and phi(z_i) operational
efficiency.

Execution produces the allocation x_it.

Competence then evolves according to

    z_{i,t+1} = z_it - beta_i + eta_i x_it.

The resulting competence state is used by the routing rule in the next
period.

This experiment does NOT claim that this routing rule is optimal, novel,
or preferable to independent optimization.

Its sole purpose is to verify that the Beam 1 / Beam 2 feedback loop can
be represented and executed without introducing an additional learning
mechanism.

## Audit contract and reproduction

- Citekeys: `garicano2000`, `gutjahr2011`.
- Assumptions: fixed problem probabilities, deterministic extremal routing, logistic efficiency, and the documented Gutjahr state transition.
- Parameters: six periods with the state and coefficients in `config.json`.
- Pass criterion: every update uses the current allocation and every resulting state is the next period's routing state.
- Expected status: `SUPPORTED` as an HLS translation.

Run `python experiments/foundations/b12_1_closed_feedback/run.py`. This verifies an executable interface, not benefit, optimality, novelty, RQ0, or P4.
