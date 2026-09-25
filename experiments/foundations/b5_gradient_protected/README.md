# B5 Gradient-Protected Development

Phase A implements one frozen action, GREP, against the existing REP baseline.
The default runner mode is a training-free dry run. The fixed smoke case is
excluded from scientific outputs, and the 60-fit run requires `--run-full`.

Projection dot products, memory squared norms, coefficients, projected vectors,
and the `dot_after` audit use float64. The final combined gradient is converted
back to each trainable parameter's float32 dtype immediately before
`optimizer.step()`. A changed implementation fingerprint starts a fresh restart
generation and cannot reuse an earlier GREP fit.
