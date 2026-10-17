# Selección de mecanismos siguientes para HLS

**Fecha:** 2026-10-17. **Estado:** recomendación documental; no autoriza implementación ni campañas. **Alcance:** comparación conjunta de MixLLM, System-1.x y Baccara–Lee–Yariv con el laboratorio actual. HLS permanece **PARTIAL**.

## Resumen de la decisión

Se recomienda seleccionar **un solo mecanismo para la siguiente implementación**: un router contextual inspirado en la separación de MixLLM entre predicción de calidad, predicción de coste y decisión a partir del feedback del candidato seleccionado. No se propone reproducir MixLLM completo ni reutilizar sin cambios sus ecuaciones, recursos o datos. La adaptación requeriría primero un contrato explícito de contexto, candidatos, calidad observada, coste medido y feedback parcial. La estimación de incertidumbre y la penalización de cola se mantienen fuera hasta que existan señales y unidades válidas.

No se selecciona un segundo mecanismo. Baccara y System-1.x se conservan como opciones para investigaciones separadas: sus estados y restricciones centrales no están representados por el runner HLS actual. Esta recomendación no cambia fechas, prioridades generales ni el calendario operativo; las fechas ya registradas en el plan permanecen vigentes. Cualquier implementación requerirá autorización propia.

## Base de evidencia y lenguaje

**Hechos verificados en HLS:** el estado N×K usa matrices de agentes × competencias y problemas con requisitos K-dimensionales; el runner ejecuta una secuencia de problemas exógenos; el protocolo de políticas separa vista de decisión, memoria y parámetros; `nembhard_adaptive` mantiene estimaciones de productividad por celda a partir de observaciones y usa exploración epsilon-greedy. Véanse `src/hls/hls_lab_nk_geometry.py` (`OrganizationConfigNK`, `ProblemSpecNK`, `ProductiveAllocationNK`), `src/hls/hls_lab_nk_execution.py` (`run_nk_production_sequence`), `src/hls/hls_lab_nk_policies.py` (`NKCoordinationPolicy`, `NKPolicyDecisionView`) y `src/hls/hls_lab_nk_nembhard_adaptive.py` (`NembhardAdaptiveRouterConfigNK`, `ProductivityEstimatorStateNK`, `update_productivity_estimator_nk`).

**Hechos de las fuentes/auditorías:** la matriz de comparabilidad y la auditoría de routing registran las unidades de decisión, ecuaciones y necesidades de datos de cada artículo. La trazabilidad y versiones locales se mantienen en `docs/literature/ADAPTIVE_TRAINING_REFERENCE_REGISTER.md`; los PDF originales permanecen locales. MixLLM está disponible como artículo editorial NAACL 2025; System-1.x como artículo editorial ICLR 2025; para Baccara–Lee–Yariv la copia local es el manuscrito de autor de 2022 asociado al artículo de 2023. La auditoría comparativa advierte que no constituye extracción completa del manuscrito de Baccara. No se afirma reproducción de ninguno.

**Inferencias y propuestas:** las valoraciones de reutilización, dificultad y prioridad de abajo son decisiones de ingeniería para HLS, no conclusiones de los artículos.

## Comparación de mecanismos

| Investigación | Problema y mecanismo original | Estado/observables de decisión | Aprendizaje o adaptación | Restricciones y medidas originales | Correspondencia HLS y brechas | Recomendación |
|---|---|---|---|---|---|---|
| **MixLLM** | Enrutar cada consulta a un LLM candidato, equilibrando calidad prevista, coste de tokens, incertidumbre del predictor y espera. La decisión original puntúa consulta × modelo y selecciona un modelo. | Embedding de consulta; modelo candidato; predicción de calidad y coste; covarianza/incertidumbre por modelo; carga/espera. Feedback de calidad/coste del modelo elegido. | Actualiza predictores/router con feedback del candidato usado; no es aprendizaje de competencia interna del LLM. | Calidad, coste monetario de tokens y espera/latencia pertenecen a escalas distintas; el artículo aplica su score con pesos explícitos y datos/modelos concretos. Métricas: calidad, coste/latencia y resultados de routing. | **Parcialmente reutilizable:** seam de decisión de política, vistas informacionales, memoria, repetición de demanda y convención de semilla. `nembhard_adaptive` ya tiene observación, estadística online y exploración, pero estima productividad escalar por celda con media Welford. No tiene embedding/contexto de tarea × candidato, predictores de calidad/coste, calibración, precios de tokens ni cola. Calidad LLM no equivale a output/competencia HLS; las reglas de Nembhard no implementan el score MixLLM. | **Seleccionar una adaptación acotada:** predictor contextual de resultado/calidad y coste por candidato con actualización usando solo feedback observado del seleccionado. Mantener incertidumbre como diagnóstico inicial; no añadir término de cola sin cola real. |
| **System-1.x** | Componer planificación rápida y profunda dentro de una misma tarea: identificar un tramo/subobjetivo para búsqueda profunda y concatenar subplanes rápidos y profundos. El controlador y los planificadores se entrenan con planes/trazas. | Estado inicial, meta, trayectoria/plan, subobjetivos, estimación de dificultad y presupuesto de búsqueda. La decisión es composición/secuencia de plan, no selección de un único proveedor por consulta. | Entrenamiento supervisado del controlador de descomposición y de los planificadores fast/deep; el parámetro `x` controla partición/composición del entrenamiento, no probabilidad de routing online. | Requiere dominio de planificación, estados/operadores, planes válidos, trayectorias de búsqueda y presupuesto comparable. Métricas publicadas incluyen validez del plan y estados explorados. | **No directamente reutilizable como mecanismo:** HLS representa problemas por vectores de requisitos y asignaciones por periodo; no representa subobjetivos, planes, operadores ni validador de plan. Experimentos FAST/DEEP/META existentes son una línea distinta y no equivalen a System-1.x. | **No seleccionar ahora.** Si se plantea, debe ser una extensión de planificación con benchmark/validador propios, no una política N×K disfrazada. |
| **Baccara, Lee y Yariv** | Asignar llegadas entre proveedores junior y senior con diferente calidad. El servicio senior enfrenta una cola; el trabajo junior produce entrenamiento que cambia capacidad de servicio futura. Compara asignación centralizada y elección descentralizada bajo información/colas distintas. | Tasa de llegadas, mezcla junior/senior, cola/espera senior, masa/capacidad senior y tecnología de entrenamiento. Parte de la política depende de si se observa la cola. | Formación en el trabajo transforma asignaciones actuales en capacidad de servicio futura; no es transferencia dirigida entre pares ni MIS-v2. | Restricción de estabilidad/servicio, espera FIFO, calidad distinta y welfare social/privado; métricas incluyen bienestar y espera. El manuscrito consultado es versión de autor 2022; una especificación de reproducción requiere revisión completa. | **Sin soporte estructural actual:** el entorno HLS genera un problema por periodo y no tiene llegadas concurrentes, colas FIFO, tasa de servicio, espera, junior→senior o utilidad/welfare del modelo. Esfuerzo/budget HLS no equivale a tiempo de cola ni capacidad de servicio. | **No seleccionar ahora.** Es candidato a un modelo/benchmark de colas separado; no añadir cola al runner de episodios ni reinterpretar MIS/recursos. |

Referencias de las auditorías: `docs/literature/audits/HLS_ROUTING_AUDIT_2026-10-17.md` (MixLLM ecs. 1–20; System-1.x algoritmo 1 y composición); `docs/literature/audits/HLS_CROSS_MODEL_COMPARABILITY_MATRIX_2026-10-17.md` (matriz de estados, unidades y comparaciones); `docs/literature/audits/HLS_CODE_REUSE_AND_INTEGRATION_AUDIT_2026-10-17.md` (bloqueos de integración). Para Baccara, revisar el texto completo y fijar la versión antes de una especificación matemática de implementación.

## Reutilización, dependencias y aceptación del mecanismo recomendado

### Reutilizable sin alterar semántica

- Contrato de decisión/memoria de política y ejecución secuencial: patrón de `NKCoordinationPolicy` y `run_nk_production_sequence`; requiere un adaptador de contexto/candidatos, no asumir que `ProblemSpecNK` ya es un embedding de consulta.
- Reproducción de demandas congeladas, semillas separadas, trazas y tests de replay.
- Patrón de observación/posterior online de `nembhard_adaptive`, solo como infraestructura. Su estimador y su ecuación no deben renombrarse como MixLLM ni reutilizarse como predictor de calidad/coste sin pruebas de correspondencia.

### Dependencias previas a implementación

1. Declarar el universo de consultas/contextos y candidatos, con una colección común congelable y partición de entrenamiento/evaluación.
2. Definir calidad observada y coste observado en unidades propias; coste monetario no se combina con CES ni esfuerzo HLS mediante coeficientes arbitrarios.
3. Definir feedback disponible únicamente para el candidato seleccionado y cómo se tratan respuestas faltantes/errores.
4. Establecer predictores y calibración por candidato/contexto, más inicialización y actualización reproducibles. Solo después decidir si la incertidumbre se usa en la selección o se reporta.
5. Mantener un baseline de selección fija y un baseline contextual sin aprendizaje con idéntico presupuesto informacional; probar primero predicción y ranking en trazas controladas.

### Criterios de aceptación propuestos

- La vista de decisión no contiene outcomes futuros ni etiquetas no observadas; la traza diagnóstica se mantiene separada.
- La elección es factible y determinista dado el mismo estado, excepto exploración explícita con stream propio.
- Los estimadores de calidad y coste se validan por separado frente a observaciones sintéticas controladas y un conjunto de prueba retenido; se informa error/calibración, no solo reward agregado.
- La actualización cambia exclusivamente con el feedback recibido; un control de feedback bloqueado no cambia parámetros.
- Selección contextual, coste constante y predictores equivalentes ofrecen controles de equivalencia especificados antes de probar adaptaciones.
- Se conservan unidades separadas para calidad, coste y latencia; sin score combinado hasta declarar su regla y justificación, y sin reinterpretar CES.
- No se denomina “MixLLM reproducido”; es “adaptación HLS inspirada en componentes de MixLLM” si difieren datos, arquitectura, score o entrenamiento.

## Priorización conjunta

Escala cualitativa: **alta/media/baja**; complejidad mide integración técnica y metodológica en HLS, no dificultad del artículo.

| Candidato | Utilidad para HLS | Complementariedad con lo existente | Complejidad | Dependencia crítica | Capacidad de evaluación aislada |
|---|---|---|---|---|---|
| MixLLM: predicción contextual de calidad/coste + feedback elegido | Alta para extender el router recientemente implementado a decisiones dependientes del contexto | Alta: añade contexto/candidatos y outcomes distintos sin duplicar el estimador escalar Nembhard | Media-alta | Dataset/query-candidato, medidas de calidad/coste y feedback por acción | Alta una vez fijado el contrato; prediction, calibration y routing pueden verificarse separadamente |
| Baccara: congestión y formación endógena | Alta para preguntas de asignación dinámica | Media: enlaza asignación y desarrollo futuro, pero no el mecanismo de agentes/competencias HLS actual | Muy alta | Modelo de llegadas, cola/servicio, entrenamiento junior→senior y objetivo welfare | Alta solo en un benchmark de colas independiente |
| System-1.x: composición fast/deep intra-tarea | Media para el alcance organizativo actual | Baja-media: comparte asignación de esfuerzo deliberativo, pero no la unidad ni el estado de tareas HLS | Muy alta | Tareas planificables, subgoals, operadores, trazas/planes y verificador | Alta en benchmark propio; baja en HLS N×K actual |

La recomendación de una sola selección minimiza el riesgo de mezclar tres unidades incompatibles (consulta, plan y llegada a cola) y permite aprovechar la infraestructura de router sin reclamar equivalencia matemática. No se elige por novedad o publicabilidad. El valor depende de que se pueda definir el conjunto de consultas y outcomes; sin ello, el mecanismo queda **condicionado**, y la decisión correcta es no iniciar código hasta resolver esa dependencia.

## Alcance de las conclusiones

Si se implementa y valida la adaptación recomendada, HLS podría estudiar cómo predicciones contextuales de calidad/coste y feedback parcial afectan a decisiones de routing en el benchmark declarado. No permitiría concluir superioridad general de MixLLM, aprendizaje de los expertos, valor de enseñanza, eficacia de MIS-v2, equivalencia con CES ni utilidad económica fuera de las unidades observadas. Baccara y System-1.x no quedan refutados ni descartados científicamente: simplemente no se eligen para el siguiente paso técnico de este laboratorio.

**Decisión:** GO para considerar el diseño/implementación posterior del mecanismo MixLLM-inspirado, condicionado al contrato de datos y costes; HOLD para implementarlo hasta autorización. No se añade calendario ni se autoriza una campaña. HLS Laboratory continúa PARTIAL.
