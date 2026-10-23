# HLS — Routing presupuestado: corrección del predictor

**Fecha:** 23/10/2026

**Estado:** repetición focalizada completada; no se amplía la línea.

## Pregunta

¿La debilidad predictiva de la adaptación MIRT del piloto inicial condicionó sus resultados organizativos? Se sustituyó el predictor, manteniendo fijos consultas test, modelos, outcomes, costes, lotes, presupuestos, reglas, semillas y restricciones. Los resultados del piloto inicial siguen intactos.

## Diseño reproducible

Se reutilizó el archivo de outcomes del piloto inicial: MMLU `cais/mmlu` en la misma revisión y las mismas 160 consultas test equilibradas entre biología, matemáticas, historia de EE. UU. y psicología. Se conservaron los 200 ejemplos muestreados de `auxiliary_train`, divididos exactamente como antes: 160 para ajuste y 40 para calibración del precio del router independiente. Las respuestas de test no participaron en ajuste, selección de hiperparámetros, calibración de costes ni decisiones.

Se ajustó una regresión logística L2 con hashing fijo del texto de pregunta/opciones, identidad de modelo, tipo de tarea e interacciones modelo×tarea. El parámetro `C` se eligió entre `{0.01, 0.1, 1, 10}` por Brier medio de validación cruzada de cinco pliegues, agrupada por consulta para evitar que las respuestas de distintos modelos a una misma pregunta aparezcan en entrenamiento y validación. Ganó `C=1` (Brier CV 0,22589); el modelo final se ajustó con los 160 ejemplos de entrenamiento. Se comparó en idénticos datos con MIRT adaptado y prevalencia de entrenamiento por modelo.

**Cobertura de tarea:** el conjunto oficial `auxiliary_train` usado aquí representa `task_type=mmlu_auxiliary_mixed`; ninguno de los cuatro tipos del test aparece como categoría observada al ajustar. El predictor admite y codifica la identidad de tarea, pero no puede aprender coeficientes específicos para estas categorías de test no vistas. La señal contextual aprendida procede principalmente del texto y del modelo. Esta es una limitación de validez externa, no una variable completada artificialmente.

Se ejecutaron 3 predictores × 3 políticas (ILP, greedy, independiente reparado) × 2 composiciones × 2 presupuestos × 20 empaquetados: **720 ExperimentRun**. El presupuesto y la matriz de costes test se leyeron de los artefactos originales; se comprobó igualdad con la matriz recalculada (`allclose`, tolerancia absoluta 1e−12). Todas las comparaciones usan las mismas consultas y semillas. Los IC95% por consulta son bootstrap estratificado por las cuatro materias; los IC por empaquetado miden sensibilidad al packing condicionada a esta muestra fija. No se tratan ejecuciones ni períodos como réplicas independientes.

## Calidad predictiva en test

| Predictor | Brier (IC95% consulta) | Log-loss (IC95% consulta) | ECE, 10 bins | Predicción media − tasa real | Orden por pares informativos | Top-model correcto |
|---|---:|---:|---:|---:|---:|---:|
| MIRT adaptado | 0,2698 [0,2411; 0,2996] | 0,8048 [0,7221; 0,8916] | 0,1899 | −0,0918 | 0,5217 [0,4309; 0,6117] | 0,3688 |
| Prevalencia train por modelo | 0,2314 [0,2194; 0,2435] | 0,6534 [0,6269; 0,6815] | 0,0854 | +0,0854 | 0,6902 [0,6056; 0,7742] | 0,4500 |
| Logística contextual | **0,2174 [0,2032; 0,2325]** | **0,6240 [0,5922; 0,6577]** | **0,0430** | −0,0104 | 0,6902 [0,6056; 0,7742] | 0,4500 |

Las 184 comparaciones por pares informativas son pares consulta×modelos cuya corrección binaria difiere; empates de outcome no informan el orden. Logística mejoró frente a prevalencia en Brier por −0,01395 (IC95% pareado [−0,02615; −0,00184]) y log-loss por −0,02934 ([−0,05479; −0,00405]), pero no mejoró el orden por pares (diferencia 0). Frente a MIRT, la mejora pareada fue −0,05239 en Brier ([−0,07266; −0,03214]) y −0,18080 en log-loss ([−0,24842; −0,11747]).

Resultados Brier por tipo de test:

| Tipo | MIRT | Prevalencia train | Logística contextual |
|---|---:|---:|---:|
| Biología | 0,257 | 0,222 | 0,220 |
| Matemáticas | 0,201 | 0,248 | 0,167 |
| Psicología | 0,332 | 0,227 | 0,255 |
| Historia EE. UU. | 0,288 | 0,228 | 0,228 |

La logística mejora frente a prevalencia en calibración general y Brier, con variación por materia: la mejora más marcada aparece en matemáticas; psicología empeora. La clasificación del mejor modelo por consulta no cambia en tasa agregada frente a prevalencia (ambos 45%). Por tanto, mejora la estimación de probabilidades, pero no aporta una mejor ordenación agregada de modelos en estos datos.

## Calidad organizativa

Exactitud macro equilibrada de las cuatro materias; cada celda resume la media en las 20 semillas. El orden de las tres políticas en cada vector es **ILP / greedy / independiente reparado**.

| Lotes | Presupuesto | MIRT | Prevalencia train | Logística contextual |
|---|---:|---:|---:|---:|
| Homogéneos | 0,35 | 0,3250 / 0,3278 / 0,2991 | 0,4359 / 0,4356 / 0,4359 | 0,4094 / 0,3878 / 0,3872 |
| Heterogéneos | 0,35 | 0,3244 / 0,3247 / 0,2953 | 0,4309 / 0,4213 / 0,4219 | 0,4247 / 0,4194 / 0,4194 |
| Homogéneos | 0,70 | 0,3681 / 0,3688 / 0,3694 | 0,4500 / 0,4500 / 0,4500 | 0,4500 / 0,4500 / 0,4500 |
| Heterogéneos | 0,70 | 0,3681 / 0,3694 / 0,3700 | 0,4500 / 0,4500 / 0,4500 | 0,4500 / 0,4500 / 0,4500 |

La logística contextual elevó la exactitud frente a MIRT en todas las celdas, típicamente 6–12 puntos. Sin embargo, a presupuesto 0,35 el predictor constante obtuvo más exactitud que la logística: diferencia logística−prevalencia para ILP −2,66 pp en homogéneos (IC95% por consulta [−5,59; +0,06]) y −0,63 pp en heterogéneos (IC [−2,13; +0,75]). A presupuesto 0,70 ambos predictores asignaron todas las consultas al modelo de mayor calidad de entrenamiento y alcanzaron 0,45; ILP, greedy y router coincidieron.

Con predictor contextual y lote homogéneo a 0,35, el ILP superó al greedy en **2,16 pp** (IC95% por empaquetado [+1,63; +2,72], por consulta [+0,72; +3,78]) y al router reparado en **2,22 pp** (por empaquetado [+1,63; +2,81], por consulta [+0,75; +3,88]). En lotes heterogéneos, ILP−greedy fue +0,53 pp (IC por consulta [−1,34; +2,56]), compatible con cero. Con MIRT, ILP−greedy fue −0,28 pp homogéneo y −0,03 pp heterogéneo; con prevalencia, +0,03 pp y +0,97 pp, respectivamente, y el IC por consulta de este último incluyó cero. La ventaja ILP no se reproduce uniformemente al cambiar predictor o packing.

Las decisiones contextual-logística difirieron de MIRT en 51–59% de las parejas consulta×packing a presupuesto bajo; su cambio emparejado de exactitud fue positivo en todas las celdas. Frente a prevalencia, la logística cambió 13% de decisiones en lote heterogéneo y 25% en homogéneo a presupuesto bajo; el cambio de exactitud fue negativo. A presupuesto alto, prevalencia y logística eligieron el mismo modelo para todas las consultas. Son asociaciones de trayectorias deterministas emparejadas, no una descomposición causal del efecto mediado por cada decisión.

Las tres políticas cumplen en todos los lotes el presupuesto **predicho**. La latencia observada conserva el proxy local del piloto anterior y continúa sin ser un coste contractual; los resultados por política y condición están en el JSON, incluyendo distribución de modelos, latencia medida y cumplimiento observado.

## Conclusión

La debilidad MIRT sí condicionó materialmente el primer resultado: al sustituirla por una regresión logística validada solo en train, la calidad organizativa aumentó en todas las celdas. La mejora del predictor frente a MIRT también aparece en decisiones que cambian y obtienen mayor exactitud. No obstante, el predictor contextual de menor Brier no superó al predictor constante en rendimiento organizativo bajo los presupuestos restrictivos. La calidad probabilística y la utilidad de asignación son distintas.

La conclusión sobre ILP frente a greedy cambia solo en un régimen: con logística contextual, lote homogéneo y presupuesto 0,35 aparece una mejora local cuantificable; con lote heterogéneo no es concluyente, y con presupuesto 0,70 las políticas convergen. La evidencia no justifica afirmar una ventaja general del ILP. El resultado está limitado por 160 consultas, cuatro materias, tres modelos pequeños, las categorías de tarea no vistas durante el ajuste, la predicción de costes imperfecta y múltiples contrastes exploratorios sin ajuste por multiplicidad. No basta para una afirmación publicable autónoma.

## Artefactos

- Predictor y políticas reutilizadas: [`llm_routing_pilot.py`](../../src/hls/llm_routing_pilot.py).
- Runner correctivo: [`run_hls_budgeted_llm_routing_predictor_recheck.py`](../../experiments/run_hls_budgeted_llm_routing_predictor_recheck.py).
- Pruebas: [`test_hls_llm_routing_pilot.py`](../../tests/test_hls_llm_routing_pilot.py).
- Resultados nuevos, separados del piloto original: [`hls_budgeted_llm_routing_predictor_recheck/`](../../results/experiments/hls_budgeted_llm_routing_predictor_recheck/).
