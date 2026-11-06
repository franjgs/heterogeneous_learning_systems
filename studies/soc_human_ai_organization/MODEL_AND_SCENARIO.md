# Síntesis científica del estudio SOC

**Estado científico:** preparación conceptual; estudio `PROPOSED / NOT_EVALUATED`. No hay modelo organizativo congelado, protocolo aprobado, implementación ni experimento HLS.
**Decisión del PI:** recibida el 2026-10-28. La hora de adopción de la decisión no está documentada.
**Registro de esta consolidación:** 2026-10-28 20:28:21 CET (+0100).
**Alcance:** síntesis del estudio de aplicación; no modifica ni promueve conocimiento al core HLS. Las auditorías de demanda y experiencia son las fuentes agregadas de apoyo y conservan su análisis detallado.

## 1. Pregunta y propósito

El estudio investigará cómo organizar equipos humanos heterogéneos que atienden varios proyectos cuando la asistencia mediante IA modifica la carga operativa del triaje. Interesa comprender las condiciones bajo las cuales la asignación de trabajo, la especialización o polivalencia, la formación y la adaptación afectan al rendimiento presente y a la capacidad futura, contabilizando costes de organización, formación y oportunidad.

La heterogeneidad no es un objetivo ni una ventaja presumida. No se declara óptima ninguna política. La pregunta es qué estructuras y decisiones funcionan, para qué tareas y condiciones, con qué costes y límites.

Posibles mecanismos de estudios posteriores —no hechos observados ni procedimientos del SOC— incluyen asignación dinámica, aprendizaje por experiencia, formación deliberada, especialización, polivalencia, cambios de proyecto/contexto y reasignación de capacidad asociada a asistencia de IA.

## 2. Límite del testbed y papel de SOCTRA

El testbed abstracto contiene dos procesos conceptualmente distintos:

- **L1, triaje inicial:** decisiones de escalar o no y reportar o no.
- **L2, análisis profundo:** investigación de alertas que requieren análisis adicional.

La secuencia entre decisiones, criterios de entrada a L2, responsabilidades, handoffs y resultados deben definirse para cada modelo; no se asumen procedimientos reales de GMV-CERT.

El dataset SOCTRA fue concebido para triaje automático de escalado y reporte. Su uso aquí es un **anclaje empírico agregado** de escala, variación temporal y estructura de proyectos/categorías del problema. No se pretende reconstruir la organización real de GMV-CERT, sus plantillas, turnos, asignaciones históricas, políticas, ni identidades o trayectorias laborales. Los campos de tramitador, proyecto y peso se analizaron para determinar sus límites de interpretación; no son un objetivo de reconstrucción organizativa ni una medida de la matriz de competencias propuesta abajo.

SOCTRA demostró una reducción de la carga operativa de triaje, según la aclaración del PI registrada en el estudio. La magnitud no está expresada en minutos de analista, horas de capacidad o dotación liberada en las fuentes revisadas. Por ello, cualquier cantidad de capacidad liberada que se use en un modelo futuro será una **hipótesis de escenario** hasta medirla de forma independiente.

## 3. Anclaje empírico disponible

La auditoría del snapshot acumulado más reciente verificó 214.739 alertas con ID único entre 2022-12-31 y 2025-09-18, en 993 fechas de calendario. En periodos completos, el volumen diario medio fue 216,1 registros (CV 0,412) y el mensual medio 6.514,4 (CV 0,183). Se observaron 27 etiquetas de proyecto; las cinco de mayor volumen concentraron 59,23 % de los registros. De mes a mes aparecen 16–23 etiquetas de proyecto.

El extracto contiene 91 valores distintos de `tramitador` y 1.341 parejas observadas tramitador–proyecto. Estos conteos sirven para describir la estructura del dataset y sus etiquetas, **no** para inferir 91 personas, analistas simultáneos, plantilla, asignación real o historia laboral. Los 27 proyectos históricos tampoco implican 27 proyectos simultáneamente activos. Un registro de alerta no equivale a una tarea humana, horas de trabajo ni esfuerzo; puede resumir eventos y carece de inicio/fin de trabajo verificables.

Los valores por proyecto están concentrados y la demanda varía temporalmente; estas propiedades justifican que futuros escenarios no se reduzcan sin examen a una única tasa homogénea. No determinan por sí mismas una distribución de agentes ni su capacidad.

### Pesos y experiencia

El material SOCTRA describe una propuesta estática de pesos por operador–proyecto basada en recuentos y una lista de expertos, además de una variante dinámica cuyo incremento no está especificado de forma reproducible. El código consultado consume esos pesos; no aporta un generador validado. Los pesos son ponderadores de muestras en un pipeline de clasificación, no medidas validadas de experiencia, competencia o calidad individual. El detalle, las discrepancias entre snapshots, los empates y los riesgos de procedencia están en [la auditoría de experiencia](ANALYST_EXPERIENCE_AUDIT.md).

La selección de filas tampoco ofrece una trayectoria organizativa event-sourced: los snapshots recodifican el campo tramitador y no aportan fechas de asignación, trabajo o reasignación. No se utilizarán para reconstruir quién trabajó en qué tarea ni cuándo.

## 4. Experiencia y competencia son constructos distintos

| Constructo | Significado en este estudio | Evidencia actual |
|---|---|---|
| Experiencia general | Participación/acumulación de actividad a través de tareas o contextos. | No hay antigüedad laboral ni historial de formación individual verificado. |
| Experiencia específica de proyecto | Exposición previa a trabajo asociado a un proyecto. | Hay etiquetas y recuentos derivados, sujetos a semántica e identidad no verificadas; no equivalen a asignación o dominio. |
| Competencia técnica específica | Disposición o estado relevante para lograr un resultado definido en una clase de tareas bajo condiciones indicadas. | No hay mediciones individuales validadas ni rúbrica/resultado independiente. |
| Exposición histórica | Conteo/mezcla temporal de registros observados antes de un corte. | Puede derivarse de los datos con un corte estricto; es un proxy de actividad, no una capacidad. |
| Competencia efectiva en el modelo | Variable que condicionará resultados potenciales del agente en tareas definidas. | Es latente/hipotética hasta operacionalizarse y validarse; no se obtiene de los pesos SOCTRA. |

Aprendizaje requerirá una regla explícita de transición de competencia asociada a experiencia o intervención. Una mayor exposición no implica por sí misma aprendizaje; aprendizaje tampoco implica mejora de rendimiento individual o colectivo.

## 5. Hipótesis mínima de representación

La decisión conceptual provisional del PI es representar competencias mediante:

\[
C(t)\in\mathbb{R}^{N\times P},\qquad C_{ij}(t)=\text{competencia del analista modelado }i\text{ para tareas del contexto de proyecto }j\text{ en }t.
\]

Esta matriz es una **hipótesis de modelado**, no una variable observada en SOCTRA. En esta notación local, `N` es el número de analistas incluidos en un escenario y `P` el número de contextos de proyecto modelados; `N` no se fija en 91 y `P` no se fija en 27. `P` aquí no sustituye la notación de demanda usada en otros modelos del core.

El dominio, escala, significado medible y vínculo entre `C_ij(t)` y resultados de tarea siguen abiertos. Una sola competencia por proyecto puede ser una abstracción insuficiente si dentro del proyecto varían las tareas o tecnologías; se añadirá una dimensión solo con justificación científica y evidencia/hipótesis explícita. Experiencia, exposición y pesos de clasificación no se identificarán con `C(t)`.

La matriz puede cambiar con el tiempo en un modelo futuro, pero todavía no hay ley de aprendizaje, transferencia, olvido ni adaptación aprobada. La representación tampoco fija `N`, `P`, distribuciones iniciales, correlaciones, tasas de transición o relaciones entre proyecto y categoría técnica.

## 6. Fenómenos que el modelo futuro debe poder separar

El diseño mínimo posterior tendrá que distinguir:

1. **Demanda y entorno:** volúmenes y mezcla de tareas/proyectos, además de cambios de contexto. Las llegadas históricas pueden informar una referencia, no predecir por sí solas demanda futura.
2. **Organización y decisiones:** quién puede asumir qué tareas, cómo se asignan, con qué capacidad, acceso, tiempos y restricciones. Una organización define acciones factibles; una política selecciona entre ellas.
3. **Desarrollo de competencia:** aprendizaje por exposición y formación deliberada como mecanismos diferentes, con transición de `C(t)` y evidencia inciertas.
4. **Asistencia mediante IA:** método de triaje, efecto operativo sobre carga y decisiones organizativas son niveles diferentes. La capacidad liberada, fallos, re-trabajo y tiempo humano requieren medición o escenarios hipotéticos separados.
5. **Evaluación temporal y costes:** rendimiento individual y colectivo, servicio, plazos y resiliencia junto a tiempo de analistas/mentores, formación, reorganización y coste de herramientas. No se agregan en una utilidad sin una justificación explícita.

El modelo deberá comparar alternativas competitivas y permitir efectos desfavorables, nulos o dependientes del contexto. No se ha seleccionado función objetivo, política, baseline ni estimando.

## 7. Qué sabemos y qué permanece abierto

**Observaciones del extracto:** volumen y timestamps de registros de alerta; etiquetas de proyecto/categoría; etiquetas asociadas a tramitador; pesos precalculados. Se restringen al snapshot y a su semántica disponible.

**Indicadores derivados:** tasas por periodo, concentración de volúmenes y mezcla de etiquetas; no son variables medidas directamente sobre personas o capacidad.

**Hipótesis de modelado:** matriz `C(t)`, tareas y procesos L1/L2, cambios de demanda, aprendizaje, costes, especialización/polivalencia y efecto de capacidad de IA. No están validados por los datos.

**Decisión del PI:** estudiar organización de equipos humanos heterogéneos bajo cambios de carga asociados a asistencia IA; usar SOCTRA como anclaje empírico, no como reconstrucción de GMV-CERT; adoptar provisionalmente `C(t)` como representación mínima.

**Cuestiones abiertas:** definición y unidad de competencia; número y tipo de tareas por proyecto; relación entre exposición y cambio de competencia; medición de capacidad liberada por IA; disponibilidad, tiempos de servicio, plazos y costes; horizonte y métricas; comparadores y políticas; cambios de entorno representativos; permisos de uso/divulgación. Las limitaciones empíricas detalladas están en [caracterización de demanda](DEMAND_CHARACTERIZATION.md) y [auditoría de experiencia](ANALYST_EXPERIENCE_AUDIT.md).

## 8. Siguiente hito y autorización

El siguiente hito es diseñar científicamente un modelo organizativo mínimo, especificando variables de estado, decisiones, conjunto factible y restricciones, dinámica, estimandos/funciones objetivo, políticas de comparación e hipótesis falsables. Debe definir cómo se conectan `C(t)`, exposición y resultados sin usar información futura y cómo separar los efectos de asignación, formación y asistencia IA.

Este hito **no autoriza** todavía implementación, simulaciones ni entrenamiento de modelos. Antes de ejecutar, deberán existir modelo y protocolo revisables, datos/permisos apropiados y autorización explícita del PI.

## 9. Procedencia y relación con el core

Esta síntesis pertenece al estudio `study.soc_competence_heterogeneity_testbed` y al escenario propuesto `scenario.soc_alert_operations` ya registrados en el [catálogo del core](../../registry/catalog.json). Su estado continúa siendo `PROPOSED / NOT_EVALUATED`; esta síntesis no constituye resultado empírico del estudio ni cambia estados del catálogo.

- [Caracterización agregada de demanda](DEMAND_CHARACTERIZATION.md): escala y distribución temporal/proyectos; fuente local restringida.
- [Auditoría de pesos y experiencia](ANALYST_EXPERIENCE_AUDIT.md): semántica y límites de tramitador, pesos y actividad temporal; fuente local restringida.
- [Análisis AIAI/SOCTRA](AIAI_2026_ANALYSIS.md): separa clasificación publicada, evidencia SOCTRA adicional y contexto operativo.
- [Evidencia y candidatos de transferencia HLS](EVIDENCE.md): resultados sintéticos del core y límites de reutilización.
- [Literatura y requisitos editoriales](LITERATURE.md), [preparación del protocolo](PROTOCOL_AND_REPRODUCIBILITY.md) y [cronología](HISTORY.md).

El PI autorizó el 2026-10-28 incluir en este repositorio los informes agregados de demanda/actividad y las figuras anónimas enlazadas. Esto no acredita autorización del dueño de los datos para otros usos ni publicación editorial. No se copian registros, nombres de proyecto, identificadores personales ni perfiles individuales. Ningún resultado SOC se generaliza al core HLS automáticamente.
