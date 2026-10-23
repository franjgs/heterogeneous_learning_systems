# HLS — Contrato experimental común: auditoría y especificación

**Hito 1, Incremento 1 — 23 de octubre de 2026**
**Rama revisada:** `feature/hls-laboratory-v1`
**Alcance inicial:** auditoría y diseño (Incremento 1).
**Estado actualizado:** Incremento 2 implementado y validado el 23 de octubre
de 2026; no se ejecutó una campaña científica.

## 1. Objetivo y principio

HLS ya cuenta con escenarios, problemas organizativos, mecanismos, runners,
un sobre de ejecución (`ExperimentRun`) y un evaluador independiente
(HLS-PEF). La carencia observada no es la ausencia de todos esos elementos,
sino la conexión reproducible de una ruta a otra. Esta especificación mapea
sus semánticas y propone una integración mínima que reutiliza los objetos
existentes.

La cadena `escenario → problema organizativo → mecanismo → ejecución → PEF`
es una separación de responsabilidades, no un requisito de clases o paquetes
homónimos. El runner conserva el control de la dinámica y las decisiones; un
adaptador traduce sus resultados; PEF calcula métricas sin intervenir en el
bucle de decisión.

## 2. Inventario de interfaces existentes

| Estructura / símbolo | Ubicación y responsabilidad | Campos o contenido relevante | Uso, pruebas y límite |
|---|---|---|---|
| `ExperimentRun` | [`src/hls/experiment_contract.py`](../../src/hls/experiment_contract.py); sobre versionado y serializable de una ejecución | `schema_version`, `run_id`, `mechanism_id`, `policy_id`, `configuration`, `initial_conditions`, `random_seeds`, `information_available`, `observation_model`, `software_revision`, `units`, `events`, `metrics`, `mechanism_results`, `metadata` | Hay cobertura de serialización estable, validación y adaptadores en `tests/test_hls_common_experiment_contract.py`. Es un registro de resultados, no un runner, catálogo universal de escenarios ni protocolo de optimización. Algunos campos de identidad semántica solo caben hoy en mapas libres. |
| `RunAdapterContext` | Mismo módulo; aporta procedencia que no contienen resultados heredados | ID de ejecución, configuración, condiciones iniciales, flujos de semillas, información/observación, revisión de software y metadatos; opcionales | `None` significa desconocido/no suministrado; mapa vacío o tupla vacía puede declarar explícitamente que no hay contenido/aleatoriedad. Adaptadores soportados: resultados N×K seleccionados, Nembhard Direct y ruta contextual. No hay adaptadores generales para S2a, S3b o S7. |
| `SeedRecord`, `UnitDeclaration`, `MetricValue`, `ExperimentEvent` | Mismo módulo; procedencia tipada, unidades, métricas y eventos serializables | Flujo/valor/propósito; magnitud/unidad/interpretación; nombre/valor/unidad/dirección; secuencia/tipo/mecanismo/datos/índice temporal | Validan primitivas y unidades declaradas, pero no pueden deducir unidades omitidas por el simulador. Los eventos admiten payloads de un escenario; no definen un vocabulario universal de estados, decisiones u observaciones. |
| Adaptadores del contrato | `experiment_contract.py` | Convierten clases concretas de resultados al sobre común, sin simular ni normalizar resultados | Son explícitos y no destructivos. El despacho cubre un conjunto acotado de tipos; un artefacto JSON como S2a no se convierte automáticamente. La generación determinista de ID a partir del resultado puede colisionar semánticamente entre réplicas idénticas: el llamador debe dar un ID de ejecución/replicación distinto cuando corresponda. |
| `EvaluationProfile` | [`src/hls/performance_evaluation.py`](../../src/hls/performance_evaluation.py) | IDs de perfil/escenario/configuración; dominio/problema; objetivo por política; restricciones; familias/diagnósticos; régimen informacional; horizonte; agregación; distribución de demanda; disponibilidad; unidades de recursos | Define aplicabilidad y semántica de evaluación. No crea una ejecución ni conserva por sí mismo todos los datos fuente. El perfil no incluye identificación explícita de campaña/replicación. |
| `EvaluationRecord` | Mismo módulo | Periodo, demanda, producción, requisitos, éxito, déficit, recursos, recompensa original, CES, metadatos, procedencia, unidades, tarea/importancia/calidad/episodio/probabilidad/régimen/objetivo/competencias/estado de campos | Entrada suficientemente rica para métricas disponibles y agregación ponderada de episodios. Muchos campos son opcionales; se deben declarar con `field_status` y no reemplazar ausencias por cero. No es un registro físico universal ni todas las rutas producen uno. |
| `EvaluationResult` | Mismo módulo | IDs escenario/configuración/política, métrica/definición/valor/unidad/agregación/estado/procedencia/horizonte/distribución/régimen/contexto/nota | Conserva procedencia y disponibilidad, pero no tiene vínculo tipado a `profile_id`, ID de réplica ni un objeto de diferencias pareadas. |
| `PerformanceEvaluator` | Mismo módulo; agregación, importación y comparación puras | Registro de perfiles; evaluación de registros; agregación ponderada de episodios; importación histórica; valores indisponibles; comparación | Pruebas en `tests/test_hls_performance_evaluation.py`. No importa políticas. La comparación verifica escenario/configuración/definición/unidad/agregación/horizonte/distribución/contexto y régimen informacional, con excepción explícita si se permite desigualdad informacional. Devuelve diferencia escalar; no alinea semillas ni calcula IC pareados. |
| Adaptador S7→PEF | [`src/hls/synthetic/s7_pef_adapter.py`](../../src/hls/synthetic/s7_pef_adapter.py) | Convierte resultados/rutas de demanda S7 en registros de evaluación | Es específico de S7 y solo evalúa; no decide, actualiza competencias ni transita demanda. |
| Runner S7 PEF | [`experiments/run_hls_pef_s7_pilot.py`](../../experiments/run_hls_pef_s7_pilot.py) | Ejecuta cuatro políticas del árbol central T=4, pondera sus 16 ramas con probabilidades | Pruebas PEF/S7 contrastan CES ponderado con el solucionador. Es un piloto integrado operativo que aún no usa el sobre `ExperimentRun`. |
| Resultados S2a | [`experiments/run_hls_s2a_static_demand.py`](../../experiments/run_hls_s2a_static_demand.py) y artefacto bajo `results/experiments/hls_s2a_static_demand/` | Diccionario/JSON: matriz, demanda por periodo, asignaciones, recompensa, unidades satisfechas/no servidas, uso de capacidad, verificación exacta global, tiempos | Prueba determinista ejecuta dos veces y contrasta exacto 8.0, greedy 7.2 y enumeración global 8.0 (84,388 secuencias). No produce `ExperimentRun` ni PEF records. Tiempos son descriptivos y no deben entrar en identidad/reproducción del resultado. |

### 2.1 Contratos, convenciones y adaptadores

- **Implementado:** esquema `ExperimentRun` versionado; tipos de evento,
  semilla, métrica y unidad; perfiles/registros/resultados PEF; estados
  explícitos `VALID`, `NOT_APPLICABLE`, `NOT_OBSERVABLE`, `NOT_RECORDED` y
  `UNDEFINED`; conversión PEF de S7; adaptadores del sobre para algunas
  estructuras N×K, Nembhard y contextual.
- **Convención de runner:** IDs, parámetros, semillas, flujos aleatorios,
  horizonte y resultados se guardan en constantes/diccionarios/JSON propios.
  La convención varía; no equivale a un contrato validado.
- **Adaptador de escenario:** traduce significado específico (p. ej. ramas
  S7 a episodios ponderados). No debe cambiar decisiones ni simular de nuevo.
- **Solo documentado:** el encadenamiento completo de una configuración A/B/C
  con un perfil PEF. No existe una orquestación genérica ya comprobada.

## 3. Flujos reales: S2a, S3b, S4 y S7

| Ruta | Configuración e inicialización | Decisión, ejecución e información | Registro y evaluación |
|---|---|---|---|
| **S2a** | Runner determinista declara matriz estática 3×3, demanda observada por cuatro periodos y capacidad por periodo. | Exact matching o greedy; unidades de tarea se expanden y asignan. No hay estado aprendido, sorteo de recompensas ni semilla. Enumeración global verifica separabilidad y óptimo. | JSON por periodo y agregado, con asignaciones, recompensas, servicio en unidades por tipo y uso de capacidad. Sin contrato común ni PEF. |
| **S3b** | Varios runners declaran matrices/condiciones, horizonte/calibración y semillas; trazas de campañas son separadas. | UCB1/SW-UCB y otras referencias toman decisiones con feedback selectivo; hay potenciales, observaciones ejecutadas y recibidas según protocolo. En el factorial hay subflujos aleatorios separados. | Agregados JSON y, según experimento, trazas temporales comprimidas. No existe un único esquema de evento común. Política debe permanecer aislada de verdad latente/futura. |
| **S4** | Múltiples modelos N×K de asignación, producción, MIS-v2, transferencia, demanda/recursos y estimación. Instancias exactas también tienen clases propias. | Políticas P0/P1/P2 y referencias reactivas/Bellman tienen objetivos e información distintos según la formulación. Trayectorias pueden ser deterministas condicionales a sorteos o emparejadas por semillas. | Varios dataclasses y runners/artifacts. Algunos resultados N×K tienen adaptadores `ExperimentRun`; exactos e informes funcionales no comparten automáticamente la misma semántica. CES, recompensa binaria/lineal y éxito funcional deben seguir separados. |
| **S7** | Estado pequeño, demanda C5 Markov, horizonte T=4; árbol de demanda enumerado exactamente. | Bellman y reglas reactivas resuelven acciones del catálogo bajo sus restricciones; la verdad es conocida por el planificador exacto si forma parte del estado de simulación, pero no debe confundirse con régimen parcialmente observado de otras rutas. | Resultados de ramas con probabilidades y resultados por periodo. Adaptador S7 genera registros PEF; piloto comprueba agregación exacta. El árbol conserva semántica probabilística que S2a no necesita. |

### 3.1 Diferencias semánticas que debe preservar el contrato

No se debe forzar una única forma de `period`: S2a tiene periodos discretos
sin incertidumbre; S3b tiene selección y feedback por ronda; S4 puede registrar
acciones físicas y estados intertemporales; S7 tiene ramas probabilísticas
exactas. Tampoco se deben colapsar recompensa optimizada, CES, resultado
funcional, producción, costes, competencias latentes y observaciones. Las
trazas pueden ser completas, parciales o deliberadamente omitidas; su
disponibilidad debe declararse, no inferirse del valor cero.

## 4. Contrato mínimo propuesto

Usar **`ExperimentRun` como sobre de una réplica/ejecución** y **`EvaluationProfile`
como declaración de evaluación**. No introducir un segundo objeto `Experiment`.
La identidad del problema y el perfil pueden vivir inicialmente en mapas
`configuration`/`metadata` existentes. Solo promover campos tipados si una
segunda ruta demuestra necesidad recurrente.

### 4.1 Identidad y configuración (A/B)

Campos canónicos recomendados en `ExperimentRun.configuration` y/o metadata,
sin redundancia:

- `scenario_id` y `scenario_configuration_id` (versión física/configuración);
- `organizational_problem_id` (p. ej. selección, matching con restricciones
  declaradas; no usar solo nombre de solver);
- parámetros físicos: estado/condiciones iniciales, demanda, horizonte y
  unidad temporal, capacidades, restricciones y modelo de transición;
- un identificador o digest de configuración serializable.

En el `EvaluationProfile` existente, `scenario_id`, `configuration_id`,
`organizational_problem`, `constraints`, `temporal_horizon`, `demand_distribution_id`
y `aggregation` describen la interpretación evaluativa. La configuración
efectiva del run debe coincidir con el perfil antes de comparar.

### 4.2 Mecanismo e información (C)

`mechanism_id`, `policy_id` y parámetros completos identifican método y
variante. `information_available` describe qué señales puede usar la política;
`observation_model` describe qué se genera y bajo qué condición; separar
ambas cosas evita llamar observación a un dato latente disponible solo al
evaluador. Registrar restricciones de información y estimador/actualización
si son parte de la configuración del mecanismo. No registrar competencias
ocultas en entradas disponibles a la política.

### 4.3 Ejecución, resultados, evaluación y reproducción

- `run_id` debe ser único por réplica; `random_seeds` lista streams y
  propósito. Para ejecución determinista sin azar, declarar vacío explícito
  (`()`); si no se conservó, dejar desconocido (`None`). `software_revision`
  se consigna cuando está disponible, nunca se inventa.
- `events` conserva decisiones, feedback/transiciones y tiempos cuando se
  requieren diagnósticos. `mechanism_results` puede guardar salida fuente
  compacta; no es necesario duplicar cada evento si la fuente ya es auditable.
- `units` solo declara unidades conocidas. `metrics` y los registros PEF
  mantienen definición, unidad, estado y procedencia. Resultados agregados
  históricos se importan como históricos, no como reconstrucción de trazas.
- Un `EvaluationProfile` declara objetivo de decisión por política, métricas
  primarias/secundarias/diagnósticas, régimen informacional, horizonte,
  distribución de demanda, regla de agregación y disponibilidad. El perfil
  no cambia el objetivo que la política optimizó.
- Para diferencias pareadas, guardar la identidad de campaña/replicación y
  semilla en metadatos de run; PEF `compare` no calcula emparejamiento ni
  incertidumbre estadística.

### 4.4 Obligatorio, opcional y condicional

Imprescindible para una comparación reproducible: escenario/configuración,
problema organizativo, política/mecanismo y sus parámetros, objetivo de
decisión, horizonte y semántica de unidad, perfil y definición/unidad de la
métrica, procedencia, y régimen de información. Para resultados estocásticos
también se requiere identidad de réplica y semillas/streams (o una declaración
explícita de que se desconocen); para enumeración exacta, distribución y
probabilidades de las ramas. No toda evaluación necesita evento por evento:
es opcional salvo que una métrica o auditoría lo necesite. Competencias,
requisitos funcionales, recursos, calidad y observaciones son condicionales a
lo que el escenario produce; declarar `NOT_APPLICABLE`, `NOT_OBSERVABLE`,
`NOT_RECORDED` o `UNDEFINED`, en vez de crear valores. Requisitos exactos de
calidad dependen de la aplicación.

## 5. Adecuación de `ExperimentRun` y `EvaluationProfile`

| Necesidad | Soporte actual | Evaluación / mínimo necesario |
|---|---|---|
| Describir una ejecución | `ExperimentRun` reúne identidad, configuración, información, semillas, unidades, eventos y salida. | Adecuado como sobre. Completar metadata con IDs canónicos en adaptadores nuevos; no convertirlo en ejecutor. |
| Identificar escenario y organización | PEF tiene escenario/configuración/problema; el sobre solo tiene configuración/metadata libres. | Falta relación tipada común. Para primer slice basta claves documentadas y validadas en `configuration`/metadata. |
| Identificar mecanismo y parámetros | `mechanism_id`, `policy_id`, `configuration`; mecanismo resultados. | Suficiente si el adaptador serializa parámetros sin pérdidas y fija identidad estable/versionada. |
| Asociar procedencia y resultados | Semillas, revisión, unidades, eventos, métricas y payload de fuente. | Suficiente en principio; ID de réplica explícito en metadata y `run_id` único evitan colapsar réplicas idénticas. |
| Aplicar perfil PEF | `EvaluationProfile` y APIs puras. | Funciona tras traducción a `EvaluationRecord`; run no lleva `profile_id` como campo. Mantener vínculo explícito en resultado/adaptador. |
| Comparar políticas compatibles | PEF verifica varios metadatos y régimen informacional. | Adecuado para compatibilidad semántica básica; no verifica por sí solo el emparejamiento estadístico, ni da IC. No comparar una sola diferencia escalar como prueba de incertidumbre. |
| Representar ausencia | Estado de perfil/campo/resultados y valores no disponibles. | Adecuado; adaptador debe mapear campo ausente con estado significativo. No serializar ausencia como cero. |

No se justifica modificar ahora el esquema versionado. Primera integración
debe comprobar si metadata/maps bastan y producir evidencia de incompatibilidad
real antes de añadir campo nuevo. Riesgos: lectores que asumen contenido
legacy, política de ID, nombres semánticos divergentes y unidades no
declaradas. Mitigar con adaptador nuevo, tests de round-trip y artefacto
separado; no reescribir resultados históricos.

## 6. Compatibilidad y primera ruta: S2a

### S2a es una ruta apropiada, con alcance acotado

S2a ofrece un corte vertical determinista y pequeño fuera de S7: configuración
explícita, cuatro periodos, decisiones exactas/greedy, verificación por
enumeración y regresión conocida. Permite probar traducción de runner→sobre→PEF
sin añadir sorteos, emparejamiento de semillas ni política aprendida. La
comparación exacto/greedy es válida dentro de esta configuración porque
comparten demanda, capacidad, matriz, horizonte, recompensa/unidad; la
enumeración global es verificador, no tercera política desplegada.

Su límite es material: el score de S2a es suma de pesos de asignación y el
“servicio” registrado es conteo de unidades atendidas por tipo, sin requisitos
funcionales de calidad. Por ello, PEF puede evaluar la recompensa original
(8.0 exacto frente a 7.2 greedy). Los conteos de unidades atendidas y uso de
capacidad pueden conservarse como diagnósticos en el sobre o en eventos, con
unidades declaradas; el catálogo PEF actual no tiene una métrica genérica de
cobertura por tipo para calcularlos. No debe fingir que ese conteo equivale a
la tasa PEF de cumplimiento funcional ni inventar producción física, CES,
déficit funcional o esfuerzo. Esas métricas se marcan no aplicables/no
observables según la semántica acordada.

### Otras rutas

- **S3b:** buena validación posterior para feedback selectivo y estimadores,
  pero hay varios protocolos/espacios de acción, potenciales frente a outcomes
  observados, trazas diferentes y emparejamiento por streams. Requiere un
  adaptador que preserve el estimando y el régimen informacional.
- **S4:** relevante para N×K, recursos y dinámica endógena; se deben mantener
  separadas sus variantes de objetivo y dataclasses de simulación/exactas.
  Mayor carga de semántica y unidad que S2a para primera integración.
- **S7:** ya es la ruta de integración de referencia, con árbol exacto,
  probabilidades y adaptador. Repetirla no valida reutilización entre rutas.

S2a es así una primera ruta útil para validar **contrato, adaptador, estados
PEF, procedencia y compatibilidad determinista**. No valida todavía el
tratamiento de incertidumbre estadística, feedback parcial, recursos físicos,
calidad funcional o ejecución temporal estocástica.

## 7. Flujo de integración mínima propuesto

```text
Configuración S2a existente
        ↓ (sin cambio de lógica)
Runner S2a existente
        ↓ resultado fuente + contexto explícito
Adaptador S2a → ExperimentRun + EvaluationRecord
        ↓
EvaluationProfile S2a
        ↓
PerformanceEvaluator → resultados PEF separados y comparables
```

**Reutilizar:** `run_s2a`, `ExperimentRun`, `RunAdapterContext`,
`ExperimentEvent`/`MetricValue`/unidades cuando aplican, `EvaluationProfile`,
`EvaluationRecord`, `PerformanceEvaluator`, serialización y verificaciones de
matching ya existentes.

**Añadir si el PI autoriza Incremento 2:** un adaptador localizado que
consume el resultado retornado (no ejecuta ni altera `run_s2a`), metadata
canónica de problema/perfil y records por periodo. La recompensa original
entra en el catálogo PEF actual; los conteos de unidades/capacidad quedan como
diagnósticos del run, salvo que se autorice y especifique una extensión del
catálogo. Definir si se adapta el diccionario fuente existente o se normaliza
una copia in-memory; preservar intacto el JSON histórico.

**Validar:** claves/IDs presentes; configuración del perfil coincide con
fuente; exacto y greedy se registran como políticas; enumeración como
verificación separada; el objetivo permanece suma de pesos; conteos de
demanda/capacidad conservan unidades como diagnósticos; campos funcionales
ausentes reciben estado; evaluator no llama al runner/solver; comparaciones
rechazan perfiles incompatibles.

El runner sigue siendo dueño de física/decisión, adaptador de traducción y
provenance, sobre común de serialización, y evaluador de métricas. No se
propone plugin system, simulador nuevo, taxonomía ejecutable de B1–B3 ni
orquestador general.

## 8. Pruebas de aceptación del Incremento 2

1. Ejecutar la configuración S2a existente sin cambiar matriz, demanda,
   capacidad, acciones, desempates ni lógica de políticas.
2. Verificar regresión exacta: exacto por periodo/horizonte 8.0, greedy 7.2,
   enumeración global 8.0 y 84,388 secuencias; asignaciones factibles y
   resultados por periodo iguales a fuente. Excluir tiempos de identidad y
   comparación.
3. Adaptar la salida y hacer round-trip estable de `ExperimentRun`; IDs de
   política y réplica no colapsan cuando dos resultados sean iguales.
4. Comprobar que PEF da 8.0 y 7.2 para la métrica original con misma unidad,
   definición, demanda, horizonte y agregación.
5. Comprobar por periodo que unidades atendidas y restantes concuerdan con
   demanda y asignación; conservarlas como diagnósticos de ejecución y no
   llamarlas métricas PEF de éxito funcional si no hay requisitos.
6. Verificar que CES, calidad física, déficit funcional y esfuerzos se
   declaran no aplicables/no observables/no registrados según corresponda,
   nunca cero fabricado.
7. Verificar procedencia de runner, configuración, artefacto fuente, versión
   disponible, contexto determinista y unidades. No alegar semilla aleatoria:
   S2a no usa aleatoriedad (`random_seeds=()` si el contrato lo requiere).
8. Probar que añadir/quitar PEF no cambia asignaciones, estados ni artefacto
   del runner; comparar JSON fuente omitiendo solo campos temporales.
9. Probar rechazo de comparación con configuración, unidad, horizonte,
   objetivo/definición o agregación incompatible.
10. Mantener pruebas existentes del contrato, PEF, S1/S2a; tests adicionales
    deben probar solo adaptador/conversión, no reejecutar campañas.

## 9. Riesgos y decisiones del PI

- **Semántica de demanda/servicio:** decidir si el perfil inicial calcula
  únicamente la recompensa original y conserva conteos como diagnósticos;
  recomendado. El catálogo PEF actual no calcula una métrica de cobertura
  específica para S2a.
- **IDs/configuración:** adoptar claves canónicas en maps primero; evitar una
  migración de schema antes de demostrar que es necesaria.
- **Comparabilidad:** exacto frente a greedy es comparación intrainstancia;
  no inferir generalidad desde la instancia. Estadística pareada no aplica a
  este caso determinista.
- **Procedencia de código:** `software_revision` solo si se obtiene de forma
  fiable; no derivarlo de una rama o fecha declaradas en el documento.
- **Artefactos:** guardar una validación nueva en ruta aparte y preservar
  resultados S2a existentes.
- **Siguiente ruta:** escoger S4 o S3b después del vertical slice según la
  brecha que reste; no se autoriza aquí.

## 10. Decisión de integración

**Recomendación técnica:** usar S2a como primer candidato de Incremento 2,
porque es una ruta comprobable y de baja ambigüedad, siempre que el propósito
se limite a evaluar su recompensa de asignación y conservar sus conteos de
cobertura como diagnósticos del run.
Si el PI requiere métricas de cumplimiento funcional en el primer vertical
slice, S2a no las sustenta y habría que elegir un registro con requisitos
funcionales observables (probablemente una ruta S4); esa elección debe hacerse
antes de implementar. La decisión de implementar Incremento 2 sigue pendiente
de autorización explícita del PI.

## 11. Referencias de código, pruebas y evidencia

- [`experiment_contract.py`](../../src/hls/experiment_contract.py)
- [`performance_evaluation.py`](../../src/hls/performance_evaluation.py)
- [`s7_pef_adapter.py`](../../src/hls/synthetic/s7_pef_adapter.py)
- [`s2a_pef_adapter.py`](../../src/hls/synthetic/s2a_pef_adapter.py)
- [`run_hls_s2a_static_demand.py`](../../experiments/run_hls_s2a_static_demand.py)
- [`run_hls_s2a_pef_integration.py`](../../experiments/run_hls_s2a_pef_integration.py)
- [`run_hls_pef_s7_pilot.py`](../../experiments/run_hls_pef_s7_pilot.py)
- [`test_hls_common_experiment_contract.py`](../../tests/test_hls_common_experiment_contract.py)
- [`test_hls_performance_evaluation.py`](../../tests/test_hls_performance_evaluation.py)
- [`test_hls_lab_nk_assignment.py`](../../tests/test_hls_lab_nk_assignment.py)
- [`test_hls_s2a_pef_integration.py`](../../tests/test_hls_s2a_pef_integration.py)
- [Marco unificado](../architecture/HLS_UNIFIED_FRAMEWORK.md), [ontología](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md), [HLS-PEF](../architecture/HLS_PERFORMANCE_EVALUATION_FRAMEWORK.md) y [roadmap](HLS_LAB_ROADMAP_CURRENT.md).
- Para S3b/S4/S7 y resultados, véanse sus entradas fechadas y vínculos en el [registro acumulativo](HLS_LAB_EXECUTION_PLAN_2026-10-17.md); este informe no reevalúa ni modifica sus artefactos.

## 12. Incremento 2 — implementación y validación

### Arquitectura implementada

```text
run_s2a() existente
       ↓ salida en memoria, sin invocar el bloque que escribe el JSON histórico
adapt_s2a_policy()
       ↓ ExperimentRun + EvaluationRecord por periodo
EvaluationProfile S2a → PerformanceEvaluator
       ↓ resultados PEF + comparación exacto/greedy
results/experiments/hls_s2a_pef_integration/results.json
```

Se reutilizan el runner original y su instancia, `ExperimentRun`,
`RunAdapterContext`, `ExperimentEvent`, `MetricValue`, `UnitDeclaration`,
`EvaluationProfile`, `EvaluationRecord`, `EvaluationResult` y
`PerformanceEvaluator`. El adaptador valida dimensiones, periodos, demanda,
factibilidad, identidad de agentes/tareas, conciliación de conteos y
recomputación de reward desde las parejas asignadas. No toma decisiones ni
resuelve asignaciones. Los resultados agregados PEF se calculan después de
que `run_s2a()` termina.

### Políticas y referencia

`exact` identifica el optimizador bipartito exacto ya usado por el runner;
`greedy` identifica su regla existente de ordenar aristas por score
descendente y desempatar por índices de agente/tarea. Son las dos políticas
comparadas. La enumeración global de secuencias factibles (84,388) conserva
el papel de **referencia de validación de optimalidad**, no se registra como
política ni se incluye en la comparación exacto/greedy.

### Perfil, disponibilidad y procedencia

El perfil `s2a_assignment_reward_v1` usa como métrica primaria
`original_reward_cumulative` y como métrica secundaria el conteo de
asignaciones mediante la métrica PEF existente de uso de recurso, en unidades
de parejas agente-tarea. Los conteos por tipo y las asignaciones quedan como
diagnósticos estructurados en eventos; no se añadió métrica genérica de
cobertura. CES, cumplimiento funcional, déficit y producción física son
`NOT_APPLICABLE` en esta formulación; PEF conserva `value=None`, no cero.
S2a es determinista (`random_seeds=()`), y la revisión de software se deja
desconocida en vez de inferirse. Cada política tiene ID de run distinto,
parámetros/configuración, IDs del perfil/problema, referencia de fuente,
unidades, eventos temporales, métricas y resultado compacto.

El `ExperimentRun` v1 solo tenía serializador. Se añadió `from_dict` /
`from_json` estricto para permitir el round-trip exigido, sin cambiar campos
ni versión del schema; rechaza campos faltantes/desconocidos y versiones no
soportadas.

### Reutilización estructural con S7

La inspección del artefacto guardado corrigió una suposición de la petición:
el piloto S7 original usa `EvaluationProfile`, `EvaluationRecord`,
`EvaluationResult` y `PerformanceEvaluator`, pero **no emitía
`ExperimentRun`**. Para hacer comprobable la compatibilidad común se añadió
`adapt_s7_pilot_artifact_to_experiment_run`, un adaptador downstream que
envuelve registros ya almacenados, valida que las probabilidades sumen uno y
no reejecuta ni modifica S7. La ruta S2a contrasta su perfil/records/run con
las clases comunes y reevalúa registros archivados de S7 con el mismo PEF;
CES ponderado coincide con el agregado histórico. Esta comprobación no hace
que el runner S7 original produzca nativamente el sobre.

### Regresión, comparación y artefacto

Ejecución fresca de la función `run_s2a()` del runner original:

| Rol | Recompensa acumulada | Representación |
|---|---:|---|
| Asignación exacta | 8.0 | política ejecutable |
| Greedy | 7.2 | política ejecutable |
| Enumeración global | 8.0 | referencia exhaustiva, no política |

La enumeración examinó 84,388 secuencias. PEF reproduce 8.0 y 7.2 con
`declared_reward`; diferencia exacto−greedy = 0.8 en la instancia. No es una
afirmación general de superioridad. Las decisiones y diagnósticos por periodo
se conservaron en el nuevo resultado; los tiempos variables se excluyeron.
El artefacto fuente S2a y el artefacto histórico S7 no se sobrescribieron.
El nuevo resultado resumido queda en
[`results/experiments/hls_s2a_pef_integration/results.json`](../../results/experiments/hls_s2a_pef_integration/results.json).

### Pruebas y criterios C1–C10

Pruebas nuevas en `tests/test_hls_s2a_pef_integration.py` verifican valores
del runner original, configuración/demandas y factibilidad, round-trip de
`ExperimentRun`, comparación compatible e incompatible, perfil y estados PEF,
entradas incompletas/malformadas, pureza de adaptación/evaluación,
determinismo, papel de la enumeración y compatibilidad S2a/S7. La suite usa el
artefacto S7 ya guardado para no relanzar ese simulador.

| Criterio | Estado | Alcance |
|---|---|---|
| C1–C2: ejecutar el runner original y reproducir resultados | **Cumplido** | 8.0 / 7.2 / 8.0; 84,388 secuencias |
| C3–C4: `ExperimentRun` y `EvaluationProfile` válidos | **Cumplido** | Dos runs S2a; perfil registrado y reusado |
| C5–C6: evaluación PEF y disponibilidad honesta | **Cumplido** | Reward/count; físicas ausentes `NOT_APPLICABLE` |
| C7: comparación compatible | **Cumplido** | Exacto−greedy = 0.8, misma instancia y semántica |
| C8: pruebas automatizadas | **Cumplido** | 13 pruebas específicas; además, contrato/PEF/asignación y S7 |
| C9: reutilización estructural con S7 | **Cumplido con límite** | Mismas clases PEF; run S7 se adapta del artefacto existente, no del runner original |
| C10: documentación/roadmap | **Cumplido** | Registro y roadmap actualizados |

**Validación ejecutada:** 13 pruebas específicas S2a/contrato/PEF y
compatibilidad; una suite de 41 pruebas de integración S2a + contrato + PEF +
asignación; y una suite focalizada de 31 pruebas S7 que incluía esas mismas
pruebas estructurales. Las invocaciones se solapan y sus conteos no se suman.
El runner generó el nuevo artefacto de forma determinista. No se ejecutaron
otras campañas.

### Límites y siguiente incremento

La ruta valida un caso discreto, determinista y pequeño; no valida ejecución
estocástica, emparejamiento inferencial, aprendizaje, feedback parcial ni
escalabilidad. Los diagnósticos de cobertura no son métricas PEF nuevas. El
adaptador S7 a `ExperimentRun` consume un artefacto existente; integrar el
emisor del sobre en el runner S7 requeriría trabajo posterior y no era
necesario para esta prueba estructural. La siguiente recomendación de
ingeniería es un adaptador fino para una ruta N×K de S4 que conserve
explícitamente producción, requisitos y recursos, si el PI autoriza esa
validación. No se ha iniciado.

## Hito 2.2 — Integración operativa S4 N×K (23 Oct 2026)

El PI autorizó la ruta acotada propuesta en la auditoría Hito 2.1. Se añadió
`src/hls/synthetic/s4_pef_adapter.py`, que consume `ExactResult` producido por
el solver existente y crea, sin decidir ni reejecutar física, un
`ExperimentRun` v1 y tres eventos por periodo (decisión, transición física,
ejecución), más `EvaluationRecord` con output, requisitos, éxito, déficit,
recompensa, estados de competencia, MIS-v2, transferencia y recursos. La
procedencia apunta al resultado del runner nuevo. La configuración declara
estado real completo, secuencia de demanda conocida, determinismo y ausencia
de semillas aleatorias. El artefacto guarda revisión Git base, estado del
árbol y hashes de solver/adaptador/runner; si hay cambios locales, el
`software_revision` exacto queda desconocido en vez de atribuir todo al
commit base.

El runner `experiments/run_hls_s4_pef_integration.py` llama a la fábrica y
solver de `run_hls_s4_transfer_exact.py` para A/B, hace round-trip JSON y
evalúa los mismos registros bajo dos perfiles. El perfil colectivo básico
selecciona reward/CES, producción, éxito funcional y déficit. El perfil
ampliado añade esfuerzo productivo, esfuerzo docente `h`, recurso docente
`2h`, recurso total y número de acciones docentes. Los perfiles comparten
semántica, horizonte, agregación y régimen informacional; solo cambia la
selección de métricas/diagnósticos. No se añadió métrica ni campo al contrato.

La integración se ejecuta con:

```bash
PYTHONPATH=src:. python experiments/run_hls_s4_pef_integration.py
```

El nuevo artefacto es
[`results/experiments/hls_s4_pef_integration/results.json`](../../results/experiments/hls_s4_pef_integration/results.json).
Reproduce A=B=`1.9175000000000004`, éxito funcional `1/3`, déficit
acumulado `.5325`, esfuerzo productivo `6`, esfuerzo docente `0`, recurso
docente `0` y total `6`; A y B no seleccionan transferencia. La diferencia
PEF A−B de reward es `0` dentro de `1e-12`. Que producción y CES también
coincidan numéricamente es una propiedad de esta instancia, no una equivalencia
semántica. Los dos perfiles consumen el mismo run y records; la prueba de
invariancia verifica que evaluación no muta decisiones, estados o resultados.

La prueba de reutilización usa las clases comunes para S2a, S4 y S7, y evalúa
cada escenario con su propio perfil. S2a conserva sus físicas como
`NOT_APPLICABLE`; su runner determinista se invoca en memoria para producir
records completos. S7 se rehidrata desde el árbol archivado y reevalúa sus
16 ramas probabilísticas. No se comparan magnitudes heterogéneas entre
escenarios ni se sobrescriben los artefactos históricos.

**Alcance:** queda validada una tercera familia semántica mediante una
referencia determinista de estado completo. No se valida S4 P0/P1/P2 con
observación parcial ni el efecto de transferencia efectiva: el óptimo B
declara transferencia opcional pero no elige ninguna lección. La integración
tampoco es un runner universal. Pruebas nuevas: 15 específicas de integración
S4; la suite conjunta de regresión se registra en la entrada cronológica
Hito 2.2 del plan acumulativo.
