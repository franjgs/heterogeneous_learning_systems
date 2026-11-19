# HLS-B: selección D1/P1 por tasa de llegada observada

**Estado de esta campaña:** desarrollo exploratorio, seis semillas nuevas por escenario. La [validación independiente posterior](SOC_HLSB_VALIDATION_RESULTS.md) usa otras 100 semillas por escenario y no se mezcla aquí. D1, P1 y HLS-A conservaron sus reglas. Las trazas y el escalado fueron idénticos entre políticas dentro de cada escenario y semilla.

## Estimador y capacidad

En el instante (t), para el pool correspondiente, HLS-B calcula

\[
\widehat\lambda_w(t)=\frac{\#\{a:t-w<arrival_a\le t\}}{w},\qquad
\widehat\rho_w(t)=\widehat\lambda_w(t)/\mu_{equipo}.
\]

La ventana anterior al inicio del episodio cuenta como cero, lo que produce arranque conservador. Solo se añaden llegadas cuando el motor las incorpora a la cola. La capacidad \(\mu_{equipo}\) se calcula **antes del episodio** con el LP fluido de `calibrate_a1_scenarios.effective_capacity`: maximiza flujo común sujeto a una hora de servicio por analista y elegibilidad por clase, usando roster, servicios y mezcla de clases configurados. No recibe ρ nominal, semilla, calendario de cambios ni outcomes. Los pools L1/L2 tienen estimadores y estados separados. El LP supone mezcla conocida y fracciones de servicio divisibles; no representa automáticamente congestión por clase, variación de disponibilidad o capacidad de horizonte finito.

HLS-B inicia en D1; activa P1 si \(\widehat\rho\ge h\), vuelve a D1 si \(\widehat\rho\le l\) y conserva modo entre ambos valores. Solo cambia el despachador de la época siguiente; D1 y P1 originales siguen decidiendo las asignaciones. No introduce latencia o coste nuevo.

## Diseño fijado y trazabilidad

La [configuración](config/soc_hlsb_development.json) fija semillas `261180000–261180005`, H=24 h y D=24 h, roster y parámetros de servicio de D1/P1 confirmatorio. Candidatos: ventanas 2 y 4 h cruzadas con \((l,h)=(1,00;1,15)\) y \((1,05;1,20)\). Escenarios: ρ=1,00 y 1,25 constantes; ρ=0,85 durante 0–8 h seguido de 1,25 durante 8–24 h; ρ=1,25 durante 0–12 h seguido de 0,85 durante 12–24 h. Los tramos de sobrecarga duran 16 y 12 h. No hay batching. Se generó una traza por celda y semilla, compartida por D1, P1, HLS-A y cuatro HLS-B. `results/soc_hlsb_development/episodes.csv` guarda 168 ejecuciones política–episodio y un hash idéntico de la traza en los siete brazos de cada una de las 24 parejas; `modes.csv` guarda decisiones y tasas estimadas. El [runner](run_soc_hlsb_development.py) reproduce los datos.

## R/N terminal medio (seis semillas; desarrollo)

| Escenario | D1 | P1 | HLS-A | B 2h/1,00–1,15 | B 2h/1,05–1,20 | B 4h/1,00–1,15 | B 4h/1,05–1,20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| ρ=1,00 | 0,6732 | 0,6361 | 0,6437 | 0,6659 | 0,6685 | 0,6688 | **0,6708** |
| ρ=1,25 | 0,5142 | 0,6223 | 0,6221 | 0,6268 | 0,6287 | **0,6313** | 0,6290 |
| Moderada→sobrecarga | 0,6573 | 0,6365 | 0,6427 | 0,6528 | **0,6554** | 0,6533 | 0,6546 |
| Sobrecarga→recuperación | 0,6684 | 0,6364 | 0,6379 | 0,6625 | 0,6632 | 0,6616 | **0,6634** |

Promediando las cuatro celdas con el mismo peso, B 4h/1,05–1,20 obtuvo **0,6545**, mayor media entre los cuatro candidatos (otras: 0,6520–0,6540). Sus diferencias pareadas medias fueron: frente a D1 −0,0023 (ρ=1,00), +0,1148 (ρ=1,25), −0,0026 (moderada→sobrecarga) y −0,0050 (recuperación); frente a P1 +0,0348, +0,0066, +0,0182 y +0,0270, respectivamente. Frente a HLS-A: +0,0272, +0,0069, +0,0120 y +0,0255. Son diferencias de **desarrollo** con seis semillas, no inferencia confirmatoria. La configuración 4h/1,05–1,20 queda seleccionada solo como candidata de desarrollo; no se ajustó por escenario.

## Detección y estabilidad

Para esa candidata, tras las primeras 4 h, la media de \(\widehat\rho\) en las épocas de despacho fue 1,001 (DE 0,096) en ρ=1,00 y 1,252 (DE 0,105) en ρ=1,25. Esto indica separación de los regímenes estacionarios simulados. La fracción de decisiones L1 en P1 fue 7,7 %, 60,1 %, 43,8 % y 36,5 % en los cuatro escenarios de la tabla. Las fracciones de **tiempo de reloj** en P1 durante H fueron 8,2 %, 77,7 %, 50,0 % y 41,0 %. Los cambios medios L1 por episodio fueron 1,00; 2,33; 2,00; 2,33. La banda 2h/1,00–1,15 produjo 7,33 cambios en ρ=1,00 frente a 1,00 con la candidata.

En moderada→sobrecarga, las seis realizaciones estaban en D1 inmediatamente antes de 8 h y activaron P1 entre 2,09 y 5,64 h después (media 3,24 h). En sobrecarga→recuperación, las seis estaban en P1 antes de 12 h y volvieron a D1 entre 0,89 y 3,29 h después (media 2,03 h). Se trata de detección observada de presión, no de conocimiento del calendario. La tasa estimada solo puede reaccionar cuando llegan alertas, y la ventana de 4 h retrasa necesariamente la respuesta.

## Resultados negativos y límites

HLS-B conserva casi todo R/N de D1 en ρ=1,00 y supera a HLS-A en las cuatro celdas de desarrollo. Sin embargo, D1 fijo obtuvo mayor R/N en ambos escenarios variables. La sobrecarga de 8–24 h no produjo por sí sola una ventaja terminal del supervisor sobre D1: el estado inicial, los deadlines y la recuperación pueden dominar el agregado. El coste de estimación y observación no se modeló; no se puede inferir ventaja operativa real. La capacidad LP usa una mezcla de clases supuesta y puede desviarse bajo cambios de composición o elegibilidad. Las métricas R/N son calidad esperada modelada y SLA terminal por alerta admitida; las escaladas finalizan en L2.

Pasaron 74 tests relevantes, incluido un test de causalidad que conserva idénticas las decisiones antes de introducir llegadas futuras; los resultados con y sin el nuevo brazo comparten trazas. La campaña confirmatoria anterior no se reutilizó como desarrollo y permanece intacta.

**Decisión tomada tras este piloto:** validar HLS-B independientemente como hipótesis condicionada. El [resultado posterior](SOC_HLSB_VALIDATION_RESULTS.md) confirma una ventaja en el promedio sintético prefijado, dominada por sobrecarga estacionaria, sin ventaja individual concluyente en las transiciones.
