# Protocolo fijado: D1 frente a P1

> **OLD MODEL / MODELO VIEJO:** this document records the historical L1-first organizational model and its evidence. Its results remain valid only for that model and do not validate the NEW MODEL. See [MODEL_GENERATIONS.md](../soc_triage_hls_availability_robustness/MODEL_GENERATIONS.md). The current LaTeX manuscript belongs entirely to the OLD MODEL; NEW MODEL transfer is deferred.

**Registro previo a la ejecución:** 19-11-2026. Este documento y `config/soc_confirmatory.json` se fijan antes de observar los resultados de las nuevas semillas. El contraste y los niveles de sensibilidad no se cambiarán a partir de esos resultados. La campaña compara únicamente las implementaciones existentes de D1 y P1.

## Contraste primario

- Escenario: \(\rho=1,25\), tasa \(1,25\times28,41858770124891=35,52323462656114\) alertas/h; H=24 h de admisión y D=24 h de drenaje.
- Hipótesis direccional predefinida: \(H_0:E[\Delta]\leq0\) frente a \(H_1:E[\Delta]>0\), donde \(\Delta=R_{P1}/N-R_{D1}/N\) es la diferencia **por episodio** en H+D.
- \(R/N=N^{-1}\sum_a e_{i(a),k(a)}(1-0,35\,difficulty_a)\,1\{completion_a\leq deadline_a,\ completion_a\leq H+D\}\). La finalización es L2 si la alerta escala. El denominador N contiene todas las alertas admitidas; pendientes y tardías aportan cero. R/N en H usa el mismo N con corte H. Calidad entre completadas usa otro denominador.
- Prueba t pareada unilateral sobre 100 diferencias de episodio, α=0,05; p unilateral y estadístico t con 99 grados de libertad. Se informará también IC bilateral t del 95 %, media, desviación, frecuencia de \(\Delta>0\) y cambio relativo \(\overline\Delta/\overline{R_{D1}/N}\). Si la distribución de diferencias resulta muy asimétrica, se describirá como limitación; no se cambiará la prueba primaria tras mirar resultados.
- No hay umbral económico mínimo validado. Se informarán magnitudes absoluta y relativa sin llamar relevante a una diferencia por decisión económica inventada.

## Parámetros, semillas y emparejamiento

Se reutilizan exactamente `SocReference` y `build_roster` de `soc_parametric_baseline.py`, como en `config/a0_baseline_congestion.json` y `config/soc_policy_comparison.json`: seis L1 (índices 0–5), tres L2, elegibilidad media 2,5 proyectos/L1, perfiles individuales, servicio por analista/clase, mezcla de clases 0,592/0,236/0,172, prioridades 0,50/0,35/0,15, deadlines low/medium/high 12/4/1 h, IA sintética y aceptación hipotética fija de recomendación para escalar. Latencia y coste de coordinación son cero; D1/P1 no los necesitan. El simulador y las políticas permanecen intactos.

**Semillas nuevas fijadas:** enteros consecutivos `261160000–261160099` (100). No aparecen en A0 (`261140000–261140029`), A3.2 (`261132000–261132019`) ni la comparación exploratoria (`261140000–261140019`). Las mismas 100 semillas se reutilizan en todos los escenarios predefinidos para mejorar precisión pareada entre condiciones; no constituyen replicaciones independientes adicionales del contraste primario.

En cada escenario/semilla se genera una sola secuencia exógena y se entrega idéntica a D1 y P1. Se verificará hash de IDs, llegadas, clases, prioridad, dificultad, recomendación y deadlines; también N y la decisión fija de escalado. D1 usa su RNG de orden propio, reproducible con la semilla; P1 tiene desempates deterministas. Esa aleatoriedad endógena forma parte de cada política y no altera la identidad de exógenos ni invalida la diferencia pareada a nivel de episodio. La calidad se calcula como esperanza; no hay muestra Bernoulli de resolución que requiera acoplamiento adicional.

## Dependencia del régimen y multiplicidad

Se fijan cuatro cargas secundarias: \(\rho=0,85;1,00;1,10;1,15\) con tasas \(\rho\times28,41858770124891\) alertas/h y el mismo roster y mezcla. Junto con 1,25 forman la familia descriptiva de cinco cargas. Se reportarán medias, diferencias pareadas e IC95 % bilaterales por escenario. Para cualquier declaración inferencial de mejora en las **ocho comparaciones secundarias** (cuatro cargas y cuatro sensibilidades) se aplicará Holm con α familiar 0,05 a sus pruebas bilaterales. El primario unilateral es único y mantiene su α predefinido. No se seleccionarán cargas tras observar resultados.

## Robustez mínima, un factor cada vez

En \(\rho=1,25\), variar únicamente:

1. **Deadline:** multiplicar los tres plazos nominales por 0,75 o 1,25. Son perturbaciones simétricas de ±25 % sobre supuestos hipotéticos; se conservan demanda, analistas, servicio y demás variables. Las llegadas, clases y recomendaciones deben coincidir con el escenario primario bajo la misma semilla, mientras el deadline cambia como corresponde.
2. **Heterogeneidad de competencia:** para cada pool y clase, calcular \(\bar e_k\) entre analistas elegibles del roster base y fijar \(e'_{ik}=\bar e_k+g(e_{ik}-\bar e_k)\), con \(g=0,75\) o \(1,25\). Se conservan las medias por clase, elegibilidad y velocidades; se comprueba que todos los valores sigan en [0,1]. Esta perturbación no cambia la plantilla ni supone aprendizaje. La calidad modelada y la selección D1 pueden cambiar, como parte de la sensibilidad.

Los cuatro contrastes de robustez son secundarios. Se mantiene la misma tasa 35,52323462656114/h. No se ajusta P1 ni se combinan ambos factores.

## Salidas, análisis del mecanismo y validación

Por semilla y política se guardarán R/N en H y H+D, R sin normalizar, SLA en ambos cortes, completadas y pendientes, calidad esperada entre completadas, espera media/P95, cola media/máxima L1/L2, utilización L1/L2 y estratos de prioridad y clase. Se guardarán diferencias pareadas y hashes de trazas. El análisis del mecanismo comparará cambios de puntualidad, calidad, espera, colas y bloqueos de prioridad alta; interpretar estos últimos como diagnóstico de capacidad. La compatibilidad con oportunidades de orden A0 se describirá sin sumarlas como ganancias recuperables ni atribuirles toda la diferencia de episodio.

Se verificará unicidad, elegibilidad, conservación, ruta L2 terminal, separación H/H+D, 100 semillas distintas, ausencia de solapamiento con semillas exploratorias y reproducción determinista de una traza/corrida seleccionada **sin escogerla por resultado**. Resultados y figuras estarán en `results/soc_confirmatory_d1_p1/`, excluido de Git. El informe final distinguirá resultado primario, secundarios, limitaciones y validez externa; no modificará resultados previos.
