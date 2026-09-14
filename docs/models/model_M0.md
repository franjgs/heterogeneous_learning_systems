# M0 — Minimal competence-intervention model

M0 is a deliberately minimal working model designed to test whether failure frequency and quality gap are sufficient to rank competence-improvement interventions by their downstream operational value.

M0 is not claimed as novel, is not the final HLS model, and deliberately removes most mechanisms identified in the landscape. Its purpose is analytical isolation of the smallest mechanism relevant to H1.

## 1. System definition

Let the portfolio contain two models:

```text
M = {M_C, M_E}
```

where `M_C` is the cheaper model and `M_E` is the more expensive model. In M0, this distinction is operational cost, not epistemic authority.

There are two task regions:

```text
Z = {1, 2}
```

with `p_z = P(z)` and `p_1 + p_2 = 1`. The competence/quality matrix is:

```text
        [ q_C1  q_C2 ]
C   =   [ q_E1  q_E2 ]
```

Here `q_iz` is the expected task quality obtained by model `i` on region `z`. In M0, `q_iz` is known and stationary, all tasks in a region are represented by this expected quality, and competence and expected quality are identified for simplicity. That identification may be relaxed later.

## 2. Operational routing

Let execution costs satisfy `k_C < k_E`. Define immediate operational utility:

```text
r_iz = q_iz - lambda k_i
```

where `lambda >= 0` converts execution cost into the utility scale of quality. The optimal current router is:

```text
i*(z) = argmax_i r_iz.
```

The portfolio operational value per request is:

```text
R(C) = sum_z p_z max_i r_iz.
```

M0 assumes perfect knowledge of `q_iz` and deterministic utility-maximizing routing. This is intentionally stronger than a realistic router.

## 3. Quality gap and routing margin

Define the quality gap:

```text
delta_z = q_Ez - q_Cz,
```

and the operational advantage associated with using the cheaper model:

```text
c = lambda (k_E - k_C) > 0.
```

The routing margin is:

```text
m_z = r_Ez - r_Cz
    = delta_z - c.
```

Thus `delta_z` measures the cheap model's quality disadvantage, whereas `m_z` is the cost-adjusted disadvantage that determines routing. They are not the same object.

For the core analysis, assume `m_z > 0`, so the expensive model is currently selected in region `z`. The case `m_z <= 0` is straightforward but not central to H1 because the cheap model is already operationally preferred.

## 4. Learning intervention

The intervention is:

```text
u_z = train M_C on task region z.
```

It has training cost `K_z >= 0` and succeeds with probability `ell_z in [0,1]`. Conditional on success, the cheap model's expected quality in `z` improves by a fixed `g_z > 0`:

```text
q'_Cz = q_Cz + g_z    with probability ell_z,
q'_Cz = q_Cz          with probability 1 - ell_z.
```

All other `q_ij` remain unchanged. `ell_z` is a deliberately minimal representation of learnability.

M0 does not model amount of data, teacher identity, training method, learning curves, interference, forgetting, cross-task transfer, or uncertainty in `g_z`.

## 5. Post-intervention routing

After successful learning:

```text
r'_Cz = r_Cz + g_z.
```

The cheap model becomes operationally preferable exactly when:

```text
r_Cz + g_z > r_Ez
g_z > m_z
g_z > delta_z - c.
```

This is the **switching condition**. Let `[x]_+ = max(x, 0)`. Conditional on successful learning, the operational gain is:

```text
Delta R_z
    = p_z [g_z - m_z]_+
    = p_z [g_z + c - delta_z]_+.
```

The positive-part operator appears because the post-intervention router selects the maximum of the old expensive-model utility and the improved cheap-model utility. If `g_z <= m_z`, the cheap model has genuinely improved but the deterministic optimal routing winner does not change; under M0's deliberately simple objective, `Delta R_z = 0`. This is an M0-specific result, not a universal statement about learning value.

## 6. Expected intervention value

Suppose the competence change persists for `H` future operational periods with discount factor `gamma in [0,1]`. Define:

```text
A_H = sum_{t=1}^H gamma^(t-1).
```

For `gamma != 1`, `A_H = (1 - gamma^H)/(1 - gamma)`; for `gamma = 1`, `A_H = H`. The expected net intervention value is:

```text
V_z
    = -K_z + A_H p_z ell_z [g_z - m_z]_+
    = -K_z + A_H p_z ell_z [g_z + c - delta_z]_+.
```

The factors respectively represent future exposure (`p_z`), success probability (`ell_z`), conditional operational consequence (`[g_z - m_z]_+`), persistence/horizon (`A_H`), and learning investment (`K_z`). This multiplicative structure is not a general HLS law; it follows from M0's independence, stationarity, fixed-gain, and persistence assumptions.

## 7. RouteNLP-like baseline

Define an abstract frequency-gap baseline score:

```text
S_z = p_z delta_z.
```

It captures the structure of ranking a failure region by frequency (or cluster size) times quality gap. It is not claimed to be the complete RouteNLP algorithm. Call it the **RouteNLP-like targeted-intervention score**, or **frequency-gap baseline**.

The baseline intervention is `z_R = argmax_z S_z`; the M0 value-optimal intervention is `z* = argmax_z V_z`.

## 8. General M0 rank-reversal condition

For two regions, a rank reversal is:

```text
S_1 > S_2
but
V_1 < V_2.
```

Equivalently:

```text
p_1 delta_1 > p_2 delta_2

-K_1 + A_H p_1 ell_1 [g_1 + c - delta_1]_+
    <
-K_2 + A_H p_2 ell_2 [g_2 + c - delta_2]_+.
```

This is the **General M0 rank-reversal condition**. It is not yet a deep theorem; it records that the rankings are not generally order-equivalent.

## 9. Proposition M0.1 — Non-equivalence of failure-gap ranking and intervention-value ranking

Under M0 assumptions, ranking task regions by:

```text
S_z = p_z delta_z
```

is not generally order-equivalent to ranking interventions by:

```text
V_z = -K_z + A_H p_z ell_z [g_z + c - delta_z]_+.
```

**Proof.** It is sufficient to construct two regions satisfying the rank-reversal inequalities above. Let:

```text
p_1 = p_2 = 0.5
delta_1 = 0.30,  delta_2 = 0.20
c = 0.15
g_1 = g_2 = 0.18
ell_1 = ell_2 = ell > 0
K_1 = K_2 = K.
```

The baseline scores are:

```text
S_1 = 0.5 * 0.30 = 0.15
S_2 = 0.5 * 0.20 = 0.10,
```

so it selects region `z_1`. The margins are `m_1 = 0.30 - 0.15 = 0.15` and `m_2 = 0.20 - 0.15 = 0.05`. Successful operational gains are:

```text
Delta R_1 = 0.5 * (0.18 - 0.15) = 0.015
Delta R_2 = 0.5 * (0.18 - 0.05) = 0.065.
```

Because `A_H`, `ell`, and `K` are common, `V_2 > V_1`. Therefore the two rankings can differ. QED.

The reversal occurs even when task frequencies, learnability, learning cost, and successful quality gain are equal. Downstream operational consequences alone are sufficient to break the frequency-gap ordering.

## 10. Corollary M0.1 — Gap cancellation under perfect quality matching

Consider the strong special case `g_z = delta_z`: conditional on success, the cheap model reaches the expensive model's quality in that region. Then:

```text
g_z + c - delta_z = c
V_z = -K_z + A_H p_z ell_z c.
```

If `K_1 = K_2` and `ell_1 = ell_2`, `V_z` is ordered only by `p_z`. The quality gap can affect how difficult competence is to acquire, but if equal success/cost and full gap closure are assumed, the value of closing it is determined by future usage and execution-cost savings.

This motivates the conceptual separation:

```text
failure severity != learnability != value of the resulting competence.
```

The corollary must not be generalized beyond its assumptions.

## 11. Stronger switching counterexample

In the regime:

```text
m_2 < g < m_1,
```

`[g - m_1]_+ = 0`, but `[g - m_2]_+ > 0`. An intervention on region 1 can improve the cheap model but create zero downstream operational gain in M0, while the intervention on region 2 changes routing.

This is useful as a falsification example, but is almost too easy: the result follows directly from a deterministic routing threshold. It should not be oversold as a publishable theoretical contribution.

## 12. What M0 actually establishes

M0 establishes that:

1. `frequency * quality_gap` is not generally sufficient to rank learning interventions by downstream operational value;
2. quality gap and routing margin are distinct;
3. learning gain and operational gain are distinct;
4. learnability and value of the competence obtained are distinct; and
5. downstream routing can create rank reversals even when learnability, learning cost, and successful competence gain are identical.

M0 does not establish novelty of HLS, superiority of a new algorithm, need for long-horizon RL, need for bandits, value of diversity, value of forgetting, realistic LLM distillation behavior, that RouteNLP is suboptimal in its actual benchmark, or that deterministic routing thresholds are a realistic production model.

## 13. Critical limitations

M0 has deliberately severe limitations:

1. two models only;
2. two task regions only;
3. known stationary task frequencies;
4. known qualities;
5. known learning success probability;
6. deterministic fixed learning gain conditional on success;
7. no cross-competence effects;
8. no forgetting;
9. no cross-model effects;
10. no teacher choice;
11. no intervention intensity;
12. no learning lead time;
13. no demand uncertainty or drift;
14. no exploration/exploitation;
15. no uncertainty in the transition model;
16. deterministic utility-maximizing routing;
17. linear quality-cost utility;
18. no quality constraints;
19. no cascading or multi-stage routing; and
20. no mixed or stochastic routing.

Most importantly, an improvement that does not change the deterministic routing winner has zero operational value under M0. That is a property of M0, not a general HLS claim.

## 14. Why M0 is still useful

M0 is useful precisely because its rank reversal does not require uncertainty, interference, diversity, sophisticated sequential control, or different learnability. It isolates the most elementary downstream-decision mechanism.

Because that mechanism is simple and closely related to generic decision-focused reasoning, M0 alone is unlikely to constitute a sufficient research contribution. Its limited role is to establish mathematical coherence for H1 and to make the next assumptions explicit.

## 15. Transition to M1

M1 is not formulated here. The next planned extension is to allow an intervention on one target competence to modify the recipient's entire competence vector:

```text
Delta q_i = (Delta q_i1, ..., Delta q_iZ),
```

with positive or negative components. Continual/Lifelong Learning motivates forward transfer, backward transfer, interference, and forgetting. The next conceptual test is: when does individual forgetting actually create system-level harm? Because a portfolio can reroute tasks to other models:

```text
individual forgetting != system-level harm.
```

No M1 equations are derived here.
