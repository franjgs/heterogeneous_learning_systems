# HLS — Organización dinámica de capacidades heterogéneas

**Ejecución:** 23/10/2026
**Estado:** piloto completado; resultado negativo para la cascada en este régimen.

## Resumen

Se evaluaron selección fija, selección por consulta, escalado FAST→DEEP y combinación de respuestas sobre la muestra test MMLU del piloto previo. Los datos previos contenían letra predicha, acierto, tokens y latencia, pero no respuesta textual completa ni logits/confianza. Se regeneraron las respuestas con las mismas revisiones, prompt y decodificación, capturando además una señal de logits de FAST. Las 480 letras (160 preguntas × 3 modelos) reprodujeron exactamente las archivadas.

Se observa heterogeneidad real en los errores: FAST fue correcto en 22 preguntas donde DEEP falló, y DEEP corrigió 57 errores de FAST. Sin embargo, el voto por pluralidad de tres modelos obtuvo 41,9%, por debajo de DEEP siempre (45,0%). La puntuación de confianza FAST fue débil para ordenar errores. La cascada mejoró sobre FAST al escalar más, pero no superó el punto de calidad de DEEP siempre y ejecutó FAST además de DEEP. En test, el modelo designado FAST por datos de entrenamiento fue más lento en promedio que DEEP, lo que elimina la ventaja de latencia que se esperaba de esa pareja.

**Conclusión:** existe complementariedad de outcomes, pero la combinación por mayoría no la aprovecha y no se identificó una región favorable al escalado por confianza en esta evaluación. El resultado es negativo y local; no generaliza a otras tareas, modelos o infraestructuras.

## 1. Datos y validez de las señales

Los artefactos previos (`model_outcomes.csv`) guardaban `predicted_letter`, `correct`, número de tokens de entrada/salida y `latency_seconds` por pregunta/modelo. No guardaban texto de respuesta, distribución de probabilidades de respuesta ni confianza. La tabla de predicción del router guardaba calidad y coste estimados, no logits del modelo. Las letras sí permiten medir voto; no permiten construir una regla de escalado basada en incertidumbre.

Se usó la revisión MMLU `c30699e8356da336a370243923dbaf21066bb9fe`, modelos y prompt del piloto:

- **Train por tarea:** `all/dev`, cinco preguntas por materia, 20 en total. Se usó exclusivamente para elegir un modelo estático por tarea.
- **Entrenamiento del IRT-Router:** los 160 ejemplos auxiliares de ajuste ya registrados en el piloto, sin outcomes test.
- **Validación:** `all/validation`, selección determinista y equilibrada de 22 preguntas por materia (88 en total), limitada por la cobertura disponible de historia de EE. UU. Se usó para fijar los precios de coste del router y los umbrales de activación; los umbrales de cascada usaron solo la distribución de confianza, no la corrección.
- **Test:** las mismas 160 preguntas oficiales del piloto, 40 por cada una de biología, matemáticas, psicología e historia de EE. UU. Los modelos se volvieron a ejecutar de forma greedy (`max_new_tokens=8`); la coincidencia de letras con el archivo anterior fue **100%**.

La señal observable de cascada es la masa softmax normalizada de la letra generada, calculada en el primer paso de logits como suma de variantes de token `A`/` A` hasta `D`/` D`, condicionada a esas ocho variantes. No se pidió al modelo que declarase su confianza. La señal no es una probabilidad calibrada de corrección: Brier FAST fue 0,2106 en validación y 0,1964 en test; AUC de ordenar errores fue 0,444 en validación y 0,521 en test, cercana al azar. Las etiquetas de corrección solo se incorporaron después para evaluación.

Coste es tiempo medido de generación en MPS local por consulta; excluye carga/tokenización de modelos y supone que los pesos ya están residentes. Se cuentan ambas llamadas de la cascada: (C_{cascade}=C_{FAST}+1[confidence<\tau]C_{DEEP}). Los resultados de test usados para comparar políticas son las mismas salidas reproducidas, no nuevas muestras de respuesta.

## 2. Mecanismos y adaptaciones

### Selección de capacidades: IRT-Router

Se reutilizó el predictor multidimensional de respuesta de la adaptación anterior de IRT-Router. Para consulta (i), modelo (m), el predictor estima:

\[
\hat q_{im}=\sigma(\theta_m^T a_i-b_i),
\]

donde el texto se representa mediante hashing fijo. La forma IRT es la del método publicado [IRT-Router, Song et al., ACL 2025](https://aclanthology.org/2025.acl-long.761/), pero no se reproduce su representación BERT ni el warm-up semántico. Para generar la curva coste-calidad, la selección se adaptó como (m_i=\arg\max_m(\hat q_{im}-\lambda\hat c_{im})); cada (lambda) se eligió en validación para aproximar uno de once niveles de coste predicho. Esa penalización lineal y su calibración por nivel son la adaptación experimental, no se atribuyen como algoritmo original de IRT-Router.

Como comparadores se incluyeron FAST siempre, DEEP siempre y el mejor modelo fijo por tipo de tarea, elegido solo con cinco ejemplos oficiales `dev` por tipo. La política estática eligió DEEP en biología, psicología e historia, y FAST en matemáticas.

### Escalado secuencial: clasificación selectiva con rechazo

La regla publicada de clasificación selectiva acepta la predicción si un score de confianza supera un umbral y la rechaza en caso contrario; Geifman y El-Yaniv estudian este intercambio riesgo-cobertura y control de riesgo en redes profundas ([NeurIPS 2017](https://papers.nips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html)). Aquí se hizo una adaptación explícita: “rechazar” FAST llama a DEEP y devuelve su salida. No se afirma que sea la implementación del algoritmo de control de riesgo del artículo. Los once umbrales se fijaron en validación para aproximar tasas objetivo de activación de DEEP entre 0 y 100%; el test no intervino en su selección.

### Combinación

Se midió una referencia simple de pluralidad de las tres letras. Los empates entre las tres respuestas se resuelven con la respuesta DEEP. Requiere ejecutar las tres capacidades por pregunta y contabiliza la suma de sus latencias; es un comparador, no una política de bajo coste ni una contribución algorítmica nueva.

El oráculo test elige retrospectivamente la respuesta correcta más rápida si hay alguna; si todas fallan, elige la llamada más rápida. Es una cota no desplegable y usa la etiqueta verdadera.

## 3. Diseño e integración HLS

Los roles se fijaron con el conjunto de ajuste `auxiliary_train` archivado: **FAST** es `SmolLM2-360M-Instruct`, menor latencia media train (0,676 s); **DEEP** es `SmolLM2-1.7B-Instruct`, mayor exactitud train (0,569). `Qwen2.5-0.5B-Instruct` completa los candidatos de selección y voto.

Se registraron 804 salidas/confianzas nuevas (20 train por tarea + 88 validación + 160 test, por tres modelos) y 27 políticas/evaluaciones. Cada `ExperimentRun` contiene 160 eventos de decisión; HLS-PEF calcula tasa de éxito, recompensa binaria acumulada y latencia sumada. Se produjeron 4.320 eventos. La política recibe tarea, respuesta FAST y su score; la etiqueta test solo figura en evaluación posterior. Se conservan las curvas y trazas en `results/experiments/hls_dynamic_capacity_organization/`.

Los IC95% se obtuvieron con bootstrap emparejado estratificado por materia, 5.000 remuestreos de las mismas 160 preguntas. Son incertidumbre de muestra condicionada a este test; no replicación entre datasets o modelos. Para latencia, además, el remuestreo no sustituye repeticiones temporales del hardware.

## 4. Resultados

### Puntos principales calidad-coste

Latencia es media de segundos de inferencia por consulta. IC95% de exactitud y latencia son estratificados por consulta/tarea.

| Política | Exactitud (IC95%) | Latencia s/consulta (IC95%) | Llamadas DEEP / tasa | Diferencia emparejada de exactitud vs DEEP (IC95%) |
|---|---:|---:|---:|---:|
| FAST siempre | 0,2313 [0,1688; 0,3000] | 0,5191 [0,4981; 0,5400] | 0 / 0% | −21,88 pp [−31,88; −11,25] |
| DEEP siempre | 0,4500 [0,3813; 0,5250] | **0,4056 [0,3763; 0,4357]** | 160 / 100% | referencia |
| Mejor fijo por tarea | 0,4688 [0,4000; 0,5438] | 0,4401 [0,4130; 0,4676] | 120 / 75% | +1,88 pp [−2,50; +6,25] |
| Cascada, 40% de activación objetivo | 0,3813 [0,3063; 0,4563] | 0,6847 [0,6361; 0,7376] | 74 / 46,25% | −6,88 pp [−14,38; +0,63] |
| Cascada, 80% objetivo | 0,4250 [0,3500; 0,5000] | 0,8660 [0,8173; 0,9171] | 136 / 85% | −2,50 pp [−6,25; +1,25] |
| Cascada, 90% objetivo | 0,4500 [0,3813; 0,5250] | 0,9031 [0,8561; 0,9529] | 150 / 93,75% | 0,00 pp [−2,50; +2,50] |
| Cascada, 100% objetivo | 0,4438 [0,3750; 0,5188] | 0,9217 [0,8770; 0,9667] | 157 / 98,13% | −0,63 pp [−1,88; 0,00] |
| Pluralidad 3 modelos | 0,4188 [0,3500; 0,4938] | 1,4835 [1,4138; 1,5547] | 160 / 100% | −3,13 pp [−7,50; +1,88] |
| Oráculo retrospectivo | 0,6625 [0,5938; 0,7313] | 0,3885 [0,3608; 0,4163] | 90 / 56,25% | +21,25 pp [+15,00; +28,13] |

El oráculo no es una política ejecutable. La totalidad de la curva de 11 umbrales y de 11 niveles de coste del IRT-Router está en `quality_cost_curve_summary.csv` y `results.json`.

Exactitud por tipo de tarea en los comparadores principales:

| Política | Biología | Matemáticas | Psicología | Historia EE. UU. |
|---|---:|---:|---:|---:|
| FAST siempre | 0,200 | 0,225 | 0,275 | 0,225 |
| DEEP siempre | 0,525 | 0,150 | 0,650 | 0,475 |
| Mejor fijo por tarea | 0,525 | 0,225 | 0,650 | 0,475 |
| Cascada, 40% objetivo | 0,525 | 0,200 | 0,500 | 0,300 |
| Cascada, 90% objetivo | 0,525 | 0,200 | 0,625 | 0,450 |
| Pluralidad 3 modelos | 0,450 | 0,175 | 0,625 | 0,425 |

Puntos representativos de la curva del selector IRT (el coste fraccional se ajustó en validación usando calidad/coste predichos; la tabla informa latencia test medida):

| Fracción objetivo de coste predicho | Exactitud test | Latencia s/consulta | Selección de DEEP |
|---:|---:|---:|---:|
| 0,0 | 0,2313 | 0,5191 | 0% |
| 0,3 | 0,3000 | 0,4946 | 40,63% |
| 0,5 | 0,3688 | 0,5131 | 43,13% |
| 1,0 | 0,3688 | 0,5131 | 43,13% |

La selección IRT adaptada llegó a 0,3688 de exactitud con 0,5131 s/consulta en sus mejores niveles observados; los niveles de coste alto se estabilizaron en esa misma asignación. Quedó por debajo de DEEP siempre tanto en exactitud como en latencia test. La selección fija por materia tuvo el punto de mayor exactitud observado entre los mecanismos no oraculares (0,4688), pero su diferencia emparejada con DEEP fue pequeña e incierta, y costó 0,0345 s/consulta más (IC95% pareado [+0,0242; +0,0442]). La elección estática por materia se basa en (n=5) por grupo, así que no debe interpretarse como una política validada para despliegue.

### Complementariedad y tipo de tarea

| Resultado FAST/DEEP en las mismas preguntas test | Consultas |
|---|---:|
| Ambos correctos | 15 |
| Solo FAST correcto (DEEP empeora una respuesta FAST correcta) | 22 |
| Solo DEEP correcto (DEEP corrige FAST) | 57 |
| Ambos incorrectos | 66 |

El contraste pareado DEEP−FAST fue +21,88 pp (IC95% [+11,88; +31,88]). Por materia, FAST/DEEP obtuvo biología 20,0%/52,5% (4 solo FAST y 17 solo DEEP); matemáticas 22,5%/15,0% (8 solo FAST y 5 solo DEEP); psicología 27,5%/65,0% (4/19); historia de EE. UU. 22,5%/47,5% (6/16). Matemáticas ofrece aquí el caso claro donde FAST supera a DEEP en exactitud observada, aunque con solo 40 preguntas y sin una estimación precisa por subgrupo. DEEP también empeoró 22 respuestas que FAST había acertado.

La pluralidad no aprovechó la diversidad: obtuvo 0,4188 y no superó a DEEP (diferencia −3,13 pp; IC95% [−7,50; +1,88]), a un coste 1,4835 s/consulta. Hay complementariedad de errores en la muestra, pero no evidencia de que esta regla de combinación la convierta en una mejora colectiva.

En cascada al objetivo de 90%, entre las 150 llamadas a DEEP hubo 55 correcciones de error FAST y 20 respuestas donde DEEP cambió una respuesta FAST correcta a incorrecta; el resultado neto igualó exactamente a DEEP siempre en exactitud, con 0,4975 s/consulta adicionales. A 100% objetivo quedaron tres preguntas sin escalar por exceder la confianza máxima de validación; la exactitud quedó 0,63 pp por debajo de DEEP siempre. Todos los puntos de la cascada tuvieron menor o igual exactitud que DEEP siempre y mayor latencia.

### Condiciones observadas para selección/escalado

El modelo pequeño fue designado FAST por tener menor latencia train que DEEP (0,676 vs 0,866 s). Sin embargo, en las llamadas test medidas, FAST promedió 0,519 s y DEEP 0,406 s: DEEP fue más rápido en tres de cuatro materias y ligeramente más lento solo en historia. La longitud de salida y el contexto de ejecución hacen que el orden de costes observado no siga el tamaño del modelo. En este test, por tanto, ejecutar FAST antes de DEEP no ahorró latencia; todas las cascadas quedaron dominadas por DEEP siempre o empataron calidad a más del doble de coste.

Frente a FAST siempre, sí hay un intercambio local: la cascada con objetivo de 30% (40% de activación observada) subió exactitud de 0,2313 a 0,3625 (+13,13 pp; IC95% emparejado [+6,25; +20,00]) y añadió 0,1371 s/consulta (IC [+0,1012; +0,1758]). Es una mejora de calidad respecto a FAST, pero no una región no dominada: DEEP siempre alcanza 0,4500 con menor latencia que la cascada. Por eso no constituye una condición favorable de la cascada en la frontera global calidad-coste de este experimento.

Una condición potencialmente favorable a seleccionar por tarea aparece en matemáticas: el ajuste dev eligió FAST para esa materia, cuya exactitud test fue 22,5% frente a 15,0% de DEEP. La muestra train por tarea es solo cinco y el resultado conjunto del selector está dentro del intervalo de diferencia cero frente a DEEP siempre. Esto es compatible con especialización por tarea, pero no demuestra generalización.

## 5. Resultados demostrados, interpretación y preguntas abiertas

### Demostrado en este experimento

1. Las salidas test regeneradas coinciden con las archivadas; los métodos se comparan sobre los mismos outcomes y respuestas de referencia.
2. FAST y DEEP no tienen errores anidados: hay 22 éxitos exclusivos de FAST y 57 de DEEP, con 66 preguntas falladas por ambos.
3. El voto por pluralidad no mejora a DEEP siempre y consume las tres llamadas.
4. La confianza de FAST es poco discriminativa en test (AUC error 0,521); la curva de escalado no supera a DEEP siempre y contabiliza FAST más cada DEEP activado.
5. El orden de latencia train/test se invierte para FAST y DEEP; el tamaño del modelo no fue un sustituto fiable de latencia medida.

### Interpretaciones compatibles con la evidencia

- La elección estática por materia puede capturar un nicho de especialización, aquí visible en matemáticas, pero el pequeño conjunto de entrenamiento impide separar señal de variación muestral.
- Una cascada necesita una señal de dificultad/error alineada con los fallos FAST y una ventaja de coste de FAST; ambas condiciones faltan o son débiles en esta instancia.
- La diferencia entre tasa de corrección y latencia depende de la salida generada, no solo de parámetros o tamaño del modelo.

### No resuelto

- Si otra medida de incertidumbre observable ordenaría mejor los errores sin fuga, o si la misma cascada funcionaría con un FAST que realmente fuera más rápido en serving.
- Si la selección por tarea se replica con más ejemplos y materias.
- Si otra regla de fusión aprovecha la complementariedad observada.
- Si el patrón se mantiene con otros prompts, modelos, hardware, concurrencia o métricas de calidad distintas a la coincidencia exacta de una letra.

## 6. Límites científicos y uso en HLS

El estudio cubre 160 preguntas de cuatro materias y tres modelos locales pequeños; no representa routing de producción. La regresión está condicionada a una muestra test existente, y los intervalos por consulta no miden variación entre modelos, versiones, prompts o equipos. Los cinco ejemplos `dev` por materia hacen inestable la selección estática. Los logits de siguiente token constituyen un proxy, no confianza calibrada ni una garantía de riesgo. Los costes corresponden a generación MPS secuencial con modelos residentes; no incluyen carga, tokenización, precio de API ni concurrencia. La inferencia de todos los modelos se hizo offline para medir outcomes potenciales; el coste de cada política se reconstruyó sumando solo las llamadas que esa política ejecutaría.

La campaña no establece novedad científica ni una estrategia universal. Su utilidad para HLS es metodológica: ilustra cómo separar escenario/capacidades, problema de asignación y escalado, mecanismos de selección/secuencia/combinación y evaluación HLS-PEF; muestra que hay que verificar empíricamente orden de costes, calibración de señales, fallos no anidados y efectos de tarea antes de afirmar complementariedad organizativa.

## 7. Artefactos y reproducción

- Runner: [`run_hls_dynamic_capacity_organization.py`](../../experiments/run_hls_dynamic_capacity_organization.py).
- Mecanismos/estadística local: [`dynamic_capacity_organization.py`](../../src/hls/dynamic_capacity_organization.py).
- Pruebas: [`test_hls_dynamic_capacity_organization.py`](../../tests/test_hls_dynamic_capacity_organization.py).
- Resultados y 27 `ExperimentRun`: [`results/experiments/hls_dynamic_capacity_organization/`](../../results/experiments/hls_dynamic_capacity_organization/), incluidos `results.json`, `quality_cost_curve_summary.csv`, `experiment_runs.json`, `model_outputs_and_confidence.csv.gz` y `artifact_hashes.json`.
- Fuentes de comparación histórica, sin modificación: [piloto de routing presupuestado](HLS_BUDGETED_LLM_ROUTING_PILOT.md) y [revisión predictiva](HLS_BUDGETED_LLM_ROUTING_PREDICTOR_RECHECK.md).

La ejecución es reanudable desde `model_scoring_cache.jsonl`. Dataset, fuentes y artefactos finales están identificados en el manifiesto SHA-256. Los umbrales, precio del router, selección estática, reglas de empate, semilla bootstrap y particiones están registrados en el runner/resultados.
