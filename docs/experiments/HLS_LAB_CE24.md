# CE-24 — Validación experimental de HLS Laboratory v1

**Estado: PARTIAL — microexperimento determinista ejecutado y reproducible; HOLD para afirmaciones generales o escalado.** Este protocolo se fijó antes de la ejecución; el apartado de resultados se añadió después sin modificar dominio, secuencias ni métricas. No modifica los contratos C0–C4, MIS-v2 ni las políticas de laboratorios anteriores.

## Pregunta, hipótesis y alcance

Pregunta principal: bajo competencias individuales congeladas, ¿actualizar el estado tabular de `ExploreThenGreedy` durante entrenamiento mejora su rendimiento posterior en problemas de los mismos contextos, frente a ejecutar la misma regla sin actualizar su estado?

Hipótesis de trabajo H1: tras observar todas las acciones legales en dos contextos conocidos, la regla tabular puede elegir la única acción exitosa de cada contexto en una evaluación congelada. H0 operacional: sin actualización, el estado organizativo permanece vacío y el selector repite su primera acción no visitada, ya que no conserva memoria de visitas. La comparación estima el efecto de habilitar `U` en esta regla/inicialización/dominio concretos. No prueba que cualquier organización pueda aprender ni que el método generalice.

El resultado es un experimento de mecanismo dentro de un simulador determinista. La semilla de trazas no induce variación; no se tratarán repeticiones idénticas como muestras independientes ni se calcularán intervalos de confianza.

## Auditoría previa y resolución

- `JOINT_ACTIONS` contiene 64 asignaciones. Con presupuesto 1 y el límite individual por defecto, A y B tienen 10 acciones factibles cada una; C tiene 37 con presupuesto 2; D tiene 10 con presupuesto 1. El learner explora cada acción factible de un contexto una vez, por orden de catálogo, y luego explota la media de éxito.
- Se conserva el catálogo completo: no se recorta ni reordena en el análisis primario. Para A y B, enumerar antes de simular muestra una única acción exitosa entre las diez factibles; esto hace interpretable el resultado de exploración completa.
- `OrganizationState` se reinicia por defecto en `run_sequence`; la extensión CE-24 permite suministrar el estado inicial explícitamente. Así TRAIN devuelve `θ`; EVAL lo reutiliza con LO apagado y verifica que no cambie.
- Con LO=OFF y estado vacío, `choose` no avanza el conteo de acciones sin probar: repite la primera acción del catálogo (ID 0 en el orden canónico; producción nula en el equipo de referencia). Se preserva tal comportamiento, no se cambia por otro baseline. Esta limitación hace necesario incluir referencias informadas y una sensibilidad al orden; restringe la interpretación del contraste.
- `GreedyAdaptive` lee `ŝ=s` y puntúa producción/requisitos; el oráculo enumera el mismo conjunto factible. Ambos son referencias informadas, no controles causales de LO.
- La semilla no alimenta generador aleatorio alguno en v1. MIS-v2 aquí es determinista.
- `difficulty=r1+r2` solo mide escala operacional de exigencia. Factibilidad depende además de competencias, presupuesto, máximo individual y acciones legales; no se interpreta como dificultad intrínseca.
- Complementariedad C se evalúa frente a cada experto con el mismo presupuesto total 2 y el mismo máximo individual 1. C es `team_only`; A/B son individualmente factibles; D es no factible. No se equipara a sinergia superaditiva.
- El dominio no está saturado: A y B tienen acciones que pasan y fallan; C es factible solo con una acción de equipo; D no tiene acción exitosa.

## Dominio predefinido

Equipo fijo `E0=(1,0), E1=(0,1), E2=(0,0)`, con `ŝ=s`, tres expertos, acciones originales de `JOINT_ACTIONS`, máximo de esfuerzo individual 1, `eta=0.35` de referencia Campaign 0 y coste explícito por unidad de recurso 0. No se aprende competencia en el análisis primario.

| Contexto | Requisitos | Presupuesto | Acciones factibles | Acciones exitosas | Uso |
|---|---:|---:|---:|---|---|
| A | (0.8, 0) | 1 | 10 | ID 48 | entrenamiento y evaluación; suficiente por E0 |
| B | (0, 0.8) | 1 | 10 | ID 4 | entrenamiento y evaluación; suficiente por E1 |
| C | (0.8, 0.8) | 2 | 37 | ID 52 | control de complementariedad no entrenado (`team_only`) |
| D | (0.95, 0.95) | 1 | 10 | ninguna | control negativo no factible |

El conjunto factible se deriva de las 64 acciones congeladas y las restricciones de cada problema; no se diseñó un catálogo ad hoc. Los IDs exitosos se obtienen por enumeración analítica del equipo/requisitos/recursos antes de correr trayectorias.

### Secuencias

- TRAIN: diez ciclos `A,B` alternados (20 episodios), de modo que cada contexto observa una vez sus diez acciones factibles. El learner con LO=ON completa la exploración; el control LO=OFF repite la primera acción por la semántica existente.
- EVAL_RESET: cuatro ciclos `A,B` (ocho episodios frescos con IDs de contexto ya conocidos), seguidos por `C,D` como controles de contexto no entrenado/no factible (dos episodios). Se usa el equipo inicial de referencia, el estado organizativo final de TRAIN y se desactiva todo aprendizaje.
- EVAL_CARRYOVER: mismo diseño de EVAL, pero usa las competencias finales de TRAIN. Es secundario; sus diferencias incluyen el estado de competencia generado durante TRAIN y no son un efecto aislado de LO.
- Sensibilidad de orden predefinida: repetir LI=OFF con el mismo conjunto factible en orden inverso. No sustituye ni selecciona retrospectivamente el análisis primario.

La evaluación de A/B mide reutilización de contextos conocidos; `problem_id` es la clave del estado tabular. C/D nunca se usan para afirmar transferencia a contextos nuevos. Son controles: el selector comienza sin valores para ellos y permanece congelado.

## Comparadores y factorial

Primario, LI=OFF: `ExploreThenGreedy` LO=ON frente a la misma clase LO=OFF. Equipo, objetos `ProblemSpec`, recursos, acciones, información, orden, inicialización de `θ` y secuencia coinciden; solo cambia si `observe` actualiza `θ`. La evaluación preserva `θ` aprendido en LO=ON y el estado vacío en LO=OFF, sin actualizar ninguno.

Referencias EVAL adicionales: `FixedRouting` con el máximo por contexto seleccionado exhaustivamente antes de ejecutar (oráculo contextual) y `GreedyAdaptive` con competencia estimada perfecta. El oráculo se define por éxito, menor déficit normalizado, mayor margen y menor esfuerzo, con desempate por orden del catálogo. Estas referencias tienen información del modelo y no son comparadores de información igualada.

Secundario LI×LO: ejecutar las cuatro celdas ON/OFF en TRAIN. Para cada una reportar EVAL_RESET con el mismo equipo de referencia y EVAL_CARRYOVER con competencias finales. La comparación de trayectorias y de TRAIN puede estar mediada por decisiones, exposiciones y competencias; no se atribuye a un único efecto directo.

## Resultados y métricas predefinidas

Por episodio: `EpisodeRecord` completo, fase, política/condición, ID/requisitos, competencias y experiencia antes/después, acción, producción individual/colectiva, éxito, déficit normalizado, margen, esfuerzo/coste, `θ` antes/después y actualizaciones. Por fase/organización: episodios, éxitos/tasa, déficit normalizado medio, esfuerzo medio/total, coste explícito, acciones distintas por contexto, actualizaciones y estado final de competencia.

El coste explícito de recursos es cero según el microdominio; se reporta esfuerzo como consumo físico, sin convertirlo en penalización. El coste de exploración se presenta como número de acciones distintas exploradas, episodios de entrenamiento y esfuerzo, no como un escalar neto económico. Éxitos TRAIN+EVAL se pueden sumar como conteo de este protocolo, pero EVAL_RESET reinicia capacidades; no representa una trayectoria física continua. No se promedian ni se construyen intervalos sobre semillas repetidas.

Se documentarán explícitamente resultados negativos, controles sin ventaja y la sensibilidad al orden. La igualdad exacta del resultado de Greedy y el oráculo, si aparece, se interpreta como efecto de conocimiento informacional equivalente en este estado determinista, no como estimación poblacional.

## Reproducibilidad y seguridad de resultados

Comando desde la raíz:

```bash
PYTHONPATH=src:. python experiments/synthetic/hls_lab_v1/ce24.py \
  --output-dir /tmp/hls_lab_ce24_reproduction
```

Salida pequeña y create-only: el directorio nuevo indicado por `--output-dir`. El ejecutor aborta si el directorio de salida ya contiene resultados. Escribe `episodes.jsonl`, `summary.csv`, `problem_metrics.csv` y `manifest.json` con conteos, hashes, commit/código y la nota de semilla no consumida. No se ejecutan campañas grandes ni mecanismos estocásticos.

Validación ejecutada: `PYTHONPATH=src:. pytest -q tests/test_hls_lab_v1.py tests/test_hls_lab_v1_ce24.py tests/test_discover_v0.py tests/test_discover_develop_v2.py tests/test_campaign0_discriminative_capacity.py tests/synthetic/test_g0_a1_reference_worlds.py tests/synthetic/test_g0_architecture.py tests/synthetic/test_c1_reference_worlds.py` — **99 passed**. `git diff --check` — **passed**. Los tests comprueban semántica, conteos del dominio, persistencia/freeze θ, competencias, factibilidad, baselines, export/hashes y regresiones históricas pertinentes; no ejecutan campañas extensas.

## Resultados observados

Se ejecutaron 18 grupos y se conservaron 240 registros de episodio en JSONL, un resumen por grupo y métricas por problema. Las condiciones son finitas y deterministas, por lo que los valores son exactos para estas secuencias; no se reportan errores estándar, valores p ni intervalos sobre semillas ficticias.

### Contraste principal: LI=OFF

| Condición / fase | Éxitos | Éxito | Déficit normalizado medio | Esfuerzo total | Acciones distintas por contexto |
|---|---:|---:|---:|---:|---|
| LO=OFF — TRAIN (20) | 0/20 | 0% | 1.0000 | 0 | A:1, B:1 |
| LO=ON — TRAIN (20) | 2/20 | 10% | 0.8375 | 18 | A:10, B:10 |
| LO=OFF — EVAL_RESET (10) | 0/10 | 0% | 1.2000 | 0 | A/B/C/D:1 cada uno |
| LO=ON — EVAL_RESET (10) | 8/10 | 80% | 0.4000 | 8 | A/B/C/D:1 cada uno |
| LO=OFF — EVAL_CARRYOVER (10) | 0/10 | 0% | 1.2000 | 0 | A/B/C/D:1 cada uno |
| LO=ON — EVAL_CARRYOVER (10) | 8/10 | 80% | 0.4000 | 8 | A/B/C/D:1 cada uno |

En EVAL_RESET, los dos métodos aciertan A=4/4 y B=4/4 con LO=ON; LO=OFF acierta 0/8. Ambos fallan los controles C y D: el estado tabular no tiene valores para sus contextos nuevos y permanece congelado. `θ` se actualizó 20 veces durante entrenamiento LO=ON y cero durante evaluación. Las competencias permanecen idénticas en la comparación primaria LI=OFF.

El conteo bruto TRAIN+EVAL_RESET es 10/30 con LO=ON frente a 0/30 con LO=OFF en el orden canónico; el déficit medio ponderado por episodio es 0.6917 frente a 1.0667. No se convierte esfuerzo a una penalización o utilidad neta: el coste explícito del dominio es cero y el esfuerzo acumulado fue 26 frente a 0. Esto muestra que el resultado depende de cómo se inicializa el control no aprendido, no que aprender sea “gratis”.

### Referencias informadas y orden

En EVAL_RESET, `FixedRouting` con el oráculo contextual y `GreedyAdaptive` obtienen ambos 9/10 éxitos, déficit medio 0.1000 y esfuerzo 11. Son referencias privilegiadas: conocen asignaciones/requisitos o `ŝ=s`, y no son controles causales de LO. El learner con θ entrenado obtiene 8/10, déficit 0.4000 y esfuerzo 8: resuelve todos los problemas de contextos conocidos A/B, pero no transfiere a C. El oráculo sí resuelve C; D es inviable para todos.

La sensibilidad predefinida invirtió únicamente el orden del mismo conjunto legal de acciones:

| Orden / condición | TRAIN éxitos | EVAL_RESET éxitos | TRAIN+EVAL éxitos | EVAL déficit medio | Esfuerzo TRAIN/EVAL |
|---|---:|---:|---:|---:|---:|
| Canónico, LO=OFF | 0/20 | 0/10 | 0/30 | 1.2000 | 0 / 0 |
| Canónico, LO=ON | 2/20 | 8/10 | 10/30 | 0.4000 | 18 / 8 |
| Invertido, LO=OFF | 10/20 | 4/10 | 14/30 | 0.6000 | 20 / 11 |
| Invertido, LO=ON | 2/20 | 8/10 | 10/30 | 0.2000 | 18 / 11 |

El control LO=OFF repite siempre la primera acción porque θ no registra acciones ya vistas: con el orden canónico es la acción ID 0, sin esfuerzo ni producción; con el orden invertido es ID 48, que resuelve A pero falla B. Por tanto la magnitud del beneficio post-entrenamiento cambia (8 frente a 0; invertido, 8 frente a 4) y el conteo bruto acumulado TRAIN+EVAL se invierte bajo el orden invertido. Este es un resultado negativo sobre robustez del comparador y un efecto de tie/order, no evidencia de que LO empeore universalmente.

### Interacción LI×LO

En las cuatro celdas se corrieron TRAIN, EVAL_RESET con el θ aprendido congelado y EVAL_CARRYOVER con competencias finales congeladas. LI=ON/LO=OFF repitió la acción nula, adquirió exposición cero y terminó sin cambios. LI=ON/LO=ON obtuvo 2/20 éxitos de TRAIN, expuso las acciones completas y elevó competencias en dimensiones expuestas; el estado final fue `((1,.725375),(.725375,1),(.725375,.725375))`. Su EVAL_RESET fue 8/10, igual al caso LI=OFF/LO=ON; EVAL_CARRYOVER también 8/10. En esta fixture las rutas exitosas ya usaban competencias máximas, por lo que la adquisición de otras dimensiones no elevó la tasa de éxito de evaluación. El déficit TRAIN bajó de 0.8375 (LI=OFF/LO=ON) a 0.7088 (LI=ON/LO=ON), pero esta diferencia combina cambios de capacidad y resultados de exploración.

## Integridad de artefactos y ejecución

La primera exportación se conserva en `results/experiments/hls_lab_ce24/`. Al inspeccionarla se detectó que una columna del CSV resumido se llamaba `training_final_competencies` aunque contenía el estado final de cada fase. No cambió datos de episodio; se corrigió el nombre/representación en la exportación validada, que es la fuente canónica para las tablas de este reporte: `results/experiments/hls_lab_ce24_validated/`. Los SHA-256 de `episodes.jsonl` coinciden exactamente entre ambas exportaciones (`653990789acb9e4c73d1de27ce00a76495d2e8a45fbcbe93218e38a952489469`), lo que verifica que la corrección fue solo de presentación/serialización. No se sobrescribió la primera salida.

Hashes de la exportación validada:

- `episodes.jsonl`: `653990789acb9e4c73d1de27ce00a76495d2e8a45fbcbe93218e38a952489469`
- `summary.csv`: `e13424c56a943bf17139d60a8623772a0851acd8db3553bf81a503bb8b7c4153`
- `problem_metrics.csv`: `7dd759d25393de65dd6fcad20d8a2c1bdc04d85e0bdd6d6c71d83146fec54cb8`

Tras la primera exportación se normalizaron únicamente los finales de línea CSV a LF para que `git diff --check` acepte los artefactos; los registros no cambiaron. El exportador fija ahora explícitamente ese formato. Los hashes anteriores corresponden al contenido canónico normalizado y coinciden con `manifest.json`.

El manifiesto registra 240 episodios, los recuentos 64/10/37/10 del catálogo/dominio, acciones óptimas enumeradas, semilla registrada pero no consumida, comando y hashes de código/salidas. La ejecución corresponde al código basado en el commit CE-23 `624e24925d3430f1c6b34f257e3c8d1825feb773`; el hash de cada archivo local ejecutado está en el manifiesto. La repetición de serialización en tests produjo CSV y JSONL idénticos salvo metadatos de ejecución, y las salidas guardadas tienen hash validado.

## Interpretación, validez y decisión

**Hallazgo estrecho:** el estado θ tabular persiste entre TRAIN y EVAL; con LI apagado y contextos A/B conocidos, actualizarlo cambia la acción futura y mejora los resultados de evaluación frente a ejecutar la misma regla desde θ vacío. Este efecto se reproduce exactamente en el sistema determinista.

**No demostrado:** robustez del beneficio frente a inicialización/orden, superioridad frente a políticas informadas, generalización a tipos nuevos, prevalencia de problemas donde aprender ayuda, ni utilidad económica neta. El learner no resuelve el contexto complementario C si no se entrenó allí; `GreedyAdaptive`/oráculo sí lo hacen con información privilegiada. La semilla es inerte, no hay variación experimental ni base para inferencia poblacional.

Amenazas principales: una sola geometría de equipo y secuencia finita; recompensa binaria; no estacionariedad si LI está activo; selección de exploración por orden de catálogo; LO=OFF congelado no recuerda intentos y por ello repite el primer brazo; exploración causa consumo de esfuerzo y pérdidas durante TRAIN; tipos nuevos no comparten valores tabulares. El coste monetario está fijado a cero y no se adopta una conversión esfuerzo-éxito.

**Decisión: HOLD** antes de presentar una afirmación general o escalar a factoriales. CE-24 satisface una demostración mecanística local, pero el orden de acciones controla fuertemente el comparador y no hay aleatoriedad/inferencia. La v1 queda **PARTIAL**, no COMPLETE, como validación científica general; no es NO-GO para el software ni para el resultado condicional observado.

**Siguiente acción recomendada para CE-25:** revisión/decisión científica del Chief Engineer sobre el contrato de control LO=OFF y la semántica de exploración inicial (incluida su dependencia del orden) antes de cualquier nuevo dominio o ejecución. No cambiar el selector ni el protocolo CE-24 retrospectivamente.
