# Minimal competence-evolution microverification

This directory checks only the identities and local dynamics documented in [the minimal theory note](../../docs/theory_competence_evolution_minimal_model.md). It is not a benchmark, a model of real distillation, or evidence that the mechanisms occur in real HLS deployments.

## Reproduction

From the repository root:

```text
python -m pytest
python experiments/microverification/verify_minimal_theory.py
```

If the local Matplotlib or font cache is not writable, use a temporary cache:

```text
mkdir -p /tmp/hls_micro_mpl /tmp/hls_micro_cache
MPLCONFIGDIR=/tmp/hls_micro_mpl XDG_CACHE_HOME=/tmp/hls_micro_cache python experiments/microverification/verify_minimal_theory.py
```

## Checks

- `complementarity.csv` checks the finite switching threshold `G(x,y)`.
- `symbolic_jacobian_audit.txt` records the SymPy Jacobian and critical eigenvalue for the 2x2 learning-by-doing system.
- `specialization.csv` and `specialization_dynamics.*` show perturbations below, at, and above the local stability threshold.
- `rebalancing.csv` and `rebalancing_costs.*` compare the closed-form TRAIN/MIXED/ROUTE solution with an independent grid argmin, including boundaries and selected limiting cases.

The figures are diagnostic. Their parameter ranges and areas have no empirical, prevalence, or novelty interpretation.
