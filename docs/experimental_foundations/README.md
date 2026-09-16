# Experimental foundations: audited status

Status: B1, B2, and B12 foundation block implemented and audited on 2026-09-16.

This block reproduces selected mechanisms from Garicano (2000) and Gutjahr
(2011), then checks their minimal executable interface. It is not the HLS method,
does not demonstrate benefit from coupling, and does not establish novelty, RQ0,
or P4.

| Experiment | Kind | Status | Audited meaning |
| --- | --- | --- | --- |
| B1.1 | `source_reproduction` | `REPRODUCED` | Autarky fixture recovers `f(z*)=c`. |
| B1.2--B1.4 | `source_reproduction` | `REPRODUCED` | The stated finite organization fixtures recover their scoped Garicano mechanisms; they are not proofs of the full propositions. |
| B2.1 | `source_reproduction` | `REPRODUCED` | Recursive and closed-form competence dynamics agree. |
| B2.2 | `source_reproduction` | `REPRODUCED` | The extremal optimum matches the complete configured grid in a convex-region instance. |
| B2.3 | `source_reproduction` | `REPRODUCED` | Gutjahr Example 2 and its mixed optimum are recovered exactly. |
| B2.4 | `source_reproduction` | `REPRODUCED` | A finite instance of Theorem 3's persistence result is recovered. |
| B2.5 | `source_reproduction` | `FAILED_SOURCE_REPRODUCTION` | Literal published equations give objectives `2.0, 1.5, 0.5, 1.5`; the claimed switching optimum is not recovered. |
| B12.1 | `hls_translation` | `SUPPORTED` | The allocation--experience--competence--next-allocation interface executes consistently. |
| B12.2 | `limiting_case` | `REPRODUCED` | Setting `beta=eta=0` recovers the static allocation component. |
| B12.3 | `limiting_case` | `REPRODUCED` | Removing routing and supplying allocations recovers Beam 2 dynamics. |
| B12.4 | `hls_translation` | `SUPPORTED` | 36 of 96 configured cases show the defined dynamic effect; `eta=0` gives 0 of 96. |

The B12.4 fraction is grid geometry, not performance or prevalence. The two
counterfactual trajectories differ only in their first allocation and use the
same routing rule thereafter.

## Reproduction

Run `python -m pytest -q`, then execute each `run.py` under
`experiments/foundations/`. Each result directory contains `metrics.json` and a
uniform `manifest.json` linking the experiment ID, exact configuration, code
hashes, citation keys, Git state, command, and result hash.

The frozen pre-implementation specification remains in
`EXPERIMENTAL_SPEC_V0.md`; the executed sequence is preserved in
`EXECUTION_PLAN.md`.
