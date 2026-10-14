# HLS Laboratory v1

**Estado: PARTIAL — vertical slice implementada y pruebas P1–P9 ejecutadas; no es una campaña ni evidencia científica sobre equipos reales.** Esta guía describe el alcance mínimo de CE-23 y no sustituye al contrato de referencia, que se conserva en [HLS_LAB_V1_SCIENTIFIC_CONTRACTS.md](HLS_LAB_V1_SCIENTIFIC_CONTRACTS.md).

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

- `src/hls/hls_lab_v1.py`: ensamblaje v1 nuevo: contratos, filtrado de acciones por recursos, evaluación funcional, clasificadores de factibilidad, organizaciones, motor de secuencia, trazas y serialización determinista JSON.
- `src/hls/discover_v0.py`: fuente de `JOINT_ACTIONS`, validación de estado/acción y producción lineal `production_inputs`; no se modifica.
- `src/hls/discover_develop_v2.py`: transición MIS-v2 reutilizada; no se modifica.
- `experiments/synthetic/hls_lab_v1/demo.py`: demostración pequeña fija y determinista; no ejecuta factoriales.
- `tests/test_hls_lab_v1.py`: fixtures analíticos P1–P9.

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

Las nueve pruebas están en `tests/test_hls_lab_v1.py` y corresponden a P1–P9 del contrato: independencia orientación/exigencia y recompensa; complementariedad `team_only` con control individual; no etiquetar falsamente complementariedad; aislamiento de MIS-v2; actualización organizativa tabular que altera una decisión posterior; adaptación sin cambio de `θ`; firewall y controles LI/LO; dominio factible/no factible; repetibilidad y serialización determinista.

Resultado registrado en esta entrega: `PYTHONPATH=src:. pytest -q tests/test_hls_lab_v1.py` — **9 passed**. La demo determinista se ejecuta además como comprobación funcional. Esto valida contratos de software en microfixtures, no afirma que se hayan completado barridos o experimentos de desempeño. Los resultados de tests deben volver a ejecutarse en el commit/PR final.

## Trazabilidad CE-01–CE-21

La v1 responde al encargo de ensamblaje CE-23 y su contrato científico CE-22. Reutiliza de modo acotado componentes cuya semántica ya aparece en el laboratorio: producción/acciones DISCOVER-v0, transición MIS-v2 y patrones de instrumentación CE-16. Conserva deliberadamente la evidencia y los contratos de CE-01–CE-21: no reejecuta ni edita C0–C4, G0/C1, CE-16, FAST/DEEP/META-VOC, predictor-validity, ni los protocolos y resultados congelados. Los comparadores de organización de G0/C1 tampoco se redefinen. Esta implementación no reivindica resolver limitaciones científicas identificadas en esos trabajos ni hereda sus conclusiones.

SHA-256 del documento de contrato descargado al incorporar CE-23: `2ac24be1bd19f92d5d4d28e8501e6b885ef8483e83c1c066436c1319eb941349`. Hashes de las fuentes reutilizadas, verificados durante esta entrega: `discover_v0.py` `ef1eee85cf7735107e46e285af4ce2734906a55a6741ec09a72a2623c1ab470f`; `discover_develop_v2.py` `06d70479a1f8e5bd7408a3a3c5596de4fca9e139838441f5de7dbb78c32e4e80`. Son identificadores de contenido de esta revisión local, no garantías sobre otros commits.

## Limitaciones y trabajo pendiente

- Es una vertical slice, no el factorial v1 ni un laboratorio completo: no hay un conjunto de problemas/calibración registrado, campañas, CLI de barrido, persistencia de resultados o manifiestos de ejecución.
- Una decisión por problema limita preguntas temporales dentro del episodio; solo hay aprendizaje entre problemas.
- Competencia estimada igual a real elimina incertidumbre de competencia; no hay creencias ni estado informativo imperfecto.
- Producción aditiva y catálogo discreto reutilizado no representan sinergias/interdependencias más ricas.
- La transición MIS-v2 se reutiliza tal cual; `eta` no está calibrada empíricamente y no debe interpretarse como tasa real de aprendizaje.
- El learner tabular explora acciones en orden y usa problema ID como contexto; no generaliza automáticamente y puede recibir recompensas no estacionarias si LI está activo.
- El clasificador `team_only` mide factibilidad bajo restricciones compartidas, no una ventaja de producción superaditiva.
- El coste monetario/computacional es solo un campo explícito; la demo usa coste por unidad cero. No existe modelo de coste estimado.
- Antes de cualquier factorial: congelar protocolo/dominio/seeds, definir cómo se comparan learning on/off bajo no estacionariedad y revisar que el muestreo no esté saturado. No ejecutar esa fase como parte de CE-23.

La clase de entrega es **PARTIAL**, no COMPLETE: el ensamblaje, demo y pruebas contractuales existen; una evaluación científica factorial queda expresamente fuera de alcance.
