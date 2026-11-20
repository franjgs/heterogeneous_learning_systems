# Guía de evidencia para el artículo SOCTRA-HLS

**Uso:** transferencia científica al PI, CE y redactor LaTeX. Las cifras son del simulador SOC sintético; no son mediciones del rendimiento de GMV-CERT. Esta guía no sustituye los [fundamentos](SOC_FOUNDATIONS_AND_MODEL.md), la [consolidación anterior a HLS-A](SOC_SCIENTIFIC_CONSOLIDATION.md) ni los protocolos y resultados originales.

## Preguntas y niveles de evidencia

1. **Organización bajo carga:** ¿cambia el rendimiento esperado por alerta al sustituir D1 por una regla temporal P1, con plantilla y trazas iguales? La [validación D1/P1](SOC_CONFIRMATORY_RESULTS.md) responde afirmativamente **solo** para la sobrecarga sintética prefijada; en cargas menores P1 puede empeorar.
2. **Complementariedad:** ¿son preferibles D1 y P1 en regímenes distintos? Las 100 semillas confirmatorias por carga muestran signo negativo de P1−D1 en ρ=0,85/1,00/1,10 y positivo en 1,15/1,25; el umbral exacto no se ha estimado.
3. **Selección adaptativa:** ¿puede un selector causal de D1/P1 mejorar el promedio de una distribución de escenarios definida? La [validación HLS-B](SOC_HLSB_VALIDATION_RESULTS.md) responde afirmativamente para **cuatro escenarios sintéticos equiponderados**, no para cada transición ni para un SOC real. HLS-A fue un piloto funcional con resultado negativo en las transiciones examinadas.

La primera pregunta estudia políticas fijas; la tercera estudia **selección de mecanismos heterogéneos**. No se ha probado integración experimental de predicciones de triaje SOCTRA con estas decisiones organizativas.

## Modelo, políticas y estimando

El motor de eventos `src/hls/rq1_allocation.py::simulate`, acoplado a `src/hls/rq1_l1_l2.py::simulate_l1_l2`, recibe alertas con llegada, clase y deadline, asigna analistas elegibles L1/L2 con servicio no preemptivo y evalúa escaladas en la finalización L2. Las colas no tienen límite ni descarte por capacidad. El triaje y escalado de las campañas organizativas son **hipotéticos**. Plantilla, competencias, elegibilidad, velocidades, servicios y SLA terminales no están calibrados con GMV-CERT. [GMV-CERT](GMV_CERT_OPERATIONAL_REFERENCE.md) ofrece contexto cualitativo; SOCTRA aporta información de alertas y triaje, no medidas de competencia o duración de trabajo humano.

Para cada alerta admitida (a), (p_a=c_{i(a),k(a)}(1-0,35,difficulty_a)) es la probabilidad modelada de resolución correcta de su analista terminal. El rendimiento en el corte (c\in\{H,H+D\}) es

\[
R(c)/N=\frac1N\sum_{a=1}^{N}p_a\,\mathbf1\{completion_a\le d_a,\ completion_a\le c\},
\]

con (H=D=24\) h y (N) alertas admitidas; una pendiente o tardía aporta cero. Para escaladas, `completion` corresponde a L2. **Calidad entre completadas** usa otro denominador; **SLA** no pondera por (p_a). El coste de coordinación no se resta de R/N en estas comparaciones y no se ha medido operativamente.

| Política | Regla efectiva e información | Evidencia y límite |
|---|---|---|
| D1 | Analistas libres en orden aleatorio reproducible; cada uno elige alerta elegible maximizando riesgo temporal previsto, competencia propia y, en empate, escasez de otros elegibles. No conoce competencias exactas de compañeros ni planifica llegadas futuras. | Baseline descentralizado congelado; interpretación plausible de GMV, no réplica validada. |
| P1 | Analistas libres por ID; cada uno elige entre sus alertas elegibles la menor holgura (d_a-t-s_{ia}\), con deadline/llegada/ID como desempates. | Prioridad temporal local, sin coste de coordinación. |
| P2/P3 | P2 prioriza competencia; P3 escasez de elegibilidad y luego competencia. | Comparación exploratoria, sin beneficio conjunto bajo sobrecarga en la matriz estudiada. |
| P4/P5 | Matching/activación selectiva de la formulación P1–P5; no son C ni HLS-A/B. | No hubo asignaciones múltiples en las trazas principales: no atribuir a matching sus diferencias. |
| HLS-A | Presión (z(t)=\max_k[|B_k|/|E_k|+\sum_{a\in Q_k}\min_{i\in E_k}s_{ia}/(|E_k|\bar s_k)]\); histéresis 2/3 de desarrollo. Conmuta entre los despachadores originales D1/P1 por pool. | Funcional, piloto y [diagnóstico directo](SOC_HLS_ADAPTIVE_DIAGNOSTIC.md); sin ventaja adaptativa demostrada en transiciones. |
| HLS-B | \(\widehat\rho_w(t)=\widehat\lambda_w(t)/\mu_{equipo}\), \(\widehat\lambda_w(t)=\#\{a:t-w<arrival_a\le t\}/w\). Ventana (w=4\) h; inicia D1, activa P1 si \(\widehat\rho\ge1,20\), retorna a D1 si \(\widehat\rho\le1,05\), conserva modo entre umbrales. Capacidad LP fluida calculada antes del episodio con roster, servicio, elegibilidad y mezcla configurada. | Selector causal congelado tras [desarrollo](SOC_HLSB_DEVELOPMENT_RESULTS.md), [protocolo](SOC_HLSB_VALIDATION_PROTOCOL.md) y validación independiente. No recibe ρ nominal ni calendario; no interrumpe tareas ni aprende en línea. |

Las reglas implementadas están en `src/hls/rq1_allocation.py::_dispatch_d1`, `_dispatch_local_priority`, `hlsa_pressure` y `simulate`; la parametrización L1/L2 se transmite desde `src/hls/rq1_l1_l2.py::simulate_l1_l2`. HLS-A/B seleccionan un despachador existente, sin modificar D1/P1.

## Diseño y resultados que pueden citarse

| Evidencia | Diseño | Resultado defendible |
|---|---|---|
| [A0](SOC_A0_BASELINE_CONGESTION.md) y [debilidades D1](SOC_A0_D1_ORGANIZATIONAL_WEAKNESSES.md) | 30 semillas por carga para congestión; 6 por carga para contrastes locales | L1 se congestiona cerca/sobre su capacidad fluida sintética de 28,42 alertas/h; a ρ=1,25 hubo 1.484 contrastes locales de orden positivos en 5.045 decisiones L1, **no** ganancias terminales sumables. |
| [D1/P1–P5 exploratorio](SOC_POLICY_COMPARISON_RESULTS.md) | 20 semillas pareadas por celda, H=D=24 h | A ρ=1,25, R/N D1=0,5280 y P1=0,6278, diferencia +0,0998 [0,0825; 0,1172]. P2/P3 empeoraron. Sin matching múltiple observado en P4/P5. |
| [D1/P1 confirmatorio](SOC_CONFIRMATORY_PROTOCOL.md), [resultado](SOC_CONFIRMATORY_RESULTS.md) | 100 semillas nuevas; primario unilateral prefijado ρ=1,25 | D1=0,5180; P1=0,6162; diferencia +0,0982 [0,0891; 0,1073], (p=2,57\times10^{-39}\). P1 ganó 98/100 episodios. SLA terminal 0,7556→0,9663; calidad esperada entre completadas 0,6749→0,6378. |
| [HLS-A](SOC_HLS_ADAPTIVE_SUPERVISOR.md), [diagnóstico](SOC_HLS_ADAPTIVE_DIAGNOSTIC.md) | 6 semillas de desarrollo; tres umbrales; contraste directo de 24 episodios con/sin instrumentación | HLS-A 2/3 no superó D1 en los dos episodios variables del piloto; z activó P1 en muchas épocas sin contraste local favorable identificable. No hubo validación independiente de HLS-A como candidato primario. |
| [HLS-B validación](SOC_HLSB_VALIDATION_RESULTS.md) | 100 semillas nuevas por escenario, cuatro escenarios equiponderados, regla congelada | Media D1=0,6259 y HLS-B=0,6541; diferencia +0,02820 [0,02526; 0,03115], (p) unilateral (4,62\times10^{-35}\), mejora relativa de medias ≈4,51 %, 98/100 semillas positivas. En ρ=1,25: +0,1106 [0,1036; 0,1175]. En transiciones: +0,0002 [−0,0041; 0,0045] y +0,0034 [−0,0011; 0,0078], sin ventaja individual concluyente. |

Los IC exploratorios y confirmatorios pertenecen a diseños y semillas distintos; no se deben combinar. La media de HLS-B pondera **los cuatro escenarios con el mismo peso por semilla** y no estima la prevalencia de esos regímenes en GMV. La activación P1 tardó 3,87 h de media tras el cambio a sobrecarga; el retorno a D1, 1,88 h entre los episodios aún en P1 al comenzar recuperación. Estos retardos describen conmutación observada, sin identificar por sí solos la causa del efecto terminal.

## Material para tablas, figuras y reproducción

| Uso en manuscrito | Fuente publicable en Git | Fuente completa local, regenerable |
|---|---|---|
| Tabla de congestión y debilidades D1 | [A0](SOC_A0_BASELINE_CONGESTION.md), [diagnóstico](SOC_A0_D1_ORGANIZATIONAL_WEAKNESSES.md), `evidence/soc_a0_weaknesses_summary.json`, [curvas de carga](figures/soc_a0_arrival_load.svg) y [evolución de cola](figures/soc_a0_queue_evolution.svg) | `results/soc_a0_baseline_congestion/summary_metrics.csv`, `results/soc_a0_weaknesses/summary.json` |
| Tabla exploratoria D1/P1–P5 | [informe](SOC_POLICY_COMPARISON_RESULTS.md), `evidence/soc_policy_comparison_rn_terminal.csv` | `results/soc_policy_comparison/summary.csv` |
| Tabla/figuras confirmatorias D1/P1 | [informe](SOC_CONFIRMATORY_RESULTS.md), `evidence/soc_confirmatory_test_results.json`, [R/N frente a carga](figures/soc_confirmatory_rn_by_load.svg), [diferencia pareada](figures/soc_confirmatory_paired_effect.svg), [SLA y calidad](figures/soc_confirmatory_sla_quality.svg) | `results/soc_confirmatory_d1_p1/summary.csv`, `paired.csv`, `strata.csv` |
| Tabla HLS-B, incertidumbre y cohortes | [informe](SOC_HLSB_VALIDATION_RESULTS.md), `evidence/soc_hlsb_validation_statistics.json` | `results/soc_hlsb_validation/episodes.csv`, `strata.csv`, `modes.csv` |

Los artefactos locales completos se regeneran **desde la raíz del repositorio**, con `pip install -e '.[soc-calibration]'`, mediante los scripts `run_a0_baseline_congestion.py`, `analyze_a0_weaknesses.py`, `run_soc_policy_comparison.py`, `run_soc_confirmatory.py`, `run_soc_hlsa_pilot.py`, `run_soc_hlsa_direct_diagnostic.py`, `run_soc_hlsb_development.py`, `run_soc_hlsb_validation.py` y `summarize_soc_hlsb_validation.py` del directorio de este estudio. Usar `PYTHONPATH=src:.` y consultar cada JSON de `config/` antes de ejecutar. Los scripts escriben en `results/`, excluido de Git. El diagnóstico directo HLS-A genera más de 350 MB: se publican su método y cifras, no sus snapshots. La ausencia de CSV por episodio en Git impide recalcular directamente los IC desde un checkout sin ejecutar los scripts; las tablas agregadas y los estadísticos exactos sí están versionados. Los SVG son figuras **sintéticas** y no contienen datos SOCTRA privados.

## Afirmaciones permitidas y límites de redacción

**Permitidas:** en el modelo y escenarios indicados, la elección de política cambia el compromiso SLA/calidad; P1 mejora R/N bajo sobrecarga sintética prefijada; HLS-B mejora el estimando de cuatro escenarios sintéticos equiponderados frente a D1; HLS-A no demostró ventaja adaptativa en sus dos transiciones piloto. La ausencia de matching múltiple en las trazas limita la interpretación de P4/P5.

**Evitar:** «HLS-B mejora las dos transiciones», «aprende en línea», «coordina analistas», «mejora GMV-CERT», «SOCTRA mide competencias humanas», «P4 demostró beneficio de matching», «P1 es universalmente superior», o atribuir el efecto de HLS-B exclusivamente a sus retardos de conmutación. El coste operativo real del supervisor no está cuantificado. Las predicciones SOCTRA no se integraron experimentalmente con la asignación.

## Technical handoff for the LaTeX author (English)

The SOC study is a synthetic, event-driven evaluation of organizational choices among heterogeneous analysts. D1 is a frozen decentralized pull baseline; P1 orders locally by predicted post-service slack. A preregistered, paired 100-seed comparison at nominal load ρ=1.25 found a terminal expected-correct-and-on-time fraction of 0.5180 for D1 and 0.6162 for P1 (mean difference 0.0982, 95% CI [0.0891, 0.1073], one-sided (p=2.57\times10^{-39}\)). P1 improves timeliness while reducing modeled quality among completed tasks. In lower-load scenarios its net effect can be negative.

HLS-B is a fixed, interpretable selector between the unchanged D1 and P1 dispatch rules. It estimates arrival rate from a causal four-hour window, divides by modeled team capacity, switches to P1 at 1.20 and back to D1 at 1.05. On a separate 100-seed validation over four equally weighted synthetic scenarios, its terminal outcome averaged 0.6541 versus 0.6259 for D1 (paired difference 0.02820, 95% CI [0.02526, 0.03115], one-sided (p=4.62\times10^{-35}\)). The aggregate gain is driven by stationary overload; neither time-varying scenario alone showed a conclusive improvement over D1. This is **adaptation without online learning**, not empirical validation of a deployed SOC. SOCTRA's prior triage findings and the organizational simulation can be related conceptually, but their decisions were not integrated experimentally.
