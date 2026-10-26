# HLS-CE-07.4 — Auditoría de desempates del piloto CE-07.3

**Fecha del análisis:** 2026-10-26
**Base inspeccionada:** `d9dc68b188a18ad9adaa5913c13ec4647ce3c40f`
**Alcance:** análisis de solo lectura del informe CE-07.3 y de los seis registros de desempate. No se ejecutaron simulaciones ni se modificó P1.

## Fuentes y método

Se leyó íntegramente [el informe CE-07.3](02_TECHNICAL_PILOT.md) y se inspeccionaron los seis resultados por réplica, `paired_validation.json`, `configuration.json` y los 6.196 registros de `exact_tie_decisions.json`. Para interpretar competencia se usaron las matrices CE-07.2: en A, los perfiles canónicos 0–2 son altos en las cuatro funciones y 3–11 son bajos; en B, los bloques de tres perfiles corresponden a la función especializada. La permutación publicada asigna perfiles canónicos a slots.

El registro de cada empate contiene organización, semilla, tarea, familia, score máximo, slots y perfiles candidatos, slot y perfil elegidos, rango de prioridad del elegido y tamaño del conjunto admisible. No contiene el vector de carga, edad del servicio ni `F_i` de cada candidato. El protocolo P1 es `q_ik × F_i`; por ello `F_i` puede recuperarse algebraicamente como `best_score/q_ik` una vez identificado `q_ik`, pero esto no reconstruye la trayectoria operativa que produjo ese valor.

## Resultados verificados

| Organización | Empates exactos | Por semilla 30010 / 30011 / 30012 | Candidatos por empate (rango) | Competencia de los candidatos | Perfil completo dentro de cada conjunto |
|---|---:|---:|---:|---|---|
| A | 3.859 | 1.255 / 1.283 / 1.321 | 2–9 | 3.849 conjuntos todos `q=0,6`; 10 todos `q=0,9`; ningún conjunto mixto | Idéntico perfil de competencias dentro del conjunto |
| B | 2.337 | 750 / 788 / 799 | 2–8 | 482 conjuntos todos `q=0,6`; 1.855 todos `q=0,9`; ningún conjunto mixto | Los 1.855 conjuntos altos son del mismo perfil especialista. En los 482 conjuntos bajos: 60 contienen una clase de perfil, 306 dos y 116 tres clases de perfil |

En **6.196/6.196** empates, el seleccionado tenía la misma competencia en la tarea actual que todos los candidatos empatados. Así, la proporción de empates que mezcla niveles de competencia (`0,6` y `0,9`) es cero en ambos diseños. Los candidatos empatados son miembros del conjunto admisible entregado a `_choose_with_tie`; `admissible_count` registra el tamaño de ese conjunto.

Al dividir `best_score` por la competencia común del empate, el `F_i` implícito es aproximadamente **0,999123** en todos los casos (variación solo de redondeo de punto flotante). Por tanto, a la resolución y bajo la fórmula de score registrada, los candidatos empatados igualan tanto `q_ik` como `F_i` para la tarea actual. El candidato elegido coincide con el de menor rango de prioridad CE-04 en los **6.196/6.196** registros, al reconstruir la permutación de prioridad desde la semilla y el generador existente.

Los empates representan 3.859 de 7.827 llegadas en A (49,3 %) y 2.337 de 7.827 en B (29,9 %); son conteos descriptivos del piloto, no estimaciones poblacionales. La diferencia de frecuencia es compatible con conjuntos de candidatos y scores distintos entre estructuras, pero estos datos no identifican por sí solos su causa.

## Clasificación de lo identificable

| Dimensión solicitada | Qué permiten afirmar los registros |
|---|---|
| Competencia en la tarea | Reconstruible exactamente de organización, familia y perfil candidato. Todos los candidatos de cada empate tienen el mismo `q_ik`. |
| Estado operativo | Se sabe que los candidatos pasaron al conjunto admisible usado por P1. No se conserva el estado individual de ocupado/libre, la cola, la edad del servicio ni la carga pendiente de cada candidato. |
| Probabilidad de plazo | No está registrada por candidato. Se infiere `F_i≈0,999123` de `score/q` y la regla P1, condicionado a que el score guardado sea el producto sin transformación; no permite recuperar los estados que originaron `F_i`. |
| Equivalencia física | En A, los candidatos de un empate tienen el mismo vector completo de competencias. En B, los empates altos comparten perfil especialista; algunos empates bajos reúnen perfiles distintos en otras funciones (422 de 482). El registro no contiene estado de cola suficiente para declarar equivalencia física operacional. |
| Conjunto empatado | Reconstruible exactamente: slots/perfiles candidatos y seleccionado constan en cada registro. La prioridad de todos los candidatos no está serializada, aunque se puede verificar el elegido usando código, semilla y regla versionados. |

## Interpretación y límites

**Hecho:** el desempate de P1 no seleccionó entre niveles distintos de competencia actual ni entre valores distintos de `F_i` recuperados del score. A igualdad del score y bajo el objetivo inmediato `q_ik F_i`, el desempate cambia la identidad, no el valor esperado inmediato de éxito dentro de plazo de acuerdo con ese modelo de score.

**Inferencia plausible, no identificada:** elegir identidades distintas puede cambiar la asignación futura, porque cambia qué agente queda ocupado y los agentes pueden tener competencias diferentes en otras familias. También puede cambiar el resultado realizado de la tarea por los resultados potenciales indexados por agente, aun cuando su esperanza inmediata sea la misma. El piloto no ejecutó contrafactuales que cambiasen solo el desempate; por tanto no cuantifica estos efectos posteriores o realizados.

Los registros no permiten clasificar candidatos por cola/servicio individual, verificar independientemente `F_i`, reconstruir alternativas de evolución del sistema tras otro ganador ni atribuir parte del diferencial A/B al desempate. La igualdad de `F_i` se deduce del score registrado y de la competencia común, no de una traza independiente de la función de plazo.

## Suficiencia del control de permutación

El control CE-07.3 usa una permutación reproducible de perfiles a slots por semilla, comparte exactamente esa permutación entre A y B, y la genera desde un flujo separado de la semilla de perfil (`SeedSequence([seed, 12, 707])`). Los registros verifican las permutaciones, la demanda y los potenciales emparejados. Esto es adecuado para evitar que una asignación fija de perfiles a identificadores favorezca sistemáticamente A o B en la comparación emparejada, siempre que la campaña preserve una permutación independiente por réplica, la comparta dentro del par A/B y mantenga el flujo separado del desempate y de los potenciales.

No es un control que estime por separado el efecto causal del desempate: tres permutaciones piloto no prueban invariancia para todos los etiquetados y no se compararon múltiples etiquetas con idénticos demanda, potenciales y demás flujos. La campaña puede usar el control emparejado como protección frente al sesgo de etiquetas, pero cualquier afirmación de que el desempate carece de efecto sobre resultados colectivos excedería estos datos. No se recomienda cambiar P1 a partir de este análisis.

## Dictamen

Los logs bastan para reconstruir y cuantificar los conjuntos empatados, la competencia actual de los candidatos y la decisión según prioridad. Muestran que los empates no alteraron el score inmediato esperado entre candidatos, aunque pueden cambiar la identidad y, plausiblemente, la trayectoria posterior. El control de permutación emparejada es suficiente como control de etiquetas para la comparación A/B si se conserva por semilla; no identifica el efecto independiente del desempate. Esta auditoría no convierte el piloto en evidencia confirmatoria ni requiere nuevas ejecuciones.

**Artefactos fuente:** [traza completa de desempates](../../../results/experiments/hls_ce07_technical_pilot/exact_tie_decisions.json), [configuración](../../../results/experiments/hls_ce07_technical_pilot/configuration.json), [validación de pares](../../../results/experiments/hls_ce07_technical_pilot/paired_validation.json), [manifiesto](../../../results/experiments/hls_ce07_technical_pilot/manifest.json).
