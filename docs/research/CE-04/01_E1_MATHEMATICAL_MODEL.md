HLS — CE-04 / INFORME E1 AL CHIEF ENGINEER
Fecha: 26/10/2026
Estado: MODELO MATEMÁTICO PROPUESTO
Origen: E1 — Evaluación teórica

OBJETIVO

Comunicar al CE las conclusiones del análisis E1 sobre
el efecto de la heterogeneidad y la complementariedad
en el rendimiento colectivo de organizaciones de agentes.

El análisis se ha realizado conforme a RESEARCH_DOCTRINE.md.

No se presupone que las organizaciones heterogéneas sean
superiores. El objetivo es identificar las condiciones
en las que la composición, la organización y sus
interacciones modifican el rendimiento colectivo.


1. MODELO MATEMÁTICO

Considerar organizaciones de:

    N ∈ {12, 24, 48} agentes.

Con:

    - Cuatro familias de capacidades.
    - K familias de tareas.
    - Demanda variable en el tiempo.
    - Recursos limitados.
    - Colas y plazos de ejecución.
    - Competencias individuales constantes.
    - Sin aprendizaje ni transferencia.

COMPETENCIA INDIVIDUAL

    q_ik = P(éxito del agente i en tareas de familia k)

La matriz Q caracteriza las competencias de la organización.

TIEMPO Y COSTE

    τ_ik = E[tiempo de ejecución]
    c_ik = E[coste de ejecución]

No debe suponerse una relación automática entre
competencia, velocidad y coste.

COMPLEMENTARIEDAD

Para una pareja de agentes:

    q_ij,k = P(éxito conjunto | i,j,k,γ)

donde γ es un protocolo cooperativo fijo.

Definir:

    κ_ij,k = q_ij,k - max(q_ik,q_jk)

Interpretación:

    κ > 0: ventaja cooperativa en calidad.
    κ = 0: ausencia de ventaja.
    κ < 0: cooperación perjudicial.

Esta magnitud mide una ventaja operacional, no una
sinergia informacional.

La complementariedad debe medirse o parametrizarse
independientemente de la heterogeneidad.

No imponer que los agentes más diferentes sean
automáticamente más complementarios.

ASIGNACIÓN

Una organización π determina qué agentes o parejas
ejecutan cada tarea, respetando:

    - Disponibilidad.
    - Capacidad de ejecución.
    - Restricciones de recursos.
    - Colas.
    - Plazos.
    - Presupuesto.

RENDIMIENTO COLECTIVO

Para cada tarea n:

    Y_n = 1 si se resuelve correctamente y dentro
          del plazo; 0 en otro caso.

Definir:

    V_H = E[ΣY_n] / E[N_H]

El denominador incluye todas las tareas recibidas
durante el horizonte de evaluación.

Registrar también:

    - Tasa de éxito.
    - Cumplimiento de plazos.
    - Tiempo de espera.
    - Coste total.
    - Utilización de recursos.
    - Tareas pendientes o incumplidas.

No utilizar únicamente accuracy como indicador
de rendimiento colectivo.


2. NIVELES DE HETEROGENEIDAD

Estudiar:

    H0: organización homogénea.
    H1: heterogeneidad moderada.
    H2: heterogeneidad elevada.

Una parametrización posible es:

    q_ik(H) = μ_k + α_H s_ik

con:

    α_H0 = 0
    0 < α_H1 < α_H2

Los perfiles s_ik representan especialización.

Exigir, siempre que sea factible:

    (1/N) Σ_i q_ik(H) = μ_k

para cada familia de tareas y nivel de heterogeneidad.

Evitar truncamientos que alteren estas medias.

Mantener las cuatro familias de capacidades en todos
los escenarios.

La heterogeneidad debe modificar la distribución
de competencias, no incrementar automáticamente
su nivel medio.


3. CONTROLES EXPERIMENTALES

Para cada N, comparar H0, H1 y H2 con:

    - Idéntica demanda.
    - Idéntica distribución de familias de tareas.
    - Idénticos plazos.
    - Idéntico número de agentes.
    - Idéntica capacidad nominal total.
    - Idéntico presupuesto de recursos.
    - Idéntica competencia media por familia.
    - Idénticos criterios de evaluación.

Utilizar escenarios emparejados.

IMPORTANTE:

No pueden mantenerse simultáneamente constantes:

    - Competencia media.
    - Dispersión de competencias.
    - Competencia máxima por familia.
    - Rendimiento del mejor asignador.

Si aumenta la especialización, puede aumentar
la competencia del mejor agente disponible para
una familia aunque la media permanezca constante.

Este efecto no debe eliminarse artificialmente:
forma parte de lo que queremos estudiar.

Sin embargo, tampoco debe confundirse con una
ventaja intrínseca de la organización heterogénea.


4. SEPARACIÓN DE EFECTOS

Definir:

    V(H,O) = rendimiento colectivo obtenido con
             composición H y organización O.

Comparar composiciones y organizaciones mediante
un diseño factorial.

EFECTO DE COMPOSICIÓN

    ΔC = V(H1,O0) - V(H0,O0)

EFECTO DE ORGANIZACIÓN

    ΔO = V(H0,O1) - V(H0,O0)

INTERACCIÓN

    ΔCO =
        V(H1,O1) - V(H1,O0)
        - V(H0,O1) + V(H0,O0)

Interpretación:

    ΔCO ≠ 0

indica que el efecto organizativo depende de
la composición.

No demuestra por sí mismo complementariedad
entre agentes.

La complementariedad κ debe analizarse como
una propiedad diferenciada.

Distinguir expresamente:

    - Organización fija.
    - Organización readaptada a la composición.

No favorecer artificialmente una composición
mediante reglas organizativas diseñadas para ella.


5. EFECTOS DE ESCALA

Evaluar:

    N = 12, 24 y 48.

Distinguir dos regímenes:

A. ESCALADO PROPORCIONAL

    Demanda y recursos crecen con N.

    Permite comparar organizaciones a una carga
    relativa aproximadamente constante.

B. DEMANDA FIJA

    La demanda permanece constante mientras N aumenta.

    Permite estudiar el beneficio de disponer de
    más capacidad, pero no aísla efectos organizativos.

Recomendación E1:

    Utilizar el escalado proporcional como régimen
    principal para analizar efectos organizativos.

Los posibles beneficios de escala incluyen mayor
disponibilidad de competencias y absorción de demanda.

Los posibles perjuicios incluyen congestión,
competencia por recursos y coordinación.

No presuponer el signo del efecto.


6. RIESGOS METODOLÓGICOS

RIESGO 1 — VENTAJA CONSTRUIDA ARTIFICIALMENTE

Si H2 incorpora mayor competencia media, mejores
especialistas sin compensaciones o mayor
complementariedad por definición, el resultado
puede estar determinado por el generador de escenarios.

RIESGO 2 — CONFUSIÓN COMPOSICIÓN/ORGANIZACIÓN

Una organización fija puede perjudicar a una
composición especializada.

Una organización readaptada puede aprovecharla.

Sin un diseño factorial no puede distinguirse
qué factor explica las diferencias.

RIESGO 3 — CONGESTIÓN Y PLAZOS

Las diferencias de rendimiento pueden proceder
de tiempos de servicio, colas o saturación.

Es necesario registrar carga, utilización,
espera y cumplimiento de plazos.


7. CUESTIONES QUE EL CE DEBE RESOLVER

Antes de trasladar el modelo a E3, concretar:

1. Cómo se definen las cuatro familias de capacidades
   y su relación con las K familias de tareas.

2. Cómo se construyen H0, H1 y H2 manteniendo
   condiciones iniciales comparables.

3. Cómo se caracteriza la complementariedad sin
   imponer artificialmente una ventaja heterogénea.

4. Qué condiciones organizativas se compararán y
   cómo se garantiza que sean reproducibles y justas.

5. Cómo se contabilizan los recursos consumidos
   por una tarea ejecutada conjuntamente.

6. Cómo se controla la carga relativa al escalar
   de 12 a 24 y 48 agentes.

Estas decisiones son especificaciones del modelo,
no autorizaciones para desarrollar algoritmos.


8. CONCLUSIÓN E1

El modelo propuesto permite estudiar tres cuestiones
científicas diferenciadas:

A. Cómo influye la distribución de competencias
   en el rendimiento colectivo.

B. Cómo influye la organización sobre una composición
   determinada.

C. Cómo interactúan composición y organización,
   incluyendo el papel de la complementariedad.

El resultado puede ser favorable, desfavorable o
indiferente a la heterogeneidad.

La contribución científica no debe formularse como
una demostración de superioridad de HLS.

Debe consistir en caracterizar las condiciones,
límites y mecanismos que explican el rendimiento
colectivo de organizaciones heterogéneas.

ESTADO FINAL E1:

    MODELO MÍNIMO: PROPUESTO.
    CONTROLES: IDENTIFICADOS.
    RIESGOS: IDENTIFICADOS.
    IMPLEMENTACIÓN: NO AUTORIZADA POR E1.
    EXPERIMENTOS: NO EJECUTADOS.

Solicito al CE revisar especialmente la separación
entre heterogeneidad, complementariedad y organización,
y resolver las seis cuestiones anteriores antes de
aprobar una especificación experimental.
