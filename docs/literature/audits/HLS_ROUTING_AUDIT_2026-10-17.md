# HLS — Auditoría matemática de MixLLM y System-1.x

Fecha: 2026-10-17. Fuentes primarias consultadas en versión editorial, sin ejecución experimental.

**Actualización de trazabilidad (2026-10-17, posterior a esta auditoría):**
La descarga inicial descrita abajo falló en aquel entorno; posteriormente se
verificaron localmente los PDF editoriales de MixLLM y System-1.x, con
versiones, rutas y SHA-256 registrados en
[`ADAPTIVE_TRAINING_REFERENCE_REGISTER.md`](../ADAPTIVE_TRAINING_REFERENCE_REGISTER.md).
La extracción posterior no cambia el alcance ni los análisis de esta nota.
Ambos PDF permanecen solo en la copia local y están cubiertos por la regla de
ignore; no se publican en el estado actual de la rama. El historial Git no se
reescribe.

## Fuentes y trazabilidad

1. Wang et al. (2025), *MixLLM: Dynamic Routing in Mixed Large Language Models*, NAACL 2025, pp. 10912–10922, DOI 10.18653/v1/2025.naacl-long.545. PDF editorial: https://aclanthology.org/2025.naacl-long.545.pdf . Nombre local propuesto: `docs/literature/competence_organization/Wang_et_al_2025_MixLLM_Dynamic_Routing.pdf`.
2. Saha et al. (2025), *System-1.x: Learning to Balance Fast and Slow Planning with Language Models*, ICLR 2025. PDF editorial: https://proceedings.iclr.cc/paper_files/paper/2025/file/605e59e78284907aa4fce5280838def3-Paper-Conference.pdf . Nombre local propuesto: `docs/literature/cross_cutting/Saha_et_al_2025_System_1x.pdf`.

**Archivo local:** Descarga intentada el 2026-10-17, pero falló por DNS del entorno. Los PDF **NO** están archivados por esta operación. No se calculó SHA-256. La existencia de un registro BibTeX no prueba presencia del PDF local. No modificar el repositorio remoto para incorporar PDF.

## MixLLM — formulación original

Consulta: PDF editorial, sección 3, ecuaciones (1)–(20), páginas PDF 3–5.

- Consulta secuencial `q_n`, candidatos `m_l`, representación `e_n=Encoder(q_n)`; etiquetas de dominio y ajuste de embeddings, pérdida `L=L_intra+L_inter` (ec. 1).
- Calidad prevista por modelo: `p_hat[n,l]=f_l^rq(e_n;theta_l^rq)` (ec. 4).
- Coste previsto: `c_hat[n,l]=len_prompt[n,l]*price_prompt[l]+len_response_hat[n,l]*price_response[l]` (ec. 5), con longitud prevista por regresor específico (ec. 6).
- Puntuación: `s[n,l]=s_trade[n,l]+alpha*s_unc[n,l]-beta*s_pen[l]` (ec. 7).
- Compromiso calidad-coste: `s_trade=(lambda/(lambda+1))*p_hat-(1/(lambda+1))*c_hat` (ec. 8). `lambda` es voluntad de pago, NO tasa de llegada.
- Exploración/incertidumbre: `s_unc=e_n^T A_l^{-1}e_n` (ec. 9).
- Penalización de espera: `s_pen=exp(gamma*(w_l-xi*tau))` (ec. 10).
- Decisión: `m*_n=argmax_l s[n,l]` (ec. 11).
- Aprendizaje offline: descenso por gradiente en predictores de calidad y longitud, actualizaciones de `A_l` (ecs. 12–14); online: feedback individual del modelo elegido, red compartida y gradiente de política (ecs. 15–20).

**Distinción científica:** el aprendizaje online es del *router/predictores*, no se demuestra que cambien las competencias internas de los LLM candidatos. No etiquetar como equivalente a aprendizaje individual MIS-v2.

**Comparabilidad HLS:** se puede comparar routing USE si se igualan secuencias de consultas, conjunto de modelos, presupuesto, latencia y feedback. Es INCOMPATIBLE comparar directamente su puntuación normalizada con utilidad de otras políticas sin calibración. La calidad estimada `p_hat` es distinta de calidad observada. El término de espera requiere semántica temporal y recursos comparables.

**Reproducción:** ecuaciones principales formalizadas, NO reproducidas. Para réplica editorial faltan verificar con detalle particiones de datos, arquitectura, hiperparámetros y código/datasets disponibles.

## System-1.x — formulación original

Consulta: PDF editorial, secciones 2.1–2.4 y apéndice A, algoritmo 1 (páginas PDF 4–6 y 15).

- Datos supervisados `D={(s0^(i),sg^(i),P^(i),T^(i))}_{i=1}^N`: estado inicial, objetivo, plan de referencia y trayectoria de búsqueda.
- Hiperparámetro `x in [0,1]` que controla el grado de hibridación; `h(si,sj)` estima dificultad de un subobjetivo.
- Ordenar ejemplos por dificultad. Los `(1-x)N` más fáciles se etiquetan solo System-1; los restantes `xN` reciben descomposición híbrida.
- Para cada plan de longitud `n`, elegir tramo de búsqueda profunda por:
  `(j,k)=argmin_{u<=v} [h(s0,su)-h(su,sv)+h(sv,sg)]`, sujeto a `|v-u|=x*n` (sección 2.3; algoritmo 1). Los tres segmentos se asignan `System-1 / System-2 / System-1`.
- El controlador aprende descomposición y clasificación fácil/difícil; planificadores System-1 y System-2 se ajustan sobre planes directos y trazas de búsqueda, respectivamente. En inferencia se concatenan los subplanes.
- Métricas publicadas: validez de plan y número de estados explorados, con tareas Maze Navigation y Blocksworld.

**Distinción científica:** `x` es un parámetro de control de preparación de datos/entrenamiento y composición, NO probabilidad de enrutamiento online ni una ley de aprendizaje de capacidades. System-1.x resuelve tareas composicionales de planificación; MixLLM asigna una consulta a un único modelo. `RELATED`, no `EQUIVALENT`.

**Comparabilidad HLS:** para una comparación justa de System-1.x es necesario un entorno con planes y subobjetivos verificables, presupuestos de exploración de estados y condiciones de entrenamiento equiparables. La métrica de estados explorados NO equivale automáticamente a tokens, latencia o coste monetario. Reproducible en principio con datos y procedimiento; no reproducido.

## Decisión técnica (sin implementación)

- Priorizar **MixLLM** para una primera comparación de routing USE (misma unidad de decisión y múltiples candidatos).
- Mantener **System-1.x** como comparador de composición por subobjetivos, no como router equivalente.
- No inventar una métrica universal que convierta estados explorados, tiempo y dinero en el mismo recurso.
- No añadir aprendizaje de capacidades al router para hacer coincidir las dos familias.
- Estados: ambas fuentes ESTUDIADO y FORMALIZADO (núcleo), ninguna REPRODUCIDA ni todavía COMPARABLE bajo un protocolo común.

## Acciones pendientes

1. Codex local: comprobar presencia de ambos PDF, descargar solo los ausentes, aplicar nombres canónicos y calcular SHA-256; PDF solo local.
2. Revisar BibTeX maestro y añadir/corregir únicamente referencias que falten; registrar versión editorial.
3. Extraer tablas de parámetros, ablations, datasets y disponibilidad de código antes de declarar REPRODUCIBLE.
4. Elaborar matriz de equivalencia ontológica y costes de integración sin cambiar el laboratorio.
