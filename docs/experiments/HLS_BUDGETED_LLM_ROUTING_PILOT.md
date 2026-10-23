# HLS — Piloto de asignación adaptativa de consultas bajo presupuesto

**Ejecución:** 23/10/2026

**Estado:** piloto completado; resultados exploratorios, no evidencia de superioridad general.

## 1. Pregunta y alcance

¿Con un predictor de calidad y costes compartido, la asignación conjunta de modelos a un lote heterogéneo mejora la calidad frente a reglas factibles sencillas bajo un presupuesto común? Se separa la predicción de calidad/coste de la política que asigna cada consulta. El análisis no atribuye al ILP una ventaja por usar información de lote que otros métodos no reciban: todos reciben la misma matriz consulta×modelo y presupuesto del lote.

## 2. Datos y procedencia

La licencia de xRouteBench `llmrouter_generic` no pudo establecerse con suficiente claridad a partir de sus [metadatos accesibles](https://huggingface.co/datasets/ulab-ai/xRouteBench); por la condición del encargo se usó el benchmark alternativo MMLU, cuya ficha declara MIT. Se fijaron las revisiones de datos y modelos en el artefacto de resultados. Los pesos usados declaran Apache-2.0: SmolLM2-360M-Instruct, Qwen2.5-0.5B-Instruct y SmolLM2-1.7B-Instruct. Véanse las fichas de [MMLU](https://huggingface.co/datasets/cais/mmlu), [SmolLM2-360M](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) y [Qwen2.5-0.5B](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct).

Se muestrearon 200 preguntas de `auxiliary_train` (160 ajuste, 40 calibración) y 40 preguntas de cada uno de cuatro sujetos oficiales de `test`: biología, matemáticas, historia de EE. UU. y psicología. Total test: 160 consultas equilibradas por sujeto. Los modelos contestaron localmente mediante generación greedy, máximo ocho tokens; la métrica binaria es coincidencia exacta de la letra A–D. Salidas sin letra parseable cuentan como incorrectas. No se convirtieron métricas continuas ni se impusieron umbrales de calidad.

Se construyeron lotes de diez consultas: homogéneos por sujeto y heterogéneos equilibrados (dos consultas por sujeto más dos plazas repartidas). Se repitió el empaquetado con 20 semillas emparejadas. Los presupuestos fueron 0,35 y 0,70 de la distancia entre asignar cada consulta al modelo de menor latencia predicha y al de mayor latencia predicha. Cada celda de política procesa las mismas 160 consultas; las políticas comparten el predictor, costes predichos y presupuesto. La partición test no interviene en el ajuste/calibración.

## 3. Predictor, costes y mecanismos

El predictor es una adaptación MIRT de IRT-Router: para consulta `i` y modelo `m`, estima `p(im)=sigmoid(theta_m · a_i - b_i)`. El texto de pregunta y opciones se representa con hashing fijo; `a_i` y `b_i` dependen de rasgos del texto y `theta_m` se ajusta con los 160 ejemplos de entrenamiento. El artículo original usa embeddings BERT y un mecanismo de warm-up semántico; esta ejecución no reproduce esos componentes. IRT-Router fue publicado en ACL 2025 y su código está disponible [en el repositorio de autores](https://aclanthology.org/2025.acl-long.761/) ([código](https://github.com/Mercidaiha/IRT-Router)).

El coste es una regresión afín, independiente por modelo, de tokens de entrada a segundos de generación local, ajustada solo en entrenamiento. Es una aproximación de latencia local de llamada individual, no coste monetario ni latencia de servicio concurrente. La formulación conjunta es un ILP de asignación binaria, una elección modelo/consulta, maximiza suma de calidad predicha con una restricción de suma de latencias predichas. Es una adaptación de asignación por lotes; no implementa el componente robusto de incertidumbre ni restricciones de capacidad/concurrencia del trabajo CAIS 2026 *Robust Batch-Level Query Routing* ([publicación ACM](https://doi.org/10.1145/3786335.3813134), [preprint](https://arxiv.org/abs/2603.26796)).

Políticas comparadas:

- `independent_repaired`: maximiza por consulta `q − λc` y degrada opciones hasta que cumple el presupuesto.
- `greedy_feasible`: empieza en las opciones más baratas y compra mejoras factibles de calidad/coste.
- `batch_ilp`: óptimo exacto para la suma de calidades **predichas** bajo el presupuesto predicho.
- `fixed_economic`: modelo con menor latencia media observada en entrenamiento.
- `fixed_quality`: modelo con mayor exactitud observada en entrenamiento; puede violar el presupuesto predicho.
- `test_oracle`: referencia retrospectiva que conoce respuestas test; no es desplegable.

## 4. Resultados

El predictor MIRT convergió en 773 iteraciones. En test, su Brier fue 0,2698 frente a 0,2314 de un predictor constante por modelo con prevalencias de entrenamiento. La calidad media predicha fue 0,2631 frente a 0,3542 observada. El RMSE de latencia fue 0,414 s por consulta-candidata. Por tanto, el predictor compartido funcionó mal en esta muestra; las comparaciones de asignadores miden su comportamiento bajo una señal común imperfecta, no el potencial de routing con calidad/coste bien calibrados.

Exactitud global es la media equilibrada de los cuatro sujetos. IC95% de exactitud incluye dos vistas: bootstrap estratificado por consulta (incertidumbre sobre la muestra fija) y bootstrap emparejado de los 20 empaquetados (sensibilidad al packing, condicionado a las mismas consultas y respuestas). Valores principales:

| Lotes | Presupuesto | Política | Exactitud | IC95% por packing | IC95% por consulta | Presupuesto estimado medio/lote (s) | Latencia observada media/lote (s) | Lotes dentro de presupuesto predicho / latencia observada |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| Homogéneos | 0,35 | ILP | 0,3250 | [0,3178; 0,3316] | [0,2616; 0,3881] | 6,503 | 5,923 | 1,000 / 0,750 |
| Homogéneos | 0,35 | Greedy | 0,3278 | [0,3216; 0,3341] | [0,2631; 0,3916] | 6,503 | 5,848 | 1,000 / 0,759 |
| Homogéneos | 0,35 | Independiente+reparación | 0,2991 | [0,2938; 0,3047] | [0,2328; 0,3653] | 6,503 | 5,908 | 1,000 / 0,744 |
| Heterogéneos | 0,35 | ILP | 0,3244 | [0,3178; 0,3316] | [0,2609; 0,3878] | 6,505 | 5,940 | 1,000 / 0,741 |
| Heterogéneos | 0,35 | Greedy | 0,3247 | [0,3194; 0,3300] | [0,2613; 0,3881] | 6,505 | 5,888 | 1,000 / 0,744 |
| Heterogéneos | 0,35 | Independiente+reparación | 0,2953 | [0,2919; 0,2988] | [0,2303; 0,3606] | 6,505 | 5,950 | 1,000 / 0,759 |
| Homogéneos | 0,70 | ILP | 0,3681 | [0,3659; 0,3703] | [0,2975; 0,4419] | 7,132 | 6,354 | 1,000 / 0,787 |
| Homogéneos | 0,70 | Greedy | 0,3688 | [0,3672; 0,3706] | [0,2984; 0,4425] | 7,132 | 6,354 | 1,000 / 0,787 |
| Heterogéneos | 0,70 | ILP | 0,3681 | [0,3656; 0,3706] | [0,2978; 0,4403] | 7,118 | 6,342 | 1,000 / 0,847 |
| Heterogéneos | 0,70 | Greedy | 0,3694 | [0,3672; 0,3719] | [0,2991; 0,4425] | 7,118 | 6,331 | 1,000 / 0,847 |

En presupuesto 0,35, el ILP supera a `independent_repaired` en 2,6–2,9 puntos porcentuales; los intervalos emparejados por consulta excluyen cero en ambos tipos de lote. No supera a greedy: diferencia ILP−greedy −0,28 pp en homogéneos (IC consulta [−1,00; 0,44]) y −0,03 pp en heterogéneos (IC [−0,78; 0,75]). En presupuesto 0,70 las diferencias ILP−greedy son −0,06 pp y −0,13 pp; ambos IC por consulta contienen cero. Las ganancias modestas frente al router independiente no establecen una ventaja general del optimizador conjunto.

El modelo fijo económico obtuvo 0,2313 en las cuatro celdas; el fijo de mayor calidad de entrenamiento obtuvo 0,4500. Este último cumplió el presupuesto **predicho** en 25% de los lotes homogéneos y 0% de los heterogéneos a 0,35; a 0,70 fue factible según el coste predicho. La cota oracular obtuvo 0,6478–0,6625, pero usa respuestas test y solo mide margen retrospectivo. Calidad por materia en lotes heterogéneos:

| Presupuesto | Política | Biología | Matemáticas | Psicología | Historia EE. UU. |
|---:|---|---:|---:|---:|---:|
| 0,35 | ILP | 0,337 | 0,198 | 0,489 | 0,274 |
| 0,35 | Greedy | 0,339 | 0,198 | 0,499 | 0,264 |
| 0,70 | ILP | 0,374 | 0,196 | 0,528 | 0,375 |
| 0,70 | Greedy | 0,375 | 0,200 | 0,528 | 0,375 |

El reparto heterogéneo ILP a 0,35 asignó 44,3% al modelo grande, 37,0% al económico y 18,7% a Qwen.

## 5. Interpretación y límites

**Hechos observados:** el ILP respetó el presupuesto de coste predicho en todas las celdas. El greedy logró exactitud prácticamente igual a la del ILP, con diferencias que no se distinguen de cero por bootstrap de consultas. El router independiente reparado quedó por debajo del ILP y greedy en el presupuesto más restrictivo. Los lotes homogéneos y heterogéneos dieron resultados agregados cercanos; no aparece aquí una interacción clara por composición.

**Interpretación compatible:** la selección conjunta sí puede mejorar sobre una regla independiente con reparación bajo presupuesto restrictivo, pero en esta instancia el greedy captura prácticamente todo ese beneficio. El contraste ILP/greedy mantiene predictor e información del lote comunes y, por tanto, no apoya una mejora relevante atribuible a resolver exactamente el ILP. La asignación por tarea no indica un intercambio claro de calidad entre sujetos, aunque matemáticas permanece como el estrato de menor exactitud.

**Limitaciones:** cuatro materias y 40 consultas cada una; tres modelos pequeños; una plantilla de prompt y generación de ocho tokens; un único entorno de hardware y secuencia de inferencia. Latencias de test no son costes contractuales y la regresión no calibró bien: aunque la factibilidad estimada fue 100% para ILP/greedy/router reparado, la fracción de lotes que también cumple usando latencia observada fue 64–85% en estas celdas. Fijo y routing evaluados a partir del mismo subconjunto test finito. Los CIs por reempaquetado condicionan respuestas y consultas; no sustituyen replicación en datasets/modelos. La MIRT es adaptación, no réplica exacta de IRT-Router; el ILP no replica la robustez del artículo de routing por lotes.

**Potencial publicable:** este piloto no basta como resultado publicable autónomo ni demuestra novedad. La literatura ya estudia routing por consulta y asignación robusta por lote; aquí el hallazgo principal es negativo y local: con este predictor/costeo, ILP no mejora de forma medible a un greedy sencillo. La evidencia útil es la necesidad de evaluar conjuntamente calibración de coste, composición de lotes y asignador, sin atribuir las diferencias al ILP únicamente.

## 6. Reproducibilidad y artefactos

El diseño produjo 480 `ExperimentRun` v1 y 76.800 filas de asignación (20 packings × 2 composiciones × 2 presupuestos × 6 políticas × 160 consultas). Semillas de selección y empaquetado, revisiones de modelos/dataset, versiones de software, hashes de fuentes y hashes de artefactos están en el JSON. Resultados completos, asignaciones y outcomes de modelos están bajo [`results/experiments/hls_budgeted_llm_routing_pilot/`](../../results/experiments/hls_budgeted_llm_routing_pilot/).

Runner: [`run_hls_budgeted_llm_routing_pilot.py`](../../experiments/run_hls_budgeted_llm_routing_pilot.py). Implementación local: [`llm_routing_pilot.py`](../../src/hls/llm_routing_pilot.py). Pruebas: [`test_hls_llm_routing_pilot.py`](../../tests/test_hls_llm_routing_pilot.py).
