# HLS — Matriz de correspondencias y comparabilidad (v0.1)

**Fecha:** 2026-10-17. **Alcance:** auditoría de cuatro antecedentes contra la ontología y el laboratorio HLS existente. **Sin implementación ni campañas.**

## Fuentes y nivel de evidencia

- Nembhard & Bentefouet (2015): `docs/literature/audits/Nembhard_Bentefouet_2015_Mathematical_Extraction.md`, extracción original con páginas impresas 175–187; PDF local `competence_evolution/Nembhard_Bentefouet_2015_Selection_Grouping_Assignment.pdf`, SHA-256 `30129963aa6b69197140552b9431480b7b976d5c3d521eabbe3ec63478402e81`.
- Baccara, Lee & Yariv (2023): manuscrito de autor 2022, `cross_cutting/Baccara_et_al_2023_Task_Allocation_OnTheJob_Training.pdf`, SHA-256 `230af14ae06a4896a3f8091668d201b39bcf8a0da12fb83a40bef339a19a22ad`. La presente matriz se basa en la formalización anterior; **no** en una nueva extracción completa de este PDF.
- Wang et al. (2025), MixLLM: `cross_cutting/Wang_et_al_2025_MixLLM_Dynamic_Routing.pdf`, SHA-256 `b0881cf583c83a84566b85584d1a2f57f3c356b891a952b657aa0f8140473659`; auditoría matemática previa de ecuaciones 1–20.
- Saha et al. (2025), System-1.x: `cross_cutting/Saha_et_al_2025_System1x_Fast_Slow_Planning.pdf`, SHA-256 `e8a58d039d882842145a868aeffd1a9076246d015afff608d111ecc1ba1d11b1`; auditoría matemática previa del algoritmo 1.
- Autoridad semántica: `docs/hls_ontology.md`. Autoridad de estado: `docs/HLS_CURRENT_STATE.md` (revisión leída en rama `feature/hls-laboratory-v1`). Las cuatro referencias están en `docs/literature/references.bib` según comprobación local de Codex.

## A. Matriz estructural

| Dimensión | Nembhard–Bentefouet | Baccara–Lee–Yariv | MixLLM | System-1.x | HLS actual / veredicto |
|---|---|---|---|---|---|
| Unidad de decisión | Seleccionar 9/45, agrupar 3×3, asignar 9 tareas y periodos | Asignar llegada a junior o senior, política probabilística o umbral de cola | Enviar consulta a un LLM entre varios | Descomponer un plan y resolver tramos por System-1/2 | **RELATED**: `a_t` general; el runner HLS P0 no implementa selección de plantilla, colas ni subplanes |
| Estado de capacidad | Parámetros `k_ij,p_ij,r_ij,theta_ij`, productividad acumulada | Capacidad agregada senior `mu=f(x)` en régimen estacionario | Modelos candidatos, predictores del router | Planificadores, controlador, heurística de dificultad | **RELATED**, nunca identificar directamente `k`, `mu`, `p_hat` o dificultad con `S_mk` |
| Evolución de capacidades | Experiencia directa e indirecta afecta productividad individual | Servicio junior sostiene capacidad senior agregada | Aprendizaje del **router**, no demostrado del LLM | Entrenamiento del controlador/planificadores; no actualización online por uso en el modelo evaluado | Nembhard **RELATED** con MIS-v2; Baccara **RELATED** solo agregado; MixLLM **INCOMPATIBLE** como aprendizaje de agentes; System-1.x **INCOMPATIBLE** como MIS online |
| Organización/cooperación | Agrupación y transferencia dentro de tipo de máquina | Asignación y externalidades de cola/formación | Router a un candidato | Composición secuencial de subplanes | Todos `a_t` **RELATED**; solo MixLLM se aproxima al routing monoejecutor |
| Tiempo | Periodos de duración `L` y horizonte anual | Proceso de llegadas, espera y régimen estacionario | Secuencia de consultas, espera por modelo | Pasos de plan y estados explorados | **INCOMPATIBLE** sin modelo explícito de tiempo y unidades |
| Recursos | Exclusividad trabajador/tarea, sin presupuesto monetario en MINLP | Capacidad de servicio y espera | Tokens/precios y penalización de cola | Estados explorados y coste de búsqueda | **RELATED** a recursos HLS solo con transformación explícita; no sumarlos como magnitudes homogéneas |
| Información | Parámetros del trabajador usados por heurísticas; fuente de datos ajustada | Monitorización perfecta/limitada de cola | Embeddings, predicciones, feedback parcial del elegido | Dificultad estimada, planes/trazas | **UNRESOLVED** igualdad de información frente a P0/P1/P2; HLS P0 tiene información perfecta en ciertos runners |
| Objetivo original | Throughput paralelo o cuello de botella por línea serie | Calidad menos coste de espera | Compromiso calidad/coste/incertidumbre/espera | Validez de plan y exploración | **INCOMPATIBLE** comparación de puntuaciones originales; usar métricas físicas y objetivos compartidos justificados |
| Demanda | Nueve tareas fijas, sin proceso externo variable | Poisson, tasa `lambda` | Consultas secuenciales | Instancias de planificación | **RELATED** como tareas; procesos no equivalentes |
| Resultado observable | Producción | Calidad y espera | Calidad de respuesta, tokens/coste/espera | Plan válido y estados explorados | **UNRESOLVED** una variable universal de calidad; se requieren tareas comunes y validadores |

## B. Correspondencias ontológicas auditables

| Fuente y símbolo | Significado original | Destino HLS | Clase | Transformación/condición requerida |
|---|---|---|---|---|
| Nembhard `x_ijt` | Indicador binario de asignación trabajador–tarea–periodo | `a_t` | EQUIVALENT en tipo de decisión, **no** en dominio factible | Identificar índices y restricciones de exclusividad |
| Nembhard `P_ijt` | Tasa de productividad del trabajador | `Qbar`/producción esperada | RELATED | Conversión tasa→producción requiere duración y agregación; no confundir con competencia |
| Nembhard `k_ij` | Productividad asintótica | Parámetro de desempeño, no `S` | RELATED | Función explícita entre parámetros de curva y competencia, si se define |
| Nembhard `sum L*x` | Experiencia directa | `E_dir` | RELATED | Unidad de exposición temporal; resolver convención de `L` |
| Nembhard `T_ijt` | Experiencia indirecta ponderada por productividad | `E_ind` | RELATED | Preservar pesos, exclusión de trabajador y misma clase de máquina |
| Nembhard `theta_ij` | Eficiencia de transferencia | Parámetro de transición `L` | RELATED | Dominio y tratamiento de negativos/truncamiento pendientes |
| Baccara `q` | Proporción de llegadas asignada a senior | Política `a` | RELATED | Probabilidad de asignación, no acción individual binaria |
| Baccara `mu=f(x)` | Capacidad senior agregada sostenida por formación | Capacidad `b`, desarrollo agregado | RELATED | No identificar con competencia individual `S` ni con transición MIS-v2 |
| Baccara `W` | Espera en cola | Componente de latencia `L(q)` | RELATED | Latencia extremo a extremo requiere añadir servicio; mantener distinción |
| MixLLM `p_hat[n,l]` | Calidad predicha por router | `Qbar` estimada | RELATED | Calibrar a mismo criterio de calidad; no es `Q` observada |
| MixLLM `c_hat[n,l]` | Precio previsto de tokens | Coste económico `C` | RELATED | Precio/moneda/unidades y horizonte compartidos |
| MixLLM `A_l`, predictores | Incertidumbre/aprendizaje del router | Estado informacional `Theta` | RELATED | No mapear a `S_mk` del LLM |
| MixLLM `m*_n` | Modelo elegido por consulta | `a_t` | EQUIVALENT en selección única, condicional | Mismo catálogo y factibilidad de selección |
| System-1.x `x` | Fracción de hibridación en preparación/composición | Hiperparámetro de política | RELATED | No interpretarlo como probabilidad de routing online |
| System-1.x `h(s_i,s_j)` | Dificultad estimada de subobjetivo | Información/contexto `X_t` | RELATED | No confundir con calidad, latencia ni competencia |
| System-1.x tramo `(j,k)` | Selección de subplan System-2 | Organización/secuenciación `a_t` | RELATED | Necesita representación de subobjetivos y validador de plan |
| System-1.x estados explorados | Esfuerzo de búsqueda | Recurso computacional | RELATED | Conversión a CPU/tiempo/tokens requiere medición, no identidad |

## C. Qué puede compararse *hoy* sin falsear modelos

**C0 — Comparación conceptual formal (SÍ):** taxonomía de decisiones, información, efectos de desarrollo, restricciones y objetivos; todos los modelos. No constituye resultado experimental.

**C1 — Comparación experimental directa con runner HLS existente (NO para las cuatro implementaciones originales):** el laboratorio actual posee asignación, competencias, CES, recursos, MIS-v2, enseñanza y algunos runners P0/P1/P2; pero **no** implementa selección/agrupación Nembhard 45→9, formación agregada con M/M/1 Baccara, predictores/feedback y precios de MixLLM, ni planes/subobjetivos de System-1.x. Ejecutar P0/P1/P2 bajo CES no reproduce esos cuatro modelos.

**C2 — Comparación USE *de políticas abstraídas* (VIABLE COMO DISEÑO, NO EJECUTADA):** seleccionar un agente para una tarea entre candidatos, con demanda congelada y mismas competencias, factibilidad, información, calidad observada y recursos. MixLLM puede aportar **la estructura de selección** pero no su fórmula completa sin predictores y semántica de precios/cola. Una asignación greedy y otra estática son comparadores del laboratorio; no llamarlas 'reproducción MixLLM'. Nembhard solo aporta una subdecisión de asignación si se congela selección, grupos y aprendizaje, **no** su política completa. Baccara solo si se elimina formación/cola (se pierde mecanismo decisivo): **no usar como baseline fiel**. System-1.x requiere subplanes: **no comparable aquí**.

**C3 — Comparación USE–DEVELOP de leyes de experiencia (VIABLE COMO DISEÑO, NO EJECUTADA):** MIS-v2 versus curva de productividad Nembhard sobre asignaciones y exposición controladas, **solo tras** declarar un modelo de estado común, equivalencia dimensional, observables y ajuste de parámetros. Las dos leyes no son iguales: Nembhard da rendimiento dependiente de experiencia; MIS-v2 actualiza competencia antes de rendimiento por CES. Comparar resultados exige calibración a curvas observables o hitos de aprendizaje, y medir el coste de exposición. No llamar 'reproducción del experimento Nembhard' a este experimento común. Baccara `mu=f(x)` es agregado estacionario; no entra en este mismo contraste sin modelo de población/servicio. MixLLM no aprende competencias de LLM y System-1.x no comparte transición por exposición online.

**C4 — Comparación de asignación bajo congestión (NO):** Baccara y penalización de espera MixLLM podrían compararse en un nuevo banco de colas, pero el runner actual no implementa semántica homogénea de servicio, llegadas y latencia. No autorizado ampliar simulador.

**C5 — Comparación de composición intra-tarea (NO):** System-1.x requiere tareas planificables, verificación de subobjetivos y medidas de exploración; el runner HLS actual no reproduce esa física.

## D. Controles mínimos de justicia experimental

1. **Misma población exógena:** tareas, demanda, dificultad y semilla, congeladas antes de evaluar cada política.
2. **Mismo conjunto de acciones factibles:** o comparar clases explícitamente distintas y declarar la ventaja de flexibilidad; no atribuir a 'mejor algoritmo' lo que es mayor capacidad de acción.
3. **Mismo conjunto de información:** distinguir oracle P0, predictores entrenados, feedback parcial, acceso a cola y trazas; no usar información futura de forma encubierta.
4. **Misma contabilidad de recursos:** esfuerzo de inferencia, entrenamiento, búsqueda, enseñanza, espera y costes indirectos; reportar vectores físicos cuando no existe conversión justificable.
5. **Mismo objetivo y horizonte:** calidad, producción, validez y utilidad no son idénticas; fijar tarea común, métrica y orientación antes de comparar.
6. **Mismo protocolo de desarrollo:** estado inicial, experiencia, actualización temporal, datos de entrenamiento y exposición; reportar coste de aprendizaje.
7. **Baselines fuertes:** estática óptima dentro de su clase, greedy con la misma información, router aprendido y oráculo solo como cota; distinguir reproducción de adaptación.
8. **Repeticiones emparejadas y trazabilidad:** mismas instancias, semillas, intervalos, logs, versiones de fuente, configuración, código y hash.
9. **Control de fidelidad:** verificar primero invariantes/resultados de cada modelo en su entorno original; luego compararlo en mundo común con etiquetas distintas.

## E. Reutilización frente al estado actual del laboratorio

| Capacidad | Estado según `HLS_CURRENT_STATE.md` | Utilidad | Brecha |
|---|---|---|---|
| Generador de trayectorias exógenas congeladas | Implementado en laboratorio integrado parcial | Emparejar políticas | Verificar cobertura de demanda para cada modelo |
| Asignación y P0/P1/P2 3×2 | Operativos en legacy | Baselines HLS, no réplicas externas | Distintos espacios de acción e información |
| N×K P0 producción y MIS-v2 | Implementación parcial, información perfecta | Banco para USE y desarrollo propio | No equivale a Nembhard, Baccara, MixLLM o System-1.x |
| CES y registro de recursos | Existentes | Métricas comunes dentro del mundo HLS | No convertir automáticamente throughput, valor, calidad, dinero o estados explorados |
| Enseñanza dirigida | En runner integrado 3×2 | Desarrollo explícito | No equivale a transferencia incidental Nembhard |
| Colas y servicio | No hay cola multi-tarea general | Ninguna reproducción Baccara | Mecanismo ausente |
| Embeddings, predictores, bandit router | No identificados como implementación MixLLM | Ninguna réplica MixLLM | Entrenamiento, inferencia, coste y feedback |
| Descomposición de planes | No identificada | Ninguna réplica System-1.x | Planificación, subobjetivos, validadores |

**Importante:** el estado del laboratorio sigue siendo **PARTIAL**; no declarar comparabilidad experimental confirmada.

## F. Juicio y siguiente gate

- **Nembhard:** ESTUDIADO, FORMALIZADO desde original; REPRODUCIBLE **condicional** con ambigüedades `L`, truncamiento de `theta`, desempates, semillas, MINLP y datos individuales. COMPARABLE solo como adaptación expresamente etiquetada.
- **Baccara:** ESTUDIADO y núcleo FORMALIZADO; requiere validación detallada de manuscrito y benchmark de colas para comparación fiel. COMPARABLE en HLS actual: NO.
- **MixLLM:** ESTUDIADO y núcleo FORMALIZADO; más cercano a una comparación USE de selección única. No implementado como política original. COMPARABLE en HLS actual: NO, sí su *clase de decisión*.
- **System-1.x:** ESTUDIADO y núcleo FORMALIZADO; composición de subplanes, no selección única. COMPARABLE en HLS actual: NO.

**GATE 1 (ontología): PASS para clasificación y distinciones; NO PASS para equivalencia cuantitativa ni reproducción.**

**Decisión CE:** Priorizar como primera pregunta experimental un protocolo de **comparación USE de asignación monoejecutor** con baselines existentes y controles fuertes; evaluar después la incorporación fiel de un router aprendido como MixLLM, sin autorizar implementación en este paso. Mantener Nembhard como candidato de desarrollo por experiencia para la siguiente fase. No añadir colas ni planificadores ahora.

**STOP / REFRAME:** si las políticas no pueden recibir iguales observaciones y recursos, o si la comparación exige suprimir el mecanismo definitorio del artículo, etiquetar como **adaptación no equivalente** o excluir del contraste, no reportar superioridad del artículo.

---

# G. Ampliación v0.2 — reutilización de piezas, no solo comparación de artículos

**Cambio de criterio (PI, 17-10-2026).** El objetivo principal no es reproducir cuatro sistemas completos en una única arena, sino identificar componentes científicamente fundados que permitan construir un laboratorio HLS fiel, extensible y capaz de comparaciones controladas. La reproducción original y la reutilización adaptada son pistas independientes. No se descarta un artículo porque su sistema completo no sea directamente comparable.

## G1. Inventario de piezas reutilizables y contrato de adaptación

| Pieza fuente | Objeto matemático / mecanismo | Función HLS posible | Interfaz necesaria | Reutilización mínima defendible | Fidelidad y límites | Prioridad |
|---|---|---|---|---|---|---|
| N1 — Nembhard: curva de aprendizaje | `P=k z/(z+r)`, `z=p+E_dir+theta E_ind` | Ley alternativa de desempeño dependiente de experiencia | `(params, direct_exposure, indirect_exposure)->productivity` | Comparar curvas de respuesta a exposición con MIS-v2 bajo igual secuencia y rendimiento inicial/final calibrado | No equivale a evolución de `S` ni al modelo de producción CES; requiere una capa experiencia→productividad | **P1** |
| N2 — transferencia | `T_ijt` suma experiencia ajena ponderada por productividad y tipo compatible | Operador de experiencia indirecta y transferencia entre agentes | `(assignments, performance, compatibility)->E_ind` | Ablación transferencia OFF/ON con topología de tipos congelada | Preservar exclusión del propio agente, ponderación y orden temporal; circularidad temporal por revisar | **P1** |
| N3 — selección/agrupación/asignación | `45→9→3×3→3 tipos`; 10 heurísticas por etapa | Banco de organización estructural y políticas estáticas fuertes | `(pool, type_map, descriptors, constraints)->teams, assignments` | Comparar agrupaciones homogéneas/heterogéneas y selección por criterio bajo mismo pool | No llamarlo Nembhard completo si se omiten sus restricciones, horizonte o transferencia | **P2** |
| N4 — sistemas paralelo/serie | Suma de throughput vs mínimo por línea | Banco de agregación y cuellos de botella | `(task_outputs, topology)->system_output` | Misma política en dos topologías; medir inversión de rankings | Cambia la función de valor; no mezclar valores brutos | **P2** |
| B1 — Baccara: externalidad formativa | `mu=f(x)`, `x=(1-q)lambda`, `f` creciente/cóncava | Desarrollo de capacidad **agregada** inducido por asignación | `(junior_load, parameters)->senior_capacity` | Modelo reducido de asignación–capacidad, etiquetado como estacionario | `mu` no es competencia individual ni transición temporal; no presentar como aprendizaje MIS | **P2** |
| B2 — espera/congestión | `w=q lambda/[mu(mu-q lambda)]`, estabilidad `q lambda<mu` | Evaluador de latencia y restricción de estabilidad | `(arrival_rate, routing_fraction, service_capacity)->wait` | Banco analítico separado, con límites de estabilidad y casos frontera | No es cola implementada en HLS; no simular episodios discretos usando la fórmula como si fuera dinámica | **P2** |
| B3 — óptimo social vs decisión descentralizada | `theta=w+q w'` frente a `theta=w` en interior | Comparador de externalidad organizativa y eficiencia | `(q, mu(q), lambda, utility)->welfare, equilibrium` | Contrastar decisiones miopes y sociales en el mismo modelo analítico | FOC exige diferenciabilidad, solución interior y estabilidad; extremos deben comprobarse | **P2** |
| M1 — MixLLM: predictores de calidad/coste | `p_hat(q,m)`, `c_hat(q,m)` | Capa de observación/estimación para políticas USE | `(task_features, model_id, history)->estimates` | Baselines de selección por calidad estimada y calidad-coste, con estimadores comunes | Entrenamiento y calibración deben registrarse; predicción no es competencia | **P1** |
| M2 — score de routing | `lambda/(lambda+1) p_hat - c_hat/(lambda+1) + alpha U - beta W` | Política de selección monoejecutor con coste/exploración/espera | `(estimates, uncertainty, queues, budgets)->model_id` | Ablaciones: calidad; calidad+coste; +incertidumbre; +espera, cuando cada señal existe | Sin cola, no implementar el término de espera fingiendo equivalencia; pesos y unidades deben calibrarse | **P1** |
| M3 — feedback parcial / actualización | Observación solo del modelo elegido, actualización de router | Aprendizaje organizativo `theta_t→theta_t+1` separado de `S_t` | `(context, action, observed_outcome)->router_state` | Comparar router fijo, adaptativo no aprendido y aprendido con mismo feedback | Evitar oráculo que observe recompensas contrafactuales; no equivale a aprendizaje de LLM | **P1** |
| S1 — System-1.x: partición de problema | Subobjetivos, segmento `(j,k)` profundo, resto rápido | Acciones composicionales intra-tarea, no solo routing | `(problem, partial_plan, budget)->subgoals, subplans` | Banco independiente de tareas con subobjetivos verificables | Sin planes ni validador no existe adaptación fiel | **P3** |
| S2 — control de esfuerzo de planificación | Fracción `x`, dificultad `h`, estados explorados | Asignación condicional de cómputo deliberativo | `(difficulty, search_budget)->planning_mode` | Comparar presupuestos fijos y adaptativos **en tareas de planificación** | `x` no es probabilidad de routing; estados explorados no equivalen a tokens | **P3** |
| S3 — validez y coste de planes | Verificación de plan y estados explorados | Evaluador conjunto calidad–recursos para planificación | `(plan, world)->validity, search_cost` | Banco de composición separado, con trazas y coste de búsqueda | No trasladar métricas a CES sin una tarea y evaluación compartidas | **P3** |

**Prioridades:** P1 = útil para definir interfaces y controles ahora, **no autorización de implementación**; P2 = banco separado/segunda integración; P3 = requiere nueva familia de tareas. Las piezas pueden estudiarse sin copiar código ni reclamar que el autor original validó su uso en HLS.

## G2. Matriz de comparaciones defendibles por *pieza* (no por marca de artículo)

| Contraste | Universo compartido y variable intervenida | Controles que deben mantenerse | Métricas | Estado actual | Inferencia autorizada |
|---|---|---|---|---|---|
| M1/M2 vs HLS USE (políticas) | Misma tarea, candidatos y acciones; cambiar regla de selección | Vista informacional, estimadores, presupuesto y trayectorias | Valor/éxito, regret, recursos, latencia si medida | **Diseñable**; M2 completo no disponible | Valor de reglas de routing adaptadas; no superioridad de MixLLM original |
| M3 vs organización fija | Misma política parametrizada; activar/desactivar actualización | Inicialización, feedback parcial, exploración, orden temporal | Valor acumulado, coste de exploración, cambios `theta` | **Diseñable** con contrato LO; falta auditoría de implementación concreta | Efecto de aprender la política, no de aprender competencias |
| N1 vs MIS-v2 | Misma exposición y mismas tareas; cambiar ley de respuesta | Estado inicial expresado en rendimiento observable, calibración de curvas, horizonte | Curvas de productividad, valor final/acumulado, sensibilidad | **Requiere adaptador** | Sensibilidad del sistema a la ley de aprendizaje; no equivalencia de parámetros |
| N2 OFF/ON | Misma asignación y experiencia directa; activar transferencia | Topología de compatibilidad, observación, cronología, parámetros | Ganancia incremental, distribución por agente, coste de interacción | **Requiere operador de transferencia** | Efecto condicional de experiencia indirecta en modelo adaptado |
| N3 selección/grupos | Mismo pool, topología, criterios y presupuesto | Fijar composición cuando se prueba solo agrupación; fijar agrupación cuando se prueba solo asignación | Producción, equidad, diversidad, sensibilidad | **Requiere nuevas acciones** | Valor de una etapa organizativa bajo las otras fijadas |
| N4 paralelo vs serie | Misma capacidad, asignaciones y trayectorias | Cambiar únicamente agregador/topología | Throughput y cuellos de botella | **Requiere evaluador** | Sensibilidad de ranking a topología, no ventaja universal |
| B1/B2/B3 | Modelo estacionario común de colas, mismos `lambda,f,h,l,c` | Estabilidad, política interior/frontera, información de cola | Bienestar, espera, throughput, brecha social–privada | **Banco analítico separable**, no HLS runner | Externalidad de formación y congestión en el modelo de Baccara |
| S1/S2/S3 | Misma colección de problemas planificables, validadores y límites | Datos de entrenamiento, presupuesto de búsqueda, planes de referencia | Validez, estados explorados, tiempo | **No disponible en runner actual** | Valor de composición fast/deep, no routing monoejecutor |
| USE × DEVELOP (M3 con N1/N2) | Mismo entorno HLS, router y ley de experiencia declarados | Factorial LI/LO, coste de entrenamiento, orden de actualización | Rendimiento acumulado, Δcapacidad, regret | **Diseñable tras adaptadores y controles** | Interacción entre mecanismos adaptados, sin atribuir novedad al mecanismo individual |

### Experimentos analíticos que no exigen ampliar el simulador

1. **Nembhard, derivadas y límites:** con `z=p+E_dir+theta E_ind` y `z+r>0`, `dP/dE_dir=kr/(z+r)^2`, `d²P/dE_dir²=-2kr/(z+r)^3`; `dP/dE_ind=theta kr/(z+r)^2`. Para `theta<0`, la transferencia puede reducir productividad y `z+r>0` debe preservarse. Esto permite construir pruebas de propiedades antes de programar.
2. **Baccara, estabilidad y externalidad:** si `mu=f((1-q)lambda)` y `q lambda<mu`, la espera aumenta al acercarse a la frontera de estabilidad; comparar `theta=w` con `theta=w+q w'` únicamente en soluciones interiores. No inferir equilibrio social sin revisar fronteras.
3. **MixLLM, separación de señales:** con predicciones y recursos congelados, `alpha=beta=0` reduce la regla a calidad–coste; si el coste es constante entre candidatos, el ranking coincide con calidad predicha para `lambda>0`. No extrapolar a predictores aprendidos.
4. **System-1.x, dominios de `x`:** `x=0` y `x=1` requieren revisar las convenciones del algoritmo y las tareas concretas; no presumir que ambos extremos constituyen baselines válidos sin verificar la implementación editorial.

## G3. Compatibilidad técnica con HLS actual: contratos concretos y límites

| Contrato de laboratorio existente | Pieza que puede acoplarse conceptualmente | Qué debe conservarse | Evidencia de disponibilidad | Estado |
|---|---|---|---|---|
| Problema `r`, dificultad, presupuesto `B`, evaluación funcional | M1/M2/M3, N1 | Independencia de requisitos y recompensa; calidad no igual a CES | `HLS_LAB_V1_SCIENTIFIC_CONTRACTS.md`, §§1–3; `HLS_CURRENT_STATE.md` | **Interfaz propuesta; integración externa no verificada** |
| Expertos `s`, `ŝ`, exposición `e`, transición `F` | N1/N2 | `S != Qbar != Q`, experiencia != competencia; transición tras producción | Contratos §§2, 5; N×K MIS-v2 parcial | **Adaptador necesario** |
| Organización `pi_theta`, estado `theta`, actualización `U` | M3 | `a_t` distinto de `theta_{t+1}`; feedback posterior a acción | Contratos §3; implementación específica MixLLM no localizada | **Adaptador necesario** |
| Acciones de asignación y restricciones | M2, parte de N3 | Igual factibilidad, presupuesto, competencia observable | Legacy 3×2 y N×K P0 parcial | **Solo subconjunto de acciones** |
| Registro `Y`, éxito, déficit, recursos | M1/M2 y N1 en mundo HLS | Misma métrica y coste, no equivalencia throughput/CES | Contratos §§1,4; runners parciales | **Reutilizable tras calibración** |
| Generador exógeno congelado | M1/M2/M3 | Misma secuencia y semillas antes de política | `HLS_CURRENT_STATE.md` | **Reutilizable con auditoría de rutas** |
| Enseñanza dirigida 3×2 | N2 como inspiración, no copia | Enseñanza deliberada `d_t` ≠ transferencia incidental | `HLS_CURRENT_STATE.md` | **RELATED, no equivalente** |
| Sin cola de servicio general | B1/B2/B3 | No ocultar `lambda,mu,w`, estabilidad | Brecha explícita en estado/teoría HLS | **Banco separado** |
| Sin estado de planes/subobjetivos | S1/S2/S3 | No reducir composición a una sola elección | Brecha explícita | **Banco separado** |

**Nota de auditoría:** se han contrastado documentos de estado y contratos, no inspeccionado exhaustivamente todas las rutas de código en la rama local. Por tanto, no se adjudica a ningún archivo o función un adaptador ya implementado que no se haya verificado. La inspección a nivel de función es una tarea de ingeniería separada y de solo lectura.

## G4. Plan de integración científica por niveles y criterios de aceptación

**Nivel 0 — Validación de fuente.** Para cada pieza: ecuaciones con páginas, supuestos, unidades, dominio, resultados de referencia y discrepancias. Salida: ficha verificable, no código.

**Nivel 1 — Banco nativo.** Reproducir cada pieza en su universo original, sin reescribir semántica. Ejemplos: propiedades y políticas Nembhard, benchmark estacionario Baccara, routing MixLLM, planificación System-1.x. Aceptación: invariantes + resultados/ablaciones de referencia dentro de tolerancias justificadas. No afirmar completado.

**Nivel 2 — Adaptador HLS.** Definir explícitamente `(estado, observación, acción, transición, resultado, recursos, tiempo)` y mapa de unidades; preservar qué es decisión organizativa, aprendizaje del router y evolución de capacidades. Aceptación: pruebas de equivalencia o etiqueta `RELATED` con pérdidas semánticas enumeradas.

**Nivel 3 — Comparación común.** Solo para pares con tareas y evaluadores compartidos: políticas sobre mismas instancias, recursos e información; factoriales de una intervención; baselines informados; trazas reproducibles. Aceptación: protocolo predeclarado, métricas comunes, no confusión de efecto de política y efecto de física.

**Nivel 4 — Composición de piezas.** Probar interacciones M3×N1/N2, N3×N2, o B1×B2 bajo un sistema común justificado. Aceptación: ablation factorial, estimandos claros, controles de no interacción y análisis de sensibilidad. **No atribuir al artículo fuente una validación que no realizó.**

## G5. Riesgos, prioridad y decisiones

| Riesgo | Manifestación | Mitigación / condición de parada |
|---|---|---|
| Cambio silencioso de semántica | Productividad Nembhard presentada como `S` MIS; capacidad Baccara como aprendizaje individual | Exigir mapa tipado, unidades y pérdidas semánticas; si no existe, banco separado |
| Reproducción ficticia | Ablación de MixLLM sin predictores reales etiquetada como MixLLM | Nombre `MixLLM-inspired`; diferenciar nativo, adaptado y HLS baseline |
| Ventaja por información | Router usa predicciones entrenadas con resultados del test o oráculo P0 | Separar entrenamiento/test, registrar feedback disponible y política oráculo solo como cota |
| Confusión de aprendizaje | M3 mejora por ajuste del router y se atribuye a mejora de expertos | Factorial LO/LI con estado `theta` y `S` separados |
| Injusticia de recursos | Tiempo de búsqueda, tokens, dinero y espera sumados sin calibración | Vector de recursos, restricciones comunes y Pareto cuando corresponda |
| Comparación vacía | Modelo original mutilado para encajar en runner | Mantener reproducción nativa; adaptar solo si preserva el fenómeno causal relevante |
| Repetición de HLS histórico | Replantear G2/MIS/G3 o META-VOC como nueva teoría | Reutilizar controles y resultados cerrados; aplicar guardia de novedad |
| Crecimiento prematuro | Añadir colas, planificación y router aprendido antes de cerrar lab v1 | No autorizar implementación; mantener prioridad de aceptación y procedencia v1 |

**Decisión científica actualizada:** **GO** para reutilización modular, auditoría de interfaces y diseño de comparaciones por pieza; **NO-GO** para comparar los cuatro sistemas completos con una puntuación única o implementar extensiones antes de autorización. Primera secuencia razonable: (1) M1/M3 para separar USE estático, adaptativo y aprendido; (2) N1/N2 para separar experiencia directa, transferencia y evolución de rendimiento; (3) interacción controlada entre aprendizaje de organización y aprendizaje de agentes; (4) N3 y B1/B2 como bancos específicos; (5) S1/S2 cuando haya tareas de planificación. Es un orden de análisis, no una decisión de ingeniería irrevocable.

**Pendiente verificable:** auditoría de rutas de código y tests existentes por Codex, extracción matemática primaria completa de Baccara, revisión de detalles reproducibles de MixLLM/System-1.x, y definición de un protocolo mínimo pre-registrable para el primer contraste seleccionado. Ninguna de estas tareas se declara realizada aquí.
