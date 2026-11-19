# Estado científico actual de SOCTRA-HLS

## Resumen

SOCTRA-HLS es una aplicación del programa general HLS al triaje asistido por IA y la organización del trabajo humano en un SOC. El artículo para *Electronics* relacionará conceptualmente los resultados previos de triaje automático de SOCTRA con el estudio de organización de analistas, pero ambos se mantienen como marcos experimentales independientes: no se afirma que las predicciones SOCTRA se hayan integrado experimentalmente en las decisiones organizativas. D1 es la referencia descentralizada del estudio organizativo. Existe un simulador funcional, pero sus parámetros operativos son mayoritariamente hipotéticos y no lo convierten en una reproducción cuantitativamente validada de GMV-CERT.

No se ha seleccionado todavía una política organizativa definitiva ni se ha demostrado una mejora de D1 dentro del proceso integrado con triaje IA. Las mejoras observadas en simulación son condicionales a escenarios concretos y deben leerse junto con sus efectos sobre calidad, tiempos, backlog y coste.

## Hoja de ruta científica

### Paso 1 — Consolidación documental: completado

La documentación de la aplicación SOC se consolidó en seis archivos canónicos: [AGENTS.md](AGENTS.md), [README.md](README.md), [SOC_FOUNDATIONS_AND_MODEL.md](SOC_FOUNDATIONS_AND_MODEL.md), [SOC_RESULTS_AND_LESSONS.md](SOC_RESULTS_AND_LESSONS.md), este documento y [GMV_CERT_OPERATIONAL_REFERENCE.md](GMV_CERT_OPERATIONAL_REFERENCE.md). Se eliminaron documentos redundantes después de preservar sus fundamentos, resultados, limitaciones y referencias operativas. La documentación general de HLS mantiene su autoridad y no forma parte de esta consolidación.

### Paso 2 — Verificación científica: completado

La revisión documental y de código confirmó que existe un simulador SOC funcional con gestión de alertas y colas, pools L1/L2, competencias heterogéneas, restricciones temporales, triaje IA simulado y políticas de asignación. Los detalles del modelo y sus fuentes están en [Fundamentos y modelo](SOC_FOUNDATIONS_AND_MODEL.md).

Las competencias, tiempos de servicio, disponibilidad y costes de coordinación son mayoritariamente parámetros sintéticos. SOCTRA permite caracterizar alertas y estudiar modelos de triaje, pero no valida por sí solo la organización operativa ni la capacidad del SOC. D1 permanece congelado como referencia descentralizada inspirada en la descripción cualitativa de GMV-CERT; no se ha demostrado que reproduzca sus procedimientos reales.

Las campañas existentes muestran mejoras y deterioros condicionados por escenario; no existe una estrategia organizativa universalmente superior demostrada. D1-L y D1-S están implementadas y han mejorado el SLA terminal frente a D1 en ciertas condiciones, con posibles efectos adversos en otras métricas y escenarios. No se ha demostrado que ninguna mejore a D1 en el sistema integrado con triaje IA.

La métrica corregida de SLA terminal cuenta la finalización de L2 para alertas escaladas. Los resultados anteriores a esa corrección son históricos y no deben mezclarse con métricas terminales corregidas. Parte de los resultados conserva resúmenes numéricos, pero no todos los artefactos tabulares originales; véase [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md). Los dos experimentos PPO no demostraron superioridad general frente a controles competitivos; esto limita las formulaciones ensayadas, no permite concluir que RL sea inadecuado en general.

La auditoría de este paso consistió en lectura e inspección de documentación, código y artefactos existentes. No incluyó una nueva ejecución de tests, simulaciones ni experimentos. La evidencia y sus condiciones se resumen en [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md).

### Paso 3 — Selección del problema científico: completado

El artículo de *Electronics* relacionará el trabajo previo de clasificación automática de SOCTRA —incluidas detección y falsas alarmas bajo las configuraciones publicadas— con la investigación de organización de analistas. La evaluación organizativa y el triaje SOCTRA son marcos experimentales independientes; esta línea no afirma una integración experimental de predicciones IA en las decisiones de asignación.

**Pregunta seleccionada:** ¿En qué condiciones pueden estrategias sencillas de priorización temporal, especialización y coordinación mejorar el rendimiento colectivo de un SOC respecto a D1?

El propósito es identificar mecanismos organizativos, cuantificar beneficios y compromisos, y establecer bajo qué condiciones operativas funcionan. La prioridad es justificar una mejora concreta, sencilla y reproducible respecto a D1; no se exige superioridad universal. Las posibles mejoras en métricas relevantes deberán acompañarse de la cuantificación de deterioros en otras métricas. Esta es una decisión científica, no un resultado ya obtenido.

Decisiones vigentes:

- D1 permanece congelado como baseline principal.
- El repertorio vigente para el estudio organizativo es D1 y P1–P5. D1-L/D1-S y B0–B4/C0–C2×P0/P1 son formulaciones históricas, no aliases del repertorio actual.
- Las políticas P son mecanismos candidatos; no se ha seleccionado todavía una intervención definitiva ni demostrado mejora experimental frente a D1 con este repertorio.
- D1-S y C0P1 pueden aparecer como referencias históricas complementarias solo si la comparabilidad con la evaluación vigente se establece explícitamente.
- La coordinación global o selectiva podrá estudiarse si resulta útil, pero no es requisito del artículo.
- No se requiere desarrollar un nuevo agente de aprendizaje por refuerzo para el alcance inmediato.
- El aprendizaje y la evolución de competencias humanas quedan fuera del alcance inmediato.
- HLS general sigue siendo un programa de investigación más amplio; el artículo se limita a la aplicación SOCTRA-HLS.
- El simulador no se presentará como reproducción cuantitativamente validada de GMV-CERT.

### Paso 4 — Fundamentación teórica y definición de la contribución: completado documental y conceptualmente

Se formuló el problema como asignación dinámica de alertas a recursos heterogéneos con elegibilidad, deadlines y capacidad limitada. Se documentaron los mecanismos de priorización temporal, competencia, capacidad/especialización y matching selectivo/conjunto; las hipótesis contrastables H1–H5; la contribución prevista; la métrica primaria y sus complementarias; y las condiciones para comparar resultados. El repertorio implementado D1/P1–P5 está definido en [Fundamentos y modelo](SOC_FOUNDATIONS_AND_MODEL.md) y comparte el motor de eventos y métricas. La validación funcional específica y de regresión ejecutó 143 tests; no fue una campaña de rendimiento. Esto cierra la fundamentación e implementación del repertorio, pero no selecciona una política ganadora ni demuestra sus efectos.

### Paso 5 — Validación experimental y artículo: pendiente

Queda pendiente diseñar y ejecutar una comparación reproducible de D1 con las alternativas organizativas seleccionadas, bajo condiciones y parámetros compartidos, escenarios justificados y métricas homogéneas. Se informarán incertidumbre y compromisos entre objetivos. La validación funcional no sustituye esa campaña ni establece qué política mejora el rendimiento.

## Qué sigue siendo desconocido

1. Definición operativa de llegada y zona horaria por fuente/cliente, y relación entre filas SOCTRA y trabajo efectivamente atendido.
2. Inicio, parada, espera, pausa, reasignación, handoff, cierre terminal y retrabajo por alerta.
3. SLA contractuales por prioridad/cliente: reloj, evento final, pausas, horario, prioridad cambiante y tratamiento de pendientes o reaperturas.
4. Roster L1/L2/L3 por turno, ausencias, disponibilidad, carga paralela, reglas de transferencia y elegibilidad efectiva.
5. Medidas válidas de competencia por tarea, calidad adjudicada y dificultad; `tramitador` o número de cierres no las proporcionan.
6. Si los mecanismos P1–P5 mejoran resultados frente a D1 y bajo qué condiciones. El nuevo repertorio aún no se ha comparado en campaña.
7. Relación entre recomendación IA, exposición, decisión humana efectiva y tiempo/capacidad liberada; las evaluaciones organizativas no integran experimentalmente las predicciones SOCTRA.
8. Costes reales de coordinación y servicio, además de la viabilidad operativa de latencia, matching o información compartida.
9. Disponibilidad y autorización de publicación del informe original del PI de 6-11-2026 y de estadísticas de la fuente. La referencia cualitativa disponible advierte que el informe original no se encontró en el repositorio.

## Clasificación de conclusiones

| Clase | Afirmación actual |
|---|---|
| Hecho documentado | El extracto SOCTRA contiene volumen, timestamps, categorías y marcas de proceso; no hay registros de trabajo humano suficientes para reconstruir servicios. La descripción de GMV-CERT disponible es cualitativa y su fuente primaria no está en el repositorio. |
| Resultado experimental | En escenarios y semillas publicados, algunas estrategias cambian SLA, calidad modelada, cola o recompensa según carga, competencias y costes. Son resultados de simulación bajo las configuraciones descritas en [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md). |
| Decisión de investigación | El artículo relacionará conceptualmente el triaje SOCTRA previo y el estudio organizativo; sus evaluaciones se mantienen independientes. D1 queda congelado como referencia y no se exige superioridad universal. |
| Hipótesis | Roster, competencia, servicio, deadlines terminales, disponibilidad, escalado, IA simulada y costes representan configuraciones plausibles. |
| Desconocido | Si esas configuraciones describen GMV-CERT; si D1-L o D1-S mejoran el proceso integrado; y qué modificación ofrece una contribución defendible. |
| Obsoleto o condicionado | Las métricas de SLA de informes previos que computaron finalización L1 para casos escalados no equivalen a SLA terminal. Se conservan como resultados históricos y no se mezclan con la métrica corregida. |

## Estado hacia *Electronics*

La contribución organizativa aún no está demostrada mediante una mejora robusta frente a D1 y controles competitivos dentro del proceso integrado. Existe una pregunta científica delimitada, un simulador y resultados condicionales que informan la selección del problema, pero no evidencia de mejora operativa real ni validación cuantitativa del modelo para GMV-CERT. La evaluación futura deberá presentar resultados positivos y negativos con métricas terminales coherentes y supuestos explícitos.

**Estado actual:** pasos 1–4 completados; paso 5 pendiente. La selección de políticas sigue siendo candidata y la comparabilidad final se establecerá al preparar la campaña. Esta actualización no inicia el paso 5 ni prescribe una estrategia nueva.
