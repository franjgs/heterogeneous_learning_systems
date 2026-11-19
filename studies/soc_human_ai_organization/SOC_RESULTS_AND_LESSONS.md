# Resultados SOC y lecciones aprendidas

Este documento consolida resultados **condicionales a cada escenario**. No son estimaciones del desempeño real de GMV-CERT. Las políticas/semillas/modelos no son intercambiables entre campañas; los intervalos solo aplican al diseño que se indica. Los ficheros no citados por enlace permanecen como artefactos reproducibles locales, no como documentos canónicos.

Las etiquetas B0–B4, C0/C1/C2 × P0/P1 y D1-L/D1-S que aparecen aquí pertenecen a formulaciones históricas. El repertorio vigente D1/P1–P5 se define en [Fundamentos y modelo](SOC_FOUNDATIONS_AND_MODEL.md); las etiquetas P1–P5 no son renombrados de las políticas históricas con nombres coincidentes.

## 1. Cronología de la aplicación

| Etapa | Trabajo y conclusión que permanece | Estatus |
|---|---|---|
| Preparación SOCTRA-HLS (octubre 2026) | Se separó clasificación SOCTRA de organización; SOCTRA se fijó como referencia empírica de alertas/triaje, no descripción completa del trabajo humano. | Decisión de alcance. |
| RQ1: B0–B2 | Experimento inicial sintético mostró diferencias, sobre todo bajo carga alta; B2 podía cambiar calidad modelada con compromiso de SLA. | Resultado sintético válido para escenarios/versión indicados, no GMV. |
| Robustez RQ1 | Se añadieron controles B0-R (orden aleatorio reproducible) y B0-F (menos flexible primero). B0-F coincidió con B0 en esa suite porque los conteos de flexibilidad eran iguales. B1 mantuvo ventaja media en ciertos escenarios, con celdas negativas/cercanas a cero. | Resultados no universales; sensibilidad al orden/eligibilidad. |
| Mecanismo/coste de RQ1 | En 30 condiciones × políticas, la ventaja depende de carga, flexibilidad y latencia/coste hipotéticos; con más latencia se reduce o desaparece. B2 puede cambiar calidad modelada. | No calibrado operacionalmente. |
| B3 y B4 PPO de selección | B3 adaptativo no dominó de forma general. PPO inicial colapsó a B1; una segunda evaluación con cambios de régimen no mejoró frente a B3/regla secuencial y fue peor en OOD. | Cierre de ese espacio de acciones; no resultado contra RL en general. |
| B4 control organizativo | Se probaron seis configuraciones C×P en episodios completos. La regla adaptativa evaluada perdió frente a referencias fijas; C0P1 fue la referencia fija más competitiva. | No entrenar ni inferir valor de RL de estos ensayos. |
| Valor de coordinación | Con latencia/coste cero, C2P1 tuvo pequeñas mejoras en algunas condiciones con heterogeneidad; al introducir costes/latencias esas ganancias desaparecieron; C1P1 no mostró mejora clara. | Condicional; beneficios brutos/netos y escenario hipotético. |
| D1 y diagnósticos locales | D1 quedó congelado. Se investigaron errores temporales recuperables y variantes D1-L/D1-S, sin elevarlas a baseline general. | Diagnóstico, no validación de procedimiento real. |
| Modelo paramétrico D1 | Sensibilidad separada a carga, número L1, elegibilidad y deadlines. Hay congestión sintética al subir la carga y presión principalmente L1. | Laboratorio controlado, no dimensionamiento GMV. |
| Replay histórico SOCTRA A | Replay agregado ejecutado 2026-11-18 con timestamps históricos, escalado de referencia y parámetros operativos hipotéticos; sin predicciones OOS. | Conservado como replay condicional; no desempeño real ni etiqueta como verdad. |

Las fechas exactas de algunas campañas no constan en los informes originales y no se infieren aquí.

## 2. RQ1 sintético: asignación y controles

El experimento inicial usó H=12, drenaje D=12, cuatro analistas, cuatro clases, tiempos de servicio y deadlines fijos hipotéticos, cargas baja/media/alta (0,55/0,90/1,25 en la escala del runner) y ocho semillas emparejadas. B1 frente a B0 tuvo diferencia aproximadamente nula a baja carga; a carga media, SLA en H aumentó aproximadamente 0,046–0,075; a alta, 0,216–0,255. Tras drenaje, media +0,057–0,100 y alta +0,299–0,341. B2 podía aumentar calidad modelada a costa de SLA. Estos valores describen esa configuración sintética.

En el estudio de robustez con 30 semillas emparejadas, B1 menos el mejor control descentralizado agregado a nivel de escenario tuvo media +0,111 de SLA en H (rango de escenario −0,001 a +0,272), y +0,148 tras drenaje. B0-R no cambió en promedio de forma relevante; B0-F degeneró a B0 al ser iguales los conteos de flexibilidad. B2−B1 dio +0,040 de calidad modelada y −0,005 de SLA de media, con escenarios heterogéneos. Esto apoya un efecto del matching bajo algunos supuestos, no superioridad general.

El mecanismo RQ1 final usó seis analistas (cuatro especialistas y dos generalistas), 30 condiciones y 30 semillas, con latencia relativa 0, 0,1, 0,25, 0,5 y 1 tiempos medios de servicio en otra sensibilidad. Donde B1 superaba B0, retuvo en promedio 0,812 de esa diferencia frente a B0-F en H; la proporción es dependiente de las condiciones y no una tasa operacional. A mayor latencia se redujo la ventaja, especialmente en baja carga. B2 cambió el compromiso calidad/SLA. Todos los costes, skills, servicios y pools eran supuestos.

## 3. B3/B4: aprendizaje de selección y rediseño organizativo

### B3 y PPO de selector B0/B1/B2

B3 selecciona dinámicamente entre B0/B1/B2 mediante umbrales deterministas fijados con desarrollo. En evaluación sintética independiente (30 seeds, según el protocolo B3), B3−B0 en SLA al corte H fue +0,055 [IC95% 0,042; 0,067], calidad modelada +0,045 [0,035; 0,056], con 1,73 unidades de coordinación frente a 23,60 para B1 fijo. Es evidencia interna de ese protocolo, no evidencia de validez externa.

El PPO inicial, 16.384 pasos y 48 episodios, eligió B1 determinísticamente en 100% de decisiones. Recompensa media: B0 128,57; B1 142,88; B2 144,44; B3 142,74; PPO 142,88. PPO−B3 +0,14 [−1,80; 2,52], sin diferencia concluyente. El checkpoint tuvo probabilidades no degeneradas internamente, pero B1 fue argmax sistemático. La segunda evaluación con regímenes amplió observaciones y presupuesto a 65.536 pasos; hubo cambios B1/B2, no B0. PPO−B3 fue −1,51 [−2,59; −0,46] en cambios de régimen y −5,87 [−7,97; −3,78] OOD; estacionarios −0,53 [−1,97; 0,77]. La conclusión acotada es que **esas dos formulaciones y esos entrenamientos no demostraron beneficio**, no que RL no pueda funcionar.

### B4 de seis acciones y episodios completos

La formulación diagnóstica organizativa combinó coordinación C0 local, C1 urgente y C2 global con prioridad P0 deadline y P1 equilibrio competencia/SLA/velocidad. En el selector P1 se usaron pesos 0,60 competencia, 0,25 probabilidad prevista de cumplimiento y 0,15 velocidad. Se verificaron diferencias mecánicas, pero el coste de coordinación fue supuesto.

En nueve escenarios con 12 semillas (4 desarrollo, 8 evaluación), una regla adaptativa definida para las condiciones perdió frente a políticas fijas; C0P1 fue la referencia fija más competitiva globalmente (recompensa media publicada 268,278). La regla obtuvo algunas celdas cercanas a cero y pérdidas marcadas en alta demanda/cambios. No justifica entrenar RL en esa acción/recompensa como estaba definida.

En el mapa de valor, 10 escenarios × 8 semillas, C2P1 ideal sin costes ofreció +0,068 de recompensa [0,025; 0,111] con heterogeneidad de competencia y +0,052 [0,013; 0,090] con heterogeneidad conjunta de competencia/velocidad. Con costes o latencia positiva estas pequeñas ganancias netas desaparecieron; C1P1 no obtuvo mejora clara. El resultado significa que matching global puede tener valor bruto bajo complementariedad concurrente; no prueba que exista esa complementariedad en GMV ni que un coste real sea cero.

El análisis observó 214 oportunidades en estados muestreados con varios analistas/alertas: no halló perfiles distintos para los analistas elegibles ante la misma clase pendiente; D1-S y C0P1 coincidieron, y C2 modificó pocas asignaciones. Entre 71–82% de despachos C2 examinados había un solo analista libre. Esto se atribuye en parte al despacho inmediato con llegadas de una en una, no por defecto a error; el modelo no prueba coordinación informativa o temporal con reserva/espera.

## 4. D1, corrección local y valor incremental

D1 se congeló como baseline descentralizado; especificación completa en el código `src/hls/rq1_allocation.py` y en los artefactos históricos integrados aquí. En un diagnóstico de 18 episodios sintéticos (3 escenarios × 6 semillas), hubo 3.122 decisiones; 238 (7,6%) seleccionaron una alerta estimada como inviable en SLA pese a otra opción local estimada viable; 1.305 estados tuvieron especialista elegible ocupado sin elegible libre; SLA sintético medio 0,924 y calidad realizada 0,646. Las 238 son oportunidades según duración hipotética; 1.305 describen restricción/capacidad, no error. Contrafactuales conjuntos de un paso con información global y coste cero son límites diagnósticos, no beneficio terminal demostrado.

D1-L intervino al detectar esa condición local. En evaluación 8 semillas × seis escenarios, comparada con D1: sobrecarga SLA +0,477 [0,429; 0,524], recompensa +132,75 [121,26; 144,24]; deadlines ajustados SLA +0,423 [0,350; 0,497], recompensa +92,75 [70,01;115,49]; elegibilidad restringida SLA +0,073 [−0,010;0,157]. Bajo competencias/velocidades heterogéneas, la calidad esperada cayó −0,031 [−0,052;−0,010], espera +0,0170 [0,0031;0,0308] y backlog máximo +10,62 [2,03;19,22]. Esta campaña llevó a REVISE: mejora temporal en ciertos regímenes, no una corrección robusta general.

D1-S aplicó un filtro Pareto (alternativa no menor en competencia propia y no más larga en duración) sin pesos. En evaluación emparejada independiente, mantuvo mejoras D1-S−D1: sobrecarga SLA +0,477 [0,429;0,524], deadlines ajustados +0,386 [0,332;0,441], pero quedó por debajo de D1-L en tight deadlines (recompensa −8,50 [−14,38;−2,62]) y de C0P1 en recompensa allí (−22,00 [−27,23;−16,77]). En heterogeneidad mejoró calidad realizada frente a D1-L +0,032 [0,014;0,050] y redujo backlog máximo −12,50 [−21,90;−3,10], pero frente a C0P1 perdió recompensa −33,88 [−70,69;2,94] y SLA −0,120 [−0,243;0,002]. Veredicto REVISE/STOP como baseline general; los reportes previos de factibilidad describen auditorías intermedias.

La auditoría de métricas detectó que cierta ruta agregaba SLA de escaladas en finalización L1, no terminal L2. El agregador actual usa L2 cuando corresponde. Los informes que anteceden a la corrección deben leerse como resultados históricos de su métrica publicada, no mezclarse con terminales corregidos sin reconstruir el cálculo. Los estudios paramétricos y D1-S describen explícitamente SLA terminal corregido.

## 5. Replay histórico A y calibración de D1

El replay SOCTRA A usa dos ventanas de 28 días, timestamps/volumen y etiquetas históricas de escalado como proxy de encaminamiento; no usó predicciones OOS. Servicios (L1 0,0005H; L2 0,003H), deadlines, competencias, elegibilidad, pools (4 L1/2 L2), continuo 24/7, drenaje y latencia son hipotéticos. En ventanas típicas, B0 rindió mejor que B1/B2 bajo elegibilidad homogénea; la configuración especialista/backup favoreció B1/B2 en SLA con más cola. En ventanas de pico, coordinación mostró SLA mayor en varias configuraciones; B2 modeló más calidad pero menor SLA que B1. B3 usó menos person-time de coordinación. Ejemplo en pico homogéneo: SLA H B0 .6043, B1 .8124, B2 .8025, B3 .8137; con perfil especialista/backup .5550, .7790, .7488, .7734. Son salidas condicionales de simulación sobre trazas de registros, no resultados operativos ni ranking general.

El estudio paramétrico de D1 adoptó 9 alertas/h, H=24h, D=36h, 6 L1/3 L2, 12 seeds. D1 alcanzó 99,68% terminal [99,48;99,88] y sin pendientes tras drenaje en referencia; con 27/h, utilización máxima media de L1 .975, backlog máximo medio 31,4 y P95 respuesta 2,55h; L2 quedó menos cargado. La evidencia muestra sensibilidad sintética a capacidad L1 y deadlines, no un fallo general de D1 ni representatividad de GMV. No combinar estadísticamente con el diagnóstico anterior de configuración distinta.

## 6. Errores, interpretaciones superadas y evidencia vigente

| Hallazgo | Corrección/lectura actual |
|---|---|
| SLA de alerta escalada contado en L1 en una agregación anterior | Corregido a término L2 en el agregador terminal vigente. Los resultados previos afectados quedan históricos y no deben llamarse SLA terminal corregido. |
| Proxies SOCTRA interpretados potencialmente como competencia/verdad | `tramitador`, escalado y cierres no son outcomes de competencia o calidad; etiquetas de proceso se mantienen separadas de referencia simulada. |
| OOF aleatorio considerado como recomendación disponible | No es recomendación temporal OOS; no se utiliza en el replay A. El pipeline cronológico se conserva, pero no es necesario para simulación controlada. |
| C2P1 leído como “coordinación” única | Combina matching, información global y coste/latencia. Sus resultados no aíslan un efecto causal de coordinación temporal/informativa. |
| PPO que selecciona B1 | Es una limitación del checkpoint/entorno evaluado, no evidencia de que RL sea siempre ineficaz. La posterior prueba B4 organizativa tampoco demostró ventaja de su regla adaptativa. |
| Mucha carga llamada “near capacity” | Capacidad y utilización son función de roster/servicio/elegibilidad hipotéticos; nombres de escenarios no equivalen a estados observados de GMV. |

## 7. Código reproducible y artefactos locales

La implementación de asignación es `src/hls/rq1_allocation.py`; el replay L1/L2 y el simulador de IA son `src/hls/rq1_l1_l2.py` y `src/hls/ia_l1_l2_simulation.py`. El adaptador Gymnasium y los runners históricos se conservan como código, junto con sus pruebas, para identificar cómo se produjeron los resultados descritos en esta síntesis. Las pruebas del repertorio vigente D1/P1–P5 están en `tests/test_soc_organization_policies.py`; las pruebas del motor y D1 congelado, en `tests/test_rq1_allocation.py`.

Las salidas de campañas, checkpoints, resultados por episodio, manifiestos derivados de datos y tablas/figuras generadas permanecen como artefactos locales y **no forman parte del conjunto mínimo versionado**. Los datos originales SOCTRA y las figuras restringidas no se incluyen. Los resúmenes históricos de este documento conservan las cifras disponibles y sus condiciones; cuando no queda un artefacto tabular asociado, la limitación de reproducibilidad debe mantenerse explícita. Antes de reutilizar una cifra, comprobar el runner y los parámetros de la campaña correspondiente; no inferir resultados nuevos de este código.
