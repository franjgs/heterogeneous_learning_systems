# M0 computational laboratory

This directory verifies and explores exactly the minimal model in [model_M0.md](../../docs/models/model_M0.md). It does not implement M1 mechanisms such as interference, forgetting, transfer, demand uncertainty, stochastic routing, or teacher choice.

The canonical sweep is deliberately restricted to `delta_z > c`, equivalently `m_z > 0`: the expensive model must be the operational winner before intervention. A mathematically more general operational setting exists when the cheap model may already be preferred, but that regime is intentionally outside M0 and is not analysed here. The sweep rejects `--delta-min <= c` rather than silently adjusting it.

## Equations

For each region, the scripts compute:

```text
delta_z = q_Ez - q_Cz
c = lambda (k_E - k_C)
m_z = delta_z - c
S_z = p_z delta_z
V_z = -K_z + A_H p_z ell_z [g_z - m_z]_+
```

Ties select the lowest region index. Frequency-gap regret is `max_z V_z - V_{z_R}`.

## Run

Install the lightweight dependencies, then run from the repository root:

```text
python -m pytest
python experiments/m0/run_rank_reversal.py
python experiments/m0/sweep_regimes.py
```

The sweep accepts `--resolution`, `--cost-advantage`, `--gain`, `--horizon`, `--gamma`, and the remaining equal region parameters. Defaults are `c=0.15`, `g=0.18`, `p_1=p_2=0.5`, `ell_1=ell_2=1`, `K_1=K_2=0`, `H=1`, and `gamma=1`. Its default lower bound is `c + 1e-6` to enforce strict canonical routing.

## Outputs and structural boundaries

The sweep writes a CSV, JSON metadata, rank-reversal phase map, and regret map to `results/m0/`. It separates strict agreement, strict rank reversal, frequency-gap ties, intervention-value ties, and deterministic selection agreement. In the equal-parameter experiment, frequency-gap ranking increases with `delta`, while value is proportional to `[g + c - delta]_+`. The canonical M0 core band is:

```text
c < delta_z < c + g.
```

Within that band, away from ties, the two scores have opposite monotonicity in `delta`. This is an exact property of M0's fixed gain and deterministic switching threshold, not a general HLS result.
