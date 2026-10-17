# HLS Laboratory — Plan operativo y registro de decisiones (17–30 octubre 2026)

**Estado:** plan de trabajo vigente e incorporado al repositorio en la revisión documental del 17-10-2026. **Rama:** `feature/hls-laboratory-v1`. **Autoridad:** planificación operativa; no sustituye `docs/HLS_CURRENT_STATE.md`, `docs/HISTORY.md`, la ontología ni los protocolos congelados.

## 1. Reglas de gestión

- Construir y validar componentes HLS; no exigir reproducción íntegra de artículos para reutilizar mecanismos delimitados.
- No evaluar novedad o publicabilidad en esta fase, por decisión del PI.
- Mantener separados competencia, productividad, exposición, esfuerzo, output, presupuesto y observaciones; declarar adaptaciones.
- No modificar resultados históricos ni artefactos congelados. PDF científicos solo locales.
- Distinguir tests focalizados de suite completa y experimentos científicos.
- **Todo cambio de fechas, prioridades, alcance o criterios se registra en este documento en el mismo commit que lo oficializa**, sin borrar el plan anterior.
- Las campañas experimentales requieren autorización específica; el calendario no la concede.

## 2. Calendario original (línea base, no borrar)

| Fecha | Trabajo previsto inicialmente |
|---|---|
| 19 oct. | Auditoría de la memoria científica HLS |
| 20 oct. | Selección inicial de 6–10 artículos |
| 21 oct. | Priorización de 3–4 investigaciones |
| 22 oct. | Análisis matemático de los modelos |
| 23 oct. | Ontología HLS v0.1 y revisión semanal |
| 26 oct. | Matriz de reutilización del laboratorio |
| 27 oct. | Reproducibilidad y comparabilidad |
| 28 oct. | Memoria de novedad científica |
| 29 oct. | Diseño experimental preliminar |
| 30 oct. | Informe final y decisión GO / REFRAME / STOP |

## 3. Hoja de ruta de mecanismos — estado comunicado por Codex el 17 oct.

| Prioridad | Actividad | Estado | Evidencia y límite |
|---|---|---|---|
| 1 | Evaluador independiente Nembhard Direct | COMPLETADO | Commits `2e65926`, `f345535` |
| 2 | Tests matemáticos y regresión | COMPLETADO (focalizados) | 24 tests del mecanismo + 184 regresiones N×K comunicados |
| 3 | Adaptador experimental Nembhard–HLS | COMPLETADO (acotado) | Commits `be4d1a0`, `f73e688`; 222 tests focalizados; sin campañas |
| 4 | Transferencia indirecta Nembhard | APLAZADO | Fuera de integración actual |
| 5 | Reproducción completa del artículo | APLAZADO / FUERA DE ALCANCE | No necesaria para adaptación acotada |
| 6 | Router adaptativo inspirado en MixLLM | SIGUIENTE | Requiere política e información de productividad compatibles |

**Estado del laboratorio: PARTIAL.** La integración Nembhard usa `mechanism_id="nembhard_direct"`, experiencia `D[N,K]` y parámetros `k,p,r` separados de competencia; productividad al inicio del periodo, output `Σ_i e[i,k]P[i,k](D)Δt`, después incremento de experiencia `eΔt`. Contrato explícito de unidades. Presupuestos limitan intensidad `e` por periodo. Soporta asignaciones explícitas factibles y demanda del entorno; no políticas P0/P1/P2, MIS-v2, enseñanza ni estimación en esa ruta. MIS-v2 permanece predeterminado y sus serializaciones coinciden con selección explícita en modos probados. No hay política automática Nembhard. Suite completa no ejecutada para esta integración. Se conservaron cambios locales ajenos.

## 4. Calendario reajustado (objetivos, no resultados)

| Fecha | Trabajo principal | Entregable o criterio de cierre | Estado |
|---|---|---|---|
| 17 oct. | Integración Nembhard–HLS y formalización del plan | Adaptador y pruebas; registro de decisiones | Integración COMPLETADA (222 tests focalizados); plan incorporado en esta revisión documental |
| 19 oct. | Revisión de integración y contrato de comparación | Nota de observables comunes, límites de comparación y tests | PREVISTO |
| 20 oct. | Modelo de información para decisión | Definir estado conocido/estimado, productividad, costes y política base | PREVISTO |
| 21 oct. | Análisis de componentes MixLLM | Mapa de predicción, routing, feedback y límites de reutilización | PREVISTO |
| 22 oct. | Diseño del router HLS | Contrato mínimo de política, baseline y plan de pruebas | PREVISTO |
| 23 oct. | Implementación inicial del router, si está preparado; revisión semanal | Router probado o bloqueo documentado y nuevo plazo | CONDICIONAL |
| 26 oct. | Integración de política con mecanismos compatibles | Tests end-to-end, sin equivalencias implícitas | CONDICIONAL |
| 27 oct. | Revisión Baccara y System-1.x | Opciones de componentes reutilizables | PREVISTO |
| 28 oct. | Consolidación ontológica y arquitectónica | Arquitectura y contratos reales actualizados | PREVISTO |
| 29 oct. | Diseño de protocolo exploratorio | Escenarios, métricas, controles, comparabilidad; ejecución solo con autorización | PREVISTO |
| 30 oct. | Informe de cierre de fase | Capacidades, tests, límites, decisiones y siguiente fase | PREVISTO |

El objetivo inicialmente previsto para el 19–20 oct. (adaptador Nembhard) se adelantó al 17 oct. El tiempo liberado se asigna al contrato de comparación y a los datos necesarios para un router. Las fechas de implementación del router son orientativas, no garantías.

## 5. Registro de decisiones (acumulativo)

| Fecha | Cambio respecto del plan previo | Motivo | Consecuencia |
|---|---|---|---|
| 17-10-2026 | Pasar de calendario secuencial de lectura a construcción y validación incremental | Auditoría, extracción e infraestructura avanzaron antes de las fechas previstas | Mantener línea base; adelantar integraciones |
| 17-10-2026 | No exigir réplica completa de Nembhard | Se prioriza reutilizar mecanismos acotados con convenciones explícitas | Curva directa y adaptador; transferencia y réplica completa aplazadas |
| 17-10-2026 | Retirar evaluación de novedad/publicabilidad del calendario operativo | Instrucción expresa del PI | Sustituir hito del 28 oct. por consolidación de arquitectura y ontología |
| 17-10-2026 | Dar por terminada la integración Nembhard acotada según informe Codex | Commits `be4d1a0`, `f73e688` y 222 tests focalizados | Priorizar contrato de comparación y router; no confundir integración con política automática |
| 17-10-2026 | Revisar el calendario y publicar este plan con su registro acumulativo de decisiones | Hacer explícitos los cambios de calendario y conservar la línea base sin sustituirla | El registro y las tablas se mantienen versionados; el router adaptativo permanece como siguiente objetivo y las campañas siguen requiriendo autorización específica |
| 17-10-2026 | No autorizar campañas por el mero hecho de estar en el calendario | Aún no hay protocolo aprobado para nueva campaña | 29 oct. queda en diseño; ejecución requiere permiso |
| 17-10-2026 | Registrar toda modificación del plan en archivo versionado | Evitar pérdida de decisiones entre chats y agentes | Actualizar tablas y registro, hacer commit y push identificables |

## 6. Procedimiento obligatorio para cambios futuros

1. Identificar fecha/objetivo anterior, nuevo objetivo, razón y dependencias afectadas.
2. Modificar tablas de estado y calendario **sin borrar la línea base**, y añadir entrada fechada al registro.
3. Vincular documentación, tests y commits; distinguir evidencia verificada de informe de un agente.
4. Publicar la modificación en `feature/hls-laboratory-v1`, preservando cambios locales ajenos.
5. Comunicar SHA, estado de push y asuntos pendientes. No declarar una actividad completada sin evidencia.
