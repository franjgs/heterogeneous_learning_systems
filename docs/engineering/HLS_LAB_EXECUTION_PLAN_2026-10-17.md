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
| 6 | Router ORACLE Nembhard Direct, como baseline intermedio | COMPLETADO | `router_id="nembhard_oracle"`; información perfecta de experiencia/productividad, ranking funcional P0 actual, tests N×K; no es un router aprendido ni reproducción de MixLLM |
| 7 | Router Nembhard basado en estimaciones | COMPLETADO (entrega integrada única; 2026-10-17) | `nembhard_adaptive`; observación individual configurable, estimador online, epsilon-greedy reproducible y runner N×K; 48 tests Nembhard y 180 tests N×K focalizados; suite 1,458 passed / 5 fallos históricos conocidos |

**Estado del laboratorio: PARTIAL.** La integración Nembhard usa `mechanism_id="nembhard_direct"`, experiencia `D[N,K]` y parámetros `k,p,r` separados de competencia; productividad al inicio del periodo, output `Σ_i e[i,k]P[i,k](D)Δt`, después incremento de experiencia `eΔt`. Contrato explícito de unidades. Presupuestos limitan intensidad `e` por periodo. Soporta asignaciones explícitas factibles y demanda del entorno. Desde el 17-10-2026 dispone de `nembhard_oracle`, que enumera acciones factibles y aplica el ranking funcional P0 con información perfecta, y `nembhard_adaptive`, que observa output individual, mantiene estimaciones online y selecciona usando esos valores con exploración epsilon-greedy opcional. Ambos usan la producción Nembhard verdadera y el catálogo compartido; el primero conoce perfil/experiencia verdaderos, mientras el segundo no accede al perfil/productividad verdaderos en su vista de decisión. Ninguno valora aprendizaje futuro. Nembhard sigue sin admitir P0/P1/P2 históricos, MIS-v2, enseñanza, transferencia o estimación de competencias. MIS-v2 permanece predeterminado. Router adaptativo: 48 tests Nembhard y 180 tests N×K focalizados; suite completa 1,458 passed/5 fallos de integridad conocidos; no hubo campaña científica. Se conservaron cambios locales ajenos.

## 4. Calendario reajustado (objetivos, no resultados)

| Fecha | Trabajo principal | Entregable o criterio de cierre | Estado |
|---|---|---|---|
| 17 oct. | Integración Nembhard–HLS y formalización del plan | Adaptador y pruebas; registro de decisiones | Integración COMPLETADA (222 tests focalizados); plan incorporado en esta revisión documental |
| 17 oct. | Router Nembhard ORACLE intermedio | Selección determinista de asignaciones con productividad verdadera; tests N×K | COMPLETADO (166 tests focalizados combinados); no estima ni aprende |
| 19 oct. | Revisión de integración y contrato de comparación | Nota de observables comunes, límites de comparación y tests | PREVISTO |
| 20 oct. | Modelo de información para decisión | Definir estado conocido/estimado, productividad, costes y política base | PREVISTO |
| 21 oct. | Análisis de componentes MixLLM | Mapa de predicción, routing, feedback y límites de reutilización | PREVISTO |
| 22 oct. | Diseño del router Nembhard basado en estimaciones | Se conserva como antecedente del calendario; consolidado en entrega única del 17 oct. | ABSORBIDO; no es hito independiente |
| 23 oct. | Implementación inicial del router basado en estimaciones, si está preparado; revisión semanal | Se conserva como antecedente del calendario; consolidado en entrega única del 17 oct. | ABSORBIDO; no es hito independiente |
| 26 oct. | Integración de política con mecanismos compatibles | Tests end-to-end, sin equivalencias implícitas | CONDICIONAL |
| 27 oct. | Revisión Baccara y System-1.x | Opciones de componentes reutilizables | PREVISTO |
| 28 oct. | Consolidación ontológica y arquitectónica | Arquitectura y contratos reales actualizados | PREVISTO |
| 29 oct. | Diseño de protocolo exploratorio | Escenarios, métricas, controles, comparabilidad; ejecución solo con autorización | PREVISTO |
| 30 oct. | Informe de cierre de fase | Capacidades, tests, límites, decisiones y siguiente fase | PREVISTO |

El objetivo inicialmente previsto para el 19–20 oct. (adaptador Nembhard) se adelantó al 17 oct. La etapa de router ORACLE se completó como baseline intermedio. La decisión registrada el 17 oct. consolida estimación y routing basado en observaciones en una única entrega implementable, sin diseño/implementación como subfases; queda completada en el alcance acotado descrito abajo. No se autoriza por ello ninguna campaña.

## 5. Registro de decisiones (acumulativo)

| Fecha | Cambio respecto del plan previo | Motivo | Consecuencia |
|---|---|---|---|
| 17-10-2026 | Pasar de calendario secuencial de lectura a construcción y validación incremental | Auditoría, extracción e infraestructura avanzaron antes de las fechas previstas | Mantener línea base; adelantar integraciones |
| 17-10-2026 | No exigir réplica completa de Nembhard | Se prioriza reutilizar mecanismos acotados con convenciones explícitas | Curva directa y adaptador; transferencia y réplica completa aplazadas |
| 17-10-2026 | Retirar evaluación de novedad/publicabilidad del calendario operativo | Instrucción expresa del PI | Sustituir hito del 28 oct. por consolidación de arquitectura y ontología |
| 17-10-2026 | Dar por terminada la integración Nembhard acotada según informe Codex | Commits `be4d1a0`, `f73e688` y 222 tests focalizados | Priorizar contrato de comparación y router; no confundir integración con política automática |
| 17-10-2026 | Revisar el calendario y publicar este plan con su registro acumulativo de decisiones | Hacer explícitos los cambios de calendario y conservar la línea base sin sustituirla | El registro y las tablas se mantienen versionados; el router adaptativo permanece como siguiente objetivo y las campañas siguen requiriendo autorización específica |
| 17-10-2026 | Cambiar el hito inmediato previamente denominado «router adaptativo inspirado en MixLLM» por un baseline Nembhard ORACLE; conservar como objetivo posterior el router basado en estimaciones | Validar selección, catálogo y ranking con estado verdadero de productividad antes de añadir inferencia, sin presentar el ORACLE como aprendido ni como reproducción de MixLLM | `nembhard_oracle` queda disponible como baseline determinista de decisión actual; el siguiente diseño debe estimar productividad desde observaciones, sin equipararla a competencia HLS |
| 17-10-2026 | Consolidar el objetivo previamente pendiente de estimación y routing en una sola entrega integrada, en vez de diseño e implementación como hitos separados | La ruta completa Observe → Estimate → Decide → Produce → Learn puede especificarse y validarse en el componente Nembhard existente; dividirla añadiría hitos sin necesidad técnica | `nembhard_adaptive` implementado con observación individual, estimación online, exploración epsilon-greedy opcional y trazas. La evidencia/limitaciones se registran en `engineering/HLS_NEMBHARD_ADAPTIVE_ROUTER.md`; no se crean subfases ni se autorizan campañas. HLS permanece PARTIAL |
| 17-10-2026 | No autorizar campañas por el mero hecho de estar en el calendario | Aún no hay protocolo aprobado para nueva campaña | 29 oct. queda en diseño; ejecución requiere permiso |
| 17-10-2026 | Registrar toda modificación del plan en archivo versionado | Evitar pérdida de decisiones entre chats y agentes | Actualizar tablas y registro, hacer commit y push identificables |
| 17-10-2026 | Seleccionar como máximo un siguiente mecanismo de entre MixLLM, System-1.x y Baccara, sin alterar el calendario vigente | Tras completarse `nembhard_adaptive`, la comparación conjunta favorece una extensión contextual del routing, cuyo seam de decisión y trazabilidad ya existe; las otras opciones requieren estados centrales ausentes | Se recomienda un predictor contextual de calidad/coste por candidato actualizado con feedback del candidato seleccionado, inspirado en componentes de MixLLM y condicionado a un contrato de datos/unidades. System-1.x se difiere por falta de planes/subobjetivos verificables; Baccara por falta de llegadas, colas y capacidad de servicio. No es implementación, no añade fechas ni autoriza campañas; evidencia en `engineering/HLS_NEXT_MECHANISMS_SELECTION_2026-10-17.md` |
| 17-10-2026 | Fijar el contrato técnico de la adaptación MixLLM-inspired seleccionada, sin alterar el calendario | La selección necesitaba determinar unidades, predicción contextual, feedback parcial, objetivo y fallback antes de cualquier implementación; HLS no debe confundir calidad/coste con CES, competencia o esfuerzo | Contrato v0.1 documentado en `engineering/HLS_MIXLLM_ROUTER_CONTRACT.md`: calidad [0,1], coste monetario por consulta en una moneda/versionado, regresión ridge contextual separada para calidad/coste, actualización solo con outcomes observados y selector de coste mínimo sujeto a objetivo de calidad con fallback explícito. Supuestos: contexto/candidatos exógenos, evaluator/ledger versionados y priors declarados. Pendiente por instancia: dataset/schema, moneda/medición, priors y si el presupuesto debe ser hard; especificación, no implementación. No se cambian fechas ni se autoriza campaña. |
| 17-10-2026 | Implementar el contrato contextual MixLLM-inspired como capacidad sintética independiente, sin alterar el calendario | Validar de extremo a extremo predicción contextual, selección, ejecución seleccionada y actualización desde feedback observado en un entorno determinista controlable | Implementados `src/hls/contextual_router.py` y `contextual_router_synthetic.py`, con 17 tests focalizados, incluyendo el ejemplo manual del contrato y replay en procesos nuevos. La instancia declara calidad en [0,1] y coste monetario simulado por consulta; priors, transformaciones, evaluator y ledger reales siguen requiriendo decisión por dominio. Regresiones N×K: 162 pasaron; suite completa: 1,476 pasaron y 5 fallos históricos de procedencia/integridad. No es reproducción de MixLLM, no integra agentes N×K, no ejecuta campaña y no altera rutas MIS-v2/Nembhard/P0/P1/P2. Detalle: `engineering/HLS_MIXLLM_ROUTER_IMPLEMENTATION.md`; HLS permanece PARTIAL. |

## 6. Procedimiento obligatorio para cambios futuros

1. Identificar fecha/objetivo anterior, nuevo objetivo, razón y dependencias afectadas.
2. Modificar tablas de estado y calendario **sin borrar la línea base**, y añadir entrada fechada al registro.
3. Vincular documentación, tests y commits; distinguir evidencia verificada de informe de un agente.
4. Publicar la modificación en `feature/hls-laboratory-v1`, preservando cambios locales ajenos.
5. Comunicar SHA, estado de push y asuntos pendientes. No declarar una actividad completada sin evidencia.
