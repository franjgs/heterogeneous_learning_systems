# Protocolo previo: validación independiente de HLS-B

**Fijado antes de ejecutar la validación:** 19-11-2026. La configuración serializada es [soc_hlsb_validation.json](config/soc_hlsb_validation.json). No se modificarán regla, escenarios ni semillas tras observar resultados.

HLS-B conserva ventana 4 h, retorno a D1 en \(\widehat\rho\le1,05\) y activación P1 en \(\widehat\rho\ge1,20\). Las capacidades L1/L2 se calculan del mismo roster, servicios, elegibilidad y mezcla de clases mediante el LP fluido usado en desarrollo. Se comparan D1, P1, HLS-A 2/3 y HLS-B. H=24 h; D=24 h; escalado y calidad modelada, plazos, analistas y generador son los de desarrollo. Las políticas reciben idéntica traza exógena por escenario y semilla.

**Semillas independientes fijadas:** `261190000–261190099`, 100 enteros. No se solapan con las seis de desarrollo HLS-B (`261180000–005`), las seis HLS-A (`261170000–005`), las 100 confirmatorias D1/P1 (`261160000–099`) ni A0/A3.2. Las mismas semillas se reutilizan en las cuatro celdas, pero cada semilla cuenta una vez en el contraste primario.

Escenarios predefinidos: estacionarios ρ=1,00 y 1,25; ρ=0,85 de 0–8 h y 1,25 de 8–24 h; ρ=1,25 de 0–12 h y 0,85 de 12–24 h. Son exactamente las intensidades y duraciones de desarrollo. La política no observa esas etiquetas ni el calendario. Cohortes de llegada se definen por esos intervalos; el resultado de una cohorte se mide por su finalización hasta H+D, aunque ocurra en otra fase.

El estimando primario es \(\bar\Delta=100^{-1}\sum_s[\frac14\sum_{c=1}^4(R/N)_{B,c,s}-(R/N)_{D1,c,s}]\). La diferencia por episodio usa el número admitido de **su propio escenario**; luego se ponderan escenarios por igual. Prueba t pareada unilateral \(H_0:E[\Delta]\le0\) contra \(H_1:E[\Delta]>0\), α=0,05, con IC bilateral t95 % y frecuencia de semillas favorables. Esta es una distribución sintética de cuatro escenarios, no una prevalencia operativa real. No existe umbral económico mínimo validado.

Análisis secundarios predefinidos: diferencia HLS-B frente a D1, P1 y HLS-A en cada uno de cuatro escenarios (12 comparaciones), pruebas bilaterales con ajuste Holm familiar α=0,05; IC95 % t pareados se muestran como magnitudes descriptivas. También se informan R/N en H, SLA H y H+D, calidad esperada entre completadas, espera L1, colas L1/L2, utilización L1/L2 y R/N/SLA por prioridad y cohorte. La fracción de modo P1 se calcula por decisión y por tiempo de reloj en H; los retardos se miden desde el cambio exógeno hasta la primera entrada al modo correspondiente. Los resultados por cohorte y retardos son descriptivos.

Validación: 100 semillas distintas por celda; hashes y número de alertas admitidas idénticos entre las cuatro políticas; rutas L2 terminales y conservación; recomputación del R/N desde asignaciones; consistencia H frente a H+D; reproducibilidad de una semilla fijada; tests relevantes. No se reutilizarán resultados previos para la prueba.
