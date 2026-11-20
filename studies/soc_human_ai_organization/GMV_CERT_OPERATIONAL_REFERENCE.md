# Referencia operativa cualitativa: GMV-CERT

**Propósito.** Preservar la información cualitativa comunicada sobre la operación del SOC de GMV-CERT para orientar la aplicación SOCTRA-HLS. Este documento no es un procedimiento operativo oficial, una validación del simulador ni una reconstrucción de la organización real.

**Procedencia y verificación.** El PI atribuye esta información a conversaciones con personal de GMV y a una reconstrucción retrospectiva. Las notas originales no están disponibles en el repositorio; no se afirma haberlas consultado ni se puede verificar literalmente la atribución, el contexto o las fechas. No se reproducen citas textuales. Los resúmenes previos en [`docs/THEORY.md`](../../docs/THEORY.md), [`docs/RESEARCH.md`](../../docs/RESEARCH.md) y documentos del estudio SOC sirven como antecedentes, no como sustitutos de las notas originales. Este documento es preliminar y deberá contrastarse en la segunda ronda de contactos con GMV.

## 1. Niveles de conocimiento

| Categoría | Significado en este documento |
|---|---|
| **Información preliminar comunicada** | Recuerdo atribuido por el PI a una conversación con personal de GMV, reconstruido retrospectivamente. No es transcripción, observación independiente ni procedimiento escrito verificado. |
| **Interpretación del investigador principal (PI)** | Lectura o mecanismo plausible que el PI deriva del recuerdo comunicado. No debe citarse como práctica real confirmada. |
| **Hipótesis científica** | Proposición contrastable que motiva el estudio sobre coordinación, competencias o adaptación; todavía no contrastada con GMV ni demostrada por la conversación. |
| **Hipótesis del simulador** | Parámetro, estructura o regla introducida para poder experimentar. No se atribuye a GMV-CERT si no hay evidencia específica. |
| **Pendiente de confirmación** | Dato o procedimiento cuyo significado, frecuencia o existencia no se ha establecido. No se completa por inferencia. |

Las secciones distinguen explícitamente estos niveles. El silencio de la conversación o de la documentación no se toma como evidencia de ausencia.

## 2. Selección y organización de alertas

### Información preliminar comunicada (recuerdo retrospectivo)

- Los analistas utilizan una herramienta que les permite visualizar y seleccionar alertas pendientes. El nombre de la herramienta no se identificó con certeza.
- Los generalistas tienden a considerar los SLA al seleccionar trabajo; los especialistas tienden a seleccionar alertas de proyectos que conocen.
- No se confirmó una comprobación sistemática del SLA antes de cada selección. Cuando se acumula trabajo, los analistas pueden priorizar alertas próximas a incumplir sus plazos.
- Un analista puede asumir varias alertas, pero las atiende secuencialmente y puede cambiar su orden de atención.
- En la reconstrucción más reciente del PI, cada analista selecciona individualmente alertas pendientes y suele considerar el SLA y su experiencia/conocimiento del proyecto. No se recuerda que se describiera un mecanismo explícito de optimización colectiva de las asignaciones.

### Interpretación del PI y límites

El relato es compatible con **selección individual tipo pull y autonomía local**. La falta de recuerdo de un optimizador colectivo es una observación preliminar sobre lo que se describió, no evidencia de que no exista coordinación, supervisión o asignación colectiva. No establece que todos los analistas vean la misma cola, que exista una cola única compartida ni que la libertad de selección sea completa. Tampoco determina cuándo se reserva una alerta, quién puede reasignarla o cómo se resuelven selecciones concurrentes.

### Hipótesis científica aún no contrastada: competencias propias y ajenas

El PI propone como hipótesis que la selección individual podría depender tanto del conocimiento que cada analista tiene de sus propias competencias como de su conocimiento o estimación de las competencias de sus compañeros. Esta es una interpretación científica motivada por la descripción de selección individual y familiaridad con proyectos. **No está confirmado que GMV utilice formalmente estimaciones de las competencias de otros analistas**, ni que esas estimaciones sean explícitas, compartidas, precisas o determinantes de la asignación. Debe contrastarse con GMV antes de formularlo como mecanismo observado.

## 3. Especialización, formación y experiencia

### Información preliminar comunicada (recuerdo retrospectivo)

- Los analistas reciben formación sobre clientes, proyectos, sistemas, problemas habituales y procedimientos.
- Se comunicó una relación entre adquisición de experiencia y número de alertas procesadas; la experiencia también se valora principalmente de forma subjetiva.
- En el trabajo con SOCTRA se había considerado **más de 1.000 alertas procesadas** como posible umbral de “experto”. El PI precisó que, para esa interpretación, deberían considerarse alertas cerradas satisfactoriamente.
- El tiempo de resolución no es necesariamente el criterio usado para valorar experiencia.
- En esta reconstrucción, “procesadas”, “cerradas” y “cerradas satisfactoriamente” son estados diferentes. No deben intercambiarse ni inferirse unos de otros.

### Interpretación del PI y límites

La relación recordada entre volumen y experiencia no demuestra que el volumen sea una medida objetiva de competencia. El umbral de 1.000 es un **criterio exploratorio considerado en SOCTRA**, no un umbral operativo de GMV-CERT validado. El matiz de cierre satisfactorio es una precisión retrospectiva del PI, no una medición independiente de calidad. Ni el número procesado ni el número cerrado o cerrado satisfactoriamente demuestran por sí solos competencia, precisión, velocidad o experiencia transferible entre proyectos. La evaluación subjetiva no se ha traducido a una escala cuantitativa validada.

### Hipótesis científica aún no contrastada

La exposición acumulada a alertas podría contribuir a adquirir experiencia, pero su efecto dependería de dificultad, variedad de proyectos, calidad del feedback y resultados de la revisión. No hay datos longitudinales por analista para contrastar esa hipótesis, y el volumen procesado no se usa aquí como proxy validado de competencia.

## 4. Estructura del SOC y cobertura

### Información preliminar comunicada (recuerdo retrospectivo)

- La plantilla permanente podría estar en el orden de **20–30 personas**; la cifra es aproximada.
- Se describió personal en Colombia que contribuye a la cobertura nocturna respecto a España.
- Cada proyecto dispone de un analista **L3** especializado. L3 realiza coordinación y supervisión, pero no necesariamente resuelve todas las alertas del proyecto.

### Datos no confirmados

No se dispone de distribución exacta L1/L2/L3, personal efectivamente presente por turno, rotaciones, descansos, disponibilidad por proyecto, reglas de transferencia entre turnos, dedicación simultánea a tareas o proporción del tiempo de L3 dedicada a coordinación frente a resolución. La cifra total no permite derivar capacidad horaria ni número de servidores concurrentes.

## 5. SLA, prioridades y severidad

### Información preliminar comunicada (valores anotados; unidad y reloj por confirmar)

Los valores anotados son:

| Prioridad comunicada | Valor anotado | Estado de la unidad y del evento SLA |
|---|---:|---|
| Crítica | 4 | Unidad pendiente de confirmar. |
| Alta | 6 horas | Valor temporal comunicado; no se conoce el evento de inicio ni el que determina cumplimiento. |
| Media | 12 horas | Valor temporal comunicado; no se conoce el evento de inicio ni el que determina cumplimiento. |

No se confirmó si el compromiso se mide hasta primera atención, clasificación, escalado, respuesta al cliente, resolución o cierre. Por tanto, esos valores **no deben tratarse automáticamente como deadlines de resolución final**. La severidad contractual puede no coincidir con la gravedad real del incidente. No se conoce la regla para alertas reabiertas, transferidas o afectadas por un cambio de prioridad.

## 6. Evaluación del rendimiento y control de calidad

### Información preliminar comunicada (recuerdo retrospectivo)

La evaluación considera cumplimiento contractual/SLA, calidad del análisis, errores de detección y tratamiento, y revisión de alertas gestionadas incorrectamente. Se realizan reuniones periódicas, aproximadamente mensuales, para revisar casos mal tratados. Un supervisor puede revisar y reabrir un caso. Un ejemplo de fallo relevante es no identificar malware que debía detectarse. La evaluación también considera dificultad, severidad y naturaleza de las alertas.

### Límites

No se aportó rúbrica, tasa de error, esquema de adjudicación independiente ni distribución de resultados por analista. Un caso reabierto o una revisión no ofrece por sí solo una medida comparable de calidad. No debe reducirse el rendimiento individual al número de alertas cerradas ni equipararse cumplimiento SLA con calidad técnica.

## 7. Relación con HLS, SOCTRA-HLS y el simulador

Se mantienen tres niveles distintos:

1. **HLS:** programa general sobre organización, coordinación y aprendizaje de entidades heterogéneas en entornos dinámicos.
2. **SOCTRA-HLS:** aplicación de ese programa al trabajo de analistas humanos y sistemas de IA en un SOC.
3. **GMV-CERT:** referencia operativa cualitativa que motiva y acota preguntas de la aplicación; no valida cuantitativamente el simulador ni define HLS en general.

SOCTRA aporta evidencia sobre el triaje asistido por IA y características agregadas de alertas. No describe por sí solo todo el trabajo posterior de analistas, la organización, la dotación o la resolución de incidentes.

**D1** es una interpretación simplificada y plausible de selección individual de alertas, no una reproducción verificada del procedimiento de GMV-CERT. Su regla, desempates, orden de analistas y estructura de colas son especificaciones del baseline. La evidencia cualitativa no confirma una cola única compartida, EDF, elegibilidad formal por proyecto, ausencia total de coordinación ni la aplicación exacta de una regla local antes de cada selección.

Las competencias numéricas, velocidades, tiempos de servicio, probabilidades de error/escalado, plantilla concreta, turnos, SLA codificados como deadlines terminales, costes de coordinación y leyes de aprendizaje son **hipótesis del simulador** si no se respaldan por medición independiente. D1 modela una forma concreta de selección descentralizada; P1 añade una regla explícita de prioridad temporal, y HLS-B conmuta entre ambas mediante carga estimada e histéresis. Son estrategias experimentales motivadas por preguntas de organización, **no evidencia de que sus reglas reproduzcan los procedimientos reales de GMV-CERT**. La información cualitativa aquí reunida no valida individualmente ninguna política ni su mecanismo de competencias. No derivar competencia individual a partir de asignaciones, volumen de alertas, escalados o cierres.

## 8. Contraste con la documentación existente

- [`docs/THEORY.md`](../../docs/THEORY.md) y [`docs/RESEARCH.md`](../../docs/RESEARCH.md) ya registraban selección de alertas, diferencias generales/especialistas, tratamiento secuencial, escala aproximada de plantilla, cobertura desde Colombia, función de L3 y valores anotados de SLA. Son compatibles en lo esencial con esta referencia.
- La documentación previa decía que no se identificó un optimizador colectivo explícito. Se conserva esa formulación limitada: **no identificado en la conversación**, no ausencia confirmada de coordinación o supervisión.
- La mención previa de alertas cerradas como indicador subjetivo de experiencia se precisa aquí con el matiz comunicado por el PI: el umbral exploratorio de SOCTRA se refería a cierres satisfactorios. Ninguna de las dos formulaciones constituye una medida validada de competencia.
- La información más específica sobre herramienta de selección, comprobación no sistemática de SLA, cambio de orden, reuniones mensuales, reapertura por supervisión y el ejemplo de malware no estaba desarrollada en las síntesis examinadas. Se incorpora como información comunicada, no como contradicción con el silencio documental previo.
- Una versión anterior de esta referencia mencionaba un informe del PI fechado el 6 de noviembre de 2026. Ese informe no se localizó ni se verificó; la fecha se conserva únicamente como atribución previa pendiente de confirmación, no como fuente examinada.

## 9. Incógnitas operativas que esta referencia no resuelve

Persisten, entre otras, la herramienta exacta y su comportamiento; visibilidad y reglas reales de cola; autoridad y mecanismos de coordinación; roster por nivel y turno; transferencias y handovers; significado contractual de cada SLA; criterios de calidad y reapertura; medidas válidas de competencia; tiempos activos frente a espera; y la relación entre recomendación SOCTRA y decisión humana efectiva. Este documento no propone completar esas incógnitas con nuevos parámetros.

## 10. Temas para contrastar en la segunda ronda de contactos

Esta lista identifica las hipótesis con mayor riesgo para la validez externa de SOCTRA–HLS. **No es un cuestionario definitivo**; el guion específico se preparará después. La conversación deberá distinguir prácticas habituales, excepciones, herramientas disponibles y procedimientos formalizados.

1. **Colas:** cómo se presentan y actualizan las alertas pendientes, quién puede ver cada cola y cómo se reservan, retiran o reasignan alertas.
2. **Autonomía y coordinación:** cuánto decide cada analista, qué coordinación de equipo o supervisión existe y cómo se resuelven selecciones simultáneas o conflictos entre urgencia y especialización.
3. **Competencias propias y ajenas:** qué sabe cada persona sobre sus capacidades, cómo conoce o estima las de compañeros y si existe una matriz, registro o mecanismo formal de matching.
4. **Experiencia y calidad:** cómo se adquiere y evalúa experiencia; qué significan procesar, cerrar y cerrar satisfactoriamente; cómo se miden errores, reaperturas, dificultad y calidad.
5. **SLA:** significado contractual de cada prioridad, evento de inicio y fin, pausas, cambios de severidad, transferencias y diferencia entre primera respuesta y resolución.
6. **Servicio y capacidad efectiva:** tiempos activos por clase de tarea, espera, trabajo concurrente, escalado L1/L2/L3, cobertura por turnos, handovers y disponibilidad efectiva.
7. **Congestión y recuperación:** señales que provocan cambios de criterio, respuesta ante acumulación, prioridades durante sobrecarga y cómo vuelve el equipo a operación normal después del pico.

Estas cuestiones deben resolverse antes de interpretar el mapa sintético como recomendación operativa. En particular, organización de colas, SLA terminal, tiempos de servicio, competencias estimadas y capacidad continua son supuestos que pueden alterar qué política resulta preferible.

## Referencias internas

- [D1 y modelo SOC](SOC_FOUNDATIONS_AND_MODEL.md#4-estrategias-soc-y-distinción-histórica)
- [Evidencia empírica, supuestos y límites](SOC_FOUNDATIONS_AND_MODEL.md#2-evidencia-y-límites-de-observación)
- [Resultados de parametrización de D1](SOC_RESULTS_AND_LESSONS.md#5-replay-histórico-a-y-calibración-de-d1)
- [Mapa operativo paramétrico final](SOC_HLS_FINAL_OPERATING_MAP.md) y [síntesis científica final](SOC_HLS_FINAL_SCIENTIFIC_SYNTHESIS.md): resultados exploratorios y límites de D1/P1/HLS-B.
- [Punto de entrada SOCTRA-HLS](README.md)
