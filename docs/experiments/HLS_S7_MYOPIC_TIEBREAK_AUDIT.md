# HLS-S7 — Auditoría de ventaja de planificación y desempates

**Fecha:** 23/10/2026
**Configuración:** instancia central S7, C5, `T=4`; enumeración exacta de sus 16 trayectorias de demanda.
**Artefacto:** [`results.json`](../../results/experiments/hls_s7_myopic_tiebreak_audit/results.json)
**Runner:** [`run_hls_s7_myopic_tiebreak_audit.py`](../../experiments/run_hls_s7_myopic_tiebreak_audit.py)

## Pregunta y alcance

Se comprobó qué parte de la ventaja previamente medida de Bellman frente al miope fijo depende de cómo se eligen acciones con igual CES inmediato. Se conservaron la instancia, las leyes MIS-v2 y de transferencia, las restricciones, la demanda y las cuatro referencias históricas. Se añadieron dos referencias reactivas que conservan el óptimo inmediato de CES y usan un desempate explícito.

Es un cálculo exacto de una instancia, no una comparación estadística ni evidencia de generalización. Los valores son expectativas sobre el árbol completo de demanda; por ello no se presentan intervalos de confianza.

## Auditoría del miope histórico

`solve_reactive_greedy` enumera el catálogo de acciones y reemplaza la acción vigente solo si `reward > best_reward + 1e-12`. En consecuencia, entre valores empatados dentro de esa tolerancia conserva el primer candidato del catálogo. CES inmediato se calcula mediante la transición física existente `_step`; el criterio del miope es ese CES, no cumplimiento funcional ni desarrollo futuro. La transición MIS-v2 y, cuando está habilitada, la enseñanza se ejecutan después de elegir la acción. También pueden cambiar producción, esfuerzo y consumo de recursos; por tanto, dos acciones empatadas en CES no son necesariamente equivalentes físicamente.

No se encontró otro mecanismo que eleve el CES miope por anticipación: la regla original no consulta demanda futura ni valor Bellman. La elección de una acción empatada sí cambia el sucesor físico y puede alterar el CES de periodos posteriores.

## BEST-MYOPIC

En cada estado se forma el conjunto

\[
\mathcal A^*(s,d)=\{a: R(s,d,a)\geq \max_{a'}R(s,d,a')-10^{-12}\}.
\]

BEST-MYOPIC primero restringe la decisión a este conjunto. Entre sus acciones maximiza

\[
G(s,a)=\sum_{i,k}\max(0,C'_{ik}(s,a)-C_{ik}),
\]

donde `C'` se calcula aplicando MIS-v2 y la transición de transferencia existente. No consulta valor Bellman ni demanda futura. Cuando persiste un empate secundario, usa una clave canónica determinista de acción, independiente del orden del catálogo. En esta instancia exacta recibe el mismo estado de competencia y demanda actual que las referencias S7 anteriores; el resultado no convierte BEST-MYOPIC en una política desplegable bajo competencias ocultas.

## Seis políticas

Métricas obtenidas por HLS-PEF, con las mismas unidades y definición de la ejecución piloto. `Cumplimiento` es la fracción esperada de servicios tarea-periodo que satisface el requisito; `déficit` es la suma esperada de déficits absolutos. Esfuerzos y consumos son acumulados.

| Política | CES acumulado | Cumplimiento | Déficit | Producción | Esfuerzo productivo | Esfuerzo docente | Recurso docente | Acciones docentes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A — Bellman sin transferencia | 3.1628653621 | 0.750250 | 0.049950 | 3.1675720885 | 8.00000 | 0 | 0 | 0 |
| B — Bellman con transferencia | 3.1743777327 | 0.750000 | 0.175000 | 3.1743777327 | 7.00000 | 0.25000 | 0.50000 | 1 |
| MA — miope original, sin transferencia | 3.0346209871 | 0.3019375 | 0.1023575625 | 3.0346209871 | 5.20775 | 0 | 0 | 0 |
| MB — miope original, con transferencia | 3.0346209871 | 0.3019375 | 0.1023575625 | 3.0346209871 | 5.20775 | 0 | 0 | 0 |
| BMA — BEST-MYOPIC, sin transferencia | 3.0444737839 | 0.3019375 | 0.1023575625 | 4.3181911375 | 8.00000 | 0 | 0 | 0 |
| BMB — BEST-MYOPIC, con transferencia | 3.0444737839 | 0.3019375 | 0.1023575625 | 4.3181911375 | 8.00000 | 0 | 0 | 0 |

Los cuatro valores históricos A/B/MA/MB se reprodujeron con diferencia absoluta menor o igual a `1e-10`. Las 16 probabilidades de rama suman uno. Las métricas se conservan por separado; la mayor producción acumulada de BEST-MYOPIC no se interpreta por sí sola como mayor servicio o CES.

## Descomposición de la ventaja CES

Sin transferencia:

| Contraste | Valor |
|---|---:|
| D0 = A − MA, ventaja histórica de Bellman | 0.1282443750 |
| D1 = A − BMA, Bellman frente a BEST-MYOPIC | 0.1183915782 |
| T0 = BMA − MA, cambio por desempate | 0.0098527968 |
| Residuo `D0 − D1 − T0` | 0.0000000000 |

Con transferencia:

| Contraste | Valor |
|---|---:|
| D0T = B − MB | 0.1397567456 |
| D1T = B − BMB | 0.1299039488 |
| TT = BMB − MB | 0.0098527968 |
| Residuo `D0T − D1T − TT` | 0.0000000000 |

El ajuste de desempate representa contablemente alrededor del 7.7% de cada brecha histórica de CES. No es una descomposición causal independiente: cada selector induce trayectorias posteriores distintas. Bellman sigue superando BEST-MYOPIC en esta instancia, tanto sin transferencia (`0.1183915782`) como con ella (`0.1299039488`). La interacción planificación × transferencia con BEST-MYOPIC es `0.0115123706`: transferencia añade ese CES bajo Bellman y cero bajo BEST-MYOPIC. Es un contraste de esta instancia, no una afirmación general.

## Decisiones empatadas y mecanismo

Para cada variante reactiva se auditaron 32 estados en la unión de estados alcanzados por el miope original y BEST-MYOPIC. En 16 estados hubo más de una acción dentro de la tolerancia; en esos 16 cambió la acción seleccionada. Las 16 clases de empate incluyeron sucesores de competencia diferentes (clase B) y también diferencias en output productivo o recursos (clase C); las clases son no excluyentes. No hubo empate con consecuencias físicas idénticas en estos estados auditados. El JSON conserva por estado catálogo admisible, CES máximo, número de empatadas, ambas acciones, ganancias de competencia y diferencias de sucesores.

Ejemplo: en `t=0`, demanda `task-y`, el miope original produce solo con A en y. BEST-MYOPIC añade producción de B en x. Ambas decisiones tienen CES inmediato máximo idéntico; la ganancia positiva de competencia es `0.015` frente a `0.099`, y el sucesor difiere en `0.084` para B/x. Esto muestra que el desempate puede seleccionar esfuerzo y aprendizaje distintos sin preferir demanda futura. El cambio mejora CES acumulado en esta instancia, pero no cambia la tasa de cumplimiento ni el déficit esperados.

### Sacrificio inmediato de Bellman

Bellman sin transferencia no elige ninguna acción estrictamente subóptima en CES inmediato en los estados de su trayectoria óptima. Bellman con transferencia sí lo hace en un estado: `t=0`, demanda `task-x`, competencia inicial `[[0.05, 0.9], [0.3, 0.0]]`. Elige producción `0.5` por agente en x y enseñanza A→B de y con esfuerzo `0.25`; su CES inmediato es `0.175` frente al máximo `0.35`, un sacrificio de `0.175`. El sucesor incorpora `0.08` de competencia B/y. Bajo continuación Bellman, la acción de Bellman vale `3.1743777327`, frente a `3.1628653621` si en ese estado se sustituye por la acción BEST-MYOPIC inmediata y luego se sigue Bellman: diferencia local `0.0115123706`. Esto identifica una decisión intertemporal concreta y su Q local, no una atribución aditiva de toda la diferencia de políticas.

## Conclusión y límites

El desempate fijo explica una parte pequeña, cuantificada y reproducible de la ventaja previamente observada, pero no la elimina. La ventaja residual de Bellman frente a la referencia miope favorable a MIS-v2 persiste. En la variante con transferencia, Bellman además sacrifica CES inmediato para enseñar; la referencia BEST-MYOPIC no enseña porque su criterio secundario favorece más el desarrollo inmediato obtenido por producción.

La conclusión se limita al CES esperado y a la única instancia central T=4. El criterio de desarrollo de BEST-MYOPIC es un desempate de diagnóstico, no un nuevo planificador ni una recomendación universal. Su valor usa la transición física conocida en el régimen exacto de S7. No se infiere mejora funcional: BEST-MYOPIC mantiene los indicadores funcionales de MA/MB; B conserva su aumento de CES junto con mayor déficit que A. La comparación no es estadística y no generaliza a otras matrices, leyes, horizontes u observabilidad.

## Validación

El runner independiente enumera el árbol C5 y evalúa las seis políticas mediante el adaptador S7→HLS-PEF, sin alterar el evaluador ni las reglas históricas. Se verificaron: óptimo CES inmediato de BEST-MYOPIC; desempate independiente del orden del catálogo cuando difiere la ganancia secundaria; identidad de las descomposiciones; reproducción de A/B/MA/MB; procedencia HLS-PEF; y sacrificio Bellman. Pasaron las pruebas focalizadas S7/PEF indicadas en el registro acumulativo y `git diff --check`.
