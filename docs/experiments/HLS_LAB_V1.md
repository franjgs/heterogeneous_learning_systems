# HLS Laboratory v1

**Estado del hito: APPROVED — IMPLEMENTATION PARTIAL (decisión 2026-10-15; última actualización documental 2026-10-15 20:31 +02:00, Europe/Madrid).** La capa integrada B1–B6 y el entorno exógeno están publicados en `37a011804f9ea013fc3a5436c00a72eb0b8280da`. Las pruebas focalizadas pasan; la suite completa conserva 13 fallos de integridad/procedencia preexistentes, por lo que la aceptación final permanece abierta. El hito activo es **HLS-LAB-V1-INTEGRATED**. Esta guía es la referencia técnica de implementación, enlaza la [decisión operativa vigente](../HLS_CURRENT_STATE.md) y no sustituye los [contratos científicos de referencia](HLS_LAB_V1_SCIENTIFIC_CONTRACTS.md).

La evidencia científica posterior de Campaign 1 y de plausibilidad conductual
está consolidada en [HLS_CAMPAIGN1_FINDINGS.md](HLS_CAMPAIGN1_FINDINGS.md).
Ese informe documenta los resultados publicados sin cambiar la física ni
cerrar el estado **PARTIAL** del hito; sus hipótesis no deben confundirse con
hallazgos verificados.

## Hito activo: HLS-LAB-V1-INTEGRATED

El objetivo aprobado es un ejecutor integrado y reproducible de episodios
multiperiodo donde agentes heterogéneos producen, aprenden por experiencia,
enseñan a otros agentes y adaptan decisiones a partir de observaciones. La
completitud funcional precede al perfeccionamiento de mecanismos individuales;
los modelos iniciales pueden ser sencillos, pero han de ser coherentes,
verificables y sustituibles. HLS no se reduce a formación de trabajadores:
la enseñanza es una de varias acciones posibles de desarrollo de capacidades.

La implementación de este único hito se verifica en seis bloques:

| Bloque | Contenido que debe integrarse |
| --- | --- |
| B1 | Acción conjunta y recursos compartidos entre producción y enseñanza. |
| B2 | Transición formativa explícita con participación de instructor y aprendiz. |
| B3 | Observaciones formativas configurables y estimación organizativa elemental. |
| B4 | Política adaptativa mínima que pueda usar lo observado y decidir no enseñar. |
| B5 | Ejecución integrada multiperiodo con capacidades persistentes y consecuencias futuras. |
| B6 | Pruebas de invariantes y demostración reproducible de extremo a extremo. |

**Aceptación del hito:** ejecutor reproducible; contrato común de acciones y
presupuesto compartido operativo; aprendizaje individual y transición de
enseñanza funcionales y distinguibles; separación del estado real y observado;
actualización organizativa elemental; al menos una política adaptativa, una
referencia sin enseñanza y una política con enseñanza; comparaciones bajo
condiciones reproducibles; pruebas automáticas de los invariantes; y una demo
que muestre condiciones donde enseñar conviene y donde no conviene, sin forzar
la superioridad de una estrategia. El hito no se marcará DONE hasta verificar
todos estos criterios.

**Invariantes:** enseñar consume recursos que podrían producir; instructor y
aprendiz participan realmente; enseñar puede cambiar competencias futuras,
pero no garantiza mejor rendimiento; producción y mecanismos formativos
compiten por recursos; políticas no acceden a estado privado; las
observaciones pueden afectar decisiones posteriores; la evaluación funcional
no otorga recompensas arbitrarias por enseñar; y desactivar los mecanismos
nuevos preserva el comportamiento histórico bajo un contrato explícito de
compatibilidad. Los modelos G1, G2, MIS, G3-H, RQ0 y resultados congelados no
se alteran.

Se permiten como simplificaciones explícitas y sustituibles: dos dimensiones
de competencia, colectivos pequeños, generadores existentes, MIS-v2,
máximo un evento de enseñanza por periodo, eficacia docente fija y
heterogénea, transiciones formativas simples, ruido configurable, estimadores
elementales, heurísticas y horizontes cortos. No se describen como
empíricamente validadas sin evidencia.

**Fuera de alcance de este hito:** optimizadores generales, POMDP completos,
RL profundo, FAST/DEEP, META-VOC, redes complejas de cooperación, modelos
avanzados de enseñanza, estimadores sofisticados, campañas extensas, revisión
nueva de novedad, rediseño de MIS-v2 o reescritura del laboratorio. El trabajo
de desarrollo se concentra en B1–B6; bloqueos estructurales se registran en
los documentos operativos existentes y se elevan al CE. No se abrirán fases
intermedias de auditoría ni nuevos documentos de estado/roadmap sin necesidad
justificada y autorización.

**Próxima acción:** cerrar la verificación integral y resolver/disponer los
fallos de integridad preexistentes antes de considerar completado B1–B6; no
iniciar una campaña científica en esta etapa de infraestructura. La
recomendación CE-25 de priorizar FAST/DEEP es una recomendación histórica,
superada como siguiente prioridad por la decisión del 15 de octubre; el
resultado y su interpretación original se conservan en [CE-25](HLS_LAB_CE25.md).

## Registro de integración B1–B6 — 15 octubre 2026

Implementación aditiva en `src/hls/hls_lab_v1_integrated.py`; no se modifican
`hls_lab_v1.py`, DISCOVER-v0, MIS-v2 ni los ejecutores/resultados históricos.
El contrato heredado de decisión productiva `H=1` por problema se conserva;
el ejecutor integrado encadena problemas como periodos, por lo que permite
consecuencias entre periodos sin introducir decisiones internas adicionales.

- **B1, acción y recursos:** `IntegratedAction` combina una acción del catálogo
  productivo congelado con cero o una `TeachingEvent(instructor, learner,
  capability, effort)`. El instructor y aprendiz deben ser distintos. La
  factibilidad exige simultáneamente `production effort + 2 × teaching effort
  ≤ resource_budget` y, para cada persona, su esfuerzo productivo más su
  participación formativa `≤ max_effort_per_expert`. No se añade penalización
  por enseñar: se registra `resource_cost = total_resource_used ×
  resource_cost_per_unit`. La granularidad discreta de `JOINT_ACTIONS` puede
  dejar parte de la capacidad residual inutilizable durante la enseñanza; se
  conserva deliberadamente el catálogo existente.
- **B2, transición:** después de la producción y MIS-v2, solo el aprendiz
  recibe `c' = min(1, c + transfer_rate × teaching_effort × efficacy[i,j,k]
  × (1-c))`. La eficacia es fija, privada y heterogénea por relación dirigida
  y competencia. Es una simplificación de infraestructura, no una ley docente
  validada empíricamente.
- **B3, observación:** las lecturas productivas son `y_ik = x_ik c_ik +
  Normal(0, σ_prod²)` con innovaciones indexadas por semilla/periodo/agente/
  competencia. Una posterior de malla reutiliza las utilidades de
  `hls_lab_dynamic.py` y predice MIS-v2 con parámetros públicos. El resultado
  formativo observado es el incremento del aprendiz más ruido independiente;
  la organización actualiza una media recursiva de eficacia tras normalizar
  esa señal usando su competencia estimada. El incremento real se conserva
  solo como diagnóstico de la traza y nunca se entrega a la política.
- **B4, políticas comunes:** P0 maximiza el criterio funcional entre acciones
  sin enseñanza; P1 intenta una relación instructor-aprendiz-competencia
  preespecificada y recurre a P0 si no es factible; P2 explora una vez cada
  relación configurada que resulte elegible, en orden predefinido, después usa
  la eficacia observada, su umbral y una competencia objetivo. P2 no enseña si
  la mejor acción productiva ya satisface el problema. Son reglas heurísticas deterministas,
  no optimizadores.
- **B5, ejecución:** `run_integrated_sequence` usa el orden producción →
  observación productiva → MIS-v2 individual → enseñanza → observación
  formativa/actualización organizativa → traza. Los estados reales,
  posteriores de competencia y memoria de eficacia evolucionan por ejecución;
  `compare_integrated_policies` vuelve a inicializar cada organización desde
  el mismo equipo y conserva idéntica secuencia e innovaciones indexadas.
  `serialize_integrated_result` genera JSON estable.
- **B6, evidencia de ingeniería:** `tests/test_hls_lab_v1_integrated.py`
  cubre presupuesto y esfuerzo compartidos, desplazamiento productivo,
  transición docente separada de MIS, uso de observaciones por P2, opción de
  no enseñar, ausencia de acceso de política al estado privado, CRN por
  coordenadas, evolución independiente de los estados y reproducibilidad.
  Los tests integrados con CE-23/24/25, dinámica, DISCOVER-v0, MIS-v2 y Small
  Problem World: **87 passed**. La suite completa: **1181 passed, 13 failed**.
  Los fallos corresponden a hashes de fuentes ya modificadas localmente antes
  de esta intervención, artefactos preexistentes adicionales y procedencia
  congelada de Campaign 2/B2.3/RQ0; no modificamos esos paths ni actualizamos
  sus hashes. Por este motivo el hito queda **PARTIAL**, no DONE.

La demostración reproducible se ejecuta con:

```bash
PYTHONPATH=src:. python experiments/synthetic/hls_lab_v1/integrated_demo.py
PYTHONPATH=src:. pytest -q tests/test_hls_lab_v1_integrated.py
```

Es un fixture de ingeniería determinista, no un experimento científico. En
`A_LONG_RECURRENT_DEMAND` (34 periodos), P0 obtuvo recompensa CES acumulada
5.0728 y 2 éxitos funcionales; P2 obtuvo 6.4564 y 33 éxitos, con una lección.
P1 obtuvo 10.8367 y 33 éxitos, pero enseñó en los 34 periodos y no es una
política adaptativa. En `B_SHORT_MISMATCHED_DEMAND` (4 periodos), P0 obtuvo
2.1997 y 4 éxitos; P1 obtuvo 1.5763 y 0 éxitos al enseñar persistentemente
una relación irrelevante; P2 obtuvo 2.1997 y 4 éxitos, eligiendo no enseñar.
Las cifras ilustran que la regla puede producir ambos signos y declinar la
enseñanza bajo el fixture; no estiman efectos generales.

## Fundamento y objetivo

La pregunta que habilita esta versión es cómo interactúan (i) la complementariedad funcional bajo recursos comunes, (ii) el aprendizaje individual por exposición y (iii) el aprendizaje persistente de una regla organizativa al resolver problemas sucesivos. El laboratorio separa tres objetos: una especificación exógena del problema, el estado real/estimado y experiencia de cada experto, y la política más su estado organizativo. No equipara producción CES con éxito funcional, producción individual con competencia, adaptación a la vista actual con aprendizaje de la política, ni una demostración determinista con evidencia experimental.

Esta entrega es una primera ensambladura ejecutable con un paso de decisión por problema (`H=1`) y tres expertos de dos competencias. Su demostración es un fixture reproducible de ingeniería; no estima prevalencias, efectos causales, robustez poblacional ni parámetros de aprendizaje.

## Contratos ejecutables

### Problema

`ProblemSpec` (`src/hls/hls_lab_v1.py`) declara `problem_id`, requisitos no negativos `r=(r1,r2)`, presupuesto total `B`, esfuerzo máximo por experto, `H=1`, catálogo opcional de acciones permitidas y coste explícito por unidad de recurso. La dificultad operacional es `rho=r1+r2`; la orientación es `r/rho`. Son atributos declarados del problema, no se infieren de la recompensa CES ni del equipo. Los requisitos cero son válidos si al menos una dimensión tiene requisito positivo.

Las acciones se obtienen del catálogo congelado `JOINT_ACTIONS` de `src/hls/discover_v0.py` y se filtran por presupuesto y cap individual. La producción reutilizada es:

\[
Y_k=\sum_{i=1}^{3} x_{ik}s_{ik}, \qquad \sum_{i,k}x_{ik}\le B.
\]

`evaluate_problem` es un observador funcional independiente. El éxito requiere `Y_k >= r_k` en cada dimensión activa (tolerancia numérica `1e-12`); el déficit por dimensión es `max(0,r_k-Y_k)`; el déficit normalizado es la suma de los cocientes déficit/requisito para requisitos positivos; y el margen es el mínimo `Y_k-r_k` entre esas dimensiones. Los requisitos cero se omiten de déficit normalizado y margen. El recurso usado (`effort`) y el coste explícito (`effort × resource_cost_per_unit`) se registran por separado. El coste predeterminado es cero: esfuerzo no se presenta como coste monetario.

`complementarity_class` compara factibilidad del equipo frente a cada experto individual con el mismo presupuesto total y el mismo límite individual. `team_only` es una etiqueta operacional de factibilidad restringida, no superaditividad ni emergencia.

### Experto

`ExpertState` almacena competencia real, estimada, experiencia acumulada y rendimiento atribuible. El control v1 inicializa `ŝ=s` y la mantiene igual a la competencia real después de MIS-v2: es conocimiento perfecto declarado, no inferencia implementada. Antes de la transición, `y_ik=x_ik s_ik` y el total `Y` se calculan con `production_inputs`. Con aprendizaje individual activo, cada competencia cambia por la transición MIS-v2 existente importada de `src/hls/discover_develop_v2.py`:

\[
s_{ik}^{t+1}=1-(1-s_{ik}^{t})\exp(-\lambda x_{ik}^{t}),\qquad
e_{ik}^{t+1}=e_{ik}^{t}+x_{ik}^{t}.
\]

Al desactivar aprendizaje individual, `s` queda constante; la exposición sigue registrándose. No se modifica ni se recalibra MIS-v2. La demostración usa `eta=0.35`, valor heredado como referencia del ejecutor Campaign 0, no calibrado para esta v1.

### Organización

La interfaz recibe una `DecisionView` predecisional con tipo/ID del problema, requisitos, dificultad/orientación, presupuesto, competencias estimadas y acciones factibles. No expone competencia real, resultados futuros ni estado futuro.

- `FixedRouting`: tabla fija `problem_id → acción conjunta`; no se actualiza durante la secuencia.
- `GreedyAdaptive`: regla determinista preespecificada que responde a `ŝ` y requisitos actuales (prioriza éxito, menor déficit, mayor margen y menor esfuerzo, con desempate por orden del catálogo). Su estado `θ` es inmutable; variar la acción entre estados es adaptación, no aprendizaje.
- `ExploreThenGreedy`: regla tabular estándar de explorar cada acción disponible una vez por contexto `problem_id` y luego elegir la de mayor media empírica de éxito; los empates siguen el orden del catálogo. `θ` guarda conteo y media muestral por (contexto, acción). No se presenta como algoritmo novedoso ni se afirma generalización a contextos/equipos no vistos.

La actualización organizativa usa el éxito binario observado después de la acción. El interruptor LO impide cambiar `θ`; LI controla MIS-v2 de forma independiente. La comparación entre clases organizativas es una comparación de paquetes; no aísla por sí sola un efecto causal único.

## Arquitectura y reutilización

- `src/hls/hls_lab_v1.py`: ensamblaje v1 nuevo: contratos, filtrado de acciones por recursos, evaluación funcional, clasificadores de factibilidad, organizaciones, motor de secuencia, trazas, serialización determinista JSON y entrada explícita `initial_organization_state` para congelar/reutilizar θ entre TRAIN/EVAL.
- `src/hls/discover_v0.py`: fuente de `JOINT_ACTIONS`, validación de estado/acción y producción lineal `production_inputs`; no se modifica.
- `src/hls/discover_develop_v2.py`: transición MIS-v2 reutilizada; no se modifica.
- `experiments/synthetic/hls_lab_v1/demo.py`: demostración pequeña fija y determinista; no ejecuta factoriales.
- `experiments/synthetic/hls_lab_v1/ce24.py`: microexperimento TRAIN/EVAL finito, export create-only y comparación de orden predefinida.
- `experiments/synthetic/hls_lab_v1/ce25.py`: experimento mecanístico CE-25 con TRAIN/EVAL emparejado, controles de memoria/feedback, catálogo completo filtrado, horizontes y órdenes predefinidos; resultados en `results/experiments/hls_lab_ce25/`.
- `tests/test_hls_lab_v1.py`: fixtures analíticos P1–P9.
- `tests/test_hls_lab_v1_ce24.py`: validación de dominio, persistencia, congelación, baselines, integridad/reproducibilidad de export.

Small Problem World / `functional_problem.py` no se altera: su observador histórico exige requisitos estrictamente positivos y sus secuencias tienen otro contrato temporal, por lo que esta capa v1 admite cero en una dimensión y exactamente una decisión por problema sin modificar su API. `finite_problem_belief.py` queda fuera: sus creencias sobre identidad de problema no son el contrato de estimación de competencia de esta v1. G3/G3-H aportan precedentes de asignación, pero no se copian sus reglas/objetivos; G0/C1 y Configuration × Environment v0/v0.1 permanecen intactos. CE-16 inspira trazabilidad por decisión, no transfiere sus definiciones de cumplimiento ni sus resultados. No se cambia documentación de resultados históricos.

## Variables y controles

Cada `EpisodeRecord` contiene semilla e índice, problema/requisitos/dificultad/orientación/presupuesto, competencias reales y estimadas antes/después, experiencia antes/después, acción y su ID en el catálogo, producción individual y colectiva, éxito/déficit/margen, esfuerzo/coste, valores organizativos `θ` antes/después, si se actualizó `θ`, cambio de acción, recompensa organizativa y acumulados. `serialize_episode_records` produce JSON compacto con orden estable; representa entradas tabulares mediante contexto y `action_id`, evitando claves tuple no portables.

Los factores controlables son LI y LO; se mantienen fijos equipo inicial, secuencia, problemas, recursos, información, horizonte y semilla dentro de cada comparación. El rendimiento individual se registra antes del cambio de competencia. La recompensa organizativa es el éxito binario. No hay coste computacional, incertidumbre de estimación, aprendizaje de la política individual ni inferencia bayesiana en esta v1.

## Instalación y ejecución

Desde la raíz del repositorio, con el entorno Python del proyecto instalado (Python `>=3.10`, dependencias base del proyecto y `pytest` para desarrollo):

```bash
python -m pip install -e '.[dev]'
PYTHONPATH=src:. pytest -q tests/test_hls_lab_v1.py
PYTHONPATH=src:. python experiments/synthetic/hls_lab_v1/demo.py
```

La demo imprime un resumen determinista, no crea artefactos de resultados y no se debe tratar como ejecución científica. Cambiar secuencia, equipo, `eta` o semilla constituye una nueva ejecución de usuario y debe registrarse fuera de esta demostración si se usa para investigación.

## Pruebas de aceptación y resultado

Las primeras nueve pruebas de `tests/test_hls_lab_v1.py` corresponden a P1–P9 del contrato; se añadieron tres pruebas de persistencia TRAIN/EVAL, inmutabilidad de θ con LO=OFF y semilla como metadato. `tests/test_hls_lab_v1_ce24.py` valida dominio, acciones exhaustivas, evaluación congelada, referencias y export.

La ejecución de regresión previa a CE-24 registró 91 pruebas superadas; esta iteración ampliada y repetida se informa en el reporte [CE-24](HLS_LAB_CE24.md). Son verificaciones de software más un microexperimento determinista; no validan prevalencias, efectos poblacionales ni desempeño en equipos reales.

## Trazabilidad CE-01–CE-21

La v1 responde al encargo de ensamblaje CE-23 y su contrato científico CE-22. Reutiliza de modo acotado componentes cuya semántica ya aparece en el laboratorio: producción/acciones DISCOVER-v0, transición MIS-v2 y patrones de instrumentación CE-16. Conserva deliberadamente la evidencia y los contratos de CE-01–CE-21: no reejecuta ni edita C0–C4, G0/C1, CE-16, FAST/DEEP/META-VOC, predictor-validity, ni los protocolos y resultados congelados. Los comparadores de organización de G0/C1 tampoco se redefinen. Esta implementación no reivindica resolver limitaciones científicas identificadas en esos trabajos ni hereda sus conclusiones.

SHA-256 del documento de contrato descargado al incorporar CE-23: `2ac24be1bd19f92d5d4d28e8501e6b885ef8483e83c1c066436c1319eb941349`. Hashes de las fuentes reutilizadas, verificados durante esta entrega: `discover_v0.py` `ef1eee85cf7735107e46e285af4ce2734906a55a6741ec09a72a2623c1ab470f`; `discover_develop_v2.py` `06d70479a1f8e5bd7408a3a3c5596de4fca9e139838441f5de7dbb78c32e4e80`. Son identificadores de contenido de esta revisión local, no garantías sobre otros commits.

## Limitaciones y trabajo pendiente

Las limitaciones históricas siguientes describen el alcance de CE-23–25; la
prioridad para resolver las carencias necesarias para completar la integración
queda ordenada por el hito activo anterior. En particular, las antiguas
recomendaciones de congelar un factorial o avanzar a FAST/DEEP no gobiernan el
orden operativo actual.

- Es una vertical slice más ejecutores finitos CE-24/25; no hay un framework general de campañas ni dominio de problemas calibrado empíricamente.
- Una decisión por problema limita preguntas temporales dentro del episodio; solo hay aprendizaje entre problemas.
- Competencia estimada igual a real elimina incertidumbre de competencia; no hay creencias ni estado informativo imperfecto.
- Producción aditiva y catálogo discreto reutilizado no representan sinergias/interdependencias más ricas.
- La transición MIS-v2 se reutiliza tal cual; `eta` no está calibrada empíricamente y no debe interpretarse como tasa real de aprendizaje.
- El learner tabular explora acciones en orden y usa problema ID como contexto; no generaliza automáticamente y puede recibir recompensas no estacionarias si LI está activo.
- El clasificador `team_only` mide factibilidad bajo restricciones compartidas, no una ventaja de producción superaditiva.
- El coste monetario/computacional es solo un campo explícito; la demo usa coste por unidad cero. No existe modelo de coste estimado.
- Antes de cualquier factorial: congelar protocolo/dominio/seeds, definir cómo se comparan learning on/off bajo no estacionariedad y revisar que el muestreo no esté saturado. No ejecutar esa fase como parte de CE-23.

CE-25 valida de forma acotada que la experiencia exploratoria emparejada puede ser usada para cambiar decisiones, y que la memoria no consultada no altera el comportamiento; véase [el informe CE-25](HLS_LAB_CE25.md). No demuestra generalización ni una ventaja poblacional.

La clase de entrega sigue siendo **PARTIAL**, no COMPLETE: el ensamblaje, demo, pruebas contractuales y validaciones mecanísticas finitas existen; una evaluación científica amplia queda fuera de alcance.

## Entorno exógeno y trayectoria congelada

La corrección de organización/entorno añade `src/hls/hls_lab_v1_environment.py` sin reemplazar los mecanismos integrados. `ExogenousEnvironmentConfig` fija un proceso de demanda C5, una distribución emisora `DemandRegime` por estado, horizonte y presupuesto. `generate_environment_trajectory(config, seed=...)` genera primero una secuencia inmutable de `IntegratedProblem`; esa misma tupla se entrega después a P0/P1/P2. El generador no recibe equipo, competencias, política, acciones, recompensas ni estado organizativo. La trayectoria guarda los estados latentes solo para diagnóstico experimental; estos no aparecen en `IntegratedDecisionView`.

La implementación reutiliza los procesos `StationaryTaskDemand`, `NonStationaryTaskDemand` y `MarkovTaskDemand` de `src/hls/synthetic/c5.py`, más `DemandRegime`/`generate_problems` de `src/hls/hls_lab_dynamic.py`. Los flujos aleatorios de la dinámica y de la emisión están separados; la emisión se deriva de semilla y periodo, no del consumo de aleatoriedad de las políticas. El estado latente no se pasa a la política, aunque el problema emitido puede revelar información sobre él a través de sus requisitos observados. No se cambian `finite_problem_belief.py`, DISCOVER ni los contratos históricos.

Las familias se definen estructuralmente, no por etiquetas: especialización usa requisitos dominantes en una dimensión; complementariedad usa requisitos positivos simultáneos que no satisface una producción individual aislada, aunque sí una asignación colectiva; recurrencia se representa por transiciones de demanda que retienen tipos; novedad por la primera aparición de un vector de requisitos ausente del prefijo; y cambio de régimen por una transición latente cuya distribución emisora cambia los requisitos. Son capacidades de configuración y prueba del entorno, no afirmaciones sobre distribuciones reales.

Demo reproducible: `python experiments/synthetic/hls_lab_v1/environment_demo.py`. Genera un cambio determinista de demanda especializada a complementaria y compara P0/P1/P2 sobre la misma trayectoria. En la ejecución verificada, P0 obtuvo 12/12 éxitos y CES acumulado 11.14847; P1, que enseñó en 12 periodos, obtuvo 1/12 y CES 3.42640; P2 decidió no enseñar, obtuvo 12/12 y 11.14847. Es un resultado de una fixture determinista: comprueba que se representa una decisión formativa perjudicial y una política puede abstenerse, no es evidencia general sobre políticas. El JSON se imprime en stdout; no crea ni sobrescribe resultados. Pruebas: `PYTHONPATH=.:src pytest -q tests/test_hls_lab_v1_environment.py tests/test_hls_lab_v1_integrated.py`.

**Verificación de esta corrección (2026-10-15 09:57 +02:00):** 17 pruebas focalizadas superadas. La suite completa: 1189 passed, 13 failed en 314.78 s. Los 13 fallos coinciden por nombre y familia con las corridas anteriores: 1 inventario local de resultados de fundamentos; 5 validaciones de procedencia B2.3/RQ0; 7 verificaciones de hashes/artefactos congelados de Campaign 2/3 y Gate. No se actualizaron hashes ni se tocaron las fuentes congeladas durante esta intervención. **Publicación:** commit `37a011804f9ea013fc3a5436c00a72eb0b8280da`, push verificado en `origin/feature/hls-laboratory-v1` a las 09:58 +02:00. **Cierre:** el hito sigue PARTIAL, no DONE; la publicación no resuelve los 13 fallos de procedencia/integridad.

## Validación de plausibilidad conductual — 15 octubre 2026

Ejecución registrada por el manifiesto: **2026-10-15 17:42:56 +02:00**;
documentación actualizada a las **17:43 +02:00** (Europe/Madrid).

**Alcance:** comprobaciones matemáticas y seis fixtures deterministas; no se
añadieron políticas ni se cambió la física. Ejecución:
`python experiments/synthetic/hls_lab_v1/behavioral_plausibility.py`.
Resultados reproducibles y manifiesto con hashes en
`results/diagnostics/hls_behavioral_plausibility/`.

| Propiedad | Comportamiento esperado | Observación | Clasificación | Evidencia |
| --- | --- | --- | --- | --- |
| P1–P2, producción y especialización | Más competencia relevante no reduce `Y_k`; problema especializado favorece esa competencia | Confirmado por producción `Σ x_ik s_ik` y enumeración de las acciones factibles | Invariante matemática | `tests/test_hls_behavioral_plausibility.py` |
| P3–P4, complementariedad/requisito esencial | Una tarea con dos requisitos puede exigir aportes de más de un experto; omitir dimensión esencial impide éxito | Equipo complementario cumple `(0.8,0.8)` con acción conjunta; ninguna contribución unidimensional basta | Condicional al umbral y catálogo, no sinergia productiva | Test nuevo y `tests/test_hls_lab_v1_environment.py` |
| P5, ampliar recursos | No reduce el mejor valor alcanzable si se conserva el catálogo original | Verificado como inclusión de conjuntos factibles | Invariante matemática | Test nuevo |
| Contabilidad de recursos | Presupuesto común = producción + dos participaciones de enseñanza; informar residuo | Con `B=2`, enseñanza `.5`, producción `1`, residual `.5`; máximo productivo sin enseñar `2`, desplazamiento `1` | Catálogo discreto intencional; limitación de granularidad, no defecto | Test nuevo; `enumerate_feasible_integrated_actions` |
| L1–L5, MIS-v2 | Exposición mejora la celda ejercitada con rendimientos decrecientes y cotas; sin aprendizaje no cambia | Ecuación reproducida (`.4→.52→.616`, `eta=.2`); otras celdas intactas y límites respetados | Invariante del modelo MIS-v2 | Test nuevo; `mis_v2_transition` |
| T1–T7, enseñanza | Efecto dirigido y dependiente de relación, monótono en eficacia, nulo con eficacia cero, acotado; consume esfuerzo y distinguible de MIS | Todas las condiciones ejecutadas; el efecto directo se separa del cambio MIS del agente productivo | Invariante condicional a la transición codificada | Test nuevo; transición en `run_integrated_sequence` |
| E1–E6, entorno | Orientación especializada, emisión complementaria, recurrencia, novedad, cambio de régimen y exogeneidad | Verificado por la suite de entorno; se añadió control de novedad con suma de requisitos constante | Contrato de generador | `tests/test_hls_lab_v1_environment.py` y test nuevo |
| S1, equipo suficiente | Enseñar añade poco valor; política puede abstenerse | P2 elige no enseñar; intervención forzada `ΔCES_H=−0.4002` (H=24) | Resultado de fixture | CSV de resumen y trayectoria |
| S2, déficit persistente/enseñanza eficaz | Puede haber coste inicial y retorno posterior | `ΔCES_0=−0.9000`, ganancia directa `0.1275`; cruza break-even en periodo 12; `ΔCES_H=+0.8825` (H=24) | Expectativa condicional observada | CSV de trayectoria |
| S3–S4, horizonte corto/eficacia débil | Coste docente puede no amortizarse | `ΔCES_H=−0.3575` (H=8) y `−0.9000` (H=24), respectivamente | Expectativa condicional observada | CSV de resumen |
| S5–S6, MIS y cambio de régimen | El aprendizaje individual y la demanda pueden cambiar valor relativo de la enseñanza | MIS ON: `ΔCES_H=+2.4445`, break-even periodo 10; al cambiar demanda: `−0.0475`, frente a `+0.8825` sin cambio | Interacciones del fixture; no descomposición causal general | CSV de resumen/trayectoria |

Los umbrales de problema son `1.0` en la dimensión activa: la frontera
productiva inicial del equipo con déficit es `1.15` con dos esfuerzos unitarios.
Los problemas de prueba usan pesos CES `(1,0)` o `(0,1)` para que la recompensa
corresponda a la dimensión activa; no se alteró la función CES. Los escenarios
son deliberadamente diagnósticos: un solo par de ramas por caso, P0 como
continuación común, aprendizaje organizativo a partir de observaciones,
ruido cero y semilla `2501`. No hay inferencia poblacional. MIS-v2 no permite
`eta=0` por contrato (`0<eta<1`); el control sin MIS usa el interruptor de
desactivación. La especialización y complementariedad son funcionales a los
requisitos, pues la producción sigue siendo aditiva.

La política productiva maximiza el orden funcional (éxito, déficit, margen y
esfuerzo), no CES. El precio de recurso `.2` queda registrado como coste, pero
no se resta de CES ni define una tasa de intercambio; las diferencias
reportadas son recompensa productiva bruta, no valor económico neto.

No se encontró defecto de implementación que justificara modificar el motor,
la producción, MIS-v2, la transición docente o el generador. Durante la
preparación se descartó un umbral inicial `1.8`, que excedía la frontera del
equipo y hacía el fixture no informativo; se sustituyó antes de fijar la
ejecución por el nivel estructuralmente factible `1.0`. Este fue un defecto
del fixture diagnóstico, no del laboratorio. El catálogo discreto deja
residuo presupuestario en ciertos estados y no se añadió un control de
producción divisible para preservar el contrato histórico. La suite completa
no se repitió; el último resultado registrado es 1,189 passed / 13 fallos de
integridad/procedencia, que siguen visibles y sin alterar sus hashes.
