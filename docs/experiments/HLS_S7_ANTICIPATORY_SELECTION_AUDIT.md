# HLS-S7 — Auditoría mecanística de selección anticipativa

**Fecha:** 23/10/2026
**Caso:** instancia central de preparación S7, demanda C5, `T=4`, sin transferencia.
**Resultados reproducibles:** [`results.json`](../../results/experiments/hls_s7_anticipatory_selection_audit/results.json)
**Runner:** [`run_hls_s7_anticipatory_selection_audit.py`](../../experiments/run_hls_s7_anticipatory_selection_audit.py)

## Pregunta e hipótesis

Se examinó si la ventaja de Bellman frente a BEST-MYOPIC nace de diferencias en la cantidad de MIS-v2 aprendido, de su distribución entre competencias, de su utilidad futura u otros efectos físicos. Se añadió CURRENT-DEMAND-MYOPIC (CDM) como control reactivo: maximiza CES inmediato y, solo entre empates dentro de `1e-12`, maximiza incrementos positivos de competencias en las coordenadas de tarea cuyo requisito actual es positivo. Los empates restantes usan la clave canónica de acción. CDM no accede a la matriz de transición Markov.

La instancia, estados, acciones, CES, MIS-v2 e información corriente son los existentes. La política Bellman conserva sus acciones históricas; una evaluación Bellman sin poda se usa solo para disponer de `V_B` en todos los estados alcanzables por los otros controles.

## Cuatro políticas y métricas

Valores exactos esperados con HLS-PEF. Cumplimiento es la fracción de servicios tarea-periodo que satisface el requisito; déficit es suma de déficits absolutos. No hay intervalos estadísticos porque se enumeran todas las ramas con probabilidad positiva.

| Política | CES acumulado | Cumplimiento | Déficit | Producción | Esfuerzo productivo |
|---|---:|---:|---:|---:|---:|
| A — Bellman | 3.1628653621 | 0.750250 | 0.049950 | 3.1675720885 | 8 |
| MA — miope de catálogo | 3.0346209871 | 0.3019375 | 0.1023575625 | 3.0346209871 | 5.20775 |
| BMA — BEST-MYOPIC, ganancia total | 3.0444737839 | 0.3019375 | 0.1023575625 | 4.3181911375 | 8 |
| CDM — ganancia en tarea actual | 3.1628653621 | 0.750250 | 0.049950 | 3.1628653621 | 8 |

No hubo esfuerzo docente ni consumo de recursos docentes: transferencia está deshabilitada. Bellman y CDM coinciden en CES, cumplimiento y déficit esperados, aunque sus últimas acciones pueden producir estados de competencia distintos. La producción acumulada se conserva separada del CES.

Las diferencias CES solicitadas son:

| Diferencia | CES |
|---|---:|
| A − BMA | 0.1183915782 |
| A − CDM | 0.0000000000 |
| BMA − CDM | −0.1183915782 |

La ventaja de Bellman sobre BEST-MYOPIC reproduce el valor anterior. Frente a CDM, en esta instancia no queda ventaja agregada de CES.

## Estados, divergencias y aprendizaje

El árbol tiene 16 secuencias combinatorias de cuatro demandas, de las cuales **8 tienen probabilidad positiva** desde la distribución inicial (la probabilidad inicial de `task-y` es cero). Se recorrieron las ramas de soporte positivo. El JSON registra para cada estado alcanzado: estado y demanda, número de acciones admisibles, máximo CES, tamaño del conjunto empatado, acciones elegidas y probabilidad de ocupación por cada política. Las ocupaciones suman uno por periodo para cada política.

La primera divergencia A/BMA con masa positiva ocurre en `t=1`, demanda `task-y`, con probabilidad `0.9`; ambas habían ejecutado la misma acción en `t=0`, demanda x. El estado común es `C=[[.24,.90],[.384,0]]`. Las acciones usan esfuerzo productivo total 2 y obtienen CES inmediato `.90`:

- Bellman asigna ambos agentes a y. `ΔC=[[0,.015],[0,.05]]`: ganancia neta/positiva total `.065`, concentrada en y.
- BEST-MYOPIC asigna A a y y B a x. `ΔC=[[0,.015],[.07392,0]]`: ganancia total `.08892`, concentrada en x para B.

Así, Bellman desarrolla menos competencia total (`.065` frente a `.08892`), pero más de la competencia asociada a la demanda actual y persistente. La transición desde y conserva probabilidad `.95` en y y `.05` en x. La divergencia siguiente, en `t=2`, `task-y`, tiene masa `.09`: Bellman gana `.065` en y frente a `.0800496` de BMA en total, de nuevo dirigido a x por BMA. Ambas decisiones mantienen CES inmediato `.90`.

En la matriz de incrementos, la diferencia no es solo volumen: el aprendizaje de BMA se desplaza a B/x, mientras Bellman y CDM desarrollan B/y. No aparece una divergencia de Tipo II según la definición estricta (mismo total con distinta distribución), porque en las divergencias positivas el total también difiere; el JSON registra por separado ambos hechos. No se observó Tipo IV: Bellman no sacrifica CES inmediato en la variante sin transferencia.

CDM sigue las decisiones de Bellman hasta el último periodo. En `t=3`, `task-y`, masa `.009`, selecciona otra asignación empatada; como no hay continuación, sus valores Q son ambos `.90`. Esa divergencia final cambia la competencia sucesora, pero no el CES acumulado. BMA y CDM ya divergen en `t=1` y `t=2` con las mismas masas `.9` y `.09`.

## Valor de continuación

En cada divergencia compartida se calculó

\[
Q_B(s,d,a)=R(s,d,a)+\sum_{d'}P(d'\mid d)V_B(s',d').
\]

En `t=1`, Bellman obtiene continuación `2.850552725` frente a `2.765466423` si se toma la acción BMA; ambos rewards inmediatos son `.90`, así que la diferencia Q es `.085086302`. En `t=2`, las continuaciones son `.959246` y `.91499848`, diferencia `.04424752`, otra vez sin diferencia inmediata. En ambos puntos el futuro favorece la asignación que desarrolla y, por MIS-v2, hace productivo a B/y. Se trata de una comparación exacta desde un mismo estado, no de inferir utilidad futura a partir de la magnitud de competencia.

La acción CDM de desarrollar la tarea actualmente demandada obtiene la misma continuación que Bellman en los estados compartidos `t=1,2`; por eso su valor total coincide. En el único desacuerdo A/CDM, al final del horizonte, no existe valor de continuación.

## Identidad exacta de diferencia de rendimiento

Se verificó, usando `V_B` y el estado de demanda observado antes de la acción:

\[
J_B-J_\pi=\mathbb E_\pi\left[\sum_t\left(V_B(s_t,d_t)-Q_B(s_t,d_t,a_t^\pi)\right)\right].
\]

Para A−BMA, el lado izquierdo y la suma de ventajas ponderadas por la ocupación de BMA son ambos `0.1183915782` (residuo `4.2×10⁻¹⁶`). Las contribuciones por periodo son `t=0: 0`, `t=1: .0765776718`, `t=2: .0418139064`, `t=3: 0`. Para A−MA ambos lados son `0.1282443750` (residuo `8.3×10⁻¹⁷`), con `.0833568750` en `t=1` y `.0448875000` en `t=2`. Para A−CDM ambos lados son cero. La suma integra estados según la ocupación de cada política y evita agregar contrafactuales incompatibles.

## Conclusión mecanística

La ventaja A−BMA no se explica por Bellman aprendiendo más en cantidad: en las primeras divergencias aprende menos. La explica el destino del aprendizaje: el desempate global de BMA favorece el mayor incremento total en B/x, aunque la demanda actual y su persistencia favorezcan y. Los Q de continuación cuantifican la pérdida posterior de esa elección. El rendimiento de CDM, igual al de Bellman, muestra que en este caso el desempate con la tarea actual basta para capturar la ventaja; por tanto, A−BMA no demuestra una necesidad exclusiva de planificación o de conocer la distribución futura. A y CDM solo difieren en una acción terminal sin efecto sobre CES acumulado.

La afirmación queda acotada al CES, al estado exacto conocido por estas referencias, a la demanda C5 de la instancia y a `T=4`. CDM es un control de diagnóstico, no una política general recomendada. No hubo transferencia ni escenarios adicionales; no se modificaron leyes u objetivos. HLS-PEF evaluó registros del replay y conservó unidades/procedencia.

## Validación

El runner reproduce A=`3.1628653621`, MA=`3.0346209871` y BMA=`3.0444737839`; contrasta Bellman podado y sin poda; enumera las ramas de soporte; verifica ocupaciones por periodo, procedencia/unidades PEF y la identidad de diferencia de rendimiento. Las pruebas comprueban que CDM no cambia su acción inicial cuando cambia únicamente la transición futura, que sus decisiones son reproducibles y que las matrices, Q y valores esperados son coherentes.
