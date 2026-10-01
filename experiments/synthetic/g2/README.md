# G2 --- Dynamic HLS ground truth

G2 is the executable validation of the minimal D0/D1/D2 analytical controls in
[the dynamic ground truth](../../../docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md).
It supports the scoped T4--T6 foundation; it is not an RQ0 campaign, a G0
extension, or a universal dynamic HLS model.

The runner evaluates only the fixed 2-agent/2-task/2-period scenarios:

- **D0:** no-evolution sanity control;
- **D1:** action-dependent learning with an efficient-frontier/value null;
- **D2:** capability, development-value, and coupling controls.

Run from the repository root:

```text
PYTHONPATH=.:src pytest -q tests/test_g2_dynamic.py
python experiments/synthetic/g2/run_g2.py
```

The deterministic runner writes `g2_summary.json`, `g2_d2_sweep.csv`, and
`g2_manifest.json` to `results/foundations/g2_dynamic/`. The manifest records
SHA-256 hashes for the model, runner, summary, and sweep.

No additional G2 scenarios, stochasticity, teaching, knowledge transfer,
resource constraints, G0 capability, or competence mechanism is introduced.
