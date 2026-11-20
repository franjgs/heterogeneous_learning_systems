# Valor futuro de una decisión individual D1/P1: auditoría de factibilidad

**Estado:** estudio de factibilidad. No se ejecutaron contrafactuales terminales porque el simulador actual no permite bifurcar y reanudar fielmente el mismo estado de `simulate` sin modificar el motor. D1, P1 y HLS-B permanecen congeladas; no se entrenó ni ajustó ninguna política.

## Pregunta y semántica requerida

Sea (S_t) el estado completo justo después de procesar llegadas y finalizaciones en una época de despacho L1, antes de asignar trabajo. Incluye cola, trabajos en curso y sus tiempos, analistas, reloj, llegadas observadas por HLS-B, modo por pool, cursor de eventos, asignaciones anteriores, estado del RNG de D1 y entradas exógenas futuras fijadas. Se requiere una discrepancia real entre las propuestas (a_D(S_t)) y (a_P(S_t)).

El efecto buscado sería la diferencia pareada entre dos continuaciones que parten del **mismo** (S_t), aplican exactamente una vez (a_D) o (a_P), y después usan la misma HLS-B congelada en todas las épocas y pools. Cada rama conservaría la misma traza exógena futura, los mismos parámetros de calidad y escalado y el mismo conjunto (N) de alertas admitidas. Se medirían ΔR/N terminal, ΔR esperado, ΔSLA, trabajo pendiente, calidad esperada y finalizaciones. El efecto inmediato sería la asignación inicial; el posterior, todas las consecuencias de cola, elegibilidad y plazos. La igualdad de semilla por sí sola no asegura números aleatorios comunes alineados si D1 consume el RNG un número distinto de veces entre ramas; habría que fijar explícitamente la semántica del flujo aleatorio y verificarla.

Esta definición es un **contrafactual experimental** con la información exógena fijada para comparación, no una decisión disponible al supervisor en (t). La rama con mejor resultado futuro no puede usarse como selector causal observable.

## Auditoría de la interfaz actual

| Requisito | Estado observado | Consecuencia |
|---|---|---|
| Capturar (S_t) completo de `simulate` | No hay `snapshot`, `restore` ni `resume` en la función. `pending`, `running`, `dispatching`, cursor de llegadas, `order_rng`, `observed_arrivals` y modos HLS-A/B son variables locales del bucle. | La traza diagnóstica no basta para restaurar una época exacta. |
| Detectar discrepancia D1/P1 | Sí, para HLS-A: el colector calcula ambas propuestas con copia del RNG y registra el despacho real. | Identifica estados candidatos, sin poder bifurcarlos. |
| Aplicar una sola propuesta alternativa | `simulate` ejecuta una política elegida en su propio bucle; no acepta una propuesta externa puntual. | Hace falta una interfaz de inyección o una sesión cuya equivalencia esté demostrada. |
| Continuar ambas ramas con HLS-B idéntica | `AllocationSession.dispatch` acepta D1/P1, pero no implementa el estado ni la histéresis HLS-B. `simulate_l1_l2` ejecuta L1 completo y construye después las entradas L2. | Una continuación manual con `AllocationSession` no es todavía la continuación exacta del motor acoplado L1/L2. |
| Llegadas futuras comunes | El generador crea trazas reproducibles y los experimentos anteriores verificaron hashes iguales dentro de parejas. | Es posible fijar las entradas, pero esto no resuelve la restauración del estado. |
| RNG común | El diagnóstico copia `order_rng.getstate()` para previsualizar D1 sin consumir el flujo real. No exporta ese estado en el snapshot. | No se puede restaurar el RNG exacto de cada rama desde la traza guardada. |
| Mismo denominador y métricas terminales | `simulate_l1_l2` permite calcular R/N, SLA y calidad de episodios completos con admitidas comunes. | No se pueden atribuir diferencias a **una** decisión sin reanudación fiel. |

La clase incremental `AllocationSession` comparte despachadores, pero es una ruta de ejecución distinta. Su uso anterior para reconstruir épocas HLS-A produjo **4.104 épocas frente a 4.220** en ρ=1,00; el [diagnóstico directo](SOC_HLS_ADAPTIVE_DIAGNOSTIC.md) declaró esa reconstrucción no equivalente. Su capacidad de hacer una copia profunda no resolvería por sí sola la equivalencia de eventos, historial de HLS-B ni acoplamiento L2. Una solución nueva dentro de un runner que imitase el bucle tendría el mismo problema hasta superar comparaciones bit a bit de trayectorias completas.

## Equivalencia disponible y su límite

La instrumentación directa de HLS-A fue observacional: en **24 episodios de desarrollo**, `L1L2Result` con y sin diagnóstico fue idéntico, junto con R/N y las épocas de ambos pools. Registró **17.646 épocas L1 y 883 L2**. Esta prueba demuestra que observar propuestas en esa ruta no alteró sus trayectorias; **no** demuestra que se pueda reemplazar una propuesta ni reanudar desde el snapshot. La reconstrucción `AllocationSession` no superó la equivalencia de épocas. Por ello no se reporta aquí ninguna ΔR/N contrafactual de decisión individual.

## Estados de desarrollo disponibles para un estudio posterior

El diagnóstico directo utilizó seis semillas de desarrollo por escenario, sin semillas confirmatorias. En L1 observó discrepancia D1/P1 en **1.978/4.220** épocas de ρ=1,00 y **2.849/5.169** de ρ=1,25; en los dos escenarios variables, **1.994/4.218** y **2.217/4.039**. El contraste exacto de dos servicios fue evaluable en 1.919, 2.833, 1.872 y 2.200 épocas, respectivamente. Solo en ρ=1,25 distinguió signos: **35 positivos, 34 negativos y 2.764 empates** para P1−D1. Son cantidades locales de dos servicios, no efectos futuros ni ganancias agregables.

Si se habilita una bifurcación fiel, el muestreo debe fijarse antes de leer resultados futuros y estratificar por ρ=1,00/1,25, ventanas próximas a transiciones, cuantiles de cola, mezcla de clases, holguras y elegibilidad; excluir estados de validación confirmatoria. Una selección reproducible puede usar hashes de `(escenario, semilla, pool, índice de época)` dentro de cada estrato. Las épocas con varias asignaciones simultáneas exigirían definir si la «única decisión» es la propuesta conjunta de la época o una pareja individual; mezclar ambas unidades cambiaría el estimando. Se prefijaría HLS-B como continuación única y se exigiría que ambas ramas coincidan exactamente con una ejecución no intervenida cuando se aplica su propuesta original.

## Criterios técnicos antes de medir valor futuro

1. Capturar y restaurar todos los componentes dinámicos del bucle efectivo, incluido RNG y estado de HLS-B por pool, sin volver a generar servicios ni llegadas.
2. Reanudar un estado sin intervención y obtener el mismo `L1L2Result`, historial de modos, asignaciones, finalizaciones L2 y R/N que la ejecución completa original para las trayectorias de desarrollo seleccionadas.
3. Demostrar que dos copias sin intervención producen objetos y flujos RNG idénticos; documentar cómo se acoplan los sorteos de D1 si una rama consume cantidades distintas.
4. Aplicar una intervención única y comprobar que ambas ramas tienen el mismo conjunto exógeno y denominador, y que cualquier divergencia comienza en la época intervenida.
5. Solo entonces calcular métricas terminales y comparar el valor futuro con el contraste local de dos servicios. La selección de estados y el número de realizaciones futuras deben quedar fijos antes del análisis de efectos.

## Respuestas científicas actuales

**A. Diferencias futuras relevantes:** desconocidas. Hay miles de discrepancias de propuestas, pero los 69 signos no nulos del contraste local de dos servicios en sobrecarga no estiman el efecto terminal de una decisión.

**B. Relación con información observable:** no evaluada para valor futuro. Cola, clase, holgura, elegibilidad y servicio están disponibles en el diagnóstico, pero la presión HLS-A no separó bien los 35 signos locales positivos de los 34 negativos (medianas 23,45 y 22,14). Esto tampoco prueba que otras señales predigan el efecto futuro.

**C. Coordinación basada en valor futuro:** todavía no justificada por evidencia contrafactual fiel. Su estudio podría ser útil una vez cumplidos los criterios técnicos, sin elegir ahora una arquitectura.

**D. Política actual:** mantener HLS-B congelada como referencia mientras se resuelve la factibilidad. La [validación independiente](SOC_HLSB_VALIDATION_RESULTS.md) probó una mejora en su mezcla sintética de escenarios, pero no identifica el valor futuro de decisiones individuales. Los estudios [de regímenes](SOC_HLS_NONSTATIONARY_REGIMES.md) y [momento de conmutación](SOC_HLS_SWITCHING_OPPORTUNITY.md) tampoco lo aíslan.

**Conclusión:** el resultado de este trabajo es un bloqueo técnico comprobado y un protocolo de equivalencia necesario. Presentar efectos terminales de ramas reconstruidas con la interfaz actual excedería la evidencia. No se modificaron políticas, motor ni resultados confirmatorios en este estudio; no se ejecutó confirmación, commit ni push.
