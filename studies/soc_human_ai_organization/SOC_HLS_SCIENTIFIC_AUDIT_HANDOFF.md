# SOCTRA–HLS — Transferencia de evidencia para auditoría científica independiente

**Estado:** auditoría descriptiva de evidencia guardada. No se ejecutaron simulaciones ni se modificaron políticas, motor o configuraciones. Los resultados nuevos de dominio operativo y sensibilidades son exploratorios; solo se identifica como confirmatorio lo que procede de la validación independiente previa.

## 1. Alcance, fuentes y estimandos

Se examinaron íntegramente [SOC_HLS_OPERATING_REGIONS.md](SOC_HLS_OPERATING_REGIONS.md), [SOC_HLS_OVERLOAD_DURATION.md](SOC_HLS_OVERLOAD_DURATION.md), [SOC_HLS_REALISTIC_DYNAMICS.md](SOC_HLS_REALISTIC_DYNAMICS.md) y [SOC_HLSB_VALIDATION_RESULTS.md](SOC_HLSB_VALIDATION_RESULTS.md), junto con las dos configuraciones, runners y CSV locales. Las cifras que siguen se recalcularon desde `episodes.csv`, `timeseries.csv`, `modes.csv`, `cohorts.csv`, `priority.csv` y ambos manifiestos. El estimando terminal es H+D=48 h; R/N es esperanza modelada de calidad de alertas finalizadas antes del deadline dividida por todas las admitidas, no exactitud empírica observada.

El estudio central fija (H=24) h de admisión, (D=24) h de drenaje, inicio de pulso (t=4) h y carga base ρ=0.85. Para cada perfil, (T_{low}=24-(4+T_{pulso})) es el tramo de recuperación **dentro de admisión**; el drenaje posterior no se incorpora en Γ. (B=(ρ_{alta}-1)T_{pulso}) y Γ=B/[(1-ρ_{rec})T_{low}]); son aproximaciones fluidas. Los deadlines de referencia son crítica/alta/baja = 1/4/12 h. HLS-B congelada: ventana 4 h, histéresis 1.05/1.20. Roster central: 6 L1 y 3 L2, elegibilidad L1 media 2.5/3 clases, perfiles de competencia y velocidad deterministas del modelo.

### Tabla central completa (20 semillas por celda)

| Escenario | ρ habitual | ρ pulso | Duración pulso | Recuperación en H | H / D | Admitidas medias | B | Γ | D1 R/N | P1 R/N | HLS-B R/N | HLS-B−D1 [IC95] | HLS-B−P1 [IC95] | Mejor fija (media) | HLS-B−mejor fija [IC95] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| B08_rho110_d8 | 0.85 | 1.10 | 8 h | 12 h @ 0.85 | 24/24 h | 632.50 | 0.80 | 0.444 | 0.66694 | 0.63392 | 0.66479 | -0.00215 [-0.00376; -0.00053] | +0.03087 [+0.02866; +0.03309] | D1 0.66694 | -0.00215 [-0.00376; -0.00053] |
| B08_rho120_d4 | 0.85 | 1.20 | 4 h | 16 h @ 0.85 | 24/24 h | 615.70 | 0.80 | 0.333 | 0.66471 | 0.63389 | 0.66311 | -0.00159 [-0.00265; -0.00053] | +0.02922 [+0.02705; +0.03139] | D1 0.66471 | -0.00159 [-0.00265; -0.00053] |
| B08_rho140_d2 | 0.85 | 1.40 | 2 h | 18 h @ 0.85 | 24/24 h | 609.50 | 0.80 | 0.296 | 0.66370 | 0.63590 | 0.66270 | -0.00100 [-0.00183; -0.00018] | +0.02680 [+0.02433; +0.02926] | D1 0.66370 | -0.00100 [-0.00183; -0.00018] |
| B16_rho110_d16 | 0.85 | 1.10 | 16 h | 4 h @ 0.85 | 24/24 h | 698.85 | 1.60 | 2.667 | 0.66788 | 0.63398 | 0.66375 | -0.00413 [-0.00695; -0.00132] | +0.02977 [+0.02722; +0.03231] | D1 0.66788 | -0.00413 [-0.00695; -0.00132] |
| B16_rho120_d8 | 0.85 | 1.20 | 8 h | 12 h @ 0.85 | 24/24 h | 657.30 | 1.60 | 0.889 | 0.66898 | 0.63335 | 0.66304 | -0.00595 [-0.00739; -0.00450] | +0.02968 [+0.02769; +0.03167] | D1 0.66898 | -0.00595 [-0.00739; -0.00450] |
| B16_rho140_d4 | 0.85 | 1.40 | 4 h | 16 h @ 0.85 | 24/24 h | 638.40 | 1.60 | 0.667 | 0.66760 | 0.63464 | 0.66333 | -0.00427 [-0.00554; -0.00301] | +0.02870 [+0.02685; +0.03054] | D1 0.66760 | -0.00427 [-0.00554; -0.00301] |
| nom_r125_d2 | 0.85 | 1.25 | 2 h | 18 h @ 0.85 | 24/24 h | 600.05 | 0.50 | 0.185 | 0.66120 | 0.63538 | 0.66114 | -0.00007 [-0.00020; +0.00006] | +0.02576 [+0.02324; +0.02828] | D1 0.66120 | -0.00007 [-0.00020; +0.00006] |
| nom_r125_d4 | 0.85 | 1.25 | 4 h | 16 h @ 0.85 | 24/24 h | 620.95 | 1.00 | 0.417 | 0.66583 | 0.63486 | 0.66273 | -0.00311 [-0.00427; -0.00194] | +0.02786 [+0.02551; +0.03022] | D1 0.66583 | -0.00311 [-0.00427; -0.00194] |
| nom_r125_d8 | 0.85 | 1.25 | 8 h | 12 h @ 0.85 | 24/24 h | 668.30 | 2.00 | 1.111 | 0.66757 | 0.63368 | 0.66180 | -0.00577 [-0.00854; -0.00300] | +0.02812 [+0.02641; +0.02984] | D1 0.66757 | -0.00577 [-0.00854; -0.00300] |
| nom_r125_d12 | 0.85 | 1.25 | 12 h | 8 h @ 0.85 | 24/24 h | 716.85 | 3.00 | 2.500 | 0.65068 | 0.63369 | 0.65773 | +0.00706 [-0.00624; +0.02036] | +0.02404 [+0.02226; +0.02583] | D1 0.65068 | +0.00706 [-0.00624; +0.02036] |
| nom_r125_d16 | 0.85 | 1.25 | 16 h | 4 h @ 0.85 | 24/24 h | 765.20 | 4.00 | 6.667 | 0.61784 | 0.63408 | 0.65258 | +0.03474 [+0.01815; +0.05132] | +0.01850 [+0.01533; +0.02168] | P1 0.63408 | +0.01850 [+0.01533; +0.02168] |
| nom_r125_d8_fastrec | 0.85 | 1.25 | 8 h | 12 h @ 0.70 | 24/24 h | 618.10 | 2.00 | 0.556 | 0.66731 | 0.63418 | 0.65920 | -0.00811 [-0.00951; -0.00670] | +0.02502 [+0.02263; +0.02742] | D1 0.66731 | -0.00811 [-0.00951; -0.00670] |

La cantidad de alertas de la tabla es la media **admitida observada** entre episodios (idéntica entre políticas dentro de perfil/semilla), no el volumen esperado. Gamma está definida en los 12 perfiles: todos tienen (T_{low}>0) y ρrec<1. La unidad de B es “horas de exceso de carga” respecto a ρ=1. No se fuerza que perfiles con B igual tengan la misma respuesta.

**Corrección de trazabilidad:** el informe operativo previo imprimió 670.7 como llegadas esperadas para `nom_r125_d8_fastrec`, aplicando por error ρrec=0.85 a sus 12 h finales. La configuración y runner usan ρrec=0.70. La expectativa correcta es μL1[0.85·4 + 1.25·8 + 0.70·12] ≈ 619.5; el CSV muestra 618.1 admitidas medias. El valor no se sustituye en el informe previo, pero esta transferencia usa el cálculo compatible con la configuración y los episodios guardados.

Por medias de celda, HLS-B > D1 en 2/12 escenarios; > P1 en 12/12; > ambas en 2/12; < ambas en 0/12. IC95 pareado incluye cero en HLS-B−D1 en 2/12 (d2 y d12) y en HLS-B−P1 en 0/12. Por el criterio nominal bilateral sin ajuste, solo d16 excluye cero para ambos contrastes; esto no convierte la exploración en confirmación. El d12 es superior a D1 por media, pero su IC cruza cero. Mejor fija seleccionada en la misma muestra perfil a perfil; en consecuencia HLS-B−mejor-fija es retrospectivo y no un contraste confirmatorio con cobertura garantizada.

## 2. Sensibilidad a SLA

Se reutilizaron los escenarios de 8 y 16 h, con 20 semillas nuevas (261250000–261250019), tres políticas y H/D=24/24 h. Escala: T0=.75/1/1.25 con factores 4/12. Separación: factores 2/8 y 8/16 con T0=1. La tabla reporta cambios de cada política respecto a la condición de referencia de **la misma duración y semillas**; en el orden D1/P1/HLS-B. Los intervalos son t pareados, 19 gl.

| Demanda | Configuración SLA (Tcrit:Talta:Tbaja) | Tpulso/Tcrit | D1 R/N | P1 R/N | HLS-B R/N | HLS-B−D1 [IC95] | HLS-B−P1 [IC95] | Δ vs ref D1 | Δ vs ref P1 | Δ vs ref HLS-B |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---:|
| ρnormal=.85, ρpulso=1.25, 8 h | scale_075 (0.75:3:9) | 10.67 | 0.65436 | 0.63362 | 0.65817 | +0.00380 [-0.00477; +0.01238] | +0.02455 [+0.02035; +0.02875] | -0.01610 | -0.00142 | -0.00551 |
| ρnormal=.85, ρpulso=1.25, 8 h | reference (1:4:12) | 8.00 | 0.67046 | 0.63504 | 0.66368 | -0.00678 [-0.00815; -0.00541] | +0.02865 [+0.02702; +0.03027] | +0.00000 | +0.00000 | +0.00000 |
| ρnormal=.85, ρpulso=1.25, 8 h | scale_125 (1.25:5:15) | 6.40 | 0.67229 | 0.63696 | 0.66535 | -0.00694 [-0.00856; -0.00531] | +0.02839 [+0.02674; +0.03005] | +0.00183 | +0.00192 | +0.00167 |
| ρnormal=.85, ρpulso=1.25, 8 h | separation_2_8 (1:2:8) | 8.00 | 0.64163 | 0.63455 | 0.65163 | +0.01000 [+0.00098; +0.01903] | +0.01708 [+0.00776; +0.02640] | -0.02883 | -0.00049 | -0.01205 |
| ρnormal=.85, ρpulso=1.25, 8 h | separation_8_16 (1:8:16) | 8.00 | 0.67080 | 0.63504 | 0.66368 | -0.00712 [-0.00858; -0.00566] | +0.02865 [+0.02702; +0.03027] | +0.00034 | +0.00000 | +0.00000 |
| ρnormal=.85, ρpulso=1.25, 16 h | scale_075 (0.75:3:9) | 21.33 | 0.51174 | 0.59539 | 0.60187 | +0.09013 [+0.07385; +0.10641] | +0.00648 [-0.00195; +0.01491] | -0.11297 | -0.03884 | -0.05089 |
| ρnormal=.85, ρpulso=1.25, 16 h | reference (1:4:12) | 16.00 | 0.62472 | 0.63424 | 0.65276 | +0.02804 [+0.01254; +0.04355] | +0.01852 [+0.01586; +0.02118] | +0.00000 | +0.00000 | +0.00000 |
| ρnormal=.85, ρpulso=1.25, 16 h | scale_125 (1.25:5:15) | 12.80 | 0.66751 | 0.63578 | 0.65661 | -0.01089 [-0.01645; -0.00534] | +0.02083 [+0.01932; +0.02234] | +0.04279 | +0.00155 | +0.00385 |
| ρnormal=.85, ρpulso=1.25, 16 h | separation_2_8 (1:2:8) | 16.00 | 0.44543 | 0.52031 | 0.53352 | +0.08809 [+0.07652; +0.09966] | +0.01321 [+0.00396; +0.02246] | -0.17929 | -0.11393 | -0.11924 |
| ρnormal=.85, ρpulso=1.25, 16 h | separation_8_16 (1:8:16) | 16.00 | 0.67261 | 0.63444 | 0.65490 | -0.01772 [-0.01974; -0.01569] | +0.02046 [+0.01905; +0.02186] | +0.04789 | +0.00020 | +0.00214 |

La referencia SLA de esta campaña usa semillas propias, distintas de la campaña central; por eso no se compara su media directamente con el R/N central. Dentro de cada duración, la lista de hashes contiene exactamente un hash por semilla a través de las cinco configuraciones SLA, y el runner calcula ese hash sin incluir el deadline. Son las mismas alertas, clases, dificultad, recomendación, llegada e IDs; solo cambia la fecha límite. Los contrastes de cambio vs referencia comparten las mismas semillas y trazas y son descriptivos.

## 3. Sensibilidad al dimensionamiento

Campaña secundaria: d=8 y 16 h, 20 semillas, H/D=24/24. Se mantuvo fija la **demanda absoluta**: λnormal=0.85·28.4186=24.1558 alertas/h, λpulso=1.25·28.4186=35.5232 alertas/h, recuperación vuelve a λnormal. ρ se recalculó como λ/μ de L1 de cada roster; no se fijó el rho al variar la plantilla. Se mantuvieron distribución de proyecto 0.592/0.236/0.172, elegibilidad L1 media 2.5/3 proyectos, competencias y velocidades existentes; L2 es elegible en las tres clases. El ciclo de elegibilidad L1 es: tres perfiles elegibles para los tres grupos, después top5+next5, next5+tail, top5+tail; vuelve al inicio si hay más de seis. Los perfiles de competencia y velocidad L1/L2 son los definidos en el modelo y se repiten cíclicamente al ampliar la plantilla. Capacidades de L1/L2 de tabla se estiman por LP de capacidad común con mezcla fija/routing modelado. Comparaciones de plantilla no equivalen a intervención aleatoria sobre personal.

| Escenario | n L1×L2 | Elegibilidad/especialización | μL1 / μL2 (alertas/h) | λ normal / pulso | ρ normal / pulso | Admitidas medias | D1 R/N | P1 R/N | HLS-B R/N | HLS-B−D1 [IC95] | HLS-B−P1 [IC95] | Δ vs roster 6×3 (D1/P1/HB) |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| ρnormal=.85,ρpulso=1.25, 8 h | 5×3 | L1 media 2.5 proyectos, patrón cíclico; L2 todas 3 | 23.38/3.84 | 24.16/35.52 | 1.033/1.519 | 664.85 | 0.64543 | 0.63321 | 0.65425 | +0.00882 [-0.00158; +0.01923] | +0.02104 [+0.01419; +0.02789] | -0.02503/-0.00183/-0.00943 |
| ρnormal=.85,ρpulso=1.25, 8 h | 6×2 | L1 media 2.5 proyectos, patrón cíclico; L2 todas 3 | 28.42/2.43 | 24.16/35.52 | 0.850/1.250 | 664.85 | 0.66959 | 0.63448 | 0.66322 | -0.00637 [-0.00770; -0.00505] | +0.02874 [+0.02709; +0.03039] | -0.00086/-0.00056/-0.00046 |
| ρnormal=.85,ρpulso=1.25, 8 h | 6×3 | L1 media 2.5 proyectos, patrón cíclico; L2 todas 3 | 28.42/3.84 | 24.16/35.52 | 0.850/1.250 | 664.85 | 0.67046 | 0.63504 | 0.66368 | -0.00678 [-0.00815; -0.00541] | +0.02865 [+0.02702; +0.03027] | +0.00000/+0.00000/+0.00000 |
| ρnormal=.85,ρpulso=1.25, 8 h | 6×4 | L1 media 2.5 proyectos, patrón cíclico; L2 todas 3 | 28.42/5.09 | 24.16/35.52 | 0.850/1.250 | 664.85 | 0.67057 | 0.63508 | 0.66387 | -0.00670 [-0.00810; -0.00530] | +0.02879 [+0.02709; +0.03049] | +0.00011/+0.00004/+0.00019 |
| ρnormal=.85,ρpulso=1.25, 8 h | 7×3 | L1 media 2.5 proyectos, patrón cíclico; L2 todas 3 | 33.36/3.84 | 24.16/35.52 | 0.724/1.065 | 664.85 | 0.66795 | 0.63670 | 0.66546 | -0.00249 [-0.00439; -0.00059] | +0.02876 [+0.02577; +0.03174] | -0.00251/+0.00167/+0.00178 |
| ρnormal=.85,ρpulso=1.25, 16 h | 5×3 | L1 media 2.5 proyectos, patrón cíclico; L2 todas 3 | 23.38/3.84 | 24.16/35.52 | 1.033/1.519 | 763.55 | 0.45528 | 0.45118 | 0.47113 | +0.01584 [+0.00191; +0.02978] | +0.01995 [+0.01488; +0.02502] | -0.16943/-0.18306/-0.18163 |
| ρnormal=.85,ρpulso=1.25, 16 h | 6×2 | L1 media 2.5 proyectos, patrón cíclico; L2 todas 3 | 28.42/2.43 | 24.16/35.52 | 0.850/1.250 | 763.55 | 0.62391 | 0.63383 | 0.65208 | +0.02817 [+0.01290; +0.04344] | +0.01824 [+0.01562; +0.02087] | -0.00081/-0.00040/-0.00068 |
| ρnormal=.85,ρpulso=1.25, 16 h | 6×3 | L1 media 2.5 proyectos, patrón cíclico; L2 todas 3 | 28.42/3.84 | 24.16/35.52 | 0.850/1.250 | 763.55 | 0.62472 | 0.63424 | 0.65276 | +0.02804 [+0.01254; +0.04355] | +0.01852 [+0.01586; +0.02118] | +0.00000/+0.00000/+0.00000 |
| ρnormal=.85,ρpulso=1.25, 16 h | 6×4 | L1 media 2.5 proyectos, patrón cíclico; L2 todas 3 | 28.42/5.09 | 24.16/35.52 | 0.850/1.250 | 763.55 | 0.62511 | 0.63442 | 0.65280 | +0.02769 [+0.01216; +0.04322] | +0.01838 [+0.01584; +0.02092] | +0.00039/+0.00018/+0.00004 |
| ρnormal=.85,ρpulso=1.25, 16 h | 7×3 | L1 media 2.5 proyectos, patrón cíclico; L2 todas 3 | 33.36/3.84 | 24.16/35.52 | 0.724/1.065 | 763.55 | 0.67898 | 0.63522 | 0.67401 | -0.00496 [-0.00849; -0.00144] | +0.03879 [+0.03540; +0.04218] | +0.05426/+0.00098/+0.02125 |

Los cambios vs 6×3 son diferencias de medias emparejadas (misma semilla/traza); se imprimen como D1/P1/HLS-B para describir el efecto de roster. En `episodes.csv` las cinco plantillas tienen hash y n de admitidas iguales para una duración/semilla; cada una de las cinco configuraciones conserva la demanda física. Las celdas 5×3 cambian ρ normal a 1.033 y pulso a 1.519; 7×3 baja a .724/1.065. Así, el efecto de recursos combina cambio de capacidad con desplazamiento de región de carga.

## 4. Evidencia del mecanismo dinámico

La tabla se calcula a partir de `timeseries.csv` y `modes.csv`. Backlog/trabajo al final del pulso es para HLS-B, en el primer punto de muestreo a t=4+d; colas son alertas no iniciadas, trabajo son horas nominales pendientes por pool. “P1 decisiones” es proporción de registros de historia HLS-B en modo P1 entre los eventos registrados durante [4,4+d), no fracción de tiempo. Activación es el primer evento D1→P1; retorno es primer evento P1→D1 tras fin de pulso. El estado de cola al retorno se toma del punto de 0.5 h más próximo.

| Escenario | Cola L1/L2 al fin pulso | Trabajo L1/L2 (h) al fin | P1 eventos durante pulso | Primera activación P1 (t desde inicio) | Retorno D1 (h tras pulso) | Cola al retorno | Trabajo al retorno (h) | Recuperación D1 cola/trabajo |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| B08_rho110_d8 | 43.65/0.15 | 9.34/0.12 | 13.3% | 8.83 h (8/20) | 2.05 h (6/20) | 56.83 | 13.00 | 7.33 h (6/20) |
| B08_rho120_d4 | 35.50/0.05 | 7.55/0.04 | 10.8% | 7.27 h (11/20) | 2.08 h (11/20) | 36.45 | 8.17 | 8.00 h (10/20) |
| B08_rho140_d2 | 32.35/0.05 | 7.02/0.04 | 3.4% | 6.70 h (9/20) | 3.05 h (9/20) | 33.56 | 7.53 | 9.46 h (13/20) |
| B16_rho110_d16 | 86.50/0.00 | 18.70/0.00 | 29.0% | 12.39 h (18/20) | 1.65 h (10/20) | 97.30 | 21.83 | NR h (0/20) |
| B16_rho120_d8 | 66.65/0.00 | 14.91/0.00 | 41.9% | 8.12 h (18/20) | 1.96 h (17/20) | 66.06 | 14.96 | NR h (0/20) |
| B16_rho140_d4 | 57.25/0.00 | 12.71/0.00 | 37.1% | 6.48 h (19/20) | 2.47 h (19/20) | 50.16 | 11.41 | 11.60 h (5/20) |
| nom_r125_d2 | 22.85/0.00 | 4.86/0.00 | 1.0% | 6.53 h (2/20) | 2.17 h (2/20) | 30.00 | 6.65 | 7.00 h (15/20) |
| nom_r125_d4 | 40.35/0.00 | 8.72/0.00 | 18.4% | 7.07 h (15/20) | 2.15 h (15/20) | 38.07 | 8.63 | 10.41 h (11/20) |
| nom_r125_d8 | 77.45/0.00 | 17.46/0.00 | 53.3% | 7.78 h (20/20) | 1.89 h (20/20) | 71.75 | 16.34 | NR h (0/20) |
| nom_r125_d12 | 114.65/0.00 | 26.00/0.00 | 67.1% | 7.78 h (20/20) | 1.80 h (19/20) | 107.74 | 24.62 | NR h (0/20) |
| nom_r125_d16 | 149.95/0.05 | 34.14/0.04 | 74.3% | 7.78 h (20/20) | 1.80 h (19/20) | 149.05 | 34.11 | NR h (0/20) |
| nom_r125_d8_fastrec | 77.45/0.00 | 17.46/0.00 | 53.3% | 7.78 h (20/20) | 1.46 h (20/20) | 66.15 | 15.08 | 9.18 h (11/20) |

Recuperación D1 de la tabla principal = primer momento postpulso con tres muestras consecutivas (cada 0.5 h) donde tanto cola total como trabajo total no superan sus niveles en t=4. La misma definición puede reconstruirse para las tres políticas desde la serie guardada; la tabla siguiente da las medias observadas y el número de semillas que recuperan antes de 48 h. “NR” indica cero de 20; cuando el denominador es menor de 20, la media se limita a recuperaciones observadas y se informa n. No se interpreta como SLA cumplido. La serie no guarda la composición de backlog por prioridad/clase, así que no se puede reconstruir trabajo pendiente por clase; sí conserva el total por pool. Los registros HLSB conservan presión/pendientes/ocupación por evento, pero no una medida de decisiones contrafactuales no tomadas.

| Escenario | D1: tiempo desde fin del pulso (n/20) | P1 (n/20) | HLS-B (n/20) |
|---|---:|---:|---:|
| B08_rho110_d8 | 7.33 h (6/20) | 7.58 h (6/20) | 7.33 h (6/20) |
| B08_rho120_d4 | 8.00 h (10/20) | 7.75 h (10/20) | 8.32 h (11/20) |
| B08_rho140_d2 | 9.46 h (13/20) | 9.11 h (14/20) | 9.08 h (13/20) |
| B16_rho110_d16 | NR (0/20) | NR (0/20) | NR (0/20) |
| B16_rho120_d8 | NR (0/20) | 9.50 h (1/20) | NR (0/20) |
| B16_rho140_d4 | 11.60 h (5/20) | 11.40 h (5/20) | 11.75 h (6/20) |
| nom_r125_d2 | 7.00 h (15/20) | 7.18 h (17/20) | 7.00 h (15/20) |
| nom_r125_d4 | 10.41 h (11/20) | 8.25 h (8/20) | 10.23 h (11/20) |
| nom_r125_d8 | NR (0/20) | NR (0/20) | NR (0/20) |
| nom_r125_d12 | NR (0/20) | NR (0/20) | NR (0/20) |
| nom_r125_d16 | NR (0/20) | NR (0/20) | NR (0/20) |
| nom_r125_d8_fastrec | 9.18 h (11/20) | 9.14 h (11/20) | 8.96 h (12/20) |

### R/N terminal por cohorte de llegada

Promedios por semilla, ponderados por alertas admitidas de la cohorte; outcome hasta H+D. “pre”=[0,4), “pulso”=[4,4+d), “post”=[4+d,24).

| Escenario | Cohorte | n medio | D1 | P1 | HLS-B |
|---|---|---:|---:|---:|---:|
| B08_rho110_d8 | pre | 96.50 | 0.6567 | 0.6391 | 0.6567 |
| B08_rho110_d8 | pulse | 249.60 | 0.6740 | 0.6330 | 0.6690 |
| B08_rho110_d8 | post | 286.40 | 0.6638 | 0.6331 | 0.6637 |
| B08_rho120_d4 | pre | 96.50 | 0.6569 | 0.6395 | 0.6568 |
| B08_rho120_d4 | pulse | 135.40 | 0.6757 | 0.6324 | 0.6682 |
| B08_rho120_d4 | post | 383.80 | 0.6624 | 0.6330 | 0.6627 |
| B08_rho140_d2 | pre | 96.50 | 0.6569 | 0.6393 | 0.6567 |
| B08_rho140_d2 | pulse | 80.15 | 0.6756 | 0.6342 | 0.6687 |
| B08_rho140_d2 | post | 432.85 | 0.6626 | 0.6355 | 0.6627 |
| B16_rho110_d16 | pre | 96.50 | 0.6567 | 0.6391 | 0.6567 |
| B16_rho110_d16 | pulse | 505.45 | 0.6719 | 0.6331 | 0.6650 |
| B16_rho110_d16 | post | 96.90 | 0.6562 | 0.6335 | 0.6628 |
| B16_rho120_d8 | pre | 96.50 | 0.6569 | 0.6395 | 0.6568 |
| B16_rho120_d8 | pulse | 274.40 | 0.6774 | 0.6322 | 0.6606 |
| B16_rho120_d8 | post | 286.40 | 0.6646 | 0.6325 | 0.6671 |
| B16_rho140_d4 | pre | 96.50 | 0.6570 | 0.6394 | 0.6568 |
| B16_rho140_d4 | pulse | 158.10 | 0.6782 | 0.6332 | 0.6585 |
| B16_rho140_d4 | post | 383.80 | 0.6656 | 0.6341 | 0.6668 |
| nom_r125_d2 | pre | 96.50 | 0.6569 | 0.6397 | 0.6568 |
| nom_r125_d2 | pulse | 70.70 | 0.6726 | 0.6323 | 0.6714 |
| nom_r125_d2 | post | 432.85 | 0.6599 | 0.6351 | 0.6601 |
| nom_r125_d4 | pre | 96.50 | 0.6567 | 0.6397 | 0.6566 |
| nom_r125_d4 | pulse | 140.65 | 0.6763 | 0.6333 | 0.6646 |
| nom_r125_d4 | post | 383.80 | 0.6640 | 0.6343 | 0.6635 |
| nom_r125_d8 | pre | 96.50 | 0.6568 | 0.6397 | 0.6566 |
| nom_r125_d8 | pulse | 285.40 | 0.6770 | 0.6331 | 0.6581 |
| nom_r125_d8 | post | 286.40 | 0.6614 | 0.6323 | 0.6669 |
| nom_r125_d12 | pre | 96.50 | 0.6568 | 0.6397 | 0.6566 |
| nom_r125_d12 | pulse | 429.35 | 0.6559 | 0.6326 | 0.6543 |
| nom_r125_d12 | post | 191.00 | 0.6353 | 0.6332 | 0.6653 |
| nom_r125_d16 | pre | 96.50 | 0.6568 | 0.6397 | 0.6566 |
| nom_r125_d16 | pulse | 571.80 | 0.6155 | 0.6333 | 0.6503 |
| nom_r125_d16 | post | 96.90 | 0.5916 | 0.6327 | 0.6605 |
| nom_r125_d8_fastrec | pre | 96.50 | 0.6568 | 0.6397 | 0.6566 |
| nom_r125_d8_fastrec | pulse | 285.40 | 0.6774 | 0.6331 | 0.6579 |
| nom_r125_d8_fastrec | post | 236.20 | 0.6589 | 0.6333 | 0.6615 |

### R/N terminal por prioridad

Priorización `high/medium/low` corresponde a crítica/alta/baja. Son medias ponderadas por n de alertas del estrato; no se tratan alertas como réplicas estadísticas. El CSV contiene por fila también SLA y calidad entre completadas.

| Escenario | Prioridad | D1 | P1 | HLS-B |
|---|---|---:|---:|---:|
| B08_rho110_d8 | high | 0.6500 | 0.6119 | 0.6458 |
| B08_rho110_d8 | medium | 0.6733 | 0.6373 | 0.6695 |
| B08_rho110_d8 | low | 0.6675 | 0.6381 | 0.6671 |
| B08_rho120_d4 | high | 0.6456 | 0.6118 | 0.6430 |
| B08_rho120_d4 | medium | 0.6701 | 0.6357 | 0.6675 |
| B08_rho120_d4 | low | 0.6667 | 0.6393 | 0.6660 |
| B08_rho140_d2 | high | 0.6455 | 0.6152 | 0.6448 |
| B08_rho140_d2 | medium | 0.6692 | 0.6389 | 0.6677 |
| B08_rho140_d2 | low | 0.6652 | 0.6399 | 0.6645 |
| B16_rho110_d16 | high | 0.6552 | 0.6153 | 0.6472 |
| B16_rho110_d16 | medium | 0.6753 | 0.6363 | 0.6684 |
| B16_rho110_d16 | low | 0.6664 | 0.6379 | 0.6653 |
| B16_rho120_d8 | high | 0.6497 | 0.6123 | 0.6404 |
| B16_rho120_d8 | medium | 0.6771 | 0.6350 | 0.6666 |
| B16_rho120_d8 | low | 0.6689 | 0.6385 | 0.6673 |
| B16_rho140_d4 | high | 0.6495 | 0.6128 | 0.6418 |
| B16_rho140_d4 | medium | 0.6744 | 0.6373 | 0.6672 |
| B16_rho140_d4 | low | 0.6682 | 0.6393 | 0.6671 |
| nom_r125_d2 | high | 0.6425 | 0.6150 | 0.6411 |
| nom_r125_d2 | medium | 0.6661 | 0.6375 | 0.6664 |
| nom_r125_d2 | low | 0.6632 | 0.6398 | 0.6632 |
| nom_r125_d4 | high | 0.6490 | 0.6154 | 0.6425 |
| nom_r125_d4 | medium | 0.6714 | 0.6371 | 0.6662 |
| nom_r125_d4 | low | 0.6669 | 0.6391 | 0.6664 |
| nom_r125_d8 | high | 0.6502 | 0.6118 | 0.6413 |
| nom_r125_d8 | medium | 0.6760 | 0.6370 | 0.6641 |
| nom_r125_d8 | low | 0.6667 | 0.6379 | 0.6663 |
| nom_r125_d12 | high | 0.6420 | 0.6122 | 0.6347 |
| nom_r125_d12 | medium | 0.6645 | 0.6370 | 0.6588 |
| nom_r125_d12 | low | 0.6432 | 0.6378 | 0.6638 |
| nom_r125_d16 | high | 0.6232 | 0.6126 | 0.6288 |
| nom_r125_d16 | medium | 0.6283 | 0.6367 | 0.6524 |
| nom_r125_d16 | low | 0.6090 | 0.6387 | 0.6598 |
| nom_r125_d8_fastrec | high | 0.6523 | 0.6146 | 0.6379 |
| nom_r125_d8_fastrec | medium | 0.6744 | 0.6366 | 0.6600 |
| nom_r125_d8_fastrec | low | 0.6667 | 0.6383 | 0.6650 |

## 5. Robustez, regiones y sensibilidad

**Clasificación por medias, sin umbral de relevancia:** en 2 perfiles HLS-B supera ambas fijas por media (`nom_r125_d12`, `nom_r125_d16`); d12 queda incierto frente a D1 y d16 es el único con IC95 sin cero frente a ambas. En 10 perfiles supera solo P1 por media; en cero queda por debajo de ambas. Así que “supera ambas” como media no equivale a una región estable, y el criterio más estricto de ambas diferencias con IC inferior >0 se cumple en 1/12.

En el barrido nominal ρ=1.25, las medias HLS-B−D1 son negativas a 2/4/8 h, apenas positivas a 12 h (IC cruza cero), y claramente positivas a 16 h en este muestreo. No hay una serie continua con potencia para definir un umbral: el único contraste inequívoco positivo es el extremo de 16 h. Geométricamente las medias a 12 y 16 h son vecinas, pero la primera no establece superioridad. El control rápido de recuperación a 8 h baja HLS-B−D1 a −0.00811 [−0.00951;−0.00670] frente a −0.00577 [−0.00854;−0.00300] en rho recovery .85; esto sugiere dependencia del perfil completo, no una causalidad aislada de memoria.

Perfiles con B similar no garantizan mismo resultado. B=.8: los tres contrastes HB−D1 son aproximadamente −.0010 a −.0022. B=1.6: aproximadamente −.0041 a −.0060. A B=2, nominal 8h da −.00577 mientras recovery rápida da −.00811 aun con gamma .556 vs 1.111. En gamma alrededor 2.5–2.67, B=1.6/rho=1.10,d16 tiene −.00413 y nominal B=3,d12 tiene +.00706 (IC incluye cero). B/Gamma son resúmenes de primer orden; deadline mix, dispersión Poisson, heterogeneidad, escalado y ventana de HLS-B permanecen relevantes.

La sensibilidad de SLA cambia el signo HLS-B−D1 en ambas duraciones examinadas: para d=8 pasa de −.0068 en referencia a +.0038 (IC incluye cero) con T0=.75 y +.0100 con separación 2:8; sigue negativa con T0=1.25 y separación 8:16. Para d=16 la diferencia cambia de +.0280 en referencia a −.0109 con T0=1.25 y −.0177 con 8:16; es mucho mayor con T0=.75 o 2:8. HLS-B−P1 es positiva en las 10 medias; el IC incluye cero únicamente d16 con escala .75. En dimensionamiento, d8 cambia el signo HLS-B−D1 con 5×3 frente a las demás; d16 cambia signo con 7×3 frente a 5×3/6×2/6×3/6×4. HLS-B−P1 sigue positivo en todas esas celdas. Esto es robustez frente a parámetros distinta de IC dentro de una configuración: la primera es claramente limitada.

La elección de sensibilidad SLA y plantilla fue posterior al barrido central (duraciones 8 y 16 h, elegidas por ausencia/posible presencia de ventaja adaptativa); por tanto son exploratorias y están expuestas a selección. Las filas de las cinco variantes comparten las mismas trazas, no son réplicas independientes. Contrastes R/N de cada contraste, error estándar e IC se limitan a semillas de la celda. No se ajustó multiplicidad.

## 6. Auditoría estadística y reproducibilidad

- Central: 20 semillas de desarrollo 261240000–261240019 por perfil; 12 perfiles, 3 políticas; 720 episodios completos y 1,440 filas de corte H/H+D. Pareamiento: hash exógeno y número de admitidas iguales por semilla/perfil/política. `admitidas=completadas+pendientes` verificado por fila/corte.
- SLA/plantilla: semillas 261250000–261250019; 2 duraciones×5 configuraciones×3 políticas×20 semillas por bloque de sensibilidad: 600 episodios SLA y 600 staffing, 1,200 filas total. El manifiesto común contiene 400 hashes caso-semilla: 200 configuraciones SLA y 200 plantilla. En SLA el hash excluye deadline por diseño; hash y conteo admitido iguales entre cinco SLA por semilla y duración. En plantilla se conserva la demanda exógena y hash común entre cinco equipos. El mismo trace hash se comparte por política.
- IC95 calculado como media de diferencias pareadas ± t(.975,19)·s_d/√20, t=2.093, episodio como unidad. No se toman alertas/cohortes como unidades independientes. Se presentan IC bilaterales exploratorios. Sin corrección de multiplicidad en el barrido de 12 escenarios, 24 contrastes ni sensibilidades.
- Los seed IDs centrales se reutilizan entre escenarios; la secuencia de números aleatorios por tramos comparte componentes. Por ello hay dependencia entre escenarios del barrido y no deben agruparse como 240 observaciones independientes. Inferencia central por celda; sensibilidad en trazas pareadas por variante. Semillas confirmatorias no reutilizadas: validación HLS-B previa usó 261190000–261190099; otros pilotos de desarrollo usaron 261220000, 261230000. No se recalculó prueba confirmatoria con datos exploratorios.
- La mejor fija se escoge a posteriori por escenario como mayor media de D1 y P1 dentro de las mismas 20 semillas. HLS-B−mejor fija es un descriptor retrospectivo; su IC ordinario no corrige selección. No se utilizó una combinación idealizada como implementable.
- Configuraciones: [matriz central](config/soc_hls_operating_regions.json), [sensibilidad](config/soc_hls_operating_sensitivity.json). Runners: [central](run_soc_hls_operating_regions.py), [SLA y plantilla](run_soc_hls_operating_sensitivity.py); resumen: [summarize_soc_hls_operating_regions.py](summarize_soc_hls_operating_regions.py).
- CSV y metadatos centrales: [episodes.csv](../../results/soc_hls_operating_regions/episodes.csv), [cohorts.csv](../../results/soc_hls_operating_regions/cohorts.csv), [priority.csv](../../results/soc_hls_operating_regions/priority.csv), [timeseries.csv](../../results/soc_hls_operating_regions/timeseries.csv), [modes.csv](../../results/soc_hls_operating_regions/modes.csv), [manifest.json](../../results/soc_hls_operating_regions/manifest.json), [metadata.json](../../results/soc_hls_operating_regions/metadata.json).
- CSV y metadatos de sensibilidad: [episodes.csv](../../results/soc_hls_operating_sensitivity/episodes.csv), [priority.csv](../../results/soc_hls_operating_sensitivity/priority.csv), [manifest.json](../../results/soc_hls_operating_sensitivity/manifest.json), [metadata.json](../../results/soc_hls_operating_sensitivity/metadata.json).
- Estos resultados de `results/` estaban ignorados por Git; se publican como resultados sintéticos finales para que la auditoría recalcule las tablas fuera del workspace.
- Los runners de regímenes variables y oportunidad de conmutación usan la política diagnóstica `NOMINAL-REF`. En el árbol local esa compatibilidad depende de cambios no versionados en `src/hls/rq1_allocation.py` y `src/hls/rq1_l1_l2.py`. Esos cambios se excluyen para cumplir la restricción de no publicar cambios del motor; por ello esos dos runners quedan como registro del procedimiento, no pueden ejecutarse directamente desde el commit publicado. Sus CSV finales se incluyen para inspección. El dominio operativo y su sensibilidad a SLA/plantilla sí se reproducen desde el código base sin esos cambios.

## 7. Qué permiten afirmar los datos

### Resultados demostrados (confirmatorios previos)

La validación independiente congelada de HLS-B (100 semillas nuevas, cuatro escenarios sintéticos equiponderados por semilla) encontró R/N D1=.6259 y HLS-B=.6541; diferencia pareada +.02820, IC95 [.02526;.03115], 98/100 diferencias positivas, prueba unilateral preespecificada t99=18.98, p=4.62e−35. El beneficio agregado procede principalmente del escenario estacionario ρ=1.25 (HLS-B−D1 +.1106 [+.1036;+.1175]); a ρ=1.00 la diferencia es −.0013 [−.0018;−.0009], y las dos transiciones individuales no distinguen HLS-B de D1 en esa validación. HLS-B superó P1 en las cuatro celdas secundarias con corrección Holm, pero eso no equivale a superar a la mejor fija en cada dinámica. D1/P1 confirmatorio estacionario a ρ=1.25 mostró P1−D1 +.0982 [+.0891;+.1073], n=100 en el estimando de ese estudio. No extrapolar dichos resultados a prevalencia/turnos reales.

### Tendencias exploratorias repetidas

En 12 escenarios centrales, HLS-B supera a P1 en todas las medias con IC pareados positivos. En la mayoría de las celdas D1 conserva la mejor media fija, especialmente para pulsos breves/moderados y B similar; para pulso rho=1.25,d=16 HLS-B supera ambas por media y por IC nominal sin ajuste. La congestión al fin del pulso y el backlog al retorno crecen con duración en el nominal rho=1.25; el retorno D1 ocurre todavía con backlog medio alto (d16: 149 alertas, 34.1 h servicio en HLS-B). Esto evidencia memoria del estado en el modelo, no que otra decisión hubiese causado mejora.

### Resultados sensibles

La ventaja de HLS-B sobre D1 para pulsos largos no persiste bajo plazos más holgados (T0=1.25) ni separación 8:16; tampoco con roster L1=7,L2=3 para d16. Los cambios de SLA alteran con fuerza R/N y las clasificaciones, y acortamiento relativo de plazos aumenta la ventaja modelada de priorización. Mantener demanda absoluta mientras aumenta capacidad L1 cambia rho y puede eliminar la congestión. Las conclusiones sobre frontera D1/P1/HLS-B son condicionales al SLA, plantilla y rho efectiva.

### No concluyentes

No existe evidencia para un umbral de duración general; 12 h es positiva por media pero incierta y 16 h es solo una celda central concluyente, seleccionada entre perfiles. No hay caso en que HLS-B quede por debajo de ambas por media en los 12 escenarios; sin embargo HLS-B queda bajo D1 en 10 y bajo la mejor fija en 11. Diferencias menores no tienen umbral de relevancia económica validado. Distribución de competencia, coste operativo, cobertura y especialización real no se validaron para GMV-CERT.

## 8. Límites de validez externa

Demanda Poisson sintética por tramos, no perfil intradía calibrado; timestamps SOCTRA agregados no miden trabajo activo. SLA son hipótesis terminales de resolución (no acuerdos GMV-CERT). Capacidad continua 24×7, sin turnos/cobertura, pausas, cambios de guardia, colas limitadas, cancelación/retrabajo ni latencia real de coordinación. Roster, servicios, competencia, mezcla y escalado son sintéticos; capacidad efectiva usa mezcla conocida y recursos fraccionables. HLS-B observa proxies modelados, no indicadores operacionales validados. R/N combina calidad esperada y puntualidad; debe leerse junto a SLA, calidad entre completadas, cola, trabajo y cortes. Un final sin backlog no prueba cumplimiento del SLA, y correlación entre conmutación/backlog no es efecto causal de cambiar política.

**Cierre de auditoría:** evidencia confirmatoria apoya la configuración HLS-B en la distribución sintética predefinida, con ganancia concentrada en sobrecarga estacionaria. La caracterización operativa muestra regiones condicionales, ventaja consistente frente a P1 y ventaja frente a D1 solo localizada y sensible. No sustenta una región amplia/robusta de superioridad de HLS-B ni una frontera universal de políticas.
