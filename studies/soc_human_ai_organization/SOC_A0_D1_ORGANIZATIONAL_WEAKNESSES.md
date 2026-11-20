# A0 — Debilidades organizativas de D1

Diagnóstico ejecutado sobre 18 episodios: tres cargas (0,85; 1,00; 1,25) y seis semillas 261140000–261140005, subconjunto predefinido de A0. H=24 h, D=24 h, seis L1 y tres L2. No se comparan políticas ni se modifica el motor.

## Modelo e indicadores

Se reconstruye el estado desde llegadas e intervalos de servicio, respetando liberaciones y llegadas antes del despacho. Las duraciones son deterministas por analista/clase. h=d−t−s; p=competencia×(1−0,35×dificultad), proxy de calidad de A0; U=p·1[t+s≤d]. La dificultad es información del evaluador: no se entrega a D1 ni se propone un controlador que la observe. Estos indicadores no representan exactitud empírica.

Para cada selección j se examinan todas las alternativas k elegibles pendientes para el mismo analista. V(j,k)=p_j·1[t+s_j≤d_j]+p_k·1[t+s_j+s_k≤d_k]. L_orden=max(0,V(k,j)−V(j,k)). Se registra el máximo por selección, sin sumar pérdidas solapadas. Inversión significa h_k<h_j; no implica ganancia. El contraste supone dos servicios consecutivos del mismo pool; para alertas escaladas una mejora L1 no garantiza SLA terminal L2.

L_asig compara dos asignaciones simultáneas ejecutadas con su intercambio, únicamente si ambas parejas cruzadas son elegibles. No permite mover investigaciones iniciadas. El archivo de asignaciones ordena por tiempo/analista: la interpretación individual es inequívoca aquí porque no aparecen pares simultáneos; no generalizar esta reconstrucción a despachos múltiples sin registrar su orden real.

I_idle se mide después de todos los inicios del timestamp. Los tiempos de bloqueo integran intervalos entre eventos: existe al menos una alerta pendiente con todos sus elegibles ocupados. El bloqueo crítico restringe a prioridad high. Se distingue ocupación de elegibles de ocupación de todo el pool. Son horas de reloj, no suma de esperas de alertas.

R(c)=Σ p_final·1[fin terminal≤min(deadline,c)] para todas las admitidas. La calidad media usa sólo completadas; R/N y SLA usan todas las admitidas. Fin terminal es L2 cuando hay escalado.

## Metodología y reproducibilidad

Runner: `analyze_a0_weaknesses.py`; reutiliza configuración y roster del runner A0. Resultados locales ignorados: `results/soc_a0_weaknesses/{episodes.csv,decisions.csv,summary.json}`. No hubo búsqueda de parámetros. Se regeneraron únicamente 18 trayectorias porque A0 no conservaba asignaciones individuales completas. Las métricas de espera, utilización e incumplimientos por prioridad del piloto amplio siguen en A0; este incremento añade los indicadores de decisión y R.

## Resultados numéricos

Frecuencias agregadas sobre asignaciones individuales de todo el episodio, incluido drenaje. Las duraciones se presentan separadas por corte; el contador de decisiones repetido en cada fila de episodes.csv corresponde siempre al episodio completo.

|ρ|Asignaciones L1|Con alternativas|Inversiones|Inversión con ganancia|Selecciones con L_orden>0|L positivo medio|
|---:|---:|---:|---:|---:|---:|---:|
|0.85|3459|2034 (58.8%)|562 (16.2%)|0|0 (0.0%)|0.0000|
|1.0|4021|3632 (90.3%)|1096 (27.3%)|0|0 (0.0%)|0.0000|
|1.25|5045|4945 (98.0%)|1619 (32.1%)|291|1484 (29.4%)|0.6219|

|ρ|Bloqueo L1 H / H+D (h)|Bloqueo high H / H+D (h)|Todo L1 ocupado con high esperando, H (h)|SLA H / terminal|R/N H / terminal|Calidad completadas terminal|
|---:|---:|---:|---:|---:|---:|---:|
|0.85|15.489 / 15.652|3.193 / 3.193|2.956|0.9775 / 0.9942|0.6444 / 0.6556|0.6595|
|1.0|23.044 / 24.491|5.241 / 5.246|5.034|0.9285 / 0.9935|0.6274 / 0.6698|0.6741|
|1.25|23.731 / 31.301|12.996 / 13.637|12.989|0.5973 / 0.7780|0.4142 / 0.5346|0.6767|

No se observaron pares simultáneos intercambiables, L_asig positivo, ni tiempo ocioso con trabajo elegible en ningún pool. El conflicto presente definido como elegir una tarea atendible por otro libre mientras queda otra dependiente exclusivamente del elegido también tuvo frecuencia cero. Esto no descarta costes de oportunidad intertemporales, que el indicador no identifica. L2 tuvo 165/190/242 asignaciones por carga; ninguna pérdida de orden positiva. Su bloqueo high en H fue 0,016/0,106/0,046 h de media.

## Ejemplos reproducibles y distribución

L_orden positivo: mínimo 0.0000, mediana 0.6701, máximo 0.8854. No se suma como pérdida global.

|Semilla|Pool|t (h)|Analista|Elegida|Alternativa|L_orden|
|---|---|---:|---|---|---|---:|
|261140000|L1|16.248491379274448|L1-03|sim-00000540|sim-00000165|0.5850151012496086|
|261140000|L1|16.332594622248557|L1-02|sim-00000523|sim-00000439|0.6793292047609176|
|261140000|L1|16.3751459887851|L1-04|sim-00000165|sim-00000439|0.03909211497683751|

Los IDs de estos ejemplos son sintéticos. Se recuperan con el runner, la semilla y el timestamp.

## Interpretación, incertidumbre y conclusión

Se demuestra en estas trayectorias la existencia de selecciones localmente dominadas bajo el contraste de dos servicios en sobrecarga. No se demuestra una pérdida terminal recuperable de igual magnitud. Muchas inversiones no afectan al indicador binario de plazo porque ambas tareas cumplen o ambas incumplen. A cargas menores este indicador no detectó pérdida positiva: no demuestra optimalidad de D1.

Los bloqueos crecen con la carga y casi coinciden con ocupación de todo L1 en sobrecarga. La causalidad organizativa no queda identificada: no hubo comparación contrafactual de episodios. No se halló ociosidad factible ni oportunidad de intercambio conjunto en estas trazas continuas. La baja concurrencia limita la identificación de matching, no la capacidad general del motor.

Seis semillas constituyen evidencia exploratoria; las decisiones dentro de episodio no son observaciones independientes. Las tablas no son intervalos confirmatorios ni estimaciones GMV. Competencias, tiempos, elegibilidad, calidad y deadlines son hipotéticos. El contraste local omite otras tareas, disponibilidad futura y propagación L2. La dificultad sólo interviene en valoración del evaluador, no en la decisión.

P1 puede cambiar el orden temporal, pero priorizar menor holgura no garantiza aumentar V cuando la tarea ya es irrecuperable. P2 cambia calidad; P3 cambia uso de elegibilidad; sus beneficios no se deducen de estos resultados. P4/P5 tienen escasa base de identificación conjunta bajo este despacho y estas trazas.

**Dictamen:** existe fundamento para comparar el orden local frente a D1 bajo sobrecarga con métricas terminales y de calidad comunes. No existe evidencia aquí para afirmar que P1–P5 corregirán las pérdidas ni para atribuir beneficio a matching. A0 queda cerrado como diagnóstico exploratorio; la comparación deberá admitir resultados nulos y conservar los regímenes sin pérdidas detectadas.
