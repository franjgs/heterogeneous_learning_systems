# Paso 5, Fase A3.1 — Viabilidad de mecanismos y diagnóstico del escenario

**Estado:** diagnóstico de viabilidad completado; A3 no está completada. El repertorio D1/T/Q/C/M está aprobado provisionalmente para evaluación, pero no congelado. C es todavía una especificación/prototipo diagnóstico, no una política implementada. No se ejecutó campaña comparativa de rendimiento.

## 1. Objetivo y criterios

Se estudia si el modelo permite que las reglas propuestas produzcan decisiones distintas y si esas diferencias pueden atribuirse a urgencia, competencia, información central o matching. Distinguimos:

1. **Oportunidad estructural:** hay una o más parejas elegibles en el snapshot.
2. **Oportunidad conjunta:** el grafo bipartito tiene matching de cardinalidad `nu(G)>=2`.
3. **Conflicto de asignación:** una decisión local/greedy consume una alerta o analista de forma que reduce el objetivo agregado alcanzable por otra asignación.
4. **Desacuerdo:** las reglas eligen parejas o conjuntos distintos.
5. **Diferencia de objetivo prevista:** sus asignaciones tienen distinto número en plazo, cardinalidad u otra métrica predicha.
6. **Efecto de episodio:** al simular dinámicas completas cambian SLA terminal, calidad, espera, backlog o coste.

Estos niveles no son equivalentes. Los estados de contraste de la sección 5 son pruebas lógicas construidas, no evidencia de frecuencias operativas ni de beneficio sostenido.

## 2. Auditoría de implementaciones relevantes

- `D1` está en `_dispatch_d1` de `src/hls/rq1_allocation.py`: analistas libres en orden barajado por el RNG sembrado; selección secuencial por riesgo temporal truncado, competencia propia, elegibles libres de pares y deadline/llegada/ID. No se modifica.
- `P1` y `P2` están en `_dispatch_local_priority` y `_dispatch_local_competence`: selección local secuencial por menor holgura `d-t-s` y competencia propia, respectivamente.
- `P3` (`_dispatch_local_capacity`) puntúa la escasez de otros analistas libres elegibles para cada alerta pendiente y luego la competencia propia; no reserva analistas ante futuras llegadas.
- `P4` llama a `_dispatch_coordinated(..., "B1", ...)`: matching del snapshot por número previsto a tiempo, cardinalidad, urgencia de deadline y desempate determinista. El objetivo es local al despacho, no al horizonte.
- `P5` compara P3/P4 por la pareja prevista (número a tiempo, cardinalidad); la activación no descuenta el coste de recursos de coordinación.
- **C no está implementada en el repertorio vigente.** Los mecanismos históricos C0/C1/C2 pertenecen a otra formulación y no se usan como sustituto.
- `AllocationSession.advance_to()` agrupa llegadas y finalizaciones de un mismo timestamp y libera recursos; el caller invoca `dispatch()`. `simulate()` incorpora todas las llegadas del timestamp y las finalizaciones simultáneas antes de una época de despacho. No hay parámetro de espera deliberada entre evento y despacho.
- A1, en `studies/soc_human_ai_organization/calibrate_a1_scenarios.py::inspect_stage`, registra el estado después de `advance_to` y antes del despacho D1. Calcula aristas elegibles, `nu(G)`, número de matchings de cardinalidad máxima y previews P3/P4. No calcula C ni el conflicto C–M.

El despacho inmediato no imposibilita matching múltiple en general: la prueba existente `test_simultaneous_arrivals_and_completions_can_create_multi_matching_state` crea dos alertas y libera dos analistas en un mismo evento. Sí elimina las oportunidades residuales después de una decisión exhaustiva cuando entre eventos cambia solo un lado del grafo con un único vértice. El argumento de grafo estrella de los expertos es válido bajo esas condiciones, no como invariante universal del motor.

## 3. Criterios formales para C y M

Sea `G_t=(F_t,Q_t,E_t)` el grafo de analistas libres y alertas pendientes, donde `(i,a)∈E_t` si i es elegible para a. Para coordinación con latencia `ell`, una pareja es temporalmente puntual si `t+ell+s_ia<=d_a`.

- `nu(G_t)>=2` es necesario para asignar conjuntamente dos o más tareas, pero **no suficiente** para que M mejore C.
- También se requiere conflicto: una elección greedy de C debe impedir o degradar una asignación posterior respecto a un matching conjunto factible bajo la misma prioridad. Formalmente, si `A_C` y `A_M` son las asignaciones, debe existir un objetivo primario preespecificado `J` tal que `J(A_M)>J(A_C)` estrictamente. Con el objetivo propuesto, `J` es lexicográfico: (número previsto en plazo, número total asignado, vector de deadlines más próximos, desempate estable).
- Si `nu(G_t)>=2` pero C y M producen la misma asignación (o asignaciones equivalentes en plazo, cardinalidad y métricas relevantes), hay oportunidad estructural pero no contraste efectivo.
- Si difieren las asignaciones pero todas tienen holgura suficiente y servicio/calidad equivalentes, hay desacuerdo sin efecto medible de episodio.
- Si `nu(G_t)=1`, M puede todavía elegir otra pareja o analista, pero tal diferencia es una selección central de una pareja, no evidencia de matching conjunto.

### Candidato diagnóstico de C (no implementado)

Para evitar confundir centralización con matching, C tendría acceso al mismo snapshot, elegibilidad, tiempos, deadlines y latencia que M. Seleccionaría una sola pareja; la retiraría y actualizaría los recursos; repetiría hasta no quedar pareja elegible. El orden local común propuesto es: puntual antes que tardía; entre puntuales, menor holgura (deadline más urgente); entre tardías, menor tardanza prevista; IDs estables. Este procedimiento greedy no maximiza el número de asignaciones puntuales del conjunto. M usa ese mismo orden de urgencia para desempatar, pero maximiza primero el número global de asignaciones puntuales y luego cardinalidad.

Esta especificación hace posible un contraste de información central/selección secuencial frente a optimización conjunta. **No debe llamarse comparación causal limpia hasta congelar en A3.2 los desempates, alcance de cada decisión central, coste por época y regla de repetición de C.** Si C recibiese una regla de desempate que ya protegiera globalmente la pareja alternativa, podría eliminar el contraste; si se le da un objetivo de cardinalidad global, dejaría de ser C y se acercaría a M.

## 4. Diagnóstico cuantitativo de A1 y simultaneidad

Se reutilizó el artefacto local sintético `results/soc_a1_calibration/dispatch_opportunities.csv` (sin datos SOCTRA) y el código/configuración A1. Los porcentajes siguientes son descriptivos de filas diagnósticas, no inferencias independientes: varias celdas de latencia/coste reevalúan las mismas trazas y sus filas no deben tratarse como episodios estadísticos independientes.

| Pool | Filas | Estados con ≥2 libres | Estados con una alerta multi-elegible | `nu(G)>=2` | Estados P3/P4 con pareja distinta | P4 mejora lexicográficamente el objetivo previsto vs P3 |
|---|---:|---:|---:|---:|---:|---:|
| L1 | 162.517 | 44.759 (27,54%) | 26.419 (16,26%) | 0 | 36.687 (22,57%) | 8.203 (5,05%) |
| L2 | 7.746 | 5.586 (72,12%) | 5.586 (72,12%) | 0 | 197 (2,54%) | 74 (0,96%) |

En L1 hubo al menos dos alertas pendientes en 67,51% de filas, pero `nu(G)` permaneció 1 como máximo; en L2 solo 5,10% tenía dos o más alertas pendientes. La coexistencia de analistas libres y cola no basta: las aristas pueden estar concentradas en una única alerta o los recursos libres no cubrir clases distintas simultáneamente. La multiplicidad de matchings máximos en A1 suele contar alternativas de **una sola pareja** y no evidencia una asignación múltiple.

Los desacuerdos P3/P4 y sus diferencias de objetivo son diagnósticos de esas reglas antiguas; no estiman C–M ni deben atribuirse al matching. En particular, el 22,57% de desacuerdo L1 no es tasa de matching conjunto. P4 mejora su par local previsto en 5,05% de filas L1; tampoco es una mejora de resultado de episodio.

### Llegadas exactas agrupadas

El generador `generate_alerts()` de `src/hls/ia_l1_l2_simulation.py` usa interllegadas exponenciales (Poisson homogéneo o por tramos) y la ráfaga A1 multiplica la tasa en una ventana de dos horas, conservando volumen esperado. No genera lotes: bajo la distribución continua la probabilidad matemática de timestamps de llegada exactamente iguales es cero. En una comprobación acotada de 20 semillas por nivel —semillas `261129000`–`261129019`, baja 0,35× (9,947 alertas/h), referencia 0,85× (24,157/h), sobrecarga 1,25× (35,525/h) y ráfaga 0,65× (18,473/h antes del ajuste de volumen, ventana 8–10 h a ×3)— se generaron 42.293 alertas en 80 trazas de 24 h y hubo **0 timestamps de llegada duplicados**. La ráfaga por tramos no cambia esa propiedad. El cálculo reutiliza `read_config()`/`build_scenario()` del runner A1; no ejecuta el simulador de asignación ni reemplaza los artefactos A1.

Las llegadas y finalizaciones coincidentes sí se agrupan por el motor. Finalizaciones simultáneas pueden surgir de servicios iguales y asignaciones que arrancan en el mismo evento, pero en A1 los servicios por clase/analista y velocidades heterogéneas reducen ese empate exacto. El resultado observado en 170.263 filas —cero `nu(G)>=2`— confirma que **M no tuvo oportunidades de matching múltiple en el régimen A1**, aunque el motor las admite. Para ese generador y despacho inmediato, la frecuencia efectiva observada fue cero; no puede estimarse un beneficio de episodio de M.

No se introdujo batching ni se ejecutó una campaña nueva. El muestreo de duplicados de llegada fue solo una comprobación técnica de un subconjunto de semillas, no una estimación operativa.

## 5. Estados de contraste controlados

Las predicciones de C son el resultado del prototipo greedy diagnóstico descrito en la sección 3, hecho a mano para estos estados; C no existe en producción. D1, T, Q y M se comprobaron con las funciones actuales o se evaluaron directamente con sus reglas. Competencia, servicios y deadlines son valores ilustrativos, no calibrados.

| Caso | Analistas libres | Alertas / elegibilidad | Servicio, competencia y deadlines | Decisión | Lectura |
|---|---|---|---|---|---|
| **D1 vs T: conflicto temporal** | A: elegible para x,y | x y y elegibles para A | `s_Ax=1`, `d_x=0,5`; `s_Ay=10`, `d_y=5`; `e` igual. D1 con seed 0. | D1 elige x: riesgo x=(1−0,5)/1=0,5; riesgo y=(10−5)/10=0,5; desempate por deadline. T elige y: holguras −0,5 y −5; P1 minimiza holgura. | Decisiones distintas. Ambas son tardías; T produce tardanza prevista mayor (5 frente a 0,5 h). Comprueba que “menor holgura” puede priorizar una tarea irrecuperable; no demuestra efecto de episodio. |
| **D1 vs Q: urgencia/calidad** | A: elegible para u,q | u y q elegibles para A | `s=1`; `d_u=0,5`, `e_Au=0,2`; `d_q=10`, `e_Aq=0,9`. | D1 selecciona u por riesgo 0,5 frente a 0 de q; Q selecciona q por competencia. | Aísla un conflicto local: Q favorece calidad modelada y sacrifica el deadline urgente. |
| **D1 vs C: selección de analista por información global** | A y B elegibles para x; orden D1 seed 0 empieza por A | Solo alerta x | `s_Ax=2`, `s_Bx=0,5`; deadline 1; competencia igual. | D1 asigna x a A y prevé tardanza 1 h. C conoce la duración de ambas parejas y elige B; termina en 0,5 h, a tiempo. | Diferencia potencial de selección central con cardinalidad máxima 1; no es matching. La ventaja requiere que C conozca servicio de compañeros, un supuesto no observado en GMV. |
| **C vs M: conflicto conjunto** | A elegible x,y; B elegible solo x | x,y pendientes; `E={(A,x),(A,y),(B,x)}` | Ambos servicios 1; `d_x=1`, `d_y=2`; `t=0`, `ell=0`. Desempate C por alerta urgente y luego ID A. | C greedy selecciona A-x primero; B no puede atender y; resultado: 1 a tiempo, cardinalidad 1. M elige B-x y A-y: 2 a tiempo, cardinalidad 2. | `nu(G)=2`, existe conflicto y M mejora estrictamente el objetivo primario en este snapshot. Estado posible si dos analistas/alertas están disponibles en el mismo evento; caso funcional, no frecuencia natural ni efecto terminal. |
| **Sin ventaja conjunta** | A y B elegibles x,y, mismo servicio | x,y pendientes | Todos los servicios 1; ambos deadlines holgados; mismo nivel de competencia. | C elige A-x y luego B-y; M también puede elegir A-x/B-y; 2 a tiempo en ambas. | `nu=2` y hay varias parejas, pero no hay diferencia de objetivo. M no añade beneficio. |
| **Latencia perjudicial** | A elegible para x | Solo x | `s=1`, `d_x=1,1`, `ell=0,2`. | Sin latencia termina 1,0 a tiempo; C/M con latencia termina 1,2 tarde. | Una sola pareja y `nu=1`: la coordinación no crea matching y su coste temporal cambia SLA de forma adversa. |

El ejemplo C–M depende de la regla greedy/tie-break congelada. El rasgo que crea la mejora no es solo tener dos analistas y dos alertas: A puede trabajar ambas clases, B solo x, y C consume A-x antes de considerar que A-y más B-x preserva dos terminaciones puntuales. Si C incorpora esa complementariedad al ordenar, estaría usando criterio global adicional o realizando una optimización que debe clasificarse explícitamente.

## 6. Viabilidad por política

| Política | Condición mínima para diferir de D1 | Oportunidad observada/limitación | Dictamen A3.1 |
|---|---|---|---|
| **D1** | Referencia; diferencia no aplicable | Regla reproducible, pero la aleatoriedad del orden de analistas puede afectar decisiones | Mantener congelada. |
| **T** | Un analista tiene ≥2 alertas elegibles y D1 y menor holgura las ordenan distinto; discrepancias aparecen con clases/servicios distintos o riesgo D1 saturado | A1 no comparó P1/T con D1 en previews. Estados construidos prueban posible desacuerdo; P1 puede priorizar una tardanza grande por holgura más negativa | Estructuralmente viable; medir SLA, tardanza, espera y colas por clase. Revisar la semántica de tarea irrecuperable antes de congelar regla. |
| **Q** | Un analista tiene alertas elegibles con competencias propias distintas y la prioridad D1 no coincide con la mayor competencia | A1 no calculó Q-vs-D1; si competencias son homogéneas por clase o las alertas son de una sola clase, no diferencia. Competencia/calidad sintéticas | Viable en escenarios heterogéneos; evaluar calidad por separado y no llamar exactitud. |
| **C** | Hay al menos una pareja; C observa atributo global/servicio de compañeros que cambia qué analista o alerta selecciona | No está implementada. Los resultados P4 no sustituyen C. La decisión de asignar un único trabajo puede diferir aunque `nu=1` | Viable como contraste conceptual, pendiente de especificación e implementación aislada. |
| **M** | `nu(G)>=2`, conflicto entre asignaciones factibles y diferente objetivo/resultado potencial | A1 observó 0/170.263 estados `nu>=2`; llegadas A1 sin lotes y servicios heterogéneos no produjeron empates de liberación suficientes. El motor sí admite eventos simultáneos | Funcionalmente viable, empíricamente sin oportunidad en A1; mantener solo como contraste limitado/diagnóstico hasta que A3.2 justifique prevalencia. No atribuirle mejora actual. |

## 7. Conclusiones y requisitos para A3.2

1. **M no es estructuralmente imposible**, pero su oportunidad observada bajo A1 es cero. Con la demanda Poisson continua A1 y despacho inmediato, llegadas simultáneas exactas no se producen en la muestra; las ráfagas por tramos no son lotes. Las terminaciones simultáneas tampoco generaron estados con `nu>=2` en esa calibración. El cuello es el mecanismo temporal combinado con las trazas, no únicamente cantidad nominal de analistas.
2. El gran desacuerdo P3/P4 observado en alta carga no mide coordinación conjunta: si `nu=1`, refleja en buena parte una regla distinta para elegir una pareja. Es un diagnóstico de prioridad, no evidencia C ni M.
3. C añade una pregunta científica identificable (información global y asignación secuencial), pero hoy no hay código que permita evaluarla a nivel de episodio. No afirmar que C mejora ni usar C0/C1/C2 antiguos como sustituto.
4. No se justifica batching artificial. Para M, A3.2 debe establecer si eventos simultáneos ocurren en replay o con un generador empíricamente defendible, y medir su frecuencia por pool, clase y causa. Si siguen sin aparecer, M debe pasar a contraste funcional/secundario o salir del núcleo confirmatorio, salvo decisión explícita de estudiar un mecanismo operativo de coordinación diferida con coste de espera.
5. A3.2 debe analizar competencia propia (T/Q), beneficio de C en `nu=1`, estratos de oportunidad M y coste de latencia por separado. Debe reportar `nu`, número de alternativas, conflictos, desacuerdos, objetivo previsto y resultado de episodio como capas distintas.
6. Necesitan evidencia adicional: semántica de timestamps agrupados, cadencia de liberación real, roster/eligibilidad y velocidades por clase, coste/latencia de coordinación y cualquier procedimiento de despacho central/espera. GMV-CERT solo está descrito cualitativamente; no se le atribuyen prácticas.

**Recomendación provisional:** mantener D1/T/Q/C como mecanismos comparables en A3.2; mantener M como contraste diagnóstico condicionado a oportunidades conjuntas reales, no como política cuya prevalencia o beneficio se dé por supuesto. No cerrar A3 ni iniciar campaña B.

## 8. Decisiones pendientes del PI

- Aprobar la regla exacta de C (prioridad para tardías, desempates y coste por época) y confirmar que se implementará solo como política SOC nueva, sin alterar P1–P5 ni C0–C2 históricos.
- Decidir si M permanece en el núcleo confirmatorio si A3.2 vuelve a encontrar frecuencia prácticamente nula bajo trazas justificables.
- Decidir qué evidencia justificaría modelar despacho periódico/diferido; no usarlo solo para elevar `nu(G)`.
- Aprobar parámetros de competencia, servicio y costes como hipótesis experimentales y no calibración GMV.

## 9. Trazabilidad y pruebas

La calibración, parámetros, semillas y limitaciones A1 están en [A1](SOC_A1_EXPERIMENTAL_DIMENSIONING.md), `config/a1_calibration.json` y `calibrate_a1_scenarios.py`; los resultados CSV usados aquí son locales e ignorados por Git. La taxonomía A2 y la comparación de carteras están en [A2](SOC_A2_POLICY_TAXONOMY_AND_DESIGN.md) y [A2.2](SOC_A2_POLICY_PORTFOLIO_DECISION.md). Los dos expertos externos están representados solo por el resumen del PI en [rediseño del Paso 5](SOC_STEP5_REDESIGN.md), pues no se encontraron los originales.

Se ejecutó `PYTHONPATH=src pytest -q tests/test_soc_organization_policies.py tests/test_rq1_allocation.py`: **52 passed**. Son pruebas funcionales existentes de D1/P1–P5, matching P4 y semántica de eventos; no prueban C, que sigue sin implementar. El subconjunto de llegadas duplicadas y los estados de contraste no son una campaña de rendimiento.
