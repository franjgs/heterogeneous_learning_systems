# Comparación experimental D1/P1–P5

> **OLD MODEL / MODELO VIEJO:** this document records the historical L1-first organizational model and its evidence. Its results remain valid only for that model and do not validate the NEW MODEL. See [MODEL_GENERATIONS.md](../soc_triage_hls_availability_robustness/MODEL_GENERATIONS.md). The current LaTeX manuscript belongs entirely to the OLD MODEL; NEW MODEL transfer is deferred.

**Estado:** campaña exploratoria sintética de mecanismos, revisada en la [consolidación científica](SOC_SCIENTIFIC_CONSOLIDATION.md); no estimación del SOC de GMV ni prueba confirmatoria de superioridad general.

## Configuración y políticas efectivas

Se reutilizaron exactamente el generador, mezcla de clases/prioridades, seis perfiles L1 de referencia, tres L2, servicios, competencias, elegibilidad, escalado hipotético y deadlines de [A0](SOC_A0_BASELINE_CONGESTION.md). H=24 h; D=24 h. Cuatro cargas principales ρ=0,65/0,85/1,00/1,25 y sensibilidad separada a seis/cinco/cuatro L1 con 18,472 alertas/h. Veinte semillas emparejadas 261140000–261140019. Los perfiles retenidos en la sensibilidad son los subconjuntos A0; no se recalibraron.

Las reglas se leyeron en `src/hls/rq1_allocation.py`: D1 es elección secuencial en orden aleatorio reproducible según riesgo temporal, competencia propia y elegibilidad de compañeros; P1 elige menor holgura posterior al servicio; P2 mayor competencia propia; P3 menor número de otros analistas libres elegibles y después competencia/holgura; P4 optimiza matching uno a uno lexicográfico (finalizaciones previstas a tiempo, cardinalidad y deadlines); P5 usa P3 salvo mejora estricta de (finalizaciones previstas a tiempo, cardinalidad) del matching, con latencia incluida en la predicción. C es una regla central greedy secuencial distinta y no se utilizó. Todas usan el mismo motor, elegibilidad y servicio; P4/P5 no tienen información futura.

La fase «sin coste» fija latencia=0 y coste por arista=0. La sensibilidad «con coste» reutiliza **0,05 h (3 min) por época coordinada y 1 unidad abstracta por arista elegible**, ya definidos en A3.2. El coste abstracto se informa aparte y no reduce R/N. P5 sólo incurre en latencia/recurso cuando activa P4 en el código; el coste de evaluar la alternativa conjunta no está modelado. Estos parámetros no son observaciones GMV.

Cada política recibió la misma tupla de alertas generadas por escenario/semilla; se verificó igualdad de SHA-256 de la traza. La ruta L2 está fijada por la misma recomendación IA sintética para todas. El RNG de orden D1 es específico de esa política; el emparejamiento común cubre exógenos, y calidad se evalúa como esperanza modelada sin muestreo Bernoulli adicional.

Métrica principal: R/N=Σ sobre alertas admitidas de `competencia del analista terminal × (1−0,35×dificultad simulada) × 1[finalización terminal≤deadline y corte]` dividido entre todas las admitidas. Las escaladas terminan en L2. Se separan H y H+D; pendientes cuentan en denominador con contribución cero al corte. Calidad completada usa sólo las completadas. No hay descartes.

## Resultado principal sin latencia ni coste

La tabla elige la mayor media observada por celda para orientar lectura; esa elección posterior no es una prueba de superioridad. IC95% t pareado contra D1, n=20, df=19, sin ajuste de multiplicidad.

|Escenario|D1 R/N terminal|Mayor media|Δ absoluto frente a D1 [IC95%]|
|---|---:|---|---:|
|rho_065|0.6394|P5 0.6418|0.0024 [0.0008; 0.0039]|
|rho_085|0.6550|P5 0.6559|0.0008 [-0.0005; 0.0021]|
|rho_100|0.6699|P5 0.6701|0.0001 [-0.0006; 0.0009]|
|rho_125|0.5280|P4 0.6336|0.1056 [0.0844; 0.1268]|
|staff_6|0.6394|P5 0.6418|0.0024 [0.0008; 0.0039]|
|staff_5|0.6520|P5 0.6534|0.0015 [0.0001; 0.0028]|
|staff_4|0.6865|P5 0.6871|0.0006 [-0.0002; 0.0014]|

|Escenario|Política|R/N H|R/N terminal ± SD|Δ terminal frente D1 [IC95%]|Episodios >D1|SLA terminal|Calidad completada|
|---|---|---:|---:|---:|---:|---:|---:|
|rho_065|D1|0.6323|0.6394 ± 0.0036|0.0000 [0.0000; 0.0000]|0/20|0.9947|0.6429|
|rho_065|P1|0.6297|0.6364 ± 0.0031|-0.0030 [-0.0048; -0.0012]|5/20|0.9947|0.6399|
|rho_065|P2|0.6347|0.6416 ± 0.0024|0.0022 [0.0005; 0.0039]|14/20|0.9947|0.6451|
|rho_065|P3|0.6347|0.6416 ± 0.0024|0.0022 [0.0005; 0.0039]|14/20|0.9947|0.6451|
|rho_065|P4|0.6301|0.6370 ± 0.0032|-0.0024 [-0.0041; -0.0007]|4/20|0.9951|0.6402|
|rho_065|P5|0.6349|0.6418 ± 0.0023|0.0024 [0.0008; 0.0039]|14/20|0.9949|0.6451|
|rho_085|D1|0.6429|0.6550 ± 0.0051|0.0000 [0.0000; 0.0000]|0/20|0.9942|0.6590|
|rho_085|P1|0.6224|0.6344 ± 0.0033|-0.0207 [-0.0232; -0.0182]|0/20|0.9943|0.6381|
|rho_085|P2|0.6432|0.6555 ± 0.0052|0.0005 [-0.0008; 0.0018]|10/20|0.9942|0.6594|
|rho_085|P3|0.6432|0.6555 ± 0.0052|0.0005 [-0.0008; 0.0018]|10/20|0.9942|0.6594|
|rho_085|P4|0.6234|0.6347 ± 0.0033|-0.0204 [-0.0227; -0.0180]|0/20|0.9946|0.6382|
|rho_085|P5|0.6435|0.6559 ± 0.0052|0.0008 [-0.0005; 0.0021]|12/20|0.9947|0.6594|
|rho_100|D1|0.6203|0.6699 ± 0.0046|0.0000 [0.0000; 0.0000]|0/20|0.9937|0.6741|
|rho_100|P1|0.5889|0.6343 ± 0.0038|-0.0356 [-0.0376; -0.0336]|0/20|0.9941|0.6382|
|rho_100|P2|0.6204|0.6698 ± 0.0045|-0.0001 [-0.0010; 0.0007]|9/20|0.9938|0.6739|
|rho_100|P3|0.6204|0.6698 ± 0.0045|-0.0001 [-0.0010; 0.0007]|9/20|0.9938|0.6739|
|rho_100|P4|0.5931|0.6342 ± 0.0034|-0.0357 [-0.0373; -0.0340]|0/20|0.9943|0.6380|
|rho_100|P5|0.6206|0.6701 ± 0.0044|0.0001 [-0.0006; 0.0009]|11/20|0.9942|0.6739|
|rho_125|D1|0.4127|0.5280 ± 0.0466|0.0000 [0.0000; 0.0000]|0/20|0.7689|0.6762|
|rho_125|P1|0.4740|0.6278 ± 0.0207|0.0998 [0.0825; 0.1172]|20/20|0.9849|0.6376|
|rho_125|P2|0.4332|0.4859 ± 0.0383|-0.0421 [-0.0539; -0.0302]|1/20|0.7068|0.6791|
|rho_125|P3|0.4332|0.4859 ± 0.0383|-0.0421 [-0.0539; -0.0302]|1/20|0.7068|0.6791|
|rho_125|P4|0.4790|0.6336 ± 0.0042|0.1056 [0.0844; 0.1268]|20/20|0.9929|0.6383|
|rho_125|P5|0.4947|0.6167 ± 0.0143|0.0887 [0.0724; 0.1050]|20/20|0.9029|0.6791|

La tabla completa `summary.csv` incluye espera media/P95, colas medias/máximas L1/L2, utilización, completadas y pendientes H/H+D. `strata.csv` conserva prioridades y clases por semilla; todos los denominadores y desviaciones se calculan a nivel de episodio.

### Espera, cola, utilización y pendientes en las cuatro cargas

Valores medios de 20 episodios; P95 se calcula dentro de cada episodio y luego se promedia. La cola L1 media se integra durante H+D=48 h y la máxima se observa hasta ese corte; excluyen tareas en servicio. La utilización corresponde a H=24 h; pendientes H incluye trabajo en servicio y L2.

|Carga|Política|Espera L1 media / P95 (h)|Cola L1 media 0–48 h / máx.|Util. L1/L2 en H|Pendientes H|
|---|---|---:|---:|---:|---:|
|rho_065|D1|0.03 / 0.14|0.24 / 7.3|0.688 / 0.250|5.2|
|rho_065|P1|0.03 / 0.15|0.24 / 7.3|0.688 / 0.246|4.8|
|rho_065|P2|0.03 / 0.14|0.24 / 7.3|0.688 / 0.247|5.0|
|rho_065|P3|0.03 / 0.14|0.24 / 7.3|0.688 / 0.247|5.0|
|rho_065|P4|0.02 / 0.14|0.23 / 7.0|0.687 / 0.246|4.9|
|rho_065|P5|0.03 / 0.14|0.24 / 7.3|0.688 / 0.247|5.0|
|rho_085|D1|0.14 / 0.74|1.76 / 15.8|0.890 / 0.326|10.9|
|rho_085|P1|0.14 / 0.67|1.71 / 15.8|0.893 / 0.323|11.1|
|rho_085|P2|0.14 / 0.74|1.77 / 16.0|0.889 / 0.324|11.1|
|rho_085|P3|0.14 / 0.74|1.77 / 16.0|0.889 / 0.324|11.1|
|rho_085|P4|0.13 / 0.62|1.64 / 15.6|0.891 / 0.324|10.3|
|rho_085|P5|0.14 / 0.74|1.77 / 16.0|0.889 / 0.324|11.1|
|rho_100|D1|1.04 / 5.06|14.78 / 57.0|0.981 / 0.366|53.0|
|rho_100|P1|0.95 / 3.17|13.59 / 52.6|0.988 / 0.363|49.0|
|rho_100|P2|1.03 / 5.00|14.65 / 57.1|0.981 / 0.366|52.5|
|rho_100|P3|1.03 / 5.00|14.65 / 57.1|0.981 / 0.366|52.5|
|rho_100|P4|0.87 / 2.94|12.46 / 49.6|0.987 / 0.362|44.6|
|rho_100|P5|1.03 / 5.00|14.65 / 57.1|0.981 / 0.366|52.5|
|rho_125|D1|4.19 / 11.92|73.86 / 214.0|0.994 / 0.371|218.6|
|rho_125|P1|3.96 / 10.34|69.78 / 207.8|0.995 / 0.363|212.7|
|rho_125|P2|4.48 / 14.59|78.95 / 228.4|0.994 / 0.380|233.8|
|rho_125|P3|4.48 / 14.59|78.95 / 228.4|0.994 / 0.380|233.8|
|rho_125|P4|3.84 / 10.08|67.68 / 202.7|0.995 / 0.366|207.6|
|rho_125|P5|4.48 / 16.62|78.95 / 228.4|0.994 / 0.381|233.8|

## Prioridad alta y plantilla reducida

|Escenario|Política|SLA high terminal|R/N high terminal|
|---|---|---:|---:|
|rho_085|D1|0.9597|0.6363|
|rho_085|P1|0.9600|0.6130|
|rho_085|P2|0.9597|0.6337|
|rho_085|P3|0.9597|0.6337|
|rho_085|P4|0.9625|0.6131|
|rho_085|P5|0.9631|0.6360|
|rho_100|D1|0.9563|0.6523|
|rho_100|P1|0.9589|0.6111|
|rho_100|P2|0.9568|0.6537|
|rho_100|P3|0.9568|0.6537|
|rho_100|P4|0.9602|0.6121|
|rho_100|P5|0.9595|0.6556|
|rho_125|D1|0.7710|0.5370|
|rho_125|P1|0.9620|0.6143|
|rho_125|P2|0.7739|0.5387|
|rho_125|P3|0.7739|0.5387|
|rho_125|P4|0.9640|0.6160|
|rho_125|P5|0.8778|0.6106|

|L1 activos|ρ aprox.|D1|P1|P2|P3|P4|P5|
|---:|---:|---:|---:|---:|---:|---:|
|6|.650|0.6394|0.6364|0.6416|0.6416|0.6370|0.6418|
|5|.773|0.6520|0.6410|0.6532|0.6532|0.6412|0.6534|
|4|.983|0.6865|0.6531|0.6867|0.6867|0.6548|0.6871|

## Coste y latencia de coordinación

|Escenario|P4 R/N sin/con latencia|P5 R/N sin/con latencia|P4 latencia acumulada h / recurso unidades|P5 latencia acumulada h / recurso unidades|
|---|---:|---:|---:|---:|
|rho_065|0.6370 / 0.6336|0.6418 / 0.6416|23.27 / 1247|0.00 / 0|
|rho_085|0.6347 / 0.6339|0.6559 / 0.6555|30.40 / 15181|0.00 / 0|
|rho_100|0.6342 / 0.6324|0.6701 / 0.6698|35.46 / 45005|0.01 / 0|
|rho_125|0.6336 / 0.5538|0.6167 / 0.6003|44.21 / 114220|10.00 / 35201|

La latencia acumulada suma épocas de ambos pools y puede superar la duración de reloj por incluir varios despachos. No es utilización de un coordinador medido. El recurso abstracto puede crecer mucho con el tamaño de la cola; no se le asignó precio.

## Interpretación científica y resultados negativos

A ρ=1,25, P1 y P4 ideal mejoran R/N frente a D1, principalmente por el incremento de SLA; su calidad media de completadas cae aproximadamente de 0,676 (D1) a 0,638. P5 ideal mejora menos; P2/P3 empeoran R/N pese a mayor calidad de completadas. Bajo carga holgada/transición, P1 y P4 pierden R/N: el SLA terminal ya tiene techo y el cambio de asignaciones reduce calidad modelada. P2 y P3 son prácticamente equivalentes en todos los episodios de esta matriz; la escasez de elegibilidad no generó un mecanismo P3 separado en estas configuraciones.

Con latencia hipotética P4 conserva mejora de R/N frente a D1 en sobrecarga (+0,0258, IC95% [0,0091; 0,0424]) pero pierde parte importante de la mejora ideal (+0,1056). P5 conserva +0,0723 [0,0571; 0,0876]. No se monetiza el recurso, por lo que éstas no son ganancias netas económicas.

El diagnóstico independiente `diagnose_soc_matching.py` encontró 0 épocas con ≥2 asignaciones simultáneas en las 80 trazas principales de P4 y en las 80 de P5 (ambos pools). Por tanto, estas salidas no identifican valor de matching conjunto; P4 está ejerciendo selección central individual. En la sensibilidad con coste, P5 pagó latencia media acumulada de 0/0/0,01/10,00 h por episodio en las cuatro cargas, frente a 23,27/30,40/35,46/44,21 h de P4. El coste de cribar estados P5 que terminan en P3 sigue sin modelarse.

La alta prioridad también mejora en SLA a ρ=1,25 con P1/P4, aunque su R/N incorpora la reducción de calidad. En la sensibilidad de plantilla fija, retirar L1 altera la composición del pool y la carga; P1/P4 no mejoran R/N, y las ventajas de P2/P3/P5 son pequeñas o inciertas. La mejora no aumenta monótonamente al reducir plantilla.

A0 había identificado oportunidades locales de orden bajo sobrecarga; este resultado de episodio es compatible con que la prioridad temporal aproveche parte de ellas. No permite atribuir un número concreto de alertas recuperadas a esas decisiones ni sumar pérdidas locales. Las diferencias P4 pueden proceder de información global y selección individual. El diagnóstico de cardinalidad se consigna abajo.

## Validación, límites y reproducibilidad

Se comprobaron unicidad de asignación, elegibilidad L1, conservación en H y H+D, identidad SHA-256 de trazas y semillas emparejadas. Se usó el mismo resultado terminal L2 en todas las métricas. La semilla fija hace reproducible la generación y el orden D1. Los CSV de episodios, estratos y estadísticos, la configuración y `run_metadata.json` quedan bajo `results/soc_policy_comparison/` (ignorado por Git).

Esta comparación depende de competencias, servicios, SLA, plantillas, elegibilidad, IA y escalado sintéticos. Los IC95% t pareados son exploratorios y no corrigen multiplicidad ni la selección del máximo observado. R/N no mide exactitud real. El coste de información de P5 cuando examina matching y termina usando P3 no se contabiliza, por lo que su sensibilidad de coste es optimista. La cola es ilimitada; incumplir un deadline no descarta una alerta.

**Conclusión acotada:** bajo la sobrecarga sintética ρ=1,25 existe evidencia exploratoria de mayor rendimiento esperado por alerta sin aumentar plantilla para P1 y para P4/P5, incluso con la latencia hipotética configurada en los dos últimos. No hay mejora general en las demás cargas. Esta campaña no observó asignaciones conjuntas múltiples; no identifica un efecto incremental de matching. Las diferencias de P4/P5 deben atribuirse a sus reglas efectivas de selección central y su latencia supuesta, sin separar causalmente información global de prioridad temporal.
