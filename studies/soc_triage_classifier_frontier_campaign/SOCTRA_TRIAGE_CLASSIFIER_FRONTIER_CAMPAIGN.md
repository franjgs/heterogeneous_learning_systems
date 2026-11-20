# SOCTRA–HLS joint classifier-frontier campaign

## Objetivo y fuente de configuraciones

Esta extensión evalúa, en el simulador organizativo existente, los 13 puntos de la frontera conjunta de detección/falsa alarma y cuatro controles de la fase 2. Los puntos publicados son tasas agregadas del artículo, no predicciones individuales sobre alertas SOCTRA. Las recomendaciones son sintéticas y automáticas. No se simula reportado. D1, P1 y WAPS/HLS-B permanecen sin cambios.

La frontera conjunta se fija por definición de etiquetas, agrupando Tables 5 y 7, con el criterio maximize pD/minimize pFA; se conservan BA, beneficio, coste, algoritmo y características en [`joint_pareto_frontier_13.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/joint_pareto_frontier_13.csv), con el inventario auditado completo en [`classifier_inventory_72.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/classifier_inventory_72.csv). Los resultados de coste simétrico y asimétrico son puntos operativos de configuraciones diferentes, no una única curva ROC.

## Auditoría de prevalencia, trazas y reutilización

Se mantuvieron por separado original 39/14.449 (etiquetas auditadas directamente), original 40/14.449 (inferencia del IR redondeado de la Tabla 1) y estandarizadas 19/14.449 (IR del artículo). La configuración fase 2 había guardado pi=0.002699840128036543, aunque estaba rotulada 39/14.449. La regeneración con el mismo generador y semillas mostró que las trazas exógenas y los hashes completos de recomendación de sus cuatro puntos originales coinciden exactamente con pi=39/14.449 en las 80 celdas semilla×carga; esas filas se reutilizaron como realización sintética compatible, dejando constancia de la discrepancia de metadatos.

Para pi=40/14.449, coincidieron 77/80 celdas semilla×carga. Las únicas diferencias fueron semilla 272600013 con rhoL1=1.25 y semilla 272600030 con rhoL1=.85 y 1.25. Se reutilizaron las filas de las otras 77 celdas y se repitieron solamente las 108 filas policy×roster×punto antiguas afectadas (3 celdas×4 puntos originales×3 rosters×3 políticas). Las cinco configuraciones estandarizadas de la fase 2 coincidieron en hashes con pi=19/14.449 y se reutilizaron. El detalle está en [`phase2_reuse_trace_audit.csv`](../../results/soc_triage_classifier_frontier_campaign/phase2_reuse_trace_audit.csv).

### Recuentos ejecutados

- 8 puntos nuevos de frontera: 5 originales evaluados bajo ambas prevalencias y 3 estandarizados bajo su prevalencia del artículo, **9.360 episodios de política**.
- 108 repeticiones justificadas para las tres celdas originales incompatibles bajo pi=40/14.449.
- 9.252 episodios de fase 2 reutilizados por compatibilidad de hash/configuración.
- Dataset analítico unido: **18.720 episodios**, 720 celdas de condición agrupadas por escenario, punto, carga, roster y semilla.

Las 40 semillas (272600000–272600039) ya se habían usado en fase 2. Esta campaña es una extensión exploratoria emparejada, no una validación independiente. Se mantuvieron rhoL1=.85/1.25, roster 6 L1, 2/3/4 L2, horizonte 24 h, drenaje 36 h, deadlines 1/4/12 h y WAPS ventana 4 h / umbrales 1.05/1.20. Cambiar L2 mantuvo constante la tasa absoluta de llegadas.

## Validación de integridad

[`validation_checks.json`](../../results/soc_triage_classifier_frontier_campaign/validation_checks.json) registra PASS: los hashes exógenos son únicos por condición emparejada; denominadores coinciden; TP+FP+FN+TN=admitidas; TP+FN=necesidad sintética; no hay deadlines sin madurar al corte. Se preservaron los CSV originales de la fase 2. No se modificó motor ni políticas; los cambios locales preexistentes añaden una referencia NOMINAL-REF no utilizada.

## Resultados principales por régimen

La comparación operativa se presenta como vector: resolución correcta y puntual, SLA de necesidad, detección de necesidad, servicio L2 innecesario por falsas alarmas, y backlog. No se impone un índice ponderado único. La frontera de Pareto operativa es descriptiva de medias y no equivale a superioridad inferencial. Intervalos de política y clasificador son contrastes pareados por semilla, t bilateral 95%, sin corrección por multiplicidad.

En la figura, las etiquetas numéricas remiten a [`figure_classifier_codebook.csv`](../../results/soc_triage_classifier_frontier_campaign/figure_classifier_codebook.csv); el orden de códigos se mantiene separado para cada definición de etiqueta.

### HLS-B/WAPS con carga L1 elevada y 3 analistas L2: etiquetas originales, pi=39/14.449

| Punto | pD | pFA | Correcta y puntual/admitida (IC95%) | SLA necesario | Servicio FP h / 1.000 | Backlog L2 terminal |
|---|---:|---:|---:|---:|---:|---:|
| original_rf_apc_symmetric | 0.7500 | 0.1618 | 0.5778 [0.5640, 0.5916] | 0.8763 | 132.1 | 0.0 |
| original_lr_apc_symmetric | 0.8000 | 0.2050 | 0.5349 [0.5231, 0.5467] | 0.8121 | 167.3 | 0.0 |
| original_bayesian_mlp_apc_symmetric | 0.8500 | 0.2056 | 0.5343 [0.5226, 0.5461] | 0.8114 | 167.8 | 0.0 |
| original_bayesian_mlp_a_symmetric | 0.8000 | 0.2301 | 0.5135 [0.5020, 0.5251] | 0.7801 | 187.4 | 0.3 |
| original_lsensemble_apc_symmetric | 0.7500 | 0.1510 | 0.5902 [0.5759, 0.6045] | 0.8945 | 123.9 | 0.0 |
| original_bayesian_mlp_apc_asymmetric_cM3cFA | 0.9250 | 0.3632 | 0.4130 [0.4039, 0.4221] | 0.6279 | 297.4 | 88.7 |
| original_rf_apc_asymmetric_cM3cFA | 0.9500 | 0.5279 | 0.3036 [0.2966, 0.3105] | 0.4614 | 436.3 | 231.1 |
| original_lightgbm_c_asymmetric_cM3cFA | 0.9750 | 0.6025 | 0.2551 [0.2487, 0.2616] | 0.3875 | 498.2 | 294.4 |
| original_bayesian_mlp_c_asymmetric_cM3cFA | 1.0000 | 0.7692 | 0.1482 [0.1440, 0.1525] | 0.2249 | 635.6 | 435.2 |

### HLS-B/WAPS con carga L1 elevada y 3 analistas L2: etiquetas originales, pi=40/14.449

| Punto | pD | pFA | Correcta y puntual/admitida (IC95%) | SLA necesario | Servicio FP h / 1.000 | Backlog L2 terminal |
|---|---:|---:|---:|---:|---:|---:|
| original_rf_apc_symmetric | 0.7500 | 0.1618 | 0.5777 [0.5639, 0.5916] | 0.8762 | 132.1 | 0.0 |
| original_lr_apc_symmetric | 0.8000 | 0.2050 | 0.5349 [0.5230, 0.5467] | 0.8121 | 167.3 | 0.0 |
| original_bayesian_mlp_apc_symmetric | 0.8500 | 0.2056 | 0.5343 [0.5225, 0.5461] | 0.8113 | 167.8 | 0.0 |
| original_bayesian_mlp_a_symmetric | 0.8000 | 0.2301 | 0.5135 [0.5020, 0.5250] | 0.7800 | 187.4 | 0.3 |
| original_lsensemble_apc_symmetric | 0.7500 | 0.1510 | 0.5901 [0.5759, 0.6044] | 0.8945 | 123.9 | 0.0 |
| original_bayesian_mlp_apc_asymmetric_cM3cFA | 0.9250 | 0.3632 | 0.4129 [0.4038, 0.4220] | 0.6278 | 297.4 | 88.7 |
| original_rf_apc_asymmetric_cM3cFA | 0.9500 | 0.5279 | 0.3035 [0.2966, 0.3105] | 0.4614 | 436.2 | 231.1 |
| original_lightgbm_c_asymmetric_cM3cFA | 0.9750 | 0.6025 | 0.2551 [0.2487, 0.2615] | 0.3875 | 498.1 | 294.5 |
| original_bayesian_mlp_c_asymmetric_cM3cFA | 1.0000 | 0.7692 | 0.1482 [0.1440, 0.1524] | 0.2249 | 635.6 | 435.2 |

### HLS-B/WAPS con carga L1 elevada y 3 analistas L2: etiquetas estandarizadas, pi=19/14.449

| Punto | pD | pFA | Correcta y puntual/admitida (IC95%) | SLA necesario | Servicio FP h / 1.000 | Backlog L2 terminal |
|---|---:|---:|---:|---:|---:|---:|
| standardized_lr_apc_symmetric | 0.6842 | 0.0081 | 0.6360 [0.6223, 0.6497] | 0.9671 | 6.1 | 0.0 |
| standardized_bayesian_mlp_apc_symmetric | 0.7042 | 0.0154 | 0.6353 [0.6215, 0.6490] | 0.9659 | 12.5 | 0.0 |
| standardized_lightgbm_apc_symmetric | 0.8421 | 0.0450 | 0.6328 [0.6189, 0.6467] | 0.9618 | 37.3 | 0.0 |
| standardized_lightgbm_c_symmetric | 0.8947 | 0.4051 | 0.3851 [0.3767, 0.3935] | 0.5856 | 334.0 | 125.2 |
| standardized_rf_apc_symmetric | 0.8421 | 0.1491 | 0.5933 [0.5791, 0.6076] | 0.8992 | 122.8 | 0.0 |
| standardized_rf_apc_asymmetric_cM3cFA | 0.9474 | 0.1938 | 0.5457 [0.5335, 0.5579] | 0.8284 | 158.9 | 0.0 |
| standardized_lsensemble_a_asymmetric_cM3cFA | 0.9649 | 0.2695 | 0.4821 [0.4711, 0.4931] | 0.7328 | 220.3 | 9.8 |
| standardized_lightgbm_apc_asymmetric_cM3cFA | 1.0000 | 0.3351 | 0.4334 [0.4240, 0.4429] | 0.6590 | 274.2 | 63.2 |

Las tablas completas por etiqueta, prevalencia, punto, carga, capacidad y política se encuentran en [`summary_by_condition.csv`](../../results/soc_triage_classifier_frontier_campaign/summary_by_condition.csv). Los contrastes de políticas, puntos de clasificador e interacciones están en `paired_policy_contrasts.csv`, `paired_classifier_contrasts.csv` y `classifier_organization_interactions.csv`.

## Comparación e incertidumbre

En todos los puntos de una condición, las políticas comparten por semilla las mismas alertas, necesidad oculta y recomendaciones; solo cambia el modo organizativo. Los contrastes classifier B−A comparan las mismas semillas y trazas. La interacción diferencia-en-diferencias compara cuánto cambia WAPS frente a D1 o P1 al cambiar el punto de clasificación. Las tablas incluyen el IC95% de cada contraste, n=40, sin ajuste por la cantidad de contrastes.

Para la métrica primaria de resolución correcta y puntual, WAPS−D1 tiene IC95% completamente positivos en 89/156 condiciones de punto×prevalencia×carga×roster, negativos en 17 y cruzan cero en 50; WAPS−P1 queda completamente positivo en 156/156, negativo en 0, y cruza cero en 0. Son conteos exploratorios sobre muchas comparaciones, no pruebas familiares confirmatorias. Los efectos de WAPS frente a las fijas varían por régimen; las tablas completas permiten ver signo y magnitud en cada estrato.

El Pareto operativo utiliza medias de cinco resultados (detección, correcta/puntual, SLA necesario, trabajo innecesario y backlog) por política y condición. [`operational_pareto.csv`](../../results/soc_triage_classifier_frontier_campaign/operational_pareto.csv) no elige ganador único. [`descriptive_classifier_choices.csv`](../../results/soc_triage_classifier_frontier_campaign/descriptive_classifier_choices.csv) separa la mayor BA de la mayor media de resolución correcta/puntual; esta última es solo descriptiva y debe interpretarse con sus contrastes emparejados.

## Falsas alarmas, detección y sobrecarga

En estas prevalencias bajas, un incremento de pFA puede multiplicar las recomendaciones y horas L2, mientras que las investigaciones positivas siguen siendo escasas. En consecuencia, mayor detección solo mejora la resolución correcta/puntual si esas tareas L2 adicionales llegan a tiempo y su beneficio compensa el servicio innecesario y la congestión. Los datos por condición incluyen las tasas realizadas, horas FP, FN omitidas, SLA, utilización y backlog; no se resta una penalización arbitraria a las falsas alarmas. La figura [`frontier_operational_tradeoff.png`](../../results/soc_triage_classifier_frontier_campaign/frontier_operational_tradeoff.png) muestra el compromiso para rhoL1=1.25 y nL2=3, con IC marginales visibles; las inferencias entre puntos deben leerse en los contrastes pareados.

## Resultado cuantitativo sobre la preferencia operativa

El mayor promedio de resolución correcta y puntual fue estable dentro de la cuadrícula evaluada: LSEnsemble A+C simétrico encabezó las 36 combinaciones de etiqueta original (2 prevalencias × 2 cargas L1 × 3 plantillas L2 × 3 políticas); LR A+C simétrico encabezó las 18 combinaciones estandarizadas. En las 54 combinaciones, el punto con mayor BA publicada no fue el de mayor media de resolución correcta y puntual. Esto describe el máximo dentro de los puntos muestreados, no una superioridad inferencial universal ni una selección válida para una prevalencia operativa desconocida.

La frontera de medias operativas (cinco objetivos simultáneos) retuvo siete de nueve puntos originales en cada una de sus 36 condiciones. En el grupo estandarizado retuvo cinco puntos en 15 condiciones y seis en tres condiciones, de ocho evaluadas. La aparición/desaparición de RF A+C simétrico en tres condiciones refleja una frontera de medias sensible a esa condición; no es evidencia confirmatoria de un cambio de preferencia. Los objetivos permanecen en tensión: más detección puede coexistir con más trabajo FP, menos resoluciones puntuales y mayor backlog.

Un contraste ilustrativo, fijado aquí como descripción de la cuadrícula y no como prueba confirmatoria, es rhoL1=1.25, tres analistas L2, WAPS y etiquetas originales con pi=39/14.449. Frente a LSEnsemble A+C simétrico (pD=.75, pFA=.151), Bayesian MLP A+C asimétrico (pD=.925, pFA=.3632) elevó la detección sintética de necesidad de .666 a .805, pero el servicio innecesario pasó de 123.9 a 297.4 h por 1,000 alertas, el SLA de necesidades bajó de .895 a .628 y la resolución correcta/puntual cayó de .5902 a .4130. La diferencia pareada LSEnsemble menos Bayesian MLP fue +.1772 [IC95% .1700, .1844], n=40 semillas. El backlog L2 terminal aumentó de 0 a 88.7 tareas medias. Así, en este régimen la detección adicional no compensó la carga inducida para el resultado puntual, aunque atendió más necesidades en términos de detección.

La ganancia de WAPS sobre políticas fijas dependió del punto de clasificación. En ese mismo estrato WAPS−D1 fue +.0853 [+.0719,+.0988] para LSEnsemble y +.0572 [+.0473,+.0670] para Bayesian MLP asimétrico. La diferencia-en-diferencias (cambio en WAPS−D1, LSEnsemble menos Bayesian MLP) fue +.0282 [+.0239,+.0325]. Es evidencia exploratoria de interacción dentro del simulador y bajo sus supuestos, separada del efecto directo del punto de clasificador; no implica que WAPS rescate la configuración de alta falsa alarma. En las 1,200 interacciones por métricas y estratos, 913 IC95% no ajustados excluyeron cero y el mayor valor absoluto de la media fue .0762. La multiplicidad hace que esos recuentos sean descriptivos; no deben leerse como una tasa de hallazgos confirmados.

La lectura global es, por tanto, condicionada. En el objetivo primario de resolución correcta/puntual no se observó cambio del máximo medio entre carga .85/1.25, 2/3/4 analistas L2 y las tres organizaciones, dentro de cada definición de etiquetas. Sí aparecen intercambios operativos que pueden cambiar cuál punto es aceptable al imponer requisitos mínimos de detección, límites de trabajo innecesario o SLA. Sin preferencias/umbrales operativos justificados, los datos no identifican un clasificador único preferible. La evidencia apoya que BA por sí sola no basta para ordenar los puntos según este desenlace sintético y que la alta pFA puede ser material bajo presión de capacidad; no establece que los modelos reales causarían esos efectos en alertas reales.

## Sensibilidad a la prevalencia original

La diferencia entre las prevalencias 39/14.449 y 40/14.449 se evalúa con semillas emparejadas en [`prevalence_sensitivity_paired.csv`](../../results/soc_triage_classifier_frontier_campaign/prevalence_sensitivity_paired.csv). La mayoría de las realizaciones se conserva, pero tres de 80 celdas semilla×carga tienen hashes de recomendación distintos y se repitieron. Para resolución correcta y puntual, las 162 diferencias pareadas tienen IC95% que incluyen cero y la mayor diferencia media absoluta es 0.0000407. Esa pequeña sensibilidad simulada no resuelve el origen documental de la discrepancia ni justifica sustituir el conteo auditado por el índice redondeado. Las conclusiones de régimen dependen también de la hipótesis de necesidad técnica sintética y no reflejan necesariamente prevalencias operativas de investigación L2.

## Positivos escasos y limitaciones

En las 240 trazas únicas hay 341 alertas con necesidad sintética entre 170040 admitidas; la fracción de trazas semilla con cero necesidades es 0.275. En el conjunto estandarizado y especialmente por semilla, numerosos episodios contienen cero o muy pocos positivos. Las tasas pD por seed son, por ello, discretas e imprecisas; no se debe confundir el pD objetivo publicado con el pD realizado. La incertidumbre t por semillas resume la variabilidad simulada, pero no corrige el bajo número de casos positivos ni la falta de errores estratificados por clase.

Los errores del clasificador siguen supuestos intercambiables entre tipos de tarea; la necesidad es oculta y sintética; las recomendaciones se aceptan automáticamente; los tiempos, elegibilidad y capacidades son del simulador; y no hay dependencia de errores por proyecto ni respuesta humana. Las tablas comparan puntos agregados publicados y no recrean decisiones individuales de los modelos SOCTRA. Los resultados son exploratorios, sin ajuste de multiplicidad y con prevalencia original parcialmente inferida.

## Conclusión

En la matriz sintética emparejada, BA o pD no bastaron para ordenar las configuraciones por resolución correcta y puntual. Los puntos de menor pFA tuvieron los mayores promedios de ese desenlace en cada definición de etiqueta, y los puntos de alta detección/alta falsa alarma mostraron pérdidas importantes bajo sobrecarga L1 incluso con WAPS. La ventaja relativa de organización varió según el punto de clasificación, aunque la interacción es exploratoria y no ajustada por multiplicidad. Los objetivos operativos conservan compromisos; no se identifica una configuración universal ni se demuestra impacto en GMV-CERT. Las conclusiones están condicionadas a prevalencias auditadas/inferidas, necesidad técnica sintética, aceptación automática, errores intercambiables, servicios y recursos del simulador y solo 40 semillas con positivos escasos.

## Reproducción

- Configuración fija: `config/campaign.json`.
- Runner con auditoría de reutilización y hashes: `run_campaign.py`.
- Resumen pareado, fronteras y figura: `summarize_campaign.py`.
- Validación y manifiesto: `results/soc_triage_classifier_frontier_campaign/validation_checks.json` y `reproducibility_manifest.json`.
- CSV de episodios unido y CSVs de análisis: `results/soc_triage_classifier_frontier_campaign/`.

Recrear la extensión desde el estado actual requiere ejecutar `python studies/soc_triage_classifier_frontier_campaign/run_campaign.py`; el análisis posterior es `python studies/soc_triage_classifier_frontier_campaign/summarize_campaign.py`. El subconjunto sintético de Phase 2 requerido para verificar y reutilizar episodios se incluye como `results/soc_triage_classifier_frontier_campaign/phase2_reuse_source_episodes.csv`.
