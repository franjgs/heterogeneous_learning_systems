# Diagnóstico del supervisor HLS-A

> **Actualización con instrumentación directa.** El análisis basado en `AllocationSession` que aparece más abajo es histórico y queda **superado** por los snapshots tomados dentro de `simulate`. Su conclusión de detener la sublínea no se mantiene. Las cifras vigentes y la recomendación están en esta sección.

## Diagnóstico directo sobre las trayectorias originales

Se añadió a `simulate` un colector opcional `diagnostic_trace`, desactivado por defecto. En cada época HLS-A, antes de ejecutar la asignación, registra tiempo, modo, (z), libres/ocupados, cola con clase/deadline/llegada, parejas factibles con duración, competencia y holgura, propuestas D1/P1 y asignación ejecutada. El runner une la prioridad de la alerta sintética. La propuesta D1 usa una copia exacta del estado del RNG y no consume el generador real; P1 consulta el mismo estado sin mutarlo. No se alteraron D1, P1 ni la conmutación HLS-A.

Se repitieron las **mismas seis semillas de desarrollo** en ρ=1,00, ρ=1,25 y ambos escenarios variables. Para cada uno de los 24 episodios se comparó la ejecución con diagnóstico activado y desactivado: el objeto `L1L2Result` completo fue idéntico, incluidos épocas HLS-A, asignaciones, escalado, SLA, R/N y estado final. Además, R/N coincidió exactamente con el CSV del piloto. Se registraron **17.646 épocas L1 y 883 L2**. La prueba unitaria de equivalencia con/sin diagnóstico pasó junto con 14 pruebas relevantes adicionales. Los artefactos son `direct_diagnostic.jsonl` y `direct_equivalence.csv` en `results/soc_hlsa_pilot/`; el runner es `run_soc_hlsa_direct_diagnostic.py`.

El contraste local ΔV se define solo si hay **un analista libre** y D1/P1 eligen **dos alertas distintas** elegibles para él. Se comparan los órdenes exactos de esas dos alertas con (V(j\to k)=p_{ij}1[t+s_{ij}\le d_j]+p_{ik}1[t+s_{ij}+s_{ik}\le d_k]), usando (p_{ij}) igual a la competencia modelada del analista. Si hay varios analistas libres, falta una alerta alternativa, o las elecciones coinciden, el contraste se marca **no evaluable**. Su signo es una oportunidad local observable, no un resultado terminal; no se suman valores entre épocas.

| Escenario L1 | Épocas | P1 | Desacuerdo D1/P1 | Contraste evaluable | ΔV>0 | ΔV<0 | ΔV=0 |
|---|---:|---:|---:|---:|---:|---:|---:|
| ρ=1,00 | 4.220 | 2.860 (67,8 %) | 1.978 (46,9 %) | 1.919 | 0 | 0 | 1.919 |
| ρ=1,25 | 5.169 | 4.828 (93,4 %) | 2.849 (55,1 %) | 2.833 | 35 | 34 | 2.764 |
| Ráfaga/recuperación | 4.218 | 2.786 (66,1 %) | 1.994 (47,3 %) | 1.872 | 0 | 0 | 1.872 |
| Sobrecarga/recuperación | 4.039 | 3.474 (86,0 %) | 2.217 (54,9 %) | 2.200 | 0 | 0 | 2.200 |

En L2 hubo 883 épocas, ninguna en modo P1, y 359 desacuerdos; solo 19 contrastes de dos servicios fueron evaluables, todos con ΔV=0. En L1, P1 se activó **sin cambiar la propuesta** en 1.267/2.860 épocas P1 de ρ=1,00 (44,3 %), 2.087/4.828 en ρ=1,25 (43,2 %), 1.124/2.786 en ráfaga (40,3 %) y 1.448/3.474 en sobrecarga inicial (41,7 %). Entre los contrastes evaluables ejecutados en modo P1, hubo 34 con ΔV<0 en ρ=1,25 y cero en los otros tres escenarios; ninguna oportunidad evaluable con ΔV>0 quedó en modo D1. Los muchos empates no prueban que las políticas sean equivalentes en trayectoria: asignar una alerta distinta cambia qué trabajo y qué analista quedan disponibles después.

En ρ=1,25, la media de ΔV entre los 2.833 contrastes evaluables fue **+0,0068** correctas esperadas por dos servicios; 35 valores positivos y 34 negativos, con el resto nulo. La mediana de (z) fue 23,45 cuando ΔV>0 y 22,14 cuando ΔV<0: la presión elevada no separó bien los signos. En ρ=1,00, (z) medio durante P1 fue 5,03 y durante D1 1,67, pero **todos** los contrastes evaluables empataron en ΔV. La regla actual detecta cola/ocupación y activa P1 sin evidencia local de orden recuperable en ese régimen. Los cambios de carga variables tampoco mostraron ΔV positiva en los contrastes evaluables; la cola residual y la histéresis mantienen P1 activo durante parte de la recuperación, sin demostrar que esa persistencia cause por sí sola la pérdida terminal.

Ejemplos reproducibles, semilla sintética `261170004`, ρ=1,25: en (t=22,880) h, (z=29,19), un analista L1 con competencia 0,72/0,75 y servicios 0,18/0,33 h puede escoger una alerta `top5` con 0,42 h restantes o una `tail` con 0,78 h. P1 elige la primera y el contraste de dos servicios da ΔV=+0,72. En (t=23,105) h, (z=29,38), otro analista tiene dos alertas con 0,45/0,36 h restantes, servicios 0,24/0,22 h y competencias 0,87/0,75: P1 elige la segunda, con ΔV=−0,12. Ambos snapshots tienen presión alta; los resultados locales divergen. Los IDs completos permanecen solo en el JSONL sintético.

**Conclusión vigente:** el indicador de congestión es insuficiente para discriminar beneficio local de P1, pero el contraste de dos servicios raramente distingue las reglas y no explica por sí solo la diferencia de R/N terminal. Hay información observable (holguras, duraciones y competencias) para estudiar una señal más informativa; **todavía no hay evidencia suficiente para fijar cuál ni para atribuir la pérdida a un umbral concreto**. Mantener HLS-A como línea diagnóstica abierta, sin cambiar la regla ni declarar mejora adaptativa. El análisis no justifica detenerla por una reconstrucción fallida.

**Alcance:** análisis de desarrollo de la regla (l=2,h=3), seis semillas por cinco escenarios. No es validación confirmatoria. No se modificó HLS-A, D1, P1 ni el motor. El piloto original conserva `mode_history.csv`; las trazas detalladas por época no se guardaron.

## Método y evidencia disponible

El supervisor calcula el indicador por pool en cada época de asignación. Para la auditoría se usaron sus modos y niveles de presión guardados en `results/soc_hlsa_pilot/mode_history.csv`. Para recuperar estados faltantes se hizo una reproducción diagnóstica con `AllocationSession`, mismas semillas, alertas, umbrales y generación. Antes de cada despacho se calcularon propuestas sombra D1/P1 sobre la cola presente, copiando el estado del RNG para no consumirlo. Se guardaron los estados y propuestas en `diagnostic_epochs.csv` y `diagnostic_disagreements.csv`.

La reproducción no igualó el piloto: por ejemplo, ρ=1,00 registra 4.220 épocas L1 en el artefacto original y 4.104 en la reproducción; la diferencia también aparece en los escenarios variables. Por ello, **las tasas de desacuerdo y los valores locales de la reproducción no se atribuyen a las decisiones exactas del piloto**. Este desajuste impide una auditoría causal fiel sin instrumentar el bucle efectivo de `simulate`; hacerlo requeriría modificar el motor, expresamente excluido en esta tarea. Los contrafactuales reproducidos se conservan solo como análisis exploratorio de snapshots.

## Activación efectivamente registrada en el piloto

| Escenario | Épocas L1 | Fracción de decisiones en P1 | Cambios medios por episodio |
|---|---:|---:|---:|
| Estacionario ρ=0,85 | 3.747 | 6,7 % | 2,33 |
| Estacionario ρ=1,00 | 4.220 | 67,8 % | 6,67 |
| Estacionario ρ=1,25 | 5.169 | 93,4 % | 2,00 |
| Ráfaga y recuperación | 4.218 | 66,1 % | 2,33 |
| Sobrecarga y recuperación | 4.039 | 86,0 % | 2,33 |

El indicador deja P1 activo en gran parte de ρ=1,00, aunque allí D1 rindió mejor en el piloto (R/N 0,6707 frente a 0,6382 con umbral 2/3). En ρ=1,25 P1 rindió mejor que D1 (0,5995 frente a 0,5202), y el supervisor obtuvo 0,6037. En ambos escenarios variables HLS-A quedó por debajo de D1. Los niveles de presión, modo y conmutación de cada época están en el CSV original; el resumen de episodio está en `episodes.csv`.

## Contrafactuales locales exploratorios

En la reproducción diagnóstica hubo discrepancias D1/P1 en 48,2 % de épocas en ρ=1,00 y 55,3 % en ρ=1,25; ráfaga 49,0 % y sobrecarga/recuperación 55,2 %. Estos denominadores y resultados pertenecen a la reproducción no equivalente, no al piloto original. Como comparación inmediata de las asignaciones propuestas, en las discrepancias la suma de (p_{ia}=competencia_{ik}(1-0,35 dificultad_a)) para asignaciones que acabarían a tiempo fue mayor con P1 en 328/1.979 casos discordantes de ρ=1,00 y 454/2.848 de ρ=1,25; mayor con D1 en 1.650 y 2.267 respectivamente. Empates/resto no equivalen a oportunidades recuperables. Esta medida instantánea no considera que el analista atienda tareas posteriores.

Se calculó además, solo cuando había un analista libre y ambas reglas escogían alertas distintas, el valor máximo observable para las dos tareas pendientes de ese analista: (V(a_1,a_2)=p_{ia_1}1[t+s_{ia_1}\le d_{a_1}]+p_{ia_2}1[t+s_{ia_1}+s_{ia_2}\le d_{a_2}]), maximizando la segunda alerta entre las pendientes elegibles actuales. En esa reproducción, P1 superó a D1 en 293/1.919 casos en ρ=1,00 y 444/2.833 en ρ=1,25; D1 superó a P1 en 1.560 y 2.249. La diferencia media fue −0,0914 y −0,0950 correctas esperadas por snapshot, respectivamente. No se suman estas oportunidades: se solapan en el tiempo y no son una ganancia de episodio. El proxy de calidad y los plazos son hipotéticos.

El contraste muestra por qué la elección P1 no garantiza mayor valor local: P1 ordena por holgura y no considera competencia; D1 incorpora competencia propia después del riesgo temporal. Bajo la recompensa modelada, P1 puede adelantar tareas puntuales a costa de asignar alertas a analistas con menor competencia. La tasa de activación de presión no mide si hay discrepancia ni si la discrepancia favorece a P1.

## Evaluación de z y decisión

Los resultados sostienen que (z) responde a carga/ocupación, no a beneficio marginal de cambiar de regla. En particular, el máximo por clase puede amplificar la presión de clases con pocos elegibles; el término de ocupación activa aunque no exista una alternativa temporal mejor; y el trabajo pendiente residual mantiene el modo P1 durante parte de la recuperación. Sin snapshots fieles del motor no puede cuantificarse cuántas activaciones originales ocurrieron sin oportunidad, cuántas llegaron tarde, ni la relación estadística entre (z) y valor local.

No hay evidencia suficiente para proponer una modificación de señal: los contrafactuales de propuestas vienen de una reproducción que no coincide con las épocas originales, y no estiman ganancia terminal. La hipótesis de que (z) confunde congestión con ventaja comparativa de P1 es plausible y está alineada con la mecánica de las reglas, pero la atribución específica permanece sin verificar.

**Recomendación inequívoca: conservar el resultado negativo del piloto y detener esta sublínea de ajuste de HLS-A.** No cambiar el indicador con estos datos. No se ha demostrado que modificar la señal mejore la selección; la información guardada no permite justificarlo. El script de reconstrucción y los dos CSV diagnósticos se conservaron en `diagnose_soc_hlsa.py` y `results/soc_hlsa_pilot/` para trazabilidad.
