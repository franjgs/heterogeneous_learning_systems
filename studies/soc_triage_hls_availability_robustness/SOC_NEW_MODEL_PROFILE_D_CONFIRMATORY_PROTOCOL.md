# Protocolo confirmatorio: ventaja de HLS-B en perfil D — NEW MODEL

> **NEW MODEL / MODELO NUEVO.** El OLD MODEL / MODELO VIEJO y el manuscrito LaTeX actual quedan fuera de este protocolo. Ninguna evidencia confirmatoria histórica del OLD MODEL se incorpora aquí.

## Registro y congelación

Este protocolo queda fijado antes de ejecutar ninguna de las semillas confirmatorias. Commit de origen: `1eade759c6fb8f46275a797d627f76d9a3a1acfd`, rama `research/soctra-hls-new-model`. La configuración congelada y versionada es [`config/SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY.json`](config/SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY.json); su SHA-256 debe ser `10733bf5f5a890e312163f96028b4bdc3b1cf36da3e278f6411a7c29b8535efc`, igual al JSON D del piloto exploratorio. SHA-256 de roster/organización: `9c055bf7341e36d71788cd7cc9b8d6a7220ddd1889d7972cf11f38a0175fbc9b`.

El protocolo y la copia congelada se guardan en un commit propio **antes** de seleccionar/ejecutar el bloque de resultados. No se cambiarán hipótesis, estimando, configuración, semillas ni pruebas tras observar resultados. Si una incidencia técnica obliga a desviarse, se registrará sin reemplazar ni seleccionar episodios por su resultado.

## Pregunta e hipótesis primaria conjunta

En el perfil D del NEW MODEL, se contrasta si HLS-B obtiene mayor R/N terminal medio que **ambas** políticas fijas:

- (H_{01}: E[\Delta_{B,D1}]\leq0) frente a (H_{11}: E[\Delta_{B,D1}]>0), donde \(\Delta_{B,D1}=R/N_{HLS-B}-R/N_{D1}\).
- (H_{02}: E[\Delta_{B,P1}]\leq0) frente a (H_{12}: E[\Delta_{B,P1}]>0), donde \(\Delta_{B,P1}=R/N_{HLS-B}-R/N_{P1}\).
- La afirmación conjunta requiere rechazar ambos nulos. Se usa una prueba de intersección-unión: cada contraste unilateral pareado tiene \(\alpha=0.05\); no se divide alfa, pues la hipótesis nula conjunta es la unión de los dos nulos y solo se declara superioridad si ambos se rechazan.

La unidad independiente es el **episodio/semilla**. Para cada contraste se aplicará la prueba t de Student unilateral a las diferencias pareadas por semilla. Se informarán el estadístico t, grados de libertad, valor p unilateral, media, desviación estándar muestral, IC t bilateral del 95%, proporción y número de semillas con diferencia positiva, y diferencia relativa respecto de la media del control. La aproximación t presupone que la media de las diferencias es inferible con esta distribución; asimetría/outliers se describirán como limitación, sin cambiar la prueba primaria después de ver los datos.

No se fija un umbral de relevancia práctica o económica: no hay uno validado. Los efectos se expresarán en unidades absolutas de R/N y como cambio relativo descriptivo.

## Dimensionamiento previo

Solo para planificar, se recuperan las 12 diferencias por semilla del piloto exploratorio D (semillas `2026112801–2026112812`); no se incorporarán al análisis confirmatorio:

| Contraste exploratorio | Media Δ | DE muestral |
|---|---:|---:|
| HLS-B − D1 | 0.0085523 | 0.0056572 |
| HLS-B − P1 | 0.0051998 | 0.0021036 |

Se usa la mayor DE observada, 0.0056572, como base conservadora de variabilidad común. Para robustez, la tabla usa una potencia marginal objetivo del 95% para cada prueba unilateral (esto garantiza por la cota de unión al menos 90% de potencia conjunta, sin asumir independencia entre contrastes), \(\alpha=0.05\), prueba t no central emparejada, y efectos de planificación anclados al efecto menor observado y a la mitad de este. La mitad es una sensibilidad, no un umbral científico mínimo.

| DE supuesta | Efecto de planificación Δ | n aproximado requerido por contraste para 95% de potencia |
|---:|---:|---:|
| 1× DE máxima observada = 0.005657 | 0.00520 | 15 |
| 1.5× = 0.008486 | 0.00520 | 31 |
| 2× = 0.011314 | 0.00520 | 53 |
| 2× = 0.011314 | 0.00260 (mitad del menor efecto exploratorio) | 207 |

Se eligen **60 episodios**: supera el requerimiento de 53 en el escenario de variabilidad duplicada y efecto de planificación 0.00520, sin asumir que el efecto exploratorio se mantenga ni inflar el tamaño automáticamente a 100. Bajo ese escenario la potencia marginal calculada excede 95% para cada contraste y la cota conservadora de potencia conjunta excede 90%. La potencia caería si el efecto fuera menor; la sensibilidad muestra que detectar la mitad del menor efecto exploratorio con esa variabilidad requeriría una campaña mucho mayor. El cálculo es aproximado por el modelo de diferencias normales y sirve para dimensionamiento, no garantiza el resultado ni convierte el efecto exploratorio en efecto verdadero.

## Escenario y estimando congelados

Se utilizará exactamente el perfil D exploratorio, copia congelada arriba: admisión 192 h; ordinario `[0,96)` h con \(\rho_{L1}=0.85\), sobrecarga `[96,144)` h con \(\rho_{L1}=1.25\), recuperación `[144,192)` h con \(\rho_{L1}=0.65\); evaluación terminal a 360 h (168 h de drenaje desde fin de admisión). Tasas por clase, organización, profesionales, disponibilidad individual 24x7, elegibilidad, competencia, eficiencia, servicios, deadlines, mezcla, referencia sintética de escalado, clasificador, flujo `triage_single_investigation`, `alpha=0.50`, `beta=0`, `gamma=1` y parámetros de política permanecen exactamente como en el perfil D congelado.

Se comparan D1, P1 y HLS-B/WAPS existentes, sin modificar reglas ni parámetros adaptativos. Cada episodio comparte una traza exógena idéntica entre las tres políticas, incluidas llegadas, clase, severidad, dificultad, referencia oculta, recomendación, deadline y realizaciones ambientales cuando proceda. Solo las decisiones/endógenos propios de cada política pueden diferir.

La métrica primaria terminal por episodio es:

\[
R/N = \frac{\sum_{a\in\mathcal A} q^{modelada}_a\,\mathbf 1\{t_{fin,a}\le d_a,\ t_{fin,a}\le 360h\}}{|\mathcal A|},
\]

donde \(\mathcal A\) son todas las alertas admitidas, \(q^{modelada}_a\) conserva la calidad esperada basada en competencia que usa el NEW MODEL, \(d_a\) es el deadline absoluto y las alertas tardías o pendientes contribuyen cero al numerador. No se redefine calidad ni denominador.

## Semillas y número de ejecuciones

Se fijan 60 semillas consecutivas `2026112901–2026112960`, idénticas entre políticas. Este bloque no se solapa con bloques de semillas documentados en el repositorio hasta el commit de origen, incluidos `2026112701–2026112710`, `2026112801–2026112812`, `998001`, `910000/920000/930000` y `711000000–711000399`; la búsqueda de `20261129` en las declaraciones versionadas no encontró usos previos. No se seleccionarán, reemplazarán ni descartarán semillas según sus resultados. Total previsto: **180 episodios** (60 semillas × 3 políticas).

La campaña es una validación confirmatoria solo para el perfil sintético D y sus supuestos. El piloto exploratorio, aunque informó contrastes positivos, se excluye completamente de las pruebas e intervalos confirmatorios.

## Resultados secundarios predefinidos

Se informarán descriptivamente (sin reclasificarlos como primarios): R/N por cohorte de llegada (ordinario `[0,96)`, sobrecarga `[96,144)`, recuperación `[144,192)`), SLA global y por cohorte, calidad modelada entre completadas, esperas, colas/backlog, utilización L1/L2 y estados/transiciones de HLS-B. Cohortes se atribuyen por hora de llegada y se siguen hasta el mismo corte terminal. Episodios son las unidades; no se tratarán alertas ni cohortes de una misma semilla como réplicas independientes. No se usarán contrastes secundarios para rescatar una hipótesis primaria no confirmada.

## Integridad y límites

Antes del análisis se comprobarán identidad de trazas y ambiente entre políticas por semilla, conteos de alerta y TP/FP/TN/FN, una sola investigación por alerta, rutas TP/FP a L2 y TN/FN a L1, deadlines, configuración/roster iguales, métricas recomputables, ausencia de fugas de información oculta, estados SLA y reproducibilidad de ejecución fijada. Se reportarán alertas pendientes, sin eliminarlas de los denominadores.

La evidencia será sobre un modelo sintético, un perfil D prefijado y el proxy de calidad vigente; no valida empíricamente un SOC real, no generaliza automáticamente a otras organizaciones/demandas, ni ofrece por sí sola una explicación causal de las transiciones HLS-B. OLD MODEL y NEW MODEL son generaciones organizativas distintas y sus magnitudes no se combinarán.
