HLS — CE-04 / INFORME E2
Fecha: 26/10/2026
Asunto: Políticas de asignación y cierre del protocolo experimental

CE,

He revisado el modelo de E1 y RESEARCH_DOCTRINE.md.

RECOMENDACIÓN: CERRAR EL DISEÑO Y COMENZAR LA PRIMERA CAMPAÑA.

1. POLÍTICAS RECOMENDADAS

P0 — Join-Shortest-Expected-Workload:
Asignación según carga y disponibilidad, sin utilizar competencias específicas.

P1 — Min-Min:
Asignación basada en tiempos estimados de finalización. Complementar con un baseline estándar que considere explícitamente probabilidades de éxito, carga y plazos. Min-Min clásico no incorpora probabilidades de éxito.

P2 — Contextual Thompson Sampling:
Asignación adaptativa que estima competencias a partir de resultados observados, respetando restricciones de capacidad.

Añadir P1 con competencias estimadas para separar el efecto de la información del efecto de la política.

2. COMPARACIONES JUSTAS

Distinguir dos regímenes:

A. Información completa: competencias verdaderas conocidas por las políticas informadas.
B. Información aprendida: competencias estimadas exclusivamente mediante observaciones anteriores.

Mantener idénticas las demandas, recursos, plazos, condiciones iniciales y realizaciones aleatorias entre políticas.

No comparar políticas con información privilegiada como si dispusieran de las mismas condiciones.

3. COOPERACIÓN

Recomiendo DESACTIVARLA en la primera campaña.

Una tarea será atendida por un agente.

Así podremos distinguir:
- Heterogeneidad: composición de competencias.
- Organización: política de asignación.
- Interacción entre ambas.

La complementariedad mediante cooperación debe estudiarse posteriormente, sin introducirla como factor de confusión.

4. COLAS Y PLAZOS

Utilizar mecanismos existentes:
- SimPy para simulación de eventos discretos.
- FCFS como disciplina común de cola.
- Plazos explícitos.
- Trabajo pendiente para estimar disponibilidad.
- Reglas uniformes de expiración y sobrecarga.

No desarrollar un simulador ni algoritmos propios.

5. DISEÑO EXPERIMENTAL

Diseño factorial:

Composiciones: H0, H1, H2.
Políticas: P0, P1 informada, P1 estimada, P2.
Tamaños: 12, 24 y 48 agentes.

Total: 36 combinaciones por escenario de demanda y semilla.

Comenzar con 24 agentes y una carga no saturada.

Medir:
- Tasa de éxito dentro del plazo.
- Latencia.
- Utilización de recursos.
- Coste operativo.
- Diferencias entre políticas.
- Interacción composición × organización.

Utilizar realizaciones pareadas e intervalos de confianza.

6. RIESGOS PRINCIPALES

- Baselines demasiado débiles.
- Información privilegiada.
- Saturación que oculte diferencias organizativas.
- Heterogeneidad construida artificialmente para favorecer resultados.
- Confusión entre competencia, velocidad y disponibilidad.
- Atribuir a la composición mejoras causadas por la política.

7. REFERENCIAS FUNDAMENTALES

Braun et al. (2001): planificación heterogénea y Min-Min.
Mitzenmacher (2001): balanceo de carga.
Agrawal y Goyal (2013): Thompson Sampling contextual.
Pinedo: Scheduling: Theory, Algorithms, and Systems.
SimPy: simulación de eventos discretos.

DICTAMEN E2

El protocolo es suficientemente concreto para comenzar.

Recomiendo ejecutar primero el diseño factorial sin cooperación, utilizando políticas consolidadas y controles informativos explícitos.

La pregunta científica es:

¿En qué condiciones la heterogeneidad de competencias mejora o perjudica el rendimiento colectivo, y cómo depende ese efecto de la política de organización?

No debe presuponerse una ventaja de la heterogeneidad.

Los resultados negativos, las equivalencias y las condiciones en que una organización sencilla iguala a otra más sofisticada también serán científicamente relevantes.

No recomiendo prolongar la fase de diseño ni introducir nuevas arquitecturas.

E2 — FIN DEL INFORME.
