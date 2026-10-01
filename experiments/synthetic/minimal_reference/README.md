# Minimal-reference Phase-V validation

This runner evaluates a fixed deterministic family of the canonical 2×2×2
minimal reference scenario.  It varies primitive competence entries, present
and future demand mixtures, the common learning scale, and `beta`; `L` and
`G` are derived from every evaluated world.

```text
python experiments/synthetic/minimal_reference/run_validation.py
```

The runner writes `worlds.csv`, `summary.json`, and `manifest.json` under
`results/foundations/minimal_reference_validation/`.  Counts describe the
declared grid only.  They are not estimates of real-world prevalence, policy
superiority, or irreducibility.
