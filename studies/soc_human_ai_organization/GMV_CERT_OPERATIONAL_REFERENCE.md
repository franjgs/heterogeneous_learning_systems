# Referencia operativa cualitativa: GMV-CERT

**Propósito.** Preservar la información cualitativa comunicada sobre la operación del SOC de GMV-CERT para orientar la aplicación SOCTRA-HLS. Este documento no es un procedimiento operativo oficial, una validación del simulador ni una reconstrucción de la organización real.

**Procedencia y verificación.** El PI indicó que la información procede de una conversación con un profesional de GMV y de su informe del **6 de noviembre de 2026**. Ese informe original no se encontró en el repositorio durante esta revisión; por tanto, no se afirma haberlo consultado ni se puede verificar literalmente la atribución, el contexto o la fecha. El contenido operativo que sigue es el proporcionado para esta consolidación. Los resúmenes previos en [`docs/THEORY.md`](../../docs/THEORY.md), [`docs/RESEARCH.md`](../../docs/RESEARCH.md) y documentos del estudio SOC sirven como antecedentes, no como sustitutos del informe original.

## 1. Niveles de conocimiento

| Categoría | Significado en este documento |
|---|---|
| **Comunicado** | Información atribuida por el PI al profesional o a sus notas de conversación. No equivale a observación independiente ni a procedimiento escrito verificado. |
| **Interpretación del PI** | Lectura plausible para formular la investigación, conservada como interpretación y no como hecho operativo. |
| **No confirmado / desconocido** | La conversación o las fuentes localizadas no establecen el dato. No se completa mediante supuestos. |
| **Hipótesis de simulación** | Parámetro o regla introducida por HLS. No se atribuye a GMV-CERT mientras no exista evidencia específica. |

## 2. Selección y organización de alertas

### Información comunicada

- Los analistas utilizan una herramienta que les permite visualizar y seleccionar alertas pendientes. El nombre de la herramienta no se identificó con certeza.
- Los generalistas tienden a considerar los SLA al seleccionar trabajo; los especialistas tienden a seleccionar alertas de proyectos que conocen.
- No se confirmó una comprobación sistemática del SLA antes de cada selección. Cuando se acumula trabajo, los analistas pueden priorizar alertas próximas a incumplir sus plazos.
- Un analista puede asumir varias alertas, pero las atiende secuencialmente y puede cambiar su orden de atención.

### Interpretación y límites

El relato es compatible con **selección tipo pull y autonomía individual**. No establece que todos los analistas vean la misma cola, que exista una única cola compartida, que la libertad de selección sea completa ni que no haya coordinación central, supervisión u otras formas de distribución del trabajo. Tampoco determina cuándo se reserva una alerta, quién puede reasignarla o cómo se resuelven selecciones concurrentes.

En consecuencia, la frase “no se identificó un optimizador colectivo explícito” significa únicamente que no se describió tal mecanismo en la conversación disponible. No permite concluir que GMV-CERT carezca de coordinación o de procedimientos organizativos.

## 3. Especialización, formación y experiencia

### Información comunicada

- Los analistas reciben formación sobre clientes, proyectos, sistemas, problemas habituales y procedimientos.
- La experiencia se desarrolla progresivamente mediante la resolución de alertas y se valora principalmente de forma subjetiva.
- En el trabajo con SOCTRA se había considerado **más de 1.000 alertas procesadas** como posible umbral de “experto”. El PI precisó que, para esa interpretación, deberían considerarse alertas cerradas satisfactoriamente.
- El tiempo de resolución no es necesariamente el criterio usado para valorar experiencia.

### Interpretación y límites

El umbral de 1.000 es un **criterio exploratorio considerado en SOCTRA**, no un umbral operativo de GMV-CERT validado. El matiz de cierre satisfactorio es una precisión del PI, no una medición objetiva de calidad. Ni el recuento de alertas ni su cierre demuestran por sí solos competencia, precisión, velocidad o experiencia transferible entre proyectos. La evaluación subjetiva no se ha traducido a una escala cuantitativa validada.

## 4. Estructura del SOC y cobertura

### Información comunicada

- La plantilla permanente podría estar en el orden de **20–30 personas**; la cifra es aproximada.
- Se describió personal en Colombia que contribuye a la cobertura nocturna respecto a España.
- Cada proyecto dispone de un analista **L3** especializado. L3 realiza coordinación y supervisión, pero no necesariamente resuelve todas las alertas del proyecto.

### Datos no confirmados

No se dispone de distribución exacta L1/L2/L3, personal efectivamente presente por turno, rotaciones, descansos, disponibilidad por proyecto, reglas de transferencia entre turnos, dedicación simultánea a tareas o proporción del tiempo de L3 dedicada a coordinación frente a resolución. La cifra total no permite derivar capacidad horaria ni número de servidores concurrentes.

## 5. SLA, prioridades y severidad

Los valores anotados son:

| Prioridad comunicada | Valor anotado | Estado de la unidad y del evento SLA |
|---|---:|---|
| Crítica | 4 | Unidad pendiente de confirmar. |
| Alta | 6 horas | Valor temporal comunicado; no se conoce el evento de inicio ni el que determina cumplimiento. |
| Media | 12 horas | Valor temporal comunicado; no se conoce el evento de inicio ni el que determina cumplimiento. |

No se confirmó si el compromiso se mide hasta primera atención, clasificación, escalado, respuesta al cliente, resolución o cierre. Por tanto, esos valores **no deben tratarse automáticamente como deadlines de resolución final**. La severidad contractual puede no coincidir con la gravedad real del incidente. No se conoce la regla para alertas reabiertas, transferidas o afectadas por un cambio de prioridad.

## 6. Evaluación del rendimiento y control de calidad

### Información comunicada

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

Las competencias numéricas, velocidades, tiempos de servicio, probabilidades de error/escalado, plantilla concreta, turnos, SLA codificados como deadlines terminales, costes de coordinación y leyes de aprendizaje son **hipótesis de simulación** si no se respaldan por medición independiente. No derivar competencia individual a partir de asignaciones, volumen de alertas, escalados o cierres.

## 8. Contraste con la documentación existente

- [`docs/THEORY.md`](../../docs/THEORY.md) y [`docs/RESEARCH.md`](../../docs/RESEARCH.md) ya registraban selección de alertas, diferencias generales/especialistas, tratamiento secuencial, escala aproximada de plantilla, cobertura desde Colombia, función de L3 y valores anotados de SLA. Son compatibles en lo esencial con esta referencia.
- La documentación previa decía que no se identificó un optimizador colectivo explícito. Se conserva esa formulación limitada: **no identificado en la conversación**, no ausencia confirmada de coordinación o supervisión.
- La mención previa de alertas cerradas como indicador subjetivo de experiencia se precisa aquí con el matiz comunicado por el PI: el umbral exploratorio de SOCTRA se refería a cierres satisfactorios. Ninguna de las dos formulaciones constituye una medida validada de competencia.
- La información más específica sobre herramienta de selección, comprobación no sistemática de SLA, cambio de orden, reuniones mensuales, reapertura por supervisión y el ejemplo de malware no estaba desarrollada en las síntesis examinadas. Se incorpora como información comunicada, no como contradicción con el silencio documental previo.
- No se encontró el informe original del PI del 6 de noviembre de 2026 ni una versión equivalente identificable en los archivos del repositorio. La fecha y atribución se conservan tal como fueron indicadas en la solicitud y quedan pendientes de contraste documental.

## 9. Incógnitas operativas que esta referencia no resuelve

Persisten, entre otras, la herramienta exacta y su comportamiento; visibilidad y reglas reales de cola; autoridad y mecanismos de coordinación; roster por nivel y turno; transferencias y handovers; significado contractual de cada SLA; criterios de calidad y reapertura; medidas válidas de competencia; tiempos activos frente a espera; y la relación entre recomendación SOCTRA y decisión humana efectiva. Este documento no propone completar esas incógnitas con nuevos parámetros.

## Referencias internas

- [D1 y modelo SOC](SOC_FOUNDATIONS_AND_MODEL.md#4-estrategias-soc-y-distinción-histórica)
- [Evidencia empírica, supuestos y límites](SOC_FOUNDATIONS_AND_MODEL.md#2-evidencia-y-límites-de-observación)
- [Resultados de parametrización de D1](SOC_RESULTS_AND_LESSONS.md#5-replay-histórico-a-y-calibración-de-d1)
- [Punto de entrada SOCTRA-HLS](README.md)
