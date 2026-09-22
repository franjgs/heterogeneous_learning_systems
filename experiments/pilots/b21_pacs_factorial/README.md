# B2.1 PACS domain-development factorial

This pilot keeps the B2.0 PACS split manifest, ImageNet-pretrained
MobileNetV2/ResNet-50 models, optimizer settings, three epochs, and validation
only evaluation. It runs on CPU and never opens the TEST split.

For each of five seeds, the runner trains the B2.0 teacher `D` on BASE+TRANSFER
and `F0` on the exact B2.0 fraction 0.25 BASE subset. For each `N` in
`{25, 50, 100}`, it pseudo-labels TRANSFER examples with `D`, then trains each
singleton and each direct pair intervention from the same `F0` checkpoint.
There are 4 singletons plus 6 pairs per `N`: 160 fits total including the ten
shared `D`/`F0` fits. Transfer counts are photo=1665, art_painting=2050,
cartoon=2350, sketch=3925, so all three N values are feasible.

Scores are validation balanced accuracies in the fixed domain order
`photo, art_painting, cartoon, sketch`, with uniform `p_k=1/4`. The runner
stores `Gamma_learn = V(Fij)-V(Fi)-V(Fj)+V(F0)` and, for every predeclared
`c` in `{0.00, 0.02, 0.05, 0.10, 0.15}`, stores
`V_oper(F;c)=mean_k max(S_F(k), S_D(k)-c)`, Gamma_oper, and the domain routing
pattern.

Observed B2.0 CPU timings imply approximately 7.1 hours for the full 160-fit
factorial (about 3800 s/teacher, 550 s/F0, with intervention time scaled by
intervention sample count). This is an estimate only; the full factorial is
not run by the preparation workflow.
