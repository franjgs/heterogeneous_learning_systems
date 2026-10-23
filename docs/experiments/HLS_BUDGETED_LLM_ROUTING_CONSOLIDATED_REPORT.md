# HLS — Routing de consultas bajo presupuesto: informe científico consolidado

**Cierre de campaña:** 23/10/2026
**Estado:** campaña cerrada; no se ejecutan análisis experimentales adicionales.

## Resumen ejecutivo

Se consolidan el piloto inicial y la repetición correctiva del predictor. En ambos, se asignó cada consulta a un único modelo, maximizando calidad binaria esperada bajo un presupuesto compartido de latencia estimada por lote. El piloto mostró que el ILP no mejoró al greedy con la adaptación MIRT inicial. La revisión corrigió la debilidad predictiva: una regresión logística contextual mejoró Brier y log-loss, pero no superó uniformemente al predictor constante en calidad organizativa. El ILP aventajó al greedy de manera estadísticamente distinguible solo en una celda exploratoria: predictor contextual, lote homogéneo y presupuesto restrictivo. No hay evidencia de ventaja general del ILP ni base suficiente para una afirmación publicable autónoma.

La campaña demuestra una separación práctica entre calidad del predictor y utilidad de la asignación: mejorar la calibración probabilística no garantiza mejores decisiones bajo presupuesto. Los resultados son locales al benchmark, los modelos, el coste proxy y los lotes evaluados.

## 1. Problema y formulación

Sea (i\in I) una consulta del lote y (m\in M) un modelo candidato. El outcome registrado es (y_{im}\in\{0,1\}), definido por coincidencia exacta de la letra A–D con la respuesta de MMLU. El predictor proporciona (\hat q_{im}\), probabilidad estimada de respuesta correcta, y un modelo de coste proporciona (\hat c_{im}\), latencia local estimada. La variable (x_{im}\in\{0,1\}) indica la selección del modelo. Cada consulta recibe exactamente un modelo:

\[
\sum_{m\in M}x_{im}=1\quad(\forall i),\qquad
\sum_{i\in I}\sum_{m\in M}\hat c_{im}x_{im}\le B.
\]

El mecanismo conjunto resuelve

\[
\max_x\sum_{i\in I}\sum_{m\in M}\hat q_{im}x_{im}
\]

sujeto a esas restricciones. Es exacto para el objetivo aditivo y los costes **predichos** de esta formulación; no es un óptimo robusto ante error de predicción ni una garantía sobre latencia real de servicio. Los presupuestos se fijaron en 0,35 o 0,70 del intervalo entre las asignaciones extremas de coste predicho del lote.

No se fusionan respuestas: la posible complementariedad ocurre entre consultas de un lote que se distribuyen entre modelos.

## 2. Datos, mecanismos y adaptaciones

La licencia de `xRouteBench/llmrouter_generic` no pudo establecerse suficientemente; se utilizó MMLU, cuya ficha indica MIT. Los modelos utilizados declaran Apache-2.0. La revisión de MMLU quedó fijada en `c30699e8356da336a370243923dbaf21066bb9fe`:

- `HuggingFaceTB/SmolLM2-360M-Instruct`
- `Qwen/Qwen2.5-0.5B-Instruct`
- `HuggingFaceTB/SmolLM2-1.7B-Instruct`

Se seleccionaron 200 consultas de `auxiliary_train` (160 para ajuste y 40 para calibrar el precio del router independiente) y 160 consultas oficiales de `test`: 40 por materia, biología, matemáticas, historia de EE. UU. y psicología. La inferencia local fue greedy con máximo de ocho tokens. Salidas sin letra parseable se puntuaron como incorrectas. No se transformó F1 ni otra métrica continua a una etiqueta.

| Componente | Implementación y alcance |
|---|---|
| Predictor del piloto | Adaptación de IRT-Router: \(p(y_{im}=1)=\sigma(\theta_m^T a_i-b_i)\), con hashing fijo de texto en lugar de embeddings BERT y sin reproducir su warm-up semántico. Convergió en 773 iteraciones. No es una réplica completa del método publicado. Referencia: [IRT-Router, ACL 2025](https://aclanthology.org/2025.acl-long.761/), [código de autores](https://github.com/Mercidaiha/IRT-Router). |
| Predictor correctivo | Regresión logística L2 sobre texto hash, identidad de modelo, tipo de tarea e interacciones modelo×tarea. (C\in\{0.01,0.1,1,10\}) se seleccionó con Brier en cinco pliegues `GroupKFold` agrupados por consulta, solo con las 160 consultas de ajuste; ganó (C=1). |
| Coste | Regresión afín por modelo de tokens de entrada a segundos de generación local, ajustada en entrenamiento. RMSE test inicial: 0,414 s por consulta-modelo. Es proxy local serial, no precio monetario ni latencia de serving concurrente. |
| `independent_repaired` | Selección independiente mediante (\hat q-\lambda\hat c), seguida de degradación determinista de opciones hasta cumplir el presupuesto predicho. En el correctivo, el parámetro del router se calibró con las mismas 40 consultas auxiliares. |
| `greedy_feasible` | Parte de opciones económicas y añade mejoras factibles según calidad/coste. Comparador presupuestario factible, sin optimización global exacta. |
| `batch_ilp` | Asignación conjunta exacta para la suma de calidades predichas con presupuesto de latencia predicha. Es una adaptación de routing por lotes, no implementa el tratamiento robusto de incertidumbre ni restricciones de capacidad/concurrencia del trabajo [Robust Batch-Level Query Routing](https://doi.org/10.1145/3786335.3813134), [preprint](https://arxiv.org/abs/2603.26796). |
| Referencias del piloto inicial | Modelo fijo económico; modelo fijo de mayor exactitud de entrenamiento; oráculo retrospectivo que usa outcomes test, exclusivamente como cota no desplegable. No se volvieron a ejecutar en la revisión correctiva. |

En la revisión correctiva, las materias de test no aparecían como categorías de tarea en el entrenamiento disponible: `auxiliary_train` solo contenía `mmlu_auxiliary_mixed`. La logística incluye y codifica el campo de tarea, pero no pudo aprender coeficientes específicos para las cuatro materias test no vistas. La separación train/test se mantuvo; no se usaron outcomes test para entrenar, seleccionar hiperparámetros ni decidir asignaciones.

## 3. Diseño y controles

El piloto inicial cruzó lote homogéneo por materia y lote heterogéneo equilibrado, presupuestos 0,35/0,70 y seis métodos, con 20 semillas de empaquetado emparejadas y lotes de 10. Cada método recibió las mismas matrices consulta×modelo de calidad y coste predichos y las mismas consultas. Se registraron 480 `ExperimentRun` y 76.800 filas de asignación.

La corrección mantuvo exactamente las consultas test, outcomes, costes, lotes, presupuestos, reglas y semillas del piloto; verificó la matriz de costes recalculada con tolerancia absoluta (10^{-12}). Cruzó tres predictores con ILP, greedy y router reparado, dos composiciones y dos presupuestos: 720 `ExperimentRun` y 115.200 decisiones. Los resultados se guardaron en un directorio separado. La corrección no volvió a generar inferencias ni reemplazó datos originales.

La incertidumbre predictiva se calculó mediante bootstrap de consultas estratificado por las cuatro materias, emparejando resultados de los modelos sobre las mismas consultas. Las comparaciones organizativas incluyen bootstrap estratificado por consulta y, donde se indica, bootstrap emparejado de los 20 empaquetados, condicionado a esta muestra fija de preguntas y outcomes. Los 480/720 registros de ejecución no se trataron como réplicas independientes. Se examinaron múltiples contrastes exploratorios sin corrección por multiplicidad; los intervalos deben interpretarse en ese contexto.

## 4. Resultados cuantitativos consolidados

### 4.1 Calidad predictiva

| Predictor | Brier (IC95% consulta) | Log-loss (IC95%) | ECE, 10 bins | Media predicha − prevalencia | Orden de modelos por pares (IC95%) | Modelo top correcto |
|---|---:|---:|---:|---:|---:|---:|
| MIRT adaptado | 0,2698 [0,2411; 0,2996] | 0,8048 [0,7221; 0,8916] | 0,1899 | −0,0918 | 0,5217 [0,4309; 0,6117] | 0,3688 |
| Prevalencia train por modelo | 0,2314 [0,2194; 0,2435] | 0,6534 [0,6269; 0,6815] | 0,0854 | +0,0854 | 0,6902 [0,6056; 0,7742] | 0,4500 |
| Logística contextual | **0,2174 [0,2032; 0,2325]** | **0,6240 [0,5922; 0,6577]** | **0,0430** | −0,0104 | 0,6902 [0,6056; 0,7742] | 0,4500 |

La logística menos prevalencia produjo diferencias emparejadas de Brier −0,01395 (IC95% [−0,02615; −0,00184]) y log-loss −0,02934 (IC95% [−0,05479; −0,00405]); la tasa de orden correcto por pares no cambió. Frente a MIRT, la diferencia fue −0,05239 en Brier (IC95% [−0,07266; −0,03214]) y −0,18080 en log-loss (IC95% [−0,24842; −0,11747]); el orden por pares aumentó 0,16848 (IC95% [0,06818; 0,26786]). Había 184 pares consulta×modelos con outcomes distintos que informaban el orden.

| Materia | Brier MIRT | Brier prevalencia | Brier logística |
|---|---:|---:|---:|
| Biología | 0,257 | 0,222 | 0,220 |
| Matemáticas | 0,201 | 0,248 | **0,167** |
| Psicología | 0,332 | 0,227 | 0,255 |
| Historia EE. UU. | 0,288 | 0,228 | 0,228 |

La mejora predictiva no fue uniforme entre materias; psicología empeoró respecto a prevalencia. Tampoco elevó la tasa de selección del mejor modelo sobre la prevalencia: ambas fueron 0,45.

### 4.2 Asignación en el piloto original

Exactitud es macro media de las cuatro materias. En cada celda se muestran ILP / greedy / router independiente reparado:

| Lotes | Presupuesto | ILP | Greedy | Independiente reparado |
|---|---:|---:|---:|---:|
| Homogéneos | 0,35 | 0,3250 | 0,3278 | 0,2991 |
| Heterogéneos | 0,35 | 0,3244 | 0,3247 | 0,2953 |
| Homogéneos | 0,70 | 0,3681 | 0,3688 | 0,3694 |
| Heterogéneos | 0,70 | 0,3681 | 0,3694 | 0,3700 |

En presupuesto 0,35, ILP−greedy fue −0,28 puntos porcentuales (pp; IC95% por consulta [−1,00; +0,44]) en lotes homogéneos y −0,03 pp (IC [−0,78; +0,75]) en heterogéneos. ILP superó al router reparado en +2,59 pp (IC por consulta [+0,41; +4,91]) y +2,91 pp (IC [+0,91; +4,97]), respectivamente. Con presupuesto 0,70, ILP y greedy quedaron separados por menos de 0,2 pp y los intervalos por consulta incluyeron cero. El ILP no mostró ventaja frente al greedy con MIRT.

Las referencias del piloto inicial dieron exactitud 0,2313 para el modelo fijo económico, 0,4500 para el modelo fijo de mayor exactitud de entrenamiento y 0,6478–0,6625 para el oráculo retrospectivo. El fijo de mayor calidad cumplió el presupuesto predicho en solo 25% de los lotes homogéneos y 0% de los heterogéneos con presupuesto 0,35. El oráculo usa respuestas test, por lo que no es una política ejecutable.

### 4.3 Asignación en la corrección del predictor

Exactitud macro. Cada vector presenta ILP / greedy / independiente reparado:

| Lotes | Presupuesto | MIRT | Prevalencia train | Logística contextual |
|---|---:|---:|---:|---:|
| Homogéneos | 0,35 | 0,3250 / 0,3278 / 0,2991 | 0,4359 / 0,4356 / 0,4359 | 0,4094 / 0,3878 / 0,3872 |
| Heterogéneos | 0,35 | 0,3244 / 0,3247 / 0,2953 | 0,4309 / 0,4213 / 0,4219 | 0,4247 / 0,4194 / 0,4194 |
| Homogéneos | 0,70 | 0,3681 / 0,3688 / 0,3694 | 0,4500 / 0,4500 / 0,4500 | 0,4500 / 0,4500 / 0,4500 |
| Heterogéneos | 0,70 | 0,3681 / 0,3694 / 0,3700 | 0,4500 / 0,4500 / 0,4500 | 0,4500 / 0,4500 / 0,4500 |

La logística mejoró la exactitud frente a MIRT en todas las celdas, típicamente 6–12 pp, pero quedó por debajo de prevalencia con presupuesto 0,35. Para ILP, logística−prevalencia fue −2,66 pp en homogéneos (IC95% por consulta [−5,59; +0,06]) y −0,63 pp en heterogéneos (IC [−2,13; +0,75]). A presupuesto 0,70, prevalencia y logística asignaron todas las consultas al modelo de mayor exactitud de entrenamiento; las tres políticas alcanzaron 0,45.

### 4.4 Comparación ILP–greedy y condiciones de ventaja

| Predictor y condición | ILP−greedy | Incertidumbre reportada | Lectura |
|---|---:|---|---|
| MIRT, homogéneo, 0,35 | −0,28 pp | IC95% consulta [−0,97; +0,44] | Sin diferencia distinguible de cero. |
| MIRT, heterogéneo, 0,35 | −0,03 pp | IC95% consulta [−0,75; +0,75] | Sin diferencia distinguible de cero. |
| Prevalencia, homogéneo, 0,35 | +0,03 pp | Diferencia casi nula | Sin ventaja relevante observada. |
| Prevalencia, heterogéneo, 0,35 | +0,97 pp | IC95% consulta [−1,16; +3,19] | Incertidumbre incluye cero. |
| Logística, homogéneo, 0,35 | **+2,16 pp** | IC95% packing [+1,63; +2,72]; consulta [+0,72; +3,78] | Ventaja local observada en esta celda. |
| Logística, heterogéneo, 0,35 | +0,53 pp | IC95% consulta [−1,34; +2,56] | No concluyente. |
| Logística o prevalencia, 0,70 | 0,00 pp | Asignaciones coincidentes | No se observó diferencia entre asignadores. |

Con logística y lote homogéneo a 0,35, ILP−router reparado fue +2,22 pp (IC95% packing [+1,63; +2,81]; consulta [+0,75; +3,88]). Con lote heterogéneo la diferencia frente al greedy no quedó establecida. En otras combinaciones, predictor y empaquetado, la ventaja del ILP desapareció o cambió de magnitud/signo. Así, la condición observada de mejora es estrecha: presupuesto restrictivo, predictor contextual y packing homogéneo; además, forma parte de varios contrastes exploratorios no corregidos por multiplicidad.

Todos los asignadores reparados/factibles cumplieron el presupuesto **predicho**. En el piloto inicial, el cumplimiento bajo latencia local medida fue solo de aproximadamente 64–85% según la celda (74–85% en las celdas destacadas). Por ello, la factibilidad registrada no equivale a cumplimiento de un SLA real.

## 5. Relación entre predicción y organización

**Demostrado en estos datos:** la logística mejoró Brier y log-loss respecto a prevalencia y MIRT; aun así, no mejoró la exactitud de asignación frente a prevalencia bajo el presupuesto restrictivo. La prevalencia superó a logística organizativamente en esas celdas, pese a peor Brier. La logística sí mejoró frente a MIRT en asignación. A presupuesto 0,70, prevalencia y logística convergieron en una asignación constante al modelo de mayor exactitud observada en entrenamiento.

**Compatible con los datos:** la calidad organizativa depende de qué errores probabilísticos afectan las comparaciones coste-calidad y de cómo estas interaccionan con el presupuesto y el lote, no solo del score agregado Brier. El predictor contextual cambió 51–59% de decisiones frente a MIRT en celdas de presupuesto bajo y su exactitud subió; frente a prevalencia cambió alrededor de 25% (homogéneo) y 13% (heterogéneo), pero su exactitud cayó. Estos cambios son diagnósticos descriptivos de decisiones emparejadas, no una identificación causal completa de mediadores.

**No resuelto:** si la diferencia entre predictores se mantendría con categorías de tarea representadas en entrenamiento, más datos, otros modelos o costes operativos; si calibración o ranking es el componente predictivo más útil para otros objetivos; y si la ventaja local del ILP persistiría fuera de esta muestra/packing.

## 6. Diseño, mecanismos y resultado científico: distinciones

### Resultados demostrados

1. En el piloto inicial, MIRT adaptado rindió peor en Brier que el predictor constante; el ILP no superó al greedy de forma distinguible en las cuatro celdas.
2. La regresión contextual mejoró Brier y log-loss sobre los otros predictores, pero no elevó la tasa top-model frente a la prevalencia y no produjo una mejora organizativa uniforme.
3. La calidad organizativa varió con el predictor, el presupuesto y la composición del lote. Una menor pérdida probabilística no implicó mayor exactitud de asignación en todas las condiciones.
4. Solo se observó una ventaja ILP–greedy con intervalo excluyendo cero en la combinación logística/homogéneo/0,35; los restantes contrastes no acreditan una ventaja general.
5. El límite predicho se respetó; la medición de latencia local no lo respetó sistemáticamente.

### Interpretaciones compatibles

- Resolver conjuntamente la asignación puede ayudar frente a una reparación independiente en algunas condiciones de presupuesto, pero el greedy factible captura casi todo el beneficio observado en la mayor parte de las celdas.
- La utilidad de predicciones depende de cómo ordenan alternativas después de incorporar costes y restricciones; Brier, ranking y resultado de decisión miden propiedades distintas.
- La composición del lote puede cambiar qué intercambios son posibles bajo el presupuesto, aunque este diseño no aporta evidencia general sobre un efecto de heterogeneidad.

### Hipótesis no resueltas

- Que el ILP tenga una ventaja general, o que una ventaja local se replique con otros datos/semillas independientes.
- Que la logística contextual sea el predictor preferible en despliegue: faltan categorías de entrenamiento coincidentes y la métrica top-model no mejoró.
- Que el desempeño se traduzca a presupuesto monetario, inferencia concurrente o latencia de producción.
- Que esta combinación de mecanismo y problema aporte novedad científica suficiente frente a la literatura existente.

## 7. Limitaciones y validez

- La selección cambió a MMLU por licencia incierta del benchmark inicialmente propuesto. El resultado se limita a cuatro materias, 40 preguntas por materia y tres modelos pequeños.
- Las consultas test constituyen una muestra fija y modesta; los bootstraps cuantifican incertidumbre de consulta y packing dentro de este diseño, no replicación entre datasets, modelos, hardware o periodos.
- Las materias test no aparecen como clases en el subconjunto de entrenamiento de la corrección. La afirmación de contexto/task-specific está limitada por esa cobertura.
- Los costes son latencias locales seriales estimadas por regresión, con error de predicción; no son dinero ni servicio concurrente. El ILP es óptimo solo para coeficientes predichos y objetivo aditivo.
- El predictor MIRT y el ILP son adaptaciones, no reproducciones completas de los métodos publicados. IRT-Router utiliza componentes semánticos distintos; el artículo robusto de routing por lotes incluye elementos no implementados aquí.
- El oráculo retrospectivo usa outcomes de test y solo es una cota; no debe compararse como política desplegable.
- Hay múltiples comparaciones exploratorias sin ajuste por multiplicidad. La única celda con diferencia ILP–greedy concluyente requiere réplica externa antes de generalizar.
- La mejora del piloto original frente al router reparado no demuestra que optimización exacta sea la causa, pues greedy rindió de forma similar y el predictor común era débil.

El estudio no demuestra novedad científica ni basta como artículo autónomo. Los trabajos previos sobre [IRT-Router](https://aclanthology.org/2025.acl-long.761/) y [routing robusto por lotes](https://doi.org/10.1145/3786335.3813134) ya cubren problemas próximos. La aportación verificable de esta campaña es una evaluación local y controlada de interacción predictor–asignador bajo presupuesto, con resultado negativo para superioridad general del ILP.

## 8. Uso de los resultados en HLS

Esta campaña deja un ejemplo aplicado del flujo HLS: consultas y modelos como escenario/capacidades; asignación de lote bajo presupuesto como problema organizativo; predictor, router, greedy e ILP como mecanismos diferenciados; `ExperimentRun` y HLS-PEF como registro/evaluación independientes. Sus resultados aconsejan mantener separadas la evaluación del predictor, la decisión organizativa y el cumplimiento real de recursos. Son aprendizajes metodológicos para diseños HLS; no validan por sí solos conclusiones generales sobre otras organizaciones.

## 9. Artefactos, procedencia y cierre

La evidencia completa permanece en los informes de cada iteración y sus artefactos, que no se alteran:

- [Informe del piloto inicial](HLS_BUDGETED_LLM_ROUTING_PILOT.md) y [resultados originales](../../results/experiments/hls_budgeted_llm_routing_pilot/).
- [Informe correctivo del predictor](HLS_BUDGETED_LLM_ROUTING_PREDICTOR_RECHECK.md) y [resultados correctivos separados](../../results/experiments/hls_budgeted_llm_routing_predictor_recheck/).
- Implementación: [`llm_routing_pilot.py`](../../src/hls/llm_routing_pilot.py); runners: [`piloto`](../../experiments/run_hls_budgeted_llm_routing_pilot.py), [`corrección`](../../experiments/run_hls_budgeted_llm_routing_predictor_recheck.py); pruebas: [`test_hls_llm_routing_pilot.py`](../../tests/test_hls_llm_routing_pilot.py).

Los JSON de hashes y resultados se conservan en sus directorios originales. El piloto inicial produjo 480 `ExperimentRun`; la corrección produjo otros 720 registros, reutilizando outcomes, no una nueva muestra independiente de respuestas. Se preservan además las tablas de decisiones, métricas por semilla y metadatos originales.

**Conclusión de campaña:** el predictor contextual es mejor en probabilidad calibrada dentro de esta evaluación, pero no se traduce uniformemente en mejor routing; el ILP solo mejora al greedy en una condición local y exploratoria. La campaña queda cerrada. Estos resultados son evidencia contextual, no una recomendación universal de asignador ni una afirmación de novedad.
