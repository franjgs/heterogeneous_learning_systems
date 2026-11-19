# SOCTRA-HLS: organización de equipos SOC

## Punto de entrada

Esta carpeta documenta una aplicación de **HLS** al trabajo de analistas humanos y sistemas de IA en un Security Operations Center. HLS es el programa general; SOCTRA aporta contexto empírico sobre triaje y alertas, y GMV-CERT es una referencia operativa cualitativa. La aplicación no define ni sustituye HLS.

**Antes de proponer experimentos, modificar estrategias, interpretar resultados o continuar la investigación SOC, leer este README y los documentos canónicos indicados.**

## Lectura recomendada

1. [Fundamentos y modelo SOC](SOC_FOUNDATIONS_AND_MODEL.md): pregunta, fuentes, límites empíricos, simulador y políticas.
2. [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md): evolución experimental, resultados positivos y negativos, correcciones métricas y artefactos reproducibles.
3. [Estado científico actual](SOC_CURRENT_STATE.md): conclusiones válidas, incógnitas y situación hacia *Electronics*.
4. [Referencia operativa GMV-CERT](GMV_CERT_OPERATIONAL_REFERENCE.md): contenido cualitativo comunicado, interpretación, incógnitas e hipótesis, preservado como documento fuente de contexto.

La documentación general conserva autoridad para HLS: consultar [THEORY](../../docs/THEORY.md), [RESEARCH](../../docs/RESEARCH.md) y [HISTORY](../../docs/HISTORY.md) cuando la pregunta exceda esta aplicación. No se modifican desde esta consolidación.

## Estado en una frase

Existe un laboratorio SOC simulado con demanda parametrizada, IA de triaje, pools L1/L2 y estrategias de asignación; se han evaluado políticas RQ1, controladores y variantes diagnósticas. Los resultados son condicionales a parámetros operativos mayoritariamente hipotéticos y no demuestran mejoras en GMV-CERT. No hay una estrategia adaptativa que haya demostrado superioridad general sobre controles competitivos.

## Congelaciones y límites

- **D1** permanece congelado como baseline descentralizado. No representa un procedimiento GMV verificado.
- El repertorio organizativo vigente es D1 y P1–P5, descrito en [Fundamentos y modelo](SOC_FOUNDATIONS_AND_MODEL.md). B0–B4, C0/C1/C2 × P0/P1 y D1-L/D1-S son etiquetas históricas de campañas anteriores, no aliases de P1–P5; consultar [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md) para interpretarlas.
- No inferir competencias, velocidad, calidad humana, plantilla, turnos, SLA terminal ni costes reales a partir de SOCTRA o de la referencia cualitativa.
- No tratar `escalada_L2`, `reportado` ni otras etiquetas de proceso como verdad objetiva de seguridad o calidad.
- Las cifras simuladas no son observaciones operativas. Mantener identificada cada afirmación como hecho documentado, resultado experimental, hipótesis o desconocido.

## Reproducibilidad y alcance

Los informes canónicos apuntan a código y artefactos que permanecen en el repositorio; los datos SOCTRA originales son restringidos y no se incluyen aquí. El informe agregado del replay histórico A queda integrado en [Resultados y lecciones](SOC_RESULTS_AND_LESSONS.md). No publicar identificadores, registros o nombres de proyecto.
