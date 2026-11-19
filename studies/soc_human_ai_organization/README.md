# SOCTRA-HLS: organización de equipos SOC

## Punto de entrada

Esta carpeta documenta una aplicación de **HLS** al trabajo de analistas humanos y sistemas de IA en un Security Operations Center. HLS es el programa general; SOCTRA aporta contexto empírico sobre triaje y alertas, y GMV-CERT es una referencia operativa cualitativa. La aplicación no define ni sustituye HLS.

**Antes de proponer experimentos, modificar estrategias, interpretar resultados o continuar la investigación SOC, leer este README y los documentos canónicos indicados.**

## Lectura recomendada

- **Recuperar el estado:** [SOC_CURRENT_STATE.md](SOC_CURRENT_STATE.md) tras este README.
- **Revisar evidencia científica:** [SOC_PAPER_EVIDENCE_GUIDE.md](SOC_PAPER_EVIDENCE_GUIDE.md), [SOC_SCIENTIFIC_CONSOLIDATION.md](SOC_SCIENTIFIC_CONSOLIDATION.md) y los informes originales enlazados allí.
- **Reproducir experimentos:** protocolos, `config/`, scripts y tablas agregadas de `evidence/`, según la [guía de evidencia](SOC_PAPER_EVIDENCE_GUIDE.md#material-para-tablas-figuras-y-reproducción).
- **Redactar el artículo:** [SOC_PAPER_EVIDENCE_GUIDE.md](SOC_PAPER_EVIDENCE_GUIDE.md), incluida la transferencia técnica en inglés.
- **Continuar la investigación:** [SOC_FOUNDATIONS_AND_MODEL.md](SOC_FOUNDATIONS_AND_MODEL.md), [SOC_CURRENT_STATE.md](SOC_CURRENT_STATE.md) y la [referencia GMV-CERT](GMV_CERT_OPERATIONAL_REFERENCE.md).

1. [Fundamentos y modelo SOC](SOC_FOUNDATIONS_AND_MODEL.md): pregunta, fuentes, límites empíricos, simulador y políticas.
2. [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md): evolución experimental, resultados positivos y negativos, correcciones métricas y artefactos reproducibles.
3. [Estado científico actual](SOC_CURRENT_STATE.md): conclusiones válidas, incógnitas y situación hacia *Electronics*.
4. [Dimensionamiento experimental A1](SOC_A1_EXPERIMENTAL_DIMENSIONING.md): calibración piloto, capacidad estimada y oportunidades observadas.
5. [Rediseño del Paso 5](SOC_STEP5_REDESIGN.md) y [revisión de políticas](SOC_POLICY_DESIGN_REVIEW.md): auditoría estructural, repertorio candidato y decisiones pendientes.
6. [Propuesta taxonómica A2](SOC_A2_POLICY_TAXONOMY_AND_DESIGN.md): dimensiones organizativas, políticas candidatas y controles causales.
7. [Decisión de cartera A2.2](SOC_A2_POLICY_PORTFOLIO_DECISION.md): comparación crítica; D1/T/Q/C/M está aprobado provisionalmente para evaluación, no congelado.
8. [Viabilidad de mecanismos A3.1](SOC_A3_1_MECHANISM_FEASIBILITY.md): diagnóstico estructural y estados de contraste.
9. [Piloto A3.2 D1/T/Q/C](SOC_A3_2_PILOT_COMPARISON.md): prototipo central secuencial C, piloto emparejado, métricas y diagnósticos; exploratorio, pendiente de revisión científica.
10. [A0: congestión de D1](SOC_A0_BASELINE_CONGESTION.md): caracterización D1-only de carga, disponibilidad, colas, SLA y bloqueo urgente; sintética y exploratoria.
11. [Comparación exploratoria D1/P1–P5](SOC_POLICY_COMPARISON_RESULTS.md): campaña emparejada A0, rendimiento esperado, sensibilidad de plantilla y coste; sin evidencia de matching múltiple.
12. [Consolidación científica](SOC_SCIENTIFIC_CONSOLIDATION.md): interpretación verificada y límites de A0, A3.2 y D1/P1–P5; punto de entrada a las cifras originales.
13. [Validación confirmatoria D1/P1](SOC_CONFIRMATORY_RESULTS.md) y [protocolo prefijado](SOC_CONFIRMATORY_PROTOCOL.md): 100 semillas independientes en sobrecarga, análisis de carga y sensibilidad; evidencia limitada al simulador sintético.
14. [Referencia operativa GMV-CERT](GMV_CERT_OPERATIONAL_REFERENCE.md): contenido cualitativo comunicado, interpretación, incógnitas e hipótesis, preservado como documento fuente de contexto.
15. [Desarrollo HLS-B](SOC_HLSB_DEVELOPMENT_RESULTS.md), [protocolo de validación](SOC_HLSB_VALIDATION_PROTOCOL.md) y [resultados independientes](SOC_HLSB_VALIDATION_RESULTS.md): selector D1/P1 por llegadas observadas, configuración congelada y cuatro escenarios sintéticos.

La documentación general conserva autoridad para HLS: consultar [THEORY](../../docs/THEORY.md), [RESEARCH](../../docs/RESEARCH.md) y [HISTORY](../../docs/HISTORY.md) cuando la pregunta exceda esta aplicación. No se modifican desde esta consolidación.

## Estado en una frase

El [supervisor HLS-A](SOC_HLS_ADAPTIVE_SUPERVISOR.md) está implementado y tiene un piloto de desarrollo con seis semillas nuevas; selecciona D1/P1 por presión observable con histéresis. El piloto no demostró ventaja sobre D1 en episodios de carga variable y no constituye validación independiente.

La [variante HLS-B](SOC_HLSB_DEVELOPMENT_RESULTS.md) usa una ventana de llegadas observadas y capacidad modelada; su piloto de desarrollo separa mejor las cargas estacionarias y mejora a HLS-A, pero D1 sigue ganando en las dos transiciones ensayadas.

La [validación independiente de HLS-B](SOC_HLSB_VALIDATION_RESULTS.md), con 100 semillas nuevas por escenario, encontró una diferencia media HLS-B−D1 de +0,02820 [IC95 % 0,02526; 0,03115] en cuatro escenarios sintéticos equiponderados. La ganancia se concentra en sobrecarga estacionaria; en los dos escenarios variables no se observó ventaja concluyente frente a D1.

Existe un laboratorio SOC simulado con demanda parametrizada, IA de triaje, pools L1/L2 y estrategias de asignación; se han evaluado políticas RQ1, controladores y variantes diagnósticas. Los resultados son condicionales a parámetros operativos mayoritariamente hipotéticos y no demuestran mejoras en GMV-CERT. No hay una estrategia adaptativa que haya demostrado superioridad general sobre controles competitivos.

Una validación preespecificada con 100 semillas nuevas confirmó que P1 mejora R/N terminal frente a D1 bajo sobrecarga sintética ρ=1,25 (+0,0982 [IC95 % 0,0891; 0,1073]), mientras lo empeora en ρ≤1,10. Es evidencia de dependencia del régimen, no superioridad universal.

## Congelaciones y límites

- **D1** permanece congelado como baseline descentralizado. No representa un procedimiento GMV verificado.
- El motor conserva D1/P1–P5; para el piloto A3.2 se exponen T=P1, Q=P2 y el prototipo C secuencial. La cartera D1/T/Q/C/M sigue provisional: M no se implementó ni evaluó en A3.2. B0–B4, C0/C1/C2 × P0/P1 y D1-L/D1-S son etiquetas históricas, no aliases de P1–P5 ni de T/Q/C/M; consultar [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md) y el [informe A3.2](SOC_A3_2_PILOT_COMPARISON.md).
- No inferir competencias, velocidad, calidad humana, plantilla, turnos, SLA terminal ni costes reales a partir de SOCTRA o de la referencia cualitativa.
- No tratar `escalada_L2`, `reportado` ni otras etiquetas de proceso como verdad objetiva de seguridad o calidad.
- Las cifras simuladas no son observaciones operativas. Mantener identificada cada afirmación como hecho documentado, resultado experimental, hipótesis o desconocido.

## Reproducibilidad y alcance

Los informes apuntan a código, configuraciones, [tablas agregadas](evidence/manifest.json) y [figuras sintéticas](figures/soc_confirmatory_rn_by_load.svg) versionadas. Los CSV por episodio y trazas completas permanecen en `results/`, ignorado por Git; para recalcular desde cero se necesitan los scripts y sus dependencias según la guía de evidencia. Los datos SOCTRA originales son restringidos y no se incluyen aquí. El informe agregado del replay histórico A queda integrado en [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md). No publicar identificadores, registros o nombres de proyecto.

El [diagnóstico cuantitativo de debilidades D1](SOC_A0_D1_ORGANIZATIONAL_WEAKNESSES.md) añade 18 episodios acotados: pérdidas positivas de orden local sólo en la carga 1,25, sin intercambios simultáneos ni ociosidad factible observados. Son oportunidades locales, no mejoras terminales demostradas.
