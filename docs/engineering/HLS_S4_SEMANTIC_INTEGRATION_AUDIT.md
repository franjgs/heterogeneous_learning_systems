# HLS S4 N×K — Auditoría semántica de integración

**Hito 2.1 — 23 de octubre de 2026**
**Rama revisada:** `feature/hls-laboratory-v1`
**Alcance:** caracterización de una referencia ya existente. No se cambió
runner, política, física, objetivo, contrato, catálogo PEF ni resultado
histórico. No se implementó el adaptador S4 permanente.

## 1. Objetivo y conclusión ejecutiva

Se comprobó si una ejecución S4 N×K puede expresarse con `ExperimentRun` v1
y las métricas PEF disponibles sin confundir competencia, esfuerzo,
producción, servicio y CES. La respuesta es **sí para la semántica colectiva
registrada en la referencia exacta**, mediante un adaptador pequeño que
conecte filas de periodo y el diseño. La salida histórica contiene suficiente
información para esos campos. No se requiere cambiar el contrato ni ampliar
el catálogo PEF.

Hay límites de alcance: la referencia es un Bellman exacto con estado real y
demanda completa conocidos, no una ejecución P0/P1/P2 parcialmente observada;
la calidad/rendimiento individual no está definida como objetivo; el output
por agente se deriva de la ley productiva, no se guarda como campo; y el
artefacto no lleva revisión de software ni semillas porque la instancia es
determinista. Por tanto, recomiendo **GO acotado para Hito 2.2** sobre esta
ruta exacta, preservando esos límites. No es evidencia de integración
general S4 ni autorización para otra campaña.

## 2. Instancia S4 seleccionada

Se seleccionó la referencia determinista S4 «MIS-v2 frente a transferencia
opcional», implementada en
[`hls_s4_transfer_exact.py`](../../src/hls/synthetic/hls_s4_transfer_exact.py)
y construida por
[`run_hls_s4_transfer_exact.py::make_case`](../../experiments/run_hls_s4_transfer_exact.py).
El runner `run()` escribe sobre su artefacto histórico; esta auditoría no lo
invocó. Las pruebas llaman a `make_case`, `solve_bellman` y funciones físicas
sin ejecutar el escritor.

| Elemento | Configuración efectiva |
|---|---|
| Sistema | Agentes A/B; competencias x/y; `C₀=((.85,.15),(.2,.2))` |
| Demanda y horizonte | Conocida y determinista `task-x, task-y, task-y`; `T=3` |
| Requisitos | x: `(.35,0)`; cada y: `(0,.70)` |
| Pesos CES | x: `(1,0)`; y: `(0,1)`; `ρ=0.5` |
| Competencias | MIS-v2 tras producir; opción B añade transferencia tras MIS-v2 |
| Recursos | Límite por agente 1.0; presupuesto colectivo 2.0; cada problema limita también a 2.0; docencia usa `2h` |
| Régimen informacional | Referencia exacta observa competencias reales y conoce la secuencia completa; no hay feedback ruidoso ni semilla aleatoria |
| Mecanismos | A: Bellman exacto, sin transferencia; B: mismo Bellman con transferencia opcional |
| Catálogos | 36 acciones por periodo para A y 72 para B; construcción independiente comprobada y acciones A contenidas en B |
| Regresión | `J_A=J_B=1.9175000000000004`; Bellman coincide con enumeración independiente; cero eficacia de transferencia reproduce A |

La instancia es una referencia organizativa de **esfuerzo productivo N×K**,
no matching bipartito ni asignación indivisible agente-tarea. La acción
conjunta es una matriz continua/discreta de esfuerzo productivo por
agente-competencia, con posible acción docente.

## 3. Semántica física original

Las definiciones verificadas están en
[`hls_lab_nk_production.py`](../../src/hls/hls_lab_nk_production.py),
[`hls_lab_nk_geometry.py`](../../src/hls/hls_lab_nk_geometry.py),
[`hls_s4_transfer_exact.py`](../../src/hls/synthetic/hls_s4_transfer_exact.py)
y [`hls_lab_nk_teaching.py`](../../src/hls/hls_lab_nk_teaching.py).

### Producción y competencia

Para esfuerzo `e_{ikt}` y competencia real previa `c_{ikt}`:

`y_{kt} = Σ_i e_{ikt} c_{ikt}`.

La salida agregada es un vector por competencia. La contribución individual
`y_{ikt}=e_{ikt}c_{ikt}` es derivable con exactitud en esta referencia porque
se guardan esfuerzo y competencia previa y la ley es determinista. La salida
por agente no es, por ello, una medida de calidad o utilidad individual.
Competencia (`[0,1]`) es un estado físico; no es esfuerzo, output, reward ni
éxito.

MIS-v2 se aplica después de registrar output/reward, celda por celda:

`c'_{ik}=1-(1-c_{ik}) exp(-λ(η_{ik})e_{ik})`.

Si hay docencia, la transición docente actúa sobre el estado ya actualizado
por MIS-v2. Ninguna enseñanza fue elegida en las trayectorias óptimas A/B de
esta instancia, aunque B dispone de ella.

### Requisitos, servicio y déficit

Para requisitos `q_k`, éxito es `all(y_k + 10⁻¹² ≥ q_k)` sobre los índices con
`q_k>0`. Déficit absoluto por dimensión es `(q_k-y_k)_+`; déficit normalizado
es la suma de `deficit_k/q_k` solo sobre requisitos activos; margen es el
mínimo `y_k-q_k` activo. La referencia guarda éxito y vector de déficits
absolutos; requisito por periodo se obtiene uniendo el índice temporal con
`design.requirements`. El código rechaza un vector de requisitos todo cero.

Una asignación de esfuerzo no implica cumplimiento. En la traza A/B, periodo
0 produce `1.05` en x frente al requisito `.35` y cumple; periodo 1 produce
`.35` en y frente a `.70` y falla pese a producción positiva; periodo 2
produce `.5175` frente a `.70` y vuelve a fallar. Solo uno de los tres
periodos cumple. Esto muestra por qué output positivo no es éxito.

### Objetivo original y recursos

Reward por periodo es CES antes de transiciones:

`R_t = (Σ_k w_{kt} y_{kt}^{ρ})^{1/ρ}`, con pesos no negativos que suman 1;
el valor por defecto verificado es `ρ=.5`.

El objetivo Bellman es la suma de estos rewards. Los requisitos funcionales
no entran automáticamente en CES; recursos tampoco se restan del reward.
En esta instancia las ponderaciones ponen todo el peso en la competencia
demandada y la trayectoria produce solo esa competencia, por lo que reward
CES y output total coinciden numéricamente (`1.9175`). Es coincidencia de
esta configuración, no identidad general.

El coste productivo es `E_t=Σ_{ik}e_{ikt}`; el consumo docente es `H_t=2h_t`;
consumo total `E_t+H_t`, capacidad aplicable
`min(budget_organization,budget_problem)` y ociosidad su diferencia no
negativa. La unidad «effort» es abstracta del modelo, no dinero, tiempo ni
energía. En cada periodo óptimo de esta instancia, producción consume 2.0 de
2.0, sin ociosidad. Recursos son restricciones físicas y diagnósticos, no
penalización CES.

## 4. Semántica organizativa y modelo de decisión

El problema decide esfuerzo productivo por agente y competencia bajo límites
individuales y colectivo; B permite añadir una acción docente factible. El
runner genera el catálogo completo declarado y comprueba que los catálogos
independientes coinciden, que B contiene todas las acciones de A y que cada
asignación respeta recursos. El solver Bellman maximiza CES acumulado, no
éxito funcional ni minimización de déficit.

En el S4 exacto elegido, información real y observable de la política de
referencia es estado completo; la demanda futura está conocida por
construcción. No se debe extrapolar este perfil al N×K P0/P1/P2 imperfecto:
esa ruta tiene otros registros y reglas de información.

## 5. Matriz de compatibilidad semántica

`DIRECTA` significa que el resultado fuente contiene la magnitud con su
semántica; aún hay una conversión de tipo para un campo PEF. `DERIVABLE`
indica cálculo algebraico desde datos conservados. `REQUIERE_ADAPTADOR`
indica que la semántica cabe en tipos existentes pero exige juntar/remapear
registros. Las etiquetas son de esta auditoría, no nuevos estados de código.

| Magnitud S4 | Definición original | Unidad / nivel | Fuente de código/datos | Campo `ExperimentRun` posible | Métrica/campo PEF | Transformación necesaria | Disponibilidad | Riesgo semántico |
|---|---|---|---|---|---|---|---|---|
| Competencia real | Matriz `c_{ik}` antes/después de MIS y docencia | Escala de competencia; agente×skill×periodo | `PeriodResult.competence_before/after_mis/after`; JSON A/B | `initial_conditions`, eventos `state_update`/`execution` | `competence_state` (diagnóstico) | Mapear estados y marcar que son estado real del exact reference | DIRECTA | No confundir con estimación observada por políticas imperfectas |
| Esfuerzo productivo | Matriz `e_{ik}` de la acción | Esfuerzo abstracto; agente×skill×periodo | `JointActionNK.production` | Evento `decision` | `available_metadata`/diagnóstico | Conservar matriz; no reducirla a output | DIRECTA | Esfuerzo no es competencia ni output |
| Producción individual | `e_{ik}c_{ik}` | Output model-specific; agente×skill×periodo | Derivable de acción y competencia previa; no campo independiente | Payload de evento | No hay métrica PEF por agente | Calcular solo como diagnóstico si se desea; no etiquetar como calidad individual | DERIVABLE | No existe criterio de calidad individual |
| Producción colectiva | `y_k=Σ_i e_{ik}c_{ik}` | Output por skill×periodo; unidad externa no declarada | `PeriodResult.outputs` | Evento `execution` | `EvaluationRecord.output`; `production_cumulative` | Copiar vector al record, sumar por periodo | REQUIERE_ADAPTADOR | No asumir dimensión de output ni utilidad de skills con peso CES cero |
| Requisito | `q_k` del `ProblemSpecNK` activo | Output por skill×periodo | `design.requirements[t]` | `configuration` o datos del evento | `EvaluationRecord.requirements` | Unión por tiempo; horizonte y orden deben coincidir | DERIVABLE | Un desfase temporal hace inválida la evaluación |
| Cumplimiento funcional | Todos los requisitos activos alcanzados con tolerancia `1e-12` | Booleano por problema-periodo | `PeriodResult.success` / `evaluate_problem_nk` | Evento `execution` | `EvaluationRecord.success`; `functional_success_rate` | Copia por periodo; denominador = periodos demandados (3) | DIRECTA | No sustituir por reward o output positivo |
| Déficit funcional absoluto | `(q_k-y_k)_+` | Output por skill×periodo | `PeriodResult.deficits` | Evento `execution` | `EvaluationRecord.deficit`; `functional_deficit_cumulative` | Copiar y sumar por skill/periodo | DIRECTA | No confundir con déficit normalizado; PEF actual mide suma absoluta |
| Déficit normalizado / margen | `Σ deficit_k/q_k`; `min(y_k-q_k)` activos | Sin unidad / output; periodo | `FunctionalResultNK`, calculable de output/requisito; no persistido en `PeriodResult` | Evento diagnóstico | Sin métrica PEF correspondiente en catálogo | Derivable, pero no incluido en esta integración | DERIVABLE | No declararlo calculado/medido por el runner |
| CES/reward | Fórmula CES sobre outputs y pesos; reward original de Bellman es CES | Output compuesto / periodo | `PeriodResult.reward`, pesos en `design.ces_weights` | `MetricValue`; evento `execution` | `original_reward_cumulative`, `ces_cumulative` | Mapeo directo; distinguir IDs/unidades aun cuando valores coincidan | DIRECTA | No incorpora éxito ni coste; no asumir equivalencia con servicio |
| Esfuerzo productivo | `Σ_{ik}e_{ik}` | effort / periodo | `PeriodResult.productive_effort` | Evento `execution`, `MetricValue` | `resource_usage:productive_effort` | Copia/suma | DIRECTA | Esfuerzo del modelo, no coste monetario |
| Recurso docente/total/ocioso | `2h`; `E+H`; `max(0,B-E-H)` | effort / periodo | `PeriodResult` | Evento `execution` | `resource_usage:teaching_resource`, `total_resource` | Copiar separado por recurso; no sumar dos veces | DIRECTA | Ociosidad no es penalización del reward |
| Capacidad/límites | Límite por agente y colectivo; presupuesto de cada problema | effort/periodo; agente y colectivo | Configuración y validador factibilidad | `configuration`; decisión/evento | No hay métrica de restricción activa | Registrar como restricciones y derivar slack desde acción/recursos | DERIVABLE | Capacidad declarada no equivale a recurso consumido |
| Política/información | Bellman A/B con estado real y secuencia futura conocida | política/ejecución | `design.demand_information`, `competence_information`; `actions` | `mechanism_id`, `policy_id`, `information_available` | `EvaluationProfile.decision_objective`, `information_regime` | Declarar «exact reference, full state/future sequence known» | REQUIERE_ADAPTADOR | No compararlo como si fuera política parcialmente observada |
| Calidad individual/valor por agente | No definida por este escenario | No definida | No hay métrica individual de calidad/reward | Evento puede retener outputs por agente | Sin métrica PEF | No inventar objetivo individual; `NOT_APPLICABLE` si se solicita | NO_APLICABLE | Output individual no es utilidad/calidad individual |

## 6. Información, observabilidad y procedencia

| Categoría | Qué consta en esta instancia | Evaluación |
|---|---|---|
| Estado real | Competencia completa antes, después de MIS y después de transferencia | Disponible al exact reference y guardado para diagnóstico |
| Información de política | Estado real exacto; secuencia `x,y,y` y modelo determinista conocidos | El artefacto lo declara explícitamente; no es un problema de aprendizaje parcial |
| Decisión | Esfuerzo por agente×competencia y docente opcional, por periodo | Guardada en las acciones de A/B |
| Transición | MIS-v2 y transferencia como etapas separadas | Incrementos y estados antes/después disponibles |
| Resultado | Vector de producción agregado, reward/CES, éxito, déficit y recursos | Guardado por periodo; producción individual se deriva con fórmula verificada |
| Evaluación retrospectiva | PEF lee estado/resultados completos para calcular sus indicadores | Admisible porque es información de evaluador y el perfil declara estado completo; no retroalimenta decisiones |
| Procedencia | Artefacto JSON y función/fuente de referencia; sin semilla ni revisión | Se debe registrar la ruta y dejar revisión desconocida; ejecución determinista con `random_seeds=()` |

No hay observaciones Bernoulli ni observabilidad parcial en este caso. La
palabra «observado» no debe usarse como sinónimo de output calculado desde el
estado real. Tampoco debe exponerse `competence_before` como entrada de
políticas distintas de esta referencia exacta.

## 7. Casos de estrés semántico observados

| Caso | Decisión y hecho físico | Registro existente | PEF posible | Riesgo a evitar |
|---|---|---|---|---|
| A — producción y requisito satisfecho | Periodo 0, ambos agentes dedican 1 a x; outputs individuales `.85,.20`, output x `1.05`, requisito `.35`; éxito | Acción, competencia previa, output, reward, éxito, déficit y recursos | Output 1.05, éxito verdadero, déficit 0, reward 1.05 | No llamar a 1.05 «reward» en general; aquí coinciden por peso CES x=1 |
| B — producción positiva, requisito fallido | Periodo 1, ambos producen y; output `.35` frente a `.70`; déficit `.35`, éxito falso | Los mismos campos por periodo | Éxito falso y déficit positivo pese a output y reward `.35` | No inferir cumplimiento de producción positiva ni de CES positivo |
| C — recurso/capacidad activa | Cada periodo usa esfuerzo productivo 2, capacidad aplicable 2, ociosidad 0; límites individuales 1 | Esfuerzo, recurso docente, total y ociosidad; acción íntegra | Recurso productivo/total 6 acumulado; `effort` | Consumo de capacidad no es una penalización adicional CES; no contabilizar E dos veces dentro de total |

Los tres casos están en la trayectoria A y también en B; ambas políticas
óptimas coinciden en acciones en esta instancia. B permite enseñar, pero no
enseña. Esto es una observación de la instancia y no evidencia de inutilidad
general de la transferencia.

## 8. Resultados de regresión y HLS-PEF

Las pruebas recalculan Bellman A/B a partir de `make_case()` sin llamar al
escritor del runner. También recalculan producción, éxito/déficit, CES y
recursos desde las funciones físicas ya implementadas. El artefacto fuente
mantiene:

| Métrica S4 | A | B | PEF | Estado / unidad / agregación |
|---|---:|---:|---|---|
| Recompensa original acumulada | 1.9175 | 1.9175 | 1.9175 | VALID; `declared_reward`; suma de 3 periodos; definición declara CES |
| CES acumulado | 1.9175 | 1.9175 | 1.9175 | VALID; `CES_output`; suma de periodos |
| Tasa funcional | 1/3 | 1/3 | 1/3 | VALID; fracción; 1 éxito / 3 periodos demandados |
| Déficit absoluto acumulado | .5325 | .5325 | .5325 | VALID; unidad `output`; suma de dimensiones y periodos |
| Producción acumulada | 1.9175 | 1.9175 | 1.9175 | VALID; `output`; suma de skills y periodos |
| Esfuerzo productivo | 6.0 | 6.0 | 6.0 | VALID; `effort`; suma de periodos |
| Recurso docente / total | 0.0 / 6.0 | 0.0 / 6.0 | igual | VALID; `effort`; suma de periodos |

Estos valores ya se habían recalculado mediante
[`run_hls_pef_retrospective.py`](../../experiments/run_hls_pef_retrospective.py)
desde el JSON existente; la prueba confirma el mapeo y sus unidades. El
perfil declara objetivo CES, horizonte 3, demanda determinista `x-y-y` e
información completa. PEF no reconstruye política ni física; consume records
de periodo. No se añadió ni redefinió métrica.

## 9. Compatibilidad de `ExperimentRun` v1

La prueba temporal crea un sobre v1 con IDs, configuración, condición inicial,
sin semillas aleatorias, información disponible, observación determinista,
declaraciones de unidad, eventos de decisión/ejecución, reward y payload
fuente. El round-trip JSON preserva los campos. Las matrices y resultados
caben en `configuration`, `initial_conditions`, eventos y
`mechanism_results`; `information_available` puede declarar correctamente
que el exact reference recibe estado completo.

No se identificó una limitación de capacidad en el esquema. Sí se necesita un
adaptador que una requisitos del diseño con periodos, asigne IDs/procedencia
y mantenga la salida por agente como diagnóstico. `ExperimentRun` no da
campos tipados S4 ni asocia por sí mismo un `EvaluationProfile`; esto se
resuelve en metadata/mapas, como en S2a, sin crear otra estructura. La
representación estructural no hace comparable este caso con políticas que
reciben información distinta.

## 10. Compatibilidad y límites de HLS-PEF

| Métrica/campo | Datos requeridos y disponibles | Definición / unidad / denominador | Estado |
|---|---|---|---|
| `original_reward_cumulative` | `PeriodResult.reward`, tres periodos | Suma; `declared_reward`, objetivo CES declarado | VALID |
| `ces_cumulative` | Outputs y CES registrado | Suma de CES; `CES_output` | VALID |
| `functional_success_rate` | Demanda, requisitos, success | `Σ success / 3`; fracción | VALID; denominador positivo |
| `functional_deficit_cumulative` | Déficit vectorial por periodo | Suma por skill/periodo; output | VALID |
| `production_cumulative` | Outputs agregados por skill/periodo | Suma de output; la unidad externa no está especificada por el modelo | VALID con unidad genérica `output` |
| `resource_usage:productive_effort` | Esfuerzo en las matrices de acción | Suma; esfuerzo abstracto | VALID |
| `resource_usage:teaching_resource` | `2h` por acción docente | Suma; esfuerzo abstracto | VALID (valor medido 0) |
| `resource_usage:total_resource` | `E+H` | Suma; esfuerzo abstracto | VALID |
| Calidad/utilidad individual | El escenario no define función de calidad individual | No hay unidad ni denominador | NOT_APPLICABLE si se solicita |
| Producción por agente | Derivable, no es métrica del catálogo | Por agente×skill; no agrega como reward | No se calcula por métrica PEF; conservar como diagnóstico/evento |
| Métrica de restricción activa/slack | Límites/acciones existen | Slack derivable desde factibilidad y recursos | No está en el catálogo PEF; mantener en diagnóstico |

En esta instancia no se deben usar `NOT_RECORDED`, `NOT_OBSERVABLE` ni
`UNDEFINED` para datos completos que sí están presentes. `NOT_APPLICABLE`
corresponde a calidad individual no definida; cero docencia es un valor
`VALID`, no ausencia.

## 11. Limitaciones detectadas

1. Es una sola configuración exacta T=3; no valida la ejecución N×K de
   políticas P0/P1/P2, estimación parcial, aleatoriedad o distribución de
   seeds.
2. Las unidades output/effort son escalas del modelo, no magnitudes físicas
   externas; el PEF debe declarar esa limitación.
3. No existe un objetivo de calidad/rendimiento individual. El output por
   agente se deriva, pero no implica calidad individual.
4. El PEF actual no tiene métrica de output individual ni de slack/violación
   de recursos; esos datos pueden vivir como diagnósticos, sin extensión de
   catálogo en esta fase.
5. La configuración hace que reward y output acumulado coincidan. No usar
   esta coincidencia como identidad ni doble contarlos.
6. El piloto S4 retrospectivo actual mapea JSON a `EvaluationRecord` dentro
   de un runner de auditoría; aún no es una ruta S4 que emita un
   `ExperimentRun` en ejecución.

## 12. Propuesta mínima para Hito 2.2

Si el PI autoriza:

1. Añadir un adaptador localizado sobre el resultado de
   `solve_bellman`/`replay_actions` que traduzca `PeriodResult` a
   `ExperimentEvent`, métricas/units y `EvaluationRecord` existentes. No
   modificar el solver, `make_case` ni leyes.
2. Definir un `EvaluationProfile` específico de la referencia exacta, con
   objetivo CES e información `full true state and known deterministic demand
   sequence`; conservar recompensa original y CES como métricas separadas.
3. Evaluar output, cumplimiento, déficit y recursos disponibles. Salida por
   agente y slack se quedan como diagnósticos, no nuevas métricas.
4. Ejecutar A y B usando la configuración existente en un runner de
   integración que escriba en una ruta nueva; nunca llamar al escritor
   histórico ni cambiar A/B.
5. Comparar A/B por perfil compatible. Etiquetar la comparación como esta
   referencia determinista; no inferir incertidumbre estadística ni
   superioridad general.

### Pruebas de aceptación propuestas

- Reproducir `1.9175000000000004` para A y B, sus acciones y estados por
  periodo, con enumeración/regresión existente intacta.
- Reconciliar `y_k=Σ_i e_{ik}c_{ik}`, CES, success, déficit, `E`, `H`, total
  y ociosidad con las funciones físicas.
- Reproducir las métricas PEF anteriores, unidades, denominadores, estados y
  procedencia del resultado fuente.
- Validar `ExperimentRun.to_json/from_json`, IDs de política/configuración,
  separación de información y eventos temporales.
- Verificar que evaluación conectada/desconectada no cambia acciones,
  estados ni archivo histórico.
- Mantener `NOT_APPLICABLE` para calidad individual, y no crear métrica
  individual o de cobertura de restricciones sin definición aprobada.

## 13. Decisiones pendientes del PI

1. Autorizar o no Hito 2.2 para la referencia exacta S4 N×K descrita, sin
   extender todavía a P0/P1/P2.
2. Confirmar que producción individual sea diagnóstico y no objetivo en esta
   primera integración.
3. Confirmar unidad declarada `output`/`effort` como escalas abstractas del
   modelo, sin conversión física.

## 14. Evidencia y referencias

- [Runner exacto y configuración `make_case`](../../experiments/run_hls_s4_transfer_exact.py)
- [Modelo exacto, `PeriodResult`, transición y solución](../../src/hls/synthetic/hls_s4_transfer_exact.py)
- [Producción, CES y funcionalidad](../../src/hls/hls_lab_nk_production.py)
- [Geometría/requisitos y límites](../../src/hls/hls_lab_nk_geometry.py)
- [MIS-v2](../../src/hls/hls_lab_nk_learning.py) y [transferencia/recursos docentes](../../src/hls/hls_lab_nk_teaching.py)
- [Artefacto fuente histórico](../../results/experiments/hls_s4_transfer_exact/results.json)
- [Evaluación retrospectiva existente](../../experiments/run_hls_pef_retrospective.py) y [su resultado](../../results/experiments/hls_pef_retrospective/results.json)
- [Caracterización ejecutable nueva](../../tests/synthetic/test_hls_s4_pef_semantic_characterization.py)
- [Contrato común](../../src/hls/experiment_contract.py), [PEF](../../src/hls/performance_evaluation.py) y [S4 N×K en el plan](HLS_LAB_EXECUTION_PLAN_2026-10-17.md)

## Seguimiento — Hito 2.2, integración operativa (23 Oct 2026)

Con autorización posterior del PI, se implementó el adaptador localizado
[`s4_pef_adapter.py`](../../src/hls/synthetic/s4_pef_adapter.py) y el runner
[`run_hls_s4_pef_integration.py`](../../experiments/run_hls_s4_pef_integration.py).
El adaptador convierte el resultado resuelto en `ExperimentRun` v1 y filas
`EvaluationRecord`; no elige acciones ni reconstruye una trayectoria desde
HLS-PEF. El runner escribe el nuevo artefacto
[`results.json`](../../results/experiments/hls_s4_pef_integration/results.json)
en una ruta separada.

Dos perfiles operan sobre los mismos resultados: evaluación colectiva básica
y evaluación ampliada con recursos y diagnósticos existentes. Ambos
reproducen reward/CES `1.9175000000000004`, producción `1.9175`, cumplimiento
`1/3` y déficit `.5325`; el perfil ampliado además registra esfuerzo
productivo `6`, esfuerzo docente `0`, recurso docente `0`, total `6` y cero
acciones docentes. Reward y producción conservan IDs y unidades distintos.
El cambio de perfil no altera el `ExperimentRun`, records, acciones, estados
ni resultados de origen.

Se comprobó reutilización estructural de `ExperimentRun`, `EvaluationProfile`,
`EvaluationRecord` y `PerformanceEvaluator` con S2a, S4 y S7. Cada familia
mantiene su perfil, unidades y disponibilidad semántica. S2a se genera en
memoria con su función determinista para reconstruir los records completos;
su artefacto guardado no se sobrescribe. El piloto S7 se rehidrata de sus 16
ramas archivadas y su CES ponderado vuelve a coincidir. Esto valida la
reutilización de estructuras, no una métrica común entre escenarios.

**Límite conservado:** el resultado S4 es una referencia exacta que conoce
competencias reales y secuencia futura. No valida las políticas P0/P1/P2 ni
observación parcial. B no selecciona transferencia: esta integración valida
representación semántica y contabilidad, no un beneficio causal/físico de
enseñar. El esquema v1 y el catálogo PEF permanecieron sin cambios. La
validación automatizada y el estado de los criterios C1–C10 quedan registrados
en la entrada Hito 2.2 del plan acumulativo.
