# Análisis por cohorte del piloto de políticas — NEW MODEL / MODELO NUEVO

> Este análisis utiliza exclusivamente el piloto del **NEW MODEL / MODELO NUEVO**. El manuscrito LaTeX y los estudios confirmatorios del repositorio pertenecen al **OLD MODEL / MODELO VIEJO**; sus magnitudes no son comparables directamente.

## Procedencia y método

Fuente de datos: [`SOC_REFERENCE_V2_24X7_POLICY_PILOT_RESULTS.json`](SOC_REFERENCE_V2_24X7_POLICY_PILOT_RESULTS.json), creado por el piloto documentado en [`SOC_REFERENCE_V2_24X7_POLICY_PILOT.md`](SOC_REFERENCE_V2_24X7_POLICY_PILOT.md), sobre la configuración [`SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json`](config/SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json). El piloto se ejecutó con la configuración de `6ab0934aaf5b9f821b55ca002e05e68e00a68334`; este análisis documental/postproceso parte de `1b19fc8e2a549287d55da1f8f69979d37856283d` en `research/soctra-hls-new-model`. No se ejecutó el simulador.

Se usaron sin selección posterior las diez semillas emparejadas `2026112701`–`2026112710`, con D1, P1 y WAPS/HLS-B para cada una (30 episodios). Las llegadas, recomendaciones y realizaciones ambientales coinciden por semilla entre políticas. El corte común fue 336 h; no hubo tareas pendientes en ese corte.

Las cohortes se determinan por **hora de llegada**, no por hora de finalización: ordinario `[0,96) h`, sobrecarga `[96,120) h` y recuperación `[120,168) h`. Una alerta conserva su cohorte aunque el servicio termine en un régimen posterior. `R/N` mantiene la definición del piloto: suma de competencia modelada de las alertas terminadas dentro del SLA, dividida por todas las alertas admitidas en la cohorte. El SLA es la fracción de la cohorte finalizada antes o en su deadline. La calidad entre completadas incluye tanto finalizaciones puntuales como tardías; por eso no es intercambiable con `R/N`.

Las diferencias son por semilla: **P1−D1**, **WAPS−D1** y **WAPS−P1**. Se informa media, desviación estándar muestral, intervalo t bilateral descriptivo del 95% (9 grados de libertad) y conteo de semillas con diferencia positiva/negativa/empate. No son pruebas confirmatorias. Las tres cohortes de una semilla no son réplicas independientes; los intervalos se calculan dentro de cada contraste de cohorte usando las diez diferencias pareadas de semilla.

## Resultados principales por cohorte

Medias sobre las diez semillas. `n` es el tamaño medio de cohorte; los tamaños y trazas son idénticos entre políticas para una semilla. Calidad significa competencia modelada media entre completadas. Espera es media desde llegada hasta primer servicio, en horas naturales.

| Cohorte de llegada | Política | n medio | R/N terminal | SLA | Calidad completadas | Espera (h) |
|---|---|---:|---:|---:|---:|---:|
| Ordinario | D1 | 1,571.6 | 0.7964 | 99.99% | 0.7965 | 0.103 |
|  | P1 | 1,571.6 | 0.7751 | 100.00% | 0.7751 | 0.104 |
|  | WAPS / HLS-B | 1,571.6 | 0.7800 | 100.00% | 0.7800 | 0.104 |
| Sobrecarga | D1 | 585.2 | 0.7513 | 90.13% | 0.8264 | 3.128 |
|  | P1 | 585.2 | 0.7763 | 100.00% | 0.7763 | 2.974 |
|  | WAPS / HLS-B | 585.2 | 0.7771 | 99.20% | 0.7833 | 3.000 |
| Recuperación | D1 | 614.9 | 0.7858 | 98.50% | 0.7973 | 0.955 |
|  | P1 | 614.9 | 0.7748 | 100.00% | 0.7748 | 0.961 |
|  | WAPS / HLS-B | 614.9 | 0.7920 | 99.37% | 0.7969 | 0.972 |

No hay pendientes al corte en ninguna cohorte. En la sobrecarga, WAPS tiene 0.80% de finalizaciones tardías y D1 9.87%; P1 no tiene tardías. En recuperación, WAPS tiene 0.63% tardías, D1 1.50% y P1 ninguna. Las medias de espera se calculan para el conjunto admitido/completado en el estrato según los registros del piloto; no equivalen al tiempo de servicio.

### Desglose por nivel asignado

R/N, SLA y espera media por ruta L1/L2 (medias por semilla). Los tamaños medios de ruta por cohorte son constantes entre políticas: ordinario L1=1,374.5 y L2=197.1; sobrecarga L1=513.7 y L2=71.5; recuperación L1=536.6 y L2=78.3.

| Cohorte | Nivel | D1 R/N; SLA; espera h | P1 R/N; SLA; espera h | WAPS R/N; SLA; espera h |
|---|---|---|---|---|
| Ordinario | L1 | 0.7878; 99.99%; 0.118 | 0.7639; 100%; 0.118 | 0.7688; 100%; 0.119 |
|  | L2 | 0.8562; 100%; 0.004 | 0.8528; 100%; 0.003 | 0.8584; 100%; 0.003 |
| Sobrecarga | L1 | 0.7369; 88.81%; 3.557 | 0.7652; 100%; 3.382 | 0.7658; 99.09%; 3.411 |
|  | L2 | 0.8577; 100%; 0.007 | 0.8568; 100%; 0.009 | 0.8584; 100%; 0.008 |
| Recuperación | L1 | 0.7752; 98.28%; 1.095 | 0.7627; 100%; 1.102 | 0.7820; 99.28%; 1.114 |
|  | L2 | 0.8587; 100%; 0.003 | 0.8580; 100%; 0.003 | 0.8600; 100%; 0.003 |

La variación de resultados se concentra descriptivamente en L1, la ruta mayoritaria y más presionada; L2 conserva espera muy baja y puntualidad completa en estas trazas. Esto no aísla por sí solo un mecanismo causal de política.

## Diferencias emparejadas por cohorte

En cada celda se da `media (DE), IC95% descriptivo; semillas +/−/=`. Para SLA, media, DE e intervalo están expresados en **puntos porcentuales**; para R/N, en unidades de R/N. “+” significa que la política de la izquierda de la diferencia tiene valor mayor.

| Cohorte | Diferencia | Δ R/N: media (DE), IC95%; +/−/= | Δ SLA (pp): media (DE), IC95%; +/−/= |
|---|---|---|---|
| Ordinario | P1−D1 | −0.02137 (0.00403), [−0.02425, −0.01849]; 0/10/0 | +0.006 (0.020), [−0.008, +0.021]; 1/0/9 |
|  | WAPS−D1 | −0.01639 (0.00475), [−0.01979, −0.01300]; 0/10/0 | +0.006 (0.020), [−0.008, +0.021]; 1/0/9 |
|  | WAPS−P1 | +0.00498 (0.00127), [+0.00407, +0.00588]; 10/0/0 | 0.000 (0.000), [0.000, 0.000]; 0/0/10 |
| Sobrecarga | P1−D1 | +0.02502 (0.05088), [−0.01137, +0.06142]; 6/4/0 | +9.866 (6.546), [+5.183, +14.548]; 9/0/1 |
|  | WAPS−D1 | +0.02580 (0.04715), [−0.00793, +0.05953]; 7/3/0 | +9.068 (5.955), [+4.808, +13.328]; 9/0/1 |
|  | WAPS−P1 | +0.00077 (0.00825), [−0.00513, +0.00668]; 7/3/0 | −0.797 (1.111), [−1.592, −0.002]; 0/6/4 |
| Recuperación | P1−D1 | −0.01098 (0.00798), [−0.01669, −0.00527]; 1/9/0 | +1.496 (1.221), [+0.623, +2.369]; 9/0/1 |
|  | WAPS−D1 | +0.00618 (0.01107), [−0.00174, +0.01410]; 9/1/0 | +0.868 (1.199), [+0.010, +1.725]; 8/1/1 |
|  | WAPS−P1 | +0.01716 (0.00835), [+0.01119, +0.02313]; 9/1/0 | −0.628 (1.239), [−1.514, +0.258]; 0/5/5 |

## Interpretación

1. **Régimen ordinario:** D1 conserva una ventaja clara de R/N: supera a P1 y WAPS en las diez semillas; sus diferencias medias son −0.02137 para P1−D1 y −0.01639 para WAPS−D1. El SLA es prácticamente idéntico (nueve empates); la diferencia de R/N refleja principalmente la competencia modelada de quienes reciben trabajo, no puntualidad.
2. **Sobrecarga:** P1 mejora el SLA sobre D1 en 9.87 pp, con IC descriptivo positivo, pero no hay evidencia clara de que mejore R/N: su diferencia es +0.0250, muy variable y con intervalo que cruza cero. WAPS presenta el mismo patrón respecto de D1: +9.07 pp de SLA y +0.0258 R/N medio, también incierto en R/N. Frente a P1, WAPS queda prácticamente empatado en R/N y tiene SLA inferior en promedio 0.80 pp (6 semillas inferiores y 4 empates). Por tanto, HLS-B no aventaja a P1 en esta cohorte.
3. **Recuperación:** WAPS tiene el mayor R/N medio (0.7920), supera a P1 en 0.01716 y la diferencia emparejada es positiva en 9/10 semillas con IC descriptivo por encima de cero. Frente a D1, la ventaja media es +0.00618 y aparece en 9/10 semillas, pero el intervalo cruza cero; no se demuestra una ventaja clara de R/N frente a D1. WAPS mejora el SLA de D1 en 0.87 pp de media, mientras P1 alcanza 100% y queda 0.63 pp por encima de WAPS, con incertidumbre descriptiva.
4. **¿Queda una ventaja local de HLS-B oculta globalmente?** Sí, en R/N durante recuperación frente a P1, y como señal no concluyente frente a D1. No supera a P1 en R/N durante el pulso ni a D1 en el tramo ordinario. En el total del episodio WAPS−D1 fue −0.00231 y WAPS−P1 +0.00679; la agregación oculta que las diferencias cambian de signo entre cohortes.
5. **Puntualidad y calidad modelada:** por semilla y cohorte se cumple `R/N = SLA × competencia media de las finalizadas dentro del SLA`. En sobrecarga frente a D1, el incremento de SLA explica una contribución positiva importante a R/N (descomposición simétrica descriptiva aproximada +0.0794 de puntualidad para P1−D1, compensada por −0.0544 de calidad entre puntuales; neto +0.0250; WAPS: +0.0733 y −0.0475; neto +0.0258). En recuperación, WAPS frente a D1 tiene calidad media entre puntuales casi igual (0.7970 frente a 0.7978); su incremento de SLA contribuye aproximadamente +0.0069 a R/N y el cambio de calidad −0.0007. Es una identidad contable descriptiva por episodio promediada, no una mediación causal.
6. **Comportamiento adaptativo:** el archivo del piloto registra transiciones de modo de WAPS, pero este análisis por cohorte no identifica el estado/retardo de conmutación como causa de los resultados. La recuperación con mejor R/N es compatible con una ventaja local del comportamiento mixto D1/P1, pero no prueba que la conmutación la produzca.

## Relación cualitativa con OLD MODEL / MODELO VIEJO

El OLD MODEL ya examinó dependencia con carga, intensidad y duración de sobrecarga, deadlines, dimensionamiento, heterogeneidad y retardos de adaptación HLS-B. En ese modelo se observó que la prioridad temporal de P1 protege SLA bajo sobrecarga sintética, mientras puede reducir R/N frente a políticas que priorizan calidad modelada; la ventaja agregada de HLS-B dependió de ponderar escenarios y no se extendió uniformemente a sus escenarios temporales. Este patrón cualitativo de compensación y dependencia del régimen es compatible con el NEW MODEL.

La señal de recuperación NEW MODEL (WAPS por encima de P1 en R/N, pero no concluyentemente de D1) es distinta en detalle, no una contradicción: las cohortes, el ruteo directo por triaje, la investigación única, el roster, servicios, perfil de carga, horizonte y endpoint son diferentes. No se comparan magnitudes absolutas ni se atribuye la diferencia al mismo mecanismo. Las fuentes históricas son [`SOC_HLSB_VALIDATION_RESULTS.md`](../soc_human_ai_organization/SOC_HLSB_VALIDATION_RESULTS.md), [`SOC_HLS_FINAL_OPERATING_MAP.md`](../soc_human_ai_organization/SOC_HLS_FINAL_OPERATING_MAP.md) y [`SOC_PAPER_EVIDENCE_GUIDE.md`](../soc_human_ai_organization/SOC_PAPER_EVIDENCE_GUIDE.md); todo el manuscrito LaTeX actual sigue correspondiendo al OLD MODEL.

## Limitaciones y recomendación

- Diez semillas aportan una lectura exploratoria, no confirmación ni control de multiplicidad para varios contrastes/cohortes. Los IC t son descriptivos y las cohortes dentro de episodio están correlacionadas.
- Una configuración organizativa y un solo perfil de demanda, alpha=0.50, beta=0 y gamma=1 no sustentan generalización a otras mezclas, perfiles ni efectos no neutros de dificultad/FN.
- Competencia es calidad esperada modelada, no tasa empírica de resolución correcta. SLA y R/N tampoco miden coste.
- Las cohortes se evalúan hasta el corte común; su espera/resultados dependen del estado de cola heredado entre regímenes. El análisis no evalúa contrafactuales de política ni descompone causalmente las transiciones de HLS-B.

**Recomendación:** no hace falta una simulación adicional para documentar este hallazgo exploratorio; el piloto conservado ya permite responder que existe una ventaja localizada de WAPS sobre P1 en R/N durante recuperación, pero no establece superioridad sobre D1 ni una ventaja en la sobrecarga. Si la investigación futura pretende afirmar confirmatoriamente una mejora de WAPS frente a D1 en recuperación, entonces sí se requiere un bloque nuevo de semillas emparejadas y un contraste/cohorte preespecificados antes de ejecutar; no se recomienda lanzar ahora una campaña amplia ni ajustar el controlador a estos resultados.
