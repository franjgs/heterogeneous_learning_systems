# HLS-G0-C6 — Cierre científico y técnico

**Fecha:** 19 de octubre de 2026  
**Estado:** **CLOSED — STOP**  
**Decisión:** cerrar la línea C6 y preservar el modelo, código y evidencia. No se ejecutó ninguna campaña adicional para este cierre.

## A. Motivación y pregunta

C6 examinó si anticipar el desarrollo de capacidades bajo demanda estocástica puede superar la mejor asignación estática de rutas entre agente y tipo de tarea. La pregunta fue acotada a si, en la instancia G0/RQ0 configurada, la decisión conjunta de enrutamiento y desarrollo obtiene mayor valor esperado que el mejor mapa estacionario tarea→agente.

Referencias: [diseño de validación HLS-E1](HLS_E1_VALIDATION_DESIGN_2026-10-19.md), [informe exploratorio C6](HLS_G0_C6_EXPLORATORY_REPORT_2026-10-19.md) y [análisis exacto del mecanismo](HLS_G0_C6_EXACT_MECHANISM_ANALYSIS_2026-10-19.md). HLS-E1 (Nembhard) no es el experimento HLS-G0-C6.

## B. Modelo

Se usó G0/RQ0 con dos agentes (`M1`, `M2`), dos tareas y horizonte de cuatro periodos. La competencia inicial es `((0.8, 0.8), (0.6, 0.6))`. En cada periodo se observa la tarea, se enruta a un agente, se observa la oportunidad de desarrollo y se decide si desarrollar: **routing → opportunity observation → development**. La recompensa operativa es la competencia del agente asignado en la tarea actual.

La acción explícita A1 puede mejorar la competencia del agente elegido en la tarea 1 mediante `c' = c + eta (1-c)`. Hay presupuesto inicial 1; una acción no nula consume todo el presupuesto. El coste de desarrollo en el objetivo es cero (`beta=1`), y se suma al final la mayor competencia en tarea 1. Presupuesto físico y coste objetivo son, por tanto, magnitudes distintas.

Factores: `eta ∈ {0, 0.1, 0.75}`. **Stationary:** demanda 0.5/0.5 para tareas 1/2 en cada periodo. **Changing:** (0.8, 0.2) en periodos 0–1 y (0.2, 0.8) en 2–3. La oportunidad A1 depende del agente enrutado: probabilidad 0 tras M1 y 1 tras M2, independiente de tarea. Es determinista condicional a la ruta; el replay no valida oportunidades con aleatoriedad no degenerada.

## C. Políticas

| Política | Definición ejecutada |
| --- | --- |
| `BEST_STATIC` | Optimiza globalmente un mapa estacionario tarea→agente bajo la ley de demanda. El mapa de rutas queda fijo; el desarrollo sí se optimiza con continuación. No es una organización completamente fija. |
| `MYOPIC` | Maximiza la recompensa operativa actual; en empates de desarrollo se elige no desarrollar. |
| `STRONG_SEP` | Enruta solo dentro del conjunto de máximos de recompensa operativa inmediata; la continuación resuelve empates únicamente dentro de ese conjunto. Prueba focalizada: `test_strong_sep_uses_continuation_only_to_resolve_immediate_ties`; no hubo empates de ruta en la campaña. |
| `HLS` | Optimización exacta conjunta de enrutamiento y desarrollo en horizonte finito. Conoce modelo y ley de demanda, no las tareas futuras realizadas; no es un aprendiz online. |

Las interfaces y el orden temporal se encuentran en [`e1_minimum.py`](../../src/hls/synthetic/e1_minimum.py) y [`exact.py`](../../src/hls/synthetic/exact.py).

## D. Diseño y validación registrada

Se cruzaron 3 intensidades × 2 demandas × 20 bloques de semillas: 120 trayectorias exógenas, cada una evaluada con las cuatro políticas (480 evaluaciones). Los IDs son `2026101900`–`2026101919` en cada celda. Configuración, semillas, realizaciones de demanda, cintas de oportunidad, trazas y resultados están en [`exploratory_results.json`](../../results/experiments/hls_g0_c6/exploratory_results.json), bajo `campaign_design` e `instances[].trajectory_records`.

El informe de campaña registra 101 pruebas focalizadas, 272 pruebas de la suite sintética y `ruff check` satisfactorios en el alcance indicado. Esta evidencia verifica contratos de ejecución/replay descritos por esos tests; no demuestra superioridad. Este cierre no vuelve a ejecutar pruebas ni campaña.

## E. Resultados exactos

El JSON guarda floats IEEE-754 (p. ej. `4.015624999999999`); la tabla presenta sus valores matemáticos, y la diferencia es solo redondeo numérico.

| `eta` | Demanda | BEST_STATIC | MYOPIC | STRONG_SEP | HLS | Gap HLS−BEST_STATIC |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | Stationary | 4.0 | 4.0 | 4.0 | 4.0 | 0 |
| 0.1 | Stationary | 4.0 | 4.0 | 4.0 | 4.0 | 0 |
| 0 | Changing | 4.0 | 4.0 | 4.0 | 4.0 | 0 |
| 0.1 | Changing | 4.0 | 4.0 | 4.0 | 4.0 | 0 |
| 0.75 | Stationary | 4.015625 | 4.0 | 4.0 | 4.175 | **0.159375** |
| 0.75 | Changing | 4.00544 | 4.0 | 4.0 | 4.13 | **0.12456** |

Identidad: valor = producción operativa acumulada − coste objetivo de desarrollo + recompensa terminal.

| Demanda | Diferencia operativa | Diferencia de coste de desarrollo | Diferencia terminal | Diferencia total |
| --- | ---: | ---: | ---: | ---: |
| Stationary | +0.10625 | 0 | +0.053125 | **+0.159375** |
| Changing | +0.07232 | 0 | +0.05224 | **+0.12456** |

Esta descomposición es una identidad contable exacta, no una atribución causal única de efectos de routing y desarrollo, que interactúan mediante oportunidades y estados futuros. El coste objetivo es cero; eso no significa que el uso del presupuesto sea idéntico.

## F. Mecanismo exacto

Con `eta=0.75` y tarea inicial 2, HLS enruta M2 (recompensa inmediata 0.6, frente a 0.8 con M1), observa oportunidad con probabilidad 1 y desarrolla M1 en competencia 1. BEST_STATIC enruta M1 para la tarea 2, recibe 0.8 y no tiene oportunidad. El valor Bellman para HLS:

| Demanda | Ruta M1 | Ruta M2 + desarrollar M1 | Diferencia a favor de M2 |
| --- | ---: | ---: | ---: |
| Stationary | 4.100 | 4.175 | **+0.075** |
| Changing | 4.010 | 4.130 | **+0.120** |

La oportunidad aporta continuación 0.275/0.320, que compensa la pérdida inmediata 0.2: `−0.2 + 0.275 = +0.075` y `−0.2 + 0.320 = +0.120`. Son diferencias exactas entre acciones en el estado inicial, no estimaciones del muestreo.

Con tarea inicial 1, ambos enrutan M2 y reciben 0.6. Tras observar la oportunidad, HLS desarrolla M1 y BEST_STATIC desarrolla M2. La competencia de M1 en tarea 1 sube de 0.8 a 0.95; luego HLS enruta M1 para ambas tareas. BEST_STATIC mantiene su mapa optimizado `task 1→M2, task 2→M1`. Así, el mecanismo incluye anticipación del desarrollo y flexibilidad de enrutamiento futuro.

Testigo de trayectoria factible `(2,1,1,1)`, con probabilidad positiva `1/16` en stationary y `0.0064` en changing: HLS obtiene recompensas operativas `0.6, 0.95, 0.95, 0.95` y terminal 0.95 (total 4.4); BEST_STATIC obtiene `0.8, 0.6, 0.9, 0.9` y terminal 0.9 (total 4.1). Es una ilustración, no una descomposición causal del valor esperado.

## G. Relación con hallazgos HLS anteriores

- **G1:** aporta principios de organización/demanda y controles nulos; C6 no establece un principio organizativo nuevo.
- **G2:** ya muestra sacrificio presente por desarrollo futuro y reversión de decisión en un modelo finito 2×2. C6 cuantifica una instancia de horizonte 4 con demanda estocástica y oportunidad condicionada por ruta.
- **MIS:** C6 no usa MIS/MIS-v2 learning-by-doing; usa desarrollo explícito A1 posterior a una oportunidad. No valida MIS-v2.
- **G3/G3-H:** ya caracterizan valor del desarrollo vía sensibilidad de asignación y relevancia de oportunidades futuras. C6 es compatible como instancia cuantitativa, pero su ley no es la ley MIS heterogénea de G3-H.
- **RQ0:** la comparación reproduce numéricamente el valor oportunidad `−0.2 + 0.275 = 0.075` / `−0.2 + 0.320 = 0.120`; no añade un teorema de inclusión de clases.
- **Campaign 2:** tiene otra estructura de enseñanza/MIS-v2 e información. Sus retornos prospectivos condicionales no establecen superioridad Q11 sobre Q10 y no son esta comparación A1.

Conclusión de alcance: C6 aporta validación de una ruta pequeña G0/RQ0 y caracterización cuantitativa exacta de un mecanismo ya consistente con G2, G3-H y RQ0; no demuestra una contribución científica estructural nueva.

## H. Límites y activos preservados

El resultado cubre una matriz inicial, dos agentes, dos tareas, cuatro periodos, un presupuesto, una tarea desarrollable y una estructura A1. Las oportunidades son degeneradas 0/1; el coste objetivo de desarrollo es cero; BEST_STATIC restringe rutas pero no congela desarrollo. HLS conoce el modelo y la ley de demanda: no hay estimación ni exploración. El gap también aparece con demanda estacionaria, por lo que el diseño no identifica la no-estacionariedad como causa. Los 20 pares por celda son exploratorios; los valores exactos son más decisivos para estas instancias.

Se preservan en el alcance **G0/RQ0**: solucionador exacto finito, demanda estocástica, cuatro políticas ejecutables, baseline de routing estacionario globalmente optimizado, regla STRONG_SEP de empates, replay pareado, runner, persistencia estructurada y pruebas de regresión. No atribuir estas capacidades a la ruta N×K completa: son activos de esta rama sintética G0/RQ0.

## I. Decisión final

**DECISIÓN: STOP HLS-G0-C6 — CLOSED.** El gap de estas instancias queda explicado por desarrollo anticipatorio condicionado por oportunidad y posterior routing flexible. El análisis no ofrece una proposición adicional que justifique prolongar C6 como línea independiente.

STOP implica no realizar más campañas C6, no ampliar sus parámetros y no sostener una afirmación de publicación basada solo en C6; sí implica preservar código, pruebas, informes y resultados. STOP no significa fallo de implementación, invalidez de resultados ni cierre del programa HLS.

## J. Reproducción e inspección

Tests focalizados:

```sh
PYTHONPATH=src pytest -q tests/synthetic/test_e1_minimum.py tests/synthetic/test_exact_solver.py
```

Recalcular los valores exactos de las seis celdas con APIs existentes (no es una campaña):

```sh
PYTHONPATH=src python -c 'from hls.synthetic.e1_minimum import build_e1_instance, four_policy_solutions; [(print(eta, demand, {name: sol.value for name, sol in four_policy_solutions(build_e1_instance(eta=eta, demand=demand, horizon=4)).items()})) for demand in ("stationary", "changing") for eta in (0.0, 0.1, 0.75)]'
```

El runner original es `PYTHONPATH=src python experiments/run_hls_g0_c6.py`. El resultado canónico ya existe y el runner usa creación exclusiva, rechazando sobrescritura; no ejecutarlo sobre el archivo archivado. No hay opción CLI de reanudación ni destino alternativo documentado. El informe de mecanismos no tiene un comando standalone que reconstruya la tabla completa de estados y descomposición; esa limitación analítica queda registrada. Configuraciones, seeds y trazas se inspeccionan en `results/experiments/hls_g0_c6/exploratory_results.json`, bajo `campaign_design` e `instances[].trajectory_records`.

## K. Fuentes

- [Diseño HLS-E1](HLS_E1_VALIDATION_DESIGN_2026-10-19.md) — motivación y comparadores.
- [Informe exploratorio](HLS_G0_C6_EXPLORATORY_REPORT_2026-10-19.md) — ejecución, tests y resultados empíricos.
- [Análisis exacto](HLS_G0_C6_EXACT_MECHANISM_ANALYSIS_2026-10-19.md) — estados, valores Bellman, descomposición y mecanismo.
- [G0](G0.md), [fundamentos del entorno sintético](../experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md), [RQ0](../theory/rq0_routing_integration_boundaries.md), [G2](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md), [G3/G3-H](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md) y [Campaign 2](../theory/CAMPAIGN_2_THEORETICAL_SPECIFICATION.md) — contexto científico previo.
- Código y evidencia: [`e1_minimum.py`](../../src/hls/synthetic/e1_minimum.py), [`exact.py`](../../src/hls/synthetic/exact.py), [`run_hls_g0_c6.py`](../../experiments/run_hls_g0_c6.py), [`test_e1_minimum.py`](../../tests/synthetic/test_e1_minimum.py), [`test_exact_solver.py`](../../tests/synthetic/test_exact_solver.py), [`exploratory_results.json`](../../results/experiments/hls_g0_c6/exploratory_results.json).
