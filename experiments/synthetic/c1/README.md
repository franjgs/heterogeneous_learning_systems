# C1 exact reference worlds

This runner verifies the exact C1 reference worlds implemented on the G0
synthetic environment. They are acceptance cases, not a phase sweep or an
answer to RQ0.

```bash
python experiments/synthetic/c1/run_reference_worlds.py
python -m pytest -q tests/synthetic/test_c1_reference_worlds.py
```

The authoritative specification is Section 28 of
`docs/experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md`.
